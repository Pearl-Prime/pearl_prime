#!/usr/bin/env python3
"""Batch-render N random 2hr books via the proven plain-subprocess path.

Canonical driver (replaces the earlier ad-hoc killpg/process-group-timeout
wrapper — see
docs/agent_prompt_packs/20260721_bestseller_atom_flow/03_batch_driver_cell_aware_precheck.md
for the freeze diagnosis this file is built against).

Freeze root cause (superseded design, kept here for provenance): the earlier
run_random_2h_book_x100.py used
``subprocess.Popen(..., start_new_session=True)`` + ``proc.wait(timeout=180)``
+ ``os.killpg(proc.pid, 9)`` on timeout. Observed real-world
``extended_book_2h`` renders take ~822s — over 4x that 180s default — so
essentially every book was being SIGKILLed mid-render via a process-group
kill. That is consistent with the freeze/orphan pattern the operator saw
(1/7 hung). ``run_random_2h_book_with_trace.py``'s own ``run_render()`` uses
a single untimed ``subprocess.run(cmd, cwd=cwd)`` and completed 3/3 in the
operator's own proof run. This driver keeps that plain-subprocess shape: no
process-group detachment, no killpg. An optional per-book timeout is still
available (``--timeout-s``, default 1200s — comfortably above the observed
822s) using a plain ``terminate()`` -> ``wait(grace)`` -> ``kill()``
escalation on the single child process, never a process-group kill.

Cell-aware pre-check: before spending ~90-800s rendering a book, this driver
resolves the (persona, topic, engine) cell the seed will pick — using the
exact same ``list_candidates()`` / ``pick_candidate()`` the wrapper uses
internally, with an identical (unfiltered) candidate pool so the seed maps
to the same cell in-process and in the subprocess — and checks for a
``story_atoms/<persona>/anchored/<topic>/<engine>/`` bank. Cells with no bank
are, by default, SKIPPED and logged to
``<out-dir>/cells_needing_authoring.jsonl`` (feeds Lane 02 /
``ws_story_cell_authoring_20260425``) instead of rendering a book that can
only ever land at Layer 1 ("structurally clear") at best. Pass
``--allow-unauthored`` to render floor-only smoke books anyway.

Usage:
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_x100.py --n 5
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_x100.py --n 1 --seed-start 43004
  PYTHONPATH=. python3 scripts/qa/run_random_2h_book_x100.py --n 100 --allow-unauthored
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.qa.run_random_2h_book_with_trace import (  # noqa: E402
    CellCandidate,
    _has_story_atoms,
    list_candidates,
    pick_candidate,
)

WRAPPER = REPO_ROOT / "scripts" / "qa" / "run_random_2h_book_with_trace.py"
DEFAULT_TIMEOUT_S = 1200  # spec floor is >=900s given observed 822s runs
TERMINATE_GRACE_S = 30


def _word_count(book_path: Optional[Path]) -> Optional[int]:
    if not book_path or not book_path.is_file():
        return None
    try:
        return len(book_path.read_text(encoding="utf-8", errors="ignore").split())
    except OSError:
        return None


def _acceptance_layer(render_dir: Optional[Path]) -> Optional[str]:
    """Read the Lane 04 (book-acceptance-stamp) verdict for this render, if
    any exists. Checks ``book_acceptance_stamp.json`` first (the canonical
    Lane 04 file, written by ``scripts/run_pipeline.py`` at render time —
    see ``phoenix_v4/quality/acceptance_layer.py``), falling back to
    ``quality_summary.json``'s ``acceptance_layer`` field for renders that
    only wrote that. Returns ``None`` if neither is present — this driver
    never invents a verdict itself; it only surfaces what run_pipeline.py
    already stamped.
    """
    if render_dir is None:
        return None
    stamp_path = render_dir / "book_acceptance_stamp.json"
    if stamp_path.is_file():
        try:
            stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            stamp = {}
        layer = stamp.get("acceptance_layer") if isinstance(stamp, dict) else None
        if layer:
            return str(layer)
    qs_path = render_dir / "quality_summary.json"
    if qs_path.is_file():
        try:
            qs = json.loads(qs_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            qs = {}
        acc = qs.get("acceptance_layer") if isinstance(qs, dict) else None
        if isinstance(acc, dict):
            layer = acc.get("acceptance_layer")
            if layer:
                return str(layer)
    return None


def _research_fit_bound(render_dir: Optional[Path]) -> Optional[bool]:
    """True/False once an enrichment_audit.json is present, else None.

    Once Lane 01's honesty gate lands, ``research_fit.mode`` is guaranteed to
    be either an active mode (research_fit_v1 / twelve_shape_continuity) or
    "skipped" with a skip_reason — never a silently-empty dict. Mirrors the
    mode check in scripts/ci/check_research_fit_honesty.py.
    """
    if render_dir is None:
        return None
    audit_path = render_dir / "enrichment_audit.json"
    if not audit_path.is_file():
        return None
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rf = audit.get("research_fit")
    if not isinstance(rf, dict):
        return False
    mode = str(rf.get("mode") or "").strip()
    return bool(rf) and mode not in ("", "skipped")


def resolve_cell(
    seed: int, *, repo_root: Path
) -> tuple[Optional[CellCandidate], bool]:
    """Mirror the wrapper's own (unfiltered) cell selection for this seed.

    require_story_atoms is intentionally False — the pre-check below decides
    skip/run, not the candidate pool itself, so cells_needing_authoring.jsonl
    reflects real random draws rather than a pool already filtered to
    authored-only. The driver never passes --bestseller-path to the wrapper
    subprocess, so this pool must stay unfiltered to keep seed->cell mapping
    identical between this process and the subprocess.
    """
    candidates = list_candidates(repo_root=repo_root, require_story_atoms=False)
    if not candidates:
        return None, False
    cell = pick_candidate(candidates, seed=seed)
    has_atoms = _has_story_atoms(cell.persona, cell.topic, cell.engine, repo_root=repo_root)
    return cell, has_atoms


def run_one_book(
    seed: int,
    *,
    repo_root: Path,
    out_dir: Path,
    timeout_s: int,
    log,
) -> dict:
    """Render one book via the proven plain-subprocess path.

    No start_new_session, no os.killpg. On timeout: terminate() -> bounded
    wait() -> kill(), on the single child process only.
    """
    run_log = out_dir / f"run_{seed}.log"
    t0 = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    env["PHOENIX_OMEGA_REMOTE"] = env.get("PHOENIX_OMEGA_REMOTE", "local-override")
    timed_out = False
    rc = -1
    with run_log.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(
            [sys.executable, "-u", str(WRAPPER), "--seed", str(seed)],
            cwd=str(repo_root),
            env=env,
            stdout=fh,
            stderr=subprocess.STDOUT,
        )
        try:
            rc = int(proc.wait(timeout=timeout_s))
        except subprocess.TimeoutExpired:
            timed_out = True
            log(f"TIMEOUT seed={seed} after {timeout_s}s — terminate()")
            proc.terminate()
            try:
                rc = int(proc.wait(timeout=TERMINATE_GRACE_S))
            except subprocess.TimeoutExpired:
                log(f"TIMEOUT seed={seed} still alive after terminate() — kill()")
                proc.kill()
                rc = int(proc.wait(timeout=TERMINATE_GRACE_S))
            fh.write(
                f"\nTIMEOUT after {timeout_s}s — terminate()/kill() on child pid only "
                "(no process-group kill)\n"
            )

    elapsed = round(time.time() - t0, 1)
    text = run_log.read_text(encoding="utf-8", errors="ignore") if run_log.is_file() else ""
    book = trace = persona = topic = engine = render_dir_str = None
    pipeline_exit = None
    for line in text.splitlines():
        if line.startswith("book:"):
            book = line.split(":", 1)[1].strip()
        elif line.startswith("trace:"):
            trace = line.split(":", 1)[1].strip()
        elif line.startswith("persona:"):
            persona = line.split(":", 1)[1].strip()
        elif line.startswith("topic:"):
            topic = line.split(":", 1)[1].strip()
        elif line.startswith("engine:"):
            engine = line.split(":", 1)[1].strip()
        elif line.startswith("RENDER_DIR "):
            render_dir_str = line.split(" ", 1)[1].strip()
        elif line.startswith("pipeline_exit:"):
            try:
                pipeline_exit = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass

    book_path = Path(book) if book else None
    book_ok = bool(book_path and book_path.is_file()) and not timed_out
    words = _word_count(book_path) if book_ok else None
    render_dir = Path(render_dir_str) if render_dir_str else None
    research_fit_bound = _research_fit_bound(render_dir)
    acceptance_layer = _acceptance_layer(render_dir)

    return {
        "seed": seed,
        "elapsed_s": elapsed,
        "wrapper_rc": rc,
        "pipeline_exit": pipeline_exit,
        "timed_out": timed_out,
        "book_ok": book_ok,
        "persona": persona,
        "topic": topic,
        "engine": engine,
        "words": words,
        "research_fit_bound": research_fit_bound,
        "acceptance_layer": acceptance_layer,
        "book": book,
        "trace": trace,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed-start", type=int, default=42000)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "qa" / "random_2h_x100_20260721",
    )
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument(
        "--timeout-s",
        type=int,
        default=DEFAULT_TIMEOUT_S,
        help=f"Per-book hard timeout in seconds (default {DEFAULT_TIMEOUT_S}; "
        "observed real extended_book_2h renders ~822s).",
    )
    ap.add_argument(
        "--checkpoint-every",
        type=int,
        default=5,
        help="Write a CHECKPOINT_*.json + log line every N attempted (run or skipped) books.",
    )
    ap.add_argument(
        "--allow-unauthored",
        action="store_true",
        help="Render cells with no story_atoms bank instead of skipping "
        "(floor-only smoke books; still logged as authored_cell=false).",
    )
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)

    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "driver.log"
    results_path = out_dir / "results.jsonl"
    skip_report_path = out_dir / "cells_needing_authoring.jsonl"

    def log(msg: str) -> None:
        line = f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    log(
        "VERIFY_OK canonical driver: plain subprocess, no process-group kill; "
        f"timeout_s={args.timeout_s} allow_unauthored={args.allow_unauthored} "
        f"n={args.n} seed_start={args.seed_start}"
    )

    ok = fail = skip = attempted = 0
    acceptance_layer_counts: dict[str, int] = {}
    for i in range(args.start_index, args.n):
        seed = args.seed_start + i
        marker = out_dir / f"done_{seed}.json"
        if marker.is_file():
            log(f"SKIP-DONE [{i + 1}/{args.n}] seed={seed} (already completed)")
            skip += 1
            ok += 1
            continue

        cell, has_atoms = resolve_cell(seed, repo_root=repo_root)
        if cell is None:
            log(f"BLOCKED [{i + 1}/{args.n}] seed={seed} no viable candidates at all")
            fail += 1
            attempted += 1
            continue

        if not has_atoms and not args.allow_unauthored:
            skip += 1
            attempted += 1
            rec = {
                "seed": seed,
                "persona": cell.persona,
                "topic": cell.topic,
                "engine": cell.engine,
                "reason": "no_story_atoms_bank",
                "at": datetime.now(timezone.utc).isoformat(),
            }
            with skip_report_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            log(
                f"SKIP-UNAUTHORED [{i + 1}/{args.n}] seed={seed} "
                f"{cell.persona}×{cell.topic}×{cell.engine} (no story_atoms bank; "
                "logged to cells_needing_authoring.jsonl)"
            )
        else:
            log(
                f"RUN  [{i + 1}/{args.n}] seed={seed} "
                f"{cell.persona}×{cell.topic}×{cell.engine} authored={has_atoms}"
            )
            row = run_one_book(
                seed, repo_root=repo_root, out_dir=out_dir, timeout_s=args.timeout_s, log=log
            )
            row["i"] = i
            row["authored_cell"] = has_atoms
            attempted += 1
            with results_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")

            if row["book_ok"]:
                marker.write_text(json.dumps(row, indent=2), encoding="utf-8")
                ok += 1
                _layer_key = row["acceptance_layer"] or "unknown"
                acceptance_layer_counts[_layer_key] = acceptance_layer_counts.get(_layer_key, 0) + 1
                log(
                    f"OK   [{i + 1}/{args.n}] seed={seed} {row['elapsed_s']}s "
                    f"{row['persona']}×{row['topic']}×{row['engine']} words={row['words']} "
                    f"research_fit_bound={row['research_fit_bound']} "
                    f"acceptance_layer={row['acceptance_layer']} "
                    f"pipeline_exit={row['pipeline_exit']}"
                )
                if row["acceptance_layer"] in ("system_working", "bestseller_register"):
                    log(
                        f"WARN seed={seed} acceptance_layer={row['acceptance_layer']!r} "
                        "reported by an automated batch driver — Layer 3/4 require a "
                        "logged human/operator review; re-verify this was not "
                        "auto-assigned (see phoenix_v4/quality/acceptance_layer.py)"
                    )
            else:
                fail += 1
                why = "TIMEOUT" if row["timed_out"] else f"rc={row['wrapper_rc']}"
                log(f"FAIL [{i + 1}/{args.n}] seed={seed} {row['elapsed_s']}s {why}")

        if attempted > 0 and attempted % args.checkpoint_every == 0:
            checkpoint = {
                "checkpoint": attempted,
                "of": args.n,
                "ok": ok,
                "fail": fail,
                "skip": skip,
                "last_seed": seed,
                "last_cell": f"{cell.persona}×{cell.topic}×{cell.engine}",
                "acceptance_layer_counts": dict(acceptance_layer_counts),
                "at": datetime.now(timezone.utc).isoformat(),
            }
            (out_dir / f"CHECKPOINT_{attempted:03d}.json").write_text(
                json.dumps(checkpoint, indent=2), encoding="utf-8"
            )
            log(
                f"CHECKPOINT {attempted}/{args.n} ok={ok} fail={fail} skip={skip} "
                f"acceptance_layer_counts={acceptance_layer_counts}"
            )

    summary = {
        "ok": ok,
        "fail": fail,
        "skip": skip,
        "n": args.n,
        "acceptance_layer_counts": acceptance_layer_counts,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log(f"DONE ok={ok} fail={fail} skip={skip}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

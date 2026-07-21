#!/usr/bin/env python3
"""Thin-persona rebuild proof — reproducible #1922-pattern packet.

Derives the live canonical recovery set from current docs/artifacts (not stale
notes), runs tuple-viability via the real Stage-1 gate, optionally attempts a
spine render, and classifies blockers honestly:

  writing     — NO_STORY_POOL / POOL_TOO_SHALLOW / BAND_DEFICIT / EnrichmentGap*
  parser      — silent zero-atom parse / delimiter-shape failures (when detected)
  governance  — NO_BINDING (arc targets engine not in allowed_engines)
  other       — NO_ARC, infrastructure, unexpected render errors
  none        — TUPLE_VIABLE and (if rendered) book produced

Authority for the live set (origin/main as of 2026-07-12):
  - docs/PROGRAM_STATE.md — outstanding "4-cell rebuild proof (#1922 pattern)"
  - artifacts/qa/THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md
    → 4 REPAIRED recovery cells (#5489)
  - artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md
    → live authoritative TUPLE_VIABLE grid is **5 cells** (adds educators ×
      imposter_syndrome × shame, unblocked by the shared REFLECTION fix in #5530)
  - artifacts/qa/pilot_rebuild_20260625/SUMMARY.md — original #1922 pilot quartet
    (tracked as context/delta; not the recovery set)

Default proof set = the July 11 5-cell authoritative grid.
Governance-only NO_BINDING cells are reported separately and are NOT claimed as
writing failures.

Usage:
  PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py
  PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py --render
  PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py --set all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.gates.check_tuple_viability import (  # noqa: E402
    check_tuple_viability,
)

DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "thin_persona_rebuild_proof_2026-07-12"

# Live canonical recovery set — July 11 authoritative grid (5 cells).
# Cells 1–4 = #5489 REPAIRED surfaces; cell 5 = shared-REFLECTION related PASS.
RECOVERY_CELLS: list[dict[str, str]] = [
    {
        "persona": "educators",
        "topic": "imposter_syndrome",
        "engine": "false_alarm",
        "format": "F006",
        "role": "recovery_repaired",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + thin_persona_buildability_2026-07-11",
    },
    {
        "persona": "nyc_executives",
        "topic": "imposter_syndrome",
        "engine": "false_alarm",
        "format": "F006",
        "role": "recovery_repaired",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + thin_persona_buildability_2026-07-11",
    },
    {
        "persona": "nyc_executives",
        "topic": "anxiety",
        "engine": "spiral",
        "format": "F006",
        "role": "recovery_repaired",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + thin_persona_buildability_2026-07-11",
    },
    {
        "persona": "nyc_executives",
        "topic": "anxiety",
        "engine": "watcher",
        "format": "F006",
        "role": "recovery_repaired",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + thin_persona_buildability_2026-07-11",
    },
    {
        "persona": "educators",
        "topic": "imposter_syndrome",
        "engine": "shame",
        "format": "F006",
        "role": "recovery_related_shared_reflection",
        "source": "thin_persona_buildability_2026-07-11/SUMMARY.md live authoritative grid (5th cell)",
    },
]

# Original #1922 pilot quartet — context/delta only (PROGRAM_STATE still cites the pattern).
PILOT_1922_CELLS: list[dict[str, str]] = [
    {
        "persona": "educators",
        "topic": "burnout",
        "engine": "overwhelm",
        "format": "F006",
        "role": "pilot_1922_context",
        "source": "artifacts/qa/pilot_rebuild_20260625/SUMMARY.md",
    },
    {
        "persona": "educators",
        "topic": "imposter_syndrome",
        "engine": "false_alarm",
        "format": "F006",
        "role": "pilot_1922_context",
        "source": "artifacts/qa/pilot_rebuild_20260625/SUMMARY.md",
    },
    {
        "persona": "nyc_executives",
        "topic": "burnout",
        "engine": "overwhelm",
        "format": "F006",
        "role": "pilot_1922_context",
        "source": "artifacts/qa/pilot_rebuild_20260625/SUMMARY.md",
    },
    {
        "persona": "nyc_executives",
        "topic": "anxiety",
        "engine": "false_alarm",
        "format": "F006",
        "role": "pilot_1922_context",
        "source": "artifacts/qa/pilot_rebuild_20260625/SUMMARY.md",
    },
]

# Governance-only — report honestly; do not conflate with writing gaps.
GOVERNANCE_CELLS: list[dict[str, str]] = [
    {
        "persona": "educators",
        "topic": "boundaries",
        "engine": "overwhelm",
        "format": "F006",
        "role": "governance_nobinding",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + PROGRAM_STATE",
    },
    {
        "persona": "educators",
        "topic": "burnout",
        "engine": "shame",
        "format": "F006",
        "role": "governance_nobinding",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + PROGRAM_STATE",
    },
    {
        "persona": "educators",
        "topic": "compassion_fatigue",
        "engine": "shame",
        "format": "F006",
        "role": "governance_nobinding",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + PROGRAM_STATE",
    },
    {
        "persona": "nyc_executives",
        "topic": "burnout",
        "engine": "shame",
        "format": "F006",
        "role": "governance_nobinding",
        "source": "THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md + PROGRAM_STATE",
    },
]


@dataclass
class CellProof:
    persona: str
    topic: str
    engine: str
    format: str
    role: str
    source: str
    cell_id: str = ""
    arc_path: str = ""
    tuple_viability: str = "UNKNOWN"
    viability_errors: list[str] = field(default_factory=list)
    blocker_class: str = "unknown"
    exact_blocker: str = ""
    render_attempted: bool = False
    render_status: str = "skipped"
    render_exit_code: Optional[int] = None
    render_words: Optional[int] = None
    render_error: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.cell_id:
            self.cell_id = f"{self.persona}__{self.topic}__{self.engine}__{self.format}"
        if not self.arc_path:
            self.arc_path = (
                f"config/source_of_truth/master_arcs/"
                f"{self.persona}__{self.topic}__{self.engine}__{self.format}.yaml"
            )


def _git_sha(repo: Path) -> str:
    for args in (
        ["git", "rev-parse", "HEAD"],
        ["git", "rev-parse", "origin/main"],
    ):
        try:
            out = subprocess.check_output(
                args,
                cwd=str(repo),
                text=True,
                stderr=subprocess.DEVNULL,
            )
            sha = out.strip()
            if sha:
                return sha
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    # Archive-extract / non-git run dirs: allow operator override.
    return os.environ.get("PHOENIX_PROOF_SHA", "unknown")


def _classify_viability_errors(errors: list[str]) -> tuple[str, str]:
    if not errors:
        return "none", ""
    joined = ";".join(errors)
    if any(e.startswith("NO_BINDING") for e in errors):
        return "governance", joined
    if any(
        e.startswith(p)
        for e in errors
        for p in ("NO_STORY_POOL", "POOL_TOO_SHALLOW", "BAND_DEFICIT")
    ):
        return "writing", joined
    if any(e.startswith("NO_ARC") for e in errors):
        return "other", joined
    return "other", joined


def _classify_render_error(msg: str) -> tuple[str, str]:
    low = msg.lower()
    if "enrichmentgaperror" in low or "insufficientvariantserror" in low:
        # #5530 / tip: EnrichmentGap on REFLECTION often means the CANONICAL.txt
        # is present but `_parse_canonical_txt` yielded 0 bodies (missing second
        # `---` after YAML frontmatter). That is parser-shape, not a writing gap.
        if "parse" in low or "delimiter" in low:
            return "parser", msg.strip()[:500]
        if "slot reflection" in low or "slot_type=reflection" in low or "for slot reflection" in low:
            return "parser", msg.strip()[:500]
        return "writing", msg.strip()[:500]
    if "no_binding" in low:
        return "governance", msg.strip()[:500]
    if "tuple" in low and "viab" in low:
        return "other", msg.strip()[:500]
    return "other", msg.strip()[:500]


def _count_words(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"\S+", text))


def _select_cells(which: str) -> list[dict[str, str]]:
    if which == "recovery":
        return list(RECOVERY_CELLS)
    if which == "pilot_1922":
        return list(PILOT_1922_CELLS)
    if which == "governance":
        return list(GOVERNANCE_CELLS)
    if which == "all":
        # Deduplicate by (p,t,e,f) preferring recovery role over pilot context.
        seen: dict[tuple[str, str, str, str], dict[str, str]] = {}
        for cell in RECOVERY_CELLS + PILOT_1922_CELLS + GOVERNANCE_CELLS:
            key = (cell["persona"], cell["topic"], cell["engine"], cell["format"])
            if key not in seen or cell["role"].startswith("recovery"):
                seen[key] = cell
        return list(seen.values())
    raise SystemExit(f"Unknown --set {which!r}")


def _run_render(
    cell: CellProof,
    repo: Path,
    out_dir: Path,
    quality_profile: str,
    timeout_s: int,
) -> None:
    cell.render_attempted = True
    arc = repo / cell.arc_path
    if not arc.exists():
        cell.render_status = "blocked"
        cell.render_error = f"arc missing: {cell.arc_path}"
        cell.blocker_class = "other"
        cell.exact_blocker = cell.render_error
        return

    cell_dir = out_dir / "renders" / cell.cell_id
    cell_dir.mkdir(parents=True, exist_ok=True)
    book_path = cell_dir / "book.txt"
    log_path = cell_dir / "build.log"

    # QA tuple-viability rebuild-proof harness, not the catalog production pipeline
    # path. The chord is actually complete (spine + exercise-journeys are literal
    # below; --quality-profile defaults to "production" per this script's own
    # argparse default) — the static scanner just cannot trace the `quality_profile`
    # variable to that default, hence the allowlist rather than a code change.
    cmd = [  # CI-ALLOWLIST: legacy-registry-ok — QA harness, chord already complete (see comment above)
        sys.executable,
        str(repo / "scripts" / "run_pipeline.py"),
        "--persona",
        cell.persona,
        "--topic",
        cell.topic,
        "--arc",
        str(arc),
        "--pipeline-mode",
        "spine",
        "--quality-profile",
        quality_profile,
        "--exercise-journeys",
        "--render-book",
        "--render-formats",
        "txt",
        "--render-dir",
        str(cell_dir),
        "--no-job-check",
    ]
    if quality_profile == "draft":
        cmd.extend(["--scene-gate-mode", "draft"])

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        cell.render_status = "timeout"
        cell.render_exit_code = None
        cell.render_error = f"timeout after {timeout_s}s"
        cell.blocker_class = "other"
        cell.exact_blocker = cell.render_error
        log_path.write_text(
            (exc.stdout or "") + "\n" + (exc.stderr or "") + f"\nTIMEOUT after {timeout_s}s\n",
            encoding="utf-8",
        )
        return

    log_path.write_text(
        "CMD: " + " ".join(cmd) + "\n\n" + (proc.stdout or "") + "\n" + (proc.stderr or ""),
        encoding="utf-8",
    )
    cell.render_exit_code = proc.returncode

    # Locate rendered book (pipeline may name it variously).
    candidates = list(cell_dir.rglob("*.txt"))
    candidates = [p for p in candidates if p.name != "build.log" and p.stat().st_size > 200]
    if book_path.exists():
        candidates.insert(0, book_path)
    best = max(candidates, key=lambda p: p.stat().st_size) if candidates else None

    blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
    blocked = re.search(r"BLOCKED:\s*([^\n]+)", blob)

    if best is not None and (proc.returncode == 0 or blocked):
        cell.render_words = _count_words(best)
        if proc.returncode == 0:
            cell.render_status = "rendered"
            if cell.blocker_class in ("unknown", "none"):
                cell.blocker_class = "none"
                cell.exact_blocker = ""
            cell.notes = f"book={best.relative_to(out_dir)}"
            return
        # Book exists but production quality gates blocked exit — Layer 1 only.
        cell.render_status = "rendered_structurally_clear_gates_blocked"
        cell.blocker_class = "governance"
        cell.exact_blocker = blocked.group(1).strip() if blocked else f"exit={proc.returncode}"
        cell.notes = f"book={best.relative_to(out_dir)}; production gates blocked exit"
        return

    # Failed render — classify from log.
    bclass, exact = _classify_render_error(blob)
    # Prefer a concise exception line if present.
    m = re.search(
        r"EnrichmentGapError:\s*[^\n]{0,400}",
        blob,
    ) or re.search(
        r"(InsufficientVariantsError|NO_BINDING|EnrichmentGapError|Error|Exception)[^\n]{0,300}",
        blob,
    )
    if m:
        exact = m.group(0).strip()[:500]
        # Prefer full REFLECTION enrich line from blob when raise() was multi-line
        if "enrichmentgaperror" in exact.lower() and "reflection" not in exact.lower():
            m2 = re.search(r"No enrichable content for slot REFLECTION[^\n]*", blob)
            if m2:
                exact = ("EnrichmentGapError: " + m2.group(0)).strip()[:500]
        bclass, _ = _classify_render_error(exact)
    cell.render_status = "failed"
    cell.render_error = exact or f"exit={proc.returncode}"
    if cell.tuple_viability == "PASS":
        cell.blocker_class = bclass
        cell.exact_blocker = cell.render_error
    cell.notes = f"see renders/{cell.cell_id}/build.log"


def prove_cell(
    spec: dict[str, str],
    repo: Path,
    out_dir: Path,
    do_render: bool,
    quality_profile: str,
    timeout_s: int,
) -> CellProof:
    cell = CellProof(
        persona=spec["persona"],
        topic=spec["topic"],
        engine=spec["engine"],
        format=spec["format"],
        role=spec["role"],
        source=spec["source"],
    )
    result = check_tuple_viability(
        persona=cell.persona,
        topic=cell.topic,
        engine=cell.engine,
        format_id=cell.format,
        repo_root=repo,
    )
    cell.tuple_viability = result.status
    cell.viability_errors = list(result.errors)
    bclass, exact = _classify_viability_errors(result.errors)
    cell.blocker_class = bclass
    cell.exact_blocker = exact

    if cell.role.startswith("governance") and bclass == "governance":
        cell.notes = "governance-only NO_BINDING — not a writing gap; binding call pending"
        cell.render_status = "not_attempted_governance"
        return cell

    if do_render and result.status == "PASS":
        _run_render(cell, repo, out_dir, quality_profile, timeout_s)
    elif do_render and result.status != "PASS":
        cell.render_status = "skipped_not_viable"
        cell.notes = "render skipped because tuple viability FAIL"
    else:
        cell.render_status = "skipped"
    return cell


def _write_summary(
    out_dir: Path,
    cells: list[CellProof],
    meta: dict[str, Any],
) -> Path:
    lines: list[str] = []
    lines.append("# Thin-Persona Rebuild Proof Packet")
    lines.append("")
    lines.append(f"**Date:** {meta['date']}")
    lines.append(f"**Repo SHA:** `{meta['sha']}`")
    lines.append(f"**Set:** `{meta['set']}` (live canonical recovery grid = **5 cells**)")
    lines.append(f"**Render:** `{meta['render_mode']}`")
    lines.append(f"**Quality profile:** `{meta['quality_profile']}`")
    lines.append("")
    lines.append("## Why 5 cells (not 4)")
    lines.append("")
    lines.append(
        "PROGRAM_STATE still names the outstanding work as a **4-cell rebuild proof "
        "(#1922 pattern)** — that is the *methodology* (viability + honest spine attempt "
        "packet), not a frozen cell count. The live recovery surfaces from #5489 are "
        "four REPAIRED cells; `artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md` "
        "adds a fifth live-authoritative TUPLE_VIABLE cell "
        "(`educators × imposter_syndrome × shame × F006`) because #5530's REFLECTION "
        "parser-shape repair is topic-level and unblocks every engine on that "
        "persona/topic. This packet therefore proves the **5-cell live grid** and "
        "separately reports governance-only `NO_BINDING` cells."
    )
    lines.append("")
    lines.append("## Per-cell status")
    lines.append("")
    lines.append(
        "| Cell | Role | Tuple viability | Render | Blocker class | Exact blocker |"
    )
    lines.append("|---|---|---|---|---|---|")
    for c in cells:
        blocker = c.exact_blocker.replace("|", "\\|") if c.exact_blocker else "—"
        render = c.render_status
        if c.render_words is not None:
            render = f"{c.render_status} ({c.render_words} words)"
        lines.append(
            f"| `{c.persona} × {c.topic} × {c.engine} × {c.format}` | `{c.role}` | "
            f"**{c.tuple_viability}** | {render} | `{c.blocker_class}` | {blocker} |"
        )
    lines.append("")
    lines.append("## Blocker-class legend")
    lines.append("")
    lines.append("- `none` — viable; no active blocker for this proof layer")
    lines.append("- `writing` — missing/shallow/band-deficit STORY pool or enrichment gap")
    lines.append("- `parser` — atom file present but real parse yields zero usable atoms")
    lines.append("- `governance` — `NO_BINDING` (engine not in topic `allowed_engines`)")
    lines.append("- `other` — missing arc, infra, timeout, unexpected error")
    lines.append("")
    lines.append("## Reproduce")
    lines.append("")
    lines.append("```bash")
    lines.append("PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py")
    lines.append(
        "PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py --render "
        "--quality-profile production"
    )
    lines.append(
        "PYTHONPATH=. python3 scripts/qa/run_thin_persona_rebuild_proof.py --set all"
    )
    lines.append("```")
    lines.append("")
    lines.append("## Acceptance labeling")
    lines.append("")
    lines.append(
        "Per bestseller doctrine: a completed spine render here is at most "
        "**structurally clear** (Layer 1). `register_gate` WARN/FAIL is not claimed "
        "fixed. No bestseller-register claim is made."
    )
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append("- `SUMMARY.md` — this file")
    lines.append("- `cells.json` — machine-readable per-cell results")
    lines.append("- `meta.json` — run metadata")
    lines.append("- `renders/<cell_id>/` — optional render logs/books when `--render`")
    path = out_dir / "SUMMARY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--set",
        choices=("recovery", "pilot_1922", "governance", "all"),
        default="recovery",
        help="Which cell set to prove (default: live 5-cell recovery grid)",
    )
    ap.add_argument(
        "--render",
        action="store_true",
        help="Attempt spine render for TUPLE_VIABLE non-governance cells",
    )
    ap.add_argument(
        "--quality-profile",
        default="production",
        choices=("production", "draft"),
        help="Pipeline quality profile when --render (default: production chord)",
    )
    ap.add_argument(
        "--timeout-s",
        type=int,
        default=900,
        help="Per-cell render timeout seconds (default: 900)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output directory (default: {DEFAULT_OUT})",
    )
    ap.add_argument(
        "--repo",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (default: auto from script location)",
    )
    ap.add_argument(
        "--only",
        action="append",
        default=[],
        help=(
            "Restrict to cell_id(s) like persona__topic__engine__format "
            "(repeatable). Applied after --set selection."
        ),
    )
    args = ap.parse_args()

    repo = args.repo.resolve()
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    specs = _select_cells(args.set)
    if args.only:
        wanted = set(args.only)
        specs = [
            s
            for s in specs
            if f"{s['persona']}__{s['topic']}__{s['engine']}__{s['format']}" in wanted
        ]
        missing = wanted - {
            f"{s['persona']}__{s['topic']}__{s['engine']}__{s['format']}" for s in specs
        }
        if missing:
            raise SystemExit(f"--only cell_id(s) not in --set {args.set!r}: {sorted(missing)}")
    cells: list[CellProof] = []
    for spec in specs:
        print(
            f"[prove] {spec['persona']}×{spec['topic']}×{spec['engine']}×{spec['format']} "
            f"({spec['role']})",
            flush=True,
        )
        cell = prove_cell(
            spec,
            repo=repo,
            out_dir=out_dir,
            do_render=bool(args.render),
            quality_profile=args.quality_profile,
            timeout_s=args.timeout_s,
        )
        cells.append(cell)
        print(
            f"  -> viability={cell.tuple_viability} render={cell.render_status} "
            f"blocker={cell.blocker_class} {cell.exact_blocker}",
            flush=True,
        )

    meta = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha": _git_sha(repo),
        "set": args.set,
        "render_mode": "spine_attempted" if args.render else "viability_only",
        "quality_profile": args.quality_profile if args.render else "n/a",
        "cell_count": len(cells),
        "live_canonical_recovery_count": len(RECOVERY_CELLS),
        "why_five_not_four": (
            "July 11 SUMMARY live authoritative grid includes the 4 #5489 REPAIRED "
            "cells plus educators×imposter_syndrome×shame (shared REFLECTION fix)."
        ),
        "authority_docs": [
            "docs/PROGRAM_STATE.md",
            "artifacts/qa/THIN_PERSONA_CANONICAL_ATOM_GAP_RECONCILE_2026-07-10.md",
            "artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md",
            "artifacts/qa/pilot_rebuild_20260625/SUMMARY.md",
        ],
    }

    (out_dir / "meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "cells.json").write_text(
        json.dumps([asdict(c) for c in cells], indent=2) + "\n", encoding="utf-8"
    )
    summary = _write_summary(out_dir, cells, meta)
    print(f"\nWrote {summary}")
    print(f"Wrote {out_dir / 'cells.json'}")

    # Exit 0 always for packet generation; status is in the artifact.
    # Non-zero only on unexpected tooling crash (handled by exceptions).
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)

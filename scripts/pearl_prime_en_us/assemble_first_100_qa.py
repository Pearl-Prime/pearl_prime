#!/usr/bin/env python3
"""
Pearl_Publisher — First 100 Books QA Assembly (en_US, spine pipeline).

Wraps `scripts/generate_full_catalog.py` and `scripts/run_pipeline.py` to:
  1. Allocate BookSpecs via the canonical planner chain
     (teacher_portfolio_planner → catalog_planner) with `--plan-only`.
     Over-allocate (default 200) to absorb arc-gap drops.
  2. Pre-filter specs where no compatible master_arc exists, using the
     teacher's `allowed_engines` from teacher_persona_matrix.yaml as the
     selector. Post-PR #625 every teacher has the canonical 7 engines,
     so the engine-mismatch path is mostly dead; the filter remains
     defensive in case a teacher gets re-narrowed later.
  3. Take first N (default 100) viable specs.
  4. Assemble each via `scripts/run_pipeline.py`:
       --pipeline-mode spine
       --render-book
       --render-dir <per-book>
       --quality-profile production
       --no-job-check           (QA run; each book is its own pipeline
                                 invocation, per-book job.json per book
                                 would be pure overhead for this eval)
       --no-generate-freebies
  5. Emit per-book reports + aggregate summary.

Output tree:
  artifacts/pearl_prime_en_us/first_100_qa/
    specs/book_NNNN_topic_persona.spec.json
    filter_report.json       (dropped specs + reasons)
    renders/book_NNNN_topic_persona/
      plan.json, book.txt, quality_summary.json,
      chapter_flow_report.json, ei_v2_report.json,
      section_packet_audit.json, ...
    assembly_summary.json    (per-book outcomes + aggregate counts)

Usage:
  python3 scripts/pearl_prime_en_us/assemble_first_100_qa.py
  python3 scripts/pearl_prime_en_us/assemble_first_100_qa.py --target 100 --over-allocate 200
  python3 scripts/pearl_prime_en_us/assemble_first_100_qa.py --target 10  --seed-tag smoke

Notes:
  - Quality gates fail for the majority of books today (chapter_flow,
    EI V2, book_pass). `book.txt` is still written when gates fail;
    the summary flags both `quality_gates_pass` and `has_book_txt` so
    a reviewer can separate structural-failure books from no-output books.
  - This is a QA/evaluation tool, not a production release tool. No wave
    selection, no upload, no TTS. See docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md
    for the listening-evaluation companion protocol.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
OUT_ROOT = REPO_ROOT / "artifacts" / "pearl_prime_en_us" / "first_100_qa"
GENERATE_FULL_CATALOG = REPO_ROOT / "scripts" / "generate_full_catalog.py"
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
TEACHER_MATRIX = REPO_ROOT / "config" / "catalog_planning" / "teacher_persona_matrix.yaml"

# Per-book timeout — spine+render+quality typically runs 30s–3min; 8min is safety margin.
BOOK_TIMEOUT_SEC = 480


# -----------------------------------------------------------------------------
# Teacher × engine compatibility
# -----------------------------------------------------------------------------

_TEACHER_ENGINES: dict[str, set[str]] | None = None


def load_teacher_allowed_engines() -> dict[str, set[str]]:
    """Return {teacher_id: {allowed_engine, ...}} from teacher_persona_matrix.yaml."""
    import yaml
    data = yaml.safe_load(TEACHER_MATRIX.read_text()) or {}
    out: dict[str, set[str]] = {}
    for teacher_id, cfg in (data.get("teachers") or {}).items():
        out[teacher_id] = set(cfg.get("allowed_engines") or [])
    return out


def teacher_allowed_engines(teacher_id: str) -> set[str]:
    global _TEACHER_ENGINES
    if _TEACHER_ENGINES is None:
        _TEACHER_ENGINES = load_teacher_allowed_engines()
    return _TEACHER_ENGINES.get(teacher_id, set())


def engine_from_arc_path(arc_path: Path) -> str | None:
    """Arc filename: {persona}__{topic}__{engine}__{format}.yaml. Engine = token[2]."""
    parts = arc_path.stem.split("__")
    return parts[2] if len(parts) >= 3 else None


def pick_compatible_arc(persona_id: str, topic_id: str, teacher_id: str) -> tuple[Path | None, str | None]:
    """Return (arc_path, drop_reason).

    drop_reason is None if a compatible arc was found.
    Defensively filters arcs by the teacher's allowed_engines — post-PR #625
    this is a no-op for non-narrow teachers, but preserved so the wrapper
    still drops cleanly if a teacher gets re-narrowed in the future.
    """
    matches = sorted(ARCS_ROOT.glob(f"{persona_id}__{topic_id}__*.yaml"))
    if not matches:
        return None, "no_master_arc"

    if teacher_id in (None, "default_teacher"):
        return matches[0], None

    allowed = teacher_allowed_engines(teacher_id)
    if not allowed:
        # Teacher not in matrix or no restrictions — permissive.
        return matches[0], None

    for arc in matches:
        eng = engine_from_arc_path(arc)
        if eng and eng in allowed:
            return arc, None

    available = sorted({engine_from_arc_path(a) or "?" for a in matches})
    return None, f"teacher_engine_mismatch (teacher={teacher_id} allowed={sorted(allowed)} arcs_have={available})"


# -----------------------------------------------------------------------------
# Step 1: allocate BookSpecs via the canonical planner chain
# -----------------------------------------------------------------------------

def allocate_specs(out_dir: Path, over_allocate: int, seed: str) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(GENERATE_FULL_CATALOG),
        "--max-books", str(over_allocate),
        "--skip-wave-selection",
        "--plan-only",
        "--candidates-dir", str(out_dir),
        "--seed", seed,
    ]
    print(f"[allocate] {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=600)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"generate_full_catalog failed (exit {r.returncode})")
    return len(list(out_dir.glob("*.spec.json")))


# -----------------------------------------------------------------------------
# Step 2: filter by arc existence + teacher engine compatibility
# -----------------------------------------------------------------------------

def load_specs_with_arcs(spec_dir: Path, target: int) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    dropped: list[dict] = []
    for spec_file in sorted(spec_dir.glob("*.spec.json")):
        spec = json.loads(spec_file.read_text())
        persona = spec.get("persona_id")
        topic = spec.get("topic_id")
        teacher = spec.get("teacher_id") or "default_teacher"
        arc, drop_reason = pick_compatible_arc(persona, topic, teacher)
        if arc is None:
            dropped.append({
                "spec_file": spec_file.name,
                "persona": persona,
                "topic": topic,
                "teacher": teacher,
                "reason": drop_reason,
            })
            continue
        kept.append({
            "spec_file": spec_file.name,
            "spec": spec,
            "arc_path": str(arc.relative_to(REPO_ROOT)),
        })
        if len(kept) >= target:
            break
    return kept, dropped


# -----------------------------------------------------------------------------
# Step 3: assemble a single book via run_pipeline (spine mode)
# -----------------------------------------------------------------------------

def assemble_book(item: dict, render_dir: Path) -> dict:
    spec = item["spec"]
    render_dir.mkdir(parents=True, exist_ok=True)

    atoms_root = str(REPO_ROOT / "atoms")
    teacher_id = spec.get("teacher_id") or "default_teacher"

    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic", spec["topic_id"],
        "--persona", spec["persona_id"],
        "--arc", str(REPO_ROOT / item["arc_path"]),
        "--teacher", teacher_id,
        "--seed", spec["seed"],
        "--out", str(render_dir / "plan.json"),
        "--atoms-model", spec.get("atoms_model", "legacy"),
        "--atoms-root", atoms_root,
        "--pipeline-mode", "spine",
        "--render-book",
        "--render-dir", str(render_dir),
        "--quality-profile", "production",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    if spec.get("angle_id"):
        cmd += ["--angle", spec["angle_id"]]
    if spec.get("series_id"):
        cmd += ["--series", spec["series_id"]]
    if spec.get("installment_number") is not None:
        cmd += ["--installment", str(spec["installment_number"])]

    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=BOOK_TIMEOUT_SEC)
        returncode = r.returncode
        stdout, stderr = r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        returncode = -9
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\nTIMEOUT after {BOOK_TIMEOUT_SEC}s"
    elapsed = time.time() - t0

    (render_dir / "run.log").write_text(
        f"# cmd: {' '.join(cmd)}\n# exit: {returncode}\n# elapsed: {elapsed:.1f}s\n\n"
        f"--- STDOUT ---\n{stdout}\n\n--- STDERR ---\n{stderr}\n"
    )

    qs_path = render_dir / "quality_summary.json"
    quality_summary = None
    if qs_path.exists():
        try:
            quality_summary = json.loads(qs_path.read_text())
        except Exception as e:  # pragma: no cover — defensive
            quality_summary = {"parse_error": str(e)}

    book_txt = render_dir / "book.txt"
    has_book_txt = book_txt.exists() and book_txt.stat().st_size > 0
    book_word_count = len(book_txt.read_text().split()) if has_book_txt else None

    return {
        "topic": spec["topic_id"],
        "persona": spec["persona_id"],
        "teacher": teacher_id,
        "brand": spec.get("brand_id"),
        "returncode": returncode,
        "elapsed_sec": round(elapsed, 1),
        "has_book_txt": has_book_txt,
        "book_word_count": book_word_count,
        "quality_gates_pass": returncode == 0,
        "quality_summary": quality_summary,
    }


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=100, help="Books to assemble (default 100)")
    ap.add_argument("--over-allocate", type=int, default=200, help="Specs to request from planner (default 200; absorbs arc-gap drops)")
    ap.add_argument("--seed-tag", default=None, help="Override seed tag (default: first100_qa_YYYYMMDD)")
    args = ap.parse_args()

    if args.seed_tag is None:
        args.seed_tag = f"first100_qa_{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Step 1: allocate
    spec_dir = OUT_ROOT / "specs"
    n_specs = allocate_specs(spec_dir, args.over_allocate, args.seed_tag)
    print(f"[allocate] emitted {n_specs} BookSpecs → {spec_dir}", flush=True)

    # Step 2: filter
    kept, dropped = load_specs_with_arcs(spec_dir, args.target)
    filter_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "over_allocate": args.over_allocate,
        "specs_allocated": n_specs,
        "kept": len(kept),
        "dropped": len(dropped),
        "dropped_details": dropped,
    }
    (OUT_ROOT / "filter_report.json").write_text(json.dumps(filter_report, indent=2))
    print(f"[filter] kept {len(kept)} / dropped {len(dropped)}", flush=True)
    if len(kept) < args.target:
        print(
            f"[filter] WARNING: only {len(kept)} viable specs; target was {args.target}. "
            f"Rerun with larger --over-allocate.",
            flush=True,
        )

    # Step 3: assemble
    renders_root = OUT_ROOT / "renders"
    renders_root.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    t_start = time.time()
    for i, item in enumerate(kept):
        render_name = f"book_{i:04d}_{item['spec']['topic_id']}_{item['spec']['persona_id']}"
        render_dir = renders_root / render_name
        print(
            f"[{i+1}/{len(kept)}] assemble {item['spec']['topic_id']} × {item['spec']['persona_id']} "
            f"(teacher={item['spec'].get('teacher_id') or 'default_teacher'}, "
            f"brand={item['spec'].get('brand_id')})",
            flush=True,
        )
        outcome = assemble_book(item, render_dir)
        outcome["idx"] = i
        outcome["render_name"] = render_name
        outcome["spec_file"] = item["spec_file"]
        results.append(outcome)

        if (i + 1) % 10 == 0 or (i + 1) == len(kept):
            n_pass = sum(1 for r in results if r["quality_gates_pass"])
            n_have_txt = sum(1 for r in results if r["has_book_txt"])
            elapsed_total = time.time() - t_start
            eta = (elapsed_total / (i + 1)) * (len(kept) - i - 1)
            print(
                f"  ▸ running: {i+1} done — {n_pass} pass quality gates, "
                f"{n_have_txt} have book.txt. elapsed {elapsed_total/60:.1f}m, ETA {eta/60:.1f}m",
                flush=True,
            )

    # Step 4: summary
    n_pass = sum(1 for r in results if r["quality_gates_pass"])
    n_have_txt = sum(1 for r in results if r["has_book_txt"])
    mean_wc = int(sum((r["book_word_count"] or 0) for r in results) / max(1, n_have_txt))
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "assembled": len(results),
        "quality_gates_pass": n_pass,
        "have_book_txt": n_have_txt,
        "mean_word_count_of_rendered": mean_wc,
        "elapsed_sec": round(time.time() - t_start, 1),
        "books": results,
    }
    (OUT_ROOT / "assembly_summary.json").write_text(json.dumps(summary, indent=2))

    print(
        f"\n=== DONE ===\n"
        f"assembled:            {len(results)}\n"
        f"quality_gates_pass:   {n_pass}\n"
        f"rendered book.txt:    {n_have_txt}\n"
        f"mean word count:      {mean_wc}\n"
        f"total elapsed:        {summary['elapsed_sec']/60:.1f} min\n"
        f"artifacts:            {OUT_ROOT}\n",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

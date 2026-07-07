#!/usr/bin/env python3
"""
Flagship EXERCISE five-layer integrity gate (twelve-shape continuity books).

Ch1 is lean by design (content_only — the approved golden chapter). Every
other chapter's EXERCISE slot must render the FULL practice_library compose:
bridge + intro + description + aha + integration. A downstream pass (most
often `_strip_secular_violation_paragraphs`, which silently drops any
paragraph matching the secular-frame blocklist — e.g. "loving kindness") can
gut a chapter down to 2-3 surviving layers while the pipeline still exits 0,
because nothing upstream checks that every layer it composed actually
survived into the rendered book. That is exactly what happened with the
`med_019` ("Loving Kindness Expanding") pick on ch7 of the 2026-07-07
flagship 2h retarget: the plan-assigned exercise itself is secular-blocklist
incompatible, so `intro` and `description` vanished from the render while
`bridge`/`aha`/`integration` survived, and no gate caught it.

This gate re-composes each chapter's assigned exercise_id directly via
`_try_practice_library_by_id` (the same function the pipeline calls) to get
the ground-truth 5 layers, then asserts each one appears verbatim in the
rendered book text. Mutation-testable: delete any one layer's text from a
render and this gate goes RED.

Usage:
  python3 scripts/ci/check_flagship_exercise_five_layer.py --book path/to/book.txt \\
      --plan config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml \\
      --seed flagship_phase2_layer6
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

PIPELINE_SCRIPT = REPO_ROOT / "scripts/run_pipeline.py"
ARC_PATH = (
    REPO_ROOT
    / "config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml"
)
DEFAULT_PLAN = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
DEFAULT_SEED = "flagship_phase2_layer6"
DEFAULT_TOPIC = "anxiety"
DEFAULT_PERSONA = "gen_z_professionals"
DEFAULT_ENGINE = "overwhelm"
# The seed actually used at composition time is built in two stages, both of
# which must be reconstructed exactly or every chapter's deterministic
# aha/intro rotation offset mismatches the real render (false positive on
# every chapter, not just a genuinely broken one):
#   1. scripts/run_pipeline.py: seed = f"spine:{topic_id}:{persona_id}:{cli_seed}"
#   2. enrichment_select.select_enrichment: seed = f"{seed}:engine:{engine}"
#      (only when the arc binds an engine, which the flagship arc always does)


def _self_render(render_dir: Path) -> Path:
    """Rebuild the canonical flagship 2h book via the production invocation."""
    cmd = [
        sys.executable,
        str(PIPELINE_SCRIPT),
        "--topic", DEFAULT_TOPIC,
        "--persona", DEFAULT_PERSONA,
        "--arc", str(ARC_PATH),
        "--pipeline-mode", "spine",
        "--runtime-format", "extended_book_2h",
        "--quality-profile", "production",
        "--exercise-journeys",
        "--no-job-check",
        "--render-book",
        "--render-dir", str(render_dir),
        "--seed", DEFAULT_SEED,
    ]
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=600, check=False)
    book_path = render_dir / "book.txt"
    if not book_path.exists():
        raise RuntimeError("self-render did not emit book.txt")
    return book_path


def _split_chapters(book_text: str) -> dict[int, str]:
    parts = re.split(r"\n(?=Chapter \d+)", book_text.strip())
    out: dict[int, str] = {}
    for part in parts:
        m = re.match(r"Chapter (\d+)", part)
        if m:
            out[int(m.group(1))] = part
    return out


def check(book_path: Path, plan_path: Path, seed: str) -> list[str]:
    import yaml

    from phoenix_v4.planning.enrichment_select import _try_practice_library_by_id

    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}
    chapters = plan.get("chapters") or []
    book_text = book_path.read_text(encoding="utf-8")
    rendered = _split_chapters(book_text)

    failures: list[str] = []
    for entry in chapters:
        ch_num = int(entry.get("chapter") or 0)
        exercise_id = str(entry.get("exercise_id") or "").strip()
        if not ch_num or not exercise_id:
            continue
        if ch_num == 1:
            continue  # golden lean chapter — content_only by design, excluded
        ch_text = rendered.get(ch_num)
        if not ch_text:
            failures.append(f"ch{ch_num}: chapter not found in rendered book")
            continue

        chapter_index0 = ch_num - 1
        composed = _try_practice_library_by_id(exercise_id, chapter_index0, seed)
        if not composed:
            failures.append(
                f"ch{ch_num}: exercise_id {exercise_id!r} did not compose "
                f"via practice_library (resolution failure, not a layer check)"
            )
            continue

        full_text, resolved_id = composed
        layers = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        # compose_exercise emits at most 5 blocks: bridge, [introduction cue],
        # intro, description, aha, integration — "introduction" is usually
        # empty (superseded by intro), so 4-5 non-empty blocks is normal.
        missing = [
            layer[:70] for layer in layers
            if layer not in ch_text
        ]
        if missing:
            failures.append(
                f"ch{ch_num} ({exercise_id} -> {resolved_id}): "
                f"{len(missing)}/{len(layers)} layer(s) missing from render: "
                f"{missing}"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", type=Path, default=None, help="omit to self-render the canonical flagship 2h build")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--seed", type=str, default=DEFAULT_SEED, help="raw CLI --seed used at build time")
    parser.add_argument("--topic", type=str, default=DEFAULT_TOPIC)
    parser.add_argument("--persona", type=str, default=DEFAULT_PERSONA)
    parser.add_argument("--engine", type=str, default=DEFAULT_ENGINE)
    args = parser.parse_args()

    spine_seed = f"spine:{args.topic}:{args.persona}:{args.seed}"
    effective_seed = f"{spine_seed}:engine:{args.engine}" if args.engine else spine_seed

    if args.book is not None:
        failures = check(args.book, args.plan, effective_seed)
    else:
        with tempfile.TemporaryDirectory(prefix="flagship_exercise_gate_") as tmp:
            try:
                book_path = _self_render(Path(tmp))
            except RuntimeError as exc:
                print(f"FAIL: {exc}", file=sys.stderr)
                return 3
            failures = check(book_path, args.plan, effective_seed)

    if failures:
        print("❌ FLAGSHIP EXERCISE FIVE-LAYER GATE — FAILED", file=sys.stderr)
        for f in failures:
            print(f"   ✗ {f}", file=sys.stderr)
        return 1
    print("✅ FLAGSHIP EXERCISE FIVE-LAYER GATE — ALL CHAPTERS INTACT (ch1 excluded, lean by design)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Pilot: Spine → KnobApply → BeatmapCompile → EnrichmentSelect → compose_from_enriched_book.

Standalone (does not import run_pipeline). Writes book.txt, book_plan.json,
enrichment_audit.json, budget.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    parser = argparse.ArgumentParser(description="Pilot spine → enrichment → prose pipeline")
    parser.add_argument("--topic", required=True, help="Topic id (e.g. anxiety)")
    parser.add_argument("--persona", required=True, help="Persona id (e.g. gen_z_professionals)")
    parser.add_argument("--teacher", default="", help="Teacher id for atom overlay (e.g. ahjan)")
    parser.add_argument("--format", dest="runtime_format", default="standard_book")
    parser.add_argument("--seed", default="pilot_v1", help="Deterministic selection seed")
    parser.add_argument("--output-dir", required=True, help="Directory for artifacts")
    parser.add_argument("--additive-enrichment", action="store_true", help="Layer all sources per slot: persona first → registry always → teacher third")
    args = parser.parse_args()

    from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
    from phoenix_v4.planning.enrichment_select import (
        EnrichmentRequest,
        apply_depth_pass,
        budget_from_enriched,
        dump_enriched_book_json,
        select_enrichment,
    )
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
    from phoenix_v4.rendering.book_renderer import clean_for_delivery
    from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book

    topic = args.topic.strip()
    persona = args.persona.strip()
    teacher = args.teacher.strip() or None
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    spine = load_spine(topic, REPO_ROOT)
    knobs = load_knob_profile(topic, REPO_ROOT)
    shaped = apply_knobs(
        spine,
        knobs,
        runtime_format=args.runtime_format,
        persona_id=persona,
        repo_root=REPO_ROOT,
    )
    engines = load_topic_engines(topic, REPO_ROOT)
    fmt_spec = load_format_spec(args.runtime_format, REPO_ROOT)
    beatmap = compile_beatmap(shaped, engines, fmt_spec, REPO_ROOT)

    req = EnrichmentRequest(
        beatmap=beatmap,
        teacher_id=teacher,
        persona_id=persona,
        topic_id=topic,
        seed=args.seed,
        additive_enrichment=args.additive_enrichment,
    )
    enriched = select_enrichment(req, REPO_ROOT)

    depth_map_path = REPO_ROOT / "config" / "depth" / "depth_module_map.yaml"
    if yaml is None:
        raise RuntimeError("PyYAML is required for depth_module_map.yaml")
    depth_map = yaml.safe_load(depth_map_path.read_text(encoding="utf-8"))
    enriched = apply_depth_pass(enriched, depth_map, repo_root=REPO_ROOT)

    prose = compose_from_enriched_book(enriched, quality_profile="draft")
    # Match run_pipeline spine mode: full-manuscript clean (section-strip + cross-chapter dedup).
    prose = clean_for_delivery(prose)

    (out_dir / "book.txt").write_text(prose, encoding="utf-8")
    (out_dir / "book_plan.json").write_text(dump_enriched_book_json(enriched), encoding="utf-8")
    (out_dir / "enrichment_audit.json").write_text(
        json.dumps(enriched.enrichment_audit, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "budget.json").write_text(
        json.dumps(budget_from_enriched(enriched), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote pilot outputs under {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

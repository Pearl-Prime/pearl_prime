#!/usr/bin/env python3
"""
Pilot: Spine → KnobApply → BeatmapCompile → EnrichmentSelect + depth →
legacy template slice + section_packet_composer → book.txt.

Side pipeline — does not change run_pipeline defaults.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    parser = argparse.ArgumentParser(description="Legacy template section packet pilot")
    parser.add_argument("--topic", default="anxiety")
    parser.add_argument("--persona", default="gen_z_professionals")
    parser.add_argument("--teacher", default="ahjan")
    parser.add_argument("--format", dest="runtime_format", default="standard_book")
    parser.add_argument("--seed", default="legacy_packet_pilot_v1")
    parser.add_argument(
        "--output-dir",
        default="artifacts/pilot/stacked_packet/anxiety",
    )
    parser.add_argument(
        "--legacy-library",
        default="v2_somatic",
        help="library_id from config/templates/legacy_template_index.yaml (v2_somatic = 12×10 somatic YAML)",
    )
    parser.add_argument(
        "--exercise-journeys",
        action="store_true",
        help="Attach thesis-aligned exercise journeys after depth pass (enrichment_select)",
    )
    args = parser.parse_args()

    if yaml is None:
        print("PyYAML required", file=sys.stderr)
        return 1

    from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
    from phoenix_v4.planning.enrichment_select import (
        EnrichmentRequest,
        apply_depth_pass,
        attach_exercise_journeys,
        budget_from_enriched,
        peek_registry_content_for_beatmap_slot,
        select_enrichment,
    )
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
    from phoenix_v4.planning.legacy_template_loader import (
        load_legacy_section,
        load_transition_bridge_for_chapter_start,
    )
    from phoenix_v4.planning.injection_resolver import BookSlotTracker
    from phoenix_v4.planning.story_planner import build_story_schedule, describe_schedule
    from phoenix_v4.rendering.section_packet_composer import compose_section_packet

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
    ch_by_num = {ch.number: ch for ch in shaped.chapters}

    engines = load_topic_engines(topic, REPO_ROOT)
    fmt_spec = load_format_spec(args.runtime_format, REPO_ROOT)
    beatmap = compile_beatmap(shaped, engines, fmt_spec, REPO_ROOT)
    bm_ch_by_num = {ch.number: ch for ch in beatmap.chapters}

    req = EnrichmentRequest(
        beatmap=beatmap,
        teacher_id=teacher,
        persona_id=persona,
        topic_id=topic,
        seed=args.seed,
    )
    enriched = select_enrichment(req, REPO_ROOT)

    depth_map_path = REPO_ROOT / "config" / "depth" / "depth_module_map.yaml"
    depth_map = yaml.safe_load(depth_map_path.read_text(encoding="utf-8"))
    enriched = apply_depth_pass(enriched, depth_map, repo_root=REPO_ROOT)
    if args.exercise_journeys:
        journey_seed = f"{args.seed}:legacy_packet_journey"
        enriched = attach_exercise_journeys(
            enriched,
            seed=journey_seed,
            enabled=True,
            repo_root=REPO_ROOT,
        )

    # Build the full-book story schedule once: 3 full-arch stories per phase,
    # each character's arc spread across their chapter's 3 SCENE slots.
    story_schedule = build_story_schedule(
        persona_id=persona,
        topic=topic,
        seed=args.seed,
        repo_root=REPO_ROOT,
        n_per_phase=3,
    )
    print(describe_schedule(story_schedule))

    # One tracker per book: enforces no-repeat variant IDs and collision-family spread
    # across all 12 chapters × all slot types (HOOK recognition, SCENE injection, etc.).
    slot_tracker = BookSlotTracker()

    audit_rows: List[Dict[str, Any]] = []
    chapter_words: Dict[int, int] = defaultdict(int)
    total_w = 0
    legacy_hits = 0
    bridge_hits = 0
    enrichment_hits = 0
    depth_hits = 0
    under_target_count = 0
    thin_200 = 0
    target_total = 54000
    target_per_section_nominal = 450

    book_parts: List[str] = []

    for ech in enriched.chapters:
        ch_num = ech.number
        bm_ch = bm_ch_by_num.get(ch_num)
        spine_ch = ch_by_num.get(ch_num)
        thesis = getattr(spine_ch, "thesis", "") if spine_ch else ech.thesis
        role = getattr(spine_ch, "role", "") if spine_ch else ech.role
        emotional_job = getattr(spine_ch, "emotional_job", "") if spine_ch else ""

        chapter_header = f"Chapter {ch_num}\n{ech.working_title}\n\n"
        book_parts.append(chapter_header)

        bm_slot_count = len(bm_ch.slots) if bm_ch else 0

        for slot_idx, slot in enumerate(ech.slots):
            section_idx1 = slot_idx + 1
            bridge_text = None
            if slot_idx == 0 and ch_num > 1:
                bridge_text = load_transition_bridge_for_chapter_start(ch_num, repo_root=REPO_ROOT)
                if bridge_text:
                    bridge_hits += 1

            legacy_dict = None
            if bm_slot_count and slot_idx < bm_slot_count:
                # Rotate variant families across chapters so each chapter gets distinct template text.
                # v2_somatic has 5 variants (F1-F5) per section; cycling by chapter index ensures
                # chapters 1-5 use F1-F5 respectively, chapters 6-10 cycle again, etc.
                _variant_families = ["F1", "F2", "F3", "F4", "F5"]
                _variant_family = _variant_families[(ch_num - 1) % len(_variant_families)]
                # Only load template text for slots 1-10 (the somatic grid); depth slots beyond 10
                # use depth_module content only and don't need a template scaffold.
                _sec_idx = min(section_idx1, 10)
                legacy = load_legacy_section(
                    args.legacy_library,
                    ch_num,
                    _sec_idx,
                    _variant_family,
                    repo_root=REPO_ROOT,
                )
                if legacy.text.strip():
                    legacy_dict = {"text": legacy.text, "word_count": legacy.word_count}
                    legacy_hits += 1

            spine_context = {
                "thesis": thesis,
                "role": role,
                "emotional_job": emotional_job,
                "working_title": ech.working_title,
                "topic": topic,
                "topic_id": topic,
                "persona_id": persona,
                "teacher_id": teacher,
                "seed": args.seed,
            }
            beat_slot: Dict[str, Any] = {}
            if bm_ch and slot_idx < len(bm_ch.slots):
                s = bm_ch.slots[slot_idx]
                beat_slot = {
                    "slot_type": s.slot_type,
                    "target_words": s.target_words,
                    "weight": s.weight,
                }

            teacher_layer = None
            enrichment_body = slot.content
            if bm_ch and slot_idx < bm_slot_count and slot.source == "teacher_atom":
                teacher_layer = slot.content
                reg_stack = peek_registry_content_for_beatmap_slot(
                    beatmap=beatmap,
                    chapter_number=ch_num,
                    slot_index=slot_idx,
                    topic_id=topic,
                    teacher_id=teacher,
                    persona_id=persona,
                    seed=args.seed,
                )
                enrichment_body = reg_stack if reg_stack.strip() else ""

            enr = {
                "content": enrichment_body,
                "source": slot.source,
                "enrichment_applied": list(slot.enrichment_applied or []),
                "exercise_phase": getattr(slot, "exercise_phase", None),
            }
            if slot.source not in ("gap",):
                enrichment_hits += 1
            if str(slot.source).startswith("depth_module:"):
                depth_hits += 1

            tw = beat_slot.get("target_words") if beat_slot else target_per_section_nominal
            if not isinstance(tw, int) or tw <= 0:
                tw = target_per_section_nominal
            # Floor at nominal so beatmap standard_book small targets don't truncate injection.
            # Also write back into beat_slot so the composer's bm_slot override uses the floored value.
            tw = max(tw, target_per_section_nominal)
            if beat_slot:
                beat_slot["target_words"] = tw

            ex_phase = getattr(slot, "exercise_phase", None)
            if not (bm_slot_count and slot_idx < bm_slot_count):
                ex_phase = None

            packet = compose_section_packet(
                chapter_index=ch_num,
                section_index=section_idx1,
                section_type=slot.slot_type,
                target_words=tw,
                spine_context=spine_context,
                beatmap_slot=beat_slot,
                enrichment_slot=enr,
                legacy_template_section=legacy_dict,
                bridge_text=bridge_text,
                quality_profile="draft",
                exercise_phase=ex_phase,
                teacher_atom_content=teacher_layer,
                story_schedule=story_schedule,
                slot_tracker=slot_tracker,
            )

            body = packet["text"]
            wc = int(packet["word_count"])
            total_w += wc
            chapter_words[ch_num] += wc
            if packet["under_target"]:
                under_target_count += 1
            if wc < 200:
                thin_200 += 1

            book_parts.append(body + "\n\n")

            audit_rows.append(
                {
                    "chapter": ch_num,
                    "section_index": section_idx1,
                    "slot_type": slot.slot_type,
                    "word_count": wc,
                    "target_words": tw,
                    "under_target": packet["under_target"],
                    "sources_used": packet["sources_used"],
                    "legacy_warnings": legacy.warnings,
                    "composer_warnings": packet["warnings"],
                }
            )

    book_txt = "".join(book_parts).strip() + "\n"
    (out_dir / "book.txt").write_text(book_txt, encoding="utf-8")
    (out_dir / "section_packet_audit.json").write_text(
        json.dumps(audit_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    budget = budget_from_enriched(enriched)
    budget["legacy_template_library"] = args.legacy_library
    budget["packet_total_words"] = total_w
    budget["chapter_words_from_packets"] = {str(k): v for k, v in sorted(chapter_words.items())}
    # Include variety stats from the BookSlotTracker so the audit shows collision-family spread.
    budget["slot_tracker_variety"] = {
        "unique_variants_used": len(slot_tracker._used_ids),
        "collision_family_counts": dict(slot_tracker._family_counts),
        "slot_history": {k: v for k, v in slot_tracker._slot_history.items()},
    }
    (out_dir / "word_budget.json").write_text(
        json.dumps(budget, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    n_sections = len(audit_rows)
    avg = total_w / n_sections if n_sections else 0
    at_400 = sum(1 for r in audit_rows if r["word_count"] >= 400)

    readme = f"""# Legacy template packet pilot — {topic}

## Parameters

- topic: {topic}
- persona: {persona}
- teacher: {teacher or "(none)"}
- runtime_format: {args.runtime_format}
- seed: {args.seed}
- legacy_library: {args.legacy_library}

## Outputs

- `book.txt` — stitched section packets
- `section_packet_audit.json` — per-section sources and warnings
- `word_budget.json` — beatmap/enrichment budget plus packet totals

## Note

Default `--legacy-library` is `v2_somatic` when `template_expand2/_extracted/.../sections_somatic_v2/`
is present (12×10×5 somatic YAML). Use `--legacy-library v4_therapeutic` only for the sparse
2-section bootstrap tree. **Stacking:** teacher slots use registry peek + `teacher_atom` layer;
composer stacks bridge → journey → legacy → enrichment → teacher → depth.

## Measured (from this run)

- Total words (packets): {total_w}
- Sections: {n_sections}
- Average words/section: {avg:.1f}
- Sections with legacy scaffold text: {legacy_hits}
- Bridge inserts (chapter starts >1): {bridge_hits}
- Under beatmap target_words: {under_target_count}
- Thin sections (<200 words): {thin_200}
- Sections >=400 words: {at_400}
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"Wrote pilot outputs under {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

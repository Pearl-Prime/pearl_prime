#!/usr/bin/env python3
"""Planner-owned spine packet integrity gate.

This gate protects the contract that duplicate authored composite packets must be
resolved in planning/enrichment, not masked later by renderer-side dedupe.

Default behavior runs a small canonical probe corpus and blocks when:
  1. A chapter reuses the same composite doctrine/reflection source_id.
  2. Two composite packets in one chapter share multiple substantive sentences.
  3. Repeated authored STORY/REFLECTION/TEACHER_DOCTRINE packets disappear before
     additive compose is selected.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from phoenix_v4.planning.beatmap_compile import (  # noqa: E402
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
)
from phoenix_v4.planning.enrichment_select import (  # noqa: E402
    EnrichmentRequest,
    chapter_composite_sentence_overlap_violations,
    chapter_duplicate_doctrine_source_violations,
    select_enrichment,
)
from phoenix_v4.planning.chapter_planner import (  # noqa: E402
    assign_chapter_purpose_contracts,
    resolve_effective_max_exercises,
)
from phoenix_v4.planning.knob_apply import (  # noqa: E402
    apply_knobs,
    load_knob_profile,
    load_spine,
)
from phoenix_v4.rendering.chapter_composer import _requires_additive_compose  # noqa: E402
from phoenix_v4.rendering.golden_chapter_synthesis import build_virtual_slot_streams  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "artifacts" / "qa" / "spine_packet_integrity"
DEFAULT_JSON = DEFAULT_REPORT_DIR / "SPINE_PACKET_INTEGRITY.json"
DEFAULT_MD = DEFAULT_REPORT_DIR / "SPINE_PACKET_INTEGRITY.md"
REPEATABLE_TYPES = ("STORY", "REFLECTION", "TEACHER_DOCTRINE")


@dataclass(frozen=True)
class CanonicalCase:
    case_id: str
    topic: str
    persona: str
    runtime_format: str
    seed: str
    chapter: int


CANONICAL_CASES: tuple[CanonicalCase, ...] = (
    CanonicalCase(
        case_id="burnout_corporate_managers_ch2_seed4242",
        topic="burnout",
        persona="corporate_managers",
        runtime_format="standard_book",
        seed="4242",
        chapter=2,
    ),
)


def _build_enriched(case: CanonicalCase, repo_root: Path) -> Any:
    fmt = load_format_spec(case.runtime_format, repo_root)
    spine = load_spine(case.topic, repo_root, runtime_format=case.runtime_format)
    shaped = apply_knobs(
        spine,
        load_knob_profile(case.topic, repo_root),
        runtime_format=case.runtime_format,
    )
    beatmap = compile_beatmap(
        shaped,
        load_topic_engines(case.topic, repo_root),
        fmt,
        repo_root=repo_root,
    )
    return select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
            persona_id=case.persona,
            topic_id=case.topic,
            seed=case.seed,
        ),
        repo_root=repo_root,
    )


def audit_case(case: CanonicalCase, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    enriched = _build_enriched(case, repo_root)
    chapter = enriched.chapters[case.chapter - 1]

    source_dupes = chapter_duplicate_doctrine_source_violations(chapter.slots)
    sentence_dupes = chapter_composite_sentence_overlap_violations(chapter.slots)
    slot_types_live = [
        str(getattr(slot, "slot_type", "") or "").strip().upper()
        for slot in chapter.slots
        if str(getattr(slot, "content", "") or "").strip()
        and not str(getattr(slot, "content", "") or "").strip().startswith("[CONTENT GAP")
    ]
    virtual_types, _ = build_virtual_slot_streams(
        chapter.slots,
        chapter_index0=case.chapter - 1,
    )
    live_counts = Counter(slot_types_live)
    virtual_counts = Counter(t.strip().upper() for t in virtual_types)
    count_mismatches = []
    for slot_type in REPEATABLE_TYPES:
        if live_counts.get(slot_type, 0) != virtual_counts.get(slot_type, 0):
            count_mismatches.append(
                {
                    "slot_type": slot_type,
                    "live_count": live_counts.get(slot_type, 0),
                    "virtual_count": virtual_counts.get(slot_type, 0),
                }
            )

    additive_required = _requires_additive_compose(virtual_types)
    repeated_packet_present = any(live_counts.get(t, 0) > 1 for t in REPEATABLE_TYPES)

    failures: list[str] = []
    if source_dupes:
        failures.append("duplicate composite source_id reused within chapter")
    if sentence_dupes:
        failures.append("composite packets share repeated substantive sentences")
    if count_mismatches:
        failures.append("repeatable packet counts changed before compose")
    if repeated_packet_present and not additive_required:
        failures.append("repeated packets did not trigger additive compose")

    contracts = assign_chapter_purpose_contracts(
        len(enriched.chapters),
        case.runtime_format,
    )
    contract = contracts[case.chapter - 1]
    effective_max = resolve_effective_max_exercises(
        contract.max_exercises,
        case.runtime_format,
    )
    exercise_count = sum(
        1
        for slot in chapter.slots
        if str(getattr(slot, "slot_type", "") or "").strip().upper() == "EXERCISE"
    )
    if exercise_count > effective_max:
        failures.append(
            f"chapter has {exercise_count} EXERCISE slots but planner contract allows {effective_max}"
        )

    return {
        **asdict(case),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "duplicate_source_violations": source_dupes,
        "composite_sentence_overlap_violations": sentence_dupes,
        "repeatable_live_counts": {k: live_counts.get(k, 0) for k in REPEATABLE_TYPES},
        "repeatable_virtual_counts": {k: virtual_counts.get(k, 0) for k in REPEATABLE_TYPES},
        "repeatable_count_mismatches": count_mismatches,
        "additive_required": additive_required,
        "exercise_count": exercise_count,
        "exercise_contract_max": effective_max,
        "chapter_packet_guard": list(
            (enriched.enrichment_audit or {}).get("chapter_packet_guard") or []
        ),
    }


def write_reports(rows: list[dict[str, Any]], json_out: Path, md_out: Path) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    lines = [
        "# Spine Packet Integrity",
        "",
        "Planner-owned guard: duplicate packet resolution must happen upstream of compose/render.",
        "",
        "| case | status | failures |",
        "|---|---|---|",
    ]
    for row in rows:
        fail = "; ".join(row["failures"]) if row["failures"] else ""
        lines.append(f"| {row['case_id']} | {row['status']} | {fail} |")
        if row["duplicate_source_violations"]:
            lines.append("")
            lines.append(f"- `{row['case_id']}` duplicate sources: `{json.dumps(row['duplicate_source_violations'])}`")
        if row["composite_sentence_overlap_violations"]:
            lines.append(f"- `{row['case_id']}` sentence overlap: `{json.dumps(row['composite_sentence_overlap_violations'])}`")
    md_out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Planner-owned spine packet integrity gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--report-out-json", type=Path, default=DEFAULT_JSON)
    ap.add_argument("--report-out-md", type=Path, default=DEFAULT_MD)
    args = ap.parse_args(argv)

    rows = [audit_case(case, repo_root=args.repo_root) for case in CANONICAL_CASES]
    write_reports(rows, args.report_out_json, args.report_out_md)

    failures = [row for row in rows if row["status"] == "FAIL"]
    if not failures:
        print(
            f"SPINE-PACKET-INTEGRITY: PASS ({len(rows)} case(s)) → {args.report_out_json}",
            file=sys.stderr,
        )
        return 0

    print(
        f"SPINE-PACKET-INTEGRITY BLOCKED: {len(failures)} failing case(s) → {args.report_out_json}",
        file=sys.stderr,
    )
    for row in failures:
        print(f"  FAIL {row['case_id']}: {', '.join(row['failures'])}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

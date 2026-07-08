#!/usr/bin/env python3
"""Planner-owned EXERCISE slot contract gate.

Blocks when enrichment emits more EXERCISE slots than the chapter purpose
contract allows. Exercise multiplicity is resolved upstream in beatmap compile;
the renderer must not silently drop authored packets.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from phoenix_v4.planning.beatmap_compile import (  # noqa: E402
    compile_beatmap,
    load_format_spec,
    load_topic_engines,
)
from phoenix_v4.planning.chapter_planner import (  # noqa: E402
    assign_chapter_purpose_contracts,
    resolve_effective_max_exercises,
)
from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment  # noqa: E402
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = REPO_ROOT / "artifacts" / "qa" / "exercise_slot_contract" / "EXERCISE_SLOT_CONTRACT.json"


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
    failures: list[str] = []
    if exercise_count > effective_max:
        failures.append(
            f"chapter has {exercise_count} EXERCISE slots but planner contract allows {effective_max}"
        )
    return {
        **asdict(case),
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "exercise_count": exercise_count,
        "exercise_contract_max": effective_max,
        "contract_emotional_job": contract.emotional_job,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Planner-owned EXERCISE slot contract gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--report-out-json", type=Path, default=DEFAULT_REPORT)
    args = ap.parse_args(argv)

    rows = [audit_case(case, repo_root=args.repo_root) for case in CANONICAL_CASES]
    args.report_out_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_out_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    failures = [row for row in rows if row["status"] == "FAIL"]
    if not failures:
        print(
            f"EXERCISE-SLOT-CONTRACT: PASS ({len(rows)} case(s)) → {args.report_out_json}",
            file=sys.stderr,
        )
        return 0

    print(
        f"EXERCISE-SLOT-CONTRACT BLOCKED: {len(failures)} failing case(s) → {args.report_out_json}",
        file=sys.stderr,
    )
    for row in failures:
        print(f"  FAIL {row['case_id']}: {', '.join(row['failures'])}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

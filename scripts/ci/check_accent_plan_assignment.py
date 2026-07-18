#!/usr/bin/env python3
"""Accent plan assignment gate — rendered accents must match planner accent_beats."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from phoenix_v4.planning.accent_planner import attach_accent_plan, validate_accent_plan
from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = REPO_ROOT / "artifacts" / "qa" / "accent_plan_assignment" / "ACCENT_PLAN_ASSIGNMENT.json"


@dataclass(frozen=True)
class CanonicalCase:
    case_id: str
    topic: str
    persona: str
    brand_id: str
    runtime_format: str
    seed: str


CANONICAL_CASES: tuple[CanonicalCase, ...] = (
    CanonicalCase(
        case_id="burnout_corporate_managers_accent_v1",
        topic="burnout",
        persona="corporate_managers",
        brand_id="stillness_press",
        runtime_format="standard_book",
        seed="4242",
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
    enriched = select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
            persona_id=case.persona,
            topic_id=case.topic,
            seed=case.seed,
        ),
        repo_root=repo_root,
    )
    return attach_accent_plan(
        enriched,
        brand_id=case.brand_id,
        seed=case.seed,
        repo_root=repo_root,
    )


def _body_in_prose(body: str, prose: str) -> bool:
    text = body.strip()
    if not text:
        return False
    if text in prose:
        return True
    for line in text.splitlines():
        line = line.strip()
        if len(line) >= 20 and line in prose:
            return True
    return False


def audit_case(case: CanonicalCase, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    enriched = _build_enriched(case, repo_root)
    errors.extend(validate_accent_plan(enriched))

    ctx = enriched.spine_context or {}
    signature = str(ctx.get("accent_signature") or "")
    if not signature and sum((ctx.get("accent_budget") or {}).values()):
        errors.append("accent_signature missing despite non-zero accent_budget")

    assignments = list(ctx.get("accent_assignments") or [])
    planned_ids = {str(r.get("accent_id") or "") for r in assignments if r.get("accent_id")}
    classes = {str(r.get("class") or "") for r in assignments}

    if "EXTERNAL_STORY" not in classes:
        errors.append("missing EXTERNAL_STORY accent")
    if "CITED_EVIDENCE" not in classes:
        errors.append("missing CITED_EVIDENCE accent")
    if "ENCOURAGEMENT" not in classes:
        errors.append("missing ENCOURAGEMENT accent")

    prose = compose_from_enriched_book(enriched, quality_profile="draft")
    rendered_hits: list[str] = []
    for ch in enriched.chapters:
        for aid, body in (ch.accent_bodies or {}).items():
            text = body.strip()
            if not text:
                continue
            if not _body_in_prose(text, prose):
                errors.append(f"planned accent not found in render: {aid}")
            else:
                rendered_hits.append(aid)

    for ch in enriched.chapters:
        for beat in ch.accent_beats or []:
            aid = str(beat.get("accent_id") or "")
            if aid and aid not in planned_ids:
                errors.append(f"chapter accent_beats lists unplanned accent_id: {aid}")

    for tok in ("ahjan", "master wu", "junko", "sai ma", "master sha"):
        if tok in prose.lower():
            errors.append(f"composite secular-safe violation: teacher token {tok!r} in render")

    return {
        "case_id": case.case_id,
        "pass": not errors,
        "errors": errors,
        "accent_signature": signature,
        "accent_assignment_count": len(assignments),
        "accent_classes": sorted(classes),
        "rendered_accent_ids": sorted(rendered_hits),
        "prose_words": len(prose.split()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    results = [audit_case(c) for c in CANONICAL_CASES]
    payload = {"cases": results, "pass": all(r["pass"] for r in results)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    for row in results:
        status = "PASS" if row["pass"] else "FAIL"
        print(
            f"{status} {row['case_id']} signature={row.get('accent_signature')} "
            f"assignments={row.get('accent_assignment_count')}"
        )
        for err in row.get("errors") or []:
            print(f"  - {err}")

    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

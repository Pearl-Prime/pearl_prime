"""Plan-time chapter contracts derived from the current BookStructurePlan."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from phoenix_v4.planning.book_structure_plan import BookStructurePlan


def _slot_types(chapter: Any) -> list[str]:
    slots = []
    for slot in getattr(chapter, "slot_plans", []) or []:
        raw = slot.get("type") or slot.get("slot_type") if isinstance(slot, dict) else ""
        if raw:
            slots.append(str(raw).upper())
    return slots


def _reader_promise(chapter: Any) -> str:
    thesis = str(getattr(chapter, "chapter_thesis", "") or "").strip()
    if thesis:
        return thesis
    return f"Reader can name the {getattr(chapter, 'emotional_role', 'chapter')} pattern."


def _acceptance_profile(profile: str) -> dict[str, Any]:
    return {
        "current": profile,
        "structural_spec_pass_possible": True,
        "operator_read_required_for_public_release": True,
        "production_public_release_authorized": False,
    }


def build_chapter_contracts(
    plan: BookStructurePlan,
    *,
    acceptance_profile: str = "structural",
) -> dict[str, Any]:
    """Return plan-time contracts without modifying the planner or render output."""
    contracts: list[dict[str, Any]] = []
    for chapter in plan.chapters:
        slot_types = _slot_types(chapter)
        exercise_slots = [s for s in slot_types if s == "EXERCISE"]
        story_required = "STORY" in slot_types
        contracts.append(
            {
                "chapter_identity": {
                    "plan_id": plan.plan_id,
                    "topic_id": plan.topic_id,
                    "persona_id": plan.persona_id,
                    "teacher_id": plan.teacher_id,
                    "engine_type": plan.engine_type,
                    "runtime_format_id": plan.runtime_format_id,
                    "chapter_number": chapter.chapter_number,
                    "chapter_index": chapter.chapter_index,
                    "title": chapter.title,
                },
                "thesis": chapter.chapter_thesis,
                "reader_promise": _reader_promise(chapter),
                "reader_state_entry": f"{plan.topic_id}:{chapter.emotional_role}:entry",
                "reader_state_exit": f"{plan.topic_id}:{chapter.emotional_role}:exit",
                "same_person_story_requirement": {
                    "required": story_required,
                    "non_story_reason": "" if story_required else "chapter slot plan has no STORY slot",
                    "continuity_scope": "same_person_or_explicit_composite",
                },
                "exercise_tool_policy": {
                    "exercise_slots": len(exercise_slots),
                    "policy": "canonical_exercise" if exercise_slots else "tool_or_reflection_only",
                    "expected_aha": "reader can name a concrete shift, not just complete a step",
                    "expected_integration": "chapter lands the practice into the next ordinary moment",
                },
                "atom_surface_depth_expectations": {
                    "slot_types": slot_types,
                    "requires_depth_contract": True,
                    "source": "config/atoms/surface_taxonomy.yaml",
                },
                "source_evidence_constraints": {
                    "quotes_require_source": True,
                    "external_story_requires_bridge": True,
                    "composite_story_requires_label": True,
                },
                "close_handoff_requirement": {
                    "required": True,
                    "final_chapter": bool(getattr(chapter, "ending_contract", None)),
                    "expected_close": "ending_contract" if getattr(chapter, "ending_contract", None) else "next-chapter handoff",
                },
                "acceptance_profile": _acceptance_profile(acceptance_profile),
                "planning_trace": {
                    "bestseller_structure": chapter.bestseller_structure,
                    "band": chapter.band,
                    "intensity": chapter.intensity,
                    "regulation_support": chapter.regulation_support,
                    "emotional_role": chapter.emotional_role,
                },
            }
        )
    return {
        "schema_version": "1.0.0",
        "artifact_type": "plantime_chapter_contract",
        "plan_id": plan.plan_id,
        "topic_id": plan.topic_id,
        "persona_id": plan.persona_id,
        "teacher_id": plan.teacher_id,
        "engine_type": plan.engine_type,
        "runtime_format_id": plan.runtime_format_id,
        "chapter_count": plan.chapter_count,
        "contracts": contracts,
    }


def validate_chapter_contract_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contracts = packet.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        return ["contracts must be a non-empty list"]
    theses = []
    bands = []
    for idx, contract in enumerate(contracts):
        prefix = f"contracts[{idx}]"
        for field in (
            "chapter_identity",
            "thesis",
            "reader_promise",
            "reader_state_entry",
            "reader_state_exit",
            "same_person_story_requirement",
            "exercise_tool_policy",
            "atom_surface_depth_expectations",
            "source_evidence_constraints",
            "close_handoff_requirement",
            "acceptance_profile",
        ):
            if not contract.get(field):
                errors.append(f"{prefix} missing {field}")
        thesis = str(contract.get("thesis") or "")
        if thesis:
            theses.append(thesis)
        trace = contract.get("planning_trace") or {}
        bands.append(int(trace.get("band") or 0))
        profile = contract.get("acceptance_profile") or {}
        if profile.get("production_public_release_authorized") is not False:
            errors.append(f"{prefix} must not authorize production public release")
    if len(set(theses)) < max(1, len(theses) // 2):
        errors.append("chapter theses are not sufficiently distinct")
    if bands and max(bands) <= min(bands):
        errors.append("band line must rise somewhere across the plan")
    return errors

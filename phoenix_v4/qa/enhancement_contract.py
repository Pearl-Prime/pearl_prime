"""Authoritative enhancement-contract proof against the delivered manuscript."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from phoenix_v4.planning.accent_planner import (
    accent_class_bucket,
    build_enhancement_contract_v21_summary,
    count_unit_for_surface,
    disallowed_positions_for_surface,
    preferred_positions_for_surface,
)
from phoenix_v4.planning.enhancement_contract_v21_runtime import validate_v21_integrity
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter
from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams

FLAGSHIP_TOPIC_ID = "anxiety"
FLAGSHIP_PERSONA_ID = "gen_z_professionals"
FLAGSHIP_RUNTIME_FORMAT = "extended_book_2h"
DEFAULT_CONTRACT_ID = "enhancement_contract_v1"

SUPPORTED_ACCENT_POSITIONS = frozenset(
    {
        "before_HOOK",
        "after_HOOK",
        "before_STORY",
        "after_EXERCISE",
        "after_REFLECTION",
        "before_THREAD",
        "after_PIVOT",
        "after_INTEGRATION",
        "after_turning_point",
    }
)

PROOF_SLOT_TYPES = frozenset({"STORY", "EXERCISE", "ANGLE_DEFINITION", "ANGLE_CALLBACK"})

_CHAPTER_RE = re.compile(r"(?m)^Chapter\s+(\d+)\s*$")
_PARAGRAPH_RE = re.compile(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", re.S)
_UNRESOLVED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("curly_placeholder", re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")),
    ("persona_stub", re.compile(r"\[Persona-specific hook for [^\]]+\]", re.I)),
    ("todo_marker", re.compile(r"\b(?:TODO|TKTK|TBD|FIXME)\b")),
    ("inject_marker", re.compile(r":inject:\d+:\d+")),
)


def enhancement_contract_v1_flagship(
    *,
    topic_id: str,
    persona_id: str,
    runtime_format: str,
) -> bool:
    return (
        str(topic_id or "").strip() == FLAGSHIP_TOPIC_ID
        and str(persona_id or "").strip() == FLAGSHIP_PERSONA_ID
        and str(runtime_format or "").strip() == FLAGSHIP_RUNTIME_FORMAT
    )


def _as_mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _excerpt(text: str, *, words: int = 18) -> str:
    pieces = str(text or "").split()
    if not pieces:
        return ""
    return " ".join(pieces[:words]).strip()


def _chapter_sections(manuscript_text: str) -> Dict[int, Dict[str, Any]]:
    matches = list(_CHAPTER_RE.finditer(manuscript_text or ""))
    sections: Dict[int, Dict[str, Any]] = {}
    for idx, match in enumerate(matches):
        try:
            number = int(match.group(1))
        except (TypeError, ValueError):
            continue
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(manuscript_text)
        sections[number] = {
            "start": start,
            "end": end,
            "text": manuscript_text[start:end],
        }
    return sections


def _paragraph_spans(text: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx, match in enumerate(_PARAGRAPH_RE.finditer(text or "")):
        para = match.group(0).strip()
        if not para:
            continue
        out.append(
            {
                "index": idx,
                "start": match.start(),
                "end": match.end(),
                "text": para,
            }
        )
    return out


def _find_body_in_text(
    text: str,
    body: str,
    *,
    search_start: int = 0,
    chapter_offset: int = 0,
    paragraphs: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    raw = str(body or "").strip()
    base = {
        "present": False,
        "match_mode": "missing",
        "char_start": None,
        "char_end": None,
        "absolute_char_start": None,
        "absolute_char_end": None,
        "paragraph_index": None,
        "excerpt": _excerpt(raw),
    }
    if not raw or not text:
        return base
    idx = text.find(raw, max(0, search_start))
    match_len = len(raw)
    mode = "exact"
    if idx < 0:
        fragments: List[str] = []
        paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
        if paras:
            fragments.extend(paras)
        head = _excerpt(raw, words=14)
        if head:
            fragments.append(head)
        for fragment in fragments:
            if len(fragment) < 24:
                continue
            idx = text.find(fragment, max(0, search_start))
            if idx >= 0:
                match_len = len(fragment)
                mode = "fragment"
                break
    if idx < 0:
        return base
    para_index = None
    for row in list(paragraphs or []):
        start = int(row.get("start") or 0)
        end = int(row.get("end") or 0)
        if start <= idx < end:
            para_index = int(row.get("index") or 0)
            break
    return {
        "present": True,
        "match_mode": mode,
        "char_start": idx,
        "char_end": idx + match_len,
        "absolute_char_start": chapter_offset + idx,
        "absolute_char_end": chapter_offset + idx + match_len,
        "paragraph_index": para_index,
        "excerpt": text[idx : idx + min(match_len, 220)].replace("\n", " ").strip(),
    }


def _unresolved_markers(text: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for code, pattern in _UNRESOLVED_PATTERNS:
        for match in pattern.finditer(text or ""):
            rows.append(
                {
                    "kind": code,
                    "match": match.group(0),
                    "char_start": match.start(),
                    "char_end": match.end(),
                }
            )
    return rows


def _source_tail(source_id: str) -> str:
    raw = str(source_id or "").strip()
    if ":" in raw:
        return raw.split(":", 1)[1].strip()
    return raw


def _callback_metadata(slot_type: str, source_id: str) -> Dict[str, Any]:
    plant_id = _source_tail(source_id)
    slot = str(slot_type or "").strip().upper()
    if slot == "ANGLE_DEFINITION":
        return {
            "callback_role": "plant",
            "plant_id": plant_id,
            "return_function": "",
            "semantic_development": "initial_angle_plant",
        }
    if slot == "ANGLE_CALLBACK":
        return {
            "callback_role": "return",
            "plant_id": plant_id,
            "return_function": "angle_callback",
            "semantic_development": "later_chapter_reactivation",
        }
    return {
        "callback_role": "",
        "plant_id": plant_id,
        "return_function": "",
        "semantic_development": "",
    }


def _chapter_v21_groups(
    chapter: EnrichedChapter,
    accent_rows: Sequence[Mapping[str, Any]],
) -> Dict[str, List[str]]:
    slot_types = {str(slot.slot_type or "").strip().upper() for slot in (chapter.slots or []) if slot.slot_type}
    hooks = {
        str(hook).strip().lower()
        for slot in (chapter.slots or [])
        for hook in (slot.enrichment_applied or [])
        if str(hook).strip()
    }
    accent_classes = {str(row.get("class") or "").strip().upper() for row in accent_rows if row.get("class")}
    chapter_engine: List[str] = []
    if "EXERCISE" in slot_types:
        chapter_engine.append("PRACTICE_APPLICATION")
    if "TAKEAWAY" in slot_types:
        chapter_engine.append("CLOSING_TAKEAWAY")
    if "THREAD" in slot_types:
        chapter_engine.append("PROPULSION")
    if "TROUBLESHOOTING" in accent_classes:
        chapter_engine.append("TROUBLESHOOTING")

    proof_and_embodiment: List[str] = []
    if "STORY" in slot_types:
        proof_and_embodiment.append("HOOK_STORY")
    for surface in ("EXTERNAL_STORY", "CITED_EVIDENCE", "AUTHOR_DISCLOSURE"):
        if surface in accent_classes:
            proof_and_embodiment.append(surface)

    optional_accents = sorted(
        surface
        for surface in accent_classes
        if accent_class_bucket(surface) == "optional_accents"
    )

    cohesion_and_craft: List[str] = []
    if "ANGLE_DEFINITION" in slot_types:
        cohesion_and_craft.append("CALLBACK_PLANT")
    if "ANGLE_CALLBACK" in slot_types:
        cohesion_and_craft.append("CALLBACK_RETURN")
    if any("analogy" in hook for hook in hooks) or "ANGLE_DEFINITION" in slot_types:
        cohesion_and_craft.append("ANALOGY")
    if any("metaphor" in hook for hook in hooks) or "ANGLE_DEFINITION" in slot_types:
        cohesion_and_craft.append("METAPHOR")

    return {
        "chapter_engine": sorted(set(chapter_engine)),
        "proof_and_embodiment": sorted(set(proof_and_embodiment)),
        "optional_accents": optional_accents,
        "cohesion_and_craft": sorted(set(cohesion_and_craft)),
    }


def _stream_rows_for_chapter(
    chapter: EnrichedChapter,
) -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    slot_rows: List[Dict[str, Any]] = []
    for idx, slot in enumerate(chapter.slots or []):
        body = str(slot.content or "").strip()
        slot_rows.append(
            {
                "kind": "slot",
                "chapter": int(chapter.number),
                "slot_index": idx,
                "slot_type": str(slot.slot_type or "").strip().upper(),
                "source": str(slot.source or "").strip(),
                "source_id": str(slot.source_id or "").strip(),
                "variant_id": str(slot.variant_id or "").strip(),
                "atom_id": str(slot.atom_id or "").strip(),
                "enrichment_applied": list(slot.enrichment_applied or []),
                "body": body,
                "body_hash": _content_hash(body) if body else "",
            }
        )

    rendered_rows: List[Dict[str, Any]] = []
    if chapter.accent_beats and chapter.accent_bodies:
        slot_types = [row["slot_type"] for row in slot_rows]
        slot_proses = [row["body"] for row in slot_rows]
        _, _, rendered_rows = insert_accent_beats_into_streams(
            slot_types,
            slot_proses,
            chapter.accent_beats,
            chapter.accent_bodies,
        )

    stream_rows = list(slot_rows)
    accent_stream_by_id: Dict[str, Dict[str, Any]] = {}
    for rendered in sorted(rendered_rows, key=lambda row: int(row.get("chapter_insert_index") or 0)):
        keys = _as_mapping(rendered.get("keys"))
        accent_row = {
            "kind": "accent",
            "chapter": int(chapter.number),
            "accent_id": str(rendered.get("accent_id") or ""),
            "class": str(rendered.get("class") or ""),
            "position": str(rendered.get("position") or ""),
            "keys": keys,
            "surface_bucket": str(rendered.get("surface_bucket") or keys.get("surface_bucket") or ""),
            "count_unit": str(rendered.get("count_unit") or keys.get("count_unit") or ""),
            "provenance": str(rendered.get("provenance") or ""),
            "body": str(rendered.get("body") or "").strip(),
            "body_hash": str(rendered.get("body_hash") or ""),
            "chapter_insert_index": int(rendered.get("chapter_insert_index") or 0),
            "rendered_excerpt": str(rendered.get("rendered_excerpt") or "").strip(),
        }
        insert_at = max(0, min(accent_row["chapter_insert_index"], len(stream_rows)))
        stream_rows.insert(insert_at, accent_row)
        if accent_row["accent_id"]:
            accent_stream_by_id[accent_row["accent_id"]] = accent_row

    for idx, row in enumerate(stream_rows):
        row["renderer_stream_index"] = idx
    return stream_rows, accent_stream_by_id


def build_enhancement_contract_payload(
    *,
    enriched: EnrichedBook,
    manuscript_text: str,
    contract_id: str = DEFAULT_CONTRACT_ID,
    topic_id: str = "",
    persona_id: str = "",
    runtime_format: str = "",
    accent_render_audit: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    audit = _as_mapping(enriched.enrichment_audit)
    strategy = _as_mapping(audit.get("enrichment_strategy_report"))
    alignment = _as_mapping(audit.get("bestseller_alignment_report"))
    spine = _as_mapping(enriched.spine_context)
    topic = topic_id or str(enriched.topic or "")
    persona = persona_id or str(enriched.persona_id or "")
    runtime = runtime_format or str(enriched.runtime_format or "")
    assignments = _as_list(spine.get("accent_assignments")) or _as_list(strategy.get("assignments"))
    render_rows = list(accent_render_audit or _as_list(audit.get("accent_render_audit")))
    render_by_id = {
        str(row.get("accent_id") or ""): dict(row)
        for row in render_rows
        if isinstance(row, Mapping) and row.get("accent_id")
    }
    v21_summary = _as_mapping(strategy.get("enhancement_contract_v21")) or _as_mapping(
        spine.get("enhancement_contract_v21")
    )
    if not v21_summary:
        v21_summary = build_enhancement_contract_v21_summary(
            accent_budget=_as_mapping(spine.get("accent_budget") or strategy.get("accent_budget")),
            flat_rows=assignments,
            chapter_count=len(enriched.chapters or []),
            story_mix_profile=str(
                strategy.get("enrichment_strategy_profile")
                or spine.get("story_mix_profile")
                or ""
            ).strip(),
            max_accents_per_chapter=int(
                _as_mapping(_as_mapping(strategy.get("enhancement_contract_v21")).get("optional_accent_budget")).get(
                    "max_accents_per_chapter"
                )
                or 2
            ),
            persona_id=persona,
            topic_id=topic,
        )
    chapter_sections = _chapter_sections(manuscript_text)

    surface_notes: List[Dict[str, str]] = [
        {
            "surface": "accent_selected_body",
            "status": "partial",
            "detail": (
                "No dedicated selected-accent artifact exists; selected bodies are proven from "
                "EnrichedChapter.accent_bodies."
            ),
        }
    ]
    if not render_rows:
        surface_notes.append(
            {
                "surface": "accent_render_audit",
                "status": "partial",
                "detail": "Composer render audit was absent; renderer stream indices were reconstructed from planner beats.",
            }
        )

    validation: Dict[str, List[Dict[str, Any]]] = {
        "missing_planned": [],
        "missing_selected_body": [],
        "orphan_selected": [],
        "orphan_rendered": [],
        "unsupported_positions": [],
        "malformed_bodies": [],
        "missing_story_function": [],
        "missing_truth_metadata": [],
        "unresolved_markers": _unresolved_markers(manuscript_text),
        "core_surface_failures": [],
    }
    accent_rows: List[Dict[str, Any]] = []
    core_surface_rows: List[Dict[str, Any]] = []
    chapters_payload: List[Dict[str, Any]] = []

    for chapter in enriched.chapters or []:
        chapter_num = int(chapter.number)
        chapter_section = chapter_sections.get(chapter_num) or {"start": 0, "text": ""}
        chapter_text = str(chapter_section.get("text") or "")
        chapter_start = int(chapter_section.get("start") or 0)
        paragraphs = _paragraph_spans(chapter_text)
        stream_rows, accent_stream_by_id = _stream_rows_for_chapter(chapter)
        cursor = 0
        located_rows: List[Dict[str, Any]] = []
        for row in stream_rows:
            loc = _find_body_in_text(
                chapter_text,
                str(row.get("body") or ""),
                search_start=cursor,
                chapter_offset=chapter_start,
                paragraphs=paragraphs,
            )
            row["final_location"] = loc
            if loc.get("present"):
                cursor = max(cursor, int(loc.get("char_end") or 0))
                located_rows.append(row)
        located_order = {
            id(row): idx
            for idx, row in enumerate(sorted(located_rows, key=lambda item: int(item["final_location"]["char_start"])))
        }

        chapter_assignments = [
            dict(row)
            for row in assignments
            if isinstance(row, Mapping) and int(row.get("chapter") or 0) == chapter_num
        ]
        chapter_accent_rows: List[Dict[str, Any]] = []
        planned_ids = {str(row.get("accent_id") or "") for row in chapter_assignments if row.get("accent_id")}
        for accent_id, body in dict(chapter.accent_bodies or {}).items():
            if accent_id not in planned_ids:
                validation["orphan_selected"].append(
                    {
                        "chapter": chapter_num,
                        "accent_id": str(accent_id),
                        "body_hash": _content_hash(str(body or "")),
                    }
                )
        for accent_id, render_row in render_by_id.items():
            if int(render_row.get("chapter") or 0) != chapter_num:
                continue
            if accent_id not in planned_ids:
                validation["orphan_rendered"].append(
                    {
                        "chapter": chapter_num,
                        "accent_id": accent_id,
                        "class": str(render_row.get("class") or ""),
                    }
                )

        for assignment in chapter_assignments:
            accent_id = str(assignment.get("accent_id") or "")
            body = str((chapter.accent_bodies or {}).get(accent_id) or "").strip()
            position = str(assignment.get("position") or "").strip()
            if position and position not in SUPPORTED_ACCENT_POSITIONS:
                validation["unsupported_positions"].append(
                    {"chapter": chapter_num, "accent_id": accent_id, "position": position}
                )
            if not body:
                validation["missing_selected_body"].append(
                    {"chapter": chapter_num, "accent_id": accent_id, "class": assignment.get("class")}
                )
            for marker in _unresolved_markers(body):
                validation["malformed_bodies"].append(
                    {
                        "chapter": chapter_num,
                        "accent_id": accent_id,
                        "kind": marker["kind"],
                        "match": marker["match"],
                    }
                )
            stream_row = accent_stream_by_id.get(accent_id) or {}
            loc = _as_mapping(stream_row.get("final_location"))
            if body and not loc.get("present"):
                validation["missing_planned"].append(
                    {"chapter": chapter_num, "accent_id": accent_id, "class": assignment.get("class")}
                )
            render_row = _as_mapping(render_by_id.get(accent_id))
            keys = _as_mapping(assignment.get("keys"))
            truth_metadata = _as_mapping(keys.get("truth_metadata"))
            accent_class = str(assignment.get("class") or "").strip()
            if accent_class == "EXTERNAL_STORY":
                if not str(keys.get("story_function") or "").strip():
                    validation["missing_story_function"].append(
                        {"chapter": chapter_num, "accent_id": accent_id, "class": accent_class}
                    )
                if not truth_metadata.get("citation") or not truth_metadata.get("source"):
                    validation["missing_truth_metadata"].append(
                        {"chapter": chapter_num, "accent_id": accent_id, "class": accent_class}
                    )
            accent_payload = {
                "chapter": chapter_num,
                "class": accent_class,
                "accent_id": accent_id,
                "position": position,
                "surface_bucket": str(
                    keys.get("surface_bucket") or accent_class_bucket(accent_class)
                ),
                "count_unit": str(
                    keys.get("count_unit") or count_unit_for_surface(accent_class)
                ),
                "preferred_positions": list(
                    keys.get("preferred_positions") or preferred_positions_for_surface(accent_class)
                ),
                "disallowed_positions": list(
                    keys.get("disallowed_positions") or disallowed_positions_for_surface(accent_class)
                ),
                "story_function": str(keys.get("story_function") or "").strip(),
                "story_function_source": str(keys.get("story_function_source") or "").strip(),
                "truth_metadata": truth_metadata,
                "renderer_stream_index": stream_row.get("renderer_stream_index"),
                "chapter_insert_index": stream_row.get("chapter_insert_index"),
                "final_char_start": loc.get("absolute_char_start"),
                "final_char_end": loc.get("absolute_char_end"),
                "final_paragraph_index": loc.get("paragraph_index"),
                "final_order_index": located_order.get(id(stream_row)),
                "final_order_matches_renderer": (
                    located_order.get(id(stream_row)) == stream_row.get("renderer_stream_index")
                    if loc.get("present") and stream_row
                    else False
                ),
                "present_in_manuscript": bool(loc.get("present")),
                "match_mode": loc.get("match_mode"),
                "body_hash": _content_hash(body) if body else "",
                "selected_body_excerpt": _excerpt(body),
                "rendered_excerpt": str(
                    render_row.get("rendered_excerpt")
                    or stream_row.get("rendered_excerpt")
                    or _excerpt(body)
                ).strip(),
                "final_excerpt": str(loc.get("excerpt") or "").strip(),
                "provenance": str(
                    assignment.get("supply_source")
                    or keys.get("supply_provenance")
                    or render_row.get("provenance")
                    or stream_row.get("provenance")
                    or ""
                ).strip(),
                "supply_source": str(assignment.get("supply_source") or "").strip(),
                "keys": keys,
                "selected_surface_status": "partial",
                "render_surface_status": "real" if render_row else "reconstructed",
            }
            accent_rows.append(accent_payload)
            chapter_accent_rows.append(accent_payload)

        slot_flow: List[str] = []
        source_ids: List[str] = []
        enhancement_hooks: List[str] = []
        for row in stream_rows:
            if row.get("kind") == "slot":
                slot_type = str(row.get("slot_type") or "")
                if slot_type:
                    slot_flow.append(slot_type)
                source_id = str(row.get("source_id") or "")
                if source_id:
                    source_ids.append(source_id)
                for hook in list(row.get("enrichment_applied") or []):
                    name = str(hook or "").strip()
                    if name and name not in enhancement_hooks:
                        enhancement_hooks.append(name)
                if slot_type in PROOF_SLOT_TYPES:
                    loc = _as_mapping(row.get("final_location"))
                    callback_meta = _callback_metadata(slot_type, source_id)
                    slot_row = {
                        "chapter": chapter_num,
                        "slot_type": slot_type,
                        "source": str(row.get("source") or "").strip(),
                        "source_id": source_id,
                        "variant_id": str(row.get("variant_id") or "").strip(),
                        "atom_id": str(row.get("atom_id") or "").strip(),
                        "renderer_stream_index": row.get("renderer_stream_index"),
                        "final_char_start": loc.get("absolute_char_start"),
                        "final_char_end": loc.get("absolute_char_end"),
                        "final_paragraph_index": loc.get("paragraph_index"),
                        "final_order_index": located_order.get(id(row)),
                        "present_in_manuscript": bool(loc.get("present")),
                        "match_mode": loc.get("match_mode"),
                        "body_hash": str(row.get("body_hash") or ""),
                        "selected_body_excerpt": _excerpt(str(row.get("body") or "")),
                        "final_excerpt": str(loc.get("excerpt") or "").strip(),
                        **callback_meta,
                    }
                    core_surface_rows.append(slot_row)
                    if not slot_row["present_in_manuscript"]:
                        validation["core_surface_failures"].append(
                            {
                                "chapter": chapter_num,
                                "slot_type": slot_type,
                                "source_id": source_id,
                            }
                        )

        chapters_payload.append(
            {
                "chapter": chapter_num,
                "working_title": str(chapter.working_title or "").strip(),
                "slot_flow": slot_flow,
                "source_ids": source_ids,
                "enhancement_hooks": enhancement_hooks,
                "accent_ids": sorted(planned_ids),
                "v21_surface_groups": _chapter_v21_groups(chapter, chapter_accent_rows),
                "callback_semantics": [
                    {
                        "slot_type": row["slot_type"],
                        "plant_id": row.get("plant_id") or "",
                        "return_function": row.get("return_function") or "",
                        "semantic_development": row.get("semantic_development") or "",
                    }
                    for row in core_surface_rows
                    if row["chapter"] == chapter_num and row.get("callback_role")
                ],
                "confirmed_required_slots": [
                    row["slot_type"]
                    for row in core_surface_rows
                    if row["chapter"] == chapter_num and row.get("present_in_manuscript")
                ],
            }
        )

    v21_integrity = validate_v21_integrity(
        optional_budget=_as_mapping(v21_summary.get("optional_accent_budget")),
        accent_rows=accent_rows,
        core_surface_rows=core_surface_rows,
        chapter_count=len(enriched.chapters or []),
    )
    validation["v21_integrity"] = v21_integrity  # type: ignore[assignment]

    errors: List[str] = []
    for key, rows in validation.items():
        if key == "v21_integrity":
            continue
        if key == "unresolved_markers":
            for row in rows:
                errors.append(f"{key}:{row.get('kind')}:{row.get('match')}")
            continue
        for row in rows:
            ident = row.get("accent_id") or row.get("slot_type") or row.get("kind") or "row"
            errors.append(f"{key}:{row.get('chapter')}:{ident}")
    for row in _as_list(v21_integrity.get("hard_failures")):
        if not isinstance(row, Mapping):
            continue
        errors.append(f"v21_integrity:{row.get('code')}:{row.get('chapter', '')}:{row.get('accent_id') or row.get('plant_id') or ''}")

    payload = {
        "schema_version": 1,
        "stage": "enhancement_contract",
        "contract_id": contract_id,
        "status": "PASS" if not errors else "FAIL",
        "topic_id": topic,
        "persona_id": persona,
        "runtime_format": runtime,
        "book_idea": str(strategy.get("book_idea") or spine.get("book_idea") or "").strip(),
        "book_motif": str(strategy.get("book_motif") or spine.get("book_motif") or "").strip(),
        "accent_budget": dict(spine.get("accent_budget") or strategy.get("accent_budget") or {}),
        "accent_signature": str(spine.get("accent_signature") or strategy.get("accent_signature") or ""),
        "story_mix_profile": str(
            strategy.get("enrichment_strategy_profile")
            or spine.get("story_mix_profile")
            or ""
        ).strip(),
        "supported_underfilled_budget_by_class": dict(
            alignment.get("supported_underfilled_budget_by_class") or {}
        ),
        "enhancement_contract_v21": v21_summary,
        "surface_notes": surface_notes,
        "manuscript": {
            "sha256": _content_hash(manuscript_text),
            "word_count": len((manuscript_text or "").split()),
            "char_count": len(manuscript_text or ""),
        },
        "validation": {
            **validation,
            "errors": errors,
        },
        "accent_rows": accent_rows,
        "core_surface_rows": core_surface_rows,
        "chapters": chapters_payload,
    }
    return payload


def render_enhancement_contract_markdown(payload: Mapping[str, Any]) -> str:
    lines: List[str] = [
        "# Enhancement Contract",
        "",
        f"**Status:** `{payload.get('status') or 'UNKNOWN'}`",
        f"**Contract:** `{payload.get('contract_id') or ''}`",
        f"**Topic / persona:** `{payload.get('topic_id') or ''}` × `{payload.get('persona_id') or ''}`",
        f"**Runtime format:** `{payload.get('runtime_format') or ''}`",
        f"**Book idea:** {payload.get('book_idea') or '_none recorded_'}",
        f"**Book motif:** {payload.get('book_motif') or '_none recorded_'}",
        f"**Accent signature:** `{payload.get('accent_signature') or ''}`",
        "",
        "## Surface Notes",
        "",
    ]
    notes = _as_list(payload.get("surface_notes"))
    if not notes:
        lines.append("_None._")
    else:
        for note in notes:
            if not isinstance(note, Mapping):
                continue
            lines.append(
                f"- `{note.get('surface')}` [{note.get('status')}] {note.get('detail')}"
            )

    v21 = _as_mapping(payload.get("enhancement_contract_v21"))
    if v21:
        opt = _as_mapping(v21.get("optional_accent_budget"))
        actual = _as_mapping(opt.get("actual"))
        lines.extend(
            [
                "",
                "## V2.1 Model",
                "",
                "- Buckets: chapter_engine / proof_and_embodiment / optional_accents / cohesion_and_craft",
                (
                    "- Optional accents: assigned={assigned} hard_max={hard_max} "
                    "chapters_with_optional={chapters} max_per_chapter={per_chapter}"
                ).format(
                    assigned=actual.get("assigned_total_optional_accents") or 0,
                    hard_max=opt.get("hard_max_total_accents") or 0,
                    chapters=len(_as_list(actual.get("chapters_with_optional_accents"))),
                    per_chapter=opt.get("max_accents_per_chapter") or 0,
                ),
                "- Ceiling rule: class maxima are ceilings, not maximize-all directives.",
            ]
        )

    lines.extend(["", "## Validation", ""])
    errors = _as_list(_as_mapping(payload.get("validation")).get("errors"))
    if not errors:
        lines.append("- PASS: no contract failures recorded.")
    else:
        for err in errors:
            lines.append(f"- FAIL: {err}")
    v21_integrity = _as_mapping(_as_mapping(payload.get("validation")).get("v21_integrity"))
    for warning in _as_list(v21_integrity.get("warnings")):
        if not isinstance(warning, Mapping):
            continue
        lines.append(
            "- WARN: V2.1 {code} — {detail}".format(
                code=warning.get("code") or "warning",
                detail=warning.get("detail") or "",
            )
        )

    lines.extend(
        [
            "",
            "## Accent Proof",
            "",
            "| Chapter | Class | Accent ID | Position | Stream | Final Paragraph | Present | Provenance |",
            "|---:|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in _as_list(payload.get("accent_rows")):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| {chapter} | {cls} | `{accent_id}` | {position} | {stream} | {paragraph} | {present} | {prov} |".format(
                chapter=row.get("chapter") or 0,
                cls=row.get("class") or "",
                accent_id=row.get("accent_id") or "",
                position=row.get("position") or "",
                stream=row.get("renderer_stream_index") if row.get("renderer_stream_index") is not None else "—",
                paragraph=row.get("final_paragraph_index") if row.get("final_paragraph_index") is not None else "—",
                present="yes" if row.get("present_in_manuscript") else "no",
                prov=row.get("provenance") or "",
            )
        )

    lines.extend(
        [
            "",
            "## Core Surface Proof",
            "",
            "| Chapter | Slot | Source ID | Stream | Final Paragraph | Present |",
            "|---:|---|---|---:|---:|---|",
        ]
    )
    for row in _as_list(payload.get("core_surface_rows")):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| {chapter} | {slot_type} | `{source_id}` | {stream} | {paragraph} | {present} |".format(
                chapter=row.get("chapter") or 0,
                slot_type=row.get("slot_type") or "",
                source_id=row.get("source_id") or "",
                stream=row.get("renderer_stream_index") if row.get("renderer_stream_index") is not None else "—",
                paragraph=row.get("final_paragraph_index") if row.get("final_paragraph_index") is not None else "—",
                present="yes" if row.get("present_in_manuscript") else "no",
            )
        )

    lines.extend(["", "## Chapter Summary", ""])
    for row in _as_list(payload.get("chapters")):
        if not isinstance(row, Mapping):
            continue
        groups = _as_mapping(row.get("v21_surface_groups"))
        callback_bits = [
            "{plant_id}:{return_function}:{semantic_development}".format(
                plant_id=str(item.get("plant_id") or ""),
                return_function=str(item.get("return_function") or "plant"),
                semantic_development=str(item.get("semantic_development") or ""),
            )
            for item in _as_list(row.get("callback_semantics"))
            if isinstance(item, Mapping)
        ]
        lines.append(
            f"- ch{row.get('chapter')}: slot_flow={','.join(_as_list(row.get('slot_flow')))} "
            f"accents={','.join(_as_list(row.get('accent_ids')))} "
            f"engine={','.join(_as_list(groups.get('chapter_engine')))} "
            f"proof={','.join(_as_list(groups.get('proof_and_embodiment')))} "
            f"optional={','.join(_as_list(groups.get('optional_accents')))} "
            f"cohesion={','.join(_as_list(groups.get('cohesion_and_craft')))} "
            f"callbacks={','.join(callback_bits)}"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_enhancement_contract(
    *,
    enriched: EnrichedBook,
    manuscript_text: str,
    render_dir: Path,
    contract_id: str = DEFAULT_CONTRACT_ID,
    topic_id: str = "",
    persona_id: str = "",
    runtime_format: str = "",
    accent_render_audit: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Path]:
    render_dir = Path(render_dir)
    render_dir.mkdir(parents=True, exist_ok=True)
    payload = build_enhancement_contract_payload(
        enriched=enriched,
        manuscript_text=manuscript_text,
        contract_id=contract_id,
        topic_id=topic_id,
        persona_id=persona_id,
        runtime_format=runtime_format,
        accent_render_audit=accent_render_audit,
    )
    json_path = render_dir / "enhancement_contract.json"
    md_path = render_dir / "enhancement_contract.md"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_enhancement_contract_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

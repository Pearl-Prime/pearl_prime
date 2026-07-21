"""Operator-facing book outline for Pearl Prime spine renders.

Builds book_outline.md (+ companion book_outline.json) from already-landed
truth surfaces: enriched chapters, spine_context, enrichment_strategy_report,
accent assignments, section_packet_audit, and selected_content_variants.
Does not invent planner state or change assembly behavior.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from phoenix_v4.planning.accent_planner import (
    accent_class_bucket,
    build_enhancement_contract_v21_summary,
)
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter

CORE_SLOTS: tuple[str, ...] = (
    "HOOK",
    "SCENE",
    "STORY",
    "PIVOT",
    "REFLECTION",
    "EXERCISE",
    "TAKEAWAY",
    "INTEGRATION",
    "THREAD",
)

# Operator-facing enrichment family labels derived from landed slots / accents / hooks.
FAMILY_KEYS: tuple[str, ...] = (
    "metaphor",
    "analogy",
    "parable_or_external_story",
    "exercise",
    "encouragement",
    "wisdom",
    "callback",
)


def _as_mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else []


def _slot_types(chapter: EnrichedChapter) -> List[str]:
    return [str(s.slot_type or "").strip().upper() for s in (chapter.slots or []) if s.slot_type]


def _core_slot_presence(chapter: EnrichedChapter) -> Dict[str, bool]:
    present = set(_slot_types(chapter))
    return {slot: slot in present for slot in CORE_SLOTS}


def _format_slot_presence(presence: Mapping[str, bool]) -> str:
    parts = []
    for slot in CORE_SLOTS:
        mark = "✓" if presence.get(slot) else "—"
        parts.append(f"{slot} {mark}")
    return " · ".join(parts)


def _chapter_accents(
    chapter_num: int,
    assignments: Sequence[Mapping[str, Any]],
    accent_render_audit: Sequence[Mapping[str, Any]],
) -> List[Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {}
    sources = list(assignments) + list(accent_render_audit)
    for row in sources:
        try:
            ch = int(row.get("chapter") or 0)
        except (TypeError, ValueError):
            continue
        if ch != chapter_num:
            continue
        cls = str(row.get("class") or row.get("accent_class") or "").strip()
        accent_id = str(row.get("accent_id") or "").strip()
        if not cls and not accent_id:
            continue
        key = f"{cls}|{accent_id}"
        item = merged.setdefault(
            key,
            {
                "class": cls,
                "accent_id": accent_id,
                "position": "",
                "provenance": "",
                "rendered": "",
                "renderer_stream_index": "",
            },
        )
        provenance = str(
            row.get("provenance")
            or row.get("supply_source")
            or _as_mapping(row.get("keys")).get("supply_provenance")
            or ""
        ).strip()
        position = str(row.get("position") or "").strip()
        if position:
            item["position"] = position
        if provenance:
            item["provenance"] = provenance
        if "present_in_manuscript" in row:
            item["rendered"] = "yes" if row.get("present_in_manuscript") else "no"
        stream_index = row.get("renderer_stream_index")
        if stream_index is None:
            stream_index = row.get("chapter_insert_index")
        if stream_index is not None:
            item["renderer_stream_index"] = str(stream_index)
    rows = list(merged.values())
    rows.sort(key=lambda r: (r["class"], r["accent_id"]))
    return rows


def _source_tail(source_id: str) -> str:
    raw = str(source_id or "").strip()
    if ":" in raw:
        return raw.split(":", 1)[1].strip()
    return raw


def _angle_info(chapter: EnrichedChapter) -> Dict[str, Any]:
    definition_ids: List[str] = []
    callback_ids: List[str] = []
    callback_semantics: List[Dict[str, str]] = []
    for slot in chapter.slots or []:
        st = str(slot.slot_type or "").upper()
        sid = str(slot.source_id or slot.atom_id or slot.variant_id or "").strip()
        if st == "ANGLE_DEFINITION" and sid:
            definition_ids.append(sid)
            callback_semantics.append(
                {
                    "slot_type": st,
                    "plant_id": _source_tail(sid),
                    "return_function": "",
                    "semantic_development": "initial_angle_plant",
                }
            )
        elif st == "ANGLE_CALLBACK" and sid:
            callback_ids.append(sid)
            callback_semantics.append(
                {
                    "slot_type": st,
                    "plant_id": _source_tail(sid),
                    "return_function": "angle_callback",
                    "semantic_development": "later_chapter_reactivation",
                }
            )
    return {
        "definition_ids": definition_ids,
        "callback_ids": callback_ids,
        "has_definition": bool(definition_ids) or "ANGLE_DEFINITION" in _slot_types(chapter),
        "has_callback": bool(callback_ids) or "ANGLE_CALLBACK" in _slot_types(chapter),
        "callback_semantics": callback_semantics,
    }


def _chapter_v21_groups(
    chapter: EnrichedChapter,
    accents: Sequence[Mapping[str, str]],
) -> Dict[str, List[str]]:
    slot_types = set(_slot_types(chapter))
    hooks = {
        str(hook).strip().lower()
        for slot in (chapter.slots or [])
        for hook in (slot.enrichment_applied or [])
        if str(hook).strip()
    }
    accent_classes = {str(a.get("class") or "").upper() for a in accents}
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
    # NOTE: keep in sync with phoenix_v4/qa/enhancement_contract.py::_chapter_v21_groups.
    # ANALOGY/METAPHOR must be driven by their own hook signal only — the old
    # `or "ANGLE_DEFINITION" in slot_types` fallback reported both as present on
    # every angle-callback-plant chapter regardless of whether any analogy/metaphor
    # content was ever produced (no hook producer emits "analogy"/"metaphor";
    # verified against a real render: artifacts/qa/enhancement_contract_v21_integration_2026-07-13).
    if any("analogy" in hook for hook in hooks):
        cohesion_and_craft.append("ANALOGY")
    if any("metaphor" in hook for hook in hooks):
        cohesion_and_craft.append("METAPHOR")
    return {
        "chapter_engine": sorted(set(chapter_engine)),
        "proof_and_embodiment": sorted(set(proof_and_embodiment)),
        "optional_accents": optional_accents,
        "cohesion_and_craft": sorted(set(cohesion_and_craft)),
    }


def _enrichment_families(
    chapter: EnrichedChapter,
    accents: Sequence[Mapping[str, str]],
) -> Dict[str, bool]:
    slot_types = set(_slot_types(chapter))
    hooks: set[str] = set()
    for slot in chapter.slots or []:
        for h in slot.enrichment_applied or []:
            hooks.add(str(h).strip().lower())
    accent_classes = {str(a.get("class") or "").upper() for a in accents}
    story_like = (
        "EXTERNAL_STORY" in accent_classes
        or "PARABLE" in accent_classes
        or any("parable" in hook for hook in hooks)
    )
    return {
        # See _chapter_v21_groups note above: ANGLE_DEFINITION presence alone is
        # not evidence of analogy/metaphor content and must not be OR'd in here.
        "metaphor": any("metaphor" in h for h in hooks),
        "analogy": any("analogy" in h for h in hooks),
        "parable_or_external_story": story_like,
        "exercise": "EXERCISE" in slot_types
        or any(getattr(s, "journey_exercise_id", None) for s in (chapter.slots or [])),
        "encouragement": "ENCOURAGEMENT" in accent_classes,
        "wisdom": "WISDOM_ESSENCE" in accent_classes,
        "callback": "ANGLE_CALLBACK" in slot_types,
    }


def _landed_enrichment_hooks(chapter: EnrichedChapter) -> List[str]:
    out: List[str] = []
    for slot in chapter.slots or []:
        for h in slot.enrichment_applied or []:
            name = str(h).strip()
            if name and name not in out:
                out.append(name)
    return out


def _source_provenance(chapter: EnrichedChapter) -> List[str]:
    sources: List[str] = []
    for slot in chapter.slots or []:
        src = str(slot.source or "").strip()
        if not src:
            continue
        for part in src.split("+"):
            p = part.strip()
            if p and p not in sources:
                sources.append(p)
    # Prefer source_breakdown keys when slots are sparse.
    for key in sorted((chapter.source_breakdown or {}).keys()):
        k = str(key).strip()
        if k and k not in sources:
            sources.append(k)
    return sources


def _exercise_presence(chapter: EnrichedChapter) -> Dict[str, Any]:
    exercise_slots = [s for s in (chapter.slots or []) if str(s.slot_type or "").upper() == "EXERCISE"]
    journey_ids = []
    for s in exercise_slots:
        jid = getattr(s, "journey_exercise_id", None)
        if jid:
            journey_ids.append(str(jid))
    journey = chapter.exercise_journey if isinstance(chapter.exercise_journey, Mapping) else {}
    if journey.get("exercise_id"):
        journey_ids.append(str(journey["exercise_id"]))
    # de-dupe preserve order
    seen: set[str] = set()
    uniq: List[str] = []
    for j in journey_ids:
        if j not in seen:
            seen.add(j)
            uniq.append(j)
    return {
        "present": bool(exercise_slots),
        "slot_count": len(exercise_slots),
        "journey_exercise_ids": uniq,
    }


def _story_presence(
    chapter: EnrichedChapter,
    accents: Sequence[Mapping[str, str]],
) -> Dict[str, Any]:
    story_slots = [s for s in (chapter.slots or []) if str(s.slot_type or "").upper() == "STORY"]
    external = [a for a in accents if str(a.get("class") or "").upper() == "EXTERNAL_STORY"]
    return {
        "story_slot": bool(story_slots),
        "story_slot_count": len(story_slots),
        "external_story_accents": [
            {"accent_id": a.get("accent_id") or "", "provenance": a.get("provenance") or ""}
            for a in external
        ],
        "present": bool(story_slots) or bool(external),
    }


def _chapter_outline_row(
    chapter: EnrichedChapter,
    *,
    assignments: Sequence[Mapping[str, Any]],
    accent_render_audit: Sequence[Mapping[str, Any]],
    spa_by_chapter: Mapping[int, List[Mapping[str, Any]]],
) -> Dict[str, Any]:
    accents = _chapter_accents(chapter.number, assignments, accent_render_audit)
    families = _enrichment_families(chapter, accents)
    angle = _angle_info(chapter)
    spa_rows = list(spa_by_chapter.get(int(chapter.number), []))
    return {
        "number": int(chapter.number),
        "role": str(chapter.role or "").strip(),
        "working_title": str(chapter.working_title or "").strip(),
        "thesis": str(chapter.thesis or "").strip(),
        "core_slots": _core_slot_presence(chapter),
        "slot_types_landed": _slot_types(chapter),
        "angle": angle,
        "callback_semantics": list(angle.get("callback_semantics") or []),
        "enrichment_hooks": _landed_enrichment_hooks(chapter),
        "enrichment_families": families,
        "v21_surface_groups": _chapter_v21_groups(chapter, accents),
        "accents": accents,
        "exercise": _exercise_presence(chapter),
        "story": _story_presence(chapter, accents),
        "source_provenance": _source_provenance(chapter),
        "section_packet_rows": [
            {
                "slot_type": str(r.get("slot_type") or ""),
                "source": str(r.get("source") or ""),
                "source_id": str(r.get("source_id") or ""),
            }
            for r in spa_rows
        ],
        "total_words": int(chapter.total_words or 0),
    }


def _spa_by_chapter(audit: Mapping[str, Any]) -> Dict[int, List[Mapping[str, Any]]]:
    spa = audit.get("section_packet_audit")
    rows: List[Any] = []
    if isinstance(spa, list):
        rows = spa
    elif isinstance(spa, Mapping):
        nested = spa.get("slots")
        if isinstance(nested, list):
            rows = nested
    out: Dict[int, List[Mapping[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            ch = int(row.get("chapter") or 0)
        except (TypeError, ValueError):
            continue
        if ch <= 0:
            continue
        out.setdefault(ch, []).append(row)
    return out


def build_book_outline_payload(
    enriched: EnrichedBook,
    *,
    topic_id: str = "",
    persona_id: str = "",
    locale: str = "",
    runtime_format: str = "",
    accent_render_audit: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build structured outline dict from landed enrichment surfaces."""
    audit = _as_mapping(enriched.enrichment_audit)
    strategy = _as_mapping(audit.get("enrichment_strategy_report"))
    spine = _as_mapping(enriched.spine_context)
    assignments = _as_list(spine.get("accent_assignments")) or _as_list(strategy.get("assignments"))
    render_audit = list(accent_render_audit or [])
    if not render_audit:
        render_audit = _as_list(audit.get("accent_render_audit"))

    book_idea = str(strategy.get("book_idea") or spine.get("book_idea") or "").strip()
    book_motif = str(strategy.get("book_motif") or spine.get("book_motif") or "").strip()
    strategy_profile = str(
        strategy.get("enrichment_strategy_profile")
        or strategy.get("strategy_profile")
        or spine.get("story_mix_profile")
        or ""
    ).strip()
    v21_summary = _as_mapping(strategy.get("enhancement_contract_v21")) or _as_mapping(
        spine.get("enhancement_contract_v21")
    )
    if not v21_summary:
        v21_summary = build_enhancement_contract_v21_summary(
            accent_budget=_as_mapping(spine.get("accent_budget") or strategy.get("accent_budget")),
            flat_rows=assignments,
            chapter_count=len(enriched.chapters or []),
            story_mix_profile=strategy_profile,
            max_accents_per_chapter=int(
                _as_mapping(_as_mapping(strategy.get("enhancement_contract_v21")).get("optional_accent_budget")).get(
                    "max_accents_per_chapter"
                )
                or 2
            ),
            persona_id=persona_id or str(enriched.persona_id or ""),
            topic_id=topic_id or str(enriched.topic or ""),
        )

    spa_map = _spa_by_chapter(audit)
    chapters = [
        _chapter_outline_row(
            ch,
            assignments=assignments,
            accent_render_audit=render_audit,
            spa_by_chapter=spa_map,
        )
        for ch in (enriched.chapters or [])
    ]

    return {
        "schema_version": 1,
        "stage": "book_outline",
        "topic": topic_id or str(enriched.topic or ""),
        "persona_id": persona_id or str(enriched.persona_id or ""),
        "locale": locale or str(getattr(enriched, "locale", None) or "") or "en-US",
        "runtime_format": runtime_format or str(enriched.runtime_format or ""),
        "book_idea": book_idea,
        "book_motif": book_motif,
        "enrichment_strategy_profile": strategy_profile,
        "brand_accent_profile": str(strategy.get("brand_accent_profile") or "").strip(),
        "enhancement_contract_v21": v21_summary,
        "chapter_count": len(chapters),
        "chapters": chapters,
    }


def render_book_outline_markdown(payload: Mapping[str, Any]) -> str:
    """Render a concise operator-readable markdown outline."""
    lines: List[str] = [
        "# Book Outline",
        "",
        f"**Topic / persona:** `{payload.get('topic') or ''}` × `{payload.get('persona_id') or ''}`",
        f"**Locale:** `{payload.get('locale') or ''}`",
        f"**Runtime format:** `{payload.get('runtime_format') or ''}`",
        f"**Book idea:** {payload.get('book_idea') or '_none recorded_'}",
        f"**Book motif:** {payload.get('book_motif') or '_none recorded_'}",
        f"**Enrichment strategy profile:** `{payload.get('enrichment_strategy_profile') or ''}`",
    ]
    brand = str(payload.get("brand_accent_profile") or "").strip()
    if brand:
        lines.append(f"**Brand accent profile:** `{brand}`")
    v21 = _as_mapping(payload.get("enhancement_contract_v21"))
    if v21:
        opt = _as_mapping(v21.get("optional_accent_budget"))
        actual = _as_mapping(opt.get("actual"))
        lines.append(
            "**V2.1 optional budget:** "
            f"assigned={actual.get('assigned_total_optional_accents') or 0} / "
            f"hard_max={opt.get('hard_max_total_accents') or 0} / "
            f"max_per_chapter={opt.get('max_accents_per_chapter') or 0}"
        )
    lines.extend(["", f"**Chapters:** {payload.get('chapter_count') or 0}", ""])

    chapters = _as_list(payload.get("chapters"))
    if not chapters:
        lines.append("_No chapters recorded._")
        lines.append("")
        return "\n".join(lines)

    for ch in chapters:
        if not isinstance(ch, Mapping):
            continue
        num = ch.get("number") or 0
        role = str(ch.get("role") or "").strip()
        title = str(ch.get("working_title") or "").strip()
        heading = f"## Chapter {num}"
        if role:
            heading += f" — {role}"
        if title and title != role:
            heading += f" ({title})"
        lines.append(heading)
        lines.append("")

        thesis = str(ch.get("thesis") or "").strip()
        if thesis:
            lines.append(f"**Thesis:** {thesis}")
        else:
            lines.append("**Thesis:** _none recorded_")

        presence = _as_mapping(ch.get("core_slots"))
        lines.append(f"**Core slots:** {_format_slot_presence(presence)}")

        angle = _as_mapping(ch.get("angle"))
        def_ids = [str(x) for x in _as_list(angle.get("definition_ids")) if x]
        cb_ids = [str(x) for x in _as_list(angle.get("callback_ids")) if x]
        angle_bits: List[str] = []
        if angle.get("has_definition"):
            angle_bits.append("DEFINITION " + (", ".join(f"`{x}`" for x in def_ids) if def_ids else "landed"))
        if angle.get("has_callback"):
            angle_bits.append("CALLBACK " + (", ".join(f"`{x}`" for x in cb_ids) if cb_ids else "landed"))
        lines.append(f"**Angle:** {'; '.join(angle_bits) if angle_bits else '_none_'}")

        hooks = [str(h) for h in _as_list(ch.get("enrichment_hooks")) if h]
        lines.append(
            "**Enrichment hooks:** "
            + (", ".join(f"`{h}`" for h in hooks) if hooks else "_none_")
        )

        families = _as_mapping(ch.get("enrichment_families"))
        fam_landed = [k for k in FAMILY_KEYS if families.get(k)]
        lines.append(
            "**Enrichment families:** "
            + (", ".join(fam_landed) if fam_landed else "_none_")
        )

        v21_groups = _as_mapping(ch.get("v21_surface_groups"))
        lines.append(
            "**V2.1 groups:** "
            + " | ".join(
                [
                    "engine=" + ",".join(_as_list(v21_groups.get("chapter_engine"))),
                    "proof=" + ",".join(_as_list(v21_groups.get("proof_and_embodiment"))),
                    "optional=" + ",".join(_as_list(v21_groups.get("optional_accents"))),
                    "cohesion=" + ",".join(_as_list(v21_groups.get("cohesion_and_craft"))),
                ]
            )
        )

        accents = [a for a in _as_list(ch.get("accents")) if isinstance(a, Mapping)]
        if accents:
            accent_bits = []
            for a in accents:
                cls = str(a.get("class") or "")
                aid = str(a.get("accent_id") or "")
                bit = f"{cls}" + (f" `{aid}`" if aid else "")
                pos = str(a.get("position") or "")
                prov = str(a.get("provenance") or "")
                rendered = str(a.get("rendered") or "")
                stream = str(a.get("renderer_stream_index") or "")
                extras = []
                if pos:
                    extras.append(f"@{pos}")
                if prov:
                    extras.append(f"via {prov}")
                if stream:
                    extras.append(f"stream {stream}")
                if rendered:
                    extras.append(f"rendered={rendered}")
                if extras:
                    bit += " (" + ", ".join(extras) + ")"
                accent_bits.append(bit)
            lines.append("**Accents:** " + " · ".join(accent_bits))
        else:
            lines.append("**Accents:** _none_")

        exercise = _as_mapping(ch.get("exercise"))
        if exercise.get("present"):
            jids = [str(x) for x in _as_list(exercise.get("journey_exercise_ids")) if x]
            extra = f" (journey: {', '.join(jids)})" if jids else ""
            lines.append(f"**Exercise:** yes ×{exercise.get('slot_count') or 1}{extra}")
        else:
            lines.append("**Exercise:** no")

        story = _as_mapping(ch.get("story"))
        if story.get("present"):
            bits = []
            if story.get("story_slot"):
                bits.append(f"STORY slot ×{story.get('story_slot_count') or 1}")
            for ext in _as_list(story.get("external_story_accents")):
                if isinstance(ext, Mapping) and ext.get("accent_id"):
                    bits.append(f"EXTERNAL_STORY `{ext.get('accent_id')}`")
                elif isinstance(ext, Mapping):
                    bits.append("EXTERNAL_STORY")
            lines.append(f"**Story / parable / external:** {' · '.join(bits) if bits else 'yes'}")
        else:
            lines.append("**Story / parable / external:** _none_")

        callback_semantics = [
            item
            for item in _as_list(ch.get("callback_semantics"))
            if isinstance(item, Mapping)
        ]
        if callback_semantics:
            bits = []
            for item in callback_semantics:
                bits.append(
                    "{slot} `{plant}` {ret} {dev}".format(
                        slot=str(item.get("slot_type") or ""),
                        plant=str(item.get("plant_id") or ""),
                        ret=str(item.get("return_function") or "plant"),
                        dev=str(item.get("semantic_development") or ""),
                    ).strip()
                )
            lines.append("**Callback semantics:** " + " · ".join(bits))
        else:
            lines.append("**Callback semantics:** _none_")

        provenance = [str(p) for p in _as_list(ch.get("source_provenance")) if p]
        lines.append(
            "**Provenance:** "
            + (", ".join(f"`{p}`" for p in provenance) if provenance else "_none_")
        )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_book_outline(
    *,
    enriched: EnrichedBook,
    render_dir: Path,
    topic_id: str = "",
    persona_id: str = "",
    locale: str = "",
    runtime_format: str = "",
    accent_render_audit: Optional[Sequence[Mapping[str, Any]]] = None,
    write_json: bool = True,
) -> Dict[str, Path]:
    """Write book_outline.md and optionally book_outline.json into render_dir."""
    render_dir = Path(render_dir)
    render_dir.mkdir(parents=True, exist_ok=True)
    payload = build_book_outline_payload(
        enriched,
        topic_id=topic_id,
        persona_id=persona_id,
        locale=locale,
        runtime_format=runtime_format,
        accent_render_audit=accent_render_audit,
    )
    md_path = render_dir / "book_outline.md"
    md_path.write_text(render_book_outline_markdown(payload), encoding="utf-8")
    out: Dict[str, Path] = {"markdown": md_path}
    if write_json:
        json_path = render_dir / "book_outline.json"
        json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        out["json"] = json_path
    return out

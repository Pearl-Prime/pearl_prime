"""
Deterministic section packet assembly — bridge → journey → legacy → enrichment → teacher → depth.

Stacks all available layers (no mutual exclusion). Same inputs produce the same output.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from phoenix_v4.rendering.book_renderer import clean_for_delivery
except ImportError:  # pragma: no cover

    def clean_for_delivery(text: str, plan: Optional[dict] = None) -> str:
        del plan
        return (text or "").strip()

from phoenix_v4.planning.exercise_journey_planner import JOURNEY_INTROS


_DOUBLE_BRACE_RE = re.compile(r"\{\{[^}]+\}\}")
_SINGLE_BRACE_RE = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def _strip_placeholders(text: str) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    def sub_double(m: re.Match[str]) -> str:
        warnings.append(f"unresolved_placeholder:{m.group(0)}")
        return ""

    def sub_single(m: re.Match[str]) -> str:
        warnings.append(f"unresolved_placeholder:{m.group(0)}")
        return ""

    out = _DOUBLE_BRACE_RE.sub(sub_double, text)
    out = _SINGLE_BRACE_RE.sub(sub_single, out)
    return out, warnings


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _packet_injection_seed(spine_context: dict, chapter_index: int, section_index: int) -> str:
    ctx = spine_context or {}
    base = str(ctx.get("packet_seed") or ctx.get("seed") or "inject").strip() or "inject"
    return f"{base}:inject:{chapter_index}:{section_index}"


def _exercise_phase_dict_for_injection(
    exercise_phase: Optional[Any],
    enrichment_slot: Optional[dict],
) -> Optional[dict]:
    if isinstance(exercise_phase, dict):
        return exercise_phase
    if exercise_phase and enrichment_slot and isinstance(enrichment_slot, dict):
        jid = enrichment_slot.get("journey_exercise_id")
        if jid:
            return {"phase": str(exercise_phase), "exercise_id": str(jid)}
    return None


def _collapse_ws(text: str) -> str:
    return " ".join((text or "").split())


def _enrichment_split(enrichment_slot: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    """Core body vs depth body based on source prefix."""
    if not enrichment_slot:
        return "", ""
    src = str(enrichment_slot.get("source") or "")
    body = str(enrichment_slot.get("content") or "").strip()
    if src.startswith("depth_module:"):
        return "", body
    return body, ""


def _exercise_phase_key(exercise_phase: Any) -> Optional[str]:
    if exercise_phase is None:
        return None
    if isinstance(exercise_phase, dict):
        p = exercise_phase.get("phase")
        if p is None:
            return None
        s = str(p).strip().lower()
        return s if s else None
    s = str(exercise_phase).strip().lower()
    return s if s else None


def _append_layer(
    blocks: List[str],
    sources_used: List[str],
    label: str,
    text: str,
    seen_norms: set[str],
    *,
    min_words: int = 11,
) -> None:
    raw = (text or "").strip()
    if _word_count(raw) < min_words:
        return
    norm = _collapse_ws(raw)
    if norm in seen_norms:
        return
    seen_norms.add(norm)
    blocks.append(raw)
    sources_used.append(label)


def compose_section_packet(
    *,
    chapter_index: int,
    section_index: int,
    section_type: str,
    target_words: int,
    spine_context: dict,
    beatmap_slot: dict,
    enrichment_slot: Optional[dict],
    legacy_template_section: Optional[Dict[str, Any]] = None,
    bridge_text: Optional[str] = None,
    quality_profile: str = "draft",
    exercise_phase: Optional[Any] = None,
    depth_module_content: Optional[str] = None,
    teacher_atom_content: Optional[str] = None,
) -> dict:
    """
    Stack all available layers into one section packet.

    Order:
      1. Bridge (optional)
      2. Exercise journey intro (optional)
      3. Legacy template scaffold (optional)
      4. Core enrichment (registry / persona / practice / gap — not depth_module-only rows)
      5. Teacher atom overlay (optional, separate from slot.content when passed explicitly)
      6. Depth module expansion (explicit arg and/or depth_module:* enrichment source)
    """
    del beatmap_slot, quality_profile  # reserved for future routing / parity
    spine_context = spine_context or {}

    sources_used: List[str] = []
    blocks: List[str] = []
    extra_warnings: List[str] = []
    seen_norms: set[str] = set()

    if bridge_text and str(bridge_text).strip():
        _append_layer(blocks, sources_used, "bridge", str(bridge_text), seen_norms, min_words=1)

    phase_key = _exercise_phase_key(exercise_phase)
    if phase_key:
        intro = JOURNEY_INTROS.get(phase_key)
        if intro:
            _append_layer(
                blocks,
                sources_used,
                f"journey_intro:{phase_key}",
                intro,
                seen_norms,
                min_words=1,
            )

    legacy_text = ""
    if legacy_template_section:
        legacy_text = str(legacy_template_section.get("text") or "").strip()
        if legacy_text:
            from phoenix_v4.planning.injection_resolver import resolve_injections

            inj_seed = _packet_injection_seed(spine_context, chapter_index, section_index)
            ex_phase_dict = _exercise_phase_dict_for_injection(exercise_phase, enrichment_slot)
            resolved = resolve_injections(
                legacy_text,
                chapter_index=chapter_index,
                section_index=section_index,
                section_type=section_type,
                topic=str(spine_context.get("topic") or spine_context.get("topic_id") or ""),
                persona_id=str(spine_context.get("persona_id") or ""),
                teacher_id=spine_context.get("teacher_id"),
                exercise_phase=ex_phase_dict,
                seed=inj_seed,
            )
            legacy_text = str(resolved.get("text") or "").strip()
            for src in resolved.get("sources_used") or []:
                if src:
                    sources_used.append(str(src))
            for failed in resolved.get("injections_failed") or []:
                extra_warnings.append(f"injection failed: {failed}")
            _append_layer(
                blocks,
                sources_used,
                "legacy_template",
                legacy_text,
                seen_norms,
                min_words=11,
            )

    core_from_slot, depth_from_slot = _enrichment_split(enrichment_slot)
    core = core_from_slot.strip()

    if core:
        gap = core.startswith("[CONTENT GAP:")
        min_c = 1 if gap else 11
        if _word_count(core) >= min_c and (
            gap or _collapse_ws(core) != _collapse_ws(legacy_text)
        ):
            _append_layer(blocks, sources_used, "enrichment", core, seen_norms, min_words=min_c)

    if teacher_atom_content:
        _append_layer(
            blocks,
            sources_used,
            "teacher_atom",
            str(teacher_atom_content),
            seen_norms,
            min_words=11,
        )

    depth_text = (depth_module_content or "").strip() or depth_from_slot
    if depth_text and _word_count(depth_text) >= 11:
        _append_layer(blocks, sources_used, "depth_module", depth_text, seen_norms, min_words=11)

    raw_text = "\n\n".join(b for b in blocks if b)
    cleaned_placeholders, ph_warn = _strip_placeholders(raw_text)
    extra_warnings.extend(ph_warn)

    final_text = clean_for_delivery(cleaned_placeholders, plan=None)
    wc = _word_count(final_text)

    return {
        "text": final_text,
        "word_count": wc,
        "sources_used": sources_used,
        "target_words": target_words,
        "under_target": wc < target_words,
        "warnings": extra_warnings,
        "section_type": section_type,
        "chapter_index": chapter_index,
        "section_index": section_index,
    }

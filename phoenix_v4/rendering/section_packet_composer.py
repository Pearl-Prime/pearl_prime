"""
Deterministic section packet assembly — bridge → legacy → enrichment → depth.

No LLM calls. Same inputs produce the same output.
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


def _enrichment_split(enrichment_slot: Optional[Dict[str, Any]]) -> Tuple[str, str]:
    """Core body vs depth body based on source prefix."""
    if not enrichment_slot:
        return "", ""
    src = str(enrichment_slot.get("source") or "")
    body = str(enrichment_slot.get("content") or "").strip()
    if src.startswith("depth_module:"):
        return "", body
    return body, ""


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
    exercise_phase: Optional[str] = None,
) -> dict:
    """
    Compose a single section packet from multiple sources.

    Assembly order:
      1. Bridge snippet (optional)
      2. Legacy template scaffold (optional)
      3. Core enrichment content (non-depth_module sources)
      4. Depth module content (depth_module source OR explicit depth in slot)
    """
    del beatmap_slot, spine_context, quality_profile  # reserved for future routing / parity

    sources_used: List[str] = []
    blocks: List[str] = []
    extra_warnings: List[str] = []

    if bridge_text and str(bridge_text).strip():
        blocks.append(str(bridge_text).strip())
        sources_used.append("bridge")

    legacy_text = ""
    if legacy_template_section:
        legacy_text = str(legacy_template_section.get("text") or "").strip()
        if legacy_text:
            blocks.append(legacy_text)
            sources_used.append("legacy_template")

    core, depth_from_split = _enrichment_split(enrichment_slot)

    if exercise_phase:
        phase_key = str(exercise_phase).strip().lower()
        intro = JOURNEY_INTROS.get(phase_key)
        if intro:
            blocks.append(intro)
            sources_used.append("journey_transition")

    if core:
        blocks.append(core)
        sources_used.append("enrichment")

    depth_body = depth_from_split
    if not depth_body and enrichment_slot:
        src = str(enrichment_slot.get("source") or "")
        if src.startswith("depth_module:"):
            depth_body = str(enrichment_slot.get("content") or "").strip()

    if depth_body:
        blocks.append(depth_body)
        if "depth_module" not in sources_used:
            sources_used.append("depth_module")

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

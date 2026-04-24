"""
Deterministic section packet assembly — bridge → journey → legacy → enrichment → teacher → depth.

Stacks all available layers (no mutual exclusion). Same inputs produce the same output.

Spine manuscripts apply manuscript-level flow cohesion via
``book_renderer.strengthen_rendered_spine_manuscript`` after ``compose_from_enriched_book``.
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

# Location profile registry — loaded once from config/localization/render_location_profiles.yaml
_location_profiles_cache: Optional[Dict[str, Any]] = None
_DEFAULT_LOCATION_PROFILE = "generic_us_urban"

# Per-persona default location profile (based on persona_aware_grounding_research.md)
_PERSONA_LOCATION_DEFAULTS: Dict[str, str] = {
    "corporate_managers":          "nyc_grand_central",
    "millennial_women_professionals": "nyc_metro",
    "tech_finance_burnout":        "generic_us_urban",
    "gen_z_professionals":         "generic_us_urban",
    "entrepreneurs":               "coastal_california",
    "working_parents":             "generic_us_urban",
    "healthcare_rns":              "generic_us_urban",
    "first_responders":            "generic_us_urban",
    "gen_x_sandwich":              "generic_us_urban",
    "gen_alpha_students":          "generic_us_urban",
}

# Hard fallbacks used only when profile file is missing or a token has no profile entry.
_LOCALE_TOKEN_HARDCODED_FALLBACKS: Dict[str, str] = {
    "street_name":    "the street below",
    "weather_detail": "the afternoon light",
    "transit_line":   "the train",
    "transit_stop":   "the platform",
    "city_name":      "the city",
    "neighborhood":   "the neighborhood",
    "building_type":  "the building",
    "local_landmark": "a landmark nearby",
    "park_name":      "the park",
    "coffee_shop":    "a coffee shop",
    "commute_mode":   "the commute",
    "restaurant":     "a nearby restaurant",
    "store_name":     "a nearby store",
    "office_building": "the office building",
}


def _load_location_profiles() -> Dict[str, Any]:
    global _location_profiles_cache
    if _location_profiles_cache is not None:
        return _location_profiles_cache
    try:
        import yaml as _yaml
        from pathlib import Path as _Path
        _repo = _Path(__file__).resolve().parent.parent.parent
        _path = _repo / "config" / "localization" / "render_location_profiles.yaml"
        if _path.exists():
            with open(_path, encoding="utf-8") as _f:
                _data = _yaml.safe_load(_f) or {}
            _location_profiles_cache = _data.get("profiles") or {}
        else:
            _location_profiles_cache = {}
    except Exception:
        _location_profiles_cache = {}
    return _location_profiles_cache


def _resolve_location_profile(spine_context: Dict[str, Any]) -> Dict[str, str]:
    """
    Return a {token_name: value} map for the book's location profile.
    Priority: spine_context["location_profile"] > persona default > generic_us_urban.
    Falls back to hardcoded strings if profile file is missing.
    """
    profiles = _load_location_profiles()
    if not profiles:
        return dict(_LOCALE_TOKEN_HARDCODED_FALLBACKS)

    # Determine which profile to use
    explicit = str(spine_context.get("location_profile") or "").strip().lower()
    persona_id = str(spine_context.get("persona_id") or "").strip()
    persona_default = _PERSONA_LOCATION_DEFAULTS.get(persona_id, _DEFAULT_LOCATION_PROFILE)
    profile_key = explicit or persona_default

    profile = profiles.get(profile_key) or profiles.get(_DEFAULT_LOCATION_PROFILE) or {}
    result: Dict[str, str] = dict(_LOCALE_TOKEN_HARDCODED_FALLBACKS)
    result.update({k: str(v) for k, v in profile.items() if k != "aliases" and v})
    return result


_SENTENCE_START_RE = re.compile(r'(^|[.!?]\s+|\n\s*)(\{[A-Za-z_][A-Za-z_0-9.]*\})')


def _fill_locale_tokens(text: str, location_tokens: Optional[Dict[str, str]] = None) -> str:
    """Replace {token_name} placeholders with resolved locale values.

    Case-insensitive matching: handles both {weather_detail} and {Weather_detail}
    (the latter appears in some first_responders and entrepreneurs atom files due
    to an authoring inconsistency — treated as the same token).

    Sentence-start capitalization: when a token appears after a period/newline,
    the substitution is capitalized so ". {street_name}" → ". Traffic" (not ". traffic").
    Fixes the 1,926 lowercase-after-period bugs found in ch1_sprint_v2.
    """
    tokens = location_tokens or _LOCALE_TOKEN_HARDCODED_FALLBACKS

    # First: capitalize values whose {token} lands at sentence start.
    def _cap_start(m: re.Match[str]) -> str:
        prefix, token_braced = m.group(1), m.group(2)
        token_name = token_braced[1:-1]
        # Look up value (handles title-case authoring variant)
        value = tokens.get(token_name) or tokens.get(token_name[0].lower() + token_name[1:])
        if not value:
            return m.group(0)  # unknown token — leave for fallback pass
        capped = value[0].upper() + value[1:] if value else value
        return f"{prefix}{capped}"

    text = _SENTENCE_START_RE.sub(_cap_start, text)

    # Second: replace remaining (mid-sentence) occurrences with the lowercase value.
    for token_name, value in tokens.items():
        text = text.replace(f"{{{token_name}}}", value)
        title_token = token_name[0].upper() + token_name[1:]
        if title_token != token_name:
            text = text.replace(f"{{{title_token}}}", value)
    return text

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
    """Seed must be scoped by (topic, persona, book_seed) so different books never pick
    the same HOOK variant deterministically. Previously used only args.seed, which caused
    all 195 ch1_sprint_v2 books to open chapter 1 with the identical Elena passage.
    """
    ctx = spine_context or {}
    base = str(ctx.get("packet_seed") or ctx.get("seed") or "inject").strip() or "inject"
    topic = str(ctx.get("topic") or ctx.get("topic_id") or "").strip()
    persona = str(ctx.get("persona_id") or "").strip()
    teacher = str(ctx.get("teacher_id") or "").strip()
    scope = ":".join(p for p in (topic, persona, teacher) if p) or "global"
    return f"{base}:{scope}:inject:{chapter_index}:{section_index}"


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
    # Defense in depth: never let CONTENT GAP sentinels into the final prose,
    # regardless of which code path produced them.
    if raw.startswith("[CONTENT GAP:") or "[CONTENT GAP:" in raw:
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
    expand_thin_sections: bool = False,
    teacher_voice: Optional[Any] = None,
    supplemental_enrichment_blocks: Optional[List[str]] = None,
    story_schedule: Optional[Any] = None,
    slot_tracker: Optional[Any] = None,
) -> dict:
    """
    Stack all available layers into one section packet.

    Order:
      1. Bridge (optional)
      2. Exercise journey intro (optional)
      3. [HOOK only] Core enrichment first — recognition beat precedes somatic invitation
      4. Legacy template scaffold (optional)
      5. Core enrichment (all non-HOOK section types)
      6. Supplemental enrichment blocks (optional — multi-variant / format scaling)
      7. Teacher atom overlay — only when spine_context["teacher_id"] is set
      8. Depth module expansion (explicit arg and/or depth_module:* enrichment source)

    When ``beatmap_slot`` includes ``target_words``, it overrides the ``target_words`` argument.
    """
    del quality_profile  # reserved for future routing / parity
    spine_context = spine_context or {}
    bm_slot = beatmap_slot or {}
    tw_slot = bm_slot.get("target_words")
    if isinstance(tw_slot, int) and tw_slot > 0:
        target_words = tw_slot

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

    core_from_slot, depth_from_slot = _enrichment_split(enrichment_slot)
    core = core_from_slot.strip()

    # ── HOOK: persona-specific recognition beat precedes the somatic template ────
    # Priority: scene_recognition bank (persona+topic filtered, forbidden_terms enforced)
    # → fall back to enrichment slot content if no bank entry found for this persona.
    # The template's somatic invitation always follows.
    is_hook = str(section_type).upper() == "HOOK"
    if is_hook:
        _hook_beat: Optional[str] = None
        _hook_source: str = "enrichment"
        try:
            from phoenix_v4.planning.injection_resolver import _find_scene_content
            _persona = str(spine_context.get("persona_id") or "")
            _topic = str(spine_context.get("topic") or spine_context.get("topic_id") or "")
            _hook_seed = _packet_injection_seed(spine_context, chapter_index, section_index)
            try:
                import importlib
                _root = importlib.import_module("phoenix_v4.planning.injection_resolver").REPO_ROOT
            except Exception:
                from pathlib import Path as _Path
                _root = _Path(__file__).resolve().parent.parent.parent
            _scene = _find_scene_content(
                _topic, _persona, _hook_seed, _root,
                bank_type="recognition",
                slot_tracker=slot_tracker,
            )
            if _scene and _word_count(str(_scene.get("text") or "")) >= 5:
                _hook_beat = str(_scene["text"]).strip()
                _hook_source = str(_scene.get("source") or "scene_recognition")
        except Exception:
            pass
        # Fall back to enrichment slot content if no recognition bank hit
        if not _hook_beat and core and not core.startswith("[CONTENT GAP:"):
            _hook_beat = core
        if _hook_beat:
            _append_layer(blocks, sources_used, _hook_source, _hook_beat, seen_norms, min_words=5)
        core = ""  # consumed for HOOK; skip post-template enrichment append below

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
                story_schedule=story_schedule,
                slot_tracker=slot_tracker,
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

    if core:
        # NEVER append CONTENT GAP sentinels to prose — they were leaking into 100% of
        # books (3,031 occurrences in ch1_sprint_v2). Gap is a signal, not content.
        if core.startswith("[CONTENT GAP:"):
            extra_warnings.append(f"enrichment_gap_suppressed: {core[:80]}")
        elif (
            _word_count(core) >= 11
            and _collapse_ws(core) != _collapse_ws(legacy_text)
        ):
            _append_layer(blocks, sources_used, "enrichment", core, seen_norms, min_words=11)

    extra_blocks: List[str] = list(supplemental_enrichment_blocks or [])
    slot_supp = bm_slot.get("supplemental_enrichment_blocks")
    if isinstance(slot_supp, list):
        for item in slot_supp:
            if isinstance(item, str) and item.strip():
                extra_blocks.append(item)
    for bi, blk in enumerate(extra_blocks):
        _append_layer(
            blocks,
            sources_used,
            f"enrichment_supplement:{bi}",
            blk,
            seen_norms,
            min_words=11,
        )

    # Teacher atom only appends in explicit teacher mode (teacher_id set in spine_context).
    # Without a teacher_id the content has no owner, no wrapper, and no voice attribution.
    _teacher_id = spine_context.get("teacher_id") or spine_context.get("teacher")
    if teacher_atom_content and _teacher_id:
        from phoenix_v4.rendering.teacher_wrapper import resolve_wrapper

        _wrap_seed = _packet_injection_seed(spine_context, chapter_index, section_index)
        _prefix, _suffix = resolve_wrapper(
            teacher_id=str(_teacher_id),
            section_type=section_type,
            seed=_wrap_seed,
            spine_context=spine_context,
        )
        _tw_content = str(teacher_atom_content).strip()
        if _prefix or _suffix:
            _parts: List[str] = []
            if _prefix:
                _parts.append(_prefix)
            _parts.append(_tw_content)
            if _suffix:
                _parts.append(_suffix)
            _tw_content = "\n\n".join(_parts)
        _append_layer(
            blocks,
            sources_used,
            "teacher_atom",
            _tw_content,
            seen_norms,
            min_words=11,
        )

    depth_text = (depth_module_content or "").strip() or depth_from_slot
    if depth_text and _word_count(depth_text) >= 11:
        _append_layer(blocks, sources_used, "depth_module", depth_text, seen_norms, min_words=11)

    raw_text = "\n\n".join(b for b in blocks if b)

    # ── Slot-level word cap ──────────────────────────────────────────────────
    # Honour beatmap target_words as a hard ceiling.  The legacy
    # ``packet_word_cap`` key (never injected by any caller) is kept as a
    # secondary override.
    _cap = spine_context.get("packet_word_cap")
    if not (isinstance(_cap, int) and _cap > 0):
        # Use beatmap target_words as the cap (with 10 % headroom so sentences
        # don't get cut mid-thought).
        _cap = int(target_words * 1.10) if target_words and target_words > 0 else 0
    if isinstance(_cap, int) and _cap > 0:
        _w = raw_text.split()
        if len(_w) > _cap:
            raw_text = " ".join(_w[:_cap]).strip()

    # Fill {selected_mechanism} / {selected_signal} before locale tokens and strip pass.
    # These appear in REFLECTION atoms for tech_finance_burnout + millennial_women_professionals.
    _mech_topic = str(spine_context.get("topic") or spine_context.get("topic_id") or "")
    _mech_persona = str(spine_context.get("persona_id") or "")
    _mech_seed = _packet_injection_seed(spine_context, chapter_index, section_index)
    if _mech_topic and _mech_persona and (
        "{selected_mechanism}" in raw_text or "{selected_signal}" in raw_text
    ):
        try:
            from phoenix_v4.planning.injection_resolver import (
                _fill_mechanism_tokens as _fmt,
            )
        except ImportError:
            _fmt = None  # resolver unavailable — leave _strip_placeholders to scrub
        if _fmt is not None:
            from pathlib import Path as _Path
            _mech_root = _Path(__file__).resolve().parent.parent.parent
            raw_text = _fmt(raw_text, _mech_persona, _mech_topic, _mech_seed, _mech_root)

    _loc_tokens = _resolve_location_profile(spine_context)
    raw_text = _fill_locale_tokens(raw_text, _loc_tokens)
    cleaned_placeholders, ph_warn = _strip_placeholders(raw_text)
    extra_warnings.extend(ph_warn)

    # ── Pearl_Writer thin-section expansion (spec: docs/PEARL_WRITER_EXPANSION_SPEC.md) ──
    # Runs AFTER stacking, BEFORE clean_for_delivery.  Default OFF — must opt in.
    expansion_result: Optional[dict] = None
    if expand_thin_sections:
        from phoenix_v4.rendering.pearl_writer_expand import expand_section, should_expand

        _pre_packet = {
            "text": cleaned_placeholders,
            "word_count": _word_count(cleaned_placeholders),
            "target_words": target_words,
            "sources_used": list(sources_used),
            "warnings": list(extra_warnings),
            "section_type": section_type,
            "chapter_index": chapter_index,
            "section_index": section_index,
        }
        if should_expand(_pre_packet):
            _ctx = dict(spine_context)
            _seed = (
                f"{_ctx.get('packet_seed') or _ctx.get('seed') or 'pw'}"
                f":expand:{chapter_index}:{section_index}:expansion_v1"
            )
            _expand_req = {
                "packet": _pre_packet,
                "spine_context": _ctx,
                "teacher_voice": teacher_voice,
                "layer_preservation": list(sources_used),
                "seed": _seed,
            }
            expansion_result = expand_section(_expand_req, dry_run=False)
            if expansion_result.get("expanded"):
                cleaned_placeholders = expansion_result["text"]
                extra_warnings.extend(expansion_result.get("warnings") or [])
                sources_used = list(sources_used) + (
                    expansion_result.get("sources_used_delta") or []
                )

    final_text = clean_for_delivery(cleaned_placeholders, plan=None)
    wc = _word_count(final_text)

    result: Dict[str, Any] = {
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
    if expansion_result is not None:
        result["pearl_writer_expansion"] = {
            "expanded": expansion_result.get("expanded", False),
            "layer_map": expansion_result.get("layer_map"),
            "sources_used_delta": expansion_result.get("sources_used_delta") or [],
        }
    return result

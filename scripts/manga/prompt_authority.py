#!/usr/bin/env python3
"""Shared research-backed prompt authority for live manga render lanes.

V3 (2026-07-10): consumes ``config/manga/genre_prompt_cookbook.yaml`` — the
manga-panel cookbook (distinct from ``genre_prompt_cookbook_v2.yaml`` for KDP
covers). Five-slot scaffold: REGISTER → SUBJECT → COMPOSITION → RENDERING →
LOCALE overlay. Qwen-primary for panel tasks; negatives only in the negative slot.
"""

from __future__ import annotations

from typing import Any

from phoenix_v4.manga.genre_tradition import (
    cookbook_entry,
    genre_tradition_tokens,
    resolve_canonical_genre,
    resolve_tradition_genre,
)

DEFAULT_PANEL_TASK = "t2i_qwen_image"


def task_to_base_model(task: str) -> str:
    """Map render task name to prompt-engine family.

    V3 default: Qwen-Image for all panel tasks unless explicitly flux/animagine.
    FLUX-schnell is never the silent default (research 2026-07-10).
    """
    low = str(task or "").strip().lower()
    if "qwen" in low:
        return "qwen_image"
    if "animagine" in low:
        return "animagine_xl_4_0"
    if "flux" in low or "schnell" in low:
        return "flux_schnell"
    return "qwen_image"


def resolve_panel_task(task: str | None = None, *, genre_id: str | None = None) -> str:
    """Return the canonical Procrastinate task for a manga panel/layer render."""
    if task and str(task).strip():
        return str(task).strip()
    entry = cookbook_entry(genre_id) if genre_id else None
    if entry:
        preferred = str(entry.get("preferred_model") or "").strip()
        if preferred == "flux_schnell":
            return "t2i_flux_schnell"
        if preferred.startswith("animagine"):
            return "t2i_flux_dev_h1a"  # animagine routed via h1a lane today
    return DEFAULT_PANEL_TASK


def _dedupe_chunks(chunks: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in chunks:
        text = str(raw or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _split_scaffold_positive(scaffold: str) -> dict[str, str]:
    """Best-effort split of cookbook positive_scaffold into REGISTER + RENDERING."""
    text = str(scaffold or "").strip()
    if not text:
        return {"REGISTER": "", "RENDERING": ""}
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) <= 3:
        return {"REGISTER": text, "RENDERING": ""}
    register = ", ".join(parts[:4])
    rendering = ", ".join(parts[4:])
    return {"REGISTER": register, "RENDERING": rendering}


def build_panel_prompt(
    *,
    genre_id: str | None,
    subject: str = "",
    composition: str = "",
    locale: str | None = None,
    market_demo: str | None = None,
    visual_grammar: str | None = None,
    extra_style: str = "",
    task: str = DEFAULT_PANEL_TASK,
    fail_closed: bool = False,
) -> tuple[str, str, dict[str, Any]]:
    """Build a five-slot manga panel prompt from cookbook + tradition authority."""
    canonical = resolve_tradition_genre(genre_id)
    base_model = task_to_base_model(task)
    entry = cookbook_entry(canonical) if canonical else None

    if canonical and not entry and fail_closed:
        raise ValueError(
            f"genre_prompt_cookbook missing or empty for canonical genre {canonical!r}"
        )

    pos_tradition, neg_tradition = genre_tradition_tokens(canonical, base_model=base_model)

    slots: dict[str, list[str]] = {
        "REGISTER": [],
        "SUBJECT": [],
        "COMPOSITION": [],
        "RENDERING": [],
        "LOCALE": [],
    }

    if entry:
        split = _split_scaffold_positive(str(entry.get("positive_scaffold") or ""))
        if split["REGISTER"]:
            slots["REGISTER"].append(split["REGISTER"])
        if split["RENDERING"]:
            slots["RENDERING"].append(split["RENDERING"])
        comp_rules = entry.get("composition_rules")
        if isinstance(comp_rules, str) and comp_rules.strip():
            slots["COMPOSITION"].append(comp_rules.strip())
        color_policy = entry.get("color_policy")
        if isinstance(color_policy, str) and color_policy.strip():
            slots["RENDERING"].append(color_policy.replace("_", " "))
    elif canonical and fail_closed:
        raise ValueError(f"fragmented genre authority for {canonical!r}")

    if market_demo:
        slots["REGISTER"].append(f"{market_demo} manga register")
    if visual_grammar:
        slots["RENDERING"].append(str(visual_grammar).replace("_", " "))
    if locale:
        from phoenix_v4.manga.genre_tradition import locale_overlay_tokens

        loc_add, loc_avoid = locale_overlay_tokens(locale)
        if loc_add:
            slots["LOCALE"].append(loc_add)
        for avoid in loc_avoid:
            slots["RENDERING"].append(f"avoid {avoid}")
    if subject:
        slots["SUBJECT"].append(subject.strip())
    if composition:
        slots["COMPOSITION"].append(composition.strip())
    slots["RENDERING"].extend(pos_tradition)
    if extra_style:
        slots["RENDERING"].append(extra_style.strip())

    positive_parts: list[str] = []
    for key in ("REGISTER", "SUBJECT", "COMPOSITION", "RENDERING", "LOCALE"):
        positive_parts.extend(slots[key])

    negative_parts: list[str] = []
    if entry:
        neg_scaffold = entry.get("negative_scaffold")
        if isinstance(neg_scaffold, str) and neg_scaffold.strip():
            negative_parts.append(neg_scaffold.strip())
    negative_parts.extend(neg_tradition)

    provenance: dict[str, Any] = {
        "genre_requested": genre_id,
        "genre_canonical": canonical,
        "base_model": base_model,
        "panel_task": resolve_panel_task(task, genre_id=canonical),
        "cookbook_applied": bool(entry),
        "tradition_tokens_applied": bool(pos_tradition or neg_tradition),
        "scaffold_slots": {k: v for k, v in slots.items() if v},
    }
    return (
        ", ".join(_dedupe_chunks(positive_parts)),
        ", ".join(_dedupe_chunks(negative_parts)),
        provenance,
    )


def build_authority_prompt_block(
    *,
    genre_id: str | None,
    task: str,
    market_demo: str | None = None,
    visual_grammar: str | None = None,
    extra_style: str = "",
    extra_negative: str = "",
    locale: str | None = None,
    subject: str = "",
    composition: str = "",
) -> tuple[str, str, dict[str, Any]]:
    """Compatibility wrapper used by enqueue/render lanes."""
    style, negative, provenance = build_panel_prompt(
        genre_id=genre_id,
        subject=subject,
        composition=composition,
        locale=locale,
        market_demo=market_demo,
        visual_grammar=visual_grammar,
        extra_style=extra_style,
        task=task or DEFAULT_PANEL_TASK,
        fail_closed=bool(genre_id),
    )
    if extra_negative:
        negative = ", ".join(_dedupe_chunks([negative, extra_negative]))
    return style, negative, provenance

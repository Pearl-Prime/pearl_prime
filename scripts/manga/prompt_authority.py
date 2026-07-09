#!/usr/bin/env python3
"""Shared research-backed prompt authority for live manga render lanes."""

from __future__ import annotations

from typing import Any

from phoenix_v4.manga.genre_tradition import (
    genre_tradition_tokens,
    resolve_canonical_genre,
    resolve_tradition_genre,
)


def task_to_base_model(task: str) -> str:
    low = str(task or "").strip().lower()
    if "qwen" in low:
        return "qwen_image"
    if "animagine" in low:
        return "animagine_xl_4_0"
    return "flux_schnell"


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


def build_authority_prompt_block(
    *,
    genre_id: str | None,
    task: str,
    market_demo: str | None = None,
    visual_grammar: str | None = None,
    extra_style: str = "",
    extra_negative: str = "",
) -> tuple[str, str, dict[str, Any]]:
    canonical = resolve_tradition_genre(genre_id)
    base_model = task_to_base_model(task)
    pos_tokens, neg_tokens = genre_tradition_tokens(canonical, base_model=base_model)

    positive_parts: list[str] = []
    if market_demo:
        positive_parts.append(f"{market_demo} manga register")
    if visual_grammar:
        positive_parts.append(str(visual_grammar).replace("_", " "))
    positive_parts.extend(pos_tokens)
    if extra_style:
        positive_parts.append(extra_style)

    negative_parts: list[str] = []
    negative_parts.extend(neg_tokens)
    if extra_negative:
        negative_parts.append(extra_negative)

    return (
        ", ".join(_dedupe_chunks(positive_parts)),
        ", ".join(_dedupe_chunks(negative_parts)),
        {
            "genre_requested": genre_id,
            "genre_canonical": canonical,
            "base_model": base_model,
            "tradition_tokens_applied": bool(pos_tokens or neg_tokens),
        },
    )

"""Locale-aware text resolver for lettering_spec v3.

PR #631 Decision 1: each dialogue_line carries text_by_locale dict so one
layered render can ship to multiple markets without re-rendering art.
This module is the single chokepoint that resolves "what text goes in
this bubble for this locale" at compose-time.

Backward-compatible with lettering_spec v2 — when text_by_locale is
absent, falls back to the v2 single-text field.

Usage:
    from phoenix_v4.manga.chapter.locale_resolver import resolve_dialogue_text

    text = resolve_dialogue_text(line, locale="ja_JP", default_locale="en_US")

Renderer integration (bubble_render.py and webtoon_compose.py call this
during composite, NOT during initial art render):

    for line in panel["dialogue_lines"]:
        text = resolve_dialogue_text(line, locale=publish_locale, default_locale=spec_default)
        if text is None:
            continue        # missing locale + no fallback = silent line
        font = resolve_font(line, locale=publish_locale, default_locale=spec_default)
        draw_bubble(panel, text, font, ...)

Cost rationale (PR #631):
    Re-rendering art per language: ~$N per series × 5 markets = ~$5N
    Re-compositing text only:       ~$N per series × 1 + tiny per-locale = ~$1.05N
    Saving: ~80% of cost across 5 markets, ~50–99× ROI on the v3 schema effort.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

VALID_LOCALES = ("en_US", "ja_JP", "ko_KR", "zh_TW", "zh_CN")


def resolve_dialogue_text(
    line: Mapping[str, Any],
    *,
    locale: str,
    default_locale: str = "en_US",
) -> str | None:
    """Return the dialogue text for the given locale.

    Resolution order:
        1. line["text_by_locale"][locale] (v3 explicit)
        2. line["text_by_locale"][default_locale] (v3 fallback)
        3. line["text"] (v2 backward-compat)
        4. None (line is silent for this locale)
    """
    by_locale = line.get("text_by_locale") or {}
    if locale in by_locale and by_locale[locale]:
        return by_locale[locale]
    if default_locale in by_locale and by_locale[default_locale]:
        return by_locale[default_locale]
    text = line.get("text")
    return text if text else None


def resolve_font_override(
    line: Mapping[str, Any],
    *,
    locale: str,
    default_locale: str = "en_US",
) -> str | None:
    """Return the font_override for the given locale, or None.

    CJK fonts may not render the same emphasis style as Latin fonts —
    e.g. ``all_caps_scream`` is meaningless for Japanese; v3 lets a
    series specify a per-locale override.
    """
    by_locale = line.get("font_override_by_locale") or {}
    if locale in by_locale:
        return by_locale[locale]
    if default_locale in by_locale:
        return by_locale[default_locale]
    return line.get("font_override")


def resolve_sfx(
    panel: Mapping[str, Any],
    *,
    locale: str,
    default_locale: str = "en_US",
) -> Sequence[str]:
    """Return the SFX list for this locale.

    Japanese onomatopoeia (e.g. ``ドキドキ``) often localize differently:
    keep as-is for ja_JP, transliterate for en_US, translate per series
    convention for zh_TW / zh_CN. v3 lets each market carry its own list.
    """
    by_locale = panel.get("sfx_by_locale") or {}
    if locale in by_locale:
        return list(by_locale[locale])
    if default_locale in by_locale:
        return list(by_locale[default_locale])
    return list(panel.get("sfx") or [])


def resolve_narrator_caption(
    panel: Mapping[str, Any],
    *,
    locale: str,
    default_locale: str = "en_US",
) -> str | None:
    """Return the narrator caption for this locale, or None."""
    by_locale = panel.get("narrator_caption_by_locale") or {}
    if locale in by_locale and by_locale[locale]:
        return by_locale[locale]
    if default_locale in by_locale and by_locale[default_locale]:
        return by_locale[default_locale]
    cap = panel.get("narrator_caption")
    return cap if cap else None


def coverage_check(
    panel: Mapping[str, Any],
    *,
    locale: str,
    default_locale: str = "en_US",
) -> float | None:
    """Return the estimated bubble coverage for this locale.

    Per PR #631 Decision 6 (Scroll Therapeutic Test), every panel should
    keep coverage under the cap defined per genre/format. CJK ↔ Latin
    text expansion can shift coverage 30–50%; v3 stores per-locale.
    """
    by_locale = panel.get("estimated_bubble_coverage_by_locale") or {}
    if locale in by_locale and by_locale[locale] is not None:
        return float(by_locale[locale])
    if default_locale in by_locale and by_locale[default_locale] is not None:
        return float(by_locale[default_locale])
    cov = panel.get("estimated_bubble_coverage")
    return float(cov) if cov is not None else None


def assert_locale_complete(
    spec: Mapping[str, Any],
    locale: str,
) -> list[str]:
    """Return a list of validation errors if `spec` is incomplete for `locale`.

    A spec is "complete for locale L" if every dialogue_line either:
      - has text_by_locale[L] populated, OR
      - has text_by_locale[default_locale] populated, OR
      - has v2 `text` field populated (backward-compat fallback)

    Useful as a pre-publish check: before shipping a chapter to LINE Manga
    Indies in ja_JP, run assert_locale_complete(spec, "ja_JP") and refuse
    publish if errors > 0.
    """
    if locale not in VALID_LOCALES:
        return [f"unknown locale: {locale}"]

    default_locale = spec.get("default_locale") or "en_US"
    errors: list[str] = []

    for panel in spec.get("lettering_panels") or []:
        panel_id = panel.get("panel_id", "?")
        for i, line in enumerate(panel.get("dialogue_lines") or []):
            text = resolve_dialogue_text(line, locale=locale, default_locale=default_locale)
            if not text:
                speaker = line.get("speaker", "?")
                errors.append(
                    f"panel {panel_id} line {i} ({speaker}): no text for {locale} "
                    f"(no text_by_locale[{locale}], no text_by_locale[{default_locale}], no v2 text fallback)"
                )
    return errors

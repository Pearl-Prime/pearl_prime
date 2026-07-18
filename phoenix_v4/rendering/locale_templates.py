"""Locale-aware pipeline template loader.

When locale is set (e.g. zh-TW), loads translated template strings from
config/localization/pipeline_templates_{locale_underscore}.yaml.
English strings are looked up and replaced with locale versions.
If no translation exists, the English original is returned unchanged.

Usage:
    from phoenix_v4.rendering.locale_templates import get_template
    text = get_template("The point is that...", locale="zh-TW")
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "config" / "localization"

_CACHE: dict[str, dict[str, str]] = {}


def _load_templates(locale: str) -> dict[str, str]:
    """Load template map for locale. Returns empty dict if no file exists."""
    if locale in _CACHE:
        return _CACHE[locale]

    locale_underscore = locale.replace("-", "_")
    path = CONFIG_DIR / f"pipeline_templates_{locale_underscore}.yaml"
    if not path.exists():
        _CACHE[locale] = {}
        return {}

    try:
        import yaml
    except ImportError:
        _CACHE[locale] = {}
        return {}

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    templates = data.get("templates") or {}
    _CACHE[locale] = templates
    logger.info("Loaded %d pipeline templates for locale %s", len(templates), locale)
    return templates


def get_template(english: str, locale: Optional[str] = None) -> str:
    """Return locale translation of english string, or english if not found."""
    if not locale or locale == "en-US":
        return english
    templates = _load_templates(locale)
    return templates.get(english, english)


def localize_rendered_text(text: str, locale: Optional[str] = None) -> str:
    """Replace all known English template strings in rendered text with locale versions.

    This is a post-processing pass applied after chapter_composer produces the
    English-template book. It replaces bridge sentences, transitions, and
    framing text with their locale equivalents from pipeline_templates_{locale}.yaml.
    """
    if not locale or locale == "en-US":
        return text
    templates = _load_templates(locale)
    if not templates:
        logger.warning("No pipeline templates for locale %s — book will contain English framing", locale)
        return text

    # Sort by length descending so longer strings are replaced first (avoid partial matches)
    sorted_pairs = sorted(templates.items(), key=lambda kv: len(kv[0]), reverse=True)
    for en, zh in sorted_pairs:
        if en in text:
            text = text.replace(en, zh)

    return text


def translate_fstring(template: str, locale: Optional[str] = None, **kwargs) -> str:
    """Translate an f-string template, then format with kwargs.

    Example:
        translate_fstring("The point is that {core}", locale="zh-TW", core="anxiety hurts")
    """
    translated = get_template(template, locale)
    try:
        return translated.format(**kwargs)
    except (KeyError, IndexError):
        return translated

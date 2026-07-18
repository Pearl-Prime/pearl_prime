"""
Lightweight funnel book URL index — fast lookup without loading sku_url_map.yaml.
Authority: artifacts/catalog/pearl_prime_book_script_catalogs/*_catalog.csv
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INDEX = REPO_ROOT / "config" / "marketing" / "funnel_book_url_index.json"

DEFAULT_TEACHER_PRIORITY = ("ahjan", "omote", "joshin")


def _locale_key(locale: str) -> str:
    return locale.replace("-", "_")


def _url_locale(locale: str) -> str:
    return locale.replace("_", "-")


def load_index(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_INDEX
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


DEFAULT_BRAND_PRIORITY = ("stillness_press", "body_memory", "cognitive_clarity", "warrior_calm")


def _pick_brand_entry(persona_entry: Any, brand_id: str | None) -> dict[str, Any] | None:
    if not isinstance(persona_entry, dict):
        return None
    # Legacy flat cell (pre brand-nesting)
    if "book_url" in persona_entry:
        if brand_id and persona_entry.get("brand_id") not in (None, brand_id):
            return None
        return persona_entry
    if brand_id and brand_id in persona_entry:
        row = persona_entry[brand_id]
        return row if isinstance(row, dict) else None
    for bid in DEFAULT_BRAND_PRIORITY:
        if bid in persona_entry and isinstance(persona_entry[bid], dict):
            return persona_entry[bid]
    for row in persona_entry.values():
        if isinstance(row, dict) and row.get("book_url"):
            return row
    return None


def resolve_book_url(
    topic_id: str,
    persona_id: str,
    *,
    locale: str = "en_US",
    product_type: str = "book",
    brand_id: str | None = None,
    index: dict[str, Any] | None = None,
) -> str | None:
    """Return pearlprime.shop URL for topic×persona, or None."""
    index = index or load_index()
    locales = index.get("locales") or {}
    loc = locales.get(_locale_key(locale)) or {}
    topic = loc.get(topic_id) or {}
    persona_entry = topic.get(persona_id)
    persona = _pick_brand_entry(persona_entry, brand_id)
    if not persona:
        return None
    if product_type == "audiobook":
        return persona.get("audiobook_url") or None
    return persona.get("book_url") or None


def resolve_series_shop_url(
    topic_id: str,
    persona_id: str,
    *,
    locale: str = "en_US",
    shop_base: str = "https://pearlprime.shop",
    brand_id: str | None = None,
    index: dict[str, Any] | None = None,
) -> str | None:
    """Series upsell: brand catalog root on shop."""
    index = index or load_index()
    locales = index.get("locales") or {}
    loc = locales.get(_locale_key(locale)) or {}
    topic = loc.get(topic_id) or {}
    persona = _pick_brand_entry(topic.get(persona_id), brand_id)
    if not isinstance(persona, dict):
        return f"{shop_base.rstrip('/')}/{_url_locale(locale)}/book/{brand_id or 'stillness_press'}"
    bid = brand_id or persona.get("brand_id") or "stillness_press"
    return f"{shop_base.rstrip('/')}/{_url_locale(locale)}/book/{bid}"

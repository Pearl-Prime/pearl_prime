from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
ASSIGNMENTS = REPO / "config" / "brand_management" / "brand_director_assignments.yaml"


def load_director_assignments() -> dict:
    """Load public-safe Brand Director assignments keyed by brand_id and base_brand."""
    if not ASSIGNMENTS.exists():
        return {"by_brand": {}, "by_base": {}}
    data = yaml.safe_load(ASSIGNMENTS.read_text(encoding="utf-8")) or {}
    raw = data.get("assignments") or {}
    by_brand: dict[str, dict] = {}
    by_base: dict[str, dict] = {}
    for key, rec in raw.items():
        if not isinstance(rec, dict):
            continue
        name = str(rec.get("brand_director_name") or "").strip()
        director_id = str(rec.get("brand_director_id") or "").strip()
        if not (name and director_id):
            continue
        norm = {
            "brand_director_name": name,
            "brand_director_id": director_id,
            "brand_director_status": str(rec.get("status") or "assigned").strip(),
        }
        if rec.get("display_brand"):
            norm["display_brand"] = str(rec["display_brand"]).strip()
        brand_id = str(rec.get("brand_id") or key).strip()
        base = str(rec.get("base_brand") or "").strip()
        if brand_id:
            by_brand[brand_id] = norm
        if base:
            by_base[base] = norm
    return {"by_brand": by_brand, "by_base": by_base}


def director_for(
    *,
    brand_id: str | None = None,
    base_brand: str | None = None,
    assignments: dict | None = None,
    allow_base: bool = False,
) -> dict:
    """Return explicit Brand Director fields without touching teacher identity."""
    data = assignments if assignments is not None else load_director_assignments()
    if brand_id:
        rec = (data.get("by_brand") or {}).get(brand_id)
        if rec:
            return dict(rec)
    if allow_base and base_brand:
        rec = (data.get("by_base") or {}).get(base_brand)
        if rec:
            return dict(rec)
    return {}

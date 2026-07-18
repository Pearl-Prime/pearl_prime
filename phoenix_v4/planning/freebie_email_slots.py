"""
Email slot + archetype metadata for freebie bundles.
Authority: config/freebies/archetype_assignments.yaml, nurture_asset_mix.yaml
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = REPO_ROOT / "config" / "freebies"


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}


def email_slot_for_type(freebie_type: str, assignments: Optional[dict] = None) -> str:
    assignments = assignments or _load_yaml(CONFIG / "archetype_assignments.yaml")
    mapping = assignments.get("email_slot_by_type") or {}
    return str(mapping.get(freebie_type) or "")


def enrich_bundle_with_slots(
    bundle_with_formats: list[dict[str, Any]],
    freebies_map: dict[str, Any],
    buyer: bool = False,
) -> list[dict[str, Any]]:
    """Add email_slot and requires_buyer_tag to each bundle row."""
    mix = _load_yaml(CONFIG / "nurture_asset_mix.yaml")
    forbidden = set(mix.get("pre_purchase", {}).get("forbidden_pre_purchase_types") or [])
    out: list[dict[str, Any]] = []
    for row in bundle_with_formats:
        fid = row.get("freebie_id") or ""
        fb = freebies_map.get(fid) or {}
        ftype = str(fb.get("type") or "")
        slot = email_slot_for_type(ftype)
        requires_buyer = ftype in forbidden and not buyer
        enriched = dict(row)
        if slot:
            enriched["email_slot"] = slot
        enriched["freebie_type"] = ftype
        enriched["requires_buyer_tag"] = requires_buyer
        out.append(enriched)
    return out

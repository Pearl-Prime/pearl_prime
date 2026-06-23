"""
Resolve GHL feed metadata: funnel_variant, email_slot, content_type.
Authority: config/marketing/ghl_*.yaml, config/freebies/archetype_assignments.yaml
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_MARKETING = REPO_ROOT / "config" / "marketing"
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"

FREEBIE_TYPE_TO_CONTENT_TYPE: dict[str, str] = {
    "interactive_html_tool": "somatic_exercise",
    "assessment_html": "assessment_html",
    "downloadable_workbook": "assessment_html",
    "guided_audio": "guided_audio",
    "checklist_pdf": "checklist_pdf",
    "companion_workbook_pdf": "companion_workbook_pdf",
}

LEGACY_VARIANT_MAP = {"A": "tight", "B": "welcome_depth"}


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def normalize_funnel_variant(value: str | None, default: str = "tight") -> str:
    if not value:
        return default
    v = str(value).strip()
    if v in LEGACY_VARIANT_MAP:
        return LEGACY_VARIANT_MAP[v]
    if v in ("tight", "welcome_depth"):
        return v
    return default


def resolve_persona_id(persona_id: str | None, persona_map: dict[str, Any]) -> str:
    if not persona_id:
        return "corporate_managers"
    aliases = persona_map.get("persona_aliases") or {}
    return str(aliases.get(persona_id) or persona_id)


def resolve_funnel_variant(
    topic_id: str,
    persona_id: str | None = None,
    archetype_row: dict[str, Any] | None = None,
    persona_map: dict[str, Any] | None = None,
) -> str:
    persona_map = persona_map or _load_yaml(CONFIG_MARKETING / "ghl_persona_variant_map.yaml")
    default = normalize_funnel_variant(persona_map.get("default_variant"), "tight")
    persona_id = resolve_persona_id(persona_id, persona_map)

    topic_variants = persona_map.get("topic_variants") or {}
    if topic_id in topic_variants:
        return normalize_funnel_variant(topic_variants[topic_id], default)

    persona_variants = persona_map.get("persona_variants") or {}
    if persona_id in persona_variants:
        return normalize_funnel_variant(persona_variants[persona_id], default)

    if archetype_row and archetype_row.get("funnel_variant"):
        return normalize_funnel_variant(str(archetype_row["funnel_variant"]), default)

    return default


def resolve_email_slot(
    content_type: str,
    pricing: str = "free",
    explicit_slot: str | None = None,
    slot_rules: dict[str, Any] | None = None,
) -> str:
    if explicit_slot:
        return explicit_slot
    slot_rules = slot_rules or _load_yaml(CONFIG_MARKETING / "ghl_email_slot_rules.yaml")
    defaults = slot_rules.get("defaults_by_content_type") or {}
    slot = str(defaults.get(content_type) or "")
    if content_type == "book_offer" and pricing != "paid":
        return "e4"
    return slot


def content_type_for_freebie(freebie_type: str) -> str:
    return FREEBIE_TYPE_TO_CONTENT_TYPE.get(freebie_type, "somatic_exercise")


def validate_slot_rules(item: dict[str, Any], slot_rules: dict[str, Any] | None = None) -> list[str]:
    """Return validation errors for a feed item against ghl_email_slot_rules."""
    slot_rules = slot_rules or _load_yaml(CONFIG_MARKETING / "ghl_email_slot_rules.yaml")
    errors: list[str] = []
    content_type = str(item.get("content_type") or "")
    email_slot = str(item.get("email_slot") or "")
    pricing = str(item.get("pricing") or "")

    if content_type == "guided_audio" and email_slot in ("e1", "e2"):
        errors.append(f"guided_audio must not use email_slot {email_slot}")
    if content_type == "book_offer" and pricing != "paid":
        errors.append("book_offer requires pricing: paid")
    return errors


def archetype_for_topic(topic_id: str, assignments: Optional[dict] = None) -> dict[str, Any]:
    assignments = assignments or _load_yaml(CONFIG_FREEBIES / "archetype_assignments.yaml")
    topics = assignments.get("topics") or {}
    row = topics.get(topic_id) or {}
    return {
        "primary_archetype_id": str(row.get("primary_archetype_id") or ""),
        "e2_archetype_id": str(row.get("e2_archetype_id") or ""),
        "e2_somatic_app": str(row.get("e2_somatic_app") or ""),
        "funnel_slug": str(row.get("funnel_slug") or ""),
    }

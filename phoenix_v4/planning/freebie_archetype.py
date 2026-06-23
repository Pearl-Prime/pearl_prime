"""
Resolve funnel archetype + E2 somatic app from topic assignments.
Authority: config/freebies/archetype_assignments.yaml
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


def resolve_archetype_for_topic(
    topic_id: str,
    assignments: Optional[dict] = None,
    persona_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Return primary_archetype_id, e2_somatic_app, funnel_slug, funnel_variant for a topic.
    funnel_variant is canonical tight | welcome_depth (GHL WF1 branch).
    """
    from phoenix_v4.marketing.feed_metadata import resolve_funnel_variant

    assignments = assignments or _load_yaml(CONFIG / "archetype_assignments.yaml")
    topics = assignments.get("topics") or {}
    row = topics.get(topic_id) or {}
    variant = resolve_funnel_variant(topic_id, persona_id, row)
    return {
        "topic_id": topic_id,
        "primary_archetype_id": row.get("primary_archetype_id") or "",
        "e2_archetype_id": row.get("e2_archetype_id") or "",
        "e2_somatic_app": row.get("e2_somatic_app") or "",
        "funnel_slug": row.get("funnel_slug") or "",
        "funnel_variant": variant,
    }

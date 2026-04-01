"""
Experience Resolver — resolves 7-field experience tuple from planning keys.

Authority: specs/EXPERIENCE_LAYER_ANTI_SPAM_SPEC.md §3, §4.
Config: config/experience/experience_defaults.yaml

Resolution priority:
  1. Explicit override in plan/BookSpec (highest)
  2. Defaults from config (engine → delivery, topic → intent, arc → pacing)
  3. Hardcoded fallback

Output: dict with 7 fields + experience_hash (sha256 of sorted tuple).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "experience" / "experience_defaults.yaml"

EXPERIENCE_FIELDS = (
    "delivery_experience",
    "reader_intent",
    "pacing_model",
    "outcome_type",
    "engagement_depth",
    "transformation_speed",
    "perceived_positioning",
)

# Hardcoded fallback (matches config/experience/experience_defaults.yaml fallback section)
_FALLBACK = {
    "delivery_experience": "passive_reading",
    "reader_intent": "understand_self",
    "pacing_model": "single_sitting",
    "outcome_type": "cognitive_clarity",
    "engagement_depth": "moderate",
    "transformation_speed": "gradual",
    "perceived_positioning": "reflective_insight",
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise ImportError("PyYAML required for experience resolver")
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def compute_experience_hash(exp: Dict[str, str]) -> str:
    """SHA-256 of sorted 7-field tuple for O(1) dedup."""
    canonical = json.dumps(
        {k: exp.get(k, "") for k in sorted(EXPERIENCE_FIELDS)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _arc_size_bucket(chapter_count: int, thresholds: Dict[str, int]) -> str:
    short_max = thresholds.get("short_max", 5)
    medium_max = thresholds.get("medium_max", 10)
    if chapter_count <= short_max:
        return "short"
    elif chapter_count <= medium_max:
        return "medium"
    return "long"


def resolve_experience(
    plan: Dict[str, Any],
    *,
    config_path: Optional[Path] = None,
) -> Dict[str, str]:
    """
    Resolve experience dimensions for a compiled plan or BookSpec.

    Args:
        plan: dict with keys like engine_id, topic_id, arc_id, chapter_count,
              format_id, and optional explicit experience overrides.
        config_path: path to experience_defaults.yaml (defaults to repo config).

    Returns:
        dict with all 7 experience fields + experience_hash.
    """
    cfg_path = config_path or CONFIG_PATH
    raw = _load_yaml(cfg_path)
    defaults_cfg = raw.get("experience_defaults", {})

    by_engine = defaults_cfg.get("by_engine", {})
    by_topic = defaults_cfg.get("by_topic", {})
    by_arc = defaults_cfg.get("by_arc_chapter_count", {})
    arc_thresholds = defaults_cfg.get("arc_chapter_thresholds", {})
    fallback = defaults_cfg.get("fallback", _FALLBACK)

    result: Dict[str, str] = {}

    # --- Layer 1: Engine defaults ---
    engine_id = str(plan.get("engine_id") or "").strip()
    engine_defaults = by_engine.get(engine_id, {})
    for field in ("delivery_experience", "engagement_depth"):
        if field in engine_defaults:
            result[field] = engine_defaults[field]

    # --- Layer 2: Topic defaults ---
    topic_id = str(plan.get("topic_id") or "").strip()
    topic_defaults = by_topic.get(topic_id, {})
    for field in ("reader_intent", "outcome_type", "perceived_positioning"):
        if field in topic_defaults:
            result[field] = topic_defaults[field]

    # --- Layer 3: Arc length defaults ---
    chapter_count = plan.get("chapter_count") or 0
    if not chapter_count:
        # Try to infer from chapters list or chapter_slot_sequence (compiled plans)
        chapters = plan.get("chapters") or plan.get("chapter_slot_sequence") or []
        chapter_count = len(chapters) if isinstance(chapters, list) else 0

    if chapter_count > 0:
        bucket = _arc_size_bucket(chapter_count, arc_thresholds)
        arc_defaults = by_arc.get(bucket, {})
        for field in ("pacing_model", "transformation_speed"):
            if field in arc_defaults:
                result[field] = arc_defaults[field]

    # --- Layer 4: Fill remaining from fallback ---
    for field in EXPERIENCE_FIELDS:
        if field not in result:
            result[field] = fallback.get(field, _FALLBACK[field])

    # --- Layer 5: Explicit overrides from plan (highest priority) ---
    for field in EXPERIENCE_FIELDS:
        explicit_val = plan.get(field)
        if explicit_val and str(explicit_val).strip():
            result[field] = str(explicit_val).strip()

    # --- Compute hash ---
    result["experience_hash"] = compute_experience_hash(result)

    return result


def resolve_and_attach(plan: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
    """Resolve experience and merge into plan dict (non-destructive: won't overwrite existing)."""
    exp = resolve_experience(plan, **kwargs)
    for field in EXPERIENCE_FIELDS:
        if field not in plan or not plan[field]:
            plan[field] = exp[field]
    if "experience_hash" not in plan or not plan["experience_hash"]:
        plan["experience_hash"] = exp["experience_hash"]
    return plan


# --- AI Disclosure default ---
def ensure_ai_disclosure(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Set ai_disclosure_status to 'disclosed' if not present (pipeline-generated books)."""
    if not plan.get("ai_disclosure_status"):
        plan["ai_disclosure_status"] = "disclosed"
    return plan

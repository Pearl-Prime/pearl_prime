"""
EI V2 config loader.

Loads from config/quality/ei_v2_config.yaml with sensible defaults.
All modules are disabled by default — enable via config to opt in.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

from phoenix_v4.quality.ei_v2.ei_warnings import log_ei_warning

_EI_V2_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _EI_V2_ROOT.parent.parent.parent

_CONFIG_PATH = _REPO_ROOT / "config" / "quality" / "ei_v2_config.yaml"


def ei_v2_repo_root() -> Path:
    """Return repo root for EI V2 artifact paths (avoids CWD brittleness)."""
    return _REPO_ROOT
_CACHE: Dict[str, Any] | None = None

DEFAULTS: Dict[str, Any] = {
    "marketing_sources": {
        "enabled": False,
        "source_path": "marketing_deep_research",
        "use_marketing_lexicons": True,
        "use_marketing_safety_bans": True,
        "use_invisible_script_alignment": False,
    },
    "safety_classifier": {
        "enabled": True,
        "mode": "heuristic_plus",
        "medical_claim_threshold": 0.6,
        "promotional_threshold": 0.5,
        "clinical_language_threshold": 0.5,
        "marketing_compliance_weight": 0.2,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/safety_cache.jsonl",
    },
    "cross_encoder": {
        "enabled": True,
        "mode": "heuristic",
        "model": None,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/rerank_cache.db",
        "top_n": 5,
    },
    "domain_embeddings": {
        "enabled": True,
        "mode": "weighted",
        "persona_weight": 0.3,
        "topic_weight": 0.3,
        "thesis_weight": 0.4,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/domain_embed_cache.db",
    },
    "tts_readability": {
        "enabled": True,
        "max_sentence_words": 35,
        "ideal_sentence_range": [8, 25],
        "min_paragraph_breaks_per_500_words": 3,
        "rhythm_variance_min": 0.15,
        "problematic_tts_patterns": [
            r"\b\w{15,}\b",
            r"\([^)]{50,}\)",
            r";\s*\w+;\s*\w+;",
        ],
    },
    "semantic_dedup": {
        "enabled": True,
        "mode": "ngram_plus_embedding",
        "ngram_n": 6,
        "ngram_overlap_threshold": 0.30,
        "semantic_similarity_threshold": 0.85,
        "cache_enabled": True,
        "cache_path": "artifacts/ei_v2/dedup_cache.db",
    },
    "emotion_arc": {
        "enabled": True,
        "mode": "lexicon",
        "valence_lexicon_size": "medium",
        "arc_deviation_warn": 0.3,
        "arc_deviation_fail": 0.6,
    },
    "composite_weights": {
        "rerank": 0.30,
        "safety": 0.20,
        "domain_similarity": 0.15,
        "tts_readability": 0.15,
        "duration_fit": 0.20,
    },
    "duration_fit": {
        "enabled": True,
        "mode": "rule_based",
        "neutral_when_unscored": 0.62,
        "weights": {
            "therapeutic_fit": 0.40,
            "platform_fit": 0.35,
            "attention_fit": 0.25,
        },
        "thresholds": {"pass": 0.60, "warn": 0.45, "fail": 0.44},
    },
    # Book structure (Pearl Prime): slot types and arc context for EI learning and assembly.
    # When plan has chapter_thesis, callers pass chapter thesis per chapter; arc_intent may include
    # chapter_thesis, bestseller_structure. Known slot types include structural slots beyond core 6.
    "book_structure": {
        "known_slot_types": [
            "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION", "COMPRESSION",
            "PIVOT", "TAKEAWAY", "PERMISSION", "THREAD",
        ],
        "thesis_from_arc": True,   # When True, thesis is chapter-level from arc chapter_thesis when present
        "arc_intent_keys": ["band", "emotional_role", "chapter_index", "chapter_thesis", "bestseller_structure"],
        # BG-PR-09: when True, compile fails if chapter_slot_sequence disagrees with chapter_bestseller_structures
        "enforce_bestseller_beat_order": False,
    },
    "visual_therapeutic": {
        "enabled": False,
        "mode": "heuristic",
        "dimensions": {
            "vt_parasympathetic": {"weight": 0.30, "warn_below": 0.40, "fail_below": 0.20, "target_threshold": 0.60},
            "vt_processing": {"weight": 0.25, "warn_below": 0.35, "fail_below": 0.15, "target_threshold": 0.60},
            "vt_somatic": {"weight": 0.25, "warn_below": 0.35, "fail_below": 0.15, "target_threshold": 0.60},
            "vt_stealth": {
                "weight": 0.20,
                "warn_below": 0.70,
                "fail_below": 0.50,
                "target_threshold": 0.60,
                "blocker_threshold": 0.50,
                "penalty_weight": 100,
                "forbidden_terms": [],
            },
        },
        "composite": {"pass_threshold": 0.50, "target": 0.70},
    },
}


def load_ei_v2_config(
    path: Path | None = None,
    force_reload: bool = False,
) -> Dict[str, Any]:
    """Load V2 config, merging file values over defaults."""
    global _CACHE
    if _CACHE is not None and path is None and not force_reload:
        return _CACHE

    cfg = _deep_copy_dict(DEFAULTS)
    config_path = path or _CONFIG_PATH
    if config_path.exists() and yaml is not None:
        try:
            file_cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            cfg = _deep_merge(cfg, file_cfg)
        except Exception as e:
            log_ei_warning("config", f"YAML parse failed: {e}", {"path": str(config_path)})

    if path is None:
        _CACHE = cfg
    return cfg


def invalidate_ei_v2_config_cache() -> None:
    """Clear the config cache. Use for long-lived processes that need fresh config."""
    global _CACHE
    _CACHE = None


def _deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = _deep_copy_dict(v)
        elif isinstance(v, list):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = _deep_copy_dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result

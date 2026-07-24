"""Book Engine Policy V1 — load and resolve config/publishing/book_engine_policy_v1.yaml.

Wiring surface for BOOK_ENGINE_POLICY_V1_SPEC.md. Selector/gate callers read policy at
build time; this module does not change atom inventory or composer register.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "config" / "publishing" / "book_engine_policy_v1.yaml"

# Exercise-wrapper phrases cleared on the corporate-burnout reader-layer render.
# Hard-gate: count must stay 0 when policy hard_gate_cleared_scaffolds is enabled.
CLEARED_EXERCISE_WRAPPER_PHRASES: Tuple[str, ...] = (
    "if anything feels sharp",
    "that shift matters",
    "now we are going to shift",
    "the order matters",
)

# High-level chapter scaffold phrases (mirrors scripts/qa/check_book_engine_repetition.py).
VISIBLE_SCAFFOLD_PHRASES: Tuple[str, ...] = (
    "what i want to name here",
    "here is the deeper point",
    "that is where we go next",
    "where we go next",
    "in this chapter you will learn",
    "i want to give you",
    "i want to offer you",
    "you do not need to believe",
)


class BookEnginePolicyError(ValueError):
    """Raised when the policy file is missing required V1 fields."""


def default_policy_path(repo_root: Optional[Path] = None) -> Path:
    root = repo_root or REPO_ROOT
    return root / "config" / "publishing" / "book_engine_policy_v1.yaml"


@lru_cache(maxsize=4)
def _load_policy_cached(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    if not path.is_file():
        raise BookEnginePolicyError(f"book engine policy missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise BookEnginePolicyError("book engine policy root must be a mapping")
    validate_policy_schema(data)
    return data


def load_book_engine_policy(
    path: Optional[Path] = None,
    *,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load and schema-check the V1 policy object (cached by resolved path)."""
    resolved = Path(path) if path else default_policy_path(repo_root)
    return dict(_load_policy_cached(str(resolved.resolve())))


def validate_policy_schema(policy: Mapping[str, Any]) -> None:
    if int(policy.get("schema_version") or 0) != 1:
        raise BookEnginePolicyError("schema_version must be 1")
    if not policy.get("global_rules"):
        raise BookEnginePolicyError("global_rules required")
    smoke = policy.get("smoke_cell") or {}
    if not isinstance(smoke, dict) or not smoke.get("book_id"):
        raise BookEnginePolicyError("smoke_cell.book_id required")
    chapter_policy = smoke.get("chapter_policy") or {}
    if not isinstance(chapter_policy, dict) or not chapter_policy:
        raise BookEnginePolicyError("smoke_cell.chapter_policy required")
    for ch_key, ch in chapter_policy.items():
        if not isinstance(ch, dict):
            raise BookEnginePolicyError(f"chapter_policy.{ch_key} must be a mapping")
        for req in ("variation_mode", "entry_contract", "exit_contract"):
            if not str(ch.get(req) or "").strip():
                raise BookEnginePolicyError(f"chapter_policy.{ch_key}.{req} required")
        proof = str(ch.get("proof_class") or "").strip()
        if proof == "author_disclosure":
            raise BookEnginePolicyError(
                f"chapter_policy.{ch_key}: author_disclosure requires "
                "proof_class=real_author_source_required"
            )


def smoke_cell_persona_topic(policy: Mapping[str, Any]) -> Tuple[str, str]:
    book_id = str((policy.get("smoke_cell") or {}).get("book_id") or "")
    parts = book_id.split("__")
    if len(parts) < 2:
        return "", ""
    return parts[0].strip(), parts[1].strip()


def policy_applies_to(
    policy: Mapping[str, Any],
    *,
    persona_id: str = "",
    topic_id: str = "",
) -> bool:
    """True when the build cell matches the smoke cell (or an explicit dry-run cell)."""
    persona = (persona_id or "").strip()
    topic = (topic_id or "").strip()
    if not persona or not topic:
        return False
    smoke_persona, smoke_topic = smoke_cell_persona_topic(policy)
    if persona == smoke_persona and topic == smoke_topic:
        return True
    for cell in policy.get("dry_run_cells") or []:
        if not isinstance(cell, dict):
            continue
        if cell.get("proof_mode") == "metadata_only":
            continue
        if str(cell.get("persona") or "").strip() == persona and str(
            cell.get("topic") or ""
        ).strip() == topic:
            return True
    return False


def chapter_policy_key(chapter_number: int) -> str:
    return f"ch{int(chapter_number):02d}"


def resolve_chapter_policy(
    policy: Mapping[str, Any],
    chapter_number: int,
) -> Optional[Dict[str, Any]]:
    chapter_policy = (policy.get("smoke_cell") or {}).get("chapter_policy") or {}
    raw = chapter_policy.get(chapter_policy_key(chapter_number))
    return dict(raw) if isinstance(raw, dict) else None


def repetition_thresholds(policy: Mapping[str, Any]) -> Dict[str, int]:
    global_rules = policy.get("global_rules") or {}
    reuse = global_rules.get("maximum_visible_phrase_reuse") or {}
    validator = policy.get("validator_profile") or {}
    thresholds = validator.get("thresholds") or {}
    return {
        "exact_phrase": int(
            thresholds.get("exact_phrase")
            or reuse.get("exact_phrase_default")
            or 3
        ),
        "scaffold_phrase": int(
            thresholds.get("scaffold_phrase")
            or reuse.get("scaffold_phrase_default")
            or 2
        ),
        "five_gram": int(
            thresholds.get("five_gram") or reuse.get("five_gram_default") or 4
        ),
    }


def validator_profile(policy: Mapping[str, Any]) -> Dict[str, Any]:
    profile = dict(policy.get("validator_profile") or {})
    profile.setdefault("enabled_gates", ["visible_repetition"])
    profile.setdefault("hard_gate_repetition", False)
    profile.setdefault("hard_gate_cleared_scaffolds", True)
    return profile


def build_selector_policy_context(
    policy: Mapping[str, Any],
    *,
    persona_id: str,
    topic_id: str,
    chapter_numbers: Optional[list[int]] = None,
) -> Dict[str, Any]:
    """Audit/spine metadata attached by enrichment_select / accent_planner."""
    applies = policy_applies_to(policy, persona_id=persona_id, topic_id=topic_id)
    smoke = policy.get("smoke_cell") or {}
    chapters: Dict[str, Any] = {}
    variation_modes: list[str] = []
    for n in chapter_numbers or []:
        ch = resolve_chapter_policy(policy, n)
        if ch:
            key = chapter_policy_key(n)
            chapters[key] = ch
            mode = str(ch.get("variation_mode") or "").strip()
            if mode:
                variation_modes.append(mode)
    adjacent_same_mode = [
        i + 1
        for i in range(len(variation_modes) - 1)
        if variation_modes[i] and variation_modes[i] == variation_modes[i + 1]
    ]
    return {
        "policy_id": str(policy.get("policy_id") or "book_engine_policy_v1"),
        "schema_version": int(policy.get("schema_version") or 1),
        "status": str(policy.get("status") or ""),
        "applies": applies,
        "smoke_book_id": str(smoke.get("book_id") or ""),
        "motif_ledger": dict(smoke.get("motif_ledger") or {}) if applies else {},
        "tool_ledger": list(smoke.get("tool_ledger") or []) if applies else [],
        "chapter_policies": chapters if applies else {},
        "adjacent_same_variation_mode_chapters": adjacent_same_mode if applies else [],
        "troubleshooting_permission_split": dict(
            (policy.get("global_rules") or {}).get("troubleshooting_permission_split")
            or {}
        ),
        "repetition_thresholds": repetition_thresholds(policy),
        "validator_profile": validator_profile(policy),
    }


def clear_policy_cache() -> None:
    _load_policy_cached.cache_clear()

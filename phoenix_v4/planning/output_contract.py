"""
Output contract metadata (Hardening Spec 5G).

Captures the full truth of what the user requested vs what the pipeline
actually resolved and produced. Written into plan.json under the key
``output_contract`` and persisted as a standalone ``output_contract.json``
alongside rendered artifacts.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ALIASES_PATH = REPO_ROOT / "config" / "identity_aliases.yaml"
FORMAT_REGISTRY_PATH = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"


class TopicIdentityError(Exception):
    """Raised when strict_identity mode detects silent topic alias collapse.

    Hardening Spec §5A: if user requests topic X and system would silently
    collapse it to canonical topic Y, strict mode rejects instead of allowing
    silent drift.
    """


def _load_yaml(path: Path) -> dict:
    if not path.exists() or not yaml:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _resolve_topic_alias(requested_topic: str, *, aliases_path: Path = ALIASES_PATH) -> str:
    """Return the canonical topic after alias lookup (before direct-support override)."""
    data = _load_yaml(aliases_path)
    topic_aliases = data.get("topic_aliases") or {}
    return topic_aliases.get(requested_topic, requested_topic)


def _word_count_target(runtime_format: str | None, *, registry_path: Path = FORMAT_REGISTRY_PATH) -> dict[str, int]:
    """Return {min, max} word-count target for the given runtime format."""
    if not runtime_format:
        return {"min": 0, "max": 0}
    data = _load_yaml(registry_path)
    runtimes = data.get("runtime_formats") or data.get("runtimes") or {}
    entry = runtimes.get(runtime_format) or {}
    word_range = entry.get("word_range") or entry.get("word_count_range")
    if isinstance(word_range, (list, tuple)) and len(word_range) >= 2:
        return {"min": int(word_range[0]), "max": int(word_range[1])}
    return {"min": 0, "max": 0}


def build_output_contract(
    args: Any,
    resolved_config: dict[str, Any],
    *,
    aliases_path: Path = ALIASES_PATH,
    registry_path: Path = FORMAT_REGISTRY_PATH,
    strict_identity: bool = False,
) -> dict[str, Any]:
    """Build an output contract dict capturing requested-vs-resolved state.

    Parameters
    ----------
    args
        The parsed CLI ``argparse.Namespace`` (or any object with the same
        attribute names).
    resolved_config
        A dict carrying at least ``canonical_topic_id``,
        ``canonical_persona_id``, ``resolved_location_id``, and optionally
        ``teacher_mode``, ``teacher_id``, ``quality_profile``,
        ``runtime_format``, ``structural_format``.

    Returns
    -------
    dict
        JSON-serializable output contract.
    """
    requested_topic = getattr(args, "topic", None) or ""
    canonical_topic = resolved_config.get("canonical_topic_id") or requested_topic
    alias_target = _resolve_topic_alias(requested_topic, aliases_path=aliases_path)
    topic_aliased = bool(requested_topic and alias_target != requested_topic)

    if strict_identity and topic_aliased:
        raise TopicIdentityError(
            f"Strict identity mode: requested topic '{requested_topic}' would be "
            f"silently aliased to '{alias_target}'. Either resolve via governed "
            f"'{requested_topic}' path or fail before compile."
        )

    requested_location = getattr(args, "location", None) or ""
    resolved_location = resolved_config.get("resolved_location_id") or requested_location or ""
    location_fallback = bool(
        requested_location and resolved_location and requested_location != resolved_location
    ) or bool(not requested_location and resolved_location)

    runtime_format = (
        getattr(args, "runtime_format", None)
        or resolved_config.get("runtime_format")
        or resolved_config.get("runtime_format_id")
        or ""
    )
    structural_format = (
        getattr(args, "structural_format", None)
        or resolved_config.get("structural_format")
        or resolved_config.get("format_id")
        or ""
    )

    teacher_mode = bool(resolved_config.get("teacher_mode"))
    teacher_id = resolved_config.get("teacher_id") or getattr(args, "teacher", None) or None

    quality_profile = resolved_config.get("quality_profile") or "production"

    wc_target = _word_count_target(runtime_format, registry_path=registry_path)

    return {
        "requested_topic_id": requested_topic,
        "canonical_topic_id": canonical_topic,
        "topic_aliased": topic_aliased,
        "requested_location_id": requested_location,
        "resolved_location_id": resolved_location,
        "location_fallback": location_fallback,
        "teacher_mode": teacher_mode,
        "teacher_id": teacher_id,
        "quality_profile": quality_profile,
        "runtime_format": runtime_format,
        "structural_format": structural_format,
        "runtime_request": runtime_format,
        "runtime_achieved": "",
        "word_count_target": wc_target,
        "word_count_achieved": 0,
        "budget_check_result": "skipped",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def update_contract_post_render(
    contract: dict[str, Any],
    *,
    runtime_achieved: str = "",
    word_count_achieved: int = 0,
    budget_check_result: str = "skipped",
) -> dict[str, Any]:
    """Return a *new* contract dict with post-render fields filled in."""
    updated = dict(contract)
    updated["runtime_achieved"] = runtime_achieved or contract.get("runtime_format", "")
    updated["word_count_achieved"] = word_count_achieved
    if budget_check_result != "skipped":
        updated["budget_check_result"] = budget_check_result
    else:
        target = contract.get("word_count_target") or {}
        wmin = target.get("min", 0)
        wmax = target.get("max", 0)
        if wmin and wmax and word_count_achieved:
            updated["budget_check_result"] = (
                "pass" if wmin <= word_count_achieved <= wmax else "fail"
            )
        else:
            updated["budget_check_result"] = "skipped"
    return updated

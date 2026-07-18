"""Shared loader for config/publishing/ai_policy_blockers.yaml.

Used by all uploader/submitter scripts to consult AI policy before targeting
a platform. Provides a single point that returns:
  - status (ALLOWED / ALLOWED_GREY / BLOCKED / PARTNER_ONLY / UNKNOWN)
  - disclosure_required (bool)
  - rationale (for failure messages)

Usage:
    from scripts.publish._policy_loader import get_platform_policy, PolicyError

    pol = get_platform_policy("amazon_kdp_comics")
    if pol["status"] in ("BLOCKED", "PARTNER_ONLY", "UNKNOWN"):
        raise PolicyError(f"Cannot target {pol['name']}: {pol['rationale']}")
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / "config" / "publishing" / "ai_policy_blockers.yaml"


class PolicyError(Exception):
    """Raised when a target platform is BLOCKED, PARTNER_ONLY, or UNKNOWN."""


def _load_policy() -> dict[str, Any]:
    import yaml  # local import — only needed when consulted

    if not POLICY_PATH.exists():
        raise PolicyError(f"Policy file missing: {POLICY_PATH}")
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}


def get_platform_policy(platform_id: str) -> dict[str, Any]:
    """Return the policy entry for a platform_id.

    Raises PolicyError if the platform is unknown to the policy file.
    Always returns a dict with at least: name, status, region, disclosure_required, rationale.
    """
    policy = _load_policy()
    platforms = policy.get("platforms") or {}
    spec = platforms.get(platform_id)
    if spec is None:
        raise PolicyError(
            f"Platform {platform_id!r} not in {POLICY_PATH.relative_to(REPO)}. "
            f"Add an entry before targeting."
        )
    return {
        "name": platform_id,
        "status": spec.get("status", "UNKNOWN"),
        "region": spec.get("region", ""),
        "disclosure_required": bool(spec.get("disclosure_required", False)),
        "rationale": (spec.get("rationale") or "").strip(),
        "if_targeted": (spec.get("if_targeted") or "").strip(),
        "source": (spec.get("source") or "").strip(),
    }


def assert_target_allowed(platform_id: str) -> dict[str, Any]:
    """Raise PolicyError if the platform is not ALLOWED or ALLOWED_GREY.

    Returns the policy dict on success, for downstream use (e.g. disclosure logic).
    """
    pol = get_platform_policy(platform_id)
    status = pol["status"]
    if status in ("ALLOWED", "ALLOWED_GREY"):
        return pol
    raise PolicyError(
        f"Cannot target {platform_id} (status={status}). "
        f"Reason: {pol['rationale'][:160]}\n"
        f"Suggested alternative: {pol['if_targeted'] or '(see ai_policy_blockers.yaml)'}"
    )


def disclosure_text(platform_id: str) -> str:
    """Return the AI-disclosure text required for this platform, or empty string."""
    pol = get_platform_policy(platform_id)
    if not pol["disclosure_required"]:
        return ""
    # Standard disclosure phrasing — reusable across platforms requiring disclosure.
    return (
        "AI Disclosure: This work was created with AI-assisted illustration "
        "(FLUX-schnell) and AI-assisted writing (Anthropic Claude). All "
        "story, characters, and editorial decisions are by the human "
        "author/team. AI tools were used for image generation, text drafting "
        "support, and translation."
    )

"""Tests for strict topic identity enforcement (Hardening Spec §5A).

Ensures the pipeline rejects silent alias collapse when strict_identity=True.
"""
from __future__ import annotations

import types
from pathlib import Path

import pytest

from phoenix_v4.planning.output_contract import (
    TopicIdentityError,
    build_output_contract,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES_PATH = REPO_ROOT / "config" / "identity_aliases.yaml"
FORMAT_REGISTRY_PATH = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"


def _make_args(**overrides):
    defaults = {
        "topic": "anxiety",
        "persona": "gen_z_professionals",
        "location": None,
        "teacher": None,
        "runtime_format": "standard_book",
        "structural_format": "F006",
    }
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def _make_resolved(**overrides):
    defaults = {
        "canonical_topic_id": "anxiety",
        "canonical_persona_id": "gen_z_professionals",
        "resolved_location_id": "",
        "teacher_mode": False,
        "teacher_id": None,
        "quality_profile": "production",
        "runtime_format": "standard_book",
        "structural_format": "F006",
    }
    defaults.update(overrides)
    return defaults


# Known aliases from config/identity_aliases.yaml
ALIAS_PAIRS = [
    ("overthinking", "anxiety"),
    ("burnout", "anxiety"),
    ("shame", "self_worth"),
    ("comparison", "self_worth"),
    ("social_anxiety", "anxiety"),
    ("overwhelm", "anxiety"),
    ("spiral_thoughts", "anxiety"),
]


class TestStrictModeRejectsAlias:
    """strict_identity=True raises TopicIdentityError on alias collapse."""

    @pytest.mark.parametrize("requested,canonical", ALIAS_PAIRS)
    def test_alias_rejected_in_strict_mode(self, requested, canonical):
        with pytest.raises(TopicIdentityError, match=requested):
            build_output_contract(
                _make_args(topic=requested),
                _make_resolved(canonical_topic_id=canonical),
                aliases_path=ALIASES_PATH,
                registry_path=FORMAT_REGISTRY_PATH,
                strict_identity=True,
            )


class TestStrictModePassesWhenNoAlias:
    """strict_identity=True succeeds when topic is already canonical."""

    def test_canonical_topic_passes(self):
        contract = build_output_contract(
            _make_args(topic="anxiety"),
            _make_resolved(canonical_topic_id="anxiety"),
            strict_identity=True,
        )
        assert contract["topic_aliased"] is False
        assert contract["requested_topic_id"] == "anxiety"

    def test_self_worth_passes(self):
        contract = build_output_contract(
            _make_args(topic="self_worth"),
            _make_resolved(canonical_topic_id="self_worth"),
            strict_identity=True,
        )
        assert contract["topic_aliased"] is False


class TestNonStrictModeAllowsAlias:
    """Default (strict_identity=False) allows alias with flag only."""

    @pytest.mark.parametrize("requested,canonical", ALIAS_PAIRS)
    def test_alias_allowed_with_flag(self, requested, canonical):
        contract = build_output_contract(
            _make_args(topic=requested),
            _make_resolved(canonical_topic_id=canonical),
            aliases_path=ALIASES_PATH,
            registry_path=FORMAT_REGISTRY_PATH,
            strict_identity=False,
        )
        assert contract["topic_aliased"] is True
        assert contract["requested_topic_id"] == requested

    def test_default_is_non_strict(self):
        """Omitting strict_identity defaults to False (no rejection)."""
        contract = build_output_contract(
            _make_args(topic="overthinking"),
            _make_resolved(canonical_topic_id="anxiety"),
            aliases_path=ALIASES_PATH,
            registry_path=FORMAT_REGISTRY_PATH,
        )
        assert contract["topic_aliased"] is True


class TestTopicIdentityErrorMessage:
    """Error message is actionable per Hardening Spec."""

    def test_error_mentions_both_topics(self):
        with pytest.raises(TopicIdentityError) as exc_info:
            build_output_contract(
                _make_args(topic="overthinking"),
                _make_resolved(canonical_topic_id="anxiety"),
                aliases_path=ALIASES_PATH,
                strict_identity=True,
            )
        msg = str(exc_info.value)
        assert "overthinking" in msg
        assert "anxiety" in msg
        assert "strict" in msg.lower() or "Strict" in msg

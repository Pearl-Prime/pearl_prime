"""Tests for phoenix_v4.planning.output_contract (Hardening Spec 5G)."""
from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from phoenix_v4.planning.output_contract import (
    build_output_contract,
    update_contract_post_render,
    _resolve_topic_alias,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES_PATH = REPO_ROOT / "config" / "identity_aliases.yaml"
FORMAT_REGISTRY_PATH = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_args(**overrides):
    """Build a minimal argparse-like Namespace for testing."""
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


def _make_resolved_config(**overrides):
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


REQUIRED_FIELDS = {
    "requested_topic_id",
    "canonical_topic_id",
    "topic_aliased",
    "requested_location_id",
    "resolved_location_id",
    "location_fallback",
    "teacher_mode",
    "teacher_id",
    "quality_profile",
    "runtime_format",
    "structural_format",
    "runtime_request",
    "runtime_achieved",
    "word_count_target",
    "word_count_achieved",
    "budget_check_result",
    "timestamp",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestContractFields:
    """Contract includes all required fields and is JSON-serializable."""

    def test_all_required_fields_present(self):
        contract = build_output_contract(_make_args(), _make_resolved_config())
        missing = REQUIRED_FIELDS - set(contract.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_json_serializable(self):
        contract = build_output_contract(_make_args(), _make_resolved_config())
        # Must not raise
        serialized = json.dumps(contract)
        roundtrip = json.loads(serialized)
        assert roundtrip["requested_topic_id"] == "anxiety"

    def test_timestamp_is_iso8601(self):
        contract = build_output_contract(_make_args(), _make_resolved_config())
        ts = contract["timestamp"]
        assert "T" in ts  # basic ISO check
        assert "+" in ts or "Z" in ts  # timezone info present


class TestTopicAliasing:
    """Topic aliasing detected (overthinking -> anxiety)."""

    def test_overthinking_aliased(self):
        """overthinking maps to anxiety; topic_aliased must be True."""
        contract = build_output_contract(
            _make_args(topic="overthinking"),
            _make_resolved_config(canonical_topic_id="anxiety"),
        )
        assert contract["requested_topic_id"] == "overthinking"
        assert contract["canonical_topic_id"] == "anxiety"
        assert contract["topic_aliased"] is True

    def test_no_alias_when_same(self):
        contract = build_output_contract(
            _make_args(topic="anxiety"),
            _make_resolved_config(canonical_topic_id="anxiety"),
        )
        assert contract["topic_aliased"] is False

    def test_resolve_topic_alias_from_config(self):
        """_resolve_topic_alias reads real config/identity_aliases.yaml."""
        if not ALIASES_PATH.exists():
            pytest.skip("identity_aliases.yaml not present")
        result = _resolve_topic_alias("overthinking", aliases_path=ALIASES_PATH)
        assert result == "anxiety"


class TestLocationFallback:
    """Location fallback detected."""

    def test_fallback_when_different(self):
        contract = build_output_contract(
            _make_args(location="nyc"),
            _make_resolved_config(resolved_location_id="nyc_grand_central"),
        )
        assert contract["requested_location_id"] == "nyc"
        assert contract["resolved_location_id"] == "nyc_grand_central"
        assert contract["location_fallback"] is True

    def test_no_fallback_when_same(self):
        contract = build_output_contract(
            _make_args(location="nyc_metro"),
            _make_resolved_config(resolved_location_id="nyc_metro"),
        )
        assert contract["location_fallback"] is False

    def test_fallback_when_no_request_but_resolved(self):
        contract = build_output_contract(
            _make_args(location=None),
            _make_resolved_config(resolved_location_id="nyc_metro"),
        )
        assert contract["location_fallback"] is True


class TestPostRenderUpdate:
    """Post-render fields updated correctly."""

    def test_word_count_pass(self):
        contract = build_output_contract(
            _make_args(runtime_format="standard_book"),
            _make_resolved_config(runtime_format="standard_book"),
            registry_path=FORMAT_REGISTRY_PATH,
        )
        updated = update_contract_post_render(
            contract,
            runtime_achieved="standard_book",
            word_count_achieved=10000,
        )
        assert updated["word_count_achieved"] == 10000
        assert updated["runtime_achieved"] == "standard_book"
        assert updated["budget_check_result"] == "pass"

    def test_word_count_fail(self):
        contract = build_output_contract(
            _make_args(runtime_format="standard_book"),
            _make_resolved_config(runtime_format="standard_book"),
            registry_path=FORMAT_REGISTRY_PATH,
        )
        updated = update_contract_post_render(
            contract,
            word_count_achieved=4000,
        )
        assert updated["budget_check_result"] == "fail"

    def test_explicit_budget_result(self):
        contract = build_output_contract(_make_args(), _make_resolved_config())
        updated = update_contract_post_render(
            contract,
            budget_check_result="pass",
            word_count_achieved=9500,
        )
        assert updated["budget_check_result"] == "pass"

    def test_original_contract_unchanged(self):
        contract = build_output_contract(_make_args(), _make_resolved_config())
        original_ts = contract["timestamp"]
        updated = update_contract_post_render(contract, word_count_achieved=5000)
        # Original dict must not be mutated
        assert contract["word_count_achieved"] == 0
        assert updated["word_count_achieved"] == 5000


class TestTeacherMode:
    """Teacher mode and teacher_id carried correctly."""

    def test_teacher_mode_on(self):
        contract = build_output_contract(
            _make_args(teacher="ahjan"),
            _make_resolved_config(teacher_mode=True, teacher_id="ahjan"),
        )
        assert contract["teacher_mode"] is True
        assert contract["teacher_id"] == "ahjan"

    def test_teacher_mode_off(self):
        contract = build_output_contract(
            _make_args(teacher=None),
            _make_resolved_config(teacher_mode=False, teacher_id=None),
        )
        assert contract["teacher_mode"] is False
        assert contract["teacher_id"] is None

"""Tests for the DashScope Qwen candidate client's guardrails, and for the
structural_validator.py fallback header parser added alongside it.

Does NOT make a real DashScope API call (no network, no spend) -- these are
unit tests of the guard logic (governance re-check, cloud opt-in, intl-only
endpoint, call cap). A real single-digit live smoke test against
qwen3.7-max was run manually per this lane's CLOSEOUT_RECEIPT; it is not
part of the automated suite because it requires live Keychain-loaded
DASHSCOPE_API_KEY and spends real money.
"""
from __future__ import annotations

import os

import pytest

from scripts.localization.translation_quality.candidates.dashscope_qwen_client import (
    DashScopeEndpointError,
    DashScopeNotYetExemptError,
    DEFAULT_DASHSCOPE_BASE_URL,
    _CallBudget,
    _assert_intl_endpoint,
    _governance_exemption_landed,
    translate,
)
from scripts.localization.translation_quality.structural_validator import validate


# ─── call cap ──────────────────────────────────────────────────────────────


def test_call_cap_halts_at_third_call_on_cap_2():
    budget = _CallBudget(cap=2)
    budget.check_and_increment()
    budget.check_and_increment()
    with pytest.raises(RuntimeError, match="call cap"):
        budget.check_and_increment()
    assert budget.calls_made == 2  # the 3rd (rejected) call is not counted


# ─── intl-endpoint guard ───────────────────────────────────────────────────


def test_intl_endpoint_accepted():
    _assert_intl_endpoint(DEFAULT_DASHSCOPE_BASE_URL)  # must not raise


def test_beijing_mainland_endpoint_rejected():
    with pytest.raises(DashScopeEndpointError):
        _assert_intl_endpoint("https://dashscope.aliyuncs.com/compatible-mode/v1")


def test_arbitrary_non_dashscope_url_rejected():
    with pytest.raises(DashScopeEndpointError):
        _assert_intl_endpoint("https://evil.example.com/v1")


# ─── governance + cloud opt-in guards (real runtime checks, not one-time) ──


def test_governance_exemption_currently_landed():
    # This asserts the live repo state on purpose: if Lane 00's exemption is
    # ever reverted from banned_llm_patterns.yaml, this test starts failing,
    # which is the intended signal (translate() must refuse to call too).
    assert _governance_exemption_landed() is True


def test_translate_refuses_without_allow_cloud_env(monkeypatch):
    monkeypatch.delenv("PHOENIX_TRANSLATION_ALLOW_CLOUD", raising=False)
    monkeypatch.setenv("DASHSCOPE_API_KEY", "fake-key-not-used")
    with pytest.raises(RuntimeError, match="PHOENIX_TRANSLATION_ALLOW_CLOUD"):
        translate("hello world", target_locale="zh-CN")


def test_translate_refuses_without_api_key(monkeypatch):
    monkeypatch.setenv("PHOENIX_TRANSLATION_ALLOW_CLOUD", "1")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
        translate("hello world", target_locale="zh-CN")


def test_translate_refuses_non_intl_base_url(monkeypatch):
    monkeypatch.setenv("PHOENIX_TRANSLATION_ALLOW_CLOUD", "1")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "fake-key-not-used")
    monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    with pytest.raises(DashScopeEndpointError):
        translate("hello world", target_locale="zh-CN")


# ─── structural_validator.py alt-header fallback ──────────────────────────


VARIANT_SOURCE = (
    "--- variant: v01\n"
    "You're allowed to be terrified about money.\n\n"
    "--- variant: v02\n"
    "You have permission to stop checking.\n"
)


def test_variant_convention_good_candidate_passes():
    candidate = (
        "--- variant: v01\n"
        "你可以对钱感到恐惧。\n\n"
        "--- variant: v02\n"
        "你有权停止检查。\n"
    )
    result = validate(VARIANT_SOURCE, candidate, locale="zh-CN")
    assert result.ok, result.reasons


def test_variant_convention_missing_block_detected():
    candidate = "--- variant: v01\n你可以对钱感到恐惧。\n"
    result = validate(VARIANT_SOURCE, candidate, locale="zh-CN")
    assert not result.ok
    assert "missing_header_ids" in result.reasons
    assert "VARIANT_v02" in result.details["missing_header_ids"]


def test_variant_convention_translated_label_line_still_parses():
    # Even if a candidate mistranslates the literal word "variant" inside
    # the header line itself, the parser's job here is just structural
    # counting -- catching the mistranslation itself is glossary/protected-
    # terms scope, not this fallback parser's job. Confirm it degrades to
    # zero blocks (safely) rather than crashing.
    candidate = "--- 版本: v01\n你可以对钱感到恐惧。\n"
    result = validate(VARIANT_SOURCE, candidate, locale="zh-CN")
    assert not result.ok
    assert "missing_header_ids" in result.reasons

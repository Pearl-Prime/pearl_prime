"""Tests for _fill_mechanism_tokens — the {selected_mechanism}/{selected_signal}
resolver used by REFLECTION atoms in tech_finance_burnout × millennial_women_professionals
combos.

Guards:
  * happy path — known combo replaces both tokens from the bank (no braces leak)
  * defaults fallback — unknown combo still replaces tokens via the defaults pool
  * missing bank file — resolver no-ops by stripping tokens instead of raising
  * determinism — same seed produces identical output across calls
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning import injection_resolver as ir


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _reset_cache():
    ir._reset_mechanism_resolver_cache()
    yield
    ir._reset_mechanism_resolver_cache()


def _sample_text() -> str:
    return (
        "The mechanism is {selected_mechanism}. "
        "{selected_signal} And the day continues."
    )


def test_happy_path_known_combo_fills_both_tokens():
    out = ir._fill_mechanism_tokens(
        _sample_text(),
        persona_id="tech_finance_burnout",
        topic="sleep_anxiety",
        seed="unit_test_seed_1",
        repo_root=REPO_ROOT,
    )
    assert "{selected_mechanism}" not in out
    assert "{selected_signal}" not in out
    # sanity: something non-empty replaced each token
    assert "The mechanism is ." not in out
    assert len(out) > len(_sample_text()) - len("{selected_mechanism}") - len("{selected_signal}")


def test_fallback_to_defaults_for_unknown_combo(tmp_path):
    """Unknown (persona, topic) should still resolve via the ``defaults`` pool."""
    out = ir._fill_mechanism_tokens(
        _sample_text(),
        persona_id="no_such_persona_xyz",
        topic="no_such_topic_xyz",
        seed="unit_test_seed_2",
        repo_root=REPO_ROOT,
    )
    assert "{selected_mechanism}" not in out
    assert "{selected_signal}" not in out


def test_missing_bank_file_strips_tokens(tmp_path):
    """When the YAML is absent the resolver must not crash — it strips tokens so
    no braces reach the reader."""
    # tmp_path has no config/content_banks/selected_mechanism_resolver.yaml
    out = ir._fill_mechanism_tokens(
        _sample_text(),
        persona_id="tech_finance_burnout",
        topic="sleep_anxiety",
        seed="unit_test_seed_3",
        repo_root=tmp_path,
    )
    assert "{selected_mechanism}" not in out
    assert "{selected_signal}" not in out


def test_determinism_same_seed_same_output():
    seed = "deterministic_seed_42"
    a = ir._fill_mechanism_tokens(
        _sample_text(), "tech_finance_burnout", "overthinking", seed, REPO_ROOT
    )
    # reset cache to ensure we're not relying on it
    ir._reset_mechanism_resolver_cache()
    b = ir._fill_mechanism_tokens(
        _sample_text(), "tech_finance_burnout", "overthinking", seed, REPO_ROOT
    )
    assert a == b


def test_different_seeds_may_differ():
    """Not strictly required (collisions are possible with short pools), but
    across a few seeds at least one pair should differ — confirms the seed is
    actually factored into the pick rather than being ignored."""
    outs = {
        ir._fill_mechanism_tokens(
            _sample_text(), "tech_finance_burnout", "overthinking", f"seed_{i}", REPO_ROOT
        )
        for i in range(10)
    }
    assert len(outs) > 1


def test_bank_has_tfb_financial_anxiety_and_imposter_syndrome():
    """Regression guard — these two combos were missing from the bank and the
    composer was silently stripping the tokens for them."""
    path = REPO_ROOT / "config" / "content_banks" / "selected_mechanism_resolver.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    resolver = data.get("resolver") or {}
    tfb = resolver.get("tech_finance_burnout") or {}
    for topic in ("financial_anxiety", "imposter_syndrome"):
        assert topic in tfb, f"tfb.{topic} missing from resolver"
        entry = tfb[topic]
        assert len(entry.get("selected_mechanism") or []) >= 5
        assert len(entry.get("selected_signal") or []) >= 5
    assert (data.get("defaults") or {}).get("selected_mechanism")
    assert (data.get("defaults") or {}).get("selected_signal")

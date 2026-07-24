"""Tests for scripts/ci/check_store_series_name_consistency.py."""
from __future__ import annotations

from scripts.ci.check_store_series_name_consistency import (
    check_store_series_name_consistency,
)


def _plan(store_series=None, installment_number=1, source_path="p.yaml"):
    return {
        "store_series": store_series,
        "installment_number": installment_number,
        "_source_path": source_path,
    }


def test_consistent_names_pass():
    plans = [
        _plan({"id": "s1", "name": "The Signal Map"}, installment_number=1, source_path="a.yaml"),
        _plan({"id": "s1", "name": "The Signal Map"}, installment_number=2, source_path="b.yaml"),
    ]
    ok, hard_failures, warnings = check_store_series_name_consistency(plans)
    assert ok
    assert not hard_failures
    assert not warnings


def test_inconsistent_names_hard_fail():
    plans = [
        _plan({"id": "s1", "name": "The Signal Map"}, installment_number=1, source_path="a.yaml"),
        _plan({"id": "s1", "name": "The Signal Map (Alt)"}, installment_number=2, source_path="b.yaml"),
    ]
    ok, hard_failures, warnings = check_store_series_name_consistency(plans)
    assert not ok
    assert len(hard_failures) == 1
    assert "s1" in hard_failures[0]
    assert "The Signal Map" in hard_failures[0]
    assert "The Signal Map (Alt)" in hard_failures[0]


def test_missing_store_series_is_warn_not_fail():
    plans = [
        _plan(None, source_path="a.yaml"),
        _plan({"id": "s1", "name": "The Signal Map"}, source_path="b.yaml"),
    ]
    ok, hard_failures, warnings = check_store_series_name_consistency(plans)
    assert ok
    assert not hard_failures
    assert any("no store_series" in w for w in warnings)


def test_duplicate_installment_number_is_warn_not_fail():
    plans = [
        _plan({"id": "s1", "name": "The Signal Map"}, installment_number=1, source_path="a.yaml"),
        _plan({"id": "s1", "name": "The Signal Map"}, installment_number=1, source_path="b.yaml"),
    ]
    ok, hard_failures, warnings = check_store_series_name_consistency(plans)
    assert ok
    assert not hard_failures
    assert any("duplicate installment_number" in w for w in warnings)


def test_empty_plans_pass_trivially():
    ok, hard_failures, warnings = check_store_series_name_consistency([])
    assert ok
    assert not hard_failures
    assert not warnings

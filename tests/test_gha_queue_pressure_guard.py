"""Tests for scripts/ci/gha_queue_pressure_guard.py decision logic."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.ci.gha_queue_pressure_guard import (
    assess_queue_pressure,
    snapshot_from_runs,
)


def _runs(branches: list[str]) -> list[dict]:
    return [{"status": "queued", "headBranch": b} for b in branches]


def test_cool_queue_allows_proceed():
    runs = _runs(["main", "agent/foo", "agent/bar"])
    snap = snapshot_from_runs(runs)
    decision = assess_queue_pressure(snap)
    assert not decision.blocked
    assert snap.queued_total == 3
    assert snap.catalog_queued == 0


def test_high_total_blocks():
    branches = ["main"] * 20 + [f"ci/catalog-ja_jp-brand-1-b1"] * 65
    snap = snapshot_from_runs(_runs(branches))
    decision = assess_queue_pressure(snap)
    assert decision.blocked
    assert "queued_total" in decision.reason


def test_high_catalog_blocks():
    branches = [f"ci/catalog-ko_kr-brand-{i}-1-b1" for i in range(70)]
    snap = snapshot_from_runs(_runs(branches))
    decision = assess_queue_pressure(snap)
    assert decision.blocked
    assert "catalog_queued" in decision.reason


def test_starvation_ratio_blocks():
    branches = (
        [f"ci/catalog-ja_jp-x-1-b{i}" for i in range(30)]
        + ["agent/manga-stillness-continuity-repair-2026-07-09"] * 2
    )
    snap = snapshot_from_runs(_runs(branches))
    decision = assess_queue_pressure(snap)
    assert decision.blocked
    assert "starvation" in decision.reason


def test_wave2_hot_shape_blocks():
    branches = (
        [f"ci/catalog-ko_kr-high_performer-28923213690-b{i % 6}" for i in range(166)]
        + ["agent/manga-stillness-continuity-repair-2026-07-09"] * 7
    )
    snap = snapshot_from_runs(_runs(branches))
    assert snap.queued_total == 173
    assert snap.catalog_queued == 166
    decision = assess_queue_pressure(snap)
    assert decision.blocked

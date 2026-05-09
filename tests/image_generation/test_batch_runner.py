"""Tests for dual-path image batch runner scaffold (dry-run only)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts.image_generation import batch_runner


def _write_plan(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "plan.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_load_plan_parses_batch_blocks(tmp_path: Path) -> None:
    plan = _write_plan(
        tmp_path,
        """# Plan
Intro text.

```batch
batch_id: alpha
locale: en-US
dispatch_path: runcomfy
sequence: 2
panels: p_1_1, p_1_2
```

```batch
batch_id: beta
locale: ja-JP
dispatch_path: pearl_star
sequence: 1
```
""",
    )
    batches = batch_runner.load_plan(plan)
    assert [b["batch_id"] for b in batches] == ["alpha", "beta"]
    assert batches[0]["locale"] == "en-US"
    assert batches[0]["panels"] == ["p_1_1", "p_1_2"]
    assert batches[1]["dispatch_path"] == "pearl_star"


def test_priority_sort_locale_first_q_img_1() -> None:
    batches = [
        {"batch_id": "en", "locale": "en-US", "sequence": 1},
        {"batch_id": "ja", "locale": "ja-JP", "sequence": 9},
        {"batch_id": "zh", "locale": "zh-CN", "sequence": 3},
        {"batch_id": "de", "locale": "de-DE", "sequence": 0},
    ]
    ordered = batch_runner.priority_sort(batches)
    assert [b["batch_id"] for b in ordered] == ["ja", "zh", "de", "en"]


def test_dispatch_dry_run_pearl_star() -> None:
    batch = {"batch_id": "x1", "locale": "ja-JP", "dispatch_path": "pearl_star"}
    res = batch_runner.dispatch(batch, dry_run=True)
    assert res["dispatch_path"] == "pearl_star"
    assert res["dry_run"] is True
    assert res["status"] == "dry_run"


def test_dispatch_dry_run_runcomfy() -> None:
    batch = {"batch_id": "x2", "locale": "en-US", "dispatch_path": "runcomfy"}
    res = batch_runner.dispatch(batch, dry_run=True)
    assert res["dispatch_path"] == "runcomfy"
    assert res["dry_run"] is True
    assert res["status"] == "dry_run"


def test_runcomfy_cost_check_missing_file() -> None:
    missing = Path("/nonexistent/runcomfy_monthly_spend.tsv")
    info = batch_runner.runcomfy_cost_check(spend_path=missing)
    assert info["spend_to_date_usd"] == 0.0
    assert info["cooldown"] is False
    assert info["source_path"] is None


def test_runcomfy_cost_check_cooldown_at_cap(tmp_path: Path) -> None:
    spend = tmp_path / "spend.tsv"
    spend.write_text(
        "date\tspend_usd\n2026-05-01\t6.25\n2026-05-02\t3.75\n",
        encoding="utf-8",
    )
    info = batch_runner.runcomfy_cost_check(spend_path=spend, cooldown_usd=10.0)
    assert info["spend_to_date_usd"] == 10.0
    assert info["cooldown"] is True
    assert info["source_path"] == str(spend)


def test_run_batches_skips_runcomfy_when_cooled_down(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spend = tmp_path / "spend.tsv"
    spend.write_text("date\tspend_usd\n2026-05-01\t12.00\n", encoding="utf-8")
    monkeypatch.setattr(batch_runner, "RUNCOMFY_SPEND_TSV", spend)
    batches = [
        {"batch_id": "r1", "locale": "en-US", "dispatch_path": "runcomfy", "sequence": 1},
        {"batch_id": "p1", "locale": "ja-JP", "dispatch_path": "pearl_star", "sequence": 2},
    ]

    def _cost() -> dict:
        return batch_runner.runcomfy_cost_check(spend_path=spend)

    results = batch_runner.run_batches(batches, dry_run=True, cost_check=_cost)
    # Locale-first: ja pearl_star first even though runcomfy listed first in input
    assert results[0]["dispatch_path"] == "pearl_star"
    assert results[1].get("skipped") is True
    assert results[1].get("reason") == "runcomfy_cost_cooldown"


def test_log_dispatch_appends_tsv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = tmp_path / "image_batch_dispatch_log.tsv"
    monkeypatch.setattr(batch_runner, "DISPATCH_LOG_TSV", log)
    batch_runner.log_dispatch(
        {
            "batch_id": "b99",
            "dispatch_path": "pearl_star",
            "dry_run": True,
            "status": "dry_run",
            "notes": "unit",
            "payload": {"k": 1},
        }
    )
    batch_runner.log_dispatch(
        {
            "batch_id": "b100",
            "dispatch_path": "runcomfy",
            "dry_run": True,
            "status": "dry_run",
            "payload": {},
        }
    )
    with log.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows[0]["batch_id"] == "b99"
    assert rows[1]["batch_id"] == "b100"
    payload = json.loads(rows[0]["payload_json"])
    assert payload == {"k": 1}

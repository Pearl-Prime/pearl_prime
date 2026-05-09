"""Tests for RunComfy dispatch + cost tracker wiring (dry-run, no vendor HTTP)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.image_generation import batch_runner
from scripts.image_generation.runcomfy_dispatch import (
    RunComfyAuthError,
    dispatch_workflow,
    load_token,
)
from scripts.image_generation.runcomfy_cost_tracker import poll_billing, read_latest_cumulative_spend_usd


def _flux_workflow() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"


def test_dispatch_workflow_dry_run_shape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RUNCOMFY_API_TOKEN", raising=False)
    monkeypatch.delenv("RUNCOMFY_API_KEY", raising=False)
    monkeypatch.delenv("RUNCOMFY_TOKEN", raising=False)
    spend = tmp_path / "spend.tsv"
    spend.write_text(
        "date\tdispatched_jobs_today\tcumulative_month_spend_usd\n"
        "2026-05-09\t0\t1.0000\n",
        encoding="utf-8",
    )
    out = dispatch_workflow(
        _flux_workflow(),
        dry_run=True,
        require_token=False,
        spend_tsv=spend,
    )
    assert out["dry_run"] is True
    assert out["status"] == "dry_run"
    assert out["cooldown"] is False
    assert "workflow_path" in out
    assert out["workflow_node_count"] > 0
    assert "http_would_call" in out


def test_cumulative_spend_tsv_uses_last_row_not_sum(tmp_path: Path) -> None:
    spend = tmp_path / "spend.tsv"
    spend.write_text(
        "date\tdispatched_jobs_today\tcumulative_month_spend_usd\n"
        "2026-05-01\t1\t5.0000\n"
        "2026-05-02\t2\t12.0000\n",
        encoding="utf-8",
    )
    assert read_latest_cumulative_spend_usd(spend) == 12.0
    info = batch_runner.runcomfy_cost_check(spend_path=spend, cooldown_usd=10.0)
    assert info["spend_to_date_usd"] == 12.0
    assert info["cooldown"] is True


def test_cost_cap_cooldown_dispatch_flag(tmp_path: Path) -> None:
    spend = tmp_path / "spend.tsv"
    spend.write_text(
        "date\tdispatched_jobs_today\tcumulative_month_spend_usd\n"
        "2026-05-10\t3\t10.0000\n",
        encoding="utf-8",
    )
    out = dispatch_workflow(
        _flux_workflow(),
        dry_run=True,
        require_token=False,
        spend_tsv=spend,
        cooldown_usd=10.0,
    )
    assert out["cooldown"] is True


def test_poll_billing_dry_run_mock() -> None:
    out = poll_billing(dry_run=True)
    assert out["dry_run"] is True
    assert out["cumulative_month_spend_usd"] == 3.25
    assert "billing_url" in out
    assert out["cooldown"] is False


def test_missing_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RUNCOMFY_API_TOKEN", raising=False)
    monkeypatch.delenv("RUNCOMFY_API_KEY", raising=False)
    monkeypatch.delenv("RUNCOMFY_TOKEN", raising=False)
    monkeypatch.setattr("sys.platform", "linux")
    with pytest.raises(RunComfyAuthError) as ei:
        load_token(require=True)
    assert "RUNCOMFY_API_TOKEN" in str(ei.value)


def test_batch_runner_dispatch_includes_runcomfy_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RUNCOMFY_API_TOKEN", raising=False)
    monkeypatch.delenv("RUNCOMFY_API_KEY", raising=False)
    monkeypatch.delenv("RUNCOMFY_TOKEN", raising=False)
    batch = {"batch_id": "z1", "locale": "en-US", "dispatch_path": "runcomfy"}
    res = batch_runner.dispatch(batch, dry_run=True)
    assert res["dispatch_path"] == "runcomfy"
    assert res["status"] == "dry_run"
    assert "runcomfy_dispatch" in res
    assert res["runcomfy_dispatch"]["dry_run"] is True


def test_dispatch_workflow_json_roundtrip(tmp_path: Path) -> None:
    wf = tmp_path / "w.json"
    payload = {"1": {"class_type": "Stub", "inputs": {}}}
    wf.write_text(json.dumps(payload), encoding="utf-8")
    out = dispatch_workflow(wf, dry_run=True, require_token=False)
    assert out["workflow_node_count"] == 1

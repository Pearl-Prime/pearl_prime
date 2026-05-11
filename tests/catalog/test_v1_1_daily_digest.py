"""Tests for ``scripts/catalog/v1_1_daily_digest.py``.

Covers:
- spend rollup math (cumulative + per-day from ledger TSV)
- per-locale + per-surface breakdown
- ETA extrapolation
- handoff append idempotency on (date, run_id)
- markdown digest contains required fields
- CLI exit code
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog import v1_1_daily_digest as dd  # noqa: E402
from scripts.catalog import v1_1_dispatch_checkpoint as cp  # noqa: E402


@pytest.fixture
def primed_run(tmp_path):
    """Build a checkpoint with a known status mix and a ledger with spend."""
    batches = [
        {"batch_id": "c1", "brand_id": "stillness_press", "locale": "en-US",
         "surface": "cover", "dispatch_path": "pearl_star",
         "output_path": "/x/c1.png"},
        {"batch_id": "c2", "brand_id": "stillness_press", "locale": "ja-JP",
         "surface": "cover", "dispatch_path": "pearl_star",
         "output_path": "/x/c2.png"},
        {"batch_id": "p1", "brand_id": "warrior_calm", "locale": "en-US",
         "surface": "panel", "dispatch_path": "runcomfy",
         "output_path": "/x/p1.png"},
        {"batch_id": "p2", "brand_id": "warrior_calm", "locale": "ja-JP",
         "surface": "panel", "dispatch_path": "runcomfy",
         "output_path": "/x/p2.png"},
        {"batch_id": "p3", "brand_id": "warrior_calm", "locale": "ja-JP",
         "surface": "panel", "dispatch_path": "runcomfy",
         "output_path": "/x/p3.png"},
    ]
    cp.init_checkpoint("rd1", batches, root=tmp_path)
    cp.mark_succeeded("rd1", "c1", 22.0, "/x/c1.png", root=tmp_path)
    cp.mark_succeeded("rd1", "c2", 30.0, "/x/c2.png", root=tmp_path)
    cp.mark_succeeded("rd1", "p1", 40.0, "/x/p1.png", root=tmp_path)
    cp.mark_failed("rd1", "p2", "RunComfyTimeout", "queue stuck", 3, root=tmp_path)
    # p3 stays pending

    ledger = tmp_path / "runcomfy_spend_ledger.tsv"
    ledger.write_text(
        "timestamp_utc\tdate_local\tbatch_id\tworkflow_id\tgpu_seconds\test_usd\t"
        "cumulative_month_usd\tsource\trate_per_second_usd\trequest_id\n"
        "2026-05-12T01:00:00+00:00\t2026-05-12\tp1\tqwen\t40\t0.013\t0.013\test\t0.000337\trid1\n"
        "2026-05-12T02:00:00+00:00\t2026-05-12\tp2\tqwen\t10\t0.003\t0.016\test\t0.000337\trid2\n",
        encoding="utf-8",
    )

    handoff = tmp_path / "CONDUCTOR_HANDOFF.md"
    return {
        "root": tmp_path,
        "ledger": ledger,
        "handoff": handoff,
    }


def test_compute_digest_aggregates_status(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    assert d["cells_succeeded"] == 3
    assert d["cells_failed_permanently"] == 1
    assert d["total_pending"] == 1


def test_compute_digest_spend_math(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    assert d["cumulative_runcomfy_spend_usd"] == 0.016
    assert d["day_runcomfy_spend_usd"] == pytest.approx(0.016, abs=1e-4)
    assert d["cap_remaining_usd"] == pytest.approx(10.0 - 0.016, abs=1e-4)


def test_compute_digest_pearl_seconds(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    # c1 (22) + c2 (30) = 52 on pearl_star
    assert d["gpu_seconds_pearl_star"] == 52.0


def test_compute_digest_per_locale(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    assert "en-US" in d["by_locale"]
    assert "ja-JP" in d["by_locale"]


def test_compute_digest_per_surface(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    assert d["by_surface"]["cover"]["succeeded"] == 2
    assert d["by_surface"]["panel"]["succeeded"] == 1


def test_eta_extrapolation_finite(primed_run):
    d = dd.compute_digest(
        "rd1",
        date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    assert "days at current rate" in d["est_completion_eta"]


def test_eta_handles_zero_succeeded(tmp_path):
    cp.init_checkpoint("rd_empty", [
        {"batch_id": "b1", "brand_id": "x", "locale": "en-US", "surface": "cover"}
    ], root=tmp_path)
    d = dd.compute_digest(
        "rd_empty", date="2026-05-12",
        checkpoint_root=tmp_path,
        ledger_path=tmp_path / "no_such_ledger.tsv",
    )
    assert "n/a" in d["est_completion_eta"]


def test_handoff_append_idempotent(primed_run):
    d = dd.compute_digest(
        "rd1", date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    dd.append_handoff(d, handoff_path=primed_run["handoff"])
    dd.append_handoff(d, handoff_path=primed_run["handoff"])
    text = primed_run["handoff"].read_text(encoding="utf-8")
    # Idempotent on (day, run_id): only one matching line
    matching = [ln for ln in text.splitlines() if "run_id=rd1" in ln and "2026-05-12" in ln]
    assert len(matching) == 1


def test_handoff_keeps_other_runs(primed_run):
    d1 = dd.compute_digest(
        "rd1", date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
    )
    dd.append_handoff(d1, handoff_path=primed_run["handoff"])
    # Different run_id same day → both kept
    d2 = dict(d1)
    d2["run_id"] = "rd2"
    dd.append_handoff(d2, handoff_path=primed_run["handoff"])
    text = primed_run["handoff"].read_text(encoding="utf-8")
    assert "run_id=rd1" in text
    assert "run_id=rd2" in text


def test_write_digest_creates_markdown(primed_run, tmp_path):
    out_dir = tmp_path / "coord"
    out = dd.write_digest(
        "rd1",
        date="2026-05-12",
        output_dir=out_dir,
        checkpoint_root=primed_run["root"],
        ledger_path=primed_run["ledger"],
        handoff_path=primed_run["handoff"],
    )
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Pearl_Conductor v3 daily digest" in text
    assert "cumulative_runcomfy_spend_usd" in text
    assert "Per-locale" in text
    assert "Per-surface" in text


def test_cumulative_picks_max_not_last(tmp_path):
    """The ledger's cumulative_month_usd is monotonic per row; we report the
    max so an out-of-order final row cannot under-report."""
    ledger = tmp_path / "led.tsv"
    ledger.write_text(
        "timestamp_utc\tdate_local\tbatch_id\tworkflow_id\tgpu_seconds\test_usd\t"
        "cumulative_month_usd\tsource\trate_per_second_usd\trequest_id\n"
        "t1\t2026-05-12\tx\tw\t10\t0.01\t0.10\test\t0.001\tr1\n"
        "t2\t2026-05-12\tx\tw\t10\t0.02\t0.05\test\t0.001\tr2\n",
        encoding="utf-8",
    )
    rows = dd._read_ledger_rows(ledger)
    cum, day = dd.cumulative_runcomfy_spend(rows, day="2026-05-12")
    assert cum == 0.10
    assert day == pytest.approx(0.03, abs=1e-4)


def test_cli_writes_digest(primed_run, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(dd, "DEFAULT_LEDGER", primed_run["ledger"])
    monkeypatch.setattr(dd, "HANDOFF_PATH", primed_run["handoff"])
    out_dir = tmp_path / "cli_out"
    rc = dd._cli([
        "--run-id", "rd1",
        "--date", "2026-05-12",
        "--output-dir", str(out_dir),
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert "conductor_v3_daily_digest_2026-05-12.md" in out


def test_compute_digest_handles_missing_ledger(primed_run, tmp_path):
    d = dd.compute_digest(
        "rd1", date="2026-05-12",
        checkpoint_root=primed_run["root"],
        ledger_path=tmp_path / "absent.tsv",
    )
    assert d["cumulative_runcomfy_spend_usd"] == 0.0
    assert d["cap_remaining_usd"] == 10.0


def test_top_5_transient_causes_capped(tmp_path):
    batches = [
        {"batch_id": f"b{i}", "brand_id": "x", "locale": "en-US", "surface": "cover"}
        for i in range(10)
    ]
    cp.init_checkpoint("rd_err", batches, root=tmp_path)
    causes = ["E1", "E1", "E2", "E2", "E2", "E3", "E4", "E5", "E6", "E7"]
    for i, c in enumerate(causes):
        cp.mark_failed("rd_err", f"b{i}", c, "msg", 1, root=tmp_path)
    d = dd.compute_digest(
        "rd_err", date="2026-05-12",
        checkpoint_root=tmp_path,
        ledger_path=tmp_path / "no.tsv",
    )
    assert len(d["top_5_transient_causes"]) == 5
    assert d["top_5_transient_causes"][0]["error_class"] == "E2"
    assert d["top_5_transient_causes"][0]["count"] == 3

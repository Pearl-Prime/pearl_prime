"""Tests for scripts.image_generation.runcomfy_spend_ledger."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from scripts.image_generation import runcomfy_spend_ledger as ledger


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def test_estimate_call_cost_usd_basic() -> None:
    # 30 GPU-seconds at default L40S rate (~$0.000337/s) ≈ $0.01011.
    cost = ledger.estimate_call_cost_usd(30.0)
    assert cost == pytest.approx(30 * ledger.DEFAULT_PER_SECOND_USD, rel=1e-6)


def test_estimate_call_cost_usd_clamps_negatives() -> None:
    assert ledger.estimate_call_cost_usd(-5) == 0.0
    assert ledger.estimate_call_cost_usd(0) == 0.0
    assert ledger.estimate_call_cost_usd(10, rate_per_second_usd=0) == 0.0


def test_record_dispatch_writes_ledger_and_rollup(tmp_path: Path) -> None:
    led = tmp_path / "ledger.tsv"
    rol = tmp_path / "rollup.tsv"

    fixed_now = datetime(2026, 5, 12, 16, 30, 0, tzinfo=ZoneInfo("UTC"))
    row = ledger.record_dispatch(
        batch_id="smoke_batch_a",
        workflow_id="flux_txt2img_manga",
        gpu_seconds=20.0,
        ledger_tsv=led,
        rollup_tsv=rol,
        now=fixed_now,
    )

    assert row.source == "estimated"
    assert row.est_usd == pytest.approx(20.0 * ledger.DEFAULT_PER_SECOND_USD, rel=1e-6)
    assert row.cumulative_month_usd == pytest.approx(row.est_usd, rel=1e-6)

    led_rows = _read_tsv(led)
    assert len(led_rows) == 1
    assert led_rows[0]["batch_id"] == "smoke_batch_a"
    assert led_rows[0]["source"] == "estimated"
    assert led_rows[0]["workflow_id"] == "flux_txt2img_manga"
    assert float(led_rows[0]["est_usd"]) == pytest.approx(row.est_usd, rel=1e-6)

    rol_rows = _read_tsv(rol)
    assert len(rol_rows) == 1
    assert rol_rows[0]["dispatched_jobs_today"] == "1"
    # The rollup uses .4f formatting; cap-gate reads this column.
    # Rollup rounds to 4 dp so absolute tolerance of 5e-5 is sufficient.
    assert float(rol_rows[0]["cumulative_month_spend_usd"]) == pytest.approx(
        row.est_usd, abs=5e-5,
    )


def test_record_dispatch_accumulates_in_same_month(tmp_path: Path) -> None:
    led = tmp_path / "ledger.tsv"
    rol = tmp_path / "rollup.tsv"

    n0 = datetime(2026, 5, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    n1 = datetime(2026, 5, 12, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    n2 = datetime(2026, 5, 12, 12, 5, 0, tzinfo=ZoneInfo("UTC"))

    r0 = ledger.record_dispatch(
        batch_id="a", workflow_id="wf", gpu_seconds=10.0,
        ledger_tsv=led, rollup_tsv=rol, now=n0,
    )
    r1 = ledger.record_dispatch(
        batch_id="b", workflow_id="wf", gpu_seconds=20.0,
        ledger_tsv=led, rollup_tsv=rol, now=n1,
    )
    r2 = ledger.record_dispatch(
        batch_id="c", workflow_id="wf", gpu_seconds=15.0,
        ledger_tsv=led, rollup_tsv=rol, now=n2,
    )

    expected_total = (10 + 20 + 15) * ledger.DEFAULT_PER_SECOND_USD
    assert r2.cumulative_month_usd == pytest.approx(expected_total, rel=1e-6)
    assert r0.cumulative_month_usd < r1.cumulative_month_usd < r2.cumulative_month_usd

    led_rows = _read_tsv(led)
    assert [r["batch_id"] for r in led_rows] == ["a", "b", "c"]


def test_record_dispatch_separates_months(tmp_path: Path) -> None:
    led = tmp_path / "ledger.tsv"
    rol = tmp_path / "rollup.tsv"

    apr = datetime(2026, 4, 30, 23, 0, 0, tzinfo=ZoneInfo("UTC"))
    may = datetime(2026, 5, 1, 23, 0, 0, tzinfo=ZoneInfo("UTC"))

    r_apr = ledger.record_dispatch(
        batch_id="apr_call", workflow_id="wf", gpu_seconds=100.0,
        ledger_tsv=led, rollup_tsv=rol, now=apr,
    )
    r_may = ledger.record_dispatch(
        batch_id="may_call", workflow_id="wf", gpu_seconds=10.0,
        ledger_tsv=led, rollup_tsv=rol, now=may,
    )

    # Default TZ is America/Los_Angeles, but rollover only matters for the
    # date_local field; both timestamps map to distinct months in LA tz too.
    assert r_apr.date_local.startswith("2026-04")
    assert r_may.date_local.startswith("2026-05")
    # The May call's MTD must NOT include the April spend.
    assert r_may.cumulative_month_usd == pytest.approx(
        10.0 * ledger.DEFAULT_PER_SECOND_USD, rel=1e-6,
    )


def test_record_dispatch_invalid_source_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="source must be"):
        ledger.record_dispatch(
            batch_id="x",
            workflow_id="wf",
            gpu_seconds=1.0,
            source="scraped_dashboard",
            ledger_tsv=tmp_path / "l.tsv",
            rollup_tsv=tmp_path / "r.tsv",
        )


def test_record_dispatch_billing_api_source_accepted(tmp_path: Path) -> None:
    row = ledger.record_dispatch(
        batch_id="b1",
        workflow_id="wf",
        gpu_seconds=12.5,
        source="billing_api",
        ledger_tsv=tmp_path / "l.tsv",
        rollup_tsv=tmp_path / "r.tsv",
    )
    assert row.source == "billing_api"


def test_rollup_schema_compatible_with_cap_gate(tmp_path: Path) -> None:
    """rollup TSV must remain readable by batch_runner.runcomfy_cost_check."""
    from scripts.image_generation import batch_runner

    led = tmp_path / "ledger.tsv"
    rol = tmp_path / "rollup.tsv"
    ledger.record_dispatch(
        batch_id="cap_probe", workflow_id="wf", gpu_seconds=50.0,
        ledger_tsv=led, rollup_tsv=rol,
    )
    info = batch_runner.runcomfy_cost_check(spend_path=rol, cooldown_usd=10.0)
    assert info["source_path"] == str(rol)
    assert info["spend_to_date_usd"] > 0
    assert info["cooldown"] is False  # well under $10


def test_cli_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = ledger.main(
        [
            "--batch-id", "cli_smoke",
            "--workflow-id", "flux_txt2img_manga",
            "--gpu-seconds", "30",
            "--dry-run",
        ],
    )
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["dry_run"] is True
    assert parsed["batch_id"] == "cli_smoke"
    assert parsed["est_usd"] > 0


def test_cli_writes_when_not_dry_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    led = tmp_path / "l.tsv"
    rol = tmp_path / "r.tsv"
    rc = ledger.main(
        [
            "--batch-id", "cli_real",
            "--workflow-id", "wf",
            "--gpu-seconds", "5",
            "--ledger-tsv", str(led),
            "--rollup-tsv", str(rol),
        ],
    )
    assert rc == 0
    rows = _read_tsv(led)
    assert len(rows) == 1
    assert rows[0]["batch_id"] == "cli_real"

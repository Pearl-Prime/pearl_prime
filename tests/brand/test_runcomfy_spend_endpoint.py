"""Tests for scripts.brand.runcomfy_spend_endpoint."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.brand.runcomfy_spend_endpoint import build_runcomfy_spend_payload
from scripts.brand.runcomfy_spend_endpoint import main as endpoint_main


def test_missing_tsv_graceful(tmp_path: Path) -> None:
    missing = tmp_path / "nope.tsv"
    p = build_runcomfy_spend_payload(spend_tsv=missing)
    assert p["tsv_present"] is False
    assert p["cumulative_month_spend_usd"] is None
    assert p["budget_warn_80pct"] is False
    assert p["utilization"] is None
    assert p["status"] == "no_tsv"
    assert p["parse_mode"] == "no_file"


def test_normative_cumulative_latest_by_date(tmp_path: Path) -> None:
    tsv = tmp_path / "runcomfy_monthly_spend.tsv"
    tsv.write_text(
        "date\tdispatched_jobs_today\tcumulative_month_spend_usd\n"
        "2026-05-01\t2\t4.0000\n"
        "2026-05-03\t1\t7.5000\n"
        "2026-05-02\t0\t6.0000\n",
        encoding="utf-8",
    )
    p = build_runcomfy_spend_payload(spend_tsv=tsv, monthly_budget_cap_usd=10.0)
    assert p["tsv_present"] is True
    assert p["cumulative_month_spend_usd"] == 7.5
    assert p["last_snapshot_date"] == "2026-05-03"
    assert p["parse_mode"] == "latest_cumulative_month_spend_usd"
    assert p["budget_warn_80pct"] is False
    assert p["status"] == "ok"


def test_warn_at_80_percent(tmp_path: Path) -> None:
    tsv = tmp_path / "runcomfy_monthly_spend.tsv"
    tsv.write_text(
        "date\tdispatched_jobs_today\tcumulative_month_spend_usd\n"
        "2026-05-04\t1\t8.0000\n",
        encoding="utf-8",
    )
    p = build_runcomfy_spend_payload(spend_tsv=tsv, monthly_budget_cap_usd=10.0)
    assert p["budget_warn_80pct"] is True
    assert p["status"] == "warn_80pct"
    assert p["utilization"] == 0.8


def test_incremental_spend_usd_sums(tmp_path: Path) -> None:
    tsv = tmp_path / "legacy.tsv"
    tsv.write_text("date\tspend_usd\n2026-05-01\t6.25\n2026-05-02\t3.75\n", encoding="utf-8")
    p = build_runcomfy_spend_payload(spend_tsv=tsv, monthly_budget_cap_usd=10.0)
    assert p["cumulative_month_spend_usd"] == 10.0
    assert p["parse_mode"] == "sum_incremental_usd"
    assert p["budget_warn_80pct"] is True


def test_cli_json_stdout(tmp_path: Path, capsysbinary) -> None:
    code = endpoint_main(
        [
            "--json",
            "--spend-tsv",
            str(tmp_path / "absent.tsv"),
            "--cap-usd",
            "10",
        ],
    )
    assert code == 0
    data = json.loads(capsysbinary.readouterr().out.decode("utf-8"))
    assert data["status"] == "no_tsv"

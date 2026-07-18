#!/usr/bin/env python3
"""Per-call RunComfy spend ledger (RUNCOMFY-SPEND-LEDGER-V1).

Pearl_Conductor v3 unattended runs require a real spend signal feeding the
``$10/mo`` cumulative cap gate in
``scripts/image_generation/batch_runner.runcomfy_cost_check``.

Two ingestion paths are supported:

* ``source=billing_api``  — vendor billing endpoint (HTTP 403 in current env
  per `artifacts/qa/batch_runner_activation_smoke_2026-05-10.md`; reserved for
  when token/account gains the documented scope).
* ``source=estimated``    — per-call estimation derived from wall-clock
  GPU-seconds × published per-second rate (default L40S Serverless).

The estimation path is conservative w.r.t. the cap: it over-counts wall time
vs. metered compute when queueing/transfer dominates, which is the safe
posture for an unattended cap gate.

Two artifacts are written:

* **`artifacts/finance/runcomfy_spend_ledger.tsv`** — append-only per-call
  rows with full provenance.
* **`artifacts/qa/runcomfy_monthly_spend.tsv`**     — existing daily rollup
  consumed by `batch_runner.runcomfy_cost_check` and the brand-admin endpoint.
  Each estimated append re-emits the latest cumulative row so the cap gate
  reads a current month-to-date number.

No RunComfy token is read, logged, or persisted by this module.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_LEDGER_TSV = REPO_ROOT / "artifacts" / "finance" / "runcomfy_spend_ledger.tsv"
DEFAULT_ROLLUP_TSV = REPO_ROOT / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"

# RunComfy Serverless GPU per-second rate, USD.
# Source: RunComfy public pricing — Serverless L40S tier
# (https://www.runcomfy.com/pricing — "Pay-as-you-go GPU seconds").
# Documented at docs/specs/RUNCOMFY_SPEND_LEDGER_V1_SPEC.md §3.
# Conservative: actual dashboard charge may differ; estimated rows flagged
# with ``source=estimated`` so reconciliation against the dashboard is auditable.
DEFAULT_PER_SECOND_USD = 0.000337  # ≈ $1.21 / GPU-hour, L40S baseline

DEFAULT_TZ = "America/Los_Angeles"

LEDGER_HEADER = [
    "timestamp_utc",
    "date_local",
    "batch_id",
    "workflow_id",
    "gpu_seconds",
    "est_usd",
    "cumulative_month_usd",
    "source",
    "rate_per_second_usd",
    "request_id",
]

_ROLLUP_HEADER = [
    "date",
    "dispatched_jobs_today",
    "cumulative_month_spend_usd",
]


# ── data structures ────────────────────────────────────────────────────


@dataclass(frozen=True)
class SpendRow:
    timestamp_utc: str
    date_local: str
    batch_id: str
    workflow_id: str
    gpu_seconds: float
    est_usd: float
    cumulative_month_usd: float
    source: str
    rate_per_second_usd: float
    request_id: str

    def as_dict(self) -> dict[str, str]:
        return {
            "timestamp_utc": self.timestamp_utc,
            "date_local": self.date_local,
            "batch_id": self.batch_id,
            "workflow_id": self.workflow_id,
            "gpu_seconds": f"{self.gpu_seconds:.3f}",
            "est_usd": f"{self.est_usd:.6f}",
            "cumulative_month_usd": f"{self.cumulative_month_usd:.6f}",
            "source": self.source,
            "rate_per_second_usd": f"{self.rate_per_second_usd:.6f}",
            "request_id": self.request_id,
        }


# ── estimation ─────────────────────────────────────────────────────────


def estimate_call_cost_usd(
    gpu_seconds: float,
    *,
    rate_per_second_usd: float = DEFAULT_PER_SECOND_USD,
) -> float:
    """Return ``gpu_seconds * rate_per_second_usd`` (clamped at 0)."""
    if gpu_seconds is None or gpu_seconds < 0:
        return 0.0
    if rate_per_second_usd <= 0:
        return 0.0
    return round(float(gpu_seconds) * float(rate_per_second_usd), 6)


# ── ledger I/O ─────────────────────────────────────────────────────────


def _read_ledger_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    buf = io.StringIO(text)
    reader = csv.DictReader(buf, delimiter="\t")
    return [dict(r) for r in reader if r]


def month_to_date_usd(
    rows: list[Mapping[str, Any]],
    *,
    as_of_date_local: str,
) -> float:
    """Sum ``est_usd`` of rows whose ``date_local`` falls in same ISO month."""
    if not as_of_date_local or len(as_of_date_local) < 7:
        return 0.0
    month_prefix = as_of_date_local[:7]  # "YYYY-MM"
    total = 0.0
    for r in rows:
        d = str(r.get("date_local", "")).strip()
        if not d.startswith(month_prefix):
            continue
        cell = str(r.get("est_usd", "")).strip().replace("$", "")
        if not cell:
            continue
        try:
            total += float(cell)
        except ValueError:
            continue
    return round(total, 6)


def record_dispatch(
    *,
    batch_id: str,
    workflow_id: str,
    gpu_seconds: float,
    source: str = "estimated",
    request_id: str = "",
    rate_per_second_usd: float = DEFAULT_PER_SECOND_USD,
    ledger_tsv: Path | None = None,
    rollup_tsv: Path | None = None,
    tz_name: str = DEFAULT_TZ,
    now: datetime | None = None,
) -> SpendRow:
    """Append one ledger row + refresh daily rollup.

    Returns the appended ``SpendRow``. Does not raise on empty paths;
    creates parent directories as needed.
    """
    if source not in ("estimated", "billing_api"):
        raise ValueError(
            f"source must be 'estimated' or 'billing_api'; got {source!r}",
        )
    ledger = ledger_tsv or DEFAULT_LEDGER_TSV
    rollup = rollup_tsv or DEFAULT_ROLLUP_TSV

    moment = now or datetime.now(ZoneInfo("UTC"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ZoneInfo("UTC"))
    local = moment.astimezone(ZoneInfo(tz_name))
    date_local = local.date().isoformat()
    ts_utc = moment.astimezone(ZoneInfo("UTC")).isoformat()

    est = estimate_call_cost_usd(gpu_seconds, rate_per_second_usd=rate_per_second_usd)

    prior_rows = _read_ledger_rows(ledger)
    prior_mtd = month_to_date_usd(prior_rows, as_of_date_local=date_local)
    cumulative = round(prior_mtd + est, 6)

    row = SpendRow(
        timestamp_utc=ts_utc,
        date_local=date_local,
        batch_id=str(batch_id or ""),
        workflow_id=str(workflow_id or ""),
        gpu_seconds=float(gpu_seconds or 0.0),
        est_usd=est,
        cumulative_month_usd=cumulative,
        source=source,
        rate_per_second_usd=float(rate_per_second_usd),
        request_id=str(request_id or ""),
    )

    _append_ledger_row(ledger, row)
    _refresh_rollup(
        rollup,
        date_local=date_local,
        cumulative_month_usd=cumulative,
        ledger_rows=prior_rows + [row.as_dict()],
    )
    return row


def _append_ledger_row(path: Path, row: SpendRow) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.is_file() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_HEADER, delimiter="\t", lineterminator="\n")
        if is_new:
            w.writeheader()
        w.writerow(row.as_dict())


def _refresh_rollup(
    path: Path,
    *,
    date_local: str,
    cumulative_month_usd: float,
    ledger_rows: list[Mapping[str, Any]],
) -> None:
    """Append a fresh daily rollup row reflecting today's cumulative spend.

    Schema preserved for ``batch_runner.runcomfy_cost_check`` compatibility:
    ``date \t dispatched_jobs_today \t cumulative_month_spend_usd`` — the cap
    gate reads only the latest ``cumulative_month_spend_usd``.
    """
    jobs_today = sum(
        1
        for r in ledger_rows
        if str(r.get("date_local", "")).strip() == date_local
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.is_file() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=_ROLLUP_HEADER, delimiter="\t", lineterminator="\n")
        if is_new:
            w.writeheader()
        w.writerow(
            {
                "date": date_local,
                "dispatched_jobs_today": str(int(jobs_today)),
                "cumulative_month_spend_usd": f"{cumulative_month_usd:.4f}",
            },
        )


# ── CLI ────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--batch-id", required=True)
    p.add_argument("--workflow-id", default="")
    p.add_argument("--gpu-seconds", type=float, required=True)
    p.add_argument(
        "--source",
        choices=["estimated", "billing_api"],
        default="estimated",
    )
    p.add_argument("--request-id", default="")
    p.add_argument(
        "--rate-per-second-usd",
        type=float,
        default=DEFAULT_PER_SECOND_USD,
        help="USD per GPU-second; default: RunComfy Serverless L40S baseline.",
    )
    p.add_argument("--ledger-tsv", type=Path, default=None)
    p.add_argument("--rollup-tsv", type=Path, default=None)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the would-be row to stdout WITHOUT writing.",
    )
    args = p.parse_args(argv)

    if args.dry_run:
        est = estimate_call_cost_usd(
            args.gpu_seconds,
            rate_per_second_usd=args.rate_per_second_usd,
        )
        out = {
            "dry_run": True,
            "batch_id": args.batch_id,
            "workflow_id": args.workflow_id,
            "gpu_seconds": args.gpu_seconds,
            "est_usd": est,
            "source": args.source,
            "rate_per_second_usd": args.rate_per_second_usd,
        }
        print(json.dumps(out, indent=2))
        return 0

    row = record_dispatch(
        batch_id=args.batch_id,
        workflow_id=args.workflow_id,
        gpu_seconds=args.gpu_seconds,
        source=args.source,
        request_id=args.request_id,
        rate_per_second_usd=args.rate_per_second_usd,
        ledger_tsv=args.ledger_tsv,
        rollup_tsv=args.rollup_tsv,
    )
    print(json.dumps(row.as_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

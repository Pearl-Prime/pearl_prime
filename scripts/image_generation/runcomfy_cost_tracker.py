#!/usr/bin/env python3
"""Daily RunComfy billing poll → ``artifacts/qa/runcomfy_monthly_spend.tsv``.

Normative billing URL (vendor contract): GET
``https://api.runcomfy.com/v1/account/billing/summary`` (see
``docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md`` §4.D).

``dry_run=True`` never performs HTTP and returns deterministic mock metrics.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.error
import urllib.request
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SPEND_TSV = REPO_ROOT / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"
_BILLING_URL = "https://api.runcomfy.com/v1/account/billing/summary"
_COOLDOWN_USD = 25.0  # TEMPORARY: RunComfy deprecation burn — restore to 10.0 after closure
_WARN_USD = 20.0  # TEMPORARY: bumped from 8.0 alongside cap raise
_TZ_DEFAULT = "America/Los_Angeles"


def _tsv_header() -> list[str]:
    return ["date", "dispatched_jobs_today", "cumulative_month_spend_usd"]


def read_latest_cumulative_spend_usd(path: Path) -> float:
    """Return the last non-empty ``cumulative_month_spend_usd`` in the TSV."""
    if not path.is_file():
        return 0.0
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return 0.0
    buf = io.StringIO(text)
    reader = csv.DictReader(buf, delimiter="\t")
    if reader.fieldnames is None:
        return 0.0
    fields = [f.strip() for f in reader.fieldnames]
    if "cumulative_month_spend_usd" not in fields:
        return 0.0
    last = 0.0
    for row in reader:
        cell = (row.get("cumulative_month_spend_usd") or "").strip().replace("$", "")
        if not cell:
            continue
        try:
            last = float(cell)
        except ValueError:
            continue
    return last


def append_spend_row(
    path: Path,
    *,
    date_iso: str,
    dispatched_jobs_today: int,
    cumulative_month_spend_usd: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.is_file() or path.stat().st_size == 0
    row = {
        "date": date_iso,
        "dispatched_jobs_today": str(int(dispatched_jobs_today)),
        "cumulative_month_spend_usd": f"{cumulative_month_spend_usd:.4f}",
    }
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=_tsv_header(), delimiter="\t", lineterminator="\n")
        if is_new:
            w.writeheader()
        w.writerow(row)


def poll_billing(
    *,
    dry_run: bool = True,
    spend_tsv: Path | None = None,
    tz_name: str = _TZ_DEFAULT,
) -> dict[str, Any]:
    """Fetch vendor billing summary or return mock payload when ``dry_run``."""
    path = spend_tsv or _DEFAULT_SPEND_TSV
    now = datetime.now(ZoneInfo(tz_name))
    date_iso = now.date().isoformat()

    if dry_run:
        mock_spend = 3.25
        cooldown = mock_spend >= _COOLDOWN_USD
        warn = mock_spend >= _WARN_USD
        return {
            "dry_run": True,
            "billing_url": _BILLING_URL,
            "date_local": date_iso,
            "timezone": tz_name,
            "cumulative_month_spend_usd": mock_spend,
            "usage_images_completed_mock": 12,
            "cooldown": cooldown,
            "budget_warn": warn,
            "spend_tsv": str(path),
            "notes": "Mock vendor response; no HTTP request performed.",
        }

    # Production path (not exercised in Pearl_Int dry-run wiring session).
    from scripts.image_generation.runcomfy_dispatch import load_token

    token = load_token(require=True)
    request = urllib.request.Request(
        _BILLING_URL,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 404):
            print("BILLING_FALLBACK_MANUAL: billing API unavailable", file=sys.stderr)
        raise
    accrued = float(payload.get("spend", {}).get("accrued_usd", 0.0))
    usage = int(payload.get("usage_images", {}).get("completed", 0))
    cooldown = accrued >= _COOLDOWN_USD
    warn = accrued >= _WARN_USD
    if warn and not cooldown:
        print("BUDGET_WARN: RunComfy accrued spend >= $8 (80% soft cap)", file=sys.stderr)
    return {
        "dry_run": False,
        "billing_url": _BILLING_URL,
        "date_local": date_iso,
        "timezone": tz_name,
        "cumulative_month_spend_usd": round(accrued, 4),
        "usage_images_completed": usage,
        "cooldown": cooldown,
        "budget_warn": warn,
        "raw_keys": sorted(payload.keys()),
        "spend_tsv": str(path),
    }


def update_spend_tsv_from_poll(result: Mapping[str, Any], *, spend_tsv: Path | None = None) -> None:
    """Append one rollup row from a ``poll_billing`` result dict."""
    path = spend_tsv or _DEFAULT_SPEND_TSV
    date_iso = str(result.get("date_local", ""))
    jobs = int(result.get("usage_images_completed", result.get("usage_images_completed_mock", 0)))
    spend = float(result.get("cumulative_month_spend_usd", 0.0))
    append_spend_row(path, date_iso=date_iso, dispatched_jobs_today=jobs, cumulative_month_spend_usd=spend)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--poll", action="store_true", help="Run billing poll path")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit mock poll (default when --live is omitted)",
    )
    p.add_argument(
        "--live",
        action="store_true",
        help="Call RunComfy billing HTTP API (default: mock / no network)",
    )
    p.add_argument(
        "--write-tsv",
        action="store_true",
        help="Append a TSV row from poll output (uses mock spend when --dry-run)",
    )
    p.add_argument("--spend-tsv", type=Path, default=None, help="Override spend TSV path")
    args = p.parse_args(argv)
    if not args.poll:
        p.error("--poll is required")
    if args.live and args.dry_run:
        p.error("--live and --dry-run are mutually exclusive")
    try:
        out = poll_billing(dry_run=not args.live, spend_tsv=args.spend_tsv)
    except Exception as e:  # noqa: BLE001 — CLI surface
        print(str(e), file=sys.stderr)
        return 2
    if args.write_tsv:
        update_spend_tsv_from_poll(out, spend_tsv=args.spend_tsv)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

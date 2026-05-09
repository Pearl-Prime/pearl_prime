#!/usr/bin/env python3
"""
JSON helper for Brand Admin RunComfy monthly spend (IMG-RENDER-DUAL-PATH-V1-01).

Reads ``artifacts/qa/runcomfy_monthly_spend.tsv`` when present (Pearl_Int writer).
Mirrors **80% budget warn** posture vs ``monthly_budget_cap_usd`` (default ``$10``
soft cap per program spec).

Usage:
  PYTHONPATH=. python3 scripts/brand/runcomfy_spend_endpoint.py --json
  PYTHONPATH=. python3 scripts/brand/runcomfy_spend_endpoint.py --serve --port 8766
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEND_TSV = REPO_ROOT / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"
DEFAULT_MONTHLY_CAP_USD = 10.0
WARN_THRESHOLD_RATIO = 0.8
JSON_ROUTE = "/runcomfy-monthly-spend.json"


def _parse_float_cell(cell: str) -> float | None:
    s = cell.strip().replace("$", "").replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _spend_from_normative_cumulative(rows: list[list[str]], header: list[str]) -> tuple[float, str | None]:
    """Latest ``cumulative_month_spend_usd`` by ``date`` (ISO); else last data row."""
    h = [c.strip().lower() for c in header]
    if "cumulative_month_spend_usd" not in h:
        return 0.0, None
    ic = h.index("cumulative_month_spend_usd")
    idate = h.index("date") if "date" in h else None
    parsed: list[tuple[str | None, float]] = []
    for row in rows[1:]:
        if not row or ic >= len(row):
            continue
        v = _parse_float_cell(row[ic])
        if v is None:
            continue
        dkey: str | None = None
        if idate is not None and idate < len(row):
            dkey = row[idate].strip() or None
        parsed.append((dkey, v))
    if not parsed:
        return 0.0, None
    if all(p[0] for p in parsed):
        parsed.sort(key=lambda x: x[0] or "")
    last_date, spend = parsed[-1]
    return spend, last_date


def _spend_from_incremental_usd(rows: list[list[str]], header: list[str]) -> float:
    """Sum ``spend_usd`` / ``amount_usd`` columns (legacy / test-friendly)."""
    h = [c.strip().lower() for c in header]
    if "spend_usd" in h:
        idx = h.index("spend_usd")
    elif "amount_usd" in h:
        idx = h.index("amount_usd")
    else:
        idx = len(h) - 1
    total = 0.0
    for row in rows[1:]:
        if not row or idx >= len(row):
            continue
        v = _parse_float_cell(row[idx])
        if v is not None:
            total += v
    return total


def parse_monthly_spend_tsv(text: str) -> dict[str, Any]:
    """Parse TSV body; never raises for malformed rows."""
    buf = io.StringIO(text)
    reader = csv.reader(buf, delimiter="\t")
    rows = [r for r in reader if any(c.strip() for c in r)]
    if not rows:
        return {
            "cumulative_month_spend_usd": 0.0,
            "last_snapshot_date": None,
            "parse_mode": "empty",
        }
    header = rows[0]
    hlow = [c.strip().lower() for c in header]
    if any("usd" in x or "spend" in x for x in hlow) and "cumulative_month_spend_usd" not in hlow:
        return {
            "cumulative_month_spend_usd": round(_spend_from_incremental_usd(rows, header), 4),
            "last_snapshot_date": None,
            "parse_mode": "sum_incremental_usd",
        }
    spend, last_d = _spend_from_normative_cumulative(rows, header)
    if "cumulative_month_spend_usd" in hlow:
        return {
            "cumulative_month_spend_usd": round(spend, 4),
            "last_snapshot_date": last_d,
            "parse_mode": "latest_cumulative_month_spend_usd",
        }
    # No recognizable header: try last-column floats (append-only daily numbers).
    total = 0.0
    for row in rows:
        if not row:
            continue
        v = _parse_float_cell(row[-1])
        if v is not None:
            total += v
    return {
        "cumulative_month_spend_usd": round(total, 4),
        "last_snapshot_date": None,
        "parse_mode": "heuristic_last_column_sum",
    }


def build_runcomfy_spend_payload(
    *,
    spend_tsv: Path | None = None,
    monthly_budget_cap_usd: float = DEFAULT_MONTHLY_CAP_USD,
    warn_threshold_ratio: float = WARN_THRESHOLD_RATIO,
) -> dict[str, Any]:
    path = spend_tsv or DEFAULT_SPEND_TSV
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    if not path.is_file():
        return {
            "schema_version": 1,
            "generated_at": generated_at,
            "tsv_path": str(path.resolve()),
            "tsv_present": False,
            "cumulative_month_spend_usd": None,
            "monthly_budget_cap_usd": monthly_budget_cap_usd,
            "warn_threshold_ratio": warn_threshold_ratio,
            "utilization": None,
            "budget_warn_80pct": False,
            "last_snapshot_date": None,
            "parse_mode": "no_file",
            "status": "no_tsv",
        }

    raw = path.read_text(encoding="utf-8")
    parsed = parse_monthly_spend_tsv(raw)
    spend = float(parsed["cumulative_month_spend_usd"])
    cap = float(monthly_budget_cap_usd)
    util = (spend / cap) if cap > 0 else None
    warn_line = cap * warn_threshold_ratio
    warn = cap > 0 and spend >= warn_line
    status = "warn_80pct" if warn else "ok"
    if parsed.get("parse_mode") == "empty":
        status = "no_rows"

    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "tsv_path": str(path.resolve()),
        "tsv_present": True,
        "cumulative_month_spend_usd": spend,
        "monthly_budget_cap_usd": cap,
        "warn_threshold_ratio": warn_threshold_ratio,
        "utilization": round(util, 4) if util is not None else None,
        "budget_warn_80pct": warn,
        "last_snapshot_date": parsed.get("last_snapshot_date"),
        "parse_mode": parsed.get("parse_mode"),
        "status": status,
    }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def make_handler(repo_root: Path):
    spend_path = repo_root / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

        def do_GET(self) -> None:  # noqa: N802
            if self.path.split("?", 1)[0] != JSON_ROUTE:
                self.send_error(404, "Not Found")
                return
            body = _json_bytes(build_runcomfy_spend_payload(spend_tsv=spend_path))
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--json", action="store_true", help="Write snapshot JSON to stdout")
    mode.add_argument("--serve", action="store_true", help="Run local JSON HTTP endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--spend-tsv", type=Path, default=None)
    parser.add_argument("--cap-usd", type=float, default=DEFAULT_MONTHLY_CAP_USD)

    args = parser.parse_args(argv)
    repo = args.repo_root.resolve() if args.repo_root else REPO_ROOT
    spend = args.spend_tsv.resolve() if args.spend_tsv else repo / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"

    if args.json:
        payload = build_runcomfy_spend_payload(
            spend_tsv=spend,
            monthly_budget_cap_usd=args.cap_usd,
        )
        sys.stdout.buffer.write(_json_bytes(payload))
        return 0

    if args.serve:
        handler = make_handler(repo)
        server = HTTPServer((args.host, args.port), handler)
        url = f"http://{args.host}:{args.port}{JSON_ROUTE}"
        print(f"Serving {url} (Ctrl+C to stop)", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
HTTP/JSON helper for Brand Admin weekly packaging (WORLDWIDE-CATALOG-GO-LIVE-V1 P2 surface 3).

Reads ``artifacts/coordination/weekly_packages_<YYYY-MM-DD>.tsv`` where the date is the
**Monday** (ISO week) anchor for that coordination drop. Joins rows with **active** brands
from ``ActiveBrandClassifier`` (PR #972). If the TSV is missing, responds with an empty
JSON object ``{}``.

Usage:
  PYTHONPATH=. python3 scripts/brand/weekly_package_endpoint.py --json
  PYTHONPATH=. python3 scripts/brand/weekly_package_endpoint.py --serve --port 8767
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from scripts.brand.active_brand_classifier import ActiveBrandClassifier

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COORD_DIR = REPO_ROOT / "artifacts" / "coordination"
JSON_ROUTE = "/weekly-package-status.json"


def iso_week_monday(d: date) -> date:
    """Monday (ISO) for the calendar week containing ``d``."""
    return d - timedelta(days=d.weekday())


@dataclass
class _BrandRollup:
    ready_count: int = 0
    pending_count: int = 0
    error_count: int = 0
    ready_urls: list[str] = field(default_factory=list)
    last_updated: list[str] = field(default_factory=list)


def _norm_status(cell: str) -> str:
    s = (cell or "").strip().lower()
    if s in ("ready", "pending", "error"):
        return s
    if not s:
        return "pending"
    return "pending"


def parse_weekly_packages_tsv(text: str) -> dict[str, _BrandRollup]:
    """Parse TSV; malformed rows are skipped. Header names are matched case-insensitively."""
    buf = io.StringIO(text)
    reader = csv.reader(buf, delimiter="\t")
    rows = [r for r in reader if any((c or "").strip() for c in r)]
    if not rows:
        return {}
    header = [h.strip().lower() for h in rows[0]]
    try:
        ic_brand = header.index("brand_id")
    except ValueError:
        return {}
    ic_status = header.index("status") if "status" in header else -1
    ic_url = header.index("download_url") if "download_url" in header else -1
    ic_lu = header.index("last_updated") if "last_updated" in header else -1

    out: dict[str, _BrandRollup] = {}
    for row in rows[1:]:
        if ic_brand >= len(row):
            continue
        bid = (row[ic_brand] or "").strip()
        if not bid:
            continue
        st_raw = row[ic_status].strip() if ic_status >= 0 and ic_status < len(row) else ""
        st = _norm_status(st_raw)
        url = ""
        if ic_url >= 0 and ic_url < len(row):
            url = (row[ic_url] or "").strip()
        lu = ""
        if ic_lu >= 0 and ic_lu < len(row):
            lu = (row[ic_lu] or "").strip()

        roll = out.setdefault(bid, _BrandRollup())
        if st == "ready":
            roll.ready_count += 1
            if url:
                roll.ready_urls.append(url)
        elif st == "pending":
            roll.pending_count += 1
        elif st == "error":
            roll.error_count += 1
        if lu:
            roll.last_updated.append(lu)
    return out


def _rollup_to_payload(roll: _BrandRollup) -> dict[str, Any]:
    if roll.error_count:
        status = "error"
    elif roll.pending_count:
        status = "pending"
    elif roll.ready_count and not roll.pending_count and not roll.error_count:
        status = "ready"
    else:
        status = "pending"
    last = None
    if roll.last_updated:
        last = max(roll.last_updated)
    dl: str | None = None
    if status == "ready" and roll.ready_urls:
        dl = roll.ready_urls[0]
    return {
        "status": status,
        "ready_count": roll.ready_count,
        "pending_count": roll.pending_count,
        "last_updated": last,
        **({"download_url": dl} if dl else {}),
    }


def weekly_packages_tsv_path(coord_dir: Path, week_monday: date) -> Path:
    return coord_dir / f"weekly_packages_{week_monday.isoformat()}.tsv"


def build_weekly_package_status_payload(
    classifier: ActiveBrandClassifier,
    *,
    coord_dir: Path,
    week_monday: date,
) -> dict[str, Any]:
    """
    Return ``{ brand_id: { status, ready_count, pending_count, last_updated, download_url? } }``.

    If the coordination TSV for ``week_monday`` is missing, returns ``{}`` (no keys).
    """
    tsv_path = weekly_packages_tsv_path(coord_dir, week_monday)
    if not tsv_path.is_file():
        return {}
    try:
        text = tsv_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    by_brand = parse_weekly_packages_tsv(text)
    active_ids = sorted(classifier.list_active())
    out: dict[str, Any] = {}
    for bid in active_ids:
        roll = by_brand.get(bid) or _BrandRollup()
        out[bid] = _rollup_to_payload(roll)
    return out


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def make_handler(classifier: ActiveBrandClassifier, coord_dir: Path, week_monday: date):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

        def do_GET(self) -> None:  # noqa: N802
            path_only = self.path.split("?", 1)[0]
            if path_only != JSON_ROUTE:
                self.send_error(404, "Not Found")
                return
            payload = build_weekly_package_status_payload(
                classifier,
                coord_dir=coord_dir,
                week_monday=week_monday,
            )
            body = _json_bytes(payload)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def _parse_week_monday(s: str) -> date:
    return date.fromisoformat(s.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly package status JSON for Brand Admin")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--json", action="store_true", help="Write JSON to stdout")
    mode.add_argument("--serve", action="store_true", help="Run local HTTP endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--wizard-dir", type=Path, default=None)
    parser.add_argument("--coord-dir", type=Path, default=None)
    parser.add_argument(
        "--week-monday",
        type=str,
        default=None,
        help="Override ISO date (Monday) for filename; default = Monday of current UTC week",
    )
    parser.add_argument(
        "--reference-utc",
        type=str,
        default=None,
        help="ISO datetime (UTC) for computing default week Monday (tests)",
    )

    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve() if args.repo_root else None
    wizard_dir = args.wizard_dir.resolve() if args.wizard_dir else None
    coord_dir = (args.coord_dir or DEFAULT_COORD_DIR).resolve()

    if args.reference_utc:
        ref = datetime.fromisoformat(args.reference_utc.replace("Z", "+00:00"))
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)
        wk = iso_week_monday(ref.astimezone(timezone.utc).date())
    elif args.week_monday:
        wk = _parse_week_monday(args.week_monday)
    else:
        wk = iso_week_monday(datetime.now(tz=timezone.utc).date())

    classifier = ActiveBrandClassifier(repo_root=repo_root, wizard_yaml_dir=wizard_dir)

    if args.json:
        payload = build_weekly_package_status_payload(classifier, coord_dir=coord_dir, week_monday=wk)
        sys.stdout.buffer.write(_json_bytes(payload))
        return 0

    if args.serve:
        handler = make_handler(classifier, coord_dir=coord_dir, week_monday=wk)
        server = HTTPServer((args.host, args.port), handler)
        url = f"http://{args.host}:{args.port}{JSON_ROUTE}"
        print(f"Serving {url} (week {wk.isoformat()} TSV; Ctrl+C to stop)", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

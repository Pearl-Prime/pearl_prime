#!/usr/bin/env python3
"""
HTTP/JSON helper for Brand Admin active/inactive panel (ACTIVE_BRAND_SSOT consumer).

Cap: WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01. Serves a JSON snapshot built from
``ActiveBrandClassifier`` (PR #972); does not change classifier logic.

Usage:
  PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --json
  PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --serve --port 8765
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from scripts.brand.active_brand_classifier import (
    ActiveBrandClassifier,
    manga_canonical_brand_ids,
    summarize_manga_slice,
)


def _wizard_mtime_iso(classifier: ActiveBrandClassifier, brand_id: str) -> str | None:
    """UTC ISO-8601 from brand_wizard YAML mtime; proxy for last wizard materialization."""
    path = classifier.wizard_yaml_dir / f"{brand_id}.yaml"
    if not path.is_file():
        return None
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def build_dashboard_payload(classifier: ActiveBrandClassifier) -> dict[str, Any]:
    """JSON-serializable snapshot for the Brand Admin panel."""
    snap = classifier.snapshot()
    manga_ids = set(manga_canonical_brand_ids(classifier.repo_root))
    ma, mi, mt = summarize_manga_slice(classifier)

    by_region: dict[str, dict[str, int]] = {
        "manga_canonical": {"active": 0, "inactive": 0, "total": 0},
        "other_registry": {"active": 0, "inactive": 0, "total": 0},
    }

    brands: list[dict[str, Any]] = []
    for bid in sorted(snap.keys()):
        st = snap[bid]
        region = "manga_canonical" if bid in manga_ids else "other_registry"
        by_region[region]["total"] += 1
        if st.active:
            by_region[region]["active"] += 1
        else:
            by_region[region]["inactive"] += 1

        row: dict[str, Any] = {
            "brand_id": bid,
            "status": "active" if st.active else "inactive",
            "reason": "" if st.active else (st.reason or "inactive"),
            "last_wizard_run": _wizard_mtime_iso(classifier, bid) if st.active else None,
            "region": region,
        }
        brands.append(row)

    active_n = sum(1 for b in brands if b["status"] == "active")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "totals": {
            "active": active_n,
            "inactive": len(brands) - active_n,
            "universe": len(brands),
        },
        "locale_breakdown": None,
        "manga_canonical_slice": {"active": ma, "inactive": mi, "total": mt},
        "by_region": by_region,
        "music_registry_deferred": classifier.music_registry_deferred,
        "brands": brands,
    }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def make_handler(classifier: ActiveBrandClassifier):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

        def do_GET(self) -> None:  # noqa: N802
            if self.path.split("?", 1)[0] != "/active-brand-dashboard.json":
                self.send_error(404, "Not Found")
                return
            body = _json_bytes(build_dashboard_payload(classifier))
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Active brand dashboard JSON helper")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--json", action="store_true", help="Write snapshot JSON to stdout")
    mode.add_argument("--serve", action="store_true", help="Run local JSON HTTP endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--wizard-dir", type=Path, default=None)

    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve() if args.repo_root else None
    wizard_dir = args.wizard_dir.resolve() if args.wizard_dir else None
    classifier = ActiveBrandClassifier(repo_root=repo_root, wizard_yaml_dir=wizard_dir)

    if args.json:
        sys.stdout.buffer.write(_json_bytes(build_dashboard_payload(classifier)))
        return 0

    if args.serve:
        handler = make_handler(classifier)
        server = HTTPServer((args.host, args.port), handler)
        url = f"http://{args.host}:{args.port}/active-brand-dashboard.json"
        print(f"Serving {url} (Ctrl+C to stop)", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

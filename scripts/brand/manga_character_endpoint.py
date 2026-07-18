#!/usr/bin/env python3
"""
HTTP/JSON helper for Brand Admin manga main-character panel (Phase 2 P0).

Reads Pearl_PM worldwide catalog plan TSV when present and resolves character
PNGs under ``artifacts/manga/`` (inventory layout per PR #988 / manga catalog).

Usage:
  PYTHONPATH=. python3 scripts/brand/manga_character_endpoint.py --json
  PYTHONPATH=. python3 scripts/brand/manga_character_endpoint.py --serve --port 8768
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from scripts.brand.active_brand_classifier import ActiveBrandClassifier

# Pearl_PM drop (fixed date stamp; parallel session may add/rename — see glob fallback).
CATALOG_PLAN_EN_TSV = Path("artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv")
CATALOG_PLAN_JA_TSV = Path("artifacts/catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv")
CATALOG_PLAN_GLOB = "worldwide_catalog_plan_*_*.tsv"

LOCALES_ORDER: tuple[str, str] = ("en_US", "ja_JP")

_BRAND_KEYS: tuple[str, ...] = ("brand_id", "brand")
_SERIES_KEYS: tuple[str, ...] = ("series_id", "series_slug")
_LOCALE_KEYS: tuple[str, ...] = ("locale", "market_locale", "locale_id")


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def _cell(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row:
            v = (row.get(k) or "").strip()
            if v:
                return v
    return ""


def _normalize_headers(raw: list[str]) -> dict[str, str]:
    """Map normalized header -> original key used in row dict."""
    out: dict[str, str] = {}
    for h in raw:
        key = h.strip()
        nk = re.sub(r"\s+", "_", key.lower())
        out[nk] = key
    return out


def _parse_tsv(path: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        return [], {}
    reader = csv.reader(lines, delimiter="\t")
    try:
        header_row = next(reader)
    except StopIteration:
        return [], {}
    norm = _normalize_headers(header_row)
    rows: list[dict[str, str]] = []
    for parts in reader:
        if not parts or all(not (c or "").strip() for c in parts):
            continue
        row: dict[str, str] = {}
        for i, cell in enumerate(parts):
            if i < len(header_row):
                row[header_row[i].strip()] = cell.strip()
        rows.append(row)
    return rows, norm


def _locale_from_filename(path: Path) -> str | None:
    m = re.search(r"worldwide_catalog_plan_(en_US|ja_JP)_", path.name)
    if m:
        return m.group(1)
    return None


def _row_locale(row: dict[str, str], header_norm: dict[str, str], default: str) -> str:
    for lk in _LOCALE_KEYS:
        nk = lk.lower()
        orig = header_norm.get(nk)
        if orig and row.get(orig, "").strip():
            loc = row[orig].strip()
            if loc in LOCALES_ORDER:
                return loc
    return default


def _row_brand(row: dict[str, str], header_norm: dict[str, str]) -> str:
    for bk in _BRAND_KEYS:
        orig = header_norm.get(bk.lower())
        if orig:
            v = row.get(orig, "").strip()
            if v:
                return v
    return ""


def _row_series(row: dict[str, str], header_norm: dict[str, str]) -> str:
    for sk in _SERIES_KEYS:
        orig = header_norm.get(sk.lower())
        if orig:
            v = row.get(orig, "").strip()
            if v:
                return v
    return ""


def _catalog_plan_paths(repo_root: Path) -> list[Path]:
    """Fixed-date Pearl_PM paths first, then any ``worldwide_catalog_plan_*_*.tsv`` (deduped)."""
    root = repo_root.resolve()
    out: list[Path] = []
    seen: set[Path] = set()
    for rel in (CATALOG_PLAN_EN_TSV, CATALOG_PLAN_JA_TSV):
        p = (root / rel).resolve()
        if p.is_file() and p not in seen:
            seen.add(p)
            out.append(p)
    cat_dir = root / "artifacts" / "catalog"
    if cat_dir.is_dir():
        for p in sorted(cat_dir.glob(CATALOG_PLAN_GLOB)):
            rp = p.resolve()
            if rp.is_file() and rp not in seen:
                seen.add(rp)
                out.append(p)
    return out


def load_series_index(repo_root: Path) -> tuple[dict[str, dict[str, set[str]]], bool]:
    """
    Returns (index, any_tsv_read) where index[brand_id][locale] = set of series_id.
    any_tsv_read is True if at least one catalog plan file existed and was parsed (even if empty).
    """
    root = repo_root.resolve()
    index: dict[str, dict[str, set[str]]] = {}
    any_read = False
    for path in _catalog_plan_paths(root):
        if not path.is_file():
            continue
        any_read = True
        default_loc = _locale_from_filename(path) or "en_US"
        rows, header_norm = _parse_tsv(path)
        for row in rows:
            bid = _row_brand(row, header_norm)
            sid = _row_series(row, header_norm)
            if not bid or not sid:
                continue
            loc = _row_locale(row, header_norm, default_loc)
            if loc not in LOCALES_ORDER:
                continue
            index.setdefault(bid, {}).setdefault(loc, set()).add(sid)
    return index, any_read


def resolve_main_character_path(repo_root: Path, brand_id: str, series_id: str, locale: str) -> tuple[str | None, str]:
    """
    Return (repo-relative posix path or None, status ready|missing).

    Resolution order matches inventory under ``artifacts/manga/`` (locale segment
    per manga catalog CSV) then fallbacks including brand-level ``main_character.png``.
    """
    root = repo_root.resolve()
    candidates = [
        root / "artifacts" / "manga" / locale / brand_id / series_id / "main_character.png",
        root / "artifacts" / "manga" / brand_id / series_id / "main_character.png",
        root / "artifacts" / "manga" / brand_id / "main_character.png",
    ]
    for full in candidates:
        try:
            full = full.resolve()
        except OSError:
            continue
        if full.is_file():
            try:
                rel = full.relative_to(root).as_posix()
            except ValueError:
                rel = str(full)
            return rel, "ready"
    return None, "missing"


def build_manga_character_panel_payload(
    classifier: ActiveBrandClassifier,
    *,
    series_index: dict[str, dict[str, set[str]]] | None = None,
) -> dict[str, Any]:
    """JSON for ``/manga-character-panel.json`` (active brands × locales × series)."""
    root = classifier.repo_root.resolve()
    if series_index is None:
        series_index, _seen = load_series_index(root)

    snap = classifier.snapshot()
    active_brands = sorted(bid for bid, st in snap.items() if st.active)

    body: dict[str, Any] = {}
    for bid in active_brands:
        body[bid] = {}
        per_loc_src = series_index.get(bid, {})
        for loc in LOCALES_ORDER:
            sids = sorted(per_loc_src.get(loc, set()))
            series_list: list[dict[str, Any]] = []
            for sid in sids:
                path, status = resolve_main_character_path(root, bid, sid, loc)
                series_list.append(
                    {
                        "series_id": sid,
                        "main_character_image_path": path,
                        "status": status,
                    }
                )
            body[bid][loc] = {"series": series_list}

    return body


def make_handler(classifier: ActiveBrandClassifier):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: object) -> None:
            sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

        def do_GET(self) -> None:  # noqa: N802
            if self.path.split("?", 1)[0] != "/manga-character-panel.json":
                self.send_error(404, "Not Found")
                return
            body = _json_bytes(build_manga_character_panel_payload(classifier))
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manga character panel JSON helper")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--json", action="store_true", help="Write snapshot JSON to stdout")
    mode.add_argument("--serve", action="store_true", help="Run local JSON HTTP endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--wizard-dir", type=Path, default=None)

    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve() if args.repo_root else None
    wizard_dir = args.wizard_dir.resolve() if args.wizard_dir else None
    classifier = ActiveBrandClassifier(repo_root=repo_root, wizard_yaml_dir=wizard_dir)

    if args.json:
        sys.stdout.buffer.write(_json_bytes(build_manga_character_panel_payload(classifier)))
        return 0

    if args.serve:
        handler = make_handler(classifier)
        server = HTTPServer((args.host, args.port), handler)
        url = f"http://{args.host}:{args.port}/manga-character-panel.json"
        print(f"Serving {url} (Ctrl+C to stop)", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

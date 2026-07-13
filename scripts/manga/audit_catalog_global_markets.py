#!/usr/bin/env python3
"""Inventory manga catalog, brand, locale, and global-market plans."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import yaml

TEXT_TYPES = {".json", ".yaml", ".yml"}


def _load(path: Path) -> Any:
    try:
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _walk(value: Any, path: Path, rows: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        keys = set(value)
        if keys & {
            "market", "market_id", "locale", "locale_id", "brand_id",
            "target_audience", "genre_shell", "proof_status", "production_owner",
        }:
            rows.append({
                "source": str(path),
                "market": value.get("market") or value.get("market_id") or "",
                "locale": value.get("locale") or value.get("locale_id") or "",
                "brand_id": value.get("brand_id") or "",
                "target_audience": value.get("target_audience") or value.get("audience") or "",
                "genre_shell": value.get("genre_shell") or value.get("genre_id") or value.get("genre") or "",
                "topic_embed_strategy": (
                    value.get("topic_embed_strategy")
                    or value.get("subtle_embed_strategy")
                    or value.get("topic")
                    or ""
                ),
                "reading_format": value.get("reading_format") or value.get("format") or "",
                "proof_status": value.get("proof_status") or "",
                "production_owner": value.get("production_owner") or value.get("owner") or "",
            })
        for child in value.values():
            _walk(child, path, rows)
    elif isinstance(value, list):
        for child in value:
            _walk(child, path, rows)


def audit(repo_root: Path) -> dict[str, Any]:
    candidates: list[Path] = []
    for base in (
        repo_root / "config" / "manga",
        repo_root / "config" / "brands",
        repo_root / "docs",
        repo_root / "artifacts" / "analysis",
    ):
        if base.exists():
            candidates.extend(
                path for path in base.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_TYPES
            )
    rows: list[dict[str, Any]] = []
    for path in sorted(set(candidates)):
        value = _load(path)
        if value is not None:
            _walk(value, path, rows)

    unique_markets = sorted({
        str(row["market"]).strip()
        for row in rows
        if str(row["market"]).strip()
    })
    unique_locales = sorted({
        str(row["locale"]).strip()
        for row in rows
        if str(row["locale"]).strip()
    })
    required = (
        "target_audience", "genre_shell", "topic_embed_strategy",
        "locale", "reading_format", "proof_status", "production_owner",
    )
    incomplete = [
        row for row in rows
        if any(not str(row.get(field) or "").strip() for field in required)
    ]
    return {
        "manga-global-market-count": len(unique_markets),
        "locale_count": len(unique_locales),
        "markets": unique_markets,
        "locales": unique_locales,
        "catalog_row_count": len(rows),
        "incomplete_row_count": len(incomplete),
        "manga-catalog-coverage": (
            "green" if rows and not incomplete else ("partial" if rows else "blocked")
        ),
        "manga-brand-plan-coverage": (
            "green"
            if rows and all(str(row.get("brand_id") or "").strip() for row in rows)
            else ("partial" if rows else "blocked")
        ),
        "claimed_14_markets_verified": len(unique_markets) == 14,
        "overall-manga-green": "NOT_PROVEN",
        "rows": rows,
    }


def write_matrix(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "source", "market", "locale", "brand_id", "target_audience",
        "genre_shell", "topic_embed_strategy", "reading_format",
        "proof_status", "production_owner",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--matrix", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report = audit(args.repo_root)
    write_matrix(args.matrix, report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["claimed_14_markets_verified"] and report["incomplete_row_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

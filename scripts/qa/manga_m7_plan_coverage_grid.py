#!/usr/bin/env python3
"""M7 plan-coverage conformance grid — read-only locale rollout audit.

Reads live SSOT series plans, locale_genre_allocations.yaml, and
format_routing.yaml. Emits a TSV grid for operator memos / M7 closeout.

No LLM calls. No plan mutation.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SERIES_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"
ALLOC_PATH = REPO / "config" / "manga" / "locale_genre_allocations.yaml"
ROUTING_PATH = REPO / "config" / "manga" / "format_routing.yaml"
CATALOG_SSOT = REPO / "artifacts" / "catalog" / "manga" / "ssot_rollup"

KO_KR_HOLD = "hold_pending_market_clearance (Q-MANGA-05)"
WAVE_A_ZERO = (
    "fr_FR", "pt_BR", "de_DE", "es_ES", "es_US", "it_IT", "hu_HU", "zh_SG", "zh_HK",
)
SHIPPED = ("en_US", "ja_JP", "zh_TW", "zh_CN")

COLUMNS = [
    "locale",
    "series_plans",
    "allocation",
    "format_routing",
    "catalog_ssot_csv",
    "wave_a_lane",
    "grid_cell",
    "blockers",
]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _plan_count(locale: str) -> int:
    d = SERIES_ROOT / locale
    if not d.is_dir():
        return 0
    return len(list(d.glob("*.yaml")))


def _has_routing(locale: str, routing: dict) -> bool:
    defaults = (routing.get("defaults_by_locale_genre") or {})
    return locale in defaults


def _catalog_csv(locale: str) -> bool:
    return (CATALOG_SSOT / f"{locale}_manga_catalog_ssot.csv").is_file()


def _grid_cell(locale: str, plans: int, alloc: bool, routing: bool, catalog: bool) -> str:
    if locale == "ko_KR":
        return "HOLD" if plans else "ABSENT"
    if plans and alloc and routing and catalog:
        return "GREEN"
    if plans and alloc and routing:
        return "PARTIAL"
    if alloc and routing and plans == 0:
        return "READY"
    if alloc and not routing:
        return "BLOCKED"
    if plans and not catalog:
        return "PARTIAL"
    return "ABSENT"


def _blockers(locale: str, plans: int, alloc: bool, routing: bool, catalog: bool) -> str:
    items: list[str] = []
    if locale == "ko_KR":
        items.append(KO_KR_HOLD)
    if not alloc:
        items.append("locale_genre_allocations_missing")
    if not routing:
        items.append("format_routing_missing")
    if plans == 0 and locale not in ("ko_KR",):
        if alloc and routing:
            items.append("wave_a_not_emitted")
        elif not routing:
            pass  # covered above
    if plans > 0 and not catalog:
        items.append("catalog_ssot_csv_missing")
    return ";".join(items) if items else "none"


def build_rows() -> list[dict[str, str]]:
    alloc_data = _load_yaml(ALLOC_PATH)
    locales_block = alloc_data.get("locales") or {}
    routing = _load_yaml(ROUTING_PATH)
    registry = sorted(locales_block.keys())

    rows: list[dict[str, str]] = []
    for locale in registry:
        plans = _plan_count(locale)
        alloc = locale in locales_block
        routing_ok = _has_routing(locale, routing)
        catalog = _catalog_csv(locale)
        if locale in WAVE_A_ZERO:
            lane = "wave_a"
        elif locale in SHIPPED:
            lane = "shipped_m3"
        elif locale == "ko_KR":
            lane = "hold"
        else:
            lane = "other"
        rows.append(
            {
                "locale": locale,
                "series_plans": str(plans),
                "allocation": "yes" if alloc else "no",
                "format_routing": "yes" if routing_ok else "no",
                "catalog_ssot_csv": "yes" if catalog else "no",
                "wave_a_lane": lane,
                "grid_cell": _grid_cell(locale, plans, alloc, routing_ok, catalog),
                "blockers": _blockers(locale, plans, alloc, routing_ok, catalog),
            }
        )
    return rows


def write_tsv(rows: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        default=f"artifacts/qa/manga_m7_plan_coverage_grid_{date.today().strftime('%Y%m%d')}.tsv",
        help="Output TSV path (relative to repo root).",
    )
    args = ap.parse_args()
    out = REPO / args.out
    rows = build_rows()
    write_tsv(rows, out)

    green = sum(1 for r in rows if r["grid_cell"] == "GREEN")
    partial = sum(1 for r in rows if r["grid_cell"] == "PARTIAL")
    with_plans = sum(1 for r in rows if int(r["series_plans"]) > 0)
    print(f"locales={len(rows)} with_plans={with_plans} green={green} partial={partial}")
    print(f"→ {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

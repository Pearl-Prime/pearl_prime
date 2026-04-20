#!/usr/bin/env python3
"""Build normalized manga_series_index.json from manga profile plan YAML files.

Phase-0 sources (verified 2026-04-20):
  - config/source_of_truth/manga_profiles/**/*.yaml (excluding schema.yaml)
  - brand metadata joined from config/brand_registry.yaml

See stderr gap report + SUMMARY line.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from e

BRAND_REGISTRY_PATH = REPO_ROOT / "config" / "brand_registry.yaml"
MANGA_PROFILE_ROOT = REPO_ROOT / "config" / "source_of_truth" / "manga_profiles"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "catalog_visibility" / "manga_series_index.json"

# Fields treated as "required for marketing completeness" (dashboard amber pills + gap view).
MARKETING_REQUIRED = (
    "reader_promise",
    "marketing_angle",
    "series_description",
    "launch_priority",
)

NORMALIZED_KEYS: tuple[str, ...] = (
    "brand_id",
    "catalog_id",
    "locale",
    "series_id",
    "series_title",
    "series_logline",
    "series_description",
    "market_demo",
    "genre_family",
    "subgenre",
    "emotional_engine",
    "serialization_engine",
    "visual_grammar",
    "reader_promise",
    "positioning",
    "audience",
    "comp_titles",
    "marketing_angle",
    "hook_lines",
    "launch_priority",
    "status",
    "main_character_name",
    "main_character_role",
    "main_character_image_path",
    "plan_source_path",
)


def _s(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s if s else None
    return str(v)


def _list_str(v: Any) -> list[str] | None:
    if v is None:
        return None
    if isinstance(v, list):
        out = [str(x).strip() for x in v if str(x).strip()]
        return out if out else None
    return None


def load_brand_registry(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    brands = data.get("brands") or {}
    out: dict[str, dict[str, Any]] = {}
    for bid, meta in brands.items():
        if isinstance(meta, dict):
            out[str(bid)] = meta
    return out


def discover_profile_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    if not root.is_dir():
        return paths
    for p in sorted(root.rglob("*.yaml")):
        if p.name == "schema.yaml":
            continue
        paths.append(p)
    return paths


def _plan_source_display(plan_path: Path) -> str:
    try:
        return str(plan_path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(plan_path)


def raw_doc_to_entry(raw: dict[str, Any], plan_path: Path, brands: dict[str, dict[str, Any]]) -> dict[str, Any]:
    brand_id = _s(raw.get("brand_id"))
    title_id = _s(raw.get("title_id"))
    series_id = _s(raw.get("series_id")) or title_id

    bmeta = brands.get(brand_id or "", {}) if brand_id else {}
    catalog_id = _s(bmeta.get("catalog_id"))
    locale = _s(bmeta.get("locale"))

    series_description = _s(raw.get("series_description") or raw.get("description"))
    if series_description is None:
        series_description = _s(raw.get("series_notes"))

    entry: dict[str, Any] = {
        "brand_id": brand_id,
        "catalog_id": catalog_id,
        "locale": locale,
        "series_id": series_id,
        "series_title": _s(raw.get("series_title")),
        "series_logline": _s(raw.get("series_logline") or raw.get("logline")),
        "series_description": series_description,
        "market_demo": _s(raw.get("market_demo")),
        "genre_family": _s(raw.get("genre_family")),
        "subgenre": _s(raw.get("subgenre")),
        "emotional_engine": _s(raw.get("emotional_engine")),
        "serialization_engine": _s(raw.get("serialization_engine")),
        "visual_grammar": _s(raw.get("visual_grammar")),
        "reader_promise": _s(raw.get("reader_promise")),
        "positioning": _s(raw.get("positioning")),
        "audience": _s(raw.get("audience")),
        "comp_titles": _list_str(raw.get("comp_titles")),
        "marketing_angle": _s(raw.get("marketing_angle")),
        "hook_lines": _list_str(raw.get("hook_lines")),
        "launch_priority": _s(raw.get("launch_priority")),
        "status": _s(raw.get("status")),
        "main_character_name": _s(raw.get("main_character_name")),
        "main_character_role": _s(raw.get("main_character_role")),
        "main_character_image_path": _s(raw.get("main_character_image_path")),
        "plan_source_path": _plan_source_display(plan_path),
    }

    for k in NORMALIZED_KEYS:
        if k not in entry:
            entry[k] = None

    return entry


def marketing_gaps(entry: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for k in MARKETING_REQUIRED:
        v = entry.get(k)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(k)
    return missing


def extract_all(profile_root: Path, brand_registry_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    brands = load_brand_registry(brand_registry_path)
    series: list[dict[str, Any]] = []
    errors: list[str] = []

    for path in discover_profile_files(profile_root):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:  # pragma: no cover — defensive
            errors.append(f"{path}: YAML error: {exc}")
            continue
        if not isinstance(raw, dict):
            errors.append(f"{path}: top-level must be mapping")
            continue
        if "title_id" not in raw and "series_id" not in raw:
            continue
        if "brand_id" not in raw:
            errors.append(f"{path}: missing brand_id — skipped")
            continue
        series.append(raw_doc_to_entry(raw, path, brands))

    return series, errors


# Fields surfaced as "required" in the operator gap report (stderr), aligned with dashboard badges.
GAP_REPORT_REQUIRED: tuple[str, ...] = (
    "main_character_image_path",
    "series_description",
    "marketing_angle",
    "reader_promise",
    "launch_priority",
)


def gap_lines(entries: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for e in entries:
        sid = e.get("series_id") or "?"
        missing: list[str] = []
        for k in GAP_REPORT_REQUIRED:
            v = e.get(k)
            if v is None:
                missing.append(k)
            elif isinstance(v, str) and not v.strip():
                missing.append(k)
        if missing:
            lines.append(f"[gap] series_id={sid} missing: {', '.join(missing)}")
    return lines


def summarize(entries: list[dict[str, Any]]) -> tuple[int, int, int]:
    n = len(entries)
    with_img = sum(1 for e in entries if e.get("main_character_image_path"))
    full_m = 0
    for e in entries:
        if not marketing_gaps(e):
            full_m += 1
    return n, with_img, full_m


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract normalized manga series index JSON.")
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output JSON path",
    )
    ap.add_argument(
        "--profile-root",
        type=Path,
        default=MANGA_PROFILE_ROOT,
        help="Root directory for manga profile YAML",
    )
    ap.add_argument(
        "--brand-registry",
        type=Path,
        default=BRAND_REGISTRY_PATH,
        help="brand_registry.yaml path",
    )
    args = ap.parse_args()

    entries, errs = extract_all(args.profile_root, args.brand_registry)
    for msg in errs:
        print(msg, file=sys.stderr)

    for line in gap_lines(entries):
        print(line, file=sys.stderr)

    n, m_img, k_meta = summarize(entries)
    print(
        f"SUMMARY: extracted={n} with_character_image={m_img} full_marketing_metadata={k_meta}",
        file=sys.stderr,
    )

    payload = {
        "schema_version": 1,
        "series": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

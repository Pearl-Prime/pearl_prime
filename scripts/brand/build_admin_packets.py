#!/usr/bin/env python3
"""
Build weekly admin ZIP bundles from coordination TSV + per-brand manifests.

Reads ``artifacts/coordination/weekly_packages_<Monday>.tsv`` and writes:
  artifacts/weekly_packages/<brand>/<YYYY-WW>/<brand>_<YYYY-WW>.zip

Each ZIP contains ``manifest.json`` plus all repo-relative files listed in the manifest.
Updates the coordination TSV ``download_url`` for rows whose content was bundled (status ready).

Usage:
  PYTHONPATH=. python3 scripts/brand/build_admin_packets.py
  PYTHONPATH=. python3 scripts/brand/build_admin_packets.py --week-monday 2026-05-19
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

from scripts.brand.weekly_package_endpoint import iso_week_monday, weekly_packages_tsv_path
from scripts.brand.weekly_package_writer import TSV_COLUMNS, week_iso_label

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.brand_admin_platform import PLATFORM_SPECS, platform_zip_path  # noqa: E402


def _parse_tsv(text: str) -> list[dict[str, str]]:
    buf = io.StringIO(text)
    reader = csv.reader(buf, delimiter="\t")
    rows = [r for r in reader if any((c or "").strip() for c in r)]
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]
    out: list[dict[str, str]] = []
    for row in rows[1:]:
        rec = {}
        for i, key in enumerate(header):
            rec[key] = row[i].strip() if i < len(row) else ""
        out.append(rec)
    return out


def _write_tsv(path: Path, records: list[dict[str, str]]) -> None:
    lines = ["\t".join(TSV_COLUMNS)]
    for rec in records:
        lines.append("\t".join(rec.get(col, "") for col in TSV_COLUMNS))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def zip_path_for_brand(packages_dir: Path, brand_id: str, week_iso: str) -> Path:
    week_dir = packages_dir / brand_id / week_iso
    week_dir.mkdir(parents=True, exist_ok=True)
    return week_dir / f"{brand_id}_{week_iso}.zip"


def build_zip_for_brand(
    repo_root: Path,
    brand_id: str,
    week_iso: str,
    *,
    packages_dir: Path | None = None,
) -> tuple[Path | None, list[str]]:
    """Return (zip_path, missing_files). zip_path is None if nothing to bundle."""
    root = repo_root.resolve()
    pkg_base = (packages_dir or root / "artifacts" / "weekly_packages").resolve()
    manifest_path = pkg_base / brand_id / week_iso / "manifest.json"
    if not manifest_path.is_file():
        return None, ["manifest.json"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rel_files: list[str] = []
    for block in (manifest.get("deliverables") or {}).values():
        if not isinstance(block, dict):
            continue
        for rel in block.get("files") or []:
            if isinstance(rel, str) and rel.strip():
                rel_files.append(rel.strip())

    rel_files = sorted(set(rel_files))
    missing: list[str] = []
    zip_out = zip_path_for_brand(pkg_base, brand_id, week_iso)

    with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", manifest_path.read_bytes())
        for rel in rel_files:
            src = root / rel
            if not src.is_file():
                missing.append(rel)
                continue
            zf.write(src, rel)

    if zip_out.stat().st_size == 0:
        zip_out.unlink(missing_ok=True)
        return None, missing

    return zip_out, missing


def build_platform_zips_for_brand(
    repo_root: Path,
    brand_id: str,
    week_iso: str,
    *,
    packages_dir: Path | None = None,
) -> list[Path]:
    """Emit per-platform ZIPs under ``<week>/<platform>/`` (OPD-145 split-at-build)."""
    root = repo_root.resolve()
    pkg_base = (packages_dir or root / "artifacts" / "weekly_packages").resolve()
    manifest_path = pkg_base / brand_id / week_iso / "manifest.json"
    if not manifest_path.is_file():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    readme = pkg_base / brand_id / week_iso / "README.txt"
    built: list[Path] = []
    deliverables = manifest.get("deliverables") or {}
    for slug, dtype in PLATFORM_SPECS:
        block = deliverables.get(dtype)
        if not isinstance(block, dict):
            continue
        files = block.get("files") or []
        if not files:
            continue
        plat_manifest = {
            "brand_id": brand_id,
            "week_iso": week_iso,
            "platform": slug,
            "deliverable_type": dtype,
            "deliverables": {dtype: block},
        }
        zip_out = platform_zip_path(pkg_base, brand_id, week_iso, slug)
        with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(plat_manifest, indent=2) + "\n")
            if readme.is_file():
                zf.write(readme, "README.txt")
        if zip_out.stat().st_size > 0:
            built.append(zip_out)
    return built


def apply_download_urls(
    records: list[dict[str, str]],
    *,
    brand_id: str,
    week_iso: str,
    zip_rel: str,
    generated_at: str,
) -> None:
    """Set download_url on ready rows for this brand/week."""
    for rec in records:
        if rec.get("brand_id") != brand_id or rec.get("week_iso") != week_iso:
            continue
        if (rec.get("status") or "").lower() != "ready":
            continue
        rec["download_url"] = zip_rel
        rec["last_updated"] = generated_at


def build_packets(
    repo_root: Path,
    *,
    coord_dir: Path | None = None,
    packages_dir: Path | None = None,
    week_monday: date,
    update_tsv: bool = True,
) -> dict[str, str]:
    root = repo_root.resolve()
    coord = (coord_dir or root / "artifacts" / "coordination").resolve()
    pkg = (packages_dir or root / "artifacts" / "weekly_packages").resolve()
    tsv_path = weekly_packages_tsv_path(coord, week_monday)
    if not tsv_path.is_file():
        raise FileNotFoundError(f"Missing coordination TSV: {tsv_path}")

    week_iso = week_iso_label(week_monday)
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = _parse_tsv(tsv_path.read_text(encoding="utf-8"))
    brands = sorted({r.get("brand_id", "") for r in records if r.get("brand_id")})

    built: dict[str, str] = {}
    for bid in brands:
        zip_path, missing = build_zip_for_brand(root, bid, week_iso, packages_dir=pkg)
        if zip_path is None:
            continue
        build_platform_zips_for_brand(root, bid, week_iso, packages_dir=pkg)
        rel = zip_path.resolve().relative_to(root).as_posix()
        built[bid] = rel
        if missing:
            print(f"warn: {bid} zip missing {len(missing)} file(s)", file=sys.stderr)
        if update_tsv:
            apply_download_urls(records, brand_id=bid, week_iso=week_iso, zip_rel=rel, generated_at=ts)

    if update_tsv and built:
        _write_tsv(tsv_path, records)

    return built


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build weekly admin ZIP packets from coordination TSV")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--coord-dir", type=Path, default=None)
    parser.add_argument("--packages-dir", type=Path, default=None)
    parser.add_argument("--week-monday", type=str, default=None)
    parser.add_argument("--no-tsv-update", action="store_true")
    args = parser.parse_args(argv)

    root = (args.repo_root or REPO_ROOT).resolve()
    if args.week_monday:
        mon = date.fromisoformat(args.week_monday)
    else:
        mon = iso_week_monday(datetime.now(tz=timezone.utc).date())

    built = build_packets(
        root,
        coord_dir=args.coord_dir,
        packages_dir=args.packages_dir,
        week_monday=mon,
        update_tsv=not args.no_tsv_update,
    )
    for bid, path in sorted(built.items()):
        print(f"{bid}: {path}")
    print(f"Built {len(built)} ZIP(s) for week {week_iso_label(mon)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

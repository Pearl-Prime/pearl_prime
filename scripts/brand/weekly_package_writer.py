#!/usr/bin/env python3
"""
Write Monday coordination TSV + per-brand weekly manifests (OPD-119 / OPD-121).

Output:
  artifacts/coordination/weekly_packages_<YYYY-MM-DD>.tsv  (Monday anchor)
  artifacts/weekly_packages/<brand_id>/<YYYY-WW>/manifest.json

TSV columns (endpoint reader + coordination extras):
  brand_id, week_iso, deliverable_type, status, download_url, last_updated

One row per (brand_id, week_iso, deliverable_type). ``download_url`` is left empty
for the writer; ``scripts/brand/build_admin_packets.py`` fills ZIP paths after bundling.

Usage:
  PYTHONPATH=. python3 scripts/brand/weekly_package_writer.py
  PYTHONPATH=. python3 scripts/brand/weekly_package_writer.py --reference-date 2026-05-20
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import yaml

from scripts.brand.active_brand_classifier import ActiveBrandClassifier
from scripts.brand.weekly_package_endpoint import iso_week_monday, weekly_packages_tsv_path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COORD_DIR = REPO_ROOT / "artifacts" / "coordination"
DEFAULT_PACKAGES_DIR = REPO_ROOT / "artifacts" / "weekly_packages"

# Canonical deliverable types for brand-admin weekly bundles.
#
# ``audiobook`` was added per AMENDMENT-2026-05-27-BRAND-ADMIN-V2-PHASE-1-P0-COMPLETE
# §3 (Phase 2 audiobook axis: Pearl_Audio audiobook pipeline → M4B + chapter markers
# → packaged into ``<brand>/<week>/{audible,google_play_audiobook}/``). Per-axis
# discovery below resolves an audiobook M4B (+ optional .cue sidecar) under
# ``artifacts/weekly_packages/<brand>/<week>/audiobook/`` (shared source for both
# platforms; split-at-build packager emits per-platform ZIPs).
DELIVERABLE_TYPES: tuple[str, ...] = (
    "books",
    "atoms",
    "manga_panels",
    "pearl_news",
    "podcast",
    "audiobook",
)

TSV_COLUMNS: tuple[str, ...] = (
    "brand_id",
    "week_iso",
    "deliverable_type",
    "status",
    "download_url",
    "last_updated",
)


@dataclass(frozen=True)
class TsvRow:
    brand_id: str
    week_iso: str
    deliverable_type: str
    status: str
    download_url: str
    last_updated: str

    def as_list(self) -> list[str]:
        return [
            self.brand_id,
            self.week_iso,
            self.deliverable_type,
            self.status,
            self.download_url,
            self.last_updated,
        ]


def week_iso_label(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def resolve_week_monday(
    *,
    reference_date: date | None = None,
    week_monday: date | None = None,
) -> date:
    if week_monday is not None:
        return week_monday
    ref = reference_date or datetime.now(tz=timezone.utc).date()
    return iso_week_monday(ref)


def _load_yaml_brands(path: Path) -> list[str]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    brands = data.get("brands")
    if not isinstance(brands, dict):
        return []
    out: list[str] = []
    for bid, meta in brands.items():
        if not isinstance(meta, dict):
            continue
        lifecycle = str(meta.get("lifecycle", "active")).lower()
        if lifecycle in ("active", ""):
            out.append(str(bid))
    return sorted(out)


def catalog_brand_ids(repo_root: Path) -> list[str]:
    """Union of book registry + manga canonical list (source-of-truth catalogs)."""
    ids: set[str] = set()
    ids.update(_load_yaml_brands(repo_root / "config" / "brand_registry.yaml"))
    ids.update(_load_yaml_brands(repo_root / "config" / "manga" / "canonical_brand_list.yaml"))
    return sorted(ids)


def target_brand_ids(
    repo_root: Path,
    *,
    classifier: ActiveBrandClassifier | None = None,
    active_only: bool = True,
) -> list[str]:
    c = classifier or ActiveBrandClassifier(repo_root=repo_root)
    catalog = catalog_brand_ids(repo_root)
    if active_only:
        active = set(c.list_active())
        return sorted(bid for bid in catalog if bid in active) or sorted(active)
    return catalog or c.brand_universe()


def _week_date_range(week_monday: date) -> tuple[date, date]:
    return week_monday, week_monday + timedelta(days=6)


def _rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _teacher_ids_for_brand(repo_root: Path, brand_id: str) -> list[str]:
    path = repo_root / "config" / "brand_registry.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    brands = data.get("brands") or {}
    meta = brands.get(brand_id) if isinstance(brands, dict) else None
    if not isinstance(meta, dict):
        return []
    teachers = meta.get("teacher_ids") or meta.get("teachers") or []
    if isinstance(teachers, str):
        return [teachers]
    if isinstance(teachers, list):
        return [str(t) for t in teachers if t]
    return []


@dataclass
class _ArtifactIndex:
    """Pre-indexed artifact paths for a single week (avoids per-brand full-tree scans)."""

    repo_root: Path
    week_monday: date
    pearl_news_files: dict[str, list[str]]
    manga_files: dict[str, list[str]]

    @classmethod
    def build(cls, repo_root: Path, week_monday: date) -> _ArtifactIndex:
        root = repo_root.resolve()
        mon, sun = _week_date_range(week_monday)
        pearl: dict[str, list[str]] = {}
        pub = root / "artifacts" / "pearl_news" / "published"
        if pub.is_dir():
            for day_dir in sorted(pub.iterdir()):
                if not day_dir.is_dir():
                    continue
                try:
                    day = date.fromisoformat(day_dir.name)
                except ValueError:
                    continue
                if not (mon <= day <= sun):
                    continue
                for p in sorted(day_dir.rglob("*")):
                    if p.is_file():
                        pearl.setdefault("_week", []).append(_rel(root, p))

        manga: dict[str, list[str]] = {}
        manga_root = root / "artifacts" / "manga"
        if manga_root.is_dir():
            bank = manga_root / "image_bank"
            if bank.is_dir():
                for brand_dir in sorted(bank.iterdir()):
                    if brand_dir.is_dir():
                        files = [
                            _rel(root, p)
                            for p in sorted(brand_dir.rglob("*"))
                            if p.is_file()
                        ]
                        if files:
                            manga[brand_dir.name] = files
            for sub in ("panel_prompts", "chapter_scripts", "brand_admin_handoff"):
                sub_root = manga_root / sub
                if not sub_root.is_dir():
                    continue
                for entry in sorted(sub_root.iterdir()):
                    if not entry.is_dir():
                        continue
                    token = entry.name.split("__", 1)[0]
                    files = [_rel(root, p) for p in sorted(entry.rglob("*")) if p.is_file()]
                    if files:
                        manga.setdefault(token, []).extend(files)

        return cls(repo_root=root, week_monday=week_monday, pearl_news_files=pearl, manga_files=manga)


def discover_deliverable_files(
    repo_root: Path,
    brand_id: str,
    deliverable_type: str,
    *,
    week_iso: str,
    week_monday: date,
    index: _ArtifactIndex | None = None,
) -> list[str]:
    """Return repo-relative paths published for this brand/week."""
    root = repo_root.resolve()
    pkg = root / "artifacts" / "weekly_packages" / brand_id / week_iso
    found: list[str] = []

    if deliverable_type == "books":
        for name in ("upload_manifest.csv", "README.txt"):
            p = pkg / name
            if p.is_file():
                found.append(_rel(root, p))
        books = pkg / "books"
        if books.is_dir():
            for p in sorted(books.rglob("*")):
                if p.is_file():
                    found.append(_rel(root, p))
        catalog_books = root / "artifacts" / "catalog" / "published" / brand_id
        if catalog_books.is_dir():
            mon, sun = _week_date_range(week_monday)
            for p in sorted(catalog_books.iterdir()):
                if not p.is_file():
                    continue
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date()
                if mon <= mtime <= sun:
                    found.append(_rel(root, p))

    elif deliverable_type == "atoms":
        for tid in _teacher_ids_for_brand(root, brand_id):
            bank = root / "SOURCE_OF_TRUTH" / "teacher_banks" / tid / "approved_atoms"
            if bank.is_dir():
                for p in sorted(bank.rglob("*.txt"))[:50]:
                    found.append(_rel(root, p))

    elif deliverable_type == "manga_panels":
        idx = index or _ArtifactIndex.build(root, week_monday)
        found.extend(idx.manga_files.get(brand_id, []))

    elif deliverable_type == "pearl_news":
        idx = index or _ArtifactIndex.build(root, week_monday)
        found.extend(idx.pearl_news_files.get("_week", []))

    elif deliverable_type == "podcast":
        pod = pkg / "podcast"
        if pod.is_dir():
            for p in sorted(pod.rglob("*")):
                if p.is_file():
                    found.append(_rel(root, p))

    elif deliverable_type == "audiobook":
        # Per AMENDMENT-2026-05-27-BRAND-ADMIN-V2-PHASE-1-P0-COMPLETE §3, audiobook
        # source assets (M4B + optional .cue chapter sidecar) live under
        # ``<brand>/<week>/audiobook/`` and are shared by the audible +
        # google_play_audiobook platforms (split-at-build emits per-platform ZIPs).
        ab = pkg / "audiobook"
        if ab.is_dir():
            for p in sorted(ab.rglob("*")):
                if p.is_file():
                    found.append(_rel(root, p))

    # Stable, deduped order for idempotent output
    seen: set[str] = set()
    out: list[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def build_manifest(
    repo_root: Path,
    brand_id: str,
    *,
    week_iso: str,
    week_monday: date,
    generated_at: str,
    index: _ArtifactIndex | None = None,
) -> dict:
    deliverables: dict[str, dict] = {}
    for dtype in DELIVERABLE_TYPES:
        files = discover_deliverable_files(
            repo_root,
            brand_id,
            dtype,
            week_iso=week_iso,
            week_monday=week_monday,
            index=index,
        )
        deliverables[dtype] = {
            "status": "ready" if files else "pending",
            "files": files,
        }
    return {
        "brand_id": brand_id,
        "week_iso": week_iso,
        "week_monday": week_monday.isoformat(),
        "generated_at": generated_at,
        "deliverables": deliverables,
    }


def build_tsv_rows(
    repo_root: Path,
    brand_ids: Iterable[str],
    *,
    week_iso: str,
    week_monday: date,
    generated_at: str,
) -> list[TsvRow]:
    rows: list[TsvRow] = []
    index = _ArtifactIndex.build(repo_root, week_monday)
    for bid in sorted(brand_ids):
        manifest = build_manifest(
            repo_root,
            bid,
            week_iso=week_iso,
            week_monday=week_monday,
            generated_at=generated_at,
            index=index,
        )
        pkg_dir = repo_root / "artifacts" / "weekly_packages" / bid / week_iso
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for dtype in DELIVERABLE_TYPES:
            block = manifest["deliverables"][dtype]
            rows.append(
                TsvRow(
                    brand_id=bid,
                    week_iso=week_iso,
                    deliverable_type=dtype,
                    status=block["status"],
                    download_url="",
                    last_updated=generated_at,
                )
            )
    return rows


def render_tsv(rows: list[TsvRow]) -> str:
    lines = ["\t".join(TSV_COLUMNS)]
    for row in rows:
        lines.append("\t".join(row.as_list()))
    return "\n".join(lines) + "\n"


def write_weekly_packages(
    repo_root: Path,
    *,
    coord_dir: Path | None = None,
    week_monday: date,
    brand_ids: Iterable[str] | None = None,
    generated_at: str | None = None,
) -> Path:
    root = repo_root.resolve()
    coord = (coord_dir or root / "artifacts" / "coordination").resolve()
    coord.mkdir(parents=True, exist_ok=True)
    ts = generated_at or datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wk_iso = week_iso_label(week_monday)
    bids = list(brand_ids) if brand_ids is not None else target_brand_ids(root)
    rows = build_tsv_rows(root, bids, week_iso=wk_iso, week_monday=week_monday, generated_at=ts)
    out_path = weekly_packages_tsv_path(coord, week_monday)
    out_path.write_text(render_tsv(rows), encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write weekly_packages coordination TSV + manifests")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--coord-dir", type=Path, default=None)
    parser.add_argument("--reference-date", type=str, default=None, help="YYYY-MM-DD (UTC) for week anchor")
    parser.add_argument("--week-monday", type=str, default=None, help="Override Monday YYYY-MM-DD")
    parser.add_argument("--all-brands", action="store_true", help="Include inactive catalog brands")
    args = parser.parse_args(argv)

    root = (args.repo_root or REPO_ROOT).resolve()
    if args.week_monday:
        mon = date.fromisoformat(args.week_monday)
    else:
        ref = date.fromisoformat(args.reference_date) if args.reference_date else None
        mon = resolve_week_monday(reference_date=ref)

    out = write_weekly_packages(
        root,
        coord_dir=args.coord_dir,
        week_monday=mon,
        brand_ids=target_brand_ids(root, active_only=not args.all_brands),
    )
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

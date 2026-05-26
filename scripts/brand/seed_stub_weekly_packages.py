#!/usr/bin/env python3
"""Seed stub weekly packages: monolithic + per-platform ZIPs (OPD-145 split-at-build)."""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from server.brand_admin_platform import (  # noqa: E402
    PLATFORM_SPECS,
    monolithic_zip_path,
    platform_zip_path,
)

WEEK_ISO = "2026-W22"
WEEK_MONDAY = date(2026, 5, 25)
MANGA_LIST = REPO / "config" / "manga" / "canonical_brand_list.yaml"
PACKAGES = REPO / "artifacts" / "weekly_packages"
COORD = REPO / "artifacts" / "coordination"
DTYPES = ("books", "atoms", "manga_panels", "pearl_news", "podcast")
README = (
    "Stub weekly package (MVP seed).\n"
    "Real content TBD per upstream pipeline workstreams.\n"
    "ws_weekly_packages_directory_seed_20260526 + OPD-145 per-platform stubs\n"
)


def _write_zip(zip_path: Path, manifest: dict, readme_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        if readme_path.is_file():
            zf.write(readme_path, "README.txt")


def main() -> None:
    brands = sorted((yaml.safe_load(MANGA_LIST.read_text()) or {}).get("brands", {}))
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tsv_path = COORD / f"weekly_packages_{WEEK_MONDAY.isoformat()}.tsv"
    tsv_lines = [
        "\t".join(
            ("brand_id", "week_iso", "deliverable_type", "status", "download_url", "last_updated")
        )
    ]

    platform_count = 0
    for bid in brands:
        pkg_dir = PACKAGES / bid / WEEK_ISO
        pkg_dir.mkdir(parents=True, exist_ok=True)
        readme_path = pkg_dir / "README.txt"
        if not readme_path.is_file():
            readme_path.write_text(
                README + f"brand_id={bid}\nweek={WEEK_ISO}\n", encoding="utf-8"
            )

        manifest = {
            "brand_id": bid,
            "week_iso": WEEK_ISO,
            "week_monday": WEEK_MONDAY.isoformat(),
            "generated_at": ts,
            "package_type": "stub_mvp",
            "deliverables": {d: {"status": "stub", "files": ["README.txt"]} for d in DTYPES},
        }
        manifest_path = pkg_dir / "manifest.json"
        if not manifest_path.is_file():
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        mono = monolithic_zip_path(PACKAGES, bid, WEEK_ISO)
        if not mono.is_file() or mono.stat().st_size == 0:
            _write_zip(mono, manifest, readme_path)
        rel_mono = mono.relative_to(REPO).as_posix()
        for dtype in DTYPES:
            tsv_lines.append("\t".join((bid, WEEK_ISO, dtype, "ready", rel_mono, ts)))

        for slug, dtype in PLATFORM_SPECS:
            plat_manifest = {
                "brand_id": bid,
                "week_iso": WEEK_ISO,
                "week_monday": WEEK_MONDAY.isoformat(),
                "generated_at": ts,
                "package_type": "stub_platform",
                "platform": slug,
                "deliverable_type": dtype,
                "deliverables": {dtype: {"status": "stub", "files": ["README.txt"]}},
            }
            pzip = platform_zip_path(PACKAGES, bid, WEEK_ISO, slug)
            if not pzip.is_file() or pzip.stat().st_size == 0:
                _write_zip(pzip, plat_manifest, readme_path)
                platform_count += 1
            rel_plat = pzip.relative_to(REPO).as_posix()
            tsv_lines.append("\t".join((bid, WEEK_ISO, f"platform:{slug}", "ready", rel_plat, ts)))

    tsv_path.write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")
    print(f"Seeded {len(brands)} brands, {platform_count} new platform ZIPs -> {tsv_path.name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Seed stub weekly packages for manga-canon brands (ws_weekly_packages_directory_seed)."""
from __future__ import annotations

import json
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WEEK_ISO = "2026-W22"
WEEK_MONDAY = date(2026, 5, 25)
MANGA_LIST = REPO / "config" / "manga" / "canonical_brand_list.yaml"
PACKAGES = REPO / "artifacts" / "weekly_packages"
COORD = REPO / "artifacts" / "coordination"
DTYPES = ("books", "atoms", "manga_panels", "pearl_news", "podcast")
README = (
    "Stub weekly package (MVP seed).\n"
    "Real content TBD per upstream pipeline workstreams.\n"
    "ws_weekly_packages_directory_seed_20260526\n"
)


def main() -> None:
    brands = sorted((yaml.safe_load(MANGA_LIST.read_text()) or {}).get("brands", {}))
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tsv_path = COORD / f"weekly_packages_{WEEK_MONDAY.isoformat()}.tsv"
    tsv_lines = ["\t".join(("brand_id", "week_iso", "deliverable_type", "status", "download_url", "last_updated"))]

    for bid in brands:
        pkg_dir = PACKAGES / bid / WEEK_ISO
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "README.txt").write_text(README + f"brand_id={bid}\nweek={WEEK_ISO}\n", encoding="utf-8")
        manifest = {
            "brand_id": bid,
            "week_iso": WEEK_ISO,
            "week_monday": WEEK_MONDAY.isoformat(),
            "generated_at": ts,
            "package_type": "stub_mvp",
            "deliverables": {d: {"status": "stub", "files": ["README.txt"]} for d in DTYPES},
        }
        (pkg_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        zip_path = pkg_dir / f"{bid}_{WEEK_ISO}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(pkg_dir / "manifest.json", "manifest.json")
            zf.write(pkg_dir / "README.txt", "README.txt")
        rel_zip = zip_path.relative_to(REPO).as_posix()
        for dtype in DTYPES:
            tsv_lines.append("\t".join((bid, WEEK_ISO, dtype, "ready", rel_zip, ts)))

    tsv_path.write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")
    print(f"Seeded {len(brands)} brands -> {tsv_path.name}")


if __name__ == "__main__":
    main()

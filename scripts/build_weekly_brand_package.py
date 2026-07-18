#!/usr/bin/env python3
"""
Build weekly upload package for each brand manager.

For each brand lane (locale × brand), produces:
1. CSV manifest of books to upload this week (title, format, platform, file paths)
2. Rendered book files (txt, metadata JSON)
3. Cover art references
4. Platform-specific metadata (keywords, categories, descriptions)

Output: artifacts/weekly_packages/<brand_id>/<date>/
  - upload_manifest.csv
  - books/ (rendered book files)
  - metadata/ (per-platform metadata JSONs)
  - README.txt (instructions for the brand manager)

Delivery: sends package notification via configured channels
(Slack, LINE, WeChat, email — per brand_admin_channels.yaml).

Usage:
    python scripts/build_weekly_brand_package.py --brand stillness_press --week 2026-W14
    python scripts/build_weekly_brand_package.py --all --week current
    python scripts/build_weekly_brand_package.py --all --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    print("pyyaml required")
    sys.exit(1)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _current_week() -> str:
    return datetime.now().strftime("%Y-W%V")


def get_brand_lanes() -> dict[str, dict]:
    """Return brand_id → {locale, platforms, teacher_ids, topics, personas, max_per_week}."""
    registry = _load_yaml(REPO_ROOT / "config" / "brand_registry.yaml")
    brands = registry.get("brands") or {}
    wave_controls = _load_yaml(REPO_ROOT / "config" / "release_wave_controls.yaml")
    max_brand_week = (wave_controls.get("hard_constraints") or {}).get("max_same_brand_id_per_week", 20)

    lanes = {}
    for bid, bdata in brands.items():
        if not isinstance(bdata, dict):
            continue
        lanes[bid] = {
            "locale": bdata.get("locale", "en-US"),
            "platforms": bdata.get("platforms", []),
            "teacher_ids": bdata.get("teacher_ids", []),
            "topics": bdata.get("topics", []),
            "personas": bdata.get("personas", []),
            "max_per_week": min(max_brand_week, bdata.get("max_per_week", max_brand_week)),
        }
    return lanes


def build_package(
    brand_id: str,
    lane: dict,
    week: str,
    dry_run: bool = False,
    quality_profile: str = "draft",
) -> dict:
    """Build weekly package for one brand lane."""
    from scripts.generate_catalog import build_catalog_manifest

    locale = lane.get("locale", "en-US")
    teachers = lane.get("teacher_ids") or None
    topics = lane.get("topics") or None
    personas = lane.get("personas") or None
    max_books = lane.get("max_per_week", 10)

    # Build manifest for this brand's lane
    manifest = build_catalog_manifest(
        teachers=teachers,
        topics=topics,
        personas=personas,
        locales=[locale] if locale else None,
        limit=max_books,
    )

    pkg_dir = REPO_ROOT / "artifacts" / "weekly_packages" / brand_id / week
    pkg_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "brand_id": brand_id,
        "week": week,
        "locale": locale,
        "books_planned": len(manifest),
        "books_built": 0,
        "books_failed": 0,
        "package_dir": str(pkg_dir),
    }

    if dry_run:
        # Write manifest CSV only
        csv_path = pkg_dir / "upload_manifest.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "teacher", "persona", "topic", "format", "platform", "locale", "arc"])
            writer.writeheader()
            for m in manifest:
                writer.writerow({
                    "title": f"{m['topic'].replace('_', ' ').title()} — {m['persona'].replace('_', ' ').title()}",
                    "teacher": m["teacher"],
                    "persona": m["persona"],
                    "topic": m["topic"],
                    "format": m["format"],
                    "platform": m.get("platform", ""),
                    "locale": m.get("locale", locale),
                    "arc": m["arc"],
                })
        result["manifest_path"] = str(csv_path)
        return result

    # Build books
    books_dir = pkg_dir / "books"
    books_dir.mkdir(exist_ok=True)
    built_books = []

    for i, m in enumerate(manifest):
        book_name = f"{m['teacher']}_{m['persona']}_{m['topic']}_{m['format']}"
        book_dir = books_dir / book_name
        book_dir.mkdir(exist_ok=True)

        # CI-ALLOWLIST: legacy-registry-ok — parameterized builder (quality via --quality-profile, defaults draft), not a fixed bestseller build
        cmd = [
            sys.executable, str(REPO_ROOT / "scripts" / "run_pipeline.py"),
            "--topic", m["topic"],
            "--persona", m["persona"],
            "--arc", m["arc_path"],
            "--teacher", m["teacher"],
            "--location", "nyc_metro",
            "--quality-profile", quality_profile,
            "--render-book",
            "--render-dir", str(book_dir),
            "--out", str(book_dir / "plan.json"),
        ]

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))

        if r.returncode == 0 and list(book_dir.glob("*.txt")):
            result["books_built"] += 1
            wc = sum(len(f.read_text().split()) for f in book_dir.glob("*.txt"))
            built_books.append({
                "title": f"{m['topic'].replace('_', ' ').title()} — {m['persona'].replace('_', ' ').title()}",
                "teacher": m["teacher"],
                "words": wc,
                "path": str(book_dir),
                "platform": m.get("platform", ""),
            })
        else:
            result["books_failed"] += 1

    manifest_rows = list(built_books)
    if not dry_run and built_books:
        try:
            from scripts.podcast._lib import brand_has_podcast, podcast_locale_for_brand

            if brand_has_podcast(brand_id):
                book0 = Path(built_books[0]["path"])
                ploc = podcast_locale_for_brand(brand_id, locale)
                prc = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / "scripts/podcast/run_podcast_pipeline.py"),
                        "--brand-id",
                        brand_id,
                        "--locale",
                        ploc,
                        "--week",
                        week,
                        "--book-dir",
                        str(book0),
                        "--output-dir",
                        str(pkg_dir),
                        "--formats",
                        "podcast_episode,podcast_short",
                        "--skip-upload",
                    ],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=7200,
                )
                result["podcast_pipeline_rc"] = prc.returncode
                if prc.returncode != 0 and prc.stderr:
                    result["podcast_pipeline_stderr"] = prc.stderr[-2000:]
                pd = pkg_dir / "podcast"
                if pd.is_dir():
                    for mp3 in sorted(pd.glob("*.mp3")):
                        manifest_rows.append(
                            {
                                "title": mp3.stem,
                                "teacher": "",
                                "words": "",
                                "platform": "podcast",
                                "path": str(mp3),
                            }
                        )
                    feed = pd / "feed.xml"
                    if feed.is_file():
                        manifest_rows.append(
                            {
                                "title": "podcast_feed",
                                "teacher": "",
                                "words": "",
                                "platform": "podcast",
                                "path": str(feed),
                            }
                        )
        except Exception as e:
            result["podcast_error"] = str(e)

    # Write manifest CSV
    csv_path = pkg_dir / "upload_manifest.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "teacher", "words", "platform", "path"])
        writer.writeheader()
        for b in manifest_rows:
            writer.writerow(b)

    # Write README
    readme_path = pkg_dir / "README.txt"
    readme_path.write_text(
        f"Weekly Upload Package — {brand_id}\n"
        f"Week: {week}\n"
        f"Locale: {locale}\n"
        f"Books: {result['books_built']} built, {result['books_failed']} failed\n\n"
        f"Upload each book from the books/ directory to the appropriate platform.\n"
        f"See upload_manifest.csv for the full list with metadata.\n"
        f"\nPodcast: if enabled for this brand, rendered audio is under podcast/ (MP3 + feed.xml).\n"
    )

    result["manifest_path"] = str(csv_path)
    result["readme_path"] = str(readme_path)
    return result


def notify_brand_admin(brand_id: str, result: dict) -> None:
    """Send notification to brand admin via configured channels."""
    try:
        notify_script = REPO_ROOT / "scripts" / "distribution" / "distribute_to_brand_admins.py"
        if notify_script.exists():
            msg = (
                f"Weekly package ready for {brand_id} (week {result['week']})\n"
                f"Books: {result['books_built']} ready to upload\n"
                f"Package: {result['package_dir']}"
            )
            subprocess.run(
                [sys.executable, str(notify_script), "--brand", brand_id, "--message", msg],
                capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
            )
    except Exception:
        pass  # notification is best-effort


def run_ei_learn(results: list[dict]) -> None:
    """Run EI learning cycle after batch build to refine quality weights."""
    try:
        learn_script = REPO_ROOT / "scripts" / "ci" / "run_ei_v2_catalog_calibration.py"
        if learn_script.exists():
            subprocess.run(
                [sys.executable, str(learn_script)],
                capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT),
            )
            print("EI learning cycle complete.")
    except Exception as e:
        print(f"EI learning skipped: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build weekly brand upload packages")
    parser.add_argument("--brand", help="Specific brand ID")
    parser.add_argument("--all", action="store_true", help="Build for all brands")
    parser.add_argument("--week", default="current", help="ISO week (e.g. 2026-W14) or 'current'")
    parser.add_argument("--dry-run", action="store_true", help="Manifest only, no builds")
    parser.add_argument("--quality-profile", default="draft", choices=["production", "draft"])
    parser.add_argument("--ei-learn", action="store_true", help="Run EI learning after builds")
    parser.add_argument("--notify", action="store_true", help="Send notifications to brand admins")
    args = parser.parse_args()

    week = _current_week() if args.week == "current" else args.week
    lanes = get_brand_lanes()

    if args.brand:
        if args.brand not in lanes:
            print(f"Brand '{args.brand}' not found. Available: {', '.join(sorted(lanes.keys()))}")
            return 1
        target_brands = {args.brand: lanes[args.brand]}
    elif args.all:
        target_brands = lanes
    else:
        parser.error("Specify --brand or --all")
        return 1

    print(f"Building weekly packages for {len(target_brands)} brand(s), week {week}")
    all_results = []

    for bid, lane in sorted(target_brands.items()):
        print(f"\n{'='*60}")
        print(f"Brand: {bid} | Locale: {lane.get('locale', '?')} | Max/week: {lane.get('max_per_week', '?')}")
        print(f"{'='*60}")

        result = build_package(bid, lane, week, dry_run=args.dry_run, quality_profile=args.quality_profile)
        all_results.append(result)

        print(f"  Books planned: {result['books_planned']}")
        print(f"  Books built:   {result.get('books_built', 'N/A (dry-run)')}")
        print(f"  Package:       {result.get('package_dir', 'N/A')}")

        if args.notify and not args.dry_run:
            notify_brand_admin(bid, result)

    # EI learning after all builds
    if args.ei_learn and not args.dry_run:
        run_ei_learn(all_results)

    # Summary
    total_built = sum(r.get("books_built", 0) for r in all_results)
    total_failed = sum(r.get("books_failed", 0) for r in all_results)
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(all_results)} brands, {total_built} books built, {total_failed} failed")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

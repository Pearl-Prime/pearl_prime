#!/usr/bin/env python3
"""Phase 0 — populate ja_JP text in stillness_press chapter scripts via Pearl Star Ollama qwen2.5.

Auto-discovers en_US chapter scripts under
``artifacts/manga/chapter_scripts/stillness_press__*__en_US__*/`` and invokes
``scripts/manga/translate_chapter_script.py`` per chapter to fill
``text_by_locale[ja_JP]`` / ``sfx_by_locale[ja_JP]`` / ``narrator_caption_by_locale[ja_JP]``.

Idempotent + resumable: writes a sentinel per chapter to
``artifacts/manga/sentinels/ja_jp_phase0_<series>__<chapter>.ok`` and skips
chapters whose sentinel exists.

Tier-2 LLM: Pearl Star Ollama ``qwen2.5:14b`` (free, unattended-safe per
``CLAUDE.md`` LLM Tier Policy). No paid API call.

Usage:
    python3 scripts/manga/ja_jp_phase0_source_gen.py [--single-chapter SERIES/CHAPTER]
                                                      [--force-retranslate]
                                                      [--dry-run]

Exit code 0 on full success, 1 on any chapter failure (orchestrator stops).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_SCRIPTS_DIR = REPO_ROOT / "artifacts" / "manga" / "chapter_scripts"
SENTINEL_DIR = REPO_ROOT / "artifacts" / "manga" / "sentinels"
TRANSLATOR = REPO_ROOT / "scripts" / "manga" / "translate_chapter_script.py"


def discover_en_us_chapters(brand: str = "stillness_press"):
    """Yield (series_dir_name, chapter_yaml_path) for every available en_US chapter."""
    pattern = f"{brand}__*__en_US__*"
    for series_dir in sorted(CHAPTER_SCRIPTS_DIR.glob(pattern)):
        if not series_dir.is_dir():
            continue
        for chapter in sorted(series_dir.glob("ep_*.yaml")):
            yield series_dir.name, chapter


def sentinel_path(series_name: str, chapter_path: Path) -> Path:
    chapter_stem = chapter_path.stem
    return SENTINEL_DIR / f"ja_jp_phase0_{series_name}__{chapter_stem}.ok"


def translate_one(chapter_path: Path, *, force: bool, dry_run: bool) -> int:
    cmd = [
        sys.executable,
        str(TRANSLATOR),
        "--in",
        str(chapter_path),
        "--target-locales",
        "ja_JP",
        "--backend",
        "qwen_ollama",
    ]
    if force:
        cmd.append("--force")
    print(f"  → {' '.join(cmd[1:])}", flush=True)
    if dry_run:
        return 0
    t0 = time.time()
    r = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=900)
    dt = time.time() - t0
    if r.returncode != 0:
        print(f"  ✗ FAIL (rc={r.returncode}, {dt:.1f}s)", flush=True)
        print(f"    stdout: {r.stdout[-400:] if r.stdout else '(empty)'}", flush=True)
        print(f"    stderr: {r.stderr[-400:] if r.stderr else '(empty)'}", flush=True)
        return r.returncode
    print(f"  ✓ ok ({dt:.1f}s)", flush=True)
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--single-chapter", help="series_dir/chapter_stem (e.g. stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001) for smoke testing")
    p.add_argument("--force-retranslate", action="store_true", help="pass --force to translator (re-translate even if ja_JP already populated)")
    p.add_argument("--dry-run", action="store_true", help="list what would happen; do nothing")
    p.add_argument("--brand", default="stillness_press", help="brand_id prefix filter (default: stillness_press)")
    args = p.parse_args()

    if not TRANSLATOR.exists():
        print(f"FATAL: translator not found at {TRANSLATOR}", file=sys.stderr)
        return 1

    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)

    chapters = list(discover_en_us_chapters(brand=args.brand))
    if args.single_chapter:
        target = args.single_chapter.strip("/")
        chapters = [(s, c) for (s, c) in chapters if f"{s}/{c.stem}" == target]
        if not chapters:
            print(f"FATAL: no chapter matched --single-chapter={args.single_chapter}", file=sys.stderr)
            return 1

    print(f"Phase 0 — ja_JP translation. Discovered {len(chapters)} en_US chapter(s) for brand={args.brand}.", flush=True)
    if not chapters:
        print("Nothing to translate. (This is expected if no en_US chapter scripts have been authored.)", flush=True)
        return 0

    failed = []
    skipped = []
    translated = []
    for series_name, chapter_path in chapters:
        sentinel = sentinel_path(series_name, chapter_path)
        label = f"{series_name}/{chapter_path.stem}"
        if sentinel.exists() and not args.force_retranslate:
            print(f"[skip] {label} (sentinel exists)", flush=True)
            skipped.append(label)
            continue
        print(f"[translate] {label}", flush=True)
        rc = translate_one(chapter_path, force=args.force_retranslate, dry_run=args.dry_run)
        if rc != 0:
            failed.append(label)
            continue
        if not args.dry_run:
            sentinel.write_text(f"ja_JP phase 0 ok @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        translated.append(label)

    print(flush=True)
    print(f"Phase 0 summary: translated={len(translated)} skipped={len(skipped)} failed={len(failed)}", flush=True)
    if failed:
        print(f"FAILED chapters: {failed}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

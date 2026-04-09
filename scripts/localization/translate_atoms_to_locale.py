#!/usr/bin/env python3
"""Batch translate ALL persona atoms + teacher bank atoms to a target locale.

Uses Ollama on Pearl Star (Qwen3:14b) for translation. Free, self-hosted.
Idempotent: skips already-translated files. Resumable on failure.

Usage:
  # Translate all atoms to zh-TW
  python3 scripts/localization/translate_atoms_to_locale.py --locale zh-TW

  # Translate single persona
  python3 scripts/localization/translate_atoms_to_locale.py --locale zh-TW --persona gen_z_student

  # Translate teacher banks only
  python3 scripts/localization/translate_atoms_to_locale.py --locale zh-TW --teacher-banks-only

  # Dry run
  python3 scripts/localization/translate_atoms_to_locale.py --locale zh-TW --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

LOCALE_NAMES = {
    "zh-TW": "Traditional Chinese (Taiwan)",
    "zh-CN": "Simplified Chinese (Mainland China)",
    "zh-HK": "Traditional Chinese (Hong Kong / Cantonese context)",
    "zh-SG": "Simplified Chinese (Singapore)",
    "ja-JP": "Japanese",
    "ko-KR": "Korean",
}

SYSTEM_PROMPTS = {
    "zh-TW": "You are a professional translator. Translate the following English therapeutic/self-help text into Traditional Chinese (繁體中文) suitable for Taiwan audiences. Maintain the emotional tone, body-awareness language, and second-person address. Preserve any ## headers and structural markers exactly as-is. Do NOT add commentary. Output ONLY the translation.",
    "zh-CN": "You are a professional translator. Translate the following English therapeutic/self-help text into Simplified Chinese (简体中文) suitable for Mainland China audiences. Maintain the emotional tone, body-awareness language, and second-person address. Preserve any ## headers and structural markers exactly as-is. Do NOT add commentary. Output ONLY the translation.",
    "ja-JP": "You are a professional translator. Translate the following English therapeutic/self-help text into Japanese (日本語). Use appropriate keigo level for wellness content. Maintain the emotional tone, body-awareness language, and second-person address. Preserve any ## headers and structural markers exactly as-is. Do NOT add commentary. Output ONLY the translation.",
    "ko-KR": "You are a professional translator. Translate the following English therapeutic/self-help text into Korean (한국어). Use appropriate 존댓말 level for wellness content. Maintain the emotional tone, body-awareness language, and second-person address. Preserve any ## headers and structural markers exactly as-is. Do NOT add commentary. Output ONLY the translation.",
}


def _translate_text(text: str, locale: str, ollama_url: str, model: str) -> str | None:
    """Translate text via Ollama."""
    system = SYSTEM_PROMPTS.get(locale, SYSTEM_PROMPTS.get("zh-TW", "Translate to the target language."))

    prompt = f"{system}\n\n{text[:8000]}"

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.25, "num_predict": 8000},
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
        reply = result.get("response", "").strip()
        # Strip any stray thinking blocks
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
        return reply if len(reply) > 10 else None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def translate_persona_atoms(
    locale: str,
    ollama_url: str,
    model: str,
    persona_filter: str | None = None,
    dry_run: bool = False,
    workers: int = 4,
) -> tuple[int, int]:
    """Translate all persona atoms to locale using parallel workers."""
    # Find all English CANONICAL.txt files
    atom_files = sorted(ATOMS_ROOT.glob("*/*/[A-Z]*/CANONICAL.txt"))
    engine_files = sorted(ATOMS_ROOT.glob("*/*/*/CANONICAL.txt"))
    all_files = list(set(atom_files + engine_files))
    all_files = [f for f in all_files if "/locales/" not in str(f)]

    if persona_filter:
        all_files = [f for f in all_files if f.parts[-4] == persona_filter or f.parts[-3] == persona_filter]

    # Filter to untranslated only
    work = []
    skipped = 0
    for atom_path in all_files:
        locale_dir = atom_path.parent / "locales" / locale
        out_path = locale_dir / "CANONICAL.txt"
        if out_path.exists() and out_path.stat().st_size > 20:
            skipped += 1
            continue
        en_text = atom_path.read_text(encoding="utf-8").strip()
        if not en_text or len(en_text) < 20:
            skipped += 1
            continue
        work.append((atom_path, en_text))

    total = len(work)
    print(f"Persona atoms to translate: {total} (skipped {skipped} already done)")
    if not work:
        return 0, skipped

    translated = 0
    lock = Lock()
    start_time = time.time()

    def _do_one(idx: int, atom_path: Path, en_text: str) -> bool:
        nonlocal translated
        locale_dir = atom_path.parent / "locales" / locale
        out_path = locale_dir / "CANONICAL.txt"
        rel = atom_path.relative_to(ATOMS_ROOT)

        if dry_run:
            with lock:
                translated += 1
                print(f"  [{idx+1}/{total}] {rel} [DRY-RUN]")
            return True

        zh = _translate_text(en_text, locale, ollama_url, model)
        if zh:
            locale_dir.mkdir(parents=True, exist_ok=True)
            out_path.write_text(zh, encoding="utf-8")
            with lock:
                translated += 1
                elapsed = time.time() - start_time
                rate = translated / max(elapsed, 1) * 60
                eta = (total - translated) / max(rate, 0.1)
                print(f"  [{translated}/{total}] {rel} OK ({len(zh)} chars) {rate:.0f}/min ETA:{eta:.0f}min")
            return True
        else:
            with lock:
                print(f"  [{idx+1}/{total}] {rel} FAILED")
            return False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_do_one, i, p, t): i for i, (p, t) in enumerate(work)}
        for f in as_completed(futures):
            f.result()  # propagate exceptions

    return translated, skipped


def translate_teacher_banks(
    locale: str,
    ollama_url: str,
    model: str,
    dry_run: bool = False,
    workers: int = 4,
) -> tuple[int, int]:
    """Translate all teacher bank atoms to locale using parallel workers."""
    if not TEACHER_BANKS_ROOT.exists():
        print("Teacher banks root not found")
        return 0, 0

    try:
        import yaml as _yaml
    except ImportError:
        print("PyYAML required")
        return 0, 0

    yaml_files = sorted(TEACHER_BANKS_ROOT.glob("*/approved_atoms/*/*.yaml"))
    yaml_files = [f for f in yaml_files if "/locales/" not in str(f)]

    work = []
    skipped = 0
    for yaml_path in yaml_files:
        locale_dir = yaml_path.parent / "locales" / locale
        out_path = locale_dir / yaml_path.name
        if out_path.exists() and out_path.stat().st_size > 20:
            skipped += 1
            continue
        data = _yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not data or not isinstance(data, dict):
            skipped += 1
            continue
        body = data.get("body", "")
        if not body or len(body) < 20:
            skipped += 1
            continue
        work.append((yaml_path, data, body))

    total = len(work)
    print(f"\nTeacher bank atoms to translate: {total} (skipped {skipped} already done)")
    if not work:
        return 0, skipped

    translated = 0
    lock = Lock()
    start_time = time.time()

    def _do_one(idx: int, yaml_path: Path, data: dict, body: str) -> bool:
        nonlocal translated
        locale_dir = yaml_path.parent / "locales" / locale
        out_path = locale_dir / yaml_path.name
        rel = yaml_path.relative_to(TEACHER_BANKS_ROOT)

        if dry_run:
            with lock:
                translated += 1
            return True

        zh_body = _translate_text(body, locale, ollama_url, model)
        if zh_body:
            locale_dir.mkdir(parents=True, exist_ok=True)
            out_data = dict(data)
            out_data["body"] = zh_body
            out_data["locale"] = locale
            out_path.write_text(
                _yaml.dump(out_data, allow_unicode=True, default_flow_style=False, width=200),
                encoding="utf-8",
            )
            with lock:
                translated += 1
                elapsed = time.time() - start_time
                rate = translated / max(elapsed, 1) * 60
                eta = (total - translated) / max(rate, 0.1)
                print(f"  [{translated}/{total}] {rel} OK ({len(zh_body)} chars) {rate:.0f}/min ETA:{eta:.0f}min")
            return True
        else:
            with lock:
                print(f"  [?/{total}] {rel} FAILED")
            return False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_do_one, i, p, d, b): i for i, (p, d, b) in enumerate(work)}
        for f in as_completed(futures):
            f.result()

    return translated, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch translate atoms to target locale via Ollama.")
    parser.add_argument("--locale", required=True, help="Target locale (e.g. zh-TW, ja-JP)")
    parser.add_argument("--persona", default=None, help="Translate single persona only")
    parser.add_argument("--teacher-banks-only", action="store_true", help="Translate teacher banks only")
    parser.add_argument("--persona-atoms-only", action="store_true", help="Translate persona atoms only")
    parser.add_argument("--ollama-url", default=None, help="Ollama URL (default: QWEN_BASE_URL or Pearl Star)")
    parser.add_argument("--model", default="qwen3:14b", help="Ollama model")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ollama_url = args.ollama_url or os.environ.get("QWEN_BASE_URL", "").replace("/v1", "") or "http://192.168.1.112:11434"
    locale_name = LOCALE_NAMES.get(args.locale, args.locale)

    print(f"{'='*60}")
    print(f"Batch Atom Translation → {args.locale} ({locale_name})")
    print(f"Ollama: {ollama_url} / {args.model}")
    print(f"{'='*60}")

    total_translated = 0
    total_skipped = 0

    if not args.teacher_banks_only:
        t, s = translate_persona_atoms(args.locale, ollama_url, args.model, args.persona, args.dry_run, workers=args.workers)
        total_translated += t
        total_skipped += s

    if not args.persona_atoms_only:
        t, s = translate_teacher_banks(args.locale, ollama_url, args.model, args.dry_run, workers=args.workers)
        total_translated += t
        total_skipped += s

    print(f"\n{'='*60}")
    print(f"DONE: {total_translated} translated, {total_skipped} skipped")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

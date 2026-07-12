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

from scripts.localization.run_translation_loop import format_canonical, parse_canonical
from scripts.localization.validate_cjk_atom import validate_locale_atom

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

PROSE_SYSTEM_PROMPTS = {
    "zh-TW": (
        "You are a professional translator. Translate the following English therapeutic/self-help "
        "PROSE ONLY into Traditional Chinese (繁體中文) suitable for Taiwan audiences. Maintain emotional "
        "tone, body-awareness language, and second-person address. Do NOT add headers, metadata, "
        "--- delimiters, or commentary. Output ONLY the translated prose."
    ),
    "zh-CN": (
        "You are a professional translator. Translate the following English therapeutic/self-help "
        "PROSE ONLY into Simplified Chinese (简体中文) suitable for Mainland China audiences. Maintain "
        "emotional tone, body-awareness language, and second-person address. Do NOT add headers, "
        "metadata, --- delimiters, or commentary. Output ONLY the translated prose."
    ),
    "ja-JP": (
        "You are a professional translator. Translate the following English therapeutic/self-help "
        "PROSE ONLY into Japanese (日本語). Use appropriate keigo for wellness content. Maintain "
        "emotional tone, body-awareness language, and second-person address. Do NOT add headers, "
        "metadata, --- delimiters, or commentary. Output ONLY the translated prose."
    ),
    "ko-KR": (
        "You are a professional translator. Translate the following English therapeutic/self-help "
        "PROSE ONLY into Korean (한국어). Use appropriate 존댓말 for wellness content. Maintain "
        "emotional tone, body-awareness language, and second-person address. Do NOT add headers, "
        "metadata, --- delimiters, or commentary. Output ONLY the translated prose."
    ),
}

# Legacy whole-block prompts for non-CANONICAL bodies (teacher banks without ## headers).
LEGACY_SYSTEM_PROMPTS = {
    "zh-TW": "You are a professional translator. Translate the following English therapeutic/self-help text into Traditional Chinese (繁體中文). Output ONLY the translation.",
    "zh-CN": "You are a professional translator. Translate the following English therapeutic/self-help text into Simplified Chinese (简体中文). Output ONLY the translation.",
    "ja-JP": "You are a professional translator. Translate the following English therapeutic/self-help text into Japanese (日本語). Output ONLY the translation.",
    "ko-KR": "You are a professional translator. Translate the following English therapeutic/self-help text into Korean (한국어). Output ONLY the translation.",
}


# Atoms store multiple variants in one file, each introduced by a `## ` header
# (e.g. "## HOOK v01", "## HOOK v02"). The pre-fix code truncated the whole
# concatenated atom at 8000 chars before translating, silently dropping every
# variant past the cutoff (e.g. a 32-variant REFLECTION atom kept only 4).
# We now chunk per variant: split on `## ` headers, translate each segment
# independently (no input truncation), then reassemble — and assert the output
# variant count matches the input so variant loss fails loudly instead of
# shipping a corrupted, half-translated atom.
_VARIANT_SPLIT_RE = re.compile(r"(?m)^(?=##\s)")


def _split_variants(text: str) -> list[str]:
    """Split atom text into segments at each `## ` variant header.

    Any preamble before the first `## ` header is kept as its own leading
    segment so nothing is lost. Each `## ...` variant becomes one segment
    (header + its body). Returns the original text as a single segment when no
    `## ` headers are present (e.g. teacher-bank bodies).
    """
    parts = [p for p in _VARIANT_SPLIT_RE.split(text) if p.strip()]
    return parts if parts else [text]


def _count_variant_headers(text: str) -> int:
    """Count `## ` variant headers in a block of atom text."""
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("## "))


def _ollama_generate(
    prompt: str,
    ollama_url: str,
    model: str,
    num_predict: int,
    *,
    max_retries: int = 3,
) -> str | None:
    """Ollama /api/generate with retry on empty/short completions.

    Empty replies are a known intermittent Ollama flake; retry before failing
    the atom so a single blank completion does not drop a whole file.
    """
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.25, "num_predict": num_predict},
    }).encode("utf-8")
    attempts = max(1, int(max_retries))

    for attempt in range(1, attempts + 1):
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
            if len(reply) > 10:
                return reply
            if attempt < attempts:
                print(
                    f"    WARN: empty Ollama completion "
                    f"(attempt {attempt}/{attempts}); retrying"
                )
        except Exception as e:
            if attempt < attempts:
                print(
                    f"    WARN: Ollama error on attempt {attempt}/{attempts}: {e}; retrying"
                )
            else:
                print(f"    ERROR: {e}")
                return None
    return None


def _translate_prose(prose: str, locale: str, ollama_url: str, model: str) -> str | None:
    """Translate a single prose block (no structural tokens)."""
    system = PROSE_SYSTEM_PROMPTS.get(locale, PROSE_SYSTEM_PROMPTS["zh-TW"])
    num_predict = max(2048, min(len(prose) * 4, 16000))
    out = _ollama_generate(f"{system}\n\n{prose.strip()}", ollama_url, model, num_predict)
    return out.strip() if out else None


def _translate_canonical_atom(text: str, locale: str, ollama_url: str, model: str) -> str | None:
    """Translate CANONICAL.txt: prose only; headers + metadata preserved verbatim from en."""
    variants = parse_canonical(text)
    if not variants:
        return None

    translated: list[tuple[str, str, str]] = []
    for header, metadata, prose in variants:
        if not prose.strip():
            translated.append((header, metadata, prose))
            continue
        out = _translate_prose(prose, locale, ollama_url, model)
        if out is None:
            print(f"    ERROR: prose translation empty for {header}")
            return None
        translated.append((header, metadata, out))

    return format_canonical(translated)


def _translate_text(text: str, locale: str, ollama_url: str, model: str) -> str | None:
    """Translate atom text via Ollama.

    CANONICAL.txt with ## variant headers: parse structure, translate prose only,
    reattach en-source headers/metadata verbatim (eliminates #1590 parse-fail class).
    Plain bodies (teacher banks): legacy per-segment translation.
    """
    canonical_variants = parse_canonical(text)
    if canonical_variants:
        return _translate_canonical_atom(text, locale, ollama_url, model)

    system = LEGACY_SYSTEM_PROMPTS.get(locale, LEGACY_SYSTEM_PROMPTS["zh-TW"])
    segments = _split_variants(text)
    in_variants = _count_variant_headers(text)

    translated_segments: list[str] = []
    for seg in segments:
        num_predict = max(2048, min(len(seg) * 4, 16000))
        prompt = f"{system}\n\n{seg}"
        out = _ollama_generate(prompt, ollama_url, model, num_predict)
        if out is None:
            print(f"    ERROR: variant translation returned empty ({len(seg)} chars)")
            return None
        translated_segments.append(out.strip())

    combined = "\n\n".join(translated_segments).strip()
    out_variants = _count_variant_headers(combined)
    if out_variants != in_variants:
        print(
            f"    ERROR: variant count mismatch (in={in_variants} out={out_variants}); "
            f"dropping translation to avoid silent loss"
        )
        return None

    return combined if len(combined) > 10 else None


def _write_locale_atom(out_path: Path, translated: str, *, validate: bool = True) -> bool:
    """Write translated atom; optional parse-sweep pre-check."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(translated, encoding="utf-8")
    if not validate:
        return True
    ok, reasons = validate_locale_atom(out_path)
    if not ok:
        out_path.unlink(missing_ok=True)
        print(f"    REJECTED (structural): {'; '.join(reasons)}")
        return False
    return True


def translate_persona_atoms(
    locale: str,
    ollama_url: str,
    model: str,
    persona_filter: str | None = None,
    dry_run: bool = False,
    workers: int = 4,
    paths_file: Path | None = None,
    force: bool = False,
) -> tuple[int, int]:
    """Translate all persona atoms to locale using parallel workers."""
    # Find all English CANONICAL.txt files
    if paths_file and paths_file.exists():
        rel_paths = [
            line.strip().split("\t")[0]
            for line in paths_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        all_files = []
        for rel in rel_paths:
            if f"/locales/{locale}/" in rel:
                en_rel = rel.replace(f"/locales/{locale}/", "/")
            else:
                en_rel = rel
            p = REPO_ROOT / en_rel
            if p.exists():
                all_files.append(p)
        all_files = sorted(set(all_files))
    else:
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
        if out_path.exists() and out_path.stat().st_size > 20 and not force:
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
        if zh and _write_locale_atom(out_path, zh):
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
    parser.add_argument("--paths-file", default=None, help="Re-translate specific en atom paths (from backlog manifest)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing locale files (backlog re-run)")
    args = parser.parse_args()

    paths_file = Path(args.paths_file) if args.paths_file else None

    ollama_url = args.ollama_url or os.environ.get("QWEN_BASE_URL", "").replace("/v1", "") or "http://192.168.1.112:11434"
    locale_name = LOCALE_NAMES.get(args.locale, args.locale)

    print(f"{'='*60}")
    print(f"Batch Atom Translation → {args.locale} ({locale_name})")
    print(f"Ollama: {ollama_url} / {args.model}")
    print(f"{'='*60}")

    total_translated = 0
    total_skipped = 0

    if not args.teacher_banks_only:
        t, s = translate_persona_atoms(
            args.locale, ollama_url, args.model, args.persona, args.dry_run,
            workers=args.workers, paths_file=paths_file, force=args.force,
        )
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

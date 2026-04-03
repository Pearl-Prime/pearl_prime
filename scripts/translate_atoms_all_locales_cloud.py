#!/usr/bin/env python3
"""
Translate bestseller atom CANONICAL.txt files (PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY)
from English to CJK locales via Qwen on Alibaba Cloud Dashscope.

Outputs: atoms/{persona}/{topic}/{SLOT}/locales/{locale}/CANONICAL.txt

Requires DASHSCOPE_API_KEY for non-dry-run. Optional: DASHSCOPE_MODEL (default qwen-plus).
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.llm_client import call_llm  # noqa: E402

logger = logging.getLogger("translate_atoms_cloud")

SLOT_TYPES = ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "STORY")
ENGINE_DIRS = ("comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher")
ALL_ATOM_TYPES = SLOT_TYPES + ENGINE_DIRS

CJK6_LOCALES = ("ja-JP", "ko-KR", "zh-CN", "zh-HK", "zh-SG", "zh-TW")

LOCALE_NAMES: dict[str, str] = {
    "ja-JP": "Japanese (日本語)",
    "ko-KR": "Korean (한국어)",
    "zh-CN": "Simplified Chinese (简体中文)",
    "zh-HK": "Traditional Chinese — Hong Kong (繁體中文 — 香港)",
    "zh-SG": "Simplified Chinese — Singapore (简体中文 — 新加坡)",
    "zh-TW": "Traditional Chinese — Taiwan (繁體中文 — 台灣)",
}

# Same structure as prose_resolver: split on \n---\s*\n
VARIANT_RE = re.compile(
    r"(^##\s+\S+\s+v\d+\s*)\s*\n---\s*\n([\s\S]*?)---\s*\n(.*?)(?=\n---\s*\n\n##|\n---\s*\Z)",
    re.MULTILINE | re.DOTALL,
)
VARIANT_RE_LEGACY = re.compile(
    r"(^##\s+\S+\s+v\d+\s*)\s*\n---\s*\n\s*---\s*\n(.*?)(?=\n---\s*\n\n##|\n---\s*\Z)",
    re.MULTILINE | re.DOTALL,
)


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


def parse_canonical(text: str) -> list[tuple[str, str, str]]:
    """Extract (header, metadata, prose) per variant. Handles both legacy (no metadata) and engine (with metadata) formats."""
    results = list(VARIANT_RE.finditer(text))
    if results:
        return [(m.group(1).strip(), m.group(2).strip(), m.group(3).strip()) for m in results]
    legacy = list(VARIANT_RE_LEGACY.finditer(text))
    return [(m.group(1).strip(), "", m.group(2).strip()) for m in legacy]


def format_canonical(variants: list[tuple[str, str, str] | tuple[str, str]]) -> str:
    """Rebuild CANONICAL.txt from (header, metadata, prose) or (header, prose) tuples."""
    blocks: list[str] = []
    for v in variants:
        if len(v) == 3:
            header, meta, prose = v
            if meta.strip():
                blocks.append(f"{header}\n---\n{meta}\n---\n{prose}\n---")
            else:
                blocks.append(f"{header}\n---\n\n---\n{prose}\n---")
        else:
            header, prose = v
            blocks.append(f"{header}\n---\n\n---\n{prose}\n---")
    return "\n\n".join(blocks) + "\n"


def validate_translation(
    source_variants: list[tuple[str, str]],
    out_text: str,
) -> tuple[bool, str]:
    """Post-translation checks: count, non-empty, not identical to English, not header-only."""
    out_vars = parse_canonical(out_text)
    if len(out_vars) != len(source_variants):
        return False, (
            f"variant count mismatch: expected {len(source_variants)}, got {len(out_vars)}"
        )
    for i, ((src_h, src_p), (out_h, out_p)) in enumerate(
        zip(source_variants, out_vars)
    ):
        if src_h.strip() != out_h.strip():
            return False, f"variant {i + 1}: header must stay English; mismatch"
        if not out_p.strip():
            return False, f"variant {i + 1}: empty prose"
        if out_p.strip() == src_p.strip():
            return False, f"variant {i + 1}: prose identical to English (likely untranslated)"
        # Header/delimiters only: very short or no letters (heuristic)
        if len(out_p.strip()) < 4:
            return False, f"variant {i + 1}: prose too short"
    return True, "ok"


def discover_atoms(
    atoms_root: Path,
    persona: str | None = None,
    topic: str | None = None,
    slot: str | None = None,
) -> list[tuple[str, str, str, Path]]:
    """
    Return manifest: (persona, topic, slot_type, filepath) for English sources.
    Skips locales/ subtrees.
    """
    if slot:
        upper = slot.upper()
        lower = slot.lower()
        if upper in SLOT_TYPES:
            slots = (upper,)
        elif lower in ENGINE_DIRS:
            slots = (lower,)
        elif lower in ("engine", "engines"):
            slots = ENGINE_DIRS
        else:
            slots = (slot,)
    else:
        slots = ALL_ATOM_TYPES

    manifest: list[tuple[str, str, str, Path]] = []
    for st in slots:
        for path in atoms_root.rglob(f"{st}/CANONICAL.txt"):
            if "locales" in path.parts:
                continue
            try:
                rel = path.relative_to(atoms_root)
            except ValueError:
                continue
            parts = rel.parts
            if len(parts) < 4:
                continue
            p_persona, p_topic, p_slot, name = parts[0], parts[1], parts[2], parts[3]
            if name != "CANONICAL.txt" or p_slot != st:
                continue
            if persona and p_persona != persona:
                continue
            if topic and p_topic != topic:
                continue
            manifest.append((p_persona, p_topic, st, path))

    manifest.sort(key=lambda x: (x[0], x[1], x[2], str(x[3])))
    return manifest


def output_path_for(
    atoms_root: Path,
    persona: str,
    topic: str,
    slot_type: str,
    locale: str,
) -> Path:
    return atoms_root / persona / topic / slot_type / "locales" / locale / "CANONICAL.txt"


def system_prompt(locale: str) -> str:
    locale_name = LOCALE_NAMES.get(locale, locale)
    return (
        "You are a professional translator specializing in therapeutic and "
        f"self-help content. Translate the following from English to {locale_name}.\n"
        "Rules:\n"
        "1. Preserve the second-person voice ('You are allowed to...')\n"
        "2. Preserve emotional tone — gentle, validating, zero judgment\n"
        "3. Use locale-native phrasing (not translationese)\n"
        "4. Preserve the ## TYPE vNN headers exactly as-is (English)\n"
        "5. Preserve the --- delimiters exactly as-is\n"
        "6. Do not add explanations or notes\n"
        "7. Return ONLY the translated text in identical format"
    )


def translate_file(
    source_path: Path,
    locale: str,
    cfg: dict[str, Any],
    max_retries: int = 3,
) -> str:
    """One API call per file; returns translated full file text."""
    text = source_path.read_text(encoding="utf-8")
    sys_p = system_prompt(locale)
    last_err: Exception | None = None
    # Initial try + max_retries with exponential backoff 2^n seconds (cap 60s)
    for attempt in range(max_retries + 1):
        try:
            return call_llm(
                sys_p,
                text,
                cfg,
                role="draft",
                temperature=0.25,
                max_tokens=32000,
            )
        except Exception as e:
            last_err = e
            status = getattr(e, "status_code", None) or getattr(
                getattr(e, "response", None), "status_code", None
            )
            body = str(e).lower()
            retryable = status in (429, 500, 502, 503) or "429" in body or "rate" in body
            if not retryable or attempt >= max_retries:
                raise
            wait_s = min(60.0, float(2**attempt))
            logger.warning(
                "API error (attempt %s): %s; sleeping %.1fs",
                attempt + 1,
                e,
                wait_s,
            )
            time.sleep(wait_s)
    assert last_err is not None
    raise last_err


class RateLimiter:
    """Minimum interval between acquire() calls (global across threads)."""

    def __init__(self, interval_s: float) -> None:
        self._interval = interval_s
        self._lock = threading.Lock()
        self._last = 0.0

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait_t = self._interval - (now - self._last)
            if wait_t > 0:
                time.sleep(wait_t)
            self._last = time.monotonic()


def should_resume(
    out_path: Path,
    source_variants: list[tuple[str, str]],
) -> bool:
    if not out_path.is_file():
        return False
    try:
        txt = out_path.read_text(encoding="utf-8")
    except OSError:
        return False
    ok, _ = validate_translation(source_variants, txt)
    return ok


def run_job(
    item: tuple[str, str, str, Path],
    locale: str,
    atoms_root: Path,
    cfg: dict[str, Any],
    resume: bool,
    limiter: RateLimiter,
    dry_run: bool,
) -> tuple[str, str, str, str]:
    """Returns (persona, topic, slot, status_message)."""
    persona, topic, slot_type, src = item
    out_path = output_path_for(atoms_root, persona, topic, slot_type, locale)
    if dry_run:
        return persona, topic, slot_type, f"dry-run: would write {out_path}"

    src_text = src.read_text(encoding="utf-8")
    source_variants = parse_canonical(src_text)
    if len(source_variants) == 0:
        return (
            persona,
            topic,
            slot_type,
            f"skip: source has 0 variants (cannot translate empty file): {src}",
        )

    if resume and should_resume(out_path, source_variants):
        return persona, topic, slot_type, f"resume: skip existing valid {out_path}"

    limiter.acquire()
    raw = translate_file(src, locale, cfg)
    ok, msg = validate_translation(source_variants, raw)
    if not ok:
        return persona, topic, slot_type, f"validation failed: {msg}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(raw, encoding="utf-8")
    return persona, topic, slot_type, f"ok: {out_path}"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(
        description="Translate bestseller atoms to CJK locales (Dashscope/Qwen)"
    )
    ap.add_argument("--locale", help="Target locale (e.g. ja-JP)")
    ap.add_argument(
        "--all-locales",
        action="store_true",
        help="All 6 CJK locales",
    )
    ap.add_argument("--persona", help="Filter to one persona")
    ap.add_argument("--topic", help="Filter to one topic")
    ap.add_argument(
        "--slot",
        help="Filter to atom type: slot (PIVOT/TAKEAWAY/THREAD/PERMISSION/STORY), engine (comparison/false_alarm/grief/overwhelm/shame/spiral/watcher), or 'engines' for all 7",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Show manifest, don't translate",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Skip files that already have translations",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Concurrent API calls",
    )
    ap.add_argument(
        "--rate-limit",
        type=float,
        default=0.1,
        help="Seconds between API calls",
    )
    args = ap.parse_args()

    atoms_root = REPO_ROOT / "atoms"

    locales: list[str] = []
    if args.all_locales:
        locales = list(CJK6_LOCALES)
    elif args.locale:
        locales = [args.locale]
    else:
        print("Specify --locale or --all-locales", file=sys.stderr)
        return 2

    for loc in locales:
        if loc not in LOCALE_NAMES:
            logger.warning("Unknown locale %r — proceeding (prompt uses raw code)", loc)

    if not args.dry_run and not os.environ.get("DASHSCOPE_API_KEY", "").strip():
        print("DASHSCOPE_API_KEY is required unless --dry-run", file=sys.stderr)
        return 2

    manifest = discover_atoms(
        atoms_root,
        persona=args.persona,
        topic=args.topic,
        slot=args.slot,
    )
    total_files = len(manifest)
    total_variants = total_files * 20
    print(
        f"Manifest: {total_files} files, {total_variants} variants "
        f"(~{total_files * len(locales)} API calls for {len(locales)} locale(s))"
    )
    for row in manifest:
        print(f"  {row[0]}/{row[1]}/{row[2]} -> {row[3]}")

    if args.dry_run:
        return 0

    cfg: dict[str, Any] = {
        "draft_model": {
            "temperature": 0.25,
            "max_output_tokens": 32000,
            "timeout_seconds": 300,
        }
    }
    if os.environ.get("DASHSCOPE_MODEL", "").strip():
        cfg["draft_model"]["cloud_model_id"] = os.environ["DASHSCOPE_MODEL"].strip()

    limiter = RateLimiter(args.rate_limit)

    for locale in locales:
        print(f"\n--- locale {locale} ---")
        with ThreadPoolExecutor(max_workers=max(1, args.batch_size)) as ex:
            futures = [
                ex.submit(
                    run_job,
                    item,
                    locale,
                    atoms_root,
                    cfg,
                    args.resume,
                    limiter,
                    False,
                )
                for item in manifest
            ]
            for fut in as_completed(futures):
                p, t, s, msg = fut.result()
                print(f"  [{p}/{t}/{s}] {msg}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

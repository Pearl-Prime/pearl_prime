#!/usr/bin/env python3
"""
Translate bestseller atom CANONICAL.txt files (PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY)
from English to CJK locales via Qwen on Alibaba Cloud Dashscope.

Outputs: atoms/{persona}/{topic}/{SLOT}/locales/{locale}/CANONICAL.txt

Requires DASHSCOPE_API_KEY for non-dry-run. Optional: DASHSCOPE_MODEL (default qwen-plus).

DashScope-only (ignore Together when both keys exist): --dashscope-only or
PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY=1

Token spend estimate for --budget-cap-usd:
  LOCALIZATION_BLEND_USD_PER_MILLION_TOKENS (default 2.0)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.llm_client import call_llm_with_meta  # noqa: E402

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


def atom_key(persona: str, topic: str, slot_type: str) -> str:
    return f"{persona}/{topic}/{slot_type}"


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


def _variant_header_prose(v: tuple[str, str, str] | tuple[str, str]) -> tuple[str, str]:
    """Normalize parse_canonical rows to (header, prose)."""
    if len(v) == 3:
        return v[0], v[2]
    return v[0], v[1]


def validate_translation(
    source_variants: list[tuple[str, str, str] | tuple[str, str]],
    out_text: str,
) -> tuple[bool, str]:
    """Post-translation checks: count, non-empty, not identical to English, not header-only."""
    out_vars = parse_canonical(out_text)
    if len(out_vars) != len(source_variants):
        return False, (
            f"variant count mismatch: expected {len(source_variants)}, got {len(out_vars)}"
        )
    for i, (src_v, out_v) in enumerate(zip(source_variants, out_vars)):
        src_h, src_p = _variant_header_prose(src_v)
        out_h, out_p = _variant_header_prose(out_v)
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
) -> tuple[str, dict[str, Any]]:
    """One API call per file; returns (translated full file text, last response meta)."""
    text = source_path.read_text(encoding="utf-8")
    sys_p = system_prompt(locale)
    last_err: Exception | None = None
    last_meta: dict[str, Any] = {}
    # Initial try + max_retries with exponential backoff 2^n seconds (cap 60s)
    for attempt in range(max_retries + 1):
        try:
            out, meta = call_llm_with_meta(
                sys_p,
                text,
                cfg,
                role="draft",
                temperature=0.25,
                # Note: do NOT pass max_tokens here — let get_client_config() apply
                # per-provider caps (e.g. DeepSeek V3 hard limit is 8192).
            )
            last_meta = meta
            return out, meta
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


class BudgetTracker:
    """Thread-safe estimated spend from token usage."""

    def __init__(self, cap_usd: float | None) -> None:
        self.cap_usd = cap_usd
        self.blend_per_million = float(
            os.environ.get("LOCALIZATION_BLEND_USD_PER_MILLION_TOKENS", "2.0").strip() or "2.0"
        )
        self._lock = threading.Lock()
        self.total_tokens = 0
        self.estimated_usd = 0.0

    def add_usage(self, usage: dict[str, Any]) -> float:
        pt = int(usage.get("prompt_tokens") or 0)
        ct = int(usage.get("completion_tokens") or 0)
        tt_raw = usage.get("total_tokens")
        tt = int(tt_raw) if tt_raw is not None else pt + ct
        delta_usd = (float(tt) / 1_000_000.0) * self.blend_per_million
        with self._lock:
            self.total_tokens += int(tt)
            self.estimated_usd += delta_usd
        return delta_usd

    def over_cap(self) -> bool:
        if self.cap_usd is None or self.cap_usd <= 0:
            return False
        with self._lock:
            return self.estimated_usd >= self.cap_usd


def load_checkpoint_keys(path: Path | None, locale: str) -> set[str]:
    if path is None or not path.is_file():
        return set()
    keys: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("locale") == locale and "key" in row:
                keys.add(str(row["key"]))
    return keys


def append_checkpoint_line(path: Path | None, locale: str, key: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = json.dumps({"locale": locale, "key": key}, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(rec + "\n")


def append_log_line(path: Path | None, obj: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def should_resume(
    out_path: Path,
    source_variants: list[tuple[str, str, str] | tuple[str, str]],
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
    budget: BudgetTracker | None,
    halt: threading.Event | None,
    checkpoint_path: Path | None,
    log_path: Path | None,
    ck_done: set[str],
    ck_lock: threading.Lock,
) -> tuple[str, str, str, str]:
    """Returns (persona, topic, slot, status_message)."""
    persona, topic, slot_type, src = item
    out_path = output_path_for(atoms_root, persona, topic, slot_type, locale)
    key = atom_key(persona, topic, slot_type)

    if dry_run:
        return persona, topic, slot_type, f"dry-run: would write {out_path}"

    if halt is not None and halt.is_set():
        return persona, topic, slot_type, "skip: halted (budget or operator)"
    if budget is not None and budget.over_cap():
        if halt is not None:
            halt.set()
        return persona, topic, slot_type, "skip: budget cap reached"

    with ck_lock:
        in_ck = key in ck_done
    if in_ck and resume:
        return persona, topic, slot_type, f"resume: skip checkpoint {key}"

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

    if halt is not None and halt.is_set():
        return persona, topic, slot_type, "skip: halted (budget or operator)"
    if budget is not None and budget.over_cap():
        if halt is not None:
            halt.set()
        return persona, topic, slot_type, "skip: budget cap reached"

    limiter.acquire()
    if halt is not None and halt.is_set():
        return persona, topic, slot_type, "skip: halted (budget or operator)"
    if budget is not None and budget.over_cap():
        if halt is not None:
            halt.set()
        return persona, topic, slot_type, "skip: budget cap reached"

    try:
        raw, meta = translate_file(src, locale, cfg)
    except Exception as e:
        append_log_line(
            log_path,
            {"event": "error", "locale": locale, "key": key, "error": str(e)},
        )
        return persona, topic, slot_type, f"error: {e}"

    resp_model = (meta.get("model_response") or "").lower()
    if "qwen3" in resp_model:
        if halt is not None:
            halt.set()
        append_log_line(
            log_path,
            {
                "event": "abort_wrong_model_family",
                "locale": locale,
                "key": key,
                "model_response": meta.get("model_response"),
            },
        )
        return persona, topic, slot_type, "abort: API returned qwen3 model (use qwen2.5 only)"

    usage = meta.get("usage") or {}
    delta_usd = 0.0
    if budget is not None and isinstance(usage, dict):
        delta_usd = budget.add_usage(usage)
        if budget.over_cap() and halt is not None:
            halt.set()

    ok, msg = validate_translation(source_variants, raw)
    if not ok:
        append_log_line(
            log_path,
            {
                "event": "validation_failed",
                "locale": locale,
                "key": key,
                "message": msg,
                "model_response": meta.get("model_response"),
                "estimated_usd_delta": delta_usd,
            },
        )
        return persona, topic, slot_type, f"validation failed: {msg}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(raw, encoding="utf-8")

    append_log_line(
        log_path,
        {
            "event": "ok",
            "locale": locale,
            "key": key,
            "path": str(out_path.relative_to(REPO_ROOT)),
            "model_response": meta.get("model_response"),
            "usage": usage,
            "estimated_usd_delta": delta_usd,
            "latency_s": meta.get("latency_s"),
        },
    )
    append_checkpoint_line(checkpoint_path, locale, key)
    with ck_lock:
        ck_done.add(key)

    return persona, topic, slot_type, f"ok: {out_path}"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(
        description="Translate bestseller atoms to CJK locales (Dashscope/Qwen)"
    )
    ap.add_argument("--locale", help="Single target locale (e.g. ja-JP)")
    ap.add_argument(
        "--locales",
        nargs="+",
        metavar="LOCALE",
        help="One or more target locales (e.g. zh-CN zh-TW ja-JP)",
    )
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
        help="Show manifest summary only; no API calls; no files written",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Skip files that already have valid translations",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Concurrent API calls",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Alias for --batch-size",
    )
    ap.add_argument(
        "--rate-limit",
        type=float,
        default=0.1,
        help="Seconds between API calls (global throttle)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N atoms from the manifest (after filters)",
    )
    ap.add_argument(
        "--budget-cap-usd",
        type=float,
        default=None,
        help="Stop new work past this estimated USD (token-based; see LOCALIZATION_BLEND_USD_PER_MILLION_TOKENS)",
    )
    ap.add_argument(
        "--checkpoint-path",
        type=Path,
        default=None,
        help="Append JSONL checkpoint lines (locale + persona/topic/slot key)",
    )
    ap.add_argument(
        "--output-log",
        type=Path,
        default=None,
        help="Append JSONL per atom (ok, error, validation_failed)",
    )
    ap.add_argument(
        "--dashscope-only",
        action="store_true",
        help="Ignore TOGETHER_API_KEY (sets PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY)",
    )
    args = ap.parse_args()

    if args.dashscope_only:
        os.environ["PHOENIX_TRANSLATION_USE_DASHSCOPE_ONLY"] = "1"

    atoms_root = REPO_ROOT / "atoms"

    locales: list[str] = []
    if args.all_locales:
        locales = list(CJK6_LOCALES)
    elif args.locales:
        locales = list(args.locales)
    elif args.locale:
        locales = [args.locale]
    else:
        print("Specify --locale, --locales, or --all-locales", file=sys.stderr)
        return 2

    for loc in locales:
        if loc not in LOCALE_NAMES:
            logger.warning("Unknown locale %r — proceeding (prompt uses raw code)", loc)

    # Accept any of the supported providers; DeepSeek is now the preferred CJK provider.
    _has_llm_key = (
        os.environ.get("DEEPSEEK_API_KEY", "").strip()
        or os.environ.get("DASHSCOPE_API_KEY", "").strip()
        or os.environ.get("TOGETHER_API_KEY", "").strip()
        or os.environ.get("GOOGLE_AI_API_KEY", "").strip()
        or os.environ.get("CLOUDFLARE_AI_API_TOKEN", "").strip()
    )
    if not args.dry_run and not _has_llm_key:
        print(
            "No LLM API key found. Set DEEPSEEK_API_KEY (preferred), "
            "DASHSCOPE_API_KEY, TOGETHER_API_KEY, GOOGLE_AI_API_KEY, "
            "or CLOUDFLARE_AI_API_TOKEN unless --dry-run.",
            file=sys.stderr,
        )
        return 2

    manifest = discover_atoms(
        atoms_root,
        persona=args.persona,
        topic=args.topic,
        slot=args.slot,
    )
    if args.limit is not None and args.limit >= 0:
        manifest = manifest[: args.limit]

    total_files = len(manifest)
    workers = args.workers if args.workers is not None else args.batch_size
    workers = max(1, int(workers))

    print(
        f"Manifest: {total_files} files (~{total_files * len(locales)} API calls "
        f"for {len(locales)} locale(s), workers={workers})"
    )
    if args.dry_run:
        for row in manifest[:50]:
            print(f"  {row[0]}/{row[1]}/{row[2]} -> {row[3]}")
        if total_files > 50:
            print(f"  ... and {total_files - 50} more (omitted in dry-run preview)")
        print("Dry-run: no API calls, no files written.")
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
        budget_tracker: BudgetTracker | None = None
        if args.budget_cap_usd is not None:
            budget_tracker = BudgetTracker(cap_usd=float(args.budget_cap_usd))
        halt = threading.Event()
        ck_path = args.checkpoint_path
        ck_done = load_checkpoint_keys(ck_path, locale)
        ck_lock = threading.Lock()
        pool: set[Any] = set()
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for item in manifest:
                pool.add(
                    ex.submit(
                        run_job,
                        item,
                        locale,
                        atoms_root,
                        cfg,
                        args.resume,
                        limiter,
                        False,
                        budget_tracker,
                        halt,
                        ck_path,
                        args.output_log,
                        ck_done,
                        ck_lock,
                    )
                )
            while pool:
                done, pool = wait(pool, return_when=FIRST_COMPLETED)
                for fut in done:
                    p, t, s, msg = fut.result()
                    print(f"  [{p}/{t}/{s}] {msg}")
                    if budget_tracker is not None and budget_tracker.over_cap():
                        print(
                            f"BUDGET_CAP: estimated ${budget_tracker.estimated_usd:.4f} "
                            f">= cap ${budget_tracker.cap_usd:.4f}; halting new work.",
                            file=sys.stderr,
                        )
                        halt.set()
                if halt.is_set() and budget_tracker is not None and budget_tracker.over_cap():
                    for fut in pool:
                        fut.cancel()
                    pool.clear()
                    break

        if budget_tracker is not None:
            print(
                f"Locale {locale} budget summary: "
                f"est_usd=${budget_tracker.estimated_usd:.4f} "
                f"total_tokens={budget_tracker.total_tokens} "
                f"(blend ${budget_tracker.blend_per_million}/1M tokens)"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())

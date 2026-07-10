#!/usr/bin/env python3
"""
Translate SOURCE_OF_TRUTH/teacher_banks/**/approved_atoms/{SLOT}/*.yaml atoms
into locale-specific SOURCE_OF_TRUTH/teacher_banks/**/approved_atoms_localized/{locale}/{SLOT}/*.yaml
files.

This is a SEPARATE lane from scripts/translate_atoms_all_locales_cloud.py, which
owns the persona/topic bestseller-atom tree (atoms/{persona}/{topic}/{slot}/
CANONICAL.txt — plain-text, multi-variant files). Teacher-bank atoms are a
different shape entirely: one structured YAML file per atom, with a single
`body` string plus teacher/provenance metadata fields that vary per slot type
(hook_type, story_origin, mechanism_depth, etc.). Neither discover_atoms() nor
output_path_for() in that script walks SOURCE_OF_TRUTH/teacher_banks/** (grep
confirmed 2026-07-10), so this narrow script exists to own that surface without
forcing a CANONICAL.txt-shaped rewrite onto a YAML-shaped problem.

Reuses the shared LLM client (scripts/localization/llm_client.py) and the
locale name table from scripts/translate_atoms_all_locales_cloud.py — no
duplicated provider-routing logic.

LLM TIER POLICY (CLAUDE.md, mandatory): this script hard-refuses to run a real
(non-dry-run) translation unless the resolved LLM client mode is "ollama"
(Qwen on Pearl Star, Tier 2 — free, unattended). Any banned paid-cloud key
present in the environment (DEEPSEEK_API_KEY, TOGETHER_API_KEY,
GOOGLE_AI_API_KEY, CLOUDFLARE_AI_API_TOKEN, DASHSCOPE_API_KEY) is unset for
the lifetime of this process before resolving the client, so a leftover
keychain-loaded key can never silently route a real API call to a paid
provider.

Usage:
  # Preflight only
  python3 scripts/localization/translate_teacher_bank_atoms.py --dry-run \
      --teacher kenjin --locale ja-JP

  # Real batch (Ollama/Pearl Star only)
  export OLLAMA_HOST="http://pearlstar.tail7fd910.ts.net:11434"
  export OLLAMA_MODEL="qwen2.5:14b"
  python3 scripts/localization/translate_teacher_bank_atoms.py \
      --locale ja-JP --teacher kenjin adi_da --resume \
      --checkpoint-path artifacts/localization/ja_jp_teacher_bank_20260710/checkpoint.jsonl \
      --output-log artifacts/localization/ja_jp_teacher_bank_20260710/output_log.jsonl
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.llm_client import call_llm_with_meta, get_client_config  # noqa: E402
from scripts.translate_atoms_all_locales_cloud import LOCALE_NAMES  # noqa: E402  (reuse, not duplicate)

logger = logging.getLogger("translate_teacher_bank_atoms")

TEACHER_BANKS_DIR = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

# Same slot list as scripts/localization/teacher_bank_locale_parity.py.
# TEACHER_DOCTRINE is deliberately excluded — it is teacher-level doctrine
# reference material, not a per-atom translatable slot.
SLOT_TYPES = [
    "COMPRESSION", "EXERCISE", "HOOK", "INTEGRATION", "PERMISSION",
    "PIVOT", "REFLECTION", "SCENE", "STORY", "TAKEAWAY", "THREAD",
]

# Banned-by-CLAUDE.md paid cloud keys. Unset before resolving the LLM client
# so this script can never silently fall through to a paid provider.
_BANNED_PAID_ENV_KEYS = (
    "DEEPSEEK_API_KEY",
    "TOGETHER_API_KEY",
    "GOOGLE_AI_API_KEY",
    "CLOUDFLARE_AI_API_TOKEN",
    "DASHSCOPE_API_KEY",
)

# Unicode ranges used as a cheap "did this actually translate" sanity check.
_LOCALE_SCRIPT_RANGES: dict[str, list[tuple[int, int]]] = {
    "ja-JP": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],  # hiragana/katakana + kanji
    "ko-KR": [(0xAC00, 0xD7A3)],  # hangul syllables
    "zh-CN": [(0x4E00, 0x9FFF)],
    "zh-TW": [(0x4E00, 0x9FFF)],
    "zh-HK": [(0x4E00, 0x9FFF)],
    "zh-SG": [(0x4E00, 0x9FFF)],
}


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


def atom_key(teacher: str, slot: str, atom_id: str) -> str:
    return f"{teacher}/{slot}/{atom_id}"


def discover_atoms(
    teachers: list[str] | None = None,
    slots: list[str] | None = None,
) -> list[tuple[str, str, str, Path]]:
    """Return manifest: (teacher, slot, atom_id, en_source_path)."""
    if not TEACHER_BANKS_DIR.is_dir():
        return []
    slot_filter = set(s.upper() for s in slots) if slots else None
    manifest: list[tuple[str, str, str, Path]] = []
    for teacher_dir in sorted(TEACHER_BANKS_DIR.iterdir()):
        if not teacher_dir.is_dir() or teacher_dir.name.startswith("."):
            continue
        teacher = teacher_dir.name
        if teachers and teacher not in teachers:
            continue
        approved = teacher_dir / "approved_atoms"
        if not approved.is_dir():
            continue
        for slot in SLOT_TYPES:
            if slot_filter and slot not in slot_filter:
                continue
            slot_dir = approved / slot
            if not slot_dir.is_dir():
                continue
            for f in sorted(slot_dir.iterdir()):
                if f.suffix != ".yaml":
                    continue
                atom_id = f.stem
                manifest.append((teacher, slot, atom_id, f))
    return manifest


def output_path_for(teacher: str, slot: str, atom_id: str, locale: str) -> Path:
    return (
        TEACHER_BANKS_DIR / teacher / "approved_atoms_localized" / locale / slot
        / f"{atom_id}_{locale}.yaml"
    )


def system_prompt(locale: str, teacher: str) -> str:
    locale_name = LOCALE_NAMES.get(locale, locale)
    return (
        "You are a professional literary translator specializing in "
        "contemplative / therapeutic teaching content. Translate the "
        f"following single passage from English into {locale_name}.\n"
        f"The passage is spoken in the voice of a teacher persona named "
        f"'{teacher}' inside a fictional wellness/self-help catalog "
        "(not a real historical or religious figure's verbatim words) — "
        "preserve its established tone: direct, embodied, non-judgmental, "
        "teacherly.\n"
        "Rules:\n"
        "1. Translate faithfully — preserve the meaning and argument "
        "structure of the source; do not summarize, expand, or invent new "
        "content or examples not present in the English.\n"
        "2. Preserve person/voice (second-person address stays second-person, "
        "etc.) and preserve paragraph breaks.\n"
        "3. Use natural, locale-native phrasing — not literal/mechanical "
        "translationese.\n"
        "4. Do not translate the teacher's proper name if one appears.\n"
        "5. Do not add explanations, notes, quotation marks around the "
        "whole passage, or any text besides the translation itself. This "
        "includes inline parentheticals that comment on your own translation "
        "choices (e.g. explaining that a term is 'kept as in the original' "
        "or 'cannot be directly translated') — never do this, in English or "
        "in the target language.\n"
        "6. If a term or concept has no clean equivalent in the target "
        "language, translate it confidently anyway (transliterate into the "
        "target script if needed) rather than leaving it in English or "
        "commenting on the difficulty.\n"
        "7. Return ONLY the translated passage text."
    )


def _script_ok(locale: str, text: str) -> bool:
    ranges = _LOCALE_SCRIPT_RANGES.get(locale)
    if not ranges:
        # Non-CJK6 locale (EU) — this script is CJK6-shaped only for now;
        # fall back to "non-empty and differs from ASCII-only" as a weak check.
        return any(ord(ch) > 127 for ch in text)
    for ch in text:
        cp = ord(ch)
        for lo, hi in ranges:
            if lo <= cp <= hi:
                return True
    return False


# Substrings that indicate the model leaked meta-commentary / a self-correction
# note into the body instead of returning only the translation (rule 5 in
# system_prompt()). Found in the wild during this session's QA pass on
# junko_PERMISSION_001 — the model appended "(Note: ... Let me correct it for
# natural flow.)" plus a duplicated corrected sentence.
_LEAK_MARKERS = (
    "(note", "note:", "let me correct", "for natural flow", "i apologize",
    "as an ai", "here is the translation", "here's the translation",
    "translated text", "翻訳します", "翻訳:",
    # Japanese-language self-referential translation-choice commentary
    # (found in the wild: junko_PERMISSION_003 — "councill" left untranslated
    # with an inline note explaining it couldn't be translated directly).
    "直接翻訳", "原文のまま", "翻訳できない", "翻訳が難しい", "訳せない",
)


def validate_translation(locale: str, source_body: str, translated_body: str) -> tuple[bool, str]:
    t = translated_body.strip()
    if not t:
        return False, "empty translation"
    if t == source_body.strip():
        return False, "identical to English source (likely untranslated)"
    if len(t) < 4:
        return False, "translation too short"
    if not _script_ok(locale, t):
        return False, f"translation contains no {locale} script characters"
    t_lower = t.lower()
    for marker in _LEAK_MARKERS:
        if marker in t_lower:
            return False, f"leaked meta-commentary detected (marker: {marker!r})"
    # CJK6 outputs should be almost entirely non-Latin; a large run of ASCII
    # letters indicates leaked English commentary rather than a clean
    # translation (proper nouns aside, which are short).
    if locale in _LOCALE_SCRIPT_RANGES:
        ascii_letters = sum(1 for ch in t if ch.isascii() and ch.isalpha())
        if ascii_letters > max(20, int(0.15 * len(t))):
            return False, f"suspiciously high ASCII-letter count ({ascii_letters}/{len(t)}) — possible leaked commentary"
    return True, "ok"


def load_checkpoint_keys(path: Path | None) -> set[str]:
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
            if "key" in row:
                keys.add(str(row["key"]))
    return keys


def append_checkpoint_line(path: Path | None, key: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"key": key}, ensure_ascii=False) + "\n")


def append_log_line(path: Path | None, obj: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _call_with_llm_retries(
    sys_p: str,
    source_body: str,
    cfg: dict[str, Any],
    temperature: float,
    max_retries: int,
) -> tuple[str, dict[str, Any], Exception | None]:
    """Call the LLM, retrying on transient (429/5xx/timeout) errors only."""
    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            out_text, meta = call_llm_with_meta(
                sys_p, source_body, cfg, role="draft", temperature=temperature,
            )
            return out_text, meta, None
        except Exception as e:  # noqa: BLE001
            last_err = e
            status = getattr(e, "status_code", None) or getattr(
                getattr(e, "response", None), "status_code", None
            )
            body_s = str(e).lower()
            retryable = status in (429, 500, 502, 503) or "429" in body_s or "rate" in body_s or "timeout" in body_s
            if not retryable or attempt >= max_retries:
                return "", {}, e
            wait_s = min(60.0, float(2**attempt))
            logger.warning("retryable error (attempt %s): %s; sleeping %.1fs", attempt + 1, e, wait_s)
            time.sleep(wait_s)
    return "", {}, last_err


def translate_one(
    teacher: str,
    slot: str,
    atom_id: str,
    src_path: Path,
    locale: str,
    cfg: dict[str, Any],
    max_retries: int = 3,
    max_validation_retries: int = 2,
) -> tuple[bool, str, dict[str, Any]]:
    """Translate one atom and write its output file. Returns (ok, message, meta)."""
    raw = yaml.safe_load(src_path.read_text(encoding="utf-8")) or {}
    source_body = str(raw.get("body", "")).strip()
    if not source_body:
        return False, "source atom has empty body", {}

    sys_p = system_prompt(locale, teacher)
    last_validation_msg = ""
    meta: dict[str, Any] = {}
    # Outer loop: re-roll on validation failure (e.g. leaked meta-commentary),
    # not just on transient API errors. Nudge temperature up slightly each
    # retry to escape a deterministic bad pattern (observed: the model can
    # consistently leave one ambiguous term untranslated across identical
    # low-temperature calls — see junko_PERMISSION_003 in this session's QA).
    for v_attempt in range(max_validation_retries + 1):
        temperature = 0.3 + 0.15 * v_attempt
        out_text, meta, err = _call_with_llm_retries(sys_p, source_body, cfg, temperature, max_retries)
        if err is not None:
            return False, f"LLM call failed: {err}", {}

        ok, msg = validate_translation(locale, source_body, out_text)
        if ok:
            out_dict = dict(raw)
            out_dict["body"] = out_text.strip()
            out_path = output_path_for(teacher, slot, atom_id, locale)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(out_dict, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            return True, f"wrote {out_path.relative_to(REPO_ROOT)}", meta

        last_validation_msg = msg
        if v_attempt < max_validation_retries:
            logger.warning(
                "validation failed (attempt %s/%s) for %s/%s/%s: %s; retrying",
                v_attempt + 1, max_validation_retries + 1, teacher, slot, atom_id, msg,
            )

    return False, f"validation failed after {max_validation_retries + 1} attempts: {last_validation_msg}", meta


def resolve_ollama_only_client(role_cfg: dict[str, Any]) -> dict[str, Any]:
    """Force-resolve the LLM client to Ollama mode only. Raises RuntimeError otherwise."""
    for k in _BANNED_PAID_ENV_KEYS:
        if os.environ.pop(k, None):
            logger.warning("Unset banned paid-cloud env var %s for this process (LLM Tier Policy).", k)
    params = get_client_config(role_cfg)
    if params["mode"] != "ollama":
        raise RuntimeError(
            "Refusing to run: resolved LLM client mode is "
            f"'{params['mode']}', not 'ollama'. CLAUDE.md LLM Tier Policy requires "
            "Qwen via Ollama on Pearl Star for this pipeline step. Set OLLAMA_HOST "
            "(e.g. http://pearlstar.tail7fd910.ts.net:11434) and OLLAMA_MODEL "
            "(e.g. qwen2.5:14b), and ensure no paid-cloud key is set."
        )
    return params


def main() -> int:
    ap = argparse.ArgumentParser(description="Translate teacher-bank atoms to a locale")
    ap.add_argument("--locale", default="ja-JP")
    ap.add_argument("--teacher", nargs="+", default=None, help="Restrict to these teacher ids")
    ap.add_argument("--slot", nargs="+", default=None, help="Restrict to these slot types")
    ap.add_argument("--max-atoms", type=int, default=None, help="Cap number of atoms translated this run")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--rate-limit-s", type=float, default=1.0, help="Min seconds between LLM calls")
    ap.add_argument("--checkpoint-path", type=Path, default=None)
    ap.add_argument("--output-log", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    manifest = discover_atoms(teachers=args.teacher, slots=args.slot)
    ck_done = load_checkpoint_keys(args.checkpoint_path) if args.resume else set()

    jobs: list[tuple[str, str, str, Path]] = []
    for teacher, slot, atom_id, src in manifest:
        key = atom_key(teacher, slot, atom_id)
        out_path = output_path_for(teacher, slot, atom_id, args.locale)
        if args.resume and (key in ck_done or out_path.is_file()):
            continue
        jobs.append((teacher, slot, atom_id, src))

    if args.max_atoms is not None:
        jobs = jobs[: args.max_atoms]

    print(f"Manifest: {len(manifest)} atoms total; {len(jobs)} jobs to run this invocation (locale={args.locale})")
    if args.dry_run:
        for teacher, slot, atom_id, src in jobs[:20]:
            print(f"  dry-run: would translate {teacher}/{slot}/{atom_id} -> {output_path_for(teacher, slot, atom_id, args.locale).relative_to(REPO_ROOT)}")
        if len(jobs) > 20:
            print(f"  ... and {len(jobs) - 20} more")
        return 0

    if not jobs:
        print("Nothing to do.")
        return 0

    role_cfg: dict[str, Any] = {}
    try:
        params = resolve_ollama_only_client(role_cfg)
    except RuntimeError as e:
        print(f"BLOCKER: {e}", file=sys.stderr)
        return 2
    print(f"LLM client: ollama mode, base_url={params['base_url']}, model={params['model_id']}")

    ok_count = 0
    fail_count = 0
    last_call = 0.0
    for i, (teacher, slot, atom_id, src) in enumerate(jobs, start=1):
        elapsed_since = time.monotonic() - last_call
        if elapsed_since < args.rate_limit_s:
            time.sleep(args.rate_limit_s - elapsed_since)
        last_call = time.monotonic()

        key = atom_key(teacher, slot, atom_id)
        t0 = time.time()
        ok, msg, meta = translate_one(teacher, slot, atom_id, src, args.locale, role_cfg)
        dt = time.time() - t0
        status = "OK" if ok else "FAIL"
        print(f"  [{i}/{len(jobs)}] {key}: {status} ({dt:.1f}s) {msg}")
        append_log_line(args.output_log, {
            "key": key, "ok": ok, "message": msg, "elapsed_s": round(dt, 2), "meta": meta,
        })
        if ok:
            ok_count += 1
            append_checkpoint_line(args.checkpoint_path, key)
        else:
            fail_count += 1

    print(f"\nDone: {ok_count} translated, {fail_count} failed, out of {len(jobs)} attempted this run.")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

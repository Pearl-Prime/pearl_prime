#!/usr/bin/env python3
"""
Translate Atoms All Locales — translate_atoms_all_locales.py

Translates en-US teacher atoms to target locales via Qwen (cloud or local).
Works for both Pearl News and Pearl Prime atom systems.

Architecture:
  - Reads en-US source atoms from pearl_news/atoms/teacher_quotes_practices/topic_*.yaml
  - For each target locale, generates locale-appropriate translations via Qwen
  - Writes translated atoms to pearl_news/atoms/teacher_quotes_practices/locales/<locale>/topic_<topic>.yaml
  - Updates translation_status from 'stub' to 'draft' after translation
  - Respects atom lifecycle: translated atoms start as status: starter (never auto-approved)

Translation quality contracts:
  - Preserve atom meaning: semantic fidelity to the original teaching
  - Locale-native phrasing: must read as if written by a native speaker, not translated
  - Cultural adaptation: reference locale-specific concepts where the teaching connects
  - Word count: 40-80 words per atom (same as English)
  - Tradition-specific: preserve tradition-specific terminology in the target language

LLM Mode:
  Cloud (recommended for GitHub Actions):
    Set DASHSCOPE_API_KEY env var → uses Alibaba Cloud Dashscope Qwen API.
    Optionally set DASHSCOPE_MODEL (default: qwen-plus).
  Local (development):
    No DASHSCOPE_API_KEY → uses LM Studio at 127.0.0.1:1234.
  Config: reads pearl_news/config/llm_expansion.yaml or config/audiobook_script/comparator_config.yaml.

Usage:
  # Translate all topics for ja-JP (dry-run first)
  python scripts/localization/translate_atoms_all_locales.py --locale ja-JP --dry-run
  python scripts/localization/translate_atoms_all_locales.py --locale ja-JP

  # Translate a specific topic for a specific locale
  python scripts/localization/translate_atoms_all_locales.py --locale zh-CN --topic climate

  # Translate all locales (batch)
  python scripts/localization/translate_atoms_all_locales.py --all-locales

  # Validate translation output without writing
  python scripts/localization/translate_atoms_all_locales.py --locale ja-JP --validate-only

  # Cloud mode (GitHub Actions)
  DASHSCOPE_API_KEY=sk-... python scripts/localization/translate_atoms_all_locales.py --all-locales
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any

import os

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _load_dotenv() -> None:
    """Load .env from repo root if present (no dependency required)."""
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

logger = logging.getLogger("translate_atoms")

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# ─── CONFIG ──────────────────────────────────────────────────────────────────

PEARL_NEWS_TOPICS = [
    "climate", "economy_work", "education", "inequality",
    "mental_health", "partnerships", "peace_conflict",
]

# All non-en-US target locales in the system.
TARGET_LOCALES = [
    # CJK (Route 1: Claude meta-prompt → Qwen executor)
    "ja-JP",
    "zh-CN",
    "zh-TW",
    "zh-HK",
    "zh-SG",
    "ko-KR",
    # European + Latin American (Route 2: Claude direct)
    "es-US",
    "es-ES",
    "fr-FR",
    "de-DE",
    "it-IT",
    "hu-HU",
    # Portuguese markets
    "pt-BR",
    "pt-PT",
    # Russian
    "ru-RU",
]

# Locale-specific translation context for the LLM
LOCALE_TRANSLATION_CONTEXT = {
    "ja-JP": {
        "language": "Japanese",
        "register": "丁寧語 (polite register). Contemplative, understated. "
                     "Avoid direct commands — use suggestive, reflective phrasing. "
                     "Reference Japanese cultural concepts where natural (e.g., wa/harmony, mu/emptiness, "
                     "ikigai, mono no aware). The atom should read as if it was originally written "
                     "by a Japanese teacher, not translated from English.",
        "avoid": "Do not use katakana for concepts that have native Japanese equivalents. "
                 "Avoid mental health terminology (精神的健康) — prefer wellbeing (ウェルビーイング), "
                 "nervous system (神経系), or self-care (セルフケア).",
    },
    "zh-CN": {
        "language": "Simplified Chinese (Mainland China)",
        "register": "Warm, accessible standard Mandarin (putonghua). Personal, not broadcast. "
                     "Collective framing — name structural forces, not individual blame. "
                     "Reference Chinese cultural concepts where natural (e.g., he/和/harmony, "
                     "dao/道/way, ren/仁/benevolence). The atom should read as native Chinese writing.",
        "avoid": "Avoid overtly political framing. Do not reference specific government policies "
                 "unless the original atom does. Prefer systemic/structural language.",
    },
    "zh-TW": {
        "language": "Traditional Chinese (Taiwan)",
        "register": "Softer, literary Mandarin. Civic identity framing. "
                     "Reference Taiwanese cultural context where natural — democratic values, "
                     "citizen participation, cultural preservation. "
                     "Use Traditional Chinese characters throughout.",
        "avoid": "Do not use Simplified Chinese characters. "
                 "Avoid PRC-specific terminology or framing.",
    },
    "zh-HK": {
        "language": "Traditional Chinese (Hong Kong)",
        "register": "Warm, colloquial Cantonese-influenced written Chinese. "
                     "Clear, measured, authoritative but accessible. "
                     "Use Traditional Chinese characters.",
        "avoid": "Do not use Simplified Chinese. "
                 "Avoid overly formal written Mandarin register.",
    },
    "zh-SG": {
        "language": "Simplified Chinese (Singapore)",
        "register": "Clean, direct, warm. Singapore Mandarin — bilingual context. "
                     "More concise than Mainland register.",
        "avoid": "Avoid PRC-specific political references.",
    },
    "ko-KR": {
        "language": "Korean",
        "register": "Emotionally present, warm. Use 해요체 (polite informal). "
                     "Reference Korean cultural concepts where natural (e.g., jeong/정, "
                     "nunchi/눈치, han/한). Fast-paced delivery preferred.",
        "avoid": "Avoid overly formal 합니다체 unless the context demands it.",
    },
    "es-US": {
        "language": "Spanish (US Hispanic, Neutral Latin American)",
        "register": "Warm, accessible. Neutral Latin American Spanish — avoid regional slang. "
                     "Reference Latino/a cultural values where natural (familia, comunidad).",
        "avoid": "Avoid vosotros (use ustedes). Avoid Spain-specific vocabulary.",
    },
    "fr-FR": {
        "language": "French (France)",
        "register": "Warm, philosophical framing accepted. Existentialist angle works. "
                     "Strong audiobook market — literary quality matters.",
        "avoid": "Avoid overly casual register.",
    },
    "de-DE": {
        "language": "German (DACH market)",
        "register": "Science-grounded framing. Direct, precise. "
                     "Evidence-based language preferred over spiritual framing.",
        "avoid": "Avoid overtly spiritual language — prefer scientific/psychological framing.",
    },
    "it-IT": {
        "language": "Italian",
        "register": "Warm, relational, expressive. Literary tradition respected. "
                     "Personal, conversational tone that feels like a trusted friend. "
                     "Reference Italian cultural values where natural (famiglia, comunità, bellezza).",
        "avoid": "Avoid overly clinical or corporate phrasing. "
                 "Avoid dialect — use standard Italian (italiano standard).",
    },
    "hu-HU": {
        "language": "Hungarian (Standard Magyar — Budapest norm)",
        "register": "Formal but warm. Hungarian respects directness but values understatement. "
                     "Intellectual framing accepted. "
                     "Hungarian agglutinative grammar — ensure verbs agree correctly with subjects.",
        "avoid": "Do not use regional dialect. Avoid excessive anglicisms. "
                 "Avoid overly casual register (Magyar nem kedveli a túlzott informalitást).",
    },
    "pt-BR": {
        "language": "Brazilian Portuguese",
        "register": "Warm, rhythmic, emotionally present. Open vowels, full syllable pronunciation. "
                     "Você is informal/neutral (equivalent to tu in daily use). "
                     "Inclusive, personal, peer-to-peer mentor tone. "
                     "Reference Brazilian cultural values where natural (comunidade, acolhimento).",
        "avoid": "Do not use European Portuguese phrasing (clitic placement after verbs, "
                 "clipped vowels, vós/vosso forms). "
                 "Avoid excessive anglicisms.",
    },
    "pt-PT": {
        "language": "European Portuguese (Português Europeu)",
        "register": "Measured, precise, slightly more formal than Brazilian Portuguese. "
                     "Clitic pronouns placed after verbs (clítico enclítico). "
                     "Tu is informal; você is formal. "
                     "European literary tradition respected.",
        "avoid": "Do not use Brazilian Portuguese constructions (proclitic pronouns, "
                 "você as informal, open vowel patterns). "
                 "Avoid Brazilianisms — EU Portuguese readers find them jarring.",
    },
    "ru-RU": {
        "language": "Russian",
        "register": "Warm but substantive. Russian self-help readers expect intellectual depth — "
                     "not motivational fluff. "
                     "Collective framing natural; reference shared experience before individual. "
                     "Gentle encouragement without Western-style positivity overload. "
                     "Reference Russian cultural/literary tradition where natural "
                     "(душа/dusha — soul, терпение/terpenie — patience, стойкость/stoikost — resilience).",
        "avoid": "Do not use overly casual or slang register. "
                 "Avoid direct translation of Western therapeutic buzzwords — find Russian equivalents. "
                 "Avoid politically sensitive framing.",
    },
}

ATOMS_PER_TEACHER = 10
MIN_ATOM_WORDS = 40
MAX_ATOM_WORDS = 80


def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_llm_config() -> dict[str, Any]:
    """Load LLM config — try Pearl News config first, then audiobook config."""
    for config_name in ["pearl_news/config/llm_expansion.yaml", "config/audiobook_script/comparator_config.yaml"]:
        path = REPO_ROOT / config_name
        if path.exists():
            cfg = _load_yaml(path)
            if cfg:
                return cfg
    raise RuntimeError("No LLM config found (llm_expansion.yaml or comparator_config.yaml)")


def _call_llm(prompt: str, system_prompt: str, cfg: dict) -> str:
    """Call Qwen — cloud (Dashscope) if DASHSCOPE_API_KEY set, else local LM Studio."""
    from scripts.localization.llm_client import call_llm as _cloud_call
    return _cloud_call(system_prompt, prompt, cfg, role="draft")


# ─── TRANSLATION PROMPT ─────────────────────────────────────────────────────

def _build_translation_prompt(
    teacher_id: str,
    teacher_name: str,
    tradition: str,
    topic: str,
    en_atoms: list[str],
    locale: str,
) -> tuple[str, str]:
    """Build system + user prompts for atom translation."""
    locale_ctx = LOCALE_TRANSLATION_CONTEXT.get(locale, {
        "language": locale,
        "register": "Natural, native-sounding.",
        "avoid": "",
    })

    system_prompt = (
        f"You are a professional translator specializing in spiritual and therapeutic content. "
        f"You translate from English to {locale_ctx['language']}.\n\n"
        f"REGISTER: {locale_ctx['register']}\n\n"
        f"AVOID: {locale_ctx['avoid']}\n\n"
        f"QUALITY REQUIREMENTS:\n"
        f"- Each translated atom must be 40-80 words in the target language\n"
        f"- Preserve the specific teaching meaning — do not generalize\n"
        f"- Preserve tradition-specific terminology (translate or transliterate appropriately)\n"
        f"- The result must read as native {locale_ctx['language']}, NOT as a translation\n"
        f"- Preserve the connectable quality — each atom should still be usable in a news context\n"
        f"- Do NOT add explanatory notes or commentary\n"
    )

    atoms_text = "\n".join(f"  {i+1}. {atom.strip()}" for i, atom in enumerate(en_atoms))

    user_prompt = (
        f"TEACHER: {teacher_name}\n"
        f"TRADITION: {tradition}\n"
        f"TOPIC: {topic}\n"
        f"TARGET LOCALE: {locale}\n\n"
        f"ENGLISH SOURCE ATOMS:\n{atoms_text}\n\n"
        f"Translate each atom to {locale_ctx['language']}. "
        f"Output ONLY the translated atoms as a numbered list (1. ... 2. ... etc.), "
        f"one per line. No preamble, no commentary, no headers.\n"
    )

    return system_prompt, user_prompt


def _parse_translation_response(response: str, expected_count: int) -> list[str]:
    """Parse numbered list of translated atoms from LLM response."""
    lines = response.strip().split("\n")
    atoms: list[str] = []
    current_atom = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check if this starts a new numbered item
        match = re.match(r"^\d+[\.\)]\s*", line)
        if match:
            if current_atom:
                atoms.append(current_atom.strip())
            current_atom = line[match.end():]
        else:
            current_atom += " " + line

    if current_atom:
        atoms.append(current_atom.strip())

    if len(atoms) != expected_count:
        logger.warning(
            "Expected %d atoms, got %d. Response may need manual review.",
            expected_count, len(atoms)
        )

    return atoms


# ─── TRANSLATION ENGINE ─────────────────────────────────────────────────────

def translate_teacher_atoms(
    teacher_id: str,
    teacher_data: dict[str, Any],
    topic: str,
    locale: str,
    cfg: dict,
    dry_run: bool = False,
) -> dict[str, Any] | None:
    """Translate one teacher's atoms for one topic to one locale."""
    teacher_name = teacher_data.get("display_name", teacher_id)
    tradition = teacher_data.get("tradition", "interfaith")
    en_atoms = teacher_data.get("atoms") or []

    if not en_atoms:
        logger.warning("No English atoms for %s/%s — skipping", teacher_id, topic)
        return None

    if dry_run:
        logger.info("[DRY RUN] Would translate %d atoms for %s/%s -> %s",
                     len(en_atoms), teacher_id, topic, locale)
        return {"atoms": [f"[WOULD TRANSLATE: {a[:50]}...]" for a in en_atoms]}

    system_prompt, user_prompt = _build_translation_prompt(
        teacher_id, teacher_name, tradition, topic, en_atoms, locale
    )

    logger.info("Translating %d atoms: %s/%s -> %s", len(en_atoms), teacher_id, topic, locale)
    response = _call_llm(user_prompt, system_prompt, cfg)
    translated = _parse_translation_response(response, len(en_atoms))

    return {
        "display_name": teacher_name,
        "tradition": tradition,
        "attribution": teacher_data.get("attribution", ""),
        "status": "starter",  # Translated atoms start as starter, never auto-approved
        "source_locale": "en-US",
        "translation_method": "qwen_llm",
        "atoms": translated,
    }


def translate_topic(topic: str, locale: str, cfg: dict, dry_run: bool = False) -> dict[str, Any]:
    """Translate all teachers for one topic to one locale."""
    en_data = _load_yaml(
        REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / f"topic_{topic}.yaml"
    )
    en_teachers = en_data.get("teachers") or {}

    translated_teachers: dict[str, Any] = {}
    for teacher_id, teacher_data in en_teachers.items():
        result = translate_teacher_atoms(teacher_id, teacher_data, topic, locale, cfg, dry_run)
        if result:
            translated_teachers[teacher_id] = result

    return {
        "topic_key": topic,
        "locale": locale,
        "source_locale": "en-US",
        "translation_status": "draft" if not dry_run else "stub",
        "description": f"Translated atoms for {locale} — topic: {topic}",
        "teachers": translated_teachers,
    }


def _sanitize_strings(obj: Any) -> Any:
    """Recursively replace non-UTF-8 bytes in strings with U+FFFD, then strip them."""
    if isinstance(obj, str):
        # Roundtrip through bytes to catch any stray non-UTF-8
        clean = obj.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        return clean.replace("\ufffd", "")
    if isinstance(obj, dict):
        return {k: _sanitize_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_strings(v) for v in obj]
    return obj


def write_translated_topic(topic_data: dict, locale: str, topic: str) -> Path:
    """Write translated topic data to the locale atom file."""
    out_dir = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / "locales" / locale
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"topic_{topic}.yaml"

    # Sanitize any non-UTF-8 content from LLM responses before writing
    clean_data = _sanitize_strings(topic_data)

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(clean_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    logger.info("Wrote translated atoms: %s", out_path)
    return out_path


# ─── VALIDATION ──────────────────────────────────────────────────────────────

def validate_translation(topic_data: dict, locale: str) -> list[str]:
    """Basic validation of translated atoms."""
    errors: list[str] = []
    teachers = topic_data.get("teachers") or {}

    for teacher_id, tdata in teachers.items():
        atoms = tdata.get("atoms") or []
        if not atoms:
            errors.append(f"{teacher_id}: no atoms translated")
            continue

        for i, atom in enumerate(atoms):
            atom_str = str(atom).strip()
            if not atom_str:
                errors.append(f"{teacher_id} atom {i+1}: empty")
            elif len(atom_str) < 10:
                errors.append(f"{teacher_id} atom {i+1}: suspiciously short ({len(atom_str)} chars)")

    return errors


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

    ap = argparse.ArgumentParser(description="Translate Pearl News atoms to target locales via Qwen LLM")
    ap.add_argument("--locale", default=None, help="Target locale (e.g., ja-JP)")
    ap.add_argument("--topic", default=None, help="Specific topic to translate")
    ap.add_argument("--teacher", default=None, help="Specific teacher_id to translate (single LLM call)")
    ap.add_argument("--all-locales", action="store_true", help="Translate all target locales")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be translated")
    ap.add_argument("--validate-only", action="store_true", help="Validate existing translations")
    args = ap.parse_args()

    if not args.locale and not args.all_locales and not args.validate_only:
        ap.print_help()
        return 0

    topics = [args.topic] if args.topic else PEARL_NEWS_TOPICS
    locales = TARGET_LOCALES if args.all_locales else ([args.locale] if args.locale else TARGET_LOCALES)

    if args.validate_only:
        all_errors: list[str] = []
        for locale in locales:
            for topic in topics:
                path = (REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices"
                        / "locales" / locale / f"topic_{topic}.yaml")
                if not path.exists():
                    all_errors.append(f"{locale}/{topic}: file missing")
                    continue
                data = _load_yaml(path)
                errors = validate_translation(data, locale)
                all_errors.extend(f"{locale}/{topic}: {e}" for e in errors)

        if all_errors:
            print(f"VALIDATION FAILED — {len(all_errors)} issues:")
            for e in all_errors:
                print(f"  - {e}")
            return 1
        else:
            print("VALIDATION PASSED — all translations look valid")
            return 0

    cfg = _load_llm_config()
    total_translated = 0
    total_failed = 0
    total_pairs = len(locales) * len(topics)
    pair_idx = 0

    for locale in locales:
        for topic in topics:
            pair_idx += 1
            t0 = time.time()
            try:
                # If --teacher specified, only translate that single teacher (1 LLM call)
                if args.teacher:
                    en_data = _load_yaml(
                        REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / f"topic_{topic}.yaml"
                    )
                    en_teachers = en_data.get("teachers") or {}
                    if args.teacher not in en_teachers:
                        logger.info("[%d/%d] %s/%s: teacher %s not in this topic — skip",
                                     pair_idx, total_pairs, locale, topic, args.teacher)
                        continue
                    teacher_data = en_teachers[args.teacher]
                    result = translate_teacher_atoms(
                        args.teacher, teacher_data, topic, locale, cfg, dry_run=args.dry_run
                    )
                    if result and not args.dry_run:
                        # Read existing file, update just this teacher, write back
                        out_dir = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices" / "locales" / locale
                        out_dir.mkdir(parents=True, exist_ok=True)
                        out_path = out_dir / f"topic_{topic}.yaml"
                        existing = _load_yaml(out_path) if out_path.exists() else {
                            "topic_key": topic, "locale": locale, "source_locale": "en-US",
                            "translation_status": "draft",
                            "description": f"Translated atoms for {locale} — topic: {topic}",
                            "teachers": {},
                        }
                        existing.setdefault("teachers", {})[args.teacher] = result
                        existing["translation_status"] = "draft"
                        with open(out_path, "w", encoding="utf-8") as f:
                            yaml.dump(existing, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                        logger.info("Updated teacher %s in %s", args.teacher, out_path)
                    elapsed = time.time() - t0
                    print(f"[{pair_idx}/{total_pairs}] {locale}/{topic}/{args.teacher} "
                          f"{'OK' if result else 'skip'} ({elapsed:.1f}s)")
                    total_translated += 1
                else:
                    topic_data = translate_topic(topic, locale, cfg, dry_run=args.dry_run)
                    if not args.dry_run:
                        write_translated_topic(topic_data, locale, topic)
                        errors = validate_translation(topic_data, locale)
                        if errors:
                            logger.warning("Validation issues for %s/%s: %s", locale, topic, errors)
                    elapsed = time.time() - t0
                    n_teachers = len(topic_data.get("teachers", {}))
                    print(f"[{pair_idx}/{total_pairs}] {locale}/{topic} "
                          f"{n_teachers} teachers ({elapsed:.1f}s)")
                    total_translated += 1
            except Exception as e:
                elapsed = time.time() - t0
                logger.error("[%d/%d] Failed %s/%s after %.1fs: %s",
                             pair_idx, total_pairs, locale, topic, elapsed, e)
                total_failed += 1
                continue

    print(f"\nTranslated {total_translated} pairs, failed {total_failed} "
          f"{'(dry-run)' if args.dry_run else ''}")
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

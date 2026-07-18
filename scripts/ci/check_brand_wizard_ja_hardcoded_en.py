#!/usr/bin/env python3
"""Fail if BrandWizard-ja.jsx contains Latin user-facing strings outside allowed zones."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "brand-wizard-app" / "src" / "BrandWizard-ja.jsx"

ALLOWED_CONST_BLOCKS = (
    "ARCHETYPES",
    "PERSONAS",
    "MOMENTS",
    "VISUAL_STYLES",
    "PROVEN",
    "VOICE_TONE_10",
    "SELECTION_FEEDBACK",
    "TOPIC_CATEGORIES",
    "ANGLE_FEEDBACK",
    "V4_ANGLES",
    "V4_FORMATS_STRUCTURAL",
    "TOPIC_MARKET",
    "ANGLE_MARKET",
    "VISUAL_MARKET",
    "VOICE_AUDIO_SRC",
    "VOICE_SLIDERS",
    "EMOTION_CATEGORIES",
    "TRADITIONS",
)

USER_PROP_RE = re.compile(
    r"\b(eyebrow|title|subtitle|helper|label|desc|placeholder|alt|value|systemEffect|emotionalBenefit|technique|bullet|personas|topics|keywords)\s*=\s*\"([^\"]+)\""
)
JSX_TEXT_RE = re.compile(r">([^<>{}]+)<")
STRING_ASSIGN_RE = re.compile(r"\b(label|desc|value|subtitle|title)\s*:\s*\"([^\"]+)\"")
SENTENCE_LATIN_RE = re.compile(r"[A-Za-z][A-Za-z\s'.,!?;:\-—–/()0-9]{14,}")
CJK_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
TODO_RE = re.compile(r"^TODO_JA:")

SKIP_LINE_HINTS = (
    "className",
    "class=",
    "style=",
    "src=",
    "href=",
    "gradient",
    "border",
    "import ",
    "from ",
    "imagePrompt",
    "emotionPrompt",
    "localStorage",
    "fetch(",
    "console.",
    "cmp_",
    ".mp3",
    ".png",
    ".html",
    "wizard-",
    "api/",
)


def is_user_facing_latin(text: str) -> bool:
    if not text or TODO_RE.match(text.strip()):
        return False
    if CJK_RE.search(text):
        return False
    if not SENTENCE_LATIN_RE.search(text):
        return False
    if text.startswith("/") or text.startswith("http"):
        return False
    if re.fullmatch(r"[\w.-]+", text):
        return False
    return True


def check_ja_wizard_latin() -> int:
    if not TARGET.is_file():
        print(f"ERROR: missing {TARGET}")
        return 1

    lines = TARGET.read_text(encoding="utf-8").splitlines()
    violations: list[str] = []
    active_const: str | None = None
    brace_depth = 0

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if any(h in line for h in SKIP_LINE_HINTS):
            continue
        if stripped.startswith("//"):
            continue

        m_const = re.match(r"const\s+(\w+)\s*=", stripped)
        if m_const and m_const.group(1) in ALLOWED_CONST_BLOCKS:
            active_const = m_const.group(1)
            brace_depth = stripped.count("{") - stripped.count("}")
            continue
        if active_const:
            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth <= 0 and (";" in stripped or stripped == "};"):
                active_const = None
            continue

        for prop, val in USER_PROP_RE.findall(line):
            if is_user_facing_latin(val):
                violations.append(f"{lineno} prop {prop}: {val[:100]}")

        for val in JSX_TEXT_RE.findall(line):
            val = val.strip()
            if is_user_facing_latin(val):
                violations.append(f"{lineno} jsx: {val[:100]}")

        # object literal user fields inside components (scores, cards, etc.)
        if "function " in line or stripped.startswith("const ") or stripped.startswith("return"):
            pass
        for field, val in STRING_ASSIGN_RE.findall(line):
            if is_user_facing_latin(val):
                violations.append(f"{lineno} field {field}: {val[:100]}")

    if violations:
        print("BrandWizard-ja.jsx hardcoded Latin user-facing strings detected:")
        for v in violations[:50]:
            print(f"  - {v}")
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more")
        return 1

    print("OK: BrandWizard-ja.jsx has no disallowed hardcoded Latin UI strings")
    return 0


# ── Routing-continuity guards (all CJK locales) ──────────────────────────────
# A CJK user must never be handed off to an English page mid-journey. These check
# the teacher_showcase surface + the composite-entry routing so a future regression
# (re-pointing a localized wizard at the bare English teacher_showcase, dropping the
# ?lang= override, or a missing/English localized sibling) fails CI.

PUBLIC = ROOT / "brand-wizard-app" / "public"
SRC = ROOT / "brand-wizard-app" / "src"
SHOWCASE_EN = PUBLIC / "teacher_showcase.html"

# locale routing code -> (wizard component, localized showcase sibling, <html lang> BCP-47)
# Routing codes (ja/zh/tw) stay short for _teacherLang() / _wizardFile(); html lang uses
# valid BCP-47 (zh-Hant for Taiwan Traditional Chinese — never bare "tw").
LOCALES = {
    "ja": ("BrandWizard-ja.jsx", "teacher_showcase-ja.html", "ja"),
    "zh": ("BrandWizard-zh.jsx", "teacher_showcase-zh.html", "zh"),
    "tw": ("BrandWizard-tw.jsx", "teacher_showcase-tw.html", "zh-Hant"),
}


def check_localized_teacher_handoff() -> int:
    """Each localized wizard's teacher-book button must route to its locale-carrying
    showcase sibling, not the bare English teacher_showcase.html."""
    rc = 0
    for loc, (wiz, sibling, _lang) in LOCALES.items():
        wf = SRC / wiz
        if not wf.is_file():
            print(f"ERROR: missing {wf}")
            rc = 1
            continue
        text = wf.read_text(encoding="utf-8")
        m = re.search(r"goToTeacherShowcase\s*=\s*\(\)\s*=>\s*\{[^}]*window\.location\.href\s*=\s*\"([^\"]+)\"", text)
        if not m:
            print(f"ERROR: {wiz} goToTeacherShowcase handler not found (routing guard cannot verify)")
            rc = 1
            continue
        target = m.group(1)
        if sibling in target or f"lang={loc}" in target:
            print(f"OK: {wiz} teacher handoff carries locale -> {target}")
        else:
            print(f"{wiz} teacher handoff drops locale: goToTeacherShowcase -> {target}")
            print(f"  Expected {sibling} (or ?lang={loc}). A {loc} user must not land on the English page.")
            rc = 1
    return rc


def check_localized_showcase_pages() -> int:
    """Each localized teacher_showcase sibling must exist, declare its <html lang>,
    and its _teacherLang() must default to its routing locale (never fall through to English)."""
    rc = 0
    for loc, (_wiz, sibling, html_lang) in LOCALES.items():
        f = PUBLIC / sibling
        if not f.is_file():
            print(f"ERROR: missing {f} ({loc} teacher showcase page)")
            rc = 1
            continue
        text = f.read_text(encoding="utf-8")
        problems = []
        if f'<html lang="{html_lang}">' not in text:
            problems.append(f'missing <html lang="{html_lang}">')
        fn = re.search(r"function _teacherLang\(\)\s*\{(.*?)\n\}", text, re.S)
        if not fn:
            problems.append("_teacherLang() not found")
        elif f"return '{loc}';" not in fn.group(1) or "return 'en'" in fn.group(1):
            problems.append(f"_teacherLang() does not default to '{loc}' (English fallback still reachable)")
        if problems:
            print(f"{sibling} is not locale-clean:")
            for p in problems:
                print(f"  - {p}")
            rc = 1
        else:
            print(f"OK: {sibling} declares lang={html_lang} and _teacherLang() defaults to {loc}")
    return rc


def check_en_showcase_honors_lang_param() -> int:
    """The English base teacher_showcase.html must honor a ?lang= override so the
    composite/teacher handoff can be locale-directed instead of guessing from the browser."""
    if not SHOWCASE_EN.is_file():
        print(f"ERROR: missing {SHOWCASE_EN}")
        return 1
    text = SHOWCASE_EN.read_text(encoding="utf-8")
    fn = re.search(r"function _teacherLang\(\)\s*\{(.*?)\n\}", text, re.S)
    if not fn or ".get('lang')" not in fn.group(1):
        print("teacher_showcase.html _teacherLang() does not honor a ?lang= URL override")
        print("  Add a ?lang= branch so the composite/teacher handoff keeps the caller's locale.")
        return 1
    print("OK: teacher_showcase.html _teacherLang() honors ?lang= override")
    return 0


def main() -> int:
    checks = (
        check_ja_wizard_latin,
        check_localized_teacher_handoff,
        check_localized_showcase_pages,
        check_en_showcase_honors_lang_param,
    )
    rc = 0
    for fn in checks:
        rc |= fn()
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())

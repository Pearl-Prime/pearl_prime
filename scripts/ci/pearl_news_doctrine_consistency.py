#!/usr/bin/env python3
"""
pearl_news_doctrine_consistency.py — CI gate validating Pearl News teacher
topic packs against the doctrine SSOT.

Authority chain:
  Pearl_Prime config/teachers/teacher_registry.yaml         (active teacher list)
      ↓
  SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml (SSOT — wins on conflict)
      ↓
  pearl_news/config/teacher_news_roster.yaml                (Pearl_News projection)
      ↓
  pearl_news/teacher_topic_packs/teachers/<id>/*.yaml       (downstream prose)

Checks performed (per teacher in the Pearl News roster):
  1. SSOT presence:  every active roster teacher has a doctrine.yaml.
  2. Prohibited in roster:  no doctrine `prohibited_outcomes` substring
     appears in the roster `tradition` / `tradition_short` fields.
  3. Prohibited in pack tradition:  no doctrine `prohibited_outcomes`
     substring appears in any pack's `identity.tradition` field.
  4. Prohibited in pack prose:  no doctrine `prohibited_outcomes`
     substring appears in any pack's prose fields (teacher_intro,
     teacher_perspective, teacher_witness, etc.).

Modes:
  --report   (default) — exit 0; log violations to stdout.
                          Use this while Phase A/B content rewrites are in
                          flight so the gate doesn't block unrelated PRs.
  --strict             — exit 1 if ANY ERROR-level violation exists.
                          Flip to this once content rewrites complete
                          (Phase E "make required").
  --json               — machine-readable output for downstream tooling.

Usage:
  python3 scripts/ci/pearl_news_doctrine_consistency.py
  python3 scripts/ci/pearl_news_doctrine_consistency.py --strict
  python3 scripts/ci/pearl_news_doctrine_consistency.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("ERROR: pyyaml required (pip install pyyaml)")

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER_PATH = REPO_ROOT / "pearl_news" / "config" / "teacher_news_roster.yaml"
DOCTRINE_DIR = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
PACKS_DIR = REPO_ROOT / "pearl_news" / "teacher_topic_packs" / "teachers"

# Minimum substring length to use from a forbidden phrase. Short matches
# (e.g. "the") would produce false positives.
MIN_SUBSTR_LEN = 6

# Filler / qualifier words that should be skipped when picking the content
# tokens of a forbidden phrase. The actual drift uses different syntax than
# the prohibited_outcomes phrasing (e.g. doctrine says "Theravada Buddhist
# framing" but packs say "Theravada Buddhist teacher" — both share the
# content tokens "Theravada Buddhist").
FILLER_WORDS = frozenset({
    "a", "an", "the", "of", "to", "from", "into", "for", "with", "without",
    "as", "in", "on", "by", "is", "are", "be", "and", "or", "but",
    "framing", "context", "alone", "instead", "only",
    "is", "not", "any", "form",
})


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# Pack subtrees that intentionally MIRROR doctrine prohibitions
# (anti-templates declaring what NOT to do). Scanning them produces
# false positives.
EXCLUDED_FIELDS = frozenset({
    "forbidden_angles",
    "forbidden_claims",
    "tone_boundaries",
    "prohibited_outcomes",
    "prohibited_claims",
    "do_not_say",
    "negative_examples",
})


def extract_prose(node) -> str:
    """Recursively collect all string values from a pack dict, excluding
    anti-template fields (forbidden_*, tone_boundaries, etc.) that intentionally
    mirror doctrine prohibitions."""
    chunks: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if str(k).lower() in EXCLUDED_FIELDS:
                    continue
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
        elif isinstance(o, str):
            chunks.append(o)

    walk(node)
    return "\n".join(chunks)


def forbidden_keys(phrase: str) -> list[str]:
    """Extract one or more candidate substring keys from a prohibited phrase.

    Strategy: take the first 2 *content* tokens (non-filler, non-short),
    plus any single-quoted substring inside the phrase (which often carries
    the literal forbidden phrasing, e.g. "reducing to 'Vedic Hindu' without
    Jagadguru..." → 'Vedic Hindu'). A match on ANY emitted key counts as a
    violation.
    """
    import re

    out: set[str] = set()

    # 1. Single-quoted substrings (literal forbidden phrasings)
    for m in re.finditer(r"['\"]([^'\"]+)['\"]", phrase):
        candidate = m.group(1).lower().strip()
        if len(candidate) >= MIN_SUBSTR_LEN:
            out.add(candidate)

    # 2. First 2 content tokens (skip fillers, drop punctuation)
    # ALWAYS require 2 tokens — single words ("therapist", "Vedic", etc.) are
    # too generic and produce false positives when mentioned in third-party
    # context in prose. Multi-word keys ("Theravada Buddhist", "Vedic Hindu")
    # carry enough specificity to be reliable signals.
    tokens = []
    for raw in phrase.split():
        t = re.sub(r"[^a-z0-9]+", "", raw.lower())
        if not t or t in FILLER_WORDS or len(t) < 3:
            continue
        tokens.append(t)
        if len(tokens) >= 2:
            break
    if len(tokens) == 2:
        key = " ".join(tokens)
        if len(key) >= MIN_SUBSTR_LEN:
            out.add(key)

    return sorted(out)


def check_teacher(teacher_id: str, roster_entry: dict) -> list[dict]:
    """Return list of violations for one teacher."""
    violations: list[dict] = []
    doctrine_path = DOCTRINE_DIR / teacher_id / "doctrine" / "doctrine.yaml"
    doctrine = load_yaml(doctrine_path)

    if not doctrine:
        violations.append({
            "teacher_id": teacher_id,
            "severity": "ERROR",
            "kind": "missing_doctrine",
            "message": f"No doctrine.yaml at {doctrine_path.relative_to(REPO_ROOT)}",
        })
        return violations

    prohibited = doctrine.get("prohibited_outcomes", []) or []
    # Map: original phrase → list of candidate keys
    phrase_keys: list[tuple[str, list[str]]] = [
        (p, forbidden_keys(p)) for p in prohibited
    ]

    # 2. Check roster tradition fields for prohibited substrings
    roster_text = " ".join(
        str(roster_entry.get(f, "")) for f in ("tradition", "tradition_short", "attribution_template")
    ).lower()
    for original, keys in phrase_keys:
        for key in keys:
            if key in roster_text:
                violations.append({
                    "teacher_id": teacher_id,
                    "severity": "WARN",
                    "kind": "roster_prohibited_hit",
                    "message": f"Roster tradition contains prohibited substring '{key}' (from '{original}')",
                })
                break  # one hit per phrase is enough

    # 3 + 4. Check each pack
    pack_dir = PACKS_DIR / teacher_id
    if pack_dir.exists():
        for pack_path in sorted(pack_dir.glob("*.yaml")):
            pack = load_yaml(pack_path)
            identity = pack.get("identity", {}) if isinstance(pack, dict) else {}
            pack_trad = " ".join(
                str(identity.get(f, "")) for f in ("tradition", "tradition_short")
            ).lower()
            prose = extract_prose(pack).lower()
            for original, keys in phrase_keys:
                hit_in_trad = False
                hit_in_prose = False
                for key in keys:
                    if key in pack_trad:
                        hit_in_trad = True
                        matched_key = key
                        break
                    if key in prose:
                        hit_in_prose = True
                        matched_key = key
                if hit_in_trad:
                    violations.append({
                        "teacher_id": teacher_id,
                        "pack": pack_path.name,
                        "severity": "ERROR",
                        "kind": "pack_tradition_prohibited",
                        "message": (
                            f"Pack tradition contains prohibited substring '{matched_key}' "
                            f"(from '{original}')"
                        ),
                    })
                elif hit_in_prose:
                    violations.append({
                        "teacher_id": teacher_id,
                        "pack": pack_path.name,
                        "severity": "WARN",
                        "kind": "pack_prose_prohibited",
                        "message": (
                            f"Pack prose contains prohibited substring '{matched_key}' "
                            f"(from '{original}')"
                        ),
                    })

    return violations


def render_text(violations: list[dict]) -> str:
    error_count = sum(1 for v in violations if v["severity"] == "ERROR")
    warn_count = sum(1 for v in violations if v["severity"] == "WARN")

    lines = []
    lines.append("=" * 64)
    lines.append("PEARL NEWS — Doctrine Consistency Gate")
    lines.append("=" * 64)
    lines.append(f"Errors:    {error_count}")
    lines.append(f"Warnings:  {warn_count}")
    lines.append("")

    if not violations:
        lines.append("✅ All Pearl News teachers align with their doctrine SSOT.")
        return "\n".join(lines)

    # Group by teacher
    by_teacher: dict[str, list[dict]] = {}
    for v in violations:
        by_teacher.setdefault(v["teacher_id"], []).append(v)

    for teacher_id in sorted(by_teacher):
        lines.append(f"--- {teacher_id} ({len(by_teacher[teacher_id])} issue(s)) ---")
        for v in by_teacher[teacher_id]:
            tag = "🚨 ERROR" if v["severity"] == "ERROR" else "⚠️  WARN "
            pack = f"  {v['pack']}" if "pack" in v else ""
            lines.append(f"  {tag}{pack}  [{v['kind']}]")
            lines.append(f"      {v['message']}")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Pearl News doctrine consistency gate")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any ERROR")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    roster = load_yaml(ROSTER_PATH).get("teachers", {})
    if not roster:
        print(f"ERROR: roster not loadable: {ROSTER_PATH}", file=sys.stderr)
        return 2

    all_violations: list[dict] = []
    for teacher_id, entry in roster.items():
        all_violations.extend(check_teacher(teacher_id, entry))

    error_count = sum(1 for v in all_violations if v["severity"] == "ERROR")

    if args.json:
        print(json.dumps({
            "violations": all_violations,
            "summary": {
                "errors": error_count,
                "warnings": sum(1 for v in all_violations if v["severity"] == "WARN"),
                "teachers_checked": len(roster),
            },
        }, indent=2))
    else:
        print(render_text(all_violations))

    if args.strict and error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

# Phase F: cross-system scan paths. Catalog/brand config files contain
# teacher-keyed blocks (e.g. `teacher: ra`, `teacher_id: maat`) whose
# tradition/positioning/prose can violate doctrine prohibited_outcomes
# even when the Pearl News pack layer is clean. The gate walks each YAML
# file, finds teacher-keyed blocks, and scans the block context against
# that teacher's prohibited keys.
CROSS_SYSTEM_DIRS = [
    REPO_ROOT / "config" / "catalog_planning",
    REPO_ROOT / "config" / "brand_management",
]
TEACHER_REGISTRY_PATH = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"

# Field names whose value identifies which teacher a YAML block belongs to.
TEACHER_KEY_FIELDS = frozenset({"teacher", "teacher_id", "author", "kb_id"})

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
            location = ""
            if "pack" in v:
                location = f"  {v['pack']}"
            elif "file" in v:
                location = f"  {v['file']}"
            lines.append(f"  {tag}{location}  [{v['kind']}]")
            lines.append(f"      {v['message']}")
        lines.append("")

    return "\n".join(lines)


def build_doctrine_keys(teacher_ids) -> dict:
    """For each teacher, pre-compute the list of (original_phrase, keys) pairs
    from their doctrine.yaml prohibited_outcomes. Returns dict[teacher_id] →
    list of (phrase, [keys]).

    Filters out keys that ALSO appear in the teacher's own positive doctrine
    (tradition, primary_methods, core_principles, tone_profile, glossary).
    Otherwise the gate flags legitimate uses of doctrine vocabulary as
    violations — e.g. Ra's prohibition "witness practice as detachment from
    life" extracts the 2-word key "witness practice", which also appears in
    Ra's primary_methods as the literal teaching practice. Without this
    filter the gate cannot distinguish "witness practice as a method" from
    "witness practice as detachment."
    """
    out: dict[str, list[tuple[str, list[str]]]] = {}
    for tid in teacher_ids:
        doctrine = load_yaml(DOCTRINE_DIR / tid / "doctrine" / "doctrine.yaml")
        prohibited = doctrine.get("prohibited_outcomes", []) or []
        # Concatenate the teacher's POSITIVE doctrine fields — terms here
        # are legitimate vocabulary and should not trigger as forbidden
        # substrings.
        safe_text_parts = []
        for f in ("tradition", "primary_methods", "core_principles",
                  "tone_profile", "glossary", "display_name"):
            v = doctrine.get(f)
            if isinstance(v, str):
                safe_text_parts.append(v)
            elif isinstance(v, list):
                safe_text_parts.extend(str(x) for x in v)
        safe_text = " ".join(safe_text_parts).lower()

        pairs = []
        for phrase in prohibited:
            keys = forbidden_keys(phrase)
            # Drop keys whose entire content appears in positive doctrine
            filtered = [k for k in keys if k not in safe_text]
            if filtered:
                pairs.append((phrase, filtered))
        if pairs:
            out[tid] = pairs
    return out


def check_cross_system_file(path: Path, doctrine_keys: dict) -> list[dict]:
    """Walk a YAML file looking for teacher-keyed blocks. For each block,
    scan its content against that teacher's doctrine prohibited substrings."""
    violations: list[dict] = []
    data = load_yaml(path)
    if not data:
        return violations
    rel_path = path.relative_to(REPO_ROOT)

    def walk(node):
        if isinstance(node, dict):
            tid = None
            for field in TEACHER_KEY_FIELDS:
                if field in node and isinstance(node[field], str):
                    candidate = node[field].strip().lower()
                    if candidate in doctrine_keys:
                        tid = candidate
                        break
            if tid:
                block_text = extract_prose(node).lower()
                for original, keys in doctrine_keys[tid]:
                    for key in keys:
                        if key in block_text:
                            violations.append({
                                "teacher_id": tid,
                                "file": str(rel_path),
                                "severity": "ERROR",
                                "kind": "cross_system_prohibited",
                                "message": (
                                    f"{rel_path} block (teacher={tid}) contains prohibited "
                                    f"substring '{key}' (from '{original}')"
                                ),
                            })
                            break  # one hit per phrase is enough
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(data)
    return violations


def check_cross_system_paths(doctrine_keys: dict) -> list[dict]:
    """Iterate CROSS_SYSTEM_DIRS and run check_cross_system_file on each .yaml."""
    violations: list[dict] = []
    for d in CROSS_SYSTEM_DIRS:
        if not d.exists():
            continue
        for path in sorted(d.glob("*.yaml")):
            violations.extend(check_cross_system_file(path, doctrine_keys))
    return violations


def main():
    ap = argparse.ArgumentParser(description="Pearl News doctrine consistency gate")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any ERROR")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--no-cross-system",
        action="store_true",
        help="skip catalog_planning/brand_management cross-system scan (Phase F)",
    )
    args = ap.parse_args()

    roster = load_yaml(ROSTER_PATH).get("teachers", {})
    if not roster:
        print(f"ERROR: roster not loadable: {ROSTER_PATH}", file=sys.stderr)
        return 2

    all_violations: list[dict] = []
    for teacher_id, entry in roster.items():
        all_violations.extend(check_teacher(teacher_id, entry))

    # Phase F: cross-system scan across all Pearl_Prime registry teachers.
    # The catalog/brand layer references all 13 teachers (incl. adi_da,
    # pamela_fellows, ra), so we walk the full registry, not just the
    # Pearl News roster.
    if not args.no_cross_system:
        registry = load_yaml(TEACHER_REGISTRY_PATH).get("teachers", {})
        all_teacher_ids = set(registry.keys()) | set(roster.keys())
        doctrine_keys = build_doctrine_keys(all_teacher_ids)
        all_violations.extend(check_cross_system_paths(doctrine_keys))

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

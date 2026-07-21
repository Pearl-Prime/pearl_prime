#!/usr/bin/env python3
"""
phoenix_v4/quality/story_atom_lint.py

Deterministic story-atom linting:
- checks specificity, conflict, cost, insight pivot
- scores PASS/WARN/FAIL per atom
- CANONICAL.txt: parses ## ROLE vNN --- metadata --- prose blocks and lints each atom separately (no whole-file masking).
- Other .txt/.md: linted as single blob (one result per file).

Exit codes (see phoenix_v4/quality/base.py): 0 PASS, 1 FAIL, 2 WARN.

Usage:
  PYTHONPATH=. python3 phoenix_v4/quality/story_atom_lint.py --path atoms/.../CANONICAL.txt --json-out artifacts/ops/story_lint.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from phoenix_v4.quality.base import (
    EXIT_FAIL,
    EXIT_PASS,
    EXIT_WARN,
    parse_canonical_blocks_from_path,
    status_to_exit_code,
)

# -----------------------------
# Patterns (tweakable)
# -----------------------------

ACTION_VERBS = [
    r"\b(sat|stood|walked|drove|ran|stared|grabbed|held|shook|typed|called|texted|opened|closed|slammed)\b",
]
SENSORY_WORDS = [
    r"\b(cold|warm|loud|silent|tight|heavy|burning|buzzing|aching|sweaty|shaky)\b",
]
CONFLICT_MARKERS = [
    r"\b(but|however|although|yet)\b",
    r"\b(couldn['']t|cannot|can't)\b",
    r"\b(wanted to|should)\b",
]
COST_MARKERS = [
    r"\b(lost|exhausted|ashamed|avoided|broke|collapsed|quit)\b",
    r"\b(couldn['']t sleep|stopped eating|panic|crying)\b",
]
PIVOT_MARKERS = [
    r"\b(I|she|he|they)\s+(realized|noticed|understood|saw|recognized)\b",
    r"\b(the truth was|that's when|thats when|it hit (me|her|him)|what (I|she|he) didn['']t know)\b",
]

PROPER_NOUN_RE = re.compile(r"\b(?!I\b)[A-Z][a-z]{2,}\b")
WORD_RE = re.compile(r"\b[\w'']+\b")

# -----------------------------
# Story-type / origin conformance (docs/STORY_TYPES_AND_STRUCTURES.md §7)
# Deterministic metadata rules. Only fire when story_type is PRESENT — untagged
# atoms (e.g. the persona STORY pools until they are tagged) are never flagged
# by these, so this is additive and does not red-wall the untagged catalog.
# -----------------------------

VALID_STORY_TYPES = frozenset(
    {"parable", "direct_teaching", "character_study", "atmospheric", "recognition_exchange"}
)
# §1.5: composite origin may not put the teacher in-scene → recognition_exchange forbidden.
_COMPOSITE_FORBIDDEN_TYPES = frozenset({"recognition_exchange"})
# §2.2: principle teachers may only use these types.
_PRINCIPLE_ALLOWED_TYPES = frozenset({"parable", "atmospheric", "direct_teaching"})


def check_story_type_conformance(
    story_type: "str | None",
    story_origin: "str | None",
    teacher_is_principle: bool = False,
) -> List[str]:
    """§7 conformance flags for a STORY atom's metadata. Empty list = conformant.

    Only evaluates when ``story_type`` is present; an untagged atom returns [].
    Returned codes are FAIL-severity (schema violations), keyed to the authority.
    """
    st = (story_type or "").strip().lower()
    so = (story_origin or "").strip().lower()
    if not st:
        return []  # untagged: conformance is vacuous until Phase-3 tagging
    flags: List[str] = []
    if st not in VALID_STORY_TYPES:
        flags.append("UNKNOWN_STORY_TYPE")
        return flags  # can't evaluate the rest against an unknown type
    if so == "composite" and st in _COMPOSITE_FORBIDDEN_TYPES:
        flags.append("COMPOSITE_FORBIDS_RECOGNITION_EXCHANGE")
    if st == "recognition_exchange" and so and so != "true_story":
        flags.append("RECOGNITION_EXCHANGE_REQUIRES_TRUE_STORY")
    if teacher_is_principle and st not in _PRINCIPLE_ALLOWED_TYPES:
        flags.append("PRINCIPLE_TEACHER_TYPE_FORBIDDEN")
    return flags


# A named protagonist in this corpus is a capitalized token used as an actor
# (Name + verb-ish token): "Priya submits", "Naomi sat", "Sam reads". Bare
# count_proper_nouns is too crude — it counts sentence-initial "She"/"The" and
# brand/place capitals (LinkedIn, Slack, Tuesday). This targets a *person* name.
_NON_NAME_CAPS = frozenset(
    {
        "She", "He", "They", "We", "You", "It", "The", "But", "And", "When", "That",
        "This", "Then", "There", "Her", "His", "Their", "Not", "Now", "One", "Nobody",
        "Everybody", "Someone", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    }
)
# Function words that follow a capital but are not actor-verbs ("In the", "On Monday").
_NON_ACTOR_FOLLOWERS = frozenset(
    {
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "but",
        "with", "from", "by", "as", "into", "about", "between", "through", "during",
        "before", "after", "above", "below", "over", "under", "again", "further",
        "then", "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "also", "now", "still",
        "who", "whom", "whose", "which", "what", "that", "this", "these", "those",
    }
)
# Letters incl. common Latin diacritics (Zoë, José, Søren).
_NAME_TOKEN = r"[A-Z][A-Za-z\u00C0-\u024F]{1,}"
_NAME_POSSESSIVE_RE = re.compile(rf"\b({_NAME_TOKEN})['\u2019]s\b")
_NAME_BE_RE = re.compile(
    rf"\b({_NAME_TOKEN})\s+(?:is|was|were|has|had|have|does|did|can|could|will|would)\b"
)
_NAME_ACTOR_RE = re.compile(
    rf"\b({_NAME_TOKEN})\s+(?:had\s+|has\s+|just\s+)?"
    rf"([a-z]+(?:'t)?)\b"
)


def _has_named_person(text: str) -> bool:
    for m in _NAME_POSSESSIVE_RE.finditer(text):
        if m.group(1) not in _NON_NAME_CAPS:
            return True
    for m in _NAME_BE_RE.finditer(text):
        if m.group(1) not in _NON_NAME_CAPS:
            return True
    for m in _NAME_ACTOR_RE.finditer(text):
        name, follower = m.group(1), m.group(2)
        if name not in _NON_NAME_CAPS and follower not in _NON_ACTOR_FOLLOWERS:
            return True
    return False


def check_character_study_naming(story_type: "str | None", prose: str) -> "str | None":
    """§3 rule #1: a character_study needs a NAMED protagonist. FAIL under hard-gate.

    Fires for character_study atoms whose protagonist is only a pronoun (no
    Name-as-actor). Returns a flag code or None.
    """
    if (story_type or "").strip().lower() != "character_study":
        return None
    if not _has_named_person(normalize_text(prose)):
        return "CHARACTER_STUDY_UNNAMED"
    return None


def check_anchored_story_naming(prose: str, path: "Path | None" = None) -> "str | None":
    """Anchored story_atoms are character-arc prose — always require a NAMED protagonist."""
    text = normalize_text(prose)
    if _has_named_person(text):
        return None
    if path is not None:
        source_path = source_story_atom_path_for_localized(path)
        if source_path and source_path.exists():
            try:
                source_text = source_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                source_text = ""
            if source_text and _has_named_person(normalize_text(source_text)):
                return None
    return "CHARACTER_STUDY_UNNAMED"


def story_type_variety_flag(story_types: List[str]) -> "str | None":
    """§9: a compiled book should carry ≥2 distinct story_types. FAIL under hard-gate.

    Ignores blank/untagged entries; returns a flag only when ≥1 type is present
    but fewer than 2 distinct tagged types appear.
    """
    distinct = {t.strip().lower() for t in story_types if t and t.strip()}
    if distinct and len(distinct) < 2:
        return "LOW_STORY_TYPE_VARIETY"
    return None


def is_anchored_story_atom_path(path: Path) -> bool:
    """True for story_atoms/<persona>/anchored/... prose files."""
    parts = path.parts
    try:
        i = parts.index("story_atoms")
    except ValueError:
        return False
    return len(parts) > i + 2 and parts[i + 2] == "anchored"


def source_story_atom_path_for_localized(path: Path) -> "Path | None":
    """Map a localized anchored story path back to its source sibling."""
    parts = list(path.parts)
    try:
        i = parts.index("locales")
    except ValueError:
        return None
    if i + 2 >= len(parts):
        return None
    return Path(*parts[:i], *parts[i + 2 :])


def load_principle_teachers(registry_path: "Path | None" = None) -> "set[str]":
    """Return the set of teacher_ids with teacher_as_principle: true (§2.2)."""
    path = registry_path or (REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml")
    try:
        import yaml  # local import: keep module import-light
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return set()
    teachers = data.get("teachers", data) if isinstance(data, dict) else {}
    out: "set[str]" = set()
    if isinstance(teachers, dict):
        for tid, cfg in teachers.items():
            if isinstance(cfg, dict) and cfg.get("teacher_as_principle") is True:
                out.add(str(tid))
    return out


# -----------------------------
# Data
# -----------------------------


@dataclass(frozen=True)
class StoryLintResult:
    path: str
    story_id: str
    word_count: int
    flags: List[str]
    missing_signals: int
    status: str  # PASS/WARN/FAIL
    notes: List[str]
    band: str = ""


# -----------------------------
# Helpers
# -----------------------------


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_hits(text: str, patterns: List[str]) -> int:
    flags = re.IGNORECASE | re.MULTILINE
    return sum(len(re.findall(p, text, flags)) for p in patterns)


def has_any(text: str, patterns: List[str]) -> bool:
    return count_hits(text, patterns) > 0


def count_proper_nouns(text: str) -> int:
    tokens = PROPER_NOUN_RE.findall(text)
    return len(tokens)


def derive_story_id(path: Path) -> str:
    return path.stem


def lint_one_prose(prose: str, story_id: str, path: str, band: str = "") -> StoryLintResult:
    """Lint a single story prose block. Used for per-atom and single-blob modes."""
    text = normalize_text(prose)
    wc = word_count(text)

    flags: List[str] = []
    notes: List[str] = []

    if wc < 120:
        flags.append("TOO_SHORT_LT_120")

    proper_n = count_proper_nouns(text)
    has_action = has_any(text, ACTION_VERBS)
    has_sensory = has_any(text, SENSORY_WORDS)
    if (proper_n == 0) and (not has_action) and (not has_sensory):
        flags.append("NO_SPECIFIC_DETAIL")

    if not has_any(text, CONFLICT_MARKERS):
        flags.append("NO_INTERNAL_CONFLICT")

    if not has_any(text, COST_MARKERS):
        flags.append("NO_COST_SIGNAL")

    pivot = has_any(text, PIVOT_MARKERS)
    if not pivot:
        flags.append("NO_INSIGHT_PIVOT")
        if wc < 180:
            notes.append("Short story with no pivot tends to read generic.")

    signal_flags = {"NO_SPECIFIC_DETAIL", "NO_INTERNAL_CONFLICT", "NO_COST_SIGNAL", "NO_INSIGHT_PIVOT"}
    missing = sum(1 for f in flags if f in signal_flags)

    status = "PASS"
    if "TOO_SHORT_LT_120" in flags or missing >= 3:
        status = "FAIL"
    elif missing == 2:
        status = "WARN"

    return StoryLintResult(
        path=path,
        story_id=story_id,
        word_count=wc,
        flags=flags,
        missing_signals=missing,
        status=status,
        notes=notes,
        band=band,
    )


def lint_story(text: str, path: Path) -> StoryLintResult:
    """Lint whole text as one story (legacy single-blob)."""
    return lint_one_prose(text, derive_story_id(path), str(path), band="")


def iter_text_files(root: Path) -> List[Path]:
    if root.is_file():
        return [root]
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".txt", ".md"):
            files.append(p)
    return sorted(files)


# Extract the STORY_TYPE meta value per block, in document order, from a raw
# CANONICAL.txt (persona pools tagged by scripts/atom_writing/classify_story_types.py).
_CANON_META_RE = re.compile(
    r"##\s*[^\n]+\n---\s*\n(?P<meta>.*?)\n---\s*\n", re.DOTALL
)
_STORY_TYPE_LINE_RE = re.compile(r"^\s*STORY_TYPE\s*:\s*(\S+)", re.MULTILINE)


def _canonical_story_types(path: Path) -> List["str | None"]:
    text = path.read_text(encoding="utf-8", errors="replace")
    types: List["str | None"] = []
    for m in _CANON_META_RE.finditer(text):
        mt = _STORY_TYPE_LINE_RE.search(m.group("meta"))
        types.append(mt.group(1) if mt else None)
    return types


def lint_canonical_file(path: Path) -> List[StoryLintResult]:
    """Parse CANONICAL.txt into blocks and lint each atom. Raises ValueError if malformed.

    When a block carries a STORY_TYPE meta tag (persona pools, Phase-3), the §7
    conformance + §3 naming checks are applied too. Untagged blocks get only the
    5-element prose lint (unchanged behavior).
    """
    blocks = parse_canonical_blocks_from_path(path)
    path_str = str(path)
    story_types = _canonical_story_types(path)
    aligned = len(story_types) == len(blocks)
    results: List[StoryLintResult] = []
    for i, block in enumerate(blocks):
        base = lint_one_prose(block.body, block.atom_id, path_str, band=block.band)
        st = story_types[i] if aligned else None
        if st:
            # persona pools carry no story_origin / teacher → origin=None, principle=False
            extra = check_story_type_conformance(st, None, teacher_is_principle=False)
            naming = check_character_study_naming(st, block.body)
            if naming:
                extra = extra + [naming]
            base = _escalate(base, extra, _HARD_GATE_FAIL_CODES)
        results.append(base)
    return results


def _escalate(base: StoryLintResult, extra_flags: List[str], fail_codes: frozenset) -> StoryLintResult:
    """Merge extra flags into a StoryLintResult and re-derive status.

    A flag in ``fail_codes`` forces FAIL; any other extra flag lifts PASS→WARN.
    """
    if not extra_flags:
        return base
    flags = list(base.flags) + [f for f in extra_flags if f not in base.flags]
    status = base.status
    if any(f in fail_codes for f in extra_flags):
        status = "FAIL"
    elif status == "PASS":
        status = "WARN"
    return StoryLintResult(
        path=base.path,
        story_id=base.story_id,
        word_count=base.word_count,
        flags=flags,
        missing_signals=base.missing_signals,
        status=status,
        notes=base.notes,
        band=base.band,
    )


# Only genuine §7 CONTRADICTIONS block the gate. UNKNOWN_STORY_TYPE is a WARN,
# not a FAIL: teacher banks legitimately carry esoteric extension types
# (receiver_witness, soul_remembrance, conduit_session) that the 5-type authority
# doesn't enumerate — surface them for review, don't red-wall CI. Whether to
# canonicalize or extend the enum is an authority decision, not a merge blocker.
_CONFORMANCE_FAIL_CODES = frozenset(
    {
        "COMPOSITE_FORBIDS_RECOGNITION_EXCHANGE",
        "RECOGNITION_EXCHANGE_REQUIRES_TRUE_STORY",
        "PRINCIPLE_TEACHER_TYPE_FORBIDDEN",
    }
)

# Hard gate (restore workstream #3): naming + variety + §7 conformance are FAIL.
# Persona catalog atoms/ stay on --conformance-only until Claude finishes authoring;
# story_atoms/anchored and tagged character_study atoms use --hard-gate.
_HARD_GATE_FAIL_CODES = _CONFORMANCE_FAIL_CODES | frozenset(
    {
        "CHARACTER_STUDY_UNNAMED",
        "LOW_STORY_TYPE_VARIETY",
    }
)


def lint_story_atom_yaml(path: Path, principle_teachers: "set[str] | None" = None) -> StoryLintResult:
    """Lint a teacher-mode STORY atom YAML: 5-element prose lint + §7 conformance + §3 naming.

    Enforces the story_type/origin rules NOW on tagged atoms. An atom with no
    story_type gets only the base prose lint (conformance/naming no-op).
    """
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("story atom yaml is not a mapping")
    atom_id = str(data.get("atom_id") or derive_story_id(path))
    body = str(data.get("body") or "")
    band = str(data.get("band") or "")
    story_type = data.get("story_type")
    story_origin = data.get("story_origin")
    teacher_id = ""
    tmeta = data.get("teacher")
    if isinstance(tmeta, dict):
        teacher_id = str(tmeta.get("teacher_id") or "")
    principle = bool(principle_teachers and teacher_id in principle_teachers)

    base = lint_one_prose(body, atom_id, str(path), band=band)
    extra = check_story_type_conformance(story_type, story_origin, teacher_is_principle=principle)
    naming = check_character_study_naming(story_type, body)
    if naming:
        extra = extra + [naming]
    return _escalate(base, extra, _HARD_GATE_FAIL_CODES)


# The story_type authority (docs/STORY_TYPES_AND_STRUCTURES.md) governs the
# APPROVED ENGLISH STORY atoms. Localized banks carry a separate translated
# vocabulary (e.g. story_type: dialogue_exchange) and candidate banks are pre-
# approval WIP — both are out of scope for §7 conformance.
_YAML_ATOM_EXCLUDE_PARTS = frozenset({"approved_atoms_localized", "candidate_atoms"})


def _is_in_scope_story_yaml(p: Path) -> bool:
    parts = set(p.parts)
    return "STORY" in parts and not (_YAML_ATOM_EXCLUDE_PARTS & parts)


def iter_story_atom_yaml(root: Path) -> List[Path]:
    """Find in-scope (approved-English) STORY-atom YAML files for conformance linting."""
    if root.is_file():
        return [root] if (root.suffix.lower() in (".yaml", ".yml") and _is_in_scope_story_yaml(root)) else []
    out: List[Path] = []
    for p in root.rglob("*.y*ml"):
        if p.is_file() and _is_in_scope_story_yaml(p):
            out.append(p)
    return sorted(out)


# -----------------------------
# CLI
# -----------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="File or directory of story atoms")
    ap.add_argument("--json-out", default=None, help="Write JSON report to this path")
    ap.add_argument(
        "--fail-on",
        choices=["PASS", "WARN", "FAIL"],
        default="FAIL",
        help="Exit nonzero if any result is at/above this severity",
    )
    ap.add_argument(
        "--conformance-only",
        action="store_true",
        help=(
            "CI-gate mode: exit nonzero ONLY on §7 story_type conformance FAILs "
            "(schema violations on TAGGED atoms). Ignores the pre-existing "
            "5-element FAILs so legacy/untagged content never red-walls the gate."
        ),
    )
    ap.add_argument(
        "--hard-gate",
        action="store_true",
        help=(
            "CI hard gate: exit nonzero on CHARACTER_STUDY_UNNAMED, "
            "LOW_STORY_TYPE_VARIETY, and §7 conformance FAILs. Use on "
            "story_atoms/anchored and tagged teacher STORY atoms."
        ),
    )
    ap.add_argument(
        "--story-only",
        action="store_true",
        help="In directory mode, lint only files under a STORY/ path (skip HOOK/SCENE/EXERCISE).",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path)

    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        return 1

    text_files = iter_text_files(root)
    if args.story_only:
        text_files = [f for f in text_files if "STORY" in f.parts]

    results: List[StoryLintResult] = []
    for f in text_files:
        try:
            if f.name == "CANONICAL.txt":
                try:
                    results.extend(lint_canonical_file(f))
                except ValueError as ve:
                    results.append(
                        StoryLintResult(
                            path=str(f),
                            story_id=derive_story_id(f),
                            word_count=0,
                            flags=["MALFORMED_CANONICAL"],
                            missing_signals=4,
                            status="FAIL",
                            notes=[str(ve)],
                            band="",
                        )
                    )
            else:
                text = f.read_text(encoding="utf-8", errors="replace")
                base = lint_story(text, f)
                if is_anchored_story_atom_path(f):
                    naming = check_anchored_story_naming(text, f)
                    if naming:
                        base = _escalate(base, [naming], _HARD_GATE_FAIL_CODES)
                results.append(base)
        except Exception as e:
            results.append(
                StoryLintResult(
                    path=str(f),
                    story_id=derive_story_id(f),
                    word_count=0,
                    flags=["READ_ERROR"],
                    missing_signals=4,
                    status="FAIL",
                    notes=[str(e)],
                    band="",
                )
            )
            continue

    # Teacher-mode STORY atom YAMLs: 5-element lint + §7 story_type conformance.
    yaml_atoms = iter_story_atom_yaml(root)
    if yaml_atoms:
        principle_teachers = load_principle_teachers()
        for yf in yaml_atoms:
            try:
                results.append(lint_story_atom_yaml(yf, principle_teachers=principle_teachers))
            except Exception as e:
                results.append(
                    StoryLintResult(
                        path=str(yf),
                        story_id=derive_story_id(yf),
                        word_count=0,
                        flags=["READ_ERROR"],
                        missing_signals=4,
                        status="FAIL",
                        notes=[str(e)],
                        band="",
                    )
                )

    if not results:
        print("No story files found.", file=sys.stderr)
        return 1

    fail_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARN")
    pass_count = sum(1 for r in results if r.status == "PASS")
    overall = "fail" if fail_count else ("warn" if warn_count else "pass")

    # Ops artifact (schema story_atom_lint_v1)
    entity_id = str(root.resolve())
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    ops_payload = {
        "schema_version": "1.0",
        "tool": "story_atom_lint",
        "entity_type": "atom_file",
        "entity_id": entity_id,
        "generated_at": generated_at,
        "status": overall,
        "summary": {
            "total_atoms": len(results),
            "fail_count": fail_count,
            "warn_count": warn_count,
            "pass_count": pass_count,
        },
        "details": [
            {
                "atom_id": r.story_id,
                "band": r.band,
                "status": r.status.lower(),
                "issues": list(r.flags),
            }
            for r in results
        ],
    }

    outp = Path(args.json_out) if args.json_out else None
    if not outp:
        outp = REPO_ROOT / "artifacts" / "ops" / f"story_atom_lint_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(ops_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    top = [r for r in results if r.status != "PASS"][:20]
    if top:
        print("\nTop issues:")
        for r in top:
            print(f"- {r.status} {r.story_id} ({r.word_count}w) {Path(r.path).name} :: {', '.join(r.flags)}")

    if args.hard_gate:
        # Book-level variety: when ≥1 tagged story_type is present across the
        # lint set, require ≥2 distinct types (per-book floor).
        tagged_types: List[str] = []
        for f in text_files:
            if f.name == "CANONICAL.txt":
                tagged_types.extend(t for t in _canonical_story_types(f) if t)
        for yf in yaml_atoms:
            try:
                import yaml as _yaml
                data = _yaml.safe_load(yf.read_text(encoding="utf-8")) or {}
                st = data.get("story_type") if isinstance(data, dict) else None
                if st:
                    tagged_types.append(str(st))
            except Exception:
                pass
        variety = story_type_variety_flag(tagged_types)
        if variety:
            results.append(
                StoryLintResult(
                    path=str(root),
                    story_id="__book_variety__",
                    word_count=0,
                    flags=[variety],
                    missing_signals=0,
                    status="FAIL",
                    notes=["per-book story_type variety floor (≥2 distinct tagged types)"],
                    band="",
                )
            )

        hard_fails = [
            r for r in results if any(f in _HARD_GATE_FAIL_CODES for f in r.flags)
        ]
        if hard_fails:
            print("\nStory-atom hard-gate violations (BLOCKING):")
            for r in hard_fails:
                bad = [f for f in r.flags if f in _HARD_GATE_FAIL_CODES]
                print(f"- {r.story_id} {Path(r.path).name} :: {', '.join(bad)}")
            return EXIT_FAIL
        print(
            "\nStory-atom hard-gate: PASS "
            "(no CHARACTER_STUDY_UNNAMED / LOW_STORY_TYPE_VARIETY / §7 violations)."
        )
        return EXIT_PASS

    if args.conformance_only:
        # CI-gate mode: block ONLY on §7 schema violations (tagged atoms).
        # Legacy 5-element FAILs and naming/variety WARNs never fail the gate.
        conformance_fails = [
            r for r in results if any(f in _CONFORMANCE_FAIL_CODES for f in r.flags)
        ]
        if conformance_fails:
            print("\nStory-type conformance violations (BLOCKING):")
            for r in conformance_fails:
                bad = [f for f in r.flags if f in _CONFORMANCE_FAIL_CODES]
                print(f"- {r.story_id} {Path(r.path).name} :: {', '.join(bad)}")
            return EXIT_FAIL
        print("\nStory-type conformance: PASS (no §7 schema violations on tagged atoms).")
        return EXIT_PASS

    return status_to_exit_code(overall)


if __name__ == "__main__":
    raise SystemExit(main())

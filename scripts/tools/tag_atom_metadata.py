#!/usr/bin/env python3
"""
Suggest bestseller metadata tags for un-tagged atoms in a registry YAML.

Usage:
  python3 scripts/tools/tag_atom_metadata.py --registry registry/burnout.yaml --dry-run
  python3 scripts/tools/tag_atom_metadata.py --registry registry/burnout.yaml --write

Reads each atom section. If metadata fields are absent, suggests values based on
content keywords in the section's variant body text. --dry-run prints suggestions.
--write patches them in-place.

Fields tagged:
  reader_objection  — what reader resistance this atom addresses
  proof_mode        — how the atom proves its point
  tension_type      — what emotional tension it creates
  propulsion_type   — what makes the reader keep reading
  shareability      — how likely someone shares this (1-5 int)
  collision_family  — semantic group for dedup
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

METADATA_FIELDS = [
    "reader_objection",
    "proof_mode",
    "tension_type",
    "propulsion_type",
    "shareability",
    "collision_family",
]

# Keyword -> field value mappings for heuristic suggestion
_PROOF_MODE_KEYWORDS: List[tuple[tuple[str, ...], str]] = [
    (("amygdala", "cortisol", "nervous system", "neuroscience", "prefrontal", "hippocampus", "dopamine", "serotonin"), "neuroscience"),
    (("research", "study", "scientists", "findings", "evidence", "clinical", "meta-analysis"), "research"),
    (("she felt", "he felt", "she realized", "he realized", "she said", "he said", "story", "once there was", "years ago"), "story"),
    (("breath", "inhale", "exhale", "breathe", "breathing"), "lived_experience"),
    (("framework", "model", "system", "method", "approach", "steps", "technique"), "framework"),
]

_COLLISION_FAMILY_KEYWORDS: List[tuple[tuple[str, ...], str]] = [
    (("breath", "inhale", "exhale", "breathe", "breathing", "4-7-8", "box breath", "diaphragm"), "breathing_exercise"),
    (("body scan", "scan your body", "body sensation", "physical sensation", "notice in your body"), "body_scan"),
    (("nervous system", "fight or flight", "freeze", "amygdala", "cortisol", "regulate", "window of tolerance"), "nervous_system_reset"),
    (("shame", "worthless", "broken", "flaw", "defective", "embarrass", "humiliat"), "shame_recognition"),
    (("thought", "label", "notice the thought", "name the thought", "thought pattern", "cognitive", "ruminate", "worry spiral"), "thought_labeling"),
    (("boundary", "limit", "say no", "push back", "people pleasing", "overextend"), "boundary_narrative"),
    (("hypervigilance", "scanning", "threat", "alarm", "alert", "danger signal", "false alarm"), "hypervigilance_pattern"),
)

_TENSION_TYPE_KEYWORDS: List[tuple[tuple[str, ...], str]] = [
    (("what if", "why does", "how does", "what is", "did you know"), "curiosity_gap"),
    (("you are not who", "identity", "who you are", "who you think", "the person you"), "identity_threat"),
    (("relief", "finally", "lighter", "ease", "calm", "peace"), "relief_anticipation"),
    (("but", "however", "yet", "despite", "paradox", "contradiction"), "contradiction"),
    (("mystery", "secret", "hidden", "beneath the surface", "nobody talks about"), "mystery"),
    (("cost", "risk", "loss", "price", "stakes", "consequence"), "stakes"),
]

_PROPULSION_KEYWORDS: List[tuple[tuple[str, ...], str]] = [
    (("?", "what happens", "what if you"), "question"),
    (("you will", "by the end", "promise", "here is what", "you are about to"), "promise"),
    (("turns out", "the truth is", "what actually", "here is the thing"), "revelation"),
    (("to be continued", "next chapter", "coming up", "what happens next"), "cliffhanger"),
    (("remember", "recall", "back to", "earlier we saw", "that image"), "image_return"),
]


def _get_body_text(section_data: Dict[str, Any]) -> str:
    """Collect all variant body text from a section."""
    parts: List[str] = []
    for v in section_data.get("variants") or []:
        if isinstance(v, dict):
            txt = str(v.get("content") or "").strip()
            if txt:
                parts.append(txt)
    return " ".join(parts).lower()


def _suggest_proof_mode(body: str) -> str:
    for keywords, value in _PROOF_MODE_KEYWORDS:
        if any(kw in body for kw in keywords):
            return value
    return "lived_experience"


def _suggest_collision_family(body: str, section_type: str) -> str:
    for keywords, value in _COLLISION_FAMILY_KEYWORDS:
        if any(kw in body for kw in keywords):
            return value
    st = (section_type or "").upper()
    if st == "EXERCISE":
        return "breathing_exercise"
    if st == "REFLECTION":
        return "thought_labeling"
    if st in ("HOOK", "SCENE"):
        return "hypervigilance_pattern"
    return "nervous_system_reset"


def _suggest_tension_type(body: str) -> str:
    for keywords, value in _TENSION_TYPE_KEYWORDS:
        if any(kw in body for kw in keywords):
            return value
    return "curiosity_gap"


def _suggest_propulsion(body: str) -> str:
    for keywords, value in _PROPULSION_KEYWORDS:
        if any(kw in body for kw in keywords):
            return value
    return "question"


def _suggest_shareability(body: str, section_type: str) -> int:
    st = (section_type or "").upper()
    # Identity-insight atoms = 4-5
    if any(kw in body for kw in ("identity", "who you are", "who you think", "you are not", "who i am")):
        return 5
    if any(kw in body for kw in ("shame", "broken", "defective", "flaw", "nobody talks")):
        return 4
    # Breathing/exercise = 3
    if any(kw in body for kw in ("inhale", "exhale", "breath", "breathing")):
        return 3
    # Dry framework = 2
    if st in ("TEACHER_DOCTRINE",):
        return 4
    if st == "EXERCISE":
        return 3
    if st == "INTEGRATION":
        return 3
    return 3


def _suggest_reader_objection(body: str, purpose: str) -> str:
    p = (purpose or "").lower()
    if "mechanism" in p or "how it works" in body:
        return "not_that_bad"
    if "origin" in p or "where it came from" in body:
        return "not_broken_enough"
    if "practice" in p or "exercise" in p or "try this" in body or "already tried" in body:
        return "already_tried"
    if "cost" in p or "loss" in p or "price" in body:
        return "not_broken_enough"
    if "turning" in p or "difficult" in p:
        return "too_painful"
    if "relapse" in p or "setback" in p:
        return "wont_work_for_me"
    if "identity" in p:
        return "wont_work_for_me"
    return "not_that_bad"


def suggest_tags(section_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict of suggested metadata fields for a section."""
    meta = section_data.get("metadata") or {}
    section_type = str(meta.get("section_type") or section_data.get("type") or "")
    purpose = str(section_data.get("purpose") or "")
    body = _get_body_text(section_data)

    return {
        "reader_objection": _suggest_reader_objection(body, purpose),
        "proof_mode": _suggest_proof_mode(body),
        "tension_type": _suggest_tension_type(body),
        "propulsion_type": _suggest_propulsion(body),
        "shareability": _suggest_shareability(body, section_type),
        "collision_family": _suggest_collision_family(body, section_type),
    }


def _is_missing_metadata(section_data: Dict[str, Any]) -> bool:
    """Return True if any of the 6 fields are missing from the section's metadata."""
    meta = section_data.get("metadata") or {}
    return any(f not in meta for f in METADATA_FIELDS)


def _iter_sections(data: Dict[str, Any]):
    """Yield (chapter_key, section_key, section_data) for all sections."""
    sections_root = data.get("sections") or {}
    for ch_key, ch_data in sections_root.items():
        if not isinstance(ch_data, dict):
            continue
        for sec_key, sec_data in (ch_data.get("sections") or {}).items():
            if not isinstance(sec_data, dict):
                continue
            yield ch_key, sec_key, sec_data


def patch_yaml_text(raw: str, data: Dict[str, Any]) -> str:
    """Patch the raw YAML text in-place with suggested metadata fields for missing sections."""
    lines = raw.split("\n")
    new_lines: List[str] = []

    # Build lookup: section_id -> suggested tags (only for sections missing fields)
    suggestions: Dict[str, Dict[str, Any]] = {}
    for ch_key, sec_key, sec_data in _iter_sections(data):
        sec_type = str(sec_data.get("type") or "").upper()
        if sec_type == "STORY":
            continue
        sec_id = str(sec_data.get("section_id") or "")
        if sec_id and _is_missing_metadata(sec_data):
            suggestions[sec_id] = suggest_tags(sec_data)

    current_section_id: Optional[str] = None
    in_metadata = False
    metadata_indent = ""
    loc_tokens_list_mode = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        m = re.match(r"^(\s+)section_id:\s+(\S+)", line)
        if m:
            current_section_id = m.group(2)
            in_metadata = False
            loc_tokens_list_mode = False

        if current_section_id and re.match(r"^\s+metadata:\s*$", line):
            in_metadata = True
            mm = re.match(r"^(\s+)", line)
            metadata_indent = mm.group(1) if mm else "        "
            loc_tokens_list_mode = False

        if in_metadata:
            loc_m = re.match(r"^(\s+)location_tokens:\s*(\[\])?$", line)
            if loc_m:
                if loc_m.group(2) == "[]":
                    new_lines.append(line)
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if "reader_objection:" not in next_line and current_section_id in suggestions:
                        tags = suggestions[current_section_id]
                        ind = metadata_indent + "  "
                        for field in METADATA_FIELDS:
                            new_lines.append(f"{ind}{field}: {tags[field]}")
                    in_metadata = False
                    current_section_id = None
                    i += 1
                    continue
                else:
                    loc_tokens_list_mode = True
                    new_lines.append(line)
                    i += 1
                    continue

            if loc_tokens_list_mode:
                if stripped.startswith("- '") or stripped.startswith('- "') or stripped.startswith("- {"):
                    new_lines.append(line)
                    i += 1
                    continue
                else:
                    if current_section_id in suggestions:
                        tags = suggestions[current_section_id]
                        ind = metadata_indent + "  "
                        for field in METADATA_FIELDS:
                            new_lines.append(f"{ind}{field}: {tags[field]}")
                    in_metadata = False
                    loc_tokens_list_mode = False
                    current_section_id = None
                    new_lines.append(line)
                    i += 1
                    continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Suggest bestseller metadata tags for un-tagged atoms in a registry YAML."
    )
    parser.add_argument("--registry", required=True, help="Path to registry YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print suggestions only, don't write")
    parser.add_argument("--write", action="store_true", help="Patch file in-place with suggestions")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print("ERROR: specify --dry-run or --write", file=sys.stderr)
        sys.exit(1)

    reg_path = Path(args.registry)
    if not reg_path.exists():
        print(f"ERROR: registry file not found: {reg_path}", file=sys.stderr)
        sys.exit(1)

    raw = reg_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Collect suggestions
    needs_tagging = []
    for ch_key, sec_key, sec_data in _iter_sections(data):
        sec_type = str(sec_data.get("type") or "").upper()
        if sec_type == "STORY":
            continue
        sec_id = str(sec_data.get("section_id") or "")
        if _is_missing_metadata(sec_data):
            tags = suggest_tags(sec_data)
            needs_tagging.append((sec_id, sec_type, sec_data.get("purpose", ""), tags))

    if not needs_tagging:
        print(f"All sections in {reg_path.name} already have metadata fields. Nothing to do.")
        return

    print(f"Found {len(needs_tagging)} sections missing metadata fields in {reg_path.name}:")
    print()

    for sec_id, sec_type, purpose, tags in needs_tagging:
        print(f"  [{sec_id}] type={sec_type}, purpose={purpose!r}")
        for field in METADATA_FIELDS:
            print(f"    {field}: {tags[field]}")
        print()

    if args.dry_run:
        print(f"(dry-run — no changes written)")
        return

    # Write mode: patch in-place
    patched = patch_yaml_text(raw, data)

    # Validate patched YAML parses
    try:
        yaml.safe_load(patched)
    except yaml.YAMLError as e:
        print(f"ERROR: patched YAML is invalid: {e}", file=sys.stderr)
        sys.exit(1)

    reg_path.write_text(patched, encoding="utf-8")
    print(f"Wrote {reg_path} with {len(needs_tagging)} sections tagged.")


if __name__ == "__main__":
    main()

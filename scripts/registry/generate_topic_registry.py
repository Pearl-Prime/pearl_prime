#!/usr/bin/env python3
"""
generate_topic_registry.py — Phoenix Omega V4 Registry Generator

Generates complete section registry YAML files for each topic, using:
  1. PERSONA ATOM POOL   — atoms/gen_z_professionals/{topic}/ CANONICAL.txt
  2. TEACHER ATOM ADAPT  — SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/{TYPE}/
  3. QWEN GENERATION     — Pearl Star at 192.168.1.112:11434, model qwen2.5:14b

Usage:
    python3 scripts/registry/generate_topic_registry.py --topic anxiety
    python3 scripts/registry/generate_topic_registry.py --all
    python3 scripts/registry/generate_topic_registry.py --all --dry-run
    python3 scripts/registry/generate_topic_registry.py --provenance-report
    python3 scripts/registry/generate_topic_registry.py --topic anxiety --resume

Environment:
    PEARL_STAR_IP=192.168.1.112  (default)
    QWEN_MODEL=qwen2.5:14b       (default)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

# ─── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "registry"
TEMPLATE_PATH = REPO_ROOT / "scripts" / "registry" / "registry_template.yaml"
TITLES_PATH = REPO_ROOT / "config" / "registry" / "topic_chapter_titles.yaml"
SKINS_PATH = REPO_ROOT / "config" / "topic_skins.yaml"
ENGINE_BINDINGS_PATH = REPO_ROOT / "config" / "topic_engine_bindings.yaml"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
ATOMS_ROOT = REPO_ROOT / "atoms"
CACHE_ROOT = REPO_ROOT / "artifacts" / "registry_gen"

# ─── Constants ───────────────────────────────────────────────────────────────
PERSONA = "gen_z_professionals"
TEACHER_ID = "ahjan"

PEARL_STAR_IP = os.environ.get("PEARL_STAR_IP", "192.168.1.112")
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen2.5:14b")
QWEN_BASE_URL = f"http://{PEARL_STAR_IP}:11434/v1"
QWEN_RATE_LIMIT_S = 2.0  # seconds between Qwen calls

ALL_TOPICS = [
    "anxiety", "burnout", "self_worth", "imposter_syndrome", "boundaries",
    "depression", "courage", "overthinking", "compassion_fatigue",
    "social_anxiety", "sleep_anxiety", "financial_anxiety",
    "financial_stress", "somatic_healing",
]

# Chapter section layouts (from template — sequence of type per chapter)
CHAPTER_LAYOUTS: dict[str, list[dict]] = {
    "chapter_01": [
        {"seq": 1,  "type": "HOOK",            "scene_type": None,          "location_aware": False, "min_variants": 5},
        {"seq": 2,  "type": "SCENE",           "scene_type": "digital",     "location_aware": True,  "min_variants": 5},
        {"seq": 3,  "type": "SCENE",           "scene_type": "relational",  "location_aware": True,  "min_variants": 5},
        {"seq": 4,  "type": "SCENE",           "scene_type": "social",      "location_aware": True,  "min_variants": 5},
        {"seq": 5,  "type": "REFLECTION",      "scene_type": None,          "location_aware": False, "min_variants": 3},
        {"seq": 6,  "type": "TEACHER_DOCTRINE","scene_type": None,          "location_aware": False, "min_variants": 5},
        {"seq": 7,  "type": "REFLECTION",      "scene_type": None,          "location_aware": False, "min_variants": 3},
        {"seq": 8,  "type": "REFLECTION",      "scene_type": None,          "location_aware": False, "min_variants": 3},
        {"seq": 9,  "type": "INTEGRATION",     "scene_type": None,          "location_aware": False, "min_variants": 3},
        {"seq": 10, "type": "INTEGRATION",     "scene_type": None,          "location_aware": False, "min_variants": 3},
    ],
    "chapter_02": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,     "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "origin", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 8, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 9, "type": "INTEGRATION", "scene_type": None,     "location_aware": False, "min_variants": 3},
    ],
    "chapter_03": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,       "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "internal", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,       "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,       "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,       "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,       "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "REFLECTION",  "scene_type": None,       "location_aware": False, "min_variants": 3},
        {"seq": 8, "type": "INTEGRATION", "scene_type": None,       "location_aware": False, "min_variants": 3},
    ],
    "chapter_04": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,     "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "action", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "EXERCISE",    "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,     "location_aware": False, "min_variants": 3},
    ],
    "chapter_05": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,             "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "high-intensity", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,             "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,             "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,             "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,             "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,             "location_aware": False, "min_variants": 3},
    ],
    "chapter_06": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,     "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "memory", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,     "location_aware": False, "min_variants": 3},
    ],
    "chapter_07": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,     "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "action", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "EXERCISE",    "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "EXERCISE",    "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "EXERCISE",    "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,     "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,     "location_aware": False, "min_variants": 3},
    ],
    "chapter_08": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,      "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "setback", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "EXERCISE",    "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "EXERCISE",    "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "EXERCISE",    "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,      "location_aware": False, "min_variants": 3},
    ],
    "chapter_09": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,           "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "integration",  "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,           "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,           "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,           "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,           "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,           "location_aware": False, "min_variants": 3},
    ],
    "chapter_10": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,      "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "setback", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,      "location_aware": False, "min_variants": 3},
    ],
    "chapter_11": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,      "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "forward", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,      "location_aware": False, "min_variants": 3},
    ],
    "chapter_12": [
        {"seq": 1, "type": "HOOK",        "scene_type": None,      "location_aware": False, "min_variants": 5},
        {"seq": 2, "type": "SCENE",       "scene_type": "forward", "location_aware": True,  "min_variants": 5},
        {"seq": 3, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 4, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 5, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 6, "type": "REFLECTION",  "scene_type": None,      "location_aware": False, "min_variants": 3},
        {"seq": 7, "type": "INTEGRATION", "scene_type": None,      "location_aware": False, "min_variants": 3},
    ],
}

ARC_ROLES = {
    "chapter_01": "recognition",
    "chapter_02": "origin",
    "chapter_03": "pattern",
    "chapter_04": "mechanism",
    "chapter_05": "cost",
    "chapter_06": "turning_point",
    "chapter_07": "first_practice",
    "chapter_08": "difficulty",
    "chapter_09": "integration",
    "chapter_10": "relapse",
    "chapter_11": "identity",
    "chapter_12": "forward",
}

LOCATION_TOKENS = {
    "digital":        "{location.digital_space}",
    "relational":     "{location.digital_space}",
    "social":         "{location.social_gathering}",
    "origin":         "{location.memory_space}",
    "internal":       "{location.daily_space}",
    "action":         "{location.learning_space}",
    "high-intensity": "{location.high_stakes_space}",
    "memory":         "{location.memory_space}",
    "setback":        "{location.daily_space}",
    "integration":    "{location.daily_space}",
    "forward":        "{location.learning_space}",
}

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── Config loaders ──────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_topic_skin(topic: str) -> dict:
    skins = _load_yaml(SKINS_PATH)
    global_rules = skins.get("global_rules", {})
    topic_skin = skins.get(topic, {})
    prohibited = list(global_rules.get("prohibited_terms", []))
    prohibited += topic_skin.get("additional_prohibited_terms", [])
    prohibited_patterns = list(global_rules.get("prohibited_patterns", []))
    return {
        "prohibited_terms": prohibited,
        "prohibited_patterns": prohibited_patterns,
        "recognition_suffix": topic_skin.get("recognition_suffix", {}).get("text", ""),
        "mechanism_proof_suffix": topic_skin.get("mechanism_proof_suffix", {}).get("text", ""),
        "turning_point_suffix": topic_skin.get("turning_point_suffix", {}).get("text", ""),
        "embodiment_suffix": topic_skin.get("embodiment_suffix", {}).get("text", ""),
        "allowed_terms_override": topic_skin.get("allowed_terms_override", []),
    }


def load_engine_bindings(topic: str) -> dict:
    bindings = _load_yaml(ENGINE_BINDINGS_PATH)
    return bindings.get(topic, {})


def load_chapter_titles(topic: str) -> dict:
    titles = _load_yaml(TITLES_PATH)
    return titles.get(topic, {})

# ─── Atom pool loaders ───────────────────────────────────────────────────────

def _parse_canonical_txt(path: Path) -> list[str]:
    """Parse CANONICAL.txt into list of prose content strings."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = []
    current_lines: list[str] = []
    in_body = False
    delimiter_count = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    blocks.append(content)
            current_lines = []
            in_body = False
            delimiter_count = 0
        elif stripped == "---":
            delimiter_count += 1
            if delimiter_count >= 2:
                in_body = True
        elif in_body:
            current_lines.append(line)

    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            blocks.append(content)

    return blocks


def load_persona_atoms(topic: str) -> dict[str, list[str]]:
    """Load persona atom content from atoms/gen_z_professionals/{topic}/"""
    persona_root = ATOMS_ROOT / PERSONA / topic
    atoms: dict[str, list[str]] = {}
    if not persona_root.exists():
        return atoms
    for slot_dir in persona_root.iterdir():
        if not slot_dir.is_dir():
            continue
        canonical = slot_dir / "CANONICAL.txt"
        if canonical.exists():
            parsed = _parse_canonical_txt(canonical)
            if parsed:
                atoms[slot_dir.name.upper()] = parsed
    return atoms


def load_teacher_atoms() -> dict[str, list[str]]:
    """Load teacher atom content from SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/"""
    teacher_root = TEACHER_BANKS_ROOT / TEACHER_ID / "approved_atoms"
    atoms: dict[str, list[str]] = {}
    if not teacher_root.exists():
        return atoms
    for slot_dir in teacher_root.iterdir():
        if not slot_dir.is_dir():
            continue
        slot_type = slot_dir.name.upper()
        contents = []
        for atom_file in sorted(slot_dir.glob("*.yaml")):
            data = _load_yaml(atom_file)
            body = data.get("body", data.get("content", ""))
            if body:
                contents.append(str(body))
        if contents:
            atoms[slot_type] = contents
    return atoms


# ─── Fingerprint ─────────────────────────────────────────────────────────────

def compute_fingerprint(content: str) -> dict:
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    # Simple sentence split: split on . ! ? followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    sentences = [s for s in sentences if s.strip()]
    return {
        "char_count": len(content),
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
    }


def extract_location_tokens(content: str) -> list[str]:
    return sorted(set(re.findall(r'\{location\.[^}]+\}', content)))


# ─── Cache ───────────────────────────────────────────────────────────────────

def _cache_path(topic: str, ch_key: str, sec_key: str, variant_n: int) -> Path:
    return CACHE_ROOT / topic / f"{ch_key}_{sec_key}_v{variant_n}.txt"


def _load_cached(topic: str, ch_key: str, sec_key: str, variant_n: int) -> Optional[str]:
    p = _cache_path(topic, ch_key, sec_key, variant_n)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def _save_cache(topic: str, ch_key: str, sec_key: str, variant_n: int, content: str) -> None:
    p = _cache_path(topic, ch_key, sec_key, variant_n)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ─── Provenance tracking ─────────────────────────────────────────────────────

_provenance_log: list[dict] = []


def _track(topic: str, ch_key: str, sec_key: str, variant_n: int, source: str) -> None:
    _provenance_log.append({
        "topic": topic,
        "chapter": ch_key,
        "section": sec_key,
        "variant": variant_n,
        "source": source,
    })


# ─── Qwen generation ─────────────────────────────────────────────────────────

def _build_system_prompt(topic: str, skin: dict, section_type: str, arc_role: str) -> str:
    prohibited = skin.get("prohibited_terms", [])
    arc_suffix = ""
    if arc_role == "recognition":
        arc_suffix = skin.get("recognition_suffix", "")
    elif arc_role in ("mechanism", "mechanism_proof"):
        arc_suffix = skin.get("mechanism_proof_suffix", "")
    elif arc_role == "turning_point":
        arc_suffix = skin.get("turning_point_suffix", "")
    elif arc_role in ("integration", "first_practice", "identity", "forward"):
        arc_suffix = skin.get("embodiment_suffix", "")

    prohibited_str = ", ".join(f'"{t}"' for t in prohibited[:20]) if prohibited else "none"

    type_instructions = {
        "HOOK": (
            "Write a HOOK section: 3–5 short paragraphs, maximum 400 words. "
            "Concrete image + body state + recognition moment. "
            "Sentences 8–15 words each. Second person present tense. "
            "End with '---' on its own line."
        ),
        "SCENE": (
            "Write a SCENE section: 5–8 paragraphs of sensory immersion, 300–500 words. "
            "One concrete detail per sentence. Second person present tense. "
            "Honor the section purpose exactly — digital, relational, and social scenes "
            "must be distinct and purpose-appropriate. "
            "Never emit unresolved template tokens (no {location.*}, no {weather_detail}). "
            "Illustrates the pattern — does not explain it. "
            "End with '---' on its own line."
        ),
        "REFLECTION": (
            "Write a REFLECTION section: mechanism explanation, 4–8 paragraphs, 180–280 words. "
            "Second person present tense. Active verbs. Body anchors for emotional moments. "
            "No rhetorical questions — convert to statements. "
            "End with '---' on its own line."
        ),
        "TEACHER_DOCTRINE": (
            "Write a TEACHER_DOCTRINE section: core worldview statement, 5–8 paragraphs, 200–350 words. "
            "Authoritative but not prescriptive. Names the pattern, corrects the misconception, "
            "offers the reframe. No wellness language. Second person. "
            "End with '---' on its own line."
        ),
        "EXERCISE": (
            "Write an EXERCISE section: body-based practice, 4–6 steps. "
            "Imperatives only, maximum 10 words per instruction. "
            "Concrete physical actions, not metaphors. 100–150 words total. "
            "End with '---' on its own line."
        ),
        "INTEGRATION": (
            "Write an INTEGRATION section: landing not summary, 3–5 paragraphs, 120–200 words. "
            "One reframe, one carry line (8 words or fewer). Concrete body state. "
            "No reassurance language. Second person present tense. "
            "End with '---' on its own line."
        ),
    }
    type_instruction = type_instructions.get(section_type, type_instructions["REFLECTION"])

    lines = [
        f"You are writing therapeutic audiobook content for the topic '{topic}'.",
        "",
        "RULES (non-negotiable):",
        "- Second person, present tense throughout",
        "- Behavior over emotion, specific over abstract",
        "- Active verbs only. No passive constructions.",
        "- No rhetorical questions. Convert to statements.",
        f"- PROHIBITED TERMS (never use): {prohibited_str}",
        "- No therapy/wellness language: no 'self-care', 'mindfulness', 'empower', 'safe space', 'toxic'",
        "- TTS-optimized: sentences 8–25 words, paragraph breaks every 60–80 words",
        "- No markdown headers. No bullet points. Prose paragraphs only.",
        f"- Arc role for this chapter: {arc_role}",
        f"- Arc framing note: {arc_suffix}" if arc_suffix else "",
        "",
        "SECTION TYPE INSTRUCTIONS:",
        type_instruction,
    ]
    return "\n".join(l for l in lines if l is not None)


def qwen_generate(
    topic: str,
    section_type: str,
    arc_role: str,
    chapter_title: str,
    section_purpose: str,
    variant_n: int,
    prev_opening: str,
    skin: dict,
    location_token: Optional[str],
    dry_run: bool = False,
) -> str:
    if dry_run:
        return f"[DRY RUN — {topic} {section_type} ch variant {variant_n}]"

    system = _build_system_prompt(topic, skin, section_type, arc_role)
    # Never splice unresolved {location.*} placeholders into prompts or prose.
    # SCENE distinctness comes from section_purpose (scene_*_purpose), not token injection.

    diversity_hint = ""
    if prev_opening and variant_n > 1:
        diversity_hint = (
            f"\nPREVIOUS VARIANT OPENED WITH: \"{prev_opening[:120]}...\"\n"
            "Make this variant structurally different — different opening sentence, "
            "different concrete image, different metaphor or scene entry point."
        )

    user_msg = (
        f"Write variant {variant_n} of 5.\n"
        f"Chapter title: \"{chapter_title}\"\n"
        f"Section purpose: \"{section_purpose}\"\n"
        f"Section type: {section_type}\n"
        f"Arc role: {arc_role}\n"
        + diversity_hint
    )

    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user_msg},
        ],
        "temperature": 0.85,
        "max_tokens": 800,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{QWEN_BASE_URL}/chat/completions",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        # Strip trailing --- if present (we add it ourselves in fingerprint pass)
        content = re.sub(r'\n---\s*$', '', content).strip()
        return content
    except Exception as e:
        logger.error("Qwen error: %s", e)
        return f"[GENERATION_FAILED: {e}]"


# ─── Variant generation logic ─────────────────────────────────────────────────

def get_section_purpose(titles: dict, ch_key: str, sec_spec: dict) -> str:
    # ch_key is "chapter_01" but titles map uses "ch01"
    short_key = "ch" + ch_key.split("_")[1]
    ch_data = titles.get("chapters", {}).get(short_key, {})
    seq = sec_spec["seq"]
    sec_type = sec_spec["type"]
    scene_type = sec_spec.get("scene_type")

    if seq == 1:
        return ch_data.get("hook_purpose", f"{sec_type} — ch{ch_key}")
    if sec_type == "SCENE":
        if scene_type == "digital":
            return ch_data.get("scene_digital_purpose", ch_data.get("scene_purpose", f"SCENE {scene_type}"))
        elif scene_type == "relational":
            return ch_data.get("scene_relational_purpose", ch_data.get("scene_purpose", f"SCENE {scene_type}"))
        elif scene_type == "social":
            return ch_data.get("scene_social_purpose", ch_data.get("scene_purpose", f"SCENE {scene_type}"))
        return ch_data.get("scene_purpose", f"SCENE {scene_type}")
    if sec_type == "TEACHER_DOCTRINE":
        return ch_data.get("doctrine_purpose", "Teacher doctrine — core worldview")
    if sec_type == "INTEGRATION":
        if seq == 9 or seq == 10:
            return ch_data.get("integration_purpose", ch_data.get(f"integration_0{seq - 8}_purpose", "Integration landing"))
        return ch_data.get("integration_purpose", "Landing")
    if sec_type == "REFLECTION":
        ref_seq = seq - (4 if ch_key == "chapter_01" else 2)
        key = f"reflection_0{ref_seq}_purpose"
        return ch_data.get(key, f"REFLECTION {seq} — {ARC_ROLES.get(ch_key, '')}")
    if sec_type == "EXERCISE":
        return f"EXERCISE — {ARC_ROLES.get(ch_key, 'practice')}"
    return f"{sec_type} — {ARC_ROLES.get(ch_key, '')}"


def generate_variants(
    topic: str,
    ch_key: str,
    sec_key: str,
    sec_spec: dict,
    sec_id: str,
    section_purpose: str,
    chapter_title: str,
    arc_role: str,
    skin: dict,
    persona_atoms: dict[str, list[str]],
    teacher_atoms: dict[str, list[str]],
    min_variants: int,
    dry_run: bool,
    resume: bool,
) -> tuple[list[dict], dict[str, int]]:
    """Generate `min_variants` variants for one section. Returns (variants_list, provenance_counts)."""
    sec_type = sec_spec["type"]
    scene_type = sec_spec.get("scene_type")
    # LOCATION_TOKENS are unresolved {location.*} placeholders — never inject them.
    # SCENE purpose-distinctness is driven by section_purpose (scene_*_purpose).
    location_token = None

    # Variant family names
    if sec_type == "TEACHER_DOCTRINE":
        families = [f"D{i:02d}" for i in range(1, min_variants + 1)]
    else:
        families = [f"F{i}" for i in range(1, min_variants + 1)]

    provenance_counts = {"atom_pool": 0, "teacher_adapted": 0, "qwen_generated": 0}
    variants = []
    prev_opening = ""

    # Pool from persona atoms (HOOK/STORY only). SCENE always routes to Qwen so
    # scene_{digital,relational,social}_purpose is honored — robotic SCENE banks
    # (atoms/*/SCENE/CANONICAL.txt) are code-path dead (physical delete needs Rule 0).
    persona_pool = persona_atoms.get(sec_type, [])

    # Pool from teacher atoms (TEACHER_DOCTRINE, HOOK, EXERCISE, INTEGRATION)
    teacher_type_map = {
        "TEACHER_DOCTRINE": ["COMPRESSION", "REFLECTION", "TEACHING"],
        "HOOK": ["HOOK"],
        "EXERCISE": ["EXERCISE"],
        "INTEGRATION": ["INTEGRATION"],
        "REFLECTION": ["REFLECTION", "TEACHING"],
    }
    teacher_pool: list[str] = []
    for dir_name in teacher_type_map.get(sec_type, []):
        pool = teacher_atoms.get(dir_name, [])
        if pool:
            teacher_pool = pool
            break

    for i, family in enumerate(families):
        variant_n = i + 1
        variant_id = f"{sec_id}_{sec_type.lower().replace('_', '')}_{family.lower()}"

        # 1. Check resume cache
        if resume:
            cached = _load_cached(topic, ch_key, sec_key, variant_n)
            if cached:
                fp = compute_fingerprint(cached)
                loc_toks = extract_location_tokens(cached)
                variants.append({
                    "variant_id": variant_id,
                    "variant_number": variant_n,
                    "variant_family": family,
                    "content": cached,
                    "fingerprint": fp,
                    "location_tokens": loc_toks,
                    "_provenance": "cached",
                })
                prev_opening = cached[:80]
                continue

        # 2. Try persona atom pool (HOOK/STORY only — SCENE is Qwen-by-purpose)
        content = None
        source = "qwen_generated"

        if persona_pool and sec_type in ("HOOK", "STORY"):
            idx = i % len(persona_pool)
            atom_content = persona_pool[idx]
            if atom_content and len(atom_content) > 50:
                content = atom_content
                source = "atom_pool"
                provenance_counts["atom_pool"] += 1
                _track(topic, ch_key, sec_key, variant_n, "atom_pool")

        # 3. Try teacher atom adaptation (for TEACHER_DOCTRINE, EXERCISE, INTEGRATION)
        if content is None and teacher_pool and sec_type in ("TEACHER_DOCTRINE", "EXERCISE", "INTEGRATION", "HOOK", "REFLECTION"):
            idx = i % len(teacher_pool)
            teacher_content = teacher_pool[idx]
            if teacher_content and len(teacher_content) > 50:
                # Adapt by prepending topic context note (thin layer)
                content = teacher_content
                source = "teacher_adapted"
                provenance_counts["teacher_adapted"] += 1
                _track(topic, ch_key, sec_key, variant_n, "teacher_adapted")

        # 4. Fall back to Qwen generation (SCENE always lands here)
        if content is None:
            logger.info("  Qwen: %s ch%s sec%s v%d", topic, ch_key[-2:], sec_key[-2:], variant_n)
            content = qwen_generate(
                topic=topic,
                section_type=sec_type,
                arc_role=arc_role,
                chapter_title=chapter_title,
                section_purpose=section_purpose,
                variant_n=variant_n,
                prev_opening=prev_opening,
                skin=skin,
                location_token=location_token,
                dry_run=dry_run,
            )
            source = "qwen_generated"
            provenance_counts["qwen_generated"] += 1
            _track(topic, ch_key, sec_key, variant_n, "qwen_generated")
            if not dry_run:
                time.sleep(QWEN_RATE_LIMIT_S)

        # Save to cache
        if not dry_run:
            _save_cache(topic, ch_key, sec_key, variant_n, content)

        fp = compute_fingerprint(content)
        loc_toks = extract_location_tokens(content)

        variants.append({
            "variant_id": variant_id,
            "variant_number": variant_n,
            "variant_family": family,
            "content": content,
            "fingerprint": fp,
            "location_tokens": loc_toks,
            "_provenance": source,
        })
        prev_opening = content[:80]

    return variants, provenance_counts


# ─── Registry builder ────────────────────────────────────────────────────────

def build_registry(
    topic: str,
    dry_run: bool = False,
    resume: bool = False,
) -> dict:
    """Build the complete registry dict for one topic."""
    skin = load_topic_skin(topic)
    titles = load_chapter_titles(topic)
    display_name = titles.get("display_name", topic.replace("_", " ").title())
    persona_atoms = load_persona_atoms(topic)
    teacher_atoms = load_teacher_atoms()

    logger.info("Building registry: %s (dry_run=%s resume=%s)", topic, dry_run, resume)
    logger.info("  Persona atom types loaded: %s", list(persona_atoms.keys()))
    logger.info("  Teacher atom types loaded: %s", list(teacher_atoms.keys()))

    registry: dict = {
        "sections": {}
    }

    total_variants = 0
    total_provenance = {"atom_pool": 0, "teacher_adapted": 0, "qwen_generated": 0}

    for ch_key in sorted(CHAPTER_LAYOUTS.keys()):
        arc_role = ARC_ROLES[ch_key]
        ch_num = int(ch_key.split("_")[1])
        # ch_key is "chapter_01", titles map uses "ch01"
        short_key = "ch" + ch_key.split("_")[1]
        ch_titles = titles.get("chapters", {}).get(short_key, {})
        ch_title = ch_titles.get("title", f"Chapter {ch_num}")

        chapter_dict: dict = {
            "chapter": ch_num,
            "title": ch_title,
            "sections": {},
        }

        logger.info("  Chapter %d: %s", ch_num, ch_title)

        for sec_spec in CHAPTER_LAYOUTS[ch_key]:
            seq = sec_spec["seq"]
            sec_type = sec_spec["type"]
            scene_type = sec_spec.get("scene_type")
            location_aware = sec_spec.get("location_aware", False)
            min_v = sec_spec["min_variants"]
            story_eligible = sec_type in ("HOOK", "REFLECTION", "SCENE")

            sec_key = f"section_{seq:02d}"
            sec_id = f"ch{ch_num:02d}_sec{seq:02d}"

            section_purpose = get_section_purpose(titles, ch_key, sec_spec)

            variants, prov_counts = generate_variants(
                topic=topic,
                ch_key=ch_key,
                sec_key=sec_key,
                sec_spec=sec_spec,
                sec_id=sec_id,
                section_purpose=section_purpose,
                chapter_title=ch_title,
                arc_role=arc_role,
                skin=skin,
                persona_atoms=persona_atoms,
                teacher_atoms=teacher_atoms,
                min_variants=min_v,
                dry_run=dry_run,
                resume=resume,
            )

            for k, v in prov_counts.items():
                total_provenance[k] += v
            total_variants += len(variants)

            # Build location_tokens for metadata (union across all variants)
            all_loc_tokens = sorted(set(
                tok for var in variants for tok in var.get("location_tokens", [])
            ))

            # Strip internal _provenance field for output
            clean_variants = []
            for var in variants:
                clean_var = {k: v for k, v in var.items() if k != "_provenance"}
                clean_variants.append(clean_var)

            chapter_dict["sections"][sec_key] = {
                "section_id": sec_id,
                "section": seq,
                "type": sec_type,
                "purpose": section_purpose,
                "scene_type": scene_type,
                "min_variants_required": min_v,
                "story_eligible": story_eligible,
                "location_aware": location_aware,
                "variants": clean_variants,
                "metadata": {
                    "persona": "Gen Z",
                    "topic": topic,
                    "section_type": sec_type,
                    "scene_type": scene_type,
                    "location_tokens": all_loc_tokens,
                },
            }

        registry["sections"][ch_key] = chapter_dict

    logger.info(
        "Registry built: %s — %d variants total | atom_pool=%d teacher_adapted=%d qwen_generated=%d",
        topic,
        total_variants,
        total_provenance["atom_pool"],
        total_provenance["teacher_adapted"],
        total_provenance["qwen_generated"],
    )
    return registry


# ─── Provenance report ───────────────────────────────────────────────────────

def print_provenance_report() -> None:
    if not _provenance_log:
        print("No provenance data recorded in this session.")
        return

    from collections import Counter
    by_topic: dict[str, Counter] = {}
    for entry in _provenance_log:
        t = entry["topic"]
        if t not in by_topic:
            by_topic[t] = Counter()
        by_topic[t][entry["source"]] += 1

    print("\n=== PROVENANCE REPORT ===")
    for topic in sorted(by_topic):
        c = by_topic[topic]
        total = sum(c.values())
        print(f"  {topic:25s}: {total:3d} variants | "
              f"atom_pool={c['atom_pool']} "
              f"teacher_adapted={c['teacher_adapted']} "
              f"qwen_generated={c['qwen_generated']}")


# ─── YAML serialization ──────────────────────────────────────────────────────

class _LiteralStr(str):
    """YAML block scalar for multiline strings."""
    pass


def _literal_representer(dumper: yaml.Dumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(_LiteralStr, _literal_representer)


def _wrap_content(registry: dict) -> dict:
    """Wrap all content fields in LiteralStr for block scalar output."""
    def _walk(obj):
        if isinstance(obj, dict):
            return {k: (_LiteralStr(v) if k == "content" and isinstance(v, str) else _walk(v))
                    for k, v in obj.items()}
        if isinstance(obj, list):
            return [_walk(item) for item in obj]
        return obj
    return _walk(registry)


def write_registry_yaml(topic: str, registry: dict, display_name: str) -> Path:
    out_path = REGISTRY_ROOT / f"{topic}.yaml"
    header = (
        f"# {display_name} Pack — Phoenix Omega V4\n"
        f"# Generated from universal therapeutic arc template\n"
        f"# Topic skin: config/topic_skins.yaml → {topic}\n"
        f"# Engine bindings: config/topic_engine_bindings.yaml → {topic}\n"
        f"# Generator: scripts/registry/generate_topic_registry.py\n\n"
    )
    wrapped = _wrap_content(registry)
    body = yaml.dump(
        wrapped,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    out_path.write_text(header + body, encoding="utf-8")
    logger.info("Written: %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Phoenix Omega topic registries from universal arc template + Qwen/atom pool"
    )
    parser.add_argument("--topic", help="Single topic to generate (e.g. anxiety)")
    parser.add_argument("--all", action="store_true", help="Generate all 14 missing topic registries")
    parser.add_argument("--dry-run", action="store_true", help="Skip Qwen calls, output placeholders")
    parser.add_argument("--resume", action="store_true", help="Resume from cache (skip already generated variants)")
    parser.add_argument("--provenance-report", action="store_true", help="Print provenance report and exit")
    parser.add_argument("--list-topics", action="store_true", help="List topics missing registries")
    args = parser.parse_args()

    if args.list_topics:
        existing = {p.stem for p in REGISTRY_ROOT.glob("*.yaml")}
        missing = [t for t in ALL_TOPICS if t not in existing]
        print(f"Missing registries ({len(missing)}): {missing}")
        return

    # Determine topics to build
    topics: list[str] = []
    if args.all:
        existing = {p.stem for p in REGISTRY_ROOT.glob("*.yaml")}
        topics = [t for t in ALL_TOPICS if t not in existing]
        logger.info("Topics to generate (%d): %s", len(topics), topics)
    elif args.topic:
        topics = [args.topic]
    else:
        parser.print_help()
        return

    if not topics:
        print("All registries already exist. Nothing to do.")
        return

    # Ensure cache dir
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    for topic in topics:
        titles = load_chapter_titles(topic)
        display_name = titles.get("display_name", topic.replace("_", " ").title())
        registry = build_registry(
            topic=topic,
            dry_run=args.dry_run,
            resume=args.resume,
        )
        if not args.dry_run:
            write_registry_yaml(topic, registry, display_name)
        else:
            chapters = registry.get("sections", {})
            total_vars = sum(
                len(sec.get("variants", []))
                for ch in chapters.values()
                for sec in ch.get("sections", {}).values()
            )
            print(f"[DRY RUN] {topic}: {len(chapters)} chapters, {total_vars} variant slots")

    if args.provenance_report:
        print_provenance_report()

    if not args.dry_run:
        print("\nAll done. Validate with:")
        print("  python3 -c \"")
        print("  from phoenix_v4.planning.registry_resolver import load_registry, available_registries")
        print("  for t in available_registries(): r = load_registry(t); print(t, len(r['sections']), 'chapters')")
        print("  \"")


if __name__ == "__main__":
    main()

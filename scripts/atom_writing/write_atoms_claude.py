#!/usr/bin/env python3
"""
Atom Writer Module — write_atoms_claude.py

Provides prompt builders, output parsers, and file writers for atom generation.
This module does NOT call any external API. It is designed to be used from
Claude Code sessions via the Agent tool (zero external API cost).

Architecture:
    1. generate_campaign_plan() -> outputs campaign_plan.json
    2. Claude Code session reads plan and spawns Agent subagents per item
    3. Each subagent uses build_system_prompt() + build_user_prompt() as its prompt
    4. Subagent output is parsed by parse_canonical_output() and written by write_canonical()

Usage from Claude Code:
    # In a Claude Code session:
    from scripts.atom_writing.write_atoms_claude import (
        build_system_prompt, build_user_prompt, write_canonical,
        load_existing_examples, validate_output, generate_campaign_plan,
    )

CLI:
    # Generate campaign plan
    python scripts/atom_writing/write_atoms_claude.py --plan

    # Generate prompt for a single atom batch
    python scripts/atom_writing/write_atoms_claude.py \
        --persona corporate_managers --topic anxiety --slot HOOK --variants 6

    # Parse and write generated output
    python scripts/atom_writing/write_atoms_claude.py \
        --parse --input output.txt --persona corporate_managers --topic anxiety --slot HOOK
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.atom_writing.validate_atoms import (
    ALL_PERSONAS,
    ALL_TOPICS,
    CANONICAL_SLOT_TYPES,
    ENGINE_DIRS,
    FORBIDDEN_PATTERNS,
    WORD_LIMITS,
    validate_canonical,
)

logger = logging.getLogger("atom_writer")

# ─── RE-EXPORTS (for run_writing_campaign.py compatibility) ────────────────
# These are imported by run_writing_campaign.py
__all__ = [
    "ALL_PERSONAS",
    "ALL_TOPICS",
    "ENGINE_DIRS",
    "load_existing_examples",
    "validate_output",
    "write_atoms",
    "write_canonical",
    "build_system_prompt",
    "build_user_prompt",
    "generate_campaign_plan",
]


# ─── SYSTEM PROMPTS ───────────────────────────────────────────────────────────

ATOM_SYSTEM_PROMPT = """You are a professional prose writer for Phoenix Omega, a TTS audiobook system.
You write atoms — short, standalone prose units that are assembled into books.
Your prose will be read by a flat synthetic voice (Google Play auto-narration).

## ABSOLUTE RULES (no exceptions)

1. NO RHETORICAL QUESTIONS. Zero "?" marks.
2. NO TENTATIVE LANGUAGE. Forbidden: perhaps, you might, it's possible, maybe, could be.
3. ACTIVE VERBS ONLY. No "was feeling", "was sitting", "was thinking".
4. BODY ANCHORS REQUIRED. Every emotional moment grounded in concrete body state.
5. NEVER USE "WE".
6. Max 15 words per emotional beat. One action per sentence.

## PERSONA-AWARE GROUNDING

- "The drive" not "the train." "The kitchen counter" not "a coffee shop."
- Body sensations first, weather never.
- No geographic specifics. Universal physical experience.

## OUTPUT FORMAT

Use CANONICAL.txt format. Each variant starts with a header:

## {SLOT_TYPE} v{NN}

---
{metadata if applicable}
---
{prose body}

Separate variants with blank lines. Number variants starting at v01.
"""

SLOT_SPECIFIC_GUIDANCE: dict[str, str] = {
    "HOOK": "HOOK atoms are 40-60 words. One sharp opening beat. Grab attention in the first sentence. End with a body-anchored moment that creates urgency.",
    "SCENE": "SCENE atoms are 60-80 words. Set a specific moment. Named character optional. Third-person present tense. Show don't tell. Ground in physical space.",
    "STORY": "STORY atoms are 200-300 words. Named character. Specific moment. Third-person present tense. Use dialogue. Show visible consequences for every action. Include MECHANISM_DEPTH (1-5), IDENTITY_STAGE (pre_awareness/destabilization/self_claim/integration), COST_TYPE (social/internal/identity/relational), COST_INTENSITY (1-5) in metadata.",
    "REFLECTION": "REFLECTION atoms are 150-220 words. Direct address to reader. Guide them to examine their own experience. Include family (origin/current), voice_mode (gentle/direct/fierce), mechanism_emphasis in metadata.",
    "EXERCISE": "EXERCISE atoms are 50-80 words. One clear instruction. Body-first. No setup. Just the action. Reader should be able to do it right now.",
    "INTEGRATION": "INTEGRATION atoms are 150-250 words. Bridge a teaching into daily life. Concrete steps. Include integration_mode and reframe_type in metadata.",
    "PIVOT": "PIVOT atoms are 25-40 words. One sharp reframe. Flip the reader's assumption. Maximum density.",
    "TAKEAWAY": "TAKEAWAY atoms are 40-60 words. One clear insight to carry forward. Memorable phrasing. Body-anchored.",
    "THREAD": "THREAD atoms are 40-60 words. Connect this chapter to the next. Create continuity without cliffhangers.",
    "PERMISSION": "PERMISSION atoms are 40-60 words. Grant the reader explicit permission for something they've been denying themselves. Direct. Fierce. No hedging.",
    "COMPRESSION": "COMPRESSION atoms are 80-120 words. Dense summary of a teaching. Maximum information per word. No filler.",
}

ENGINE_GUIDANCE: dict[str, str] = {
    "watcher": "The Watcher engine: dissociation, observation from distance, numbness as protection. Character notices they're watching their life from outside.",
    "shame": "The Shame engine: core unworthiness, hiding, performing to cover. Character's body contracts — shoulders round, gaze drops, voice thins.",
    "comparison": "The Comparison engine: measuring against others, never-enough, ranking. Character's eyes scan for evidence of falling behind.",
    "false_alarm": "The False Alarm engine: anxiety without danger, body lying about threat. Character's body fires fight-or-flight in safe environments.",
    "overwhelm": "The Overwhelm engine: too much input, shutdown, paralysis. Character's processing collapses — everything becomes static.",
    "grief": "The Grief engine: loss that changes shape but never resolves. Character discovers grief in unexpected moments — a smell, a phrase, an empty chair.",
    "spiral": "The Spiral engine: recursive thinking, loop without exit, thought eating itself. Character notices the same thought arriving for the third time.",
}


# ─── PROMPT BUILDERS ──────────────────────────────────────────────────────────

def build_system_prompt(slot_type: str) -> str:
    """Build the system prompt for a given slot type or engine."""
    base = ATOM_SYSTEM_PROMPT
    guidance = SLOT_SPECIFIC_GUIDANCE.get(slot_type) or ENGINE_GUIDANCE.get(slot_type, "")
    if guidance:
        base += f"\n## SLOT-SPECIFIC GUIDANCE: {slot_type}\n\n{guidance}\n"
    return base


def build_user_prompt(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    num_variants: int = 6,
    existing_examples: list[str] | None = None,
    is_engine: bool = False,
    engine_name: str | None = None,
) -> str:
    """Build the user prompt for atom generation."""
    actual_slot = engine_name if is_engine else slot_type
    word_limit = WORD_LIMITS.get(actual_slot, 300)

    parts = [
        f"Write {num_variants} new {actual_slot} atom variants.",
        f"Persona: {persona_id.replace('_', ' ').title()}",
        f"Topic: {topic_id.replace('_', ' ').title()}",
        f"Word limit per variant: {word_limit} words",
        "",
    ]

    if is_engine and engine_name:
        eg = ENGINE_GUIDANCE.get(engine_name, "")
        if eg:
            parts.append(f"Engine context: {eg}")
            parts.append("")

    if existing_examples:
        parts.append(f"Here are {len(existing_examples)} existing examples to match in quality and style:")
        parts.append("---BEGIN EXAMPLES---")
        for ex in existing_examples[:3]:
            parts.append(ex.strip())
            parts.append("---")
        parts.append("---END EXAMPLES---")
        parts.append("")

    parts.extend([
        f"Number variants v01 through v{num_variants:02d}.",
        f"Use the ## {actual_slot} vNN header format.",
        "Vary emotional intensity across variants.",
        "Ground every emotional moment in the body.",
    ])

    return "\n".join(parts)


# ─── EXAMPLE LOADER ───────────────────────────────────────────────────────────

def load_existing_examples(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    max_examples: int = 2,
    atoms_dir: Path | None = None,
) -> list[str]:
    """Load existing CANONICAL.txt examples for few-shot prompting."""
    if atoms_dir is None:
        atoms_dir = REPO_ROOT / "atoms"

    canon = atoms_dir / persona_id / topic_id / slot_type / "CANONICAL.txt"
    if not canon.exists():
        return []

    content = canon.read_text(encoding="utf-8")
    # Extract individual variants
    header_re = re.compile(r"^## \w+ v\d{2}\s*$", re.MULTILINE)
    headers = list(header_re.finditer(content))

    examples = []
    for idx, match in enumerate(headers[:max_examples]):
        start = match.start()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(content)
        examples.append(content[start:end].strip())

    return examples


# ─── OUTPUT VALIDATION ─────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    valid: bool = True
    variant_count: int = 0
    word_counts: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_output(content: str, slot_type: str) -> ValidationResult:
    """Validate generated atom content before writing."""
    result = ValidationResult()

    header_re = re.compile(r"^## \w+ v(\d{2})\s*$", re.MULTILINE)
    headers = list(header_re.finditer(content))
    result.variant_count = len(headers)

    if not headers:
        result.valid = False
        result.errors.append("No variants found in output")
        return result

    word_limit = WORD_LIMITS.get(slot_type, 300)

    for idx, match in enumerate(headers):
        start = match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(content)
        block = content[start:end].strip()

        # Extract prose (after metadata separator if present)
        parts = block.split("---")
        prose = parts[-1].strip() if parts else block

        wc = len(prose.split())
        result.word_counts.append(wc)

        vnum = match.group(1)

        if wc > word_limit * 1.5:
            result.warnings.append(f"v{vnum}: {wc} words significantly exceeds {word_limit} limit")
        elif wc > word_limit:
            result.warnings.append(f"v{vnum}: {wc} words exceeds {word_limit} limit")

        if wc < 3:
            result.errors.append(f"v{vnum}: suspiciously short ({wc} words)")

        for pattern, label in FORBIDDEN_PATTERNS:
            if pattern.search(prose):
                result.warnings.append(f"v{vnum}: forbidden construction '{label}'")

    if result.errors:
        result.valid = False

    return result


# ─── FILE WRITER ───────────────────────────────────────────────────────────────

def write_canonical(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    content: str,
    output_dir: Path | None = None,
    is_engine: bool = False,
    engine_name: str | None = None,
) -> Path:
    """Write generated content to CANONICAL.txt format."""
    if output_dir is None:
        output_dir = REPO_ROOT / "atoms"

    if is_engine and engine_name:
        out_path = output_dir / persona_id / topic_id / engine_name / "CANONICAL.txt"
    else:
        out_path = output_dir / persona_id / topic_id / slot_type / "CANONICAL.txt"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Append to existing if present
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        # Find highest existing variant number
        header_re = re.compile(r"^## \w+ v(\d{2})\s*$", re.MULTILINE)
        existing_nums = [int(m.group(1)) for m in header_re.finditer(existing)]
        max_num = max(existing_nums) if existing_nums else 0

        # Renumber new variants
        new_content = content
        new_headers = list(header_re.finditer(new_content))
        offset = max_num
        for m in reversed(new_headers):
            old_num = int(m.group(1))
            new_num = old_num + offset
            new_content = (
                new_content[:m.start()]
                + f"## {slot_type} v{new_num:02d}"
                + new_content[m.end():]
            )

        combined = existing.rstrip() + "\n\n" + new_content.strip() + "\n"
        out_path.write_text(combined, encoding="utf-8")
    else:
        out_path.write_text(content.strip() + "\n", encoding="utf-8")

    return out_path


# ─── WRITE_ATOMS (compatibility shim for run_writing_campaign.py) ──────────

def write_atoms(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    num_variants: int = 6,
    model: str = "claude-sonnet-4-6",
    existing_examples: list[str] | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    dry_run: bool = False,
    is_engine: bool = False,
    engine_name: str | None = None,
) -> str:
    """
    Generate atom prompt and return it.

    NOTE: This function does NOT call any API. It returns a combined
    prompt string. When used from Claude Code, the caller should pass
    this prompt to an Agent subagent for generation.

    In dry_run mode, returns the prompt. In normal mode, raises an error
    directing the user to use Claude Code Agent tool.
    """
    system = build_system_prompt(slot_type if not is_engine else (engine_name or slot_type))
    user = build_user_prompt(
        persona_id=persona_id,
        topic_id=topic_id,
        slot_type=slot_type,
        num_variants=num_variants,
        existing_examples=existing_examples,
        is_engine=is_engine,
        engine_name=engine_name,
    )

    if dry_run:
        return f"=== SYSTEM PROMPT ===\n{system}\n\n=== USER PROMPT ===\n{user}"

    # When called programmatically, return the prompt for Agent tool usage
    return f"SYSTEM:\n{system}\n\nUSER:\n{user}"


# ─── CAMPAIGN PLAN GENERATOR ──────────────────────────────────────────────────

NEW_TOPICS = [
    "adhd_focus", "people_pleasing", "trauma_recovery",
    "emotional_regulation", "loneliness",
]


def generate_campaign_plan(output_path: Path | None = None) -> list[dict[str, Any]]:
    """
    Generate a campaign plan JSON that a Claude Code session can iterate over.

    Each plan item contains:
    - task_name: which campaign task this belongs to
    - persona, topic, slot_type (or teacher_id, engine)
    - system_prompt: the full system prompt
    - user_prompt: the full user prompt
    - output_path: where to write the result

    A Claude Code session reads this plan and for each item:
    1. Spawns an Agent subagent with the combined prompt
    2. Takes the output and writes it via write_canonical()
    3. Validates with validate_output()
    """
    plan: list[dict[str, Any]] = []

    # Task 1: PIVOT/TAKEAWAY/THREAD/PERMISSION for 4 personas x 15 topics
    key_personas = ["entrepreneurs", "first_responders", "healthcare_rns", "millennial_women_professionals"]
    for persona in key_personas:
        for topic in ALL_TOPICS:
            for slot in ["PIVOT", "TAKEAWAY", "THREAD", "PERMISSION"]:
                examples = load_existing_examples(persona, topic, slot)
                plan.append({
                    "task": "pivot_takeaway_thread_permission",
                    "persona": persona,
                    "topic": topic,
                    "slot_type": slot,
                    "variants": 13,
                    "system_prompt": build_system_prompt(slot),
                    "user_prompt": build_user_prompt(persona, topic, slot, 13, examples),
                    "output_path": f"atoms/{persona}/{topic}/{slot}/CANONICAL.txt",
                })

    # Task 2: 6 core slots for 5 new topics across 10 personas
    for persona in ALL_PERSONAS[:10]:
        for topic in NEW_TOPICS:
            for slot in ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]:
                plan.append({
                    "task": "new_topics",
                    "persona": persona,
                    "topic": topic,
                    "slot_type": slot,
                    "variants": 6,
                    "system_prompt": build_system_prompt(slot),
                    "user_prompt": build_user_prompt(persona, topic, slot, 6),
                    "output_path": f"atoms/{persona}/{topic}/{slot}/CANONICAL.txt",
                })

    # Task 3: Teacher stories handled separately (write_teacher_stories.py)

    # Task 4: EXERCISE/COMPRESSION gap fills
    gap_fills = [
        ("corporate_managers", "EXERCISE", 13),
        ("first_responders", "COMPRESSION", 13),
    ]
    for persona, slot, variants_per_topic in gap_fills:
        for topic in ALL_TOPICS:
            examples = load_existing_examples(persona, topic, slot)
            plan.append({
                "task": "exercise_compression_gap",
                "persona": persona,
                "topic": topic,
                "slot_type": slot,
                "variants": variants_per_topic,
                "system_prompt": build_system_prompt(slot),
                "user_prompt": build_user_prompt(persona, topic, slot, variants_per_topic, examples),
                "output_path": f"atoms/{persona}/{topic}/{slot}/CANONICAL.txt",
            })

    # Task 5: Engine atoms for new topics
    engines = ["watcher", "shame", "comparison", "false_alarm", "overwhelm", "grief", "spiral"]
    for persona in ALL_PERSONAS[:10]:
        for topic in NEW_TOPICS:
            for engine in engines:
                plan.append({
                    "task": "engine_atoms_new_topics",
                    "persona": persona,
                    "topic": topic,
                    "slot_type": engine,
                    "variants": 5,
                    "is_engine": True,
                    "engine_name": engine,
                    "system_prompt": build_system_prompt(engine),
                    "user_prompt": build_user_prompt(persona, topic, engine, 5, is_engine=True, engine_name=engine),
                    "output_path": f"atoms/{persona}/{topic}/{engine}/CANONICAL.txt",
                })

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        logger.info("Campaign plan written to %s (%d items)", output_path, len(plan))

    return plan


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Phoenix Omega Atom Writer (prompt builder + file writer)",
    )
    sub = parser.add_subparsers(dest="command")

    # Plan command
    plan_cmd = sub.add_parser("plan", help="Generate campaign plan JSON")
    plan_cmd.add_argument(
        "--output", type=Path,
        default=REPO_ROOT / "artifacts" / "atom_writing" / "campaign_plan.json",
    )

    # Prompt command
    prompt_cmd = sub.add_parser("prompt", help="Generate prompt for a single batch")
    prompt_cmd.add_argument("--persona", required=True)
    prompt_cmd.add_argument("--topic", required=True)
    prompt_cmd.add_argument("--slot", required=True)
    prompt_cmd.add_argument("--variants", type=int, default=6)
    prompt_cmd.add_argument("--engine", action="store_true")

    # Parse command
    parse_cmd = sub.add_parser("parse", help="Parse generated output and write to disk")
    parse_cmd.add_argument("--input", type=Path, required=True)
    parse_cmd.add_argument("--persona", required=True)
    parse_cmd.add_argument("--topic", required=True)
    parse_cmd.add_argument("--slot", required=True)
    parse_cmd.add_argument("--engine", action="store_true")
    parse_cmd.add_argument("--output-dir", type=Path, default=None)

    args = parser.parse_args()

    if args.command == "plan":
        plan = generate_campaign_plan(args.output)
        print(f"Generated campaign plan: {len(plan)} items")
        # Summary
        tasks = {}
        for item in plan:
            t = item["task"]
            tasks[t] = tasks.get(t, 0) + 1
        for t, count in tasks.items():
            print(f"  {t}: {count} items")

    elif args.command == "prompt":
        examples = load_existing_examples(args.persona, args.topic, args.slot)
        system = build_system_prompt(args.slot)
        user = build_user_prompt(
            args.persona, args.topic, args.slot, args.variants, examples,
            is_engine=args.engine, engine_name=args.slot if args.engine else None,
        )
        print("=== SYSTEM PROMPT ===")
        print(system)
        print("\n=== USER PROMPT ===")
        print(user)

    elif args.command == "parse":
        content = args.input.read_text(encoding="utf-8")
        result = validate_output(content, args.slot)
        print(f"Variants found: {result.variant_count}")
        print(f"Valid: {result.valid}")
        if result.warnings:
            for w in result.warnings:
                print(f"  WARNING: {w}")
        if result.errors:
            for e in result.errors:
                print(f"  ERROR: {e}")

        if result.valid or not result.errors:
            path = write_canonical(
                args.persona, args.topic, args.slot, content,
                output_dir=args.output_dir,
                is_engine=args.engine,
                engine_name=args.slot if args.engine else None,
            )
            print(f"Written to: {path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

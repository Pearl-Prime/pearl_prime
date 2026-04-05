#!/usr/bin/env python3
"""
Teacher STORY Atom Writer — write_teacher_stories.py

Reads teacher doctrine + existing approved atoms + KB and generates new STORY atoms
matching the teacher's voice, tradition, and doctrine.

Usage:
  # Single teacher
  python scripts/atom_writing/write_teacher_stories.py --teacher junko --count 5

  # Multiple teachers
  python scripts/atom_writing/write_teacher_stories.py \
    --teacher junko --teacher maat --teacher miki --count 10

  # All teachers
  python scripts/atom_writing/write_teacher_stories.py --all --target 20

  # Dry run
  python scripts/atom_writing/write_teacher_stories.py --teacher junko --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

try:
    import yaml
except ImportError:
    # Fallback: minimal YAML loader for simple key-value files
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("teacher_writer")

# ─── CONSTANTS ──────────────────────────────────────────────────────────────

TEACHER_BANK_DIR = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

ALL_TEACHERS = [
    "junko", "maat", "miki", "master_sha", "master_wu",
    "joshin", "master_feung", "omote", "pamela_fellows", "ra", "sai_ma",
]


# ─── TEACHER SYSTEM PROMPT ──────────────────────────────────────────────────

TEACHER_STORY_SYSTEM_PROMPT = """You are a professional prose writer for Phoenix Omega, a TTS audiobook system.
You are writing STORY atoms in the voice of a specific spiritual teacher.
Your prose will be read by a flat synthetic voice (Google Play auto-narration).

## ABSOLUTE RULES (no exceptions)

1. NO RHETORICAL QUESTIONS. Zero "?" marks.
2. NO TENTATIVE LANGUAGE. Forbidden: perhaps, you might, it's possible, maybe, could be.
3. ACTIVE VERBS ONLY. No "was feeling", "was sitting", "was thinking".
4. BODY ANCHORS REQUIRED. Every emotional moment grounded in concrete body state.
5. NEVER USE "WE".
6. Max 15 words per emotional beat. One action per sentence.

## STORY ATOM RULES

- Named character. Specific moment. Third-person present tense. Never past. Never first-person.
- Use dialogue when possible. Write silence as held moments.
- Include visible consequences for every action.
- No emotion labels ("felt anxious"). Show through body, action, consequence.

## TEACHER MODE

Each story must:
- Reflect the teacher's tradition, methods, and core principles
- Use the teacher's tone profile (spare/warm/direct/etc.)
- Respect the teacher's forbidden claims and tone boundaries
- Reference the teacher's glossary terms naturally (not forced)
- Show the teacher's methodology through the character's experience

## OUTPUT FORMAT

For each story, output this YAML format:

```yaml
atom_id: {teacher_id}_STORY_{number:03d}
story_origin: composite
story_type: character_study
emotional_intensity_band: {1-5}
body: |
  {Story prose here. Multiple paragraphs. Third-person present tense.}
band: {1-5}
teacher:
  teacher_id: {teacher_id}
  source_refs: []
  synthesis_method: authored_v2
never_know: {true/false}
misfire_tax: {true/false}
mechanism_depth: {1-5}
identity_stage: {pre_awareness/destabilization/self_claim/integration}
cost_type: {social/internal/identity/relational}
cost_intensity: {1-5}
```

Separate each atom with a line containing only `---`.
Vary emotional_intensity_band across stories (at least 3 different bands).
Vary identity_stage and cost_type across stories.
"""


# ─── DOCTRINE LOADER ────────────────────────────────────────────────────────

def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file with fallback for missing PyYAML."""
    content = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(content) or {}
    # Minimal fallback: parse simple key-value YAML
    result: dict[str, Any] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def load_teacher_doctrine(teacher_id: str) -> dict[str, Any]:
    """Load teacher doctrine from YAML."""
    doctrine_path = TEACHER_BANK_DIR / teacher_id / "doctrine" / "doctrine.yaml"
    if not doctrine_path.exists():
        raise FileNotFoundError(f"Doctrine not found: {doctrine_path}")
    return load_yaml_file(doctrine_path)


def load_existing_stories(teacher_id: str) -> list[str]:
    """Load existing approved STORY atoms as examples."""
    story_dir = TEACHER_BANK_DIR / teacher_id / "approved_atoms" / "STORY"
    if not story_dir.exists():
        return []

    examples = []
    for yaml_file in sorted(story_dir.glob("*.yaml")):
        content = yaml_file.read_text(encoding="utf-8")
        examples.append(content)

    return examples


def load_teacher_kb(teacher_id: str) -> str | None:
    """Load teacher knowledge base index if it exists."""
    kb_path = TEACHER_BANK_DIR / teacher_id / "kb" / "index.json"
    if not kb_path.exists():
        return None
    try:
        data = json.loads(kb_path.read_text(encoding="utf-8"))
        # Return a summary of available KB entries
        if isinstance(data, list):
            return f"KB contains {len(data)} entries."
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)[:2000]
    except (json.JSONDecodeError, OSError):
        return None
    return None


def count_existing_stories(teacher_id: str) -> int:
    """Count existing approved STORY atoms for a teacher."""
    story_dir = TEACHER_BANK_DIR / teacher_id / "approved_atoms" / "STORY"
    if not story_dir.exists():
        return 0
    return len(list(story_dir.glob("*.yaml")))


# ─── CORE WRITER ────────────────────────────────────────────────────────────

def build_teacher_prompt(
    teacher_id: str,
    doctrine: dict[str, Any],
    existing_examples: list[str],
    num_stories: int,
    start_index: int = 0,
    kb_summary: str | None = None,
) -> str:
    """Build user prompt for teacher story generation."""
    parts = [
        f"Write {num_stories} new STORY atoms for teacher: {doctrine.get('display_name', teacher_id)}",
        f"Teacher ID: {teacher_id}",
        "",
        "## TEACHER DOCTRINE",
        f"Tradition: {doctrine.get('tradition', 'not specified')}",
        f"Primary methods: {doctrine.get('primary_methods', 'not specified')}",
        f"Core principles: {doctrine.get('core_principles', 'not specified')}",
        f"Tone profile: {doctrine.get('tone_profile', 'not specified')}",
        "",
    ]

    # Forbidden claims
    forbidden = doctrine.get("forbidden_claims", [])
    if forbidden:
        parts.append("FORBIDDEN CLAIMS (never include):")
        for claim in forbidden:
            parts.append(f"  - {claim}")
        parts.append("")

    # Tone boundaries
    boundaries = doctrine.get("tone_boundaries", [])
    if boundaries:
        parts.append("TONE BOUNDARIES:")
        for b in boundaries:
            parts.append(f"  - {b}")
        parts.append("")

    # Glossary
    glossary = doctrine.get("glossary", [])
    if glossary:
        parts.append("GLOSSARY (use naturally, do not force):")
        for term in glossary:
            parts.append(f"  - {term}")
        parts.append("")

    # KB summary
    if kb_summary:
        parts.append("KNOWLEDGE BASE CONTEXT:")
        parts.append(kb_summary)
        parts.append("")

    # Existing examples
    if existing_examples:
        parts.append(f"EXISTING APPROVED STORIES ({len(existing_examples)} total). Match this quality.")
        parts.append("Here are up to 3 examples:")
        parts.append("---BEGIN EXAMPLES---")
        for ex in existing_examples[:3]:
            parts.append(ex.strip())
            parts.append("---")
        parts.append("---END EXAMPLES---")
        parts.append("")

    parts.extend([
        f"Start atom numbering at: {teacher_id}_STORY_{start_index:03d}",
        f"Generate exactly {num_stories} new stories.",
        "Each story must feature a different named character.",
        "Vary emotional_intensity_band (use at least 3 different bands).",
        "Vary identity_stage across stories.",
        "Show the teacher's tradition through character experience, not exposition.",
    ])

    return "\n".join(parts)


def write_teacher_stories(
    teacher_id: str,
    num_stories: int = 5,
    model: str = "claude-sonnet-4-6",
    temperature: float = 0.7,
    max_tokens: int = 8192,
    dry_run: bool = False,
) -> str:
    """
    Generate new STORY atoms matching teacher's voice, tradition, and doctrine.

    Loads:
    - SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/doctrine/doctrine.yaml
    - SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/approved_atoms/STORY/*.yaml
    - SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/kb/index.json

    Returns generated content as string.
    """
    # Load doctrine
    doctrine = load_teacher_doctrine(teacher_id)
    logger.info("Loaded doctrine for %s: %s", teacher_id, doctrine.get("display_name", teacher_id))

    # Load existing examples
    existing = load_existing_stories(teacher_id)
    existing_count = len(existing)
    logger.info("Found %d existing approved stories for %s", existing_count, teacher_id)

    # Load KB
    kb_summary = load_teacher_kb(teacher_id)

    # Build prompt
    user_prompt = build_teacher_prompt(
        teacher_id=teacher_id,
        doctrine=doctrine,
        existing_examples=existing,
        num_stories=num_stories,
        start_index=existing_count,
        kb_summary=kb_summary,
    )

    if dry_run:
        logger.info("DRY RUN — not calling API")
        print("=== SYSTEM PROMPT ===")
        print(TEACHER_STORY_SYSTEM_PROMPT[:500] + "...")
        print("\n=== USER PROMPT ===")
        print(user_prompt)
        return ""

    client = anthropic.Anthropic()

    logger.info(
        "Calling %s for teacher %s (%d stories)",
        model, teacher_id, num_stories,
    )
    t0 = time.monotonic()

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=TEACHER_STORY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    elapsed = time.monotonic() - t0
    content = message.content[0].text
    logger.info(
        "Response received in %.1fs (%d chars, stop=%s)",
        elapsed, len(content), message.stop_reason,
    )

    return content


def write_teacher_yaml_files(
    teacher_id: str,
    content: str,
    output_dir: Path | None = None,
) -> list[Path]:
    """
    Parse generated content and write individual YAML files.
    Returns list of written file paths.
    """
    if output_dir is None:
        output_dir = TEACHER_BANK_DIR / teacher_id / "approved_atoms" / "STORY"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Split on --- delimiter between atoms
    blocks = content.split("\n---\n")
    written: list[Path] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Extract atom_id from content
        atom_id = None
        for line in block.splitlines():
            if line.strip().startswith("atom_id:"):
                atom_id = line.split(":", 1)[1].strip()
                break

        if not atom_id:
            logger.warning("Could not extract atom_id from block, skipping")
            continue

        file_path = output_dir / f"{atom_id}.yaml"
        file_path.write_text(block, encoding="utf-8")
        written.append(file_path)
        logger.info("Wrote %s", file_path)

    return written


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate teacher STORY atoms using Claude Sonnet 4.6",
    )
    parser.add_argument("--teacher", action="append", help="Teacher ID(s)")
    parser.add_argument("--all", action="store_true", help="Process all teachers")
    parser.add_argument("--count", type=int, default=5, help="Stories to generate per teacher")
    parser.add_argument("--target", type=int, default=None, help="Target total stories (write enough to reach this)")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)

    args = parser.parse_args()

    teachers = ALL_TEACHERS if args.all else (args.teacher or [])
    if not teachers:
        parser.error("Specify --teacher or --all")

    results: dict[str, Any] = {}

    for teacher_id in teachers:
        logger.info("=== Processing teacher: %s ===", teacher_id)

        # Determine how many to write
        if args.target:
            existing = count_existing_stories(teacher_id)
            needed = max(0, args.target - existing)
            if needed == 0:
                logger.info("Teacher %s already has %d stories (target=%d), skipping",
                            teacher_id, existing, args.target)
                results[teacher_id] = {"status": "skipped", "existing": existing}
                continue
            num_stories = needed
        else:
            num_stories = args.count

        content = write_teacher_stories(
            teacher_id=teacher_id,
            num_stories=num_stories,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            results[teacher_id] = {"status": "dry_run"}
            continue

        # Write files
        written = write_teacher_yaml_files(
            teacher_id=teacher_id,
            content=content,
            output_dir=args.output_dir,
        )

        results[teacher_id] = {
            "status": "ok",
            "stories_written": len(written),
            "files": [str(p) for p in written],
        }

    # Summary
    print("\n=== TEACHER STORY GENERATION SUMMARY ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

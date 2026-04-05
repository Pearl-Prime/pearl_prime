#!/usr/bin/env python3
"""
Atom Writer — write_atoms_claude.py

Core atom writer using Anthropic Claude Sonnet 4.6 API.
Generates CANONICAL.txt content for any persona x topic x slot_type combination.

Usage:
  # Single slot
  python scripts/atom_writing/write_atoms_claude.py \
    --persona corporate_managers --topic anxiety --slot HOOK --variants 6

  # With few-shot examples from existing atoms
  python scripts/atom_writing/write_atoms_claude.py \
    --persona educators --topic burnout --slot STORY --variants 8

  # Dry run (print prompt, don't call API)
  python scripts/atom_writing/write_atoms_claude.py \
    --persona entrepreneurs --topic grief --slot REFLECTION --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("atom_writer")

# ─── CONSTANTS ──────────────────────────────────────────────────────────────

ALL_PERSONAS = [
    "corporate_managers", "educators", "entrepreneurs", "first_responders",
    "gen_alpha_students", "gen_x_sandwich", "gen_z_professionals",
    "healthcare_rns", "millennial_women_professionals", "nyc_executives",
    "tech_finance_burnout", "working_parents",
]

ALL_TOPICS = [
    "anxiety", "boundaries", "burnout", "compassion_fatigue", "courage",
    "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "overthinking", "self_worth", "sleep_anxiety",
    "social_anxiety", "somatic_healing",
]

SLOT_TYPES = [
    "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
    "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "COMPRESSION",
]

ENGINE_DIRS = [
    "watcher", "shame", "comparison", "false_alarm",
    "overwhelm", "grief", "spiral",
]

# Metadata fields required per slot type
METADATA_FIELDS: dict[str, list[str]] = {
    "STORY": ["MECHANISM_DEPTH", "IDENTITY_STAGE", "COST_TYPE", "COST_INTENSITY"],
    "REFLECTION": ["family", "voice_mode", "mechanism_emphasis"],
    "INTEGRATION": ["integration_mode", "reframe_type"],
}

# Word count limits per atom type (max per variant)
WORD_LIMITS: dict[str, int] = {
    "HOOK": 60,
    "SCENE": 80,
    "STORY": 300,
    "REFLECTION": 220,   # Tier S ceiling
    "EXERCISE": 80,
    "INTEGRATION": 250,
    "PIVOT": 40,
    "TAKEAWAY": 60,
    "THREAD": 60,
    "PERMISSION": 60,
    "COMPRESSION": 120,
}

# Sentence word caps per function
SENTENCE_CAPS: dict[str, int] = {
    "emotional_beat": 15,
    "teaching": 12,
    "instruction": 10,
    "carry_line": 8,
}

# Variant regex: matches ## TYPE v01 through ## TYPE v99
VARIANT_RE = re.compile(
    r"^## (\w+) v(\d{2})\s*\n---\n(.*?)\n---\n(.*?)\n---$",
    re.MULTILINE | re.DOTALL,
)

# Forbidden constructions
FORBIDDEN_PATTERNS = [
    (re.compile(r"\?"), "rhetorical_question"),
    (re.compile(r"\bperhaps\b", re.I), "tentative_perhaps"),
    (re.compile(r"\byou might\b", re.I), "tentative_you_might"),
    (re.compile(r"\bit'?s possible\b", re.I), "tentative_its_possible"),
    (re.compile(r"\bmaybe\b", re.I), "tentative_maybe"),
    (re.compile(r"\bcould be\b", re.I), "tentative_could_be"),
    (re.compile(r"\bmight be\b", re.I), "tentative_might_be"),
    (re.compile(r"\byou may want to\b", re.I), "tentative_you_may"),
    (re.compile(r"\bconsider trying\b", re.I), "tentative_consider"),
    (re.compile(r"\bsometimes it helps to\b", re.I), "tentative_sometimes"),
    (re.compile(r"\bdo whatever feels right\b", re.I), "tentative_whatever"),
    (re.compile(r"\bwe\b", re.I), "forbidden_we"),
    (re.compile(r"\bwas feeling\b", re.I), "passive_was_feeling"),
    (re.compile(r"\bwas sitting\b", re.I), "passive_was_sitting"),
    (re.compile(r"\bwas thinking\b", re.I), "passive_was_thinking"),
    (re.compile(r"\bwere looking\b", re.I), "passive_were_looking"),
    (re.compile(r"\bhad been\b", re.I), "passive_had_been"),
]


# ─── SYSTEM PROMPT ──────────────────────────────────────────────────────────

WRITER_SYSTEM_PROMPT = """You are a professional prose writer for Phoenix Omega, a TTS audiobook system.
Your prose will be read by a flat synthetic voice (Google Play auto-narration) at 150 words per minute.
100% of the emotional weight comes from how you write. The robot contributes nothing.

## ABSOLUTE RULES (no exceptions)

1. NO RHETORICAL QUESTIONS. Zero "?" marks. Convert every question to a direct statement.
2. NO TENTATIVE LANGUAGE. Forbidden: perhaps, you might, it's possible, maybe, could be, might be, you may want to, consider trying, sometimes it helps to, do whatever feels right.
3. ACTIVE VERBS ONLY. No "was feeling", "was sitting", "was thinking", "were looking", "had been".
4. BODY ANCHORS REQUIRED. Every emotional moment grounded in concrete body state or sensory detail.
5. NEVER USE "WE". The author observes, names, and respects. "We" implies shared experience the author cannot guarantee.
6. SENTENCE LENGTH CAPS:
   - Emotional beats: max 15 words
   - Teaching sentences: max 12 words
   - Instructions (EXERCISE): max 10 words
   - Integration carry lines: max 8 words
7. SENTENCE RHYTHM VARIANCE. Within any 10 consecutive sentences, range between shortest and longest must be at least 12 words. Include at least one sentence of 3 words or fewer.
8. PARAGRAPH BREAKS AS BREATH. In REFLECTION: paragraph break every 60-80 words. In STORY: tight paragraphs for tension, spacious for processing.

## VOICE

The author. Not a guru. Not a therapist. Not a friend. Authority comes from precision, not credentials.

| Type | Person / Tense |
|------|---------------|
| HOOK | First-person author or second-person direct |
| SCENE | Second-person present always |
| STORY | Third-person present. Never past tense. Never first-person. |
| REFLECTION | First-person author to second-person listener |
| EXERCISE | Second-person imperative |
| INTEGRATION | First-person author. Quiet. Concrete. |
| PIVOT | Second-person direct. One reframe per variant. |
| TAKEAWAY | Second-person. One key insight distilled. |
| THREAD | Second-person. Connects current moment to larger pattern. |
| PERMISSION | Second-person. Grants permission the listener cannot give themselves. |
| COMPRESSION | Second-person imperative. Micro-dose exercise. |

## ATOM TYPE SPECIFICATIONS

### HOOK (grab)
- Max 3 sentences (short-format). First line max 12 words. Body anchor included.
- Job: make the listener think "this is about me" as fast as possible.

### SCENE (ground)
- Second-person, present tense, always. One sensory detail per sentence. Max 10 words per sensory beat.
- SCENE illustrates; it does not teach. No insight, no explanation.
- End with action or sensory moment, not with insight.
- Location tokens allowed: {street_name}, {transit_line}, {weather_detail}

### STORY (show)
- Named character. Specific moment. Third-person present tense.
- Use dialogue. One action per sentence. Max 15 words per emotional beat.
- Write silence as held moments. Include visible consequences.
- REQUIRED METADATA: MECHANISM_DEPTH (1-3), IDENTITY_STAGE (pre_awareness/destabilization/integration), COST_TYPE (social/internal/relational), COST_INTENSITY (1-5)
- No emotion labels ("felt anxious"). Show, don't tell.

### REFLECTION (teach)
- Mechanism explanation. Statement-based teaching only.
- Tier S max: 220 words. Post-impact: 180 words.
- Max 12 words per teaching sentence. Max 2 mechanism terms per reflection.
- Chunk every 60-80 words with paragraph break.
- Include 1 reflective beat (directs listener to their own experience) in first third.
- REQUIRED METADATA: family (F1-F6), voice_mode (teacher), mechanism_emphasis (automatic/structural)

### EXERCISE (guide)
- Imperatives only. One instruction per sentence. Max 10 words per instruction.
- No options. No "you might." Body-based. Explicit timing ("Count to four" not "about four seconds").

### INTEGRATION (landing)
- First-person author. Quiet. Concrete. Body-landed.
- Includes a carry_line (max 8 words, bold standalone).
- REQUIRED METADATA: integration_mode (BODY-LANDED/MIND-SHIFT/PRACTICAL-GROUNDED/INTEGRATED-ACTION), reframe_type

### PIVOT (reframe)
- One sentence. One reframe. Max 40 words. Second-person direct.

### TAKEAWAY (distill)
- 1-3 sentences. Key insight. Max 60 words. Second-person.

### THREAD (connect)
- 1-3 sentences. Connects moment to larger pattern. Max 60 words.

### PERMISSION (grant)
- 1-3 sentences. Grants permission listener can't give themselves. Max 60 words.

### COMPRESSION (micro-exercise)
- Micro-dose exercise. 2-5 sentences. Max 120 words. Second-person imperative.

## OUTPUT FORMAT

For each variant, output EXACTLY this format:

```
## TYPE v01
---
METADATA_KEY: value
ANOTHER_KEY: value
---
Prose content here. Multiple sentences. Paragraph breaks as needed.

Second paragraph if needed.
---
```

- Variant numbers: v01, v02, v03... (zero-padded two digits)
- Metadata block between first and second `---` lines (empty if no metadata required)
- Prose content between second and third `---` lines
- Each variant separated by a blank line

For STORY atoms, always include: MECHANISM_DEPTH, IDENTITY_STAGE, COST_TYPE, COST_INTENSITY
For REFLECTION atoms, always include: family, voice_mode, mechanism_emphasis
For INTEGRATION atoms, always include: integration_mode, reframe_type

For all other types, the metadata block is empty (just two --- lines with nothing between).
"""


# ─── PERSONA CONTEXT ────────────────────────────────────────────────────────

PERSONA_CONTEXT: dict[str, str] = {
    "corporate_managers": "Mid-level corporate managers. Hierarchy anxiety, reorg fear, performance review cycles, managing up and down, skip-level meetings, team uncertainty.",
    "educators": "Teachers and school staff. Compassion fatigue, student crises, admin pressure, underpay, emotional labor, classroom dynamics.",
    "entrepreneurs": "Founders and solo operators. Financial uncertainty, identity-business fusion, loneliness, pitch anxiety, cash flow fear, imposter syndrome.",
    "first_responders": "Police, fire, EMS, dispatchers. Trauma exposure, hypervigilance, compartmentalization, re-entry to civilian life, sleep disruption.",
    "gen_alpha_students": "Students born 2010+. Digital native anxiety, social media comparison, academic pressure, identity formation, parental expectations.",
    "gen_x_sandwich": "Gen X adults caring for aging parents and children simultaneously. Role exhaustion, financial squeeze, invisible labor, identity erosion.",
    "gen_z_professionals": "Early-career professionals born 1997-2012. First job anxiety, hustle culture, burnout, student debt, remote work isolation.",
    "healthcare_rns": "Registered nurses. Shift work, moral injury, patient loss, staffing crises, compassion fatigue, physical exhaustion.",
    "millennial_women_professionals": "Millennial women in professional roles. Glass ceiling, motherhood penalty, people-pleasing, perfectionism, work-life integration.",
    "nyc_executives": "Senior executives in high-pressure urban environments. Status anxiety, isolation at the top, decision fatigue, public persona management.",
    "tech_finance_burnout": "Tech and finance professionals. Always-on culture, performance metrics, golden handcuffs, burnout cycles, competence addiction.",
    "working_parents": "Parents balancing careers and childcare. Time poverty, guilt, logistics overload, identity splitting, exhaustion.",
}


# ─── CORE WRITER ────────────────────────────────────────────────────────────

def build_user_prompt(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    num_variants: int,
    existing_examples: list[str] | None = None,
    metadata_template: dict | None = None,
) -> str:
    """Build the user prompt for atom generation."""
    persona_desc = PERSONA_CONTEXT.get(persona_id, f"Persona: {persona_id}")
    word_limit = WORD_LIMITS.get(slot_type, 200)

    parts = [
        f"Write {num_variants} {slot_type} atom variants for:",
        f"  Persona: {persona_id} — {persona_desc}",
        f"  Topic: {topic_id}",
        f"  Slot type: {slot_type}",
        f"  Max words per variant: {word_limit}",
        "",
    ]

    # Metadata instructions
    if slot_type in METADATA_FIELDS:
        fields = METADATA_FIELDS[slot_type]
        parts.append(f"REQUIRED METADATA for each variant: {', '.join(fields)}")
        if slot_type == "STORY":
            parts.extend([
                "  MECHANISM_DEPTH: 1 (surface), 2 (pattern), 3 (root)",
                "  IDENTITY_STAGE: pre_awareness, destabilization, or integration",
                "  COST_TYPE: social, internal, or relational",
                "  COST_INTENSITY: 1-5 (1=mild, 5=crisis)",
                "  Vary these across variants. Include at least 3 different bands.",
            ])
        elif slot_type == "REFLECTION":
            parts.extend([
                "  family: F1 through F6 (vary across variants)",
                "  voice_mode: teacher",
                "  mechanism_emphasis: automatic or structural (alternate)",
            ])
        elif slot_type == "INTEGRATION":
            parts.extend([
                "  integration_mode: BODY-LANDED, MIND-SHIFT, PRACTICAL-GROUNDED, or INTEGRATED-ACTION",
                "  reframe_type: BODY-FACT, ACCEPTANCE-THROUGH-ACTION, RESOURCE-SHIFT, NORMALCY-REDEFINED, SEPARATION, RHYTHM-RESTORATION, or PRODUCTIVE-ANXIETY",
                "  Include a carry_line (max 8 words, bold standalone sentence).",
            ])
        parts.append("")

    if metadata_template:
        parts.append("Metadata template for reference:")
        for k, v in metadata_template.items():
            parts.append(f"  {k}: {v}")
        parts.append("")

    # Few-shot examples
    if existing_examples:
        parts.append("EXISTING EXAMPLES (match this quality and format, but create NEW content):")
        parts.append("---BEGIN EXAMPLES---")
        for ex in existing_examples[:3]:  # limit to 3 examples
            parts.append(ex.strip())
            parts.append("")
        parts.append("---END EXAMPLES---")
        parts.append("")

    parts.extend([
        f"Output exactly {num_variants} variants numbered v01 through v{num_variants:02d}.",
        "Use the exact output format specified in your instructions.",
        "Each variant must be unique — different character names, different moments, different body anchors.",
        "Do NOT repeat syntactic patterns across variants.",
    ])

    return "\n".join(parts)


def write_atoms(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    num_variants: int = 6,
    model: str = "claude-sonnet-4-6",
    existing_examples: list[str] | None = None,
    metadata_template: dict | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    dry_run: bool = False,
) -> str:
    """
    Generates CANONICAL.txt content for one persona x topic x slot_type.
    Returns the full text content ready to write to disk.

    Uses Anthropic Python SDK:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    """
    user_prompt = build_user_prompt(
        persona_id=persona_id,
        topic_id=topic_id,
        slot_type=slot_type,
        num_variants=num_variants,
        existing_examples=existing_examples,
        metadata_template=metadata_template,
    )

    if dry_run:
        logger.info("DRY RUN — not calling API")
        print("=== SYSTEM PROMPT ===")
        print(WRITER_SYSTEM_PROMPT[:500] + "...")
        print("\n=== USER PROMPT ===")
        print(user_prompt)
        return ""

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    logger.info(
        "Calling %s for %s/%s/%s (%d variants)",
        model, persona_id, topic_id, slot_type, num_variants,
    )
    t0 = time.monotonic()

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=WRITER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    elapsed = time.monotonic() - t0
    content = message.content[0].text
    logger.info(
        "Response received in %.1fs (%d chars, stop=%s)",
        elapsed, len(content), message.stop_reason,
    )

    return content


# ─── VALIDATION ─────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    variant_count: int = 0
    word_counts: list[int] = field(default_factory=list)
    content: str = ""

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "variant_count": self.variant_count,
            "word_counts": self.word_counts,
        }


def validate_output(content: str, slot_type: str) -> ValidationResult:
    """
    Validate generated atom content against spec rules.
    Returns ValidationResult with errors, warnings, and word counts.
    """
    result = ValidationResult(valid=True, content=content)

    if not content.strip():
        result.valid = False
        result.errors.append("Empty content")
        return result

    # Parse variants
    variants = parse_variants(content, slot_type)
    result.variant_count = len(variants)

    if not variants:
        result.valid = False
        result.errors.append("No valid variants found. Expected ## TYPE vNN / --- / metadata / --- / prose / --- pattern.")
        return result

    word_limit = WORD_LIMITS.get(slot_type, 200)

    for i, (vnum, metadata_str, prose) in enumerate(variants):
        # Word count check
        wc = len(prose.split())
        result.word_counts.append(wc)

        if wc > word_limit:
            result.errors.append(
                f"v{vnum}: {wc} words exceeds {slot_type} limit of {word_limit}"
            )

        if wc < 5:
            result.errors.append(f"v{vnum}: suspiciously short ({wc} words)")

        # Metadata check
        if slot_type in METADATA_FIELDS:
            required = METADATA_FIELDS[slot_type]
            for field_name in required:
                if field_name.lower() not in metadata_str.lower():
                    result.errors.append(
                        f"v{vnum}: missing required metadata field '{field_name}'"
                    )

        # Forbidden construction check
        for pattern, label in FORBIDDEN_PATTERNS:
            matches = pattern.findall(prose)
            if matches:
                # Allow "?" only in EXERCISE timing context
                if label == "rhetorical_question":
                    result.errors.append(
                        f"v{vnum}: contains question mark(s) — forbidden ({label})"
                    )
                elif label == "forbidden_we":
                    # Check if it's standalone "we" (not part of other words)
                    standalone = re.findall(r"\bwe\b", prose, re.I)
                    if standalone:
                        result.warnings.append(
                            f"v{vnum}: contains 'we' — forbidden per spec ({len(standalone)}x)"
                        )
                else:
                    result.errors.append(
                        f"v{vnum}: forbidden construction '{label}' found"
                    )

    # Set validity
    if result.errors:
        result.valid = False

    return result


def parse_variants(content: str, slot_type: str) -> list[tuple[str, str, str]]:
    """
    Parse CANONICAL.txt format into list of (variant_number, metadata_str, prose).
    Handles the ## TYPE vNN / --- / metadata / --- / prose / --- format.
    """
    variants = []

    # Split on variant headers
    header_re = re.compile(r"^## \w+ v(\d{2})\s*$", re.MULTILINE)
    headers = list(header_re.finditer(content))

    for idx, match in enumerate(headers):
        vnum = match.group(1)
        start = match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(content)

        block = content[start:end].strip()

        # Split on --- delimiters
        parts = block.split("---")
        # Expected: empty, metadata, prose, (trailing)
        # Filter out empty parts at boundaries
        parts = [p for p in parts if p is not None]

        if len(parts) >= 3:
            metadata_str = parts[1].strip()
            prose = parts[2].strip()
            variants.append((vnum, metadata_str, prose))
        elif len(parts) == 2:
            # metadata might be empty
            metadata_str = parts[0].strip() if parts[0].strip() else ""
            prose = parts[1].strip()
            variants.append((vnum, metadata_str, prose))

    return variants


# ─── FILE I/O ───────────────────────────────────────────────────────────────

def load_existing_examples(persona_id: str, topic_id: str, slot_type: str, max_examples: int = 3) -> list[str]:
    """Load existing CANONICAL.txt content as few-shot examples."""
    canon_path = REPO_ROOT / "atoms" / persona_id / topic_id / slot_type / "CANONICAL.txt"
    if not canon_path.exists():
        return []

    content = canon_path.read_text(encoding="utf-8")
    if not content.strip():
        return []

    # Parse into individual variants and return first N
    variants = parse_variants(content, slot_type)
    examples = []
    for vnum, meta, prose in variants[:max_examples]:
        block = f"## {slot_type} v{vnum}\n---\n{meta}\n---\n{prose}\n---"
        examples.append(block)

    return examples


def write_canonical(
    persona_id: str,
    topic_id: str,
    slot_type: str,
    content: str,
    output_dir: Path | None = None,
    is_engine: bool = False,
    engine_name: str | None = None,
) -> Path:
    """Write content to the correct CANONICAL.txt path."""
    if output_dir is None:
        output_dir = REPO_ROOT / "atoms"

    if is_engine and engine_name:
        path = output_dir / persona_id / topic_id / engine_name / "CANONICAL.txt"
    else:
        path = output_dir / persona_id / topic_id / slot_type / "CANONICAL.txt"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logger.info("Wrote %s (%d bytes)", path, len(content))
    return path


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate atom content using Claude Sonnet 4.6",
    )
    parser.add_argument("--persona", required=True, help="Persona ID (e.g. corporate_managers)")
    parser.add_argument("--topic", required=True, help="Topic ID (e.g. anxiety)")
    parser.add_argument("--slot", required=True, help="Slot type (e.g. HOOK, STORY)")
    parser.add_argument("--variants", type=int, default=6, help="Number of variants (default: 6)")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Model ID")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling API")
    parser.add_argument("--no-examples", action="store_true", help="Skip loading existing examples")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing file only")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override output directory")
    parser.add_argument("--engine", default=None, help="Engine name for engine atoms (e.g. watcher)")

    args = parser.parse_args()

    # Validate-only mode
    if args.validate_only:
        canon_path = REPO_ROOT / "atoms" / args.persona / args.topic / args.slot / "CANONICAL.txt"
        if not canon_path.exists():
            print(f"File not found: {canon_path}")
            sys.exit(1)
        content = canon_path.read_text(encoding="utf-8")
        result = validate_output(content, args.slot)
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(0 if result.valid else 1)

    # Load few-shot examples
    examples = None
    if not args.no_examples:
        examples = load_existing_examples(args.persona, args.topic, args.slot)
        if examples:
            logger.info("Loaded %d existing examples as few-shot", len(examples))

    # Generate
    content = write_atoms(
        persona_id=args.persona,
        topic_id=args.topic,
        slot_type=args.slot,
        num_variants=args.variants,
        model=args.model,
        existing_examples=examples,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        return

    # Validate
    result = validate_output(content, args.slot)
    if result.errors:
        logger.warning("Validation errors found:")
        for err in result.errors:
            logger.warning("  %s", err)
    if result.warnings:
        for w in result.warnings:
            logger.warning("  WARN: %s", w)

    logger.info(
        "Generated %d variants, word counts: %s, valid: %s",
        result.variant_count, result.word_counts, result.valid,
    )

    # Write to disk
    is_engine = args.engine is not None
    out_path = write_canonical(
        persona_id=args.persona,
        topic_id=args.topic,
        slot_type=args.slot,
        content=content,
        output_dir=args.output_dir,
        is_engine=is_engine,
        engine_name=args.engine,
    )
    print(f"Written to: {out_path}")
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()

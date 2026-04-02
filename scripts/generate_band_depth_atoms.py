#!/usr/bin/env python3
"""
Generate STORY atoms at sparse band×depth combinations using LLM.

Reads existing atoms for style reference, identifies which (band, depth)
combos need more atoms, generates new variants via Qwen, and appends them
to the engine's CANONICAL.txt.

Usage:
    python scripts/generate_band_depth_atoms.py --dry-run --persona gen_z_professionals --topic anxiety --engine comparison
    python scripts/generate_band_depth_atoms.py --all --target-bands 4,5 --target-depths 3,4 --atoms-per-combo 3
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ATOMS_ROOT = REPO_ROOT / "atoms"
ENGINE_DIRS = {"comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher"}
HEADER_RE = re.compile(r"^##\s+(\w+)\s+v(\d+)\s*$")

logger = logging.getLogger("generate_atoms")

# ── Role/depth/stage mapping ─────────────────────────────────────────────────

DEPTH_TO_ROLE = {1: "RECOGNITION", 2: "MECHANISM_PROOF", 3: "TURNING_POINT", 4: "EMBODIMENT"}
DEPTH_TO_STAGE = {1: "pre_awareness", 2: "destabilization", 3: "experimentation", 4: "self_claim"}
DEPTH_TO_COST_TYPE = {1: "social", 2: "internal", 3: "opportunity", 4: "identity"}

BAND_DESCRIPTION = {
    1: "Cool and calm. The character observes the pattern in a quiet, grounded moment. Low emotional intensity. Small everyday scene.",
    2: "Cool-warm. The character notices something unsettling. Slight unease. The pattern is visible but not yet pressing.",
    3: "Warm. Real friction. The pattern creates tension the character can feel in the body. Stakes are becoming personal.",
    4: "Hot. Direct confrontation. Body activated — chest tight, hands cold, stomach dropping. The pattern demands attention NOW.",
    5: "Peak crisis. Breakthrough or collapse. Maximum somatic intensity. The old way is no longer survivable. Something breaks open.",
}

DEPTH_DESCRIPTION = {
    1: "RECOGNITION: The character sees the pattern for the first time. No insight yet — just noticing. The pattern has a name now.",
    2: "MECHANISM_PROOF: The character sees WHY the pattern persists. The protective logic becomes visible. Understanding arrives.",
    3: "TURNING_POINT: The character's frame shifts. The old story stops working. What they believed about the pattern is no longer true.",
    4: "EMBODIMENT: The character owns a new identity. The pattern no longer defines them. They act from the new understanding, not against the old one.",
}

# Persona context (abbreviated)
PERSONA_CONTEXT = {
    "gen_z_professionals": "Gen Z professionals (22-28): remote work, side hustles, LinkedIn anxiety, student loans, gig economy, doom-scrolling, Slack notifications",
    "millennial_women_professionals": "Millennial women professionals (30-42): glass ceiling, invisible labor, maternal wall, work-life balance, imposter syndrome at senior levels",
    "tech_finance_burnout": "Tech/finance burnout (28-45): sprint cycles, KPIs, equity vesting, golden handcuffs, performance reviews, always-on culture",
    "healthcare_rns": "Healthcare RNs (25-55): shift work, compassion fatigue, code blue, patient death, charting, bedside manner while breaking inside",
    "entrepreneurs": "Entrepreneurs (25-50): burn rate, pitch decks, co-founder conflict, investor pressure, pivot anxiety, loneliness of leadership",
    "working_parents": "Working parents (28-48): daycare pickup, bedtime routines, screen time guilt, pumping at work, never enough time for anyone",
    "gen_x_sandwich": "Gen X sandwich generation (42-58): aging parents, teenage children, career plateau, retirement anxiety, caretaker burnout",
    "corporate_managers": "Corporate managers (32-50): team morale, layoff decisions, upward management, meeting culture, performance improvement plans",
    "first_responders": "First responders (22-55): hypervigilance, critical incidents, brotherhood code, civilian disconnect, shift-to-home transition",
    "gen_alpha_students": "Gen Alpha students (12-18): social media comparison, academic pressure, identity formation, digital-native anxiety, friendship drama",
    "educators": "Educators (25-60): classroom management, standardized testing, budget cuts, emotional labor, student trauma exposure",
    "nyc_executives": "NYC executives (35-55): high-stakes deals, commute pressure, prestige addiction, isolation at the top, work-identity fusion",
}

ENGINE_CONTEXT = {
    "comparison": "the comparison engine — measuring self against others, social metrics, perceived inadequacy",
    "false_alarm": "the false alarm engine — anxiety firing without real threat, anticipatory dread, body activating before mind catches up",
    "grief": "the grief engine — loss, absence, what's no longer there, the space where something used to be",
    "overwhelm": "the overwhelm engine — too much input, system overload, paralysis from excess demand",
    "shame": "the shame engine — exposure, being seen as defective, the impulse to hide or shrink",
    "spiral": "the spiral engine — recursive thought loops, each rotation adding intensity, unable to exit the pattern",
    "watcher": "the watcher engine — hypervigilance, scanning for threat, the nervous system on permanent alert",
}

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a therapeutic audiobook prose writer for the Phoenix system.

VOICE RULES (non-negotiable):
- Third-person present tense. Never past tense. Never first-person.
- No rhetorical questions. No tentative language (perhaps, might, could, maybe).
- Active verbs only. No passive voice.
- Every emotional moment anchored in physical sensation (body state, sensory detail).
- Sentence length: emotional beats max 15 words, teaching max 12 words.
- Sentence rhythm must vary — mix short fragments (2-4 words) with longer beats.
- Paragraph breaks create breath. Use them for pacing.
- No inspirational language. No "you can do this." No guru voice.
- This prose will be read by a flat robotic TTS voice. 100% of emotional weight comes from text structure.

FORMAT:
- Return ONLY the prose. No headers, no metadata, no explanations.
- 80-150 words. One continuous scene.
- Concrete, specific, embodied. Name objects, places, body parts.
"""

# ── Core functions ────────────────────────────────────────────────────────────

def _get_next_version(text: str, role: str) -> int:
    """Find the highest existing version for a role and return next."""
    pattern = re.compile(rf"^##\s+{role}\s+v(\d+)", re.MULTILINE)
    versions = [int(m.group(1)) for m in pattern.finditer(text)]
    return max(versions, default=0) + 1


def _get_reference_atoms(text: str, role: str, max_refs: int = 2) -> list[str]:
    """Extract existing prose for a role as style reference."""
    lines = text.split("\n")
    refs = []
    i = 0
    while i < len(lines) and len(refs) < max_refs:
        m = HEADER_RE.match(lines[i].strip())
        if m and m.group(1).upper() == role:
            # Skip to prose (past metadata block)
            i += 1
            if i < len(lines) and lines[i].strip() == "---":
                i += 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            if i < len(lines):
                i += 1  # skip closing ---
            # Collect prose until next ---
            prose_lines = []
            while i < len(lines) and lines[i].strip() != "---":
                prose_lines.append(lines[i])
                i += 1
            prose = "\n".join(prose_lines).strip()
            if prose and len(prose) > 50:
                refs.append(prose)
        i += 1
    return refs


def _build_user_prompt(
    persona: str, topic: str, engine: str,
    band: int, depth: int,
    references: list[str],
) -> str:
    """Build the user prompt for atom generation."""
    persona_desc = PERSONA_CONTEXT.get(persona, persona)
    engine_desc = ENGINE_CONTEXT.get(engine, engine)
    band_desc = BAND_DESCRIPTION.get(band, f"BAND {band}")
    depth_desc = DEPTH_DESCRIPTION.get(depth, f"DEPTH {depth}")

    parts = [
        f"Write one STORY atom for:",
        f"  Persona: {persona_desc}",
        f"  Topic: {topic}",
        f"  Engine: {engine_desc}",
        f"",
        f"EMOTIONAL TEMPERATURE (BAND {band}):",
        f"  {band_desc}",
        f"",
        f"NARRATIVE FUNCTION (DEPTH {depth}):",
        f"  {depth_desc}",
    ]

    if references:
        parts.append("")
        parts.append("STYLE REFERENCE (match this voice and density):")
        for i, ref in enumerate(references[:2]):
            parts.append(f"--- Example {i+1} ---")
            parts.append(ref[:400])

    parts.append("")
    parts.append("Write the prose now. 80-150 words. Third-person present. One scene. Concrete body detail.")

    return "\n".join(parts)


def _format_atom_block(
    role: str, version: int, band: int, depth: int,
    cost_intensity: int, prose: str,
) -> str:
    """Format a CANONICAL.txt atom block."""
    stage = DEPTH_TO_STAGE[depth]
    cost_type = DEPTH_TO_COST_TYPE[depth]
    return (
        f"\n## {role} v{version:02d}\n"
        f"---\n"
        f"BAND: {band}\n"
        f"MECHANISM_DEPTH: {depth}\n"
        f"COST_TYPE: {cost_type}\n"
        f"COST_INTENSITY: {cost_intensity}\n"
        f"IDENTITY_STAGE: {stage}\n"
        f"---\n"
        f"{prose.strip()}\n"
        f"---\n"
    )


def _cost_for_band_depth(band: int, depth: int) -> int:
    """Derive cost_intensity from band and depth."""
    # Higher band + higher depth = higher cost
    base = max(1, min(5, (band + depth) // 2))
    return base


def generate_atoms_for_engine(
    canon_path: Path,
    target_bands: list[int],
    target_depths: list[int],
    atoms_per_combo: int,
    llm_cfg: dict,
    dry_run: bool = False,
) -> dict:
    """Generate atoms for one engine CANONICAL.txt file."""
    from scripts.localization.llm_client import call_llm

    rel = canon_path.relative_to(ATOMS_ROOT)
    parts = rel.parts  # (persona, topic, engine, CANONICAL.txt)
    persona, topic, engine = parts[0], parts[1], parts[2]

    text = canon_path.read_text(encoding="utf-8")
    stats = {"file": str(rel), "generated": 0, "errors": 0, "skipped": 0}
    new_blocks = []

    for band in target_bands:
        for depth in target_depths:
            role = DEPTH_TO_ROLE[depth]
            refs = _get_reference_atoms(text, role)
            if not refs:
                # Try any role for style reference
                for alt_role in ["RECOGNITION", "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT"]:
                    refs = _get_reference_atoms(text, alt_role)
                    if refs:
                        break

            for atom_i in range(atoms_per_combo):
                next_v = _get_next_version(text + "".join(new_blocks), role)
                cost = _cost_for_band_depth(band, depth)

                if dry_run:
                    stats["generated"] += 1
                    continue

                user_prompt = _build_user_prompt(persona, topic, engine, band, depth, refs)

                try:
                    prose = call_llm(
                        SYSTEM_PROMPT, user_prompt, llm_cfg,
                        role="draft",
                        temperature=0.7,
                        max_tokens=500,
                    )
                    # Clean prose — remove any markdown headers or metadata the LLM might add
                    prose = prose.strip()
                    if prose.startswith("##"):
                        prose = "\n".join(prose.split("\n")[1:]).strip()
                    if prose.startswith("---"):
                        # Skip metadata block
                        parts_split = prose.split("---")
                        prose = "---".join(parts_split[2:]).strip() if len(parts_split) > 2 else prose

                    if len(prose) < 30:
                        stats["errors"] += 1
                        logger.warning("Short prose for %s/%s/%s band=%d depth=%d: %d chars",
                                      persona, topic, engine, band, depth, len(prose))
                        continue

                    block = _format_atom_block(role, next_v, band, depth, cost, prose)
                    new_blocks.append(block)
                    stats["generated"] += 1

                except Exception as exc:
                    stats["errors"] += 1
                    logger.error("LLM error for %s/%s/%s band=%d depth=%d: %s",
                                persona, topic, engine, band, depth, exc)
                    time.sleep(2)  # backoff on error

    if new_blocks and not dry_run:
        with open(canon_path, "a", encoding="utf-8") as f:
            f.write("".join(new_blocks))

    return stats


def find_engine_files(
    atoms_root: Path,
    persona: str | None = None,
    topic: str | None = None,
    engine: str | None = None,
) -> list[Path]:
    """Find engine CANONICAL.txt files."""
    files = []
    for p_dir in sorted(atoms_root.iterdir()):
        if not p_dir.is_dir() or (persona and p_dir.name != persona):
            continue
        for t_dir in sorted(p_dir.iterdir()):
            if not t_dir.is_dir() or (topic and t_dir.name != topic):
                continue
            for e_dir in sorted(t_dir.iterdir()):
                if e_dir.name not in ENGINE_DIRS or (engine and e_dir.name != engine):
                    continue
                canon = e_dir / "CANONICAL.txt"
                if canon.exists():
                    files.append(canon)
    return files


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Generate STORY atoms at sparse band×depth combos")
    parser.add_argument("--persona", help="Filter to persona (or --all)")
    parser.add_argument("--topic", help="Filter to topic")
    parser.add_argument("--engine", help="Filter to engine")
    parser.add_argument("--all", action="store_true", help="Process all personas/topics/engines")
    parser.add_argument("--target-bands", default="4,5", help="Comma-separated bands to fill (default: 4,5)")
    parser.add_argument("--target-depths", default="3,4", help="Comma-separated depths to fill (default: 3,4)")
    parser.add_argument("--atoms-per-combo", type=int, default=3, help="Atoms per (band,depth) combo (default: 3)")
    parser.add_argument("--model", default="qwen-plus", help="LLM model (default: qwen-plus)")
    parser.add_argument("--max-parallel", type=int, default=1, help="Parallel workers (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    parser.add_argument("--limit", type=int, help="Limit to first N files")
    args = parser.parse_args()

    target_bands = [int(b) for b in args.target_bands.split(",")]
    target_depths = [int(d) for d in args.target_depths.split(",")]

    if not args.all and not args.persona:
        parser.error("Specify --persona or --all")

    files = find_engine_files(
        ATOMS_ROOT,
        persona=None if args.all else args.persona,
        topic=args.topic,
        engine=args.engine,
    )
    if args.limit:
        files = files[:args.limit]

    if not files:
        print("No engine CANONICAL.txt files found.")
        return 1

    combos = len(target_bands) * len(target_depths) * args.atoms_per_combo
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Generating atoms:")
    print(f"  Files: {len(files)}")
    print(f"  Target bands: {target_bands}")
    print(f"  Target depths: {target_depths}")
    print(f"  Atoms per combo: {args.atoms_per_combo}")
    print(f"  Total atoms to generate: {len(files) * combos}")
    print(f"  Model: {args.model}")
    print()

    llm_cfg = {
        "draft_model": {
            "temperature": 0.7,
            "max_output_tokens": 500,
            "timeout_seconds": 60,
        }
    }

    total_gen = total_err = 0

    if args.max_parallel > 1 and not args.dry_run:
        with ThreadPoolExecutor(max_workers=args.max_parallel) as pool:
            futures = {
                pool.submit(generate_atoms_for_engine, f, target_bands, target_depths,
                           args.atoms_per_combo, llm_cfg, args.dry_run): f
                for f in files
            }
            for future in as_completed(futures):
                stats = future.result()
                total_gen += stats["generated"]
                total_err += stats["errors"]
                if stats["generated"] > 0:
                    print(f"  {stats['file']}: +{stats['generated']} atoms")
    else:
        for i, f in enumerate(files):
            stats = generate_atoms_for_engine(f, target_bands, target_depths,
                                              args.atoms_per_combo, llm_cfg, args.dry_run)
            total_gen += stats["generated"]
            total_err += stats["errors"]
            if stats["generated"] > 0 and not args.dry_run:
                print(f"  [{i+1}/{len(files)}] {stats['file']}: +{stats['generated']} atoms")
            elif args.dry_run and (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(files)}] processed...")

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{prefix}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Atoms generated: {total_gen}")
    print(f"  Errors: {total_err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

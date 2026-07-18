#!/usr/bin/env python3
"""Compose exercises from 5 dimensions — no two exercises alike.

Generates exercise definitions for an entire book (12 chapters),
each with a unique combination of context, body signal, entry,
technique, and landing. Assembles from the sentence bank.

Usage:
    # Generate 12 exercises for a book
    python3 scripts/pearl_practice/compose_exercise.py \
        --persona healthcare_rns --topic grief --chapters 12 \
        -o artifacts/practice/healthcare_rns_grief/

    # Generate and assemble one exercise as MP3
    python3 scripts/pearl_practice/compose_exercise.py \
        --persona corporate_managers --topic anxiety --chapter 1 \
        -o ~/Desktop/anxiety_ch1_exercise.mp3 --assemble
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    sys.exit(1)


def _load_dimensions() -> dict:
    return yaml.safe_load((REPO_ROOT / "config" / "pearl_practice" / "exercise_dimensions.yaml").read_text())


def _load_pacing(topic: str) -> dict:
    cfg = yaml.safe_load((REPO_ROOT / "config" / "pearl_practice" / "pacing_profiles.yaml").read_text())
    profiles = cfg.get("profiles", {})
    return profiles.get(topic, profiles.get("default", {}))


def _det_pick(items: list, seed: int) -> any:
    """Deterministic selection from list based on seed."""
    return items[seed % len(items)]


def compose_exercise(
    persona: str,
    topic: str,
    chapter: int,
    *,
    total_chapters: int = 12,
) -> dict:
    """Compose one exercise from 5 dimensions.

    Uses deterministic selection so the same persona+topic+chapter
    always produces the same exercise. Different chapters get different
    combos.
    """
    dims = _load_dimensions()
    pacing = _load_pacing(topic)

    seed_str = f"{persona}:{topic}:{chapter}"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)

    # Get persona contexts (fall back to corporate_managers)
    contexts = dims["dim1_context"].get(persona, dims["dim1_context"].get("corporate_managers", []))
    body_signals = dims["dim2_body_signal"]
    entries = dims["dim3_entry"]
    techniques = dims["dim4_technique"]
    tech_names = list(techniques.keys())
    landings = dims["dim5_landing"].get(topic, dims["dim5_landing"].get("default", []))

    # Select one from each dimension — rotate through to avoid repeats across chapters
    context = contexts[(chapter - 1) % len(contexts)]
    body_signal = body_signals[(chapter - 1 + seed % 5) % len(body_signals)]
    entry = entries[(chapter - 1 + seed % 3) % len(entries)]
    tech_name = tech_names[(chapter - 1) % len(tech_names)]
    technique = techniques[tech_name]
    landing = landings[(chapter - 1) % len(landings)]

    # Build the full exercise section list
    sections = []

    # DIM 1 + DIM 2: Context + Body (narrated intro)
    sections.append({"text": context, "pause_s": pacing.get("standard_pause_s", 4), "section": "context", "source": "dim1"})
    sections.append({"text": body_signal, "pause_s": pacing.get("standard_pause_s", 4), "section": "body_signal", "source": "dim2"})

    # DIM 3: Entry
    sections.append({"text": entry, "pause_s": pacing.get("opening_pause_s", 6), "section": "entry", "source": "dim3_bank"})

    # DIM 4: Technique (all from bank)
    for step in technique["sentences"]:
        sections.append({
            "text": step["text"],
            "pause_s": step["pause_s"],
            "section": "technique",
            "source": "dim4_bank",
        })

    # DIM 5: Landing
    sections.append({"text": landing, "pause_s": pacing.get("closing_pause_s", 4), "section": "landing", "source": "dim5"})

    # Standard close
    sections.append({"text": "Open your eyes.", "pause_s": 3, "section": "close", "source": "bank"})

    # Calculate stats
    total_pause = sum(s["pause_s"] for s in sections)
    est_speech = sum(len(s["text"].split()) / 80 * 60 for s in sections)
    bank_count = sum(1 for s in sections if "bank" in s["source"])

    return {
        "persona": persona,
        "topic": topic,
        "chapter": chapter,
        "technique": tech_name,
        "context": context,
        "body_signal": body_signal,
        "entry": entry,
        "landing": landing,
        "sections": sections,
        "stats": {
            "total_sections": len(sections),
            "bank_sentences": bank_count,
            "narrated_sentences": len(sections) - bank_count,
            "bank_ratio": round(bank_count / max(1, len(sections)), 2),
            "est_speech_s": round(est_speech, 1),
            "est_silence_s": round(total_pause, 1),
            "est_total_s": round(est_speech + total_pause, 1),
            "speech_ratio": round(est_speech / max(1, est_speech + total_pause), 2),
        },
    }


def compose_book(persona: str, topic: str, chapters: int = 12) -> list[dict]:
    """Compose all exercises for a book."""
    return [compose_exercise(persona, topic, ch, total_chapters=chapters) for ch in range(1, chapters + 1)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Compose exercises from 5 dimensions")
    ap.add_argument("--persona", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--chapter", type=int, default=None, help="Single chapter (1-based)")
    ap.add_argument("--chapters", type=int, default=12, help="Total chapters for book mode")
    ap.add_argument("-o", "--output", required=True, type=Path)
    ap.add_argument("--assemble", action="store_true", help="Also assemble MP3 from sentence bank")
    args = ap.parse_args()

    if args.chapter:
        exercises = [compose_exercise(args.persona, args.topic, args.chapter, total_chapters=args.chapters)]
    else:
        exercises = compose_book(args.persona, args.topic, args.chapters)

    # Print summary
    print(f"{'='*60}", flush=True)
    print(f"EXERCISE PLAN: {args.persona} / {args.topic} / {len(exercises)} exercises", flush=True)
    print(f"{'='*60}", flush=True)
    for ex in exercises:
        s = ex["stats"]
        print(f"  Ch {ex['chapter']:2d}: {ex['technique']:22s} | {s['est_total_s']:5.0f}s | "
              f"bank={s['bank_ratio']:.0%} | {ex['context'][:40]}", flush=True)

    # Save
    if args.output.suffix in (".yaml", ".yml"):
        args.output.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(exercises if len(exercises) > 1 else exercises[0],
                  open(args.output, "w"), default_flow_style=False, allow_unicode=True, width=120)
    elif args.output.suffix == ".json":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(exercises if len(exercises) > 1 else exercises[0], indent=2))
    elif args.output.suffix == ".mp3" and args.assemble and len(exercises) == 1:
        # Assemble single exercise as MP3
        from scripts.pearl_practice.assemble_from_bank import assemble_practice
        stats = assemble_practice(exercises[0]["sections"], args.output)
        print(f"\nAssembled: {args.output} ({stats['total_duration_s']}s, "
              f"{stats['sentences_matched']} matched, {stats['sentences_missed']} missed)", flush=True)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(exercises, indent=2))

    print(f"\nSaved: {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

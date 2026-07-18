#!/usr/bin/env python3
"""Compose exercise components from templates + description.

Takes any exercise (from practice library or atoms) and assembles
full 5-component structure using the template system. Only the
description is per-exercise; bridge/intro/aha/integration come
from rotating templates.

Usage:
    # Compose one exercise
    python3 scripts/pearl_practice/template_composer.py \
        --exercise-id cyclic_sighing --chapter 3 \
        --source ab_tady_37

    # Compose all exercises for a 12-chapter book
    python3 scripts/pearl_practice/template_composer.py \
        --type body_awareness --chapters 12 \
        -o artifacts/practice/body_awareness_book.json

    # Convert all 272 library_34 exercises to production-ready
    python3 scripts/pearl_practice/template_composer.py --convert-all
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


def _load_templates() -> dict:
    return yaml.safe_load((REPO_ROOT / "config" / "pearl_practice" / "component_templates.yaml").read_text())


def _det_pick(items: list, seed: int, offset: int = 0) -> str:
    """Deterministic pick — different offset gives different item."""
    return items[(seed + offset) % len(items)]


def compose_components(
    exercise_name: str,
    exercise_type: str,
    description_full: str,
    description_lean: str,
    chapter: int = 1,
    total_chapters: int = 12,
) -> dict:
    """Assemble 5 components from templates.

    Returns dict with bridge/intro/description/aha/integration,
    each with full/lean variants.
    """
    tmpl = _load_templates()
    seed = int(hashlib.sha256(f"{exercise_type}:{exercise_name}:{chapter}".encode()).hexdigest()[:8], 16)

    # Normalize type name for template lookup
    etype = exercise_type.lower().replace("00_", "").replace("06_", "").replace("_sound", "")
    if etype not in tmpl.get("intro_mechanism", {}):
        # Try without prefix numbers
        for key in tmpl["intro_mechanism"]:
            if key in etype or etype in key:
                etype = key
                break
        else:
            etype = "body_awareness"  # safe fallback

    bridges = tmpl["bridge"]
    mechanisms = tmpl["intro_mechanism"].get(etype, tmpl["intro_mechanism"]["body_awareness"])
    observations = tmpl["aha_observation"].get(etype, tmpl["aha_observation"]["body_awareness"])
    permissions = tmpl["aha_permission"]
    takeaways = tmpl["integration_takeaway"].get(etype, tmpl["integration_takeaway"]["body_awareness"])
    closings = tmpl["integration_closing"]

    # Pick one from each, rotating by chapter so no repeats in a book
    bridge_lean = bridges[(chapter - 1) % len(bridges)]
    mechanism = _det_pick(mechanisms, seed, chapter)
    observation = _det_pick(observations, seed, chapter)
    permission = _det_pick(permissions, seed, chapter)
    takeaway = _det_pick(takeaways, seed, chapter)
    closing = _det_pick(closings, seed, chapter)

    # Assemble full variants (richer versions of lean)
    bridge_full = f"{bridge_lean} Not to fix anything. Just to give yourself a different input for a moment."
    intro_full = f"This is {exercise_name}. {mechanism} You do not need to believe that. Just try it."
    aha_full = f"Now, I want you to notice something. Notice {observation}. {permission} Whatever happened — or did not happen — is exactly right."
    integration_full = f"Now, before you move on, {takeaway}. Nothing has to change from this moment forward. {closing}"

    return {
        "bridge": {
            "full": bridge_full,
            "lean": bridge_lean,
        },
        "intro": {
            "full": intro_full,
            "lean": f"This is {exercise_name}. {mechanism}",
        },
        "description": {
            "full": description_full,
            "lean": description_lean,
        },
        "aha": {
            "full": aha_full,
            "lean": f"Now, notice {observation}. {permission}",
        },
        "integration": {
            "full": integration_full,
            "lean": f"Before you move on, {takeaway}. {closing}",
        },
    }


def compress_description(text: str, max_sentences: int = 4, max_words: int = 8) -> str:
    """Compress exercise text to lean description.

    Keeps only action verbs. Strips metaphor and explanation.
    Each sentence ≤ max_words. Max max_sentences total.
    """
    import re
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    # Score sentences: prefer short imperatives with action verbs
    action_words = {"breathe", "feel", "notice", "close", "open", "hold", "release",
                    "count", "repeat", "press", "push", "shake", "place", "sit",
                    "stand", "look", "name", "find", "imagine", "picture", "write",
                    "say", "take", "let", "put", "move", "drop", "squeeze", "tense",
                    "relax", "soften", "scan", "bring", "rest", "focus", "return",
                    "check", "touch", "listen", "hear", "see", "smell", "taste"}

    scored = []
    for s in sentences:
        words = s.split()
        word_count = len(words)
        has_action = any(w.lower().rstrip(".,!?") in action_words for w in words[:3])
        is_short = word_count <= max_words
        is_instruction = words[0][0].isupper() and not s.startswith(("The ", "This ", "That ", "It ", "Your "))

        score = 0
        if has_action:
            score += 3
        if is_short:
            score += 2
        if is_instruction:
            score += 1
        if word_count > 12:
            score -= 2

        scored.append((score, s, word_count))

    # Take top-scoring sentences, preserving original order
    scored_with_idx = [(score, s, wc, i) for i, (score, s, wc) in enumerate(scored)]
    scored_with_idx.sort(key=lambda x: -x[0])
    selected_indices = sorted([idx for _, _, _, idx in scored_with_idx[:max_sentences]])

    lean_parts = []
    for idx in selected_indices:
        s = sentences[idx]
        words = s.split()
        if len(words) > max_words:
            # Truncate to max_words
            s = " ".join(words[:max_words]).rstrip(".,") + "."
        lean_parts.append(s)

    return " ".join(lean_parts)


def convert_library_34(exercise_type: str) -> dict:
    """Convert one library_34 file to production-ready format."""
    input_path = REPO_ROOT / "SOURCE_OF_TRUTH" / "practice_library" / "inbox" / f"{exercise_type}_library_34.json"
    if not input_path.is_file():
        raise FileNotFoundError(f"Not found: {input_path}")

    data = json.loads(input_path.read_text())
    exercises_in = data.get("exercises", [])

    exercises_out = []
    for i, ex in enumerate(exercises_in):
        name = ex.get("name", ex.get("id", f"{exercise_type}_{i+1}"))
        text = ex.get("text", "")
        lean_desc = compress_description(text)

        components = compose_components(
            exercise_name=name,
            exercise_type=exercise_type,
            description_full=text,
            description_lean=lean_desc,
            chapter=(i % 12) + 1,
        )

        exercises_out.append({
            "id": ex.get("id", f"lib34_{exercise_type}_{i+1:02d}"),
            "name": name,
            "exercise_type": exercise_type,
            "duration_seconds": ex.get("duration_seconds", 60),
            "difficulty": ex.get("difficulty", "beginner"),
            "tags": ex.get("tags", []),
            "text": text,
            "components": components,
        })

    return {
        "content_type": exercise_type,
        "version": "1.0",
        "total_count": len(exercises_out),
        "schema_note": "Each exercise has backward-compatible 'text' field plus structured 'components' with full/lean variants for the exercise component assembly system.",
        "exercises": exercises_out,
    }


def convert_all() -> dict:
    """Convert all 8 library_34 types to production-ready format."""
    types = ["affirmations", "body_awareness", "integration_bridges", "meditations",
             "reflections", "self_inquiry", "sensory_grounding", "thought_experiments"]

    results = {}
    for etype in types:
        try:
            output = convert_library_34(etype)
            out_path = (REPO_ROOT / "SOURCE_OF_TRUTH" / "practice_library" / "inbox"
                        / f"{etype}_library_34_PRODUCTION_READY.json")
            out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
            results[etype] = {"count": output["total_count"], "path": str(out_path)}
            print(f"  {etype:25s}: {output['total_count']} exercises → {out_path.name}", flush=True)
        except Exception as e:
            results[etype] = {"error": str(e)}
            print(f"  {etype:25s}: ERROR — {e}", flush=True)

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Compose exercise components from templates")
    ap.add_argument("--convert-all", action="store_true", help="Convert all 272 library_34 exercises")
    ap.add_argument("--type", help="Single exercise type to convert")
    ap.add_argument("--exercise-id", help="Single exercise ID")
    ap.add_argument("--chapter", type=int, default=1)
    ap.add_argument("--chapters", type=int, default=12)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    if args.convert_all:
        print("Converting all 272 library_34 exercises to production-ready format...\n", flush=True)
        results = convert_all()
        total = sum(r.get("count", 0) for r in results.values())
        print(f"\nTotal: {total} exercises converted across {len(results)} types", flush=True)
        return 0

    if args.type:
        output = convert_library_34(args.type)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False))
            print(f"Wrote {output['total_count']} exercises to {args.output}")
        else:
            print(json.dumps(output["exercises"][0], indent=2))
        return 0

    print("Use --convert-all or --type <exercise_type>", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

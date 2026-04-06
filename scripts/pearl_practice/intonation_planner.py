#!/usr/bin/env python3
"""Intonation planner for therapeutic audio.

Analyzes each sentence in an exercise and generates TTS-ready text with
intonation control markup. Every sentence gets:

1. Emotional function classification (grounding, permission, validation,
   instruction, invitation, declaration, processing)
2. Final-word intonation direction (fall, level, gentle_rise)
3. TTS text rewrite with ellipsis, punctuation, and trailing phrases
   that force the correct intonation from ElevenLabs

The core insight: ElevenLabs TTS intonation is driven by punctuation and
sentence structure, not SSML. A period forces falling tone. A question mark
forces rising. An ellipsis forces a pause-then-neutral approach. A trailing
phrase after the key word ensures the key word doesn't get sentence-final
rising intonation.

Rules for therapeutic grief/somatic content:
- Declarations of truth → FALL ("The grief is real." → down on "real")
- Permission statements → FALL ("That's allowed." → down, grounding)
- Body instructions → LEVEL then FALL ("Feel it in your body." → steady)
- Questions about sensation → GENTLE RISE then FALL ("Where is the heaviness?" → slight rise, but compassionate)
- Validation → FALL ("You cared." → warm, downward, final)
- Invitations → LEVEL ("Let yourself feel." → open, not commanding)
"""
from __future__ import annotations

import hashlib
import re
from typing import Any


# ── Sentence function classification ────────────────────────────────

# Keywords that signal each function type
_FUNCTION_SIGNALS: dict[str, list[str]] = {
    "permission": ["allowed", "okay", "can", "may", "permission", "it's okay", "that's okay",
                    "you can", "you may", "if you need", "don't have to"],
    "validation": ["you cared", "you were", "that's right", "that matters", "that's real",
                    "you did", "you showed up", "you are", "brave", "humanity", "real love",
                    "they mattered", "truly present"],
    "grounding": ["feet", "floor", "ground", "solid", "here", "now", "this moment",
                   "beneath you", "supported", "safe", "breath"],
    "body_instruction": ["feel", "notice", "put your hand", "hold it", "breathe",
                          "body", "chest", "shoulders", "tension", "sensation"],
    "invitation": ["let yourself", "let it", "let the", "allow", "when you're ready",
                    "gently", "slowly", "softly"],
    "declaration": ["is real", "is true", "is the", "means", "that's what",
                     "it's the proof", "doesn't have", "don't need"],
    "processing": ["cry", "tears", "grief", "pain", "loss", "heaviness",
                    "hurt", "sorrow", "ache"],
}


def classify_sentence(sentence: str) -> str:
    """Classify sentence by therapeutic function."""
    s = sentence.lower().strip()
    # Check each function type — first match wins (ordered by specificity)
    for func in ["permission", "validation", "processing", "body_instruction",
                 "grounding", "invitation", "declaration"]:
        for signal in _FUNCTION_SIGNALS[func]:
            if signal in s:
                return func
    # Short imperative sentences (2-4 words) are usually instructions
    if len(s.split()) <= 4 and s.endswith("."):
        return "body_instruction"
    return "declaration"


def intonation_direction(function: str, sentence: str) -> str:
    """Determine how the final word should be spoken.

    fall       = downward, grounding, definitive, compassionate
    level      = steady, open, continuing, inviting
    gentle_rise = slight upward for genuine questions, but warmer than normal question
    """
    if function in ("permission", "validation", "declaration"):
        return "fall"
    if function == "processing":
        return "fall"  # grief content always falls — grounding, not exciting
    if function == "invitation":
        return "level"  # open, not commanding
    if function == "grounding":
        return "fall"  # anchoring
    if function == "body_instruction":
        # Questions about body sensation get gentle rise, statements fall
        if "?" in sentence:
            return "gentle_rise"
        return "fall"
    return "fall"


# ── TTS text rewriting ──────────────────────────────────────────────

def _needs_restructure(sentence: str, direction: str) -> bool:
    """Check if this sentence will likely get wrong intonation from TTS."""
    s = sentence.strip()
    # Short sentences ending in emotionally loaded words often rise incorrectly
    words = s.rstrip("?.!").split()
    if not words:
        return False
    final_word = words[-1].lower()

    # Words that TTS tends to make rise when they should fall
    problem_finals = {"real", "right", "true", "enough", "here", "now",
                      "allowed", "that", "humanity", "present", "feel",
                      "still", "shift", "loss", "grief"}

    if final_word in problem_finals and direction == "fall":
        return True

    # Very short sentences (1-3 words) often get weird intonation
    if len(words) <= 2:
        return True

    return False


def rewrite_for_intonation(sentence: str, direction: str, function: str) -> str:
    """Rewrite sentence to guide TTS toward correct intonation.

    Techniques:
    1. Ellipsis before key final word → forces neutral approach
    2. Trailing phrase after key word → ensures key word isn't sentence-final
    3. Period instead of question mark → forces falling tone for rhetorical questions
    4. Sentence splitting → short declaratives get more control
    """
    s = sentence.strip()

    if not _needs_restructure(s, direction):
        # Sentence is probably fine as-is
        # But still convert rhetorical questions to statements for falling tone
        if direction == "fall" and s.endswith("?"):
            return s[:-1] + "."
        return s

    words = s.rstrip("?.!").split()
    final_word = words[-1] if words else ""
    punct = s[-1] if s[-1] in ".?!" else "."

    if direction == "fall":
        # Strategy 1: Add ellipsis before final word
        if len(words) >= 3:
            pre = " ".join(words[:-1])
            return f"{pre}... {final_word}."

        # Strategy 2: For very short sentences, use ellipsis before final word
        if len(words) >= 2:
            pre = " ".join(words[:-1])
            return f"{pre}... {final_word}."

    elif direction == "gentle_rise":
        # Convert hard question marks to softer phrasing
        if s.endswith("?"):
            # Keep the question but make it feel rhetorical/gentle
            return s  # Questions are fine for gentle_rise

    elif direction == "level":
        # Add continuation feel — comma or ellipsis before period
        if s.endswith("."):
            return s[:-1] + "..."

    return s


# ── Full sentence analysis ──────────────────────────────────────────

def analyze_sentence(sentence: str, topic: str = "grief") -> dict[str, Any]:
    """Full analysis of one sentence for therapeutic TTS delivery."""
    function = classify_sentence(sentence)
    direction = intonation_direction(function, sentence)
    rewritten = rewrite_for_intonation(sentence, direction, function)

    return {
        "original": sentence.strip(),
        "rewritten": rewritten,
        "function": function,
        "intonation": direction,
        "changed": rewritten != sentence.strip(),
    }


def plan_exercise_intonation(sentences: list[str], topic: str = "grief") -> list[dict[str, Any]]:
    """Analyze every sentence in an exercise and produce intonation plan."""
    return [analyze_sentence(s, topic) for s in sentences if s.strip()]


# ── CLI for inspection ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Default: analyze grief exercise v01
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    path = REPO_ROOT / "atoms" / "healthcare_rns" / "grief" / "EXERCISE" / "CANONICAL.txt"

    text = path.read_text(encoding="utf-8")
    # Get v01
    blocks = re.split(r"## EXERCISE v\d+\s*\n-+\s*\n\s*-+\s*\n", text)
    blocks = [b.strip().strip("-").strip() for b in blocks if b.strip().strip("-").strip()]
    raw = blocks[0]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]

    print("=== GRIEF EXERCISE v01 — Intonation Plan ===\n")
    plan = plan_exercise_intonation(sentences, "grief")
    for p in plan:
        marker = "↓" if p["intonation"] == "fall" else ("→" if p["intonation"] == "level" else "↗")
        changed = " *** REWRITTEN" if p["changed"] else ""
        print(f"  {marker} [{p['function']:18s}] {p['rewritten']}{changed}")
        if p["changed"]:
            print(f"    (was: \"{p['original']}\")")
    print(f"\n  {sum(1 for p in plan if p['changed'])}/{len(plan)} sentences rewritten for intonation control")

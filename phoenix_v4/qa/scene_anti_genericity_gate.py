"""
Scene anti-genericity gate — runtime enforcement of §8 anti-generic scene rules.

Maps to docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md §8:
  - §8.2 Three-detail rule (unique sensory details per chapter)
  - §8.3 Action-state test (micro-action or body state required)
  - §8.4 SCENE collision scan (Jaccard similarity on 4-gram sets)
  - §8.5 Location phrase repetition cap

Deterministic: same chapters list -> same result.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChapterDiagnostic:
    """Per-chapter diagnostic detail."""
    chapter_index: int
    unique_details: int
    has_action: bool
    collisions: List[str]
    location_phrases: List[str]
    errors: List[str]
    warnings: List[str]


@dataclass(frozen=True)
class SceneReport:
    """Aggregate result from check_scene_genericity."""
    status: str  # PASS | WARN | FAIL
    chapter_diagnostics: List[ChapterDiagnostic]
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


@dataclass(frozen=True)
class GateResult:
    """Result from enforce_scene_gate."""
    status: str  # PASS | WARN | FAIL
    report: SceneReport
    mode: str
    blocking: bool


# ---------------------------------------------------------------------------
# Sensory-detail extraction
# ---------------------------------------------------------------------------

_SENSORY_NOUNS = frozenset({
    "thumb", "finger", "fingers", "hand", "hands", "wrist", "palm", "knuckle",
    "shoulder", "shoulders", "jaw", "teeth", "lip", "lips", "tongue", "throat",
    "chest", "ribs", "spine", "neck", "forehead", "cheek", "eyelid", "eyelids",
    "knee", "knees", "ankle", "heel", "toe", "toes", "elbow", "hip",
    "skin", "hair", "nail", "nails", "stomach", "belly",
    "mug", "cup", "glass", "phone", "screen", "keyboard", "laptop", "desk",
    "chair", "mirror", "door", "window", "counter", "pillow", "blanket",
    "clock", "watch", "ring", "pen", "paper", "receipt", "ticket",
    "steering wheel", "dashboard", "seat belt",
})

_SENSORY_ADJECTIVES = frozenset({
    "cold", "warm", "hot", "damp", "wet", "dry", "sticky", "smooth", "rough",
    "sharp", "dull", "soft", "hard", "tight", "loose", "heavy", "light",
    "bright", "dim", "dark", "loud", "quiet", "silent", "bitter", "sweet",
    "sour", "metallic", "stale", "fresh", "grey", "gray", "fluorescent",
})

_DETAIL_PATTERN = re.compile(
    r"\b(?:"
    + "|".join(re.escape(w) for w in sorted(_SENSORY_ADJECTIVES))
    + r")\s+\w+"
    r"|\b(?:"
    + "|".join(re.escape(w) for w in sorted(_SENSORY_NOUNS))
    + r")\b",
    re.I,
)

_SPECIFIC_QUALIFIER = re.compile(
    r"\b(\d+|oat[\s-]?milk|fluorescent|digital|grey|gray|lukewarm|cracked|chipped|"
    r"stained|frayed|faded|torn|bent|yellowed|scratched|dented|rusted)\b",
    re.I,
)


def _extract_sensory_phrases(text: str) -> List[str]:
    """Return list of sensory detail phrases found in text."""
    matches = _DETAIL_PATTERN.findall(text)
    return [m.strip().lower() for m in matches if m.strip()]


def _unique_details_for_chapter(
    chapter_phrases: List[str],
    all_other_phrases: set[str],
) -> List[str]:
    """Return phrases in this chapter not found in any other chapter."""
    return [p for p in chapter_phrases if p not in all_other_phrases]


# ---------------------------------------------------------------------------
# 4-gram Jaccard collision scan (§8.4)
# ---------------------------------------------------------------------------

def _ngrams(text: str, n: int = 4) -> set[tuple[str, ...]]:
    """Extract n-gram set from text."""
    words = re.findall(r"[a-z]+", text.lower())
    if len(words) < n:
        return set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _find_collisions(
    chapters: List[str],
    threshold: float = 0.8,
) -> List[tuple[int, int, float]]:
    """Return pairs (i, j, similarity) where Jaccard > threshold on 4-gram sets."""
    gram_sets = [_ngrams(ch) for ch in chapters]
    collisions = []
    for i in range(len(gram_sets)):
        for j in range(i + 1, len(gram_sets)):
            sim = _jaccard(gram_sets[i], gram_sets[j])
            if sim > threshold:
                collisions.append((i, j, round(sim, 4)))
    return collisions


# ---------------------------------------------------------------------------
# Action-state test (§8.3)
# ---------------------------------------------------------------------------

_ACTION_VERBS = re.compile(
    r"\b(hover|press|grip|clench|unclench|reach|pull|push|lift|lower|turn|"
    r"shift|lean|step|walk|sit|stand|stretch|exhale|inhale|breathe|swallow|"
    r"blink|nod|shake|tap|scroll|type|squeeze|release|drop|place|hold|"
    r"curl|fold|cross|rest|tighten|loosen|move|freeze|flinch|shrug|"
    r"rub|scratch|dig|tuck|roll|slide|twist|arch|hunch|straighten)s?\b",
    re.I,
)

_BODY_PARTS_FOR_ACTION = re.compile(
    r"\b(hand|hands|finger|fingers|thumb|foot|feet|leg|legs|arm|arms|"
    r"shoulder|shoulders|jaw|head|body|knee|knees|back|spine|"
    r"chest|neck|hip|hips|wrist|toe|toes|eye|eyes)\b",
    re.I,
)


def _has_character_action(text: str) -> bool:
    """True if text contains at least one verb + body/movement combination."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sent in sentences:
        if _ACTION_VERBS.search(sent) and _BODY_PARTS_FOR_ACTION.search(sent):
            return True
    return False


# ---------------------------------------------------------------------------
# Location phrase repetition (§8.5)
# ---------------------------------------------------------------------------

_LOCATION_PATTERN = re.compile(
    r"\b(?:in the|at the|on the|by the|near the|inside the|outside the|"
    r"across the|behind the|beside the)\s+[a-z]+(?:\s+[a-z]+)?",
    re.I,
)


def _extract_location_phrases(text: str) -> List[str]:
    """Return location phrases found in text."""
    return [m.strip().lower() for m in _LOCATION_PATTERN.findall(text)]


def _find_repeated_locations(
    chapters: List[str],
    threshold: float = 0.5,
) -> Dict[str, List[int]]:
    """Return location phrases appearing in >threshold fraction of chapters."""
    location_index: Dict[str, set[int]] = {}
    for idx, ch in enumerate(chapters):
        phrases = set(_extract_location_phrases(ch))
        for phrase in phrases:
            location_index.setdefault(phrase, set()).add(idx)

    n = len(chapters)
    if n < 2:
        return {}
    return {
        phrase: sorted(indices)
        for phrase, indices in location_index.items()
        if len(indices) / n > threshold
    }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def check_scene_genericity(chapters: List[str]) -> SceneReport:
    """
    Analyse a list of chapter texts for scene genericity issues.

    Returns a SceneReport with per-chapter diagnostics and aggregate pass/fail.

    Rules enforced:
      1. Three-detail rule: each chapter >= 3 unique sensory details
      2. Scene collision scan: Jaccard > 0.8 on 4-gram sets between any pair
      3. Action-state test: each chapter must have >= 1 character action
      4. Location phrase repetition: same phrase in > 50% chapters = flagged
    """
    if not chapters:
        return SceneReport(
            status="PASS",
            chapter_diagnostics=[],
            errors=[],
            warnings=[],
            metrics={"chapter_count": 0},
        )

    errors: List[str] = []
    warnings: List[str] = []
    diagnostics: List[ChapterDiagnostic] = []

    # Extract sensory phrases per chapter
    chapter_phrases = [_extract_sensory_phrases(ch) for ch in chapters]
    all_phrases_flat = [set(phrases) for phrases in chapter_phrases]

    # Collision scan
    collisions = _find_collisions(chapters)
    collision_map: Dict[int, List[str]] = {}
    for i, j, sim in collisions:
        msg = f"collision_ch{i}_ch{j}_sim={sim}"
        collision_map.setdefault(i, []).append(msg)
        collision_map.setdefault(j, []).append(msg)
        errors.append(f"SCENE_COLLISION: chapters {i} and {j} share 4-gram Jaccard={sim}")

    # Location repetition
    repeated_locations = _find_repeated_locations(chapters)
    for phrase, indices in repeated_locations.items():
        pct = len(indices) / len(chapters)
        errors.append(
            f"LOCATION_REPETITION: '{phrase}' appears in {len(indices)}/{len(chapters)} "
            f"chapters ({pct:.0%})"
        )

    # Per-chapter checks
    for idx, chapter_text in enumerate(chapters):
        ch_errors: List[str] = []
        ch_warnings: List[str] = []

        # Unique details
        other_phrases: set[str] = set()
        for j, pset in enumerate(all_phrases_flat):
            if j != idx:
                other_phrases |= pset
        unique = _unique_details_for_chapter(chapter_phrases[idx], other_phrases)
        unique_count = len(set(unique))

        if unique_count < 3:
            ch_errors.append(
                f"THREE_DETAIL_RULE: only {unique_count} unique sensory "
                f"detail(s), need >=3"
            )

        # Action-state test
        has_action = _has_character_action(chapter_text)
        if not has_action:
            ch_errors.append("STATIC_SCENE: no character action (verb + body/movement) found")

        # Location repetition flagging per chapter
        ch_locations = _extract_location_phrases(chapter_text)
        ch_repeated_locs = [
            loc for loc in ch_locations if loc in repeated_locations
        ]
        if ch_repeated_locs:
            ch_warnings.append(
                f"REPEATED_LOCATION: uses overused phrase(s): {', '.join(set(ch_repeated_locs))}"
            )

        diagnostics.append(ChapterDiagnostic(
            chapter_index=idx,
            unique_details=unique_count,
            has_action=has_action,
            collisions=collision_map.get(idx, []),
            location_phrases=ch_locations,
            errors=ch_errors,
            warnings=ch_warnings,
        ))

        errors.extend(f"ch{idx}: {e}" for e in ch_errors)
        warnings.extend(f"ch{idx}: {w}" for w in ch_warnings)

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")

    metrics: Dict[str, Any] = {
        "chapter_count": len(chapters),
        "collision_count": len(collisions),
        "repeated_location_count": len(repeated_locations),
        "chapters_below_3_details": sum(
            1 for d in diagnostics if d.unique_details < 3
        ),
        "chapters_without_action": sum(
            1 for d in diagnostics if not d.has_action
        ),
    }

    return SceneReport(
        status=status,
        chapter_diagnostics=diagnostics,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
    )


# ---------------------------------------------------------------------------
# Gate enforcement
# ---------------------------------------------------------------------------

def enforce_scene_gate(
    chapters: List[str],
    mode: str = "production",
) -> GateResult:
    """
    Enforce the scene anti-genericity gate.

    mode="production":
        FAIL if any chapter has < 2 unique details AND a collision is detected.
        Also FAIL on any individual SCENE_COLLISION or LOCATION_REPETITION error.
    mode="draft":
        WARN only (never blocks).

    Returns GateResult with per-chapter diagnostics.
    """
    report = check_scene_genericity(chapters)

    if mode == "draft":
        draft_status = "WARN" if (report.errors or report.warnings) else "PASS"
        return GateResult(
            status=draft_status,
            report=SceneReport(
                status=draft_status,
                chapter_diagnostics=report.chapter_diagnostics,
                errors=[],
                warnings=report.errors + report.warnings,
                metrics=report.metrics,
            ),
            mode=mode,
            blocking=False,
        )

    # Production mode
    has_collision = report.metrics.get("collision_count", 0) > 0
    has_detail_deficit = any(
        d.unique_details < 2 for d in report.chapter_diagnostics
    )

    prod_errors: List[str] = []

    if has_detail_deficit and has_collision:
        prod_errors.append(
            "PRODUCTION_BLOCK: chapter(s) with <2 unique details AND scene collision detected"
        )

    for err in report.errors:
        if "SCENE_COLLISION" in err or "LOCATION_REPETITION" in err:
            prod_errors.append(err)

    prod_warnings = [
        e for e in report.errors
        if "STATIC_SCENE" in e or "THREE_DETAIL_RULE" in e
    ]
    prod_warnings.extend(report.warnings)

    if prod_errors:
        final_status = "FAIL"
    elif prod_warnings:
        final_status = "WARN"
    else:
        final_status = "PASS"

    return GateResult(
        status=final_status,
        report=SceneReport(
            status=final_status,
            chapter_diagnostics=report.chapter_diagnostics,
            errors=prod_errors,
            warnings=prod_warnings,
            metrics=report.metrics,
        ),
        mode=mode,
        blocking=final_status == "FAIL",
    )

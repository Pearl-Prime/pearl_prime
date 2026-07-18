"""
Pearl_Editor pilot content tests — ENGINE × anxiety × gen_z_professionals.

Verifies the OPD-116/117 Tier-1 pilot atom set ("The Mechanism"):
- ANGLE_DEFINITION exists, 1,200-1,500 words
- 5 ANGLE_CALLBACK YAML files exist, each 250-350 words in body
- ENGINE journey block in registry has no TODO markers
- F2 quality: 0 bare "is." sentences in ANGLE_DEFINITION
- voice constraint: "your nervous system" appears <= 3 times in ANGLE_DEFINITION

Authority:
- docs/plans/OPD-116-117_BOOK_ANGLE_AS_JOURNEY_PLAN_2026-05-20.md (§2.1, §2.2)
- config/angles/angle_registry.yaml ENGINE entry
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PERSONA = "gen_z_professionals"
TOPIC = "anxiety"
ANGLE = "ENGINE"

ANGLE_DEFINITION_PATH = (
    REPO_ROOT / "atoms" / PERSONA / TOPIC / "ANGLE_DEFINITION" / ANGLE / "CANONICAL.txt"
)
CALLBACK_DIR = REPO_ROOT / "atoms" / PERSONA / TOPIC / "ANGLE_CALLBACK" / ANGLE
REGISTRY_PATH = REPO_ROOT / "config" / "angles" / "angle_registry.yaml"

EXPECTED_LAYERS = [1, 2, 3, 4, 5]
EXPECTED_PHASES = {
    1: "definition",
    2: "pattern_recognition",
    3: "identity_implications",
    4: "civilizational_spiritual",
    5: "transcendence_reintegration",
}
EXPECTED_CHAPTER_RANGES = {
    1: [1, 2],
    2: [3, 5],
    3: [6, 7],
    4: [8, 10],
    5: [11, 12],
}

WORD_RX = re.compile(r"\S+")


def _word_count(text: str) -> int:
    return len(WORD_RX.findall(text))


def _strip_markdown_header(text: str) -> str:
    """Strip the leading '# ...' header line so word count reflects prose only."""
    lines = text.splitlines()
    out = []
    for line in lines:
        if line.startswith("#") and not out:
            continue
        out.append(line)
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# ANGLE_DEFINITION tests
# ─────────────────────────────────────────────────────────────────────────────

def test_angle_definition_file_exists():
    assert ANGLE_DEFINITION_PATH.exists(), (
        f"ANGLE_DEFINITION missing: {ANGLE_DEFINITION_PATH}"
    )


def test_angle_definition_word_count_in_range():
    text = _strip_markdown_header(ANGLE_DEFINITION_PATH.read_text(encoding="utf-8"))
    wc = _word_count(text)
    assert 1200 <= wc <= 1500, (
        f"ANGLE_DEFINITION word count {wc} not in [1200, 1500]"
    )


def test_angle_definition_no_bare_is_sentences():
    """F2 pattern guard: no sentence ending in a bare 'is.'"""
    text = ANGLE_DEFINITION_PATH.read_text(encoding="utf-8")
    # Match any sentence ending with "<space>is." that is not preceded by other content.
    # We look for sentences like ". XYZ is." Specifically: a sentence whose final
    # token before the period is the word 'is' alone (verb with no predicate).
    sentences = re.split(r"(?<=[.!?])\s+", text)
    bare_is = [
        s for s in sentences
        if re.search(r"(^|[.\s])is\.\s*$", s.strip())
    ]
    assert bare_is == [], (
        f"Bare 'is.' sentences detected ({len(bare_is)}): "
        f"{bare_is[:3]}"
    )


def test_angle_definition_nervous_system_limit():
    """Voice constraint: 'your nervous system' appears <= 3 times."""
    text = ANGLE_DEFINITION_PATH.read_text(encoding="utf-8")
    count = len(re.findall(r"your nervous system", text, flags=re.IGNORECASE))
    assert count <= 3, (
        f"'your nervous system' appears {count} times; "
        f"voice spec says <= 3 (operator caught the over-repeat pattern earlier)"
    )


def test_angle_definition_names_the_mechanism():
    """The named object 'The Mechanism' must be introduced explicitly."""
    text = ANGLE_DEFINITION_PATH.read_text(encoding="utf-8")
    assert "The Mechanism" in text, "Named object 'The Mechanism' missing from definition"


def test_angle_definition_includes_gen_z_anchors():
    """At least 4 of the gen-z professional scene anchors should appear."""
    text = ANGLE_DEFINITION_PATH.read_text(encoding="utf-8")
    anchors = [
        "Slack", "OKR", "LinkedIn", "demo", "standup",
        "design crit", "comp band", "code review",
    ]
    found = [a for a in anchors if a.lower() in text.lower()]
    assert len(found) >= 4, (
        f"Only {len(found)} gen-z anchors found: {found}; expected >= 4"
    )


# ─────────────────────────────────────────────────────────────────────────────
# ANGLE_CALLBACK tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("layer", EXPECTED_LAYERS)
def test_callback_file_exists(layer: int):
    path = CALLBACK_DIR / f"level_{layer}.yaml"
    assert path.exists(), f"ANGLE_CALLBACK L{layer} missing: {path}"


@pytest.mark.parametrize("layer", EXPECTED_LAYERS)
def test_callback_required_fields(layer: int):
    path = CALLBACK_DIR / f"level_{layer}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    for field in ("atom_id", "angle_id", "layer", "phase", "chapter_range", "body", "synthesis_method"):
        assert field in data, f"L{layer} missing field: {field}"
    assert data["angle_id"] == ANGLE
    assert int(data["layer"]) == layer
    assert data["phase"] == EXPECTED_PHASES[layer]
    assert list(data["chapter_range"]) == EXPECTED_CHAPTER_RANGES[layer]


@pytest.mark.parametrize("layer", EXPECTED_LAYERS)
def test_callback_body_word_count(layer: int):
    path = CALLBACK_DIR / f"level_{layer}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    body = str(data.get("body") or "")
    wc = _word_count(body)
    assert 250 <= wc <= 350, (
        f"L{layer} body word count {wc} not in [250, 350]"
    )


@pytest.mark.parametrize("layer", EXPECTED_LAYERS)
def test_callback_memory_line_prefix(layer: int):
    """3-move structure: each callback opens with a memory-line ('Earlier I said...')."""
    path = CALLBACK_DIR / f"level_{layer}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    body = str(data.get("body") or "")
    first_para = body.strip().split("\n\n", 1)[0].strip().lower()
    assert "earlier" in first_para, (
        f"L{layer} memory-line prefix missing; first paragraph: {first_para[:120]!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Registry tests
# ─────────────────────────────────────────────────────────────────────────────

def test_engine_journey_has_no_todo_markers():
    """ENGINE journey block must be fully populated — no TODO placeholders."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    engine = data["angles"]["ENGINE"]
    journey = engine.get("journey", {})

    # Mantras: no TODO strings, at least 3
    mantras = journey.get("core_mantras") or []
    assert len(mantras) >= 3, f"ENGINE mantras count {len(mantras)} < 3"
    todo_mantras = [m for m in mantras if "TODO" in str(m)]
    assert todo_mantras == [], f"ENGINE has TODO mantras: {todo_mantras}"

    # Layer progression: every assertion must be non-TODO
    for lp in journey.get("layer_progression", []):
        assert "TODO" not in str(lp.get("assertion") or ""), (
            f"ENGINE L{lp.get('layer')} assertion still TODO: {lp.get('assertion')!r}"
        )


def test_engine_anxiety_named_object():
    """ENGINE.journey.named_object_by_topic.anxiety must be 'The Mechanism'."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    engine = data["angles"]["ENGINE"]
    named = engine["journey"]["named_object_by_topic"].get("anxiety")
    assert named == "The Mechanism", (
        f"ENGINE.journey.named_object_by_topic.anxiety = {named!r}; "
        f"expected 'The Mechanism'"
    )


def test_engine_mantras_align_with_pilot_content():
    """The six operator-specified mantras must be present in the registry."""
    expected_mantras = {
        "It's not YOU. It's The Mechanism.",
        "The Mechanism speaks in your voice.",
        "The Mechanism turns temporary pain into permanent identity.",
        "Awareness interrupts The Mechanism.",
        "The moment you can observe it, you are already larger than it.",
        "The doorway opens the moment observation returns.",
    }
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    mantras = set(data["angles"]["ENGINE"]["journey"]["core_mantras"])
    missing = expected_mantras - mantras
    assert not missing, f"Missing ENGINE mantras: {missing}"

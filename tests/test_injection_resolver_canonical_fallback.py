"""Tests for chapter/section-aware canonical fallback in injection_resolver.

Covers the fix in `phoenix_v4/planning/injection_resolver.py` for the
dedupe-leak diagnosis (artifacts/qa/dedupe_leak_diagnosis_2026-05-16.md,
patch (b)) — the canonical fallback used to read the whole CANONICAL.txt
verbatim, so every STORY slot in every chapter received the same multi-block
blob. With patch (b), CANONICAL.txt is parsed into discrete ``## ARC vNN``
atom blocks and a deterministic per-(chapter, section, seed) block is picked.

These tests are intentionally self-contained — they build synthetic
CANONICAL.txt fixtures under ``tmp_path`` so they do not rely on the canary
artifacts staying on disk.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import pytest

from phoenix_v4.planning import injection_resolver as ir
from phoenix_v4.planning.injection_resolver import (
    _split_canonical_into_atom_blocks,
    clear_exercise_registry_cache,
    resolve_injections,
)


@pytest.fixture(autouse=True)
def _clear_reg_cache():
    clear_exercise_registry_cache()
    yield
    clear_exercise_registry_cache()


# ─── Helpers ───────────────────────────────────────────────────────────────


def _build_canonical_file(persona: str, topic: str, engine: str, n_blocks: int,
                          root: Path) -> Path:
    """Author a synthetic CANONICAL.txt under ``atoms/{persona}/{topic}/{engine}/``.

    Creates ``n_blocks`` arc blocks cycling through the four primary positions
    (RECOGNITION / MECHANISM_PROOF / TURNING_POINT / EMBODIMENT) so every
    chapter band in a 12-chapter book has at least one matching block. Each
    block's body is a unique long string so tests can assert which block was
    chosen.
    """
    arc_cycle = [
        "RECOGNITION",
        "MECHANISM_PROOF",
        "TURNING_POINT",
        "EMBODIMENT",
    ]
    parts = [""]
    for i in range(n_blocks):
        arc = arc_cycle[i % len(arc_cycle)]
        variant = f"v{i + 1:02d}"
        body_marker = f"BLOCK_{arc}_{variant}_BODY_MARKER"
        body_words = " ".join(f"w{k}" for k in range(30))
        parts.append(
            f"## {arc} {variant}\n"
            f"---\n"
            f"path: synthetic/{arc.lower()}/{variant}.txt\n"
            f"BAND: 2\n"
            f"---\n"
            f"{body_marker} {body_words}\n"
            f"---\n"
        )
    text = "\n".join(parts)
    canonical = root / "atoms" / persona / topic / engine / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(text, encoding="utf-8")
    return canonical


def _resolve(root: Path, *, chapter: int, section: int, seed: str,
             persona: str = "test_persona",
             topic: str = "test_topic") -> Tuple[str, list]:
    """Run resolve_injections with the test fixture as repo_root.

    Returns ``(text, sources_used)``.
    """
    out = resolve_injections(
        "[STORY_INJECTION_POINT]",
        chapter_index=chapter,
        section_index=section,
        section_type="SCENE",
        topic=topic,
        persona_id=persona,
        teacher_id=None,
        exercise_phase=None,
        seed=f"{seed}:inject:{chapter}:{section}",
        repo_root=root,
    )
    return out["text"], out["sources_used"]


# ─── Parser-level tests ────────────────────────────────────────────────────


def test_split_canonical_parses_five_arc_blocks():
    """Five sequential RECOGNITION blocks should yield five entries with
    distinct variants and bodies."""
    text = ""
    for i in range(1, 6):
        text += (
            f"## RECOGNITION v0{i}\n"
            f"---\n"
            f"meta: line\n"
            f"---\n"
            f"This is body number {i}. " + " ".join(f"f{j}" for j in range(20)) + "\n"
            f"---\n\n"
        )
    blocks = _split_canonical_into_atom_blocks(text)
    assert len(blocks) == 5
    assert [b["variant"] for b in blocks] == ["v01", "v02", "v03", "v04", "v05"]
    assert all(b["arc_position"] == "recognition" for b in blocks)
    # Bodies preserved
    assert "This is body number 1." in blocks[0]["text"]
    assert "This is body number 5." in blocks[4]["text"]


def test_split_canonical_handles_mixed_arc_positions():
    """Mixed arc positions in source order should be preserved."""
    text = (
        "## RECOGNITION v01\n---\nmeta\n---\nbody_a\n---\n\n"
        "## MECHANISM_PROOF v01\n---\nmeta\n---\nbody_b\n---\n\n"
        "## TURNING_POINT v01\n---\nmeta\n---\nbody_c\n---\n\n"
        "## EMBODIMENT v01\n---\nmeta\n---\nbody_d\n---\n\n"
        "## COST_REVEAL v01\n---\nmeta\n---\nbody_e\n---\n\n"
        "## RECKONING v01\n---\nmeta\n---\nbody_f\n---\n"
    )
    blocks = _split_canonical_into_atom_blocks(text)
    arcs = [b["arc_position"] for b in blocks]
    assert arcs == [
        "recognition", "mechanism_proof", "turning_point",
        "embodiment", "cost_reveal", "reckoning",
    ]


def test_split_canonical_returns_empty_for_plain_prose():
    """A plain-prose file without the ``## ARC vNN`` headers returns []."""
    text = "Just a paragraph of prose with no headers.\n\nAnother paragraph."
    assert _split_canonical_into_atom_blocks(text) == []


def test_split_canonical_empty_input():
    assert _split_canonical_into_atom_blocks("") == []
    assert _split_canonical_into_atom_blocks(None) == []  # type: ignore[arg-type]


# ─── Resolver-level tests ──────────────────────────────────────────────────


def test_different_sections_select_different_blocks(tmp_path: Path):
    """Same chapter, different section → different blocks. Closes the leak."""
    _build_canonical_file("test_persona", "test_topic", "engine_a", 5, tmp_path)

    texts = set()
    sources = set()
    for sec in range(1, 11):
        text, srcs = _resolve(tmp_path, chapter=1, section=sec, seed="diverse")
        texts.add(text)
        sources.update(srcs)
    # With 5 blocks (only the recognition ones match arc_position for ch1),
    # we expect at least 2 distinct picks across 10 sections. In practice the
    # deterministic index will spread the 10 picks across the available
    # candidate pool.
    # Specifically: ch1 → arc_pos=recognition → 2 of 5 blocks match
    # (v01, v05 with our cycling). We assert at least 2 distinct texts.
    assert len(texts) >= 2, (
        f"Expected per-section variation, got {len(texts)} unique block(s) "
        f"across 10 sections"
    )
    # Source string includes arc_position and variant — sanity check.
    assert any(":recognition:" in s for s in sources)


def test_different_chapters_select_different_arc_positions(tmp_path: Path):
    """Chapter 1 (recognition band) and chapter 10 (embodiment band) should
    select blocks from different arc positions when both exist."""
    _build_canonical_file("test_persona", "test_topic", "engine_a", 8, tmp_path)

    _, srcs_ch1 = _resolve(tmp_path, chapter=1, section=1, seed="phase_sep")
    _, srcs_ch10 = _resolve(tmp_path, chapter=10, section=1, seed="phase_sep")

    assert any(":recognition:" in s for s in srcs_ch1), (
        f"Chapter 1 should match recognition arc, got sources: {srcs_ch1}"
    )
    assert any(":embodiment:" in s for s in srcs_ch10), (
        f"Chapter 10 should match embodiment arc, got sources: {srcs_ch10}"
    )


def test_determinism_same_seed_returns_same_block(tmp_path: Path):
    """Same (chapter, section, seed) returns the same block on repeated calls."""
    _build_canonical_file("test_persona", "test_topic", "engine_a", 5, tmp_path)

    a, srcs_a = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    b, srcs_b = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    c, srcs_c = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    assert a == b == c
    assert srcs_a == srcs_b == srcs_c


def test_different_seeds_can_diverge(tmp_path: Path):
    """Different book-level seeds produce different deterministic picks for
    at least some (chapter, section) tuples — proving the seed actually
    threads into the canonical pick."""
    _build_canonical_file("test_persona", "test_topic", "engine_a", 5, tmp_path)

    diffs = 0
    for sec in range(1, 11):
        a, _ = _resolve(tmp_path, chapter=1, section=sec, seed="seed_alpha")
        b, _ = _resolve(tmp_path, chapter=1, section=sec, seed="seed_beta")
        if a != b:
            diffs += 1
    assert diffs >= 1, (
        "Expected at least one (chapter, section) to diverge across seeds; "
        "got 0 — the seed may not be threading through to the pick"
    )


def test_single_block_canonical_returns_same_block_for_all_sections(tmp_path: Path):
    """A CANONICAL.txt with a single ARC block falls back to that one block
    for every (chapter, section). Pre-patch behavior preserved for the
    gen_z_professionals case (where story_atoms shadow the canonical anyway).
    """
    persona, topic, engine = "single_block_persona", "single_topic", "engine_x"
    text = (
        "## RECOGNITION v01\n---\nmeta\n---\n"
        + "ONLY_BLOCK_MARKER " + " ".join(f"w{i}" for i in range(30))
        + "\n---\n"
    )
    canonical = tmp_path / "atoms" / persona / topic / engine / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(text, encoding="utf-8")

    bodies = set()
    for sec in range(1, 5):
        body, _ = _resolve(
            tmp_path, chapter=1, section=sec, seed="single",
            persona=persona, topic=topic,
        )
        bodies.add(body)
    assert len(bodies) == 1
    assert "ONLY_BLOCK_MARKER" in next(iter(bodies))


def test_plain_prose_canonical_emits_degraded_log(tmp_path: Path, caplog):
    """A CANONICAL.txt without any ``## ARC vNN`` headers (plain prose) falls
    back to the verbatim-paste behavior AND emits a [canonical_fallback]
    warning log so the degradation is visible in production telemetry.
    """
    persona, topic, engine = "plain_persona", "plain_topic", "engine_y"
    body = (
        "PLAIN_PROSE_MARKER This is a long plain-prose canonical file "
        "without the structured ARC vNN convention. " + " ".join(
            f"w{i}" for i in range(40)
        )
    )
    canonical = tmp_path / "atoms" / persona / topic / engine / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(body, encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="phoenix_v4.planning.injection_resolver"):
        text, _ = _resolve(
            tmp_path, chapter=1, section=1, seed="plain",
            persona=persona, topic=topic,
        )
    assert "PLAIN_PROSE_MARKER" in text
    # Telemetry: degradation must be visible in logs.
    assert any(
        "[canonical_fallback] no ARC blocks found" in r.getMessage()
        for r in caplog.records
    ), f"Expected degraded-behavior warning; got logs: {[r.getMessage() for r in caplog.records]}"


def test_chapter_section_selection_log_emitted(tmp_path: Path, caplog):
    """For a normal (parseable) CANONICAL.txt, an INFO log records which
    arc-block was selected — production telemetry for the patch."""
    _build_canonical_file("test_persona", "test_topic", "engine_a", 5, tmp_path)
    with caplog.at_level(logging.INFO, logger="phoenix_v4.planning.injection_resolver"):
        _resolve(tmp_path, chapter=2, section=3, seed="telemetry")
    assert any(
        "[canonical_fallback] selected" in r.getMessage()
        and "chapter 2 section 3" in r.getMessage()
        for r in caplog.records
    ), f"Expected selection telemetry; got logs: {[r.getMessage() for r in caplog.records]}"


def test_book_wide_variation_simulates_canary_shape(tmp_path: Path):
    """End-to-end shape check: simulate a 12-chapter × 3-SCENE-slot book
    against a 5-block CANONICAL.txt and assert no single block dominates
    the way it did pre-patch.

    Pre-patch behavior: the whole-file blob (containing the marker for every
    block) was injected 36 times. Post-patch: each slot gets exactly one
    block. With 5 candidate blocks distributed over 12 chapters × 3 sections,
    no single block should appear more than ~12 times (which would be the
    degenerate case of one-block-per-chapter from pre-patch).
    """
    _build_canonical_file("test_persona", "test_topic", "engine_a", 5, tmp_path)

    from collections import Counter
    body_counts: Counter = Counter()
    for ch in range(1, 13):
        for sec in range(1, 4):
            body, _ = _resolve(tmp_path, chapter=ch, section=sec, seed="canary_shape")
            body_counts[body] += 1

    most_common = body_counts.most_common(1)[0]
    # 36 slots, 5 candidate blocks → uniform-ish ~7-8 per block. Allow some
    # slack; the failure mode we're guarding against is a single block taking
    # 16+ of 36 slots (the pre-patch leak).
    assert most_common[1] <= 14, (
        f"Pre-patch leak shape detected: one block consumed {most_common[1]} of "
        f"36 slots. Distribution: {dict(body_counts)}"
    )
    # And we should see at least 3 distinct bodies in a 36-slot book.
    assert len(body_counts) >= 3, (
        f"Insufficient block variety: only {len(body_counts)} distinct picks "
        f"across 36 slots"
    )

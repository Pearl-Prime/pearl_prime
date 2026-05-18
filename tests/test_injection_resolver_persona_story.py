"""Tests for chapter/section-aware persona_story branch in injection_resolver.

Covers patch (c) of the dedupe-leak diagnosis
(artifacts/qa/dedupe_leak_diagnosis_2026-05-16.md): the persona_story branch
in `phoenix_v4/planning/injection_resolver.py` used to read the entire
``atoms/{persona}/{topic}/STORY/CANONICAL.txt`` and paste it verbatim into
every SCENE slot in the book, **shadowing patch (b) entirely** because the
canonical-engine fallback branch never even gets a chance to run when
STORY/CANONICAL.txt exists. The integration smoke on 2026-05-16 surfaced
this bypass — every chapter/section still received the same blob.

With patch (c), STORY/CANONICAL.txt is parsed via
``_split_canonical_into_atom_blocks`` (the helper from patch b in PR #1137)
and a deterministic per-(chapter, section, seed) block is picked — mirroring
patch (b)'s shape but for the persona_story code path. Plain-prose
STORY/CANONICAL.txt files without the ``## ARC vNN`` convention fall back to
verbatim paste AND emit a ``[persona_story] no ARC blocks found`` WARNING
log so the degradation is visible in production telemetry.

These tests are intentionally self-contained — they build synthetic
STORY/CANONICAL.txt fixtures under ``tmp_path`` so they do not rely on the
canary artifacts staying on disk.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import pytest

from phoenix_v4.planning import injection_resolver as ir
from phoenix_v4.planning.injection_resolver import (
    clear_exercise_registry_cache,
    resolve_injections,
)


@pytest.fixture(autouse=True)
def _clear_reg_cache():
    clear_exercise_registry_cache()
    yield
    clear_exercise_registry_cache()


# ─── Helpers ───────────────────────────────────────────────────────────────


def _build_persona_story_file(persona: str, topic: str, n_blocks: int,
                              root: Path) -> Path:
    """Author a synthetic STORY/CANONICAL.txt under
    ``atoms/{persona}/{topic}/STORY/CANONICAL.txt``.

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
        body_marker = f"PSTORY_BLOCK_{arc}_{variant}_BODY_MARKER"
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
    canonical = root / "atoms" / persona / topic / "STORY" / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(text, encoding="utf-8")
    return canonical


def _resolve(root: Path, *, chapter: int, section: int, seed: str,
             persona: str = "ps_persona",
             topic: str = "ps_topic") -> Tuple[str, list]:
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


# ─── Resolver-level tests for the persona_story branch ────────────────────


def test_persona_story_different_sections_select_different_blocks(tmp_path: Path):
    """Same chapter, different section → different blocks via the persona_story
    branch. Closes the integration-smoke bypass surfaced 2026-05-16.
    """
    _build_persona_story_file("ps_persona", "ps_topic", 5, tmp_path)

    texts = set()
    sources = set()
    for sec in range(1, 11):
        text, srcs = _resolve(tmp_path, chapter=1, section=sec, seed="diverse")
        texts.add(text)
        sources.update(srcs)
    # With 5 blocks (only the recognition ones match arc_position for ch1),
    # we expect at least 2 distinct picks across 10 sections — same as patch
    # (b)'s test contract. The deterministic index will spread the 10 picks
    # across the available candidate pool.
    assert len(texts) >= 2, (
        f"Expected per-section variation, got {len(texts)} unique block(s) "
        f"across 10 sections"
    )
    # Source string includes arc_position and variant — sanity check that the
    # persona_story-specific source tag is emitted.
    assert any("injection:persona_story:" in s for s in sources), (
        f"Expected injection:persona_story:<arc>:<variant> source, got: {sources}"
    )
    assert any(":recognition:" in s for s in sources)


def test_persona_story_different_chapters_select_different_arc_positions(
    tmp_path: Path,
):
    """Chapter 1 (recognition band) and chapter 10 (embodiment band) should
    select blocks from different arc positions when both exist — same
    behavior as the canonical-engine branch in patch (b).
    """
    _build_persona_story_file("ps_persona", "ps_topic", 8, tmp_path)

    _, srcs_ch1 = _resolve(tmp_path, chapter=1, section=1, seed="phase_sep")
    _, srcs_ch10 = _resolve(tmp_path, chapter=10, section=1, seed="phase_sep")

    assert any(":recognition:" in s for s in srcs_ch1), (
        f"Chapter 1 should match recognition arc, got sources: {srcs_ch1}"
    )
    assert any(":embodiment:" in s for s in srcs_ch10), (
        f"Chapter 10 should match embodiment arc, got sources: {srcs_ch10}"
    )


def test_persona_story_determinism_same_seed_returns_same_block(tmp_path: Path):
    """Same (chapter, section, seed) returns the same block on repeated calls."""
    _build_persona_story_file("ps_persona", "ps_topic", 5, tmp_path)

    a, srcs_a = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    b, srcs_b = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    c, srcs_c = _resolve(tmp_path, chapter=3, section=2, seed="determinism")
    assert a == b == c
    assert srcs_a == srcs_b == srcs_c


def test_persona_story_different_seeds_can_diverge(tmp_path: Path):
    """Different book-level seeds produce different deterministic picks for
    at least some (chapter, section) tuples — proving the seed actually
    threads into the persona_story pick.
    """
    _build_persona_story_file("ps_persona", "ps_topic", 5, tmp_path)

    diffs = 0
    for sec in range(1, 11):
        a, _ = _resolve(tmp_path, chapter=1, section=sec, seed="seed_alpha")
        b, _ = _resolve(tmp_path, chapter=1, section=sec, seed="seed_beta")
        if a != b:
            diffs += 1
    assert diffs >= 1, (
        "Expected at least one (chapter, section) to diverge across seeds; "
        "got 0 — the seed may not be threading through to the persona_story pick"
    )


def test_persona_story_single_block_returns_same_block_for_all_sections(
    tmp_path: Path,
):
    """A STORY/CANONICAL.txt with a single ARC block falls back to that one
    block for every (chapter, section). Pre-patch behavior preserved.
    """
    persona, topic = "single_ps_persona", "single_ps_topic"
    text = (
        "## RECOGNITION v01\n---\nmeta\n---\n"
        + "ONLY_PSTORY_BLOCK_MARKER " + " ".join(f"w{i}" for i in range(30))
        + "\n---\n"
    )
    canonical = tmp_path / "atoms" / persona / topic / "STORY" / "CANONICAL.txt"
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
    assert "ONLY_PSTORY_BLOCK_MARKER" in next(iter(bodies))


def test_persona_story_plain_prose_emits_degraded_log(tmp_path: Path, caplog):
    """A STORY/CANONICAL.txt without any ``## ARC vNN`` headers (plain prose)
    falls back to the verbatim-paste behavior AND emits a ``[persona_story]``
    warning log so the degradation is visible in production telemetry.
    """
    persona, topic = "plain_ps_persona", "plain_ps_topic"
    body = (
        "PLAIN_PSTORY_MARKER This is a long plain-prose persona_story canonical "
        "file without the structured ARC vNN convention. " + " ".join(
            f"w{i}" for i in range(40)
        )
    )
    canonical = tmp_path / "atoms" / persona / topic / "STORY" / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text(body, encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="phoenix_v4.planning.injection_resolver"):
        text, srcs = _resolve(
            tmp_path, chapter=1, section=1, seed="plain",
            persona=persona, topic=topic,
        )
    assert "PLAIN_PSTORY_MARKER" in text
    # Source string is the plain persona_story tag (no arc/variant suffix on the
    # degraded path).
    assert any(s == "injection:persona_story" for s in srcs), (
        f"Expected degraded-path source 'injection:persona_story', got: {srcs}"
    )
    # Telemetry: degradation must be visible in logs.
    assert any(
        "[persona_story] no ARC blocks found" in r.getMessage()
        for r in caplog.records
    ), f"Expected degraded-behavior warning; got logs: {[r.getMessage() for r in caplog.records]}"


def test_persona_story_per_section_selection_log_emitted(tmp_path: Path, caplog):
    """For a parseable STORY/CANONICAL.txt, an INFO log records which arc-block
    was selected — production telemetry for patch (c).
    """
    _build_persona_story_file("ps_persona", "ps_topic", 5, tmp_path)
    with caplog.at_level(logging.INFO, logger="phoenix_v4.planning.injection_resolver"):
        _resolve(tmp_path, chapter=2, section=3, seed="telemetry")
    assert any(
        "[persona_story_per_section] selected ARC" in r.getMessage()
        and "chapter 2 section 3" in r.getMessage()
        for r in caplog.records
    ), f"Expected per-section selection telemetry; got logs: {[r.getMessage() for r in caplog.records]}"


def test_persona_story_book_wide_variation_simulates_canary_shape(tmp_path: Path):
    """End-to-end shape check: simulate a 12-chapter × 3-SCENE-slot book
    against a 5-block STORY/CANONICAL.txt and assert no single block dominates
    the way it did pre-patch (the integration-smoke bypass).

    Pre-patch behavior: the whole STORY/CANONICAL.txt blob was injected
    verbatim into every slot. Post-patch: each slot gets exactly one block.
    With 5 candidate blocks distributed over 12 chapters × 3 sections,
    no single block should appear more than ~12 times (the degenerate case
    pre-patch would be all 36 slots receiving the same blob).
    """
    _build_persona_story_file("ps_persona", "ps_topic", 5, tmp_path)

    from collections import Counter
    body_counts: Counter = Counter()
    for ch in range(1, 13):
        for sec in range(1, 4):
            body, _ = _resolve(tmp_path, chapter=ch, section=sec, seed="canary_shape")
            body_counts[body] += 1

    most_common = body_counts.most_common(1)[0]
    # 36 slots, 5 candidate blocks → uniform-ish ~7-8 per block. Allow slack;
    # the failure mode we're guarding against is a single block taking 16+ of
    # 36 slots (the pre-patch leak).
    assert most_common[1] <= 14, (
        f"Pre-patch persona_story leak shape detected: one block consumed "
        f"{most_common[1]} of 36 slots. Distribution: {dict(body_counts)}"
    )
    # And we should see at least 3 distinct bodies in a 36-slot book.
    assert len(body_counts) >= 3, (
        f"Insufficient block variety: only {len(body_counts)} distinct picks "
        f"across 36 slots"
    )


def test_persona_story_branch_takes_priority_over_canonical_engine(tmp_path: Path):
    """When both ``atoms/{persona}/{topic}/STORY/CANONICAL.txt`` and
    ``atoms/{persona}/{topic}/<engine>/CANONICAL.txt`` exist, the
    persona_story branch fires first (matches existing pre-patch precedence).
    Patch (c) must not regress this — only change *what* the persona_story
    branch returns, not whether it runs.
    """
    persona, topic = "priority_persona", "priority_topic"
    # persona_story file (this branch should win):
    _build_persona_story_file(persona, topic, 5, tmp_path)
    # Also create a competing engine subdir with its own CANONICAL.txt:
    engine_canonical = tmp_path / "atoms" / persona / topic / "engine_a" / "CANONICAL.txt"
    engine_canonical.parent.mkdir(parents=True, exist_ok=True)
    engine_canonical.write_text(
        "## RECOGNITION v99\n---\nmeta\n---\n"
        + "ENGINE_BLOCK_SHOULD_NOT_APPEAR " + " ".join(f"w{i}" for i in range(30))
        + "\n---\n",
        encoding="utf-8",
    )

    text, srcs = _resolve(
        tmp_path, chapter=1, section=1, seed="priority",
        persona=persona, topic=topic,
    )
    # The persona_story branch wins — the engine block must not show up:
    assert "ENGINE_BLOCK_SHOULD_NOT_APPEAR" not in text
    assert "PSTORY_BLOCK_" in text
    assert any("injection:persona_story:" in s for s in srcs), (
        f"Expected persona_story source tag, got: {srcs}"
    )


def test_persona_story_zero_block_short_text_falls_through(tmp_path: Path):
    """A STORY/CANONICAL.txt that has no ARC blocks AND too few words also
    must not short-circuit; the resolver should fall through to the
    canonical-engine branch (or whatever comes next) rather than emit
    [STORY_INJECTION_POINT] verbatim.
    """
    persona, topic = "shortprose_persona", "shortprose_topic"
    canonical = tmp_path / "atoms" / persona / topic / "STORY" / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    # 5 words — below the 20-word floor.
    canonical.write_text("Not enough words here yet.", encoding="utf-8")
    # Provide an engine-dir fallback so the resolver has somewhere to land:
    engine_canonical = tmp_path / "atoms" / persona / topic / "engine_a" / "CANONICAL.txt"
    engine_canonical.parent.mkdir(parents=True, exist_ok=True)
    engine_canonical.write_text(
        "## RECOGNITION v01\n---\nmeta\n---\n"
        + "ENGINE_FALLBACK_MARKER " + " ".join(f"w{i}" for i in range(30))
        + "\n---\n",
        encoding="utf-8",
    )

    text, srcs = _resolve(
        tmp_path, chapter=1, section=1, seed="shortprose",
        persona=persona, topic=topic,
    )
    # Should NOT contain the short prose verbatim:
    assert "Not enough words here yet." not in text
    # SHOULD have fallen through to the engine_a canonical:
    assert "ENGINE_FALLBACK_MARKER" in text
    assert any("injection:persona_engine:engine_a" in s for s in srcs)

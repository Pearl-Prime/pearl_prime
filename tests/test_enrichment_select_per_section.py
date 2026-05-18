"""Tests for patch (d) of the dedupe-leak diagnosis — per-section ARC block
selection in ``phoenix_v4.planning.enrichment_select``.

Closes the spine-mode dedupe-leak that surfaced as the 9× Tanya / Sarah verbatim
paragraph repeats in Integration Smoke #2:

    artifacts/qa/integration_smoke_v2_2026-05-16.md
    artifacts/canary/integration_smoke_v2_2026-05-16/
        anxiety_corporate_managers_ahjan/selected_content_variants.json

Integration Smoke #2 confirmed that patches (b) (PR #1137) and (c) (PR #1140)
are DEAD CODE in spine mode — the spine pipeline routes STORY/SCENE-class
content through ``enrichment_select.py`` (``persona_atom`` / ``teacher_atom``
slot types via ``_load_depth_content``), not through
``injection_resolver.resolve_injections._find_story_content``. Patch (d) ports
patch (b)'s per-section ARC-block selection logic into the actual spine
resolution path.

These tests cover:
  - _split_canonical_into_atom_blocks parser correctness
  - per-section variation (different sections within the same chapter pick
    different ARC blocks)
  - determinism (same input → same output)
  - single-block fallback (1 ARC block file: paste it verbatim)
  - plain-prose fallback (0 ARC blocks: degraded WARNING + None return)
  - INFO telemetry emission ([enrichment_per_section] selected ...)
  - end-to-end _load_depth_content persona_atom branch picks distinct bodies
    per (chapter, section)
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

from phoenix_v4.planning.enrichment_select import (
    _chapter_to_arc_position_patch_d,
    _load_depth_content,
    _pick_canonical_block_per_section,
    _split_canonical_into_atom_blocks,
)


# ── Test fixtures ────────────────────────────────────────────────────────────


_SYNTHETIC_5_BLOCK_CANONICAL = """\
## RECOGNITION v01
---
path: synthetic/recognition/v01
BAND: 1
---
Recognition body one. Lorem ipsum dolor sit amet consectetur adipiscing elit.
---

## RECOGNITION v02
---
path: synthetic/recognition/v02
BAND: 2
---
Recognition body two. The second recognition variant. Sed do eiusmod tempor.
---

## MECHANISM_PROOF v01
---
path: synthetic/mechanism_proof/v01
BAND: 3
---
Mechanism proof body one. Incididunt ut labore et dolore magna aliqua.
---

## TURNING_POINT v01
---
path: synthetic/turning_point/v01
BAND: 4
---
Turning point body one. Ut enim ad minim veniam quis nostrud exercitation.
---

## EMBODIMENT v01
---
path: synthetic/embodiment/v01
BAND: 5
---
Embodiment body one. Ullamco laboris nisi ut aliquip ex ea commodo consequat.
---
"""


_SINGLE_BLOCK_CANONICAL = """\
## RECOGNITION v01
---
path: synthetic/recognition/v01
BAND: 1
---
The only recognition body in this synthetic file. Lorem ipsum dolor sit amet.
---
"""


_PLAIN_PROSE_CANONICAL = """\
Some plain prose paragraph with no headers.

Another plain prose paragraph still with no headers.

Third paragraph also lacking the ## ARC vNN structure.
"""


# ── Parser tests ─────────────────────────────────────────────────────────────


def test_split_returns_all_five_blocks():
    blocks = _split_canonical_into_atom_blocks(_SYNTHETIC_5_BLOCK_CANONICAL)
    assert len(blocks) == 5
    arc_positions = [b["arc_position"] for b in blocks]
    assert arc_positions == [
        "recognition", "recognition", "mechanism_proof",
        "turning_point", "embodiment",
    ]
    variants = [b["variant"] for b in blocks]
    assert variants == ["v01", "v02", "v01", "v01", "v01"]
    # Bodies are the prose only (no header, no metadata, no trailing `---`).
    assert "Recognition body one" in blocks[0]["text"]
    assert "Recognition body two" in blocks[1]["text"]
    assert "Mechanism proof body one" in blocks[2]["text"]
    assert "Turning point body one" in blocks[3]["text"]
    assert "Embodiment body one" in blocks[4]["text"]
    # Header lines must NOT be in the body.
    assert "## RECOGNITION" not in blocks[0]["text"]
    # YAML metadata must NOT be in the body.
    assert "BAND:" not in blocks[0]["text"]
    assert "path:" not in blocks[0]["text"]


def test_split_returns_empty_for_plain_prose():
    blocks = _split_canonical_into_atom_blocks(_PLAIN_PROSE_CANONICAL)
    assert blocks == []


def test_split_returns_empty_for_empty_input():
    assert _split_canonical_into_atom_blocks("") == []
    assert _split_canonical_into_atom_blocks("   \n  \n") == []


def test_split_single_block_returns_one():
    blocks = _split_canonical_into_atom_blocks(_SINGLE_BLOCK_CANONICAL)
    assert len(blocks) == 1
    assert blocks[0]["arc_position"] == "recognition"
    assert blocks[0]["variant"] == "v01"
    assert "The only recognition body" in blocks[0]["text"]


# ── _chapter_to_arc_position_patch_d ─────────────────────────────────────────


def test_chapter_to_arc_position_phases():
    # Phase 0 (chapters 1-3) → recognition
    assert _chapter_to_arc_position_patch_d(1) == "recognition"
    assert _chapter_to_arc_position_patch_d(3) == "recognition"
    # Phase 1 (chapters 4-6) → mechanism_proof
    assert _chapter_to_arc_position_patch_d(4) == "mechanism_proof"
    assert _chapter_to_arc_position_patch_d(6) == "mechanism_proof"
    # Phase 2 (chapters 7-9) → turning_point
    assert _chapter_to_arc_position_patch_d(7) == "turning_point"
    assert _chapter_to_arc_position_patch_d(9) == "turning_point"
    # Phase 3 (chapters 10-12) → embodiment
    assert _chapter_to_arc_position_patch_d(10) == "embodiment"
    assert _chapter_to_arc_position_patch_d(12) == "embodiment"
    # Out-of-range chapters clamp to ends.
    assert _chapter_to_arc_position_patch_d(0) == "recognition"
    assert _chapter_to_arc_position_patch_d(99) == "embodiment"


# ── Per-section selector tests ───────────────────────────────────────────────


def test_pick_per_section_distinct_sections_in_same_chapter(tmp_path):
    """Different (chapter, section) tuples MUST pick different ARC blocks
    when enough blocks are available.
    """
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_SYNTHETIC_5_BLOCK_CANONICAL, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    picks = []
    for sec_idx in range(10):
        block = _pick_canonical_block_per_section(
            raw, chapter_index=1, section_index=sec_idx,
            seed="test-seed-A", slot_label="depth_eng:engine_a",
            source_path=canonical,
        )
        assert block is not None
        picks.append(block["variant"])

    # Across 10 sections, we must hit at least 2 distinct variants —
    # the leak surfaced as same-content-everywhere.
    assert len(set(picks)) >= 2, f"per-section variation absent: {picks}"


def test_pick_per_section_determinism(tmp_path):
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_SYNTHETIC_5_BLOCK_CANONICAL, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    a = _pick_canonical_block_per_section(
        raw, chapter_index=5, section_index=3,
        seed="seed-X", slot_label="depth_eng:engine_b",
        source_path=canonical,
    )
    b = _pick_canonical_block_per_section(
        raw, chapter_index=5, section_index=3,
        seed="seed-X", slot_label="depth_eng:engine_b",
        source_path=canonical,
    )
    assert a == b


def test_pick_per_section_seed_sensitivity(tmp_path):
    """Different seeds with the same (chapter, section) coords produce
    different picks at least at the chapter-band where the file has 2+
    candidates for that arc_position. Sanity check, not a strict guarantee
    — chapter-bands with only 1 matching candidate cannot vary.
    """
    canonical = tmp_path / "CANONICAL.txt"
    # Use a fixture with MULTIPLE blocks per arc_position so the seed can
    # actually drive variation when chapter_to_arc_position_patch_d picks
    # one of the multi-variant positions.
    multi_variant = """\
## RECOGNITION v01
---
band: 1
---
Recognition body one prose text.
---

## RECOGNITION v02
---
band: 1
---
Recognition body two prose text.
---

## RECOGNITION v03
---
band: 1
---
Recognition body three prose text.
---

## MECHANISM_PROOF v01
---
band: 2
---
Mechanism body one.
---

## MECHANISM_PROOF v02
---
band: 2
---
Mechanism body two.
---

## MECHANISM_PROOF v03
---
band: 2
---
Mechanism body three.
---

## TURNING_POINT v01
---
band: 3
---
Turning body one.
---

## TURNING_POINT v02
---
band: 3
---
Turning body two.
---

## EMBODIMENT v01
---
band: 4
---
Embodiment body one.
---

## EMBODIMENT v02
---
band: 4
---
Embodiment body two.
---
"""
    canonical.write_text(multi_variant, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    seed_a_picks = []
    seed_b_picks = []
    for ch in range(1, 13):
        for sec in range(12):
            a = _pick_canonical_block_per_section(
                raw, chapter_index=ch, section_index=sec,
                seed="seed-A", slot_label="depth", source_path=canonical,
            )
            b = _pick_canonical_block_per_section(
                raw, chapter_index=ch, section_index=sec,
                seed="seed-B", slot_label="depth", source_path=canonical,
            )
            seed_a_picks.append(a["variant"])
            seed_b_picks.append(b["variant"])
    differing = sum(1 for x, y in zip(seed_a_picks, seed_b_picks) if x != y)
    # >= 10% of slots should differ between seeds when candidates are plural.
    assert differing >= 14, f"seed_A and seed_B picks too similar: {differing}/144 differ"


def test_pick_per_section_single_block_pastes_verbatim(tmp_path, caplog):
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_SINGLE_BLOCK_CANONICAL, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    with caplog.at_level(logging.INFO, logger="phoenix_v4.planning.enrichment_select"):
        block = _pick_canonical_block_per_section(
            raw, chapter_index=1, section_index=0,
            seed="seed-Y", slot_label="depth_eng:engine_solo",
            source_path=canonical,
        )
    assert block is not None
    assert block["variant"] == "v01"
    assert "The only recognition body" in block["text"]
    # INFO telemetry must include "single-block file" annotation.
    info_msgs = [
        r.message for r in caplog.records
        if r.levelname == "INFO" and "[enrichment_per_section]" in r.message
    ]
    assert any("single-block file" in m for m in info_msgs), (
        f"missing single-block INFO log; got: {info_msgs}"
    )


def test_pick_per_section_zero_blocks_warns_and_returns_none(tmp_path, caplog):
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_PLAIN_PROSE_CANONICAL, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="phoenix_v4.planning.enrichment_select"):
        result = _pick_canonical_block_per_section(
            raw, chapter_index=1, section_index=0,
            seed="seed-Z", slot_label="depth_eng:engine_plain",
            source_path=canonical,
        )
    assert result is None
    warn_msgs = [
        r.message for r in caplog.records
        if r.levelname == "WARNING" and "[enrichment_per_section]" in r.message
    ]
    assert any("no ARC blocks parsed" in m for m in warn_msgs), (
        f"missing degraded WARNING; got: {warn_msgs}"
    )


def test_pick_per_section_emits_info_telemetry(tmp_path, caplog):
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(_SYNTHETIC_5_BLOCK_CANONICAL, encoding="utf-8")
    raw = canonical.read_text(encoding="utf-8")

    with caplog.at_level(logging.INFO, logger="phoenix_v4.planning.enrichment_select"):
        _pick_canonical_block_per_section(
            raw, chapter_index=4, section_index=2,
            seed="seed-W", slot_label="depth_eng:engine_w",
            source_path=canonical,
        )
    info_msgs = [
        r.message for r in caplog.records
        if r.levelname == "INFO" and "[enrichment_per_section]" in r.message
    ]
    assert info_msgs, "expected at least one [enrichment_per_section] INFO log"
    last = info_msgs[-1]
    assert "chapter 4" in last
    assert "section 2" in last
    assert "depth_eng:engine_w" in last


# ── End-to-end _load_depth_content tests ─────────────────────────────────────


def test_load_depth_content_persona_atom_per_section(tmp_path):
    """Synthetic atoms tree → _load_depth_content with persona_atom source
    type returns DIFFERENT bodies for the same chapter at different
    section_index values."""
    persona = "synth_persona"
    topic = "synth_topic"
    engine_dir = tmp_path / "atoms" / persona / topic / "engine_a"
    engine_dir.mkdir(parents=True, exist_ok=True)
    (engine_dir / "CANONICAL.txt").write_text(
        _SYNTHETIC_5_BLOCK_CANONICAL, encoding="utf-8",
    )

    seed = "depth:synth_topic:1:recognition_depth:r0:res"
    src = {"type": "persona_atom", "slot_types": []}
    bodies = []
    for sec_idx in range(8):
        body = _load_depth_content(
            source=src, topic=topic, teacher_id=None, persona_id=persona,
            chapter_number=1, seed=seed, repo_root=tmp_path,
            book_seen_bodies=None, locale=None,
            section_index=sec_idx,
        )
        bodies.append(body)
    distinct = {b for b in bodies if b}
    # Pre-patch behavior: same chunk in every call.
    # Post-patch: at least 2 distinct bodies across the 8 sections.
    assert len(distinct) >= 2, (
        f"persona_atom depth content not varying per section: {distinct}"
    )


def test_load_depth_content_teacher_atom_per_section(tmp_path):
    """teacher_atom branch now varies idx per section_index."""
    teacher = "synth_teacher"
    slot_type = "DEPTH_TEACHER"
    bank_dir = tmp_path / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher / "approved_atoms" / slot_type
    bank_dir.mkdir(parents=True, exist_ok=True)
    # Author 4 distinct teacher atoms with sufficient word counts.
    for i in range(4):
        (bank_dir / f"atom_{i:02d}.yaml").write_text(
            "body: " + "word " * 25 + f"unique_{i}\n", encoding="utf-8",
        )

    seed = "depth:synth_topic:1:recognition_depth:r0:res"
    src = {"type": "teacher_atom", "slot_types": [slot_type]}
    bodies = []
    for sec_idx in range(6):
        body = _load_depth_content(
            source=src, topic="synth_topic", teacher_id=teacher,
            persona_id="synth_persona",
            chapter_number=1, seed=seed, repo_root=tmp_path,
            book_seen_bodies=None, locale=None,
            section_index=sec_idx,
        )
        bodies.append(body)
    # Different section_idx should hit different YAMLs (post-patch).
    distinct = {b for b in bodies if b}
    assert len(distinct) >= 2, (
        f"teacher_atom depth content not varying per section: {distinct}"
    )


def test_load_depth_content_persona_atom_single_block(tmp_path):
    """Single-block CANONICAL.txt: depth content returns that single body
    rather than the prose-chunk legacy path."""
    persona = "synth_persona"
    topic = "synth_topic"
    engine_dir = tmp_path / "atoms" / persona / topic / "engine_solo"
    engine_dir.mkdir(parents=True, exist_ok=True)
    (engine_dir / "CANONICAL.txt").write_text(
        _SINGLE_BLOCK_CANONICAL, encoding="utf-8",
    )
    seed = "depth:synth_topic:1:recognition_depth:r0:res"
    src = {"type": "persona_atom", "slot_types": []}
    body = _load_depth_content(
        source=src, topic=topic, teacher_id=None, persona_id=persona,
        chapter_number=1, seed=seed, repo_root=tmp_path,
        book_seen_bodies=None, locale=None, section_index=0,
    )
    assert body is not None
    assert "The only recognition body" in body
    assert "## RECOGNITION" not in body  # header stripped


def test_load_depth_content_persona_atom_plain_prose_emits_warning(tmp_path, caplog):
    """Plain-prose CANONICAL.txt (no ## ARC vNN headers): a WARNING is
    emitted so the degraded fallback is visible. The function may return
    None when even the legacy ``_extract_prose_from_canonical`` cannot
    extract a usable chunk (that helper requires ``## TYPE vNN`` headers
    to split prose), which mirrors the pre-patch behavior.
    """
    persona = "synth_persona"
    topic = "synth_topic"
    engine_dir = tmp_path / "atoms" / persona / topic / "engine_plain"
    engine_dir.mkdir(parents=True, exist_ok=True)
    # Make the plain prose long enough to satisfy _select_prose_chunk's min_words.
    plain_text = (
        "First plain prose paragraph " + ("alpha " * 25) + "end.\n\n"
        "Second plain prose paragraph " + ("beta " * 25) + "end.\n\n"
        "Third plain prose paragraph " + ("gamma " * 25) + "end.\n"
    )
    (engine_dir / "CANONICAL.txt").write_text(plain_text, encoding="utf-8")
    seed = "depth:synth_topic:1:recognition_depth:r0:res"
    src = {"type": "persona_atom", "slot_types": []}
    with caplog.at_level(logging.WARNING, logger="phoenix_v4.planning.enrichment_select"):
        _ = _load_depth_content(
            source=src, topic=topic, teacher_id=None, persona_id=persona,
            chapter_number=1, seed=seed, repo_root=tmp_path,
            book_seen_bodies=None, locale=None, section_index=0,
        )
    warn_msgs = [
        r.message for r in caplog.records
        if r.levelname == "WARNING" and "[enrichment_per_section]" in r.message
    ]
    assert any("no ARC blocks parsed" in m for m in warn_msgs), (
        f"missing degraded WARNING; got: {warn_msgs}"
    )


# ── Canary parity tests (uses the real ja-JP CANONICAL.txt if present) ───────


def test_canary_ja_jp_spiral_per_section_variation():
    """Pin the canary regression: the spiral ja-JP CANONICAL.txt MUST yield
    distinct bodies across the 12 chapters × 3 STORY-section grid.

    Skipped when the scrubbed-atoms tree is not present in the worktree.
    """
    canary = Path(
        "/Users/ahjan/phoenix_omega/.claude/worktrees/compassionate-goodall-344d56/"
        "atoms/corporate_managers/anxiety/spiral/locales/ja-JP/CANONICAL.txt"
    )
    if not canary.exists():
        pytest.skip(f"canary file not present: {canary}")
    raw = canary.read_text(encoding="utf-8")
    blocks = _split_canonical_into_atom_blocks(raw)
    # Real file has > 5 ARC blocks.
    assert len(blocks) >= 5

    seed = "depth:anxiety:1:recognition_depth:r0:res"
    picks = []
    for ch in range(1, 13):
        for sec in (1, 4, 8):  # SCENE_SECTION_INDICES rough proxy
            block = _pick_canonical_block_per_section(
                raw, chapter_index=ch, section_index=sec,
                seed=seed, slot_label="depth_eng:spiral",
                source_path=canary,
            )
            assert block is not None
            picks.append((ch, sec, block["arc_position"], block["variant"]))
    distinct_variants = {(p[2], p[3]) for p in picks}
    # Pre-patch the leak surfaced as ~1 unique body across all 36 slots.
    # Post-patch we expect > 5 distinct ARC blocks selected across the grid.
    assert len(distinct_variants) >= 5, (
        f"canary parity failed — only {len(distinct_variants)} distinct ARC "
        f"variants selected across 36 slots; picks={picks[:8]}…"
    )

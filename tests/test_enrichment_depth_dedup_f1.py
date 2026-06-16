"""Regression tests for the cross-chapter fuzzy depth-dedup.

ws_f1_depth_dedup_20260615 (task_48b619ed).

The depth pass (``apply_depth_pass``) used to keep a PER-CHAPTER exact-match
``book_seen_bodies`` set, so the same atom body (HOOK v02 "The task is open",
EXERCISE / doctrine blocks) was re-injected across every chapter — the bulk of
the full-12 F1 mass (⑤ leverB attribution: 223/224 deep-tier clusters). The fix
makes the registry BOOK-WIDE and FUZZY (Jaccard ≥ threshold, mirroring the
register-gate F1 detector) so a near-duplicate body is rejected and the selector
rotates to an unused sibling block/variant instead.

These tests exercise the new ``_SeenBodies`` registry and the
``_pick_canonical_block_per_section`` sibling rotation directly (fast, no full
render). The end-to-end book-level F1 drop is proven separately by
``artifacts/qa/f1_depth_dedup_20260615/gen_proof.py``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning.enrichment_select import (
    _SeenBodies,
    _pick_canonical_block_per_section,
    _seen_similar,
)

# A multi-sentence atom paragraph (>30 words) and a per-chapter trailing-clause
# variant of it — exactly the shape the composer produces (same body, different
# one-line tail). The two share ~0.6 Jaccard, well above the 0.55 F1 threshold.
_BODY_A = (
    "The task is open. You have been looking at it for forty minutes. This is "
    "not laziness. Your body knows something your calendar does not. The "
    "shoulders climb toward the ears without permission."
)
_BODY_A_VARIANT = (
    "The task is open. You have been looking at it for forty minutes. This is "
    "not laziness. Your body knows something your calendar cannot. Watch the "
    "breath go shallow as the screen keeps glowing."
)
_BODY_B = (
    "Maria opens her laptop and the spreadsheet glows back at her. The numbers "
    "march down the column like soldiers on parade. She has not slept properly. "
    "The quarterly review is tomorrow and the model is plainly wrong."
)
_SHORT = "Stay here. Breathe. Let the sentence land."


def test_seen_bodies_exact_membership_is_set_compatible():
    """The registry preserves the plain-set surface old call-sites rely on."""
    reg = _SeenBodies()
    key = es._norm_ws(_BODY_A)
    assert key not in reg
    reg.add(key)
    assert key in reg
    assert len(reg) == 1


def test_seen_bodies_catches_trailing_clause_variant():
    """Exact match misses the variant; fuzzy match catches it (the core bug)."""
    reg = _SeenBodies()
    reg.add(es._norm_ws(_BODY_A))
    # exact set membership does NOT catch the variant (this is what defeated the
    # legacy dedup)
    assert es._norm_ws(_BODY_A_VARIANT) not in reg
    # fuzzy DOES
    assert reg.seen_similar(_BODY_A_VARIANT) is True


def test_seen_bodies_does_not_flag_unrelated_body():
    reg = _SeenBodies()
    reg.add(es._norm_ws(_BODY_A))
    assert reg.seen_similar(_BODY_B) is False


def test_seen_bodies_exempts_short_transitions():
    """Short bodies are free to repeat (mirrors F1's ≥3-sentence floor)."""
    reg = _SeenBodies()
    reg.note(_SHORT)
    assert reg.seen_similar(_SHORT) is False  # below min_words → never a dup


def test_seen_bodies_flag_off_disables_fuzzy(monkeypatch):
    """PHOENIX_DEPTH_DEDUP_FUZZY=0 falls back to pure exact-match behavior."""
    monkeypatch.setenv("PHOENIX_DEPTH_DEDUP_FUZZY", "0")
    reg = _SeenBodies()
    reg.add(es._norm_ws(_BODY_A))
    assert reg.seen_similar(_BODY_A_VARIANT) is False  # fuzzy disabled
    assert es._norm_ws(_BODY_A) in reg                  # exact still works


def test_seen_similar_tolerates_plain_set():
    """_seen_similar must not blow up when handed a legacy bare set."""
    assert _seen_similar(set(), _BODY_A) is False
    s = {es._norm_ws(_BODY_A)}
    # a plain set has no fuzzy layer → always False (exact-only semantics preserved)
    assert _seen_similar(s, _BODY_A_VARIANT) is False


# ── Sibling-block rotation in _pick_canonical_block_per_section ──────────────

_MULTIBLOCK_CANONICAL = """## RECOGNITION v01
PERSONA: gen_z_professionals
---
META: x
---
{a}

## RECOGNITION v02
PERSONA: gen_z_professionals
---
META: x
---
{b}
""".format(a=_BODY_A, b=_BODY_B)


def test_pick_block_rotates_off_rejected_sibling():
    """When the deterministic pick is rejected, rotation finds an unused sibling."""
    src = Path("atoms/gen_z_professionals/anxiety/recognition/CANONICAL.txt")

    # First call: no reject → records whichever block the hash picks.
    first = _pick_canonical_block_per_section(
        _MULTIBLOCK_CANONICAL,
        chapter_index=1, section_index=0,
        seed="t", slot_label="depth_eng:recognition", source_path=src,
    )
    assert first is not None
    used = first["text"]

    # Second call with a reject predicate that rejects the FIRST block's text:
    # rotation must return the OTHER block, not the rejected one.
    second = _pick_canonical_block_per_section(
        _MULTIBLOCK_CANONICAL,
        chapter_index=1, section_index=0,
        seed="t", slot_label="depth_eng:recognition", source_path=src,
        reject=lambda txt: txt.strip() == used.strip(),
    )
    assert second is not None
    assert second["text"].strip() != used.strip()


def test_pick_block_falls_back_when_all_rejected():
    """If every sibling is rejected, return a block anyway (completeness > no-repeat)."""
    src = Path("atoms/gen_z_professionals/anxiety/recognition/CANONICAL.txt")
    out = _pick_canonical_block_per_section(
        _MULTIBLOCK_CANONICAL,
        chapter_index=1, section_index=0,
        seed="t", slot_label="depth_eng:recognition", source_path=src,
        reject=lambda txt: True,  # reject everything
    )
    assert out is not None  # slot still filled
    assert out["text"].strip() in (_BODY_A.strip(), _BODY_B.strip())


# ── End-to-end completeness guard ───────────────────────────────────────────


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("fmt", ["deep_book_6h"])
def test_depth_dedup_preserves_book_completeness(fmt):
    """With the fuzzy dedup ON, a deep book still fills its word budget — the fix
    rotates content, it does not strip required depth (no thinner books)."""
    import yaml

    from phoenix_v4.planning.beatmap_compile import (
        compile_beatmap, load_format_spec, load_topic_engines,
    )
    from phoenix_v4.planning.enrichment_select import (
        EnrichmentRequest, apply_depth_pass, select_enrichment,
    )
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine

    root = _repo_root()
    topic, persona = "anxiety", "gen_z_professionals"
    spine = load_spine(topic, root, runtime_format=fmt)
    shaped = apply_knobs(spine, load_knob_profile(topic, root), runtime_format=fmt,
                         persona_id=persona, repo_root=root)
    beatmap = compile_beatmap(shaped, load_topic_engines(topic, root),
                              load_format_spec(fmt, root), root)
    req = EnrichmentRequest(beatmap=beatmap, teacher_id="ahjan", persona_id=persona,
                            topic_id=topic, seed="leverB_baseline")
    enriched = select_enrichment(req, root)
    depth_map = yaml.safe_load(
        (root / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    enriched = apply_depth_pass(enriched, depth_map, repo_root=root)
    # deep_book_6h must clear 40k words (same guard as test_deep_book_6h_exceeds_40k_words).
    assert enriched.total_words > 40000, (
        f"deep book thinned to {enriched.total_words}w — dedup stripped required depth"
    )

"""Tests for the song-kit lyric / mood-instruction engine scaffold.

Offline-first: every test runs with the deterministic template fallback (no LLM,
no network) unless it explicitly injects a fake Tier-1 callable. This file lives
under ``tests/`` which is globally exempt from the paid-LLM audit, and it imports
no LLM client of any kind.
"""
from __future__ import annotations

import pytest

from phoenix_v4.musician.lyric_mood_engine import (
    ALL_POOLS,
    LYRIC_POOLS,
    REFLECTION_POOLS,
    SPEC_739_CEILING,
    SPEC_739_FLOOR,
    Atom,
    EngineContext,
    Tier,
    TierRouter,
    build_mood_instruction_prompt,
    build_prompt,
    generate_kit,
)

# Mirrors the on-main test_artist_alpha derived context (profile/themes/voice).
ALPHA_PROFILE = {
    "display_name": "Test Artist Alpha",
    "primary_genre": "indie folk",
    "healing_intent_summary": "Stillness through honest lyric — naming small fears.",
}
ALPHA_VOICE = {
    "voice_person": "first_person",
    "register": "plain_spoken",
    "pacing": "varied",
    "signature_devices": ["returning morning imagery", "short refrain lines"],
}


def _ctx(**overrides):
    base = dict(
        musician_id="test_artist_alpha",
        profile=ALPHA_PROFILE,
        theme="quiet courage",
        family_id="quiet_courage",
        topic_anchor="courage",
        persona_anchor="anxious_seeker",
        genre="indie folk",
        voice_profile=ALPHA_VOICE,
        lyric_register_hint="Understated resolve; small concrete acts.",
        instrumental_mood_hint="Grounded, steady; gentle low strings; ~70-84 BPM.",
        lyric_form="free_verse",
    )
    base.update(overrides)
    return EngineContext(**base)


# ---------------------------------------------------------------------------
# Offline / deterministic behavior (the CI-critical contract)
# ---------------------------------------------------------------------------
def test_with_lyrics_offline_fills_all_six_pools():
    kit = generate_kit(_ctx(), fork="with-lyrics")  # router=None → fallback
    assert kit.fork == "with-lyrics"
    assert set(kit.atoms.keys()) == set(ALL_POOLS)
    # Kit-level tier_used records the RESOLVED tier (what was selected/attempted).
    # With no operator callable + English default, that resolves to Gemma (T2).
    assert kit.tier_used == Tier.T2_GEMMA_UNATTENDED.value
    # But with no router backend wired, each pool is actually drafted by the
    # deterministic template — the per-atom provenance reflects that.
    for pool, atom in kit.atoms.items():
        assert atom.tier_used == Tier.TEMPLATE_FALLBACK.value, pool


def test_no_lyrics_offline_fills_only_reflection_pools_and_mood_text():
    kit = generate_kit(_ctx(), fork="no-lyrics")
    assert set(kit.atoms.keys()) == set(REFLECTION_POOLS)
    # No lyric pools on the no-lyrics fork.
    assert not (set(kit.atoms.keys()) & set(LYRIC_POOLS))
    # MusicGen mood-instruction TEXT line is produced (no audio — spec §1.4).
    assert kit.mood_instruction
    assert "no audio rendered" in kit.mood_instruction.lower()


def test_spec_739_floor_every_pool_has_at_least_three_variants():
    kit = generate_kit(_ctx(), fork="with-lyrics")
    for pool, atom in kit.atoms.items():
        assert atom.variant_count >= SPEC_739_FLOOR, f"{pool}: {atom.variant_count}"
        assert atom.meets_spec_739, pool
    assert kit.complete is True
    assert set(kit.pools_meeting_floor) == set(ALL_POOLS)


def test_variants_per_pool_respects_ceiling_and_floor():
    # Above ceiling clamps to 5.
    kit_hi = generate_kit(_ctx(), fork="with-lyrics", variants_per_pool=99)
    for atom in kit_hi.atoms.values():
        assert atom.variant_count <= SPEC_739_CEILING
    # Below floor lifts to 3.
    kit_lo = generate_kit(_ctx(), fork="with-lyrics", variants_per_pool=1)
    for atom in kit_lo.atoms.values():
        assert atom.variant_count >= SPEC_739_FLOOR


# ---------------------------------------------------------------------------
# Atom shape parity with on-main (atom_id + variants[].body) + template vars
# ---------------------------------------------------------------------------
def test_atom_yaml_shape_matches_on_main():
    kit = generate_kit(_ctx(), fork="with-lyrics")
    atom = kit.atoms["LYRIC_OPENING"]
    d = atom.to_atom_yaml_dict()
    assert set(d.keys()) == {"atom_id", "variants"}
    assert isinstance(d["variants"], list)
    for v in d["variants"]:
        assert set(v.keys()) == {"body"}
        assert isinstance(v["body"], str) and v["body"].strip()


def test_atom_id_follows_on_main_convention():
    kit = generate_kit(_ctx(), fork="with-lyrics")
    assert kit.atoms["LYRIC_OPENING"].atom_id == "test_artist_alpha_LYRIC_OPENING_01"
    assert kit.atoms["MUSIC_REFLECTION_CLOSING"].atom_id == (
        "test_artist_alpha_MUSIC_REFLECTION_CLOSING_01"
    )


def test_template_vars_only_uses_established_placeholders():
    import re

    allowed = {
        "musician_name", "topic_anchor", "theme", "genre",
        "persona_anchor", "healing_intent",
    }
    kit = generate_kit(_ctx(), fork="with-lyrics")
    seen = set()
    for atom in kit.atoms.values():
        for v in atom.variants:
            seen |= set(re.findall(r"\{\{\s*(\w+)\s*\}\}", v["body"]))
    assert seen, "fallback bodies should carry template placeholders"
    assert seen <= allowed, f"unexpected template vars: {seen - allowed}"


def test_lyric_pool_bodies_do_not_use_healing_intent_var():
    # healing_intent is a reflection-pool var; lyric fallbacks should not need it.
    kit = generate_kit(_ctx(), fork="with-lyrics")
    for pool in LYRIC_POOLS:
        for v in kit.atoms[pool].variants:
            assert "{{healing_intent}}" not in v["body"], pool


def test_variants_are_deduped_within_pool():
    kit = generate_kit(_ctx(), fork="with-lyrics", variants_per_pool=SPEC_739_CEILING)
    for pool, atom in kit.atoms.items():
        bodies = [v["body"].strip().lower() for v in atom.variants]
        assert len(bodies) == len(set(bodies)), f"dupes in {pool}"


# ---------------------------------------------------------------------------
# Tier routing (no paid API anywhere; T1 is an injected callable)
# ---------------------------------------------------------------------------
def test_tier1_pearl_writer_callable_is_used_when_operator_present():
    calls = {"n": 0}

    def fake_pearl_writer(prompt: str, system):
        calls["n"] += 1
        # Three distinct lyric-ish lines so the pool clears the floor via the LLM tier.
        return (
            "{{musician_name}} holds {{theme}} steady\n"
            "A small brave act for {{persona_anchor}}\n"
            "{{topic_anchor}} loosens by a degree\n"
            "Quiet resolve in {{genre}} air"
        )

    router = TierRouter(pearl_writer_fn=fake_pearl_writer)
    kit = generate_kit(_ctx(), fork="with-lyrics", router=router, operator_present=True)
    assert calls["n"] > 0, "Pearl_Writer callable should be invoked for T1"
    assert kit.tier_used == Tier.T1_PEARL_WRITER.value
    # At least one pool should carry the T1 provenance label.
    assert any(a.tier_used == Tier.T1_PEARL_WRITER.value for a in kit.atoms.values())


def test_no_callable_falls_back_even_when_operator_present():
    # Operator present but NO Pearl_Writer callable wired → must not crash; must
    # produce a complete kit via the deterministic template.
    router = TierRouter(pearl_writer_fn=None, allow_tier2_router=False)
    kit = generate_kit(_ctx(), fork="with-lyrics", router=router, operator_present=True)
    assert kit.complete
    for atom in kit.atoms.values():
        assert atom.tier_used == Tier.TEMPLATE_FALLBACK.value


def test_cjk_fork_resolves_to_qwen_tier():
    from phoenix_v4.musician.lyric_mood_engine import _resolve_tier

    router = TierRouter(pearl_writer_fn=lambda p, s: "x")
    # CJK language must route to Qwen regardless of operator presence.
    assert _resolve_tier("zh-CN", True, router) is Tier.T2_QWEN_CJK
    assert _resolve_tier("ja", False, router) is Tier.T2_QWEN_CJK


def test_english_unattended_resolves_to_gemma_tier():
    from phoenix_v4.musician.lyric_mood_engine import _resolve_tier

    router = TierRouter(pearl_writer_fn=lambda p, s: "x")
    # Unattended English → Gemma (T2), not Pearl_Writer.
    assert _resolve_tier("en", False, router) is Tier.T2_GEMMA_UNATTENDED
    # Operator present but no callable → also Gemma (can't use T1 without a callable).
    assert _resolve_tier("en", True, TierRouter()) is Tier.T2_GEMMA_UNATTENDED


def test_router_draft_returns_none_for_template_fallback_tier():
    router = TierRouter()
    assert router.draft(Tier.TEMPLATE_FALLBACK, "anything") is None


def test_router_draft_t1_swallows_callable_errors():
    def boom(prompt, system):
        raise RuntimeError("backend down")

    router = TierRouter(pearl_writer_fn=boom)
    # Must degrade to None (→ engine fallback), never propagate.
    assert router.draft(Tier.T1_PEARL_WRITER, "x") is None


def test_tier2_router_disabled_returns_none():
    router = TierRouter(allow_tier2_router=False)
    assert router.draft(Tier.T2_QWEN_CJK, "x") is None
    assert router.draft(Tier.T2_GEMMA_UNATTENDED, "x") is None


# ---------------------------------------------------------------------------
# Prompt builders + context backfill + validation
# ---------------------------------------------------------------------------
def test_build_prompt_lyric_vs_reflection_mentions_right_vars():
    ctx = _ctx()
    lyric_prompt = build_prompt(ctx, "LYRIC_OPENING", 3)
    refl_prompt = build_prompt(ctx, "MUSIC_REFLECTION_OPENING", 3)
    assert "{{healing_intent}}" not in lyric_prompt
    assert "{{healing_intent}}" in refl_prompt
    assert "lyric block" in lyric_prompt
    assert "music-reflection passage" in refl_prompt


def test_mood_instruction_prompt_is_single_line_instrumental():
    p = build_mood_instruction_prompt(_ctx())
    assert "MusicGen" in p and "no lyrics" in p.lower()


def test_context_backfills_genre_and_healing_from_profile():
    ctx = EngineContext(musician_id="m", profile=ALPHA_PROFILE)
    assert ctx.genre == "indie folk"
    assert ctx.healing_intent.startswith("Stillness")
    assert ctx.musician_name == "Test Artist Alpha"


def test_musician_name_falls_back_to_id():
    ctx = EngineContext(musician_id="ahjan", profile={})
    assert ctx.musician_name == "ahjan"


def test_invalid_fork_raises():
    with pytest.raises(ValueError):
        generate_kit(_ctx(), fork="instrumental-only")


def test_atom_helpers():
    atom = Atom(atom_id="x_LYRIC_OPENING_01", variants=[{"body": "a"}, {"body": "b"}])
    assert atom.variant_count == 2
    assert atom.meets_spec_739 is False
    atom.variants.append({"body": "c"})
    assert atom.meets_spec_739 is True

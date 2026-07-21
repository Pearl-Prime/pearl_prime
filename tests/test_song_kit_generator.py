"""Tests for the Song-Kit survey → generator orchestrator (offline, deterministic).

All tests run with the ``DeterministicStubEngine`` — zero network, zero LLM, no paid
API (CLAUDE.md Tier policy). The taxonomy is loaded either from the real on-repo
``config/music/song_kit_topic_families.yaml`` (when present) or from an inline fixture
so the suite is hermetic.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.musician.bank_writer import write_kit_to_bank
from phoenix_v4.musician.lyric_mood_engine import (
    TierRoutedEngine,
    TierRouter,
    make_operator_authored_pearl_writer_fn,
)
from phoenix_v4.musician.song_kit_generator import (
    ALL_POOLS,
    LYRIC_POOLS,
    REFLECTION_POOLS,
    SPEC_739_FLOOR,
    DeterministicStubEngine,
    DraftAtom,
    GenerationRequest,
    KitResult,
    SongKitGenerator,
    build_kit_skeleton,
    load_topic_families,
    match_families,
    run_diversity_gate,
)

REPO = Path(__file__).resolve().parents[1]

# Inline family fixture mirroring the on-main 8-family SSOT shape (spec §2). Used when
# the real config file is not on disk so the suite stays hermetic.
_FAMILY_FIXTURE: dict[str, dict[str, object]] = {
    "recovery_and_repair": {
        "family_id": "recovery_and_repair",
        "display": "Recovery & Repair",
        "topic_anchors": ["burnout", "compassion_fatigue", "addiction"],
        "default_themes": ["rebuilding after depletion", "the slow work of repair"],
        "lyric_register_hint": "Plain-spoken, patient, present-tense.",
        "instrumental_mood_hint": "Warm, restorative, unhurried; tempo ~60-72 BPM.",
    },
    "presence_and_stillness": {
        "family_id": "presence_and_stillness",
        "display": "Presence & Stillness",
        "topic_anchors": ["overthinking", "sleep_anxiety"],
        "default_themes": ["returning to the body", "one breath at a time"],
        "lyric_register_hint": "Spare, sensory, slow.",
        "instrumental_mood_hint": "Sparse, meditative, spacious; tempo ~50-66 BPM.",
    },
}


def _families() -> dict[str, dict[str, object]]:
    """Prefer the real SSOT file; fall back to the inline fixture (hermetic)."""
    real = load_topic_families(REPO / "config/music/song_kit_topic_families.yaml")
    return real or _FAMILY_FIXTURE


# Survey dicts conforming to the SURVEY_TEMPLATE.yaml fork blocks (spec §3.1/§3.2).
def _survey_with_lyrics() -> dict:
    return {
        "identity": {"display_name": "River Vale", "primary_genre": "indie folk"},
        "themes": {
            "primary_themes": ["recovery", "the slow work of repair"],
            "avoided_themes": ["glamour"],
            "listener_hope_one": "That rest can be honest.",
        },
        "voice_craft": {
            "voice_person": "first_person",
            "register": "plain_spoken",
            "pacing": "varied",
            "signature_devices": ["morning imagery"],
        },
        "healing_intent": {"what_helps_heal": "naming small fears"},
        "output_preferences_with_lyrics": {
            "lyric_form": "free_verse",
            "explicit_content_ok": False,
            "companion_ai_song_consent": True,
        },
        "synthetic": True,
    }


def _survey_no_lyrics() -> dict:
    return {
        "identity": {"display_name": "Still Water", "primary_genre": "ambient"},
        "themes": {"primary_themes": ["presence", "returning to the body"]},
        "voice_craft": {"voice_person": "second_person", "register": "spare"},
        "output_preferences_no_lyrics": {
            "reflection_form": "meditation",
            "reflection_perspective": "listener",
        },
        "synthetic": True,
    }


def _survey_both() -> dict:
    s = _survey_with_lyrics()
    s["output_preferences_no_lyrics"] = {
        "reflection_form": "journal_entry",
        "reflection_perspective": "musician",
    }
    return s


# --- pool-name lockstep -----------------------------------------------------------
def test_pools_match_music_overlay():
    """song_kit pools must equal the music_overlay injection-planner pool keys."""
    from phoenix_v4.planning.music_overlay import plan_music_injection

    keys = {
        p.atom_pool_key
        for mode in ("with-lyrics", "no-lyrics")
        for p in plan_music_injection(chapter_count=1, music_mode=mode)
    }
    assert keys == set(ALL_POOLS)
    assert set(LYRIC_POOLS).isdisjoint(REFLECTION_POOLS)
    assert len(ALL_POOLS) == 6


# --- fork selection ---------------------------------------------------------------
def test_select_fork_with_lyrics():
    assert SongKitGenerator.select_fork(_survey_with_lyrics()) == "with-lyrics"


def test_select_fork_no_lyrics():
    assert SongKitGenerator.select_fork(_survey_no_lyrics()) == "no-lyrics"


def test_select_fork_both():
    assert SongKitGenerator.select_fork(_survey_both()) == "both"


def test_select_fork_consent_false_disables_lyrics():
    s = _survey_with_lyrics()
    s["output_preferences_with_lyrics"]["companion_ai_song_consent"] = False
    # with-lyrics block present but consent withheld + no no-lyrics block → safe default
    assert SongKitGenerator.select_fork(s) == "no-lyrics"


def test_targeted_pools_per_fork():
    assert SongKitGenerator.targeted_pools("with-lyrics") == ALL_POOLS
    assert SongKitGenerator.targeted_pools("both") == ALL_POOLS
    assert SongKitGenerator.targeted_pools("no-lyrics") == REFLECTION_POOLS


# --- family matching --------------------------------------------------------------
def test_match_families_recovery():
    matched = match_families(["recovery", "the slow work of repair"], _families())
    assert "recovery_and_repair" in matched


def test_match_families_is_focused_not_everything():
    """A focused survey must not match all families (stopwords must be dropped)."""
    fams = _families()
    matched = match_families(["recovery", "the slow work of repair"], fams)
    # the recovery theme is specific; it must NOT light up every family via fillers
    assert matched == ["recovery_and_repair"]


def test_match_families_anchor_token():
    """A bare canonical anchor (burnout) routes to its owning family."""
    matched = match_families(["burnout"], _families())
    assert "recovery_and_repair" in matched


def test_match_families_presence():
    matched = match_families(["presence", "returning to the body"], _families())
    assert "presence_and_stillness" in matched


def test_match_families_none_returns_empty():
    matched = match_families(["quantum tax accounting"], _families())
    assert matched == []


# --- end-to-end kit build (with-lyrics) -------------------------------------------
def test_build_kit_with_lyrics_offline():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_with_lyrics(), "river_vale")
    assert isinstance(kit, KitResult)
    assert kit.fork == "with-lyrics"
    assert kit.brand_id == "river_vale_music"  # Q2 <handle>_music slug
    # all 6 pools targeted on the with-lyrics fork
    assert set(kit.pools) == set(ALL_POOLS)
    # every pool has exactly one atom of >= floor variants → SPEC-739 complete
    for pool in ALL_POOLS:
        atoms = kit.pools[pool]
        assert len(atoms) == 1
        assert atoms[0].variant_count() >= SPEC_739_FLOOR
    assert kit.spec739["complete"] is True
    assert kit.spec739["floor"] == SPEC_739_FLOOR
    assert not kit.spec739["deficient_pools"]
    assert kit.complete is True


def test_build_kit_no_lyrics_emits_reflection_only():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_no_lyrics(), "still_water")
    assert kit.fork == "no-lyrics"
    # no-lyrics fork: only the 3 MUSIC_REFLECTION_* pools are drafted
    assert set(kit.pools) == set(REFLECTION_POOLS)
    for pool in REFLECTION_POOLS:
        # bodies are MusicGen mood-instruction TEXT (no audio; spec §1.4)
        body = kit.pools[pool][0].variants[0]["body"]
        assert "mood-instruction" in body
    assert kit.complete is True


def test_no_lyrics_does_not_emit_lyric_pools():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_no_lyrics(), "still_water")
    for pool in LYRIC_POOLS:
        assert pool not in kit.pools


def test_build_kit_both_fork_targets_all_pools():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_both(), "river_vale")
    assert kit.fork == "both"
    assert set(kit.pools) == set(ALL_POOLS)


# --- atom shape (on-main: atom_id + variants:[{body:...}]) -------------------------
def test_atom_yaml_shape_matches_on_main():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_with_lyrics(), "river_vale")
    atom = kit.pools["LYRIC_OPENING"][0]
    obj = atom.to_atom_yaml_obj()
    assert set(obj.keys()) == {"atom_id", "variants"}  # exactly the 2 canonical keys
    assert obj["atom_id"] == "river_vale_LYRIC_OPENING_01"
    assert isinstance(obj["variants"], list)
    assert all(set(v.keys()) == {"body"} for v in obj["variants"])
    assert atom.status == "draft"  # PROPOSED, human-reviewed (spec §3.3)


def test_template_vars_present_in_bodies():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_with_lyrics(), "river_vale")
    body = kit.pools["LYRIC_OPENING"][0].variants[0]["body"]
    # established template vars are preserved, not replaced (spec §3.3)
    assert "{{musician_name}}" in body
    assert "{{topic_anchor}}" in body


# --- SPEC-739 floor enforcement ---------------------------------------------------
def test_spec739_floor_deficiency_flagged():
    # An engine producing only the requested variants but a floor raised to 5 against a
    # generator built with floor=2 → deficiency surfaces in the verdict.
    gen = SongKitGenerator(families=_families(), floor=2)
    kit = gen.build_kit(_survey_no_lyrics(), "still_water")
    # generator floor=2 → each pool has 2 variants; re-score against a stricter floor
    strict = SongKitGenerator(families=_families(), floor=5)
    verdict = strict._spec739_verdict(kit, REFLECTION_POOLS)
    assert verdict["complete"] is False
    assert set(verdict["deficient_pools"]) == set(REFLECTION_POOLS)


def test_floor_must_be_positive():
    with pytest.raises(ValueError):
        SongKitGenerator(families=_families(), floor=0)


# --- diversity gate adapter (reuse, never reimplement) ----------------------------
def test_diversity_gate_runs_now_that_the_canonical_gate_landed():
    # music_mode_diversity_ci_guard_20260721 landed scripts/ci/check_music_brand_
    # diversity.py with an evaluate_kit entry point — the adapter now finds and
    # calls it (previously asserted "skipped" when the gate didn't exist yet).
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_with_lyrics(), "river_vale")
    assert kit.diversity["status"] == "ran"
    assert kit.diversity["entry_point"] == "evaluate_kit"
    assert "check_music_brand_diversity" in kit.diversity["gate"]
    assert "verdict" in kit.diversity
    assert "G1" in kit.diversity["verdict"]["gates"]


def test_run_diversity_gate_direct_runs_and_returns_g1_verdict():
    gen = SongKitGenerator(families=_families())
    kit = gen.build_kit(_survey_no_lyrics(), "still_water", run_gate=False)
    assert kit.diversity["status"] == "not_requested"
    verdict = run_diversity_gate(kit, quality_profile="production")
    assert verdict["status"] == "ran"
    assert verdict["quality_profile"] == "production"
    assert verdict["verdict"]["gates"]["G1"]["status"] == "pass"


# --- pluggable engine -------------------------------------------------------------
def test_engine_is_pluggable():
    class MarkerEngine:
        name = "marker"

        def generate(self, request: GenerationRequest) -> str:
            return f"MARKER::{request.slot_pool}::{request.variant_index}"

    gen = SongKitGenerator(engine=MarkerEngine(), families=_families())
    kit = gen.build_kit(_survey_no_lyrics(), "still_water")
    body = kit.pools["MUSIC_REFLECTION_OPENING"][0].variants[0]["body"]
    assert body.startswith("MARKER::MUSIC_REFLECTION_OPENING::0")


def test_deterministic_stub_is_deterministic():
    eng = DeterministicStubEngine()
    fam = next(iter(_families().values()))
    req = GenerationRequest(
        musician_id="x",
        slot_pool="LYRIC_OPENING",
        position="opening",
        family_id="recovery_and_repair",
        kind="lyric",
        variant_index=0,
        profile={},
        themes={},
        voice_profile={},
        family=fam,
        topic_anchor="burnout",
        theme="repair",
    )
    assert eng.generate(req) == eng.generate(req)  # no RNG / clock / I/O


def test_stub_engine_carries_no_paid_api():
    """Guard: the stub must not reference any paid-LLM env var or client."""
    import inspect

    from phoenix_v4.musician import song_kit_generator as mod

    src = inspect.getsource(mod)
    banned = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_API_KEY",
        "openai",
        "dashscope",
        "together",
        "replicate",
        "perplexity",
        "cohere",
    ]
    lowered = src.lower()
    for token in banned:
        assert token.lower() not in lowered, f"banned LLM token in module: {token}"


# --- functional one-call helper ---------------------------------------------------
def test_build_kit_skeleton_runs_offline():
    kit = build_kit_skeleton(_survey_with_lyrics(), "river_vale", families=_families())
    assert kit.complete is True
    summ = kit.summary()
    assert summ["fork"] == "with-lyrics"
    assert summ["complete"] is True
    assert all(c >= SPEC_739_FLOOR for c in summ["pool_variant_counts"].values())


def test_summary_is_json_serializable():
    import json

    kit = build_kit_skeleton(_survey_no_lyrics(), "still_water", families=_families())
    json.dumps(kit.summary())  # must not raise


def test_unmatched_family_flags_degraded_note():
    gen = SongKitGenerator(families=_families())
    survey = _survey_no_lyrics()
    survey["themes"]["primary_themes"] = ["quantum tax accounting"]
    kit = gen.build_kit(survey, "still_water")
    assert kit.matched_families == []
    assert any("No topic family matched" in n for n in kit.notes)
    # still produces a kit skeleton (neutral fallback), just review-flagged
    assert set(kit.pools) == set(REFLECTION_POOLS)


# ---------------------------------------------------------------------------
# TierRoutedEngine wiring (music_mode_real_lyric_mood_engine_20260721):
# proves SongKitGenerator — the orchestrator that ships to the pipeline/lane 05 —
# can run end-to-end on real, operator-authored Tier-1 content, not only the
# DeterministicStubEngine. Operator-authored fixture below (no network/LLM call).
# ---------------------------------------------------------------------------
STILL_WATER_REFLECTION_BODIES = {
    "MUSIC_REFLECTION_OPENING": [
        "Still Water opens with presence, not performance — let the room quiet "
        "before the first exhale.",
        "Returning to the body starts here: notice the feet, then the breath, "
        "then the rest.",
        "No music yet, just permission to arrive exactly as tired as you are.",
    ],
    "MUSIC_REFLECTION_BESTSELLER_BEAT": [
        "Here is the turn: presence is not the absence of noise, it is choosing "
        "which sound gets your attention.",
        "The body already knows the chapter's answer; this passage just slows "
        "down long enough to hear it.",
        "Returning to the body again, mid-chapter, because the mind wandered off "
        "to fix something that isn't broken.",
    ],
    "MUSIC_REFLECTION_CLOSING": [
        "Let the stillness close the chapter softly, no need to summarize what "
        "the body already understood.",
        "Presence doesn't expire when the track ends; carry the quieter "
        "shoulders into whatever is next.",
        "Return to the body once more before you go — that's the whole "
        "practice, repeated.",
    ],
}


def test_song_kit_generator_runs_end_to_end_on_tier_routed_engine():
    fn = make_operator_authored_pearl_writer_fn(STILL_WATER_REFLECTION_BODIES)
    engine = TierRoutedEngine(
        router=TierRouter(pearl_writer_fn=fn, allow_tier2_router=False),
        operator_present=True,
    )
    gen = SongKitGenerator(engine=engine, families=_families())
    kit = gen.build_kit(_survey_no_lyrics(), "still_water")
    assert kit.complete is True
    for pool, expected in STILL_WATER_REFLECTION_BODIES.items():
        bodies = [v["body"] for atom in kit.pools[pool] for v in atom.variants]
        assert bodies == expected


# ---------------------------------------------------------------------------
# Bank writer (music_mode_real_lyric_mood_engine_20260721, README "Remaining
# work" item #2): serializes a KitResult to SOURCE_OF_TRUTH/musician_banks/.
# ---------------------------------------------------------------------------
def test_write_kit_to_bank_writes_canonical_atom_shape(tmp_path):
    kit = build_kit_skeleton(_survey_with_lyrics(), "river_vale", families=_families())
    written = write_kit_to_bank(kit, "river_vale", tmp_path)
    assert written, "must write at least one file"

    opening_path = (
        tmp_path / "SOURCE_OF_TRUTH/musician_banks/river_vale/approved_atoms"
        "/LYRIC_OPENING/river_vale_LYRIC_OPENING_01.yaml"
    )
    assert opening_path in written
    assert opening_path.is_file()

    import yaml

    data = yaml.safe_load(opening_path.read_text(encoding="utf-8"))
    # Canonical on-main 2-key shape, matching to_atom_yaml_obj() exactly — no
    # "status" field, no draft/approved split invented (matches ahjan/
    # test_artist_alpha on-disk convention verified at discovery time).
    assert set(data.keys()) == {"atom_id", "variants"}
    assert data["atom_id"] == "river_vale_LYRIC_OPENING_01"
    assert all(set(v.keys()) == {"body"} for v in data["variants"])

    # No draft_atoms/ directory is ever created — approved_atoms/ only.
    bank_dir = tmp_path / "SOURCE_OF_TRUTH/musician_banks/river_vale"
    assert not (bank_dir / "draft_atoms").exists()
    assert (bank_dir / "approved_atoms").is_dir()


def test_write_kit_to_bank_persists_survey_and_derived_yaml(tmp_path):
    survey = _survey_with_lyrics()
    kit = build_kit_skeleton(survey, "river_vale", families=_families())
    written = write_kit_to_bank(
        kit, "river_vale", tmp_path, survey=survey, survey_date="2026-07-21",
    )
    bank_dir = tmp_path / "SOURCE_OF_TRUTH/musician_banks/river_vale"
    for name in ("profile.yaml", "themes.yaml", "voice_profile.yaml"):
        assert (bank_dir / name).is_file()
        assert (bank_dir / name) in written
    resp = bank_dir / "survey_responses/2026-07-21.yaml"
    assert resp.is_file()
    assert resp in written

    import yaml

    profile = yaml.safe_load((bank_dir / "profile.yaml").read_text(encoding="utf-8"))
    assert profile["display_name"] == "River Vale"
    persisted_survey = yaml.safe_load(resp.read_text(encoding="utf-8"))
    assert persisted_survey == survey


def test_write_kit_to_bank_writes_every_pool_covering_all_atoms(tmp_path):
    kit = build_kit_skeleton(_survey_with_lyrics(), "river_vale", families=_families())
    write_kit_to_bank(kit, "river_vale", tmp_path)
    atoms_dir = tmp_path / "SOURCE_OF_TRUTH/musician_banks/river_vale/approved_atoms"
    for pool, atoms in kit.pools.items():
        for atom in atoms:
            path = atoms_dir / pool / f"{atom.atom_id}.yaml"
            assert path.is_file(), path

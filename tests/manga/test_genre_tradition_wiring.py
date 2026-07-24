"""R1 — genre drawing-tradition wired into the PRODUCTION panel-prompt compiler.

Asserts the fix for the "healing rendered like the wrong tradition" failure:
the per-genre drawing-tradition cookbook (drawing_tradition_per_genre.yaml +
cross_genre_blending_rules.yaml) now feeds the production chapter-DAG compiler
``compile_panel_prompts_from_chapter_script`` for EVERY panel whenever a genre
is known — DECOUPLED from character individuation. A Devotion/healing chapter
gets iyashikei tokens even with no character_design; a horror chapter gets a
visibly different (dense ink / gekiga) tradition.
"""
from __future__ import annotations

from phoenix_v4.manga.chapter.visual_from_script import (
    compile_panel_prompts_from_chapter_script,
)
from phoenix_v4.manga.genre_tradition import (
    genre_tradition_tokens,
    resolve_tradition_genre,
)


def _chapter_script():
    return {
        "pages": [
            {
                "page_number": 1,
                "panels": [
                    {"panel_id": "c1p1", "action": "a quiet moment by the window",
                     "mood": "calm", "dialogue": ["..."]},
                ],
            }
        ]
    }


# ── Unit: the token resolver itself ───────────────────────────────────────────

def test_devotion_healing_resolves_iyashikei_tokens():
    pos, neg = genre_tradition_tokens("healing", base_model="flux_schnell")
    blob = " ".join(pos).lower()
    # The curated H_token_mapping flux_schnell positive for healing.
    assert "watercolor" in blob
    assert "sparse pen-and-ink" in blob or "sparse linework" in blob
    # Healing forbids harsh / dramatic shading on the negative side.
    assert any("dramatic" in n.lower() or "harsh" in n.lower() for n in neg)


def test_horror_resolves_distinct_dense_ink_tokens():
    pos, _ = genre_tradition_tokens("psychological_horror", base_model="flux_schnell")
    blob = " ".join(pos).lower()
    assert "cross-hatching" in blob or "dense" in blob or "ito" in blob
    # Definitely NOT the healing register.
    assert "watercolor" not in blob


def test_healing_and_horror_tokens_differ():
    h_pos, _ = genre_tradition_tokens("healing", base_model="flux_schnell")
    x_pos, _ = genre_tradition_tokens("psychological_horror", base_model="flux_schnell")
    assert set(t.lower() for t in h_pos) != set(t.lower() for t in x_pos)


def test_deferred_phase2_genre_yields_nothing():
    # "essay" is still a deferred_phase2 stub (wave-2 2026-07-22 upgraded
    # battle/sports/mystery/workplace/sci_fi_cyberpunk/supernatural_everyday
    # to wave_2_deep — see config/manga/drawing_tradition_per_genre.yaml) →
    # fail-open empty for a genre still deferred.
    pos, neg = genre_tradition_tokens("essay", base_model="flux_schnell")
    assert pos == [] and neg == []


def test_wave_2_deep_genre_resolves_tokens():
    # Wave-2 backfill (2026-07-22): these 6 genres moved from deferred_phase2
    # to a full A-H deep block (status: wave_2_deep). genre_tradition_tokens
    # treats any status != "deferred_phase2" as active, so they now resolve
    # non-empty tokens same as a top_8_deep genre.
    for genre_id in (
        "battle",
        "sports",
        "mystery",
        "workplace",
        "sci_fi_cyberpunk",
        "supernatural_everyday",
    ):
        pos, neg = genre_tradition_tokens(genre_id, base_model="qwen_image")
        assert pos, f"{genre_id} should resolve non-empty positive tokens"
        assert neg, f"{genre_id} should resolve non-empty negative tokens"


def test_unknown_genre_and_empty_are_fail_open():
    assert genre_tradition_tokens(None) == ([], [])
    assert genre_tradition_tokens("") == ([], [])
    assert genre_tradition_tokens("no_such_genre_xyz") == ([], [])


def test_psychological_horror_stays_distinct_from_deferred_horror():
    # Wave-2 constraint (spec item 1 point 4): psychological_horror must stay
    # on its own top_8_deep block and must NOT collapse into the deferred
    # `horror` genre.
    assert resolve_tradition_genre("psychological_horror") == "psychological_horror"
    # `horror` remains deferred_phase2 (out of scope for this wave) — it
    # fails open (canonical resolution only, no deep tradition block).
    horror_pos, horror_neg = genre_tradition_tokens("horror", base_model="flux_schnell")
    assert horror_pos == [] and horror_neg == []
    ph_pos, _ = genre_tradition_tokens("psychological_horror", base_model="flux_schnell")
    assert ph_pos  # psychological_horror still resolves its own tokens


def test_mystery_resolves_a_positive_and_negative_token_via_resolver():
    canonical = resolve_tradition_genre("mystery")
    assert canonical == "mystery"
    pos, neg = genre_tradition_tokens(canonical, base_model="qwen_image")
    assert pos and neg


# ── Integration: production compiler folds tradition into every panel ──────────

def test_devotion_panels_carry_iyashikei_without_character_design():
    """The core fix: genre tradition is DECOUPLED from individuation.

    series_id resolves to no character design, yet healing tokens still ride.
    """
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(),
        series_id="no_such_series",   # no character_design → individuation skipped
        brand_id="devotion_path",
        genre_id="healing",
        market_demo="josei",
    )
    prompt = doc["panels"][0]["prompt"].lower()
    # devotion_path/healing/josei routes to Animagine → the iyashikei register
    # arrives as the Animagine H_token_mapping (soft lighting / gentle / peaceful
    # / slice of life), not the flux-specific "watercolor" word. Assert the
    # engine-agnostic iyashikei signal.
    assert any(k in prompt for k in ("soft lighting", "peaceful", "gentle", "slice of life", "watercolor"))
    # Provenance flag recorded.
    assert doc["render_routing"]["genre_tradition_engaged"] is True


def test_horror_vs_devotion_production_prompts_differ():
    devotion = compile_panel_prompts_from_chapter_script(
        _chapter_script(), series_id="no_such_series",
        brand_id="devotion_path", genre_id="healing", market_demo="josei",
    )["panels"][0]["prompt"].lower()
    horror = compile_panel_prompts_from_chapter_script(
        _chapter_script(), series_id="no_such_series",
        genre_id="psychological_horror",
    )["panels"][0]["prompt"].lower()
    assert devotion != horror
    # Devotion carries the iyashikei (soft/gentle/peaceful) register; horror does not.
    assert any(k in devotion for k in ("soft lighting", "peaceful", "gentle", "slice of life"))
    assert not any(k in horror for k in ("soft lighting", "peaceful", "slice of life"))
    # Horror carries dense-ink / gekiga / Ito-lineage tokens.
    assert any(k in horror for k in ("cross-hatch", "ito", "dense", "gekiga", "desaturated", "blood red"))


def test_legacy_call_without_genre_is_verbatim():
    """No genre → no tradition tokens, no render_routing block (legacy shape)."""
    doc = compile_panel_prompts_from_chapter_script(
        _chapter_script(), series_id="no_such_series",
    )
    assert "render_routing" not in doc
    prompt = doc["panels"][0]["prompt"].lower()
    # Default style archetype is dark_psychological; healing tokens must be absent.
    assert "watercolor" not in prompt

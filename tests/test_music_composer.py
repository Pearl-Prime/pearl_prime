from pathlib import Path

from phoenix_v4.rendering.music_composer import (
    build_substitutions,
    compose_atom_text,
    list_atom_files,
    load_musician_profile,
)

REPO = Path(__file__).resolve().parents[1]


def test_list_atom_files():
    files = list_atom_files(REPO, "test_artist_alpha", "LYRIC_OPENING")
    assert len(files) >= 1


def test_compose_deterministic_differs_by_seed():
    subs = build_substitutions(load_musician_profile(REPO, "test_artist_alpha"), "gen_z_professionals", "anxiety")
    a = compose_atom_text(
        REPO,
        "test_artist_alpha",
        "LYRIC_OPENING",
        chapter_index=0,
        book_seed="same-seed",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        substitutions=subs,
    )
    b = compose_atom_text(
        REPO,
        "test_artist_alpha",
        "LYRIC_OPENING",
        chapter_index=3,
        book_seed="same-seed",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        substitutions=subs,
    )
    assert a != b


def test_hydration_replaces_slots():
    subs = build_substitutions(load_musician_profile(REPO, "test_artist_alpha"), "gen_z_professionals", "anxiety")
    t = compose_atom_text(
        REPO,
        "test_artist_alpha",
        "LYRIC_OPENING",
        chapter_index=1,
        book_seed="fixed",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        substitutions=subs,
    )
    assert "{{" not in t
    assert "Test Artist Alpha" in t

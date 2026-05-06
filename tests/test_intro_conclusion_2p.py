from pathlib import Path

from phoenix_v4.rendering.intro_conclusion_2p import render_music_conclusion_2p, render_music_intro_2p

REPO = Path(__file__).resolve().parents[1]


def test_intro_hydrates():
    t = render_music_intro_2p(
        REPO,
        "test_artist_alpha",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        book_seed="s1",
    )
    assert "Test Artist Alpha" in t
    assert "{{" not in t


def test_intro_seed_variation():
    a = render_music_intro_2p(REPO, "test_artist_alpha", persona_id="p", topic_id="t", book_seed="aa")
    b = render_music_intro_2p(REPO, "test_artist_alpha", persona_id="p", topic_id="t", book_seed="bb")
    assert a != b


def test_conclusion_present():
    c = render_music_conclusion_2p(REPO, "test_artist_alpha", persona_id="p", topic_id="t", book_seed="cc")
    assert len(c) > 80

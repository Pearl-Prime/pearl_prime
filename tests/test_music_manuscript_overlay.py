from pathlib import Path

from phoenix_v4.rendering.music_manuscript_overlay import apply_music_overlay_to_manuscript

REPO = Path(__file__).resolve().parents[1]


def test_overlay_inserts_music_markers():
    base = (
        "Preface line\n\n"
        "Chapter 1\n\n"
        "First paragraph of chapter one.\n\nSecond paragraph here.\n\nThird.\n\n"
        "Chapter 2\n\n"
        "Alpha paragraph.\n\nBeta paragraph.\n\n"
    )
    out, audit = apply_music_overlay_to_manuscript(
        base,
        repo_root=REPO,
        music_mode="no-lyrics",
        musician_id="test_artist_alpha",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        book_seed="overlay-test",
    )
    assert audit.get("applied") is True
    assert "--- Music" in out
    assert "A note from your reader" in out
    assert "Closing note" in out

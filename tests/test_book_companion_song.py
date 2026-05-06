import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_gbs():
    path = REPO / "scripts/music/generate_book_companion_song.py"
    spec = importlib.util.spec_from_file_location("generate_book_companion_song", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_extract_snippets_from_sample_book(tmp_path: Path):
    gbs = _load_gbs()
    book = tmp_path / "book.txt"
    book.write_text(
        "Chapter 1\n\n"
        "Body para one.\n\n"
        "--- Music — chapter opening ---\n\n"
        "Some lyric lines that are long enough to count as a snippet for testing purposes here.\n\n"
        "More body.\n",
        encoding="utf-8",
    )
    snips = gbs._extract_music_snippets(book.read_text(encoding="utf-8"))
    assert snips


def test_build_prompt_shape():
    gbs = _load_gbs()
    p = gbs.build_musicgen_prompt(
        snippets=["a" * 50, "b" * 50],
        genre="indie folk",
        theme="recovery",
        topic="anxiety",
    )
    assert "60 seconds" in p
    assert "no vocals" in p


def test_cli_writes_json(tmp_path: Path):
    gbs = _load_gbs()
    book = tmp_path / "book.txt"
    book.write_text(
        "Chapter 1\n\nhello\n\n--- Music — reflection beat ---\n\n" + "x" * 120 + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "companion.json"
    old = sys.argv
    try:
        sys.argv = [
            "generate_book_companion_song.py",
            "--book-output",
            str(book),
            "--musician-id",
            "test_artist_alpha",
            "--out",
            str(out),
        ]
        assert gbs.main() == 0
    finally:
        sys.argv = old
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["audio_status"] == "deferred"
    assert "musicgen_prompt" in data

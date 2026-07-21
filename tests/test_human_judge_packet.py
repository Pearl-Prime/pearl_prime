from __future__ import annotations

from pathlib import Path

from scripts.qa.build_human_judge_packet import build_packet, split_chapters


def test_split_chapters_extracts_numbered_chapters():
    chapters = split_chapters("Chapter 1: Start\nWords here.\n\nChapter 2: Next\nMore words.")

    assert [c[0] for c in chapters] == ["chapter_001", "chapter_002"]


def test_human_judge_packet_is_advisory_only(tmp_path):
    book = tmp_path / "artifacts" / "qa" / "packet" / "book.txt"
    book.parent.mkdir(parents=True)
    body = " ".join(["This chapter has enough words for sampling."] * 40)
    book.write_text(f"Chapter 1: Test\n{body}\n\nChapter 2: Test\n{body}", encoding="utf-8")

    packet = build_packet(tmp_path, max_samples=2)

    assert packet["hard_ship_gate_created"] is False
    assert packet["production_public_release_authorized"] is False
    assert packet["operator_ratings_needed"] is True
    assert packet["stats"]["chapters_selected"] == 2

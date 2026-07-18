"""Tests for manga story excellence realization gate."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from phoenix_v4.manga.modern_reader_context import (
    canonical_genre_ids,
    validate_modern_reader_doctrine,
)
from phoenix_v4.manga.qc.gate_registry import load_gate_registry
from phoenix_v4.manga.story_quality import evaluate_story_excellence

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "tests/fixtures/manga/story_excellence"
CLI = REPO / "scripts/manga/validate_story_excellence.py"

EXCELLENCE_GATE_IDS = {
    "MANGA.STORY.RESEARCH_DOCTRINE_COVERAGE",
    "MANGA.STORY.ARCHITECT_CONTEXT",
    "MANGA.STORY.ALIAS_COHERENCE",
    "MANGA.STORY.MODERN_READER_REALIZATION",
    "MANGA.STORY.GENRE_CORE_PLEASURE",
    "MANGA.STORY.INTERACTION_REALIZATION",
    "MANGA.STORY.PAGE_ONE_HOOK",
    "MANGA.STORY.MARKET_NATIVE_SURFACE",
    "MANGA.STORY.BLAND_FALLBACK_LINT",
    "MANGA.STORY.REPAIR_PACKET",
}


def _load_pair(folder: Path) -> tuple[dict, dict]:
    story = json.loads((folder / "story_architecture_handoff.json").read_text())
    script = json.loads((folder / "chapter_script_writer_handoff.json").read_text())
    return story, script


def test_doctrine_valid_and_covers_canonical_genres():
    assert validate_modern_reader_doctrine() == []
    assert len(canonical_genre_ids()) == 25


def test_gate_registry_includes_excellence_ids_without_dropping_wired_rows():
    gates = load_gate_registry()
    ids = {g.gate_id for g in gates}
    # pre-existing wired anchors must remain
    assert "MANGA.CHAPTER.HOOK" in ids
    assert "MANGA.BESTSELLER.SUBSTANCE" in ids
    assert "STRUCT.CHAPTER_SCRIPT_VALID" in ids
    missing = EXCELLENCE_GATE_IDS - ids
    assert not missing, f"missing excellence gate registry rows: {sorted(missing)}"


@pytest.mark.parametrize(
    "name",
    sorted(p.name for p in (FIX / "pass").iterdir() if p.is_dir()),
)
def test_pass_fixtures(name: str):
    story, script = _load_pair(FIX / "pass" / name)
    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=script,
        production=True,
        repo_root=REPO,
    )
    assert report["status"] == "PASS", report
    assert report["score"] >= 85
    assert report["repair_packet"] is None
    # immutability
    story2, script2 = _load_pair(FIX / "pass" / name)
    assert story == story2 and script == script2


@pytest.mark.parametrize(
    "name",
    sorted(p.name for p in (FIX / "block").iterdir() if p.is_dir()),
)
def test_block_fixtures(name: str):
    story, script = _load_pair(FIX / "block" / name)
    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=script,
        production=True,
        repo_root=REPO,
    )
    assert report["status"] == "BLOCKED", report
    assert report["repair_packet"] is not None
    assert report["repair_packet"]["repair_scope"] in {
        "rewrite_opening_pages",
        "rewrite_chapter",
        "regenerate_architecture",
    }
    assert report["repair_packet"]["failed_gate_ids"]


def test_mention_only_modern_object_fails_realization():
    story, script = _load_pair(FIX / "block" / "mention_only_phone_train")
    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=script,
        production=True,
        repo_root=REPO,
    )
    failed = {g["gate_id"] for g in report["gates"] if g["status"] == "BLOCKED"}
    assert "MANGA.STORY.MODERN_READER_REALIZATION" in failed
    assert "MANGA.STORY.BLAND_FALLBACK_LINT" in failed


def test_cli_pass_and_block_exit_codes(tmp_path: Path):
    pass_dir = FIX / "pass" / "dark_fantasy_ja_jp_genz"
    out = tmp_path / "report.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--story-handoff",
            str(pass_dir / "story_architecture_handoff.json"),
            "--chapter-script",
            str(pass_dir / "chapter_script_writer_handoff.json"),
            "--production",
            "--out",
            str(out),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert out.is_file()
    assert json.loads(out.read_text())["status"] == "PASS"

    block_dir = FIX / "block" / "mention_only_phone_train"
    proc2 = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--story-handoff",
            str(block_dir / "story_architecture_handoff.json"),
            "--chapter-script",
            str(block_dir / "chapter_script_writer_handoff.json"),
            "--production",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert proc2.returncode == 2


def test_report_schema_shape():
    story, script = _load_pair(FIX / "pass" / "romance_en_us_genz")
    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=script,
        production=True,
        repo_root=REPO,
    )
    schema = json.loads(
        (REPO / "schemas/manga/story_excellence_realization_report.schema.json").read_text()
    )
    assert report["schema_version"] == schema["properties"]["schema_version"]["const"]
    assert report["artifact_type"] == schema["properties"]["artifact_type"]["const"]
    assert report["status"] in schema["properties"]["status"]["enum"]

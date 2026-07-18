"""CI story-engine batch audit — architect probe + script scan."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.manga.qc.story_engine_audit import (
    audit_architect_governed_genres,
    audit_chapter_script_engine,
)
from phoenix_v4.manga.story_engine_loader import is_engine_governed

REPO = Path(__file__).resolve().parents[2]


def test_architect_probe_all_governed_genres_pass():
    rows = audit_architect_governed_genres(REPO)
    assert rows
    fails = [r for r in rows if r["status"] == "FAIL"]
    assert not fails, fails


def test_cultivation_martial_in_architect_probe():
    rows = audit_architect_governed_genres(REPO)
    cult = [r for r in rows if r["engine_genre"] == "cultivation_martial"]
    assert len(cult) == 1
    assert cult[0]["status"] == "PASS"


def test_pilot_cultivation_script_engine_audit():
    pilot = (
        REPO
        / "artifacts/manga/pilots/wave2/the_mountain_does_not_move__ep_001.chapter_script.yaml"
    )
    if not pilot.is_file():
        return
    row = audit_chapter_script_engine(pilot, repo_root=REPO)
    assert is_engine_governed("cultivation_martial")
    assert row["governed"] == "yes"
    assert row["status"] in ("PASS", "FAIL")

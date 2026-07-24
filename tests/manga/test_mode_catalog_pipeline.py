from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.manga.chapter.writer import build_chapter_writer_prompt
from phoenix_v4.manga.mode.catalog import (
    active_music_brands,
    apply_brand_mode,
    build_mode_source_packet,
)
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
from phoenix_v4.manga.transmission import story_architecture_internal_to_handoff
from scripts.manga.generate_mode_brand_catalog import build_mode_catalog

REPO = Path(__file__).resolve().parents[2]


def test_catalog_routes_teacher_and_active_music_brand():
    teacher = apply_brand_mode({
        "series_id": "teacher-s", "brand_id": "stillness_press", "teacher_id": "ahjan"
    })
    assert teacher["mode"] == "teacher"
    assert teacher["teacher_id"] == "ahjan"
    assert teacher["musician_id"] is None

    assert active_music_brands()["ahjan_music"] == "ahjan"
    music = apply_brand_mode({
        "series_id": "music-s", "brand_id": "ahjan_music", "teacher_id": None
    })
    assert music["mode"] == "music"
    assert music["musician_id"] == "ahjan"
    assert music["teacher_id"] is None


def test_source_packets_load_real_banks_and_are_deterministic():
    teacher_plan = apply_brand_mode({
        "series_id": "mecha-ahjan", "brand_id": "stillness_press", "teacher_id": "ahjan"
    })
    first = build_mode_source_packet(teacher_plan, topic="burnout", seed="fixed")
    second = build_mode_source_packet(teacher_plan, topic="burnout", seed="fixed")
    assert first == second
    assert first and first["doctrine_excerpts"]
    assert all("placeholder" not in x.lower() for x in first["doctrine_excerpts"])

    music_plan = apply_brand_mode({
        "series_id": "horror-ahjan", "brand_id": "ahjan_music", "teacher_id": None
    })
    packet = build_mode_source_packet(music_plan, topic="trauma_recovery", seed="fixed")
    assert packet and packet["mode"] == "music"
    assert set(packet["motif_atoms"]) == {
        "lyric_opening", "lyric_bestseller_beat", "lyric_closing"
    }


def test_declared_mode_fails_closed_without_identity():
    with pytest.raises(Exception):
        apply_brand_mode({"series_id": "broken", "brand_id": "x", "mode": "teacher"})


@pytest.mark.parametrize(
    "genre,brand_id,teacher_id,musician_id,mode,source_marker",
    [
        ("mecha", "stillness_press", "ahjan", None, "teacher", "doctrine_excerpts"),
        ("psychological_horror", "ahjan_music", None, "ahjan", "music", "motif_atoms"),
    ],
)
def test_identity_reaches_architect_handoff_and_writer(
    genre, brand_id, teacher_id, musician_id, mode, source_marker
):
    internal = build_story_architecture_internal(
        series_id=f"{mode}-pipeline",
        arc_id="arc-1",
        genre_id=genre,
        topic="burnout" if mode == "teacher" else "trauma_recovery",
        mode=mode,
        teacher_id=teacher_id,
        musician_id=musician_id,
        brand_id=brand_id,
    )
    assert internal["mode"] == mode
    assert source_marker in internal["mode_vessel"]["source_packet"]
    handoff = story_architecture_internal_to_handoff(internal)
    assert handoff.get("teacher_id") == teacher_id
    assert handoff.get("musician_id") == musician_id
    prompt = build_chapter_writer_prompt(
        handoff,
        chapter_number=1,
        series_id=internal["series_id"],
        chapter_id="ep-1",
    )
    assert "identity source" in prompt
    assert ("Never paste a lecture" if mode == "teacher" else "Never explain the lesson") in prompt


def test_active_music_brand_gets_all_fifteen_genres():
    plans = build_mode_catalog(brand_id="ahjan_music", locale="en_US")
    assert len(plans) == 15
    assert len({p["genre"] for p in plans}) == 15
    assert all(p["mode"] == "music" and p["musician_id"] == "ahjan" for p in plans)

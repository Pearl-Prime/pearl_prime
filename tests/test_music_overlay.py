from phoenix_v4.planning.music_overlay import plan_music_injection, summarize_injection_plan


def test_plan_music_injection_with_lyrics_counts():
    pts = plan_music_injection(chapter_count=2, music_mode="with-lyrics")
    assert len(pts) == 12  # 6 per chapter
    assert pts[0].chapter_index == 0
    assert summarize_injection_plan(pts)["total"] == 12


def test_plan_music_injection_no_lyrics_smaller():
    pts = plan_music_injection(chapter_count=3, music_mode="no-lyrics")
    assert len(pts) == 9
    assert summarize_injection_plan(pts)["total"] == 9


def test_plan_none():
    assert plan_music_injection(chapter_count=5, music_mode="none") == []

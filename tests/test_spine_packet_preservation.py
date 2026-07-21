"""Spine packet preservation — repeated authored slots + planner duplicate guards."""
from __future__ import annotations

from phoenix_v4.planning.enrichment_select import (
    EnrichedSlot,
    chapter_composite_sentence_overlap_violations,
    chapter_duplicate_doctrine_source_violations,
)
from phoenix_v4.rendering.chapter_composer import (
    compose_additive_chapter_prose,
    compose_chapter_prose,
    compose_ordered_chapter_prose,
    _requires_additive_compose,
)
from phoenix_v4.rendering.golden_chapter_synthesis import build_ordered_slot_streams


class _Slot:
    def __init__(self, slot_type: str, content: str):
        self.slot_type = slot_type
        self.content = content


def test_build_virtual_slot_streams_preserves_repeated_story_reflection_doctrine() -> None:
    story_a = (
        "David tells his wife he is burned out. The words leave his mouth and the shame "
        "ignites. His face is fire. His hands grip the kitchen counter."
    )
    story_b = (
        "There was a moment — right after the team meeting — where everything went quiet. "
        "Not peaceful quiet. The kind of quiet where the empty tank gets louder."
    )
    reflection_a = (
        "You are not failing at rest; you have been resting in a way that does not restore. "
        "Maybe you have tried. You took the weekend."
    )
    reflection_b = (
        "What contemplative practitioners keep rediscovering is simple: start where you actually are. "
        "You are not failing at rest; you have been resting in a way that does not restore."
    )
    doctrine = (
        "Doing less is the treatment, even when doing less feels unbearable. "
        "For most of a working life, the answer to falling behind is to do more."
    )
    slots = [
        _Slot("HOOK", "Your team had a good quarter."),
        _Slot("STORY", story_a),
        _Slot("REFLECTION", reflection_a),
        _Slot("EXERCISE", "Notice your jaw right now."),
        _Slot("STORY", story_b),
        _Slot("TEACHER_DOCTRINE", doctrine),
        _Slot("REFLECTION", reflection_b),
        _Slot("INTEGRATION", "The burnout you are carrying does not stay with you."),
    ]
    types_, proses = build_ordered_slot_streams(slots, chapter_index0=1)
    assert types_ == [
        "HOOK", "STORY", "REFLECTION", "EXERCISE", "STORY",
        "TEACHER_DOCTRINE", "REFLECTION", "INTEGRATION",
    ]
    assert proses[1] == story_a
    assert proses[4] == story_b
    assert proses[2] == reflection_a
    assert proses[6] == reflection_b
    assert proses[5] == doctrine


def test_compose_chapter_prose_additive_path_preserves_all_authored_words() -> None:
    story_a = "Story alpha with enough words to survive any short-block filter easily here."
    story_b = "Story beta with different words so dedupe would have dropped it previously."
    reflection_a = "Reflection alpha teaches rest without restoring the nervous system yet."
    reflection_b = "Reflection beta asks what your rest actually consists of each evening."
    types = ["HOOK", "STORY", "REFLECTION", "STORY", "REFLECTION"]
    proses = ["Hook line.", story_a, reflection_a, story_b, reflection_b]
    assert _requires_additive_compose(types)
    out = compose_chapter_prose(types, proses, chapter_index=1, arc_thesis="Thesis line.")
    for block in (story_a, story_b, reflection_a, reflection_b):
        assert block in out
    assert out.index(story_a) < out.index(reflection_a) < out.index(story_b) < out.index(reflection_b)


def test_compose_additive_chapter_prose_no_word_loss() -> None:
    blocks = [
        "Block one preserves every authored word without truncation or replacement.",
        "Block two is wholly different so prefix dedupe cannot silently erase it.",
    ]
    out = compose_additive_chapter_prose(["REFLECTION", "REFLECTION"], blocks)
    assert blocks[0] in out
    assert blocks[1] in out
    assert out.count("Block one") == 1
    assert out.count("Block two") == 1


def test_compose_additive_chapter_prose_defers_scene_adjacent_and_back_to_back_stories() -> None:
    scene = (
        "Priya's bedroom is dark except for the laptop screen. The send button waits in the corner."
    )
    story_open = (
        "Priya submits the project update at 11:47pm. The message leaves her hands before her chest agrees."
    )
    story_mid = (
        "Priya wakes to the calendar already running in her body. The first meeting is still an hour away."
    )
    story_close = (
        "Priya leaves a fifteen-minute block empty and discovers the day does not collapse around it."
    )
    pivot = "The first useful distinction is between the alarm and the story the alarm writes."
    reflection = "Your body is rehearsing a future that has not happened yet."
    takeaway = "The weather of the body is not the climate of the self."
    types = [
        "HOOK",
        "SCENE",
        "STORY",
        "PIVOT",
        "REFLECTION",
        "EXERCISE",
        "STORY",
        "STORY",
        "TAKEAWAY",
        "THREAD",
    ]
    proses = [
        "You sent it and your chest never got the receipt.",
        scene,
        story_open,
        pivot,
        reflection,
        "Take one slow exhale before you check the phone again.",
        story_mid,
        story_close,
        takeaway,
        "The next chapter begins where the body keeps score.",
    ]

    out = compose_chapter_prose(types, proses, chapter_index=1, total_chapters=12)

    for block in (scene, story_open, story_mid, story_close, pivot, reflection, takeaway):
        assert block in out
    assert out.index(scene) < out.index(pivot) < out.index(story_open)
    assert out.index(reflection) < out.index(story_mid) < out.index(takeaway) < out.index(story_close)


def test_compose_ordered_chapter_prose_preserves_strict_slot_order() -> None:
    """Flagship ordered path must stay 1:1 — deferral would break beat fingerprints."""
    scene = "Priya waits in the blue light of the laptop, still not pressing send."
    story_open = "Priya submits the update at 11:47pm and checks Slack again before the room changes."
    pivot = "The first distinction is between the alarm and the story it writes."
    story_mid = "Priya wakes to the calendar already running in her body before she stands up."
    story_close = "Priya leaves a fifteen-minute block empty and learns the day can stay standing."
    takeaway = "The weather of the body is not the climate of the self."

    out = compose_ordered_chapter_prose(
        [
            "HOOK",
            "ANGLE_DEFINITION",
            "SCENE",
            "STORY",
            "PIVOT",
            "REFLECTION",
            "EXERCISE",
            "STORY",
            "STORY",
            "TAKEAWAY",
            "THREAD",
        ],
        [
            "You sent it and your chest never got the receipt.",
            "Anxiety is a protective alarm, not a character flaw.",
            scene,
            story_open,
            pivot,
            "Your body is rehearsing a future that has not happened yet.",
            "Take one slow exhale before you check the phone again.",
            story_mid,
            story_close,
            takeaway,
            "The next chapter begins where the body keeps score.",
        ],
    )

    assert out.index(scene) < out.index(story_open) < out.index(pivot)
    assert out.index(story_mid) < out.index(story_close) < out.index(takeaway)


def test_chapter_duplicate_doctrine_source_violations_detects_slot_pair() -> None:
    slots = [
        EnrichedSlot("REFLECTION", "a", "composite_doctrine", "COMPOSITE_DOCTRINE v02", 100, 50, []),
        EnrichedSlot("EXERCISE", "b", "persona_atom", "EXERCISE v09", 30, 30, []),
        EnrichedSlot("REFLECTION", "c", "composite_doctrine", "COMPOSITE_DOCTRINE v02", 100, 50, []),
    ]
    violations = chapter_duplicate_doctrine_source_violations(slots)
    assert len(violations) == 1
    assert violations[0]["slot_index"] == 3
    assert violations[0]["source_id"] == "COMPOSITE_DOCTRINE v02"


def test_chapter_composite_sentence_overlap_violations_detects_shared_packet_body() -> None:
    slots = [
        EnrichedSlot(
            "REFLECTION",
            (
                "You are not failing at rest; you have been resting in a way that does not restore. "
                "You keep calling collapse recovery because no one taught you a gentler pace. "
                "Maybe you have tried. You took the weekend. You sat down."
            ),
            "composite_doctrine",
            "COMPOSITE_DOCTRINE v02",
            100,
            50,
            [],
        ),
        EnrichedSlot(
            "TEACHER_DOCTRINE",
            (
                "What contemplative practitioners keep rediscovering is simple: start where you actually are. "
                "You are not failing at rest; you have been resting in a way that does not restore. "
                "You keep calling collapse recovery because no one taught you a gentler pace. "
                "Maybe you have tried. You took the weekend."
            ),
            "composite_doctrine",
            "COMPOSITE_DOCTRINE v01",
            100,
            50,
            [],
        ),
    ]
    violations = chapter_composite_sentence_overlap_violations(slots)
    assert len(violations) == 1
    assert violations[0]["slot_index_a"] == 1
    assert violations[0]["slot_index_b"] == 2
    assert violations[0]["shared_sentence_count"] >= 2


def test_burnout_ch2_duplicate_guard_reroutes_second_reflection() -> None:
    """Repro target: seed 4242 ch2 slot 7 must not reuse slot 3 doctrine id."""
    from pathlib import Path

    from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
    from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine

    repo = Path(__file__).resolve().parents[1]
    topic, persona, seed = "burnout", "corporate_managers", "4242"
    fmt = load_format_spec("standard_book", repo)
    spine = load_spine(topic, repo, runtime_format="standard_book")
    shaped = apply_knobs(spine, load_knob_profile(topic, repo), runtime_format="standard_book")
    bm = compile_beatmap(shaped, load_topic_engines(topic, repo), fmt, repo_root=repo)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id=persona,
            topic_id=topic,
            seed=seed,
        ),
        repo_root=repo,
    )
    ch = book.chapters[1]
    doctrine_ids = [
        s.source_id
        for s in ch.slots
        if s.slot_type.strip().upper() in {"REFLECTION", "TEACHER_DOCTRINE"}
        and "composite" in (s.source or "")
    ]
    assert doctrine_ids[0] == "COMPOSITE_DOCTRINE v02"
    assert doctrine_ids[1] != doctrine_ids[0]
    assert chapter_duplicate_doctrine_source_violations(ch.slots) == []
    assert chapter_composite_sentence_overlap_violations(ch.slots) == []

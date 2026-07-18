from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.rendering import chapter_composer as cc


@pytest.fixture(autouse=True)
def _enable_render_glue_for_exercise_wrapper_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise wrapper tests exercise template glue; production default is OFF."""
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
    monkeypatch.setenv("PHOENIX_EXERCISE_WRAPPER_FAMILIES", "1")
    monkeypatch.setenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", "1")
    cc._EXERCISE_WRAPPER_CACHE = None
    cc._BRIDGE_TRANSITION_CACHE = None


def test_setup_sentence_varies_by_emotional_job() -> None:
    reflection = "Tension rises before the message arrives."
    story = "You keep reading the same line."
    a = cc._exercise_setup_sentence(reflection, story, emotional_job="recognition", practice_type="grounding", exercise_memory=cc.ExerciseWrapperMemory())
    b = cc._exercise_setup_sentence(reflection, story, emotional_job="practice", practice_type="grounding", exercise_memory=cc.ExerciseWrapperMemory())
    assert a != b


def test_same_practice_type_different_jobs_routes_differently() -> None:
    a = cc._bridge_before_exercise("thesis", reflection="r", story="s", emotional_job="mechanism", practice_type="breath_regulation", exercise_memory=cc.ExerciseWrapperMemory())
    b = cc._bridge_before_exercise("thesis", reflection="r", story="s", emotional_job="integration", practice_type="breath_regulation", exercise_memory=cc.ExerciseWrapperMemory())
    assert a != b


def test_exact_wrapper_phrase_not_reused_in_book() -> None:
    memory = cc.ExerciseWrapperMemory()
    seen: set[str] = set()
    for i in range(12):
        cc._CHAPTER_INDEX_TLS = i
        phrase = cc._bridge_before_integration(
            "thesis",
            integration="integration",
            emotional_job=["recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"][i % 7],
            practice_type="integration_pause",
            exercise_memory=memory,
        )
        assert phrase not in seen
        seen.add(phrase)


def test_validation_stem_not_overused_adjacent() -> None:
    memory = cc.ExerciseWrapperMemory()
    for i in range(12):
        cc._CHAPTER_INDEX_TLS = i
        cc._post_practice_validation_sentence(
            emotional_job=["recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"][i % 7],
            practice_type="grounding",
            exercise_memory=memory,
        )
    for idx in range(1, 12):
        stems = memory.stem_usage_by_chapter.get(idx, {})
        for stem in stems:
            total = sum(memory.stem_usage_by_chapter.get(k, {}).get(stem, 0) for k in range(max(0, idx - 1), idx + 1))
            assert total <= 1


def test_practice_type_routes_to_different_families() -> None:
    memory = cc.ExerciseWrapperMemory()
    cc._CHAPTER_INDEX_TLS = 0
    breath = cc._exercise_setup_sentence("tight focus", "story", emotional_job="practice", practice_type="breath_regulation", exercise_memory=memory)
    cc._CHAPTER_INDEX_TLS = 1
    ground = cc._exercise_setup_sentence("tight focus", "story", emotional_job="practice", practice_type="grounding", exercise_memory=memory)
    assert breath != ground


def test_body_locus_logic_still_fires() -> None:
    assert "sternum" in cc._exercise_setup_sentence("sternum pressure", "story").lower()
    assert "jaw" in cc._exercise_setup_sentence("jaw locks", "story").lower()
    assert "throat" in cc._exercise_setup_sentence("throat tight", "story").lower()


def test_late_jobs_use_softer_transitions() -> None:
    memory = cc.ExerciseWrapperMemory()
    cc._CHAPTER_INDEX_TLS = 0
    practice = cc._bridge_before_integration("thesis", "integration", emotional_job="practice", practice_type="integration_pause", exercise_memory=memory)
    cc._CHAPTER_INDEX_TLS = 1
    resolution = cc._bridge_before_integration("thesis", "integration", emotional_job="resolution", practice_type="integration_pause", exercise_memory=memory)
    assert practice != resolution


def test_yaml_missing_fallback_no_crash(monkeypatch) -> None:
    monkeypatch.setattr(cc, "_EXERCISE_WRAPPER_CACHE", None)
    monkeypatch.setattr(cc, "_EXERCISE_WRAPPER_PATH", Path("/tmp/does_not_exist_exercise.yaml"))
    setup = cc._exercise_setup_sentence("tight chest", "story", emotional_job="practice", practice_type="grounding")
    bridge = cc._bridge_before_exercise("thesis", reflection="r", story="s", emotional_job="practice", practice_type="grounding")
    integration = cc._bridge_before_integration("thesis", integration="i", emotional_job="practice", practice_type="grounding")
    assert setup and bridge and integration


def test_backward_compat_with_empty_job_and_practice() -> None:
    setup = cc._exercise_setup_sentence("tight chest", "story", emotional_job="", practice_type="")
    bridge = cc._bridge_before_exercise("thesis", reflection="r", story="s", emotional_job="", practice_type="")
    integration = cc._bridge_before_integration("thesis", integration="i", emotional_job="", practice_type="")
    assert setup and bridge and integration


def test_bridge_before_integration_varies() -> None:
    memory = cc.ExerciseWrapperMemory()
    outputs = []
    for i, job in enumerate(["recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"]):
        cc._CHAPTER_INDEX_TLS = i
        outputs.append(
            cc._bridge_before_integration(
                "thesis",
                integration="integration",
                emotional_job=job,
                practice_type="integration_pause",
                exercise_memory=memory,
            )
        )
    assert len(set(outputs)) >= 4
    assert any("notice what shifted" not in x.lower() for x in outputs)

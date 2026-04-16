from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from phoenix_v4.rendering.rhetorical_memory import RhetoricalMemory, UsageRecord


def _usage(chapter: int, layer: str, sublayer: str, stem: str, shape: str) -> UsageRecord:
    return UsageRecord(
        chapter_index=chapter,
        layer=layer,
        sublayer=sublayer,
        variant_id=f"{layer}-{chapter}",
        shape=shape,
        register="conversational",
        movement="inward",
        instruction_tone="gentle",
        cadence="medium_flowing",
        abstraction_level="mid_concept",
        root_family="notice",
        stem=stem,
    )


def test_record_and_recent_at_layer() -> None:
    memory = RhetoricalMemory()
    memory.record(_usage(0, "bridge", "after_opening", "stay with the moment", "declarative"))
    memory.record(_usage(1, "bridge", "after_opening", "let it settle now", "interrogative"))
    memory.record(_usage(2, "bridge", "before_story", "watch what unfolds", "declarative"))

    recent = memory.recent_at_layer("bridge", "after_opening", current_chapter=3, window=3)
    assert len(recent) == 2
    assert {r.chapter_index for r in recent} == {0, 1}


def test_stem_used_recently_true_false() -> None:
    memory = RhetoricalMemory()
    memory.record(_usage(1, "thesis", "thesis_frame", "this is the point", "declarative"))

    assert memory.stem_used_recently("thesis", "thesis_frame", "this is the point", 2, window=3)
    assert not memory.stem_used_recently("thesis", "thesis_frame", "another stem", 2, window=3)


def test_same_chapter_other_layers_excludes_current_layer() -> None:
    memory = RhetoricalMemory()
    memory.record(_usage(4, "bridge", "before_story", "let us notice this", "declarative"))
    memory.record(_usage(4, "exercise", "setup", "keep the breath soft", "imperative"))

    others = memory.same_chapter_other_layers(4, exclude_layer="bridge")
    assert len(others) == 1
    assert others[0].layer == "exercise"


def test_dimension_ratio_math() -> None:
    memory = RhetoricalMemory()
    memory.record(_usage(0, "bridge", "after_opening", "a stem", "declarative"))
    memory.record(_usage(1, "bridge", "after_opening", "b stem", "declarative"))
    memory.record(_usage(2, "bridge", "after_opening", "c stem", "interrogative"))

    assert memory.dimension_ratio("shape", "declarative") == 2 / 3
    assert memory.dimension_ratio("shape", "interrogative") == 1 / 3


def test_record_thread_safety_concurrent_writes() -> None:
    memory = RhetoricalMemory()

    def writer(i: int) -> None:
        memory.record(
            _usage(
                chapter=i % 20,
                layer="bridge",
                sublayer="before_story",
                stem=f"stem {i}",
                shape="declarative" if i % 2 == 0 else "interrogative",
            )
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(writer, range(200)))

    assert memory.total_selections == 200
    assert memory.dimension_ratio("shape", "declarative") == 0.5


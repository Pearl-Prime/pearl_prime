"""Generalized teacher-wrapper book-wide rotation (phrase-density lane)."""

from __future__ import annotations

from phoenix_v4.rendering.teacher_wrapper import (
    WrapperUsageMemory,
    _pick_variant,
    apply_wrapper,
    resolve_wrapper,
)


def test_pick_variant_spreads_usage_under_book_cap() -> None:
    variants = [
        "{TRADITION} teaches that change starts with what you can feel right now.",
        "I came across this teaching tradition at a time when nothing else was landing.",
        "Rooted in {TRADITION}, this approach holds that presence comes before strategy.",
    ]
    slots = {
        "TRADITION": "the contemplative tradition",
        "TRADITION_SHORT": "contemplative",
    }
    memory = WrapperUsageMemory(book_cap=3)
    picks: list[str] = []
    for i in range(9):
        chosen = _pick_variant(variants, slots, f"seed:ch{i}", usage_memory=memory)
        assert chosen
        memory.record(chosen)
        picks.append(chosen)
    assert max(memory._counts.values()) <= 3


def test_generalized_wrapper_rotates_across_chapters() -> None:
    memory = WrapperUsageMemory(book_cap=11)
    body = "Every person carries the capacity for awakening."
    seen_prefixes: set[str] = set()
    for ch in range(1, 15):
        out = apply_wrapper(
            body,
            teacher_id="__generalized__",
            section_type="REFLECTION",
            seed=f"4242:topic:burnout:ch{ch}:slot:1:REFLECTION:composite",
            spine_context={},
            usage_memory=memory,
        )
        prefix = out.split("\n\n", 1)[0]
        seen_prefixes.add(prefix)
    assert len(seen_prefixes) >= 3


def test_ngram_load_prefers_low_collision_variant() -> None:
    variants = [
        "{TRADITION} teaches that change starts with what you can feel right now.",
        "Across {TRADITION_SHORT} teaching, the first move is to feel the body before you explain it.",
    ]
    slots = {
        "TRADITION": "the contemplative tradition",
        "TRADITION_SHORT": "contemplative",
    }
    memory = WrapperUsageMemory(book_cap=11)
    first = _pick_variant(variants, slots, "seed:1", usage_memory=memory)
    assert first
    memory.record(first)
    second = _pick_variant(variants, slots, "seed:2", usage_memory=memory)
    assert second and second != first

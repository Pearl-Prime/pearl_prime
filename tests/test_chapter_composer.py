from __future__ import annotations

import pytest

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
from phoenix_v4.rendering.chapter_composer import compose_chapter_prose


def test_compose_chapter_applies_overlay_craft_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    # Exercise setup glue is part of the overlay craft path; production default is OFF.
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
    monkeypatch.setenv("PHOENIX_EXERCISE_WRAPPER_FAMILIES", "1")
    slots = ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
    proses = [
        "You reread the message before your feet hit the floor.",
        (
            "Your inbox is open on the laptop. gray light through the window on the glass. "
            "Your thumb hovers over reply. It does not land."
        ),
        (
            "Maya opens the draft and rewrites the first line six times. "
            "Her chest tightens before she touches the keyboard. "
            "She finally sends two rough sentences. Nobody mocks her. "
            "The disaster she rehearsed does not happen, but her body has already paid for it."
        ),
        (
            "Anxiety predicts regret so loudly that it blocks useful choice. "
            "The mechanism asks for perfect certainty and calls everything less a threat. "
            "Your sternum stays tight because your system is still bargaining with an imaginary future."
        ),
        "Exhale for six. Name the cost. Write one rough sentence. Keep moving.",
        (
            "Still here. Your chest is not loose yet, but it is no longer locked. "
            "That small drop in pressure is enough to take back into the day."
        ),
    ]

    chapter = compose_chapter_prose(slots, proses, chapter_index=0, total_chapters=6)
    lower = chapter.lower()

    assert "that moment matters because" not in lower
    assert "so this is not just your private glitch" not in lower
    assert "what this means going forward is simple" not in lower
    assert "gray light through the window" not in lower
    assert "start with the pressure under the sternum" in lower
    assert "in the next chapter" not in lower

    result = evaluate_chapter_flow(chapter)
    assert result.status == "PASS", result.errors


def test_compose_chapter_cleans_location_placeholder_collisions() -> None:
    slots = ["HOOK", "SCENE", "REFLECTION"]
    proses = [
        "You are trying to stay in the room.",
        (
            "Your manager's door is open. Fluorescent tunnel light smears across the window "
            "through the window behind their desk. The chair across from them is empty."
        ),
        (
            "The alarm fires before evidence arrives. The point is not to erase the alarm. "
            "The point is to stop treating it like final truth."
        ),
    ]

    chapter = compose_chapter_prose(slots, proses, chapter_index=0, total_chapters=1)

    assert "through the window through the window" not in chapter.lower()
    assert "smears across the window through the window" not in chapter.lower()

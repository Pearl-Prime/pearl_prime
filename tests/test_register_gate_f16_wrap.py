"""F16 / G-WRAP — exercise-wrapper stem spam across chapters."""
from __future__ import annotations

from phoenix_v4.quality.register_gate import (
    F16_WRAPPER_CHAPTER_LIMIT,
    evaluate_register,
)


def test_f16_hard_fails_when_wrapper_in_four_plus_chapters():
    stem = "Now we are going to shift"
    assert F16_WRAPPER_CHAPTER_LIMIT == 4
    parts = []
    for i in range(1, 5):
        parts.append(
            f"Chapter {i}\n\n"
            f"{stem} into a practice for chapter {i}. "
            f"The body settles. A longer paragraph keeps F1 quiet here with "
            f"unique words about breath and shoulders and the desk lamp {i}.\n"
        )
    body = "\n".join(parts)
    result = evaluate_register(body, quality_profile="production")
    f16 = [f for f in result.findings if f.failure_id == "F16"]
    assert f16, "expected F16 finding for wrapper stem in 4 chapters"
    assert any(f.severity == "HARD_FAIL" for f in f16)
    assert result.verdict == "HARD_FAIL"


def test_f16_ok_when_wrapper_in_fewer_chapters():
    stem = "Now we are going to shift"
    body = (
        f"Chapter 1\n\n{stem} once.\n\n"
        f"Chapter 2\n\nA clean chapter without the stem.\n\n"
        f"Chapter 3\n\n{stem} again but only twice total chapters.\n"
    )
    result = evaluate_register(body, quality_profile="production")
    f16_hard = [
        f
        for f in result.findings
        if f.failure_id == "F16" and f.severity == "HARD_FAIL"
    ]
    assert not f16_hard

"""Twelve-shape plan validation — doctrine pool v01–v15."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.chapter_object_continuity import (
    assert_twelve_shape_plan,
    validate_twelve_shape_plan,
)


def _chapter(n: int, doctrine: str) -> dict:
    return {
        "chapter": n,
        "character": "Priya",
        "object": f"object_{n}",
        "doctrine_id": doctrine,
        "exercise_id": f"med_{n:03d}",
    }


def test_validate_accepts_v06_through_v15() -> None:
    chapters = [
        _chapter(n, f"COMPOSITE_DOCTRINE v{((n - 1) % 15) + 1:02d}") for n in range(1, 13)
    ]
    assert validate_twelve_shape_plan(chapters) == []


def test_validate_rejects_phantom_v16() -> None:
    chapters = [_chapter(n, f"COMPOSITE_DOCTRINE v{(n % 15) + 1:02d}") for n in range(1, 13)]
    chapters[11] = _chapter(12, "COMPOSITE_DOCTRINE v16")
    errors = validate_twelve_shape_plan(chapters)
    assert any("phantom doctrine" in e and "v16" in e for e in errors)


def test_distinct_sequence_file_ch1_locked() -> None:
    from pathlib import Path

    import yaml

    path = (
        Path(__file__).resolve().parents[3]
        / "config/source_of_truth/twelve_shape_chapter_plans"
        / "gen_z_professionals_anxiety_distinct_doctrine_sequence.yaml"
    )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    by_ch = {int(k): v for k, v in (data.get("doctrine_by_chapter") or {}).items()}
    assert by_ch[1] == "COMPOSITE_DOCTRINE v03"
    assert len(set(by_ch.values())) == 12
    assert_twelve_shape_plan(
        [
            {
                "chapter": ch,
                "character": "Priya",
                "object": "x",
                "doctrine_id": did,
                "exercise_id": "med_001",
            }
            for ch, did in sorted(by_ch.items())
        ]
    )

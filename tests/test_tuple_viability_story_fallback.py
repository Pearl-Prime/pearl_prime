from pathlib import Path

from phoenix_v4.gates.check_tuple_viability import check_tuple_viability


def _write_minimal_tuple(root: Path) -> None:
    (root / "config" / "source_of_truth" / "master_arcs").mkdir(parents=True)
    (root / "config" / "topic_engine_bindings.yaml").write_text(
        "anxiety:\n  allowed_engines:\n    - false_alarm\n",
        encoding="utf-8",
    )
    (root / "config" / "gates.yaml").write_text(
        "tuple_viability:\n  min_story_pool_size: 1\n",
        encoding="utf-8",
    )
    (root / "config" / "source_of_truth" / "master_arcs" / "persona__anxiety__false_alarm__F006.yaml").write_text(
        "emotional_curve: [3]\n",
        encoding="utf-8",
    )
    story_dir = root / "atoms" / "persona" / "anxiety" / "STORY"
    story_dir.mkdir(parents=True)
    (story_dir / "CANONICAL.txt").write_text(
        "## STORY v01\n---\nA usable generic story lands here.\n---\n",
        encoding="utf-8",
    )


def test_tuple_viability_uses_generic_story_pool_when_engine_bank_missing(tmp_path: Path) -> None:
    _write_minimal_tuple(tmp_path)

    result = check_tuple_viability(
        "persona",
        "anxiety",
        "false_alarm",
        "F006",
        repo_root=tmp_path,
    )

    assert result.status == "PASS"
    assert "NO_STORY_POOL" not in result.errors

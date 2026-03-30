from pathlib import Path

from phoenix_v4.planning.pool_index import _load_teacher_pool


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_teacher_story_band_universal_defaults_to_3(tmp_path: Path) -> None:
    root = tmp_path / "approved_atoms"
    _write_yaml(
        root / "STORY" / "story_universal.yaml",
        "atom_id: adi_da_story_u1\nband: universal\nsource: native\n",
    )

    pool = _load_teacher_pool(root, "STORY")
    assert len(pool) == 1
    assert (pool[0].metadata or {}).get("band") == 3


def test_teacher_story_band_universal_uses_emotional_intensity_band(tmp_path: Path) -> None:
    root = tmp_path / "approved_atoms"
    _write_yaml(
        root / "STORY" / "story_universal_eib.yaml",
        "atom_id: adi_da_story_u2\nband: universal\nemotional_intensity_band: 2\nsource: native\n",
    )

    pool = _load_teacher_pool(root, "STORY")
    assert len(pool) == 1
    assert (pool[0].metadata or {}).get("band") == 2


def test_teacher_story_band_numeric_still_parses(tmp_path: Path) -> None:
    root = tmp_path / "approved_atoms"
    _write_yaml(
        root / "STORY" / "story_numeric.yaml",
        "atom_id: adi_da_story_n1\nband: 4\nsource: native\n",
    )

    pool = _load_teacher_pool(root, "STORY")
    assert len(pool) == 1
    assert (pool[0].metadata or {}).get("band") == 4

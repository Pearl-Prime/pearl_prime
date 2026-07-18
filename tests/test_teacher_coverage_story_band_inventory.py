from pathlib import Path

from phoenix_v4.teacher.coverage_gate import compute_story_band_inventory


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_story_band_inventory_uses_eib_for_universal(tmp_path: Path, monkeypatch) -> None:
    teacher_root = tmp_path / "teacher_banks" / "adi_da" / "approved_atoms" / "STORY"
    _write_yaml(
        teacher_root / "s1.yaml",
        "atom_id: s1\nband: universal\nemotional_intensity_band: 2\n",
    )
    _write_yaml(
        teacher_root / "s2.yaml",
        "atom_id: s2\nband: universal\nemotional_intensity_band: 4\n",
    )
    _write_yaml(
        teacher_root / "s3.yaml",
        "atom_id: s3\nband: 3\n",
    )

    import phoenix_v4.teacher.coverage_gate as cg
    monkeypatch.setattr(cg, "TEACHER_BANKS_ROOT", tmp_path / "teacher_banks")

    out = compute_story_band_inventory("adi_da")
    assert out.get("2") == 1
    assert out.get("4") == 1
    assert out.get("3") == 1

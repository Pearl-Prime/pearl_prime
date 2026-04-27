"""Tests for spec #739 Phase 1 variant-coverage validator.

Builds a synthetic fixture tree under tmp_path so the tests stay isolated
from the live registry/ and atoms/ inventories.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.registry.validate_variant_coverage import (
    REQUIRED_SECTION_TYPES,
    AtomGap,
    RegistryGap,
    check_atoms,
    check_registry,
    count_atom_variants,
    main,
    render_report,
)


def _write_registry(
    registry_dir: Path,
    topic: str,
    sections: list[tuple[str, int]],
    min_required: int = 5,
) -> Path:
    """Build a single-chapter registry YAML with the supplied (type, variant_count) pairs."""
    chapter = {
        "chapter": 1,
        "title": f"{topic} test chapter",
        "sections": {},
    }
    for idx, (sec_type, variant_count) in enumerate(sections, start=1):
        section_key = f"section_{idx:02d}"
        chapter["sections"][section_key] = {
            "section_id": f"ch01_{section_key}",
            "section": idx,
            "type": sec_type,
            "min_variants_required": min_required,
            "variants": [
                {"variant_id": f"ch01_{section_key}_v{j}", "variant_number": j}
                for j in range(1, variant_count + 1)
            ],
        }
    payload = {"sections": {"chapter_01": chapter}}
    registry_dir.mkdir(parents=True, exist_ok=True)
    path = registry_dir / f"{topic}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


def _write_atom_canonical(
    atoms_dir: Path,
    persona: str,
    topic: str,
    section_type: str,
    variant_count: int,
) -> Path:
    target_dir = atoms_dir / persona / topic / section_type
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / "CANONICAL.txt"
    blocks = []
    for n in range(1, variant_count + 1):
        blocks.append(f"## {section_type} v{n:02d}\n---\n\n---\nbody {n}\n---\n")
    path.write_text("\n".join(blocks))
    return path


def test_count_atom_variants_matches_header_count(tmp_path: Path) -> None:
    path = _write_atom_canonical(tmp_path / "atoms", "p1", "anxiety", "HOOK", 7)
    assert count_atom_variants(path) == 7


def test_count_atom_variants_returns_zero_for_missing(tmp_path: Path) -> None:
    assert count_atom_variants(tmp_path / "nope.txt") == 0


def test_check_registry_passes_when_variants_meet_min(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    _write_registry(registry, "anxiety", [("HOOK", 5), ("STORY", 6), ("REFLECTION", 5)])
    passed, gaps = check_registry(registry, min_variants=5)
    assert passed == 3
    assert gaps == []


def test_check_registry_flags_gaps(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    _write_registry(registry, "burnout", [("HOOK", 5), ("STORY", 3), ("EXERCISE", 1)])
    passed, gaps = check_registry(registry, min_variants=5)
    assert passed == 1
    assert {g.section_type for g in gaps} == {"STORY", "EXERCISE"}
    by_type = {g.section_type: g for g in gaps}
    assert by_type["STORY"].have == 3
    assert by_type["STORY"].need == 5
    assert by_type["EXERCISE"].have == 1


def test_check_registry_handles_missing_dir(tmp_path: Path) -> None:
    passed, gaps = check_registry(tmp_path / "does_not_exist", min_variants=5)
    assert passed == 0
    assert gaps == []


def test_check_atoms_passes_when_count_meets_min(tmp_path: Path) -> None:
    atoms = tmp_path / "atoms"
    for st in ("HOOK", "STORY", "REFLECTION"):
        _write_atom_canonical(atoms, "p1", "anxiety", st, 5)
    passed, gaps = check_atoms(
        atoms, ["p1"], ["anxiety"], ("HOOK", "STORY", "REFLECTION"), min_variants=5
    )
    assert passed == 3
    assert gaps == []


def test_check_atoms_flags_below_threshold_and_missing(tmp_path: Path) -> None:
    atoms = tmp_path / "atoms"
    _write_atom_canonical(atoms, "p1", "anxiety", "HOOK", 5)
    _write_atom_canonical(atoms, "p1", "anxiety", "STORY", 2)
    # REFLECTION intentionally absent.
    passed, gaps = check_atoms(
        atoms, ["p1"], ["anxiety"], ("HOOK", "STORY", "REFLECTION"), min_variants=5
    )
    assert passed == 1
    by_type = {g.section_type: g for g in gaps}
    assert by_type["STORY"].reason == "below_threshold"
    assert by_type["STORY"].have == 2
    assert by_type["REFLECTION"].reason == "missing_file"
    assert by_type["REFLECTION"].have == 0


def test_required_section_types_cover_grid_and_beats() -> None:
    grid = {"HOOK", "STORY", "REFLECTION", "EXERCISE", "TEACHER_DOCTRINE", "INTEGRATION"}
    beats = {"PIVOT", "PERMISSION", "TAKEAWAY", "THREAD", "COMPRESSION"}
    assert grid <= set(REQUIRED_SECTION_TYPES)
    assert beats <= set(REQUIRED_SECTION_TYPES)
    assert len(REQUIRED_SECTION_TYPES) == 11


def test_render_report_contains_summary_and_gap_tables() -> None:
    result_with_gaps = type(
        "R",
        (),
        {
            "registry_passed": 4,
            "registry_gaps": [
                RegistryGap("anxiety", "chapter_01", "section_02", "STORY", 3, 5)
            ],
            "atom_passed": 1,
            "atom_gaps": [
                AtomGap("p1", "anxiety", "STORY", 2, 5, "below_threshold"),
                AtomGap("p2", "burnout", "PIVOT", 0, 5, "missing_file"),
            ],
            "total_gaps": 3,
        },
    )()
    report = render_report(result_with_gaps, min_variants=5, today="2026-04-27")
    assert "Variant Coverage Gap Report" in report
    assert "registry sections passing: **4**" in report
    assert "anxiety | chapter_01 | section_02 | STORY | 3 | 5" in report
    assert "p1 | anxiety | STORY | 2 | 5" in report
    assert "Missing tuples by persona" in report
    assert "p2 | burnout | PIVOT" in report


def test_main_warn_only_returns_zero_on_gaps(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    registry = tmp_path / "registry"
    atoms = tmp_path / "atoms"
    _write_registry(registry, "anxiety", [("HOOK", 5), ("STORY", 2)])
    _write_atom_canonical(atoms, "p1", "anxiety", "HOOK", 6)
    report_path = tmp_path / "report.md"
    rc = main(
        [
            "--registry-dir", str(registry),
            "--atoms-dir", str(atoms),
            "--report-out", str(report_path),
            "--persona", "p1",
            "--topic", "anxiety",
            "--quiet",
        ]
    )
    assert rc == 0  # warn-only is the Phase 1 default
    assert report_path.is_file()
    contents = report_path.read_text()
    assert "Variant Coverage Gap Report" in contents
    captured = capsys.readouterr()
    assert "variant-coverage:" in captured.out


def test_main_strict_returns_one_on_gaps(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    atoms = tmp_path / "atoms"
    _write_registry(registry, "anxiety", [("HOOK", 5), ("STORY", 2)])
    _write_atom_canonical(atoms, "p1", "anxiety", "HOOK", 6)
    report_path = tmp_path / "report.md"
    rc = main(
        [
            "--registry-dir", str(registry),
            "--atoms-dir", str(atoms),
            "--report-out", str(report_path),
            "--persona", "p1",
            "--topic", "anxiety",
            "--strict",
            "--quiet",
        ]
    )
    assert rc == 1


def test_main_strict_returns_zero_when_clean(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    atoms = tmp_path / "atoms"
    _write_registry(registry, "anxiety", [("HOOK", 5), ("STORY", 5)])
    for st in REQUIRED_SECTION_TYPES:
        _write_atom_canonical(atoms, "p1", "anxiety", st, 5)
    report_path = tmp_path / "report.md"
    rc = main(
        [
            "--registry-dir", str(registry),
            "--atoms-dir", str(atoms),
            "--report-out", str(report_path),
            "--persona", "p1",
            "--topic", "anxiety",
            "--strict",
            "--quiet",
        ]
    )
    assert rc == 0


def test_main_no_report_skips_disk_write(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    _write_registry(registry, "anxiety", [("HOOK", 5)])
    report_path = tmp_path / "report.md"
    rc = main(
        [
            "--registry-dir", str(registry),
            "--skip-atoms",
            "--report-out", str(report_path),
            "--no-report",
            "--quiet",
        ]
    )
    assert rc == 0
    assert not report_path.exists()

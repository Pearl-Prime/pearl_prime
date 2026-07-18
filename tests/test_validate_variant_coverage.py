"""Tests for spec #739 Phase 1 variant-coverage validator.

Builds a synthetic fixture tree under tmp_path so the tests stay isolated
from the live registry/ and atoms/ inventories.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.registry.validate_variant_coverage import (
    DEFAULT_MIN_VARIANTS,
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


def test_count_atom_variants_handles_dash_variant_format(tmp_path: Path) -> None:
    """Legacy `--- variant: vNN` headers (used by gen_z_professionals + 10
    other personas; ~4% of repo variant headers) must count."""
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "--- variant: v01\nbody one\n\n--- variant: v02\nbody two\n\n--- variant: v03\nbody three\n"
    )
    assert count_atom_variants(path) == 3


def test_count_atom_variants_handles_typed_dash_variant_format(tmp_path: Path) -> None:
    """Rare `--- variant: TYPE vNN` typed dash form (~9 instances repo-wide)
    must also count under the same regex."""
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "--- variant: EMBODIMENT v01\nbody one\n\n"
        "--- variant: MECHANISM_PROOF v02\nbody two\n"
    )
    assert count_atom_variants(path) == 2


def test_count_atom_variants_handles_mixed_formats(tmp_path: Path) -> None:
    """A single CANONICAL.txt with both header conventions should sum cleanly."""
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "## HOOK v01\nbody one\n\n"
        "--- variant: v02\nbody two\n\n"
        "## HOOK v03\nbody three\n"
    )
    assert count_atom_variants(path) == 3


def test_count_atom_variants_ignores_non_variant_dash_lines(tmp_path: Path) -> None:
    """Loose `---` separators inside `## TYPE vNN` blocks must not be counted
    as variants. They are a separator convention, not a header."""
    path = tmp_path / "CANONICAL.txt"
    path.write_text(
        "## HOOK v01\n---\nbody\n---\n## HOOK v02\n---\nbody\n---\n"
    )
    assert count_atom_variants(path) == 2


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
    passed, gaps, alt = check_atoms(
        atoms,
        ["p1"],
        ["anxiety"],
        ("HOOK", "STORY", "REFLECTION"),
        min_variants=5,
        teacher_banks_dir=tmp_path / "no_teacher_banks",
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    assert passed == 3
    assert gaps == []
    assert alt == {}


def test_check_atoms_flags_below_threshold_and_missing(tmp_path: Path) -> None:
    atoms = tmp_path / "atoms"
    _write_atom_canonical(atoms, "p1", "anxiety", "HOOK", 5)
    _write_atom_canonical(atoms, "p1", "anxiety", "STORY", 2)
    # REFLECTION intentionally absent.
    passed, gaps, alt = check_atoms(
        atoms,
        ["p1"],
        ["anxiety"],
        ("HOOK", "STORY", "REFLECTION"),
        min_variants=5,
        teacher_banks_dir=tmp_path / "no_teacher_banks",
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    assert passed == 1
    by_type = {g.section_type: g for g in gaps}
    assert by_type["STORY"].reason == "below_threshold"
    assert by_type["STORY"].have == 2
    assert by_type["REFLECTION"].reason == "missing_file"
    assert by_type["REFLECTION"].have == 0
    # No alt sources configured; no alt-source coverage expected
    assert alt == {}


# --- ws_spec_739_validator_teacher_banks_awareness_20260428 ---


def _seed_teacher_doctrine(teacher_banks_dir: Path, teacher_id: str = "maat") -> Path:
    """Create a minimal teacher_banks/<teacher>/doctrine/<teacher>.yaml fixture."""
    doctrine_dir = teacher_banks_dir / teacher_id / "doctrine"
    doctrine_dir.mkdir(parents=True, exist_ok=True)
    path = doctrine_dir / f"{teacher_id}.yaml"
    path.write_text(yaml.safe_dump({"teacher_id": teacher_id, "tradition": "test"}))
    return path


def _seed_teacher_approved_atoms(
    teacher_banks_dir: Path,
    section_type: str,
    teacher_id: str = "maat",
    count: int = 3,
) -> None:
    approved_dir = teacher_banks_dir / teacher_id / "approved_atoms" / section_type
    approved_dir.mkdir(parents=True, exist_ok=True)
    for n in range(count):
        (approved_dir / f"{teacher_id}_{section_type}_{n:03d}.yaml").write_text(
            yaml.safe_dump({"id": f"{teacher_id}_{section_type}_{n:03d}", "body": f"body {n}"})
        )


def _seed_practice_library(practice_path: Path, count: int = 3) -> None:
    practice_path.parent.mkdir(parents=True, exist_ok=True)
    practice_path.write_text(
        "\n".join(f'{{"practice_id": "p_{n}", "text": "body {n}"}}' for n in range(count))
        + "\n"
    )


def test_teacher_doctrine_resolves_from_teacher_banks_doctrine(tmp_path: Path) -> None:
    """TEACHER_DOCTRINE has no atoms/<persona>/<topic>/TEACHER_DOCTRINE/CANONICAL.txt
    by design — the pipeline pulls from teacher_banks/<teacher>/doctrine/. Validator
    must NOT flag missing_file for any persona×topic when at least one teacher has
    doctrine, since the pipeline can route any persona×topic to that teacher.
    """
    teacher_banks = tmp_path / "teacher_banks"
    _seed_teacher_doctrine(teacher_banks, teacher_id="maat")
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",
        personas=["mwp", "gen_z"],
        topics=["anxiety", "burnout"],
        section_types=("TEACHER_DOCTRINE",),
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    # 2 personas × 2 topics × 1 section_type = 4 tuples, all pass via teacher_banks/doctrine
    assert passed == 4
    assert gaps == []
    assert alt == {"teacher_banks/doctrine": 4}


def test_teacher_doctrine_still_flags_when_no_teachers_have_doctrine(tmp_path: Path) -> None:
    """Regression guard: an empty teacher_banks dir must NOT silently mask phantom
    gaps. If no teacher has doctrine, every TEACHER_DOCTRINE tuple is genuinely
    missing and the validator must flag it.
    """
    teacher_banks = tmp_path / "teacher_banks"
    teacher_banks.mkdir()
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",
        personas=["mwp"],
        topics=["anxiety"],
        section_types=("TEACHER_DOCTRINE",),
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    assert passed == 0
    assert len(gaps) == 1
    assert gaps[0].reason == "missing_file"
    assert gaps[0].section_type == "TEACHER_DOCTRINE"
    assert alt == {}


def test_exercise_resolves_from_teacher_approved_atoms(tmp_path: Path) -> None:
    """Per spec §4.5 EXERCISE three-source rule: a missing
    atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt is covered by
    teacher_banks/<teacher>/approved_atoms/EXERCISE/*.yaml.
    """
    teacher_banks = tmp_path / "teacher_banks"
    _seed_teacher_approved_atoms(teacher_banks, "EXERCISE", count=3)
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",
        personas=["mwp"],
        topics=["anxiety"],
        section_types=("EXERCISE",),
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    assert passed == 1
    assert gaps == []
    assert alt == {"teacher_banks/approved_atoms/EXERCISE": 1}


def test_exercise_resolves_from_practice_library(tmp_path: Path) -> None:
    """Per spec §4.5: when canonical AND approved_atoms are both empty, the
    practice_library backstop covers EXERCISE.
    """
    practice_path = tmp_path / "practice_items.jsonl"
    _seed_practice_library(practice_path, count=3)
    teacher_banks = tmp_path / "teacher_banks"
    teacher_banks.mkdir()  # empty — no approved_atoms
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",
        personas=["mwp"],
        topics=["anxiety"],
        section_types=("EXERCISE",),
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=practice_path,
    )
    assert passed == 1
    assert gaps == []
    assert alt == {"practice_library": 1}


def test_exercise_flags_when_all_three_sources_empty(tmp_path: Path) -> None:
    """Regression guard: spec §4.5 three-source rule must still surface gaps when
    ALL three sources are empty.
    """
    teacher_banks = tmp_path / "teacher_banks"
    teacher_banks.mkdir()
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",
        personas=["mwp"],
        topics=["anxiety"],
        section_types=("EXERCISE",),
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=tmp_path / "no_practice.jsonl",
    )
    assert passed == 0
    assert len(gaps) == 1
    assert gaps[0].reason == "missing_file"
    assert gaps[0].section_type == "EXERCISE"
    assert alt == {}


def test_other_section_types_remain_persona_atom_only_per_scope(tmp_path: Path) -> None:
    """Scope-discipline anchor for ws_spec_739_validator_teacher_banks_awareness_20260428.

    Even with teacher_banks/approved_atoms populated for HOOK / STORY / REFLECTION /
    INTEGRATION / COMPRESSION / PIVOT / PERMISSION / TAKEAWAY / THREAD, the validator
    must NOT silently broaden multi-source awareness to those types in this PR. They
    remain persona-atom-only until a separate Pearl_Architect routing decision lands.
    """
    teacher_banks = tmp_path / "teacher_banks"
    # Populate approved_atoms for every section type EXCEPT EXERCISE
    for st in ("HOOK", "STORY", "REFLECTION", "INTEGRATION", "COMPRESSION",
               "PIVOT", "PERMISSION", "TAKEAWAY", "THREAD"):
        _seed_teacher_approved_atoms(teacher_banks, st, count=5)
    # Also seed doctrine + practice library for completeness
    _seed_teacher_doctrine(teacher_banks)
    practice_path = tmp_path / "practice_items.jsonl"
    _seed_practice_library(practice_path)

    out_of_scope_types = (
        "HOOK", "STORY", "REFLECTION", "INTEGRATION", "COMPRESSION",
        "PIVOT", "PERMISSION", "TAKEAWAY", "THREAD",
    )
    passed, gaps, alt = check_atoms(
        atoms_dir=tmp_path / "atoms",  # no canonical files
        personas=["mwp"],
        topics=["anxiety"],
        section_types=out_of_scope_types,
        min_variants=3,
        teacher_banks_dir=teacher_banks,
        practice_library_path=practice_path,
    )
    # All 9 should be flagged missing_file — alt-source resolution is deliberately
    # NOT extended to these types in this PR.
    assert passed == 0
    assert len(gaps) == len(out_of_scope_types)
    for g in gaps:
        assert g.reason == "missing_file"
        assert g.section_type in out_of_scope_types
    assert alt == {}


def test_required_section_types_cover_grid_and_beats() -> None:
    grid = {"HOOK", "STORY", "REFLECTION", "EXERCISE", "TEACHER_DOCTRINE", "INTEGRATION"}
    beats = {"PIVOT", "PERMISSION", "TAKEAWAY", "THREAD", "COMPRESSION"}
    assert grid <= set(REQUIRED_SECTION_TYPES)
    assert beats <= set(REQUIRED_SECTION_TYPES)
    assert len(REQUIRED_SECTION_TYPES) == 11


def test_default_min_variants_is_three_per_spec_739_threshold_01() -> None:
    """Production floor = 3 per SPEC-739-THRESHOLD-01 cap entry (2026-04-28).

    Reconciled from ≥5 to ≥3 to match the curated authoring tradition
    established by PR #178 (commit 4725390b29) and sibling PRs #174/#176/#177
    which replaced auto-generated 20-variant template content with 3
    high-quality persona-voiced variants per slot. 5 remains an optional
    ceiling: registry sections may declare ``min_variants_required: 5`` to
    enforce the higher target, and the validator's per-section override path
    at ``check_registry`` line 153 honors that without lowering it to 3.
    """
    assert DEFAULT_MIN_VARIANTS == 3


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
            "atom_passed_via_alt_source": {},
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


def test_render_report_surfaces_alt_source_breakdown_when_present() -> None:
    """When alt-source coverage exists (TEACHER_DOCTRINE / EXERCISE per
    ws_spec_739_validator_teacher_banks_awareness_20260428), the report's summary
    must show the breakdown so future readers see the difference between
    persona-atom passing and alt-source coverage.
    """
    result_with_alt = type(
        "R",
        (),
        {
            "registry_passed": 0,
            "registry_gaps": [],
            "atom_passed": 5,  # 2 canonical + 3 alt-source
            "atom_gaps": [],
            "atom_passed_via_alt_source": {
                "teacher_banks/doctrine": 2,
                "teacher_banks/approved_atoms/EXERCISE": 1,
            },
            "total_gaps": 0,
        },
    )()
    report = render_report(result_with_alt, min_variants=3, today="2026-04-28")
    assert "via persona-atom canonical: **2**" in report
    assert "via alternative source: **3**" in report
    assert "`teacher_banks/doctrine`: 2" in report
    assert "`teacher_banks/approved_atoms/EXERCISE`: 1" in report
    assert "spec §4.5 three-source rule" in report.lower() or "§4.5" in report


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

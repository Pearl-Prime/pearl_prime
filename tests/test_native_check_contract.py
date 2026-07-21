"""Tests for translation native_check contract gate.

Run:
    PYTHONPATH=. python3 -m pytest tests/test_native_check_contract.py -v
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
import yaml

import scripts.ci.check_native_check as native_gate

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_contract(repo: Path) -> None:
    src = REPO_ROOT / "config" / "localization" / "native_check_contract.yaml"
    dest = repo / "config" / "localization" / "native_check_contract.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _teacher_yaml(path: Path, native_check: str | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "atom_id": "adi_da_PIVOT_001",
        "body": "localized body",
    }
    if native_check is not None:
        doc["native_check"] = native_check
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")


def _atom_locale_dir(
    repo: Path,
    locale: str,
    variants: dict[str, str] | None,
    *,
    header_style: str = "alt",
) -> Path:
    locale_dir = (
        repo
        / "atoms"
        / "educators"
        / "anxiety"
        / "PIVOT"
        / "locales"
        / locale
    )
    locale_dir.mkdir(parents=True, exist_ok=True)
    canonical = locale_dir / "CANONICAL.txt"
    keys = sorted(variants or {"v01": "y"})
    blocks = []
    for key in keys:
        if header_style == "header":
            blocks.append(f"## PIVOT {key}\n---\n\n---\nTranslated text for {key}.")
        else:
            blocks.append(f"--- variant: {key}\nTranslated text for {key}.")
    canonical.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    if variants is not None:
        sidecar = {"schema_version": 1, "variants": variants}
        (locale_dir / "native_check.yaml").write_text(
            yaml.safe_dump(sidecar, allow_unicode=True),
            encoding="utf-8",
        )
    return locale_dir


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    _write_contract(tmp_path)
    return tmp_path


def test_teacher_bank_y_passes(fixture_repo: Path) -> None:
    ypath = (
        fixture_repo
        / "SOURCE_OF_TRUTH"
        / "teacher_banks"
        / "adi_da"
        / "approved_atoms_localized"
        / "ja-JP"
        / "PIVOT"
        / "adi_da_PIVOT_001_ja-JP.yaml"
    )
    _teacher_yaml(ypath, "y")
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 0


def test_teacher_bank_missing_fails_production(fixture_repo: Path) -> None:
    ypath = (
        fixture_repo
        / "SOURCE_OF_TRUTH"
        / "teacher_banks"
        / "adi_da"
        / "approved_atoms_localized"
        / "ja-JP"
        / "PIVOT"
        / "adi_da_PIVOT_001_ja-JP.yaml"
    )
    _teacher_yaml(ypath, None)
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1


def test_teacher_bank_missing_warns_bootstrap(fixture_repo: Path) -> None:
    ypath = (
        fixture_repo
        / "SOURCE_OF_TRUTH"
        / "teacher_banks"
        / "adi_da"
        / "approved_atoms_localized"
        / "ja-JP"
        / "PIVOT"
        / "adi_da_PIVOT_001_ja-JP.yaml"
    )
    _teacher_yaml(ypath, None)
    assert native_gate.main(["--repo-root", str(fixture_repo), "--bootstrap-mode"]) == 0


def test_teacher_bank_n_fails_production(fixture_repo: Path) -> None:
    ypath = (
        fixture_repo
        / "SOURCE_OF_TRUTH"
        / "teacher_banks"
        / "adi_da"
        / "approved_atoms_localized"
        / "zh-CN"
        / "PIVOT"
        / "adi_da_PIVOT_001_zh-CN.yaml"
    )
    _teacher_yaml(ypath, "n")
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1


def test_atoms_sidecar_y_passes(fixture_repo: Path) -> None:
    _atom_locale_dir(fixture_repo, "ja-JP", {"v01": "y", "v02": "y"})
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 0


def test_atoms_header_style_y_passes(fixture_repo: Path) -> None:
    """Production CANONICAL.txt uses ## SLOT vNN headers."""
    _atom_locale_dir(
        fixture_repo, "ja-JP", {"v01": "y", "v02": "y"}, header_style="header"
    )
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 0


def test_atoms_sidecar_missing_fails_production(fixture_repo: Path) -> None:
    _atom_locale_dir(fixture_repo, "ja-JP", None)
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1


def test_atoms_sidecar_n_fails_production(fixture_repo: Path) -> None:
    _atom_locale_dir(fixture_repo, "ko-KR", {"v01": "y", "v02": "n"})
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1


def test_atoms_sidecar_missing_variant_fails(fixture_repo: Path) -> None:
    locale_dir = _atom_locale_dir(fixture_repo, "zh-TW", {"v01": "y"})
    canonical = locale_dir / "CANONICAL.txt"
    canonical.write_text(
        textwrap.dedent(
            """\
            --- variant: v01
            First variant.

            --- variant: v02
            Second variant.
            """
        ),
        encoding="utf-8",
    )
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1


def test_en_us_locale_skipped(fixture_repo: Path) -> None:
    _atom_locale_dir(fixture_repo, "en-US", None)
    ypath = (
        fixture_repo
        / "SOURCE_OF_TRUTH"
        / "teacher_banks"
        / "adi_da"
        / "approved_atoms_localized"
        / "en-US"
        / "PIVOT"
        / "adi_da_PIVOT_001_en-US.yaml"
    )
    _teacher_yaml(ypath, None)
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 0


def test_scan_stats_counts(fixture_repo: Path) -> None:
    _teacher_yaml(
        fixture_repo
        / "SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms_localized/ja-JP/PIVOT/a.yaml",
        "y",
    )
    _atom_locale_dir(fixture_repo, "ja-JP", {"v01": "y", "v02": "n"})
    result = native_gate.scan_native_check(
        fixture_repo, bootstrap_mode=False, production_only=False
    )
    assert result.stats.teacher_atoms == 1
    assert result.stats.atom_locale_dirs == 1
    assert result.stats.atom_variants == 2
    assert result.stats.native_y == 2
    assert result.stats.native_n == 1
    assert "ja-JP" in result.by_locale_class
    assert result.by_locale_class["ja-JP"]["PIVOT"]["y"] >= 1


def test_json_out_coverage_by_locale(fixture_repo: Path, tmp_path: Path) -> None:
    _teacher_yaml(
        fixture_repo
        / "SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms_localized/ja-JP/PIVOT/a.yaml",
        "y",
    )
    out = tmp_path / "coverage.json"
    rc = native_gate.main(
        [
            "--repo-root",
            str(fixture_repo),
            "--bootstrap-mode",
            "--json-out",
            str(out),
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "by_locale" in payload
    assert "ja-JP" in payload["by_locale"]
    assert payload["native_y"] >= 1


def test_mutation_missing_fails_loud(fixture_repo: Path) -> None:
    """Mutation: deliberately omit native_check → production gate RED."""
    _atom_locale_dir(fixture_repo, "pt-BR", None)
    assert native_gate.main(["--repo-root", str(fixture_repo), "--production-only"]) == 1

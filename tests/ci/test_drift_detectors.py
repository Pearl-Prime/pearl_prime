"""Tests for drift-detector CI scripts (Wave 2)."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_DIR = REPO_ROOT / "scripts" / "ci"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "drift_detectors"


def _run(script: str, repo: Path, *extra: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    run_env["PYTHONPATH"] = f"{repo / 'scripts' / 'ci'}:{repo}"
    if env:
        run_env.update(env)
    cmd = [sys.executable, str(CI_DIR / script), "--repo-root", str(repo), *extra]
    return subprocess.run(cmd, capture_output=True, text=True, env=run_env, check=False)


def _write_map(repo: Path) -> None:
    coord = repo / "artifacts" / "coordination"
    coord.mkdir(parents=True)
    (coord / "SUBSYSTEM_AUTHORITY_MAP.tsv").write_text(
        "subsystem_id\tauthority_doc\tconfig_path\towner_agent\tstatus\n"
        "pearl_devops\tdocs/GITHUB_GOVERNANCE.md\t.github/workflows/;scripts/ci/\tPearl_DevOps\tactive\n"
        "core_pipeline\tspecs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md\tconfig/governance/\tPearl_Prime\tactive\n",
        encoding="utf-8",
    )


# --- check_canonical_pipeline_path ---


def test_canonical_pipeline_pass_with_full_chord(tmp_path: Path) -> None:
    """G3: a production invocation carrying the full four-piece chord PASSES."""
    scripts = tmp_path / "scripts" / "prod"
    scripts.mkdir(parents=True)
    (scripts / "assemble.py").write_text(
        textwrap.dedent(
            """
            cmd = [
                sys.executable, "scripts/run_pipeline.py",
                "--pipeline-mode", "spine",
                "--quality-profile", "production",
                "--exercise-journeys",
                "--render-book",
                "--arc", "arc.yaml",
            ]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        "scripts/prod/assemble.py",
        "--gate-mode",
        "fail",
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "PASS" in r.stderr


def test_canonical_pipeline_fail_spine_only_missing_chord(tmp_path: Path) -> None:
    """G3: spine alone is no longer enough — missing quality-profile/exercise-journeys FAILS."""
    scripts = tmp_path / "scripts" / "prod"
    scripts.mkdir(parents=True)
    (scripts / "assemble.py").write_text(
        textwrap.dedent(
            """
            cmd = [
                sys.executable, "scripts/run_pipeline.py",
                "--pipeline-mode", "spine",
                "--render-book",
                "--arc", "arc.yaml",
            ]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        "scripts/prod/assemble.py",
        "--gate-mode",
        "fail",
    )
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert "incomplete bestseller chord" in r.stderr
    assert "--quality-profile production" in r.stderr
    assert "--exercise-journeys" in r.stderr


def test_drift_detectors_workflow_uses_chord_fail_mode() -> None:
    """G3 enforcement: drift-detectors CI must BLOCK incomplete chords (not warn)."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "drift-detectors.yml").read_text(
        encoding="utf-8"
    )
    assert "CANONICAL_PIPELINE_GATE_MODE: fail" in workflow
    assert "--gate-mode fail" in workflow
    assert "--gate-mode warn" not in workflow


def test_canonical_pipeline_chord_kill_switch_reverts_to_spine_only(tmp_path: Path) -> None:
    """G3 kill-switch: CANONICAL_PIPELINE_CHORD_FULL=0 → spine-only PASSES (pre-G3 behavior)."""
    scripts = tmp_path / "scripts" / "prod"
    scripts.mkdir(parents=True)
    (scripts / "assemble.py").write_text(
        textwrap.dedent(
            """
            cmd = [
                sys.executable, "scripts/run_pipeline.py",
                "--pipeline-mode", "spine",
                "--render-book",
                "--arc", "arc.yaml",
            ]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        "scripts/prod/assemble.py",
        "--gate-mode",
        "fail",
        env={"CANONICAL_PIPELINE_CHORD_FULL": "0"},
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "PASS" in r.stderr


def test_canonical_pipeline_fail_without_spine(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "catalog.yml").write_text(
        "run: python scripts/run_pipeline.py --render-book --arc arc.yaml\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        ".github/workflows/catalog.yml",
        "--gate-mode",
        "fail",
    )
    assert r.returncode == 1
    assert "missing --pipeline-mode spine" in r.stderr


def test_canonical_pipeline_warn_mode_exits_zero(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "catalog.yml").write_text(
        "run: python scripts/run_pipeline.py --render-book --arc arc.yaml\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        ".github/workflows/catalog.yml",
        "--gate-mode",
        "warn",
    )
    assert r.returncode == 0
    assert "::warning::" in r.stderr


def test_canonical_pipeline_allowlisted_legacy(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts" / "ci"
    scripts.mkdir(parents=True)
    (scripts / "legacy_sim.py").write_text(
        textwrap.dedent(
            """
            # CI-ALLOWLIST: legacy-registry-ok — systems test harness
            subprocess.run(["python", "scripts/run_pipeline.py", "--render-book", "--arc", "a.yaml"])
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        "scripts/ci/legacy_sim.py",
        "--gate-mode",
        "fail",
    )
    assert r.returncode == 0


def test_canonical_pipeline_skips_video_run_pipeline(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts" / "video"
    scripts.mkdir(parents=True)
    (scripts / "invoke.py").write_text(
        'subprocess.run(["python", "scripts/video/run_pipeline.py", "--plan-id", "x"])\n',
        encoding="utf-8",
    )
    r = _run(
        "check_canonical_pipeline_path.py",
        tmp_path,
        "--paths",
        "scripts/video/invoke.py",
        "--gate-mode",
        "fail",
    )
    assert r.returncode == 0


# --- check_duplicate_modules ---


def test_duplicate_modules_warns_on_matching_function(tmp_path: Path) -> None:
    lib = tmp_path / "phoenix_v4" / "utils"
    lib.mkdir(parents=True)
    (lib / "helpers.py").write_text(
        "def normalize_topic_slug(value, locale):\n    return value\n",
        encoding="utf-8",
    )
    new = tmp_path / "scripts" / "new_helper.py"
    new.parent.mkdir(parents=True)
    new.write_text(
        "def normalize_topic_slug(value, locale):\n    return value.upper()\n",
        encoding="utf-8",
    )
    r = _run(
        "check_duplicate_modules.py",
        tmp_path,
        "--new-files",
        "scripts/new_helper.py",
    )
    assert r.returncode == 0
    assert "::warning::" in r.stderr
    assert "phoenix_v4/utils/helpers.py" in r.stderr


def test_duplicate_modules_pass_legitimate_new_api(tmp_path: Path) -> None:
    lib = tmp_path / "phoenix_v4" / "utils"
    lib.mkdir(parents=True)
    (lib / "helpers.py").write_text(
        "def normalize_topic_slug(value, locale):\n    return value\n",
        encoding="utf-8",
    )
    new = tmp_path / "scripts" / "new_helper.py"
    new.parent.mkdir(parents=True)
    new.write_text(
        "def build_spine_manifest(book_id, chapter_count, locale):\n    return {}\n",
        encoding="utf-8",
    )
    r = _run(
        "check_duplicate_modules.py",
        tmp_path,
        "--new-files",
        "scripts/new_helper.py",
    )
    assert r.returncode == 0
    assert "PASS" in r.stderr
    assert "::warning::" not in r.stderr


def test_duplicate_modules_similar_name_different_arity(tmp_path: Path) -> None:
    lib = tmp_path / "phoenix_v4" / "utils"
    lib.mkdir(parents=True)
    (lib / "helpers.py").write_text(
        "def normalize_topic_slug(value, locale):\n    return value\n",
        encoding="utf-8",
    )
    new = tmp_path / "scripts" / "new_helper.py"
    new.parent.mkdir(parents=True)
    new.write_text(
        "def normalize_topic_slug(value):\n    return value\n",
        encoding="utf-8",
    )
    r = _run(
        "check_duplicate_modules.py",
        tmp_path,
        "--new-files",
        "scripts/new_helper.py",
    )
    assert r.returncode == 0
    assert "::warning::" not in r.stderr


# --- check_authority_doc_read ---


def test_authority_doc_read_warns_without_citation(tmp_path: Path) -> None:
    _write_map(tmp_path)
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "new.yml").write_text("name: test\n", encoding="utf-8")
    r = _run(
        "check_authority_doc_read.py",
        tmp_path,
        "--paths",
        ".github/workflows/new.yml",
        "--reference-text",
        "unrelated change only",
    )
    assert r.returncode == 0
    assert "::warning::" in r.stderr
    assert "pearl_devops" in r.stderr


def test_authority_doc_read_pass_with_citation(tmp_path: Path) -> None:
    _write_map(tmp_path)
    ci = tmp_path / "scripts" / "ci"
    ci.mkdir(parents=True)
    (ci / "new_check.py").write_text("# gate\n", encoding="utf-8")
    r = _run(
        "check_authority_doc_read.py",
        tmp_path,
        "--paths",
        "scripts/ci/new_check.py",
        "--reference-text",
        "Read docs/GITHUB_GOVERNANCE.md before editing workflows.",
    )
    assert r.returncode == 0
    assert "PASS" in r.stderr


def test_authority_doc_read_pass_unmapped_path(tmp_path: Path) -> None:
    _write_map(tmp_path)
    misc = tmp_path / "misc"
    misc.mkdir()
    (misc / "notes.txt").write_text("hello\n", encoding="utf-8")
    r = _run(
        "check_authority_doc_read.py",
        tmp_path,
        "--paths",
        "misc/notes.txt",
        "--reference-text",
        "",
    )
    assert r.returncode == 0
    assert "PASS" in r.stderr

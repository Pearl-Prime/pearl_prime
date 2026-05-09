"""Phase 2 cover art gate: warn vs fail for missing cover_art_base files (CI_BASELINE_RECOVERY Q2)."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = REPO_ROOT / "scripts" / "ci" / "check_author_cover_art.py"


def _write_fixture_tree(root: Path, *, create_png: bool, style_ok: bool = True) -> None:
    (root / "config" / "catalog_planning").mkdir(parents=True)
    (root / "config" / "authoring").mkdir(parents=True)
    (root / "assets" / "authors" / "cover_art").mkdir(parents=True)

    (root / "config" / "catalog_planning" / "brand_teacher_matrix.yaml").write_text(
        textwrap.dedent(
            """
            brands:
              test_brand:
                teachers:
                  - fixture_author
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (root / "config" / "author_registry.yaml").write_text("authors: {}\n", encoding="utf-8")

    style = "minimal" if style_ok else ""
    (root / "config" / "authoring" / "author_cover_art_registry.yaml").write_text(
        textwrap.dedent(
            f"""
            authors:
              fixture_author:
                cover_art_base: assets/authors/cover_art/fixture_author_base.png
                style_hint: {style!r}
                palette_tokens: ["a", "b"]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    png = root / "assets" / "authors" / "cover_art" / "fixture_author_base.png"
    if create_png:
        png.write_bytes(b"\x89PNG\r\n\x1a\n")


def _run(repo: Path, *, gate_mode: str | None, cli_flag: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if gate_mode is None:
        env.pop("COVER_ART_GATE_MODE", None)
    else:
        env["COVER_ART_GATE_MODE"] = gate_mode
    cmd = [sys.executable, str(_SCRIPT), "--repo-root", str(repo)]
    if cli_flag is not None:
        cmd.extend(["--gate-mode", cli_flag])
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def test_warn_mode_missing_png_exits_zero_with_github_warning_prefix(tmp_path: Path) -> None:
    _write_fixture_tree(tmp_path, create_png=False)
    r = _run(tmp_path, gate_mode="warn")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "::warning::" in (r.stderr or "")
    assert "missing asset" in (r.stderr or "").lower() or "missing cover_art_base" in (r.stderr or "")


def test_fail_mode_missing_png_exits_one(tmp_path: Path) -> None:
    _write_fixture_tree(tmp_path, create_png=False)
    r = _run(tmp_path, gate_mode="fail")
    assert r.returncode == 1
    assert "FAIL:" in (r.stderr or "")


def test_present_png_ok_warn_and_fail_mode(tmp_path: Path) -> None:
    _write_fixture_tree(tmp_path, create_png=True)
    assert _run(tmp_path, gate_mode="warn").returncode == 0
    assert _run(tmp_path, gate_mode="fail").returncode == 0


def test_cli_gate_mode_overrides_env(tmp_path: Path) -> None:
    _write_fixture_tree(tmp_path, create_png=False)
    # env says warn but CLI fail => strict
    r = _run(tmp_path, gate_mode="warn", cli_flag="fail")
    assert r.returncode == 1


def test_default_is_warn_when_env_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_fixture_tree(tmp_path, create_png=False)
    monkeypatch.delenv("COVER_ART_GATE_MODE", raising=False)
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "COVER_ART_GATE_MODE"},
        check=False,
    )
    assert r.returncode == 0
    assert "::warning::" in (r.stderr or "")


def test_hard_error_still_fails_in_warn_mode(tmp_path: Path) -> None:
    _write_fixture_tree(tmp_path, create_png=True, style_ok=False)
    r = _run(tmp_path, gate_mode="warn")
    assert r.returncode == 1
    assert "style_hint" in (r.stderr or "")

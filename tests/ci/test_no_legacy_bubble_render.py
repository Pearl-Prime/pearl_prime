"""Legacy bubble_render fence (scripts/ci/check_no_legacy_bubble_render.py).

The v2 lettering path (bubble_render_v2 + genre_bubble_styles) is the
production path; this ratchet blocks NEW production imports of legacy
bubble_render while grandfathering the six pre-v2 callers as WARN.

Run:
    PYTHONPATH=. python3 -m pytest tests/ci/test_no_legacy_bubble_render.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))

import check_no_legacy_bubble_render as fence  # noqa: E402


def test_repo_has_no_new_legacy_bubble_render_imports() -> None:
    violations = fence.scan()
    new = [rel for rel, _hits in violations if rel not in fence.KNOWN_LEGACY_CALLERS]
    assert new == [], (
        "new production imports of legacy bubble_render — use bubble_render_v2: "
        f"{new}"
    )


def test_grandfathered_set_only_shrinks() -> None:
    # Ratchet: entries may be removed as callers migrate to v2, never added.
    baseline = {
        "phoenix_v4/manga/chapter/chapter_production.py",
        "scripts/manga/compose_episode_from_renders.py",
        "scripts/manga/ja_jp_phase1_smoke.py",
        "scripts/manga/ja_jp_phase2_bulk.py",
        "scripts/manga/render_episode_strip.py",
        "scripts/manga/run_bubble_compose_v31.py",
    }
    assert fence.KNOWN_LEGACY_CALLERS <= baseline


def test_detector_catches_legacy_import(tmp_path: Path) -> None:
    sample = tmp_path / "offender.py"
    sample.write_text(
        "from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels\n"
    )
    hits = fence._ast_imports_legacy(sample)
    assert hits and "bubble_render" in hits[0]


def test_detector_catches_module_form(tmp_path: Path) -> None:
    sample = tmp_path / "offender2.py"
    sample.write_text("from phoenix_v4.manga.chapter import bubble_render\n")
    hits = fence._ast_imports_legacy(sample)
    assert hits


def test_main_exits_zero_on_current_tree(capsys) -> None:
    assert fence.main() == 0
    out = capsys.readouterr().out
    assert "PASS: no new production imports" in out

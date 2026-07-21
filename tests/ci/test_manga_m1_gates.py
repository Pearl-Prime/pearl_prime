"""Tests for the M1 manga enforcement rails (three drift-class kills).

Covers:
  - check_render_progress_bytes: passes real byte rows, fails bytes<50KB
    stub-as-done rows, fails non-integer bytes, --require-images path check,
    LFS-pointer-aware sizing.
  - check_manga_story_authored: passes the real authored ep_001, blocks a
    plan-only (missing) series, blocks a thin/stub script, blocks a
    series_plan (wrong artifact_type).
  - check_manga_wiring: passes the current tree (declared allowlist), fails an
    undeclared orphan config, passes with a status:unwired marker.

Run:
    PYTHONPATH=. python3 -m pytest tests/ci/test_manga_m1_gates.py -v
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.ci.check_render_progress_bytes as bytes_gate
import scripts.ci.check_manga_story_authored as story_gate
import scripts.ci.check_manga_wiring as wiring_gate

REPO_ROOT = Path(__file__).resolve().parents[2]


# ── render-bytes gate ────────────────────────────────────────────────────────


def _tsv(tmp: Path, rows: str) -> Path:
    d = tmp / "ep_001"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "RENDER_PROGRESS.tsv"
    p.write_text("panel_id\tstatus\tbytes\tseconds\n" + rows)
    return p


def test_bytes_gate_passes_real_rows(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\t2596354\t23.1\nep001_002\tok\t2156201\t20.7\n")
    assert bytes_gate.main(["--paths", str(p)]) == 0


def test_bytes_gate_fails_stub_row(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\t1\t0.0\n")
    assert bytes_gate.main(["--paths", str(p)]) == 1


def test_bytes_gate_ignores_pending_rows(tmp_path):
    # a small byte count is fine if the row is not claimed done
    p = _tsv(tmp_path, "ep001_001\tpending\t0\t0.0\n")
    assert bytes_gate.main(["--paths", str(p)]) == 0


def test_bytes_gate_fails_noninteger_bytes(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\tN/A\t0.0\n")
    assert bytes_gate.main(["--paths", str(p)]) == 1


def test_bytes_gate_require_images_missing(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\t2596354\t23.1\n")  # no png beside it
    assert bytes_gate.main(["--paths", str(p), "--require-images"]) == 1


def test_bytes_gate_require_images_present(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\t60000\t23.1\n")
    (p.parent / "ep001_001.png").write_bytes(b"x" * 60000)
    assert bytes_gate.main(["--paths", str(p), "--require-images"]) == 0


def test_bytes_gate_lfs_pointer_counts_real_size(tmp_path):
    p = _tsv(tmp_path, "ep001_001\tok\t2000000\t23.1\n")
    pointer = ("version https://git-lfs.github.com/spec/v1\n"
               "oid sha256:" + "0" * 64 + "\nsize 2000000\n")
    (p.parent / "ep001_001.png").write_text(pointer)
    assert bytes_gate.main(["--paths", str(p), "--require-images"]) == 0


def test_bytes_gate_offload_manifest_passes_without_image(tmp_path):
    """Offloaded panels pass --require-images via manifest-verify (Q-LFS-03)."""
    from scripts.artifacts.lfs_offload_manifest import OffloadEntry, write_manifest_tsv

    d = tmp_path / "artifacts/manifests/lfs_offload"
    d.mkdir(parents=True)
    tsv_dir = tmp_path / "ep_001"
    tsv_dir.mkdir()
    p = tsv_dir / "RENDER_PROGRESS.tsv"
    p.write_text("panel_id\tstatus\tbytes\tseconds\nep001_001\tok\t1882246\t0.0\n")
    repo_path = "ep_001/ep001_001.png"
    write_manifest_tsv(
        d / "pilot.tsv",
        slug="pilot",
        namespace="manga_rendered_books",
        bucket="phoenix-omega-artifacts",
        entries=[OffloadEntry(repo_path, "manga/rendered_books/x/ep001_001.png", 1882246, "a" * 64)],
    )
    rel = str(p.relative_to(tmp_path))
    # Rewrite manifest with full repo_path matching gate lookup
    write_manifest_tsv(
        d / "pilot.tsv",
        slug="pilot",
        namespace="manga_rendered_books",
        bucket="phoenix-omega-artifacts",
        entries=[OffloadEntry(rel.replace("RENDER_PROGRESS.tsv", "ep001_001.png").replace("\\", "/"),
                           "manga/x.png", 1882246, "a" * 64)],
    )
    assert bytes_gate.main([
        "--repo-root", str(tmp_path),
        "--paths", rel,
        "--require-images",
        "--offload-manifest-dir", "artifacts/manifests/lfs_offload",
    ]) == 0


def test_bytes_gate_real_tree_passes():
    # the two committed TSVs on main are all >= 50KB; the gate must land green
    assert bytes_gate.main([]) == 0


# ── story-authored gate ──────────────────────────────────────────────────────

REAL_SERIES = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"


def test_story_gate_passes_real_authored_episode():
    rc = story_gate.main(["--series", REAL_SERIES, "--episode", "ep_001"])
    assert rc == 0


def test_story_gate_blocks_missing_series():
    rc = story_gate.main(["--series", "no_such_plan_only_series", "--episode", "ep_001"])
    assert rc == 1


def test_story_gate_blocks_plan_not_script(tmp_path):
    plan = tmp_path / "series_plan.yaml"
    plan.write_text(yaml.safe_dump({
        "artifact_type": "series_plan", "series_id": "x", "pages": [],
    }))
    with pytest.raises(story_gate.StoryNotAuthoredError, match="not an authored script|not.*chapter_script|listing"):
        story_gate.assert_story_authored(plan)


def test_story_gate_blocks_thin_script(tmp_path):
    thin = tmp_path / "ep_001.yaml"
    thin.write_text(yaml.safe_dump({
        "artifact_type": "chapter_script_writer_handoff",
        "pages": [{"panels": [{"panel_id": "p1", "scene": "a lone panel"}]}],
    }))
    with pytest.raises(story_gate.StoryNotAuthoredError, match="authored panel"):
        story_gate.assert_story_authored(thin)


def test_story_gate_blocks_stub_marker(tmp_path):
    stub = tmp_path / "ep_001.yaml"
    panels = [{"panel_id": f"p{i}", "scene": f"scene {i}"} for i in range(6)]
    panels[3]["scene"] = "the protagonist is TODO here"
    stub.write_text(yaml.safe_dump({
        "artifact_type": "chapter_script_writer_handoff", "pages": [{"panels": panels}],
    }))
    with pytest.raises(story_gate.StoryNotAuthoredError, match="stub marker"):
        story_gate.assert_story_authored(stub)


def test_story_gate_inline_mirrors_match_bestseller_gate():
    # the gate falls back to inline copies of _MIN_PANELS/_STUB_RE in the
    # dependency-light CI env; they must stay identical to the real primitives.
    from phoenix_v4.manga.qc.bestseller_gate import _MIN_PANELS as real_min
    from phoenix_v4.manga.qc.bestseller_gate import _STUB_RE as real_re
    assert story_gate._MIN_PANELS == real_min
    assert story_gate._STUB_RE.pattern == real_re.pattern


def test_story_gate_accepts_locale_caption_schema(tmp_path):
    ok = tmp_path / "ep_001.yaml"
    panels = [{"panel_id": f"p{i}",
               "narrator_caption_by_locale": {"en_US": f"beat {i}"}} for i in range(6)]
    ok.write_text(yaml.safe_dump({
        "artifact_type": "chapter_script_writer_handoff", "pages": [{"panels": panels}],
    }))
    story_gate.assert_story_authored(ok)  # must not raise


# ── wiring gate ──────────────────────────────────────────────────────────────


def test_wiring_gate_passes_current_tree():
    assert wiring_gate.main(["--repo-root", str(REPO_ROOT)]) == 0


def test_wiring_gate_fails_orphan(tmp_path):
    (tmp_path / "config/manga").mkdir(parents=True)
    (tmp_path / "config/manga/zzz_orphan.yaml").write_text("schema_version: '1.0.0'\n")
    (tmp_path / "scripts").mkdir()
    assert wiring_gate.main(["--repo-root", str(tmp_path)]) == 1


def test_wiring_gate_passes_status_unwired(tmp_path):
    (tmp_path / "config/manga").mkdir(parents=True)
    (tmp_path / "config/manga/zzz_orphan.yaml").write_text(
        "schema_version: '1.0.0'\nstatus: unwired\n")
    (tmp_path / "scripts").mkdir()
    assert wiring_gate.main(["--repo-root", str(tmp_path)]) == 0


def test_wiring_gate_passes_with_consumer(tmp_path):
    (tmp_path / "config/manga").mkdir(parents=True)
    (tmp_path / "config/manga/zzz_used.yaml").write_text("schema_version: '1.0.0'\n")
    (tmp_path / "scripts/manga").mkdir(parents=True)
    (tmp_path / "scripts/manga/loader.py").write_text(
        "import yaml\nyaml.safe_load(open('config/manga/zzz_used.yaml'))\n")
    assert wiring_gate.main(["--repo-root", str(tmp_path)]) == 0


def test_wiring_gate_ignores_ci_self_reference(tmp_path):
    # a scripts/ci/ file naming the config must NOT count as a consumer
    (tmp_path / "config/manga").mkdir(parents=True)
    (tmp_path / "config/manga/zzz_named_in_ci.yaml").write_text("schema_version: '1.0.0'\n")
    (tmp_path / "scripts/ci").mkdir(parents=True)
    (tmp_path / "scripts/ci/some_gate.py").write_text("CFG = 'zzz_named_in_ci.yaml'\n")
    assert wiring_gate.main(["--repo-root", str(tmp_path)]) == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

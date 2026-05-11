"""Tests for ``scripts/catalog/v1_1_allocation_to_batch_plan.py``.

Covers:
- expected batch counts from real 296-row TSV (4 locales)
- structural fields per batch
- text-free cover validation (no literal V1.1 series titles in cover prompts)
- markdown round-trip through ``batch_runner.load_plan``
- dispatch_path routing per AMENDMENT-2026-05-10-PATH-BY-WORKFLOW
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.catalog import v1_1_allocation_to_batch_plan as gen  # noqa: E402
from scripts.image_generation.batch_runner import load_plan  # noqa: E402


@pytest.fixture(scope="module")
def real_run_summary(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("v1_1_full")
    summary = gen.generate_plans(
        run_id="test_run_001",
        output_dir=out_dir,
        dry_run=True,
    )
    return summary, out_dir


def test_full_run_emits_4_locale_plans(real_run_summary):
    summary, _ = real_run_summary
    assert set(summary["locales"].keys()) == {"en_US", "ja_JP", "zh_TW", "zh_CN"}
    for loc, info in summary["locales"].items():
        assert info["batch_count"] > 0
        assert info["cover_count"] > 0
        assert info["panel_count"] > 0
    assert summary["total_cells"] == 296


def test_per_locale_batch_count_balanced(real_run_summary):
    """All 4 locales receive identical batch counts (allocation TSV is
    locale-balanced 74 cells each)."""
    summary, _ = real_run_summary
    counts = {loc: info["batch_count"] for loc, info in summary["locales"].items()}
    assert len(set(counts.values())) == 1, f"locales not balanced: {counts}"


def test_load_plan_roundtrip(real_run_summary):
    _, out_dir = real_run_summary
    p = out_dir / "plan_en_US.md"
    batches = load_plan(p)
    assert len(batches) > 0
    required = {
        "batch_id", "brand_id", "locale", "surface", "dispatch_path",
        "workflow_template", "asset_type", "positive_prompt",
        "negative_prompt", "output_path",
    }
    for b in batches[:50]:
        missing = required - set(b.keys())
        assert not missing, f"missing fields in batch: {missing}"


def test_text_free_cover_prompts(real_run_summary):
    """No literal V1.1 series_title may appear in any cover positive_prompt.

    Enforces ``feedback_cover_text_overlay_two_stage``: FLUX renders imagery
    only; titles come from PIL overlay downstream.
    """
    _, out_dir = real_run_summary
    themes = yaml.safe_load(
        (REPO_ROOT / "artifacts" / "marketing"
         / "v1_1_25_brand_series_themes_2026-05-11.yaml").read_text(encoding="utf-8")
    )
    titles: set[str] = set()
    for _bn, bb in (themes.get("brands") or {}).items():
        for _loc, items in (bb.get("series") or {}).items():
            for it in items or []:
                t = (it.get("series_title") or "").strip()
                if t:
                    titles.add(t)
    assert titles, "no V1.1 series titles loaded — fixture broken"

    violations: list[str] = []
    for loc in ("en_US", "ja_JP", "zh_TW", "zh_CN"):
        for b in load_plan(out_dir / f"plan_{loc}.md"):
            if b.get("surface") != "cover":
                continue
            # load_plan splits comma values into lists; rejoin for the check
            pp = b.get("positive_prompt")
            if isinstance(pp, list):
                pp = " ".join(str(x) for x in pp)
            pp = str(pp)
            for t in titles:
                if t and t in pp:
                    violations.append(f"{b['batch_id']} contains {t!r}")
                    break
    assert not violations, f"cover text leak: {violations[:5]}"


def test_dispatch_routing_per_surface(real_run_summary):
    _, out_dir = real_run_summary
    batches = load_plan(out_dir / "plan_en_US.md")
    for b in batches:
        if b["surface"] == "cover":
            assert b["dispatch_path"] == "pearl_star", b
            assert str(b["workflow_template"]).startswith("flux_"), b
        elif b["surface"] == "panel":
            assert b["dispatch_path"] == "runcomfy", b
            assert str(b["workflow_template"]).startswith("qwen_"), b


def test_batch_id_deterministic(tmp_path):
    s1 = gen.generate_plans(
        run_id="det_run", output_dir=tmp_path / "a", dry_run=True,
    )
    s2 = gen.generate_plans(
        run_id="det_run", output_dir=tmp_path / "b", dry_run=True,
    )
    a = (tmp_path / "a" / "plan_en_US.md").read_text(encoding="utf-8")
    b = (tmp_path / "b" / "plan_en_US.md").read_text(encoding="utf-8")
    assert a == b
    assert s1["total_batches"] == s2["total_batches"]


def test_locale_filter(tmp_path):
    s = gen.generate_plans(
        run_id="filter_run",
        output_dir=tmp_path,
        locale_filter="en_US",
        dry_run=True,
    )
    assert set(s["locales"].keys()) == {"en_US"}
    assert (tmp_path / "plan_en_US.md").exists()
    assert not (tmp_path / "plan_ja_JP.md").exists()


def test_lora_resolution_uses_plans():
    """A known V1.0 brand (stillness_press) resolves to its style + character
    LoRA refs from the plans YAML."""
    style = gen._resolve_style_lora(
        "stillness_press",
        {"stillness_press": {"trigger_word": "style_sp"}},
        canon=gen._DEFAULT_STYLE_CANON,
    )
    assert "stillness_press" in style
    char = gen._resolve_character_lora(
        "stillness_press",
        cover_specs={"brands": {"stillness_press": {"character_lora": "ahjan_sp"}}},
        char_loras={"ahjan": {"trigger_word": "ahjan_sp"}},
    )
    assert "ahjan" in char


def test_negative_prompt_is_text_free(real_run_summary):
    _, out_dir = real_run_summary
    batches = load_plan(out_dir / "plan_en_US.md")
    for b in batches[:20]:
        np_ = b["negative_prompt"]
        if isinstance(np_, list):
            np_ = " ".join(str(x) for x in np_)
        # text_free_negative_prompt block contains "watermark" + "typography"
        assert "watermark" in str(np_)
        assert "typography" in str(np_)


def test_cli_dry_run_exits_zero(tmp_path, capsys):
    rc = gen._cli([
        "--run-id", "cli_test",
        "--output-dir", str(tmp_path),
        "--dry-run",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert "total_batches" in captured.out

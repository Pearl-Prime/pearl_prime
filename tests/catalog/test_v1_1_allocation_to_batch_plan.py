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


def test_batch_id_uniqueness_full_allocation(real_run_summary):
    """Every batch in the real 296-cell allocation expansion MUST have a
    unique ``batch_id`` AND a unique ``output_path``.

    Regression for the cover collision that blocked Pearl_Conductor v3
    run_id ``conductor_v3_2026_05_11_t0103`` at checkpoint init: 148
    brand+locale pairs in the allocation TSV carry both ``ebook`` and
    ``manga`` rows, and prior to AMENDMENT-2026-05-12-COVER-UNIQUENESS the
    cover batch_id was hashed only over ``(brand, locale, "cover", sidx,
    0)`` — yielding 724 duplicates per 13,540-batch full plan. The fix
    includes the allocation row's ``source_surface`` in both the hash and
    the output_path segment.
    """
    _, out_dir = real_run_summary
    all_ids: list[str] = []
    all_paths: list[str] = []
    per_locale: dict[str, dict[str, int]] = {}
    for loc in ("en_US", "ja_JP", "zh_TW", "zh_CN"):
        batches = load_plan(out_dir / f"plan_{loc}.md")
        ids = [b["batch_id"] for b in batches]
        paths = [b["output_path"] for b in batches]
        per_locale[loc] = {
            "batches": len(batches),
            "unique_ids": len(set(ids)),
            "dup_ids": len(ids) - len(set(ids)),
            "unique_paths": len(set(paths)),
            "dup_paths": len(paths) - len(set(paths)),
        }
        all_ids.extend(ids)
        all_paths.extend(paths)
    # Per-locale: zero dups, batch_ids and output_paths fully unique.
    for loc, stats in per_locale.items():
        assert stats["dup_ids"] == 0, (
            f"{loc}: {stats['dup_ids']} duplicate batch_ids (stats={stats})"
        )
        assert stats["dup_paths"] == 0, (
            f"{loc}: {stats['dup_paths']} duplicate output_paths (stats={stats})"
        )
    # Cross-locale: still unique. Total = 13,540 over the real TSV.
    assert len(set(all_ids)) == len(all_ids), (
        f"cross-locale: {len(all_ids) - len(set(all_ids))} duplicate batch_ids"
    )
    assert len(set(all_paths)) == len(all_paths), (
        f"cross-locale: {len(all_paths) - len(set(all_paths))} "
        "duplicate output_paths"
    )
    assert len(all_ids) == 13540, (
        f"expected 13540 total batches from 296-cell allocation, got {len(all_ids)}"
    )


def test_ebook_and_manga_covers_diverge():
    """For a synthetic brand+locale carrying both ``ebook`` and ``manga``
    allocation rows, the cover batches MUST have distinct ``batch_id`` AND
    distinct ``output_path``. The system MUST also expose ``source_surface``
    on the batch dict so downstream prompt authors can diverge per surface
    (e.g. KDP-cover-specific vs manga-cover-specific framing).
    """
    canon = gen._DEFAULT_STYLE_CANON
    series_themes = {
        "brands": {
            "stillness_press": {
                "series": {
                    "en_US": [
                        {
                            "series_title": "Synthetic Calm",
                            "arc_shape": "settle into stillness",
                            "emotional_throughline": "quiet returns",
                            "surface_priority": "balanced",
                        }
                    ]
                }
            }
        }
    }
    cover_specs = {
        "brands": {
            "stillness_press": {"prompt_template": "", "character_lora": ""}
        },
        "text_free_negative_prompt": "watermark, typography, text",
    }
    ebook_batches = gen.build_batches_for_cell(
        brand="stillness_press",
        locale="en_US",
        surface="ebook",
        series_count=3,
        episodes_per_series=5,
        priority_phase="V1.0_matrix_confirmed",
        series_themes=series_themes,
        cover_specs=cover_specs,
        style_loras={},
        char_loras={},
        canon=canon,
        run_id="synthetic",
    )
    manga_batches = gen.build_batches_for_cell(
        brand="stillness_press",
        locale="en_US",
        surface="manga",
        series_count=3,
        episodes_per_series=5,
        priority_phase="V1.0_matrix_confirmed",
        series_themes=series_themes,
        cover_specs=cover_specs,
        style_loras={},
        char_loras={},
        canon=canon,
        run_id="synthetic",
    )
    ebook_covers = [b for b in ebook_batches if b["surface"] == "cover"]
    manga_covers = [b for b in manga_batches if b["surface"] == "cover"]
    assert len(ebook_covers) == 3
    assert len(manga_covers) == 3
    ebook_ids = {b["batch_id"] for b in ebook_covers}
    manga_ids = {b["batch_id"] for b in manga_covers}
    assert not (ebook_ids & manga_ids), (
        f"ebook/manga cover batch_id collision: {ebook_ids & manga_ids}"
    )
    ebook_paths = {b["output_path"] for b in ebook_covers}
    manga_paths = {b["output_path"] for b in manga_covers}
    assert not (ebook_paths & manga_paths), (
        f"ebook/manga cover output_path collision: {ebook_paths & manga_paths}"
    )
    # System exposes source_surface so prompts CAN diverge per surface.
    for b in ebook_covers:
        assert b.get("source_surface") == "ebook"
    for b in manga_covers:
        assert b.get("source_surface") == "manga"
    # Output paths must include the source_surface segment so two cover
    # PNGs land in distinct directories — required for KDP vs manga asset
    # sorting downstream.
    for b in ebook_covers:
        assert "/ebook/" in b["output_path"], b["output_path"]
    for b in manga_covers:
        assert "/manga/" in b["output_path"], b["output_path"]


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

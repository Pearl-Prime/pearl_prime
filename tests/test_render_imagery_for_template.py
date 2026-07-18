"""Tests for scripts.publish.render_imagery_for_template (Stage 1 of the
template-based KDP cover pipeline).

These tests cover plan computation, dry-run output, the
``--i-have-confirmed-pearl-star`` safety gate, type-dominant skip
behavior, and v3 imagery output naming. They never call ComfyUI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.publish import render_imagery_for_template as rimg  # noqa: E402


# ─── ASPECT MATCHES TEMPLATE ──────────────────────────────────────────


@pytest.mark.parametrize("genre", [
    "anxiety", "sleep_anxiety", "grief", "overthinking", "burnout", "courage",
])
def test_aspect_matches_template(genre: str) -> None:
    """Per-genre planned width/height must match the template's
    imagery_zone aspect ratio (within multiple-of-64 rounding)."""
    templates = rimg.load_templates()["templates"]
    tpl = templates[genre]
    iz = tpl["imagery_zone"]
    expected_aspect = (
        (iz["x_pct"][1] - iz["x_pct"][0]) / 100.0 * rimg.CANVAS_W
        / ((iz["y_pct"][1] - iz["y_pct"][0]) / 100.0 * rimg.CANVAS_H)
    )
    w, h = rimg.flux_dimensions(expected_aspect, target_megapixels=1.0)
    # Both dims must be multiples of 64.
    assert w % 64 == 0
    assert h % 64 == 0
    # Aspect should match within 5% (rounding to multiples of 64 introduces
    # small drift).
    actual_aspect = w / h
    assert abs(actual_aspect - expected_aspect) / expected_aspect < 0.05, (
        f"{genre}: planned {w}x{h} aspect {actual_aspect:.3f} drifts "
        f">5% from template aspect {expected_aspect:.3f}"
    )


# ─── DRY-RUN BATCH ───────────────────────────────────────────────────


def test_dry_run_lists_planned_renders_without_calling_comfyui(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Dry-run prints one JSON line per book; no ComfyUI call."""
    rc = rimg.main(["--batch", "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) >= 13, f"Expected >=13 lines, got {len(out)}"
    parsed = [json.loads(line) for line in out]
    statuses = {p["status"] for p in parsed}
    assert "planned" in statuses
    assert "skipped_type_dominant" in statuses


# ─── SAFETY GATE ───────────────────────────────────────────────────────


def test_real_run_requires_pearl_star_flag(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --i-have-confirmed-pearl-star and without --dry-run, the
    CLI must refuse before opening any network call."""
    rc = rimg.main(["--book", "ahjan_anxiety"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "i-have-confirmed-pearl-star" in err


# ─── TYPE-DOMINANT SKIP ──────────────────────────────────────────────


@pytest.mark.parametrize("book_id,genre", [
    ("maat_boundaries", "boundaries"),
    ("adi_da_self_worth", "self_worth"),
    ("miki_imposter_syndrome", "imposter_syndrome"),
    ("ra_imposter_syndrome", "imposter_syndrome"),
])
def test_type_dominant_genres_are_skipped(book_id: str, genre: str) -> None:
    """Type-dominant genres must produce a skipped_type_dominant plan."""
    plan = rimg.plan_for_book(book_id)
    assert plan.type_dominant is True
    assert plan.genre == genre
    assert plan.width == 0
    assert plan.height == 0
    result = rimg.execute_plan(plan, dry_run=True)
    assert result["status"] == "skipped_type_dominant"


# ─── OUTPUT PATH NAMING ──────────────────────────────────────────────


def test_output_path_uses_v3_imagery_naming() -> None:
    """The v3 naming convention is reserved for template-aware FLUX
    renders (cover_<book_id>_v3_imagery.png)."""
    plan = rimg.plan_for_book("ahjan_anxiety")
    assert plan.output_path.name == "cover_ahjan_v3_imagery.png"
    assert plan.output_path.parent.name == "ahjan"
    plan = rimg.plan_for_book("master_sha_grief")
    assert plan.output_path.name == "cover_master_sha_v3_imagery.png"
    assert plan.output_path.parent.name == "master_sha"


# ─── PROMPT COMPOSITION ──────────────────────────────────────────────


def test_positive_prompt_contains_subject_register_and_lockin() -> None:
    """compose_positive_prompt must concat subject + universal_register +
    lock_in_tokens (per cookbook v2 contract)."""
    cookbook = rimg.load_cookbook()
    positive = rimg.compose_positive_prompt(cookbook, "anxiety")
    # Must contain key R4 §11 subject phrase
    assert "single open hand emerging from soft indigo shadow" in positive
    # Must include universal_register breadcrumbs
    assert "KDP portrait composition" in positive or \
           "trade paperback book cover" in positive
    # Must include at least one lock_in_tokens entry
    assert "cool blue and cream palette" in positive


def test_compose_refuses_type_dominant_genres() -> None:
    cookbook = rimg.load_cookbook()
    for genre in ("boundaries", "self_worth", "imposter_syndrome"):
        with pytest.raises(ValueError, match="FLUX-bypassed"):
            rimg.compose_positive_prompt(cookbook, genre)

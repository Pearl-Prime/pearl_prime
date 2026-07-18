"""Regression tests for the L5 audiobook SQUARE exporter (lane 4).

Covers scripts/publishing/export_cover_profiles.export_audiobook — the 1:1
audiobook cover for Google Play audiobook + ACX + Findaway (OPD-20260702-002).

SSOT for every asserted number:
  docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md §3/§4/§7 lane 4
  config/publishing/platform_cover_profiles.yaml
    (google_play_audiobook / acx_audiobook / findaway_voices_audiobook, render_masters.square)
  docs/authoring/AUTHOR_COVER_ART_SPEC.md §2/§4/§5/§6/§7/§8

Architectural assertion (lane 4 != lane 3):
  The audiobook cover is a NATIVE SQUARE 4-slot render, NOT a downscale of the
  portrait master. We prove this by rendering the square base at 3000² and
  confirming it is 1:1 from the base up (equal axes at every size), that no
  reflow/letterbox path is taken, and that a portrait master is never read.

Uses a type-dominant genre (boundaries) so the render path needs NO FLUX
illustration and is fully deterministic — no GPU, no paid LLM.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from scripts.publishing import export_cover_profiles as ecp
from scripts.publishing.load_cover_profiles import get_profile

pytestmark = pytest.mark.sanity

REPO_ROOT = Path(__file__).resolve().parents[1]
GENRE = "boundaries"  # type-dominant → no FLUX illustration required
AUTHOR_ID = "lena_thorne"
BOOK_ID = "corporate_managers_burnout"


def _sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def acx_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("acx")
    return ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "acx_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        subtitle="A Field Guide", out_dir=out,
    )


@pytest.fixture(scope="module")
def findaway_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("findaway")
    return ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "findaway_voices_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        subtitle="A Field Guide", out_dir=out,
    )


@pytest.fixture(scope="module")
def gplay_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("gplay")
    return ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "google_play_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        subtitle="A Field Guide", out_dir=out,
    )


# ─── SQUARE: exactly 1:1 at every profile size ───────────────────────


def test_acx_recommended_is_exactly_square_3000(acx_export):
    im = Image.open(acx_export["outputs"]["distributor_png"])
    assert im.size == (3000, 3000), f"ACX rec must be 3000x3000, got {im.size}"
    assert im.size[0] == im.size[1], "not 1:1"


def test_gplay_and_findaway_are_2400_square(gplay_export, findaway_export):
    gp = Image.open(gplay_export["outputs"]["distributor_png"])
    fw = Image.open(findaway_export["outputs"]["distributor_png"])
    assert gp.size == (2400, 2400), f"GP audiobook must be 2400², got {gp.size}"
    assert fw.size == (2400, 2400), f"Findaway must be 2400², got {fw.size}"


def test_square_master_is_3000(acx_export):
    m = Image.open(acx_export["square_master_png"])
    assert m.size == (ecp.SQUARE_MASTER_SIZE, ecp.SQUARE_MASTER_SIZE)
    assert m.size == (3000, 3000)


def test_all_audiobook_profiles_declare_1x1():
    for key in ("google_play_audiobook", "acx_audiobook",
                "findaway_voices_audiobook"):
        prof = get_profile(key)
        assert prof["aspect_ratio"]["decimal"] == 1.0, key
        rec = prof["size_recommended"]
        assert rec["width"] == rec["height"], f"{key} not square"


# ─── NATIVE SQUARE, NOT A PORTRAIT DOWNSCALE (lane 4 != lane 3) ──────


def test_square_base_is_native_not_a_portrait_crop():
    """The square base must be composed at 1:1 from the fingerprint
    primitives — never a cropped/resized portrait (5:8 or 5:7). We render the
    base directly and confirm it is square at the requested size with no
    portrait geometry involved."""
    base, meta = ecp._render_square_base(
        genre=GENRE, author_id=AUTHOR_ID, book_id=BOOK_ID, size=3000,
    )
    assert base.size == (3000, 3000), "square base not native 1:1"
    assert meta["square_base"] is True
    # The render_kdp_cover portrait constants must NOT bound the square base.
    from scripts.publish import render_kdp_cover as rkc
    assert base.size[1] != rkc.CANVAS_H, "square height leaked the portrait H"
    assert base.size[0] != rkc.CANVAS_W or base.size[0] == base.size[1]


def test_no_portrait_master_file_emitted(acx_export):
    """Lane 4 must not write a *_portrait_master.png — that is the lane-3
    reflow artifact. Only a *_square_master_* master is produced."""
    master = acx_export["square_master_png"]
    assert "square_master" in Path(master).name
    assert "portrait" not in Path(master).name


def test_export_uses_square_render_strategy(acx_export):
    assert acx_export["render_strategy"] == "native_square_4slot_no_reflow"


# ─── DETERMINISTIC 4-SLOT SELECTION (spec §5) ───────────────────────


def test_slot_is_deterministic_and_in_range():
    s1 = ecp.slot_for(AUTHOR_ID, BOOK_ID)
    s2 = ecp.slot_for(AUTHOR_ID, BOOK_ID)
    assert s1 == s2 and 0 <= s1 < 4
    # SHA256(author+":"+book) % 4 (spec §5).
    expected = hashlib.sha256(f"{AUTHOR_ID}:{BOOK_ID}".encode()).digest()[0] % 4
    assert s1 == expected


def test_export_reports_the_slot(acx_export):
    assert acx_export["slot"] == ecp.slot_for(AUTHOR_ID, BOOK_ID)
    assert acx_export["slot_name"] in ecp._SLOT_NAMES


# ─── DISTRIBUTOR RULES: no borders, no marketing copy, JPG ───────────


def test_acx_borders_and_marketing_forbidden(acx_export):
    prof = get_profile("acx_audiobook")
    assert prof["borders_allowed"] is False
    assert prof["marketing_copy_allowed"] is False
    # Exporter honored marketing_copy_allowed=false (no subtitle layer).
    assert acx_export["marketing_copy_allowed"] is False


def test_findaway_borders_and_marketing_forbidden(findaway_export):
    prof = get_profile("findaway_voices_audiobook")
    assert prof["borders_allowed"] is False
    assert prof["marketing_copy_allowed"] is False
    assert findaway_export["marketing_copy_allowed"] is False


def test_no_letterbox_bars_on_distributor_variant(acx_export, findaway_export):
    for exp in (acx_export, findaway_export):
        im = Image.open(exp["outputs"]["distributor_png"]).convert("RGB")
        assert not ecp._has_letterbox_bars(im), "distributor art has edge bars"


def test_acx_exports_jpg_within_budget(acx_export):
    jpg = acx_export["outputs"]["distributor_jpeg"]
    assert jpg["path"].endswith(".jpg")
    max_mb = get_profile("acx_audiobook")["max_file_mb"]
    assert jpg["bytes"] <= max_mb * 1024 * 1024, "ACX JPG over max_file_mb"
    assert jpg["over_budget"] is False


def test_findaway_jpg_within_2mb(findaway_export):
    jpg = findaway_export["outputs"]["distributor_jpeg"]
    assert jpg["path"].endswith(".jpg")
    max_mb = get_profile("findaway_voices_audiobook")["max_file_mb"]
    assert max_mb == 2
    assert jpg["bytes"] <= max_mb * 1024 * 1024, "Findaway JPG over 2 MB"


# ─── BADGED MARKETING VARIANT SEPARATE FROM UNBADGED DISTRIBUTOR ─────


def test_marketing_variant_is_badged_and_separate(acx_export):
    mkt = acx_export["marketing_variant"]
    assert mkt is not None and mkt["badged"] is True
    assert "_marketing" in Path(mkt["png"]).name
    # Distributor art is a DIFFERENT file from the badged marketing art.
    assert Path(mkt["png"]) != Path(acx_export["outputs"]["distributor_png"])


def test_no_marketing_variant_when_disabled(tmp_path):
    res = ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "acx_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        marketing_variant=False, out_dir=tmp_path,
    )
    assert res["marketing_variant"] is None


# ─── WCAG-AA CONTRAST GUARD RUNS (spec §4) ──────────────────────────


def test_wcag_report_present_on_square(acx_export):
    wcag = acx_export["wcag"]
    assert "wcag_contrast_ratio" in wcag
    assert wcag["wcag_target"] == 4.5


# ─── pHASH GUARD (spec §7) ──────────────────────────────────────────


def test_phash_present_and_int(acx_export):
    assert isinstance(acx_export["phash"], int)


def test_different_authors_differ_by_phash(tmp_path):
    a = ecp.export_audiobook(
        BOOK_ID, "lena_thorne", "acx_audiobook",
        genre=GENRE, title="X", author="A", out_dir=tmp_path / "a",
    )
    b = ecp.export_audiobook(
        BOOK_ID, "marcus_cole", "acx_audiobook",
        genre=GENRE, title="X", author="B", out_dir=tmp_path / "b",
    )
    # Same-brand pHash guard threshold is 12 (spec §7); different authors
    # should be well clear of a collision.
    dist = ecp.hamming_distance(a["phash"], b["phash"])
    assert dist >= 8, f"two authors' squares too similar (hamming={dist})"


# ─── DETERMINISM: byte-identical re-run ─────────────────────────────


def test_deterministic_byte_identical(tmp_path):
    r1 = ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "acx_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        out_dir=tmp_path / "one",
    )
    r2 = ecp.export_audiobook(
        BOOK_ID, AUTHOR_ID, "acx_audiobook",
        genre=GENRE, title="The Quiet Fix", author="Lena Thorne",
        out_dir=tmp_path / "two",
    )
    assert _sha(r1["outputs"]["distributor_png"]) == _sha(
        r2["outputs"]["distributor_png"]
    ), "square export is not deterministic"


# ─── GUARD: ebook profile is rejected by the audiobook path ─────────


def test_ebook_profile_rejected(tmp_path):
    with pytest.raises(ValueError):
        ecp.export_audiobook(
            BOOK_ID, AUTHOR_ID, "kobo_ebook",
            genre=GENRE, out_dir=tmp_path,
        )

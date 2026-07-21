"""Cover/social recipe registry + image-aware type placement.

Guards three things:
  1. the 12-topic recipe registry stays well-formed and NOT_PRODUCTION_APPROVED;
  2. placement is genuinely driven by the image (quiet band wins, busy band gets
     backing) and is deterministic;
  3. the fast downsampled busy verdict does not drift from the production
     `templates._is_busy` verdict it is derived from.
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest
import yaml
from PIL import Image, ImageDraw

from scripts.publish.waystream_covers import image_placement as IP
from scripts.publish.waystream_covers import symbols as S
from scripts.publish.waystream_covers import templates as T

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "config/publishing/waystream_cover_social_recipes.yaml"

CORE_TOPICS = {
    "anxiety", "depression", "grief", "overthinking", "burnout", "self_worth",
    "anger", "loneliness", "healing", "boundaries", "trauma", "hope",
}
CREAM = (246, 241, 226)


@pytest.fixture(scope="module")
def registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text())


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #
def test_registry_covers_the_twelve_core_topics(registry):
    assert set(registry["topics"]) == CORE_TOPICS


def test_registry_is_not_production_approved(registry):
    """The honesty bar: this registry must never assert production readiness."""
    assert registry["status"] == "NOT_PRODUCTION_APPROVED"
    assert registry["production_ready_count"] == 0


def test_every_topic_has_required_recipe_fields(registry):
    required = {
        "title", "subtitle", "persona_line", "social_hook", "social_body",
        "micro_steps", "pin_title", "linkedin_angle", "accent", "scrim",
        "symbol", "metaphors", "avoid", "plan_status",
    }
    for topic, rec in registry["topics"].items():
        missing = required - set(rec)
        assert not missing, f"{topic} missing {sorted(missing)}"


def test_symbols_exist_in_production_motif_vocabulary(registry):
    """Anti-reinvention: recipes must reuse symbols.py motifs, not invent new ones."""
    for topic, rec in registry["topics"].items():
        assert rec["symbol"] in S.MOTIF_FN, f"{topic}: unknown motif {rec['symbol']!r}"


def test_colors_are_rgb_triples(registry):
    for topic, rec in registry["topics"].items():
        for key in ("accent", "scrim"):
            v = rec[key]
            assert len(v) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in v), f"{topic}.{key}"


def test_every_topic_carries_safety_guardrails(registry):
    """`avoid` encodes the plan doc's face/logo/sensitive-topic gates. A topic
    with no guardrails would let curation drift straight past the legal review."""
    for topic, rec in registry["topics"].items():
        assert rec["avoid"], f"{topic} has no avoid guardrails"
        assert rec["metaphors"], f"{topic} has no metaphors"


def test_sensitive_topics_name_their_hard_exclusions(registry):
    """The plan doc calls trauma the riskiest lane; its exclusions must be explicit."""
    avoid = " ".join(registry["topics"]["trauma"]["avoid"]).lower()
    for term in ("accident", "blood", "abuse"):
        assert term in avoid, f"trauma.avoid does not exclude {term!r}"


# --------------------------------------------------------------------------- #
# synthetic fixtures
# --------------------------------------------------------------------------- #
def _fill_noise(img: Image.Image, y_from: int, y_to: int, seed: int = 7, block: int = 8) -> None:
    """Deterministic broadband noise.

    `block` must stay comfortably larger than the analysis downsample ratio, or
    the texture aliases away to a flat field and the fixture silently stops
    testing anything (this bit us once already).
    """
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for y in range(y_from, y_to, block):
        for x in range(0, img.width, block):
            v = rnd.randrange(0, 256)
            d.rectangle((x, y, x + block - 1, y + block - 1), fill=(v, v, v))


def _quiet_top_busy_bottom(w=400, h=800) -> Image.Image:
    """Flat sky on top, dense noise on the bottom."""
    img = Image.new("RGB", (w, h), (120, 140, 170))
    _fill_noise(img, h // 2, h)
    return img


def _busy_everywhere(w=400, h=800) -> Image.Image:
    img = Image.new("RGB", (w, h), (120, 140, 170))
    _fill_noise(img, 0, h)
    return img


def _flat() -> Image.Image:
    return Image.new("RGB", (400, 800), (128, 128, 128))


def test_fixture_actually_produces_a_busy_half():
    """Guard the guard: a fixture that aliases to flat would make the placement
    tests vacuously pass."""
    img = _quiet_top_busy_bottom()
    analysis = IP._analysis_copy(img)
    assert IP.band_stat(analysis, 0.55, 0.95).busy
    assert IP.band_stat(analysis, 0.05, 0.45).quiet


# --------------------------------------------------------------------------- #
# placement
# --------------------------------------------------------------------------- #
def test_title_moves_to_the_quiet_half():
    """The core promise: type goes where the image has room."""
    p = IP.choose_placement(_quiet_top_busy_bottom(), block_h=0.18, cream=CREAM)
    assert p.band.y1 <= 0.5, f"title landed on the busy half at y={p.band.y0}"


def test_quiet_band_gets_plain_type_no_backing():
    p = IP.choose_placement(_flat(), block_h=0.18, cream=CREAM)
    assert p.treatment == IP.TREATMENT_PLAIN


def test_busy_only_image_gets_a_backing_box():
    """When there is no negative space anywhere, protect the type."""
    p = IP.choose_placement(_busy_everywhere(), block_h=0.18, cream=CREAM)
    assert p.treatment == IP.TREATMENT_BOX
    assert p.ink == CREAM  # box imposes a dark ground


def test_placement_is_deterministic():
    img = _quiet_top_busy_bottom()
    a = IP.choose_placement(img, block_h=0.18, cream=CREAM)
    b = IP.choose_placement(img, block_h=0.18, cream=CREAM)
    assert a == b


def test_prefer_only_breaks_ties_never_overrides_the_image():
    """`prefer='bottom'` must not drag type onto a busy band."""
    img = _quiet_top_busy_bottom()
    p = IP.choose_placement(img, block_h=0.18, cream=CREAM, prefer="bottom")
    assert p.band.y1 <= 0.5, "prefer overrode the image's actual free space"


def test_dark_ink_chosen_on_a_bright_quiet_band():
    bright = Image.new("RGB", (400, 800), (240, 240, 238))
    p = IP.choose_placement(bright, block_h=0.18, cream=CREAM, dark=(24, 24, 26))
    assert p.treatment == IP.TREATMENT_PLAIN
    assert p.ink == (24, 24, 26)


def test_reason_is_populated_for_every_treatment():
    for img in (_flat(), _quiet_top_busy_bottom()):
        p = IP.choose_placement(img, block_h=0.18, cream=CREAM)
        assert p.reason and p.band is not None
        assert p.as_dict()["band"]["variance"] >= 0


def test_block_taller_than_canvas_is_rejected():
    with pytest.raises(ValueError):
        IP.choose_placement(_flat(), block_h=1.5, cream=CREAM)


# --------------------------------------------------------------------------- #
# thumbnail legibility (reuses the production rule)
# --------------------------------------------------------------------------- #
def test_thumbnail_rule_matches_production_constant():
    w = 1600
    min_px = IP.min_font_px_for_thumbnail(w)
    assert IP.thumbnail_ok(min_px, w)
    assert not IP.thumbnail_ok(min_px - 1, w)
    assert IP.thumb_cap_px(min_px, w) >= T.MIN_THUMB_CAP_PX


def test_tiny_subtitle_fails_the_thumbnail_rule():
    assert not IP.thumbnail_ok(20, 1600)


# --------------------------------------------------------------------------- #
# anti-drift: fast path vs production verdict
# --------------------------------------------------------------------------- #
def test_fast_busy_verdict_agrees_with_production_is_busy():
    """`image_placement` downsamples for speed; `templates._is_busy` walks every
    pixel. If these two ever disagree on a clear-cut image, the proof layer has
    drifted from the renderer it claims to mirror."""
    for img, expected in ((_flat(), False), (_quiet_top_busy_bottom(), True)):
        box = (0.0, 0.5, 1.0, 1.0)  # bottom half
        production = T._is_busy(img, box)
        analysis = IP._analysis_copy(img)
        fast = IP.band_stat(analysis, box[1], box[3]).busy
        assert production == expected, f"production verdict changed: {production}"
        assert fast == production, f"fast={fast} production={production}"


def test_thresholds_are_imported_not_restated():
    """Single source of truth for the busy verdict."""
    assert IP.BUSY_VARIANCE_THRESHOLD is T.BUSY_VARIANCE_THRESHOLD
    assert IP.BUSY_EDGE_THRESHOLD is T.BUSY_EDGE_THRESHOLD
    assert IP.QUIET_VARIANCE < IP.BUSY_VARIANCE_THRESHOLD
    assert IP.QUIET_EDGE < IP.BUSY_EDGE_THRESHOLD

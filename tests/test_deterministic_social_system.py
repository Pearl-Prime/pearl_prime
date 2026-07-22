import json
from pathlib import Path

from phoenix_v4.social.deterministic_social import (
    DEFAULT_BRAND_DISPLAY_NAME,
    build_metricool_payload,
    generate_copy_package,
    load_platform_specs,
    load_voice_profiles,
    render_static_asset,
    resolve_brand_display_name,
    resolve_voice_profile,
    select_visual,
    validate_asset,
    validate_copy_package,
)


def test_platform_contracts_cover_required_surfaces():
    surfaces = load_platform_specs()["surfaces"]
    required = {
        "instagram_feed_portrait",
        "instagram_carousel",
        "linkedin_document_slide",
        "pinterest_pin",
        "tiktok_reels_shorts_vertical",
        "youtube_shorts",
        "x_image",
        "threads_image",
        "bluesky_image",
        "google_business_square",
        "facebook_feed",
    }
    assert required.issubset(surfaces)
    assert all(not s.get("auto_publish_allowed", False) for s in surfaces.values())


def test_copy_packages_are_safe_and_platform_native():
    linkedin = generate_copy_package("corporate_managers", "burnout", "linkedin_document_slide")
    instagram = generate_copy_package("corporate_managers", "burnout", "instagram_carousel")
    x_post = generate_copy_package("corporate_managers", "burnout", "x_image")
    assert linkedin["caption"] != instagram["caption"]
    assert instagram["caption"] != x_post["caption"]
    assert len(x_post["caption"]) <= 280
    for copy in [linkedin, instagram, x_post]:
        ok, failures = validate_copy_package(copy)
        assert ok, failures


def test_visual_selector_never_marks_pending_license_as_production():
    visual = select_visual("overthinking", "gen_z_professionals", "instagram_carousel")
    assert visual["preview_allowed"] is True
    if visual["license_status"] != "verified":
        assert visual["production_allowed"] is False
        assert "pending" in visual["approval_state"] or visual["approval_state"].startswith("operator_preview")


def test_static_render_receipt_passes(tmp_path: Path):
    out = tmp_path / "linkedin_burnout.jpg"
    receipt = render_static_asset("corporate_managers", "burnout", "linkedin_feed_portrait", out)
    assert out.exists()
    assert receipt["validation"]["status"] == "pass"
    assert receipt["render"]["canvas"] == {"width": 1080, "height": 1350}


def test_metricool_payload_is_dry_run(tmp_path: Path):
    out = tmp_path / "linkedin_burnout.jpg"
    asset = render_static_asset("corporate_managers", "burnout", "linkedin_feed_portrait", out)
    payload = build_metricool_payload(asset)
    assert payload["autoPublish"] is False
    assert payload["draft"] is True
    assert payload["manualReviewRequired"] is True
    assert payload["dryRun"] is True


def test_validate_asset_blocks_unsafe_copy():
    copy = generate_copy_package("corporate_managers", "burnout", "linkedin_feed_portrait")
    asset = {
        "asset_id": "unsafe",
        "topic": "burnout",
        "persona": "corporate_managers",
        "platform": "linkedin",
        "surface": "linkedin_feed_portrait",
        "format_family": "static",
        "copy": {
            "hook_family": copy["hook_family"],
            "overlay_text": ["This cures anxiety"],
            "caption": "This cures anxiety.",
            "first_comment": None,
            "hashtags": ["burnout", "workplacewellbeing", "selfreflection"],
            "alt_text": "Unsafe test alt text.",
            "cta": copy["cta"],
        },
        "media_refs": [
            {
                "visual_source_ref": "test",
                "path": None,
                "usage_class": "generated_prompt_reference",
                "license_status": "not_applicable",
                "production_allowed": False,
                "preview_allowed": True,
            }
        ],
        "render": {"path": None},
    }
    validation = validate_asset(asset)
    assert validation["status"] == "blocked"
    assert validation["checks"]["claim_safety"] == "blocked"


def test_no_brand_args_copy_package_is_byte_identical_to_baseline():
    """Regression: default kwargs must match the pre-vibe package shape/bytes."""
    a = generate_copy_package("corporate_managers", "burnout", "linkedin_feed_portrait")
    b = generate_copy_package("corporate_managers", "burnout", "linkedin_feed_portrait")
    c = generate_copy_package(
        "corporate_managers",
        "burnout",
        "linkedin_feed_portrait",
        brand_id=None,
        author_id=None,
        post_index=0,
    )
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert json.dumps(a, sort_keys=True) == json.dumps(c, sort_keys=True)
    assert "brand_id" not in a
    assert "selected_atom_ids" not in a
    assert resolve_brand_display_name(None) == DEFAULT_BRAND_DISPLAY_NAME == "Waystream Sanctuary"


def test_brand_voice_changes_cta_and_sign_off():
    house = generate_copy_package("corporate_managers", "burnout", "linkedin_feed_portrait")
    stillness = generate_copy_package(
        "corporate_managers",
        "burnout",
        "linkedin_feed_portrait",
        brand_id="stillness_press",
    )
    clarity = generate_copy_package(
        "corporate_managers",
        "burnout",
        "linkedin_feed_portrait",
        brand_id="cognitive_clarity",
    )
    assert house["caption"] != stillness["caption"]
    assert stillness["caption"] != clarity["caption"]
    assert "Stillness Press" in stillness["caption"] or stillness["cta"]["text"] != house["cta"]["text"]
    assert "Clear Seeing" in clarity["caption"] or "Bookmark this framework" in clarity["caption"]
    voice = resolve_voice_profile(brand_id="stillness_press")
    assert voice["display_name"] == "Stillness Press"
    assert "universal" in load_voice_profiles()["profiles"]

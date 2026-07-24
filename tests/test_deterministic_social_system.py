import json
import subprocess
import sys
from pathlib import Path

from phoenix_v4.social.deterministic_social import (
    DEFAULT_BRAND_DISPLAY_NAME,
    VIDEO_BEAT_ROLE_ORDER,
    assemble_social_post,
    build_atom_carousel_package,
    build_atom_thread_package,
    build_atom_video_beat_script,
    build_metricool_payload,
    generate_copy_package,
    generate_story_led_copy_package,
    hashtags_for,
    load_platform_specs,
    load_social_atoms,
    load_voice_profiles,
    render_static_asset,
    resolve_brand_display_name,
    resolve_voice_profile,
    select_visual,
    validate_asset,
    validate_copy_package,
    _walk_self_chain,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VARIATION_GATE = REPO_ROOT / "scripts/ci/check_social_post_variation.py"


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


# --- Regressions: 2026-07-23 assembler bugfix + gate hardening lane ---------


def test_no_doubled_lead_in_label_when_atom_embeds_one():
    """Bug 1 (doubled label): SOURCE_OF_TRUTH/social_media_atoms TOOL_STEP rows
    embed their own colon-terminated lead-in ("Try this: ...", "Run the
    ninety-second reset: ..."). The professional-mode caption template also
    prepends its own "Try this:" label, so folding the atom text in verbatim
    used to double it — live pilot example: "Try this: The system keeps
    spending energy as if the old reserve is still there. Try this: close the
    loop, lower your jaw...". No caption in a full rotation cycle should stack
    two lead-in labels back to back.
    """
    # Known embedded lead-ins actually authored into TOOL_STEP atom copy
    # (SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl). A
    # generic "any colon-clause" regex over-fires on legitimate rotate_practice
    # phrasing like "Ask: what is the smallest honest yes..." — check for
    # these specific known lead-ins stacked directly after the template's own
    # "Try this:" instead.
    known_embedded_lead_ins = (
        "Try this:",
        "Run the ninety-second reset:",
        "Run a silent boundary tonight:",
        "Use this as a script",
    )
    for post_index in range(0, 9):
        pkg = generate_copy_package(
            "corporate_managers",
            "burnout",
            "linkedin_feed_portrait",
            brand_id="stillness_press",
            post_index=post_index,
        )
        caption = pkg["caption"]
        for lead_in in known_embedded_lead_ins:
            assert f"Try this: {lead_in}" not in caption, (lead_in, caption)


def test_rotation_arrays_never_collide_insight_and_practice():
    """Bug 1 (doubled label), second facet: rotate_practice[1] used to equal
    rotate_insights[1] (both topic_row['mechanism']), so at post_index%8==2 the
    caption body repeated the exact same sentence twice back to back. No
    caption paragraph in a full rotation cycle should repeat verbatim.
    """
    for post_index in range(1, 9):
        pkg = generate_copy_package(
            "corporate_managers", "burnout", "instagram_feed_portrait", post_index=post_index
        )
        paragraphs = [p.strip() for p in pkg["caption"].split("\n\n") if p.strip()]
        assert len(paragraphs) == len(set(paragraphs)), (post_index, pkg["caption"])


def test_no_third_person_persona_naming_leakage():
    """Bug 2: the professional and conversational/thoughtful caption templates
    used to open a clause with "For {persona_label}, ..." (e.g. "For corporate
    managers, the hidden cost often shows up as ..."), narrating about the
    reader in third person rather than addressing them. Confirmed
    assembler-injected (the literal template), not atom content — the phrase
    does not occur anywhere in SOURCE_OF_TRUTH/social_media_atoms/*.jsonl.
    """
    for post_index in range(0, 4):
        pkg = generate_copy_package(
            "corporate_managers", "burnout", "linkedin_feed_portrait", post_index=post_index
        )
        assert "For corporate managers," not in pkg["caption"]
    for surface_id in ("threads_image", "bluesky_image"):
        pkg = generate_copy_package("corporate_managers", "burnout", surface_id)
        assert "For corporate managers," not in pkg["caption"]


def test_hashtag_rotation_diverges_across_a_batch():
    """Gate-gap remediation: hashtags_for used to return the exact same
    hashtag SET for every post regardless of post_index (confirmed 2026-07-23:
    10/10 posts per brand/surface shared one verbatim hashtag set in the pilot
    batch). post_index=0 (baseline/no-vibe path) must stay byte-identical;
    post_index>0 must rotate the set, not just its order.
    """
    baseline_a = hashtags_for("burnout", "instagram", 15, 5)
    baseline_b = hashtags_for("burnout", "instagram", 15, 5, post_index=0)
    assert baseline_a == baseline_b

    sets_seen = {tuple(sorted(hashtags_for("burnout", "instagram", 15, 5, post_index=i))) for i in range(1, 6)}
    assert len(sets_seen) > 1, "hashtag sets did not diverge across post_index rotation"
    # The primary topic tag must always be present (discoverability anchor).
    for i in range(1, 6):
        assert "burnout" in hashtags_for("burnout", "instagram", 15, 5, post_index=i)


def test_cta_rotation_diverges_across_a_batch_with_brand_voice():
    """Gate-gap remediation: a brand voice's cta_phrase is one fixed string, so
    once applied every post from that brand repeated it verbatim (confirmed
    2026-07-23: only 2 distinct CTA strings across 20 pilot posts, one per
    brand, 10/10 each). post_index=0 must stay byte-identical to the existing
    brand-voice behavior; post_index>0 must vary the rendered CTA text while
    keeping the brand's own phrase recognizable inside it.
    """
    base = generate_copy_package(
        "corporate_managers", "burnout", "linkedin_feed_portrait", brand_id="stillness_press", post_index=0
    )
    ctas_seen = set()
    for i in range(1, 6):
        pkg = generate_copy_package(
            "corporate_managers", "burnout", "linkedin_feed_portrait", brand_id="stillness_press", post_index=i
        )
        assert "stillness practice" in pkg["cta"]["text"]
        ctas_seen.add(pkg["cta"]["text"])
    assert len(ctas_seen) > 1, "CTA text did not diverge across post_index rotation"
    assert base["cta"]["text"] not in ctas_seen or len(ctas_seen) > 1


def test_social_post_variation_gate_mutation_cta_and_hashtag_checks():
    """Mutation-test the gate 36 extension: baseline batch must PASS; forcing
    a CTA or hashtag set to repeat across a majority of one brand/platform/
    topic slice (while leaving captions distinct, isolating the new checks
    from the pre-existing near-duplicate-caption checks) must FAIL RED.
    """
    baseline = subprocess.run(
        [sys.executable, str(VARIATION_GATE)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert baseline.returncode == 0, baseline.stderr

    cta_mutation = subprocess.run(
        [sys.executable, str(VARIATION_GATE), "--inject-cta-repeat", "3"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert cta_mutation.returncode == 1
    assert "cta_repeat_over_threshold" in cta_mutation.stderr

    hashtag_mutation = subprocess.run(
        [sys.executable, str(VARIATION_GATE), "--inject-hashtag-repeat", "3"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert hashtag_mutation.returncode == 1
    assert "hashtag_set_repeat_over_threshold" in hashtag_mutation.stderr


# --- Lane E (2026-07-23): wiring the 5 new atom families ------------------------------
#
# MICRO_STORY, CASE_PROOF, CAROUSEL_SLIDE, THREAD_UNIT, VIDEO_BEAT were authored by Lane C
# (SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl) but confirmed
# unreachable from generate_copy_package by Lane D's inspection. These tests exercise the
# real promoted rows for the two fully-covered pilot cells (burnout x corporate_managers,
# anxiety x gen_z_professionals) plus one deliberately-uncovered cell (healthcare_rns x
# burnout) to prove both the happy path and the honest-gap fallback.

FULL_STORY_CELL = ("corporate_managers", "burnout")
FULL_THREAD_CELL = ("gen_z_professionals", "anxiety")
GAP_CELL = ("healthcare_rns", "burnout")


def _atom_ids_for(topic: str, persona: str, family: str) -> set[str]:
    return {
        a["atom_id"]
        for a in load_social_atoms()
        if a.get("atom_family") == family and a.get("topic") == topic and a.get("persona") == persona
    }


def test_walk_self_chain_orders_by_any_start_then_atom_id():
    """Unit test of the generic chain-walker in isolation, with synthetic atoms so the
    test does not depend on the live bank's current row count.
    """
    fabricated = [
        {"atom_id": "Z-03", "atom_family": "X", "compatible_previous": "X", "compatible_next": "CTA_ANCHOR"},
        {"atom_id": "Z-01", "atom_family": "X", "compatible_previous": "ANY_START", "compatible_next": "X"},
        {"atom_id": "Z-02", "atom_family": "X", "compatible_previous": "X", "compatible_next": "X"},
    ]
    ordered = _walk_self_chain(fabricated, "X")
    assert [a["atom_id"] for a in ordered] == ["Z-01", "Z-02", "Z-03"]


def test_walk_self_chain_returns_empty_when_no_any_start_row():
    fabricated = [{"atom_id": "Z-02", "atom_family": "X", "compatible_previous": "X", "compatible_next": "X"}]
    assert _walk_self_chain(fabricated, "X") == []


def test_story_led_chain_assembles_micro_story_case_proof_tool_step_cta():
    persona, topic = FULL_STORY_CELL
    pkg = generate_story_led_copy_package(persona, topic, "instagram_feed_portrait")
    assert pkg["story_led_chain_complete"] is True
    assert pkg["format_family"] == "story_led"
    assert pkg["chain_families"] == ["MICRO_STORY", "CASE_PROOF", "TOOL_STEP", "CTA_ANCHOR"]
    assert pkg["chain_compatibility_verified"] is True
    micro_story_ids = _atom_ids_for(topic, persona, "MICRO_STORY")
    case_proof_ids = _atom_ids_for(topic, persona, "CASE_PROOF")
    assert set(pkg["selected_atom_ids"][:1]).issubset(micro_story_ids)
    assert set(pkg["selected_atom_ids"][1:2]).issubset(case_proof_ids)
    ok, failures = validate_copy_package(pkg)
    assert ok, failures


def test_story_led_falls_back_honestly_when_chain_incomplete():
    """Bank-depth gap, not a wiring bug: healthcare_rns has no MICRO_STORY/CASE_PROOF rows
    for burnout yet. The wiring must not fabricate a chain — it must fall back to the
    standard static copy package and say so.
    """
    persona, topic = GAP_CELL
    assert not _atom_ids_for(topic, persona, "MICRO_STORY"), "test fixture assumption changed — pick a new gap cell"
    pkg = generate_story_led_copy_package(persona, topic, "instagram_feed_portrait")
    assert pkg["story_led_chain_complete"] is False
    assert pkg["story_led_gap_reason"] == "incomplete_chain_families_for_cell"
    assert pkg["format_family"] == "static"
    ok, failures = validate_copy_package(pkg)
    assert ok, failures


def test_story_led_rotation_diverges_across_post_index():
    persona, topic = FULL_STORY_CELL
    pairs = set()
    for idx in range(5):
        pkg = generate_story_led_copy_package(persona, topic, "instagram_feed_portrait", post_index=idx)
        paras = [p.strip() for p in pkg["caption"].split("\n\n") if p.strip()]
        pairs.add((paras[2], paras[3]))
    assert len(pairs) > 1, "TOOL_STEP/CTA_ANCHOR pick did not rotate across post_index"


def test_atom_carousel_package_assembles_ordered_slide_list():
    persona, topic = FULL_STORY_CELL
    pkg = build_atom_carousel_package(persona, topic, "instagram_carousel")
    assert pkg["chain_complete"] is True
    assert pkg["format_family"] == "carousel_atoms"
    assert pkg["slide_count"] == len(pkg["slides"]) >= 2
    assert pkg["slides"][0]["is_cover"] is True
    assert pkg["slides"][-1]["is_close"] is True
    # multi-slide structure, not a single caption
    assert isinstance(pkg["slides"], list)
    ids = [s["atom_id"] for s in pkg["slides"]]
    assert ids == sorted(ids), "slide order should match the authored CS-NN suffix order"
    assert len(ids) == len(set(ids))


def test_atom_carousel_package_gap_cell_reports_honestly():
    persona, topic = GAP_CELL
    pkg = build_atom_carousel_package(persona, topic, "instagram_carousel")
    assert pkg["chain_complete"] is False
    assert pkg["slides"] == []
    assert pkg["gap_reason"] == "no_carousel_slide_atoms_for_cell"


def test_atom_thread_package_assembles_ordered_post_list():
    persona, topic = FULL_THREAD_CELL
    pkg = build_atom_thread_package(persona, topic, "x_image")
    assert pkg["chain_complete"] is True
    assert pkg["format_family"] == "thread_atoms"
    assert pkg["post_count"] == len(pkg["posts"]) >= 2
    assert pkg["posts"][0]["is_hook"] is True
    assert pkg["posts"][-1]["is_invitation"] is True
    assert isinstance(pkg["posts"], list)
    for post in pkg["posts"]:
        assert post["char_count"] <= 280, "thread posts must fit an X/Threads single-post limit"


def test_atom_video_beat_script_covers_five_canonical_roles_in_order():
    persona, topic = FULL_STORY_CELL
    pkg = build_atom_video_beat_script(persona, topic, "tiktok_reels_shorts_vertical")
    assert pkg["chain_complete"] is True
    assert pkg["format_family"] == "video_beat_atoms"
    assert [b["beat_role"] for b in pkg["beats"]] == list(VIDEO_BEAT_ROLE_ORDER)
    # beat-timed script structure, not a caption
    assert pkg["beats"][0]["start_s"] == 0.0
    for i in range(len(pkg["beats"]) - 1):
        assert pkg["beats"][i]["end_s"] == pkg["beats"][i + 1]["start_s"]


def test_atom_video_beat_script_gap_cell_names_missing_roles():
    persona, topic = GAP_CELL
    pkg = build_atom_video_beat_script(persona, topic, "tiktok_reels_shorts_vertical")
    assert pkg["chain_complete"] is False
    assert pkg["beats"] == []
    assert "missing_beat_roles" in pkg["gap_reason"]


def test_new_format_brand_voice_overlay_appends_cta_without_mutating_other_slides():
    persona, topic = FULL_STORY_CELL
    house = build_atom_carousel_package(persona, topic, "instagram_carousel")
    branded = build_atom_carousel_package(persona, topic, "instagram_carousel", brand_id="stillness_press")
    assert branded["brand_id"] == "stillness_press"
    assert branded["brand_display_name"] == "Stillness Press"
    # every slide except the last is untouched by the brand overlay
    assert branded["slides"][:-1] == house["slides"][:-1]
    assert branded["slides"][-1]["text"] != house["slides"][-1]["text"]
    assert house["slides"][-1]["text"] in branded["slides"][-1]["text"]


def test_assemble_social_post_dispatches_all_new_format_families():
    persona, topic = FULL_STORY_CELL
    story = assemble_social_post(persona, topic, "instagram_feed_portrait", "story_led")
    carousel = assemble_social_post(persona, topic, "instagram_carousel", "carousel_atoms")
    video = assemble_social_post(persona, topic, "tiktok_reels_shorts_vertical", "video_beat_atoms")
    thread_persona, thread_topic = FULL_THREAD_CELL
    thread = assemble_social_post(thread_persona, thread_topic, "x_image", "thread_atoms")
    assert story["format_family"] == "story_led"
    assert carousel["format_family"] == "carousel_atoms"
    assert video["format_family"] == "video_beat_atoms"
    assert thread["format_family"] == "thread_atoms"


def test_assemble_social_post_passthrough_unaffected_for_existing_formats():
    """Existing format_family values ("static"/"carousel"/"video_storyboard") must dispatch
    to the unchanged generate_copy_package path byte-identically to calling it directly.
    """
    persona, topic = FULL_STORY_CELL
    direct = generate_copy_package(persona, topic, "linkedin_feed_portrait")
    via_dispatch = assemble_social_post(persona, topic, "linkedin_feed_portrait")
    assert json.dumps(direct, sort_keys=True) == json.dumps(via_dispatch, sort_keys=True)


def test_new_format_variation_gate_check_new_formats_flag_passes_and_catches_duplicates(monkeypatch):
    """Mutation-tests the additive --check-new-formats gate extension: the real bank must
    pass, and a forced duplicate-atom_id chain (simulating a broken chain-walk) must fail
    the check-6 detector, proving it is a real, wired check rather than decorative.
    """
    import scripts.ci.check_social_post_variation as gate

    baseline = subprocess.run(
        [sys.executable, str(VARIATION_GATE), "--check-new-formats"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert baseline.returncode == 0, baseline.stderr

    persona, topic = FULL_STORY_CELL
    real = gate.build_atom_carousel_package(persona, topic, "instagram_carousel")
    broken = dict(real)
    # Simulate a broken chain-walk: same slide duplicated (same atom_id and text twice).
    broken["slides"] = [real["slides"][0], real["slides"][0]]

    def fake_build_atom_carousel_package(*args, **kwargs):
        return broken

    monkeypatch.setattr(gate, "build_atom_carousel_package", fake_build_atom_carousel_package)
    failures = gate.evaluate_new_formats()
    assert any("carousel_atoms_duplicate_atom_id" in f for f in failures)
    assert any("carousel_atoms_duplicate_slide_text" in f for f in failures)

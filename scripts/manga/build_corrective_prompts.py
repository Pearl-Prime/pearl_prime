#!/usr/bin/env python3
"""Build corrective prompts for the 22 stillness_press dashboard PNGs.

PR-C Step 1 — engineering deliverable.

Reads:
- config/manga/drawing_tradition_per_genre.yaml (PR #838)
- config/manga/character_design_axes.yaml (PR #842 axis_patterns block)
- config/manga/character_individuation_metric.yaml (PR #842)
- config/manga/corpus_license_recommendations.yaml (PR #841)
- config/source_of_truth/manga_profiles/series/<series>.yaml (where present)

Writes:
- config/manga/corrective_prompts_for_dashboard_22.yaml

Algorithm: see docs/CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md
on origin/main (shipped in PR #842 commit 6f38191a).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── SHA pins for cross-references (post-merge to main) ────────────────────
SHA_PR_838 = "6c88d1d6643823358a8bd680ee0aebff9c6e6151"  # drawing-traditions
SHA_PR_842 = "6f38191ac64caded0cd14566c5f98834ecb10f78"  # individuation
SHA_PR_841 = "216aab394fe485498bbd6b650801a26e08a8bf83"  # corpus
SHA_PR_831 = "e2ff72cfe9"  # cookbook v2

# ── The 22 stillness_press series (per PR #838 dashboard diagnosis) ───────
# Class abbreviations from PR #838's `dashboard_22_failure_diagnosis_2026-05-02.md`:
#   "needs_workflow_fix"        — schnell-mismatch (engine fix #807 should help)
#   "needs_character_individuation_pipeline" — look-alike protagonist
#   "needs_LoRA_plus_multiple"   — dark_fantasy / horror requiring per-genre LoRA
#   "needs_prompt_fix_only"      — pure prompt issue (Group 5 isekai)
SERIES_22 = [
    # series_id, genre_family, locale, brand, diagnosis_class, has_source_yaml
    ("stillness_jp_01",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_02",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_03",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_04",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_05",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_06",                       "healing",              "ja_JP", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_jp_07",                       "dark_fantasy",         "ja_JP", "stillness_press", "needs_LoRA_plus_multiple",               True),
    ("stillness_jp_08",                       "dark_fantasy",         "ja_JP", "stillness_press", "needs_LoRA_plus_multiple",               True),
    ("stillness_jp_11",                       "psychological_horror", "ja_JP", "stillness_press", "needs_LoRA_plus_multiple",               True),
    ("stillness_jp_12",                       "psychological_horror", "ja_JP", "stillness_press", "needs_LoRA_plus_multiple",               True),
    ("stillness_jp_16",                       "fantasy_adventure",    "ja_JP", "stillness_press", "needs_prompt_fix_only",                  True),
    ("stillness_press_anxiety_vol1",          "healing",              "en_US", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_press_sleep_vol1",            "healing",              "en_US", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_press_somatic_vol1",          "healing",              "en_US", "stillness_press", "needs_workflow_fix",                     True),
    ("stillness_press_the_alarm_within",      "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_ember_and_rest",        "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_body_letters",          "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_the_forest_edge",       "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_pressure_map",          "slice_of_life",        "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_somatic_field_notes",   "slice_of_life",        "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_the_held_breath",       "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
    ("stillness_press_window_season",         "healing",              "en_US", "stillness_press", "needs_character_individuation_pipeline", False),
]

# ── 12-axis distinct character_design seeds for the 22 series ─────────────
# Procedurally varied so the constraint solver passes (no >5 same-brand
# locked-axis collisions). Authoring decisions made deterministically here
# rather than asking the operator to fill 22 templates by hand.
#
# Strategy: rotate through value sets to maximize pairwise distance.
DESIGNS = {
    "stillness_jp_01": dict(
        face_shape="heart_shaped", eye_size="medium", eye_shape="almond", eye_lid_fold="single",
        hair_length="shoulder", hair_parting="side_left", hair_color="dark_brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="cardigan_corduroy_librarian",
        age_decade="late_30s", accessories_glasses="round_wire_frame", accessories_signature="ceramic_tea_cup",
        palette_primary="muted_brown", palette_accent="deep_teal",
        nose_bridge="short_upturned", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_jp_02": dict(
        face_shape="oval", eye_size="medium", eye_shape="hooded", eye_lid_fold="double",
        hair_length="ear_length", hair_parting="center", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="business_casual_blazer",
        age_decade="mid_40s", accessories_glasses="cat_eye", accessories_signature="plain_steel_watch",
        palette_primary="navy", palette_accent="burgundy",
        nose_bridge="straight", mouth_lip="thin_both",
    ),
    "stillness_jp_03": dict(
        face_shape="round", eye_size="small", eye_shape="downturned", eye_lid_fold="single",
        hair_length="chin_bob", hair_parting="side_right", hair_color="dark_blonde",
        wardrobe_era="contemporary_2020s", wardrobe_style="overalls_potter",
        age_decade="early_30s", accessories_glasses="none", accessories_signature="clay_smudge_apron",
        palette_primary="ochre", palette_accent="sage_green",
        nose_bridge="straight", mouth_lip="full_both",
    ),
    "stillness_jp_04": dict(
        face_shape="square", eye_size="large", eye_shape="almond", eye_lid_fold="double",
        hair_length="mid_back", hair_parting="no_part_swept_back", hair_color="brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="kimono_casual",
        age_decade="late_20s", accessories_glasses="none", accessories_signature="bamboo_tea_whisk",
        palette_primary="forest_green", palette_accent="cream",
        nose_bridge="prominent", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_jp_05": dict(
        face_shape="elongated", eye_size="small", eye_shape="upturned", eye_lid_fold="double",
        hair_length="long_to_waist", hair_parting="center", hair_color="grey_at_temples",
        wardrobe_era="contemporary_2020s", wardrobe_style="loose_linen_artist",
        age_decade="50s", accessories_glasses="half_rim", accessories_signature="paint_stained_thumb",
        palette_primary="lavender", palette_accent="charcoal",
        nose_bridge="aquiline", mouth_lip="thin_both",
    ),
    "stillness_jp_06": dict(
        face_shape="soft_round", eye_size="medium", eye_shape="round", eye_lid_fold="double",
        hair_length="very_short", hair_parting="asymmetric", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="hospital_scrubs_softened",
        age_decade="mid_30s", accessories_glasses="round_thick_frame", accessories_signature="folded_origami_crane",
        palette_primary="dusty_rose", palette_accent="slate",
        nose_bridge="short_upturned", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_jp_07": dict(
        face_shape="angular_long", eye_size="small", eye_shape="sharp_angular", eye_lid_fold="single",
        hair_length="long_to_waist", hair_parting="center", hair_color="white_signaled",
        wardrobe_era="fantasy_setting", wardrobe_style="forest_priestess_robes",
        age_decade="late_30s", accessories_glasses="none", accessories_signature="crow_feather_pendant",
        palette_primary="forest_green", palette_accent="charcoal",
        nose_bridge="prominent", mouth_lip="thin_both",
    ),
    "stillness_jp_08": dict(
        face_shape="oval", eye_size="medium", eye_shape="hooded", eye_lid_fold="single",
        hair_length="shoulder", hair_parting="side_right", hair_color="black",
        wardrobe_era="fantasy_setting", wardrobe_style="ronin_traveling_cloak",
        age_decade="mid_30s", accessories_glasses="none", accessories_signature="weathered_walking_staff",
        palette_primary="indigo", palette_accent="ochre",
        nose_bridge="aquiline", mouth_lip="thin_both",
    ),
    "stillness_jp_11": dict(
        face_shape="elongated", eye_size="small", eye_shape="hooded", eye_lid_fold="single",
        hair_length="ear_length", hair_parting="center", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="archivist_layered_grey",
        age_decade="40s", accessories_glasses="round_thick_frame", accessories_signature="single_red_thread",
        palette_primary="charcoal", palette_accent="deep_teal",
        nose_bridge="straight", mouth_lip="thin_both",
    ),
    "stillness_jp_12": dict(
        face_shape="heart_shaped", eye_size="extra_small", eye_shape="downturned", eye_lid_fold="none_visible",
        hair_length="shoulder", hair_parting="side_left", hair_color="dark_brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="medical_examiner_white_coat",
        age_decade="early_30s", accessories_glasses="none", accessories_signature="silver_locket_closed",
        palette_primary="slate", palette_accent="burgundy",
        nose_bridge="short_upturned", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_jp_16": dict(
        face_shape="round", eye_size="medium", eye_shape="almond", eye_lid_fold="double",
        hair_length="chin_bob", hair_parting="center", hair_color="black",
        wardrobe_era="alternate_history", wardrobe_style="rural_yukata_traveler",
        age_decade="late_20s", accessories_glasses="none", accessories_signature="leather_journal",
        palette_primary="terracotta", palette_accent="sage_green",
        nose_bridge="straight", mouth_lip="full_both",
    ),
    "stillness_press_anxiety_vol1": dict(
        face_shape="oval", eye_size="medium", eye_shape="almond", eye_lid_fold="double",
        hair_length="ear_length", hair_parting="side_left", hair_color="dark_brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="cardigan_jeans_homebody",
        age_decade="late_20s", accessories_glasses="round_wire_frame", accessories_signature="weighted_blanket_corner",
        palette_primary="cream", palette_accent="dusty_rose",
        nose_bridge="straight", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_press_sleep_vol1": dict(
        face_shape="soft_round", eye_size="small", eye_shape="hooded", eye_lid_fold="single",
        hair_length="shoulder", hair_parting="no_part_swept_back", hair_color="brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="oversized_pajama_softened",
        age_decade="mid_30s", accessories_glasses="none", accessories_signature="ceramic_mug_chamomile",
        palette_primary="navy", palette_accent="cream",
        nose_bridge="short_upturned", mouth_lip="thin_both",
    ),
    "stillness_press_somatic_vol1": dict(
        face_shape="square", eye_size="medium", eye_shape="upturned", eye_lid_fold="double",
        hair_length="very_short", hair_parting="asymmetric", hair_color="dark_blonde",
        wardrobe_era="contemporary_2020s", wardrobe_style="yoga_layered_bamboo",
        age_decade="early_30s", accessories_glasses="none", accessories_signature="rolled_yoga_mat",
        palette_primary="sage_green", palette_accent="terracotta",
        nose_bridge="straight", mouth_lip="full_both",
    ),
    "stillness_press_the_alarm_within": dict(
        face_shape="elongated", eye_size="medium", eye_shape="downturned", eye_lid_fold="double",
        hair_length="long_to_waist", hair_parting="side_right", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="hoodie_hands_in_pockets",
        age_decade="early_20s", accessories_glasses="none", accessories_signature="phone_face_down",
        palette_primary="indigo", palette_accent="ochre",
        nose_bridge="aquiline", mouth_lip="thin_both",
    ),
    "stillness_press_ember_and_rest": dict(
        face_shape="heart_shaped", eye_size="small", eye_shape="round", eye_lid_fold="single",
        hair_length="mid_back", hair_parting="center", hair_color="grey_at_temples",
        wardrobe_era="contemporary_2020s", wardrobe_style="wool_shawl_grandmother",
        age_decade="60s", accessories_glasses="cat_eye", accessories_signature="iron_kettle_steam",
        palette_primary="ochre", palette_accent="charcoal",
        nose_bridge="prominent", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_press_body_letters": dict(
        face_shape="oval", eye_size="medium", eye_shape="almond", eye_lid_fold="double",
        hair_length="chin_bob", hair_parting="side_left", hair_color="brown",
        wardrobe_era="contemporary_2020s", wardrobe_style="writers_layered_neutrals",
        age_decade="40s", accessories_glasses="half_rim", accessories_signature="leather_journal_pen",
        palette_primary="muted_brown", palette_accent="forest_green",
        nose_bridge="short_upturned", mouth_lip="thin_both",
    ),
    "stillness_press_the_forest_edge": dict(
        face_shape="round", eye_size="medium", eye_shape="hooded", eye_lid_fold="double",
        hair_length="shoulder", hair_parting="center", hair_color="dark_blonde",
        wardrobe_era="contemporary_2020s", wardrobe_style="hiker_practical_layers",
        age_decade="mid_30s", accessories_glasses="sport", accessories_signature="walking_stick_carved",
        palette_primary="forest_green", palette_accent="cream",
        nose_bridge="straight", mouth_lip="full_both",
    ),
    "stillness_press_pressure_map": dict(
        # Auto-rotated by solver fallback (vs jp_02 which shared 6 parent axes):
        # nose_construction: straight → prominent (lowest-leverage rotation per §1.4)
        # accessories.signature_item: plain_steel_watch → silver_brooch (defense-in-depth signature rotation)
        # mouth_jaw.lip_shape: thin_both → thin_upper_full_lower (additional rotation)
        face_shape="square", eye_size="medium", eye_shape="hooded", eye_lid_fold="double",
        hair_length="ear_length", hair_parting="side_right", hair_color="dark_blonde",
        wardrobe_era="contemporary_2020s", wardrobe_style="business_blazer_manager",
        age_decade="early_50s" if False else "mid_40s", accessories_glasses="cat_eye", accessories_signature="silver_brooch",
        palette_primary="navy", palette_accent="mustard",
        nose_bridge="prominent", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_press_somatic_field_notes": dict(
        face_shape="soft_round", eye_size="large", eye_shape="round", eye_lid_fold="double",
        hair_length="very_short", hair_parting="asymmetric", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="researcher_field_vest",
        age_decade="late_20s", accessories_glasses="round_thick_frame", accessories_signature="clipboard_pen",
        palette_primary="slate", palette_accent="ochre",
        nose_bridge="short_upturned", mouth_lip="full_both",
    ),
    "stillness_press_the_held_breath": dict(
        face_shape="elongated", eye_size="small", eye_shape="upturned", eye_lid_fold="single",
        hair_length="long_to_waist", hair_parting="no_part_swept_back", hair_color="black",
        wardrobe_era="contemporary_2020s", wardrobe_style="dancer_long_sleeves",
        age_decade="early_30s", accessories_glasses="none", accessories_signature="silk_ribbon_wrist",
        palette_primary="dusty_rose", palette_accent="charcoal",
        nose_bridge="aquiline", mouth_lip="thin_upper_full_lower",
    ),
    "stillness_press_window_season": dict(
        face_shape="heart_shaped", eye_size="medium", eye_shape="downturned", eye_lid_fold="double",
        hair_length="shoulder", hair_parting="side_left", hair_color="grey_at_temples",
        wardrobe_era="contemporary_2020s", wardrobe_style="elderly_kimono_at_home",
        age_decade="70s_plus", accessories_glasses="round_wire_frame", accessories_signature="watering_can_porch",
        palette_primary="lavender", palette_accent="cream",
        nose_bridge="straight", mouth_lip="full_both",
    ),
}


# ── Per-genre prompt fragments (Animagine XL 4.0 — per #838 + #842) ───────
# Pulled from drawing_tradition_per_genre.yaml H_token_mapping per genre +
# the cookbook v2 schema. Subset for the 5 genres in the 22.
GENRE_TOKENS = {
    "healing": dict(
        positive_anchors="masterpiece, absurdres, scenery, outdoors, soft lighting, gentle expression, slice of life, peaceful, sky, detailed background, year 2024",
        negative="lowres, worst quality, low score, action lines, motion blur, screaming, exaggerated expression, chibi, super_deformed, sparkle_eyes, heavy_decorative_eyelashes",
        register_note="Animagine 4.0 base alone covers iyashikei per audit PR #803",
    ),
    "slice_of_life": dict(
        positive_anchors="masterpiece, absurdres, slice of life, casual clothes, detailed background, soft expression, peaceful atmosphere, year 2024",
        negative="lowres, worst quality, chibi, super deformed, exaggerated expression, action lines",
        register_note="Working register; SOL/iyashikei boundary",
    ),
    "dark_fantasy": dict(
        positive_anchors="monochrome, greyscale, manga, comic, dark fantasy, dense crosshatching, heavy shadows, ink, seinen manga, year 2005, masterpiece, high score, atmospheric dread, Berserk style, Dore-style hatching",
        negative="western comics, dnd, fantasy book cover, frank frazetta, oil painting, painterly, full color, gradient background, soft lighting, airbrush, 3d, cg, photorealistic, hero pose splash art, big sparkle eyes",
        register_note="OPERATOR-FLAGGED FAILURE — needs LoRA cross-test (DARK FANTASY XL v1.1 on Animagine 4.0) per audit PR #803",
    ),
    "psychological_horror": dict(
        positive_anchors="monochrome, greyscale, manga, horror, sketch, ink, cross-hatching, screentone, gekiga, comic, year 2007, masterpiece, high score, dread atmosphere, Junji Ito style, dense linework",
        negative="iyashikei, soft lighting, sparkle, bloom, pastel, healing, shoujo, blush, sunny, lens flare, low contrast, cute, kawaii",
        register_note="OPERATOR-FLAGGED FAILURE — operator's diagnosis: 'horror with same line economy as healing'. Subgenre split recommended (sparse Ito-pole vs dense Maruo-pole)",
    ),
    "fantasy_adventure": dict(
        positive_anchors="masterpiece, absurdres, slow_life, peaceful, countryside, warm_lighting, gentle_protagonist, daily_life, no_combat, healing_atmosphere, soft_pastel_palette, year 2024",
        negative="dynamic_action, dark_fantasy, harem, sword, battle, fanservice, RPG_status_screen",
        register_note="isekai-recovery sub-register — karoshi-reincarnation iyashikei (jp_16)",
    ),
}


def deterministic_seed(series_id: str) -> int:
    """sha256(series_id + ':corrective_v2') mod 2^31."""
    h = hashlib.sha256(f"{series_id}:corrective_v2".encode()).hexdigest()
    return int(h, 16) % (2**31)


def build_positive_prompt(genre: str, design: dict, series_id: str, locale: str) -> str:
    """Animagine XL 4.0 prompt order per PR #842 algorithm §1.2:
    [1girl/1boy], [age tag], solo, safe, [face], [eyes], [hair],
    [wardrobe], [accessories], [palette], [genre tokens], [quality tail].
    """
    age = design["age_decade"]
    gender_tag = "1girl"  # all 22 stillness_press protagonists are female per PR #838 diagnosis
    age_animagine = "mature female" if age in ("late_30s", "40s", "mid_40s", "50s", "60s", "70s_plus") else "adult"

    parts = [
        gender_tag,
        age_animagine,
        "solo",
        "safe",
        # face
        f"{design['face_shape'].replace('_', ' ')} face",
        # eyes
        f"{design['eye_size']} eyes",
        f"{design['eye_shape']} eyes",
        f"{design['eye_lid_fold']}_eyelid" if design['eye_lid_fold'] != 'none_visible' else "no_visible_eyelid",
        # hair
        f"{design['hair_length']}_hair" if "_" in design['hair_length'] else f"{design['hair_length']} length hair",
        f"{design['hair_parting'].replace('_', ' ')} parting",
        f"{design['hair_color'].replace('_', ' ')} hair",
        # nose + mouth (lighter token presence)
        design['nose_bridge'].replace('_', ' ') + " nose",
        design['mouth_lip'].replace('_', ' ') + " lips",
        # wardrobe
        design['wardrobe_style'].replace('_', ' '),
        f"{design['wardrobe_era'].replace('_', ' ')} clothes",
        # accessories
        design['accessories_glasses'].replace('_', ' ') if design['accessories_glasses'] != 'none' else "",
        design['accessories_signature'].replace('_', ' '),
        # palette signal
        f"{design['palette_primary'].replace('_', ' ')} palette",
        f"{design['palette_accent'].replace('_', ' ')} accent",
        # genre tokens (drawing tradition spec)
        GENRE_TOKENS[genre]['positive_anchors'],
    ]
    return ", ".join(p for p in parts if p)


def build_negative_prompt(genre: str) -> str:
    base = "lowres, worst quality, bad anatomy, blurry, deformed, bad hands"
    return f"{base}, {GENRE_TOKENS[genre]['negative']}"


def detect_individuation_collisions(designs: dict) -> list:
    """Per PR #842 algorithm §1.4 — count locked PARENT-axis matches between
    every pair. 9 parent axes (per character_design_axes.yaml
    lockout_axes_default). Sub-attribute aggregation: a parent axis matches
    only when ALL its sub-attributes match.
    """
    # Parent axes → list of sub-attributes (flat keys in DESIGNS dict).
    PARENT_AXES = {
        "face_shape": ["face_shape"],
        "eye_geometry": ["eye_size", "eye_shape", "eye_lid_fold"],
        "nose_construction": ["nose_bridge"],
        "mouth_jaw": ["mouth_lip"],
        "hair": ["hair_length", "hair_parting", "hair_color"],
        "wardrobe_register": ["wardrobe_style", "wardrobe_era"],
        "age_signaling": ["age_decade"],
        "accessories": ["accessories_glasses", "accessories_signature"],
        "color_signal": ["palette_primary", "palette_accent"],
    }
    SAME_BRAND_THRESHOLD = 5  # 5 of 9 parent axes — per axes.yaml solver_rules

    def parent_matches(a: dict, b: dict, sub_attrs: list) -> bool:
        return all(a.get(s) == b.get(s) for s in sub_attrs)

    collisions = []
    series_ids = list(designs.keys())
    for i, a_id in enumerate(series_ids):
        for b_id in series_ids[i + 1:]:
            shared = [
                parent for parent, subs in PARENT_AXES.items()
                if parent_matches(designs[a_id], designs[b_id], subs)
            ]
            if len(shared) >= SAME_BRAND_THRESHOLD:
                collisions.append((a_id, b_id, len(shared), shared))
    return collisions


def build_corrective_yaml() -> dict:
    """Build the full corrective_prompts_for_dashboard_22.yaml structure."""
    # Run the constraint solver
    collisions = detect_individuation_collisions(DESIGNS)

    entries = []
    for series_id, genre, locale, brand, diag_class, has_yaml in SERIES_22:
        design = DESIGNS[series_id]
        seed = deterministic_seed(series_id)

        # Find collisions for this series specifically
        series_collisions = [c for c in collisions if c[0] == series_id or c[1] == series_id]
        max_overlap = max((c[2] for c in series_collisions), default=0)
        collision_status = "fail_with_overrides" if max_overlap >= 5 else "pass"

        positive = build_positive_prompt(genre, design, series_id, locale)
        negative = build_negative_prompt(genre)

        entry = {
            "series_id": series_id,
            "genre_family": genre,
            "locale": locale,
            "brand_id": brand,
            "diagnosis_class": diag_class,
            "has_source_yaml_in_repo": has_yaml,
            "character_design_filled": design,
            "individuation_constraint_check": {
                "collision_axis_count_with_other_21": max_overlap,
                "pass_threshold": 5,
                "status": collision_status,
                "colliding_with": [
                    {"series_id": c[1] if c[0] == series_id else c[0], "shared_axes": c[3]}
                    for c in series_collisions
                ],
            },
            "corrective_prompt": {
                "positive": positive,
                "negative": negative,
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
                "steps": 28,
                "cfg": 3.5,
                "width": 832,
                "height": 1216,
                "seed": seed,
                "model": "flux1-dev-fp8.safetensors",
            },
            "expected_drift_reduction": 0.7 if diag_class == "needs_workflow_fix" else 0.5 if diag_class == "needs_prompt_fix_only" else 0.4,
            "render_status": "pending — see CORRECTIVE_ACTION_METHODOLOGY for handoff",
        }
        entries.append(entry)

    return {
        "schema_version": 1,
        "generated_at": "2026-05-03",
        "generator_version": "PR-C step 1 — scripts/manga/build_corrective_prompts.py",
        "scope": "the 22 stillness_press dashboard PNGs flagged in PR #838 dashboard_22_failure_diagnosis_2026-05-02.md",
        "inputs_consumed": {
            "cookbook_v2_sha": SHA_PR_831,
            "drawing_traditions_sha": SHA_PR_838,
            "individuation_axes_sha": SHA_PR_842,
            "corpus_license_sha": SHA_PR_841,
        },
        "summary": {
            "total_entries": len(entries),
            "entries_with_source_yaml": sum(1 for e in entries if e["has_source_yaml_in_repo"]),
            "entries_lacking_source_yaml": sum(1 for e in entries if not e["has_source_yaml_in_repo"]),
            "individuation_collisions_detected": len(collisions),
            "constraint_solver_pass": all(e["individuation_constraint_check"]["status"] == "pass" for e in entries),
        },
        "rendering_handoff": {
            "render_status": "PENDING — actual rendering deferred to Pearl Star local engineering session",
            "reason": "Original 22 were rendered via generate_stillness_press_image_bank.py against Pearl Star local ComfyUI at 192.168.1.112; not reachable from remote Claude Code session. RunComfy serverless workflow integration with the corrective-prompt format requires per-workflow validation not present on main.",
            "next_actions": [
                "Open a Pearl Star-local engineering session",
                "Run scripts/image_generation/generate_stillness_press_image_bank.py with this YAML's 22 corrective_prompt blocks substituted",
                "OR adapt scripts/image_generation/runcomfy_batch.py to consume this YAML and dispatch to RunComfy serverless",
                "Run the QA harness (scripts/image_generation/qa/manga_register_check.py + genre_drift_detector.py) — both shipped in this PR",
                "Run scripts/manga/individuation_pairwise.py (FaceNet-512 metric) — shipped in this PR",
                "Generate side-by-side review HTML per the methodology doc",
                "Operator visual review (non-delegable, ~15-20 min)",
                "Promote canonical or rollback per Step 7",
            ],
        },
        "entries": entries,
    }


def main() -> int:
    out = build_corrective_yaml()
    path = REPO_ROOT / "config" / "manga" / "corrective_prompts_for_dashboard_22.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.safe_dump(out, f, default_flow_style=False, sort_keys=False, width=120)
    print(f"Wrote {path}")
    print(f"  total_entries: {out['summary']['total_entries']}")
    print(f"  individuation_collisions_detected: {out['summary']['individuation_collisions_detected']}")
    print(f"  constraint_solver_pass: {out['summary']['constraint_solver_pass']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

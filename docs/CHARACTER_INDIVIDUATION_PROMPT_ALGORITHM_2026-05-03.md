# Character Individuation — Prompt-Construction Algorithm (Q4, 2026-05-03)

**Status:** AUTHORITY (new, this PR — research-only spec; no implementation code).
**Branch:** `agent/character-individuation-lit-scan-20260503`
**Predecessors:**
- PR #838 commit `3d7118b3` — `config/manga/character_design_axes.yaml` + `character_design_template.yaml` + `CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`
- PR-A Batch 1 (this PR earlier): Q1 vocabulary depth, Q2 metric pick (`character_individuation_metric.yaml`), Q3 workaround empirics

**Cross-references (SHA-pinned):**
- Cookbook: `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ `2881dd970bf2433e2225800ac6f73b1dd0281be5` (#802) — §2.3 weight-syntax responsiveness
- Audit: `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803)

---

## §1 Algorithm spec

### §1.1 Token-budget research per base (empirically grounded)

#### FLUX-schnell — dual encoder (CLIP-L 77 + T5-XXL 256)

| Encoder | Hard cap | Effective character-design budget | Source |
|---|---|---|---|
| CLIP-L/14 | 77 tokens (75 usable) | ~30-40 tokens for character signal | [HF FLUX.1-dev #43](https://huggingface.co/black-forest-labs/FLUX.1-dev/discussions/43) |
| T5-v1.1-XXL | 256 tokens (FLUX.1-schnell) | ~120-180 tokens for character signal | [Boqiang Liang Medium](https://medium.com/@lbq999/flux-1-dev-encoders-and-token-limitations-8631c179eaad), [ComfyUI #6200](https://github.com/comfyanonymous/ComfyUI/issues/6200) |

**Empirical findings:**
- CLIP-L hard-truncates at 77; T5 absorbs the overflow but loses CLIP-L coverage past position 77
- "FLUX general domain knowledge dropped 50–75% when CLIP-L and T5 were given the same prompt" ([HF FLUX.1-dev #77](https://huggingface.co/black-forest-labs/FLUX.1-dev/discussions/77))
- Cookbook §2.3: weight syntax `(token:1.3)` half-responsive on FLUX vs SDXL — practical ceiling 1.3

**Phoenix per-character allocation:**
- CLIP-L (77 cap): ~30 tokens for distinct silhouette signal — face_shape, hair length+color, build, signature accessory, age-decade, demo register. Front-loaded.
- T5-XXL (256 cap): ~150 tokens for full 12-axis prose. ~80-100 tokens reserved for genre cookbook downstream.

#### Qwen-Image — Qwen2.5-VL bidirectional attention (~1000 tokens)

| Aspect | Limit | Source |
|---|---|---|
| Practical prompt cap | ~1000 tokens (v1) | [Segmind](https://blog.segmind.com/qwen-image-prompt-parameter-guide/) |
| Position weighting | **Front-loaded subject** receives heaviest attention | [fal.ai 2512](https://fal.ai/learn/devs/qwen-image-2512-text-to-image-prompt-guide) |
| `(token:1.3)` weight syntax | **Inert** (cookbook §2.3) | PR #802 |
| Prose emphasis | **Active** — "dramatically", "strongly", "prominently" function as soft weights | [fal.ai 2512](https://fal.ai/learn/devs/qwen-image-2512-text-to-image-prompt-guide) |

**Phoenix allocation:** Full 12-axis description ~200-300 prose tokens; ~700 tokens headroom. **No squeeze.**

#### Animagine XL 4.0 — SDXL CLIP-L + CLIP-G dual 77-token encoders

| Encoder | Hard cap | Source |
|---|---|---|
| CLIP-L/14 | 77 tokens | [HF SDXL #60](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/discussions/60) |
| CLIP-G | 77 tokens | Same |
| **With `lpw_stable_diffusion_xl`** | Unlimited (chunks of 75) | [HF Animagine XL 4.0 card](https://huggingface.co/cagliostrolab/animagine-xl-4.0), [O'Reilly Ch.10](https://www.oreilly.com/library/view/using-stable-diffusion/9781835086377/B21263_10.xhtml) |

**Animagine quirk:** Quality tags MUST be at END ([CagliostroLab optimizing post](https://cagliostrolab.net/posts/optimizing-animagine-xl-40-in-depth-guideline-and-update)) — never trained at front; front-loading silently degrades style fidelity.

**Phoenix allocation:** ~150 tokens character signal (~2 chunks). Reserve chunk 3 for style + quality tail.

### §1.2 Token-order research per base

**Animagine XL 4.0 — Danbooru tag-order convention (TRAINED, not heuristic):**

```
1girl|1boy|1other, character_name, from_series, rating,
[everything else in any order], [quality_tags AT END]
```

Phoenix mapping (drop slot 2; Phoenix-original character):

```
1girl, [age tag e.g. "mature female"], solo, [rating: safe],
[face_shape tag], [eye_geometry tags], [hair tags], [wardrobe tags],
[accessories], [posture], [color signals], [environment if any],
masterpiece, high score, great score, absurdres, year 2024
```

**FLUX-schnell — front-load distinct descriptors; CLIP-L gets compressed signal:**

```
[POSITION 1-30 — CLIP-L survives]:
  Subject anchor + age + demo register + highest-leverage axis values
[POSITION 31-150 — T5-only territory]:
  Full prose for remaining axes
[POSITION 151-220 — T5 budget remaining]:
  Style + medium anchor + lighting + composition
```

**Qwen-Image — natural-language sentence order, subject-first:**

```
Sentence 1 (highest weight): Subject — age, gender, face, hair, eyes
Sentence 2: Style/medium
Sentence 3: Environment
Sentence 4: Composition / camera / framing
Sentence 5: Fine details — accessories, posture, color signal
```

### §1.3 Per-axis prompt routing

| Axis | Routing | Per-base mapping |
|---|---|---|
| `face_shape` | POSITIVE (front, all 3) | Animagine: tag (`heart_shaped_face`); Qwen: prose ("softly heart-shaped face"); FLUX: front-loaded explicit |
| `eye_geometry` | POSITIVE (front-mid) | Animagine: comma-separated tags; Qwen: prose sentence; FLUX: prose with prose-emphasis |
| `hair` | POSITIVE (front-mid; very_high leverage) | Animagine: tags; Qwen: full prose; FLUX: prose, front-load if signature silhouette |
| `wardrobe_register` | POSITIVE (mid) | Animagine: era + style tags; Qwen: prose; FLUX: prose |
| `age_signaling` | POSITIVE (front; affects 1girl→`mature female` token) | All 3: explicit |
| `accessories` | POSITIVE (mid) | Animagine: tags; Qwen: prose; FLUX: prose with prose-emphasis on signature_item |
| `color_signal` | POSITIVE (mid; sub-attribute of hair/eyes) | All 3: explicit color |
| `mouth_jaw` | NEGATIVE (forbidden patterns) + light POSITIVE | Negative: Animagine `bow_mouth` etc.; Qwen prose negative; FLUX negative |
| `nose_construction` | SOLVER-ONLY | Differentiation signal; manga noses stylistically minimal |
| `skin_treatment` | SOLVER-ONLY + style-tail POSITIVE | Affects LoRA selection more than per-token |
| `posture_default` | SOLVER-ONLY + light POSITIVE when in-frame | Animagine: tag; Qwen: brief mention |
| `build` | SOLVER-ONLY | Light prose mention if salient; `lockout_default: no` |

**Negative-prompt construction** (auto-derived from axis `forbidden_combinations` + global Animagine negatives):

```
ANIMAGINE NEGATIVE:
  bow_mouth, sparkle_eyes, heavy_decorative_eyelashes,
  child, immature, low score, bad score, low quality, worst quality,
  bad anatomy, blurry, deformed
FLUX NEGATIVE:
  child-like features, big sparkle eyes, heart-shaped pupils,
  blurry, distorted face, deformed
QWEN NEGATIVE (prose form):
  No "bow mouth", no childlike sparkle eyes, no heavy decorative eyelashes,
  no blurry, no distorted features
```

### §1.4 Forbidden-collision detection logic

```python
def detect_collisions(new_char, catalog):
    LOCKED_AXES = [
        "face_shape", "eye_geometry", "nose_construction", "mouth_jaw",
        "hair", "wardrobe_register", "age_signaling", "accessories",
        "color_signal"
    ]   # 9 default lockout axes per axes.yaml schema
    SAME_BRAND_THRESHOLD = 5      # per PR #838 spec
    CROSS_BRAND_THRESHOLD = 7

    same_brand_collisions = []
    cross_brand_collisions = []

    for existing in catalog:
        shared = []
        for axis in LOCKED_AXES:
            if axis_values_match(new_char[axis], existing[axis]):
                shared.append(axis)
        if not shared:
            continue
        record = (existing.series_id, shared)
        if existing.brand_id == new_char.brand_id:
            if len(shared) >= SAME_BRAND_THRESHOLD:
                same_brand_collisions.append(record)
        else:
            if len(shared) >= CROSS_BRAND_THRESHOLD:
                cross_brand_collisions.append(record)

    if same_brand_collisions or cross_brand_collisions:
        return CollisionReport(verdict="REJECT", ...)
    return CollisionReport(verdict="PASS", ...)


def axis_values_match(a, b):
    """Sub-attribute-aware equality. eye_geometry has 5 sub-attrs;
    'match' = all sub-attributes equal."""
    if isinstance(a, dict):
        return all(a.get(k) == b.get(k) for k in a.keys())
    return a == b
```

**Solver fallback chain on REJECT:**

```
ITERATION 1-3 (author-driven): operator/author edits any colliding axis.
  Re-run detect_collisions. If PASS, proceed.
ITERATION 4 (auto-rotate lowest-leverage): solver auto-rotates the
  lowest-leverage colliding axis to a fresh allowed value:
    rotate_priority = [
      nose_construction (medium),
      build (low_to_medium),
      posture_default (low),
      mouth_jaw.lip_shape sub-attribute,
    ]
ITERATION 5 (auto-rotate accessories.signature_item): rotate to a
  catalog-novel entry from accessories.signature_pool.
ESCALATION: catalog axis-vocabulary saturation — operator review.
```

**Decision-tree logging:** Every iteration writes to
`artifacts/character_solver/<series_id>/iterations.jsonl` for audit.

### §1.5 Token-construction step-by-step pseudocode

```python
def build_prompt(character_design, target_base):
    # STEP 1: Constraint solver — verify no collision
    catalog = load_yaml("config/manga/character_brand_registry.yaml")
    collision_report = detect_collisions(character_design, catalog)
    if collision_report.verdict == "REJECT":
        raise CollisionError(collision_report)

    # STEP 2: Per-base token vocabulary mapping (PR-A Batch 1 Leg 1 Q1)
    vocab = load_axis_vocabulary(target_base)
    tokens = {axis: vocab[axis][character_design[axis]] for axis in CHARACTER_DESIGN_AXES}

    # STEP 3: Per-base token order assembly
    if target_base == "animagine_xl_4_0":
        positive = build_animagine_ordered(tokens, character_design)
    elif target_base == "flux_schnell":
        positive = build_flux_front_loaded(tokens, character_design)
    elif target_base == "qwen_image":
        positive = build_qwen_sentences(tokens, character_design)

    # STEP 4: Forbidden-combination filter
    apply_forbidden_filter(positive, character_design)

    # STEP 5: Append base-specific quality tail
    positive = append_quality_tail(positive, target_base)

    # STEP 6: Build negative prompt
    negative = build_negative(character_design, target_base)

    # STEP 7: Return
    return PromptBundle(
        positive=positive,
        negative=negative,
        solver_metadata={
            "collision_report": collision_report,
            "axis_token_map": tokens,
            "target_base": target_base,
            "token_count_estimate": estimate_tokens(positive, target_base),
            "budget_status": ("OK" if estimate_tokens(...) < base_budget(target_base) else "OVER_BUDGET"),
        }
    )
```

---

## §2 Three worked examples

### §2.1 Example 1 — Simple: `stillness_press_anxiety_vol1` (iyashikei, Saki)

**Filled `character_design`:**

```yaml
series_id: stillness_jp_01
brand_id: stillness_press
character_id: saki
gender: female
age_signaling: { apparent_age_decade: late_30s }
face_shape: heart_shaped
eye_geometry: { size: medium, shape: almond, lid_fold: single, eyelash_density: minimal }
hair: { length: shoulder, parting: side_left, fringe_style: side_swept, texture: slight_wave, color_signal: dark_brown }
mouth_jaw: { resting_expression: neutral_soft, lip_shape: thin_upper_full_lower, jaw_width: narrow, chin_shape: soft_pointed }
wardrobe_register: { era_signal: contemporary_2020s, personality_encoding: muted_palette_neutrals }
accessories: { glasses: round_wire_frame, signature_item: ceramic_tea_cup, jewelry: minimal_or_none }
color_signal: { hair: dark_brown, eyes: warm_brown }
demo_register: josei
genre: iyashikei
```

**Step 1 — Solver:** Catalog at this point has 0 entries. PASS, same_brand_max=0.

**Step 2-3 — Per-base assembly:**

#### Animagine XL 4.0
```
Positive: 1girl, mature female, solo, safe,
  heart_shaped_face, almond_eyes, medium_eyes, single_eyelid, sparse_eyelashes, warm_brown_eyes,
  shoulder_length_hair, side_swept_bangs, side_parting, wavy_hair, dark_brown_hair,
  contemporary_clothes, muted_palette, neutral_blouse, slacks,
  round_eyewear, glasses, holding_teacup,
  relaxed_posture, sitting, soft_smile, parted_lips,
  masterpiece, high score, great score, absurdres, year 2024
Negative: bow_mouth, sparkle_eyes, heavy_decorative_eyelashes, child, loli,
  low score, bad score, low quality, worst quality, bad anatomy, blurry, deformed, big_eyes_extreme
Token estimate: ~75 positive (within 1 lpw chunk), ~20 negative. Status: OK.
```

#### Qwen-Image
```
A late-thirties Japanese woman with a softly heart-shaped face and a narrow,
soft-pointed jaw. She has medium-sized almond eyes with single eyelid folds,
sparse natural eyelashes, and warm brown irises. Her dark-brown shoulder-length
hair has a slight wave and a left side-parting, with side-swept bangs and a few
loose strands escaping. She wears a muted-palette contemporary 2020s blouse
with neutral slacks, round wire-frame glasses, and minimal jewelry. Her resting
expression is gently neutral, with a thin upper lip and fuller lower lip. She
holds a small ceramic tea cup, sitting in a slightly slumped relaxed posture.

Rendered in modern josei iyashikei manga style — soft graphite line work, matte
minimal skin tone, gentle ambient natural light. High-detail manga illustration.

Negative (prose): No bow-mouth, no big sparkle eyes, no heavy decorative eyelashes,
no childlike proportions, no blurry features, no distorted face.

Token estimate: ~180 (under 1000 cap). Status: OK.
```

#### FLUX-schnell
```
Manga panel of a late-thirties Japanese woman, softly heart-shaped face,
medium almond eyes, dark-brown shoulder-length wavy hair side-parted, round
wire-frame glasses. She has a narrow soft-pointed jaw, single eyelid fold,
sparse natural eyelashes, warm brown irises, thin upper lip and fuller lower
lip, gently neutral resting expression. She wears a muted-palette contemporary
2020s blouse with neutral slacks, minimal jewelry, holding a small ceramic
tea cup in a slightly slumped relaxed posture. Modern josei iyashikei style,
soft graphite line work, matte minimal skin tone, gentle ambient light, high
detail, manga panel art, cinematic.

Negative: Avoid: childlike features, big sparkle eyes, heart-shaped pupils, bow mouth,
heavy decorative eyelashes, blurry, distorted face, deformed.

Token estimate: First sentence ≈ 28 tokens (CLIP-L 77 cap with ~50 tokens headroom for downstream).
Full positive ≈ 145 tokens (T5-XXL 256 cap with ~100-token headroom). Status: OK.
```

### §2.2 Example 2 — Cross-genre: `stillness_press_mecha_us` ("After the Cockpit")

Operator-flagged failing pair. Per PR #838 cross-genre rules: medium anchor + subject anchor with framing pattern.

**Filled `character_design` (Mara, ex-mech pilot):**

```yaml
series_id: stillness_us_05
character_id: mara
gender: female
age_signaling: { apparent_age_decade: late_20s }
face_shape: oval
eye_geometry: { size: medium, shape: almond, spacing: wide, lid_fold: double, eyelash_density: minimal }
hair: { length: chin_bob, parting: no_part_swept_back, fringe_style: no_fringe, texture: straight, color_signal: black }
wardrobe_register: { era_signal: near_future, personality_encoding: military_utilitarian_civilian_transition }
accessories: { glasses: none, signature_item: dog_tags, jewelry: minimal }
color_signal: { hair: black, eyes: cool_grey }
demo_register: josei
genre_primary: iyashikei
genre_secondary: mecha
cross_genre_anchor:
  medium_anchor: "manga panel"
  subject_anchor: "former mech pilot in civilian clothing"
  framing_pattern: "After the Cockpit — daily quiet life shot"
```

**Step 1 — Solver vs catalog {Saki, Mara}:** shared with Saki = 4 axes (under 5 same-brand threshold). PASS.

**Per-base assembly (showing cross-genre weight syntax application):**

#### Animagine XL 4.0 (full weight responsiveness)
```
1girl, mature female, solo, safe,
oval_face, almond_eyes, medium_eyes, double_eyelid, sparse_eyelashes,
wide_set_eyes, cool_grey_eyes,
short_bob, chin_length_bob, no_bangs, swept_back_hair, straight_hair, black_hair,
near_future_clothes, military_utilitarian:1.2, civilian_jacket, plain_pants,
dog_tags:1.3, minimal_jewelry,
slight_frown, thin_lips, neutral_expression,
upright_posture, alert_stance,
(soft iyashikei atmosphere:1.4), quiet daily_life, after_the_cockpit_framing,
masterpiece, high score, great score, absurdres, year 2024

Negative: mecha_close_up, robot_hardware, cockpit_interior, action_combat,
bow_mouth, sparkle_eyes, heavy_decorative_eyelashes, child, loli,
low score, bad score, low quality, worst quality, bad anatomy, blurry, deformed
```

`(soft iyashikei atmosphere:1.4)` boosts iyashikei against mecha-leaning subject anchor — cookbook §2.3 confirmed full-responsiveness on Animagine.

#### Qwen-Image (prose emphasis — weight syntax inert)
```
A late-twenties woman with a clean oval face, medium wide-set almond eyes
with double lid folds and minimal natural lashes, cool grey irises. Her hair
is a neat short black chin-length bob, swept back with no bangs, in a
military-utilitarian style. She wears a near-future civilian jacket over plain
pants, with dog tags clearly visible at her collar — a subtle but prominent
signal of her past as a mech pilot. Her expression is a slight resting frown,
thin lips, jaw of medium width with a rounded chin. She stands in an alert
upright posture with residual military bearing.

The mood is dramatically iyashikei — the atmosphere is softly quiet, gently
contemplative, deliberately distant from any mecha hardware. This is her
daily quiet life After the Cockpit. Rendered as a manga panel, soft graphite
line work, matte minimal skin tone, gentle ambient natural light filling a
small kitchen interior.
```

Prose-emphasis "dramatically iyashikei", "softly quiet", "gently contemplative", "deliberately distant" carries weight — no SD weight syntax.

#### FLUX-schnell (CLIP-L survives subject + framing only)
```
Manga panel, late-twenties former mech pilot in quiet civilian life, oval face,
short black chin-bob, dog tags. She has medium wide-set almond eyes with
double lid folds and minimal lashes, cool grey irises, slight resting frown,
thin lips, rounded chin, alert upright posture with residual military bearing.
She wears a near-future civilian jacket over plain pants, no glasses, minimal
jewelry. The atmosphere is strongly iyashikei — softly quiet, gently
contemplative, completely free of mecha hardware. After the Cockpit framing,
quiet kitchen interior, soft graphite line work, matte minimal skin, gentle
ambient natural light, high detail, cinematic.
```

CLIP-L survivors (~25 tokens): "Manga panel" + "former mech pilot in quiet civilian life" + "oval face" + "short black chin-bob" + "dog tags" — the medium-anchor + subject-anchor + framing-pattern triplet from PR #838's mecha drift recipe.

### §2.3 Example 3 — Collision-edge: `stillness_press_quiet_ferns`

Hypothetical author has filled in Mio with 8 of 9 axes matching Saki.

**Step 1 — Solver run #1:**

```
detect_collisions(mio, catalog={saki, mara}):
  vs saki: shared = 8 axes → REJECT (over threshold of 5)
  vs mara: shared = 4 axes → under threshold

VERDICT: REJECT
colliding_axes: face_shape, eye_geometry, hair, age_signaling,
                wardrobe_register, accessories, mouth_jaw, nose_construction
colliding_series_ids: [stillness_jp_01]
```

**Diagnostic:** "Saki and Mio are visually indistinguishable as series leads. Recommended: rotate at least 3 of: face_shape, eye_geometry, hair (very_high leverage)."

**Iteration 2 — author edits face_shape: heart_shaped → oval; hair.length: shoulder → ear_length:**
```
vs saki: shared = 6 axes → still REJECT
```

**Iteration 3 — author edits eye_geometry sub-attrs:**
```yaml
eye_geometry:
  spacing: wide          # was standard
  lid_fold: double       # was single
```
```
vs saki: shared = 5 axes → REJECT (at threshold; spec says ≥5 → reject)
```

**Iteration 4 — solver auto-rotate (lowest-leverage):**
```
nose_construction.bridge_length: short → medium
vs saki: shared = 4 axes → PASS
```

**Iteration 5 — solver auto-rotate signature_item (defense-in-depth):**
```
accessories.signature_item: ceramic_tea_cup → wooden_walking_stick
vs saki: shared = 3 axes
```

**Final assembled prompt — Animagine XL 4.0:**
```
1girl, mature female, solo, safe,
oval_face, almond_eyes, medium_eyes, wide_set_eyes, double_eyelid, sparse_eyelashes,
ear_length_hair, center_part, straight_bangs, straight_hair, dark_brown_hair,
contemporary_clothes, neutral_blouse, slacks,
round_eyewear, glasses, holding_walking_stick, wooden_cane,
soft_smile, thin_upper_lip,
relaxed_posture,
masterpiece, high score, great score, absurdres, year 2024

Negative: bow_mouth, sparkle_eyes, heavy_decorative_eyelashes, child, loli,
low score, bad score, low quality, worst quality, bad anatomy, blurry,
deformed, ceramic_teacup
```

(Note: `ceramic_teacup` added to negative as defense-in-depth on top of solver-level signature_item rotation.)

**Solver metadata:**
```yaml
collision_report:
  initial_verdict: REJECT
  initial_collision_count: 8
  iterations: 5
  final_verdict: PASS
  final_collision_count: 3
  rotated_by_solver:
    - { axis: nose_construction.bridge_length, from: short, to: medium, reason: lowest-leverage colliding }
    - { axis: accessories.signature_item, from: ceramic_tea_cup, to: wooden_walking_stick, reason: defense-in-depth }
  decision_log_path: artifacts/character_solver/stillness_jp_07/iterations.jsonl
budget_status: OK
```

---

## §3 Implementation status

This document is **research-only spec**. Implementation is a follow-up engineering PR:

1. `scripts/manga/character_individuation_solver.py` — implements `detect_collisions()` + iteration logic (~400 LOC)
2. `scripts/manga/character_prompt_builder.py` — implements `build_prompt()` per-base routing (~300 LOC)
3. `scripts/manga/character_design_validator.py` — pre-solver validator for forbidden_combinations + lockout-axis count (~200 LOC)

Estimated engineering effort: ~2 days. Out of scope for this research PR.

---

## Sources

- [HF FLUX.1-dev #43 (token limits)](https://huggingface.co/black-forest-labs/FLUX.1-dev/discussions/43)
- [Boqiang Liang Medium — FLUX encoders](https://medium.com/@lbq999/flux-1-dev-encoders-and-token-limitations-8631c179eaad)
- [HF FLUX.1-dev #77 (CLIP-L vs T5)](https://huggingface.co/black-forest-labs/FLUX.1-dev/discussions/77)
- [ComfyUI #6200](https://github.com/comfyanonymous/ComfyUI/issues/6200)
- [HF Animagine XL 4.0](https://huggingface.co/cagliostrolab/animagine-xl-4.0)
- [CagliostroLab — Optimizing Animagine 4.0](https://cagliostrolab.net/posts/optimizing-animagine-xl-40-in-depth-guideline-and-update)
- [HF SDXL #60](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/discussions/60)
- [Diffusion Tokenizer](https://sd-tokenizer.rocker.boo/)
- [O'Reilly Ch.10](https://www.oreilly.com/library/view/using-stable-diffusion/9781835086377/B21263_10.xhtml)
- [Segmind — Qwen-Image guide](https://blog.segmind.com/qwen-image-prompt-parameter-guide/)
- [fal.ai — Qwen 2512 prompt guide](https://fal.ai/learn/devs/qwen-image-2512-text-to-image-prompt-guide)
- [WaveSpeedAI — Qwen-Image 2.0](https://wavespeed.ai/blog/posts/blog-how-to-use-qwen-image-2-0-text-to-image-editing/)

WebFetch tally: 4/8 (50%). WebSearch: 4.

---

*End of CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md.*

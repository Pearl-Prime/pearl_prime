# V2 Phase A.4 — Pearl_Editor character_design YAML pre-staged checklist

**Status:** pre-staged by Pearl_Dev session 2026-05-07. Waits on Pearl_Editor + brand owners to fill the YAML instances.

**Authority:** [`docs/PEARL_ARCHITECT_STATE.md`::MANGA-LAYERED-PIPELINE-V2-01](../../docs/PEARL_ARCHITECT_STATE.md) §A4. Implementation reference: [`docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`](../../docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md) §2.1. Vocabulary: [`config/manga/character_design_axes.yaml`](../../config/manga/character_design_axes.yaml). Schema: [`config/manga/character_design_template.yaml`](../../config/manga/character_design_template.yaml).

**Estimated effort:** ~15 minutes per teacher × 12 = ~3 hr operator time, parallelizable across brand owners.

---

## How to use this checklist

1. **Open the per-teacher block below.** Each block has axis seeds — concrete starting values for the 12 axes inferred from `brand_lora_plans.yaml::character_loras` notes + (where available) the brand's character_model_sheets.
2. **Copy the section** into `config/source_of_truth/manga_profiles/series/<series_id>.yaml` under a `character_design:` key. (One series per teacher per brand; if a brand has multiple series with the same teacher, each series file gets its own block.)
3. **Fill the 12 axes.** Allowed values per axis: `config/manga/character_design_axes.yaml`. Free-form fields like `mangaka_tradition` and `signature_shape_note` are encouraged but not parsed by the solver.
4. **Mark ≥ 9 axes `lockout: yes`.** The solver requires this; the optional 3 (`build`, `posture_default`, `skin_treatment`) are typically left unlocked unless they're identity-load-bearing for a given character.
5. **Run the solver:**
   ```bash
   PYTHONPATH=. python3 -m scripts.manga.character_individuation.constraint_solver \
       --series-yaml config/source_of_truth/manga_profiles/series/<series_id>.yaml
   ```
   On `ACCEPT`: commit. On `REJECT`: solver returns colliding axes; mutate one or more high-leverage axes (`eye_geometry`, `hair`, `face_shape`) and re-run.
6. **Catalog audit:** run `--validate-all` to verify the whole catalog stays distinct as new entries land.

---

## The 12 named teachers

| # | teacher_id | brand | brand_suffix | trigger_word | model_sheets present? |
|---|---|---|---|---|---|
| 1 | `ahjan` | stillness_press | sp | `ahjan_sp` | **YES** — 12 sheets + 8 expressions at `artifacts/manga/image_bank/stillness_press/character_model_sheets.json` |
| 2 | `joshin` | cognitive_clarity | cc | `joshin_cc` | NO — Pearl_Editor + brand owner generate via Phase B6 |
| 3 | `pamela_fellows` | somatic_wisdom | sw | `pamela_sw` | NO — Phase B6 |
| 4 | `master_feung` | qi_foundation | qf | `feung_qf` | NO — Phase B6 |
| 5 | `miki` | digital_ground | dg | `miki_dg` | NO — Phase B6 |
| 6 | `maat` | heart_balance | hb | `maat_hb` | NO — Phase B6 |
| 7 | `junko` | relational_calm | rc | `junko_rc` | NO — Phase B6 |
| 8 | `master_wu` | warrior_calm | wc | `wu_wc` | NO — Phase B6 |
| 9 | `master_sha` | sleep_restoration | sr | `sha_sr` | NO — Phase B6 |
| 10 | `omote` | body_memory | bm | `omote_bm` | NO — Phase B6 |
| 11 | `ra` | solar_return | so | `ra_so` | NO — Phase B6 |
| 12 | `sai_ma` | devotion_path | dp | `sai_ma_dp` | NO — Phase B6 |

Phase B6 generates canonical reference character sheets per teacher (the Phase B Pearl_Dev session task; uses the post-fill character_design YAML as input to seed the reference-image generation).

---

## Per-teacher seed blocks

Each block is **opinionated about high-leverage axes** (`face_shape`, `eye_geometry`, `hair`) where the brand_lora_plans notes give clear direction, and **TBD on lower-leverage axes** that need brand-owner judgment. The mangaka-tradition vocabulary in axes YAML is the right place to ground deliberate distinctness choices.

### 1. ahjan (stillness_press)

```yaml
character_design:
  series_id: stillness_press_<topic>_vol1   # Pearl_Editor sets per series
  brand_id: stillness_press
  market_demo: seinen                       # contemplative seinen, not josei
  genre_family: healing
  axes:
    face_shape:
      value: oval                           # neutral; pair with mature seinen markers
      lockout: yes
      mangaka_tradition: "Asano late-period seinen oval (not Adachi sports-shonen)"
    eye_geometry:
      size: small                           # seinen register
      shape: almond
      spacing: standard
      lid_fold: double
      eyelash_density: minimal
      lockout: yes
    nose_construction:
      bridge_angle: straight
      bridge_length: medium
      tip_shape: rounded
      nostril_visibility: drawn             # seinen drawn, not implied
      lockout: yes
    mouth_jaw:
      resting_expression: neutral_soft
      jaw_width: medium
      chin_shape: rounded
      lip_shape: thin_both
      lockout: yes
    hair:
      length: ear_length
      parting: side_left
      fringe_style: side_swept
      texture: slight_wave
      color_signal: black                   # South Asian male anchor
      lockout: yes
    color_signal:
      value: warm_earth_tone                # forest-refuge wardrobe per brand notes
      lockout: yes
    wardrobe_register:
      value: monastic_casual                # contemplative bearing
      lockout: yes
    age_signaling:
      value: late_30s                       # mid-career teacher
      lockout: yes
    accessories:
      value: prayer_beads_subtle            # signature item
      lockout: yes
    build:
      value: average
      lockout: no                           # leverage low; leave free
    skin_treatment:
      value: clean
      lockout: no
    posture_default:
      value: contemplative_grounded
      lockout: no
```

### 2. joshin (cognitive_clarity)

```yaml
character_design:
  series_id: cognitive_clarity_<topic>_vol1
  brand_id: cognitive_clarity
  market_demo: josei
  genre_family: essay                       # cognitive_clarity primary per allocation
  axes:
    face_shape:
      value: heart_shaped                   # josei-soft (NOT shojo)
      lockout: yes
    eye_geometry:
      size: small                           # josei seinen-adjacent
      shape: almond
      spacing: narrow
      lid_fold: single                      # epicanthic, Japanese-American
      eyelash_density: minimal
      lockout: yes
    # ... fill remaining axes per character_design_axes.yaml
    # high-leverage seeds from brand_lora_plans notes:
    #   - precise gaze → eye_geometry: shape: sharp_angular OR almond
    #   - zen authority → posture: composed_alert (lockout: no acceptable)
    #   - Japanese-American female → hair: black or dark_brown; texture: straight
```

### 3. pamela_fellows (somatic_wisdom)

```yaml
character_design:
  series_id: somatic_wisdom_<topic>_vol1
  brand_id: somatic_wisdom
  market_demo: josei
  genre_family: romance                     # somatic_wisdom primary per allocation
  axes:
    # Caucasian female; clinical warmth; somatic awareness posture
    face_shape:
      value: oval                           # neutral; differentiate via eye + hair
      lockout: yes
    eye_geometry:
      size: medium                          # warmer than seinen-small
      shape: almond
      lid_fold: double
      eyelash_density: moderate
      lockout: yes
    hair:
      length: shoulder
      parting: center
      fringe_style: curtain
      texture: slight_wave
      color_signal: dark_blonde             # Caucasian anchor
      lockout: yes
    # ... fill remaining axes
```

### 4. master_feung (qi_foundation)

```yaml
character_design:
  series_id: qi_foundation_<topic>_vol1
  brand_id: qi_foundation
  market_demo: seinen
  genre_family: cultivation                 # qi_foundation primary per allocation
  axes:
    # Chinese male; elder presence; qigong practitioner posture
    face_shape:
      value: angular_long                   # seinen-realist elder
      lockout: yes
    eye_geometry:
      size: small
      shape: almond
      lid_fold: single                      # epicanthic
      eyelash_density: minimal
      lockout: yes
    hair:
      length: very_short                    # OR: long_to_waist for cultivation register
      texture: straight
      color_signal: grey_at_temples         # elder
      lockout: yes
    age_signaling:
      value: late_50s_to_60s
      lockout: yes
    # ... fill remaining
```

### 5. miki (digital_ground)

```yaml
character_design:
  series_id: digital_ground_<topic>_vol1
  brand_id: digital_ground
  market_demo: josei                        # OR mature; brand owner judgment
  genre_family: supernatural_everyday       # digital_ground primary
  axes:
    # Japanese-American female; Gen Z bearing; digital native energy
    face_shape:
      value: round                          # Gen Z youth signal
      lockout: yes
    eye_geometry:
      size: medium
      shape: round                          # younger register than other teachers
      lid_fold: double
      eyelash_density: moderate
      lockout: yes
    hair:
      length: chin_bob
      parting: asymmetric
      fringe_style: asymmetric
      texture: straight
      color_signal: dark_brown_with_highlight  # Gen Z signal
      lockout: yes
    age_signaling:
      value: mid_20s
      lockout: yes
    # ... fill remaining
```

### 6. maat (heart_balance)

```yaml
character_design:
  series_id: heart_balance_<topic>_vol1
  brand_id: heart_balance
  market_demo: josei
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Egyptian-coded female; regal bearing; shadow work intensity
    face_shape:
      value: elongated                      # regal anchor
      lockout: yes
    eye_geometry:
      size: medium
      shape: sharp_angular                  # shadow-work intensity
      lid_fold: double
      eyelash_density: moderate
      lockout: yes
    hair:
      length: long_to_waist
      texture: straight                     # OR coiled depending on coding choice
      color_signal: black
      lockout: yes
    accessories:
      value: gold_signature_jewelry         # Egyptian-coded
      lockout: yes
    # ... fill remaining
```

### 7. junko (relational_calm)

```yaml
character_design:
  series_id: relational_calm_<topic>_vol1
  brand_id: relational_calm
  market_demo: josei
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Japanese female; wabi-sabi simplicity; radical acceptance
    face_shape:
      value: soft_round                     # wabi-sabi soft
      lockout: yes
    eye_geometry:
      size: small
      shape: almond
      lid_fold: single
      eyelash_density: minimal              # iyashikei restrained
      lockout: yes
    hair:
      length: shoulder
      parting: center
      fringe_style: straight_blunt
      texture: straight
      color_signal: dark_brown
      lockout: yes
    wardrobe_register:
      value: simple_natural_fiber           # wabi-sabi anchor
      lockout: yes
    # ... fill remaining
```

### 8. master_wu (warrior_calm)

```yaml
character_design:
  series_id: warrior_calm_<topic>_vol1
  brand_id: warrior_calm
  market_demo: seinen
  genre_family: cultivation                 # tentpole; battle is en_US matrix primary (coexist registered)
  axes:
    # Chinese male; martial composure; controlled power in stillness
    face_shape:
      value: square                         # gekiga-seinen masculine
      lockout: yes
    eye_geometry:
      size: small
      shape: sharp_angular                  # martial intensity
      lid_fold: single
      eyelash_density: minimal
      lockout: yes
    build:
      value: muscular_compact               # martial; lockout this one (high-leverage for wu)
      lockout: yes
    posture_default:
      value: rooted_alert
      lockout: yes
    # ... fill remaining
```

### 9. master_sha (sleep_restoration)

```yaml
character_design:
  series_id: sleep_restoration_<topic>_vol1
  brand_id: sleep_restoration
  market_demo: seinen
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Chinese male; healing presence; luminous calm
    face_shape:
      value: oval
      lockout: yes
    eye_geometry:
      size: medium                          # healing-warm, not seinen-small
      shape: almond
      lid_fold: double
      eyelash_density: minimal
      lockout: yes
    color_signal:
      value: cool_luminous_blue             # sleep / luminous anchor
      lockout: yes
    # ... fill remaining
```

### 10. omote (body_memory)

```yaml
character_design:
  series_id: body_memory_<topic>_vol1
  brand_id: body_memory
  market_demo: seinen
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Japanese male; Noh-influenced bearing; grief held in body
    face_shape:
      value: angular_long                   # Noh-influenced
      lockout: yes
    eye_geometry:
      size: small
      shape: hooded                         # held grief register
      lid_fold: single
      eyelash_density: minimal
      lockout: yes
    posture_default:
      value: held_grief_stillness
      lockout: yes                          # high-leverage for omote
    # ... fill remaining
```

### 11. ra (solar_return)

```yaml
character_design:
  series_id: solar_return_<topic>_vol1
  brand_id: solar_return
  market_demo: <ambiguous-coded — operator decision>
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Ambiguous ethnicity; post-burnout rebirth energy; ember warmth
    face_shape:
      value: oval
      lockout: yes
    eye_geometry:
      size: medium
      shape: almond
      lid_fold: double
      eyelash_density: moderate
      lockout: yes
    color_signal:
      value: ember_warm_orange              # signature warmth
      lockout: yes
    # ... fill remaining; ambiguous ethnicity = avoid heavy ethnicity-locking tokens
```

### 12. sai_ma (devotion_path)

```yaml
character_design:
  series_id: devotion_path_<topic>_vol1
  brand_id: devotion_path
  market_demo: josei
  genre_family: <pick from brand_genre_allocation>
  axes:
    # Indian female; bhakti devotion radiance; flowing presence
    face_shape:
      value: heart_shaped
      lockout: yes
    eye_geometry:
      size: large                           # bhakti radiance — but watch shojo_eye_in_josei rule
      shape: almond
      lid_fold: double
      eyelash_density: moderate             # NOT heavy_decorative (forbidden in josei)
      lockout: yes
    hair:
      length: long_to_waist                 # flowing presence
      parting: center
      texture: slight_wave
      color_signal: black
      lockout: yes
    wardrobe_register:
      value: flowing_devotional_garment     # signature
      lockout: yes
    # ... fill remaining
```

---

## After all 12 are filled

1. **Run catalog audit** — verifies the 12 don't collide with each other:
   ```bash
   PYTHONPATH=. python3 -m scripts.manga.character_individuation.constraint_solver \
       --validate-all
   ```
2. **Phase B6** generates canonical reference character sheet PNG per teacher (Pearl_Dev session, ~30 min per teacher; uses these YAML instances as input to PuLID/Animagine reference-image generation on Pearl Star).
3. **Phase B7** wires the reference-image input pathway into the prompt compiler so panel rendering can condition on the canonical reference.

The 12 character_design instances + their reference sheets = the deterministic identity-lock backbone for every panel render across the catalog from this point forward. Phase A's load-bearing deliverable.

# Character Individuation Pipeline — Specification (2026-05-02)

**Status:** AUTHORITY (new, this PR — research-only spec; no implementation code).
**Branch:** `agent/manga-drawing-traditions-research-20260502`
**Companion files:**
- `config/manga/character_design_axes.yaml` — the 12-axis vocabulary
- `config/manga/character_design_template.yaml` — per-series instance schema
- `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md` — visual evidence
- `artifacts/research/average_face_problem_eval_2026-05-02.md` — diffusion-attractor literature

**Cross-references (SHA-pinned):**
- Cookbook research: `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ `2881dd970bf2433e2225800ac6f73b1dd0281be5` (#802) — §6 character consistency
- Community audit: `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803) — Character consistency (PuLID-FaceNet recommendation; InsightFace dependencies are commercially blocked)

---

## §0 The problem this pipeline solves

The operator inspected 22 stillness_press dashboard PNGs (2026-05-02) and observed:

> Across 22 main_character.png images, the protagonists read as variations of the same person — same face shape, same age, same hair construction, same expression range. No two characters are visually distinct enough to function as separate series leads.

Direct visual inspection of 6 representative PNGs (this research PR) confirmed: 5 of 6 protagonists collapse to a near-identical face geometry — oval-to-heart face shape, large rounded anime-default eyes, soft jaw, slight upturned nose, bobbed-or-short hair, late-20s/early-30s appearance. The 6th (jp_08 dark_fantasy) differs in the wrong direction — anime-fantasy waifu — rather than via the 12-axis individuation vocabulary needed.

With 200+ planned series across 12-24 brands, every protagonist must be visually distinct enough to function as a separate series lead. This pipeline makes that distinctiveness deterministic and verifiable.

---

## §1 The pipeline overview

```
                ┌────────────────────────────────────┐
                │ 1. AUTHOR fills character_design   │
                │    YAML per series (12 axes)       │
                └────────────────────────────────────┘
                                 │
                                 ▼
                ┌────────────────────────────────────┐
                │ 2. CONSTRAINT SOLVER validates     │
                │    against catalog                 │
                │    (axis collision detection)      │
                └────────────────────────────────────┘
                          │             │
                          ▼             ▼
                  ┌───────────┐  ┌─────────────┐
                  │ COLLISION │  │  ALL CLEAR  │
                  └───────────┘  └─────────────┘
                          │             │
                          ▼             ▼
                ┌──────────┐    ┌───────────────────┐
                │ Author   │    │ 3. PROMPT BUILDER │
                │ iterates │    │    emits tokens   │
                └──────────┘    │    per axis       │
                                └───────────────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ 4. RENDER PASS   │
                                │ (commercial-clean│
                                │  base + opt LoRA │
                                │  + opt PuLID-    │
                                │  FaceNet ref     │
                                │  image)          │
                                └──────────────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │ 5. QA HARNESS    │
                                │ pairwise face    │
                                │ distance metric  │
                                │ vs catalog       │
                                └──────────────────┘
                                         │
                                         ▼
                          ┌──────────────────────────┐
                          │ pass = check in           │
                          │ fail = back to step 1     │
                          └──────────────────────────┘
```

---

## §2 Stage-by-stage specification

### §2.1 Stage 1 — Author fills character_design YAML

Schema: `config/manga/character_design_template.yaml`. Every new series MUST produce a filled instance under `config/source_of_truth/manga_profiles/series/<series_id>.yaml` under a `character_design:` block before image-generation pipeline runs.

Validation rules per `config/manga/character_design_axes.yaml`:
- All 12 axes present (no nulls)
- Minimum 9 of 12 axes have `lockout: yes`
- No forbidden axis combinations (e.g., `bow_mouth + josei` rejected pre-solver)

### §2.2 Stage 2 — Constraint solver

**Implementation language:** Python (out of scope for this research PR; engineering follow-up).

**Algorithm (pseudocode):**

```
function check_collision(new_design, catalog, brand_scope):
    locked_axes = [a for a in new_design.axes if a.lockout == "yes"]
    if len(locked_axes) < 9:
        return REJECT("minimum 9 lockout axes required")

    for forbidden_rule in forbidden_combinations:
        if matches(new_design, forbidden_rule):
            return REJECT(f"forbidden combination: {forbidden_rule.rule_id}")

    same_brand_threshold = 5
    cross_brand_threshold = 7

    for existing in catalog:
        if existing.brand == new_design.brand:
            threshold = same_brand_threshold
        else:
            threshold = cross_brand_threshold

        match_count = count_matching_locked_axes(new_design, existing)
        if match_count >= threshold:
            return REJECT(
                f"collision with {existing.series_id} on {match_count} locked axes",
                colliding_axes=[axis for axis in locked_axes if matches_value(new_design, existing, axis)]
            )

    return ACCEPT

function count_matching_locked_axes(a, b):
    # Iterate axes in priority order from character_design_axes.yaml::solver_rules.axis_priority_order_for_solver
    # eye_geometry, hair, color_signal, face_shape, mouth_jaw, ...
    count = 0
    for axis in axis_priority_order:
        if a.axes[axis].lockout == "yes" and b.axes[axis].lockout == "yes":
            if a.axes[axis].value == b.axes[axis].value:
                count += 1
    return count
```

**When the solver REJECTs**, the author iterates: the solver returns the colliding axes so the author can deliberately mutate one or more high-leverage axes (eye_geometry / hair / face_shape) to produce a distinct character.

**Fallback rotation strategy** when the solver can't find a valid distinct combination after N author iterations:
1. Rotate the lowest-leverage locked axis (e.g., `nose_construction`) into a fresh value
2. If still colliding, rotate `accessories` to a unique signature_item
3. If still colliding, escalate to operator review — the catalog has reached saturation on this brand's character-design space, and the brand needs a deliberate axis-vocabulary expansion

**Estimated implementation effort:** 200-400 LOC Python; ~1 engineering day. Out of scope for this research PR.

### §2.3 Stage 3 — Prompt builder

Per the validated `character_design` block, the prompt builder emits axis-specific tokens routed by `template.render.prompt_axis_priority`:

- **positive_prompt_axes:** `face_shape, eye_geometry, hair, wardrobe_register, age_signaling, accessories, color_signal` — these go into the positive prompt as descriptive token fragments
- **negative_prompt_axes:** `mouth_jaw` — expressed as negation tokens (e.g., "no bow_mouth")
- **solver_only_axes:** `skin_treatment, posture_default, build, nose_construction` — used by solver for collision detection only; not in prompt

**Per-base-model adaptation** (commercial-clean stack from audit PR #803):

| Base | Token strategy |
|---|---|
| Animagine XL 4.0 | Booru-tag style: `realistic eye proportions, small almond eyes, single eyelid, side-parted shoulder bob, dark brown hair with grey at temples, late 30s, smile lines visible, round wire-frame glasses, muted brown palette, deep teal accent` |
| Qwen-Image | Natural-language prose: "An adult woman in her late 30s with a heart-shaped face, small almond eyes with single eyelids, a side-parted shoulder bob in dark brown with grey at the temples, round wire-frame glasses, dressed in a layered cardigan and corduroy skirt, in a muted brown and deep teal palette" |
| FLUX-schnell | Front-loaded natural-language: "Adult woman, heart-shape face, small almond eyes, single eyelid, dark-brown shoulder bob with grey-temple, round wire-frame glasses, late 30s, muted brown palette" — front-load most distinctive axes |

### §2.4 Stage 4 — Render pass

Commercial-clean base stack per audit PR #803:

| Genre cluster | Recommended base | Character lock |
|---|---|---|
| B&W manga panel (mecha, dark_fantasy, horror, battle, mystery, seinen-dramatic) | Animagine XL 4.0 + per-genre LoRA | PuLID-FLUX-FaceNet (`lldacing/ComfyUI_PuLID_Flux_ll`) — Apache 2.0 + commercial-clean facenet-pytorch VGGFace2 |
| Color webtoon (romance, slice_of_life-color, food, comedy) | FLUX-schnell or Qwen-Image | PuLID-FLUX-FaceNet |
| Sparse iyashikei (healing, supernatural_everyday) | Animagine XL 4.0 base (no LoRA per audit) | PuLID-FLUX-FaceNet OR no lock if catalog distinctiveness sufficient |
| Cultivation / manhwa-vertical | Animagine XL 4.0 | PuLID-FLUX-FaceNet |

**Reference-image strategy:**
- For one-shot named cast members: PuLID-FaceNet from a single canonical character-sheet image (generated from the cookbook's prompt + the `character_design` YAML's prompt fragments)
- For series-level consistency (12+ chapters): once 1 canonical sheet exists, train a per-character LoRA via `ai-toolkit (ostris, MIT)` per audit PR #803. PuLID becomes the bridge while LoRA training catches up.

**Seed strategy:** deterministic seed = hash(`series_id + character_role`) so re-runs are reproducible.

**InsightFace blocked:** InstantID and IP-Adapter-FaceID rely on InsightFace AntelopeV2 which is non-commercial — DO NOT use these per audit PR #803. PuLID-FaceNet variant only.

### §2.5 Stage 5 — QA harness

Pairwise face-distance metric across catalog using a commercial-clean face-recognition library:

**Recommended primary:** `facenet-pytorch` (commercial-clean VGGFace2) + cosine-distance over face embeddings.

**Recommended fallback:** `DeepFace` library with `Facenet512` model.

**Threshold (proposed, requires empirical calibration in follow-up PR):**
- Pairwise face-distance < 0.4 → fail (too similar — same person)
- 0.4 ≤ distance < 0.55 → borderline (manual operator review)
- distance ≥ 0.55 → pass (distinct)

The QA harness runs after each render pass and before the image is committed to disk. Failures trigger a regeneration with one or more axis values mutated.

---

## §3 The "average face" problem (Q3.D summary)

**Status:** literature scan deferred to follow-up PR (`average_face_problem_eval_2026-05-02.md` carries the deferred-stub structure).

**What we know without the literature scan:**

Diffusion models exhibit a Gaussian "average face" attractor — without strong character-design tokens, generated characters drift toward a small set of training-distribution modes. The cookbook PR §1.2 documents that AnimagineXL 4.0 / Qwen-Image / FLUX-schnell each have different attractor strengths:

- **Animagine XL 4.0** — strong attractor toward shojo / shonen-soft default. Heavily anime-trained. Without explicit "realistic eye proportions, small almond eyes, mature female" tokens, the model defaults to large-eyed shojo register. The 12-axis prompt token-stack is essential to override.
- **Qwen-Image** — broader natural-language prior; weaker attractor than Animagine. Responds well to explicit "in their late 30s with a heart-shaped face" descriptions. Best of the three for character distinctiveness from prompt alone.
- **FLUX-schnell** — at 4 steps, strong attractor due to distillation pressure. Smoke-test at 8 steps recommended for character-design work.

**Recommendation for Phoenix Omega's 200+ series catalog:**

1. **First-line individuation via prompt-stack + 12-axis YAML** — works for ~70% of cases per the cookbook PR's empirical estimate
2. **Second-line via PuLID-FaceNet reference image** — adds strong identity lock for one-shot named cast
3. **Third-line via per-character LoRA** — for named recurring cast (per `brand_lora_plans.yaml`); 32-rank character LoRAs train in ~10 min on H100 from 8 reference images, producing consistent identity across hundreds of panels
4. **QA harness as final gate** — pairwise face-distance metric flags any catalog drift before image commits

---

## §4 Implementation roadmap (this PR is research only — implementation is follow-up)

| Phase | Description | Effort | Gate |
|---|---|---|---|
| 1 | Implement `scripts/manga/character_individuation_solver.py` (200-400 LOC Python) | ~1 engineering day | Solver passes against the 22 stillness_press existing characters |
| 2 | Fill `character_design:` block for the 22 stillness_press series | ~5.5 hr (~15 min × 22) | Solver validates all 22 |
| 3 | Patch `runcomfy_batch.py::submit_inference` to read `character_design` block + emit per-axis prompt fragments | ~0.5 engineering day | Re-render the 22 with corrective spec |
| 4 | Empirical QA harness — `scripts/manga/face_distinctiveness_qa.py` using facenet-pytorch | ~1 engineering day | Threshold calibrated against operator-eyeballed distinctness |
| 5 | Backfill `character_design:` for the other 600+ catalog characters across all brands | ~150 hr at 15 min each — needs distribution across teacher-brand owners | Solver validates entire catalog |
| 6 | Train per-character LoRAs for the named cast in `brand_lora_plans.yaml` (12-14 LoRAs) | ~3-5 days compute + iteration | LoRA outputs pass QA harness |

**Cost-of-being-wrong reasoning:** the operator currently has 22 dashboard images each costing the operator-perception of "all the same person." The cost of pausing and implementing this pipeline is ~10 engineering days; the cost of NOT implementing and shipping 200+ series with the look-alike problem is catastrophic to brand differentiation.

---

## §5 Deferred items (follow-up PR)

The character-individuation literature-scan agent did not return in this PR's session. Items below need a focused follow-up PR:

1. **Mark Crilley character-design tutorial cross-reference** — the YouTube + Mastering Manga book series may have an explicit axis-vocabulary that supersedes or refines this PR's 12 axes
2. **Manga University textbooks** — same: cross-reference for axis-naming
3. **Stanchfield gesture/character framework** — applicability to manga
4. **ArcFace / DeepFace / CLIP empirical metric calibration** — what threshold values actually correspond to "operator says these are clearly different people"?
5. **Empirical model comparison** — fix prompt + 100 seeds across Animagine 4.0 / Qwen-Image / FLUX-schnell; measure pairwise face-distance via DeepFace; rank by attractor strength
6. **Open-source character-design generators** — does Character.ai-style design-axis system exist publicly? If yes, evaluate for fork
7. **Multi-controlnet face-landmark + body-pose + depth combination** — empirical test for Phoenix Omega's pipeline

---

## §6 NEXT_ACTION (post this PR)

1. Implement the constraint solver (Phase 1 above)
2. Fill the 22 stillness_press `character_design:` blocks
3. Re-render the 22 with corrective spec — smoke test
4. If smoke test passes, propagate to other 600+ catalog characters
5. Build the QA harness
6. Train named-cast LoRAs
7. Run the deferred literature-scan as its own focused PR

---

*End of CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md.*

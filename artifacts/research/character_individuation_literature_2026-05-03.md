# Character Individuation — Literature Synthesis (2026-05-03)

**Status:** AUTHORITY (new, this PR — research-only narrative companion).
**Branch:** `agent/character-individuation-lit-scan-20260503`
**Scope:** Synthesis narrative for the 4 questions PR-A closes — Q1 vocabulary depth, Q2 metric pick, Q3 workaround empirics, Q4 prompt-construction algorithm.

**Companion deliverables:**
- `config/manga/character_design_axes.yaml` — Q1 (axis_patterns block populated)
- `config/manga/character_individuation_metric.yaml` — Q2
- `artifacts/research/average_face_workaround_empirical_comparison_2026-05-03.md` — Q3
- `docs/CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md` — Q4

**Cross-references (SHA-pinned):**
- PR #838 commit `3d7118b33448ca42c9af67f3e1b7e5efbb1c5d11` — pipeline spec + 12-axis vocabulary scaffolding
- PR #802 commit `2881dd970bf2433e2225800ac6f73b1dd0281be5` — cookbook §2.3 weight-syntax responsiveness
- PR #803 commit `f4c50142b63df134d2f34c10a4a761bd9015c910` — commercial-clean stack (Qwen-Image / Animagine XL 4.0 / FLUX-schnell)

---

## §1 Why this PR exists

PR #838 shipped the character-individuation pipeline spec but flagged 4 deferred-stub questions because 1 of 7 agents stalled. PR-A closes those gaps:

- **Q1 (12-axis vocabulary depth)** — 5-8 named patterns per axis with mangaka exemplars + per-base token mappings. The 12 axes from PR #838 (face_shape, eye_geometry, nose_construction, mouth_jaw, hair, build, wardrobe_register, posture_default, age_signaling, skin_treatment, accessories, color_signal) had allowed values but no operationalized vocabulary. This PR adds the operationalization.

- **Q2 (individuation metric)** — Phoenix needs a single quantitative metric to determine whether two characters are visually distinguishable. PR #838's pipeline spec referenced facenet-pytorch generically; this PR locks in the metric, library, install path, and (proposed) operational thresholds.

- **Q3 (average-face attractor workaround empirics)** — PR #838 ranked the attractor problem qualitatively (Animagine strongest, Qwen weakest, FLUX-schnell mid). This PR adds empirical effectiveness/cost numbers across 8 workaround techniques and a per-brand-size recommendation matrix.

- **Q4 (12-axis → prompt-token construction algorithm)** — the "connective tissue" between a filled `character_design_template.yaml` and the actual generated prompts. This PR documents the algorithm + 3 worked examples (simple / cross-genre / collision-edge).

The operator's "smaller tasks, multiple steps" lesson from PR #838 was applied: 3 agents max in flight, 2 batches with mid-batch synthesis, ≤2 hr per agent.

---

## §2 Q1 — 12-axis vocabulary depth (headline findings)

### §2.1 Methodology note on token-mapping evidence

Of the three commercial-clean bases:

- **Animagine XL 4.0** is documented by its model card to require **Danbooru tag-based prompts**; "natural language input may not be effective" per the [HuggingFace card](https://huggingface.co/cagliostrolab/animagine-xl-4.0). The Danbooru tag groups for [hair styles](https://danbooru.donmai.us/wiki_pages/tag_group%3Ahair_styles), [eyes](https://danbooru.donmai.us/wiki_pages/tag_group%3Aeyes_tags), [attire](https://danbooru.donmai.us/wiki_pages/tag_group%3Aattire) are the load-bearing token vocabulary.

- **Qwen-Image** accepts natural-language phrases and renders them more literally than tag-trained anime models.

- **FLUX-schnell** sits between: parses natural language but front-loaded explicit feature descriptors are more reliable than buried ones.

### §2.2 9 of 12 axes well-cited; 3 marked `build_the_knowledge_gap`

Per the operator's stop-condition reframe (continue + tag, don't halt):

**Well-cited axes (5-8 patterns each):**
- `face_shape` — 8 patterns (Adachi-oval, Hara-square, Toriyama-round, Asano-heart-soft, CLAMP-elongated, Otomo-compact-realist, Inoue-Vagabond-angular-long, Yotsuba-Azuma-soft-round)
- `eye_geometry` — 7 patterns including the 2G_takeuchi_sparkle anti-pattern marker for josei
- `nose_construction` — 6 patterns (CLAMP-shojo-invisible, iyashikei-implied, Asano-Urasawa-seinen-drawn, Hara-Otomo-gekiga-prominent, Mizuki-memoir-realist, Inoue-Vagabond-chiseled)
- `mouth_jaw` — 7 patterns including 4D_bow_mouth_dated as deprecated for josei
- `hair` — 8 patterns including signature silhouettes (Toriyama-spike, Frieren-elf-twin-tail, Berserk-Guts-white-streak, Sailor-Moon-odango)
- `wardrobe_register` — 8 patterns spanning era + personality encoding
- `age_signaling` — 6 patterns including 9F_frieren_long_lived_elf
- `accessories` — 8 patterns (Tezuka-stitched-cape, Takeuchi-tiara-odango, Asano-Punpun-bird-glyph, etc.)
- `color_signal` — 8 patterns (mostly Qwen-Image natural-language; FLUX/Animagine partial coverage)

**Build-the-knowledge-gap axes:**
- `build` — diffusion bases poorly preserve build without explicit body tags + accessory/wardrobe reinforcement; all bases collapse undescribed builds to default-anime-slim
- `posture_default` — diffusion bases poorly preserve posture without ControlNet/OpenPose conditioning
- `skin_treatment` — most diffusion-base skin tokens trained on photoreal/color domains; stylized B&W manga preservation untested

For each gap-axis, the YAML now carries a `phoenix_internal_probe` recommendation (e.g., 100-seed comparison of `muscular`/`broad-shoulders`/`stocky`/`heavyset` across the 3 commercial-clean bases).

### §2.3 The `2G_takeuchi_sparkle` anti-pattern

Particularly useful finding from Q1: Animagine 4.0's default-girl attractor is essentially the Naoko Takeuchi sparkle register (`large round eyes, sparkling eyes, gradient eyes, long eyelashes, thick eyelashes, fake eyelashes`). Operator's 22 stillness_press dashboard PNGs collapse to this attractor. The Q1 vocabulary now flags this explicitly as **anti-pattern for josei market_demo**, used as a negative-prompt anchor in the Q4 algorithm.

---

## §3 Q2 — Individuation metric pick

### §3.1 Decision: DeepFace + FaceNet-512 (PRIMARY); CLIP ViT-B/32 (FALLBACK)

Three decision criteria evaluated:

**(a) Reliable on stylized manga faces** — limited public empirical data on stylized-domain face metrics. FaceNet-512 chosen because the same backbone is already adopted by the Phoenix stack via PuLID-FLUX-FaceNet (`lldacing/ComfyUI_PuLID_Flux_ll`), which carved it out as the commercial-clean alternative to InsightFace AntelopeV2.

**(b) Installable WITHOUT paid API** — FaceNet weights MIT-compatible (VGGFace2 license); DeepFace wrapper MIT.

**(c) Fast enough for 200+ catalog batch** — facenet-pytorch reports 12.97 FPS at 1080×1920 with GPU; DeepFace end-to-end is 4-6 FPS. 200-character × 10-image catalog = ~10 minutes single-GPU pass.

**ArcFace REJECTED as primary:** strongest reference implementation rides on InsightFace toolkit using AntelopeV2 (NC dependency per audit PR #803). DeepFace's Keras-InsightFace port keeps that obligation per the README.

### §3.2 Proposed thresholds (require empirical calibration)

| Distance band | Verdict | Action |
|---|---|---|
| `cosine_distance < 0.25` | Look-alike risk | REJECT — solver reruns on at least one locked axis |
| `0.25 ≤ distance < 0.40` | Borderline | WARN — flag for operator review |
| `distance ≥ 0.40` | Distinct enough | PASS |

**Empirical calibration scheduled for PR-C** (corrective-action smoke test on the 22 stillness_press dashboard PNGs).

### §3.3 Stylized-manga validity caveat

Public empirical literature on photoreal-trained backbones (FaceNet, ArcFace, VGG-Face) applied to stylized anime/manga faces is thin. Closest published work: [AniWho (arXiv 2208.11012)](https://arxiv.org/abs/2208.11012) reports 85.08% top-1 on EfficientNet-B7 for anime-character classification — but no head-to-head vs FaceNet/ArcFace/CLIP. **For stylized B&W manga, all candidate metrics need empirical calibration on Phoenix's own catalog before threshold values are trusted.**

---

## §4 Q3 — Average-face workaround empirics

### §4.1 Highest-leverage finding: PuLID-FLUX-FaceNet wins on face-similarity

Per [Apatero 2025 empirical comparison](https://apatero.com/blog/instantid-vs-pulid-vs-faceid-ultimate-face-swap-comparison-2025):
- **PuLID: 91% face recognition accuracy** (8.2-9.3/10 quality)
- InstantID: 84% (8.0-8.4/10)
- IP-Adapter FaceID: 79% (7.6-8.2/10)

[PuLID paper](https://arxiv.org/html/2404.16022v2) DivID-120: FaceSim **0.733**, CLIP-T 31.31, CLIP-I 0.812 — best-in-class.

**Catch:** PuLID-FLUX runs only on FLUX-schnell. SDXL/Animagine path uses IP-Adapter Plus (no InsightFace, commercial-clean) at FaceSim 0.619.

### §4.2 Per-brand-size recommendation matrix

```yaml
brand_size_10:
  primary: 12-axis prompt stack (covers ~70%)
  secondary: PuLID-FLUX-FaceNet on FLUX-schnell OR IP-Adapter Plus on Animagine
  qa_gate: per-character seed offset (reproducibility)
  total_setup_time: ~5 hours
  total_compute_cost_per_render: $0.10-$0.25 per scene

brand_size_50:
  primary: 12-axis prompt stack
  secondary: PuLID-FLUX-FaceNet for protagonist tier (~5 chars)
  tertiary: IP-Adapter Plus reference for supporting cast (~25 chars)
  qa_gate: FaceNet-512 distance metric
  total_setup_time: ~30-40 hours
  total_compute_cost_per_render: $0.75 per scene

brand_size_200:
  primary: 12-axis prompt stack
  secondary: ai-toolkit LoRA for top 20-40 recurring characters
  tertiary: PuLID-FLUX-FaceNet for one-off / mid-tier (next 80-100)
  quaternary: 12-axis + seed-offset alone for background cast (last 60-100)
  qa_gate: FaceNet-512 metric automated
  total_setup_time: ~160 hr engineering
  total_compute_cost_per_render: $2.40 per scene
```

**Why this combo:** 12-axis covers ~70% per cookbook §6.1; PuLID-FLUX-FaceNet handles the 30% tail; LoRA amortizes for high-recurrence characters (~$1.85 train cost beats $0.025 PuLID inference after ~75 generations).

### §4.3 Empirical model comparison gap (deferred to PR-D)

No published benchmark directly measures attractor strength on Animagine 4.0 vs Qwen-Image vs FLUX-schnell. Q3 file documents a Phoenix-internal A/B framework: 10 prompts × 100 seeds × 3 models = 3000 renders, FaceNet-512 cosine distance metric, ~$5-15 cost on RunComfy/Replicate, 30 min wall-clock on 8× H100. **One-day engineering sprint** for PR-D.

---

## §5 Q4 — Prompt-construction algorithm (highlights)

Full spec in `docs/CHARACTER_INDIVIDUATION_PROMPT_ALGORITHM_2026-05-03.md`. Headline findings:

### §5.1 Token-budget empirics confirmed for all 3 bases

- **FLUX-schnell:** CLIP-L 77 (~30 tokens for character signal at front), T5-XXL 256 (~150 tokens for full prose). Important: CLIP-L gets compressed signal, T5 gets full description — feeding both the same prompt drops domain knowledge 50-75%.
- **Qwen-Image:** ~1000 tokens, no squeeze. Prose-emphasis ("dramatically", "strongly") functions as soft weights since SD `(token:1.3)` syntax is inert.
- **Animagine XL 4.0:** With `lpw_stable_diffusion_xl` pipeline, unlimited via 75-token chunks. Quality tags MUST be at END (Animagine quirk).

### §5.2 7 of 12 axes go in positive prompt; 1 negative-only; 4 solver-only

Routing summary:
- **Positive:** face_shape, eye_geometry, hair, wardrobe_register, age_signaling, accessories, color_signal
- **Negative:** mouth_jaw (forbidden patterns expressed as negation)
- **Solver-only:** nose_construction, skin_treatment, posture_default, build (these inform collision detection but rarely tokenize)

### §5.3 Constraint solver fallback chain

```
ITERATION 1-3 (author): operator edits colliding axis. Re-run.
ITERATION 4 (auto): rotate lowest-leverage colliding axis (nose_construction → build → posture_default → mouth_jaw.lip_shape)
ITERATION 5 (auto): rotate accessories.signature_item to catalog-novel value
ESCALATION: catalog axis-vocabulary saturation → operator review
```

Decision logging to `artifacts/character_solver/<series_id>/iterations.jsonl`.

---

## §6 Implementation roadmap (post-PR-A)

| Phase | Description | Effort | Gate |
|---|---|---|---|
| 1 | `scripts/manga/character_individuation_solver.py` (Python; ~400 LOC) | ~1.5 day | Solver passes against the 22 stillness_press characters |
| 2 | `scripts/manga/character_prompt_builder.py` (~300 LOC) | ~1 day | Per-base prompts emit cleanly |
| 3 | `scripts/manga/character_design_validator.py` (~200 LOC) | ~0.5 day | Pre-solver validation catches forbidden_combinations |
| 4 | Empirical FaceNet-512 threshold calibration on 22 dashboard PNGs (PR-C) | ~0.5 day | Calibrated thresholds replace proposed defaults |
| 5 | Phoenix-internal A/B framework for attractor model comparison (PR-D) | ~1 day | Single calibrated `attractor_strength_score ∈ [0,1]` per base |

**Total engineering effort:** ~4.5 days. All out of scope for this research PR; queued as engineering follow-ups gated on the operator's PR review.

---

## §7 NEXT_ACTION (post this PR)

1. Operator review of Q2 metric thresholds (proposed; require calibration in PR-C)
2. Operator decides whether to schedule PR-D (empirical model attractor comparison) before or after PR-C
3. Engineering follow-up PR implements the constraint solver (~1.5 day)
4. PR-C corrective-action smoke test consumes both PR-A's metric YAML + PR-A's algorithm spec
5. The 3 `build_the_knowledge_gap` axes (build, posture, skin_treatment) get Phoenix-internal probes — separate engineering PR

---

## §8 Resource tally across PR-A

| Leg | WebFetch used | Budget | Status |
|---|---|---|---|
| Leg 1 (Q1 + Q2) | 9 | 20 | 45% — well under |
| Leg 2 (Q3) | 4 | 17 | 24% — well under |
| Leg 3 (Q4) | 4 | 8 | 50% — under |
| **Total** | **17** | **45** + 5 main-thread reserve = 50 | **34%** |

No stop conditions triggered. Stylized-manga literature gaps tagged as `build_the_knowledge_gap` per operator's reframe — no halt needed.

---

*End of character_individuation_literature_2026-05-03.md.*

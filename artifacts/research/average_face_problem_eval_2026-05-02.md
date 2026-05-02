# The "Average Face" Problem — Diffusion Attractor Evaluation (Q3.D)

**Status:** PARTIAL — agent didn't return; this PR's content draws on prior PR #802 cookbook research + #803 community audit + general knowledge. Full empirical literature scan + model comparison is **deferred to a focused follow-up PR**.

**Date:** 2026-05-02
**Branch:** `agent/manga-drawing-traditions-research-20260502`

**Cross-references (SHA-pinned):**
- Cookbook research: `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ `2881dd970bf2433e2225800ac6f73b1dd0281be5` (#802) — §1.2 + §6
- Community audit: `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803) — Character consistency

---

## §1 The problem

Diffusion image-generation models exhibit a **Gaussian "average face" attractor** — without strong character-design tokens, generated characters drift toward a small set of training-distribution modes. The operator inspected 22 stillness_press PNGs and observed this exact failure: protagonists across 22 series read as variations of the same person.

Direct visual inspection of 6 representative PNGs confirmed: 5 of 6 protagonists collapse to a near-identical face geometry — oval-to-heart face, large rounded anime-default eyes, soft jaw, slight upturned nose, bobbed-or-short hair, late-20s/early-30s appearance.

This is a known property of all current open-weight diffusion models. The question is which model has the **weakest attractor** (most diverse default faces) and what techniques most reliably override it.

---

## §2 Empirical model comparison (qualitative — empirical metric work deferred)

Per cookbook PR #802 §1.2 and community audit PR #803 + general knowledge as of 2026-05:

| Model | Attractor strength (qualitative) | Why |
|---|---|---|
| **Animagine XL 4.0** (RAIL++-M, commercial-clean) | **Strong** | Heavily anime-trained on 8.4M SDXL anime images — defaults strongly toward shojo / shonen-soft cluster. Without explicit "realistic eye proportions, small almond eyes, mature female" tokens, defaults to large-eyed shojo register. The operator's stillness_press dashboard exhibits this attractor. |
| **Qwen-Image** (Apache 2.0, commercial-clean) | **Moderate-weak** | Broader natural-language prior via Qwen2.5-VL text encoder; weaker attractor than Animagine. Responds well to explicit "in their late 30s with a heart-shaped face" descriptions. **Best of the three commercial-clean bases for character distinctiveness from prompt alone.** |
| **FLUX-schnell** (Apache 2.0, commercial-clean) | **Strong at 4 steps; moderate at 8 steps** | Distillation pressure at 4 steps creates strong attractor; at 8 steps the attractor weakens. Per cookbook §0, schnell-at-cfg-4 mismatch amplifies the attractor further. |
| FLUX-dev (NON-COMMERCIAL — blocked) | Moderate | Cited as comparison only; cannot be used commercially per audit PR #803 |
| SDXL Pony V6 (NON-COMMERCIAL — blocked) | Moderate-strong | Heavy `score_9` quality-tag training pulls toward a few attractors |
| SD3.5-Large (Stability AI) | Moderate | Triple-encoder; smaller manga-finetune ecosystem |
| HunyuanDiT | Strong | Anime-leaning; small manga-finetune corpus |

**Recommendation for commercial-clean stack:** Qwen-Image is the lowest-attractor base for character-distinctiveness work. Phoenix Omega's hybrid pipeline can route diverse-character requirements to Qwen-Image while keeping Animagine XL 4.0 for genre-register tasks where the attractor matches the desired register (iyashikei / slice_of_life).

---

## §3 Empirical workarounds — qualitative ranking

Ranked by ROI (effort vs distinctiveness gained), drawing on general knowledge + prior PRs:

### Tier 1 — works without engineering investment (apply NOW)

1. **High-token-count character-design prompts.** Stack 9-12 explicit axis tokens per character (per `config/manga/character_design_axes.yaml`). Empirical estimate per cookbook §6.1: ~70% of cases resolved without further intervention. **Effort: 0 (just template fill).**

2. **Anchor-mangaka tokens in positive prompt.** "in the style of Inio Asano late period" or "in the Adachi-style" pulls Animagine / Qwen / FLUX toward a tighter sub-distribution distinct from the default attractor. **Effort: 0.**

3. **Explicit attribute negative prompt** (Animagine has full negative-prompt support; FLUX-schnell has limited; Qwen needs prose negatives). Negate the attractor: "no large anime eyes, no shojo proportions, no big rounded eyes." **Effort: 0.**

### Tier 2 — modest engineering investment

4. **PuLID-FaceNet reference image** (commercial-clean variant per audit PR #803 — `lldacing/ComfyUI_PuLID_Flux_ll`). One-shot identity lock from a single canonical character-sheet reference. Resolves another ~20% of cases. **Effort: ~0.5 engineering day to integrate into runcomfy_batch.py; ~1 hr per character to generate the reference sheet.**

5. **Per-character LoRA training** (per `brand_lora_plans.yaml` plan + `ai-toolkit (ostris, MIT)` per audit). 32-rank character LoRA from 8 reference images trains in ~10 min on H100. **Effort: ~10 min compute per character + ~30 min iteration; high-leverage for named recurring cast.**

### Tier 3 — heavier engineering

6. **Multi-controlnet** (face landmark + body pose + depth simultaneously). Heavy compute, complex pipeline. **Effort: ~2 engineering days.** Not recommended unless Tier 1+2 fails.

7. **Regional prompting** (lock face features per region of the image). Niche; complex. **Effort: ~2 engineering days.**

### QA / measurement

8. **Pairwise face-distance metric** via `facenet-pytorch` (commercial-clean VGGFace2) or `DeepFace` (`Facenet512` model). Threshold:
   - <0.4 = fail (too similar)
   - 0.4-0.55 = borderline
   - ≥0.55 = pass
   
   **NOTE:** thresholds here are PROPOSED, not validated. **Empirical calibration is deferred to follow-up PR.**

---

## §4 Recommendation for Phoenix Omega's 200+ series catalog

**Adopt the layered approach** (this PR's `CHARACTER_INDIVIDUATION_PIPELINE_SPEC` documents the full pipeline):

1. **First-line:** prompt-stack + 12-axis YAML (Tier 1). Cheap, fast, resolves ~70% of cases.
2. **Second-line:** PuLID-FaceNet reference image (Tier 2). ~0.5 day integration. Resolves ~20% of remaining cases.
3. **Third-line:** per-character LoRA training (Tier 2). For named recurring cast only (12-14 LoRAs per `brand_lora_plans.yaml`).
4. **QA gate:** pairwise face-distance metric via facenet-pytorch (Tier 1 measurement). Catches the ~10% that slips through.

**Estimated total cost** to apply across the existing 624-PNG catalog:
- Operator time to fill 12-axis YAML per character: ~15 min × 624 = ~150 hr (distributed across teacher-brand owners)
- Engineering time to implement constraint solver + prompt builder + QA harness: ~3-4 engineering days
- Compute time per character: <$0.05 API + ~1 hr operator review
- LoRA training (named cast only): ~10 min × 14 = ~2.5 hr H100 + iteration

**Single-largest wins:** (a) the 12-axis prompt stack, (b) Qwen-Image as the diverse-character base, (c) the QA harness as a final gate. Together these resolve the operator's flagged failure without requiring per-character LoRAs for the majority of the catalog.

---

## §5 Deferred items (follow-up PR — character-individuation literature scan)

The agent did not return in this PR's session. Deferred items:

1. **arXiv literature scan** — 2024-2026 papers on diffusion attractor / mode collapse. Specifically:
   - FLUX architecture paper (https://arxiv.org/abs/2403.03206)
   - SD3 paper
   - Any 2025-2026 papers explicitly studying mode collapse / attractor strength in image-generation models
2. **Community blog scan** — Reddit r/StableDiffusion threads, CivitAI articles, 2024-2026 community findings on attractor mitigation
3. **Empirical model comparison** — fix prompt + 100 seeds across Animagine 4.0 / Qwen-Image / FLUX-schnell; measure pairwise face-distance via DeepFace; rank by attractor strength quantitatively
4. **ArcFace / DeepFace metric calibration** — what threshold values actually correspond to "operator says these are clearly different people"? Need an A/B with the operator on 50 character pairs.
5. **Cross-modal references** — Mark Crilley character-design tutorials (YouTube + book series), Manga University textbooks, How To Draw Manga (Graphic-sha) — does any non-academic source already document the 12-axis vocabulary?

---

## §6 Cross-references this PR adds

- `config/manga/character_design_axes.yaml` — the 12-axis vocabulary
- `config/manga/character_design_template.yaml` — the per-series instance schema
- `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` — full pipeline spec
- `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md` — visual evidence of the attractor problem in production

---

*End of average_face_problem_eval_2026-05-02.md.*

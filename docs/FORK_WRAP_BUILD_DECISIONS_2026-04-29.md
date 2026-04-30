# Fork / Wrap / Build Decisions — Phoenix Omega Manga Image Generation (Phase 1)

**Date:** 2026-04-29
**Phase:** 1 of 2
**Companion:** [community_assets_audit_2026-04-29.yaml](../config/manga/community_assets_audit_2026-04-29.yaml) · [COMMUNITY_ASSETS_AUDIT.md](COMMUNITY_ASSETS_AUDIT_2026-04-29.md) · [integration_effort_estimates](../artifacts/research/integration_effort_estimates_2026-04-29.md)

**Convention:**
- **Fork** = use the public asset directly (or with minor patches), import into Phoenix's tree.
- **Wrap** = use the public asset as-is via API/CLI, no fork; Phoenix-side wrapper code only.
- **Build** = no public asset adequate; Phoenix builds in-house.

License tier on every recommendation: 🟢 commercial-clean / 🟡 commercial-conditional / 🔴 non-commercial-blocked.

---

## Phase 1 decisions

### 1. Base diffusion model — **FORK** (Qwen-Image primary, Animagine 4.0 secondary)

| Path | Call | Tier | Effort |
|---|---|---|---|
| Migrate primary base to **Qwen-Image** ([github.com/QwenLM/Qwen-Image](https://github.com/QwenLM/Qwen-Image)) | **Fork** | 🟢 (Apache 2.0) | 2–3 days for ComfyUI integration + LoRA retrain pilot |
| Add **Animagine XL 4.0** ([HF cagliostrolab/animagine-xl-4.0](https://huggingface.co/cagliostrolab/animagine-xl-4.0)) as secondary | **Fork** | 🟢 (RAIL++-M) | 1 day workflow swap |
| Migrate from **FLUX.1-dev** for training | **Build** (configuration-only — switch trainer base) | 🔴 → 🟢 | 0.5 days config edit |

**Rationale.** Three 🟢 base models exist; Phoenix should run two (Qwen primary for ja/zh/ko locales + speech bubbles, Animagine secondary for SDXL ecosystem coverage). FLUX-dev must be retired from training due to the non-commercial license inheritance.

**License risk if any:** Qwen-Image individual LoRAs on ModelScope are 🟡 — verify per-LoRA before bundling. Animagine RAIL++-M restricts certain illegal/harmful uses; Phoenix's catalog doesn't trip these.

---

### 2. Character consistency — **HYBRID FORK + BUILD**

| Path | Call | Tier | Effort |
|---|---|---|---|
| Train protagonist LoRAs for named cast (already planned in `brand_lora_plans.yaml`) | **Build** (training pipeline forked from ai-toolkit) | 🟢 | ~30 min/character on H100 |
| Add PuLID-FLUX with FaceNet loader for one-shot characters | **Fork** ([lldacing/ComfyUI_PuLID_Flux_ll](https://github.com/lldacing/ComfyUI_PuLID_Flux_ll)) | 🟢 | 1 day to install custom nodes + edit workflow JSON |
| InstantID / IP-Adapter FaceID | **Skip** | 🔴 (InsightFace dep) | n/a |

**Rationale.** Phoenix is already on the build path for protagonist LoRAs (correct call). The fork is the additive PuLID layer for ephemeral characters that don't justify a training run. Combined coverage = both named cast and incidentals.

**License risk if any:** PuLID-FLUX on the FaceNet path is fully Apache 2.0; ensure the custom-node install does not pull AntelopeV2 by default.

---

### 3. Per-genre LoRAs — **HYBRID per genre**

| Genre | Call | Tier | Effort |
|---|---|---|---|
| mecha | **Fork-test then Build if needed** — try Super Robot Diffusion XL on Animagine 4.0; if degraded, train a Phoenix mecha LoRA on Animagine ([Civitai 124747](https://civitai.com/models/124747)) | 🟡 (verify Civitai flags) | 0.5 day test; 1 day train if needed |
| dark_fantasy | **Fork** — DARK FANTASY XL v1.1 ([Civitai 1223108](https://civitai.com/models/1223108/dark-fantasy-xl)) | 🟡 | 0.5 day install + smoke test |
| fantasy_adventure | **Wrap** — Animagine 4.0 base alone covers the register | 🟢 | 0 days additional |
| healing (control) | **Wrap** — Animagine 4.0 base alone covers it | 🟢 | 0 days additional (already working) |

**Rationale.** The Phase 1 control-genre finding is decisive: well-covered registers don't need LoRAs. The 21 deferred-Phase-2 genres should be triaged by the same lens — if Animagine/Qwen-Image cover the register out of the box, no LoRA is the answer.

**License risk if any:** the recommended fork-targets all require per-page Civitai license-flag verification (the 6 commercial flags). The roster artifact ([community_lora_roster_2026-04-29.yaml](../artifacts/research/community_lora_roster_2026-04-29.yaml)) flags this for engineering follow-up.

---

### 4. ComfyUI workflows — **FORK**

| Workflow | Call | Tier | Effort |
|---|---|---|---|
| Single-character portrait — fork **Mickmumpitz Flux Consistent Characters** | **Fork** | 🟡 | 1 day — JSON edit + custom-node install |
| Multi-character — fork **PuLID Flux II RunComfy template** with FaceNet loader swap | **Fork** | 🟢 (after swap) | 1 day |
| Anime-specific — fork **PuLID + OpenPose + DeepSeek-Janus** ([comfyui.org](https://comfyui.org/en/unlock-anime-style-characters-with-ai)) | **Fork** | 🟡 | 1–2 days |
| Character sheet grid (for LoRA training reference image generation) — fork **Consistent Character Creator 3.0** | **Fork** | 🟡 | 1 day |
| `Manga Editor Desu!` — JP orchestration tool | **Evaluate-fork in Phase 2** ([Qiita](https://qiita.com/kerimeka/items/d3cf8b338c742bc96a89)) | 🟡 | 0.5 day eval; 3–5 days deep fork if pursued |

Replace the current bare 7-node `flux_character_portrait_template.json` with the fork. The audit's PNG inspection found the bare workflow is the structural cause of register oscillation — character consistency is absent and the schnell-at-dev settings produce drift.

**License risk if any:** RunComfy ToS applies to RunComfy-hosted workflow JSON downloads. The underlying node packs are all Apache/MIT.

---

### 5. ComfyUI custom nodes — **FORK (required + recommended)**

| Pack | Call | Tier |
|---|---|---|
| ComfyUI-Manager (required) | Fork | 🟡 (GPL-3.0 — runtime use OK; bundling requires care) |
| `lldacing/ComfyUI_PuLID_Flux_ll` (required for FLUX path) | Fork | 🟢 (FaceNet path) |
| `cubiq/PuLID_ComfyUI` (required for SDXL/Animagine path) | Fork | 🟢 (verify FaceNet path) |
| ComfyUI_LayerStyle (HalfTone) | Fork | 🟢 (MIT) |
| sketch2manga | Fork | 🟡 (license not_listed) |
| ComfyUI-Img2DrawingAssistants | Fork | 🟡 |
| ComfyUI_Fill-Nodes | Fork | 🟡 |
| ComfyUI-IPAdapter-Plus FaceID | **Skip** | 🔴 |

---

### 6. LoRA training tools — **FORK**

| Tool | Call | Tier |
|---|---|---|
| **ai-toolkit (ostris)** — primary | Fork | 🟢 (MIT) |
| **kohya_ss** — co-primary | Fork | 🟢 (Apache-2.0) |
| FluxGym — onboarding | Fork | 🟢 (MIT) |
| SimpleTuner | Skip unless materially needed | 🟡 (AGPL-3.0 contamination on distribution) |
| OneTrainer | Skip | 🟡 (AGPL-3.0; no FLUX advantage over Kohya) |

**Rationale.** The Phoenix-trained LoRAs (62 in `brand_lora_plans.yaml`) need a license-clean training pipeline. ai-toolkit + kohya are MIT/Apache. The AGPL alternatives provide no Phoenix-relevant capability the primary pair lacks.

**AGPL trade-off explicitly documented:** if Phoenix's training-driver wrapper code imports SimpleTuner or OneTrainer and Phoenix later distributes that wrapper externally (e.g. as part of an open-source release or partner integration), the wrapper code inherits AGPL — must be open-sourced. Internal-only use is fine. The decision is the operator's; the recommendation is to avoid AGPL unless a specific feature requires it (none currently identified).

---

### 7. JP/CN-specific surfaces — **MIXED**

| Surface | Call | Notes |
|---|---|---|
| Qwen-Image base | **Fork** (already in §1) | 🟢 |
| Qwen-Image-i2L (one-image-to-LoRA) | **Evaluate** (validate claim with in-house bench before committing) | 🟢 if real |
| ColorManga / Multiple-Angles-LoRA on ModelScope | **Fork after license verify** | 🟡 |
| `Manga Editor Desu!` (NegiTurkey) | **Evaluate-fork in Phase 2** | 🟡 |
| Zenn `qikta` corporate-deployment workflow | **Fork pattern** (not the OpenAI step) | 🟢 |
| Catapp-Art3D note.com paid templates | **Buy-and-evaluate** (¥1000/mo) | 🟡 |
| `animeoutlineV4` Anime Lineart LoRA (recurring across JP/CN tutorials) | **Fork** as Phoenix baseline lineart helper | 🟡 (verify) |
| Rakuten AI Studio | **Stop watching** | not a manga surface |

---

## Phase 2 dimensions — pending decisions

The following Phase 1 dimensions are deferred. Decisions are NOT made until operator approves Phase 2 scope:

- `prompt_libraries_and_cookbooks` — likely **fork** (Danbooru tag wiki + JP `老漫画_Monochrome manga` cookbook + Catapp-Art3D)
- `datasets_for_finetuning_or_reference` — likely **build** (Manga109 academic-only; commercial alternatives sparse)
- `post_processing_and_lineart_cleanup` — likely **fork** (LayerStyle + sketch2manga combo)
- `qa_and_drift_detection` — likely **build** with **fork** of `WD-EVA02-large-tagger-v3` (SmilingWolf, HF)
- `panel_layout_and_speech_balloons` — likely **build** (Phoenix-specific composition; partial fork of ControlNet+Latent Couple patterns)
- `orchestration_and_batch` — **fork-or-keep** decision (deep diff vs `Manga Editor Desu!`)
- remaining 21 genres in `manga_style_loras_per_genre` — likely **wrap** for genres covered by the base, **fork** for outliers (period-specific, very-stylized)

---

## Summary table

| Dimension | Headline call | Tier of recommendation |
|---|---|---|
| Base model | Fork Qwen-Image + Animagine 4.0 | 🟢 |
| Character consistency | Fork PuLID (FaceNet) + Build LoRAs | 🟢 |
| Mecha LoRA | Fork-test then Build if needed | 🟡→🟢 |
| Dark-fantasy LoRA | Fork | 🟡 |
| Fantasy-adventure | Wrap (no LoRA) | 🟢 |
| Healing (control) | Wrap (no LoRA) | 🟢 |
| ComfyUI workflows | Fork | 🟢 (after FaceNet swap) |
| Custom nodes | Fork required + recommended | 🟢 |
| LoRA training | Fork ai-toolkit + kohya | 🟢 |
| JP/CN base layer | Fork Qwen-Image | 🟢 |
| JP/CN orchestration | Evaluate-fork (Phase 2) | 🟡 |

**Net Phase 1 verdict: ~70% fork / ~10% wrap / ~20% build.** Phoenix is rebuilding less than the operator suspected at the asset level — the public ecosystem covers most of what Phoenix needs. The build effort that *does* remain (proprietary character/brand LoRAs, mecha LoRA, QA harness) is the right place for Phoenix-specific investment.

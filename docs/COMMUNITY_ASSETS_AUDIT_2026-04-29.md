# Community Assets Audit — Phoenix Omega Manga Image Generation (Phase 1)

**Date:** 2026-04-29
**Phase:** 1 of 2 (operator-approved phased run)
**Branch:** `claude/hopeful-heyrovsky-fa644c`
**Canonical YAML:** [config/manga/community_assets_audit_2026-04-29.yaml](../config/manga/community_assets_audit_2026-04-29.yaml)
**Companion artifacts:** [community_lora_roster](../artifacts/research/community_lora_roster_2026-04-29.yaml) · [comfyui_workflow_audit](../artifacts/research/comfyui_workflow_audit_2026-04-29.md) · [jp_cn_specific_finds](../artifacts/research/jp_cn_specific_finds_2026-04-29.md) · [license_risk_register](../artifacts/research/license_risk_register_2026-04-29.md) · [integration_effort_estimates](../artifacts/research/integration_effort_estimates_2026-04-29.md) · [fork_wrap_build_decisions](FORK_WRAP_BUILD_DECISIONS_2026-04-29.md)

---

## Executive summary

The audit's central question — *"is Phoenix reinventing the wheel for manga image generation?"* — answers **partially yes, mostly no, but for the wrong reasons**. The pieces Phoenix is rebuilding (orchestration, batch infrastructure, brand/character LoRAs) are not where the cheap forks live. The pieces Phoenix is *not* doing (commercial-license discipline on the base model, CJK speech-bubble rendering, character-consistency tooling, per-genre style LoRAs for the failing genres) are where the public ecosystem has shipped solutions Phoenix should adopt.

### Top 5 forks worth doing now (Phase 1 ranked)

1. **Migrate base model off FLUX.1-dev to Qwen-Image (Apache 2.0) primary or Animagine XL 4.0 (RAIL++-M) secondary.** Phoenix's `brand_lora_plans.yaml` declares FLUX.1-dev as the LoRA training base — this is non-commercial, and every Phoenix LoRA trained on it inherits the restriction. The inference workflow uses `flux1-schnell-fp8` (Apache 2.0, fine), but at 24 steps cfg 4.0, which are Dev settings — Schnell is spec'd for 4 steps cfg 1.0. Migrating resolves the licensing ambiguity and the workflow drift in one move. ([Effort: 1–3 days for base swap + LoRA retrain.](../artifacts/research/integration_effort_estimates_2026-04-29.md))

2. **Fork PuLID-FLUX with the FaceNet loader path (`lldacing/ComfyUI_PuLID_Flux_ll`).** Phoenix's current 7-node workflow has no character-consistency tooling at all. Adding PuLID gives one-shot character lock for ephemeral cast members; combined with Phoenix's already-planned protagonist LoRAs this covers both named cast and incidentals. The FaceNet loader avoids the InsightFace AntelopeV2 non-commercial dependency that disqualifies InstantID for Phoenix. ([Apache 2.0 all the way down.](https://github.com/lldacing/ComfyUI_PuLID_Flux_ll))

3. **Fork the JP `Manga Editor Desu!` orchestration tool (NegiTurkey, Qiita 2024+).** This is the asset Phoenix is most directly competing against — a JP OSS tool that orchestrates ComfyUI/Forge/WebUI APIs for end-to-end manga page generation, featured on Gigazine. Surfaced by the [JP/CN subagent](../artifacts/research/jp_cn_specific_finds_2026-04-29.md). Phoenix should evaluate forking the orchestration layer rather than rebuilding it; the differentiation should come from catalog scale, brand voice, and EI-character-author authoring, not from re-implementing the local-ComfyUI control plane.

4. **Fork the JP corporate-deployment workflow (Zenn `qikta`, 2024-10).** End-to-end pipeline: prose → `himawarimix` checkpoint + `animeoutlineV4` LoRA → CLIP STUDIO assembly. The `Anime Lineart Style LoRA` family recurs across every JP/CN tutorial — strong signal Phoenix should pin `animeoutlineV4` as a baseline lineart LoRA layered on whatever base model wins.

5. **Fork `ai-toolkit` (ostris, MIT) as the LoRA training pipeline.** It supports FLUX-schnell native training (`train_lora_flux_schnell_24gb.yaml`), SDXL/Animagine, and multi-aspect-ratio bucket training — eliminating the FLUX-dev licensing inheritance. MIT-licensed so no contamination concerns for Phoenix's wrapper code. SimpleTuner and OneTrainer are AGPL — surface as alternatives but recommend against unless materially needed.

### Top 3 builds Phoenix can't avoid

1. **Phoenix-proprietary character/style LoRAs for the named brand cast.** All 12 character + 12 brand-style + 14 protagonist LoRAs in `brand_lora_plans.yaml` are Phoenix-specific and cannot map to any community asset. The fork-not-build call here is the *training pipeline* (use `ai-toolkit`), not the LoRAs themselves.

2. **Phoenix mecha LoRA (or an Animagine-native variant).** All comprehensive mecha LoRAs in the public ecosystem (Super Robot Diffusion XL, Gundam-specific) are built on Illustrious-XL or Pony — both commercial-blocked. Phoenix needs to either (a) cross-test Super Robot Diffusion XL on Animagine 4.0 (also SDXL — should partially transfer) and accept quality variance, or (b) train an Animagine-native mecha LoRA. Phase 2 should do the cross-test before committing to (b).

3. **Phoenix QA harness wired to the cookbook PR.** The audit found `WD-EVA02-large-tagger-v3` (SmilingWolf) as the de-facto manga reverse-prompt tagger, and Qwen-VL is *not* yet validated on manga (no public benchmark vs WD-EVA02). The QA layer that connects tagger → cookbook → drift-detection is Phoenix-specific. Phase 2 dimension `qa_and_drift_detection` will detail this.

### License-risk headline

Phoenix Omega ships commercial product. The audit's most urgent finding is the [FLUX.1-dev license inheritance issue](../artifacts/research/license_risk_register_2026-04-29.md). Of the 6 candidate base models surveyed, only **Qwen-Image, FLUX-schnell, and Animagine XL 4.0** are 🟢 commercial-clean. Pony V6, NoobAI, Illustrious-XL, and FLUX-dev are all 🔴 for Phoenix. The community LoRA ecosystem is heavily concentrated on Illustrious/Pony (especially mecha) — meaning even where the LoRA file's own license is permissive, the base model contamination blocks commercial deployment. This narrows Phoenix's per-genre LoRA options significantly.

---

## Per-dimension findings (Phase 1)

### Base diffusion model

Six candidates surveyed. Only three commercial-clean for Phoenix:

| Model | License | Tier | Notes |
|---|---|---|---|
| **Qwen-Image (Alibaba, 2026)** | Apache 2.0 | 🟢 | First-class CJK text for speech bubbles; ModelScope LoRA pack; one-image-to-LoRA via `Qwen-Image-i2L`. **Primary recommendation.** |
| **Animagine XL 4.0** (Cagliostro) | CreativeML Open RAIL++-M | 🟢 | SDXL fine-tune trained on 8.4M anime images. Native Danbooru tag prompting. **Secondary recommendation.** |
| **FLUX.1-schnell** (BFL) | Apache 2.0 | 🟢 | Distilled — needs heavy LoRA stack for manga register. Phoenix's current path; keep as fallback. |
| FLUX.1-dev | Non-Commercial v2.0 | 🔴 | Phoenix's `brand_lora_plans.yaml` lists this as training base. **License violation** for any commercial output. Must migrate. |
| Pony Diffusion V6 XL | Modified Fair AI 1.0-SD | 🔴 | Commercial inference requires explicit creator permission. |
| NoobAI XL | Restrictive | 🔴 | Prohibits commercialization of model outputs and derivatives. |
| Illustrious-XL | Output-restricted | 🔴 | Generated images not commercial-OK if not edited. |

**Decision:** primary = Qwen-Image (esp. given Phoenix's ja_JP/zh_TW/zh_CN/ko_KR locale lanes); secondary = Animagine XL 4.0 for genres where Qwen's register is weaker; FLUX-schnell as legacy fallback while migration is in flight.

### Character consistency

Five candidates. Two commercial-clean for Phoenix:

| Tool | License | Tier | Notes |
|---|---|---|---|
| **PuLID-FLUX (FaceNet path)** | Apache 2.0 (PuLID + node) + facenet-pytorch (commercial-clean VGGFace2) | 🟢 | Use `lldacing/ComfyUI_PuLID_Flux_ll`'s `PulidFluxFaceNetLoader`. Multi-character supported. |
| **LoRA-per-character** | depends on trainer (ai-toolkit MIT, kohya Apache) | 🟢 | Phoenix's already-planned path; right call for named cast. |
| InstantID | Apache code + InsightFace AntelopeV2 (NC) | 🔴 | Highest face-similarity score but blocked by InsightFace dependency. |
| IP-Adapter FaceID | InsightFace dep | 🔴 | Same issue. |
| PuLID-FLUX (default InsightFace path) | Apache code + AntelopeV2 (NC) | 🟡 | Use FaceNet variant instead. |

**Decision:** hybrid — train LoRA-per-protagonist for the named cast (already in `brand_lora_plans.yaml`); use PuLID-FLUX-FaceNet for one-shots.

### Per-genre LoRAs (4 genres deep — Phase 1)

| Genre | Pick | Tier | Action |
|---|---|---|---|
| **mecha** | Super Robot Diffusion XL ([Civitai 124747](https://civitai.com/models/124747)) | 🟡 (Illustrious base) | Fork-test on Animagine 4.0; if degraded, build Phoenix mecha LoRA. |
| **dark_fantasy** | DARK FANTASY XL v1.1 ([Civitai 1223108](https://civitai.com/models/1223108/dark-fantasy-xl)) | 🟡 (verify Civitai flags) | Fork. |
| **fantasy_adventure** | Animagine XL 4.0 base, no LoRA | 🟢 | Wrap (no LoRA needed; base covers register). |
| **healing (control)** | Animagine XL 4.0 base, no LoRA | 🟢 | Wrap. Confirms thesis: well-covered genres don't need LoRAs. |

**Implicit finding:** the "per-genre LoRA roster" reflex is over-engineering for genres in the base model's training density. The genres that *do* need a LoRA are those outside the anime base model's default register — mecha, dark fantasy, very-specific period art — not the bread-and-butter slice-of-life / romance / school / comedy genres that Animagine and Qwen-Image already cover.

### ComfyUI workflows + custom nodes

Five public workflows audited (full audit at [comfyui_workflow_audit_2026-04-29.md](../artifacts/research/comfyui_workflow_audit_2026-04-29.md)). Phoenix's current 7-node template is bare; the nearest fork target is the **anime-style consistent character workflow** (PuLID + OpenPose + DeepSeek-Janus, comfyui.org). Custom nodes: required = ComfyUI-Manager + `lldacing/ComfyUI_PuLID_Flux_ll` + `cubiq/PuLID_ComfyUI` (for SDXL/Animagine path). Recommended = ComfyUI_LayerStyle (halftone), sketch2manga (screentone via diffusion).

### LoRA training tools

| Tool | License | Tier | Verdict |
|---|---|---|---|
| **ai-toolkit (ostris)** | MIT | 🟢 | **Primary.** FLUX-schnell + SDXL/Animagine native. Multi-aspect-ratio bucket training. |
| **kohya_ss / sd-scripts** | Apache 2.0 | 🟢 | Co-primary. Industry standard, deeper config surface. |
| FluxGym (Kohya wrapper) | MIT | 🟢 | Onboarding tool; schnell support is "suboptimal" per repo. |
| SimpleTuner | AGPL-3.0 | 🟡 | Avoid unless materially needed — wrapper inherits AGPL on distribution. |
| OneTrainer | AGPL-3.0 | 🟡 | Same. Furkan's bench: "no benefit over Kohya for FLUX." |

### JP/CN-specific finds

Surfaced by the parallel general-purpose subagent (12-fetch sub-budget; used 4). Headline finding: **Qwen-Image (already escalated to base-model recommendation above)**. Other notable forks: `Manga Editor Desu!` (orchestration tool, JP), Zenn corporate-deployment pattern (`himawarimix` + `animeoutlineV4`), Catapp-Art3D paid template membership (¥1000/mo, commercial-license-disciplined). Rakuten AI Studio confirmed dead-end for manga assets (it's a B2B LLM-agent product, not an image hub). Full report at [jp_cn_specific_finds_2026-04-29.md](../artifacts/research/jp_cn_specific_finds_2026-04-29.md).

---

## Phase 2 scope and gating decision

The Phase 1 findings are sufficient to make the headline base-model + character-consistency + LoRA-training calls without Phase 2. Phase 2 dimensions remaining:

- prompt_libraries_and_cookbooks
- datasets_for_finetuning_or_reference (Manga109 commercial-licensing question)
- post_processing_and_lineart_cleanup
- qa_and_drift_detection (Qwen-VL-vs-WD-EVA02 in-house bench)
- panel_layout_and_speech_balloons
- orchestration_and_batch (deeper diff vs `Manga Editor Desu!`)
- remaining 21 of 25 canonical genres in the LoRA roster

**My recommendation: NARROW_PHASE_2** rather than full proceed or cancel. Specifically:

- **Worth running in Phase 2:** `qa_and_drift_detection` (the Qwen-VL benchmark question is unresolved and matters for the cookbook PR), `orchestration_and_batch` (Manga Editor Desu! deserves a deep diff before Phoenix commits to keeping `runcomfy_batch.py` as-is), and 4–6 more high-priority genre LoRAs (battle, romance, school, horror — the lanes most likely to be Phoenix's volume traffic).
- **Worth deferring indefinitely:** the bulk per-genre LoRA roster (Phase 1's healing-control finding suggests anime base models cover most lanes natively — running a 21-genre LoRA hunt that confirms "no LoRA needed" is bad allocation), `panel_layout_and_speech_balloons` (will rebuild this Phoenix-side regardless), `post_processing_and_lineart_cleanup` (covered by Phase 1's custom-node section adequately).

If Phase 2 is approved at the narrowed scope, estimated budget is ~30 WebFetch calls and ~2 hours of agent time, vs the original ~3–5 hour Phase 2 spec.

---

## Cross-pollination with the cookbook PR

This audit cross-references the cookbook PR's drift autopsy in three places:

1. **Schnell-vs-Dev settings finding.** The workflow runs Schnell at Dev steps/cfg. Same finding as cookbook PR §0. The fix in the cookbook PR (revert to 4 steps cfg 1.0 OR migrate base) is the same fix called for here.
2. **Mecha failure root-cause.** Audit's PNG inspection diagnosed `stillness_press_mecha_us` as asset-absence (no mecha visible) rather than stylistic drift. Cookbook PR's mecha prompt fix should be paired with this audit's mecha LoRA recommendation (Super Robot Diffusion XL cross-tested on Animagine, or build Phoenix-native).
3. **Asian-script artifacts.** The audit's PNGs show unprompted kanji/hanzi calligraphy stamps appearing in outputs. Qwen-Image's first-class CJK text rendering would actually let Phoenix *control* this rather than suppress it — adding intentional dialogue/sfx text becomes a feature instead of a fight.

The cookbook PR (genre prompt cookbook) and this audit (community asset roster) are now mutually-grounded. The follow-up engineering PRs should pull from both.

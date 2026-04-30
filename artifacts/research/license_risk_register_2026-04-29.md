# License Risk Register — Phoenix Omega Manga Image Generation (Phase 1)

**Date:** 2026-04-29
**Phase:** 1
**Companion:** [community_assets_audit_2026-04-29.yaml](../../config/manga/community_assets_audit_2026-04-29.yaml) · [community_lora_roster](community_lora_roster_2026-04-29.yaml)

**Operator constraint:** Phoenix Omega ships commercial product. Every recommended asset MUST permit commercial use of generated outputs without per-deployment licensing negotiation.

**Tier convention:**
- 🟢 **commercial-clean** — license + base model + dependencies all permit commercial use without per-case verification.
- 🟡 **commercial-conditional** — at least one element requires per-page verification, attribution, paid creator permission, or carries AGPL contamination risk for wrapper code.
- 🔴 **non-commercial-blocked** — explicit NC tag, base model blocks commercial output, or unavoidable IP overlap.

---

## 🔴 BLOCKED items (do NOT use in production; documented for completeness)

### FLUX.1-dev base model

- **URL:** https://bfl.ai/legal/non-commercial-license-terms
- **License:** FLUX.1 [dev] Non-Commercial License v2.0
- **Risk to Phoenix:** **CRITICAL.** `config/manga/brand_lora_plans.yaml::training_defaults.base_model = "FLUX.1-dev"` declares this as the LoRA training base. Per the license, every LoRA derivative inherits the non-commercial restriction. Phoenix's commercial output of any image touched by a dev-trained LoRA is a license violation.
- **Remediation:** migrate training to FLUX-schnell (Apache 2.0), Animagine XL 4.0 (RAIL++-M), or Qwen-Image (Apache 2.0). See [integration_effort_estimates_2026-04-29.md](integration_effort_estimates_2026-04-29.md) for cost.
- **Commercial path if Phoenix wants to keep FLUX-dev:** purchase BFL self-hosted commercial license (https://bfl.ai/pricing/licensing) — pricing not surveyed; out of audit scope.

### NoobAI XL

- **URL:** https://huggingface.co/Laxhar/noobai-XL-1.0
- **License:** Restrictive — "prohibits any form of commercialization, including but not limited to monetization or commercial use of the model, derivative models, or model-generated products."
- **Risk to Phoenix:** **HARD STOP.** Even non-edited generated images cannot be used commercially. No remediation path short of license renegotiation with the creator.
- **Status:** documented; do not use.

### Pony Diffusion V6 XL

- **URL:** https://ponydiffusion.com/faq
- **License:** Modified Fair AI Public License 1.0-SD
- **Risk to Phoenix:** **BLOCKED.** "Not permitted to run inference of this model on websites or applications allowing any form of monetization." Civitai and HuggingFace have explicit grants; Phoenix would not.
- **Remediation:** contact contact@purplesmart.ai for explicit commercial permission. Out of audit scope.
- **Status:** documented; do not use without explicit permission.

### Illustrious-XL (and most popular community LoRAs based on it)

- **URL (compare):** https://civitai.com/articles/8642/ilxl-illustrious-xl-nai-xl-noobai-xl-model-comparison
- **License:** Generated images not commercial-OK if not edited.
- **Risk to Phoenix:** **BLOCKED.** Even where a downstream LoRA's own license is permissive, the base model contamination blocks commercial output. This affects the [Super Robot Diffusion XL](https://civitai.com/models/124747) mecha LoRA (Illustrious-base) — Phoenix can fork the LoRA file but cannot ship images generated with the Illustrious base.
- **Remediation:** cross-test the Illustrious-trained LoRA on Animagine XL 4.0 (also SDXL — partial transfer expected). If quality acceptable, run with Animagine; if not, train Phoenix-native mecha LoRA on Animagine.

### InstantID and IP-Adapter FaceID

- **URL:** https://huggingface.co/InstantX/InstantID/discussions/2
- **Risk to Phoenix:** **BLOCKED via dependency.** Code is Apache-2.0, but uses InsightFace's AntelopeV2 face-recognition weights, which are non-commercial unless InsightFace's commercial license is purchased.
- **Remediation:** use PuLID-FLUX with the FaceNet loader path (see 🟢 section below) which avoids InsightFace entirely.

### Studio Ghibli LoRAs (Ghibli-named LoRAs on Civitai)

- **Examples:** [civitai.com/models/137562](https://civitai.com/models/137562/studioghibliredmond-studio-ghibli-lora-for-sd-xl), [civitai.com/models/359367](https://civitai.com/models/359367)
- **Risk to Phoenix:** **BLOCKED.** Creator declared non-commercial, AND the LoRA's training data overlaps Studio Ghibli's protected IP. Even with a permissive LoRA license, the IP risk is unmanageable for Phoenix's commercial scale.
- **Remediation:** none. For iyashikei/healing register, use Animagine XL 4.0 base (no LoRA needed; covers register natively).

---

## 🟡 CONDITIONAL items (use with verification)

### CivitAI LoRAs with default permissive flags but unverified per-page

- **Examples:** Super Robot Diffusion XL, DARK FANTASY XL v1.1, LineAniRedmond, H4LFT0N3_XL, animeoutlineV4
- **Risk to Phoenix:** Civitai license model has 6 flags ([guide](https://education.civitai.com/guide-to-licensing-options-on-civitai/)) — defaults to "allow" but creators can restrict any flag. Phoenix engineering must verify per-page before bundling.
- **Required verification (per LoRA):**
  1. "Sell generated images" flag = ON
  2. "Use on other generation services" flag = ON (Phoenix is a third-party service)
  3. "Use without crediting me" = ON OR plan attribution
  4. "Share Merges of this model" matches Phoenix's redistribution plans
  5. Base model permits commercial output
  6. Record last_updated date and creator handle for audit trail
- **Remediation:** complete checklist in [community_lora_roster_2026-04-29.yaml::license_verification_checklist](community_lora_roster_2026-04-29.yaml).

### PuLID-FLUX (default InsightFace path)

- **Risk:** Uses AntelopeV2 weights (non-commercial). Same dependency that blocks InstantID.
- **Remediation:** swap to FaceNet loader via `lldacing/ComfyUI_PuLID_Flux_ll`'s `PulidFluxFaceNetLoader`. After swap → 🟢.

### SimpleTuner (AGPL-3.0)

- **URL:** https://github.com/bghira/SimpleTuner
- **Risk to Phoenix:** **AGPL contamination on distribution.** If Phoenix imports/wraps SimpleTuner and later distributes the wrapper externally (open-source release, partner integration, customer-facing build), the wrapper code itself becomes obligated to AGPL — Phoenix would need to open-source the wrapper.
- **Internal-only use:** OK. AGPL only triggers obligations on distribution.
- **Remediation:** prefer **ai-toolkit (MIT)** or **kohya_ss (Apache-2.0)** for Phoenix's training pipeline. SimpleTuner only if a specific feature is materially required (none currently identified).

### OneTrainer (AGPL-3.0)

- Same risk profile as SimpleTuner.
- Per Furkan Gözükara's comparative review, "no benefit of using OneTrainer for FLUX training instead of using Kohya." No reason to take the AGPL hit.
- **Remediation:** skip.

### ComfyUI-Manager (GPL-3.0)

- **URL:** https://github.com/ltdrdata/ComfyUI-Manager
- **Risk:** GPL-3.0 contamination concern for wrapper code that imports/links ComfyUI-Manager. Runtime use (running ComfyUI with the manager installed for ops convenience) is generally OK; bundling the manager into Phoenix's distributed product would trigger obligations.
- **Remediation:** use ComfyUI-Manager as an operator tool, not as a Phoenix product dependency. Phoenix's batch driver (`runcomfy_batch.py`) does not need to import ComfyUI-Manager.

### Catapp-Art3D paid template membership (¥1000/mo, note.com)

- **URL:** https://note.com/catap_art3d/n/nb24d97f8c2b9
- **Risk:** Paid creator content; reuse rights vary per template. Author is explicit about commercial-license-clean workflows but Phoenix must verify per-template.
- **Remediation:** if Phoenix subscribes (likely worth the ¥1000/mo for the workflow patterns alone), document per-template reuse rights before bundling any pattern into Phoenix workflows.

### Manga Editor Desu! (NegiTurkey)

- **URL:** https://qiita.com/kerimeka/items/d3cf8b338c742bc96a89
- **Risk:** Free + Pro tier. License terms not surveyed in Phase 1.
- **Remediation:** Phase 2 evaluation — read the repo's actual license file before committing to a fork.

### Qwen-Image individual community LoRAs on ModelScope

- **Examples:** ColorManga, Multiple-Angles-LoRA, Qwen-Image-i2L
- **Risk:** Qwen-Image base is Apache 2.0 (🟢), but individual community-uploaded LoRAs have varying licenses (mixed CC-BY, Apache, sometimes 🔴 non-commercial).
- **Remediation:** per-LoRA verification before bundling.

---

## 🟢 CLEAN items (recommended for primary use)

### Qwen-Image

- **URL:** https://github.com/QwenLM/Qwen-Image
- **License:** Apache 2.0
- **Status:** Use as primary base model for ja_JP/zh_TW/zh_CN/ko_KR locales and any catalog row needing speech-bubble text rendering.

### Animagine XL 4.0

- **URL:** https://huggingface.co/cagliostrolab/animagine-xl-4.0
- **License:** CreativeML Open RAIL++-M
- **Status:** Use as primary or secondary base model. Permits both commercial use and modification. RAIL++-M restricts certain illegal/harmful uses; Phoenix's catalog doesn't trip these.

### FLUX.1-schnell

- **URL:** https://huggingface.co/black-forest-labs/FLUX.1-schnell
- **License:** Apache 2.0
- **Status:** Phoenix's current path (workflow misconfiguration aside). Acceptable as fallback; weaker manga register than Animagine/Qwen requires heavier LoRA stack.

### PuLID-FLUX with FaceNet loader

- **URL:** https://github.com/lldacing/ComfyUI_PuLID_Flux_ll
- **License:** Apache 2.0 (PuLID + node) + facenet-pytorch + VGGFace2 weights (commercial-clean)
- **Status:** Use `PulidFluxFaceNetLoader` (NOT `PulidFluxInsightFaceLoader`).

### ai-toolkit (ostris)

- **URL:** https://github.com/ostris/ai-toolkit
- **License:** MIT
- **Status:** Primary LoRA training pipeline.

### kohya_ss / sd-scripts

- **URL:** https://github.com/bmaltais/kohya_ss
- **License:** Apache-2.0
- **Status:** Co-primary LoRA training pipeline (advanced config surface).

### FluxGym

- **URL:** https://github.com/cocktailpeanut/fluxgym
- **License:** MIT
- **Status:** Onboarding tool for non-engineers training character LoRAs.

### ComfyUI_LayerStyle

- **URL:** https://github.com/chflame163/ComfyUI_LayerStyle
- **License:** MIT
- **Status:** HalfTone node + film/levels/colormap.

### Animagine 4.0 base for fantasy_adventure and healing genres

- See [community_lora_roster_2026-04-29.yaml](community_lora_roster_2026-04-29.yaml). No LoRA needed for these genres.

---

## Summary table

| Item | Tier | Use? |
|---|---|---|
| Qwen-Image | 🟢 | Yes — primary base |
| Animagine XL 4.0 | 🟢 | Yes — secondary base |
| FLUX.1-schnell | 🟢 | Yes — legacy fallback |
| FLUX.1-dev | 🔴 | **NO — license violation** |
| Pony V6 / NoobAI / Illustrious | 🔴 | No |
| PuLID-FLUX (FaceNet path) | 🟢 | Yes |
| PuLID-FLUX (InsightFace path) | 🟡 | Use only if FaceNet swap done; else no |
| InstantID / IP-Adapter FaceID | 🔴 | No |
| ai-toolkit | 🟢 | Yes — primary trainer |
| kohya_ss | 🟢 | Yes — co-primary |
| FluxGym | 🟢 | Yes — onboarding |
| SimpleTuner / OneTrainer | 🟡 | Avoid unless materially required |
| ComfyUI-Manager | 🟡 | Operator tool only; do not bundle |
| ComfyUI_LayerStyle | 🟢 | Yes |
| sketch2manga / Img2DrawingAssistants / Fill-Nodes | 🟡 | Use after license verification |
| Super Robot Diffusion XL (mecha) | 🟡 | Use only if Animagine cross-test passes |
| DARK FANTASY XL v1.1 | 🟡 | Use after Civitai flag verification |
| Studio Ghibli LoRAs | 🔴 | No |
| Qwen-Image community LoRAs (ColorManga, Multiple-Angles, i2L) | 🟡 | Use after per-LoRA verification |
| `Manga Editor Desu!` | 🟡 | Phase 2 evaluation |
| Catapp-Art3D paid templates | 🟡 | Subscribe to evaluate; per-template verification |

---

## Decision points for the operator

1. **FLUX.1-dev migration timing.** Every day Phoenix continues training new LoRAs on FLUX-dev compounds the license-clearing cost. Recommend: freeze new dev-LoRA training immediately; migrate to schnell-or-Animagine-or-Qwen in the next sprint.

2. **AGPL acceptance.** Operator's stated preference is to avoid AGPL for wrapper code. Confirmed — recommendation is to pin training pipeline to MIT/Apache (ai-toolkit + kohya_ss) and skip SimpleTuner/OneTrainer.

3. **Civitai license-flag verification cost.** Each 🟡 LoRA requires a manual page check. ~15 LoRAs in the Phase 1 list need verification; ~5 minutes per LoRA = ~1.5 hours of engineering time to clear the Phase 1 roster. Worth doing before bundling into production.

4. **Studio Ghibli aesthetic substitute.** Phoenix may want a Ghibli-adjacent style for some healing/iyashikei outputs. The audit's recommendation is to lean on Animagine 4.0's native register rather than fork a Ghibli-named LoRA — the IP risk is unmanageable regardless of license. If a stronger watercolor-soft-painterly aesthetic is needed, training a Phoenix-named LoRA on cleared training data is the path.

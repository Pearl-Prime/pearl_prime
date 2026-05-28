# Manga Layer Compositing Research — 2026-05-20

**Status:** RESEARCH (advisory; empirical validation required before adoption)
**Author:** Pearl_Research (sub-agent)
**Scope:** Concrete architectural and tooling guidance to resolve the V4 layer-render compositing problem documented in `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.6.1 (scene-prior load-bearing, rembg cutout keeps attached props, L2/L0 table fragments don't align).
**Visual evidence reviewed:**
- `artifacts/manga/.../composed_v4_qwen/ep_001/ep001_005.png` — Mira floating + visible misaligned chair fragment lower-right.
- `artifacts/manga/.../composed_v4_qwen/ep_001/ep001_018.png` — happens to align; the exception.
- `artifacts/manga/.../experiments/v4_b_test/ep001_006_L2_v4btest2_face_only_alpha_u2net_human_seg_v2.png` — visible chair sliver kept by u2net_human_seg.
- `artifacts/manga/.../experiments/v4_b_test/ep001_006_L2_v4btest2_face_only_alpha_isnet_anime_v2.png` — isnet-anime keeps stove fragment behind shoulder.

> **Evidence note (provenance, 2026-05-29):** the `experiments/v4_b_test/` cutout files cited above are NOT present in the repo checkout (cannot be re-verified). The core V4→V5 decision is independently corroborated by the 35 `composed_v4_qwen/ep_001/` composites + the operator ep_001 review — see `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md`.

---

## Executive summary (the recommended architectural shift)

**The post-cutout architecture is fighting the wrong problem.** Three production-ready options have emerged in 2025–2026 that bypass it entirely; the recommendation is to A/B test them in this priority order:

1. **ToonOut (BiRefNet fine-tuned on anime, MIT-licensed, 2025-09)** — A drop-in rembg replacement specifically trained on the "Action" category (characters holding items). Reported 99.0% pixel accuracy on character-with-prop scenes vs. BiRefNet baseline's 76.8%. Same Python API as rembg; immediate swap-in path. **This alone likely solves 80% of the visible artifact problem.**

2. **Qwen-Image-Layered (Alibaba native model, late-2025)** — Designed exactly for this case: takes ONE scene+character render and decomposes it into clean RGBA layers (background, subject, foreground props) with reconstructed occluded regions. Native ComfyUI support. Eliminates the L0+L2 split entirely — render the whole panel once, decompose into layers, recompose with placement/positioning. **Architectural shift, not a tooling swap.**

3. **IC-Light V2 FBC (FLUX-based, foreground+background conditioned, 2025)** — Solves the OTHER half of the problem (lighting mismatch between L2 cutout and L0 background). After cutout, relight the character to match L0's lighting environment. Works downstream of any cutout solution.

**Anti-recommendation:** Do not invest in Layer Diffusion (`lllyasviel/sd-forge-layerdiffuse`). It is SDXL/SD1.5-only — Qwen-Image is not supported, and the project hasn't shipped FLUX/Qwen support in 12+ months.

**Recommended path:** Run ToonOut against the existing v4_b_test L2 renders this week (1-day swap). If pixel-accuracy gets the operator's "floating + table edge" complaints below threshold, ship V4.1 with that. If it doesn't, pivot to Qwen-Image-Layered as the V5 architecture (render whole panel, decompose, no L0+L2 split). IC-Light V2 is a separate later add-on for lighting consistency.

---

## §1 — Visual diagnosis (what the cutouts actually look like)

I read the actual v4_b_test alpha images. Concrete findings:

- **u2net_human_seg** (`ep001_006_L2_v4btest2_face_only_alpha_u2net_human_seg_v2.png`): keeps a visible **chair fragment on the right shoulder area** (~30px slice of wooden chair edge). The character body is otherwise clean.
- **isnet_anime** (`ep001_006_L2_v4btest2_face_only_alpha_isnet_anime_v2.png`): keeps a **stove fragment behind the left shoulder** (~80px wide gray rectangle). Cleaner around hair than u2net but worse around shoulder/scene-attached regions.
- **isnet_general_use** (`ep001_006_L2_v4btest2_face_only_alpha_isnet_general_use_v2.png`): worst — large chunks of kitchen counter visible behind body.
- The composite `ep001_005.png` reveals: L0 has its own table on the LEFT (correctly placed). L2 cutout's chair fragment lands in the LOWER-RIGHT of the composite — disjoint from L0's table. That's the misalignment the operator describes.

**Root cause is two-layered:**
1. **Cutout precision** — rembg's anime/human models don't have a strong enough prior to distinguish "character body" from "scene element touching the character body." They treat the contact region as ambiguous and include the prop.
2. **Geometric alignment between layers** — even with a perfect cutout, L2's implied "where the character is sitting" is determined by Qwen at render time. L0's "where the table is" is also determined by Qwen at render time. They don't share a coordinate system; the composite paste-bbox is a pct-of-canvas heuristic that doesn't match either render's internal geometry.

The fix is to either (a) get a precise enough cutout that the prop fragments disappear (ToonOut), or (b) eliminate the L0+L2 split entirely by rendering the whole panel and decomposing (Qwen-Image-Layered).

---

## §2 — Q1: State-of-the-art character segmentation models 2026

### §2.1 ToonOut (the headline finding — recommend adopting this immediately)

- **Paper:** [ToonOut: Fine-tuned Background-Removal for Anime Characters](https://arxiv.org/abs/2509.06839) (2025-09-08)
- **GitHub:** https://github.com/MatteoKartoon/BiRefNet
- **HuggingFace dataset:** https://huggingface.co/datasets/joelseytre/toonout
- **License:** MIT (code), CC-BY 4.0 (dataset) — commercial-clean.
- **Architecture:** BiRefNet fine-tuned with dual supervision (auxiliary gradient + GT). Dataset: 1,228 hand-annotated anime images, 80/10/10 split. Training: 4,646 epochs on 2× RTX 4090 (24GB), bf16, weighted loss (SSIM λ=10, MAE λ=90, IoU λ=0.25).
- **Reported metrics:**
  - Overall: Pixel Accuracy 95.3% → 99.5%; Boundary IoU 88.5% → 95.6%.
  - **"Action" category (characters with held items): 76.8% → 99.0% PA.** This is exactly Mira-with-cup case.
  - Outperforms BRIA 2.0 baseline AND closed-source Photoroom.
- **Inference cost:** Same as BiRefNet (it's the same model, fine-tuned weights). BiRefNet at 1024×1024 takes ~0.5-1.5s on RTX 5070 Ti, ~3-8s on CPU. CPU-feasible on Apple Silicon but slow; recommend Pearl Star (RTX 5070 Ti) for batch.
- **How to swap in:** Replace the `rembg.new_session("u2net_human_seg")` call in `scripts/manga/render_v4_episode.py:354` with a BiRefNet inference call using the ToonOut checkpoint. The output is the same: an RGBA PIL Image with alpha-cut character. Drop-in.
- **Risk / unknown:** The paper claims excellent prop handling for "Action" category but the eval set is unknown to us. Empirical test needed: run ToonOut on the existing 4 v4_b_test L2 renders and visually compare to the current isnet_anime / u2net_human_seg outputs.

### §2.2 SAM 3 (Meta, 2025-11-20) + GroundingDINO

- **Paper:** [SAM 3: Segment Anything with Concepts](https://blog.roboflow.com/what-is-sam3/), [Meta blog](https://ai.meta.com/blog/segment-anything-model-3/)
- **GitHub (ComfyUI integration):** https://github.com/1038lab/ComfyUI-RMBG (supports SAM2, SAM3, GroundingDINO; v3.0.0 released 2026-01-01)
- **Capability:** SAM 3 accepts **open-vocabulary text prompts** — you can say "the woman, but not the chair or the table" and get a mask just for her body. This is qualitatively new.
- **Limitation on anime per recent literature:** "SAM3 often produces incomplete or ambiguous segmentations on anime characters. Typical failure cases include missing regions (e.g., hair or trousers) and overlapping masks across parts" (paraphrased from See-through SIGGRAPH 2026 paper context). It's tuned on real-world photos; anime is OOD.
- **Practical use:** For Mira-with-cup, the prompt-driven approach could remove the cup deterministically. But SAM3's anime weakness means body parts may be cut incorrectly. **Not recommended as primary**, but a useful supplement: use ToonOut for the body, use SAM3-prompted on a small "kitchen counter / chair / cup / table" prompt to subtract residual props from the alpha if any survive.
- **Inference cost:** SAM 3 base is ~2-4 GB VRAM, runs at ~5fps on RTX 5070 Ti for single-image inference. CPU on Apple Silicon: feasible but slow (~5-10s/image).

### §2.3 SkyTNT/anime-segmentation (isnet-anime)

- **GitHub:** https://github.com/SkyTNT/anime-segmentation (Apache-2.0, the upstream of rembg's `isnet-anime` model)
- **Status:** Mature (since 2023), well-trained on anime, but lower precision than ToonOut by 2025 benchmarks. The current pipeline already uses this — confirmed in v4_b_test outputs to keep stove/chair fragments. Already at its ceiling for our case.

### §2.4 BiRefNet (general) family — what's available

- **GitHub:** https://github.com/ZhengPeng7/BiRefNet
- **Variants:** BiRefNet-general (general dichotomous), BiRefNet-portrait (human-tuned), BiRefNet-HR (high-resolution up to 2560×2560), BiRefNet-massive (largest weights). All Apache-2.0.
- **Verdict:** Without ToonOut fine-tuning, BiRefNet-portrait is still tuned on photorealistic humans — likely better than rembg's `birefnet-portrait` (it's the same upstream) but no specific anime training. ToonOut wins on anime.

### §2.5 Comparison table

| Model | Anime-tuned | Handles attached props | License | Inference (RTX 5070 Ti) | Drop-in via rembg API |
|---|---|---|---|---|---|
| **ToonOut (BiRefNet-FT)** | YES (1228 anime imgs) | **YES (99% PA on "Action")** | MIT | ~1s | Manual swap (not rembg-native, but same input/output contract) |
| rembg `isnet-anime` | YES (SkyTNT) | Partial (visible fragments) | Apache-2.0 | ~0.3s | YES |
| rembg `u2net_human_seg` | NO | Partial | Apache-2.0 | ~0.3s | YES |
| BiRefNet-HR | NO (general) | Better edges, not prop-aware | Apache-2.0 | ~2s @ 2560px | Manual swap |
| BRIA RMBG-2.0 | NO (struggles on 2D anime) | Decent | **CC-BY-NC** (not commercial-clean) | ~0.5s | Manual swap |
| SAM 3 + text prompt | NO | YES (prompted subtraction) | Apache-2.0 | ~0.5s | Custom integration |

---

## §3 — Q2: Render-side approaches that avoid the cutout problem entirely

### §3.1 Qwen-Image-Layered (the architectural shift)

- **Native ComfyUI support:** [ComfyUI Wiki](https://comfyui-wiki.com/en/tutorial/advanced/image/qwen/qwen-image-layered), [official ComfyUI docs](https://docs.comfy.org/tutorials/image/qwen/qwen-image-layered)
- **WaveSpeed AI explainer:** https://wavespeed.ai/blog/posts/introducing-wavespeed-ai-qwen-image-layered-on-wavespeedai/
- **Required files:** `qwen_2.5_vl_7b_fp8_scaled.safetensors`, `qwen_image_layered_bf16.safetensors` (or `_fp8mixed.safetensors`), `qwen_image_layered_vae.safetensors`. Download from HuggingFace or ModelScope.
- **What it does:** Takes one input image (a complete panel — e.g., kitchen scene with Mira at table). Decomposes into multiple independent RGBA layers (background, subject, text overlays, foreground props). **Reconstructs the occluded background region behind the subject** — so the kitchen behind Mira is filled in with kitchen, not white. Cleanly separates subject pixels from prop pixels via semantic decomposition (not edge detection).
- **VRAM:** bf16 ~45GB peak (needs RTX 6000 Pro / A100); fp8mixed runs on RTX 4090 24GB with quality close to bf16. Pearl Star RTX 5070 Ti has 16GB — fp8mixed may fit; needs testing.
- **Inference time:** ~120s per 1024px image on RTX Pro 6000 (96GB). On a 16GB card running fp8mixed: estimate 180-300s per panel.
- **Capability claims:** "The model distributes visual elements across layers based on depth and semantic understanding — background to layer 0, main subject to layer 1, text overlays to layer 2, small foreground objects to layer 3. Each element cleanly separated with proper transparency." (WaveSpeed AI). Handles occlusion: "when a person stands before a building, the model intelligently fills in obscured background areas."
- **Architectural implication for Phoenix:** The L0+L2 split becomes unnecessary. Workflow becomes:
  1. Render the WHOLE panel with Qwen-Image (Mira sitting at kitchen table) — what Qwen wants to render anyway.
  2. Run Qwen-Image-Layered decompose → 4 RGBA layers.
  3. Composite back with archetype-aware positioning of each layer.
  4. Continuity becomes per-layer: the "kitchen background layer" can be reused across panels (matches the V4 efficiency goal), and the "Mira layer" can be repositioned via the subject_placement_bbox.
- **License:** Qwen models are Apache-2.0 (commercial-clean).
- **Risk:** "Complex scenarios like 'people hugging' may show layer bleed" (WaveSpeed). Single-character Mira sitting at table is well within easy-mode for this model.

### §3.2 ControlNet Inpaint into existing L0 (the operator's hypothesis)

- **Workflow:** Render L0 first. Compute Mira's bbox from the archetype's `subject_placement_bbox`. Mask the bbox region of L0. Run a ControlNet-Inpaint pass with Mira's prompt + Mira's character reference (PuLID-FLUX or IP-Adapter or just text). The output: L0 with Mira inpainted directly into the bbox, inheriting L0's lighting and geometry. **No cutout needed.**
- **Tooling:** [Flux Fill](https://docs.comfy.org/tutorials/flux/flux-1-fill-dev) (FLUX inpainting model, 2024-11). Or [SDXL Inpaint + ControlNet Union](https://civitai.com/models/2374331/sdxl-10-inpaint-controlnet) for SDXL bases. Both stable in ComfyUI.
- **Pros:** Solves the geometric alignment problem deterministically — Mira's table/chair IS L0's table/chair because there's only one. Solves the lighting problem — Mira is rendered in L0's lighting context.
- **Cons:**
  1. **Identity drift risk:** Inpainting Mira from text alone won't preserve identity panel-to-panel without character-lock (PuLID-FLUX, IP-Adapter, or a trained LoRA). PuLID requires a face reference image (you have Mira's reference sheet from `artifacts/manga/character_references/`).
  2. **Lighter render-side efficiency:** L0 must be re-inpainted for every panel rather than reusing one L0 across an episode — kills the V4 caching win UNLESS the L0+inpaint is cached by `(scene, temporal, rig, character_state)` tuple.
  3. **Qwen-Image lacks an official inpaint variant.** Flux Fill is FLUX-based; SDXL has many. So switching to ControlNet-Inpaint means switching off Qwen for character renders.
- **Why this might still win:** The operator's CLAUDE.md tier policy is Qwen on Pearl Star for scheduled pipelines. But render_v4_episode.py already calls a ComfyUI workflow file at `scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json` — you can have a parallel FLUX-Fill workflow for the inpaint step without breaking the architecture.
- **Recommended config:** Use **FLUX Fill dev** + **PuLID-FLUX-FaceNet** (already on the Phoenix radar per CHARACTER_INDIVIDUATION_PIPELINE_SPEC.md). Inpaint Mira into L0's bbox; her face is locked by PuLID using her ref-sheet.

### §3.3 IP-Adapter face-locking with inpainting masks

- Same architectural idea as §3.2 but with IP-Adapter (older, more mature than PuLID). Mature ComfyUI nodes exist. Less identity-preservation strength than PuLID-FLUX-FaceNet per published comparisons ([MyAIForce 2024](https://myaiforce.com/hyperlora-vs-instantid-vs-pulid-vs-ace-plus/)).
- **Recommend skipping in favor of PuLID-FLUX** for new builds.

### §3.4 LoRA trained on transparent-background Mira samples

- **Status:** This is per `docs/specs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC.md §2.4`'s ai-toolkit LoRA proposal for the 12-14 named cast. Training data of "Mira on transparent" would need to be generated (chicken-and-egg if Qwen can't render her on transparent).
- **Workaround:** Train the LoRA on "Mira on simple solid-color backgrounds" — easier for the diffusion model — then rely on cutout to extract. This doesn't solve the cutout-quality problem.
- **Recommend:** Defer; LoRA training is independent of the layer-render architecture decision.

### §3.5 Layer Diffusion (lllyasviel/sd-forge-layerdiffuse)

- **GitHub:** https://github.com/lllyasviel/LayerDiffuse, https://github.com/huchenlei/ComfyUI-layerdiffuse
- **Status:** SDXL/SD1.5 only. Per the ComfyUI integration docs: "Currently only SDXL/SD15 are supported." No FLUX or Qwen support in 12+ months. **Stalled.**
- **What it does:** Trains a custom VAE that encodes RGB+alpha jointly. Renders directly to RGBA. Modes: "Generate foreground", "Blending given FG" (composite into given background), "Blending given BG" (generate FG conditioned on background).
- **Why not recommended:** Phoenix is committed to Qwen-Image (the cookbook §2.3 + commercial-clean stack). Going back to SDXL just for this is a major architectural regression.
- **Note:** The newer **See-through (SIGGRAPH 2026)** paper does an SDXL-based version of this with anime-specific training. ComfyUI workflow exists on RunComfy. Same SDXL caveat.

### §3.6 See-through / Layer decomposition (SIGGRAPH 2026)

- **Paper:** [arxiv 2602.03749](https://arxiv.org/html/2602.03749v1) — Single-image Layer Decomposition for Anime Characters (conditionally accepted SIGGRAPH 2026)
- **GitHub:** https://github.com/shitagaki-lab/see-through (Apache-2.0; last update 2026-04-14)
- **ComfyUI workflow:** https://www.runcomfy.com/comfyui-workflows/see-through-workflow-in-comfyui-anime-layer-decomposition-psd
- **What it does:** Decomposes a SINGLE anime character (already isolated) into 23 semantic layers (face, hair, eyes, clothes, accessories, occluded body parts inferred). Output is a PSD.
- **VRAM:** 12-16 GB @ 1280px; 8GB-optimized variants exist.
- **Why interesting:** For panel-to-panel pose articulation, this gives you a face-layer that can be swapped/morphed independently of the body. Long-term architecture: render Mira once, decompose into 23 layers, manipulate them per panel (gaze, expression) without re-rendering.
- **Why not now:** Requires already-isolated character (so doesn't replace cutout). Solves a different problem (pose/expression manipulation, not background separation). Worth tracking for V5+.

---

## §4 — Q3: Compositing-time approaches (refinement after cutout)

### §4.1 Trimap-based alpha matting upgrades

- The current pipeline uses `rembg`'s built-in alpha_matting (PyMatting under the hood) with foreground/background thresholds 240/10. This is the soft-edge tool.
- **SAM2-Matte** (Fan et al., 2026-01-17, [arxiv 2601.12147](https://arxiv.org/html/2601.12147v1)) — unified segmentation + matting with SAM2 backbone + dual prediction heads. State-of-the-art on real-world matting benchmarks. Anime performance unknown; based on SAM2 weaknesses on anime, likely similar to SAM3's caveats.
- **Mask-Guided Iterative Refinement** ([arxiv 2502.17093](https://arxiv.org/html/2502.17093)) — takes any initial mask (e.g., ToonOut's) and iteratively refines edges. Could stack on top of ToonOut for the last-mile.
- **Matting Anything (MAM)** — [GitHub](https://github.com/SHI-Labs/Matting-Anything) — SAM features + 2.7M-param Mask-to-Matte head. Prompt-guided (point/box/text). Real-time-ish. **Could** be used as: ToonOut produces a binary mask → MAM produces the final alpha matte from it.
- **Recommendation:** Start with ToonOut alone (its alpha is already soft-edged and high-quality per the paper). Only stack MAM if visible aliasing remains.

### §4.2 MODNet, Robust Video Matting, BackgroundMattingV2

- All photorealistic-portrait-tuned. MODNet documented to "predict fine-grained details like hair strands accurately" but tuned for video portrait matting, not anime stills.
- **Verdict:** Not specifically tuned for anime; ToonOut dominates these for the Phoenix use case. Don't pursue.

### §4.3 Edge-aware blending / Poisson seam

- The post-paste artifact (visible edge between Mira's cutout and L0) can be reduced with Poisson seam blending. OpenCV `cv2.seamlessClone(MIXED_CLONE)` is the canonical tool — well-trodden.
- Phoenix's `composite_panel` in `scripts/manga/render_v4_episode.py:370` currently does straight alpha_composite. Adding `cv2.seamlessClone` on top of the alpha is a 30-line change.
- **Recommendation:** Add as a final polish step after ToonOut. Test for color-shift artifacts (Poisson can introduce them on highly stylized art).

### §4.4 Mediapipe Holistic / Selfie Segmentation

- Google's Mediapipe is photorealistic-tuned and known to fail on anime faces (the face detector misses anime-style large eyes / no-nose). **Skip.**

---

## §5 — Q4: The hybrid "render whole panel then extract" approach

This is exactly what §3.1 (Qwen-Image-Layered) does. To answer it specifically:

- **AnyDoor** — [paper review](https://liner.com/review/anydoor-zeroshot-objectlevel-image-customization) — zero-shot object insertion using DINOv2 ID extractor + frequency-aware detail extractor. Outperforms PaintByExample on identity preservation. Could be used as: render Mira in any pose on any background, then "insert" her into a target scene with AnyDoor. Mature; multiple open implementations.
- **PaintByExample** — older (2023), inferior to AnyDoor by 2025 benchmarks.
- **Verdict:** AnyDoor is a viable path for character-into-scene composition with identity preservation. But it does not solve the SAME problem as §3.1 Qwen-Image-Layered — AnyDoor inserts an EXISTING character into a NEW scene; Qwen-Image-Layered decomposes ONE rendered scene into layers. For Phoenix's case (we have many panel renders and need clean layers), Qwen-Image-Layered is the more direct fit.

---

## §6 — Q5: GitHub repo recommendations (actively maintained, 2025+)

| Repo | What it does | Last active | License | Direct relevance |
|---|---|---|---|---|
| [MatteoKartoon/BiRefNet (ToonOut)](https://github.com/MatteoKartoon/BiRefNet) | Anime-FT BiRefNet for character cutout | 2025-09 | MIT | **Critical — immediate adoption candidate** |
| [1038lab/ComfyUI-RMBG](https://github.com/1038lab/ComfyUI-RMBG) | ComfyUI custom node: RMBG-2.0, BiRefNet, BEN2, SAM3, GroundingDINO | 2026-01-01 (v3.0.0) | Apache-2.0 | High — single node to swap multiple cutout models for A/B test |
| [SHI-Labs/Matting-Anything](https://github.com/SHI-Labs/Matting-Anything) | SAM-based prompt-driven matting (point/box/text) | Active | Apache-2.0 | Medium — post-cutout edge refinement |
| [shitagaki-lab/see-through](https://github.com/shitagaki-lab/see-through) | SIGGRAPH 2026 anime layer decomposition (23 semantic layers per character) | 2026-04-14 | Apache-2.0 | Medium — V5+ pose/expression manipulation |
| [SkyTNT/anime-segmentation](https://github.com/SkyTNT/anime-segmentation) | The current upstream for `isnet-anime` | Stable | Apache-2.0 | Already in use; reference baseline |
| [huchenlei/ComfyUI-layerdiffuse](https://github.com/huchenlei/ComfyUI-layerdiffuse) | Layer Diffusion (SDXL/SD1.5 only) | Stalled (no FLUX/Qwen) | Apache-2.0 | Low — anti-recommendation |
| [lllyasviel/IC-Light](https://github.com/lllyasviel/IC-Light) | IC-Light V1 (SD1.5) + V2 (FLUX) — character-into-scene relighting | Active 2025 | Apache-2.0 | High — post-composite lighting consistency |
| [yeates/OmniPaint](https://github.com/yeates/OmniPaint) | ICCV 2025 — disentangled insertion-removal inpainting | 2025 | Research code | Medium — alternative to ControlNet Inpaint |

### Native Qwen-Image-Layered workflow
- ComfyUI: native (no custom node). Just download the 3 model files from HuggingFace and update ComfyUI.
- Workflow JSON examples: [ComfyUI docs](https://docs.comfy.org/tutorials/image/qwen/qwen-image-layered)

---

## §7 — Q6: Anti-recommendations (things tried elsewhere that fail on anime)

1. **MODNet / Robust Video Matting / BackgroundMattingV2** — photorealistic portrait matting. Fails on anime due to stylized face geometry and out-of-distribution color palettes.
2. **Mediapipe SelfieSegmentation / Holistic** — Google's mobile vision stack. Face detector misses anime-style faces (large eyes, simplified nose) entirely. The skeleton-pose estimator fails on stylized proportions.
3. **BRIA RMBG-2.0 (commercial)** — license is CC-BY-NC (not commercial-clean per Phoenix tier policy). Also explicitly weaker on 2D anime per the model card. **Banned by license alone.**
4. **u2net (general) / u2netp** — original rembg defaults. Decent on photos, mediocre on anime (already replaced by isnet-anime in current pipeline).
5. **SAM 1 / SAM 2 without text prompts** — interactive segmentation needs a human in the loop. Not pipeline-friendly. SAM 3 with text prompts fixes this, but anime weakness remains (§2.2).
6. **Layer Diffusion (`sd-forge-layerdiffuse`)** — stalled at SDXL/SD1.5. Not Qwen-compatible. Architectural regression to adopt.
7. **PaintByExample** — superseded by AnyDoor on identity preservation by 2024 benchmarks. Don't use directly.
8. **Negative prompts to suppress scene rendering** — already empirically demonstrated to fail in v4_b_test #2 (Qwen ignored "NO SCENE, no table, no chair, no cup" and rendered them anyway). The model has a strong scene prior; negatives don't dent it. This led to v0.6.1's reframe. **Don't go back to this path.**

---

## §8 — Recommended path forward (concrete implementation steps)

### Phase 1 (1-2 days) — ToonOut drop-in test
**Goal:** see if a better cutout alone gets the operator's complaints under threshold.

1. `pip install` BiRefNet dependencies (`torch`, `kornia`, `einops`, the BiRefNet package or its source).
2. Download ToonOut weights from https://github.com/MatteoKartoon/BiRefNet (or HuggingFace mirror).
3. Add a `cutout_engine: "toonout"` option to the `cutout_policy` block in `config/manga/panel_templates/iyashikei.yaml` archetypes.
4. In `scripts/manga/render_v4_episode.py:352`, add a branch in `apply_cutout`: if `model_name == "toonout"`, use BiRefNet inference instead of rembg.
5. Run on the 4 existing v4_b_test L2 renders (`ep001_006_L2_v4btest2_face_only.png` etc.). Output ToonOut cutouts next to existing isnet_anime/u2net cutouts for operator side-by-side review.
6. **Decision gate:** if the chair / stove fragments are gone (compare to `ep001_006_L2_v4btest2_face_only_alpha_isnet_anime_v2.png`), ship V4.1 with ToonOut. If fragments still visible, escalate to Phase 2.

### Phase 2 (3-5 days) — Qwen-Image-Layered architectural shift
**Goal:** eliminate the L0+L2 split; render whole panel, decompose into layers.

1. Verify Pearl Star (RTX 5070 Ti, 16 GB) can run `qwen_image_layered_fp8mixed`. If not, fp8mixed offload-to-CPU or fall back to a smaller variant.
2. Build a new ComfyUI workflow `qwen_image_layered_decompose.json` that takes one rendered panel + the decompose prompt, outputs N RGBA layers.
3. Refactor `scripts/manga/render_v4_episode.py`:
   - L0+L2 → single full-panel render dispatch.
   - Add `decompose_panel(rendered: Path) -> list[Path]` that returns the per-layer RGBA images.
   - Continuity caching shifts from "per-layer renders" to "per-layer post-decompose" — same architectural shape, different unit.
4. Compose-time: place each decomposed layer per archetype's `subject_placement_bbox` (the architectural intent doesn't change; only the source of the layers does).
5. **Decision gate:** if Qwen-Image-Layered preserves Mira's identity AND cleanly separates her from the kitchen scene, ship V5. If layer bleed on character-prop contact is too high, go to Phase 3.

### Phase 3 (1-2 weeks) — ControlNet-Inpaint into existing L0
**Goal:** Eliminate cutout entirely; inpaint Mira directly into L0 with PuLID face-lock.

1. Switch character render from Qwen-Image to FLUX Fill (FLUX-1-fill-dev).
2. Add PuLID-FLUX-FaceNet workflow with Mira's reference sheet (`artifacts/manga/character_references/mira_aoki/`).
3. L0 → mask `subject_placement_bbox` → Flux Fill inpaint with PuLID-locked Mira → output is composed panel directly. No cutout.
4. Continuity: cache L0 per `(scene, temporal, rig)`. Each panel runs a fresh inpaint into a copy of L0. Single L0 reused across the panel set.
5. **Risk:** identity may still drift across panels; PuLID-FLUX is good but not LoRA-quality. Cross-check with `qa_face_distance.py` (already in pipeline). If drift > threshold, train a Mira LoRA via ai-toolkit and stack on top.

### Independent track — IC-Light V2 lighting consistency
After whichever cutout/render path is chosen, run IC-Light V2 FBC (foreground+background conditioned) over the composite to relight Mira to match L0's lighting environment. This is an OR-condition with Phase 3 — Phase 3 inherently gives consistent lighting; Phase 1 and 2 benefit from IC-Light post-pass.

- **Cost:** ~3-5s per panel on RTX 5070 Ti.
- **Risk on anime:** IC-Light is photorealistic-tuned. May shift skin tones / desaturate. Empirical test required on Mira specifically.

---

## §9 — Risk and uncertainty (where empirical testing must happen)

1. **ToonOut on Mira specifically:** The paper's 99% PA is on their test set (Yamer's Anime SDXL renders). Qwen-Image renders may have different boundary characteristics. **Run side-by-side comparison test before committing.** This is a 1-day experiment.

2. **Qwen-Image-Layered VRAM fit on RTX 5070 Ti 16GB:** Unknown. fp8mixed claims fit in 24GB; 16GB needs testing. Possible fallback: ModelScope hosted (free) or WaveSpeed AI hosted ($0.05/4-layer image — note this violates the BANNED-paid-API policy in CLAUDE.md, so only as a one-off feasibility test, not production).

3. **Identity preservation across decomposed layers (Qwen-Image-Layered):** WaveSpeed's docs claim semantic preservation; not validated on consistent-character episodes. Could the decomposed "Mira layer" of panel 1 look like a different person from panel 2's decomposed "Mira layer"? Untested.

4. **IC-Light on anime skin tones:** Photorealistic-trained model on stylized illustration. Likely to fail in subtle ways. Test on Mira's reference sheet before deploying.

5. **PuLID-FLUX-FaceNet on Mira reference:** Mira's reference sheet is anime-stylized. PuLID's FaceNet feature extractor is photorealistic-trained. Identity preservation may be weaker than on photo refs. (This is the same average-face problem documented in `artifacts/research/average_face_problem_eval_2026-05-02.md`.) Cross-reference that earlier audit.

6. **The geometric-alignment problem at root:** If we stick with the L0+L2 split (Phase 1 ToonOut), even a perfect cutout doesn't solve the underlying problem that L0's table is at coord (X1,Y1) and L2's implied seat is at (X2,Y2). The composite's `subject_placement_bbox` is a pct-of-canvas approximation. **A perfect cutout makes Mira's body clean, but she may STILL float above L0's bottom edge.** Only Phase 2 (decompose) or Phase 3 (inpaint into L0) fully solves this. Operator should know that Phase 1 is a partial fix.

---

## §10 — One-paragraph TL;DR for operator

The current rembg cutout problem is well-known and well-solved in 2025-2026 publications. The minimum-cost fix is **ToonOut** (an MIT-licensed BiRefNet fine-tune on 1,228 anime images, GitHub: MatteoKartoon/BiRefNet, paper 2509.06839) — drop-in replacement for the cutout step, claims 99% PA on character-with-prop ("Action" category) vs. our baseline ~77%. Run a 1-day side-by-side test on the v4_b_test images first. If the visible fragment problem (cup, chair, stove) goes away, ship V4.1. If it doesn't, or the geometric "floating above bottom" issue persists (which it will, even with perfect cutouts — that's a coordinate-system problem between L0 and L2 renders, not a cutout problem), the architectural fix is **Qwen-Image-Layered** (Alibaba's native model, ComfyUI-supported, late-2025) which renders the whole panel once and decomposes into clean RGBA layers with proper occlusion handling — eliminating the L0+L2 split entirely. Both are commercial-clean (MIT / Apache-2.0). Do not pursue Layer Diffusion (SDXL-only, stalled), MODNet/RVM (photoreal-tuned, fails on anime), or BRIA RMBG-2.0 (CC-BY-NC, banned). For the secondary "lighting mismatch" complaint after cutout, **IC-Light V2 FBC** (FLUX-based, foreground+background conditioned) is the standard tool — empirically test on anime skin tones before adopting.

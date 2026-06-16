# Manga V5 — Qwen-Image-Layered single-render decompose architecture (supersedes V4 L0+L2 split)

**Status:** AUTHORITY (v1.0.0 — operator-directed 2026-05-20 after V4 ep_001 composite review)
**Author:** Pearl_Architect + Pearl_Int + Pearl_Research
**Schema version:** 1.0.0 (standalone V5 spec, sibling to `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7)
**Doc-split rationale:** Per V4 spec §15.C.6 (doc-split trip-wire at 1900 lines), the V4 spec is at 2,032 lines and inflating it with the full V5 architecture would push it past 2,400. V5 is therefore documented in this standalone sibling doc; the V4 spec carries only a short §16 deprecation marker pointing here.

**Supersedes:** V4 sections §3 (Architecture: the layer pipeline), §4 (Layer taxonomy — L0/L1/L2/L3/L4), §7 (Per-archetype layer composition maps), §13.4 (Phase D — render pipeline scripts), §15.A.6 (V4 composite-level operator review). V4 sections remain valid as the experiment-of-record + as fallback contract for V3.1 single-pass rendering.

**Does NOT supersede:** V4 sections §5 (Safe-zone hierarchical contracts), §6 (Continuity state schema), §5.9 (Contract-to-prompt compiler), §12 (Validator infrastructure), §14 (Failure modes & recovery), §15.A.1 (Identity lock). V5 reuses these contracts unchanged — see §8 of this doc.

---

## 1. Why V5 exists

V4 (per `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §3–§13, §15) describes a layered architecture in which each panel is built by independently rendering an L0 backdrop + an L2 character + optional L1/L3/L4 layers, then cutting the character out via `rembg` and compositing the layers at archetype-specified bounding boxes. The V4 architecture shipped to `stillness_en_01` ep_001 (35 composed panels) in PR #1239 on 2026-05-20.

**Operator review of the 35 V4 composites (2026-05-20) found only 2/35 properly placed the subject.** The other 33 exhibited two systemic failure modes:

1. **Cutout-residue artifacts:** `u2net_human_seg` kept a ~30px chair-edge slice on the right shoulder; `isnet_anime` kept an ~80px stove fragment behind the left shoulder; `isnet_general_use` (worst) kept kitchen-counter chunks behind the body. The rembg models cannot reliably distinguish "character body" from "scene element touching the character body."
2. **Geometric mis-alignment between layers:** L0 placed its table at coord (X1,Y1); L2's implied "where the character sits" landed at coord (X2,Y2). The two renders were independent Qwen-Image dispatches with no shared coordinate system. The composite's `subject_placement_bbox` is a pct-of-canvas approximation that does not encode either render's internal geometry. Result: **even after a perfect cutout, the subject floats above L0's bottom edge** — exactly what the operator observed.

Pearl_Research delivered findings (`artifacts/research/manga_layer_compositing_research_2026-05-20.md`) recommending three production-ready options in 2025–2026. Operator approved Phase 2 (architectural shift) on 2026-05-20. V5 is that shift.

## 2. Decision

**Approved:** Pivot V4 → V5. Render each panel as ONE full-panel dispatch via Qwen-Image-Layered, then decompose into N RGBA layers in the same workflow. Eliminate the L0+L2 split and the post-render rembg cutout step. Reuse the V4 archetype contracts, continuity_state schema, safe-zone hierarchical inheritance, and prompt compiler — V5 changes the *dispatch and cutout layers* of the pipeline, not the *contract scaffolding* above them.

**Operator quote (2026-05-20):** *"of the images, only 18 and 19 properly place her in the picture. often she is floating above the bottom and look cut. in almost all of them i can see the table from her pic and it doesn't match the background."* + *"have pearl_research do deep research on how to do this right."*

**Authority:** This document is the canonical V5 architecture. V4 sections in `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` are retained as the experiment-of-record — the architectural reasoning + the empirical findings that led to V5 — but are no longer the pipeline shape V5 ships.

## 3. The architectural shift

| Aspect | V4 (deprecated for ep_001+) | V5 (current) |
|---|---|---|
| Renders per panel | L0 + L2 (+ optional L1/L3/L4) | ONE full-panel render |
| Cutout step | `rembg` u2net_human_seg / isnet_anime / birefnet on L2 | Qwen-Image-Layered native decompose into N RGBA layers |
| Coordinate system | Independent — L0 and L2 don't share geometry | Single — model renders subject + scene together |
| Cutout precision | Variable per cutout model; props attached to silhouette | Native; model knows where subject ends and scene begins |
| Composite step | `PIL` paste of L2 RGBA onto L0 RGB at archetype bbox | `PIL` paste of decomposed layer 0 (subject RGBA) onto layer 1 (background RGB) — or render-time composite if the model provides one |
| Unique renders per series | ~82 unique L0×L2 combos compose to ~300 panels | One unique render per unique panel (no cross-panel L0 reuse) |
| Render cost | 1 L0 + 1 L2 per unique combo ≈ 0.8–1.5 min on Pearl Star fp8 | 1 unified render per panel ≈ 1.5–3 min (50 steps vs V4's 24 + decompose pass) |
| Continuity cache key | (scene_id, temporal, rig) for L0 + (character, archetype, pose, …) for L2 | (panel_id) — every panel is a unique render |

**Trade:** V5 gives up V4's L0-reuse cache efficiency in exchange for geometric coherence and cutout reliability. Empirically, V4's L0-reuse efficiency mattered LESS than predicted (operator review showed 33/35 panels needed bespoke rework anyway), so the trade is favorable.

## 4. Why V4 was rejected — root cause analysis

V4 was not rejected for prompt-engineering reasons. Every B-test (B-test #1 through B-test #4) confirmed Qwen-Image renders the *requested* subject correctly. V4 was rejected because **the post-render layering steps could not reconstruct the geometric and segmentation guarantees the architecture assumed.**

- **Cutout precision (root cause A):** rembg's anime/human-seg models lack a strong enough prior to distinguish subject body from subject-attached scene elements. The B-test #2 finding that "scene-prior is load-bearing" (V4 spec §8.1) forced V4 to render L2 WITH scene context (cup, table edge, chair fragment), and the cutout step then could not surgically remove only the scene without nicking the body. Pearl_Research evaluated SOTA replacements (research doc §2.1–§2.4): ToonOut (BiRefNet anime FT, MIT, 2025-09) claims 99.0% pixel accuracy on character-with-prop scenes vs ~77% baseline — a real improvement, deployed in V5's Phase 1 fallback path (§12). But cutout precision alone does NOT solve root cause B.

- **Coordinate-system mismatch (root cause B):** L0 and L2 are independent Qwen renders with no shared scene geometry. L0's "table at the lower-left" and L2's "character seated at a table" are produced by different sampling runs of the same model — the model produces a plausible scene in each, but the implicit table position in L2's *seated* pose does not align with L0's *table* position. The composite paste-bbox (`subject_placement_bbox`) is a percent-of-canvas heuristic that ignores both renders' internal geometry. Result: subject floats above L0's bottom edge, or sits at the wrong height relative to L0's table. **No cutout solves this.** Only a unified-render architecture does.

V5 collapses both root causes into a single dispatch where the model produces all layers together with consistent internal geometry, then decomposes them into separable RGBA channels.

## 5. Model file requirements

V5 requires three model files in Pearl Star's ComfyUI:

| Role | File | Size | Source | Notes |
|---|---|---|---|---|
| Text encoder | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | ~7 GB | `Comfy-Org/HunyuanVideo_1.5_repackaged/split_files/text_encoders/` | Reused from V4 base Qwen-Image; already on Pearl Star |
| Diffusion (decompose) | `qwen_image_layered_fp8mixed.safetensors` | 20.5 GB | `Comfy-Org/Qwen-Image-Layered_ComfyUI/split_files/diffusion_models/` | NEW for V5. Public, no auth required; HF cas-bridge throttle observed at ~24–46 KB/s on Pearl Star WAN — full download takes hours to days depending on the daily throttle |
| VAE | `qwen_image_layered_vae.safetensors` | 254 MB | `Comfy-Org/Qwen-Image-Layered_ComfyUI/split_files/vae/` | NEW for V5 |

**License:** Qwen-Image-Layered Apache-2.0 (Comfy-Org repackage); Qwen2.5-VL Apache-2.0. Commercial-clean per Phoenix tier policy.

**VRAM target:** RTX 5070 Ti 16 GB. fp8mixed claims fit in 24 GB; 16 GB fit is empirically untested as of v1.0.0 spec landing. See §11 risk #1. The feasibility test driver (`scripts/manga/v5_qwen_layered_feasibility.py`) is the gate that clears or rejects this assumption. If it OOMs at 16 GB, fallback options are (in order): (a) UNETLoader weight_dtype="fp8_e4m3fn" CPU offload; (b) reduce default panel resolution from 1024×1024 to 640×640; (c) Phase 1 ToonOut interim (§12); (d) escalate to operator.

## 6. Workflow JSON contract

Committed at `scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json` (V5 PR `826e88d6e`). 11 nodes:

```
UNETLoader(37) → ModelSamplingAuraFlow(40) → KSampler(44).model
CLIPLoader(38) → CLIPTextEncode(41 pos, 42 neg) → KSampler(44).positive/negative
EmptyQwenImageLayeredLatentImage(43) → KSampler(44).latent_image
KSampler(44) → LatentCutToBatch(45) → VAEDecode(46) → SaveImage(47)
                                       VAELoader(39) ─┘
```

**Default parameters (V5 baseline; per-archetype overrides allowed):**

| Parameter | Default | Rationale |
|---|---|---|
| width × height | 1024 × 1024 | Manga-panel-equivalent; downstream resize for webtoon vertical formats |
| layers | 2 | Default = subject + background. 3-layer mode (subject / mid-objects / background) is per-archetype opt-in (§7) |
| steps | 50 | Alibaba minimum recommendation for Qwen-Image-Layered |
| cfg | 4.0 | Alibaba recommendation |
| sampler_name | euler | Alibaba template default |
| scheduler | simple | Alibaba template default |
| ModelSamplingAuraFlow.shift | 1.0 | Required pre-processor for the layered model |
| LatentCutToBatch.axis | "t" | Cuts the multi-layer latent across the time axis into a batch dimension for per-layer VAE decode |

**Substitution placeholders:** `{{positive_prompt}}` and `{{negative_prompt}}` in the `CLIPTextEncode` nodes are filled by the V5 orchestrator (§8) per panel.

## 7. Layer semantics

Qwen-Image-Layered's `EmptyQwenImageLayeredLatentImage` node accepts a `layers: int` parameter. Output of the workflow is `layers × batch_size` RGBA images via `LatentCutToBatch → VAEDecode → SaveImage`.

| Mode | layers | Layer ordering (per Alibaba doc + ComfyUI template) | Use case |
|---|---|---|---|
| **2-layer (V5 default)** | 2 | layer 0: foreground subject (RGBA, alpha-cut); layer 1: background scene (RGB) | All iyashikei archetypes; iyashikei has the cleanest "subject + ambient scene" structure |
| **3-layer (opt-in per archetype)** | 3 | layer 0: subject (RGBA); layer 1: mid-objects (RGBA — cup, phone, succulent); layer 2: background (RGB) | Archetypes with explicit named props in `prop_state` that need independent compositing — e.g., `chest_breath_micro` (cup + phone visible on table), `hand_table_micro` (cup wrapped, phone face_up_notification) |
| **N-layer (experimental, deferred to V5.1+)** | 4+ | Per-character-element decomposition (face / hair / clothing / hands / etc.) — see-through SIGGRAPH 2026 paper | Multi-character or fine-grained pose-edit workflows; not part of V5.0 |

**V5.0 ships with 2-layer default.** 3-layer opt-in is per-archetype via `layer_render_contract.V5_layered_decompose.layers: 3` in `iyashikei.yaml` (schema extension to be added in V5 orchestrator commit).

## 8. V5 orchestrator (`scripts/manga/render_v5_episode.py`) — to be authored after spec lands

The V5 orchestrator replaces `scripts/manga/render_v4_episode.py`'s L0+L2 unique-render manifest with a simpler per-panel dispatch. Architectural shape:

```
for panel in continuity_state(ep_001):
  prompt = contract_to_prompt_compiler(panel)             # reuses V4's compiler unchanged
  layer_paths = dispatch_layered_render(prompt, workflow) # NEW: 1 dispatch, N output images
  composite = recompose_layers(layer_paths, archetype)    # NEW: PIL alpha-blend in layer order
  validate(composite)                                     # reuses V4's validate_layer.py + validate_continuity_invariants.py
  save(composite, panel_id)
```

**Continuity cache:** Per-panel, not per-layer. Cache key = `(panel_id, character_design_hash, scene_state_hash, light_rig_id, prompt_hash, workflow_version)`. Cache hit returns the previously-composed panel; cache miss runs a fresh dispatch.

**No L0+L2 unique-render dedup.** V4's manifest-building step (`build_render_manifest` in `render_v4_episode.py`) is removed. Every panel is its own dispatch.

**Output paths:**
- `artifacts/manga/<series>/panels_v5/<panel_id>/composite.png` — the final composed panel
- `artifacts/manga/<series>/panels_v5/<panel_id>/layer_00.png` — subject RGBA (forensic / re-edit asset)
- `artifacts/manga/<series>/panels_v5/<panel_id>/layer_01.png` — background RGB (forensic / re-edit asset)
- `artifacts/manga/<series>/panels_v5/<panel_id>/_telemetry.json` — dispatch time, VRAM peak, prompt sha256, workflow version

## 9. What carries forward from V4 unchanged

| V4 deliverable | V5 status |
|---|---|
| V4 spec §5 Safe-zone hierarchical contract inheritance (base → framing → subject → genre → archetype_exception) | UNCHANGED. V5 reuses the compiled safe-zone rows; the `subject_placement_bbox` becomes the per-layer paste box in the recompose step. |
| V4 spec §6 Continuity state schema (per-panel YAMLs in `artifacts/manga/<series>/continuity_state/`) | UNCHANGED. V5 reads the same YAMLs; the continuity invariants validator (§6.3) still gates beat-to-beat transitions. |
| V4 spec §7 Per-archetype layer composition maps (`iyashikei.yaml` 19 archetypes) | UNCHANGED contract; V5 adds a `layer_render_contract.V5_layered_decompose` block per archetype (default 2 layers, opt-in 3). |
| V4 spec §5.9 Contract-to-prompt compiler | UNCHANGED. V5 compiles a single full-panel prompt per panel (vs V4's separate L0 prompt + L2 prompt); the compiler is fed the same continuity_state + safe-zone + archetype inputs. |
| V4 spec §12 Validator infrastructure (validate_layer.py, validate_continuity_invariants.py, contract_to_prompt_compiler tests) | UNCHANGED at the class-A gate level. Some V4 gates become advisory in V5 (e.g., `subject_does_not_touch_edge` per-axis logic still applies to the decomposed subject layer). |
| V4 spec §14.F Failure budget & recovery semantics | UNCHANGED. V5 honors per-archetype retry limits + per-episode/series thresholds + halt conditions. |
| V4 spec §15.A.1 Identity lock for L2 | RECAST. V5's "subject layer" is the L2 analog; identity-lock acceptance criteria carry forward but the engine choice may change (PuLID-FLUX-FaceNet remains untested on the layered model; LoRA via ai-toolkit still works). |

## 10. What changes from V4

| V4 component | V5 replacement |
|---|---|
| `scripts/manga/render_v4_episode.py` (L0+L2 unique-render manifest + sequential dispatch + rembg cutout + PIL composite) | `scripts/manga/render_v5_episode.py` (per-panel single dispatch + decompose collection + PIL recompose). To be authored after this spec lands. |
| `scripts/image_generation/comfyui_workflows/qwen_image_no_pulid_manga.json` (single-image Qwen-Image dispatch) | `scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json` (N-layer Qwen-Image-Layered dispatch). Already committed. |
| `apply_cutout()` step using `rembg.new_session("u2net_human_seg" / "isnet-anime" / "birefnet-portrait")` | REMOVED. V5's `LatentCutToBatch` + `VAEDecode` produce already-alpha-cut RGBA per layer. |
| V4 spec §12.3 L2 cutout gates (`rembg_clean_alpha`, `character_extraction_coverage`, `background_bleed_check`) | Recast as V5 layer 0 (subject) gates. Same gate logic, applied to the model-emitted alpha rather than the rembg-emitted alpha. Threshold tuning likely needed; documented as v1.0.1 follow-up. |
| V4 spec §15.A.6 composite-level operator review acceptance | RETAINED but specialized as §11 here. Same ≥18/20 shippability gate; specific applied to `stillness_en_01 ep_001`. |

## 11. V5 acceptance criteria — ACCEPTANCE CRITERIA

V5 ships only after the composite-level operator review passes for `stillness_en_01 ep_001`. This is the V5 analog of V4 spec §15.A.6 (V4's launch blocker that V4 failed at 2/35 = 6%).

**Pass requires all of:**
- All 35 ep_001 panels render via the V5 pipeline (`render_v5_episode.py` → `qwen_image_layered_decompose.json`)
- Per-panel: `validate_layer.py` passes on the recomposed composite (class-A gates green); `validate_continuity_invariants.py` passes against the previous panel's continuity_state
- Operator binary review per panel: "is this a shippable manga panel?" → **≥31 of 35 yes (≥88%)** — relaxed slightly from V4 §15.A.6's 90% threshold because V5 is a first-attempt architectural shift; the gate raises to ≥90% in V5.1
- Operator open-text review surfaces no systemic visual artifact (e.g., "every panel has a halo around the subject seam" would block even if 88% are "shippable")
- Side-by-side comparison against the 35 V4 composites of the same panel_ids — **V5 must be visually better on ≥30 of 35** (vs V4's 2/35 baseline; this is intentionally a low bar because V4 was visibly broken)
- VRAM peak per dispatch logged ≤ 15 GB on Pearl Star RTX 5070 Ti 16 GB (proves the model fit; if peak ≥ 15.5 GB, escalate to fp8 quantization or CPU offload)

**Test path:** `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/v5_acceptance_review/<timestamp>/` — composited panels + filled review template + telemetry JSON.

**Manual gate.** Operator review IS the gate. Composite-pass on class-A validators is necessary but not sufficient.

**Fallback if unmet:** V5 does not ship for `stillness_en_01`. Two routes:
1. Diagnose which panels failed, iterate on prompt templates / archetype layer_render_contract / scene_context_clause, re-dispatch the failing panels, re-review. Per V4 spec §14.F failure budget, max 2 iteration cycles before escalating.
2. If iteration cannot clear the gate (systemic Qwen-Image-Layered failure mode), pivot to Phase 1 ToonOut (§12) as the V5.0 ship and re-attempt full Qwen-Image-Layered in V5.1 with FLUX-Fill + PuLID inpaint (Phase 3 of the research doc).

## 12. Open questions / unresolved risks

These risks are documented for operator awareness; each must clear empirically before V5 ships.

1. **VRAM fit on RTX 5070 Ti 16 GB:** Alibaba's fp8mixed variant claims 24 GB fit. 16 GB is empirically untested. The feasibility test (`v5_qwen_layered_feasibility.py`) is the gate. Mitigation if OOM: weight_dtype="fp8_e4m3fn" CPU offload, then 640px resolution fallback, then Phase 1 pivot.

2. **Identity preservation across decomposed layers:** Qwen-Image-Layered's docs claim semantic preservation across the decompose step, but not validated on a consistent-character episode at scale. The decomposed "Mira layer" of panel 1 may not look like a different person from panel 2's decomposed "Mira layer" — but it might. Mitigation: V4 spec §15.A.1 identity-lock acceptance criteria apply to the V5 subject layer; `qa_face_distance.py` (already in pipeline) checks embedding cosine distance ≤ 0.55 per panel.

3. **Lighting consistency between decomposed layers:** Decomposed subject + decomposed background should share the model's internal lighting model by construction, but seam artifacts at the subject/background boundary may emerge under the soft-shadow conditions iyashikei requires. Mitigation: IC-Light V2 FBC as an optional post-pass relight (research §5.3). Adds 3–5 s per panel on RTX 5070 Ti. Empirical test on Mira required before adopting — IC-Light is photoreal-tuned and may shift anime skin tones (research §9.4).

4. **Layer-decompose precision at character-prop contact:** Qwen-Image-Layered's claim is that the model "knows" where the cup ends and the hand begins; reality may be that contact regions still smear. If 3-layer mode (cup as mid-object layer) is needed to clean this up, we hit V5.1 territory. Mitigation: start with 2-layer default, escalate per-archetype to 3-layer as the operator review surfaces specific failures.

5. **Cache invalidation surface area:** V5 cache keys are per-panel; V4 cached at unique-render granularity. A continuity_state change in panel N propagates to N+1's cache lookup but not to N+2 (assuming archetype isolation). Verify that beat-to-beat micro-changes don't unnecessarily invalidate downstream panels. (Test: change `panel_005.expression_dial` from 0.4 → 0.5; verify only panel_005 cache invalidates.)

6. **HF cas-bridge throttle for model download:** Empirically observed at 24–46 KB/s on Pearl Star WAN, with the 20.5 GB diffusion model taking hours-to-days to download fully. Not a V5-architecture risk, but a deployment-blocker for the feasibility test. Documented as known limitation; Phase 1 ToonOut path (§13) is the operationally faster alternative until the download completes or HF rate-limit lifts.

## 13. Phase 1 ToonOut fallback (interim V4.x improvement while V5 download / VRAM fit clears)

Pearl_Research's three-phase plan (research §8) provides a faster interim path that improves V4 composites without architectural change:

**ToonOut (BiRefNet fine-tuned on anime, MIT, 2025-09):**
- Paper: arxiv 2509.06839
- GitHub: `MatteoKartoon/BiRefNet`
- Dataset: 1,228 hand-annotated anime images, "Action" category includes characters-with-held-props
- Reported metrics: 99.0% pixel accuracy on character-with-prop scenes (vs ~77% baseline for `isnet-anime` and `u2net_human_seg`)
- Inference: ~0.5–1.5 s at 1024×1024 on RTX 5070 Ti; CPU-feasible on Apple Silicon (~3–8 s)

**Integration as V4.x patch:**
1. Add `cutout_engine: "toonout"` option to the `cutout_policy` block in `iyashikei.yaml` archetypes.
2. In `scripts/manga/render_v4_episode.py:354` (`apply_cutout` function), branch on `cutout_engine`: if `"toonout"`, use BiRefNet inference with ToonOut checkpoint instead of `rembg.new_session(...)`.
3. Run side-by-side on the 4 existing `v4_b_test` L2 renders (`ep001_006_L2_v4btest2_face_only.png` etc.). Operator side-by-side review.
4. If chair/stove fragments visibly disappear: ship V4.1 with ToonOut as the default `cutout_engine` for iyashikei archetypes. Operator review the V4.1 ep_001 35-panel composite re-run.
5. If fragments persist OR the "subject floats above bottom" problem (root cause B) is the dominant failure mode: ToonOut alone is insufficient → V5 is the only path → wait for the Qwen-Image-Layered download.

**Phase 1 is an operational improvement of V4, not a V5 component.** V5 supersedes both V4 and V4.1+ToonOut. Phase 1 exists because the V5 model download has a multi-day ETA on Pearl Star and the operator may want V4.1 ToonOut as an interim ship for ep_001 while the V5 download completes.

**Operator decision required:** confirm whether to start Phase 1 ToonOut in parallel with the V5 download wait (1–2 days), or stand down on Phase 1 and wait exclusively for V5. Per `docs/PEARL_OPERATOR_PROXY_SPEC.md` decision-routing, this is an in-envelope routing decision (architectural pivot scope already in V5 scope; Phase 1 is an interim implementation of the same scope).

---

## 14. Cross-references

**Authority chain (this spec inherits from / depends on):**
- `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7 (sibling V4 spec — contract scaffolding §5/§6/§5.9/§12/§14.F that V5 reuses unchanged; §17 deprecation marker pointing here)
- `artifacts/research/manga_layer_compositing_research_2026-05-20.md` (Pearl_Research findings — the empirical basis for the V4→V5 pivot)
- `config/manga/panel_templates/iyashikei.yaml` (19 archetypes — V5 extends `layer_render_contract` with V5_layered_decompose block)
- `config/source_of_truth/manga_profiles/series/stillness_en_01.yaml` (target series for V5 acceptance review)
- `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_001/*.yaml` (35 panel continuity states — V5 reads these unchanged)

**This spec is referenced by (planned):**
- `scripts/manga/render_v5_episode.py` (V5 orchestrator — to be authored)
- `scripts/image_generation/comfyui_workflows/qwen_image_layered_decompose.json` (V5 workflow — already committed at V5 PR `826e88d6e`)
- `scripts/manga/v5_qwen_layered_feasibility.py` (V5 feasibility test driver — already committed)
- `config/manga/panel_templates/<genre>.yaml` (V5_layered_decompose block extension — pending)

**Version history:**
- **v1.0.0 (2026-05-20):** Initial standalone V5 spec. Content factored out of `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §16 (was 200+ lines in V4 spec → 15-line deprecation marker pointing here) per V4 spec §15.C.6 doc-split commitment.
- **v1.0.1 (2026-05-21):** Runtime-empirical amendments after ep_001 end-to-end dispatch on Pearl Star (35/35 success, 10.76 GB peak VRAM, 3h 39m elapsed):
  - **§6 LatentCutToBatch input schema:** the workflow JSON uses `dim` + `slice_size` (NOT `axis` + `size` as v1.0.0 stated). ComfyUI rejects the wrong field names with HTTP 400 `required_input_missing`. Fix landed in PR #1267.
  - **§7 Layer output convention:** Qwen-Image-Layered with `layers=N` actually emits **N+1 outputs** in SaveImage order: layer_00 = composite full panel (RGBA, 100% opaque, ready-to-use as the panel); layer_01 = background-only (RGBA, 100% opaque, subject region inpainted); layer_02..N = decomposed component layers (RGBA, alpha-cut subject). v1.0.0 spec anticipated `N` outputs requiring PIL recompose; the model is more capable than spec described. Fix landed in PR #1267 (orchestrator copies layer_00 directly as composite; recompose path retained as fallback).
  - **§5 + new risk #7 — HF cas-bridge per-connection throttle:** Standard `hf download` single-stream stalls on Pearl Star at ~24-46 KB/s. Cloudflare WAN speedtest confirms ~90 KB/s peak single-stream. HF cas-bridge throttles per-connection, not per-IP — 16 parallel curl byte-range workers achieve ~12.9 MB/s aggregate. Productionized at `scripts/utils/parallel_hf_download.py`. Use this for all multi-GB HF model pulls on Pearl Star.
  - **§13 + new risk #8 — RTX 5070 Ti torch CUDA compatibility for Phase 1 ToonOut:** `torch==2.5.1` prebuilt wheels lack Blackwell SM 12.0 CUDA kernels → `RuntimeError: CUDA error: no kernel image is available for execution on the device`. Phase 1 ToonOut runs on CPU (~3-8s/image per research §2.1) until `torch 2.6+` ships or operator pulls a torch nightly with cu128 / Blackwell support. The loader at `scripts/manga/manga_cutout_toonout.py` probes CUDA + falls back to CPU automatically (env var `TOONOUT_DEVICE=cpu` or `=cuda` overrides). Fix landed in PR #1268. Does NOT affect V5 — ComfyUI on Pearl Star uses its own torch which has Blackwell support.
  - **§11 acceptance — empirical evidence:** ep_001 35-panel V5 dispatch on Pearl Star: 35/35 success, 33+1 retry + 1 cache, validation_pass=33 (smoke + retry not gate-checked because already-cached), peak_vram=10.76 GB (under §11 ≤15 GB ceiling). Composites at `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v5_qwen/ep_001/`. Operator §11 visual review is the remaining gate.

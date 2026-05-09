# RunComfy Workflow Compatibility Audit - 2026-05-09

Project: PRJ-DUAL-PATH-IMAGE-RENDER-V1  
Workstream: ws_runcomfy_workflow_compatibility_audit_20260509  
Issue context: IMG-RENDER-DUAL-PATH-V1-01 (#992)  
Subsystem: integrations  
Scope: `scripts/image_generation/comfyui_workflows/*.json`  
Method: static JSON inspection only. No RunComfy API calls, no model downloads, no workflow execution, no credential access.

## RunComfy Compatibility Basis

RunComfy documents custom workflow import, Cloud Save, and serverless deployment for ComfyUI workflows. Their custom workflow docs state that Cloud Save packages the workflow runtime, including drivers, libraries, custom nodes, models, and dependencies, and that RunComfy keeps workflows in sync with official ComfyUI versions: <https://docs.runcomfy.com/custom-workflows>.

RunComfy documents custom node installation through ComfyUI Manager, including "Install Missing Custom Nodes" and manual install/search flows: <https://docs.runcomfy.com/custom-workflows#add-custom-nodes>. RunComfy node catalog pages also document the specific standard/custom nodes used here, including `CheckpointLoaderSimple`, `IPAdapterUnifiedLoader`, `IPAdapterAdvanced`, `PulidModelLoader`, `ApplyPulid`, and `ApplyPulidFlux`:

- `CheckpointLoaderSimple`: <https://www.runcomfy.com/comfyui-nodes/ComfyUI/CheckpointLoaderSimple>
- `IPAdapterUnifiedLoader`: <https://runcomfy.com/comfyui-nodes/ComfyUI_IPAdapter_plus/IPAdapterUnifiedLoader>
- `IPAdapterAdvanced`: <https://www.runcomfy.com/comfyui-nodes/ComfyUI_IPAdapter_plus/IPAdapterAdvanced>
- `PulidModelLoader`: <https://www.runcomfy.com/comfyui-nodes/PuLID_ComfyUI/PulidModelLoader>
- `ApplyPulid`: <https://www.runcomfy.com/comfyui-nodes/PuLID_ComfyUI/ApplyPulid>
- `ApplyPulidFlux`: <https://www.runcomfy.com/comfyui-nodes/ComfyUI_PuLID_Flux_ll/apply-pulid-flux>

RunComfy documents model upload/download support for `models/checkpoints` and `models/loras`, including local upload through the Assets file browser and URL download from Civitai, Hugging Face, and Google Drive: <https://docs.runcomfy.com/custom-workflows#add-models> and <https://comfyui-guides.runcomfy.com/ultimate-comfyui-how-tos-a-runcomfy-guide/how-to-upload-files-in-runcomfy>. RunComfy also documents Qwen Image LoRA workflows via their pipeline-aligned `RCQwenImage` node, which is important for Qwen-specific inference matching: <https://www.runcomfy.com/comfyui-workflows/qwen-image-ai-toolkit-lora-inference-in-comfyui-training-matched-results>.

Verdict meanings:

- `supported`: no known RunComfy environment blocker; standard nodes or documented RunComfy catalog nodes; model dependency is preloaded, uploadable, or downloadable through documented RunComfy flows.
- `conditional`: feasible on RunComfy but needs manual Cloud Save setup, exact custom node/asset mapping, checkpoint upload, or workflow replacement before production use.
- `not_supported`: static audit found a dependency that RunComfy docs do not provide a viable install/upload/path for.

## Summary

Workflow count audited: 9

| Verdict | Count |
|---|---:|
| supported | 4 |
| conditional | 5 |
| not_supported | 0 |

No active workflow JSON contains a LoRA loader node. The two genre-LoRA files are placeholders with LoRA cross-test skip notes only; their Civitai LoRAs are not wired into runnable graph nodes.

## Per-Workflow Compatibility Matrix

| Workflow | Node dependency check | Checkpoint / model file check | LoRA check | Phoenix-side preprocessing | Verdict | Estimated migration effort |
|---|---|---|---|---|---|---|
| `animagine_xl_dark_fantasy.json` | No nodes. Placeholder-only JSON. | None. | Notes reference DARK FANTASY XL Civitai LoRA as skipped; no LoRA loader is wired. RunComfy can upload LoRAs, but this workflow has nothing to run. | None. | conditional | Low: replace placeholder with real graph and upload/link LoRA if this genre is reactivated. |
| `animagine_xl_mecha.json` | No nodes. Placeholder-only JSON. | None. | Notes reference Super Robot Diffusion XL Civitai LoRA as skipped; no LoRA loader is wired. RunComfy can upload LoRAs, but this workflow has nothing to run. | None. | conditional | Low: replace placeholder with real graph and upload/link LoRA if this genre is reactivated. |
| `animagine_xl_txt2img_manga.json` | Core nodes plus `PuLID_ComfyUI` nodes: `PulidModelLoader`, `PulidEvaClipLoader`, `PulidInsightFaceLoader`, `ApplyPulid`. RunComfy documents `PuLID_ComfyUI` install/catalog support for `PulidModelLoader` and `ApplyPulid`; exact EVA/InsightFace loader availability should be verified in a Cloud Save session. | `animagine_xl_4_0.safetensors` must be present under checkpoints. RunComfy supports checkpoint upload/download; no static evidence that the exact Animagine filename is preloaded. `ip-adapter_pulid_sdxl_fp16.safetensors` must be present in the PuLID model folder. | No LoRA loader. | Template placeholders: `{{positive_prompt}}`, `{{negative_prompt}}`, `{{reference_image}}`. Requires Phoenix caller to substitute prompts and reference image before submission. | conditional | Medium: upload/checkpoint-map Animagine 4.0 and PuLID model, install/Cloud Save PuLID nodes, verify exact loader names. |
| `flux_img2img_manga.json` | Core ComfyUI nodes only: `CheckpointLoaderSimple`, `LoadImage`, `ImageScale`, `VAEEncode`, `CLIPTextEncode`, `KSampler`, `VAEDecode`, `SaveImage`. | `flux1-dev-fp8.safetensors`. RunComfy FLUX docs state FLUX models are preloaded as `flux/flux-dev` and `flux/flux-schnell`; exact Phoenix filename may need remapping or upload. | No LoRA loader. | `manga_teacher_batch.py` base64-injects `{{input_image}}`, prompt text, and seed. | supported | Low: map the checkpoint selector/name to the RunComfy FLUX dev asset or upload the exact fp8 file. |
| `flux_ip_adapter_manga.json` | Core nodes plus `ComfyUI_IPAdapter_plus`: `IPAdapterUnifiedLoader`, `IPAdapterAdvanced`. Both are documented in RunComfy's node catalog and installable via ComfyUI Manager. | `flux1-dev-fp8.safetensors`; same FLUX dev mapping/upload note as above. IPAdapter model assets must exist in the session. | No LoRA loader. | `manga_teacher_batch.py` base64-injects `{{input_image}}`, prompt text, and seed. | supported | Medium-low: install/verify IPAdapter Plus and FaceID assets, map/upload FLUX dev checkpoint, Cloud Save. |
| `flux_txt2img_manga.json` | Core ComfyUI nodes only: `CheckpointLoaderSimple`, `CLIPTextEncode`, `EmptyLatentImage`, `KSampler`, `VAEDecode`, `SaveImage`. | `flux1-schnell-fp8.safetensors`. RunComfy FLUX docs state `flux/flux-schnell` is preloaded; exact Phoenix filename may need remapping or upload. | No LoRA loader. | Used by local/Phoenix scripts that substitute prompt text, geometry, seed, steps, and CFG. | supported | Low: map the checkpoint selector/name and Cloud Save. |
| `flux_txt2img_manga_pulid.json` | Core nodes plus `ApplyPulidFlux` and `PulidFluxFaceNetLoader`. RunComfy documents `ApplyPulidFlux` under `ComfyUI_PuLID_Flux_ll`; exact `PulidFluxFaceNetLoader` is not shown in the fetched RunComfy node page and should be verified/installed from the same extension in session. | `flux1-schnell-fp8.safetensors`; RunComfy FLUX Schnell is preloaded but exact filename may need remapping. PuLID Flux/FaceNet assets must be installed with the extension. | No LoRA loader. | Template placeholders: `{{positive_prompt}}`, `{{negative_prompt}}`, `{{reference_image}}`. Requires Phoenix caller to provide reference image. | conditional | Medium: install/verify `ComfyUI_PuLID_Flux_ll` FaceNet path, map/upload FLUX Schnell, Cloud Save. |
| `flux_video_bank.json` | Core ComfyUI nodes only: `CheckpointLoaderSimple`, `CLIPTextEncode`, `EmptyLatentImage`, `KSampler`, `VAEDecode`, `SaveImage`. | `flux1-schnell-fp8.safetensors`; RunComfy FLUX Schnell is documented as preloaded, exact filename may need remapping. | No LoRA loader. | `runcomfy_batch.py` and `generate_kdp_all_formats.py` substitute prompt, seed, and filename prefix before submission. | supported | Low: map checkpoint selector/name and Cloud Save or deploy against an existing FLUX Schnell deployment. |
| `qwen_image_txt2img_manga.json` | Core sampler graph plus `ApplyPulidFlux` and `PulidFluxFaceNetLoader`. RunComfy supports Qwen Image workflows, but their docs recommend `RCQwenImage` for pipeline-aligned Qwen Image inference and LoRA injection rather than generic sampler reconstruction. | `qwen_image_2.0.safetensors` must be uploaded or replaced by a RunComfy Qwen Image workflow/model path. PuLID Flux/FaceNet assets also required. | No LoRA loader in this Phoenix graph. If Qwen LoRAs are added later, RunComfy's documented Qwen path is `RCQwenImage` with `lora_path`/`lora_scale`, not generic loader stacking. | Template placeholders: `{{positive_prompt}}`, `{{negative_prompt}}`, `{{reference_image}}`. Requires Phoenix caller to provide reference image or strip optional PuLID path for pure-text mode. | conditional | Medium-high: decide whether to migrate to RunComfy `RCQwenImage` workflow, upload/map Qwen checkpoint, and verify PuLID FaceNet compatibility. |

## Dependency Detail

### Custom Node Dependencies

Supported/documented nodes:

- Core ComfyUI nodes: `CheckpointLoaderSimple`, `CLIPTextEncode`, `EmptyLatentImage`, `KSampler`, `LoadImage`, `ImageScale`, `VAEEncode`, `VAEDecode`, `SaveImage`.
- `ComfyUI_IPAdapter_plus`: `IPAdapterUnifiedLoader`, `IPAdapterAdvanced`.
- `PuLID_ComfyUI`: `PulidModelLoader`, `PulidEvaClipLoader`, `PulidInsightFaceLoader`, `ApplyPulid` with exact RunComfy catalog confirmation for `PulidModelLoader` and `ApplyPulid`.
- `ComfyUI_PuLID_Flux_ll`: `ApplyPulidFlux` documented; `PulidFluxFaceNetLoader` requires in-session verification because the exact FaceNet loader was not present in the fetched RunComfy catalog page.

### LoRA Dependencies

No workflow has an active LoRA loader node. RunComfy supports `models/loras` upload and URL download, so future LoRA-wired Phoenix workflows are compatible in principle. Current placeholder files are conditional because they contain skipped LoRA notes but no executable graph.

### Checkpoint Dependencies

RunComfy supports custom checkpoint upload/download via `models/checkpoints`, and documents FLUX preloads:

- `flux1-schnell-fp8.safetensors`: supported with likely name remap to RunComfy `flux/flux-schnell` or local upload.
- `flux1-dev-fp8.safetensors`: supported with likely name remap to RunComfy `flux/flux-dev` or local upload.
- `animagine_xl_4_0.safetensors`: conditional only because exact preload was not proven; upload/download is documented.
- `qwen_image_2.0.safetensors`: conditional because RunComfy supports Qwen Image workflows, but their documented production path uses `RCQwenImage` pipeline-specific inference rather than this generic `CheckpointLoaderSimple` graph.

### Phoenix-Side Preprocessing

Phoenix preprocessing remains outside the ComfyUI workflow JSON and must be preserved for migration:

- `scripts/image_generation/manga_teacher_batch.py` deep-copies workflow templates, substitutes prompt placeholders, base64-encodes input images, and writes seeds.
- `scripts/image_generation/runcomfy_batch.py` loads workflow JSON and submits `{"workflow": workflow}` to RunComfy deployments; this audit did not call it.
- `scripts/image_generation/generate_teacher_showcase_triptych.py` mutates txt2img geometry, seed, steps, CFG, sampler, and scheduler for local ComfyUI.
- `scripts/image_generation/generate_stillness_press_image_bank.py` owns brand/teacher prompt construction, dimensions, QC, and local ComfyUI submission.

## Overall Verdict

RunComfy is compatible with the Phoenix workflow portfolio at the environment level: all active dependency classes have either documented RunComfy support, documented install/upload paths, or a clear conditional migration path. The safe migration order is:

1. Cloud Save `flux_txt2img_manga.json`, `flux_video_bank.json`, and `flux_img2img_manga.json` after checkpoint name mapping.
2. Cloud Save `flux_ip_adapter_manga.json` after IPAdapter Plus and FaceID asset verification.
3. Verify PuLID SDXL/FLUX exact loader names in a no-spend RunComfy session before promoting Animagine and PuLID workflows.
4. Prefer a RunComfy `RCQwenImage` workflow for Qwen Image production parity instead of relying on the current generic sampler graph.

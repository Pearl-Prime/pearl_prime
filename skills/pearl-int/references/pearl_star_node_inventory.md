# Pearl Star — ComfyUI custom-nodes + checkpoints inventory

**Date:** 2026-05-07
**Owner:** Pearl_Int (records); Pearl_Dev (uses)
**Authority:** Phase B install runbook at `docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md`

This is the canonical record of what's installed on Pearl Star and what each install supports. Update this file whenever Pearl Star nodes change.

## Snapshot (verified 2026-05-07 post Phase B install bringup; Pearl_Int)

```
Host:         pearlstar (alias: pearl_star)
OS:           Linux 6.17.0-22-generic, Ubuntu 24.04
GPU:          NVIDIA GeForce RTX 5070 Ti (16.3 GiB VRAM)
Python:       3.12.3
ComfyUI:      v0.18.1 at ~/phoenix_server/ComfyUI/
Venv:         ~/phoenix_server/ComfyUI/venv/
torch:        2.11.0+cu130 (UNCHANGED through Phase B install — workaround successful)
```

## Custom nodes — installed post Phase B (2026-05-07)

```
~/phoenix_server/ComfyUI/custom_nodes/
├── HandFixer/                              # operator-installed; hand anatomy fixer
├── example_node.py.example                 # ComfyUI default
├── websocket_image_save.py                 # ComfyUI default
├── ComfyUI_PuLID_Flux_ll/  @ 7c7362b       # FLUX-PuLID + FaceNet (commercial-clean)
│                                           #   Apache 2.0
│                                           #   USE: PulidFluxFaceNetLoader (NOT InsightFaceLoader)
│                                           #   facenet-pytorch installed via --no-deps
│                                           #   to preserve torch 2.11.0
└── PuLID_ComfyUI/         @ 93e0c4c        # cubiq's SDXL/Animagine PuLID path
                                            #   Apache 2.0
                                            #   USE: ApplyPulid (FaceNet path at runtime)
```

Install transcript: [`artifacts/qa/pearl_star_v2_install_log_2026-05-07.md`](../../artifacts/qa/pearl_star_v2_install_log_2026-05-07.md).

### Python packages added by the PuLID install

```
facenet-pytorch  2.6.0   # MIT (Timothy Esler); installed --no-deps to skip torch<2.3 pin
facexlib         0.3.0
insightface      0.7.3   # transitive code-load dep; AntelopeV2 weights NEVER downloaded
                          #   because workflows call PulidFluxFaceNetLoader exclusively
onnxruntime      1.25.1
onnxruntime-gpu  1.25.1
timm             1.0.26
```

`torch 2.11.0+cu130` unchanged. Verified via `import torch; print(torch.__version__)` after each install step.

## Checkpoints — post Phase B (Path B' = downloads deferred to HF_TOKEN session)

```
~/phoenix_server/ComfyUI/models/checkpoints/
├── flux1-schnell-fp8.safetensors           # 17 GiB; Apache 2.0; brand-2 V1 ship base; now also FLUX-PuLID path
└── flux1-dev-fp8.safetensors               # 1.5 MB STUB (DEPRECATED; non-commercial license; safe to leave)
```

**Deferred to HF_TOKEN download session** (Pearl Star → HF CDN throttled to ~50 KB/s without auth — discovered during Phase B install attempt):

| Component | Size | License | When |
|---|---|---|---|
| `animagine-xl-4.0.safetensors` (canonical single file) | 6.94 GB | openrail++ | Path B': operator generates HF_TOKEN, adds to Keychain via `security add-generic-password -s phoenix-omega -a HF_TOKEN -w <token> -U`, runs `hf download cagliostrolab/animagine-xl-4.0 animagine-xl-4.0.safetensors --local-dir .` — should complete in 2-20 min on the authenticated rate |
| Qwen-Image (split-files via Comfy-Org repackage: `qwen_image_2512_fp8_e4m3fn.safetensors` + `qwen_2.5_vl_7b_fp8_scaled.safetensors` + `qwen_image_vae.safetensors`) | ~30 GB total | apache-2.0 | Same focused session OR a later one. Note: the workflow JSON `qwen_image_txt2img_manga.json` (PR #926) currently uses `CheckpointLoaderSimple` (single-file convention); Comfy-Org's split-files format requires `UNETLoader` + `DualCLIPLoader` + `VAELoader` — small Pearl_Dev workflow JSON edit bundled with this download. |

The engine router's `available_engines` parameter (added in this PR) gates routing: until the downloads land, all V2 routes degrade to FLUX-schnell + PuLID-FaceNet. After downloads land, the runtime caller sets `available_engines={ENGINE_FLUX_SCHNELL, ENGINE_ANIMAGINE}` (and later also `ENGINE_QWEN`) to enable full V2 routing.

## License posture (post Phase B)

All commercial-clean. No FLUX-dev / Pony / NoobAI / Illustrious / InstantID-AntelopeV2. The `lldacing` PuLID install pulls `insightface` as a transitive dependency for code-loading, but Phoenix's workflows only call `PulidFluxFaceNetLoader` so the AntelopeV2 weights are never downloaded, never used. Pearl_Int verifies this at workflow-definition time.

## Phase C+ planned additions

Phase C will add (in order):
- `ComfyUI_LayerStyle` (MIT; halftone post-processing layer)
- `animeoutlineV4` LoRA (Civitai 16014 family; license-verify per page)
- `lineart-anime-redmond` LoRA (universal manga lineart helper)
- `H4LFT0N3_XL` OR `sh-halftone-v3` halftone LoRA (operator picks; license-verify)
- 12-14 character LoRAs (trained on Pearl Star via ai-toolkit; outputs to `~/phoenix_server/ComfyUI/models/loras/character/`)
- 12 brand-style LoRAs (same)
- `ColorManga` Qwen LoRA (Civitai 1985245; for color webtoon path)
- WD-EVA02-large-tagger-v3 (Phase E QA tagger)

This file gets updated as each Phase lands.

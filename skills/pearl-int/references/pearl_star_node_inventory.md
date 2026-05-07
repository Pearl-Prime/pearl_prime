# Pearl Star — ComfyUI custom-nodes + checkpoints inventory

**Date:** 2026-05-07
**Owner:** Pearl_Int (records); Pearl_Dev (uses)
**Authority:** Phase B install runbook at `docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md`

This is the canonical record of what's installed on Pearl Star and what each install supports. Update this file whenever Pearl Star nodes change.

## Snapshot (verified 2026-05-07 by Pearl_Dev Phase B preflight)

```
Host:       pearlstar (alias: pearl_star)
OS:         Linux 6.17.0-22-generic, Ubuntu 24.04
GPU:        NVIDIA GeForce RTX 5070 Ti (16.3 GiB VRAM)
Python:     3.12.3
ComfyUI:    v0.18.1 at ~/phoenix_server/ComfyUI/
Venv:       ~/phoenix_server/ComfyUI/venv/
torch:      2.11.0
```

## Custom nodes — currently installed

```
~/phoenix_server/ComfyUI/custom_nodes/
├── HandFixer/                          # operator-installed; hand anatomy fixer
├── example_node.py.example             # ComfyUI default
└── websocket_image_save.py             # ComfyUI default
```

## Custom nodes — Phase B install plan (gated on operator-supervised execution)

```
~/phoenix_server/ComfyUI/custom_nodes/  (POST Phase B install runbook)
├── ComfyUI_PuLID_Flux_ll/              # NEW: FLUX-PuLID + FaceNet (commercial-clean)
│                                       #   Apache 2.0 + facenet-pytorch + VGGFace2 weights
│                                       #   USE: PulidFluxFaceNetLoader (NOT InsightFaceLoader)
│                                       #   torch CONFLICT: requires --no-deps install of
│                                       #   facenet-pytorch to preserve torch 2.11.0
└── PuLID_ComfyUI/                      # NEW: SDXL/Animagine PuLID path (cubiq)
                                        #   Apache 2.0; lighter requirements than lldacing
                                        #   USE: ApplyPulid (verify FaceNet path at runtime)
```

Install procedure: `docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md`.

## Checkpoints — currently installed

```
~/phoenix_server/ComfyUI/models/checkpoints/
├── flux1-schnell-fp8.safetensors           # 17 GiB; Apache 2.0; brand-2 V1 ship base
└── flux1-dev-fp8.safetensors               # 1.5 MB STUB (real model never downloaded)
                                            #   DEPRECATED — license-blocked per V2 cap entry;
                                            #   stub safe to leave in place
```

## Checkpoints — Phase B install plan

```
~/phoenix_server/ComfyUI/models/checkpoints/  (POST Phase B)
├── flux1-schnell-fp8.safetensors          # unchanged; FLUX path
├── qwen_image_2.0.safetensors             # NEW; ~20 GiB; Apache 2.0; primary V2 base
└── animagine_xl_4_0.safetensors           # NEW; ~6 GiB; RAIL++-M; secondary V2 base
```

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

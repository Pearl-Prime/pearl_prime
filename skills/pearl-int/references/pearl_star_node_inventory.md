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
├── flux1-schnell-fp8.safetensors           # 17 GiB; Apache 2.0; brand-2 V1 ship base; also FLUX-PuLID path
├── flux1-dev-fp8.safetensors               # 17 GiB; landed 2026-05-18 (verified 2026-06-02 Pearl_Int);
│                                           #   H1=A canonical config (28 steps / cfg 3.5 / dpmpp_2m / karras)
│                                           #   non-commercial license — operator-cleared for canonical manga
│                                           #   panel work per feedback_campaign_h1_h2_decisions
└── animagine-xl-4.0.safetensors            # 6.94 GiB; openrail++; V2 shojo/iyashikei path
```

> **2026-06-02 correction (Pearl_Int):** an earlier revision of this section listed `flux1-dev-fp8.safetensors` as a 1.5 MB stub deferred to a future HF_TOKEN session. That landed on 2026-05-18; the file is the real 17 GiB checkpoint. The H1=A path is unblocked.

**Qwen-Image (still deferred to HF_TOKEN download session)** — Pearl Star → HF CDN throttled to ~50 KB/s without auth:

| Component | Size | License | When |
|---|---|---|---|
| Qwen-Image (split-files via Comfy-Org repackage: `qwen_image_2512_fp8_e4m3fn.safetensors` + `qwen_2.5_vl_7b_fp8_scaled.safetensors` + `qwen_image_vae.safetensors`) | ~30 GB total | apache-2.0 | HF_TOKEN session. The workflow JSON `qwen_image_txt2img_manga.json` (PR #926) currently uses `CheckpointLoaderSimple` (single-file convention); Comfy-Org's split-files format requires `UNETLoader` + `DualCLIPLoader` + `VAELoader` — small Pearl_Dev workflow JSON edit bundled with this download. |

The engine router's `available_engines` parameter gates routing: with FLUX-dev + Animagine both present, V2 routes for shojo/iyashikei (Animagine) and FLUX-dev paths are live; Qwen-Image routes for seinen/josei still degrade to FLUX-schnell + PuLID-FaceNet until the Qwen download lands.

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

---

## Pearl Star autonomous self-monitoring (verified 2026-06-02; Pearl_Int)

Long-running orchestrator runs on Pearl Star (e.g., 5-day bulk renders) need two capabilities that don't ship in the base Ubuntu install: a GitHub CLI for progress commits and an `rclone` remote for sample uploads to R2. Both are installed user-local on Pearl Star (no `sudo` available) and verified end-to-end.

### Installed binaries (user-local, no `sudo` required)

```
~/.local/bin/gh        # v2.45.0 — tarball install from https://github.com/cli/cli/releases
~/.local/bin/rclone    # v1.69.0 — zip install from https://downloads.rclone.org/
~/.bashrc              # exports PATH=$HOME/.local/bin:$PATH (idempotent — checked before append)
```

### `gh` auth state

- **Account:** `Ahjan108`
- **Storage:** `/home/ahjan108/.config/gh/hosts.yml` (token only on disk after `gh auth login --with-token`)
- **Scopes:** `gist`, `read:org`, `repo`, `workflow` ✅ (sufficient for progress commits + PR list)
- **Origin of token:** operator's local Keychain (`security find-generic-password -s phoenix-omega -a GH_TOKEN -w`). The same token now lives in Keychain under both `GH_TOKEN` and `GITHUB_TOKEN`.

### `rclone` R2 remote `r2`

- **Config file:** `~/.config/rclone/rclone.conf`
- **Remote name:** `r2`
- **Provider:** `s3` / `Cloudflare`
- **Endpoint:** EU-jurisdiction host (lives in Keychain as `R2_ENDPOINT` — host hash differs from `R2_ACCOUNT_ID`)
- **Bucket:** `phoenix-omega-artifacts` (existing prefixes: `manga/`, `teacher_showcase/`)
- **Required setting:** `no_check_bucket = true` — the R2 token is bucket-scoped, no account-level `CreateBucket` permission. Without `no_check_bucket`, every upload pre-validates via `CreateBucket` and 403s.

### Verification commands (re-run any time)

```bash
# gh auth
ssh pearl_star '~/.local/bin/gh auth status'
ssh pearl_star 'cd ~/phoenix_omega && ~/.local/bin/gh pr list --limit 1'

# rclone R2 round-trip (writes test/po_smoke_$timestamp.txt, deletes, confirms gone)
ssh pearl_star 'TS=$(date +%s); echo smoke > /tmp/po_smoke_$TS.txt
  ~/.local/bin/rclone copy /tmp/po_smoke_$TS.txt r2:phoenix-omega-artifacts/test/
  ~/.local/bin/rclone ls r2:phoenix-omega-artifacts/test/ | grep po_smoke_$TS
  ~/.local/bin/rclone delete r2:phoenix-omega-artifacts/test/po_smoke_$TS.txt
  rm -f /tmp/po_smoke_$TS.txt'
```

### tmux substitute (no sudo, no install)

Pearl Star does not have `tmux` installed and `sudo apt install tmux` requires the operator's password. For long-running orchestrators, use `nohup … &` plus `disown` instead of a tmux session. The orchestrator log file is the source of truth; monitor via `ssh pearl_star "tail -f <log>"`. Abort via `ssh pearl_star "pkill -f <script-name>"`.

### Setup runbook (full procedure)

See [`docs/runbooks/PEARL_STAR_SETUP_RUNBOOK.md`](../../docs/runbooks/PEARL_STAR_SETUP_RUNBOOK.md) for the end-to-end procedure when rebuilding the Pearl Star host or onboarding a new one.

# Pearl Star — Qwen-Image transformer shard 08 completion

**Date:** 2026-05-10  
**Agent:** Pearl_Int  
**PROJECT_ID:** PRJ-MANGA-V2  
**Subsystem:** integrations  
**Scope:** Single file — `Qwen/Qwen-Image` transformer shard **08 of 09** only (`diffusion_pytorch_model-00008-of-00009.safetensors`).

## Objective

Finish the last incomplete **~4.3 GiB** shard on Pearl Star under:

`~/phoenix_server/ComfyUI/models/transformer/diffusion_pytorch_model-00008-of-00009.safetensors`

Hub resolve URL (canonical):

`https://huggingface.co/Qwen/Qwen-Image/resolve/main/transformer/diffusion_pytorch_model-00008-of-00009.safetensors`

**Expected bytes:** `4984232856`  
**Expected SHA256 (LFS content):** `caedc7cc2914ab113cfbb3684cf072350201182ae8de1a7308e419385987ae40`

## Strategy

1. **Stop throttled / stuck single-connection** `curl` / `hf download` jobs (scoped `pkill` patterns).
2. **Stage `HF_TOKEN` on Pearl Star** with stdin redirection to `/tmp/.hf_token_session` (mode 600). Do **not** pass the token on remote `ssh` argv.
3. **`aria2c`:** non-interactive `apt-get install aria2` was unavailable; use a **static `aria2c` 1.37.0** binary on Pearl Star at `~/.local/bin/aria2c` (prepend to `PATH`).
4. **First download (16 connections)** — command shape:

```bash
cd ~/phoenix_server/ComfyUI/models/transformer
export HF_TOKEN=$(cat /tmp/.hf_token_session)
nohup aria2c \
  --header="Authorization: Bearer $HF_TOKEN" \
  --max-connection-per-server=16 \
  --split=16 \
  --min-split-size=1M \
  --continue=true \
  --max-tries=20 \
  --retry-wait=30 \
  --console-log-level=warn \
  --summary-interval=60 \
  --out=diffusion_pytorch_model-00008-of-00009.safetensors \
  "https://huggingface.co/Qwen/Qwen-Image/resolve/main/transformer/diffusion_pytorch_model-00008-of-00009.safetensors" \
  >> /tmp/aria2c_shard08.log 2>&1 &
```

**Outcome:** file grew **beyond** the Hub content length and **`sha256sum` did not match** the OID above. **Aborted success path** — removed the bad `.safetensors` and `.aria2` control file before retry.

5. **Second download (8 connections, conservative)** — after clean slate:

```bash
cd ~/phoenix_server/ComfyUI/models/transformer
nohup env "HF_TOKEN=$(cat /tmp/.hf_token_session)" bash -c 'export PATH="$HOME/.local/bin:$PATH"
cd "$HOME/phoenix_server/ComfyUI/models/transformer"
aria2c \
  --header="Authorization: Bearer ${HF_TOKEN}" \
  --max-connection-per-server=8 \
  --split=8 \
  --min-split-size=5M \
  --continue=true \
  --max-tries=30 \
  --retry-wait=20 \
  --console-log-level=warn \
  --summary-interval=60 \
  --auto-file-renaming=false \
  --allow-overwrite=false \
  --out=diffusion_pytorch_model-00008-of-00009.safetensors \
  "https://huggingface.co/Qwen/Qwen-Image/resolve/main/transformer/diffusion_pytorch_model-00008-of-00009.safetensors"' \
  >> /tmp/aria2c_shard08.log 2>&1 &
```

**Terminal log (excerpt):** `(OK):download completed` with reported throughput on the order of **~10 MiB/s** during the run.

## Verification

| Check | Result |
|--------|--------|
| Byte size `stat` / `ls` | **4984232856** |
| `sha256sum diffusion_pytorch_model-00008-of-00009.safetensors` | **`caedc7cc2914ab113cfbb3684cf072350201182ae8de1a7308e419385987ae40`** |
| Residual `.aria2` next to final file | **None** after completion |
| Transformer shard count (`diffusion_pytorch_model-*.safetensors`) | **9** |
| Text encoder + VAE `.safetensors` (paths searched) | Present alongside transformer shards (see install log appendix) |

**SHA256 verdict:** **PASS** (matches Hub LFS OID).

## GPU evidence (CosyVoice2 coexistence)

```text
$ nvidia-smi --query-gpu=memory.free,memory.used --format=csv | head -2
memory.free [MiB], memory.used [MiB]
2808 MiB, 13033 MiB
```

Interpretation: substantial VRAM remains in use by stack services (including CosyVoice2-style resident footprint per prior Pearl Star baseline); no regression check beyond this snapshot.

## Workflow smoke (no `main.py --validate-workflow`)

ComfyUI on Pearl Star (`main.py --help`) **does not** list `--validate-workflow`. **Fallback:**

1. `scp` repo file `scripts/image_generation/comfyui_workflows/qwen_image_txt2img_manga.json` → `/tmp/qwen_image_txt2img_manga.json` on Pearl Star.
2. `GET http://127.0.0.1:8188/object_info` (ComfyUI already listening on **8188**).
3. Python: collect all `class_type` from the workflow JSON; assert each exists as a key in `object_info`.

**Result:** **9** required node types; **`missing`** list **empty** (all registered).

**Caveat:** workflow `CheckpointLoaderSimple` expects **`qwen_image_2.0.safetensors`** under checkpoints layout; that **single-file checkpoint name was not found** under `~/phoenix_server/ComfyUI/models/checkpoints/` at verification time. Node registration **PASS**; **full end-to-end graph execution** still depends on checkpoint packaging / `extra_model_paths` / workflow loader alignment (out of scope for this shard-only PR).

**Smoke verdict:** **PASS (API / node registration)** with **checkpoint path caveat** above.

## Cleanup

On Pearl Star after verification:

`rm -f /tmp/.hf_token_session /tmp/aria2c_shard08.log /tmp/qwen_image_txt2img_manga.json`

## Operator follow-ups

- **Rotate HF token** if any `ps`/`pgrep` output ever captured `Authorization: Bearer …` in argv (treat as possible exposure on log surfaces).
- If **`aria2c` with high split** against Hugging Face repeatedly yields **wrong length or wrong SHA256**, prefer **lower `--split` / `--max-connection-per-server`** or a **single-stream** tool with explicit `Content-Length` checks before trusting bytes.

## Related

- Install log append: [`pearl_star_v2_install_log_2026-05-07.md`](pearl_star_v2_install_log_2026-05-07.md) (appendix — shard 08).

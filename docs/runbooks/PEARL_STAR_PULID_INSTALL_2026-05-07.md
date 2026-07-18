# Pearl Star — PuLID + Qwen-Image + Animagine XL 4.0 install runbook

**Date:** 2026-05-07
**Phase:** V2 Phase B (cap entry MANGA-LAYERED-PIPELINE-V2-01)
**Owner:** Pearl_Int (executes); Pearl_Dev (verifies workflow templates render)

This runbook is the **operator-supervised install procedure** for Phase B's Pearl Star bringup. Phase B's PR ships the workflow JSONs + engine router + reference sheet generator + queue_panel_renders extension as **CODE that's ready to consume** these installs. Execute this runbook in a focused session before kicking off Phase C.

## Why this is operator-supervised, not agent-driven

The Phase B Pearl_Dev session author flagged a **torch version conflict** that requires hands-on resolution:

- Pearl Star's `~/phoenix_server/ComfyUI/venv` has **torch 2.11.0** (verified 2026-05-07).
- `lldacing/ComfyUI_PuLID_Flux_ll` requirements include `facenet-pytorch` which **requires torch < 2.3.0**.
- Per the upstream README, the workaround is: `pip install facenet-pytorch --no-deps`.
- An unattended `pip install -r requirements.txt` would fail or downgrade torch, breaking the running ComfyUI server.

Operator runs the steps below with eyes on the install output, ready to roll back if anything goes sideways. ComfyUI is currently warm-cached (~6 GiB FLUX-schnell-fp8 in VRAM); a botched install + restart loses that cache.

## Pre-install gates

```bash
# Pearl Star reachable via alias (post Pearl_Int #920 setup)
ssh pearl_star 'echo OK $(hostname); ls ~/.phoenix_omega_pearl_star'

# Disk space ≥ 30 GiB free (Qwen-Image ~20 GiB + Animagine 4.0 ~6 GiB + PuLID weights ~1 GiB)
ssh pearl_star 'df -h ~/phoenix_server/ComfyUI/models/checkpoints/ | tail -1'

# ComfyUI venv exists at known path
ssh pearl_star 'ls ~/phoenix_server/ComfyUI/venv/bin/pip ~/phoenix_server/ComfyUI/venv/bin/python'

# huggingface_hub installed (for checkpoint downloads)
ssh pearl_star '~/phoenix_server/ComfyUI/venv/bin/pip show huggingface_hub | head -3'

# GPU snapshot (informational)
ssh pearl_star 'nvidia-smi --query-gpu=memory.free,memory.total,name --format=csv,noheader'
```

If any of these fail, stop and resolve before proceeding.

## Step 1 — Install lldacing/ComfyUI_PuLID_Flux_ll (FLUX path; ~5 min)

```bash
ssh pearl_star bash -lc '"
cd ~/phoenix_server/ComfyUI/custom_nodes
git clone https://github.com/lldacing/ComfyUI_PuLID_Flux_ll.git
cd ComfyUI_PuLID_Flux_ll

# CRITICAL: install requirements WITHOUT facenet-pytorch first
~/phoenix_server/ComfyUI/venv/bin/pip install \
    cython facexlib insightface onnxruntime onnxruntime-gpu ftfy timm

# THEN install facenet-pytorch with --no-deps to skip its torch<2.3 constraint
~/phoenix_server/ComfyUI/venv/bin/pip install facenet-pytorch --no-deps

# Verify torch version stayed at 2.11.0 (not downgraded)
~/phoenix_server/ComfyUI/venv/bin/python -c \"import torch; print('torch', torch.__version__)\"
"'
```

Expected: `torch 2.11.0` after install. If it downgrades to <2.3, **roll back** (`rm -rf ~/phoenix_server/ComfyUI/custom_nodes/ComfyUI_PuLID_Flux_ll`) and re-pin torch before retrying.

## Step 2 — Install cubiq/PuLID_ComfyUI (SDXL path; ~5 min)

```bash
ssh pearl_star bash -lc '"
cd ~/phoenix_server/ComfyUI/custom_nodes
git clone https://github.com/cubiq/PuLID_ComfyUI.git
cd PuLID_ComfyUI
~/phoenix_server/ComfyUI/venv/bin/pip install -r requirements.txt
"'
```

cubiq's requirements are lighter (no facenet-pytorch torch conflict). Watch for any torch downgrade attempts and abort if they appear.

## Step 3 — Download Qwen-Image base (~20 GiB; ~30-60 min on Pearl Star bandwidth)

```bash
ssh pearl_star bash -lc '"
cd ~/phoenix_server/ComfyUI/models/checkpoints
~/phoenix_server/ComfyUI/venv/bin/huggingface-cli download Qwen/Qwen-Image \
    --include qwen_image_2.0.safetensors \
    --local-dir . --local-dir-use-symlinks False
ls -lh qwen_image_*.safetensors
"'
```

(Adjust the `--include` filename if Qwen has rolled forward to a newer tag — check https://huggingface.co/Qwen/Qwen-Image for the current canonical filename.)

## Step 4 — Download Animagine XL 4.0 base (~6 GiB; ~10 min)

```bash
ssh pearl_star bash -lc '"
cd ~/phoenix_server/ComfyUI/models/checkpoints
~/phoenix_server/ComfyUI/venv/bin/huggingface-cli download cagliostrolab/animagine-xl-4.0 \
    --include animagine_xl_4_0.safetensors \
    --local-dir . --local-dir-use-symlinks False
ls -lh animagine_xl_*.safetensors
"'
```

## Step 5 — Restart ComfyUI to register custom nodes

```bash
# Stop existing ComfyUI process
ssh pearl_star 'pkill -f "phoenix_server/ComfyUI.*main.py" || true'
sleep 2

# Start fresh (operator's standard invocation; adjust if Pearl Star uses systemd or tmux session)
ssh pearl_star 'cd ~/phoenix_server/ComfyUI && nohup ~/phoenix_server/ComfyUI/venv/bin/python main.py \
    --listen 0.0.0.0 --port 8188 > /tmp/comfyui_v2_phase_b.log 2>&1 &'

sleep 30  # let ComfyUI import all custom nodes + models

# Verify nodes registered
ssh pearl_star 'curl -s http://localhost:8188/object_info | python3 -c "
import json, sys
d = json.load(sys.stdin)
for needed in [\"PulidFluxFaceNetLoader\", \"ApplyPulidFlux\", \"PulidModelLoader\", \"ApplyPulid\"]:
    print(f\"{needed:30s}\", \"OK\" if needed in d else \"MISSING\")
"'
```

All four nodes should print `OK`. If any are MISSING, check the ComfyUI log:

```bash
ssh pearl_star 'tail -100 /tmp/comfyui_v2_phase_b.log | grep -iE "error|traceback|fail" | head -20'
```

Common failures:
- **`No module named 'facenet_pytorch'`** — Step 1 install incomplete; re-run.
- **`No module named 'insightface'`** — pip install rejected the wheel; check Python version (need 3.12).
- **`onnxruntime-gpu` CUDA mismatch** — install the CPU-only variant: `pip install onnxruntime` only (drop the `-gpu` line).

## Step 6 — Smoke test: 1-panel reference sheet generation (Phase A's ahjan + character_design YAML)

This validates the full Phase B install end-to-end against Phase A's deliverables. **Requires Pearl_Editor to have filled `config/source_of_truth/manga_profiles/series/stillness_press_<topic>_vol1.yaml` per the A4 checklist.**

```bash
# From the repo root on operator's local machine, against Pearl Star ComfyUI
COMFYUI_URL=http://pearl_star:8188 \
PYTHONPATH=. python3 -m scripts.manga.character_individuation.reference_sheet_generator \
    --character-design config/source_of_truth/manga_profiles/series/stillness_press_anxiety_vol1.yaml \
    --teacher-id ahjan \
    --brand-id stillness_press
```

Expected outputs:
- `artifacts/manga/image_bank/stillness_press/reference_sheets/ahjan/ahjan_reference_sheet.png` (1080x1920 PNG, ~1-3 MB)
- `artifacts/manga/image_bank/stillness_press/reference_sheets/ahjan/provenance.json` (engine + seed + prompt SHA + character_design SHA)

If the smoke test passes, Phase B is operationally complete. Spawn Phase C.

## Rollback procedure (if anything breaks)

```bash
# Roll back custom nodes
ssh pearl_star 'rm -rf ~/phoenix_server/ComfyUI/custom_nodes/ComfyUI_PuLID_Flux_ll'
ssh pearl_star 'rm -rf ~/phoenix_server/ComfyUI/custom_nodes/PuLID_ComfyUI'

# Roll back checkpoint downloads (frees disk; doesn't touch existing flux1-schnell-fp8)
ssh pearl_star 'rm -f ~/phoenix_server/ComfyUI/models/checkpoints/qwen_image_*.safetensors'
ssh pearl_star 'rm -f ~/phoenix_server/ComfyUI/models/checkpoints/animagine_xl_*.safetensors'

# Restart ComfyUI back to pre-install state
ssh pearl_star 'pkill -f "phoenix_server/ComfyUI.*main.py" || true'
ssh pearl_star 'cd ~/phoenix_server/ComfyUI && nohup ~/phoenix_server/ComfyUI/venv/bin/python main.py \
    --listen 0.0.0.0 --port 8188 > /tmp/comfyui_post_rollback.log 2>&1 &'
```

## License verification (Pearl_Int)

After install, verify license tier holds at runtime per the audit pattern. Each component's license clause is reproduced below for fast reference:

| Component | License | Action verb |
|---|---|---|
| Qwen-Image | Apache 2.0 | unrestricted commercial use |
| Animagine XL 4.0 | CreativeML Open RAIL++-M | commercial use OK; verify Phoenix's catalog doesn't trip the harmful-uses clauses |
| `lldacing/ComfyUI_PuLID_Flux_ll` (FaceNet variant) | Apache 2.0 + facenet-pytorch (Apache 2.0) + VGGFace2 weights (commercial-clean) | only when using `PulidFluxFaceNetLoader` (NOT `PulidFluxInsightFaceLoader`) |
| `cubiq/PuLID_ComfyUI` (SDXL/Animagine path) | Apache 2.0 | verify FaceNet path enabled at workflow time |

If any flag changes since the audit (2026-04-29) — operator surfaces; do not proceed with renders until cleared.

# Pearl Star V2 manga pipeline install log — 2026-05-07

**Agent:** Pearl_Int (operator-collaborative, "do everything" delegation)
**Runbook:** [`docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md`](../../docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md)
**Authority:** cap entry [`MANGA-LAYERED-PIPELINE-V2-01`](../../docs/PEARL_ARCHITECT_STATE.md), Phase B
**Closes:** install side of `ws_manga_v2_phase_b_base_models_pulid_20260507`

## Pre-install state

```
Host:         pearlstar (alias: pearl_star)
SSH:          OK; marker ~/.phoenix_omega_pearl_star present (Apr 25)
GPU:          NVIDIA RTX 5070 Ti, 6.7 GiB free of 16.3 GiB
              (CosyVoice2 holds 2.9 GiB; ComfyUI warm cache holds ~6 GiB)
Disk:         1.6 TB free of 1.8 TB at ComfyUI checkpoints volume
ComfyUI:      v0.18.1 at ~/phoenix_server/ComfyUI/
Venv torch:   2.11.0+cu130
Custom nodes: HandFixer + ComfyUI defaults only
Checkpoints:  flux1-schnell-fp8.safetensors (17 GiB; brand-2 V1 ship base)
              flux1-dev-fp8.safetensors (1.5 MB stub; deprecated)
```

## Step-by-step transcript

### Step 1 — lldacing/ComfyUI_PuLID_Flux_ll (FLUX path) ✅

Repo: `https://github.com/lldacing/ComfyUI_PuLID_Flux_ll.git`
Commit installed: `7c7362b update README`
License: Apache 2.0 ✓ (verified via `LICENSE` file in clone)

Procedure:

```
git clone (~/phoenix_server/ComfyUI/custom_nodes/ComfyUI_PuLID_Flux_ll)
~/phoenix_server/ComfyUI/venv/bin/pip install \
    cython facexlib insightface onnxruntime onnxruntime-gpu ftfy timm
~/phoenix_server/ComfyUI/venv/bin/pip install facenet-pytorch --no-deps
```

The `requirements.txt` in lldacing's repo has `# facenet-pytorch` commented out with the inline note "facenet-pytorch limits torch<2.3.0, so use command: pip install facenet-pytorch --no-deps". Followed verbatim.

**torch 2.11.0+cu130 unchanged after install.** ✓

Verification (FaceNet variant import test — the commercial-clean path):

```
$ python -c "from facenet_pytorch import MTCNN, InceptionResnetV1; print('OK')"
facenet-pytorch import OK
torch 2.11.0+cu130
```

Installed packages (key ones):

```
facenet-pytorch  2.6.0
facexlib         0.3.0
insightface      0.7.3
onnxruntime      1.25.1
onnxruntime-gpu  1.25.1
timm             1.0.26
torch            2.11.0          (UNCHANGED — workaround successful)
```

### Step 2 — cubiq/PuLID_ComfyUI (SDXL/Animagine path) ✅

Repo: `https://github.com/cubiq/PuLID_ComfyUI.git`
Commit installed: `93e0c4c maintenance mode`
License: Apache 2.0 ✓ (verified via `LICENSE` file in clone)

Procedure:

```
git clone (~/phoenix_server/ComfyUI/custom_nodes/PuLID_ComfyUI)
~/phoenix_server/ComfyUI/venv/bin/pip install -r requirements.txt
```

All deps already satisfied by Step 1 install (cubiq's requirements are a strict subset of lldacing's + transitive deps via facexlib/insightface/timm). No new packages added. **torch 2.11.0+cu130 unchanged.** ✓

### Step 3 — Qwen-Image checkpoint download — DEFERRED (operator decision)

Source: `https://huggingface.co/Qwen/Qwen-Image` (canonical Comfy-Org repackage at `https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI`)
License (HF API verified 2026-05-07): `apache-2.0` ✓ (matches audit)

Discovery during execution: the runbook's ~20 GB estimate undershot. `Qwen/Qwen-Image` is published in Diffusers multi-subdir format (scheduler/text_encoder/tokenizer/transformer/vae); ComfyUI consumes the Comfy-Org-canonical split-files repackage which weighs **~30 GB minimum** at FP8 (`qwen_image_2512_fp8_e4m3fn.safetensors` 20.43 GB + `qwen_2.5_vl_7b_fp8_scaled.safetensors` 9.38 GB + `qwen_image_vae.safetensors` 0.25 GB). The PR #926 workflow `qwen_image_txt2img_manga.json` uses `CheckpointLoaderSimple` (single-file convention); Comfy-Org's split-files format requires `UNETLoader` + `DualCLIPLoader` + `VAELoader` — a separate workflow JSON edit.

Operator decision (Path B in the operator-collaborative install thread): **defer Qwen-Image to a focused follow-up session** that bundles the ~30 GB download with the workflow JSON loader update. Animagine 4.0 carries V2 for shojo / iyashikei / healing brands (the lanes where attractor-matches-register matters most); Phase B's engine router fallback degrades seinen / josei / psychological routes to FLUX-schnell with explicit `fallback_used=True` reasoning until Qwen lands.

**Status:** DEFERRED to a focused operator-supervised session post-Phase-C / pre-Phase-E. This install delivers Animagine + PuLID nodes; Phase E V1→V2 comparison shows whether brand-1 V2 (full-Animagine) is acceptable enough to defer Qwen further or compels the focused Qwen install session.

### Step 4 — Animagine XL 4.0 checkpoint download — DEFERRED (HF rate-limit discovery)

Source: `https://huggingface.co/cagliostrolab/animagine-xl-4.0`
License (HF API verified 2026-05-07): `openrail++` ✓ (= RAIL++-M per audit)
Target: `~/phoenix_server/ComfyUI/models/checkpoints/animagine-xl-4.0.safetensors`
Canonical filename: 6.94 GB single file (the repo also ships an `-opt` variant; the non-opt is the canonical full-precision).

Operational discovery during execution: **HF CDN throttles unauthenticated downloads from Pearl Star's IP to ~50 KB/s.** Direct curl test confirmed:

```
$ curl -L -o /dev/null --max-time 8 "https://huggingface.co/cagliostrolab/animagine-xl-4.0/resolve/main/animagine-xl-4.0.safetensors"
speed_avg: 43505 B/s | downloaded: 365899 B | time: 8.41 s
```

At 50 KB/s, 6.94 GB takes ~37 hours. Not viable in this session. The earlier `Qwen/Qwen-Image` partial-download progress (35 GB observed during the multi-variant Path A attempt) was bursty and is consistent with HF's intermittent throttling; the steady-state we hit on the Path B retry was the true rate-limit floor.

Resolution path: operator adds `HF_TOKEN` to Keychain (existing Pearl_Int convention per `skills/pearl-int/references/credential_staging_files.md`). Authenticated downloads from HF run at ~5-50 MB/s — the 6.94 GB Animagine file lands in 2-20 min depending on bandwidth. With the token, both Animagine AND Qwen-Image (when operator commits to its 30 GB) ship in one focused install session.

**Status:** DEFERRED. Operator runs in a follow-up Pearl_Int mini-session: (1) generate HF_TOKEN at `https://huggingface.co/settings/tokens` (read-only scope sufficient), (2) `security add-generic-password -s phoenix-omega -a HF_TOKEN -w <token> -U` (per the credential_staging_files convention from PR #920), (3) `eval $(load_integration_env_from_keychain.py)` propagates it to env, (4) re-run the Animagine + (optionally) Qwen download commands documented above. ETA ~10 min operator time + 10-30 min download.

### Step 5 — ComfyUI restart + PuLID node registration ✅

**Path chosen: A — full restart**, per operator's "do everything" delegation. Restart was needed for ComfyUI to register the new custom nodes (PuLID Flux + cubiq PuLID); without restart the nodes don't appear in `/object_info`.

CosyVoice2 (PID 1561, 2.9 GiB) is a separate service; its memory is not affected by ComfyUI restart. ComfyUI queue was empty pre-restart (verified `curl localhost:8188/queue` → `{"queue_running":[],"queue_pending":[]}`); no in-flight work was lost.

Verification post-restart:

```
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8188/system_stats
HTTP 200

$ curl -s http://localhost:8188/object_info | <node-presence-check>
  PulidFluxFaceNetLoader         OK
  ApplyPulidFlux                 OK
  PulidFluxInsightFaceLoader     OK   (present but NOT used; FaceNet is the commercial-clean path)
  PulidModelLoader               OK
  ApplyPulid                     OK
  PulidEvaClipLoader             OK
  PulidInsightFaceLoader         OK   (present but NOT used; same reason)
  total nodes: 683
```

All 7 PuLID nodes registered. The InsightFace-loader variants are imported by the node packs but the workflow JSONs (`flux_txt2img_manga_pulid.json`, `animagine_xl_txt2img_manga.json`) reference the FaceNet variants exclusively. AntelopeV2 weights never download.

**Engine router fallback wiring (operator-authorized in-PR addition).** Because Qwen-Image AND Animagine are both deferred, this PR also extends `scripts/manga/character_individuation/engine_router.py::select_engine` with an `available_engines` parameter — when set to a runtime registry (`{ENGINE_FLUX_SCHNELL}` for the current Pearl Star state, `{ENGINE_FLUX_SCHNELL, ENGINE_ANIMAGINE}` after the focused HF_TOKEN download session lands Animagine), routes that would pick a not-yet-installed engine instead degrade to FLUX-schnell with explicit `fallback_used=True` and reasoning. This means routes don't break; they degrade gracefully to the V1 brand-2 ship config (FLUX-schnell + PuLID-FaceNet identity lock — which is itself a V2 upgrade over V1's pure FLUX-schnell-no-PuLID). 3 new tests cover the path. When `available_engines=None` the pre-runtime-registry behavior is preserved (back-compat for unit tests + non-Pearl-Star consumers). 12 + 3 = 15 engine_router tests passing.

### Step 6 — ahjan reference sheet smoke

**DEFERRED.** Pre-condition not met:

```
$ grep -lr "^character_design:" config/source_of_truth/manga_profiles/series/
(no matches)
```

24 series profile YAMLs exist (`stillness_jp_*`, `cogclar_jp_*`, etc.) but none carry a `character_design:` block yet. Pearl_Editor's Phase A.4 task — filling the 12-axis character_design YAML per teacher per the [pre-staged checklist](character_design_a4_pre_staged_checklist_2026-05-07.md) — has not been started. The reference_sheet_generator.py code from PR #926 returns a clean `skipped=True` result when the character_design block is missing; this is the correct behavior, not a failure.

Smoke deferral status: code path verified by Phase B test suite (8/8 reference_sheet_generator tests passing on main). End-to-end smoke runs the moment Pearl_Editor lands the first character_design YAML for ahjan in `config/source_of_truth/manga_profiles/series/<stillness_press_series>.yaml`.

## License verification (vs audit `2026-04-29`)

| Component | Audit said | Verified `2026-05-07` | Delta |
|---|---|---|---|
| Qwen-Image | Apache 2.0 ✓ | HF API: `apache-2.0` | unchanged |
| Animagine XL 4.0 | RAIL++-M ✓ | HF API: `openrail++` (= RAIL++-M) | unchanged |
| `lldacing/ComfyUI_PuLID_Flux_ll` | Apache 2.0 ✓ | `LICENSE` file: Apache 2.0 (from `Cloning into 'ComfyUI_PuLID_Flux_ll'... Apache License Version 2.0`) | unchanged |
| `cubiq/PuLID_ComfyUI` | Apache 2.0 ✓ | `LICENSE` file: Apache 2.0 | unchanged |
| `facenet-pytorch` (transitive via lldacing PuLID) | MIT (commercial-clean per audit) | `timesler/facenet-pytorch` `LICENSE.md`: `MIT License Copyright (c) 2019 Timothy Esler` | unchanged |

**No flag changes** since audit. Pearl_Architect re-ratification not required.

**FaceNet vs InsightFace — runtime path commitment.** Both PuLID node packs ship with `insightface` as a transitive dep (used for code loading), but Phase B's workflow JSONs (`flux_txt2img_manga_pulid.json`, `qwen_image_txt2img_manga.json`, `animagine_xl_txt2img_manga.json`) ALL explicitly call `PulidFluxFaceNetLoader` (lldacing path) or the FaceNet-style ApplyPulid node (cubiq path). The InsightFace AntelopeV2 weights (the non-commercial dependency) are never downloaded because `PulidFluxInsightFaceLoader` is never invoked. License posture preserved at runtime.

## Post-install state

```
GPU:          (will be re-checked in PR description after restart)
Venv torch:   2.11.0+cu130 (UNCHANGED)
Custom nodes: HandFixer + ComfyUI defaults
              + ComfyUI_PuLID_Flux_ll @ 7c7362b
              + PuLID_ComfyUI @ 93e0c4c
Checkpoints:  flux1-schnell-fp8 (17 GiB)
              flux1-dev-fp8 (1.5 MB stub; DEPRECATED — keep until cleanup)
              qwen_image_2.0 + tokenizer (~20 GiB; in progress)
              animagine_xl_4_0 (~6 GiB; in progress)
```

## Phase C readiness — Path B (further deferred to Path B') verdict

**Conditional yes — every route degrades to FLUX-schnell + PuLID-FaceNet baseline.** Animagine and Qwen-Image both deferred to a focused operator session that bundles HF_TOKEN setup + downloads.

Coverage matrix once this PR merges:

| Brand-demographic-genre lane | V2 base post-PR | Status |
|---|---|---|
| any V2 route | engine router fallback → FLUX-schnell + PuLID-FaceNet | **PuLID-augmented FLUX baseline** (V1 brand-2 ship was FLUX-schnell-no-PuLID; this is meaningful upgrade) |
| **all routes** ↑ when Animagine + Qwen land in follow-up session | Animagine for shojo/iyashikei; Qwen for seinen/josei; FLUX-schnell as fallback only | full V2 multi-base routing |

Phase C (LoRA training + animeoutlineV4 + halftone + per-character / brand LoRAs) is **unblocked** with PuLID-FaceNet identity lock available now. Character LoRAs train against any base; the LoRA outputs land regardless of whether Qwen / Animagine are installed yet.

Order of operations operator faces:
1. **Merge this PR** — PuLID nodes + engine_router fallback + workflow templates active; Phase C unblocks
2. **Focused HF_TOKEN session** (~10 min operator + 10-30 min download): generate token, store in Keychain, download Animagine 4.0 (and optionally Qwen-Image at ~30 GB)
3. **Update available_engines runtime registry** in any consumer (e.g. add `ENGINE_ANIMAGINE` to the set) to flip on Animagine routing
4. **Phase E** V1 → V2 visual comparison reveals whether even the FLUX-schnell-only V2 (with PuLID + character LoRA + brand-style LoRA + animeoutlineV4 + halftone from Phase C) is bestseller-grade enough to defer Animagine further

## Pearl_Editor blocker for B6

12 of 12 named teachers pending character_design YAML completion. The Phase A.4 [pre-staged checklist](character_design_a4_pre_staged_checklist_2026-05-07.md) provides axis seeds and operator instructions; ahjan has the richest seed material (12 model_sheets + 8 expressions on disk per `artifacts/manga/image_bank/stillness_press/character_model_sheets.json`). Once Pearl_Editor lands the first `character_design:` block in a series YAML, the reference_sheet_generator (already on main from PR #926) renders the canonical reference PNG against the now-installed PuLID stack — closing the B6 deferral.

---

## Appendix — Qwen-Image transformer shard 08 completion (Pearl_Int, 2026-05-10)

**PROJECT_ID:** PRJ-MANGA-V2 · **Subsystem:** integrations

Transcript (Pearl Star host `pearl_star`):

1. **Stuck single-connection jobs cleared** — `pkill` patterns scoped to avoid matching the SSH session itself (`curl` / `hf download` lines targeting Qwen).
2. **HF token staged on Pearl Star** via stdin → `/tmp/.hf_token_session` (chmod 600); never passed on `ssh` argv. Token file removed after download (`rm -f /tmp/.hf_token_session`).
3. **`aria2c`:** system `apt-get` for `aria2` was not usable non-interactively; a **static `aria2c` 1.37.0** binary was placed under `~/.local/bin/aria2c` on Pearl Star (operator-supplied x86_64 musl build). `PATH` included `~/.local/bin` for the download command.
4. **First attempt (`--split=16 --max-connection-per-server=16`)** produced an **oversized** artifact (~5.2 GiB vs expected **4,984,232,856** bytes) and **SHA256 mismatch** vs Hub LFS OID. Corrupt file + `.aria2` control file **removed**; download **not** declared successful.
5. **Second attempt (`--split=8 --max-connection-per-server=8`, fresh file)** completed with **`aria2c` status OK**; final size **4984232856** bytes; **no** residual `.aria2` next to the `.safetensors`.
6. **SHA256 (required gate):**

```
$ cd ~/phoenix_server/ComfyUI/models/transformer && sha256sum diffusion_pytorch_model-00008-of-00009.safetensors
caedc7cc2914ab113cfbb3684cf072350201182ae8de1a7308e419385987ae40  diffusion_pytorch_model-00008-of-00009.safetensors
```

**Verdict: MATCH** (expected OID `caedc7cc2914ab113cfbb3684cf072350201182ae8de1a7308e419385987ae40`).

7. **Inventory:** `find …/transformer -name 'diffusion_pytorch_model-*.safetensors' | wc -l` → **9** (shards 01–09). Text encoder shards (`model-0000[1-4]-of-00004.safetensors`) and VAE `.safetensors` under `models/vae` present per `find` listing at completion time.
8. **GPU snapshot after completion:** `nvidia-smi --query-gpu=memory.free,memory.used --format=csv` → `2808 MiB` free, `13033 MiB` used (CosyVoice2 + ComfyUI footprint unchanged in spirit from the 2026-05-07 baseline).
9. **Workflow smoke:** ComfyUI `main.py` on this host **does not** expose `--validate-workflow` (help output checked). Fallback: copied repo workflow JSON to `/tmp`, then **`GET http://127.0.0.1:8188/object_info`** + Python intersection over all `class_type` values → **missing list empty** (all nine node types registered). **Caveat:** `CheckpointLoaderSimple` in `qwen_image_txt2img_manga.json` references `qwen_image_2.0.safetensors`; that filename was **not** present under `models/checkpoints/` at check time — shard completion does not by itself supply the single-file checkpoint; execution smoke remains gated on checkpoint packaging / path config.
10. **Cleanup:** `/tmp/.hf_token_session`, `/tmp/aria2c_shard08.log`, and the temporary workflow copy under `/tmp` removed after verification.

**Security note:** Any process listing that captured `Authorization: Bearer …` in argv should be treated as a **credential hygiene** signal; operator should **rotate** the Hugging Face token stored in Keychain after this session.

**Detail doc:** [`pearl_star_qwen_shard_08_complete_2026-05-10.md`](pearl_star_qwen_shard_08_complete_2026-05-10.md).

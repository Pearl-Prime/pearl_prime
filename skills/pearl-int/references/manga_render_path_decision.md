# Manga Image Generation — Canonical Path & Decision Tree

**Date:** 2026-05-07
**Owner:** Pearl_Int (path) + Pearl_Dev (execution)
**Authority:** `artifacts/research/comfyui_workflow_audit_2026-04-29.md` +
operator decision H1=A per memory `feedback_campaign_h1_h2_decisions`
+ PR #807 (schnell→dev fix) + PR #809 (LoRA base_model sweep) +
`artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md` (smoke status).

## Canonical config (operator-approved H1=A)

Every manga panel render — regardless of backend — MUST use:

| Setting | Value |
|---|---|
| Checkpoint | `flux1-dev-fp8.safetensors` (NOT schnell) |
| Steps | 28 |
| CFG | 3.5 |
| Sampler | `dpmpp_2m` |
| Scheduler | `karras` |
| Denoise | 1.0 |

**flux-schnell is BANNED for manga panel work** per the audit. Schnell
is distilled for ~4 steps cfg 1.0; running it at higher steps produces
register oscillation (B&W manga ↔ full color flips) and unpredictable
identity drift. The audit confirmed via PNG inspection of 8 outputs.

## Two backend paths

### Path A — Pearl Star local ComfyUI (FREE, default)

- **Endpoint:** `http://192.168.1.112:8188` (Pearl Star LAN, RTX 5070 Ti)
- **Driver:** `scripts/manga/queue_panel_renders.py`
- **Workflow:** `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json`
  — already on H1=A as of PR #807. `_build_workflow` only injects prompt/
  negative/seed; the canonical config flows automatically.
- **GPU need:** ≥ 12 GiB free for FLUX-dev-fp8 at 1080×1920
- **Coordination:** `ws_teacher_manga_triptych_20260410` shares the GPU.
  Check `nvidia-smi` before queuing; back off + retry if < 12 GiB free.
- **Auth:** SSH to `pearl_star` alias (Tailscale-routed). Marker file at
  `~/.phoenix_omega_pearl_star` confirms canonical host.
- **Cost:** $0. This is the default for all manga panel work.

### Path B — RunComfy serverless ComfyUI (PAID; video_bank only as of 2026-05-07)

- **Endpoint:** `https://api.runcomfy.net/prod/v1`
- **Deployment:** `677edba8-ace0-4b2b-bad2-8e94b9959065` (`RUNCOMFY_DEPLOYMENT_ID`)
- **Driver:** `scripts/image_generation/runcomfy_batch.py`
- **Workflow on the deployment:** `flux_video_bank.json` —
  flux1-schnell-fp8 / 4 steps / 1.0 cfg / euler / simple. **This is
  CORRECT for schnell** (schnell is distilled for ~4 steps cfg 1.0).
  The audit's "schnell defects" finding was specifically about schnell
  run at DEV settings (24 steps / 4.0 cfg) — that combination is broken.
  Schnell at its native 4/1.0 is fine.
- **Cost:** ~$0.03/render (per RunComfy metering). Used for video_bank
  asset generation, not manga panels.
- **Auth:** `RUNCOMFY_API_KEY` + `RUNCOMFY_DEPLOYMENT_ID` from Keychain
  (post PR #920 scheme: `service=phoenix-omega`, `account=NAME`).
- **Manga panels are NOT served by this deployment.** Node IDs and
  workflow shape are video_bank-specific. Submitting a manga-shape
  graph (`flux_txt2img_manga.json`) returns HTTP 422 — that is NOT
  staleness; it is graph-shape mismatch.

### What was previously misdocumented

The `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md` smoke test
attempted to validate the schnell→dev fix by submitting a manga-shape
workflow against the video_bank deployment. The 422 there was about
graph-shape mismatch, not deployment staleness. The smoke MD's "Path
to actually validating the fix → re-deploy the workflow" framing
implied the deployment needed re-sync; in fact:

- The deployment is correctly serving its video_bank purpose.
- The schnell-at-dev-settings defect lives in OTHER template files
  (`config/comfyui_workflows/manga_covers/*.json`) which PR #807/#809
  already corrected on origin/main.
- Manga panel work routes to Path A (Pearl Star); RunComfy is not a
  manga fallback unless a separate manga-compatible RunComfy
  deployment is created (not currently scheduled).

**Net: nothing to fix on RunComfy deployment 677edba8.** Cap-entry
follow-up: when/if manga-RunComfy fallback is needed, open a separate
deployment + a separate `RUNCOMFY_MANGA_DEPLOYMENT_ID` env var. Don't
overwrite the video_bank deployment.

## Decision tree

```
START: manga panel batch needed
│
├── Q1: Is this a brand-1 / brand-2 ep_NNN ship at WEBTOON-Canvas
│        scale (10-50 panels)?
│   ├── YES → default to Path A (Pearl Star); free + GPU sufficient
│   │         when not contending with triptych
│   └── NO  → continue
│
├── Q2: Is Pearl Star GPU free memory ≥ 12 GiB?
│   ├── YES → Path A
│   └── NO  → check `ws_teacher_manga_triptych_20260410` status
│             ├── If completing within 30 min → wait + Path A
│             ├── If hot for hours → operator decides (Path B paid
│             │                       OR defer brand-2)
│             └── If not running but GPU still hot → another job;
│                                                      surface to operator
│
├── Q3: Is this a video_bank job?
│   ├── YES → Path B (RunComfy serverless 677edba8); already configured
│   │         correctly with schnell/4/1.0 — no re-sync needed
│   └── NO  → Path A (Pearl Star) for manga panels
│
└── Q4: Are we time-critical (release deadline within hours)?
    ├── YES → operator authorizes Path B with explicit cost approval
    └── NO  → Path A (free; queue-and-wait if GPU constrained)
```

## NOT a re-sync — when manga-RunComfy fallback IS desired

If at some future date manga-on-RunComfy becomes useful (e.g., Pearl
Star migration, scale beyond local GPU, time-critical batch), the
correct procedure is:

1. Create a NEW RunComfy deployment (don't overwrite 677edba8).
2. Import `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json`
   to the new deployment.
3. Add a new env var (`RUNCOMFY_MANGA_DEPLOYMENT_ID`) tracked in
   `scripts/ci/integration_env_registry.py`.
4. Update `runcomfy_batch.py` to accept a deployment-routing arg, OR
   write a manga-specific submitter that targets the new deployment.
5. Smoke-test against the new deployment.
6. Update this doc with the new deployment ID + cost considerations.

This is a multi-hour Pearl_Dev session, not a 5-minute console action.

## Future composite (Phase 2, not currently scheduled)

The audit recommends a composite workflow for character consistency:
- PuLID-Flux-II for face lock (>90% feature retention)
- OpenPose ControlNet for pose control
- LoRA stack for protagonist + brand-style + manga-register
- HalfTone post-processing for screentone

Phoenix's current path has none of these. They're Phase 2 work; not
required for V1 ep ships, but identity will drift between panels.
Operator decides when to schedule the Phase 2 composite ws.

## Related Pearl_Int knowledge

- Credential staging: `skills/pearl-int/references/credential_staging_files.md`
  (PR #920 — Keychain scheme, EU-jurisdiction R2 endpoint)
- Integration registry: `skills/pearl-int/references/integration_registry.md`

## Quick reference for Pearl_Dev sessions

When opening a manga ship Pearl_Dev session, default the prompt to:
- Backend: Pearl Star (`pearl_star` SSH alias)
- Driver: `scripts/manga/queue_panel_renders.py`
- DO NOT specify `--model` flag (the script reads from the template,
  which is already H1=A on main)
- DO add a GPU-availability preflight check (`nvidia-smi --query-gpu=memory.free`)
- DO NOT route to RunComfy unless operator explicitly authorizes the
  paid path AND the deployment re-sync has completed

## V2 update — multi-base-model stack (post Phase B; cap entry MANGA-LAYERED-PIPELINE-V2-01)

After Phase B (cap entry MANGA-LAYERED-PIPELINE-V2-01) lands, the Pearl
Star render path expands from FLUX-only to a 3-engine commercial-clean
stack with PuLID-FaceNet identity-lock layered on top. The
`scripts/manga/character_individuation/engine_router.py` selects the
right engine + workflow per (brand, genre, demographic, color_mode,
use_reference) tuple.

### Engine inventory (commercial-clean)

| Engine | License | When | Workflow file |
|---|---|---|---|
| **Qwen-Image** | Apache 2.0 | seinen / josei character-distinctness work; CJK speech-bubble rendering on JP/CN locales | `qwen_image_txt2img_manga.json` |
| **Animagine XL 4.0** | RAIL++-M | shojo / iyashikei / healing register where the anime-soft attractor IS the desired register | `animagine_xl_txt2img_manga.json` |
| **FLUX-schnell-fp8** | Apache 2.0 | fallback path AND the brand-2 V1 ship config (4 steps / cfg 1.0 / euler / simple); PuLID variant available for FaceNet conditioning | `flux_txt2img_manga.json` (brand-2 V1) + `flux_txt2img_manga_pulid.json` (Phase B PuLID) |

### Banned base models (license-blocked per `artifacts/research/license_risk_register_2026-04-29.md`)

- **FLUX-dev** — non-commercial license; LoRAs trained on it inherit the NC restriction. `brand_lora_plans.yaml::training_defaults.base_model` migrates to schnell or Animagine in Phase C.
- **Pony Diffusion V6 XL** — explicit no-monetization clause.
- **NoobAI XL** — explicit no-commercialization clause.
- **Illustrious-XL standalone** — base contamination blocks generated-image commercial use.

### PuLID-FaceNet identity lock

Phase B installs `lldacing/ComfyUI_PuLID_Flux_ll` (FaceNet variant) for the FLUX path and `cubiq/PuLID_ComfyUI` for the SDXL/Animagine path. Use **`PulidFluxFaceNetLoader`** specifically — `PulidFluxInsightFaceLoader` would pull the AntelopeV2 weights which are non-commercial. See `docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md` for the install procedure (venv torch-conflict caveat included).

### V2 routing summary

```
queue_panel_renders.py (extended Phase B):
  --workflow-path   → override default workflow
  --reference-image → auto-selects PuLID variant; injects image into LoadImage node

engine_router.select_engine(brand_id, genre, market_demo, color_mode, use_reference):
  color_mode=color   → FLUX-schnell + ColorManga (Phase C)
  genre ∈ Qwen-set   → Qwen-Image
  genre ∈ Animagine-set → Animagine XL 4.0
  demographic shojo / kodomomuke → Animagine
  demographic seinen / josei / mature → Qwen
  fallback           → FLUX-schnell (V1 brand-2 ship config)
```

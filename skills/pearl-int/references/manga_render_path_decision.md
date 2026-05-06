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

### Path B — RunComfy serverless ComfyUI (PAID fallback)

- **Endpoint:** `https://api.runcomfy.net/prod/v1`
- **Deployment:** `677edba8-ace0-4b2b-bad2-8e94b9959065`
- **Driver:** `scripts/image_generation/runcomfy_batch.py`
- **Workflow:** `scripts/image_generation/comfyui_workflows/flux_video_bank.json`
  (different from manga panel template — uses node-id-override pattern)
- **Cost:** ~$0.03/render (per RunComfy metering)
- **Per-batch budget:** 25-panel manga episode ≈ $0.75
- **Auth:** `RUNCOMFY_API_KEY` + `RUNCOMFY_DEPLOYMENT_ID` from Keychain
  (post PR #920 scheme: `service=phoenix-omega`, `account=NAME`)
- **KNOWN BLOCKER:** RunComfy serverless deployment holds an OLDER
  workflow bundle. Local templates updated by PR #807/#809; serverless
  rejects the new graph with HTTP 422 until re-imported via the RunComfy
  console (operator action — see `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md` §4A).
  Until re-sync, RunComfy returns the OLD schnell-mismatch outputs.

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
├── Q3: Is this a video_bank or large-batch (>100 renders) job?
│   ├── YES → Path B (RunComfy serverless, after re-sync); horizontal
│   │         scaling; cost amortizes
│   └── NO  → Path A
│
└── Q4: Are we time-critical (release deadline within hours)?
    ├── YES → operator authorizes Path B with explicit cost approval
    └── NO  → Path A (free; queue-and-wait if GPU constrained)
```

## RunComfy re-sync procedure (operator-only; ~5 min in console)

1. Open RunComfy console → Deployments → `677edba8-ace0-4b2b-bad2-8e94b9959065`
2. Re-import workflow JSON: `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json`
3. Verify `flux1-dev-fp8.safetensors` checkpoint slot is populated
4. Save deployment
5. Test: `python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run`
   — expect 8 renders × 4 genres × 2 configs = $0.24 cost; outputs at
   `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md`

After re-sync, Path B is unblocked. Until then, Path B is BROKEN; do NOT
route brand-2 panel work there even if Pearl Star is unavailable.

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

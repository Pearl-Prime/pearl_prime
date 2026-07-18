# FLUX workflow schnell→dev smoke test — 2026-04-30

**PR:** [#807](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/807) (FLUX schnell-mismatch fix) + [#809](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/809) (LoRA `base_model` sweep)
**Acceptance criterion source:** master execution brief P0.3 — *"smoke test: regenerate 1 each of (mecha, dark_fantasy, fantasy_adventure, healing-control) at the new config + side-by-side comparison committed to `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md`"*
**Status:** ⚠️ **BLOCKED on RunComfy deployment re-sync** — see §3 below

---

## 1. Configs intended for comparison

| | OLD (schnell-mismatch) | NEW (Option A — operator-approved) |
|-|-|-|
| ckpt | `flux1-schnell-fp8.safetensors` | `flux1-dev-fp8.safetensors` |
| steps | 24 | **28** |
| cfg | 4.0 | **3.5** |
| sampler | euler | **dpmpp_2m** |
| scheduler | normal | **karras** |

## 2. What was attempted

Built `scripts/image_generation/smoke_test_flux_workflow_fix.py` — minimal CLI that:

1. Constructs a 7-node FLUX txt2img workflow with the same shape as the templates edited in PR #807 (`config/comfyui_workflows/manga_covers/flux_character_portrait_template.json` and the 3 sibling workflows under `scripts/image_generation/comfyui_workflows/`)
2. Loads RunComfy creds from Keychain (`RUNCOMFY_API_KEY`, `RUNCOMFY_DEPLOYMENT_ID`)
3. Submits each genre × config pair to `submit_workflow(...)` (which `POST`s `{"workflow": <full_graph>}` to the deployment's `/inference` endpoint)
4. Polls run, downloads image, writes side-by-side artifact

Dry-run validates plan: `4 genres × 2 configs = 8 renders, ~$0.24 cost`.

```
$ python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --dry-run
Smoke test: 4 genres × 2 configs = 8 renders
Genres: ['mecha', 'dark_fantasy', 'fantasy_adventure', 'healing']
Configs: ['old', 'new']
Deployment: 677edba8-ace0-4b2b-bad2-8e94b9959065
Cost estimate: ~$0.24
DRY RUN — no API calls made.
```

## 3. Why the live render failed (THE blocker)

Real submission of `healing_old` + `healing_new` against deployment `677edba8-ace0-4b2b-bad2-8e94b9959065` returned **HTTP 422 Unprocessable Entity** for both:

```
[healing_old] submitting…
[healing_old] FAILED: 422 Client Error: Unprocessable Entity for url:
  https://api.runcomfy.net/prod/v1/deployments/677edba8-…/inference
[healing_new] submitting…
[healing_new] FAILED: 422 Client Error: Unprocessable Entity
```

**Root cause:** `scripts/image_generation/runcomfy_batch.py` lines 60-65 reveal the deployment expects **input overrides on specific node IDs** (`_NODE_POSITIVE_PROMPT = "6"`, `_NODE_SEED = "25"`), not a full arbitrary workflow graph. Our smoke runner submits a fresh 7-node txt2img graph (nodes 1–7), which the deployment rejects as schema-incompatible.

**Implication:** the schnell-fix landed in PR #807 / #809 changes the **local template files**, but the **live RunComfy serverless deployment** holds its own (older) workflow bundle. The local edits will only take effect remotely once the deployment is **re-synced** with the new template.

This is a structural property of RunComfy serverless deployments, not a bug in PR #807.

## 4. Path to actually validating the fix (operator action)

Pick one of:

### 4A. Re-deploy the workflow to RunComfy (recommended)

1. Open RunComfy console → Deployments → `677edba8-ace0-4b2b-bad2-8e94b9959065`
2. Re-import the updated workflow JSON (`scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json` — flux1-dev / steps=28 / cfg=3.5 / dpmpp_2m / karras)
3. Verify the deployment's `flux1-dev-fp8.safetensors` checkpoint slot is populated (may require uploading the checkpoint if not already on the deployment image)
4. Re-run `python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run` — should now work

### 4B. Run smoke test against a local ComfyUI instance

If a local ComfyUI server is available at `COMFYUI_URL`, refactor the smoke runner to use the local `/prompt` endpoint (`runcomfy_batch.py` line 583 shows the alternate code path). This validates the workflow JSON edit works in principle, but doesn't validate the production path.

### 4C. Bundle smoke validation into Phase 2 (defer)

Phase 2 (P2.1) includes "regenerate the 8 known stillness_press failures" using the new cookbook prompts AND the schnell-fix. If RunComfy re-deploy is non-trivial, fold the smoke validation into P2.1 — same render budget, validates fix + cookbook prompts + character-consistency pipeline together.

## 5. Genre slots (template — populate after deployment re-sync)

| Genre | OLD (schnell) | NEW (flux1-dev) | Drift improved? |
|-------|--------------|-----------------|------------------|
| mecha (failure) | _pending_ | _pending_ | _pending_ |
| dark_fantasy (failure) | _pending_ | _pending_ | _pending_ |
| fantasy_adventure (failure) | _pending_ | _pending_ | _pending_ |
| healing (control) | _pending_ | _pending_ | _pending_ |

## 6. Operator decision (2026-04-30)

**APPROVED: path 4C** — merge #807 and #809 on diff review, defer actual smoke rendering until either:
- the RunComfy deployment is re-synced (path 4A, operator-side), OR
- Phase 2 / P2.1 renders the 8 known stillness_press failures (which already plans to use the new schnell-fix + cookbook prompts together — same render budget, better signal)

**Operator directive:** *"Do not spend render budget against the old deployment because it will not validate the fix."*

This is now the load-bearing path. Future agents: do NOT attempt live renders against deployment `677edba8-…` to validate #807 / #809 — re-sync first, or wait for P2.1.

The local JSON template fix in #807 + the LoRA `base_model` sweep in #809 are **prerequisites** — the deployment re-sync (path 4A) is the **runtime activation**. Both are needed; the local fix is correct independent of activation.

**Merge gate for #807 / #809:** operator diff review — that's it.

## 7. Artifacts

- Smoke runner: `scripts/image_generation/smoke_test_flux_workflow_fix.py` (dry-run validates; real run blocked per §3)
- Run output dir: `artifacts/qa/flux_workflow_fix_smoke_2026-04-30/` (empty — no successful renders)
- This artifact: `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md`

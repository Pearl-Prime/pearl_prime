# RunComfy Deployment Sync Runbook

**Status:** Operator-actionable. **No render spend permitted by this runbook.**
**First written:** 2026-04-30 (Session 5 of the Phoenix Omega 100% production campaign)
**Owners:** Operator (RunComfy console access) + Pearl_GitHub agent (repo edits)

---

## 0. Purpose

Image generation in this repo flows through a **RunComfy serverless deployment**.
The deployment holds its own internal `workflow_api.json` (checkpoint, sampler,
scheduler, steps, cfg, negative-prompt node — all baked in). Local repo files
under `scripts/image_generation/comfyui_workflows/` and
`config/comfyui_workflows/manga_covers/` are **templates / evidence of intent**
— they are NOT the code that runs in production.

This runbook tells the operator exactly how to sync the deployment with the
repo so that future smoke renders actually validate repo workflow changes.

---

## 1. Current state (verified 2026-04-30)

| | |
|-|-|
| Engine | RunComfy serverless, US-region |
| API base | `https://api.runcomfy.net/prod/v1` |
| Deployment ID | `677edba8-ace0-4b2b-bad2-8e94b9959065` ("RunComfy/FLUX v1") |
| Auth | `Bearer $RUNCOMFY_API_KEY` (Keychain item `phoenix-omega / RUNCOMFY_API_KEY`) |
| Production callsite | `scripts/image_generation/runcomfy_batch.py::submit_inference` |
| Submission shape | `POST /deployments/<id>/inference  {"overrides": {…}}` |
| Override targets | Node `"6"` (CLIPTextEncode positive `inputs.text`) + node `"25"` (KSampler `inputs.noise_seed`) |
| What the deployment supplies (NOT in repo) | checkpoint, sampler, scheduler, steps, cfg, negative-prompt node, all other nodes |
| Local template node IDs | `1` CheckpointLoader · `2` positive · `3` negative · `5` KSampler · `7` SaveImage |
| Deployment node IDs (known) | `6` positive · `25` KSampler — the rest are unknown |

### What the API can and can't tell us

Probed 2026-04-30 with `RUNCOMFY_API_KEY`:

| Endpoint | Status |
|----------|--------|
| `GET /deployments/<id>` | 404 |
| `GET /deployments/<id>/workflow` | 404 |
| `GET /deployments` | 404 |
| `GET /v1/deployments/<id>` | 404 |
| `GET /v2/deployments/<id>` | 404 |
| `POST /deployments/<id>/inference` with `{"workflow": <full_graph>}` | **422 Unprocessable Entity** (Session 1 smoke test finding) |
| `POST /deployments/<id>/inference` with `{"overrides": {…}}` | works (production path) |

**Conclusion:** RunComfy's serverless API has **no metadata GETs**. The
deployment's `workflow_api.json` is only inspectable via the **RunComfy web
console** (https://www.runcomfy.com → Workflows → the saved deployment). The
operator must do this manually; the agent cannot.

---

## 2. The sync problem (why local repo edits don't reach production)

Session 1 PR [#807](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/807) +
[#809](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/809) edited the
local templates: `flux1-schnell-fp8 → flux1-dev-fp8`, `steps 24 → 28`,
`cfg 4.0 → 3.5`, `euler/normal → dpmpp_2m/karras`. Those PRs are merged.

But:
- **Local templates use node IDs 1–7.** `submit_inference` overrides only
  nodes `"6"` and `"25"`. The two graphs don't share schema.
- **The production deployment's saved workflow_api.json is unchanged** since
  whenever it was last deployed (per
  [`docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md`](../COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md)
  §0, this was the original cause of the chronic mecha / dark_fantasy /
  fantasy_adventure drift).
- **Therefore production renders are still using the old schnell-mismatch
  config** until the deployment is re-synced.

The repo fix is correct. The deployment activation is a separate operator step.

---

## 3. Sync paths (operator picks one)

### 3A. Re-deploy via RunComfy console (RECOMMENDED — confirms the fix and unblocks all downstream work)

**Operator-only.** Agent cannot do this.

1. Sign in to https://www.runcomfy.com.
2. **Workflows → Deployments**. Find the deployment whose ID matches
   `677edba8-ace0-4b2b-bad2-8e94b9959065`.
3. **Open it. Export the current `workflow_api.json`** to disk
   (`Download workflow JSON` or equivalent). Save it under
   `scripts/image_generation/comfyui_workflows/_deployed/runcomfy_677edba8_<date>.json`
   in a follow-up PR for repo audit trail.
4. **Confirm the symptoms:** read the `class_type: CheckpointLoaderSimple`
   node and the `class_type: KSampler` node. Verify (or refute) the schnell
   mismatch hypothesis by checking:
   - `ckpt_name` — is it `flux1-schnell-fp8.safetensors`? (mismatch confirmed)
   - `steps` — is it >4? (mismatch confirmed)
   - `cfg` — is it >1? (mismatch confirmed)
5. **Patch the workflow** in the RunComfy console UI:
   - `ckpt_name` → `flux1-dev-fp8.safetensors` (verify the deployment's image
     has this checkpoint installed; if not, upload it first)
   - `steps` → 28
   - `cfg` → 3.5
   - `sampler_name` → `dpmpp_2m`
   - `scheduler` → `karras`
   - **Add a real negative-prompt CLIPTextEncode node** if one isn't already
     present — record its node ID (let's call it `_NODE_NEGATIVE_PROMPT`)
6. **Save / re-deploy.** Note the new deployment ID if it changes; if it
   stays the same, that's ideal.
7. **Update the repo:** open a PR that
   - adds the exported workflow JSON under `_deployed/`
   - updates `runcomfy_batch.py` constants if the deployment ID changed
   - records the new `_NODE_NEGATIVE_PROMPT` constant if a negative node
     was added (so `submit_inference` can override it)

**Outcome:** production renders now use the corrected engine config.
[`scripts/image_generation/smoke_test_flux_workflow_fix.py`](../../scripts/image_generation/smoke_test_flux_workflow_fix.py)
needs a small refactor (see §5) to actually validate this — the existing
runner submits full graphs, which the deployment will continue to reject
even after re-deploy unless the deployment is configured to accept that
shape.

### 3B. Switch to full-graph submission (NOT RECOMMENDED today)

Possible if the operator configures the RunComfy deployment to accept
arbitrary `{"workflow": ...}` payloads (some RunComfy plans support this).
Higher risk: every caller in the repo would need to migrate from override
shape to full-graph shape, and every render would carry the full graph in
flight.

Skip unless 3A is somehow blocked.

### 3C. Defer to Phase 2 / P2.1 (cheap option if 3A is delayed)

The pathway doc Phase 2 deliverable P2.1 already plans to re-render the
8 known stillness_press failure images using cookbook prompts +
schnell-fix together. That work necessarily requires 3A as a precondition,
so 3A still has to happen — but the smoke comparison can be folded into
P2.1's render budget rather than a standalone validation pass.

---

## 4. Pre-sync checklist (run before any console work)

- [ ] Confirm `RUNCOMFY_API_KEY` is in Keychain: `python3 scripts/ci/load_integration_env_from_keychain.py --list | grep RUNCOMFY` should show `RUNCOMFY_API_KEY`.
- [ ] Confirm the deployment is still active: `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)" && python3 -c "import os, requests; r = requests.post(f'https://api.runcomfy.net/prod/v1/deployments/{os.environ[\"RUNCOMFY_DEPLOYMENT_ID\"]}/inference', headers={'Authorization': f'Bearer {os.environ[\"RUNCOMFY_API_KEY\"]}'}, json={'overrides': {}}, timeout=10); print(r.status_code)"` — expect 4xx (request validation, not 404). 404 = deployment retired; abort and confirm with operator.
- [ ] Confirm the operator has RunComfy console access (https://www.runcomfy.com).
- [ ] Confirm the operator knows the cost model — re-deploy doesn't bill, only renders do. Per
      [Session 1's smoke test](../../artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md),
      one image ≈ $0.03; 4 genres × 2 configs ≈ $0.24 for the comparison run.
- [ ] Confirm path 4C (defer to P2.1) is NOT preferred — if it is, stop here and capture in a project memory.

---

## 5. Post-sync smoke test command path

After 3A completes, the existing smoke runner needs **one small refactor**
before it can validate the fix. Today it uses the full-graph submission
shape (`{"workflow": <graph>}`), which doesn't match how production
renders run. Switch it to the production override shape.

The smoke command path target — to be runnable after the refactor + 3A:

```bash
# Load creds
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

# Smoke — 4 genres on the freshly-synced deployment (cost ≈ $0.12)
python3 scripts/image_generation/smoke_test_flux_workflow_fix.py --run \
    --genres mecha,dark_fantasy,fantasy_adventure,healing

# Compare against the artifact stub from Session 1
ls artifacts/qa/flux_workflow_fix_smoke_2026-04-30/
cat artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md
```

### Refactor needed first

Today's smoke runner builds a full 7-node graph and submits it via
`submit_workflow`. The deployment rejects this with HTTP 422
(see Session 1's smoke artifact §3). For real validation, the runner
should instead call `submit_inference(api_key, deployment_id, positive_prompt, seed)`
with prompts for each of the 4 genres (no per-config split — the deployment's
config is the only one that matters once 3A lands).

Suggested refactor scope for a follow-up PR:

- Replace `build_workflow(...)` + `submit_workflow(...)` calls in
  `smoke_test_flux_workflow_fix.py` with `submit_inference(...)` from
  `runcomfy_batch.py`.
- Drop the `--config old/new` flag. Once 3A lands, only one config exists
  (the synced one). The smoke run becomes a 4-prompt sanity check, not a
  before/after comparison.
- For a real before/after: capture screenshots of the OLD deployment outputs
  via the RunComfy console history before doing the re-deploy in 3A. Save
  them as `artifacts/qa/flux_workflow_fix_smoke_2026-04-30/<genre>_old.png`
  by hand. The new outputs become `<genre>_new.png` after the smoke run.

This refactor is **not in this PR** (Session 5 is documentation only). It
becomes Session 7 work or operator-attended after 3A.

---

## 6. Cost / risk envelope

| Action | Cost | Risk |
|--------|------|------|
| Read this runbook | $0 | none |
| Probe deployment via API GET (404s only) | $0 | none |
| RunComfy console open + read existing workflow | $0 | low — read-only |
| Console patch + re-deploy (path 3A) | $0 | medium — backs out by re-uploading the saved old `workflow_api.json` |
| Smoke render (4 genres, after refactor) | ≈ $0.12 | low — bounded |
| Full failure-genre re-render (8 images, P2.1) | ≈ $0.24 | low |

---

## 7. Operator action items (ordered)

1. **Operator → RunComfy console** — pull current `workflow_api.json`,
   confirm/refute schnell-mismatch, patch + re-deploy per §3A.
2. **Operator → repo** — open a follow-up PR adding
   `scripts/image_generation/comfyui_workflows/_deployed/runcomfy_677edba8_<date>.json`
   and any constant updates to `runcomfy_batch.py`. Reference this runbook.
3. **Agent (Session 7+ or operator-attended)** — refactor
   `smoke_test_flux_workflow_fix.py` to use `submit_inference` (override
   shape). One small PR.
4. **Operator → run smoke** with the refactored runner; produce side-by-side
   artifact at
   [`artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md`](../../artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md)
   §5 (existing stub).
5. **Operator approval gate:** if 3 of 3 failure genres improve and healing
   control holds, mark PR #807 + #809 acceptance criterion green; otherwise
   escalate to Phase 2 / P2.1 (LoRAs + cookbook prompts).
6. **Once green** — the path opens for cover regeneration (Session 6 plan).

---

## 8. References

- [Session 1 smoke artifact](../../artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md) — the original 422 finding
- [`scripts/image_generation/runcomfy_batch.py`](../../scripts/image_generation/runcomfy_batch.py) — production submission code
- [`scripts/image_generation/smoke_test_flux_workflow_fix.py`](../../scripts/image_generation/smoke_test_flux_workflow_fix.py) — current (mismatched-shape) smoke runner
- [`docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md`](../COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md) — drift autopsy, §0 NEXT_ACTION matches §3A above
- [`artifacts/research/drift_autopsy_2026-04-29.md`](../../artifacts/research/drift_autopsy_2026-04-29.md) — the autopsy that motivated PR #807
- PRs [#807](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/807), [#809](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/809) — local template + LoRA `base_model` fixes

---

## 9. What this PR (Session 5) ships

This document. **No code changes.** No render budget spent. The runbook is
the deliverable; the actions inside it are operator + future-session work.

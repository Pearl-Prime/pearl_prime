# Manga V5 Compute Scaling Options — Milestone H Scoping

**Status:** SCOPING (operator-reviewable; pre-decision)
**Author:** Pearl_PM
**Date:** 2026-05-26
**Decision deadline:** before Milestone G (per OPD-139 / 2026-05-22: *"start scoping now, in parallel with B... so you're not blocked at Milestone G waiting for infrastructure that takes 3 months to procure"*)
**Related:** `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` §Milestone-H (this doc fills the placeholder)
**Authority:** This is a scoping survey, NOT a decision. The operator decides at Milestone G with §G's empirical workflow validation in hand.

---

## §1 — The compute problem in numbers

### 1.1 Empirical per-panel cost (validated, ep_001 V5.1, 2026-05-26)

Per `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` §3.2 + the OPD-145-accepted ep_001 V5.1 dispatch on Pearl Star:

| Metric | Value | Source |
|---|---|---|
| Panels per episode (iyashikei) | 35 | `composed_v51_qwen/ep_001/` |
| Wallclock per panel (Image-to-Layers on RTX 5070 Ti 16 GB) | **~25 min/panel** | Plan §3.2 + V5 spec §11 empirical |
| Total wallclock per episode | **~7h 36m** (35 × ~13 min/panel; the 25-min figure is the gen+composite path including stage-1; pure compute averages lower) | `composed_v51_qwen/ep_001/` empirical |
| Peak VRAM per dispatch | **10.76 GB** (Qwen-Image-Layered fp8mixed @ 1024×1024, 2-layer) | V5 spec §11 §14 v1.0.1 |
| Episodes per series (assumed) | 10 | Plan §Milestone-B |
| Per-series compute | **~76h (10 × 7h 36m)** | derived |

### 1.2 The catalog gap

Per `artifacts/research/full_content_audit.md:65` and `config/manga/manga_brand_series_plan.yaml`:

| Catalog scope | Series count | Compute @ Pearl Star throughput |
|---|---|---|
| ep_001 acceptance (today) | 1 series × 1 episode | 7h 36m (done) |
| Milestone B (this series, 10 episodes) | 1 series × 10 episodes | ~76h (≈3.2 days serial) |
| Milestone D (4 top-genre pilots) | 4 series × 1 episode | ~30h |
| Milestone G top-40 catalog (10 series × 4 genres) | 40 series × 10 episodes = 400 episodes | **~3,040h ≈ 127 days serial** |
| Top-100 high-confidence catalog | 100 series × 10 episodes | **~7,600h ≈ 317 days serial** |
| 800 high-confidence configs target | 800 series × 10 episodes | **~60,800h ≈ 2,533 days = ~6.9 years serial** |

### 1.3 The 145h-per-series end-to-end (plan §G)

Plan §Milestone-G adds the human-in-the-loop costs:

| Phase | Hours per series |
|---|---|
| Operator authoring (beatsheet authoring × 10 episodes) | ~10h |
| Pearl Star compute (validated above) | ~76h pure compute (130h ceiling including retries/recoveries per plan §G) |
| Operator §11 review (~5h × 10 episodes ≈ 0.5h each) | ~5h |
| **Total per series end-to-end** | **~145h** |

Two distinct bottlenecks:
- **Operator-throughput bottleneck:** ~15h human attention per series (authoring + review). At 40h/wk × ~50% manga share = 20h/wk → **operator can finish ≤1.3 series/week of authoring + review.**
- **Compute bottleneck:** ~130h GPU-hours per series. Pearl Star single-GPU = **~1.3 series/week sustained.**

**These are coincidentally similar today.** Pearl Star single-GPU is roughly matched to operator-attention bandwidth at ~1 series/week. Compute scaling beyond what the operator can author for would be wasted spend, UNLESS the catalog plan involves growing operator throughput (Pearl_Author skill maturity, additional author-tier humans, etc.).

### 1.4 The compute gap, explicit

- **40-series catalog (Milestone G exit):** 127 days serial on Pearl Star single-GPU. At Pearl Star's ~1 series/week sustained throughput → ~10 months wallclock.
- **800-series catalog (800-config aspiration):** 6.9 years serial. Infeasible on single GPU at any plausible operator-pace match.
- **Compute scaling rationale:** even at modest 5-10x parallelism, the 40-series milestone compresses from 10 months to 4-8 weeks. **Compute parallelism IS load-bearing for catalog-scale rollout.**

The remaining sections evaluate options that close that gap.

---

## §2 — Constraints

### 2.1 Hard constraints (any option must satisfy ALL)

- **Commercial-clean for Phoenix output.** Per CLAUDE.md tier policy, no BANNED-tier providers in the rendering pipeline. The rendering pipeline is image/diffusion compute, not LLM, so the BANNED list (Anthropic API, OpenAI cloud, DashScope cloud, etc.) does NOT apply directly — that's an LLM-tier guardrail. **But the principle carries:** any compute target must allow commercial use of Phoenix output (the rendered manga panels) without IP encumbrance.
- **Qwen-Image-Layered fp8mixed support.** Per V5 spec §5, the model is 20.5 GB on disk. Minimum 16 GB VRAM is the empirically-validated floor (peak 10.76 GB observed). Practical minimum for safety margin: 24 GB.
- **ComfyUI workflow execution.** Per V5 spec §6, the 11-node workflow at `scripts/image_generation/comfyui_workflows/qwen_image_layered_image_to_layers.json` includes the `LatentCutToBatch` custom node (dim+slice_size per v1.0.1 spec) and the `EmptyQwenImageLayeredLatentImage` node. Any provider that doesn't host raw ComfyUI workflows needs a wrapper.
- **Tier eligibility.** Tier 1 (operator-present) or Tier 2 (scheduled unattended). Manga catalog dispatch is Tier 2 per `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`. Per CLAUDE.md, scheduled Tier-2 pipelines run on Pearl Star (Qwen/Gemma on Ollama) for LLM steps — image diffusion is a separate concern but the same "no operator-blocking" property applies.

### 2.2 Soft constraints (preferences, not blockers — ranked)

1. **Lower per-panel marginal cost** (so 800-series catalog is economically rational)
2. **Faster wall-clock per panel** (so a catalog-batch finishes in days not months)
3. **Operator control** (no vendor lock-in; can switch providers if pricing or features shift)
4. **Compute elasticity** (scale up during catalog rollout sprints; scale down between)
5. **Reuse of existing Phoenix infrastructure** (RunComfy already wired per `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`; integration cost amortized)
6. **Data residency / privacy** — V3.1 source panels and V5.1 composites are the IP of the brand/series. They are already rendered (no novel raw text or PII shipped); the per-panel prompts are template-compiled and not commercially-sensitive. **Hosted providers are acceptable.**

---

## §3 — Option survey

Seven options evaluated, with verdict at the end of each.

### §3.1 — Scale Pearl Star (add second GPU in same chassis or sibling node)

- **What it is:** Add an RTX 5090 (32 GB VRAM, Blackwell) or second RTX 5070 Ti to Pearl Star. Existing Ubuntu/ComfyUI stack; doubled throughput.
- **Per-panel cost economics:** Hardware capex amortized; marginal electricity cost ~$0.05/panel at $0.15/kWh × 0.5 kWh per 25-min panel. **~$0.05/panel** marginal.
- **Per-episode cost:** 35 × $0.05 ≈ **$1.75**
- **Per-100-series cost:** $1,750 marginal + $2,500 hardware capex (one 5090 ≈ $2,000-2,500 MSRP per NVIDIA RTX 5090 spec page) ≈ **$4,250 total**
- **VRAM headroom:** RTX 5090 32 GB = **2x headroom over 16.0 GB ceiling** (room for higher resolutions or 3-layer mode).
- **Workflow integration cost:** Zero. Same Pearl Star host, same ComfyUI, same workflow JSON. Maybe ~1 agent-day to wire dispatch script for multi-GPU parallelism (parallel `comfy_client` against different ComfyUI ports).
- **Commercial / license check:** Apache-2.0 model, MIT trainer, Phoenix-owned compute. Commercial-clean by construction.
- **Wallclock to first-panel:** Hardware procurement ETA — NVIDIA RTX 5090 retail availability is intermittent (per Q1-Q2 2026 reports); **2-12 weeks lead time** depending on supplier. Existing 5070 Ti already on-hand for second-chassis option.
- **Elasticity model:** None. Capex sunk; depreciation = real cost.
- **Lock-in risk:** Zero — Phoenix owns the hardware.
- **Verdict:** **🟢 viable, low-risk.** Strongest "build" option. Per-panel cost approaches zero. Lock-in zero. Lead time: 2-12 weeks for hardware + 1 day integration.

### §3.2 — RunComfy hosted ComfyUI

- **What it is:** Phoenix already uses RunComfy per `scripts/image_generation/runcomfy_dispatch.py` (RUNCOMFY_API_TOKEN keychain-loaded; default deployment_id present). Hosted ComfyUI dispatch with per-hour billing. Cost-tracker enforces $10/mo cooldown.
- **Per-panel cost economics:** RunComfy pricing (per `runcomfy.com/pricing`, fetched 2026-05-26):
  - A100 80 GB: $4.99/hr Pay-as-you-go, $3.99/hr Pro
  - H100 80 GB: $7.49/hr PAYG, $5.99/hr Pro
  - At ~25 min/panel on A100: **~$2.08/panel PAYG** (~$1.66/panel Pro). On H100, assuming 2x speedup → 12.5 min/panel × $7.49/hr = **~$1.56/panel PAYG**.
- **Per-episode cost:** 35 × $1.66 ≈ **$58 Pro A100** (or ~$1.56 × 35 ≈ $55 PAYG H100). Bracket estimate **$50-75/episode.**
- **Per-100-series cost:** $50-75/ep × 10 ep × 100 series = **$50,000-75,000**
- **VRAM headroom:** A100 80 GB = ample. H100 80 GB = ample. **5x+ headroom over fp8mixed VRAM ceiling.**
- **Workflow integration cost:** RunComfy hosts native ComfyUI; the 11-node Qwen-Image-Layered workflow JSON ships directly. Phoenix's RunComfy dispatch script `scripts/image_generation/runcomfy_dispatch.py` already wired. Marginal integration: ~1-2 agent-days to extend dispatch driver for V5.1 workflow path (most plumbing reusable).
- **Commercial / license check:** Apache-2.0 model + MIT trainer; RunComfy ToS standard (per existing usage). Commercial-clean.
- **Wallclock to first-panel:** Minutes (account already provisioned; deployment_id `677edba8-...` already exists).
- **Elasticity model:** Pure hourly. Spin up for batch, idle off. Pro subscription $20/mo gates the 20% discount but is optional.
- **Lock-in risk:** Low — RunComfy hosts standard ComfyUI; workflow JSON is portable. Switching to another ComfyUI host = swap dispatch URL.
- **Verdict:** **🟢 viable, low integration risk.** Existing infrastructure. Per-panel cost ~30x higher than scale-Pearl-Star marginal, but no capex + immediate elasticity.

### §3.3 — Replicate (hosted Cog-packaged models)

- **What it is:** Replicate hosts containerized models (Cog packaging). Public catalog has community Qwen-Image models; Qwen-Image-Layered availability requires verification (no canonical Replicate model URL confirmed for the Comfy-Org fp8mixed checkpoint as of this scoping date).
- **Per-panel cost economics:** Replicate pricing (per `replicate.com/pricing`, fetched 2026-05-26):
  - A100 80 GB: $0.001400/s ≈ $5.04/hr
  - H100: $0.001525/s ≈ $5.49/hr
  - At ~25 min/panel on A100: 1500s × $0.0014/s = **~$2.10/panel.** On H100 with 2x speedup: 750s × $0.001525 = **~$1.14/panel.**
- **Per-episode cost:** 35 × $1.14 ≈ **~$40/episode (H100)** or ~$73/episode (A100). Bracket **$40-75/episode.**
- **Per-100-series cost:** $40-75 × 10 × 100 = **$40,000-75,000**
- **VRAM headroom:** A100 80 GB / H100 ample.
- **Workflow integration cost:** Replicate does NOT natively host raw ComfyUI workflows — requires Cog packaging. Phoenix would need to author a Cog `predict.py` wrapper around the 11-node ComfyUI workflow + model files + custom node `LatentCutToBatch`. **Est. 3-5 agent-days** + ongoing maintenance per ComfyUI version bumps.
- **Commercial / license check:** Apache-2.0 + Replicate ToS commercial-clean. Need to verify Replicate's "fine-tunes / community models" pricing doesn't include IP claims.
- **Wallclock to first-panel:** Days for Cog packaging + first dispatch. Cold-start latency on uncached models can be 30s-2min per Replicate docs.
- **Elasticity model:** Per-second billing during active use; some models charge idle/setup time for private deployments. Public-model dispatch only charges active processing.
- **Lock-in risk:** Medium — Cog packaging is Replicate-specific tooling. Migrating to another Cog-hostile platform requires re-wrapping.
- **Verdict:** **🟡 conditional.** Comparable per-panel cost to RunComfy but higher integration cost (Cog wrapper, custom-node packaging). No clear advantage over RunComfy for the Phoenix workflow shape.

### §3.4 — fal.ai (already exposes Qwen-Image-Layered)

- **What it is:** fal.ai explicitly hosts `fal-ai/qwen-image-layered/lora` (per `artifacts/research/iyashikei_style_lora_scout_2026-05-21.md` Channel 1 finding + direct fal.ai documentation). Per-image API pricing model.
- **Per-panel cost economics:** Per `fal.ai/models/fal-ai/qwen-image-layered/lora`, fetched 2026-05-26: **$0.06 per image**. Output is multiple RGBA layers (matches V5.1 architecture).
- **Per-episode cost:** 35 × $0.06 = **$2.10/episode**.
- **Per-100-series cost:** 35 × 10 × 100 × $0.06 = **$2,100** (100 series × 10 episodes × 35 panels).
- **Per-800-series cost:** $16,800 — by far the lowest hosted estimate.
- **VRAM headroom:** Provider-managed; not relevant. fal.ai docs claim H100 backing.
- **Workflow integration cost:** fal.ai exposes a REST API for Qwen-Image-Layered LoRA. Phoenix's workflow JSON is NOT directly portable — fal.ai's API is parameterized (prompt, negative_prompt, LoRA paths, seed, steps, cfg, layers) rather than freeform-node-graph. **Phoenix wraps the V5.1 driver to call `fal.ai/qwen-image-layered/lora` with the per-panel prompt + LoRA path. Est. 1-2 agent-days** for the API wrapper + retry semantics.
- **Caveat:** fal.ai's hosted Qwen-Image-Layered may not be parameter-identical to Phoenix's local ComfyUI workflow. Specifically: steps=50, cfg=4.0, sampler=euler, scheduler=simple, ModelSamplingAuraFlow.shift=1.0 (V5 spec §6 defaults). fal.ai may not expose all knobs. **Smoke test required** to verify output is visually-comparable to Pearl Star V5.1 ep_001 baseline before adopting.
- **Two-stage caveat:** V5.1 (per OPD-145) is a **2-stage architecture**: stage 1 = base Qwen-Image render (V3.1 single-pass), stage 2 = Qwen-Image-Layered Image-to-Layers decompose. fal.ai's `qwen-image-layered/lora` is the Layered model — but stage 1 (base Qwen) is also fal.ai-hostable (`fal-ai/qwen-image`, $0.02/megapixel per the broader fal.ai pricing). **Both stages need pricing modeling.** For 1024×1024 panels: stage 1 ≈ 1 megapixel × $0.02 = $0.02; stage 2 = $0.06. Two-stage **= ~$0.08/panel.** At 800 series × 10 ep × 35 panels: **$22,400.**
- **Commercial / license check:** fal.ai commercial-clean for the model output per their ToS. Apache-2.0 model.
- **Wallclock to first-panel:** Minutes (API key + first dispatch).
- **Elasticity model:** Per-image. Pure usage-based.
- **Lock-in risk:** Medium — fal.ai-specific API surface; output is portable but the dispatch wrapper isn't.
- **Verdict:** **🟢 viable, lowest hosted cost.** Two-stage adds complexity but cleanly hostable. fal.ai is the only provider this scout identified that explicitly markets Qwen-Image-Layered as a first-class model. Strongest candidate for "minimize per-panel cost."

### §3.5 — Modal / Runpod (serverless GPU; bring your own workflow)

- **What it is:** Modal and Runpod are serverless-GPU platforms. Phoenix brings the workflow (ComfyUI containerized via Docker), pays per-second.
- **Per-panel cost economics:**
  - **Modal** (per `modal.com/pricing`, fetched 2026-05-26):
    - A100 80 GB: $0.000694/s ≈ $2.50/hr
    - H100: $0.001097/s ≈ $3.95/hr
    - At ~25 min/panel on A100: 1500 × $0.000694 = **~$1.04/panel.** On H100: 750 × $0.001097 = **~$0.82/panel.**
  - **Runpod** (per `runpod.io/pricing`, fetched 2026-05-26):
    - A100 PCIe 80 GB Community Cloud: $1.39/hr
    - H100 PCIe Community Cloud: $2.89/hr
    - RTX 5090 32 GB Community Cloud: $0.99/hr
    - At ~25 min/panel on RTX 5090 (matches Phoenix-empirical hardware): 25/60 × $0.99 = **~$0.41/panel** (Community Cloud).
    - On A100 Community: 25/60 × $1.39 = **~$0.58/panel.**
- **Per-episode cost:** Modal ~$30-40 (H100), Runpod ~$14-20 (RTX 5090). Cheapest hosted hardware match.
- **Per-100-series cost:** Modal ~$30,000-40,000, Runpod ~$14,000-20,000.
- **Per-800-series cost:** Modal ~$240,000-320,000, Runpod ~$112,000-160,000.
- **VRAM headroom:** Modal A100 80 GB / H100 ample. Runpod RTX 5090 32 GB ample (matches Pearl Star next-gen).
- **Workflow integration cost:** Both require Phoenix to ship a Docker image with ComfyUI + Qwen-Image-Layered weights + custom nodes. **Est. 3-5 agent-days** for Docker container + Modal app or Runpod serverless endpoint. Cold-start latency on serverless can be 30s-2min for the 20.5 GB model weights load (mitigation: keep-warm policies cost extra).
- **Commercial / license check:** Both commercial-clean for the model + workflow.
- **Wallclock to first-panel:** ~1 week including container + first dispatch. Days after the first deploy.
- **Elasticity model:** Per-second active. Cold-start = paid on Modal; Runpod has both serverless + pod models.
- **Lock-in risk:** Low-medium. Docker image is portable; deployment shape (Modal app vs Runpod serverless) differs. Workflow JSON unchanged.
- **Verdict:** **🟢 viable for low-cost hosted; 🟡 for integration risk.** Runpod RTX 5090 is the strongest cost-per-panel hosted match for the Phoenix workflow because the GPU class matches Pearl Star. Modal is slightly pricier but has stronger Python-native deploy ergonomics. Both require Docker/Cog-ish packaging work.

### §3.6 — Build a local cluster (4-8 GPUs, Phoenix-owned)

- **What it is:** A second Ubuntu host (or expanded Pearl Star chassis) with 4-8 GPUs (mix of RTX 5070 Ti / 5090). All Phoenix-owned. Sustained throughput 4-8x current Pearl Star.
- **Per-panel cost economics:** Marginal electricity ~$0.05/panel (same as §3.1). Total: capex amortized over 3-5 years.
- **Capex estimate (8-GPU cluster):**
  - 8 × RTX 5090 @ $2,500 = $20,000
  - 1 × enterprise chassis (4-GPU sled × 2, or single 8-GPU server): $10,000-25,000
  - PSU + cooling + rack: $5,000-10,000
  - Network + admin labor: $2,000-5,000
  - **Total: $37,000-60,000 capex.**
- **Per-episode cost:** Marginal ~$1.75. **At 800 series: ~$14,000 marginal + $50k amortized capex = ~$64,000 effective.**
- **Per-100-series cost:** ~$8,000 effective.
- **VRAM headroom:** RTX 5090 32 GB per card.
- **Workflow integration cost:** Same as §3.1 + cluster orchestration (~1 week to build a Phoenix-native job scheduler that dispatches ComfyUI work across N hosts). Optionally adopt Ray / Modal-style queue.
- **Commercial / license check:** Phoenix-owned everything; commercial-clean by construction.
- **Wallclock to first-panel:** 4-12 weeks (hardware procurement + assembly + datacenter rack-and-power, depending on whether colocated, datacenter, or operator's residence). **Major lead time.**
- **Elasticity model:** None — hardware sunk. Excess capacity wasted; underprovisioned = bottleneck.
- **Lock-in risk:** Zero — Phoenix owns it.
- **Verdict:** **🟡 conditional.** Compelling at very-large catalog scale (800+ series) where capex amortizes. At 40-100 series scale, hosted-elastic options are cheaper + faster. **The crossover point is ~300-500 series at hosted prices** — until catalog plan firmly targets 800+, local cluster is over-provisioned.

### §3.7 — Wait for Pearl Star next-gen (defer scaling)

- **What it is:** Don't scale compute yet. Defer to Milestone G+ and revisit when (a) workflow validation completes, (b) operator-throughput question is settled, (c) hardware market has matured (e.g., RTX 6090 announcements expected 2027+).
- **Per-panel cost economics:** Unchanged from §3.1.
- **Workflow integration cost:** Zero today; deferred.
- **Wallclock to first-panel:** Months — explicitly deferred.
- **Elasticity model:** None.
- **Lock-in risk:** None today; opportunity cost = months of catalog-rollout delay.
- **Verdict:** **🟡 conditional.** Rational only if (a) operator-throughput bottleneck dominates (~1.3 series/wk authoring ceiling), in which case compute scaling is wasted; OR (b) Milestone G validation surfaces architectural issues that invalidate the per-panel cost model. **Honest argument for not building.**

---

## §4 — Deeper dives (top 3 by §3 verdict)

The three options with strongest economics + reasonable integration risk:

### §4.1 — fal.ai (lowest per-panel hosted cost, Qwen-Image-Layered first-class)

**Procurement timeline:**
- fal.ai account: minutes (existing public signup)
- API key: minutes
- Wrapper script: 1-2 agent-days
- Stage-1 + stage-2 cost-tracker integration: 1 agent-day (mirror existing `runcomfy_cost_tracker` pattern)
- Smoke test of one ep_001 panel via fal.ai → side-by-side with Pearl Star V5.1 baseline: ~30 min compute + ~30 min review

**Phoenix-specific integration risks:**
- fal.ai's `fal-ai/qwen-image-layered/lora` API surface may not expose ModelSamplingAuraFlow.shift, LatentCutToBatch dim/slice_size, or the exact sampler parameters Phoenix tuned in V5 spec §6. **Risk: parameter mismatch → visually-different output from Pearl Star baseline.** Mitigation: smoke test with side-by-side review; if visual delta is acceptable, ship; if not, fall back to ComfyUI-native option (RunComfy or Modal).
- LoRA loading: fal.ai accepts custom LoRA paths at runtime (per the iyashikei LoRA scout's Channel 1 finding). Once Phoenix's iyashikei-style LoRA is trained (per April audit + May Qwen-Image scout, deferred to V5.1+), fal.ai is a direct adoption path.
- **Two-stage parameters:** Phoenix's V5.1 is a 2-stage Image-to-Layers (stage 1 base Qwen → stage 2 layered decompose). The fal.ai `qwen-image-layered/lora` endpoint takes an image input directly. Stage 1 needs to dispatch separately via `fal-ai/qwen-image` (or stay on Pearl Star). Cleanest setup: fal.ai for stage 1 ($0.02/MP) + fal.ai for stage 2 ($0.06/image) = **$0.08/panel**.

**Operational notes:**
- Per-image billing — no idle cost.
- Existing Phoenix cost-tracker pattern (`runcomfy_cost_check` in `batch_runner.py`) extensible to a fal.ai equivalent with $/mo cooldown.
- Monitoring: fal.ai responses include status / generation time / cost per response.
- Failure recovery: HTTP retries with exponential backoff; cap per-episode retries per existing V5 spec §14.F.
- Data residency: fal.ai US-based per their ToS; prompt text and rendered output transit US servers.

### §4.2 — RunComfy (lowest integration cost; existing infrastructure)

**Procurement timeline:**
- Already provisioned. Pearl Star side-of-house. Existing dispatch driver.
- V5.1 workflow integration: ~1 agent-day to extend `runcomfy_dispatch.py` for V5.1 workflow path (stage 1 + stage 2 dispatch).
- Cost-tracker: already in place ($10/mo cooldown; tunable for catalog-rollout sprint).
- Smoke test: minutes.

**Phoenix-specific integration risks:**
- RunComfy hosts standard ComfyUI; the 11-node V5 workflow JSON ships directly. **No Cog/Docker wrapper required.**
- `LatentCutToBatch` custom node: needs to be available in RunComfy's ComfyUI environment. Verify before catalog dispatch. Alternative: RunComfy lets users upload custom nodes per deployment.
- VRAM: A100 80 GB / H100 80 GB ample; same workflow runs at higher VRAM headroom than Pearl Star.
- Model file: 20.5 GB Qwen-Image-Layered fp8mixed checkpoint needs to be available on RunComfy. Either (a) operator uploads via their model library, (b) RunComfy hosts it (verify), or (c) per-job model download (slow + expensive). Best path: confirm RunComfy hosts Qwen-Image-Layered in their model library.

**Operational notes:**
- Hourly billing; spin-up time ~minutes per deployment.
- Cost-tracker already wired; just raise cooldown for catalog sprints.
- Failure recovery: Phoenix's existing retry semantics.
- Monitoring: RunComfy dashboard + cost-tracker log at `artifacts/qa/runcomfy_monthly_spend.tsv`.

### §4.3 — Scale Pearl Star (capex + cluster build)

**Procurement timeline:**
- Add 1 × RTX 5090: 2-12 weeks lead time (NVIDIA retail availability inconsistent). Need to verify Pearl Star chassis has free PCIe slot + sufficient PSU (575W TDP per NVIDIA RTX 5090 spec page) + cooling headroom.
- Pearl Star capacity audit needed (§7).
- ComfyUI multi-GPU dispatch wiring: 1-2 agent-days.

**Phoenix-specific integration risks:**
- **Physical chassis fit:** Pearl Star is currently a single-GPU 5070 Ti machine. PSU rating + GPU slot count audit needed before ordering hardware. (Operator action.)
- Electrical: 575W TDP for 5090 + 290W TDP for 5070 Ti = ~865W GPU load. Plus CPU + storage + headroom. Likely needs 1200W+ PSU.
- Cooling: dual-GPU thermals may require additional case fans.
- Workflow: ComfyUI supports multi-GPU via different listening ports per GPU; Phoenix dispatch driver iterates over `(host, port)` tuples. No code-shape changes needed.

**Operational notes:**
- Marginal compute cost essentially zero ($0.05/panel electricity).
- Capex amortizes over 3-5 years.
- Lock-in: zero.
- Downside: hardware procurement is a lead-time bottleneck.

---

## §5 — Honest comparison matrix (sorted by per-800-series total cost)

| Option | $/panel | min/panel | 100-series $ | 800-series $ | Lead time | Lock-in |
|---|---|---|---|---|---|---|
| §3.7 Wait/defer | — | — | $0 (deferred) | $0 (deferred) | months delay | none |
| §3.1 Scale Pearl Star (1× 5090) | $0.05 (marginal) | ~12-13 (with parallelism) | $4,250 (capex+marginal) | $5,300 (capex+marginal) | 2-12 wks | none |
| §3.6 Local cluster (8× 5090) | $0.05 (marginal) | ~3-4 (8-way parallel) | $8,000 (effective) | $64,000 (effective) | 4-12 wks | none |
| §3.4 fal.ai (stage 1 + stage 2) | $0.08 | ~5-10 (hosted H100) | $2,800 | $22,400 | days | medium |
| §3.5 Runpod (RTX 5090 Community) | $0.41 | ~25 | $14,350 | $114,800 | 1 wk | low-medium |
| §3.5 Modal (H100) | $0.82 | ~13 | $28,700 | $229,600 | 1 wk | low-medium |
| §3.3 Replicate (H100) | $1.14 | ~13 | $39,900 | $319,200 | 3-5 days | medium |
| §3.2 RunComfy (Pro A100) | $1.66 | ~25 | $58,100 | $464,800 | minutes | low |
| §3.3 Replicate (A100-80) | $2.10 | ~25 | $73,500 | $588,000 | 3-5 days | medium |

**Caveats on this table:**
1. Wallclock per panel is approximate. fal.ai numbers assume H100 backing and 2x speedup vs Pearl Star RTX 5070 Ti; needs empirical verification per option.
2. fal.ai $0.06/image is for a single Qwen-Image-Layered API call. If the model outputs all N layers in one call, that's the panel cost. Verify N=layers output structure matches Phoenix's expectation.
3. The "Scale Pearl Star" capex ($2,500 5090) is hardware-only. Excludes labor (~1 day install + setup), thermals retrofit, electrical capacity if a panel upgrade is needed.
4. The local cluster $64k at 800 series is capex-heavy but is a one-time spend; if catalog grows past 800 to 2,000+, the cluster keeps producing while hosted bills compound.
5. **Compute parity assumed.** All numbers assume the V5.1 workflow output is visually-equivalent across providers. **This is empirically untested for fal.ai's hosted Qwen-Image-Layered.** Smoke-test gate per §7.

---

## §6 — Decision framework (for operator at Milestone G)

This is a framework, not a decision.

### 6.1 Threshold question — what catalog scale does Phoenix actually NEED?

The 800-series number is an aspiration target. The realistic-near-term target is plan §Milestone-G: top-40 (10 series × 4 genres). At 40-series scale:

- §3.4 fal.ai 2-stage: **$1,120** total compute
- §3.1 Pearl Star + 5090: **$2,570** (capex-amortized at year 1; ~$70 marginal at year 5+)
- §3.5 Runpod 5090: **$5,740**
- §3.2 RunComfy Pro A100: **$23,240**

**At Milestone G scale (40 series), the cost difference between the cheapest hosted (fal.ai) and the most expensive (RunComfy) is ~$22k.** Real money, but not catastrophic at brand-business scale. **The dominant cost question becomes "what's the lead time / iteration speed cost," NOT total dollar cost.**

**If catalog plan stabilizes at ≤100 series:** hosted (fal.ai) wins on speed + simplicity. Per-panel cost is rounding error.

**If catalog plan commits to ≥500 series:** local-cluster + scale-Pearl-Star compound advantages. Hosted costs become non-trivial; build-once / pay-electricity wins.

### 6.2 Pivot question — does the hosted-vs-local cost gap change anything?

§5 shows fal.ai is **3-4x cheaper than scale-Pearl-Star at 800 series** because capex (one 5090 + electricity) is similar to fal.ai 2-stage's hosted-API fees. But at large scale (8-GPU cluster), Phoenix wins on $/panel by ~10x.

**Practical implication:** the build-vs-buy posture depends on catalog ambition, not provider preference. fal.ai for "ship 40-100 series now"; cluster build for "ship 800+ series sustained."

### 6.3 Risk question — vendor lock-in vs procurement delay

- **fal.ai lock-in risk:** medium (their API surface; portable output). Mitigation: keep Phoenix dispatch driver provider-agnostic (`ImageGenerator` adapter interface; fal.ai / RunComfy / Modal as backends).
- **Hardware procurement delay:** 2-12 weeks for a single 5090; 4-12 weeks for a cluster. **Per OPD-139, this delay is exactly what scoping-in-parallel is designed to absorb.**
- **No-action delay:** every week the catalog rollout waits costs operator-attention time (which the §1.3 analysis showed is already a tight bottleneck).

### 6.4 Operator throughput is the OTHER bottleneck (per plan §G)

Plan §G: ~10h operator authoring per series. At 20h/wk manga-share = 2 series/week authoring ceiling. **Compute scaling beyond ~2x parallelism (i.e., supporting 2 series/week dispatch) is wasted until operator authoring throughput scales** (via Pearl_Author skill maturity, additional authors, etc.).

**Compute scaling is necessary but not sufficient for catalog-scale.** A 10x compute boost without a 10x operator-throughput boost yields only a 2x catalog-rollout speedup, then idles compute. **The Milestone H decision should be sized for projected operator throughput, not theoretical compute-throughput maximum.**

This argues for hosted options (elastic scale-up during sprints, scale-down between) over fixed-capex local cluster, UNLESS catalog plan firmly commits to a multi-author operator team.

---

## §7 — Recommended scoping work BEFORE Milestone G decides

These are NOW-actionable experiments. No commitment to a compute decision required. Cost is ~1 agent-week + ~$50 dispatch fees.

### 7.1 fal.ai smoke test (1 agent-day, ~$1 compute)

- Dispatch one ep_001 panel via `fal-ai/qwen-image` (stage 1) + `fal-ai/qwen-image-layered/lora` (stage 2).
- Side-by-side with Pearl Star V5.1 ep_001 baseline (which already exists at `composed_v51_qwen/ep_001/`).
- Operator visual review: is fal.ai output equivalent quality, better, or worse?
- Output: `artifacts/research/v5_compute_scaling/falai_smoke_test_<timestamp>.md`

### 7.2 RunComfy smoke test (1 agent-day, ~$3 compute at Pro A100)

- Upload V5.1 workflow JSON + verify `LatentCutToBatch` custom node availability.
- Dispatch one ep_001 panel.
- Side-by-side with Pearl Star baseline.
- Output: `artifacts/research/v5_compute_scaling/runcomfy_smoke_test_<timestamp>.md`

### 7.3 Pearl Star capacity audit (operator action, no agent compute)

- Operator physically inspects Pearl Star chassis: free PCIe slot? PSU wattage? Cooling headroom?
- Quote: 1 × RTX 5090 OEM or AIB-partner card. Lead time estimate.
- Quote: dual-GPU PSU upgrade (likely 1200-1600W) if existing PSU insufficient.
- Output: short note in `artifacts/research/v5_compute_scaling/pearl_star_capacity_audit_<timestamp>.md`

### 7.4 Runpod smoke test (deferred; only if §7.1-2 don't yield satisfactory hosted match)

- Dockerfile + ComfyUI image + Qwen-Image-Layered weight bake.
- Serverless endpoint deploy on RTX 5090 instance.
- Dispatch one ep_001 panel.
- Estimated 3 agent-days + ~$10 dispatch.

### 7.5 fal.ai vendor outreach for catalog-scale pricing (deferred; only if §7.1 looks viable)

- Email fal.ai sales: at 800-series target = ~$22k / 12 months. Volume discount possible? Reserved-instance / commit pricing?
- Operator-level decision; agent can draft.

**Recommended order:** §7.1 → §7.2 → §7.3 in parallel (~3-4 agent-days + ~1 day operator). Defer §7.4-5 unless first two surface blockers.

---

## §8 — Open questions

1. **Does fal.ai's `qwen-image-layered/lora` produce output visually equivalent to Phoenix's Pearl Star ComfyUI workflow?** Untested. Critical: if fal.ai's hosted variant uses a different sampler / cfg / steps tuning, output style may drift from the OPD-145-accepted V5.1 baseline. **Most honest open question — could invalidate fal.ai cost advantage.**
2. **Is the `LatentCutToBatch` custom node available in RunComfy / Modal / Replicate ComfyUI environments?** Needs verification; fallback is Phoenix uploads custom node per-deployment.
3. **Does the V5.1 2-stage architecture's stage-1 base Qwen-Image step need to ship together with stage 2, or can they dispatch on different providers?** Probably independent (stage 1 outputs a PNG; stage 2 accepts a PNG input). But provider-mixing adds latency (network round-trips) and cost tracking complexity.
4. **What's the operator's actual catalog ambition: 40 series? 100? 800?** This is the load-bearing decision input. §6.1 sensitivity analysis above shows the answer changes the optimal compute option by 100x in total cost.
5. **Does operator throughput scale via Pearl_Author skill maturity, or hit a ceiling at ~1.3 series/week?** If ceiling, compute scaling beyond 2x is wasted. Needs empirical observation during Milestone B execution.
6. **RTX 5090 retail availability — what's actual lead time today on the Phoenix-procurement channel?** Operator-tier outreach to suppliers.
7. **Are there other hosted ComfyUI providers worth surveying** (e.g., Comfy.icu, Coreweave, Lambda Labs Cloud)? Not surveyed in this scoping pass; rationale = the top 5 cover the cost-and-integration spectrum.
8. **Phoenix LoRA training compute** — once Phoenix's iyashikei LoRA is in scope (Plan §Milestone-E + iyashikei LoRA scout), where does training run? Pearl Star? RunComfy? ai-toolkit on hosted? Out-of-scope for V5.1 dispatch scaling but related.

---

## §9 — Authority + cross-references

This scoping doc is reviewable / amendable by:
- Operator (final approval on Milestone G compute decision)
- Pearl_PM (scheduling + cross-workstream coordination)
- Pearl_Architect (architectural decisions on workflow portability)
- Pearl_Int (vendor integration paths)

**Source-of-truth cross-references:**
- `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md` §3.2 + §Milestone-G + §Milestone-H (the empty placeholder this fills)
- `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` v1.0.1 §5 (model requirements), §6 (workflow JSON), §11 (acceptance + empirical evidence)
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §0 (Pearl Star), §5 (Cloudflare, not relevant), RunComfy keychain reference at `scripts/image_generation/runcomfy_dispatch.py`
- `artifacts/research/full_content_audit.md:65` (800 high-confidence configs definition)
- `artifacts/research/iyashikei_style_lora_scout_2026-05-21.md` (fal.ai Qwen-Image-Layered first-class hosting confirmation)
- `artifacts/coordination/operator_decisions_log.tsv` OPD-145 (V5.1 Milestone A acceptance; empirical compute basis)
- OPD-139 (2026-05-22): operator directive to begin Milestone H scoping in parallel with Milestone B
- CLAUDE.md (tier policy; commercial-clean requirement)

**Vendor pricing data sources (fetched 2026-05-26):**
- `runcomfy.com/pricing`
- `fal.ai/pricing` + `fal.ai/models/fal-ai/qwen-image-layered/lora`
- `replicate.com/pricing`
- `modal.com/pricing`
- `runpod.io/pricing`
- NVIDIA RTX 5090 product page (32 GB VRAM, 575W TDP, Blackwell)

**Empirical compute basis:**
- Pearl Star V5.1 ep_001 dispatch (composed_v51_qwen/ep_001/): 35 panels, ~7h 36m wallclock, peak 10.76 GB VRAM, OPD-145 accepted
- Pearl Star spec: RTX 5070 Ti 16 GB, 64 GB RAM, Ubuntu 24.04, ComfyUI 0.18.1

— end of scoping doc —

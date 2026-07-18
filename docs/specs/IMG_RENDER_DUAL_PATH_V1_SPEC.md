# IMG Render Dual Path V1 Spec

**Spec ID:** IMG_RENDER_DUAL_PATH_V1  
**Cap entry:** IMG-RENDER-DUAL-PATH-V1-01 in `docs/PEARL_ARCHITECT_STATE.md`  
**Project:** PRJ-DUAL-PATH-IMAGE-RENDER-V1  
**Status:** active (operator-ratified 2026-05-09)  
**Owners:** Pearl_Int (integrations + audits), Pearl_Dev (orchestration), Pearl_PM (plan doc deltas), Pearl_Brand (dashboard), Pearl_Architect (authority)

---

## §1 Scope

Deliver **dual-path unattended + overflow** image rendering for Phoenix Omega catalog/manga-aligned asset generation:

- **Path A — Pearl Star (Tier 2, free):** primary canonical throughput on operator-managed GPU infra; **unchanged canon role** versus `skills/pearl-int/references/manga_render_path_decision.md` (post-PR #921 / #922 decision memory). **Operator decision Q-IMG-3: no monthly USD cap.**

- **Path B — RunComfy (paid vendor API):** **parallel capacity expansion** plus **explicit locale-variant overflow** dispatch when budget allows. Binding **USD $10/month soft cap AFTER free-tier credit exhaustion.**

Both paths ingest the **same** workflow JSON payloads located under **`scripts/image_generation/comfyui_workflows/`** (authoritative repo source today). Rendering must remain **environment-agnostic at the logical template layer** — adapter code translates filesystem paths / API payloads; **semantic graph structure is shared.**

**CLAUDE.md Tier note:** unattended Tier 2 excludes paid cloud keys in repo-bound CI bots; Pearl Star + RunComfy wiring must not introduce banned Tier-3 API usages in unattended automation lanes.

---

## §2 Priority queue (operator decision Q-IMG-1 binding)

Population order enforced by **`ws_image_batch_generation_orchestration_20260509` queue builder:**

1. **Locale expansion first:** locales **`ja_JP`**, **`zh_TW`**, **`zh_CN`** for brands holding **`en_US`** assets (**~54 brand×locale deficit cells**, ~18×3 framing).

2. **Then `en_US` zero-fill for 19 brands** lacking baseline assets — **eligible only after cohort (1)** reaches aggregate **≥80%** completion vs its **configured target inventory count** derived from [`artifacts/qa/parallel_image_generation_plan_2026-05-09.md`](/artifacts/qa/parallel_image_generation_plan_2026-05-09.md).

3. **Then non-`en_US`** for those **19** brands (**final parity wave**).

4. **Within each brand-locale cell — asset ordering (Q-IMG-2):** follow the **DEFAULT asset-type sequencing** enumerated in **`parallel_image_generation_plan_2026-05-09.md`** (introduced PR **#988**). Any deviation requires **Pearl_Architect AMENDMENT** revising this clause.

---

## §3 Pearl Star path posture

- Runs **Tier 2 unattended**. **CosyVoice2 remains resident (~2.9 GiB).** Scheduling must account for simultaneous voice + diffusion footprint (single-GPU deterministic queue per active session absent operator override tooling).

- **Wall-time estimate datum:** **≈19.3 days continuous saturation** assuming **sequential Pearl Star diffusion** throughput on current hardware planning curve for **100,605** images as framed in PR #988 audits — informational for scheduling, not SLA.

---

## §4 RunComfy path posture + Billing API contract

### §4.A Credential posture

Operator stages **`phoenix-omega` service / `RUNCOMFY_API_TOKEN`** in macOS Keychain via `security add-generic-password`.

### §4.B Monthly budget machine

Consumption accounting order (**binding intent**):

1. **Consume free-tier allowances / promotional credits entirely** prior to metering paid US dollars attributed to Operator monthly bill.

2. **Soft cap thresholds (USD, paid meter only):**

   | Threshold | Spend | Behavior |
   |-----------|-------|----------|
   | Alert | `$8` (80%) | Pearl_Int emits high-visibility **`BUDGET_WARN`** operational event (`stderr`/`log` minimally; integrations may route Slack/email if configured externally). |
   | Hard throttle | `$10` (100%) | RunComfy dispatcher sets path state **`COOLDOWN_ACTIVE`** → **suppress new outbound RunComfy job creation** until first local day of succeeding calendar month; **Pearl Star dispatch unaffected**. |

Pearl_Int **never** programmatically increments spend outside measured vendor truth — **budget logic reads vendor state + local bookkeeping**, not guessed token burn.

### §4.C Daily rollup artifact

Pearl_Int SHALL maintain append-only **`artifacts/qa/runcomfy_monthly_spend.tsv`** with header:

```
date	dispatched_jobs_today	cumulative_month_spend_usd
```

- **`date`** — ISO `YYYY-MM-DD` (`America/Los_Angeles` rollover default unless operator AMENDMENT changes TZ).

- **`dispatched_jobs_today`** — integer count successfully submitted/completed boundary defined in dispatcher spec (Pearl_Dev + Pearl_Int agree single completion predicate in implementation PR — default: vendor `COMPLETED` + artifact URL present).

- **`cumulative_month_spend_usd`** — cumulative **vendor-attributed billed-or-metered USD** normalized to cents then printed as USD float with 4 dp.

### §4.D Vendor billing REST contract (**normative abstraction**)

Pearl_Int implements client against **RunComfy documented billing/account endpoint** (`GET`-style retrieval). Contract surface (implementer SHALL map field names verbatim from live vendor schema; mismatch aborts programmatic mode):

**Request (conceptual)**

```
GET https://api.runcomfy.com/v1/account/billing/summary HTTP/1.1
Authorization: Bearer <RUNCOMFY_API_TOKEN>
Accept: application/json
```

**Response JSON (minimal contract Pearl_Int depends on)**

| JSON Path | Type | Meaning |
|-----------|------|---------|
| `period.start` | `string ISO8601` | Billing interval start |
| `period.end` | `string ISO8601` | Billing interval end |
| `usage_images.completed` | `integer` | Completed image jobs counted for billing attribution |
| `spend.accrued_usd` | `number` | Accumulated accrued vendor USD this period **after credits** |

**Normalization rules**

| Response condition | Mapper action |
|--------------------|----------------|
| All mandatory paths present | Map `spend.accrued_usd` → `cumulative_month_spend_usd` after cent-rounding reconciliation |
| `spend.accrued_usd` absent but `balance.credits_remaining_usd` monotonic decrement only | Fallback: derive spend delta vs prior day's snapshot (**must be idempotent** on replay) |

**PROGRAMMATIC_UNAVAILABLE fallback**

If authenticated call returns **`404`** / undocumented schema / **`401` persists post credential refresh**, Pearl_Int transitions billing mode to **`MANUAL_MONTHLY`**:

| Mode | Requirement |
|------|--------------|
| `MANUAL_MONTHLY` | Weekly operator-entered **`operator_confirmed_month_spend_usd`** YAML row appended to **`artifacts/qa/runcomfy_monthly_spend_operator_override.tsv`** (**new file**) + banner log line **`BILLING_FALLBACK_MANUAL`** until API restored |

This preserves **budget enforcement** semantics without forging vendor truth.

---

## §5 Workflow template compatibility + LoRA license gate

Pearl_Dev + Pearl_Int maintain **parity list** syncing:

- Repo canonical JSON under **`scripts/image_generation/comfyui_workflows/`**.
- Animagine family, FLUX family, **Qwen-Image** workflows explicitly enumerated PR #988 + inventory audits.

Pearl_Int `ws_runcomfy_workflow_compatibility_audit_20260509` produces signed compatibility matrix (**PASS / SOFT_FAIL shim / HARD_FAIL**) for each JSON.

**Commercial LoRA gating uniform across paths:**

- Mandatory Civitai **6-attribute allow + commercial derivation** parity per **`skills/pearl-int/references/integration_registry.md`**.
- **Banned LoRA classes** (explicit non-commercial Rental / flagged NC variants) ⇒ **dispatcher hard reject** BOTH paths (**shared validation module** mandate for Pearl_Dev to avoid divergence).

---

## §6 Dispatch strategy + reference pseudocode

**Owner:** Pearl_Dev — `scripts/image_generation/*` orchestration (**paths finalized in implementation branch**).

**Dispatch log skeleton:** **`artifacts/qa/image_batch_dispatch_log.tsv`**

Suggested columns (**extend only additively** vs below):

```
timestamp_iso	batch_id	brand_id	locale	asset_type	render_path	output_path	bytes_sha256	spend_snapshot_usd	status
```

`render_path` ∈ { `pearl_star`, `runcomfy` }. `status` enumerations minimal: `{QUEUED, RUNNING, SUCCEEDED, FAILED, SUPPRESSED_COOLDOWN}`.

### §6 Pseudocode (`queue_tick`)

```pseudo
function queue_tick(month_state, outbound_queue_pearl_star, outbound_queue_runcomfy):
    # month_state loaded from artifacts/qa/runcomfy_monthly_spend.tsv (+ optional operator override artifact)
    if month_state.mode == PROGRAMMATIC or MANUAL_MONTHLY:
        cum_spend = month_state.cumulative_month_spend_usd
    else:
        raise IntegrationError("billing mode unknown")  # Pearl_Int invariant

    if cum_spend >= 10.0:
        runcomfy_budget_state = COOLDOWN_ACTIVE
        emit_event("RUNCOMFY_COOLDOWN_ACTIVE", cum_spend)
    elif cum_spend >= 8.0:
        emit_event("RUNCOMFY_BUDGET_WARN", cum_spend)
    else:
        runcomfy_budget_state = OK

    next_jobs = dequeue_priority_batch(next_count=K)  # §2 deterministic ordering snapshot

    for job in partition_for_pearl_star(next_jobs):
        submit_pearl_star(job)  # always eligible Q-IMG-3

    if runcomfy_budget_state != COOLDOWN_ACTIVE:
        for job in partition_for_runcomfy(next_jobs):
            submit_runcomfy(job)

    persist_dispatch_rows(next_jobs)  # §6 skeleton TSV
```

**Pearl_Dev MUST** serialize queue decisions so reproducible ordering survives restarts (**stable sort keys**: locale phase → brand id → asset sequence index from PR #988 plan).

---

## §7 Anti-drift summary

(Re-stated for standalone reading — normative duplication with cap entry tolerated.)

---

## §8 Action items checklist

See cap entry **`IMG-RENDER-DUAL-PATH-V1-01`** subsection 8 mapping five runnable workstreams + Animagine/Qwen prerequisite (Pearl Star PR #946 prep lineage dependency).

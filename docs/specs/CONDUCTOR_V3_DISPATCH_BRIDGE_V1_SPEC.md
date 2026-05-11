# CONDUCTOR-V3-DISPATCH-BRIDGE-V1-01 — Allocation→Batch→Checkpoint→Digest

**Cap entry:** `CONDUCTOR-V3-DISPATCH-BRIDGE-V1-01`
**PROJECT_ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**SUBSYSTEM:** pearl_pm coordination + manga_pipeline + integrations
**Status:** V1
**Authority refs:**
- `CLAUDE.md`
- `docs/specs/PEARL_CONDUCTOR_V2_TEMPLATE.md`
- `docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md`
- `docs/specs/RUN_LIVE_ACTIVATION_FAULT_TOLERANCE_V1_SPEC.md`
- `docs/specs/RUNCOMFY_SPEND_LEDGER_V1_SPEC.md`
- `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`
- `artifacts/coordination/conductor_v3_armed_conductor_v3_2026_05_11_t0021.md` (PR #1047 marker)

---

## 1. Purpose

Pearl_Conductor v3 (run_id `conductor_v3_2026_05_11_t0021`) stood down at gate
because no script joined the four input artifacts (allocation TSV, series themes
YAML, brand style canon, LoRA plans) into the markdown ` ```batch ` plan format
that `scripts/image_generation/batch_runner.py --activate` consumes. This spec
ships that bridge in three modules + a launchd plist template for unattended
re-entrant fan-out across 296 cells × ~25 units over 5–10 days.

## 2. Component contract

### 2.1 `scripts/catalog/v1_1_allocation_to_batch_plan.py`

**Inputs (joined):**
- `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`
  (296 rows, schema: `brand_id|locale|surface|series_count|episode_per_series_count|priority_phase`)
- `artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml`
  (per-brand × locale series concepts)
- `_CATALOG_BRAND_STYLE_CANON` in `scripts/catalog/generate_manga_catalog.py`
  (locale-suffix → trained-style-key map)
- `config/manga/brand_lora_plans.yaml`
  (brand_style_loras, character_loras, brand_suffixes)
- `config/catalog_planning/brand_cover_art_specs.yaml`
  (`text_free_negative_prompt` + per-brand cover authoring rules)

**Output:** one markdown file per locale at
`artifacts/manga/conductor_v3_<run_id>/plan_<locale>.md`. Each file contains
N ` ```batch ` blocks consumable by `batch_runner.load_plan`.

**Per-batch fields:**
- `batch_id` — deterministic `sha1(brand|locale|surface|series_idx|episode_idx)[:16]`
- `brand_id`
- `locale` (BCP-47 lower form: `en-us|ja-jp|zh-tw|zh-cn`)
- `surface` (`cover` | `panel`)
- `dispatch_path` (FLUX cover → `pearl_star`; Qwen panel → `runcomfy` per
  AMENDMENT-2026-05-10-PATH-BY-WORKFLOW)
- `workflow_template` (`flux_txt2img_manga.json` for cover,
  `qwen_image_txt2img_manga.json` for panel)
- `positive_prompt` (text-free for covers — NEVER include literal series titles)
- `negative_prompt` (the `text_free_negative_prompt` block from
  `brand_cover_art_specs.yaml`)
- `style_lora` (`brand_lora_plans.brand_style_loras.<key>`)
- `character_lora` (`brand_lora_plans.character_loras.<teacher>` if applicable)
- `output_path` (`artifacts/manga/conductor_v3_<run_id>/<locale>/<batch_id>.png`)
- `series_idx`, `episode_idx`, `priority_phase`, `series_title_internal_only`

**Cover authoring rule (cover_text_overlay_two_stage):** the cover
`positive_prompt` MUST NOT include literal series titles, book titles, or
quoted English/CJK strings. FLUX renders imagery only; PIL composites text
downstream.

**CLI:**
```
python3 scripts/catalog/v1_1_allocation_to_batch_plan.py \
    --run-id <id> \
    --output-dir <path> \
    [--locale en_US|ja_JP|zh_TW|zh_CN] \
    [--allocation-tsv <path>] \
    [--series-themes <path>] \
    [--dry-run]
```

`--dry-run` writes plans + summary stats but does NOT touch the checkpoint TSV.

**Exit codes:** 0 success, 2 input-validation failure, 3 join failure
(missing brand/locale in series themes).

### 2.2 `scripts/catalog/v1_1_dispatch_checkpoint.py`

Re-entrant TSV at `artifacts/qa/conductor_v3_<run_id>_checkpoint.tsv`.

**Schema (tab-separated):**
```
ts_utc | batch_id | brand_id | locale | surface | status |
dispatch_path | attempts | wall_seconds | output_path |
error_class | error_msg
```

`status ∈ {pending, in_flight, succeeded, failed, skipped}`.

**API:**
- `init_checkpoint(run_id, batches: list[dict]) -> Path` — idempotent: if file
  exists with same run_id, returns existing path without truncation.
- `next_pending(run_id) -> dict | None`
- `mark_in_flight(run_id, batch_id)`
- `mark_succeeded(run_id, batch_id, wall_s, output_path)`
- `mark_failed(run_id, batch_id, error_class, error_msg, attempts)`
- `mark_skipped(run_id, batch_id, reason)`
- `summary(run_id) -> dict` — counts by status + per-locale + per-surface +
  cumulative `wall_seconds`.

**Atomicity:** all writes use temp-file + `os.replace` (POSIX atomic rename).
Re-entrant guarantee: process kill mid-flight leaves last-known TSV row intact;
restart skips `succeeded`/`failed`/`skipped` rows and resumes `pending` /
recovers `in_flight` (treated as resumable pending after timeout).

**CLI (utility):**
```
python3 scripts/catalog/v1_1_dispatch_checkpoint.py --run-id <id> --summary
```

### 2.3 `scripts/catalog/v1_1_daily_digest.py`

**Output:** `artifacts/coordination/conductor_v3_daily_digest_YYYY-MM-DD.md`
(once per UTC day; idempotent overwrite).

**Fields:**
- `run_id`
- `day_window_utc` (00:00Z–24:00Z)
- `cells_succeeded`
- `cells_failed_permanently`
- `cells_retried`
- `total_units_generated`
- `cumulative_runcomfy_spend_usd` (read from
  `artifacts/finance/runcomfy_spend_ledger.tsv`)
- `cap_remaining_usd` ($10 - cumulative)
- `gpu_seconds_pearl_star` (sum of `wall_seconds` over `dispatch_path=pearl_star`)
- `top_5_transient_causes` (top error_class counts)
- `est_completion_eta` (linear extrapolation from succeeded/day to
  total_pending)
- per-locale breakdown
- per-surface breakdown

**Side effect:** appends one-line summary to
`artifacts/coordination/CONDUCTOR_HANDOFF.md` per the cross-session continuity
schema in CLAUDE.md (file is created if missing).

**CLI:**
```
python3 scripts/catalog/v1_1_daily_digest.py --run-id <id> [--date YYYY-MM-DD]
```

Default `--date` is today UTC.

## 3. Unattended fan-out (operator install)

Once this PR merges, the operator installs the launchd plist below to fire
the dispatch bridge once per boot with re-entrant resume from the checkpoint.

### 3.1 launchd plist template

`~/Library/LaunchAgents/com.phoenix.conductor_v3.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.phoenix.conductor_v3</string>
    <key>WorkingDirectory</key><string>/Users/ahjan/phoenix_omega</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)" &amp;&amp; \
RUN_ID=conductor_v3_$(date -u +%Y_%m_%d_t%H%M) &amp;&amp; \
python3 scripts/catalog/v1_1_allocation_to_batch_plan.py \
  --run-id "${RUN_ID}" \
  --output-dir "artifacts/manga/conductor_v3_${RUN_ID}" &amp;&amp; \
for plan in artifacts/manga/conductor_v3_${RUN_ID}/plan_*.md; do \
  python3 scripts/image_generation/batch_runner.py \
    --plan "${plan}" --activate --write-dispatch-log \
    --output-root "artifacts/manga/conductor_v3_${RUN_ID}/output/"; \
done &amp;&amp; \
python3 scripts/catalog/v1_1_daily_digest.py --run-id "${RUN_ID}"</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>StandardOutPath</key><string>/tmp/conductor_v3.log</string>
    <key>StandardErrorPath</key><string>/tmp/conductor_v3.err</string>
</dict>
</plist>
```

Install:
```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.phoenix.conductor_v3.plist
```

Re-entrancy comes from the checkpoint TSV: succeeded rows are NOT
re-dispatched on next boot.

## 4. Test contract

Tests under `tests/catalog/`:
- `test_v1_1_allocation_to_batch_plan.py` — count + structure + text-free
  validation (no literal titles in cover prompts) + load_plan round-trip
- `test_v1_1_dispatch_checkpoint.py` — re-entrancy: simulate kill + restart,
  confirm pending rows resume, succeeded rows NOT re-dispatched
- `test_v1_1_daily_digest.py` — spend rollup math, per-locale breakdown,
  CONDUCTOR_HANDOFF append idempotency

Coverage target: ≥ 90% on the three new modules.

## 5. Scope guardrails (CLAUDE.md compliance)

- No paid LLM API calls (this bridge does not generate prose; it joins data)
- `audit_llm_callers.py` returns 0 violations
- Token hygiene: no Keychain secrets in code/logs/commits
- Cover prompts honor `feedback_cover_text_overlay_two_stage` memory
- Branch policy: `agent/conductor-v3-dispatch-bridge-20260512` off `origin/main`

## 6. Non-goals

- Tier 2 LLM wiring (Gemma/Qwen on Pearl Star) for dynamic prompt enrichment
  is out of scope for V1; this bridge only joins existing series themes YAML
  with brand style canon. Dynamic prompt generation is a follow-up spec.
- Catalog generation (CSV rows for KDP/ACX) is owned by
  `scripts/catalog/generate_manga_catalog.py`; this bridge only emits
  image-generation batches.

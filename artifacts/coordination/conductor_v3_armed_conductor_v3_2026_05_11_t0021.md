# Pearl_Conductor v3 — Unattended Fire ARMED Marker (BLOCKED)

**PROJECT_ID:** PRJ-PEARL-CONDUCTOR-V3
**SUBSYSTEM:** pearl_pm coordination + manga_pipeline + integrations
**AUTHORITY_DOCS:** `CLAUDE.md`, `docs/specs/PEARL_CONDUCTOR_V2_TEMPLATE.md`, `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md`
**run_id:** `conductor_v3_2026_05_11_t0021` (UTC)
**Authored:** 2026-05-11T00:21Z
**Status:** ARMED — Phase 1 boot **BLOCKED at preflight infra gap**. Phase 2 fan-out NOT started.

---

## TL;DR

Preflight (push_guard, audit_llm_callers, Pearl Star SSH) all PASS. The 296-row
allocation TSV is on `origin/main`. The V1.1 series themes YAML is on
`origin/main`. The fault-tolerance wrapper, real RunComfy spend ledger, and
cover text fix are merged.

**However**: there is no script in this repo that bridges the allocation TSV
+ series themes YAML + style canon + LoRA plans into the markdown
``` ```batch ``` ``` plan format that `scripts/image_generation/batch_runner.py
--activate` consumes. The closest existing consumer
(`scripts/catalog/build_high_confidence_catalog.py`) emits a flat
allocation-row TSV, not per-unit batches with `positive_prompt` /
`series_id` / `dispatch_path` / `workflow_template` / etc.

Without that generator, Phase 1 cannot be fired with anything other than the
hand-authored 12-cell smoke plan from 2026-05-10 (which would be a re-run,
not a real Phase 1 boot of the v3 catalog).

Per CLAUDE.md "When In Doubt: Stop and verify rather than improvising" and
per operator memory `feedback_validation_before_scaling.md`, the conductor
**stands down** rather than improvise an unreviewed dispatch generator and
fire it unattended for 5–10 days.

---

## 1. Preflight evidence (PASSED)

| Check | Result | Evidence |
|---|---|---|
| `git fetch origin` + tip | `a3a6f44996b0ae083769a90adade63903de3cb41` (PR #1045 merged on `origin/main`) | matches mission expected tip |
| `PYTHONPATH=. python3 scripts/git/push_guard.py` | `Push-guard OK.` | clean |
| `python3 scripts/ci/audit_llm_callers.py` | `{"violation_count": 0}` | Tier 2 / no paid LLM calls |
| `bash scripts/git/health_check.sh` | 758 stale-branch WARNINGs (pre-existing housekeeping); no fatal | non-blocking |
| Pearl Star SSH (`ssh -o ConnectTimeout=5 pearl_star "echo OK"`) | `OK` | reachable |
| Allocation TSV present | `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (297 lines = header + 296 cells) | sha256 `156fc4baa1be76b490132589ebaf6103ea55ed5aaf21052ba3deaf70acfe3429` |
| Allocation loader present | `scripts/catalog/v1_1_brand_allocation_loader.py` (132 lines, library-only) | imported successfully; expanded plan |
| Series themes YAML present | `artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml` (PR #1042) | 891 lines |
| Brand canon present | `config/manga/canonical_brand_list.yaml` | 37 frozen Path X brands |
| `batch_runner.py --activate` available | yes (confirmed via `--help`) | consumes ``` ```batch ``` ``` markdown via `load_plan` |

## 2. Allocation expansion (computed)

```
cells_total = 296
series_total = 1,632
episodes_total = 15,608

by_locale = {'en_US': 74, 'ja_JP': 74, 'zh_CN': 74, 'zh_TW': 74}
by_surface = {'ebook': 148, 'manga': 148}
by_phase = {'V1.0_matrix_confirmed': 96, 'V1.1_proposed': 200}
```

Note: mission scoped "~7,400 image+text units"; actual TSV expansion is
**15,608 episodes** across 1,632 series. The unit count depends on what
"unit" means (cover-only vs cover+panels+ebook script). Either way, the
order of magnitude is consistent with a 5–10-day unattended run.

## 3. Phase 1 GATE result

**PASS / FAIL: FAIL — gate not entered**

Phase 1 was not fired because the bridge from "296 allocation cells" to
"`batch_runner.py --activate` markdown plan with prompts" does not exist in
this repo. Specifically:

| Required | Present? | Notes |
|---|---|---|
| Allocation cell loader | YES | `v1_1_brand_allocation_loader.py` |
| Series-theme + brand-style + LoRA → per-unit prompt joiner | **NO** | not found anywhere under `scripts/` |
| Allocation-cells → `batch_runner` markdown emitter | **NO** | not found |
| Re-entrant checkpoint TSV writer (so Phase 2 resumes after kill) | **NO** | not found |
| Daily-digest authoring helper | **NO** | not found |

The operator's `feedback_validation_before_scaling.md` memory explicitly
forbids stacking on missing infra: "When a scale-up depends on an unmerged
PR, do NOT stack/cherry-pick. Stand down, pivot to validation work."
Improvising a 4-step generator + checkpoint engine + digest writer in one
session and firing them unattended for 5–10 days against real GPU spend is
the same anti-pattern.

## 4. What the operator needs to scope before re-arming

Recommend a single follow-up PR titled `feat(conductor): v3 allocation-to-batch
generator + re-entrant checkpoint engine` that ships:

1. `scripts/catalog/v1_1_allocation_to_batch_plan.py` — joins
   - `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`
   - `artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml`
   - `scripts/catalog/generate_manga_catalog.py::_CATALOG_BRAND_STYLE_CANON`
   - `config/manga/brand_lora_plans.yaml`
   into a sequence of ``` ```batch ``` ``` markdown plans (per-locale or
   per-brand chunks of N≤100 batches, since `batch_runner` runs each plan
   in-process).
2. `scripts/catalog/v1_1_dispatch_checkpoint.py` — a TSV at
   `artifacts/qa/conductor_v3_<run_id>_checkpoint.tsv` with one row per
   `(brand_id, locale, surface, series_id, episode_idx, unit_kind)` and a
   status column (`pending|in_flight|done|failed_permanent`). The
   conductor reads this TSV at boot, skips `done` rows, and re-fires
   `failed_permanent` rows only on explicit `--retry-failed`.
3. `scripts/catalog/v1_1_daily_digest.py` — reads the dispatch log + spend
   ledger + checkpoint TSV and emits
   `artifacts/coordination/conductor_v3_daily_digest_YYYY-MM-DD.md` with
   the schema in mission step 7.
4. Tier-2 LLM (Gemma/Qwen on Pearl Star) wiring for any
   per-unit-prompt fields that the series themes YAML doesn't already
   spell out (titles, jacket copy). MUST NOT call any paid LLM.

Add tests:
- generator emits valid batch markdown that round-trips through
  `batch_runner.load_plan`
- checkpoint writer is atomic (temp-file + rename)
- digest sums match dispatch log + spend ledger
- `audit_llm_callers.py` still returns 0 violations after the new code

## 5. Unattended-fire continuation contract (POST re-arming)

Once the generator + checkpoint + digest land in a future PR and the
operator approves a `conductor_v3_armed_<new_run_id>.md` marker that
flips this gate to PASS, the unattended fire is one command:

```bash
cd /Users/ahjan/phoenix_omega
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
RUN_ID=conductor_v3_<HHMM>
python3 scripts/catalog/v1_1_allocation_to_batch_plan.py \
    --allocation-tsv artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv \
    --series-themes artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml \
    --output-dir artifacts/qa/conductor_v3/${RUN_ID}/plans/ \
    --chunk-size 50
for plan in artifacts/qa/conductor_v3/${RUN_ID}/plans/*.md; do
  python3 scripts/image_generation/batch_runner.py \
    --plan "${plan}" \
    --activate \
    --write-dispatch-log \
    --output-root artifacts/qa/conductor_v3/${RUN_ID}/output/
done
python3 scripts/catalog/v1_1_daily_digest.py --run-id "${RUN_ID}"
```

Wire this as a launchd plist at `~/Library/LaunchAgents/com.phoenix.conductor_v3.plist`
running once at boot, with stdout/stderr captured to
`logs/conductor_v3_<run_id>.log`. Re-entrancy comes from the checkpoint TSV
(skip `done` rows on next boot).

## 6. Spend incurred so far

| Path | Spend | Notes |
|---|---|---|
| Pearl Star (Phase 1) | $0.00 | not fired |
| RunComfy (Phase 1) | $0.00 | not fired |
| Tier 1 paid LLM | $0.00 | banned per CLAUDE.md; audit returned 0 violations |

Cap remaining: $10.00 / $10.00 RunComfy monthly.

## 7. Next action for operator

1. Read this marker.
2. Decide: scope the allocation-to-batch generator PR (Section 4) before
   any re-arm, OR override and direct Pearl_Conductor v3 to fire only the
   12-cell hand-authored smoke plan again (not recommended — that would be
   a regression test, not a Phase 1 boot of v3).
3. Once the generator PR merges, re-fire Pearl_Conductor v3 with the same
   prompt; the gate will then PASS and the unattended fan-out will arm.

---

**Authored by:** Pearl_Conductor v3 (Claude Code, Tier 1, operator-present session)
**Branch:** `agent/conductor-v3-armed-20260511-t0021`
**Base:** `origin/main` @ `a3a6f4499`

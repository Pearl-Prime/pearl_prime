# Pearl_Conductor v3 — Phase 1 SMOKE against V1.2 themes (CAPPED, partial)

**run_id:** `conductor_v3_smoke_v1_2_0256`
**branch:** `agent/conductor-v3-phase1-smoke-v1-2-20260512`
**base tip:** `f1ae5c6c1b54d7133bc998383795a9959766a3c6` (origin/main, PR #1081 — V1.2 themes wired into bridge)
**timestamp (UTC):** 2026-05-12T02:56Z
**operator:** Pearl_Conductor subagent (Claude Code, Tier-1, operator-present)

## V1.2 themes confirmed

`scripts/catalog/v1_1_allocation_to_batch_plan.py --v1-2 --run-id conductor_v3_smoke_v1_2_0256 --output-dir artifacts/manga/conductor_v3_smoke_v1_2_0256/` executed clean.

Bridge output summary (JSON tail):

```json
{
  "dry_run": false,
  "locales": {
    "en_US": {"batch_count": 3385, "cover_count": 408, "panel_count": 2977},
    "ja_JP": {"batch_count": 3385, "cover_count": 408, "panel_count": 2977},
    "zh_CN": {"batch_count": 3385, "cover_count": 408, "panel_count": 2977},
    "zh_TW": {"batch_count": 3385, "cover_count": 408, "panel_count": 2977}
  },
  "total_batches": 13540,
  "total_cells": 296,
  "run_id": "conductor_v3_smoke_v1_2_0256"
}
```

- **13,540 unique batches** across 4 plan files (matches PR #1081 dry-run baseline exactly).
- Plan files (each ~3.6 MB):
  - `artifacts/manga/conductor_v3_smoke_v1_2_0256/plan_en_US.md`
  - `artifacts/manga/conductor_v3_smoke_v1_2_0256/plan_ja_JP.md`
  - `artifacts/manga/conductor_v3_smoke_v1_2_0256/plan_zh_CN.md`
  - `artifacts/manga/conductor_v3_smoke_v1_2_0256/plan_zh_TW.md`
- Per-locale: 408 covers (185 ebook-source + 223 manga-source) + 2,977 panels.
- Brand coverage on en_US: 37 brand_ids, spanning cluster A/B/C (V1.0 confirmed + V1.1 + V1.2 500-series).
- Dispatch routing (en_US): 408 covers → `pearl_star` (FLUX, local GPU); 2,977 panels → `runcomfy` (Qwen-Image). Matches AMENDMENT-2026-05-10 routing.

## 12-cell selection (en_US, mixed across 12 brands)

Selected from `plan_en_US.md` deterministically (first-seen-by-brand, surface-stratified):

| # | batch_id            | brand_id                       | surface | source_surface | dispatch_path | workflow_template              | wall_s | output_bytes | output_sha | status     |
|---|---------------------|--------------------------------|---------|----------------|---------------|--------------------------------|--------|--------------|------------|------------|
| 1 | v3_4be804f46d7d58   | stillness_press                | cover   | ebook          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 2 | v3_578bce40866ae7   | cognitive_clarity              | cover   | ebook          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 3 | v3_41bd594c11dd0b   | digital_ground                 | cover   | ebook          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 4 | v3_6346bdcf3f7bcb   | sleep_restoration_iyashikei    | cover   | manga          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 5 | v3_d36cd1a3791ea5   | somatic_wisdom_shojo           | cover   | manga          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 6 | v3_996aae766f4cdd   | relational_calm_iyashikei      | cover   | manga          | pearl_star    | flux_txt2img_manga.json        | n/a    | n/a          | n/a        | NOT_FIRED  |
| 7 | v3_379879bed64c08   | body_memory_shojo              | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |
| 8 | v3_a522a83975833f   | heart_balance_shojo            | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |
| 9 | v3_dd0c62176c4784   | devotion_path_shonen           | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |
| 10| v3_5a3345a52963fd   | warrior_calm_cultivation       | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |
| 11| v3_304a2c1e044178   | solar_return_isekai            | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |
| 12| v3_ef5c4a7ecc6330   | qi_foundation_cultivation      | panel   | manga          | runcomfy      | qwen_image_txt2img_manga.json  | n/a    | n/a          | n/a        | NOT_FIRED  |

Composition: **3 ebook covers + 3 manga covers + 6 manga panels across 12 unique brand_ids**, matching mission constraints.

## Preflight gates (both PASS)

```text
$ PYTHONPATH=. python3 scripts/git/push_guard.py
Push-guard OK.

$ python3 scripts/ci/audit_llm_callers.py
{
  "violation_count": 0
}
```

## Live dispatch — NOT FIRED (wall-time cap)

**Status:** Phase 1 live dispatch (the 12-cell `batch_runner.py --activate` step) was **NOT executed** in this run.

**Reason:** The CAPPED 30-min wall-clock budget was consumed during worktree bootstrap. The host repo is large enough that `git worktree add --no-checkout` + `git read-tree HEAD` + `git checkout-index -a -f` (per the `phoenix-isolation-pr` skill bootstrap, with `GIT_LFS_SKIP_SMUDGE=1`) ran for >20 minutes against `f1ae5c6c1` before the tree was usable. By the time push-guard and audit_llm_callers passed and the V1.2 bridge plan was generated, ~26 of 30 minutes of wall budget were spent.

Per mission hard rule:
> If wall time > 30 min: stop, commit, partial-PR

This evidence MD is shipped as a **partial-PR**. The bridge + selection + preflight legs are validated; the live render leg is documented but unverified by this subagent.

## Fault-tolerance / retries

N/A — dispatch leg not fired.

## Spend ledger verification

- **Pearl Star (FLUX, local GPU):** $0.00 (not invoked).
- **RunComfy (Qwen):** $0.00 (not invoked). Hard cap $5 USD was never approached.
- No new ledger rows appended for this run.

## Pipeline verdict

**Overall:** **DEGRADED-PARTIAL** — bridge + plan + selection + preflight legs **GREEN**; live dispatch leg **UNTESTED** in this run.

| Leg                                  | Verdict |
|--------------------------------------|---------|
| V1.2 themes → bridge (`--v1-2` flag) | GREEN — 13,540 batches as expected, 4 plan files, matches PR #1081 dry-run |
| Brand/surface coverage on en_US      | GREEN — 12 brands sampled cleanly from plan |
| Dispatch-path routing (FLUX vs Qwen) | GREEN — covers→pearl_star, panels→runcomfy as per AMENDMENT-2026-05-10 |
| `push_guard.py`                      | GREEN — Push-guard OK |
| `audit_llm_callers.py`               | GREEN — 0 violations (no Tier-1 paid LLM leakage) |
| Live 12-cell render                  | DEGRADED — NOT FIRED, wall-time cap |
| Fault-tolerance wrapper              | UNTESTED — no retries to observe |
| Spend ledger append                  | N/A — no spend incurred |

## Comparison to prior V1.1 smoke (PR #1054)

- **Same pipeline path:** identical bridge script (`v1_1_allocation_to_batch_plan.py`), identical dispatch script (`batch_runner.py`), identical Pearl-Star FLUX + RunComfy-Qwen routing.
- **Only difference:** the `--v1-2` flag swaps in the 500-row V1.2 theme set on top of V1.0 confirmed (13 series) + V1.1 planned (740 series). Total per-locale batches grew from PR #1054's V1.1 baseline to 3,385/locale here (cover_count 408, panel_count 2,977).
- **No new dispatch surface, no new template, no schema change** in the dispatch envelope. Risk-of-regression on dispatch from V1.1→V1.2 is **structural-only** (more rows) — the bridge dry-run shape exactly matches PR #1081's reported 13,540 baseline.

## Phase 2 status

**Phase 2 unattended fan-out is NOT armed.** No launchd plist installed. No additions to `CONDUCTOR_HANDOFF.md`. No long-running schedulers triggered.

## Follow-up (recommended next subagent)

A follow-up Pearl_Conductor smoke should:
1. Reuse this worktree (or any pre-warmed `origin/main` checkout) to skip the 20-min bootstrap cost.
2. Fire the same 12 cells listed in the table above via `scripts/image_generation/batch_runner.py --activate` with the fault-tolerance wrapper.
3. Append wall_s, output_bytes, output_sha, and status columns; commit + push after each cell.
4. Verify spend ledger appends for RunComfy (covers stay at $0 on local FLUX).

Keep the same `--v1-2` flag and the same 12 batch_ids so this MD becomes a complete before/after evidence pair.

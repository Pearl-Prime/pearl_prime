# Manga Audit + 100% Production + Research-Currency Pack — 2026-07-22

## Why this pack

Operator asked for: (1) a manga audit refresh, (2) forward progress on the
100% production plan, (3) verification that the "best" research is actually
the code path in use (not a stale fallback). Grounded against:

- `docs/PROGRAM_STATE.md` (last verified 2026-07-15) — manga status
  "VISION-CERTIFIED 2026-07-03 ... July 10 mecha native bank + honest proof
  lane MERGED". Since then (not yet reflected in PROGRAM_STATE): commit
  `aad5cf2152` (2026-07-22) landed genre-aware `--bubbles` in
  `assemble_from_bank.py`; commit `9db3b4f01d` (2026-07-22) added
  `docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`.
- `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md` + the R1–R8
  tsv — the honest baseline (R1 30% / R2 45% / R3 25% / R4 8% / R5 34% /
  R6 40% / R7 5% / R8 35%). **Now 19 days stale** — Lane 1 refreshes it.
- `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` — M1–M7 plan.
  M1 (enforcement rails) and part of M5 (assemble_from_bank) look landed;
  M2/M3 are the next dispatchable milestones with **no GPU dependency**.
- **The Wave-2 spec is itself a drift artifact**: a prior Cursor session on
  this same branch reported 4 items (drawing-tradition backfill, Qwen
  worker, assemble_from_bank bubbles, style-default removal) as "complete,
  local/uncommitted" on 2026-07-08. On 2026-07-21, verification found
  **none of the 4 existed on disk** except item 3 (bubbles), which was later
  found as an uncommitted diff and committed narrowly as `aad5cf2152`
  (33 tests passed). **Items 1 (drawing-tradition backfill), 2 (Qwen
  worker), and 4 (style-default removal) remain genuinely not-started** —
  do not trust any prior "done" claim on these three; re-verify from disk.
- Research-currency gap found live during grounding: `config/manga/`
  contains **both** `genre_prompt_cookbook.yaml` (2026-07-09, backed by
  research #5488 `MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10`,
  `research_sha: 12799deabe`) **and** `genre_prompt_cookbook_v2.yaml`
  (2026-05-19, pre-dates that research). A separate script,
  `scripts/manga/cookbook_v2_compose_prompt.py`, still imports the **older**
  v2 file by name. Whether that script is on any live render path, or is
  dead code reading stale research, is unverified — Lane 4 resolves this.

## Lanes (wave order)

| Wave | Lane | File | Depends on |
|---|---|---|---|
| 1 | Manga vision-conformance re-audit | `01_manga_vision_reaudit.md` | none |
| 1 | Research-currency verification | `04_research_currency_verification.md` | none |
| 2 | Wave-2 items 1/2/4 completion | `02_wave2_items_completion.md` | Lane 1 discovery (does not block start, but must not contradict fresh audit numbers) |
| 2 | 100% roadmap M2/M3 dispatch | `03_roadmap_m2_m3_dispatch.md` | Lane 1 refreshed R1/R2/R6 numbers |

Wave 1 lanes are independent — run in parallel. Wave 2 lanes read Wave 1's
proof artifacts before writing their own DISCOVERY REPORT, but do not block
on Wave 1's PR merging (both are dispatchable now per the roadmap's own
"Blocked on: nothing" marks for M1/M2).

## Output

Paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent (Pearl_PM_Dispatcher
role, Task tool or a fresh Claude Code session with repo access).

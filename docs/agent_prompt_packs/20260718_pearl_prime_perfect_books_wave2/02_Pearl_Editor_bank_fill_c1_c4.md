# 02 — Wave 1: Bank Fill C1–C4 (Pearl_Editor)

EXECUTE. This is the upstream-of-composer content lane — the spec's §5 step 3, and
the prerequisite that makes G-DEF4-hard-stopped cells renderable again. Do not stop
at summary/plan. Turn ends only on the signal below or one concrete BLOCKER.

GATE CHECK: `grep "perfect-books-wave2-substrate=" artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md` returns a value. Absent ⇒ STOP.

```
STARTUP_RECEIPT
AGENT: Pearl_Editor (lane 02)
TASK: Fill banks (C1 STORY pools, C2 EXERCISE, C3 accent banks, C4 persona-registry routing) for the designated ship-matrix cells so they render production-clean without foreign-persona bleed
SUBSYSTEM: teacher_mode + core_pipeline atoms (authority: specs/PHOENIX_V4_5_WRITER_SPEC.md; docs/SYSTEMS_V4.md; SOURCE_OF_TRUTH/)
AUTHORITY_DOCS: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.C (C1–C4) + §2 ownership + §6 non-goals; ANALYSIS_REPORT.md; MATRIX.tsv; CLAUDE.md anti-drift doctrine
WRITE_SCOPE: atoms/** and SOURCE_OF_TRUTH/** for the designated cells (STORY/EXERCISE/accent-bank/persona-routing surfaces); config routing/persona-label files the DEF4 fix requires; artifacts/qa/perfect_books_wave2_20260718/lane02/
OUT_OF_SCOPE: composer/topology (phoenix_v4/planning selector internals — banned lever); register_gate.py / F16 / DEF4 detector code (Lane 04 / Wave-1 own gates — never silence detectors); frozen flagship goldens + atoms feeding them; the line-edit manuscripts (Lane 03); hot coordination files
PROVENANCE:
  research:  ANALYSIS_REPORT.md register-fail findings + MATRIX.tsv per-cell gaps (the 100-book corpus study)
  documents: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.C
  builds_on: existing atom banks + tuple viability + accent planner anti-spam — FILL in place, mirror known-good pools; never greenfield a parallel bank
  inventory: EXTENDS (add atoms; no pool shrunk, no detector silenced)
BACKGROUND_SAFE: no   RESUME_SURFACE: lane02 proof root + offline ref
```

## DISCOVERY REPORT (before authoring)

1. From `MATRIX.tsv` + the ship matrix, list the designated Wave-2 cells and their
   exact deficits per C-item. Coordinate with Lane 03's cell picks (Q-W2-CELLS-01
   default: `corporate_managers×burnout×overwhelm` + 2 machine-clean cells) — fill
   the banks those 3 cells need FIRST (they gate the line-edit render), then broader
   ship-matrix cells as budget allows.
2. Thin-pool diagnosis (memory: deficit is SHAPE, not count): for each thin STORY
   pool, identify the missing emotional bands / classifier shape vs a known-good
   pool; mirror the known-good shape — do not just bulk-add atoms.
3. G-DEF4 debt: find which cells the Wave-1 DEF4 hard-stop now fails (foreign-persona
   registry bleed, esp. Gen-Z registry depth used as fallback for other personas —
   spec C4). The fix is routing / persona labels so the correct persona's registry
   is used — NOT silencing the detector.
4. Reuse-first: check `CANONICAL_ARTIFACTS_REGISTRY.tsv` for the canonical bank
   surfaces; edit in place.

## MISSION (research → banks; NEVER LLM-expand on the spine path)

- **C1** STORY pool ≥ `min_story_pool_size` with required emotional bands per
  designated cell (tuple viability PASS).
- **C2** per-cell EXERCISE bank for production (no silent practice_library-only on
  flagship cells — EXERCISE-BANK-RESOLUTION-01).
- **C3** accent banks stocked per topic for production budgets: `EXTERNAL_STORY`,
  `AUTHOR_COMMENTARY`, `WISDOM_ESSENCE` (3-para + secular — honor the lint gate),
  `CITED_EVIDENCE`. Accent planner anti-spam stays fail-closed.
- **C4** kill Gen-Z-registry-as-default-fallback for other personas via routing /
  persona labels → the DEF4 hard-stop clears legitimately.

Deterministic composition means thin pools must raise `InsufficientVariantsError` and
be fixed by ADDING atoms — never LLM-expand at build (`pearl_writer_expand.py` must
stay off the spine/production path). Authoring the atoms themselves is Tier-1 Pearl
Editor work (Claude Code, operator-present) — fine; the BUILD stays deterministic.

## VERIFY (per cell you fill)

- Tuple viability PASS. Four-piece chord render
  (`--pipeline-mode spine --quality-profile production --exercise-journeys --render-book`)
  reaches Layer-1 PASS with **DEF4 drops = 0** (no foreign-persona bleed) and no
  bracket/template stub. Record the enrichment_audit `defect4_drops` = 0.
- **Flagship parity:** if any atom you touch could feed the frozen goldens, run
  `scripts/ci/check_flagship_book_parity.py` (ch1 + `--snapshot full`, FULL checkout —
  sparse cones give false FAILs). Any parity break ⇒ revert that atom, record it.

## SMOKE → PILOT → SCALE

Smoke: fill 1 deficit on 1 cell → tuple viability PASS. Pilot: fully fill the 3
line-edit cells → each renders Layer-1 clean with DEF4=0. Scale: broader ship-matrix
cells as budget allows (bounded; log what was left for a later wave — no silent
truncation). Checkpoint ≤10 min to the proof root; tee long renders and poll; three
no-progress intervals ⇒ reduce to the 3 cells and land those.

## DO NOT

- Do NOT tune the composer/topology to "improve register" (banned lever, §2 + CLAUDE.md).
- Do NOT silence DEF4/F16 or weaken tuple viability / F14 / chord CI (§6).
- Do NOT edit frozen goldens or LLM-expand on the spine path. No `git add -A`.
- Do NOT claim any cell above `authored candidate` — that's Lane 03's ONTGP job.

## LANDING + CLEANUP + HANDOFF

Land the atom/bank/routing edits + per-cell render evidence (audits/scorecards; not
multi-MB EPUBs — declare those by path) via the INDEX recipe onto
`offline/perfect-books-wave2-bankfill-20260718` (or PR→merge if github; G-CLAIM will
require the acceptance-layer term — use `authored candidate`). Explicit paths;
diff-stat gate. Cleanup: render scratch removed/declared; temp index removed; CLEANUP
LEDGER in the handoff. Handoff:
`artifacts/coordination/handoffs/perfect_books_wave2_bankfill_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Editor_lane02
CELLS_FILLED=<n> (3 line-edit cells: <status each>)
C1_STORY=<pools brought to viability> C2_EXERCISE=<cells> C3_ACCENT=<banks stocked> C4_DEF4=<cells cleared, drops=0>
RENDER_PROOF=<per-cell Layer-1 PASS + defect4_drops=0 paths>
FLAGSHIP_PARITY=<byte-identical yes/no>
ACCEPTANCE_LAYER=authored candidate (banks filled; NOT system working — that's Lane 03)
DEFERRED=<ship-matrix cells left for a later wave, named — no silent truncation>
LANDED=<ref@full-sha | merge-sha>
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_bankfill_2026-07-18.md
SIGNAL=perfect-books-wave2-bankfill=<full-sha>
NEXT_ACTION=Lane 03 line-edit may launch on the 3 filled cells
```

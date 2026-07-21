# Handoff — Pearl Prime Perfect Books Wave-2 / Lane 04 — deferred CI gates

**Date:** 2026-07-19 (dispatched 2026-07-18; local execution)
**Agent:** Pearl_Dev (lane 04)
**Spec:** `artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md` §3.B
**Wave-1 parent:** `artifacts/coordination/handoffs/pearl_prime_perfect_books_wave1_2026-07-18.md`
(builds on gates 35-37, `agent/pearl-prime-perfect-books-wave1` @ `9056df3354df6a84755fb47a38da2793f141efa9`)
**Substrate:** `pearlstar_offline` (GitHub 403-suspended; `SUBSTRATE_LOCK.md`)
**Acceptance layer:** structurally clear (enforcement mechanisms only — no
register/quality claim per CLAUDE.md Bestseller Quality Anti-Drift Doctrine).

## Wave completed

Wave-2 / Wave-1's deferred sequencing step 3 from the spec: the three §3.B
rows left unbuilt by Wave-1 — G-F1H, G-ORIENT, G-ACCENT — all shipped
(none BLOCKED).

## Mechanisms landed

| ID | Mechanism | Path |
|---|---|---|
| G-F1H | F1 templated-paragraph cluster HARD_FAIL when it spans >= 6 distinct chapters (escalation on top of register_gate's existing WARN@2 / FAIL@3+ ladder — untouched) | `scripts/ci/check_f1h_templated_cluster_hard.py` |
| G-ORIENT | Ch1 first-120-words body/scene anchor check (lexicon OR SCENE-atom provenance); WARN by default, `--strict` for Layer-2 eligibility | `scripts/ci/check_orient_ch1_scene_anchor.py` + new lexicon SSOT `config/quality/orient_body_scene_lexicon.yaml` |
| G-ACCENT | Weekly accent-fill preflight matrix over top-N `MATRIX.tsv` cells; report-only per-PR, `--fail-closed` weekly cron | `scripts/ci/check_accent_supply_preflight.py` + `.github/workflows/accent-supply-preflight.yml` |

Wired into `.github/workflows/drift-detectors.yml` (3 new steps, non-blocking
for G-ORIENT/G-ACCENT, integrity-BLOCK for G-F1H) and
`scripts/run_production_readiness_gates.py` **gates 38-40**.

## Lexicon SSOT (new)

No approved body/scene anchor lexicon SSOT existed prior to this lane. Per the
prompt's fallback instruction, a minimal v1 was authored at
`config/quality/orient_body_scene_lexicon.yaml`, seeded from:

1. The frozen flagship Ch1 exemplar (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`,
   gen_z_professionals x anxiety, PROVEN-AT-BAR — read-only, not modified).
2. The existing HOOK-SCENE-FIRST-01 / F11 scene-first regex vocabulary already
   "approved" in `phoenix_v4/quality/register_gate.py` — cited as authority,
   not re-derived, to avoid two independently-drifting "approved" word lists
   for the same concept.

G-ORIENT is therefore **shipped, not BLOCKED** — but the lexicon is a v1
(58 words, English-only) and should be widened once Lane 03's line-edited
flagship cells give a larger authored-candidate corpus to seed from (see
NEXT_ACTION below).

## Discovery finding worth flagging upstream

The G-ACCENT preflight, run live against the real top-20 `MATRIX.tsv` cells,
found **14/20 cells with a real `no_supply_pool` gap** for a budgeted accent
class (mostly `WISDOM_ESSENCE` / `AUTHOR_COMMENTARY` / `EXTERNAL_STORY` on
non-pilot persona x topic pairs) — see
`artifacts/qa/perfect_books_wave2_20260718/lane04/ACCENT_SUPPLY_PREFLIGHT_SAMPLE.json`.
This is exactly the "Accent `no_supply_pool` hard-stops" finding the spec's
ANALYSIS_REPORT.md flagged, now materialized as a checkable ops-cadence
report. This is a bank-fill (C1-C4 / Lane 02-03) signal, not a Lane-04 fix —
Lane-04's mandate was the detector/matrix job, not filling the banks.

## What was NOT touched (per hard constraints)

- `register_gate.py`'s F16 (G-WRAP) severity logic/thresholds — read-only
  import of `_detect_f1_templated_paragraphs` / `_split_chapters` only.
- The DEF4 detector / enrichment path.
- F14 / chord CI / tuple viability / any existing threshold.
- Gates 35-37 (`check_acceptance_claim_language.py`,
  `check_catalog_manifest_acceptance_layer.py`,
  `check_catalog_ship_wrap_defect4.py`) — zero edits, only referenced as the
  shape to mirror.
- Atom banks, manuscripts, frozen goldens, hot coordination files
  (`PROGRAM_STATE.md`, `ACTIVE_WORKSTREAMS.tsv`, spec §8 checkboxes — Lane 06
  owns those).

## Tests + mutation checks

15/15 new unit tests pass
(`tests/test_check_f1h_templated_cluster_hard.py`,
`tests/test_check_orient_ch1_scene_anchor.py`,
`tests/test_check_accent_supply_preflight.py`). All three gates ran a §14
mutation check (violating fixture -> RED -> revert -> green) — full
commands/output in
`artifacts/qa/perfect_books_wave2_20260718/lane04/MUTATION_CHECKS.md`.

## Cleanup ledger

- Temp `GIT_INDEX_FILE` used for the offline landing recipe: unset after push
  (never left in the shell environment).
- No debug instrumentation, `print`-only scratch code, or `.bak` files left in
  any landed script (verified via the explicit-path diff-stat gate below —
  only the intended new/modified files are in the commit).
- Mutation-check scratch fixtures were written under `/tmp/lane04_mutation/`
  (outside the repo tree) and deleted at the end of each check — none were
  ever staged or committed.

## SIGNAL

```
SIGNAL=perfect-books-wave2-cigates=<full-sha — see CLOSEOUT_RECEIPT below>
```

## NEXT_ACTION

- Spec §8 "Done when" gate-row checkboxes for G-F1H/G-ORIENT/G-ACCENT are now
  checkable by Lane 06 (final audit) against gates 38-40 + this handoff.
- G-ORIENT lexicon SSOT v1 -> widen against Lane 03's flagship line-edit
  authored-candidate corpus once it lands (follow-on, not a Lane-04 blocker).
- The 14/20 G-ACCENT `no_supply_pool` gaps are a bank-fill signal for Lane
  02/03 (C1-C4), not a re-open of Lane 04's scope.

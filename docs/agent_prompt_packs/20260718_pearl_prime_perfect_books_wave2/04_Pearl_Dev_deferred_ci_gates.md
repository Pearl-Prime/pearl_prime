# 04 — Wave 1: Deferred CI Gates G-F1H / G-ORIENT / G-ACCENT (Pearl_Dev)

EXECUTE. The Wave-1-deferred pure-CI gates — buildable offline, independent of the
content lanes. Additive only; never weaken or touch the Wave-1 gates. Do not stop at
summary/plan. Turn ends only on the signal below or one concrete BLOCKER.

GATE CHECK: `grep "perfect-books-wave2-substrate=" artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md` returns a value. Absent ⇒ STOP.

```
STARTUP_RECEIPT
AGENT: Pearl_Dev (lane 04)
TASK: Implement G-F1H (templated cluster ≥6 chapters HARD), G-ORIENT (Ch1 body/scene lexicon), G-ACCENT (weekly accent-fill preflight matrix) per spec §3.B — additive gates + tests, mutation-verified
SUBSYSTEM: pearl_devops CI gates + core_pipeline quality (authority: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.B; docs/GITHUB_OPERATIONS_FRAMEWORK.md)
AUTHORITY_DOCS: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.B (G-F1H/G-ORIENT/G-ACCENT rows) + §6 non-goals; Wave-1 IMPLEMENTATION_CLOSEOUT.md (existing G-CLAIM/G-LAYER/G-WRAP/G-DEF4 patterns to mirror)
WRITE_SCOPE: scripts/ci/ (new gate scripts); phoenix_v4/quality/ (F1 cluster detector ONLY if additive — never edit F16/DEF4); tests/; .github/workflows/drift-detectors.yml (new BLOCK steps); scripts/run_production_readiness_gates.py (new gate numbers 38+); artifacts/qa/perfect_books_wave2_20260718/lane04/
OUT_OF_SCOPE: register_gate.py F16 (G-WRAP, Wave-1) + enrichment DEF4 path (G-DEF4, Wave-1) — do not modify; atom banks / manuscripts (content lanes); frozen goldens; hot coordination files
PROVENANCE:
  research:  ANALYSIS_REPORT.md F1/F6/F7 register-fail dominance + accent no_supply_pool findings
  documents: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.B
  builds_on: the Wave-1 gate scripts (check_acceptance_claim_language.py / check_catalog_manifest_acceptance_layer.py / check_catalog_ship_wrap_defect4.py) — same shape, additive
  inventory: EXTENDS (new gates; existing gates untouched)
BACKGROUND_SAFE: yes (CI code + tests) — but poll test runs, no monitor-parking
RESUME_SURFACE: lane04 proof root + offline ref
```

## DISCOVERY REPORT

1. Read the three §3.B rows precisely: G-F1H (F1 templated cluster ≥6 chapters →
   HARD_FAIL; note F1 already FAILs at size ≥3 — escalate carefully, don't
   double-count), G-ORIENT (Ch1 first 120 words ≥1 body/scene anchor from an approved
   lexicon OR SCENE-atom provenance → WARN→escalate to authored-candidate eligibility),
   G-ACCENT (weekly preflight matrix fails if top-N catalog cells have
   `no_supply_pool` for budgeted accents).
2. G-ORIENT needs an **approved lexicon SSOT** — check if one exists; if not, this
   gate's blocker is that SSOT (author a minimal one from the flagship Ch1 Orient
   exemplar, or mark G-ORIENT BLOCKED-on-lexicon and ship G-F1H + G-ACCENT).
3. Reuse-first: mirror the Wave-1 gate script + test structure exactly (same CLI
   shape, same drift-detectors wiring pattern).

## MISSION

Implement each gate as an additive script + wire into `drift-detectors.yml` (new
BLOCK/WARN steps) + `run_production_readiness_gates.py` (new gate numbers). Each gate
ships with tests AND a **mutation check (§14):** deliberately introduce a violating
fixture → gate goes RED → revert; a gate green under mutation is not accepted.
G-ACCENT is a weekly *preflight matrix* (ops-cadence report + fail-closed), not a
per-PR blocker — build the matrix job + fill-rate report.

## SMOKE → PILOT → SCALE

Smoke: G-F1H script + 1 passing + 1 failing fixture. Pilot: all three gates' fixtures
+ mutation checks. Scale: drift-detectors + readiness wiring + full test run.
Checkpoint ≤10 min; tee pytest and poll; three no-progress intervals ⇒ land the gates
that pass mutation, mark the rest BLOCKED.

## DO NOT

- Do NOT modify F16 (G-WRAP) or the DEF4 detector (Wave-1) — additive only.
- Do NOT weaken F14 / chord CI / tuple viability / existing thresholds to make CI
  green (§6). Fix the ruler, never bend it (precision-fix only, with a regression
  test proving real violations still fail).
- No `git add -A`. No touching content banks or goldens.

## LANDING + CLEANUP + HANDOFF

Land gate scripts + tests + workflow wiring via the INDEX recipe onto
`offline/perfect-books-wave2-cigates-20260718` (or PR→merge if github — these gates
are pure CI, safe to merge on green). Explicit paths; diff-stat gate. Cleanup: temp
index removed; no debug instrumentation left (verify staged diff); CLEANUP LEDGER in
handoff. Handoff:
`artifacts/coordination/handoffs/perfect_books_wave2_cigates_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev_lane04
GATES_LANDED=<G-F1H|G-ORIENT|G-ACCENT — per gate: shipped/BLOCKED-reason>
MUTATION_CHECKS=<per gate RED-then-green | FAIL>
TESTS=<counts>
WIRED=<drift-detectors steps + readiness gate numbers>
ACCEPTANCE_LAYER=structurally clear (enforcement mechanisms; not a quality certification)
LANDED=<ref@full-sha | merge-sha>
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_cigates_2026-07-18.md
SIGNAL=perfect-books-wave2-cigates=<full-sha>
NEXT_ACTION=spec §8 gate rows checkable by Lane 06; G-ORIENT lexicon SSOT is a follow-on if BLOCKED
```

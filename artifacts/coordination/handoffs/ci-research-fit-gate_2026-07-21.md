# Handoff — Lane 01 ci-research-fit-gate (2026-07-21)

## CLOSEOUT_RECEIPT

- AGENT: Pearl_Architect
- LANE: ci-research-fit-gate
- STATUS: LANDED-OFFLINE (local branch + diffs only; no commit, no push — per operator constraint)
- BRANCH: `agent/ci-research-fit-gate-20260721`
- PR: none (do not open until GitHub access returns / operator asks)
- MERGE_SHA: n/a
- SIGNAL: Lane 01 smoke PASS (advisory). Lane 02/04 unblocked on gate contract below.
- PROOF_ROOT: `artifacts/qa/bestseller_register_20260719/batch9/corporate_managers__burnout__overwhelm` (seed-43001-style `research_fit: {}`)
- TESTS: see below
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure (gate wiring) — not bestseller
- CLEANUP: no worktree; local branch kept (HOLD — uncommitted Lane 01 diffs); no remote branch; scratch `/tmp/lane01_*` removable; no background jobs held
- HANDOFF: this file
- NEXT_ACTION: Lane 02 (atom authoring queue) + Lane 04 (acceptance-layer stamp) may consume cell-key / stamp contract; do not start Lane 03 from this handoff

## Branch / base note (IMPORTANT)

- Current branch: `agent/ci-research-fit-gate-20260721` @ `eae593f0b070f20722a7a41502b0150bc5c8b0de`
- `origin/main`: `9e9b9e606791590337cd7d0f2fb425def2e6f760`
- Clean `git checkout -b … origin/main` failed (stale `index.lock` + checkout SIGKILL on this large worktree). Branch was created from the prior local tip (teacher-onboarding lineage; ~13 commits ahead of origin/main).
- **Landing must cherry-pick / re-apply only the Lane 01 file list onto a fresh `origin/main` branch** before PR. Do not open a PR that includes the unrelated teacher-onboarding commits.

## Discovery vs pack INDEX

- Pack claimed `check_research_fit_honesty.py` exists but is unwired. On `origin/main` the path **does not exist** (`git cat-file` fatal). File was local-only untracked; Lane 01 **adds** it as a new tracked candidate.
- `StorySchedule.research_fit` / `no_story_atoms` skip stamping is **not** present in current `phoenix_v4/planning/story_planner.py` on this tree. Real proof-root audits use bare `research_fit: {}`. Gate treats that as unbound (legacy_planner ≡ no_story_atoms).
- `tests/test_bestseller_atom_pipeline_honesty_20260720.py` still fails 4/5 against current planner (pre-existing; not introduced by Lane 01). New `tests/test_check_book_story_authored.py` is 15/15 PASS.

## Files changed

| Path | Status |
|---|---|
| `scripts/ci/check_book_story_authored.py` | NEW (untracked) |
| `scripts/ci/check_research_fit_honesty.py` | NEW (untracked; not on origin/main) |
| `tests/test_check_book_story_authored.py` | NEW (untracked) |
| `scripts/run_production_readiness_gates.py` | MODIFIED (gates 34–35 advisory + WARN status) |
| `.github/workflows/drift-detectors.yml` | MODIFIED (two ADVISORY steps, `continue-on-error: true`) |
| `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` | MODIFIED (Layer 1 research_fit binding cap paragraph) |
| `artifacts/coordination/handoffs/ci-research-fit-gate_2026-07-21.md` | NEW (this handoff) |

## Gate contract (for Lane 02/04)

- Unbound when: `research_fit.mode == "skipped"` + skip_reason contains `no_story_atoms`, OR bare `research_fit: {}` / missing structure.
- Bound when: mode in `{research_fit_v1, twelve_shape_continuity}` AND at least one of `spine_pins` / `book_phases` / `motif_ledger`.
- Stamp file: `book_acceptance_stamp.json` next to audit → `{research_fit_bound: false, acceptance_layer: "structurally_clear_only", research_fit_unbound_reason: ...}`
- CLI: `--strict` hard-blocks (exit 1); default advisory (exit 0 + WARN).

## THRESHOLD DECISION (operator-tier — NOT flipped)

**Hard-blocking book rendering on unbound research_fit is OFF.**

- Default: advisory WARN + Layer 1 cap stamp; books still render.
- Documented hard-block: `--strict` on `check_book_story_authored.py`; drop `--advisory` / remove `continue-on-error` on Drift detectors honesty step.
- Flipping to hard-block changes which books can render at all and requires operator sign-off before merge (INDEX Evidence Requirements).

## Smoke tests

```bash
# Proof root (seed-43001-style empty research_fit)
PROOF=artifacts/qa/bestseller_register_20260719/batch9/corporate_managers__burnout__overwhelm
cp -R "$PROOF" /tmp/lane01_smoke

PYTHONPATH=. python3 scripts/ci/check_book_story_authored.py --book-dir /tmp/lane01_smoke
# PASS: EXIT 0, WARN unbound, stamp research_fit_bound:false / structurally_clear_only

PYTHONPATH=. python3 scripts/ci/check_book_story_authored.py --book-dir /tmp/lane01_smoke --strict
# PASS: EXIT 1 (strict blocks)

PYTHONPATH=. python3 scripts/ci/check_research_fit_honesty.py --advisory /tmp/lane01_smoke
# PASS: EXIT 0 with WARN findings

PYTHONPATH=. python3 -m pytest tests/test_check_book_story_authored.py -q
# PASS: 15 passed

PYTHONPATH=scripts/ci:. python3 scripts/ci/check_book_story_authored.py --base HEAD~1 --head HEAD --no-stamp
# PASS: EXIT 0 (0 changed audits)

# Full readiness suite (prior run): gates 34 WARN + 35 WARN advisory; unrelated gate 27 data-dict FAIL pre-existing
```

## Reviewer checklist (Claude Sonnet 5)

1. Confirm both new CI steps in `drift-detectors.yml` are **ADVISORY** (`continue-on-error: true` / `--advisory` / no `--strict`).
2. Confirm readiness gates 34–35 use `advisory=True` and do **not** increment `failed`.
3. Confirm `check_book_story_authored.py` default exit 0 on unbound; `--strict` exit 1.
4. Confirm stamp fields: `research_fit_bound`, `acceptance_layer: structurally_clear_only`.
5. Confirm scorecard paragraph caps unbound books at Layer 1.
6. Confirm no weakening of manga gates 21–23 / F14.
7. Flag that `check_research_fit_honesty.py` is **new on origin/main** (pack assumed pre-existing).
8. Flag branch is **not** a clean origin/main tip — re-base/cherry-pick Lane 01 files only before PR.
9. Do not treat this lane as bestseller; infrastructure only.
10. Do not start Lane 03 from this PR.

## Diff summary

Tracked: +138 / −3 across workflow, scorecard, readiness runner (see `git diff` on those three paths).

Untracked new file sizes:
- `scripts/ci/check_book_story_authored.py` — 281 lines
- `scripts/ci/check_research_fit_honesty.py` — 129 lines
- `tests/test_check_book_story_authored.py` — 162 lines

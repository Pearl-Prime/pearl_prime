# Parse-Sweep Guard: Check (D) — Bare-Header-Text Stub Content (2026-07-10)

Follow-up from `artifacts/qa/OVERTHINKING_STUB_CONTENT_FIX_2026-07-10.md` (PR #5503). Extends
`scripts/ci/check_canonical_atom_parse_sweep.py` — a **required status check** gating every PR
to main — with a new check (D) that catches the un-promoted sibling of the PR #1590 DEFECT-7
over-match this gate already guards against.

## Why this needed extreme caution

This gate's own docstring documents a prior incident: PR #1590's automated repair over-matched
and turned 1,215 clean `CANONICAL.txt` files into `NO_STORY_POOL` failures. A bug in this
extension would not just affect atom-content PRs — the `pull_request` trigger is deliberately
unfiltered (any path filter + required-check = merge deadlock), so it runs on **every PR to
main**. Treated this as load-bearing infrastructure, not a quick script edit:

1. Unit-tested the new regex logic in isolation against 6 synthetic cases (including the two
   riskiest: legit terse "band-fill" prose like `"Crisis. Breakthrough. The moment of maximum
   intensity."` must NOT false-positive, and prose that merely *mentions* a role/version in
   passing must NOT false-positive) before touching the real script.
2. Built the baseline against a **clean `origin/main` snapshot** (`git archive`, not the local
   working tree, which already had PR #5503's fix applied and would have produced a
   983-entry-short, incorrect baseline for the current main branch state).
3. Ran the full existing regression test suite (`test_canonical_atom_parse_sweep_guard.py`) plus
   4 new tests against that clean snapshot before landing — 11/11 pass, ~12.5 min.
4. Verified check (D) does not interact with or regress checks (A)/(B)/(C) at all (identical
   `new_parse_failures`/`new_overmatch_signatures`/`story_pool_overmatch` counts with or without
   the new check present).
5. Verified the gate stays green both before *and after* PR #5503 lands (order-independent):
   applying #5503's fix to the clean snapshot drops `stub_fail_total` from 883 → 881 with
   `new_stub_failures` staying at 0 in both cases — the baseline over-covering two now-fixed
   files is harmless, not a false negative.

## What was added

- **Check (D)**: `stub_prose_signature_hits()` — counts blocks whose PROSE body (not metadata,
  which is what checks A/B/C already inspect) is an exact bare `LABEL vNN` token. Uses a new
  4-group regex (`_PROSE_BLOCK_RE`) matching the shape
  `prose_resolver._parse_canonical_with_prose` uses at render time, since this check targets
  exactly what the renderer would select — not what the strict metadata-only parser validates.
- **Separate baseline file**: `scripts/ci/check_canonical_atom_parse_sweep_stub_baseline.txt`
  (883 entries, generated via the new `--update-stub-baseline` flag against the clean origin/main
  snapshot) — kept independent from the existing `check_canonical_atom_parse_sweep_baseline.txt`
  so the two debt categories (structural parse failures/over-matches vs. content-level stubs)
  stay separately reviewable. No hand-editing; regenerated only via the script's own mechanism,
  mirroring the existing `--update-baseline` convention exactly.
- `sweep()` now also returns `stub_fail_total`/`new_stub_failures`/`stub_baseline_size`; `ok`
  requires `new_stub_failures == []` alongside the existing three conditions.
- 4 new tests in `test_canonical_atom_parse_sweep_guard.py`, mirroring the existing test style:
  detects the un-repaired shape, silent on real prose, silent on legit terse band-fill prose
  (the specific false-positive risk flagged in the task), and confirmed non-overlapping with the
  existing over-match signature (each defect class triggers only its own check).
- `.github/workflows/atoms-parse-sweep.yml`: added the new baseline file to the `push` trigger's
  `paths:` filter (so a baseline-only push to main also re-verifies); updated comments/step name
  to reflect checks A/B/C/D. `pull_request` trigger unchanged (still deliberately unfiltered).

**Deliberately NOT added**: a STORY-pool "never baseline-able" exception for check (D), mirroring
check (C)'s treatment of over-matched STORY pools. (C) exists because an over-matched STORY pool
causes a hard `NO_STORY_POOL` build failure that can never legitimately be "pre-existing debt" —
but a check-(D) stub doesn't fail any build; it silently ships as garbage one-line text, which is
a real problem but a different one, and the task didn't ask for this extra carve-out. Noted here
as a design choice open for reconsideration, not added unprompted.

## Verification (against the clean origin/main snapshot, base SHA see PR)

- `17,195` `CANONICAL.txt` files scanned
- `883` stub-content signatures found, all baselined — `new_stub_failures: 0`, `ok: True`
- `new_parse_failures: 0`, `new_overmatch_signatures: 0`, `story_pool_overmatch: 0` — zero
  interaction with existing checks
- Full test suite: 11/11 pass (7 existing + 4 new)
- Post-#5503-fix simulation: `stub_fail_total` 883 → 881, `new_stub_failures` stays 0

## Scope

`scripts/ci/check_canonical_atom_parse_sweep.py`, its test file, the new baseline file, and the
workflow YAML. No `atoms/**` content touched.

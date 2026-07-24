# Lane 03 — Extend locale coverage to authored-vs-stub-vs-missing, every locale

```text
EXECUTE. Do not stop at summary or plan. End only MERGED, LANDED-OFFLINE, or BLOCKED.

You are Pearl_Localization for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Localization
- LANE=locale-matrix-authored-vs-stub
- EXECUTION_MODE=local_fallback
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/03_locale_matrix_authored_vs_stub.md

READ FIRST:
- docs/PROGRAM_STATE.md ("Localization" section)
- docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md
- Lane 01's CLOSEOUT_RECEIPT / handoff at
  artifacts/coordination/handoffs/atom-matrix-true-topics_2026-07-23.md — you
  need its reconciled topic list and 3-state schema as the EN-side baseline
  you are crossing with locales
- scripts/ci/report_translation_coverage.py IN FULL (the tool you are
  extending — note it already imports `check_native_check.scan_native_check`
  for some corruption detection; read that too)
- config/localization/locale_registry.yaml (14 locales: en-US baseline + CJK6
  + European/pt-BR bucket)
- artifacts/qa/atom_authoring_backlog_20260722.tsv (650-row EN_ALSO_CORRUPTED
  backlog, landed yesterday — read-only input, do not edit) and its handoff at
  artifacts/coordination/handoffs/atom_corruption_authoring_backlog_20260722.md
- docs/PEARL_NEWS_SIDEBAR... no — irrelevant, skip; instead read
  `feedback_translation_bar_is_stub_contaminated`-equivalent context by
  grepping the repo/CLAUDE.md history for prior stub-vs-file-existence
  findings on translation coverage (search commit log for "stub" AND
  "coverage" AND locale terms) to confirm you are not re-deriving a fix that
  already landed
- Open PR #211 (`gh pr view 211`) — zh-TW book build BLOCKED on
  EXERCISE-BANK-RESOLUTION-01 English-only classifier — read its current
  description/comments for the exact classifier behavior; you are not fixing
  this PR, but your locale matrix must correctly represent this cell's true
  state (not "covered")
- Open PR #208 (`gh pr view 208`) — zh-CN missing gen_x_sandwich
  compassion_fatigue EN source variants — same: represent honestly, do not
  duplicate the fix
- Open PR #93 (`gh pr view 93`) — zh-TW register-rewrite scope correction,
  "bucket is untranslated not register" — a live example of exactly the
  mis-bucketing class you must avoid reproducing in your new classifier

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm Lane 01 landed and re-read its actual final
  schema (not the version described in this prompt, which is a snapshot).
- confirm PRs #211/#208/#93 current state (may have merged/closed since this
  pack was authored) — do not treat them as still-open without checking.
- confirm the 650-row backlog TSV path/row-count is unchanged; if it has been
  worked down since 2026-07-22, use the live remaining count.
- gh pr list --state open — confirm no other PR is mid-edit on
  report_translation_coverage.py.

PRE-REQUISITE CHECKS:
- Lane 01's matrix artifact is readable and its schema is stable.
- report_translation_coverage.py runs standalone without error on current
  origin/main.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA
- Lane 01's final EN matrix schema fields
- current file-existence coverage numbers per locale (re-run
  report_translation_coverage.py fresh, do not copy the 07-22 PROGRAM_STATE
  figures — they are already stale by definition)
- exact stub/corruption detection logic already present in
  check_native_check.scan_native_check — do not reinvent if it already does
  what you need, extend it instead

PROVENANCE:
- research: docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md;
  artifacts/qa/atom_authoring_backlog_20260722.tsv
- documents: CLAUDE.md Manga Vision-Conformance Doctrine (stub-as-done drift
  class — the CJK-atom equivalent of `check_render_progress_bytes.py`'s
  bytes<50_000 stub kill); PROGRAM_STATE.md Localization section
- builds_on: scripts/ci/report_translation_coverage.py (EXTENDS, do not fork),
  scripts/ci/check_native_check.py (reuse its corruption-detection logic),
  Lane 01's 3-state EN matrix (the baseline you cross with locale)
- inventory: EXTENDS — existing file-existence coverage numbers must remain
  in the output (for anything already consuming them) alongside the new
  authored-vs-stub-vs-missing breakdown, never REDUCED

MISSION:
Cross Lane 01's true EN persona×topic matrix with every locale in
`locale_registry.yaml`, classifying each (persona, topic, locale) cell into:
- `MISSING` — no locale CANONICAL.txt exists for a cell that has EN
  CANONICAL_ONLY or ANCHORED_REAL (i.e. translation simply hasn't happened).
- `STUB_OR_CORRUPTED` — a locale file exists but fails the corruption/stub
  check (reuse/extend `check_native_check.scan_native_check`'s detection;
  cross-reference the 650-row EN_ALSO_CORRUPTED backlog as known-bad EN
  sources whose locale translations, if any, are downstream-corrupted by
  construction).
- `AUTHORED_REAL` — locale file exists, passes the corruption/stub check, and
  its EN source cell is at least CANONICAL_ONLY (a locale cell cannot be
  AUTHORED_REAL if its EN source is MISSING — that would be translating
  nothing; flag any such case as a data-integrity anomaly to report, not
  silently classify).

Also add a targeted honesty check for the #93-style mis-bucketing class: any
cell your classifier would otherwise report as a "register" or "quality"
issue must first confirm the cell has actually been translated at all
(non-MISSING) — an untranslated cell is `MISSING`, never a register/quality
bucket, no matter what upstream gate produced the original wrong bucketing.

DELIVERABLES:
- scripts/ci/report_translation_coverage.py (extended in place, new 3-state
  per-locale output alongside existing file-existence counts)
- artifacts/qa/locale_atom_governance_<run-date>/ (new proof root: per-locale
  matrix JSON + summary MD, one file per locale plus a combined rollup)
- tests/test_report_translation_coverage_3state.py (new) proving the 3
  classifications on: one known-MISSING locale cell, one known
  STUB_OR_CORRUPTED cell (pull a real row from the 650-row backlog TSV as
  fixture), one known AUTHORED_REAL cell (pick from the highest-coverage
  locale, e.g. zh-TW)
- one paragraph noting PRs #211/#208/#93's cells' TRUE classification under
  this new tool, added to this lane's handoff (not to PROGRAM_STATE directly
  — that's Lane 04's job)

SMALLEST SAFE BATCH:
- smoke: run the extended tool for ONE locale (zh-TW, the most mature) against
  ONE persona, confirm all 3 states appear plausibly
- pilot: run for zh-TW, ja-JP, zh-CN, ko-KR (the 4 locales with existing
  PROGRAM_STATE figures) full catalog, sanity-check the new authored-vs-stub
  numbers are lower than or equal to the old file-existence numbers (they
  can never be higher — stub/corrupted is a subset of file-exists)
- scale: run for all 14 locales, generate the full rollup artifact, open PR

HANG PREVENTION:
- poll interval: 5 minutes
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED after three unchanged polls
- max window: 120 minutes (14-locale full sweep may run longer than a typical
  90-minute lane — this is explicitly budgeted, not a violation of the
  standard window)

TESTS/PROOFS:
- `python3 scripts/ci/report_translation_coverage.py` (full run, all locales)
- `pytest tests/test_report_translation_coverage_3state.py`
- Proof root: `artifacts/qa/locale_atom_governance_<run-date>/` with all 14
  locale files present plus rollup.

DO NOT:
- do not fix the underlying #211/#208/#93 gaps in this lane — represent them
  honestly in the matrix, cross-reference the PRs, do not scope-creep into
  authoring atoms or translations yourself
- do not treat file-existence as authored-real anywhere in the new
  classification — that is the exact bug being fixed
- do not fork a parallel translation-coverage tool — extend
  report_translation_coverage.py in place
- no stale locale figures — every number in PROGRAM_STATE's Localization
  section is a snapshot; re-derive live, note deltas explicitly in the handoff

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- LANDED-OFFLINE: GitHub blocked — branch pushed, full diff in handoff, ready
  to open PR the moment access returns.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree; local branch; remote branch; scratch files; background jobs; held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/locale-matrix-authored-vs-stub_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Localization
- LANE: locale-matrix-authored-vs-stub
- STATUS=MERGED|LANDED-OFFLINE|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: locale-atom-matrix-3state=<full-sha>
- PROOF_ROOT:
- TESTS:
- PER_LOCALE_AUTHORED_REAL_COUNTS: (the honest numbers — expect these to be
  materially lower than the file-existence numbers in PROGRAM_STATE; report
  the delta explicitly, do not soften it)
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure
- CLEANUP:
- HANDOFF:
- NEXT_ACTION: (should point at Lane 04, which combines this with Lane 01's
  output into the single "are we 100%" report)
```

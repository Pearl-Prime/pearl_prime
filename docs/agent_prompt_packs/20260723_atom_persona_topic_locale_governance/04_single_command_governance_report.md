# Lane 04 — Single "are we 100%" report + claim-honesty gate + PROGRAM_STATE reconciliation

```text
EXECUTE. Do not stop at summary or plan. End only MERGED, LANDED-OFFLINE, or BLOCKED.

You are Pearl_Architect for Phoenix Omega, closing out as Pearl_PM for the
final SSOT reconciliation step.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=atom-governance-single-report
- EXECUTION_MODE=local_fallback + github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/04_single_command_governance_report.md

READ FIRST:
- docs/PROGRAM_STATE.md (full — you will edit its "Atom coverage (en_US)" and
  "Localization" sections)
- docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md
- Lane 01's CLOSEOUT_RECEIPT/handoff (EN 3-state matrix, final schema)
- Lane 03's CLOSEOUT_RECEIPT/handoff (per-locale 3-state matrix, final schema)
- Lane 02's CLOSEOUT_RECEIPT/handoff (the registration gate — you report on
  its presence, you do not modify it)
- CLAUDE.md Bestseller Quality Anti-Drift Doctrine + Manga Vision-Conformance
  Doctrine (the acceptance-layer naming discipline this report must enforce
  on every consumer of it — a report output is never itself "100%" without
  the denominator and layer printed alongside)
- docs/SESSION_UNITY_PROTOCOL.md (hot-file rules — PROGRAM_STATE.md is a hot
  coordination file, you are the ONE serial actor for this edit)

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm BOTH Lane 01 and Lane 03 have landed (MERGED or
  LANDED-OFFLINE) — if either has not, STOP, this lane is blocked, name which
  one and its current status.
- re-read PROGRAM_STATE.md's live current content immediately before editing
  it — another session may have updated it since Lane 01/03 landed; do not
  clobber unrelated edits, merge your section update cleanly.
- gh pr list --state open — confirm no other PR is mid-edit on
  docs/PROGRAM_STATE.md right now; if one is, serialize behind it.

PRE-REQUISITE CHECKS:
- Lane 01's matrix artifact and Lane 03's per-locale artifacts are both
  present, readable, and their schemas are compatible enough to combine
  (same cell-key format for persona/topic).

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA
- Lane 01's final EN 3-state totals (MISSING / CANONICAL_ONLY / ANCHORED_REAL
  counts and the reconciled topic-list denominator)
- Lane 03's final per-locale 3-state totals (all 14 locales)
- Lane 02's registration gate status (wired? advisory or strict? any
  currently-unregistered dimensions flagged?)
- confirm no other in-flight edit to PROGRAM_STATE.md right now

PROVENANCE:
- research: Lane 01 + Lane 03 output artifacts (the only source of truth for
  this report — do not hand-estimate any number)
- documents: CLAUDE.md acceptance-layer taxonomies (bestseller + manga);
  docs/PROGRAM_STATE.md's existing glossary conventions (Listing vs EPUB
  distinction — apply the same "do not conflate two different things" rigor
  to CANONICAL_ONLY vs ANCHORED_REAL vs AUTHORED_REAL)
- builds_on: Lane 01's atom_coverage_audit.py output, Lane 03's
  report_translation_coverage.py output, Lane 02's check_atom_registration.py
- inventory: EXTENDS (new report script, new PROGRAM_STATE section content),
  never REDUCED — do not delete the existing Atom coverage / Localization
  prose, replace stale numbers with reconciled ones and add the new schema's
  numbers alongside

MISSION:
Give the operator ONE command that answers "are we 100%" honestly, per
persona×topic cell and per locale, with the acceptance layer always named.

1. Write `scripts/inventory/atom_governance_report.py`: loads Lane 01's EN
   matrix + Lane 03's per-locale matrices, and for a given scope (all cells,
   one persona, one locale, or one specific persona×topic×locale cell) prints:
   - the cell's classification (MISSING / CANONICAL_ONLY / ANCHORED_REAL for
     EN; MISSING / STUB_OR_CORRUPTED / AUTHORED_REAL for locale)
   - the acceptance layer that classification caps out at (never higher than
     `authored_candidate` — this report cannot know Layer 3/4 without a human
     read, and must say so explicitly in its own output, not just omit it)
   - the denominator used (reconciled topic-list count from Lane 01)
   - a summary rollup: total cells, count per state, percentage ONLY ever
     printed alongside its denominator and never as a bare number
2. Write a claim-honesty CI gate (extend an existing gate or add a small new
   one in the same PR): any doc, handoff, or CLOSEOUT_RECEIPT under this
   repo that contains the string "100%" together with "atom" or "coverage" or
   "story" (case-insensitive, word-boundary matched — precision-fix per
   router §15, avoid false-positiving on unrelated "100%" mentions) must also
   cite this report's output path/timestamp/hash in the same file, or the
   gate WARNs. This is advisory, matching Lane 02's default posture — surface
   any hard-block escalation to the operator, do not decide it silently.
3. Reconcile `docs/PROGRAM_STATE.md`: update the "Atom coverage (en_US)"
   section to show the reconciled 3-state EN numbers (replacing the old bare
   "100% on 15 topics / 29.8% on 57" framing with the new honest breakdown
   and its denominator), and update the "Localization" section's per-locale
   percentages to show both the old file-existence number AND the new
   authored-vs-stub number side by side, labeled clearly, so the delta is
   visible rather than silently replacing one potentially-misleading number
   with another that could itself be misread without context.
4. Run the final audit named in INDEX.md: verify the report correctly labels
   (a) a known-anchored EN cell, (b) a known-uncovered EN cell, (c) a
   known-stub-contaminated locale cell from the 650-row backlog sample — all
   three must classify correctly, not just run without error.

DELIVERABLES:
- scripts/inventory/atom_governance_report.py (new)
- CI claim-honesty gate (new or extended existing file — your choice of
  minimal-footprint location; document which)
- docs/PROGRAM_STATE.md updated (Atom coverage + Localization sections)
- tests/test_atom_governance_report.py (new) covering the 3 final-audit cases
  above plus the claim-honesty gate's own mutation test (a doc claiming "100%
  atom coverage" with no citation must WARN; the same doc with a citation
  must pass)
- artifacts/qa/atom_governance_report_<run-date>/ (proof root: full report
  output for at least the 3 audit cases plus a full-catalog rollup run)

SMALLEST SAFE BATCH:
- smoke: run the report for ONE known cell, confirm correct classification +
  layer label
- pilot: run the report for the 3 final-audit cases, confirm all correct;
  run the claim-honesty gate against one intentionally-bad fixture doc and
  one intentionally-good one, confirm WARN vs pass
- scale: run the full-catalog + full-locale rollup, update PROGRAM_STATE.md,
  open PR

HANG PREVENTION:
- poll interval: 5 minutes
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED after three unchanged polls
- max window: 90 minutes

TESTS/PROOFS:
- `python3 scripts/inventory/atom_governance_report.py --scope all`
- `python3 scripts/inventory/atom_governance_report.py --cell
  millennial_women_professionals anxiety overwhelm` (or equivalent CLI form)
- `pytest tests/test_atom_governance_report.py`
- Proof root: artifacts/qa/atom_governance_report_<run-date>/ with the 3
  audit-case outputs plus full rollup.

DO NOT:
- do not print a bare percentage anywhere in this report's output without its
  denominator and acceptance-layer cap printed in the same breath
- do not claim Layer 3 (system working) or Layer 4 (bestseller
  register/PROVEN-AT-BAR) from this report — it is a Layer 1/2 instrument only,
  say so in the report's own header every time it runs
- do not silently overwrite PROGRAM_STATE.md's existing prose — preserve the
  glossary and other sections untouched, edit only the two named sections,
  and re-read the file immediately before writing to catch concurrent edits
- no local-only finish — this is the pack's final lane, it must end MERGED or
  LANDED-OFFLINE with a real signal, never "report generated, someone review
  later"

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- LANDED-OFFLINE: GitHub blocked — branch pushed, full diff in handoff, ready
  to open PR the moment access returns.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree; local branch; remote branch; scratch files; background jobs; held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/atom-governance-single-report_2026-07-23.md
- Update artifacts/coordination/ACTIVE_WORKSTREAMS.tsv with this pack's final
  row (status=complete, signal tokens from all 4 lanes)

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Architect
- LANE: atom-governance-single-report
- STATUS=MERGED|LANDED-OFFLINE|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: atom-governance-report-live=<full-sha>
- PROOF_ROOT:
- TESTS:
- FINAL_EN_NUMBERS: (reconciled 3-state totals + denominator)
- FINAL_LOCALE_NUMBERS: (all 14 locales, authored-real counts)
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure (Layer 1/2
  measurement instrument — this pack does not itself produce a bestseller or
  PROVEN-AT-BAR claim for any cell)
- CLEANUP:
- HANDOFF:
- NEXT_ACTION: name the single next real content-authoring lane this report
  surfaces as highest-priority (e.g. the persona×topic cell(s) closest to
  ANCHORED_REAL, or the locale with the largest authored-vs-file-existence
  gap) — this pack builds the instrument, the next lane uses it to actually
  close a gap
```

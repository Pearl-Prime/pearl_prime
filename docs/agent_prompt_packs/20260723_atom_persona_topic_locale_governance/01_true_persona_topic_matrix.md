# Lane 01 — Build the true EN persona×topic 3-state coverage matrix

```text
EXECUTE. Do not stop at summary or plan. End only MERGED, LANDED-OFFLINE, or BLOCKED.

You are Pearl_Architect for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=atom-matrix-true-topics
- EXECUTION_MODE=local_fallback
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/01_true_persona_topic_matrix.md

READ FIRST:
- docs/PROGRAM_STATE.md ("Atom coverage (en_US)" section)
- docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md
- docs/agent_prompt_packs/20260721_bestseller_atom_flow/INDEX.md (research_fit
  binding mechanism you are consuming as a signal, not re-deriving)
- scripts/inventory/atom_coverage_audit.py (the tool you are extending —
  read `get_canonical_topics()` fully; it has a 3-tier fallback chain that is
  the likely source of the 15-vs-57 discrepancy)
- config/source_of_truth/topic_registry.yaml (15 topics)
- scripts/ci/check_research_fit_honesty.py and
  scripts/ci/check_book_story_authored.py (PR #9 — the honesty signal for
  "does this cell actually bind," which you will use to distinguish
  CANONICAL-only from ANCHORED-real)
- phoenix_v4/planning/story_planner.py (build_story_schedule ~line 665, atom
  load ~line 254 — confirm the exact story_atoms directory convention:
  `story_atoms/<persona>/anchored/<topic>/<engine>/<arc_position>/micro/v*.txt`)
- artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv (confirm no existing
  row for these tools before adding one — do not duplicate a row)
- scripts/ci/check_manga_wiring.py (read for style/pattern only — Lane 02 ports
  this, you do not need to touch it, but your matrix's field names must be
  something Lane 02 can gate against)

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm current SHA (do not trust the pack's recorded tip).
- confirm `atom_coverage_audit.py`'s topic-source fallback chain is unchanged
  since this pack's research (grep for `canonical_topics.yaml`,
  `catalog_generation_config.yaml`, and the atoms/ dir-scan fallback in the
  file); if someone already reconciled the 15-vs-57 discrepancy, STOP, report
  LANDED already, do not re-do it.
- confirm PR #9's `check_research_fit_honesty.py` / `check_book_story_authored.py`
  are on origin/main unmodified by any other in-flight PR.
- gh pr list --state open — confirm no other open PR is currently editing
  `scripts/inventory/atom_coverage_audit.py` or `config/source_of_truth/
  topic_registry.yaml`; if one is, STAND DOWN and report BLOCKED with that PR
  number.

PRE-REQUISITE CHECKS:
- `scripts/inventory/atom_coverage_audit.py` runs standalone and produces
  `artifacts/inventory/atom_coverage_matrix.json` without error.
- `config/source_of_truth/topic_registry.yaml` is readable and its topic count
  matches "15" as recorded — if it has drifted, use the live count, not 15.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA
- exact resolved topic list length from EACH source in
  `get_canonical_topics()`'s fallback chain (topic_registry.yaml /
  canonical_topics.yaml / catalog_generation_config.yaml / atoms/ dir scan) —
  confirm which one the tool is actually using today and why the count differs
  from 15
- exact count of (persona, topic) cells with a `story_atoms/<persona>/
  anchored/<topic>/` directory present, cross-checked against the "9 cells /
  6 personas" figure in this pack's INDEX — report the live number, it may
  have changed since 2026-07-22
- confirm no other in-flight workstream is mid-edit on these files

PROVENANCE:
- research: docs/PROGRAM_STATE.md "Atom coverage (en_US)" section (2026-07-22
  measurement); docs/agent_prompt_packs/20260721_bestseller_atom_flow/INDEX.md
  ground-truth section
- documents: CLAUDE.md Bestseller Quality Anti-Drift Doctrine (acceptance-layer
  naming discipline — port the same discipline to atom coverage claims);
  CLAUDE.md Manga Vision-Conformance Doctrine (six-layer taxonomy pattern this
  matrix's 3 states are a book-side instance of)
- builds_on: scripts/inventory/atom_coverage_audit.py (EXTENDS, do not fork),
  config/source_of_truth/topic_registry.yaml, check_research_fit_honesty.py /
  check_book_story_authored.py (PR #9, consumed as a signal source)
- inventory: EXTENDS (new classification states added to existing tool's
  output), never REDUCED — the existing binary CANONICAL-presence count must
  remain in the output for backward compatibility with any consumer of the
  current `atom_coverage_matrix.json` schema; add fields, do not remove them

MISSION:
Turn "100% CANONICAL presence on 15 topics" from a proxy into an honest,
3-state, full-topic-list matrix.

1. Reconcile the topic-list discrepancy. Determine which list is authoritative
   for "what topics does the catalog actually need coverage for" — likely
   `topic_registry.yaml` needs to be expanded/reconciled against whatever the
   57-topic fallback source contains (or vice versa: if the 57-topic list
   contains topics that are not actually catalog-planned, document that and
   narrow it explicitly with a named reason, never silently). Whichever way it
   resolves, write down the reconciliation decision in the tool's own
   docstring/comments and in this lane's handoff — this must never again be an
   implicit, undocumented discrepancy.
2. Extend `atom_coverage_audit.py` (in place — do not create a parallel tool)
   to classify every (persona, topic) cell into exactly one of 3 states:
   - `MISSING` — no `atoms/<persona>/<topic>/` CANONICAL.txt anywhere.
   - `CANONICAL_ONLY` (maps to acceptance layer `structurally_clear_only`) —
     CANONICAL.txt exists but no `story_atoms/<persona>/anchored/<topic>/`
     directory with real (non-empty, non-stub) content — i.e. research_fit
     cannot bind for this cell. Use `check_book_story_authored.py`'s own
     stub/emptiness logic if it already has one; otherwise apply the same
     byte-floor style check already used elsewhere in this repo for stub
     detection (see `check_render_progress_bytes.py`'s bytes<50_000 pattern
     for the analogous manga class — do not invent a new heuristic from
     scratch, reuse the established convention).
   - `ANCHORED_REAL` (maps to acceptance layer `authored_candidate`) —
     `story_atoms/<persona>/anchored/<topic>/` exists with real content.
     This is NOT a claim of Layer 3 (system working) or Layer 4 (bestseller
     register) — those require a Pearl_Editor ONTGP sample read and an
     operator blind-10 respectively, and this tool must never claim them.
3. Emit the updated `artifacts/inventory/atom_coverage_matrix.json` and
   `.md` report with per-cell state, persona/topic totals per state, and the
   reconciled topic-list count front and center (no more bare "100%" without
   the denominator it was measured against printed alongside it).
4. Add registry rows to `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`
   for `atom_coverage_audit.py` and `config/source_of_truth/topic_registry.yaml`
   (edit_not_recreate=YES) since neither has one today — this is a genuine gap,
   not new-artifact creation, so no NEW-ARTIFACT-JUSTIFIED tag is needed.

DELIVERABLES:
- scripts/inventory/atom_coverage_audit.py (extended in place)
- config/source_of_truth/topic_registry.yaml (updated if reconciliation
  requires it, with a comment explaining the reconciliation)
- artifacts/inventory/atom_coverage_matrix.json + atom_coverage_report.md
  (regenerated with 3-state schema)
- artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv (2 new rows)
- tests/test_atom_coverage_audit_3state.py (new) proving each of the 3 states
  classifies correctly against a small fixture set (one MISSING cell, one
  CANONICAL_ONLY cell, one ANCHORED_REAL cell — use real repo cells for the
  latter two, e.g. a random uncovered cell and
  `millennial_women_professionals`×`anxiety`×`overwhelm`)
- one paragraph in docs/PROGRAM_STATE.md's "Atom coverage (en_US)" section
  updated to cite the new 3-state numbers (Lane 04 will do the full
  reconciliation later; this lane only needs to not leave a stale claim behind
  if it changes the underlying tool's output format)

SMALLEST SAFE BATCH:
- smoke: run the extended tool against ONE persona (e.g.
  millennial_women_professionals) and confirm all 3 states appear correctly
  across its topics
- pilot: run against the 6 personas known to have anchored banks, confirm the
  9 known ANCHORED_REAL cells are correctly identified and nothing else is
  miscategorized as ANCHORED_REAL
- scale: run the full audit across all personas/topics, generate the final
  matrix artifact, open PR

HANG PREVENTION:
- poll interval: 5 minutes
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED after three unchanged polls
- max window: 90 minutes

TESTS/PROOFS:
- `python3 scripts/inventory/atom_coverage_audit.py` (full run, confirm exit 0
  and matrix artifact regenerated)
- `pytest tests/test_atom_coverage_audit_3state.py`
- Proof root: `artifacts/inventory/atom_coverage_matrix.json` with visible
  3-state breakdown and the reconciled topic-list denominator.

DO NOT:
- do not pick the smaller topic-list number just because it makes the
  percentage look better — the reconciliation must be a documented, defensible
  decision, not a convenience
- do not claim ANCHORED_REAL implies Layer 3 or Layer 4 — cap this tool's
  claims at Layer 1/2 always
- do not fork a parallel coverage tool — extend atom_coverage_audit.py in place
- do not touch check_research_fit_honesty.py / check_book_story_authored.py
  (PR #9's files) — consume their logic/output, do not modify them in this lane
- no stale metrics — every number in this prompt is a 2026-07-22 or earlier
  snapshot; re-derive live before writing anything down as current

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- LANDED-OFFLINE: GitHub blocked at dispatch time — branch pushed, full diff in
  handoff, ready to open PR the moment access returns.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree; local branch; remote branch; scratch files; background jobs; held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/atom-matrix-true-topics_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Architect
- LANE: atom-matrix-true-topics
- STATUS=MERGED|LANDED-OFFLINE|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: atom-matrix-3state-schema=<full-sha>
- PROOF_ROOT:
- TESTS:
- RECONCILED_TOPIC_COUNT: (the number Lane 03/04 must use going forward)
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure (a matrix tool
  landing is not itself "100% coverage")
- CLEANUP:
- HANDOFF:
- NEXT_ACTION: (should point at Lane 02 and Lane 03 unblock, with the exact
  field names/schema they need to consume)
```

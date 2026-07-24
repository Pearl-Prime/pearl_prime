# Lane 02 — CI gate: new atom / metadata that reaches prose must register in the matrix

```text
EXECUTE. Do not stop at summary or plan. End only MERGED, LANDED-OFFLINE, or BLOCKED.

You are Pearl_Architect for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Architect
- LANE=ci-atom-registration-gate
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch/pr
- RESUME_SURFACE=docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/02_ci_atom_registration_gate.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md
- Lane 01's CLOSEOUT_RECEIPT / handoff at
  artifacts/coordination/handoffs/atom-matrix-true-topics_2026-07-23.md — you
  need its exact 3-state schema field names and reconciled topic-list source
  before writing this gate
- scripts/ci/check_manga_wiring.py IN FULL — this is the pattern you are
  porting. Read its docstring (the "unwired-config-as-working kill"
  rationale), its `CONSUMER_ROOTS` / consumer-detection logic, its
  `KNOWN_UNWIRED` allowlist mechanism, and its exit-code contract.
- scripts/run_production_readiness_gates.py (find where check_manga_wiring is
  wired, ~gates 21-23 region, and where check_research_fit_honesty /
  check_book_story_authored were wired by PR #9 — your gate slots in near
  those, numbered after the highest existing gate)
- CLAUDE.md "Manga Vision-Conformance Doctrine" §2 (the exact prose this gate
  generalizes: "unwired-config-as-working" — you are applying the same
  discipline to atoms/story_atoms/metadata fields instead of config/manga/*.yaml)

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm Lane 01 has actually landed (MERGED or
  LANDED-OFFLINE) — if not, STOP, this lane is blocked on Lane 01, do not guess
  its schema.
- confirm check_manga_wiring.py's pattern is unchanged since research.
- gh pr list --state open — confirm no other PR is mid-edit on
  scripts/run_production_readiness_gates.py; if one is, coordinate/serialize,
  do not silently conflict.

PRE-REQUISITE CHECKS:
- Lane 01's 3-state matrix schema is readable (artifacts/inventory/
  atom_coverage_matrix.json in its new format) and its field names are stable
  enough to gate against.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA
- Lane 01's exact schema fields (state names, cell-key format)
- current count of top-level dimensions this gate must cover: atom "types"
  (slot/engine dirs under atoms/), story_atoms bank additions, and any
  metadata field currently read by book_renderer/composer/register_gate that
  ends up in written prose — enumerate the actual current set from the code,
  do not assume a fixed list from this prompt

PROVENANCE:
- research: docs/agent_prompt_packs/20260723_atom_persona_topic_locale_governance/INDEX.md
- documents: CLAUDE.md Manga Vision-Conformance Doctrine §2
  ("unwired-config-as-working" — the class this gate generalizes)
- builds_on: scripts/ci/check_manga_wiring.py (the pattern, ported not copied
  verbatim — atoms have a different shape than config/manga/*.yaml, adapt the
  detection logic accordingly), Lane 01's 3-state matrix schema
- inventory: EXTENDS (new gate added to run_production_readiness_gates.py and
  Drift detectors), never REDUCED

MISSION:
Make it structurally impossible for a new atom-generating code path, a new
CANONICAL.txt family, or a new metadata field that ends up in written book
prose to go permanently ungoverned by the coverage matrix.

Write `scripts/ci/check_atom_registration.py`:
1. Detect "new dimensions" since the matrix was last regenerated: new
   top-level atom-type directories under `atoms/` (new slot/engine family
   beyond the existing PIVOT/TAKEAWAY/THREAD/PERMISSION/STORY slots and
   comparison/false_alarm/grief/overwhelm/shame/spiral/watcher engines listed
   in `report_translation_coverage.py`'s `ALL_ATOM_TYPES`), new
   `story_atoms/<persona>/anchored/` persona directories, and any new field
   read by `phoenix_v4/planning/story_planner.py`, `register_gate.py`, or
   `book_renderer` that flows into rendered book text.
2. For each new dimension found: it must EITHER already be reflected in Lane
   01's matrix output (i.e., the matrix was regenerated after this dimension
   was added — check a freshness/timestamp or hash marker), OR carry a
   `status: unwired` / `excluded_from_prose: <reason>` declaration at its own
   definition site, OR be listed in a `KNOWN_UNWIRED`-equivalent allowlist in
   this new gate file with a reason and the lane that will register it. A new
   dimension satisfying none of these fails the gate.
3. Wire into `scripts/run_production_readiness_gates.py` as a new numbered
   gate (follow the existing gate numbering convention, do not renumber
   existing gates) and into the "Drift detectors" required check in the
   relevant `.github/workflows/*.yml`.
4. Ship as ADVISORY (WARN, non-blocking) by default per the operator-tier rule
   below — draft the hard-block `--strict` variant in the same file as a
   documented, unused-by-default option.
5. Mutation-test it: add a deliberately unregistered fake atom-type directory
   in a scratch/test fixture, confirm the gate goes RED, remove it, confirm
   GREEN. Include this as an actual test, not a manual one-off check.

DELIVERABLES:
- scripts/ci/check_atom_registration.py (new)
- scripts/run_production_readiness_gates.py updated (new gate wired, advisory)
- .github/workflows/*.yml updated (gate added to Drift detectors required check)
- tests/test_check_atom_registration.py (new) including the mutation-test case
- one paragraph added to whatever doc governs CI gate conventions (follow
  wherever check_manga_wiring.py's own gate is documented, likely
  docs/GITHUB_GOVERNANCE.md or a CI-gates reference doc — grep for
  check_manga_wiring to find it) describing this new gate and its
  advisory/strict modes

SMALLEST SAFE BATCH:
- smoke: run check_atom_registration.py standalone against current
  origin/main state, confirm it reports 0 unregistered dimensions (or an
  accurate, explicable count if some exist) without crashing
- pilot: inject one deliberately fake unregistered dimension via a scratch
  fixture, confirm RED, revert, confirm GREEN (the mutation test)
- scale: wire into run_production_readiness_gates.py + CI workflow, open PR,
  confirm required-check status shows the new gate

HANG PREVENTION:
- poll interval: 5 minutes
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED after three unchanged polls
- max window: 90 minutes

TESTS/PROOFS:
- `python3 scripts/ci/check_atom_registration.py`
- `python3 scripts/run_production_readiness_gates.py`
- `pytest tests/test_check_atom_registration.py`
- Proof root: gate output log showing the mutation-test RED→GREEN cycle.

DO NOT:
- no gate weakening — this is a NEW gate, there is nothing to weaken, but do
  not make it silently pass on parse errors or missing files (fail loud, WARN
  is about severity not silence)
- do not make this a hard render/merge-block without surfacing the threshold
  decision to the operator first — ship advisory-only
- do not modify check_manga_wiring.py itself — port the pattern into a new
  file, the manga gate is out of scope for this lane
- no stale assumptions about the current dimension list — enumerate it live
  from the code at lane start, the "current set" named in this prompt is
  illustrative, not authoritative

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- LANDED-OFFLINE: GitHub blocked — branch pushed, full diff in handoff, ready
  to open PR the moment access returns.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree; local branch; remote branch; scratch files; background jobs; held artifacts.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/ci-atom-registration-gate_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Architect
- LANE: ci-atom-registration-gate
- STATUS=MERGED|LANDED-OFFLINE|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: atom-registration-gate-wired=<full-sha>
- PROOF_ROOT:
- TESTS: (include the mutation-test RED/GREEN evidence explicitly)
- ACCEPTANCE_LAYER_OF_THIS_LANE'S_OWN_CLAIM: infrastructure
- CLEANUP:
- HANDOFF:
- NEXT_ACTION: (should point at Lane 04, which will consume this gate's
  presence as part of the "are we 100%" report's own honesty check)
```

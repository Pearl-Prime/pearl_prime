# Pearl Prime Book Pipeline Audit — Bestseller Register + Cohesive Flow + Atom Utilization

EXECUTE. Do not summarize state, do not produce a plan-only response, do not stop
after any intermediate step (reading docs, running one gate, drafting a partial
table). The turn ends ONLY on the MERGED-or-BLOCKED signal defined in "Landing"
below, or one concrete BLOCKER with evidence. A status summary is not a
deliverable. If you find yourself about to say "here's my plan" or "I'll now
proceed to X" as a final message, that is a stall — keep going instead.

## Turn contract

- This is a READ/AUDIT lane (existing gates + scripts + goldens), not a rewrite of
  the composer or the atom pools. Do not "fix" what you find by re-tuning
  `enrichment_select.py`, `register_gate.py`, or the composer — CLAUDE.md's
  Bestseller Quality Anti-Drift Doctrine is explicit that re-tuning the composer for
  register is drift, not craft. Your job is to produce an honest, evidence-backed,
  layer-labeled audit report and land it. If you find a genuine, narrowly-scoped bug
  (e.g. a parser silently returning zero atoms, a gate that isn't wired into CI), you
  may fix that specific bug with a regression test — but the audit report is the
  primary deliverable, not a refactor.
- Poll any CI/gate run you kick off to resolution; never arm a background run and
  end the turn.

## PRE-REQUISITE CHECK (STOP + surface if unmet)

1. `git fetch origin && git branch --show-current` — confirm you can reach
   `origin/main`. If GitHub is unreachable (403/network), do not block — land as a
   pushed branch / offline artifact per `docs/GITHUB_OPERATIONS_FRAMEWORK.md` and say
   so in the closeout.
2. `gh pr list --state open --search "bestseller"` and `--search "atom cohesion"` and
   `--search "cohesive flow"` — if a live open PR already covers this exact audit,
   STAND DOWN, reconcile, and report the delta instead of duplicating.
3. Confirm these three scripts exist and run cleanly (they landed 2026-07-21 via the
   merged `agent/bestseller-atom-flow-20260721` lane — verify this claim, don't trust
   it blindly): `scripts/ci/check_research_fit_honesty.py`,
   `scripts/ci/check_book_story_authored.py`,
   `scripts/inventory/atom_coverage_audit.py`. If any is missing/broken, that is
   itself an audit finding, not a blocker to stop on — note it and keep going with
   the tools that do work.

## Stale-state reconciliation (re-verify every claim below against live origin/main)

- `docs/PROGRAM_STATE.md` says `LAST VERIFIED @ origin/main 8a0b09f9b0...` dated
  2026-07-15. A PR titled `feat(bestseller-atom-flow): research_fit honesty gate +
  acceptance-layer stamp + cell-aware driver + courage atoms` merged 2026-07-21 —
  **PROGRAM_STATE.md is at least one merge behind current `origin/main`.** Part of
  this audit's job is to refresh the relevant PROGRAM_STATE sections with what you
  actually verify, not to read the stale version as ground truth.
- Memory-derived claims below (re-derive live, do not copy numbers):
  - en_US bestseller-atom coverage was last measured ~97.7% via
    `atom_coverage_audit.py` — re-run it fresh.
  - `#5237` (atom-cohesion craft lane) and `#5206` (bestseller-conformance audit)
    were OPEN/dirty/red as of PROGRAM_STATE's 07-15 snapshot — `gh pr view 5237` /
    `gh pr view 5206` currently fail to resolve against this repo, meaning those PR
    numbers are stale, closed, or renumbered. Re-derive their current state via
    `gh pr list --search` on title keywords, don't cite the old numbers as live.
  - Story-atoms banks: only 6 personas (educators, first_responders,
    gen_z_professionals, healthcare_rns, millennial_women_professionals,
    working_parents) had `story_atoms/anchored/` banks as of 07-21, and only for a
    handful of topics — `courage` had zero banks anywhere until the 07-21 lane added
    some. Re-verify current coverage; it may have moved since.
  - Twelve-shape word-mass gap (19.3k vs 50k+ target) was diagnosed as an assembly-
    architecture gap, not a raw volume/atom-count problem — check whether this still
    holds under the current composer.

## READ FIRST (in order, before writing anything)

1. `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`
2. `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (the 4-layer taxonomy —
   `structurally clear` / `authored candidate` / `system working` / `bestseller
   register`)
3. `docs/PROGRAM_STATE.md` §Flagship book, §Production-Gate, §Books-first roadmap
4. `docs/agent_prompt_packs/20260721_bestseller_atom_flow/INDEX.md` (yesterday's
   directly-adjacent lane — do not re-derive its research, verify what landed)
5. `phoenix_v4/quality/register_gate.py`, `phoenix_v4/quality/chapter_flow_gate.py`,
   `phoenix_v4/quality/book_quality_gate.py`, `phoenix_v4/quality/acceptance_layer.py`,
   `phoenix_v4/quality/bestseller_craft_gate.py`
6. `scripts/inventory/atom_coverage_audit.py`,
   `scripts/ci/check_research_fit_honesty.py`, `scripts/ci/check_book_story_authored.py`
7. `docs/sessions/cohesion_chunk_prompts_20260630/` (thesis de-templating +
   adjacency-selector craft backlog — Q1/Q2 in PROGRAM_STATE's post-flip quality
   backlog table)
8. CLAUDE.md's Bestseller Quality Anti-Drift Doctrine (already in your context) —
   re-read rules 1–3 before writing any status claim.

## PROVENANCE

```
PROVENANCE:
  research:   docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md;
              artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md (methodology
              precedent — six-layer taxonomy, adversarially refuted — port the same
              rigor to books, don't reinvent a lighter one)
  documents:  docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md;
              docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md;
              docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
  builds_on:  register_gate.py (F1-F16 checks incl. F14 beat-line ceiling);
              chapter_flow_gate.py; book_quality_gate.py; acceptance_layer.py;
              atom_coverage_audit.py; check_research_fit_honesty.py;
              check_book_story_authored.py
  inventory:  UNCHANGED — this is a read/report lane. Any narrow bug fix you make
              (see Turn contract) must be inventory=EXTENDS (add a regression test),
              never REDUCED.
```

## MISSION

Produce ONE honest, evidence-backed audit report,
`artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`, covering three
axes against the CURRENT `origin/main` state (not memory, not the stale
PROGRAM_STATE snapshot):

### Axis 1 — Bestseller register
- Run the flagship parity gate (`scripts/ci/check_flagship_book_parity.py`) and
  confirm the golden (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt`) is still
  byte-identical — this is the one PROVEN-AT-BAR book in the program; it must not
  have drifted.
- Pick 2-3 *non-flagship* recently-rendered or freshly-rendered books/cells
  (production profile, four-piece chord: `--pipeline-mode spine --quality-profile
  production --exercise-journeys`) and run them through `register_gate.py` +
  `bestseller_craft_gate.py` + `acceptance_layer.py`. For each: report the F-code
  breakdown (which of F1-F16 PASS/WARN/FAIL, especially F14 beat-line ceiling),
  ONTGP Give/Hold/Pull if available, and — critically — label the result on the
  4-layer taxonomy. A `register_gate` PASS is AT MOST `structurally clear` — say so
  explicitly for every cell, never call gate-PASS "bestseller."
- Cross-check against `check_research_fit_honesty.py` and
  `check_book_story_authored.py` (yesterday's new gates): for each sampled cell, is
  `research_fit` real (story_atoms bank present + used) or silently skipped? A book
  can pass every prose gate and still have zero character through-line if its
  research_fit skipped — that is the exact drift the operator caught on seed 43001.

### Axis 2 — Cohesive flow
- This is the atom-cohesion / dwell-pacing lane (`docs/sessions/
  cohesion_chunk_prompts_20260630/`, the F14 beat-share metric, the parked adjacency
  selector). Determine the CURRENT live state of `#5237` (atom-cohesion craft lane)
  and any successor — re-derive via `gh pr list --search`, do not trust the
  "OPEN/RED/DIRTY" label from the 07-15 PROGRAM_STATE snapshot without checking.
  - What memory/PROGRAM_STATE call the "top remaining quality lever": the chapter-
    thesis bank keyed `intent → engine` only, so the same load-bearing thesis
    sentence repeats across ~128 (persona×topic) cells. Verify: is Q1 (thesis
    de-templating) still open, landed, or superseded? Sample a few cells and check
    for literal thesis-sentence repetition across topics sharing an engine.
  - Integration/dwell pacing: verify whether a dwell-beat gate exists and is wired,
    or whether books still "race no dwell" (per the operator's #1 craft concern per
    prior audits). Cite the gate file or its absence.
  - Report per sampled book: an F14 beat-share number (or equivalent cohesion
    metric) and a plain-language read of whether consecutive beats feel connected
    or list-like/templated. Quote 2-3 short (<15 words each, since this is your own
    generated content not copyrighted external material — no citation limit
    applies to internally authored atoms) representative lines if it clarifies the
    finding.

### Axis 3 — Atom utilization
- Run `scripts/inventory/atom_coverage_audit.py` fresh for en_US and report the
  actual current percentage — do not cite the memory's ~97.7% without re-running.
- Distinguish (per `docs/DOCS_INDEX.md` / prior drift lessons already in your
  context): **listing exists** vs **atom bank exists** vs **atom bank is WIRED into
  a render path** vs **atom bank is actually consumed by a real render**. A config
  file with atoms in it that no code path reads is not "utilized."
  - Check `story_atoms/<persona>/anchored/<topic>/<engine>/` coverage breadth (which
    personas × topics have real banks vs `[]` → `research_fit skipped`) — this
    was the exact gap yesterday's lane partially closed for `courage`; verify current
    breadth honestly, including any personas/topics still at zero.
  - Spot-check for the known dup-fill failure mode (variant-index fill instead of
    purpose fill, per prior drift finding) in at least one atom pool family (e.g.
    REFLECTION or STORY) — confirm it's still present, fixed, or you can't tell from
    available tooling.
  - Report a single honest utilization number with its scope stated (e.g. "97.x%
    slot-fill rate across en_US production cells, measured by
    atom_coverage_audit.py on `<date>`" — NOT "atoms are basically done").

### Cross-axis synthesis
- One short section: where do the three axes interact? (e.g. a book can be
  Axis-3 "atoms present" but Axis-1 "research_fit skipped" if the atoms aren't
  wired into that cell's engine key; Axis-2 cohesion failures often trace back to
  Axis-3 thin/repeated pools.) Name the SINGLE highest-leverage next fix — do not
  recommend re-tuning the composer (that's the doctrine's explicit anti-pattern);
  recommend either atom authoring, gate wiring, or the line-edit lane.

## OPEN OPERATOR QUESTIONS

None expected — this is a diagnostic read against existing gates/scripts, not a
scope or taste decision. If you discover a genuinely operator-tier call (e.g.
whether to promote `check_research_fit_honesty.py` from advisory to hard-block),
surface it as a `Q-AUDIT-<TAG>-01` with a recommended default in the report; do not
decide it yourself and do not block the audit on it.

## DO NOT

- Do not report any sampled book as "bestseller," "shippable," or "done" off a
  `register_gate` PASS alone — name the acceptance layer every time (CLAUDE.md rule).
- Do not re-tune `enrichment_select.py`, `register_gate.py` thresholds, or the
  composer to make a sample "look better" — that is the drift this doctrine exists
  to prevent. Report what you find, even if it's unflattering.
- Do not conflate "listing" (catalog metadata) with "EPUB" (a readable file) —
  glossary is in `docs/PROGRAM_STATE.md` line 8-14.
- Do not cite `#5237` / `#5206` by number without confirming they still resolve on
  this repo — they may be stale.
- Do not restitch old renders as "fresh proof" — render or gate-check live for any
  claim you make (per the fresh-assets-not-old-images-as-proof lesson).
- Do not park a background CI/gate run and end the turn without polling it to
  resolution.

## GOTCHAS

- `atom_coverage_audit.py` and the story_atoms bank checks can be slow on the full
  catalog — scope to en_US + the sampled cells first; note if a full sweep is out of
  budget for this turn and say what was NOT covered (no silent truncation).
- `gh pr view <old-number>` failing with "could not resolve" does not mean no work
  happened on that topic — search by title/branch keyword, not number.
- Worktree/disk discipline applies if you create any worktree: ≥20GB free,
  `GIT_LFS_SKIP_SMUDGE=1`, sparse cone, poison-protocol commit gate (§4 of
  `docs/agent_brief.txt`). Prefer working directly in the existing checkout for a
  read-only audit — you likely don't need a worktree at all.

## Landing (the landing contract — work is not done until it is IN the system)

End in exactly ONE of:
- **(a) MERGED** — PR opened with `artifacts/qa/pearl_prime_pipeline_audit_20260722/
  AUDIT_REPORT.md` (+ any PROGRAM_STATE.md refresh + any narrow bug-fix diff),
  required checks green, squash-merged. Emit signal:
  `pearl-prime-audit-20260722=<full-merge-SHA>`.
- **(b) BLOCKED** — one concrete blocker with evidence, work pushed to a remote
  branch (never left only-local/uncommitted). State the blocker and the branch name.

There is no third state — "audit written locally, will PR later" is not done.

### Cleanup ledger (required in the closeout)
- worktree removed (or state "none created")
- local branch deleted / remote branch deleted after merge (or HOLD + reason)
- scratch files removed or declared by path
- any background gate/audit run stopped or explicitly declared still running

## CLOSEOUT_RECEIPT (required, exact)

```
CLOSEOUT_RECEIPT
lane: pearl-prime-bestseller-cohesion-atom-audit-20260722
signal: pearl-prime-audit-20260722=<full-SHA-or-BLOCKED>
state: MERGED | BLOCKED
acceptance_layer_per_axis:
  bestseller_register: <layer label + 1-line evidence>
  cohesive_flow: <layer label + 1-line evidence>
  atom_utilization: <number + scope + 1-line evidence>
autonomous_decisions: <list, each with 1 alternative considered>
evidence_paths: <every gate/script output path cited>
program_state_refresh: <yes/no + which sections>
cleanup_ledger: <as above>
next_action: <specific enough for a cold-start agent to resume>
```

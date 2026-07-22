```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_QA (manga vision-conformance auditor) for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_QA
- LANE=manga_vision_reaudit_20260722
- EXECUTION_MODE=local_fallback
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local checkout
- PERSISTENCE_SURFACES=branch/PR/artifact
- RESUME_SURFACE=artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md (new)

READ FIRST:
- docs/PROGRAM_STATE.md (manga section — note it is stale relative to
  2026-07-22 commits; do not trust its manga numbers without re-verifying)
- artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md (the prior
  baseline — R1 30% / R2 45% / R3 25% / R4 8% / R5 34% / R6 40% / R7 5% /
  R8 35%, six-layer taxonomy, adversarially refuted)
- artifacts/qa/manga_vision_conformance_20260703.tsv
- docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md (the R1–R8 →
  100%-means table + M1–M7 milestones)
- CLAUDE.md "Manga Vision-Conformance Doctrine" section (six-layer taxonomy,
  the three CI-enforced drift classes, layered-assembly rule)
- docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md
  (documents a real prior drift incident: 3 of 4 claimed-done items were
  actually absent from disk on re-verification — your audit method must not
  repeat that failure mode)

LIVE STATE RECONCILIATION:
- `git fetch origin`; diff `git log --oneline main..origin/main` for any
  manga commits since this pack was authored.
- Re-run whatever byte-verification method produced the 2026-07-03 tsv (grep
  the audit doc's methodology section for its exact commands/scripts) against
  current `main` — do not hand-wave new percentages.
- Specifically re-verify against current disk, not narrative claims:
  - `scripts/manga/assemble_from_bank.py` — commit `aad5cf2152` (2026-07-22)
    claims genre-aware `--bubbles` via `bubble_render_v2` is now wired.
    Confirm by running `scripts/manga/tests/test_assemble_from_bank.py` and
    reading the actual diff, not the commit message alone.
  - Any manga render artifacts newer than 2026-07-03 under
    `artifacts/manga/` / `artifacts/qa/manga_*` — classify each by the
    six-layer taxonomy from bytes on disk (size, whether it's a real image
    vs INTERIM placeholder, provenance field), not from any closeout .md's
    self-report.
- Check `gh pr list` for any open manga PRs whose merge would move an R-axis
  before you finalize numbers.

PRE-REQUISITE CHECKS:
- none — this lane is dispatchable immediately per the roadmap's own M1
  framing ("Blocked on: nothing").

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- full list of manga-touching commits between 2026-07-03 and now (`git log
  --oneline --since=2026-07-03 -- '*manga*' 'phoenix_v4/manga/**'
  'scripts/manga/**' 'config/manga/**'`);
- for each, classify: did it move an R-axis, and by how much, with what
  proof;
- any open manga PR whose merge is imminent and should be reflected;
- proposed smallest safe batch (this is a research/verification lane, not a
  build lane — the "batch" is which axes you re-measure first).

PROVENANCE:
- research: artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md
  (methodology to reuse, not to copy numbers from)
- documents: CLAUDE.md manga doctrine, MANGA_100PCT_PRODUCTION_ROADMAP
- builds_on: the existing byte-verification method and six-layer taxonomy —
  do not invent a new scoring rubric
- inventory: this REPLACES the 2026-07-03 audit as current authority; it
  does not delete it (keep as superseded-provenance, same convention already
  used for prior superseded manga audits per PROGRAM_STATE)

MISSION:
Produce a byte-verified refresh of the R1–R8 manga vision-conformance
audit as of 2026-07-22, using the same six-layer taxonomy and adversarial
method as the 2026-07-03 baseline, incorporating everything that has
actually landed on `main` since (notably `aad5cf2152` bubble-render wiring;
check for anything else). Flag every axis where the number is unchanged
and every axis where it moved, with byte-level evidence for each move.

DELIVERABLES:
- `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md` — new audit,
  same R1–R8 structure, six-layer taxonomy, explicit diff vs the 07-03
  baseline per axis (what changed, what didn't, why).
- `artifacts/qa/manga_vision_conformance_20260722.tsv` — updated machine
  companion, same schema as the 07-03 tsv.
- Update `docs/PROGRAM_STATE.md` manga section to point at the new audit as
  current authority (mark 07-03 as superseded-provenance, same pattern as
  other superseded manga audits in that file).
- Update `docs/DOCS_INDEX.md` manga rows if the audit doc's path changed the
  authority pointer.

SMALLEST SAFE BATCH:
- smoke: re-verify ONE axis (R5, since assemble_from_bank moved) end-to-end
  first — confirm your verification method reproduces a number you can
  defend before running all 8.
- pilot: re-verify all 8 axes.
- scale: n/a — this is a single audit document, not a scaling operation.

HANG PREVENTION:
- poll interval: 10 minutes if any step shells out to a long-running
  script (e.g. re-running a full test suite)
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED or narrow scope after three unchanged polls
- max window: 3 hours

TESTS/PROOFS:
- `python3 -m pytest scripts/manga/tests/test_assemble_from_bank.py -q`
- Whatever byte-verification script(s) the 07-03 audit's methodology
  section names — run them, don't re-derive from scratch if they exist.
- proof roots: `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md`,
  `artifacts/qa/manga_vision_conformance_20260722.tsv`

DO NOT:
- no gate weakening;
- no stale metrics — every percentage must cite a specific file/byte-count
  or test result, not a prior document's claim;
- no fake proof;
- no local-only finish;
- no giant batch first;
- do not report any axis as "improved" without a byte-level artifact to
  point at (this exact failure mode — narrated success with no underlying
  write — is what produced the Wave-2 reimplementation spec).

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, pushed remote branch if useful, handoff
  written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/manga_vision_reaudit_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_QA
- LANE: manga_vision_reaudit_20260722
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL:
- PROOF_ROOT:
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```

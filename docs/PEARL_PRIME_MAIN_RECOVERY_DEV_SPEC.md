# Pearl Prime Main Recovery Dev Spec

**Purpose:** Move the missing Pearl Prime runtime truth from branch/spec drift into clean, reviewable GitHub PRs against `origin/main`, without replaying autobackup noise or widening into unrelated content work.

**Status:** Execution spec for Pearl_Dev / Pearl_GitHub recovery work.

**Authority:**

- [docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md](./PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md)
- [docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md](./PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md)
- [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)
- [docs/PEARL_PRIME_RELEASE_CONTRACT.md](./PEARL_PRIME_RELEASE_CONTRACT.md)
- [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md)
- [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md)

---

## 1. Prompt vs Spec

A prompt is not a spec.

A prompt tells an agent how to start or how to behave in a chat.

A dev spec tells the implementer:

- exactly what problem is being solved
- what files are in scope
- what files are out of scope
- what order to implement in
- what acceptance criteria must pass
- what stop conditions require escalation instead of improvisation

This file is the dev spec.

---

## 2. Problem Statement

Pearl Prime has meaningful runtime and quality hardening work on `codex/state-convergence-20260328`, but that work is not on `origin/main`.

The missing production delta includes:

1. explicit-topic preservation instead of silent topic collapse
2. location as a first-class runtime contract
3. page-one location grounding enforcement
4. a stronger chapter composer / flow-gate / bestseller-editor runtime
5. governing tests for the above behavior

The missing work is real, but it is mixed into a convergence branch with autobackup commits. The recovery job is to transplant the correct runtime truth to `origin/main` in clean PRs, not to merge backup history wholesale.

---

## 3. Source Branch and Boundaries

### Source branch

- `codex/state-convergence-20260328`

### Canonical merge target

- `origin/main`

### Core rule

Do **not** blindly cherry-pick autobackup commits.

Instead:

- create clean branches from `origin/main`
- transplant the intended file states
- run tests on each PR slice
- keep PRs narrow enough to review

### Out of scope for this spec

- writing new atom banks from scratch
- fixing all teacher coverage gaps
- redesigning the planner architecture beyond the identified runtime delta
- manga, Pearl News, brand-admin, or GitHub-governance work
- broad persona redesign beyond what is required to avoid false runtime claims

---

## 4. Recovery Goal

After this spec is complete, `origin/main` must contain the missing Pearl Prime runtime truth for:

- explicit supported topic integrity
- location-aware runtime honesty
- page-one location grounding gates
- bestseller composition/runtime hardening
- tests that prove those behaviors

It is acceptable if `origin/main` still fails some requests because source banks are hollow. It is **not** acceptable for `origin/main` to silently drift or pretend success.

In short:

- honest runtime on main: required
- complete content coverage on main: not required by this spec

---

## 5. Implementation Strategy

Implement this as **three PRs** plus one follow-up lane.

### PR 1 — Runtime Identity + Location Truth

**Goal:** Make Pearl Prime honest about topic and location.

#### Files in scope

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/planning/catalog_planner.py](../phoenix_v4/planning/catalog_planner.py) — location/profile wiring in planning (included in the proven PR #67 runtime-truth slice; keep aligned with harvest `pearl_prime_pr1`).
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [config/localization/render_location_profiles.yaml](../config/localization/render_location_profiles.yaml)
- [tests/test_book_renderer.py](../tests/test_book_renderer.py)
- [tests/test_book_renderer_location_fallbacks.py](../tests/test_book_renderer_location_fallbacks.py)
- [tests/test_topic_identity_resolution.py](../tests/test_topic_identity_resolution.py)

#### Required behavior

1. Explicit supported topics such as `overthinking` must not silently collapse to broader aliases when a matching governed path exists.
2. If the explicit topic path is preserved but the dedicated source bank is hollow, the CLI must fail before compile with a clear reason.
3. `--location` must be accepted as a first-class CLI input.
4. Location must survive into plan/output metadata.
5. If a run has location, the rendered opening must realize that location with governed profile signals or fail.
6. The renderer must emit `location_grounding_report.json` for location-bearing runs.

#### Acceptance criteria

- the explicit-topic preservation tests pass
- the location-report tests pass
- a real `overthinking + location` CLI run fails honestly on hollow source coverage instead of drifting to `anxiety`
- a render with location but weak opening grounding raises the location-grounding error instead of silently shipping

#### Verification commands

```bash
PYTHONPATH=. python3 -m pytest \
  tests/test_topic_identity_resolution.py \
  tests/test_book_renderer_location_fallbacks.py \
  tests/test_book_renderer.py \
  tests/test_location_passthrough.py -q
```

### PR 2 — Bestseller Composition + Editorial Runtime

**Goal:** Put the stronger composition/editor flow on `main`.

#### Merge base (required)

PR 1 and PR 2 both touch [`phoenix_v4/rendering/book_renderer.py`](../phoenix_v4/rendering/book_renderer.py). **Do not** open PR 2 as a **standalone** PR from `origin/main` while PR 1 is still outstanding (or while `main` lacks PR 1’s `book_renderer` + location/topic runtime), or you will duplicate or conflict the same seam.

**Base your branch on `agent/pearl-prime-runtime-truth`, not `origin/main`, unless PR 1 has already merged.**

- **Preferred:** branch PR 2 from **`agent/pearl-prime-runtime-truth`** (PR 1 head) or any branch that already contains the merged PR 1 slice, then open PR 2 targeting that base (or rebase onto `main` after PR 1 lands).
- **Alternate:** wait until PR 1 merges to `main`, then branch PR 2 from **updated** `origin/main`.

#### Files in scope

- [phoenix_v4/rendering/chapter_composer.py](../phoenix_v4/rendering/chapter_composer.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py) — active runtime: `compose_chapter_prose` in `TxtWriter`, flow gate on composed chapter text
- [phoenix_v4/quality/chapter_flow_gate.py](../phoenix_v4/quality/chapter_flow_gate.py)
- [phoenix_v4/qa/bestseller_editor.py](../phoenix_v4/qa/bestseller_editor.py)
- [phoenix_v4/planning/slot_resolver.py](../phoenix_v4/planning/slot_resolver.py)
- [phoenix_v4/planning/assembly_compiler.py](../phoenix_v4/planning/assembly_compiler.py) — wires arc `chapter_thesis` into `ResolverContext` so thesis-aware slot ranking is live in Stage 3
- [tests/test_chapter_composer.py](../tests/test_chapter_composer.py)
- [tests/test_chapter_flow_gate.py](../tests/test_chapter_flow_gate.py)

#### Required behavior

1. The new chapter composer is the active runtime path for cohesive chapter composition.
2. The flow gate evaluates composed/cleaned chapter output, not just raw slot fragments.
3. Thesis-aware atom ranking is active in slot resolution.
4. The bestseller-editor logic exists on main as runtime quality tooling, not only as a lost side artifact.

#### Acceptance criteria

- composer tests pass
- chapter-flow tests pass
- no regression in render path imports or runtime wiring
- a proof chapter generated through the current composer path is measurably cleaner than the raw-slot baseline

#### Verification commands

PR 2 scoped tests plus render-path regression for `book_renderer.py` (shared with PR 1; run after PR 1 base is present):

```bash
PYTHONPATH=. python3 -m pytest \
  tests/test_chapter_composer.py \
  tests/test_chapter_flow_gate.py \
  tests/test_book_renderer.py -q
```

### PR 3 — Governing Pearl Prime Docs

**Goal:** Put the missing Pearl Prime recovery docs on `main` alongside the runtime they describe.

#### Files in scope

- [docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md](./PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md)
- [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)
- [docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md](./PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md)
- [docs/DOCS_INDEX.md](./DOCS_INDEX.md)

#### Required behavior

1. Docs on `main` must describe the runtime that is actually merged.
2. `DOCS_INDEX.md` must link all three Pearl Prime recovery docs.
3. Docs must not claim content readiness that the source banks do not actually have.

#### Acceptance criteria

- docs governance passes
- the docs describe:
  - explicit-topic preservation
  - location grounding contract
  - bestseller composition/runtime recovery
  - remaining source-bank debt

#### Verification commands

```bash
PYTHONPATH=. python3 scripts/ci/check_docs_governance.py
```

### Follow-up Lane — Source/Bank Repair

This is **not** part of the three recovery PRs.

It should be tracked as a separate implementation lane after the runtime truth is on `main`.

#### Problems in this follow-up lane

- hollow [atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt](../atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt)
- tech-coded or over-narrow atoms that misrepresent broader personas
- incomplete teacher slot-family coverage
- too-small governed location profile universe

#### Why it is separate

The recovery PRs should make the system honest.
The follow-up lane should make the system fuller.

Do not mix those two jobs in the same recovery PRs.

---

## 6. Required PR Order

Use this order:

1. PR 1 — runtime identity + location truth
2. PR 2 — bestseller composition + editorial runtime
3. PR 3 — docs alignment
4. Follow-up implementation lane — source/bank repair

Why this order:

- PR 1 makes the runtime truthful
- PR 2 improves the active composition/runtime path on top of that truth
- PR 3 documents what actually landed
- source repair comes after runtime honesty exposes the true remaining gaps

---

## 7. Stop Conditions

Stop and escalate instead of improvising if any of these happen:

1. The convergence branch code depends on unrelated local-only files not listed in this spec.
2. Transplanting PR 1 requires planner/schema changes beyond preserving location/topic metadata and runtime checks.
3. PR 2 requires atom-bank rewrites to pass its own unit tests.
4. The file states on `codex/state-convergence-20260328` and current local working tree differ materially for the same target files.
5. `origin/main` has moved in a way that already overlaps part of this recovery scope.

If any stop condition is hit, write a short deviation note into the workstream and narrow the PR rather than widening it.

---

## 8. Git / Branching Rules

Pearl_GitHub owns final branch/commit/push/PR operations.

**PR 1**

1. start from `origin/main`
2. transplant only the files listed in that PR’s scope
3. run the verification commands for that PR
4. run push-guard and preflight
5. open a narrow PR with the exact scope label

**PR 2**

1. start from **`agent/pearl-prime-runtime-truth`** (preferred) or **updated `origin/main`** after PR 1 merges — **not** a fresh standalone branch from `origin/main` while PR 1 and PR 2 would both rewrite `book_renderer.py` independently
2. transplant only the files listed in PR 2 scope (§5)
3. run PR 2 verification commands (§5)
4. run push-guard and preflight
5. open a narrow PR with the exact scope label (base = PR 1 branch until PR 1 lands, then rebase/retarget to `main` as appropriate)

**PR 3**

1. start from `origin/main` after PR 2 is merged (or stack on the PR 2 head if docs-only delta is cleaner — prefer linear history when possible)
2. transplant only the files listed in PR 3 scope
3. run verification for that PR
4. run push-guard and preflight
5. open a narrow PR with the exact scope label

Recommended branch names:

- `agent/pearl-prime-runtime-truth` (PR 1)
- `agent/pearl-prime-bestseller-runtime` (PR 2; branch **from** PR 1 head or post-merge `main`)
- `agent/pearl-prime-recovery-docs` (PR 3)

---

## 9. Closeout Requirements

At the end of each PR lane, the dev closeout must include:

- changed paths
- tests run
- whether runtime behavior changed or only docs/tests changed
- remaining known gaps
- whether the next PR in sequence is unblocked

At the end of the full recovery sequence, the final closeout must answer:

1. Is explicit-topic drift fixed on `main`?
2. Is location now a first-class runtime contract on `main`?
3. Is page-one location grounding enforced on `main`?
4. Is the stronger composer/editor runtime on `main`?
5. What still fails because of source-bank debt rather than runtime drift?

---

## 10. Definition Of Done

This dev spec is complete when:

- PR 1, PR 2, and PR 3 are merged to `main`
- the recovery docs are on `main`
- `origin/main` no longer silently drifts explicit topics or location-bearing titles
- remaining failures are content/readiness failures that are surfaced honestly

This dev spec is **not** complete merely because the convergence branch contains the code.

The work is only done when the missing Pearl Prime runtime truth is on `main` in clean, reviewable PRs.

# Pearl Prime Salvage Audit 2026-03-29

**Purpose:** Answer the concrete recovery question for Pearl Prime: what prior architecture exists only in `old_chat_specs/`, what real implementation exists only on unmerged branches, what is already on `origin/main`, and what exact PR plan should move the missing runtime truth onto GitHub main without replaying backup-noise drift.

**Status:** Recovery audit only. This file is not a replacement for the canonical runtime/spec docs. It is the branch/spec reconciliation map for Pearl Prime salvage.

## Current `origin/main` status (post-recovery PRs)

**As of 2026-03-30,** Pearl Prime recovery **PR #67** (runtime identity + location truth), **PR #74** (bestseller composition + editorial runtime), and **PR #75** (governing recovery docs + selective `DOCS_INDEX` links) are merged to `origin/main` (tip `37e55387`). The **14-file Pearl Prime runtime delta** that was previously carried on `codex/state-convergence-20260328` is **on `main`** for the code paths merged in PR #67 and PR #74 (see `book_renderer`, `chapter_composer`, `bestseller_editor`, `run_pipeline`, tests, and location profiles).

The **Repo Snapshot** below and **§B — Exists on unmerged branches only** describe the **2026-03-29 audit moment** and are **retained for traceability**; they are not a live description of merge state after those PRs.

**Still open:** Source/bank repair and content-readiness work (**§PR 4** / follow-up lane in [PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md](./PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md)) remains; recovery PRs surface gaps honestly rather than hiding them.

## Questions Answered

1. Did earlier work already describe persona + topic + location tied to lived experience?
2. Does unmerged code already exist for some of the missing Pearl Prime runtime behavior?
3. What Pearl Prime capabilities are already on `origin/main`?
4. What should be PR'd next, in what order, and from which source branch?

## Repo Snapshot

- **Canonical remote main at audit time:** `origin/main` = `d1072f0fb9adc425bc557f25769b0558dfeec5d2`
- **Primary unmerged Pearl Prime source branch:** `codex/state-convergence-20260328`
- **Ahead/behind vs `origin/main`:** `0 30` (`codex/state-convergence-20260328` is 30 commits ahead)
- **Important finding:** the missing Pearl Prime runtime delta is real, but it is not a clean single-feature branch. The relevant implementation is mixed into a convergence branch with many autobackup commits.

## A. Exists In `old_chat_specs/` Only

These items are evidence that the architecture thinking already existed, but did not become the fully merged canonical implementation.

### 1. Aha + Integration As Explicit Section Contracts

- [old_chat_specs/last chat recap.txt](../old_chat_specs/last%20chat%20recap.txt)
- Contains the explicit sequence:
  - `intro -> guided_practice -> aha_noticing -> integration`
- Contains validator-style rules such as:
  - `aha_noticing missing required callout prefix`
  - `aha_noticing must contain 'notice' or 'might notice'`
- This is stronger than the current baseline runtime because it treats aha/integration as an authored section contract, not just a prose quality aspiration.

### 2. Teacher Stories + Persona/Location Wrappers

- [old_chat_specs/phoenix omega v4 analysis.txt](../old_chat_specs/phoenix%20omega%20v4%20analysis.txt)
- Explicitly states:
  - `Ensure teacher coverage complete`
  - `Pre-make teacher stories`
  - then apply `persona + location wrappers and overlays at assembly`
- This is important because it matches the current failure mode: teacher coverage and persona/location realization were already recognized as separate layers that both had to be complete.

### 3. Section-First, Location-Aware V4 Architecture

- [old_chat_specs/last chats recap.txt](../old_chat_specs/last%20chats%20recap.txt)
- Describes a fuller section-first architecture including:
  - `location_hydrator_v4.py`
  - `scene_loader_v4.py`
  - `location_policy.yaml`
  - section fields such as `location_aware: true`
  - scenes bound to `persona + topic + location_class`
- This is materially deeper than the currently merged baseline, where location was historically closer to render metadata/fallback than a fully modeled planning/source axis.

### Recovery Meaning

`old_chat_specs/` does not just contain vague brainstorming. It contains prior architecture for:

- location-aware scenes
- teacher coverage completeness
- aha/integration section contracts
- persona/topic/location coupling at assembly time

But those ideas mostly remained transcript/spec material rather than becoming one merged runtime path.

## B. Exists On Unmerged Branches Only

### Primary Branch With Missing Runtime Truth

- `codex/state-convergence-20260328`

This is the main source of missing Pearl Prime runtime work. Against `origin/main`, the Pearl Prime delta is a **14-file set**:

- [config/localization/render_location_profiles.yaml](../config/localization/render_location_profiles.yaml)
- [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)
- [docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md](./PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md)
- [phoenix_v4/planning/slot_resolver.py](../phoenix_v4/planning/slot_resolver.py)
- [phoenix_v4/qa/bestseller_editor.py](../phoenix_v4/qa/bestseller_editor.py)
- [phoenix_v4/quality/chapter_flow_gate.py](../phoenix_v4/quality/chapter_flow_gate.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [phoenix_v4/rendering/chapter_composer.py](../phoenix_v4/rendering/chapter_composer.py)
- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [tests/test_book_renderer.py](../tests/test_book_renderer.py)
- [tests/test_book_renderer_location_fallbacks.py](../tests/test_book_renderer_location_fallbacks.py)
- [tests/test_chapter_composer.py](../tests/test_chapter_composer.py)
- [tests/test_chapter_flow_gate.py](../tests/test_chapter_flow_gate.py)
- [tests/test_topic_identity_resolution.py](../tests/test_topic_identity_resolution.py)

**Diff size:** `2692 insertions, 48 deletions`

### Named Commits Carrying Real Pearl Prime Work

These two named commits are signal, not just backup noise:

- `742c16a9` `feat(slot-resolver): add thesis-aware atom ranking for bestseller composition`
- `370a93fe` `feat(v32): recreate lost Writers Bible v3.2 configs, deliverables, and bestseller_editor`

Later autobackup commits on the convergence branch also carry real work, including:

- first-class `location` passthrough in plan generation and CLI
- universal location grounding gate in render
- explicit-topic preservation and fail-fast topic source readiness in CLI
- chapter composer / flow-gate hardening
- bestseller overlay integration

### What This Unmerged Runtime Delta Actually Adds

1. **Location as a real runtime contract**
   - location profiles file exists
   - `run_pipeline.py` and planning persist requested/resolved location
   - renderer enforces page-one location realization and writes `location_grounding_report.json`

2. **No silent topic drift for explicit supported topics**
   - explicit topics such as `overthinking` are preserved when dedicated support exists
   - compile fails honestly if the dedicated topic bank is hollow, instead of collapsing to a broader alias like `anxiety`

3. **Composer/editor hardening for bestseller-ness**
   - new `chapter_composer.py`
   - stronger `chapter_flow_gate.py`
   - new `bestseller_editor.py`
   - thesis-aware slot ranking in `slot_resolver.py`

4. **Governed tests for the new runtime behavior**
   - location report tests
   - chapter composer / flow tests
   - topic identity preservation tests

### Other Relevant Unmerged Branches

- `origin/agent/bestseller-100-signoff-clean`

This branch is relevant, but only for signoff evidence. The key commit:

- `239d272309ba73b80cc4838f31ac42a34b60f563`

adds:

- [artifacts/governance/bestseller_100_signoff_2026-03-26.md](../artifacts/governance/bestseller_100_signoff_2026-03-26.md)

It does **not** contain the missing runtime/location/topic architecture.

## C. Already On `origin/main`

These Pearl Prime pieces are already merged and should be treated as existing production baseline, not as missing salvage.

### Canonical Docs Already On Main

- [docs/BESTSELLER_STRUCTURES.md](./BESTSELLER_STRUCTURES.md)
- [docs/CHAPTER_THESIS_BANK.md](./CHAPTER_THESIS_BANK.md)
- [docs/TEACHER_PRODUCTION_READINESS.md](./TEACHER_PRODUCTION_READINESS.md)
- [docs/PEARL_PRIME_RELEASE_CONTRACT.md](./PEARL_PRIME_RELEASE_CONTRACT.md)
- [docs/PEARL_PRIME_100_PERCENT_DEV_PLAN.md](./PEARL_PRIME_100_PERCENT_DEV_PLAN.md)

### Baseline Runtime Already On Main

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [phoenix_v4/planning/slot_resolver.py](../phoenix_v4/planning/slot_resolver.py)
- [phoenix_v4/quality/chapter_flow_gate.py](../phoenix_v4/quality/chapter_flow_gate.py)
- [tests/test_book_renderer.py](../tests/test_book_renderer.py)
- [tests/test_chapter_flow_gate.py](../tests/test_chapter_flow_gate.py)

### Release Evidence Already On Main

- `origin/main` commit `d1072f0fb9adc425bc557f25769b0558dfeec5d2`
- Adds bestseller signoff evidence to main

### Important Boundary

What is already on `origin/main` proves that Pearl Prime has:

- strong docs/specs
- bestseller structure thinking
- baseline runtime path
- release/signoff evidence

It does **not** prove that `origin/main` already has:

- first-class persona/topic/location runtime truth
- no-silent-drift topic identity
- universal page-one location realization gating
- the new bestseller composer/editor layer

## D. What Is Still Missing Even After Salvage

These are not “branch merge only” problems. They are content/readiness debts that still need real implementation work.

### 1. Hollow Source Banks

- [atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt](../atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt)

This is the clearest live example. The runtime now fails honestly when this bank is hollow, but the content debt itself still exists.

### 2. Teacher Slot-Family Coverage Is Not Production-Complete

Current approved teacher-bank slot inventory is mostly:

- `STORY`
- `EXERCISE`

Only `ahjan` currently adds:

- `QUOTE`
- `TEACHING`

No teacher currently has approved bank coverage for:

- `HOOK`
- `SCENE`
- `REFLECTION`
- `COMPRESSION`
- `INTEGRATION`

That means teacher mode is still not 100% compile-ready across teachers for long-form format expectations.

### 3. Persona Layer Still Over-Collapses

`gen_z_professionals` is still doing too much work as a catch-all Gen Z stand-in. This is a modeling gap, not just a rendering issue.

### 4. Location Universe Is Still Tiny

Governed render-location profiles currently number `2`. The runtime contract is stronger now, but the location catalog itself is still narrow.

### 5. Random Catalog Samples Can Miss Structural Failures

The 1000-book planner sample can look green while still missing red cells. Example:

- full active arc-universe scan shows `3` failing tuples for explicit-topic source readiness
- all three are `gen_z_professionals × overthinking × {false_alarm, spiral, watcher}`

So production readiness must use exhaustive readiness matrices, not just successful batches.

## E. Exact PR Plan

**Do not blindly cherry-pick autobackup commits.** The convergence branch has real value, but the history is noisy. The safe move is to transplant the relevant file sets onto clean branches from `origin/main`.

### PR 1 — Runtime Identity + Location Truth

**Goal:** Make the runtime honest about explicit topic and location.

Files:

- [scripts/run_pipeline.py](../scripts/run_pipeline.py)
- [phoenix_v4/rendering/book_renderer.py](../phoenix_v4/rendering/book_renderer.py)
- [config/localization/render_location_profiles.yaml](../config/localization/render_location_profiles.yaml)
- [tests/test_book_renderer.py](../tests/test_book_renderer.py)
- [tests/test_book_renderer_location_fallbacks.py](../tests/test_book_renderer_location_fallbacks.py)
- [tests/test_topic_identity_resolution.py](../tests/test_topic_identity_resolution.py)

Accept when:

- explicit supported topics no longer silently collapse
- hollow dedicated topic banks fail before compile
- any run with location must ground page one or fail

### PR 2 — Bestseller Composition + Editorial Runtime

**Goal:** Restore the stronger writing/composition runtime that was missing from main.

Files:

- [phoenix_v4/rendering/chapter_composer.py](../phoenix_v4/rendering/chapter_composer.py)
- [phoenix_v4/quality/chapter_flow_gate.py](../phoenix_v4/quality/chapter_flow_gate.py)
- [phoenix_v4/qa/bestseller_editor.py](../phoenix_v4/qa/bestseller_editor.py)
- [phoenix_v4/planning/slot_resolver.py](../phoenix_v4/planning/slot_resolver.py)
- [tests/test_chapter_composer.py](../tests/test_chapter_composer.py)
- [tests/test_chapter_flow_gate.py](../tests/test_chapter_flow_gate.py)

Accept when:

- composed chapters use the new bestseller overlay path
- flow gates evaluate cleaned/composed prose
- thesis-aware slot ranking is live

### PR 3 — Pearl Prime Truth Docs

**Goal:** Put the governing recovery docs on main with the code they describe.

Files:

- [docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md](./PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md)
- [docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)

Accept when:

- docs match the merged runtime
- `DOCS_INDEX.md` references the docs cleanly

### PR 4 — Source/Bank Repair (New Work, Not Simple Cherry-Pick)

**Goal:** Fix the content debts the new runtime truth exposes.

Required work:

- repair hollow overthinking source banks
- replace overly tech-coded `gen_z_professionals` atoms
- expand teacher-bank slot-family coverage
- add more governed location profiles only when real source grounding exists

This PR is not a pure salvage PR. It is a new production-readiness implementation lane.

## Recommended Ownership

- **Pearl_Dev:** PR 1 and PR 2 implementation/transplant
- **Pearl_Writer / Pearl_Editor:** PR 4 source-bank and prose quality repairs
- **Pearl_PM:** track these as separate workstreams so salvage does not get mixed with manga/repo-health lanes
- **Pearl_Architect:** verify subsystem routing and prevent this from drifting back into generic fallback behavior

## Bottom Line

Yes, the missing Pearl Prime behavior was already anticipated before.

- Some of it exists only in `old_chat_specs/`
- some of it exists only on the unmerged convergence branch
- some of the broader bestseller/teacher docs are already on `origin/main`

But there is **not** one magical hidden branch that already merges all of it cleanly.

The real missing production delta is the 14-file Pearl Prime runtime set on `codex/state-convergence-20260328`, plus a separate source-readiness/content-repair lane that no branch already solves for us.

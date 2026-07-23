# Lane B — Pearl_Editor / Content-Authority Sequencing Audit

**Date:** 2026-07-23
**Agent:** Pearl_PM (Lane B, Pearl Prime Catalog Plan + Assembly Readiness Audit — acting as audit lane, not a live Pearl_Editor content-authoring session)
**Scope:** Read-only doc + code archaeology. No atom, teacher_bank, story_atoms, or `PEARL_ARCHITECT_STATE.md` file was edited.

## Operator's question (verbatim intent)

"Is the Pearl_Editor agent getting in the process at the right point — are we
creating the contract of what a book is supposed to do, and seeing that contract
through, before it's even okayed for the catalog?"

## One-line answer

**No.** Content-authority does not get "created and seen through" before catalog
okay. It is consumed **only at render time, as a best-effort lookup that fails
soft (silent skip) when absent.** No mechanism checks story_atoms/teacher_banks
presence before a `(persona, topic, engine)` cell enters
`config/source_of_truth/book_plans_en_us/`. The gate that does check binding runs
after render, in CI, advisory-only.

## Note on agent identity

There is no `.claude/agents/*editor*.md` file — "Pearl_Editor" is a
routing/role label from `SUBSYSTEM_AUTHORITY_MAP.tsv`, the same pattern as
Pearl_Prime, Pearl_PM, Pearl_Architect (none of those are literal subagent files
either). This lane audits the cap-entry authority chain, not a literal running
agent — that absence is expected repo architecture, not a finding.

## 1. What PEARL-EDITOR-UPSTREAM-01 actually says

`docs/PEARL_ARCHITECT_STATE.md:668-694`. Load-bearing quote:

> "Pearl_Editor is the content-authority node; Pearl_Prime's render pipeline is
> the consumption node. **'Upstream' reframes correctly as authority precedes
> render.** **Pearl_Editor is NOT inserted as a runtime pipeline step**... the
> existing **read-overlay mechanism** in `registry_resolver.py:415-462` is the
> integration point and stays unchanged." (:682)

And (:671): *"The 'upstream' framing is correct as **authority-flow**... but
**not as pipeline-stage**."* This directly answers discovery Q1: the cap
**declines** to answer the operator's stage question and answers only an
ownership question. "Authority precedes render consumption" only requires
content exist on disk by the time *some* render reads it — it says nothing about
catalog admission. The cap even flags this as deferred, not resolved (:687):
*"defer the formal decision until catalog 800 data-artifact... reveals
scale-of-authoring-needed pressure"* — still open, no follow-up cap closes it.

## 2. Code trace

**2.1 Catalog admission gates on `master_arcs/`, not content-authority.**
`scripts/catalog/gen_plan_skeletons.py` (the generator that writes
`book_plans_en_us/*.yaml`) filters admissible cells via
`ARCS = ROOT / "config/source_of_truth/master_arcs"` /
`for p in sorted(ARCS.glob("*.yaml"))` (lines 26, 56). A grep for
`story_atoms|teacher_bank|research_fit|CANONICAL` in this 160-line file returns
**zero hits**. A cell can be arc-backed (admitted) with zero story_atoms/
teacher_banks coverage.

**2.2 Content-authority consumption fails soft.**
`phoenix_v4/planning/story_planner.py::build_story_schedule()` (lines 697-705):

```python
all_atoms = _load_all_atoms(persona_id, topic, repo_root, locale=locale)
if not all_atoms:
    skip = f"no_story_atoms: story_atoms/{persona_id}/anchored/{topic}/"
    return StorySchedule(research_fit={"mode": "skipped", "skip_reason": skip})
```

Absence doesn't raise or halt anything — it produces a payload labeled after the
fact. Its one production call site is
`phoenix_v4/planning/enrichment_select.py:2527`, inside the render-time
enrichment path; there's no such call anywhere in `scripts/catalog/*.py`
(plan-generation, pre-catalog-entry).

**Contrast:** when a bank *exists but is thin*, `enrichment_select.py` raises
`InsufficientVariantsError` (defined :135, raised :2433) — a hard-fail. So the
only hard-stop fires for **partial** coverage, never **total absence**, which is
backwards from "contract must exist before render." This answers discovery Q3:
`BESTSELLER-INJECTIONS-MANDATORY-01`'s own table already says "Named-character
story atoms... **YES — content-dependent (where present; per-persona content
gap)**" (`PEARL_ARCHITECT_STATE.md:632`) = mandatory-if-present, not
mandatory-hard-fail-if-absent. Code confirms cap text.

**2.3 The honesty gates are post-render, CI-advisory.**
`scripts/ci/check_research_fit_honesty.py` and `check_book_story_authored.py`
both read already-rendered `enrichment_audit.json` (written at
`run_pipeline.py:2521-2522`; research_fit stamp computed at `:2704-2749`). Both
wired into `.github/workflows/drift-detectors.yml` under
`continue-on-error: true`; the honesty check runs with `--advisory`, and
`check_book_story_authored.py`'s own docstring: *"Exit code is always 0... The
book still renders."* `--strict` exists but the workflow comment calls it *"an
operator-tier threshold decision; do not flip without sign-off."*

`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` Layer 1 (2026-07-21
addition) already codifies the resulting cap: unbound `research_fit` caps a book
at `structurally_clear_only` regardless of other Layer-1 passes; *"Hard-blocking
render on unbound research_fit is an operator-tier threshold (--strict); default
remains advisory."* Accurate and current — Lane B's contribution is showing this
is a **label attached after the render**, not a gate before it.

**2.4 Sequencing verdict:** content-authority enters **only at render time as a
lookup** — not before catalog approval (admission checks an unrelated artifact,
`master_arcs`), not as a separate post-approval-pre-render gate (no such stage
exists in code), and not "varies by persona" in mechanism (the mechanism is
uniform soft-skip; only bank *existence* varies — 6 of 13 personas have any
story_atoms at all per the 2026-07-22 pipeline audit, and `corporate_managers`,
the EPUB workhorse persona, has **zero**).

## 3. The gap this creates (cited, not re-derived)

`artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md` (§1.2, §3.3)
already names it: *"a book can PASS register_gate (anxiety×comparison) and still
have zero character through-line because research_fit never bound...
Corporate_managers is the EPUB workhorse persona — and it has no story_atoms
banks → research_fit skip/unbound by construction."*

**Lane B's sequencing trace explains why, structurally:** (a) catalog admission
never checks content-authority — it checks `master_arcs`; (b) the render-time
lookup degrades silently on absence rather than blocking, so an uncovered cell
sails through Layer-1 machine gates; (c) the only gate that notices fires after
the fact, non-blocking, on the finished artifact — the `structurally_clear_only`
cap is a label a human has to go read. Nothing between "plan admitted" and "book
fully rendered and scored" ever asks "does this cell's contract exist yet?" This
is the sequencing-level version of CLAUDE.md's "gate-PASS ≠ bestseller":
**catalog-admitted ≠ contract-exists.**

## 4. What "seeing the contract through" would require

**(A) Current state — render-time-only advisory.** Near-zero cost,
visibility-only, doesn't change what's catalogued/rendered.

**(B) Proposed, not built — plan-time gate.** A check in
`gen_plan_skeletons.py` (or a companion script) that, per cell, checks
`story_atoms/<persona>/anchored/<topic>/<engine>/` (or teacher_banks coverage)
**before** the plan YAML is written — either withholding the cell or flagging
it `_needs_story_atoms: true` (mirroring the existing `_needs_authoring: true`
prose-skeleton convention).

**Not this lane's call, for two concrete reasons:**

1. **Touches `CATALOG-800-PER-BRAND-01`.** Story_atoms banks exist for only
   **9** persona×topic×engine cells today (07-22 audit §3.3) against a catalog
   target on the order of ~800 system-wide high-confidence configs. A
   withhold-on-missing-bank policy would currently make almost the entire
   catalog inadmissible.
2. **Touches `PEARL-EDITOR-UPSTREAM-01` directly.** The cap explicitly rejected
   inserting Pearl_Editor as a runtime pipeline step "because it would require
   new pipeline architecture" (:682). A plan-time gate *is* that new
   architecture — it converts Pearl_Editor from read-overlay consumer to
   catalog-admission gatekeeper, a real authority-boundary change.

**Verdict:** executable-default as a script change; the *policy* (withhold vs.
flag, interaction with the 800-config target) is operator-tier / Pearl_Architect's
call.

## 5. Cap-entry-candidate (flagged for Lane F / operator ratification — not self-ratified)

**Working title `PEARL-EDITOR-PLAN-TIME-GATE-01`:** should
`book_plans_en_us/` admission also require/flag story_atoms/teacher_banks
coverage before catalog entry, vs. today's render-time-only soft-skip +
post-render advisory label? Options for the operator:

- (a) leave as-is;
- (b) plan-time flag only;
- (c) plan-time withhold (would shrink admissible cells to ~9 today — likely too
  aggressive without scoped rollout);
- (d) profile-gated hybrid mirroring `BESTSELLER-INJECTIONS-MANDATORY-01`'s
  pattern (withhold under production catalog runs, flag-only under
  draft/debug).

## What this lane did NOT cover

- Any actual plan-time gate implementation (proposal only, per lane scope).
- Locales beyond en_US.
- Whether option (c)/(d) would leave enough admissible cells to hit any
  catalog-scale target — that depends on Lane A's/Lane C's numbers, not this
  lane's.

## Sources read in full or at cited line ranges

`docs/PEARL_ARCHITECT_STATE.md` (PEARL-EDITOR-UPSTREAM-01 :668-694,
BESTSELLER-INJECTIONS-MANDATORY-01 :620-647, CATALOG-800-PER-BRAND-01 :648-667,
HOOK-SCENE-FIRST-01 :1890-1909); `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
(teacher_mode row); `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`
(full); `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`;
`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`;
`phoenix_v4/planning/story_planner.py`, `enrichment_select.py`,
`registry_resolver.py`; `scripts/catalog/gen_plan_skeletons.py` (full);
`scripts/ci/check_research_fit_honesty.py`, `check_book_story_authored.py`;
`.github/workflows/drift-detectors.yml`; `scripts/run_pipeline.py`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM (Lane B audit)
TASK:           Lane B — Pearl_Editor / content-authority sequencing audit
COMMIT_SHA:     <filled in by dispatcher at commit time>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_b_editor_sequencing/REPORT.md
FILES_READ:     docs/PEARL_ARCHITECT_STATE.md (targeted sections); artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md (full); docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md; docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; phoenix_v4/planning/story_planner.py, enrichment_select.py, registry_resolver.py; scripts/catalog/gen_plan_skeletons.py (full); scripts/ci/check_research_fit_honesty.py, check_book_story_authored.py; .github/workflows/drift-detectors.yml; scripts/run_pipeline.py
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 §1.2/§3.3 | documents: PEARL-EDITOR-UPSTREAM-01, BESTSELLER-INJECTIONS-MANDATORY-01, BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md | builds_on: existing cap-entry chain | inventory: EXTENDS
STATUS:         completed
HANDOFF_TO:     Lane F (synthesis)
NEXT_ACTION:    Operator ratification needed on cap-entry-candidate PEARL-EDITOR-PLAN-TIME-GATE-01 (Section 5) before any implementation lane.
SIGNAL:         lane-b-editor-sequencing-merged=<sha>
```

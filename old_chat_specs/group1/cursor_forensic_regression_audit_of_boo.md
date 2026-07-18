# Forensic regression audit of book quality
_Exported on 4/16/2026 at 19:28:56 GMT+8 from Cursor (3.1.15)_

---

**User**

Use this as the **exact repo-agent intake prompt**.

---

STARTUP_RECEIPT
AGENT: Pearl_Dev
TASK: Run regression audit to identify why previously higher-quality book governance no longer governs final Pearl Prime manuscript output
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; config/quality/book_pass_gate_thresholds.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; config/source_of_truth/frame_registry.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
READ_PATH_COMPLETE: yes
WRITE_SCOPE: artifacts/audit/book_quality_regression_audit_20260414.md; artifacts/audit/book_quality_regression_matrix_20260414.tsv; artifacts/audit/book_quality_path_diff_20260414.md; artifacts/pilots/book_quality_regression_verify/*; optional small helper script under phoenix_v4/quality/ or scripts/ only if needed for evidence extraction
OUT_OF_SCOPE: rewriting books by hand; adding new LLM quality systems; Pearl News; video; broad refactors before audit findings
BLOCKERS: none known
READY_STATUS: ready

You are Pearl_Dev + Pearl_Architect. This is a **forensic regression audit**, not a generic writing-quality brainstorm.

## Mission

Determine **why previously higher-quality governance / editorial / chapter-contract / composition logic is no longer sufficiently governing the final Pearl Prime manuscript output**.

Assume the user’s claim may be true:

* there were earlier regimes where outputs scored 8–9/10
* substantial editorial, contract, and gating work already exists
* current outputs are materially worse
* the problem may be regression, path drift, ordering drift, authority drift, or metric drift rather than total absence of quality architecture

Your job is to identify:

1. what the last known stronger regime was
2. what exact path created it
3. what exact path creates the current weaker outputs
4. where those paths diverge
5. which divergences most plausibly explain the drop in real book quality

## Required evidence corpus

Treat these as key evidence inputs:

* `artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt`
* `combined_qa_all_runtime_formats.txt` if present in the current workspace / uploaded context
* current runtime ladder evidence showing:

  * `micro_book_15` Reject
  * `micro_book_20` Reject
  * `short_book_30` Reject
  * repeated-block dedup shrinking `short_book_30` from 7819 to 4074 words
  * repeated warnings about weak escalation, exercise fallback/drops, and visible artifact leakage such as `## HOOK v14` and broken merges like `The the train` 

Use the anxiety runtime ladder as the **current bad regime** anchor.

## Core question

Do **not** just restate symptoms like repetition, weak flow, or low scores.
Determine **why the already-built quality machinery is not sufficiently controlling final prose anymore**.

## Audit framework

Produce findings in the following structure.

### 1. Comparison set

Create three groups:

#### Group A — prior stronger regime

Find 3–5 historical runs / artifacts / branches / PR eras / manifests that appear to represent the earlier higher-scoring or better-feeling regime.

For each:

* commit SHA or PR if recoverable
* runtime format
* topic / persona / teacher
* exact command or manifest if recoverable
* output artifact paths
* quality scores present
* whether a fresh human-style read still suggests it was actually better

Do not trust old scores blindly. Verify with evidence.

#### Group B — current weak regime

Use current anxiety runtime ladder outputs:

* `micro_book_15`
* `micro_book_20`
* `short_book_30`
* plus 1–2 longer runtimes if available in the file or workspace

#### Group C — transition points

Identify commits / PRs / path changes likely relevant to regression:

* spine path changes
* `compose_from_enriched_book` or related composer changes
* chapter composition / bridge logic changes
* frame governor changes
* editorial agent / contract enforcement changes
* delivery cleanup / dedupe ordering changes
* runtime expansion changes
* fallback selection changes

## Required analysis sections

### 2. Score audit

Determine whether older 8–9 scores measured the same thing as current failing judgments.

For old-good and current-bad outputs, answer:

* what exact metrics produced the score
* chapter-level vs section-level vs whole-book
* whether cross-chapter repetition was measured
* whether escalation was measured
* whether artifact leakage was penalized
* whether whole-book reading flow was measured
* whether the score mostly captured compliance vs actual reader experience

Output:

* `artifacts/audit/book_quality_regression_matrix_20260414.tsv`
  with columns like:
  `run_id | era | score_source | scope | repetition_measured | escalation_measured | artifact_penalty | whole_book_flow_measured | comments`

### 3. Path trace

For both stronger-regime and weak-regime examples, trace exact generation path:

#### Planning

* planner / spine source
* chapter job source
* runtime expansion behavior

#### Content selection

* atom banks used
* fallback rate
* story / exercise / insight sources
* teacher-mode behavior

#### Composition

* exact function that turns structure into prose
* whether true chapter prose composition is used
* whether enriched slots are concatenated directly
* whether bridge logic is active
* whether chapter-to-chapter state is used

#### Editorial / gating

* whether editorial systems can change generation or only score it
* whether chapter contracts are hard-enforced or warning-only
* whether gating occurs before or after prose is effectively fixed

#### Delivery cleanup

* exact order of dedupe / cleanup / rendering / quality summary / book-quality gate
* whether cleanup can repair root issues or only surface them

Output:

* `artifacts/audit/book_quality_path_diff_20260414.md`

### 4. Governance table

Create a table with four columns:

| Quality mechanism | Exists in repo? | Invoked on current path? | Can still materially change final prose? |

Audit at least:

* chapter purpose contracts
* frame governor
* delivery contract gate
* editorial agent / editorial pass
* chapter composer / transition logic
* dedupe logic
* therapeutic quality checks
* story selection constraints
* exercise coverage constraints
* runtime novelty controls
* any stronger legacy compose path if found

The goal is to catch mechanisms that **exist but no longer govern**.

### 5. Warning-only system audit

For each warning observed in current runs, classify whether it is:

* harmless
* quality-degrading
* book-killing

Examples to inspect:

* emotional job repeats previous chapter
* exercise fallback
* exercise dropped by governance cap
* repeated-block dedup would shrink below floor so pre-dedup kept
* quality gate Reject but QA artifacts still written/rendered

Determine whether these used to be blocking or should now be blocking.

### 6. Data-source regression audit

Check whether the architecture is fine but content pools degraded.

Inspect:

* atom pool breadth
* exercise coverage
* story bank diversity
* teacher-specific content coverage
* fallback frequency
* repeated scene-furniture inventory
* chapter job diversity
* frame coverage

Quantify where possible:

* fallback rate old vs current
* unique story count
* unique exercise count
* repeated scene stem frequency
* proportion of repeated symptom-chain paragraphs

### 7. Composer regression audit

This section is mandatory.

Determine:

* which function actually rendered final prose in stronger-regime outputs
* which function renders final prose now
* whether stronger-regime used a real chapter composer with bridges / sequencing
* whether current spine path mainly concatenates enriched slots
* whether later steps flatten earlier stronger composition
* whether chapter dominant_job is actually enforced during composition or only logged

Be explicit. If `compose_from_enriched_book` bypasses a stronger composer path, say so with evidence. If that hypothesis is wrong, say so.

### 8. Fake-length audit

For each runtime in the current ladder, quantify:

* nominal word count
* repeated block rate
* dedup-adjusted effective word count
* repeated scene-furniture rate
* number of chapters with repeated emotional job
* number of chapters dominated by the same structural mode mix

Goal:
determine whether longer runtimes are creating real depth or mainly repetition inflation.

### 9. Human-judgment drift audit

Compare internal score vs actual read quality on a small sample of older and current outputs.

Score manually using deterministic rubric:

* cohesive flow
* repetition
* escalation
* felt authorship
* emotional containment
* desire to keep reading

You do not need an LLM for this. Use evidence-based rubric notes.

Goal:
identify whether metric drift explains why older outputs could score high while still not being truly strong.

## Required final artifacts

### A. Main narrative audit

`artifacts/audit/book_quality_regression_audit_20260414.md`

This must answer:

1. what was the last known stronger regime
2. what path created it
3. what path creates current weak outputs
4. where the paths diverge
5. which divergence most plausibly explains the quality drop
6. which quality systems now exist but are advisory/non-governing
7. which problems are routing/order/authority/data/metric/composer regressions
8. minimum viable restoration plan

### B. Regression matrix TSV

`artifacts/audit/book_quality_regression_matrix_20260414.tsv`

### C. Path diff document

`artifacts/audit/book_quality_path_diff_20260414.md`

### D. Pilot verification folder

`artifacts/pilots/book_quality_regression_verify/`
Include:

* README.md
* one compact evidence table
* one “most likely regression causes” summary
* optional tiny extracted text snippets used in comparison

## Required classification buckets

Every major finding must be categorized as one of:

* ROUTING regression
* ORDERING regression
* AUTHORITY regression
* DATA regression
* METRIC regression
* COMPOSER regression

## Success criteria

The audit is successful only if it moves beyond “the books are repetitive / low quality” and identifies **why previously built quality architecture is not currently controlling final manuscript quality**.

## Strong hypotheses to test

Do not assume these are true; test them:

1. current spine/runtime path bypasses or weakens stronger chapter composition logic
2. chapter contracts now warn instead of controlling
3. repetition now comes from narrow fallback pools plus late-stage concatenation
4. older scores measured local compliance more than whole-book quality
5. newer gates describe failure better than they prevent failure
6. later cleanup / dedupe / runtime logic overwrites earlier good shaping

## Constraints

* no web browsing
* no LLM classifiers
* no broad repo refactors before the audit
* prefer direct code-path evidence, manifests, and artifact comparisons
* if repo evidence is incomplete, say exactly what is missing and what that prevents you from proving

## Output tone

Be blunt, specific, and evidence-based. Avoid vague advice. Name exact functions, configs, artifacts, and path divergences.

## CLOSEOUT required

Return:

* 10-line executive summary
* strongest evidence chain
* top 3 regression causes
* what to restore first
* commit SHA
* PR link if any
* whether `ws_book_quality_regression_audit_20260414` was registered in `ACTIVE_WORKSTREAMS.tsv`

CLOSEOUT_RECEIPT required.

---

That is the prompt I would use.


Use this as the **exact repo-agent intake prompt**.

---

STARTUP_RECEIPT
AGENT: Pearl_Dev
TASK: Run regression audit to identify why previously higher-quality book governance no longer governs final Pearl Prime manuscript output
PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: core_pipeline
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; config/quality/book_pass_gate_thresholds.yaml; config/source_of_truth/chapter_purpose_contracts.yaml; config/source_of_truth/frame_registry.yaml; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
READ_PATH_COMPLETE: yes
WRITE_SCOPE: artifacts/audit/book_quality_regression_audit_20260414.md; artifacts/audit/book_quality_regression_matrix_20260414.tsv; artifacts/audit/book_quality_path_diff_20260414.md; artifacts/pilots/book_quality_regression_verify/*; optional small helper script under phoenix_v4/quality/ or scripts/ only if needed for evidence extraction
OUT_OF_SCOPE: rewriting books by hand; adding new LLM quality systems; Pearl News; video; broad refactors before audit findings
BLOCKERS: none known
READY_STATUS: ready

You are Pearl_Dev + Pearl_Architect. This is a **forensic regression audit**, not a generic writing-quality brainstorm.

## Mission

Determine **why previously higher-quality governance / editorial / chapter-contract / composition logic is no longer sufficiently governing the final Pearl Prime manuscript output**.

Assume the user’s claim may be true:

* there were earlier regimes where outputs scored 8–9/10
* substantial editorial, contract, and gating work already exists
* current outputs are materially worse
* the problem may be regression, path drift, ordering drift, authority drift, or metric drift rather than total absence of quality architecture

Your job is to identify:

1. what the last known stronger regime was
2. what exact path created it
3. what exact path creates the current weaker outputs
4. where those paths diverge
5. which divergences most plausibly explain the drop in real book quality

## Required evidence corpus

Treat these as key evidence inputs:

* `artifacts/qa/pearl_prime_ahjan_genz_anxiety_all_runtimes.txt`
* `combined_qa_all_runtime_formats.txt` if present in the current workspace / uploaded context
* current runtime ladder evidence showing:

  * `micro_book_15` Reject
  * `micro_book_20` Reject
  * `short_book_30` Reject
  * repeated-block dedup shrinking `short_book_30` from 7819 to 4074 words
  * repeated warnings about weak escalation, exercise fallback/drops, and visible artifact leakage such as `## HOOK v14` and broken merges like `The the train` 

Use the anxiety runtime ladder as the **current bad regime** anchor.

## Core question

Do **not** just restate symptoms like repetition, weak flow, or low scores.
Determine **why the already-built quality machinery is not sufficiently controlling final prose anymore**.

## Audit framework

Produce findings in the following structure.

### 1. Comparison set

Create three groups:

#### Group A — prior stronger regime

Find 3–5 historical runs / artifacts / branches / PR eras / manifests that appear to represent the earlier higher-scoring or better-feeling regime.

For each:

* commit SHA or PR if recoverable
* runtime format
* topic / persona / teacher
* exact command or manifest if recoverable
* output artifact paths
* quality scores present
* whether a fresh human-style read still suggests it was actually better

Do not trust old scores blindly. Verify with evidence.

#### Group B — current weak regime

Use current anxiety runtime ladder outputs:

* `micro_book_15`
* `micro_book_20`
* `short_book_30`
* plus 1–2 longer runtimes if available in the file or workspace

#### Group C — transition points

Identify commits / PRs / path changes likely relevant to regression:

* spine path changes
* `compose_from_enriched_book` or related composer changes
* chapter composition / bridge logic changes
* frame governor changes
* editorial agent / contract enforcement changes
* delivery cleanup / dedupe ordering changes
* runtime expansion changes
* fallback selection changes

## Required analysis sections

### 2. Score audit

Determine whether older 8–9 scores measured the same thing as current failing judgments.

For old-good and current-bad outputs, answer:

* what exact metrics produced the score
* chapter-level vs section-level vs whole-book
* whether cross-chapter repetition was measured
* whether escalation was measured
* whether artifact leakage was penalized
* whether whole-book reading flow was measured
* whether the score mostly captured compliance vs actual reader experience

Output:

* `artifacts/audit/book_quality_regression_matrix_20260414.tsv`
  with columns like:
  `run_id | era | score_source | scope | repetition_measured | escalation_measured | artifact_penalty | whole_book_flow_measured | comments`

### 3. Path trace

For both stronger-regime and weak-regime examples, trace exact generation path:

#### Planning

* planner / spine source
* chapter job source
* runtime expansion behavior

#### Content selection

* atom banks used
* fallback rate
* story / exercise / insight sources
* teacher-mode behavior

#### Composition

* exact function that turns structure into prose
* whether true chapter prose composition is used
* whether enriched slots are concatenated directly
* whether bridge logic is active
* whether chapter-to-chapter state is used

#### Editorial / gating

* whether editorial systems can change generation or only score it
* whether chapter contracts are hard-enforced or warning-only
* whether gating occurs before or after prose is effectively fixed

#### Delivery cleanup

* exact order of dedupe / cleanup / rendering / quality summary / book-quality gate
* whether cleanup can repair root issues or only surface them

Output:

* `artifacts/audit/book_quality_path_diff_20260414.md`

### 4. Governance table

Create a table with four columns:

| Quality mechanism | Exists in repo? | Invoked on current path? | Can still materially change final prose? |

Audit at least:

* chapter purpose contracts
* frame governor
* delivery contract gate
* editorial agent / editorial pass
* chapter composer / transition logic
* dedupe logic
* therapeutic quality checks
* story selection constraints
* exercise coverage constraints
* runtime novelty controls
* any stronger legacy compose path if found

The goal is to catch mechanisms that **exist but no longer govern**.

### 5. Warning-only system audit

For each warning observed in current runs, classify whether it is:

* harmless
* quality-degrading
* book-killing

Examples to inspect:

* emotional job repeats previous chapter
* exercise fallback
* exercise dropped by governance cap
* repeated-block dedup would shrink below floor so pre-dedup kept
* quality gate Reject but QA artifacts still written/rendered

Determine whether these used to be blocking or should now be blocking.

### 6. Data-source regression audit

Check whether the architecture is fine but content pools degraded.

Inspect:

* atom pool breadth
* exercise coverage
* story bank diversity
* teacher-specific content coverage
* fallback frequency
* repeated scene-furniture inventory
* chapter job diversity
* frame coverage

Quantify where possible:

* fallback rate old vs current
* unique story count
* unique exercise count
* repeated scene stem frequency
* proportion of repeated symptom-chain paragraphs

### 7. Composer regression audit

This section is mandatory.

Determine:

* which function actually rendered final prose in stronger-regime outputs
* which function renders final prose now
* whether stronger-regime used a real chapter composer with bridges / sequencing
* whether current spine path mainly concatenates enriched slots
* whether later steps flatten earlier stronger composition
* whether chapter dominant_job is actually enforced during composition or only logged

Be explicit. If `compose_from_enriched_book` bypasses a stronger composer path, say so with evidence. If that hypothesis is wrong, say so.

### 8. Fake-length audit

For each runtime in the current ladder, quantify:

* nominal word count
* repeated block rate
* dedup-adjusted effective word count
* repeated scene-furniture rate
* number of chapters with repeated emotional job
* number of chapters dominated by the same structural mode mix

Goal:
determine whether longer runtimes are creating real depth or mainly repetition inflation.

### 9. Human-judgment drift audit

Compare internal score vs actual read quality on a small sample of older and current outputs.

Score manually using deterministic rubric:

* cohesive flow
* repetition
* escalation
* felt authorship
* emotional containment
* desire to keep reading

You do not need an LLM for this. Use evidence-based rubric notes.

Goal:
identify whether metric drift explains why older outputs could score high while still not being truly strong.

## Required final artifacts

### A. Main narrative audit

`artifacts/audit/book_quality_regression_audit_20260414.md`

This must answer:

1. what was the last known stronger regime
2. what path created it
3. what path creates current weak outputs
4. where the paths diverge
5. which divergence most plausibly explains the quality drop
6. which quality systems now exist but are advisory/non-governing
7. which problems are routing/order/authority/data/metric/composer regressions
8. minimum viable restoration plan

### B. Regression matrix TSV

`artifacts/audit/book_quality_regression_matrix_20260414.tsv`

### C. Path diff document

`artifacts/audit/book_quality_path_diff_20260414.md`

### D. Pilot verification folder

`artifacts/pilots/book_quality_regression_verify/`
Include:

* README.md
* one compact evidence table
* one “most likely regression causes” summary
* optional tiny extracted text snippets used in comparison

## Required classification buckets

Every major finding must be categorized as one of:

* ROUTING regression
* ORDERING regression
* AUTHORITY regression
* DATA regression
* METRIC regression
* COMPOSER regression

## Success criteria

The audit is successful only if it moves beyond “the books are repetitive / low quality” and identifies **why previously built quality architecture is not currently controlling final manuscript quality**.

## Strong hypotheses to test

Do not assume these are true; test them:

1. current spine/runtime path bypasses or weakens stronger chapter composition logic
2. chapter contracts now warn instead of controlling
3. repetition now comes from narrow fallback pools plus late-stage concatenation
4. older scores measured local compliance more than whole-book quality
5. newer gates describe failure better than they prevent failure
6. later cleanup / dedupe / runtime logic overwrites earlier good shaping

## Constraints

* no web browsing
* no LLM classifiers
* no broad repo refactors before the audit
* prefer direct code-path evidence, manifests, and artifact comparisons
* if repo evidence is incomplete, say exactly what is missing and what that prevents you from proving

## Output tone

Be blunt, specific, and evidence-based. Avoid vague advice. Name exact functions, configs, artifacts, and path divergences.

## CLOSEOUT required

Return:

* 10-line executive summary
* strongest evidence chain
* top 3 regression causes
* what to restore first
* commit SHA
* PR link if any
* whether `ws_book_quality_regression_audit_20260414` was registered in `ACTIVE_WORKSTREAMS.tsv`

CLOSEOUT_RECEIPT required.

---

That is the prompt I would use.


---

**Cursor**

I’m going to run the regression audit directly from your intake prompt: first I’ll map the current bad-runtime evidence and the code paths that generate prose, then compare those against older stronger regimes from git/artifacts, and finally write the four required audit deliverables under `artifacts/audit/` and `artifacts/pilots/book_quality_regression_verify/`.

I found the two anchor QA artifacts and initial composer files; next I’m drilling into those rendering and gate paths plus git history to build the strong-vs-weak path diff with concrete evidence.

I’ve confirmed all seven runtime QA report folders are present (15m through 6h). Next I’m extracting the exact fail/hold reasons and gate semantics from those JSON reports so we can classify warning-only vs governing behavior.

I’ve now extracted concrete weak-regime signals (including the dedup floor behavior and repeated “escalation contract may be weak” warnings). Next I’m locating prior pass/8–9-era artifacts and their code paths so we can identify exact divergence points.

I found likely “stronger-era” evidence in an older planning bundle under `artifacts/ops`; I’m now running a repo-wide JSON scan for historical `release_band: Pass`/high-score records and mapping them back to runtime paths and commits.

I found the key transition commits: `ed4db4275c` (introduces `compose_from_enriched_book`) and `04c405afa7` (wires spine mode into the main runner). I’m now validating whether pilot baseline outputs were actually better by reading those historical artifacts directly, not just trusting old scores.

I now have strong path-level evidence from code/history; next I’m pulling the authority specs you listed so the final findings are grounded against intended governance (not just observed behavior).

I have enough evidence for the root-cause chain, and I’m now verifying whether the batch runs used draft/production gate mode so the warning-vs-blocking conclusions are precise before I write the final audit artifacts.

I’ve confirmed the key missing link: the failing runtime batch was generated with `quality_profile=debug`, so most gates were intentionally non-blocking while still writing `Reject` reports. Next I’m writing the three requested audit artifacts plus a pilot verification folder with evidence tables and cause ranking, then I’ll register this audit workstream in `ACTIVE_WORKSTREAMS.tsv`.

I’m now writing the verification bundle under `artifacts/pilots/book_quality_regression_verify/` so the audit has a compact, reproducible evidence trail (matrix + cause ranking + quick rerun pointers).

Implemented the audit deliverables and filled them with the forensic findings chain you asked for.

### What I wrote

- Main narrative audit: `artifacts/audit/book_quality_regression_audit_20260414.md`
- Regression matrix: `artifacts/audit/book_quality_regression_matrix_20260414.tsv`
- Path divergence doc: `artifacts/audit/book_quality_path_diff_20260414.md`
- Pilot verification bundle:
  - `artifacts/pilots/book_quality_regression_verify/README.md`
  - `artifacts/pilots/book_quality_regression_verify/evidence_table.tsv`
  - `artifacts/pilots/book_quality_regression_verify/most_likely_regression_causes.md`
  - `artifacts/pilots/book_quality_regression_verify/replay_notes.md`
- Workstream registration updated in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` with `ws_book_quality_regression_audit_20260414`.

### Core conclusions captured in the audit

- Last stronger regime is the chapter-thesis composition regime centered on `compose_chapter_prose` (`COMPOSER`).
- Current weak outputs are created by spine runtime routing through `compose_from_enriched_book` concatenation behavior (`ROUTING` + `COMPOSER`).
- Current ladder runs were executed with `quality_profile=debug`, so `Reject` outcomes are diagnostic/non-blocking in that batch (`AUTHORITY` + `ORDERING`).
- Dedup floor logic retained repeated text when dedup would drop below floor, causing nominal-length inflation (`METRIC` + `DATA` + `ORDERING`).
- The strongest causal chain is composer parity gap first, then non-binding gate profile, then fake-length retention.

### Verification

- Checked all newly edited files for diagnostics with `ReadLints`; no linter errors reported.

### Notes

- No commit or PR was created in this turn.
- If you want, I can now stage only these audit/workstream changes and create a clean commit with your preferred message style.


# B2 Release-Profile Emission Contract — AUTHORITATIVE (real-doctrine base)

**Author:** Pearl_Dev (lane W3, RE-FIRE) · **Date:** 2026-06-17
**Project:** `proj_pearl_prime_bestseller_rebase_20260425` · **Subsystem:** `core_pipeline`
**Base measured:** clean `origin/main` HEAD **`aaebe0cdc4`** = the **#1700 merge commit itself** (authored the 12 sai_ma TEACHER_DOCTRINE atoms). Contains #1701 SCENE/F2 repair (`692b27d919`, ancestor) and #1578 EI P0 T×E×F fitness (`6d01afed99`, ancestor — advisory).
**Authority:** `docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` §6/§8 (B2 named co-gate, L222-223); `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` §5D/§9 (emission-contract home); `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md`.

> **Status:** Measurement + contract draft. The contract's normative emit-vs-abort rule is proposed as an amendment to `PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` §5D (text in §6) — **Pearl_Architect ratifies; this document does not self-ratify.** No gate was loosened. No pipeline code behavior was changed.

> **⚠ SUPERSEDES the degraded-base run.** An earlier same-day W3 artifact —
> `artifacts/analysis/pearl_prime_priorities/B2_RELEASE_PROFILE_EMISSION_CONTRACT_20260617.md`
> (no `_REALBASE` suffix) + `b2_emission_contract_20260617/` — was built on **`6d01afed99`**,
> the **parent** of the #1700 merge. **That tree has ZERO TEACHER_DOCTRINE atoms** (verified:
> `git ls-tree -r 6d01afed99 | grep TEACHER_DOCTRINE = 0`; on `aaebe0cdc4` = 12), so its devotion
> books rendered on **COMPRESSION-degraded substitute doctrine** and its devotion verdict (F2 = 0)
> is **INVALID** for this doctrine-dependent measurement. Its PR will be closed as superseded.
> THIS document is the authoritative run.

---

## 0. TL;DR

1. **The devotion §6 B2 premise is STALE.** `--quality-profile production` **already emits `book.txt` with exit 0** on `origin/main` `aaebe0cdc4`, for both a devotion cell (real doctrine) and a non-devotion cell. The #1536 numbers (register 81 / ei_v2 0.53 / chapter_flow 2/12) are **dead**.
2. **On the real-doctrine base the book is far closer to shipping than #1536 implied:** `book_pass` **PASS** (word_count clamps under the 22k ceiling), `chapter_flow` **PASS**, `ei_v2` **PASS (0.65)**, `scene_anti_genericity` **WARN** (not FAIL), `book_quality` band **Hold** (non-blocking).
3. **The sole remaining production blocker is the *separate* `register_gate` HARD_FAIL on a tiny residual F2** — **3 findings** (devotion) / **2 findings** (cross-check), down from #1536's 81-class. Of those, ~1–2 per book are **genuine** sub-4-word truncation orphans (real "never-ship" composer artifacts), the rest are **F2.B sentence-final-preposition calibration false-positives**.
4. **register_gate is NOT wired into run_pipeline** (`grep register_gate scripts/run_pipeline.py` → nothing). So today a book can emit from `production` while still carrying an F2 HARD_FAIL that the separate CLI would catch. **This independence is the gap the B2 contract closes.**
5. **The B2 contract is therefore "ratify WHEN production emits + wire register_gate F2 as the single ship-blocking gate," not "make production emit."** Defined normatively in §6; proposed as a §5D amendment for Pearl_Architect to ratify.

---

## 1. How the measurement was taken (reproducible, no paid API, no worktree)

The working branch (`agent/gold-reference-7tier-redirect-20260530`) is **235 behind / 200 ahead** of `origin/main`, and **every pipeline file differs** — `run_pipeline.py` (+436 lines), `register_gate.py` (**+572 lines**), `golden_chapter_synthesis.py` (+108), `enrichment_select.py` (+186), `book_renderer.py` (+312). **A working-tree run measures drifted code, not `aaebe0cdc4`.** (A first pass from the repo dir gave book_pass FAIL word_budget=24,602 + scene FAIL + register F2=23 — all artifacts of working-branch drift; recorded here only as the contrast that proves the base matters.)

The authoritative build ran against a clean `origin/main` tree materialized via `git archive` (no worktree, no index mutation):

```bash
GIT_LFS_SKIP_SMUDGE=1 git archive aaebe0cdc4 | tar -x -C /tmp/po_main_w3
# VERIFIED: /tmp/po_main_w3/{scripts/run_pipeline.py, phoenix_v4/quality/register_gate.py,
#   golden_chapter_synthesis.py, enrichment_select.py} == git show aaebe0cdc4:<path>  (byte-exact)
# VERIFIED: 12 sai_ma TEACHER_DOCTRINE atoms present in the tree.
```

Build (the surface W4 uses):

```bash
PYTHONPATH=/tmp/po_main_w3 python3 /tmp/po_main_w3/scripts/run_pipeline.py \
  --topic burnout --persona corporate_managers --teacher sai_ma \
  --arc .../master_arcs/corporate_managers__burnout__overwhelm__F006.yaml \
  --pipeline-mode spine --quality-profile production \
  --runtime-format standard_book --chapter-architecture-version 2 \
  --render-book --render-dir <D> --atoms-root .../atoms \
  --exercise-journeys --enforce-scene-gate --no-job-check --no-generate-freebies
```

Separate register gate (NOT part of run_pipeline — see §3d):

```bash
PYTHONPATH=/tmp/po_main_w3 python3 -m phoenix_v4.quality.register_gate \
  --book <D>/book.txt --teacher sai_ma --persona corporate_managers --topic burnout \
  --output <D>/register_gate_report.json
```

**SANITY — real doctrine was drawn (the dispatch's STOP-gate):** the built `book.txt` contains **90** "Sai Maa"/doctrine references and **9** "as taught by Sai Maa" practice headings, sourced from the real `TEACHER_DOCTRINE_000..011` atoms (substantive doctrinal prose: Divine Mother, Jagadguru Vishnuswami lineage). The book is genuinely built on the real 12 atoms — **not** COMPRESSION substitutes. Proceed.

Cells:
- **Devotion (W4 surface):** `devotion_path / sai_ma / corporate_managers / burnout / overwhelm` — engine-legal (`burnout → overwhelm` allowed per `topic_engine_bindings.yaml`); book plan + arc present; book plan pinned to the `aaebe0cdc4` version (working-tree title drift is naming-engine metadata only, irrelevant to prose/gates).
- **Cross-check (contract generalization):** `ahjan / gen_z_professionals / anxiety / spiral` — different teacher, topic, persona.

---

## 2. Current production-profile measurement (clean `origin/main` `aaebe0cdc4`)

| cell | book.txt? | exit | run_pipeline failures | chapter_flow | scene_gate | book_pass | ei_v2 | craft | book_quality | **register verdict** | **F2 (HARD_FAIL)** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **devotion** (sai_ma/corp_mgr/burnout) | **YES** (125 KB / 21,654 w) | **0** | **[]** | PASS | WARN | **PASS** | PASS 0.65 | PASS 0.56 | **Hold** | **HARD_FAIL** | **3** |
| **cross-check** (ahjan/gen_z/anxiety) | **YES** (125 KB / 21,673 w) | **0** | **[]** | PASS | WARN | **PASS** | PASS 0.68 | PASS 0.69 | **Hold** | **HARD_FAIL** | **2** |

### 2a. run_pipeline emits cleanly (exit 0) — the §6 premise is stale

`book.txt` is written, both cells, exit 0, `quality_gate_failures: []`. No `BLOCKED:` line. **There is no production-profile emission abort on `aaebe0cdc4`.** The §6 "currently emits no book.txt" symptom does **not** reproduce on the real base.

### 2b. book_pass = PASS — word_budget clamps under the SSOT-reconciled ceiling

`book_pass` is **PASS** on both cells. Sole historical failure mode (`word_budget`) is **resolved**:
- `format_registry.yaml standard_book.word_range = [9000, 22000]` — **already reconciled** to the duration SSOT (`platform_duration_profiles.yaml:222 T5_standard 22000`) per DURATION-DERIVATION-01. The stale `20000` ceiling the COMPOSER_FRONTIER spec flagged is **gone**.
- Rendered counts (devotion 21,654; cross-check 21,673) sit **under** 22,000 — origin/main's render path clamps to ceiling (the `_reduce_scene_anchor_density` / post-render accounting on `origin/main` keeps the final count in-band). All book_pass subchecks PASS: band_distribution (12 distinct roles), identity_stages (recognition/mechanism/integration 3/3), callback_completion, angle_journey_coherence.
- **No word-budget config change is needed** (the W3 dispatch's "trivial config reconciliation IF a real gap" — there is **no residual gap** on `aaebe0cdc4`; `format_registry` is already at 22000). The +23% one_hour overshoot finding (`ONE_HOUR_WORD_OVERSHOOT_FINDING_20260615`) is a **different runtime_format** (`one_hour_book`, not `standard_book`) and is out of this lane.

### 2c. scene_anti_genericity = WARN (not blocking) on the real base

Both cells **WARN**, not FAIL. (The working-tree first pass FAILed because of drifted `golden_chapter_synthesis.py` scene injection; origin/main's reducer trims over-cap n-grams before the gate.) Devotion metrics: `chapters_below_3_details` and `repeated_location_count` within WARN tolerance. The thinner corporate_managers/burnout SCENE bank (30 variants, no `## ARC_POSITION` headers → degraded legacy prose-chunk path, 35 warnings) is a **content-density** observation for the F-COHERENCE/W2 lane, not a B2 blocker.

### 2d. ei_v2 = PASS, #1578 fitness stayed ADVISORY (confirmed)

`ei_v2` composite **0.65** (devotion) / **0.68** (cross-check), status **PASS**. The run_pipeline EI block blocks only at `composite < 0.55` (L1084) — both clear it. The #1578 T×E×F multi-objective fitness / Reader Council did **not** become ship-blocking: `ei_v2_report.json` carries no fitness/objective/council gating keys, and `quality_gate_failures` stayed `[]`. The #1578-era voice/dwell checks surface in **register_gate** as **F12 (voice-out-of-zone)** and **F13 (dwell-pacing)** at **FAIL** severity (never HARD_FAIL). **#1578 fitness is advisory exactly as the dispatch stated.**

### 2e. register_gate residual — the only HARD_FAIL, driven by a tiny F2

| cell | total | F1 (WARN) | **F2 (HARD_FAIL)** | F6 | F7 (WARN) | F12 (FAIL) | F13 (FAIL) |
|---|---|---|---|---|---|---|---|
| devotion | 59 | 30 | **3** | 1 | 12 | 7 | 6 |
| cross-check | 67 | 43 | **2** | 1 | 12 | 1 | 8 |

`_aggregate_verdict` (`register_gate.py:749`) returns **HARD_FAIL iff any F2** exists; F1/F4/F6/F7/F12/F13 max at FAIL and never escalate. So the entire HARD_FAIL hinges on **2–3 F2 findings** — see §4 for the defect-vs-calibration split.

**Delta vs the superseded (degraded) run:** superseded devotion F2 = **0** (on COMPRESSION substitutes); real-doctrine devotion F2 = **3**. The doctrine atoms introduce wrapper headings + a slot-template orphan that the substitute content did not — which is precisely why measuring on the real base matters and why the degraded run's "F2=0" verdict is not safe to act on.

---

## 3. Emission behavior — ROOT-CAUSED (exact control flow in `run_pipeline.py`)

The emit-vs-abort behavior is fully determined by three code regions. `book.txt` is written **before** the exit-code decision.

### 3a. Two genuine pre-render aborts (the only paths that suppress book.txt)

These fire **before any render**, only under `--quality-profile production`, and `raise SystemExit` (no book.txt):
- **Content-gap audit** (`run_pipeline.py` L699–712): any slot whose content starts with `[CONTENT GAP` → abort. **Did not fire** for either cell.
- **EXERCISE strict-canonical gate** (`_check_exercise_strict_canonical_gate`, L270/L715): EXERCISE slots falling through to `practice_library` under production → `SystemExit` (the book #3 / financial_anxiety failure class). **Did not fire** for either cell (their EXERCISE banks have practice-shaped survivors).

### 3b. book.txt is written, THEN gates run, THEN exit code is set

- `book.txt` is written at **L1459** (`book_path.write_text(_prose_out, ...)`), unconditionally inside `if args.render_book`.
- Quality gates run **after** that write and append to `_quality_gate_failures` (chapter_flow L939, ei_v2 L1084, editorial L1169, book_pass L1375, book_quality only when band==`Reject` at L374).
- **L1628**: `if _quality_gate_failures and (gates_hard or flagship): print("BLOCKED…"); return 1`. `gates_hard = (quality_profile == "production")` (L1859).

**Consequence:** in production, gate FAILs change the **exit code to 1** but the **book.txt is already on disk**. The §6 wording "emits no book.txt (gates hard-fail)" conflates *exit-1* with *no-emission* — they are different. On `aaebe0cdc4` both cells reach `_quality_gate_failures == []` → **exit 0**, so even that conflation does not bite here.

### 3c. book_quality band `Hold` does NOT block

Both cells land `book_quality` band **Hold** (`fail=0 hold=1`, "repeated phrase density above book cap"). Only band **`Reject`** appends to failures (`gates_hard and release_band == "Reject"`, L374). `Hold` is non-blocking by design → does not contribute to exit code.

### 3d. THE STRUCTURAL GAP — register_gate is NOT wired into run_pipeline

`grep register_gate scripts/run_pipeline.py` → **nothing.** register_gate (F1–F13; the **only** `HARD_FAIL`-severity gate, via F2) is a **separate CLI** (`python3 -m phoenix_v4.quality.register_gate`). Therefore **`run_pipeline --quality-profile production` emits a `book.txt` (exit 0) that register_gate would HARD_FAIL on F2** — proven by both cells (run_pipeline `[]`+emit+exit-0, register_gate HARD_FAIL). **The two verdicts are independent today. Closing that independence is the B2 contract.**

### 3e. register_gate verdict precedence (F2-only HARD_FAIL — confirmed)

`register_gate.py:749 _aggregate_verdict`: `HARD_FAIL` if any `severity=="HARD_FAIL"` (only F2 sets that) → else `FAIL` if any `FAIL` → else WARN-count tiering. **F2 is the sole ship-blocking severity**, matching devotion spec §6 ("register HARD_FAIL = never ship; contract gates on F2 not F1") and the gate's own docstring ("HARD_FAIL — any F2 violation; never ship").

---

## 4. Failure categorization (the W3 deliverable: defect / calibration / config)

Every remaining production-relevant failure, classified, with the owning lane.

### 4a. REAL DEFECTS (need a composer/atom/voice fix — sized in §5)

| # | Defect | Evidence (real base) | Class | Owner lane |
|---|---|---|---|---|
| D1 | **F2.D sub-4-word truncation orphans** | devotion ch6 `"Not the project"` (standalone para between two complete paras); cross-check ch3 `"Now we're"`, ch4 `"Start with the"` | COMPOSER (truncation-orphan family; COMPOSER_FRONTIER DEFECT 2 — `golden_chapter_synthesis.py` in-place phrase-cap shears sentence tails) | Pearl_Dev composer (W2/F-COHERENCE) |
| D2 | **Degraded SCENE assembly** (drives scene_gate WARN + some register findings) | corp_mgr/burnout SCENE bank: 30 variants, **0** `## ARC_POSITION` headers → 35× "no ARC blocks parsed … legacy prose-chunk path (degraded)" | CONTENT/DATA (SCENE bank shape) + composer fallback | Pearl_Editor (atom) + Pearl_Dev (composer) |
| D3 | **F1 templated-paragraph clusters** (30–43, WARN) + **F7 over-prescribed practice density** (12, WARN) + **F12/F13** (voice-zone / dwell, FAIL) | register findings, both cells | COMPOSER scaffolding-repetition (F-COHERENCE) + voice/dwell craft (#1578 family) | Pearl_Dev composer + Pearl_Editor (W2) |

**D1 is the only defect that touches the *ship-blocking* gate (F2).** D2/D3 are advisory under the proposed contract (they degrade quality but are not "never-ship" renderer breakage). Closing D1 (the ~1–2 orphans/book) is what flips register from HARD_FAIL to PASS.

### 4b. GATE CALIBRATION (flag — do NOT silently change; not a content fix)

| # | Finding | Evidence | Why calibration |
|---|---|---|---|
| C1 | **F2.B sentence-final-preposition false-positives** | devotion `"Let light be allowed in."`, `"a room she forgot she lived in."`; cross-check/working-tree `"Here's a practice to work with."` | These are **grammatical English** (valid imperatives / phrasal constructions). F2.B treats any sentence-final preposition as a dangling slot artifact. Inflates F2 → inflates HARD_FAIL. |
| C2 | **F2.C lowercase-known-noun-start on legitimate headings** (working-tree drift only; not present in origin/main F2 set) | `"the practice (as taught by Sai Maa)"` standalone heading flagged "template did not fill leading article" | Section-heading style, not a broken template. (Surfaced on the drifted working-tree register_gate at 15×; origin/main's register_gate.py does **not** emit these for this book — a reason the drifted-tree F2=23 was wrong.) |

**The COMPOSER_FRONTIER spec already named the F2.C lowercase false-positive and the wrapper-template ellipsis/dangling-prep tails.** C1/C2 are **flagged for Pearl_Architect**, not silently retuned — per the guardrail "real failures are real; never loosen a gate." If Pearl_Architect decides F2.B/F2.C over-trigger, the fix is a **calibration amendment to the register-gate spec** (tighten F2.B to true template artifacts, e.g. require an adjacent colon/empty-fill; exempt standalone heading lines from F2.C), tracked separately — NOT in this B2 lane.

### 4c. CONFIG (verify SSOT — reconcile only a real residual gap)

| # | Item | State on `aaebe0cdc4` | Action |
|---|---|---|---|
| G1 | `standard_book` word ceiling | `format_registry.yaml = [9000, 22000]` == duration SSOT `T5_standard 22000` | **Already reconciled. No change.** (The COMPOSER_FRONTIER 20000-vs-22000 conflict is closed.) |

**No config change is shipped in this lane** — the only candidate (word-budget) is already reconciled on the real base.

---

## 5. Sized path to production-passing devotion books (SCOPE — not the fix)

Ordered by leverage; effort in Pearl_Dev/Pearl_Editor days. The deliverable is this scope + the §6 contract; the multi-lane fix is **not** done here.

| Lane | Goal | What | Effort | Dependency | Flips which gate |
|---|---|---|---|---|---|
| **L0 — B2 contract ratify + wire** | make production's ship-verdict authoritative | Pearl_Architect ratifies §6 amendment; Pearl_Dev wires register_gate into run_pipeline as the F2 ship-block (§6.3) | **S** (~0.5 d wiring + ratify) | §6 amendment ratified | — (makes F2 the single emit-block) |
| **L1 — F2.D truncation-orphan fix** | clear the genuine F2 (→ register PASS) | COMPOSER_FRONTIER DEFECT 2: in `golden_chapter_synthesis.py` cap at **sentence granularity** (drop whole containing sentence, never bare substring) + purge lead/mid-clause fragments from the signature list + regression "no orphaned sub-4-word para survives" | **S–M** (~0.5 d) | none (independent) | **register HARD_FAIL → PASS** (removes the 1–2 real orphans) |
| **L2 — F2.B/F2.C calibration review** | stop inflating F2 with valid prose | Pearl_Architect decision + register-gate-spec calibration amendment (tighten F2.B to true template artifacts; exempt heading lines from F2.C). **Gate-spec lane, not B2.** | **S** (~0.5 d) | Pearl_Architect | reduces F2 false-positive count |
| **L3 — SCENE bank ARC-header + density (F-COHERENCE / W2)** | scene_gate WARN→PASS; reduce F1 | author/restructure corp_mgr-burnout-class SCENE banks with `## ARC_POSITION` headers; topic-aware `(topic,engine)` atom routing; bridge/transition de-dup (#1589/#1590/#1601) | **M–L** (the existing W2 lane; weeks across banks) | W2 lane | scene_gate WARN→PASS; F1/F7 down |
| **L4 — voice/dwell craft (F12/F13, #1578 family)** | raise register FAIL-tier toward clean | dwell-beat craft gate + voice-zone atom routing | **M** (multi-week craft) | #1578 follow-on | F12/F13 FAIL→advisory-clean |

**Critical-path to a production-passing devotion book = L0 + L1** (≈1 day of Pearl_Dev) — wire register_gate as the F2 ship-block, then clear the ~1–2 genuine truncation orphans so F2→0 and register→PASS. L2 hardens the signal; L3/L4 are the months-long quality frontier the dispatch said to **scope, not do**. **This is dramatically smaller than #1536's "81/0.53" implied** because the doctrine repair (#1700), #1701 SCENE/F2, and origin/main's composer/word-budget fixes already landed the bulk.

---

## 6. B2 RELEASE-PROFILE EMISSION CONTRACT (proposed — Pearl_Architect ratifies)

> **Proposed as an amendment to `PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` §5D and §9.
> Pearl_Architect ratifies (cap consideration in §7). This document does not self-ratify.**

### 6.1 Definitions

- **Emit** = write `book.txt` + the standard report bundle (`book_pass_report.json`, `chapter_flow_report.json`, `ei_v2_report.json`, `register_gate_report.json`, `budget.json`, `quality_summary.json`) to the render dir.
- **Ship-blocking gate** = a gate whose failure means the manuscript must NOT be emitted as a release artifact (exit non-zero, no `book.txt` promoted).
- **Advisory-with-threshold gate** = a gate that runs and is reported, may set a WARN/FAIL band and a non-zero *quality* score, but does **not** by itself block emission.

### 6.2 The contract (normative)

1. **Production emits a `book.txt` + report bundle whenever no ship-blocking failure exists.** The single ship-blocking condition is **register_gate verdict == HARD_FAIL (i.e. any F2 finding)**. F2 = broken slot-template/renderer artifacts a reader would see as breakage ("never ship", per the gate docstring and devotion §6).
2. **The pre-render `SystemExit` aborts remain ship-blocking** (content-gap audit; EXERCISE strict-canonical gate). These are genuine "the manuscript cannot be assembled" conditions and pre-date this contract; they continue to suppress emission.
3. **All other gates are advisory-with-threshold and do NOT block emission:**
   - `book_pass` (incl. `word_budget`) — advisory; report the FAIL/PASS and the count, but emit. (On `aaebe0cdc4` it PASSes anyway.)
   - `chapter_flow`, `ei_v2` (composite, incl. the `<0.55` line), `bestseller_craft`, `editorial`, `transformation`, `scene_anti_genericity`, `book_quality` band (`Hold`/`Reject`) — advisory.
   - register_gate **F1/F4/F6/F7/F11/F12/F13** (everything except F2) — advisory.
4. **Emission must be honest (hardening-spec §9):** the emitted `quality_summary.json` records, per gate, the band/score and whether it blocked. A book that emits with advisory FAILs is **labeled** (e.g. `release_eligible: false, blocking_reason: "register F2"` when F2 present; `release_eligible: true, advisories: [...]` when only advisories present). Never present an advisory-FAIL book as clean.
5. **`draft`/`debug` profiles:** emit unconditionally, no blocking (unchanged). `production`/`flagship` apply the blocking rule above.

### 6.3 Where the rule lives (the wiring, for L0)

- **Today:** the emit decision lives implicitly in `run_pipeline.py` (book.txt written at L1459; exit code at L1628 from `_quality_gate_failures`), and register_gate is a **disconnected** CLI. There is **no** single place that says "emit iff no F2."
- **Proposed:** add a **register_gate invocation inside `run_pipeline.py`** after the `book.txt` write, gated on `quality_profile in ("production","flagship")`. Its F2 verdict becomes the **one** ship-block: on HARD_FAIL, write the report bundle + a `release_eligible:false` marker and `return 1`; otherwise emit normally + `return 0`. `book_pass`/`chapter_flow`/`ei_v2`/etc. move to advisory (they populate `quality_summary.json` but no longer append to the blocking `_quality_gate_failures` set under this contract). This makes the implicit emit decision **explicit, single-sourced, and F2-gated** — closing §3d.
- **Guardrail:** wiring register_gate in is **not** loosening — it *adds* the only HARD_FAIL gate to the pipeline's own verdict. Moving `book_pass` etc. to advisory is a **contract decision** (they remain reported and remain hard in `flagship` if Pearl_Architect prefers); it does not delete any check.

### 6.4 Amendment text (paste-ready for §5D)

> **§5D addendum — B2 release-profile emission contract (2026-06-17, Pearl_Dev W3, base `aaebe0cdc4`).**
> Production emission is defined as: write `book.txt` + the report bundle whenever (a) neither pre-render abort fires (content-gap; EXERCISE strict-canonical) and (b) `register_gate` verdict ≠ HARD_FAIL. **register_gate F2 is the sole ship-blocking quality gate**; F1/F4/F6/F7/F11/F12/F13, `book_pass` (incl. `word_budget`), `chapter_flow`, `ei_v2`, `bestseller_craft`, `editorial`, `transformation`, `scene_anti_genericity`, and the `book_quality` band are **advisory-with-threshold** — run, reported in `quality_summary.json`, and may mark `release_eligible:false`, but do not suppress emission. register_gate is invoked from `run_pipeline.py` under `production`/`flagship` so the pipeline's own exit verdict equals the F2 ship-block (closing the current run_pipeline↔register_gate independence). No gate is loosened; advisory reclassification is a release-policy decision, and `flagship` may retain hard `book_pass` at the architect's discretion.

---

## 7. Does this need a Pearl_Architect cap amendment?

**Yes — a hardening-spec amendment, ratified by Pearl_Architect; this lane does not self-ratify** (per dispatch + `PEARL_ARCHITECT_STATE.md` entry "Pearl_Dev — decide the B2 release-profile emission contract … before any production-profile assembly run"). Specifically:
- **§5D amendment (§6.4 text)** — defines emit-vs-abort + the F2-only ship-block. Pearl_Architect ratifies.
- **L2 (F2.B/F2.C calibration)** — a **separate** register-gate-spec amendment; flag to Pearl_Architect, do not bundle into B2.
- **No `topic_engine_bindings.yaml` / canonical-spec / format_registry change** is implied (G1 already reconciled).

Routing if the architect wants it brokered: `Pearl_Operator_Proxy` per `docs/PEARL_OPERATOR_PROXY_SPEC.md`, logged to `artifacts/coordination/operator_decisions_log.tsv`.

---

## 8. Co-gate status for devotion §8 assembly (W4)

- **W3 (this lane):** the B2 contract is **drafted** (above) — production emits today; the ship-verdict is F2. **Once ratified + L0/L1 land, a *production* assembly run is contract-clean.** Until then, W4 may proceed on **`--quality-profile draft`** for coherence validation (draft ≡ production prose; only blocking differs), exactly as devotion §6 permits.
- **W2 (F-COHERENCE, #1589/#1590/#1601):** independent; still the gating quality lane for assembly (L3/L4 above map to it). Not in W3 scope.
- **Recommendation to W4/PM:** do not block the *draft* coherence proof on W3; do block a *production/release* run on **L0 ratify + L1 orphan fix** (≈1 Pearl_Dev day), at which point register→PASS for the measured cells.

---

## 9. Evidence index

- Authoritative build (devotion): `/tmp/w3_REALBASE_devotion/` — `book.txt` (21,654 w), `book_pass_report.json` (PASS), `register_gate_report.json` (HARD_FAIL, F2=3), `ei_v2_report.json` (0.65), `scene_gate/spine-burnout.json` (WARN), `stderr.log` (35× "no ARC blocks parsed").
- Cross-check build: `/tmp/w3_REALBASE_crosscheck/` — `book.txt` (21,673 w), book_pass PASS, register HARD_FAIL F2=2, ei_v2 0.68.
- Base proof: `git ls-tree -r 6d01afed99 | grep TEACHER_DOCTRINE` = **0**; `git ls-tree -r aaebe0cdc4 | grep TEACHER_DOCTRINE` = **12**; `git rev-list --parents -n1 aaebe0cdc4` → parent `6d01afed99`.
- Clean-tree proof: `/tmp/po_main_w3/{run_pipeline.py,register_gate.py,golden_chapter_synthesis.py,enrichment_select.py}` byte-equal to `aaebe0cdc4:<path>`.
- Drift proof (why working-tree runs are invalid): working branch 235/200 vs origin/main; pipeline files differ by +436/+572/+108/+186/+312 lines.

## 10. Anti-drift / guardrails honored

- Measured on clean `origin/main` `aaebe0cdc4` (real 12 doctrine atoms drawn — 90 refs verified), **not** #1536's stale numbers, **not** the drifted working tree, **not** the degraded `6d01afed99` superseded run.
- **No gate loosened.** F2 = real "never-ship"; the contract gates on F2, not F1. Calibration false-positives are **flagged to Pearl_Architect**, not silently retuned.
- Did **not** merge #1536; did **not** redo atom-header repair (#1590 family); did **not** run the W4 assembly; no paid API; no git worktree; commit via object-DB plumbing off `origin/main^{tree}`.
- Contract proposed as a §5D amendment — **Pearl_Architect ratifies**, not self-ratified.

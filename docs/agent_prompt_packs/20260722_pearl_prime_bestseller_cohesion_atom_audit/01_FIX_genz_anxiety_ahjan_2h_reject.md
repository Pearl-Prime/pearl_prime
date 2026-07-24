# Fix — genz_anxiety_ahjan_2h book REJECT (2 confirmed code bugs + 1 candidate gate false-negative)

EXECUTE. Do not summarize state, do not produce a plan-only response, do not stop
after any intermediate step. The turn ends ONLY on the MERGED-or-BLOCKED signal
below or one concrete BLOCKER with evidence.

## Context — this is root-caused, not speculative

The operator ran (from terminal, verbatim):
```
PYTHONPATH=. python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --teacher ahjan --pipeline-mode spine --runtime-format extended_book_2h \
  --quality-profile production --exercise-journeys --no-job-check --render-book \
  --render-dir artifacts/qa/genz_anxiety_ahjan_2h --seed flagship_phase2_layer6
```
Result: `book_quality_gate` REJECT (fail=1). An external tool (ChatGPT, no repo access) was
asked to diagnose this from the console log alone and produced a generic, speculative
read (guessed the content-bank warning meant "corporate manager scenes might be leaking
into the Gen Z book" — that is WRONG, verified below). Treat that external analysis as
background color only, not ground truth — it explicitly said it couldn't see the repo.
**This prompt is grounded in the actual artifacts at
`artifacts/qa/genz_anxiety_ahjan_2h/*.json` and the actual source at
`phoenix_v4/planning/enrichment_select.py` / `phoenix_v4/content_banks/loader.py`,
already read and root-caused below — do not re-diagnose from scratch, verify and fix.**

## PRE-REQUISITE CHECK

1. `git fetch origin && gh pr list --state open --search "content bank"` and
   `--search "teacher rotation"` and `--search "genz_anxiety_ahjan"` — stand down if a
   live PR already covers this.
2. Confirm the artifacts still exist at `artifacts/qa/genz_anxiety_ahjan_2h/` (local,
   gitignored render output — do not commit it; it's evidence for this turn only, not
   a golden/artifact to ship. If missing, re-run the exact command above first.)

## CONFIRMED FINDING A — teacher-atom picker has no within-book rotation (root cause of F1 + likely F6)

**Evidence:** `register_gate_report.json` shows 3 `F1` FAIL findings — "templated
paragraph cluster size 3" — each is the SAME teacher REFLECTION atom rendered
**verbatim, three times**, in the same 12-chapter book:
- Chapters 1, 5, 6 all contain `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/REFLECTION/ahjan_REFLECTION_002.yaml` verbatim.
- Chapters 2, 10, 11 all contain `ahjan_REFLECTION_001.yaml` verbatim.
- Chapters 3, 4, 7 all contain `ahjan_REFLECTION_000.yaml` verbatim.

There are **63 files** in `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/REFLECTION/`
(12 REFLECTION + ~51 TEACHING_*_mined), so this is not a thin-pool problem — it's a
selection problem: 9 of 12 chapters drew from only 3 distinct REFLECTION atoms.

**Root cause, confirmed by reading the code:** `_try_teacher_content()` in
`phoenix_v4/planning/enrichment_select.py` (~line 1201) picks via
`idx = _deterministic_index(f"{seed_key}:teacher", len(pool))` — a pure hash-of-seed
index with **no rotation/no-repeat-within-book tracking**. Contrast this with its
sibling picker for persona EXERCISE atoms in the SAME file (~line 2778, comment
`# OPD-109 Phase 3: rotation-aware least-used pick`), which uses
`_pick_primary_index_unseen(_persona_rotation, pool, seed, kind, _book_seen_bodies)`
specifically because "the same 1-3 practice atoms win every EXERCISE slot when the
teacher pool misses; rotation spreads picks across the pool." **The teacher-content
picker was never given this fix.** `_try_persona_content()` (~line 1230) has the same
gap.

**Fix:**
1. Give `_try_teacher_content()` (and `_try_persona_content()`) the same
   rotation-aware least-used selection already implemented for persona-EXERCISE
   (`_pick_primary_index_unseen` + a rotation-tracking object, following the OPD-109
   pattern in the same file). Reuse the existing rotation/dedup machinery — do not
   invent a second one (reuse-first, §9 of `docs/agent_brief.txt`).
2. Check whether `_book_seen_bodies` / an equivalent already-rendered-body registry is
   threaded through the teacher-content call sites; if the call sites for REFLECTION
   (and other teacher slot types) don't currently pass a per-book memory object, that
   plumbing is the actual gap — trace it before assuming a one-line index-picker swap
   is sufficient.
3. Regression test: a synthetic book render (or a focused unit test against
   `_try_teacher_content`) with a pool of ≥6 atoms and ≥6 same-slot-type picks across
   a book must select ≥4 distinct atoms (not repeat any atom until the pool is
   exhausted or near-exhausted), mirroring whatever test already covers the
   persona-EXERCISE rotation fix (find it — likely `tests/test_*rotation*` or
   `tests/test_*enrichment*dedup*` — and add a parallel case for teacher content).
4. After the fix, re-run the exact command above and confirm the 3 F1 findings are
   gone from `register_gate_report.json`, and check whether the F6 "pedagogical-cadence
   4-gram repeated 3+ times" finding also clears (it likely shares this root cause —
   verify, don't assume).

## CONFIRMED FINDING B — one malformed content bank silently disables ALL content-bank enrichment, catalog-wide

**Evidence:** console showed `Content bank registry unavailable:
/Users/ahjan/phoenix_omega/config/content_banks/anxiety_corporate_managers_scene_recognition_bank.yaml:
variant 'acmr_001' missing keys [...]`. This is **not specific to this book's
persona** (gen_z_professionals) — it is a warning that the ENTIRE registry failed to
load, for an unrelated persona's bank (corporate_managers), and it silently zeroes
out content-bank enrichment for every render in the process, not just corporate_managers
ones.

**Root cause, confirmed by reading the code:** `load_content_bank_registry()`
(`phoenix_v4/content_banks/loader.py`) eagerly loads and schema-validates **all 27**
files under `config/content_banks/` in one pass; `_validate_variant()` raises
`ContentBankSchemaError` on the first missing-key variant it finds anywhere. The
caller in `enrichment_select.py` (~line 2441-2445) catches this broadly and sets
`cb_reg = None`, i.e. **fail-open for the whole catalog on one bad file** — a schema
regression in any single persona's bank silently degrades content-bank enrichment for
every book, every persona, system-wide, with only a WARNING log line (not a hard
error, not surfaced in `quality_summary.json`).

Separately, `anxiety_corporate_managers_scene_recognition_bank.yaml` is authored to an
**old, pre-schema-hardening format** — its 40 variants have only `variant_id`,
`collision_family`, `body` (verified: none of the 40 variants have the other 14
required keys, e.g. `slot_type`, `topic_allowlist`, `band`, `ei_v2_targets`, etc., that
`anxiety_genz_scene_recognition_bank.yaml` — a sibling bank in current schema — does
have). This is a whole-file authoring gap, not a single typo.

**Fix (two independent pieces — do both, they address different failure classes):**
1. **Blast-radius fix (code, do first, higher priority):** make
   `load_content_bank_registry()` fail per-file, not per-registry — a malformed bank
   file should be skipped with a WARNING (bank excluded from `cb_reg.banks`, its
   variants unavailable) while every OTHER valid bank file still loads normally.
   Regression test: a registry directory fixture with one malformed + one valid file
   must load the valid one and report the malformed one as skipped, not return
   `None`/empty for everything.
2. **Content-authoring fix (data, can run in parallel, lower urgency since #1 bounds
   the damage):** either backfill the 14 missing keys on all 40
   `anxiety_corporate_managers_scene_recognition_bank.yaml` variants to match the
   current schema (`REQUIRED_VARIANT_KEYS` in `phoenix_v4/content_banks/loader.py`),
   using a sibling current-schema bank as the template, OR — if this bank is stale/
   superseded — mark it `status: retired`/move it out of `config/content_banks/`
   entirely per whatever retirement convention this repo uses for stale config
   (check `docs/DOCS_INDEX.md` / `CANONICAL_ARTIFACTS_REGISTRY.tsv` first; don't just
   delete). This is Pearl_Editor/Pearl_Writer authoring work — hand off separately if
   #1 already lands and unblocks the urgent case.

## CANDIDATE FINDING C — chapter 4 `MISSING_CLEAR_POINT`: verify gate precision before touching content

**Evidence:** `chapter_flow_report.json` shows chapter 4 `thesis_hits: 0` (every other
chapter shows 3-5). The detector (`_THESIS_CUES` in `phoenix_v4/quality/chapter_flow_gate.py`
~line 130) is a literal substring match against phrases like `"the point is"`,
`"is not the problem"`, `"is not a sign"`, `"is meant to"`.

Read Chapter 4 in `artifacts/qa/genz_anxiety_ahjan_2h/book.txt` (starts at line 196,
"What The Alarm Actually Does To Your Body" — Priya's presentation-anxiety scene). It
contains clear, well-formed thesis-shaped sentences —
e.g. *"None of this is metaphor. It is a budget, and every predicted disaster is a
withdrawal."* and *"Your hands shaking before a presentation is mobilization, not
malfunction."* — that read as a governing point but do not match any literal
`_THESIS_CUES` substring.

**Do not treat this as "the chapter needs a thesis added."** It may already have one
in different phrasing — a possible gate coverage gap, not a content gap. Per CLAUDE.md
§15 (precision-fix vs gate-weakening): decide which of these is true by actually
reading the chapter against the full book's editorial intent, then:
- If the chapter genuinely lacks a governing point (the scene is vivid but doesn't
  resolve to one claim) → this is a real content fix, Pearl_Editor/Pearl_Writer
  territory, rebuild around one transformation claim (do NOT just insert a sentence
  containing a cue phrase to game the detector).
- If the chapter has a real thesis in non-matching phrasing → this is a PROVABLE
  false-negative class (the cue list is substring-only and this book's teacher voice
  legitimately phrases theses differently, same class as the `ws_flow_glue_selector_cap_enforcement_20260517`
  expansion already in this cue list's history) → add the specific matching
  pattern(s) to `_THESIS_CUES` (or `_ZH_THESIS_CUES` sibling if relevant) with a
  regression test proving (a) this chapter now passes and (b) a synthetic chapter with
  NO governing point at all still correctly FAILs. Never widen the cue list to the
  point where a thesis-free chapter would pass.
- Do not decide this alone if it's ambiguous — if after reading the chapter you are
  genuinely unsure whether it has a governing point, surface `Q-AUDIT-CH4-THESIS-01`
  with your read and a recommended default rather than silently picking one.

## Verification (required before landing)

Re-run the exact operator command from Context above after A + B(1) land (C may land
separately/later if it needs an operator answer). Confirm in the fresh
`artifacts/qa/genz_anxiety_ahjan_2h/` output:
- `register_gate_report.json`: F1 findings gone (or materially reduced — report exact
  count), F6 re-checked.
- `Content bank registry unavailable` warning gone from console output (assuming the
  corporate_managers bank issue is either fixed or now correctly skipped-not-fatal).
- `book_quality_gate`: report whatever the new verdict is — PASS, or still Reject with
  updated `fail_reasons`. **Label the result on the 4-layer acceptance taxonomy
  (`docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`) — a book_quality PASS is at
  most `structurally clear`, never call it "bestseller" or "shippable."**

## DO NOT

- Do not hand-edit the rendered `book.txt` to patch over these findings — fix the
  selector/loader/gate, then re-render from scratch. A hand-patched artifact is not
  reproducible and hides the real defect from the next render.
- Do not weaken `_THESIS_CUES` or any register_gate threshold just to make this one
  book pass — CLAUDE.md's explicit anti-pattern. Fix must generalize and pass a
  regression test proving real violations still fail (§15 of `docs/agent_brief.txt`).
- Do not conflate Finding B's code fix (bounding blast radius) with the content
  authoring backfill — they're different owners/urgency; land the code fix first.
- Do not commit anything under `artifacts/qa/genz_anxiety_ahjan_2h/` — it's gitignored
  local QA evidence, not a golden/shipped artifact.

## Landing

- **(a) MERGED** — PR with the rotation-aware teacher-content fix (Finding A), the
  per-file-fail-safe content bank loader fix (Finding B.1), regression tests for both,
  and Finding C's resolution (either a chapter content fix or a precision-fixed cue
  list with regression test, or a surfaced `Q-AUDIT-CH4-THESIS-01` if genuinely
  ambiguous) — required checks green, squash-merged.
  Signal: `genz-anxiety-ahjan-2h-fix-20260722=<full-merge-SHA>`.
- **(b) BLOCKED** — concrete blocker, work pushed to a remote branch.

Finding B.2 (the 40-variant content-authoring backfill) may land as a separate,
later PR/spawned task if it's out of scope for this turn — declare that explicitly
rather than silently dropping it.

## CLOSEOUT_RECEIPT (required, exact)

```
CLOSEOUT_RECEIPT
lane: genz-anxiety-ahjan-2h-fix-20260722
signal: genz-anxiety-ahjan-2h-fix-20260722=<full-SHA-or-BLOCKED>
state: MERGED | BLOCKED
finding_a_teacher_rotation: <fixed/blocked + regression test path>
finding_b1_loader_blast_radius: <fixed/blocked + regression test path>
finding_b2_content_backfill: <landed-this-turn | spawned-separately | not-started + why>
finding_c_ch4_thesis: <content-fixed | gate-precision-fixed | Q-AUDIT-CH4-THESIS-01 open>
reverify_render: <book_quality verdict + acceptance layer label, or "not re-run" + why>
evidence_paths: <every report path cited>
cleanup_ledger: <worktree/branch/scratch state>
next_action: <specific enough for a cold-start agent to resume>
```

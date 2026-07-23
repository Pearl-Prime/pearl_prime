# Session Handoff — zh-TW First Book → Waystream 100-Book QA Pack (2026-07-23)

**Repo:** `Pearl-Prime/pearl_prime` · **`origin/main` at handoff = `a3bcd69e3d15410093c4ccb4823f7f39e7a4697d`**
**Branch this session worked on:** `agent/bestseller-atom-flow-lanes-20260721` (pre-existing branch with a large
pile of unrelated dirty binary/LFS files at session start — not touched; only explicit new paths were staged)
**Session type:** Piper (prompt-router) — authored prompts and a prompt pack, did not execute pipeline builds
itself. No atoms, no pipeline code, no EPUBs were produced by this session.
**SSOT:** `docs/PROGRAM_STATE.md` — NOT updated by this session (nothing here reached a milestone-merge yet;
next session should update it once Wave 0/1 of the pack below actually lands).

---

## 0. The single most important clarification this session

**Zero zh-TW Waystream books currently complete the production pipeline.** Every "coverage %" number in
memory or `docs/PROGRAM_STATE.md` (zh-TW ~96%, or an older memory's 99.87%) measures **file-existence**, not
**usable content** — this was already known going in, but this session found the sharper, more current version
of that fact: a live PR (#211) already tried to build book #1 and hit a **confirmed cell-independent** pipeline
bug, unrelated to atom content quality at all. See §2.

## 1. What this session actually did (chronological)

1. **First ask:** "create a Taiwan (zh-TW) language book from the pipeline, get a trace on it, analyze the atom
   bank first, make sure there are enough atoms." Read the full Piper read-path (`docs/agent_brief.txt`,
   `docs/PROGRAM_STATE.md`, `docs/SESSION_UNITY_PROTOCOL.md`, coordination TSVs), then found and read
   `artifacts/qa/atom_corruption_scope_20260722.md` — a same-day, block-level classifier audit finding **35% of
   5,279 zh-TW atom files corrupted** (raw LLM chat commentary, untranslated English bodies, empty stubs), root-
   caused to 3 incidents including one commit whose own subject line said "do-NOT-merge" and got merged anyway.
   Authored a single paste-ready prompt: pick a zh-TW-clean, tuple-viable cell via live cross-reference (not
   trusted coverage %), build via the four-piece chord + `--locale zh-TW`, treat the pipeline's own
   `locale_fallback_report.py` gate as the sufficiency proof, capture `assembly_trace.md` as "the trace."
2. **Operator correction:** flagged that the prompt's snapshot was already stale — by the time it was drafted, a
   same-session cleanup wave had landed: 872 contamination-glyph fixes, all 14 name-conversion families, 909
   files retranslated from clean English source, plus a consolidated 863-row EN-authoring backlog (PR #162)
   superseding the old 650-row file. **Verified all of it live** (not taken on faith): PR #162 merged (864-line
   TSV present at `origin/main`), 6/6 contamination batches merged, 14/14 name-conversion PRs merged, 4/4
   retranslation-consolidation PRs (#152-#155) merged. Corrected the prompt accordingly — also found, spot-
   checking the fix, that `gen_z_professionals × anxiety` (the English flagship cell) is **still** not fully
   clean post-cleanup (8/49 files, a new `KNOWN_FILLER_REUSE` defect class), so the "don't default to the
   English flagship" caution held for a different, current reason.
3. **Second ask:** "make 100 zh-tw books of all sorts for waystream sanctuaries brand in zh-TW, even though it's
   an eng brand, for QA, use pipeline." Before authoring anything, ran `gh pr list` deconfliction and found **PR
   #211 already exists** — someone had already dispatched a version of the single-book prompt above. Read it in
   full: see §2. Because zero books currently ship, a flat 100-way fan-out was rejected in favor of a sequenced
   pack (Wave 0 unblock → Wave 1 smoke → Wave 2 pilot → Wave 3 scale). Also confirmed live that Waystream's
   catalog uses exactly **10 personas** (not all 14) — `corporate_managers, entrepreneurs, first_responders,
   gen_alpha_students, gen_x_sandwich, gen_z_professionals, healthcare_rns, millennial_women_professionals,
   tech_finance_burnout, working_parents` — ~80 cells each, 800 total.
4. **Authored and committed the pack** (this session's only write to the repo): see §3.

## 2. Live PR state at handoff — read these before doing anything else

| PR | Title | State | What it means for this program |
|---|---|---|---|
| **#211** | first zh-TW book attempt — cell selected, build BLOCKED | OPEN, docs-only | Diagnosed the blocker below on `gen_z_professionals × overthinking × spiral`; confirmed cell-independent by reproducing on a second, unrelated cell. This PR's own diagnosis is the authority for Wave 1 — do not re-diagnose from scratch. |
| **#223** | locale-aware EXERCISE practice-atom classifier | OPEN, code fix, NOT merged | Fixes `_is_practice_atom` (`phoenix_v4/planning/enrichment_select.py`), which was classifying EXERCISE atoms by **English-only substring match** — every faithfully-translated zh-TW EXERCISE atom was misclassified as non-practice and fell through to the shared English `practice_library`, tripping `EXERCISE-BANK-RESOLUTION-01`. Fix is written, tested (7/7 new tests, 681/682 in a 65-file regression sweep), and verified via a real rebuild that clears the gate on the same cell. **Its required checks are currently red for a reason it does not own** — see #131. |
| **#131** | author real zh-CN prose for compassion_fatigue stub blocks | OPEN, NOT merged | Unrelated pre-existing issue: 4 zh-CN stub files trip `test_parse_sweep_is_green_tree_wide`, which is **red on `origin/main` itself** right now, and therefore also red on #223 (which branched from a main that already had this problem). This is the actual gate on #223 merging. Verified by pulling #223's own CI log — the failure is byte-identical to what #223's PR body already disclosed, not a new regression. |

**Even after #223 merges**, the same PR #211 cell hits a **further, unfixed** gate afterward — an
accent-planner supply gap for `AUTHOR_DISCLOSURE` (per #223's own PR body, "carrying the cell further ... remains
Pearl_Localization's lane on PR #211, not this PR's scope"). Nobody has fixed this yet. This is Wave 1's real work,
not just a landing exercise.

**Re-verify all three PR states before acting** — this program moved several PRs/hour on 2026-07-22/23; by the
time you read this they may already be merged, in which case the corresponding pack wave is done, not blocked.

## 3. What's committed (this session)

- **Commit `cd70b60924`** on `agent/bestseller-atom-flow-lanes-20260721` (**local only — NOT pushed to origin**):
  `docs/agent_prompt_packs/20260723_waystream_zhtw_100_books/` — 6 files, 804 insertions, docs-only:
  - `INDEX.md` — program goal, wave order, lane matrix, deconfliction notes, evidence/cleanup requirements
  - `00_MASTER_DISPATCH_PROMPT.md` — the paste-ready dispatcher prompt (**paste this to start**)
  - `01_Pearl_GitHub_prereq_unblock.md` — Wave 0: land #131 → verify #223 green → merge #223
  - `02_Pearl_Localization_smoke_first_ship.md` — Wave 1: ship the PR #211 cell end-to-end (incl. the
    AUTHOR_DISCLOSURE gap), supersede/close #211
  - `03_Pearl_Localization_pilot_10.md` — Wave 2: 9 more diverse cells, 1 PR
  - `04_Pearl_Localization_scale_batches.md` — Wave 3: 6 parallel batches (~15 cells each) covering all 10
    Waystream personas, to reach 100 total (persona/target table included; Batch F is an explicit flex/backfill
    slot, not a fixed pair, since exact clean-cell yield per persona isn't knowable until live at dispatch time)
- **This doc.**
- **Nothing else was written or modified.** No atoms, no pipeline code, no EPUBs, no PROGRAM_STATE.md edit (there
  is no milestone yet to reflect).

**Decision point for next session / operator:** push `cd70b60924` and open a docs-only PR (matches the #211/#93
precedent of docs-only diagnostic/pack PRs merging cleanly), or leave it local and let the executing dispatcher
commit it as part of Wave 0. Not yet done — deliberately left as an open choice rather than acted on unprompted.

## 4. Standing lessons from this session

- **File-existence coverage % is a recurring false signal for zh-TW** (and likely other CJK locales) — this is
  now the second time in this program alone (the 07-22 corruption scan, then PR #93's register-bucket triage)
  that a "coverage" metric turned out to be measuring the wrong thing. Always cross-reference the CURRENT
  authoring-backlog TSV (path-keyed), never a percentage, before picking a cell.
- **This program moves fast — hours, not days.** Between this session's two asks, a full cleanup wave (contamination
  + name-conversion + retranslation, ~15 PRs) landed and superseded the router's own first-draft snapshot. Any
  prompt or handoff (including this one) is stale on arrival; every gate check must be re-run live, never trusted
  from a prior turn's numbers.
- **A pipeline bug can masquerade as a content problem.** The EXERCISE-BANK-RESOLUTION-01 failure looked, at first
  glance, like "not enough clean zh-TW atoms" — it was actually a locale-blind classifier bug that would have
  blocked *every* cell, clean or not. Confirming cell-independence (reproduce on a second, unrelated cell) before
  assuming a gate failure is cell-specific saved this program from an expensive misdiagnosis loop.
- **register_gate PASS is never "bestseller" or "done."** Every book this pack ships is at most Layer 1
  ("structurally clear") — reinforced explicitly in every lane file's DO NOT section, because a 100-book batch is
  exactly the scale at which "PASS" starts getting rounded up to "shipped a catalog" in casual reporting.
- **Waystream's real persona scope is 10, not 14** — `nyc_executives`, `educators`, `midlife_women`,
  `gen_z_student` have zh-TW atoms in the wider bank but are NOT in the Waystream catalog. Don't assume brand
  scope from the atom bank; verify against the actual catalog file listing.

## 5. Open lanes / NEXT_ACTION (priority order)

1. **Paste `docs/agent_prompt_packs/20260723_waystream_zhtw_100_books/00_MASTER_DISPATCH_PROMPT.md` into a lead
   agent.** This is the single next action — it reads the INDEX and dispatches Wave 0 first.
2. **Wave 0 (prereq unblock)** cannot be skipped or parallelized ahead of Wave 1 — re-check #131/#223/#211 state
   first, since they may have already merged since this doc was written (§2's re-verify note).
3. **Wave 1 (smoke)** is the load-bearing lane — it has to actually resolve the AUTHOR_DISCLOSURE accent-planner
   gap, not just re-confirm the EXERCISE fix. If that gap turns out to be another locale-blind classifier (same
   shape as the EXERCISE bug), expect a second narrow code-fix PR before Wave 1 can close.
4. **Decide on pushing `cd70b60924`** (§3) — currently local-only on this branch.
5. **Once Wave 3 completes:** update `docs/PROGRAM_STATE.md` Localization section with the real shipped count
   (out of the 100 target) — do not round up if fewer actually cleared gates.

**Reality line:** this session produced a routing artifact (a prompt pack), not a shipped book. The zh-TW
Waystream program is still pre-smoke-test as of this handoff — the very first real zh-TW EPUB for this brand has
not yet been produced by anyone.

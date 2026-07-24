# First zh-TW Pearl Prime Book — TRACE_SUMMARY

**Lane:** PRJ-ZHTW-FIRST-BOOK-20260723 · **Agent:** Pearl_Localization · **Date:** 2026-07-23
**Base:** `origin/main` @ `14cd6aac5a`
**Status:** BLOCKED (infrastructure gate, cell-independent — see root cause below)

## Plain-English summary

The goal was to ship the first real zh-TW Pearl Prime EPUB, picking a (persona ×
topic) cell that clears the current 863-row zh-TW authoring backlog and is
structurally viable, then running the mandatory four-piece-chord production build
(`--pipeline-mode spine --quality-profile production --exercise-journeys --locale
zh-TW`). Cell selection succeeded — `gen_z_professionals × overthinking × spiral`
is zh-TW-clean and tuple-viable. The production build itself hard-fails, but not
on the locale-fallback honesty gate the task anticipated. It fails on a
**different, pre-existing production gate (`EXERCISE-BANK-RESOLUTION-01`) that is
English-only under the hood** — its practice-atom classifier (`_is_practice_atom`
in `phoenix_v4/planning/enrichment_select.py`) tests content against a tuple of
English substrings (`"notice the "`, `"feel the "`, `"step 1"`, …) and an
English-numbered-list regex. Real, clean, human-quality zh-TW EXERCISE atoms
(confirmed present and NOT in the authoring backlog) contain none of those
English tokens, so every zh-TW EXERCISE atom is classified as "not
practice-shaped," the resolver falls through to the shared English
`practice_library` for all 12 chapters, and the production gate — designed to
catch *thin* per-cell coverage — fires because it cannot distinguish
"thin" from "legitimately non-English." This reproduced identically on a second,
unrelated persona/topic/engine (`corporate_managers × adhd_focus × overwhelm`),
confirming the failure is **cell-independent**: no re-pick of persona/topic can
route around it, because the classifier itself has no CJK-aware path. This is a
genuine infrastructure gap, out of this lane's scope to fix (no atom authoring,
no pipeline-code changes authorized under this task's WRITE_SCOPE), and is
reported here as the concrete BLOCKER.

## Step 1 — Cell selection (completed)

Source of truth: `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv`
(863 rows, PR #162, MERGED 2026-07-23T00:29:06Z) — re-verified as current; no
newer consolidation exists (checked `git log` on the backlog file pattern +
PR #191 "zh-TW quality program complete — full closeout," merged
2026-07-23T01:15:23Z same day, which explicitly names this 863-row file as the
remaining real work).

### Candidates evaluated and rejected (with reason)

| Cell | zh-TW backlog hits | Structural check | Verdict |
|---|---|---|---|
| `nyc_executives × burnout × overwhelm` | 0 (clean) | English **SCENE** bank folder does not exist at all for this topic (`atoms/nyc_executives/burnout/SCENE/` missing) — a pre-existing EN-source gap, not a translation gap | REJECTED (structural, EN-source) |
| `nyc_executives × anxiety × {false_alarm,watcher}` | 3 (COMPRESSION, REFLECTION — both load-bearing F006 slots — + 1 engine-specific) | `check_tuple_viability.py` PASS | REJECTED (zh-TW dirty on core slots regardless of engine) |
| `gen_z_student × anxiety` (all 7 engines) | 0 (clean) | `check_tuple_viability.py`: `POOL_TOO_SHALLOW: 9 < 12` on every engine/format combo | REJECTED (structural — persona-wide thin STORY pool) |
| `gen_z_student × burnout` (all 7 engines) | 0 (clean) | Mix of `BAND_DEFICIT` / `NO_BINDING` / `POOL_TOO_SHALLOW` on every combo | REJECTED (structural) |
| `midlife_women × anxiety` (all 7 engines) | 0 (clean) | `BAND_DEFICIT: missing band 5` on every engine at F006 | REJECTED (structural) |
| `midlife_women × boundaries` (4 engines) | 0 (clean) | `BAND_DEFICIT: missing band 5` on every engine | REJECTED (structural) |
| `gen_z_professionals × sleep_anxiety` | 0 on {watcher, comparison, grief, shame}; 3 dirty on {false_alarm, overwhelm, spiral} | The zh-TW-clean engines all fail `NO_BINDING`/`BAND_DEFICIT`; the tuple-viable engines are the dirty ones | REJECTED (clean ∩ viable is empty) |
| `corporate_managers × {adhd_focus, mindfulness} × {overwhelm, shame, comparison}` | 0 (clean) | `check_tuple_viability.py` PASS on all 6 combos | VIABLE runner-up — no existing Waystream book-plan listing for these topics (Waystream's 15-topic set doesn't include adhd_focus/mindfulness) |
| **`gen_z_professionals × overthinking × spiral`, F006** | **0 (clean — verified against all core F006 slot types + the `spiral` engine bank specifically)** | `check_tuple_viability.py` → **TUPLE_VIABLE**. Real Waystream listing already exists: `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__default_teacher__gen_z_professionals__overthinking__spiral.yaml` | **SELECTED** |

### Why this cell

- **English precedent:** `gen_z_professionals` is the flagship persona
  (`gen_z_professionals × anxiety` is the program's one PROVEN-AT-BAR book,
  operator Layer-4 approved). `overthinking` is a different topic on the same
  persona, giving the strongest available cross-validation among zh-TW-clean,
  tuple-viable candidates (no clean+viable cell existed with a register-PASS
  precedent on the *exact* same topic).
- **Brand:** Waystream (`way_stream_sanctuary`), matching the existing
  real-EPUB convention (Q-ZHTW-BOOK-BRAND-01 default) — and a listing for
  this exact persona×topic×engine cell already exists under that brand.
- **Alternative considered and rejected:** `corporate_managers ×
  {adhd_focus, mindfulness}` — equally zh-TW-clean and tuple-viable, and
  `corporate_managers` has the single strongest EN precedent in the whole
  catalog (the *first* gate-passing Waystream EPUB, `corporate_managers ×
  burnout × overwhelm`) — but adhd_focus/mindfulness are outside Waystream's
  15-topic set and have no existing listing, so `gen_z_professionals ×
  overthinking × spiral` was preferred as the cleaner Waystream-native fit.

## Step 2 — Production build (BLOCKED)

Command run (four-piece chord + locale, exactly as specified):

```
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic overthinking --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__overthinking__spiral__F006.yaml \
  --pipeline-mode spine --quality-profile production --exercise-journeys \
  --locale zh-TW --runtime-format standard_book \
  --no-job-check --render-book \
  --render-dir artifacts/qa/zhtw_first_book_20260723/
```

Result: hard `SystemExit` —

```
[PRODUCTION GATE] EXERCISE-BANK-RESOLUTION-01 strict-canonical: 12 EXERCISE
slot(s) resolved via practice_library fall-through. Production must resolve
EXERCISE from teacher_banks/approved_atoms/EXERCISE or persona-atom EXERCISE
bank. Add atoms upstream (Pearl_Editor + Pearl_Writer ws), or use
--quality-profile draft/debug to allow practice_library fall-through during
development.
```

Full log: `build_attempt2_gen_z_professionals_overthinking_spiral_zhTW_FAILED_exercise_gate.log`

**This is NOT the locale-fallback honesty gate** (`phoenix_v4/rendering/locale_fallback_report.py`)
that the task anticipated as the likely failure mode. That gate never ran to
completion because `EXERCISE-BANK-RESOLUTION-01` (`scripts/run_pipeline.py`
`_check_exercise_strict_canonical_gate`, landed in PR #912 /
`755b05d6f5`) fires first and hard-exits.

### Root-cause diagnosis (verified, not guessed)

1. `phoenix_v4/planning/registry_resolver.py::_load_persona_atoms` **is**
   locale-threaded (probes `locales/{locale}/CANONICAL.txt` before falling
   back to English) — confirmed by reading the function and its docstring.
   So with `--locale zh-TW`, the EXERCISE slot-fill path correctly loads
   `atoms/gen_z_professionals/overthinking/EXERCISE/locales/zh-TW/CANONICAL.txt`,
   which is real, clean, human-quality translated content (sample: "停下來。你的思緒正飛向未來。說出三件你現在看得見的東西...").
2. That pool is then filtered by `_filter_practice_pool` →
   `_is_practice_atom` (`phoenix_v4/planning/enrichment_select.py:1559-1614`).
   The positive-evidence check is either (a) a numbered-list regex
   (`_NUMBERED_STEP_RE`, expects `"1."`/`"1)"`-style lines) or (b) a
   membership test against `_PRACTICE_STEP_MARKERS` — a tuple of **44
   English-language substrings** (`"inhale"`, `"notice the "`, `"feel the
   "`, `"step 1"`, `"close your eyes"`, …). Chinese-language content
   structurally cannot contain any of these English tokens.
3. Result: **every** zh-TW EXERCISE atom — regardless of how well it is
   translated — is classified `not practice-shaped` and rejected. All 12
   chapters fall through to the shared English `practice_library`, and
   `EXERCISE-BANK-RESOLUTION-01` correctly (by its own logic) detects 12
   unbound `practice_library` slots and hard-exits, because from its point
   of view zero per-cell EXERCISE atoms resolved.
4. **Confirmed cell-independent:** an English-only control run of the exact
   same cell (no `--locale` flag) got past this gate cleanly
   (`slots_from_practice_library=0`, `slots_from_persona=84` in
   `enrichment_audit.json`) and proceeded all the way to `register_gate`
   (see `control_attempt3_..._ENGLISH_control.log`). A second, unrelated
   cell — `corporate_managers × adhd_focus × overwhelm`, also zh-TW-clean
   and tuple-viable — reproduced the **identical** 12/12 fallthrough and
   hard-exit under `--locale zh-TW`
   (`control_attempt4_corporate_managers_adhd_focus_overwhelm_zhTW_universal_confirm.log`).
   This rules out a cell-selection mistake: the gap is in the shared
   classifier, not in any one persona/topic's atom bank.
5. A `--teacher ahjan --teacher-attribution generalized` attempt did not
   change the outcome (identical log, `teacher_atoms` path did not visibly
   engage) — teacher banks are also English-only content, so this would not
   have been a real fix even if it had engaged.

### Why this was not routed around

Per the task's DO-NOT list: never bypass, weaken, or catch-and-ignore a
production gate to force a build through, and never author atom content in
this lane. `EXERCISE-BANK-RESOLUTION-01` is a real, intentional,
well-tested gate (7 unit tests, `tests/test_exercise_strict_canonical.py`)
protecting against genuinely thin per-cell EXERCISE coverage — the fix
belongs in the classifier (`_is_practice_atom` needs a CJK-aware positive-evidence
path, e.g. metadata-driven `slot_type: exercise` tagging at authoring time, or
locale-specific marker sets), which is pipeline code outside this task's
WRITE_SCOPE (`artifacts/`, `ACTIVE_WORKSTREAMS.tsv`, `PROGRAM_STATE.md` only)
and outside Pearl_Localization's authority (this is Pearl_Dev / Pearl_Prime
composer territory). Weakening or monkey-patching the gate to force a zh-TW
EPUB through would ship a book that *looks* localized while its EXERCISE
chapters are silently English underneath in every future zh-TW render —
exactly the "gate PASS ≠ real" failure mode CLAUDE.md's Bestseller Anti-Drift
Doctrine and this task's own DO-NOT list exist to prevent.

## Evidence artifacts (this directory)

- `build_attempt1_nyc_executives_burnout_overwhelm_FAILED_scene_bank_missing.log`
- `build_attempt2_gen_z_professionals_overthinking_spiral_zhTW_FAILED_exercise_gate.log`
- `control_attempt3_gen_z_professionals_overthinking_spiral_ENGLISH_control.log`
- `control_attempt4_corporate_managers_adhd_focus_overwhelm_zhTW_universal_confirm.log`
- `scan_step1_cell_candidates.py` / `scan_step2_engine_level_candidates.py` —
  the cell-selection scans run against the live 863-row backlog + atom tree.

No `locale_fallback_report.json` / `enrichment_audit.json` (full) /
`register_gate` output exist for a *completed* zh-TW render because the build
never reached those stages under production profile — the `enrichment_audit.json`
referenced above (`slots_from_practice_library=0` etc.) is from the **English
control** run only, included as diagnostic evidence, not as a zh-TW artifact.

## Recommendation for next session

Fix belongs to Pearl_Dev/Pearl_Prime: extend
`_is_practice_atom` (`phoenix_v4/planning/enrichment_select.py:1559`) with a
locale-aware or metadata-driven positive-evidence path so legitimately
translated, human-quality CJK EXERCISE atoms are not universally rejected.
Once fixed, `gen_z_professionals × overthinking × spiral` (this lane's
selected cell — zh-TW-clean, tuple-viable, real Waystream listing already
exists) is ready to re-attempt with no further cell-selection work needed.

## Addendum — secondary, unrelated CI blocker discovered while landing this PR

While opening PR #211 for this docs-only change, the repo-wide **required**
`parse-sweep` status check (`config/governance/required_checks.yaml` —
`always_required: ["Verify governance", "parse-sweep"]`) was found **red on
`origin/main` itself**, on every push since `2026-07-23T00:58:40Z` (verified via
`gh run list --workflow="Atoms parse sweep" --branch main`), independent of this
PR. Cause: 4 new zh-CN `NEW STUB CONTENT` regressions in
`atoms/{corporate_managers,entrepreneurs}/compassion_fatigue/{grief,overwhelm,watcher}/locales/zh-CN/CANONICAL.txt`
(the "PR #1590 failure class" the check itself names). This blocks merging
**any** PR to `main` right now, not specific to this lane. A fix is already
in flight and unmerged: PR #131 (`fix(atoms): author real zh-CN prose for
compassion_fatigue stub blocks (PR #1590 failure class)`) and PR #208
(`fix(zh-cn): author missing gen_x_sandwich compassion_fatigue EN source
variants`) — PR #131's own branch reports `parse-sweep: SUCCESS`, confirming
the fix. Not fixed here: it is zh-CN atom-authoring, outside this lane's
zh-TW / no-atom-authoring scope, and duplicating in-flight work risks
conflicting with those two open PRs. This PR (#211) will be mergeable once
#131 or #208 lands on `main`.

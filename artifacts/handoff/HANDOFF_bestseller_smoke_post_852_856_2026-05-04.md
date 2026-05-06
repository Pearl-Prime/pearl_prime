# HANDOFF — Bestseller Smoke Verification Session

**Date:** 2026-05-04
**Operator brief:** "merge #852 + #856, run bestseller smoke at compact_book_8ch_30min, ship artifact PR"
**Worktree:** `/Users/ahjan/phoenix_omega/.claude/worktrees/nervous-banzai-1af281`
**Session outcome:** Directive executed end-to-end. Smoke result: **REJECT** with 3-finding diagnosis. Artifact PR open.

---

## TL;DR (read this first)

1. **PR #856 merged this session.** Squash SHA `37edc4375c` on `origin/main`.
2. **PR #852 was already on main** at session start (squash `dcc5fad25a`). No action needed.
3. **Smoke verification ran** against the post-merge `origin/main`. Result: **REJECT** — pipeline exit 1 at `quality_gate`, did not reach `prose_render`.
4. **Artifact PR #858 opened** with full diagnosis and next-cycle scope. No production code touched. Iteration cap held at 0.
5. **Two next-cycle PRs scoped**, neither stacked: a small engineering wiring PR and a medium content backfill PR.

**The single most important finding:** PR #856 added `compact_book_8ch_30min` to the format registry but did **not** wire it into the auto-plan generator's hardcoded chapter-count lookup. The format declaration is **not authoritative** for the auto-plan path — the registry's `chapter_count_default: 8` is silently overridden by a fallback default. This is a single-source-of-truth violation introduced by #856 and should land as a small follow-up PR before any further compact-format work.

---

## What was on the table (operator directive recap)

The session-opening directive was a tight 9-section brief covering three concurrent streams:

| Stream | This session's scope |
|---|---|
| **Book pipeline (bestseller pass)** | Merge #852 + #856, run smoke verification, ship artifact PR |
| Cover quality (#855, #857) | NOT TOUCHED — separate branch chain, awaiting operator review |
| Pearl News (#850, #853) | NOT TOUCHED — separate branch chain, awaiting operator visual sign-off |

Memory entry [`feedback_validation_before_scaling`](https://github.com) governed the approach: do not stack/cherry-pick on uncertain APIs; gate scaling on validator output, not vibes.

---

## What I did

### Step 1 — PR state check
Found PR #852 was already merged (squash `dcc5fad25a` was the first commit visible from session start). PR #856 was open, mergeable, and all CI green except the documented Cloudflare `pearl-prime` worker-build exception (per directive: "If #856's CI shows red on anything other than the Cloudflare pearl-prime check, stop and surface — don't override.")

Diff sizes verified rule-0 clean:
- #852: +1447 / -0 / 12 files
- #856: +96 / -0 / 4 files

### Step 2 — Merged PR #856
```bash
gh pr merge 856 --squash --delete-branch
```
Local branch deletion failed (worktree `nifty-kilby-6e8968` has it checked out) but the remote merge succeeded. Verified via `gh pr view 856`: `mergedAt: 2026-05-04T00:32:00Z`, `mergeCommit: 37edc4375c96db9fb64598f406d07b3711df8cef`.

### Step 3 — Branched for smoke verification
```bash
git fetch origin
git checkout -b agent/bestseller-smoke-verification-20260504 origin/main
# branch HEAD: 37edc4375c (PR #856 squash)
# parent:      dcc5fad25a (PR #852 squash)
PYTHONPATH=. python3 scripts/git/push_guard.py  # → "Push-guard OK."
```

### Step 4 — Ran smoke pipeline
Exact directive command, no modifications:
```bash
ws=/tmp/bestseller_smoke_post_merge
rm -rf "$ws" && mkdir -p "$ws"
PYTHONPATH=. python3 scripts/pipeline/create_job.py \
  --pipeline ebook --workspace "$ws" \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml
PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace "$ws"
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml \
  --pipeline-mode spine \
  --runtime-format compact_book_8ch_30min \
  --render-book --render-dir "$ws" \
  --out "$ws/plan.json" \
  --quality-profile production \
  --seed 20260504 \
  --workspace "$ws"
```
Pipeline exit code: `1`. No `book.txt` rendered. No `plan.json` produced. Failed at `quality_gate` stage.

### Step 5 — Diagnosed the failure
Three findings (detail in §"Failure modes" below). Confirmed root cause for finding #1 by reading [phoenix_v4/planning/book_structure_plan.py:18-36, 496](phoenix_v4/planning/book_structure_plan.py).

### Step 6 — Wrote and shipped the artifact PR
- Commit: `65e26e9d96` on `agent/bestseller-smoke-verification-20260504`
- PR: [#858](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/858)
- 4 files, +1144 lines, 0 deletions, 0 production code touched

---

## Smoke result (verbatim)

**Pipeline reached:** planning → content selection. Failed at `quality_gate`.
**Pipeline did NOT reach:** `prose_render`, `book.txt` write, EI v2 scoring, memorable_lines, transformation_arc, bestseller composite.

| Win-condition criterion | Target | Observed |
|---|---|---|
| Pipeline reaches `prose_render` | yes | **no** |
| `book.txt` produced | yes | no |
| `word_count` in `[5500, 7500]` | yes | n/a |
| `chapter_flow` 0 FAIL | yes | n/a |
| `EI v2` composite ≥ 0.55 | yes | n/a |
| `memorable_lines` ≥ 6/8 chapters | yes | n/a |
| `bestseller_composite` Pass / non-blocking Hold | yes | n/a |

---

## Failure modes (3, in order of importance)

### Finding 1 — Wiring gap in auto-plan (small fix, high impact)

**Symptom:** Auto-plan produced 13 chapters instead of the format-declared 8. Run log shows `EXERCISE FALLBACK` for chapters `0`-`11` and `Chapter contract: chapter 12: emotional_job 'resolution' matches previous chapter`, confirming a 13-chapter book was generated.

**Root cause:** [phoenix_v4/planning/book_structure_plan.py:18](phoenix_v4/planning/book_structure_plan.py:18) holds:
```python
FORMAT_CHAPTER_COUNTS: dict[str, int] = {
    "micro_book_15": 5,
    "micro_book_20": 6,
    "five_min_practice": 5,
    "pocket_guide": 6,
    "ten_things_to_do": 8,
    "short_book_30": 8,
    "symptom_to_action_atlas": 8,
    "daily_text_audio_companion": 10,
    "crisis_cards": 6,
    "weekly_challenge_pack": 8,
    "faq_audiobook": 8,
    "myth_vs_mechanism": 8,
    "protocol_library": 10,
    "standard_book": 10,
    "extended_book_2h": 14,
    "deep_book_4h": 16,
    "deep_book_6h": 20,
}
```
None of `compact_book_5ch_15min`, `compact_book_5ch_20min`, `compact_book_8ch_30min` are listed. At line 496:
```python
n_chapters = chapter_count or FORMAT_CHAPTER_COUNTS.get(runtime_format, 10)
```
Fallback is 10. The observed 13 implies downstream logic (probably `assign_bestseller_structures` post-pad based on the 20-chapter F006 arc) further pads upward. Either way, the format-registry declaration is silently ignored.

**Single-source-of-truth violation:** `config/format_selection/format_registry.yaml` correctly declares `chapter_count_default: 8` for `compact_book_8ch_30min`. The auto-plan generator does not read it. PR #856 added the registry entry but did not wire the lookup.

**Fix scope:** small. Either (a) add the three compact formats to `FORMAT_CHAPTER_COUNTS`, or (b) better, refactor the auto-plan to read `chapter_count_default` from the registry as the single source of truth and delete the hardcoded dict. Option (b) prevents the same regression on the next format added.

### Finding 2 — EXERCISE coverage gap (content backfill)

**Symptom:** Every chapter logged:
```
EXERCISE FALLBACK: Using library_34 for chapter <N> topic anxiety persona gen_z_professionals.
No registry or teacher exercise was available for this slot —
add EXERCISE coverage upstream if this is unexpected.
```
12 chapters, 12 fallbacks. PR #852's atom backfill covered TEACHER_DOCTRINE + chapter-flow but not EXERCISE slots for the `gen_z_professionals × anxiety` matrix.

**Root cause:** Content gap. Not a wiring bug.

**Fix scope:** medium. Atom backfill PR for EXERCISE slots in this matrix, mirroring the pattern of #852 but for a different slot type.

### Finding 3 — Scene anchor density FAIL on chapter 10 (likely downstream of #1)

**Symptom:** Hard quality-gate failure (the actual exit-1 cause):
```json
{
  "status": "FAIL",
  "scene_anchor_cap": 2,
  "violations": [
    {
      "chapter": 10,
      "offenders": [{"phrase": "the nervous system is", "paragraph_count": 3}]
    }
  ]
}
```

**Root cause hypothesis:** With 13 chapters instead of 8, the spine/atom selection re-pulled the same scene anchor across over-many slots. With a correctly-sized 8-chapter plan it is **plausible (not certain)** that no chapter would hit the cap.

**Fix scope:** Don't chase directly. Re-run smoke after Finding #1's wiring PR lands, and only triage this independently if it still trips.

---

## Dependency verification table

| Check | Expected | Observed |
|---|---|---|
| PR #852 squash on `origin/main` | yes | `dcc5fad25a` ✓ |
| PR #856 squash on `origin/main` | yes | `37edc4375c` ✓ (merged this session) |
| Format `compact_book_8ch_30min` declared in registry | yes | yes ✓ |
| Format auto-plan chapter count = 8 | yes | **no — observed 13** |
| TEACHER_DOCTRINE atoms loaded | yes | yes (no `EnrichmentGap` raised) |
| EXERCISE atoms loaded for matrix | n/a per directive | **no — every chapter `library_34` fallback** |
| Word-budget clamp active | n/a (no render) | n/a |
| `push_guard` | PASS | PASS |
| `preflight_push` | PASS | PASS |
| LLM audit (zero paid LLM calls) | PASS | PASS (template/atom-driven render) |
| No production code touched | PASS | PASS (only `artifacts/qa/` writes) |

---

## Files changed by this session

### On `origin/main` (via merge)
- PR #856 (squash `37edc4375c`): 4 files, +96/-0
  - `config/format_selection/format_registry.yaml` — three compact formats declared
  - per-section budget config
  - runtime_policies wiring
  - tests

### On `agent/bestseller-smoke-verification-20260504` (in PR #858)
- `artifacts/qa/bestseller_smoke_post_852_856_2026-05-04.md` — narrative diagnosis
- `artifacts/qa/bestseller_smoke_books/run.log` — full pipeline stdout/stderr (3848B)
- `artifacts/qa/bestseller_smoke_books/scene_anchor_density_report.json` — gate report (326B)
- `artifacts/qa/bestseller_smoke_books/selected_content_variants.json` — content selections (28832B)

**Not changed:** any production code, any atom, any spec doc, any catalog, any config under `config/source_of_truth/`. Iteration cap of 0 was held.

---

## Open PR for handoff

**[PR #858](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/858) — qa(bestseller): compact-format smoke post #852+#856 — REJECT + 3-finding diagnosis**

- State: OPEN, awaiting operator review
- Branch: `agent/bestseller-smoke-verification-20260504`
- Base: `main`
- Commit SHA: `65e26e9d96`
- Diff: +1144 / -0 / 4 files (all under `artifacts/qa/`)

---

## Next-cycle work (NOT done in this session — for the next operator/agent)

The bestseller-pass goal for compact formats is **two PRs away**, not one:

| PR | Type | Scope | Size | Order |
|---|---|---|---|---|
| `eng/auto-plan-compact-format-counts` | wiring | wire `compact_book_*` formats into auto-plan; ideally refactor to read `chapter_count_default` from registry as single source of truth; add unit test asserting parity between registry and auto-plan | small (~30 LOC + test) | first |
| `content/exercise-atoms-anxiety-gen-z-professionals` | content | backfill EXERCISE atom slots for the matrix so `library_34` is not the fallback | medium | concurrent with first |

**After both land:** re-run the same smoke command (documented in artifact md and this handoff). The scene_anchor_density failure may resolve on its own once chapter count is correct; if it persists, treat as a third small wiring PR.

**Order:** the two next-cycle PRs are concurrent (different concerns: engineering vs. content) but both should land before any third smoke retry. Per memory entry [`feedback_validation_before_scaling`](https://github.com): do not stack on uncertain APIs; gate the next smoke on both PRs being on `origin/main`.

---

## What stays deferred

Per the operator directive's §3 and §6:

1. **V4 modular `output_format` mapping** — deferred from #856 closeout. Should not proceed until a compact-format smoke actually passes bestseller composite. No point wiring a modular mapping onto an auto-plan that doesn't honor format-declared chapter counts.

2. **Cover stream PR-5..PR-7b** — not opened. Per directive Option A, wait for #855 + #857 to land before opening PR-5. The 6-PR plan in §5 of the directive (with PR-7 split into PR-7a engineering and PR-7b data) holds.

3. **Pearl News operator visual sign-off** — pending. After #850 + #853 merge, render at three layout variants (left / right / bottom sidebar), commit screenshots, operator visual sign-off in PR comments. Memory entry [`feedback_preview_verification`](https://github.com) governs.

4. **Compact format applied to other personas/topics** — gates on this verification passing for `gen_z_professionals × anxiety` first.

---

## State the next agent walks into

- **Branch:** worktree `nervous-banzai-1af281` is on `agent/bestseller-smoke-verification-20260504`. Working tree clean.
- **`origin/main` HEAD:** `37edc4375c` (PR #856) over `dcc5fad25a` (PR #852).
- **One open PR from this stream:** [#858](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/858).
- **Other concurrent PRs (untouched this session):** #850, #853 (Pearl News); #855, #857 (cover); plus whatever the operator has in flight elsewhere.
- **Memory entries that governed this session:**
  - `feedback_validation_before_scaling` — gate scaling on validator output
  - `feedback_message_terseness` — diagnosis + concrete next step
  - `feedback_closeout_receipt_format` — full SHA, NEXT_ACTION, gates
  - `feedback_preview_verification` — applies to Pearl News, deferred from this session

---

## CLOSEOUT_RECEIPT (canonical, also in PR #858)

```
CLOSEOUT_RECEIPT — Bestseller Smoke Verification

Branch: agent/bestseller-smoke-verification-20260504
Commit SHA: 65e26e9d96 (full SHA in git log)
PR: #858
Outcome: REJECT

Files written:
  artifacts/qa/bestseller_smoke_post_852_856_2026-05-04.md   — 1144L total commit
  artifacts/qa/bestseller_smoke_books/run.log                — pipeline stdout/stderr
  artifacts/qa/bestseller_smoke_books/scene_anchor_density_report.json
  artifacts/qa/bestseller_smoke_books/selected_content_variants.json

Smoke result (compact_book_8ch_30min):
  rendered: no (pipeline exit 1)
  word_count: n/a (no render)
  in_band: n/a
  chapter_flow: n/a (gate not reached)
  EI v2 composite: n/a
  memorable_lines: n/a
  transformation_arc: n/a
  bestseller_composite: n/a
  pre-render gate failure: scene_anchor_density FAIL on chapter 10
  hard alarm triggered: chapter count = 13 (expected 8) — auto-plan wiring gap
  hard alarm triggered: EXERCISE coverage gap (every chapter library_34 fallback)

PR #852 + #856 dependency verification:
  PR #852 squash SHA on main: dcc5fad25a (already on main at session start)
  PR #856 squash SHA on main: 37edc4375c (merged this session)
  TEACHER_DOCTRINE atoms loaded: yes (no EnrichmentGap raised)
  Compact format declared in registry: yes
  Auto-plan honors chapter_count_default: NO — wiring gap in
    phoenix_v4/planning/book_structure_plan.py FORMAT_CHAPTER_COUNTS

Gates:
  push_guard: PASS
  preflight: PASS
  llm_audit: PASS (zero paid LLM calls; pipeline render is template/atom-driven)
  no production code touched: PASS (only artifacts/qa/ writes)

NEXT_ACTION:
  Operator review of PR #858 + decide on next-cycle PR ordering.
  Two follow-on PRs scoped (NOT opened, NOT stacked):
    1. eng/auto-plan-compact-format-counts (small wiring + test)
    2. content/exercise-atoms-anxiety-gen-z-professionals (medium backfill)
  After both merge, re-run the same smoke command as closing verification.
  V4 modular output_format mapping remains deferred.
  Cover stream and Pearl News stream untouched, separate branch chains.
```

---

## Appendix — repro command for next agent

```bash
ws=/tmp/bestseller_smoke_post_merge
rm -rf "$ws" && mkdir -p "$ws"
PYTHONPATH=. python3 scripts/pipeline/create_job.py \
  --pipeline ebook --workspace "$ws" \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml
PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace "$ws"
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml \
  --pipeline-mode spine \
  --runtime-format compact_book_8ch_30min \
  --render-book --render-dir "$ws" \
  --out "$ws/plan.json" \
  --quality-profile production \
  --seed 20260504 \
  --workspace "$ws"
```

Run this exact command after the two next-cycle PRs land. If exit code is 0 and `book.txt` exists in `$ws`, inspect quality summary for bestseller composite.

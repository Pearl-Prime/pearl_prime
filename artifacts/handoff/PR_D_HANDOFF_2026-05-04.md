# PR-D Handoff — Wire Compact Formats + Bestseller Smoke

**Date:** 2026-05-04
**Status:** PARTIAL — 3 of 8 wires landed (uncommitted, local only); blocked at W3b/c on a spine-architecture decision (P1/P2/P3) that requires operator pick before continuing.
**Branch:** `agent/wire-compact-formats-bestseller-smoke-20260504` (local, not pushed)
**Worktree:** `/Users/ahjan/phoenix_omega/.claude/worktrees/pensive-jepsen-9d50be`
**Base:** `origin/main` at SHA `dcc5fad25a` (= PR #852 squash-merge)
**Authority docs:**
- `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` (PR #852 — canonical spec)
- `docs/TEACHER_DOCTRINE_ATOM_CONVENTION_2026-05-04.md` (PR #852 — atom convention)

---

## 1. Sequence of decisions

### PR #852 prerequisite
- Merged squash via `gh pr merge 852 --squash --delete-branch`
- Squash SHA: `dcc5fad25a6ab008b19311ce54a750a0e4e61d8e`
- All Phoenix Omega gates green at merge; only failing check was Cloudflare Worker build (`pearl-prime`), which is the documented build-always-fails issue per CLAUDE.md and is orthogonal to atom content
- Local branch deletion failed (worktree lock on `agent/pearl-writer-compact-formats-genz-anxiety-20260504`); remote branch deleted cleanly

### V1-V7 reconciliation (operator decisions, all = spec/recommend)

The PR-D brief and PR #852's canonical spec doc disagreed on 7 material points. Operator chose "all recommend":

| # | Issue | Brief said | Spec said | Decision |
|---|-------|------------|-----------|----------|
| V1 | Base value in `_max_extra_chunks_for_format` for compact formats | 0/0/1 | 1/1/1 | **1/1/1** |
| V2 | W2 word-budget clamp (`min(max_chunks_per_slot, base+extra)`) | Add it | Not mentioned | **Skip** (16-43% overrun source is not in this function; it's spine-side) |
| V3 | W3 scope: only beatmap_compile, or also story_planner.py? | Only beatmap | (silent) | **Expand to story_planner** |
| V4 | `story_planner.ARC_BEATS` extension for 5 new beats (cost_exposure, reframe, practical_interruption, practice_under_pressure, escalation) | Drop validation | (silent) | **Extend ARC_BEATS** |
| V5 | `derived_from` value | `standard_book` | `micro_book_15` / `micro_book_20` / `short_book_30` | **Spec values** |
| V6 | TEACHER_DOCTRINE runtime-aware budget | Not mentioned | Required (load-bearing) | **Add as sub-wire** |
| V7 | Add compact formats to `SOMATIC_FULL_RUNTIME_FORMATS` | Not mentioned | Implied (10-section grid) | **Yes** |

**Resulting wire count:** 8 (W1, W2, W3a, W3b, W3c, W3d, W4, W5/W6) — up from brief's original 6.

---

## 2. Landed work (3 of 8 wires)

All edits are in working tree, **uncommitted**. Diff vs. `origin/main`:

```
config/format_selection/format_registry.yaml | +87 lines  (W1)
phoenix_v4/planning/enrichment_select.py     | +6/-1      (W2)
phoenix_v4/planning/beatmap_compile.py       | +13/-1     (W3a)
```

### W1 — format_registry.yaml (✓ verified parses)

Appended 3 compact runtime format blocks under `runtime_formats:` per spec §4. Schema keys per format: `format_id`, `display_name`, `duration_minutes`, `audio_runtime_minutes`, `word_range`, `word_target_min/max/canonical`, `chapter_count`, `chapter_count_default`, `sections_per_chapter`, `variants_per_section`, `scene_section_indices`, `word_budget_per_section`, `beat_compression_strategy`, `beat_sheet` (list of {chapter, phase, arc_beat, narrative_role, word_target}), `compatible_tiers`, `compatible_structural_formats`, `derived_from`, `authority_doc`.

Validation: `python3 -c "yaml.safe_load(open('config/format_selection/format_registry.yaml'))"` → 10 runtime_formats keys, beat_sheets correct length (5 / 5 / 8).

### W2 — enrichment_select.py:518-525 (✓ verified)

Added 3 compact format ids to the `base = 1` branch of `_max_extra_chunks_for_format`. Per V1 decision (spec wins, base=1 for all three).

Verified per-format behavior at `slot_target_words=600`:
- `compact_book_5ch_15min` → 2 (base=1 + extra=1)
- `compact_book_5ch_20min` → 2
- `compact_book_8ch_30min` → 2
- `micro_book_15` → 1 (no regression)
- `short_book_30` → 2 (no regression)

Per V2 decision: **no word-budget clamp added.** The 16-43% overrun documented in spec §2 doesn't originate in this function (24-cap rarely binds in practice for typical slot targets); it's a spine-architecture issue (see W3b/c blocker).

### W3a — beatmap_compile.SOMATIC_FULL_RUNTIME_FORMATS (✓ landed)

Added 3 compact format ids to `SOMATIC_FULL_RUNTIME_FORMATS` (lines 37-49). This routes compact formats through the 10-slot somatic grid path with TEACHER_DOCTRINE at section_06 — required for V6 (TEACHER_DOCTRINE runtime-aware budget) to apply.

---

## 3. Blocker (W3b/c) — spine architecture decision required

### What was discovered

The original brief assumed `story_planner.DEFAULT_PHASE_CHAPTERS` was the load-bearing ingredient (override → 5/8 chapters). Reading the actual call chain found a deeper coupling:

1. `phoenix_v4/planning/knob_apply.py:219` `load_spine(topic)` reads `config/spines/{topic}_spine.yaml` — fixed 12-chapter file (e.g., `anxiety_spine.yaml`).
2. `apply_knob_profile` (line 515): `chapter_count = len(spine.chapters)` (= 12); `per_chapter = total_target / chapter_count`.
3. `story_planner.build_story_schedule` accepts `phase_chapters` override, but it **schedules stories into existing chapter slots** — it doesn't synthesize new chapters.

**Implication:** Compact formats can't render as 5/8-chapter books unless the spine itself has 5/8 chapters. Overriding `phase_chapters` against a 12-chapter spine produces 12-chapter books with redistributed phase boundaries — not compact books.

### Three paths to resolve

**P1 — Synthesize compact spine from format spec's `beat_sheet`**
- Modify `knob_apply.load_spine` (or a new helper called before it) to detect compact `runtime_format` and synthesize N `SpineChapter` objects from the format's `beat_sheet`, deriving fields from beat_sheet's `arc_beat` + `narrative_role` + a fallback template for `thesis` / `practical_job` / `required_sections`.
- ~50 lines new code, no new YAML files
- Single source of truth = format spec
- **Risk:** synthesized scaffolding may be too thin for downstream gates
- **Time:** +30-60 min on PR-D

**P2 — Author 3 new compact spine YAMLs (Pearl_Writer follow-up)**
- New files: `config/spines/anxiety_compact_5ch.yaml`, `anxiety_compact_8ch.yaml` (and per-topic files for each topic to be supported)
- Hand-tuned thesis/role text → highest smoke-pass odds
- **Crosses engineering/content line** — not appropriate for PR-D per Hard rule #1 (no content edits)
- **Hand off to Pearl_Writer** (pattern established by PR #852)
- **Time:** PR-D ships W1+W2+W3a+W4 only; Pearl_Writer follow-up authors compact spines; W3b/c lands in a third PR

**P3 — Subset 12-chapter spine to N chapters at apply_knob time**
- Map compact's beat_sheet → existing 12-chapter spine ranges (HARDSHIP=ch{1-3}, HELP=ch{4-6}, HEALING=ch{7-9}, HOPE=ch{10-12}); pick N chapters per beat_sheet's chapter→phase mapping
- ~15-30 lines new code
- **Brittleness:** existing spine ch10's text may not match compact ch4's `practice_under_pressure` role; selection rule is fragile
- **Time:** +15-30 min on PR-D

### Recommendation

**P1** for one-shot continuation of PR-D within the current cycle. Synthesizes spine from beat_sheet (which already has phase + arc_beat + narrative_role per chapter — sufficient to populate SpineChapter with reasonable defaults). If smoke fails on weak scaffolding, that diagnosis becomes the scope for a Pearl_Writer P2 follow-up PR with hand-tuned compact spines.

**P2** for highest quality but slower (3 sequential PRs: this one ships partial wiring; Pearl_Writer authors compact spines; final wiring PR).

---

## 4. Pending work (5 of 8 wires)

### W3b — Make `_scale_budget` chapter target compact-format-aware
- File: `phoenix_v4/planning/beatmap_compile.py` ~line 482-505
- Today: `ch_target = ch.target_word_count` — value comes from upstream `ShapedChapter.target_word_count`, which is set in `knob_apply.py:691` as `per_chapter` (= `total_target / chapter_count`)
- Once W3c lands (spine has correct N chapters), `ch_target` flows correctly and existing `_scale_budget(SOMATIC_WORD_BUDGET, ch_target)` proportionally scales TEACHER_DOCTRINE from 460→~80/~96/~83 — **no W3b change needed**
- **W3b reduces to "verify correct flow after W3c lands"** — not a separate edit if W3c is correct

### W3c — Spine source for compact formats
- Choice depends on P1/P2/P3:
  - **P1:** modify `knob_apply.load_spine` to synthesize spine from format spec's `beat_sheet` when `runtime_format` is compact
  - **P2:** add 3 new spine YAML files (Pearl_Writer task)
  - **P3:** add `_subset_spine_for_format` helper in `knob_apply` that selects N chapters from 12-chapter spine

### W3d — Extend `story_planner.ARC_BEATS`
- File: `phoenix_v4/planning/story_planner.py:51-55`
- Add 5 new beats: `cost_exposure`, `reframe`, `practical_interruption`, `practice_under_pressure`, `escalation`
- Today's value: `["recognition", "mechanism_proof", "turning_point", "embodiment"]`
- Per V4 decision: extend (not drop validation)
- **~5 line edit. Trivial. Independent of P1/P2/P3.**

### W4 — runtime_policies in book_quality_gate.yaml
- File: `config/quality/book_quality_gate.yaml:39-48`
- Append 3 entries: `compact_book_5ch_15min: {default_reject: false, allow_override: true}` (and same for the other two)
- **~6 line edit. Trivial. Independent of P1/P2/P3.**

### W5/W6 — Smoke pass
- Cannot run without W3b/c landed
- Per brief: `gen_z_professionals × anxiety` × {5ch_15min, 8ch_30min} with `--quality-profile production`
- Expected: bestseller composite = Pass (or Hold-with-known-non-blocking-reasons) on at least one format
- Iteration cap: 2 (per memory `feedback_validation_before_scaling`)

---

## 5. Resume instructions

### Pre-resume checks
```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/pensive-jepsen-9d50be
git branch --show-current   # expect: agent/wire-compact-formats-bestseller-smoke-20260504
git status --short           # expect: 3 modified files (W1/W2/W3a uncommitted)
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0 (since work uncommitted)
git log origin/main --oneline -1   # expect: dcc5fad25a (#852)
```

### If continuing with P1 (synthesize)

1. Implement W3c: modify `knob_apply.py:load_spine` to detect compact `runtime_format` (passed via new parameter or via context) and synthesize spine from format spec's `beat_sheet`. Cleanest: add a new function `_synthesize_compact_spine(format_spec, topic)` and route there before the YAML read.
   - Map `beat_sheet[i].arc_beat` → `SpineChapter.role` (or store separately)
   - Map `beat_sheet[i].phase` → `SpineChapter.thesis` template ("This chapter establishes {phase} via {arc_beat}: {narrative_role}.")
   - Default `required_sections` = `["HOOK", "SCENE", "REFLECTION", "EXERCISE", "INTEGRATION"]`
   - Default `forbidden_moves` = `[]`
   - Default `recommended_enrichments` = derived from `arc_beat` (e.g., `mechanism_proof` → `["teacher_voice", "mechanism_depth"]`)
2. Update `apply_knob_profile` caller (or wherever `load_spine` is called) to pass format spec for compact-detection.
3. Implement W3d: extend `ARC_BEATS` in `story_planner.py:51-55`.
4. Implement W4: append 3 entries to `book_quality_gate.yaml:runtime_policies`.
5. Run smoke per brief W6.

### If continuing with P2 (Pearl_Writer follow-up)

1. **This PR closes** with W1+W2+W3a+W3d+W4 only (the engineering wires that don't depend on spine).
2. Add a defensive raise in `knob_apply.load_spine` for compact `runtime_format` when no compact spine YAML exists, so failures are clean rather than silent 12-chapter renders.
3. Open a follow-up Pearl_Writer brief for compact spine YAMLs.
4. Open a third engineering PR for the spine wiring once compact spines are authored.

### If continuing with P3 (subset)

1. Implement `_subset_spine_for_format(spine, format_spec)` helper in `knob_apply.py`.
2. Map: `beat_sheet[i].phase` → spine chapter range; pick `i`-th chapter from the range (or the chapter whose `role` best matches `arc_beat`).
3. Implement W3d + W4 + smoke.

### Resume signal needed from operator
- P1 / P2 / P3 / abandon
- Whether to commit + push the W1+W2+W3a partial wiring as a standalone PR (engineering hygiene) or hold uncommitted until full path forward is decided

---

## 6. Risks captured

1. **W3b/c is the load-bearing change.** Without it, smoke produces 12-chapter compact books that fail word-band gates again — the same failure documented in spec §2 for `micro_book_15`. The W1/W2/W3a wires alone don't fix the underlying overrun.
2. **Synthesized spine (P1) may produce chapters with thin thesis/practical_job text.** This may pass downstream gates by minimum but produce books with weaker prose density than hand-tuned spines. Acceptable for smoke validation; may not be acceptable for shipping.
3. **`ARC_BEATS` extension (W3d) is required regardless of path.** If beatmap_compile or downstream code validates `arc_beat ∈ ARC_BEATS`, the new beats fail. Even if no validation exists today, adding ARC_BEATS makes the codebase honest about what beats exist.
4. **Branch protection on this PR.** PR-D must pass governance, EI v2 gates, variant coverage, and Cloudflare Worker check. If Cloudflare keeps failing (known-known), operator decision needed at merge time per #852 precedent.
5. **Push-guard / preflight ran clean at branch creation** — but will need to re-run before any push; W3c-sized edits may trigger different gates.

---

## 7. Files / receipts

### Files modified (uncommitted, local working tree)
```
config/format_selection/format_registry.yaml  +87 lines (W1)
phoenix_v4/planning/beatmap_compile.py        +13/-1    (W3a)
phoenix_v4/planning/enrichment_select.py      +6/-1     (W2)
```

### Verification commands run
- `python3 -c "yaml.safe_load(open('config/format_selection/format_registry.yaml'))"` → 10 runtime_formats; compact entries parse with correct word_target_canonical (3800 / 4750 / 6500), correct beat_sheet lengths (5 / 5 / 8)
- `python3 -c "from phoenix_v4.planning.enrichment_select import _max_extra_chunks_for_format; ..."` → compact formats return base=1 ladder; no regression on micro_book_15 / short_book_30
- `PYTHONPATH=. python3 scripts/git/push_guard.py` → Push-guard OK (at branch creation; not re-run after edits)
- `bash scripts/ci/preflight_push.sh` → Preflight OK (at branch creation; not re-run after edits)

### Files NOT yet modified (still pending W3b/c/d/W4)
```
phoenix_v4/planning/knob_apply.py              (W3c if P1 or P3)
phoenix_v4/planning/story_planner.py           (W3d)
config/quality/book_quality_gate.yaml          (W4)
config/spines/anxiety_compact_*.yaml           (only if P2)
artifacts/qa/compact_format_bestseller_smoke_2026-05-04.md  (W6 output)
```

---

## 8. Cost & time

- **Wall-clock so far:** ~50 min (validation + V1-V7 cycle + W1-W3a edits + scope-expansion surface)
- **Paid LLM API calls:** zero (per CLAUDE.md tier policy)
- **RunComfy / external service cost:** zero
- **Iteration count:** 0 of 2 cap (no smoke runs yet)

## 9. Memory lessons applied

- `feedback_validation_before_scaling` — Stood down on PR-D until #852 merged; pivoted to validation read of #852's spec docs while waiting; did not stack on unmerged branch
- `feedback_message_terseness` — Each operator-facing message kept to diagnosis + concrete decisions + resume signal
- `feedback_closeout_receipt_format` — This handoff includes full SHA, file-by-file changes, methodology lessons, NEXT_ACTION
- Hard rule #6 — Branched from `origin/main` after #852 merge, not from #852's branch

---

## 10. Open questions for operator

1. **P1 / P2 / P3 / abandon** — which path forward?
2. Commit W1+W2+W3a as a standalone engineering PR (hygienic mid-cycle save), or hold uncommitted until full path is decided?
3. If P2: open Pearl_Writer brief for compact spines now, or wait for current cycle wrap?
4. Iteration cap remains 2 once smoke is reachable?
5. Any new authority docs to amend? (Spec §8 mentioned `SOMATIC_WORD_BUDGET["TEACHER_DOCTRINE"]` runtime-aware as a separate change — current finding shows existing `_scale_budget` already does this once `ch_target` is correct, so spec §8 may need a clarifying note. Defer to follow-up doc PR.)

---

**End of handoff.**

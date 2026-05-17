# deep_book_6h parity canary — gen_z_professionals × anxiety × ahjan

Date: 2026-05-17
Agent: Pearl_Dev
Branch: `fix-issues-A-B-2026-05-17` (off `origin/main` + 5 cherry-picks of dedupe-leak PRs #1136/#1137/#1138/#1140/#1144)
Audit input: `artifacts/qa/bestseller_chord_audit_2026-05-17.md` (parent worktree) Axis 3 — PR #939 (`635e1a96b`) validated deep_book_6h, NOT standard_book; the failing wave's format was never validated.

---

## Canary CLI

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --pipeline-mode spine --quality-profile production --exercise-journeys \
  --topic anxiety --persona gen_z_professionals --teacher ahjan \
  --runtime-format deep_book_6h \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__comparison__F006.yaml \
  --locale en-US --render-book --render-dir /tmp/deep_book_6h_canary \
  --no-job-check --no-generate-freebies
```

Arc choice rationale: wave-audit aggregate (`teacher_mode_gen_z_professionals_anxiety_2026-05-17.md`) names `gen_z_professionals__anxiety__comparison__F006.yaml` as the wave's arc; this is the only `--arc` value that produces the wave's 12-chapter shell because `load_book_structure_plan` resolves to `config/plans/anxiety_gen_z_professionals_6h.yaml` (12 chapters) for both standard_book and deep_book_6h runtime formats.

CLI flag confirmed via `scripts/run_pipeline.py --help`: `--runtime-format <id>` (not `--book-plan-id`).

---

## Result: ✗ FAIL (different failure pattern than standard_book)

| Dimension | standard_book wave (parent) | deep_book_6h canary (this run) |
|---|---|---|
| book.txt produced | ✓ (58-66 KB, 12 chapters) | ✗ (rendering blocked pre-write) |
| ch 11-12 word counts | **5 + 6 words** (Axis 4 collapse) | **63 + 59 slots populated** (slot fill, content composed) |
| ch 11-12 collapse | ✓ uniform across 13 teachers | ✗ **NOT present** — slot grid populated with depth atoms |
| Failure mode | book_quality_gate Reject (4 chapter_flow FAILs at ch 7/11/12) | scene_anchor_density cap FAIL (4 chapters: 1, 6, 10, 11; 7 offending phrases) |
| Per-format failure axis | format_wmax cap (13000) truncates ch 11-12 content to 0 in `enrichment_select.py:1228-1231` | dedup_below_floor: book size 30386-49554 vs deep_book_6h floor 50000; then scene_anchor cap=2 hit |

**Verdict:** **deep_book_6h fails differently** — the Axis 4 collapse problem (chapters 11-12 truncated to 0 words) is **structurally resolved** by deep_book_6h's larger word range (50000-72000 vs standard_book's 9000-13000), but a **new failure** in the dedup/scene-anchor cascade blocks render. The 5 dedupe-leak PRs cherry-picked here are compatible with PR #939's main, but the combined dedup behavior over-aggressively removes scene anchors, dropping word counts below the 50000 floor AND triggering scene_anchor_density cap=2 violations.

---

## Evidence

**Slot allocation for ch 11-12 in deep_book_6h canary** (`selected_content_variants.json`):
- ch11: 63 slots (HOOK, STORY, REFLECTION, EXERCISE, STORY, TEACHER_DOCTRINE, REFLECTION, EXERCISE, STORY, INTEGRATION, then DEPTH_MECHANISM_DEPTH × 3, DEPTH_STORY_SCENE, + depth modules)
- ch12: 59 slots (same pattern)
- Total slots in book: 629 (vs standard_book's 120)

**Compared to standard_book wave** (master_sha sample):
- ch11: 10 slots — same slot types — but slot.content TRUNCATED TO "" by format_wmax cap in `phoenix_v4/planning/enrichment_select.py:1163-1231`. Audit's `section_packet_audit` shows 1704 words SELECTED for ch11 BEFORE the truncation; `_truncate_to_word_budget(content, room_book=0)` zeroed them out.
- ch12: 10 slots, 1428 words SELECTED → truncated to 0.

**scene_anchor_density violations** (`/tmp/deep_book_6h_canary/scene_anchor_density_report.json`):
- Chapters with violations: 1, 6, 10, 11
- 7 offending phrases total
- Examples: "this is a body" (4 paragraph occurrences in ch 1), "your nervous system has" (3 in ch 1)

**dedup_below_floor warnings** (`/tmp/deep_book_6h_canary/run.log:194-195`):
- Final book deduped to 30386-49554 words — below deep_book_6h's 50000 floor
- "deduped text returned (no longer retains duplicates to hit floor)"

---

## Recommendation: standard_book fix is mandatory

Per task spec: "If deep_book_6h ALSO fails (Reject, same ch 11-12 collapse) → upstream issue → Phase 2 mandatory". Here deep_book_6h does NOT collapse ch 11-12 (positive surprise) but ALSO does not produce a clean book (different failure axis: dedup cascade + scene anchor cap).

**Operator pivot decision (in envelope per `feedback_operator_proxy_routing`):**
- **Do NOT pivot the wave to deep_book_6h without further investigation.** Even though the chapter-11-12 issue is resolved, the dedupe+scene-anchor failure blocks production output. Validation of deep_book_6h on the current `main + 5 dedupe-leak PRs` stack would need additional tuning that is out of this session's scope.
- **DO ship the standard_book ch 11-12 fix.** It addresses Axis 4 head-on (raises `word_range[1]` from 13000 → 18000 to accommodate 12-chapter arcs without truncating late chapters). Independent of dedupe-leak PR merge order.

**Out-of-scope follow-up (operator-pickable):**
- Investigate scene_anchor_density cap interaction between PR #939's `dedupe_scene_furniture_book` (moved post-strengthen) and the 5 dedupe-leak PRs' per-chapter dedup. PR #1136 (book-wide paragraph dedupe safety net) is the most likely interaction point — its `whole_book_dedupe_notes` were 35-45 events/book in the audit, which combined with PR #939's post-strengthen dedup may now over-prune.
- Decide whether `deep_book_6h` parity should be restored before or after merging the 5 dedupe-leak PRs.

---

## OPD-eligible decision (logged)

- `OPD-20260517-canary-001`: Use ahjan teacher + production profile for canary (preserves PR #939 parity intent per `feedback_operator_proxy_routing` envelope). Decided in-session.
- `OPD-20260517-canary-002`: Use `gen_z_professionals__anxiety__comparison__F006.yaml` as the arc (matches wave aggregate report; resolves to the 12-chapter book_structure_plan). Decided in-session.

---

## Files referenced

- Canary output: `/tmp/deep_book_6h_canary/{run.log, selected_content_variants.json, scene_anchor_density_report.json}`
- Wave baseline: `/Users/ahjan/phoenix_omega/.claude/worktrees/keen-sinoussi-5b6b10/artifacts/books/en_US/teacher_mode/gen_z_professionals/anxiety/master_sha/`
- Format truncation site: `phoenix_v4/planning/enrichment_select.py:1163-1231`
- Format registry: `config/format_selection/format_registry.yaml:114-119` (standard_book entry)
- PR #939 baseline commit: `635e1a96b`
- 5 dedupe-leak PRs in this branch: #1136 (`ae530fd38`), #1137 (`b0de84dea`), #1138 (`3cfb082cf`), #1140 (`b202d3bcf`), #1144 (`0e9f22318`)

# Compact Book Format Specs — 2026-05-04

Authority document for three **compact runtime formats** in the Pearl Prime
book pipeline. Originally a proposal (2026-05-04); **wired on main** via
`config/format_selection/format_registry.yaml` (`compact_book_5ch_15min`,
`compact_book_5ch_20min`, `compact_book_8ch_30min`) with `compact_chapter_subset`
spine compression (PR-D-SPINE-01). This doc remains the beat-sheet authority;
§1 status below reflects landed reality.

---

## 1. Status

| Field | Value |
| --- | --- |
| Status | `landed` (was `proposal`; registry + spine path wired) |
| Wiring | **wired** — `format_registry.yaml` compact runtimes + `compact_chapter_subset` in spine path |
| Author agent | Pearl_Writer-A1 (Tier 1, Claude Code subagent) |
| Approval | Engineering landed; operator GTM sign-off on micro→compact deprecation still open (OQ-DFU-02) |
| Affects | `phoenix_v4/planning/enrichment_select.py`, `phoenix_v4/planning/beatmap_compile.py`, `phoenix_v4/planning/story_planner.py`, `config/format_selection/format_registry.yaml`, `config/quality/book_quality_gate.yaml` |
| Related authority | `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` §6 (format registry), `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` |

---

## 2. Problem statement

Today the pipeline forces every runtime format through the same 12-chapter
spine. The shorter the runtime band, the worse the per-chapter and per-section
budget squeeze becomes. Concrete evidence pulled from
`/tmp/pearl_prime_runs/` for `gen_z_professionals × anxiety` on
`book_plan_id = ref_anxiety_genz_1h_v1`:

| Runtime | Word band | Actual word_count | Overrun | Chapter-flow failures | EI v2 composite |
| --- | --- | --- | --- | --- | --- |
| `micro_book_15` (production) | 2,500–4,500 | **6,451** | **+43.4%** over 4,500 cap | **7 of 12 chapters** | **0.4753 (FAIL)** |
| `micro_book_20` (draft)      | 3,000–5,500 | **7,838** | **+42.5%** over 5,500 cap | **6 of 12 chapters** | 0.5843 (PASS) |
| `short_book_30` (draft)      | 4,500–7,500 | **8,672** | **+15.6%** over 7,500 cap | 4 of 12 chapters | 0.6386 (PASS) |

Source files:
`/tmp/pearl_prime_runs/micro_book_15/quality_summary.json`,
`/tmp/pearl_prime_runs/micro_book_15/book_pass_report.json`,
`/tmp/pearl_prime_runs/micro_book_20_draft/quality_summary.json`,
`/tmp/pearl_prime_runs/micro_book_20_draft/book_pass_report.json`,
`/tmp/pearl_prime_runs/short_book_30_draft/quality_summary.json`,
`/tmp/pearl_prime_runs/short_book_30_draft/book_pass_report.json`.

Failure pattern (consistent across all three runs):

- `book_pass.word_budget` FAIL — every short runtime overruns its band.
- `chapter_flow` FAIL — short runtimes have weak transitions and no clear
  thesis per chapter (the 12-chapter spine forces 12 thesis moments into
  ~4–7k words, so most chapters land MISSING_CLEAR_POINT and
  WEAK_TRANSITIONS).
- `book_quality_gate.release_band = Reject` — `runtime_policies` already
  marks `micro_book_15` and `micro_book_20` as `default_reject: true` in
  `config/quality/book_quality_gate.yaml`, acknowledging that the current
  format/spine pairing is unshipable.
- `governance_report.chapter_contract_warnings` — chapters 6–12 repeat
  emotional_job=`resolution`, because there is nothing left to escalate
  after splitting a 4–7k word arc across 12 chapters.

Root cause is structural, not prompt-level: a 12-chapter spine cannot carry a
3–7k word band without bleeding budget per section past what
`enrichment_select._max_extra_chunks_for_format` is willing to cap. The fix is
to give short runtimes a chapter spine sized to the band.

---

## 3. Proposed compact formats

Three new runtime format IDs, all with **10 sections per chapter** and
**5 variants per slot**, mirroring the 10-section somatic grid in
`phoenix_v4/planning/beatmap_compile.py:42` (`SOMATIC_10_SLOT_GRID`). Variant
count of 5 matches today's atom-stacking density in
`config/format_selection/format_registry.yaml`.

### 3.1 `compact_book_5ch_15min`

| Field | Value |
| --- | --- |
| Chapters | 5 |
| Sections per chapter | 10 |
| Variants per slot | 5 |
| Word target band | 3,000–4,500 |
| Canonical word target | 3,800 |
| Audio runtime | 12–18 min |
| Per-chapter target | ~760 words |
| Per-section target | ~76 words |
| Replaces (in practice) | `micro_book_15` for tiered B/C topics |

Beat sheet (HARDSHIP / HELP / HEALING / HOPE compressed to 5 chapters; HOPE
gets two chapters because the bestseller "embodiment" beat needs its own
chapter to land with felt texture, not a footer):

| Ch | Phase | Arc beat | Narrative role | Word target |
| --- | --- | --- | --- | --- |
| 1 | HARDSHIP | recognition | Name the pattern; reader sees themselves | 760 |
| 2 | HELP | mechanism_proof | Show why the pattern persists (teacher voice carries) | 760 |
| 3 | HEALING | turning_point | First interruption; small rep of the new move | 760 |
| 4 | HOPE | escalation | Practice under pressure; harder context, same move | 760 |
| 5 | HOPE | embodiment | Identity shift; the move is now who they are | 760 |

### 3.2 `compact_book_5ch_20min`

| Field | Value |
| --- | --- |
| Chapters | 5 |
| Sections per chapter | 10 |
| Variants per slot | 5 |
| Word target band | 4,000–5,500 |
| Canonical word target | 4,750 |
| Audio runtime | 16–22 min |
| Per-chapter target | ~950 words |
| Per-section target | ~95 words |
| Replaces (in practice) | `micro_book_20` for tiered B/C topics |

Same 5-chapter beat sheet as 3.1; only word budget per chapter/section
changes.

### 3.3 `compact_book_8ch_30min`

| Field | Value |
| --- | --- |
| Chapters | 8 |
| Sections per chapter | 10 |
| Variants per slot | 5 |
| Word target band | 5,500–7,500 |
| Canonical word target | 6,500 |
| Audio runtime | 25–35 min |
| Per-chapter target | ~812 words |
| Per-section target | ~81 words |
| Replaces (in practice) | `short_book_30` for tiered A/B topics |

Beat sheet (2 chapters per phase; clean phase boundaries):

| Ch | Phase | Arc beat | Narrative role | Word target |
| --- | --- | --- | --- | --- |
| 1 | HARDSHIP | recognition | Name the pattern | 812 |
| 2 | HARDSHIP | cost_exposure | What the pattern costs | 812 |
| 3 | HELP | mechanism_proof | Why the pattern persists (teacher voice) | 812 |
| 4 | HELP | reframe | The pattern as protection, not failure | 812 |
| 5 | HEALING | turning_point | First small rep of the new move | 812 |
| 6 | HEALING | practical_interruption | The move under everyday pressure | 812 |
| 7 | HOPE | practice_under_pressure | The move under hard pressure | 812 |
| 8 | HOPE | embodiment | Identity shift; the move is who they are | 812 |

Phase distinct_roles map directly to the 12 already enumerated in
`/tmp/pearl_prime_runs/micro_book_20_draft/book_pass_report.json:band_distribution`,
so existing role-tagged atoms work unchanged.

---

## 4. YAML schema proposal

Two placement options. **Recommendation: extend
`config/format_selection/format_registry.yaml:runtime_formats`** rather than
introduce a new file. That file already defines `runtime_formats:` and
`compatible_structural_formats:`, so adding three keys keeps a single source
of truth and avoids a second loader path. A separate `runtime_formats.yaml`
would force `format_registry.yaml`, `book_quality_gate.yaml`,
`enrichment_select.py`, and `beatmap_compile.py` all to learn a new file
location for marginal organizational benefit.

Schema fields (every compact format MUST set all of these):

```yaml
# To be appended under runtime_formats: in
# config/format_selection/format_registry.yaml.
# This is the SCHEMA PROPOSAL — do not commit as YAML in this PR.

compact_book_5ch_15min:
  format_id: compact_book_5ch_15min
  display_name: "Compact 5-chapter / 15 min"
  duration_minutes: 15
  audio_runtime_minutes: [12, 18]
  word_target_min: 3000
  word_target_max: 4500
  word_target_canonical: 3800
  chapter_count: 5
  sections_per_chapter: 10
  variants_per_section: 5
  scene_section_indices: [2, 5, 9]   # positional, mirrors story_planner.py
  word_budget_per_section: 76        # 3800 / (5 * 10)
  beat_compression_strategy: "hope_doubled"   # 1+1+1+2 across HARDSHIP/HELP/HEALING/HOPE
  beat_sheet:
    - {chapter: 1, phase: HARDSHIP, arc_beat: recognition,         narrative_role: "name the pattern",       word_target: 760}
    - {chapter: 2, phase: HELP,     arc_beat: mechanism_proof,     narrative_role: "why it persists",        word_target: 760}
    - {chapter: 3, phase: HEALING,  arc_beat: turning_point,       narrative_role: "first interruption",     word_target: 760}
    - {chapter: 4, phase: HOPE,     arc_beat: practice_under_pressure, narrative_role: "harder context",     word_target: 760}
    - {chapter: 5, phase: HOPE,     arc_beat: embodiment,          narrative_role: "identity shift",         word_target: 760}
  compatible_tiers: [A, B, C]
  compatible_structural_formats: [F003, F005, F015]
  derived_from: micro_book_15
  authority_doc: docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md

compact_book_5ch_20min:
  format_id: compact_book_5ch_20min
  display_name: "Compact 5-chapter / 20 min"
  duration_minutes: 20
  audio_runtime_minutes: [16, 22]
  word_target_min: 4000
  word_target_max: 5500
  word_target_canonical: 4750
  chapter_count: 5
  sections_per_chapter: 10
  variants_per_section: 5
  scene_section_indices: [2, 5, 9]
  word_budget_per_section: 95
  beat_compression_strategy: "hope_doubled"
  beat_sheet:
    - {chapter: 1, phase: HARDSHIP, arc_beat: recognition,         narrative_role: "name the pattern",       word_target: 950}
    - {chapter: 2, phase: HELP,     arc_beat: mechanism_proof,     narrative_role: "why it persists",        word_target: 950}
    - {chapter: 3, phase: HEALING,  arc_beat: turning_point,       narrative_role: "first interruption",     word_target: 950}
    - {chapter: 4, phase: HOPE,     arc_beat: practice_under_pressure, narrative_role: "harder context",     word_target: 950}
    - {chapter: 5, phase: HOPE,     arc_beat: embodiment,          narrative_role: "identity shift",         word_target: 950}
  compatible_tiers: [A, B, C]
  compatible_structural_formats: [F003, F005, F012, F015]
  derived_from: micro_book_20
  authority_doc: docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md

compact_book_8ch_30min:
  format_id: compact_book_8ch_30min
  display_name: "Compact 8-chapter / 30 min"
  duration_minutes: 30
  audio_runtime_minutes: [25, 35]
  word_target_min: 5500
  word_target_max: 7500
  word_target_canonical: 6500
  chapter_count: 8
  sections_per_chapter: 10
  variants_per_section: 5
  scene_section_indices: [2, 5, 9]
  word_budget_per_section: 81
  beat_compression_strategy: "two_per_phase"
  beat_sheet:
    - {chapter: 1, phase: HARDSHIP, arc_beat: recognition,            narrative_role: "name the pattern",     word_target: 812}
    - {chapter: 2, phase: HARDSHIP, arc_beat: cost_exposure,          narrative_role: "what it costs",        word_target: 812}
    - {chapter: 3, phase: HELP,     arc_beat: mechanism_proof,        narrative_role: "why it persists",      word_target: 812}
    - {chapter: 4, phase: HELP,     arc_beat: reframe,                narrative_role: "protection not flaw",  word_target: 812}
    - {chapter: 5, phase: HEALING,  arc_beat: turning_point,          narrative_role: "first new rep",        word_target: 812}
    - {chapter: 6, phase: HEALING,  arc_beat: practical_interruption, narrative_role: "everyday pressure",    word_target: 812}
    - {chapter: 7, phase: HOPE,     arc_beat: practice_under_pressure, narrative_role: "hard pressure",       word_target: 812}
    - {chapter: 8, phase: HOPE,     arc_beat: embodiment,             narrative_role: "identity shift",       word_target: 812}
  compatible_tiers: [A, B]
  compatible_structural_formats: [F003, F006, F007, F011]
  derived_from: short_book_30
  authority_doc: docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md
```

Notes:

- `scene_section_indices: [2, 5, 9]` mirrors `SCENE_SECTION_INDICES` in
  `phoenix_v4/planning/story_planner.py:68`. Indices are positional within a
  10-section chapter, so they hold across compact and standard formats
  unchanged. No story_planner edit is needed beyond verification.
- `compatible_structural_formats` re-uses entries already defined for the
  derived-from runtime in `config/format_selection/format_registry.yaml` so
  no structural format edits are needed.
- `audio_runtime_minutes` is a tuple (lo, hi). The existing
  `duration_minutes` scalar is kept for backward compatibility with code
  paths that read a single number.

---

## 5. Beat compression rationale

### 5-chapter compact (15-min and 20-min)

Strategy: `hope_doubled` (1 + 1 + 1 + 2 across HARDSHIP / HELP / HEALING /
HOPE).

- HARDSHIP gets 1 chapter because recognition is fast in compact runtimes —
  the reader already self-selected by topic. Lingering in HARDSHIP for two
  chapters at this band re-creates the "weak escalation" warning we see at
  `governance_report.chapter_contract_warnings` for chapters 9–12 in the
  current micro_book runs.
- HELP gets 1 chapter, anchored on TEACHER_DOCTRINE in section_06 (see §6).
  This is the mechanism beat; it earns its own chapter so the teacher voice
  is not buried in a multi-beat chapter.
- HEALING gets 1 chapter (turning_point only) because first-rep evidence
  needs only one good scene at this length.
- HOPE gets 2 chapters: practice_under_pressure (escalation) and embodiment
  (close). Bestseller embodiment must land with body-level texture; in a
  single shared HOPE chapter it competes with practice_under_pressure for
  scene budget and loses, which is what produces today's
  `chapter_flow` MISSING_CLEAR_POINT for the closing chapters in the
  micro_book runs.

### 8-chapter compact (30-min)

Strategy: `two_per_phase` (2 + 2 + 2 + 2). Symmetric, easier to validate,
and matches the eight distinct narrative roles (recognition, cost_exposure,
mechanism_proof, reframe, turning_point, practical_interruption,
practice_under_pressure, embodiment). All eight roles are already present in
`distinct_roles` from the existing run, so atom selection works without new
content.

---

## 6. TEACHER_DOCTRINE slot placement

Source: `phoenix_v4/planning/beatmap_compile.py:48` — `TEACHER_DOCTRINE`
sits at section_06 of the SOMATIC_10_SLOT_GRID. Source:
`phoenix_v4/planning/beatmap_compile.py:76` — its 6-hour baseline
SOMATIC_WORD_BUDGET is **460 words**.

That 460-word budget assumes a ~4,520 word/chapter scale (12 chapters,
six-hour book). Compact formats keep the slot but compress its budget
proportionally:

| Runtime | Per-chapter target | TEACHER_DOCTRINE budget |
| --- | --- | --- |
| 6-hour baseline (today) | ~4,520 | 460 |
| `compact_book_5ch_15min` | 760 | **~80** (rounded) |
| `compact_book_5ch_20min` | 950 | **~96** |
| `compact_book_8ch_30min` | 812 | **~83** |

(Math: `460 * (per_chapter_target / 4520)`. The previous draft's "~38–48
words" target is too tight — at that budget the teacher voice cannot land a
single complete proof. ~80–100 words per chapter is the operational floor.)

Slot placement (section_06) is **unchanged**. Word target becomes
runtime-aware, gated by the engineering PR (§8).

---

## 7. EI v2 fit

Composite EI v2 score targets (based on
`/tmp/pearl_prime_runs/*/quality_summary.json`):

| Runtime | EI v2 today | Compact target |
| --- | --- | --- |
| `micro_book_15` | 0.4753 (FAIL — below 0.5 floor) | ≥ 0.55 |
| `micro_book_20` | 0.5843 | ≥ 0.55 (hold) |
| `short_book_30` | 0.6386 | ≥ 0.60 (improve) |

Why short formats lose density today: per-section budget is too small to
carry both the somatic anchor and the emotional shift — the composer
either drops scene-anchor density (hurts somatic_precision) or drops
emotional micro-shifts (hurts EI). Per-section budgets in the compact
formats (76 / 95 / 81 words) are sized so a single anchor + a single
emotional micro-shift fit in one section, instead of fighting for ~50
words apiece on the 12-chapter spine.

The compact formats are **not** expected to match `standard_book` EI
density. They are expected to be acceptable-grade emotional intelligence
at compact runtime. The 0.55 floor matches `book_quality_gate.yaml`
soft_thresholds for compact-band publication.

---

## 8. Wiring requirements (follow-up engineering PR — NOT this PR)

| File | Change | Why |
| --- | --- | --- |
| `phoenix_v4/planning/enrichment_select.py` | Extend `_max_extra_chunks_for_format` (currently lines 514–533) to recognize `compact_book_5ch_15min`, `compact_book_5ch_20min`, `compact_book_8ch_30min` and apply `base = 1` for all three. The slot_target_words divisor stays the same; only the base extra-chunk allowance changes vs. today's `base = 0` for `micro_book_*`. | Compact formats get one extra variant per slot to restore atom-stacking depth that the 12-chapter spine collapsed. |
| `phoenix_v4/planning/beatmap_compile.py` | Make `SOMATIC_WORD_BUDGET["TEACHER_DOCTRINE"]` (line 76) runtime-aware. Default 460 stays for ≥ standard_book; compact runtimes scale to per-chapter target × (460 / 4520). | TEACHER_DOCTRINE must compress with the chapter, not stay at 460 words against a 760-word chapter. |
| `phoenix_v4/planning/story_planner.py` | **No change required.** `SCENE_SECTION_INDICES = (2, 5, 9)` (line 68) is positional within a 10-section chapter and applies to compact formats unchanged. The engineering PR should add a unit assertion that confirms this. | Confirms invariant. |
| `config/quality/book_quality_gate.yaml` | Add three new entries under `runtime_policies`: `compact_book_5ch_15min: { default_reject: false, allow_override: true }` (and same for the other two). | Compact formats are designed to ship; they should not inherit the `default_reject: true` from `micro_book_15` / `micro_book_20`. |
| `config/format_selection/format_registry.yaml` | Append the three YAML blocks from §4 under `runtime_formats:`. Do not modify existing entries. | Single source of truth. |

The follow-up PR is expected to be **code + config only**. This authority
doc is not edited again unless a finding from the test plan (§10) forces a
schema revision.

---

## 9. Migration / rollback plan

### Phase 1 — shadow-render

1. With the engineering PR open, run `gen_z_professionals × anxiety` at
   each new compact runtime in **draft mode**, against
   `book_plan_id = ref_anxiety_genz_1h_v1`, alongside the current
   `micro_book_20_draft` run.
2. Diff outputs by:
   - `quality_summary.book_quality_gate.release_band`
   - `quality_summary.gates.chapter_flow.status`
   - `quality_summary.gates.ei_v2.composite`
   - `book_pass_report.checks.word_budget.word_count`
3. Acceptance: compact formats land in band, chapter_flow PASS, EI v2 ≥
   0.55. Today's micro_book runs are kept producing for comparison until
   acceptance.

### Phase 2 — feature flag

1. Gate compact formats behind a runtime-format allowlist
   (`PEARL_PRIME_COMPACT_FORMATS_ENABLED=1`) inside the format selector.
2. Operator-controlled rollout per brand × topic.
3. New catalog configs may opt into compact runtimes; existing configs
   stay on their current runtime by default.

### Phase 3 — promotion

1. Once 10+ catalog configs have shipped at compact runtimes with
   `release_band = Pass` or `release_band = Hold (override)`, remove the
   feature flag.
2. Optionally: deprecate `micro_book_15` and `micro_book_20` with a
   redirect (selector silently maps requests to the matching compact
   runtime). This is reversible and out-of-scope for the wiring PR.

### Rollback

If acceptance fails at Phase 1 or 2:

- Revert the wiring PR (single revert; this doc stays as historical
  rationale).
- Compact runtime IDs disappear from `format_registry.yaml`; selector
  fails-closed for any in-flight catalog config requesting them.
- No data migration needed — books already rendered at compact runtimes
  remain valid artifacts; only future renders are affected.

---

## 10. Test plan

Minimum acceptance suite for the engineering PR:

1. Render `gen_z_professionals × anxiety` at `compact_book_5ch_15min`
   (production profile).
   - Expected: `book_pass.word_budget.status = PASS`, `word_count ∈
     [3000, 4500]`.
   - Expected: `chapter_flow.status = PASS` (failed_chapters ≤ 1 of 5).
   - Expected: `ei_v2.composite ≥ 0.55`.
   - Expected: `book_quality_gate.release_band ∈ {Pass, Hold}`.
2. Render `gen_z_professionals × anxiety` at `compact_book_8ch_30min`
   (production profile).
   - Expected: word_count ∈ [5500, 7500], chapter_flow PASS,
     ei_v2.composite ≥ 0.60.
3. Render `gen_z_professionals × anxiety` at `compact_book_5ch_20min`
   (draft, side-by-side with the current
   `/tmp/pearl_prime_runs/micro_book_20_draft/`).
   - Expected: same EI v2 composite (±0.03) at lower word_count, chapter
     flow PASS, no `chapter_contract_warnings` from chapters 6–12 (those
     chapters do not exist in compact 5-chapter spine).
4. Unit assertion: `SCENE_SECTION_INDICES == (2, 5, 9)` is treated as an
   invariant across compact formats.
5. Unit assertion: TEACHER_DOCTRINE per-section target for each compact
   runtime is in [70, 100] words.

Test plan does **not** require new personas, topics, or engines. All
inputs are existing canonical entries.

---

## 11. Open questions

1. Should `compact_book_5ch_15min` accept tier C topics, or restrict to
   A/B like `compact_book_8ch_30min`? The schema in §4 currently allows
   C; revisit if C-tier compact books underperform EI v2 ≥ 0.55 in Phase
   1 shadow runs.
2. Is the per-section 76-word floor (5ch/15min) compatible with the
   editorial gate's `clipped_fragment.max_words = 4 + require_all_lower`
   filter under heavy compression? Phase 1 must inspect editorial WARN
   counts.
3. Does `book_pass.identity_stages` (currently FAIL on micro_book_20
   draft because recognition/mechanism/integration tags don't fire on
   short text) need a compact-aware threshold, or do the new beat sheets
   resolve it organically? Defer to test plan §10.

---

# Compact-Subset Proof — `compact_chapter_subset` honored vs not (2026-06-15)

**What this proves:** the operator's structural hypothesis — *fewer chapters for shorter
books* — directly cuts F1 register-repetition **and** word-overshoot, and the lever is a
**two-line bug fix**, not new machinery.

## Root cause (verified on `origin/main`)

The `compact_chapter_subset` mechanism (PR-D-SPINE-01, ratified, shipped in #865) was
**silently inert** in two places that omit `runtime_format=`:

| Site | Before | After (this fix) |
|------|--------|------------------|
| `scripts/pilot/run_spine_pipeline.py` | `load_spine(topic, REPO_ROOT)` | `load_spine(topic, REPO_ROOT, runtime_format=args.runtime_format)` |
| `phoenix_v4/planning/beatmap_compile.py:440` | `load_spine(shaped_spine.topic, root)` | `load_spine(..., runtime_format=shaped_spine.runtime_format)` |

The real entry point (`scripts/run_pipeline.py:613`) already passes `runtime_format`, so the
chapter **count** survived end-to-end there — but `beatmap_compile.py:440` re-loaded the
**full** spine for its `by_num` lookup, mapping each subsetted chapter's
`required_sections`/`forbidden_moves` to the **wrong original chapter**. Both sites are now
consistent.

The pilot harness gap is why the published `duration_ladder_20260615` rendered **12 chapters
at every tier** — including `compact_book_8ch_30min`, which *declares* an 8-chapter subset.

## Before / After — `gen_z_professionals × anxiety`, fixed word target, only the subset toggled

| format | variant | chapters | words | vs word_range | F1 | F2 | F7 | verdict |
|--------|---------|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| `compact_book_5ch_15min` | before (bug) | 12 | 7106 | +58% OVER | 17 | 6 | 7 | HARD_FAIL |
| `compact_book_5ch_15min` | **after (fix)** | **5** | **5396** | **+20% OVER** | **6** | 7 | 5 | HARD_FAIL |
| `compact_book_5ch_20min` | before (bug) | 12 | 8138 | +48% OVER | 17 | 7 | 8 | HARD_FAIL |
| `compact_book_5ch_20min` | **after (fix)** | **5** | **7494** | **+36% OVER** | **9** | 7 | 5 | HARD_FAIL |
| `compact_book_8ch_30min` | before (bug) | 12 | 10751 | +43% OVER | 35 | 12 | 11 | HARD_FAIL |
| `compact_book_8ch_30min` | **after (fix)** | **8** | **9352** | **+25% OVER** | **22** | 9 | 8 | HARD_FAIL |

**F1 drop: −65% / −47% / −37%.** Word-overshoot roughly halved at every tier. F7 (practice
density) also falls. Both metrics move monotonically with chapter count.

### What does NOT change: the verdict

All variants stay `HARD_FAIL`. The register verdict is driven **solely by F2** (the only
`HARD_FAIL`-severity finding; `register_gate._aggregate_verdict`). F1 maxes at `FAIL` and
never gates. So this lever improves **prose quality + length** (Lever A); flipping the gate to
PASS additionally needs the **F2** data-layer work (atom-label corruption + teacher-wrapper
templates) owned by **#1601** + atom-repair — *not* this session.

## Option S — default short tiers subset to `chapter_count_default` (operator-chosen 2026-06-15)

The registry already declared `chapter_count_default` = 5 / 8 / 8 for these tiers, but the spine
path ignored it (no `compact_chapter_subset`). Declaring the ratified subset patterns wires the
spine path to honor the existing SSoT counts. Before/after via the **real registry path**:

| format | declared count | before (12ch) | after (subset) | F1 | overshoot |
|--------|:--:|:--:|:--:|:--:|:--:|
| `micro_book_15` | 5 | 12ch / 7393w | **5ch / 5354w** | 16 → **3** (−81%) | +64% → **+19%** |
| `micro_book_20` ⁽ᶠᵘ⁾ | 6 | 12ch / 8475w | **6ch / 6455w** | 20 → **14** (−30%) | +54% → **+17%** |
| `short_book_30` | 8 | 12ch / 10839w | **8ch / 8445w** | 35 → **25** (−29%) | +45% → **+13%** |
| `one_hour_book` | 8 | 12ch / 13095w | **8ch / 12291w** | 39 → **28** (−28%) | +31% → **+23%** |

⁽ᶠᵘ⁾ `micro_book_20` added in the **follow-up** below — it was the one short-tier sibling
#1612 missed.

`one_hour_book` still overshoots +23% (12291 vs 10000): the atom-floor can't hit the 8–10k band
at 8 chapters without per-chapter budget tightening — a **depth-budget / duration-derivation**
follow-up, not a chapter-count one. Chapter count still cut overshoot 8pts and F1 28%.

## Follow-up (2026-06-15): `micro_book_20` gap + full `chapter_count_default < 12` audit

#1612 declared subsets on `micro_book_15`(5) / `short_book_30`(8) / `one_hour_book`(8) — but
**missed `micro_book_20`**, which declares `chapter_count_default: 6` with no
`compact_chapter_subset`. The spine path therefore rendered it at the full 12 chapters
(8475w, **+54% over** [3000,5500], F1=20). This follow-up adds
`compact_chapter_subset: [1, 3, 4, 7, 10, 12]` — the 5ch anchor set `[1,4,7,10,12]` + `ch3`
(`pattern_mapping`, the same 2nd-HARDSHIP keeper the 8ch subset uses; drops `ch2`=`origin`).
Result: **6ch / 6455w / +17% over / F1 20→14** (see the ⁽ᶠᵘ⁾ row above).

### Audit — every `runtime_format` with `chapter_count_default < 12` and no subset

| format | ch_default | spine-path? | decision | rationale |
|--------|:--:|:--:|--------|-----------|
| `micro_book_20` | 6 | **yes** | **subset added** `[1,3,4,7,10,12]` | first-class tier (word_range, F015/F003, consumed); overshoots +54% at 12ch — same gap class as `micro_book_15` |
| `standard_book` | 10 | yes | **excluded (intentional full-12)** | `fill_regime: cap`, `cap_word_target: 22000` is tuned for the 12-chapter **gold** render (22346w = **+2%**, on-target — see control below). `ch_default=10` governs the *auto-plan* path (`book_structure_plan`), not the spine path. Flipping the flagship spine render 12→10 is an **operator-tier product decision** (AUTO-PLAN-SSOT-01-AMENDMENT: *"Most consequential… preserve"*), out of this envelope. |
| `five_min_practice`, `pocket_guide`, `ten_things_to_do`, `symptom_to_action_atlas`, `daily_text_audio_companion`, `crisis_cards`, `weekly_challenge_pack`, `faq_audiobook`, `myth_vs_mechanism`, `protocol_library` | 5–10 | **no** | **out of scope (modular)** | Group-A backfill: **not consumed** by `format_selector` / `enrichment_select` / `knob_apply` (registry comment + AMENDMENT verified 0 hits); no `word_range` (cannot be budget-scored); modular content shapes (FAQ / cards / listicle / atlas / protocols), not the 4-phase narrative arc the subset assumes. A subset on these would never be read. |

Formats with `chapter_count_default ≥ 12` (`extended_book_2h`=14, `deep_book_4h`=16,
`deep_book_6h`=20) never over-render — the 12-chapter spine is their ceiling — so they need no
subset.

### Full-spine control — proof `standard_book` is NOT a gap

| format | variant | chapters | words | vs word_range | F1 | verdict |
|--------|---------|:--:|:--:|:--:|:--:|:--|
| `standard_book` | full_spine_12ch | 12 | 22346 | **+2% OVER** | 61 | HARD_FAIL |

`standard_book` declares no subset, so it renders the full 12-chapter gold arc either way and
lands **on-target** (22346 vs the 22000 cap; matches the published ladder's 22155/+1%). Subsetting
it to 10 would render ~18.5k — **under** `cap_word_target` and away from the tuned gold target.
This is the empirical basis for its exclusion: no overshoot ⇒ no gap. (The 10 modular formats are
absent here because they carry no `word_range` to score against.)

## Faithfulness check (this harness vs the published ladder)

The `before_12ch` column above doubles as the faithfulness check: re-rendering at 12 chapters
reproduces the published `duration_ladder_20260615` within backup-commit drift (micro 7393 vs
7193 / F1 16 vs 14; short 10839 vs 10561 / 35 vs 30; one_hour 13095 vs 12780 / 39 vs 34). Hourly
auto-backup commits moved `origin/main` past the ladder's `ff896141e`; the before/after deltas
are internally consistent (same code, same seed).

## Reproduce

```bash
PYTHONPATH=. python3 artifacts/qa/duration_ladder_subset_proof_20260615/gen_proof.py
```

Deterministic atom composition; **no paid LLM API** (CLAUDE.md tier policy). Scored with
`origin/main`'s `register_gate.py` for parity with the published ladder (this branch carries a
stripped copy). Per-variant `book.txt` + `register_report.json` are written under each
`<format>__<variant>/` subdir; `SUMMARY.json` holds the table data.

# Duration Correctness Audit — Pearl Prime

**Date:** 2026-06-11 · **Mode:** plan-only (no assembly, no LLM) · **Books planned:** 1,000 · **Scope:** 10 fully-specced runtime formats · **Locale:** en-US (CJK flagged separately)

---

## TL;DR (the three answers you asked for)

1. **"Is our hour book really 1h15m?"** — It's worse. The **`standard_book` advertised at 55 min is really ~2h23m as an audiobook** (+161%). It's not a rounding gap; the label is off by ~2.6×.

2. **Where it goes over its own cap (Mode 1):** Almost entirely **`standard_book`** — **94% of gold books exceed the 20,000-word cap** (median ~21,500, +7.6%). And that cap was *already raised three times* (13k→18k→20k) to stop earlier overshoots from failing gates. Against the original 13k design intent, gold standard books are **+65%**.

3. **Where the duration is just mis-advertised (Mode 2):** **Nearly everywhere.** Duration is a **hand-set label**, not a computed value. The product is consumed as audiobook at **150 WPM**, but the labels imply **125–364 WPM** with no consistent formula. At 150 WPM, **7 of 10 formats run long past tolerance**; only `deep_book_4h` (−11%) and `deep_book_6h` (+2%) are honest.

**The books are fine. The labels are wrong.** The fix is to re-derive every format's advertised duration from its real word target at 150 WPM — not to shrink the books.

---

## 1. How duration is actually determined

**There is no word→minute formula in the advertising path.** Each runtime format carries a **hand-set fixed `duration_minutes`** in `config/format_selection/format_registry.yaml`. It is never derived from word count.

The **only** word→minute conversion in the entire codebase:

```yaml
# config/duration_scorecard.yaml
duration_adherence_scorecard:
  tts_wpm: 150            # "TTS WPM estimate (standard audiobook pace)"
  duration_tolerance_pct: 10
```

…and it is used **only** inside the read-only `phoenix_v4/ops/duration_adherence_scorecard.py` (`estimated_min = actual_words / 150`) — a *measurement* tool, never the source of the advertised number.

**Intended consumption = audiobook at 150 WPM**, confirmed twice:
- `tts_wpm: 150` (config), and
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` §413 (verbatim): *"read the atom sequence aloud at **TTS pace (flat, 150 WPM)**."*

So the **honest** label is `minutes = words / 150` for the audiobook, and `words / 230` for the ebook reading edition (Pearl Prime ships both). This audit checks both.

### The two word-target regimes (root of Mode 1)

| regime | rule | source |
|---|---|---|
| **midpoint** | plan total validated to **word_range midpoint ±10%** | `phoenix_v4/planning/beatmap_compile.py:651` |
| **cap** | gold/depth-fill pins to the **ceiling** | QA gold `standard_book` budget.json: pre_depth 19,026 → depth-fill 20,000 (=cap) → render **21,454** |
| **floor** | fills to just above the **floor** | `deep_book_6h` registry comment: "compose retains ~72% → ~52K final (clear 50K floor)" |

The gold path (the **$-makers**) targets the **cap** for `standard_book`. The registry ceiling was raised **13k→18k→20k** specifically so gold renders (~19.9k observed) would stop tripping the word-range gate — i.e. **the cap was moved to match the overshoot, while the 55-minute label never moved.**

---

## 2. Format inventory (10 specced + 10 stubs)

**10 fully-specced** (have both `duration_minutes` and `word_range` — measurable):

| format | adv. min | word_range | implied WPM @mid | @cap |
|---|---|---|---|---|
| micro_book_15 | 15 | 2,500–4,500 | 233 | 300 |
| micro_book_20 | 20 | 3,000–5,500 | 212 | 275 |
| short_book_30 | 30 | 4,500–7,500 | 200 | 250 |
| **standard_book** | **55** | **9,000–20,000** | **264** | **364** |
| extended_book_2h | 120 | 17,000–25,000 | 175 | 208 |
| deep_book_4h | 240 | 20,000–40,000 | 125 | 167 |
| deep_book_6h | 360 | 50,000–72,000 | 169 | 200 |
| compact_book_5ch_15min | 15 | 3,000–4,500 | 250 | 300 |
| compact_book_5ch_20min | 20 | 4,000–5,500 | 238 | 275 |
| compact_book_8ch_30min | 30 | 5,500–7,500 | 217 | 250 |

**Honest listening WPM = 150.** Implied WPM ranges **125 → 364** — a 2.9× spread with no consistent formula. Only `deep_book_4h` (125 @mid) sits at/under the honest 150.

**10 stub formats** — `five_min_practice, pocket_guide, ten_things_to_do, symptom_to_action_atlas, daily_text_audio_companion, crisis_cards, weekly_challenge_pack, faq_audiobook, myth_vs_mechanism, protocol_library` — have **only `chapter_count_default`; no `duration_minutes`, no `word_range`.** They have **no advertised-duration contract at all** (so they can't be over/under — but they also can't ship a duration honestly until both fields are added).

---

## 3. MODE 2 — the marketing gap (advertised vs real duration)

The representative reality across 1,000 projected books. **Listening = the product's intended pace (150 WPM); Reading = ebook edition (230 WPM).**

| format | advertised | **real listening** | gap (listen) | real reading | gap (read) | verdict @ ±15/25 band |
|---|---|---|---|---|---|---|
| micro_book_15 | 15 min | **25.3 min** | **+68%** | 16.5 min | +10% | 🔴 ACT |
| micro_book_20 | 20 min | **29.8 min** | **+49%** | 19.4 min | −3% | 🔴 ACT |
| short_book_30 | 30 min | **42.8 min** | **+43%** | 27.9 min | −7% | 🔴 ACT |
| **standard_book** | **55 min** | **143.4 min (2h23m)** | **+161%** | 93.5 min | +70% | 🔴 **ACT (severe)** |
| extended_book_2h | 120 min | 149.2 min | +24% | 97.3 min | −19% | 🟡 NOTE |
| deep_book_4h | 240 min | 214.2 min | −11% | 139.7 min | −42% | 🟢 FINE |
| deep_book_6h | 360 min | 368.2 min | +2% | 240.1 min | −33% | 🟢 FINE |
| compact_book_5ch_15min | 15 min | **26.8 min** | **+78%** | 17.4 min | +16% | 🔴 ACT |
| compact_book_5ch_20min | 20 min | **34.3 min** | **+72%** | 22.4 min | +12% | 🔴 ACT |
| compact_book_8ch_30min | 30 min | **47.5 min** | **+58%** | 31.0 min | +3% | 🔴 ACT |

**Read it this way:**
- **At the intended audiobook pace (150 WPM), 7 of 10 formats run long past the act threshold.** The micro/short/compact formats are ~1.5× their label; `standard_book` is ~2.6×.
- **At reading pace (230 WPM), the small formats are roughly honest (±15%), but the big formats run *short*** (`deep_book_4h` −42%, `deep_book_6h` −33%) and `standard_book` is still +70%. This tells us the labels were set as loose *reading-ish* estimates at ~200–260 WPM and never reconciled to the 150 WPM audiobook the product actually ships.
- **`standard_book` is the headline.** Advertised ≈ "1 hour"; real audiobook ≈ **2h23m**. At the 20k cap it's 133 min (+142%); the real ~21.5k gold render makes it 143 min (+161%).

---

## 4. MODE 1 — overshoot of the format's own word cap

Does the pipeline blow past `word_range[max]`? **Concentrated in `standard_book`; minor in the narrow-range compact formats; absent elsewhere.**

| format | cap | proj. median | % books **over cap** | median vs cap | note |
|---|---|---|---|---|---|
| **standard_book** | 20,000 | 21,514 | **94%** | **+7.6%** | cap-pinned by design; cap already raised 13k→18k→20k |
| compact_book_8ch_30min | 7,500 | 7,130 | 21% | −4.9% | narrow range; render inflation tips the top tail over |
| compact_book_5ch_20min | 5,500 | 5,146 | 19% | −6.4% | narrow range |
| extended_book_2h | 25,000 | 22,390 | 9% | −10.4% | occasional top-tail |
| compact_book_5ch_15min | 4,500 | 4,014 | 6% | −10.8% | |
| micro_book_15 | 4,500 | 3,790 | 0% | −15.8% | fills to midpoint, well under cap |
| micro_book_20 | 5,500 | 4,464 | 0% | −18.8% | |
| short_book_30 | 7,500 | 6,434 | 0% | −14.2% | |
| deep_book_4h | 40,000 | 32,129 | 0% | −19.6% | midpoint regime |
| deep_book_6h | 72,000 | 55,229 | 0% | −23.3% | floor regime |

**Findings:**
- **`standard_book` is the one real Mode-1 offender** — 94% of gold books exceed the cap (render ~+7.6% over the 20k depth-fill target). This was historically "fixed" by **raising the cap**, which masks rather than resolves it: the words crept 13k→21.5k while the duration label stayed at 55 min.
- **Narrow-range compact formats** (`compact_5ch_20`, `compact_8ch_30`) tip over their caps in ~20% of books — they have little headroom between midpoint and cap, so render inflation (+7%) pushes the top tail across. A modest cap-headroom or a render-trim would clear this.
- **Everything else sits comfortably under cap** — these formats are *not* over-producing words. Their problem is purely Mode 2 (the label).

---

## 5. Mode 1 vs Mode 2 — which is which

| | **Mode 1** (overshoot own word cap) | **Mode 2** (advertised duration is wrong) |
|---|---|---|
| What | assembly exceeds `word_range[max]` | `duration_minutes` ≠ words / 150 |
| Cause | gold depth-fill pins to cap + render +7% | hand-set label, no formula, implied 125–364 WPM |
| Who | **`standard_book`** (94%); minor compact tails | **almost every format** (7/10 act, 1 note, 2 fine) |
| Severity | contained, partly self-masked by cap-raises | **systematic and large** (up to +161%) |
| Fix | raise/accept cap, or render-trim | **re-derive the label from word_target / 150** |

**The dominant problem is Mode 2.** Mode 1 is real but small and concentrated; Mode 2 is broad and large. A single duration-derivation fix resolves most of it.

---

## 6. Tolerance-band summary (on the listening gap — the intended pace)

Band: **≤±15% fine · 15–25% note · >25% act.**

- 🟢 **FINE (2):** `deep_book_4h` (−11%), `deep_book_6h` (+2%)
- 🟡 **NOTE (1):** `extended_book_2h` (+24%)
- 🔴 **ACT (7):** `standard_book` (+161%), `compact_5ch_15` (+78%), `compact_5ch_20` (+72%), `micro_15` (+68%), `compact_8ch_30` (+58%), `micro_20` (+49%), `short_30` (+43%)

---

## 7. Method & provenance (every number is sourced)

- **Plan-only.** No prose generated, no LLM, no paid API. Config-read + atom-count + arithmetic.
- **Intended pace 150 WPM** ← `config/duration_scorecard.yaml` + OVERLAY_SPEC §413. **Reading 230 WPM** ← standard ebook reading rate.
- **Mode 2 is deterministic** — pure registry math (`words / wpm`), no modeling. Reported at word_range floor/mid/cap in `projection_results.json`.
- **Mode 1 / projection** — 1,000 books over the live `atoms/` coverage frame (14 personas × 15–21 topics, gold combos ×3 weighted). Per book: `projected_words = regime_target × render_inflation`.
  - `regime_target`: cap (`standard_book`), floor×~1.04 (`deep_book_6h`), midpoint±10% (rest) — each with the evidence above.
  - `render_inflation = 1.073` — **MEASURED** from the one clean gold render (`21,454 / 20,000`). **Calibration check: projected `standard_book` median 21,514 vs real 21,454 = 0.3% error.**
- **Atom distributions** — 66,321 real per-variant word counts from 4,779 `CANONICAL.txt` pools (`atom_wordcount_distributions.json`).

### Caveats (read before acting)
- **Single render anchor.** `render_inflation` (1.073) is measured on `standard_book` only and applied to all formats. The per-format render-vs-target overshoot for the *other* 9 formats is **extrapolated** — a **dry-run-assembly pass** (invoke depth-fill + render once per format, no LLM if the renderer is deterministic) would confirm Mode 1 per format. Mode 2 needs no such follow-up (it's deterministic).
- **`bare6beat_skeleton_words` is a lower bound, not pre-depth.** It's one variant per 6-beat slot; production uses a far richer 15+ slot beatmap (QA pre-depth was 19,026). Do **not** read the production/skeleton ratio as "% padding."
- **CJK not covered.** This is English word-count math. `ja-JP/zh-TW/zh-CN` use **character counts** and different narration rates (Mandarin ~250–300 chars/min; Japanese differs). Applying the English 150 WPM to CJK would be wrong — **CJK needs its own char-based duration audit.**

---

## Artifacts

- `duration_audit_data.tsv` — 1,000 rows (one per planned book), all columns
- `projection_results.json` — per-format aggregates + Mode-2 deterministic floor/mid/cap table
- `atom_wordcount_distributions.json` — 66k real atom variant measurements
- `project_1000_books.py`, `measure_atom_distributions.py` — reproducible, seeded
- `RECOMMENDATIONS.md` — per-format fixes + what needs a Pearl_Architect spec
- `DURATION_AUDIT_DECK.pptx` — operator-facing deck

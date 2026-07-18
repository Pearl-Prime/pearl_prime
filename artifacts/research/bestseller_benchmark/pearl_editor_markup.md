# Pearl_Editor markup — internal long-form probe + canary (9-dimension rubric)

**Scope.** This pass scores **eleven in-repo Phoenix texts**: `internal_deep6h_ch01` … `internal_deep6h_ch10` (first chapters from the `deep_book_6h` scratch manuscript) plus `_canary_standard_book_ch1` (first chapter of the `standard_book` scratch artifact). These are **not** the copyrighted first chapters of the ten commercial titles listed in `book_corpus.yaml`; commercial text ingest is still pending for a title-identified benchmark.

**Rubric (1–10 each).** Hook, Thesis clarity, Mechanism explanation, Specific stories, Memorable lines, Voice consistency, Pacing, Emotional accuracy (anxiety/burnout realism), Would-keep-reading. **Aggregate** = mean of the nine.

**Method.** Each row was read open (first ~600 words) and spot-checked mid-chapter for repetition and voice breaks. Annotations quote the **on-disk** sample files under `artifacts/research/bestseller_benchmark/samples/`.

---

## Scorecard

| Sample ID | Hook | Thesis | Mechanism | Stories | Lines | Voice | Pace | Emotion | Keep | **Avg** |
|-----------|------|--------|-----------|---------|-------|-------|------|---------|------|--------|
| internal_deep6h_ch06 | 7 | 7 | 7 | 6 | 6 | 7 | 7 | 8 | 8 | **7.11** |
| internal_deep6h_ch02 | 6 | 6 | 6 | 7 | 6 | 6 | 7 | 7 | 7 | **6.44** |
| internal_deep6h_ch07 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | 7 | **6.33** |
| internal_deep6h_ch05 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | **6.22** |
| internal_deep6h_ch08 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 7 | 7 | **6.11** |
| internal_deep6h_ch04 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 7 | 7 | **6.00** |
| internal_deep6h_ch10 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 6 | 7 | **6.00** |
| internal_deep6h_ch09 | 6 | 6 | 6 | 6 | 5 | 6 | 6 | 7 | 7 | **5.89** |
| internal_deep6h_ch03 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 7 | **5.56** |
| internal_deep6h_ch01 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 6 | **5.11** |
| _canary_standard_book_ch1 | 5 | 4 | 5 | 6 | 4 | 3 | 4 | 5 | 5 | **4.33** |

---

## Ranked (best → worst on aggregate)

1. internal_deep6h_ch06 — 7.11  
2. internal_deep6h_ch02 — 6.44  
3. internal_deep6h_ch07 — 6.33  
4. internal_deep6h_ch05 — 6.22  
5. internal_deep6h_ch08 — 6.11  
6. (tie) internal_deep6h_ch04 / internal_deep6h_ch10 — 6.00  
8. internal_deep6h_ch09 — 5.89  
9. internal_deep6h_ch03 — 5.56  
10. internal_deep6h_ch01 — 5.11  
11. **_canary_standard_book_ch1 — 4.33 (last / 11)**

---

## Per-sample notes (3 annotations each)

### internal_deep6h_ch01 (avg 5.11)

- **Thesis / mechanism:** Opens with contemplative abstractions (“Every person carries the capacity for awakening…”) before grounding workplace anxiety — thesis reads like a different book than the persona promise.  
- **Voice:** Dense reuse of spiritual-expository cadence (“The Buddha taught…”, “Most people believe enlightenment…”) stacks committee tone.  
- **Pacing:** Long runway of doctrine before scene; hook is calm, not urgent.

### internal_deep6h_ch02 (avg 6.44)

- **Stories:** More situational texture than ch01; reader can feel a through-line even when teaching frames repeat.  
- **Memorable lines:** Some contrast lines land; fewer pure aphorism stacks than ch01.  
- **Voice:** Still leans teacherly, but less monolithic than ch01.

### internal_deep6h_ch03 (avg 5.56)

- **Hook:** Title-adjacent framing (“The Pattern Running Your Nervous System”) is clear, but opening paragraphs recycle prior-chapter diction — cognitive déjà vu hurts hook freshness.  
- **Mechanism:** Explains mind habits abstractly; limited embodied consequence in the opening window.  
- **Pacing:** Feels like mid-book continuation despite being chapter three textually.

### internal_deep6h_ch04 (avg 6.00)

- **Emotional accuracy:** Burnout-adjacent language reads closer to lived work stress than ch01–03 openings.  
- **Voice:** Slightly more varied sentence shapes in the sampled head.  
- **Would-keep-reading:** Enough specificity to earn another page turn.

### internal_deep6h_ch05 (avg 6.22)

- **Mechanism:** Mix of instruction + consequence reads more operational than ch01.  
- **Pacing:** Maintains forward motion; fewer stacked abstractions in the first screen.  
- **Stories:** Still light on named characters, but situational nouns help.

### internal_deep6h_ch06 (avg 7.11 — strongest)

- **Hook:** “Letting The Alarm Ring” + immediate Buddha paragraph still teacherly, but subsequent beats cycle faster and feel more intentional.  
- **Emotional accuracy:** Anxiety/burnout register feels most honest in this set.  
- **Would-keep-reading:** Highest trust that the chapter will land a concrete practice.

### internal_deep6h_ch07 (avg 6.33)

- **Pacing:** Comparable to ch05–06; fewer opening-stacks of pure doctrine than ch01.  
- **Voice:** Mostly one register; occasional sharper line.  
- **Memorable lines:** Moderate quotable density.

### internal_deep6h_ch08 (avg 6.11)

- **Stories / specificity:** Middle of the pack; not as crisp as ch06.  
- **Mechanism:** Adequate explanation; some generic self-help scaffolding.  
- **Keep-reading:** Serviceable, not electric.

### internal_deep6h_ch09 (avg 5.89)

- **Hook:** Functional but familiar; competes with memory of earlier chapters’ phrasing.  
- **Pacing:** Slight sag from repetition of canonical lines reused across manuscript.  
- **Emotion:** Still recognizable anxiety voice, weaker novelty.

### internal_deep6h_ch10 (avg 6.00)

- **Thesis:** Readable; closing-book energy without a fireworks hook.  
- **Voice:** Steady; risks blending with ch08–09 without strong signature opening.  
- **Would-keep-reading:** Acceptable landing chapter tone.

### _canary_standard_book_ch1 (avg 4.33 — **canary**)

- **Quoted hook problem:** The alarm + desk scene opens with promise, then the text stacks repeated visual anchors — e.g. “soft daylight along the sill” appears in tight loops across office / transit beats (`_canary_standard_book_ch1.txt` lines 7–17 region), which reads like template residue, not authorial choice.  
- **Voice inconsistency:** Same file mixes second-person workplace micro-scenes with detached doctrine (“Every person carries the capacity for awakening…”) and bullet-like `---` staccato blocks (lines 27–28 region), which feels like merged pipelines.  
- **Memorable lines (negative example):** Accidental repetition undermines quotability — e.g. “The the train lurches.” (`_canary_standard_book_ch1.txt` line 41) reads like a copy-edit miss, not a stylistic device.

---

## Where the canary sits

On this rubric the canary is **11th of 11** (below the internal deep-book chapters). Relative to the **median** internal aggregate (~6.06), the canary is **materially below** the median, which supports treating manuscript quality as a **first-order risk** *for this artifact path* — **without** yet claiming comparison to external NYT prose until commercial chapters are ingested.

---

## Relation to prior Pearl baseline

The repo’s earlier **3.7 / 10** Pearl_Editor baseline (see sprint governing spec path in operator brief) referred to a different artifact snapshot. This table is **not** a re-score of that same file; it extends the methodology to eleven long samples available on disk for this branch.

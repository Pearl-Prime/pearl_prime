# Duration Gap Verification — our REAL durations vs each platform's winning length

**Date:** 2026-06-13 · **Agent:** Pearl_Research · **Mode:** verification (no padding; real over aspirational)
**Compares:** (a) our 7-tier **ladder targets** + (b) our two **REAL render realities** against the platform targets in `DURATION_PER_PLATFORM_PLAN.md` §2.
**Reality sources:** `artifacts/qa/duration_correctness_audit_20260611/` (1,000-book projection) + `artifacts/qa/duration_marketing_targets_20260613/DURATION_REASSESSMENT.md` §5B (measured JA catalog renders) + the merged registry (#1550).

---

## TL;DR — the verdict

1. **Today we ship ZERO product that wins the flagship paid-book surfaces (full-length Audible / full KDP).** The ladder *has* a tier for it (T7 "Complete," 52k words), but **no confirmed catalog book actually renders that long.**
2. **The bulk catalog renders THIN (~5k words ≈ 33 min ≈ 20 pp).** That length wins **exactly one** surface: **a single podcast episode.** It is a structural loser on every paid-book platform [A6][K8].
3. **The gold/depth-fill path (~21.5k words ≈ 2.4 hr ≈ 86 pp)** — the ~800 high-confidence "$-maker" configs — wins a **podcast season** and a **KDP short-read**, but **misses full Audible (under the 3-hr floor) and full KDP (88<150 pp).**
4. **The existing config routing is actively wrong:** `platform_knob_tuning.yaml` routes `standard_book` (2.45 hr) → Audible while *stating* `ideal_runtime_hours: 5` — it was authored on the old, wrong "55-min standard_book" label and never reconciled to #1550.
5. **Two fixes, cleanly separated:** the **routing** is config (Pearl_Research, in-lane); the **missing 52k-word flagship product** is content-length (routed to the writing program, real length only).

---

## 1. Our two render realities (not the aspirational ladder)

| | **THIN catalog render** (the bulk) | **GOLD / depth-fill render** ($-makers) | Ladder *target* |
|---|---|---|---|
| Representative words | **~5,000** (measured JA 標準書籍 ≈ 5.2k) | **~21,500** (standard_book gold, +7.6% over 20k cap) | 22,000 (T5) |
| Audiobook @150 WPM | **~33 min** | **~143 min (2.4 hr)** | 147 min |
| Ebook print pp @250 w/pg | **~20 pp** | **~86 pp** | 88 pp |
| Source | DURATION_REASSESSMENT §5B (measured, n=4) | DURATION_CORRECTNESS_REPORT §4 (1,000-book projection, render_inflation 1.073 measured) | MARKETING_DURATION_TARGETS |

**The thin render is the honest baseline the brief flagged.** The gold path proves the pipeline *can* reach ~21.5k, but (a) that's still the §5B "標準書籍" tier and (b) even it is below every paid-book platform's full-length norm. **No tier in either reality reaches the T7 52k flagship target** — that tier is presently aspirational.

---

## 2. MEETS / MISSES — both realities + ladder vs every platform

Verdict key: ✅ wins · ⚠️ marginal/wrong-home · ❌ miss · ❌❌ catastrophic miss

| Platform target | THIN (~5k / 33 min / 20pp) | GOLD (~21.5k / 2.4 hr / 86pp) | Ladder T5 (22k) | Ladder T7 (52k) |
|---|---|---|---|---|
| **KDP full ebook** (150–230pp / 35–50k w) | ❌❌ lead-magnet | ❌ short-read (86<150pp) | ❌ short-read | ✅ **MEETS** (208pp) |
| **KDP Short Reads** (<100pp, funnel) | ⚠️ tiny | ✅ fits | ✅ | (overshoots — full book) |
| **Audible** (5–7 hr / 45–63k w; floor 3 hr) | ❌❌ bottom $6.95 tier | ❌ under 3-hr floor (2.4 hr) | ❌ | ✅ **MEETS** (5.8 hr) |
| **Spotify audiobook** (4–6 hr / 36–54k w) | ❌❌ | ❌ below 4 hr | ❌ | ✅ **MEETS** (5.8 hr) |
| **Podcast** (20–40 min/episode) | ✅ **MEETS = 1 episode** | ✅ **MEETS = a season** (8–10 ep) | ✅ season | ✅ multi-season |
| **Apple/Google free AI audiobook** (length-agnostic, EN) | ⚠️ 33-min "sample" | ✅ listable | ✅ | ✅ best value |
| **YouTube teaching** (8–15 min) | (n/a — text; trailer/Short instead) | (n/a) | (n/a) | (n/a) |

**The single most important row:** the **thin render's only ✅ is a podcast episode.** Everything we render today is, on the paid-book surfaces, either a lead-magnet (thin) or a short-read (gold) — **never a flagship audiobook or full ebook.** The gold render's best honest home is a **podcast season**, not an audiobook.

---

## 3. The config routing bug (verified, concrete)

`config/catalog_planning/platform_knob_tuning.yaml` (authority `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md`, last_updated 2026-04-04) — the Audible profile:

```yaml
audible:
  preferred_runtimes: [standard_book, extended_book_2h]   # ← 2.45 hr & 2.3 hr
  max_runtime_hours: 6
  ideal_runtime_hours: 5        # ← states the 5-hr self-help sweet spot…
```

**The contradiction:** `ideal_runtime_hours: 5` is correct (matches Audible's 5–7 hr norm [A4][A5]), but the `preferred_runtimes` it routes — `standard_book` (147 min = 2.45 hr) and `extended_book_2h` (140 min = 2.3 hr) — **cannot reach 5 hr.** The only runtimes that do (`deep_book_4h` ≈ 3.3 hr, `deep_book_6h` ≈ 5.8 hr) are **absent** from Audible's list. The mapping was written when `standard_book` was mislabeled "55 min" (pre-#1550), so someone reasonably-but-wrongly treated `standard_book + extended` as a multi-hour Audible book. **#1550 corrected the label (55→147); this routing was never reconciled, so it now silently routes sub-3-hr books to a 5-hr surface.** Same defect on `spotify` (`ideal_runtime_hours: 3`, routes `short_book_30`/`micro_book_20` = 28–45 min), `apple_books`, `google_play`.

`docs/PLATFORM_ALGORITHM_RESEARCH_2026.md` carries the same stale table ("Audible | standard_book (55 min) or extended_book_2h"). **Both the config and its authority doc need the correction.**

> Mitigating note: neither `platform_knob_tuning.yaml` nor `platform_duration_profiles.yaml` has live Python consumers (`grep` = 0 hits) — they are **planning references**, so the bug isn't mis-routing production *today*. But they are the SSOT the moment catalog routing is wired (CDIS §14 Phase-2 criterion 11), so fixing them now prevents shipping the wrong routing.

---

## 4. CDIS §4 number validation (what the research changed)

| CDIS / config number | Verdict | Correction |
|---|---|---|
| KDP 150–230pp sweet spot | ✅ VALIDATED | widen price floor $4.99→$2.99 (70% band opens at $2.99) [K4] |
| Audible self-help 5–7 hr | ✅ VALIDATED | — [A4][A5] |
| Audible "curates under-3hr collections" | ❌ CORRECTED | no official collection; shorts disadvantaged by credit/pool economics [A1][A6] |
| Audible monetization_threshold 3 hr | ✅ VALIDATED | keep as the real go/no-go gate [A5] |
| Spotify audiobook 5–7 hr | ✅ VALIDATED | bias lower (4–6 hr) for Spotify's casual audience [S3][S6] |
| Spotify podcast "20–30 min" | ⚠️ CORRECTED | → 20–40 min (target 25–35); completion holds to ~45 min [S7][S8] |
| Spotify `monetization_threshold 1200s` | ⚠️ MISLABELED | Spotify has no audiobook consumption gate; reclassify as internal podcast floor [S5] |
| YouTube long 10–20 min | ⚠️ CORRECTED | → 10–15 min (tighten top) [Y6] |
| YouTube monetize 8 min | ✅ VALIDATED | unchanged 2026 [Y1][Y2] |
| YouTube Shorts hard_max 60s | ❌ CORRECTED | → 180s (3-min Shorts since 2024-10-15) [Y3] |
| WEBTOON Canvas 20–30 / Originals 40–60 panels | ⚠️ VALIDATED-as-heuristic | creator aim, not a platform rule; real Canvas ~30–45 [W1] |
| Lezhin 70+ panels / min 24 ep | ❌ CORRECTED | ~60-panel guidance; 4 ep to submit; ≥30-ep plan [W3] |
| iyashikei 55–65 panels | ❌ CORRECTED | → ~40–55; pacing via gutters/long-drops, not panel count [W-INT] |
| Ximalaya 10–30 min | ✅ VALIDATED | typical 15–20 min [C1] |
| Millie 15–30 min summary | ✅ VALIDATED | but Korea = ALSO ship full edition (Welaaa) [C11][C12] |
| ja tankōbon 180–220pp | ✅ VALIDATED | back-derived from 300 文字/分 × 6 hr [C8] |
| expansion ja 2.15 / zh 1.6 / ko 2.0 | ⚠️ PARTIAL | ja measured ✅; **zh + ko UNVERIFIED — measure before ship** [§7] |
| Findaway "serves Spotify, Apple, Kobo" | ❌ STALE | Findaway ceased 2025-08-01 → INaudio + Spotify for Authors [A8][S4] |

---

## 5. The gap, stated as the fix split

| Gap | Magnitude | Fix type | Owner |
|---|---|---|---|
| **No flagship 52k-word product** (Audible/KDP-full unservable) | thin ~5k → 52k = **~10×**; gold ~22k → 52k = **~2.4×** | **CONTENT-LENGTH** → writing program (real length, ≥70% completion, NO padding) | writing program |
| **Routing sends sub-3hr books to Audible** | structural (every routed title sub-floor) | **CONFIG** (correct `platform_knob_tuning.yaml` + authority doc) | Pearl_Research (this PR) |
| **Platform profiles uncited + 6 stale numbers** | medium (Shorts 60→180s, podcast 20→40, findaway, etc.) | **CONFIG** (cite + correct `platform_duration_profiles.yaml`) | Pearl_Research (this PR) |
| **No tier→platform cross-walk** | the missing SSOT | **CONFIG** (new `ladder_tier_platform_fit` block) | Pearl_Research (this PR) |
| **CJK targets char-based, zh/ko unverified** | provisional | **GATE on measured render** (Pearl Star off) | deferred |

**Bottom line for the operator:** the duration *labels* are now honest (#1550). The duration *reality* is that our content is too short to win the surfaces that pay the most — and our routing config points the short content at exactly the wrong (full-length) surfaces. Config fixes the routing today; the writing program must produce the 52k-word flagship for us to have an Audible/KDP-full product at all. **Real length, never padded — padding loses the read-through revenue that is the whole reason to be long.**

---

## 6. Execute — before/after config (this PR)

### 6a. `config/catalog_planning/platform_knob_tuning.yaml` — route to tiers that reach the stated ideal

```diff
 audible:
-  preferred_runtimes: [standard_book, extended_book_2h]
+  preferred_runtimes: [deep_book_6h, deep_book_4h]   # T7 5.8h + T6 3.3h — the only runtimes that reach ideal_runtime_hours:5 (standard_book is 2.45h, below the 3h Audible floor; corrected post-#1550 label fix)
 spotify:
-  preferred_runtimes: [short_book_30, standard_book, micro_book_20]
+  preferred_runtimes: [deep_book_4h, deep_book_6h, standard_book]   # 4–6h bias; standard_book only as a podcast-season source, not a standalone audiobook
```
(+ analogous corrections to apple_books/google_play audiobook surfaces; route T1–T4 to ximalaya/short-read/podcast; refresh the `findaway` note to INaudio/Spotify-for-Authors 2025-08-01.)

### 6b. `config/duration/platform_duration_profiles.yaml` — cite + correct + add the cross-walk

- youtube: `sweet_spot 600–1200 → 480–900` (8–15 min); add `source: [Y1][Y6]`
- youtube_shorts: `hard_max 60 → 180`; note 15–30s completion / 30–60s views
- spotify: podcast note `20–30 → 20–40 min`; relabel `monetization_threshold_seconds` as podcast-completion floor
- audible: note "under-3hr collections" → "shorts disadvantaged by credit/consumption-pool economics"; add `royalty_model: consumption_pool_2026-05-26`
- add top-level **`ladder_tier_platform_fit:`** block = the §1 matrix (tier → {wins, marginal, loser} per platform) as machine-readable SSOT
- add `sources:` refs throughout (the [K#]/[A#]/… keys resolve to `PLATFORM_DURATION_SOURCES.md`)

All changes are **additive/corrective** (no key deletions → RULE-0 clean). PR is **do-NOT-merge** pending operator review of the platform-strategy + routing decision; CJK rows carry a provisional flag pending a measured render.

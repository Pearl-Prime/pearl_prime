# Duration-Per-Platform Plan — the length that WINS on each surface, mapped to our 7 tiers

**Date:** 2026-06-13 · **Agent:** Pearl_Research (platform-duration strategy) · **Status:** PLAN for operator review (config PR is do-NOT-merge; content-length routed to writing program)
**Evidence:** `PLATFORM_DURATION_SOURCES.md` (50+ cited) · **Verified against our reality in:** `DURATION_GAP_VERIFICATION.md`
**Builds on (does not re-derive):** the merged honest 7-tier ladder (`MARKETING_DURATION_TARGETS.md`, PR #1550), CDIS §4 (`platform_duration_profiles.yaml`), and the platform→tier routing in `platform_knob_tuning.yaml` (which this plan **corrects**).

---

## The decision in one line

**Our 7 tiers are not interchangeable across surfaces: only the top tier (T7 "Complete," ~52k words / ~5.8 hr / ~208 pp) wins the flagship $-maker surfaces — full-length KDP + Audible + Spotify audiobook — simultaneously. Everything T1–T5 is a podcast / short-read / lead-magnet / sample play, NOT a standalone audiobook. Route each tier to the surface its length actually wins on, and feed the writing program a flagship 52k-word target (real length, never padding) so we have a product that wins Audible/KDP at all.**

---

## 1. The tier → platform fit matrix (en-US, the master cross-walk)

Every row is our tier at its **honest ladder length**; every cell is whether that length **wins** on that surface, with the reason. Audiobook min = words ÷ 150 WPM; print pp = words ÷ 250.

Legend: ✅✅ flagship win · ✅ wins · ⚠️ marginal/wrong-home · ❌ structural loser

| Our tier | words | audio | print pp | **KDP** (KU read-through) | **Audible** (5–7 hr) | **Spotify audiobook** (4–6 hr) | **Apple/Google AI-narr** | **Podcast** (20–40 min/ep) | **YouTube/social** |
|---|--:|--:|--:|---|---|---|---|---|---|
| **T1 Quick Reset** | 3.5k | 23m | 14pp | ❌ lead-magnet only | ❌ bottom tier | ❌ sample | ⚠️ 23-min "sample" | ✅✅ **1 episode** (in 20–40) | ✅ Short/Reel companion |
| **T2 Mini** | 4.5k | 30m | 18pp | ❌ free/funnel | ❌ | ❌ | ⚠️ | ✅✅ **1 episode** (sweet center) | ✅ |
| **T3 Short** | 6.0k | 40m | 24pp | ⚠️ KDP **Short Read** ($0.99–2.99) | ❌ <3 hr floor | ❌ | ⚠️ | ✅✅ **1 episode** (top of band) | ✅ |
| **T4 One-Hour** | 9.0k | 60m | 36pp | ⚠️ Short Read | ❌ | ❌ | ⚠️ | ✅ 2-ep mini / 60-min special | ✅ |
| **T5 Standard** | 22k | 2.45h | 88pp | ⚠️ **still a Short Read** (88<150pp) | ⚠️ just under 3-hr floor | ⚠️ below 4–6 hr | ✅ listable | ✅✅ **full season** (8–10 ep) | — |
| **T6 Long-Form** | 30k | 3.3h | 120pp | ⚠️ low-end full (120<150pp) | ✅ **3–5 hr band** ($19.95) | ⚠️ below 4 hr | ✅ | ✅ meaty season | — |
| **T7 Complete** | 52k | 5.8h | 208pp | ✅✅ **150–230pp sweet** | ✅✅ **5–7 hr sweet** | ✅ **top of 4–6 / in 5–7** | ✅ full AI audiobook | ✅ multi-season | — |

**Read it this way (the three findings that drive the strategy):**

1. **Only T7 wins the flagship audiobook+ebook surfaces.** 52k words is the *only* tier that lands in BOTH the KDP 150–230pp band [K1–K5] and the Audible 5–7 hr band [A1–A6]. T6 (30k) is an acceptable *entry* full-audiobook (Audible 3–5 hr tier) but thin on KDP (120pp). **Everything ≤T5 is sub-floor on Audible and a "short read" on KDP.**
2. **Even "Standard" (T5, 22k) is a KDP short-read and a sub-3-hr Audible title** — the names imply a full book; the length doesn't deliver one on the paid-book surfaces. T5's real home is a **podcast season**, where 22k = 8–10 episodes × ~20 min each, squarely in the 20–40-min podcast sweet spot [S7][S8].
3. **The short tiers are not "bad" — they're mis-routed when sold as books.** T1–T3 are *excellent* podcast episodes, lead-magnets, KDP short-read funnel entries, and Apple/Google free-AI samples. They are *structural losers* as standalone Audible audiobooks [A6] (bottom $6.95 price tier, "not worth a credit," negligible weight in the new consumption pool [A1]).

---

## 2. Per-platform target — the single number to hit + why + source

| Platform | Format | **Target length to WIN** | In our units | Why (mechanism) | Src |
|---|---|---|---|---|---|
| **Amazon KDP** | ebook (full) | **150–230 pp / 35–50k words** | **T7** (208pp); T6 low-end | KU pays per KENP page read × rising rate (~$0.0045); 70% band $2.99–9.99; <150pp reads as short-read | [K1][K2][K4] |
| **Amazon KDP** | ebook (Short Read) | **<100 pp / <25k words, $0.99–2.99** | T1–T4 | series/cadence funnel; forfeits 70% band; not a standalone earner | [K5][K8] |
| **Audible / ACX** | audiobook | **5–7 hr / 45–63k words** (floor 3 hr) | **T7** (5.8h); T6 = 3–5h entry | length sets à-la-carte price tier + consumption-pool weight; <3 hr = bottom tier | [A1][A4][A5][A6] |
| **Spotify** | audiobook | **4–6 hr / 36–54k words** | **T7**; T6 marginal | 15 hr/mo at normal speed → runtime scarce → shorter "tryable"; payout pro-rata on completed hours | [S1][S3][S4][S6] |
| **Spotify / Apple** | podcast episode | **20–40 min / 3–6k words/episode** | **T1–T3 = 1 ep**; T5 = a season | completion flat 10→45 min, drops past 50; cadence (~14-day) ≈ +5 chart positions | [S7][S8][S9] |
| **Apple Books** | ebook + AI audiobook | length-agnostic; **English self-help eligible** | any tier; T7 best value | flat 70% per-sale, no read-through → length = price justification; free AI narration (EN only) | [P1][P4][P5] |
| **Google Play** | ebook + auto-narr audiobook | length-agnostic; EN/ES/FR/DE/HI/pt-BR narration | any tier | 70% ebook / 52% audio; free auto-narration; reaches JP/KR/HK/TW ebooks | [P2][P3][P4][P7] |
| **YouTube** | long-form teaching | **8–15 min** (≥50% retention; ≥8 min for mid-roll) | (video, not book) | watch-time × satisfaction layer; 8-min unlocks mid-roll | [Y1][Y2][Y6] |
| **YouTube** | Shorts / trailer | **15–60 s Shorts (max 180s); 60–90 s trailer** | (video) | 15–30s completion-optimal, 30–60s views-optimal; hook = first ~15s | [Y3][Y5][Y8] |
| **WEBTOON** (Canvas/Originals) | manga episode | **~8–12 min read / 3,500–4,500px / ~40–55 panels (healing)** | (manga) | retention sweet ≈ 4,000px; weekly cadence ≈ 3× subscriber velocity; ep 1 = ~70% conversion | [W1][W2][W10] |
| **WEBTOON** | series | **launch 3 ep; binge/monetize at ~25–30 ep** | (manga) | Fast-Pass needs locked backlog; subscribe prompt at ep 3 | [W3][W4][W10] |
| **Piccoma / LINE Manga** (JP) | manga chapter | **short ~10–20 pp chapters, DEEP backlog, daily cadence** | (manga) | wait-until-free per-title every 23 hr → chapter count = revenue lever; Piccoma self-pub closed → LINE Manga Indies | [W7][W8] |

---

## 3. CJK char-based targets — PROVISIONAL (gate on a measured render)

> **⚠️ Provisional.** CJK is char-based, NOT word-based. **ja expansion 2.15 is repo-measured (trust); zh ≈ 1.6 and ko ≈ 2.0 are UNVERIFIED estimates** [PLATFORM_DURATION_SOURCES §7]. **ja narration 300 文字/分 is the one hard-sourced rate** [C8][C9]; zh 160–190 字/分 is a deliberate slow floor [C2]; ko 자/分 has **no source** [verify]. **Do not ship any CJK platform duration label until one zh + one ko render are measured on Pearl Star (CosyVoice2 currently off).**

The flagship T7 (52k EN words) translated to each CJK market, with the local platform's own norm for comparison:

| Locale | T7 chars (×expansion) | T7 audiobook (÷ rate) | local audiobook norm | T7 ebook chars vs local norm | Flagship platforms |
|---|--:|--:|---|---|---|
| **en-US** | — | 5.8 hr | Audible 5–7 hr ✅ | 208pp vs 150–230 ✅ | Audible, KDP, Spotify |
| **ja-JP** | 111,800 (×2.15) | **6.2 hr** (÷300 文字/分) | 自己啓発 4–6 hr → top ✅ | 111.8k vs 80–120k ✅ | Audible JP, audiobook.jp, Kobo JP |
| **zh** (CN/TW/SG) | 83,200 (×1.6 *[verify]*) | **7.3 hr** (÷190 字/分) | Ximalaya = episodes, not full books | 83.2k **vs 100–150k → BELOW** ⚠️ | Ximalaya (episodic), WeChat Read |
| **ko-KR** | 104,000 (×2.0 *[verify]*) | **~5.0 hr** (÷~350 *[verify]*) | **two-market split** | 104k vs 120–180k → low ⚠️ | **Welaaa (full) + Millie (summary)** |
| **zh-HK** | 83,200 (Cantonese audio) | 7.3 hr *[verify]* | as zh-TW | as zh | Cantonese TTS-gated |

**Three CJK strategy notes:**
- **zh wants MORE, not less.** A 52k-EN-word book → ~83k zh chars is *below* the 100–150k 字 zh self-help ebook norm [C3], and the slow 160–190 字/分 calm pace pushes the audiobook to ~7.3 hr. zh editions should target a **higher word_target** (≈ 65–95k EN-equivalent) to hit the zh ebook norm — but Ximalaya (the dominant zh audio channel) wants **15–20 min episodes** [C1][C7], so zh audio is an **episodic/serialized** play, not a single 7.3-hr file.
- **Korea = ship BOTH editions.** A T1–T3-length **Millie summary** (15–30 min, AI-voiced) [C11] AND a full **Welaaa** T7 edition (pro-narrator) [C12]. "Korea wants short" is platform segmentation, not an audience truth.
- **ja is the cleanest CJK win** — T7 lands in the ja self-help audiobook band (4–6 hr) AND the ja ebook 文字 band, both anchored on the hard 300 文字/分 rate.

---

## 4. Tier → platform ROUTING (the corrected catalog routing)

This replaces the stale routing in `config/catalog_planning/platform_knob_tuning.yaml` (which routes `standard_book` → Audible on the old 55-min label — see `DURATION_GAP_VERIFICATION.md` §3). The corrected routing, by primary surface:

| Surface | Route these tiers | NOT these | Rationale |
|---|---|---|---|
| **Audible / ACX** (flagship audiobook) | **T7** (5.8h ✅✅), T6 (3.3h ✅ entry) | T1–T5 (<3 hr floor) | length sets price tier + pool weight; sub-3hr = structural loser [A1][A6] |
| **Spotify audiobook** | **T7**, T6 (marginal) | T1–T5 | 4–6 hr bias; completion-weighted payout [S4][S6] |
| **KDP full ebook** | **T7** (208pp ✅✅), T6 (120pp low-end) | T1–T5 (short-reads) | 150–230pp credible-book band; KU read-through [K1][K4] |
| **KDP Short Reads** (funnel) | T1–T4 ($0.99–2.99) | — | series/cadence funnel; lead-in to flagship [K5][K8] |
| **Podcast** (Spotify/Apple) | **T1–T3 = 1 episode each**; T5–T7 = seasons (chapter→episode) | — | 20–40 min/episode; book→season mapping [S7][S8] |
| **Apple/Google free AI audiobook** | **any English tier** (T7 best value) | CJK (not AI-narrated) | length-agnostic per-sale; English/genre-eligible [P1][P2] |
| **Ximalaya (zh)** | episodic cut of any tier (15–20 min episodes) | single long file | companion/commute listening [C1][C7] |
| **Naver (ko)** | ~90-min compact + serialized | — | "90-min compact" trend [PAR-2026] |
| **Millie (ko)** | **T1–T3 summary edition** | full-length | summary-dominant, AI-voiced [C11][C12] |
| **Welaaa (ko)** | **T7 full edition** | summary | full pro-narrator platform [C12] |
| **WEBTOON / Piccoma / Kakao** | manga (panels/episodes, not book tiers) | — | see §2 manga rows |
| **YouTube** | 8–15 min teaching + 60–90s trailers + 15–60s Shorts | — | watch-time × satisfaction [Y1][Y6] |

---

## 5. Content-length targets ROUTED to the writing program (real length, never padding)

The matrix above exposes the dominant gap: **we have no tier that wins the flagship audiobook+ebook surfaces at our REAL render lengths** (see `DURATION_GAP_VERIFICATION.md`). Closing it is a **content-length** problem — books must be FULLER — which is the **writing program's** job, not a config edit and **never padding/inflation**. The targets to feed the writing program:

| Writing target | word_target | maps to | wins | persona modifier (CDIS §10.2) |
|---|--:|---|---|---|
| **Flagship "Complete"** (the priority) | **52,000** (band 45–63k) | T7 / `deep_book_6h` | Audible 5–7h + KDP 150–230pp + Spotify | millennial/corporate/tech 52–63k (6–7h); gen_z/working 45k (5h) |
| **Entry full audiobook** | **30,000** | T6 / `deep_book_4h` | Audible 3–5h entry; lower-mid KDP | gen_z under-3–5h listeners |
| **Podcast-season source** | 22,000 (already a tier) | T5 / `standard_book` | full podcast season (8–10 ep) | — |
| **Short-read / podcast-episode / lead-magnet** | 3.5–9k (already tiers) | T1–T4 | KDP short-read funnel; 1–2 podcast episodes; freebie | gen_alpha/gen_z micro |

**CJK content-length (provisional, gate on measured render):** ja flagship ≈ 52k EN-equiv (lands in band); **zh flagship should target HIGHER (~65–95k EN-equiv)** to reach the 100–150k 字 zh ebook norm; ko ship a full (T7) + a summary (T1–T3) edition.

**Routing mechanism:** these targets are handed to the writing program as `word_target` inputs (the registry already supports `cap_word_target`/`fill_regime` per #1550). The **#1 ask is producing real 52k-word "Complete" books** — today's catalog renders ~5–22k (see gap doc). This is a depth/fill + multi-arc authoring task, explicitly **not** padding: it must sustain ≥70% completion (the universal platform signal) or it loses the very read-through revenue that motivates the length.

---

## 6. What this plan changes in config (executed in-lane; do-NOT-merge PR)

Two existing planning configs are corrected (details + before/after in `DURATION_GAP_VERIFICATION.md` §6):

1. **`config/duration/platform_duration_profiles.yaml`** (CDIS §4) — add source citations; correct: YouTube long sweet 600–1200→480–900s (8–15 min) + Shorts hard_max 60→180s; Spotify podcast note 20–30→20–40 min; Audible note "under-3hr collections" → "shorts disadvantaged by credit/pool economics"; mark `monetization_threshold_seconds` on spotify as a podcast-completion floor; flag findaway as INaudio (2025-08-01).
2. **`config/catalog_planning/platform_knob_tuning.yaml`** — fix the core routing bug: `audible.preferred_runtimes` `[standard_book, extended_book_2h]` (2.3–2.5 hr) → `[deep_book_6h, deep_book_4h]` (T7/T6, the only tiers reaching the stated `ideal_runtime_hours: 5`); same correction for spotify/apple/google audiobook surfaces; route the short tiers to podcast/short-read/Ximalaya; refresh the stale findaway note.

Plus a new **`ladder_tier_platform_fit`** block (the §1 matrix as machine-readable config) appended to `platform_duration_profiles.yaml` — the missing cross-walk, so the routing has a single source of truth instead of living only in prose.

**Operator reviews all platform-strategy changes** (tier→platform routing is a catalog-economics decision). The config PR is **do-NOT-merge** pending that review; CJK rows are provisional pending a measured render.

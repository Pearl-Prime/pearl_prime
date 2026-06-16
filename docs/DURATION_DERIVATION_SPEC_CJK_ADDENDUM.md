# Duration Derivation Spec — CJK Addendum (char-based, per-locale)

**Status:** PROPOSED · **Date:** 2026-06-13 · **Owner:** Pearl_Prime + Pearl_Architect
**Parent:** `docs/DURATION_DERIVATION_SPEC.md` (§7 deferred CJK to this addendum) · **Authorizes:** the CJK half of OPD-20260613-001
**Evidence:** `artifacts/qa/duration_marketing_targets_20260613/` (DURATION_REASSESSMENT.md §4, MARKETING_DURATION_TARGETS.md §3, duration_targets.tsv)

---

## 0. TL;DR

The en-US derivation (`audiobook_minutes = word_target / 150`) is **structurally wrong for CJK**.
CJK audiobooks are paced in **characters per minute**, and translation changes the unit count.
A CJK edition's duration MUST be derived per-locale and **never inherit the en-US label**.

```
CJK_chars   = en_word_target × expansion_ratio[locale]     # words → characters
CJK_minutes = round(CJK_chars / narration_cpm[locale])     # characters → minutes
```

---

## 1. The leakage this prevents

- The registry `word_range` / `audiobook_minutes` / `ebook_minutes` have **no locale dimension**;
  the parent spec's derivation is **en-US-only (§7)**.
- A storefront that reads a CJK edition's duration from the format's `audiobook_minutes` would
  advertise the **English** number — wrong by **−9% (ko) to +26% (zh)**.
- Real `*.ja.txt` renders carry the English format id in their own header (`形式：標準書籍`).

**Rule:** CJK editions derive duration from the **per-edition character count ÷ the locale's
narration rate**. Never reuse the en-US minutes.

---

## 2. Per-locale constants

| locale | expansion (en-word→char) | narration cpm (audio) | reading cpm (ebook) | confidence |
|---|---:|---:|---:|---|
| **ja-JP** | **2.15** | 300 | 500 | ratio **MEASURED** (n=4 real renders); rate iyashikei-adjusted **EST** |
| zh-CN / zh-TW / zh-SG | 1.60 | **190** | 350 | rate **REPO-NATIVE** (`PHOENIX_V4_5_CHINESE_WRITER_SPEC §10.1`, 160–190 字/分); ratio **EST** |
| zh-HK (Cantonese audio) | 1.60 | 190 | 350 | **EST** — char count ≈ zh-TW; **FLAG: measure** |
| ko-KR | 2.00 | 330 | 400 | **EST (all)** — **FLAG: measure** |

**Provenance of the two anchored numbers:**
- **ja expansion 2.15** — four real `artifacts/catalog/brand1_deep/stillness_press/ja_JP/books/text/*.ja.txt`
  renders vs their en counterparts: ratios 2.05 / 2.16 / 2.16 / 2.23 → mean 2.15 (σ≈0.07).
- **zh rate 160–190 字/分** — `specs/PHOENIX_V4_5_CHINESE_WRITER_SPEC_v2.5.md §10.1`
  (`語速設定：比標準慢 20%，約 160–190 字/分`); point estimate 190 (top of band, non-sleep content).

---

## 3. Per-tier CJK durations (advertised)

Advertise the locale row; never the en row. (Full grid: `duration_targets.tsv`.)

| tier | en-US | ja-JP | zh (CN/TW/SG/HK) | ko-KR |
|---|---|---|---|---|
| Quick Reset | ~25 min | ~25 min | ~30 min | ~25 min |
| Short | ~45 min | ~45 min | ~50 min | ~35 min |
| One-Hour Book | ~1 hr | ~1 hr | ~1 hr 15 min | ~55 min |
| Standard Book | ~2.5 hr | ~2.5 hr | ~3 hr | ~2 hr |
| Long-Form | ~3.5 hr | ~3.5 hr | ~4 hr | ~3 hr |
| Complete | ~6 hr | ~6 hr | ~7 hr 30 min | ~5 hr |

**Multipliers vs en:** zh ≈ **1.26×**, ja ≈ **1.08×**, ko ≈ **0.91×**. A "6-hour" book is a
**7½-hour** listen in Chinese.

---

## 4. Acceptance gate (before ANY CJK duration ships)

1. **ja-JP** — expansion measured; the narration rate (300 cpm) is still an estimate → confirm
   with one TTS-timed render before advertising ja durations.
2. **zh + ko** — **PROVISIONAL.** Both the zh expansion ratio and all ko constants are estimates.
   **Gate: measure ≥1 real rendered + TTS-timed book per locale** (zh-CN, ko-KR) and replace the
   estimated constants before advertising any zh/ko duration. **Blocked today: Pearl Star
   (CosyVoice2 CJK TTS) is OFF** — no zh/ko render+timing possible yet.
3. **zh-HK** ships **Cantonese (yue)** audio; char count ≈ zh-TW but confirm the Cantonese
   narration rate separately.
4. Until a locale passes its gate, its storefront MUST NOT advertise a duration (parent spec §8.3
   stub-handling pattern: no honest duration ⇒ no duration claim).

---

## 5. Implementation note (deferred — no consumer today)

There is **no customer-facing duration-label generator** in the repo today (confirmed: no
listing/epub builder emits minutes/hours). When that storefront layer is built, it consumes this
addendum: compute the CJK edition's char count from the actual translated render, divide by the
locale cpm, and advertise that — gated per §4. A CJK derivation helper (sibling to
`phoenix_v4/ops/duration_derivation.py`, which is en-US-only by design) is a follow-up to build
alongside that consumer, not before it (an unconsumed gated function adds surface with no benefit).

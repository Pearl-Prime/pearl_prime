# Brand-1 Deep Build — Build Manifest & Continuation

**Brand:** stillness_press (tier=flagship, demographic=josei, primary_topic=anxiety)
**Layer:** 2 (VALIDATE — proves the per-brand template before Layer 3 fan-out to 36 brands)
**Owner:** Pearl_Writer (en prose) + Pearl_Author (manga) + Pearl_Audio
**main HEAD at start:** `66f5010e1` · **Spend:** $0 (RunComfy ledger unchanged at $0.137/$10)

---

## DONE (committed, en_US)

### A. Books — 4 full-text titles (all 3 topics × 4 flagship personas)

| Title | topic / persona | words | EPUB | validate_epub |
|---|---|---|---|---|
| The Room Is Safe | anxiety / gen_z_professionals | 5,491 | ✓ w/ cover | rc=0, 0 err |
| The Hour That Won't Let Go | sleep_anxiety / midlife_women | 5,299 | ✓ w/ cover | rc=0, 0 err |
| The Fourth Draft of a Text Message | overthinking / millennial_women_professionals | 5,406 | ✓ w/ cover | rc=0, 0 err |
| The Dashboard in Your Chest | anxiety / tech_finance_burnout | 5,342 | ✓ w/ cover | rc=0, 0 err |

- Scene-first openings per HOOK addendum (person + situation + posture in paragraph 1).
- Ahjan contemplative voice; **Stillness Press** identity (not legacy "Inner Light Press").
- 4 PIL typographic covers (1600×2560, iyashikei palette) embedded in EPUBs.
- Structure: A Note on the Teachings → Ch1 Hook → Ch2 The Pattern → Ch3 The Practice (4 practices)
  → Ch4 The Return → Ch5 (acute/setback handling) → Where to Go Deeper.

### B. Manga — 3 series scripted (= full active_series_target)

| Series | topic | script | render |
|---|---|---|---|
| What the Body Holds | anxiety | ep_001, mapped 1:1 to 35 rendered panels | RENDERED + assembled (KDP PDF 35pp, WEBTOON strip 800×49770) |
| The Night Before You Sleep | sleep_anxiety | ep_001, ~35 render-ready panels | script-only |
| Hands, Shoulders, Breath | somatic_healing | ep_001, ~35 render-ready panels | script-only |

### C. Podcast — The Stillness Check-In, 3 episode scripts

- Ep1 anxiety (standard 15-25min), Ep2 sleep_anxiety (`podcast_sleep` inverse-engagement curve),
  Ep3 overthinking (standard). Full segment structure + guided practice + show notes each.

### D. Images — $0

- 4 book covers committed (PIL, iyashikei palette).
- 35 series-1 composed panels reused (already on main).
- Image bank inventory + deferred render jobs documented (`…/images/IMAGE_BANK_MANIFEST.md`).

### E. Assembly

- 4 EPUBs (committed, validated). Series-1 KDP PDF + WEBTOON strip assembled locally
  (gitignored — >1 MB cap + LFS budget exhausted; reproducible per MANGA_MANIFEST.md).

---

## REMAINING (continuation)

### F. ja_JP — queued for Qwen (Tier 2), NOT started by design

Per CLAUDE.md: ja_JP prose must route through Qwen on Pearl Star, never Claude. Pearl Star was
unreachable from this session (local LAN). Full run plan + exact commands in
`stillness_press/ja_JP/JA_JP_CONTINUATION.md`. Zero Claude-authored Japanese prose.

### Deferred image renders (Pearl Star LAN, $0)

- Cover imagery layer (FLUX field behind the 4 typographic covers).
- Series 2 + 3 manga panel renders (~35 each) from the committed scripts.
- Yuki + Mei character model sheets (series 2/3 character locks).

### Book catalog breadth (optional Layer-2 extension)

The high-confidence catalog has 20 unique topic×persona book identities and 8 length formats
(standard/deep_6h/deep_4h/extended_2h/compact/micro_15/micro_20/short_30) × 2 locales (en-US, en-GB).
This build wrote the 4 top-ranked standard_book narratives (the score-8.0 / score-7.7 core covering
all 3 topics + all 4 flagship personas). Remaining personas (corporate_managers, healthcare_rns,
nyc_executives, working_parents) and the longer-format expansions are Tier-2 batch work (Gemma on
Pearl Star) per the Layer-3 fan-out program — the template they'd follow is now validated.

---

## Template validation verdict (Layer 2 gate)

The full per-brand pipeline is proven end-to-end on stillness_press en_US:
**book text → scene-first EPUB (validated) + cover → manga chapter script → rendered/assembled
KDP PDF + WEBTOON → podcast script (segmented) → image bank → assembly manifest.**
This is the fan-out template for the remaining 36 brands (Layer 3, gated on operator approval).

Tier policy held throughout: en prose = Claude (Tier 1); ja prose = deferred to Qwen (Tier 2);
images = $0 reuse + PIL (Pearl Star unreachable, no RunComfy spend); no paid LLM APIs called.

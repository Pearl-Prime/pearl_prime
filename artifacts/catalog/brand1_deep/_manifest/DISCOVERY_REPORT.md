# Brand-1 Deep Build — Discovery Report (stillness_press)

**Layer 2 validation** of the worldwide-catalog fan-out template.
**Authority:** `docs/SYSTEMS_STATE_20260527.md` §3 LAYER 2. **main HEAD at start:** `66f5010e1`.

## Catalog scope (high_confidence_catalog_v1.tsv)

- **144 stillness_press rows** → collapse to **20 unique book identities** (topic × persona).
- **Topics:** anxiety (64 rows), sleep_anxiety (64), overthinking (16).
- **Personas:** gen_z_professionals, midlife_women, millennial_women_professionals,
  tech_finance_burnout (28 rows each, all formats); corporate_managers, healthcare_rns,
  nyc_executives, working_parents (8 rows each, book-only formats).
- **Formats:** standard_book, deep_book_6h, deep_book_4h, extended_book_2h,
  compact_book_8ch_30min, micro_book_15, micro_book_20, short_book_30 (length variants).
- **Locales:** en-US (112), en-GB (32).
- **Top-ranked (score 8.0, rank 1–8):** anxiety + sleep_anxiety × 4 flagship personas × standard_book.

## Manga series (3 profiles on disk)

| Series | title_id | character | topic | priority |
|---|---|---|---|---|
| What the Body Holds | stillness_press_anxiety_vol1 | Hana / Mira | anxiety | P0 |
| The Night Before You Sleep | stillness_press_sleep_vol1 | Yuki | sleep_anxiety | P1 |
| Hands, Shoulders, Breath | stillness_press_somatic_vol1 | Mei | somatic_healing | — |

- **35 rendered composed_v4 panels** on disk for anxiety ep_001 (real 1080×1920 PNGs) + full panel_prompts JSON.

## Pipelines reachable

- **EPUB:** `scripts/release/build_epub.py` — parses CHAPTER markers → KDP EPUB3 (ebooklib + PIL verified).
- **Podcast:** `scripts/podcast/run_podcast_pipeline.py`.
- **Qwen CJK (ja_JP):** `scripts/manga/translate_chapter_script.py`, `scripts/localization/translate_atoms_*` (cloud/DashScope variants; tier policy routes ja → Qwen on Pearl Star).
- **Pearl Star runner check:** `scripts/ci/check_pearl_star_runner_online.py` requires `GITHUB_REPOSITORY` (CI-only). Local Ollama unconfirmed in-session.

## On disk from MVP (2026-W22)

- 1 EPUB ("The Alarm Is Lying", real scene-first chapter text, **legacy "Inner Light Press" branding** — needs stillness_press identity).
- 1 manga PDF + WEBTOON PNG (35 panels).
- Podcast MP3 (script.txt empty stub).
- Image bank progress TSV logs "completed" but **0 PNGs locally** (R2-offloaded); 35 composed panels present.

## Spend

- RunComfy ledger: $0.137 cumulative/month (full ~$9.86 headroom). This build targets $0 (reuse rendered panels; Pearl Star for any new images).

## Build plan (priority order)

1. **Books (en_US):** scene-first full text (HOOK addendum applied) for anxiety + sleep_anxiety + overthinking × flagship personas → EPUBs with stillness_press identity.
2. **Manga:** full chapter script (beats + panel descriptions) for series 1 (anxiety) reusing 35 panels; scripts for series 2 (sleep) + 3 (somatic).
3. **Podcast:** weekly podcast script set.
4. **Images:** reuse 35 composed panels as image bank; attempt Pearl Star covers.
5. **Assemble + manifest.**
6. **ja_JP:** stub + Qwen continuation note (NO Claude CJK prose — tier policy).

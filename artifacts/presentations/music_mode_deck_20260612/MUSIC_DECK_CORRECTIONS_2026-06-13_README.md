# MUSIC_MODE_INTRODUCTION_DECK — 2026-06-13 model correction (EN / JA / ZH)

Corrects the music-mode **model** on the intro deck per operator (Ahjan) direction, and folds in the
operator's own `.pptx` edits. Governed by
[`docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` §AMENDMENT-2026-06-13](../../../docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md).
The deck was machine-built with **no committed build script**; this correction therefore edits the
`.pptx` directly via python-pptx and ships the edit scripts as the reproducible source of truth.

## Build pipeline (reproducible)

```
operator copy:  ~/Downloads/MUSIC_MODE_INTRODUCTION_DECK 3.pptx   (operator edits live here)
   │  apply_music_deck_corrections.py   (corrections 1–8 layered ON the operator copy)
   ▼
MUSIC_MODE_INTRODUCTION_DECK.pptx       (corrected EN)
   │  extract_for_translation.py   ->  en_records.json + en_translatable.txt (250 strings)
   │  Tier-1 Claude translators (operator-present; CLAUDE.md tier policy) ->
   ▼                                    ja_translations.tsv / zh_translations.tsv   (idx<TAB>text)
apply_translation.py  (+ existing localized deck as serif/sans font-oracle; sets a:latin + a:ea)
   ▼
MUSIC_MODE_INTRODUCTION_DECK_JA.pptx  ·  MUSIC_MODE_INTRODUCTION_DECK_ZH_CN.pptx
   │  soffice --headless --convert-to pdf  →  pdftoppm -png   (render)
   ▼  fresh-eyes QA subagent per locale  →  fix → re-render
```

Rebuild EN: `python3 apply_music_deck_corrections.py "~/Downloads/MUSIC_MODE_INTRODUCTION_DECK 3.pptx" MUSIC_MODE_INTRODUCTION_DECK.pptx`
Rebuild JA: `python3 apply_translation.py JA ja_translations.tsv MUSIC_MODE_INTRODUCTION_DECK_JA.pptx MUSIC_MODE_INTRODUCTION_DECK_JA.pptx "Hiragino Mincho ProN" "Hiragino Sans"`
Rebuild ZH: `python3 apply_translation.py ZH zh_translations.tsv MUSIC_MODE_INTRODUCTION_DECK_ZH_CN.pptx MUSIC_MODE_INTRODUCTION_DECK_ZH_CN.pptx "Songti SC" "Heiti SC"`

> py3.9 note: scripts start with `from __future__ import annotations`. CJK runs need the **East-Asian**
> font (`a:ea`) set — `font.name` alone (Latin only) renders CJK as tofu in LibreOffice.

## The model corrections (1–8) → slides

| # | Correction (amendment §) | Slides changed |
|---|---|---|
| 1 | **Both-ways, data-driven mix** — not a variant choice; `lyric_ratio` from data; planner picks per book; one brand (§A1) | 2, 3, 4, 7, 12 |
| 2 | **Persona reuse vs composite** — teacher reuses; non-teacher draws teachings from the Pearl Prime composite (§A2) | 2, 6, 15 |
| 3 | **= regular Pearl Prime ebook + music slots** (§A3) | 2, 3 |
| 4 | **First-person music_wrapper, music-attributed** (#1527 sibling) + Stage-6 lint; 1P default / 2P kept (§A4) | 3, 8 |
| 5 | **Volume → Pearl Prime ~800 + per-platform rollout** — kills SOLO/STANDARD/ENTERPRISE (supersedes #1497 row-12) (§A5) | 10, 11 |
| 6 | **Behind-the-Song = podcast AND PDF** (§A6) | 13, 14 |
| 7 | **No music-file distribution** — music lives on channels; AI companion-song = internal/optional (§A7) | 2, 3, 7, 11, 12, 13, 14 |
| 8 | **Slide-13 M3 typos** — "You Tube"→YouTube, "Tikok"→TikTok (§A8) | 13 |

## Operator `.pptx` edits — PRESERVED (built ON the operator copy)

s1 title "Pearl Prime / Music Content" + format list (truncated subtitle completed) · s2 "on the
Platform" · s3 "books→scripts", dropped "max 3" · s4 "Ei Review" (cased to brand-standard **EI**) ·
s11 "Brand Director", "Standard 800 book catalog", "14 Markets" · s12 simplified Mode-Selector +
intake · s13 M3 YouTube&TikTok + M5 "Podcasts:" · s15 "**Composite USLF**", "Therapeutic Content",
"spiritual wisdom".

## Fresh-eyes QA verdict (per locale, on rendered PNGs)

- **EN — SHIP.** Fixed: s4 "Ei"→"EI"; s6 dangling bullet → "The gold standard for every future
  musician kit." ("Composite USLF" on s15 kept — operator intent, documented in §A2/§A7.)
- **JA — SHIP.** Fixed: s10 "Short Reads"→"ショートリード"; CJK tofu resolved via `a:ea` fonts; s15
  title translated + fit to one line.
- **ZH — SHIP.** Fixed: "Brand Director"→品牌总监 (s1/s11/s12); s10 header 规模→推出, "SEQUENCE"→序列;
  s15 title/subtitle overlap resolved (one-line fit).

No tofu, overflow, overlap, placeholder, or typo remaining in any locale.

## Status

Deck + spec amendment are **operator-review-pending**. Cap ratification
(`MUSIC-ONBOARDING-SONG-KIT-V1-01-AMENDMENT-2026-06-13`) + the code fan-out (planner variant-mix,
wizard Music-Format→data-derived, brand-admin composite path, `music_wrapper` resolver + Stage-6
lint, freebie M1/YouTube-bridge) are the **gated serial-lane next-actions** — see amendment §A8.

# Europe Catalog Plan

**Generated:** 2026-04-27
**Status:** SCAFFOLD — Pearl_Research deep-research authors fill format mix + revenue tables.
**Authority:** Pearl_Architect (scaffold) → Pearl_Research (research authoring) → Pearl_PM (acceptance)
**Scope:** European locales — initially `hu_HU` (Hungary), with placeholder slots for `de_DE`, `fr_FR`, `it_IT`, `es_ES` per `artifacts/research/full_content_audit.md` top-5 high-confidence locale list.

This file is created as part of extending the manga catalog generator from 5 → 8 markets (`scripts/manga/generate_catalog_plan_from_strategic.py:55`). It exists so the generator can resolve `hu_HU` per-locale rules; deep market research must follow.

---

## 1. Status

This plan is a **scaffold** for `hu_HU` (Hungary). Other European locales (`de_DE`, `fr_FR`, `it_IT`, `es_ES`) are listed in §6 as future expansion slots but are NOT yet wired in `VALID_LOCALES`.

## 2. Hungary (hu_HU) — known constraints

Per [artifacts/research/full_content_audit.md](../artifacts/research/full_content_audit.md):

> "Hungarian market (hu-HU) is too small for deep books (4h+, 6h)"
>
> "Any deep-form content in hu-HU — Hungarian audiobook market ~$2M. A 6-hour deep book will sell <50 copies. Production cost exceeds revenue."

**Implications for hu_HU catalog:**
- Restrict to micro-format (≤2h) or short standard (~3h)
- Prioritize webtoon vertical-strip over deep tankobon (lower production cost per unit)
- Skip the bottom 6 of the 12 genre shells until evidence accumulates — focus on the top revenue genres only
- TTS: `hu-HU-NoemiNeural` via Edge TTS (free, confirmed in PR #734)

## 3. Format and art style by sub-market — PLACEHOLDER

| Sub-market | Format | Art Style | Platform |
|---|---|---|---|
| HU (Hungary) | Webtoon vertical-strip OR micro tankobon (≤2h) | TBD | TBD |

## 4. Brand tier assignments for hu_HU — TO RESEARCH

Pearl_Research input needed:
- Which Phoenix Omega brands resonate in Hungarian post-Soviet cultural context?
- Are there genre preferences amplified by Hungarian literary tradition (Krasznahorkai for psychological_horror? Esterházy for literary memoir?)
- Cultural sensitivities around mental health framing (clinical vs. spiritual vs. philosophical register)

## 5. Genre allocation for hu_HU — TO RESEARCH

Per-brand × per-genre % allocations following the same 4-leg blend, with **HARD constraint** that micro-format dominates (no deep books).

**Hungarian revenue weights** (TO POPULATE in `_GENRE_REVENUE_WEIGHTS` per Hungary):
- `psychological_thriller` likely amplified by literary tradition
- `psychological_horror` (Junji Ito has European market translation track record)
- `iyashikei` undertested
- Action shells underweighted (smaller market for shonen-style content)

## 6. Future European locales — RESERVED, NOT YET WIRED

Per `artifacts/research/full_content_audit.md` top-5 high-confidence locale list (en-US, de-DE, ja-JP, ko-KR, fr-FR), the high-confidence European locales are de-DE and fr-FR — neither is wired in current 8-market `VALID_LOCALES`. Adding them is a future extension:

| Locale | Status | Notes |
|---|---|---|
| `de_DE` | Future | High-confidence per audit; large audiobook market; spiritual/teacher framing underperforms — needs evidence-based register |
| `fr_FR` | Future | High-confidence per audit; manga aisle developed via FR/BD tradition; literary register required |
| `it_IT` | Future | Lower priority; manga aisle smaller than DE/FR |
| `es_ES` | Future | Could share `es_LA` infrastructure or split — operator decision |

When adding any of these:
1. Append to `VALID_LOCALES` in `generate_catalog_plan_from_strategic.py` and `generate_series_plans_from_catalog.py`
2. Extend schema enum and bump schema version
3. Author per-locale strategic doc section (or new file)
4. Add format-routing config entries

## 7. Translation provider routing — DECISION NEEDED for hu_HU

| Provider option | Cost | Quality | Notes |
|---|---|---|---|
| DeepSeek | Free tier | Unknown for Hungarian | Need quality benchmark |
| Claude Code (Tier 1) | Subscription | High | Operator-attended only |
| Google Translate API | Free tier | Lower | Fallback only |

**Decision needed:** translation provider for series-level metadata before catalog generator emits hu_HU rows.

## 8. Distribution platform mapping — TO RESEARCH

Format-routing entries needed in `config/manga/format_routing.yaml` for hu_HU.

## 9. Risk gates

- **Market-size risk:** Hungarian audiobook market ~$2M — keep production budgets proportional.
- **Translation quality risk:** Hungarian is morphologically rich — agglutinative grammar makes machine translation harder than Romance / Germanic languages.
- **Distribution risk:** No major Hungarian-native manga platform — must rely on cross-shipping from EU webtoon platforms.

---

## Generator wiring

`hu_HU` is wired in:
- `scripts/manga/generate_catalog_plan_from_strategic.py:55` — `VALID_LOCALES`
- `scripts/manga/generate_series_plans_from_catalog.py:44` — `VALID_LOCALES`
- `scripts/manga/generate_series_plans_from_catalog.py:60` — `_RE_LOCALE_HEADING`
- `schemas/manga/series_plan.schema.json` — `locale` + `default_locale` + `localized_titles` enums (v2.2.0)

Format-routing entries in `config/manga/format_routing.yaml` are still needed before generator can emit hu_HU rows successfully.

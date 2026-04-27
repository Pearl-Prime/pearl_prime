# LATAM Catalog Plan (Spanish-language)

**Generated:** 2026-04-27
**Status:** SCAFFOLD — Pearl_Research deep-research authors fill format mix + revenue tables.
**Authority:** Pearl_Architect (scaffold) → Pearl_Research (research authoring) → Pearl_PM (acceptance)
**Scope:** `es_LA` locale — pan-Latin-America Spanish catalog covering MX, AR, CO, CL, PE, ES (cross-shipping)

This file is created as part of extending the manga catalog generator from 5 → 8 markets (`scripts/manga/generate_catalog_plan_from_strategic.py:55`). It exists so the generator can resolve `es_LA` per-locale rules; deep market research must follow.

---

## 1. Status

This plan is a **scaffold** — it defines the locale slot in the generator pipeline but DOES NOT yet contain the per-brand × per-genre allocation research that the CJK and US plans contain. Until Pearl_Research authors the §3 + §4 + §5 sections, the generator will fall back to defaults for `es_LA` rows.

## 2. Format and art style by sub-market (PLACEHOLDER)

| Sub-market | Format | Art Style | Platform |
|---|---|---|---|
| MX (Mexico) | TBD | TBD | TBD |
| AR (Argentina) | TBD | TBD | TBD |
| CO/CL/PE/other | TBD | TBD | TBD |
| ES (Spain — cross-shipping) | TBD | TBD | TBD |

**Decision needed:** is `es_LA` one consolidated format mix or split into `es_MX` / `es_AR` / `es_ES` later?

## 3. Brand tier assignments for es_LA — TO RESEARCH

Pearl_Research input needed:
- Which Phoenix Omega brands have natural fit for Spanish-speaking adult audiences?
- Which genres have proven LATAM market traction (telenovela influence on josei drama? lucha libre on action_battle? horror inheritance from horror cinema?)
- Cultural localization gates (Catholic vs secular framing; mestizo identity; family-centric framing of healing/grief)

## 4. Genre allocation for es_LA — TO RESEARCH

Pearl_Research input needed: per-brand × per-genre % allocations following the same 4-leg blend (`generate_catalog_plan_from_strategic.py:122-127` — strategic 0.20 + metadata 0.05 + market_revenue 0.70 + baseline 0.05).

**LATAM revenue weights** (TO POPULATE in `_GENRE_REVENUE_WEIGHTS` per LATAM):
- One Piece, Naruto, DBZ have huge LATAM resonance — `action_battle` likely > 1.50
- Telenovela genre baked into manga form may amplify `romance_josei_drama`
- Horror via Junji Ito + native folklore heritage — `psychological_horror` likely strong
- Iyashikei is undertested in LATAM market — measure via webtoon platform analytics

## 5. Translation provider routing — DECISION NEEDED

| Provider option | Cost | Quality | Notes |
|---|---|---|---|
| DeepSeek | Free tier | Unknown for Spanish | Need quality benchmark against Mexican/Argentine register |
| Claude Code (Tier 1) | Subscription | High | Operator-attended for hero titles |
| Edge TTS | Free | N/A (TTS not translation) | Audiobook side; Spanish voices: `es-MX-DaliaNeural`, `es-AR-ElenaNeural`, etc. |

**Decision needed before catalog generator emits LATAM rows:**
1. Translation provider for series-level metadata
2. Audiobook narrator voice mapping
3. Whether to consolidate `es_LA` or split per country

## 6. Distribution platform mapping — TO RESEARCH

Format-routing entries needed in `config/manga/format_routing.yaml`:
- `defaults_by_locale_genre.es_LA.<each genre>`
- `target_platforms_by_locale_format.es_LA.<each master_format>`
- `connector_lane_by_locale_format.es_LA.<each master_format>`
- `pending_partner_targets_by_locale.es_LA`

LATAM platforms (Pearl_Research to verify):
- Webtoon LATAM (Spanish-language Naver/LINE)
- Tappytoon ES, Lezhin ES
- Amazon LATAM (KDP)
- BookWalker LATAM (limited)
- Local: Bilbo (MX), Cúspide (AR), Editorial Planeta

## 7. Risk gates

- **Market-size risk:** LATAM audiobook market sizing per `artifacts/research/full_content_audit.md` — verify before committing to deep-format budgets.
- **Translation register risk:** Mexican vs Argentine Spanish vs European Spanish — wrong register loses entire sub-market.
- **Cultural fit risk:** wellness / self-help framing differs from Asian context; heavy individual-responsibility framing may underperform vs family-centric framing.

---

## Generator wiring

This locale is wired in:
- `scripts/manga/generate_catalog_plan_from_strategic.py:55` — `VALID_LOCALES`
- `scripts/manga/generate_series_plans_from_catalog.py:44` — `VALID_LOCALES`
- `scripts/manga/generate_series_plans_from_catalog.py:60` — `_RE_LOCALE_HEADING`
- `schemas/manga/series_plan.schema.json` — `locale` + `default_locale` + `localized_titles` enums (v2.2.0)

Format-routing entries in `config/manga/format_routing.yaml` are still needed before generator can emit LATAM rows successfully.

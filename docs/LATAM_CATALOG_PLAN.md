# LATAM Catalog Plan (Spanish-language)

**Generated:** 2026-04-27
**Status:** SCAFFOLD — Pearl_Research deep-research authors fill format mix + revenue tables.
**Authority:** Pearl_Architect (scaffold) → Pearl_Research (research authoring) → Pearl_PM (acceptance)
**Scope:** `es_LA` locale — pan-Latin-America Spanish catalog covering MX, AR, CO, CL, PE, ES (cross-shipping)

This file is created as part of extending the manga catalog generator from 5 → 8 markets (`scripts/manga/generate_catalog_plan_from_strategic.py:55`). It exists so the generator can resolve `es_LA` per-locale rules; deep market research must follow.

---

## 1. Status

This plan is a **scaffold** — it defines the locale slot in the generator pipeline but DOES NOT yet contain the per-brand × per-genre allocation research that the CJK and US plans contain. Until Pearl_Research authors the §3 + §4 + §5 sections, the generator will fall back to defaults for `es_LA` rows.

## 1A. RATIFIED — es_LA + pt_BR strategy (2026-05-29, operator)

> **✅ RATIFIED 2026-05-29 (operator).** These strategies are accepted; §3/§4 are authored from here. **Locale-wiring scope expansion APPROVED** — `pt_BR` (manga-forward, 2nd priority after France) to be wired via a separately-governed `VALID_LOCALES` + schema + `lane_content_mix` + `format_routing` change with series_plan regen (its own atomic PR, NOT done here); `es_LA` needs its dedicated `lane_content_mix` + `_GENRE_REVENUE_WEIGHTS` + format_routing. Figures cited inline.

### es_LA (Spanish-LATAM, Mexico-anchored)
- **Format mix (proposed):** ebook ~80% / manga ~10% / **audiobook companion on all hero titles** — audiobook is the growth engine (Mexico audiobooks $88.5M → $461.5M by 2030, **31.5% CAGR**; books +12.6% in 2024 = strongest global growth; self-help ≈ 30% of ebook revenue).
- **Genre tilt:** OVER `romance_josei_drama` (telenovela affinity), `psychological_horror` (folklore + horror-cinema), `dark_fantasy`, `supernatural_mystery`; self-help-adjacent contemporary. `action_battle` resonates (One Piece/Naruto/DBZ) but is licensed-IP-dominated → enter via webtoon, not print. UNDER cultivation, historical.
- **First-wave brands:** `gentle_growth_healing`, `confidence_core_romance`, `relational_calm_iyashikei`, `healing_ground_healing`, `digital_ground`. **Framing:** family-centric / Catholic-aware (not individual-responsibility) — repo risk gate.
- **Wiring (es_LA already in VALID_LOCALES):** needs dedicated `lane_content_mix.es_LA` (currently `_default`) + `format_routing` es_LA entries + `_GENRE_REVENUE_WEIGHTS.es_LA` before generation. European Spanish (es_ES) may share production but **NOT register**.

### pt_BR (Brazil) — FUTURE EXPANSION, NOT YET WIRED
- **Why best-for-manga:** top-3 ex-Asia anime market; manga $17M (2025) → $89.9M by 2033 (**23.7% CAGR**); One Piece = #2 best-selling comic nationally. Manga-forward (2nd-highest weight after France).
- **Format mix (proposed):** ebook ~72% / manga ~13% / audiobook companion. **Genre tilt:** OVER `action_battle`, `dark_fantasy`, `isekai`, `romance_josei_drama`, `psychological_horror`.
- **First-wave brands:** `solar_return_isekai`, `stillness_press` (full genre ladder), `digital_ground`, `healing_ground_healing`, `confidence_core_romance`.
- **Wiring (operator decision — scope expansion):** add `pt_BR` to `VALID_LOCALES` (both generators) + schema enum bump + `locale_pricing` (~0.55–0.65) + `lane_content_mix` + `format_routing`. This **enables BR catalog generation** — a deliberate scope expansion, not done here.

---

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

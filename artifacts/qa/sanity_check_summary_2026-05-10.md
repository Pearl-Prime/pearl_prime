# Executive brief — Marketing / revenue sanity check (2026-05-10)

**Project:** PRJ-MARKETING-RESEARCH-SANITY-CHECK-V1  
**Full report:** `artifacts/research/marketing_revenue_sanity_check_2026-05-10.md`  
**Verbatim audit (empty until MCP):** `artifacts/research/asian_market_external_ai_audit_2026-05-10.md`

---

## Headline

**Phoenix Omega marketing/revenue model is 0% confirmed by the intended external region-native AI layer** in this run, because **Chrome Claude MCP was not available** in the agent tool surface — no DeepSeek, Qwen, or Rakuten AI queries were executed. Internal repo claims were **catalogued** for the next cross-validation pass.

---

## Top 5 confirmed (repo-internal only — not external AI)

These are **documented and self-consistent** in Phoenix Omega materials; they are **not** independent third-party confirmations.

1. **Worldwide packaged-asset spine (1 : 1 : 2)** — English : Japanese : Chinese script weighting and 45,216 worldwide total appear on the Pearl Prime EN investor deck and reference PR #1023 rollups (`brand-wizard-app/public/pearl_prime_v6-3-en.html`).
2. **LINE OA is the Japan funnel backbone** — Pricing tiers, step messages, and LAP benchmarks are sourced in `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` with explicit URLs.
3. **Manga GTM uses explicit global/webtoon CAGR table** — `docs/MANGA_GTM_PLAN.md` states global manga ~$19.35B (2025), webtoons ~$9.7B, US manga ~$1.68B, and Year 1 net revenue band $120K–$240K.
4. **Investor DD workbook labels provenance** — `PHOENIX_OMEGA_INVESTOR_DD.xlsx` “Market Sizing” and “Unit Economics” sheets mark rows as EXTERNAL / ESTIMATE / ASSUMPTION / REPO-BACKED (sanity-checkable).
5. **Marketing volume SSOT is draft with zero non-manga surfaces** — `config/marketing/weekly_volumes_per_brand.yaml` documents V1 baseline `manga: 1/week` per Path-X brand and `0` for ebook/audiobook/podcast until operator Table 6 ratification.

---

## Top 5 refined or contradicted (needs external or primary-source pass)

Until the three chat UIs answer Q1–Q15, treat these as **“needs revision or proof”**, not as AI-verdicted.

1. **Master catalog locale “market size” cells** (`artifacts/catalog/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md`) mix audiobook USD, manga JPY, webtoon USD, and podcast-adjacent figures — **not always apples-to-apples** with `docs/MANGA_GTM_PLAN.md` global manga stats.
2. **Therapeutic audiobook TAM ($350M) and SAM ($245M)** in the investor workbook — **derived stack** from global audiobook TAM × genre shares; sensitive to the parent $7.7B figure and percentage assumptions (`PHOENIX_OMEGA_INVESTOR_DD.xlsx`, Market Sizing sheet).
3. **JP “+ Japanese market (manga adaptation)” $35M** line in same sheet cites “JP audiobook market growing 30% YoY” — **high leverage claim** for operator + external audit.
4. **Platform streaming economics** (`Unit Economics` — Spotify $/min, library checkout bands) — marked ESTIMATE/ASSUMPTION; should be checked against 2025–2026 distributor statements.
5. **`docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`** — **not present** in this tree at authoring time; deck references it (PR #1023). Spec/doc drift is a **governance risk** for any “confirmed” worldwide number.

---

## Operator decisions needed

| # | Decision |
|---|----------|
| 1 | **Enable Chrome MCP** (or paste verbatim AI transcripts into the audit file) so Pearl_Research can complete the 45 captures without fabricating quotes. |
| 2 | **Restore or link `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`** as the canonical worldwide plan doc referenced by the deck, or update deck footers to the real path. |
| 3 | After external AI responses exist: **ratify or revise** workbook TAM/SAM/SOM rows (Market Sizing sheet, rows 5–19) — do not auto-change without operator sign-off. |
| 4 | Choose whether **internal-only** confirmation (above) is acceptable for interim investor comms, or hold comms until **≥2 independent sources** agree on each headline number. |

**Count:** 4 decision clusters (MCP + doc drift + TAM stack + comms policy).

---

## HTML deck + spreadsheet

**Updates this run:** **0** HTML files, **0** spreadsheet cells — no external AI consensus and no operator ratification for numeric changes.

---

## Recommended next step

1. Operator: connect Chrome MCP + confirm logins.  
2. Re-run Phase 3 (15 questions × 3 AIs); paste verbatim outputs into `asian_market_external_ai_audit_2026-05-10.md`.  
3. Pearl_Research: regenerate the cross-validation matrix in the full sanity-check report, then apply **only** “refined + well-cited” updates to `pearl_prime_v6-3-en.html` and `PHOENIX_OMEGA_INVESTOR_DD.xlsx` per governance rules.

---

## Counts (this session)

| Metric | Value |
|--------|------:|
| External AI queries completed | 0 |
| DeepSeek captures | 0 |
| Qwen captures | 0 |
| Rakuten AI captures | 0 |
| HTML cells/slides changed | 0 |
| Workbook cells changed | 0 |
| Operator decisions listed | 4 |

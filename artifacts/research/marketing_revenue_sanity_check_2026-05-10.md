# Marketing + revenue sanity check — 2026-05-10

**Project ID:** PRJ-MARKETING-RESEARCH-SANITY-CHECK-V1  
**Subsystem:** marketing + research  
**Git branch:** `agent/marketing-revenue-sanity-check-20260510`  
**Worktree:** `/Users/ahjan/phoenix_omega_sanity_wt` (bootstrap from `origin/main`)

---

## STARTUP_RECEIPT

| Field | Value |
|-------|--------|
| Timestamp (authoritative date) | 2026-05-10 |
| Repo | phoenix_omega |
| Base | `origin/main` @ checkout time **06c75db33** (Pearl Prime worldwide catalog plan PR #1023) |
| External AI policy | Free chat UIs only — **no** DeepSeek/Qwen/Rakuten **API** calls |
| Chrome Claude MCP | **Not available** in this Cursor agent session → Phase 2–3 **not executed** |
| Files changed (this PR intent) | 3 markdown artifacts only (deck + workbook **unchanged**) |

---

## 1. Methodology

1. **Phase 1 — Internal capture:** Read marketing/revenue authority docs in-repo and extract numeric and strategic claims (see §2). Note: requested master file `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` was **not found** in this tree; QA artifact `artifacts/qa/pearl_prime_v6-3-en_authoring_2026-05-10.md` already flags that gap.
2. **Phase 2–3 — External region-native AIs:** Planned sources: DeepSeek, Qwen, Rakuten AI via Chrome MCP. **Blocked** — see `STOP_REASON: CHROME_MCP_UNAVAILABLE` in `artifacts/research/asian_market_external_ai_audit_2026-05-10.md`.
3. **Phase 4 — Matrix:** Built with **external columns empty**; verdicts default to **pending_external_validation**. A short **repo-only consistency** subsection flags internal tensions that external research should stress-test first.
4. **Phase 5 — Deck + workbook:** **No mutations.** Policy: no “refined” numbers without verbatim third-party capture + operator ratification for anything touching revenue (`CLAUDE.md` tier + task OUT_OF_SCOPE).
5. **Phase 6 — Deliverables:** This file + executive brief + audit template.

---

## 2. Phoenix Omega claims captured (Phase 1)

**Legend:** *Primary doc* = where the claim is stated for this sanity pass.

### 2.1 Per-locale market size — self-help / wellness **books**

| Locale / scope | Claim (summary) | Primary doc |
|----------------|-----------------|-------------|
| US | Illustrated self-help is text-first / Western cartoon; manga self-help niche “thin” | `docs/CJK_CATALOG_PLAN.md` §1 |
| Global / US | (Indirect) Therapeutic category whitespace framing | `docs/MANGA_GTM_PLAN.md` exec summary |
| en_US | “$5.2B audiobook” listed under Tier 1 locale row (audiobook, not print self-help) | `artifacts/catalog/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` Part 1 |

### 2.2 Per-locale market size — **manga** (zh + ja emphasis)

| Metric | Claim | Primary doc |
|--------|--------|-------------|
| Global manga 2025 | $19.35B | `docs/MANGA_GTM_PLAN.md` |
| Global manga 2031 | $56.38B; CAGR 19.52% | same |
| Webtoons 2025 / 2033 | $9.7B → $83.2B; CAGR 29.7% | same |
| US manga 2025 | $1.68B | same |
| Digital share | 72.7% | same |
| ja_JP | “¥200B+ manga” | `artifacts/catalog/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` |
| zh_CN | “$2.4B audio (Ximalaya 303M MAU)” | same |
| JP digital comics platforms | Piccoma / LINE Manga revenue order-of-magnitude and shares | `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` §1.8 |

### 2.3 Per-locale market size — **podcasts**

| Claim | Primary doc |
|-------|-------------|
| Marketing SSOT V1: `podcast: 0/week` baseline all Path-X brands | `config/marketing/weekly_volumes_per_brand.yaml` |
| Deep-research prompt inventory references Spotify listening model | `marketing_deep_research/deep-research-report.md` |

### 2.4 Audiobook market **growth** by locale

| Claim | Primary doc |
|-------|-------------|
| JP row: “JP audiobook market growing **30% YoY**” (supports $35M line) | `PHOENIX_OMEGA_INVESTOR_DD.xlsx` sheet **Market Sizing** row 13 (openpyxl read) |

### 2.5 Acquisition cost benchmarks (CPA, CTR, CVR) — channels / locales

| Claim | Primary doc |
|-------|-------------|
| LINE Ads: CPC ≈ ¥24+; CPM ≈ ¥100+ / 1k; CPV ¥50–75; **CPF ≈ ¥75–¥300** | `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` §1.7 |
| Blended CVR 1.5–2.5%; high-intent 2.5–3.5%; browse 0.8–1.5% | `PHOENIX_OMEGA_INVESTOR_DD.xlsx` **Unit Economics** rows 17–19 |

### 2.6 Per-brand revenue / throughput assumptions

| Claim | Primary doc |
|-------|-------------|
| Manga Year 1 net (all regions) **$120K–$240K** | `docs/MANGA_GTM_PLAN.md` |
| Regional Year 1 breakdown (CN, KR, US, BR, FR, UK/DE/ES bands) | same |
| US Pearl Prime deck: peak **$10,200/mo** month 12; 48Social **$850–$3.4K/mo** | `brand-wizard-app/public/pearl_prime_v6-3-en.html` (chart data + card) |
| ASP bands, platform splits, impression bands | `PHOENIX_OMEGA_INVESTOR_DD.xlsx` **Unit Economics** |

### 2.7 TAM / SAM / SOM (investor workbook)

| Row (sheet) | Claim | Provenance column |
|-------------|--------|---------------------|
| Market Sizing r5 | Global audiobook $7.7B (2025) | EXTERNAL: Grand View Research 2025 |
| r7 | Self-help audiobook TAM $1.4B | ESTIMATE |
| r9 | Therapeutic audiobook TAM $350M | ESTIMATE |
| r12–r14 | SAM components + $245M total | ESTIMATE |
| r17–r19 | SOM $68K / $240K / $800K Y1–Y3 | ASSUMPTION |

### 2.8 Competitive landscape

| Claim | Primary doc |
|-------|-------------|
| “Therapeutic manga” blue ocean; Graphic Medicine reference | `docs/MANGA_GTM_PLAN.md` |
| “ZERO localized therapeutic manga in ANY of these 13 markets” | `artifacts/catalog/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md` |
| Genre-shell revenue gap (explicit healing vs genre shell comps) | `docs/CJK_CATALOG_PLAN.md` §1 |
| Sunmark 本とTREE / Forest / competitive LINE audit | `artifacts/research/japan_line_competitive_funnel_audit_2026-04-29.md` |

### 2.9 Distribution fees / economics

| Claim | Primary doc |
|-------|-------------|
| China revenue model ~45% effective after MCN + tax | `docs/MANGA_GTM_PLAN.md` |
| US: Kindle 35–70%, Webtoon ad-share, Apple/Google 70/30 | same |
| Google Play 70%; INaudio net 80%; GP/INaudio split 62/38 in unit model | `PHOENIX_OMEGA_INVESTOR_DD.xlsx` **Unit Economics** |
| Kindle / BookWalker / Kobo as JP buy paths | `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` |

### 2.10 Freebie / funnel mechanics (non-dollar but GTM-critical)

| Claim | Primary doc |
|-------|-------------|
| Proof Loop: two micro-reliefs before offer; E4 book | `docs/FREEBIE_MARKETING_PLAN.md` |
| LINE step cadence vs email half-life | `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` §0, §1.2 |
| CJK shaping / font licensing context (HarfBuzz, FONT_REGISTRY) | `docs/MANGA_CJK_SHAPING.md` |

---

## 3. Per-AI findings summary

| AI | Questions asked | Verbatim stored |
|----|------------------:|-----------------|
| DeepSeek | 0 | No |
| Qwen | 0 | No |
| Rakuten AI | 0 | No |

**Reason:** Chrome Claude MCP tools absent from agent session — see audit file `STOP_REASON`.

---

## 4. Cross-validation matrix (external layer)

**Rule:** Without captured answers, every external cell is **—** and verdict is **pending_external_validation**.

| Phoenix Omega claim (§2 ref) | DeepSeek says | Qwen says | Rakuten AI says | VERDICT |
|------------------------------|-----------------|-----------|-------------------|---------|
| Global manga $19.35B / CAGR 19.52% (2.2) | — | — | — | pending_external_validation |
| ja_JP ¥200B+ manga (2.2) | — | — | — | pending_external_validation |
| zh_CN $2.4B audio + Ximalaya MAU (2.2) | — | — | — | pending_external_validation |
| JP audiobook +30% YoY (2.4) | — | — | — | pending_external_validation |
| Therapeutic TAM $350M / SAM $245M (2.7) | — | — | — | pending_external_validation |
| LINE CPF ¥75–¥300 (2.5) | — | — | — | pending_external_validation |
| Unit economics CVR bands (2.5) | — | — | — | pending_external_validation |
| Manga Y1 net $120K–$240K (2.6) | — | — | — | pending_external_validation |
| US deck peak $10,200 / 48Social $850–$3.4K (2.6) | — | — | — | pending_external_validation |
| “Zero therapeutic manga” competition (2.8) | — | — | — | pending_external_validation |

---

## 5. Per-claim verdicts (this session)

| Verdict | Meaning here | Count |
|---------|----------------|------:|
| **pending_external_validation** | Awaiting DeepSeek / Qwen / Rakuten verbatim passes | 10+ |
| **repo_documented** | Claim is traceable to an internal markdown/xlsx row; not independently verified | All captured claims |
| **internal_tension** | Two internal sources use different metrics or definitions — external pass should reconcile | See §5.1 |

No **confirmed** / **refined** / **contradicted** / **expanded** verdicts from the three external AIs (no data).

### 5.1 Internal tensions (repo-only — not a verdict on truth)

1. **“Market size” column in `PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md`** mixes formats (USD audiobook, JPY manga band, MAU) — fine for strategy, risky if read as a unified TAM table without footnotes.
2. **`MANGA_GTM_PLAN.md` regional revenue table** vs **`weekly_volumes_per_brand.yaml`** zero podcast/ebook/audio weekly targets — strategic revenue story vs SSOT throughput story must be explained together to investors.
3. **Deck cites `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1`** — file missing from tree at Phase 1 discovery; **doc drift** risk.

---

## 6. Changes made to HTML / spreadsheet

| Asset | Change | Before / After |
|-------|--------|----------------|
| `brand-wizard-app/public/pearl_prime_v6-3-en.html` | **None** | N/A |
| `PHOENIX_OMEGA_INVESTOR_DD.xlsx` | **None** | N/A |

**Rationale:** External AI layer blocked; workbook and deck numbers are high-sensitivity; operator ratification required for any revision.

---

## 7. Operator decisions needed

1. **Connect Chrome MCP** and re-run 45 Q&A captures (or manually paste verbatim answers into the audit file).
2. **Resolve worldwide plan doc path** vs deck references (`PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1`).
3. After external captures: **which TAM/SOM rows** in Market Sizing may be updated, and who signs off.
4. **Comms policy:** whether to cite “repo_documented” metrics as “confirmed” externally (recommended: no).

---

## 8. Recommended follow-up research workstreams

1. **MCP-enabled Pearl_Research rerun** — fill matrix §4; populate `asian_market_external_ai_audit_2026-05-10.md`.
2. **Primary-source pack** for workbook rows labeled EXTERNAL (Grand View, BookStat, etc.) — PDFs or paywalled extracts stored under `artifacts/research/provenance/` (separate PR if large).
3. **Single “metric dictionary”** doc — for each headline number, define: geography, year, currency, print vs digital vs audio, B2C vs B2B, gross vs net of platform fee.
4. **JP podcast + LINE funnel** — tie Q3/Q10 answers to `docs/JAPAN_LINE_FREEBIE_FUNNEL_PLAN_2026-04-29.md` (repo path; not under `docs/specs/` in this tree).

---

## CLOSEOUT_RECEIPT (partial — pending MCP + PR)

| Field | Value |
|-------|--------|
| Commit SHA | **244686880** (tip of PR branch; initial research payload **539ec9226**) |
| PR URL | **https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1029** |
| External alignment % | **0%** (0 / N claims validated by the three AIs) |
| DeepSeek / Qwen / Rakuten query counts | **0 / 0 / 0** |
| HTML / spreadsheet updates | **0 / 0** |
| Operator decisions surfaced | **4** (see executive brief) |
| Top “contradicted” by external AI | **N/A** — no external responses |
| STOP_REASON | **CHROME_MCP_UNAVAILABLE** |

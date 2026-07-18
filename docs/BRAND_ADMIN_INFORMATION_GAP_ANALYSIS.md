# Brand Admin Information Gap Analysis

**Date:** 2026-04-09
**Author:** Pearl_Marketing + Pearl_Prez + Pearl_Research
**Project:** proj_state_convergence_20260328
**Method:** Phase 1 (spreadsheet + research → independent needs list), Phase 2 (17-page HTML audit), Phase 3 (gap synthesis)

---

## Executive Summary

| Category | Total Items | Covered | Partial | Missing | Score |
|----------|------------|---------|---------|---------|-------|
| Tier 1 (Day 1 blockers) | 14 | 8 | 4 | 2 | 57% covered |
| Tier 2 (Week 2 quality) | 12 | 3 | 5 | 4 | 25% covered |
| Tier 3 (Mastery) | 8 | 2 | 3 | 3 | 25% covered |
| **Total** | **34** | **13** | **12** | **9** | **38% fully covered** |

**Worst-served category:** Locale intelligence — invisible scripts, cultural framing, per-market SEO strategy, and regulatory requirements are almost entirely absent from brand admin pages despite being extensively documented in research.

**Most redundant information:** `brand_admin.html` and `brand_admin_weekly_os.html` share identical brand data (24 brands), keyword dictionary, setup steps, upload platforms, and weekly schedule. Any data change must be made in two places — active drift risk.

**Highest-priority gaps (top 5):**

1. **No data provenance labels on any HTML page** — 21 metrics were corrected from fabricated to repo-backed, but no page tells the admin which numbers are proven vs projected
2. **No per-locale invisible scripts or cultural framing** — research docs contain extensive per-market language guidance (e.g., ko-KR: never use 정신건강; use 힐링) but zero pages surface this
3. **No unit economics for brand admins** — pricing tiers, revenue shares, and cost structure exist in the spreadsheet but are not shown in any operational page
4. **No podcast/video/manga platform playbooks** — operational pages cover ebook uploads only; podcast RSS, video specs, manga distribution are absent
5. **No per-market keyword/SEO strategy** — search behavior research identifies optimal title structures and pain-state keywords per market but no page delivers this

---

## Phase 1: What Brand Admins Need

### Spreadsheet Analysis (11 Sheets)

#### Sheet 1: Data Provenance
- **Brand admin value:** CRITICAL — teaches admins that revenue figures are assumptions, not actuals. Without this, admins may set unrealistic expectations.
- **Decision enabled:** Trust calibration — know what's proven ($0 COGS) vs projected (revenue ramps).
- **Currently surfaced in HTML:** NOWHERE. No page shows provenance labels.
- **Provenance:** N/A (meta-sheet).

#### Sheet 2: Executive Summary
- **Brand admin value:** HIGH — entity name, mission, teacher count, format count, topic count.
- **Decision enabled:** Elevator pitch to stakeholders; understanding system scope.
- **Key items for admins:** 13 teachers, 24 brands, 15 topics, 18 formats, 7 V3.2 systems, $0 COGS.
- **Provenance:** MIXED — system facts REPO-BACKED; "2,160+ books" is ESTIMATE (24×90 target).

#### Sheet 3: Monthly Revenue Ramp
- **Brand admin value:** LOW-MEDIUM — useful for expectation-setting but ALL ASSUMPTION.
- **Decision enabled:** Cash flow planning; understanding organic growth curve.
- **Risk:** Admin may treat $1,800 Month 1 GP revenue as a promise rather than a projection.
- **Provenance:** ALL ASSUMPTION: pre-revenue projections.

#### Sheet 4: Unit Economics
- **Brand admin value:** CRITICAL — pricing tiers, platform rev shares, cost structure.
- **Decision enabled:** Which price to set per book type; which platform to prioritize.
- **Key items:** Micro $1.99-$7.99, Deep $14.99-$29.99, GP 70%, INaudio 80%, $0 COGS.
- **Provenance:** MIXED — pricing REPO-BACKED; conversion rates ASSUMPTION.

#### Sheet 5: Brand Catalog (24)
- **Brand admin value:** HIGH — persona, emotional job, functional job, pricing per brand.
- **Decision enabled:** Which persona to target; what language to use per brand.
- **Key items:** 24 brands with specific persona ages, emotional jobs, pricing tiers.
- **Provenance:** MOSTLY REPO-BACKED (brand_archetype_registry); book counts are ESTIMATE.

#### Sheet 6: Revenue by Cluster
- **Brand admin value:** MEDIUM — shows Nervous System cluster at 42% of projected revenue.
- **Decision enabled:** Resource allocation across clusters.
- **Provenance:** MIXED — cluster composition REPO-BACKED; revenue ASSUMPTION.

#### Sheet 7: Top Brand Performance
- **Brand admin value:** MEDIUM — portfolio decision framework (double down / monitor / kill).
- **Decision enabled:** 90-day brand triage.
- **Provenance:** ALL ASSUMPTION — no sales data exists.

#### Sheet 8: Platform Strategy
- **Brand admin value:** HIGH — platform rev shares, % of total revenue, role per platform.
- **Decision enabled:** Upload prioritization (GP 62% → highest priority).
- **Provenance:** MIXED — rev shares EXTERNAL; % splits ASSUMPTION.

#### Sheet 9: IP & Technology
- **Brand admin value:** MEDIUM — understanding what EI v2 does for trust building.
- **Decision enabled:** Explaining the system to stakeholders; understanding QA pipeline.
- **Provenance:** ALL REPO-BACKED.

#### Sheet 10: Market Sizing
- **Brand admin value:** LOW-MEDIUM — context for why this market matters.
- **Decision enabled:** Stakeholder conversations; market justification.
- **Provenance:** MIXED — TAM EXTERNAL; SOM targets ASSUMPTION.

#### Sheet 11: 3-Year P&L
- **Brand admin value:** LOW — primarily investor-facing.
- **Decision enabled:** Understanding business trajectory; knowing $0 COGS is structural.
- **Key admin insight:** $0 COGS means every sale is pure margin minus platform fees.
- **Provenance:** MOSTLY ASSUMPTION; $0 COGS is REPO-BACKED.

### Market Research Analysis (14 Documents)

**Critical findings a brand admin needs:**

1. **Platform-specific tactics per market** — Source: advertising_roi_research.md, podcast_platform_marketing_research.md
   - US: Amazon Ads + Meta core, BookTok primary organic, 10+ reviews before ads work
   - JP: LINE Ads at $0.67 CPM (10× cheaper than Meta), seiyuu narration, Audiobook.jp
   - KR: Naver at $0.054 CPC (cheapest globally), blog reviews > display ads
   - CN: Ximalaya 345M MAU, WeChat $7K minimum, requires Chinese entity
   - TW: LINE Ads dominant, Readmoo for ebooks, KKBOX for audio

2. **Invisible scripts per market** — Source: 04_invisible_scripts.yaml, therapeutic_manga_wellness_market_research.md
   - ko-KR: NEVER use 정신건강 (mental health, severe stigma), USE 힐링/마음 건강
   - ja-JP: Indirect language ("you may notice" not "you will"), keigo required
   - de-DE: "Wissenschaftlich fundiert" (scientifically grounded) is THE keyword
   - zh-TW: "身心靈" (body-mind-spirit) is the power keyword
   - fr-FR: Philosophical/existentialist framing works; avoid aggressive marketing

3. **Pricing psychology per market** — Source: global_format_market_research.md
   - US: $0.99 cold-start → $3.99-$6.99 standard → $14.99+ premium
   - JP: ¥100-¥300 micro viable; creative/paradoxical titles culturally accepted
   - KR: KRW 5,000-10,000 sweet spot; healing essays dominate charts
   - TW: NT$200-$350 sweet spot; 身心靈 discovery keyword
   - CN: ¥10-¥30 ebooks; short-form often outsells full-length

4. **Content format priorities per market** — Source: global_format_market_research.md, manga_gtm_plan.md
   - US: Audiobook → Ebook → Podcast → Video → Manga
   - JP: Manga → Audiobook → Ebook → Video (manga market $10B)
   - KR: Webtoon → Audiobook → Ebook (webtoon market $1.54B → $8.2B)
   - FR: Manga → Ebook → Audiobook (#2 manga market globally)
   - DE: Audiobook → Ebook (Europe's #1 audiobook market, 29M users)

5. **Title/SEO strategy** — Source: search_behavior_title_strategy_research.md
   - Optimal: Creative title (2-5 words) + keyword-rich subtitle (5-12 words)
   - Amazon: 37% ranking lift from keyword in title OR subtitle
   - Pain-state keywords outperform clinical terms ("can't sleep" > "sleep anxiety")
   - Per-market: Japan accepts creative/metaphorical; Korea rewards emotional resonance; Germany requires scientific framing

6. **Competitive whitespace** — Source: therapeutic_manga_wellness_market_research.md
   - Wellness manga: ZERO localized examples in ANY of 9 studied markets
   - Polyvagal/somatic content in Korean: completely unoccupied
   - Hungarian self-help: "virtually non-existent" — total greenfield
   - Cantonese audiobooks: near-zero supply

### Phase 1C: Prioritized Needs List

#### TIER 1 — Must Know on Day 1 (Blocks All Work Without It)

| # | Need | Why It Matters | Data Source |
|---|------|---------------|-------------|
| T1.1 | Which brands they manage (name, persona, topics) | Can't create/upload without knowing the brand | Spreadsheet: Brand Catalog (24); config/brand_archetype_registry.yaml |
| T1.2 | Pricing tiers per brand (micro vs deep) | Wrong price = wrong royalty tier | Spreadsheet: Unit Economics; brand_archetype_registry.yaml |
| T1.3 | Upload platforms and accounts needed | Can't distribute without accounts | Spreadsheet: Platform Strategy; brand_admin.html Phase 1 setup |
| T1.4 | Weekly operating rhythm (7-day schedule) | Missed uploads = missed revenue windows | brand_admin.html Phase 3; brand_admin_weekly_os.html |
| T1.5 | Revenue share per platform | Must understand take-home per sale | Spreadsheet: Unit Economics (GP 70%, INaudio 80%) |
| T1.6 | Content package structure (what arrives weekly) | Must know what to expect and upload | brand_admin.html Phase 2 (15 titles: 8 ebook + 4 manga + 3 micro) |
| T1.7 | $0 COGS reality and what it means | Fundamental value proposition | Spreadsheet: Unit Economics; REPO-BACKED |
| T1.8 | Platform-specific metadata requirements | Uploads rejected without correct metadata | Platform docs (Amazon KDP, Google Play, Apple Books specs) |
| T1.9 | Per-market language (what locale they serve) | Wrong language = wrong market | config/localization/locale_registry.yaml |
| T1.10 | AI disclosure requirements per platform | Legal compliance, especially zh-CN | locale_registry.yaml notes; platform TOS |
| T1.11 | KPI tracking — what to measure weekly | Can't improve what you don't measure | Not documented anywhere operationally |
| T1.12 | Escalation path (when uploads fail, what to do) | Stuck admin = lost revenue | Not documented anywhere |
| T1.13 | Quality verification steps per upload | Bad uploads damage brand trust | Partially in brand_admin.html checklist |
| T1.14 | Data provenance — which claims are proven | Prevents false confidence in projections | Spreadsheet: Data Provenance sheet |

#### TIER 2 — Must Know by Week 2 (Quality and Growth Depend On It)

| # | Need | Why It Matters | Data Source |
|---|------|---------------|-------------|
| T2.1 | Invisible scripts per market | Wrong language alienates readers | 04_invisible_scripts.yaml; therapeutic_manga_research.md |
| T2.2 | Voice/narrator identity per brand | Audio brand consistency | config/tts/narrator_voice_assignments.yaml |
| T2.3 | SEO keywords per topic per market | Discoverability depends on keyword matching | search_behavior_title_strategy_research.md |
| T2.4 | Title structure strategy | Creative title + keyword subtitle = 37% ranking lift | search_behavior_title_strategy_research.md |
| T2.5 | Cover art guidelines per brand | Visual brand identity consistency | config/catalog_planning/brand_identity_system.yaml |
| T2.6 | Release cadence recommendations | Timing affects algorithm favor | global_format_market_research.md |
| T2.7 | Format priorities per market | Audiobook first in US/DE; manga first in JP/KR/FR | global_format_market_research.md |
| T2.8 | Podcast RSS submission (Spotify, Apple, etc.) | New format channel not covered operationally | docs/PODCAST_PLATFORM_MARKETING_RESEARCH.md |
| T2.9 | Video upload specs per platform | 16:9 vs 9:16, duration limits, text overlay rules | video_format_strategy_2026_04_06.md |
| T2.10 | Manga distribution (LINE, Piccoma, Kakao, WEBTOON) | Per-market manga platforms with different models | manga_gtm_plan.md |
| T2.11 | Ad spend readiness criteria | When to start paid ads (10+ reviews, 3.3+ average) | advertising_roi_research.md |
| T2.12 | Email/SMS marketing playbook | E1-E5 proof loop sequence, 2K subscriber target | advertising_roi_research.md |

#### TIER 3 — Should Know for Mastery (Competitive Advantage)

| # | Need | Why It Matters | Data Source |
|---|------|---------------|-------------|
| T3.1 | Market sizing context | Why this opportunity matters | Spreadsheet: Market Sizing |
| T3.2 | Competitor gaps per market | Where first-mover advantage exists | therapeutic_manga_research.md; global_format_market_research.md |
| T3.3 | Algorithm optimization per platform | Amazon A10, Spotify BERT, BookTok signals | search_behavior_title_strategy_research.md |
| T3.4 | Teacher market validation matrix | Which teacher fits which market best | teacher_market_validation_matrix.md |
| T3.5 | Portfolio decision framework | Double down / monitor / kill at 90 days | Spreadsheet: Top Brand Performance |
| T3.6 | B2B corporate wellness opportunity | License micro-books to employers | global_format_market_research.md |
| T3.7 | Revenue ramp expectations (honest) | Realistic Month 1-12 trajectory | Spreadsheet: Monthly Revenue Ramp (ALL ASSUMPTION) |
| T3.8 | 3-year business trajectory | Long-term context for daily work | Spreadsheet: 3-Year P&L |

---

## Phase 2: Page-by-Page Audit

### Coverage Matrix (17 Pages × 6 Categories)

| Page | Unit Econ | Platform Playbook | Locale Intel | Brand Identity | Weekly Ops | Multi-Format | Provenance | Quality |
|------|-----------|------------------|--------------|----------------|------------|--------------|------------|---------|
| brand_onboarding_hub.html | MISSING | PARTIAL (links) | MISSING | PARTIAL (5 archetypes, voice) | MISSING | PARTIAL (mentions audio) | MISSING | 8/10 |
| us_brand_admin_v32_briefing.html | MISSING | MISSING | MISSING | PARTIAL (V3.2 systems) | MISSING | PARTIAL (audiobook tab) | MISSING | 7/10 |
| jp_brand_admin_v32_briefing.html | MISSING | PARTIAL (9 platforms listed) | PARTIAL (cultural protocols) | PARTIAL (manga archetypes) | MISSING | PARTIAL (manga focus) | MISSING | 8/10 |
| writer_v32_quick_reference.html | MISSING | MISSING | MISSING | COVERED (21 V3.2 fields) | MISSING | PARTIAL (audio fields) | N/A | 9/10 |
| brand_admin.html | MISSING | COVERED (10 setup + 7 upload) | MISSING | PARTIAL (24 brands listed) | COVERED (7-day schedule) | PARTIAL (ebook + manga + video) | MISSING | 8/10 |
| brand_admin_weekly_os.html | MISSING | COVERED (duplicate) | MISSING | PARTIAL (duplicate) | COVERED (duplicate) | PARTIAL (duplicate) | MISSING | 7/10 |
| brand_admin_master_onboarding.html | MISSING | MISSING | MISSING | MISSING | MISSING | PARTIAL (audio proof) | MISSING | 6/10 |
| lane_examples_gallery.html | MISSING | MISSING | MISSING | PARTIAL (visual proofs) | MISSING | PARTIAL (multi-type tiles) | PARTIAL (status pills) | 7/10 |
| market_lane_matrix.html | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | PARTIAL (ready/missing) | 8/10 |
| brand-wizard-app brand_admin.html | MISSING | COVERED (10 setup + 7 upload) | MISSING | PARTIAL (24 brands) | COVERED (7-day) | PARTIAL (ebook + manga + video) | MISSING | 7/10 |
| marketing_dashboard.html | PARTIAL (value ladder) | PARTIAL (ad simulator) | PARTIAL (lane comparison) | MISSING | MISSING | MISSING | MISSING | 8/10 |
| teacher_showcase.html | MISSING | MISSING | MISSING | COVERED (13 teachers) | MISSING | COVERED (book + audio + video + manga) | MISSING | 6/10 |
| presenter.html | PARTIAL (revenue ranges) | PARTIAL (per-market platforms) | PARTIAL (per-market narration) | MISSING | PARTIAL (weekly OS slides) | PARTIAL (audiobook mentions) | MISSING | 8/10 |
| teacher_select.html | MISSING | MISSING | MISSING | COVERED (13 teachers) | MISSING | PARTIAL (cover + book) | MISSING | 8/10 |
| content_inventory.html | MISSING | MISSING | MISSING | MISSING | MISSING | COVERED (all types tracked) | COVERED | 9/10 |
| pearl_prime_entry.html | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | 9/10 |
| market_lane_matrix.html (wizard) | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | PARTIAL | 7/10 |

### Specific Gap Assessment

#### a) UNIT ECONOMICS
- **Exact pricing tiers per brand:** MISSING from all operational pages. The spreadsheet has detailed per-brand pricing (micro $1.99-$7.99, deep $14.99-$29.99) but no HTML page shows this.
- **Revenue share per platform:** MISSING. GP 70%, INaudio 80% documented in spreadsheet only.
- **Expected revenue per brand per month:** Only in marketing_dashboard.html's lane comparison (hardcoded estimates without provenance).
- **$0 COGS explanation:** Mentioned in onboarding_hub.html narrative but not explained operationally.

#### b) PLATFORM PLAYBOOK
- **Step-by-step upload instructions:** COVERED in brand_admin.html (10 setup + 7 upload platforms).
- **Platform-specific metadata requirements:** PARTIAL — prefill fields exist but no platform-specific format spec.
- **Release timing recommendations:** MISSING entirely.
- **Algorithm optimization tips:** MISSING. Research docs contain Amazon A10, Spotify BERT, BookTok signal data but no page delivers it.

#### c) LOCALE INTELLIGENCE
- **Invisible scripts per market:** MISSING from all pages. Research has extensive per-market guidance.
- **Cultural framing differences:** PARTIAL — jp_brand_admin_v32_briefing.html has 6 cultural protocol cards. No other market has this.
- **Per-market keyword/SEO strategy:** MISSING. Title strategy research identifies optimal structures per market but no page delivers this.
- **Regulatory requirements:** MISSING. zh-CN AI disclosure, ISBN requirements, Douyin content rules — all in research, none in pages.

#### d) BRAND IDENTITY
- **Full visual identity per brand:** PARTIAL — config/brand_identity_system.yaml has 37 brands × complete visual specs (colors, fonts, colophon, texture) but no page renders this for brand admins.
- **Cover art guidelines:** MISSING from operational pages.
- **Voice/narrator identity per brand:** MISSING — 480 narrator assignments in config but not surfaced.
- **Brand positioning vs competitors:** MISSING from admin pages; only in research docs.

#### e) WEEKLY OPERATING RHYTHM
- **Clear weekly checklist:** COVERED in brand_admin.html Phase 3 (7-day schedule with day cards).
- **KPI tracking:** MISSING. No page tells admins what metrics to check or what "good" looks like.
- **Escalation paths:** MISSING. No documentation of what to do when uploads fail.
- **Quality verification steps:** PARTIAL — checkboxes exist but no verification criteria documented.

#### f) MULTI-FORMAT COVERAGE
- **Ebook:** COVERED (upload steps in brand_admin.html).
- **Audiobook:** PARTIAL — mentioned in briefings, 60s clips in showcase, but no upload playbook.
- **Podcast:** MISSING entirely from all operational pages. Research doc (PODCAST_PLATFORM_MARKETING_RESEARCH.md) has complete platform data.
- **Video:** PARTIAL — TikTok and YouTube mentioned in brand_admin.html Phase 3 but no spec/format guidance.
- **Manga:** PARTIAL — WEBTOON upload in brand_admin.html; jp_briefing covers manga archetypes. LINE, Piccoma, Kakao distribution MISSING.

#### g) DATA PROVENANCE
- **REPO-BACKED/ESTIMATE/ASSUMPTION labels:** MISSING from every HTML page except content_inventory.html.
- **Fabricated data risk:** 21 metrics were corrected from fabricated to repo-backed (per SESSION_HANDOFF), but the correction is only documented internally, not visible to admins.
- **Provenance system exists:** The spreadsheet Data Provenance sheet defines the label system perfectly — it just isn't applied in any HTML.

---

## Phase 3: Gap Analysis

### Critical Missing Information (Tier 1 Gaps)

#### GAP 1: Data Provenance Labels on All Pages
- **What's missing:** No HTML page labels any metric as REPO-BACKED, ESTIMATE, or ASSUMPTION.
- **Why it matters:** Brand admins may set unrealistic revenue expectations or present assumptions as facts to stakeholders. The Data Provenance sheet defines a clear 4-label system — it's just not applied.
- **Source data:** Spreadsheet: Data Provenance sheet; PRESENTATION_SET_README.md (design rules).
- **Target page(s):** ALL pages with metrics — onboarding_hub.html, us_briefing, jp_briefing, marketing_dashboard.html, presenter.html.
- **Implementation:** Add colored label pills (green/orange/red/blue per PRESENTATION_SET_README.md) next to every metric.
- **Complexity:** MODERATE — requires auditing every metric on every page.

#### GAP 2: Unit Economics for Brand Admins
- **What's missing:** Pricing tiers, revenue shares, and cost structure not shown in any operational page.
- **Why it matters:** Admin can't set correct prices or prioritize platforms without knowing GP 70% vs INaudio 80%.
- **Source data:** Spreadsheet: Unit Economics sheet; config/brand_archetype_registry.yaml.
- **Target page(s):** brand_onboarding_hub.html (new "Economics" tab); brand_admin.html (pricing reference in Phase 2).
- **Complexity:** TRIVIAL — data exists, just needs HTML rendering.

#### GAP 3: KPI Tracking and Escalation Paths
- **What's missing:** No page tells admins what to measure weekly or what to do when something breaks.
- **Why it matters:** Admins operating without feedback loops can't improve; stuck admins lose revenue days.
- **Source data:** Needs creation based on platform analytics docs.
- **Target page(s):** brand_admin.html Phase 3 (add KPI card to Saturday "Review" day); new escalation section.
- **Complexity:** MODERATE — KPI definitions need authoring.

### Partial Coverage (Needs Improvement)

#### PARTIAL 1: Locale Intelligence (JP only)
- **Current state:** jp_brand_admin_v32_briefing.html has 6 cultural protocol cards (keigo, seasonal resonance, visual density, reading direction, group harmony, quiet authority). No other market has this.
- **What's needed:** Equivalent cultural protocol + invisible scripts sections for US, KR, TW, CN, DE, FR markets.
- **Source data:** 04_invisible_scripts.yaml; therapeutic_manga_research.md; per-market sections in research docs.

#### PARTIAL 2: Multi-Format Platform Playbooks
- **Current state:** Ebook upload steps covered well. Audiobook, podcast, video, manga have minimal or zero operational guidance.
- **What's needed:** Per-format upload playbooks covering at minimum: podcast RSS submission, video specs per platform, manga distribution per market.
- **Source data:** PODCAST_PLATFORM_MARKETING_RESEARCH.md; video_format_strategy.md; MANGA_GTM_PLAN.md.

#### PARTIAL 3: Marketing Dashboard Provenance
- **Current state:** marketing_dashboard.html has 6 Chart.js visualizations with hardcoded data. The heatmap is explicitly random-seeded in code but presented as "Content Performance" to viewers.
- **What's needed:** Provenance disclosure; replace random-seeded heatmap with actual data or honest labeling.

### Redundancy / Conflict

| Issue | Files Affected | Risk |
|-------|---------------|------|
| Near-identical brand admin pages | brand_admin.html + brand_admin_weekly_os.html | Data drift — any brand/keyword change must be made twice |
| Duplicate brand data (24 brands) | brand_admin.html + brand_admin_weekly_os.html + brand-wizard-app brand_admin.html | Triple maintenance |
| Duplicate nav bars | 4+ pages duplicate the same 6-10 link nav bar inline | Link changes must be made in every file |
| Market data without provenance | onboarding_hub.html + us_briefing + marketing_dashboard.html | Same metrics shown differently without source |
| Teacher count inconsistency | Some pages say 12 teachers, some say 13 | Confusion about canonical count |

### Recommended Page Architecture

#### Pages to Consolidate
1. **brand_admin_weekly_os.html → DEPRECATE** — brand_admin.html with `?phase=3` serves the same purpose with more features.
2. **brand_admin_master_onboarding.html → DEPRECATE** — role is unclear; brand_onboarding_hub.html is the better entry point.

#### Pages Needing New Sections
1. **brand_onboarding_hub.html** — Add: Unit Economics tab, Locale Intelligence tab (or expand Market Data).
2. **us_brand_admin_v32_briefing.html** — Add: Provenance labels on all metrics; Platform Economics section.
3. **brand_admin.html** — Add: KPI tracking to Phase 3 Saturday; Escalation section; Pricing reference to Phase 2.
4. **marketing_dashboard.html** — Add: Provenance disclosure; Replace random heatmap.

#### Ideal Brand Admin Journey (Page Flow)
```
pearl_prime_entry.html (market selection)
  → brand_onboarding_hub.html (orientation, 7 tabs)
    → teacher_select.html (choose teacher)
      → brand_admin.html?phase=0 (onboarding)
        → Phase 1: Setup platforms
        → Phase 2: First upload
        → Phase 3: Weekly rhythm ← KPI + escalation needed here
  → {market}_briefing.html (deep market knowledge)
  → marketing_dashboard.html (strategy + analytics)
  → teacher_showcase.html (content preview)
  → presenter.html (stakeholder presentation)
```

---

## Appendix: Spreadsheet Sheet → Admin Relevance

| Sheet | Admin Relevant? | Which Page Should Carry It | How |
|-------|----------------|---------------------------|-----|
| Data Provenance | YES — meta | ALL pages with metrics | Provenance labels (colored pills) |
| Executive Summary | YES — partial | brand_onboarding_hub.html Mission tab | Metric cards with provenance |
| Monthly Revenue Ramp | LOW — expectations only | marketing_dashboard.html | Honest-labeled chart |
| Unit Economics | YES — critical | brand_onboarding_hub.html (new tab) + brand_admin.html | Pricing table + platform rev share table |
| Brand Catalog (24) | YES — critical | brand_admin.html picker + brand_onboarding_hub.html | Already partially covered |
| Revenue by Cluster | MEDIUM | marketing_dashboard.html | Chart with ASSUMPTION label |
| Top Brand Performance | MEDIUM | marketing_dashboard.html | Portfolio framework with ASSUMPTION label |
| Platform Strategy | YES | brand_onboarding_hub.html + brand_admin.html | Platform comparison table |
| IP & Technology | LOW-MEDIUM | brand_onboarding_hub.html V3.2 tab | Already partially covered |
| Market Sizing | LOW | marketing_dashboard.html | Context chart with EXTERNAL label |
| 3-Year P&L | LOW | Investor-only (spreadsheet) | Do not add to admin pages |

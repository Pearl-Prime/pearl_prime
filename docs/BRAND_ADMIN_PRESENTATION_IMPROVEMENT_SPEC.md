# Brand Admin Presentation Improvement Spec

**Date:** 2026-04-09
**Author:** Pearl_Marketing + Pearl_Prez + Pearl_Research
**Companion:** docs/BRAND_ADMIN_INFORMATION_GAP_ANALYSIS.md
**Priority:** Top 10 improvements from the gap analysis, dev-ready

---

## Improvement 1: Data Provenance Labels on All Metric Pages

**Priority:** P0
**Gap:** GAP 1 — No HTML page labels metrics as REPO-BACKED / ESTIMATE / ASSUMPTION
**Target pages:** brand_onboarding_hub.html, us_brand_admin_v32_briefing.html, jp_brand_admin_v32_briefing.html, marketing_dashboard.html

**Content to add:**
Add a colored label pill next to every hardcoded metric:
- `<span class="prov prov-repo">REPO-BACKED</span>` — green
- `<span class="prov prov-est">ESTIMATE</span>` — orange, yellow background
- `<span class="prov prov-assum">ASSUMPTION</span>` — red, yellow background
- `<span class="prov prov-ext">EXTERNAL</span>` — blue

**CSS (add to each page's `<style>` block):**
```css
.prov { font-family: var(--mono, 'DM Mono', monospace); font-size: .55rem; padding: 2px 6px; border-radius: 4px; letter-spacing: .04em; vertical-align: middle; margin-left: 4px; }
.prov-repo { color: #4ade80; background: rgba(74,222,128,.1); }
.prov-est { color: #f59e0b; background: rgba(245,158,11,.1); }
.prov-assum { color: #f87171; background: rgba(248,113,113,.1); }
.prov-ext { color: #60a5fa; background: rgba(96,165,250,.1); }
```

**Metrics to label (per page):**

brand_onboarding_hub.html:
| Metric | Value | Label |
|--------|-------|-------|
| Revenue to admin | 90.6% | ASSUMPTION |
| Pearl Prime share | 4.8% | ASSUMPTION |
| Month 12 revenue | $10.8-18.7K | ASSUMPTION |
| Global audiobook market 2030 | $35B+ | EXTERNAL |
| YoY audiobook growth | 25%+ | EXTERNAL |
| BookTok 2024 sales | 59M | EXTERNAL |
| V3.2 titles/quarter | 2.7x | ASSUMPTION |
| Pre-purchase conversion | +35% | ASSUMPTION |

us_brand_admin_v32_briefing.html (all 7 system metrics × 3 each = ~21 metrics):
- All V3.2 system metrics (+42%, +28%, +31%, etc.): ASSUMPTION
- Languages at launch (11): REPO-BACKED
- BookTok 59M: EXTERNAL
- Revenue ranges: ASSUMPTION

**Data source:** Spreadsheet: Data Provenance sheet (exact classifications per sheet).
**Design:** Match existing dark theme; labels appear inline after the metric value.
**LOE:** 4-6 hours (audit ~60 metrics across 4 pages, add label per metric).

---

## Improvement 2: Unit Economics Section in Onboarding Hub

**Priority:** P0
**Gap:** T1.2, T1.5, T1.7 — Pricing, revenue shares, and $0 COGS not shown
**Target page:** brand_onboarding_hub.html — new 8th tab "Economics"

**Content to add:**

New tab panel `<div class="tp" id="t-econ">` with three sections:

**Section A: Pricing Tiers (source: Spreadsheet: Unit Economics; brand_archetype_registry.yaml)**
```
Micro Sessions (Tier D-E)    $1.99 – $7.99   REPO-BACKED
Standard Books               $3.99 – $6.99   REPO-BACKED
Deep Dives (Tier A-B)       $14.99 – $29.99  REPO-BACKED
Blended ASP                  $6.00 – $6.50   REPO-BACKED
Series Bundle Discount       15 – 25%         ESTIMATE
```

**Section B: Platform Revenue Shares (source: Spreadsheet: Unit Economics; platform TOS)**
```
Google Play Books    70% to publisher   EXTERNAL
INaudio (Findaway)   80% net revenue    EXTERNAL
Library Checkouts    $1.50-$4.00/each   ESTIMATE
Spotify Streaming    $0.005-$0.02/min   ESTIMATE
```

**Section C: Cost Structure (source: Spreadsheet: Unit Economics; pipeline docs)**
```
Voice Production     $0  (auto-narration)      REPO-BACKED
Content Writing      $0  (deterministic assembly) REPO-BACKED
Paid Advertising     $0  (organic only)         REPO-BACKED
COGS Per Book        $0  (zero marginal cost)   REPO-BACKED
```

**Design:** Use existing `.ssg` stat grid for pricing, `.rc` resource cards for platform shares, `.ss` stat boxes for cost structure. All with provenance pills.
**LOE:** 2-3 hours.

---

## Improvement 3: Per-Market Invisible Scripts and Cultural Framing

**Priority:** P0
**Gap:** T2.1 — Invisible scripts per market completely absent from all pages
**Target pages:** brand_onboarding_hub.html (expand Market Data tab); per-market briefings

**Content to add (per market, sourced from 04_invisible_scripts.yaml + therapeutic_manga_research.md):**

**Korea (ko-KR):**
- NEVER use: 정신건강 (mental health) — severe stigma, only 7% seek psychiatric help
- USE: 힐링 (healing), 번아웃 (burnout), 마음 건강 (heart/mind health), 신경계 (nervous system)
- Polyvagal/vagus nerve framing: COMPLETELY UNOCCUPIED — first-mover opportunity
- Ppalli-ppalli culture: micro-content (15-30 min) outperforms long-form

**Japan (ja-JP):**
- Indirect language: "you may notice" not "you will"
- Keigo (politeness register) required for narration
- Seasonal framing (cherry blossom/autumn/winter) increases engagement
- 嫌われる勇気 pattern: creative/paradoxical titles culturally accepted
- Secular/practical positioning — never "therapy"

**Germany (de-DE):**
- "Wissenschaftlich fundiert" (scientifically grounded) is THE selling keyword
- Frame somatic healing as neuroscience, meditation as cognitive training
- Cite research. Precise language. Long-form preferred.
- Avoid emotional/hype language — opposite of US approach

**Taiwan (zh-TW):**
- 身心靈 (body-mind-spirit) is THE discovery keyword
- Filial piety angle for parent-focused topics
- Academic pressure + tech overwork (Hsinchu Science Park) = high-demand topics

**China (zh-CN):**
- 内卷 (involution/rat race) coping content is a gap
- Douyin regulatory risk: "Buddhist lifestyle" accounts face removal
- ISBN required for domestic publication
- MCN agent required for mainland distribution

**France (fr-FR):**
- Philosophical/existentialist framing works uniquely well
- Government "Mon Soutien Psy" = institutional MH acceptance
- Never use aggressive marketing language — French readers distrust hard sells
- Bande dessinee tradition creates cultural comfort with sequential art

**Design:** Use `.rc` cards with flag emoji headers per market; collapsible accordion if adding to hub. Match dark theme. Each rule tagged with source doc.
**Data source:** marketing_deep_research/04_invisible_scripts.yaml; artifacts/research/therapeutic_manga_wellness_market_research_2026_04_04.md
**LOE:** 6-8 hours (6 markets × cultural protocol cards + content authoring).

---

## Improvement 4: Multi-Format Platform Playbooks (Podcast + Video + Manga)

**Priority:** P1
**Gap:** T2.8, T2.9, T2.10 — Operational guidance covers only ebook uploads
**Target page:** brand_admin.html Phase 2 and Phase 3

**Content to add:**

**Podcast section (source: PODCAST_PLATFORM_MARKETING_RESEARCH.md):**
- RSS submission checklist: Spotify for Podcasters, Apple Podcasts Connect, Google Podcasts
- Per-platform metadata requirements (cover art 3000×3000, episode descriptions, category selection)
- Weekly podcast schedule integration into Phase 3 day cards

**Video section (source: video_format_strategy_2026_04_06.md):**
- Platform specs table:
  - YouTube Long: 16:9, 1920×1080, up to 12h
  - YouTube Shorts: 9:16, 1080×1920, up to 3 min
  - TikTok: 9:16, 1080×1920, up to 10 min, hook in 1-2s
  - IG Reels: 9:16, 1080×1920, up to 3 min
  - Bilibili: 16:9, subtitles expected
  - Douyin: 9:16, big text overlays required
- Format recommendation: hybrid_nature_text_wave for YouTube long-form
- Shorts optimal: 15-35s, 85%+ completion rate

**Manga section (source: MANGA_GTM_PLAN.md):**
- Per-market platform upload:
  - WEBTOON Canvas: scroll vertical format, coin model
  - LINE Manga: 130M+ users, JP-specific
  - Piccoma: wait-or-pay freemium model
  - Kakao Page: Korean webtoon platform
  - Izneo: French manga distribution
- Reading direction note: R-to-L for JP manga, L-to-R for webtoon format

**Design:** Add new expandable cards in Phase 2 upload section following existing pattern (accordion + checklist + prefill). Add to Phase 3 weekly schedule (podcast on Wednesday, video on Friday, manga on Thursday).
**LOE:** 8-10 hours.

---

## Improvement 5: KPI Tracking and Escalation Paths

**Priority:** P1
**Gap:** T1.11, T1.12 — No KPI tracking or escalation documentation
**Target page:** brand_admin.html Phase 3 (Saturday "Review" day card)

**Content to add:**

**Weekly KPIs (Saturday Review checklist):**
```
Amazon KDP Dashboard:
  - Units sold this week          Track trend ↑↓
  - Page reads (KU)               Track trend ↑↓
  - Reviews added                 Target: 10+ within 90 days
  - Average rating                Target: 3.3+ minimum

Google Play Books:
  - Views → purchases             Conversion rate
  - Auto-narration plays          Track audio vs ebook ratio

YouTube Analytics:
  - Impressions → click-through   Target: 6-10% CTR
  - Average view duration         Target: 50%+ retention

Revenue:
  - Weekly total across platforms  Compare to last week
  - Highest-performing title       Double down candidate
  - Lowest-performing title        Kill candidate at 90 days
```

**Escalation Paths:**
```
Upload rejected → Check metadata against platform spec → Resubmit
  → If persists: Screenshot error, check platform TOS for AI disclosure

Review removed → Do NOT contact reviewer → Check Amazon review policy
  → If pattern: Check for review manipulation flags

Revenue drop >50% → Check if listing was suppressed/hidden
  → Verify metadata still correct → Check competitor pricing

Content package not received by Monday noon → Check delivery channel
  → Escalate to Pearl Prime ops
```

**Design:** Add to existing Saturday `.dy` card as expandable `.det` block. Use `.rc` cards for escalation paths with red/amber/green severity indicators.
**Data source:** Needs creation based on platform documentation + operational experience. Revenue thresholds from Spreadsheet: Top Brand Performance (decision framework).
**LOE:** 4-5 hours.

---

## Improvement 6: Search/Title Strategy Reference per Market

**Priority:** P1
**Gap:** T2.3, T2.4 — SEO keywords and title structure not surfaced
**Target page:** brand_onboarding_hub.html (expand Market Data tab or new tab)

**Content to add (source: search_behavior_title_strategy_research.md):**

**Universal Title Formula:**
```
Creative Title (2-5 words, ≤25 chars for thumbnail)
+ Keyword-Rich Subtitle (5-12 words, carries SEO)
= 37% ranking lift (Amazon A10)
Total: under 120 characters combined (Amazon limit: 200)
```

**Per-market title strategy:**
- US: Creative + keyword subtitle. BookTok shareability matters. Pain-state keywords ("can't sleep" > "sleep anxiety").
- Japan: Creative/paradoxical titles culturally accepted. Obi-style subtitle carries keywords. Short 2-4 word main.
- Korea: Emotional resonance wins — "healing essay" format dominates charts. Poetic > instructional.
- Germany: "Wissenschaftlich fundiert" + methodical subtitles ("Ein X-Schritte-Programm für...").
- China: 4-character compound titles (成語-style) are powerful. WeChat social discovery.

**High-volume keywords by topic (BookTok validated):**
- #anxietybooks: 200M+ views
- #nervoussystem: 2B+ views
- #ADHD: 60B+ views (most destigmatized)
- #impostersyndrome: 1.5B+ views

**Design:** Use `.ssg` stat cards for keyword volumes, `.rc` cards per market with flag headers.
**LOE:** 4-5 hours.

---

## Improvement 7: Deprecate Redundant Pages

**Priority:** P1
**Gap:** Redundancy — brand_admin_weekly_os.html and brand_admin_master_onboarding.html serve roles already covered
**Target pages:** 2 files to deprecate

**Action:**
1. **brand_admin_weekly_os.html** → Add deprecation banner at top redirecting to `brand_admin.html?phase=3`. Do not delete (existing links may reference it).
2. **brand_admin_master_onboarding.html** → Add deprecation banner redirecting to `brand_onboarding_hub.html`. Its "spine page" role is now served by the hub.

**Deprecation banner HTML:**
```html
<div style="padding:12px 20px; background:rgba(248,113,113,.1); border:1px solid rgba(248,113,113,.2); border-radius:8px; margin:16px; font-family:var(--mono); font-size:.8rem; color:#f87171; text-align:center">
  This page has moved. <a href="brand_admin.html?phase=3" style="color:#60a5fa; text-decoration:underline">Go to Brand Admin Weekly Operations →</a>
</div>
```

**LOE:** 30 minutes.

---

## Improvement 8: Brand Visual Identity Reference Panel

**Priority:** P2
**Gap:** T2.5 — Cover art guidelines and brand visual identity not surfaced
**Target page:** brand_onboarding_hub.html (expand Visual Identity tab)

**Content to add (source: config/catalog_planning/brand_identity_system.yaml):**

Per-brand visual identity cards showing:
- Brand name + teacher + tagline
- Colophon mark description
- 2 primary colors + 1 accent (rendered as CSS swatches)
- Display font + body font
- Cover template style
- Texture/pattern description

Start with the 13 teacher brands (first priority). Show first 4-5 on page load with "Show all 37" expand.

**Design:** Use existing `.vc` visual card grid pattern from the Visual Identity tab. Each card shows actual color swatches (not just hex codes). Font names rendered in their own typeface where possible.
**Data source:** config/catalog_planning/brand_identity_system.yaml (all 37 brands, complete visual specs).
**LOE:** 6-8 hours (37 brands × visual card rendering).

---

## Improvement 9: Marketing Dashboard Provenance + Heatmap Fix

**Priority:** P2
**Gap:** marketing_dashboard.html shows random-seeded heatmap as "Content Performance"
**Target page:** marketing_dashboard.html

**Content to fix:**

1. **Heatmap tab:** Replace random-seeded `HEATMAP_DATA` with honest labeling. Either:
   - Replace with actual data from config/authoring/ (topic × brand coverage matrix from catalog planning)
   - Or add prominent disclaimer: "Simulated data for planning purposes — not measured performance"

2. **Lane comparison tab:** Add provenance labels to Y1 revenue estimates:
   - en_US $180K: ASSUMPTION
   - ja_JP $95K: ASSUMPTION
   - etc.

3. **Ad spend simulator:** Add note: "All CPC/CPM/CTR values sourced from: advertising_roi_research.md (2026-04-05). Market conditions vary."

4. **Value ladder:** Label conversion rates as ASSUMPTION.

**Design:** Use `.prov` pill CSS from Improvement 1.
**LOE:** 3-4 hours.

---

## Improvement 10: Per-Market Briefing Pages (KR, TW, CN, DE, FR)

**Priority:** P2
**Gap:** Only US and JP have dedicated briefing pages; 5 other active markets lack them
**Target:** New briefing HTML pages following jp_brand_admin_v32_briefing.html pattern

**Markets needing briefings (in priority order):**
1. **ko-KR** — Korea: Naver/Kakao ecosystem, webtoon distribution, 힐링 culture, ppalli-ppalli content format
2. **zh-CN** — China: Ximalaya/WeChat/Douyin ecosystem, regulatory requirements, MCN agents, ISBN rules
3. **de-DE** — Germany: Evidence-based positioning, Audible DE, Thalia/Tolino, Waldbaden opportunity
4. **zh-TW** — Taiwan: Readmoo/KKBOX, 身心靈 framing, filial piety angles, academic pressure topics
5. **fr-FR** — France: Manga first-mover, philosophical framing, Izneo/Kobo FR, Prix unique book law

**Per briefing, include:**
- Market overview with sizing data (EXTERNAL labeled)
- Platform stack with upload instructions
- Cultural protocols (invisible scripts from research)
- V3.2 system adaptations per market
- Cold-start strategy per market
- Revenue projection (ASSUMPTION labeled)
- Navigate section linking back to hub

**Design:** Follow jp_brand_admin_v32_briefing.html structure exactly. Dark theme for all except potentially zh-TW (light theme consideration). Include native language subtitles using appropriate Google Fonts (Noto Sans KR, Noto Sans SC, Noto Sans TC).
**Data source:** Per-market sections in advertising_roi_research.md, global_format_market_research.md, therapeutic_manga_research.md; presenter.html narration scripts.
**LOE:** 15-20 hours per briefing (5 briefings = 75-100 hours total). Consider phased delivery.

---

## Special Section: Spreadsheet → HTML Translation

| Sheet | Show in HTML? | Which Page | How | Provenance Label |
|-------|--------------|------------|-----|-----------------|
| Data Provenance | YES (meta) | All metric pages | Provenance pills per metric | N/A (is the label system itself) |
| Executive Summary | YES (partial) | brand_onboarding_hub.html Mission tab | Metric cards (13 teachers, 24 brands, 15 topics) | MIXED: system facts REPO-BACKED, catalog size ESTIMATE |
| Monthly Revenue Ramp | YES (cautious) | marketing_dashboard.html | Line chart with heavy ASSUMPTION labeling | ALL ASSUMPTION |
| Unit Economics | YES (critical) | brand_onboarding_hub.html new "Economics" tab | Pricing table + platform rev share table + cost structure | MIXED per row |
| Brand Catalog (24) | Already partial | brand_admin.html picker | Enhance picker to show persona + pricing per brand | MOSTLY REPO-BACKED |
| Revenue by Cluster | YES (partial) | marketing_dashboard.html | Bar chart with cluster breakdown | MIXED |
| Top Brand Performance | YES (partial) | marketing_dashboard.html | Portfolio framework (double down / monitor / kill) | ALL ASSUMPTION |
| Platform Strategy | YES | brand_onboarding_hub.html + brand_admin.html | Platform comparison table with rev shares | MIXED |
| IP & Technology | Partial (already) | brand_onboarding_hub.html V3.2 Systems tab | Already covered — add provenance labels | REPO-BACKED |
| Market Sizing | YES (context) | marketing_dashboard.html Lane Comparison | TAM/SAM/SOM chart | MIXED: TAM EXTERNAL, SOM ASSUMPTION |
| 3-Year P&L | NO | Keep in spreadsheet only | Investor-facing; too complex for admin page | N/A |

---

## Implementation Priority Summary

| # | Improvement | Priority | LOE | Dependencies |
|---|-----------|----------|-----|-------------|
| 1 | Data provenance labels | P0 | 4-6h | None |
| 2 | Unit economics tab | P0 | 2-3h | None |
| 3 | Per-market invisible scripts | P0 | 6-8h | None |
| 4 | Multi-format playbooks | P1 | 8-10h | None |
| 5 | KPI tracking + escalation | P1 | 4-5h | None |
| 6 | Title/SEO strategy reference | P1 | 4-5h | None |
| 7 | Deprecate redundant pages | P1 | 30min | None |
| 8 | Brand visual identity panel | P2 | 6-8h | None |
| 9 | Dashboard provenance fix | P2 | 3-4h | Improvement 1 (CSS) |
| 10 | Per-market briefing pages | P2 | 75-100h | Improvement 3 (locale research) |

**Total P0:** 12-17 hours
**Total P1:** 17-21 hours
**Total P2:** 84-112 hours

All P0 and P1 items are independent and can be parallelized. P2 item 10 (market briefings) is the largest single effort and should be phased.

# Pearl Prime Manga/Illustrated Content -- Go-to-Market Plan

## Executive Summary

Phoenix Omega's Pearl Prime content pipeline (therapeutic audiobooks, 24 brands, 12 languages) can be adapted to manga/illustrated format using the existing AI manga pipeline (7-agent system). This GTM plan maps the path from content to platform distribution across 3 regional tiers.

The core thesis: **therapeutic manga is a blue ocean**. No competitor occupies this niche at scale on any major platform worldwide. Phoenix Omega's 2,160+ title catalog, EI v2 quality framework, and 12-language localization infrastructure create a defensible content moat.

---

## Market Opportunity

| Metric | Value |
|---|---|
| Global manga market (2025) | $19.35B |
| Global manga market (2031 projected) | $56.38B |
| Global manga CAGR | 19.52% |
| Webtoons market (2025) | $9.7B |
| Webtoons market (2033 projected) | $83.2B |
| Webtoons CAGR | 29.7% |
| US manga market (2025) | $1.68B |
| Digital share of consumption | 72.7% |

**Strategic Position:**
- "Therapeutic manga" does not exist as a commercial category on any platform
- Graphic Medicine movement validates demand but lacks commercial platform presence
- China's National Action Plan for Mental Health of Children (2025-2030) explicitly encourages therapeutic content for youth
- Phoenix Omega's 2,160+ title catalog provides massive content moat for adaptation

---

## Regional Tiers

### Tier 1: Asia-Pacific (Highest Revenue Potential)

#### China / Hong Kong / Singapore

- **Entry mechanism:** MCN agent (recommend Muser or Edovision)
- **Target platforms:** Ximalaya Kids (subscription), Kuaikan Manhua (per-chapter)
- **Content:** Therapeutic manga adapted for Minor Protection Law compliance
- **Languages:** zh-CN, zh-TW
- **Revenue model:** 50/50 exclusive splits -> approximately 45% effective after MCN commission + tax
- **Regulatory:** Pre-entry compliance review with TransAsia Lawyers
- **Timeline:** Q3 2026 MCN contract -> Q4 2026 first titles live
- **Key risk:** Censorship rejection. Mitigation: pre-compliance review removes supernatural/violence/romance content for under-14

#### Korea

- **Entry mechanism:** Naver Webtoon Canvas (free) -> pitch to Originals
- **Target platforms:** Naver Webtoon, Lezhin
- **Content:** Vertical-scroll therapeutic webtoons
- **Language:** ko-KR
- **Revenue model:** Ad-share (Canvas) -> revenue-share (Originals)
- **Timeline:** Q3 2026 Canvas launch -> Q1 2027 Originals pitch
- **Key opportunity:** Korean govt Translation Support Center launching 2025 may co-fund localization

#### Taiwan

- **Entry mechanism:** Naver Webtoon (LINE Webtoon), Comico
- **Language:** zh-TW
- **Priority:** Lower -- smaller market, Kakao pulled out
- **Timeline:** Q1 2027

---

### Tier 2: Americas (Highest Growth Rate)

#### US / Canada

- **Multi-platform strategy:** Webtoon Canvas + ComiXology/Kindle + Apple Books + Google Play
- **Content:** English therapeutic manga/illustrated books
- **Revenue model:** Kindle royalties (35-70%) + Webtoon ad-share + Apple/Google 70/30
- **EI v2 integration:** Use marketability scores to select highest-converting titles for manga adaptation
- **Timeline:** Q2 2026 first 10 titles on Kindle/Apple -> Q3 2026 Webtoon Canvas
- **Key advantage:** Lowest barrier to entry, highest per-unit margins

#### Brazil

- **Platforms:** Social Comics (partnership), Manga Plus (if Shueisha partnership possible), Webtoon PT-BR
- **Language:** pt-BR
- **Content:** Therapeutic manga localized for Brazilian market
- **Revenue model:** Social Comics subscription share + direct Kindle BR
- **KOCCA-style approach:** Partner with local conventions/communities
- **Timeline:** Q4 2026

#### Mexico / Latin America

- **Platforms:** Webtoon ES, Kindle ES, Tapas
- **Languages:** es-MX, es-419
- **Timeline:** Q1 2027
- **Key consideration:** Low ARPU; freemium model with premium upsell; focus on brand awareness first

---

### Tier 3: Europe (Established Manga Culture)

#### France

- **Context:** Largest EU manga market, 55% webtoon viewership growth 2025-2026
- **Platforms:** Izneo (European digital comics), Webtoon FR, Kindle FR
- **Language:** fr-FR
- **Timeline:** Q1 2027

#### Germany / UK / Spain

- **Platforms:** Kindle local, Webtoon local, Apple Books
- **Languages:** de-DE, en-GB, es-ES
- **Timeline:** Q2 2027

---

## EI v2 Marketing Integration

The go-to-market plan leverages EI v2's six quality dimensions to select and optimize content for manga adaptation:

| EI v2 Dimension | Minimum Threshold | GTM Application |
|---|---|---|
| Therapeutic Value | 0.60 | Only adapt titles scoring above therapeutic threshold -- ensures content integrity in visual format |
| Engagement (marketability) | -- | Prioritize highest-engagement titles for first wave -- maximize platform traction |
| Safety Compliance | 0.95 | Critical for China Minor Protection Law -- auto-gate unsafe content before adaptation |
| Emotional Coherence | -- | Ensures manga arc maintains emotional curve from source audiobook |
| Somatic Precision | -- | Visual panels must preserve somatic exercise fidelity -- custom QA gate |
| Listen Experience / TTS | -- | Adapt narration-heavy scenes to visual storytelling -- identify panels that need voice-over vs silent |

### Marketing Lexicon Integration

- Enable `marketing_sources.enabled: true` in ei_v2_config.yaml
- Use `invisible_script_alignment` for culturally-tuned marketing copy per region
- Deploy **consumer language** (not clinical) in all platform descriptions
- Per-platform metadata optimization (tags, categories, descriptions) using EI v2 engagement scores

---

## Content Adaptation Pipeline

```
1. TITLE SELECTION
   EI v2 scores -> top 20 titles per persona x thread

2. MANGA CONVERSION (7-Agent Pipeline)
   Director -> Visual Identity -> Story Architect -> Chapter Writer ->
   Visual -> Lettering/Layout -> QC

3. LOCALIZATION
   12-language pipeline, regional sensitivity review

4. PLATFORM FORMATTING
   Vertical scroll (webtoons) vs page-turn (Kindle/Apple) vs panel-based (Kuaikan)

5. UPLOAD & DISTRIBUTION
   Per-platform submission via MCN (China), Canvas/portal (Korea/US), KDP (Amazon)
```

### Format Requirements by Platform

| Platform Type | Format | Panel Layout | Resolution |
|---|---|---|---|
| Webtoon (Naver, Tapas) | Vertical scroll, single column | Long-strip panels | 800px wide |
| Kindle/Apple Books | Page-turn, traditional manga layout | Standard manga pages | 1600x2560px |
| Kuaikan Manhua | Panel-based, horizontal swipe | 3-5 panels per page | 720px wide |
| Ximalaya Kids | Illustrated audio companion | Key scene illustrations | 1080x1080px |

---

## Success Metrics (Year 1)

| Metric | Target |
|---|---|
| Titles adapted to manga format | 50 |
| Platforms live | 8+ |
| Regional markets entered | 6 (CN, KR, US, BR, FR, UK) |
| Monthly readers | 500K+ |
| Revenue (net after platform/MCN fees) | $120K-$240K |
| EI v2 safety compliance | 100% |
| Average therapeutic value score | >= 0.65 |
| Platform rejection rate | < 5% |

### Revenue Breakdown by Region (Year 1 Estimate)

| Region | Revenue Range | Primary Driver |
|---|---|---|
| China (via MCN) | $40K-$80K | Ximalaya Kids subscription + Kuaikan per-chapter |
| Korea | $10K-$25K | Naver Canvas ad-share (ramping) |
| US/Canada | $40K-$80K | Kindle royalties + Apple Books |
| Brazil | $10K-$20K | Social Comics + Kindle BR |
| France | $10K-$20K | Izneo + Kindle FR |
| UK/Germany/Spain | $10K-$15K | Kindle + Apple Books |

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| China censorship rejection | High | Pre-compliance review with Chinese law firm; remove all supernatural/violence/romance for under-14 content |
| Platform revenue lower than projected | Medium | Multi-platform strategy -- no single-platform dependency |
| Piracy (25%+ of webtoon traffic is unauthorized) | High | Watermarking, DMCA automation, priority for platforms with DRM |
| Low ARPU in LatAm | Medium | Freemium model with premium upsell; focus on brand awareness first |
| EI v2 safety false positives blocking content | Low | Manual override workflow with editorial review |
| MCN agent underperformance | Medium | 90-day performance review clause in MCN contract; backup agent identified |
| Kakao further retreat impacts distribution | Low | No Kakao dependency in plan; Naver + independent platforms only |

---

## Phased Timeline

```
Q2 2026  US/Canada launch (Kindle, Apple Books -- 10 titles)
Q3 2026  US Webtoon Canvas + Korea Naver Canvas + China MCN contract signed
Q4 2026  China first titles live (Ximalaya Kids, Kuaikan) + Brazil launch
Q1 2027  Korea Originals pitch + Taiwan + France + Mexico/LatAm
Q2 2027  Germany/UK/Spain + second wave (20 additional titles)
```

---

## Immediate Next Steps

1. **Select first 10 titles** using EI v2 engagement + therapeutic value scores
2. **Run manga pipeline** on selected titles (7-agent conversion)
3. **Set up Kindle Direct Publishing** account and upload first batch
4. **Engage MCN agent** for China market entry (TransAsia Lawyers for contract review)
5. **Register Naver Webtoon Canvas** creator account
6. **Commission platform-specific format adaptations** (vertical scroll + page-turn + panel-based)

---

*Plan authored March 2026 by Pearl_Marketing. Research inputs from Pearl_Research via DeepSeek, Rakuten AI, Google, Gemini, Claude.*

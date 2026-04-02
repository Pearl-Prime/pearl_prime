# Web Search Gap-Fill Research
## Source: Web searches (2026-03-23)
## Purpose: Fill data gaps from DeepSeek responses

---

## Taiwan (zh-TW) Market

### Platforms
- **Readmoo (讀墨)**: Established 2013. Taiwan's largest ebook store with 130,000+ volumes in Traditional Chinese. Offers both e-books and audiobooks. Caters to readers in Taiwan, Hong Kong, and Southeast Asia.
- **Kobo TW (Rakuten Kobo)**: Launched Kobo Plus in Taiwan (Feb 2024). Pricing:
  - Reading plan: **NT$199/month** (~USD 6.20)
  - Listening plan: **NT$199/month** (~USD 6.20)
  - Reading + Listening: **NT$259/month** (~USD 8.10)
  - 14-day free trial available
  - Access to 1.5M+ ebooks and 150K+ audiobooks
- **Books.com.tw (博客來)**: Launched BooksPad e-reader (Feb 2025), sold 10,000+ units in 3 months. Major retailer with e-book and potential audiobook offerings.
- **Amazon Kindle**: Selling Traditional Chinese e-books since 2019.

### Market Context
- APAC audiobook market expected to grow at 27.2% CAGR through 2031
- Taiwan e-reader market surging (2025 data)
- Traditional Chinese content produced primarily locally
- No censorship (unlike mainland China)
- Open platform access (no Great Firewall)
- Payment: credit cards, convenience store payment, LINE Pay — no WeChat Pay

---

## China (zh-CN) Market — Additional Data

### Ximalaya FM (喜马拉雅) — Updated Data
- **303 million MAU** (as of 2023)
- **2.9 million active content creators**
- Audiobooks = **75% of paid content** (children's content = 13%)
- Revenue streams: paid subscriptions, advertisements, live broadcasts
- Content strategy: PGC + PUGC + UGC
- **Acquired by Tencent Music for $2.4 billion** (June 2025) — now part of Tencent ecosystem
- User willingness to pay: two-thirds would pay **¥11-20/month** (USD 1.60-3.00)
- Q1 2025 SVIP ARPU: **RMB 11.4** (rose 7.5% YoY)

### ISBN Requirements
- Foreign publishers MUST have a **CSBN (China Standard Book Number)** — international ISBN not valid in China
- Must work through a **domestic Chinese publishing house** for local ISBN
- Manuscript must be submitted for content review
- Chinese ISBN application requires domestic partner

### Tax Rates
- VAT on digital content: **6%-13%** depending on product type
- Payments treated as labor remuneration: 20% standard deduction
- Monthly personal exemption: RMB 5,000
- Progressive tax rates: 3%-45%
- New digital platform tax reporting requirements effective June 2025

---

## Japan (ja-JP) Market — Platform Pricing

### Audible JP
- Subscription: **¥1,500/month** (~USD 10) for unlimited listening
- Unlimited model (differs from US credit system)
- Dominant player in Japan
- Celebrated 10 years in Japan market

### audiobook.jp
- Major local competitor to Audible
- "ListenJapan" also in market
- Subscription-based model

### Spotify JP
- Aggressively pushing audiobooks
- Included in Premium subscription
- Good algorithm for surfacing wellness/ambient content

### Creator Revenue Share (General)
- Authors typically earn **20-40%** from audiobook sales royalties
- ACX titles make up 31%+ of Audible catalog
- Specific Japan revenue share terms not publicly available

---

## South Korea (ko-KR) Market — Platform Details

### Major Platforms
- **Naver AudioClip (오디오클립)**: Market leader. Most extensive Korean-language audiobook database. Features lectures, language studies, web novels, audiobooks read by voice actors, authors, and celebrities.
- **Millie's Library (밀리의 서재)**: Major subscription-based reading/audiobook platform
- **Willa (윌라)**: Subscription-based audiobook platform with AI-powered speed narration. Won "self-development app of the year" award.
- **Storytel KR**: International player expanding in Korea
- **Kakao Page**: Primarily webtoons/web novels, with "wait-and-pay" model

### Market Dynamics
- Market valued at **over USD 150 million** (2024)
- High smartphone penetration drives mobile-first consumption
- Limited high-quality localized Korean content = opportunity
- Cultural preference for physical books being overcome by audio convenience
- Mergers and pricing wars reshaping content industry (2025)

---

## Wellness/Self-Help Audiobook Competitors (English-Language)

### Polyvagal / Vagus Nerve Audiobooks Already Published
- "Accessing the Healing Power of the Vagus Nerve" — Stanley Rosenberg (described as "bestselling guide")
- "Polyvagal Theory: The Ultimate Self-Help Guide to Activate the Vagus Nerve" — Stephen Mayer
- "Polyvagal Theory and Exercises" — Casey J. Bennett (2025)
- "The Nervous System Reset: Heal Trauma, Resolve Chronic Pain" — Martha N. Beck (2025)
- "The Only Vagus Nerve Exercises You'll Ever Need" — Elise Hart (2025)
- "Our Polyvagal World" — Dr. Stephen Porges

### Key Observation
- Multiple English-language polyvagal/vagus nerve audiobooks exist on Audible
- **No evidence found** of localized Asian-language versions of these titles
- This represents a significant first-mover opportunity in zh-TW, zh-CN, ja-JP, ko-KR markets
- The niche is established in English but unoccupied in Asian languages

---

## Trend Infrastructure for Asian Markets (User Request)

### Context
The user has an existing SerpApi-based trend scraping system for US market:
- 250 searches/month budget
- 10 personas × 15 topics = 150 cells
- Day-of-week rotation across 5 tiers
- consumer_language_by_topic.yaml (14 topics)
- invisible_scripts_by_persona_topic.yaml (140 entries)

### What's Needed for Asian Markets
The same infrastructure needs to be extended for all Asian locales, using:
- **DeepSeek** as a research/trend source for: zh-CN, zh-SG, zh-HK, ko-KR, zh-TW
- **Rakuten AI** as a research/trend source for: ja-JP, ko-KR, zh-TW
- Locale-specific consumer_language_by_topic.yaml files per market
- Locale-specific invisible_scripts per market
- Brand lane coverage across all markets

### Implementation Notes
- SerpApi supports regional search (country codes: JP, KR, TW, CN, SG, HK)
- Google Trends has regional data for all target markets
- Budget allocation needed: reserve Tier 5 searches for locale pilots (zh-TW, ja-JP first)
- Need locale-specific keyword configs in `config/trend_keywords/`

# Japan LINE Freebie-Funnel Market Research — 2026-04-29

**Author:** pearl_research
**Operator context:** 12 ja_JP wellness / self-help / iyashikei brands currently running a US-style 5-email Proof Loop on GoHighLevel; this report sizes a parallel Japan funnel built on **LINE Official Account (LINE OA)** instead of email.
**Scope window:** 2024–2026 data. Today is 2026-04-29.
**Source policy:** Every numeric claim is either cited at the end of its section or marked `[unverified — hypothesis]` inline. No paid LLM API calls, no paid research subscriptions.

---

## 0. Executive Framing (read first)

LINE is not a Japanese clone of email + SMS. It is the dominant 1-to-1 channel in Japan with effectively-saturated reach (97 M MAU in a country of 124 M, smartphone penetration 95.2 %), open-rate behaviour that rewards short cadence over long autoresponders, and a built-in payment, login, and mini-app surface (LINE Pay, LINE Login, LIFF / LINE MINI App) that lets a publisher build the entire freebie → trust → buy loop inside one app the reader already uses 60+ times a day. **The single biggest mental shift for the operator is this: LINE is not an email replacement, it is a CRM-grade messenger replacing both email and the sub-page of a website.** The Sunmark Publishing 本とTREE LINE OA, which crossed **1 million friends** by August 2024 and put a single LINE broadcast into Amazon Top 100, is not an outlier: it is what a publisher-grade LINE OA looks like when it stops being a coupon channel and becomes a reading-community surface.

The 5-email Proof Loop translates cleanly to LINE — but the cadence telescopes: E1 (immediate) and E2 (+24h) collapse into hour-0 + hour-12 step messages because the open-rate half-life on LINE is single-digit hours, not 24–48 hours. The 48-hour story-to-offer gap remains useful, but for governance reasons (LINE OA Terms of Service prohibit aggressive "dark-pattern" sales push), not deliverability reasons.

---

## 1. LINE Official Account — Product Reality (2026)

### 1.1 Pricing tiers (Japan, as of 2026-04)

LINE OA in Japan is sold in three tiers. Singapore / Indonesia / US can only buy the lowest tier ("Communication"); **Japan is one of the markets with the full ladder.**

| Plan | JPY / month | Free outbound messages / month | Add'l messages |
|---|---|---|---|
| Communication (コミュニケーション) | ¥0 | 200 | not available |
| Light (ライト) | ¥5,000 | 5,000 | not available |
| Standard (スタンダード) | ¥15,000 | 30,000 | ¥3 / msg up to +50,000, then graduated |

Two important caveats:

- **"1 message" = 1 broadcast unit per recipient.** A single broadcast to 10,000 friends with 3 message bubbles burns 30,000 messages. This is the structural cost driver of any LINE funnel and the reason almost every operator segments aggressively.
- **2026-10-01 pricing reform:** Standard plan additional-message pricing is being simplified from a multi-tier table into a two-tier table broken at 200,000 messages. Operators planning ≥10,000-friend audiences in Q4 2026 should re-model.

For 12 brands × ~5,000 friends/brand × Proof-Loop cadence (≈5 messages over 2 weeks = ~3 broadcasts/month with bubbles), per-brand burn is roughly 3 broadcasts × 3 bubbles × 5,000 friends = 45,000 msg/month → **Standard plan is the floor**, with overage at the top end. Twelve Standard accounts = ¥180,000/month base + per-brand overage `[unverified — hypothesis based on operator's stated friend ambitions]`.

### 1.2 Functional surface

LINE OA in 2026 ships with a feature set that is closer to HubSpot + a chat app than to Mailchimp.

- **Step messages (ステップ配信):** LINE's native drip mechanic. Trigger = friend-add or tag assignment. Steps fire at fixed offsets (minutes/hours/days) and can branch on tag, demographic, or response. **This is the direct analog of the operator's 5-email Proof Loop** and removes the need for an external orchestrator (no GHL parallel needed).
- **Keyword auto-reply (キーワード応答):** Free-text triggers — a reader who types `不眠` ("insomnia") can be branched into a sleep funnel automatically.
- **Rich menu (リッチメニュー):** The persistent bottom dock that occupies the bottom ~40% of the LINE chat window. **Specifications (2026):**
  - **Large layout:** 2500 × 1686 px, max 6 tappable cells (2 × 3 grid). Recommended for publisher / catalog use.
  - **Compact layout:** 2500 × 843 px, max 3 cells.
  - Via LINE OA Manager (no-code UI): up to 6 preset cells.
  - **Via Messaging API: up to 20 tappable areas per menu** — enough for a 12-brand multi-page rich menu with locale or topic filters.
  - File: JPEG/PNG, ≤1 MB.
- **Surveys (リサーチ):** Built-in survey unit, returns to friend's profile as tags.
- **Coupons (クーポン):** Native coupon object; not just a link — has redemption tracking.
- **Segmented broadcast (絞り込み配信):** Free segmentation by gender, age range, OS, region, and tag. Only Standard plan supports tag-based segmentation in full.
- **LINE Notify status:** **Sunset.** LINE Notify ended general service through 2025; the recommended migration path is the Messaging API with push notifications. Anyone still architecting on Notify in 2026 is on dead infrastructure.

### 1.3 LIFF / LINE MINI App

**LIFF (LINE Front-end Framework)** is LINE's web-app-inside-LINE framework. A LIFF view can:

- Read the user's LINE userId, displayName, language, statusMessage, profile picture without re-auth.
- Send messages on behalf of the user (with consent).
- Scan QR codes, share to a friend, share to VOOM, open a LINE Pay flow.
- Be packaged as a **LINE MINI App**, which gets surface area in LINE's Wallet / "Services" tab.

**2026 status:** LIFF is being rolled into the LINE MINI App brand. For the operator's funnel, LIFF is the right answer for any of these:
- Custom freebie picker ("choose your free chapter")
- In-LINE EPUB / PDF reader pane (legal — LIFF can host arbitrary HTML/JS)
- Quiz → segment-and-tag flow ("which of the 12 brands fits you?")
- LINE Pay one-tap purchase

Build cost for a basic LIFF app is small (any front-end dev with a LINE Developers account, a TLS-served URL, and ~1 day of work). The operator does **not** need to be on LINE MINI App's curated directory to launch — LIFF apps work from a LINE OA's rich menu, message bubble, or `liff.line.me/` URL.

### 1.4 LINE Login (OAuth 2.1 / OIDC)

Friend-add captures: LINE userId, displayName, profile image URL, language. **Email is not captured by friend-add.**

LINE Login (separately invoked, OAuth flow inside LIFF or web) captures, by scope:

- `profile` — displayName, userId, picture URL, statusMessage
- `openid` — ID token
- `email` — email address (**requires per-app permission application in LINE Developers Console**, not auto-granted)
- LINE Profile+ partner scopes — real_name, gender, birthdate (only for Profile+ partners)

**Operator implication:** if the operator wants email on top of the LINE userId — useful for cross-platform retargeting and as a hedge against a LINE policy change — they should request `email` scope at app setup. Birthdate, gender, and real_name are *not* available without a Profile+ partnership, which is gated by LINE business development.

### 1.5 LINE Pay merchant integration

Online merchants pay **no monthly or initial fee**. The historical published rate for LINE Pay terminal (physical POS) is **2.45% transaction + ¥1,500/mo terminal fee** (2018 disclosure, last public rate at search time). Online-only merchant transaction percentages are negotiated per-merchant and not publicly listed at a single rate `[unverified — current online rate]`. Settlement is monthly.

**Friction reality:** LINE Pay's market share in Japan QR-payment sits behind PayPay; for a digital-book funnel where the alternative is "tap to Amazon JP and use a credit card", LINE Pay is **a nice-to-have, not a must-have**. Recommend leading the buy step with Kindle / BookWalker affiliate redirects and offering LINE Pay only as a secondary route for direct-EPUB sales via LIFF.

### 1.6 LINE VOOM — the timeline-style surface

LINE VOOM is the short-video / image timeline that replaced the old "タイムライン" feature in 2021. By 2025 it has 68 M+ MAU and is integrated with Yahoo and Google search results for participating Creator-Program accounts. Posts to VOOM **do not count against the message-broadcast cap**, which makes VOOM the cheap content surface for the funnel: drop manga panels, ASMR breath-work clips, and book teaser cards into VOOM at high frequency, broadcast into the chat tab only on cadence days.

### 1.7 LINE Ads Platform (LAP) — ad surfaces and 2026 pricing snapshot

| Surface | Description | 2025 pricing benchmark |
|---|---|---|
| **Talk Head View** | Premium banner at the top of the chat tab. Reaches base of ~65 M unique users / day. | Reservation-buy. Multi-million yen day-rate `[unverified — exact 2026 day-rate]`. |
| **Smart Channel** | Top of friends list; small native unit. | CPM-based. Smart Channel MVP Full-Star unit launched 2025-11. |
| **LAP standard placements** | Talk list bottom, LINE NEWS, LINE Manga, LINE VOOM. | CPC ≈ ¥24+ (US$0.16+); CPM ≈ ¥100+ / 1,000 imp; CPV ¥50–75 / view; **CPF (Cost-Per-Friend) ≈ ¥75–¥300** depending on category and creative. |
| **Click-to-Message** | Ad → opens chat with OA. | CPM-bid + per-friend implicit. |

**2026-04-01 platform shift:** LINE Ads merged with Yahoo! JAPAN Display Ads into "**LINE Yahoo Ads Display Ads**" (one unified UI). Existing campaigns migrate. Practical effect for the operator: a single planning seat can buy across LINE chat surfaces and Yahoo's display network, which is meaningful for the 35–60 demographic that over-indexes on Yahoo.

### 1.8 LINE Manga as a separate ecosystem

LINE Manga is **not** a publisher's friend-add channel. It is a **distribution platform** with its own commission split and its own audience. Q1 2025 saw LINE Manga become Japan's #1 mobile app by revenue, edging Piccoma. Combined Piccoma + LINE Manga share is roughly 70% of digital comics:

- Piccoma 2024 revenue ≈ ¥480 B; share 36.6%
- LINE Manga 2024 revenue ≈ ¥435 B; share 32.3%
- Piccoma MAU ~12.5 M; LINE Manga MAU ~10.8 M

For the operator's **manga_partnership** track, "be on LINE Manga" is a separate go-to-market motion (commission split, editorial relationships). For the **digital_publishing** track, LINE Manga is irrelevant — the LINE OA is the pre-purchase funnel; the buy happens on Amazon JP / BookWalker / Kobo. Treat them as orthogonal motions.

**Sources (§1):**
- [LINE Messaging API pricing | LINE Developers](https://developers.line.biz/en/docs/messaging-api/pricing/)
- [【2026年最新】LINE公式アカウントの料金プランを解説 | Liny](https://line-sm.com/blog/line-official-2023-price-update/)
- [LINE公式アカウントの料金プラン | LY for Business](https://www.lycbiz.com/jp/service/line-official-account/plan/)
- [Rich menus overview | LINE Developers](https://developers.line.biz/en/docs/messaging-api/rich-menus-overview/)
- [LINE Notify to End in 2025 | ke2b](https://ke2b.com/en/line-notify-closing-alt/)
- [LIFF overview | LINE Developers](https://developers.line.biz/en/docs/liff/overview/)
- [LINE Login v2.1 reference | LINE Developers](https://developers.line.biz/en/reference/line-login/)
- [LINE Profile+ | LINE Developers](https://developers.line.biz/en/docs/partner-docs/line-profile-plus/)
- [LINE Pay Merchant 金流收費](https://pay.line.me/jp/intro/taxGuide?locale=en_US)
- [LINE Pay Terminal launch | LINE Corporation](https://www.linecorp.com/en/pr/news/en/2018/2428)
- [LINE VOOM organic discovery update | LINE](https://voom-creators.line.me/ja/newsroom/updatereach/)
- [Advertising on LINE in Japan: Complete Guide 2025 | ULPA](https://www.ulpa.jp/post/advertising-on-line-in-japan-a-complete-guide)
- [LINE Yahoo Ads 2026 Platform Integration | DM4A](https://www.digitalmarketingforasia.com/line-yahoo-ads-2026-platform-integration/)
- [LINE Smart Channel MVP Full Star Ad Sales Kit (Nov 2025)](https://vos.line-scdn.net/lbstw-static/images/uploads/download_files/f2aac31d941f9e7b27c9cb97afda0c1b/EN_LINE%20Smart%20Channel%20MVP%20Full%20Star%20Ad%20Sales%20Kit_20251112.pdf)
- [2025年Q1 アプリ収益 LINEマンガ1位 | Real Sound](https://realsound.jp/book/2025/04/post-2003072.html)
- [国内マンガ市場 アクションプラン | METI 2025-01](https://www.meti.go.jp/shingikai/mono_info_service/entertainment_creative/pdf/003_04_03.pdf)

---

## 2. Acquisition Cost Benchmarks (Japan, 2024–2026)

### 2.1 LINE friend-add CPA (CPF)

The headline benchmark for **wellness / lifestyle / beauty** category friend-add via LINE Ads (LAP) campaigns is approximately **¥300 / friend**, with a published floor of ~¥75 (the LAP minimum CPF rate sheet) and ceilings of ¥500–¥1,000 for premium-targeted, high-quality (i.e., not incentivized-coupon-driven) friends in narrow demographics.

For self-help / book-related categories, no clean public benchmark exists; **the wellness / lifestyle ¥300 figure is the closest available analog and is what the operator should plan against** `[unverified — direct self-help / digital-book CPF, no public benchmark found]`.

Real-world distribution of CPF on a single campaign typically follows:

- **Coupon-driven friend-add** (e.g., "free PDF chapter"): ¥150–¥250
- **Brand-driven friend-add** (no incentive): ¥400–¥800
- **Niche-targeted friend-add** (e.g., 35-49F interested in wellness): ¥300–¥500

For 12 brands × ~5,000 friends each = 60,000 friends to acquire, the CPF math at ¥300 = ¥18 M one-time (≈ US$120k) `[unverified — exact CPF will vary]`. This is a back-of-envelope ceiling and explains why publisher LINE OAs almost universally seed friends from owned channels (in-book QR codes, website pop-ups, existing email list cross-promotion) before scaling LAP buys.

### 2.2 Open-rate benchmarks: LINE vs. email vs. SMS in Japan

Multiple independent Japanese marketing-vendor surveys (2024–2026) converge on:

| Channel | Open rate | Click rate |
|---|---|---|
| LINE OA broadcast | **60–80%** typical, peak >80% in tight, opt-in lists | **~25–30%** average |
| Email (Japan B2C) | 10–22% (HubSpot's global avg ~43% does *not* apply to Japan; JP open rates are structurally lower) | ~3–6% |
| SMS (Japan) | ~80–90% open within minutes (delivery cost is the constraint, not open) | ~5–10% |

**Open-rate half-life on LINE in Japan:** ~20% of recipients open within minutes, ~50% within 3–6 hours, ~80% within the same day. For the operator's Proof Loop, **this means E1 (immediate) and E2 (+24h) should be redesigned as M1 (hour 0) + M2 (hour 6 or hour 12)**, not M2 (hour 24). At 24h, the message is competing with another day of LINE-friend chatter.

**Email open-rate ceiling in Japan is structurally lower than US.** Sawai Coffee published a case study where their email open rate was declining year-over-year while their LINE open rate sat at ~60% — a 20× gap. They moved their primary CRM channel to LINE.

### 2.3 Click-through to off-platform link

LINE → external link CTR in published case studies sits **~25–30%**, vs. ~3–6% for email. This is the multiplier that drives the LINE-vs-email decision more than open rate: a 3× open-rate gap becomes a **5–10× outbound click gap**.

### 2.4 Friend-add → first purchase

No clean public benchmark for digital-book publishers `[unverified — hypothesis from analogous categories below]`:

- Beauty/wellness e-comm friend-add → first purchase within 30 days: typically 3–8% (case studies; coupon-driven)
- Sunmark Publishing: 1 LINE broadcast → Amazon Top 100, implying a friend-base in the **5-figure-percent of friend list buying within hours of broadcast** (exact CVR not disclosed)
- Operator's Proof Loop conversion benchmark from email is a separate question; the email-to-LINE delta should be modeled at +30% to +50% for CVR based on the channel-CTR uplift `[unverified — hypothesis]`

**Sources (§2):**
- [Pulse Marketing — LINE Friends Campaigns for Wellness Brands](https://pulsemarketing.jp/insights/line-friends-campaigns-tips-for-beauty-wellness-brands/)
- [LINE Ads CPF Introduced | LINE Corp](https://www.linecorp.com/en/pr/news/en/2018/2063)
- [Advertising on LINE in Japan | ULPA](https://www.ulpa.jp/post/advertising-on-line-in-japan-a-complete-guide)
- [メルマガからLINEへ | netshop.impress 澤井珈琲・白鳩 case](https://netshop.impress.co.jp/node/10273)
- [LINE開封率 業界別ベンチマーク | Ligla](https://ligla.jp/blog/delivery/ctraverage/)
- [LINE公式アカウント 開封率 | mico](https://mico-inc.com/blog/line-message-open-rate/)
- [LINE開封率60%超え | MARKELINE](https://www.lstepoffcial.com/column/line-open-rate/)
- [Top CPA statistics 2025 | Amra & Elma](https://www.amraandelma.com/top-cost-per-acquisition-statistics/)

---

## 3. Comparable Funnels — Publisher / Wellness Creator LINE OAs (Inventory)

This section is the inventory; deep walkthroughs sit in Doc 2.

### 3.1 Self-help / business-book publishers

| Publisher | LINE OA | Approx. friends | Segment |
|---|---|---|---|
| サンマーク出版 (Sunmark) | 「本とTREE」 | **1,000,000+** (Aug 2024); 130k after year-1 | Self-help / wellness / mass-trade |
| ダイヤモンド社 (Diamond) | Dia-Online + book-specific OAs `[partial]` | Not publicly disclosed | Business / hardback self-help (publisher of 嫌われる勇気) |
| ディスカヴァー・トゥエンティワン (Discover 21) | OA exists; friend count not disclosed `[unverified]` | — | Business / self-improvement |
| フォレスト出版 (Forest Publishing) | `page.line.me/415oanmr` (confirmed live) | Not publicly disclosed; their *email* list sits at ~60,000 | Business / self-improvement / spiritual |
| KADOKAWA | Multiple — including BookWalker OA + imprint OAs | Not centrally disclosed | All-category incl. self-help (publisher of 反応しない練習) |
| 潮出版社 (Ushio) | `page.line.me/wxd3111q` (confirmed live) | — | Religious / spiritual / general |
| 集英社 (Shueisha) | Brand-LINE-collab acct (Seventeen, non-no) | ~1.89 M reach via fashion-mag accounts | Magazine / manga; relevant as cross-publisher LINE-collab pattern |
| 講談社 (Kodansha) | コミックDAYS app + manga title OAs | — | Manga, not direct LINE OA-led monetization (app subscription instead) |

### 3.2 Wellness / iyashikei comparables

| Creator / brand | LINE OA presence | Notes |
|---|---|---|
| こんまり / Marie Kondo (KMJ) | No publicly-discoverable JP LINE OA | Distribution is Instagram + YouTube + Netflix; lesson is *channel mix*, not a LINE walkthrough |
| 川野泰周 (Zen monk + psychiatrist, mindfulness author) | No dedicated LINE OA found `[unverified]` | Activity is via Engakuji blog and book sales — opportunity for the operator |
| 整える習慣 (Toshitaka Mogi) publisher OA | Not directly identifiable as a single OA `[unverified]` | Likely subsumed into Kobunsha or Shogakukan publisher OAs |
| LINEヘルスケア (LINE Healthcare official) | Health-counseling channel | Different vertical (telemedicine consultation), not a wellness-book funnel — but useful policy precedent on what LINE allows for "soft-medical" content |
| こころの耳 SNS相談 (MHLW) | LINE-based mental-health-consultation gov channel | Same — policy precedent that LINE permits anxiety/depression content with proper guardrails |

### 3.3 Manga publisher LINE OAs (separate motion)

The big-3 (Shueisha / Kodansha / KADOKAWA) primarily route manga monetization through **dedicated manga apps** (少年ジャンプ＋, ジャンプTOON, コミックDAYS, カドコミ) and through **LINE Manga as a distribution venue**, not through a LINE OA freebie funnel. Shueisha's "LINE Collaboration Account" tactic (placing branded content inside the *Seventeen* and *non-no* LINE OAs) is the relevant pattern — partner with an existing high-friend OA rather than building from zero.

**Sources (§3):**
- [Sunmark 本とTREE 100k breach | PR Times](https://prtimes.jp/main/html/rd/p/000000023.000045477.html)
- [Sunmark x Kaizen Platform 1M friends case study](https://kaizenplatform.com/case/sunmark)
- [Forest Publishing LINE OA](https://page.line.me/415oanmr)
- [Ushio Publishing LINE OA](https://page.line.me/wxd3111q)
- [Shueisha LINE collab account | Markezine](https://markezine.jp/article/detail/21043)
- [LINE-based mental health gov channel | MHLW kokoro.mhlw.go.jp](https://kokoro.mhlw.go.jp/sns-soudan/)

---

## 4. Payment + Book-Delivery Surfaces

### 4.1 Where Japanese self-help / wellness readers actually buy

| Storefront | Position | Audience fit for self-help/wellness | Affiliate program | Commission |
|---|---|---|---|---|
| **Amazon JP Kindle** | Largest single ebook share | Excellent — deepest catalog, strongest review surface for self-help | Amazon Associates Japan | Kindle books typically 4–8% category commission `[unverified — exact 2026 JP table]` |
| **BookWalker** (KADOKAWA) | #2–3, manga-strong, growing in light novels and self-help | Good — wide enough catalog; Kindle native readers may not have the BW app | Yes — **3% point-back** on Global store; JP store rates not publicly broken out | 3% (global) |
| **Apple Books JP** | Niche; iOS native | Mid — iOS-only, smaller catalog for JP self-help | No formal affiliate publisher program | n/a |
| **Rakuten Kobo** | Top-2 alongside Kindle in Japan | Good — Rakuten ecosystem cross-sells; Rakuten Points are a real conversion lever | Rakuten Affiliate (via Rakuten Affiliate / Rakuten Affiliate Network) | 2–4% typical `[unverified — current 2026 ebook rate]` |
| **honto** | Daimaru/Marubeni-backed; print + ebook hybrid | Mid — declining mindshare among under-40 readers | Yes (smaller scale) | `[unverified]` |
| **ebookjapan** (Yahoo) | Manga-leaning, also catalogues self-help | Mid for self-help; primary draw is manga discount campaigns | Yes via Yahoo affiliate | `[unverified]` |
| **Reader Store** (Sony) | Niche | Low for under-50 wellness readers | Limited | n/a |

**Operator implication:** the buy step in the LINE funnel should be a **2-button choice (Amazon JP Kindle OR BookWalker)** for the digital_publishing track. Adding more storefronts increases operator overhead (separate affiliate accounts, separate tracking) for negligible incremental conversion. Honto / Reader Store / ebookjapan only matter if a specific brand's reader cohort over-indexes there — for the operator's wellness/self-help catalog, the answer is Kindle dominance.

### 4.2 LINE Pay direct sale vs. affiliate redirect

| Path | Operator economics | Reader friction |
|---|---|---|
| Affiliate redirect to Amazon Kindle | 4–8% commission; lose customer-of-record to Amazon | Low — 1-tap if reader has Amazon JP account |
| Affiliate redirect to BookWalker | 3% commission; lose customer-of-record; KADOKAWA reader pool | Low if reader has BW account; medium otherwise |
| **Direct EPUB sale via LIFF + LINE Pay** | Keep ~95–97% of revenue (LINE Pay merchant fee + payment-processor cut); **own the customer record (LINE userId, email if scoped)** | Medium — requires reader to authorize LINE Pay; more steps than Amazon |

**Recommendation:** lead with affiliate redirect for cold/warm friends in the first 14 days. Layer in LIFF + LINE Pay direct-sale for repeat buyers and brand-loyal readers (the 3rd-purchase-and-up cohort). This matches what Sunmark does — affiliate-leaning for the first conversion, in-LIFF "本とTREE" experience for the long-term relationship.

### 4.3 Konbini payment

For self-help readers **35–55F** (a real cohort for the operator's anxiety / sleep / burnout brands), konbini cash payment (7-Eleven, FamilyMart, Lawson) still represents a non-trivial slice of payment preference. For physical books with ISBN it's mostly a non-issue (Amazon and Rakuten already accept konbini); for digital-only EPUB sales via LIFF, konbini integration adds 5–10 days of integration work via a payment aggregator (Stripe JP, Paymentwall, KOMOJU). **For phase 1, recommend skipping konbini and revisiting at scale** `[unverified — hypothesis on slice size]`.

### 4.4 Direct EPUB-to-LINE delivery via LIFF

**Legality:** legal. LIFF can host arbitrary HTML/JS, including a paginated EPUB reader. The operator must own or have license to distribute the EPUB. The same DRM-vs-no-DRM tradeoff applies as with any direct distribution.

**Feasibility:** straightforward. A LIFF EPUB reader is ~1–2 weeks of dev. The bigger question is operational: customer support, returns, refund handling, technical support for "the file won't open on my phone". Amazon and BookWalker handle that; the operator handling it themselves is the real cost.

**Sources (§4):**
- [Japan eBook market | Statista](https://www.statista.com/outlook/amo/media/books/ebooks/japan)
- [Tofugu — Practical Guide to Japanese E-books](https://www.tofugu.com/japanese/how-to-buy-japanese-ebooks/)
- [BookWalker Point Affiliate Program](https://global.bookwalker.jp/coin-affiliate/)
- [BookWalker Affiliate Rewards launch](https://global.bookwalker.jp/info-news_20191120/)
- [Stripe — Payment agent fees in Japan](https://stripe.com/resources/more/payment-agency-fees-japan)
- [Lightspark — Instant Payments Japan 2026](https://www.lightspark.com/knowledge/instant-payments-japan)

---

## 5. Compliance + Legal

### 5.1 特定商取引法 (Specified Commercial Transactions Act / SCTA)

If the operator sells **anything** to a Japanese consumer over the internet — including EPUB via LIFF / LINE Pay, including a LINE-stamp-bundle paid offer, including a LINE-coupon to an off-platform shop — they must publish a 特定商取引法に基づく表示 page covering:

- Operator legal entity name + representative
- Address (no PO-box-only)
- Phone, email
- Sale price (incl. tax) and shipping/delivery cost
- Payment method, payment timing, delivery timing (digital: "決済完了後直ちに" if instant)
- Returns / refunds policy (digital downloads: typically "デジタルコンテンツの性質上、返品はお受けできません" with a clear exception for product defect)

**LINE-specific:** LINE OA's coupon and shop functions, and any LIFF-hosted commerce, all count as internet sales — full SCTA disclosure applies. LINE provides a template page; the operator must publish one per legal entity.

### 5.2 個人情報保護法 (Personal Information Protection Act / APPI)

Friend-add automatically collects LINE userId + display name. Under APPI 2022-amendment + 2023 LINE-Yahoo merger update:

- **Privacy policy must be linked from the OA profile** before friend-add or, at minimum, at first message.
- Purpose of use (利用目的) must be specified — e.g., "新刊情報の配信", "お問い合わせ対応", "リターゲティング広告のためのデータ連携".
- For any data combining LINE-side ID with operator-side data (e.g., joining a LIFF-collected email to LINE userId), the privacy policy must call out cross-system identification.
- May 2025: LINE-Yahoo unified privacy policy; users can no longer defer consent. This affects the *consumer* not the *operator*, but it means every LINE friend the operator gains in 2025+ has clicked through the unified policy — a quiet baseline.
- For sensitive categories (要配慮個人情報) — health condition, mental health diagnosis, religion, criminal history — explicit opt-in is required. **The operator's anxiety / burnout / sleep-disorder content edges this line.** Any survey question of the form "Do you have insomnia?" should be framed as a self-classification, not a clinical claim, and the privacy policy should state that no medical data is being collected.

### 5.3 特定電子メール法 (Anti-Spam Act)

**Does not apply to LINE messages.** The Act regulates SMTP email and SMS (telephone-number-routed). LINE is an OTT messaging app and is out of scope. This is a quiet and large advantage of LINE over email for the operator: opt-out mechanics, footer requirements, and 同意の取得 record-keeping requirements that bite GHL email campaigns do not bite LINE OA broadcasts.

**Caveat:** the LINE OA Terms of Service and LINE OA Guidelines impose their own opt-out / cadence rules (see §5.4). The legal floor is lower; the platform-policy floor is real.

### 5.4 LINE OA Terms of Service / Guidelines — relevant edges

- **Cadence:** No hard daily/monthly cap beyond the message-count cost. But LINE Guidelines warn against "high-frequency / spam-like" pushes. Practical industry norm is 2–4 broadcasts per week max for a non-news brand. The operator's Proof Loop (~5 broadcasts in 2 weeks then steady-state) is well inside norms.
- **Prohibited categories — wellness-specific:**
  - **No medical efficacy claims** ("不眠が治る", "うつが消える") on health food, supplements, or services. Falls under 薬機法 (Pharmaceuticals and Medical Devices Act) and 景品表示法 (Premiums and Representations Act).
  - **For books**, summarizing the *content* of a book that itself makes claims is allowed (a book review can quote the author); but the OA's *own marketing copy* should describe the book as "悩みを軽くするヒント" not "うつが治る本".
  - **特定保健用食品 / 機能性表示食品 / 栄養機能食品** can claim within their registered scope. Generic supplements and "wellness products" cannot.
- **No illegal-good promotion, no adult content (18+ R-rated content has separate restrictions), no gambling promotion outside licensed operators.**
- **Opt-out via `block` is the user's right at any time.** A blocked friend stops counting toward broadcast targets but continues counting toward total friend acquisition.

### 5.5 Quick-reference checklist for the operator's funnel

- [ ] One 特定商取引法 page per legal entity that ever sells anything (EPUB via LIFF, LINE Pay, etc.)
- [ ] Privacy policy linked in OA profile, in welcome message, in every LIFF view that collects data
- [ ] Purpose-of-use enumerated incl. LINE-Yahoo data linkage if used
- [ ] No medical-efficacy language in book descriptions or OA copy
- [ ] All 12 brand OAs onboarded to LINE Yahoo Business Manager (mandatory for new JP OAs from 2025-06-25)
- [ ] Block-rate monitored (a block-rate >5% in the first week is a content/cadence problem)

**Sources (§5):**
- [LINE 特定商取引法に基づく表示 (LINE OA template)](https://terms2.line.me/official_account_JP_Act_commercial_transactions?lang=ja)
- [LINE公式アカウントガイドライン](https://terms2.line.me/official_account_guideline_jp)
- [LINE公式アカウント プライバシーポリシー設定 2025最新 | lme.jp](https://lme.jp/media/line/privacypolicy/)
- [LINE公式アカウントで取得できる個人情報 | Ligla](https://ligla.jp/blog/line-official/personalinformation/)
- [特定電子メール法とSMS/LINE | Accrete](https://www.accrete-inc.com/useful_information/20220622/)
- [LY for Business — 健康食品 広告審査](https://www.lycbiz.com/jp/service/line-ads/review/health-food/)
- [配信コンテンツに関する禁止事項 | LY for Business](https://www.lycbiz.com/jp/column/line-official-account/guideline/20240829/)
- [LINE-Yahoo unified privacy policy (May 2025) | SBAPP](https://sbapp.net/appnews/sns/line/privacypolicy-171754)

---

## 6. Demographic Fit

### 6.1 LINE penetration by age cohort (Japan, FY2023→2025 trajectory)

- **Overall MAU (2025):** 97 M — 78.6% of the entire Japanese population.
- **Among internet users:** 89.1% (effectively saturated).
- **20-somethings:** 99.5% (near-universal).
- **Older cohorts:** unusually well-penetrated by social-app standards. LINE is the only social app where 50–69 cohort penetration exceeds 80% `[unverified — exact 2025 figure for that cohort, derived from Statista penetration-by-age-group reporting]`.
- **Gender:** 53.3% F / 46.7% M.
- **Smartphone penetration in Japan:** 95.2%.

The asymmetric story is the older cohort: **TikTok, Instagram, X all underweight in the 50+ population by a large margin; LINE is the only digital channel where 55F readers are reachable at scale.** For self-help / wellness brands targeting that cohort, LINE is not a "nice channel" — it is the channel.

### 6.2 Self-help / wellness reader demographics in Japan

Synthesizing publicly-available bestseller data + Mynavi / Best Present rankings:

- **Self-help bestsellers** skew toward the 30–55 cohort, with female readership ~55–60% on the wellness/iyashikei shelf (anxiety, sleep, somatic), shifting toward male majority on the business-strategy / productivity shelf.
- **Aging readership** is real: hardback self-help retains a 50+ readership; ebook self-help skews younger (30–45).
- **Smartphone-first** for ebook self-help: nearly all reading happens on smartphone. E-ink (Kindle Paperwhite / Kobo) is a minority for self-help (more dominant in long-novel and light-novel categories).
- **Print preference** persists for *gift* and *desk-reference* books (e.g., 嫌われる勇気 is read on phone but bought as a paperback for the bookshelf).

### 6.3 Reading device preference for the wellness shelf

| Device | Share of self-help reading (estimate) | Notes |
|---|---|---|
| Smartphone | ~70–80% `[unverified — derived from JP ebook-format share data]` | Primary surface; LINE OA + LIFF native fit |
| E-ink | ~5–10% | Niche for self-help |
| Print | ~15–25% | Higher for older cohorts and gift purchases |

For the operator's funnel, the buyer is reading on smartphone, so the affiliate redirect should be a smartphone-rendered Amazon Kindle / BookWalker product page, not a desktop-optimized link.

### 6.4 Time-of-day messaging windows

Japan-wide LINE-active windows (2024–2025 vendor surveys):

| Window | Activity | Notes |
|---|---|---|
| 07:00–09:00 | Morning commute | High open-rate, but message has competition |
| 12:00–13:00 | Lunch break | High open-rate; good for short-form |
| 17:00–19:00 | Evening commute / cooking | High; food/lifestyle peak |
| 20:00–22:00 | Free time at home | **Highest open-rate for self-help / wellness content** — quiet, reflective state |

For BtoC retail/EC the 17:00–21:00 window dominates. **For the operator's wellness/self-help funnel, the recommendation is 20:00–21:30** — readers are post-dinner, kids in bed, scrolling LINE in bed or on the couch. This is the moment somatic / breathwork / sleep content lands. Friday-evening broadcasts are over-saturated; **Sunday 20:00 and Wednesday 21:00 are under-saturated windows** worth A/B testing `[unverified — recommendation, not benchmark]`.

**Sources (§6):**
- [Digital 2025: Japan | DataReportal](https://datareportal.com/reports/digital-2025-japan)
- [Japan LINE Users Statistics 2025 | The Global Statistics](https://www.theglobalstatistics.com/japan-line-users-statistics/)
- [LINE penetration rate by age group | Statista](https://www.statista.com/statistics/1077541/japan-line-penetration-rate-by-age-group/)
- [LINE penetration rate FY2015–2024 | Statista](https://www.statista.com/statistics/1337533/japan-line-penetration-rate/)
- [LINE user trends 2025 | TAMLO](https://tam-tamlo.com/en/307)
- [自己啓発本おすすめ40選 | Mynavi 2025](https://osusume.mynavi.jp/4490/)
- [LINE配信時間 業界別 | Ligla](https://ligla.jp/blog/delivery/besttime/)
- [LINE開封率を上げる時間帯 | lme.jp](https://lme.jp/media/know-how/timing/)

---

## 7. Headline Implications for the Funnel

Synthesis — what the above means for cadence, freebie format, monetization, and multi-brand orchestration.

1. **Telescope the Proof Loop in time.** E1+E2 collapse to M1 (immediate) + M2 (+6h or +12h). E3 (story) at +48–72h is correct. E4 (book) at +48h after E3 is correct. E5 (more books) at +168h is correct. The 5-step shape survives; the front-end gets compressed because LINE open-rate half-life is hours, not days.

2. **Send between 20:00 and 21:30 on Sun/Tue/Wed/Thu.** Avoid Friday evening (oversaturated) and Saturday morning (low-engagement on lifestyle content). For high-stakes broadcasts (E4 = the book offer), use 20:30 Tuesday or Wednesday `[unverified — A/B-test recommendation]`.

3. **Use LIFF for the freebie and the segmenter, not for the buy.** Phase-1 buy-step = affiliate redirect to Amazon JP Kindle (and BookWalker as a B-test). LIFF wins for: free chapter reader, "which brand fits you?" 3-question quiz that tags into one of the 12 brands, exercise pages with breath-pacing animations. LIFF + LINE Pay direct-sell is a phase-2 economics decision (own customer-of-record, capture more margin) and should not block phase-1 launch.

4. **Acquire friends from owned channels first; LAP CPF buy second.** In-book QR codes, GHL email-to-LINE migration, website pop-ups, brand X / Threads / Instagram cross-promo. Only after each brand has a 3,000–5,000-friend organic baseline should LAP buys at ¥300 CPF be turned on, and only with brand-fit incentives (not generic coupons that pull low-LTV friends).

5. **Multi-brand orchestration: 12 OAs, not 1.** Each ja_JP brand (静心社, 直見堂, 体知社, 氣根社, 今此処社, 羽と秤社, 素形堂, 鉄門社, 夜の設計社, 体記堂, 炎転社, 開心堂) gets its own LINE OA. Reasons: (a) each speaks to a topic — 鉄門社 ≠ 羽と秤社 reader; (b) friend-add CPA stays low when the brand promise is narrow; (c) 12 separate friend lists hedge against any single OA being throttled. The Standard plan is the floor for each, ¥180k/mo combined base. **Do not try to run 12 brands on one OA;** LINE segmentation is good enough but reader brand-trust and rich-menu space are not.

6. **Build a 14-cell rich-menu via Messaging API, not the 6-cell preset.** Twelve brand cells + a "book of the month" cell + an FAQ cell = 14 tappable areas, well within the 20-area API cap. Each brand cell deep-links to a brand-specific LIFF view or a brand-specific keyword auto-reply. (This is the multi-brand alternative to running 12 OAs — but it is *worse* than 12 OAs for the reasons above; keep this as plan B.)

7. **LINE Pay is phase-2.** Phase-1 economics: 4–8% Amazon Associates JP commission on the book, with the operator's catalog being the upsell/cross-sell-driver, not the immediate revenue-line-item. Operator's revenue model is reader → friend → buyer → 3rd+ purchase reader, where the 3rd+ purchase reader gets routed to a LIFF + LINE Pay direct-sale flow that captures 95% of revenue. **Don't build phase-2 until phase-1 has a 3,000-friend OA driving any sales at all.**

8. **Compliance baseline for wellness content:** No medical-efficacy claims. Frame all books as "悩みを軽くするヒント" / "夜の落ち着きを取り戻すための物語" — not as therapeutic claims. Privacy policy linked from each OA profile + welcome message + every LIFF data-collection point. One 特定商取引法 page per selling legal entity. APPI sensitive-data care for any "do you have anxiety / insomnia / depression" question (frame as self-classification, not health data).

9. **VOOM is the cheap content surface.** Manga panels, breath-work loops, book teaser cards — all to VOOM at high frequency (3–5/week per brand). Chat-tab broadcasts at 2–3/week per brand. The VOOM-search-integration (Yahoo, Google) gives the manga panels organic SEO surface that owned blog content does not get.

10. **Hedge channel risk.** LINE-Yahoo merger, the 2026-04 ad-platform integration, and the 2026-10 pricing reform all create a single point of failure if the operator becomes 100% LINE-dependent. Maintain the email Proof Loop in parallel for at least the first 12 months; capture email via LIFF + LINE Login `email` scope so every LINE friend is also a recoverable email contact. **The right framing is LINE-primary, email-archive — not LINE-only.**

---

## Appendix A — Open Questions for Phase 2

These are questions the operator should answer before scaling beyond a pilot OA:

- **Empirical CPF for "wellness book reader" segment in 2026:** publicly the closest analog is ¥300; the operator's actual CPF in narrow-targeted Tier-1 brand campaigns may be ¥500–¥1,200. Run a 2-week LAP test with a ¥500k cap on the lowest-friction brand (likely 夜の設計社 — sleep, broadest appeal) before sizing the 12-brand spend.
- **Exact 2026 Amazon Associates JP commission table for Kindle books:** public sources are out-of-date. Confirm directly via the operator's Amazon Associates JP dashboard.
- **BookWalker JP affiliate rate:** the published 3% is for the global store. JP-store rate may differ. Confirm via BW partner contact.
- **Sunmark 1M-friends acquisition path:** the case-study disclosure does not break down friend acquisition by source. The operator should reach out for industry-event-level disclosure or run their own tests assuming 30% LAP buy / 30% in-book QR / 30% email migration / 10% organic VOOM `[unverified — hypothesis on Sunmark mix]`.
- **Block-rate targets for wellness OAs:** no public benchmark. Operator should set a 5% ceiling for the first 30 days post-friend-add and treat anything higher as a content-fit problem.

---

*End of Doc 1.*

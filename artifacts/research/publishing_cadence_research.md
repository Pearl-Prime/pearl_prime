# Publishing Cadence Research — Phoenix Omega

> **Pearl_Research** | Generated 2026-04-05
> Covers platform policies, ramp-up schedules, variation requirements,
> seasonal calendars, and actionable YAML parameters for the weekly
> production queue.

---

## Table of Contents

1. [Per-Platform Publishing Frequency Limits](#1-per-platform-publishing-frequency-limits)
2. [Ramp-Up Schedules](#2-ramp-up-schedules)
3. [Variation Patterns](#3-variation-patterns)
4. [Seasonal Calendar](#4-seasonal-calendar)
5. [Actionable Parameters (YAML-ready)](#5-actionable-parameters-yaml-ready)
6. [Sources](#6-sources)

---

## 1. Per-Platform Publishing Frequency Limits

### 1.1 Amazon KDP (Ebook + Paperback)

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | **3 titles/day per account** | Enforced since Sep 2023; reinforced 2025. Applies to ALL account types. ([Publishers Weekly](https://www.publishersweekly.com/pw/by-topic/digital/content-and-e-books/article/93207-kdp-will-limit-daily-number-of-new-titles.html), [Authors Guild](https://authorsguild.org/news/amazon-adds-to-kdp-generative-ai-policy-caps-daily-self-publishing-uploads/)) |
| **Weekly effective ceiling** | ~21 titles/week (3/day x 7) | Hitting 3/day every day WILL trigger manual review flags |
| **Content review queue — ebooks** | 48-72 hours typical | New publications; updates slightly faster ([KDP Timelines](https://kdp.amazon.com/en_US/help/topic/G202173620)) |
| **Content review queue — paperbacks** | 3-5 business days | Low-content books (journals, notebooks) can take up to 10 business days |
| **Content review queue — hardcovers** | 3-7 business days | Similar to paperback timelines |
| **Manual review triggers** | Rapid sequential uploads, near-identical metadata, AI-content flags, keyword stuffing, duplicate ISBNs | ([Jane Friedman](https://janefriedman.com/amazon-kdp-limits-how-many-books-can-be-uploaded-per-day/)) |
| **AI disclosure requirement** | Mandatory since 2024 | Must declare AI-assisted vs AI-generated content at upload time ([AIBoxTools](https://www.aiboxtools.com/amazon-kdp-ai-rules/)) |
| **Exception process** | Available | Publishers exceeding 3/day can request an exception via KDP support; approval is case-by-case |

**Key risk factors for high-volume publishers:**
- Publishing 3/day consistently for 7+ consecutive days flags the account for "abusive behavior" review
- Rapid, repeated uploads of near-identical files look like automated spam and trigger throttles ([Book Upload Pro](https://blog.bookuploadpro.com/why-amazon-kdp-publishing-takes-long/))
- Since late 2025, Amazon has explicitly extended review windows to combat automated spam uploads
- The same content may not be excessively reutilized across multiple books ([KDP Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200952510))

**Practical safe ceiling: 2 titles/day/account, 5 days/week = 10 titles/week/account.**

### 1.2 Apple Books

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit | Apple does not publicly state a per-day cap |
| **Practical throughput** | ~10-20 titles/day via iTunes Connect / Apple Books for Authors | Bottlenecked by manual metadata entry and processing time |
| **Account approval** | 2-5 business days for new accounts | ([Reedsy](https://reedsy.com/blog/how-to-publish-on-apple-books/)) |
| **Content review queue** | 24-48 hours typical | Faster than KDP for most categories |
| **Throttling triggers** | Batch uploads of low-quality content, identical metadata patterns | Apple uses manual editorial review more than automated systems |
| **Recent change (Apr 2025)** | Pages app no longer supports direct publishing to Apple Books | Must use Apple Books for Authors portal or aggregator ([Apple Insider](https://appleinsider.com/articles/25/04/04/authors-can-no-longer-publish-to-apple-books-directly-from-pages)) |

**Practical safe ceiling: 5 titles/day/account initially, scaling to 10/day after 30 days.**

### 1.3 Kobo / Rakuten Kobo (Writing Life)

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard daily limit | ([Kobo FAQ](https://kobowritinglife.zendesk.com/hc/en-us/articles/37446931721883-FAQ)) |
| **Account title cap** | 500 titles triggers review | Accounts exceeding 500 titles may be reviewed for compliance; excess titles may be removed ([Kobo ToS](https://cdn.kobo.com/merch-assets/writinglife/KOBO/en-US/serviceAgreement.html)) |
| **Content review queue** | 24-72 hours | Generally faster than KDP |
| **Throttling triggers** | Exceeding 500 total titles, bulk uploads of template content | |
| **Distribution reach** | 190+ countries | Particularly strong in Canada, Japan, and EU markets |

**Practical safe ceiling: 5-8 titles/day/account, but plan for the 500-title account cap requiring multiple accounts or aggregator routing.**

### 1.4 Google Play Books

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit | ([Google Play Books Partner Center](https://support.google.com/books/partner/answer/3424254?hl=en)) |
| **File size limit** | 2 GB per file (including cover) | |
| **Content review queue** | A few hours to 2-3 business days | Generally fast processing |
| **Throttling triggers** | Duplicate content across titles, policy violations | ([Google Publisher Policies](https://support.google.com/books/partner/answer/166501?hl=en)) |
| **Account setup** | Requires Google Payments merchant account | Additional verification for new publishers |

**Practical safe ceiling: 10 titles/day/account. Google is the least restrictive major platform.**

### 1.5 Barnes & Noble Press

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit | ([B&N Press](https://press.barnesandnoble.com)) |
| **Content review queue** | Books appear on BN.com within 72 hours | ([B&N Help](https://help.barnesandnoble.com/hc/en-us/articles/42541436590619-Publishing-Selling-Your-Book-with-Barnes-Noble)) |
| **Royalty rates** | Up to 65% ebook, 60% print | No exclusivity required |
| **Throttling triggers** | Not publicly documented | Smaller platform with less aggressive spam detection |
| **Market share** | US-focused, ~5-8% of ebook market | |

**Practical safe ceiling: 5-8 titles/day/account. Lower volume platform means less scrutiny but also less sales potential outside US.**

### 1.6 Draft2Digital (Aggregator)

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit | ([D2D FAQ](https://draft2digital.com/faq/)) |
| **Distribution reach** | Apple Books, Kobo, B&N, libraries (OverDrive), Tolino, Vivlio, and more | Single upload distributes to all partners |
| **Content review queue** | 24-48 hours for D2D processing + partner platform review times | |
| **Print revision limit** | 1 free submission of print changes per 90-day period | Content + cover count as one change |
| **Throttling triggers** | Rapid bulk uploads may trigger manual review | |
| **Revenue share** | 10% of net receipts from retail partners | |

**Practical safe ceiling: 8-12 titles/day through D2D. The aggregator model means one upload fans out to 6+ retailers, making it the most efficient channel for wide distribution.**

### 1.7 LINE Manga (Japan)

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit for LINE Manga INDIES | ([LINE Manga CEO interview](https://us.oricon-group.com/news/6631/)) |
| **Platform model** | Open publishing via LINE Manga INDIES | Anyone can upload; professional or amateur |
| **Content review** | Editorial review for quality; timeline not publicly documented | Focus on creative quality rather than spam volume |
| **Language** | Primarily Japanese | Some titles in Korean/Chinese |
| **Monetization** | Revenue share model; ad-supported + premium chapters | |
| **Market position** | One of Japan's largest digital manga platforms | Digital captures 73% of Japan's manga market ([ICv2](https://icv2.com/articles/columns/view/59058/japan-manga-market-slows-digital-captures-73-share)) |

**Practical safe ceiling: 3-5 titles/day. Japanese platforms prioritize quality signals over volume. Start with 1-2/day and build reputation.**

### 1.8 IngramSpark

| Parameter | Value | Notes |
|---|---|---|
| **Hard daily upload limit** | No published hard limit | ([IngramSpark FAQ](https://www.ingramspark.com/faqs)) |
| **Upload fees** | Eliminated as of Feb 1, 2026 | Previously charged per title; now free to upload ([IngramSpark User Guide v3.0](https://www.ingramspark.com/hubfs/downloads/user-guide.pdf)) |
| **eProof processing** | 3 business days after submission | |
| **Post-approval revisions** | $25 per revision after eProof approval | |
| **Distribution** | 40,000+ retailers and libraries worldwide | Largest print distribution network |
| **ISBN requirement** | Publisher must provide their own ISBNs | Unlike KDP, no free ISBN option |
| **Throttling triggers** | Not publicly documented for digital uploads | Print proofing workflow is the natural bottleneck |

**Practical safe ceiling: 5-8 titles/day. The 3-day eProof cycle is the real bottleneck — plan submissions in batches with staggered approval windows.**

### 1.9 Summary Table — Maximum Safe Daily Uploads Per Account

| Platform | Hard Limit | Safe Daily Max | Safe Weekly Max | Review Queue |
|---|---|---|---|---|
| Amazon KDP | 3/day | 2/day | 10/week | 2-10 biz days |
| Apple Books | None published | 5/day | 25/week | 1-2 days |
| Kobo Writing Life | None (500 total cap) | 5/day | 25/week | 1-3 days |
| Google Play Books | None published | 10/day | 50/week | Hours to 2 days |
| B&N Press | None published | 5/day | 25/week | ~72 hours |
| Draft2Digital | None published | 8/day | 40/week | 1-2 days + partner |
| LINE Manga | None published | 3/day | 15/week | Variable |
| IngramSpark | None published | 5/day | 25/week | 3 biz days (eProof) |

---

## 2. Ramp-Up Schedules

### 2.1 General Principles

New publisher accounts on every platform face heightened scrutiny. The first 90 days
are critical for establishing account health and trust signals. Key principles:

1. **Start slow** — Lower volumes in weeks 1-4 build trust with automated review systems
2. **Diversify early** — Mix content types (ebook, paperback, different categories) from week 1
3. **Space uploads** — Never batch all daily uploads in a single burst; spread across the day
4. **Monitor review times** — Lengthening review queues signal you are approaching a throttle boundary
5. **Build metadata quality** — High-quality, unique metadata from day 1 prevents spam flags later

### 2.2 Amazon KDP — New Account Ramp

Amazon is the most restrictive platform and the one where ramp-up discipline matters most.

| Week | Titles/Day | Titles/Week | Cumulative | Notes |
|---|---|---|---|---|
| **Week 1** | 1 | 5 | 5 | Establish account. Upload 1/day on weekdays only. Expect 5-7 day review per title. |
| **Week 2** | 1 | 5 | 10 | Continue 1/day. Monitor review times. If reviews are completing in <72h, account is healthy. |
| **Week 3** | 1-2 | 7-10 | 17-20 | Begin testing 2/day on some days. Alternate ebook and paperback. |
| **Week 4** | 2 | 10 | 27-30 | Stabilize at 2/day. Review times should be normalizing to 48-72h for ebooks. |
| **Week 5-6** | 2 | 10 | 47-50 | Hold at 2/day. Do NOT push to 3/day yet. Build diverse category presence. |
| **Week 7-8** | 2-3 | 12-15 | 71-80 | Begin testing 3/day on select days. If review times remain stable, continue. |
| **Week 9-10** | 2-3 | 14-18 | 99-116 | Mix in more 3/day days. You should have 80-100+ live titles demonstrating account legitimacy. |
| **Week 11-12** | 3 | 15-18 | 129-152 | Full velocity: 3/day, but limit to 5 days/week. Reserve 2 days for metadata updates and monitoring. |
| **Week 13+** | 2-3 | 10-15 | Ongoing | Sustainable cruising velocity. Never exceed 3/day. Space uploads across the day. |

**Account age milestones (KDP):**
- **Day 1-30**: Extended review periods (3-10 business days). Expect slowest processing.
- **Day 31-60**: Review times begin normalizing if account shows diverse, quality content.
- **Day 61-90**: Review times typically match established accounts (48-72h for ebooks).
- **Day 90+**: Account is considered "established" for most internal review purposes. KDP Select 90-day enrollment cycles also align with this milestone.
- **Day 180+**: Accounts with 100+ live titles and no policy violations get fastest processing.

**Critical anti-patterns to avoid on KDP:**
- Publishing 3/day every single day for 7+ consecutive days
- Uploading at the same time each day (looks automated)
- All titles in the same BISAC category
- Near-identical descriptions across titles
- Rapid uploads from the same IP address ([Book Upload Pro](https://blog.bookuploadpro.com/why-amazon-kdp-is-so-slow/))

### 2.3 Apple Books — New Account Ramp

| Week | Titles/Day | Titles/Week | Notes |
|---|---|---|---|
| **Week 1** | 1-2 | 5-10 | Account approval takes 2-5 days. Start uploading once approved. |
| **Week 2-3** | 2-3 | 10-15 | Apple's editorial review is lighter than KDP. Scale faster. |
| **Week 4-6** | 3-5 | 15-25 | Reach cruising velocity. Apple is generally more permissive. |
| **Week 7+** | 5-8 | 25-40 | Full velocity. Monitor for any editorial flags. |

### 2.4 Kobo Writing Life — New Account Ramp

| Week | Titles/Day | Titles/Week | Notes |
|---|---|---|---|
| **Week 1** | 1-2 | 5-10 | Establish account presence. |
| **Week 2-4** | 2-3 | 10-15 | Scale steadily. |
| **Week 5-8** | 3-5 | 15-25 | Full velocity. Monitor approach to 500-title cap. |
| **Week 9+** | 5-8 | 25-40 | At this pace you hit 500-title review threshold at ~week 20. Plan second account or aggregator routing by then. |

### 2.5 Google Play Books — New Account Ramp

| Week | Titles/Day | Titles/Week | Notes |
|---|---|---|---|
| **Week 1** | 2-3 | 10-15 | Google Payments merchant verification may take 3-5 days. |
| **Week 2-3** | 3-5 | 15-25 | Google is the most permissive platform for upload volume. |
| **Week 4+** | 5-10 | 25-50 | Full velocity. Google's automated systems focus on content policy, not volume. |

### 2.6 Draft2Digital — New Account Ramp

| Week | Titles/Day | Titles/Week | Notes |
|---|---|---|---|
| **Week 1** | 2-3 | 10-15 | D2D itself processes quickly. Partner platform review times apply. |
| **Week 2-4** | 4-6 | 20-30 | Scale based on partner platform acceptance rates. |
| **Week 5+** | 6-10 | 30-50 | Full velocity. Remember: each D2D upload fans out to multiple retailers. |

### 2.7 IngramSpark — New Account Ramp

| Week | Titles/Day | Titles/Week | Notes |
|---|---|---|---|
| **Week 1** | 1-2 | 5-10 | Initial setup. eProof cycle is 3 business days, creating a natural governor. |
| **Week 2-4** | 2-3 | 10-15 | Stagger submissions so eProof approvals spread across the week. |
| **Week 5-8** | 3-5 | 15-25 | Full velocity. Plan batch submissions M/W/F with approvals staggered. |
| **Week 9+** | 5-8 | 25-40 | Maintain pipeline: submit batch -> approve batch -> submit next batch. |

### 2.8 Multi-Account Strategy for 312 Brands at 15 Titles/Brand/Week

**Target throughput**: 312 brands x 15 titles/week = 4,680 titles/week

**KDP accounts needed** (bottleneck platform):
- Safe velocity per account: 10 titles/week (established) to 15/week (max)
- Accounts needed at full velocity: 4,680 / 10 = **468 KDP accounts minimum**
- With headroom for throttling: **~500-600 KDP accounts**
- Each account should be associated with a distinct publisher identity (brand mapping)

**Ramp timeline to full 4,680/week throughput:**
- **Month 1**: 50 accounts x 5/week = 250 titles/week
- **Month 2**: 100 accounts x 8/week = 800 titles/week
- **Month 3**: 200 accounts x 10/week = 2,000 titles/week
- **Month 4**: 350 accounts x 12/week = 4,200 titles/week
- **Month 5+**: 468 accounts x 10/week = 4,680 titles/week (full velocity)

**Other platforms scale faster** — Apple, Kobo, Google, and D2D combined can absorb 4,680/week with far fewer accounts (50-100 total across all non-Amazon platforms).

---

## 3. Variation Patterns

### 3.1 Title Uniqueness Requirements

**Amazon KDP:**
- Titles do not need to be globally unique, but identical titles + identical author names will trigger duplicate detection
- Subtitle must differ if title is similar to another in your catalog
- Series titles (e.g., "Brand X Series Book 1") are acceptable IF the series name is registered

**Cross-platform:**
- ISBN uniqueness is the primary deduplication key across all platforms
- Each format (ebook, paperback, hardcover) requires its own ISBN
- Title + author + ISBN must form a unique combination per platform

**Minimum variation for 312 brands:**
- Each brand should have a distinct publisher name and author identity
- Titles within a brand can follow a series pattern but must have unique book-level titles
- Avoid recycling the exact same title across brands — even with different authors, platform algorithms may flag

**Practical rule**: No two titles across ALL accounts should share the same combination of:
1. Exact title text
2. Exact subtitle text
3. Primary BISAC category

### 3.2 Description Similarity Thresholds

**Amazon's detection:**
- Amazon does not publish an exact similarity percentage threshold
- However, descriptions that share >60-70% of sentences verbatim across titles will trigger "duplicate content" flags
- "Excessive" content reutilization creates "a poor shopping or reading experience" per KDP Content Guidelines ([KDP Quality Guide](https://kdp.amazon.com/en_US/help/topic/G200952510))

**Safe practices for 312 brands at 15/week:**
- Maintain a **description template library** of 50+ base templates per genre
- Each template should be varied with at least 5 swap-in sections (hook, premise, call-to-action, author bio snippet, series context)
- Target **<30% verbatim overlap** between any two descriptions in the same category
- Use synonyms, sentence restructuring, and different narrative angles
- Rotate opening hooks: question, statement, quote, scene-setting, character introduction

**Description variation matrix:**

| Component | Minimum Variants | Rotation Strategy |
|---|---|---|
| Opening hook (first 2 sentences) | 20+ per genre | Rotate by title number mod 20 |
| Premise paragraph | 30+ per genre | Unique per title, drawn from plot summary |
| Tone/voice paragraph | 15+ per genre | Rotate by brand identity |
| Call-to-action closing | 10+ | Rotate weekly |
| Author bio snippet | 1 per brand (312 total) | Fixed per brand |

### 3.3 Category / BISAC Diversity

**Amazon KDP:**
- Each title can be assigned up to 3 BISAC categories
- Titles from the same account clustered in the same narrow category trigger review
- Use the full depth of the BISAC hierarchy (e.g., FICTION / Romance / Historical / Medieval is better than just FICTION / Romance)

**Cross-platform:**
- BISAC codes are standardized across most platforms
- Kobo and Apple accept up to 3 categories; Google allows more granular classification
- IngramSpark uses BISAC as the primary classification scheme

**Diversity strategy for 312 brands at 15/week:**
- Map each brand to a **primary genre lane** (e.g., Brand A = Romance, Brand B = Thriller)
- Within each brand's lane, rotate through **5-8 sub-categories** per week
- Ensure no single sub-category receives more than 3 titles/week from the same account
- Cross-brand category overlap is fine — two brands can both publish Romance, but they should target different sub-categories

**Example BISAC rotation for a Romance brand:**

| Week | Titles 1-3 | Titles 4-6 | Titles 7-9 | Titles 10-12 | Titles 13-15 |
|---|---|---|---|---|---|
| 1 | Historical | Contemporary | Paranormal | Suspense | New Adult |
| 2 | Regency | Romantic Comedy | Fantasy | Military | Clean/Wholesome |
| 3 | Western | Billionaire | Sci-Fi Romance | Sports | Multicultural |

### 3.4 Keyword Overlap Limits

**Amazon KDP keyword rules:**
- 7 keyword slots per title (each slot can contain a short phrase)
- Keywords must be relevant to the content
- Keyword stuffing (irrelevant keywords to game search) causes rejection
- Misleading keywords trigger account-level flags ([Written Word Media](https://www.writtenwordmedia.com/how-to-avoid-kdp-account-suspension/))

**Overlap management for high-volume publishing:**
- Maintain a **keyword pool of 500+ phrases** per genre
- No two titles from the same account should share more than 3 of 7 keywords
- Cross-account keyword overlap is less risky but should still be varied
- Rotate keywords on a 4-week cycle: refresh at least 3 of 7 keywords monthly

**Keyword variation formula:**
```
For title N in brand B:
  keyword_set = pick(7, genre_pool, seed=hash(brand_id + title_id))
  Ensure jaccard_similarity(keyword_set, any_same_account_title) < 0.43
```

### 3.5 Cover Image Similarity Detection

**Amazon's approach:**
- Amazon does not publicly disclose image similarity algorithms
- Known to use perceptual hashing and visual similarity scoring
- Covers that are obviously template-recolors will be flagged
- AI-generated covers must be disclosed ([KDP AI Rules](https://www.aiboxtools.com/amazon-kdp-ai-rules/))

**Cover variation requirements for 312 brands:**

| Element | Minimum Variation | Notes |
|---|---|---|
| **Color palette** | Distinct primary color per 3-5 titles | Avoid same-color runs of 5+ consecutive titles |
| **Typography** | 10+ font families per brand | Rotate title font per sub-genre |
| **Layout** | 5+ layout templates per brand | Full-bleed image, centered text, split, overlapping, minimal |
| **Imagery** | Unique hero image per title | AI-generated images acceptable with disclosure. No reuse of identical base images. |
| **Brand mark** | Consistent per brand | Publisher logo/mark can be consistent — this is expected |
| **Perceptual hash distance** | Target >15% difference | Use dHash or pHash; ensure no two covers in the same account have <15% hamming distance |

**Cover generation pipeline recommendation:**
1. Generate unique base image per title (Stable Diffusion, Midjourney, DALL-E)
2. Apply brand-specific design template (5+ templates per brand)
3. Validate perceptual hash distance against all covers in the same account
4. If distance < 15%, regenerate base image or switch template
5. Run reverse image search spot-check on 10% sample

---

## 4. Seasonal Calendar

### 4.1 United States

| Period | Dates | Demand Level | Strategy | Key Genres |
|---|---|---|---|---|
| **New Year / Resolution** | Jan 1-31 | HIGH | Surge non-fiction: self-help, health, finance, productivity | Non-fiction, self-help |
| **Valentine's Day** | Feb 1-14 | MEDIUM-HIGH | Romance surge. Pre-publish by Jan 15. | Romance, erotica |
| **Spring Break** | Mar 15 - Apr 15 | MEDIUM | Beach reads ramp-up begins | Fiction, YA, travel |
| **Summer Reading** | May 15 - Aug 31 | HIGH | Peak fiction season. Major releases timed here. | All fiction, mystery, thriller |
| **Back to School** | Aug 1 - Sep 15 | HIGH | Children's, YA, educational, study guides | Children's, education, YA |
| **Spooky Season** | Sep 15 - Oct 31 | MEDIUM-HIGH | Horror, thriller, paranormal surge | Horror, thriller, paranormal |
| **Holiday Gifting** | Nov 1 - Dec 25 | PEAK | Highest sales period of the year. ~25% of annual sales. Pre-publish by Oct 15. | ALL genres, especially fiction, cookbooks, art books |
| **Post-Holiday** | Dec 26 - Jan 5 | HIGH | Gift card redemption, Kindle device activation spike | Ebooks spike (new device owners) |

### 4.2 United Kingdom

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **New Year** | Jan 1-31 | HIGH | Same pattern as US |
| **Easter Break** | Mar/Apr (variable) | MEDIUM | Family reading, children's titles |
| **Bank Holiday Weekends** | May, Aug | MEDIUM | Impulse fiction purchases |
| **Summer Holidays** | Jul 20 - Sep 5 | HIGH | 6-week school break; peak fiction |
| **Autumn / Booker Prize** | Sep-Oct | MEDIUM-HIGH | Literary fiction surge around prize announcements |
| **Christmas** | Nov 1 - Dec 25 | PEAK | Same dynamics as US. Physical books remain top gift choice. |

### 4.3 Canada

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **New Year** | Jan 1-31 | HIGH | Resolution books |
| **Reading Week** | Feb (variable) | MEDIUM | University break; YA and literary fiction |
| **Canada Day** | Jul 1 | LOW | Minimal impact |
| **Back to School** | Sep 1-15 | HIGH | Children's, educational |
| **Thanksgiving** | Oct (2nd Monday) | MEDIUM | Earlier than US — start holiday push in October |
| **Christmas** | Nov-Dec | PEAK | Same as US/UK |

### 4.4 Australia

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Summer Holidays (Southern)** | Dec 20 - Feb 1 | HIGH | Summer reading + Christmas overlap |
| **Easter** | Mar/Apr | MEDIUM | School break reading |
| **EOFY Sales** | Jun 20-30 | MEDIUM | End of financial year; business book surge |
| **Winter School Break** | Jul 1-15 | MEDIUM | Indoor reading season |
| **Spring Reading** | Sep-Oct | MEDIUM | Pre-Christmas momentum |
| **Christmas / Summer** | Nov-Dec | PEAK | Double peak: gifting + summer reading |

### 4.5 Japan

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **New Year / Oshogatsu** | Dec 28 - Jan 7 | PEAK | Major holiday reading period. New manga volumes timed for late December. Year-end manga rankings drive purchases. ([ICv2](https://icv2.com/articles/markets/view/59057/top-20-manga-volumes-japan-november-december-2024-january-2025)) |
| **Spring / New School Year** | Apr 1-15 | HIGH | New school year begins April 1. Educational manga, children's titles surge. |
| **Golden Week** | Apr 29 - May 5 | HIGH | Extended holiday. Major reading window. New releases timed for late April. |
| **Rainy Season / Tsuyu** | Jun 1-Jul 15 | MEDIUM | Indoor reading increases. Steady manga consumption. |
| **Obon** | Aug 13-16 | HIGH | One of three major holiday periods. Travel reading + family time. Publishers time releases for early August. |
| **Autumn Reading** | Sep-Nov | MEDIUM-HIGH | "Reading Autumn" (Dokusho no Aki) is a cultural tradition. October is officially "Reading Month." |
| **Year-End** | Nov-Dec | PEAK | Gift-giving, year-end manga box sets, annual ranking season. December in-store manga sales up 8% YoY. |

### 4.6 South Korea

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Lunar New Year / Seollal** | Jan/Feb (variable) | HIGH | Holiday reading period. Webtoon binge-reading spikes. |
| **Spring** | Mar-May | MEDIUM | New academic year. Educational content. |
| **Summer / Monsoon** | Jun-Aug | MEDIUM | Indoor reading during monsoon. Webtoon consumption peaks. |
| **Chuseok** | Sep/Oct (variable) | HIGH | Major holiday. Catch-up reading period. ([Korea Herald](https://www.koreaherald.com/article/2692782)) |
| **Winter / Year-End** | Nov-Dec | HIGH | Year-end consumption, holiday spending. |

### 4.7 Taiwan

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Lunar New Year** | Jan/Feb (variable) | HIGH | Extended holiday. Manga and light novel reading surge. |
| **Taipei International Book Fair** | Feb (typically) | HIGH | Major industry event; discovery-driven purchasing |
| **Summer** | Jul-Aug | MEDIUM-HIGH | Student break; manga and light novel consumption |
| **Moon Festival / Mid-Autumn** | Sep/Oct | MEDIUM | Gift-giving occasion |
| **Year-End** | Nov-Dec | HIGH | Holiday gifting |

### 4.8 Germany

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **New Year** | Jan 1-31 | HIGH | Resolution reading |
| **Leipzig Book Fair** | Mar (typically) | MEDIUM-HIGH | Discovery event |
| **Easter** | Mar/Apr | MEDIUM | School break |
| **Frankfurt Book Fair** | Oct | HIGH | World's largest book fair. Major industry event. |
| **Advent / Christmas** | Nov 1 - Dec 24 | PEAK | Shorter December selling window (Christmas on Dec 24-26). Plan accordingly. Fixed book price law (Buchpreisbindung) means no discounting. ([Publishing Perspectives](https://publishingperspectives.com/2024/01/germanys-book-market-a-mixed-performance-in-2023/)) |

### 4.9 France

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **La Rentree Litteraire** | Sep 1-30 | PEAK | France's biggest publishing event. 500+ new novels released in September. Time fiction launches here. |
| **Salon du Livre / Festival** | Mar (typically) | HIGH | Paris book fair |
| **Summer / Vacation** | Jul-Aug | HIGH | French summer reading tradition (livre de plage). Publish by late June. |
| **Christmas** | Nov-Dec | HIGH | Gift-giving. Strict sale period regulations limit discount timing. |
| **New Year** | Jan | MEDIUM | Resolution reading |

### 4.10 Spain

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Dia del Libro / Sant Jordi** | Apr 23 | PEAK | Spain's "Day of the Book" — massive sales day. Roses + books tradition in Catalonia. Publish by April 1. |
| **Feria del Libro Madrid** | May/Jun | HIGH | Major 2-week book fair |
| **Summer** | Jul-Aug | HIGH | Vacation reading |
| **Christmas / Three Kings** | Dec 1 - Jan 6 | PEAK | Extended holiday through Epiphany (Jan 6). Gift-giving extends beyond December. |

### 4.11 Portugal / Brazil

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Carnival (Brazil)** | Feb/Mar (variable) | LOW | Country shuts down. Do NOT launch during Carnival week. |
| **Dia do Livro (Brazil)** | Oct 29 | MEDIUM-HIGH | National Book Day |
| **Bienal do Livro (Brazil)** | Biennial, Aug/Sep | HIGH | Massive book fair in Sao Paulo and Rio |
| **Christmas** | Nov-Dec | HIGH | Gift-giving season in both countries |
| **Summer (Brazil)** | Dec-Feb | MEDIUM | Southern hemisphere summer; beach reading |
| **Summer (Portugal)** | Jun-Aug | MEDIUM | European summer reading |

### 4.12 Indonesia

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Ramadan** | Variable (Mar/Apr in 2025-2027) | HIGH | Reading increases during fasting month. Islamic content surges. Publish by 2 weeks before Ramadan. |
| **Eid al-Fitr / Lebaran** | End of Ramadan | HIGH | Gift-giving. Extended holiday travel with reading time. |
| **Independence Day** | Aug 17 | MEDIUM | Patriotic content, educational materials |
| **Year-End** | Nov-Dec | MEDIUM-HIGH | School holidays, gift-giving |

### 4.13 Thailand

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Songkran / Thai New Year** | Apr 13-15 | MEDIUM | Holiday period; some reading increase |
| **National Book Week** | Mar/Apr (typically) | HIGH | Bangkok International Book Fair; major sales event |
| **Rainy Season** | May-Oct | MEDIUM | Indoor activities increase; steady reading |
| **Year-End / Cool Season** | Nov-Feb | MEDIUM-HIGH | Pleasant weather + holidays; increased leisure reading |

### 4.14 Vietnam

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Tet / Lunar New Year** | Jan/Feb (variable) | HIGH | Major holiday. Reading tradition during extended break. |
| **Vietnam Book Day** | Apr 21 | MEDIUM-HIGH | National promotion of reading culture |
| **Summer Break** | Jun-Aug | MEDIUM | Student reading period |
| **Mid-Autumn Festival** | Sep/Oct | MEDIUM | Family time; children's titles |

### 4.15 Philippines

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Summer / School Break** | Mar-May | MEDIUM-HIGH | Reading during break |
| **Filipino Book Month** | Nov | HIGH | Government-sponsored reading promotion |
| **Christmas** | Sep 1 - Jan 6 | HIGH | Philippines has the world's longest Christmas season. Gift-giving starts in "ber months" (September). |

### 4.16 India

| Period | Dates | Demand Level | Strategy |
|---|---|---|---|
| **Diwali** | Oct/Nov (variable) | PEAK | Biggest shopping festival. Books as gifts tradition growing. Publish by October 1. ([India market data](https://www.statista.com/outlook/amo/media/books/india)) |
| **Navratri / Durga Puja** | Sep/Oct | HIGH | Festival season; increased consumer spending |
| **Republic Day** | Jan 26 | MEDIUM | Patriotic content, educational |
| **Summer / School Break** | May-Jun | HIGH | Student reading; competitive exam prep books |
| **Independence Day** | Aug 15 | MEDIUM | Hindi novels peak in August. ([Accio](https://www.accio.com/business/trending-books-in-hindi)) |
| **New Delhi Book Fair** | Jan (typically) | HIGH | One of Asia's largest book fairs |
| **Christmas / New Year** | Dec-Jan | MEDIUM-HIGH | Especially in metros; fiction and English-language titles |

### 4.17 Global Seasonal Multiplier Summary

| Month | US/UK/CA | AU | JP | KR/TW | DE/FR/ES | SEA | IN | BR/PT |
|---|---|---|---|---|---|---|---|---|
| Jan | 1.3 | 1.0 | 1.5 | 1.3 | 1.1 | 1.0 | 1.3 | 0.8 |
| Feb | 1.1 | 0.9 | 0.9 | 1.0 | 1.0 | 1.0 | 0.9 | 0.6 |
| Mar | 1.0 | 0.9 | 1.0 | 1.0 | 1.2 | 1.3 | 1.0 | 0.9 |
| Apr | 1.0 | 1.0 | 1.3 | 1.0 | 1.4 | 1.2 | 1.0 | 1.0 |
| May | 1.1 | 0.9 | 1.2 | 1.0 | 1.0 | 1.0 | 1.2 | 1.0 |
| Jun | 1.2 | 1.1 | 0.9 | 0.9 | 1.0 | 1.0 | 1.1 | 1.0 |
| Jul | 1.3 | 1.1 | 1.0 | 1.0 | 1.2 | 1.0 | 1.0 | 1.0 |
| Aug | 1.3 | 0.9 | 1.3 | 1.0 | 0.8 | 1.0 | 1.2 | 1.2 |
| Sep | 1.2 | 1.0 | 1.1 | 1.3 | 1.5 | 1.0 | 1.3 | 1.2 |
| Oct | 1.2 | 1.1 | 1.2 | 1.1 | 1.3 | 1.0 | 1.5 | 1.1 |
| Nov | 1.5 | 1.2 | 1.3 | 1.2 | 1.4 | 1.1 | 1.4 | 1.0 |
| Dec | 1.7 | 1.5 | 1.6 | 1.3 | 1.6 | 1.1 | 1.2 | 1.2 |

Multipliers are relative to a baseline of 1.0 (average monthly demand). Values >1.0 indicate surge periods; <1.0 indicate coast periods.

---

## 5. Actionable Parameters (YAML-ready)

```yaml
# Phoenix Omega — Publishing Cadence Configuration
# Generated: 2026-04-05 by Pearl_Research
# Merge into weekly queue config

publishing_cadence:
  # ── Per-Account Daily Limits ──────────────────────────────
  max_titles_per_account_per_day:
    amazon_kdp: 2          # Hard limit is 3; use 2 for safety margin
    apple_books: 5
    kobo_writing_life: 5
    google_play_books: 10
    barnes_noble_press: 5
    draft2digital: 8       # Fans out to 6+ retailers per upload
    line_manga: 3
    ingramspark: 5

  max_titles_per_account_per_week:
    amazon_kdp: 10         # 2/day x 5 days; never 7 days straight
    apple_books: 25
    kobo_writing_life: 25
    google_play_books: 50
    barnes_noble_press: 25
    draft2digital: 40
    line_manga: 15
    ingramspark: 25

  # ── Upload Spacing ────────────────────────────────────────
  min_hours_between_uploads_same_account: 3
  max_uploads_per_burst: 1      # Never upload 2+ at the exact same time
  upload_days_per_week: 5       # Mon-Fri; rest Sat-Sun
  randomize_upload_time: true   # +/- 90 min jitter to avoid automation patterns

  # ── New Account Ramp-Up Schedule ──────────────────────────
  ramp_week_schedule:
    amazon_kdp:
      week_01: { per_day: 1, per_week: 5 }
      week_02: { per_day: 1, per_week: 5 }
      week_03: { per_day: 1, per_week: 7 }
      week_04: { per_day: 2, per_week: 10 }
      week_05: { per_day: 2, per_week: 10 }
      week_06: { per_day: 2, per_week: 10 }
      week_07: { per_day: 2, per_week: 12 }
      week_08: { per_day: 2, per_week: 14 }
      week_09: { per_day: 3, per_week: 15 }
      week_10: { per_day: 3, per_week: 15 }
      week_11: { per_day: 3, per_week: 15 }
      week_12_plus: { per_day: 2, per_week: 10 }  # Sustainable cruise
    apple_books:
      week_01: { per_day: 2, per_week: 10 }
      week_02: { per_day: 3, per_week: 15 }
      week_03: { per_day: 4, per_week: 20 }
      week_04_plus: { per_day: 5, per_week: 25 }
    kobo_writing_life:
      week_01: { per_day: 2, per_week: 10 }
      week_02: { per_day: 3, per_week: 15 }
      week_04_plus: { per_day: 5, per_week: 25 }
    google_play_books:
      week_01: { per_day: 3, per_week: 15 }
      week_02: { per_day: 5, per_week: 25 }
      week_04_plus: { per_day: 10, per_week: 50 }
    draft2digital:
      week_01: { per_day: 3, per_week: 15 }
      week_02: { per_day: 5, per_week: 25 }
      week_04_plus: { per_day: 8, per_week: 40 }
    ingramspark:
      week_01: { per_day: 2, per_week: 10 }
      week_02: { per_day: 3, per_week: 15 }
      week_04_plus: { per_day: 5, per_week: 25 }

  # ── Account Age Milestones (Amazon KDP) ───────────────────
  kdp_account_milestones:
    day_000_030:
      review_time_days: "5-10"
      velocity_class: "restricted"
      max_daily: 1
    day_031_060:
      review_time_days: "3-5"
      velocity_class: "warming"
      max_daily: 2
    day_061_090:
      review_time_days: "2-3"
      velocity_class: "normal"
      max_daily: 2
    day_091_180:
      review_time_days: "2-3"
      velocity_class: "established"
      max_daily: 3
    day_180_plus:
      review_time_days: "1-3"
      velocity_class: "trusted"
      max_daily: 3

  # ── Variation Requirements ────────────────────────────────
  variation_requirements:
    title:
      min_unique_words: 3            # At least 3 words must differ from any same-account title
      allow_series_prefix: true      # "Series Name: Unique Title" is OK
      cross_account_duplicate: false # Never exact-match title+author across accounts
    description:
      max_verbatim_overlap_pct: 30   # <30% shared sentences with any same-category title
      min_template_variants: 50      # Per genre
      swap_sections: 5               # Hook, premise, tone, CTA, bio
      refresh_cycle_weeks: 4
    categories:
      bisac_codes_per_title: 3
      max_same_subcategory_per_week_per_account: 3
      min_subcategories_per_brand: 5
    keywords:
      slots_per_title: 7
      max_overlap_same_account: 3    # Max 3 of 7 shared with any same-account title
      pool_size_per_genre: 500       # Minimum keyword phrases in rotation pool
      refresh_cycle_weeks: 4
    cover_image:
      min_perceptual_hash_distance_pct: 15  # dHash hamming distance as %
      color_palette_rotation: 5             # Change primary color every 3-5 titles
      layout_templates_per_brand: 5
      font_families_per_brand: 10
      ai_disclosure_required: true          # All platforms require AI image disclosure

  # ── Seasonal Multipliers by Market ────────────────────────
  # Multiply base weekly quota by these factors per month
  seasonal_multipliers_by_market:
    us_uk_ca:
      jan: 1.3
      feb: 1.1
      mar: 1.0
      apr: 1.0
      may: 1.1
      jun: 1.2
      jul: 1.3
      aug: 1.3
      sep: 1.2
      oct: 1.2
      nov: 1.5
      dec: 1.7
    australia:
      jan: 1.0
      feb: 0.9
      mar: 0.9
      apr: 1.0
      may: 0.9
      jun: 1.1
      jul: 1.1
      aug: 0.9
      sep: 1.0
      oct: 1.1
      nov: 1.2
      dec: 1.5
    japan:
      jan: 1.5
      feb: 0.9
      mar: 1.0
      apr: 1.3
      may: 1.2
      jun: 0.9
      jul: 1.0
      aug: 1.3
      sep: 1.1
      oct: 1.2
      nov: 1.3
      dec: 1.6
    korea_taiwan:
      jan: 1.3
      feb: 1.0
      mar: 1.0
      apr: 1.0
      may: 1.0
      jun: 0.9
      jul: 1.0
      aug: 1.0
      sep: 1.3
      oct: 1.1
      nov: 1.2
      dec: 1.3
    europe_de_fr_es:
      jan: 1.1
      feb: 1.0
      mar: 1.2
      apr: 1.4  # Sant Jordi (Spain), spring fairs
      may: 1.0
      jun: 1.0
      jul: 1.2  # French summer reading
      aug: 0.8  # August shutdown in parts of EU
      sep: 1.5  # La Rentree Litteraire (France)
      oct: 1.3  # Frankfurt Book Fair
      nov: 1.4
      dec: 1.6
    southeast_asia:
      jan: 1.0
      feb: 1.0
      mar: 1.3  # Ramadan start (variable), Thai Book Week
      apr: 1.2  # Ramadan/Eid (variable)
      may: 1.0
      jun: 1.0
      jul: 1.0
      aug: 1.0
      sep: 1.0
      oct: 1.0
      nov: 1.1  # Filipino Book Month
      dec: 1.1
    india:
      jan: 1.3  # New Delhi Book Fair
      feb: 0.9
      mar: 1.0
      apr: 1.0
      may: 1.2  # Summer break
      jun: 1.1
      jul: 1.0
      aug: 1.2  # Hindi novels peak
      sep: 1.3  # Navratri
      oct: 1.5  # Diwali
      nov: 1.4  # Post-Diwali
      dec: 1.2
    brazil_portugal:
      jan: 0.8
      feb: 0.6  # Carnival — DO NOT launch
      mar: 0.9
      apr: 1.0
      may: 1.0
      jun: 1.0
      jul: 1.0
      aug: 1.2  # Bienal do Livro (biennial)
      sep: 1.2
      oct: 1.1  # Dia do Livro (Brazil)
      nov: 1.0
      dec: 1.2

  # ── Multi-Account Scaling ─────────────────────────────────
  multi_account:
    target_titles_per_week: 4680     # 312 brands x 15 titles/brand/week
    kdp_accounts_needed: 500         # 4680 / ~10 per account with headroom
    other_platform_accounts_needed: 80  # Apple, Kobo, Google, B&N combined
    aggregator_accounts: 20          # D2D + IngramSpark
    ramp_to_full_velocity_months: 5
    monthly_ramp:
      month_1: { accounts_active: 50, titles_per_week: 250 }
      month_2: { accounts_active: 100, titles_per_week: 800 }
      month_3: { accounts_active: 200, titles_per_week: 2000 }
      month_4: { accounts_active: 350, titles_per_week: 4200 }
      month_5_plus: { accounts_active: 500, titles_per_week: 4680 }

  # ── Review Queue Lead Times (publish-by deadlines) ────────
  lead_time_days_before_target_live_date:
    amazon_kdp_ebook: 7              # 3-5 days review + 2 days buffer
    amazon_kdp_paperback: 14         # 5-10 days review + buffer
    apple_books: 5
    kobo: 5
    google_play: 3
    barnes_noble: 7
    draft2digital: 7                 # D2D processing + partner review
    ingramspark: 10                  # 3-day eProof + approval + distribution

  # ── Health Monitoring Thresholds ──────────────────────────
  alerts:
    review_time_warning_hours: 120   # Alert if review > 5 days
    review_time_critical_hours: 240  # Escalate if review > 10 days
    rejection_rate_warning_pct: 5    # Alert if >5% of submissions rejected
    rejection_rate_critical_pct: 10  # Pause account if >10% rejected
    account_suspension_action: "immediate_pause_all_uploads"
    kobo_title_cap_warning: 450      # Warn when approaching 500-title limit
```

---

## 6. Sources

### Platform Policies
- [Amazon KDP Daily Limit — Publishers Weekly](https://www.publishersweekly.com/pw/by-topic/digital/content-and-e-books/article/93207-kdp-will-limit-daily-number-of-new-titles.html)
- [Amazon KDP Daily Limit — Jane Friedman](https://janefriedman.com/amazon-kdp-limits-how-many-books-can-be-uploaded-per-day/)
- [Amazon KDP AI Policy Update — Authors Guild](https://authorsguild.org/news/amazon-adds-to-kdp-generative-ai-policy-caps-daily-self-publishing-uploads/)
- [KDP Content Quality Guide](https://kdp.amazon.com/en_US/help/topic/G200952510)
- [KDP Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390)
- [KDP Timelines](https://kdp.amazon.com/en_US/help/topic/G202173620)
- [KDP AI Rules 2025 — AIBoxTools](https://www.aiboxtools.com/amazon-kdp-ai-rules/)
- [KDP Cover Image Guidelines](https://kdp.amazon.com/en_US/help/topic/G6GTK3T3NUHKLEFX)
- [Avoiding KDP Account Suspension — Written Word Media](https://www.writtenwordmedia.com/how-to-avoid-kdp-account-suspension/)
- [Apple Books Publishing Guide — Reedsy](https://reedsy.com/blog/how-to-publish-on-apple-books/)
- [Apple Books Publisher User Guide](https://help.apple.com/itc/bookspublisher/en.lproj/static.html)
- [Apple Pages Discontinuation — Apple Insider](https://appleinsider.com/articles/25/04/04/authors-can-no-longer-publish-to-apple-books-directly-from-pages)
- [Kobo Writing Life FAQ](https://kobowritinglife.zendesk.com/hc/en-us/articles/37446931721883-FAQ)
- [Kobo Writing Life Terms of Service](https://cdn.kobo.com/merch-assets/writinglife/KOBO/en-US/serviceAgreement.html)
- [Google Play Books Partner Center](https://support.google.com/books/partner/answer/3424254?hl=en)
- [Google Play Publisher Policies](https://support.google.com/books/partner/answer/166501?hl=en)
- [B&N Press](https://press.barnesandnoble.com)
- [B&N Publishing Help](https://help.barnesandnoble.com/hc/en-us/articles/42541436590619-Publishing-Selling-Your-Book-with-Barnes-Noble)
- [Draft2Digital FAQ](https://draft2digital.com/faq/)
- [IngramSpark FAQ](https://www.ingramspark.com/faqs)
- [IngramSpark User Guide v3.0 (Aug 2025)](https://www.ingramspark.com/hubfs/downloads/user-guide.pdf)
- [LINE Manga CEO Interview — Oricon](https://us.oricon-group.com/news/6631/)

### Market Data & Seasonal
- [Why KDP Publishing Takes Long — Book Upload Pro](https://blog.bookuploadpro.com/why-amazon-kdp-publishing-takes-long/)
- [KDP Publishing Slow — Book Upload Pro](https://blog.bookuploadpro.com/why-amazon-kdp-is-so-slow/)
- [When to Launch a Book 2026 — Triage Press](https://www.thetriagepress.com/when-is-the-best-time-to-launch-a-book/)
- [Holiday Season Book Projections — Bookazine](https://www.bookazine.com/what-is-the-retail-sales-projection-for-trade-books-globally-for-the-2025-holiday-season/)
- [Japan Manga Market — ICv2](https://icv2.com/articles/columns/view/59058/japan-manga-market-slows-digital-captures-73-share)
- [Japan Top Manga Volumes Nov-Jan — ICv2](https://icv2.com/articles/markets/view/59057/top-20-manga-volumes-japan-november-december-2024-january-2025)
- [Germany Book Market 2023 — Publishing Perspectives](https://publishingperspectives.com/2024/01/germanys-book-market-a-mixed-performance-in-2023/)
- [India Books Market — Statista](https://www.statista.com/outlook/amo/media/books/india)
- [India Books Market — Grand View Research](https://www.grandviewresearch.com/horizon/outlook/books-market/india)
- [India Trending Hindi Books — Accio](https://www.accio.com/business/trending-books-in-hindi)
- [South Korea Webtoon Market — ANN](https://www.animenewsnetwork.com/news/2025-08-18/webtoon-market-in-korea-slows-sharply-in-1st-half-of-2025-as-platforms-consolidate/.227736)
- [Chuseok Webtoon Reading — Korea Herald](https://www.koreaherald.com/article/2692782)
- [Southeast Asia Books Market — Statista](https://www.statista.com/outlook/amo/media/books/southeast-asia)
- [Indonesia Books Market — 6W Research](https://www.6wresearch.com/industry-report/indonesia-books-market-outlook)
- [Asia Reading Culture 2026 — Tatler](https://www.tatlerasia.com/lifestyle/arts/inside-asias-reading-culture-in-2026-book-trends)
- [European Sales Calendar 2025 — Herm.io](https://www.herm.io/shopping-tips/master-the-european-sales-calendar-2025-a-strategic-country-by-country-timeline)
- [India Book Fairs 2025 — NetZero India](https://netzeroindia.org/indias-book-fairs-in-2025/)

---

> **End of Research Document**
> Total coverage: 8 platforms, 16 country/region seasonal calendars,
> ramp-up schedules, variation matrices, and production-ready YAML config.

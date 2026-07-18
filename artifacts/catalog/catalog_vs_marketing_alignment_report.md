# Catalog vs Marketing Alignment Report -- Cross-Analysis

**Date:** 2026-04-05
**Analyst:** Pearl_Marketing + Pearl_Research
**Catalog:** W14 en_US weekly production queue (360 titles, 24 brands)
**Cross-referenced against:** marketing_plan.yaml, all 8 research reports, catalog configs, 48 Social spec, daily market intelligence config

---

## 1. Marketing Plan Alignment Check

### 1.1 Channel-by-Channel Content Fit

**Channel: Google Play Search (primary discovery for en_US)**

- marketing_plan.yaml lists `google_play_search` as the #1 en_US discovery channel.
- The catalog produces titles with keyword-loaded subtitles, which is correct for search discoverability.
- HOWEVER: The catalog's `keyword_templates` in `catalog_generation_config.yaml` show identical 7-keyword sets per topic across ALL 360 titles. Google Play search de-duplicates heavily. Having 45 anxiety titles with the same keywords means most will be invisible.
- **Verdict: PARTIAL ALIGNMENT.** Titles exist but keyword differentiation by format is missing.

**Channel: YouTube Organic (primary discovery for en_US)**

- marketing_plan.yaml specifies YouTube long-form 3/week, Shorts daily.
- The content repurposing pipeline (48 Social spec) confirms 5 video formats per book, including YouTube and Shorts.
- The catalog produces 360 titles/week, which feeds 1,800 video assets (5 per book). This exceeds the posting cadence (3 long + 7 Shorts = 10/week per brand). At 24 brands, that is 240 videos/week needed vs. 1,800 produced -- massive surplus.
- **Verdict: ALIGNED.** Content supply exceeds distribution demand. No bottleneck.

**Channel: TikTok Organic (primary discovery for en_US)**

- marketing_plan.yaml lists TikTok organic + daily posting.
- The marketing analysis identified 10 "BookTok-ready" titles (Own Your Seat, You're Not a Fraud, Safe Enough, etc.) that have the emotional punch for virality.
- PROBLEM: The catalog's best BookTok titles are concentrated in 3-4 topics (imposter_syndrome, anxiety, boundaries). Topics like grief (63 titles -- the HIGHEST in the queue) are overrepresented relative to their BookTok potential. Grief content works on BookTok but not at 63-title scale.
- **Verdict: PARTIAL ALIGNMENT.** BookTok-ready titles exist but topic weighting does not match BookTok demand patterns.

**Channel: Instagram Reels (secondary discovery)**

- marketing_plan.yaml specifies carousel mix 3/week.
- 48 Social creates 5 carousel posts per book. At 360 titles, that is 1,800 carousels/week -- again massive surplus.
- The advertising_roi_research found carousel ads have the best engagement for educational/self-help content (0.55% engagement rate). The catalog's educational subtitle pattern (e.g., "A Somatic Guide to...") supports carousel-format breakdowns.
- **Verdict: ALIGNED.**

**Channel: Podcast Cross-Promo (secondary discovery)**

- marketing_plan.yaml lists podcast_crosspromo.
- advertising_roi_research confirms podcast guesting is the highest-ROI organic strategy. 158M monthly US podcast listeners.
- The catalog does NOT produce podcast-specific content (interview scripts, episode outlines, sound bites). This is a missing content layer.
- **Verdict: GAP.** The catalog feeds books and social posts but not podcast appearance prep materials.

**Channel: Email (proof loop E1-E5 via GHL)**

- marketing_plan.yaml specifies expected 35% open rate, 8% click rate.
- 48 Social spec confirms E1-E5 email sequence is live and auto-triggered by freebie downloads.
- CRITICAL GAP: The catalog has ZERO $0.00 (permafree) titles. The `catalog_generation_config.yaml` specifies `book_1_price_override: 0.00` for series, but the W14 queue shows ALL series books at $3.99 (all are "Book 4" -- no Book 1s in this week's queue). Without a permafree entry point, the email funnel has no traffic source.
- **Verdict: MISALIGNED.** The email funnel exists but the catalog is not producing the free lead magnet that feeds it.

**Channel: Reddit Organic (secondary discovery)**

- marketing_plan.yaml lists reddit_organic.
- advertising_roi_research found Reddit CPM is $3-7 for health niche (vs. Meta's $20.70). Reddit users are research-oriented buyers.
- The catalog produces educational standalone titles ($2.99) that would work for Reddit's value-first audience. However, no Reddit-specific content (AMAs, excerpt posts, worksheet shares) is planned.
- **Verdict: PARTIAL ALIGNMENT.** Product fits the channel but no Reddit-specific content strategy exists.

### 1.2 Title Readiness Assessment

**BookTok-Ready?**
- YES for top-tier titles: "Own Your Seat," "Safe Enough," "You're Not a Fraud," "The Proof Was Always You," "Still Here Without You."
- NO for series entries: "The Steady Ground Collection: Book 4" is not BookTok-shareable. The "Book 4" suffix kills virality.
- NO for generic titles: "Steady Ground" (used by 3+ different brands in the queue), "False Alarm" (appears multiple times).
- Score: 6/10. Top titles are excellent. Bottom 40% are forgettable.

**Instagram-Ready?**
- YES. The visual title + subtitle pattern maps well to quote cards and carousels.
- The cover_brief_templates in catalog_generation_config.yaml provide 10 visual styles. The minimalist_gradient and bold_typography styles work best for Instagram.
- Score: 7/10.

**Amazon-Search-Optimized?**
- PARTIAL. Subtitles contain keywords, but the bestseller_titles_seo_covers_research found the optimal total title+subtitle length is under 120 characters. Several subtitles with "-- A Quick Guide" suffix exceed this.
- The marketing analysis already flagged "-- A Quick Guide" as a P0 fix item. It is still present in the W14 queue output (multiple micro titles still carry it).
- Score: 5/10. Keywords present but optimization is incomplete.

### 1.3 Weekly Mix vs Marketing Funnel

The marketing_plan.yaml defines a value ladder: free -> micro ($0.99) -> standard ($3.99-$6.99) -> premium ($14.99-$24.99) -> series ($4.99/installment) -> bundle.

The W14 queue produces:
| Format | Count | Price | Funnel Role |
|--------|-------|-------|-------------|
| micro_book_15 | 72 | $0.99 | Cold-start / review gen |
| micro_book_20 | 24 | $0.99 | Cold-start / review gen |
| short_book_30 | 192 | $2.99 | Core revenue |
| standard_book (series) | 48 | $3.99 | Retention / LTV |
| extended_book_2h | 24 | $9.99 | High-value |

**Funnel gaps:**
1. NO $0.00 permafree tier. The config says `book_1_price_override: 0.00` but the queue produces only Book 4s this week.
2. NO $4.99-$7.99 tier. The value ladder mentions $3.99-$6.99 standard, but the catalog jumps from $3.99 to $9.99. No $4.99 or $5.99 products exist.
3. NO bundles. The value ladder mentions bundles but the queue produces zero bundle products.
4. NO $14.99-$24.99 premium tier. The format_pricing in weekly_queue_config.yaml lists `deep_book_4h: $17.99` and `deep_book_6h: $24.99` but neither appears in the W14 queue.

**Verdict: The catalog covers the bottom and middle of the funnel but misses the top (premium, bundles) and the entry (free).** The funnel is headless (no free) and topless (no premium), making it a mid-funnel machine with no acquisition and no maximum-LTV strategy.

### 1.4 Permafree Strategy Alignment

- marketing_plan.yaml cold_start_product for en_US: "$0.99 7-Day Anxiety Challenge"
- advertising_roi_research: "every 1,000 email subscribers = 50-150 sales per launch"
- catalog_generation_config.yaml: `book_1_price_override: 0.00` (permafree via KDP price-match)
- W14 queue reality: ZERO permafree titles. All series entries are Book 4 at $3.99.

**This is the single largest misalignment in the entire system.** The marketing plan, advertising research, and catalog config all agree that permafree is the highest-ROI acquisition strategy. But the production queue is in Week 14 producing Book 4 of existing series with no Book 1 (free) entry points being generated this week.

- **Verdict: CRITICAL MISALIGNMENT.** The permafree strategy is configured but not executing. The queue needs to produce new series with Book 1 at $0.00, not just continuation installments.

---

## 2. Research-to-Catalog Alignment

### 2.1 bestseller_titles_seo_covers_research.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| FORMULA 1: "The [Concept Name]" pattern dominates bestsellers | YES -- "The Alarm Is Lying," "The Open Door Problem," "The Grey Season" follow this | ALIGNED |
| FORMULA 4: "[Provocative Hook]: [Practical Promise]" | YES -- "You're Not a Fraud: Overcoming Imposter Syndrome" follows this | ALIGNED |
| FORMULA 5: "[Verb] Your [Inner State]" command pattern | PARTIAL -- "Own Your Seat" uses command. But most titles use "The [Noun]" pattern instead | GAP |
| Main title sweet spot: 2-6 words, 15-40 characters | YES -- most titles fit (e.g., "Safe Enough" = 2 words, "The Replay Button" = 3 words) | ALIGNED |
| Avoid AI-signal words: "Blueprint," "Strategies," "Master," "Step into," "Practical guide" | PARTIAL -- "A Practical Guide" appears in 2 subtitle patterns. "Guide" appears in 18+ subtitles. Not flagged as severely as "practical guide" but still overused. | GAP |
| 77% of Amazon self-help is AI-generated; differentiate with emotional, story-driven language | YES -- titles like "Still Here Without You," "The Weight of Gone," "Color Returns" are distinctly human-sounding | ALIGNED |
| Total title+subtitle under 120 characters for best display | NOT VERIFIED at scale. "-- A Quick Guide" suffix pushes many micro titles over 120 characters | GAP |
| Words that sell: Purpose, Journey, Heal, Transform, Rise, Nervous System, Somatic | PARTIAL -- "Nervous system" and "somatic" are in subtitles. "Purpose," "journey," "transform" are underused. | PARTIAL |

**GAPS NOT REFLECTED:**
1. The research identified that SOCIAL PROOF in subtitles ("That Millions Can't Stop Talking About") drives virality. Zero catalog titles use social proof language.
2. The research found AUDIENCE-FIRST subtitles ("A Millennial and Gen Z Guide to...") work when targeting specific demographics. The catalog's subtitles are generic -- no persona-specific subtitle variants.
3. Cover requirements per platform were documented in detail (Google Play: 1600x2400px, Amazon: 2560x1600px, etc.) but the catalog config has only 10 generic cover_brief_templates with no per-platform sizing specifications.

### 2.2 search_behavior_title_strategy_research.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| People search PAIN STATE, not clinical terms. "Can't sleep" not "sleep anxiety" | PARTIAL -- keyword_templates include "cant sleep book" and "3am anxiety" (good) but also "insomnia self help" (clinical). Title "The 3 AM Mind" captures this well. | MOSTLY ALIGNED |
| "Nervous system regulation" has 5x growth and 246K monthly searches | YES -- keyword_templates for somatic_healing lead with "nervous system regulation book" | ALIGNED |
| "Imposter syndrome" IS the colloquial search term (1.5B+ TikTok views) | YES -- keyword_templates use exact phrase | ALIGNED |
| "People pleasing" is fastest-growing related search for boundaries | YES -- keyword_templates include "people pleasing recovery" | ALIGNED |
| "Phone anxiety" and "social media anxiety" are emerging Gen Z searches | NO -- keyword_templates for social_anxiety do not include "phone anxiety." They have "social anxiety recovery" and "introvert anxiety" but miss the Gen Z-specific terms. | GAP |
| "Burnout" = the search term AND colloquial term; "moral injury" 4x growth in healthcare | PARTIAL -- "burnout recovery" is present. "Moral injury" is completely absent from keyword_templates. | GAP |
| "How to love yourself" is #3 search for self-worth at HIGH volume | NO -- keyword_templates for self_worth do not include it. Has "self love guide" which is adjacent but not the exact search phrase. | GAP |
| Per-topic subtitle recommendations (e.g., anxiety subtitle must capture: anxiety, nervous system, calm, relief, recovery) | MOSTLY YES -- subtitle patterns generally include the research-specified keywords. | ALIGNED |

**CRITICAL GAP: The research produced 57 title+subtitle pairs (19 topics x 3) as templates. The catalog_generation_config.yaml has title_templates for only 15 topics (missing adhd_focus and mindfulness templates entirely).** The research also recommended per-market title adaptations, but the catalog uses English-only title templates with no localization guidance.

### 2.3 advertising_roi_research.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| Amazon Sponsored Products: $0.30-$0.60 CPC, best for $2.99+ titles | YES -- 192 titles at $2.99 are the perfect price point for Amazon ads. $2.09 royalty with $0.60 CPC = profitable. | ALIGNED |
| TikTok Spark Ads: $0.50 CPC median, boost organic BookTok content | PARTIAL -- BookTok-ready titles exist but topic distribution skews toward grief (63 titles), which is not the highest-engagement TikTok topic. Anxiety and imposter_syndrome are TikTok's top self-help categories. | PARTIAL |
| Reddit Ads: $3-7 CPM, underpriced for niche health targeting | The catalog produces educational standalones that fit Reddit's audience. But the queue produces zero Reddit-specific content (excerpts, worksheets). | GAP |
| Email list: every 1,000 subscribers = 50-150 sales per launch | CRITICAL: No permafree funnel entry to BUILD the email list. The 48 Social GHL integration is configured but the traffic source (free book -> email capture) is not being produced. | CRITICAL GAP |
| Short-form video drives 84% conversion increase | The content pipeline produces 5 video formats per book. This aligns. | ALIGNED |
| Minimum 10+ reviews before Amazon ads become cost-effective | The $0.99 micro books (96 titles) are designed as review generators. This is correct strategy. | ALIGNED |
| LINE Japan: $0.67-$1.52 CPM, cheapest platform found | This is a Japan-market finding. The current analysis is en_US only. Not directly applicable but noted for lane expansion. | N/A (different lane) |

**GAPS NOT REFLECTED:**
1. Research found carousel ads outperform Reels for self-help conversions on Meta. The 48 Social spec creates 5 carousel posts per book -- this is aligned. But the ad budget recommendation in the marketing analysis allocates $300/month to Meta retargeting with no specific carousel ad creative brief.
2. Research found lookalike audiences from email lists consistently outperform interest-based targeting. With ZERO permafree funnel, there is no email list to build lookalikes from.
3. Research found Pinterest pins have long shelf life and books rank in top 23 viral pin categories. Pinterest is listed in the marketing_plan.yaml content_repurposing platforms but no Pinterest-specific content formatting exists in the catalog or 48 Social spec.

### 2.4 publishing_cadence_research.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| Amazon KDP hard limit: 3 titles/day/account | weekly_queue_config.yaml: 15 titles/brand/week. With 24 brands, that is 360 titles/week. At 3/day max = 21/week max per account. Need 17+ accounts to publish 360/week. | MISALIGNMENT (see Section 6) |
| Practical safe ceiling: 2/day, 5 days/week = 10/week/account | At 10/week/account, need 36 accounts for 360 titles. This is a significant operational requirement. | MISALIGNMENT |
| New account ramp: Week 1-4 = 1-2/day max | If launching 36 accounts simultaneously, the first month can only produce ~5-10 titles/account/week = 180-360 total. Month 1 might produce only 50% of the queue. | GAP |
| Apple Books: 5-8/day safe ceiling after 30 days | More permissive. 24 brands x 15 titles = 360 titles. At 8/day = 56/week per account. Need ~7 Apple accounts. | PARTIAL ALIGNMENT |
| Kobo: 500-title account cap triggers review | At 360/week, a single Kobo account hits 500 titles in under 2 weeks. Multi-account strategy needed. | GAP |
| Google Play: 10/day safe ceiling (least restrictive) | At 10/day = 70/week. Need ~5 Google Play accounts. Most feasible platform for volume. | ALIGNED |

### 2.5 global_topic_gap_analysis.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| Recommend expanding from 15 to 20-22 topics | catalog_generation_config.yaml now has 17 topics (added adhd_focus, mindfulness). Still 3-5 short of the recommendation. | PARTIAL |
| MERGE financial_anxiety + financial_stress -> financial_wellness | NOT DONE. Both still exist as separate topics. Combined they only produce 12 titles (7 financial_stress + 5 financial_anxiety). | GAP |
| Add people-pleasing/codependency (HIGH priority) | NOT ADDED. The boundaries keyword_templates include "people pleasing recovery" and "codependency healing" but no dedicated topic exists. | GAP |
| Add trauma recovery/PTSD (HIGH priority) | NOT ADDED. somatic_healing covers body-based trauma but no dedicated trauma recovery topic. | GAP |
| Add anger management/emotional regulation (HIGH priority) | NOT ADDED. Zero representation. | GAP |
| Add ADHD/neurodivergence (HIGH priority) | PARTIALLY ADDED. adhd_focus is now a topic with 4 titles in the W14 queue, but the gap analysis recommended it as a full 20+ title topic. 4 is severely underweight. | UNDERWEIGHT |
| Add loneliness/isolation (HIGH priority) | NOT ADDED. Zero representation despite research showing 74% of Gen Z report regular loneliness. | GAP |
| Depression: reframe away from clinical term per market | PARTIAL. Depression title templates use "The Light You Forgot," "Still Breathing," "Color Returns" -- these avoid the clinical term in the title. But the keyword_templates still lead with "depression recovery book." | PARTIAL |
| Compassion fatigue: reframe as "emotional exhaustion from caring" in non-English markets | N/A for en_US lane. For en_US, the titles "Caring Until There's Nothing Left" and "Who Heals the Healer" are well-framed. | ALIGNED (en_US) |

**5 of 7 HIGH-PRIORITY missing topics from the gap analysis are STILL missing from the catalog.** Only adhd_focus was added (severely underweight at 4 titles), and mindfulness was added (6 titles). People-pleasing, trauma recovery, anger management, ADHD (full scale), and loneliness are all absent.

### 2.6 gen_z_student_persona_research.md

| Research Finding | Catalog Implementation | Status |
|-----------------|----------------------|--------|
| 83M+ addressable student population across 13 markets | gen_z_student is a canonical persona in the config | ALIGNED (in theory) |
| 60%+ of Gen Z diagnosed with anxiety; social anxiety is #1 subtype | W14 queue: gen_z_student persona titles are distributed across brands. The marketing analysis found only 24 gen_z_student titles in the W14 catalog -- UNDERWEIGHT. | GAP |
| Phone anxiety (74% anxious making calls) and social media anxiety are distinct triggers | keyword_templates do not include "phone anxiety" or "social media anxiety" | GAP |
| Academic burnout is a massive search category | The marketing analysis found 0 burnout titles for gen_z_student | CRITICAL GAP |
| Financial stress: 59% cite it as top concern | financial_anxiety and financial_stress are on the kill list for gen_z_student persona (`catalog_generation_config.yaml` kill_list includes `{topic: financial_anxiety, persona: gen_z_student}`) | MISALIGNMENT -- research says 59% of Gen Z cite financial stress, but the catalog KILLS this combination |
| ADHD is #1 Gen Z mental health search after anxiety | adhd_focus has only 4 titles in W14, none specifically for gen_z_student persona. The strong_clusters list does not pair adhd_focus with gen_z_student. | GAP |
| Gen Z discovers books via TikTok first | BookTok-ready titles exist but gen_z_student-specific titles are underproduced | GAP |

**CRITICAL FINDING: The kill_list in catalog_generation_config.yaml KILLS financial_anxiety and financial_stress for gen_z_student. But gen_z_student_persona_research.md shows 59% of Gen Z students cite financial stress as a top concern. The kill list directly contradicts the research.** This needs immediate review.

### 2.7 48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md

| Spec Element | Catalog Support | Status |
|-------------|----------------|--------|
| 30-50 social posts per book | The catalog produces 360 books/week = 10,800-18,000 social posts/week. Content surplus is massive. | ALIGNED |
| CTA pointing to freebie landing page | PROBLEM: CTAs point to `brand-admin-onboarding.pages.dev/free/{slug}`. But the catalog produces no freebie content directly. Freebies are generated separately as companion workbooks. If the companion pipeline is not matched 1:1 with book production, CTAs will 404. | RISK |
| Email proof loop E1-E5 auto-triggered by freebie downloads | Requires freebie traffic. Without permafree books, freebie downloads depend entirely on organic social reach. | DEPENDENT ON GAP |
| Auto-approve ON (posts go live without admin review) | No catalog dependency -- this is a 48 Social config. But the risk is that 10,000+ posts/week going live without review could include titles with issues. | OPERATIONAL RISK |
| MP4s deleted from R2 on Sunday 23:59 UTC | The catalog's weekly cycle produces content on Monday. 48 Social must pull all 1,800 videos within 6 days. At scale this is a logistics concern. | OPERATIONAL RISK |

### 2.8 daily_market_intelligence.yaml

| Intelligence Stream | Catalog Connection | Status |
|--------------------|-------------------|--------|
| Trending topics -> add to candidate_topics queue | The config exists but the catalog's topic list (17) has not expanded to 20-22 as the gap analysis recommends | GAP |
| EI v2 signal scoring with 0.3 trending topic weight | No evidence in the W14 queue output that trending topics influenced this week's production | UNCLEAR |
| Max mix shift: 10% per week | Good governance constraint. At 360 titles, max 36 could shift topic allocation per week. | ALIGNED |
| Per-lane market signals (2 lanes/day rotation) | The daily intelligence system is designed but there's no feedback loop visible in the W14 queue showing lane-specific adaptation | GAP |

---

## 3. Keyword-to-Title Alignment

### 3.1 Title Template Keyword Density

The `catalog_generation_config.yaml` title_templates provide 3 title+subtitle pairs per topic. The question: do these use the highest-volume keywords from search_behavior_title_strategy_research.md?

| Topic | Top Keywords (from research) | Title Template Keywords | Match Score |
|-------|------------------------------|------------------------|-------------|
| anxiety | "anxiety," "nervous system," "calm," "relief," "high functioning anxiety" | Subtitles include "Nervous System Guide," "Calm Anxiety," "High-Functioning Anxiety" | 5/5 |
| burnout | "burnout recovery," "work exhaustion," "hustle culture," "moral injury" | Subtitles include "Burnout Recovery," "Work Exhaustion." Missing "moral injury" | 3/5 |
| sleep_anxiety | "can't sleep," "insomnia," "racing thoughts," "3am anxiety" | Subtitles include "Insomnia," "Racing Thoughts." Title "The 3 AM Mind" nails #5 search | 5/5 |
| imposter_syndrome | "imposter syndrome," "feeling like a fraud," "self doubt," "confidence" | Title "You're Not a Fraud" nails the exact pain-state search. Subtitles have "Imposter Syndrome," "Worth" | 5/5 |
| social_anxiety | "social anxiety," "overcoming shyness," "phone anxiety," "making friends" | Subtitles have "Social Anxiety Recovery," "Quiet People," "Confidence." Missing "phone anxiety," "making friends" | 3/5 |
| self_worth | "self esteem," "self worth," "how to love yourself," "confidence," "feeling worthless" | Subtitles have "Self-Esteem," "Self-Love," "Confidence." Missing EXACT phrase "how to love yourself" | 3/5 |
| boundaries | "setting boundaries," "how to say no," "people pleasing," "codependency" | Subtitles have "Setting Boundaries," "People Pleasers," "Without Guilt." Strong match | 5/5 |
| grief | "grief," "coping with loss," "losing loved one" | Subtitles have "Grief," "Loss," "Healing." Excellent match | 5/5 |
| overthinking | "stop overthinking," "racing thoughts," "quiet mind," "analysis paralysis" | Subtitles have "Stop Overthinking," "Racing Mind," "Analysis Paralysis" | 5/5 |
| somatic_healing | "nervous system regulation," "somatic exercises," "vagus nerve," "body trauma" | Subtitles have "Nervous System Recovery," "Somatic Guide," "Trauma Release." But "vagus nerve" is only in keywords, not titles | 4/5 |
| depression | "depression," "feeling numb," "no motivation," "can't get out of bed" | Subtitles have "Healing Depression," "Finding Hope." Missing "no motivation," "can't get out of bed" -- highest-intent pain states | 2/5 |
| courage | "courage," "afraid of failure," "fear of change," "fear holding me back" | Subtitles have "Courage," "Facing the Unknown." Missing FEAR-FIRST language. Research says people search their FEAR not "courage" | 2/5 |
| compassion_fatigue | "compassion fatigue," "caregiver burnout," "empathy exhaustion," "moral injury" | Subtitles have "Compassion Fatigue," "Emotional Exhaustion." Missing "caregiver burnout" (the laypeople's term) | 3/5 |
| financial_anxiety | "money anxiety," "financial stress," "money shame," "broke and scared" | Subtitles have "Financial Anxiety," "Financial Peace," "Money Shame." "Broke and Breathing" uses financial pain state | 4/5 |
| adhd_focus | No title_templates exist in catalog_generation_config.yaml | MISSING ENTIRELY | 0/5 |
| mindfulness | No title_templates exist in catalog_generation_config.yaml | MISSING ENTIRELY | 0/5 |

**Average keyword-to-title alignment: 3.4/5** (excluding topics with no templates: 3.8/5 for the 15 that exist)

### 3.2 Subtitle Optimization Issues

1. **"-- A Quick Guide" suffix wastes 16 characters.** Amazon allows 200 total. Every character matters for keyword insertion.
2. **Subtitles use {topic} placeholder verbatim.** Example: "A Nervous System Guide to {topic} Recovery" becomes "A Nervous System Guide to Anxiety Recovery." The word "anxiety" appears as the raw topic slug. This works for some topics but breaks for others -- "A Nervous System Guide to Sleep Anxiety Recovery" is awkward. Need per-topic subtitle variants, not mechanical substitution.
3. **No persona-specific subtitles.** The research recommends audience-first subtitles ("A Millennial and Gen Z Guide to...") but all subtitle_patterns are generic.

---

## 4. Persona-Market Fit Validation

### 4.1 Persona x Topic Mix vs Research

**gen_z_student: Research says TOP DEMAND for...**

| Topic | Research Demand Signal | Catalog Coverage (W14 per marketing analysis) | Verdict |
|-------|----------------------|------------------------------------------------|---------|
| Anxiety (general) | 60%+ diagnosed; #1 condition | Present but exact count unclear across brands | CHECK |
| Social anxiety | #1 subtype for Gen Z; "phone anxiety" trending | Only 1 title in marketing analysis findings | SEVERELY UNDERWEIGHT |
| Academic burnout | Massive search category for students | 0 titles | MISSING |
| ADHD/focus | #1 Gen Z mental health search after anxiety | 0 titles for gen_z_student specifically | MISSING |
| Financial stress | 59% cite as top concern | KILLED by catalog kill_list | CONTRADICTS RESEARCH |
| Sleep anxiety | Epidemic levels in students | Only 1 title | UNDERWEIGHT |
| Imposter syndrome | Peaks in September (school year start) | Only 1 title | UNDERWEIGHT |
| Self-worth / self-esteem | "How to love yourself" massive search | Only 2 titles | UNDERWEIGHT |
| Loneliness/isolation | 74% of Gen Z report regular loneliness | Topic does not exist in catalog | MISSING TOPIC |
| Overthinking | Top Gen Z concern | 7 titles | ALIGNED |
| Boundaries | High resonance | 7 titles | ALIGNED |

**Verdict: gen_z_student is the most misaligned persona in the catalog.** Research shows this is an 83M+ addressable market with distinct needs, but the catalog treats it as a secondary persona with minimal topic coverage.

**corporate_managers: Research says...**

| Topic | Research Demand | Catalog Coverage | Verdict |
|-------|----------------|------------------|---------|
| Burnout / work stress | HIGH | Multiple brands cover this heavily | OVERWEIGHT |
| Anxiety (workplace) | HIGH | 21 titles per marketing analysis | OVERWEIGHT relative to other personas |
| Imposter syndrome | HIGH | Strong coverage | ALIGNED |
| Sleep anxiety | MEDIUM-HIGH (stress-driven insomnia) | Present | ALIGNED |

The marketing analysis flagged corporate_managers at 67 titles (18.6% of catalog). While corporate managers buy self-help, this concentration creates internal competition. The research does not identify corporate managers as the highest-demand persona -- Gen Z and millennial women are larger addressable markets.

**Verdict: corporate_managers is overweighted relative to research-derived demand signals. Should be reduced from 18.6% to ~12-14% with reallocated titles going to gen_z_student and working_parents.**

### 4.2 High-Demand Persona x Topic Combos Missing from Catalog

Based on cross-referencing gen_z_student_persona_research.md with global_topic_gap_analysis.md:

1. **gen_z_student x social_anxiety** -- 60%+ diagnosed anxiety, social anxiety is #1 subtype. Only 1 title.
2. **gen_z_student x academic_burnout** -- Not a separate topic. Should be a burnout variant for student persona. 0 titles.
3. **gen_z_student x ADHD** -- #1 search after anxiety. 0 titles.
4. **gen_z_student x financial_stress** -- 59% cite it. Actively KILLED by config.
5. **gen_z_student x loneliness** -- 74% regularly lonely. Topic does not exist.
6. **working_parents x burnout** -- 0 titles per marketing analysis. Parenting burnout is a massive category.
7. **healthcare_rns x depression** -- 0 titles. Healthcare worker depression is 3x general population.
8. **educators x burnout** -- 0 titles. Teacher burnout is #1 education search.
9. **first_responders x grief** -- 0 titles. Line-of-duty death grief is acute in this persona.
10. **gen_z_professionals x burnout** -- 0 titles. Early-career burnout is a massive emerging category.

---

## 5. Pricing vs Research

### 5.1 Price Ladder Assessment

| Catalog Tier | Price | Research Validation | Verdict |
|-------------|-------|---------------------|---------|
| Micro ($0.99) | $0.99 | Correct for cold-start. Amazon ACoS breakeven at $0.99 is ~35% -- tight but viable as loss leader. Research confirms $0.99 minimizes buyer risk for first purchase. | ALIGNED |
| Standalone ($2.99) | $2.99 | Research sweet spot for impulse self-help purchases. $2.09 royalty at 70% rate. Amazon ACoS breakeven at ~70% -- very achievable. | ALIGNED |
| Series ($3.99) | $3.99 | Justified by series lock-in. Research shows series readers are highest LTV. $2.79 royalty provides good Amazon ad margin. | ALIGNED |
| Extended ($9.99) | $9.99 | Appropriate for 2hr audiobook format. Aligned with Audible pricing norms. | ALIGNED |
| Permafree ($0.00) | MISSING | Research says this is the #1 acquisition strategy. marketing_plan.yaml specifies it. catalog_generation_config.yaml configures it. But W14 queue produces ZERO. | CRITICAL GAP |
| Mid-tier ($4.99-$7.99) | MISSING | No product fills the gap between $3.99 and $9.99. Research suggests "complete guide" format at $4.99-$5.99 would capture upgrade buyers. | GAP |
| Premium ($14.99-$24.99) | MISSING from W14 | weekly_queue_config.yaml lists deep_book_4h at $17.99 and deep_book_6h at $24.99. Zero produced in W14. | GAP |
| Bundle ($6.99-$8.99) | MISSING | Research says bundles convert at 2-3x single title rates. Zero bundle products in the catalog. | GAP |

### 5.2 Permafree Cold-Start Alignment

The advertising_roi_research.md is unambiguous: email list is the #1 organic growth metric. Every 1,000 subscribers = 50-150 sales per launch. The permafree book -> email capture -> proof loop E1-E5 is the designed acquisition funnel.

The catalog_generation_config.yaml correctly specifies `book_1_price_override: 0.00`.

**But the W14 weekly production queue produces only "Book 4" series installments. No Book 1s appear in the queue. This means the permafree funnel has no new content feeding it.**

Resolution: The queue needs to generate NEW series (not just continuing existing ones) or produce standalone permafree titles dedicated to email capture.

### 5.3 Pricing Gaps Identified by Research

1. **No KDP Select strategy.** Research mentions KDP Select 90-day enrollment for promotional pricing (countdown deals, free promotions). The catalog config has no KDP Select toggle or promotional pricing layer.
2. **No promotional pricing calendar.** The publishing_cadence_research.md includes seasonal calendars (Mental Health Awareness Month in May, back-to-school in September). The catalog has no mechanism to drop prices during high-demand periods.
3. **No audiobook-specific pricing.** The extended_book_2h at $9.99 is one price point. Audible uses a credit-based system. The catalog does not account for Audible's credit-equivalent pricing.

---

## 6. Publishing Cadence Alignment

### 6.1 Does 15 titles/brand/week Align With Platform Limits?

| Platform | Safe Weekly Max (per account) | Titles Needed (360/week) | Accounts Needed | Status |
|----------|-------------------------------|--------------------------|-----------------|--------|
| Amazon KDP | 10/week (2/day x 5 days) | 360 | 36 accounts | HEAVY operational load |
| Apple Books | 25-40/week | 360 | 9-15 accounts | Manageable |
| Google Play | 50/week | 360 | 8 accounts | Most feasible |
| Kobo | 25/week (500-title account cap) | 360 | 15 accounts, rotating | Complex |
| D2D (aggregator) | 40/week | 360 | 9 accounts | Efficient |

**CRITICAL: 360 titles/week on Amazon alone requires 36 separate KDP accounts at the safe ceiling of 10/week/account.** This is the hardest operational constraint.

### 6.2 Ramp-Up Compliance

The publishing_cadence_research.md specifies a 12-week ramp for new KDP accounts:
- Weeks 1-4: 5-10 titles/week
- Weeks 5-8: 10-15 titles/week
- Weeks 9-12: 15-18 titles/week
- Week 13+: 15/week sustained

If launching 36 accounts in parallel:
- Month 1: 36 accounts x 5-10/week = 180-360 titles/week (50-100% capacity)
- Month 2: 36 accounts x 10-15/week = 360-540 (at target)
- Month 3: Full velocity achievable

**The catalog config does not account for ramp-up.** It assumes 15/brand/week from day 1. If the accounts are new, Month 1 will produce roughly half the planned output.

### 6.3 Format Mix vs Platform Preferences

The W14 queue produces:
- 192 short_book_30 (53.3%) -- ebook optimized
- 72 micro_book_15 (20%) -- ebook + audio
- 48 standard_book series (13.3%) -- ebook + audio
- 24 micro_book_20 (6.7%) -- ebook
- 24 extended_book_2h (6.7%) -- audiobook optimized

Research insights on format preferences:
- Amazon KDP favors longer content (30+ pages) for better search ranking
- Audiobook platforms (Audible, Google Play) prefer 2+ hour content
- Google Play Books has no page minimum, making it best for micro content

The catalog is HEAVILY weighted toward short ebooks (80% are under 30 pages). Only 24 extended titles (6.7%) serve the audiobook market. This underserves Audible, which is one of the largest self-help platforms.

**Verdict: Format mix is ebook-first but audiobook-light. Consider increasing extended_book_2h from 24 to 48 titles (from 6.7% to 13%) to serve the audiobook market.**

---

## 7. Competitive Gap Check

### 7.1 Opportunities Identified by Research

| Opportunity (from research) | Catalog Response | Status |
|-----------------------------|-----------------|--------|
| Grief + specific loss types (miscarriage, pet loss, divorce) are blue ocean | 63 grief titles produced (HIGHEST topic count) but no evidence of sub-type specialization. All appear to be general grief. | PARTIAL -- volume is there but specificity is missing |
| Compassion fatigue for non-healthcare (educators, social workers, nonprofit) | 14 titles. The kill_list blocks compassion_fatigue x entrepreneurs but does allow educators. However, 0 titles for educators x compassion_fatigue appear in the queue. | GAP |
| Sleep anxiety + somatic crossover | Both topics exist separately. The title "Held by the Body: A Somatic Healing Guide for Stress, Trauma, and Anxiety" bridges somatic + anxiety. But no title bridges somatic + sleep specifically. | GAP |
| Financial anxiety for specific demographics (nurses, teachers) | 12 total financial titles. No evidence of persona-specific financial titles. | GAP |
| ADHD as full topic (market doubling to $7.55B by 2033) | 4 titles. Dramatically underweight vs. opportunity size. | SEVERELY UNDERWEIGHT |
| People-pleasing / codependency (dedicated topic) | Not a topic. Covered partially by boundaries keywords. | GAP |
| Loneliness / isolation (74% Gen Z lonely, $500B loneliness economy) | Topic does not exist. | CRITICAL GAP |

### 7.2 What the Catalog Captures Well

1. **Nervous system / somatic angle as differentiator.** Research shows this is a 15%+ YoY growth category with $12.4B projected market by 2032. The catalog has 19 somatic_healing titles + somatic language in anxiety and burnout subtitles. This positions the brand catalog distinctly from generic self-help.

2. **Emotional / metaphorical title strategy.** The 77% AI-saturation finding means most competitors have robotic, formulaic titles. Our titles ("The Weight of Gone," "Still Here Without You," "Color Returns") sound distinctly human. This is a strategic advantage.

3. **Price laddering for funnel economics.** $0.99 -> $2.99 -> $3.99 -> $9.99 creates a clear upgrade path. The margin at $2.99 ($2.09 royalty) makes Amazon ads viable.

### 7.3 What is Still Missing

1. **Habits/productivity topic** -- massive Amazon category (Atomic Habits adjacency), zero coverage.
2. **Relationships/communication** -- boundaries is adjacent but not the same. "Healthy communication" is a distinct high-volume search.
3. **Meditation/mindfulness as standalone** -- 6 titles (mindfulness) just added as VIABLE. Needs 20+ for category credibility.
4. **Trauma recovery** -- somatic_healing partially covers this. But "trauma" as a keyword drives $1.8B PTSD market and dedicated Amazon categories.
5. **Anger management** -- zero coverage. Dedicated Amazon subcategory with distinct audience (men, teens, parents).

---

## 8. VERDICT + Action Items

### Overall Alignment Score: 5.5/10

The catalog is a well-engineered production machine with correct structural fundamentals (price ladder, format mix, emotional title strategy, somatic differentiation). But it has critical strategic gaps that undermine the marketing plan's effectiveness.

**What drags the score down:**
- Permafree funnel is configured but not executing (kills the #1 acquisition strategy)
- 5 of 7 high-priority topics from gap analysis still missing
- gen_z_student persona severely underweight despite being the largest addressable market
- Kill list contradicts research (financial stress killed for gen_z_student when 59% cite it)
- Keyword cannibalization across identical 7-keyword strings per topic
- Grief is the most-produced topic (63 titles) despite not being the highest-demand topic
- No premium tier ($14.99+) or bundles in current queue
- Publishing cadence assumes full velocity without ramp-up planning

### Top 5 Misalignments to Fix (Priority Order)

**1. PERMAFREE FUNNEL IS BROKEN (P0)**
- The marketing plan, advertising research, and catalog config all specify permafree as the #1 acquisition strategy. The W14 queue produces zero $0.00 titles. All series entries are Book 4 -- no new series with Book 1 at $0.00 are being started.
- FIX: Add a queue rule that every brand must have at least 1 active series with Book 1 at $0.00 on Google Play/Kobo (for Amazon price-match). Produce new series, not just continuation installments.

**2. GEN_Z_STUDENT PERSONA IS STARVED (P0)**
- 83M+ addressable market. Only 24 titles. Missing social_anxiety, academic_burnout, ADHD, and financial_stress (actively killed).
- FIX: Remove financial_anxiety and financial_stress from the gen_z_student kill list. Add gen_z_student to STRONG clusters for social_anxiety, burnout, sleep_anxiety, imposter_syndrome, and self_worth. Target 50+ titles.

**3. KEYWORD CANNIBALIZATION ACROSS FORMAT TYPES (P0)**
- All titles in a topic share identical 7-keyword strings. Amazon's algorithm will suppress duplicates.
- FIX: Create 4 keyword variants per topic (one per content_type: micro=pain-state, standalone=category, series=method, extended=comprehensive). The search_behavior_title_strategy_research.md already provides the keyword tiers needed.

**4. TOPIC DISTRIBUTION DOES NOT MATCH DEMAND (P1)**
- grief has 63 titles (highest). anxiety has 41. adhd_focus has 4. This does not match search volume data. Anxiety and burnout are VERY HIGH volume; grief is HIGH but lower. ADHD is VERY HIGH growth.
- FIX: Implement topic caps per brand. grief should be capped at 2 titles/brand (48 total). adhd_focus should be raised to at least 1 title/brand (24 total). The topic_cap_per_brand mechanism already exists (from recent commit `42a3b5fe8c`).

**5. MISSING HIGH-PRIORITY TOPICS (P1)**
- People-pleasing/codependency, trauma recovery, anger management, loneliness/isolation are all HIGH-priority recommendations from gap analysis with zero catalog representation.
- FIX: Add at least people-pleasing and loneliness as new topics in the next config update. These can reuse existing boundary and social_anxiety atoms with ~30% new content per the gap analysis.

### Top 5 Things the Catalog Gets Right

**1. EMOTIONAL TITLE STRATEGY IS A COMPETITIVE MOAT**
- In a market where 77% of titles are AI-generated with robotic phrasing, our titles ("The Weight of Gone," "Safe Enough," "Own Your Seat," "You're Not a Fraud") sound distinctly human. The bestseller_titles_seo_covers_research.md explicitly identifies this as the #1 differentiation strategy, and the catalog implements it well. The top 5 titles score 4-5/5 on BookTok readiness.

**2. SOMATIC/NERVOUS SYSTEM POSITIONING IS FIRST-MOVER**
- The somatic therapy market is projected to reach $12.4B by 2032 (17.5% CAGR). "Nervous system regulation" has 5x search growth since 2023 and 246K monthly Google searches. The catalog correctly threads somatic language through anxiety, burnout, and sleep_anxiety subtitles -- not just the somatic_healing topic. This positions the entire brand portfolio as "body-based wellness" rather than generic self-help.

**3. PRICE LADDER ECONOMICS ARE SOUND**
- $0.99 micro books as review generators and cold-start funnels -> $2.99 standalones as the revenue workhorse ($2.09 royalty, 70% ACoS breakeven) -> $3.99 series for LTV -> $9.99 extended for premium buyers. The margin structure supports profitable Amazon advertising at the $2.99 and $3.99 tiers. The advertising_roi_research.md validates these price points.

**4. 48 SOCIAL CONTENT SURPLUS ELIMINATES MARKETING BOTTLENECK**
- 360 titles/week x 30-50 posts per book = 10,800-18,000 social posts/week. The marketing plan calls for 2-3 posts/day/platform/brand = ~10/day/brand = 70/week/brand = 1,680/week total. Content supply exceeds demand by 6-10x. This means 48 Social can cherry-pick the best content and A/B test aggressively without ever running out of material.

**5. KILL LIST AND DUPLICATION PREVENTION ARE WELL-DESIGNED**
- The kill_list prevents persona-inappropriate content (financial_anxiety for gen_alpha_students is correctly killed). The duplication_prevention system with `same_topic_persona_engine_format_seed: NEVER_REPEAT` prevents exact duplicates. The variation_knobs (5 journey shapes, 7 motifs, 3 book structures) create legitimate differentiation. The system can produce 588 unique products per brand before repeating -- nearly a year of content at 15/week.

---

## Appendix: Data Sources Cross-Reference

| Source | Key Data Points Used |
|--------|---------------------|
| marketing_plan.yaml | Channel priorities, value ladder, 48 Social spec, ad budget scenarios, permafree strategy |
| bestseller_titles_seo_covers_research.md | Title formulas, AI-signal words, keyword density, character limits |
| search_behavior_title_strategy_research.md | Per-topic search volumes, pain-state searches, keyword gaps |
| advertising_roi_research.md | CPC/CPM benchmarks, ROAS targets, permafree ROI, email list economics |
| publishing_cadence_research.md | Platform upload limits, ramp-up schedules, safe ceilings |
| global_topic_gap_analysis.md | Missing topics, topic merge recommendations, priority rankings |
| gen_z_student_persona_research.md | 83M+ market, demographic data, topic preferences, financial stress data |
| 48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md | Content repurposing pipeline, CTA patterns, email automation |
| daily_market_intelligence.yaml | Intelligence loop design, EI v2 integration, adaptation constraints |
| weekly_queue_config.yaml | 15 titles/brand, mix ratios, strong/viable clusters, kill list |
| catalog_generation_config.yaml | Title templates, keyword templates, pricing, kill list, locale pricing |
| W14 queue dry-run output | 360 titles, 24 brands, actual format/price/topic distribution |

---

*End of cross-analysis. File: `artifacts/catalog/catalog_vs_marketing_alignment_report.md`*
*Analyst: Pearl_Marketing + Pearl_Research*
*Date: 2026-04-05*

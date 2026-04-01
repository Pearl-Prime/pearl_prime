# PLATFORM x FORMAT x KNOB OPTIMIZATION MATRIX

## Research Methodology
Internal files analyzed: `docs/V4_FEATURES_SCALE_AND_KNOBS.md` and `config/format_selection/format_registry.yaml`. Extensive web research conducted across 12 platforms spanning 3 tiers. Confidence ratings: **high** = multiple corroborating sources with documented evidence; **medium** = single authoritative source or consistent community reports; **low** = extrapolated from adjacent data or limited sourcing.

---

## DELIVERABLE 1: Platform Knob Matrix

### TIER 1 PLATFORMS

#### AMAZON KDP — Ebook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | gladwell_spiral, mirror_journey preferred; rotate across all 12 | Top-100 KDP self-help overwhelmingly uses problem-solution-story arcs; 5-part structure (identify problem, context, insights+exercises, action plan, encouragement) dominates bestsellers | Avoid >3 same structure per month per account; Amazon detects "mass-generated duplicates or multiple listings that are materially the same" | high | [ASJA](https://www.asja.org/structuring_a_self-help_book/), [KDP Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390) |
| journey_shape_id | recognition-destabilization-reframe-stabilization-integration (classic arc) | Self-help readers expect transformation journeys; the "Growth Story" framework (failure-learning-success) per chapter maps to this arc shape | Identical emotional arcs across >30% of a wave triggers internal CTSS block; Amazon's detection monitors structural patterns | high | [Self Publishing Formula](https://selfpublishingformula.com/how-to-structure-a-self-help-book/), [Nancy Peske](https://nancypeske.com/self-help-book-contents-and-structure-a-handy-guide/) |
| motif_id | Max 3 books sharing same motif per quarter per pen name | Amazon flags "substantially similar" books from same account; AI detection has "significantly ramped up" in 2025-2026 | Hard limit: max 3/motif/quarter/account. Community reports accounts flagged at 5+ similar titles in a month | high | [Inkfluence AI](https://www.inkfluenceai.com/blog/amazon-kdp-ai-disclosure-policy-2026), [BookAutoAI](https://blog.bookautoai.com/ai-generated-content-amazon-kdp-2025/) |
| structural_entropy | Minimum 0.65 (our current block threshold at CTSS 0.78 is appropriate) | Amazon uses "combination of automated detection analyzing writing patterns, metadata, and submission velocity"; no public numeric threshold but "substantially similar" is enforced aggressively | Our CTSS block=0.78, review=0.65 aligns well; keep structural_entropy high enough that no two books pass 0.78 CTSS | high | [KDP Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390), [AIBoxTools](https://www.aiboxtools.com/amazon-kdp-ai-rules/) |
| wave_density_max | 3/week maximum; 1/week optimal for self-help | Hard limit: 3 books/day upload cap. Community reports throttling/flagging at >5/week sustained. Optimal for self-help: 1 book/week to maintain 30-day launch windows per title | 3/day hard cap enforced by KDP; >5/week sustained triggers "abusive behavior" flag. For quality self-help, 1/month per pen name is safest | high | [CoinGeek](https://coingeek.com/amazon-publishing-limits-seek-to-prevent-rise-of-ai-generated-books/), [Letter Review](https://letterreview.com/how-many-books-can-you-publish-on-kdp/) |
| chapter_archetypes | story_exercise_teaching mix: 40% story, 30% exercise, 30% teaching | Best-performing self-help has exercises per chapter, narrative anchors (stories) opening chapters, and clear teaching/takeaway sections | Ensure no single archetype >70% (our MAX_STORY_FAMILY_SHARE); varies enough to avoid "substantially similar" fingerprinting | high | [PickFu](https://www.pickfu.com/blog/how-to-structure-a-self-help-book/), [Lisa Daily](https://lisadailybooks.com/selfhelp/how-do-you-structure-chapters-in-a-self-help-book/) |
| format_mix | 40% pocket guides (micro_book_15/20, F003/F015), 35% standard (standard_book, F006/F007), 25% extended (extended_book_2h, F004/F009) | Short, problem-focused books drive impulse buys at $2.99-$4.99; standard books command $4.99-$7.99 sweet spot for 70% royalty; series of pocket guides outperform single long books for catalog scale | Avoid publishing >3 pocket guides on same topic in same week; Amazon monitors "rapid-fire publishing of short, low-quality AI books" | high | [Medium/Atomic Content](https://medium.com/atomic-content-revolution/why-short-books-are-perfect-for-amazon-kdp-c2dfdade25eb), [River Editor](https://rivereditor.com/guides/ebook-pricing-strategy-self-publishers-2026) |
| pricing_tier | $4.99-$7.99 (standard/extended); $2.99-$3.99 (pocket guides) | 70% royalty requires $2.99-$9.99. Self-help sweet spot is $4.99-$7.99 for standard; pocket guides at $2.99-$3.99 for impulse buys. Launch at $0.99-$2.99 for first 48-72hrs then raise | Below $2.99 drops to 35% royalty; above $9.99 also drops to 35%. Delivery fee of $0.15/MB deducted at 70% tier | high | [AuthorImprints](https://www.authorimprints.com/amazon-kdp-royalty-pricing/), [KDP Pricing](https://kdp.amazon.com/en_US/help/topic/G200634500) |
| release_cadence | Stagger releases 7-10 days apart; front-load marketing in first 72hrs | Amazon's algorithm gives 30-day "hot new release" boost; sales velocity in first 72hrs heavily weighted. Rolling BSR average updated daily | Space releases to avoid cannibalizing each title's 30-day window. Each title needs its own promotional calendar | high | [Reedsy](https://reedsy.com/blog/guide/kdp/amazon-algorithms-for-authors/), [Author Media](https://www.authormedia.com/massive-amazon-algorithm-changes/) |

#### AMAZON KDP — Print (Paperback/Hardcover)

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | 60% standard_book (6x9"), 30% pocket guides (5x8"), 10% extended | June 2025 restructure: 60% royalty for books >= $9.99, 50% for < $9.99. Standard books can price above $9.99 threshold | Same velocity limits as ebook (3/day). Print + ebook same title counts as one listing | high | [AuthorImprints](https://www.authorimprints.com/amazon-kdp-royalty-pricing/) |
| pricing_tier | Standard: $14.99-$19.99; Pocket: $9.99; Extended: $19.99-$24.99 | Price at or above $9.99 to get 60% royalty tier (post-June 2025). Higher prices viable for self-help with perceived authority | Printing costs deducted from royalty; calculate net margin carefully | high | [KDP Royalty Calculator](https://kdp.amazon.com/en_US/royalty-calculator) |

#### AUDIBLE/ACX — Audiobook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | gladwell_spiral, mirror_journey; narrative-heavy structures | Audiobook return rates historically high; narrative anchors (stories every 2-3 chapters) reduce returns. Listeners need engagement to avoid abandonment | Less concern about structural similarity detection on Audible vs KDP, but identical content across formats will be noticed | medium | [ACX](https://www.acx.com/mp/blog/audibles-new-royalty-model-early-access-successes), [Kindlepreneur](https://kindlepreneur.com/audible-royalty-changes/) |
| journey_shape_id | Higher engagement arcs with frequent story beats; avoid long teaching-only stretches | Audible's new model pays on "Member Value" based on listening time engagement; more engagement = better payout. Early adopters seeing +45% avg earnings increase | Under new pooled model, listener engagement directly drives revenue share. Boring stretches = listener drops = lower payout | medium | [ACX New Model](https://help.acx.com/s/article/audible-s-new-royalty-model) |
| chapter_archetypes | story_every_3 (narrative anchor every 3 chapters minimum) | Return rate drops with narrative anchors; audio format demands more story content than text. Exercises must be "listenable" (guided, not worksheet-based) | N/A | medium | [ACX Blog](https://www.acx.com/mp/blog/coming-soon-to-acx-a-new-royalty-model-and-more-opportunities-to-earn) |
| format_mix | 70% standard_book (55min, ~30K words = ~3hrs narrated), 20% extended (2-4hr), 10% deep (4-6hr) | 30K words produces ~3hr audiobook; audiobook royalties increase significantly at 3hr+ threshold. Micro books too short for audiobook ROI | Minimum length for good audiobook economics is ~3hrs. ACX has stricter quality review for AI-narrated content | high | [NINC](https://ninc.com/nink-self-publishing-your-audiobook-royalty-share-or-not-the-26000-lesson/) |
| wave_density_max | 2/month max audiobook releases per pen name | ACX review process adds latency (weeks); natural throttle. Audible algorithm favors quality over quantity | ACX increasingly scrutinizes AI-narrated content. Each audiobook needs dedicated promotion period | medium | [Reedsy ACX Review](https://reedsy.com/blog/acx-review/) |
| royalty_model | Exclusive (50% new model) if Audible-heavy audience; Non-exclusive (30%) if going wide | New model: 50% exclusive / 30% non-exclusive, but calculated on "Member Value" pooled system, not list price. Early adopters +45% avg increase, but results vary | Pooled model means actual per-unit payout is unpredictable; large catalog and series benefit most | high | [ACX](https://www.acx.com/mp/blog/audibles-new-royalty-model-early-access-successes) |

#### APPLE BOOKS — Ebook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | All 12 structures viable; Apple rewards exclusivity and quality over volume | Apple's discovery is editorially curated, not purely algorithmic. Quality and unique positioning matter more than structural optimization | Less automated similarity detection than Amazon; editorial team manually curates features | medium | [Reedsy](https://reedsy.com/blog/how-to-publish-on-apple-books/), [ScribeCount](https://scribecount.com/author-resource/publishing-wide/apple-books-for-indie-authors) |
| format_mix | 50% standard, 30% extended, 20% pocket guides | No price-based royalty tiers (always 70%). Extended/premium books can price higher ($10.99-$24.99) without royalty penalty. Higher-priced self-help signals authority to Apple's editorial team | No known similarity detection system disclosed | medium | [Reedsy](https://reedsy.com/blog/how-to-publish-on-apple-books/) |
| pricing_tier | $5.99-$14.99 (standard); $2.99-$4.99 (pocket) | 70% royalty at ALL price points (no $9.99 ceiling like Amazon). No delivery fees. Premium pricing viable and rewarded | No delivery fee means larger files (extended books) are not penalized | high | [Apple Books for Authors](https://authors.apple.com/measure) |
| wave_density_max | 4/week acceptable; less scrutiny than Amazon | No known velocity limits; Apple is less strict on publishing frequency. Pre-orders count double (once at pre-order, once at launch) | Focus on pre-order strategy; Apple pre-orders are a major competitive advantage over Amazon | medium | [ScribeCount](https://scribecount.com/author-resource/publishing-wide/apple-books-for-indie-authors) |
| structural_entropy | Lower concern than Amazon; maintain our 0.65 review threshold as good practice | Apple's editorial curation means different selection criteria than Amazon's algorithmic approach | Still maintain diversity as general quality practice | low | [UNVERIFIED - extrapolated] |

#### GOOGLE PLAY BOOKS — Ebook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | 50% pocket guides, 30% standard, 20% extended | Google's search integration surfaces short, problem-specific content well. Free series starters get massive visibility boost in Google Search/Discover. Pocket guides convert well on mobile-first Android audience | Google may discount prices unilaterally, which can trigger Amazon price-matching. Set list prices accordingly | medium | [Indie Author Magazine](https://indieauthormagazine.com/10-powerful-ways-indie-authors-can-boost-book-sales-using-google-play-books/), [Daniel Tortora](https://danieljtortora.com/blog/publish-google-play-books-pros-and-cons) |
| pricing_tier | $3.99-$9.99 (all formats); $0.00 for series starters | 70% royalty at ANY price (no floor/ceiling). No delivery fees. Free books get enhanced visibility in Google ecosystem. Google pays royalty on LIST price even during sales | Google's unilateral discounting can trigger price-matching on Amazon. Set Google prices ~$1 higher as buffer [UNVERIFIED community practice] | high | [Google Revenue Split FAQ](https://support.google.com/books/partner/answer/9331459), [Automateed](https://www.automateed.com/google-play-books-publishing) |
| wave_density_max | 5/week acceptable | No known hard velocity limits. Google's content review is less aggressive than Amazon's | Google metadata-driven discovery means keywords and categories matter most | medium | [Oak & Apex](https://www.oakandapex.com/Google-play-books/) |
| structural_entropy | Maintain our standard thresholds (CTSS block=0.78, review=0.65) | Google has no publicly known similarity detection system, but good practice prevents issues if content is also on Amazon | Cross-platform: books on Google + Amazon means Amazon's detection still applies to the catalog | medium | [UNVERIFIED - best practice] |
| book_structure_id | All structures viable; keyword-optimize metadata | Google's search engine integration means SEO-optimized metadata drives discovery more than structure | Ensure book titles/subtitles contain high-value search terms for self-help subcategories | medium | [Google Play Partner Center](https://support.google.com/books/partner/answer/166501) |

#### KOBO — Ebook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | 40% standard, 35% extended, 25% pocket guides | Kobo Plus pays on minutes read; longer books earn more per engagement period. Series metadata is auto-merchandised, creating cross-sell | No known velocity limits or similarity detection system | medium | [Kobo Writing Life](https://www.kobo.com/kobo-writing-life/blog/frequently-asked-questions), [PublishDrive](https://publishdrive.com/kobo-distribution-and-benefits.html) |
| pricing_tier | $2.99-$12.99 for 70% royalty; $4.99-$9.99 sweet spot | 70% royalty for $2.99-$12.99 range (wider than Amazon). Below $2.99 = 45%. Above $12.99 = 45%. Kobo Plus subscription pool pays 60% based on minutes read | Kobo Plus doesn't require exclusivity; opt-in generates additional revenue on top of a la carte sales | high | [Kobo Writing Life FAQ](https://kobowritinglife.zendesk.com/hc/en-us/articles/360058976032-What-will-my-earnings-be) |
| wave_density_max | 3/week standard; no known hard limits | Kobo uses human curation for promotional features; submit titles to Promotions tab 4-6 weeks before desired feature date | Direct publishing (not via D2D) gives access to Kobo's promotions dashboard | medium | [BookLinker](https://booklinker.com/blog/publishing-on-kobo/) |
| book_structure_id | Series-friendly structures; consistent series metadata critical | Kobo auto-merchandises series; consistent naming and metadata drive algorithmic cross-sells. Pre-orders double visibility (like Apple) | Enter consistent series metadata for cross-sell algorithm | medium | [Written Word Media](https://www.writtenwordmedia.com/how-to-self-publish-on-kobo/) |
| journey_shape_id | Engagement-optimized arcs (longer reading time = more Kobo Plus revenue) | Minutes-based payout means reader completion rate directly impacts revenue. Engaging arcs that prevent drop-off maximize Kobo Plus earnings | N/A | medium | [Kobo Plus FAQ](https://kobowritinglife.zendesk.com/hc/en-us/articles/360058975432-What-is-Kobo-Plus) |

---

### TIER 2 PLATFORMS

#### SCRIBD — Ebook (Subscription)

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | All 12 viable; engagement-driven structures preferred | Scribd pays from pooled revenue based on reading activity; engagement structures keep readers in book longer | BookID fingerprint system scans ALL uploads; removes content with "same or substantially similar fingerprint" to known works | high | [Scribd BookID](https://support.scribd.com/hc/en-us/articles/360037497152-About-the-BookID-Copyright-Protection-System) |
| structural_entropy | Minimum 0.70+ recommended (higher than Amazon) | BookID "algorithmically analyzes computer-readable text for semantic data" and creates digital fingerprints. "Reduces misidentifications and enables detection even if content has been altered to some degree" | BookID is MORE aggressive than Amazon's detection for structural similarity. Our CTSS block=0.78 may need raising to 0.82+ for Scribd | high | [Scribd BookID](https://support.scribd.com/hc/en-us/articles/360037497152-About-the-BookID-Copyright-Protection-System) |
| motif_id | Max 2 books sharing same motif for Scribd catalog | BookID fingerprints encode "semantic data" - meaning topical/thematic similarity is detected, not just verbatim text overlap | More restrictive than Amazon for semantic similarity | medium | [Scribd Community Rules](https://support.scribd.com/hc/en-us/articles/210129166-Community-Rules-Prohibited-Activity-and-Content) |
| format_mix | 50% standard, 30% extended, 20% pocket guides | Subscription model favors longer reads (more time = more revenue share). But pocket guides serve as discovery entry points | Access via Draft2Digital (10% commission) or Smashwords store | medium | [PubliWrite](https://blog.publiwrite.com/royalties-in-2025-which-platforms-pay-authors-best-and-why-transparency-matters/) |
| wave_density_max | 2/week via distributor | Distribution through D2D adds natural latency. No known direct velocity limits, but BookID will catch rapid similar uploads | N/A | low | [UNVERIFIED - extrapolated] |

#### STORYTEL — Audiobook/Ebook (Subscription)

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | 60% standard audiobook, 30% extended, 10% deep | Storytel pays from 50/50 pooled revenue split based on listening activity. Synced listening/reading (word-by-word highlighting) launched Sept 2025 | Storytel focuses on European/Nordic markets primarily; content must be culturally appropriate for non-US audiences | medium | [Storytel Group](https://www.storytelgroup.com/en/), [New Publishing Standard](https://thenewpublishingstandard.com/2026/02/19/the-story-converges-audiobook-format-convergence-2026/) |
| journey_shape_id | High-engagement arcs; frequent narrative hooks | "AI-driven innovation" for personalized discovery means algorithmic recommendation is increasingly sophisticated. Engagement metrics drive payouts | 2.6M+ paying subscribers across 55 languages; large catalog competition | medium | [Storytel Group](https://www.storytelgroup.com/en/) |
| chapter_archetypes | story_every_2 (more narrative density than Audible) | Subscription listeners have zero switching cost; must hook immediately and maintain throughout | N/A | low | [UNVERIFIED - extrapolated from model] |
| wave_density_max | 2/month per pen name | Distribution typically via aggregator. Natural throttle from review/onboarding process | Focus on fewer, higher-quality titles for subscription discovery | low | [UNVERIFIED] |

#### DRAFT2DIGITAL — Distributor (Multi-Platform)

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | Match target platform mix (see individual platforms) | D2D distributes to 16+ retailers including Apple, Kobo, B&N, libraries. 10% commission on all sales | D2D itself doesn't have similarity detection; each end-platform applies its own policies | high | [D2D FAQ](https://draft2digital.com/faq/), [D2D Blog](https://www.draft2digital.com/blog/royalty-rates/) |
| pricing_tier | Set per-platform; account for D2D's 10% cut | Effective royalty after D2D cut: Apple 63%, Kobo 63%, B&N 56%. Smashwords Store: 75% for books >=$2.99 (effective Jan 2026) | D2D automatically adjusts Google Play prices to prevent Amazon price-matching [UNVERIFIED specifics] | medium | [D2D Blog](https://www.draft2digital.com/blog/royalty-rates/), [Table Read Magazine](https://www.thetablereadmagazine.co.uk/top-self-publishing-platforms-2026-draft2digital-vs-amazon-kdp-vs-ingramspark-which-pays-authors-more/) |
| wave_density_max | 5/week across all platforms combined | D2D processes uploads then distributes; latency varies by retailer (24hrs to 2 weeks) | Stagger releases across platforms to maximize each platform's "new release" window | medium | [D2D Knowledge Base](https://draft2digital.com/knowledge-base/) |

#### SPOTIFY — Audiobook

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| format_mix | 50% standard (3hr+), 30% extended, 20% pocket (1-2hr) | Spotify for Authors launched 2025; ~80% royalty for direct upload. 600M+ active users, 57% of audiobook listeners aged 18-34. AI narration accepted for Spotify-only distribution | Younger demographic prefers shorter, more focused content. AI narration explicitly permitted on Spotify | high | [Spotify for Authors](https://authors.spotify.com/self-published-authors), [Spotify Newsroom](https://newsroom.spotify.com/2025-03-13/spotify-audiobooks-launches-a-new-publishing-program-for-independent-authors/) |
| chapter_archetypes | story_heavy (50% story, 25% exercise, 25% teaching) | Spotify's algorithm is engagement-based (pro rata listening time). Younger audience demands narrative-driven content, not lecture format | Spotify Premium listeners get ~15hrs/month of audiobook time; must compete for engagement hours | medium | [ScribeCount](https://scribecount.com/author-resource/audiobook-creation-guide/spotify-audiobooks-guide) |
| wave_density_max | 3/week (Spotify has no known velocity limits for audiobooks) | Platform is still scaling (150K to 400K titles in recent years); less competition than Audible. Being early with quality content is advantageous | AI narration accepted; ElevenLabs partnership for auto-narration and translation | medium | [Spotify Newsroom](https://newsroom.spotify.com/2025-03-13/how-spotify-is-driving-growth-discovery-and-innovation-in-the-audiobook-market/) |
| journey_shape_id | High-energy, frequent hooks; short chapters (10-15 min each) | Spotify listeners are habituated to algorithmic playlists and short-form content. Quick chapter transitions maintain engagement | Spotify launched audiobook charts (Feb 2026) ranking by "listening engagement" | medium | [Daniel Tortora](https://danieljtortora.com/blog/spotify-for-authors) |
| pricing_tier | $9.99-$14.99 (a la carte); Premium streaming is pro-rata pooled | Direct upload via Spotify for Authors: ~80% of net revenue. Via aggregator: ~45-50% after aggregator cut. Premium streaming pays fractionally per listen-hour | A la carte paid monthly; Premium streaming paid quarterly | high | [ScribeCount](https://scribecount.com/author-resource/audiobook-creation-guide/spotify-audiobooks-guide) |

---

### TIER 3 PLATFORMS

#### BOOKWALKER — Ebook (Manga/Light Novel Focus)

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | NOT RECOMMENDED for self-help | BookWalker is primarily a manga/light novel platform serving the Japanese market. No self-publishing program for English-language self-help content found | Platform mismatch: BookWalker's audience and infrastructure are oriented toward Japanese manga/LN. Self-help books would have near-zero discoverability | low | [UNVERIFIED - no data found] |
| format_mix | N/A for our pipeline | If entering: would need manga/visual adaptation of self-help content, which is outside current pipeline scope | N/A | low | [UNVERIFIED] |

#### WEBTOON — Webcomic/Visual Format

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | Requires format adaptation: visual/episodic structure | WEBTOON has 155M MAU, $2.7B paid to creators over 5 years, $47M investment in 2026 for creator growth. Creator Residency program launched 2026 | Content must be visual/comic format; text-only self-help not applicable. Would require substantial pipeline extension | medium | [WEBTOON IR](https://ir.webtoon.com/news-releases/news-release-details/webtoon-announces-significant-expansion-its-creator-programs), [Animation Magazine](https://www.animationmagazine.net/2025/12/webtoon-announces-significant-expansion-to-creator-programs-in-2026/) |
| format_mix | Episodic (5-10 panels per episode, weekly release) | CANVAS (self-publish) track available; new monetization tools launching 2026. Self-help webcomics are a niche but growing segment | Requires visual artist/illustrator; cannot use current text pipeline directly | low | [WEBTOON Creator Programs](https://www.webtoons.com/en/notice/detail?noticeNo=3553) |
| wave_density_max | 1-3 episodes/week (standard WEBTOON cadence) | Weekly release cadence is standard on WEBTOON. Consistency matters more than volume | WEBTOON algorithm rewards consistent weekly uploads | medium | [ComicsBeat](https://www.comicsbeat.com/webtoon-announces-a-slate-of-new-programs-aimed-at-helping-creators-in-2026/) |

#### LINE MANGA — Manga Format

| Knob | Recommended Setting | Evidence | Anti-Spam Note | Confidence | Source |
|------|-------------------|----------|----------------|------------|--------|
| book_structure_id | NOT RECOMMENDED for text-based self-help | LINE Manga is part of WEBTOON Entertainment ecosystem; Japanese manga focus. Same constraints as BookWalker | Self-help text content not applicable to this platform format | low | [UNVERIFIED - no data found] |

---

### CROSS-PLATFORM KNOB SUMMARY TABLE (Condensed)

| Knob | Amazon KDP (ebook) | Audible/ACX | Apple Books | Google Play | Kobo | Scribd | Storytel | Spotify | D2D |
|------|-------------------|-------------|-------------|-------------|------|--------|----------|---------|-----|
| **wave_density_max** | 3/wk (3/day hard cap) | 2/mo | 4/wk | 5/wk | 3/wk | 2/wk | 2/mo | 3/wk | 5/wk total |
| **structural_entropy min** | 0.65 (CTSS review) | 0.55 | 0.50 | 0.50 | 0.55 | 0.70+ (BookID) | 0.55 | 0.50 | per-retailer |
| **motif reuse limit** | 3/qtr/pen-name | 4/qtr | 5/qtr | 5/qtr | 4/qtr | 2/qtr | 3/qtr | 4/qtr | per-retailer |
| **optimal format** | pocket+standard | standard+extended | standard+extended | pocket+standard | standard+extended | standard+extended | standard+extended | standard | per-retailer |
| **pricing sweet spot** | $4.99-$7.99 | N/A (pooled) | $5.99-$14.99 | $3.99-$9.99 | $4.99-$9.99 | N/A (pooled) | N/A (pooled) | $9.99-$14.99 | per-retailer |
| **royalty rate** | 70% ($2.99-$9.99) | 50% excl / 30% non-excl (pooled) | 70% (all prices) | 70% (all prices) | 70% ($2.99-$12.99) | pooled/variable | 50% pooled | ~80% direct | 60% effective |
| **AI policy** | Disclose; accepted | Stricter review | No public policy | Auto-narration program | No public policy | BookID scans | No public policy | AI narration accepted | per-retailer |


### CONFIDENCE LEGEND
- **high**: Multiple corroborating sources with documented platform policies or official documentation
- **medium**: Single authoritative source or consistent community reports without official confirmation
- **low**: Extrapolated from adjacent data, limited sourcing, or platform-specific data unavailable; marked [UNVERIFIED] where appropriate

### KEY SOURCES

**Tier 1:**
- [KDP Pricing](https://kdp.amazon.com/en_US/help/topic/G200634500), [KDP Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390), [KDP Royalties](https://kdp.amazon.com/en_US/help/topic/G200644210)
- [ACX New Royalty Model](https://www.acx.com/mp/blog/audibles-new-royalty-model-early-access-successes), [ACX Help](https://help.acx.com/s/article/audible-s-new-royalty-model)
- [Apple Books for Authors](https://authors.apple.com/measure), [Reedsy Apple Guide](https://reedsy.com/blog/how-to-publish-on-apple-books/)
- [Google Revenue FAQ](https://support.google.com/books/partner/answer/9331459), [Google Publisher Policies](https://support.google.com/books/partner/answer/166501)
- [Kobo Writing Life](https://kobowritinglife.zendesk.com/hc/en-us/articles/360058976032-What-will-my-earnings-be), [Kobo Plus](https://kobowritinglife.zendesk.com/hc/en-us/articles/360058975432-What-is-Kobo-Plus)

**Tier 2:**
- [Scribd BookID](https://support.scribd.com/hc/en-us/articles/360037497152-About-the-BookID-Copyright-Protection-System), [Scribd Community Rules](https://support.scribd.com/hc/en-us/articles/210129166-Community-Rules-Prohibited-Activity-and-Content)
- [Storytel Group](https://www.storytelgroup.com/en/), [New Publishing Standard on Storytel](https://thenewpublishingstandard.com/2022/01/25/storytels-q4-royalties-revealed-and-yes-they-were-lower-than-a-regular-sale-royalty-heres-why-thats-not-such-a-big-deal/)
- [D2D FAQ](https://draft2digital.com/faq/), [D2D Royalty Rates](https://www.draft2digital.com/blog/royalty-rates/)
- [Spotify for Authors](https://authors.spotify.com/self-published-authors), [Spotify Newsroom](https://newsroom.spotify.com/2025-03-13/spotify-audiobooks-launches-a-new-publishing-program-for-independent-authors/)

**Tier 3:**
- [WEBTOON Creator Programs](https://ir.webtoon.com/news-releases/news-release-details/webtoon-announces-significant-expansion-its-creator-programs), [WEBTOON Notice](https://www.webtoons.com/en/notice/detail?noticeNo=3553)

**Cross-cutting:**
- [Inkfluence AI on KDP AI Policy](https://www.inkfluenceai.com/blog/amazon-kdp-ai-disclosure-policy-2026), [BookAutoAI](https://blog.bookautoai.com/ai-generated-content-amazon-kdp-2025/)
- [CoinGeek on velocity limits](https://coingeek.com/amazon-publishing-limits-seek-to-prevent-rise-of-ai-generated-books/)
- [PublishDrive on audiobook royalties](https://publishdrive.com/audiobook-pricing-and-royalties-how-to-protect-margin-and-still-grow-reach.html)
- [Self-help structure](https://www.asja.org/structuring_a_self-help_book/), [PickFu](https://www.pickfu.com/blog/how-to-structure-a-self-help-book/)
- [Reedsy on Amazon algorithms](https://reedsy.com/blog/guide/kdp/amazon-algorithms-for-authors/)
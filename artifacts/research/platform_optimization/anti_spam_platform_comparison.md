## DELIVERABLE 2: Anti-Spam Comparison Matrix

### Our Internal Gates vs. Platform Policies

| Our Gate | Our Threshold | Platform | Platform Policy | Gap | Recommendation |
|----------|--------------|----------|----------------|-----|----------------|
| **CTSS block** | 0.78 similarity | Amazon KDP | "Substantially similar" flagging; no numeric threshold published; uses "automated detection analyzing writing patterns, metadata, and submission velocity" | GAP: Amazon's threshold is unknown but enforcement has "significantly ramped up in 2025-2026." Our 0.78 may be at or near their boundary | Maintain 0.78 for Amazon; consider lowering to 0.75 as safety margin. Source: [Inkfluence](https://www.inkfluenceai.com/blog/amazon-kdp-ai-disclosure-policy-2026) |
| **CTSS review** | 0.65 similarity | Amazon KDP | No known review tier; binary accept/reject | GAP: Our review tier is a useful internal safety net that Amazon doesn't offer | Keep 0.65 review threshold; books in 0.65-0.78 range get manual editorial review before publishing |
| **CTSS block** | 0.78 | Scribd (BookID) | BookID: semantic fingerprinting, "same or substantially similar" removal, detects content "even if altered to some degree" | GAP: BookID appears MORE aggressive than our 0.78 threshold. It uses semantic analysis, not just structural fingerprints | RAISE to 0.82+ for Scribd-destined content. BookID's semantic analysis likely catches content our structural CTSS would pass. Source: [Scribd BookID](https://support.scribd.com/hc/en-us/articles/360037497152-About-the-BookID-Copyright-Protection-System) |
| **CTSS block** | 0.78 | Apple Books | No known automated similarity detection; editorial curation | GAP: Apple relies on human curation, not automated detection. Our gate is stricter than Apple's apparent requirements | Our 0.78 is more than adequate for Apple. Could safely publish wider range of structural variants |
| **CTSS block** | 0.78 | Google Play | No known similarity detection system published | GAP: Google's content policies are focused on publisher quality, not structural similarity. However, Google's price-matching behavior creates indirect exposure to Amazon's detection | Maintain 0.78 since Google content also appears on Amazon ecosystem. Source: [Google Publisher Policies](https://support.google.com/books/partner/answer/166501) |
| **CTSS block** | 0.78 | Kobo | No known similarity detection system | GAP: Kobo has no apparent structural similarity detection. Our gate is conservative for this platform | Maintain 0.78 for catalog integrity even without platform enforcement |
| **Wave density (arc_id)** | 30% max same | Amazon KDP | 3/day hard upload limit; "abusive behavior" flagging at sustained high velocity; community reports 5/week throttle | GAP: Our 30% arc threshold is structural; Amazon's limit is velocity-based. A 10-book wave with 3 same arc (30%) released over 3 days would be fine velocity-wise but structurally risky | Combine both: enforce our 30% arc cap AND space releases to max 3/week for Amazon. Source: [CoinGeek](https://coingeek.com/amazon-publishing-limits-seek-to-prevent-rise-of-ai-generated-books/) |
| **Wave density (band_seq)** | 40% max same | Amazon KDP | No known band_seq-specific check; general "substantially similar" detection | GAP: Amazon doesn't specifically check emotional band sequences, but their automated pattern detection may catch this as part of broader similarity | Our 40% threshold is a reasonable safety margin for a metric Amazon may indirectly detect |
| **Wave density (slot_sig)** | 50% max same | Amazon KDP | No known slot-signature check | GAP: This is an internal structural metric with no known external analog | Maintain as internal quality control; not directly relevant to platform compliance |
| **Freebie density (bundle)** | 40% max identical | All platforms | No platform-specific freebie density checks found | GAP: Platforms don't monitor freebie similarity, but readers noticing identical lead magnets across books reduces trust and conversion | Maintain for brand integrity, not platform compliance |
| **Freebie density (CTA)** | 50% max identical | All platforms | No platform-specific CTA monitoring | GAP: Same as above - this is brand/trust protection, not platform compliance | Maintain as is |
| **Story family dominance** | 70% max one family | Amazon KDP | General "quality" and "originality" requirements; no specific structural family check | GAP: Amazon's detection is holistic, not family-specific. But publishing books with >70% same story family would likely trigger "substantially similar" flags | Our 70% threshold with 55% warning is well-calibrated |
| **Exercise family concentration** | 60% max one family | All platforms | No platform-specific exercise detection | GAP: Internal quality gate only; no external analog | Maintain for content quality |
| **Compression family diversity** | 70% max one family | All platforms | No platform-specific compression check | GAP: Internal quality gate only | Maintain for structural diversity |
| **Upload velocity** | Not currently gated | Amazon KDP | 3/day HARD LIMIT; sustained high velocity = account flag | CRITICAL GAP: Our pipeline has no explicit upload velocity gate | ADD: wave_orchestrator should enforce per-platform upload velocity limits. Amazon: max 3/day, recommended 3/week. Others: variable. Source: [CoinGeek](https://coingeek.com/amazon-publishing-limits-seek-to-prevent-rise-of-ai-generated-books/) |
| **AI disclosure** | Not currently tracked | Amazon KDP | MANDATORY disclosure of AI-generated content during upload; failure = removal + royalty withholding + potential account termination | CRITICAL GAP: Our pipeline doesn't track or flag AI disclosure requirements per platform | ADD: Metadata field `ai_disclosure_required: true/false` per platform in export config. All Amazon uploads must include AI-generated disclosure. Source: [KDP AI Policy](https://kdp.amazon.com/en_US/help/topic/G200672390) |
| **AI disclosure** | Not currently tracked | Spotify | AI narration explicitly accepted for Spotify-only distribution | Different from Amazon: Spotify is permissive on AI narration. Track disclosure requirements per-platform | ADD to export metadata: per-platform AI policy compliance flags |
| **Engagement metrics** | Not currently tracked | Audible (new model), Storytel, Kobo Plus, Spotify Premium | Pooled revenue models pay based on listening/reading engagement (minutes/hours consumed) | CRITICAL GAP: Our pipeline optimizes for structural diversity but not for reader/listener engagement signals that drive pooled-model payouts | CONSIDER: Add engagement prediction score to compiled plan. Chapter-level engagement modeling (time-to-drop-off prediction) would optimize for subscription platforms |
| **Price-matching exposure** | Not currently managed | Google Play <-> Amazon | Google may unilaterally discount; Amazon price-matches, potentially dropping you to 35% royalty tier | GAP: No cross-platform pricing coordination in current pipeline | ADD: Per-platform pricing offset rules. Set Google list price $1-2 higher than Amazon to absorb potential discounting. Source: [PublishDrive](https://help.publishdrive.com/google-play-special-terms) |
| **Pre-order strategy** | Not currently managed | Apple Books, Kobo | Pre-orders count double on Apple (pre-order sale + launch sale). Kobo pre-orders double visibility | GAP: No pre-order timing coordination in release wave planning | ADD: wave_orchestrator should support pre-order windows (4-8 weeks before release) for Apple and Kobo titles specifically |

---

### CRITICAL GAPS REQUIRING PIPELINE CHANGES

1. **Upload velocity gate**: Add per-platform velocity limits to wave_orchestrator (Amazon: 3/day max, 3/week recommended; others: variable).

2. **AI disclosure tracking**: Add `ai_disclosure_status` field to CompiledBook/export metadata. Required for Amazon KDP compliance.

3. **Scribd-specific entropy**: Raise CTSS block threshold to 0.82+ for Scribd-destined content due to BookID's aggressive semantic fingerprinting.

4. **Cross-platform pricing coordination**: Add pricing offset rules to prevent Google Play discounting from triggering Amazon price-match royalty drops.

5. **Pre-order window support**: Add pre-order scheduling to wave_orchestrator for Apple Books and Kobo releases.

6. **Engagement optimization signal**: For subscription platforms (Audible new model, Kobo Plus, Storytel, Spotify Premium), consider adding engagement prediction scoring that favors narrative density and shorter chapters.

---

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
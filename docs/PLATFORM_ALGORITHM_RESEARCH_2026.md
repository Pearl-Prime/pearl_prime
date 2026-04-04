# Platform Algorithm Research — April 2026

**Source:** Pearl_Research deep web research + existing repo docs
**Purpose:** Wire platform-specific tuning into catalog planners

## Key Findings by Platform

### Audible (50% market share)
- **Primary ranking signal:** Sales velocity + completion rate
- **Completion target:** 70%+ triggers positive recommendations
- **Self-help sweet spot:** 5-6 hours (beyond 10h = second-half drop-off)
- **Chapter duration:** 15-30 min optimal
- **First 10-20 min:** Highest drop-off zone — invest in opening
- **Metadata:** 7-10 keywords, accurate categories, narrator bio
- **Royalty:** Exclusive 50%, non-exclusive 30%

### Spotify (fastest growing)
- **Algorithm:** Graph Neural Networks (2T-HGNN) — cross-domain from music/podcast
- **AudioBoost:** LLM-generated queries for cold-start discovery
- **Metrics that matter:** Unique listeners, time spent, completion, saves, shares
- **Engagement-weighted:** Sustained listening > many first plays
- **Included in Premium:** 15 hours/month, no separate pricing
- **Catalog:** 400K+ English titles, 30% YoY listener growth

### Apple Books
- **Ranking:** Editorial curation + algorithmic personalization
- **Metadata accuracy critical:** Mismatched metadata → suppression
- **Category:** Accuracy > size. Don't game categories.

### Google Play (strictest anti-duplicate)
- **Ranking:** Popularity + downloads
- **Duplicate detection:** Automated models, rejects identical ISBNs, blocks public domain duplicates entirely
- **Content policy:** Automated + human review pipeline

### Ximalaya (China, 70%+ market share)
- **303M MAU, 600M+ total users**
- **AI-driven:** Everest AI Audio Multimodal Large Model
- **Pricing:** Freemium (vast majority free), VIP ~$2.49/month
- **Content moderation:** Strict government compliance required
- **Tencent acquired April 2025** — algorithm may change

### Naver/Kakao (Korea)
- **Naver:** 90-minute compact format trending, Naver Search SEO critical
- **Kakao:** "Wait for Free" serialization model, serialized > complete books
- **Market:** 10.6M listeners projected by 2030

### Japan (2nd largest audiobook market)
- **$296.8M revenue 2024, projected $1.3B by 2030**
- **Fiction dominates (79.89%)**
- **Voice actor quality (seiyuu) is primary differentiator**

## Universal Rules

| Metric | Target | Why |
|--------|--------|-----|
| Completion rate | ≥70% | Universal positive algorithm signal |
| Self-help length | 5-6 hours | Beyond 10h kills completion |
| Chapter duration | 15-30 min | Matches average session |
| Opening chapter | Best prose in book | Highest drop-off zone |
| Unique metadata per title | Mandatory | Anti-duplicate on all platforms |
| Release window | January-March (Q1) | Peak self-help season |

## Anti-Spam Thresholds

| Platform | Strictness | Key Rule |
|----------|-----------|----------|
| Google Play | Strictest | Rejects identical ISBNs, blocks public domain |
| Spotify | Tightening | New spam filter 2025, targets mass uploads |
| Audible | Moderate | ACX QC review on submission |
| Apple | Moderate | Duplicate listings possible, resolved via support |

## Seasonal Windows

| Window | Best For |
|--------|---------|
| January | Self-help peak (New Year resolutions) |
| Q1 (Jan-Mar) | Business, self-improvement, health |
| Late May-June | Summer reading season |
| September | Back-to-school/routine, secondary self-improvement peak |
| **Avoid** Nov 15-Dec 31 | Holiday competition noise |
| China: Feb + Nov 11 | Chinese New Year + Singles Day |
| Japan: late April | Golden Week |
| Korea: Feb + Sep/Oct | Seollal + Chuseok |

## Platform-Specific Knob Tuning

### Duration → Format Selection
| Platform | Ideal Runtime | Format |
|----------|-------------|--------|
| Audible | standard_book (55 min) or extended_book_2h | F006, F003 |
| Spotify | short_book_30 or standard_book | F003, F006, F015 |
| Ximalaya | micro_book_15 or micro_book_20 (episode format) | F015, F003 |
| Naver | short_book_30 (90-min compact trend) | F003 |
| Kakao | micro serialized episodes | F015, F001 |
| Apple/Google/Kobo | standard_book or extended | F006, F004, F009 |

### Structure → Bestseller Type
| Platform Audience | Preferred Structures |
|------------------|---------------------|
| Audible Premium | Promise Engine, Gladwell Spiral, Brené Brown |
| Spotify Casual | Atomic, Myth-Killer, Permission Slip (shorter, punchier) |
| Ximalaya Episode | Case File, Zoom Lens (self-contained chapters) |
| Korea Serialized | The Letter, Contrast Engine (cliffhanger threads) |
| Japan Literary | Van der Kolk, Ancestor, Zoom Lens (depth, precision) |

# 48 Social + GoHighLevel — Brand Admin Operations Spec

**Authority:** Pearl_Marketing + Pearl_PM
**Audience:** Brand admins worldwide (312 brands × 13 lanes)
**Purpose:** Exact instructions for what every brand admin does with 48 Social content repurposing and GHL email/SMS campaigns.

---

## 1. What 48 Social Does For You

48 Social is Pearl Prime's exclusive organic marketing partner. For every book your brand produces, 48 Social:

1. **Breaks the book into 30-50 social media assets** — teaching carousels, practical posts, recognition posts, stories, reframes, original quote-with-commentary cards, and offers
2. **Schedules them across all your platforms** — Instagram, TikTok, Facebook, Twitter/X, LinkedIn, Pinterest
3. **Runs your email proof-loop campaign** (E1-E9) via GoHighLevel
4. **Manages your freebie funnel** — landing page → email capture → nurture → book sale
5. **Tracks everything** in the GHL CRM — who downloaded what, who bought what, who's ready for upsell

**You don't create marketing content.** 48 Social creates it from your books. You review and approve.

**Cost:** 4.8% of your monthly platform revenue (auto-collected via Plaid on the 1st of each month).

---

## 1b. How 48 Social Gets Our Content (Integration Spec)

### Content Delivery: Cloudflare R2 → 48 Social

48 Social gets READ-ONLY access to the Cloudflare R2 bucket where all brand content lives. They pull what they need — they don't need to ask us.

**R2 bucket structure (per brand, per week):**
```
r2://pearl-prime-content/{brand_id}/{week}/
  ├── books/                    # rendered prose .txt files
  │   ├── book_001.txt
  │   └── book_002.txt
  ├── videos/                   # all 5 formats per book
  │   ├── book_001_youtube.mp4      (10 min, 16:9)
  │   ├── book_001_shorts.mp4       (60s, 9:16)
  │   ├── book_001_tiktok.mp4       (30-60s, 9:16)
  │   ├── book_001_instagram.mp4    (60s, 9:16)
  │   └── book_001_line.mp4         (60-90s, 9:16 — Japan/Taiwan only)
  ├── covers/                   # ebook + audiobook + manga covers
  │   ├── book_001_ebook_cover.jpg
  │   ├── book_001_audiobook_cover.jpg
  │   └── book_001_manga_cover.jpg
  ├── metadata/                 # per-platform metadata JSONs
  │   ├── book_001_google_play.json
  │   ├── book_001_youtube.json
  │   └── book_001_tiktok.json
  ├── freebies/                 # companion workbooks, tools
  │   └── book_001_workbook.html
  └── manifest.json             # full inventory for the week
```

**48 Social access:**
- **Read-only R2 API key** scoped to `r2://pearl-prime-content/` (all brands)
- They can list, read, download — but NOT modify or delete
- New content appears every Monday (weekly build cycle)
- MP4s are deleted Sunday 23:59 UTC — 48 Social must pull videos within the week

### What 48 Social Does With Our Content

| Our Asset | What 48 Social Creates | How |
|-----------|----------------------|-----|
| `book_001.txt` (prose) | Carousels, practical posts, recognition posts, story posts, reframes, and original quote-with-commentary cards | Extract clear points, mechanisms, practices, stories, callbacks, quotable lines, and offers |
| `book_001_shorts.mp4` (60s video) | 4 video clip posts | Trim to 15-30s highlights, add captions + CTA overlay |
| `book_001_tiktok.mp4` (30-60s) | 3 TikTok posts | Add trending sounds, text hooks, hashtags |
| `book_001_instagram.mp4` (60s) | 3 Reels + 2 Stories | Reels with CTA, Stories with swipe-up |
| `book_001_ebook_cover.jpg` | Post graphics | Cover reveal posts, "new release" announcements |
| `book_001_workbook.html` | 2 freebie promo posts | "Free companion guide" CTA posts |
| `manifest.json` | Scheduling calendar | Maps content to posting dates |

### What We Give 48 Social (One-Time Setup Per Brand)

| Item | Format | Where | Purpose |
|------|--------|-------|---------|
| R2 read-only API key | API credential | Secure handoff | Access all brand content |
| Brand style guide | JSON | `manifest.json → brand_style` | Colors, fonts, logo, CTA templates |
| CTA URL templates | String | In manifest.json | `brand-admin-onboarding.pages.dev/free/{slug}?utm_source={platform}` |
| GHL sub-account credentials | Login | Secure handoff | Post scheduling, email automation |
| Platform account handles | List | In manifest.json | @handle per platform per brand |
| Voice/tone brief | Text | In manifest.json | "Warm, direct, somatic, no guru voice" |

### What 48 Social Accesses via Metricool/GHL

48 Social uses **Metricool** (or GHL native scheduling) to:
1. Pull videos from R2 → upload to Metricool media library
2. Create posts with our CTA text + brand hashtags
3. Schedule across all connected platforms
4. Track engagement metrics → feed back to GHL CRM

**Metricool integration:**
- 48 Social connects each brand's social accounts to their Metricool workspace
- They import videos weekly from R2 (API or manual download)
- Posts are created in Metricool with our pre-written captions + CTAs
- Scheduling follows our upload_schedule.yaml cadence (2-3/day/platform)
- Auto-approve is ON — posts go live without brand admin approval

**GHL integration:**
- 48 Social has admin access to each brand's GHL sub-account
- Email sequences (E1-E9) are pre-configured and auto-triggered by freebie downloads
- Social scheduling can also run through GHL's social module if preferred over Metricool
- CRM tracks: freebie downloads → email signups → book purchases → upsells

### Weekly Sync

Every Monday:
1. Pipeline builds weekly content → uploads to R2
2. 48 Social's system detects new content in R2 (webhook or polling)
3. 48 Social pulls assets, creates posts, schedules across platforms
4. Brand admin gets a "Your week is live" notification (auto — no action needed)

### What Happens to Videos After the Week

- **Monday-Saturday:** Videos live on R2, 48 Social pulls and schedules them
- **Sunday 23:59 UTC:** MP4s deleted from R2 (save storage)
- **But:** 48 Social already has the videos in their Metricool media library — deletion doesn't affect scheduled or published posts
- **Metadata, covers, freebies, book text:** Persist indefinitely on R2

---

## 2. The Content Repurposing Pipeline

**Current static-content authority:** see [STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md](specs/STATIC_SOCIAL_BOOK_CONTENT_ENGINE_2026-07-13.md).

The 2026 operating model is **carousel/practical-teaching first**, not quote-card first. The best static social assets behave like miniature self-help chapters: recognize the reader, validate the experience, explain one mechanism, offer one reframe, give one micro-practice, and end with a natural invitation.

```
Book (from Pearl Prime weekly package)
  ↓
48 Social Content Engine
  ↓
30-50 static/social assets per book:
  ├── 5-8 Instagram teaching carousels
  ├── 2-4 LinkedIn PDF/document posts
  ├── 6-10 Pinterest vertical Pins
  ├── 4-6 Facebook photo/text/story posts
  ├── 6-10 X/Threads text-native posts
  ├── 2-4 TikTok photo-mode sequences
  ├── 1-3 original quote-with-commentary cards
  └── 2-4 offer/invitation posts
```

Each post includes a **CTA** pointing to your freebie landing page.

Default non-video mix per 20 posts:

| Class | Target | Function |
|-------|--------|----------|
| Practical teaching | 8 | Saves, authority, usable value |
| Recognition / validation | 5 | Emotional specificity, sharing |
| Personal or reader-style stories | 3 | Trust and proof of method |
| Strong opinions / reframes | 2 | Conversation and thought leadership |
| Original quote with commentary | 1 | Shareable identity signal |
| Offer / invitation | 1 | Freebie, book, bundle, or list growth |

Quote-style posts must stay under 10-15% of the static feed unless a brand-specific test proves otherwise. Famous borrowed quotes are not default content.

---

## 3. Exact CTAs — What They Say and Where They Point

### 3.1 CTA URL Pattern

Every CTA points to:
```
https://brand-admin-onboarding.pages.dev/free/{freebie_slug}
```

With UTM parameters per platform:
```
?utm_source={platform}&utm_medium={post_type}&utm_campaign={brand_id}&utm_content={book_id}
```

**Examples:**
- Instagram post: `brand-admin-onboarding.pages.dev/free/anxiety-corporate-managers-breath-timer-v1?utm_source=instagram&utm_medium=quote_card&utm_campaign=stabilizer_en_us&utm_content=book_042`
- TikTok bio: `brand-admin-onboarding.pages.dev/free/anxiety-corporate-managers-breath-timer-v1?utm_source=tiktok&utm_medium=bio_link&utm_campaign=stabilizer_en_us`

### 3.2 CTA Text by Post Type

| Post Type | CTA Text (English) | Where |
|-----------|-------------------|-------|
| **Quote Card** | "Free companion guide → link in bio" | Caption + text on image |
| **Micro-Practice** | "Get the full practice free → link in bio" | Caption, last line |
| **Hook Post** | "This is from our new book. Free guide in bio ↗" | Caption |
| **Carousel** | Slide 5 (last): "Want the full guide? Free → link in bio" | Last carousel slide |
| **Video Clip** | Overlay last 3 seconds: "Link in bio 📖" | Video overlay + caption |
| **Story/Reel** | Swipe-up or "Link in bio" sticker | Story CTA element |
| **Thread** | Final tweet: "Full free guide: [link]" | Last tweet in thread |
| **Engagement** | "Which resonates? Get the free guide → bio" | Caption |

### 3.3 CTA Text by Language

| Language | CTA (Short) | CTA (Medium) | CTA (Bio Link) |
|----------|------------|-------------|----------------|
| **English** | "Free guide in bio ↗" | "Get the companion guide free → link in bio" | "Free wellness tools: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Japanese** | "無料ガイド → プロフリンク" | "無料の実践ガイドをダウンロード → プロフィールのリンクから" | "無料ウェルネスツール: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Korean** | "무료 가이드 → 프로필 링크" | "무료 실천 가이드 받기 → 프로필 링크에서" | "무료 웰니스 도구: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Traditional Chinese** | "免費指南 → 個人檔案連結" | "免費下載實踐指南 → 個人檔案連結" | "免費身心工具: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Simplified Chinese** | "免费指南 → 个人资料链接" | "免费下载实践指南 → 个人资料链接" | "免费身心工具: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Spanish** | "Guía gratis en bio ↗" | "Descarga la guía complementaria gratis → enlace en bio" | "Herramientas gratis: brand-admin-onboarding.pages.dev/free/{slug}" |
| **French** | "Guide gratuit → lien en bio" | "Téléchargez le guide gratuit → lien dans la bio" | "Outils gratuits: brand-admin-onboarding.pages.dev/free/{slug}" |
| **German** | "Kostenloser Guide → Link in Bio" | "Kostenloser Begleitguide herunterladen → Link in Bio" | "Kostenlose Tools: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Italian** | "Guida gratuita → link in bio" | "Scarica la guida gratuita → link nel profilo" | "Strumenti gratuiti: brand-admin-onboarding.pages.dev/free/{slug}" |
| **Hungarian** | "Ingyenes útmutató → link a bio-ban" | "Töltsd le az ingyenes útmutatót → link a profilban" | "Ingyenes eszközök: brand-admin-onboarding.pages.dev/free/{slug}" |

---

## 4. Email Proof-Loop Campaign (E1-E9)

When someone downloads a freebie, they enter the **evergreen proof-loop email sequence**. 48 Social manages this via GHL. The current GHL implementation is contact-specific inbound webhook -> custom fields -> 9-email sequence, not an RSS/feed blast.

### The 9-Email Sequence

| Email | Timing | Subject | Content | CTA |
|-------|--------|---------|---------|-----|
| **E1** | Immediate | "Your free {workbook_label} is ready" | Freebie download link + first somatic exercise | "Try this 2-minute exercise now" |
| **E2** | +24 hours | "A second exercise — different mechanism" | Second exercise from the book (different from E1) | "This one works on a different part of your nervous system" |
| **E3** | +72 hours | "Someone's story" | Transformation story from the book's STORY atoms | "Read how this changed for someone like you" |
| **E4** | +48 hours after E3 | "The full book is available" | Book offer with cover art + excerpt + companion info | "Get the full book → {store_link}" |
| **E5** | +7 days after E4 | "More from {brand_name}" | Recommend 2-3 related books from the same brand | "Explore more → {brand_catalog_link}" |
| **E6** | +72 hours after E5 | "Book two recommendation" | Second book recommendation for continuity | "Open recommendation 2" |
| **E7** | After E6 | "Book three / bundle path" | Third book or bundle-style path | "See the bundle path" |
| **E8** | Last direct nudge | "Last chance" | Final book-sequence reminder | "Take the next step" |
| **E9** | Still-here reminder | "Still here" | Original free tool link again | "Reopen the free tool" |

**Psychology:** Demonstrate the mechanism twice (E1 + E2), show transformation through a story (E3), then make the book offer (E4). E5-E9 continue the evergreen recommendation path without requiring a weekly feed lookup.

For the current Waystream field map, see [GHL_ADMIN_WAYSTREAM_EVERGREEN_FREEBIE_FUNNEL.md](ghl/GHL_ADMIN_WAYSTREAM_EVERGREEN_FREEBIE_FUNNEL.md) and [proof_loop_sequence.md](email_sequences/proof_loop_sequence.md).

### Email CTA Links

| Email | CTA URL |
|-------|---------|
| E1 | `brand-admin-onboarding.pages.dev/free/{slug}#download` (direct download) |
| E2 | `brand-admin-onboarding.pages.dev/free/{slug}#exercise2` (second exercise) |
| E3 | `brand-admin-onboarding.pages.dev/free/{slug}#story` (story page) |
| E4 | `{platform_store_link}` (Google Play, Amazon, Apple — varies by lane) |
| E5 | `catalog.brand-admin-onboarding.pages.dev/{brand_id}` or campaign-plan book list |
| E6 | `phoenix_e6_url` |
| E7 | `phoenix_e7_url` |
| E8 | `phoenix_e8_url` |
| E9 | `phoenix_e9_url` (usually original free tool) |

### Email Subject Lines by Language

| Email | English | Japanese | Korean | Spanish |
|-------|---------|----------|--------|---------|
| E1 | "Your free guide is ready" | "無料ガイドをお届けします" | "무료 가이드가 준비되었습니다" | "Tu guía gratuita está lista" |
| E2 | "Try a different exercise" | "別のエクササイズを試してみてください" | "다른 운동을 시도해 보세요" | "Prueba un ejercicio diferente" |
| E3 | "Someone's story" | "ある人のストーリー" | "어떤 사람의 이야기" | "La historia de alguien" |
| E4 | "The full book is here" | "完全版の書籍はこちら" | "전체 책이 여기 있습니다" | "El libro completo está aquí" |
| E5 | "More tools for you" | "あなたのためのツール" | "당신을 위한 도구들" | "Más herramientas para ti" |

---

## 5. GHL Setup Per Brand

Each brand gets its own GHL sub-account. 48 Social sets this up. Brand admin needs to:

### 5.1 What You Provide to 48 Social
- Brand name + display name
- Platform accounts (Instagram handle, TikTok username, YouTube channel, etc.)
- Logo + brand colors (from cover art system)
- Freebie landing page URL (auto-generated by pipeline)

### 5.2 What 48 Social Configures in GHL
- **Contact lists:** Segmented by freebie type, book purchased, engagement level
- **Email templates:** E1-E9 proof-loop, branded with your colors/logo
- **SMS templates:** Book launch announcements (opt-in only)
- **Funnel pages:** Freebie landing page + thank-you page
- **Social calendar:** 30-50 posts per book, spread across 2-3 weeks
- **Automation workflows:**
  - Freebie download → tag contact → start E1-E9 sequence
  - E4 purchase → tag as buyer → add to upsell list
  - No engagement after E5 → move to re-engagement sequence (30 days later)

### 5.3 Auto-Approve Mode (DEFAULT)

**All posts are auto-approved and auto-published.** Brand admins do NOT need to review or approve individual posts. 48 Social's content comes directly from your books — it's already brand-safe because the books passed quality gates.

```
Auto-approve: ON (default for all brands)
Review mode:  OFF (admin can opt-in if they want manual review)
```

To opt into manual review mode, admin toggles "Review Before Publish" in their GHL settings. This is NOT recommended — it adds work without improving quality since content is deterministic from book atoms.

### 5.3b What You (Brand Admin) Actually Do Weekly
1. **Monday:** Glance at weekly notification (email/Slack) confirming content was published
2. **Thursday:** Optional — check GHL dashboard for engagement metrics (2 min)
3. **That's it.** Everything else runs automatically.

Total weekly time: **2-5 minutes.** Not hours.

### 5.4 What You NEVER Do
- Write social media copy (48 Social does this from your books)
- Design graphics (generated from cover art system)
- Set up email sequences (48 Social configures in GHL)
- Manage ad campaigns (organic only at baseline; paid is optional)
- Approve individual posts (auto-approve is default)
- Upload content to platforms (Pearl_Int auto-uploads via API)
- Schedule anything (48 Social handles all scheduling)

---

## 6. Video Distribution CTAs

Every book produces 5 video formats. Each video has CTAs baked in:

### 6.1 YouTube Long-Form (10 min)

| Timing | CTA Type | Text |
|--------|----------|------|
| ~2 min mark | Spoken by narrator | "This video has a free companion {workbook_label}. Link in the description." |
| Last 10 seconds | Text overlay | "Free {workbook_label}: brand-admin-onboarding.pages.dev/free/{slug}" |
| Description | Link | "📖 Free {workbook_label}: {url}?utm_source=youtube&utm_medium=video" |
| Pinned comment | Link | "Get the free {workbook_label}: {url}" |

### 6.2 YouTube Shorts (60s)

| Timing | CTA Type | Text |
|--------|----------|------|
| Last 5 seconds | Text overlay | "Link in bio 🔗" |
| Description | Link | "{url}?utm_source=youtube_shorts" |
| Pinned comment | Link | "Free {workbook_label}: {url}" |

### 6.3 TikTok (30-60s)

| Timing | CTA Type | Text |
|--------|----------|------|
| Last 3 seconds | Text overlay | "Link in bio 📖" |
| Bio link | URL | "{url}?utm_source=tiktok" |
| Caption | Text + hashtags | "Free {workbook_label} in bio 📖 #mentalhealth #{topic} #selfhelp" |

### 6.4 Instagram Reels (60s)

| Timing | CTA Type | Text |
|--------|----------|------|
| Last 5 seconds | Text overlay | "Free guide in bio ↗" |
| Caption | Link | "Free {workbook_label} — link in bio 📖" |
| Bio link | URL | "{url}?utm_source=instagram&utm_medium=reels" |

### 6.5 LINE (60-90s, Japan/Taiwan)

| Timing | CTA Type | Text |
|--------|----------|------|
| Last 5 seconds | Text overlay | "無料ガイド：下のリンクから" (JP) / "免費指南：點擊下方連結" (TW) |
| Last 8 seconds | QR code | Bottom-right, 150px, points to freebie URL |
| Push message | After video | "📖 無料の{workbook_label}はこちら: {url}" |

---

## 7. Platform-Specific Social Posting Rules

### 7.1 Instagram
- **Post frequency:** 1-2 posts/day (48 Social manages)
- **Content mix:** carousel-first. Use 3-4 teaching carousels/week when asset volume allows, with occasional original quote-with-commentary cards, photo-story posts, and Stories.
- **Carousel structure:** specific hook -> recognizable situation -> validation -> mechanism -> reframe -> practice -> obstacle -> takeaway -> save/share/reflection invitation
- **Hashtags:** 15-20 per post, mix of broad (#selfcare #mentalhealth) and niche (#nervousystem #somatichealing)
- **Bio link:** Linktree or direct to freebie (rotate with each new book)
- **CTA:** Always in caption, never as only element (Instagram penalizes CTA-only posts)
- **Avoid:** generic quote-card feed, stock meditation photos, large blocks of text over busy images

### 7.2 TikTok
- **Post frequency:** 1-2/day
- **Hook:** First 2 seconds must stop the scroll — text on screen + movement
- **Static content:** use photo-mode carousels selectively for diary-style stories, "things I wish I knew" lists, progress narratives, and practical self-help sequences
- **Video content:** still useful for reach, but static photo posts must feel native, immediate, and personal rather than reposted Instagram graphics
- **Hashtags:** 3-5 max (TikTok algorithm prefers fewer, more specific)
- **Bio:** Single link to current freebie

### 7.3 Facebook
- **Post frequency:** 1/day
- **Content:** authentic photo plus 150-400-word story, text-only reflection, practical graphic, 3-5 image album, or discussion prompt
- **Groups:** Join 3-5 relevant wellness/self-help groups, share value (NOT promotional)
- **CTA:** "Download the free guide" with direct link (Facebook allows links in posts)
- **Priority:** emotional relevance and community conversation matter more than exact format

### 7.4 Twitter/X
- **Post frequency:** 2-3/day (tweets are short-lived)
- **Content:** text-first claims, sharp distinctions, short threads, diagrams, handwritten notes, or raw screenshots
- **CTA:** Final tweet in thread: "Full free guide: [link]"
- **Hashtags:** 1-2 per tweet max
- **Rule:** one clear claim, one tension, one clean final sentence

### 7.5 Pinterest
- **Post frequency:** 5-10 pins/week (Pinterest is evergreen — pins last months)
- **Content:** vertical 2:3 instructional Pins, journal prompts, checklists, worksheet previews, book covers, and exercise infographics
- **CTA:** Pin description links directly to freebie page
- **Boards:** Create 3-5 boards per brand (Anxiety Tools, Sleep Practices, etc.)
- **Search framing:** titles should answer specific needs, e.g. "journal prompts for decision anxiety" or "five grounding practices before sleep"

### 7.6 LinkedIn
- **Post frequency:** 2-3/week
- **Content:** native PDF/document carousels, practical frameworks, leadership psychology, burnout, confidence, boundaries, difficult conversations, focus, and emotional regulation under pressure
- **CTA:** "Free toolkit for professionals → [link]"
- **Best for:** stabilizer, optimizer, executive_calm, career_lift brands
- **Rule:** do not upload an Instagram screenshot; rewrite for work-relevant language and professional dwell time

---

## 8. Freebie Types and When to Use Each

| Freebie Type | Best For | Format | CTA Framing |
|-------------|---------|--------|-------------|
| **Breath Timer** | Anxiety, sleep, somatic | Interactive HTML | "Try this 2-minute reset" |
| **Companion Workbook** | Standard/deep books | PDF (80-120 pages) | "Get the companion workbook free" |
| **Practice Guide** | Pocket guides, micro-books | PDF (30-50 pages) | "Download the practice guide" |
| **Assessment** | Shame, anxiety, burnout | Interactive HTML | "Take the free assessment" |
| **Emergency Kit** | Panic, crisis, acute anxiety | HTML tool | "Get the emergency toolkit" |
| **Journal Prompts** | Grief, self-worth, boundaries | PDF | "Start journaling with these prompts" |
| **Guided Meditation** | Sleep, somatic, spiritual | MP3 audio | "Listen to the free guided practice" |
| **30-Day Tracker** | Daily practice books | PDF | "Track your 30-day journey" |
| **Checklist** | Burnout, organization | PDF | "Get the free checklist" |

The pipeline automatically selects the right freebie for each book based on topic × persona × format. You don't choose — it's deterministic.

---

## 9. Weekly Metrics to Track

| Metric | Where to Find It | Target |
|--------|------------------|--------|
| Freebie downloads | GHL dashboard → Contacts | 50+/week growing |
| Email list size | GHL → Contacts → Active | 500 by month 3, 2,000 by month 6 |
| Email open rate | GHL → Campaigns → Analytics | >30% |
| Email click rate | GHL → Campaigns → Analytics | >5% |
| Social engagement rate | Instagram/TikTok insights | >3% |
| Video views | YouTube Studio / TikTok Analytics | Growing week-over-week |
| Book sales | Platform dashboards | Growing month-over-month |
| Freebie → Purchase conversion | GHL → Pipeline → Conversions | >5% |

---

## 10. What Goes Wrong and How to Fix It

| Problem | Cause | Fix |
|---------|-------|-----|
| No freebie downloads | CTA not visible or compelling | Rewrite CTA to lead with benefit, not feature |
| Low email open rate (<20%) | Subject lines too generic | Use curiosity/benefit format: "The 2-minute exercise that changes your nervous system" |
| High unsubscribe rate (>2%) | Emails too frequent or salesy | Extend E2→E3 gap to 96 hours; make E3 story longer |
| Social posts not engaging | Content too promotional | Switch to 80% value / 20% CTA ratio |
| Videos not getting views | Weak hook in first 2 seconds | Put the strongest text on screen in frame 1 |
| No book sales after email sequence | E4 offer too abrupt | Add a "soft E3.5" email with a book excerpt before the offer |

---

## 11. Brand URL Setup (FREE — Path-Based on Cloudflare Pages)

Every brand gets its own unique path on Cloudflare Pages. No custom domain needed. No DNS setup. $0 cost.

**Structure:** `brand-admin-onboarding.pages.dev/{brand-slug}/` — one path per brand

**Per brand:**
| URL | Purpose |
|-----|---------|
| `brand-admin-onboarding.pages.dev/{brand-slug}/` | Brand landing page, catalog |
| `brand-admin-onboarding.pages.dev/free/{freebie-slug}` | Freebie download page |
| GHL sends from `{brand-name}@msgsndr.com` | Email sending (no custom domain needed) |

**Examples:**
- `brand-admin-onboarding.pages.dev/stabilizer-en-us/` → Stabilizer brand page
- `brand-admin-onboarding.pages.dev/inner-light-press-ja-jp/` → Inner Light Press Japan
- `brand-admin-onboarding.pages.dev/free/anxiety-workbook` → Freebie landing page

**Email sending:** GHL provides unique sending addresses via `msgsndr.com`. Each GHL sub-account sends from a distinct address. No custom email domain needed.

**Anti-spam isolation:** Each GHL sub-account has independent sender reputation. Path-based URLs on Pages are all under one domain but email is isolated per GHL sub-account.

**Cost: $0.** Cloudflare Pages free tier. GHL email infrastructure included in plan.

---

## 12. Brand Admin Onboarding Checklist

**Pearl Prime does (before admin starts):**
- [x] Subdomain created on Cloudflare (automated — `setup_brand_subdomains.py`)
- [x] GHL sub-account created with email templates, funnels, automation
- [x] R2 read-only access configured for 48 Social
- [x] Weekly content pipeline configured for this brand
- [x] Freebie landing page template deployed to brand subdomain

**Brand admin does (one-time, ~30 minutes):**
- [ ] Create social accounts (YouTube, TikTok, Instagram, Facebook, + lane-specific)
- [ ] Log into Metricool → connect each social account via OAuth (5 min)
- [ ] Enter platform credentials in brand admin portal (Google Play, Kobo, etc.)
- [ ] Connect bank via Plaid Link (for revenue collection)
- [ ] Verify: open `{brand-slug}.brand-admin-onboarding.pages.dev` — landing page loads
- [ ] Verify: receive test email from `mail.{brand-slug}.brand-admin-onboarding.pages.dev`

**After onboarding, brand admin does weekly:**
- [ ] Glance at Monday notification confirming content was published (2 min)
- [ ] Optional: check GHL dashboard Thursday for engagement metrics (3 min)
- [ ] Handle 2FA prompts when platforms require re-authentication (rare)

**Total ongoing weekly effort: 2-5 minutes.**

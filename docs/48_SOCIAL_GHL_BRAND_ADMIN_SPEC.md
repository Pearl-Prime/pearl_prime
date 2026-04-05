# 48 Social + GoHighLevel — Brand Admin Operations Spec

**Authority:** Pearl_Marketing + Pearl_PM
**Audience:** Brand admins worldwide (312 brands × 13 lanes)
**Purpose:** Exact instructions for what every brand admin does with 48 Social content repurposing and GHL email/SMS campaigns.

---

## 1. What 48 Social Does For You

48 Social is Pearl Prime's exclusive organic marketing partner. For every book your brand produces, 48 Social:

1. **Breaks the book into 30-50 social media posts** — quotes, insights, micro-practices, hooks
2. **Schedules them across all your platforms** — Instagram, TikTok, Facebook, Twitter/X, LinkedIn, Pinterest
3. **Runs your email proof-loop campaign** (E1-E5) via GoHighLevel
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
| `book_001.txt` (prose) | 10 quote cards, 6 hook posts, 5 carousels | Extract best lines, overlay on brand-colored templates |
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
| CTA URL templates | String | In manifest.json | `PhoenixProtocolBooks.com/free/{slug}?utm_source={platform}` |
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
- Email sequences (E1-E5) are pre-configured and auto-triggered by freebie downloads
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

```
Book (from Pearl Prime weekly package)
  ↓
48 Social Content Engine
  ↓
30-50 Social Posts per book:
  ├── 10 Quote Cards (key insights as images with text overlay)
  ├── 8 Micro-Practice Posts (one exercise/technique per post)
  ├── 6 Hook Posts (first line that stops the scroll)
  ├── 5 Carousel Posts (multi-slide educational breakdowns)
  ├── 4 Video Clip Posts (from your YouTube/Shorts/TikTok videos)
  ├── 3 Story/Reel Templates (vertical format with CTA)
  ├── 2 Thread Posts (Twitter/X long-form breakdowns)
  └── 2 Engagement Posts (polls, questions, "which resonates?")
```

Each post includes a **CTA** pointing to your freebie landing page.

---

## 3. Exact CTAs — What They Say and Where They Point

### 3.1 CTA URL Pattern

Every CTA points to:
```
https://PhoenixProtocolBooks.com/free/{freebie_slug}
```

With UTM parameters per platform:
```
?utm_source={platform}&utm_medium={post_type}&utm_campaign={brand_id}&utm_content={book_id}
```

**Examples:**
- Instagram post: `PhoenixProtocolBooks.com/free/anxiety-corporate-managers-breath-timer-v1?utm_source=instagram&utm_medium=quote_card&utm_campaign=stabilizer_en_us&utm_content=book_042`
- TikTok bio: `PhoenixProtocolBooks.com/free/anxiety-corporate-managers-breath-timer-v1?utm_source=tiktok&utm_medium=bio_link&utm_campaign=stabilizer_en_us`

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
| **English** | "Free guide in bio ↗" | "Get the companion guide free → link in bio" | "Free wellness tools: PhoenixProtocolBooks.com/free/{slug}" |
| **Japanese** | "無料ガイド → プロフリンク" | "��料の実践ガイドをダウンロード → プロフィールのリンクから" | "無料ウェルネスツール: PhoenixProtocolBooks.com/free/{slug}" |
| **Korean** | "무료 가이드 → 프로필 링크" | "무료 실천 가이드 받기 → 프로필 링크에서" | "무료 웰니스 도구: PhoenixProtocolBooks.com/free/{slug}" |
| **Traditional Chinese** | "免費指南 → 個人檔案連結" | "免費下載實踐指南 → 個人檔案連結" | "免費身心工具: PhoenixProtocolBooks.com/free/{slug}" |
| **Simplified Chinese** | "免费指南 → 个人资料链接" | "免费下载实践指南 → 个人资料链接" | "免费身心工具: PhoenixProtocolBooks.com/free/{slug}" |
| **Spanish** | "Guía gratis en bio ↗" | "Descarga la guía complementaria gratis → enlace en bio" | "Herramientas gratis: PhoenixProtocolBooks.com/free/{slug}" |
| **French** | "Guide gratuit → lien en bio" | "Téléchargez le guide gratuit → lien dans la bio" | "Outils gratuits: PhoenixProtocolBooks.com/free/{slug}" |
| **German** | "Kostenloser Guide → Link in Bio" | "Kostenloser Begleitguide herunterladen → Link in Bio" | "Kostenlose Tools: PhoenixProtocolBooks.com/free/{slug}" |
| **Italian** | "Guida gratuita → link in bio" | "Scarica la guida gratuita → link nel profilo" | "Strumenti gratuiti: PhoenixProtocolBooks.com/free/{slug}" |
| **Hungarian** | "Ingyenes útmutató → link a bio-ban" | "Töltsd le az ingyenes útmutatót ��� link a profilban" | "Ingyenes eszközök: PhoenixProtocolBooks.com/free/{slug}" |

---

## 4. Email Proof-Loop Campaign (E1-E5)

When someone downloads a freebie, they enter the **proof-loop email sequence**. 48 Social manages this via GHL.

### The 5-Email Sequence

| Email | Timing | Subject | Content | CTA |
|-------|--------|---------|---------|-----|
| **E1** | Immediate | "Your free {workbook_label} is ready" | Freebie download link + first somatic exercise | "Try this 2-minute exercise now" |
| **E2** | +24 hours | "A second exercise — different mechanism" | Second exercise from the book (different from E1) | "This one works on a different part of your nervous system" |
| **E3** | +72 hours | "Someone's story" | Transformation story from the book's STORY atoms | "Read how this changed for someone like you" |
| **E4** | +48 hours after E3 | "The full book is available" | Book offer with cover art + excerpt + companion info | "Get the full book → {store_link}" |
| **E5** | +7 days after E4 | "More from {brand_name}" | Recommend 2-3 related books from the same brand | "Explore more → {brand_catalog_link}" |

**Psychology:** Demonstrate the mechanism twice (E1 + E2) before offering the book (E4). Minimum 48-hour gap between story and offer.

### Email CTA Links

| Email | CTA URL |
|-------|---------|
| E1 | `PhoenixProtocolBooks.com/free/{slug}#download` (direct download) |
| E2 | `PhoenixProtocolBooks.com/free/{slug}#exercise2` (second exercise) |
| E3 | `PhoenixProtocolBooks.com/free/{slug}#story` (story page) |
| E4 | `{platform_store_link}` (Google Play, Amazon, Apple — varies by lane) |
| E5 | `catalog.phoenixprotocolbooks.com/{brand_id}` (brand catalog) |

### Email Subject Lines by Language

| Email | English | Japanese | Korean | Spanish |
|-------|---------|----------|--------|---------|
| E1 | "Your free guide is ready" | "無料ガイドをお届けします" | "무료 가이드가 준비되었습니다" | "Tu guía gratuita está lista" |
| E2 | "Try a different exercise" | "別のエクササイズを試してみてください" | "다른 운동을 시도해 보세요" | "Prueba un ejercicio diferente" |
| E3 | "Someone's story" | "ある人のストーリー" | "어떤 사람의 이야기" | "La historia de alguien" |
| E4 | "The full book is here" | "完全版の書籍はこちら" | "전�� 책이 여기 있습니다" | "El libro completo está aquí" |
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
- **Email templates:** E1-E5 proof-loop, branded with your colors/logo
- **SMS templates:** Book launch announcements (opt-in only)
- **Funnel pages:** Freebie landing page + thank-you page
- **Social calendar:** 30-50 posts per book, spread across 2-3 weeks
- **Automation workflows:**
  - Freebie download → tag contact → start E1-E5 sequence
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
| Last 10 seconds | Text overlay | "Free {workbook_label}: PhoenixProtocolBooks.com/free/{slug}" |
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
- **Content mix:** 40% quote cards, 25% carousels, 20% Reels clips, 15% Stories
- **Hashtags:** 15-20 per post, mix of broad (#selfcare #mentalhealth) and niche (#nervousystem #somatichealing)
- **Bio link:** Linktree or direct to freebie (rotate with each new book)
- **CTA:** Always in caption, never as only element (Instagram penalizes CTA-only posts)

### 7.2 TikTok
- **Post frequency:** 1-2/day
- **Hook:** First 2 seconds must stop the scroll — text on screen + movement
- **Content:** 60% video clips from book videos, 30% text-on-screen quotes, 10% trending sound + wellness message
- **Hashtags:** 3-5 max (TikTok algorithm prefers fewer, more specific)
- **Bio:** Single link to current freebie

### 7.3 Facebook
- **Post frequency:** 1/day
- **Content:** Link posts to freebie landing page, quote images, short text excerpts
- **Groups:** Join 3-5 relevant wellness/self-help groups, share value (NOT promotional)
- **CTA:** "Download the free guide" with direct link (Facebook allows links in posts)

### 7.4 Twitter/X
- **Post frequency:** 2-3/day (tweets are short-lived)
- **Content:** Quote threads (break one insight into 5-7 tweets), single quotes, engagement polls
- **CTA:** Final tweet in thread: "Full free guide: [link]"
- **Hashtags:** 1-2 per tweet max

### 7.5 Pinterest
- **Post frequency:** 5-10 pins/week (Pinterest is evergreen — pins last months)
- **Content:** Quote cards, book covers, exercise infographics, carousel pins
- **CTA:** Pin description links directly to freebie page
- **Boards:** Create 3-5 boards per brand (Anxiety Tools, Sleep Practices, etc.)

### 7.6 LinkedIn
- **Post frequency:** 2-3/week
- **Content:** Professional framing — "workplace wellness", "executive burnout", "leadership resilience"
- **CTA:** "Free toolkit for professionals → [link]"
- **Best for:** stabilizer, optimizer, executive_calm, career_lift brands

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

## 11. Brand Subdomain Setup (FREE — Automated)

Every brand gets its own unique subdomain for landing pages and email sending. This prevents spam flags and keeps brands isolated.

**Structure:** 1 root domain (`phoenixprotocolbooks.com`) → 312 subdomains (FREE on Cloudflare)

**Per brand:**
| URL | Purpose | Points To |
|-----|---------|-----------|
| `{brand-slug}.phoenixprotocolbooks.com` | Landing pages, freebie funnels | GHL funnels (funnels.msgsndr.com) |
| `mail.{brand-slug}.phoenixprotocolbooks.com` | Email sending (E1-E5 proof loop) | GHL email (Mailgun) |

**Examples:**
- `stabilizer-en-us.phoenixprotocolbooks.com` → Stabilizer brand landing pages
- `inner-light-press-ja-jp.phoenixprotocolbooks.com` → Inner Light Press Japan landing pages
- `mail.zen-clarity-ko-kr.phoenixprotocolbooks.com` → Zen Clarity Korea email sending

**Cost:** $0. Subdomains are free on Cloudflare. SSL auto-generated by GHL.

**Setup:** Automated via `scripts/brand_management/setup_brand_subdomains.py`:
```bash
# Preview all 312 subdomains
python scripts/brand_management/setup_brand_subdomains.py --dry-run

# Create all 624 DNS records (312 landing + 312 email)
python scripts/brand_management/setup_brand_subdomains.py --create
```

**Anti-spam isolation:** Each subdomain has independent sender reputation. If one brand gets flagged, others are unaffected.

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
- [ ] Verify: open `{brand-slug}.phoenixprotocolbooks.com` — landing page loads
- [ ] Verify: receive test email from `mail.{brand-slug}.phoenixprotocolbooks.com`

**After onboarding, brand admin does weekly:**
- [ ] Glance at Monday notification confirming content was published (2 min)
- [ ] Optional: check GHL dashboard Thursday for engagement metrics (3 min)
- [ ] Handle 2FA prompts when platforms require re-authentication (rare)

**Total ongoing weekly effort: 2-5 minutes.**

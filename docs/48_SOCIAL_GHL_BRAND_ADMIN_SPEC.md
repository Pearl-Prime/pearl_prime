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

## 11. Brand Admin Onboarding Checklist

Before your brand goes live, confirm:

- [ ] Platform accounts created (Google Play, YouTube, TikTok, Instagram, + lane-specific)
- [ ] Platform credentials entered in brand admin portal (encrypted, one-time entry)
- [ ] Bank connected via Plaid Link (for revenue collection)
- [ ] 48 Social GHL sub-account configured (email templates, social calendar, funnel pages)
- [ ] Freebie landing page live and tested (freebie downloads, email capture works)
- [ ] First 5 books uploaded to all platforms
- [ ] First 25 social posts reviewed and approved in GHL
- [ ] E1 test email received and links working
- [ ] Bio links set on all social platforms (pointing to freebie URL)
- [ ] Weekly checkin scheduled with Pearl Prime operations team

# Video Distribution and Upload Automation Plan

**Authority:** Pearl_Research + Pearl_Architect
**Date:** 2026-04-05
**Status:** PLAN (not yet implemented)
**Depends on:** channel_registry.yaml, format_specs.yaml, upload_config.yaml, music_policy.yaml, freebie_registry.yaml, brand_archetype_registry.yaml, run_pipeline.py, run_upload.py

---

## Section 1: Video Production Matrix

### 1.1 Channel-to-Brand Mapping and Visual Styles

Each of the 24 channels has an isolated image bank, unique visual style, dedicated TTS voice, and distinct upload window. The table below maps every channel to its production specs across all 5 target platforms plus the existing YouTube long-form.

| CH | Style Name | Brand | Style Family | Emotional Band | TTS Voice | Assembly Profile |
|----|-----------|-------|-------------|----------------|-----------|-----------------|
| ch_001 | Soft Ghibli-esque | stillness_press | calm_healing | cool_calm | en-US-Journey-F | profile_a (4.0s hold, crossfade, lower-third, 9:16-first) |
| ch_002 | Minimalist Line Art | cognitive_clarity | calm_healing | neutral_root | en-US-Neural2-D | profile_b (3.0s hold, cut, full-overlay, 16:9-first) |
| ch_003 | Chibi/Deformed | cognitive_clarity | calm_healing | cool_calm | en-US-Wavenet-F | profile_c (3.5s hold, zoom-dissolve, word-by-word, 9:16-first) |
| ch_004 | Watercolor Wash | stillness_press | calm_healing | cool_calm | en-US-Studio-M | profile_d (5.0s hold, dip-to-black, lower-third, 1:1-first) |
| ch_005 | Kawaii/Cute | cognitive_clarity | calm_healing | warm_rise | en-US-Wavenet-H | profile_e (3.0s hold, crossfade, full-overlay, 9:16-first) |
| ch_006 | Lo-fi/Chill | stillness_press | calm_healing | cool_calm | en-GB-Neural2-B | profile_f (4.5s hold, cut, no caption, 16:9-first) |
| ch_007 | Shonen Action | cognitive_clarity | bold_dynamic | warm_rise | en-US-Polyglot-1 | profile_g (3.0s hold, zoom-dissolve, word-by-word, 9:16-first) |
| ch_008 | Cyberpunk/Sci-Fi | cognitive_clarity | bold_dynamic | neutral_root | en-US-Studio-O | profile_h (3.0s hold, cut, lower-third, 9:16-first) |
| ch_009 | Vintage/Noir | stillness_press | bold_dynamic | cool_calm | en-US-Neural2-J | profile_i (4.0s hold, dip-to-black, lower-third, 16:9-first) |
| ch_010 | Pop Art | cognitive_clarity | bold_dynamic | warm_rise | en-US-Wavenet-I | profile_j (3.0s hold, cut, full-overlay, 9:16-first) |
| ch_011 | Sketchy/Rough | cognitive_clarity | bold_dynamic | warm_rise | en-AU-Neural2-B | profile_k (3.5s hold, crossfade, lower-third, 9:16-first) |
| ch_012 | Retro 80s/90s | stillness_press | bold_dynamic | warm_rise | en-US-Neural2-H | profile_l (3.5s hold, zoom-dissolve, word-by-word, 9:16-first) |
| ch_013 | Geometric/Abstract | cognitive_clarity | abstract_symbolic | neutral_root | en-US-Neural2-A | profile_m (3.0s hold, cut, no caption, 16:9-first) |
| ch_014 | Ink Wash (Sumi-e) | stillness_press | abstract_symbolic | cool_calm | en-US-Neural2-C | profile_n (5.0s hold, dip-to-black, no caption, 16:9-first) |
| ch_015 | Stained Glass | stillness_press | abstract_symbolic | cool_calm | en-GB-Wavenet-A | profile_o (4.5s hold, crossfade, lower-third, 1:1-first) |
| ch_016 | Glitch Art | cognitive_clarity | abstract_symbolic | neutral_root | en-US-Wavenet-D | profile_p (3.0s hold, cut+glitch, full-overlay, 9:16-first) |
| ch_017 | Pointillism | stillness_press | abstract_symbolic | cool_calm | en-AU-Wavenet-C | profile_q (4.0s hold, dip-to-black, lower-third, 9:16-first) |
| ch_018 | Collage | stillness_press | abstract_symbolic | neutral_root | en-GB-Neural2-F | profile_r (4.0s hold, crossfade, lower-third, 1:1-first) |
| ch_019 | Cyberpunk/Steampunk | cognitive_clarity | hybrid_experimental | warm_rise | en-US-Neural2-F | profile_s (3.5s hold, cut, lower-third, 9:16-first) |
| ch_020 | Art Nouveau | stillness_press | hybrid_experimental | warm_rise | en-GB-Wavenet-F | profile_t (4.5s hold, crossfade, full-overlay, 9:16-first) |
| ch_021 | Kawaii-LoFi | cognitive_clarity | hybrid_experimental | cool_calm | en-US-Casual-K | profile_u (3.5s hold, crossfade, word-by-word, 9:16-first) |
| ch_022 | Dark/Moody | stillness_press | hybrid_experimental | cool_calm | en-AU-Neural2-D | profile_v (5.0s hold, dip-to-black, no caption, 16:9-first) |
| ch_023 | Cartoonish/Silly | cognitive_clarity | hybrid_experimental | warm_rise | en-US-News-K | profile_w (3.0s hold, cut, full-overlay, 9:16-first) |
| ch_024 | Surrealist | cognitive_clarity | hybrid_experimental | neutral_root | en-GB-Neural2-D | profile_x (4.0s hold, zoom-dissolve, lower-third, 1:1-first) |

### 1.2 Per-Platform Format Specs (per channel)

**YouTube Long-Form (10 min, 16:9 cinematic)**
- Format key: `long` (900-1800s)
- Resolution: 1920x1080 @ 24fps
- Audio: stereo AAC 256kbps
- Therapeutic mechanism: multi_arc_chapters
- Layer mode: five_layer
- Assembly: uses channel's 16:9-first profile variant
- Chapters: auto-generated from script segment boundaries
- End screen: 20s end card with CTA overlay + subscribe button

**YouTube Shorts (60s, 9:16 portrait)**
- Format key: `short` (15-60s)
- Resolution: 1080x1920 @ 30fps
- Audio: stereo AAC 128kbps
- Therapeutic mechanism: hook_parasympathetic_compressed
- Layer mode: three_layer (L1 + L3 + L5)
- Metadata: auto-append `#Shorts` tag (per upload_config.yaml)
- Max duration: 60s hard cap
- Assembly: 9:16-first profile variant, faster hold times

**TikTok (30-60s, 9:16, faster cuts)**
- Shares `short` format specs (1080x1920 @ 30fps)
- Shorter hold times: reduce channel's default hold by 0.5s (min 2.0s)
- Faster transition cuts: prefer `cut` over `crossfade`/`dip-to-black`
- Hook in first 1.5s (even tighter than Shorts)
- Caption style: word-by-word regardless of channel default (TikTok native feel)
- No end card; CTA is text overlay in final 3s + pinned comment

**Instagram Reels (30-60s, 9:16, text-heavy)**
- Shares `short` format specs (1080x1920 @ 30fps)
- Text overlay density: +30% more on-screen text vs Shorts
- Full-overlay caption style forced for all channels
- Hashtag budget: up to 30 (from upload_config metadata_limits)
- Caption max: 2200 chars
- Story cross-post: first 15s auto-extracted as Story clip

**LINE (60-90s, 9:16, gentler pacing)**
- Resolution: 1080x1920 @ 30fps (short format base)
- Duration: 60-90s (custom; between short and mid)
- Hold times: add +1.0s to channel default (slower, meditative pacing)
- Transitions: prefer `crossfade` and `dip-to-black` (softer)
- QR code overlay: bottom-right corner, final 5s (links to freebie)
- Cultural framing: Japan/Taiwan localized captions (ja, zh-TW from multilang stage)
- No aggressive hooks; opening uses gentle_rise mood

### 1.3 CTA Placement per Format

| Format | CTA Timing | CTA Type | Freebie Reference | URL Placement |
|--------|-----------|---------|-------------------|---------------|
| YT Long | Post-intro (2:00), mid-point, end card (last 20s) | Spoken + text overlay + end screen card | Brand-topic matched from freebie_registry | Description (first 3 lines) + pinned comment + end screen URL |
| YT Shorts | Text overlay final 3s | Text overlay only (no spoken) | Companion workbook or breath timer | Description link only |
| TikTok | Text overlay final 3s + pinned comment | Text overlay + comment link | Assessment or emergency kit (interactive) | Bio link + pinned comment |
| IG Reels | Text overlay at 50% mark and final 3s | Text-heavy overlay | Companion workbook | Caption link-in-bio reference + Story swipe-up |
| LINE | QR code final 5s + spoken mention | QR code overlay + gentle spoken CTA | Guided meditation or breath timer | QR code URL + message body |

### 1.4 Voice/Narrator per Brand (from channel_registry)

Each channel's `tts_voice_id` maps to a Google Cloud TTS or ElevenLabs voice. The channel registry defines 24 unique voice assignments. For video narration:
- YT Long: full narration with channel's TTS voice
- YT Shorts: narration compressed to 60s; same voice, slightly faster pace (+5% speed)
- TikTok: narration at +8% speed; or voiceover-free with text-only for some channels
- IG Reels: narration at normal speed; text overlays supplement
- LINE: narration at -5% speed (gentler pacing); same voice

---

## Section 2: Content-to-Video Pipeline

### 2.1 Pipeline Architecture: Book/Manga to 5 Videos

A single book (plan JSON) produces 5 video variants through the existing VCE pipeline with format-specific branching.

```
Book Plan JSON
    |
    v
[Stage 1] prepare_script_segments.py
    | render_manifest → timed script segments (WPM-based)
    v
[Stage 2] run_shot_planner.py (PER FORMAT)
    | script_segments → shot_plan (visual_intent, hook, pacing)
    | Different pacing configs for: long / short / tiktok / reels / line
    v
[Stage 3] run_asset_resolver.py
    | shot_plan → resolved_assets (from channel's image bank)
    | assets/image_banks/{channel_id}/ — isolated per channel
    v
[Stage 4-8] Timeline → Caption → Layer Compositor → Animation → Soundtrack
    | All stages run per-format with format-specific configs
    v
[Stage 9] CTA Overlay Injection (NEW STAGE)
    | Inject freebie CTA based on: brand × topic × format × freebie_selection_rules
    | Resolve freebie slug, URL, QR code (LINE), text template
    v
[Stage 10] run_qc.py
    | QC per platform requirements:
    |   - Duration bounds (short: 15-60s, long: 900-1800s)
    |   - Resolution match
    |   - Caption contrast >= 4.5
    |   - CTA placement validation
    |   - Asset diversity (no 3+ consecutive same visual_intent)
    v
[Stage 11] run_render.py (FFmpeg)
    | timeline + assets + captions + CTA → rendered MP4
    | Per-format encode settings (CRF, preset from quality_tuning)
    v
[Stage 12-14] Platform Adapter → Multilang → Provenance
    v
[Stage 15] run_platform_adapter.py
    | Generate platform_variants.json with per-platform metadata
    v
[Stage 18] run_upload.py
    | Upload to YouTube / TikTok / IG / LINE via API
```

### 2.2 Format Branching Strategy

The pipeline currently runs linearly for a single format. For multi-format production:

1. **Stage 1 (Script Segments):** Run ONCE per book — segments are format-independent
2. **Stage 2 (Shot Planner):** Run ONCE with base pacing, then derive format variants:
   - `long`: full shot plan, all segments, multi_arc_chapters pacing
   - `short`: select hook + 2-3 strongest segments, compressed to 60s
   - `tiktok`: same as short but tighter hold times (-0.5s)
   - `reels`: same as short but more text overlay slots
   - `line`: select 4-6 segments, gentler pacing (+1.0s holds), 60-90s
3. **Stages 3-8:** Run per-format (different aspect ratios, durations, layer modes)
4. **Stage 9 (CTA):** Format-specific injection rules (see Section 4)
5. **Stage 10+ (QC → Render → Upload):** Per-format, per-platform

### 2.3 Segment Selection for Short-Form Derivatives

For a book with N segments, short-form variants need intelligent selection:

```
Selection algorithm (short/tiktok/reels):
1. Always include segment[0] (hook) — first 8-10s
2. Score remaining segments by:
   - emotional_intensity (from metadata arc_role: climax > build > resolution)
   - exercise_present (EXERCISE slots are demo-friendly for video)
   - text_density (lower is better for short-form)
3. Select top 2-3 segments by score
4. Total duration must fit: short=60s, tiktok=45s, reels=45s, line=75s
5. If over, trim from resolution segments first
```

---

## Section 3: Upload Automation Architecture

### 3.1 Platform API Integration

**YouTube Data API v3** (via `google-api-python-client`)
- Auth: OAuth2 with refresh token (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN)
- Per-brand credentials: suffix pattern from upload_config (e.g., YT_CLIENT_ID_SP for stillness_press)
- Upload: resumable upload, 10MB chunks
- Quota: 10,000 units/day per project; 1 upload = ~1,600 units = ~6 uploads/day/project
- Shorts: same API, add `#Shorts` to title/tags, ensure duration <= 60s
- Metadata: title (100 chars), description (5000 chars), tags (500 chars, max 30)
- Features: chapters (from segment timestamps), end screens, cards, playlists

**TikTok Content Posting API v2**
- Auth: OAuth2 (TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN)
- Upload method: pull-from-URL or direct chunk upload
- Rate limit: 20 videos/day per app
- Metadata: title (150 chars), description (2200 chars), max 30 hashtags
- Max file size: 4GB

**Instagram Graph API v18.0** (via Meta)
- Auth: OAuth2 (IG_ACCESS_TOKEN, IG_USER_ID)
- Upload method: container-publish (create container, poll status, publish)
- Rate limit: 25 posts/day per account
- Max duration: 90s for Reels
- Metadata: caption (2200 chars), max 30 hashtags
- Max file size: 1GB

**LINE Official Account API** (NEW — not yet in upload_config)
- Auth: Channel Access Token (LINE_CHANNEL_ACCESS_TOKEN)
- Upload method: Messaging API rich video message or LINE VOOM post
- Rate limit: platform-specific (LINE VOOM: ~50 posts/day)
- QR code: generated per video with freebie URL encoded
- Locales: ja (Japan), zh-TW (Taiwan)
- NOTE: LINE does not have a standard video upload API like YouTube. Strategy:
  - Option A: Upload to YouTube unlisted, share via LINE rich message with video preview
  - Option B: Use LINE VOOM (timeline) video posting API
  - Option C: Host on CDN, share via LINE Messaging API video message type

### 3.2 Per-Brand Channel Credentials Mapping

From upload_config.yaml `brand_platform_map`:

| Brand | Credential Suffix | YouTube | Shorts | TikTok | IG Reels | LINE |
|-------|------------------|---------|--------|--------|----------|------|
| stillness_press | _SP | yes | yes | yes | yes | planned |
| cognitive_clarity | _CC | yes | yes | yes | yes | planned |

Env var pattern: `{PLATFORM_VAR}_{SUFFIX}` (e.g., `YT_CLIENT_ID_SP`, `TIKTOK_CLIENT_KEY_CC`)

Channels map to brands: each of the 24 channels uses its brand's credentials. Multiple channels under the same brand share the same API project but upload to different YouTube channel handles (managed via channel-specific refresh tokens).

### 3.3 Upload Scheduling

From upload_config.yaml scheduling defaults:
- Base time: 14:00 UTC (6:00 AM PT)
- Publish window: 6-9 AM PT
- Stagger between brands: 15 minutes
- Stagger between platforms: 5 minutes
- Each channel: `upload_window_offset_hours` (0-23) from channel_registry
- Daily cap per channel: 3 uploads (from `daily_upload_cap`)
- Retry: max 3 retries, 60s exponential backoff
- Default: dry-run mode (safety)

**Daily upload schedule per channel:**
```
Channel ch_001 (offset 0h):
  06:00 PT — YouTube Long
  06:05 PT — YouTube Short
  06:10 PT — TikTok

Channel ch_002 (offset 1h):
  07:00 PT — YouTube Long
  07:05 PT — YouTube Short
  07:10 PT — TikTok

... (each channel offset by upload_window_offset_hours)
```

Since daily_upload_cap = 3 per channel, and we have 5 formats, the upload cadence is:
- Day 1: YT Long + YT Short + TikTok (3 uploads)
- Day 2: IG Reels + LINE (2 uploads) + next book's YT Long (1 upload)
- This creates a rolling 2-day cycle per book per channel

### 3.4 Weekly Cadence Calculation

Given 15 new books per week per brand:

```
Per channel (1 channel = 1 topic×style combination):
- Books assigned to this channel per week: ~2-3 (15 books / ~6 channels per brand)
- Videos per book: 5 formats
- Total videos per channel per week: 10-15
- Upload cap: 3/day × 7 days = 21/week → fits 10-15 videos

Per brand (e.g., stillness_press has ch_001, ch_004, ch_006, ch_009, ch_012, ch_017, ch_018, ch_020, ch_022):
- 9 channels × ~15 videos/channel/week = ~135 videos/brand/week
- YouTube quota constraint: 6 uploads/day/project × 7 = 42/week
  → Need separate YouTube API projects per 2-3 channels, OR stagger across days
  → RECOMMENDATION: 1 YouTube API project per brand, upload 6/day rotating across channels

Per platform (all 24 channels):
- YouTube Long: 24 channels × ~2.5 books/week = ~60 long videos/week
- YouTube Shorts: ~60 shorts/week
- TikTok: ~60/week
- IG Reels: ~60/week
- LINE: ~60/week (Japan/Taiwan subset only; ~10 channels × ~15 = ~150, but LINE is lower priority)
- TOTAL: ~300 videos/week across all platforms
```

---

## Section 4: Freebie CTA Strategy per Video

### 4.1 Freebie-to-Brand-Topic Matching

From freebie_registry.yaml and freebie_selection_rules.yaml:

**Rule 1 (Companion):** Books >= 60 min get companion_workbook_pdf → CTA in YT Long
**Rule 2 (Somatic):** Books with EXERCISE slot get somatic_html_tool → CTA in all short-form
**Rule 3 (Assessment):** Engine in anxiety/burnout/shame → assessment_html → CTA in TikTok/Reels

**Priority matching by persona:**
- Structured (executives, healthcare, educators): breath_reset_structured_v1, burnout_checklist_v1, shame_assessment_v1
- Interactive (gen_z, gen_alpha): breath_timer_v1, anxiety_assessment_v1, emergency_kit_v1

### 4.2 CTA Templates per Format

**YouTube Long-Form:**
```
[Spoken CTA at 2:00 mark]
"This book has a companion {workbook_label} with all the exercises and reflection prompts.
You can get it free at PhoenixProtocolBooks.com/free/{slug}."

[End Card — final 20s]
Text overlay: "Download your free {freebie_type} → link in description"
End screen card: subscribe + freebie URL

[Description — first 3 lines]
"Get the free companion {workbook_label}: PhoenixProtocolBooks.com/free/{slug}?utm_source=youtube&utm_medium=video&utm_campaign={brand}"
```

**YouTube Shorts:**
```
[Text overlay — final 3s]
"Free {freebie_type} → link in description"

[Description]
"PhoenixProtocolBooks.com/free/{slug}?utm_source=youtube_shorts&utm_medium=video&utm_campaign={brand}"
```

**TikTok:**
```
[Text overlay — final 3s]
"Free tool in bio"

[Pinned comment]
"Get the free {freebie_type}: PhoenixProtocolBooks.com/free/{slug}?utm_source=tiktok&utm_medium=video&utm_campaign={brand}"

[Bio link]
LinkTree or direct URL to freebie landing page
```

**Instagram Reels:**
```
[Text overlay — at 50% mark]
"Free {freebie_type} — link in bio"

[Text overlay — final 3s]
"PhoenixProtocolBooks.com/free/{slug}"

[Caption]
"...Get the free {freebie_type} → link in bio
PhoenixProtocolBooks.com/free/{slug}?utm_source=instagram&utm_medium=reels&utm_campaign={brand}"
```

**LINE:**
```
[QR code overlay — final 5s, bottom-right]
QR encodes: PhoenixProtocolBooks.com/free/{slug}?utm_source=line&utm_medium=video&utm_campaign={brand}

[Gentle spoken CTA — final 10s]
"If you'd like to go deeper, scan the QR code or visit the link in the message below."

[Message body]
Freebie URL with ja/zh-TW localized description
```

### 4.3 URL Pattern

```
Base: PhoenixProtocolBooks.com/free/{slug}
UTM:  ?utm_source={platform}&utm_medium=video&utm_campaign={brand_id}

Where:
  {slug} = {topic}-{persona}-{primary_freebie}
  {platform} = youtube | youtube_shorts | tiktok | instagram | line
  {brand_id} = stillness_press | cognitive_clarity
```

### 4.4 CTA Delivery Mechanisms by Platform

| Platform | End Card | Pinned Comment | Description Link | Bio Link | QR Code | Spoken CTA |
|----------|---------|---------------|-----------------|---------|---------|-----------|
| YT Long | yes | yes | yes (first 3 lines) | n/a | no | yes (post-intro + back-matter) |
| YT Shorts | no | no | yes | n/a | no | no |
| TikTok | no | yes | n/a | yes | no | no |
| IG Reels | no | no | n/a | yes | no | no |
| LINE | no | n/a | n/a | n/a | yes | yes (gentle) |

---

## Section 5: Weekly Production Schedule

### 5.1 Volume Calculations

```
Given: 15 new books/week per brand, 3 active brands, 24 total channels

Per brand:
  15 books × 5 formats = 75 videos/brand/week

All brands:
  75 × 3 brands = 225 videos/week (content-brand level)
  But channels overlap brands, so per channel:
  ~2-3 books/week × 5 formats = 10-15 videos/channel/week

Total across all 24 channels:
  24 channels × ~12.5 avg = ~300 videos/week
```

### 5.2 Upload Cadence

Per platform per channel: 2-3 uploads/day

```
YouTube Long:    1 per channel every 2-3 days  → ~3/week/channel
YouTube Shorts:  1 per channel per day          → ~7/week/channel (limited by cap to 3/day across all formats)
TikTok:          1 per channel per day          → ~7/week/channel
IG Reels:        1 per channel every 2 days     → ~4/week/channel
LINE:            1 per channel every 3 days     → ~2/week/channel

Actual per-channel daily budget (daily_upload_cap = 3):
  Day 1: YT Long + YT Short + TikTok
  Day 2: IG Reels + LINE + YT Short (next book)
  Day 3: TikTok (next book) + YT Long (next book) + IG Reels
  ... rolling pattern
```

### 5.3 Stagger Schedule

To avoid audience fatigue (same brand posting to same platform simultaneously):
- Each channel has unique `upload_window_offset_hours` (0-23), ensuring no two channels upload at the same time
- Within a channel: 5-minute gaps between platform uploads
- Between brands on same platform: 15-minute gaps

### 5.4 Buffer Strategy

Build 2 weeks ahead:
- Week N: Render videos for books from Week N+2
- Week N+1: QC review, fix rejects, stage uploads
- Week N+2: Automated daily uploads from buffer

Buffer depth: 2 weeks × 300 videos = 600 pre-rendered videos in staging

### 5.5 Priority Order

When buffer is thin or catch-up is needed:
1. **YouTube Long** — highest SEO value, longest shelf life, strongest freebie CTA
2. **YouTube Shorts** — discoverability funnel, drives subscribers to Long content
3. **TikTok** — broadest reach for Gen Z personas
4. **Instagram Reels** — text-heavy format good for carousel cross-promotion
5. **LINE** — Japan/Taiwan market only; lower volume, higher per-viewer value

---

## Section 6: Platform-Specific Adaptations

### 6.1 YouTube Long-Form

- **Chapters:** Auto-generate from script_segments boundaries; format as `00:00 Hook`, `02:15 Chapter 1: {segment_title}`, etc. in description
- **End Screens:** 20s end card programmed via YouTube Studio API; link to freebie + next video + subscribe
- **Cards:** In-video interactive cards at CTA moments (post-intro, mid-point); link to freebie landing page
- **Description:** Structured template:
  ```
  Line 1: Freebie CTA URL
  Line 2: One-sentence book summary
  Line 3: Chapters (timestamps)
  Lines 4+: Extended description with keywords
  Bottom: Hashtags (5-8 relevant)
  ```
- **Playlists:** Auto-add to brand playlist by topic (e.g., "Stillness Press — Anxiety")
- **Thumbnails:** Auto-extracted from `thumbnail_frame_ref` in timeline; custom text overlay with title

### 6.2 YouTube Shorts

- **Hook:** First 2s must be visually arresting — use highest-contrast frame from hook segment; text overlay with question or statement
- **No end screen:** Shorts do not support end screens; CTA is text overlay only
- **Text overlay CTA:** Persistent lower-third in final 3s: "Free [tool] — link in description"
- **Caption style:** Word-by-word animation (matches TikTok native feel)
- **Auto-loop friendly:** Last frame should visually connect to first frame where possible
- **Title:** Include `#Shorts` tag (auto-appended by upload_config)

### 6.3 TikTok

- **Trending sounds:** Soundtrack engine checks trending audio catalog (Phase 2 — manual curation initially); fallback to original brand soundtrack
- **Faster cuts:** Hold times reduced by 0.5s from channel default; minimum 2.0s per shot
- **Hashtag strategy:** 5-8 hashtags from:
  - Topic-specific: #anxiety, #burnout, #mentalhealth
  - Persona-specific: #corporatelife, #entrepreneurmindset, #studentlife
  - Trending: pulled from TikTok Creative Center API (Phase 2)
  - Brand: #{brand_id}
- **Duet-friendly:** Leave visual space in left 30% for duet reactions (optional; controlled by assembly profile)
- **Hook:** First 1.5s — text question overlay + visually dynamic opening shot
- **Pinned comment:** Auto-post comment with freebie link after upload (via TikTok API comment endpoint)

### 6.4 Instagram Reels

- **Carousel-friendly:** Extract 3-5 key frames from video as carousel images (for cross-posting as carousel post); each frame has text overlay summary
- **Text-heavy:** +30% more on-screen text compared to Shorts/TikTok; captions are full-overlay style forced
- **Story cross-post:** Auto-extract first 15s as Instagram Story; add "See full Reel" sticker
- **Caption:** Rich caption with paragraph breaks, emojis (brand-appropriate), and 20-30 hashtags
- **Cover image:** First frame with title text overlay (not auto-extracted; custom generated)

### 6.5 LINE

- **Softer pacing:** +1.0s to all hold times; prefer crossfade and dip-to-black transitions
- **QR codes:** Generated with `qrcode` Python library; encoded URL includes UTM params; overlaid bottom-right for final 5s
- **Japan/Taiwan cultural framing:**
  - Use ja/zh-TW localized captions from multilang stage
  - Softer emotional vocabulary (avoid aggressive self-help language)
  - Opening: gentle question or observation rather than bold statement
  - Colors: softer palette variants where available
- **Distribution:** Via LINE Official Account → Rich Video Message to followers, and LINE VOOM timeline post
- **Frequency:** Lower than other platforms; 1-2 per channel per week to respect LINE communication norms

---

## Section 7: Integration Checklist

### 7.1 YouTube Upload (via google-api-python-client)

Pearl_Int must wire:
- [ ] Install `google-api-python-client`, `google-auth-oauthlib`
- [ ] Set up OAuth2 credentials per brand:
  - `YT_CLIENT_ID_{suffix}`, `YT_CLIENT_SECRET_{suffix}`, `YT_REFRESH_TOKEN_{suffix}`
  - Suffix: `_SP` (stillness_press), `_CC` (cognitive_clarity)
- [ ] Implement resumable upload with 10MB chunks (already specified in upload_config)
- [ ] Implement metadata setting: title, description, tags, category, privacy status
- [ ] Implement chapter timestamps in description
- [ ] Implement end screen API calls (YouTube Studio API)
- [ ] Implement playlist management (create per brand×topic, auto-add)
- [ ] Handle quota exhaustion (retry after 3600s per upload_config)
- [ ] Existing: `scripts/video/uploaders/` module with UPLOADERS registry and UploadResult

### 7.2 TikTok Upload (via Content Posting API v2)

Pearl_Int must wire:
- [ ] Set up OAuth2 credentials per brand:
  - `TIKTOK_CLIENT_KEY_{suffix}`, `TIKTOK_CLIENT_SECRET_{suffix}`, `TIKTOK_ACCESS_TOKEN_{suffix}`
- [ ] Implement two upload methods:
  - Pull-from-URL (host rendered video on CDN, TikTok pulls)
  - Direct chunk upload (fallback)
- [ ] Implement metadata: title, description, hashtags, privacy level
- [ ] Implement pinned comment posting after upload
- [ ] Handle rate limit: 20/day per app, retry after 60s
- [ ] Existing: `scripts/video/uploaders/` likely has TikTok stub

### 7.3 Instagram Upload (via Graph API v18.0)

Pearl_Int must wire:
- [ ] Set up OAuth2 credentials per brand:
  - `IG_ACCESS_TOKEN_{suffix}`, `IG_USER_ID_{suffix}`
- [ ] Implement container-publish flow:
  1. POST to `/{ig_user_id}/media` with video URL + caption → container_id
  2. Poll container status until FINISHED
  3. POST to `/{ig_user_id}/media_publish` with container_id
- [ ] Max duration: 90s; max file size: 1GB
- [ ] Handle rate limit: 25/day, retry after 300s
- [ ] Implement Story cross-post (separate container for Stories)

### 7.4 LINE Upload (via Messaging API)

Pearl_Int must wire:
- [ ] Set up LINE Official Account per brand (Japan/Taiwan market):
  - `LINE_CHANNEL_ACCESS_TOKEN_{suffix}`
- [ ] Determine best video delivery method:
  - Option A: Upload to YouTube (unlisted), share rich message with preview
  - Option B: LINE VOOM posting API for timeline videos
  - Option C: Host on CDN (S3/CloudFront), share via video message type
- [ ] Implement QR code generation (Python `qrcode` library)
- [ ] Implement localized message templates (ja, zh-TW)
- [ ] LINE VOOM rate limits: research and document

### 7.5 Rate Limits and Quotas Summary

| Platform | Daily Limit | Per Upload Cost | Effective Daily Max | Retry Wait |
|----------|------------|----------------|--------------------:|-----------|
| YouTube | 10,000 quota units | ~1,600 units | 6 uploads | 3600s |
| TikTok | 20 videos/app | 1 video | 20 uploads | 60s |
| Instagram | 25 posts/account | 1 post | 25 uploads | 300s |
| LINE VOOM | ~50 posts/day (est.) | 1 post | 50 uploads | TBD |

### 7.6 Credential Requirements per Platform per Brand

Total env vars needed for 3 brands × 4 platforms:

```
YouTube (3 vars × 3 brands = 9):
  YT_CLIENT_ID_SP, YT_CLIENT_SECRET_SP, YT_REFRESH_TOKEN_SP
  YT_CLIENT_ID_CC, YT_CLIENT_SECRET_CC, YT_REFRESH_TOKEN_CC
  YT_CLIENT_ID_ND, YT_CLIENT_SECRET_ND, YT_REFRESH_TOKEN_ND

TikTok (3 vars × 3 brands = 9):
  TIKTOK_CLIENT_KEY_SP, TIKTOK_CLIENT_SECRET_SP, TIKTOK_ACCESS_TOKEN_SP
  TIKTOK_CLIENT_KEY_CC, TIKTOK_CLIENT_SECRET_CC, TIKTOK_ACCESS_TOKEN_CC
  TIKTOK_CLIENT_KEY_ND, TIKTOK_CLIENT_SECRET_ND, TIKTOK_ACCESS_TOKEN_ND

Instagram (2 vars × 3 brands = 6):
  IG_ACCESS_TOKEN_SP, IG_USER_ID_SP
  IG_ACCESS_TOKEN_CC, IG_USER_ID_CC
  IG_ACCESS_TOKEN_ND, IG_USER_ID_ND

LINE (1 var × 3 brands = 3):
  LINE_CHANNEL_ACCESS_TOKEN_SP
  LINE_CHANNEL_ACCESS_TOKEN_CC
  LINE_CHANNEL_ACCESS_TOKEN_ND

TOTAL: 27 credential env vars (stored in GitHub Secrets, injected at CI runtime)
```

---

## Appendix A: New Components Required

### A.1 New Stages to Build

1. **CTA Overlay Injector** (`scripts/video/run_cta_injector.py`):
   - Input: timeline.json + freebie_selection output + brand config
   - Output: cta_overlay.json (timing, text, position, QR code data)
   - Integrates into render pipeline between animation_engine and QC

2. **Short-Form Segment Selector** (`scripts/video/select_shortform_segments.py`):
   - Input: script_segments.json (full book) + target duration
   - Output: script_segments_short.json (selected subset)
   - Algorithm: hook + top-scored segments by emotional intensity

3. **QR Code Generator** (`scripts/video/generate_qr.py`):
   - Input: freebie URL + UTM params
   - Output: QR code PNG for LINE overlay

4. **LINE Uploader** (`scripts/video/uploaders/line_uploader.py`):
   - New uploader module for LINE VOOM / Messaging API

### A.2 Config Files to Add

1. `config/video/line_config.yaml` — LINE-specific format specs, pacing overrides, QR placement
2. `config/video/cta_templates.yaml` — per-format CTA text templates (extend companion_workbook_platform_content.yaml for video)
3. `config/video/shortform_selection_rules.yaml` — segment selection scoring weights

### A.3 Upload Config Updates

Add to `upload_config.yaml`:
- `line` platform block with API endpoint, auth, rate limits
- Per-channel LINE-specific upload windows for Japan/Taiwan timezone alignment
- Update `brand_platform_map` with `line: true/false` per brand

---

## Appendix B: Implementation Priority

### Phase 1 (Week 1-2): Core Multi-Format Pipeline
- Build short-form segment selector
- Add format branching to run_pipeline.py (run per format)
- Validate YouTube Long + Shorts end-to-end

### Phase 2 (Week 3-4): TikTok + Instagram
- Wire TikTok uploader with Pearl_Int credentials
- Wire Instagram uploader with container-publish flow
- Build CTA overlay injector

### Phase 3 (Week 5-6): LINE + QR + Buffer
- Build LINE uploader
- Implement QR code generation
- Build 2-week buffer system with staging directory
- Wire automated daily upload cron

### Phase 4 (Week 7-8): Scale + Monitoring
- Upload monitoring dashboard (analytics_ingestor integration)
- Quota tracking and auto-throttle
- A/B test CTA placements across platforms
- Trending audio integration for TikTok (Phase 2 of soundtrack engine)

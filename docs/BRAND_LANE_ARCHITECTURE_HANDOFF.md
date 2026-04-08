# Brand Lane Architecture — Handoff Document

**Date:** 2026-04-07
**Author:** Pearl_GitHub + Pearl_Architect session
**Status:** Architecture complete, 4/13 teacher brands fully expanded, 9 skeleton
**Next action:** Expand 9 skeleton teacher brands to full author profiles

---

## What Was Built

A complete global brand distribution architecture for Phoenix Omega: 37 publishing imprints across 12 worldwide markets, with audiobook video production pipeline and balanced upload cadence.

---

## 1. The Architecture (Read This First)

### Core Rule

**1 teacher per brand. Everywhere. No exceptions.**

A brand is a nonprofit publishing imprint. Each brand publishes content from exactly one teacher (teacher mode) or one persona archetype (standard mode). If Brand A publishes Teacher X on Google Play, no other brand on Google Play can publish Teacher X.

### Numbers

| Dimension | Count |
|-----------|-------|
| Brand lanes (addressable markets) | 12 |
| Brands per lane | 37 (13 teacher + 24 standard) |
| Total brand instances worldwide | 444 |
| Teachers | 13 |
| Authors per teacher brand | 5–9 (91 total) |
| Authors per standard brand | 8 (192 total EN) |
| Total EN authors | 283 |

### The 12 Brand Lanes

| # | Lane | Markets | Language | Key Platforms |
|---|------|---------|----------|---------------|
| 1 | English Global | US, UK, CA, AU, NZ | English | KDP, Audible US, Google Play, Apple, Kobo, Spotify |
| 2 | DACH | Germany, Austria, Switzerland | German | Audible DE, Thalia, Storytel |
| 3 | France | France, Belgian FR, Swiss FR | French | Audible FR, Storytel |
| 4 | Spain | Spain | Castilian Spanish | KDP, Storytel |
| 5 | Italy | Italy | Italian | Audible IT, Storytel |
| 6 | Latin America | Mexico, Colombia, Argentina, Chile, etc. | LATAM Spanish | KDP, Google Play, Spotify |
| 7 | Brazil | Brazil | BR Portuguese | Audible BR, Tocalivros, Ubook |
| 8 | Japan | Japan | Japanese | Audible JP, audiobook.jp, Kobo JP |
| 9 | Korea | South Korea | Korean | Naver, Millie's, Kakao Page, Ridi |
| 10 | Taiwan | Taiwan | Traditional Chinese | Readmoo, KKBox, Books.com.tw |
| 11 | China | Mainland + HK + Singapore | Simplified + Traditional Chinese | Ximalaya, WeChat Read, Dedao |
| 12 | Hungary | Hungary | Hungarian | Google Play, Kobo |

**Why these lanes?** Each lane is an addressable market where catalog is isolated. Google Play is global (one lane), but Audible DE is separate from Audible US (different lane). China is completely isolated behind the Great Firewall (requires MCN agent). Korea's domestic platforms dominate over global ones. Each lane can have the same 37 brand names with a locale suffix.

### The 37 Brands

#### 13 Teacher Mode Brands (1 teacher each, gets ALL content)

| Brand ID | Publisher Name | Teacher | Unique Angle |
|----------|---------------|---------|--------------|
| stillness_press | Stillness Press | Ahjan | Alarm recognition — "see the alarm for what it is" |
| cognitive_clarity | Clear Seeing Books | Joshin | Zen inquiry — "stop believing the thinker" |
| norcal_dharma | NorCal Dharma Press | Ajahn X | Forest simplicity — "enough already exists" |
| somatic_wisdom | Felt Sense Publishing | Pamela Fellows | Polyvagal science — "the body already knows" |
| qi_foundation | Root & Meridian Press | Master Feung | Qi cultivation — "rebuild from the root" |
| digital_ground | Present Tense Books | Miki | Gen Z mindfulness — "exist without the phone" |
| heart_balance | Feather & Scale Press | Maat | Egyptian shadow work — "speak what the heart knows" |
| relational_calm | Bare Form Books | Junko | Radical acceptance — "nothing extra, nothing missing" |
| warrior_calm | Iron Gate Press | Master Wu | Martial composure — "the fiercer the pressure, the stiller you become" |
| sleep_restoration | Night Architecture Books | Master Sha | Energy medicine — "sleep is not something you force" |
| body_memory | Held Ground Press | Omote | Body grief — "where the body keeps what the mind released" |
| solar_return | Ember & Ash Publishing | Ra | Burnout as initiation — "what grows after the burn" |
| devotion_path | Open Vessel Press | Sai Ma | Bhakti devotion — "for those who forgot to include themselves" |

#### 24 Standard Mode Brands (pen-name authors, no teacher)

| Brand ID | Publisher Name | Persona | Emotional Job |
|----------|---------------|---------|---------------|
| stabilizer | Harbor Line Books | burned_out_professional | calm nervous system |
| optimizer | Daybreak Editions | high_efficiency_achiever | feel ahead of the day |
| night_reset | Still Hour Press | insomniac_creative | stop dreading the night |
| career_lift | Next Chapter Press | mid_career_stalled | feel unstuck |
| adhd_forge | Livewire Books | neurodivergent_young_adult | stop feeling broken |
| longevity_lab | Long Arc Press | longevity_seeker | feel in control of aging |
| creative_unfold | Blank Canvas Books | artistic_student | creative confidence |
| resilient_parent | Stolen Moment Press | overwhelmed_parent | feel like a person again |
| executive_calm | Granite Ridge Publishing | corporate_leader | steady under pressure |
| trauma_path | Soft Ground Books | trauma_recovery_adult | feel safe in body |
| spiritual_ground | Deep Well Publishing | spiritually_curious | connection to something larger |
| focus_sprint | Launchpad Press | startup_founder | sustain without burning |
| hormone_reset | Tide & Cycle Books | women_35_plus | feel in control of body |
| stoic_edge | Anvil Books | young_male_growth | mental toughness |
| calm_student | Blue Exam Press | gen_z_student | stop spiraling |
| healing_ground | Midday Press | chronic_stress_worker | midday reset |
| bio_flow | Signal Path Books | biohacker | optimize and feel good |
| confidence_core | Threshold Books | socially_anxious_adult | feel okay showing up |
| relationship_clarity | Two Chairs Press | couples_repair | repair and reconnect |
| morning_momentum | First Light Publishing | early_riser_professional | own the morning |
| minimal_mind | Clearwater Books | digital_overwhelm_adult | feel less scattered |
| high_performer | Close Rate Press | competitive_sales | confident under pressure |
| gentle_growth | Tender Root Books | therapy_newcomer | safe place to start |
| legacy_builder | Second Mountain Press | 45_plus_reinventor | meaning in next chapter |

### Anti-Spam Differentiation

Every teacher brand has a documented reason WHY it doesn't overlap with any standard brand. Example:

- **Stillness Press** (Ahjan) vs **Harbor Line Books** (stabilizer): "Stabilizer calms the nervous system. Stillness Press teaches you to SEE the alarm — recognition before regulation."
- **Iron Gate Press** (Master Wu) vs **Granite Ridge Publishing** (executive_calm): "Executive Calm is boardroom steady. Iron Gate is battlefield still — for when steady isn't enough."

Full differentiation matrix: `config/catalog_planning/teacher_brand_archetypes.yaml`

---

## 2. File Map

### Core Architecture Files

| File | What It Defines | Read Order |
|------|----------------|------------|
| `config/catalog_planning/teacher_brand_lane_assignments.yaml` | **Master config.** 12 lanes, 37 brands per lane, locale suffixes, platform lists, market sizes. The single source of truth for "what brand goes where." | 1st |
| `config/catalog_planning/brand_teacher_matrix.yaml` | Teacher constraints per brand (max books per topic/persona). Updated: all 13 teachers assigned. | 2nd |
| `config/catalog_planning/teacher_brand_archetypes.yaml` | 13 teacher brand definitions with unique persona × topic × emotional_job and anti-spam differentiation vs every nearby standard brand. | 3rd |
| `config/catalog_planning/brand_archetype_registry.yaml` | 24 standard brand definitions (existing, predates this work). | 4th |

### Brand Identity Files

| File | What It Defines |
|------|----------------|
| `config/catalog_planning/brand_identity_system.yaml` | Visual identity for all 37 brands: colophon mark, 2 primary colors + accent, display + body font, cover template, texture, mood description, cover art style description. |
| `config/catalog_planning/brand_display_names.yaml` | English publisher imprint names + taglines for all 37. |
| `config/catalog_planning/locale_brand_names.yaml` | Culturally native publisher names for all 37 brands × 12 lanes = 444 names. Uses correct local publisher naming conventions (社 for Japan, Verlag for Germany, Éditions for France, etc.). |

### Author Roster

| File | What It Defines |
|------|----------------|
| `config/catalog_planning/teacher_brand_author_roster.yaml` | 91 authors across 13 teacher brands. 4 brands fully expanded (individual bios, voice IDs, settings, topics, personas, portrait presets, cover styles). 9 brands skeleton (voice palette + topic spread, no individual authors yet). |

### Audiobook Video Pipeline

| File | What It Does |
|------|-------------|
| `scripts/video/render_audiobook.py` | FFmpeg renderer: black bg + white serif text + waveform + audio → MP4. Descript-style visual. Takes audio + optional transcript, uses Whisper alignment. |
| `scripts/video/align_transcript.py` | Word-level forced alignment via stable-ts (Whisper). Falls back to WPM estimation. |
| `scripts/video/generate_karaoke_ass.py` | Generates ASS subtitle file with `\kf` karaoke timing tags. Word-by-word white→gray highlighting. |
| `scripts/video/orchestrate_book_to_video.py` | End-to-end: book MP3 + transcript → chapter splits → long-form + short clips + upload schedule JSON. |
| `scripts/release/generate_video_schedule.py` | Week-by-week video upload scheduler. Respects per-platform caps, cross-brand spacing, ramp-up phases. Outputs revenue estimates. |

### Video/Upload Configs

| File | What It Defines |
|------|----------------|
| `config/video/format_specs.yaml` | Added `audiobook` (16:9, 5-90min) and `audiobook_short` (9:16, 30-60s) formats. |
| `config/video/audiobook_style.yaml` | Visual presets: default (black/white/grey), warm (grief topics), cool (anxiety topics). Topic→style mapping. |
| `config/release_velocity/video_cadence.yaml` | Platform upload pacing. YT: 1 long/day + 2-3 shorts/day. TikTok: 3/day. IG Reels: 2/day. Cross-brand: 4h minimum gap. Book drip: shorts start 3 days before chapter 1, full audiobook drops day 21. |
| `config/catalog_planning/audiobook_video_catalog.yaml` | Video derivatives per book (20 long + 40 short + 1 full = 61). Revenue model ($12 RPM for long, $0.05/1K for shorts). Phase 1-3 projections. |

---

## 3. What Works (Tested)

### Audiobook Video Renderer ✅

Tested with Maat WAV (24 min audiobook). Produces Descript-style video matching reference examples.

```bash
export PATH="/opt/homebrew/bin:$PATH"
python3 scripts/video/render_audiobook.py \
  --audio /path/to/chapter.mp3 \
  --format long --style default \
  --clip-start 10 --clip-end 40 \
  --quality draft --whisper-model tiny \
  -o output.mp4
```

Output: black background + white Georgia serif text + amplitude-reactive waveform at bottom + synced audio. Word-by-word karaoke highlighting (white = current word, gray = trailing).

Demo file: `~/Desktop/maat_audiobook_video_demo.mp4`

### Video Schedule Generator ✅

```bash
python3 scripts/release/generate_video_schedule.py --lane en --phase 1 --weeks 12 --dry-run
```

Output:
```
Lane: en | Phase: 1 | 12 weeks
Total videos: 1,142
Avg/week: 95
Revenue est: $1,412.87
Daily throughput: youtube_long=5, youtube_shorts=10, tiktok=3, instagram_reels=2, total=20
Weeks to drain all 354 books' videos: 154.2
```

Ramp: Week 1 at 20% (28 videos) → Week 12 at 100% (140 videos). All 13 teachers rotate evenly.

---

## 4. What's Not Done (Next Sprint)

### Priority 1: Expand 9 Skeleton Teacher Brands

These brands have voice palettes and topic spreads but NO individual author profiles yet:

| Brand | Teacher | Authors Needed |
|-------|---------|---------------|
| Root & Meridian Press | Master Feung | 7 |
| Present Tense Books | Miki | 6 |
| Feather & Scale Press | Maat | 6 |
| Bare Form Books | Junko | 5 |
| Iron Gate Press | Master Wu | 7 |
| Night Architecture Books | Master Sha | 6 |
| Held Ground Press | Omote | 6 |
| Ember & Ash Publishing | Ra | 6 |
| Open Vessel Press | Sai Ma | 6 |
| **Total** | | **55 authors** |

**Each author needs:**
1. `author_id` (snake_case, unique)
2. `display_name` (culturally appropriate pen name)
3. `positioning` (somatic_companion / research_guide / elder_stabilizer)
4. `voice_id` (ElevenLabs voice ID — pick from brand's `voice_palette`, never reuse across brands)
5. `voice_settings` (stability, similarity_boost, style — follow content-type table below)
6. `topics` (2-4 from 15 canonical, must spread across brand's `topic_spread`)
7. `personas` (2-3 from 10 canonical)
8. `bio` (120-180 words, third person, ties lived experience to topic authority)
9. `portrait_preset` (one of: contemplative, grounded, radiant, authority, energetic, scientific, warm_intimate, stoic_minimal, youthful_peer, legacy_wisdom)
10. `cover_style` (1-2 sentences describing cover art using brand palette from `brand_identity_system.yaml`)

**Voice settings by content type:**

| Content | Stability | Style | Notes |
|---------|-----------|-------|-------|
| Meditation/somatic | 0.60-0.75 | 0.0-0.1 | Consistent calm |
| Grief/trauma | 0.55-0.70 | 0.1-0.2 | Slightly more range |
| Executive/authority | 0.70-0.85 | 0.1-0.3 | Authoritative consistency |
| Gen Z/casual | 0.40-0.55 | 0.3-0.5 | Conversational |
| Long-form nonfiction | 0.65-0.80 | 0.1-0.2 | Clean delivery |

**Reference:** The 4 fully expanded brands (Stillness Press, Clear Seeing Books, NorCal Dharma, Felt Sense Publishing) in `teacher_brand_author_roster.yaml` show exactly how to do this.

### Priority 2: Register Brands in Existing Systems

The new teacher brands need entries in:
- `config/brand_registry.yaml` (add 10 new brands — stillness_press, cognitive_clarity, norcal_dharma already exist)
- `config/brand_author_assignments.yaml` (add author pools per brand)
- `config/brand_narrator_assignments.yaml` (add default narrator per brand)
- `config/voice_author_lock_table.yaml` (add voice locks for all 91 authors)

### Priority 3: Generate Author Assets

For each of the 91 teacher brand authors:
- `config/authoring/author_registry.yaml` — add entry
- `assets/authors/cover_art/{author_id}_base.png` — generate via FLUX/RunComfy
- `config/authoring/author_pic_prompts.yaml` — add portrait prompt
- Author bio YAML files (per `AUTHOR_ASSET_WORKBOOK.md`)

### Priority 4: Wire Audiobook Video to Production Pipeline

The `render_audiobook.py` works standalone. It needs to be wired into:
- `scripts/video/run_pipeline.py` — add `--format audiobook` path that skips image stages
- `scripts/video/orchestrate_book_to_video.py` → should be callable from the main `run_pipeline.py`
- The book pass system should trigger video production after audiobook MP3 download

### Priority 5: Locale Brand Registration

444 brand names exist in `locale_brand_names.yaml` but need:
- Platform account creation per lane (KDP accounts, Google Play, Audible DE/JP, etc.)
- ISBN assignment per locale
- `config/localization/brand_registry_locale_extension.yaml` entries
- MCN agent setup for China lane

---

## 5. Key Decisions Made (Do Not Reverse)

1. **1 teacher per brand, everywhere.** This was explicitly discussed and confirmed by the owner. No multi-teacher brands, even on regional platforms, because same-platform overlap of obscure teachers triggers anti-spam.

2. **37 brands per lane = 13 teacher + 24 standard.** Matches the "Phoenix 24-Brand Governance Architecture" (the 24 standard brands existed before teacher mode was added). Teacher brands are additive.

3. **12 brand lanes, not 13.** China lane covers mainland + HK + Singapore (one isolated ecosystem). Hungary gets its own lane despite small size (minimal competition = easy ranking). Brazil and LATAM are separate lanes (different language, different platforms, different narration).

4. **Locale naming follows local publisher conventions.** Japanese brands use 社/出版/堂 suffix. German brands use Verlag. French use Éditions prefix. Not translated English — culturally native. See `locale_brand_names.yaml`.

5. **Audiobook video format = Descript style.** Black background, white serif text (Georgia), word-by-word karaoke, amplitude waveform at bottom. Three style presets: default, warm (grief), cool (anxiety). Tested and verified against reference videos.

6. **Upload cadence is conservative.** 20 videos/day total across platforms (5 long + 15 shorts). Ramps from 20% to 100% over 12 weeks. One book's 61 videos drip over 60 days. Cross-brand spacing: 4 hours minimum between different brands on same platform.

---

## 6. Reference Examples

### 3 Audiobook Reference Files

| File | Teacher | Duration | Format |
|------|---------|----------|--------|
| `/Users/ahjan/Downloads/maat_audiobook_example.wav` | Maat | 24 min | Audio (WAV) |
| `/Users/ahjan/Downloads/joshin_audiobook_example.mp4` | Joshin | 72 min | Descript video (MP4) |
| `/Users/ahjan/Downloads/ahjan_audiobook_example.mp4` | Ahjan | 63 min | Descript video (MP4) |

### Demo Output

`~/Desktop/maat_audiobook_video_demo.mp4` — 30s clip rendered by our pipeline. Compare visually to the Joshin/Ahjan Descript reference videos.

---

## 7. Related Docs (Read in Order)

| Doc | What It Covers |
|-----|---------------|
| `docs/PEN_NAME_AUTHOR_SYSTEM.md` | The existing 452-author pen name system (standard brands). Architecture, voice locks, positioning profiles, topic scores. **Read this first for author expansion.** |
| `docs/VOICE_ARCHITECTURE_PLAN.md` | ElevenLabs voice layering: teacher voices, channel voices, manga voices, locale voices. |
| `docs/authoring/AUTHOR_COVER_ART_SYSTEM.md` | How cover art bases work. Author→PNG→palette tokens→KDP covers. |
| `docs/authoring/AUTHOR_ASSET_WORKBOOK.md` | Required assets per author: bio, why_this_book, authority_position, audiobook_pre_intro. |
| `docs/LOCALE_CATALOG_MARKETING_PLAN.md` | All 13 locale marketing strategies, invisible scripts, platform positioning. |
| `docs/GLOBAL_PERSONA_MARKETING_PLAN.md` | 10 personas × 12 locales × 12 topics market fit matrix. |
| `docs/PHOENIX_24_BRAND_GOVERNANCE_ARCHITECTURE.md` | Governance at scale: anti-duplication, brand separation, KPI sentinels. |
| `docs/RELEASE_VELOCITY_AND_SCHEDULE.md` | Release velocity ramp, platform caps, scheduling. |
| `artifacts/research/teacher_market_validation_matrix_2026_04_04.md` | Which teachers validated for which markets. Tiers 1-3. |
| `artifacts/research/video_format_strategy_2026_04_06.md` | Video format performance, YouTube RPM data, all 13 markets. |

---

## 8. Quick Start Commands

```bash
# Render an audiobook video (Descript style)
export PATH="/opt/homebrew/bin:$PATH"
python3 scripts/video/render_audiobook.py \
  --audio chapter.mp3 --transcript chapter.txt \
  --format long --style default --quality standard \
  -o chapter_video.mp4

# Render a short clip (9:16 for Shorts/TikTok)
python3 scripts/video/render_audiobook.py \
  --audio chapter.mp3 --format short \
  --clip-start 45 --clip-end 105 \
  -o chapter_short.mp4

# Orchestrate full book → all video variants + schedule
python3 scripts/video/orchestrate_book_to_video.py \
  --audio full_audiobook.mp3 --transcript book.txt \
  --brand stillness_press --teacher ahjan --book-id book_001 \
  -o artifacts/video/audiobook/book_001/

# Generate upload schedule (dry run)
python3 scripts/release/generate_video_schedule.py \
  --lane en --phase 1 --weeks 12 --dry-run

# Generate upload schedule (write file)
python3 scripts/release/generate_video_schedule.py \
  --lane en --phase 1 --weeks 12 \
  -o artifacts/schedules/video_schedule_en_p1.json
```

---

## 9. Dependencies

| Package | Version | Used By |
|---------|---------|---------|
| stable-ts | 2.19.1 | Whisper word-level alignment |
| pysubs2 | 1.8.1 | ASS subtitle manipulation |
| openai-whisper | 20250625 | Audio transcription |
| torch | 2.8.0 | Whisper backend |
| pyyaml | * | Config loading |
| ffmpeg | 8.1 | Video rendering (at `/opt/homebrew/bin/ffmpeg`) |

**Note:** `ffmpeg` is NOT on system PATH by default. Scripts use `/opt/homebrew/bin/ffmpeg` explicitly, but `stable-ts` calls `ffmpeg` via PATH. Either add `/opt/homebrew/bin` to PATH or symlink.

---

*End of handoff. Questions → read the files in order listed in Section 7.*

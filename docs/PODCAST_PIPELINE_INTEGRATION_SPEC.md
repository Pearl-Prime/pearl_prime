# Podcast Pipeline Integration Spec

> **Authority:** Pearl_Architect
> **Target:** Pearl_Prime (scripts), Pearl_Int (platform integration), Pearl_GitHub (CI)
> **Date:** 2026-04-09
> **Status:** Design complete. Implementation required.
>
> This document specifies exactly what needs to be built or modified to wire
> podcast production into the weekly brand admin delivery pipeline.

---

## Overview: What Exists vs What's Missing

```
COMPLETE (configs + design):
  ✅ config/podcast/podcast_format.yaml        — episode structure, music wiring
  ✅ config/podcast/brand_podcast_plans.yaml   — 13 market plans
  ✅ config/podcast/platform_distribution.yaml — RSS spec, APIs, cadence
  ✅ config/catalog/weekly_queue_config.yaml    — podcast_weekly section added
  ✅ config/brand_management/marketing_plan.yaml — podcast layer activated
  ✅ config/duration/serialization_cadence.yaml — podcast cadence already existed

MISSING (implementation needed):
  ❌ scripts/podcast/*.py                      — assembly, render, feed, upload
  ❌ server/routes/brand_admin.py              — podcast API endpoint
  ❌ config/brand_management/ updates          — credential fields, platform lanes
  ❌ brand-wizard-app/ UI                      — podcast tab in admin portal
  ❌ .github/workflows/podcast-weekly.yml      — CI trigger
  ❌ scripts/build_weekly_brand_package.py     — add podcast to package
```

---

## Gap 1: Weekly Package Builder

**File:** `scripts/build_weekly_brand_package.py`

**Current state:** Builds packages with books (.txt), metadata (.json), covers (.jpg/.png),
manifests (.csv). Does NOT include podcast MP3s or RSS metadata.

**Required change:** After book compilation, run podcast render and include outputs.

**New output structure:**

```
artifacts/weekly_packages/{brand_id}/{week}/
├── upload_manifest.csv          ← ADD podcast rows
├── books/                       ← existing
├── metadata/                    ← existing
├── podcast/                     ← NEW directory
│   ├── episodes/
│   │   ├── ep01_chapter_title.mp3
│   │   ├── ep01_chapter_title.json       # per-episode metadata
│   │   ├── ep02_chapter_title.mp3
│   │   ├── ep02_chapter_title.json
│   │   └── ...
│   ├── micro/                            # podcast_short daily drops
│   │   ├── micro_mon.mp3
│   │   ├── micro_tue.mp3
│   │   ├── micro_wed.mp3
│   │   ├── micro_thu.mp3
│   │   └── micro_fri.mp3
│   ├── sleep/                            # podcast_sleep (sleep brands only)
│   │   └── sleep_episode.mp3
│   ├── trailer.mp3                       # season trailer (week 1 only)
│   ├── feed.xml                          # RSS feed (ready to upload to R2)
│   ├── artwork.jpg                       # 3000x3000 show artwork
│   └── platform_metadata/
│       ├── spotify.json                  # Spotify-specific metadata
│       ├── apple_podcasts.json           # Apple-specific metadata
│       ├── youtube.json                  # YouTube-specific metadata
│       ├── ximalaya.json                 # zh-CN only
│       └── platform_submission_guide.md  # per-locale platform instructions
└── README.txt                   ← UPDATE to include podcast section
```

**Per-episode metadata JSON schema:**

```json
{
  "episode_id": "uuid-v4",
  "guid": "uuid-v4 (NEVER CHANGE after creation)",
  "series_id": "social_anxiety_arc",
  "series_title": "La Sala Llena de Gente",
  "episode_number": 1,
  "season_number": 1,
  "title": "La Puerta Que Casi No Abriste",
  "description": "Episode description (max 4000 bytes)",
  "duration_s": 990,
  "duration_formatted": "16:30",
  "topic": "social_anxiety",
  "persona": "millennial_women_professionals",
  "teacher": "ahjan",
  "brand_id": "stillness_press",
  "locale": "es-US",
  "format": "podcast_episode",
  "audio": {
    "file": "ep01_chapter_title.mp3",
    "size_bytes": 15840000,
    "bitrate_kbps": 128,
    "sample_rate": 44100,
    "channels": "mono",
    "loudness_lufs": -16.0,
    "true_peak_dbtp": -1.2
  },
  "music": {
    "music_group": "grounding",
    "topic_modifier": "social_anxiety",
    "brand_dna": "ch_001",
    "base_track_id": "grounding_social_anxiety_neutral_001"
  },
  "rss": {
    "enclosure_url": "https://podcast.phoenix-omega.com/stillness_press/es-US/social_anxiety_arc/ep01.mp3",
    "enclosure_type": "audio/mpeg",
    "pub_date_rfc2822": "Wed, 15 Apr 2026 09:00:00 -0500",
    "itunes_episode_type": "full",
    "itunes_explicit": false
  },
  "id3_tags": {
    "TIT2": "La Puerta Que Casi No Abriste",
    "TPE1": "Stillness Press",
    "TALB": "La Sala Llena de Gente",
    "TRCK": "1",
    "TCON": "Podcast",
    "TYER": "2026"
  },
  "platforms": ["spotify", "apple_podcasts", "amazon_music"]
}
```

**Upload manifest CSV additions:**

```csv
title,teacher,persona,topic,format,platform,locale,file_path,duration_s,guid
"La Puerta Que Casi No Abriste",ahjan,millennial_women_professionals,social_anxiety,podcast_episode,spotify,es-US,podcast/episodes/ep01_chapter_title.mp3,990,uuid-here
"La Puerta Que Casi No Abriste",ahjan,millennial_women_professionals,social_anxiety,podcast_episode,apple_podcasts,es-US,podcast/episodes/ep01_chapter_title.mp3,990,uuid-here
```

---

## Gap 2: Brand Admin API Endpoint

**File:** `server/routes/brand_admin.py`

**Add these endpoints:**

```python
# ── Podcast Endpoints ───────────────────────────────────────────────

@router.get("/api/v1/admin/podcast")
async def list_podcast_episodes(brand_id: str = Depends(get_brand_from_session)):
    """List all podcast episodes for this brand across all weeks.
    Returns: series list with episodes, each with download URL + metadata.
    Source: artifacts/weekly_packages/{brand_id}/*/podcast/episodes/*.json
    """
    pass

@router.get("/api/v1/admin/podcast/feed/{series_id}")
async def get_podcast_feed(
    brand_id: str = Depends(get_brand_from_session),
    series_id: str = Path(...)
):
    """Return the RSS feed XML for a specific series.
    Brand admin can copy this URL and submit to platforms.
    Source: R2 URL or artifacts/weekly_packages/{brand_id}/*/podcast/feed.xml
    """
    pass

@router.get("/api/v1/admin/podcast/download/{week}")
async def download_podcast_package(
    brand_id: str = Depends(get_brand_from_session),
    week: str = Path(...)
):
    """Download all podcast assets for a week as ZIP.
    Includes: MP3s, feed.xml, artwork, platform_metadata/, submission guide.
    """
    pass

@router.get("/api/v1/admin/podcast/platforms")
async def get_podcast_platform_status(
    brand_id: str = Depends(get_brand_from_session)
):
    """Return platform submission status for this brand's podcasts.
    Shows: which platforms have the RSS feed submitted, episode counts,
    last sync time, any errors.
    Source: artifacts/podcast_status/{brand_id}/platform_status.json
    """
    pass
```

---

## Gap 3: Platform Credential Fields

**File:** `config/brand_management/platform_credential_fields.yaml`

**Add these platform entries:**

```yaml
spotify_podcast:
  display_name: "Spotify for Podcasters"
  fields:
    - id: spotify_podcast_show_id
      label: "Spotify Show ID"
      type: text
      help: "Found in Spotify for Podcasters dashboard URL"
      required: false       # RSS auto-ingested; ID is for tracking
    - id: spotify_podcast_rss_submitted
      label: "RSS Feed Submitted?"
      type: boolean
      help: "Have you submitted the RSS feed at podcasters.spotify.com?"
  locales: [all]            # available in all locales

apple_podcasts:
  display_name: "Apple Podcasts Connect"
  fields:
    - id: apple_podcast_show_id
      label: "Apple Podcasts Show ID"
      type: text
      help: "Found in Apple Podcasts Connect after RSS submission"
      required: false
    - id: apple_podcast_rss_submitted
      label: "RSS Feed Submitted?"
      type: boolean
  locales: [all]

youtube_podcast:
  display_name: "YouTube Podcasts"
  fields:
    - id: youtube_podcast_playlist_id
      label: "YouTube Podcast Playlist ID"
      type: text
      help: "Created when you submit RSS in YouTube Studio"
      required: false
    - id: youtube_podcast_rss_submitted
      label: "RSS Feed Submitted?"
      type: boolean
  locales: [all]

ximalaya_podcast:
  display_name: "Ximalaya (喜马拉雅)"
  fields:
    - id: ximalaya_album_id
      label: "Ximalaya Album ID (专辑ID)"
      type: text
      help: "The album/show ID on Ximalaya for this series"
      required: true         # needed for manual upload
    - id: ximalaya_creator_verified
      label: "Creator Account Verified?"
      type: boolean
      help: "Ximalaya requires verified account for uploads"
  locales: [zh-CN]          # zh-CN only

podbbang_podcast:
  display_name: "Podbbang (팟빵)"
  fields:
    - id: podbbang_show_id
      label: "Podbbang Show ID"
      type: text
      required: false
    - id: podbbang_rss_submitted
      label: "RSS Feed Submitted?"
      type: boolean
  locales: [ko-KR]

noice_podcast:
  display_name: "Noice"
  fields:
    - id: noice_show_id
      label: "Noice Show ID"
      type: text
      required: false
    - id: noice_rss_submitted
      label: "RSS Feed Submitted?"
      type: boolean
  locales: [id-ID]
```

---

## Gap 4: Brand Admin Platform Lanes

**File:** `config/brand_management/brand_admin_users.yaml`

**Update platform_lanes to include podcast platforms:**

```yaml
platform_lanes:
  en_US:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, youtube_podcast, amazon_music_podcast]
  ja_JP:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram, line]
    add: [spotify_podcast, apple_podcasts, amazon_music_podcast]
  ko_KR:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, podbbang_podcast]
  zh_TW:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram, line]
    add: [spotify_podcast, apple_podcasts, kkbox_podcast]
  zh_HK:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts]
  zh_CN:
    existing: [ximalaya, youtube_shorts, tiktok, instagram]
    add: [ximalaya_podcast]   # same platform, different content type
  zh_SG:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts]
  es_US:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, amazon_music_podcast]
  es_ES:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, ivoox_podcast]
  fr_FR:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, deezer_podcast]
  de_DE:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts, amazon_music_podcast]
  it_IT:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts]
  hu_HU:
    existing: [google_play, youtube, youtube_shorts, tiktok, instagram]
    add: [spotify_podcast, apple_podcasts]
```

---

## Gap 5: R2 Lifecycle Rules

**File:** `config/brand_management/brand_admin_users.yaml` → `video_lifecycle` section

**Add podcast lifecycle rule:**

```yaml
podcast_lifecycle:
  storage: cloudflare_r2
  bucket: phoenix-podcast
  retention: permanent         # MP3s persist (unlike MP4 video, no weekly cleanup)
  cleanup_schedule: null       # no cleanup — podcast episodes must be permanently available
  rationale: >
    Podcast MP3s are served via RSS feed enclosure URLs. If we delete them,
    every podcast app that cached the RSS will have broken playback links.
    MP3s MUST persist as long as the show is active. Unlike video (which is
    uploaded to YouTube/TikTok and the MP4 is just a staging copy), podcast
    MP3s on R2 ARE the canonical distribution source.
  cost_estimate: >
    100 episodes × 50 MB = 5 GB. R2 free tier = 10 GB.
    At full scale (1,500 episodes/year × 50 MB) = 75 GB = ~$1.13/month.
    Zero egress cost on R2.
```

**Operator note (R2):** Do **not** attach lifecycle rules that delete `podcast/` objects. Unlike staging MP4s, podcast MP3s and `feed.xml` are canonical distribution. Removal breaks RSS enclosures and client caches.

---

## Gap 6: Brand Admin UI (React)

**File:** `brand-wizard-app/src/` — new component needed

**Add a Podcast tab to the brand admin dashboard:**

```
brand-wizard-app/src/
├── podcast/                          ← NEW directory
│   ├── PodcastDashboard.jsx          ← main podcast tab
│   ├── PodcastSeriesList.jsx         ← list of series with episode counts
│   ├── PodcastEpisodeRow.jsx         ← per-episode row with play/download
│   ├── PodcastPlatformStatus.jsx     ← RSS submission status per platform
│   ├── PodcastRSSCard.jsx            ← copy-to-clipboard RSS feed URL
│   └── PodcastDownloadPackage.jsx    ← download week's podcast ZIP
```

**PodcastDashboard layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 🎙️ Podcasts                                   [Week 14] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  RSS Feed URL:                                           │
│  ┌────────────────────────────────────────────┐ [Copy]  │
│  │ https://podcast.phoenix-omega.com/...      │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  Platform Status:                                        │
│  ┌──────────────────┬──────────┬──────────────┐         │
│  │ Spotify          │ ✅ Live   │ 12 episodes  │         │
│  │ Apple Podcasts   │ ✅ Live   │ 12 episodes  │         │
│  │ Amazon Music     │ ⏳ Review │ —            │         │
│  │ YouTube Podcasts │ ❌ Not    │ Submit RSS → │         │
│  └──────────────────┴──────────┴──────────────┘         │
│                                                          │
│  This Week's Episodes:                                   │
│  ┌──────────────────────────────────────────────┐       │
│  │ ▶ Ep 3: The Five-Minute Threshold  (18:22)  │ [⬇]  │
│  │ ▶ Micro Mon: Morning Breath Reset  (3:15)   │ [⬇]  │
│  │ ▶ Micro Tue: Body Scan Check-In    (2:45)   │ [⬇]  │
│  │ ▶ Micro Wed: Grounding Exercise    (3:30)   │ [⬇]  │
│  │ ▶ Micro Thu: Self-Compassion Pause (2:50)   │ [⬇]  │
│  │ ▶ Micro Fri: Integration Moment    (3:10)   │ [⬇]  │
│  └──────────────────────────────────────────────┘       │
│                                                          │
│  [Download All (ZIP)]    [View Platform Guide]           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key UI features:**
- RSS feed URL with one-click copy (brand admin submits this once per platform)
- Platform submission status (auto-tracked or manually marked)
- Audio player preview (inline HTML5 `<audio>` tag pointing to R2 URL)
- Per-episode download button
- Download All ZIP for the week
- Platform-specific submission guide (step-by-step per locale)

---

## Gap 7: Pipeline Scripts

**Directory:** `scripts/podcast/`

**Scripts to create:**

### 7a. `assemble_podcast_episode.py`

```python
"""
Assemble a podcast episode script from a compiled book chapter.

Input:
    compiled_book.json  — full compiled book
    chapter_index       — which chapter (0-based)
    brand_id            — for brand DNA music selection
    locale              — for TTS voice routing
    topic               — for music topic modifiers
    format              — podcast_episode | podcast_short | podcast_sleep

Output:
    episode_script.json — segment list with:
        - segment_id, source_atom, text, duration_target_s
        - music_group, music_track_id, music_level_db
        - voice_config (provider, voice_id, locale, speed, pitch)

Process:
    1. Read chapter from compiled_book
    2. Extract atoms (HOOK, SCENE, REFLECTION, STORY, EXERCISE, INTEGRATION, THREAD)
    3. Map atoms to podcast segments per config/podcast/podcast_format.yaml
    4. Calculate target durations per segment
    5. Select music tracks per segment:
       - Look up segment → music_group (from podcast_format.yaml)
       - Apply topic modifier (from exercise_music_mapping.yaml)
       - Apply brand DNA (from brand_music_dna.yaml)
       - Resolve R2 URL for the track
    6. Output episode_script.json

Dependencies:
    - config/podcast/podcast_format.yaml
    - config/music/exercise_music_mapping.yaml
    - config/music/brand_music_dna.yaml
"""
```

### 7b. `render_podcast_audio.py`

```python
"""
Render a podcast episode from script to MP3.

Input:
    episode_script.json — from assemble_podcast_episode.py

Output:
    episode.mp3 — loudness-normalized, ID3-tagged, ready for distribution

Process:
    1. For each segment with text:
       - Call ElevenLabs TTS API (eleven_multilingual_v2)
       - Save per-segment WAV
    2. For each segment with music:
       - Download music track from R2 (or local cache)
       - Loop to segment duration (crossfade looping)
       - Apply brand DNA FFmpeg transform if not pre-rendered
    3. Mix voice + music per segment:
       - FFmpeg sidechain compression for ducking
       - Music at -18dB, duck -6dB during voice, attack 200ms, release 800ms
    4. Concatenate all segments with crossfades
    5. Apply loudness normalization: -16 LUFS, true peak -1.0 dBTP
    6. Inject ID3v2.3 tags (title, artist, album, track, genre, artwork)
    7. Output final MP3

Dependencies:
    - ElevenLabs API (ELEVENLABS_API_KEY)
    - ffmpeg (system binary)
    - pyloudnorm (Python library)
    - mutagen (Python library for ID3 tags)
    - Cloudflare R2 access (music bank)
"""
```

### 7c. `generate_podcast_feed.py`

```python
"""
Generate RSS 2.0 + iTunes podcast feed XML.

Input:
    brand_id, locale, series_id
    episode_metadata/*.json — per-episode metadata

Output:
    feed.xml — valid RSS 2.0 with iTunes + Podcast 2.0 namespace

Process:
    1. Read series metadata (title, description, artwork URL)
    2. Read all episode metadata JSONs
    3. Generate XML with required tags:
       Channel: title, description, language, itunes:category, itunes:image,
               itunes:explicit, itunes:type=serial, podcast:locked=yes
       Items:  title, enclosure (url, length, type), guid, pubDate,
               itunes:duration, itunes:episode, itunes:season, itunes:episodeType
    4. Validate XML against RSS 2.0 + iTunes DTD
    5. Output feed.xml

Dependencies:
    - xml.etree.ElementTree (stdlib)
    - config/podcast/platform_distribution.yaml (for RSS spec)
"""
```

### 7d. `upload_podcast_to_r2.py`

```python
"""
Upload podcast MP3s and feed.xml to Cloudflare R2.

Input:
    episodes/*.mp3, feed.xml, artwork.jpg

Output:
    Public URLs on https://podcast.phoenix-omega.com/

Process:
    1. Connect to R2 via boto3 (S3-compatible API)
    2. Upload each MP3 to: {brand_id}/{locale}/{series_id}/{episode_id}.mp3
    3. Upload feed.xml to: {brand_id}/{locale}/{series_id}/feed.xml
    4. Upload artwork to: {brand_id}/{locale}/{series_id}/artwork.jpg
    5. Set Content-Type headers (audio/mpeg, application/rss+xml, image/jpeg)
    6. Verify uploads via HEAD request

Dependencies:
    - boto3 (S3 client)
    - R2 credentials (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT)
"""
```

### 7e. `run_podcast_pipeline.py`

```python
"""
Orchestrator: end-to-end podcast production for one brand for one week.

Usage:
    python scripts/podcast/run_podcast_pipeline.py \
        --brand stillness_press \
        --locale es-US \
        --week 2026-W16 \
        --series social_anxiety_arc \
        --chapter-range 1-1          # or "next" for next unproduced chapter

Flow:
    1. Load compiled book for brand/locale/series
    2. Determine which chapter(s) to produce this week
    3. For each chapter:
       a. assemble_podcast_episode.py → episode_script.json
       b. render_podcast_audio.py → episode.mp3
    4. If podcast_short format enabled for this locale:
       a. Extract 5 EXERCISE atoms from upcoming chapters
       b. Render 5 micro-episodes (2-5 min each)
    5. If podcast_sleep format enabled for this brand:
       a. Assemble sleep episode from SCENE + STORY atoms
       b. Render with inverse pacing curve
    6. generate_podcast_feed.py → feed.xml (updated with new episodes)
    7. upload_podcast_to_r2.py → all files to R2
    8. Copy outputs to artifacts/weekly_packages/{brand_id}/{week}/podcast/
    9. Log results to artifacts/observability/podcast_production_{date}.json
"""
```

---

## Gap 8: GitHub Actions Workflow

**File:** `.github/workflows/podcast-weekly.yml`

```yaml
name: Weekly Podcast Production
on:
  schedule:
    - cron: '0 10 * * 1'     # Monday 10 AM UTC (2h after main pipeline)
  workflow_dispatch:           # manual trigger

jobs:
  podcast-production:
    runs-on: ubuntu-latest
    timeout-minutes: 120       # podcast rendering is slower than book compilation

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install elevenlabs boto3 pyloudnorm mutagen
          sudo apt-get install -y ffmpeg

      - name: Load credentials
        run: |
          eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
          R2_ACCESS_KEY_ID: ${{ secrets.R2_ACCESS_KEY_ID }}
          R2_SECRET_ACCESS_KEY: ${{ secrets.R2_SECRET_ACCESS_KEY }}

      - name: Run podcast pipeline (all active brands)
        run: |
          python scripts/podcast/run_podcast_pipeline.py \
            --all-active \
            --week current

      - name: Upload production report
        uses: actions/upload-artifact@v4
        with:
          name: podcast-production-${{ github.run_number }}
          path: artifacts/observability/podcast_production_*.json

      - name: Notify brand admins
        run: |
          python scripts/distribution/distribute_to_brand_admins.py \
            --all --message "🎙️ This week's podcast episodes are ready in your dashboard."
```

---

## Implementation Priority Order

| Priority | Gap | Owner | Effort | Dependency |
|----------|-----|-------|--------|------------|
| **P0** | Gap 7a+7b: assemble + render scripts | Pearl_Prime | 3-5 days | ElevenLabs API, ffmpeg |
| **P0** | Gap 7c: RSS feed generator | Pearl_Prime | 1 day | None |
| **P0** | Gap 7d: R2 upload script | Pearl_Int | 1 day | R2 credentials |
| **P1** | Gap 7e: orchestrator | Pearl_Prime | 1 day | P0 scripts |
| **P1** | Gap 1: weekly package builder update | Pearl_Prime | 1 day | P0 scripts |
| **P2** | Gap 3: credential fields | Pearl_Int | 0.5 day | None |
| **P2** | Gap 4: platform lanes | Pearl_Int | 0.5 day | None |
| **P2** | Gap 5: R2 lifecycle | Pearl_Int | 0.5 day | None |
| **P2** | Gap 2: brand admin API | Pearl_Int | 1-2 days | Gap 1 |
| **P3** | Gap 6: brand admin UI | Pearl_Int | 2-3 days | Gap 2 |
| **P3** | Gap 8: GitHub Actions | Pearl_GitHub | 0.5 day | P1 scripts |

**Total estimated effort:** ~12-16 days across Pearl_Prime + Pearl_Int + Pearl_GitHub.

**Critical path:** P0 scripts → P1 orchestrator → P1 weekly package → P2 API → P3 UI

---

## Validation Checklist (Definition of Done)

- [ ] Pilot episode renders from existing atoms (es-US, anxiety, Stillness Press)
- [ ] Loudness measures -16 LUFS ±1 LU
- [ ] ID3 tags readable by Spotify, Apple Podcasts
- [ ] RSS feed validates against Apple Podcasts RSS spec
- [ ] Feed.xml + MP3s served from R2 with correct Content-Type headers
- [ ] Weekly package ZIP includes podcast/ directory with all assets
- [ ] Brand admin portal shows podcast tab with episode list
- [ ] Brand admin can copy RSS URL and submit to Spotify
- [ ] Platform submission guide shows locale-specific instructions
- [ ] zh-CN package includes Ximalaya-specific upload instructions
- [ ] GitHub Actions workflow runs Monday 10 AM UTC without errors
- [ ] Brand admin notification sent after podcast production completes

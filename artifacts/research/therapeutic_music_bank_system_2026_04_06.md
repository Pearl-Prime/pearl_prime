# Therapeutic Music Bank System
## Complete Specification for Pearl Practice + Video Pipeline Music

**Date:** 2026-04-06
**Author:** Pearl_Research
**Authority:** docs/MUSIC_BANK_PLAN.md, config/music/therapeutic_music_prompts.yaml

---

## Executive Summary

This document specifies a comprehensive therapeutic music bank that serves TWO pipelines:

1. **Pearl Practice** (guided exercises) -- 9 exercise types x 15 topics x 5 temperatures x 24 brands
2. **Video Pipeline** (YouTube/TikTok) -- 15 topics x 5 temperatures x 24 channels

The system uses a **base track + brand DNA transform** architecture to minimize generation while maximizing uniqueness. Total unique audio: ~675 base tracks, each transformed 24 ways = ~16,200 unique rendered files stored on Cloudflare R2. Cost: $0.

---

## Part 1: Exercise Type to Music Mapping

### Research Foundation

Each exercise type has distinct neurological goals that require different sonic characteristics. The music must ENHANCE the exercise without becoming a distraction -- the voice/guidance is primary; music is the ambient bed.

### 1.1 Breath Regulation

**Goal:** Entrain breathing rhythm, activate parasympathetic nervous system, reduce cortisol.

Research confirms music around 6 breaths/minute (10-second cycle) optimally triggers vagal tone increase. Music-Guided Resonance Breathing (MGRB) combines consciously slowed breathing with attentive music listening, proven to reduce anxiety in clinical settings.

| Parameter | Value |
|-----------|-------|
| BPM | 50-65 (or no pulse -- use breath-rate swell at ~6/min) |
| Texture | Slow swelling pads synced to breath cycle, predictable, no surprises |
| Instruments | Warm synth pads, soft sine layers, sub-bass breath pulse |
| AVOID | Percussion, rhythmic complexity, melodic hooks, sudden changes |
| Frequency emphasis | Low-mid (100-500 Hz body resonance), theta-alpha carrier |
| Duration | 30s loopable with seamless crossfade |
| Enhancement factor | Pad swell timing matches inhale/exhale rhythm |
| Distraction risk | Any beat that competes with breathing count; any melodic phrase that demands attention |

### 1.2 Body Awareness (Body Scan)

**Goal:** Direct attention systematically through body regions, increase interoception, promote parasympathetic dominance.

Research from a 2019 pilot study found that participants preferred nature sounds or minimal ambient textures during body scan. The music should be nearly invisible -- a warm tonal bed that fills silence without creating narrative.

| Parameter | Value |
|-----------|-------|
| BPM | None (pure drone/texture, no rhythmic pulse) |
| Texture | Ultra-smooth continuous drone, no movement, "warm blanket" feel |
| Instruments | Deep warm pad, sine-wave layers, very gentle room-tone hum |
| AVOID | Any rhythmic element, melodic phrases, chimes/bells that punctuate |
| Frequency emphasis | Low (80-300 Hz) for body resonance; theta 4-8 Hz binaural undertone |
| Duration | 30s seamless loop; must be imperceptible at loop point |
| Enhancement factor | Low-frequency warmth creates proprioceptive resonance |
| Distraction risk | Any sound event that pulls attention away from body awareness |

### 1.3 Sensory Grounding (5-4-3-2-1)

**Goal:** Redirect attention from internal anxiety to external sensory experience. The 5-4-3-2-1 technique engages all five senses systematically.

Music must provide a gentle anchor WITHOUT becoming one of the "things you hear" that competes with the exercise. It should be barely-there atmospheric texture.

| Parameter | Value |
|-----------|-------|
| BPM | 60-68 (matches resting heart rate, grounding) |
| Texture | Steady, earthy, grounded low-end, subtle organic textures |
| Instruments | Earth-tone drone, muted plucked strings, very soft nature-adjacent textures |
| AVOID | Prominent melody, bright frequencies, anything that demands "naming" |
| Frequency emphasis | Low-mid grounding (100-800 Hz), alpha 8-13 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Steady predictable sound reduces hypervigilance |
| Distraction risk | If music is noticeable enough to become "one thing you hear" it defeats the exercise |

### 1.4 Meditations

**Goal:** Sustained present-moment awareness, deepening focus, cultivating specific states (compassion, equanimity, visualization).

Meditation has the broadest music range because the topic determines the emotional quality. This is where the topic x temperature matrix matters most. Music should support a 3-20 minute sustained state.

| Parameter | Value |
|-----------|-------|
| BPM | Topic-dependent (40-80 range per therapeutic_music_prompts.yaml) |
| Texture | Continuous ambient wash, spacious, open, non-directive |
| Instruments | Warm pads, distant bells, gentle drones (varies by topic/temperature) |
| AVOID | Verse-chorus structure, lyrical content, sharp transients |
| Frequency emphasis | Full spectrum, topic-dependent (see existing 75 profiles) |
| Duration | 30s seamless loop, designed for 10+ minute extended listening |
| Enhancement factor | Spaciousness supports expanded awareness |
| Distraction risk | Melodic hooks, beat patterns that create expectations |

### 1.5 Affirmations

**Goal:** Support internalization of positive self-statements. Music adds emotional weight to affirmations, engaging the limbic system so statements land emotionally, not just intellectually.

Research shows that slow music works for grounding and self-compassion affirmations; medium tempo for confidence-building; upbeat for motivation. The music should have a warm, supportive, slightly uplifting quality.

| Parameter | Value |
|-----------|-------|
| BPM | 65-80 (gentle forward motion, supportive energy) |
| Texture | Warm, gently uplifting, golden/bright quality, subtle harmonic shimmer |
| Instruments | Warm pad, soft piano harmonics, light bells, gentle bass |
| AVOID | Dark textures, dissonance, heavy bass, anything sad/mournful |
| Frequency emphasis | Mid-high warmth (300-4000 Hz), alpha-beta 10-15 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Warmth and gentle uplift reinforce self-worth statements |
| Distraction risk | Too much energy competes with voice; too little feels hollow |

### 1.6 Reflections (Journaling/Contemplation)

**Goal:** Support introspective writing or verbal processing. The mind needs space to think while music prevents the silence from feeling oppressive.

Research shows ambient music with slow tempo and no vocals enables focus on the internal soundscape. Lo-fi beats and ambient textures block distractions while keeping the mind gently active.

| Parameter | Value |
|-----------|-------|
| BPM | 60-72 (gentle, thinking pace) |
| Texture | Spacious, open, room for thought, like a quiet room with warmth |
| Instruments | Soft ambient pad, distant muted piano, gentle vinyl/tape warmth |
| AVOID | Strong rhythms, bright leads, anything that writes a narrative |
| Frequency emphasis | Mid-range warmth (200-2000 Hz), alpha 8-12 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Gentle warmth prevents "empty room anxiety" while leaving cognitive space |
| Distraction risk | Melodic phrases that hijack the internal monologue |

### 1.7 Self-Inquiry

**Goal:** Deep contemplation of fundamental questions ("Who am I?", "What is real?"). Requires the most spacious, least directive music. Silence with warmth.

Self-inquiry practice, rooted in Advaita Vedanta, requires a calming environment where the practitioner contemplates the nature of self. Music should create an open container.

| Parameter | Value |
|-----------|-------|
| BPM | None to 55 (barely perceptible movement, if any) |
| Texture | Ultra-minimal, open, vast, sparse -- like sitting in an empty cathedral |
| Instruments | Single sustained pad, very distant reverb tail, occasional sine shimmer |
| AVOID | Any musical narrative, progression, build, or resolution |
| Frequency emphasis | Mid (300-1500 Hz resonant space), theta 4-8 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Spaciousness mirrors the open inquiry of self-investigation |
| Distraction risk | Any musical event that answers a question the mind should be asking |

### 1.8 Integration Bridges

**Goal:** Connect a somatic or emotional experience back to daily life. Transition from meditative to functional state. These are "re-entry" exercises.

Music should provide a gentle upward energy shift, like sunrise after deep rest. Slightly more present and grounded than meditation music.

| Parameter | Value |
|-----------|-------|
| BPM | 68-78 (gently activating, approaching normal resting state) |
| Texture | Warm with gentle forward motion, settling-into-clarity feel |
| Instruments | Clear warm pad, gentle rhythmic hint, bright but soft overtones |
| AVOID | Heaviness, darkness, anything that pulls back into deep states |
| Frequency emphasis | Full spectrum with slight high-mid emphasis, alpha-beta 10-15 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Gentle activation supports bridging internal experience to outer world |
| Distraction risk | Too much activation feels jarring after deep work |

### 1.9 Thought Experiments

**Goal:** Support imaginative cognitive exercises ("Imagine you are...", "What if..."). These are guided visualization/imagination exercises requiring creative mental engagement.

Research confirms music reliably induces imagination and enhances vividness of imagined journeys. Music should be dream-like and open, supporting visual imagination without dictating its content.

| Parameter | Value |
|-----------|-------|
| BPM | 55-70 (dream-pace, floating, exploratory) |
| Texture | Floating, dreamy, Lydian quality, shifting harmonic color, open narrative |
| Instruments | Floating pad, dreamy FM bell, gentle harp-like pluck, soft shimmer |
| AVOID | Grounding bass, rigid rhythm, earth-tone drones (too anchoring) |
| Frequency emphasis | Mid-high (500-6000 Hz floating quality), alpha 8-12 Hz |
| Duration | 30s seamless loop |
| Enhancement factor | Dreamy quality activates imagination centers |
| Distraction risk | Too specific a mood pre-determines the thought experiment's emotional direction |

---

## Part 2: Persona Music Affinity

### Research Foundation

Different demographics respond to music styles based on cultural context, age cohort, daily environment, and therapeutic needs. The ISO principle requires first MATCHING the listener's state before shifting it.

### 2.1 Corporate Managers

| Dimension | Profile |
|-----------|---------|
| Style affinity | Clean ambient, architectural, minimal electronic, lo-fi study |
| AVOID | "Hippie" new age, world music, overtly spiritual, didgeridoo, wind chimes |
| BPM sweet spot | 60-75 (controlled, measured, professional) |
| Instrument preferences | Clean synth pads, soft piano, muted string textures |
| Context | At desk with headphones OR in car commute. Needs to feel "sophisticated" |
| Emotional need | Permission to stop performing. Space to not be "on." |

### 2.2 Healthcare RNs

| Dimension | Profile |
|-----------|---------|
| Style affinity | Warm natural sounds, gentle acoustic, personalized choice matters most |
| AVOID | Clinical/sterile sounds, hospital beep associations, urgent rhythms |
| BPM sweet spot | 50-65 (parasympathetic recovery, deeply decompressing) |
| Instrument preferences | Nature sounds, warm pads, gentle acoustic guitar, soft piano |
| Context | Post-shift decompression, break room, car before going home. Needs deep rest. |
| Emotional need | Being held. Not having to care for anyone. Being the patient for once. |

Research: A 2022 systematic review confirmed personalized music listening reduced emotional exhaustion in nurses. Hospital decompression rooms use nature sounds and calming music as standard practice.

### 2.3 Gen Z Professionals

| Dimension | Profile |
|-----------|---------|
| Style affinity | Lo-fi study beats, GhibliCore, indie folk, ambient electronic, "sad music" |
| AVOID | Boomer meditation music, crystal bowls, Tibetan singing bowls, "spa music" |
| BPM sweet spot | 65-80 (slightly energized, study-mode adjacent) |
| Instrument preferences | Lo-fi piano, vinyl crackle, muted beats, soft synth |
| Context | Headphones at desk, in bed at night, phone speaker. Digital-first. |
| Emotional need | Validation that struggle is real. Not toxic positivity. Permission to feel sad. |

Research: Gen Z uses sad music as self-soothing. They prefer emotional authenticity over forced positivity. Lo-fi Girl aesthetics are their ambient norm.

### 2.4 First Responders

| Dimension | Profile |
|-----------|---------|
| Style affinity | Simple, predictable, grounded. Nature sounds work well. No surprises. |
| AVOID | Alarm sounds, sirens, urgent tempo, chaotic textures, sudden loud events |
| BPM sweet spot | 50-65 (deeply calming, predictable, safe) |
| Instrument preferences | Low warm drones, nature (rain, ocean), simple guitar, steady bass |
| Context | Post-call in vehicle, station break room, home decompression. Hypervigilant nervous system. |
| Emotional need | Safety. Predictability. Permission to stop being alert. |

Research: Music with simple repetitive rhythms, low pitch, slow tempos, harmony and lack of percussion/vocals helps manage PTSD and anxiety in trauma-exposed populations.

### 2.5 Entrepreneurs

| Dimension | Profile |
|-----------|---------|
| Style affinity | Forward-energy ambient, motivational undertone, tech-adjacent, clean electronic |
| AVOID | Passive/defeated tones, overly soft/gentle (feels unproductive), "giving up" energy |
| BPM sweet spot | 68-85 (action-oriented, but not manic) |
| Instrument preferences | Clean synth, confident pad, subtle pulse, bright overtones |
| Context | Late-night work, morning routine, between meetings. Needs fuel. |
| Emotional need | Reassurance they are not crazy. Energy to keep going. |

### 2.6 Working Parents

| Dimension | Profile |
|-----------|---------|
| Style affinity | Warm, nostalgic, gentle, "hug in music form", lo-fi, soft acoustic |
| AVOID | High-energy (exhausting), complex (cognitively taxing), clinical |
| BPM sweet spot | 55-70 (restful, nurturing) |
| Instrument preferences | Soft piano, warm pad, gentle guitar, music-box quality |
| Context | Kids asleep, stolen 5 minutes, in bed, bathroom break. Tiny windows. |
| Emotional need | Being taken care of. Being told they are enough. |

### 2.7 NYC Executives

| Dimension | Profile |
|-----------|---------|
| Style affinity | Sophisticated ambient, architectural minimalism, refined, understated |
| AVOID | Cheap-sounding synths, generic spa music, anything that feels "mass market" |
| BPM sweet spot | 60-72 (composed, measured, high-quality production) |
| Instrument preferences | Clean sine layers, subtle brass warmth, refined string pads |
| Context | Private office, first class, hotel room. High production value expected. |
| Emotional need | Permission to feel. Space behind the mask. |

### 2.8 Gen Alpha Students

| Dimension | Profile |
|-----------|---------|
| Style affinity | Kawaii, GhibliCore, lo-fi, gentle pop-adjacent, game soundtrack aesthetics |
| AVOID | Adult meditation voice, clinical tones, overly serious, "old" sounding |
| BPM sweet spot | 65-78 (youthful energy, but not overwhelming) |
| Instrument preferences | Chiptune-adjacent pads, music-box bells, gentle synth, soft pluck |
| Context | Phone speaker in bedroom, headphones during homework, small speaker. |
| Emotional need | Feeling understood. Not being talked down to. Gentle safety. |

### 2.9 Educators

| Dimension | Profile |
|-----------|---------|
| Style affinity | Warm acoustic, classical-adjacent, nature sounds, thoughtful ambient |
| AVOID | Chaotic textures, harsh electronic, anything resembling school bells/alarms |
| BPM sweet spot | 55-68 (reflective, decompressing, processing) |
| Instrument preferences | Acoustic guitar, warm piano, gentle strings, nature underlays |
| Context | After school, grading at night, lunch break. Needs mental space. |
| Emotional need | Being reminded why they started. Refueling purpose. |

### 2.10 Tech/Finance Burnout

| Dimension | Profile |
|-----------|---------|
| Style affinity | Lo-fi study beats, synthwave ambient, muted electronic, dark ambient |
| AVOID | Corporate motivation music, "rise and grind" energy, forced positivity |
| BPM sweet spot | 55-72 (decompression, not productivity optimization) |
| Instrument preferences | Lo-fi keys, muted synth, vinyl texture, distant bass |
| Context | At desk (always), in bed with phone, late night. Screen-adjacent. |
| Emotional need | Permission to stop optimizing. Feeling like a person, not a resource. |

### 2.11 Gen X Sandwich Generation

| Dimension | Profile |
|-----------|---------|
| Style affinity | Warm analog, nostalgic 80s/90s ambient, mature, dignified, nature sounds |
| AVOID | Trendy sounds, anything that feels like it is trying too hard, TikTok aesthetics |
| BPM sweet spot | 55-68 (restful, dignified, grounded) |
| Instrument preferences | Warm analog pads, gentle piano, acoustic textures, nature sounds |
| Context | Driving between care duties, late night after everyone is asleep. Stolen moments. |
| Emotional need | Being seen. Being told their exhaustion is valid. |

### 2.12 Millennial Women Professionals

| Dimension | Profile |
|-----------|---------|
| Style affinity | Warm indie folk-adjacent, gentle ambient, "quiet luxury" sonic, soft pop-adjacent |
| AVOID | Aggressive, clinical, overly masculine energy, preachy |
| BPM sweet spot | 60-75 (balanced, warm, empowering without being pushy) |
| Instrument preferences | Warm piano, soft strings, gentle pad, breathy textures |
| Context | Morning routine, bath, bedtime, commute. Intentional self-care moments. |
| Emotional need | Rest without guilt. Reconnecting with themselves beyond roles. |

---

## Part 3: Brand Music Fingerprint (Anti-Spam DNA)

### Problem

24 channels publish content from the same 15 topics. YouTube/TikTok audio fingerprinting (Shazam-derived spectral hash) will detect identical music across channels and flag as spam/duplicate. Each brand needs a unique sonic signature that makes the same topic's music sound like DIFFERENT tracks to fingerprinting algorithms.

### How Audio Fingerprinting Works

Platforms like YouTube Content ID and TikTok's audio matching use spectral peak extraction. They identify time-frequency peaks in the spectrogram and create a hash from peak constellations. To defeat matching, we need to shift peaks in both time AND frequency dimensions.

### Brand DNA Parameters

Each of the 24 channels gets a unique combination of these 7 parameters that are applied as FFmpeg transforms to every base track:

1. **Root key offset** (semitones): Shifts all frequencies, moving spectral peaks
2. **BPM multiplier**: Changes temporal spacing of peaks
3. **Primary instrument EQ emphasis**: Changes which frequencies dominate
4. **Reverb character**: Changes spectral envelope (room size, decay)
5. **Stereo width**: Changes spatial distribution of peaks
6. **Warmth/brightness EQ curve**: Shifts overall spectral tilt
7. **Texture overlay**: Adds unique micro-texture (vinyl, tape, rain, etc.)

### The 24 Brand DNA Assignments

See `config/music/brand_music_dna.yaml` for the full specification. Key design principles:

- **No two brands share the same key offset + BPM multiplier combination**
- **Instrument EQ emphasis varies by brand family** (calm_healing = warm low-mid; bold_dynamic = mid-high presence; abstract_symbolic = wide spectrum; hybrid_experimental = unique textures)
- **Reverb character is unique per brand** (no two brands have same room size + decay combo)
- **Texture overlay is the strongest differentiator** -- each brand gets a unique micro-texture that fundamentally changes the spectral fingerprint

### Anti-Spam Effectiveness

The combination of 7 independent parameters, each with 12-24 possible values, creates a vast combinatorial space. Even a 2-semitone pitch shift + 3% tempo change + different reverb is enough to defeat Shazam-class fingerprinting. Our system applies ALL 7 transforms simultaneously.

Additionally, per the existing MUSIC_BANK_PLAN.md, each individual VIDEO also gets its own anti-spam edit (speed, pitch, EQ, start offset) derived from the video_id hash. This means:

- **Layer 1:** Brand DNA transform (same for all content from a brand)
- **Layer 2:** Video-specific anti-spam edit (unique per video)
- **Result:** No two videos on any platform will ever have matching audio

---

## Part 4: AI Music Generation Strategy

### Generation Architecture

We use a **base track + transform** model:

1. Generate **base tracks** (topic x temperature x exercise_type_group)
2. Apply **brand DNA transforms** per channel
3. Apply **video-specific anti-spam edits** per video

### Base Track Count

Exercise types cluster into 5 music groups (types with similar sonic needs share base tracks):

| Music Group | Exercise Types | Rationale |
|-------------|---------------|-----------|
| **stillness** | body_awareness, self_inquiry | No pulse, pure drone, minimal |
| **breath** | breath_regulation | Breath-synced swells, specific cycle timing |
| **grounding** | sensory_grounding, integration_bridges | Earthy, steady, anchoring |
| **contemplative** | meditations, reflections, thought_experiments | Spacious, topic-colored ambient |
| **affirming** | affirmations | Warm, gently uplifting, supportive |

Base tracks needed:
- 5 music groups x 15 topics x 5 temperatures = **375 exercise tracks**
- 15 topics x 5 temperatures = **75 video tracks** (already specified in therapeutic_music_prompts.yaml)
- **Some overlap** between contemplative group and video tracks

**Total unique base tracks: ~400** (375 exercise + 75 video, minus ~50 overlap = 400)

### Generation Sources (Ranked)

| Source | Tracks | Quality for Ambient | Cost | Notes |
|--------|--------|-------------------|------|-------|
| **MusicGen-small (Colab)** | 300 | Good (8/10 for drones and pads) | $0 | 30s per track, ~5 min batch of 10 on T4 |
| **Pixabay Music CC0** | 50-80 | Variable (6/10, need curation) | $0 | Best for nature sounds, acoustic textures |
| **FreePD CC0** | 20-30 | Good for specific instruments (7/10) | $0 | Good piano, guitar textures |
| **MusicGen-looper** | 50+ | Best for seamless loops (9/10) | $0 | Fork optimized for loop generation |

### MusicGen Colab Batch Workflow

```
1. Open Colab notebook (free T4 GPU)
2. Install audiocraft: !pip install audiocraft
3. Load musicgen-small (300M, fits in T4 16GB VRAM)
4. Generate batch of 10 tracks per session (~5 minutes per batch)
5. Download .wav files
6. Convert to .mp3 (128kbps, adequate for ambient)
7. Apply brand DNA transforms via FFmpeg
8. Upload to R2

Estimated time for 400 tracks:
- 40 batches of 10 = ~200 minutes of GPU time
- ~15 Colab sessions (free tier limits ~90 min per session)
- Total calendar time: 2-3 days of batch processing
```

### MusicGen Quality Assessment for Therapeutic Ambient

MusicGen-small produces good results for:
- Continuous pad textures (excellent)
- Drone-based ambient (excellent)
- Slow-evolving atmospheric pieces (good)
- Simple rhythmic pulses under pads (good)

MusicGen-small struggles with:
- Complex melodic phrases (mediocre)
- Realistic acoustic instruments (fair)
- Precise BPM control (approximate)
- Seamless looping (use musicgen-looper fork)

**Verdict:** MusicGen-small is well-suited for our therapeutic ambient use case. The music types we need (drones, pads, swells, textures) are exactly what it does best.

### Riffusion as Alternative

Riffusion generates real-time high-fidelity audio from text prompts. It has a Loop Mode for seamless repetition. However, Riffusion's free tier is more limited for batch generation than Colab + MusicGen. Use Riffusion as a supplementary source for tracks where MusicGen quality is insufficient.

### ElevenLabs Sound Effects API

The existing DO NOT USE guidance in MUSIC_BANK_PLAN.md lists ElevenLabs music as expensive. However, the ElevenLabs Sound Effects API (which we already use) could generate ambient textures (rain, wind, room tone) as overlays for free/cheap. Use for texture overlays in brand DNA, not as primary music source.

---

## Part 5: Cloudflare R2 Storage + CDN

### R2 Free Tier (as of 2025-2026)

| Resource | Free Allowance | Our Estimated Usage |
|----------|---------------|-------------------|
| Storage | 10 GB-month | ~8 GB (16,200 files x ~500KB avg) |
| Class A operations | 1M/month | ~50K/month (uploads, list) |
| Class B operations | 10M/month | ~500K/month (downloads) |
| Egress bandwidth | **Unlimited free** | All streaming is free |

**Key insight:** R2 has ZERO egress fees. This is the critical advantage over S3/GCS for audio serving. All streaming bandwidth is free regardless of volume.

### Storage Architecture

```
r2://phoenix-music-bank/
  base/                                    # 400 unprocessed base tracks
    {music_group}/{topic}/{temperature}/
      base.mp3                             # 30s, 128kbps, ~500KB

  exercises/                               # Brand-transformed exercise tracks
    {exercise_type}/{topic}/{temperature}/{brand_id}/
      track.mp3                            # Brand DNA applied

  video/                                   # Brand-transformed video tracks
    {topic}/{temperature}/{brand_id}/
      track.mp3                            # Brand DNA applied

  textures/                                # Brand-specific texture overlays
    {brand_id}/
      vinyl.mp3
      tape.mp3
      rain.mp3
      room_tone.mp3

  index.json                               # Complete metadata index
```

### Storage Math

- Base tracks: 400 x 500KB = 200 MB
- Exercise tracks: 400 x 24 brands = 9,600 files x 500KB = 4.8 GB
- Video tracks: 75 x 24 brands = 1,800 files x 500KB = 900 MB
- Textures: 24 brands x 4 files x 200KB = 19 MB
- Index: ~2 MB
- **Total: ~5.9 GB** (well within 10 GB free tier)

### CDN Configuration

```yaml
# R2 bucket settings
bucket: phoenix-music-bank
public_access: true  # via custom domain or R2.dev
cache_control: "public, max-age=31536000, immutable"  # 1 year cache
content_type: "audio/mpeg"

# Custom domain (optional, via Cloudflare DNS)
domain: music.phoenix-omega.com
```

Best practices:
- Set `Cache-Control: public, max-age=31536000, immutable` (tracks never change)
- Use consistent filenames so CDN caching is maximally effective
- 128kbps MP3 is adequate for ambient background (not foreground listening)
- Consider 64kbps for mobile-first delivery (halves storage)

---

## Part 6: Complete Music Bank Specification

### Track Count Summary

| Category | Base Tracks | x Brands | Total Files | Storage |
|----------|-------------|----------|-------------|---------|
| Exercise (stillness group) | 150 | 24 | 3,600 | 1.8 GB |
| Exercise (breath group) | 75 | 24 | 1,800 | 900 MB |
| Exercise (grounding group) | 150 | 24 | 3,600 | 1.8 GB |
| Exercise (contemplative group) | Shared with video | -- | -- | -- |
| Exercise (affirming group) | 75 | 24 | 1,800 | 900 MB |
| Video | 75 | 24 | 1,800 | 900 MB |
| Texture overlays | -- | 24 | 96 | 19 MB |
| **TOTAL** | **~400** | -- | **~12,696** | **~5.4 GB** |

Note: Contemplative exercise group shares base tracks with video tracks (same topic x temperature profiles), saving ~75 base tracks.

### Generation Plan

**Phase 1: MusicGen Base Tracks (Days 1-3)**
- Generate 400 base tracks on Colab free tier
- ~15 Colab sessions, 40 batches of 10
- Use prompts from therapeutic_music_prompts.yaml (75 existing) + new exercise-specific prompts

**Phase 2: CC0 Library Curation (Day 4)**
- Download 50-80 tracks from Pixabay Music (ambient, meditation, nature)
- Download 20-30 tracks from FreePD (acoustic textures)
- Tag with mood/topic/energy metadata
- These supplement or replace MusicGen tracks where quality is insufficient

**Phase 3: Brand DNA Transforms (Day 5)**
- Apply brand_music_dna.yaml transforms via FFmpeg batch script
- 400 base tracks x 24 brands = 9,600 transformed exercise tracks
- 75 base tracks x 24 brands = 1,800 transformed video tracks
- Generate texture overlays per brand

**Phase 4: Upload to R2 (Day 6)**
- Upload ~12,700 files to Cloudflare R2
- Build index.json metadata file
- Configure CDN caching headers
- Test streaming from custom domain

**Phase 5: Pipeline Integration (Day 7)**
- Wire Pearl Practice exercise pipeline to pull from R2
- Wire video pipeline to pull from R2
- Implement brand-specific track selection
- Test end-to-end with sample exercises and videos

### Pipeline Integration: Pearl Practice

```python
def select_exercise_music(exercise_type: str, topic: str, temperature: str, brand_id: str) -> str:
    """Select music URL for a Pearl Practice exercise."""
    music_group = EXERCISE_TO_MUSIC_GROUP[exercise_type]

    # Try brand-specific transformed track first
    url = f"{R2_BASE}/exercises/{music_group}/{topic}/{temperature}/{brand_id}/track.mp3"

    # Fall back to base track if brand-specific not available
    if not exists(url):
        url = f"{R2_BASE}/base/{music_group}/{topic}/{temperature}/base.mp3"

    return url
```

### Pipeline Integration: Video

```python
def select_video_music(topic: str, temperature: str, brand_id: str, video_id: str) -> str:
    """Select and transform music for a video."""
    # 1. Get brand-transformed track
    track_url = f"{R2_BASE}/video/{topic}/{temperature}/{brand_id}/track.mp3"

    # 2. Download and apply video-specific anti-spam edit
    local_track = download(track_url)
    output = anti_spam_edit(local_track, video_id)  # from MUSIC_BANK_PLAN.md

    return output
```

### Cost Summary

| Item | Cost |
|------|------|
| MusicGen on Colab free tier | $0 |
| Pixabay Music CC0 | $0 |
| FreePD CC0 | $0 |
| FFmpeg brand DNA transforms | $0 |
| Cloudflare R2 storage (5.4 GB < 10 GB free) | $0 |
| Cloudflare R2 egress bandwidth | $0 (always free) |
| Custom domain (via existing Cloudflare account) | $0 |
| **Total** | **$0** |

### Scaling Considerations

If we exceed the 10 GB free tier:
- R2 paid storage is $0.015/GB/month = $0.08/month for 5.4 GB
- Even at 50 GB (massive expansion), cost would be $0.75/month
- Egress remains free at any scale

If we need more variety:
- Generate additional base tracks on Colab (unlimited, just time-constrained)
- Each new base track + 24 brand transforms = 24 new unique files
- Marginal cost per track: $0

---

## Research Sources

### Exercise Type Music Research
- ScienceDirect: Deep Breathing and Body Scan Meditation Combined with Music (2020)
- PubMed: Pilot study investigating preferred background sounds during mindfulness meditation (2019)
- Springer: Integrating music in breathing training and relaxation (Applied Psychophysiology)
- ScienceDirect: Music-guided resonance breathing for perioperative stress (2024)
- ScienceDirect: Expanding the Music Breathing method (2025)
- Nature Scientific Reports: Music influences vividness of imagined journeys in directed visual imagery (2021)

### Persona Affinity Research
- Activaire: The Vibe Shift -- How Gen Z and Millennials Are Reinventing Wellness Music (2025)
- YPulse: Gen Z and Millennials Listen to Music to Alter Their Mood (2022)
- PMC: The Use of Music to Manage Burnout in Nurses -- Systematic Review (2022)
- SAGE Journals: Personalized music intervention on nurse burnout (2022)
- PMC: Music Therapy for Posttraumatic Stress in Adults -- Theoretical Review
- PulseZ: What Music Means to Gen Z
- Psychology Today: Songs That Induce More Relaxation Than a Massage (Gen Z)

### Audio Fingerprinting and Brand DNA
- Wikipedia: Acoustic fingerprint
- BMAT: Audio fingerprinting -- How we identify songs
- AcoustID/Chromaprint: Open source audio identification services
- Envato Elements: What is sonic branding (2025)
- SyncBrief: Audio Branding 101 -- How a Sonic Identity Builds Listener Trust
- designerpeople.com: Sonic Branding Strategies to Create a Brand's Signature Sound

### AI Music Generation
- Meta/Facebook Research: AudioCraft / MusicGen documentation
- GitHub: ambigen -- Ambient Music Generation using MusicGen
- GitHub: camenduru/MusicGen-colab
- DEV Community: Run MusicGen-stereo on Google Colab Free-tier
- Riffusion AI: AI Music Generator documentation

### Cloudflare R2
- Cloudflare R2 Pricing documentation (developers.cloudflare.com)
- Oreate AI: Cloudflare R2 Free Tier -- What to Expect in 2025 and Beyond
- R2 Calculator: cloudflare.com

### Therapeutic Music Foundation (from prior research)
- PMC 8656869: ISO Principle -- Emotion Modulation through Music after Sadness Induction
- PMC 3011183: Music and Autonomic Nervous System
- PMC 10751054: Effect of Music on Cardiac Vagal Control
- Frontiers in Digital Health: Personalized digital therapeutics with music therapy + AI (2025)

---

*Authority: docs/MUSIC_BANK_PLAN.md, config/music/therapeutic_music_prompts.yaml, artifacts/research/therapeutic_music_matching_2026_04_04.md*

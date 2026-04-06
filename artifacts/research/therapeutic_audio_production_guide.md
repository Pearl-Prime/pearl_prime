# Therapeutic Audio Production Guide

> Deep research compiled 2026-04-06 by Pearl_Research
> Covers: therapeutic technique timing, ElevenLabs capabilities, FFmpeg post-production, pointer phrases, per-topic voice design

---

## PART 1: THERAPEUTIC AUDIO TECHNIQUES — How Professionals Do It

### 1.1 Speech Rate (Words Per Minute)

| Context | WPM | Notes |
|---------|-----|-------|
| Normal conversation | 120-160 | Baseline |
| Presentations | 130-150 | Clear, audience-friendly |
| Guided meditation | 80-110 | Research-backed optimal for retention (+40% in high-stress) |
| Body scan / yoga nidra | 60-90 | Very slow, maximizing silence |
| Somatic exercise | 70-100 | Body-focused, checking in |
| Crisis / grounding | 90-110 | Slightly faster for anchoring presence |

Key finding: Speaking at 80-90 WPM increases message retention by 40% compared to normal speech in high-stress situations. The therapeutic voice should start slightly faster (more conversational) and progressively slow down as relaxation deepens.

### 1.2 Pause Timing — Exact Seconds

| Pause Type | Duration | When Used |
|------------|----------|-----------|
| Micro-pause (breath) | 1-2s | Between phrases within a sentence |
| Standard pause | 3-5s | Between instructions (e.g., "Now bring attention to your shoulders...") |
| Body part transition | 5-8s | Moving from one body region to another in body scan |
| Processing pause | 8-15s | After emotional content; letting the listener sit with a feeling |
| Deep silence | 15-30s | Mid-meditation silence blocks; yoga nidra rotation pauses |
| Extended silence | 30-60s | Advanced meditation; post-visualization integration |

Professional meditation teachers follow the principle: the most impactful moments happen when you are NOT speaking. The secret to leading great meditation is maximizing silence time.

### 1.3 Body Scan Timing Structure

**Short body scan (6-7 minutes):**
- Per body part focus: 2-3 seconds each (scalp, back of head, sides of head, face)
- Arms and hands: 5 seconds
- Front and back of body: 3 seconds
- Feet: 5 seconds
- Contact with chair/floor: 10 seconds

**Standard body scan (20 minutes):**
- Introduction/settling: 2-3 minutes
- Per body region (head, neck, shoulders, arms, torso, hips, legs, feet): 1.5-2 minutes each
- Whole-body awareness: 2-3 minutes
- Return to room: 1-2 minutes

**Advanced body scan (45 minutes):**
- Slower pace, 3-5 seconds per individual body part
- Longer silence between regions (10-15s)
- Deeper investigation of sensations

### 1.4 Yoga Nidra Stage Structure

**8-Stage Full Practice (40-45 minutes) — Satyananda tradition:**

| Stage | Duration | Content |
|-------|----------|---------|
| 1. Settling / preparation | 3-5 min | Lying down, closing eyes, environmental awareness |
| 2. Sankalpa (resolve) | 2-3 min | Short positive statement repeated 3x mentally |
| 3. Rotation of consciousness | 10-15 min | Systematic journey through body parts |
| 4. Breath awareness | 5-7 min | Counting breath, natural observation |
| 5. Feelings & sensations | 3-5 min | Pairs of opposites (heavy/light, warm/cool) |
| 6. Visualization | 5-8 min | Guided imagery, symbolic content |
| 7. Sankalpa (repeat) | 1-2 min | Same resolve, repeated 3x |
| 8. Return to wakefulness | 2-3 min | Gradual reawakening, movement |

**4-Stage Short Practice (20 minutes):**
Eliminates Sankalpa, Feelings & Sensations, and Visualization stages.

**10-Minute Quick Practice:**
Major body parts only in rotation stage, reduced duration per stage.

### 1.5 NSDR (Non-Sleep Deep Rest) Protocol — Huberman

Available in 10, 20, and 30-minute versions. Key components:
- Long exhale breathing (exhales longer than inhales)
- Perceptual shifts: from cognitive planning mode to pure sensation
- Body-based relaxation that the nervous system matches
- NOT trying to think your way into relaxation — using body to affect mind
- NSDR boosts dopamine levels by up to 60% (Yoga Nidra study)

### 1.6 Somatic Experiencing Pacing — Peter Levine

Core principles for somatic audio guidance:
- **Titration**: Process feelings at a pace that feels safe, not overwhelming
- **Pendulation**: Oscillate between arousal state and calm state
- **Resourcing**: Always establish a "safe place" before approaching disturbance
- **Progressive**: Move from contraction/discomfort to calm/expansion gradually

Verbal approach: Start with a mildly disturbing stimulus, guide attention to body sensations, then shift to a body part that feels totally different — calm, neutral, peaceful, settled, grounded. Alternate between the two.

### 1.7 RAIN Structure — Tara Brach

Four stages, each with its own vocal quality:
1. **Recognize** (what is happening) — clear, direct, naming tone
2. **Allow** (the experience to be there) — soft, accepting, spacious
3. **Investigate** (with interest and care) — curious, gentle, warm
4. **Nurture** (with self-compassion) — tender, loving, intimate

Duration: 9-25 minutes typical. Can be standalone meditation or in-the-moment technique.

### 1.8 Therapeutic Voice Qualities — Research-Backed

From published research on therapist vocal features during psychotherapy (PMC9979575):

| Quality | Therapeutic | Anti-therapeutic |
|---------|------------|-----------------|
| Pitch | Lower, descending through session | High pitch = lower perceived empathy |
| Volume | Conversational start, progressively quieter | Loud = perceived as aggressive |
| Rate | Progressively slower (halved by mid-session) | Fast = anxious, pressured |
| Tone | Smooth, quiet, not purposely hypnotic | Harsh, strained |
| Breathiness | Slight breathiness = warmth, intimacy | Too breathy = distracting |
| Monotony | Gentle monotony aids relaxation | Too monotone = robotic / sleep-inducing |

The recommended therapeutic voice profile: smooth and quiet, perhaps even monotonous, but not purposely hypnotic. Begin conversational, progressively decrease pitch, volume, and rate. By the time the session is half to two-thirds completed, the therapist should be speaking considerably more slowly.

### 1.9 What Makes a Voice Sound Therapeutic vs Robotic

Key study finding: Respondents guided by human voices rated meditation exercises as MORE enjoyable, useful, and reported MORE relaxation than those guided by synthetic voices. The effect was more pronounced with female voices.

Critical factors:
- **Natural prosody**: Slight pitch variations within a narrow range (not flat, not dramatic)
- **Breath sounds**: Audible inhales between phrases signal humanness
- **Micro-variations**: Tiny timing inconsistencies between phrases (not metronomic)
- **Warmth**: Lower formant frequencies, slight breathiness
- **Pacing with breath**: Voice rhythm synchronized with natural breathing pattern
- **Gentle onset**: Words begin softly, not with hard attacks

---

## PART 2: ELEVENLABS FOR THERAPEUTIC AUDIO

### 2.1 Current Best Settings (Confirmed)

```python
THERAPEUTIC_VOICE_SETTINGS = {
    "voice_id": "pjcYQlDFKMbcOUp6F5GD",  # Brittney
    "stability": 0.9,           # High = consistent, calm
    "similarity_boost": 0.7,    # Moderate = natural variation
    "style": 0.05,              # Very low = no dramatic expression
    "speed": 0.75,              # 75% speed (range: 0.7-1.2)
    "model_id": "eleven_multilingual_v2"  # or eleven_v3
}
```

### 2.2 SSML Support — Complete Tag Reference

**Supported by all models EXCEPT Eleven v3:**

| Tag | Syntax | Max/Notes |
|-----|--------|-----------|
| `<break>` | `<break time="1.5s" />` | Max 3 seconds. Too many = instability |
| `<phoneme>` (IPA) | `<phoneme alphabet="ipa" ph="...">word</phoneme>` | English only. Flash v2, English v1 only |
| `<phoneme>` (CMU) | `<phoneme alphabet="cmu-arpabet" ph="...">word</phoneme>` | English only. Flash v2, English v1 only |
| `<prosody>` | `<prosody rate="slow" pitch="low">text</prosody>` | Adjusts pitch, rate, volume |
| `<emphasis>` | `<emphasis level="moderate">word</emphasis>` | Emphasizes specific words |
| Pronunciation dict | XML .pls file with `<lexeme>` + `<grapheme>` + `<alias>` | All models via API |

**Critical limitation: `<break>` max is 3 seconds.** For longer pauses, you MUST insert silence in post-production.

**NOT supported by Eleven v3.** v3 uses audio tags instead (see 2.3).

### 2.3 Eleven v3 Audio Tags — Therapeutic Subset

v3 does NOT support SSML. Instead it uses square-bracket audio tags.

**Pause and Pacing Tags:**
- `[pause]` — standard pause
- `[short pause]` — brief beat
- `[long pause]` — extended pause
- `[breathes]` — audible breath
- `[continues after a beat]` — natural beat before continuing
- `[slows down]` — reduces pace
- `[deliberate]` — careful, measured delivery

**Emotional Tags (Therapeutic):**
- `[calm]` — steady, peaceful tone
- `[softly]` — reduced volume, gentle
- `[gently]` — tender delivery
- `[sorrowful]` — grief-appropriate tone
- `[warmly]` — warm, caring tone
- `[quietly]` — low volume
- `[whispers]` — whispered delivery
- `[tenderly]` — intimate, caring
- `[reassuring]` — comforting delivery
- `[encouraging]` — supportive tone
- `[contemplative]` — thoughtful, slow
- `[resigned tone]` — accepting, gentle surrender

**Reaction Tags:**
- `[sighs]` / `[sigh of relief]` — natural exhale
- `[breathes]` — audible breath between phrases
- `[clears throat]` — natural vocal reset
- `[hesitates]` — gentle hesitation
- `[laughs softly]` — warmth/connection

**Speed and Rhythm Tags:**
- `[rushed]` — faster delivery
- `[slows down]` — slower delivery
- `[deliberate]` — measured pace
- `[rapid-fire]` — quick succession
- `[drawn out]` — elongated words
- `[stammers]` — natural hesitation

**Example therapeutic prompt for v3:**
```
[softly] [calm] Allow your eyes to gently close. [breathes] [pause]
Notice the weight of your body... [long pause]
wherever it makes contact with the surface beneath you. [pause]
[gently] There is nothing you need to do right now. [breathes]
[whispers] Nothing to fix... nothing to change. [long pause]
```

**Important usage note:** Use audio tags sparingly — 1-2 per paragraph maximum for natural results. Overuse causes artifacts.

### 2.4 Prosody Tag — Non-v3 Models

```xml
<prosody rate="slow" pitch="-10%" volume="soft">
  Allow your body to settle into stillness.
</prosody>
```

Attributes:
- `rate`: "x-slow", "slow", "medium", "fast", "x-fast", or percentage
- `pitch`: "x-low", "low", "medium", "high", "x-high", or +/- percentage/Hz
- `volume`: "silent", "x-soft", "soft", "medium", "loud", "x-loud"

### 2.5 Speed Parameter

- **Range**: 0.7 (slowest) to 1.2 (fastest)
- **Default**: 1.0
- **Therapeutic recommendation**: 0.70-0.80
- **Warning**: Extreme values (near 0.7 or 1.2) may degrade quality
- Available across TTS API, Studio, and Agents Platform

### 2.6 Pronunciation Dictionaries

Use XML-based `.pls` files to control pronunciation of specific terms:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
         alphabet="ipa" xml:lang="en-US">
  <lexeme>
    <grapheme>chakra</grapheme>
    <alias>CHAH-krah</alias>
  </lexeme>
  <lexeme>
    <grapheme>qi</grapheme>
    <alias>chee</alias>
  </lexeme>
  <lexeme>
    <grapheme>pranayama</grapheme>
    <alias>prah-nah-YAH-mah</alias>
  </lexeme>
  <lexeme>
    <grapheme>sankalpa</grapheme>
    <alias>sahn-KAHL-pah</alias>
  </lexeme>
  <lexeme>
    <grapheme>namaste</grapheme>
    <alias>nah-mah-STAY</alias>
  </lexeme>
</lexicon>
```

**Phoneme tags**: IPA and CMU supported, but ONLY for English, ONLY on Flash v2 and English v1.
**Alias tags**: Work for all languages — replace words with phonetic spellings that produce desired pronunciation.

### 2.7 Voice Design API — Custom Therapeutic Voices

**Endpoint:** `POST https://api.elevenlabs.io/v1/text-to-voice/design`

**Key Parameters:**
```json
{
  "voice_description": "A warm female voice in her 40s, speaking slowly with gentle pauses, as if guiding someone through grief. Soft, slightly breathy, with a low pitch and intimate quality. Perfect audio quality.",
  "model_id": "eleven_ttv_v3",
  "text": "Allow yourself to simply be here. There is nothing you need to do right now. Just breathe, and let whatever wants to come, come.",
  "auto_generate_text": false,
  "loudness": -0.3,
  "guidance_scale": 7,
  "should_enhance": true,
  "quality": 0.8
}
```

**Full parameter reference:**

| Parameter | Type | Range | Notes |
|-----------|------|-------|-------|
| `voice_description` | string | required | Natural language description of voice |
| `model_id` | string | — | `eleven_multilingual_ttv_v2` or `eleven_ttv_v3` |
| `text` | string | 100-1000 chars | Preview text to generate |
| `auto_generate_text` | bool | — | Auto-generates preview text if true |
| `loudness` | float | -1 to 1 | Negative = quieter (good for meditation) |
| `guidance_scale` | float | — | Higher = stricter adherence to description |
| `should_enhance` | bool | — | AI expands simple prompts for better quality |
| `quality` | float | — | Higher = better output, less variety |
| `reference_audio_base64` | string | — | Base64 audio reference (v3 only) |
| `prompt_strength` | float | 0-1 | Balance prompt vs reference (v3 only) |
| `seed` | int | — | Same seed = identical voice (reproducibility) |

**Response:** Returns 3 voice preview candidates, each with `generated_voice_id` and base64 audio. Choose one, then save via `/v1/text-to-voice` endpoint.

**Cost:** Only charged once for the preview text, even though 3 samples generated.

**v3 capabilities:** Handles nuanced cues like "middle-aged with rising intonation and a half-smile" without artifacts. Adding "perfect audio quality" to your prompt is honored by v3.

### 2.8 Best Practices for Therapeutic ElevenLabs Content

1. **Segment your script**: Generate in short chunks (1-3 sentences). Long passages degrade quality.
2. **Use punctuation for pacing**: Ellipses (...) create hesitation. Em dashes create short pauses.
3. **Avoid too many break tags**: Instability increases. Better to add silence in post-production.
4. **For v3**: Use audio tags sparingly — 1-2 per paragraph maximum for natural results.
5. **Test with real meditation text**: Voices behave differently with therapeutic language vs conversational text.
6. **Seed for consistency**: Use the same seed across segments for consistent voice character.
7. **Post-production pauses**: Since break tags max at 3s, always add longer pauses via FFmpeg silence insertion.

---

## PART 3: FFmpeg POST-PRODUCTION TECHNIQUES

### 3.1 Rubberband vs Atempo — Time Stretching

**Verdict: Rubberband is far superior for therapeutic audio.**

| Feature | atempo | rubberband |
|---------|--------|-----------|
| Quality | Artifacts, poor | Best available |
| Pitch preservation | No | Yes |
| Speed range | 0.5-2.0 (chain for more) | Any ratio |
| Requires compilation | No (built-in) | Yes (`--enable-librubberband`) |
| Use case | Quick/dirty previews | Final production |

**Rubberband usage:**
```bash
# Slow down to 80% speed, preserving pitch
ffmpeg -i input.wav -filter:a "rubberband=tempo=0.8" output.wav

# Slow down to 70% with highest quality
ffmpeg -i input.wav -filter:a "rubberband=tempo=0.7:transients=smooth:detector=compound:phase=laminar:window=long" output.wav
```

**Rubberband quality options:**
- `transients=smooth` — preserves smooth transitions (ideal for voice)
- `detector=compound` — better transient detection
- `phase=laminar` — maintains phase coherence
- `window=long` — longer analysis window for better quality at slow speeds

**Check if your FFmpeg has rubberband:**
```bash
ffmpeg -filters 2>/dev/null | grep rubberband
```

### 3.2 Room Tone / Background Ambience

**Generate pink noise (warm, natural room feel):**
```bash
# 5-minute pink noise at very low volume
ffmpeg -f lavfi -i "anoisesrc=c=pink:a=0.003:d=300" -ar 44100 room_tone.wav
```

**Noise colors for therapeutic use:**

| Color | Character | Use |
|-------|-----------|-----|
| Pink | Warm, natural, -3dB/octave | Room tone, bed under voice |
| Brown | Deep, rumbling, -6dB/octave | Deep relaxation background |
| White | Harsh, flat | NOT recommended for therapeutic |

**Mix room tone under voice:**
```bash
ffmpeg -i voice.wav -i room_tone.wav \
  -filter_complex "[1:a]volume=0.02[bg];[0:a][bg]amix=inputs=2:duration=longest" \
  output_with_room.wav
```

### 3.3 Sidechain Compression — Voice Over Music Ducking

```bash
ffmpeg -i voice.wav -i background_music.wav \
  -filter_complex \
  "[0:a]asplit=2[voice][sc]; \
   [1:a][sc]sidechaincompress=threshold=0.02:ratio=8:attack=200:release=1500:level_in=1:level_sc=1[ducked_music]; \
   [voice][ducked_music]amix=inputs=2:duration=first:weights=1 0.15" \
  -c:a aac -b:a 192k output_ducked.m4a
```

**Recommended settings for meditation ducking:**

| Parameter | Value | Why |
|-----------|-------|-----|
| threshold | 0.02 | Trigger on quiet voice (meditation is soft) |
| ratio | 6-10 | Aggressive ducking so music fully yields to voice |
| attack | 200ms | Gradual onset so ducking is not jarring |
| release | 1500-2000ms | Slow recovery — music rises back gently |
| Music volume weight | 0.10-0.20 | Music very quiet even when not ducked |

### 3.4 Binaural Beats Generation

**FFmpeg can generate binaural beats directly:**

```bash
# Theta binaural beat (6 Hz) — deep relaxation/meditation
# 200 Hz left, 206 Hz right = 6 Hz perceived beat
ffmpeg -f lavfi -i "sine=frequency=200:duration=600" \
       -f lavfi -i "sine=frequency=206:duration=600" \
       -filter_complex "[0:a][1:a]amerge=inputs=2,pan=stereo|c0=c0|c1=c1" \
       -ar 44100 theta_binaural_6hz.wav

# Alpha binaural beat (10 Hz) — relaxed awareness
ffmpeg -f lavfi -i "sine=frequency=200:duration=600" \
       -f lavfi -i "sine=frequency=210:duration=600" \
       -filter_complex "[0:a][1:a]amerge=inputs=2,pan=stereo|c0=c0|c1=c1" \
       -ar 44100 alpha_binaural_10hz.wav

# Delta binaural beat (2 Hz) — deep sleep
ffmpeg -f lavfi -i "sine=frequency=150:duration=600" \
       -f lavfi -i "sine=frequency=152:duration=600" \
       -filter_complex "[0:a][1:a]amerge=inputs=2,pan=stereo|c0=c0|c1=c1" \
       -ar 44100 delta_binaural_2hz.wav
```

**Frequency ranges:**

| Brainwave | Frequency | Effect |
|-----------|-----------|--------|
| Delta | 0.5-4 Hz | Deep sleep, healing |
| Theta | 4-8 Hz | Deep meditation, creativity, REM |
| Alpha | 8-14 Hz | Relaxed awareness, calm focus |
| Beta | 14-30 Hz | Active thinking (not for therapeutic relaxation) |

**Mix binaural beats under voice (very quiet):**
```bash
ffmpeg -i voice_with_room.wav -i theta_binaural_6hz.wav \
  -filter_complex "[1:a]volume=0.03[beats];[0:a][beats]amix=inputs=2:duration=first" \
  final_with_beats.wav
```

### 3.5 Audio Crossfade Between Segments

```bash
# Crossfade two segments with 2-second exponential transition
ffmpeg -i segment1.wav -i segment2.wav \
  -filter_complex "acrossfade=duration=2:curve1=exp:curve2=exp" \
  output_crossfaded.wav

# Chain multiple segments with crossfades
ffmpeg -i seg1.wav -i seg2.wav -i seg3.wav \
  -filter_complex \
  "[0:a][1:a]acrossfade=d=2:c1=tri:c2=tri[a12]; \
   [a12][2:a]acrossfade=d=2:c1=tri:c2=tri" \
  output_3_segments.wav
```

**Recommended curve types for therapeutic transitions:**
- `exp` (exponential) — gentle, natural-feeling fade
- `tri` (triangular) — linear, predictable crossfade
- `log` (logarithmic) — slow start, quick end

### 3.6 Reverb Settings — Intimate Meditation Room (Not a Cave)

**Using aecho for subtle room feel:**
```bash
# Intimate room reverb — short delays, moderate decay
ffmpeg -i input.wav -af "aecho=0.8:0.88:40:0.3" intimate_room.wav

# Parameters: in_gain:out_gain:delays(ms):decays(0-1)
# 40ms delay = small room (~4.5m wall distance)
# 0.3 decay = absorptive room (carpeted, curtains)
```

**Better approach — using convolution reverb with impulse response:**
```bash
# If you have an impulse response file of a real room:
ffmpeg -i voice.wav -i room_ir.wav \
  -filter_complex "[0:a][1:a]afir=dry=10:wet=2" \
  voice_with_room_reverb.wav
```

**Recommended aecho settings by room type:**

| Setting | Delays (ms) | Decays | Character |
|---------|-------------|--------|-----------|
| Intimate studio | 20:30 | 0.2:0.15 | Tight, close, warm |
| Small meditation room | 40:60 | 0.3:0.2 | Gentle space, not echoey |
| Warm living room | 50:80:120 | 0.35:0.25:0.15 | Natural, slightly spacious |
| Cave (AVOID) | 200:400:600 | 0.6:0.5:0.4 | Too reverberant, distracting |

**Key principle**: For meditation, shorter delays (20-60ms) and lower decay values (0.15-0.35) create intimacy without distraction. Longer delays sound cavernous and pull attention away from the voice.

### 3.7 EQ Warmth Boost

```bash
# Boost low-mids for warmth, gentle high-end rolloff
ffmpeg -i input.wav -af \
  "equalizer=f=200:t=q:w=1.5:g=3, \
   equalizer=f=2500:t=q:w=2:g=-2, \
   equalizer=f=8000:t=q:w=1:g=-4" \
  warm_voice.wav
```

| Band | Frequency | Gain | Purpose |
|------|-----------|------|---------|
| Warmth | 200 Hz | +3 dB | Body and warmth |
| Presence cut | 2.5 kHz | -2 dB | Remove harshness |
| Air rolloff | 8 kHz | -4 dB | Less sibilance, softer |

### 3.8 Dynamic Range Compression for Consistent Volume

```bash
# Gentle compression for therapeutic voice
ffmpeg -i input.wav -af \
  "compand=attacks=0.3:decays=0.8:points=-80/-80|-45/-30|-27/-20|-10/-10|0/-5:gain=3" \
  compressed_voice.wav
```

Alternatively, use loudnorm for EBU R128 normalization:
```bash
ffmpeg -i input.wav -af "loudnorm=I=-18:TP=-2:LRA=7" normalized.wav
```

Target loudness for meditation: **-18 to -16 LUFS** (quieter than music/podcast standards of -14 LUFS).

### 3.9 Adding Breath Sounds Between Phrases

Three approaches:
1. **Record actual breaths** and splice them in at silence points
2. **Use ElevenLabs v3 `[breathes]` tag** to generate natural breath sounds inline
3. **Generate synthetic breath** with filtered noise:

```bash
# Synthetic breath-like sound (filtered pink noise with envelope)
ffmpeg -f lavfi -i "anoisesrc=c=pink:d=1.5" \
  -af "afade=t=in:d=0.3,afade=t=out:st=0.8:d=0.7,bandpass=f=500:w=300,volume=0.15" \
  breath_sound.wav
```

### 3.10 Silence Insertion Between Segments

Since ElevenLabs break tags max at 3 seconds, use FFmpeg to insert longer silences:

```bash
# Generate 10 seconds of silence
ffmpeg -f lavfi -i "anullsrc=r=44100:cl=stereo" -t 10 silence_10s.wav

# Concatenate: speech -> silence -> speech
ffmpeg -i phrase1.wav -i silence_10s.wav -i phrase2.wav \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1" \
  output_with_pauses.wav
```

### 3.11 Complete Post-Production Pipeline

```bash
#!/bin/bash
# Full therapeutic audio post-production pipeline

INPUT="raw_voice.wav"
OUTPUT="final_therapeutic.wav"

ffmpeg -i "$INPUT" \
  -filter_complex " \
    [0:a] rubberband=tempo=0.85 [slowed]; \
    [slowed] equalizer=f=200:t=q:w=1.5:g=3, \
             equalizer=f=2500:t=q:w=2:g=-2, \
             equalizer=f=8000:t=q:w=1:g=-4 [eq]; \
    [eq] compand=attacks=0.3:decays=0.8: \
         points=-80/-80|-45/-30|-27/-20|-10/-10|0/-5:gain=3 [comp]; \
    [comp] aecho=0.8:0.88:40:0.25 [reverb]; \
    anoisesrc=c=pink:a=0.003:d=600 [room]; \
    sine=frequency=200:duration=600 [left_beat]; \
    sine=frequency=206:duration=600 [right_beat]; \
    [left_beat][right_beat] amerge=inputs=2, \
         pan=stereo|c0=c0|c1=c1,volume=0.025 [beats]; \
    [reverb][room]amix=inputs=2:duration=first [with_room]; \
    [with_room][beats]amix=inputs=2:duration=first [final]; \
    [final] loudnorm=I=-17:TP=-2:LRA=7 \
  " "$OUTPUT"
```

---

## PART 4: POINTER PHRASES CATALOG (93 Phrases)

### 4.1 Transition Phrases (Moving Between Body Parts)

1. "And now, gently shifting your attention..."
2. "Allowing your awareness to slowly drift down to..."
3. "When you're ready, bring your attention to..."
4. "And now, moving to..."
5. "Letting your awareness travel to..."
6. "Softly releasing [previous area] and turning your attention to..."
7. "As [previous area] settles, notice..."
8. "Now, with the same gentle curiosity, explore..."
9. "And in your own time, let your awareness find..."
10. "Gradually, your attention moves to..."

### 4.2 Deepening Phrases (Going Deeper into Relaxation)

11. "Allow yourself to sink a little deeper..."
12. "With each exhale, letting go just a little more..."
13. "Relaxation spreading like warm water through your body..."
14. "Drifting deeper into stillness..."
15. "Each breath carrying you further into ease..."
16. "Letting the ground hold all of your weight..."
17. "There's nothing you need to hold onto right now..."
18. "Surrendering completely into this moment..."
19. "Allowing yourself to be fully supported..."
20. "Melting into the surface beneath you..."
21. "Sinking deeper... and deeper... into rest."
22. "Let gravity do all the work."

### 4.3 Grounding Phrases (When Content Gets Heavy)

23. "Feel the solid ground beneath you..."
24. "You are here. You are safe. You are held."
25. "Notice the places where your body touches the surface..."
26. "Feel the weight of your body... real and present..."
27. "If at any time this feels like too much, simply open your eyes..."
28. "You can always come back to the breath..."
29. "Right here. Right now. This moment only."
30. "Your feet on the floor. The air in your lungs. You are here."
31. "There is ground beneath you. You are supported."
32. "Notice five things you can feel touching your skin..."
33. "You are in control of this experience. Always."
34. "If you need to, place a hand on your heart. Feel it beating."

### 4.4 Processing Phrases (After Emotional Content)

35. "Just let that be there. No need to change it."
36. "Whatever you're feeling right now is allowed."
37. "There's no right or wrong way to feel."
38. "Give yourself permission to feel exactly what you feel."
39. "You don't need to understand it. Just notice it."
40. "Let the sensation have its space..."
41. "Whatever arises, meet it with kindness."
42. "This feeling is temporary. Like a wave, it will pass."
43. "You are not your thoughts. You are the one observing them."
44. "Just breathing with whatever is here..."
45. "Allow this to move through you at its own pace..."
46. "Some things don't need to be fixed. Just witnessed."

### 4.5 Completion Phrases (Ending a Section)

47. "And now, gently letting that go..."
48. "Allowing that to dissolve with your next exhale..."
49. "Softly releasing... and returning to the breath..."
50. "And when you're ready, we'll move on..."
51. "Take one more breath here... and then let it go."
52. "Resting in the wholeness of this moment..."
53. "Carrying whatever serves you... releasing the rest..."
54. "And that's enough. That's always enough."

### 4.6 Topic-Specific: Anxiety

55. "Your nervous system is doing its job. You can help it settle."
56. "Notice where the anxiety lives in your body..."
57. "It's safe to let your guard down here..."
58. "The alarm is loud, but the danger has passed."
59. "You don't have to believe every thought right now."
60. "Anxiety is energy. Let's redirect it gently."

### 4.7 Topic-Specific: Grief

61. "Grief is love with nowhere to go. Let it have this space."
62. "You don't have to be strong right now."
63. "There is no timeline for this. Take all the time you need."
64. "Some losses reshape us. That's not weakness. That's being human."
65. "Let the missing be here. Don't push it away."

### 4.8 Topic-Specific: Somatic / Body-Focused

66. "What does your body want to tell you right now?"
67. "Notice without labeling. Just sensation."
68. "Where do you feel that in your body?"
69. "Invite that area to soften... just by 1%."
70. "Your body holds wisdom your mind hasn't caught up to yet."
71. "Can you breathe into that space?"

### 4.9 Topic-Specific: Mindset / Success

72. "You've done hard things before. You can do this."
73. "See yourself already there. Feel what that feels like."
74. "Every step counts. Even this quiet one."
75. "Clarity comes from stillness. Let it find you."
76. "You are becoming who you need to be."

### 4.10 Topic-Specific: Depression / Low Energy

77. "You showed up today. That matters."
78. "We're not going anywhere fast. Just here."
79. "Even the smallest movement forward is still forward."
80. "You don't need to feel different right now. Just present."
81. "There is gentleness waiting for you, if you'll let it in."
82. "Sometimes the bravest thing is simply staying."

### 4.11 Opening / Settling Phrases

83. "Find a comfortable position... and allow your eyes to close."
84. "Take a moment to arrive. Let the outside world wait."
85. "Begin by simply noticing that you are breathing."
86. "There's nowhere else you need to be right now."
87. "Let this be a gift you give yourself."

### 4.12 Closing / Return Phrases

88. "When you're ready, begin to deepen your breath..."
89. "Gently wiggle your fingers and toes..."
90. "Slowly allow the sounds of the room to return..."
91. "There's no rush. Come back at your own pace."
92. "Carry this stillness with you as you open your eyes..."
93. "And in your own time... welcome back."

---

## PART 5: CUSTOM VOICE DESIGN PER TOPIC

### 5.1 Voice Settings by Topic

| Topic | Speed | Stability | Similarity | Style | Pitch Direction | Special |
|-------|-------|-----------|-----------|-------|----------------|---------|
| **Grief** | 0.70 | 0.92 | 0.65 | 0.02 | Lower | More breathiness, longer pauses, warmth |
| **Anxiety** | 0.75 | 0.90 | 0.70 | 0.05 | Mid-low | Steady, grounding, reassuring |
| **Mindset/Success** | 0.80 | 0.85 | 0.75 | 0.10 | Mid | Slightly more energy, encouraging |
| **Somatic** | 0.70 | 0.93 | 0.60 | 0.01 | Low | Near-whisper, very slow, body-focused |
| **Depression** | 0.72 | 0.90 | 0.65 | 0.03 | Low-mid | Gentle, no pressure, lots of space |
| **Sleep** | 0.70 | 0.95 | 0.60 | 0.00 | Very low | Monotone-leaning, minimal variation |
| **Focus/Productivity** | 0.82 | 0.85 | 0.75 | 0.08 | Mid | Clear, present, slightly upbeat |

### 5.2 Voice Design Prompts by Topic

**Grief voice:**
```
A warm, compassionate female voice in her late 40s. Speaking very slowly with
long pauses between phrases. Slightly breathy, as if sitting beside someone in
gentle silence. Low pitch, intimate, like a trusted friend. Perfect audio quality.
No urgency whatsoever. The kind of voice that says 'I'm not going anywhere.'
```

**Anxiety voice:**
```
A steady, calm female voice in her mid-30s. Reassuring but not condescending.
Grounding and present, like an anchor in a storm. Medium-low pitch, clear
enunciation, measured pace. Not too slow - purposeful and guiding. Perfect audio
quality. The kind of voice that makes you believe everything will be okay.
```

**Mindset/Success voice:**
```
A warm, encouraging female voice in her early 40s. Confident but gentle.
Slightly upbeat energy without being hyper or motivational-speaker-like.
Mid-range pitch with subtle warmth. Speaks clearly with natural pauses.
Perfect audio quality. Sounds like a wise mentor who genuinely believes in you.
```

**Somatic voice:**
```
A very soft, slow female voice in her 40s. Almost whispered, deeply intimate.
Speaking as if guiding someone through delicate body sensations. Very low pitch,
breathy quality, minimal vocal variation. Perfect audio quality. The voice itself
feels like a gentle touch.
```

**Depression voice:**
```
A gentle, patient female voice in her late 30s. No pressure, no
forced cheerfulness. Warm and accepting, with generous space between sentences.
Low-mid pitch, soft volume, the vocal equivalent of a warm blanket. Perfect
audio quality. Never rushes, never judges.
```

**Sleep voice:**
```
A very quiet, almost monotone female voice in her 40s. Minimal pitch variation,
extremely slow, as if the voice itself is already half asleep. Very low energy,
deeply soothing, no engagement needed. Perfect audio quality. Like a lullaby
without melody.
```

### 5.3 Acoustic Property Differences by Topic

| Property | Grief | Anxiety | Mindset | Somatic | Depression |
|----------|-------|---------|---------|---------|------------|
| **Pause frequency** | Very high | Moderate | Moderate | Very high | High |
| **Pause duration** | 5-15s | 3-8s | 3-5s | 8-20s | 5-12s |
| **Breath sounds** | Audible | Minimal | Minimal | Very audible | Gentle |
| **Pitch range** | Narrow, low | Narrow, mid | Moderate, mid | Very narrow, low | Narrow, low-mid |
| **Volume** | Soft | Medium-soft | Medium | Very soft | Soft |
| **Reverb amount** | More (spacious) | Less (grounding) | Less (clear) | More (intimate) | Moderate |
| **Music bed** | Minor key, slow | Steady drone | Uplifting ambient | None or very quiet | Warm, minimal |
| **Binaural** | Theta (6 Hz) | Alpha (10 Hz) | Alpha-Beta (12 Hz) | Theta (5 Hz) | Theta-Alpha (7 Hz) |

### 5.4 How Professional Apps Vary Voice by Topic

**Headspace:**
- Uses Andy Puddicombe's voice for most meditations — single consistent voice
- Tailors pacing and script language per topic (anxiety, sleep, focus)
- Sleep stories use diverse narrators including celebrity voices
- Specialized courses by topic with different pacing structures

**Calm:**
- Multiple narrators for sleep stories (celebrities and voice actors)
- Tamara Levitt for core meditation content
- Sleep stories use notably different voice qualities (deeper, slower, more monotone)
- Daily Calm uses consistent voice but varies topic and tone

**Insight Timer:**
- Thousands of different teachers with naturally different voices
- Users can filter by voice quality preference
- Topic-specific teachers have self-selected for appropriate vocal qualities

**Key pattern**: Major apps primarily vary **script content, pacing, and music** rather than fundamentally changing the voice per topic. The voice stays consistent (trust/familiarity), while everything around it changes. Our approach of creating topic-specific voice variants is more sophisticated than industry standard.

### 5.5 Chinese/Japanese/Multilingual Voice Settings

**Available voices:**

| Voice | ID | Language | Character |
|-------|-----|----------|-----------|
| Yuki | o9LUwv6JgbYpDvUZ1W1f | Japanese | Standard |
| Miyu | EnLxjGl88dNO1Jv9AZk2 | JP/EN Multilingual | Natural bilingual |
| Liu Ping | pTOe8BQRdydOEIgv0wFL | Chinese | Calm and Clear |
| LeeTingTing | gU2KtIu9OZWy3KqiqNj6 | Taiwan Mandarin | Regional |
| James | 4VZIsMPtgggwNg7OXbPY | Chinese | Calm |

**Cultural voice considerations:**

**Chinese therapeutic audio:**
- Chinese speakers use MORE restrained emotional variation than English speakers
- Mandarin uses pitch for TONAL meaning — pitch modulation must respect tone contours
- Speech rate variation is a MORE important emotional cue in Mandarin than pitch range
- F0 (fundamental frequency) is naturally higher in Mandarin/Cantonese vs English
- Traditional Chinese medicine associates specific sounds with organ healing
- Recommended: Keep stability HIGHER (0.92-0.95) to avoid disrupting tonal accuracy
- Speed: 0.72-0.78 (slightly less slow than English to maintain tonal clarity)
- Lower similarity_boost (0.55-0.65) to allow natural Chinese prosody

**Japanese therapeutic audio:**
- Japanese uses pitch accent — stability must be high to preserve word meaning
- Japanese meditation tradition values silence even more than Western practice
- Cultural preference for restraint — less breathy, more controlled
- Honorific language forms (keigo) may be appropriate for respectful therapeutic context
- Recommended: stability=0.93, similarity=0.65, style=0.02, speed=0.73
- Longer pauses between phrases (Japanese allows more silence naturally)

**General multilingual recommendations:**
- Use `eleven_multilingual_v2` model for non-English content (most lifelike across 29 languages)
- Use alias-based pronunciation dictionaries (phoneme tags are English-only)
- Test with native speakers — accent authenticity matters for trust
- Adjust pause durations culturally (Japanese: longer; Chinese: moderate; English: moderate)
- Music beds should be culturally appropriate (shakuhachi for Japanese, guzheng for Chinese)

### 5.6 Voice Design API Prompts for Multilingual

**Chinese meditation voice:**
```
A serene Chinese female voice in her 40s. Calm and clear like still water.
Speaking Mandarin Chinese with gentle authority and warmth. Natural pacing
with mindful pauses. Perfect audio quality. A voice that embodies inner peace.
```

**Japanese meditation voice:**
```
A gentle Japanese female voice in her 30s. Soft-spoken with natural Japanese
politeness and restraint. Unhurried, with profound stillness between phrases.
Speaking Japanese with quiet dignity. Perfect audio quality. The voice of
a temple garden.
```

**Multilingual settings comparison:**

| Parameter | English | Chinese | Japanese |
|-----------|---------|---------|----------|
| speed | 0.70-0.80 | 0.72-0.78 | 0.70-0.75 |
| stability | 0.88-0.92 | 0.92-0.95 | 0.92-0.95 |
| similarity_boost | 0.65-0.75 | 0.55-0.65 | 0.60-0.70 |
| style | 0.02-0.10 | 0.01-0.05 | 0.01-0.03 |
| model | multilingual_v2 or v3 | multilingual_v2 | multilingual_v2 |

---

## APPENDIX A: COMPLETE FFmpeg FILTER REFERENCE

### Filters Used in Therapeutic Audio Production

| Filter | Purpose | Key Parameters |
|--------|---------|---------------|
| `rubberband` | Time stretching (high quality) | `tempo=0.8`, `transients=smooth` |
| `atempo` | Quick time stretch (low quality) | `0.5-2.0` (chain for more) |
| `equalizer` | EQ bands | `f=freq:t=q:w=width:g=gain_dB` |
| `aecho` | Room reverb | `in_gain:out_gain:delays_ms:decays` |
| `afir` | Convolution reverb (needs IR file) | `dry=level:wet=level` |
| `compand` | Dynamic compression | `attacks:decays:points:gain` |
| `loudnorm` | EBU R128 normalize | `I=-18:TP=-2:LRA=7` |
| `acrossfade` | Segment transitions | `duration=2:curve1=exp:curve2=exp` |
| `amix` | Mix multiple sources | `inputs=N:duration=longest:weights` |
| `sidechaincompress` | Music ducking | `threshold:ratio:attack:release` |
| `anoisesrc` | Generate noise | `c=pink:a=amplitude:d=duration` |
| `sine` | Generate tone | `frequency=Hz:duration=seconds` |
| `volume` | Adjust volume | `0.0-N` or `dB` |
| `afade` | Fade in/out | `t=in:d=seconds` or `t=out:st=start:d=seconds` |
| `bandpass` | Band filter | `f=center_freq:w=bandwidth` |
| `amerge` | Merge channels | `inputs=2` (for stereo binaural) |
| `pan` | Channel mapping | `stereo\|c0=c0\|c1=c1` |
| `anullsrc` | Generate silence | `r=44100:cl=stereo` |
| `concat` | Join segments | `n=count:v=0:a=1` |

---

## APPENDIX B: QUICK REFERENCE — SESSION STRUCTURE

### Standard 15-Minute Therapeutic Audio Structure

```
0:00-0:30   Opening bell / tone (optional)
0:30-1:30   Settling: breathing, arriving (3-5 phrases, 5s pauses)
1:30-2:30   Intention/framing (2-3 phrases, 3s pauses)
2:30-4:00   Breath awareness (4-5 phrases, 8-10s pauses)
4:00-9:00   Main content (body scan / somatic / topic-specific)
            - 8-12 phrases per body region
            - 5-10s pauses between phrases
            - 15-20s silence blocks between regions
9:00-11:00  Processing/integration (3-4 phrases, 10-15s pauses)
11:00-13:00 Deepening/wholeness (3-4 phrases, 8-12s pauses)
13:00-14:00 Return to awareness (4-5 phrases, 3-5s pauses)
14:00-14:30 Closing: eyes open, movement
14:30-15:00 Closing bell / tone (optional)
```

**Speech-to-silence ratio target: 30-40% speech, 60-70% silence.**

---

## APPENDIX C: IMPLEMENTATION CHECKLIST

- [ ] Set up ElevenLabs Brittney voice with therapeutic settings
- [ ] Test Voice Design API to create topic-specific custom voices
- [ ] Build FFmpeg post-production pipeline script
- [ ] Generate binaural beat library (delta, theta, alpha)
- [ ] Generate room tone library (pink, brown)
- [ ] Create pronunciation dictionary for therapeutic terms
- [ ] Build phrase template library from Part 4 catalog
- [ ] Test v3 audio tags for natural pause insertion
- [ ] Create per-topic voice settings profiles
- [ ] Test Chinese/Japanese voices with native speaker review
- [ ] Establish loudness targets (-17 to -16 LUFS)
- [ ] Build crossfade pipeline for multi-segment assembly
- [ ] Build silence-insertion pipeline for long pauses (>3s)
- [ ] Test rubberband availability in local FFmpeg build

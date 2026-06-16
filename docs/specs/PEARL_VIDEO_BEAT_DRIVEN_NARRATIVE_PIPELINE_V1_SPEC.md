# Pearl Prime — Beat-Driven Narrative Video Pipeline v1 Spec

**Purpose:** Define the pattern for producing spiritual narrative videos where every visual is matched to a specific narrative moment in the script and timed to actual narrator delivery (not WPM estimates). Extends `docs/VIDEO_PIPELINE_SPEC.md` with two layers it does not provide:

1. **Tier-1 LLM beat-prompt synthesis** (the per-beat prompt gap noted in the codebase audit)
2. **WhisperX-style word-level audio alignment** (the forced-alignment gap noted in `docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md`)

**First implementation:** `ahjan_update` v3.1 (June 2026). See `scripts/video/v3_1_beats.py` + `scripts/video/build_v3_1_yt_starseed.py` for the reference build.

---

## Why this pattern exists

The existing 11-stage pipeline (Script Prep → Shot Planner → Asset Resolver → Timeline Builder → Renderer) assumes prompts are either pre-built in an image bank or selected from a config-driven prompt template. For **named-entity-rich spiritual narrative** (the ahjan_update script names Sanat Kumara, the 21 Pearls of the Dragon's Garland, Master Fun, Master Wu, Joshin Sensei, Omote Sensei, Master Sha, Sai Maa, Miki, Junko, Pope Francis, Kevin Costner, the Temple of Lao Tzu, Mount Kurama, Mount Shasta, etc.), per-beat prompt selection by template lookup fails — there is no entry for "Master Fun listening to Ahjan's story across a tea table." 

The beat-driven pattern fills this gap: a Tier-1 Claude Code session (operator-present) authors a specific prompt for every beat, then a deterministic Python builder renders, times, and assembles. No paid LLM calls (per CLAUDE.md tier policy); Tier-1 work is done in this session and persists as `scripts/video/<video>_beats.py`.

---

## Stage map (extends VIDEO_PIPELINE_SPEC)

| # | Stage | Output | Tool / Spec authority |
|---|---|---|---|
| 0 | **Source script** | `docs/<video>.txt` (Markdown / plain) | Operator |
| 0a | **Narration recording** | `<video>.wav` (PCM 16-bit, 44.1kHz, mono) | Operator (or TTS via ElevenLabs) |
| 1 | **Word-level forced alignment** | `whisper_alignment.json` (per-word start/end seconds) | `scripts/video/whisper_word_align.py` (vanilla openai-whisper, `word_timestamps=True`, `base` model) |
| 2 | **Beat parsing (Tier-1)** | `scripts/video/<video>_beats.py` (BEATS list of dicts) | Tier-1 Claude Code session, operator-present |
| 3 | **Beat → audio range snap** | timed_beats with per-beat start_s/end_s | `build_<video>.py` `snap_beats_to_whisper()` |
| 4 | **Per-beat render decision** | each beat tagged `render_new` or `reuse_existing` | Tier-1 manifest in `<video>_beats.py` |
| 5 | **flux-schnell render of new beats** | `frames/frame_<3NNN>.png` | Pearl Star ComfyUI via `flux_client.call_comfyui()` |
| 6 | **Concat manifest assembly** | `frames_concat_<video>.txt` with per-beat duration | `build_<video>.py` `write_manifest()` |
| 7 | **Silent video assemble** | `<video>_silent.mp4` | ffmpeg concat-demuxer + libx264 |
| 8 | **Final mix** | `<video>.mp4` | ffmpeg merge silent + WAV with `-shortest` |
| 9 | **Pre-merge QA strip** | thumbnail grid of new render_new beats | ffmpeg xstack |
| 10 | **Operator review** | open MP4 + thumbnail grid; flag mismatches | Operator |

---

## Beat schema (the contract Tier-1 fills)

Each entry in `BEATS` is:

```python
{
    "id": "B5_21_pearls_revealed",          # snake_case slug, block + sequence
    "text": "Inside each one: thousands of dimensions of enlightenment. The Pearls of the Dragon's Garland — constructed artifacts of awakening...",
    "decision": "render_new" | "reuse_existing",
    # if reuse_existing:
    "frame": 11,                             # PNG index in artifacts/.../frames/
    # if render_new:
    "prompt": "twenty-one luminous orbs of golden-violet light arranged as a sacred garland against deep cosmic indigo, an immense ethereal dragon coiled protectively around the orbs, ...",
}
```

The builder appends `STYLE_LOCK_SUFFIX` + applies `NEGATIVE_BASE` at render time. The Tier-1 author writes only the scene-specific portion.

### Tier-1 beat-prompt authoring rules

1. **Match the specific narrative moment** — if the script names a master, location, or event, the prompt must reference that specifically (Temple of Lao Tzu at sunset; Master Wu carrying a luopan; the gold pearl above an altar). Do not fall back to generic "ancient temple" / "robed master" when specificity is available in the script.
2. **Likeness guardrails** — for any named real living person (Pope Francis, Kevin Costner, named living masters), use only architectural / symbolic silhouettes. NEVER a recognizable face. Add the specific guardrail to the prompt body (e.g., "no recognizable likeness of Pope Francis, only Vatican dome silhouette").
3. **Sacred lineage iconography** — for spiritual masters, reference the lineage's specific iconographic objects:
   - **Shingon** → vajra, bell, mudra, mandala
   - **Shinto** → torii, sakaki branch, mirror, white ceremonial robes
   - **Taoist** → bagua, gourd, luopan, calligraphy, ink-wash
   - **Vedic** → kalasha, rudraksha beads, puja fire, conch
   - **Buddhist** → lotus, dharma wheel, sutra scroll
4. **Composition lock** — golden ratio bias, centered or rule-of-thirds, never busy or chaotic. One subject focus.
5. **Anti-washout (from VIDEO_IMAGE_MASTER_PROMPT_SPEC)** — NEVER use in positive prompts: `haze, ethereal, translucent, foggy, misty, volumetric haze, soft global blur`. Always include a `dark anchor element` for grounding. Always specify `solid surfaces` and `clean edges`.
6. **Palette lock** — indigo, violet, gold, rose-gold (warm spiritual). No neon, no cool-blue-only, no green-heavy.
7. **No anatomical interiors** — never describe "chest cavity opened" / "into the heart" — these have failure-moded as gore in flux-schnell. Use abstract silhouettes with halos, mandalas surrounding the body, sacred geometry around but not inside.
8. **Visual continuity across beats** — when a single named entity recurs across multiple beats (e.g., the figure of Ahjan, Master Fun returning), use consistent descriptive language to bias the model toward consistency (same robe color, same posture register).

### Style lock applied to every render

```
, starseed cinematic spiritual painterly photorealism, 8k, soft warm light,
indigo violet gold rose-gold palette, sacred geometry undertone,
solid surfaces, clean edges, dark anchor element for grounded composition,
transcendent atmosphere
```

### Negative baseline applied to every render

```
recognizable face, photorealistic portrait of living person, named celebrity,
identifiable individual, deepfake, specific real person likeness, news photograph,
papal portrait, harsh lighting, neon, busy composition, chaotic, blurry, low quality,
watermark, text overlay, signature, distorted anatomy, extra limbs,
cool blue-only palette, green-heavy palette,
haze, ethereal blur, translucent body, foggy, misty, volumetric haze, soft global blur,
washed out colors, low contrast, no anchor element
```

---

## Word-level forced alignment

**Why not WPM estimates:** narration delivery varies dramatically within a single recording. The `ahjan_update.wav` runs ~166 effective wpm overall, but individual sections compress or expand based on emotional weight. A "Then came the diagnosis. Ninety days to live." beat may take 4 seconds of audio for 7 words (35 wpm) for dramatic effect; the next paragraph may run at 200 wpm. WPM estimates miss this.

**Tool:** vanilla `openai-whisper` with `word_timestamps=True`, model `base` (sufficient accuracy for visual timing; uses ~3 min CPU wall-clock per 11 min of audio).

**Why not stable_whisper:** on macOS Python 3.9 the torchaudio/torch ABI mismatch breaks the `stable_whisper` import (`libtorchaudio.so` missing symbol `__ZN3c1015SmallVectorBaseIjE8grow_podEPKvmm`). Don't fight this; vanilla whisper transcribe + word_timestamps is sufficient. Document this fallback in `scripts/video/whisper_word_align.py`.

**Beat-to-whisper snap algorithm** (`snap_beats_to_whisper()` in builder):
- Maintain a whisper word cursor that advances as each beat consumes its words
- For each beat, try to anchor the start by fuzzy-matching the beat's first word (normalized to alphanumeric-only, lowercase) against the next 5 whisper words
- Whisper sometimes mis-transcribes proper nouns ("Ajahn" vs "Ahjan", "Joshin Sennett" vs "Joshin Sensei", "Sai Mar" vs "Sai Maa") — when no match within 5-word window, advance cursor by beat word count without anchoring; timing stays approximately correct
- Use whisper start of beat-first-word, whisper end of beat-last-word as the beat's audio window
- Frame for that beat is held for `end_s - start_s` seconds in the concat manifest

---

## Frame numbering convention

| Range | Owner | Notes |
|---|---|---|
| `frame_0000` – `frame_0120` | v1.0 / v1.1 (original 121-frame library) | Includes v1.1 surgery insert at 0011 and rewrites in §10 |
| `frame_0200` – `frame_0299` | v2 (specific moments inserted, e.g., flying-in-light) | |
| `frame_3000` – `frame_3999` | v3.1 beat-driven renders | One per `render_new` beat; deterministic seed = blake2b(beat_id)[:4] |
| `frame_4000+` | future beat-driven videos | |

PNGs persist on disk across versions so a v3 build can reference any frame from v1.0 or v2. Concat manifest is the source of truth for which frames play when.

---

## Concat manifest format (per-beat duration)

```
ffconcat version 1.0
file 'frames/frame_0003.png'
duration 4.821                ← from whisper: end_s - start_s for this beat
file 'frames/frame_3000.png'
duration 6.382
...
file 'frames/frame_3041.png'   ← terminating file reference required by concat-demuxer
```

The terminating file (no `duration` line) is required by ffconcat to honor the last beat's duration directive. Without it the last frame plays for the codec-default 1/fps and clips.

---

## Final-mix command (always with `-shortest`)

```bash
ffmpeg -y -i <video>_silent.mp4 -i <video>.wav \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v -map 1:a -shortest <video>.mp4
```

`-shortest` clips video to audio end. If video > audio (because beat durations slightly overshoot), the visual tail is trimmed. If video < audio (rare — only happens if beats undercount), the audio tail is trimmed; in this case re-build with adjusted beat durations.

---

## Operator review gate

After build, the operator scrubs the final MP4 against the beat timing JSON (`beat_timing_v3_1.json`). For any mis-aligned beat (visual doesn't match what's being narrated at that timestamp), the fix is:

1. Edit the beat's prompt in `<video>_beats.py`
2. Bump the beat's `_new_frame_index` (or delete the cached PNG so the builder re-renders)
3. Re-run the build script — only changed beats render; cached PNGs reused; ffmpeg re-assembles + re-mixes (~12 min)

This makes surgical iteration cheap.

---

## When to use this pipeline vs the existing 11-stage `run_pipeline.py`

**Use beat-driven (this spec):**
- Named-entity-rich narrative (named masters, locations, events, quotes)
- Sacred / spiritual / philosophical content where generic stock imagery fails
- Single-script single-narrator long-form (5+ min)
- Manual operator review of every beat is acceptable

**Use the existing 11-stage pipeline:**
- Templated shorts (15-60s) where image-bank retrieval is sufficient
- Therapeutic / meditation content where the visual treatment is conceptual rather than specific
- Multi-channel high-volume production (24-brand strategy)
- Automated production where operator review is per-batch not per-beat

The two pipelines coexist. `scripts/video/run_pipeline.py` continues to be the orchestrator for high-volume work; beat-driven is the dispatched-LLM-author pattern for high-specificity narrative.

---

## See also

- `docs/VIDEO_PIPELINE_SPEC.md` — the 11-stage canonical pipeline this extends
- `docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md` — anti-washout rules, palette lock authority
- `docs/specs/PEARL_VIDEO_YT_STARSEED_AHJAN_UPDATE_V1_SPEC.md` — v1.0 spec (10s cadence section-anchor approach; superseded by v3.1 beat-driven for this video)
- `docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md` — research on forced-alignment, animation, audio post-production
- `CLAUDE.md` § "LLM Tier Policy" — Tier-1 (operator-present Claude Code) is the authorized LLM for beat-prompt synthesis; no paid API calls

---

## Reference implementation

- **Beat manifest:** `scripts/video/v3_1_beats.py` — 90 beats for `docs/ahjan_update.txt` (1,927 words, 11:33 WAV at 166 effective wpm)
- **Builder:** `scripts/video/build_v3_1_yt_starseed.py` — render + manifest + assemble + mix
- **Word align:** `scripts/video/whisper_word_align.py` — vanilla whisper word_timestamps
- **Artifacts:** `artifacts/video/yt_starseed_ahjan_update_20260610/`
  - `whisper_alignment.json` — 1893 words aligned to 693.5s
  - `beat_timing_v3_1.json` — per-beat audio windows
  - `frames_concat_v3_1.txt` — ffmpeg concat manifest
  - `ahjan_update_starseed_v3_1.mp4` — final output

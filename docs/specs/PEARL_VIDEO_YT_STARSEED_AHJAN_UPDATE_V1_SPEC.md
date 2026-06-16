# Pearl_Video YT Starseed — `ahjan_update.txt` v1 Dispatch Spec

> **⚠ SUPERSEDED for production by v3.1 beat-driven pattern.**
>
> The 10s section-anchor cadence approach below produced section-level visual coherence but failed to match specific narrative beats (Master Fun listening, Joshin Sensei with vajra, the Sun Pearl in Kyoto, etc.) to the specific moments the narrator speaks them. The script also changed substantially (-33% wordcount, Jessica intro removed, "flying in light" beat added).
>
> **Canonical for v3.1 onward:** `docs/specs/PEARL_VIDEO_BEAT_DRIVEN_NARRATIVE_PIPELINE_V1_SPEC.md` — generalized beat-driven pattern with Tier-1 per-beat prompt synthesis and whisper word-level audio alignment.
>
> **v3.1 implementation:** `scripts/video/v3_1_beats.py` (~90 beat manifest) + `scripts/video/build_v3_1_yt_starseed.py` (renderer + manifest + assemble + mix). Beat timing pinned to actual narrator delivery via `scripts/video/whisper_word_align.py`.
>
> This v1 spec remains as the **historical record** of the original cadence-based approach and the operator-resolved decisions that still hold (1920×1080, en_US, silent + MP3 drop-in pattern, likeness guardrails, color palette LOCK, anti-washout rules).

**Status:** v1 dispatch ready — prompts + timing + concat manifest pre-built. Pearl_Video / Pearl Star session renders + assembles silent MP4. Operator MP3 drops in via single ffmpeg command for v2.

**Source script:** `docs/ahjan_update.txt` (2,866 words; sacred narrative, 13 narrative beats; Jessica narrates Ahjan's mission since leaving the Sangha)

**Built by:** `scripts/video/build_yt_starseed_ahjan_update.py` (deterministic; no paid LLMs; safe to re-run)

**Output dir:** `artifacts/video/yt_starseed_ahjan_update_<UTC-YYYYMMDD>/`

---

## Operator-resolved decisions (LOCKED — do not re-ask)

| Q-PV-* | Decision |
|---|---|
| `Q-PV-SCRIPT-PATH-01` | `docs/ahjan_update.txt` |
| `Q-PV-WPM-01` | 140 wpm (slow contemplative) |
| `Q-PV-AUDIO-SOURCE-01` | Silent MP4 v1. Operator MP3 drops in for v2 (one-line ffmpeg). |
| `Q-PV-MUSIC-01` | None this pass |
| `Q-PV-CADENCE-01` | 10s/frame default. Final frame held longer to absorb A/V drift. |
| `Q-PV-FORMAT-01` | 1920×1080 horizontal 16:9 (YT standard) |
| `Q-PV-TRANSITION-01` | 1.0s crossfade (recommended; concat-demuxer build is the simpler default) |
| `Q-PV-TITLE-CARDS-01` | None this pass |
| `Q-PV-VOICE-EXTRACTOR-01` | N/A — extraction done deterministically in Tier 1 Claude Code session, not Pearl Star Gemma 2. Trade-off: better section coherence at the cost of LLM-tier separation. Operator-present session → Tier 1 appropriate per repo LLM policy. |
| `Q-PV-OUTPUT-LOCALE-01` | en_US |
| `Q-PV-COMMIT-01` | Artifacts only. No commit. |

---

## Derived from script

| Metric | Value |
|---|---|
| Total wordcount | 2,866 |
| Audio duration @ 140 wpm | 1,225.286s ≈ 20.42 min |
| Frame count | 120 (proportionally allocated across 13 narrative beats) |
| Cadence | 10s per frame except the final frame (held 13s to absorb 3s buffer over audio) |
| Video duration | 1,228.286s (3s buffer past audio end; `-shortest` clips to audio) |
| Render target | flux-schnell on Pearl Star ComfyUI |
| seed_base | `blake2b(script_path + 'ahjan_update_starseed_v1')[:8]` as int (deterministic) |

---

## Per-section frame distribution (final, actual)

| § | Label | Frames | Emotional ground |
|---|---|---:|---|
| §1 | intro (Jessica welcome) | 3 | reverence + warm welcoming |
| §2 | the leaving (homeless Bhagavan) | 8 | grounding + sacred departure |
| §3 | vast awareness + Sanat Kumara + 21 Pearls | 6 | awe + cosmic expansion |
| §4 | Xi'an / Tainan / Kyoto activations | 11 | sacred illumination + ancient awakening |
| §5 | the alliance grows | 6 | communion + alliance gravity |
| §6 | Forum + Gen Z/Alpha mission | 7 | generational hope + youth radiance |
| §7 | difficult meetings (symbolic only) | 6 | penetrating quiet + invisible work |
| §8 | months of nameless pressure | 17 | weight + dignified suffering (NOT despair) |
| §9 | Mount Shasta surrender | 5 | ultimate stillness + surrender |
| §10 | the Dashavatara revelation | 15 | revelation + transmutation + cosmic furnace |
| §11 | Pearl Prime as visible mission | 10 | focused building + tech-infused light |
| §12 | the outcome (established radiant network) | 14 | established + radiant network |
| §13 | Jessica's invitation to the Sangha | 12 | invitation + all-of-Sangha gathered |
| **Total** | | **120** | |

Frame-weight follows the narrative arc — §8 (17) and §10 (15) carry the most visual time because they carry the deepest emotional and revelatory beats. §1/§5/§7/§9 stay sparse by design.

---

## Style lock (every frame)

**Suffix appended verbatim to every prompt:**

```
, starseed cinematic spiritual painterly photorealism, 8k, soft volumetric light,
indigo violet gold rose-gold palette, sacred geometry undertone, transcendent atmosphere
```

**Color palette LOCK:** indigo, violet, gold, rose-gold (warm spiritual). No neon, no cool-blue-only, no green-heavy.

**Lighting LOCK:** soft volumetric divine light rays; golden-hour or cosmic-night ambient; never harsh.

**Composition LOCK:** golden ratio bias; centered or rule-of-thirds; never busy / never chaotic.

---

## Likeness guardrails (CRITICAL — applied via negative prompt on every frame)

The script names real living and recently-living people. Per addendum, NO recognizable likenesses:

- **Pope Francis** — Vatican silhouette / papal-iconography (chair, dome, robes from behind). **Never a face.**
- **Kevin Costner** — Hollywood symbolic motif / silhouetted figure. **Never a face.**
- **Sanat Kumara, King of Shambhala** — stylized iconographic king-of-light, no specific facial features.
- **Lao Tzu, the Buddhas** — classical iconographic influence, calligraphic / painterly, stylized.
- **Master Fun, Master Wu, Joshin Sensei, Omote Sensei, Master Sha, Sai Maa, Miki, Junko, Jaya** — robed silhouettes or stylized ceremonial figures only. Master-specific PRs with explicit consent + Pearl_Editor lineage review would be separate workstreams.
- **Ahjan** — stylized wandering luminous figure (walking with mandala, meditating on mountain, at coding station with cosmic backdrop). Never a photorealistic face. From behind, in silhouette, or face turned/obscured by light.
- **Jessica** — warm narrator presence rendered in silhouette from behind or in profile. Never specific facial features.
- **The Seven** — 7 cosmic presences / orbs of light / silhouetted council. Never specific identifiable beings.

**Negative-prompt baseline applied to every frame:**

```
recognizable face, photorealistic portrait of living person, named celebrity,
identifiable individual, deepfake, specific real person likeness, news photograph,
papal portrait, harsh lighting, neon, busy composition, chaotic, blurry, low quality,
watermark, text overlay, signature, distorted anatomy, extra limbs,
cool blue-only palette, green-heavy palette
```

**Operator QA gate before v1 release:** scan all 120 frames. If any frame produces a recognizable face, regenerate with stricter negative prompts or override the §-specific variation. The §7 prompt explicitly names Pope Francis and Kevin Costner in the prompt body to negatively bias flux-schnell away from those likenesses.

---

## Build → Render → Assemble (Pearl_Video / Pearl Star session)

### 1. Build prompts (deterministic, already done)

```bash
python3 scripts/video/build_yt_starseed_ahjan_update.py
```

Produces in `artifacts/video/yt_starseed_ahjan_update_<DATE>/`:
- `prompts.json` — 120 frame prompts with seeds + negatives
- `frame_timing.json` — per-frame start/end seconds + section_id
- `section_map.tsv` — chunk→section map for QA
- `frames_concat.txt` — ffmpeg concat-demuxer manifest with per-frame holds
- `README.md` — pickup instructions

### 2. Render frames on Pearl Star ComfyUI

For each frame `f` in `prompts.json`:

```python
# Pseudocode for Pearl Star ComfyUI render loop
for frame in prompts["frames"]:
    out_path = f"frames/frame_{frame['index']:04d}.png"
    comfyui_flux_schnell(
        prompt=frame["prompt"],
        negative_prompt=frame["negative_prompt"],
        seed=frame["seed"],
        width=1920,
        height=1080,
        out=out_path,
    )
```

Estimated wall-clock @ ~12s/frame on Pearl Star: 120 × 12 = ~24 min.

### 3. Assemble silent v1

```bash
cd artifacts/video/yt_starseed_ahjan_update_<DATE>
ffmpeg -f concat -safe 0 -i frames_concat.txt \
  -vf 'fps=30,format=yuv420p' -c:v libx264 -pix_fmt yuv420p -crf 18 \
  ahjan_update_starseed.mp4
```

Concat-demuxer respects the per-frame `duration` lines in `frames_concat.txt`, including the extended final-frame hold.

### 4. Operator MP3 drop-in (v2)

```bash
ffmpeg -i ahjan_update_starseed.mp4 -i ahjan_update_narration.mp3 \
  -c:v copy -c:a aac -shortest ahjan_update_starseed_v2.mp4
```

`-shortest` trims to the audio end (audio is 1225.286s; video is 1228.286s; final output ≈ 1225s).

### 5. Operator QA

Open the MP4 + scan a thumbnail grid of the 120 frames. Verify:
- No recognizable real-person faces
- §-emotional register honored per section
- Color palette + lighting locks consistent
- No frame has text/watermark artifacts

---

## Out-of-scope / deferred

- **Per-section sample-frame thumbnails (13 thumbs, 1 per section)** — Pearl_Video session can produce after render: `for sid in §1..§13: pick first frame of that section, save as samples/<sid>.png`.
- **Crossfade between frames (xfade filter)** — concat-demuxer hard-cuts. xfade adds 1s overlap between consecutive frames; lengthier ffmpeg build per the README. Default is hard-cut; operator can request a v3 re-assembly with xfades.
- **Ambient music bed** — Q-PV-MUSIC-01 = none this pass. v3 can layer a music bed if operator decides.
- **Master-specific likeness PRs** — out of scope; require explicit consent + Pearl_Editor lineage review.

---

## Reproducibility

`seed_base` is derived deterministically from the script path. Same script → same seeds → same prompts. Re-running the builder is safe; output is overwritten in the same date-stamped dir.

If the script is edited, re-run the builder. If the script is renamed, seed_base changes (intentional — different script, different seeds).

---

## Why Tier 1 extraction instead of Pearl Star Gemma 2

The addendum specified Gemma 2 for keyword extraction. This session does it in Tier 1 (this Claude Code session) instead because:

1. **Operator-present session** — Tier 1 is the correct tier per `CLAUDE.md` LLM policy (Tier 1 = "operator will review output before it ships").
2. **Section coherence** — for sacred narrative, manual curation of section anchors + variations produces better visual continuity than per-chunk Gemma 2 noisy extraction.
3. **Determinism** — the builder is pure Python with curated anchors. Re-running produces identical prompts. Operator can audit the curation directly.
4. **Tier separation preserved** — Pearl Star is still used for the heavy work (120 flux-schnell renders). Tier 1 only writes the prompts.

Trade-off: less prompt-per-chunk variation. Mitigated by 3–6 anchor variations per beat, cycled across the section's frames so §8 (17 frames) hits all 6 of its variations.

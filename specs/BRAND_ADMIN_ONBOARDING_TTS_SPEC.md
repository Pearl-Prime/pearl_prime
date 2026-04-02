# Brand Admin Onboarding — TTS / ElevenLabs / SSML

**Purpose:** Contract for **brand briefing narration**: ElevenLabs audio aligned to **teacher Ahjan**, **cumulative** voice/prosody state across wizard-style choices, and **SSML** (or SSML-like) pacing. Complements [BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](./BRAND_ADMIN_MEDIA_GENERATION_SPEC.md) (image/video).

**Related:** [ONBOARDING_OUTPUT_PROOF_SYSTEM.md](./ONBOARDING_OUTPUT_PROOF_SYSTEM.md), [BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md](./BRAND_ADMIN_ONBOARDING_WIZARD_SPEC.md), implementation [brand-wizard-app/src/BrandWizard.jsx](../brand-wizard-app/src/BrandWizard.jsx).

---

## 1. Terminology: SSM vs SSML vs AWS SSM

- **SSML** (Speech Synthesis Markup Language): markup for breaks, prosody (`rate`, `pitch`), and emphasis. Used here to reflect **on-screen meaning** (pace, pause density).
- **ElevenLabs `voice_settings`:** API fields `stability`, `similarity_boost`, `style`, `use_speaker_boost` — tuned **cumulatively** from the same choice sequence.
- **AWS Systems Manager (SSM) Parameter Store:** optional **secret storage** for `ELEVENLABS_API_KEY` in deploy environments only. It does **not** replace SSML; it is unrelated to “reflect the words on screen” except holding credentials.

---

## 2. Deployed HTML vs narration copy source

| URL / asset | What the user sees |
|-------------|-------------------|
| **`/` (Vite `index.html`)** | **Pearl Prime Brand Wizard** (React): intro “Voice, Visual, Reader, Formats”, five beats, sliders, etc. |
| **`/us_brand_admin_v32_briefing.html`** | **Static** “V3.2 Marketing Intelligence — US Market” (tabs: Overview, EOIS, Audiobook, …). Synced to Pages via [scripts/onboarding/sync_onboarding_config_to_public.sh](../scripts/onboarding/sync_onboarding_config_to_public.sh). |

**Canonical driver for the briefing narration pipeline** is [config/onboarding/tts/briefing_narration_fixture.json](../config/onboarding/tts/briefing_narration_fixture.json): on-screen strings aligned to **BrandWizard** categories (intro, archetype, persona, moment, tradition, visual, voice sliders, emotions, angles, formats). Update the fixture when wizard copy changes.

---

## 3. VoiceProfile (cumulative state)

Ordered steps **never reset** the profile; each step **applies a delta** then **clamps**.

| Field | Role |
|-------|------|
| `stability` | ElevenLabs consistency (higher → steadier). |
| `similarity_boost` | Closeness to reference voice. |
| `style` | Expressive exaggeration (model-dependent). |
| `use_speaker_boost` | Boolean; optional per-step override. |
| `prosody_rate_percent` | SSML `rate` baseline (e.g. 100 = default). |
| `prosody_pitch_percent` | SSML `pitch` baseline (e.g. 100 = default). |
| `break_after_ms` | Pause after each step segment (cumulative tendency). |

**Rule:** First choice sets the **spine**; later choices **add** bounded deltas (see [config/onboarding/tts/ahjan_elevenlabs.yaml](../config/onboarding/tts/ahjan_elevenlabs.yaml)).

---

## 4. Input contract (`briefing_narration_fixture.json`)

Top level:

- `source`: string identifier.
- `teacher_id`: must be `ahjan` for this pack.
- `steps`: ordered array of objects:
  - `id`: stable id.
  - `category`: e.g. `intro`, `archetype`, `persona`, `voice`, `visual`, `formats`.
  - `narration_text`: verbatim or wizard-aligned copy to speak.
  - `delta`: optional object; numeric fields merge into VoiceProfile (additive before clamp).
  - `sliders`: optional map `VOICE_SLIDERS` id → 0–100; applies formula from YAML `slider_deltas`.

---

## 5. Output layout

Script: [scripts/onboarding/generate_briefing_narration.py](../scripts/onboarding/generate_briefing_narration.py).

| Output | Description |
|--------|-------------|
| `artifacts/onboarding_audio/briefing_ssml.xml` | Full `<speak>` document (dry-run or alongside audio). |
| `artifacts/onboarding_audio/briefing_segment_profiles.json` | Audit: each step’s cumulative profile after deltas. |
| `artifacts/onboarding_audio/briefing_voice_profile.json` | Final profile after last step. |
| `artifacts/onboarding_audio/briefing_ahjan_male.mp3` | Merged male render (requires `ffmpeg` on PATH). |
| `artifacts/onboarding_audio/briefing_ahjan_female.mp3` | Merged female render (requires `ffmpeg` on PATH). |
| `artifacts/onboarding_audio/segments/ahjan_male_NN.mp3` | Per-step segments (always when API runs). |
| `artifacts/onboarding_audio/segments/ahjan_female_NN.mp3` | Per-step segments (always when API runs). |

Generated `.mp3` files are **gitignored**; commit the fixture, YAML, spec, and script only.

---

## 6. Secrets and environment

| Variable | Purpose |
|----------|---------|
| `ELEVENLABS_API_KEY` | API auth (never commit). |
| `ELEVENLABS_VOICE_ID_MALE` | First male catalog voice (or Ahjan-approved clone id). |
| `ELEVENLABS_VOICE_ID_FEMALE` | First female catalog voice (or Ahjan-approved clone id). |

Voice IDs may also be set in `ahjan_elevenlabs.yaml` under `voices.male_id` / `voices.female_id` for local non-secret overrides.

---

## 7. Verification

- Same `steps` order: male and female outputs differ only by timbre, not script.
- Cumulative: later steps use **strictly monotonic** profile evolution unless a delta is negative by design (still clamped).
- Re-run after **BrandWizard.jsx** copy edits: diff the fixture against UI strings.

---

## 8. Registry (optional, future)

To surface audio in onboarding proof UX, extend [config/onboarding/example_registry.json](../config/onboarding/example_registry.json) with a row using `production_fidelity: pipeline_demo` and an `asset_path` to hosted MP3 — only after assets exist and CI allows audio proof types (validator may need extending).

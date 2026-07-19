# Handoff — Social Media Voice Matrix (Wave 1 → operator → Wave 2)

**From:** Pearl_Research · **To:** Operator (Layer-4 listen) → Pearl_Int Lane 2  
**Date:** 2026-07-19 · **Signal:** `social-media-voice-matrix-ratified` (OPD-SMV-01)

## What landed

| Artifact | Path |
|----------|------|
| Research extension (§7 Short-Form Social / Reels) | `docs/VOICE_PERSONA_TOPIC_RESEARCH.md` |
| Alias reconcile | `docs/VOICE_MEDIUM_PERSONA_TOPIC_RESEARCH.md` → canonical |
| Selection matrix (PROPOSED) | `config/tts/social_media_voice_matrix.yaml` |
| Report + auditions | `artifacts/research/social_media_voice_matrix_2026-07-19/` |
| Registry row | `social_media_voice_matrix` in `CANONICAL_ARTIFACTS_REGISTRY.tsv` |

## Operator action (unblocks Lane 2)

1. `open artifacts/research/social_media_voice_matrix_2026-07-19/auditions`
2. Listen using `LISTEN_ORDER.md` in that folder.
3. Ratify **Q-SMV-01…04** — reply **"go with defaults"** or list overrides.
4. On ratify, flip matrix `ratification.status` → `RATIFIED` and emit durable signal:
   `social-media-voice-matrix-ratified=<commit-sha>`
5. Then paste Wave 2: `docs/agent_prompt_packs/20260719_social_media_voice_bank/02_Pearl_Int_mp3_bank_generation.md`

## Recommended defaults (for “go with defaults”)

- **Q-SMV-01:** CosyVoice2 for EN reels (ElevenLabs escape hatch if a persona fails the listen)
- **Q-SMV-02:** en-US evergreen 1,620 only
- **Q-SMV-03:** one voice per persona + topic param modulation
- **Q-SMV-04:** freeze matrix; **decide** whether healthcare may scale on INTERIM `english_female` or must wait for `en_f_warm_caregiver_01` clone

## Lane 2 must stand down until

Verifiable `social-media-voice-matrix-ratified=<sha>` on a durable surface (committed matrix + this handoff / OPD row). `READ-PENDING` alone is **not** a green light.

## RAP note for Lane 2

`pscli enqueue` has no CosyVoice TTS task yet. Prefer registering `tts_cosyvoice2` **or** document on-box synth after a working `gpu-acquire`. Do not silent-bypass via laptop `curl $COSYVOICE_URL`.


## Ratification (OPD-SMV-01)

Operator listen 2026-07-19:
- BEST: `corp_mgr_anxiety_english_female_ALT`, `corp_mgr_anxiety_english_male`
- GOOD: `rn_compassion_fatigue_english_female`, `smoke_corporate_anxiety_english_male`, `genz_anxiety_english_female`
- BAD: `corp_mgr_burnout_english_male`, `genz_courage_english_female`, `rn_anxiety_english_female`

Frozen: CosyVoice; corp=`english_female` (alt `english_male`); gen_z/RN=`english_female`; CF-biased RN base; softened burnout/courage; CTSS waiver for pilot.
Lane 2 unblocked.

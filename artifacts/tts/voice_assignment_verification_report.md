# Voice assignment verification report

Generated: 2026-04-09  
Project: `proj_state_convergence_20260328`  
Sources: `config/tts/narrator_voice_assignments.yaml`, `config/tts/voice_clone_reference_library.yaml`, `artifacts/tts/ecapa_pairwise_scores.yaml`, `config/authoring/pen_name_teacher_profiles_full.json`, `config/catalog_planning/diversity_guards.yaml`

## Executive summary

- **Reference clips:** 40 mono WAV files exist under `assets/tts/reference_clips/` (gitignored). Each `reference_id` is populated with `local_path`, `duration_s` (6.000s after padding), and `sample_rate` 16000 in `voice_clone_reference_library.yaml`.
- **Acoustic verification:** ECAPA-TDNN (`speechbrain/spkrec-ecapa-voxceleb`) pairwise cosines computed locally. **Zero** pairs exceeded the CTSS block threshold of **0.90**. Same-locale CJK maxima were all **below 0.85** on these clips.
- **Author coverage:** **480** author slots keyed as `teacher_id__brand_id`. **Zero** slots missing from `narrator_voice_assignments.yaml` relative to `pen_name_teacher_profiles_full.json`.
- **diversity_guards.yaml (topic/persona caps):** Primary-topic share max **~0.202** and primary-persona share max **~0.077** vs configured **0.30** — **PASS** for `max_share_per_topic` / `max_share_per_persona` with `fail_on_violation: true`.

## Unique audiobook voices (global count)

Counts combine providers into comparable keys `(provider, id)` for the **audiobook** row only.

| Locale | Distinct voices | Authors |
|--------|-----------------|--------:|
| ja-JP | 10 (CosyVoice2 references) | 480 |
| ko-KR | 8 | 480 |
| zh-TW | 8 | 480 |
| zh-CN | 8 | 480 |
| zh-HK | 6 | 480 |
| en-US | 25 (ElevenLabs voice_id) | 480 |
| es-US | 9 | 480 |
| es-ES | 9 | 480 |
| fr-FR | 9 | 480 |
| de-DE | 9 | 480 |
| hu-HU | 9 | 480 |

**Interpretation:** CJK locales intentionally reuse a small **clone-reference** set across brands; collision safety is enforced **within brand+locale** for CosyVoice2 **audiobook** `reference_id` (see automated check below). English and European locales reuse ElevenLabs identities across brands — consistent with the published `brand_defaults` comment that only **brand+locale** must remain unique.

## ECAPA-TDNN — closest pairs (global top 10)

From `artifacts/tts/ecapa_pairwise_scores.yaml` after mono@16kHz padding:

1. hk_m_warm_01 × tw_f_mature_01 — **0.5853**
2. ja_f_compassionate_01 × ja_m_energetic_01 — **0.4727**
3. hk_f_gentle_01 × hk_m_steady_01 — **0.4569**
4. hk_f_clear_01 × ko_m_deep_01 — **0.3976**
5. hk_f_mature_01 × ja_f_compassionate_01 — **0.3932**
6. hk_f_clear_01 × hk_f_gentle_01 — **0.3868**
7. ja_f_gentle_01 × tw_m_energetic_01 — **0.3769**
8. cn_m_energetic_01 × hk_m_warm_01 — **0.3719**
9. cn_f_clear_01 × ja_m_steady_01 — **0.3691**
10. cn_f_mature_01 × tw_m_warm_01 — **0.3678**

**CTSS threshold 0.90:** satisfied (no pairs ≥ 0.90).

## Same-locale ECAPA maxima (reference-id prefixes)

| Locale prefix | Max cosine | Closest pair |
|-----------------|-----------:|--------------|
| ja- | 0.4727 | ja_f_compassionate_01 × ja_m_energetic_01 |
| ko- | 0.2872 | ko_m_deep_01 × ko_m_warm_01 |
| cn- | 0.2467 | cn_f_bright_01 × cn_m_energetic_01 |
| tw- | 0.2659 | tw_m_energetic_01 × tw_m_steady_01 |
| hk- | 0.4569 | hk_f_gentle_01 × hk_m_steady_01 |

Stricter **0.85** same-locale rule: satisfied for these measurements.

## Constraint checks (automated)

| Check | Result |
|-------|--------|
| ja-JP audiobook: `reference_id` unique within each `brand` | **PASS** (0 duplicate brands) |
| ElevenLabs present under `ja-JP` | **PASS** (no matches) |
| `pen_name_teacher_profiles_full.json` row count == YAML author count | **PASS** (480 == 480) |
| diversity_guards topic/persona concentration | **PASS** (see shares above) |

## Known gaps / follow-ups

1. **Locale-native audio:** Clips are **LibriSpeech** stand-ins, not Japanese/Korean/Mandarin/Cantonese native speech. They unblock CosyVoice2 formatting + ECAPA plumbing but should be replaced with catalog sources in `voice_clone_reference_library.yaml` for production timbre.
2. **Pearl Star replication:** ECAPA ran on the dev workstation (`savedir=/tmp/ecapa_sb`). Re-run on `192.168.1.112` if embeddings must be co-located with CosyVoice2 for ops policy.
3. **Instruction vs inventory:** Microsoft Edge exposes **two** `ja-JP` neural voices as of 2026-04-09; literal “globally unique Edge voice per author per locale” is **infeasible** without additional providers or clone-only channels. This assignment pack therefore uses **CosyVoice2 on all ja-JP media rows** (with `edge_fallback` retained on audiobook for continuity with prior spec examples).

## Artifact index

| Path | Purpose |
|------|---------|
| `assets/tts/reference_clips/*.wav` | Local CosyVoice2 references (gitignored) |
| `artifacts/tts/ecapa_pairwise_scores.yaml` | Full 780-pair cosine table |
| `config/tts/voice_clone_reference_library.yaml` | Clips + metadata |
| `config/tts/narrator_voice_assignments.yaml` | 480 author slots |
| `config/tts/voice_diversity_matrix.yaml` | Measured ECAPA blocks per locale |

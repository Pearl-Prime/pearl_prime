# Social Media Voice Matrix — Research Report (Wave 1)

**Date:** 2026-07-19 · **Owner:** Pearl_Research · **Pack:** `docs/agent_prompt_packs/20260719_social_media_voice_bank/`
**Acceptance layer:** EXECUTED-REAL auditions; matrix “best-ness” = **READ-PENDING** (Layer-4 operator taste)
**Resume surface:** this file · **Auditions:** `auditions/`

---

## STARTUP_RECEIPT (live-verified)

| Claim | Live truth | Delta |
|-------|------------|-------|
| cwd `/Users/ahjan/phoenix_omega` | yes | — |
| branch | `codex/realist-social-samples-20260718` at session start | Wave-1 lands on `agent/social-media-voice-matrix-20260719` |
| `git fetch origin` | **403 account suspended** | `github=BLOCKED-403`; ground on local `origin/main` `9e9b9e6067` |
| evergreen atoms | **1,620** | matches claim |
| personas | `corporate_managers`, `gen_z_professionals`, `healthcare_rns` (540 each) | matches |
| topics | **20** (includes addiction/adhd/body_image/divorce/money/relationship_anxiety/shame beyond long-form §3) | claim OK; research extended for gaps |
| `surface_fit` | multi-surface string **including** `short_video_script` (not sole value) | claim “all short_video_script” = true as membership, not exclusivity |
| `platform_fit` | includes `tiktok_reels_shorts` for all 1,620 | matches |

---

## DISCOVERY REPORT / PROVENANCE

```
research:   docs/VOICE_PERSONA_TOPIC_RESEARCH.md (EXTENDED §7) + ElevenLabs EN research (operator: done, not re-run)
documents:  config/tts/voice_diversity_matrix.yaml ; config/tts/engines.yaml (§cosyvoice2)
builds_on:  §3 topic acoustic table (pace/pause/warmth/pitch) energy-shifted for reels
inventory:  EXTENDS — short-form section + NEW config/tts/social_media_voice_matrix.yaml
external:   go-viral.app first-3s hooks; Pavone Reels pacing (~+25%, cut >0.5s pauses);
            AiVoicePedia short-form AI voice norms; ~−14 LUFS short-form loudness practice
```

**Stale-ref reconcile:** `docs/VOICE_MEDIUM_PERSONA_TOPIC_RESEARCH.md` created as **alias redirect**
to the canonical research doc; config authority lines updated to point at
`docs/VOICE_PERSONA_TOPIC_RESEARCH.md`.

**Reuse-first:** did **not** fork a parallel voice research doc. Diversity matrix left as check-only;
selection is the new machine contract (justified).

---

## Engine decision (Q-SMV-01) — RECOMMENDATION

**Recommend default: CosyVoice2 for EN reels**, with ElevenLabs escape hatch per persona if the
listen fails.

| | CosyVoice2 | ElevenLabs |
|---|------------|------------|
| Cost @ 1,620 atoms | $0 (self-hosted) | paid per char |
| EN voices used | `english_male`, `english_female` (+ planned warm-caregiver clone) | Rachel baseline (operator research done) |
| Zero-shot | yes | yes (subscription) |
| RAP / Pearl Star | on-box service; see RAP notes below | cloud API |

**Benchmark notes (EXECUTED-REAL CosyVoice side):**
- Health `GET /api/v1/health` → 200; voices include `english_male`, `english_female`, …
- Smoke + 7 pilot clips synthesized on Pearl Star (`cosyvoice.service`), all ≥300 KB, playable.
- ElevenLabs A/B **not** re-synthed this turn (operator already completed that research; avoid paid burn).
  Operator compares CosyVoice `auditions/` against known Rachel baseline by ear.

**Alternative:** keep ElevenLabs for `gen_z_professionals` only if CosyVoice female reads “corporate training,” not peer.

---

## Selection matrix summary

File: `config/tts/social_media_voice_matrix.yaml`

| Persona | Voice | Archetype |
|---------|-------|-----------|
| corporate_managers | `english_male` | authoritative_clear |
| gen_z_professionals | `english_female` | bright_peer |
| healthcare_rns | `english_female` INTERIM → `en_f_warm_caregiver_01` clone | warm_caregiver |

Topic rows: 20 short-form modulations (reuse §3 + new neighbors). Granularity default = one voice
per persona + topic params (**Q-SMV-03**).

**Diversity risk:** only 2 EN built-ins → healthcare shares speaker with Gen Z until clone.
Flag in matrix: do not full-bank-scale without clone or Q-SMV-04 waiver.

---

## Auditions (EXECUTED-REAL)

Directory: `artifacts/research/social_media_voice_matrix_2026-07-19/auditions/`

| File | Persona | Topic | Voice |
|------|---------|-------|-------|
| `smoke_corporate_anxiety_english_male.mp3` | corporate_managers | anxiety | english_male |
| `corp_mgr_anxiety_english_male.mp3` | corporate_managers | anxiety | english_male |
| `corp_mgr_burnout_english_male.mp3` | corporate_managers | burnout | english_male |
| `corp_mgr_anxiety_english_female_ALT.mp3` | corporate_managers | anxiety | english_female (contrast) |
| `genz_anxiety_english_female.mp3` | gen_z_professionals | anxiety | english_female |
| `genz_courage_english_female.mp3` | gen_z_professionals | courage | english_female |
| `rn_anxiety_english_female.mp3` | healthcare_rns | anxiety | english_female |
| `rn_compassion_fatigue_english_female.mp3` | healthcare_rns | compassion_fatigue | english_female |

Atom text source: evergreen `SOMATIC_SETUP` hooks (persona-specific openers).

### RAP path honesty

- `pscli enqueue` **does not register a TTS task** yet (only t2i + `llm_translate_atoms_batch`).
  Spec §6.3 names `tts_cosyvoice2` jobs; worker queue `tts` exists but no `@app.task` for CosyVoice.
- Local/`ahjan108` `pscli gpu-acquire` failed: `PermissionError` on `/var/lib/pearl-star/gpu_lane`.
- Compliant path used: start `cosyvoice.service` on Pearl Star via SSH Host `pearl_star`, health-check,
  synthesize **on-box** to `127.0.0.1:9880` (not laptop→`COSYVOICE_URL` bypass), SCP auditions local.
- Lane 2 should either register a real `tts_cosyvoice2` Procrastinate task **or** document
  `gpu-acquire` (with writable lane path) + on-box synth as the sanctioned RAP pattern.

---

## Open questions for operator (recommend defaults — do NOT self-decide taste)

1. **Q-SMV-01 (engine):** CosyVoice for EN reels vs keep ElevenLabs?
   → *default:* CosyVoice where it passes your listen; else ElevenLabs per failing persona.
2. **Q-SMV-02 (first-bank scope):** which atoms first?
   → *default:* en-US evergreen (1,620) only.
3. **Q-SMV-03 (voice granularity):** one voice/persona + topic params vs voice per (persona,topic)?
   → *default:* one-per-persona + topic modulation.
4. **Q-SMV-04 (audition ratification):** freeze matrix as golden?
   → reply **"go with defaults"** or list per-Q overrides (especially whether to waive the
   healthcare clone before scale, or require `en_f_warm_caregiver_01` first).

---

## Cleanup ledger

| Item | Status |
|------|--------|
| CosyVoice `cosyvoice.service` | started for auditions — **leave running** for Lane 2 or stop if idle GPU needed |
| Remote `/tmp/smv_auditions_20260719` | copied local; may delete on pearlstar |
| `pscli` jobs | none enqueued (TTS task absent) |
| Audition MP3s in git | **not committed** (binaries stay under artifacts/; production bank → R2 in Lane 2) |

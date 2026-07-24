# Handoff — Qwen/DashScope free-model + social-media TTS research (2026-07-24)

**Agent:** Pearl_PM (Claude Code) · **Type:** research/synthesis only — **no code, no config, no atoms changed**
**Trigger:** Operator asked "pearl research agent ask pearl-int" what free Qwen/DashScope models exist
for social media (TTS voices, CJK, translation, music, content banks), and what's still needed.
**Acceptance layer:** RESEARCHED (synthesis of prior EXECUTED-REAL findings + fresh external web research).
No new probes were run this session; no atoms, config, or code were touched.

---

## What this session actually did

1. Read the operator's question as a request to survey the free-LLM/TTS/media landscape for the
   social-media content pipeline (English + all locales, especially CJK6).
2. Found that this exact question was already answered by prior sessions on 2026-07-19 under the
   `Pearl_Int` / `Pearl_Research` personas, and that work has since **shipped** (merged PRs, ratified
   config). Rather than re-probing DashScope or re-running audits, this session **read and reconciled
   the existing artifacts** (listed below) and added external web research for things not yet covered
   in-repo (Qwen3-TTS open-sourcing, open music models).
3. Answered the operator in chat. This file persists that answer for the next session.

---

## Source artifacts read this session (all pre-existing, dated 2026-07-19 unless noted)

| Artifact | What it established |
|---|---|
| `artifacts/research/qwen_free_tier_recon_20260719/PROBE_LOG.md` | Live probe: `QWEN_BASE_URL` = Pearl Star Ollama (free, local); `DASHSCOPE_BASE_URL` = Singapore intl (correct region). DashScope `/models` returns 149 SKUs; every generation probe returned `Arrearage`. |
| `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md` + handoff | Full free-quota table (video/image/TTS/text, all per-model, 90-day, Singapore-only) — see table below. Live key authenticates but is blocked account-wide by an overdue balance. |
| `artifacts/research/social_media_voice_matrix_2026-07-19/REPORT.md` + handoff | Wave-1 recommendation: CosyVoice2 (self-hosted, $0) over ElevenLabs for the EN social atom bank. Ratified by operator listen (`OPD-SMV-01`/`OPD-SMV-03`). |
| `artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md` | Persona/topic voice-*parameter* modulation (pace/warmth/pitch) was tried and **killed** — operator listen confirmed it degraded quality vs. plain stock voice. Replaced with gender-only stock voices + text-prep (punctuation pacing, homograph rewrites). |
| `config/tts/locale_voice_routing.yaml` | Current live provider chains per locale (see below). |
| `config/tts/social_media_voice_matrix.yaml` | Ratified persona→voice map (schema v2, `RATIFIED`, 2026-07-19). |
| Git log (`social`, `tts` scoped) | Confirms the 1,620-atom EN CosyVoice bank + 60-cell matrix actually merged (PR #36 and related), and that a fresh APAC native-speaker research refresh landed **2026-07-23** (PR #114) — separate lane, atom-authoring focused, not TTS. |
| Internal audit (Explore agent, this session) | Confirmed `scripts/audio/generate_presenter_audio.py` (ElevenLabs-first, briefing decks) is a **separate** pipeline from `scripts/social_media/generate_voice_bank.py` (CosyVoice-first, social atoms) — do not conflate the two when reasoning about "our TTS setup." |

External web research (not previously in-repo, added this session): Qwen3-TTS open-sourcing (Jan 2026, Apache 2.0), open-source music-gen landscape (MusicGen/ACE-Step/Stable Audio Open). See Sources at bottom.

---

## Current ground truth (as of 2026-07-24)

### TTS for social-media atoms
- **Engine of record: CosyVoice2, self-hosted on Pearl Star (`:9880`).** Genuinely $0 — no DashScope account, no quota, no arrearage exposure.
- **Chain (all locales):** `cosyvoice2 → edge-tts (free MS fallback) → elevenlabs (paid, last-resort only)`.
- **EN shipped:** 1,620 evergreen en-US atoms × 3 personas (`corporate_managers`, `gen_z_professionals`, `healthcare_rns`) × 20 topics. Gender-only stock voices only (`english_male` / `english_female`) — **no SSML, no engine-param modulation** (explicitly forbidden in `social_media_voice_matrix.yaml`, learned the hard way). Wired into reels; Metricool dry-run done.
- **CJK6 — configured but NOT yet run for social atoms.** `locale_voice_routing.yaml` has correct per-locale CosyVoice2 voice IDs for ja-JP/ko-KR/zh-CN/zh-TW/zh-HK/zh-SG, including the hard rule that **zh-HK must render Cantonese (`yue`), never Mandarin**. Wave-1 scope (`Q-SMV-02`) was explicitly en-US-only; nobody has pointed the social-atom bank generator at the CJK6 locales yet. This is a scoping gap, not a capability gap — the free path already exists.
- **EU locales (de/fr/es-ES/es-US/it/hu/pt-BR) — still paid.** ElevenLabs primary, Edge-TTS fallback. `hu-HU` is hard-pinned to ElevenLabs because no free neural Hungarian voice exists anywhere.
- **Atom-bank size mismatch:** the atom bank itself is now ~1,996 rows (per 2026-07-23 research, PR #114) but the TTS bank only covers the original 1,620 evergreen EN atoms — newer/repaired rows are not yet voiced.

### CJK6 translation
Free and live: **Ollama Qwen2.5:14b on Pearl Star**, not DashScope cloud. DashScope cloud is a demoted fallback only (since 2026-04-08), and is currently blocked by the same account arrearage anyway.

### Free Qwen/DashScope cloud quota (Singapore/intl, per new-user model, 90-day expiry)

| Family | Free amount | Live status (2026-07-19 probe) |
|---|---|---|
| Video (Wan T2V/I2V) | ~50s per model; HappyHorse 10s | **Blocked — `Arrearage`** |
| Image (Wan / Qwen-Image) | 50–200 images per model | **Blocked** |
| TTS-cloud (CosyVoice-cloud / Qwen3-TTS-cloud) | 10,000 / 110,000 characters | **Blocked** |
| Text/translation | 1,000,000 tokens per model | **Blocked** |

Root cause is an **overdue Alibaba Cloud balance** (account `gmalone@oneteamtech.com`, Singapore console `modelstudio.console.alibabacloud.com/ap-southeast-1`) — this blocks *all* invocation, free-quota or not, per Alibaba's own overdue-payment policy. This is a **financial/billing action** that requires the operator to act directly (out of scope for any agent to perform). Even once cleared, per CLAUDE.md's LLM tier policy this stays **operator-present-only** — never wired into scheduled/unattended pipelines.

### New this session (not in prior research)
- **Qwen3-TTS is now fully open-sourced** (Apache 2.0, released January 2026, 0.6B–1.7B params, HuggingFace/GitHub `QwenLM/Qwen3-TTS`). Free forever, no DashScope account or quota involved — a genuinely separate option from the cloud `qwen3-tts-flash` SKU in the table above. Covers 10 languages (incl. EN/zh/ja/ko) with voice cloning and natural-language delivery control; runs on 8GB+ VRAM (Pearl Star's single 16GB GPU can host it). **Not yet evaluated against CosyVoice2** — worth an A/B pilot before assuming CosyVoice2 stays the default.
- **Open-source music-gen options beyond the MusicGen already named in `MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md`:** ACE-Step (fast full-track generation, runs on consumer GPUs) and Stable Audio Open — both free, self-hostable, worth comparing before committing to MusicGen for the music-bed layer.

---

## Open questions / decisions for the operator (none of these were decided this session)

1. **Extend the ratified EN voice bank to CJK6** — routing config already exists; just needs a run of `scripts/social_media/generate_voice_bank.py` scoped to the CJK6 locales. Low effort, high leverage.
2. **Flip EU locales to CosyVoice2-first** (like EN/CJK) to remove the ElevenLabs cost — `hu-HU` must stay pinned to ElevenLabs regardless (no free alternative exists).
3. **Pay the DashScope Singapore arrearage**, if the operator wants the free image/video/cloud-TTS/translation quota unlocked. Financial action — cannot be done by an agent.
4. **Pilot Qwen3-TTS (open-weights, self-hosted) vs. CosyVoice2** before scaling TTS further — new option, unevaluated.
5. **Voice the ~376-atom gap** between the 1,996-row atom bank (2026-07-23) and the 1,620-atom TTS bank (2026-07-19), once atom authoring for those rows is confirmed non-stub.

## Explicit non-actions this session
- No DashScope probes were re-run (would burn scarce/blocked quota for no new information).
- No git commits/pushes beyond this handoff file.
- No config or atom changes.
- No billing/account actions attempted (prohibited — financial action, operator-only).

---

## Sources (external, added this session)

- [QwenLM/Qwen3-TTS (GitHub)](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS Technical Report](https://arxiv.org/html/2601.15621v1)
- [Alibaba Cloud Model Studio — model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Alibaba Cloud Model Studio — free quota for new users](https://www.alibabacloud.com/help/en/model-studio/new-free-quota)
- [Best open-source music generation models 2026 — SiliconFlow](https://www.siliconflow.com/articles/en/best-open-source-music-generation-models)

## Internal artifacts referenced (pre-existing)

- `artifacts/research/qwen_free_tier_recon_20260719/PROBE_LOG.md`
- `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md`
- `artifacts/research/social_media_voice_matrix_2026-07-19/REPORT.md`
- `artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md`
- `artifacts/coordination/handoffs/dashscope_free_media_2026-07-19.md`
- `artifacts/coordination/handoffs/social_media_voice_matrix_2026-07-19.md`
- `config/tts/locale_voice_routing.yaml`
- `config/tts/social_media_voice_matrix.yaml`
- `config/tts/engines.yaml`
- `docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md`
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §1d, §4

---

## Resume signal for next session

Read this file first. Then pick one of the 5 open questions above — recommend starting with **#1
(CJK6 voice-bank extension)** since it requires no new research, no billing action, and no new
evaluation: the routing config is already correct, only the generation run is missing.

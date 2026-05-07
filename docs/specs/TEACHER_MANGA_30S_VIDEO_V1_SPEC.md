# Teacher × Manga 30-Second Video — V1 Spec

**Status:** PROPOSED — awaiting operator ratification of Q1–Q4 (see §16)
**Cap entry:** `TEACHER-MANGA-30S-VIDEO-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`
**Project:** `PRJ-TEACHER-MANGA-30S-VIDEO-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`
**Owner:** Pearl_Architect (this scoping); Pearl_Video (pilot render); Pearl_Localization (script derivation); Pearl_Editor (style review)
**Subsystems:** video_pipeline (primary) · manga_pipeline (visual style) · teacher_mode (voice fidelity) · translation (locale fidelity)
**Authority docs:**
- `docs/PEARL_ARCHITECT_STATE.md` (cap entry)
- `config/video/format_specs.yaml` (`short` format = 9:16 / 30s envelope)
- `config/video/render_params.yaml` (loudness, vignette, xfade)
- `specs/AI_MANGA_PIPELINE_SUMMARY.md` (visual identity discipline)
- `config/authoring/pen_name_teacher_profiles.yaml` + `config/manga/brand_lora_plans.yaml` (teacher↔brand binding)
- `config/localization/locale_registry.yaml` (locale lock)
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (transformation arc DNA)

**Companion artifact:** `artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv` — the 13-row teacher × brand × locale × style matrix this spec defines.

---

## §1. Scope

12 teachers × 1 video each = **12 deliverables for V1** (with adi_da as a 13th candidate pending operator decision in §16 Q1). 30 seconds each. Vertical 1080×1920 (9:16) primary; landscape 1920×1080 (16:9) secondary if cadence config (`config/release_velocity/video_cadence.yaml`) permits.

This program is a **viewing mode** on existing teacher identity, not a new identity. No new teacher banks. No new `character_design` instances. Style varies wardrobe / setting / lighting / lineart engine; the 12-axis identity locked under `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` stays unchanged.

## §2. Story shape (per video, 30s budget)

| Beat | Window | Function |
|---|---|---|
| **HOOK** | 0–6s | Teacher-as-MC enters the scene; the felt-problem opens. |
| **STRUGGLE** | 6–22s | Visible/embodied dis-ease that mirrors the teacher's signature problem. |
| **RELEASE** | 22–30s | Teacher's signature resolution moment (their actual practice/insight in motion). |

This is the teacher's transformation arc compressed; same DNA as the audiobook chapter-1 climax. Per `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, the HOOK must be specific (named character, specific time/place sensation) and the RELEASE must be a movement of the body, not a rhetorical conclusion.

## §3. Script-reuse rule

Voiceover script meaning is anchored to the teacher's audiobook chapter-1 prose sample at `artifacts/audiobook_samples/_prose/<teacher>_<topic>_ch1.txt`. **Meaning matches; literal verbatim NOT required.**

- 30s ≈ 65–80 English words at conversational TTS pacing.
- Locale-equivalent reading rates apply: ja-JP ≈ 90–110 mora-syllables; zh-TW / zh-CN ≈ 75–95 hanzi.
- Pearl_Localization adapts per locale, NOT translates word-for-word.
- Avoids displacive copyright in social/video context (do NOT re-quote >15-word verbatim spans from audiobook prose).

## §4. Teacher-as-main-character rule

The teacher's `character_design` (from Phase A 12-axis individuation under `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`) is the MC. Same axes that govern the manga renders govern this video.

**No new `character_design` instances created for video — reuse manga's.** This program is identity-preserving.

## §5. Brand binding (verified against `config/manga/brand_lora_plans.yaml.brand_suffixes`)

| Teacher | Manga brand | Brand suffix | Demographic anchor |
|---|---|---|---|
| ahjan | stillness_press | sp | josei (anxiety flagship) |
| joshin | cognitive_clarity | cc | seinen (overthinking flagship) |
| pamela_fellows | somatic_wisdom | sw | josei (somatic_wisdom_shojo per canonical_brand_list) |
| master_feung | qi_foundation | qf | **(unmapped — see D1 in §15)** |
| miki | digital_ground | dg | manhwa (burnout flagship) |
| maat | heart_balance | hb | josei (heart_balance_shojo per canonical_brand_list) |
| junko | relational_calm | rc | josei (relational_calm_iyashikei per canonical_brand_list) |
| master_wu | warrior_calm | wc | shonen (warrior_calm_cultivation per canonical_brand_list) |
| master_sha | sleep_restoration | sr | josei (sleep_restoration_iyashikei per canonical_brand_list) |
| omote | body_memory | bm | josei (body_memory_shojo per canonical_brand_list) |
| ra | solar_return | so | shonen (solar_return_isekai per canonical_brand_list) |
| sai_ma | devotion_path | dp | shonen (devotion_path_shonen per canonical_brand_list) |

12/12 teacher↔brand bindings confirmed against `brand_lora_plans.yaml` (`brand_suffixes` map and `character_loras` keys). All 12 short brand IDs map cleanly to longer canonical entries in `canonical_brand_list.yaml` except **qi_foundation** — see D1.

## §6. Style spread (deliberate range demonstration)

Operator directive: "manga primary, but I want fantasy too, spread of types." Distribution across the 12 deliverables to demonstrate market range without losing teacher fidelity:

| Style mode | Count (of 12) | Description | Assigned teachers |
|---|---|---|---|
| **pure_manga** | 6 | Genre-canonical manga linework + screentone, faithful to brand demographic | ahjan, joshin, miki, junko, omote, master_wu |
| **manga_fantasy_hybrid** | 3 | Manga linework + fantasy setting/wardrobe/landscape (cultivation, isekai, dream) | master_feung, master_sha, ra |
| **cinematic_painterly_fantasy** | 2 | Less manga-stylized, more illustrated-novel cover (warm, brushwork, mass-clinical legibility) | pamela_fellows, sai_ma |
| **experimental** | 1 | Operator-swappable: motion-comic, webtoon-realism, 3D-illustrated, etc. — pushes range demonstration furthest from manga-realism | maat |

**Style-spread guardrail:** even in fantasy/experimental modes, the teacher's `character_design` 12 axes remain locked. Style varies wardrobe/setting/lighting/lineart-engine; identity stays.

Per-teacher rationale lives in the matrix TSV (`rationale` column).

## §7. Locale lock

Operator-stated narration locale per teacher:

| Locale | Teachers |
|---|---|
| **ja-JP** (4) | miki, junko, omote, joshin |
| **zh-TW** (1, +adi_da pending Q1) | master_wu (+ adi_da if Q1=include) |
| **zh-CN** (1) | master_feung |
| **en-US** (6) | ahjan, pamela_fellows, master_sha, maat, ra, sai_ma |

**Anti-drift:** No teacher in a locale they don't natively occupy per this matrix. If a teacher's `pen_name_teacher_profiles.yaml` declares a different native locale, the matrix overrides only with operator approval (Q4).

## §8. Voice layer (locale-native TTS only)

| Locale | TTS pipeline | Notes |
|---|---|---|
| en-US | `edge_tts` ChristopherNeural baseline OR teacher-specific voice if `teacher_voice_profile` exists in `config/audiobook/` | Tier 1 / Tier 2 (free) |
| ja-JP / zh-TW / zh-CN | CosyVoice2 on Pearl Star (free, Tier 2, unattended) | Reference-voice clone if teacher reference exists; else nearest-locale stock voice |

**Banned for unattended Tier 2 batch:** ElevenLabs paid, OpenAI TTS, DashScope cloud TTS. Tier 1 (Claude subagent script) is permitted only when operator-present.

## §9. LLM tier compliance

- **Script adaptation** = Pearl_Writer (Claude subagent, Tier 1, operator-present)
- **Unattended batch render step** = Tier 2 acceptable
- **Banned** = DashScope, ElevenLabs unattended, OpenAI

Per `CLAUDE.md` "LLM Tier Policy" section.

## §10. Render path

- **Manga panels / stills:** Pearl Star ComfyUI (Path A canonical per `docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md`). Animatable stills compose into 30s.
- **Motion / video assembly:** `scripts/video/` pipeline via `run_render.py`. A new render preset `teacher_30s_vertical_v1` may be needed under `config/video/render_params.yaml` — flagged as Pearl_Dev follow-up PR (see §13c). NOT added in this scoping cap.
- **Audio mux:** ffmpeg LUFS-normalized to **-14 LUFS / -1.0 dBTP** for short-form social (overrides the -16 LUFS audiobook default in `render_params.yaml`).

## §11. Anti-drift (binding constraints)

1. **No new teacher banks.** This program does NOT generate the 25 manga-only brand teachers (Path X axis per `docs/PEARL_ARCHITECT_STATE.md`).
2. **No new `character_design` instances.** Viewing mode on existing identity, not a new identity.
3. **No DashScope, no paid TTS, no banned APIs** unattended.
4. **No verbatim-reuse of audiobook prose.** Meaning-matched only (avoids displacive copyright in social/video context).
5. **No teacher in a locale they don't natively occupy** per the locked matrix.
6. **30s is the cap.** If script can't fit, Pearl_Localization compresses meaning, not pace.
7. **Style-spread is for range demonstration**, not a license to abandon teacher visual DNA. Wardrobe/setting/lighting can shift; the 12 individuation axes cannot.

## §12. Budget (Tier 2 unattended — free)

| Resource | Estimate |
|---|---|
| Pearl Star GPU time | ~30–60 min/teacher for stills + animation; ~6–12h total for 12 |
| CosyVoice2 inference | ~5min/teacher; ~1h total |
| ffmpeg mux | trivial |
| Operator review | ~10min/teacher × 12 = 2h |
| **Paid spend** | **0** |

## §13. Action items (with owner + handoff prompt seed)

| # | Owner | Task | Handoff prompt seed |
|---|---|---|---|
| a | Pearl_Localization | Derive 12 (or 13 incl. adi_da if Q1=include) locale-correct 30s scripts from existing audiobook prose. | "Read each teacher's `<teacher>_*_ch1.txt`; emit YAML at `artifacts/video/teacher_30s_v1/<teacher>/script_<locale>.yaml` with hook (0-6s) / struggle (6-22s) / release (22-30s) blocks; meaning-match the chapter-1 climax; respect the locale word/mora/hanzi count budget in §3." |
| b | Pearl_Editor | Confirm style-spread assignment per teacher matches teacher voice + brand demographic. | "Read the matrix TSV; for each row, confirm or flag the proposed style mode; surface any teacher whose voice would feel false in the proposed style; keep the 6/3/2/1 distribution intact." |
| c | Pearl_Dev | Propose `teacher_30s_vertical_v1` render preset under `config/video/render_params.yaml` in a SEPARATE PR (not this cap PR). | "Add a render preset that targets 9:16 / 30s / 30fps / -14 LUFS / -1.0 dBTP; reuse existing xfade and noise params; add a manga-panel-step transition mode if not present; do not modify the `short` format envelope in `format_specs.yaml`." |
| d | Pearl_Int | Confirm CosyVoice2 reference-voice availability per teacher on Pearl Star; flag any missing reference clips. | "SSH to Pearl Star (`pearl_star` alias); list `~/CosyVoice2/voices/<teacher>/` for each teacher in the matrix; flag any missing; propose nearest-locale stock voice fallback." |
| e | Pearl_Video | Pilot render: pick ONE teacher (recommended **joshin / cognitive_clarity** since brand-2 manga assets and ja-JP TTS are furthest along) for V1 pilot before fanning out to 12. | "Render the pilot per the matrix row for joshin; use the script Pearl_Localization produces; confirm 30s exact, 1080×1920, FLUX-quality stills, no displacive verbatim quote; surface artifact for operator review before fanning out." |
| f | Pearl_Architect (next-turn amendment) | Once style spread + adi_da inclusion + pilot teacher + locale overrides approved by operator (Q1–Q4), ratify final matrix into TEACHER-MANGA-30S-VIDEO-V1-01 amendment cap. | (this session's follow-up turn) |

## §14. Status lifecycle

- **proposed** — current state. This spec + cap entry + matrix exist; no work fanned out.
- **active** — after operator answers Q1–Q4 in §16; Pearl_Architect ratifies amendment; multi-parallel implementation prompts issued.
- **shipped_v1** — 12 (or 13) videos rendered, operator-approved, dropped to social platforms per `video_cadence.yaml`.

## §15. Discrepancies surfaced during scoping

The cross-check in step 4 of the scoping plan revealed three discrepancies that must be resolved before any render:

| ID | Discrepancy | Disposition |
|---|---|---|
| **D1** | `qi_foundation` brand (master_feung's binding) is **not present** in `config/manga/canonical_brand_list.yaml`. It IS present in `config/manga/brand_lora_plans.yaml.brand_suffixes` (suffix = `qf`). Demographic unconfirmed. | Propose demographic = `seinen-cultivation` for matrix purposes; flag for Pearl_Architect cap-entry follow-up to either add qi_foundation to canonical_brand_list or formally retire it. Does NOT block scoping. |
| **D2** | **maat audiobook prose anchor is missing.** No `maat_*_ch1.txt` exists under `artifacts/audiobook_samples/_prose/`. All 11 other (matrix-listed) teachers have an anchor. | Pearl_Writer prereq before Pearl_Localization can derive maat's 30s script. Until prose lands, maat's row in the matrix is **blocked**. Recommendation: Pearl_Writer authors `maat_boundaries_ch1.txt` (or operator-chosen topic) ASAP; otherwise drop maat from V1 and revisit in V1.1. |
| **D3** | adi_da has audiobook prose (`adi_da_self_worth_ch1.txt`) and operator-stated locale (zh-TW) but **no manga brand binding** in operator's 12-list, **no entry** in `brand_lora_plans.character_loras`, and **no entry** in `brand_suffixes`. | Operator decision Q1 in §16. Three paths: (a) include as 13th deliverable + author character_design + assign brand; (b) defer pending brand assignment; (c) skip. Do NOT silently drop. |

## §16. Operator-gated questions (must be answered before fan-out)

> The next router turn is blocked on these four answers. Pearl_Architect issues amendment + multi-parallel implementation prompts the moment they land.

### Q1 — adi_da inclusion

Three operator paths:

- **(a) Include adi_da as 13th deliverable.** Requires Pearl_Architect cap-entry amendment to add adi_da to `brand_lora_plans.character_loras` + assign a manga brand (operator chooses, or Pearl_Architect proposes). Adds ~1h GPU + ~5min TTS budget. zh-TW locale per operator's matrix.
- **(b) Defer.** adi_da has audiobook + voice but is unbound to manga; address in V1.1 once brand assignment lands. V1 ships at 12 teachers.
- **(c) Skip.** Drop adi_da from teacher × manga program entirely. V1 ships at 12 teachers.

**Pearl_Architect default if no answer:** (b) defer. Adi_da's audiobook content stands; just no manga-bound video in V1.

### Q2 — Style-spread assignment

Approve the proposed 6/3/2/1 distribution and per-teacher assignment in §6 + matrix TSV as-is, OR request specific changes. Per-teacher rationale is in the matrix `rationale` column.

**Pearl_Architect default if no answer:** approve as proposed.

### Q3 — Pilot teacher for V1

Recommended **joshin / cognitive_clarity** since brand-2 manga assets and ja-JP TTS are furthest along (per operator preamble). Confirm or override.

**Pearl_Architect default if no answer:** joshin / cognitive_clarity.

### Q4 — en-US default override

Any teacher whose en-US default in §7 should be overridden to a different native locale per `pen_name_teacher_profiles.yaml`? The 6 en-US-defaulted teachers are ahjan, pamela_fellows, master_sha, maat, ra, sai_ma. Operator confirms or names overrides.

**Pearl_Architect default if no answer:** all 6 stay en-US.

---

## §17. Out of scope (this PR)

- Any render. Any video file. Any audio file.
- Any code change to `phoenix_v4/`, `scripts/`, `config/video/*` params (cap entry first; param edits land later under their own PR per §13c).
- Any LoRA training, any new `character_design` YAML.
- Modifying existing cap entries.
- Q1–Q4 decisions (operator).
- Discrepancy D1 (qi_foundation canonical_brand_list reconciliation) — separate Pearl_Architect cap follow-up.
- Discrepancy D2 (maat audiobook prose authoring) — separate Pearl_Writer task; gates maat row only.

## §18. References

- `docs/PEARL_ARCHITECT_STATE.md` — cap entry TEACHER-MANGA-30S-VIDEO-V1-01
- `artifacts/qa/teacher_manga_30s_locale_brand_matrix_2026-05-08.tsv` — companion matrix
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` — PRJ-TEACHER-MANGA-30S-VIDEO-V1
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — three workstream rows: ws_teacher30s_scope_ratified, ws_teacher30s_script_derivation, ws_teacher30s_render_pilot
- `config/video/format_specs.yaml` — `short` format envelope (the existing 9:16 / 30s slot this V1 lands in)
- `config/manga/brand_lora_plans.yaml` — verified teacher↔brand binding via `brand_suffixes` and `character_loras`
- `config/localization/locale_registry.yaml` — locale code authority
- `docs/PEARL_STAR_IMAGE_GENERATION_PROTOCOL.md` — render path canon (Pearl Star Tailscale URL, flux1-schnell-fp8, two-stage pattern)
- `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` — 12-axis identity discipline

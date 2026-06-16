# Music Onboarding Song-Kit — V1 spec

**Status:** proposed (Phase-1 governance + spec doc only; NO implementation code in this PR — a
Phase-2 workstream BUILDS the generator engine; this spec DESCRIBES it).
**Cap entry (governing):** `MUSIC-ONBOARDING-SONG-KIT-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`.
**Layers atop (ACTIVE):** `MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS` (music-mode V2).
**Date:** 2026-06-12.

---

## §1. Purpose + delta from V2

### 1.1 Purpose

Music-mode V1/V2 give a musician a brand (brands 38+), a survey, a 6-pool atom bank, an injection
overlay, a brand registry, freebie templates, and diversity gates. What it does **not** give is a
**survey → generator engine**: today the 6 slot-pool atoms (`LYRIC_OPENING`/`LYRIC_CLOSING`/
`LYRIC_BESTSELLER_BEAT` + `MUSIC_REFLECTION_OPENING`/`CLOSING`/`BESTSELLER_BEAT`) are **hand-authored**
per musician by Pearl_Editor/Pearl_Writer (see `SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/`).
There is no survey→lyrics engine and no survey→mood-instruction engine. The "Song-Kit" is the
**onboarding deliverable** that closes that gap: a documented, tier-compliant flow that turns a
completed `musician_reflections_survey` into a first **kit** of draft atoms (lyric atoms on the
with-lyrics fork; MusicGen mood-instruction text on the no-lyrics fork), grouped by an 8-family
topic taxonomy, with **Ahjan as the zeroth/reference kit**.

### 1.2 What already EXISTS on `origin/main` (REUSED, not rebuilt)

| Existing artifact | Role | Song-Kit reuse |
|---|---|---|
| `artifacts/musician_survey/SURVEY_TEMPLATE.yaml` | Survey schema; **already** has `output_preferences_with_lyrics` vs `output_preferences_no_lyrics` fork | Consumed verbatim as the engine input contract (§3). |
| `phoenix_v4/musician/survey_derivation.py` | Survey → `profile.yaml` / `themes.yaml` / `voice_profile.yaml` | Consumed as the engine's upstream; song-kit reads these derived dicts (§3.1). |
| 6 slot-pool atom taxonomy + 2P templates (`INTRO_2P_TEMPLATE.yaml`, `CONCLUSION_2P_TEMPLATE.yaml`) | Atom structure per `MUSIC-MODE-V1-01` | Generator emits INTO these pools; pool structure unchanged (§3.3). |
| `phoenix_v4/planning/music_overlay.py` | Injection planner (`plan_music_injection`) | Unchanged; it consumes the pools the generator fills (§3.4). |
| `config/music/music_brand_registry.yaml` | SSOT for music-mode brands (38+) | Ahjan kit registers here as `ahjan_music` (§4). |
| `funnel/music_mode/templates/m1..m5` | Music freebie templates (`companion_track_download_v1` … `behind_the_song_interview_v1`) | YouTube bridge reuses verbatim as gate targets (§5). |
| Diversity gate spec G1–G8 (`MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES`) | Anti-spam batch gate | Generator output gated by the SAME G1–G8; song-kit authors NO parallel gate (§3.5, §6). |
| `config/source_of_truth/canonical_topics.yaml` | Canonical `topic_ids` SSOT | 8 families map onto these as additive labels; grid untouched (§2). |

### 1.3 Delta from V2 (what V2 does NOT cover and this spec adds)

1. **The survey→generator engine itself.** V2 §4 (Phase A launch gate) assumes atoms are *authored*;
   it does not specify an engine that *drafts* them from the survey. Song-Kit V1 specifies that
   engine's contract, tiering, and gates (Phase-2 build target).
2. **An 8-family topic taxonomy** (§2) as an additive grouping over canonical topics — a routing aid
   for the generator and for kit packaging. V2 works at the persona×topic cell granularity; families
   are a coarser, musician-facing grouping that sits *beside* the cells, not replacing them.
3. **YouTube → freebie wiring** (§5) as spec + config schema only — net-new; not in any prior cap.
4. **Ahjan first/reference kit** (§4) — a zeroth `musician_banks/ahjan/` seeded from the existing
   `teacher_banks/ahjan/` corpus, distinct from V2's open `Q-MM-V2-FIRST-REAL-MUSICIAN-01`
   (operator-nominated). See `Q-MSK-AHJAN-VS-V2-FIRST-01` (§7) — these do NOT collapse silently.

### 1.4 Non-goals (V1)

- NO audio rendering in V1. The no-lyrics fork emits MusicGen mood-instruction **TEXT** only; WAV
  render stays Phase-B-gated per `MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS` §6 (MusicGen on
  Pearl Star, `PEARL-STAR-JOB-QUEUE-V1-01` dependency, not yet on main).
- NO YouTube API upload in V1 (§5 is schema + config only; upload deferred to a Pearl_Marketing/
  Pearl_Int ws after credential verification).
- NO new freebie types (those are `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`).
- NO edit to the en-US persona×topic grid, `canonical_brand_list.yaml`, `topic_registry.yaml`, or any
  catalog SSOT.
- NO generator/engine/resolver code in this PR (Phase 2 builds it).

---

## §2. The 8-family topic taxonomy

The SSOT for the families is **`config/music/song_kit_topic_families.yaml`** (authored under this cap).
Each family is a curated grouping LABEL over canonical `topic_ids` from
`config/source_of_truth/canonical_topics.yaml`. Families are **additive** — they add labels mapped
onto existing therapeutic topic anchors; they do **NOT** mint new topic_ids and do **NOT** touch the
en-US persona×topic grid or `canonical_brand_list.yaml`.

| family_id | display | topic_anchors (⊂ canonical_topics) |
|---|---|---|
| `recovery_and_repair` | Recovery & Repair | burnout, compassion_fatigue, addiction |
| `quiet_courage` | Quiet Courage | courage, boundaries |
| `presence_and_stillness` | Presence & Stillness | overthinking, sleep_anxiety |
| `anxiety_and_overwhelm` | Anxiety & Overwhelm | anxiety, social_anxiety, relationship_anxiety |
| `grief_and_letting_go` | Grief & Letting Go | grief, divorce |
| `self_worth_and_shame` | Self-Worth & Shame | self_worth, shame, body_image, imposter_syndrome |
| `connection_and_belonging` | Connection & Belonging | relationship_anxiety, social_anxiety |
| `hope_and_renewal` | Hope & Renewal | depression |

Each family additionally carries `default_themes`, a `lyric_register_hint` (with-lyrics fork
guidance), and an `instrumental_mood_hint` (no-lyrics MusicGen mood-instruction guidance). See the
YAML for full per-family fields.

**Mapping integrity (enforced by the YAML's own note + the Phase-2 generator's load-time check):**
every `topic_anchors` value MUST be present in `canonical_topics.yaml` `topic_ids`. Some canonical
topics are intentionally unmapped in V1 (`financial_anxiety`, `money`, `adhd`) — they remain valid
catalog topics; song-kit V1 simply does not group them. A topic may belong to more than one family
(e.g. `relationship_anxiety` seeds both `anxiety_and_overwhelm` and `connection_and_belonging`); the
generator disambiguates from the musician's surveyed `themes.primary_themes` intent.

---

## §3. Survey → generator flow

This section DESCRIBES the engine. A Phase-2 workstream BUILDS it (`ws_..._song_kit_generator_*` +
`ws_..._lyric_mood_engine_*`). No engine code is authored here.

### 3.1 Inputs (consumed, not rebuilt)

1. A completed survey conforming to `artifacts/musician_survey/SURVEY_TEMPLATE.yaml`. The fork is
   **already** in the schema: `output_preferences_with_lyrics` (lyric_form / explicit_content_ok /
   companion_ai_song_consent) vs `output_preferences_no_lyrics` (reflection_form /
   reflection_perspective). Song-Kit V1 reuses these blocks **verbatim** — it does NOT add survey
   fields.
2. The derived dicts from `phoenix_v4/musician/survey_derivation.py`:
   `survey_to_profile_dict()` (display_name, primary_genre, themes, listener_hope_one, touchstones,
   healing_intent_summary), `survey_to_themes_yaml()` (primary_themes, avoided_themes), and
   `survey_to_voice_yaml()` (voice_person, register, pacing, signature_devices). The generator
   consumes these as its conditioning context — it does NOT re-parse the raw survey.
3. The family mapping from `config/music/song_kit_topic_families.yaml` (§2): the musician's
   `themes.primary_themes` map onto one or more `family_id`s, and the matched family supplies
   `lyric_register_hint` / `instrumental_mood_hint` / `default_themes` as drafting guidance.

### 3.2 Fork selection

The fork is driven by the survey's presence of `output_preferences_with_lyrics` vs
`output_preferences_no_lyrics` (a musician may consent to both — `companion_ai_song_consent` gates
the lyrical branch). The generator runs the matching branch(es):

- **with-lyrics → lyric atoms.** Drafts content for `LYRIC_OPENING`, `LYRIC_CLOSING`,
  `LYRIC_BESTSELLER_BEAT` (plus the paired `MUSIC_REFLECTION_*` pools), honoring
  `voice_profile.yaml` (register/pacing/voice_person) + the family `lyric_register_hint` +
  `output_preferences_with_lyrics.lyric_form` (free_verse / rhymed / verse_chorus).
- **no-lyrics → mood-instruction atoms.** Drafts MusicGen **mood-instruction TEXT** for the
  `MUSIC_REFLECTION_*` pools (and a per-book companion-song mood-instruction string), honoring the
  family `instrumental_mood_hint` + `output_preferences_no_lyrics.reflection_form` /
  `reflection_perspective`. **No audio is rendered in V1** — text only; WAV render is Phase-B-gated
  (§1.4).

### 3.3 Output target (atoms; structure unchanged)

The generator emits draft atoms into the EXISTING 6-pool structure under
`SOURCE_OF_TRUTH/musician_banks/<musician_id>/approved_atoms/<SLOT_POOL>/<atom_id>.yaml`, matching the
on-main atom shape (`atom_id` + `variants:` list of `{body: ...}`; see
`test_artist_alpha/.../LYRIC_OPENING/lo_01.yaml`). Atoms use the established template variables
(`{{musician_name}}`, `{{topic_anchor}}`, `{{theme}}`, `{{genre}}`, `{{persona_anchor}}`). The
generator does **NOT** invent new pools, new atom schema, or new template vars. The 2P templates
(`INTRO_2P_TEMPLATE.yaml`, `CONCLUSION_2P_TEMPLATE.yaml`) are reused as-is.

**Drafts are PROPOSED, human-reviewed.** Generator output is a *draft kit* that Pearl_Editor reviews
and promotes (Tier-1, operator-present per CLAUDE.md). The engine does not silently ship atoms to a
catalog run.

### 3.4 Downstream (unchanged)

Once a pool is filled, `phoenix_v4/planning/music_overlay.py` `plan_music_injection()` consumes it
exactly as today (opening / bestseller_beat / closing injection points per chapter, per
with-lyrics/no-lyrics mode). The generator changes WHO authors the pool content (engine-drafted +
human-reviewed vs hand-authored), not HOW it is injected.

### 3.5 Gating to SPEC-739 (≥3 variants/pool)

A kit is **complete for a cell** only when every targeted slot pool has **≥3 atom variants**, per the
`SPEC-739-THRESHOLD-01` floor (3 = floor; 5 = optional ceiling). This matches the V2 backfill ws
(`ws_pearl_editor_music_slot_pools_priority_backfill_20260611`, which targets ≥3 atoms × 6 pools).
The generator's "done" signal for a cell is the SPEC-739 floor; it does NOT lower or fork that
threshold. Diversity across those ≥3 variants is checked by the existing G1–G8 gate (§3.6), not by a
new song-kit gate.

### 3.6 Diversity = reuse G1–G8 (no parallel gate)

Generated atoms feed the **existing** anti-spam diversity gate specified by
`MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES` (G1–G5 HARD_FAIL under production
profile, G6–G8 WARN), whose CI guard `scripts/ci/check_music_brand_diversity.py` is the Phase-2 build
under `ws_pearl_dev_music_brand_diversity_ci_guard_20260611` (NOT yet on main as of this spec — the
gate **spec** is ratified; the script is a build target). Song-Kit authors **no** parallel diversity
gate; it routes generator output through the ratified G1–G8 envelope. (Anti-drift: reuse-not-
greenfield.)

---

## §4. Ahjan first / reference kit

### 4.1 What it is

Ahjan is the **zeroth / reference** song-kit: `brand_id` = `ahjan_music`, bank at
`SOURCE_OF_TRUTH/musician_banks/ahjan/`, registered as a music-mode brand (38+) in
`config/music/music_brand_registry.yaml` with a `survey_yaml_pointer` to a persisted Ahjan survey.
It is the SOURCE_OF_TRUTH exemplar that demonstrates the full survey→generator→6-pool flow end to end,
and the gold reference future musician kits are measured against.

### 4.2 Seed source (REUSE the existing corpus)

The Ahjan reference kit is **seeded from the existing `SOURCE_OF_TRUTH/teacher_banks/ahjan/` corpus**
(Ahjan already exists as a teacher with `approved_atoms/COMPRESSION/`, `TEACHER_DOCTRINE/`, a README,
and is the 13-teacher roster anchor per the known-good-anchors registry). The kit's profile/themes/
voice derive from an Ahjan survey response (authored under the Ahjan first-kit ws), and the generator
drafts the 6 music slot pools. This is reuse-not-greenfield: Ahjan's voice already has a documented
corpus; the music kit extends it into the music_mode bank shape, it does not invent a new persona.

### 4.3 Relationship to V2's open "first real musician" question

`Q-MSK-AHJAN-VS-V2-FIRST-01` (FLAGGED — operator-only): Ahjan as the **reference/zeroth** kit does
**NOT** silently override V2's open `Q-MM-V2-FIRST-REAL-MUSICIAN-01` (operator-nominated first *real*
external musician). The two are distinct roles: Ahjan = internal gold reference / exemplar seeded from
the operator's own teaching corpus; the V2 question = which external musician is onboarded first for
the production Phase-A launch gate. This spec leaves `Q-MM-V2-FIRST-REAL-MUSICIAN-01` open for the
operator to collapse; it does not answer it.

---

## §5. YouTube → freebie bridge (spec + config only)

### 5.1 What V1 ships

A **path-reserved config schema** at `config/music/youtube_freebie_bridge.yaml` (authored under this
cap) that maps a YouTube `video_id` → an email-gate → an existing music-mode freebie template
(`funnel/music_mode/templates/m1..m5`). V1 ships the **schema + one commented example with no real
video ids**. The file's `bridge_entries:` list is **empty** in V1.

### 5.2 What V1 does NOT ship

- NO YouTube Data API upload/poll code. The actual YT publish path is **deferred** to a
  Pearl_Marketing/Pearl_Int workstream (`ws_..._freebie_youtube_wiring_*`, proposed).
- NO credential assumptions. The bridge references `docs/INTEGRATION_CREDENTIALS_REGISTRY.md §13`
  (YouTube; per-brand `YT_CLIENT_ID_SP/CC/ND`, `YT_CLIENT_SECRET_*`, `YT_REFRESH_TOKEN_*`, consumed by
  `scripts/video/uploaders/youtube.py`). As of the registry snapshot those creds are documented but
  marked **"Missing — credentials not yet provisioned"** for at least some brands. The Phase-2 ws
  **MUST verify creds in the registry (and provision if missing) BEFORE any wiring** — do not assume.

### 5.3 Bridge contract (reuse, not new freebies)

- `freebie_template_id` MUST be one of the existing m1..m5 `template_id`s:
  `companion_track_download_v1`, `preview_clip_30s_v1`, `sample_ep_bundle_v1`, `lyric_poster_pdf_v1`,
  `behind_the_song_interview_v1`. The bridge does NOT author new freebie types (that is
  `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`).
- `email_gate.capture_step` = `email_capture_before_download_link`, mirroring the m1..m5 `gating_step`.
- `brand_id` MUST resolve to a music-mode brand in `music_brand_registry.yaml` (38+); NO Path X 37.
- `landing_route` is server-relative — **NO `file://` URLs** (same rule as the registry's
  `survey_yaml_pointer` convention).
- No secrets in the file; OAuth lives only in env vars loaded from Keychain at runtime.

### 5.4 Why this lives in song-kit (not in the freebie cap)

The freebie *types* are `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`. The YouTube→freebie *bridge* is the
**acquisition wiring** that points a song's YouTube presence at those freebies — it is the
onboarding-kit's distribution surface (a musician onboarded via the song-kit gets a YT→freebie route
provisioned). It reuses the freebie templates verbatim and adds only the mapping layer.

---

## §6. Tier-2 compliance (LLM policy)

Per CLAUDE.md LLM Tier Policy + `.github/workflows/llm-policy-enforcement.yml`:

1. **English lyrics + reflections (PRIMARY): Claude subagents (Pearl_Writer), Tier 1**
   (operator-present, human-reviewed). This is consistent with the auto-memory note
   `feedback_qwen_vs_pearl_writer` (English prose = Pearl_Writer = Claude subagents; Qwen is CJK6-only)
   and with the V2 backfill ws's "LLM Tier 1 only (Claude subagents)" instruction.
2. **CJK6 lyrics/reflections: Qwen** (Pearl Star via Ollama) — CJK6 register only.
3. **Unattended / scheduled fallback: Gemma (English) / Qwen (CJK6) on Pearl Star via Ollama** — for
   any pipeline step firing with no operator present (free, unattended tier).
4. **No paid LLM APIs anywhere** — no `ANTHROPIC_API_KEY`/`CLAUDE_API_KEY` reads in repo code; no
   OpenAI/Google AI/DashScope cloud/Together/Replicate/Perplexity/Cohere/Mistral-paid. The generator
   engine (Phase-2 build) MUST pass `python3 scripts/ci/audit_llm_callers.py`.
5. **MusicGen** (no-lyrics audio, Phase-B-gated) is a local Pearl Star workload, not a paid API; V1
   emits mood-instruction TEXT only and renders no audio (§1.4).

---

## §7. Open questions (Q-MSK)

Defaults are recommended (the cap is **proposed** because it needs a Phase-2 build + operator
ratification). The flagged question is operator-only.

| ID | Question | Recommended default |
|---|---|---|
| `Q-MSK-FAMILIES-01` | Accept the 8 topic families + their canonical-topic mappings (§2)? | **Yes** — 8 families as in `song_kit_topic_families.yaml`; additive labels over canonical topics; grid untouched. |
| `Q-MSK-ENGINE-TIER-01` | Engine tier for English lyrics/reflections? | **Claude subagents (Pearl_Writer) PRIMARY**, Tier 1; Qwen CJK6-only; Gemma-Ollama unattended fallback (§6). |
| `Q-MSK-FORK-REUSE-01` | Reuse the existing survey lyrical/instrumental fork verbatim, or extend the survey? | **Reuse verbatim** — `output_preferences_with_lyrics` / `output_preferences_no_lyrics` are already in `SURVEY_TEMPLATE.yaml`; no new survey fields in V1. |
| `Q-MSK-INSTRUMENTAL-OUTPUT-01` | No-lyrics branch output in V1? | **MusicGen mood-instruction TEXT only**; WAV render Phase-B-gated (`MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS` §6 + `PEARL-STAR-JOB-QUEUE-V1-01`). |
| `Q-MSK-YT-SCOPE-01` | YouTube→freebie scope in V1? | **Spec + config schema only**; YT API upload deferred to Pearl_Marketing/Pearl_Int ws; verify creds in `INTEGRATION_CREDENTIALS_REGISTRY.md §13` before wiring (§5). |
| `Q-MSK-DIVERSITY-01` | New diversity gate for song-kit, or reuse G1–G8? | **Reuse the ratified G1–G8** (`...AMENDMENT-DIVERSITY-GATES`); author NO parallel gate (§3.6). |
| `Q-MSK-VARIANTS-FLOOR-01` | Kit "complete" threshold per pool? | **≥3 variants/pool** per `SPEC-739-THRESHOLD-01` floor (5 optional ceiling) (§3.5). |
| **`Q-MSK-AHJAN-VS-V2-FIRST-01`** (**FLAGGED — operator-only**) | Does Ahjan-as-reference-kit collapse V2's open `Q-MM-V2-FIRST-REAL-MUSICIAN-01`? | **No (do NOT collapse silently).** Ahjan = zeroth/reference kit seeded from `teacher_banks/ahjan/` (`brand_id ahjan_music`); the operator-nominated first *real* external musician stays an open V2 question for the operator to collapse (§4.3). |

---

## §8. Cross-references

- **Rendering / atom bank:** `MUSIC-MODE-V1-01` (musician_banks/, 6 slot pools, 2P templates, survey
  template) — the generator emits into this structure unchanged.
- **Brand identity / catalog:** `MUSIC-MODE-BRAND-INTEGRATION-V1-01` (+ AMENDMENT-2026-05-09 Q1–Q4) —
  Ahjan registers as `ahjan_music` in `music_brand_registry.yaml` per Q2 `<handle>_music` slug.
- **Production-readiness layer (ACTIVE):** `MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS` — Phase
  A launch gate (§4), MusicGen Phase B (§6, §1.4), atom-coverage SSOT, the priority-backfill ws this
  generator complements.
- **Diversity gate:** `MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES` (G1–G8) — reused,
  not duplicated (§3.6).
- **Freebie cap:** `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` + `funnel/music_mode/templates/m1..m5` — the
  YouTube bridge (§5) reuses these freebie templates verbatim; new freebie *types* remain that cap's
  scope.
- **Variants floor:** `SPEC-739-THRESHOLD-01` (3 floor / 5 optional ceiling) — kit completion gate
  (§3.5).
- **Canonical topics:** `config/source_of_truth/canonical_topics.yaml` — the families' subset-source
  (§2).
- **Credentials:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md §13` (YouTube) — verify before any YT
  wiring (§5.2).
- **LLM policy:** CLAUDE.md Tier policy + `.github/workflows/llm-policy-enforcement.yml` +
  `scripts/ci/audit_llm_callers.py` (§6).

### Deliverables manifest (this PR — governance/spec/config only; NO code)

1. `docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md` (this file).
2. `config/music/song_kit_topic_families.yaml` (8-family SSOT).
3. `config/music/youtube_freebie_bridge.yaml` (path-reserved schema + 1 commented example).
4. `MUSIC-ONBOARDING-SONG-KIT-V1-01` cap entry (append to `docs/PEARL_ARCHITECT_STATE.md`).
5. 4 child ws rows (proposed) in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.
6. 1 operator-decision-log row in `artifacts/coordination/operator_decisions_log.tsv`.
7. `PRJ-MUSIC-ONBOARDING-SONG-KIT-V1` row in `artifacts/coordination/ACTIVE_PROJECTS.tsv`.

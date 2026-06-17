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

---

## §AMENDMENT-2026-06-13 — Both-Ways Data-Driven Model · Persona Reuse/Composite · First-Person Music Wrapper · Volume→Pearl-Prime · Deliverables Reconciliation

**Status:** **PROPOSED — operator-review-pending.** This amendment corrects the music-mode *model*
(not the engine contract) per operator (Ahjan) direction captured 2026-06-13. It **edits this existing
authority** (no new parallel music spec — anti-reinvention / dogfood the Canonical Artifacts Registry).
It governs the EN/JA/ZH `MUSIC_MODE_INTRODUCTION_DECK` rewrite shipped alongside.

**What it amends / supersedes:**
- **Sharpens** §3.2 of this spec (the with-lyrics / no-lyrics *fork*) into a **data-driven proportional
  mix** (§A1 below).
- **Supersedes** `MUSIC-MODE-V1-01-AMENDMENT-V2-PRODUCTION-READINESS` (#1497) **§2 Row 12 + §7 deck**
  (the `solo / standard / enterprise` `music_volume_tier`) — see §A5. The V2 spec's *other* ratified
  rows are untouched.
- **Resolves** #1497 §2 Row 1 / `Q-MM-V2-CATALOG-800-RECONCILE-01` (the 800-per-brand vs 800-system
  dispute) in favor of the Pearl-Prime "~800 high-confidence configs per brand" reading (§A5).
- **Adds** `music_wrapper` as the sibling of `teacher_wrapper` / `science_wrapper` under
  `BESTSELLER-FIT-PLAN-VOICE-DOCTRINE` (#1527) — see §A4.

**Cap status (IMPORTANT — hot-file discipline).** This amendment does **NOT** append to
`docs/PEARL_ARCHITECT_STATE.md` in this PR. It proposes cap-amendment id
**`MUSIC-ONBOARDING-SONG-KIT-V1-01-AMENDMENT-2026-06-13`** (status = PROPOSED). Ratification (the
hot-file append) is the **gated serial-lane next-action** after operator review — per
`feedback_serial_lane_hot_governance_file`, one writer at a time on the state doc. The spec doc + deck
are parallel-safe; the cap append is not, so it is deliberately deferred.

---

### §A1. Music mode is BOTH-WAYS and DATA-DRIVEN — not an either/or variant choice

**The correction.** §3.2 framed lyric-vs-instrumental as a *fork* the survey selects. That reads as
"pick a variant for the brand." It is not. **A single music brand supports lyric AND instrumental
books simultaneously; the musician's DATA sets the proportional mix.** There is **no separate brand
per variant**, and no operator/musician forced single choice.

**The mechanism (the gated planner builds this; the spec defines it):**

1. **`lyric_ratio` is data-derived and continuous**, not a toggle. The planner computes
   `lyric_ratio ∈ [0.0, 1.0]` from survey signals already in `SURVEY_TEMPLATE.yaml` + the supplied
   material — the **presence and richness of lyric touchstones**, an explicit `lyric_form` preference,
   `companion_ai_song_consent`, and how `themes` are described (word-craft-primary vs sound-primary).
   It is **not** read from a single `music_format` enum.
2. **The mix follows the data, proportionally:**
   - No lyric material in the data → `lyric_ratio = 0.0` → the catalog is **all no-lyrics
     (instrumental-reflection) books**. A purely instrumental musician needs no lyrics and no separate
     brand.
   - Abundant lyric material + word-craft-primary → high `lyric_ratio` → **mostly lyric books**.
   - **Mostly-instrumental musician with a few lyrics** → **low non-zero ratio** → **mostly
     instrumental books + a few lyric ones, inside one brand.** This is the canonical case the old
     framing could not express.
   - `lyric_ratio` is **capped below 1.0** by policy (always retain some reflection books for the
     "came for the feeling, not the words" reader reach per §A1-deck slide 7); the exact ceiling is an
     operator knob (`Q-MMX-LYRIC-CEILING-01`, §A9).
3. **The planner assigns the per-book variant deterministically.** Across the ~800-config catalog
   (§A5), each `(persona × topic × locale × spine)` book is assigned `with-lyrics` or `no-lyrics` by a
   **seeded proportional sampler** keyed to `lyric_ratio` (reproducible; no run-to-run drift). Variant
   is a **per-book** property, not a brand-level flag.
4. **`Music-Format` becomes a DERIVED signal, not a forced field.** In the wizard, "Music-Format"
   stops being a single mutually-exclusive choice and becomes the **computed mix** (e.g.
   `derived: 80% instrumental / 20% lyric`), surfaced read-back for confirmation, overridable by the
   operator but **defaulting to the data**. The survey keeps both `output_preferences_with_lyrics` and
   `output_preferences_no_lyrics` blocks (no schema change); the planner reads richness, not a switch.

**Anti-drift.** No survey field is added or removed (Q-MSK-FORK-REUSE-01 still holds — reuse verbatim).
The 6 slot pools are unchanged. Only the *planner's variant-selection logic* and the *wizard's
Music-Format presentation* change, both in the gated fan-out (§A8).

---

### §A2. Persona: REUSE vs COMPOSITE — accept non-teacher musicians on the composite

Music-mode onboarding creates or reuses a persona. Two paths:

1. **Teacher-with-music (e.g., Ahjan) → REUSE the existing persona.** Already covered by §4.2 (Ahjan
   seeds from `teacher_banks/ahjan/`). The persona, its teachings, and its exercises already exist;
   the music kit only adds the music slots + musical insights. **Do not invent a new persona.**
2. **Non-teacher, music-only → ACCEPT as music mode on the COMPOSITE.** A musician who is not a teacher
   is still a first-class music brand. Their **music slots + musical insights are theirs**; their
   book's **non-musical teachings + exercises draw from the Pearl Prime composite** —
   `SOURCE_OF_TRUTH/composite_doctrine/` (the 15-topic all-teachers synthesis: anxiety, grief,
   burnout, self_worth, …). They do **not** need to be a teacher to ship a music-mode catalog; the
   composite supplies the doctrinal substance, the musician supplies the sound.

This reconciles #1497 §2 **Row 7** ("no 25/50/25 named/influence/composite split for music — teacher
convention only"): music-mode teachings are **either** the teacher's own bank (path 1) **or** 100%
composite (path 2) — never the teacher-mode 25/50/25 distribution. The operator's deck edit
("**Composite USLF**", slide 15) is this path made explicit.

---

### §A3. Music mode = a regular Pearl Prime ebook + MUSIC SLOTS (the core framing)

A music-mode book is **a normal Pearl Prime ebook with music slots added** — not a "book about the
musician." The **main body (teachings + exercises) is non-musical**: from the composite (non-teacher,
§A2 path 2) or the teacher's own bank (teacher, §A2 path 1). The musician's **music and musical
insights fill the 6 music slot pools** (`LYRIC_*` / `MUSIC_REFLECTION_*`) + the per-book companion
artifact. This is consistent with #1497 §1 Q2 ("books are SHAPED BY the musician but ADDRESSED TO the
reader") — the amendment names the substrate: **a standard ebook the music threads through, not a
music monograph.**

---

### §A4. The MUSIC WRAPPER — first-person default, music-attributed (#1527 sibling) + a Stage-6 lint

**Architecture.** `music_wrapper` is the **sibling of `teacher_wrapper` and `science_wrapper`** under
`BESTSELLER-FIT-PLAN-VOICE-DOCTRINE` (#1527): there is **one author voice** (pen-name or EI author);
the author **REFERENCES the music and ATTRIBUTES the source**; the author **never speaks AS the
musician**. The same named/generalized structure as
`config/catalog_planning/teacher_wrapper_templates.yaml` applies, with music-specific slots.

**Two hard requirements for every music slot:**
- **Attribution** — the prose explicitly refers to the music and names the source ("from Ahjan's
  music", "one of Ahjan's songs").
- **Truth** — it names a **true structure** of the music (instrument / chord / melody / form) **and a
  true benefit**, applied to the book's topic. No invented musical claims.

**Voice default = FIRST PERSON (author voice) + first-person wrapper, for NEW prose:**
- **Lyrical:** `"Let me share a verse from one of Ahjan's songs:"` → `[lyric block]` → a short
  first-person reflection in the author's voice.
- **Instrumental:** e.g. `"Om. From Ahjan's music — on his guitar, a chord and an uplifting melody.
  This small act of lifting the spirit through music speaks to me as we sit with {topic}."` — a SHORT
  reflection naming a true structure + true benefit, applied to `{topic}`.

**The 1P/2P rule (both are correct, done right):**
- If a music slot's prose was **already authored in second person** → **KEEP it** and add a
  **second-person** wrapper (still music-attributed).
- If the prose is **not yet authored** → author it **first person + first-person wrapper** (the
  default).
- Both 1P and 2P books are valid. The book's `INTRO_2P_TEMPLATE` / `CONCLUSION_2P_TEMPLATE` framings
  are unchanged; this rule governs the **music slot wrappers**, which default to 1P.

The current deck slide-8 example ("You hear the morning…") was **too ambiguous** — it did not
attribute the music. Corrected on the deck with one 1P and one 2P **music-attributed** example.

**Stage-6 music-attribution + voice lint (NEW, gated build).** At Stage 6 of the §3 flow (review →
active), before any music slot atom is promoted, a lint asserts: (a) the slot **names/attributes the
music** (source-reference present), (b) it names a **true structure + true benefit**, (c) the **voice
is author-attributed, not musician-impersonation**, and (d) voice person is **1P for new prose / kept
2P only where pre-existing**. This lint is a **sibling to the G1–G8 diversity gates** (it checks voice
+ attribution, not slot-diversity) and is HARD under `--quality-profile production`. It is authored in
the gated fan-out (§A8), not here.

---

### §A5. Volume FOLLOWS Pearl Prime (~800 high-confidence configs) + per-platform ROLLOUT — kill the tiers

**Supersede.** `solo / standard / enterprise` and the `music_volume_tier` survey-field semantics
(#1497 §2 Row 12, §7) are **retired.** "`<800 / 800 / >800`" is meaningless: **every brand targets
~800** — the Pearl Prime / Path X standard. Music mode is not special here.

- **~800 = high-confidence configs per brand**, not "books per brand" as a tier choice:
  `brand primary topic × primary persona × proven format × top-5 locales` ≈ **800 market-validated
  configs** — the $-makers (`artifacts/research/full_content_audit.md:65`). Medium (~2,500) and low
  (~3,000) confidence tiers exist below it but are not the headline. This **resolves #1497 §2 Row 1 /
  `Q-MM-V2-CATALOG-800-RECONCILE-01`**: ~800 high-confidence configs is **per active brand**; it does
  not contradict the system-wide framing because it is the *high-confidence* slice, not a raw total.

- **The real volume strategy is the per-platform ROLLOUT**, grounded in `#1574`
  (`artifacts/research/duration_per_platform_20260613/DURATION_PER_PLATFORM_PLAN.md`), the
  marketing ladder (`artifacts/qa/duration_marketing_targets_20260613/`), and the 800-config research:
  - **Only T7 "Complete" (~52k words / ~5.8 hr / ~208 pp) wins the flagship $-maker surfaces — full
    KDP ebook + Audible + Spotify audiobook — simultaneously.** T6 (~30k) is an entry full-audiobook.
  - **T1–T5 are funnel, not standalone books:** KDP Short Reads, podcast episodes/seasons, free
    AI-narration samples, social. Mis-routed when sold as books; excellent as the on-ramp.
  - **Rollout sequence:** flagship first (T7 → KDP + Audible), then funnel tiers fan out across
    podcast / short-read / social / AI-sample. CJK length targets are **provisional** (ja anchored at
    300 文字/分; zh/ko gate on a measured Pearl Star render — see `project_duration_per_platform`).

The operator's deck edit "**Standard 800 book catalog**" (slide 11) stays. Deck slide 10 is rebuilt
from the three volume tiers into this per-platform rollout story.

---

### §A6. Behind-the-Song = PODCAST **and** PDF (both deliverables)

Freebie **M5** (`behind_the_song_interview_v1`) is **both a podcast episode AND a companion PDF** — the
deeper view of the song — not "audio **or** long-form text." The operator's "**Podcasts:**" prefix
(slide 13) is ratified; the deck body is corrected to "a podcast episode and a companion PDF." The
reader-facing deliverable set is **book + podcast + PDF** (see §A7).

---

### §A7. We do NOT distribute the musician's music as files (no MP3 / zip)

**The correction.** We do **not** hand out the musician's music as downloadable files. The music
**lives on the musician's own channels** (YouTube / streaming); each book points readers **there**
(outbound), and those channels point readers back to the books (inbound). Reader-facing **deliverables
are the book, the podcast, and the PDF** — never the music as a file.

**Reframes required (deck + freebie funnel):**
- **M1** (`companion_track_download_v1`) — was "full-quality companion song **download**." Reframed to
  a **pointer to the music on the musician's channels** (email-gated for the *book* funnel, not the
  music file). The relationship opener is a *link to where the music already lives*, not a file
  hand-out.
- **M3** (operator already edited) — **YouTube & TikTok**: inbound book sales + outbound links in each
  book to the music. The model-correct form of the old "Sample EP zip." (§A8 wires this as the
  `youtube_freebie_bridge`.)
- **"Companion song packaged/bundled with each release"** language (deck slides 2 / 3 / 11 / 12 / 14)
  is reframed: the book is the deliverable; the music stays on the channels.

**AI companion-song / MusicGen decision — FLAGGED (`Q-MMX-COMPANION-SONG-FATE-01`, §A9).** The AI
companion song is a *different* artifact from the musician's real music (a MusicGen-generated track,
Phase-B-gated, prompt-only in V1). Under "no music files," even an AI track is a file.
**Recommendation:** **de-emphasize the AI companion song as a reader-facing deliverable** — keep the
per-book MusicGen **prompt** as an **internal / optional brand-admin artifact** (unchanged from
`MUSIC-MODE-V1-01` line 767, prompt-JSON only; WAV render stays Phase-B-gated), and **drop the
"packaged with each release" reader-facing claim** from the funnel. This touches
`MUSIC-MODE-FREEBIE-FUNNEL-V1-02`; operator confirms at ratification. The deck adopts the
recommendation (companion-song reframed to internal/optional).

---

### §A8. GATED CODE FAN-OUT (defined here; NOT built this session)

The amendment is spec + deck only. The following implementation lands **after operator ratification**,
each as its own gated ws (golden-branch, Tier-1/Tier-2 compliant, no paid API). Listed so ratification
can dispatch them in order:

1. **Planner variant-mix logic** — `lyric_ratio` derivation (§A1) + the seeded per-book proportional
   sampler in `phoenix_v4/planning/music_overlay.py` (or the catalog planner). Variant becomes per-book
   data-derived; no brand-level flag.
2. **Wizard `Music-Format` → data-derived** — the wizard surfaces the **computed mix** read-back
   (overridable), not a forced single choice. `brand-admin` + `brand-wizard-app` Step-4 change.
3. **Brand-admin** — accept non-teacher music-only brands on the **composite** (§A2 path 2): wire
   `SOURCE_OF_TRUTH/composite_doctrine/` as the teachings/exercises source for music brands without a
   teacher bank.
4. **`music_wrapper` resolver + Stage-6 lint** — `config/catalog_planning/music_wrapper_templates.yaml`
   (sibling of `teacher_wrapper_templates.yaml`; 1P-default, named/generalized, attribution-required) +
   the Stage-6 music-attribution + voice lint (§A4), HARD under production profile.
5. **Freebie-funnel M1 reframe + YouTube/TikTok bridge** — reframe `companion_track_download_v1` to a
   channel pointer (no file); populate `config/music/youtube_freebie_bridge.yaml` (inbound/outbound,
   §5); enact the AI-companion-song decision (§A7) in `MUSIC-MODE-FREEBIE-FUNNEL-V1-02`.
6. **M5 podcast+PDF deliverable** — `behind_the_song_interview_v1` emits both a podcast episode and a
   companion PDF (§A6).

---

### §A9. New open questions (Q-MMX — operator answers at ratification; defaults recommended)

| ID | Question | Recommended default |
|---|---|---|
| `Q-MMX-DATA-MIX-01` | Accept the data-driven `lyric_ratio` proportional mix (§A1), retiring the variant-as-fork framing? | **Yes** — continuous data-derived ratio; planner samples per-book; one brand, no per-variant brands. |
| `Q-MMX-LYRIC-CEILING-01` | Cap on `lyric_ratio` so some reflection books always ship? | **Yes, ceiling ≈ 0.8** (always retain ≥~20% reflection books for non-lyric reader reach); tune post-launch. |
| `Q-MMX-COMPOSITE-NONTEACHER-01` | Non-teacher musicians draw teachings/exercises from `composite_doctrine/` (§A2 path 2)? | **Yes** — 100% composite for non-teachers; teacher-musicians use their own bank; never 25/50/25. |
| `Q-MMX-WRAPPER-1P-01` | `music_wrapper` first-person default + Stage-6 attribution/voice lint (§A4)? | **Yes** — 1P default for new prose; keep-2P only where pre-existing; lint HARD under production. |
| `Q-MMX-VOLUME-SUPERSEDE-01` | Retire `solo/standard/enterprise` + `music_volume_tier`; volume = ~800 high-confidence configs + per-platform rollout (§A5)? | **Yes** — supersede #1497 §2 Row 12 / §7; resolve Row 1 in favor of ~800 high-confidence-configs-per-brand. |
| `Q-MMX-COMPANION-SONG-FATE-01` | AI companion song fate under "no music files" (§A7)? | **De-emphasize as reader deliverable** — keep MusicGen prompt as internal/optional brand-admin artifact; drop "packaged with each release" reader claim. |

---

### §A10. Deck delta governed by this amendment (EN + JA + ZH)

`MUSIC_MODE_INTRODUCTION_DECK` (`artifacts/presentations/music_mode_deck_20260612/`) is corrected in
all three locales, preserving every operator `.pptx` edit and layering corrections §A1–§A7 + the M3
typo fix. Per-slide change log lives in the build script `apply_music_deck_corrections.py` (the
committed SoT) + the session CLOSEOUT_RECEIPT. Slides touched: **1** (operator title kept), **2/3**
(ebook+slots + composite + data-mix framing), **7** (both-coexist, planner picks per book), **8**
(music_wrapper 1P+2P attributed examples), **10** (per-platform rollout replaces volume tiers), **11**
(operator "Standard 800" kept; tier-choice chip aligned), **12** (Music-Format = data-derived), **13**
(M1 no-file reframe, M3 typo fix, M5 podcast+PDF), **14** (companion-song bundling reframed), **15**
(operator "Composite USLF" kept).

*End §AMENDMENT-2026-06-13. Status: PROPOSED — operator-review-pending. Cap ratification
(`MUSIC-ONBOARDING-SONG-KIT-V1-01-AMENDMENT-2026-06-13`) is the gated serial-lane next-action.*

# Music mode freebie + funnel — V1 spec

**Status:** ACTIVE — operator Q1–Q3 recorded 2026-05-09 (see §16; AMENDMENT in `docs/PEARL_ARCHITECT_STATE.md`)  
**Cap entry:** `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` in `docs/PEARL_ARCHITECT_STATE.md`  
**Project:** `PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`  
**Parent program:** `PRJ-MUSIC-MODE-BRAND-INTEGRATION-V1` / `MUSIC-MODE-BRAND-INTEGRATION-V1-01` (wizard + registry + catalog)  
**Owner (ratification):** Pearl_Architect  
**Primary implementation agents:** Pearl_Marketing (inventory + templates); Pearl_Dev (wiring); Pearl_PM (coordination)  
**Subsystems:** marketing (primary); brand_admin; music_pipeline  

**Authority docs:**

- `docs/PEARL_ARCHITECT_STATE.md` (`MUSIC-MODE-FREEBIE-FUNNEL-V1-02`; cross-ref `MUSIC-MODE-BRAND-INTEGRATION-V1-01`, `MUSIC-MODE-V1-01`)
- `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` (wizard + survey persistence contract)
- `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` + `config/freebies/freebie_registry.yaml` (existing freebie taxonomy)
- `specs/FUNNEL_AND_BOOK_COPY_WRITER_SPEC.md` (funnel + book copy alignment where applicable)
- `funnel/README.md` (operational funnel hub layout)

---

## §1. Scope

This program covers **music mode brand freebies** and **funnel artifacts** that **differ from** (or **extend**) standard Pearl Prime / teacher-brand freebie + funnel patterns—so music-mode brands (38+) can use **audio-first** lead magnets and hooks without pretending music is a generic “exercise PDF” offer.

**In scope (architecture + coordination):**

- Which existing surfaces can carry music-mode freebies (inventory).
- A **V1 candidate set** of music-native freebie **types** (operator approval via §16).
- **Funnel flow delta** vs the standard brand funnel (shared backbone + music hooks).
- **Anti-drift** rules (additive only; YAML-driven selection; catalog volume vs freebie cadence).

**Explicitly out of scope for this spec’s opening PR:**

- Code, UI, automation, or GHL wiring changes.
- Authoring finished freebie creative (Pearl_Marketing owns in implementation).
- Changing Path X **37** or `canonical_brand_list.yaml`.

**Operator-stated examples** (non-exhaustive): companion songs as freebies; music previews; sample EPs; lyric videos; listening-first CTAs.

---

## §2. Inventory of existing freebie + funnel surfaces (discovery)

Discovery date: **2026-05-09** (Pearl_Architect sweep on `origin/main` checkout). For each area: **music-mode-aware today** is taken as **no / minimal** unless a path explicitly branches on `music_mode` (none found in configs reviewed).

### 2.1 `funnel/` directory

| Location | Role | Music-mode-aware? | Where music-mode freebies belong |
|----------|------|-------------------|----------------------------------|
| `funnel/README.md` | Documents Flask proof-loop hub; points to `config/freebies/*` for hub config | No | New hub YAML slices + email templates that reference **audio/track list** assets |
| `funnel/burnout_reset/` | Reference hub: landing templates, E1–E5 emails, SQLite lead capture, GHL/SMTP modes | No (somatic + book intent) | Parallel **music-first** hub variant or parameterized templates: hero + emails + `/books/<slug>` vs `/album/<slug>` routing (implementation ws) |
| `funnel/burnout_reset/config.yaml` | Hub runtime config | No | Extend pattern for music hub(s) |

### 2.2 `platform_marketing/` directory

**Result:** No directory named `platform_marketing/` at repository root on this date. **Mapped stand-ins** used for “platform + marketing” content in-repo:

| Location | Role | Music-mode-aware? | Where music-mode freebies belong |
|----------|------|-------------------|----------------------------------|
| `config/marketing/*.yaml` | Consumer language, invisible scripts, v32 social wiring, assumptions | No (teacher/book framing) | Optional **music_mode** keyed blocks after inventory ws proposes schema |
| `docs/marketing/ITE_FEATURE_BRIEF.md` | Marketing doc | No | Reference only |
| `scripts/marketing/*.py` | Catalog priority / scaffold patches | No | Only if funnel selects SKUs by brand mode |
| `marketing_deep_research/` | Research corpus | N/A | Positioning inputs for templates |

### 2.3 `somatic_exercise_freebee_apps/` directory

| Location | Role | Music-mode-aware? | Where music-mode freebies belong |
|----------|------|-------------------|----------------------------------|
| `somatic_exercise_freebee_apps/*.html` | Standalone somatic HTML “apps” (breath tools, etc.) | No | **Does not** host audio EPs; music-mode brands still **may** reuse somatic tools as **secondary** freebies—**additive** to music-native types in §3 |

### 2.4 Per-brand freebie configuration (repo SSOT patterns)

| Location | Role | Music-mode-aware? | Music-mode extension |
|----------|------|-------------------|------------------------|
| `config/freebies/freebie_registry.yaml` | SSOT list of freebie definitions (`freebie_id`, `type`, `topics`, `personas`, `output_formats`, …) | No music-specific `type` values observed | **Add** new `freebie_id` entries with new `type` enum values **only** after taxonomy amendment agreed with `PHOENIX_FREEBIE_SYSTEM_SPEC.md` maintainers |
| `config/freebies/freebie_selection_rules.yaml` | Selection / pairing rules | No | Conditional branches on **brand archetype = music_mode** + YAML fields from wizard/survey |
| `config/freebies/funnel_proof_loop.yaml` | Per-hub proof loop: topic, `first_exercise`, `story_id`, `book_slug` | Exercise + book | Parallel keys or hubs: `first_track`, `album_slug`, `preview_clip_id` (names illustrative—Pearl_Marketing + Pearl_Dev align to schema) |
| `config/freebies/freebie_to_book_map.yaml` | Maps free exercise/topic → book URLs | Book URLs | **Add** `freebie_to_album_map` or extend map with **music destination** fields (implementation) |
| `config/freebies/funnel_sections.yaml` | Optional hero / problem / solution / CTA | Book/somatic | Music hero variants (waveform, track title, “listen 30s”) |
| `config/freebies/exercises_landing.json` | Landing exercise list | Somatic | Keep for mixed-mode; music-primary hubs may hide or reorder |
| `config/freebies/companion_workbook_platform_content.yaml` | Workbook / platform companion content | Book/workbook | Music parallel: “companion_single_sheet_music” or lyric-poster bundle (template ws) |
| `config/freebies/audio_scripts.yaml` | Audio script patterns | Partial (affirmations etc.) | Reuse channel for **preview clip** scripts + **behind-the-song** narration |

### 2.5 Per-format freebie templates (existing types)

`freebie_registry.yaml` enumerates types such as `somatic_html_tool`, `affirmations_audio`, `assessment_html`, PDF tools, etc.—centered on **book + somatic** outcomes. **Per-format templates** (HTML/MD/PDF/mp3) live alongside the freebie system per `PHOENIX_FREEBIE_SYSTEM_SPEC.md`. **Music-mode V1** proposes **additional** types (§3), not a replacement of those rows.

---

## §3. Proposed music mode freebie types (V1 candidate set)

| ID | Type | Description |
|----|------|-------------|
| M1 | `companion_track_download_v1` | **Companion song download** — one free full-quality track from an upcoming album; gated email capture. |
| M2 | `preview_clip_30s_v1` | **30s preview clip** — lyric snippet on-screen + audio hook; bridges to album/pre-save. |
| M3 | `sample_ep_bundle_v1` | **Sample EP** — 3–5 tracks as a single deliverable (zip or streaming links per policy). |
| M4 | `lyric_poster_pdf_v1` | **Lyric poster (PDF)** — printable artifact tied to M1/M2. |
| M5 | `behind_the_song_interview_v1` | **Behind-the-song interview** — audio or long-form text; ties persona to track meaning. |

Additional types (e.g. **lyric video** file, **stem/teaser** pack, **live session** recording) are **Pearl_Marketing** extensions after Q1.

---

## §4. Funnel flow delta

**Baseline:** Standard Pearl / `burnout_reset`-style funnel: landing → form → proof-loop emails → book intent / Amazon (see `funnel/README.md` + `freebie_to_book_map.yaml`).

**Music-mode brand funnel = same backbone + music-specific top-of-funnel hooks:**

| Stage | Standard (non-music) | Music-mode delta (proposed) |
|-------|----------------------|-----------------------------|
| TOF hero | Problem/somatic or book promise | **Track title + “listen”** CTA; album art; 30s embed or link |
| Lead magnet delivery | PDF / HTML tool / short audio affirmations | **M1–M5** types; file formats may include **mp3/wav**, PDF, optional video |
| Email 1–2 | Proof + credibility + exercise | **Clip + story**; link to preview; “why this track exists” |
| Mid sequence | Story bank (`funnel/burnout_reset/stories/`) | **Behind-the-song** narrative; tour dates / release timeline optional |
| Bottom | Book slug → `book_url` | **Album / EP / pre-save** destination; book funnel **still allowed** as secondary CTA for hybrid offers—**not** replacing music CTA without operator decision |

**Stays the same:** consent + unsubscribe discipline; SQLite/GHL handoff pattern; proof-loop **structure** (E1–E5 count); compliance footer; hub-per-brand configuration style in `config/freebies/`.

---

## §5. Anti-drift

1. **Additive mandate:** Music-mode freebies **extend** the standard set; implementation **must not** remove or silently swap standard Pearl Prime freebies for music-mode brands.
2. **Taxonomy:** New music freebie types appear as **new** `freebie_id` / `type` entries (or versioned suffixes) coordinated with `PHOENIX_FREEBIE_SYSTEM_SPEC.md`—no ad-hoc parallel registry.
3. **YAML consumption (normative):** Freebie selection and template variables **must** read **`brand_wizard`** session YAML and **`musician_reflections_survey`** persisted fields (wizard SSOT per `MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §3). **Forbidden:** hardcoded “this artist always gets M3” tables in application code.
4. **Catalog volume vs freebie cadence:** **Q3 = 800** (or operator override from parent spec) governs **Pearl Prime book catalog** row counts for the music-mode brand slice — **not** the count of freebie PDFs/tracks. **Freebie cadence** (e.g. one companion track per campaign wave, quarterly EP samples) is a **marketing operations** parameter; document defaults in Pearl_Marketing runbooks after Q3 phasing decision.

---

## §6. Action items (sub-workstreams)

| workstream_id | Owner | Task (one line) |
|---------------|-------|-----------------|
| `ws_music_freebie_inventory_audit_20260509` | Pearl_Marketing | Audit §2 surfaces + email/GHL realities for music-mode applicability; propose minimal schema deltas. |
| `ws_music_freebie_template_authoring_20260509` | Pearl_Marketing | Author templates + copy blocks for M1–M5; locale + voice guardrails. |
| `ws_music_freebie_funnel_wiring_20260509` | Pearl_Dev | Wire freebie generation + funnel config loaders to consume wizard + survey YAML for music-mode brands. |

---

## §7. Status

**ACTIVE** — operator recorded **Q1–Q3** in §16 on 2026-05-09 (Pearl_Conductor autonomous wave; binding). **MUSIC-MODE-FREEBIE-FUNNEL-V1-02-AMENDMENT** in `docs/PEARL_ARCHITECT_STATE.md` (2026-05-09).

---

## §16. Operator decision card (verbatim)

**Q1:** Approve §3 proposed freebie types (M1–M5 listed) as the **V1** set, **or** refine (which to drop/add)?

**Q2:** Funnel delta scope (§4) — **full delta** (rebuild all touchpoints for music-mode hubs) **or** **minimal** (top-of-funnel hooks only; remainder shared with standard funnel)?

**Q3:** Implementation phasing — **single big PR** **or** **phased** (inventory → templates → wiring)?

### Operator answers (recorded 2026-05-09 via Pearl_Conductor autonomous wave)

- **Q1 = approve** (M1-M5 set ratified)
- **Q2 = minimal** (funnel delta minimized)
- **Q3 = phased** (Phase 1 templates + inventory; Phase 2 funnel wiring gated)

Authorization: Pearl_Conductor 2026-05-09 autonomous wave (operator pre-approved).
AMENDMENT entry: docs/PEARL_ARCHITECT_STATE.md MUSIC-MODE-FREEBIE-FUNNEL-V1-02 — AMENDMENT — 2026-05-09.

---

## Revision history

| Date | Change |
|------|--------|
| 2026-05-09 | Initial Pearl_Architect doc-only cap + spec; discovery snapshot on `origin/main`. |
| 2026-05-09 | AMENDMENT — operator Q1=approve, Q2=minimal, Q3=phased recorded in §16 (Pearl_Conductor autonomous wave defaults; binding). Cap status proposed → active. Cross-ref: `docs/PEARL_ARCHITECT_STATE.md` MUSIC-MODE-FREEBIE-FUNNEL-V1-02 — AMENDMENT — 2026-05-09. |

## gt30d C05 — Wizard/survey-driven freebie selection (2026-07-22)

**Keeper:** I026 · Additive to this ACTIVE spec — does not supersede §0–§16.

### Hard rule

Freebie selection for music-mode brands MUST be driven by:

1. `brand_wizard` YAML output for the minted brand, and
2. `musician_reflections_survey` (or successor) YAML,

**not** hardcoded freebie lists in Python.

### Cursor implementation surface

- `scripts/music/select_music_mode_freebie.py` — hard-errors if wizard/survey candidates missing
- Reuse pack: `docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/`

### Signal

`gt30d-c05-spec-terminal` when this additive section lands with the selector.

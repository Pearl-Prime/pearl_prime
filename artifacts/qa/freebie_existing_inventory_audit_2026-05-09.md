# Freebie existing-inventory audit — music-mode applicability

| Field | Value |
|-------|-------|
| Audit date | 2026-05-09 |
| Workstream | `ws_music_freebie_inventory_audit_20260509` |
| Project | `PRJ-MUSIC-MODE-FREEBIE-FUNNEL-V1` |
| Cap entry | `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` (per `docs/PEARL_ARCHITECT_STATE.md`) |
| Spec authority | `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` |
| Issue ref | #989 amendment |
| Subsystems | marketing (primary); brand_admin |
| Author agent | Pearl_Editor (acting on Pearl_Marketing scope under §6) |
| Mode | doc-only audit (no code, no asset generation, no edits to existing freebies) |
| Sources of truth | `config/freebies/freebie_registry.yaml`, `config/music/music_brand_registry.yaml`, `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` §2–§3, `funnel/README.md` |

---

## §1. Purpose

Per the §989 amendment to `MUSIC-MODE-FREEBIE-FUNNEL-V1`, audit every existing freebie asset across `funnel/` and `somatic_exercise_freebee_apps/` (plus `config/freebies/` + `freebie_registry.yaml`) for **music-mode applicability**, and stage a **brand × M1–M5** gap matrix against `config/music/music_brand_registry.yaml`.

This file is **classification only**. No new freebie content is authored here. Template authoring is a separate ws (`ws_music_freebie_template_authoring_20260509`) per spec §6.

## §2. Classification taxonomy

Each existing asset is classified as exactly one of:

| Bucket | Definition |
|--------|------------|
| `book-applicable` | Asset is bound to book/somatic outcomes (PDF workbook, book-CTA email, exercise-specific landing). **Reusing it as-is in a music-mode funnel would force music brands to LARP as somatic/book brands** — explicitly flagged by spec §5 anti-drift item 1. |
| `music-applicable` | Asset is a music-native artifact (companion track, preview clip, sample EP, lyric poster, behind-the-song interview). **None exist on `origin/main` as of 2026-05-09** — that absence is the gap matrix story. |
| `both` | Asset is mode-agnostic infrastructure / channel / config (audio mp3 delivery, GHL/SMTP/GA4 plumbing, hub-config patterns, somatic tools as **secondary** add-ons per spec §2.3) and survives unchanged or via additive YAML keys for music-mode brands. |
| `neither` | Asset is irrelevant to both modes (none in this audit). |

Anti-drift note: where a config file is `book-applicable` today but spec §2.4 calls for an **additive parallel** (e.g. `freebie_to_book_map.yaml` → future `freebie_to_album_map.yaml`), it remains `book-applicable` here — the **parallel** is a deferred ws output, not a reclassification of the existing file.

## §3. Discovery summary (counts)

Discovery commands run from `origin/main` checkout (parent repo `/Users/ahjan/phoenix_omega`, identical state to fresh worktree):

```bash
find ./funnel -type f \( -name '*.html' -o -name '*.yaml' -o -name '*.md' \) -not -path '*/.claude/*'
find ./somatic_exercise_freebee_apps -type f -name '*.html' | wc -l
ls config/freebies/
```

| Surface | File count | Notes |
|---------|------------|-------|
| `funnel/` (.html / .yaml / .md, excl. `.claude/`) | **16** | Single live hub (`burnout_reset/`) + top-level `README.md` |
| `somatic_exercise_freebee_apps/*.html` | **42** | 22 `ex##_*` + 20 `app##_*` standalone breath/body tools |
| `config/freebies/*` (yaml + json) | **13** | SSOT configs + 1 JSON landing list |
| `freebie_registry.yaml` enumerated freebies | **17** | Unique `freebie_id` definitions in the `freebies:` map. Plus 15 `registered_freebies` slugs (selection-side mappings to the 17 definitions; not double-counted). |
| **Total assets audited** | **88** | (16 + 42 + 13 + 17) |

`config/music/music_brand_registry.yaml` was read for the brand axis (see §6): **1 entry, `_template_music`, status `inactive`**. No active music-mode brands on `origin/main` as of 2026-05-09.

## §4. Per-asset classification — `funnel/` (16)

| # | Path | Classification | Music-mode rationale |
|---|------|----------------|----------------------|
| 1 | `funnel/README.md` | `both` | Documents Flask proof-loop hub pattern; pattern reusable for music hubs. Spec §2.1: "New hub YAML slices + email templates that reference audio/track-list assets". |
| 2 | `funnel/burnout_reset/config.yaml` | `both` | Hub runtime config (email_mode, GHL/SMTP, GA4, base_url) — channel-agnostic; music hubs would clone the same pattern. |
| 3 | `funnel/burnout_reset/GHL_HANDBOFF.md` | `both` | GHL handoff contract is mode-agnostic (lead capture → CRM tags). Audio-CTA tags are additive. |
| 4 | `funnel/burnout_reset/LINE_HANDOFF.md` | `both` | LINE messaging handoff — channel layer; music CTAs ride the same channel. |
| 5 | `funnel/burnout_reset/GO_NO_GO.md` | `both` | Launch checklist (E1–E5 verified, unsubscribe works) — applies identically to a music hub. |
| 6 | `funnel/burnout_reset/emails/email_1_immediate.html` | `book-applicable` | E1 promotes somatic exercise + book intent; copy is topic-bound. Music E1 is a separate template (M1/M2 hook) authored under `ws_music_freebie_template_authoring_20260509`. |
| 7 | `funnel/burnout_reset/emails/email_2_delay.html` | `book-applicable` | E2 deepens somatic story + book CTA. |
| 8 | `funnel/burnout_reset/emails/email_3_delay.html` | `book-applicable` | E3 references `stories/` bank (anxiety/burnout) → book intent. |
| 9 | `funnel/burnout_reset/emails/email_4_delay.html` | `book-applicable` | E4 advances book CTA. |
| 10 | `funnel/burnout_reset/emails/email_5_delay.html` | `book-applicable` | E5 = more-books CTA (Phase 2 / optional in `config.yaml`). |
| 11 | `funnel/burnout_reset/stories/anxiety.md` | `book-applicable` | Anxiety narrative for E3 — book/somatic framing; music brands need behind-the-song narratives instead (M5). |
| 12 | `funnel/burnout_reset/stories/burnout.md` | `book-applicable` | Burnout narrative — same as above. |
| 13 | `funnel/burnout_reset/templates/burnout_reset.html` | `book-applicable` | 6-section landing page bound to somatic offer + book CTA. |
| 14 | `funnel/burnout_reset/templates/book_intent.html` | `book-applicable` | Explicit book-intent landing — by name. |
| 15 | `funnel/burnout_reset/templates/thank_you.html` | `book-applicable` | Thank-you page tied to somatic-exercise download phrasing. |
| 16 | `funnel/burnout_reset/templates/unsubscribed.html` | `both` | Unsubscribe confirmation — generic compliance copy; reusable as-is. |

**`funnel/` subtotals:** 6 `both`, 10 `book-applicable`, 0 `music-applicable`, 0 `neither`.

## §5. Per-asset classification — `somatic_exercise_freebee_apps/` (42)

All 42 standalone HTML apps are interactive breath / body / nervous-system tools (4-7-8 breathing, box breathing, coherence breathing, Wim Hof, tonglen, body scan, etc.). Per spec §2.3:

> Does not host audio EPs; music-mode brands still **may** reuse somatic tools as **secondary** freebies — additive to music-native types in §3.

Therefore **all 42 classify as `both`** (book-primary, music-secondary). They are not music-native, and they will never be the **primary** lead magnet for a music-mode brand, but they are not removed or quarantined for music-mode brands either.

| Group | Count | Examples | Classification |
|-------|------:|----------|----------------|
| `ex01_*`–`ex20_*` (numbered exercises) | 20 | `ex01_478_breathing.html`, `ex05_alternate_nostril.html`, `ex16_phoenix_flame.html`, `ex20_physiological_sigh.html` | `both` (secondary) |
| `app01_*`–`app03_*` (early apps) | 3 | `app01_478_breathing.html`, `app02_box_breathing.html`, `app03_coherence_breathing.html` | `both` (secondary) |
| `app21_*`–`app39_*` (advanced apps) | 19 | `app22_tonglen.html`, `app34_phoenix_breath.html`, `app37_wim_hof.html`, `app39_wim_hof_cold.html` | `both` (secondary) |
| **Total** | **42** | | **42 `both`** |

(Full filename list captured at discovery time in workstream worklog; not duplicated here for readability.)

**`somatic_exercise_freebee_apps/` subtotals:** 42 `both`, 0 `book-applicable`, 0 `music-applicable`, 0 `neither`.

## §6. Per-asset classification — `config/freebies/` (13)

| # | Path | Classification | Music-mode rationale |
|---|------|----------------|----------------------|
| 1 | `config/freebies/audio_scripts.yaml` | `both` | Audio script patterns; spec §2.4: "Reuse channel for preview clip scripts + behind-the-song narration" — i.e. M2 + M5 ride this file once entries are appended. |
| 2 | `config/freebies/companion_workbook_platform_content.yaml` | `book-applicable` | Workbook + platform companion content; spec §2.4 calls for a **parallel** music file (e.g. `companion_single_sheet_music`), not reuse. |
| 3 | `config/freebies/cta_anti_spam.yaml` | `both` | Anti-spam CTA hygiene — channel/compliance layer; mode-agnostic. |
| 4 | `config/freebies/cta_templates.yaml` | `both` | CTA template strings; music-CTA strings are additive entries. |
| 5 | `config/freebies/exercise_pairs.yaml` | `book-applicable` | Pair-up logic for somatic exercises (activation_down vs grounding) — somatic-only. |
| 6 | `config/freebies/exercises_landing.json` | `book-applicable` | Exercise list for landing pages; spec §2.4: "Keep for mixed-mode; music-primary hubs may hide or reorder". |
| 7 | `config/freebies/freebie_registry.yaml` | `both` | SSOT enumeration; spec §5 mandates **additive** rows for M1–M5 here (no parallel registry). |
| 8 | `config/freebies/freebie_selection_rules.yaml` | `both` | Selection rules; spec §2.4 calls for "Conditional branches on brand archetype = music_mode" — additive. |
| 9 | `config/freebies/freebie_to_book_map.yaml` | `book-applicable` | Maps freebie → book URL. Music parallel is `freebie_to_album_map` (deferred ws), not in-place edit. |
| 10 | `config/freebies/freebie_to_landing.yaml` | `both` | Freebie → landing path mapping; mode-agnostic key/value pattern. |
| 11 | `config/freebies/funnel_proof_loop.yaml` | `both` | Per-hub proof loop; spec §2.4: "Parallel keys or hubs: `first_track`, `album_slug`, `preview_clip_id`" — additive. |
| 12 | `config/freebies/funnel_sections.yaml` | `both` | Optional hero/problem/solution/CTA per hub; spec §2.4: "Music hero variants (waveform, track title, 'listen 30s')" — additive variants. |
| 13 | `config/freebies/tier_bundles.yaml` | `both` | Tier bundling pattern; mode-agnostic. |

**`config/freebies/` subtotals:** 9 `both`, 4 `book-applicable`, 0 `music-applicable`, 0 `neither`.

## §7. Per-asset classification — `freebie_registry.yaml` definitions (17)

The `freebies:` map in `config/freebies/freebie_registry.yaml` enumerates **17 unique `freebie_id` definitions**. None are music-native today (no `freebie_id` references companion track / preview clip / sample EP / lyric poster / behind-the-song interview).

| # | `freebie_id` | `type` | Classification | Music-mode rationale |
|---|--------------|--------|----------------|----------------------|
| 1 | `accountability_partner_v1` | `accountability_partner_pdf` | `book-applicable` | Book companion PDF; identity-bound to book topics. |
| 2 | `affirmations_audio_v1` | `affirmations_audio` | `both` | mp3 channel reusable; music-mode brands can ship branded affirmations as M5-adjacent narration. |
| 3 | `anxiety_assessment_v1` | `assessment_html` | `book-applicable` | Topic assessment funneling to book. |
| 4 | `audio_journal_prompts_v1` | `audio_journal_prompts` | `both` | mp3 channel reusable; behind-the-song prompts share the delivery rail. |
| 5 | `breath_reset_structured_v1` | `somatic_html_tool` | `both` | Somatic tool reusable as **secondary** for music-mode (spec §2.3). |
| 6 | `breath_timer_v1` | `somatic_html_tool` | `both` | Same as above. |
| 7 | `burnout_checklist_v1` | `checklist_pdf` | `book-applicable` | Book-companion checklist PDF. |
| 8 | `companion_core_v2` | `companion_workbook_pdf` | `book-applicable` | Book-companion workbook. |
| 9 | `conversation_scripts_v1` | `conversation_scripts_pdf` | `book-applicable` | Book-aligned scripts. |
| 10 | `emergency_kit_v1` | `emergency_kit_html` | `book-applicable` | Crisis-kit HTML; book-bound. |
| 11 | `environment_guide_v1` | `environment_guide_pdf` | `book-applicable` | Book-companion environment guide. |
| 12 | `guided_meditation_v1` | `guided_audio` | `both` | Guided audio channel reusable; music-mode brands can ship branded guided audio. |
| 13 | `identity_sheet_v1` | `identity_sheet_pdf` | `book-applicable` | Book-companion identity worksheet. |
| 14 | `journal_reflection_v1` | `journal_pdf` | `book-applicable` | Book-companion reflection journal. |
| 15 | `resistance_mapping_v1` | `resistance_mapping_html` | `book-applicable` | Book-aligned interactive map. |
| 16 | `shame_assessment_v1` | `assessment_html` | `book-applicable` | Topic assessment funneling to book. |
| 17 | `thirty_day_tracker_v1` | `thirty_day_tracker_pdf` | `book-applicable` | Book-companion habit tracker. |

**Missing music-native rows (gap, not classification):** the 5 V1 music types from spec §3 — `companion_track_download_v1` (M1), `preview_clip_30s_v1` (M2), `sample_ep_bundle_v1` (M3), `lyric_poster_pdf_v1` (M4), `behind_the_song_interview_v1` (M5) — **are not present in this map**. They surface as the **type-axis gap** in §10, not as classification rows here.

**`freebie_registry.yaml` subtotals (17 unique definitions):** 5 `both` (audio-channel reusable + somatic-secondary), 12 `book-applicable`, 0 `music-applicable`, 0 `neither`.

## §8. Aggregate classification

| Bucket | funnel | somatic | config/freebies | registry defs | **Total** |
|--------|-------:|--------:|----------------:|--------------:|----------:|
| `book-applicable` | 10 | 0 | 4 | 12 | **26** |
| `music-applicable` | 0 | 0 | 0 | 0 | **0** |
| `both` | 6 | 42 | 9 | 5 | **62** |
| `neither` | 0 | 0 | 0 | 0 | **0** |
| **Total audited** | 16 | 42 | 13 | 17 | **88** |

**Headline:** **0 / 88** existing assets are **music-applicable as a primary lead magnet**. **62 / 88** are mode-agnostic infrastructure or secondary-use somatic tools that survive a music-mode funnel intact. The full music funnel surface (M1–M5 primary lead magnets + music-native templates + per-brand album destinations) is **net-new** under `ws_music_freebie_template_authoring_20260509` + `ws_music_freebie_funnel_wiring_20260509`.

## §9. Music gap matrix (preview)

Authoritative TSV: `artifacts/qa/freebie_music_gap_matrix_2026-05-09.tsv`.

Brand axis is `config/music/music_brand_registry.yaml` (`music_brands:` list). Type axis is spec §3 M1–M5.

| brand_id | archetype | status | M1 | M2 | M3 | M4 | M5 | current_total | target_total | gap |
|----------|-----------|:-------|---:|---:|---:|---:|---:|--------------:|-------------:|----:|
| `_template_music` | `placeholder` | `inactive` | 0 | 0 | 0 | 0 | 0 | 0 | 5 | -5 |
| **TOTAL (1 brand)** | | | **0** | **0** | **0** | **0** | **0** | **0** | **5** | **-5** |

Target methodology: **1 unit of each M1–M5 type per active brand** (V1 per-brand minimum viable music funnel). The single registered brand is a `placeholder` template entry seeded for loader smoke-tests; no active musician brand exists yet (wizard + survey-save flow is the gating ws — `ws_music_brand_wizard_step1_step4_survey_pane_20260509` + `ws_music_brand_survey_save_post_yaml_advance_20260509`). Once active brands populate the registry, the gap matrix scales linearly: 5 × N active brands cells, all currently 0.

## §10. Top-3 gaps

1. **Brand-axis emptiness (most upstream).** `config/music/music_brand_registry.yaml.music_brands` contains exactly **1 inactive `_template_music` placeholder**. Zero active musician brands. Every M1–M5 generation pipeline reads `survey_yaml_pointer` from this registry, so the freebie funnel cannot ship a single real music-mode lead magnet until the wizard + survey-save flow lands.

2. **Type-axis emptiness in `freebie_registry.yaml`.** None of the 5 V1 music types from spec §3 are registered as `freebie_id` rows: `companion_track_download_v1` (M1), `preview_clip_30s_v1` (M2), `sample_ep_bundle_v1` (M3), `lyric_poster_pdf_v1` (M4), `behind_the_song_interview_v1` (M5). Spec §5 anti-drift item 2 mandates these go in **as additive rows**; absence today blocks `freebie_planner` selection logic from ever choosing a music freebie.

3. **Funnel-hub-axis emptiness in `funnel/`.** `funnel/` has exactly **one live hub** (`burnout_reset/`) and a top-level `README.md`. There is **zero music-mode parallel hub** (no `funnel/<musician_handle>_music/` analog with M1/M2-keyed landing + behind-the-song email sequence). The Flask app, SQLite leads table, and APScheduler jobstore patterns from `burnout_reset/` are reusable (classified `both` above), but the templates / emails / stories layer is fully net-new.

(Honourable mention — too narrow for the top-3 cut: zero `freebie_to_album_map.yaml` parallel to `freebie_to_book_map.yaml`. This is a single-file deferred deliverable, less structurally blocking than the 3 above.)

## §11. Out-of-scope reaffirmation

This audit explicitly does **NOT**:

- Modify any existing freebie content (no edits to `funnel/burnout_reset/`, `somatic_exercise_freebee_apps/`, `config/freebies/`, or `freebie_registry.yaml`).
- Generate any new freebie asset, template, or copy block (M1–M5 authoring belongs to `ws_music_freebie_template_authoring_20260509`).
- Wire any code, loader, or selector (belongs to `ws_music_freebie_funnel_wiring_20260509`).
- Append rows to `config/music/music_brand_registry.yaml.music_brands` (belongs to wizard + survey-save ws rows).
- Modify Path X 37 / `config/manga/canonical_brand_list.yaml` (frozen by `MUSIC-MODE-BRAND-INTEGRATION-V1-01` anti-drift invariant 1).

**Write scope honored:** exactly 2 NEW files in `artifacts/qa/`.

## §12. References

- `docs/specs/MUSIC_MODE_FREEBIE_FUNNEL_V1_SPEC.md` (cap entry, §2 inventory, §3 M1–M5 types, §5 anti-drift, §6 sub-workstreams)
- `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` (wizard + survey persistence; brand registry contract)
- `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` (existing freebie taxonomy authority)
- `config/freebies/freebie_registry.yaml` (read-only)
- `config/music/music_brand_registry.yaml` (read-only; brand axis source)
- `funnel/README.md` (operational funnel hub layout)
- Sibling output: `artifacts/qa/freebie_music_gap_matrix_2026-05-09.tsv`

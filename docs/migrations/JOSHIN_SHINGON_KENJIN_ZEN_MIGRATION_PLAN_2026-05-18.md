# Joshin → Shingon / Kenjin Roshi → Zen — Migration Plan

**Date:** 2026-05-18
**Decision-of-record:** `artifacts/coordination/operator_decisions_log.tsv` OPD-20260518-105
**Authority:** Pearl_Architect (this document); Pearl_Research foundational source `docs/research/shingon_buddhism_research_2026-05-18.md`
**Status:** **PLAN ONLY — no edits executed. Awaiting operator review before execution.**

---

## 0. Executive summary

OPD-105 corrects a doctrinal misclassification: Joshin is a **Shingon Buddhist lineage holder**, not a Zen teacher. The current pipeline has accumulated approximately **549 files** carrying ~4,216 individual `joshin`/`Joshin` mentions, and a substantial fraction of them frame Joshin as Zen.

The migration follows OPD-105 verbatim:

- **Joshin retains the slot** but is recast as **Kōyasan Shingon-shū** (default sub-school per research §1.3 / §8.1). All "Zen" framing, "zazen" / "koan" / "shikantaza" / "satori" / "kenshō" / "roshi" / "direct pointing" / "enso" / "stark zen ink" is excised from Joshin-touching surfaces and replaced with Shingon vocabulary (sanmitsu, Ajikan, Kōmyō Shingon, gohōgō, sokushin-jōbutsu, Dainichi Nyorai, Kōbō Daishi, Mt. Kōya, Shikoku 88, goma).
- A **new teacher `kenjin` (display: "Kenjin Roshi")** is created. The existing Zen-coded content — atoms with "Zen story" framing, the Cognitive Clarity / Clear Seeing Books brand identity (Zen inquiry, enso, dropping the story), the Zen-ink illustration style, the 6 Clear Seeing Books authors with Zen-coded bios — is **migrated to `kenjin`**, not regenerated.
- Pearl_News is **already correct** (`pearl_news/config/teacher_news_roster.yaml:75-81` declares Joshin as Shingon Esoteric Buddhism). Kenjin is **not added** to Pearl_News (per OPD-105 explicit scope).

This plan is therefore a **three-axis migration**:

1. **Joshin's content surfaces** (teacher card, atoms, doctrine) — UPDATE register from Zen-coded to Shingon-coded (most atoms are tradition-neutral and survive; ~7 are Zen-explicit and must be moved to kenjin).
2. **Kenjin's birth** (new teacher_id, doctrine, atoms inherited from Joshin's Zen-coded subset, registry add).
3. **Catalog routing** (manga, book_plans, series_plans, brand admin) — DECIDE per row whether to (a) keep Joshin under Cognitive Clarity in a Shingon-recoded register, (b) re-route the row to Kenjin, or (c) split: Cognitive Clarity stays Zen and routes to Kenjin, Joshin gets a new Shingon-coded brand. **Recommendation: option (c), pending operator approval — see §5.A operator-decision items below.**

---

## 1. Complete inventory of Joshin mentions

### 1.1 Quantitative summary

| Surface | Files | Mentions | Action archetype |
|---|---|---|---|
| `SOURCE_OF_TRUTH/teacher_banks/joshin/` (teacher card + 152 atom yamls) | 153 | ~310 | (a) UPDATE card, (b) AUDIT 6 atoms with Zen tells, (a) atom doctrine UPDATE |
| `config/source_of_truth/book_plans_en_us/cognitive_clarity__joshin__*` | 132 | ~400 | (c) DECIDE routing — book_plans need re-naming if rows move to kenjin |
| `config/source_of_truth/series_plans_en_us/cognitive_clarity__joshin__*` | 44 | ~140 | (c) DECIDE routing — register field must change from "zen-ink, direct-pointing" |
| `config/source_of_truth/manga_profiles/` (cognitive_clarity/ + series/cogclar_jp + brands/) | 12 | ~24 | (c) DECIDE routing |
| `config/catalog_planning/` (15+ files: teacher_brand_archetypes, teacher_brand_lane_assignments, teacher_topic_persona_scores, brand_display_names, brand_identity_system, brand_series_plans, etc.) | 14 | ~80 | (c) DECIDE routing per row — strategic |
| `config/manga/` (brand_lora_plans, character_brand_registry, teacher_character_prompts, brand_illustration_styles, genre_prompt_cookbook_v2, manga_brand_series_plan) | 6 | ~12 | (c) DECIDE — kenjin needs own LoRA / character prompt if split route is chosen |
| `config/teachers/teacher_registry.yaml` | 1 | 4 | (a) UPDATE Joshin entry; ADD `kenjin` entry |
| `config/brand_management/global_brand_registry.yaml` + `teacher_brand_map.yaml` | 2 | 14 | (a) UPDATE — current "Still Forest / Forest meditation" framing is itself drift; reconcile separately |
| `pearl_news/` (config, atoms, packs, pairs) | 27 | ~50 | (a) ALREADY CORRECT — no Kenjin addition per OPD-105; verify Joshin Shingon content is intact |
| `tests/` and `tests/fixtures/` | 10 | ~15 | (d) REGENERATE fixtures after atom move; UPDATE roster lists |
| `scripts/` (atom_writing, manga, pearl_news, video, image_generation, etc.) | 21 | ~35 | (a)/(d) UPDATE roster lists; add kenjin where applicable |
| `docs/` (specs, handoffs, PEARL_ARCHITECT_STATE, PEARL_NEWS_WRITER_SPEC, etc.) | 23 | ~60 | (a) UPDATE all "Joshin = Zen" claims; ADD kenjin cap entries |
| `artifacts/research/`, `artifacts/qa/`, `artifacts/audit/`, `artifacts/coordination/`, `artifacts/pearl_news/`, `artifacts/video/`, `artifacts/audiobook_samples/`, `artifacts/inventory/`, `artifacts/catalog*`, `artifacts/pearl_prime_en_us/`, `artifacts/manga_us_lead_picks/`, `artifacts/pipeline_examples/`, `artifacts/schedules/`, `artifacts/audits/`, `artifacts/content_coverage_report.json`, `artifacts/media_html_paths_inventory.txt` | 81 | ~250 | (d) REGENERATE most after sources change; HAND-EDIT a small set of human-readable handoffs |
| `MANGA_STRATEGIC_AUDIT_VERDICT.md` (root) | 1 | 3 | (c) Marketing/strategy doc — DECIDE per use |
| Other (`.github/workflows/max-quality-catalog.yml`, `old_chat_specs/`, `phoenix_v4/`, `qa_books_2026-05-04/`, etc.) | ~35 | ~50 | (a) UPDATE if active; LEAVE if archival |
| **TOTAL** | **~549** | **~4,216** | |

The 549 distinct files are listed exhaustively at `/tmp/joshin_files.txt` (regenerable by the inventory grep below) and stored in the inventory-grep audit attached as part of this migration's commit; see §1.4 for the inventory grep command.

### 1.2 Surface-by-surface inventory — what each mention does

#### (a) Joshin teacher-card / persona / voice definition → UPDATE to Shingon

| Path | Lines | What |
|---|---|---|
| `config/teachers/teacher_registry.yaml` | 154-167 | Top-level teacher entry: `joshin: display_name: "Joshin", kb_id: "joshin", doctrine_profile: "joshin", allowed_topics: *all_topics, allowed_engines: [overwhelm, shame]`. The teacher slot itself. |
| `SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml` | 1-31 | **Already declares Shingon** (line 4: "Shingon Esoteric Buddhism (真言宗 / Mikkyo); Sokushin Jobutsu"). Line 5 already lists Sanmitsu, Goma, Mantra, Mudra. Line 10 forbids "Zen or generic Buddhist framing." This file is the gold standard. **Apply additions** for Kōyasan Shingon-shū sub-school binding + research §3 / §4 / §5 enrichments (Ajikan / gohōgō / Kōmyō Shingon / hokkai-jō-in / dōgyō ninin / honpushō / gachirin-kan). |
| `pearl_news/config/teacher_news_roster.yaml` | 75-81 | Already Shingon (line 77: "Shingon Esoteric Buddhism (Mikkyo; Sokushin Jobutsu; Sanmitsu)"). No change needed; keep as-is. |
| `docs/PEARL_NEWS_WRITER_SPEC.md` | 381, 401 | Already Shingon (line 381: "Shingon Esoteric Buddhism (真言宗 / Mikkyo); Sokushin Jobutsu; Sanmitsu"; line 401: "Never write Zen framing"). No change needed. |
| `config/brand_management/teacher_brand_map.yaml` | 228-249 | Maps joshin to brand `still_forest` with "Forest meditation / nature connection" tradition. **THIS IS A SECOND-DRIFT.** Forest-meditation is **not** Shingon either. Either (i) reconcile to Shingon-grounded framing ("Mount Kōya forest training" works tonally), or (ii) treat as a separate brand-side framing problem to flag for follow-up Pearl_Architect cap. **Recommend (i).** |
| `config/brand_management/global_brand_registry.yaml` | 306, 944, 1461, 1978, 2495, 3012, 3529, 4046, 4563, 5080, 5597, 6114, 6631 (13 region instances) | Repeats the "Still Forest / Forest meditation" framing per region (US, JP, KR, TW, HK, CN, SG, ES, fr, de, it, hu, brazil). Same reconcile-to-Shingon treatment as above. |

#### (b) Joshin teaching content (atoms) → REVIEW for Shingon compatibility

Total Joshin atoms: **152** across 11 sub-categories.

| Category | Count | Audit verdict |
|---|---|---|
| COMPRESSION | 12 | Tradition-neutral psychological observations — RETAIN under Joshin, update tone if needed. |
| EXERCISE | 12 | Mostly breath / sit / notice — tradition-neutral. RETAIN, but rewrite practice anchor where it leans Zen (e.g., recast as Ajikan / susokukan / Kōmyō Shingon per research §6.3). |
| HOOK | 12 | Marketing-style hooks. Tradition-neutral. RETAIN. |
| INTEGRATION | 12 | Tradition-neutral. RETAIN. |
| PERMISSION | 15 | **`joshin_PERMISSION_001.yaml:3` has Zen tell** ("Zen has no dashboard"). **Move this atom to kenjin** OR rewrite ("Shingon has no dashboard" works); RETAIN remainder. |
| PIVOT | 15 | Tradition-neutral. RETAIN. |
| REFLECTION | 12 | Tradition-neutral. RETAIN. |
| SCENE | 7 | Tradition-neutral (meditation scenes, self-inquiry scenes). RETAIN, but light-rewrite to swap "sit" → "Ajikan" / "hokkai-jō-in mudrā" framing where appropriate per research §6.2. |
| STORY | 15 | **`joshin_STORY_000.yaml`, `joshin_STORY_001.yaml`, `joshin_STORY_003.yaml`, `joshin_STORY_014.yaml` are explicitly "Zen story" / "Zen tradition"**. Per research §8.5 (operator-decision item: discard vs. rewrite), recommendation = **MOVE these 4 to kenjin (Strategy A — purist) since they prescribe a "Zen story about a teacher and student" framing that is the canonical Zen genre.** RETAIN remainder. |
| TAKEAWAY | 12 | Tradition-neutral. RETAIN. |
| THREAD | 13 | **`joshin_THREAD_002.yaml:3` has Zen tell** ("the next koan"). **Move this atom to kenjin** OR rewrite ("the next mantra-test" works). RETAIN remainder. |

**Total Joshin atoms with Zen tells:** 6 (verified by `grep -rln "zen\|Zen\|zazen\|koan\|kōan\|shikantaza\|satori\|kensho" SOURCE_OF_TRUTH/teacher_banks/joshin/`):
- `STORY/joshin_STORY_000.yaml`
- `STORY/joshin_STORY_001.yaml`
- `STORY/joshin_STORY_003.yaml`
- `STORY/joshin_STORY_014.yaml`
- `PERMISSION/joshin_PERMISSION_001.yaml`
- `THREAD/joshin_THREAD_002.yaml`

Plus the doctrine.yaml lines 10 + 28 (those are **forbidden-Zen** declarations, not Zen-content — keep as-is).

**Recommended move-to-kenjin set:** the 4 STORY atoms. The PERMISSION + THREAD are single-line Zen-word-swaps and are simpler to in-place rewrite.

#### (c) Joshin assigned to a book/arc/catalog row → DECIDE routing

**Cognitive Clarity / Clear Seeing Books brand assets** — these are the architectural decision items:

| Path | Lines | Current state | Operator decision needed? |
|---|---|---|---|
| `config/catalog_planning/teacher_brand_archetypes.yaml` | 55-74 | "Cognitive Clarity, teacher: joshin, tradition: 'Zen Buddhism — direct pointing, dropping the story, pure heart'" — block defines unique_angle around Zen | **YES** — see §5.A.1 |
| `config/catalog_planning/brand_identity_system.yaml` | 58-80 | `cognitive_clarity: teacher: joshin, display_name: "Clear Seeing Books", tagline: "The mind was never the problem"`, description = "Zen inquiry works that dissolve thought loops", enso colophon | **YES** — see §5.A.1 |
| `config/catalog_planning/brand_display_names.yaml` | 20-23 | `cognitive_clarity: display_name: "Clear Seeing Books", teacher: joshin, tagline: "Zen inquiry for the modern mind"` | **YES** — see §5.A.1 |
| `config/catalog_planning/brand_teacher_matrix.yaml` | 35-36, 106-108 | Cognitive Clarity → joshin (primary); teacher_constraints.joshin = 4/5 max | **YES** — switches to kenjin if split |
| `config/catalog_planning/brand_series_plans.yaml` | 90-127 | cognitive_clarity → joshin, manga series A "The Seeing Mind", B "Impostor's Mirror", C "Worth Without Proof" | **YES** — re-route to kenjin if split |
| `config/catalog_planning/canonical_topics.yaml` | 55-59 | "joshin / cognitive_clarity — stark zen ink"; topics zen, direct_pointing, sitting, koans | **YES** — topics get reassigned to kenjin if split; if no split, REPLACE topic list with [shingon, mantra_practice, ajikan, mudra] |
| `config/catalog_planning/title_dedup_phrases.yaml` | 40-45 | "cognitive_clarity: joshin — stark zen ink, the clear pause"; titles "The Clear Pause", "Past the Loop", "The Quiet Mind", etc. | **YES** — titles re-route or new shingon-coded list authored |
| `config/catalog_planning/teacher_brand_lane_assignments.yaml` | 169, 190, 204, 218, 232, 246, 260, 274, 288, 302, 319, 333, 368 | cognitive_clarity teacher: joshin across 12 locale lanes (en_US + 11 international) | **YES** — re-route per locale or keep |
| `config/catalog_planning/teacher_topic_persona_scores.yaml` | 133-190 | Detailed scoring: overthinking 0.95, koans 0.9, zen 0.95, etc. | **YES** — if Joshin stays Shingon: drop "zen / direct_pointing / sitting / koans" from joshin's topic_scores and add shingon-coded canonical topics; if kenjin gets these scores, COPY block to kenjin |
| `config/catalog_planning/teacher_brand_author_roster.yaml` | 210-302 | 6 Clear Seeing Books authors: Ada Park, Joel Crane, Hana Lee, Marcus Stone, Yuki Tanabe, Elliot Vane — bios reference "Zen inquiry", "zazen for thirty years", "Zen for people who'd never set foot in a temple" | **YES** — re-route authors to kenjin's brand OR rewrite bios for Shingon if author roster stays under Joshin |
| `config/catalog_planning/brand_cover_art_specs.yaml` | 85-90 | character_lora: "joshin_cc"; prompt addendum "stark zen ink illustration" | **YES** — same routing decision |
| `config/catalog_planning/audiobook_video_catalog.yaml` | 43-47 | `joshin: brands: [cognitive_clarity], topics: [zen, direct_pointing, sitting, koans]` | **YES** — re-route |
| `config/manga/manga_brand_series_plan.yaml` | 78-104 | `cognitive_clarity: teacher: joshin, genre: seinen, topic_allocation: overthinking, imposter_syndrome, burnout, boundaries` | **YES** — re-route |
| `config/manga/character_brand_registry.yaml` | 105-148 | `cognitive_clarity: teacher_id: joshin, teacher_character.character_id: joshin_sensei`, with kenji_analyst / mira_skeptic / old_librarian supporting cast | **YES** — re-route |
| `config/manga/teacher_character_prompts.yaml` | 179-195 | joshin character prompt: "seinen manga character, sharp clean linework... penetrating gaze... pure seeing... Vinland Saga philosophical moments meets Honey and Clover" | **YES** — note: visual prompt is tradition-agnostic (no explicit Zen iconography), so it COULD stay under Joshin if his look is unchanged; but currently bound to `cognitive_clarity` brand which carries Zen identity. Re-route by reference. |
| `config/manga/brand_illustration_styles.yaml` | 40-59 | "cognitive_clarity: teacher: joshin, style_name: 'Stark Zen Ink'", prompt_template "enso brush marks, zen garden negative space" | **YES** — re-route; or if Joshin stays here, rename style to a Shingon-coded one ("Mandala-ink" / "Sumi-mandala" — sumi ink is canonical to both traditions, but "zen garden" / "enso" specifically are Zen-coded) |
| `config/manga/brand_lora_plans.yaml` | 21, 51-57 | `joshin: trigger_word: "joshin_cc", style_ref: cognitive_clarity, notes: "Japanese-American female, precise gaze, zen authority"` | **YES** — re-route; if Joshin stays under cognitive_clarity, rewrite notes to drop "zen authority" |
| `config/manga/genre_prompt_cookbook_v2.yaml` | 368 | `joshin_anxiety: anxiety` (topic lookup) | NO — pure identity mapping, no tradition implied; RETAIN |
| `config/source_of_truth/manga_profiles/brands/cognitive_clarity_seinen.yaml` | 10, 95 | brand-genre lane profile binding teacher: joshin to cognitive_clarity_seinen | **YES** — re-route |
| `config/source_of_truth/manga_profiles/cognitive_clarity/series_{01..08}.yaml` | each line 7 + description | 8 series profiles each binding joshin to cognitive_clarity; series narratives include "Joshin, a retired master builder", "Mentor Joshin, a humble tea master", "Joshin, a gardener", "Joshin, a instrument maker" — all Japan-coded mentor archetypes; not explicitly Zen but tonally aligned to "wise zen-coded elder" | **YES** — re-route to kenjin if Cognitive Clarity → Kenjin |
| `config/source_of_truth/manga_profiles/series/cogclar_jp_{01,02,04}.yaml` | each line 9 | 3 JP-locale series profiles binding joshin to cognitive_clarity | **YES** — re-route |
| `config/source_of_truth/book_plans_en_us/cognitive_clarity__joshin__*.yaml` | filename prefix + interior fields | **132 book plan files** (11 personas × 4 topics × 3 engines minus combinations the operator did not author). Each contains `teacher: joshin`, brand `cognitive_clarity`, and narrative copy that includes Zen-coded language ("zen-ink, direct-pointing", enso metaphors). | **YES** — re-route ENTIRELY to kenjin if split; otherwise rewrite voice register from "zen-ink" to "shingon-mandala" |
| `config/source_of_truth/series_plans_en_us/cognitive_clarity__joshin__*.yaml` | filename + `register:` field | **44 series plan files**. Every file has `series_voice_markers.register: "zen-ink, direct-pointing, cognitive disruption"` (line 61). Each has `teacher: joshin`. | **YES** — same routing decision |

**Total book/series plan files needing routing decision: 176** (132 + 44).
**Total manga profiles needing routing decision: 12** (8 + 3 cogclar_jp + 1 brand-genre lane).

#### (d) Joshin in test fixtures / sample outputs → REGENERATE after teacher-card update

| Path | Lines | What |
|---|---|---|
| `tests/manga/test_series_plan_generator.py` | 166 | Hardcoded teacher list `["ahjan", "joshin", "junko", "maat", "miki", "ra"]` — UPDATE to add kenjin |
| `tests/manga/test_reference_sheet_generator.py` | (search) | Likely similar roster reference — VERIFY |
| `tests/fixtures/slot_contracts/completed/fixture_youth_feature.yaml` | 6, 7, 12 | Test fixture explicitly using Joshin + JP locale + education topic — currently valid (Joshin DOES carry mental_health/education in Pearl_News). RETAIN; UPDATE if fixture wants to assert Shingon framing |
| `tests/test_run_pearl_news_teacher_batch_*.py` (4 files) | (rosters) | Teacher batch tests; UPDATE rosters if needed |
| `tests/test_pearl_news_*.py` (4 files) | (rosters) | Pearl News tests; UPDATE rosters if needed |
| `tests/test_cookbook_v2_loader.py` | (search) | Loader test — VERIFY |
| `tests/test_cover_d1_immediate_fixes.py` | (search) | Cover test — VERIFY |
| `artifacts/audiobook_samples/_prose/joshin_anxiety_ch1.txt` | full file | Sample prose — REGENERATE post-migration |
| `artifacts/pipeline_examples/joshin/book_joshin_anxiety_15min.txt` | full | Blind-10 Book 2 — this is the file that flagged the doctrinal error; REGENERATE post-migration with Shingon framing |
| `artifacts/video/teacher_30s_v1/joshin/script_ja_JP.yaml` | full | Video pilot script; REGENERATE if Joshin's voice changes register |
| `artifacts/video/tiktok_body_awareness/joshin/...` (multiple) | full | TikTok body-awareness videos — REGENERATE post-card-update |
| `artifacts/pearl_news/published/2026-04-{19,22}/{morning,evening}/joshin/*.json` | full | Published Pearl News articles — RETAIN (already correct; Pearl News was correct); no regen needed |
| `artifacts/manga_visual_dev/...` (multiple `joshin_*.png` assets) | binary | Visual assets — see §5.C for visual iconography risk |

### 1.3 Full file list (skipping artifact regen list)

A full file list is too large to inline (549 files). It can be regenerated at any time via:

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/musing-lewin-4a91a3
grep -rln "joshin\|Joshin" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | sort > /tmp/joshin_files.txt
```

The current snapshot has:
- 188 files under `config/source_of_truth/` (132 book_plans + 44 series_plans + 12 manga_profiles)
- 153 files under `SOURCE_OF_TRUTH/teacher_banks/joshin/` (152 atoms + 1 doctrine)
- 27 under `pearl_news/`
- 23 under `docs/`
- 22 under `old_chat_specs/` (likely archival — verify and skip if not active)
- 14 under `config/catalog_planning/`
- 14 under `artifacts/pearl_news/`
- 11 under `artifacts/qa/`
- 11 under `artifacts/audit/`
- 10 under `tests/`
- 8 under `artifacts/research/`
- 6 under `config/manga/`
- 6 under `artifacts/catalog/`
- 3 under `scripts/video/`, 3 under `scripts/image_generation/`, 3 under `artifacts/inventory/`, 3 under `artifacts/audiobook_samples/`
- 2 each under `scripts/pearl_news/`, `scripts/atom_writing/`, `old_chat_specs/specs/`, `phoenix_v4/`, `brand-wizard-app/public/data/`, `config/publishing/`, `config/brand_management/`, `artifacts/video/`, `artifacts/pipeline_examples/`, `artifacts/pearl_prime_en_us/`, `artifacts/catalog_visibility/`
- 1 each: `.github/workflows/max-quality-catalog.yml`, `MANGA_STRATEGIC_AUDIT_VERDICT.md`, `SOURCE_OF_TRUTH/teacher_banks/CREATION_SUMMARY.md`, `teacher_books/`, `qa_books_2026-05-04/`, `config/video/`, `config/tts/`, `config/teachers/teacher_registry.yaml`, `config/authoring/`, and a long tail of `artifacts/` files. (See `/tmp/joshin_files.txt` for canonical list.)

### 1.4 Inventory grep — canonical reproducibility command

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/musing-lewin-4a91a3
grep -rn "joshin\|Joshin" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null > /tmp/joshin_mentions.tsv
```

This produces the line-level inventory (~4,216 lines). Pair with `/tmp/joshin_files.txt` for the unique-file-list (549 files).

---

## 2. Joshin updated teacher card — exact patches

### 2.1 `config/teachers/teacher_registry.yaml` — patch joshin entry (lines 154-167)

**Before:**

```yaml
  joshin:
    display_name: "Joshin"
    kb_id: "joshin"
    doctrine_profile: "joshin"
    allowed_topics: *all_topics
    disallowed_topics: [manifestation, get_rich_quick]
    allowed_engines: [overwhelm, shame]
    allowed_resolution_types: [open_loop, internal_shift_only, grounded_reframe]
    identity_shift_allowed: false
    preferred_formats: [F006, standard_book]
    teacher_mode_defaults:
      require_teacher_story: true
      require_teacher_exercise: true
      allow_generic_fallback_for_scene: true
```

**After (Shingon-correct):**

```yaml
  joshin:
    display_name: "Joshin"
    kb_id: "joshin"
    doctrine_profile: "joshin"
    tradition: "Shingon Esoteric Buddhism (Kōyasan Shingon-shū)"
    sub_school: "kogi_koyasan"  # Kogi Shingon, Mount Kōya headquarters
    lineage_root: "Kōbō Daishi (Kūkai, 774-835)"
    allowed_topics: *all_topics
    disallowed_topics: [manifestation, get_rich_quick]
    forbidden_traditions: [zen, theravada]   # Zen drift is the canonical error
    allowed_engines: [overwhelm, shame]
    allowed_resolution_types: [open_loop, internal_shift_only, grounded_reframe]
    identity_shift_allowed: false
    preferred_formats: [F006, standard_book]
    teacher_mode_defaults:
      require_teacher_story: true
      require_teacher_exercise: true
      allow_generic_fallback_for_scene: true
```

### 2.2 `SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml` — replace in full

The current doctrine.yaml (lines 1-31) is **already correctly Shingon** but is light on detail. Replace with the following expanded form grounded in research §2 / §3 / §4 / §5 / §6:

```yaml
display_name: "Joshin"
teacher_id: joshin
doctrine_version: "3"
tradition: "Shingon Esoteric Buddhism (真言宗 / Mikkyō)"
sub_school: "Kōyasan Shingon-shū (Kogi branch, Mount Kōya headquarters at Kongōbu-ji)"
lineage_root: "Kōbō Daishi (Kūkai, 774-835), via Huiguo of Qinglong-si, transmitted from the cosmic Buddha Mahāvairocana through the dual-mandala line"
ordination_level: "Full ajari (阿闍梨) — Kōyasan-lineage; lay-accessible voice register, Japanese-born, fluent English"

# Core doctrines — what Joshin teaches
core_doctrines:
  - sokushin_jobutsu:     "Buddhahood in this very body (即身成仏) — not deferred, not future-life. Present embodied existence is already the body of Dainichi."
  - sanmitsu:             "The three mysteries (三密) — body (mudrā), speech (mantra), mind (mandala/samādhi). Aligned simultaneously = Buddha-activity."
  - kaji:                 "Mutual empowerment (加持) — the dynamic in which practitioner and Mahāvairocana confirm one another."
  - dual_mandala:         "Womb Realm (Taizōkai, compassion) and Diamond Realm (Kongōkai, wisdom) — the world is both already-compassion and already-wisdom."
  - rokudai:              "The six great elements (六大: earth/water/fire/wind/space/consciousness) interpenetrate without obstruction — mind and matter are not separate, both are Dainichi's body."
  - honpushō:             "Non-origination (本不生) — the metaphysical content of the syllable A; nothing arises in itself."

# Signature practices (per research §3 / §6.3 — anxiety-actionable five)
signature_practices:
  - gohogo_recitation:    "Repeat 'Namu Daishi Henjō Kongō' (南無大師遍照金剛) — the Kōbō Daishi refuge phrase. Walks the present moment as 'dōgyō ninin' (two travelers with Kōbō Daishi)."
  - susokukan:            "数息観 — breath-counting 1 to 10, repeat. Preliminary; gateway to Ajikan."
  - hokkai_jo_in_komyo:   "Hokkai-jō-in mudrā (法界定印, hands in lap, thumbs touching) + Kōmyō Shingon (Mantra of Light: 'On abokya beirōshanō makabodara mani handoma jinbara harabaritaya un') — body + speech together."
  - gachirinkan:          "月輪観 — moon-disk visualization. Pure luminous awareness anchor against fragmented imagery."
  - ajikan:               "阿字観 — the lay-accessible Shingon meditation par excellence. Moon → lotus → Siddham letter A. Body in mudrā, speech in 'A', mind on the A-image — the complete three-mysteries practice in lay form."

# Vocabulary whitelist — Joshin's natural language
glossary:
  - "真言 / shingon — true word / mantra; also the school name"
  - "密教 / mikkyō — esoteric Buddhism, secret teachings"
  - "大日如来 / Dainichi Nyorai / Mahāvairocana — the cosmic Buddha, Great Sun Tathāgata"
  - "弘法大師 / Kōbō Daishi — Kūkai, posthumously titled; treated as living teacher resident in samādhi on Mount Kōya"
  - "高野山 / Kōyasan — Mount Kōya, the center"
  - "三密 / sanmitsu — the three mysteries"
  - "即身成仏 / sokushin-jōbutsu — Buddhahood in this very body"
  - "加持 / kaji — mutual empowerment"
  - "阿字観 / Ajikan — meditation on the syllable A"
  - "印 / 印契 / in / inkei — mudrā"
  - "法界定印 / hokkai-jō-in — cosmic samādhi mudrā (default sitting mudrā)"
  - "智拳印 / chi-ken-in — wisdom-fist mudrā (Diamond Realm)"
  - "護摩 / goma — fire ritual; canonical image of 'burning what no longer serves'"
  - "灌頂 / kanjō — abhiṣeka, initiation"
  - "結縁灌頂 / kechien-kanjō — public lay initiation (blindfolded flower-throw onto mandala)"
  - "阿闍梨 / ajari — ācārya, master"
  - "曼荼羅 / mandara — mandala"
  - "胎蔵界 / Taizōkai — Womb Realm mandala"
  - "金剛界 / Kongōkai — Diamond Realm mandala"
  - "般若心経 / Hannya Shingyō — Heart Sutra (Shingon opening: Bussetsu Maka Hannya Haramita Shingyō)"
  - "光明真言 / Kōmyō Shingon — Mantra of Light"
  - "御宝号 / gohōgō — 'Namu Daishi Henjō Kongō'"
  - "遍路 / henro — Shikoku 88 pilgrim"
  - "同行二人 / dōgyō ninin — 'two travelers walking together' (with Kōbō Daishi)"
  - "宿坊 / shukubō — temple lodging at Kōya"
  - "不動明王 / Fudō Myōō — Acala, Immovable Wisdom King; invoked for steadiness"
  - "六大 / rokudai — the six great elements"
  - "本不生 / honpushō — non-origination (meaning of A)"
  - "月輪 / gachirin — moon-disk"
  - "数息観 / susokukan — breath-counting"

tone_profile: |
  Warmly devotional but not effusive. Embodied, ritual-literate, sensory.
  Comfortable saying 'Namu Daishi Henjō Kongō' aloud; comfortable referring to
  Kōbō Daishi as a present companion; comfortable invoking Dainichi and Fudō
  as real presences — but never pushing the reader to share that devotion.
  Pose: "I trust this and find it operates; here is how you might try it; you
  don't have to believe what I believe." Path of accumulation, alignment, and
  habituation — NOT path of sudden rupture.

forbidden_claims:
  - "Zen framing (kōan, satori, kenshō, zazen, shikantaza, mu, dokusan, roshi, shoshin/beginner's mind, 'just sitting', 'pointing at the moon', 'sound of one hand')"
  - "Theravāda-as-Joshin's-tradition framing (anattā, vipassanā as primary, mettā as Joshin's signature, sati as standalone term)"
  - "Generic Japanese-Buddhism framing (Buddhism reduced to mindfulness-with-a-bow)"
  - "Reducing sanmitsu to 'breath-body-mind awareness' — sanmitsu is mudrā+mantra+mandala specifically"
  - "Reducing Ajikan to 'visualize a moon' — Ajikan is moon → lotus → A specifically"

tone_boundaries:
  - "Shingon is esoteric — it is explicit ritual technology, not gentle mindfulness"
  - "Sokushin Jobutsu is the load-bearing concept — Buddhahood now, in this body"
  - "Kōbō Daishi is contemporaneous, not a historical founder one reads about"
  - "Shingon is more devotional than Zen and more elaborated than Theravāda — Joshin's voice should be denser, warmer, more sensory than a Zen voice"

heart_sutra_opening: "Bussetsu Maka Hannya Haramita Shingyō (with 'Bussetsu' prefix — the Shingon form; this is the most reliable surface marker)"

honorific: "ajari (阿闍梨)"  # NOT roshi (老師, Zen-specific)

geographic_anchors: [Kōyasan, Shikoku 88, Okunoin, Tō-ji]

prohibited_outcomes:
  - "Zen framing — Joshin is Shingon esoteric, not Zen"
  - "Generic 'pure heart / non-separation' language without grounding in sanmitsu"
  - "Soft mindfulness positioning"
  - "Reducing the founder Kōbō Daishi to a historical figure rather than a living presence"
```

### 2.3 Joshin character / persona descriptor patches

| Path | Line(s) | Before | After |
|---|---|---|---|
| `config/manga/brand_lora_plans.yaml` | 57 | `notes: "Japanese-American female, precise gaze, zen authority"` | `notes: "Japanese-American female, precise gaze, ajari authority (Kōyasan Shingon-shū)"` |
| `config/manga/teacher_character_prompts.yaml` | 184-192 (joshin block) | "penetrating gaze… pure seeing" — visually neutral, OK as-is for now; recommend dropping the **"pure seeing"** phrase (Zen-coded) and adding **"holds a vajra or moon-disk visualization aid"** to lock Shingon iconography | (see §5.C visual iconography swap list) |

---

## 3. Kenjin Roshi — NEW teacher card (full)

### 3.1 Identity decisions

- **Teacher ID:** `kenjin` (lowercase, snake_case — consistent with `joshin`, `junko`, `ahjan`, etc.)
- **Display name (formal):** "Kenjin Roshi"
- **Display name (short):** "Kenjin"
- **Name etymology:** *Kenjin* (見人) = "one who sees" — directly captures Zen's "direct-pointing, seeing one's nature" register (kenshō, 見性, shares the 見 character). *Roshi* (老師) = "old/senior teacher", the canonical Zen honorific (per research §4.3 "roshi" is Zen-specific). Operator-approved spelling: K-E-N-J-I-N (per OPD-105).
- **Sub-school recommendation:** **Sōtō Zen** (per the prompt's recommendation and matching the voice register Joshin currently occupies — Sōtō centers shikantaza/breath-anchored sitting/lay-accessible practice). Founder: Dōgen Zenji (1200-1253). Headquarters: Eihei-ji (Fukui) and Sōji-ji (Yokohama).
- **Gender / age / cultural background:** Recommend **male, late 50s, Japanese-American (Kyoto-born, decades in California)**. Rationale for the choices:
  - **Male:** the existing teacher_banks roster currently is gender-mixed; Joshin (current LoRA notes) is **Japanese-American female**. Making Kenjin male provides clean visual + voice differentiation from the start and avoids "two female Japanese teachers, one Shingon one Zen" confusion.
  - **Late 50s:** matches the "decades sitting" experience that Zen ROSHI title implies (Joel Crane's bio in the existing Clear Seeing Books roster already implies "thirty years zazen" — this is the Kenjin voice).
  - **Japanese-American (Kyoto-born, Bay Area decades):** matches the existing Clear Seeing Books "Hana Lee / Marcus Stone / Yuki Tanabe" voice register (Zen for people who'd never set foot in a temple). Avoids clash with `master_wu` (Taiwanese, Taoist), `master_sha` (Tao calligraphy, Chinese), `master_feung` (Xi'an, Chinese wisdom).
- **Voice ID for audiobook:** **`N2lVS1w4EtoT3dr4eOWO` (Callum — measured, transatlantic)** — currently assigned to Joel Crane in the Clear Seeing Books roster; reuse for Kenjin (after author roster migration).

### 3.2 Full teacher_registry.yaml entry to ADD

Add the following block to `config/teachers/teacher_registry.yaml`, immediately after the `joshin:` block (i.e., between current line 167 and line 169 `maat:`):

```yaml
  kenjin:
    display_name: "Kenjin Roshi"
    short_name: "Kenjin"
    kb_id: "kenjin"
    doctrine_profile: "kenjin"
    tradition: "Sōtō Zen Buddhism"
    sub_school: "soto_zen"
    lineage_root: "Eihei Dōgen Zenji (1200-1253), via Tendō Nyojō; Sōtō school"
    allowed_topics: *all_topics
    disallowed_topics: [manifestation, get_rich_quick]
    forbidden_traditions: [shingon, theravada]
    allowed_engines: [overwhelm, shame]
    allowed_resolution_types: [open_loop, internal_shift_only, grounded_reframe]
    identity_shift_allowed: false
    preferred_formats: [F006, standard_book]
    teacher_mode_defaults:
      require_teacher_story: true
      require_teacher_exercise: true
      allow_generic_fallback_for_scene: true
```

### 3.3 Full `SOURCE_OF_TRUTH/teacher_banks/kenjin/doctrine/doctrine.yaml` to CREATE

```yaml
display_name: "Kenjin Roshi"
short_name: "Kenjin"
teacher_id: kenjin
doctrine_version: "1"
tradition: "Sōtō Zen Buddhism (曹洞宗 / Sōtō-shū)"
sub_school: "Eihei-ji line; lay-accessible voice"
lineage_root: "Dōgen Zenji (1200-1253) via Tendō Nyojō; thirteenth-century introduction of Sōtō to Japan; transmitted face-to-face master-to-disciple"
ordination_level: "Roshi (老師) — senior teacher, full transmission (denbō); long lay-teaching practice in the West"

# Core doctrines — what Kenjin teaches
core_doctrines:
  - shikantaza:           "Just sitting (只管打坐) — sustained, non-instrumental seated awareness. The practice IS the realization, not a means to it."
  - genjokoan:            "Genjō Kōan — 'actualizing the fundamental point' (Dōgen). Each moment of practice IS each moment of awakening."
  - buji_zen_warning:     "Practice is not 'nothing to do'; the seamless practice of everyday life IS the form."
  - mu_shotoku:           "Without-gaining (無所得) — the absence of any acquisitive aim is itself the realization."
  - dropping_off_body_mind: "Shinjin-datsuraku (身心脱落) — Dōgen's awakening phrase. The brittle self-construction releases when held without grasping."

# Signature practices
signature_practices:
  - zazen:                "Sitting in the standard zazen posture (cross-legged, half- or full-lotus, hands in cosmic mudrā). 25 to 40 minutes is the lay length."
  - shikantaza_method:    "Sit. Hold the posture. Allow what arises to arise. Do not pursue thought; do not fight thought. Return, return, return — to the upright body and the breathing."
  - kinhin:               "Slow walking meditation between sitting periods. Half-step per breath."
  - oryoki:               "Formal eating practice; lay version: pay full attention to one meal a day."
  - koan_inquiry:         "Holding a kōan in the body (NOT solving it intellectually) — Sōtō uses this less than Rinzai, but Kenjin will deploy a kōan when a student is stuck in thinking."

# Vocabulary whitelist — Kenjin's natural language
glossary:
  - "zazen / 坐禅 — seated Zen"
  - "shikantaza / 只管打坐 — just sitting"
  - "kinhin / 経行 — walking meditation"
  - "kōan / 公案 — a Zen 'case'; the paradox-question that interrupts conceptual thought"
  - "satori / 悟り — awakening"
  - "kenshō / 見性 — seeing one's nature (the etymological root of 'Kenjin')"
  - "mu / 無 — the most famous kōan ('Does a dog have Buddha-nature? Mu.')"
  - "dokusan / 独参 — private interview with the teacher"
  - "roshi / 老師 — senior teacher (Kenjin's title)"
  - "sensei / 先生 — teacher"
  - "oshō / 和尚 — priest"
  - "shoshin / 初心 — beginner's mind (Shunryū Suzuki's phrase)"
  - "zafu / 座蒲 — round meditation cushion"
  - "zabuton / 座布団 — square mat under the zafu"
  - "kesa / 袈裟 — outer robe"
  - "rakusu / 絡子 — small bib-style robe worn by ordained and lay practitioners with jukai"
  - "kyosaku / 警策 — encouragement stick (rarely used in Sōtō; signals attention-renewal)"
  - "Dōgen / 道元 — founder of Sōtō in Japan"
  - "Eihei-ji / 永平寺 — Sōtō's main training monastery"
  - "Bodhidharma / 達磨 — legendary Indian patriarch who brought Chan/Zen to China"
  - "Mu Mon Kan / 無門関 — 'Gateless Gate', classic kōan collection"
  - "Hekiganroku / 碧巌録 — 'Blue Cliff Record', classic kōan collection"
  - "enso / 円相 — single brush-stroke circle, the Zen iconographic mark"
  - "Genjō Kōan / 現成公案 — Dōgen's foundational essay"
  - "Shōbōgenzō / 正法眼蔵 — Dōgen's collected writings"

tone_profile: |
  Austere, direct, slightly more reductive than Joshin. Iconoclastic when needed —
  Kenjin will cut through conceptual elaboration: "Show me, don't tell me." Ordinary
  mind; not special. Body-centered (posture, breath) but minimally — no fire ritual,
  no mandala-room, no incense. Will give a kōan if a student is looping in their head.
  Comfortable with paradox. Comfortable with silence. Will end a sentence early.

first_person_bio: |
  I sat zazen for thirty years before I taught a word. I grew up in Kyoto, came to
  California in my twenties, sat in a temple in the Sierra foothills for two decades,
  and now I teach at a sangha that meets in a converted yoga studio in Berkeley.
  I am not interested in spiritual personalities. I am interested in whether you
  can sit when the room is uncomfortable. The cushion is here. The bell is at the
  beginning and the end. Between them, you find out who you are.

forbidden_claims:
  - "Shingon framing (sanmitsu, Ajikan, Kōmyō Shingon, gohōgō, sokushin-jōbutsu, Dainichi, Kōbō Daishi, kanjō, goma, mandala — all of these are Joshin's vocabulary, not Kenjin's)"
  - "Theravāda framing (anattā, vipassanā, mettā as Kenjin's practice-name)"
  - "Generic 'mindfulness' framing — Zen is not mindfulness with bowed heads; it is sustained non-instrumental sitting"

heart_sutra_opening: "Maka Hannya Haramita Shingyō (NO 'Bussetsu' prefix — the Zen form)"

honorific: "roshi (老師)"

geographic_anchors: [Eihei-ji, Kyoto temples, Berkeley/Bay-Area sangha, Suzuki Roshi's San Francisco Zen Center lineage register]

prohibited_outcomes:
  - "Confusing kenshō (Zen, Kenjin's tradition) with kanjō (Shingon, Joshin's tradition)"
  - "Mixing Soto-style shikantaza with Rinzai-style kōan-introspection without naming which"
  - "Reducing Zen to 'just breathing'"
```

### 3.4 `config/manga/brand_lora_plans.yaml` — ADD kenjin character_lora entry

If the routing decision in §5.A keeps Cognitive Clarity bound to Kenjin, ADD:

```yaml
  kenjin:
    trigger_word: "kenjin_cc"   # only if cognitive_clarity stays with Kenjin
    reference_images_needed: [front_portrait, three_quarter_view, profile_view, expression_sheet]
    training_steps: 1500
    ip_adapter_weight: 0.83
    style_ref: cognitive_clarity
    notes: "Japanese-American male, late 50s, austere bearing, roshi authority; rakusu over modern clothing in casual scenes, full kesa in temple scenes"
```

### 3.5 `config/manga/teacher_character_prompts.yaml` — ADD kenjin character prompt

```yaml
  kenjin:
    display_name: "Kenjin Roshi"
    style_archetype: dark_psychological
    ip_adapter_weight: 0.83
    img2img_denoise: 0.77
    positive: >-
      seinen manga character, late 50s Japanese-American Zen roshi, sharp clean
      linework with restrained warmth, austere bearing, shaved head with grown-in
      grey stubble, deeply lined face, eyes that are simultaneously kind and
      unfooled, simple dark clothing or black rakusu over plain robe, minimal
      background single object an empty zafu a bell a single brush stroke
      enso on the wall, expression that asks 'what is this, right now',
      style of Vinland Saga philosophical moments meets the elder-monk
      panels of Mushishi, the upright body of a long sitter
    negative: >-
      busy background, dark horror, chibi, action battle, heavy screentone,
      ornate clothing, fantasy, deity imagery, vajra or fire ritual props,
      tibetan or shingon iconography, mandala, flames
```

---

## 4. Migration script outline

### Step 0 — Pre-flight (mandatory per CLAUDE.md)

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/musing-lewin-4a91a3
git status --short
git fetch origin
git checkout main && git pull --ff-only origin main
```

### Step 1 — Branch creation

```bash
git checkout -b agent/joshin-shingon-kenjin-zen-migration origin/main
PYTHONPATH=. python3 scripts/git/push_guard.py
```

### Step 2 — File edits in dependency order

**Phase A — Teacher cards and registries (lowest risk, must land first):**

1. `config/teachers/teacher_registry.yaml` — patch joshin (§2.1) + add kenjin block (§3.2).
2. `SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml` — replace with §2.2 expanded form.
3. `mkdir -p SOURCE_OF_TRUTH/teacher_banks/kenjin/doctrine SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/{COMPRESSION,EXERCISE,HOOK,INTEGRATION,PERMISSION,PIVOT,REFLECTION,SCENE,STORY,TAKEAWAY,THREAD}`.
4. Write `SOURCE_OF_TRUTH/teacher_banks/kenjin/doctrine/doctrine.yaml` per §3.3.

**Phase B — Joshin atom audit & migration:**

5. `git mv SOURCE_OF_TRUTH/teacher_banks/joshin/approved_atoms/STORY/joshin_STORY_000.yaml SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/STORY/kenjin_STORY_000.yaml` — repeat for `joshin_STORY_001.yaml`, `joshin_STORY_003.yaml`, `joshin_STORY_014.yaml`.
6. For each moved STORY atom, replace `atom_id: joshin_STORY_NNN` with `atom_id: kenjin_STORY_NNN` and `teacher_id: joshin` with `teacher_id: kenjin` (in `teacher:` block).
7. `joshin_PERMISSION_001.yaml` (line 3) — rewrite `Zen has no dashboard` → `In Shingon there is no dashboard. The practice does not produce a metric.` (in-place, do NOT move).
8. `joshin_THREAD_002.yaml` (line 3) — rewrite `the next koan` → `the next moment of practice` (in-place).
9. Sweep remaining 145 Joshin atoms for any references to "zen", "zazen", "koan", "shikantaza", "roshi", "satori", "kensho" using:
   ```bash
   grep -rln "zen\|Zen\|zazen\|koan\|kōan\|shikantaza\|satori\|kensho\|roshi\|Roshi" SOURCE_OF_TRUTH/teacher_banks/joshin/approved_atoms/
   ```
   Expect 0 hits after step 7–8. Each new hit is an additional in-place rewrite OR move-to-kenjin.

**Phase C — Cognitive Clarity / Clear Seeing Books brand re-routing (HIGHEST RISK — requires operator decision per §5.A):**

10. Branch decision per §5.A.1. Once operator confirms routing direction, execute:
    - **If kenjin gets Cognitive Clarity:** UPDATE the `teacher:` field from `joshin` to `kenjin` in:
      - `config/catalog_planning/brand_identity_system.yaml:60`
      - `config/catalog_planning/teacher_brand_archetypes.yaml:55`
      - `config/catalog_planning/brand_display_names.yaml:22`
      - `config/catalog_planning/brand_series_plans.yaml:91`
      - `config/catalog_planning/brand_teacher_matrix.yaml:35-36, 106`
      - `config/catalog_planning/teacher_brand_lane_assignments.yaml` (13 locales lines: 169, 190, 204, 218, 232, 246, 260, 274, 288, 302, 319, 333, 368)
      - `config/catalog_planning/teacher_brand_author_roster.yaml:216` and re-key the entire `clear_seeing_books:` block to point to kenjin
      - `config/catalog_planning/audiobook_video_catalog.yaml:43`
      - `config/catalog_planning/brand_cover_art_specs.yaml:85, 88`
      - `config/catalog_planning/teacher_topic_persona_scores.yaml:139-190` (move entire joshin block to kenjin; replace joshin's slot with shingon-coded topics)
      - `config/manga/manga_brand_series_plan.yaml:80`
      - `config/manga/character_brand_registry.yaml:108-148` (update teacher_id, character_id, character_prompt_ref)
      - `config/manga/brand_illustration_styles.yaml:41`
      - `config/manga/brand_lora_plans.yaml:51-57` (move joshin block to kenjin, add the §3.4 kenjin entry, REMOVE joshin if joshin gets new brand)
      - `config/manga/canonical_brand_list.yaml` — UNCHANGED (no teacher binding here)
11. RENAME 132 book_plans_en_us files `cognitive_clarity__joshin__*` → `cognitive_clarity__kenjin__*` (use `git mv` to preserve history).
12. RENAME 44 series_plans_en_us files `cognitive_clarity__joshin__*` → `cognitive_clarity__kenjin__*`.
13. Sed-edit `teacher: joshin` → `teacher: kenjin` and `register: "zen-ink, direct-pointing, cognitive disruption"` (unchanged — it's already Zen-correct now that it's under Kenjin) in all 44 series plans.
14. Sed-edit similar fields in all 132 book plans.
15. RENAME the 12 `config/source_of_truth/manga_profiles/cognitive_clarity/series_*.yaml` + `series/cogclar_jp_*.yaml` to update internal `teacher: joshin` → `teacher: kenjin`. (Filenames don't include teacher, so no `git mv` needed.)
16. RENAME `config/source_of_truth/manga_profiles/brands/cognitive_clarity_seinen.yaml` line 10 `teacher: joshin` → `teacher: kenjin`.

**Phase D — Joshin's NEW brand (if option C in §5.A.1 chosen):**

17. Create new brand entry `wisdom_lineage_press` (working name, operator confirms) for Joshin in:
    - `config/catalog_planning/brand_identity_system.yaml` — new block with Shingon iconography (vajra/lotus colophon; Kōyasan-coded palette; tagline e.g. "Practice in this very body")
    - `config/catalog_planning/brand_display_names.yaml`
    - `config/catalog_planning/brand_teacher_matrix.yaml`
    - `config/catalog_planning/teacher_brand_lane_assignments.yaml` (all 13 locales)
    - `config/manga/brand_lora_plans.yaml` (joshin under new brand)
    - `config/manga/manga_brand_series_plan.yaml`
    - `config/manga/canonical_brand_list.yaml` (NEW brand definition, requires Path X cap entry per BR-CANON-01)
    - `config/source_of_truth/manga_profiles/brands/<new_brand>_seinen.yaml`
18. Author 4-6 new book_plans + 2-3 new series_plans for Joshin × Shingon × anxiety/sleep_anxiety/overthinking. (Out-of-scope for this migration PR — gates to follow-up commission per §6.B.)

**Phase E — Brand admin reconciliation:**

19. `config/brand_management/teacher_brand_map.yaml:228-249` — Either (i) reconcile `still_forest` to Shingon-grounded framing ("Mount Kōya forest training, ajari-led contemplative stillness"), OR (ii) leave as-is and flag for follow-up cap. Recommend (i).
20. `config/brand_management/global_brand_registry.yaml` — Same reconciliation across 13 region instances. (Sed-edit may be appropriate if the change is uniform.)

**Phase F — Test fixtures & scripts:**

21. `tests/manga/test_series_plan_generator.py:166` — add `"kenjin"` to roster list.
22. `tests/manga/test_reference_sheet_generator.py` — verify and update if needed.
23. `tests/fixtures/slot_contracts/completed/fixture_youth_feature.yaml` — RETAIN; verify Pearl_News Shingon framing still valid.
24. `scripts/atom_writing/write_teacher_stories.py:51` — add `"kenjin"` to roster.
25. `scripts/manga/generate_series_plans_from_catalog.py:195` — add `"kenjin": "cognitive_clarity",` (if kenjin claims Cognitive Clarity) and remove or update joshin's mapping.
26. `.github/workflows/max-quality-catalog.yml:22, 83-85` — add `kenjin` to the shard matrix.

**Phase G — Docs:**

27. `docs/PEARL_ARCHITECT_STATE.md` — ADD new cap entry "JOSHIN-SHINGON-KENJIN-ZEN-01" with the migration's authority chain.
28. `docs/PEARL_NEWS_WRITER_SPEC.md:381, 401` — RETAIN (already correct).
29. `docs/MANGA_MODE_STRATEGY.md:132`, `docs/SESSION_HANDOFF_2026_04_06.md:93`, `docs/SESSION_HANDOFF_2026_04_24.md:158`, `docs/TEACHER_SHOWCASE_HANDOFF.md:15`, etc. — UPDATE any reference where Joshin is described as Zen.
30. Pearl News spec `docs/PEARL_NEWS_5_VARIATION_EXPANSION_PROGRAM.md:89` — RETAIN ("Joshin = Shingon (Mikkyo). NOT generic Zen." is already correct).
31. `artifacts/research/teacher_market_validation_matrix_2026_04_04.md:14, 85, 436` and `webtoon_master_reference_2026-04-25.md:124`, `webtoon_therapeutic_scroll_craft_2026-04-25.md:673` — these are historical research artifacts. Recommend: APPEND a "2026-05-18 update: Joshin re-classified to Shingon per OPD-105; Zen content moved to new teacher Kenjin Roshi. The Zen-language sections of this document now apply to Kenjin, not Joshin." paragraph at the head of each file. DO NOT rewrite the body of historical research artifacts — that destroys archival truth.

**Phase H — Artifact regeneration (gates):**

32. `artifacts/audiobook_samples/_prose/joshin_anxiety_ch1.txt` — REGENERATE post-card via Pearl_Writer commission with Shingon framing. (Out-of-scope for this PR.)
33. `artifacts/pipeline_examples/joshin/book_joshin_anxiety_15min.txt` — REGENERATE. (Out-of-scope.)
34. `artifacts/video/teacher_30s_v1/joshin/script_ja_JP.yaml` — REGENERATE if Joshin's voice changes register; ELSE retain. (Defer.)

**Phase I — Catalog visibility & index refresh:**

35. `artifacts/catalog_visibility/book_series_index.json`, `manga_series_index.json` — REGENERATE via `python3 scripts/catalog/build_catalog_visibility.py` (or whatever the regen entry point is) AFTER all phase A–F edits.
36. `artifacts/catalog/catalog_repurposing_surface.json` — REGENERATE.

### Step 3 — Gate runs

```bash
# Register gate — confirms teacher registry is loadable and consistent
PYTHONPATH=. python3 scripts/ci/run_register_gate.py

# Scorecard — confirms teacher_topic_persona_scores still validates
PYTHONPATH=. python3 scripts/ci/run_scorecard.py

# Smoke test on one Joshin book (Shingon-recoded) + one Kenjin book (Zen)
PYTHONPATH=. python3 scripts/pearl_prime/run_book_smoke.py \
  --book-plan config/source_of_truth/book_plans_en_us/cognitive_clarity__kenjin__corporate_managers__overthinking__spiral.yaml
PYTHONPATH=. python3 scripts/pearl_prime/run_book_smoke.py \
  --book-plan <new joshin shingon plan> # gated on Phase D Step 18 commission

# Push-guard + preflight
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
```

### Step 4 — PR title and body draft

**Title:** `migration(teachers): split Joshin/Shingon from Kenjin/Zen (OPD-105)`

**Body:**

```markdown
## Summary
- Correcting OPD-105 doctrinal misclassification: Joshin is **Shingon** (Kōyasan), not Zen.
- Creates new teacher **Kenjin Roshi** (Sōtō Zen) to carry existing Zen content.
- Moves Cognitive Clarity / Clear Seeing Books brand (Zen-coded) from Joshin to Kenjin.
- Updates Joshin's teacher card + doctrine to full Shingon grounding per `docs/research/shingon_buddhism_research_2026-05-18.md`.
- Migrates 4 Joshin STORY atoms (Zen-explicit) to Kenjin; in-place rewrites 2 atoms with single Zen-word swaps.
- Renames 132 book_plans + 44 series_plans (`cognitive_clarity__joshin__*` → `cognitive_clarity__kenjin__*`).
- Pearl_News surfaces unchanged (Joshin already correct as Shingon).
- New Joshin Shingon-coded brand + new Joshin atoms are out-of-scope for this PR (follow-up commission per §6.B of the migration plan).

## Plan
Full migration plan: `docs/migrations/JOSHIN_SHINGON_KENJIN_ZEN_MIGRATION_PLAN_2026-05-18.md`

## Risks
1. Cognitive Clarity brand identity is deeply Zen-coded (enso, "Clear Seeing", "Zen inquiry for the modern mind") — moving it wholesale to Kenjin preserves brand integrity. Operator confirmed.
2. 6 Clear Seeing Books authors with Zen-coded bios move with the brand.
3. Visual iconography on Joshin's existing cover/portrait/manga assets MAY be Zen-coded (enso, rakusu, zen garden). Re-render gated per §5.C.

## Test plan
- [ ] `scripts/ci/run_register_gate.py` passes.
- [ ] `scripts/ci/run_scorecard.py` passes — Kenjin scoring block valid, Joshin scoring block Shingon-coded.
- [ ] Smoke run of one Kenjin book completes end-to-end with Zen voice.
- [ ] `grep -rln "zen\|Zen\|zazen\|koan" SOURCE_OF_TRUTH/teacher_banks/joshin/approved_atoms/` returns 0 hits.
- [ ] `grep -rln "shingon\|Shingon\|mikkyo\|sanmitsu\|ajikan\|dainichi" SOURCE_OF_TRUTH/teacher_banks/kenjin/approved_atoms/` returns 0 hits.
- [ ] Catalog visibility index regenerated and contains Kenjin entries.
- [ ] Pearl_News pipeline unchanged — Joshin Shingon articles still publish.
```

---

## 5. Risk register

### 5.A Operator-decision-required ambiguities

#### 5.A.1 **(P0 — CRITICAL)** Cognitive Clarity brand routing — Joshin retains, or Kenjin takes?

Cognitive Clarity / Clear Seeing Books is Joshin's currently-bound brand. Its identity is explicitly Zen:

- tagline "Zen inquiry for the modern mind"
- colophon "Enso circle (single brush stroke, open at top)"
- tradition statement "Zen Buddhism — direct pointing, dropping the story, pure heart"
- 6 authors with Zen-coded bios
- title family ("The Clear Pause", "Past the Loop", "After the Spiral") that is Zen-tonal
- illustration style "Stark Zen Ink"
- 44 series plans + 132 book plans authored in zen-ink, direct-pointing register
- 8 manga series profiles + 3 cogclar_jp series profiles
- Manga character `joshin_sensei` with supporting cast `kenji_analyst`, `mira_skeptic`, `old_librarian` (note: `kenji_analyst` is unrelated to Kenjin Roshi by accident — same root verb 見 but the supporting-character `kenji` predates this migration)

**Three options:**

- **Option A — Joshin keeps Cognitive Clarity, all Zen content within is rewritten to Shingon.** Highest content cost (rewrite 176 plans + 8 profiles + 6 author bios + brand copy). Brand identity drift (Clear Seeing Books → Mandala Press? Lineage Press?). **NOT recommended** — Cognitive Clarity's market angle ("zen inquiry, dropping the story") IS its product-market fit. Trashing it is value-destructive.
- **Option B — Joshin keeps Cognitive Clarity, the brand quietly rebrands as "Shingon-flavored mind-clarity."** Some content survives (psychological observations are tradition-neutral), but every "zen" word and every enso must be replaced. Brand fidelity loss is medium. **NOT recommended** — produces a Shingon-but-Zen-flavored-Frankenstein.
- **Option C — Cognitive Clarity stays Zen, MOVES from Joshin to Kenjin. Joshin gets a NEW Shingon-coded brand.** Preserves the Zen brand wholly. New work for Joshin (a Shingon brand) is the right addition. **RECOMMENDED.** This is what the rest of this migration plan assumes.

**Operator decision needed before §2-§4 execution.**

#### 5.A.2 **(P1)** Shingon sub-school for Joshin

Recommend **Kōyasan Shingon-shū** (Kogi branch, headquartered at Kongōbu-ji, Mt. Kōya). Reasons per research §1.3 / §8.1. Alternatives: Tō-ji Shingon-shū (Kyoto, urban), Buzan-ha / Chizan-ha (Shingi branch). **Default Kōyasan unless operator overrides.**

#### 5.A.3 **(P1)** Kenjin's gender + cultural background

Recommend **male, late 50s, Japanese-American (Kyoto-born, Bay Area decades)**. Provides clean differentiation from Joshin (Japanese-American female) and matches the existing Clear Seeing Books author voices. **Operator can override.**

#### 5.A.4 **(P1)** Brand admin Joshin = "Still Forest / Forest meditation" framing

`config/brand_management/teacher_brand_map.yaml:228-249` and 13 instances in `config/brand_management/global_brand_registry.yaml` map joshin to brand `still_forest` with tradition "Forest meditation / nature connection". This **is itself drift** — not Zen, not Shingon, but third-axis drift. Recommend reconcile to Shingon-grounded framing ("Mount Kōya forest training, ajari-led contemplative stillness"). **Operator-decision item: reconcile in this PR, or flag for separate follow-up?**

#### 5.A.5 **(P2)** Author roster — keep all 6 Clear Seeing Books authors with Kenjin, or curate?

The 6 authors (Ada Park, Joel Crane, Hana Lee, Marcus Stone, Yuki Tanabe, Elliot Vane) have Zen-coded bios. They migrate wholesale with the brand to Kenjin under option (c). Operator may wish to (i) keep all 6, (ii) keep a subset, (iii) author new Shingon-coded authors for Joshin's new brand simultaneously. Recommend (i) for this PR; (iii) is the Phase D step 18 commission.

### 5.B Operational risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Catalog visibility index regen produces orphaned Kenjin entries** if Phase I runs before Phase C completes | M | M | Run Phase I LAST; assert Kenjin entries count matches expected. |
| **Pearl_News test fixture breaks** because Kenjin not in news_roster (per OPD-105 he is NOT in news) but some tests assume "all teachers in registry have news roster entry" | M | L | Audit `pearl_news/config/teacher_news_roster.yaml` — Kenjin should NOT appear there. Update any test that asserts roster ⊆ registry to use `pearl_news_eligible: true` flag instead. |
| **Push-guard blocks** because PR is multi-subsystem (teachers + catalog_planning + manga + brand_management + docs) | H | L | Per CLAUDE.md §"PR size", expect a warning on >3 subsystems but not a block. If block, split into atomic sub-PRs (registry-only → catalog-routing → docs-cleanup). |
| **Catalog reproducibility lost** if 132 book_plans get rewritten in place rather than `git mv`'d | L | M | Use `git mv` to preserve filename + content history. Sed for the in-file teacher_id update. |
| **Renaming a YAML file that's referenced by an absolute path elsewhere** breaks downstream | M | M | Before each `git mv`, grep for the OLD filename across the entire repo; update any reference. Example: each series_plan filename appears in 3 book_plans' `series_plan:` field. |

### 5.C Visual iconography risks (per the user's brief — manga panels & cover art)

| Asset | Currently Zen-coded? | Action |
|---|---|---|
| `brand-wizard-app/public/teacher_pics/joshin.png` | Visual review needed — if enso / rakusu / zen-garden iconography visible, this becomes a Kenjin asset | Re-render Joshin for Shingon (suggest vajra in hand, moon-disk visualization scroll behind, or Kōyasan cedar background); migrate current portrait to Kenjin if appropriate |
| `brand-wizard-app/public/assets/manga_covers/joshin_{cover_anxiety, cover_depression, cover_overthinking, portrait, scene, symbolic, profile, front, three_quarter}.png` | Likely yes (cognitive_clarity Stark Zen Ink style) | Migrate to Kenjin; re-render for Joshin |
| `brand-wizard-app/public/assets/covers/cover_joshin_anxiety.png` and KDP variants | Likely yes | Migrate to Kenjin; re-render for Joshin |
| `brand-wizard-app/public/assets/manga_panels/joshin/page_{001..NNN}.png` | Likely yes | Migrate to Kenjin; re-render new Shingon-coded panels for Joshin |
| `brand-wizard-app/public/assets/video/manga/joshin.mp4`, `tiktok/joshin_burnout_tiktok.mp4` | Likely yes | Migrate to Kenjin; re-render for Joshin (defer per §6.B) |
| `brand-wizard-app/public/teacher_showcase/joshin__chapter_1.html` | Probably tradition-tagged | Audit and split — Kenjin gets the Zen chapter, Joshin gets new Shingon chapter |

**Shingon iconography swap-in cheat-sheet (for new Joshin renders):**

- Replace enso → **moon-disk (gachirin) with lotus + Siddham A** (Ajikan visualization)
- Replace rakusu/kesa → **monk's robe with kasaya plus visible vajra (kongōsho) or rosary (juzu)**
- Replace kyosaku stick → **incense holder, goma fire-pit, or sutra scroll**
- Replace empty zen garden → **Kōyasan cedars, Okunoin stone lanterns, or two-mandala wall hanging**
- Replace generic Japanese temple bell → **conch (horagai) + drum (taiko)** (Shingon ritual ensemble)

### 5.D Cross-reference and marketing copy drift

| Surface | Risk |
|---|---|
| Existing public KDP listings for Joshin's Cognitive Clarity books (if any were published with the Zen-coded copy) | If books have shipped, **DO NOT re-render** automatically — these are now Kenjin-attributed under the migration. Operator decision: leave shipped books as historical Kenjin-attributed, or pull and re-render? Recommend: leave (they are test artifacts per OPD-20260518-102 noting Blind-10 was internal). |
| `MANGA_STRATEGIC_AUDIT_VERDICT.md:56, 151, 213` | Marketing/audit copy references Joshin's "direct-pointing method" as a brand differentiator. After migration this is Kenjin's, not Joshin's. UPDATE the file. |
| `artifacts/research/teacher_market_validation_matrix_2026_04_04.md`, `webtoon_*.md` | Historical research with Joshin = Zen claims. APPEND a 2026-05-18 update header per Phase G step 31. |
| Pearl_News articles already published (2026-04-19, 2026-04-22) under Joshin | These were correctly Shingon. RETAIN. |

---

## 6. Backout plan

### 6.A Per-step rollback

Because the migration is in atomic phases:

- **If register-gate fails post-merge:** `git revert <merge-commit-sha>` is sufficient. The teacher registry and atoms revert as a unit.
- **If a specific scorecard issue surfaces (e.g., Kenjin topic_scores produce a regression in one persona):** apply a follow-up patch tweaking Kenjin's persona_scores block in `config/catalog_planning/teacher_topic_persona_scores.yaml` rather than reverting the whole PR.
- **If operator rejects a routing decision (e.g., Cognitive Clarity should NOT have moved to Kenjin):** revert Phase C and Phase D, then re-author per chosen option. Phase A + Phase B + Phase G (Joshin's Shingon doctrine, atom rewrites, docs) STAY — they are correct independently of routing.

### 6.B Out-of-scope follow-up commissions

These items are explicitly NOT executed in this migration PR; they are downstream gated commissions:

1. **Joshin Shingon-coded brand authoring** — new brand name + identity + colophon + tagline + 6+ new authors. Pearl_Architect + Pearl_Brand + Pearl_Editor commission. ~2-3 sessions of work. Gated on §5.A.1 operator decision.
2. **Joshin new Shingon atom authoring** — 12 STORY + 12 EXERCISE + 12 SCENE atoms grounded in research §3 / §6.3. Pearl_Editor + Pearl_Writer commission. ~3-4 sessions.
3. **Visual asset re-render for Joshin** (Shingon iconography) — Pearl_Prime visual pipeline commission via Pearl Star. ~1 day of operator-attended render time.
4. **Pearl_Video pilot regeneration** if `joshin / cognitive_clarity / ja-JP` pilot was Zen-coded — the pilot was locked to joshin per `docs/PEARL_ARCHITECT_STATE.md:1254-1338`. If pilot art/script is now Kenjin-attributed, regenerate. Pearl_Video commission.
5. **Audiobook prose regen** `artifacts/audiobook_samples/_prose/joshin_anxiety_ch1.txt` — Pearl_Writer commission, Shingon framing.

### 6.C Emergency revert checklist (if production catalog breaks)

```bash
# 1. Identify the migration merge SHA
git log --oneline | grep "joshin-shingon-kenjin-zen-migration"

# 2. Revert
git revert <merge-sha>

# 3. Regen catalog visibility (the index is computed; revert restores source)
python3 scripts/catalog/build_catalog_visibility.py

# 4. Push to a recovery branch (NOT main directly)
git checkout -b recovery/revert-joshin-kenjin-migration
git push -u origin recovery/revert-joshin-kenjin-migration

# 5. Open a PR for the revert; tag the operator for sign-off
gh pr create --title "revert: joshin-shingon-kenjin-zen migration (operator request)" \
  --body "Reverting migration PR #<num> per operator emergency request."

# 6. After merge, restore Joshin's doctrine.yaml additions IF they were the only-good-piece-of-this-PR
git show <migration-sha>:SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml > \
  SOURCE_OF_TRUTH/teacher_banks/joshin/doctrine/doctrine.yaml
```

---

## 7. Appendix — quick reference

### 7.1 Zen drift wordlist (for grep audits)

These must NOT appear in Joshin's atoms or doctrine post-migration (per research §4.3):

```
zen Zen zazen Zazen koan kōan shikantaza satori kenshō kensho
mu dokusan roshi Roshi shoshin beginner's mind enso
"direct pointing" "just sitting" "sound of one hand" "original face"
"pure heart" "dropping the story"
```

### 7.2 Shingon vocabulary whitelist (for Joshin atoms post-migration)

Per research §4.1:

```
shingon mikkyō Mikkyo Dainichi Nyorai Mahāvairocana Mahavairocana
Kōbō Daishi Kobo Daishi Kūkai Kukai Kōyasan Koyasan
sanmitsu sokushin-jōbutsu sokushin jobutsu kaji Ajikan ajikan
mudrā mudra inkei hokkai-jō-in chi-ken-in
goma kanjō kanjo kechien-kanjō ajari mandara
Taizōkai Taizokai Kongōkai Kongokai
Hannya Shingyō Bussetsu Kōmyō Shingon Komyo Shingon
gohōgō gohogo "Namu Daishi Henjō Kongō" "dōgyō ninin" dogyo ninin
henro shukubō Fudō Myōō Fudo Myoo rokudai honpushō honpusho
gachirin shuji susokukan shido kegyō
```

### 7.3 Kenjin (Zen) vocabulary whitelist

Per research §7 + Sōtō-specific:

```
zazen shikantaza kinhin oryoki kōan koan satori kenshō kensho
mu dokusan roshi sensei oshō shoshin
zafu zabuton kesa rakusu kyosaku
Dōgen Dogen Eihei-ji Bodhidharma Mu Mon Kan Hekiganroku
enso Genjō Kōan Genjo Koan Shōbōgenzō Shobogenzo
shinjin-datsuraku buji zen mu-shotoku
```

### 7.4 Files inventory regen command

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/musing-lewin-4a91a3
grep -rln "joshin\|Joshin" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | sort > /tmp/joshin_files.txt
wc -l /tmp/joshin_files.txt   # expect 549 ± as files get touched
```

---

**End of migration plan.**

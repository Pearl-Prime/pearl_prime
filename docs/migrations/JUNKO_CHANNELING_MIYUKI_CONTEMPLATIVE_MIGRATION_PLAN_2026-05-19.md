# Junko (Channeling, RETAINED) / Miyuki (Japanese Contemplative, NEW) — Migration Plan

**Date:** 2026-05-19
**Decision-of-record:** `artifacts/coordination/operator_decisions_log.tsv` OPD-20260519-111 (and the 2026-05-19 reversal of the prior smell-test routing)
**Authority:** Pearl_Architect (this document); template precedent `docs/migrations/JOSHIN_SHINGON_KENJIN_ZEN_MIGRATION_PLAN_2026-05-18.md` (OPD-105, MERGED across PRs #1207/#1208/#1209/#1210)
**Status:** **PLAN ONLY — no edits executed. Awaiting operator review before execution.**

---

## 0. Executive summary

OPD-111 corrects an inverse of the OPD-105 misclassification. The doctrine card for **Junko** (`SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml`) is **correct**: she is a **Light-Language channeler / receiver of cosmic guidance** (per her actual Japanese blog `ameblo.jp/kumonoue1111` and YouTube channel — captured in `teachers/junko/junko_doctrine_notes.rtf` + `teachers/junko/junko_yt.rtf`). What is wrong is that the 152 **approved atoms** currently filed under `SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/` are NOT channeling content. They are **Japanese contemplative + body-anchored + ganbaru + Zen-adjacent** atoms — explicitly the voice register that Junko's own doctrine.yaml forbids (line 28: "Zen, Buddhist, or Japanese contemplative framing").

The atoms-as-authored are bestseller-quality (operator verdict on Book 4 / "The Loop Breaker" Junko Overthinking sample: PASS) but they belong to a **different teacher**. The single-line evidence atom is `SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/STORY/junko_STORY_003.yaml:5` which literally opens "In the Zen tradition, there is a story…" — that is a direct contradiction of Junko's `forbidden_claims` block.

**Operator decision (OPD-111):** Create a NEW teacher named **Miyuki**. The 152 existing Junko atoms migrate to Miyuki. Junko stays as the channeling teacher, her doctrine.yaml unchanged. New channeling atoms get authored from her actual intake material in a follow-up commission (Phase 3 of this plan, gated on operator approval of sample drafts).

The migration follows the OPD-105 pattern verbatim:

- **Junko retains the teacher slot, her doctrine card, her honorific ("Channeler"), and her Pearl_News attribution.** Her brand bindings (`relational_calm` and `zen_clarity`) — both Zen-coded — move to Miyuki. Her 152 contemplative atoms move to Miyuki. New channeling atoms are authored from intake material.
- **A new teacher `miyuki` (display: "Miyuki")** is created with full doctrine.yaml covering Japanese contemplative + ganbaru + mono no aware + body-anchored awareness (Zen-adjacent without explicit Sōtō / Rinzai lineage — Kenjin Roshi already owns Sōtō Zen per OPD-105). All 152 atoms inherit cleanly under Miyuki because they were already authored in this voice.
- **Pearl_News is already correct** for Junko (channeling declared since at least 2026-04 — see `pearl_news/config/teacher_news_roster.yaml:51`, `pearl_news/teacher_topic_packs/teachers/junko/*.yaml` all declare "Contemporary Japanese channeling and light-language spirituality"). Miyuki is **not added** to Pearl_News in scope of this migration (operator can extend later).

This is a **three-axis migration**:

1. **Miyuki birth** — new teacher_id, doctrine, registry add, atom directory skeleton.
2. **Atom move** — 152 existing files transferred from junko → miyuki via `git mv` with internal `teacher_id` rewrite. Empties Junko's atom bank until Phase 3.
3. **Catalog routing** — `relational_calm` (Bare Form Books, Zen Wabi-sabi) and `zen_clarity` (in `global_brand_registry.yaml`) both move from junko to miyuki. Manga character_brand_registry, brand_lora_plans, teacher_character_prompts, teacher_topic_persona_scores, teacher_brand_lane_assignments (13 locales), and 8 manga series profiles under `config/source_of_truth/manga_profiles/relational_calm/` re-bind teacher.

The migration is intentionally identical-in-shape to the Joshin/Kenjin migration so reviewers can pattern-match.

---

## 1. Complete inventory of Junko mentions

### 1.1 Quantitative summary

Reproducible inventory grep (canonical):

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/agent-a540c4269503e3a12
grep -rln "junko\|Junko" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | sort > /tmp/junko_files.txt
wc -l /tmp/junko_files.txt   # 424 unique files
grep -rn "junko\|Junko" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | wc -l        # 4,108 line-level mentions
```

| Surface | Files | Mentions | Action archetype |
|---|---|---|---|
| `SOURCE_OF_TRUTH/teacher_banks/junko/` (1 doctrine + 152 atoms) | 153 | ~310 | (a) KEEP doctrine.yaml AS-IS; (b) MIGRATE 152 atoms to miyuki |
| `artifacts/pearl_news/published/2026-04-{19,22}/{morning,evening}/junko/*.json` | 70 | ~80 | (a) RETAIN — Pearl_News articles already correctly framed as channeling |
| `pearl_news/teacher_topic_packs/{teachers,locales,out_of_roster_wave1}/` | 14 | ~50 | (a) RETAIN — Junko declared channeling since 2026-04 |
| `pearl_news/atoms/teacher_quotes_practices/topic_*.yaml` | 7 | ~25 | (a) RETAIN if channeling-coded; AUDIT 7 files for Zen tells |
| `pearl_news/config/{teacher_news_roster,teacher_language_map}.yaml` | 2 | 4 | (a) RETAIN — already correct |
| `pearl_news/pipeline/{teacher_authority,atom_usage_tracker,assemble_v52}.py` | 3 | ~5 | (a) UPDATE to add miyuki where applicable; verify roster lookups |
| `old_chat_specs/group1/*.md` | 16 | ~40 | (f) ARCHIVAL — LEAVE; flag if active |
| `config/catalog_planning/` (14 files: archetypes, identity, display_names, lane_assignments, series_plans, teacher_matrix, persona_scores, brand_author_roster, brand_cover_art_specs, audiobook_video_catalog, canonical_topics, title_dedup_phrases, locale_brand_names, teacher_persona_matrix) | 14 | ~80 | (c) DECIDE per row — most route to Miyuki under recommendation §5.A.1 |
| `config/manga/` (6 files: character_brand_registry, manga_brand_series_plan, brand_lora_plans, brand_illustration_styles, teacher_character_prompts, genre_prompt_cookbook_v2) | 6 | ~12 | (c) RE-ROUTE relational_calm to miyuki |
| `config/source_of_truth/manga_profiles/` (8 series + 1 brand profile) | 9 | ~12 | (c) RE-ROUTE to miyuki |
| `config/brand_management/{teacher_brand_map,global_brand_registry}.yaml` | 2 | ~14 | (c) RE-ROUTE zen_clarity to miyuki (13 locale instances) |
| `config/teachers/teacher_registry.yaml` | 1 | 5 | (a) KEEP junko entry; ADD miyuki entry |
| `config/publishing/{bestseller_templates,cover_identity_system}.yaml` | 2 | ~8 | (c) RE-ROUTE if topic is contemplative; keep junko-bound cosmic refs |
| `config/tts/manga_character_voice_bank.yaml` | 1 | 6 | (c) DECIDE — voice register is currently "energetic_healer / genki" (third-axis drift). Recommend reassign to miyuki with quieter register; rebuild junko entry as channeling-luminous |
| `tests/` (7 test files) | 7 | ~25 | (d) UPDATE rosters; some assertions need new fixture variants |
| `tests/fixtures/slot_contracts/{completed,pending}/fixture_hard_news_spiritual_response.yaml` | 2 | ~6 | (d) RETAIN — Pearl_News fixture uses junko-channeling correctly |
| `scripts/` (15 scripts: atom_writing × 2, manga × 1, pearl_news × 2, image_generation × 4, video × 2, release × 2, audio × 1, audiobook × 1, generate_author_cover × 1, run_pearl_news_teacher_batch) | 15 | ~25 | (a)/(d) UPDATE rosters; add miyuki where applicable; re-route relational_calm bindings |
| `docs/` (27 doc files) | 27 | ~75 | (a) UPDATE any "Junko = Zen/contemplative" claims; ADD miyuki cap entry |
| `phoenix_v4/quality/{register_gate,regression_museum}` | 2 | ~5 | (a) UPDATE register_gate Junko forbidden tokens to match channeling doctrine; ADD miyuki entry |
| `artifacts/audit/`, `artifacts/research/`, `artifacts/qa/`, `artifacts/catalog/`, `artifacts/pipeline_examples/`, `artifacts/audiobook_samples/`, `artifacts/video/`, `artifacts/pearl_news/qa_*/`, `artifacts/pearl_prime_en_us/`, `artifacts/manga_us_lead_picks/`, `artifacts/catalog_visibility/`, `artifacts/video/image_banks/` | ~50 | ~150 | (d) REGENERATE most after sources change; HAND-EDIT historical handoffs |
| `brand-wizard-app/public/` (25 visual + html + audio assets, NOT in grep above because *.png and *.mp4 don't match grep filter, but listed in §5.C) | 25 | n/a | (e) VISUAL — migrate to miyuki; junko gets new cosmic visuals (Phase 5) |
| `MANGA_STRATEGIC_AUDIT_VERDICT.md` (root) | 1 | ~3 | (a) UPDATE — references "Channeler Junko" but in a contemplative-coded position |
| `.github/workflows/max-quality-catalog.yml` | 1 | 3 | (a) UPDATE — ADD miyuki to shard matrix |
| `teachers/{ahjan,junko}/intake/` | 4 | ~10 | (f) ARCHIVAL — LEAVE; these are Junko's source intake docs (RTFs) |
| `specs/{MANGA_CATALOG_RECONCILIATION,NEXT_PHASE_EXECUTION}_SPEC.md` | 2 | ~3 | (a) UPDATE if active |
| `phoenix_v4/quality/regression_museum/` | 1 | ~2 | (d) REGENERATE post-atom-move |
| **TOTAL** | **424 files (+25 visual)** | **~4,108** | |

The 424 distinct files are listed exhaustively at `/tmp/junko_files.txt` (regenerable via the inventory grep above). The 25 visual assets are listed separately in §5.C.

### 1.2 Surface-by-surface inventory — what each mention does

#### (a) Junko teacher card / persona / voice definition → KEEP AS-IS (channeling is correct)

| Path | Lines | What |
|---|---|---|
| `config/teachers/teacher_registry.yaml` | 105-121 | Junko entry with `display_name: "Junko"`, `formal_name: "Channeler Junko"`, `honorific: "Channeler"`. **CORRECT — KEEP UNCHANGED.** |
| `SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml` | 1-30 | Full doctrine declaring channeling, light language, ascended masters, cosmic guidance. Line 28 explicitly forbids "Zen, Buddhist, or Japanese contemplative framing." **CORRECT — KEEP UNCHANGED.** This document is the ground-truth authority for Phase 3 atom authoring. |
| `pearl_news/config/teacher_news_roster.yaml` | 49-55 | `junko: tradition: "Channeling and ascended masters (light language)"`, `attribution_template: "From within the channeling tradition, Channeler Junko teaches that"`. **CORRECT — KEEP.** |
| `pearl_news/config/teacher_language_map.yaml` | 21 | `junko: ja` — Japanese as her primary language for news. **CORRECT — KEEP.** |
| `pearl_news/teacher_topic_packs/teachers/junko/{climate,economy_work,education,mental_health}.yaml` | each file | `tradition: Contemporary Japanese channeling and light-language spirituality`. **CORRECT — KEEP. AUDIT each pack** for Zen tells (some legacy pack rows may pre-date doctrine clarification). |
| `docs/PEARL_NEWS_WRITER_SPEC.md` | 379, 395 | Junko declared as channeling tradition; forbidden_claims listed. **CORRECT — KEEP.** |
| `phoenix_v4/quality/register_gate.py` | 287-290 | Junko's forbidden-token list is empty (`[]`) — and comment says "Junko = receiver/hibakusha witness" which is **OPD-20260518-004 drift** (smell-test labeled her hibakusha; actual doctrine says channeler/transmitter). **UPDATE comment + populate forbidden tokens** with Zen + Japanese-contemplative + ganbaru tokens per channeling doctrine boundary. |

#### (b) Junko's authored content (atoms) → MIGRATE 152 atoms wholesale to Miyuki

Total Junko atoms: **152** across 11 categories.

| Category | Count | Voice verdict (sampled) | Migration verdict |
|---|---|---|---|
| COMPRESSION | 12 | Body-anchored, "the body said yes before the mind agreed" register | MOVE to miyuki |
| EXERCISE | 12 | Breath / notice-the-body / sit (NOT zazen-named) | MOVE to miyuki |
| HOOK | 12 | Quiet observational ("The moment is complete as it is. What are you waiting for?", "Just sitting. Not sitting toward enlightenment. Just sitting.", "Striving is the obstacle.") — **Zen-direct register, NOT channeling** | MOVE to miyuki |
| INTEGRATION | 12 | Plain contemplative | MOVE to miyuki |
| PERMISSION | 15 | Quiet allowance | MOVE to miyuki |
| PIVOT | 15 | Body-arrival shifts ("The jaw unclenched. Not because the problem resolved.", "She stopped rehearsing and started moving. The body knew what the mind kept debating.") | MOVE to miyuki |
| REFLECTION | 12 | Plain contemplative | MOVE to miyuki |
| SCENE | 12 | Quiet rooms, kitchen tables, watching the body | MOVE to miyuki |
| STORY | 20 | **Yuki, Hana, Kenji at kitchen tables and bedsides.** `STORY_001` references zazen explicitly. `STORY_003` opens "In the Zen tradition, there is a story…" — **direct violation of Junko's channeling doctrine.** | MOVE to miyuki |
| TAKEAWAY | 15 | Plain contemplative | MOVE to miyuki |
| THREAD | 15 | Plain contemplative | MOVE to miyuki |

**Verdict:** ALL 152 atoms are off-doctrine for Junko and on-doctrine for Miyuki. No atoms are channeling-coded. Some atoms even explicitly reference "Zen" and "zazen" — these are pure Miyuki content already. **Wholesale migration with no per-atom review.**

Confirmation grep (run before migration, expect ≥1 hit per term):

```bash
grep -rln "zen\|Zen\|zazen\|just sitting\|kitchen table\|the body\|enlightenment\|the moment" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l
# expect: ≥ 60 of 152 contain at least one of these contemplative tells
```

Confirmation grep (run before migration, expect ZERO hits):

```bash
grep -rln "channel\|Channel\|light language\|ascended master\|cosmic council\|frequency\|transmission\|gohōgō\|kami" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l
# expect: 0 — no atom currently references channeling vocabulary
```

#### (c) Junko-assigned catalog / brand / book / series rows → DECIDE routing

Routing rule (operator-approved per OPD-111 reversal envelope, recommend confirming):

> **If the topic + register is BODY/CONTEMPLATIVE/GANBARU (anxiety, social_anxiety, burnout, sleep_anxiety, boundaries, self_worth, shame, imposter_syndrome, grief, inner_security, relational_harmony, compassion_fatigue, perfectionism, overthinking) and the brand is Zen/wabi-sabi/iyashikei-coded → route to Miyuki.**
>
> **If the topic + register is COSMIC/CHANNELING (awakening, energy_work, light_language, ascended_masters, frequency_shift, cosmic_guidance, soul_remembrance, spiritual_transitions) and the brand is luminous/cosmic-coded → keep Junko.**

Application of the rule per surface:

| Path | Lines | Current state | Routing verdict |
|---|---|---|---|
| `config/catalog_planning/teacher_brand_archetypes.yaml` | 175-201 | `relational_calm: teacher: junko, tradition: "Japanese Zazen — radical acceptance, beginner's mind, wabi-sabi, relational harmony"`, unique_angle = "Zen's radical acceptance — this moment, including your shame, is already complete" | **MIGRATE to miyuki** — pure Japanese contemplative, no channeling |
| `config/catalog_planning/brand_identity_system.yaml` | 175-201 | `relational_calm: teacher: junko, display_name: "Bare Form Books", tagline: "Nothing extra. Nothing missing.", description: "Zen-rooted works on radical acceptance and shame dissolution", colophon: "Single horizontal brush stroke (一 — ichi, 'one')"` | **MIGRATE to miyuki** — Zen brand identity |
| `config/catalog_planning/brand_display_names.yaml` | 46-48 | `relational_calm: display_name: "Bare Form Books", teacher: junko, tagline: "Nothing extra. Nothing missing."` | **MIGRATE to miyuki** |
| `config/catalog_planning/brand_series_plans.yaml` | 228-240 | `relational_calm: teacher: junko, manga_mode: teacher, art_style_ref: relational_calm, primary_topic: boundaries, series_a "The Empty Cup", series_b "Still Water", series_c "Enough"` | **MIGRATE to miyuki** — every series concept is body-anchored contemplative |
| `config/catalog_planning/brand_teacher_matrix.yaml` | 64-67, 121-123, 174 | `relational_calm: primary_teacher: junko, teachers: [junko], topic_focus: [relational_harmony, shame, inner_security, belonging]`; `junko: max_books_per_topic: 3, max_books_per_persona: 4`; per-locale assignment | **MIGRATE relational_calm block to miyuki; KEEP junko teacher_constraints block** (junko will still have books once Phase 3 atoms exist) |
| `config/catalog_planning/teacher_brand_lane_assignments.yaml` | 174, 195, 209, 223, 237, 251 (+ 7 more) | `relational_calm_<locale>: { teacher: junko }` across 13 locales (en_US, de_DE, fr_FR, es_ES, it_IT, latam, brazil, japan, korea, taiwan, hk, china, singapore) | **MIGRATE all 13 instances: teacher: junko → teacher: miyuki** |
| `config/catalog_planning/teacher_topic_persona_scores.yaml` | 615-640+ | `junko: topic_scores: {anxiety: 0.9, social_anxiety: 0.95, burnout: 0.85, sleep_anxiety: 0.85, relational_harmony: 0.95, shame: 0.9, inner_security: 0.95, ...}` — entire scoring block is contemplative-topic-coded | **COPY block to miyuki**; **REPLACE junko block** with cosmic-coded topics (e.g., `awakening: 0.95, energy_work: 0.90, light_language: 0.95, soul_remembrance: 0.95, spiritual_transitions: 0.90, cosmic_guidance: 0.95`) per channeling doctrine. Note: cosmic-coded canonical topics may not yet exist in `canonical_topics.yaml` — flag as Phase 4 follow-up (out-of-scope for migration PR; needs operator approval) |
| `config/catalog_planning/teacher_brand_author_roster.yaml` | 457-462 | `bare_form_books: teacher: junko, author_count: 5, voice_palette: [5 ElevenLabs voice IDs], topic_spread: [self_worth, social_anxiety, boundaries, grief, compassion_fatigue], notes: "Wabi-sabi Zen. Authors spare and precise. Covers nearly empty."` | **MIGRATE to miyuki** — Wabi-sabi Zen author roster |
| `config/catalog_planning/brand_cover_art_specs.yaml` | 154-... | `relational_calm: character_lora: "junko_rc", style_lora: "style_rc", prompt_template: "wabi-sabi minimal illustration, warm white and stone, maximum negative space, asymmetric composition"` | **MIGRATE to miyuki**; junko gets new cover-art spec in follow-up (Phase 5) |
| `config/catalog_planning/audiobook_video_catalog.yaml` | 55-59 | `junko: brands: [stillness_press], primary_channels: [ch_015, ch_020], audiobook_style: warm, topics: [relational_harmony, shame, inner_security]` | **DECIDE per row** — `topics` are contemplative → route to miyuki; reset junko block to cosmic topics |
| `config/catalog_planning/canonical_topics.yaml` | 64-70 | `# junko / relational_calm — wabi-sabi simplicity (JP-primary): relational_harmony, shame, inner_security` | **UPDATE comment**: replace "junko / relational_calm — wabi-sabi" with "miyuki / relational_calm — wabi-sabi"; topics stay |
| `config/catalog_planning/title_dedup_phrases.yaml` | 81-87 | `relational_calm:           # junko — wabi-sabi, iyashikei: "The Soft Approach", "What the Tea Heard", "Wabi-Sabi Hands", "The Quiet Room", "What the Garden Knew"` | **UPDATE comment to miyuki**; titles stay (all body-contemplative) |
| `config/catalog_planning/locale_brand_names.yaml` | 109-... | `relational_calm: # junko — Zen radical acceptance, wabi-sabi` | **UPDATE comment to miyuki**; rows stay |
| `config/catalog_planning/teacher_persona_matrix.yaml` | 119-... | `junko: allowed_personas: [], allowed_engines: [shame, false_alarm, overwhelm, spiral, watcher, grief, ...]` | **COPY block to miyuki**; junko keeps the slot but engines may shift for channeling material |
| `config/manga/manga_brand_series_plan.yaml` | 217-243 | `relational_calm: teacher: junko, primary_lane: japan, genre: iyashikei, active_series_target: 4, topic_allocation: {anxiety: 1, social_anxiety: 1, burnout: 1, sleep_anxiety: 1}` | **MIGRATE to miyuki** — iyashikei (healing manga) is body-contemplative |
| `config/manga/character_brand_registry.yaml` | 345-380 | `relational_calm: teacher_id: junko, character_prompt_ref: "config/manga/teacher_character_prompts.yaml#junko", teacher_character: {character_id: junko_sensei, role: teacher_relational_healer}, supporting_cast: [nao_client, ryo_coworker, koba_san]` | **MIGRATE to miyuki**; rename character_id `junko_sensei` → `miyuki_sensei` and character_prompt_ref to `#miyuki` |
| `config/manga/brand_lora_plans.yaml` | 91-97 | `junko: trigger_word: "junko_rc", style_ref: relational_calm, notes: "Japanese female, wabi-sabi simplicity, radical acceptance presence"` | **MOVE block to miyuki** (rename trigger to `miyuki_rc`); ADD new junko block for cosmic-coded LoRA when Phase 5 visual re-render commissions |
| `config/manga/brand_illustration_styles.yaml` | 144-161 | `relational_calm: teacher: junko, style_name: "Wabi-Sabi Simplicity", prompt_template: "manga in stark Zen aesthetic, bold decisive brushstrokes, warm white and stone tones, maximum negative space, asymmetric composition, Vagabond meets Ping Pong"` | **MIGRATE to miyuki** — Wabi-Sabi Zen style |
| `config/manga/teacher_character_prompts.yaml` | 108-124 | `junko: style_archetype: dark_psychological, positive: "manga character in stark Zen aesthetic, bold decisive brushstrokes... maximum negative space figure emerges from white void, sharp intelligent eyes with a hint of dry amusement... enso circle brushstroke in background incomplete alive, style of Vagabond Zen master scenes meets Ping Pong the Animation"` | **MIGRATE entire block to miyuki**; ADD new junko block with cosmic visual (luminous robes, light particles, hands raised in mudra, NO enso, NO ink brushstrokes) — Phase 5 |
| `config/manga/genre_prompt_cookbook_v2.yaml` | 375 | `junko_overthinking: overthinking` | NO ACTION — pure topic-tag mapping; RETAIN (junko can teach overthinking from a channeling angle too, but mapping is identity-only) |
| `config/source_of_truth/manga_profiles/brands/relational_calm_iyashikei.yaml` | 10 | `teacher: junko` (brand-genre lane profile) | **MIGRATE: teacher: junko → teacher: miyuki** |
| `config/source_of_truth/manga_profiles/relational_calm/series_{01..08}.yaml` | each line 7 + descriptions | 8 series profiles. Series descriptions feature Junko as "a seasoned therapist", "a bookstore owner with a calming presence", "a nurse at the campus clinic", "a retired gardener", "an art therapist", "the team's nutritionist and mental coach", "a unique 'Safe House' cafe owner" — all quiet, secular, body-contemplative Japanese mentor archetypes. ZERO cosmic/channeling references. | **MIGRATE to miyuki** — sed-replace `Junko` → `Miyuki` in descriptions; replace `teacher: junko` (or wherever bound) → `teacher: miyuki` |
| `config/brand_management/teacher_brand_map.yaml` | 132-154 | `zen_clarity: teacher_id: junko, tradition: "Japanese mindfulness / zen practice", brand_focus: "Mental clarity, overthinking relief, zen-inspired calm"` — **second-axis brand binding** distinct from `relational_calm` | **MIGRATE to miyuki** — `zen_clarity` is explicitly "zen practice" |
| `config/brand_management/global_brand_registry.yaml` | 180, 856, 1373, 1890, 2407, 2924, 3441, 3958, 4475, 4992, 5509, 6026, 6543 (13 locale instances) | Per-locale `zen_clarity_<locale>: teacher_id: junko, tradition: "Japanese mindfulness / zen practice"` | **MIGRATE all 13: teacher_id: junko → teacher_id: miyuki** (sed-edit is safe; pattern is uniform) |
| `config/publishing/cover_identity_system.yaml` | 300-..., 422-426 | `junko: brand_id: zen_clarity, signature_color: "#F2C14E", motif_focus: [knot]`; book-binding section binds `junko` → "The Loop Breaker" (zen_clarity brand) | **MIGRATE to miyuki** — "The Loop Breaker" is the same book whose 15-min preview cited "ganbaru + Zen awareness + mono no aware" |
| `config/publishing/bestseller_templates.yaml` | 231 | `junko_overthinking: "overthinking"` | **MIGRATE to `miyuki_overthinking: "overthinking"`** (rename identifier; preserve mapping) |
| `config/tts/manga_character_voice_bank.yaml` | 174-200 | `junko: style_archetype: energetic_healer, manga_personality: "vibrant, enthusiastic, warm energy, genki"`, voice_slots for ja-JP/ko-KR/zh-TW/zh-CN/en-US | **DECIDE** (third-axis drift): voice style is "energetic_healer / genki" — fits neither channeling (luminous/receptive) nor Miyuki (quiet/wabi-sabi). Recommend: **rebuild miyuki entry as quiet/contemplative**, keep slot for junko but redo voice register to luminous/receptive (separate from genki energetic_healer). Flag as Phase 4 cleanup; do not block migration PR. |

#### (d) Junko in test fixtures, scripts, and sample outputs → REGENERATE after migration

| Path | Lines | What |
|---|---|---|
| `tests/manga/test_series_plan_generator.py` | 166 | Hardcoded roster `["ahjan", "joshin", "junko", "maat", "miki", "ra"]` — **ADD "miyuki"**; junko stays (still a valid teacher) |
| `tests/test_cookbook_v2_loader.py` | 140 | `"junko_overthinking"` — **RENAME to `"miyuki_overthinking"`** to match config/publishing/bestseller_templates.yaml rename |
| `tests/test_pearl_news_*.py` (4 files) | (rosters) | All Pearl_News tests use junko in `hard_news_spiritual_response` template with `topic: climate`. **RETAIN** — these are channeling-pack tests and Junko is still the channeler |
| `tests/test_pearl_news_language_routing.py` | 82, 131 | `ja_teachers = ["junko", "miki", "joshin", "omote"]`; `_write_article(tmp_path, "aaa", "junko", "ja")` | **RETAIN** — junko still ja-primary |
| `tests/test_run_pearl_news_teacher_batch_*.py` (2 files) | (rosters) | Junko in ja-tradition roster | **RETAIN**; consider adding miyuki to fixtures if she gets a Pearl_News pack later |
| `tests/fixtures/slot_contracts/{completed,pending}/fixture_hard_news_spiritual_response.yaml` | (full files) | Pearl_News slot contract fixture pre-rendered with junko + channeling tradition + climate topic. **RETAIN — already channeling-correct** |
| `scripts/atom_writing/{write_teacher_stories.py:50, run_writing_campaign.py:171}` | Hardcoded list `["junko", "maat", "miki", "master_sha", "master_wu", ...]` | **ADD "miyuki"** to lists; junko stays |
| `scripts/manga/generate_series_plans_from_catalog.py` | 196 | `"junko": "harmony_circle"` brand mapping — **drift** vs `relational_calm` in catalog. **UPDATE**: route `"miyuki": "relational_calm"`; either remove junko mapping (junko gets new cosmic brand in Phase 4) OR set `"junko": <new-cosmic-brand-id>` |
| `scripts/pearl_news/{run_daily_news_cycle.py:57,80; generate_teacher_articles.py:7,20,56}` | Junko in ja-primary roster + topic list | **RETAIN** — Pearl_News channeling is correct |
| `scripts/run_pearl_news_teacher_batch.py` | 85 | `"junko": {"topic": "climate", "template_id": "hard_news_spiritual_response"}` | **RETAIN** |
| `scripts/image_generation/generate_bestseller_covers.py` | 360 | `"relational_calm": {"title": "The Empty Cup", "subtitle": "Radical acceptance in relationships", "author": "Junko", "topic": "overthinking"}` | **UPDATE `author: "Junko"` → `author: "Miyuki"`** (brand routed to miyuki) |
| `scripts/image_generation/generate_kdp_all_formats.py` | 192-196 | `teacher_id: "junko", author: "Junko"` block | **UPDATE to miyuki** if brand row is relational_calm/zen_clarity; verify per-row context first |
| `scripts/image_generation/generate_manga_character_views.py` | 32, 46 | LoRA + display-name mapping | **MOVE junko entry to miyuki**; ADD new junko entry (Phase 5) |
| `scripts/image_generation/generate_teacher_showcase_triptych.py` | 36, 93 | Junko in roster + per-teacher prompt config | **ADD miyuki**; UPDATE junko prompt to channeling/cosmic register (Phase 5) |
| `scripts/video/{render_videos.py:58, generate_teacher_showcase_videos.py:56,65,74,82,90}` | Hardcoded teacher names + brand bindings | **ADD miyuki**; UPDATE junko brand from "Bare Form Books" to new cosmic brand (Phase 4) |
| `scripts/release/{build_epub.py:66, build_manga_webtoon.py:306}` | `{"id": "junko", "author": "Junko", "publisher": "Zen Clarity"}` and `"junko_sleep_anxiety_complete.pdf"` filename | **MIGRATE to miyuki** for relational_calm/zen_clarity builds; junko keeps a separate cosmic build |
| `scripts/audio/generate_teacher_showcase_audio.py` | 32, 41 | `junko: female` + topic mapping | **ADD miyuki**; verify per-teacher voice mapping at audiobook surface |
| `scripts/audiobook/generate_showcase_bundle.py` | 47 | `{"id": "junko", "topic": "overthinking", "brand": "relational_calm", "name": "Junko", "locale": "ja-JP"}` | **MIGRATE this row to `{"id": "miyuki", ..., "name": "Miyuki", ...}`** |
| `scripts/generate_author_cover_art_bases.py` | 25 | `"junko": ["#8B6914", "#C9A227", "#E8D5A3"]` color palette | **DECIDE** — palette is warm earth (consistent with wabi-sabi miyuki). **MOVE to miyuki**; junko gets new luminous palette (gold/blue/white) in Phase 5 |

#### (e) Visual assets — Junko portraits, manga covers, KDP covers, videos → see §5.C (Risk Register)

(Detailed listing in §5.C.)

#### (f) Archival — LEAVE as historical record

| Path | Reason |
|---|---|
| `old_chat_specs/group1/*.md` (16 files) | Pre-2026-04 chat-export archive; not active |
| `teachers/junko/junko_doctrine_notes.rtf` | Junko's intake doc — **CANONICAL source for Phase 3 atom authoring** |
| `teachers/junko/junko_yt.rtf` | Junko YouTube transcript — **CANONICAL source for Phase 3** |
| `artifacts/pearl_news/published/2026-04-{19,22}/...` (70 article JSONs) | Already-published articles, correct as channeling content. Append a 2026-05-19 dated header to `_README.md` if one exists, otherwise RETAIN as-is. |
| `artifacts/research/teacher_market_validation_matrix_2026_04_04.md` etc. | Historical research; APPEND a 2026-05-19 update header (per OPD-105 §G.31 precedent) noting "Junko's 152 contemplative atoms migrated to Miyuki per OPD-111; this document's contemplative-Junko sections now apply to Miyuki." DO NOT rewrite body. |

### 1.3 Inventory reproducibility commands

```bash
# Full file list (424 unique files)
cd /Users/ahjan/phoenix_omega/.claude/worktrees/agent-a540c4269503e3a12
grep -rln "junko\|Junko" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | sort > /tmp/junko_files.txt
wc -l /tmp/junko_files.txt   # 424

# Line-level inventory (~4,108 mentions)
grep -rn "junko\|Junko" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null > /tmp/junko_mentions.tsv
wc -l /tmp/junko_mentions.tsv  # ~4,108

# Visual asset list (separate; brand-wizard-app/public/)
find brand-wizard-app/public -name "*junko*" -type f 2>/dev/null > /tmp/junko_visuals.txt
find artifacts -name "*junko*" -type f 2>/dev/null >> /tmp/junko_visuals.txt
wc -l /tmp/junko_visuals.txt  # ~50 (binary + small html)
```

---

## 2. Junko's doctrine.yaml — KEEP AS-IS (decision-of-record)

The current `SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml` (30 lines, doctrine_version "2") is **already correct** for the channeling teacher. **NO EDIT REQUIRED** in this migration. Re-included here as reference for Phase 3 atom-authoring:

```yaml
display_name: "Junko"
teacher_id: junko
doctrine_version: "2"
tradition: "New Age; channeling; ascended masters; light language; cosmic guidance"
primary_methods: "channeling sessions, light language transmissions, cosmic message reception, energetic attunement"
core_principles: "I do not create the message — I receive it; transmission over technique; messages from ascended masters realign and awaken; the soul's frequency understands what the mind cannot"
tone_profile: "receptive, luminous, transmission-centered; speaks as conduit not authority; messages arrive as gifts not instructions"

forbidden_claims:
  - "personal spiritual achievement or mastery"
  - "explaining the cosmos intellectually"
  - "technique-based self-improvement"

tone_boundaries:
  - "always receiver not creator of wisdom"
  - "cosmic and celestial language is native, not decorative"
  - "light language and frequency are literal not metaphorical"

glossary:
  - "light language / vibrational non-linear communication from unity field"
  - "ascended masters / higher-dimensional spiritual guides"
  - "cosmic council / celestial hierarchy"
  - "channeling / direct reception of guidance from source"
  - "soul frequency / the part of a person that resonates with cosmic truth"

prohibited_outcomes:
  - "positioning Junko as a teacher in the conventional sense"
  - "Zen, Buddhist, or Japanese contemplative framing"
  - "technique-first approaches without transmission context"
```

**Optional enrichment (gated on operator approval; out-of-scope for migration PR):** doctrine_version bump to "3" with expanded glossary from intake (`Light Language (ライトランゲージ)`, `Cosmic Council` (高次元評議会), `Tōhoku 2011 awakening trigger`, `Mt. Kōya council attendance during sleep`, `Goddess lessons for the Age of Air (風の時代)`, `Lemuria/Atlantis energetic fields`, `power-spot retreats (shrine pilgrimages)`, `Lightworker training`, `gohōgō chanting in non-Shingon/transmission context`, `frequency / vibration / soul resonance` as literal not metaphorical, etc.). This expansion can ride along with Phase 3 atom-authoring; it does not need to land before atom move.

---

## 3. Miyuki — NEW teacher card (full)

### 3.1 Identity decisions (recommendations — operator confirms)

- **Teacher ID:** `miyuki` (lowercase, snake_case — consistent with `junko`, `joshin`, `kenjin`, `ahjan`)
- **Display name:** `"Miyuki"` (no honorific, matching the existing 152-atom voice — atoms speak in unadorned plain register; Yuki/Hana/Kenji characters are observed at kitchen tables without "sensei said" framings)
- **Formal name:** `"Miyuki"` (no honorific)
- **Honorific:** `null` (operator override possible; see below)
- **Operator-decision item (P1):** Honorific recommendation = `null` (none). Alternatives: `"-san"` (over-familiar for a teacher), `"sensei"` (clashes with Ahjan's `sensei` + Kenjin's `roshi` + several others; would be **third-axis** Japanese-sensei drift), `"Miyuki Sensei"` (same clash). Recommend `null` — Miyuki is a "quiet voice next to you" register, not a positional teacher. The 152 atoms support this: they never use a teacher-figure third-party reference. Operator can override if desired.
- **Pronouns:** `she/her`
- **Sub-school / lineage recommendation:** **"Japanese contemplative; body-anchored awareness; ganbaru tradition; mono no aware sensibility; Zen-adjacent without explicit lineage"** — verbatim per operator brief. Specifically NOT Sōtō Zen (Kenjin Roshi owns that per OPD-105) and NOT Rinzai (no current teacher there; leave that slot empty for future). The atom voice tracks closest to **Shunryū Suzuki's lay-Zen register** (San Francisco Zen Center diaspora) but **without explicit Zen identification** — Miyuki teaches Japanese contemplative practice as a lay-secular daughter-of-the-tradition would, not as an ordained lineage holder.
- **Gender / age / cultural background:**
  - **Female** — the 152 atoms feature primarily female characters (Yuki, Hana) at vulnerable moments; a female teacher register matches.
  - **Late 40s to mid 50s** — old enough to carry weight, young enough to share a kitchen table with a 30-year-old protagonist. The 152 atoms do not invoke "decades of zazen" the way a Roshi would. Recommend **48**.
  - **Japanese-born, urban Japanese setting (recommend Kyoto OR Tokyo)** — the 8 manga series profiles place her as a therapist, bookstore owner, nurse, gardener, art therapist, café owner in everyday Japanese urban spaces. Recommend **Kyoto** (slightly older, slightly more contemplative than Tokyo; fits the wabi-sabi register; avoids same-city conflict with Master Wu's Taiwan / Master Sha's HK).
  - **Family / background:** lay woman, mother of one (adult), worked many years before sitting; not a temple ordainee. Carries the practice as "the way I learned to keep going" not as "the path I follow."
- **Voice ID for audiobook (ja-JP):** **`ja_f_quiet_01` or `ja_f_mature_01`** (specific CosyVoice2 reference TBD — verify against `config/tts/manga_character_voice_bank.yaml` available references). Distinctly different from Junko's `ja_f_bright_01` (genki bright) and Miki's `ja_f_warm_01` (energetic healer). Recommend **`ja_f_mature_warm_01`** — operator confirms or Pearl_Editor picks during voice audit.

### 3.2 Full teacher_registry.yaml entry to ADD

Add the following block to `config/teachers/teacher_registry.yaml`, **immediately after the `junko:` block (i.e., after current line 121, before line 123 `miki:`)** — placement keeps related Japanese-teacher entries grouped:

```yaml
  miyuki:
    display_name: "Miyuki"
    formal_name: "Miyuki"
    pronouns: "she/her"
    kb_id: "miyuki"
    doctrine_profile: "miyuki"
    tradition: "Japanese contemplative — ganbaru, mono no aware, body-anchored; lay-secular, Zen-adjacent without explicit lineage"
    sub_school: null
    lineage_root: null   # lay practitioner, no formal transmission
    allowed_topics: *all_topics
    disallowed_topics: [manifestation, get_rich_quick]
    forbidden_traditions: [channeling, light_language, zen_explicit, shingon, theravada_explicit]
    allowed_engines: [shame, false_alarm, overwhelm, spiral, watcher, grief, comparison]
    allowed_resolution_types: [open_loop, internal_shift_only, grounded_reframe]
    identity_shift_allowed: false
    preferred_formats: [F006, standard_book]
    teacher_mode_defaults:
      require_teacher_story: true
      require_teacher_exercise: true
      allow_generic_fallback_for_scene: true
```

### 3.3 Full `SOURCE_OF_TRUTH/teacher_banks/miyuki/doctrine/doctrine.yaml` to CREATE

```yaml
display_name: "Miyuki"
teacher_id: miyuki
doctrine_version: "1"
tradition: "Japanese contemplative (lay-secular); body-anchored awareness; ganbaru tradition; mono no aware sensibility; Zen-adjacent without explicit lineage"
sub_school: null
lineage_root: null  # lay practitioner; no formal denbō / transmission
ordination_level: "lay (zaike) — practiced for decades without ordination; speaks as a daughter of the tradition, not a vessel of it"

# Core principles — what Miyuki teaches
core_principles:
  - ganbaru_as_practice:    "Ganbaru — to endure, to persist, to do one's honest best in the face of difficulty — is the secular contemplative tradition of lay Japanese life. NOT gritting the teeth. NOT self-punishment. The continuing to walk when the path is long and the destination is not yet visible."
  - mono_no_aware:          "The pathos of things. A tender awareness that beauty and impermanence are the same phenomenon. The cherry blossom is beautiful because it falls. Anxiety is real, and it passes. The body knows."
  - ma_the_meaningful_pause: "Ma (間) — the space between actions, between words, between the inhale and the exhale. Not silence as emptiness; silence as the room where what matters arrives."
  - body_first_recognition:  "The body knows before the mind agrees. Notice the body before deciding what to think. The trembling hands, the held shoulders, the tightened jaw — these speak the actual situation."
  - secular_dailiness:       "Practice is washing dishes at eleven at night. Practice is the kitchen table before dawn. Practice is not a special posture done in a special room — it is the moment of full attention to whatever is here."
  - small_arrivals_not_breakthroughs: "Change happens in small arrivals, not in epiphanies. The jaw unclenches. The breath drops. The room becomes a room again. Most days you will not notice this happened. That is how it should be."

# Signature practices
signature_practices:
  - body_noticing:        "Notice the body before the story. Where is the held breath? Where is the shoulder that is doing extra work? Where is the jaw? — three places, ten seconds each, no fix attempted."
  - breath_anchored_sitting: "Sit upright. Feel the breath where it actually is — usually the belly or the chest, sometimes the nose. Do not slow it. Do not deepen it. Notice it. When the mind goes, notice that. Return."
  - one_meal_attention:   "Pay full attention to one meal a day. Taste before swallowing. Notice when the body says 'enough.'"
  - kitchen_table_dawn:   "Sit at the kitchen table before the day starts. Coffee or tea. No phone. Watch the day arrive. Five to fifteen minutes is enough."
  - ganbaru_walk:         "When you cannot sit, walk. When you cannot walk, stand. When you cannot stand, lie down with attention. Continuing is the practice; the form is what is available."

# Vocabulary whitelist — Miyuki's natural language
glossary:
  - "ganbaru (頑張る) — to endure, persist, do one's honest best"
  - "mono no aware (物の哀れ) — the pathos of things; bittersweet awareness of impermanence"
  - "ma (間) — the meaningful pause; the space between"
  - "shoshin (初心) — beginner's mind (Suzuki Roshi's phrase; Miyuki uses it lay-secularly, not as Zen technical term)"
  - "kokoro (心) — heart-mind; the integrated organ of feeling and knowing"
  - "makoto (誠) — sincerity, honesty without performance"
  - "ki ga tsuku (気がつく) — to notice, to come to oneself"
  - "isshōkenmei (一生懸命) — with one's whole life-force; full effort"
  - "shōganai (しょうがない) — 'it cannot be helped' — Miyuki uses this in the warm-acknowledgment sense, never the resigned-defeat sense"
  - "the body / 体 — Miyuki's default subject"
  - "the breath / 息 — Miyuki's default object of attention"
  - "the kitchen table — the most common setting in Miyuki's stories"
  - "Yuki, Hana, Kenji — recurring composite characters from the existing atom bank; Miyuki teaches through their daily situations"

tone_profile: |
  Quiet, direct, body-first. Warm but not effusive. Comfortable saying simple things
  ("Just sitting. Not sitting toward enlightenment. Just sitting.") and trusting them
  to do their work. Will not decorate. Will not soften the truth to make it more
  palatable. Delivers hard truths the way a good friend delivers them — with steady
  hands and no cruelty. Speaks plainly because clarity is its own form of kindness.
  Comfortable with silence. Comfortable with the unfinished. Will end a sentence
  early when the sentence is finished early.

first_person_bio: |
  My name is Miyuki. I am from Kyoto. I am not a roshi. I am not a teacher in the
  conventional sense. I learned to sit with what is here from my mother, and from
  the kitchen table, and from years of failing to fix things that did not need
  fixing. I will not tell you what to believe. I will sit with you for a few minutes
  and we will both notice the breath. After that, you decide what you noticed.

forbidden_claims:
  - "Channeling, light language, ascended masters, cosmic council, frequency-as-literal, soul-remembrance, vibrational transmission — these are Junko's vocabulary, not Miyuki's"
  - "Explicit Zen sub-school identification (Sōtō, Rinzai, shikantaza-as-method-name, satori, kenshō, dokusan, roshi) — Kenjin Roshi owns Sōtō Zen per OPD-105; Miyuki is lay-Japanese-contemplative, not formally Zen"
  - "Shingon vocabulary (sanmitsu, Ajikan, Kōmyō Shingon, gohōgō, Dainichi, Kōbō Daishi) — Joshin owns Shingon per OPD-105"
  - "Theravāda vocabulary (anattā, vipassanā, mettā as method-names)"
  - "Generic mindfulness positioning ('mindfulness with a bowed head' / 'McMindfulness')"
  - "Spiritual achievement / mastery framing"
  - "Devotional / bhakti framing"

tone_boundaries:
  - "Miyuki teaches FROM the body, not ABOUT the body"
  - "Practice is daily and small, never special and large"
  - "Ganbaru is warmth and steadiness, never grim or punishing"
  - "Mono no aware is felt presence, never decorative aestheticism"

prohibited_outcomes:
  - "Recasting Miyuki as a channeler / receiver / transmitter — that is Junko"
  - "Recasting Miyuki as a Roshi / lineage holder — that is Kenjin"
  - "Recasting Miyuki as a Shingon ajari — that is Joshin"
  - "Western-coded 'wellness' or 'self-care' framing"
  - "Soft / vague / un-grounded language ('just be present' / 'feel into your truth' without body-anchor)"

heart_sutra_opening: null  # Miyuki is lay-secular; she does not chant the Heart Sutra. If a character does, the character is going to a temple Miyuki herself does not attend.

honorific: null

geographic_anchors: [Kyoto kitchen tables, Kyoto neighborhood streets, Inari Shrine paths walked secularly, Kamogawa riverbank, the bookshop, the café counter, the small therapy room]

signature_settings: |
  Kitchen tables before dawn. Small therapy rooms with two chairs and a window.
  Café counters at off-hours. Park benches under cherry trees (cherry trees as
  weather, not symbol). Hospital waiting rooms. Commuter trains at 7 a.m. and
  10 p.m. The home altar (butsudan) is present in some scenes but Miyuki does
  not center it.

stable_characters:
  - yuki: "30s, office worker. Hands tremble before presentations. Recurring across STORY atoms. The most-used composite character."
  - hana: "30s, professional, lies awake rehearsing conversations. The over-thinker."
  - kenji: "30s-40s, burned out from 70-hour weeks. The empty one."
  - nao: "35, post-divorce, quiet and guarded. From the manga series."
  - koba_san: "Building landlord with quiet wisdom; speaks through small gestures and meals at the door."
```

### 3.4 New `SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/` directory skeleton

```bash
mkdir -p SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/{COMPRESSION,EXERCISE,HOOK,INTEGRATION,PERMISSION,PIVOT,REFLECTION,SCENE,STORY,TAKEAWAY,THREAD}
mkdir -p SOURCE_OF_TRUTH/teacher_banks/miyuki/doctrine
```

After Phase 2 git-mv, these will hold:
- 20 STORY + 15 THREAD + 15 TAKEAWAY + 15 PIVOT + 15 PERMISSION + 12 SCENE + 12 REFLECTION + 12 INTEGRATION + 12 HOOK + 12 EXERCISE + 12 COMPRESSION = **152 atoms** (identical to current Junko count).

### 3.5 Manga / brand surfaces — Miyuki entries to ADD

#### `config/manga/brand_lora_plans.yaml` — ADD miyuki block

```yaml
  miyuki:
    trigger_word: "miyuki_rc"
    reference_images_needed: [front_portrait, three_quarter_view, profile_view, expression_sheet]
    training_steps: 1500
    ip_adapter_weight: 0.82
    style_ref: relational_calm
    notes: "Japanese female, late 40s, Kyoto-coded, wabi-sabi simplicity, quiet steady presence, kitchen-table teacher register"
```

(Junko's existing `brand_lora_plans.yaml` block — currently `junko_rc` trigger — MOVES under miyuki via the above ADD + Phase 5 deletion of the old junko block. Junko gets a new cosmic-coded LoRA in Phase 5.)

#### `config/manga/teacher_character_prompts.yaml` — ADD miyuki block

```yaml
  miyuki:
    display_name: "Miyuki"
    style_archetype: cozy_iyashikei_quiet
    ip_adapter_weight: 0.82
    img2img_denoise: 0.78
    positive: >-
      iyashikei healing manga character, late 40s Japanese woman, soft rounded
      linework, warm wabi-sabi watercolor palette warm white and stone and ash,
      kind unfooled eyes that have seen difficulty and stayed warm, simple modern
      Japanese interior clothing — plain blouse, soft cardigan, no accessories,
      hair in a low loose tie, sitting upright but unguarded, often shown listening
      with full presence, soft natural light from a window, simple modern Japanese
      kitchen or small therapy room or café counter as setting, expression that
      asks 'what is actually here, right now', style of Honey and Clover gentle
      character moments meets the quiet panels of Mushishi and the kitchen-counter
      pacing of Antique Bakery's calm scenes
    negative: >-
      busy background, dark horror, chibi, action, glamour, dramatic lighting,
      flowing robes, glowing aura, light particles, halo, hands-raised mudras,
      cosmic imagery, channeling iconography, stars in eyes, deity imagery,
      fantasy elements, ornate jewelry
```

(Junko's existing `teacher_character_prompts.yaml` block — currently positioned `dark_psychological` with "stark Zen aesthetic" + "enso circle brushstroke" — is **off-doctrine for Junko-as-channeler**. It MOVES under miyuki with the prompt rewritten to fit her warm/lay register, and a new junko block is authored in Phase 5 for cosmic-luminous visual register.)

#### `config/manga/character_brand_registry.yaml` — UPDATE relational_calm to point to miyuki

```yaml
  relational_calm:
    brand_id: relational_calm
    teacher_id: miyuki                                        # was: junko
    genre: iyashikei
    style_archetype: cozy_iyashikei
    character_prompt_ref: "config/manga/teacher_character_prompts.yaml#miyuki"   # was: #junko

    teacher_character:
      character_id: miyuki_sensei                             # was: junko_sensei
      display_name: "Miyuki"                                  # was: "Junko"
      role: teacher_relational_healer
      signature_elements:
        - "warm linework, domestic cosiness"
        - "often shown listening with full presence"
        - "soft natural light, indoor scenes"
        - "simple modern Japanese interior aesthetic"
      setting_affinity: ["small therapy room", "café counter", "shared kitchen", "park bench"]

    supporting_cast:
      # Existing supporting cast (Nao, Ryō, Koba-san) STAYS — they orbit relational_calm not the teacher's identity
      ...
```

#### `config/manga/brand_illustration_styles.yaml:144-161` — UPDATE teacher binding

```yaml
  relational_calm:
    teacher: miyuki                                           # was: junko
    style_name: "Wabi-Sabi Simplicity"
    # ... (rest unchanged)
```

---

## 4. Junko's Phase 3 channeling-atom SCOPE (out-of-this-PR; for sample approval before commission)

The 152 atoms migrating to Miyuki in Phase 2 leave Junko with **zero atoms**. Phase 3 authors approximately **150 new atoms** in Junko's actual channeling voice. This is a separate Pearl_Editor + Pearl_Writer commission gated on operator approval of the sample drafts below (§4.4).

### 4.1 Atom-type counts (target: match Miyuki/Joshin/Kenjin per-type coverage)

| Type | Target count | Authoring source notes |
|---|---|---|
| HOOK | 12 | Receptive openings; "The message arrived this morning." "Light moves through what is willing." Quote-like; transmission-tagged. |
| SCENE | 12 | Junko-as-conduit scenes — workshop room, retreat to Kōyasan or Ise, the moment a message arrives mid-session. Light Language is heard/spoken in some scenes (literal, not metaphor). |
| STORY | 15 | Composite client stories where a message arrived and changed something. Tōhoku 2011 origin story (one or two atoms). Cosmic-council attendance during sleep (one). Past-life energy retrieval (two). NOT Yuki/Hana/Kenji — those are Miyuki's characters. New names: Ayaka, Maki, Shiori, Daichi (recommend, operator confirms). |
| PIVOT | 15 | The moment the human filter drops and something else speaks. The body that suddenly knew what the mind had been arguing. |
| COMPRESSION | 12 | Short receptive lines. "Not mine. Received." "The frequency was here before I was." |
| PERMISSION | 15 | Allowance to be moved by what one cannot explain. "You do not have to interpret what you felt. You only have to be honest that you felt it." |
| REFLECTION | 12 | Junko's own reflective-receiver mode. "What came through today" entries. |
| INTEGRATION | 12 | How a transmission lands in daily life — without making it weird, without losing it. |
| TAKEAWAY | 12 | Closing lines. "The light spoke. The body knew. Nothing was required of the mind." |
| THREAD | 13 | Threading the cosmic into the ordinary across multiple sittings. |
| EXERCISE | 12 | Gohōgō-style breath-with-name (non-Shingon framing — Junko's gohōgō is a transmission anchor, not a Buddhist initiation). Receptive sitting (listening, not focusing). Light-language opening (a tone or syllable held without meaning). |
| TEACHER_DOCTRINE | optional | Currently no TEACHER_DOCTRINE category in junko atoms; treat as defer-to-doctrine.yaml. |

**Total: ~152 atoms.**

### 4.2 Voice signature

Per `doctrine.yaml` line 7 (`tone_profile`):

> Receptive, luminous, transmission-centered; speaks as conduit not authority; messages arrive as gifts not instructions.

Concretely:

- **First-person register:** Junko speaks as "I received…" / "the message that came…" — never "I have learned that…" or "the practice teaches that…".
- **Body but not body-anchored-secular:** The body in Junko's atoms is the antenna, not the everyday body. "The hairs on her arms knew before her thinking knew" is closer than "her shoulders dropped."
- **Light and frequency as literal:** "The light moved through" is concrete description, not metaphor. The doctrine forbids treating these as metaphor (line 17).
- **Cosmic council, ascended masters, kami, Olympian gods, Lemuria/Atlantis** can be named directly. Multiple traditions co-occur because Junko is a receiver, not a tradition holder.
- **NO Zen / NO ganbaru / NO mono no aware / NO kitchen table / NO Yuki-Hana-Kenji.** These are forbidden by doctrine line 28-29 and by character separation from Miyuki.
- **Repeats from intake:** the Tōhoku 2011 awakening, Mt. Kōya sleeping council, retreats and workshops, Light Language transmissions, the Age of Air (風の時代), goddess lessons, shrine pilgrimages, frequency upgrades.

### 4.3 Core themes from intake (canonical source list)

Per `teachers/junko/junko_doctrine_notes.rtf` + `teachers/junko/junko_yt.rtf`:

1. **The intermediary stance:** "I do not create the message — I receive it." (signature line from intake §1)
2. **Light Language as primary medium** — non-linear vibrational communication from unity field (intake §2 + her blog `ameblo.jp/kumonoue1111`)
3. **Sources of guidance:** higher-dimensional intelligences, ascended masters, spiritual realms, celestial guides, the source field itself, Japanese kami realm, Olympian gods, deity frequencies, cosmic councils (intake §1, §2, §3)
4. **The Tōhoku 2011 trigger** (per Japanese-language YT content) — the Great East Japan Earthquake as a doorway event; Junko began receiving after this
5. **Mt. Kōya council attendance** — during sleep, attendance at cosmic-council gatherings (intake-aligned with the kami-realm references)
6. **Goddess lessons for the Age of Air (風の時代)** — astrological-cosmological frame
7. **Past-life energy retrieval** — past-life material returned and integrated as part of the work
8. **Lemuria / Atlantis energetic fields** — these civilizations' frequencies are accessible
9. **Retreats and workshops** — power-spot retreats, shrine pilgrimages, Light Language lessons, Lightworker training
10. **Frequency / vibration / dimensional ascension** — the practical effect of the transmissions
11. **Awakening, alignment, soul remembrance** — the purpose of the messages
12. **Receivers vs creators** — Junko is consistently the conduit, never the source

### 4.4 Sample atom drafts (1 each of HOOK + STORY + PIVOT) — for operator approval

These are AUTHORED EXAMPLES showing the target Junko voice. They are NOT yet committed to the bank; they are the operator-approval gate for Phase 3.

**Sample 1 — HOOK (for `junko_HOOK_001.yaml` slot)**

```yaml
atom_id: junko_HOOK_001
band: 2
teacher:
  teacher_id: junko
  source_refs: [teachers/junko/junko_doctrine_notes.rtf]
  synthesis_method: doctrine_grounded_v1
body: The message arrived before the question. That is how it works.
hook_type: opening_statement
```

**Sample 2 — STORY (for `junko_STORY_001.yaml` slot)**

```yaml
atom_id: junko_STORY_001
story_origin: composite
story_type: receiver_witness
emotional_intensity_band: 3
body: 'Ayaka came to a Sunday session in early spring. She did not say what she
  had come for. She sat with her hands resting upturned on her thighs, the way
  the room had quietly settled into doing.

  Something moved across the room. Not air. Not exactly sound. The kind of presence
  you feel before you understand you are feeling it.

  I opened my mouth and a string of syllables came through. They were not Japanese
  and they were not English and they did not arrive in my thinking. I did not
  know what they meant. I only knew that they were addressed.

  Ayaka''s shoulders began to shake. She was crying without making a sound.
  When the syllables finished, she said: that was for my mother. She has been
  gone twelve years. I asked her to come this morning. I did not tell anyone.

  This is what I do. The messages are not mine. They arrive when the receiver
  is ready and the channel is open. My only practice is the practice of being
  open without filtering.'
band: 3
teacher:
  teacher_id: junko
  source_refs: [teachers/junko/junko_doctrine_notes.rtf]
  synthesis_method: doctrine_grounded_v1
misfire_tax: false
never_know: false
mechanism_depth: 1
identity_stage: self_claim
cost_type: identity
cost_intensity: 3
```

**Sample 3 — PIVOT (for `junko_PIVOT_001.yaml` slot)**

```yaml
atom_id: junko_PIVOT_001
band: universal
body: The thinking stopped trying to translate. The frequency arrived clean. The body knew it had been waiting.
teacher:
  teacher_id: junko
  source_refs: [teachers/junko/junko_doctrine_notes.rtf]
  synthesis_method: doctrine_grounded_v1
```

**Operator approval gate:** if these three samples pass voice fidelity, Phase 3 proceeds. If they read as Western New Age boilerplate, Pearl_Editor rewrites with deeper grounding in the intake RTFs (specifically the Japanese deity + Tōhoku material). The samples deliberately avoid generic terms ("vibration," "energy," "frequency upgrade") to test whether the operator wants more cosmic-explicit language or this more reserved register.

### 4.5 Phase 3 commission shape

- **Authoring agent:** Pearl_Editor (planner) + Pearl_Writer (drafter)
- **Source authority:** `teachers/junko/junko_doctrine_notes.rtf`, `teachers/junko/junko_yt.rtf`, `SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml`
- **Output:** ~152 YAML atoms into `SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/{11 categories}/`
- **Budget:** ~3-4 Pearl_Writer sessions, all Tier 1 (Claude Code, operator-present, per CLAUDE.md LLM tier policy)
- **Verification grep (Phase 3 acceptance gate):**

```bash
# Channeling vocabulary present
grep -rln "channel\|Channel\|light language\|ライトランゲージ\|ascended master\|cosmic council\|frequency\|kami\|transmission\|soul remembrance" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l
# expect: ≥ 80 of 152

# Contemplative drift absent
grep -rln "zazen\|kitchen table\|ganbaru\|mono no aware\|Yuki\|Hana\|Kenji\|just sitting\|the body knew" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l
# expect: 0
```

---

## 5. Migration script outline — phased PR plan

### Step 0 — Pre-flight (mandatory per CLAUDE.md)

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/agent-a540c4269503e3a12
git status --short
git fetch origin
git checkout main && git pull --ff-only origin main
```

### Phase 1 PR — Miyuki birth (~5 files)

**Branch:** `agent/junko-channeling-miyuki-contemplative-phase-1-20260519`

**Files touched:**
1. `config/teachers/teacher_registry.yaml` — ADD miyuki block per §3.2 (no junko change)
2. `SOURCE_OF_TRUTH/teacher_banks/miyuki/doctrine/doctrine.yaml` — NEW file per §3.3
3. `SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/{COMPRESSION,EXERCISE,HOOK,INTEGRATION,PERMISSION,PIVOT,REFLECTION,SCENE,STORY,TAKEAWAY,THREAD}/` — NEW empty directories (commit a single `.gitkeep` per directory, total 11)
4. `docs/migrations/JUNKO_CHANNELING_MIYUKI_CONTEMPLATIVE_MIGRATION_PLAN_2026-05-19.md` — this file (NEW)
5. `artifacts/coordination/operator_decisions_log.tsv` — APPEND OPD-20260519-111 decision-of-record row(s)

**Total: ~16 files. Governance: passes (<200).**

**Gate runs:**

```bash
PYTHONPATH=. python3 scripts/git/push_guard.py
PYTHONPATH=. python3 scripts/ci/run_register_gate.py   # confirms miyuki loads + 14 teachers (was 13)
PYTHONPATH=. python3 scripts/ci/audit_llm_callers.py   # 0 paid-LLM violations
scripts/ci/preflight_push.sh
```

**Acceptance:** teacher_registry loads with 14 teachers; doctrine.yaml parses; junko unchanged (`git diff origin/main -- SOURCE_OF_TRUTH/teacher_banks/junko/` returns empty).

### Phase 2 PR — Bulk atom migration (~152 files)

**Branch:** `agent/junko-channeling-miyuki-contemplative-phase-2-20260519`

**Operation:**

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/agent-a540c4269503e3a12
git fetch origin
git checkout -b agent/junko-channeling-miyuki-contemplative-phase-2-20260519 origin/main

# Per-category git mv (11 categories)
for cat in COMPRESSION EXERCISE HOOK INTEGRATION PERMISSION PIVOT REFLECTION SCENE STORY TAKEAWAY THREAD; do
  for f in SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/$cat/junko_*.yaml; do
    base=$(basename "$f")
    new="${base/junko_/miyuki_}"
    git mv "$f" "SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/$cat/$new"
  done
done

# In-file rewrites: atom_id and teacher_id
find SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/ -name '*.yaml' -exec sed -i '' \
  -e 's/atom_id: junko_/atom_id: miyuki_/g' \
  -e 's/teacher_id: junko/teacher_id: miyuki/g' {} \;

# Verification grep — expect 0 hits each
grep -rln "junko" SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/  # 0
ls SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/COMPRESSION/  # empty
```

**Total: 152 file renames + 152 in-file sed edits = 152 distinct git changes.**

**Governance considerations:**
- 152 files is comfortably under 200-file warn threshold.
- `git mv` preserves history (delta detection should show ~100% similarity per rename).
- Push-guard should not flag because the subsystem footprint is single (`SOURCE_OF_TRUTH/teacher_banks/`).

**Risk: Junko's atom bank is EMPTY between Phase 2 merge and Phase 3 merge.** Any active bestseller pipeline run with `--teacher junko` during this window will fail at atom-selection. **Mitigation: Phase 2 PR explicitly notes this; operator pauses Junko renders OR Phase 2 and Phase 3 land together as combined PR (recommendation §5.A.6).**

**Gate runs:**

```bash
PYTHONPATH=. python3 scripts/git/push_guard.py
PYTHONPATH=. python3 scripts/ci/run_register_gate.py
PYTHONPATH=. python3 scripts/ci/run_scorecard.py   # miyuki has no scoring block yet — verify scorecard tolerates this OR add empty miyuki block
bash scripts/git/health_check.sh
```

### Phase 3 PR — Junko's NEW channeling atoms (~150 files; operator-approval-gated)

**Branch:** `agent/junko-channeling-atoms-phase-3-20260519`

**Pre-conditions:**
1. Operator approves the 3 sample atoms in §4.4.
2. Pearl_Editor + Pearl_Writer commission proceeds (Tier 1, Claude Code).

**Operation:** Pearl_Editor authors ~150 atoms across 11 categories per §4.1; commits to `SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/{11 categories}/`.

**Total: ~150 files. Governance: passes (<200).**

**Acceptance gate:**

```bash
# Channeling vocab present (≥80 of 152)
grep -rln "channel\|Channel\|light language\|ascended master\|cosmic council\|frequency\|transmission\|kami\|soul remembrance" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l

# Miyuki vocab absent (0)
grep -rln "zazen\|kitchen table\|ganbaru\|mono no aware\|Yuki\|Hana\|Kenji\|just sitting" \
  SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ | wc -l
```

**Recommended combined-PR variant:** Phase 2 + Phase 3 as a SINGLE PR (~302 files), to avoid the atom-empty Junko window. Governance: above the 200-file warn but below the 500-file block. Plan should call this option out — operator decision §5.A.6.

### Phase 4 PR — Catalog routing updates (~50-80 files)

**Branch:** `agent/junko-channeling-miyuki-contemplative-phase-4-catalog-20260519`

**Files touched (split into atomic clusters to keep PR coherent):**

**Cluster A — catalog_planning (~14 files):**

1. `config/catalog_planning/teacher_brand_archetypes.yaml` — `relational_calm` block: `teacher: junko` → `teacher: miyuki`; update tradition + unique_angle to drop "Junko teaches" → "Miyuki teaches"
2. `config/catalog_planning/brand_identity_system.yaml` — `relational_calm` block: `teacher: junko` → `teacher: miyuki`; update description "Junko's teaching" → "Miyuki's teaching"
3. `config/catalog_planning/brand_display_names.yaml:47` — `teacher: junko` → `teacher: miyuki`
4. `config/catalog_planning/brand_series_plans.yaml:229` — `teacher: junko` → `teacher: miyuki`
5. `config/catalog_planning/brand_teacher_matrix.yaml:65,66,174` — `relational_calm: primary_teacher: junko, teachers: [junko], ...` → `miyuki`; keep `junko: max_books_per_topic: 3, max_books_per_persona: 4` block (will be reseeded with cosmic brand in follow-up)
6. `config/catalog_planning/teacher_brand_lane_assignments.yaml` — 13 locale rows: `relational_calm_<locale>: { teacher: junko }` → `{ teacher: miyuki }` (sed-edit acceptable; pattern is uniform)
7. `config/catalog_planning/teacher_topic_persona_scores.yaml` — COPY junko topic_scores block to a new miyuki block; REPLACE junko block with cosmic-coded topic scores (P1 — needs operator approval on cosmic topic set; if not yet defined, leave junko block empty placeholder)
8. `config/catalog_planning/teacher_brand_author_roster.yaml:457` — `bare_form_books: teacher: junko` → `teacher: miyuki`
9. `config/catalog_planning/brand_cover_art_specs.yaml` — `relational_calm: character_lora: "junko_rc"` → `"miyuki_rc"`
10. `config/catalog_planning/audiobook_video_catalog.yaml:55` — `junko:` block: route `topics: [relational_harmony, shame, inner_security]` to miyuki; reset junko to cosmic topic list
11. `config/catalog_planning/canonical_topics.yaml:66` — UPDATE comment `# junko / relational_calm — wabi-sabi simplicity` → `# miyuki / relational_calm — wabi-sabi simplicity`
12. `config/catalog_planning/title_dedup_phrases.yaml:82` — same comment swap
13. `config/catalog_planning/locale_brand_names.yaml:109` — same comment swap
14. `config/catalog_planning/teacher_persona_matrix.yaml:119` — COPY junko block to miyuki

**Cluster B — manga + manga_profiles (~15 files):**

15. `config/manga/manga_brand_series_plan.yaml:217-243` — `teacher: junko` → `teacher: miyuki`
16. `config/manga/character_brand_registry.yaml:345-380` — full block update per §3.5.3
17. `config/manga/brand_lora_plans.yaml:91` — ADD miyuki block (§3.5.1); REMOVE junko block (junko gets new block in Phase 5)
18. `config/manga/brand_illustration_styles.yaml:145` — `teacher: junko` → `teacher: miyuki`
19. `config/manga/teacher_character_prompts.yaml:108` — ADD miyuki block (§3.5.2); REMOVE junko block; (new junko block authored in Phase 5)
20. `config/source_of_truth/manga_profiles/brands/relational_calm_iyashikei.yaml:10` — `teacher: junko` → `teacher: miyuki`
21-28. `config/source_of_truth/manga_profiles/relational_calm/series_{01..08}.yaml` — for each: replace "Junko" → "Miyuki" in series_description text (sed-edit); confirm internal teacher binding if present

**Cluster C — brand_management (~2 files, 14 line-level edits):**

29. `config/brand_management/teacher_brand_map.yaml:132-154` — `zen_clarity: teacher_id: junko` → `teacher_id: miyuki`
30. `config/brand_management/global_brand_registry.yaml` — 13 locale instances (`zen_clarity_<locale>: teacher_id: junko` → `teacher_id: miyuki`); sed-edit acceptable

**Cluster D — publishing + scripts (~10 files):**

31. `config/publishing/cover_identity_system.yaml:300,422-426` — junko block: brand_id stays `zen_clarity` (which is now miyuki's) — MOVE entire block to a new miyuki entry; reset junko block for cosmic brand (Phase 5)
32. `config/publishing/bestseller_templates.yaml:231` — `junko_overthinking` → `miyuki_overthinking`
33. `scripts/atom_writing/write_teacher_stories.py:50` — ADD `"miyuki"` to roster
34. `scripts/atom_writing/run_writing_campaign.py:171` — ADD `"miyuki"` to roster
35. `scripts/manga/generate_series_plans_from_catalog.py:196` — replace `"junko": "harmony_circle"` → `"miyuki": "relational_calm"` (and remove or update junko if she has a new cosmic brand; otherwise leave junko absent)
36. `scripts/image_generation/generate_bestseller_covers.py:360` — `"author": "Junko"` → `"author": "Miyuki"`
37. `scripts/image_generation/generate_kdp_all_formats.py:192-196` — update teacher_id + author to miyuki for relational_calm rows
38. `scripts/image_generation/generate_manga_character_views.py:32,46` — move junko entries to miyuki
39. `scripts/image_generation/generate_teacher_showcase_triptych.py:36,93` — ADD miyuki; junko entry stays but gets new cosmic prompt in Phase 5
40. `scripts/video/render_videos.py:58` — ADD miyuki entry; junko stays
41. `scripts/video/generate_teacher_showcase_videos.py:56,65,74,82,90` — ADD miyuki to all 5 maps; update junko brand label
42. `scripts/release/build_epub.py:66` — update Junko's publisher/brand label IF row maps to relational_calm; ADD miyuki entry
43. `scripts/release/build_manga_webtoon.py:306` — rename "junko_sleep_anxiety_complete.pdf" → "miyuki_sleep_anxiety_complete.pdf" IF this build is for relational_calm
44. `scripts/audio/generate_teacher_showcase_audio.py:32,41` — ADD miyuki; verify junko voice register matches doctrine (channeling, not generic female)
45. `scripts/audiobook/generate_showcase_bundle.py:47` — `{"id": "junko", "topic": "overthinking", "brand": "relational_calm", "name": "Junko"}` → `{"id": "miyuki", ..., "name": "Miyuki"}`; add separate junko row when Phase 5 cosmic brand exists
46. `scripts/generate_author_cover_art_bases.py:25` — move junko color palette to miyuki; junko gets new luminous palette in Phase 5

**Cluster E — tests + workflow (~3-4 files):**

47. `tests/manga/test_series_plan_generator.py:166` — ADD `"miyuki"` to roster
48. `tests/test_cookbook_v2_loader.py:140` — `"junko_overthinking"` → `"miyuki_overthinking"`
49. `.github/workflows/max-quality-catalog.yml:17,22,71,73` — ADD miyuki to teachers + shard matrix; junko stays

**Cluster F — docs + register_gate (~5 files):**

50. `phoenix_v4/quality/register_gate.py:287-290` — UPDATE junko comment: `# Junko = receiver/hibakusha witness` → `# Junko = channeler / light-language transmitter (receiver of cosmic guidance)`; POPULATE forbidden tokens list with `["zen", "zazen", "ganbaru", "mono no aware", "shikantaza", "shingon", "ajikan", "kitchen table"]`; ADD miyuki entry with `[ "channel", "channeling", "light language", "ascended master", "cosmic council", "frequency", "transmission", "soul remembrance", "shingon", "ajikan", "zazen", "shikantaza", "satori", "roshi"]`
51. `docs/PEARL_ARCHITECT_STATE.md` — ADD cap entry "JUNKO-CHANNELING-MIYUKI-CONTEMPLATIVE-01"; ADD miyuki teacher entry to roster
52. `docs/SYSTEM_STATE_MASTER.md:90` — add miyuki to teacher list: `..., miyuki, omote, ...` (alphabetical between miki and omote — keep junko in place)
53. `docs/TEACHER_SHOWCASE_HANDOFF.md:15` — add miyuki to teacher list
54. `docs/handoffs/HANDOFF_2026-05-08_SPRINT1_AND_TEACHER30S.md:181` — UPDATE table row `| junko | relational_calm (rc) | ja-JP | pure_manga |` → `| miyuki | relational_calm (rc) | ja-JP | pure_manga |`; junko gets new row when Phase 5 cosmic brand exists

**Cluster G — Pearl_News pipeline (~3 files; light touch):**

55. `pearl_news/pipeline/teacher_authority.py`, `pearl_news/pipeline/atom_usage_tracker.py`, `pearl_news/pipeline/assemble_v52.py` — verify junko handling unchanged (channeling Junko is still active in Pearl_News); ADD miyuki ONLY IF miyuki is also added to Pearl_News (operator decision §5.A.5; default: NO, miyuki is Pearl_Prime-only). Verify no implicit "roster must include all registry teachers" check breaks.
56. `tests/test_pearl_news_*.py` (5 files) — verify junko-as-channeler tests unchanged; ADD miyuki test variants only if miyuki gets a Pearl_News pack (default: NO)

**Total: ~50-65 files. Governance: under 200 warn but right at the 3-subsystem warn (catalog_planning + manga + brand_management + publishing + scripts + tests + docs = 7). Plan calls this out; expect a "scope >3 subsystems" warn (not block) from PR governance CI. Operator approves the warn and merges.**

**Recommended split:** if governance blocks, split into 4a (catalog_planning + manga + brand_management — pure routing, ~30 files) + 4b (scripts + tests + publishing — wrap-up, ~20 files) + 4c (docs + register_gate, ~5 files). Each sub-PR is mechanical sed-equivalent edits, low risk.

### Phase 5 PR — Visual assets re-routing (~50 files; per OPD-105 §6.B precedent, DEFER re-render)

**Branch:** `agent/junko-channeling-miyuki-contemplative-phase-5-visuals-20260519`

Per OPD-105 §6.B (Phase 5 of Kenjin migration), **visual re-renders are deferred** to a separate operator-attended Pearl Star ComfyUI commission. This phase **only updates metadata + filename references**.

**Files touched:**

1. `brand-wizard-app/public/teacher_pics/junko.png` — RENAME to `brand-wizard-app/public/teacher_pics/miyuki.png` (visual is a Japanese-female-wabi-sabi portrait per current `brand_lora_plans.yaml.junko.notes = "Japanese female, wabi-sabi simplicity"`); ADD new `junko.png` placeholder (or null) until Phase 5 re-render
2. `brand-wizard-app/public/teacher_pics/manga/junko_top.png` — same rename pattern
3. `brand-wizard-app/public/assets/manga_covers/junko_{cover_mindfulness, cover_sleep_anxiety, cover_social_anxiety, front, portrait, profile, scene, symbolic, three_quarter}.png` — 9 files RENAME to `miyuki_*` (all are wabi-sabi-coded per current `brand_illustration_styles.yaml.relational_calm.style_name = "Wabi-Sabi Simplicity"`)
4. `brand-wizard-app/public/assets/manga_covers/junko_cover_mindfulness.png` etc — same
5. `brand-wizard-app/public/assets/covers/cover_junko_overthinking.png` — RENAME to `cover_miyuki_overthinking.png` (matches `config/publishing/bestseller_templates.yaml` rename in Phase 4)
6. `brand-wizard-app/public/assets/covers/audiobook/cover_junko_overthinking.png` — same rename
7. `brand-wizard-app/public/assets/covers/kdp/junko_{social, audiobook, ebook, podcast}.png` — 4 files RENAME (these are KDP covers for "The Loop Breaker / Zen Clarity" which is Miyuki's book per Phase 4)
8. `brand-wizard-app/public/assets/video/manga/junko.mp4` — RENAME to `miyuki.mp4`
9. `brand-wizard-app/public/assets/video/tiktok/junko_courage_tiktok.mp4` — RENAME (TikTok content is body-anchored, Miyuki-coded per the audit OPD-20260517-010 noting variant videos)
10. `brand-wizard-app/public/teacher_vid_package/junko.mp4` — RENAME
11. `brand-wizard-app/public/teacher_showcase/junko__chapter_1.html` — RENAME to `miyuki__chapter_1.html`. **HOWEVER:** the current content of this file (per OPD-20260518-004 sampled) is **channeling-correct** ("このメッセージは、私が考えたものではない。受け取っているものだ。" = "This message is not what I thought up. It is what I am receiving"). **DECISION**: this chapter STAYS under Junko (channeling). The "Junko chapter" content was correctly authored to the channeling doctrine. The wabi-sabi visual assets above MIGRATE to Miyuki; this one HTML stays under Junko. Verify by reading content.
12. `brand-wizard-app/public/assets/audio/audiobook_chapters/junko_overthinking_ch1.mp3` — RENAME to `miyuki_overthinking_ch1.mp3` (audio renders ganbaru/mono no aware preamble per `book_junko_overthinking_15min.txt`)
13. `brand-wizard-app/public/assets/audio/podcast/junko_podcast_3min.mp3` — DECIDE per audit; if podcast content is contemplative → miyuki; if channeling → junko
14. `brand-wizard-app/public/assets/audio/showcase/junko_imposter_syndrome_hook.mp3` — DECIDE per audit; recommend miyuki (imposter syndrome is a body-anchored Miyuki topic)
15. `artifacts/pipeline_examples/junko/book_junko_overthinking_15min.txt` — **CANONICAL EVIDENCE FILE.** This is the bestseller-quality book whose preamble explicitly says "ganbaru + Zen + mono no aware". RENAME to `artifacts/pipeline_examples/miyuki/book_miyuki_overthinking_15min.txt`. THIS IS THE FILE THAT MATERIALLY TRIGGERED THE OPD-111 REVERSAL. **Note this in the PR description.**
16. `artifacts/pipeline_examples/junko/video_plan.json`, `cover_junko_overthinking.png` — same migration pattern
17. `artifacts/pipeline_examples/manga_covers/junko_cover_{mindfulness,sleep_anxiety,social_anxiety}.png` (3 files) — RENAME to miyuki
18. `artifacts/audiobook_samples/junko_overthinking_ch1.mp3` — RENAME
19. `artifacts/audiobook_samples/_prose/junko_overthinking_ch1.txt` — RENAME (verify content — likely Miyuki-coded since "junko_overthinking" rename is Phase 4 publishing)
20. `artifacts/video/teacher_30s_v1/junko/script_ja_JP.yaml` — DECIDE per content audit; if "I receive" register → junko stays; if "the body knows" register → miyuki
21. `artifacts/video/tiktok_body_awareness/junko/...` (8 clips + 2 final renders + 1 audio narration + 1 _work folder) — RENAME folder to `miyuki/...` (title is literal: "body_awareness" = body-anchored = Miyuki)
22. `artifacts/video/image_banks/...` — REVIEW; rename per binding

**Total: ~50 files. Governance: passes (<200; rename-only).**

**Visual re-render commission (out-of-this-PR, per OPD-105 §6.B):**
- New Junko portrait + manga assets reflecting **luminous/channeling/cosmic** visual register: flowing soft robes, light particles, hands raised receptively, soft golden/blue palette, no enso / no ink-brush, no kitchen-table setting.
- Pearl_Prime visual pipeline commission via Pearl Star ComfyUI / FLUX.
- ~1 operator-attended day of render time.

### Step 3 — PR titles and bodies

**PR 1 (Phase 1):** `migration(teachers): create Miyuki teacher card (OPD-111 Phase 1)`
**PR 2 (Phase 2):** `migration(teachers): junko -> miyuki bulk atom move, 152 files (OPD-111 Phase 2)`
**PR 3 (Phase 3):** `migration(teachers): junko channeling atom authoring (~152 files) (OPD-111 Phase 3)`
**PR 4 (Phase 4):** `migration(catalog): junko -> miyuki catalog routing for relational_calm + zen_clarity (OPD-111 Phase 4)`
**PR 5 (Phase 5):** `migration(assets): junko -> miyuki visual asset re-routing, defer re-render (OPD-111 Phase 5)`

PR 2 body (template — adapt for each phase):

```markdown
## Summary
Phase 2 of the OPD-111 doctrinal-misclassification migration. The 152 approved atoms
currently filed under SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/ are Japanese
contemplative + body-anchored + ganbaru voice (e.g. STORY_003 opens "In the Zen
tradition, there is a story…") — NOT the channeling content that Junko's doctrine.yaml
declares she is. This PR moves all 152 atoms to the new teacher `miyuki` (created in
Phase 1), preserving them as-authored. Junko's atom bank becomes empty until Phase 3
authors channeling-correct atoms from her intake material.

Operator decisions per OPD-20260519-111:
- Atom voice belongs to Miyuki, not Junko (verified by single-line evidence: STORY_003)
- Junko's doctrine.yaml stays unchanged (correct as-is)
- Phase 3 authors ~150 new channeling atoms gated on sample approval (see plan §4.4)

Plan: docs/migrations/JUNKO_CHANNELING_MIYUKI_CONTEMPLATIVE_MIGRATION_PLAN_2026-05-19.md

## Risks
1. Junko's atom bank is EMPTY between Phase 2 merge and Phase 3 merge. Pause Junko
   bestseller renders during this window, OR merge Phase 2+3 together (operator decision).
2. Catalog routing (Phase 4) still has teacher=junko bound to relational_calm —
   if any pipeline tries to render relational_calm during the Phase 2 to Phase 4 gap,
   it will fail at the atom layer.

## Test plan
- [ ] grep -rln "junko" SOURCE_OF_TRUTH/teacher_banks/miyuki/approved_atoms/ returns 0
- [ ] ls SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/*/  shows empty directories
- [ ] PYTHONPATH=. python3 scripts/ci/run_register_gate.py passes
- [ ] No pipeline run targets teacher=junko until Phase 3 lands
```

---

## 6. Risk register

### 6.A Operator-decision-required ambiguities

#### 6.A.1 **(P0 — CRITICAL)** Atom-empty Junko window: merge Phase 2 + Phase 3 together, or accept the gap?

**Two options:**

- **Option X — Separate Phase 2 and Phase 3 PRs.** Cleaner per-PR scope; matches Kenjin migration shape. Junko has zero atoms between Phase 2 merge and Phase 3 merge (estimated 3-5 days). Any pipeline rendering teacher=junko fails. **Mitigation:** pause Junko bestseller / Pearl_Prime / manga renders during the window; Pearl_News is unaffected (it uses its own teacher_topic_packs, not the teacher_banks atoms). Risk grade: M.
- **Option Y — Combined Phase 2+3 PR (~302 files).** No atom-empty window. PR governance: 302 is > 200 warn but < 500 block; expect a warn comment, not a block. Operator approval signs off the warn. Single-PR coherence: harder to review (152 mechanical moves mixed with 150 newly-authored creative content). Risk grade: M (different shape).

**Recommendation: Option X (separate).** Pause window is short; the per-PR clarity matters more for review. Pearl_News and Pearl_Prime are operator-attended workflows; the operator can defer Junko-targeted renders to after Phase 3 merge. Phase 3 authoring can run in parallel during the Phase 2 review.

**Operator decision needed before §5 Phase 2 PR is pushed.**

#### 6.A.2 **(P0 — CRITICAL)** Cosmic-coded canonical topics for Junko — author now or follow-up?

Phase 4 Cluster A item 7 (`teacher_topic_persona_scores.yaml`) wants to replace Junko's current contemplative topic_scores (anxiety 0.9, social_anxiety 0.95, etc.) with cosmic-coded topics (awakening 0.95, energy_work 0.90, etc.). **Problem:** `awakening`, `energy_work`, `light_language`, `soul_remembrance`, `spiritual_transitions`, `cosmic_guidance` are NOT in `config/catalog_planning/canonical_topics.yaml` (line 64-70 lists Junko's current contemplative topics).

**Options:**

- **Option I — In-PR cosmic topic addition.** Phase 4 also adds cosmic topics to `canonical_topics.yaml` and to all per-locale lane assignments + cover specs + display strings. ~30 additional file edits. Substantially broadens Phase 4 scope.
- **Option II — Out-of-scope: leave Junko's `teacher_topic_persona_scores.yaml` block empty post-migration.** Phase 3 atoms still exist; Pearl_News still routes Junko to mental_health/climate/etc. But Pearl_Prime bestseller rendering with `--teacher junko` has no topics to pick. Effectively pauses Junko bestseller catalog until follow-up.
- **Option III — Hybrid: Phase 4 retains Junko's current "anxiety / sleep_anxiety / overthinking" topic scores under junko (because Junko can also teach these topics from the channeling angle), and routes Miyuki to the contemplative versions of the same topics.** Both teachers cover the same canonical topics; the differentiation is voice register. **RECOMMENDED.**

**Operator decision needed.** If Option III: Phase 4 only needs to COPY junko's topic_scores block to miyuki (additive), and adjust Miyuki's scores slightly differently (e.g., Miyuki's `social_anxiety: 0.95`, Junko's `social_anxiety: 0.75` because Junko teaches it from a different angle). The per-row routing rule §1.2 then becomes a soft preference, not a hard re-route.

#### 6.A.3 **(P1)** Honorific for Miyuki

Recommend `null` (none). Alternatives: `"sensei"`, `"-san"`. **Operator confirms.**

#### 6.A.4 **(P1)** Geographic anchor for Miyuki — Kyoto or Tokyo?

Recommend **Kyoto**. The 8 manga series profiles already suggest small-Japanese-city iyashikei aesthetic (cafe, bookshop, gardener, café). Tokyo would tone the iyashikei toward urban-mainstream (Honey and Clover register). Kyoto leans toward the contemplative-aestheticism (Mushishi register). **Operator confirms or overrides.**

#### 6.A.5 **(P2)** Add Miyuki to Pearl_News in this migration?

Default: NO. Pearl_News roster intentionally has 9-10 teachers (operator-selected), not all 13+ registry teachers. Miyuki can join Pearl_News in a follow-up if needed. **Operator confirms** (just to be explicit — by default she stays Pearl_Prime-only).

#### 6.A.6 **(P2)** Sub-school explicit naming

Doctrine.yaml §3.3 sets `sub_school: null` for Miyuki — she is "Japanese contemplative; lay-secular; Zen-adjacent without explicit lineage". This is deliberately UNDERSPECIFIED to avoid the OPD-105 trap (declaring "Zen" without specifying Sōtō vs Rinzai). **Operator confirms underspecified is intentional.**

#### 6.A.7 **(P2)** Voice ID for Miyuki audiobook

Recommend `ja_f_mature_warm_01` (or analogous quiet/mature register from CosyVoice2). **Pearl_Editor confirms during voice audit; not blocking migration PRs.**

### 6.B Operational risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Atom-empty Junko window** (between Phase 2 and Phase 3 merges) breaks active Junko renders | H | M | Operator pauses Junko-targeted renders for the gap; Pearl_News unaffected (uses its own packs); see §6.A.1 |
| **Catalog routing broken** between Phase 2 and Phase 4 — relational_calm still binds teacher=junko but junko has no atoms | H | M | Phase 2 + Phase 4 merge close in time; OR operator runs no relational_calm renders during the gap |
| **OPD-105 / OPD-111 collision** — Kenjin migration already split Joshin→Shingon+Kenjin→Zen; this migration adds Miyuki as a separate Japanese-contemplative-non-Zen teacher. Risk: Miyuki and Kenjin voice-register drift convergence over time. | M | M | Doctrine.yaml §3.3 explicitly forbids Sōtō/Rinzai/shikantaza/zazen-as-method-name vocabulary for Miyuki; register_gate.py Phase 4 item 50 adds enforcement. Pearl_Editor must hold the line during atom authoring. |
| **Push-guard blocks on Phase 4** because multi-subsystem (catalog_planning + manga + brand_management + publishing + scripts + tests + docs = 7) | M | L | Split Phase 4 into 4a/4b/4c per §5 recommendation; OR accept the warn since changes are mechanical |
| **Catalog visibility index regen** after Phase 4 produces orphaned references | M | M | Run `python3 scripts/catalog/build_catalog_visibility.py` (or current entry point) as final step of Phase 4; assert miyuki entries count matches expected |
| **Pearl_News test fixture breaks** because miyuki not in news_roster but tests assume `registry ⊆ news_roster` | L | L | Audit pearl_news tests; default is no test break because we are NOT adding miyuki to news roster |
| **OPD-20260518-004 register_gate Junko comment drift** ("hibakusha witness") persists because register_gate.py edit gets forgotten | M | L | Phase 4 Cluster F item 50 explicitly updates this; PR description references it |
| **Renaming a YAML or PNG file that's referenced by an absolute path elsewhere** breaks downstream | M | M | Before each Phase 5 rename, `grep -rn "junko_<filename>"` and update any reference; cross-check `brand-wizard-app/public/data/` JSON manifests |
| **Catalog reproducibility lost** if 152 atoms get rewritten in place rather than `git mv`'d | L | M | Phase 2 script uses `git mv` per §5 explicitly; verify in PR diff that rename detection is preserved (gh pr diff --stat shows R rather than D+A) |

### 6.C Visual iconography risks

| Asset | Currently coded as | Action |
|---|---|---|
| `brand-wizard-app/public/teacher_pics/junko.png` | Per `brand_lora_plans.yaml.junko.notes` = "Japanese female, wabi-sabi simplicity, radical acceptance presence". **Wabi-sabi = Miyuki, not channeling Junko** | Migrate to `miyuki.png`; commission new luminous-cosmic Junko portrait (Phase 5 deferred re-render) |
| `brand-wizard-app/public/assets/manga_covers/junko_*.png` (9 covers) | Per `brand_illustration_styles.yaml.relational_calm` = "Wabi-Sabi Simplicity, manga in stark Zen aesthetic, bold decisive brushstrokes, warm white and stone tones, maximum negative space, asymmetric composition, Vagabond meets Ping Pong". **All wabi-sabi/Zen = Miyuki** | Migrate to miyuki_*.png; new Junko cosmic visuals (Phase 5 deferred re-render) |
| `brand-wizard-app/public/assets/covers/kdp/junko_{social,audiobook,ebook,podcast}.png` | "The Loop Breaker" KDP covers — book is Miyuki's per Phase 4 publishing rename | Migrate to miyuki_*.png |
| `brand-wizard-app/public/assets/video/tiktok/junko_courage_tiktok.mp4` | TikTok body-awareness content per `artifacts/video/tiktok_body_awareness/junko/` — body-anchored = Miyuki | Migrate to miyuki_courage_tiktok.mp4 |
| `brand-wizard-app/public/teacher_showcase/junko__chapter_1.html` | **CHANNELING-CORRECT** content (line 21 of file: "このメッセージは、私が考えたものではない。受け取っているものだ。" = "This message is not what I thought up. It is what I am receiving."). OPD-20260518-004 Pearl_Writer correctly honored Junko's channeling doctrine here. | **RETAIN UNDER JUNKO** — do not migrate |
| `artifacts/pipeline_examples/junko/book_junko_overthinking_15min.txt` | Bestseller-quality preamble explicitly says "ganbaru + Zen awareness + mono no aware" (Miyuki voice, not channeling) | Migrate to `artifacts/pipeline_examples/miyuki/book_miyuki_overthinking_15min.txt`. THIS FILE IS THE CANONICAL OPD-111 EVIDENCE — flag in PR. |
| `artifacts/showcase/teacher_writing_samples/junko__chapter_1.md` | Mirror of `teacher_showcase/junko__chapter_1.html` — CHANNELING-CORRECT (OPD-20260518-004) | **RETAIN UNDER JUNKO** |
| `artifacts/video/teacher_30s_v1/junko/script_ja_JP.yaml` | Voice register TBD — verify before migration | DECIDE per content audit |
| `artifacts/video/tiktok_body_awareness/junko/...` (8 clips, 2 finals, 1 audio, 1 _work) | Folder title says "body_awareness" — body-anchored = Miyuki | Migrate folder to miyuki/ |

**Visual iconography swap-in cheat-sheet (for new Junko cosmic renders, Phase 5 re-render):**

- Replace wabi-sabi negative space → **soft golden / luminous-blue light surrounding the figure**
- Replace enso single brush stroke → **light particles or geometric mandala forms (NOT Buddhist mandala — Shingon owns mandara; use cosmic geometry / sacred geometry)**
- Replace austere modern Japanese clothing → **flowing soft robes (white / cream / soft gold); modest spiritual aesthetic**
- Replace kitchen / café / small-therapy-room setting → **workshop / retreat space / shrine pathway / open sky / unmarked spiritual interior**
- Replace "dry amusement" eyes → **soft alert receptive eyes; sometimes closed in receiving state; hands raised in mudra / gesture of reception**
- Replace "decisive ink brushstroke" linework → **soft halated linework, watercolor-edge, light auras**

### 6.D Cross-reference and marketing copy drift

| Surface | Risk |
|---|---|
| Existing public KDP listings (if any) for "The Loop Breaker" / "Zen Clarity" attributed to Junko | If shipped: leave shipped artifacts as-is (now Miyuki-attributed under the migration, but public KDP listing stands until manually updated). Operator decision: trigger KDP metadata update or leave? Recommend: schedule KDP metadata refresh as a separate non-blocking workstream. |
| `MANGA_STRATEGIC_AUDIT_VERDICT.md` mentions "Channeler Junko" alongside Master Wu, Ra, etc. in roster lists | Update to add Miyuki; keep Junko (still a teacher; just no longer the wabi-sabi voice) |
| `artifacts/research/teacher_market_validation_matrix_2026_04_04.md` historical research | APPEND 2026-05-19 update header per OPD-105 §G.31 precedent. DO NOT rewrite body. |
| Already-published Pearl_News articles (`artifacts/pearl_news/published/2026-04-{19,22}/.../junko/...`, 70 files) | These are correctly channeling-framed. RETAIN as-is. |
| `docs/PEARL_NEWS_5_VARIATION_EXPANSION_PROGRAM.md:88` says "Junko = receiver, not creator." | KEEP — this is correct for Junko-as-channeler. |

### 6.E Catalog DECISION ROUTING rule (codified)

For any in-flight catalog row currently bound to `teacher: junko`, apply this rule:

- **Body-anchored topics** (anxiety, overthinking, sleep, overwhelm, boundaries, burnout, shame, self_worth, relational_harmony, social_anxiety, imposter_syndrome, inner_security, compassion_fatigue, perfectionism, grief-in-relationship) → **Route to MIYUKI**.
- **Cosmic / channeling topics** (awakening, energy work, light language, ascended masters, frequency shift, cosmic guidance, soul remembrance, spiritual transitions, dimensional ascension, past-life work, kami connection) → **Keep JUNKO**.
- **Edge case (topic-neutral identity)**: prefer Miyuki for now (existing atoms support Miyuki); audit-and-redirect to Junko once Phase 3 channeling atoms exist.

This routing is operationalized in `phoenix_v4/quality/register_gate.py` Phase 4 update (item 50) and in the per-row decisions of Phase 4 Cluster A.

---

## 7. Backout plan

### 7.A Per-step rollback

Each phase is atomic and revertable independently:

- **If Phase 1 (Miyuki birth) needs revert:** `git revert <Phase 1 merge SHA>`. Removes Miyuki cleanly. Junko unaffected. Zero downstream impact.
- **If Phase 2 (atom move) needs revert:** `git revert <Phase 2 merge SHA>`. Atoms return to junko/. Miyuki atom directories become empty. Catalog rows in Phase 4 will then point to Miyuki-with-no-atoms (which is a forward-state issue, not a Phase 2 issue). Recommend: only revert Phase 2 if you are ALSO reverting Phase 4.
- **If Phase 3 (Junko channeling atom authoring) is rejected by operator:** keep Phase 1+2+4+5 merged; iterate Phase 3 in a new commission round with revised sample drafts. The atoms-empty state for Junko persists until Phase 3 lands.
- **If Phase 4 (catalog routing) needs revert:** `git revert <Phase 4 merge SHA>`. Catalog rows snap back to junko binding. Now junko has no atoms (because Phase 2 moved them). Recommend: only revert Phase 4 if you are ALSO reverting Phase 2.
- **If Phase 5 (visuals) needs revert:** `git revert <Phase 5 merge SHA>`. Filenames revert to junko_*. Phase 4 catalog still binds relational_calm to miyuki, so brand→file lookups will 404. Recommend: revert Phase 4 + 5 together.

### 7.B Emergency revert checklist (if production catalog breaks post-merge)

```bash
# 1. Identify the migration merge SHAs (5 PRs)
git log --oneline | grep "junko-channeling-miyuki\|OPD-111"

# 2. Revert in reverse order (Phase 5 -> 4 -> 3 -> 2 -> 1)
git revert <phase-5-sha>
git revert <phase-4-sha>
# (Phase 3 may not need revert — keep new junko atoms even if catalog reverts)
git revert <phase-2-sha>
git revert <phase-1-sha>

# 3. Regen catalog visibility
python3 scripts/catalog/build_catalog_visibility.py

# 4. Push to a recovery branch (NOT main directly)
git checkout -b recovery/revert-junko-miyuki-migration
git push -u origin recovery/revert-junko-miyuki-migration

# 5. Open a PR for the revert; tag the operator for sign-off
gh pr create --title "revert: junko-channeling-miyuki-contemplative migration (operator request)" \
  --body "Reverting OPD-111 migration per operator emergency request."
```

### 7.C Out-of-scope follow-up commissions

These items are explicitly NOT executed in the 5-phase migration PR set; they are downstream gated commissions:

1. **Junko Shingon-coded brand authoring** — new cosmic-channeling brand name + identity + colophon + tagline + 4-6 new luminous-coded authors. Pearl_Architect + Pearl_Brand + Pearl_Editor commission. ~2-3 sessions. Gated on §6.A.2 operator decision.
2. **Junko visual asset re-render (cosmic)** — new portrait + manga covers + KDP covers + TikTok content. Pearl_Prime visual pipeline commission via Pearl Star ComfyUI. ~1 operator-attended day.
3. **Cosmic canonical topic addition** — add `awakening`, `light_language`, `cosmic_guidance`, `energy_work`, `soul_remembrance`, etc. to `config/catalog_planning/canonical_topics.yaml` if Option I/III in §6.A.2 selected. Pearl_Architect cap entry required.
4. **Junko's new bestseller book** in channeling voice — "The Receivers" (working title), authored from intake material. Pearl_Writer commission post-Phase-3. ~1-2 sessions.
5. **Miyuki Pearl_News integration** if §6.A.5 reversed — new teacher_topic_packs/teachers/miyuki/{mental_health, education, etc.}.yaml. Pearl_Editor commission. ~1 session.
6. **Voice audit for Miyuki audiobook** — pick CosyVoice2 reference clip per §6.A.7. Pearl_Editor + Pearl_Int. ~0.5 session.

---

## 8. Appendix — quick reference

### 8.1 Vocabulary whitelists (for grep audits and atom-authoring)

#### Junko (channeling) whitelist — what MUST appear in Junko's atoms post Phase 3

```
channel channeling Channel Channeler
light language ライトランゲージ
ascended masters ascended-masters
cosmic council celestial hierarchy
frequency vibration resonance
transmission receive reception conduit
soul remembrance soul frequency
unity field source field
kami Olympian gods deity frequencies
Lemuria Atlantis
power-spot retreat shrine pilgrimage
Lightworker Light Language lesson
Age of Air 風の時代
goddess lesson
dimensional ascension
gohōgō (when used in transmission anchor context, NOT Shingon ritual context)
Tōhoku 2011 awakening
Mt. Kōya council attendance
past-life retrieval
```

#### Junko (channeling) forbidden — what MUST NOT appear in Junko's atoms post Phase 3

```
zen Zen zazen Zazen
koan kōan shikantaza satori kenshō
just sitting
direct pointing
roshi sensei (in honorific position)
ganbaru mono no aware ma (as practice term)
kitchen table (as practice setting)
Yuki Hana Kenji (Miyuki's recurring characters)
shingon mikkyo Dainichi Kōbō Daishi sanmitsu Ajikan
shikoku 88 Mt. Kōya (as pilgrimage in non-cosmic context)
beginner's mind shoshin
the body knew (Miyuki's signature pivot phrase)
```

#### Miyuki (Japanese contemplative) whitelist

```
ganbaru ganbaru-as-practice
mono no aware 物の哀れ
ma 間 the meaningful pause
the body knows
the breath the breath drops
kitchen table before dawn
just sitting (lay-secular use; not as shikantaza method name)
shoshin (Suzuki-Roshi lay-secular sense)
kokoro makoto
ki ga tsuku isshōkenmei
shōganai (warm-acknowledgment sense only)
Yuki Hana Kenji Nao Koba-san (existing composite characters)
kyoto bookshop café therapy room park bench
small arrivals not breakthroughs
the practice was the practice
the answer was the willingness to be empty
```

#### Miyuki forbidden

```
channel channeling light language ascended masters
cosmic council frequency-as-literal transmission
soul remembrance unity field
Sōtō Sōtō-shū Rinzai shikantaza (as method name)
shingon mikkyo dainichi kōbō daishi
sanmitsu ajikan kōmyō shingon
mantras as literal recitation practice
vipassanā anattā mettā (as method names)
roshi (as Miyuki's honorific)
mindfulness with bowed heads
```

### 8.2 File inventory regen command

```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/agent-a540c4269503e3a12
grep -rln "junko\|Junko" \
  --include="*.yaml" --include="*.json" --include="*.md" \
  --include="*.py" --include="*.txt" --include="*.yml" \
  2>/dev/null | sort > /tmp/junko_files.txt
wc -l /tmp/junko_files.txt   # expect 424 ± as files get touched in each phase
```

### 8.3 Phase progression summary

| Phase | Files touched | Governance | Operator-decision gates | Risk |
|---|---|---|---|---|
| 1 — Miyuki birth | ~16 | passes | confirm honorific (§6.A.3), Kyoto vs Tokyo (§6.A.4), voice ID (§6.A.7) | Low |
| 2 — Atom move (152) | 152 | passes | confirm Option X vs Y (§6.A.1) | Medium (atom-empty Junko window) |
| 3 — Junko channeling atom authoring (~150) | ~150 | passes | sample atom approval (§4.4) | Medium (creative content) |
| 4 — Catalog routing | ~50-65 | warn (7 subsystems > 3) | confirm cosmic topics Option III (§6.A.2) | Low |
| 5 — Visual rename + deferred re-render | ~50 | passes | confirm content per-file (some stay junko per §6.C) | Medium (rename collisions) |
| **TOTAL** | **~420 files across 5 PRs** | | | |

### 8.4 Canonical evidence files referenced in this plan

- `teachers/junko/junko_doctrine_notes.rtf` — Junko's intake doctrine source (650 lines RTF, ~7,700 chars plain)
- `teachers/junko/junko_yt.rtf` — Junko's YouTube transcript (Japanese, content-restored ~3,425 words equivalent in plain extract)
- `SOURCE_OF_TRUTH/teacher_banks/junko/doctrine/doctrine.yaml` — current 30-line channeling doctrine (CORRECT)
- `SOURCE_OF_TRUTH/teacher_banks/junko/approved_atoms/STORY/junko_STORY_003.yaml:5` — "In the Zen tradition, there is a story…" — single-line proof of doctrine drift
- `artifacts/pipeline_examples/junko/book_junko_overthinking_15min.txt:11` — "the tradition of ganbaru — endurance, perseverance, doing one's honest best in the face of difficulty — braided with Zen awareness and the Japanese aesthetic of mono no aware" — canonical Miyuki voice in a Junko-titled file
- `artifacts/showcase/teacher_writing_samples/junko__chapter_1.md:21` — "このメッセージは、私が考えたものではない。受け取っているものだ。" — correctly channeling-coded Junko content (per OPD-20260518-004; STAYS under Junko)

### 8.5 Decision-of-record audit trail

- **OPD-20260518-004** (2026-05-18): Pearl_Editor noted Junko = "New Age channeler" per doctrine, contradicting spec's a-priori "hibakusha witness" smell-test. doctrine.yaml is canonical voice authority. Migration triggered by this verdict.
- **OPD-20260519-111-INITIAL** (2026-05-19): Operator first considered routing all 152 contemplative atoms under Junko's doctrine. REVERSED same day after re-read of atom voice + doctrine mismatch.
- **OPD-20260519-111-REVERSAL** (2026-05-19): Operator decision codified: create NEW teacher Miyuki to carry the 152 atoms; Junko retains slot + doctrine + Pearl_News; new channeling atoms authored from intake in Phase 3.

---

**End of migration plan.**

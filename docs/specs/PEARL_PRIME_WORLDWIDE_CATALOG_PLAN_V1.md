
# Pearl Prime Worldwide Catalog Plan — V1 (Phase 2)

**Project ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 strategic deliverable)  
**Subsystem owners:** pearl_pm coordination; Pearl_Marketing volume SSOT; brand_admin surfaces  
**Status:** planning baseline — doc + matrix only (no generators, no image execution, no catalog mutation)  
**Date:** 2026-05-10  
**Consumes:** `artifacts/catalog/worldwide_catalog_plan_{en_US,ja_JP,zh}_2026-05-10.tsv` (this plan’s numeric SSOT for dashboard + render backlog imports)

**Operator amendment (2026-05-10 — cell math):** Phoenix Omega **production cell** authority is **259** = **222** regular worldwide (**37 × 3 locales × 2 surfaces: ebook + manga**) + **37** Japan **manga-only** parallel catalog (**37 × ja_JP × manga**; identical `brand_id` set; separate Japanese legal entity + Line Manga / JP manga platform distribution). This **supersedes** the retired **555** (37×3×5) planner figure and any **45,216** packaged-asset deck totals tied to that retired denominator. Ratification: `docs/PEARL_ARCHITECT_STATE.md` → **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01** `AMENDMENT-2026-05-10-CELL-MATH-CORRECTION` + **JAPAN-MANGA-ONLY-CATALOG-V1-01**. Parallel spec: `docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md`.

---

## Document control

| Input (read-only discovery) | Role in this plan |
|-----------------------------|-------------------|
| `config/manga/canonical_brand_list.yaml` | 37 Path X manga `brand_id` canon + tier + demographic |
| `config/manga/brand_lora_plans.yaml` | `character_loras`, `brand_style_loras`, `protagonist_loras` — style_ref + teacher bindings |
| `config/authoring/pen_name_teacher_profiles.yaml` | Citation / methodology anchors for persona economics (not a roster file) |
| `config/teachers/teacher_registry.yaml` | Named teacher doctrine profiles (13 keys incl. `adi_da`) |
| `config/catalog_planning/teacher_brand_archetypes.yaml` | 12 teacher-brand archetypes (book lane naming; cross-ref for voice) |
| `config/marketing/weekly_volumes_per_brand.yaml` | Operator-approved V1 weekly intent (manga=1/wk/brand; other surfaces 0 until Table 6) |
| `artifacts/catalog/pearl_prime_book_script_catalogs/catalog_summary.json` | Existing standard_book rows (1478 en_US/ja_JP; zh_TW/zh_CN variants) |
| `artifacts/catalog/manga/manga_catalog_summary.json` + CSVs | Existing manga catalog rows (en_US/ja_JP primary; zh blocked rows) |
| `artifacts/qa/parallel_image_generation_plan_2026-05-09.md` | Image wave structure, per-asset targets, Pearl Star wall-time model |

---

## 1. Scope

### 1.1 Brand × locale × surface grid

- **Brands:** 37 (`canonical_brand_list.yaml`, Path X manga canon)  
- **Locales (planning buckets):** `en_US`, `ja_JP`, `zh` where **zh = zh_TW + zh_CN** as a combined execution bucket (two storefronts, one planning file).  
- **Phoenix-counted surfaces (regular worldwide catalog):** **`ebook` + `manga` only** → **37 × 3 × 2 = 222** production cells. Per-locale mix: **en_US** ebook-heavy with some manga; **ja_JP** higher manga % vs en_US; **zh** similar mix per market research.  
- **Audiobook:** **not** a Phoenix Omega cell. Each ebook manuscript is the **script** for the audiobook; **MP3 generation and storefront listing** ship via **Google Play brand admin** for supported languages (outside Phoenix cell grid).  
- **Podcast:** **separate planning track** — not counted in the **222** regular cells (marketing SSOT cadence remains orthogonal).  
- **Video:** retained in Phase 2 **TSV / marketing** rollups as planning stubs (`video_short` / `video_long` columns) but is **not** part of the **222** Phoenix ebook+manga cell definition.  
- **Japan manga-only parallel catalog:** **37** additional cells (**37 × ja_JP × manga** only) — **same 37 `brand_id` values** as the regular catalog, **different** distribution legal entity + storefront stack (Line Manga primary + other JP manga platforms). See `docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md`. **Total Phoenix-planned cells = 222 + 37 = 259.**

**Anti-drift:** Any future document that calls **555** cells or treats **audiobook** as a Phoenix cell is **superseded** by this amendment unless a new operator **AMENDMENT** explicitly revives a different denominator.

Each **cell** in the 222-grid carries: enabled flag, series depth (where applicable), unit counts, teacher/author association coverage, and downstream asset hooks (covers, manga protagonists). The **37** Japan manga-only cells reuse the same per-brand narrative/voice/character IDs with a **manga-only** surface binding and separate distribution entity.

### 1.2 Phase 2 default counts (operator Q2 baseline)

Unless superseded by operator override (see Section 10 Q2):

| Surface | Rule |
|---------|------|
| ebook | **5** series × **5** books per series = **25** books per brand per `en_US` or `ja_JP` locale bucket |
| audiobook | **Out of Phoenix cells:** ebook script is the narration source; **Google Play brand admin** produces/ships MP3 for supported languages (not counted in the **222** / **259** cell model). |
| manga series | **Tier ladder:** flagship **14**, core **8**, niche **4** active series targets (aligned to PR #988 companion `parallel_image_generation_plan_2026-05-09.md` subsection 3.1 commentary + `canonical_brand_list.yaml` tier tags) |
| manga episodes | **24** serialization units per series per locale bucket (≈ bi-weekly cadence for one planning year; reconciles to `manga_brand_series_plan.yaml` global bi-weekly default without binding chapter math) |
| podcast | **26** episodes per brand per locale bucket (bi-weekly cadence for 12 months) — *marketing SSOT currently 0/wk pending Table 6* |
| video | **12** short + **4** long pieces per brand per locale bucket (weekly-ish short + monthly long planning stub) |

**zh bucket:** each `brand_id` row in `worldwide_catalog_plan_zh_2026-05-10.tsv` **sums zh_TW + zh_CN** parallel SKUs: `total_books`, `manga_series`, podcast, and video counts are **doubled** vs en_US rows; `covers_needed` = `2 × total_books` (KDP + paired retail cover workload for each CJK SKU; **audiobook MP3 still ships via Google Play brand admin**, not as a Phoenix cell). See `artifacts/qa/worldwide_catalog_plan_v1_methodology_2026-05-10.md` Section 3.

### 1.3 Locale enablement flags (default = all on)

| Locale bucket | en_US | ja_JP | zh_TW | zh_CN |
|---------------|-------|-------|-------|-------|
| Default Phase 2 | yes | yes | yes (via zh) | yes (via zh) |

Per-brand overrides are **not** applied in V1 matrices (all `enabled=yes`); future brand_admin toggles consume the same schema with `no` rows.

---

## 2. Per-brand profile (37)

For each Path X brand: **brand_id**, **tier + demographic** (from `canonical_brand_list.yaml`), **style_ref** (`brand_lora_plans.yaml`), **8 author/teacher associations** (target band 6–12; V1 uses eight deterministic anchors = named teacher + cross-teacher faculty + registry pen names), **locale flags**, **per-surface plan** (series/units/cadence), **manga protagonist note**.

### 2.1 `stillness_press`

- **Tier / demographic:** flagship / josei
- **Topic notes (canon):** Anxiety · somatic · sleep · josei adult women
- **style_ref:** style_sp (brand_lora_plans.brand_style_loras.stillness_press)
- **Lead voice:** `ahjan` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=14; episodes_per_series=24; **episodes_total=336** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (14 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.2 `cognitive_clarity`

- **Tier / demographic:** flagship / seinen
- **Topic notes (canon):** Overthinking · CBT-adjacent · seinen adult men
- **style_ref:** style_cc
- **Lead voice:** `joshin` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** joshin, ahjan, pamela_fellows, master_feung, miki, maat, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=14; episodes_per_series=24; **episodes_total=336** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (14 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.3 `digital_ground`

- **Tier / demographic:** flagship / manhwa
- **Topic notes (canon):** Burnout · tech worker · manhwa/webtoon
- **style_ref:** style_dg
- **Lead voice:** `miki` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** miki, ahjan, joshin, pamela_fellows, master_feung, maat, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=14; episodes_per_series=24; **episodes_total=336** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (14 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.4 `sleep_restoration_iyashikei`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Sleep · night · rest
- **style_ref:** style_sr (maps sleep_restoration lane)
- **Lead voice:** `master_sha` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** master_sha, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.5 `somatic_wisdom_shojo`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Somatic healing · body memory
- **style_ref:** style_sw (somatic_wisdom)
- **Lead voice:** `pamela_fellows` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** pamela_fellows, ahjan, joshin, master_feung, miki, maat, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.6 `relational_calm_iyashikei`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Social anxiety · relationships
- **style_ref:** style_rc (relational_calm)
- **Lead voice:** `junko` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** junko, ahjan, joshin, pamela_fellows, master_feung, miki, maat, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.7 `healing_ground_healing`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Grief · general healing
- **style_ref:** style_hg (healing_ground)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.8 `body_memory_shojo`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Somatic trauma · body-held grief
- **style_ref:** style_bm (body_memory)
- **Lead voice:** `omote` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** omote, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.9 `minimal_mind_healing`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** Overthinking · mindfulness · minimal
- **style_ref:** style_min (minimal_mind)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.10 `night_reset_healing`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Sleep · anxiety · night routines
- **style_ref:** style_nr (night_reset)
- **Lead voice:** `master_sha` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** master_sha, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.11 `gentle_growth_healing`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Self-worth · imposter-adjacent · shojo-lean
- **style_ref:** style_gg (gentle_growth)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.12 `stabilizer_healing`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** Burnout recovery · regulation
- **style_ref:** style_stab (stabilizer)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.13 `career_lift_workplace`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Imposter · workplace · josei
- **style_ref:** style_cl (career_lift)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.14 `high_performer_workplace`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** Burnout · financial anxiety · performance
- **style_ref:** style_hp (high_performer)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.15 `executive_calm_workplace`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** Burnout · overthinking · executive
- **style_ref:** style_ec (executive_calm)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.16 `morning_momentum_workplace`

- **Tier / demographic:** core / shonen
- **Topic notes (canon):** Burnout · motivation · shonen
- **style_ref:** style_mm (morning_momentum)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.17 `optimizer_workplace`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** Overthinking · productivity
- **style_ref:** style_opt (optimizer)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.18 `focus_sprint_workplace`

- **Tier / demographic:** core / seinen
- **Topic notes (canon):** ADHD · focus
- **style_ref:** style_fs (focus_sprint)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.19 `heart_balance_shojo`

- **Tier / demographic:** core / josei
- **Topic notes (canon):** Social anxiety · relationships · boundaries
- **style_ref:** style_hb (heart_balance)
- **Lead voice:** `maat` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** maat, ahjan, joshin, pamela_fellows, master_feung, miki, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=8; episodes_per_series=24; **episodes_total=192** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (8 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.20 `trauma_path_healing`

- **Tier / demographic:** niche / josei
- **Topic notes (canon):** Grief · trauma · clinical-safe register
- **style_ref:** style_tp (trauma_path)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.21 `resilient_parent_social`

- **Tier / demographic:** niche / josei
- **Topic notes (canon):** Burnout · parenting · self-worth
- **style_ref:** style_rp (resilient_parent)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.22 `confidence_core_romance`

- **Tier / demographic:** niche / shojo
- **Topic notes (canon):** Imposter · self-worth · romance register
- **style_ref:** style_cc2 (confidence_core)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.23 `relationship_clarity_romance`

- **Tier / demographic:** niche / josei
- **Topic notes (canon):** Social anxiety · boundaries · intimacy
- **style_ref:** style_rel (relationship_clarity)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.24 `adhd_forge_mystery`

- **Tier / demographic:** niche / shonen
- **Topic notes (canon):** ADHD · focus · courage
- **style_ref:** style_af (adhd_forge)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.25 `devotion_path_shonen`

- **Tier / demographic:** niche / shonen
- **Topic notes (canon):** Spiritual courage · shonen
- **style_ref:** style_dp (devotion_path)
- **Lead voice:** `sai_ma` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** sai_ma, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.26 `stoic_edge_battle`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Courage · resilience · battle register
- **style_ref:** style_se (stoic_edge)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.27 `warrior_calm_cultivation`

- **Tier / demographic:** niche / shonen
- **Topic notes (canon):** Burnout · inner peace · cultivation
- **style_ref:** style_wc (warrior_calm)
- **Lead voice:** `master_wu` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** master_wu, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.28 `spiritual_ground_supernatural`

- **Tier / demographic:** niche / josei
- **Topic notes (canon):** Grief · devotion · supernatural-everyday
- **style_ref:** style_sg (spiritual_ground)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.29 `solar_return_isekai`

- **Tier / demographic:** niche / shonen
- **Topic notes (canon):** Self-worth · isekai framing
- **style_ref:** style_so (solar_return)
- **Lead voice:** `ra` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** ra, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.30 `legacy_builder_memoir`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Self-worth · purpose · memoir register
- **style_ref:** style_lb (legacy_builder)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.31 `bio_flow_healing`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Body · biology · somatic-science
- **style_ref:** style_bf (bio_flow)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.32 `longevity_lab_healing`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Health · aging · lab register
- **style_ref:** style_ll (longevity_lab)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.33 `hormone_reset_healing`

- **Tier / demographic:** niche / josei
- **Topic notes (canon):** Hormonal · somatic · josei
- **style_ref:** style_hr (hormone_reset)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.34 `qi_foundation_cultivation`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Eastern somatic · qi · cultivation
- **style_ref:** style_qf (qi_foundation_cultivation)
- **Lead voice:** `master_feung` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** master_feung, ahjan, joshin, pamela_fellows, miki, maat, junko, master_wu
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.35 `creative_unfold_social`

- **Tier / demographic:** niche / shojo
- **Topic notes (canon):** Social anxiety · creativity
- **style_ref:** style_cu (creative_unfold)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.36 `calm_student_school`

- **Tier / demographic:** niche / shojo
- **Topic notes (canon):** Anxiety · study · school
- **style_ref:** style_cs (calm_student)
- **Lead voice:** `composite_faculty` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** composite_faculty, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)

### 2.37 `bright_presence_tw_seinen`

- **Tier / demographic:** niche / seinen
- **Topic notes (canon):** Taiwan-forward social anxiety · seinen
- **style_ref:** style_tw TBD (Taiwan lane; align to locale_brand_names / bright_presence)
- **Lead voice:** `adi_da` (registry: `config/teachers/teacher_registry.yaml`; LoRA notes: `brand_lora_plans.yaml.character_loras` when present)
- **Author / teacher pack (8 of 6–12 target):** adi_da, ahjan, joshin, pamela_fellows, master_feung, miki, maat, junko
- **Per-locale enabled (default):** en_US yes; ja_JP yes; zh_TW yes; zh_CN yes (planned via combined zh TSV row)
- **ebook:** series_count=5; books_per_series=5; **total=25** / locale (50 across zh bucket per TSV)
- **audiobook:** **not a Phoenix cell** — ebook script doubles as narration script; **Google Play brand admin** output path for MP3 (see §1.1).
- **manga:** series_count=4; episodes_per_series=24; **episodes_total=96** / locale (double in zh bucket per TSV)
- **Manga protagonist note:** One protagonist identity per manga series (4 series). Lock via `config/manga/character_design_axes.yaml` + `character_design_template.yaml` when `character_design` YAML exists on series profiles; until then use `brand_lora_plans.yaml.protagonist_loras` / `character_loras` notes as the authoring seed.
- **podcast:** 26 episodes @ ~bi-weekly cadence (placeholder until `weekly_volumes_per_brand.yaml` non-zero)
- **video:** short=12; long=4 (per locale bucket; doubled in zh TSV)


---

## 3. Per-locale matrix (rollup)

### 3.0 Packaged-asset planning totals (operator cell-math correction 2026-05-10)

- **Retired deck anchor (superseded):** **45,216** “total worldwide packaged-asset target” was computed from the retired **555** (37×3×5) cell model in `brand-wizard-app/public/pearl_prime_v6-3-en.html` (PR #1027 lineage) — **do not use for Phoenix cell authority.**  
- **Revised planning scalar (illustrative):** rescale the legacy numerator by the new cell ratio **259 ÷ 555** → **45,216 × (259÷555) ≈ 21,109** → **21,100** rounded for operator-facing slides (see same HTML update in this PR). This is a **budget-shape** correction until Pearl_Marketing recomputes per-surface SSOT after Table 6 ratification.  
- **Locale column split (same 1 : 1 : 2 script-weight story as the prior deck):** **4,521 / 4,521 / 9,044** for **en_US / ja_JP / zh** on the **regular 222-cell** spine; **+3,014** reserved-shape bucket for the **37** Japan manga-only parallel cells → **≈21,100** combined headline.

Source: TSV header sums (methodology document Section 5 cross-check) — tables below remain the **SKU-depth** SSOT for generators; **§3.0** is the **cell + headline asset** correction layer.

### 3.1 en_US

| Metric | Total |
|--------|------:|
| brands enabled | 37 |
| ebook books | 925 |
| audiobook books | 925 |
| manga series | 242 |
| manga episodes | 5,808 |
| podcast episodes | 962 |
| video shorts | 444 |
| video longs | 148 |
| retail cover pair (KDP + audiobook) | 1,850 |
| manga main character identities | 242 |

### 3.2 ja_JP

Same numeric rollup as en_US at this baseline (localization labor differs; units match).

### 3.3 zh (zh_TW + zh_CN combined)

| Metric | Total |
|--------|------:|
| brands enabled | 37 |
| ebook books (both CJK SKUs) | 1,850 |
| audiobook books | 1,850 |
| manga series (both markets) | 484 |
| manga episodes | 11,616 |
| podcast episodes | 1,924 |
| video shorts | 888 |
| video longs | 296 |
| retail cover assets | 3,700 |
| manga main character identities | 484 |

---

## 4. Author / teacher associations

### 4.1 Cross-reference (teacher → brand style anchors)

| teacher_id | style_ref / brand anchor (character_loras.style_ref) | Bio status | en_US | ja_JP | zh |
|------------|---------------------------------------------------------|------------|-------|-------|-----|
| ahjan | stillness_press | registry full | y | y | y |
| joshin | cognitive_clarity | registry full | y | y | y |
| pamela_fellows | somatic_wisdom (→ `somatic_wisdom_shojo`) | registry full | y | y | y |
| master_feung | qi_foundation_cultivation | registry full | y | y | y |
| miki | digital_ground | registry full | y | y | y |
| maat | heart_balance (→ `heart_balance_shojo`) | registry full | y | y | y |
| junko | relational_calm (→ `relational_calm_iyashikei`) | registry full | y | y | y |
| master_wu | warrior_calm (→ `warrior_calm_cultivation`) | registry full | y | y | y |
| master_sha | sleep_restoration (→ `sleep_restoration_iyashikei` / `night_reset_healing`) | registry full | y | y | y |
| omote | body_memory (→ `body_memory_shojo`) | registry full | y | y | y |
| ra | solar_return (→ `solar_return_isekai`) | registry full | y | y | y |
| sai_ma | devotion_path (→ `devotion_path_shonen`) | registry full | y | y | y |
| adi_da | bright_presence_tw (→ `bright_presence_tw_seinen`) | registry full; **character_design V1.1 gate** | y | y | y |

**Pen-name economy anchors:** `config/author_registry.yaml` (16 listed pen-name ids sampled in Section 2 packs). `pen_name_teacher_profiles.yaml` documents **methodology citations**, not a teacher row count.

### 4.2 Gap analysis vs 6–12 authors / brand

- **V1 packs ship 8** named rows per brand (within the 6–12 band).  
- **Gap class A — non-teacher brands (25/37):** no `character_loras` entry; need **Pearl_Writer / brand_admin** to promote composite + pen-name bios from `draft` → `full`.  
- **Gap class B — `character_design` YAML:** `artifacts/qa/pearl_star_v2_install_log_2026-05-07.md` notes **0** series YAMLs with `character_design:` blocks; **12-axis vocabulary exists** (`character_design_axes.yaml`) but content is **missing**.  
- **Gap class C — adi_da renders:** Architect cap requires explicit V1.1 binding before unattended renders (`PEARL_ARCHITECT_STATE.md` TEACHER-MANGA note).

---

## 5. Cover art needs (Pearl Prime book lane × locales)

### 5.1 Counting rule

- **KDP / ebook cover:** one unique render per ebook title × locale SKU.  
- **Audiobook cover:** paired 1:1 with ebook (per PR #988 companion `parallel_image_generation_plan_2026-05-09.md` subsection 3 `audiobook_cover` target parity).  
- **Retail cover asset total per locale bucket:** `covers_needed` column in TSV (= `2 × total_books` for en/ja; `2 × total_books` with zh `total_books` already doubled for TW+CN SKUs).

### 5.2 Cross-reference to PR #988 inventory / gap headlines

| Gap | Evidence | Plan response |
|-----|-----------|---------------|
| KDP workflow JSON | PR #988 companion plan Section 2 — no dedicated `flux_kdp_cover.json` | Add workflow under `ws_image_batch_generation_orchestration_20260509` before batch |
| zh manga readiness | `manga_catalog_summary.json` — many `blocked_lora` rows for zh_TW/zh_CN | Phase 2.3 prioritizes LoRA + protagonist unlock before zh manga wave |
| Cover target 800 vs 25-book baseline | PR #988 uses **800** `kdp_cover` / `(brand×locale)` for historical catalog volume | Operator must reconcile **800-row catalog physics** vs **25-book Phase-2 slice** (Q2) — pick one SSOT for dashboard |

---

## 6. Manga main character needs

| Need | Plan |
|------|------|
| Description | Author 12-axis YAML per series (`CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md`; vocab `config/manga/character_design_axes.yaml`) |
| Reference image | `main_character.png` + `lora_refs/` per `brand_lora_plans.yaml.protagonist_loras` when defined |
| Existing assets | Cross-check `assets/manga_catalog/.../main_character.png` + `artifacts/catalog/manga/*_manga_catalog.csv` + future inventory TSV from PR #988 |

**Inventory snapshot (2026-04-29 generator):** en_US **170** series rows; ja_JP **166**; zh_TW **275** (191 ready / 84 blocked); zh_CN **269** (200 ready / 69 blocked) — counts **do not** equal Phase-2 target series ladder; delta is expected until matrix regeneration absorbs Path X tier targets.

---

## 7. Dashboard display requirements

### 7.1 Japan + US English first (per operator)

1. **Brand list** with active/inactive — shipped / partial per PR **#977 / #982** (`PEARL_PM_STATE.md`).  
2. **Per-brand → series list → main character thumbnail** — **NEW** workstream: consumes `main_chars_needed` + `assets/manga_catalog/.../main_character.png` + inventory status.  
3. **Per-brand → cover art gallery** — **NEW** workstream: consumes `covers_needed` + KDP/audiobook workflow outputs + `AUTHOR_COVER_ART_SPEC` / manga cover spec split.

### 7.2 zh dashboard

Same three panels after Phase 2.3; must display **TW vs CN** sub-columns where a single brand row maps to two SKUs.

---

## 8. Phasing

| Phase | Scope |
|-------|-------|
| 2.1 | en_US catalog complete + all en_US covers + all en_US manga protagonists |
| 2.2 | ja_JP catalog complete + ja_JP covers + ja_JP protagonists |
| 2.3 | zh catalog complete + zh covers + zh protagonists (TW+CN) |
| 2.4 | Full content production rollout (**podcast + video** surfaces at non-zero `weekly_volumes_per_brand.yaml` — **still orthogonal** to the **222** ebook+manga Phoenix cell grid; Japan manga-only program tracked under **PRJ-JAPAN-MANGA-ONLY-CATALOG-V1**) |

---

## 9. Volumes vs capacity (IMG-RENDER-DUAL-PATH-V1-01)

| Path | Role | Phase 2 note |
|------|------|--------------|
| Pearl Star | Tier 2 canonical renders; single GPU | Wall times scale linearly; wave model in PR #988 (~19.3 days @ 24/7 for illustrative full target) |
| RunComfy | Parallel paid lane; $10/mo soft cap | Dry-run + dashboard spend wiring per `PEARL_PM_STATE.md`; use for overflow after operator activation |

**Estimate (illustrative):** reuse PR #988 aggregate **~463 GPU-hours** equivalent for the **old** 4-locale photo plan; Phase 2 triple-locale book+manga targets require recomputation post Q2 ratification — **blocker:** operator must pick **25-book slice vs 800-cover legacy target** before scheduling.

---

## 10. Operator decisions (Q card)

Verbatim from program brief (answer in governance / operator session):

**Q1:** Phase order — en_US first, then ja_JP, then zh? OR parallel?

**Q2:** Per-brand series count default — propose 5 series per brand × 5 books per series = 25 books per brand × 37 brands × 3 locales = 2,775 books total. Override?  
*(Plan note: this master document uses **3,700** ebook SKUs when the zh bucket counts **separate zh_TW + zh_CN** editorial mirrors — 925 + 925 + 1,850. If Q2 intends **one** zh spine per brand, reset zh rows per methodology Section 2.5.)*

**Q3:** Manga main character source — generate from character_design vocab (auto) OR operator-supplied reference photos?

**Q4:** Author bio authoring source — Pearl_Writer (auto-generate) OR operator-curated?

---

## CLOSEOUT pointers (agent handoff)

- TSV row count **37** each — must match Section 2 brand subsections.  
- Aggregates: see Section 3 plus methodology document Section 5.  
- Next execution owners: Pearl_Marketing (Table 6 + SSOT), Pearl_Dev (dashboard WS), Pearl_Int (Pearl Star Step 4), Pearl_Editor (character_design A4).

---

## Appendix: brand-coverage-37 (allocation summary, 2026-05-11)

**Headline:** 25 Path X canonical brands have **no** `brand_genre_allocation.yaml` row in any locale today; only **12** teacher-aligned brands are materialized for en_US and ja_JP (and 12 + `bright_presence_tw` lane in zh_TW; 12 in zh_CN). Pearl_Conductor v3 wired only to matrix-backed brands therefore spans **12** brands, not **37**, until the generator extension lands.

**Proposed allocation (Pearl_PM + Pearl_Marketing):**

- Machine-readable grid: `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (**296** rows = 37 × 4 locales × 2 surfaces: `ebook` + `manga`).
- Gap narrative + locale matrix + surface-mix heuristics: `artifacts/qa/worldwide_catalog_37_brand_allocation_audit_2026-05-11.md`.
- Manga-only / missing-brand allocation rules: `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md`.

**Gap counts (Path X canonical vs genre matrix):** en_US **25** missing; ja_JP **25** missing; zh_TW **24** missing (13 of 37 present, including `bright_presence_tw` → `bright_presence_tw_seinen`); zh_CN **25** missing.

**Incremental surface rows proposed for the 25 missing brands:** **200** (25 × 4 locales × 2 surfaces) at default **5 series × 5 units** per cell in the TSV (`V1.1_proposed`), pending operator Q2 override to tier ladder in Section 1.2 of this document.

**Operator decisions (catalog-scale program — addendum to Section 10):**

- **Q1:** 25 missing brands — ship all in V1.1 (parallel with existing 12), OR phase to V1.2?
- **Q2:** Default series count per missing brand (5 series × 5 episodes = 25 books-equivalent)? Override per-brand?
- **Q3:** Locale priority for missing brands — en_US first (per locale-first), OR all 4 locales simultaneously?
- **Q4:** blocked_lora / blocked_score follow-up — Pearl_Dev priority order?

**Cross-reference:** PR **#1035** catalog planning status diagnostic (per-market authored row counts).

---

## §AMENDMENT-2026-05-11-V1-1-RATIFICATION

**Authority:** `docs/PEARL_ARCHITECT_STATE.md` → **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01** → **AMENDMENT-2026-05-11-V1-1-37-BRAND-ACTIVATION**. **BINDING:** Q1–Q4 ratified below; **37** Path X `brand_id` values **frozen**; **Pearl_Conductor v3** firing **gated** on action items **a** + **b** + **c** (see §6).

**Operator decisions (verbatim — ratified 2026-05-11):**

- **Q1** = **V1.1** (ship all **25** missing alongside existing **12**; single Phase 2 wave).
- **Q2** = **approve** (**5** series × **5** episodes per brand-locale-surface; default).
- **Q3** = **parallel-locales** (all **4** locales simultaneously per brand).
- **Q4** = **blocked_lora-first** (**zh_TW** + **zh_CN** `blocked_lora` cleanup before `blocked_score`).

### 1. PHASE 2 V1.1 SCOPE (Q1=V1.1 single wave)

- All **37** Path X canonical brands ship in **V1.1** (**12** existing teacher brands + **25** missing manga-only/category brands).
- **V1.1** wave produces **200** **NEW** brand-locale-surface cells (**25** brands × **4** locales × **2** surfaces) **ON TOP OF** existing **12**-brand × **4**-locale × **2**-surface = **96** cells.
- **Total V1.1 cells: 296** (per **PR #1037** TSV row count: `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`).
- **V1.2 deferred:** **NOT** a deferred-brand pile; reserved for **surface expansion** (e.g., adding **video** to brands that currently have **ebook+manga**).
- **Anti-drift:** do **NOT** spawn **V1.2-deferred-brand** workstreams; if any agent surfaces “ship **25** brands later,” that violates **Q1=V1.1** ratification.

### 2. BRAND VOLUMES (Q2=approve default 5×5)

- Default per brand-locale-surface: **5** series × **5** episodes = **25** content units.
- Total **V1.1** content units (excluding existing **12**): **200** cells × **25** units = **5,000** new content units.
- Plus existing **12** brands × **4** locales × **2** surfaces × **25** units = **2,400** (or already partially produced).
- **TOTAL V1.1 target: ~7,400** content units worldwide (**en_US** + **ja_JP** + **zh_TW** + **zh_CN** regular catalogs).
- **Note:** Japan-manga-only catalog (**37** cells, separate cap, parallel program) is **NOT** counted in **V1.1** worldwide totals; it runs as **`PRJ-JAPAN-MANGA-ONLY-CATALOG-V1`**.
- **Anti-drift:** per-brand volume override requires **AMENDMENT** (not silent edits to TSV).

### 3. LOCALE PARALLELISM (Q3=parallel-locales)

- All **4** locales (**en_US**, **ja_JP**, **zh_TW**, **zh_CN**) generate **simultaneously** per brand.
- **Pearl Star** + **RunComfy** dual-path handles concurrent dispatch (per **IMG-RENDER-DUAL-PATH-V1-01** + **AMENDMENT-2026-05-10-PATH-BY-WORKFLOW**).
- **Cost expectation:** RunComfy **$10/mo** cap will be exercised more aggressively than serial-locale approach; **Pearl Star** handles overflow.
- **Anti-drift:** any agent that switches to **serial-locale** (**en-first**) without operator **AMENDMENT** violates **Q3**.
- **Pearl_Conductor v3** (when fired) **MUST** honor **parallel-locale** dispatch order.

### 4. CLEANUP PRIORITY (Q4=blocked_lora-first)

**Pearl_Dev** priority order:

1. **zh_TW** + **zh_CN** `blocked_lora` rows (**~150** total per **PR #1035** audit).
2. **zh_TW** `blocked_score` rows (**160** per audit).
3. **ja_JP** `warrior_calm` tentpole mismatch (single-brand metadata fix).

**Rationale:** `blocked_lora` blocks **all** rendering for those rows; `blocked_score` blocks promotional metadata but **doesn't** gate renders.

**Anti-drift:** do **not** interleave `blocked_score` before `blocked_lora` unless operator **AMENDMENT**.

### 5. STATUS TRANSITIONS

- Cap entry **WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01:** continues as **ACTIVE** (**Phase 1 P0** complete via **#1022**; **Phase 2** begins now).
- Workstreams ratified to **runnable** per **Q1**:
  - `ws_catalog_generator_extend_to_37_brands_20260511` → **runnable** (**Pearl_Dev**; the most critical-path ws).
  - `ws_zh_manga_blocked_lora_followup_20260511` → **runnable** (**Pearl_Dev**; per **Q4** priority).
  - `ws_zh_manga_blocked_score_followup_20260511` → **status=queued** (waits on `blocked_lora` completion).
- **NEW** workstreams opened by this **AMENDMENT**:
  - `ws_catalog_generator_v1_1_25_brand_authoring_20260511` → **runnable** (**Pearl_Marketing**; authors per-brand series themes for the **25** missing brands).
  - `ws_pearl_conductor_v3_full_queue_activation_20260511` → **status=queued_after_v1_1_authoring** (**Pearl_Dev**; fires unattended generation once **25**-brand themes authored + generator extended + `blocked_lora` cleared).
  - `ws_warrior_calm_ja_jp_tentpole_fix_20260511` → **status=queued** (**Pearl_Editor**; small metadata fix).

### 6. ACTION ITEMS (named for next-router fan-out; not authored here)

| ID | Owner | Action |
|---|---|---|
| **a.** | **Pearl_Dev** | Extend catalog generator to **37** Path X brands (consume **PR #1037** TSV; mirror `music_mode_branch.py` pattern from **#1008**). |
| **b.** | **Pearl_Marketing** | Author per-brand series themes for the **25** missing brands (e.g., `healing_ground` series titles, workplace brands' topic anchors, romance brands' arc shapes). |
| **c.** | **Pearl_Dev** | Clear **zh_TW** + **zh_CN** `blocked_lora` rows (**~150** rows) — likely LoRA training or asset gating fix. |
| **d.** | **Pearl_Editor** | **ja_JP** `warrior_calm` tentpole metadata fix (single-brand). |
| **e.** | **Pearl_Dev** (after **a**+**b**+**c**): | **Pearl_Conductor v3** prompt — full-queue unattended generation against all **37** × **4** locales × **2** surfaces (estimated **5–10** days wall on **Pearl Star** + **RunComfy** under **$10** cap). **DO NOT** spawn / fire **v3** until **a**, **b**, and **c** are satisfied — governing **AMENDMENT** is the gate. |
| **f.** | **Pearl_Brand** | Dashboard updates to surface **37**-brand status + **V1.1** progress per brand. |
| **g.** | **Pearl_Architect** | Closeout **AMENDMENT** once **V1.1** completes (target: **7,400** content units shipped; first end-to-end worldwide brand catalog ratified at **100%**). |

**Cross-reference:** **PR #1037** (allocation plan); **PR #1035** (status diagnostic); **PR #1022** (Phase 1 P0 closure); **AMENDMENT-2026-05-10-PATH-BY-WORKFLOW** (dual-path routing); `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md`.


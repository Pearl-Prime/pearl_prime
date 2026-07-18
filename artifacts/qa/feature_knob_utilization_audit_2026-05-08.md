# Feature / knob utilization audit — catalog planner → assembler → per-platform output

**PROJECT_ID:** PRJ-PEARL-PRIME-FEATURE-UTILIZATION-AUDIT  
**Subsystem:** core_pipeline (primary); recommendations; brand_admin; cross-cutting  
**Audit date:** 2026-05-08  
**Method:** Static read-only trace (no runtime execution). No code or config changes.

---

## STARTUP_RECEIPT

| Field | Value |
|--------|--------|
| Agent role | Pearl_Architect (audit-only) |
| `ACTIVE_PROJECTS.tsv` | Project id **not** present at `artifacts/coordination/ACTIVE_PROJECTS.tsv` (2026-05-08 snapshot). **Recommend** Pearl_PM append one row per coordination protocol. |
| Worktree directive | Target worktree `/Users/ahjan/phoenix_omega_qi_foundation_recon_wt`: `git status` did not return within 30s (likely lock/scale). **Evidence gathering** used read-only file reads under `/Users/ahjan/phoenix_omega` paths only (no `git write-index` / commit from that tree in this session). |
| Authority docs reviewed (headings / anchors) | `docs/DOCS_INDEX.md`; `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`; `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`; `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`; `specs/PHOENIX_V4_5_WRITER_SPEC.md` (spot-checked for arc-first / stage contracts — detailed line-level cite below only where directly tied to a code path). |

---

## Phase 1 — Declared feature / knob surface

### Table 1 — Declared feature surface

One row per **logical dimension** (grouped where the file enumerates a closed set). `value_count` is the number of distinct legal keys/entries observed in-repo for that dimension. **Sample values** abbreviate for space.

| file | dimension_name | value_count | sample_values | spec_anchor |
|------|----------------|------------:|---------------|-------------|
| `config/format_selection/format_registry.yaml` | `default_slot_definitions` beat row | 1 (template list) | HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION | Phoenix arc-first + slot contract (OMEGA / canonical spec stack referenced in file header L1–L6) |
| same | `structural_formats` ids F001–F015 | 15 | F006, F015, F001 | Same; file L12–L89 |
| same | `runtime_formats` ids | 20 | `standard_book`, `micro_book_15`, `deep_book_4h` | Same; file L95–L119+ |
| `config/angles/angle_registry.yaml` | `angles.*.arc_variant` (+ framing fields per angle) | 4 | WRONG_PROBLEM, MAP_PROMISE, HIDDEN_TRUTH, ONE_LEVER | DEV SPEC ANGLE INTEGRATION (file L1–L3) |
| `config/source_of_truth/recurring_motif_bank.yaml` | `motifs` ids | 6 | motif_pattern, motif_cost, motif_body | Structural Variation V4 (file L1–L7) |
| `config/catalog_planning/platform_knob_tuning.yaml` | `platform_profiles` ids | 14 | audible, spotify, apple_books | `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md` (file L2–L6) |
| same | per-profile `preferred_runtimes` | 14 lists | `[standard_book, extended_book_2h]` | same; e.g. file L14–L16 |
| same | per-profile `preferred_formats` | 14 lists | `[F006, F003, F004]` | same; e.g. file L15–L16 |
| same | per-profile `preferred_structures` | 14 lists | promise_engine, atomic | same; e.g. file L16–L17 |
| same | per-profile `preferred_journey_shapes` | 14 lists | recognition_to_agency | same; e.g. file L17–L18 |
| `config/catalog_planning/canonical_topics.yaml` | `topics` list | 57 | anxiety, impermanence, forest_refuge | File L1–L40 (expansion note L7–L10) |
| `config/catalog_planning/canonical_personas.yaml` | `personas` list | 13 | corporate_managers, gen_z_professionals | File header + list body (see load in Pearl Prime generator § below) |
| `config/catalog_planning/teacher_topic_persona_scores.yaml` | composite topic/persona scoring grid | varies by teacher | threshold 0.70 in consumer | `generate_pearl_prime_book_script_catalog.py` L26–L29, L202–L224 |
| `config/recommender/scoring_weights.yaml` | numeric weight knobs | 5 | topic_weight, persona_weight, series_bonus_weight | File L1–L6 |
| same | threshold knobs | 2 | strong_fit_threshold | same |
| `config/recommender/constraints.yaml` | (declared recommender constraints) | file present | _(not enumerated line-by-line in this audit pass)_ | Directory listing: `config/recommender/` |
| `config/recommender/hard_gates.yaml` | hard gates | file present | — | same |
| `config/manga/canonical_brand_list.yaml` | brand allowlist for manga ops | file present | — | Manga governance stack |
| `config/manga/brand_lora_plans.yaml` | LoRA plan refs | file present | — | Manga image pipeline |
| `config/authoring/pen_name_teacher_profiles.yaml` | teacher voice metadata | file present | — | Writer / teacher mode |
| `config/authoring/teacher_brand_archetypes.yaml` | (referenced from catalog planning) | file present | — | Brand/teacher matrix |
| `config/quality/refrain_allowlist.yaml` | refrain policy | file present | — | Quality/EI |
| `config/quality/ei_v2_config.yaml` | EI v2 parameters | file present | — | `phoenix_v4/quality/ei_v2/` consumers |
| `config/video/format_specs.yaml` | video format specs | file present | — | Video pipeline |
| `config/video/render_params.yaml` | render params | file present | — | Video pipeline |
| `config/localization/locale_registry.yaml` | locale ids | file present | — | `CatalogPlanner` locale validation |
| `config/localization/quality_contracts/` | per-locale contracts | dir present | — | Localization QA |
| `config/catalog_planning/domain_definitions.yaml` | domain ids for Stage 1 | file present | — | `catalog_planner.py` L3–L4 |
| `config/catalog_planning/series_templates.yaml` | series → angles/domain | file present | — | `catalog_planner.py` L256–L257 |
| `config/catalog_planning/capacity_constraints.yaml` | capacity | file present | — | `catalog_planner.py` L257 |
| `config/pipeline/knob_apply_contract.py` | Python contract for knob application | module | — | Knob shaping (`knob_apply.py`) |
| `config/knobs/topic_knob_profiles.yaml` | topic-level knob defaults | file present | — | Knob ecosystem |
| **Missing expected path** | `config/format_registry.yaml` | **0** | **n/a — file does not exist** | Operators/docs that cite `config/format_registry.yaml` should use `config/format_selection/format_registry.yaml` (see `format_selector.py` L61–L62; `generate_full_catalog.py` L85–L86). |

**Phase 1 dimension row count (Table 1):** **27** populated rows + **1** explicit missing-path finding row = **28** table rows. (If each sub-list under `platform_profiles` were exploded further, the declared surface would be larger; this table stays at one row per major axis group.)

---

## Phase 2 — Catalog planner coverage

### Planners in scope

| Planner / generator | Role | Primary outputs |
|----------------------|------|----------------|
| `scripts/catalog/generate_full_catalog.py` | Broad lane × brand catalog | `artifacts/catalog/full_catalog.csv` columns `CATALOG_FIELDS` |
| `scripts/catalog/generate_pearl_prime_book_script_catalog.py` | Pearl Prime script rows | `{locale}_catalog.csv` via `COLUMNS` |
| `scripts/catalog/generate_manga_catalog.py` | Manga allocation matrix expansion | `{locale}_manga_catalog.csv` |
| `scripts/catalog/projection_planner.py` | 52-week projection | JSON plan (formats per week — not manuscript knobs) |
| `phoenix_v4/planning/catalog_planner.py` | Stage 1 `BookSpec` (runtime pipeline) | In-memory struct consumed by `run_pipeline.py` |

**Absent script (explicit):** `scripts/catalog/build_high_confidence_catalog.py` — **does not exist** in tree (glob check returned absent).

### Table 2 — Catalog planner coverage (Phase 1 dimensions → planner READ / WRITE)

| Phase 1 dimension (group) | generate_full_catalog | generate_pearl_prime_book_script_catalog | generate_manga_catalog | CatalogPlanner (runtime Stage 1) | column / output field if written |
|---------------------------|------------------------|------------------------------------------|-------------------------|-----------------------------------|----------------------------------|
| structural_format F001–F015 | READ partial via `format_registry` loader L85–L86; WRITE **no dedicated column** | READ format_registry L132; no column for F00x | NO | INDIRECT via downstream format selector later, not CSV | dropped from CSV layer |
| runtime_format vocabulary | READ + maps to rows `format_id`, `runtime_format_id` (`CATALOG_FIELDS` L1380–L1385) | READ + column `runtime_format` (`COLUMNS` L89) | Uses `series_format` enum locally (see below) — not format_registry ids | locale default only | consumed as strings on CSV rows |
| `angle_registry` angle ids | NO | NO | NO | `_derive_angle` never consults YAML registry — see L441–L495 | **`angle_id` not in Pearl/full CSV schemas** → dropped at catalog CSV layer |
| `recurring_motif_bank` motif ids | NO | NO | NO | NO | dropped at all listed planners |
| `platform_profiles` knobs | NO | NO | NO | NO | dropped |
| recommender YAMLs (`config/recommender/*`) | NO | NO | NO | NO | dropped for these planners (**no** `grep` hits under `scripts/catalog/*.py`) |
| canonical topics/personas | YES via archetype + templates | YES explicit loaders L126–127 | Uses genreallocation + brand YAMLs (not canonical_topics directly in first 120 lines); catalog header references brand matrix | Validates locale against registry; persona/topic supplied by caller | topic/persona columns in both book CSV schemas |
| `domain_definitions` / `series_templates` | NO (different planning path) | NO | NO | YES L255–L264 | BookSpec.domain_id / angle_id derivation L400–417 |
| teacher composite scores YAML | NO | YES `teacher_topic_persona_scores.yaml` L128 | NO | NO | Pearl Prime readiness / blockers |
| manga brand / lora / visual grammar declarative configs | touches `canonical_genre_list` loader L133 | NO | Rows reference allocation YAML + pacing refs — does not flatten entire brand_lora into columns | NO | manga CSV cols `visual_grammar`, `lora_plan_ref`, … (`COLUMNS` L111–L118) |

**Gap classifications (aggregate):**

- **Operational CSV generators flatten** editorial / structural knobs to identifiers useful for storefronts/scheduling (**topic**, **persona**, **runtime/format strings**, pricing text) — not full Stage 2/3 knobs.
- **Runtime Stage 1 `CatalogPlanner`** consumes a **narrow slice** of `config/catalog_planning` (domains/series/capacity/brand locale extensions) for `BookSpec` and **does not** load motif bank, angle registry, recommender configs, or platform tuning — see constructor paths `catalog_planner.py` L245–L272.

---

## Phase 3 — Per-platform assembler coverage

Platforms are traced by **representative entrypoints** listed in the operator brief.

### Table 3 — Per-platform assembler coverage

Rows = consolidated Phase‑1 knobs; columns = consumed / partial / dropped / n/a / not_yet_implemented.

| Dimension | Book / `run_pipeline` spine | Pearl Prime CSV-driven ops | Full / Pearl CSV row only (no CLI) | Manga assembler | Audiobook scripts | Video scripts | Podcast |
|-----------|----------------------------|----------------------------|-------------------------------------|-----------------|-------------------|---------------|---------|
| `topic_id` / topic column | consumed (CLI `--topic` → Stage 1) `run_pipeline.py` L1812–L1818 | CSV has `topic` / `topic_id` | consumed if operator maps row→CLI manually | series YAML + catalog row genre axis | partial via `canonical_topics` in showcase | partial `run_flux_bank_build.py` loads canonical_topics L48 | n/a / not_yet_implemented |
| `persona_id` | consumed L1812–L1818 | CSV `persona` | partial (needs manual bridge) | profile objects (`profile_loader.py` L77–L93) | partial | partial | n/a |
| `angle_registry` | **partial** — `angle_id` on `BookSpec`; `resolve_arc_from_angle` exists `format_selector.py` L330–L341 but registry rarely lists `arc_path` today (`angle_registry.yaml` sample shows commented `arc_path` L10–L11) | **dropped** (not in `COLUMNS` L78–102) | dropped | dropped | dropped | dropped | n/a |
| structural format F00x | consumed Stage 2 `FormatSelector` `format_selector.py` L53–L66 | not in CSV | dropped unless separate arc/spec | dropped from manga CSV (uses `series_format` string) | dropped | dropped | n/a |
| runtime format | consumed Stage 2 + knob shaping | `runtime_format` column L89 | partial | `series_format` heuristic `generate_manga_catalog.py` L76–L109 | dropped in sampled script | dropped | n/a |
| motif bank | consumed when `select_variation_knobs` succeeds — merged into `format_plan_dict` `motif_id` `run_pipeline.py` L2055–L2097 + compiler reads bank `assembly_compiler.py` L354–L372 | **dropped** | dropped | manga_compat metadata on motifs `recurring_motif_bank.yaml` L5–L7; enforcement via `profile_aware_selector.py` L34–L38 | dropped | dropped | n/a |
| platform_knob_tuning | **partial** — used in `knob_apply.apply_knobs` audit path `_platform_narrative_conflict` L557–L584 and optional biasing in `variation_selector` (see file L133–L141) | dropped | dropped | not observed in sampled manga loaders | dropped | dropped | n/a |
| recommender weights | dropped in catalog generators | dropped | dropped | dropped | dropped | dropped | n/a |
| audiobook-/video-specific quality contracts | Stage 3 book compiler not specialized as audiobook mux in this trace | CSV does not declare audio mastering knobs | dropped | n/a | partial (bundle generator focuses on showcases) | partial | n/a |

**Key architectural observation (binding):** The **canonical assembler** for long-form books is `scripts/run_pipeline.py`, which hydrates **`BookSpec` + arc + YAML banks**, then runs **`variation_selector` + `assembly_compiler`** — see `run_pipeline.py` L1802–L1828 and L2055–2097. **Operational CSV catalogs** (`full_catalog.csv`, Pearl Prime `*_catalog.csv`) are **not** wired in this audit path as mandatory inputs to those stages; they remain **parallel planning artifacts**.

---

## Phase 4 — Prioritized gaps

Only rows where declared vocabulary **should** flow to assembler quality but is **flattened/dropped** at the catalog-to-run boundary or inconsistent across platforms.

### Table 4 — Prioritized gaps

| dimension | platform / path | current_state | target_state | user_cost | impl_cost | priority | recommended_owner_agent |
|-----------|-------------------|---------------|--------------|-----------|-----------|----------|-------------------------|
| `angle_id` + `angle_registry` semantic fields | Pearl Prime + full CSV → `run_pipeline` | CSV rows omit `angle_id`; Stage 1 defaults via `_derive_angle` **without** consulting `angle_registry.yaml` `catalog_planner.py` L441–L495 | Explicit angle per row OR deterministic join from topic/persona→registry | Wrong narrative frame / title angle drift; operator cannot shop by angle | M | **P0** | Pearl_Dev |
| Structural variation bundle (`motif_id`, `journey_shape_id`, `book_structure_id`, …) | CSV-only workflows | Knobs selected only when `run_pipeline` executes `select_variation_knobs` L2058–L2077; **not serialized** on Pearl/full CSV | Frozen knob columns OR sidecar JSON keyed by `catalog_id` | Platform fatigue / motif collisions invisible at planning time | M | **P0** | Pearl_Dev + Pearl_Architect schema pass |
| `platform_knob_tuning` | recommendation + schedule tooling | Declared for discoverability L2–L6; **not read** by `generate_full_catalog.py` / Pearl Prime generator | Planner reads profile per `market`/`platform_id` | Lost algorithmic fit (audible vs spotify) on planned rows | S–M | **P1** | Pearl_Research + Pearl_Dev |
| `config/recommender/*` | catalog generation | **No Python consumer** under `scripts/catalog/` in this grep pass | Optionally gate row emission | Rows ignore scored marketplace constraints | S | **P1** | Pearl_Dev |
| Doc path drift (`config/format_registry.yaml`) | all readers | Expected path absent — real path `config/format_selection/format_registry.yaml` | Single canonical path or symlink policy | Operators/scripts point at wrong file | S | **P2** | Pearl_GitHub / docs housekeeping |

---

## Phase 5 — Cross-cutting findings (with file:line evidence)

Count of bullet findings below: **12**.

1. **Angle vocabulary exists but Stage 1 planner does not load it.** `angle_registry.yaml` declares named angles (`WRONG_PROBLEM`, …) at L5–29, while `CatalogPlanner._derive_angle` matches only `series_templates` + small topic map — `catalog_planner.py` L441–L495 — never calls `angle_resolver.load_angle_registry` (`angle_resolver.py` L20–26).

2. **Arc-from-angle helper is layered but under-powered with current registry content.** `resolve_arc_from_angle` defers to `resolve_arc_path` `format_selector.py` L330–341; resolver returns default when no `arc_path` string (`angle_resolver.py` L70–76). Sample entries omit `arc_path` (`angle_registry.yaml` L10–L11 comment).

3. **Operational full-catalog schema omits structural-knob columns.** `CATALOG_FIELDS` lists 23 commercial fields only — `generate_full_catalog.py` L1379–L1386 — no `angle_id`, `motif_id`, `book_structure_id`.

4. **Pearl Prime catalog schema locks pipeline metadata but not variation knobs.** `COLUMNS` — `generate_pearl_prime_book_script_catalog.py` L78–102 — includes `section_plan_id`, `bestseller_overlay_ref`, but **no** motif/angle/journey fields.

5. **Runtime pipeline injects variation after format plan, keyed off seeds + optional wave index, not CSV.** `run_pipeline.py` L2055–2097 writes `motif_id` / `reframe_profile_id` into `format_plan_dict`.

6. **Motif bank is consumed in compiler when `motif_id` present.** `assembly_compiler.py` loads `recurring_motif_bank.yaml` at L354–372.

7. **Manga profile loader validates emotional/visual grammars** (`profile_loader.py` L77–L129) — richer per-row than book CSV for those axes — but **orthogonal** to Pearl Prime book CSV columns.

8. **`platform_knob_tuning` documents consumers** (`platform_knob_tuning.yaml` L4–6: variation_selector, format_selector, wave_optimizer) **but book catalog generators do not load it** (no import in `generate_full_catalog.py` / `generate_pearl_prime_book_script_catalog.py` per static review).

9. **Recommender configs appear disconnected from catalog scripts.** `scoring_weights.yaml` defines weights L1–L6; **no** matches for `recommender` under `scripts/catalog/*.py` in this audit’s `grep`.

10. **Projection planner uses format mix percentages only** — `projection_planner.py` L87–94 — no vocabulary from motif/angle/sensory layers.

11. **Missing script finding:** `build_high_confidence_catalog.py` referenced in operator brief — **absent** from `scripts/catalog/` (existence check returned absent).

12. **Path expectation drift:** `config/format_registry.yaml` missing; actual registry consumed from `config/format_selection/format_registry.yaml` (`format_selector.py` L61–L62; `generate_full_catalog.py` L85–L86).

**Phase 5 finding count:** **12**

**Dead-vocab snapshot (from findings above):** recommender YAMLs + much of `platform_knob_tuning` are **undeclared consumers** at the **catalog generator** layer (not necessarily dead globally — `knob_apply.py` / `variation_selector.py` use platform tuning in other paths).

**Inconsistent-consumption snapshot:** **Book runtime path** (`run_pipeline` + `variation_selector` + `assembly_compiler`) consumes **motif / journey / structure knobs**, while **Pearl/full CSV rows and CatalogPlanner defaults** do not carry or consult the same vocabulary — **asymmetric** across “CLI arc run” vs “CSV planning export”.

---

## Phase 6 — Recommended next steps (≤5; no cap entries authored here)

1. **Schema bridge: catalog row ↔ `BookSpec` / `variation_knobs` (P0; effort M; owner Pearl_Dev)**  
   - **Cap / workstream to open:** e.g. `CAP-CATALOG-VARIATION-SERIALIZATION-01` — extend Pearl/full CSV (or sidecar JSON) with `angle_id`, `motif_id`, `book_structure_id`, `journey_shape_id`, deterministic hash.  
   - **User-visible win:** Planned titles carry the same structural identity the assembler will execute.  
   - **Dependency:** freeze variation signature rules in `variation_selector.py` first so columns stay stable.

2. **Teach `CatalogPlanner` to consult `angle_registry` / series angles with registry validation (P0; effort M; owner Pearl_Dev)**  
   - **Workstream:** `ws_angle_registry_stage1_alignment_20260508`  
   - **User-visible win:** Fewer `{topic}_general` fallbacks (`catalog_planner.py` L495) and alignment with declared angle vocabulary.  
   - **Dependency:** operator policy on when explicit `--angle` overrides registry.

3. **Wire `platform_knob_tuning` into `generate_full_catalog.py` / Pearl Prime generator for market-aware rows (P1; effort S–M; joint Pearl_Research + Pearl_Dev)**  
   - **Workstream:** `ws_platform_tuning_catalog_join_20260508`  
   - **User-visible win:** Catalog exports reflect Audible vs Spotify structural preferences (file `platform_knob_tuning.yaml` L11–L41).  
   - **Dependency:** stable `market` → `platform_id` map.

4. **Connect or delete `config/recommender/*` at catalog boundaries (P1; effort S; owner Pearl_Dev)**  
   - **Workstream:** `ws_recommender_catalog_gate_20260508` — either import weights as soft filters or move files to `archive/` with docs.  
   - **User-visible win:** Removes false confidence that scoring YAML affects emitted rows.  
   - **Dependency:** product decision on gating vs telemetry-only.

5. **Docs + path alias for format registry (P2; effort S; owner Pearl_GitHub/docs)**  
   - **Workstream:** `ws_format_registry_path_alias_20260508` — symlink or lint guard rejecting bogus `config/format_registry.yaml` references.  
   - **User-visible win:** Fewer misconfigured scripts.  
   - **Dependency:** none.

**Phase 6 recommendation count:** **5**  
**Top 3 P0-class items (from Phase 6):** items **1**, **2**, and the **P0 row in Table 4 (angle / registry alignment)** — expressed in deployment terms as **(a)** serialize variation knobs on catalog artifacts, **(b)** align Stage 1 angle resolution with `angle_registry`, **(c)** eliminate silent `{topic}_general` angle fallback for Pearl-scale rows.

---

## CLOSEOUT_RECEIPT

| Field | Value |
|--------|--------|
| Artifact | `artifacts/qa/feature_knob_utilization_audit_2026-05-08.md` (this file) |
| Phase 1 Table 1 row count | **28** |
| Phase 5 bullet count | **12** |
| Phase 6 recommendations | **5** |
| Git / PR | **Shipped:** shallow clone `/Users/ahjan/phoenix_omega_feature_audit_wt` → branch `agent/feature-knob-utilization-audit-20260508` → commit `cd3ecb6a6` → PR **#960** — https://github.com/Ahjan108/phoenix_omega_v4.8/pull/960 |
| HANDOFF_TO | **Operator** — read Tables 2–4; authorize which P0/P1 cap entries from Phase 6 to schedule as Pearl_Dev workstreams. |

---

### Appendix — Commands / checks executed (audit hygiene)

- File existence & key counts via `python3` + `yaml.safe_load` on registries (motifs=6, angles=4, structural=15, runtime=20, platform_profiles=14, topics=57, personas=13).
- `grep` / targeted file reads as cited inline.
- `test -f scripts/catalog/build_high_confidence_catalog.py` → absent.

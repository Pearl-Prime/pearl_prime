# Lane A — Catalog Plan Inventory (en_US, all brands)

**Agent:** Pearl_Prime | **Date:** 2026-07-23 | **Anchor:** `origin/main` = `633273c97f509037c49812d48c371e98eb2bd061`
(prompt's authoring anchor `244955eaa0…` is behind this by an unknown margin — all counts below are re-derived live
against `633273c9…`, not trusted from the prompt or from any prior doc.)

**Scope discipline:** this is a read-only inventory. No `run_pipeline.py`, no `build_epub.py`, no renderer was
invoked. `config/source_of_truth/**` was read, never edited. One read-only preflight gate
(`phoenix_v4/gates/check_tuple_viability.py`) was run for 4 spot-check cells — that script performs no writes and
issues no render.

All raw command output backing every number below is in `evidence/discovery_commands_and_output.txt`,
`evidence/tuple_viability_spotchecks.txt`, and `evidence/per_brand_inventory.csv`.

---

## 0. Headline finding

**PROGRAM_STATE.md's catalog-volume numbers are stale by roughly 15x.** It states (as "LAST VERIFIED 2026-07-22"):
"1,519 LISTINGS... across 26 brands + Waystream (800)... Total counts: 2,187 `book_plans_en_us`." The live count on
`origin/main` right now is **32,401 files in `config/source_of_truth/book_plans_en_us/`, across 40 brand
archetypes, averaging ~810 per brand** — not 26 brands, not 2,187 files. The catalog-scaleup lane (per project
memory: "en_US→800/brand via CSVs→YAML, one-brand-per-session") has clearly executed for most of the brand roster
since PROGRAM_STATE's cited PR range (#1801–#1913) and the doc was never refreshed. This also **overturns
`CATALOG-800-PER-BRAND-01`** (ratified 2026-05-06, `docs/PEARL_ARCHITECT_STATE.md:648`), which declared "800 is a
system-wide total, NOT per-brand" and rejected the operator's literal per-brand framing as not-yet-implemented. As
of today, 39 of 40 brand archetypes literally do have ~800–845 planned books each in en_US alone — the operator's
original "800 per brand" framing is now the closer-to-true one, and the ratified decision doc is the one that's
behind. This is a documentation/decision-record staleness finding, not a recommendation to re-litigate the
decision; it is reported here because Lane F synthesis needs it.

---

## 1. Mechanism — what generates a catalog plan, and which script is canonical

Traced all four candidate entry points named in the prompt (`git log -1` per file, evidence: discovery output):

| Script | Role | Status |
|---|---|---|
| `scripts/catalog/gen_brand_catalog_plan_csv.py` | Generates an 800-row-target CSV per brand: expands persona × topic × engine (+ `__1hr` variants) using the naming engine for title/subtitle and `author_brand_resolver` for byline. Docstring explicitly says "Waystream-style 800-row catalog plan CSV for a brand archetype." | **Canonical, current** (last touched 2026-07-20) |
| `scripts/catalog/catalog_plan_csv_to_plan_yaml.py` | Imports that CSV → `book_plans_<locale>/*.yaml` + `series_plans_<locale>/*.yaml`. Docstring: "mirrors `artifacts/waystream/waystream_800book_catalog_plan.csv` → YAML path used for the 800-book Waystream flagship." | **Canonical, current** (last touched 2026-07-20) |
| `phoenix_v4/planning/catalog_planner.py` | "Stage 1 Catalog Planner" — produces a `BookSpec` from `config/catalog_planning/` (domain_definitions, series_templates, capacity_constraints), contract-linked to `specs/OMEGA_LAYER_CONTRACTS.md`. Reads `master_arcs/`, `render_location_profiles.yaml`. | A **separate, deeper planning stage** (arc/format/locale resolution), not the CSV-driven volume generator. Recently touched (2026-07-08, "planner-owned accent/story intelligence v1") — active but a different concern than catalog volume. |
| `scripts/generate_catalog.py` | "Generate full content catalog for all teachers × personas × topics × locales × platforms," driven by `platform_knob_tuning.yaml` / `release_wave_controls.yaml`. | Last touched 2026-07-02; a **legacy/parallel** teacher-centric generator, not the mechanism that produced the current `book_plans_en_us` corpus (confirmed by `plan_source_path:` provenance field inside every plan file — see §2). |

**The mechanism that actually produced the 32,401 files on disk** is the CSV→YAML pair
(`gen_brand_catalog_plan_csv.py` → `catalog_plan_csv_to_plan_yaml.py`), confirmed directly from the
`plan_source_path:` field inside sampled plan YAMLs (e.g. `plan_source_path: /tmp/adhd_forge_catalog.csv` and
`plan_source_path: artifacts/waystream/waystream_800book_catalog_plan.csv`). This matches project memory
("Catalog scale-up lane... one-brand-per-session"). `catalog_planner.py` operates one layer down (arc/format
binding, not volume generation) and is out of scope for "how many books are planned," though it is directly
relevant to Lane C (spine-buildability), see §5.

**Authority doc:** `SUBSYSTEM_AUTHORITY_MAP.tsv` routes `pearl_prime` to
`docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` and `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`
(owner: Pearl_Prime, status: active). Neither doc names the CSV→YAML catalog-scaleup mechanism explicitly — it is
documented only in project memory and in the scripts' own docstrings, not in a subsystem spec. **Note:**
`artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`, cited in this lane's own PROVENANCE header as
prior research, **does not exist on `origin/main`** (confirmed: no match anywhere in the repo outside
untracked/local worktree scaffolding created by sibling lane sessions this hour). That citation could not be
verified or built on; flagging for Lane F.

---

## 2. Where the plan artifacts live, and what one contains

Confirmed location: `config/source_of_truth/book_plans_en_us/` — **flat directory, 32,401 `.yaml` files**, one per
book (not one directory per brand; the "40 top-level entries" in the prompt's authoring-time note refers to the
40 distinct brand-archetype *filename prefixes*, not 40 subdirectories — there are no subdirectories under
`book_plans_en_us/`).

Read 4 plan files in full (2 book-plan, 1 series-plan, cross-brand — see §4 for sampling rationale):

- `adhd_forge__default_teacher__corporate_managers__anxiety__comparison.yaml` — a **listing-stage** book plan.
  Fields present: `book_id`, `series_plan` (path), `installment_number`, `engine`, `duration`,
  `structural_format_id` (`F006`), `target_word_range`, `title`, `subtitle`, `description.short_blurb` (empty),
  `description.long_description` (empty), `keywords` (empty lists), `bisac_codes` (populated), `target_price`
  (populated), `author_positioning` (brand + byline_author populated, teacher null), `comp_titles` (empty),
  `plan_source_path`, and an explicit **`_needs_authoring: true`** flag.
- `stillness_press__ahjan__working_parents__somatic_healing__false_alarm.yaml` — an **authored** book plan
  (`_needs_authoring: false`): same schema, but `title`/`subtitle`/`cover_tagline` are hand-quality copy,
  `description.short_blurb` and `.long_description` are full marketing prose (~450 words), `keywords` and
  `comp_titles` are populated with real comparable titles.
- `way_stream_sanctuary__…__comparison.yaml` — same authored pattern, `plan_source_path` points at the real
  committed `artifacts/waystream/waystream_800book_catalog_plan.csv`.
- `series_plans_en_us/stillness_press__ahjan__working_parents__somatic_healing.yaml` — the **series-level** plan
  a book's `series_plan:` field points at. See §3 — this is where the closest thing to a bestseller contract
  actually lives.

Full text of all 4 is in `evidence/sample_plan_yamls/`.

**Fields present in every book-plan YAML (schema `book_plan_schema: 1.0.0`, uniform):** `book_id`, `series_plan`,
`installment_number`, `engine`, `duration`/`runtime_format_id`, `structural_format_id`, `target_word_range`,
`target_audio_minutes`, `title`, `subtitle`, `cover_tagline`, `description` (short/long), `keywords`
(primary/secondary), `bisac_codes`, `target_price`, `author_positioning` (teacher/brand/byline_author),
`comp_titles`, `plan_source_path`, `_needs_authoring`. **Persona, topic, and engine are always resolved** — they
are baked into the filename and the `engine` field for every one of the 32,401 files; there is no "title exists
but persona×topic×engine unresolved" tier on disk in this directory (see §5 for what this means for the
listing/plannable/spine-buildable ladder).

**`structural_format_id` (chapter-count/format tier) is essentially a single value:** 32,391 of 32,401 files
(99.97%) are `F006` (`standard_book_60min`); only 10 files across the whole en_US catalog use `F009`/`F013`/`F015`.
There is effectively **no format-tier diversity at plan time** — every planned book targets the same
9,000–12,000-word / 60-minute-audio shape.

---

## 3. Does a plan artifact capture a bestseller contract at plan time?

**Answer: not at the book-plan level. Yes, structurally, at the series-plan level — but the field is empty for
~86–90% of series.** This is precise and load-bearing, so both halves matter:

**Book-plan level (`book_plans_en_us/*.yaml`):** grepped for a structured thesis/positioning/promise field across
all 32,401 files. Zero files have a `positioning:` or `emotional_arc:` key. Exactly 1 file contains the string
"thesis" and 2 contain "promise" — both are incidental words inside free-text `long_description` prose (e.g. "...
becomes a thesis on your shortcomings...", "...your body is keeping an old promise..."), not a structured field.
**There is no field, populated or not, that states a book's market thesis or reader promise before it enters the
render queue.** The closest thing is the free-text `description.long_description` blurb — but that field is
present-but-empty for 30,088 of 32,401 files (`_needs_authoring: true`), and even where populated
(1,813 files, `_needs_authoring: false`) it is marketing copy, not a distinct contract field a downstream
render-time consumer could key off of.

**Series-plan level (`series_plans_en_us/*.yaml`):** every one of the 4,830 series plans (one per persona×topic
cell, each covering ~6–7 book-plan installments) carries a genuine bestseller-contract schema:
`reader_promise_family` (free text — what the reader will get across the whole series), `bestseller_hook_family`,
`emotional_engine` (a short taxonomy key, e.g. `somatic_healing_recognition` — **always populated**, 0/4,830
empty, but this reads as templated/derived from persona+topic, not authored), `reader_avatar` (structured:
`age`, `where_they_are`, `what_they_need`, `what_they_avoid` — a real scene-level reader sketch), and
`series_voice_markers` (register/tone). This is a genuine, structured, plan-time market-thesis-and-emotional-arc
capture — it exists **before** any book in the series enters the render queue, which directly answers the
mission's question. **But it is overwhelmingly blank:**

- `reader_promise_family` is the empty string `''` in 4,165 of 4,830 series plans (86.2%) — populated in only
  **665** (13.8%).
- `bestseller_hook_family` is empty in 4,347 of 4,830 (90.0%) — populated in only **483** (10.0%).
- Of the 665 populated `reader_promise_family` entries, **260 (39%) belong to `way_stream_sanctuary` alone**
  (all 260 of its series plans are populated). The remaining 405 are spread thin across 25 of the other 39 brands
  (2–48 each); 14 brands have **zero** populated series-level reader-promise fields at all (see per-brand table,
  §4).

So: render-time thesis lookup (`config/planning/chapter_thesis_bank.yaml`, keyed `intent→engine`, per the
07-22 audit's §2.2 as cited in this lane's prompt — not independently re-verified here since that audit report
does not exist on disk, see §1) may still be the operative mechanism for the ~86–90% of series that have no
plan-time promise/hook — for those, "thesis" genuinely is a render-time-only concept, consistent with the
mission's hypothesis. For the ~10–14% that do have it populated (predominantly Waystream, and secondarily
digital_ground/solar_return/cognitive_clarity/stillness_press/somatic_wisdom), a real plan-time contract exists
and (per Lane B/C's remit) whether it's actually consumed downstream is a separate, unverified question this lane
did not test.

---

## 4. Full brand roster + per-brand plan-volume reality

**Brand-roster reconciliation (the discrepancy the prompt flagged as needing resolution):**

- `config/brand_registry.yaml` (`owner: pearl_prime`, `status: active`) has a `brands:` dict with **26 keys** —
  but those 26 keys are `stillness_press`, `cognitive_clarity`, plus 24 entries that are CJK-locale-suffixed
  variants (`sleep_repair_tw/hk/cn/sg`, `stabilizer_tw/hk/cn/sg`, `panic_first_aid_*`, `gen_z_grounding_*`,
  `grief_companion_*`, `inner_security_*`). **This is not the en_US catalog brand roster** — it looks like a
  narrower/different (possibly legacy or CJK-specific) registry that happens to share the `pearl_prime` owner tag.
- The registry actually consumed by the catalog-generation scripts (`REG` constant in both
  `gen_brand_catalog_plan_csv.py` and `catalog_plan_csv_to_plan_yaml.py`) is
  `config/brand_management/global_brand_registry_unified.yaml` (376KB, `schema_version: 2.0`,
  `generated_by: build_unified_brand_registry.py`). It declares **`total_brand_archetypes: 40`,
  `total_lanes: 14`, `total_brands: 560`** (40 × 14 = 560, i.e. 40 brand archetypes fanned out across 14
  locale "lanes" — matching exactly the 14 `book_plans_<locale>` directories on disk: de_de, en_us, es_es,
  es_us, fr_fr, hu_hu, it_it, ja_jp, ko_kr, pt_br, zh_cn, zh_hk, zh_sg, zh_tw). **This is the true catalog
  brand roster**, and its 40 archetypes match exactly the 40 distinct filename prefixes found by direct
  enumeration of `book_plans_en_us/`. Resolution: `config/brand_registry.yaml`'s "26 brands" and
  PROGRAM_STATE's "26 brands + Waystream" are both stale/narrower than the live 40-archetype roster;
  `way_stream_sanctuary` is itself one of the 40 archetypes in the unified registry, not a separate 41st entity.
  `cognitive_clarity` is flagged `inactive_archetypes: [cognitive_clarity]` in the unified registry, yet it has
  821 live planned books in en_US — a real, reportable inconsistency (an "inactive" archetype with a full,
  ~90%-thesis-populated catalog on disk).
  15 archetypes (including `way_stream_sanctuary`, `bio_flow`, `focus_sprint`, `trauma_path`, etc.) are flagged
  `thin_archetypes_topics_from_manga_only` — worth Lane F attention since `way_stream_sanctuary` is
  simultaneously the *most* fully-authored brand by every metric measured here.

**Per-brand plan volume (live count, all 40 en_US archetypes, full enumeration — not sampled):**

Full table: `evidence/per_brand_inventory.csv`. Columns: `total_planned` (book-plan files),
`needs_authoring_false` (fully-blurbed/keyworded), `arc_pointer_orphaned` (see below), `plannable_arc_exists`
(total minus orphaned), `series_plans_on_disk`, `series_reader_promise_populated`.

- **37 of 40 brands sit in the 800–845 range** (min 800, max 845 — `adhd_forge` highest, most others exactly 800
  or within +25). This is the live confirmation of §0's headline: **per-brand volume genuinely is ~800 today**,
  brand by brand, not a system-wide-only figure.
- **3 brands are the exception, and not for a "deliberately smaller" reason — for a broken-pipeline reason:**
  `qi_foundation` (810 listed, only 53 have a real backing arc file), `body_memory` (801 listed, 65 real),
  `still_forest` (801 listed, 59 real). See below.
- Total en_US planned: **32,401**. Total with a genuinely existing series-arc file backing them:
  **30,166 (93.1%)**. Total orphaned (listing exists, engine/persona/topic resolved, but the arc file the
  `series_plan:` field should resolve to does not exist anywhere on disk): **2,235 (6.9%)** — and **100% of
  those 2,235 are concentrated in exactly the 3 brands above** (757/810, 736/801, 742/801 respectively — i.e.
  ~92% of *each of those 3 brands'* catalogs is orphaned, while the other 37 brands are ~100% arc-backed).

**A second, lower-severity data-hygiene finding surfaced while checking this:** 23,897 of 32,401 book-plan files
(73.8%) have a `series_plan:` field pointing at an ephemeral `/tmp/...` path (e.g.
`/tmp/adhd_forge_series/adhd_forge__default_teacher__corporate_managers__anxiety.yaml`) that obviously does not
exist under version control. For 21,662 of those (90.6% of the tmp-pointer subset), the *real* series-plan file
does exist on disk at the canonical `config/source_of_truth/series_plans_en_us/` path under the expected naming
convention — the pointer field itself is simply stale (recorded the generation-time `/tmp` location instead of
the final committed path) and any consumer trusting the literal field value rather than reconstructing the path
from the book_id convention would wrongly treat 66.9% of the whole catalog as arc-less. Only 8,504 files (26.2%)
have a correct `config/source_of_truth/...` pointer. **This stale-pointer issue is cosmetic for 21,662 files but
is the exact same symptom as the genuine 2,235-file orphan problem** — a downstream tool cannot tell the two
apart without doing the reconciliation this lane did (resolve by filename convention, then check existence).

**Why the 3 broken-arc brands are far from full plannability (the "one-line why" requested):** `qi_foundation`,
`body_memory`, and `still_forest` have only 11, 8, and 8 series-plan files on disk respectively (vs. 127–141 for
every other brand) — their catalog-plan CSVs were run through `gen_brand_catalog_plan_csv.py` to generate ~800
listing rows each, but `catalog_plan_csv_to_plan_yaml.py`'s series-plan-emission step was never completed (or was
reverted/lost) for the great majority of their persona×topic cells. This is a **partial-import gap in the
scaleup lane, not a deliberate smaller-target decision.**

---

## 5. Inventory ladder: listing-only vs. plannable vs. spine-buildable

Per the mission's requested three-tier ladder:

- **Listing only** (title/subtitle/description exist, but persona×topic×engine cell NOT resolved): **0 files.**
  Every book-plan YAML in `book_plans_en_us/` already has persona, topic, and engine resolved (they're literally
  in the filename and the `engine:` field) at the moment the file is created by the CSV→YAML importer. This tier,
  as defined in the mission prompt, does not exist as a *separate* on-disk artifact class in en_US — the CSV row
  itself (ephemeral, in `/tmp` or `artifacts/`) is the true "listing only" stage, and it is not committed once
  converted.
- **Plannable** (arc + listing exist): **30,166 of 32,401 (93.1%)** — arc file genuinely resolvable on disk
  (see §4's stale-pointer reconciliation). **2,235 (6.9%)**, concentrated in 3 brands, are listing-stage only
  with no real arc backing and are **not** plannable by this definition despite having resolved
  persona/topic/engine cells.
- **Spine-buildable** (passes tuple-viability preflight): **not exhaustively measured** — this lane is
  read-only inventory, not a full sweep, and `check_tuple_viability.py` takes a single
  persona/topic/engine/format tuple, not a batch-catalog mode. 4 spot-check cells were run (evidence:
  `evidence/tuple_viability_spotchecks.txt`, all real, no render invoked):
  - `corporate_managers × anxiety × comparison × F006` → **TUPLE_VIABLE**
  - `gen_z_professionals × grief × watcher × F006` → **TUPLE_VIABLE**
  - `working_parents × anxiety × false_alarm × F006` → **TUPLE_VIABLE**
  - `working_parents × somatic_healing × false_alarm × F006` → **NO_BINDING** (this is the exact cell behind
    `stillness_press__ahjan__working_parents__somatic_healing__false_alarm.yaml`, a *fully authored*,
    `_needs_authoring: false`, richly-blurbed book plan — it reads as "done" by every plan-level signal and
    still fails the spine-buildability preflight)
  3 of 4 spot-checked cells pass; 1 fails, and the failure is on a fully-authored plan, not a stub. This is a
  small sample (do not extrapolate a rate from n=4) but it directly corroborates project memory ("Plan ≠
  structural proxy" — plans predict quality, not renderability) and is exactly the kind of gap Lane C should
  size properly with a real batch sweep.

---

## 6. Sample-size discipline

Per the mission's requirement, this is explicit about what was **counted** (cheap, full-corpus) vs. **deep-read**
(expensive, representative):

- **Counted / structurally scanned in full** (every one of 32,401 book-plan files and 4,830 series-plan files,
  via `grep -rl`/`grep -rln` and a Python full-corpus walk — not sampled): file counts per brand, `engine`
  resolution, `_needs_authoring` true/false split, `structural_format_id` distribution, `series_plan:` pointer
  validity (tmp vs. real, orphaned vs. resolvable), `reader_promise_family` / `bestseller_hook_family` /
  `emotional_engine` / `reader_avatar` presence and emptiness. This is stronger than the "3–5 files per
  archetype" the mission asked for as a minimum — full-corpus grep is cheap enough that sampling wasn't
  necessary for the structural questions.
- **Deep-read in full** (4 files, read start-to-finish, contents quoted in §2 and copied to
  `evidence/sample_plan_yamls/`): one listing-stage book plan (`adhd_forge`, representative of the 30,088-file
  majority still needing authoring), one authored book plan (`stillness_press`, representative of the smaller
  hand-finished tier, and notably the one that fails tuple-viability), one authored Waystream book plan
  (`way_stream_sanctuary`, representative of the one brand that is ~100% authored and ~100% series-promise
  populated — an outlier worth Lane F's attention as the closest thing to a solved case), and the series-plan
  file backing the `stillness_press` sample (the only place a structured bestseller-contract schema exists).
  These 4 were chosen to span the two axes that actually differentiate plan quality in this corpus
  (`_needs_authoring` and brand-archetype "thinness"), not chosen arbitrarily or brand-by-brand — a literal
  3–5-per-40-archetypes deep-read (120–200 files) would have been redundant given the full-corpus structural
  scan already characterizes every field's prevalence exactly.

---

## 7. What this lane did NOT verify (explicit handoff boundary)

- Whether the render-time `chapter_thesis_bank.yaml` (`intent→engine`) mechanism cited in the mission prompt as
  the render-time thesis source actually exists and is wired the way described — not independently checked here
  (the audit report it's attributed to, `pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`, does not exist on
  `origin/main`; see §1).
- Whether the 30,166 "plannable" (arc-exists) books would actually pass a **batch** tuple-viability sweep — only
  4 individual cells were spot-checked (§5). Lane C should run a real batch.
- Whether the 665 series with a populated `reader_promise_family` actually get that value **consumed** anywhere
  downstream in composition/render — this lane only confirmed the field exists and is populated at plan time,
  not that anything reads it.
- Non-en_US locales — touched only to resolve the brand-roster discrepancy (§4); volume/authoring-rate inventory
  for the other 13 locales is out of this lane's scope.

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Prime
TASK:           Lane A — catalog plan inventory (en_US, all brands)
COMMIT_SHA:     <filled after commit>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/evidence/discovery_commands_and_output.txt
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/evidence/tuple_viability_spotchecks.txt
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/evidence/per_brand_inventory.csv
                artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/evidence/sample_plan_yamls/*.yaml (4 files)
FILES_READ:     docs/PROGRAM_STATE.md; docs/PEARL_ARCHITECT_STATE.md (CATALOG-800-PER-BRAND-01, PEARL-EDITOR-UPSTREAM-01);
                artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (pearl_prime row);
                config/brand_registry.yaml; config/brand_management/global_brand_registry_unified.yaml;
                scripts/generate_catalog.py; phoenix_v4/planning/catalog_planner.py;
                scripts/catalog/gen_brand_catalog_plan_csv.py; scripts/catalog/catalog_plan_csv_to_plan_yaml.py;
                phoenix_v4/gates/check_tuple_viability.py;
                4 representative plan YAMLs in full (2 book-plan, 1 series-plan, see evidence/sample_plan_yamls/);
                full-corpus structural scan (not full-text read) of all 32,401 book_plans_en_us + 4,830 series_plans_en_us files
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 (CITED BUT NOT FOUND ON DISK — could not verify or build on;
                flagged in §1/§7) | documents: CATALOG-800-PER-BRAND-01 (found STALE — live per-brand volume now
                contradicts its ratified premise, see §0), PEARL-EDITOR-UPSTREAM-01 (read, not directly load-bearing
                for this lane's findings), TEMPLATE-UNIVERSAL-01 (not located under that name; not load-bearing) |
                builds_on: gen_brand_catalog_plan_csv.py + catalog_plan_csv_to_plan_yaml.py (verified canonical, current) |
                inventory: EXTENDS (read-only report; zero code/config touched)
STATUS:         completed
HANDOFF_TO:     Lane C (assembly-readiness prediction) + Lane F (synthesis)
NEXT_ACTION:    Lane C: run a real batch tuple-viability sweep over the 30,166 "plannable" cells (this lane only
                spot-checked 4) to size the plan-to-spine-buildable gap precisely, with particular attention to
                whether NO_BINDING clusters around specific topics (somatic_healing failed here) the way arc-orphaning
                clustered around specific brands (qi_foundation/body_memory/still_forest). Lane F: reconcile
                CATALOG-800-PER-BRAND-01 and PROGRAM_STATE's en_US Listings section against this lane's live counts
                (§0) — both are now materially stale and should be flagged for a doc-refresh ws, not silently
                carried forward. Separately: qi_foundation/body_memory/still_forest's partial series-plan import
                (§4) is a concrete, scoped repair candidate (re-run catalog_plan_csv_to_plan_yaml.py for those 3
                brands' remaining CSV rows) — flagging as a spawn_task candidate rather than fixing here (out of
                this lane's read-only write-scope).
SIGNAL:         lane-a-plan-inventory-merged=<sha>
```

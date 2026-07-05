# Naming + Cover System — 37×14 Verification Audit

**Date:** 2026-07-05 · **Branch:** `agent/naming-cover-37x14-audit-20260705` · **Mode:** read-only verification  
**Sample artifact:** `artifacts/qa/naming_cover_37x14_matrix.json` (machine-readable matrix)

---

## Executive summary (scope grounding)

| Layer | Brand-general? | Applied where today? |
|-------|----------------|----------------------|
| **Title/subtitle engine** | Yes — per-brand weights in `subtitle_patterns.yaml`, seeded by `brand_id` | All skeleton plans via `gen_plan_skeletons.py` → `naming.cli.run()` |
| **Formula-4 validator + regen** | Validator is brand-agnostic code | **Enforced only** in `waystream_subtitle_regen.py` (Waystream / `book_plans_en_us`) |
| **Persona-in-subtitle** | Template pools + `content_mix` weights are brand-specific | Waystream regen + some authored cells; most brands still emit `"A guide for {Persona}"` stubs |
| **Series names (store-facing)** | Partial — `series_templates.yaml` has hook titles; no unified store_series engine | **Waystream only** has `store_series.name` on plans; others use topic slug or empty |
| **Cover collision solver** | Shared renderer (`waystream_covers` → `brand_covers`) | **Proven on Waystream**; other brands wired but not batch-rendered at scale |
| **Cover fingerprint** | `brand_covers/assignment.py` hashes `(brand_id, author_id)` for all brands | Waystream also has hand-authored cards in `waystream_cover_system.yaml` |

**Bottom line:** The *architecture* scales across 37 brands × 14 locales. The *good version* (Formula-4 titles, persona subtitles, collision-safe covers, localized text) has been **run and byte-verified for Waystream `en_US` only** (~753/800 authored plans pass Formula-4). The other **517 brand-locale cells** (37×14 minus Waystream en_US, treating Waystream as a separate imprint outside the canonical-37) remain on skeleton or English-stub patterns until propagated.

---

## Canonical grid definition

### 37 brands

Authoritative list: `specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md` §3 (lines 44–50) — 13 teacher + 24 standard archetypes.

Registry mirrors: `config/manga/canonical_brand_list.yaml` (`total_brands: 37`, lines 50–327), `config/brand_management/global_brand_registry_unified.yaml` (560 rows = 37×14).

**Not in canonical-37:** `way_stream_sanctuary` — composite imprint used for the 800-book English catalog and cover pilot (`scripts/catalog/waystream_subtitle_regen.py:25`, `config/publishing/waystream_cover_system.yaml:21–24`).

### 14 locales

`config/catalog/catalog_generation_config.yaml` lines 7–22 and `config/brand_management/global_brand_registry_unified.yaml` lines 25–39:

`en_US`, `ja_JP`, `ko_KR`, `de_DE`, `fr_FR`, `zh_TW`, `zh_CN`, `zh_HK`, `es_US`, `es_ES`, `it_IT`, `zh_SG`, `hu_HU`, `pt_BR`

**Matrix size:** 37 × 14 = **518 cells**. On-disk `book_plans_*` directories exist for **7 locales only** (207 cells with any plan files): `en_us`, `de_de`, `es_es`, `es_us`, `fr_fr`, `it_it`, `pt_br`. No `book_plans_*` tree for `ja_JP`, `ko_KR`, `zh_*`, `hu_HU`.

---

## AXIS 1 — Titles (Formula 4)

### How it scales (system description)

1. **Generation** — `phoenix_v4/naming/generator.py` builds 12 seeded candidates per book using brand-specific `title` template preferences and `content_mix` weights from `omega/title_entropy/subtitle_patterns.yaml` (loaded via `_config.load_subtitle_patterns()`, generator lines 223–233). Formula-4 template IDs exist globally:

   ```28:31:omega/title_entropy/subtitle_patterns.yaml
   formula4_hook: "{EngineAngle}: {PrimaryKeyword}"
   formula4_series: "{SeriesTitle}: {PrimaryKeyword}"
   formula4_guide: "{EngineAngle}: A Guide to {PrimaryKeyword}"
   ```

   Only **`way_stream_sanctuary`** lists these in its brand prefs (lines 301–305). Other brands prefer `scenario_direct`, `metaphor_title`, `persona_targeted`, etc.

2. **Scoring bias** — `phoenix_v4/policy/naming_scoring.yaml` lines 14–16 penalizes keyword-in-pre-colon (`keyword_in_pre_colon_penalty: 0.50`) but does **not** hard-reject it.

3. **Hard validation** — `phoenix_v4/naming/validator.py` defines `validate_formula4()` (lines 77–133) and lists Formula-4 reasons in `HARD_VALIDATORS` (lines 20–27). **`validate()` only invokes it when `formula4=True`** (lines 179–184).

4. **Production CLI** — `phoenix_v4/naming/cli.py` calls `validator.validate(...)` **without** `formula4=True` (lines 68–74). Skeleton emission uses this path:

   ```104:105:scripts/catalog/gen_plan_skeletons.py
   nm = naming.run(topic, persona, series_id, intent, args.brand, "", str(_h(book_id)), i)
   title, subtitle = (nm.get("title") or "").strip(), (nm.get("subtitle") or "").strip()
   ```

5. **Waystream regen (only enforced batch)** — `scripts/catalog/waystream_subtitle_regen.py`:
   - `PLANS = .../book_plans_en_us` (line 24), `BRAND = "way_stream_sanctuary"` (line 25)
   - Calls `validate_formula4` in `_validate_pair` (lines 149–154) and requires 800/800 pass before `--apply` (lines 546–549)

### Sampled compliance (authored plans, `validate_formula4`)

| Scope | Sample | Formula-4 pass | Hook-first (kw not in pre-colon) | Evidence |
|-------|--------|----------------|----------------------------------|----------|
| **Waystream `en_US` authored** | 800/800 plans `_needs_authoring: false` | **753/800 (94.1%)** | **800/800 (100%)** | Audit script on `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml`; sample plan `way_stream_sanctuary__...__false_alarm.yaml:14–15` passes validator |
| **Waystream non-`en_US`** | 10 plans each `de_de`, `fr_fr` | **0%** | N/A (old `{Topic}: {Engine}` pattern) | e.g. `book_plans_de_de/...`: title `'Compassion Fatigue: Shame'`, subtitle `A guide for Millennial Women Professionals` |
| **Canonical-37 `en_US` (non-Waystream)** | 50 authored `adhd_forge` plans | **0/50 (0%)** | Inverted pattern dominant in skeletons | e.g. `stabilizer__...__overwhelm.yaml:14` → `'Overthinking: Overwhelm'` fails `formula4_keyword_in_pre_colon` |
| **All brands all locales (mixed skeleton+authored sample)** | 1,792 plan samples | **0%** aggregate | 0% inverted in sample (most lack colon entirely) | `artifacts/qa/naming_cover_37x14_matrix.json` |

**Top Waystream fail reasons (47 plans):** `formula4_keyword_absent_post_colon` (40), `formula4_persona_absent_from_subtitle` (4), `formula4_combined_length_exceeded` (3).

**Verdict:** Formula-4 is **defined and brand-general** but **not enforced at generation**. It is **batch-enforced only when `waystream_subtitle_regen.py --apply` runs** on Waystream `en_US`.

---

## AXIS 2 — Subtitles (persona-in-subtitle)

### How it scales

- Subtitle templates tagged `content: persona_direct` in `subtitle_patterns.yaml` (lines 42–44, 46+).
- Per-brand `content_mix.persona_direct` weight controls persona-bearing subtitle frequency (generator lines 233, 388–393).
- Formula-4 adds a **hard** persona token check in subtitle (`validator.py` lines 121–125).
- Waystream regen uses persona-heavy subtitle template IDs (`waystream_subtitle_regen.py` lines 32–42, `subtitle_patterns.yaml` lines 301–305).

### Sampled compliance

| Scope | Persona token in subtitle | English stub `"A guide for …"` | Localized (non-English text) |
|-------|---------------------------|--------------------------------|------------------------------|
| Waystream `en_US` authored (800) | **795/800 (99.4%)** | **0%** (regen removed stubs) | N/A |
| Waystream `de_de` / `fr_fr` (10 each) | ~100% token match on stub text | **100%** | **0%** — English stubs in DE/FR dirs |
| Canonical-37 `de_de`/`fr_fr`/`es_es` (20-plan sample per brand) | ~74–79% (persona word appears in stub) | **~100%** | **0%** — titles 20/20 ASCII English in `stabilizer` DE/FR/ES samples |
| `en_US` non-Waystream (mixed) | ~84% avg (stub contains persona label) | **~99%** | N/A |

**Verdict:** Persona-in-subtitle is **engine-capable** and **Waystream-enforced**. Other locales carry **English skeleton subtitles** with no translation layer wired.

---

## AXIS 3 — Series names

### How it scales

Three parallel naming layers:

| Layer | Source | Naming style | Localization |
|-------|--------|--------------|--------------|
| **Catalog / naming engine** | `config/catalog_planning/series_templates.yaml` — `series_title` per arc (e.g. line 175: `"The Alarm Is Lying"`) | Hook-worthy, Formula-4-quality phrases | English only in config |
| **Manga lane plans** | `config/catalog_planning/brand_series_plans.yaml` — per-brand `series_a.title` etc. (e.g. stillness_press line 36: `"The Alarm Within"`) | Hand-authored per brand × lane tier | English titles; lane buckets not locale IDs |
| **Store / KDP series** | `store_series:` block on **Waystream book plans only** | Human names e.g. `Through the Low Places — for Working Parents` (`book_plans_en_us/way_stream_sanctuary__...__watcher.yaml:5–7`) | English |
| **Cover render adapter** | `scripts/publish/brand_covers/adapter.py:50` | **`topic.replace("_", " ").upper()`** — not a series engine | N/A |

**Series plan files** (`config/source_of_truth/series_plans_en_us/`, 4,830 files) encode arc structure and `comp_series` comps (e.g. `way_stream_sanctuary__...__anxiety.yaml:52–55`) but **no reader-facing `series_title` field** on standard skeleton series plans emitted by `gen_plan_skeletons.py` (lines 111–125 — empty `reader_promise_family`, no `store_series`).

**`brand_series_plans.yaml`:** 36 brands with manga series definitions; separate from bestseller book `store_series`.

**Verdict:** Hook-quality series titles exist in **`series_templates.yaml` (naming input)** and **`brand_series_plans.yaml` (manga)**. There is **no systematic store_series naming engine** for the canonical-37 book catalog — only Waystream hand/regen population.

---

## AXIS 4 — Bestseller cover templates (37×14 scaling model)

### Confirmed model (shared library × per-brand layers)

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1 — Template library (8+ families, placement variants)   │
│   waystream_covers/templates.py + layout_solver.py               │
│   Families: assignment.py:21-22 (8) + type_dominant in YAML:37-38│
├─────────────────────────────────────────────────────────────────┤
│ LAYER 2 — Collision solver + verbatim plan text                  │
│   layout_solver.py:1-6, templates.py:1-8,3-4                    │
│   Raises CoverLayoutCollisionError on overlap (lines 24-31)      │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 3 — Per-brand palette / symbol fingerprint                 │
│   brand_covers/assignment.py:26-77 (16 palette bank, hash assign)│
│   waystream_cover_system.yaml:46-68 (hand-authored author cards) │
│   Topic motif: assignment.py:40-49 → symbols.py primitives     │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 4 — Per-author variation (family × serif × sans × case)    │
│   assignment.assign_author() lines 65-77                         │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 5 — Per-book topic symbol + installment count              │
│   templates.Spec topic/motif/book_num (templates.py:38-59)       │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 6 — Per-locale text (composited onto shared FLUX pool)     │
│   brand_covers/pools.py:3-4 — pool once per (brand, author)      │
│   render_brand.py:18-20 imports shared engine                    │
└─────────────────────────────────────────────────────────────────┘
```

### Shared vs Waystream-only

| Capability | Shared (`brand_covers` reuses `waystream_covers`) | Waystream-only |
|------------|---------------------------------------------------|----------------|
| Collision solver | **Yes** — `render_brand.py:18-20` imports `templates`, which calls `layout_solver` | Origin implementation |
| Verbatim plan title/subtitle | **Yes** — `templates.py:62-67` | Same code path |
| Author-zone layout | **Yes** — `layout_zones.py` (imported by solver) | — |
| Hand-tuned author cards | — | **`waystream_cover_system.yaml:46+`** (20 authors) |
| FLUX image pools | Generic `artifacts/covers/<brand>/author_pools/` | Waystream catalog CSV-driven |
| Alternate KDP path | `render_kdp_cover.py` — gradient fingerprint, **no collision solver** | — |

### Fingerprint coverage

- **All canonical brands:** `assign_author(brand_id, author_id)` works for any brand string (`assignment.py:65-77`).
- **Hand fingerprint:** Only Waystream has curated per-author palette/family in YAML.
- **CJK / non-Latin fonts:** `waystream_covers/fonts.py` — macOS Latin serifs/sans only (lines 17–37). `render_kdp_cover.py:336-370` explicitly skips orphan logic for non-ASCII; **no CJK font registry** in the shared cover stack.

**Verdict:** Collision solver + verbatim-text fixes live in the **shared renderer** and apply to any brand invoked via `brand_covers.render_brand`. **Batch proof exists for Waystream**; other brands are arch-ready but not cover-rendered at catalog scale. **Per-locale typography for CJK is a build gap.**

---

## Coverage matrix

Legend: **F4** = Formula-4 pass rate on sampled authored plans · **Psub** = persona-in-subtitle · **Loc** = non-English localized title+subtitle · **Series** = human `store_series.name` or `series_templates` hook · **CovFP** = cover fingerprint assignable · **Plans** = plan directory exists

### Locale summary (canonical 37 brands)

| Locale | Plans dir | Brands w/ plans | F4 (avg sample) | Psub | Loc | Series named | CovFP |
|--------|-----------|-----------------|-----------------|------|-----|--------------|-------|
| en_US | `book_plans_en_us` | 37/37 | **0%**† | ~84% | EN | 0%‡ | YES |
| de_DE | `book_plans_de_de` | 37/37 | 0% | ~74% | **0%** | 0% | YES |
| fr_FR | `book_plans_fr_fr` | 37/37 | 0% | ~79% | **0%** | 0% | YES |
| es_ES | `book_plans_es_es` | 37/37 | 0% | ~79% | **0%** | 0% | YES |
| es_US | `book_plans_es_us` | 6/37 | 0% | ~77% | **0%** | 0% | YES |
| it_IT | `book_plans_it_it` | 16/37 | 0% | ~76% | **0%** | 0% | YES |
| pt_BR | `book_plans_pt_br` | 37/37 | 0% | ~79% | **0%** | 0% | YES |
| ja_JP | — | 0/37 | — | — | — | — | YES§ |
| ko_KR | — | 0/37 | — | — | — | — | YES§ |
| zh_TW/CN/HK/SG | — | 0/37 | — | — | — | — | YES§ |
| hu_HU | — | 0/37 | — | — | — | — | YES§ |

† **Waystream imprint (outside canonical-37):** `en_US` authored **753/800 F4 pass (94.1%)** — the only locale with regen applied.  
‡ **`store_series.name` populated on Waystream plans only**; canonical-37 use topic slug at cover adapter.  
§ **Fingerprint assignable in code**; no localized font stack for these locales.

### Waystream imprint row (separate from canonical-37)

| Locale | Authored plans | F4 | Psub | Loc | store_series | Collision solver |
|--------|----------------|-----|------|-----|--------------|------------------|
| en_US | 800/800 | **94.1%** | **99.4%** | EN | **Yes** (sample: lines 5–7 watcher plan) | **Proven** |
| de_DE | 0/720 | 0% | stub | **EN stub** | No | Engine shared, plans not regen'd |
| fr_FR | 0/800 | 0% | stub | **EN stub** | No | Same |

### Per-brand notes (`en_US`, canonical-37 sample)

| Brand | subtitle_prefs | Sample title pattern | F4 | Authoring state |
|-------|----------------|----------------------|-----|-----------------|
| `way_stream_sanctuary`† | Formula-4 templates (patterns:301-305) | Hook: `'When Your Mind Screams Danger: A Guide to Anxiety'` | **94%** | 800 authored |
| `stillness_press` | Custom (patterns:106+) | Mixed; some prose titles when authored | 0% | Mostly `_needs_authoring: true` skeletons |
| `stabilizer` | Custom | `'Overthinking: Overwhelm'` + stub sub | 0% | Skeleton |
| `adhd_forge` | Custom | `'False Alarm'` (no colon) + long prose sub | 0% | 45 partial authored |
| `cognitive_clarity` | Custom | `'Anxiety: False Alarm'` inverted | 0% | Skeleton |
| `qi_foundation`, `relational_calm`, `warrior_calm`, `body_memory`, `heart_transmission` | **default** fallback (patterns:353-357) | Same skeleton family | 0% | Skeleton |

Full per-brand × locale sample grid: `artifacts/qa/naming_cover_37x14_matrix.json`.

---

## AXIS 5 — Propagation gap + scale plan

### What Waystream `en_US` has that the other 517+ cells lack

| Gap | Waystream en_US | Everywhere else | Fix type |
|-----|---------------|-----------------|----------|
| Formula-4 titles | Regen applied | Skeleton / inverted `{Topic}: {Engine}` | **Re-run** — generalize `waystream_subtitle_regen.py` or add `formula4=True` to `cli.py` + batch regen per brand |
| Persona subtitles | Regen + long templates | `"A guide for {Persona}"` (~99% stub rate) | **Re-run** (same script pattern) |
| Localized title/subtitle | English (target locale) | Non-en dirs = English copy | **Build** — translation/localization pipeline per locale |
| `store_series.name` | Populated on plans | Absent; cover uses topic uppercase | **Build** — series naming engine from `series_templates.yaml` + persona |
| Collision-safe covers | Rendered + solver tested | Code wired, not batch-proven | **Re-run** — `brand_covers.render_brand --brand X` per brand |
| CJK fonts on cover | N/A (English catalog) | No font registry | **Build** — extend `fonts.py` / locale-aware `get_font` |
| Plan files | 800 authored | 7/14 locales have dirs; CJK/HU missing entirely | **Build** — locale plan generation + translation |

### Re-run vs build

| Capability | Re-run existing engine | Needs new build |
|------------|------------------------|-----------------|
| Formula-4 titles + persona subtitles | ✅ Enable validator in `cli.py`; clone regen script per brand/locale | — |
| Brand template prefs (Formula-4 templates) | ✅ Add `formula4_*` to each brand block in `subtitle_patterns.yaml` | — |
| Cover render at scale | ✅ `brand_covers` + shared solver | FLUX pools per author (GPU batch) |
| Non-English plan text | — | ✅ Translation QA + locale-aware naming |
| Store series names on all plans | — | ✅ Writer/regen from `series_templates.yaml` hooks |
| CJK/HU plan directories | — | ✅ Catalog gen for missing 7 locales |
| CJK cover typography | — | ✅ Font registry + wrapping rules |

### Recommended propagation waves (operator scope — do not self-merge)

Keep PRs ≤180 files; one brand or one locale per wave where possible.

| Wave | Scope | Action | Est. fix type |
|------|-------|--------|---------------|
| **W0** | Engine gate | Add `formula4=True` (or flag) to `phoenix_v4/naming/cli.py:68-74` so generation rejects inverted titles | Code (small) |
| **W1** | `en_US` × canonical-37 | Per-brand regen script (fork `waystream_subtitle_regen.py` → `{brand}_title_regen.py`) on `book_plans_en_us`; verify F4≥95% per brand | Re-run |
| **W2** | `en_US` store_series | Populate `store_series.name` from `series_templates.yaml` + persona flavor for each series_plan | Build + regen |
| **W3** | Cover proof | `brand_covers.render_brand --brand <X> --contact` for each canonical brand; fix pool gaps | Re-run |
| **W4** | Western locales (`de_DE`, `fr_FR`, `es_*`, `it_IT`, `pt_BR`) | Translate authored `en_US` winners OR regen with locale templates; **block on translation QA** | Build |
| **W5** | CJK + `hu_HU` | Create missing `book_plans_*` dirs; locale fonts in cover stack; manga-forward lane content | Build |
| **W6** | Waystream non-en | Apply W1 regen to Waystream rows in `book_plans_de_de`, `book_plans_fr_fr`, etc. | Re-run after W4 |

---

## File index (evidence anchors)

| Claim | File:line |
|-------|-----------|
| 37 brands | `specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md:44-50` |
| 14 locales | `config/catalog/catalog_generation_config.yaml:7-22` |
| Brand-general generator | `phoenix_v4/naming/generator.py:184-233` |
| Formula-4 not enforced in CLI | `phoenix_v4/naming/cli.py:68-74`, `validator.py:179-184` |
| Waystream-only regen | `scripts/catalog/waystream_subtitle_regen.py:24-25,149-154,546-549` |
| Formula-4 thresholds | `phoenix_v4/policy/naming_scoring.yaml:47-53` |
| Waystream Formula-4 prefs | `omega/title_entropy/subtitle_patterns.yaml:28-31,301-305` |
| Skeleton title emission | `scripts/catalog/gen_plan_skeletons.py:104-105` |
| Series hook titles (naming) | `config/catalog_planning/series_templates.yaml:11,175` |
| Manga series names | `config/catalog_planning/brand_series_plans.yaml:36-37` |
| store_series example | `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__...__watcher.yaml:5-7` |
| Cover adapter series fallback | `scripts/publish/brand_covers/adapter.py:50` |
| Collision solver | `scripts/publish/waystream_covers/layout_solver.py:1-6,24-31` |
| Shared brand renderer | `scripts/publish/brand_covers/__init__.py:1-4`, `render_brand.py:18-20` |
| Per-brand fingerprint hash | `scripts/publish/brand_covers/assignment.py:65-77` |
| Waystream hand author cards | `config/publishing/waystream_cover_system.yaml:36-48` |
| Verbatim plan text on cover | `scripts/publish/waystream_covers/templates.py:1-8,62-67` |
| No CJK fonts in cover stack | `scripts/publish/waystream_covers/fonts.py:17-37`; `render_kdp_cover.py:336-370` |
| Sample inverted skeleton | `config/source_of_truth/book_plans_en_us/stabilizer__...__overwhelm.yaml:14-15` |
| Sample Waystream F4 pass | `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__...__false_alarm.yaml:14-15` |

---

## CLOSEOUT

1. **Four how-it-scales descriptions:** Titles (brand-general engine, Waystream-only F4 enforcement), subtitles (template weights + F4 persona gate), series (three layers — templates/manga/store; no catalog engine), covers (8-family shared library × hash fingerprint × locale text layer).

2. **Coverage matrix:** Locale summary table above + machine grid at `artifacts/qa/naming_cover_37x14_matrix.json`. Only **Waystream `en_US`** hits Formula-4 / persona / collision-proof bar today.

3. **Propagation gap:** Proven fixes cover **1 imprint × 1 locale**; **517 canonical brand-locale cells** plus **Waystream × 13 locales** still on skeleton/English/stub patterns.

4. **Re-run vs build:** Title/subtitle regen and cover render = **re-run**; localization, store_series engine, CJK fonts, missing plan dirs = **build**.

5. **Recommended waves:** W0 engine gate → W1 en_US per-brand regen → W2 store_series → W3 cover proof → W4–W6 locale expansion (operator chooses scope per PR).

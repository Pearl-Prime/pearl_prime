# V1.2 Dispatch + Dashboard Wiring — V1 Spec

**Cap entry:** `V1_2_DISPATCH_DASHBOARD_WIRING_V1_01`
**Status:** AUTHORED 2026-05-12
**Authority:** Pearl_Architect (operator-ratified)
**Anchors:**
- PR #1051 (magical+serial framework)
- PR #1053 (Gen Z/Alpha portal extension)
- PR #1048 (Conductor v3 dispatch bridge — original V1.1 wiring)
- 20 V1.2 cluster YAML files at `artifacts/marketing/v1_2_themes_*_cluster_*.yaml`

## 1. Goal

Wire the 500-series V1.2 themes catalog into:
1. The dispatch bridge (`scripts/catalog/v1_1_allocation_to_batch_plan.py`)
2. The book series index (`scripts/catalog_visibility/build_book_series_index.py`)
3. The manga series index (`scripts/catalog_visibility/extract_manga_series_index.py`)

So that:
- Pearl_Conductor v3 can fan out 13,540 unique batches against V1.2 themes
- Both catalog dashboards display V1.2 planned entries with the new metadata chips (magical_register / serial_engine / portal_mechanic / persona_archetype)

## 2. V1.2 source format

20 cluster YAML files at `artifacts/marketing/v1_2_themes_<locale>_cluster_<x>.yaml`:

```yaml
schema_version: "1.2"
locale: en_US                 # one of en_US / ja_JP / zh_TW / zh_CN
cluster: A                    # one of A (Anxiety) / B (Cognitive) / C (Grief) / D (Relational) / E (Gen-Alpha)
cluster_name: "Anxiety/Somatic/Sleep"
total_series_target: 25
series:
  - series_id: <brand>__<locale>__<slug>
    brand_id: <canonical brand id>
    locale: <locale>
    persona_archetype: <Gen Z/Alpha/Mill specific persona prose>
    daily_life_anchor: <enum>
    portal_mechanic: <enum>
    episodic_frame_per_volume: <enum>
    magical_register: <enum: supernatural_everyday | magical_realism | soft_fantasy | isekai | occult_cosmic | none>
    serial_engine: <enum: mystery_box | power_escalation_ladder | companion_roster | location_anthology | case_of_the_week | life_stage_rhythm>
    long_arc_spine: <one-sentence 100+ vol question>
    volume_runway_target: <int ≥30>
    reading_platform_fit: <webtoon_vertical | manga_traditional | both>
    series_title: ...
    series_logline: ...
    series_description: ...   # 80-150 word prose
    opening_5_volume_arc:
      - vol_1: ...
      - ...
    comp_titles: [...]
    reader_promise: ...
    marketing_angle: ...
    genre_family: <enum from constraint doc>
    emotional_engine: ...
    audience: ...
```

Total: 4 locales × 5 clusters × 5 brands × 5 series = **500 series** across 20 files.

## 3. Wiring

### 3.1 Dispatch bridge — `--v1-2` flag

Added to `scripts/catalog/v1_1_allocation_to_batch_plan.py`:

```bash
PYTHONPATH=. python3 scripts/catalog/v1_1_allocation_to_batch_plan.py \
    --v1-2 \
    --run-id <id> \
    --output-dir <path>
```

When `--v1-2` is set:
- Loads the 20 V1.2 cluster files via `_load_v1_2_series_themes(repo_root)`
- Reshapes into the V1.1 contract expected by `_series_for(brand, locale, themes)`:
  - `series_title` → passthrough
  - `serial_engine` → `arc_shape`
  - `series_logline` → `emotional_throughline`
  - `reading_platform_fit` → `surface_priority`
- V1.2-specific metadata is preserved on `series._v1_2` for downstream consumers
- Bridge produces the same 13,540 unique batches (cover + panel) but driven by V1.2 content

Default behavior (no flag): unchanged, V1.1 path preserved for backwards compatibility.

### 3.2 Book series index — `_load_v1_2_planned_books()`

Added to `scripts/catalog_visibility/build_book_series_index.py`:
- Globs `artifacts/marketing/v1_2_themes_*_cluster_*.yaml`
- Emits one book index row per series with `book_id = series_id`, `status = "planned"`, `source_version = "v1.2"`
- Carries through V1.2 metadata fields (magical_register, serial_engine, portal_mechanic, persona_archetype, long_arc_spine, volume_runway_target, opening_5_volume_arc, comp_titles, reader_promise, marketing_angle, emotional_engine, audience, cluster_id) for dashboard card display
- Merged into `build_book_series_index()` AFTER teacher_books (rendered) and V1.1 planned rows; deduped by `book_id` (rendered or earlier-planned wins)

Result: **13 rendered + 740 V1.1 planned + 500 V1.2 planned = 1,253 books**

### 3.3 Manga series index — `_load_v1_2_manga_series()`

Added to `scripts/catalog_visibility/extract_manga_series_index.py`:
- Same glob pattern
- Emits one manga index row per series with `series_id` from V1.2 file, `status = "planned"`, `source_version = "v1.2"`
- Maps V1.2 fields to manga index schema:
  - `serial_engine` → both `serialization_engine` (legacy field) and `serial_engine` (V1.2 field)
- V1.2-specific metadata preserved as above
- Merged into `extract_all()` AFTER profile-file series discovery; deduped by `series_id`

Result: **312 legacy + 500 V1.2 = 812 manga series**

## 4. Migration path

The V1.1 path is fully preserved. To migrate Pearl_Conductor v3 to V1.2:
1. Conductor v3 invocation adds `--v1-2` flag to its dispatch bridge call
2. Daily digest reports include both source_version counts
3. No schema migration in checkpoint TSV or downstream tooling — only the input source changes

## 5. Test coverage

`tests/catalog/test_v1_2_allocation_to_batch_plan.py`:
- `test_load_v1_2_series_themes_loads_20_files` — confirms glob picks up exactly 20 files
- `test_v1_2_flag_produces_13540_unique_batches` — full dry-run integration test
- `test_v1_2_passthrough_metadata` — confirms `_v1_2` sub-dict carries all richer fields

`tests/catalog_visibility/test_v1_2_dashboard_wiring.py`:
- `test_load_v1_2_planned_books_returns_500` — book index V1.2 row count
- `test_load_v1_2_manga_series_returns_500` — manga index V1.2 row count
- `test_v1_2_book_dedupe_prefers_rendered` — rendered wins over planned on book_id collision

## 6. Out of scope (future PRs)

- Dashboard template chip rendering for V1.2 metadata (separate PR — purely cosmetic, no data flow change)
- Conductor v3 Phase 2 fan-out armed against V1.2 (separate operator approval gate)
- V1.2 → V2.0 audiobook + podcast surface expansion (separate spec)

## 7. Cap entry registration

Append to `docs/PEARL_ARCHITECT_STATE.md`:

```
V1_2_DISPATCH_DASHBOARD_WIRING_V1_01 (2026-05-12)
- Bridge: --v1-2 flag in allocation_to_batch_plan.py
- Book index: _load_v1_2_planned_books in build_book_series_index.py
- Manga index: _load_v1_2_manga_series in extract_manga_series_index.py
- V1.1 path preserved (backwards compat default)
- Verified: 13,540 unique batches; 1,253 books (500 V1.2); 812 manga (500 V1.2)
```

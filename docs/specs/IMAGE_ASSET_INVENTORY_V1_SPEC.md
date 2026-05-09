# Image Asset Inventory V1 — Spec

**Status:** Draft V1 (audit-paired; ratification target: Pearl_Architect cap entry alongside next program review)
**Owner:** Pearl_Editor (schema); Pearl_Brand (dashboard consumer)
**Authority parent:** `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (Phase 1 P1 surface 2 + P2 surface 3)
**Companions:** `artifacts/qa/image_asset_inventory_audit_2026-05-09.md`, `artifacts/qa/image_asset_inventory_2026-05-09.tsv`, `artifacts/qa/parallel_image_generation_plan_2026-05-09.md`

---

## 1. Purpose

Define the canonical schema, classification rules, and dashboard consumer contract for the Phoenix Omega **image asset inventory**. The inventory is the single source of truth (SSOT) for "what images exist per brand × per locale × per asset type" across all 6 known image surfaces.

### Why this spec exists

1. **Operator visibility gap.** Post-PR #977 dashboards surface only the brand active/inactive flag from `brand_wizard YAML`. They do **not** surface image inventory depth. Operators must SSH or `find` the repo to assess catalog completeness — this is unacceptable for go-live.
2. **Reproducibility.** The audit produced on 2026-05-09 is a snapshot. The inventory must be regenerable on demand by the same scanner with the same classification rules.
3. **Dashboard contract.** `ws_dashboard_image_inventory_consumer_20260509` will read the TSV produced by this spec. The schema must be stable and forward-compatible.

---

## 2. Six known image surfaces

| ID | Path | Convention | Locale signal | Pipeline source |
|---|---|---|---|---|
| S1 | `assets/authors/cover_art/` | `<teacher>_base.png` (or legacy variants in `_legacy_*`) | locale-agnostic (`n/a`) | `manual_legacy_or_seed` |
| S2 | `brand-wizard-app/public/assets/{covers/{kdp,audiobook},covers/,manga_covers,manga_panels,video_bank}/` | KDP/audiobook: `cover_<teacher>_<topic>.png`; manga: `<teacher>_<variant>.png`; panels: `<teacher>/<seq>.png`; video: `vb_<theme>.png` | `en_US` (default; explicit only if path token) | `brand_wizard_seed` |
| S3 | `artifacts/pipeline_examples/{<teacher>,manga_book,manga_covers}/*.png` | Per-teacher demos + cross-cut examples | `en_US` (default) | `pipeline_example_demo` |
| S4 | `artifacts/manga/{anxiety_series,image_bank,stillness_press_qa_run,...}/*.png` | Stillness Press anxiety series + reusable image bank + QA runs | `en_US` (default) | `manga_render_legacy`, `manga_image_bank_seed`, `manga_qa_run` |
| S5 | `artifacts/onboarding_proof_media/images/*.png` | `cmp_<dimension>_<locale_token>_<version>.png` | inferred from filename token (`_jp`, `_tw`, `_cn`, `_us`) | `onboarding_proof_seed` |
| S6 | `assets/manga_catalog/<brand>/<series>/{main_character.png,lora_refs/*.png,bg/*.png,...}` | Brand-bound, series-bound. Series ID encodes locale token. | inferred from series_id (`_jp`, `_kr`, `_tw`, `_cn`, `_us`); fallback `en_US` | `manga_catalog_seed` |

**S6 is the dominant surface (93 % of all PNGs).** It was discovered during the 2026-05-09 audit and is added to this spec as a first-class surface.

> **Surface registration is a closed set.** Any new image surface MUST be added to this spec via AMENDMENT (Pearl_Architect) with an updated scanner.

---

## 3. TSV schema (canonical)

File path: `artifacts/qa/image_asset_inventory_<DATE>.tsv` (UTF-8, tab-separated, one header row + N data rows).

| Column | Type | Domain | Definition |
|---|---|---|---|
| `brand_id` | string | canonical brand from `config/manga/canonical_brand_list.yaml` (37 entries) **or** `n/a_<reason>` for unbound | The manga brand the asset belongs to. |
| `teacher_id` | string | one of the 12 manga teachers + 5 book pen names + `""` for series-bound only | The teacher (character LoRA owner) per `brand_lora_plans.yaml.character_loras`. |
| `asset_type` | string | one of the 14 types in §4 | Functional category of the asset. |
| `locale` | string | one of `en_US`, `ja_JP`, `zh_TW`, `zh_CN` (4 primary) + `ko_KR` (observed) + `n/a` (locale-agnostic) | Target market / language. |
| `path` | string | repo-relative POSIX path | Path to the PNG file from repo root. |
| `exists` | enum | `yes` / `no` | Whether the file exists on disk at scan time. |
| `size_bytes` | integer | ≥ 0 | File size on disk. |
| `is_real_image` | enum | `yes` / `no_lfs_pointer` | `yes` iff `size_bytes ≥ 1024`. <1 KB = LFS pointer (file content not yet fetched). |
| `last_mtime` | string | ISO-8601 UTC, `YYYY-MM-DDTHH:MM:SSZ` | File modification time. |
| `source_pipeline` | string | one of the values in §2 column "Pipeline source" | Origin pipeline (for re-generation routing). |
| `series_id` | string | manga series identifier from `config/manga/manga_brand_series_plan.yaml`, or `""` | Optional series binding (only for S6 manga_catalog assets). |
| `notes` | string | free text | Human-readable note (e.g., "anxiety series rendered output"). |

**Stability promise:** the schema is append-only. Adding columns is a minor version bump; renaming or removing requires an AMENDMENT.

---

## 4. asset_type taxonomy (closed set)

The base 8 types from the operator prompt, extended with 6 manga_catalog-specific types (necessary because S6 is dominant). All 14 are normative.

| asset_type | Definition |
|---|---|
| `author_base` | Locale-agnostic teacher portrait (S1 only). |
| `kdp_cover` | KDP paperback / ebook front cover. |
| `audiobook_cover` | Audiobook square cover. |
| `showcase_cover` | 1–3 brand showcase covers per locale (the `cover_<teacher>_<topic>.png` pattern). |
| `manga_cover` | Manga cover variant (front / profile / scene / symbolic / three_quarter / portrait / topic). |
| `manga_panel` | Story page panel (manga interior). |
| `manga_protagonist` | `main_character.png` (1 per series). |
| `manga_lora_ref` | LoRA training reference view (per `brand_lora_plans.character_loras.<teacher>.reference_views`). |
| `manga_background` | Reusable BG image (subdir `bg/`). |
| `manga_image_bank` | Reusable BG/motif/character ref for the reuse-before-render pipeline. |
| `manga_render` | Rendered manga output (legacy series; e.g. anxiety_series). |
| `manga_qa_render` | QA-run rendered output. |
| `pipeline_example` | Cross-cut pipeline demo image. |
| `onboarding_proof` | Wizard comparison thumbnail. |
| `video_bank` | Brand-agnostic video b-roll thumbnail. |

> Out of vocabulary types must be added via AMENDMENT to this spec. The scanner emits a warning to stderr if an asset cannot be classified.

---

## 5. Dashboard consumer contract (`ws_dashboard_image_inventory_consumer_20260509`)

### 5.1 Data source

The dashboard panel reads:

1. **Primary:** `artifacts/qa/image_asset_inventory_<LATEST_DATE>.tsv` — refreshed on a weekly Monday cadence by `ws_image_inventory_audit_recurring_20260509`.
2. **Optional:** `artifacts/qa/image_asset_inventory_matrix_<LATEST_DATE>.tsv` — pre-aggregated `(brand × locale)` summary.

The dashboard MUST detect the latest dated file via lexicographic sort of the date suffix (`YYYY-MM-DD`). Falling back to a stale file is acceptable; aborting the panel render is not.

### 5.2 UI requirements

- **Per active brand → table:** `locale × asset_type` (rows × columns), cell value = current count.
- **Color coding (per cell):**
  - 🟢 green: `current ≥ 0.8 × target` (per `parallel_image_generation_plan_2026-05-09.md` §3 targets)
  - 🟡 yellow: `0.2 × target ≤ current < 0.8 × target`
  - 🔴 red: `current < 0.2 × target`
  - ⚫ gray: `target = 0` (asset not applicable to this cell, e.g. `author_base` for non-`n/a` locale)
- **Refresh trigger:** on dashboard load + manual "Refresh inventory" button. The button re-reads the TSV from disk; it does NOT re-run the scan (scan is the audit ws's responsibility on weekly cadence).
- **Empty cell behavior:** show `0` with red status; do not omit.
- **"Inactive" brand handling:** active vs inactive comes from `brand_wizard YAML` (PR #977 SSOT). Inactive brands are listed in a collapsed second section ("Inactive — no targets") with a single sentinel cell `n/a`.

### 5.3 JSON contract (frontend ⇄ backend)

The dashboard backend exposes `GET /api/inventory/snapshot` returning:

```json
{
  "snapshot_date": "2026-05-09",
  "tsv_path": "artifacts/qa/image_asset_inventory_2026-05-09.tsv",
  "totals": {
    "total_pngs": 6528,
    "real_images": 6447,
    "lfs_pointers": 81,
    "active_brands": 18,
    "zero_content_brands": 19
  },
  "per_brand": [
    {
      "brand_id": "stillness_press",
      "active": true,
      "tier": "flagship",
      "totals_per_locale": {
        "en_US": 1144,
        "ja_JP": 551,
        "zh_TW": 192,
        "zh_CN": 204
      },
      "per_locale_per_type": {
        "en_US": {
          "author_base": 0,
          "kdp_cover": 4,
          "audiobook_cover": 2,
          "manga_panel": 94,
          "manga_protagonist": 79,
          "manga_lora_ref": 790,
          "manga_image_bank": 61,
          "manga_render": 81,
          "manga_qa_render": 3,
          "pipeline_example": 22,
          "showcase_cover": 1,
          "manga_cover": 7
        },
        "ja_JP": { "manga_panel": 56, "manga_protagonist": 45, "manga_lora_ref": 450, "...": 0 },
        "zh_TW": { "manga_panel": 16, "manga_protagonist": 16, "manga_lora_ref": 160, "...": 0 },
        "zh_CN": { "manga_panel": 17, "manga_protagonist": 17, "manga_lora_ref": 170, "...": 0 }
      },
      "completion_pct_per_locale": {
        "en_US": 17.2,
        "ja_JP": 8.3,
        "zh_TW": 2.9,
        "zh_CN": 3.1
      }
    }
  ]
}
```

**`completion_pct_per_locale`** = `Σ asset_count / Σ asset_target × 100` per cell, where targets are from `parallel_image_generation_plan_2026-05-09.md` §3.

**Stability:** the JSON shape is forward-compatible (new keys allowed; existing keys never removed without AMENDMENT).

### 5.4 Performance targets

- Dashboard backend reads TSV (≤10 MB at current scale) and aggregates in <500 ms.
- Frontend renders 18 active-brand tables in <1 s.
- Manual refresh: <1 s round-trip from button click to repaint.

---

## 6. Scanner pseudocode

The reference scanner is `scripts/qa/scan_image_inventory.py` (proposed, to land under `ws_image_inventory_audit_recurring_20260509`):

```python
SURFACES = [
    "assets/authors/cover_art",
    "brand-wizard-app/public/assets",
    "artifacts/pipeline_examples",
    "artifacts/manga",
    "artifacts/onboarding_proof_media/images",
    "assets/manga_catalog",
]

LFS_THRESHOLD = 1024  # bytes

TEACHER_TO_BRAND = {  # from brand_lora_plans.yaml.character_loras + V1 video binding
    "ahjan": "stillness_press",
    "joshin": "cognitive_clarity",
    "pamela_fellows": "somatic_wisdom",
    "master_feung": "qi_foundation",
    "miki": "digital_ground",
    "maat": "heart_balance",
    "junko": "relational_calm",
    "master_wu": "warrior_calm",
    "master_sha": "sleep_restoration",
    "omote": "body_memory",
    "ra": "solar_return",
    "sai_ma": "devotion_path",
    "adi_da": "n/a_deferred_v1_1",
    # book pen names
    "ajahn_x": "n/a_book_pen_name",
    "diane_reyes": "n/a_book_pen_name",
    "kai_nakamura": "n/a_book_pen_name",
    "luna_hart": "n/a_book_pen_name",
    "marcus_cole": "n/a_book_pen_name",
}

LOCALE_TOKENS = [  # search-tokens in path/filename
    ("ja_JP", ["_jp", "_japan", "_ja_jp"]),
    ("zh_TW", ["_tw", "_taiwan", "_zh_tw"]),
    ("zh_CN", ["_cn", "_china", "_zh_cn"]),
    ("ko_KR", ["_kr", "_korea", "_ko_kr"]),
    ("en_US", ["_us", "_en_us", "_usa"]),
]

# Per-surface classify_path() rules — see docs §7.
```

Full reference implementation is shipped under `ws_image_inventory_audit_recurring_20260509`. The 2026-05-09 audit used an ad-hoc equivalent (not committed; output `image_asset_inventory_2026-05-09.tsv` is committed).

---

## 7. Classification rules (per-surface)

Encoded in the scanner's `classify_path()`:

### S1 `assets/authors/cover_art/`

- Pattern: `<teacher>_base.png`
- `asset_type = author_base`
- `brand_id = TEACHER_TO_BRAND[<teacher>]`
- `teacher_id = <teacher>`
- `locale = "n/a"` (locale-agnostic)

### S2 `brand-wizard-app/public/assets/`

| Subpath | asset_type | brand_id resolution | locale |
|---|---|---|---|
| `covers/kdp/<f>` | `kdp_cover` | `TEACHER_TO_BRAND[teacher_from_filename(<f>)]` | inferred from path tokens, default `en_US` |
| `covers/audiobook/<f>` | `audiobook_cover` | same | same |
| `covers/<f>` | `showcase_cover` | same | `en_US` |
| `manga_covers/<f>` | `manga_cover` | same | `en_US` |
| `manga_panels/<teacher>/<f>` | `manga_panel` | `TEACHER_TO_BRAND[<teacher>]` | `en_US` |
| `video_bank/<f>` | `video_bank` | `n/a_brand_agnostic` | `n/a` |

### S3 `artifacts/pipeline_examples/`

- `<teacher>/<f>` → `pipeline_example`, brand from teacher.
- `manga_book/<f>` or `manga_covers/<f>` → `pipeline_example`, brand=`stillness_press` (default).

### S4 `artifacts/manga/`

| Subdir | asset_type | brand_id | series_id |
|---|---|---|---|
| `anxiety_series/...` | `manga_panel` (if "panel" in path) or `manga_render` | `stillness_press` | `anxiety_series` |
| `image_bank/...` | `manga_image_bank` | `stillness_press` | "" |
| `stillness_press_qa_run/...` | `manga_qa_render` | `stillness_press` | "" |
| `<other>/...` | `manga_render` | `stillness_press` | "" |

### S5 `artifacts/onboarding_proof_media/images/`

- `cmp_<dim>_<loc>_v<n>.png` → `asset_type=onboarding_proof`, `brand_id=n/a_brand_agnostic`, `locale` inferred from `_jp/_tw/_cn` token, default `en_US`.

### S6 `assets/manga_catalog/<brand>/<series>/...`

| Filename pattern | asset_type |
|---|---|
| `main_character.png` | `manga_protagonist` |
| `lora_refs/*` | `manga_lora_ref` |
| `bg/*` or `bg.png` | `manga_background` |
| anything else | `manga_panel` |

`brand_id = <brand>` (top dir), `series_id = <series>`, `locale` inferred from series_id token.

---

## 8. Refresh cadence & ownership

| Cadence | Action | Owner |
|---|---|---|
| Weekly Monday (matches WORLDWIDE-CATALOG-GO-LIVE Q5 weekly cadence) | Re-run scanner; commit dated `image_asset_inventory_<DATE>.tsv` + matrix; update audit MD if findings change | Pearl_Editor (`ws_image_inventory_audit_recurring_20260509`) |
| On-demand | Manual refresh from operator dashboard | Pearl_Brand (dashboard panel) |
| After every Pearl Star wave completion | Re-run scanner so dashboard reflects progress | Pearl_Dev / Pearl_Int (`ws_image_batch_generation_orchestration_20260509`) |

---

## 9. Anti-drift

1. **No new image surface** without an AMENDMENT to this spec (Pearl_Architect cap entry update).
2. **No asset_type vocabulary expansion** without an AMENDMENT.
3. **No silent schema column changes** — append-only.
4. **Brand normalization map** (`brand_lora_plans.yaml` short forms ↔ `canonical_brand_list.yaml` extended forms) is documented in the scanner; updating it requires this spec to be edited in lockstep.
5. The scanner MUST never write to image files; read-only.
6. The dashboard consumer MUST never trigger generation; read-only over the TSV.

---

## 10. Open questions (deferred)

- Q1: should `manga_qa_render` and `manga_render` be merged into one type? (Currently separated for surface origin clarity.)
- Q2: should `ko_KR` be elevated to a primary locale alongside the 4 (en_US, ja_JP, zh_TW, zh_CN)? Operator decision required (cap AMENDMENT). Currently treated as bonus inventory.
- Q3: should `assets/manga_catalog/` paths be authoritative for the dashboard's "manga preview" tile, or should that pull from `brand-wizard-app/public/assets/manga_covers/` only? Recommend: catalog for backend QA, brand-wizard for public-facing display.
- Q4: should LFS pointer files (size <1 KB) count toward "complete" in dashboard color coding? Currently they count as `is_real_image=no_lfs_pointer` and the dashboard treats them as missing. Operator decision required.

---

## 11. Cross-references

- `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` cap entry — `docs/PEARL_ARCHITECT_STATE.md`
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` — Path X book vs. manga split
- `config/manga/canonical_brand_list.yaml` — 37-brand canon
- `config/manga/brand_lora_plans.yaml` — LoRA chain SSOT
- `config/manga/manga_brand_series_plan.yaml` — per-brand series allocation
- `specs/AI_MANGA_PIPELINE_SUMMARY.md` — manga pipeline summary
- `docs/MANGA_IMPLEMENTATION_OUTLINE.md` — implementation slices
- `artifacts/qa/image_asset_inventory_audit_2026-05-09.md` — first audit instance
- `artifacts/qa/parallel_image_generation_plan_2026-05-09.md` — generation plan consumer

# ACTIVE_BRAND_SSOT_V1 — Brand wizard YAML as active/inactive SSOT

**Status:** Phase 1 (classifier only; consumers in separate workstreams)  
**Caps:** `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` + AMENDMENT **2026-05-08-PRIORITIES** (Q4 = `brand_wizard` YAML SSOT for active/inactive classification)  
**Subsystem:** `brand_admin` (primary); downstream dashboards/packaging consume later  
**Authority:** `docs/PEARL_ARCHITECT_STATE.md`, `docs/specs/WORLDWIDE_CATALOG_GO_LIVE_V1_PROGRAM_SPEC.md`, `BRAND_ADMIN_CANONICAL_PACKAGE.md`

---

## 1. Problem

Catalog and packaging surfaces need a **single reusable** answer to: *is brand X active for go-live?*  
Path X manga canon (`config/manga/canonical_brand_list.yaml`) lists **37** strategic brands; the Pearl_Prime book seed (`config/brand_registry.yaml`) lists locale-keyed book brands. Neither file is the SSOT for **wizard completeness** — that role belongs to **checked-in brand_wizard bundles** per Q4.

---

## 2. Canonical on-disk layout

**Directory (repo-relative):** `brand-wizard-app/brands/`

- One YAML file per brand: `<brand_id>.yaml` (snake_case id matching registry keys).
- Discovery on 2026-05-09: no `*.yaml` files were present under `brand-wizard-app/` in-tree (wizard exports download from the SPA). Until bundles are committed here, **all registry brands classify as inactive** with reason `no brand_wizard YAML found`.

---

## 3. Registry inputs (read-only)

| Source | Path | Purpose |
|--------|------|---------|
| Manga Path X canon | `config/manga/canonical_brand_list.yaml` | `brands:` keys → manga brand IDs (37) |
| Book seed | `config/brand_registry.yaml` | `brands:` keys → book brand IDs |
| Music (optional) | `config/music/music_brand_registry.yaml` | `brands:` keys when cap **MUSIC-MODE-BRAND-INTEGRATION-V1-01** lands |

**Classifier universe** = sorted union of all keys above. If the music registry file is **missing**, music IDs are **empty**, `music_registry_deferred` is `True`, and no error is raised (graceful deferral).

---

## 4. Required `brand_wizard` YAML fields (v1)

Top-level keys (all required, non-empty where string):

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | scalar | e.g. `1` |
| `brand_id` | string | Must match filename stem `<brand_id>.yaml` |
| `display_name` | string | Human label |
| `wizard_core` | mapping | Must contain string keys `tagline`, `positioning_line` (non-empty strings) |

**Partial file:** any missing required key → **inactive**, reason `missing required field: <first missing dotted path>`.

**Invalid YAML / unreadable file:** inactive with reason `brand_wizard YAML unreadable or invalid YAML` or `brand_wizard YAML root must be a mapping`.

**`brand_id` mismatch** (file `foo.yaml` but `brand_id: bar`) → inactive with mismatch reason.

---

## 5. Classifier API (`scripts/brand/active_brand_classifier.py`)

| Symbol | Description |
|--------|-------------|
| `ActiveBrandClassifier(repo_root=..., wizard_yaml_dir=...)` | Construct with optional roots (defaults: repo root + `brand-wizard-app/brands`) |
| `.snapshot()` | `dict[brand_id, BrandWizardStatus]` with `.active` and `.reason` |
| `.is_active(brand_id)` | `bool` |
| `.list_active()` / `.list_inactive()` | Sorted brand id lists |
| `.reason_for(brand_id)` | Reason string (empty when active) |
| `.music_registry_deferred` | `bool` |
| `.music_brand_ids()` | Music-only id list (empty when deferred) |
| `list_active()`, `list_inactive()`, `is_active()`, `reason_for()`, `activation_snapshot()` | Module-level helpers using a memoized default classifier |
| `manga_canonical_brand_ids()` / `summarize_manga_slice()` | Reporting helpers for the 37-brand manga slice |

---

## 6. Downstream consumer pattern (out of scope for Phase 1)

1. Instantiate `ActiveBrandClassifier()` (or inject paths in tests).
2. Gate UI / jobs on `.is_active(brand_id)` or `.snapshot()`.
3. Do **not** duplicate “active” logic from `canonical_brand_list.yaml` alone.

**Planned consumer workstreams (names only):**

- `ws_dashboard_active_brand_consumer_20260509`
- `ws_brand_admin_active_brand_consumer_20260509`
- `ws_catalog_generator_active_brand_consumer_20260509`
- `ws_weekly_packaging_active_brand_consumer_20260509`

---

## 7. Music mode

This spec **does not** define music-mode wizard schema (owned by **MUSIC-MODE-BRAND-INTEGRATION-V1-01**). The classifier **must** tolerate absent `music_brand_registry.yaml` and expose deferral; when the registry exists, music brand IDs join the universe and use the **same** YAML directory and required-field rules.

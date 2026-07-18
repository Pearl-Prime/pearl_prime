# Active brand SSOT — Phase 1 implementation notes

**Project ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Date:** 2026-05-09  
**Caps:** `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` + AMENDMENT **2026-05-08-PRIORITIES** (Q4 = `brand_wizard` YAML SSOT)  
**Subsystem:** `brand_admin` (primary)

---

## 1. What shipped (P0 surface)

| Deliverable | Path |
|-------------|------|
| Classifier | `scripts/brand/active_brand_classifier.py` |
| Unit tests | `tests/brand/test_active_brand_classifier.py` |
| Spec | `docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md` |
| This log | `artifacts/qa/active_brand_ssot_implementation_2026-05-09.md` |

**Out of scope (this PR):** dashboard, brand admin UI, weekly packaging, catalog generator wiring — separate consumer workstreams (named below).

---

## 2. Canonical brand_wizard YAML location

On-disk SSOT directory (repo-relative): **`brand-wizard-app/brands/*.yaml`**

Discovery (`find … -path '*/brand-wizard*' -name '*.yaml'` excluding `.claude` and `*_wt`) showed **no** committed per-brand wizard bundles under `brand-wizard-app/` at implementation time — the SPA emits downloads; operators have not yet landed committed YAML into `brands/`.

---

## 3. Acceptance criteria (met)

- Reads union of brand IDs from `config/manga/canonical_brand_list.yaml` and `config/brand_registry.yaml`.
- Optional `config/music/music_brand_registry.yaml`: when **missing**, classifier exposes `music_registry_deferred=True`, `music_brand_ids()==[]`, and **no exception** (deferral until MUSIC-MODE-BRAND-INTEGRATION-V1-01).
- Missing YAML → inactive, reason `no brand_wizard YAML found`.
- Partial YAML (required field missing) → inactive, reason `missing required field: …`.
- Required-field set documented in `ACTIVE_BRAND_SSOT_V1_SPEC.md` (v1 minimal bundle: `schema_version`, `brand_id`, `display_name`, `wizard_core` with `tagline` + `positioning_line`).
- No edits to `canonical_brand_list.yaml`, `brand_lora_plans.yaml`, any wizard YAML, or any consumer.

---

## 4. Live snapshot (current tree, 2026-05-09)

Command (dogfood):

```bash
PYTHONPATH=. python3 -c "from scripts.brand.active_brand_classifier import list_active, list_inactive; print('active:', len(list_active()), 'inactive:', len(list_inactive()))"
```

**Result:**

| Metric | Value |
|--------|------:|
| `len(list_active())` | **0** |
| `len(list_inactive())` | **61** |
| Manga canonical slice (`summarize_manga_slice`) | **0 / 37 active**, **37 / 37 inactive** |
| Reason (all inactive today) | `no brand_wizard YAML found` (no files under `brand-wizard-app/brands/`) |
| Music registry | **Deferred** — `config/music/music_brand_registry.yaml` absent; `music_brand_ids` length **0** |

Universe size **61** = unique ids across manga (37) + book registry keys (overlap reduces count vs 37+28).

---

## 5. Tests

```bash
PYTHONPATH=. python3 -m pytest tests/brand/test_active_brand_classifier.py -v
```

**Result:** **6 passed** (fixture tree: active complete YAML; missing YAML; partial YAML; empty registries; 37-brand empty wizard dir; music registry absent).

---

## 6. Downstream consumer workstreams (names only)

- `ws_dashboard_active_brand_consumer_20260509`
- `ws_brand_admin_active_brand_consumer_20260509`
- `ws_catalog_generator_active_brand_consumer_20260509`
- `ws_weekly_packaging_active_brand_consumer_20260509`

---

## 7. Worktree note

Branch `agent/active-brand-ssot-v1-20260509` was created via `git worktree add … origin/main` per program hygiene; full `checkout-index` on this monorepo remains expensive, so final authoring and validation ran on the primary clone at `/Users/ahjan/phoenix_omega` with **explicit-path `git add` (4 files)** and the cached-diff gate vs `origin/main`.

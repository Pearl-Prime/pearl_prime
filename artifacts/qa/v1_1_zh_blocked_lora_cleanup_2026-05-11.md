# V1.1 zh_TW + zh_CN `blocked_lora` cleanup — 2026-05-11

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1, Q4 = blocked_lora-first)  
**Owner:** Pearl_Dev  
**Subsystem:** manga_pipeline + integrations  

## STARTUP_RECEIPT

- **Branch:** `agent/v1-1-zh-blocked-lora-cleanup-20260511` from `origin/main`
- **Inputs:** `scripts/catalog/generate_manga_catalog.py`, `config/manga/brand_lora_plans.yaml`, `config/manga/brand_genre_allocation.yaml` (`zh_specific_brand_teacher`)
- **Method:** Regenerated zh_TW + zh_CN catalogs; grouped `blockers` on `readiness_status=blocked_lora`; implemented minimal catalog-side resolution (no new LoRA training, no `blocked_score` changes)

## Root cause (grouped)

| Cause class | Evidence | Resolution |
|-------------|----------|--------------|
| **Marketing `brand_id` base ≠ `brand_style_loras` YAML key** | After `_tw` / `_cn` suffix strip, bases `sleep_repair`, `panic_first_aid`, `gen_z_grounding`, `grief_companion`, `inner_security` are distribution-guide slugs but are **not** keys under `brand_style_loras` (canonical trained keys differ, e.g. `sleep_restoration`). | `_CATALOG_BRAND_STYLE_CANON` in `generate_manga_catalog.py` maps each base to an existing trained style key; `lora_plan_ref` records provenance, e.g. `catalog style map 'sleep_repair'→'sleep_restoration'`. |
| **`bright_presence_tw` style + character** | Base `bright_presence` absent from `brand_style_loras`; teacher `adi_da` had no `character_loras` row. Rows showed `needs_lora_plan` and (on zh_TW) `needs_lora_plan;needs_character_lora` → `blocked_lora` (lora plan takes precedence in status ordering). | Map `bright_presence` → `stillness_press`; add **`character_loras.adi_da`** in `brand_lora_plans.yaml` (new key only; no edits to existing teacher blocks). |

Not observed in this pass: missing files on disk, zh-only license/schema validation, or LoRA metadata schema failures — the generator only checks YAML registry keys.

## Per-row / per-brand resolution (zh lattice)

| Marketing base (after locale strip) | Resolved style key | Rationale (minimal) |
|------------------------------------|--------------------|---------------------|
| `sleep_repair` | `sleep_restoration` | Same sleep / restoration lane as teacher brand `sleep_restoration` |
| `panic_first_aid` | `stabilizer` | Acute regulation → existing “clinical harbor” standard style |
| `gen_z_grounding` | `digital_ground` | Gen Z digital-native positioning |
| `grief_companion` | `body_memory` | Somatic grief / held-loss tone |
| `inner_security` | `relational_calm` | Attachment / relational safety |
| `bright_presence` | `stillness_press` | Taiwan-only spiritual teacher lane; closest existing teacher style anchor until dedicated style assets exist |

## Before / after `blocked_lora` counts

| Locale | Rows | **Before** `blocked_lora` | **After** `blocked_lora` | Notes |
|--------|------|---------------------------|---------------------------|--------|
| zh_TW | 275 | **84** | **0** | Remaining non-ready rows: `blocked_character_lora` only (e.g. `qi_foundation_cultivation` teacher slug mismatch vs archetype `qi_foundation` — **out of scope** for this workstream) |
| zh_CN | 269 | **69** | **0** | Same |

**Sanity:** `en_US` / `ja_JP` readiness breakdown unchanged vs pre-change baseline (`ready` / `blocked_character_lora` counts).

## Files touched (write scope)

1. `scripts/catalog/generate_manga_catalog.py` — style resolution + summary precondition string
2. `config/manga/brand_lora_plans.yaml` — `character_loras.adi_da` only
3. `tests/manga/test_zh_blocked_lora_resolution.py` — new
4. `artifacts/qa/v1_1_zh_blocked_lora_cleanup_2026-05-11.md` — this file

## Pull request

- https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1040

## Follow-up (explicitly not done here)

- **`blocked_score`** — separate `ws_zh_manga_blocked_score_followup`
- **`blocked_character_lora`** for brands whose allocation slug does not match `teacher_brand_archetypes.yaml` `brand_id` (e.g. `qi_foundation_cultivation` vs `qi_foundation`)
- **Production renders** — still require real trained weights matching refs; this change unblocks **catalog readiness gating** only

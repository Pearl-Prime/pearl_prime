# Cover Five-Layer Uniqueness — V1 Spec

**Status:** SPECCED + CODE-WIRED + EXECUTED-REAL sample (13-house grid/roster 2026-07-19)  
**Date:** 2026-07-19  
**Owner lane:** publishing / covers  
**Acceptance layer for this doc:** SPECCED requirements; orchestrator CODE-WIRED via [`scripts/publish/five_layer_cover_orchestrator.py`](../../scripts/publish/five_layer_cover_orchestrator.py); not PROVEN-AT-BAR for catalog-scale five-layer PASS

## 0. Purpose

Define what a book-cover system **must** deliver so:

- every **brand** keeps a consistent visual house identity, and
- every **author**, **series**, **topic**, and **book** still diverges.

This is the MUST / acceptance contract. It consolidates existing doctrine; it does **not** replace the research docs below.

## 1. Cite, do not fork

| Authority | Role |
|---|---|
| [`docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md`](../authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md) | Platform matrix, 4-level identity research, byline fix |
| [`config/publishing/design_grammars/REGISTRY.yaml`](../../config/publishing/design_grammars/REGISTRY.yaml) | `five_layer_uniqueness` L0–L4 + grammar registry |
| [`config/publishing/cover_identity_system.yaml`](../../config/publishing/cover_identity_system.yaml) | Brand / author / series_schemas / book SSOT (13 houses today) |
| [`artifacts/coordination/handoffs/pearl_cover_brand_differentiation_2026-07-18.md`](../../artifacts/coordination/handoffs/pearl_cover_brand_differentiation_2026-07-18.md) | Brand treatment + mark + `--template` + picker landing |
| [`artifacts/research/cover_quality_and_differentiation_framework_2026-05-03.md`](../../artifacts/research/cover_quality_and_differentiation_framework_2026-05-03.md) | House-style research |
| [`config/publishing/bestseller_templates.yaml`](../../config/publishing/bestseller_templates.yaml) | 16 composition templates |
| [`output/pdf/Pearl_Cover_System_2026-07-18.pdf`](../../output/pdf/Pearl_Cover_System_2026-07-18.pdf) | Operator visual doctrine pack |

## 2. Problem statement

**Failure modes this spec exists to kill:**

1. Different brands look like the same layout recolored (palette-only “differentiation”).
2. Brand vibe is OK, but every topic/book inside the house looks identical (title text only changes).
3. Contact sheets / grids that use a non-production path (abstract gradients, full-bleed social treatment) are presented as the production cover system.

**Success:** five identity layers cohere and diverge as specified; a blind reviewer can tell brand apart from brand, and still see topic/book change inside a brand.

## 3. Canonical layer model

Operator language maps to design-grammar L0–L4 and the live KDP path:

| Layer | Operator ask | Required mechanism | Primary SSOT / code |
|---|---|---|---|
| **L0 Market** | Platform + thumbnail legible | Canvas size, contrast, safe zones | `platform_cover_profiles.yaml` |
| **L1 Brand** | House vibe consistent | Typography (family + case) + **treatment** + **signature mark**; palette secondary | `cover_identity_system.yaml` brands; `_BRAND_TREATMENT` / `_BRAND_MARK` in [`scripts/publish/render_kdp_cover.py`](../../scripts/publish/render_kdp_cover.py) |
| **L2 Author** | Thumbprint | Signature color, motif focus, fingerprint shapes/layouts | `cover_identity_system.yaml` authors; author fingerprint in `render_kdp_cover.py` |
| **L3 Series** | Series vibe | Fixed grammar + installment symbol count/arrangement (Schema C) | Waystream / `brand_covers` via plan `store_series`; **thin on KDP identity path** |
| **L4 Book** | Unique book | Title lockup + book seed + register-picked imagery + optional micro-palette | `bank_image_picker.py` + book_seed / identity book fields |
| **Topic** (cross-cuts) | Topic reads different inside a house | Genre typography + composition zones + topic motif + topic-register imagery | `bestseller_templates.yaml`, topic motif map, picker topic |

**Topic is not a separate imprint.** It must change the cover *inside* brand/author constraints — not by swapping the whole house identity.

Palette alone is the **weakest** differentiator and is never sufficient for L1 PASS.

## 4. MUST requirements

Any production path claiming “five-layer uniqueness” MUST satisfy:

### M1 — Brand coherence (L1)

- Same `brand_id` across ≥3 topics shares: signature mark, treatment family, title face/case.
- A blind column of different brands on **one** topic must not collapse to one layout recolored.

### M2 — Topic difference (cross-cut)

- Same brand across ≥2 topics produces visibly different composition and/or field/imagery — not title text alone.
- Proof pattern: [`scripts/publish/validate_book_level_variation.py`](../../scripts/publish/validate_book_level_variation.py) contact sheet (narrow QA, not full catalog).

### M3 — Author thumbprint (L2)

- When a brand has ≥2 authors in roster, covers diverge by fingerprint / accent / type quirk — not identical type+field.

### M4 — Series vibe (L3)

- Same series installment shares a fixed grammar; installment index changes symbol count/arrangement only (Schema C).
- **REQUIRED** for Waystream / [`scripts/publish/brand_covers/render_brand.py`](../../scripts/publish/brand_covers/render_brand.py) path.
- **REQUIRED-WHEN-present** for KDP identity path (series fields on identity / plan); absence must be declared, not silently invented.

### M5 — Book uniqueness (L4)

- Same brand + author + topic + different `book_id`/title → non-identical background/imagery seed.
- Byte-identical backgrounds for two books = **FAIL**.

### M6 — Composition knob

- `--template` / `template_key` may assign any of the **16** compositions without changing L1 house identity.
- Genre still drives topic typography defaults and imagery topic.

### M7 — Imagery policy

- Image-bearing compositions use [`scripts/publish/bank_image_picker.py`](../../scripts/publish/bank_image_picker.py) (brand register), never random topic-only pick.
- Missing / LFS-pointer bank assets = **FAIL open** — never silent fake gradients presented as production covers.

### M8 — Banned

- Palette-only differentiation.
- Abstract-gradient or social full-bleed contact sheets presented as the production KDP path.
- Inventing motif glyphs outside `MOTIF_FN` in [`scripts/publish/waystream_covers/symbols.py`](../../scripts/publish/waystream_covers/symbols.py).
- Claiming `validate_book_level_variation.py` alone satisfies this spec.
- Claiming catalog “37/40 brands × all topics PASS” without G-* artifacts (below).

## 5. Current wiring map (honest)

```text
WIRED TODAY
  cover_identity_system.yaml (13 houses)
       └─► render_kdp_cover.py  ◄── bestseller_templates.yaml (16 comps)
                 ▲
                 └── illustration from bank_image_picker.py (upstream)

PARTIAL
  waystream_covers/* + brand_covers/render_brand.py  (stronger series/author/book for Waystream)
  validate_book_level_variation.py                   (QA: topic + title within brand)

WIRED (2026-07-19)
  scripts/publish/five_layer_cover_orchestrator.py
       └─► pick_image → render_kdp_cover (13 houses only; G-* gate runners)

GAPS
  Series as first-class driver on KDP identity path (Schema C still Waystream)
  40 catalog brands vs 13 identity houses (no silent synthetic house = production PASS)
```

### Proven gold artifacts (do not re-invent; restore/compare)

| Proof | Path | What it shows |
|---|---|---|
| Brand houses | `artifacts/qa/cover_feedback_truth_gen_spark_20260717/house_template_matrix_covers/` | 13 distinct L1 houses |
| Brand matrix montage | `artifacts/qa/cover_feedback_truth_gen_spark_20260717/house_template_matrix.png` | Roster at a glance |
| Brand + topic (+ title) | `artifacts/coordination/handoffs/book_level_variation_validation_20260718/_contact_sheet.jpg` | M2 + M5 inside houses |
| Doctrine PDF | `output/pdf/Pearl_Cover_System_2026-07-18.pdf` | Operator visual pack |
| Offline branch | `offline/cover-brand-differentiation-20260717` | Landed treatment/mark/template/picker |

## 6. Acceptance gates (operator-visible)

Any claim of five-layer PASS must name which gates ran and point to artifact paths (G-CLAIM / acceptance-layer habit).

| Gate | Pass condition |
|---|---|
| **G-BRAND** | 13-house roster montage: distinct houses at ~100×160 thumbnail |
| **G-TOPIC** | Within one brand, ≥2 topics diverge (variation contact-sheet pattern) |
| **G-BOOK** | Same brand+author+topic, ≥2 titles → non-identical field/imagery hashes |
| **G-TEMPLATE** | One brand × ≥5 of 16 compositions still reads as same house |
| **G-PICKER** | Fierce/dark brand never receives office/desk subject when register alternatives exist |

**Claim language:**  
`five-layer PASS` requires G-BRAND + G-TOPIC + G-BOOK at minimum, plus artifact paths.  
`structurally clear` / `CONFIG-EXISTS` / `EXECUTED-REAL sample` are weaker layers — do not upgrade silently.

## 7. What `validate_book_level_variation.py` does and does not cover

| Layer | Covered? |
|---|---|
| L1 Brand | Partial (inherits identity via `book_id`; not the test focus) |
| Topic difference | Yes (limited type-dominant topics) |
| L4 Book uniqueness | Yes (title/seed) |
| L2 Author thumbprint | Barely (one author per brand in cases) |
| L3 Series | No |

It is a **narrow QA harness** for “topics and titles diverge inside a brand after the Jul 18 field-seed fix.” It is **not** the five-layer orchestrator.

## 8. Out of scope for this V1 spec

- Expanding identity YAML to all 40 catalog brands (follow-on; until then catalog-scale “all brands” claims are blocked).
- FLUX/GPU regeneration; production imagery remains bank/photo-first.
- Manga cover uniqueness engine (separate 4-layer manga scheme; do not merge vocabularies without an explicit bridge).

## 9. Follow-on work

1. ~~Five-layer orchestrator CLI~~ — **CODE-WIRED:** `scripts/publish/five_layer_cover_orchestrator.py` (`render` / `gates` / `roster`).
2. Extend identity houses beyond 13 **or** declare a governed mapping from catalog brand → identity house (no silent synthetic houses as production PASS).
3. Wire L3 series on the KDP identity path or document permanent Waystream-only series ownership.
4. ~~Automate G-* gates~~ — **CODE-WIRED** as `… orchestrator.py gates` (operator script; not yet a required CI check).

## 10. Status summary

| Piece | Layer today |
|---|---|
| This document | SPECCED |
| `render_kdp_cover` + identity treatment/mark/type | CODE-WIRED (13 houses) |
| `bank_image_picker` | CODE-WIRED (upstream of render) |
| 16 compositions `--template` | CODE-WIRED |
| Brand roster proof | EXECUTED-REAL (Jul 17 matrix) |
| Brand+topic+title proof | EXECUTED-REAL (Jul 18 variation sheet) |
| Five-layer orchestrator + G-* runners | CODE-WIRED (`five_layer_cover_orchestrator.py`) |
| Catalog 40×17 five-layer PASS | ABSENT (blocked by gaps in §5) |

## gt30d C06 — Author signature + 37×14 registry unify (2026-07-22)

**Keepers:** I005, I049 · No second cover system.

### Additive requirements

1. **Author signature / blueprint:** each author-facing cover path must resolve an author identity layer (mark, byline treatment, or signature motif) from the cover identity SSOT — not title-only swaps.
2. **37×14 / registry unify:** brand×locale cover naming must remain single-sourced via `docs/NAMING_COVER_SYSTEM_37x14.md` + `config/publishing/cover_identity_system.yaml` (or successor). Agents must not invent a parallel registry.
3. **Delta queue:** prefer durable delta rerender (explicit `--force-rerender`) over blind full-catalog rerenders (see Waystream/export_355 signal).

### Cursor-may-implement (Wave-B unless advanced)

1. Verify orchestrator reads author signature fields; gap report only in Wave-A if missing.
2. Do not claim PROVEN-AT-BAR for catalog-scale uniqueness from this section alone.

### Signal

`gt30d-c06-spec-terminal` when this section lands.

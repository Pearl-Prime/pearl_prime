# qi_foundation vs manga canonical brand registry — reconciliation audit

**Date:** 2026-05-08  
**Agent:** Pearl_Architect  
**Origin:** PR #940 scoping discrepancy **D1**  
**Project routing:** `proj_manga_catalog_reconciliation_20260426` (ACTIVE_PROJECTS.tsv) — governs Phase 2X / 37-brand manga catalog alignment including `canonical_brand_list.yaml`. (There is no separate `PRJ-MANGA-V2` row; manga first-ship is `proj_manga_first_ship_20260425`; canonical list governance rolls up under catalog reconciliation.)

---

## 1. Discrepancy (precise string-level)

Under Path X (`docs/PEARL_ARCHITECT_STATE.md` BR-CANON-01 Path X), **`config/manga/canonical_brand_list.yaml`** is the canonical manga brand registry (`total_brands: 37`).

### Canonical registry (<Path X>)

- **`config/manga/canonical_brand_list.yaml`** defines the qi-related manga brand key as **`qi_foundation_cultivation`** under `brands:` (starts ~line **288**, file header documents 37-Path-X brands and authority chain).

There is **no** YAML map key **`qi_foundation`** under `canonical_brand_list.brands`.

### Consumer: `brand_lora_plans.yaml`

`config/manga/brand_lora_plans.yaml` uses the **non-registry** slug **`qi_foundation`**:

| Location | Evidence |
|---------|----------|
| `brand_suffixes` | **Line ~27**: `qi_foundation: qf` (suffix `qf`) |
| `character_loras.master_feung` | **Lines ~67–73**: `trigger_word: "feung_qf"`, **`style_ref: qi_foundation`** |
| `brand_style_loras` | **Lines ~159–163**: top-level block **`qi_foundation:`**, `trigger_word: "style_qf"` |

**Net:** **`qi_foundation` ∉ `canonical_brand_list.brands` keys** → D1 “absent from canonical list” holds for the **literal** id `qi_foundation`. Semantically the brand **is** represented as **`qi_foundation_cultivation`**.

---

## 2. Adjacent manga config references (`qi_foundation` alias — out of Pearl_Architect WRITE_SCOPE this session)

The same short slug **`qi_foundation`** appears elsewhere under `config/manga/` (for follow-up reconciliation by Pearl_Dev; **not edited in this audit PR**):

| File | Line ref (approx) | Summary |
|------|-------------------|---------|
| `brand_genre_allocation.yaml` | e.g. **74**, **127+** | `brand_tentpole` + locale matrices keyed `qi_foundation` |
| `manga_brand_series_plan.yaml` | **134+** | `qi_foundation:` pacing block (`teacher: master_feung`) |
| `character_brand_registry.yaml` | **200–205** | `qi_foundation:` · **`brand_id: qi_foundation`** (inner field mirrors wrong slug) · `teacher_id: master_feung` |
| `japan_dual_track_config.yaml` | **77** | `- qi_foundation` in `primary_brands` |
| `brand_illustration_styles.yaml` | **83** | Top-level **`qi_foundation:`** styling block (`teacher: master_feung`) |

Series/book plans already use **`brand_id: qi_foundation_cultivation`** extensively under `config/source_of_truth/manga_*_plans/` — evidence that **catalog execution** leaned canonical id while **LoRA/teaching-plane YAML** kept the short alias.

---

## 3. Source-of-truth audit (authority chain)

Per **`config/manga/canonical_brand_list.yaml` header**:

- Strategic input: **`docs/GENRE_PORTFOLIO_PLAN.md`**
- Governing reconciliation spec: **`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`**
- **Canonical registry file:** **`config/manga/canonical_brand_list.yaml`**
- Consumers: e.g. **`config/manga/manga_brand_series_plan.yaml`** (among others).

Per **`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`** (via PR **#682** lineage referenced in canonical list comments) + Path X: **37 manga brands as catalog allocation units** remain the governing count; **`brand_lora_plans.yaml`** is an implementation/training appendix for LoRA (**`specs/AI_MANGA_PIPELINE_SUMMARY.md`** artifact flow + **`docs/MANGA_IMPLEMENTATION_OUTLINE.md`** “config and contracts”) and must reference **canonical manga `brand_id` strings**, not ad hoc aliases.

Pearl Prime book registries (**`config/brand_registry.yaml`**, **`config/brand_management/global_brand_registry.yaml`**) remain a **different axis** (explicitly forbidden to mutate from the manga canonical list comments). No Pearl Prime **`qi_foundation`** row was required to resolve this D1.

---

## 4. Architectural decision (Pearl_Architect cap **QI-FOUNDATION-CANONICAL-RECONCILIATION-01`)

### Direction chosen: **B** (consumer alignment — not Direction A)

- **Rejected — Direction A (“add `qi_foundation` as 38ᵗʰ brand”)**: Would **duplicate** the existing canonical niche **`qi_foundation_cultivation`** (“Somatic (Eastern) · Cultivation · Seinen”; `primary_topic: somatic_healing`), violate the **37-brand Path X reconciliation**, and split one visual/teaching lineage across two ids.

- **Selected — Direction B:** Treat **`qi_foundation`** as a **non-canonical alias**. In the follow-up config PR (**Pearl_Dev**), **`remove/replace`** the **`qi_foundation`** key and **rebind **`master_feung`** to **`qi_foundation_cultivation`**:
  - `brand_suffixes`: key **`qi_foundation_cultivation: qf`** (retain **`qf`**)
  - `character_loras.master_feung.style_ref`: **`qi_foundation_cultivation`**
  - `brand_style_loras`: rename block **`qi_foundation`** → **`qi_foundation_cultivation`** (preserve `trigger_word: "style_qf"` unless a separate naming policy requires otherwise — optional micro-decision inside Pearl_Dev PR)

Trigger tokens **`feung_qf`** / **`style_qf`** can remain unchanged; **`qf`** is only a suffix, not the registry id.

### Extended sweep (Pearl_Dev backlog, not gated on this doc-only PR)

Align **`qi_foundation` → `qi_foundation_cultivation`** across the **`config/manga/*.yaml`** call sites listed in §2 **in the same or sequenced PRs** so `character_brand_registry` **inner `brand_id`** stops contradicting canonical id.

---

## 5. Follow-up actors

| Responsibility | Owner |
|----------------|-------|
| YAML edits (`brand_lora_plans.yaml` minimum; manga alias sweep §2 recommended) | **Pearl_Dev** |
| CI: validate `brand_lora_plans` brand keys/refs ⊆ `canonical_brand_list.brands` (target invariant — **see cap Anti-drift for staged rollout**) | **Pearl_DevOps** (workflow accountability) implementing check authored with **Pearl_Dev** manga-config domain input |
| Naming workstream (suggested handle) | `ws_manga_brand_id_lora_alignment_20260508` (Pearl_Dev; optional sibling `ws_brand_suffix_canonical_ci_20260508` Pearl_DevOps) |

---

## 6. CLOSEOUT linkage

Cap entry appended to **`docs/PEARL_ARCHITECT_STATE.md`** as **QI-FOUNDATION-CANONICAL-RECONCILIATION-01**. Status **`proposed`** until the Pearl_Dev YAML PR merges.

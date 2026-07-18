# Japan Manga-Only Parallel Catalog — V1

**PROJECT_ID:** PRJ-JAPAN-MANGA-ONLY-CATALOG-V1  
**Cap:** `JAPAN-MANGA-ONLY-CATALOG-V1-01` (see `docs/PEARL_ARCHITECT_STATE.md`)  
**Status:** proposed — doc-only baseline; operator/legal confirmation required before execution  
**Date:** 2026-05-10

---

## 1. Purpose

Document the **second Japan catalog** the operator described: **37 Path X brands** (same `brand_id` keys as `config/manga/canonical_brand_list.yaml`) distributed as **manga-only** SKUs through a **separate Japanese legal entity** contracting **Line Manga** (primary) and **other Japanese manga platforms** (TBD). This catalog is **parallel** to the regular worldwide program’s **`ja_JP`** lane (Google Play, Amazon, etc.) — not a replacement.

---

## 2. Scope (binding)

| Dimension | Rule |
|-----------|------|
| Brands | **37** — **identical** `brand_id` set to the regular worldwide manga registry (**no new brand rows** without an architect **AMENDMENT**). |
| Locale | **`ja_JP` only** (planning bucket matches regular Japan locale grammar). |
| Surfaces | **Manga only** — **no** ebook, **no** podcast, **no** video in this program cap. |
| Distribution | **Line Manga** + **other JP manga platforms** (contracting stack owned by the separate JP entity). |
| Narrative / voice / character | **Must match** regular-catalog `character_design` / voice doctrine per brand — drift is a **quality** risk. |
| Legal / finance | **Separate Japanese company**; revenue share and brand-admin posting paths **differ** from regular Phoenix Omega — **operator + counsel** own corporate structure. |

---

## 3. Explicit non-goals

- **No** edits to `canonical_brand_list.yaml` in this lane (37 frozen; this program **consumes** the same IDs).  
- **No** automatic code generation that assumes **one** legal owner for all JP revenue — the parallel entity is real-world operator scope.  
- **No** merge of this doc into the regular worldwide TSV row math without Pearl_Marketing + Pearl_PM reconciliation (see `ws_japan_manga_only_catalog_scoping_20260510`).

---

## 4. Coordination

| Artifact | Role |
|----------|------|
| `artifacts/catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv` | Regular **`ja_JP`** baseline; final `__japan_manga_only_parallel_catalog__` metadata row points here + to this spec. |
| `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` | Worldwide **222 + 37 = 259** cell authority + ebook/manga Phoenix surface definition. |
| PR #801 Line Manga research (repo lineage) | Primary distribution research anchor — refresh under `ws_japan_manga_only_platform_contract_research_20260510`. |

---

## 5. Operator decision card (verbatim)

1. **Q1:** Confirm **37 brand IDs identical** to regular catalog (vs different IDs for legal separation)?  
2. **Q2:** Manga volume per brand for Japan-manga-only — **same** as regular `ja_JP` manga %, **or higher** because the catalog is manga-dedicated?  
3. **Q3:** Brand admin separation — **same wizard** vs **separate Japanese-only wizard**?  
4. **Q4:** Timeline — **Phase 2 alongside V1.1 worldwide expansion**, **or Phase 3** after worldwide V1 ships?

---

## 6. Anti-drift

1. **Manga-only** is a **cap binding** — sneaking ebook/podcast/video into this program requires an **AMENDMENT**.  
2. **Brand IDs** are **shared** with the regular 37 — inventing parallel IDs is drift.  
3. Treat **Line Manga + JP platforms** economics as **separate** from Google Play / Amazon ja_JP regular lane unless operator merges them with explicit authority.

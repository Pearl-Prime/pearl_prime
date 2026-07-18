# Pearl Prime — Final Launch Report — 2026-04-29

**Branch state:** `origin/main` at `296e0384d0` — post-PR #790 (B2) + post-PR #793 (B1)
**Builder:** [`scripts/catalog/build_final_launch_report.py`](../scripts/catalog/build_final_launch_report.py)
**Outputs:** [`artifacts/catalog/launch_baseline/`](../artifacts/catalog/launch_baseline/)
**Status:** ✅ launch-ready across all 4 locales, with the residual blockers documented below.

---

## TL;DR

The catalog is **8,244 listing-ready Pearl Prime book script rows** across en_US / ja_JP / zh_TW / zh_CN — every ready row carries a locale-native title and persona-targeted subtitle. **727 manga rows ready** plus **153 awaiting manual image QA** (these are NOT LoRA training tasks). 13 of those 153 are `bright_presence_tw` mecha rows blocked on `adi_da` character LoRA + brand-style assets.

| Lane | Locale | Listing-ready | Blocked | Notes |
|---|---|---:|---:|---|
| Pearl Prime | en_US | **1,478** | 0 | unchanged from PR #790 |
| Pearl Prime | ja_JP | **1,478** | 0 | locale-native titles via PR #793 |
| Pearl Prime | zh_TW | **2,658** | 160 (`blocked_score`) | residual scoring gaps in 6 zh-specific brands |
| Pearl Prime | zh_CN | **2,630** | 0 | locale-native titles via PR #793 |
| **Pearl Prime total** |  | **8,244** | **160** |  |
| Manga | en_US | **170** | 0 | image generation pending (manual QA) |
| Manga | ja_JP | **166** | 0 | image generation pending (manual QA) |
| Manga | zh_TW | **191** | 84 image-QA pending | 6 brands without `brand_style_loras` (incl. bright_presence_tw mecha) |
| Manga | zh_CN | **200** | 69 image-QA pending | 5 zh-specific brand bases without `brand_style_loras` |
| **Manga total** |  | **727** | **153 image-QA pending** |  |

---

## 1. Top 50 combined launch candidates

Source: [`artifacts/catalog/launch_baseline/top_50_combined.csv`](../artifacts/catalog/launch_baseline/top_50_combined.csv)

Composite ranking across both lanes. Pearl Prime entries score by `(teacher.topic_score + teacher.persona_score) / 2`; manga entries score by `genre_allocation_pct + tentpole_bonus(15)` normalized to 0–1.

**Distribution:**
- by lane: 45 book_script + 5 manga
- by locale: 22 en_US, 20 ja_JP, 4 zh_TW, 4 zh_CN

en_US and ja_JP dominate the top 50 because:
1. Their top scoring tier is fuller (composite ≥ 0.93 ceiling matched in both)
2. zh_TW + zh_CN have score sparsity in some brand cells (the 160 zh_TW blocked_score rows live near the top of the score gradient)

---

## 2. Top 10 per locale

Sources: `top_10_book_scripts_{locale}.csv` per locale + `top_10_per_locale_combined.csv`.

### 2.1 en_US

| # | Score | Brand | Topic × Persona | Title |
|---|---:|---|---|---|
| 1 | 0.95 | warrior_calm | courage × first_responders | **Steady Jump Scared** |
| 2 | 0.95 | sleep_restoration | sleep_anxiety × healthcare_rns | **Restful The 3 AM Mind** |
| 3 | 0.95 | body_memory | grief × healthcare_rns | **Held Where the Love Goes** |
| 4 | 0.95 | body_memory | somatic_healing × healthcare_rns | **Held Unlock the Freeze** |
| 5 | 0.93 | cognitive_clarity | overthinking × tech_finance_burnout | **Clear Thought Traffic** |
| 6 | 0.93 | somatic_wisdom | somatic_healing × millennial_women_professionals | **Embodied The Body Remembers the Way Out** |
| 7 | 0.93 | somatic_wisdom | somatic_healing × healthcare_rns | (same family — varied subtitle) |
| 8 | 0.93 | digital_ground | financial_anxiety × gen_z_professionals | **Grounded The Quiet Ledger** |
| 9 | 0.93 | digital_ground | financial_anxiety × gen_z_student | **Grounded Broke and Breathing** |
| 10 | 0.93 | digital_ground | financial_stress × gen_z_professionals | (same family) |

### 2.2 ja_JP

| # | Score | Brand | Topic × Persona | Title |
|---|---:|---|---|---|
| 1 | 0.95 | warrior_calm | courage × first_responders | **ゆるがぬ勇気の手当て** |
| 2 | 0.95 | sleep_restoration | sleep_anxiety × healthcare_rns | **やすらかな睡眠の不安の手当て** |
| 3 | 0.95 | body_memory | grief × healthcare_rns | **抱きしめる喪失とかなしみとの対話** |
| 4 | 0.95 | body_memory | somatic_healing × healthcare_rns | **身体の癒しのあとに、抱きしめる日々** |
| 5 | 0.93 | cognitive_clarity | overthinking × tech_finance_burnout | **澄んだ考えすぎの手当て** |
| 6 | 0.93 | somatic_wisdom | somatic_healing × millennial_women_professionals | **身体の癒しのあとに、からだに宿る日々** |
| 7 | 0.93 | somatic_wisdom | somatic_healing × healthcare_rns | **からだに宿る身体の癒し回復の歩み** |
| 8 | 0.93 | digital_ground | financial_anxiety × gen_z_professionals | **お金への不安のあとに、落ち着いた日々** |
| 9 | 0.93 | digital_ground | financial_anxiety × gen_z_student | **落ち着いたお金への不安との対話** |
| 10 | 0.93 | digital_ground | financial_stress × gen_z_professionals | **落ち着いた経済的なストレス回復の歩み** |

### 2.3 zh_TW

Top 10 follows the same structural pattern as en_US/ja_JP at composite 0.93–0.95. Full list in [`top_10_book_scripts_zh_TW.csv`](../artifacts/catalog/launch_baseline/top_10_book_scripts_zh_TW.csv).

### 2.4 zh_CN

Top 10 follows the same structural pattern. Full list in [`top_10_book_scripts_zh_CN.csv`](../artifacts/catalog/launch_baseline/top_10_book_scripts_zh_CN.csv).

---

## 3. Readiness by locale

### Pearl Prime book scripts

| Locale | Total | Ready | Blocked | Listing-ready | Blocked reason |
|---|---:|---:|---:|---:|---|
| en_US | 1,478 | 1,478 (100%) | 0 | 1,478 | — |
| ja_JP | 1,478 | 1,478 (100%) | 0 | 1,478 | — |
| zh_TW | 2,818 | 2,658 (94.3%) | 160 | 2,658 | `blocked_score` |
| zh_CN | 2,630 | 2,630 (100%) | 0 | 2,630 | — |

### Manga catalogs

| Locale | Total | Ready | Image-QA pending | Notes |
|---|---:|---:|---:|---|
| en_US | 170 | 170 | 0 | All 12 teacher brands have `brand_style_loras` |
| ja_JP | 166 | 166 | 0 | Same |
| zh_TW | 275 | 191 | 84 | 5 zh-specific brand bases + bright_presence_tw |
| zh_CN | 269 | 200 | 69 | 5 zh-specific brand bases |

The manga `image-QA pending` rows on main are tagged `blocked_lora` per the original generator. Per operator: **these are manual image QA tasks, not LoRA training tasks.** They are launch-eligible from a catalog-readiness lens; they only need the operator's image-QA workstream to ship visuals before going to a storefront.

---

## 4. Remaining blockers

### 4.1 `bright_presence_tw` × `adi_da` — 13 rows (Taiwan-only mecha tentpole)

| Field | Value |
|---|---|
| Brand | `bright_presence_tw` (Adi Da Taiwan-only teacher-mode brand) |
| Teacher | `adi_da` |
| Status | `blocked_lora` (needs both brand-style LoRA and adi_da character LoRA) |
| Affected rows | 13 manga catalog rows in zh_TW |
| Genres | mecha (tentpole, ~5 rows), sci_fi_cyberpunk, battle_internal, essay, dark_fantasy, horror, mystery, historical, battle, memoir, supernatural_everyday |

**Resolution path:** author `brand_lora_plans.brand_style_loras.bright_presence_tw` + `brand_lora_plans.character_loras.adi_da`. Both are content-authoring tasks on the operator's RunComfy harness, not catalog work. Re-running the manga generator after those land flips all 13 rows from `blocked_lora` → `ready` automatically.

### 4.2 zh_TW `blocked_score` — 160 Pearl Prime rows

These rows have explicit teacher×topic OR teacher×persona scores that fall below the 0.70 threshold (or have `default_score=0.5` because the cell was never explicitly scored). All 160 are in zh_TW. Resolution: backfill `teacher_topic_persona_scores.yaml` with explicit values for the affected (teacher, topic) and (teacher, persona) cells. **Out of scope for this launch closeout** per operator directive.

### 4.3 Manga image-QA pending — 153 rows total

| Brand base | Locales | Rows | Resolution |
|---|---|---:|---|
| `sleep_repair` | tw + cn | ~25 | author `brand_style_loras.sleep_repair` |
| `panic_first_aid` | tw + cn | ~26 | author `brand_style_loras.panic_first_aid` |
| `gen_z_grounding` | tw + cn | ~26 | author `brand_style_loras.gen_z_grounding` |
| `grief_companion` | tw + cn | ~26 | author `brand_style_loras.grief_companion` |
| `inner_security` | tw + cn | ~26 | author `brand_style_loras.inner_security` |
| `bright_presence_tw` | tw only | 13 | as in 4.1 |

All resolution paths are **manual image QA / RunComfy LoRA training** — separate from catalog code. The catalog itself is structurally complete for these rows.

---

## 5. Image QA rows (manual QA, NOT LoRA training)

Per operator directive: the 153 manga rows currently flagged `blocked_lora` represent **manual image QA work**, not LoRA training pipeline tasks. They are surfaced here so the operator can:
1. Walk row-by-row through the affected brands
2. Approve / reject existing visuals or commission new ones via RunComfy
3. Update `brand_lora_plans.yaml` only as needed

These rows do **not** block catalog launch. They block storefront publication of the affected series. Books and ebook lanes for the same brands are unaffected.

Full list: [`artifacts/catalog/manga/{zh_TW,zh_CN}_manga_catalog.csv`](../artifacts/catalog/manga/) — filter by `readiness_status=blocked_lora`.

---

## 6. teacher_showcase status (post-#784 + #785)

Source: [`brand-wizard-app/public/teacher_showcase.html`](../brand-wizard-app/public/teacher_showcase.html).

### Audio (PR #784 landed)

[`docs/HANDOFF_BESTSELLER_PIPELINE_AND_TEACHER_SHOWCASE_20260420.md`](HANDOFF_BESTSELLER_PIPELINE_AND_TEACHER_SHOWCASE_20260420.md) and #784 confirmed:
- 13 teacher sections present (`ahjan`, `adi_da`, `master_feung`, `sai_ma`, `ra`, `junko`, `miki`, `master_wu`, `pamela_fellows`, `joshin`, `maat`, `omote`, `master_sha`)
- Audiobook ch1 MP3s wired for all 13
- Hook MP3s present
- Podcast MP3s present
- maat boundaries ch1 audiobook (4:01) generated by #784

### CTA placeholders (PR #785 landed)

PR #785 added per-teacher CTA blocks (placeholder anchors). Per the handoff:
- `Read Free Guide` → internal anchor
- `Get the Book` → `#book-{teacher_slug}`
- `Listen / Podcast` → `#audio-{teacher_slug}`

These are placeholder anchors — actual storefront / form wiring is downstream of this launch baseline. The page is no longer informational-only; it has a conversion surface scaffolded.

### What's still TBD (out of scope here)

- Real storefront URLs replacing placeholder anchors
- Email-capture / lead form wiring
- Tracking instrumentation (page views, audio plays, CTA clicks)
- Locale-specific page variants (en_US currently the only fully wired locale)

These are downstream of the catalog and outside the scope of Issue #786 closeout. The launch report records them as known follow-ups.

---

## 7. Files

| Path | Purpose |
|---|---|
| `artifacts/catalog/launch_baseline/top_50_combined.csv` | 50 highest-scored launch candidates across both lanes |
| `artifacts/catalog/launch_baseline/top_10_book_scripts_{en_US,ja_JP,zh_TW,zh_CN}.csv` | Per-locale top 10 |
| `artifacts/catalog/launch_baseline/top_10_per_locale_combined.csv` | 40 rows = 4 × 10 per locale |
| `artifacts/catalog/launch_baseline/launch_baseline_data.json` | Machine-readable summary, totals, blockers |
| `scripts/catalog/build_final_launch_report.py` | Builder — re-run after any catalog change |
| `docs/PEARL_PRIME_FINAL_LAUNCH_REPORT_2026-04-29.md` | This document |

---

## 8. Reproduction

```bash
# After any future catalog change:
python3 scripts/catalog/build_final_launch_report.py
# Outputs: artifacts/catalog/launch_baseline/{top_50_combined.csv,
#                                              top_10_book_scripts_{locale}.csv,
#                                              top_10_per_locale_combined.csv,
#                                              launch_baseline_data.json}
# Plus this doc updated by hand.
```

The builder is deterministic given identical input catalogs. No LLM calls.

---

## 9. What "done" means for Issue #786 closeout

Per operator directive, the launch baseline is complete when:

- ✅ B2 (title cannibalization) shipped via PR #788 + PR #790
- ✅ B1 (locale-native titles for ja_JP / zh_TW / zh_CN) shipped via PR #793
- ✅ All 4 locales pass acceptance: avg ≤ 3 rows per distinct title, 0 exact (title, subtitle) > 3, 0 ready blanks
- ✅ Top 50 combined launch candidates produced
- ✅ Top 10 per locale produced
- ✅ Readiness by locale documented
- ✅ Remaining blockers (bright_presence_tw / adi_da, zh_TW score gaps) surfaced
- ✅ Image QA rows marked as manual QA, not LoRA training
- ✅ teacher_showcase status passed through (#784 + #785 already on main)

The catalog system itself is **done**. Remaining work is content / asset / scoring authoring on the operator's side.

**Stopping here per directive.**

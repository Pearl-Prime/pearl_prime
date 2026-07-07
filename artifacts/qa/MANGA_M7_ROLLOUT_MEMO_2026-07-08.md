# M7 Locale Rollout Gap Memo — 2026-07-08

**Branch audited:** `agent/manga-m6-blind10-protocol-20260708` (68886ec692, 54659ee598)
**M7 layer claim:** **PARTIAL** — allocation chain closed (M2); Wave A tooling + fr_FR routing landed; grid not green.

---

## 1. Live repo truth (verified this session)

| Check | Status | Evidence |
|---|---|---|
| `locale_genre_allocations.yaml` | **ACTIVE — 14 locales** | `config/manga/locale_genre_allocations.yaml` |
| Generator consumes allocations | **YES** (2X.4) | `generate_catalog_plan_from_strategic.py --dry-run` → 37×14 allocation-derived |
| Series plan coverage | **5/14 locales have plans** | en_US 268, ja_JP 269, zh_TW 274, zh_CN 268, ko_KR 266; **9 zero-plan** |
| `format_routing.yaml` Wave A locales | **fr_FR only** (this session) | 8 others still missing routing blocks |
| `run_m7_wave_a.py` | **CODE-WIRED** | allocation-derived emit; fr_FR dry-run 390 plans OK |
| Schema v2.4.0 wave locales | **LANDED** | `es_US/es_ES/zh_SG` locale enum; `locale_origin` fr/de/it/hu/es/br/sg/hk |

### Plan coverage grid

| Locale | Plans | Allocation | Format routing | Wave A ready |
|---|---:|---|---|---|
| en_US | 268 | ✓ | ✓ | shipped (M3 wave 1) |
| ja_JP | 269 | ✓ | ✓ | shipped |
| zh_TW | 274 | ✓ | ✓ | shipped |
| zh_CN | 268 | ✓ | ✓ | shipped (gray-zone) |
| ko_KR | 266 | ✓ | ✓ | **hold** (Q-MANGA-05) |
| **fr_FR** | **0** | ✓ | **✓ (new)** | **READY — next Wave A PR** |
| pt_BR | 0 | ✓ | ✗ | blocked on routing |
| de_DE | 0 | ✓ | ✗ | blocked on routing |
| es_ES | 0 | ✓ | ✗ | blocked on routing |
| es_US | 0 | ✓ | ✗ | blocked on routing |
| it_IT | 0 | ✓ | ✗ | blocked on routing |
| hu_HU | 0 | ✓ | ✗ | blocked on routing |
| zh_SG | 0 | ✓ | ✗ | blocked on routing |
| zh_HK | 0 | ✓ | ✗ | blocked on routing + CJK deferral |

---

## 2. Research gap status (M2 commissioning items)

| Locale | Roadmap gap (Jul-03) | Current truth |
|---|---|---|
| **it_IT** | zero research | **CLOSED in allocation** — disaggregated EU ebook-forward mix; confidence mostly `medium` (`locale_genre_allocations.yaml` §it_IT) |
| **zh_SG** | zero | **CLOSED in allocation** — `asian-persona` §4/§9 citations; confidence `high` on primary genres |
| **hu_HU** | upgrade needed | **PARTIAL** — allocation authored (M2 §hu_HU); audit low-confidence market size still applies; not a Wave A blocker for *plans* |
| **zh_HK** | deferred per CJK §2 | **PARTIAL** — allocation authored (§zh_HK, genre-led); CJK catalog HK addendum still defers *strategic divergence*; Wave A plans possible, Wave B needs CJK lane |

---

## 3. Generator consumption gaps closed this session

1. **`generate_series_plans_from_catalog.py`** — `VALID_LOCALES` + locale heading regex: added `es_US`, `es_ES`, `zh_SG`; retired `es_LA` placeholder.
2. **`generate_catalog_plan_from_strategic.py`** — `VALID_LOCALES` aligned to 14-registry set (matches allocation keys).
3. **`run_m7_wave_a.py`** — new Wave A vehicle: allocation-derived counts (70% locale × 30% brand), `manga_locales` brand filter, schema validation.
4. **`format_routing.yaml`** — `fr_FR` block (BD-heavy bw_page_manga for dark_fantasy/historical/psych-horror/mecha).
5. **`series_plan.schema.json` v2.4.0** — wave locale enum + `locale_origin` extensions.

**Remaining consumption gap:** `run_2x4_atomic_regen.py` still uses global brand %-table only (not allocation-derived). Use `run_m7_wave_a.py` for Wave A locales until 2X.4 regen is allocation-aware.

---

## 4. Recommended Wave A order (from current truth)

1. **fr_FR** — #1 EU manga market; `fr_bd_manga` lane; format routing + emitter proven (390 plans, 0 schema failures). Split into ≤180-file PR batches (3 PRs).
2. **pt_BR** — ratified OPD-20260704-005; strong LATAM manga culture; copy `fr_FR`/`en_US` routing template next.
3. **de_DE** — ebook-forward EU peer; western_intent_led picture-book shape.
4. **es_ES** — EU Spanish; research complete in allocation.
5. **es_US** — US Hispanic; shares western_intent_led lane with en_US.
6. **it_IT** — allocation closed; medium-confidence research acceptable for plan-only Wave A.
7. **hu_HU** — allocation closed; smallest EU manga slice (15% default).
8. **zh_SG** — allocation closed; bilingual EN/zh intent-led.
9. **zh_HK** — last in Wave A; genre-led CJK; operator should confirm HK platform routing before emit.

**Not in Wave A:** ko_KR (ship-gated), ja_JP manga-only 37-cell (Q-MANGA-07).

---

## 5. Operator next steps (fr_FR first PR)

```bash
# Preflight
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR --dry-run

# Batch 1 of 3 (≤180 files per PR doctrine)
PYTHONPATH=. python3 scripts/manga/run_m7_wave_a.py --locale fr_FR \\
  --max-files 180 \\
  --out-root config/source_of_truth/manga_series_plans

# After all batches merged: regenerate fr_FR catalog CSV (2X.5) + conformance TSV re-run
```

Proof sample (5 plans): `artifacts/qa/manga_m7_wave_a_fr_FR_proof/series_plans/fr_FR/`

---

## 6. Machine summary

```
manga-m7-status=PARTIAL
manga-m7-locales-with-plans=5
manga-m7-zero-plan-locales=9
manga-m7-wave-a-ready=fr_FR
manga-m7-fr-fr-derived-count=390
manga-m7-grid-green=NO
manga-m7-wave-a-order=fr_FR,pt_BR,de_DE,es_ES,es_US,it_IT,hu_HU,zh_SG,zh_HK
manga-m7-blockers=format_routing_missing_8_locales;ko_KR_hold;wave_b_blocked_on_m3;wave_c_blocked_on_m5
```

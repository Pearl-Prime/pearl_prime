# Duration Planner Rollout — Operator Decision Memo

**Date:** 2026-07-07  
**Owner:** Pearl_Architect (decision memo; no planner code changes)  
**Authority:** `artifacts/research/DURATION_BOOK_FORMAT_ARCHAEOLOGY_2026-07-07.md`, OPD-20260613-001  
**Question:** Should mass-catalog planning stay on 60–70 minute bands, or roll out the full T1–T7 ladder as default planner behavior?

---

## 1. Current truth

| Layer | Status |
|-------|--------|
| **Doctrine** | Settled — `DURATION-DERIVATION-01`, `docs/DURATION_DERIVATION_SPEC.md` |
| **Implementation** | Landed — derived minutes in `format_registry.yaml`, `duration_derivation.py`, CI guards |
| **Plan-reference reality** | **176,595** `runtime_format_id` references; **only** `standard_book_60min` (122,083) and `one_hour_book` (54,512). Counts YAML plan-file rows (incl. nested `duration:` fields), not storefront shipments. |
| **Ladder occupancy** | Registry SSOT defines T1–T7 + compact + atom-native formats; **planner defaults do not use the ladder** except the two 60–70m bands above. |
| **Flagship proof** | One **special cell** — `extended_book_2h` ~21,012w PROVEN-AT-BAR (gen_z×anxiety per `PROGRAM_STATE.md`). Proves pipeline can reach ~T5–T6 length for one intentional build. **Not** proof the catalog inhabits the ladder or that T7 (52k) is mass-catalog reality. |
| **Render reality** | Bulk thin ~5k words; gold depth-fill ~21.5k; no confirmed mass-catalog 52k renders. |

---

## 2. Registry truth vs planner behavior

**Registry truth (what formats *mean*):**
- Honest 7-tier ladder (OPD-20260613-001): T1 Quick Reset (~25m) → T7 Complete (~347m / 52k words).
- Plus `standard_book_60min` (70m / 10.5k) and atom-native modular formats.
- All fully-specced formats carry derived `audiobook_minutes` / `ebook_minutes`.

**Planner behavior (what auto-plans *emit*):**
- Mass wave book/series plans default to **`standard_book_60min`** or **`one_hour_book`** only.
- Ladder formats (`standard_book`, `deep_book_6h`, compacts) are available in registry but **absent from plan references**.
- No planner surface today maps persona/topic/brand → ladder tier intentionally.

**Gap:** Registry says we have a 7-tier product line; planner says we ship one ~60–70 minute SKU shape at scale.

---

## 3. Rollout options

### Option A — Keep 60–70m as mass default; ladder = registry truth only

Mass auto-plan continues `standard_book_60min` / `one_hour_book`. Ladder formats used only when an operator or product lane explicitly selects them (flagship, podcast-season source, Complete tier writing program).

### Option B — Staged expansion (adjacent tiers first)

Keep 60–70m as bulk default. Add **intentional** planner routes for:
- Compact T1–T3 for short-read / podcast-episode SKUs.
- `standard_book` (T5) for gold / $-maker depth-fill builds.
- `deep_book_6h` (T7) only for commissioned flagship Complete cells.

Do **not** flip entire catalog to ladder until writing program proves render length at each new tier.

### Option C — Full ladder rollout into planner defaults

Replace mass defaults with tier-aware planner logic (persona × platform × brand → T1–T7). Would immediately create plan references for compacts, standard, deep formats across the catalog.

---

## 4. Tradeoffs

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| **Product integrity** | High — honest labels match what we actually plan to render | High — new tiers only where intentional | **Low** — plan references would claim T5/T7 without mass render proof |
| **Catalog variety** | Low — one duration band dominates | Medium — variety on demand | High on paper |
| **QA risk** | Lowest — current known band | Medium — each new tier needs smoke matrix | **High** — 176k+ plans change shape at once |
| **Writing-program readiness** | Decoupled — ladder grows via explicit builds | Aligned — tiers added as content proves length | **Misaligned** — planner outruns content depth |
| **Flagship / gold-path alignment** | Gold path manual (`standard_book` / `extended_book_2h`) | Gold path becomes explicit planner route | Ladder labels on plans that still render thin |

---

## 5. Recommendation — **Option B (staged expansion)**

**Keep `standard_book_60min` and `one_hour_book` as the mass-catalog planning default.** Do not pretend full ladder occupancy exists. Route special products into adjacent tiers **intentionally**:

| Product lane | Planner `runtime_format_id` | When |
|--------------|----------------------------|------|
| Mass catalog (current) | `standard_book_60min`, `one_hour_book` | Default; no change |
| Short-read / podcast episode / lead magnet | `compact_book_*` (T1–T3) | New SKU lanes only |
| Gold / $-maker depth-fill | `standard_book` (T5, 147m) | Explicit production builds |
| Proven flagship cell | `extended_book_2h` | Curated cells (existing proof) |
| Complete / Audible flagship | `deep_book_6h` (T7, 52k) | Writing-program commissioned cells only |

**Rationale:** Plan-reference counts prove the catalog is optimized for a 60–70 minute planning band. The ladder is correct **registry and marketing truth**, but bulk renders are still thin (~5k) or gold (~21.5k). Flipping planner defaults to T5/T7 (Option C) would create hundreds of thousands of dishonest plan references overnight. Option A is safe but leaves ladder formats permanently orphaned. Option B matches OPD-20260613-001 honesty spine: **books grow into the ladder; the planner does not jump ahead of the writing program.**

---

## 6. Next workstreams (if Option B accepted)

1. **`ws_planner_tier_routing_spec`** (Pearl_Architect) — Document explicit mapping table (brand/lane → `runtime_format_id`); no mass default change.
2. **`ws_compact_sku_pilot_plans`** (Pearl_PM) — Generate a bounded pilot set of book plans on `compact_book_8ch_30min` / `compact_book_5ch_15min` for short-read funnel SKUs; measure render length.
3. **`ws_gold_path_planner_route`** (Pearl_Dev) — Wire `--runtime-format standard_book` (or plan-level override) for production gold builds without changing mass auto-plan defaults.
4. **`ws_catalog_t7_writing_program`** (Pearl_Prime) — Commission `deep_book_6h` cells; prove 52k renders before any planner scale-up to T7.
5. **`ws_platform_routing_reconcile`** (Pearl_Research) — Fix `platform_knob_tuning.yaml` stale 55-min routing (separate from planner; still required).

---

## Operator questions still open

1. **Is `standard_book_60min` a permanent mass SKU** or a interim bridge until `standard_book` (T5) renders reliably at ~22k? (Affects whether Option B is terminal or Phase 1 of a longer migration.)
2. **Compact GTM deprecation of micro runtimes** (OQ-DFU-02) — approve redirect before compact pilot plans ship?
3. **CJK per-locale durations** — remain deferred; do not inherit en-US planner bands for ja/zh/ko storefronts.

---

## Closeout

**Memo path:** `artifacts/coordination/DURATION_PLANNER_ROLLOUT_DECISION_MEMO_2026-07-07.md`  
**Recommendation:** **Option B — staged expansion; preserve 60–70m mass default.**  
**No `10_day_challenge` format introduced.** Closest challenge ID: `weekly_challenge_pack` (7-day).

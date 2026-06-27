# Manga Market-Integration & Reuse Model — V1 Spec

**Status:** PROPOSED (design + plan only — no manga build, no generator edits)
**Author:** Pearl_Architect + Pearl_Dev (Claude Code, Tier-1)
**Date:** 2026-06-27
**Decision of record:** `OPD-20260627-001` (2026-06-27) — manga two-tier ratification, logged in `artifacts/coordination/operator_decisions_log.tsv` line 153.
**Layer:** This spec is the **manga slice** of the worldwide allocation model. It governs *how many manga units each normal market catalog carries, and which existing Path X manga story is reused into which platform/market*. It does **not** author new manga.

---

## 0. Read order / authority inputs

This spec **consumes** completed work. It cites, it does not re-derive.

| Input | Role here |
|---|---|
| `OPD-20260627-001` | Manga two-tier ratification: nonexclusive (Canvas/Tapas/GlobalComix) = DEFAULT cross-post; exclusive originals (Webtoon/Kakao/LINE/Lezhin) = per-series opt-in, never baseline; Japan manga-only 37-cell = unique/isolated, never reused. |
| `config/catalog/catalog_generation_config.yaml` :: `lane_content_mix` | **Operative SSOT** for per-market manga share (manga_series + manga_standalone + micro_manga). Cites `global_manga_distribution_strategy.md §6.1`. |
| `config/manga/canonical_brand_list.yaml` | 37 Path X manga brands (frozen; this spec consumes IDs, never edits). |
| `config/source_of_truth/manga_series_plans/` | **1,361** existing Path X manga series plans across 5 locales (en_US 272 / ja_JP 273 / ko_KR 270 / zh_CN 272 / zh_TW 274). Each plan already carries `target_platforms`, `connector_lane`, `distribution_status`. **This is the reuse pool.** |
| `image_bank/index.json` | Indexed manga visual assets (see §A.4 for the honest count + scope note). |
| `config/distribution/platform_families.DRAFT.yaml` | Family membership + `cross_references`/`translated_dupe_allowed`/`isolated` flags. **DRAFT** (untracked sibling artifact); this spec consumes its H-confidence manga rows as settled per the ratification. |
| `docs/specs/WORLDWIDE_ALLOCATION_MODEL_V1_SPEC.md` | Parent allocation model (§2.5 manga two-tier; §6 Japan 37-cell; §9b manga production driver). This spec **fills in** that model's manga slice. |
| `docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md` | The Japan manga-only 37-cell parallel catalog (isolated track — §B). |
| `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` | Cell-math authority: **222 + 37 = 259** (222 regular = 37 × 3 locales × {ebook,manga}; 37 = Japan manga-only). |
| `config/catalog/market_catalog_registry.yaml` | 14-market registry. Its per-market `content_mix` is a **stale planning artifact** — do NOT cite for format %. The registry's own header (lines 14–15) flags the gap this spec reconciles in §C. |
| `pearl_news/pipeline/atom_usage_tracker.py` | The architectural model for the manga reuse-tracker (§A.5). |

**Tier policy (CLAUDE.md mandatory):** no paid LLM. Western manga script/adaptation review = Tier-1 Claude Code. CJK6 manga text = Tier-2 Qwen on Pearl Star. This spec is design-only; no LLM runs here.

---

## A) MARKET-INTEGRATED MANGA PLAN

### A.1 Per-market manga slice (from `lane_content_mix`, the operative SSOT)

The **manga slice** of a market = the sum of its three manga families in `lane_content_mix`:
`manga_slice(market) = manga_series + manga_standalone + micro_manga`.

This is a **share of that market's catalog**, not an absolute unit count (absolute counts derive from each market's catalog denominator, which is brand × topic × persona × format and is owned by the catalog plan, not this spec). The slice is the **routing weight** that says *what fraction of a market's catalog is manga, sourced by reuse*.

| Market | Locale | manga_series | manga_standalone | micro_manga | **manga slice** | Source line in `lane_content_mix` |
|---|---|---:|---:|---:|---:|---|
| Japan | ja_JP | 40% | 20% | 10% | **70%** | L83–89 |
| Korea | ko_KR | 35% | 15% | 10% | **60%** | L92–98 |
| Taiwan | zh_TW | 30% | 15% | 10% | **55%** | L101–107 |
| France | fr_FR | 15% | 10% | 5% | **30%** | L119–125 |
| Brazil | pt_BR | 13% | 8% | 5% | **26%** | L146–152 |
| United States | en_US | 10% | 5% | 5% | **20%** | L110–116 |
| Spain | es_ES | 10% | 5% | 5% | **20%** | L128–134 |
| Germany | de_DE | 10% | 5% | 5% | **20%** | L137–143 |
| China | zh_CN | 0% | 0% | 0% | **0%** | L155–161 (SKIP — no manga; ebook-only) |
| HK / SG / LATAM / Italy / Hungary | zh_HK, zh_SG, es_US, it_IT, hu_HU | 5% | 5% | 5% | **15%** | `_default` L165–171 |

These shares reproduce the ground numbers in the operator brief exactly (Japan ~70, Korea ~60 webtoon, Taiwan ~55, France ~30, US ~20, Brazil ~26, China 0). The `_default` (15%) covers the five markets with no explicit `lane_content_mix` key.

**Slice → family routing.** Within each market's manga slice, the three families route as:
- `manga_series` + `micro_manga` → **vertical-scroll / serialized** surfaces (`manga_nonexclusive`: Webtoon Canvas, Tapas, GlobalComix by default).
- `manga_standalone` → **page-format / tankōbon** surfaces (KDP comics, BookWalker; GlobalComix accepts both formats).

### A.2 Sourced by REUSE — the 1,361-plan pool

The manga slice is filled by **reusing the 1,361 existing Path X manga series plans**, not by authoring new stories. The pool today:

| Locale | Plans | Brands covered | Today's `target_platforms` in the plans |
|---|---:|---:|---|
| en_US | 272 | 37 | `webtoon_canvas` (272), `amazon_kdp_comics` (270), `globalcomix` (270) — **nonexclusive default ✓**; 2 plans leak `line_manga_indies` (drift — see A.3) |
| ja_JP | 273 | 37 | `line_manga_indies` (273), `bookwalker` (273), `comic_cmoa`/`amazon_kdp_comics` (88) |
| ko_KR | 270 | 37 | none — `connector_lane: hold_pending_market_clearance` (all on hold) |
| zh_TW | 274 | 37 | `webtoon_canvas` (274), `line_manga_indies` (274), `bookwalker` (274) — **has a manga line ✓** (contradicts the registry — §C) |
| zh_CN | 272 | 37 | `bilibili_comics`/`kuaikan_manhua`/`tencent_comics` (270), `amazon_kdp_comics` (270) — `gray_zone_with_disclosure` (isolated_cn) |

The plans already carry the distribution substrate (`target_platforms`, `connector_lane`, `distribution_status`). **The reuse model reads and reconciles these against the ratified two-tier family map; it does not re-author the stories.**

### A.3 Reuse vs net-new — quantified

**Localize-don't-regenerate (parent §1) applies to manga.** A market manga edition is a `(canonical_series, locale)` reuse of an existing Path X plan, fanned out across the platforms that serve that market's locale. The net-new *story* count for the worldwide manga slice is therefore **near-zero**; what grows is **listings** (one plan → N platform rows) and **production** (script + art per surface, which is adaptation cost, not a new narrative).

| Driver | Net-new **stories** | Notes |
|---|---:|---|
| **Reuse of 1,361 existing plans across western nonexclusive families** (Canvas/Tapas/GlobalComix cross-post) | **0** | Each plan fans out to all 3 nonexclusive platforms simultaneously (R6: cross-post is the default). The same `canonical_series` also localizes across the western markets that take manga (US/FR/ES/DE/BR via Canvas; +`_default` 15%). |
| **Reuse into isolated CN manga family** (Bilibili/Kuaikan/Tencent) | **0** | zh_CN plans already target these; isolated family = whole-catalog, no dedup. Gated on D4 (CN entity). |
| **Reuse into Taiwan / Korea regional manga surfaces** | **0** | zh_TW plans already carry Canvas + BookWalker; ko_KR plans exist but are on hold (`hold_pending_market_clearance`). |
| **Per-market manga *production*** (script+art per surface for the slice) | **0 new stories** | Adaptation/production cost only — same canonical narrative, new surface. Parent §9b driver #2: `manga_production = Σ_market editions(market) × manga_share(market)`. |
| **Exclusive-originals opt-in** (per-series, never baseline) | **0** | A series committed to `manga_exclusive_originals` is *withdrawn from reuse* for the exclusivity term (R6), not newly authored. |
| **Japan manga-only 37-cell track** (§B) | **37** | The **only** genuinely net-new manga *story* block. Authored for Japan, isolated, never reused. |

**Headline:** the entire normal-market manga slice is **reuse of the 1,361-plan pool + image_bank assets = 0 net-new stories**. The only net-new manga authoring worldwide is the **37 Japan-unique cells** (§B). Manga *production* (art) for the reused slices is real cost but not new narrative.

**Drift to correct (not in this spec's scope to fix — flag for the plan-reconciliation lane):**
- en_US: 2 plans carry `line_manga_indies` (an exclusive-originals platform) in a nonexclusive-default lane. Per R6, `line_manga_indies` must be **opt-in per series**, not present by default. → reconciliation flag **MM-1**.
- ja_JP: all 273 regular-lane plans carry `line_manga_indies` as the primary `target_platforms`. This conflates the **regular ja_JP manga lane** with the **Japan manga-only 37-cell partnership track** (§B). The regular ja_JP lane should route nonexclusive-default + KDP/BookWalker; LINE Manga belongs to the isolated 37-cell partnership track. → reconciliation flag **MM-2**.

### A.4 image_bank reuse — honest count + scope

`image_bank/index.json` indexes **840 assets** (layer split: environment 420 / character 210 / symbolic 210) for **one brand** (`stillness_press`) across 15 topics. This is a **per-brand reference/proof bank** — the gold-master visual layer for one brand — **not** the worldwide ~5,700-asset corpus referenced in the program brief. The discrepancy is a **counter-scope** issue: the index today reflects the proven first brand; the full corpus populates as the other 36 brands render.

**Reuse rule for assets:** the reuse-tracker keys assets by `(brand, topic, layer_type, visual_intent, composition_compat)` so the **same** rendered asset can back multiple platform editions of the same canonical series **without re-render**. Cross-platform reuse of a single asset is free (assets are not platform-specific); the tracker prevents *re-rendering* the same cell, not *re-listing* it.

→ reconciliation flag **MM-3**: confirm whether the worldwide ~5,700 figure is the target corpus (840 indexed today = ~15% populated, one brand) or whether a second asset manifest exists. Do not invent the 5,700 number into any config.

### A.5 Manga reuse-tracker — design (none exists today)

**Confirmed:** no manga reuse-tracker exists in the repo (grep for `manga.*reuse.*track` / `manga_reuse` returns nothing). Design it on the proven model: `pearl_news/pipeline/atom_usage_tracker.py` (least-recently-used selector with a persisted JSON ring-buffer log).

**Name (design):** `scripts/manga/manga_reuse_tracker.py`
**Log (design):** `artifacts/manga/manga_reuse_log.json`
**Purpose:** track which canonical manga series + which image_bank assets have been fanned out to which `(family, market, locale, platform)` cells, so that (1) reuse is maximized, (2) the same asset is never re-rendered, and (3) the same `(canonical_series, locale)` is never duplicated within a `cross_references: true` family (the same-language-within-family uniqueness rule, parent §7).

**Cell key (parallel to atom_usage_tracker's `teacher|topic|slot`):**
```
manga cell key = canonical_series_id | locale | family_id
```

**Two log dimensions (the tracker carries both — atom_usage_tracker carries one):**

1. **Allocation log** (`series_id|locale|family_id → [platform_ids fanned out]`) — records every reuse of a canonical series into a family/platform. Used by the anti-spam gate (parent §8.1) to enforce: at most one `(series_id, locale)` per `cross_references: true` family; whole-catalog allowed on `isolated: true` families (parent §8.2).

2. **Asset-render log** (`brand|topic|layer_type → [rendered asset_ids]`, LRU ring) — direct analogue of atom_usage_tracker. Records which image_bank assets are already rendered so the same cell is never re-rendered; selects least-recently-used asset for variety across editions (the same operator directive that drove atom_usage_tracker: "vary the use… fewest repeats").

**Selector behavior (mirrors `pick_least_recently_used`):**
- Prefer never-used assets (cold-start) for visual variety; tie-break by stable-index hash for determinism (same algorithm as `_stable_index`).
- Ring window per cell (default 4, same as `RECENT_WINDOW`).
- Thread-safe file lock + sorted-key JSON for stable diffs (same as `_save_log`).

**API surface (design — mirrors the existing module):**
```python
def record_allocation(series_id, locale, family_id, platform_id, log_path=None) -> None
def pick_least_recently_rendered(assets, *, brand, topic, layer_type, series_id, log_path=None, record=True, recent_window=4) -> dict
def get_allocation(series_id, locale, family_id, log_path=None) -> list[str]   # platforms already fanned out
def is_duplicate(series_id, locale, family_id, log_path=None) -> bool          # same-language-within-family guard
def reset_log(log_path=None) -> None
```

**Wiring (design — no code shipped here):** the tracker feeds `check_worldwide_allocation_spam.py` (parent §8). It is read by the manga fan-out step (when built) and updated after each allocation/render. **No paid LLM** — pure deterministic Python, like atom_usage_tracker.

**Anti-drift:** the tracker is a **router/ledger**, not a generator. It never authors a series and never renders an asset; it records what was reused and refuses duplicates. This keeps "reuse the 1,361 plans" structurally enforced, not aspirational.

---

## B) JAPAN MANGA-ONLY BOUNDARY (unique / isolated — never reused)

**Boundary rule (normative, R7 of the parent model):**

> The Japan manga-only 37-cell track is **authored for Japan, is manga-surface-only, routes through `isolated_jp` (LINE Manga partnership stack via a separate Japanese legal entity), and is NEVER reuse-eligible into any other family, market, surface, or locale.** Its 37 stories are net-new (counted once, in A.3) and do **not** enter the 1,361-plan reuse pool. No canonical series from the reuse pool may be routed *into* the 37-cell track either; the boundary is two-way.

**Mapping to the manifest (parent §5 / §6):**

| Property | Value |
|---|---|
| Cells | **37** (37 × ja_JP × manga) — `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`: 259 = 222 + **37**. |
| Brand IDs | **identical** to `canonical_brand_list.yaml` (37 frozen IDs shared with regular catalog; no parallel IDs — that would be drift per `JAPAN_MANGA_ONLY_CATALOG_V1_SPEC §6`). |
| Family | `isolated_jp` (manga surface). LINE Manga = partner-only, no open indie portal. |
| Legal/finance | **Separate Japanese legal entity** — revenue/admin paths differ from regular Phoenix Omega (operator + counsel scope). |
| `engine` (manifest) | `manga_jp`. |
| `status` (manifest) | `exclusive_committed` or `blocked_open_flag` (flag **B10** — LINE Manga indie portal ETA / JP partner). |
| Reuse-eligibility | **NONE.** Two-way isolation: not reused out, nothing reused in. |

**Why isolated, not just "exclusive":** the regular ja_JP manga lane (Google Play, Amazon JP, BookWalker, Canvas) is a *reuse* lane — it localizes pool stories into Japanese and cross-posts nonexclusively. The 37-cell track is a **parallel, legally-separate, manga-dedicated catalog** contracted through LINE Manga + JP platforms. Conflating them is exactly drift **MM-2** (A.3): the 273 ja_JP pool plans currently put `line_manga_indies` on every regular-lane plan, blurring the boundary. The regular ja_JP reuse lane and the isolated 37-cell partnership track must be **manifest-separated**: regular ja_JP → reuse pool + nonexclusive default; 37-cell → `isolated_jp`, `engine: manga_jp`, never in the pool.

**Boundary enforcement (design):** the reuse-tracker's allocation log MUST refuse any `record_allocation` where `family_id == isolated_jp_manga_only` carries a `series_id` that also appears in the reuse pool, and vice-versa. The anti-spam gate (parent §8.3) FAILs on any cross-membership. The Japan 37-cell `series_id` namespace is disjoint from the 1,361-pool `series_id` namespace (enforced by a manifest-level prefix, e.g. `jp37__<brand>`).

---

## C) REGISTRY DISCREPANCY FLAGS (operator — do NOT invent numbers)

`config/catalog/market_catalog_registry.yaml` is **internally inconsistent** with `lane_content_mix` (the operative manga-share SSOT) for two manga markets. The registry's own header (lines 14–15) already admits this. **These are flagged for the operator; this spec does not invent corrected numbers.**

| # | Market | Registry says | `lane_content_mix` says | The 1,361 plans say | Flag |
|---|---|---|---|---|---|
| **C-1** | **Taiwan** (zh_TW) | `business_tracks: [ebook, audiobook]` — **NO manga/webtoon track**; `content_mix: ebook 70` (no manga line) | manga slice = **55%** (30+15+10) | **274 zh_TW manga plans exist**, targeting Canvas + LINE + BookWalker | Registry **omits** Taiwan's manga track despite a 55% slice and 274 ready plans. **Operator must add a manga track + content_mix manga line to the Taiwan registry entry.** |
| **C-2** | **France** (fr_FR) | `business_tracks: [ebook, audiobook]` — **NO manga track**; `content_mix: ebook 65` (no manga line) | manga slice = **30%** (15+10+5) | No fr_FR plans in the pool yet (pool is 5 locales: en/ja/ko/zh_CN/zh_TW) | Registry **omits** France's manga track despite a 30% slice. France is the #1 EU manga market (35% share). **Operator must add a manga track to the France registry entry**; manga editions sourced by **localizing en_US pool plans into fr_FR** (reuse, 0 net-new stories). |

**Secondary registry-vs-SSOT drift (already noted in the registry header, restated for completeness, no action requested here):**
- Japan registry `content_mix: manga 60` vs `lane_content_mix` **70** vs research 40 — three-way divergence; `lane_content_mix` is operative.
- Korea registry `content_mix: webtoon 30` vs `lane_content_mix` manga slice **60**.
- US registry `content_mix: manga 10` vs `lane_content_mix` **20**.

**Recommendation (operator decision card):**
1. Confirm `lane_content_mix` is the single manga-share SSOT and the registry `content_mix` block is **deprecated/derived** (the header already says "do NOT cite this content_mix for format %").
2. Add `manga` to `business_tracks` for **Taiwan** and **France** (C-1, C-2).
3. Pick the Taiwan/France manga platform stack (Canvas default; BookWalker TW for Taiwan; Canvas FR + KDP FR for France).

Until C-1/C-2 are operator-resolved, the manga fan-out for Taiwan and France is **held** (`status: blocked_open_flag`, flag `registry_no_manga_track`) — the planned slice is preserved, but not shipped.

---

## D) SMALL FIX — topic-fit path correction (same PR)

`docs/specs/WORLDWIDE_ALLOCATION_MODEL_V1_SPEC.md` referenced the topic-fit config at `config/catalog/market_topic_fit.yaml`. The file actually landed at **`config/catalog_planning/market_topic_fit.yaml`** (confirmed present on disk + origin/main, 42,610 bytes — where Prompt 3 wrote it). The three stale references (§R8 L142, §9b L238, §12 L302) are corrected in the same PR. See the companion edit to that spec.

---

## E) What this spec does NOT do

- **No manga build.** No series authored, no art rendered, no manifest populated. Design + plan only.
- **No generator edits.** `lane_content_mix`, `canonical_brand_list.yaml`, the 1,361 plans, and the registry are **not** modified by this PR (the C-1/C-2 registry fixes are **operator-gated**, not auto-applied).
- **No paid LLM.** The reuse-tracker is deterministic Python; CJK manga text (when built) is Tier-2 Qwen.
- **No ratification of residuals.** B10 (LINE portal), D4 (CN entity), MM-1/MM-2/MM-3 (plan/asset drift) remain open flags.
- **No reuse-tracker code.** §A.5 is a design; the implementation is a follow-on Pearl_Dev workstream gated on the anti-spam gate (parent §8).

---

## F) Downstream / dependencies

- **Gates on:** operator resolution of C-1/C-2 (Taiwan/France registry manga tracks) before those markets' manga slices ship.
- **Feeds:** the worldwide allocation manifest (parent §5) — each manga slice becomes `manga_nonexclusive` / `isolated_*` / `isolated_jp` allocation rows; the reuse-tracker (§A.5) is the ledger behind those rows.
- **Reconciliation lane (separate workstream):** fix plan-level drift MM-1 (en_US LINE leak), MM-2 (ja_JP regular-vs-37-cell conflation), MM-3 (image_bank corpus scope).
- **Build prerequisite:** the anti-spam gate `check_worldwide_allocation_spam.py` (parent §8) + the reuse-tracker (§A.5) must exist before any manga fan-out automation runs.

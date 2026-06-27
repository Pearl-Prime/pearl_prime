# Worldwide Allocation Model — V1 Spec

**Status:** RATIFIED (model A1–A3 + manga two-tier), open residuals flagged
**Author:** Pearl_Architect (Claude Code, Tier-1)
**Date:** 2026-06-27
**Decision of record:** `OPD-20260627-001` (2026-06-27) — logged in `artifacts/coordination/operator_decisions_log.tsv`
**Supersedes (this dimension only):** the "every piece of content can go on 5–6 platforms simultaneously with **zero exclusivity conflicts**" claim in `docs/DISTRIBUTION_STRATEGY.md` §1/§3. That claim was a per-asset upload statement; it is replaced by the **platform-family same-language uniqueness rule** below, which governs *which canonical story may appear in which family/market/locale*. KDP-Select-never-enroll (§10) and "Japan via partner" (§11) remain valid.
**Supersedes (uniqueness dimension):** the locale-only scope of `config/uniqueness_policy.yaml` — see §7 + the anti-spam gate design (§8).

---

## 0. Read order / authority inputs

This spec **builds on** completed research. It does not redo it. Cite, do not re-derive.

| Input | Role here |
|---|---|
| `config/distribution/platform_families.DRAFT.yaml` | Family membership + per-platform `cross_references` / `translated_dupe_allowed` / `isolated` flags. **DRAFT** until L/M items ratified; this spec consumes its H-confidence rows as settled. |
| `artifacts/research/platform_family_spam_model_research_20260627.md` | Source of every family rule. "Family Groupings" §1–13 + "Per-Platform Findings Table". |
| `artifacts/research/platform_family_ratification_sheet_20260627.md` | Ratification ledger. Sections A (model), B/C (M/L platforms), D (operational). |
| `config/catalog/market_catalog_registry.yaml` | 14 markets, brand rosters, per-market `platform_strategy`. (Its `content_mix` is a **stale planning artifact** — do not cite for format %.) |
| `config/catalog/catalog_generation_config.yaml` :: `lane_content_mix` | **Operative** per-market format mix (manga vs ebook). Cites `global_manga_distribution_strategy.md §6.1`. |
| `config/uniqueness_policy.yaml` | Today's uniqueness gate — **locale-isolated only**; superseded by §7/§8 below. |
| `docs/DISTRIBUTION_STRATEGY.md` | Per-asset upload mechanics; KDP Select / ACX / Japan-partner rules. |

Adjacent worldwide specs (this model is a **new layer**, not a replacement):
- `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` — the 259-cell (222 + 37 JP manga-only) **brand×locale×surface** grid for the 37 Path X manga brands.
- `docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md` — the Japan manga-only parallel catalog (isolated track, §6 below).
- `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md` — allocation logic for the manga brand surface.

This spec governs the **distribution/spam dimension** (which story → which family/market/locale, and whether that is allowed). Those specs govern **what gets authored** (brand×surface cells). They compose: a cell from the catalog plan becomes one or more manifest rows (§5) here.

---

## 1. The core principle: LOCALIZE, don't regenerate

> **Worldwide coverage = LOCALIZE the canonical en_US story corpus into topic-fit-approved languages per market. It is NOT regeneration of unique stories per territory.**

The canonical en_US corpus is **32,401 stories** (operator-supplied canonical count, `OPD-20260627-001`; = the buildable en_US `brand × topic × persona × format` configs, the "$-makers" high-confidence tier per `artifacts/research/full_content_audit.md`). Each canonical story is the **single source-of-truth narrative**. A market edition is a **translation + locale overlay** of that canonical story, **not** a new story.

This is licensed by the ratified spam model: translated editions are not duplicates within the western cross-referencing families (A1, §2). So the unit of worldwide scale is the **edition** (canonical_id × locale), not the **story**.

**Consequence (volume):** worldwide expansion is overwhelmingly a *listing/translation* operation with **zero net-new stories**. Net-new authoring is required only where a market has a **topic-fit gap** (a canonical en_US topic that does not fit a market) and where the **manga slice** + the **Japan-unique 37-cell track** demand original work (§9).

---

## 2. The ratified family map

Family flags are read from `platform_families.DRAFT.yaml`. Each ratified decision below cites `OPD-20260627-001` §A and the research §.

### 2.1 Western cross-referencing families — translations are SAFE (A1 — RATIFIED)

| Family | Members | cross_references | translated_dupe_allowed | Rule |
|---|---|---|---|---|
| `amazon_ecosystem` | Amazon KDP (all storefronts, 1 account) | true | **true** | Same-language same-content twice = duplicate flag. Translations = separate ASINs, **permitted**. |
| `apple_ecosystem` | Apple Books (iTunes Connect, 1 account) | true | **true** | Exact same-language dup removed; "many similar versions" → block. Translations = separate manuscripts, **permitted**. |
| `google_ecosystem` | Google Play Books (Partner Center, 1 account) | true | **true** | **Strictest** same-language/same-ISBN dedup. Translations = distinct content, **permitted**. |
| `kobo_ecosystem` | Rakuten Kobo / KWL (1 account) | true | **true** | Duplicate ISBNs declined. Translations **explicitly encouraged** as market expansion. |

**A1 (RATIFIED, `OPD-20260627-001`):** translated editions are **NOT spam** on western families. Research §"Key Corrections" + ratification §A1. The spam unit is **same-language same-content**, not cross-language (§7).

**Implication:** a single canonical story may be listed as `en_US`, `de_DE`, `fr_FR`, `ja_JP`, … on the *same* `amazon_ecosystem` account with **no duplicate risk**, because each is a distinct-language edition.

### 2.2 Audible / ACX (A2 — RATIFIED)

| Family | Members | Rule |
|---|---|---|
| `audible_acx` | Audible / ACX (9 territories, 1 account) | **Always non-exclusive** (30% royalty). KDP-Select-style lock-in via ACX Exclusive is **permanently OFF**. Translations = separate ACX titles. |

**A2 (RATIFIED, `OPD-20260627-001`):** ACX always non-exclusive; **KDP Select permanently OFF**. Research §"Audible/ACX" + ratification §A2/§D2/§D3. When non-exclusive, `audible_acx` behaves like a western cross-ref family (no cross-platform constraint). The pipeline must **hardcode** non-exclusive ACX and **block** KDP Select enrollment.

### 2.3 Spotify (A3 — RATIFIED)

| Family | Members | Rule |
|---|---|---|
| `spotify_ecosystem` | Spotify (audiobook + podcast) | **Non-exclusive.** Spam detection is **behavioral** (mass-upload pattern, metadata manipulation), not content-identity. **Behavioral risk accepted** → **rate-limit automated uploads** (§8.4). |

**A3 (RATIFIED, `OPD-20260627-001`):** Spotify non-exclusive, behavioral-risk accepted, rate-limit automated uploads. Research §"Spotify" + ratification §A3. No cross-family content-dedup risk; the only control is **upload cadence**.

### 2.4 Isolated families — whole-catalog, never shared (RATIFIED structure)

| Family | Members | isolated | Rule |
|---|---|---|---|
| `isolated_cn` | Ximalaya, WeChat Read, Dedao, NetEase, Dangdang, JD, Duokan | true | China walled garden. Zero awareness of any other family. Ximalaya **barred from exclusive deals** (SAMR, A4). |
| `isolated_tw` | Readmoo | true | Taiwan regional. **B4 OPEN** (Readmoo→GP/AB dedup, §3). |
| `isolated_kr` | RIDI, Yes24, Millie, Naver, Kakao Page (non-original) | true | Korea regional. **B5/B6/B7 OPEN**. |
| `isolated_jp` | audiobook.jp, booth.pm, LINE Manga (partner-only) | true | Japan regional. |
| `isolated_eu` | Storytel, Thalia, Fnac | true | EU regional. L-confidence (C6/C7). |

**Isolated-platform = whole-catalog rule (§4):** because an isolated family has **zero cross-platform awareness**, the *entire* locale-appropriate catalog can be placed there **without any inter-family dedup concern**. Isolation removes the cross-reference constraint entirely; the only limits are **market topic-fit** (§9) and **per-platform onboarding** (CN entity, etc., §D4 OPEN).

### 2.5 Manga two-tier (RATIFIED)

**Manga (RATIFIED, `OPD-20260627-001`):** two-tier.

| Tier | Family | Members | Default | Reuse rule |
|---|---|---|---|---|
| Non-exclusive (DEFAULT) | `manga_nonexclusive` | WEBTOON Canvas, Tapas, GlobalComix | **DEFAULT** — cross-post freely | A manga series may appear on **all three simultaneously**. Creator retains rights. |
| Exclusive originals (opt-in) | `manga_exclusive_originals` | WEBTOON Originals, Kakao Originals, LINE Manga, Lezhin | **Unique per-series opt-in only** | A series committed here is **removed from reuse** for the exclusivity scope/term. Opt-in per series, never the default. |
| Japan manga-only 37-cell | `isolated_jp` (manga surface) | JP manga platforms via JP legal entity | **Unique / isolated** | The Japan-unique 37-cell track (`JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md`) is authored for Japan and **never reused** elsewhere (§6). |

Research §11/§12, ratification §D5 + B8/B9/B10. The non-exclusive tier is the default fan-out target; exclusive originals are a deliberate per-series trade (advance + reach for a multi-year lockout), tracked as `status: exclusive_committed` in the manifest.

---

## 3. Residual open flags (do NOT block Phase-1 western fan-out)

These are unresolved in the ratification sheet. The model is **ratified without them** for western Phase-1; they gate later phases.

| Flag | Question | Gates |
|---|---|---|
| **B4** | Readmoo distributes to Google Play + Apple Books. If we *also* upload the same zh_TW ISBN directly to GP/AB, does it duplicate-flag? | zh_TW direct-vs-Readmoo routing. Until resolved: **zh_TW → Readmoo OR direct, not both** (default: Readmoo-only). |
| **D1** | INaudio vs Spotify-for-Authors — both paths create a duplicate Spotify listing. | Spotify audiobook routing. Until resolved: **one Spotify path only** (manifest must not emit two `spotify_ecosystem` rows for one canonical_id/locale). |
| **D4** | CN entity / partner for `isolated_cn` onboarding. | All `isolated_cn` rows. zh_CN deferred until partner selected. |
| **B5** | RIDI exclusivity for new foreign-publisher submissions. | `isolated_kr` RIDI rows. |
| **B6** | Kakao Page non-original indie submission tier exists? | `isolated_kr` Kakao rows. |
| **B7** | Millie foreign-publisher submission path. | `isolated_kr` Millie rows. |
| **B8** | Lezhin 2025/26 creator submission exclusivity terms. | `manga_exclusive_originals` Lezhin opt-ins. |
| **B9** | Kakao Originals exclusivity scope/duration. | `manga_exclusive_originals` Kakao opt-ins. |
| **B10** | LINE Manga indie portal ETA / JP partner. | `isolated_jp` + `manga_exclusive_originals` LINE rows. |

The manifest (§5) carries `status: blocked_open_flag` with a `flag` field for any row whose family is gated by an unresolved residual, so the gate (§8) can hold them out of go-live without losing the planned allocation.

---

## 4. Allocation rules (normative)

**R1 — Localize, don't regenerate (§1).** A market edition is `(canonical_id, locale)`. No new `canonical_id` is minted for a translation.

**R2 — Same-language-within-family uniqueness (§7).** Within one `cross_references: true` family, **at most one** edition per `(canonical_id, locale)` — i.e. no same-language same-content duplicate. Different locales of the same `canonical_id` in the same family are **allowed** (A1).

**R3 — Isolated = whole-catalog.** For `isolated: true` families, place the full locale-appropriate, topic-fit-approved catalog. No inter-family dedup applies. (§2.4)

**R4 — ACX/KDP-Select hard rules.** ACX always non-exclusive; KDP Select never enrolled. Enforced in upload automation, not just policy. (A2)

**R5 — Spotify cadence.** Emit at most one `spotify_ecosystem` row per `(canonical_id, locale)`; throttle automated uploads. (A3, D1)

**R6 — Manga default = non-exclusive cross-post; exclusive = opt-in lock.** A series with any `manga_exclusive_originals` commitment is withheld from `manga_nonexclusive` reuse for the exclusivity term. (§2.5)

**R7 — Japan manga-only 37-cell is isolated & unique.** Never reused into any other family/market. (§6)

**R8 — Topic-fit gate precedes localization.** A canonical story is localized into a market only if its topic passes that market's topic-fit (`market_topic_fit.yaml`, §9 — **TBD, Prompt 3**). Topic-fit gaps are the **only** driver of net-new western authoring.

---

## 5. Allocation manifest (schema reference)

Full schema + example: `artifacts/distribution/story_platform_allocation.schema.json` and `artifacts/distribution/story_platform_allocation.example.json`. Production manifest target: `artifacts/distribution/story_platform_allocation.json` (**NOT populated by this spec** — schema + example only).

Shape:

```
{canonical_id, brand, topic, persona, engine}
  -> allocations: [ {family_id, market, locale, status, flag?, exclusivity?} ]
```

- `canonical_id` = **locale-stable book_id** (identical across every locale edition of the story; the localization key).
- One manifest record per canonical story; the `allocations` array fans out across families/markets/locales.
- `status` ∈ `planned | localized | uploaded | live | exclusive_committed | blocked_open_flag | suppressed_dup`.
- `suppressed_dup` is what the gate (§8) sets when R2 would be violated.

---

## 6. Isolated-platform = whole-catalog rule (detail) + Japan 37-cell

**Whole-catalog rule.** An isolated family sees nothing outside itself, so there is no duplicate risk from also listing the same canonical stories on a western family. The full topic-fit-approved locale catalog is placed on each isolated family **independently**. The only constraints are onboarding (D4 for CN) and topic-fit (§9).

**Japan manga-only 37-cell track (unique / isolated).** Per `JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md` + `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` (37 × ja_JP × manga, separate JP legal entity + LINE Manga / JP manga platform stack):
- These 37 cells are **authored for Japan**, are **manga surface only**, route through `isolated_jp`, and are **never reused** into any other family, market, or surface.
- They are **net-new** content (counted in §9b), not localizations of en_US stories.
- They carry `engine: manga_jp` and `status: exclusive_committed` or `blocked_open_flag` (B10/LINE) as applicable.

---

## 7. Same-language-within-family uniqueness rule (supersedes locale-only policy)

Today `config/uniqueness_policy.yaml` is **catalog/locale-isolated** (`catalog_isolated: true`, `cross_catalog_similarity: forbidden`). That model predates the family map and cannot express **same-language-across-markets-within-one-account** duplication — the *actual* spam vector on western families.

**New rule (normative):**

> Within a single `cross_references: true` family, a `(canonical_id, locale)` edition may appear **at most once**. Two editions that share **both** family **and** locale (= same publisher account + same language + same content) are a **duplicate** → spam → **block**.
> Different locales of the same `canonical_id` within a family are **distinct editions** → **allowed** (A1).
> Across **isolated** families, no uniqueness constraint applies (each is its own world).

This is a **family×locale** key, not the old **catalog** key. It supersedes `uniqueness_policy.yaml`'s scope for the distribution dimension; the existing within-catalog authoring checks (duplicate book_id, topic/persona pair, title slug) remain valid for **authoring**.

---

## 8. Anti-spam CI gate (design only — no code)

**Name:** `check_worldwide_allocation_spam.py` (design). **Input:** `artifacts/distribution/story_platform_allocation.json`. **Wiring:** PR governance + a pre-upload gate; BLOCKS on violation.

### 8.1 Same-language-within-family uniqueness (primary check)
- Build the key `(family_id, locale, content_hash)` over all allocation rows where the family is `cross_references: true` (read from `platform_families.DRAFT.yaml`).
- **FAIL** if any key has >1 row with **distinct** `canonical_id`+same content, or any `(family_id, locale, canonical_id)` appears twice (same-content re-list). Different `locale` for the same `canonical_id` in the same family → **PASS** (A1).
- This is the rule that **supersedes** `uniqueness_policy.yaml`'s locale-only scope (note it explicitly in the gate output).

### 8.2 Isolated-family pass-through
- Rows whose family is `isolated: true` are **exempt** from the cross-family uniqueness check (R3) — they may carry the whole catalog.

### 8.3 Exclusivity-conflict check (manga + ACX/KDP)
- **FAIL** if a `canonical_id`/series has both a `manga_exclusive_originals` (`exclusivity_committed`) row **and** a `manga_nonexclusive` row active within the exclusivity term (R6).
- **FAIL** if any row sets ACX exclusive or KDP Select enrollment (R4) — hard, no exceptions.

### 8.4 Spotify cadence / single-path check
- **FAIL** if >1 `spotify_ecosystem` row exists for one `(canonical_id, locale)` (D1 single-path, R5).
- **WARN** (advisory) on automated-upload batch size exceeding the Spotify rate-limit budget (A3 behavioral-risk control).

### 8.5 Open-flag hold
- Rows with `status: blocked_open_flag` are **held** (not shipped) but do not fail the gate — they are planned allocation awaiting a residual (§3) resolution.

**Supersession note (must appear in gate output):** "This gate enforces same-language-within-family uniqueness per `WORLDWIDE_ALLOCATION_MODEL_V1_SPEC §7` and **supersedes** the locale-only scope of `config/uniqueness_policy.yaml` for the distribution dimension."

---

## 9. Volume table (corrected model)

**Notation.** `S` = canonical en_US stories = **32,401** (`OPD-20260627-001`). `L` = target localization locales. Markets/families from `market_catalog_registry.yaml`; western families that take translations = {amazon, apple, google, kobo, audible(non-excl), spotify}.

### 9a. Localization-only coverage — ZERO net-new stories
Every western/isolated market edition is a **translation** of an existing canonical story (R1). **Net-new stories = 0.** What grows is **listings (editions)**.

Localization locales (13 non-en_US market locales from the registry, excl. en_US source): `ja_JP, ko_KR, de_DE, fr_FR, zh_TW, zh_CN, zh_HK, es_US, es_ES, it_IT, zh_SG, hu_HU, pt_BR`.

**Editions (= translation jobs), before topic-fit filtering:**

```
editions_total = S × (1 + L_fit)            # +1 = the en_US source edition itself
              ≈ 32,401 × (1 + 13)  = 453,614   (UPPER BOUND, all topics fit all markets)
```

The **realistic** edition count is lower because not every topic fits every market (§9b, R8): replace `13` with `Σ_market topic_fit_fraction(market)`. **Net-new stories for this entire block = 0.**

**Listings (= per-family upload rows)** further multiply each edition across the families that serve its locale (e.g. an `en_US` story → amazon+apple+google+kobo+audible+spotify = up to 6 western listings). Listings are an **upload-row** count, not a content count, and carry **zero** authoring cost.

### 9b. Net-new authoring — REQUIRED only for these three drivers

1. **Topic-fit gaps (TBD — Prompt 3 dependency).** `config/catalog/market_topic_fit.yaml` **does not yet exist** (confirmed absent 2026-06-27). When it lands, net-new authoring for a market = stories needed to cover market-relevant topics that have **no** canonical en_US equivalent.

   **Formula (fill when `market_topic_fit.yaml` lands):**
   ```
   net_new_topic_fit = Σ_market  ( brands(market) × personas × formats
                                   × topics_market_only(market) )
   where topics_market_only(market) = topics relevant to market
                                      AND absent from the 17 canonical en_US topics.
   ```
   Until the file exists: **TBD**. Expectation per the localize-don't-regenerate principle: **small** relative to S (most therapeutic topics are universal; the 17 canonical topics already cover the core).

2. **Manga % slice (per `lane_content_mix`).** Manga editions of canonical stories are **adaptations** (script + art), counted as net-new *production* even when the narrative is a localization. Per-market manga share from `catalog_generation_config.yaml::lane_content_mix` (operative SSOT): e.g. `ja_JP` manga = 0.40+0.20+0.10 = **0.70**; `ko_KR` ≈ 0.60; `zh_TW` ≈ 0.55; `en_US` ≈ 0.20; `fr_FR` ≈ 0.30; `_default` ≈ 0.15.
   ```
   manga_production = Σ_market  editions(market) × manga_share(market)
   ```
   (Production cost, not net-new *stories* — same canonical narrative, new surface.)

3. **Japan-unique 37-cell track (§6).** **37** net-new manga cells (37 × ja_JP × manga), authored for Japan, never reused. Per `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` cell math (259 = 222 + **37**). This is the **only** genuinely net-new *story* block in the worldwide plan.

   **Net-new stories (worldwide, the corrected model):**
   ```
   net_new_stories = net_new_topic_fit (TBD, small)  +  37 (Japan manga-only)
   ```

### 9c. Contrast vs the naive ~421k

The naive worldwide estimate (~**421k**) treats every `market × brand × topic × persona × format` cell as a **unique story to author**. Under the corrected model, that entire surface is **localization of S=32,401**, not authoring.

| Model | Net-new **stories** authored | What the big number actually is |
|---|---|---|
| **Naive** | ~**421,000** | Mistakes *editions/listings* for *stories*. |
| **Corrected (this spec)** | ≈ **37 + topic_fit_gap (TBD, small)** | The ~421k collapses to ~**454k editions** (translations, 0 net-new stories) + a thin net-new authoring layer (manga production + 37 JP cells + topic-fit gaps). |

**Headline:** worldwide coverage is a **localization + upload** problem (≈454k editions / up-to-millions of listing-rows, all from S), **not** a ~421k-story authoring problem. Net-new *story* authoring ≈ **37 + (topic-fit TBD)**.

---

## 10. Localization wave plan

Sequence **Western-first** (Tier-1, attended, higher-revenue, fewest open flags), then CJK6 (Tier-2, gated on the translation lane).

| Wave | Locales | Translation tier | Families | Gating |
|---|---|---|---|---|
| **W1 — Western primary** | de_DE, fr_FR | **Tier-1 (Claude Code, attended)** | amazon, apple, google, kobo, audible(non-excl), spotify | A1/A2/A3 ratified. Clear of CN flags. **Start here.** |
| **W2 — Western secondary** | es_ES, es_US, it_IT, pt_BR, hu_HU | **Tier-1** | same western set + `isolated_eu` (Storytel/Thalia/Fnac, C6/C7 advisory) | D1 (Spotify path) resolved. |
| **W3 — CJK6 Traditional** | zh_TW, zh_HK, zh_SG | **Tier-2 (Qwen/Pearl Star)**, gated on translation lane | western set + `isolated_tw` (Readmoo) | **B4** (Readmoo dedup) → Readmoo-only default. CJK6 lane per LLM Tier Policy. |
| **W4 — CJK6 Korea + Japan** | ko_KR, ja_JP | **Tier-2 (Qwen)** | western set + `isolated_kr`, `isolated_jp` + manga tiers | **B5/B6/B7/B10**; manga two-tier (§2.5); Japan 37-cell (§6). |
| **W5 — China** | zh_CN | **Tier-2 (Qwen)** | `isolated_cn` only (whole-catalog) | **D4** (CN entity) — hard blocker, deferred until partner selected. |

**Tier policy (CLAUDE.md mandatory):** Western prose/translation review = **Tier-1 Claude Code** (operator-present). CJK6 (zh/ja/ko) translation = **Tier-2 Qwen on Pearl Star via Ollama**, scheduled/unattended, **gated on the translation lane** (`translate_atoms_to_locale.py` — note the >8000-char truncation bug, `project_localizer_truncation_bug`, must be fixed before CJK6 waves run at scale). No paid LLM at any tier (enforced by `llm-policy-enforcement.yml`).

---

## 11. What this spec does NOT do

- **No catalog generation.** Schema + example only; the production manifest is unpopulated.
- **No paid LLM.** Tier-1/Tier-2 only.
- **No ratification of L/M residuals** (§3) — those remain operator items in the ratification sheet.
- **No edit to `uniqueness_policy.yaml`** — §7 supersedes it for the distribution dimension; the config change is a follow-on PR once the gate (§8) is built.

---

## 12. Downstream

This GATES **Prompt 5** (go-live execution). Prompt 3 must deliver `config/catalog/market_topic_fit.yaml` to close the §9b net-new TBD. The anti-spam gate (§8) must be built before any worldwide upload automation runs.

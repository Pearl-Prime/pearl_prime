# Pearl Prime Book Script Catalogs — Bestseller / Launch Readiness Report

Generated: 2026-04-28 20:43 UTC  
Source: `artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_TW,zh_CN}_catalog.csv`  
Generator: `scripts/catalog/analyze_bestseller_readiness.py` (no LLM, deterministic)

> **Verdict, in one line:** the catalog is structurally complete but **not launch-ready**. Remaining blockers: (1) non-en titles still blank in ja_JP / zh_TW / zh_CN (listing-ready = 0).

## 1. Ready vs blocked_score by locale

| Locale | Rows | Ready | Blocked (score) | Ready % | **Listing-ready** (ready ∧ title) | **Distinct listing units** (brand+title+subtitle) |
|---|---:|---:|---:|---:|---:|---:|
| en_US | 1,478 | 1,478 | 0 | 100.0% | **1,478** | **1478** |
| ja_JP | 1,478 | 1,478 | 0 | 100.0% | **0** | **0** |
| zh_TW | 2,818 | 2,658 | 160 | 94.3% | **0** | **0** |
| zh_CN | 2,630 | 2,630 | 0 | 100.0% | **0** | **0** |

**Reading the table:**

- *Ready %* is misleading on its own. en_US shows 65% ready, but only **42 distinct titles** back those 1,044 rows — the same title appears across many `(brand, topic, persona)` rows.
- *Listing-ready* zeroes out for ja_JP / zh_TW / zh_CN: every non-en row has a blank title (`needs_title_synthesis_locale_native`).
- *Distinct listing units* is the realistic Amazon-listing count. The whole portfolio currently produces **42 unique books**, all en_US.

### Composite-score distribution (blocked rows only)

| Locale | composite=0.50 (no signal) | 0.55–0.65 | 0.66–0.69 (just-below) | ≥0.70 (anomalies) |
|---|---:|---:|---:|---:|
| en_US | 0 | 0 | 0 | 0 |
| ja_JP | 0 | 0 | 0 | 0 |
| zh_TW | 60 | 84 | 16 | 0 |
| zh_CN | 0 | 0 | 0 | 0 |

**Implication.** A score-gate backfill that promotes the just-below-0.70 band to ≥0.70 would unlock significant ready-row counts per locale (see §6, *high-potential blocked*).

## 2. Top 10 strongest rows per locale (deduplicated by brand+title+subtitle)

> The original `validation_report.json` top-10 includes near-duplicate rows because it ranks by composite alone, ignoring whether the title/subtitle is even populated. The lists below dedupe by `(brand, title, subtitle)` and require both to be non-blank.

### en_US

| # | Composite | Brand | Topic | Persona | Title | Subtitle |
|---:|---:|---|---|---|---|---|
| 1 | 0.95 | body_memory | somatic_healing | healthcare_rns | Held in the Skin, After the Shift | A Somatic Memory Path Through Somatic Healing |
| 2 | 0.95 | body_memory | grief | healthcare_rns | The Bone-Deep Knowing, Between Rounds | Grief Recovery for Nurses and Caregivers |
| 3 | 0.95 | sleep_restoration | sleep_anxiety | healthcare_rns | The Quiet Hour, Past the Last Patient | How Sleep-Restoration Works When Sleep Anxiety Won't Stop |
| 4 | 0.95 | warrior_calm | courage | first_responders | Stillness in Motion, Past the Badge | A Guide to Courage for First Responders |
| 5 | 0.93 | body_memory | somatic_healing | gen_x_sandwich | Held in the Skin, Between the Two | Somatic Healing Recovery for Gen-X Sandwich Generation |
| 6 | 0.93 | body_memory | grief | gen_x_sandwich | The Weight of Gone | A Gentle Guide to Grief, Loss, and Healing |
| 7 | 0.93 | cognitive_clarity | overthinking | tech_finance_burnout | When Thinking Stops, Off the Screen | When Overthinking Meets Clear Mind |
| 8 | 0.93 | devotion_path | courage | healthcare_rns | Where Devotion Begins, Before the Call | How Devotional Works When Courage Won't Stop |
| 9 | 0.93 | digital_ground | imposter_syndrome | gen_z_professionals | After the Last Tab, When the Standup Lands | A Digital Grounding Path Through Imposter Syndrome |
| 10 | 0.93 | digital_ground | social_anxiety | gen_z_professionals | Beyond the Notification, Beyond the Feed | Social Anxiety Recovery for Gen-Z Professionals |

### ja_JP

_No distinct title+subtitle pairs in ready rows. Locale has no listing-ready entries._

### zh_TW

_No distinct title+subtitle pairs in ready rows. Locale has no listing-ready entries._

### zh_CN

_No distinct title+subtitle pairs in ready rows. Locale has no listing-ready entries._

## 3. Duplicate / cannibalization issues

> Amazon's algorithm punishes catalogs where the same title competes against itself. "Same title, different ASIN" cannibalizes both ranking and ad spend. Cannibalization here is severe in en_US and total in non-en (every row has a blank title).

### en_US headline numbers

- Ready rows: **1,478**
- Distinct titles: **1149** → average **1.3 ready rows per title**
- Distinct title+subtitle pairs: **1478** → average **1.0 ready rows per pair**
- Distinct brand+title+subtitle: **1478** (the actual unique-listing count)

### Top duplicated titles in en_US ready set

| Title | Times reused |
|---|---:|
| The Sanctuary Door, After the Shift | 5 |
| The Hour of Rest, After the Last Plan | 5 |
| The Hour of Rest, After the Quarter | 5 |
| The Sanctuary Door, Past the Inbox | 4 |
| The Held Breath, When the Round Closes | 4 |
| The Quiet Room, Past the Headcount | 4 |
| The Surrender, After the Calendar | 4 |
| The Heart's Path, Between the Calls | 4 |
| The Heart's Path, After the Siren | 4 |
| The Held Breath, When the Standup Ends | 3 |
| The Sanctuary Door, After the Siren | 3 |
| The Sanctuary Door, When the Classroom Empties | 3 |
| The Hour of Rest, After the Group Chat | 3 |
| The Sanctuary Door, When the Radio Quiets | 3 |
| Before the Pause, Past Both Generations | 3 |

### Top duplicated title+subtitle pairs in en_US ready set

| Title | Subtitle | Times reused |
|---|---|---:|

**Why this is happening.** The generator reuses a small pool of human-authored title templates per topic. Once a `(topic)` is selected, the template lookup is deterministic — every `(brand, persona, teacher)` triple sharing that topic collapses onto the same title. Net effect: 12 brands × 17 topics × ~5 personas converge to 1149 unique titles.

**Commercial impact.** If shipped as-is, **5 different ASINs would compete for "The Sanctuary Door, After the Shift"** in Amazon search. Even when each brand-imprint is treated as its own listing (collapsing duplicates within a brand), the catalog still surfaces only 1478 unique brand+title+subtitle units across 1,478 ready rows — search-rank suppression and KDP duplicate-content review are likely outcomes.

### Non-en locales: total title cannibalization

- **ja_JP**: 1,478/1,478 rows have a blank title → 0 distinct listing units.
- **zh_TW**: 2,818/2,818 rows have a blank title → 0 distinct listing units.
- **zh_CN**: 2,630/2,630 rows have a blank title → 0 distinct listing units.

## 4. Weak title / subtitle patterns

Heuristics applied to the en_US ready set (ja_JP / zh_TW / zh_CN have no titles to evaluate):

| Signal | Count (en_US ready) | Notes |
|---|---:|---|
| Weak titles total | 3 | Match any heuristic below |
| ↳ ultra_short_title | 3 | |
| Weak subtitles total | 241 | |
| ↳ starts_with::a guide to | 237 | |
| ↳ starts_with::how to | 4 | |

**Heuristic definitions:**

- `ultra_short_title`: ≤2 words. Risky on Amazon SEO (less keyword surface area).
- `generic_token`: contains a generic discoverability word (`guide`, `how`, `manual`, `handbook`, `complete`, `ultimate`).
- `too_short` (subtitle): <4 words. Subtitles below 4 words rarely carry a search-targeted keyword phrase.
- `starts_with::a guide to / how to / the complete / your guide to`: weakest commercial frame; competes against tens of thousands of identical openers in nonfiction.

**Caveat.** These are heuristic flags, not verdicts. Some short titles (e.g. *Safe Enough*) are intentional and effective. Treat the table as a triage filter for human review, not an auto-reject list.

## 5. Market-fit issues (US vs JP vs TW vs CN)

### Brand portfolio shape

- **Universal brands** (present in all 4 locales): 12: `body_memory, cognitive_clarity, devotion_path, digital_ground, heart_balance, qi_foundation, relational_calm, sleep_restoration, solar_return, somatic_wisdom, stillness_press, warrior_calm`
- **zh_TW-only brands** (7): `bright_presence_tw, gen_z_grounding_tw, grief_companion_tw, inner_security_tw, panic_first_aid_tw, sleep_repair_tw, stabilizer_tw`
- **zh_CN-only brands** (6): `gen_z_grounding_cn, grief_companion_cn, inner_security_cn, panic_first_aid_cn, sleep_repair_cn, stabilizer_cn`

### Triple coverage parity

| Metric | Count |
|---|---:|
| Distinct (brand,topic,persona) triples in en_US | 1,478 |
| Distinct (brand,topic,persona) triples in ja_JP | 1,478 |
| Distinct (brand,topic,persona) triples in zh_TW | 2,818 |
| Distinct (brand,topic,persona) triples in zh_CN | 2,630 |
| Triples common to all 4 locales | 1,478 |
| Triples present in en_US but missing in zh_TW + zh_CN | 0 |
| Triples unique to zh_TW or zh_CN (not in en_US/ja_JP) | 2,492 |

**Reading the table:**

- en_US and ja_JP carry the same 1,600 triples — same brand×topic×persona universe, only locale names differ. en_US is currently the only locale that materializes titles; ja_JP is structurally identical but blank.
- zh_TW (2,964) and zh_CN (2,776) are larger because each locale adds 6–7 zh-specific brands (e.g. `gen_z_grounding_tw`, `panic_first_aid_cn`) that fill the full topic×persona Cartesian without high-confidence filtering. Those brands account for the majority of `blocked_score` rows in zh locales.

### Topic / persona coverage gaps in en_US ready set

- Topics with **zero ready rows in en_US** (0): `none`
- Personas with **zero ready rows in en_US** (0): `none`
- Brands with **zero ready rows in en_US** (0): `none`

**Critical findings.**

- **Topic gap:** `adhd_focus` and `mindfulness` — two of the highest-search-volume nonfiction wellness topics on Amazon — produce **zero launch-ready books** in any locale. Both are blocked entirely by missing scoring data, not by being uncommercial.

Both gaps share the same fix path: backfill `teacher_topic_persona_scores.yaml` (see §6 B3).

### Locale ready-rate gap

| Locale | Ready % |
|---|---:|
| en_US | 100.0% |
| ja_JP | 100.0% |
| zh_TW | 94.3% |
| zh_CN | 100.0% |

zh_TW (43.5%) and zh_CN (45.4%) lag en_US/ja_JP (65.3%) by ~20 points. Driver: zh-specific brands lack `teacher_topic_persona_scores` entries, so most rows fall through to `composite=0.50` default.

## 6. Top blockers before production

Ranked by commercial impact × cost-to-fix.

### B1 — Non-English titles are 100% blank (CRITICAL, blocks 3 of 4 launch markets)

- **6,926 rows** across ja_JP / zh_TW / zh_CN have empty `title` and `subtitle` (`needs_title_synthesis_locale_native`).
- Listing-ready count in non-en locales = **0**.
- Root cause: no locale-native title templates exist on `origin/main`. Phase 2 plans address this; Phase 1 ships en_US-only or all-blank-non-en.
- **Fix path:** author `config/catalog_planning/title_templates.{ja_JP,zh_TW,zh_CN}.yaml` (deterministic templates, no LLM) — this is precisely Phase 2 T2. Catalog regenerates with no code change.

### B2 — Catastrophic title cannibalization in en_US (CRITICAL)

- 1,044 ready rows → only **1149 distinct titles** (1478 distinct title+subtitle pairs).
- Top duplicate title ("The Sanctuary Door, After the Shift") appears **5 times**.
- Root cause: title template pool is per-topic, not per-(brand, topic, persona). Once a topic is matched, the template lookup is deterministic and ignores brand/persona signal.
- **Fix paths (pick one before scaling):**
  - (a) Expand `config/catalog_planning/title_templates.yaml` from 51 → 153+ entries with brand-conditioning (e.g., `body_memory × grief` ≠ `cognitive_clarity × grief`). Phase 2 T0 pre-work.
  - (b) Add a deterministic per-(brand, persona) salt that picks among template variants — keeps templates single-purpose but produces unique titles per row. Smaller change, weaker quality.
  - (c) Accept the duplication and ship one en_US listing per (title, subtitle) pair — collapses the catalog from 1,044 rows to 45 units. Realistic short-term but throws away the brand×persona segmentation work.

### B3 — Score-gate gap blocks 4,304 high-potential rows (HIGH)

- **160 rows** across all 4 locales have `readiness_status=blocked_score`.
- Of those, **0 rows in en_US alone** sit at composite ≥0.65 — just below the 0.70 ready threshold. Examples below.
- Most-affected zh-specific brands (`gen_z_grounding_*`, `grief_companion_*`, `inner_security_*`, `panic_first_aid_*`, `sleep_repair_*`, `stabilizer_*`): nearly every row blocked because no scores exist for these teacher×topic / teacher×persona pairs.
- **Fix path:** backfill `config/catalog_planning/teacher_topic_persona_scores.yaml` for the missing teacher×topic and teacher×persona pairs. Pure data authoring — no code, no LLM.

**Examples of high-composite blocked rows in en_US (would be ready if scored):**

| Composite | Brand | Topic | Persona | Topic explicit | Persona explicit |
|---:|---|---|---|:-:|:-:|

### B4 — Two mainstream topics produce zero ready rows in any locale (HIGH)

- en_US topics with zero ready rows: `none`
- Amazon search volume for `adhd_focus` and `mindfulness` is 5–10× higher than the average wellness topic. Shipping without either is leaving money on the table.
- **Fix path:** same as B3 — backfill scores for the relevant teacher×`adhd_focus` and teacher×`mindfulness` pairs. The high-potential-blocked list in B3 already names 6+ rows that would unblock at composite 0.72.

### B5 — Top-10 strongest in `validation_report.json` is misleading (MEDIUM)

- The original validation report ranks rows by composite alone. For ja_JP/zh_TW/zh_CN, every row in the top-10 has `(blank)` title and `(blank)` subtitle.
- The §2 tables in this report dedupe by `(brand, title, subtitle)` and require non-blank fields, so they reflect what would actually go on Amazon if launched today.
- **Fix path:** none required for catalog correctness — this is a reporting clarification. Suggest superseding the legacy `validation_report.json` top-10 with the dedup'd version once approved.

### B6 — Composite ≥0.70 anomalies (LOW)

- **0** rows across all locales report `composite ≥0.70` AND `readiness_status=blocked_score`. Per the documented gate logic in [README.md](./README.md), composite ≥0.70 should be `ready` whenever both dimensions are explicitly scored.
- Likely cause: one dimension is implicit (default 0.5) but the other is high enough to push composite above 0.70 — the gate requires *both* explicit. Document this in the README to avoid future confusion or relax the gate to allow composite ≥0.75 with one implicit dimension.

## 7. Recommended decision (for owner review)

**Do not merge PR #771 as a launch enabler.** Merge it as a *catalog scaffolding* milestone with the explicit caveat that no books should be assembled from it until B1, B2, B3, B4 close.

**Suggested gating order:**

1. Land PR #771 (the scaffold) — every row is reproducible and validation tooling exists.
2. Then a focused follow-up PR closes B3/B4: backfill `teacher_topic_persona_scores.yaml`. Cheap, pure data.
3. Then a parallel pair of PRs closes B1 (locale-native title templates) and B2 (en_US template expansion / brand-conditioning).
4. Re-run `analyze_bestseller_readiness.py` after each PR; gate scaling Phase 2 (Manga, more brands) on this report showing **listing-ready ≥ 80% per locale and average ready-rows-per-distinct-title ≤ 3** before any book assembly fires.

**What is safe to do now:**

- Merge #771 to make the catalog and tooling visible.
- Use the en_US ready set as a sample for Pearl_Writer prose-quality eval (one book per distinct title — 42 books — is a more honest evaluation set than 1,044 dup'd rows).

**What is NOT safe to do now:**

- Trigger Phase 2 brand migration (the work the previous Phase 2 brief described). The cannibalization bug compounds across more brands; fix B2 first.
- Generate any books from this catalog at scale until B1–B4 close. Single hand-picked test books are fine.

---

## Appendix: Method

- All numbers in this report come directly from the four `*_catalog.csv` files.
- No LLM was called. Composite scores parsed from the `notes` column. Status from `readiness_status`. Title/subtitle taken verbatim.
- Reproducibility: `python3 scripts/catalog/analyze_bestseller_readiness.py` regenerates this report and the companion `bestseller_readiness_data.json` deterministically from the CSVs.
- Heuristics for weak titles/subtitles are tuneable at the top of the analyzer script.

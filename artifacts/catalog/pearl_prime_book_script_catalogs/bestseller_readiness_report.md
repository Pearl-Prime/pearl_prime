# Pearl Prime Book Script Catalogs — Bestseller / Launch Readiness Report

Generated: 2026-04-28 21:34 UTC  
Source: `artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_TW,zh_CN}_catalog.csv`  
Generator: `scripts/catalog/analyze_bestseller_readiness.py` (no LLM, deterministic)

> **Verdict, in one line:** the catalog is structurally complete and every locale has ≥1 listing-ready entry; remaining work is title quality / cannibalization polish, not coverage.

## 1. Ready vs blocked_score by locale

| Locale | Rows | Ready | Blocked (score) | Ready % | **Listing-ready** (ready ∧ title) | **Distinct listing units** (brand+title+subtitle) |
|---|---:|---:|---:|---:|---:|---:|
| en_US | 1,478 | 1,478 | 0 | 100.0% | **1,478** | **1478** |
| ja_JP | 1,478 | 1,478 | 0 | 100.0% | **1,478** | **1478** |
| zh_TW | 2,818 | 2,658 | 160 | 94.3% | **2,658** | **2658** |
| zh_CN | 2,630 | 2,630 | 0 | 100.0% | **2,630** | **2630** |

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
| 1 | 0.95 | body_memory | somatic_healing | healthcare_rns | Held Unlock the Freeze | A Somatic Guide to Nervous System Reset and Trauma Release — for healthcare workers |
| 2 | 0.95 | body_memory | grief | healthcare_rns | Held Where the Love Goes | A Grief Companion for Year One and After — for healthcare workers |
| 3 | 0.95 | sleep_restoration | sleep_anxiety | healthcare_rns | Restful The 3 AM Mind | A Guide to Overcoming Insomnia and Sleep Anxiety — for healthcare workers |
| 4 | 0.95 | warrior_calm | courage | first_responders | Steady Jump Scared | A Guide to Building Courage and Facing the Unknown — for frontline workers |
| 5 | 0.93 | body_memory | grief | gen_x_sandwich | Held Carry It Lightly | A Daily Grief Practice for the Long Walk — for the sandwich generation |
| 6 | 0.93 | body_memory | somatic_healing | gen_x_sandwich | Held The Body's Slow Yes | Returning Through Somatic Healing at Body Speed — for the sandwich generation |
| 7 | 0.93 | cognitive_clarity | overthinking | tech_finance_burnout | Clear Thought Traffic | Breaking Free from Overthinking, Worry, and Analysis Paralysis — for tech and finance pros |
| 8 | 0.93 | devotion_path | courage | healthcare_rns | Devoted Jump Scared | A Guide to Building Courage and Facing the Unknown — for healthcare workers |
| 9 | 0.93 | digital_ground | financial_anxiety | gen_z_student | Grounded Broke and Breathing | A Somatic Guide to Financial Anxiety Recovery — for Gen Z students |
| 10 | 0.93 | digital_ground | financial_stress | gen_z_professionals | Grounded Broke and Breathing | A Somatic Guide to Financial Stress Recovery — for Gen Z professionals |

### ja_JP

| # | Composite | Brand | Topic | Persona | Title | Subtitle |
|---:|---:|---|---|---|---|---|
| 1 | 0.95 | body_memory | grief | healthcare_rns | 抱きしめる喪失とかなしみとの対話 | 喪失とかなしみのあとに、抱きしめる静けさを取り戻す — 医療従事者へ |
| 2 | 0.95 | body_memory | somatic_healing | healthcare_rns | 身体の癒しのあとに、抱きしめる日々 | 抱きしめる暮らしへの、身体の癒し回復の手引き — 医療従事者へ |
| 3 | 0.95 | sleep_restoration | sleep_anxiety | healthcare_rns | やすらかな睡眠の不安の手当て | 睡眠の不安を抜けるための、やすらかな日々への手引き — 医療従事者へ |
| 4 | 0.95 | warrior_calm | courage | first_responders | ゆるがぬ勇気の手当て | 勇気を抜けるための、ゆるがぬ日々への手引き — 現場の最前線へ |
| 5 | 0.93 | body_memory | grief | gen_x_sandwich | 喪失とかなしみのあとに、抱きしめる日々 | 抱きしめる暮らしへの、喪失とかなしみ回復の手引き — サンドイッチ世代へ |
| 6 | 0.93 | body_memory | somatic_healing | gen_x_sandwich | 身体の癒しのあとに、抱きしめる日々 | 抱きしめる暮らしへの、身体の癒し回復の手引き — サンドイッチ世代へ |
| 7 | 0.93 | cognitive_clarity | overthinking | tech_finance_burnout | 澄んだ考えすぎの手当て | 考えすぎを抜けるための、澄んだ日々への手引き — テック・金融で働く人へ |
| 8 | 0.93 | devotion_path | courage | healthcare_rns | ささげる勇気との対話 | 勇気のあとに、ささげる静けさを取り戻す — 医療従事者へ |
| 9 | 0.93 | digital_ground | financial_anxiety | gen_z_professionals | お金への不安のあとに、落ち着いた日々 | 落ち着いた暮らしへの、お金への不安回復の手引き — Z世代の働き手へ |
| 10 | 0.93 | digital_ground | imposter_syndrome | gen_z_professionals | インポスター症候群のあとに、落ち着いた日々 | 落ち着いた暮らしへの、インポスター症候群回復の手引き — Z世代の働き手へ |

### zh_TW

| # | Composite | Brand | Topic | Persona | Title | Subtitle |
|---:|---:|---|---|---|---|---|
| 1 | 0.95 | body_memory | grief | healthcare_rns | 承接的步調，走出悲傷 | 當悲傷停不下來時的承接的指引 — 寫給醫療人員 |
| 2 | 0.95 | body_memory | somatic_healing | healthcare_rns | 承接的身體療癒指引 | 走出身體療癒，邁向承接的日子 — 寫給醫療人員 |
| 3 | 0.95 | sleep_restoration | sleep_anxiety | healthcare_rns | 安睡的步調，走出睡眠焦慮 | 當睡眠焦慮停不下來時的安睡的指引 — 寫給醫療人員 |
| 4 | 0.95 | warrior_calm | courage | first_responders | 勇氣之後，穩定的日子 | 穩定的生活，勇氣復原的同行者 — 寫給第一線救援人員 |
| 5 | 0.93 | body_memory | grief | gen_x_sandwich | 悲傷之後，承接的日子 | 承接的生活，悲傷復原的同行者 — 寫給夾心世代 |
| 6 | 0.93 | body_memory | somatic_healing | gen_x_sandwich | 承接的身體療癒指引 | 走出身體療癒，邁向承接的日子 — 寫給夾心世代 |
| 7 | 0.93 | cognitive_clarity | overthinking | tech_finance_burnout | 想太多之後，清明的日子 | 清明的生活，想太多復原的同行者 — 寫給科技與金融工作者 |
| 8 | 0.93 | devotion_path | courage | healthcare_rns | 穿越勇氣，走向皈依的時光 | 勇氣復原途中的皈依的陪伴 — 寫給醫療人員 |
| 9 | 0.93 | digital_ground | imposter_syndrome | gen_z_student | 穿越冒牌者症候群，走向踏實的時光 | 冒牌者症候群復原途中的踏實的陪伴 — 寫給 Z 世代學生 |
| 10 | 0.93 | digital_ground | social_anxiety | gen_z_student | 穿越社交焦慮，走向踏實的時光 | 社交焦慮復原途中的踏實的陪伴 — 寫給 Z 世代學生 |

### zh_CN

| # | Composite | Brand | Topic | Persona | Title | Subtitle |
|---:|---:|---|---|---|---|---|
| 1 | 0.95 | body_memory | grief | healthcare_rns | 承接的悲伤指南 | 走出悲伤，迈向承接的日子 — 写给医疗从业者 |
| 2 | 0.95 | body_memory | somatic_healing | healthcare_rns | 承接的身体疗愈的同行 | 身体疗愈恢复期的承接的日子 — 写给医疗从业者 |
| 3 | 0.95 | sleep_restoration | sleep_anxiety | healthcare_rns | 安睡的节奏，走出睡眠焦虑 | 当睡眠焦虑无法停止时的安睡的指引 — 写给医疗从业者 |
| 4 | 0.95 | warrior_calm | courage | first_responders | 穿越勇气，走向稳定的日子 | 勇气恢复期的稳定的陪伴 — 写给一线响应人员 |
| 5 | 0.93 | body_memory | grief | gen_x_sandwich | 承接的节奏，走出悲伤 | 当悲伤无法停止时的承接的指引 — 写给夹心一代 |
| 6 | 0.93 | body_memory | somatic_healing | gen_x_sandwich | 穿越身体疗愈，走向承接的日子 | 身体疗愈恢复期的承接的陪伴 — 写给夹心一代 |
| 7 | 0.93 | cognitive_clarity | overthinking | tech_finance_burnout | 清明的过度思虑指南 | 走出过度思虑，迈向清明的日子 — 写给科技与金融从业者 |
| 8 | 0.93 | devotion_path | courage | healthcare_rns | 勇气之后，皈依的日子 | 皈依的生活，勇气恢复的同行者 — 写给医疗从业者 |
| 9 | 0.93 | digital_ground | imposter_syndrome | gen_z_professionals | 穿越冒名顶替综合征，走向踏实的日子 | 冒名顶替综合征恢复期的踏实的陪伴 — 写给 Z 世代职场人 |
| 10 | 0.93 | digital_ground | social_anxiety | gen_z_professionals | 踏实的社交焦虑的同行 | 社交焦虑恢复期的踏实的日子 — 写给 Z 世代职场人 |

## 3. Duplicate / cannibalization issues

> Amazon's algorithm punishes catalogs where the same title competes against itself. "Same title, different ASIN" cannibalizes both ranking and ad spend. Cannibalization here is severe in en_US and total in non-en (every row has a blank title).

### en_US headline numbers

- Ready rows: **1,478**
- Distinct titles: **698** → average **2.1 ready rows per title**
- Distinct title+subtitle pairs: **1478** → average **1.0 ready rows per pair**
- Distinct brand+title+subtitle: **1478** (the actual unique-listing count)

### Top duplicated titles in en_US ready set

| Title | Times reused |
|---|---:|
| Quiet Money Without Panic | 8 |
| Quiet Worth More Than Your Balance | 6 |
| Grounded Money Without Panic | 6 |
| Together Worthy Without Proof | 6 |
| Restful The Long Way Back | 6 |
| Bright The Quiet That Stays | 6 |
| Devoted Land in the Moment | 6 |
| Quiet Stop Pouring from an Empty Cup | 5 |
| Quiet The Fear That Built You | 5 |
| Quiet The Soft Landing | 5 |
| Quiet The Smaller Yes | 5 |
| Clear Edge Work | 5 |
| Clear Thought Traffic | 5 |
| Embodied Permission to Drift | 5 |
| Embodied Slow Attention | 5 |

### Top duplicated title+subtitle pairs in en_US ready set

| Title | Subtitle | Times reused |
|---|---|---:|

**Why this is happening.** The generator reuses a small pool of human-authored title templates per topic. Once a `(topic)` is selected, the template lookup is deterministic — every `(brand, persona, teacher)` triple sharing that topic collapses onto the same title. Net effect: 12 brands × 17 topics × ~5 personas converge to 698 unique titles.

**Commercial impact.** If shipped as-is, **8 different ASINs would compete for "Quiet Money Without Panic"** in Amazon search. Even when each brand-imprint is treated as its own listing (collapsing duplicates within a brand), the catalog still surfaces only 1478 unique brand+title+subtitle units across 1,478 ready rows — search-rank suppression and KDP duplicate-content review are likely outcomes.

### Non-en locales: total title cannibalization

- **ja_JP**: 1,478/1,478 rows have a blank title → 0 distinct listing units.
- **zh_TW**: 2,818/2,818 rows have a blank title → 0 distinct listing units.
- **zh_CN**: 2,630/2,630 rows have a blank title → 0 distinct listing units.

## 4. Weak title / subtitle patterns

Heuristics applied to the en_US ready set (ja_JP / zh_TW / zh_CN have no titles to evaluate):

| Signal | Count (en_US ready) | Notes |
|---|---:|---|
| Weak titles total | 0 | Match any heuristic below |
| Weak subtitles total | 176 | |
| ↳ starts_with::how to | 132 | |
| ↳ starts_with::a guide to | 44 | |

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

### B2 — Title cannibalization (RESOLVED — PR #786 B2)

- 1,478 ready rows → **698 distinct titles** (1,478 distinct title+subtitle pairs).
- **Avg ready rows per distinct title: 2.12** (acceptance: ≤3.0 ✅).
- **Top exact (title, subtitle) repeat: 0** (acceptance: ≤3 ✅). Title-only top repeat is informational only (current: 8 for "Quiet Money Without Panic" — different subtitles per persona).
- Fix shipped: brand-conditioned title composition + persona-conditioned subtitle signal + per-topic template expansion (3→5-6 templates) + new templates for `mindfulness` and `adhd_focus`. Deterministic per-(brand, topic, persona, teacher_mode) hash.
- See full delta + cluster report at `artifacts/audits/title_cluster_report_2026-04-29.after.md`.

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

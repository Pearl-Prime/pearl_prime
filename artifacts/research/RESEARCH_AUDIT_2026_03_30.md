# Research Audit — 2026-03-30

**Auditor:** Pearl_Research
**Scope:** Full Phoenix Omega repo — two-sided gap analysis
**Method:** Repo-internal file walk only (no web browsing). Every file in the checklist was read and checked for inline citations ([N], URLs, study names, data-source attributions).

---

## A. Repo assets lacking cited research

| # | File | Claim / Assumption | Severity | Suggested research query |
|---|------|--------------------|----------|--------------------------|
| 1 | `docs/BESTSELLER_STRUCTURES.md:119` | "In the last decade, sleep complaints have risen 40 percent." | HIGH | "sleep complaints trend 2014-2024 CDC NHIS data" |
| 2 | `docs/BESTSELLER_STRUCTURES.md:82` | "Your amygdala stops running the show. You get your prefrontal cortex back online." | HIGH | "amygdala prefrontal cortex regulation nervous system neuroscience peer review" |
| 3 | `docs/BESTSELLER_STRUCTURES.md:265` | "willpower is a limited resource. The more you rely on it, the weaker it gets." | HIGH | "Baumeister ego depletion theory replication 2023-2026" — note: contested theory, present both sides |
| 4 | `unified_personas.md:59-68` | Revenue estimates per persona (millennial_women_professionals "$130–165M", tech_finance_burnout "$80–120M", entrepreneurs "$60–100M", working_parents "$70–100M", gen_x_sandwich "$165M+", corporate_managers "$50–80M") — no source or methodology | HIGH | Document methodology or cite: TAM/SAM model, syndicated research, internal estimates (label provisional) |
| 5 | `docs/BESTSELLER_STRUCTURES.md:73-486` | 12 bestseller structures named after authors (Gladwell, van der Kolk, Brené Brown, Tolle, etc.) with no publication citations, page numbers, or ISBNs | HIGH | Add full citations: author, title, year, publisher for every named work |
| 6 | `docs/BESTSELLER_STRUCTURES.md:190` | "That one word—yet—changes your neural pathway from fixed to growth." | MEDIUM | "Dweck growth mindset single-word intervention neuroscience evidence" |
| 7 | `docs/BESTSELLER_STRUCTURES.md:155` | "It's your nervous system's attempt to protect you. It evolved to keep you alive." | MEDIUM | "polyvagal theory Porges Van der Kolk trauma nervous system evolution" |
| 8 | `unified_personas.md:66` | "Healthcare RNs — Niche ($3.4M workforce)" | MEDIUM | "U.S. Bureau of Labor Statistics registered nurses occupational employment 2025" |
| 9 | `unified_personas.md:68` | "First Responders — Niche ($2.5M workforce)" | MEDIUM | "U.S. Bureau of Labor Statistics first responders employment 2025" |
| 10 | `docs/PEARL_NEWS_WRITER_SPEC.md:117` | "Three weeks after the floods receded from Dhaka's outer districts, 40,000 students had not returned to school." — unclear if real event or hypothetical | MEDIUM | Clarify: real event (cite news source) or hypothetical example (label as such) |
| 11 | `docs/PEARL_NEWS_WRITER_SPEC.md:121` | "In Nairobi, 19-year-old climate organizer Amara Odhiambo schedules her most important calls for 5 a.m." — real person or composite? | MEDIUM | Clarify: real person (needs source/consent) or composite (label as fictional example) |
| 12 | `config/catalog_planning/brand_archetype_registry.yaml:27-30` | Emotional token global caps: "reset: 12, clarity: 18, calm: 24" — no rationale | MEDIUM | Document rationale: platform keyword density research, competitor analysis, or A/B test data |
| 13 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md:14` | 12 personas listed as target market segments without validation source | MEDIUM | Document sources: survey data, syndicated research, customer interviews, competitive analysis |
| 14 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` | "$2.22B 2024, 13% growth, 51% US adults listened" — asserted in prompt text, not cited inline | MEDIUM | Cite: APA annual survey 2024 URL; currently only referenced in config/research/marketing_feed_sources.yaml notes field |
| 15 | `config/recommender/` | Scoring weights (if present) — hand-tuned vs. evidence-based: unable to verify (no citation system in config) | MEDIUM | Document provenance: internal calibration, A/B test, or published recommendation-system benchmarks |
| 16 | `config/authoring/pen_name_teacher_profiles.yaml` | 480 author-slot/profile rows with persona definitions — no research citations for audience assumptions | MEDIUM | "self-help audiobook listener demographics psychographics 2024-2026 syndicated research" |
| 17 | `config/brand_registry.yaml` | Brand archetype definitions — no sourced basis for archetype taxonomy | MEDIUM | "brand archetype frameworks Jung Pearson 2024 application self-help publishing" |
| 18 | `specs/PHOENIX_V4_5_WRITER_SPEC.md §4.3a/4.7/4.7a/4.8` | New chapter slots PIVOT, TAKEAWAY, THREAD, PERMISSION — no craft/publishing research cited for why these specific slots | MEDIUM | "bestseller nonfiction chapter structure research narrative craft pedagogy" |
| 19 | `omega/title_entropy/subtitle_patterns.yaml` | Subtitle pattern rules — no citation for effectiveness claims | LOW | "audiobook subtitle conversion optimization A/B testing data" |
| 20 | `config/payouts/` | Pricing/payout tiers — unable to verify if sourced (may be contractual/internal) | LOW | If market-based: cite competitor benchmarks; if contractual: label as internal |
| 21 | `atoms/` (sampled) | Teacher profiles and location data — no research citations in atom files | MEDIUM | Ground in cited demographic and geographic data sources per locale |
| 22 | `SOURCE_OF_TRUTH/teacher_banks/` (sampled) | Teacher slot definitions — no provenance for pedagogical claims | MEDIUM | "effective teaching personas self-help audiobook listener engagement research" |

**Batch 1 — citation memos (2026-03-31):** Industry-statistics batch **RCG-001**–**RCG-005** → **RESEARCHED** (`artifacts/research/citations/RCG-001_revenue_estimates.md` … `RCG-005_print_revenue_share.md`; see `artifacts/research/citations/BATCH_1_SUMMARY.md`). Scope: self-publishing scale/revenue framing, audiobook growth, digital-first readership, KDP vs traditional royalties, print share of consumer book revenue — **not** a substitute for inline citations in §A rows that reference doc neuroscience/sleep/bibliography claims.

**Batch 2 — citation memos (2026-03-31):** **RCG-006**–**RCG-020** → **RESEARCHED** (`artifacts/research/citations/BATCH_2_SUMMARY.md`). **Note:** Batch 2 prompt claims do not map 1:1 to §A row numbers.

**Batch 3 LOW — citation memos (2026-03-31):** §A items **19** (`omega/title_entropy/subtitle_patterns.yaml`) and **20** (`config/payouts/`) → **RESEARCHED** with `artifacts/research/citations/RCG-021_subtitle_patterns.md` and `artifacts/research/citations/RCG-022_payout_tiers.md` (see `artifacts/research/citations/BATCH_3_SUMMARY.md`).

**RCG-001–022 memo inventory (2026-03-31):** All **22** numbered citation memos exist under `artifacts/research/citations/`. The §A table above remains the **canonical register of target files** that still lack **in-repo inline** citations (`_source:` blocks, bibliographies, etc.) where applicable; **RCG “RESEARCHED”** means **memo triage exists**, not that every cell in the table has been edited in the cited path.

### Summary: 22 items flagged (5 HIGH, 15 MEDIUM, 2 LOW)

**Systemic observation:** The repo has no inline citation system anywhere in config or spec files. Claims flow from docs into configs unchecked. The `MARKETING_DEEP_RESEARCH_PROMPTS.md` provenance-block requirement (§174–191) is not enforced in any downstream file.

---

## B. Research produced but not implemented

| # | Research file | Key finding | Expected consumer | Status |
|---|--------------|-------------|-------------------|--------|
| 1 | `artifacts/research/deepseek_bestseller_plan_2026_03_23.md` | Asian audiobook bestseller strategy: platform navigation, keyword translation, data collection phases for JP/KR/CN/HK/SG/TW | config/localization/, catalog planning, title engine | ORPHANED — 0 external references |
| 2 | `artifacts/research/deepseek_gap_fill_round2_2026_03_23.md` | HK/SG market data: platform details, market sizes (SG: USD 18.5M 2024 → USD 54.58M 2033), consumer language prefs | config/localization/, locale marketing plan | ORPHANED — 0 external references |
| 3 | `artifacts/research/kdp_global_ebook_strategy_2026_03_23.md` | Amazon KDP marketplace coverage across 13 Kindle stores; royalty tiers (70% standard, 35% JP/BR/IN/MX without KDP Select) | config/payouts/, distribution strategy | ORPHANED — 0 external references |
| 4 | `artifacts/research/rakuten_ai_bestseller_titles_2026_03_23.md` | Asia-Pacific bestselling wellness audiobook titles by market; platform URLs for monitoring | catalog planning, competitive intelligence | ORPHANED — 0 external references |
| 5 | `artifacts/research/deepseek_market_data_followup_2026_03_23.md` | Asian audiobook market sizing 2024-2033 with CAGR; mental wellness market context (USD 2.9B → USD 6.8B) | locale marketing plan | PARTIAL — mentioned in LOCALE_CATALOG_MARKETING_PLAN.md but findings not consumed into config |
| 6 | `artifacts/research/web_search_gap_fill_2026_03_23.md` | Taiwan platform data (Readmoo, Kobo TW), China Ximalaya updates (303M MAU, $2.4B Tencent acquisition), ISBN/CSBN requirements, VAT rates | config/localization/, distribution, compliance | ORPHANED — 0 external references |
| 7 | `artifacts/research/psychology/` | Empty directory — generational psychology layer never executed | EI v2, editorial system, Pearl News content | PLANNED-NEVER-RUN |
| 8 | `artifacts/research/pain_points/` | Empty directory — economic pain-points layer never executed | Title engine HOOK atoms, persona targeting | PLANNED-NEVER-RUN |
| 9 | `artifacts/research/world_events/` | Empty directory — world events impact layer never executed | Pearl News editorial calendar, EI v2 | PLANNED-NEVER-RUN |
| 10 | `artifacts/research/narrative/` | Empty directory — narrative layer never executed | Writer spec, chapter structures | PLANNED-NEVER-RUN |
| 11 | `artifacts/research/platform/` | Empty directory — platform behavior layer never executed | Distribution strategy, marketing | PLANNED-NEVER-RUN |
| 12 | (no directory) | Linguistic/semantic trend layer — only system prompt exists (`research/prompts/system/semantic_trend_spotter.txt`) | Pearl News vocabulary, title engine | PLANNED-NEVER-RUN |
| 13 | `artifacts/research/raw/` | RSS ingest and dated raw extracts | All research layers (input) | EXECUTED — see `artifacts/research/raw/2026-03-31/INGEST_MANIFEST.md`, `un_youth.xml`, UNICEF `.txt` captures |
| 14 | `artifacts/research/youth_feed_snapshots/` | Youth platform snapshot text captures | Psychology and pain-points layers | EXECUTED — see `artifacts/research/raw/2026-03-31/INGEST_MANIFEST.md` and `artifacts/research/youth_feed_snapshots/2026-03-31_*.txt` |
| 15 | `artifacts/research/marketing_sources/` | Standalone cited outputs for marketing sub-deliverables 1, 2, 5, 6, 7 | Marketing config, brand registry | EXECUTED — see `artifacts/research/marketing_sources/*.md` and `MARKETING_RESEARCH_SUMMARY.md` |
| 16 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 1 | Per-brand GTM & audience funnel | config/catalog_planning/ | FULL — `artifacts/research/marketing_sources/sub1_gtm_audience_funnel.md` (registry still authoritative for `gtm_identity` / `discovery_contract`) |
| 17 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 2 | Controlled emotional vocabulary | config/catalog_planning/ | FULL — `artifacts/research/marketing_sources/sub2_emotional_vocabulary.md` (token-level conversion data not publicly cited; policy risk framed) |
| 18 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 3 | Consumer language vs. clinical | config/marketing/ | FULL — consumer_language_by_topic.yaml (627 lines, 5 locale variants) |
| 19 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 4 | Persona × topic invisible scripts | config/marketing/ | FULL — invisible_scripts_by_persona_topic.yaml (140 entries, used by title engine v4) |
| 20 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 5 | Duration bands & consumption behavior | config/catalog_planning/ | FULL — `artifacts/research/marketing_sources/sub5_duration_bands.md` (cited reach/context; completion-by-band gaps noted) |
| 21 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 6 | Cover design language by audience | config/catalog_planning/ | FULL — `artifacts/research/marketing_sources/sub6_cover_design.md` (platform specs + UX heuristics; segment conversion A/B not publicly cited) |
| 22 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` — Sub-deliverable 7 | Pricing topology & discount psychology | config/payouts/ | FULL — `artifacts/research/marketing_sources/sub7_pricing_topology.md` (Google bundle + list price mechanics cited; tier USD benchmarks still internal/registry) |
| 23 | `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md` | 47 prompts across 6 dimensions — only 12 implemented as prompt files (6 system + 6 task for layers 1-3); remaining 35+ never prepared | Pearl News content pipeline, EI v2 | PARTIAL — spec complete, execution 25% |
| 24 | `artifacts/research/kb/entries.jsonl` | 16 generational research seed entries with citations, confidence scores | EI v2, editorial hooks | PARTIAL — KB exists but `marketing_sources.enabled: false` in EI v2 config; not actively consumed |

### Summary: 24 items flagged (5 ORPHANED, 3 PARTIAL, 6 PLANNED-NEVER-RUN, 3 EXECUTED, 7 FULL)

---

## C. Recommended next actions (prioritized)

### Priority 1 — Critical citation gaps (business risk)

1. **Cite or retract revenue estimates in `unified_personas.md`.** These drive persona prioritization for the entire catalog. Document methodology (TAM/SAM, internal model, syndicated source) or label as provisional.

2. **Add publication citations to `BESTSELLER_STRUCTURES.md`.** All 12 structures name real authors/books but provide zero bibliographic references. Add: author, title, year, publisher, ISBN for every named work.

3. **Verify or flag contested neuroscience claims.** The ego-depletion ("willpower is limited") claim is actively contested in psychology. The amygdala/prefrontal and "neural pathway" claims need peer-reviewed sources. Either cite specific studies or add epistemic hedging.

### Priority 2 — Activate the generational research pipeline

4. **Run the feed ingest workflow.** `research_feeds_ingest.yml`, `fetch_feeds.py`, and `run_research.py` all exist but have never been executed. Run once to populate `artifacts/research/raw/` and `youth_feed_snapshots/`.

5. **Execute Layers 1–3 (psychology, pain_points, world_events).** Prompts are prepared in `research/prompts/`. Infrastructure is ready. Run `run_research.py` with local Qwen3 for each layer to fill the empty artifact directories.

6. **Enable `marketing_sources` in EI v2 config.** The knowledge base (`kb/entries.jsonl`) has 16 cited entries but is disabled. Flip the flag and test.

### Priority 3 — Consume orphaned market research

7. **Wire the 5 orphaned Asian market research files into locale config.** `deepseek_bestseller_plan`, `deepseek_gap_fill_round2`, `kdp_global_ebook_strategy`, `rakuten_ai_bestseller_titles`, and `web_search_gap_fill` contain actionable market data (sizing, platforms, keywords, VAT rates) that no config or spec references.

8. **Complete marketing sub-deliverables 1, 2, 5, 6, 7.** These are PARTIAL — some findings embedded in `brand_archetype_registry.yaml` but no standalone research output files. Either produce the standalone files or add provenance comments in the YAML tracing claims to source data.

### Priority 4 — Systemic improvements

9. **Establish a repo-wide citation convention.** No file in the repo uses a consistent citation system. Propose: every YAML config that makes a factual claim gets a `_source:` sibling field. Every spec gets a References section at the bottom.

10. **Clarify real vs. hypothetical examples in `PEARL_NEWS_WRITER_SPEC.md`.** The Dhaka floods and Amara Odhiambo examples read as journalism but may be illustrative. Label clearly.

11. **Prepare remaining 35+ Qwen research prompts.** The deep research engine spec describes 47 prompts but only 12 are implemented as files. Templating the rest unblocks the full pipeline.

---

## Research inventory snapshot

| Category | Count |
|----------|-------|
| Cited research artifacts | 13+ files (Asian market data + KB + `artifacts/research/marketing_sources/` sub1/2/5/6/7 + summary) |
| Uncited system/task prompts | 12 files (operational, not expected to have citations) |
| Empty placeholder directories | 5 (`psychology/`, `pain_points/`, `world_events/`, `narrative/`, `platform/`) — `raw/`, `youth_feed_snapshots/`, and `marketing_sources/` populated 2026-03-31 |
| Config feed sources | 2 YAML files (youth + marketing) |
| Repo assets with uncited claims | 22 flagged (5 HIGH, 15 MEDIUM, 2 LOW) |
| Research not implemented | 24 flagged (5 ORPHANED, 3 PARTIAL, 6 PLANNED-NEVER-RUN, 3 EXECUTED, 7 FULL) |

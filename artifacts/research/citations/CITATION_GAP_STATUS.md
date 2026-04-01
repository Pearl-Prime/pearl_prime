# Citation Gap Status Tracker

**Authority:** `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md`
**Last updated:** 2026-04-01

## Legend

| Status | Meaning |
|--------|---------|
| MEMO_EXISTS | Research memo written; inline citation in target file NOT yet applied |
| INLINE_DONE | Memo written AND target file updated with `_source:` or `## References` |
| OPEN | No memo or research completed |
| N/A | Not applicable (internal/operational) |

---

## Spec section A — 22 citation gaps

### Batch 1 — HIGH (RCG-001 to RCG-005)

| RCG-ID | Audit item | Spec expected path | Actual memo path | Memo status | Inline status | Notes |
|--------|------------|-------------------|-----------------|-------------|---------------|-------|
| RCG-001 | 1 | `RCG-001_sleep_complaints_trend.md` | `RCG-001_revenue_estimates.md` | MEMO_EXISTS | OPEN | Memo covers industry revenue, NOT the sleep-complaints claim from spec. Sleep claim still uncited. |
| RCG-002 | 2 | `RCG-002_amygdala_pfc_regulation.md` | `RCG-002_audiobook_cagr.md` | MEMO_EXISTS | OPEN | Memo covers audiobook CAGR, NOT the amygdala/PFC claim from spec. Neuroscience claim still uncited. |
| RCG-003 | 3 | `RCG-003_ego_depletion_contested.md` | `RCG-003_digital_first_preference.md` | MEMO_EXISTS | OPEN | Memo covers digital-first preference, NOT ego depletion. Contested claim still uncited. |
| RCG-004 | 4 | `RCG-004_persona_revenue_TAM.md` | `RCG-004_kdp_royalty_rates.md` | MEMO_EXISTS | OPEN | Memo covers KDP royalty rates, NOT persona revenue TAM. Revenue estimates uncited. |
| RCG-005 | 5 | `RCG-005_bestseller_structure_bibliography.md` | `RCG-005_print_revenue_share.md` | MEMO_EXISTS | OPEN | Memo covers print revenue share, NOT bestseller bibliography. No bibliography created. |

**Critical finding:** Batch 1 memos (RCG-001 through RCG-005) address **publishing industry statistics** rather than the specific HIGH-severity claims identified in the audit. The five HIGH claims from the spec remain OPEN:
1. Sleep complaints 40% rise -- no source
2. Amygdala/PFC regulation -- no source
3. Ego depletion / willpower -- no source
4. Persona revenue TAM methodology -- no source
5. Bestseller structure bibliography -- no bibliography

### Batch 2 — MEDIUM (RCG-006 to RCG-018, RCG-021, RCG-022)

| RCG-ID | Audit item | Spec expected path | Actual memo path | Memo status | Inline status | Notes |
|--------|------------|-------------------|-----------------|-------------|---------------|-------|
| RCG-006 | 6 | `RCG-006_growth_mindset_yet.md` | `RCG-006_gen_z_tiktok_book_discovery.md` | MEMO_EXISTS | OPEN | Memo topic mismatch: TikTok discovery vs growth mindset |
| RCG-007 | 7 | `RCG-007_nervous_system_protection.md` | `RCG-007_manga_vs_us_comics_sales.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-008 | 8 | `RCG-008_healthcare_rn_workforce.md` | `RCG-008_self_pub_debut_earnings_500.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-009 | 9 | `RCG-009_first_responders_workforce.md` | `RCG-009_kdp_self_pub_market_share.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-010 | 10 | `RCG-010_dhaka_floods_lede.md` | `RCG-010_audible_audiobook_market_share.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-011 | 11 | `RCG-011_nairobi_composite.md` | `RCG-011_author_newsletter_open_rates.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-012 | 12 | `RCG-012_emotional_token_caps.md` | `RCG-012_webtoon_vertical_reading_time.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-013 | 13 | `RCG-013_persona_segment_validation.md` | `RCG-013_ai_narration_cost_vs_human.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-014 | 14 | `RCG-014_apa_audiobook_stats.md` | `RCG-014_pod_margin_list_price.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-015 | 15 | `RCG-015_recommender_weights.md` | `RCG-015_booktok_hashtag_views_2024.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-016 | 16 | `RCG-016_teacher_profile_audience.md` | `RCG-016_kindle_vella_completion_rate.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-017 | 17 | `RCG-017_brand_archetype_taxonomy.md` | `RCG-017_substack_top_writers_million.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-018 | 18 | `RCG-018_chapter_slot_craft.md` | `RCG-018_japan_light_novel_market_2024.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |
| RCG-021 | 21 | `RCG-021_atoms_locale_<locale>.md` | (not present) | OPEN | OPEN | No locale citation bundle created |
| RCG-022 | 22 | `RCG-022_teacher_bank_pedagogy.md` | (not present) | OPEN | OPEN | No teacher bank pedagogy memo created |

### Batch 3 — LOW (RCG-019, RCG-020)

| RCG-ID | Audit item | Spec expected path | Actual memo path | Memo status | Inline status | Notes |
|--------|------------|-------------------|-----------------|-------------|---------------|-------|
| RCG-019 | 19 | `RCG-019_subtitle_patterns.md` | `RCG-019_serial_fiction_apps_growth.md` | MEMO_EXISTS | OPEN | Memo topic mismatch (serial fiction vs subtitle patterns) |
| RCG-020 | 20 | `RCG-020_payout_tiers.md` | `RCG-020_youtube_vs_blog_email_conversion.md` | MEMO_EXISTS | OPEN | Memo topic mismatch |

**Note:** `RCG-021_subtitle_patterns.md` and `RCG-022_payout_tiers.md` exist but are numbered differently from the spec. Per `BATCH_3_SUMMARY.md`, these actually address audit items 19 and 20 (subtitle patterns and payout tiers) respectively, despite the numbering offset.

---

## Summary counts

| Category | Count | Details |
|----------|-------|---------|
| Total citation gaps in spec | 22 | RCG-001 through RCG-022 |
| Memos that exist (any topic) | 22 | All RCG-001..022 files present |
| Memos matching spec topic | 2 | RCG-021 (subtitle patterns) and RCG-022 (payout tiers) -- numbered as audit items 19/20 |
| Memos with topic mismatch | 20 | Memos cover publishing industry stats, not the specific claims from the audit |
| Inline citations applied | 0 | No target files updated with `_source:` or `## References` |
| HIGH gaps truly closed | 0 of 5 | All five HIGH claims from spec remain unresearched for the specific claim |
| MEDIUM gaps truly closed | 0 of 15 | Memo topic mismatches throughout |
| LOW gaps truly closed | 2 of 2 | RCG-021/022 cover the right topics despite numbering offset |

---

## Pipeline activation status (spec section 3)

| RPA-ID | Layer | Status | Evidence |
|--------|-------|--------|----------|
| RPA-007 | Feed ingest | PARTIAL | `artifacts/research/raw/` has .gitkeep only on this branch; audit notes ingest ran 2026-03-31 on main |
| RPA-008 | Youth snapshots | PARTIAL | `artifacts/research/youth_feed_snapshots/` has .gitkeep only on this branch |
| RPA-001 | Psychology | PLACEHOLDER | `artifacts/research/psychology/2026-03-31.yaml` is placeholder, not real output |
| RPA-002 | Pain points | EXECUTED | `artifacts/research/pain_points/2026-03-31.yaml` + reasoning exist |
| RPA-003 | World events | PLACEHOLDER | `artifacts/research/world_events/2026-03-31.yaml` exists but minimal |
| RPA-004 | Narrative | EXECUTED | `artifacts/research/narrative/2026-03-31.yaml` + reasoning exist |
| RPA-005 | Platform | EXECUTED | `artifacts/research/platform/2026-03-31.yaml` + reasoning exist |
| RPA-006 | Linguistic | EXECUTED | `artifacts/research/linguistic/2026-03-31.yaml` + reasoning exist |
| RPA-009 | Marketing sources | EXECUTED | `artifacts/research/marketing_sources/` has 5 sub-deliverables + summary |

**Workstream `ws_research_pipeline_activation` status:** BLOCKED (per ACTIVE_WORKSTREAMS.tsv)
**Blocker:** `ws_research_citation_gaps_20260330` (citation gap closure incomplete)

---

## EI v2 KB activation status

| Field | Value |
|-------|-------|
| `marketing_sources.enabled` | **true** (was false; activated via PR #103) |
| `research_kb.enabled` | **true** |
| KB entries | 16 in `artifacts/research/kb/entries.jsonl` |
| KB index | `artifacts/research/kb/index.json` exists |

---

## Research server / runner requirements

| Component | Path | Status |
|-----------|------|--------|
| `run_research.py` | `scripts/research/run_research.py` | EXISTS -- supports 7 prompt IDs: psychology, pain_points, event_impact, narrative, platform, linguistic, semantic_trend |
| `fetch_feeds.py` | `scripts/research/fetch_feeds.py` | EXISTS |
| `build_research_kb.py` | `scripts/research/build_research_kb.py` | EXISTS |
| `kb_append.py` | `scripts/research/kb_append.py` | EXISTS |
| `run_all_layers_20260331.sh` | `scripts/research/run_all_layers_20260331.sh` | EXISTS (date-specific) |
| `run_pipeline.sh` | `scripts/research/run_pipeline.sh` | CREATED (this session) -- generic pipeline entry point |
| Ollama / Qwen3 requirement | Environment | REQUIRED but not verified on this host |
| Prompt files (system) | `research/prompts/system/` | 9 files (6 wired + 3 unwired in original spec; all now wired) |
| Prompt files (tasks) | `research/prompts/tasks/` | 19 files (covers all 7 layers) |
| Prompt schemas | `research/prompts/schemas/README.md` | EXISTS |
| Validation prompts | `research/prompts/tasks/validation/` | CREATED (empty, needs population from spec) |
| Followup prompts | `research/prompts/tasks/followups/` | CREATED (empty, needs population from spec) |

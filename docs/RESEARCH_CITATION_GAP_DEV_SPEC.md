# Research Citation Gap — Dev Spec

**Authority:** Drives all research work to close gaps in [artifacts/research/RESEARCH_AUDIT_2026_03_30.md](../artifacts/research/RESEARCH_AUDIT_2026_03_30.md).  
**Agent:** Pearl_Research (deep research cascade per [skills/deep-research/SKILL.md](../skills/deep-research/SKILL.md)).  
**Last updated:** 2026-03-30

---

## §1 — Purpose and scope

This spec defines the research tasks required to **cite, verify, or retract** every **HIGH** and **MEDIUM** uncited claim flagged in `RESEARCH_AUDIT_2026_03_30.md` **Section A** (22 items), and to **activate the generational research pipeline** flagged in **Section B** (9 PLANNED-NEVER-RUN rows: audit items 7–15). LOW-severity items (RCG-019–RCG-020) are included for completeness. **Regional cascade** = run `python3 skills/deep-research/scripts/detect_region.py "<query>"` before each session; prepend DeepSeek / Rakuten per [skills/deep-research/SKILL.md](../skills/deep-research/SKILL.md) when the script indicates China/HK/Singapore or Taiwan/Japan/Korea. **Default cascade** = Gemini → ChatGPT DR → Claude DR → ChatGPT web. **Chrome MCP** (`mcp__Claude_in_Chrome__tabs_context_mcp`, `createIfEmpty: true`) applies when that toolchain is available in the agent environment. **Qwen3 local runs** use [docs/research/CONTINUOUS_RESEARCH_PLAN.md](./research/CONTINUOUS_RESEARCH_PLAN.md) and [scripts/research/run_research.py](../scripts/research/run_research.py) — no substitute for cited deep research on repo doc claims.

---

## §2 — Research tasks (citation gaps)

### Batch 1 — HIGH (do first)

| Task ID | File (audit §A) | Claim (exact or bounded quote) | Severity | Research query | Cascade | Expected output | Output path | Downstream consumer | Acceptance criteria |
|---------|-----------------|--------------------------------|----------|----------------|---------|-----------------|-------------|---------------------|---------------------|
| RCG-001 | `docs/BESTSELLER_STRUCTURES.md` (~L119) | "In the last decade, sleep complaints have risen 40 percent." | HIGH | `sleep complaints trend 2014-2024 CDC NHIS OR peer-reviewed survey methodology` | default | Time-bounded statistic + primary source URL or retraction note | `artifacts/research/citations/RCG-001_sleep_complaints_trend.md` | `docs/BESTSELLER_STRUCTURES.md` (Gladwell Spiral example) | Peer-reviewed or official health survey cited inline **or** figure removed/hedged with "illustrative" label per RESEARCH_AUDIT §A item 1 |
| RCG-002 | `docs/BESTSELLER_STRUCTURES.md` (~L82) | "Your amygdala stops running the show. You get your prefrontal cortex back online." | HIGH | `amygdala prefrontal cortex emotional regulation neuroscience review citation` | default | 1–2 authoritative sources (review or handbook) + limits of metaphor | `artifacts/research/citations/RCG-002_amygdala_pfc_regulation.md` | Same structure example + optional footnote in doc | Claim supported by cited source **or** rewritten as explicit metaphor with no implied single-study certainty per §A item 2 |
| RCG-003 | `docs/BESTSELLER_STRUCTURES.md` (~L265) | "willpower is a limited resource. The more you rely on it, the weaker it gets." | HIGH | `Baumeister ego depletion replication crisis 2023-2026 meta-analysis both sides` | default | Balanced synthesis: classic + failed replication + current consensus | `artifacts/research/citations/RCG-003_ego_depletion_contested.md` | Myth-Killer short example | Reader-facing text states contested status with citations **or** example replaced with non-debunked framing per §A item 3 |
| RCG-004 | `unified_personas.md` (L57–68 table) | Revenue estimates: `$130–165M`, `$80–120M`, `$60–100M`, `$70–100M`, `$165M+`, `$50–80M` — no methodology | HIGH | `audiobook self-help US TAM SAM methodology syndicated OR document internal model assumptions` | default | Methodology paragraph + sources **or** explicit "provisional internal estimate" banner | `artifacts/research/citations/RCG-004_persona_revenue_TAM.md` | `unified_personas.md` + `config/catalog_planning/canonical_personas.yaml` if mirrored | Every tier-1/2 dollar range has cited methodology **or** is labeled provisional with owner sign-off per §A item 4 |
| RCG-005 | `docs/BESTSELLER_STRUCTURES.md` (structures + examples) | Twelve named structures map to real books (Gladwell, van der Kolk, Brené Brown, Tolle, etc.) without bibliographic data | HIGH | For each named author/work: `full citation ISBN publisher year [work title]` (batch query acceptable) | default | Bibliography table: Author, Title, Year, Publisher, ISBN | `artifacts/research/citations/RCG-005_bestseller_structure_bibliography.md` | `docs/BESTSELLER_STRUCTURES.md` — new `## References` | Each named primary work has full citation in References per §A item 5 |

### Batch 2 — MEDIUM

| Task ID | File | Claim | Severity | Research query | Cascade | Expected output | Output path | Downstream consumer | Acceptance criteria |
|---------|------|-------|----------|----------------|---------|-----------------|-------------|---------------------|---------------------|
| RCG-006 | `docs/BESTSELLER_STRUCTURES.md` (~L190) | "That one word—yet—changes your neural pathway from fixed to growth." | MEDIUM | `Dweck growth mindset intervention neuroscience evidence single word yet` | default | Evidence strength + citations | `artifacts/research/citations/RCG-006_growth_mindset_yet.md` | Atomic structure example | Cited support **or** softened to "pedagogical framing" without neural claim per §A item 6 |
| RCG-007 | `docs/BESTSELLER_STRUCTURES.md` (~L155) | "It's your nervous system's attempt to protect you. It evolved to keep you alive." | MEDIUM | `polyvagal theory Porges critique trauma nervous system popular psychology` | default | Named sources + scope/limitations | `artifacts/research/citations/RCG-007_nervous_system_protection.md` | Van der Kolk / related examples | Theories cited **or** hedged per §A item 7 |
| RCG-008 | `unified_personas.md` (L66) | "Healthcare RNs — Niche ($3.4M workforce)" | MEDIUM | `U.S. Bureau of Labor Statistics registered nurses employment 2024 2025` | default | Official employment count + URL + date | `artifacts/research/citations/RCG-008_healthcare_rn_workforce.md` | Persona table + any YAML echo | Number matches BLS (or corrected) with citation per §A item 8 |
| RCG-009 | `unified_personas.md` (L68) | "First Responders — Niche ($2.5M workforce)" | MEDIUM | `US BLS police firefighters EMT employment total 2024 2025 definition` | default | Definition + sum + URL | `artifacts/research/citations/RCG-009_first_responders_workforce.md` | Persona table | Figure sourced or relabeled "illustrative" per §A item 9 |
| RCG-010 | `docs/PEARL_NEWS_WRITER_SPEC.md` (L117) | Dhaka floods / 40,000 students lede | MEDIUM | `Bangladesh Dhaka floods school attendance [year] news source OR confirm composite` | default (add Bangladesh keywords) | Real event + URLs **or** "composite example" ruling | `artifacts/research/citations/RCG-010_dhaka_floods_lede.md` | Lede example block | Labeled factual **or** explicitly fictional composite per §A item 10 |
| RCG-011 | `docs/PEARL_NEWS_WRITER_SPEC.md` (L121) | "Amara Odhiambo" Nairobi climate organizer | MEDIUM | `"Amara Odhiambo" Nairobi climate` + composite fictional labeling best practice | default | Real person + consent/public record **or** rename + composite label | `artifacts/research/citations/RCG-011_nairobi_composite.md` | Youth feature lede example | Same as §A item 11 |
| RCG-012 | `config/catalog_planning/brand_archetype_registry.yaml` (L27–30) | `emotional_token_global_caps` reset/clarity/calm numeric caps | MEDIUM | `audiobook marketing keyword density caps emotional language A/B OR competitor benchmark` | default | Rationale doc: evidence vs engineering default | `artifacts/research/citations/RCG-012_emotional_token_caps.md` | YAML `_source:` (see §6) + registry comment | Caps justified or marked provisional per §A item 12 |
| RCG-013 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` | Twelve personas as segments without validation source | MEDIUM | `self-help audiobook audience segmentation validation Pew Edison syndicated` | default | Source list for segment model | `artifacts/research/citations/RCG-013_persona_segment_validation.md` | Prompts doc + provenance block | Provenance block filled per §A item 13 |
| RCG-014 | `docs/research/MARKETING_DEEP_RESEARCH_PROMPTS.md` | "$2.22B 2024, 13% growth, 51% US adults listened" | MEDIUM | `APA audiobook industry report 2024 2.22 billion` | default | APA (or correct) URL + quote bounds | `artifacts/research/citations/RCG-014_apa_audiobook_stats.md` | Prompt text + `config/research/marketing_feed_sources.yaml` notes | Inline citation in prompt per §A item 14 |
| RCG-015 | `config/recommender/` | Scoring weights provenance | MEDIUM | `recommendation system hybrid weights calibration A/B benchmark` | default | Provenance memo: internal vs published | `artifacts/research/citations/RCG-015_recommender_weights.md` | `config/recommender/*.yaml` when present | Each weight block has `_source:` or "internal calibration" per §A item 15 |
| RCG-016 | `config/authoring/pen_name_teacher_profiles.yaml` | Audience assumptions uncited | MEDIUM | `audiobook listener demographics psychographics 2024 2026` | default | Cited demographic anchors | `artifacts/research/citations/RCG-016_teacher_profile_audience.md` | YAML headers or `_source:` | Representative rows documented per §A item 16 |
| RCG-017 | `config/brand_registry.yaml` | Archetype taxonomy unsourced | MEDIUM | `brand archetype Jung Pearson applied publishing 2024` | default | Framework citations + usage note | `artifacts/research/citations/RCG-017_brand_archetype_taxonomy.md` | `config/brand_registry.yaml` | Taxonomy tied to named framework or internal per §A item 17 |
| RCG-018 | `specs/PHOENIX_V4_5_WRITER_SPEC.md` §4.3a, §4.7, §4.7a, §4.8 | PIVOT, TAKEAWAY, THREAD, PERMISSION slots — no craft/publishing research cited | MEDIUM | `nonfiction chapter structure pedagogy pivot recap thread permission craft bestseller` | default | 3–5 craft/publishing sources supporting slot design | `artifacts/research/citations/RCG-018_chapter_slot_craft.md` | Writer spec `## References` | Numbered refs + inline `[N]` in slot sections per §A item 18 |
| RCG-021 | `atoms/` (sampled) | Locale/persona facts uncited | MEDIUM | Per-atom locale: `[topic] [locale] demographic official statistics` | regional when `detect_region.py` says so | Per-locale citation bundle | `artifacts/research/citations/RCG-021_atoms_locale_<locale>.md` | Representative atom files + template | Pilot set (e.g. 10 atoms) has cite trail per §A item 21 |
| RCG-022 | `SOURCE_OF_TRUTH/teacher_banks/` (sampled) | Pedagogical claims uncited | MEDIUM | `instructional design persona audiobook engagement evidence` | default | Short bibliography for teaching claims | `artifacts/research/citations/RCG-022_teacher_bank_pedagogy.md` | Teacher bank docs / YAML | Pilot slots cited or hedged per §A item 22 |

### Batch 3 — LOW

| Task ID | File | Claim | Severity | Research query | Cascade | Expected output | Output path | Downstream consumer | Acceptance criteria |
|---------|------|-------|----------|----------------|---------|-----------------|-------------|---------------------|---------------------|
| RCG-019 | `omega/title_entropy/subtitle_patterns.yaml` | Subtitle pattern effectiveness | LOW | `audiobook subtitle conversion A/B testing academic OR industry` | default | Evidence summary or "no strong public A/B" | `artifacts/research/citations/RCG-019_subtitle_patterns.md` | YAML `_source:` | Patterns labeled evidence-based vs heuristic per §A item 19 |
| RCG-020 | `config/payouts/` | Tier sourcing | LOW | `KDP royalty tiers 2025 OR internal contract label` | default | Public policy cite **or** internal-only flag | `artifacts/research/citations/RCG-020_payout_tiers.md` | Payout YAML | Each tier: market cite or `internal_contract` per §A item 20 |

---

## §3 — Pipeline activation tasks (audit §B items 7–15)

**ID mapping:** RPA-001 = psychology … RPA-009 = marketing_sources, with **RPA-007 (feed ingest) first** in the dependency graph (§7).

| Task ID | Layer (audit §B) | Prerequisites | Command / workflow | Prompts required | Output directory | Downstream consumer | Acceptance criteria |
|---------|-------------------|---------------|---------------------|------------------|------------------|---------------------|---------------------|
| RPA-007 | Feed ingest / `artifacts/research/raw/` (item 13) | `config/research/youth_feed_sources.yaml` valid | `PYTHONPATH=. python scripts/research/fetch_feeds.py` **or** dispatch [`.github/workflows/research_feeds_ingest.yml`](../.github/workflows/research_feeds_ingest.yml) (`workflow_dispatch`) | N/A (fetch only) | `artifacts/research/raw/<date>/` | All downstream layers | Non-empty raw payload committed or artifact uploaded; manifest note with date per item 13 |
| RPA-008 | Youth snapshots (item 14) | RPA-007 complete | Manual: paste platform snippets per [docs/research/RESEARCH_FEED_SOURCES.md](./research/RESEARCH_FEED_SOURCES.md) **or** extend fetch script | Paste prompts TBD in `research/prompts/tasks/` | `artifacts/research/youth_feed_snapshots/` | RPA-001, RPA-002 | At least one dated snapshot file with provenance header per item 14 |
| RPA-001 | Psychology (item 7) | RPA-007; paste path from raw | `python scripts/research/run_research.py --prompt-id psychology --paste artifacts/research/raw/<date>/<file>.xml` | `system/psych_pulse_researcher.txt`, `tasks/psychology_task.txt`, `tasks/psychology_yaml_instruction.txt` | `artifacts/research/psychology/` | EI v2, editorial, Pearl News | Non-empty `.yaml` + `.reasoning.md` with provenance per item 7 |
| RPA-002 | Pain points (item 8) | RPA-007 | `python scripts/research/run_research.py --prompt-id pain_points --paste <raw>` | `system/econ_script_analyst.txt`, `tasks/pain_points_*.txt` | `artifacts/research/pain_points/` | Title engine HOOK atoms | Same per item 8 |
| RPA-003 | World events (item 9) | RPA-007 | `python scripts/research/run_research.py --prompt-id event_impact --paste <raw>` | `system/identity_conflict_researcher.txt`, `tasks/event_impact_*.txt` | `artifacts/research/world_events/` | Pearl News editorial, EI v2 | Same per item 9 |
| RPA-004 | Narrative (item 10) | RPA-001–RPA-003 recommended | **Not in `run_research.py` yet** — add `--prompt-id narrative` **or** manual Qwen two-pass per [CONTINUOUS_RESEARCH_PLAN.md](./research/CONTINUOUS_RESEARCH_PLAN.md) | **Missing** — extract Prompts 4.1–4.3 from [PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md](./research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md) into `research/prompts/` (§4) | `artifacts/research/narrative/` | Writer spec, structures | Non-empty cited YAML per item 10 |
| RPA-005 | Platform (item 11) | RPA-007 | Same gap as RPA-004 for platform dimension | **Missing** — Prompts 5.1–5.2 → files | `artifacts/research/platform/` | Distribution / marketing config | Non-empty output per item 11 |
| RPA-006 | Linguistic / semantic (item 12) | RPA-007 | Extend runner **or** manual pass | **Partial:** `system/semantic_trend_spotter.txt` exists; **missing** paired `tasks/semantic_trend_*.txt` | `artifacts/research/` (subdir TBD) | Pearl News vocabulary, title engine | Runnable task file + artifact per item 12 |
| RPA-009 | Marketing sources (item 15) | Optional: `config/research/marketing_feed_sources.yaml` | Extend `fetch_feeds.py --config` **or** separate ingest; then marketing deep research paste | [MARKETING_DEEP_RESEARCH_PROMPTS.md](./research/MARKETING_DEEP_RESEARCH_PROMPTS.md) | `artifacts/research/marketing_sources/` | Marketing config, brand registry | Non-empty extracts with citations per item 15 |

---

## §4 — Prompt completion tasks

**Inventory:** [docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md](./research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md) states **~47 prompts** across six dimensions; the markdown body enumerates **18 primary chain prompts** (`**Prompt X.Y**` headers). The repo has **12 files** under `research/prompts/` (6 `system/*.txt`, 6 `tasks/*`), wired to **only three** `run_research.py` IDs (`psychology`, `pain_points`, `event_impact`). **Gap:** 47 − 12 = **35 file equivalents** per audit §B item 23 (includes chained "Follow-up if shallow" blocks and validation steps not yet split into standalone files).

### §4.1 — Files present today

| Path | Role |
|------|------|
| `research/prompts/system/psych_pulse_researcher.txt` | psychology system |
| `research/prompts/system/econ_script_analyst.txt` | pain_points system |
| `research/prompts/system/identity_conflict_researcher.txt` | event_impact system |
| `research/prompts/system/theory_lens_researcher.txt` | **Unwired** in `run_research.py` |
| `research/prompts/system/platform_strategist.txt` | **Unwired** |
| `research/prompts/system/semantic_trend_spotter.txt` | **Unwired** (RPA-006 partial) |
| `research/prompts/tasks/psychology_task.txt` | psychology |
| `research/prompts/tasks/psychology_yaml_instruction.txt` | psychology YAML pass |
| `research/prompts/tasks/pain_points_task.txt` | pain_points |
| `research/prompts/tasks/pain_points_yaml_instruction.txt` | pain_points YAML pass |
| `research/prompts/tasks/event_impact_task.txt` | event_impact |
| `research/prompts/tasks/event_impact_yaml_instruction.txt` | event_impact YAML pass |

### §4.2 — Primary spec prompts still needing dedicated task/system files (per-dimension)

| Dimension | Spec prompt | Proposed `research/prompts/` files | Depends on RPA |
|-----------|-------------|--------------------------------------|----------------|
| 1 | 1.1 Trauma map | `tasks/dim1_prompt_1_1_task.txt`, `system/dim1_prompt_1_1_system.txt` (or split from monolithic `psychology_task`) | RPA-001 |
| 1 | 1.2 Gen Alpha | `tasks/dim1_prompt_1_2_task.txt` | RPA-001 |
| 1 | 1.3 Anxiety architecture | `tasks/dim1_prompt_1_3_task.txt` | RPA-001 |
| 1 | 1.4 Grief / injustice | `tasks/dim1_prompt_1_4_task.txt` | RPA-001 |
| 2 | 2.1 Problem landscape | `tasks/dim2_prompt_2_1_task.txt` | RPA-002 |
| 2 | 2.2 Invisible scripts | `tasks/dim2_prompt_2_2_task.txt` | RPA-002 |
| 2 | 2.3 Aspirations | `tasks/dim2_prompt_2_3_task.txt` | RPA-002 |
| 3 | 3.0 Three-ring template | `tasks/dim3_prompt_3_0_task.txt` | RPA-003 |
| 3 | 3.1 Example application | `tasks/dim3_prompt_3_1_task.txt` | RPA-003 |
| 4 | 4.1–4.3 Narrative | `tasks/dim4_prompt_4_1_task.txt` … `4_3` + `system/dim4_narrative_system.txt` | RPA-004 |
| 5 | 5.1–5.2 Platform | `tasks/dim5_prompt_5_1_task.txt`, `5_2` + `system/dim5_platform_system.txt` | RPA-005 |
| 6 | 6.1–6.3 Story intel | `tasks/dim6_prompt_6_1_task.txt` … `6_3` + `system/dim6_story_system.txt` | RPA-004–RPA-006 (inputs) |

### §4.3 — Remaining ~29 prompt slots (reconcile to 47)

| PC-ID | Description | Action | RPA / consumer |
|-------|-------------|--------|----------------|
| PC-001–PC-029 | **Chaining, "Follow-up if shallow," validation, and Part 3–4 operational prompts** embedded under each primary prompt in PEARL_NEWS_QWEN spec | Extract each into `research/prompts/tasks/validation/` or `followups/` with stable names (`dim1_1_1_followup_shallow.txt`, etc.) | Unblocks reliable YAML pass and automated retries for RPA-001–006 |

**Rule:** No new `run_research.py` `--prompt-id` until paired `system` + `task` + optional `yaml_instruction` files exist and schema checked against `research/prompts/schemas/README.md`.

---

## §5 — EI v2 KB activation

| Field | Value |
|-------|--------|
| **Current state** | `marketing_sources.enabled: false` in [config/quality/ei_v2_config.yaml](../config/quality/ei_v2_config.yaml) **L12–L13** |
| **KB location** | `artifacts/research/kb/entries.jsonl` (16 entries; lines must include `source_citation`) |
| **Task** | After RCG/marketing lexicon safety review: set `marketing_sources.enabled: true`; run `python scripts/ci/run_ei_v2_catalog_calibration.py` (or project-standard EI v2 dry-run) with logging |
| **Acceptance** | Next pipeline/compare run loads marketing path without crash; log shows KB/marketing merge path exercised; rollback = flip flag false |

*Note:* `research_kb` is already `enabled: true` (separate block). This task is **marketing_sources** only (audit §B item 24).

---

## §6 — Citation convention proposal

| Element | Specification |
|---------|----------------|
| **YAML `_source:` schema** | `_source: { url: "", study: "", date: "", note: "" }` (all string; `url` or `study` required for factual claims) |
| **Where** | Any YAML under `config/**` asserting statistics, market size, workforce counts, or effectiveness |
| **Specs / markdown** | `## References` at bottom; inline numbered `[1]` … `[N]` tied to References |
| **Migration trigger** | After **Batch 1** (RCG-001–005): add `_source:` to the five highest-impact configs: `brand_archetype_registry.yaml`, `unified_personas.md` companion YAML if any, `docs/BESTSELLER_STRUCTURES.md` (md uses References not `_source:`), `config/brand_registry.yaml`, `config/quality/ei_v2_config.yaml` (for KB/marketing provenance notes) |

---

## §7 — Dependency graph

```
feed ingest (RPA-007)
  → psychology layer (RPA-001) → EI v2 KB activation (§5)
  → pain_points layer (RPA-002) → title engine HOOK atoms
  → world_events layer (RPA-003) → Pearl News editorial
  → narrative layer (RPA-004) → writer spec
  → platform layer (RPA-005) → distribution config
  → linguistic layer (RPA-006) → Pearl News vocabulary
youth snapshots (RPA-008) → enriches RPA-001, RPA-002
marketing_sources (RPA-009) → brand / marketing YAML

Batch 1 citation research (RCG-001–005) → citation convention (§6) → config migration
Prompt completion (§4) → pipeline activation (§3)
```

---

## §8 — Estimated effort

| Unit | Minutes (default) | Notes |
|------|-------------------|--------|
| Deep research cascade session (RCG task) | 30 | Per `skills/deep-research/SKILL.md` tool chain |
| Web-search-only fallback | 10 | When all DR tools quota-exhausted |
| Local Qwen two-pass layer (RPA) | 45–90 | Ollama + YAML fix loop; varies by paste size |
| Prompt file extraction (PC batch) | 15–30 | Per prompt pair |

| Batch | Tasks | Approx. sessions | Wall-clock estimate (1 researcher) |
|-------|-------|------------------|-------------------------------------|
| Batch 1 | 5 | 5–7 | 3–4 h |
| Batch 2 | 15 | 15–20 | 8–12 h |
| Batch 3 | 2 | 2 | 1 h |
| RPA-007–009 + RPA-001–006 | 9 + runs | 2–3 days | Includes runner wiring for RPA-004–006 |
| §4 prompt completion | ~35 files | 3–5 days | Parallelizable |

---

## Cross-reference index (audit §A)

| RCG-ID | RESEARCH_AUDIT §A item # |
|--------|-------------------------|
| RCG-001 | 1 |
| RCG-002 | 2 |
| RCG-003 | 3 |
| RCG-004 | 4 |
| RCG-005 | 5 |
| RCG-006 | 6 |
| RCG-007 | 7 |
| RCG-008 | 8 |
| RCG-009 | 9 |
| RCG-010 | 10 |
| RCG-011 | 11 |
| RCG-012 | 12 |
| RCG-013 | 13 |
| RCG-014 | 14 |
| RCG-015 | 15 |
| RCG-016 | 16 |
| RCG-017 | 17 |
| RCG-018 | 18 |
| RCG-019 | 19 |
| RCG-020 | 20 |
| RCG-021 | 21 |
| RCG-022 | 22 |

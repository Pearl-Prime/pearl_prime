# Research Integration — Dev Spec (Pearl_PM / Pearl_GitHub)

**Purpose:** Define coordination and branch/PR work to wire **existing** research artifacts into configs, specs, and runtime toggles. **No new primary research** in this lane — only extraction, schema, `_source:` provenance, and merge hygiene.

**Authority:** [artifacts/research/RESEARCH_AUDIT_2026_03_30.md](../artifacts/research/RESEARCH_AUDIT_2026_03_30.md) — Section B (research produced but not implemented). Citation-gap remediation (Section A) and pipeline activation (Section B layers 7–15) are owned by [docs/RESEARCH_CITATION_GAP_DEV_SPEC.md](./RESEARCH_CITATION_GAP_DEV_SPEC.md) (Pearl_Research).

**Status:** Dev spec — execution via small PRs from `origin/main`.

**Owner lane:** Pearl_PM (coordination, workstreams) + Pearl_GitHub (branch, push-guard, PRs).

---

## §1 — Purpose and scope

This spec covers **integration** only: orphaned markdown research → YAML/config; partial marketing sub-deliverables → standalone artifacts or inline provenance; **EI v2 `marketing_sources` enablement**; **workstream registration**; **DOCS_INDEX** pointers; **PR sequencing**. It does **not** run `run_research.py`, web search, or Qwen layers — those belong to `RESEARCH_CITATION_GAP_DEV_SPEC.md` §3–§4.

**In scope:** Paths listed in §2–§5, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, `docs/DOCS_INDEX.md`.

**Out of scope:** Editing Section A uncited claims (RCG tasks); creating missing `research/prompts/` files (RPA); atom/teacher rewrites.

---

## §2 — Orphaned research → config integration (6 PRs)

Audit reference: **RESEARCH_AUDIT §B items 1–6**. Item **5** is **PARTIAL** (also referenced in `LOCALE_CATALOG_MARKETING_PLAN.md`); PR-RI-005 must **finish** YAML/config consumption, not only doc mention.

**`_source:` convention (all PRs in this section):** Every new or updated factual block in YAML MUST include a sibling `_source:` object:

```yaml
_source:
  file: "artifacts/research/<filename>.md"
  section: "<heading or line range>"
  note: "<what was extracted; no data beyond research text>"
  extracted_at: "YYYY-MM-DD"
```

If the repo later adopts URL/study fields (per citation-gap spec §6), extend this object in a follow-up PR without removing `file:`.

| PR ID | Audit §B | Research file (source) | Actionable extracts (non-exhaustive — re-read file during PR) | Target config / spec files | Branch name | Write scope (expected) |
|-------|----------|------------------------|---------------------------------------------------------------|----------------------------|-------------|-------------------------|
| **PR-RI-001** | item **1** | [artifacts/research/deepseek_bestseller_plan_2026_03_23.md](../artifacts/research/deepseek_bestseller_plan_2026_03_23.md) | JP/KR/CN/HK/SG/TW keyword table; VPN/tooling notes; phase structure; platform-per-market checklist | New or extended: `config/localization/asia_audiobook_research_brief.yaml` (create) OR sections in `config/localization/content_roots_by_locale.yaml` + `docs/LOCALE_CATALOG_MARKETING_PLAN.md` cross-links | `agent/research-integration-asian-bestseller-plan` | New YAML brief + `_source:`; optional index row in `docs/LOCALE_CATALOG_MARKETING_PLAN.md`; `docs/DOCS_INDEX.md` if new file |
| **PR-RI-002** | item **2** | [artifacts/research/deepseek_gap_fill_round2_2026_03_23.md](../artifacts/research/deepseek_gap_fill_round2_2026_03_23.md) | HK/SG market sizes (e.g. USD 18.5M → 54.58M 2033); platform URLs; consumer language prefs | `config/localization/` (locale extension or new `hk_sg_market_facts.yaml`); link from `LOCALE_CATALOG_MARKETING_PLAN.md` | `agent/research-integration-hk-sg-markets` | New/updated YAML under `config/localization/`; `_source:` per numeric claim |
| **PR-RI-003** | item **3** | [artifacts/research/kdp_global_ebook_strategy_2026_03_23.md](../artifacts/research/kdp_global_ebook_strategy_2026_03_23.md) | 13 Kindle store table; 70% vs 35% royalty rows; JPY tax note; KDP Select implications | New: `config/payouts/kdp_store_royalty_reference.yaml` OR extend `config/payouts/` README + structured YAML; **do not** overwrite contractual `payees.yaml` | `agent/research-integration-kdp-royalties` | `config/payouts/*.yaml` (new reference file) + `CHECKLIST.md` pointer |
| **PR-RI-004** | item **4** | [artifacts/research/rakuten_ai_bestseller_titles_2026_03_23.md](../artifacts/research/rakuten_ai_bestseller_titles_2026_03_23.md) **and** [artifacts/research/rakuten_ai_market_research_2026_03_23.md](../artifacts/research/rakuten_ai_market_research_2026_03_23.md) *(second file exists in repo but is not a separate audit row — merge scope here)* | APAC wellness title patterns; platform URLs for monitoring; market context from market_research file | `config/catalog_planning/` (e.g. `competitive_intel_apac_audio.yaml` new) or documented subsection + `_source` | `agent/research-integration-rakuten-apac` | New catalog-planning YAML + optional one table in `LOCALE_CATALOG_MARKETING_PLAN.md` |
| **PR-RI-005** | item **5** | [artifacts/research/deepseek_market_data_followup_2026_03_23.md](../artifacts/research/deepseek_market_data_followup_2026_03_23.md) | Asian audiobook CAGR bands; mental wellness USD sizing (e.g. 2.9B → 6.8B context per file) | Same YAML family as RI-002 + **ensure** `docs/LOCALE_CATALOG_MARKETING_PLAN.md` numbers either **link** to YAML keys or carry `_source` footnotes | `agent/research-integration-asian-market-followup` | `config/localization/` + `LOCALE_CATALOG_MARKETING_PLAN.md` (de-dupe vs RI-002) |
| **PR-RI-006** | item **6** | [artifacts/research/web_search_gap_fill_2026_03_23.md](../artifacts/research/web_search_gap_fill_2026_03_23.md) | Taiwan (Readmoo, Kobo TW); China Ximalaya stats; ISBN/CSBN; VAT rates | `config/localization/` (TW/CN compliance snippet YAML); `config/payouts/` or governance doc for tax **reference** only | `agent/research-integration-tw-cn-compliance` | New YAML under `config/localization/` + provenance; no invented VAT — quote research |

### Per-PR checklist (all of §2)

| Field | Requirement |
|-------|-------------|
| **Base** | `git fetch origin && git checkout -b <branch> origin/main` |
| **Acceptance** | At least one downstream file contains extracted facts; each fact traceable via `_source.file` to the research markdown |
| **Review** | Reviewer confirms no numbers/platforms invented beyond research text; hedging preserved where research hedges |
| **Tests** | YAML lint / `check_docs_governance` if docs touched; no new Python required |

---

## §3 — Partial research → standalone outputs (5 tasks)

Audit reference: **RESEARCH_AUDIT §B items 16, 17, 20, 21, 22** — sub-deliverables **1, 2, 5, 6, 7** of `MARKETING_DEEP_RESEARCH_PROMPTS.md`. Item **18** (sub-deliverable 3) and **19** (sub-deliverable 4) are **FULL** per audit — out of scope here.

| Task | Audit §B | Sub-deliverable | Current state | Recommended approach | Output path | Acceptance |
|------|----------|-----------------|---------------|---------------------|-------------|--------------|
| **RIT-P01** | **16** | 1 — GTM & funnel | Embedded in `brand_archetype_registry.yaml` | **A:** Extract to `artifacts/research/marketing_sources/gtm_funnel_by_brand.md` with provenance header + bullet mapping to YAML keys | `artifacts/research/marketing_sources/gtm_funnel_by_brand.md` | Standalone file lists brand keys + research paraphrase; YAML gets `_source: { file: ... }` on densest blocks OR comment anchors `# source: RIT-P01` |
| **RIT-P02** | **17** | 2 — Emotional vocabulary | Embedded in registry | **A:** `artifacts/research/marketing_sources/emotional_vocabulary_caps.md` | same dir | Same as RIT-P01 |
| **RIT-P03** | **20** | 5 — Duration bands | Embedded | **B:** Prefer **inline** `_source` on `duration`/listening fields in YAML — fewer drift paths | `config/catalog_planning/brand_archetype_registry.yaml` | Each band claim has `_source` or adjacent comment with file+date |
| **RIT-P04** | **21** | 6 — Cover design language | Embedded | **A:** Standalone `cover_design_language_by_audience.md` in `artifacts/research/marketing_sources/` | same dir | Reviewer can read without spelunking 2k-line YAML |
| **RIT-P05** | **22** | 7 — Pricing topology | Embedded; overlaps `config/payouts/` | **B:** `_source` on pricing-related keys in registry **+** pointer to `config/payouts/` for operational tiers | registry + payouts README | No contradiction between narrative research and payee contracts |

**Why A vs B:** Use **standalone markdown** when the material is **narrative / multi-paragraph** (GTM, cover). Use **inline `_source:`** when the material is **dense key–value** already living in YAML (duration bands, pricing knobs).

**Pearl_PM rule:** These five tasks can ship in **one** PR `agent/research-integration-marketing-partials` or five micro-PRs — prefer **one** if merge conflicts on `brand_archetype_registry.yaml` are likely.

---

## §4 — EI v2 KB activation (`marketing_sources`)

| Field | Detail |
|-------|--------|
| **What** | Set `marketing_sources.enabled` from `false` to `true` |
| **Where** | [config/quality/ei_v2_config.yaml](../config/quality/ei_v2_config.yaml) — block `marketing_sources:`, key `enabled:` (currently line **13**) |
| **Pre-check** | Validate [artifacts/research/kb/entries.jsonl](../artifacts/research/kb/entries.jsonl): one JSON object per non-empty line; each object has **`source_citation`** non-empty (`wc -l` + jsonl scan). *As of 2026-03-30 the file has **15** entries; if the audit expected 16, reconcile with RESEARCH_AUDIT §B item 24 before merging PR-RI-KB.* |
| **Post-check** | Run `PYTHONPATH=. python3 -m pytest tests/test_ei_v2_hybrid.py -q` (regression); run one catalog plan path that loads `load_ei_v2_config()` and assert `marketing_sources.enabled` is True; capture log or artifact proving KB path resolved (`kb_path` under `research_kb` remains `artifacts/research/kb`) |
| **Branch** | `agent/ei-v2-kb-activation` |
| **PR ID** | **PR-RI-KB** |
| **Write scope** | `config/quality/ei_v2_config.yaml` + PR description with before/after + link to audit §B item **24** |
| **Acceptance** | Flag `true`; no crash on learner init with empty optional marketing file paths; if `source_path: marketing_deep_research` missing files, document fallback behavior or add stub path in same PR |
| **Rollback** | Single commit revert: set `enabled: false` |

---

## §5 — Workstream registration

Append rows to [artifacts/coordination/ACTIVE_WORKSTREAMS.tsv](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv) (tab-separated). **Pearl_PM** updates status when slices complete.

| workstream_id | owner_agent | task | subsystem | branch | base_ref | status | authority_doc | blockers |
|---------------|-------------|------|-----------|--------|----------|--------|---------------|----------|
| `ws_research_citation_gaps_20260330` | Pearl_Research | Close 22 citation gaps + RPA pipeline per RESEARCH_CITATION_GAP_DEV_SPEC | research / docs | — | origin/main | active | docs/RESEARCH_CITATION_GAP_DEV_SPEC.md | RCG/RPA task execution (not integration PRs) |
| `ws_research_integration_20260330` | Pearl_PM / Pearl_GitHub | Wire §B orphaned + partial outputs per this spec | config / localization / payouts / catalog | `agent/research-integration-*` | origin/main | active | docs/RESEARCH_INTEGRATION_DEV_SPEC.md | none |
| `ws_ei_v2_kb_activation_20260330` | Pearl_GitHub | PR-RI-KB: enable marketing_sources | EI v2 | `agent/ei-v2-kb-activation` | origin/main | active | docs/RESEARCH_INTEGRATION_DEV_SPEC.md §4 | Pre-check KB jsonl |
| `ws_research_pipeline_activation_20260330` | Pearl_Research | Run generational layers + feed ingest per RESEARCH_CITATION_GAP_DEV_SPEC §3 | artifacts/research/* | — | origin/main | blocked | docs/RESEARCH_CITATION_GAP_DEV_SPEC.md | ws_research_citation_gaps_20260330 planning + prompts |

*(Rows are also appended to the TSV file in-repo.)*

---

## §6 — PR sequence and dependencies

```text
Parallel (no cross-merge dependency):
  PR-RI-001 … PR-RI-006   (orphaned markdown → config) — avoid touching same YAML in same PR where possible
  PR-RI-KB                (single-file flag flip + evidence)

After Pearl_Research lands citation batches (separate spec):
  PR-RI-CITE-001 … PR-RI-CITE-005   (HIGH fixes → docs/unified_personas/BESTSELLER_STRUCTURES — not in this spec’s write scope)
  PR-RI-CONVENTION                  (repo-wide _source migration — governance)

Partial marketing tasks (§3):
  PR-RI-PARTIAL (optional single PR) — after or parallel to PR-RI-001–006 if no YAML overlap conflicts

Merge order recommendation:
  1. PR-RI-003 (payouts reference) — isolated
  2. PR-RI-001, RI-002, RI-005, RI-006 — localization family (merge RI-005 after RI-002 if same file edited)
  3. PR-RI-004 — catalog planning
  4. PR-RI-KB — config flag (independent)
  5. PR-RI-PARTIAL — registry touches last if multiple agents touched catalog planning
```

**Blockers:** PR-RI-005 **should not** duplicate numeric facts already landed in PR-RI-002 — **coordinate** or **single combined localization PR** if reviewer prefers.

---

## §7 — Golden branch pattern compliance

Every PR:

```bash
git fetch origin
git checkout -b agent/<branch-name> origin/main
# … edits …
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
git push -u origin agent/<branch-name>
```

- Never branch from `codex/*`.
- Never push to `main` directly if policy forbids (preflight will warn).

---

## §8 — DOCS_INDEX.md updates

Add to **task table** (top “Where to go”):

| Task | Where to go |
|------|-------------|
| **Research audit (gaps + orphans)** | [artifacts/research/RESEARCH_AUDIT_2026_03_30.md](../artifacts/research/RESEARCH_AUDIT_2026_03_30.md) |
| **Research → config integration PRs** | [docs/RESEARCH_INTEGRATION_DEV_SPEC.md](./RESEARCH_INTEGRATION_DEV_SPEC.md) (this file) |
| **Citation + pipeline research tasks** | [docs/RESEARCH_CITATION_GAP_DEV_SPEC.md](./RESEARCH_CITATION_GAP_DEV_SPEC.md) — ⚠️ *Pearl_Research: create if not present* |

Add to **[Marketing & deep research (document all)](#marketing--deep-research-document-all)** table (after Marketing deep research prompts row):

| **Research audit 2026-03-30** | [artifacts/research/RESEARCH_AUDIT_2026_03_30.md](../artifacts/research/RESEARCH_AUDIT_2026_03_30.md) — Two-sided audit: Section A uncited claims; Section B unimplemented research. |
| **Research integration (PM/GitHub)** | [docs/RESEARCH_INTEGRATION_DEV_SPEC.md](./RESEARCH_INTEGRATION_DEV_SPEC.md) — PR-RI-* slices, EI v2 KB activation, partial marketing extraction. |
| **Research citation gap (Pearl_Research)** | [docs/RESEARCH_CITATION_GAP_DEV_SPEC.md](./RESEARCH_CITATION_GAP_DEV_SPEC.md) — RCG/RPA task IDs; citation and pipeline activation tasks. |

Add to **Document all — complete inventory** path list (marketing subsection) the three paths above with ✓ or ⚠️ for citation gap spec.

---

## §9 — Closeout template

Each integration PR closeout states: PR ID, files changed, `_source:` samples, audit §B item numbers satisfied, reviewer name, merge commit.

---

*Last updated: 2026-03-30 — written per Pearl_PM/Pearl_GitHub integration prompt; audit authoritative for counts.*

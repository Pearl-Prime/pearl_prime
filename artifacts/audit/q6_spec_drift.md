# Q6 — Spec vs Code Drift Audit

**Audit date:** 2026-04-29
**Scope:** spot-check of ~14 major specs against code/config/CI reality.
**Method:** for each spec, 2-4 load-bearing claims selected, then verified by reading the cited code path. Drift = claim diverges from reality.

---

## A. Drift summary table

| spec | claim | code path | verdict | severity | phase_tag |
|---|---|---|---|---|---|
| `docs/BRANCH_PROTECTION_REQUIREMENTS.md:9-15` | "For `main`, require exactly these four status-check contexts: Core tests, Release gates, EI V2 gates, Change impact" | `gh api repos/Ahjan108/phoenix_omega_v4.8/rulesets/13451138` | DRIFT — only `Verify governance` is required; `Core tests`, `Release gates`, `EI V2 gates`, and `Change impact` are NOT required | **CRITICAL** | Phase-Governance |
| `docs/BRANCH_PROTECTION_REQUIREMENTS.md:9` | "branch protection on main" | `gh api repos/:owner/:repo/branches/main/protection` → 404 "Branch not protected" | DRIFT — classic branch-protection API returns NOT PROTECTED; only ruleset coverage exists | **CRITICAL** | Phase-Governance |
| `docs/BRANCH_PROTECTION_REQUIREMENTS.md` (PR review reqs implied via GITHUB_GOVERNANCE) | (any reviewer / linear-history rules) | ruleset 13451138: `required_approving_review_count: 0`, `require_code_owner_review: false` | DRIFT — zero required reviewers; bypass actor "RepositoryRole" can `bypass_mode: always` | **CRITICAL** | Phase-Governance |
| `config/governance/required_checks.yaml:18-22` (machine authority) | `["Core tests", "Release gates", "EI V2 gates", "Verify governance"]` | live ruleset only requires `Verify governance` | DRIFT — machine config out of sync with live ruleset | **CRITICAL** | Phase-Governance |
| `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:15-21` | "All book generation MUST flow through `scripts/run_pipeline.py --pipeline-mode spine`" | `scripts/run_pipeline.py:1441-1444` — choices `["registry","spine"]`, **default=`registry`** | DRIFT — default mode is `registry` (legacy), not `spine` | **CRITICAL** | Phase-Cleanup |
| `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:163-168` (Cleanup table §11) | `template_expand/`, `template_expand2/`, `legacy_template_loader.py`, `run_legacy_template_packet_pilot.py` slated for deletion in Phases C/D | trees still present: `template_expand/`, `template_expand2/`, `phoenix_v4/planning/legacy_template_loader.py`, `scripts/pilot/run_legacy_template_packet_pilot.py` | DRIFT — Phases C+D have NOT landed; "pending review" matches §11 status table | **MEDIUM** | Phase-Cleanup |
| `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:30-37` | "12 chapters / 10 sections / 5 variants per section" | `phoenix_v4/planning/story_planner.py:57-64` confirms 4 phases × 3 chapters = 12 ch ✓; `phoenix_v4/planning/beatmap_compile.py:41-52,103` confirms 10 sections ✓; **5 variants is NOT enforced** — `phoenix_v4/planning/enrichment_select.py:106,827`: `_MIN_VARIANTS = 3` (minimum, not target); `scripts/registry/validate_variant_coverage.py:93` "5 remains an optional ceiling" | DRIFT — variants minimum is 3, not 5; spec overstates the floor | **HIGH** | Phase-Quality |
| `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:55-66` | Atom stacking: "persona first → registry always → teacher third → story where scheduled" | `phoenix_v4/planning/enrichment_select.py:8,945-984` — confirms practice_library before registry for EXERCISE; teacher overlay logic present | PARTIAL — code matches for non-EXERCISE; EXERCISE slot rule deviates ("teacher → practice_library → FAIL") which is documented at §4 footnote but contradicts simple "registry always" claim | **LOW** | Phase-Quality |
| `docs/PEARL_PRIME_RELEASE_CONTRACT.md:23-29` | "canonical required checks remain: Core tests, Release gates, EI V2 gates, Change impact" | live ruleset 13451138 only requires `Verify governance`; `change-impact.yml` workflow still exists; required_checks.yaml replaced "Change impact" with "Verify governance" 2026-04-17 | DRIFT — release contract still names retired check `Change impact`; out of sync with `required_checks.yaml` | **HIGH** | Phase-Governance |
| `docs/PEARL_PRIME_RELEASE_CONTRACT.md:55-65` | release workflow must run rigorous test, real pipeline canary, rollback smoke, write `pearl_prime_release_evidence.json` | `.github/workflows/release-gates.yml:46-89` confirms `Production readiness gates`, `Rigorous system test`, `Pipeline canary (20 books)`, `Release smoke`, `Rollback smoke` (all gated `if: github.event_name != 'pull_request'`) | OK — all five gates wired; runs on push/schedule/dispatch only, not on PRs | OK | — |
| `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (Pearl_Editor scoring + chapter_composer + bestseller_editor) | `phoenix_v4/quality/chapter_flow_gate.py`, `phoenix_v4/qa/book_pass_gate.py`, `phoenix_v4/qa/bestseller_editor.py`, `phoenix_v4/quality/bestseller_craft_gate.py` | all four files exist | OK | OK | — |
| `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md §5A` | `requested_topic_id` and `canonical_topic_id` in plan output | `scripts/run_pipeline.py:1817,3079-3083` writes both fields | OK | OK | — |
| `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md §5B` | First-class `--location` CLI flag and `LocationGroundingError` | `scripts/run_pipeline.py:1397` (`--location` flag), `phoenix_v4/rendering/book_renderer.py:152,2006` (`LocationGroundingError` raised) | OK | OK | — |
| `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md §1.6` | one-hour `standard_book` runtime target = 9k–11k words | sentinel doc records 4,798 words actual; `--skip-word-count-gate` available; spec status remains "execution spec" not "merged hardening" | UNRESOLVED — workstream still open per spec's own §6 ordering | **MEDIUM** | Phase-Hardening |
| `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §11 / §3` | added `validate_arc_alignment.py`, `validate_engine_resolution.py`; deleted dynamic-range / volatility / entropy validators | `phoenix_v4/qa/validate_arc_alignment.py`, `phoenix_v4/qa/validate_engine_resolution.py` exist; old validators absent from tree | OK | OK | — |
| `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §2.2` | "300–500 arcs" needed | `config/source_of_truth/master_arcs/` count = 532 yaml | OK — exceeds estimate | OK | — |
| `specs/PHOENIX_V4_5_WRITER_SPEC.md §4.5` | "Teacher Mode: `teacher_banks/<teacher_id>/approved_atoms/EXERCISE/*.yaml`" | actual canonical path is `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/...` (per `docs/SYSTEMS_V4.md:103,200` and tree); root-level `teacher_banks/` does NOT exist | DRIFT — spec uses wrong relative path; would break copy-paste | **MEDIUM** | Phase-Docs |
| `specs/PHOENIX_V4_5_WRITER_SPEC.md §4.5 + §20` | three-source rule wired (TEACHER_DOCTRINE / EXERCISE / ATOM) | `phoenix_v4/planning/enrichment_select.py:95` defines `TEACHER_DOCTRINE` injection markers; `:945-984` codifies teacher / practice_library / registry stacking | OK | OK | — |
| `specs/AI_MANGA_PIPELINE_SUMMARY.md` (Seven Agents: Director / Visual Identity / Genre / Story Architect / Chapter Writer / Visual+Lettering / Layout / QC) | `phoenix_v4/manga/{chapter,qc,series,llm,runner}/`, `scripts/manga/*` (~30 scripts), `phoenix_v4/manga/visual_prompt_compiler.py`, `chapter/lettering_from_script.py`, `chapter/visual_from_script_v3.py` | most agents have code paths; Story Architect / Director appear distributed across `story_strategy_loader.py`, `series/`, generators | PARTIAL — pipeline largely present; no single "Director Agent" file but the catalog/series generators cover that role | **LOW** | Phase-Manga |
| `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` schema docstring 2.1.0 ("15-genre allow-list") | `scripts/manga/generate_series_plans_from_catalog.py:48-56` — VALID_GENRES has **23 entries** (10 legacy + 13 strategic); same in `schemas/manga/series_plan.schema.json` | DRIFT (semantic) — count is 23 (10 legacy retained + 13 new), schema description says "15 strategic slugs" plus 10 legacy = 25; spec D-8 says expand "to 12 strategic shells (plus bonuses)"; different docs say different totals (12, 15, 23) | **HIGH** | Phase-Manga |
| `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §10` | "all 9 OQ resolutions executed (OQ-7,8,9 via PRs #684/#685/#686; OQ-1..OQ-6 captured in Phase 2X execution PRs)" | spec records v1.1 refresh "Operator-approved through OQ-9. Phase 2X.1 atomic PR ready to author when Pearl_Dev capacity opens" — 132 series_plan, 716 book_plan **deletion (D-20 atomic)** still pending | DRIFT — OQ resolutions captured in spec but the atomic Phase 2X.1 cutover (the actual code/data flip) has NOT landed yet | **HIGH** | Phase-Manga |
| `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §2.4 / D-18` | 5 locales rendered (en_US, ja_JP, ko_KR, zh_TW, zh_CN); routing matrix 5×15 = 75 cells | `config/source_of_truth/manga_series_plans/` has 5 locale subdirs ✓ | OK | OK | — |
| `docs/AUDIOBOOK_PIPELINE_SPEC.md §12 Gap Tracker` | "11 of 12 items complete. One remaining blocker: staging run." | `scripts/audiobook_script/run_comparator_loop.py`, `run_regression.py`, `run_staging.sh`, `scripts/release/audiobook_rollback.sh` exist; `scripts/audiobook/` only has `__init__.py` + `generate_showcase_bundle.py` | PARTIAL — comparator loop wiring matches spec (under `scripts/audiobook_script/`, NOT `scripts/audiobook/`); staging-run blocker unverified | **MEDIUM** | Phase-Audiobook |
| `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md` | podcast pipeline at `scripts/podcast/` | `scripts/podcast/`: `assemble_podcast_episode.py`, `generate_podcast_feed.py`, `render_podcast_audio.py`, `run_podcast_pipeline.py`, `upload_podcast_to_r2.py` | OK | OK | — |
| `docs/PEARL_NEWS_WRITER_SPEC.md` | `pearl_news/prompts/expansion_system.txt`, `pearl_news/pipeline/quality_gates.py`, `pearl_news/config/editorial_firewall.yaml` | tree confirms: `pearl_news/pipeline/quality_gates.py`, `pearl_news/config/editorial_firewall.yaml`; daily/fill-qwen workflows present | OK | OK | — |
| `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §1-§2` | `config/freebies/`, `phoenix_v4/planning/freebie_planner.py`, `phoenix_v4/freebies/freebie_renderer.py`, `phoenix_v4/tools/generate_html_freebie.py` | all present; `funnel/burnout_reset/`, `somatic_exercise_freebee_apps/` (50+ HTML apps) present | OK | OK | — |
| `docs/SYSTEMS_V4.md` (teacher_banks reference) | `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/` with `approved_atoms/`, `doctrine/`, `synthetic_atoms/`, `reports/` | tree: `SOURCE_OF_TRUTH/teacher_banks/{adi_da, ahjan, joshin, junko, maat, master_feung, master_sha, master_wu}` (8 teachers) | OK | OK | — |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` (sections 1-18 + §0 Pearl Star + 1a/1b/1c/1d) | each documented service has env vars in `scripts/ci/integration_env_registry.py` | DeepSeek (`DEEPSEEK_API_KEY`) and Google AI Studio (`GOOGLE_AI_API_KEY`) **are in code registry** but **not documented** in INTEGRATION_CREDENTIALS_REGISTRY.md sections 1a-1d (only Together/Groq/xAI/Qwen documented; DeepSeek+Gemini cited only in `AGENT_QWEN_API_KEY_LANE.md`-adjacent flows). R2 (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET`) **in code, not in doc**. Plaid documented (§9) but no env entry (uses YAML — consistent). | DRIFT — registry doc misses DeepSeek, Google AI Studio (Gemini), and R2 (4 env vars); reverse direction OK (no doc-only services missing from code) | **HIGH** | Phase-Docs |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md §0` Pearl Star | `PEARL_STAR_IP`, `COMFYUI_URL` required | `scripts/ci/integration_env_registry.py` marks them `required=True` | OK | OK | — |
| `docs/PEARL_PRIME_RELEASE_CONTRACT.md "Workers Builds: pearl-prime is non-blocking"` | excluded from `non_blocking_checks` | `config/governance/required_checks.yaml:33` `non_blocking_checks: ["Workers Builds: pearl-prime"]` | OK | OK | — |

---

## B. CRITICAL drift items (full detail)

### B1. main is effectively unprotected: zero required reviewers, only one required check, bypass actor present

**Spec claim** (`docs/BRANCH_PROTECTION_REQUIREMENTS.md:9-15`):
> "For `main`, require exactly these status-check contexts: **Core tests**, **Release gates**, **EI V2 gates**, **Change impact**."

**Spec claim** (`docs/PEARL_PRIME_RELEASE_CONTRACT.md:23-29`):
> "The canonical required checks remain: `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`."

**Spec claim** (`config/governance/required_checks.yaml:18-22`, machine authority):
```yaml
required_checks:
  - "Core tests"
  - "Release gates"
  - "EI V2 gates"
  - "Verify governance"
```

**Code/live reality** (`gh api repos/Ahjan108/phoenix_omega_v4.8/rulesets/13451138`):
```json
"rules": [
  {"type": "deletion"},
  {"type": "non_fast_forward"},
  {"type": "pull_request", "parameters": {"required_approving_review_count": 0, ...}},
  {"type": "required_status_checks", "parameters": {
    "required_status_checks": [{"context": "Verify governance"}]
  }},
  {"type": "required_linear_history"}
],
"bypass_actors": [
  {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
]
```

`gh api repos/:owner/:repo/branches/main/protection` returns `404 Branch not protected` (classic protection API).

**Drift summary:** Three different documents claim 4 distinct required checks (two of those four are different names: docs say `Change impact`, the in-repo machine config says `Verify governance`). Reality is **only `Verify governance` is required**. `Core tests`, `Release gates`, and `EI V2 gates` are NOT enforced as merge-blocking. Required reviewer count is **0**. A bypass role can always bypass.

**Why this is critical:** The repo's own root CLAUDE.md says "NEVER merge a PR that deletes more than 50 files without explicit owner approval" and points to PR #245 which deleted 20,006 files. That governance lives entirely in `Verify governance` workflow + manual reviewer attention. With 0 required reviewers and only 1 required check, the safety net is one CI workflow's correctness. The release-gates workflow runs `release/canary/rollback_smoke` only on `push: main` (not PR), so a PR that bypasses Verify governance ships unchecked.

**Phase tag:** `Phase-Governance`. **Severity:** CRITICAL.

### B2. Canonical pipeline default is the legacy mode the spec slates for deletion

**Spec claim** (`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:15-23`):
> "All book generation MUST flow through:
> ```
> scripts/run_pipeline.py --pipeline-mode spine ...
> ```
> Anything else (registry mode, template_expand legacy, pilot pipelines) is legacy and scheduled for deletion in the phased cleanup..."

**Code reality** (`scripts/run_pipeline.py:1438-1444`):
```python
ap.add_argument("--registry", default=None, help="Section registry YAML path ...")
ap.add_argument("--pipeline-mode",
    choices=["registry", "spine"],
    default="registry",
    help="Pipeline mode: 'registry' (section-registry fast-path, default) or "
         "...")
```

**Drift summary:** The canonical doc states spine mode is mandatory for all book generation; the actual default is `registry`. Any caller that omits `--pipeline-mode spine` (which is *most* call sites in the repo) silently runs the legacy fast-path. The §11 cleanup table marks Phase E ("`pipeline-mode=registry` branch deletion") as "pending review" — but the spec wording at §1 ("MUST flow through spine") suggests the flip already landed. It has not.

**Phase tag:** `Phase-Cleanup`. **Severity:** CRITICAL.

### B3. Required-checks contract is internally inconsistent and stale

Three sources disagree on the required check set:

| Source | Required checks |
|---|---|
| `docs/BRANCH_PROTECTION_REQUIREMENTS.md:9-15` | Core tests, Release gates, EI V2 gates, **Change impact** |
| `docs/PEARL_PRIME_RELEASE_CONTRACT.md:23-29` | Core tests, Release gates, EI V2 gates, **Change impact** |
| `config/governance/required_checks.yaml:18-22` | Core tests, Release gates, EI V2 gates, **Verify governance** (replaced 2026-04-17) |
| Live ruleset 13451138 | **Verify governance** only |

**Drift summary:** `required_checks.yaml` was updated 2026-04-17 to replace `Change impact` with `Verify governance` after change-impact workflow began returning empty job lists; the two markdown docs were not updated. The live ruleset, however, only requires `Verify governance` — it never honored the multi-check `required_checks` list at all. Pattern: spec → machine config → CI → ruleset is broken at every hop.

**Phase tag:** `Phase-Governance`. **Severity:** CRITICAL.

---

## C. HIGH drift items

### C1. PEARL_PRIME_RELEASE_CONTRACT names retired check "Change impact" as canonical

`docs/PEARL_PRIME_RELEASE_CONTRACT.md:23-29` still lists `Change impact` as one of the four canonical required checks. This was retired on 2026-04-17 per `config/governance/required_checks.yaml` comment because the workflow returned empty job lists for ~2 weeks and blocked PRs. The contract was not updated to match. **Severity:** HIGH. **Phase:** Phase-Governance.

### C2. "5 variants per section" claim overstates the floor

`docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:32` states "5 variants per section (selected deterministically by seed)." Code minimum (`phoenix_v4/planning/enrichment_select.py:106,827`) is `_MIN_VARIANTS = 3`; `scripts/registry/validate_variant_coverage.py:93` literal comment: `"5 remains an optional ceiling: sections may declare min_variants_required: 5"`. The deterministic selection is real; the floor is not 5. Spec misleads anyone trying to understand catalog scale-out math. **Severity:** HIGH. **Phase:** Phase-Quality.

### C3. INTEGRATION_CREDENTIALS_REGISTRY.md missing DeepSeek, Google AI Studio (Gemini), and Cloudflare R2 sections

`scripts/ci/integration_env_registry.py` declares these env vars (with notes pointing to upstream provider URLs), but `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` has no documented section for them:

- `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` — used by zh-CN/zh-TW translation per code
- `GOOGLE_AI_API_KEY`, `GEMINI_MODEL` — ja-JP translation, 1M tokens/day free
- `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET` — Cloudflare R2 storage

Doc claims to be "single canonical reference for every external service credential." It is not. Operators reading the doc will not know to provision these keys. **Severity:** HIGH. **Phase:** Phase-Docs.

### C4. MANGA_CATALOG_RECONCILIATION 23-genre VALID_GENRES vs spec wording "15 strategic slugs"

`scripts/manga/generate_series_plans_from_catalog.py:48-56` declares **23 VALID_GENRES** entries (10 legacy + 13 new). The schema description in `schemas/manga/series_plan.schema.json` says "v2.1 = 15-genre allow-list" then immediately enumerates 15 strategic slugs. Spec D-8 in `MANGA_CATALOG_RECONCILIATION_SPEC.md:113` says "expands from 10 to **12** strategic shells (plus bonuses)." The numbers cited across spec, schema description, and code (12 / 15 / 23) cannot all be right. Reader cannot confidently say "what is the supported genre count for new YAMLs?" without reading code. **Severity:** HIGH. **Phase:** Phase-Manga.

### C5. MANGA_CATALOG_RECONCILIATION Phase 2X.1 atomic deletion has not landed

Spec status: "Operator-approved through OQ-9. Phase 2X.1 atomic PR ready to author when Pearl_Dev capacity opens." Per D-3, D-4, D-5 the 132 stale `series_plan.yaml` and 716 `book_plan.yaml` files must be **atomically deleted** in a single PR (per OQ-4 hard cutover). Until that PR lands, the planner allow-list at code line 48 already accepts the new genres while the YAMLs remain pre-cutover. This is the "5-week red-CI window" that OQ-4 disposition (c) was supposed to *avoid* — yet the window is currently open. **Severity:** HIGH. **Phase:** Phase-Manga.

---

## D. MEDIUM / LOW drift (one-liners)

- **MEDIUM** `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` §11 cleanup phase A-F all "pending review" — `template_expand/`, `template_expand2/`, `phoenix_v4/planning/legacy_template_loader.py`, `scripts/pilot/run_legacy_template_packet_pilot.py` all still present. Phase-Cleanup.
- **MEDIUM** `PHOENIX_V4_5_WRITER_SPEC.md §4.5` writes `teacher_banks/<teacher_id>/...` (root-level path) but real path is `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/...`. Authoritative `SYSTEMS_V4.md` uses correct path. Spec-doc internal inconsistency. Phase-Docs.
- **MEDIUM** `PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md` §5F runtime truthfulness still open — sentinel run produces 4,798 words against `standard_book` 9k–11k target; spec is "execution spec" and still tracks as not-done. Phase-Hardening.
- **MEDIUM** `AUDIOBOOK_PIPELINE_SPEC.md` §12 Gap Tracker last item "Staging run + evidence pack" is "⚠ NOT RUN" — no evidence pack on disk. Phase-Audiobook.
- **LOW** `AI_MANGA_PIPELINE_SUMMARY.md` "Director Agent" has no single-file home; functionality is distributed across `scripts/manga/generate_series_plans_from_catalog.py` + `phoenix_v4/manga/series/`. Functional but not 1:1 with diagram. Phase-Manga.
- **LOW** `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md §4` atom stacking simple-list deviates for EXERCISE slot (teacher → practice_library → FAIL, no persona, no registry). Documented in `enrichment_select.py:936-984` but reader of the canonical doc would not infer this without going to code. Phase-Quality.

---

## E. Spec doc lifecycle drift

- **`docs/PEARL_PRIME_RELEASE_CONTRACT.md`** still references retired check name `Change impact`; should be updated to `Verify governance` per `config/governance/required_checks.yaml`.
- **`docs/BRANCH_PROTECTION_REQUIREMENTS.md`** likewise still names `Change impact`.
- **`PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`** marked "DRAFT — cleanup-phase baseline; will be finalized when legacy paths are removed" — accurate self-labeling, but the phased cleanup table at §11 has been "pending review" for 6+ days post 2026-04-24 publish.
- **`MANGA_AUTHOR_SYSTEM_SPEC.md`** referenced as "ARCHIVED" by `MANGA_CATALOG_RECONCILIATION_SPEC.md:118` (D-14) — verified absence not checked here, but D-12/D-14 archive moves are still listed as pending Phase 2X work.
- **`docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md`** (referenced in `docs/` listing) — confirms the operator already maintains a "specs vs reality" audit lane; this Q6 audit complements rather than duplicates.
- **No "supersedes" header missing** for the live specs sampled — the supersession chain (PHOENIX_OMEGA_V4_COMPLETE_SPEC → PHOENIX_ARC_FIRST_CANONICAL_SPEC → PHOENIX_V4_5_WRITER_SPEC) is well-marked.
- **Specs cited but missing:** none observed in the sample. `phoenix_v4/planning/format_plan.py` and `config/freeze_settings.yaml` are explicitly called out as "do not exist" in `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md:99-103` (honest spec acknowledging gap — not drift).

---

## F. Phase tag rollup

| Phase | Drift count |
|---|---|
| **Phase-Governance** | 4 (3 CRITICAL + 1 HIGH) |
| **Phase-Cleanup** | 2 (1 CRITICAL + 1 MEDIUM) |
| **Phase-Manga** | 3 (2 HIGH + 1 LOW) |
| **Phase-Quality** | 2 (1 HIGH + 1 LOW) |
| **Phase-Docs** | 2 (1 HIGH + 1 MEDIUM) |
| **Phase-Hardening** | 1 (MEDIUM) |
| **Phase-Audiobook** | 1 (MEDIUM) |
| **Phase-Audiobook/Podcast/PearlNews/Freebie/Manga code presence** | OK across the board |

---

## Severity totals

| Severity | Count |
|---|---|
| CRITICAL | 4 |
| HIGH | 5 |
| MEDIUM | 5 |
| LOW | 2 |
| OK (verified) | 12 |

---

## Pattern observation

The dominant pattern across all drift items: **specs were authored ahead of CI gates, and the gates either never got enforced (Phase-Governance) or never finished landing (Phase-Cleanup, Phase-Manga)**. The repo has high-quality architectural specs and high-quality implementation code, but the binding contract layer between them — branch protection rulesets, "phase pending review" tables, machine authority configs — is consistently a step or two behind. Three different documents disagree on which 4 status checks gate `main`, and the live ruleset honors none of those four lists; that's the audit's headline.

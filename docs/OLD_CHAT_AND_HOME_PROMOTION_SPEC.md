# Old Chat And Home Promotion Spec

**Purpose:** Turn the highest-value surviving material from `old_chat_specs/` and `/Users/ahjan/` into a small number of grounded enhancement lanes instead of leaving it as permanent backlog.

**Status:** Promotion spec and cleanup contract. This document is not a substitute for current authority docs; it is a routing and execution guide for deciding what to promote next.

**Primary sources:**
- `docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md`
- `old_chat_specs/README.md`
- `salvage/SALVAGE_EXTERNAL_SWEEP_2026_03_28.md`
- `salvage/SALVAGE_EXTERNAL_RECOVERY_PASS_2026_03_28.md`
- `salvage/SALVAGE_ENHANCE_CLEANUP_PLAN_2026_03_28.md`
- `salvage/SALVAGE_PROMOTION_QUEUE_2026_03_28.tsv`

---

## 1. Promotion Rules

Use these rules before promoting anything from `old_chat_specs/` or `/Users/ahjan/`:

1. Current repo authority beats historical notes.
2. Old chat material is intent and enhancement evidence, not current truth.
3. If a live repo file already covers the same function, update that file instead of creating a parallel one.
4. If a `/Users/ahjan/` file is already represented in the repo or in the 2026-03-28 archive, do not recreate it.
5. Prefer small promotion lanes with explicit acceptance criteria over broad “harvest everything” passes.
6. Do not revive retired subsystems just because the historical material is interesting.

---

## 2. Best Enhancement Candidates

| Priority | Candidate | Score | Owner lane | Why this is worth doing now |
|----------|-----------|-------|------------|-----------------------------|
| 1 | V4 structural function enforcement + visible fallback reporting | 11/12 | Pearl_Dev | Best fit between `old_chat_specs` insight and live code gaps; directly improves book quality and validation. |
| 2 | Brand admin + investor due diligence enhancement pass | 8/12 | Pearl_Writer + Pearl_Prez | Existing HTMLs and workbook already exist; strongest user-facing presentation lane from preserved material. |
| 3 | Pearl News Gen Z prompt hardening compare/promote | 8/12 | Pearl_Writer | Preserved candidate prompt pack matches current voice/prompt needs and appears not yet merged. |
| 4 | EI disclosure / positioning compare/promote | 7/12 | Pearl_Writer | Good fit for current EI messaging and landing/disclosure language. |
| 5 | Somatic narration guidance compare/promote | 6/12 | Pearl_Writer | Potentially useful as voice/style guidance, but must not resurrect the retired audiobook comparator lane. |

Items intentionally not prioritized in this spec:

- CJK manga asset bundle
- conversation-only cowork notes
- generic old chat recaps with no concrete promotion target

Those can remain preserved until a subsystem owner explicitly asks for them.

---

## 3. Dev Lane Spec

### Lane name

`old_chat_v4_enforcement_upgrade`

### Score

`11/12`

### Best source material

- `docs/AUDIT_OLD_CHAT_SPECS_VS_V4.md`
- `old_chat_specs/repository comparison overview.txt`
- `old_chat_specs/repo systems documentation.txt`
- `old_chat_specs/chat summary v4.txt`
- `old_chat_specs/dev 2 report analysis.txt`
- `old_chat_specs/latest systme docs.txt`

### Goal

Close the strongest still-open V4 governance gap identified in the old chat audit:

1. chapter emotional role exists, but content/function enforcement is still partial
2. placeholder or silence outcomes are visible in plan ids, but there is no single verification report
3. narrative-function diversity is still missing from the resolver/validator layer

### Current live files to use

- `phoenix_v4/planning/assembly_compiler.py`
- `phoenix_v4/planning/slot_resolver.py`
- `phoenix_v4/planning/arc_loader.py`
- `phoenix_v4/planning/capability_check.py`
- `phoenix_v4/qa/validate_compiled_plan.py`
- `config/format_selection/emotional_role_slot_requirements.yaml`
- `docs/BOOK_001_ASSEMBLY_CONTRACT.md`
- `tests/test_assembly_compiler.py`
- `tests/test_slot_resolver.py`
- `tests/test_arc_loader.py`

### Required deliverables

#### A. Verification report first

Add a machine-readable and human-readable verification artifact for assembled plans that reports:

- placeholder slots by chapter and slot type
- silence slots by chapter and slot type
- missing `STORY` coverage by chapter
- fallback events that were previously only implicit in plan ids

Acceptable shape:

- one script or validator extension
- one JSON artifact
- one concise Markdown summary artifact

#### B. Narrative function metadata

Add optional `narrative_function` support for eligible story or reflection atoms.

Minimum target functions:

- `recognition`
- `pattern_exposure`
- `cost_realization`
- `paradox`
- `micro_shift`
- `identity_integration`
- `continuation`

This does not require annotating every atom on day one. It does require a safe optional path that can be incrementally expanded.

#### C. Function × role enforcement

Enforce a first useful slice of role-aware eligibility:

- chapter emotional role constrains which narrative functions are eligible
- adjacent chapters should not reuse the same primary narrative function when avoidable
- validator or resolver should surface when the system had to violate the preferred diversity rule

#### D. Strict mode for visible fallback

Add a strict validation mode that can fail when placeholder or silence appears for protected slot types such as `STORY`.

This should be additive, not a surprise default for every existing pipeline path.

### Non-goals

- do not attempt the full 10K simulation lane in this tranche
- do not create a second assembly architecture
- do not rewrite current writer specs from scratch
- do not treat historical wording as executable law without mapping it to live files

### Acceptance criteria

1. A generated plan can emit a verification report that explicitly lists placeholder, silence, and missing-story events.
2. `narrative_function` exists as an optional metadata path and is exercised by tests.
3. At least one validator or resolver rule enforces function diversity or function × emotional-role compatibility.
4. Existing tests still pass, and new tests cover the added behavior.
5. `docs/BOOK_001_ASSEMBLY_CONTRACT.md` or the nearest live contract doc is updated to describe the new reporting/enforcement behavior.

### Implementation pointer (dev lane — in repo)

- Report builder: `phoenix_v4/qa/plan_verification_report.py` (`build_plan_verification_report`, `collect_narrative_function_map_for_plan`, `validate_narrative_function_rules`, `write_verification_artifacts`).
- Role × function config: `config/planning/narrative_function_role_compat.yaml`.
- STORY / block metadata: `NARRATIVE_FUNCTION:` parsed in `assembly_compiler._parse_narrative_metadata` and in `pool_index._parse_block_file_canonical`; teacher YAML `narrative_function` supported.
- Strict STORY validation: `validate_compiled_plan(..., strict_story_resolution=True)` in `phoenix_v4/qa/validate_compiled_plan.py`.
- Example emitter: `scripts/planning/emit_plan_verification_report.py --demo-fixture`.

---

## 4. Writer / Prez Lane Spec

### Lane name

`brand_admin_and_investor_enhancement`

### Score

`8/12`

### Best source material

- `old_chat_specs/chat_clause_marketing_close_prez.txt`
- `brand_onboarding_hub.html`
- `us_brand_admin_v32_briefing.html`
- `jp_brand_admin_v32_briefing.html`
- `writer_v32_quick_reference.html`
- `PHOENIX_OMEGA_INVESTOR_DD.xlsx`

### Goal

Turn the existing brand-admin and investor-facing materials into one cleaner, current, canonical package instead of leaving multiple preserved design intentions with no promotion pass.

### Current live files to use

- `brand_onboarding_hub.html`
- `us_brand_admin_v32_briefing.html`
- `jp_brand_admin_v32_briefing.html`
- `writer_v32_quick_reference.html`
- `PHOENIX_OMEGA_INVESTOR_DD.xlsx`

### Required deliverables

#### A. Canonical package decision

Decide which files are canonical for:

- onboarding hub
- US briefing
- JP briefing
- writer quick reference
- investor due diligence workbook

Do not create duplicate replacements if the existing files can be improved in place.

#### B. Presentation enhancement pass

Use the old presentation notes to improve:

- information hierarchy
- visual grouping
- narrative chaptering
- scanability for first-time brand admins
- investor-readability of the workbook and linked HTMLs

Constraints:

- keep the HTML static and WordPress-safe
- do not introduce framework dependence
- prefer one canonical visual language across the set

#### C. Numbers discipline for the workbook

For `PHOENIX_OMEGA_INVESTOR_DD.xlsx`:

- distinguish repo-backed facts from assumptions
- label any assumption rows clearly
- tie live numbers back to current repo artifacts, configs, or docs where possible
- remove or flag stale values that only came from historical presentation text

#### D. Cross-linking note

Add one short companion note or README if needed that tells future agents:

- which HTMLs are canonical
- what the workbook is for
- where numbers come from

### Non-goals

- do not rebuild all presentation assets from scratch unless the current files are proven unusable
- do not create another investor workbook with the same purpose
- do not import random HTMLs from `/Users/ahjan/phoenix_workspace_archive_2026_03_28/user_home_loose_outputs`

### Acceptance criteria

1. One canonical set of brand-admin HTMLs is identified and updated in place.
2. The investor workbook is either refreshed in place or explicitly marked archival if it cannot be trusted.
3. Any value that is not repo-backed is labeled assumption or estimate.
4. The updated files remain static, framework-free, and WordPress-safe.

---

## 5. Writer Content Compare Lanes From `/Users/ahjan/`

These are the best non-code candidates from the preserved user-home archive. They should be treated as compare/promote lanes, not auto-imports.

Resolution note (2026-07-09): the external archive referenced in this section was fully evaluated during the external-home cleanup pass. Canonical replacements and explicit rejections were recorded in `artifacts/audit/EXTERNAL_HOME_CLEANUP_2026_07_09.md` before deleting `/Users/ahjan/phoenix_workspace_archive_2026_03_28`.

### A. Pearl News Gen Z prompt pack

**Path:** `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/preserved_candidates/pearl_news_genz_prompts.md`

**Score:** `8/12`

**Use it for:**

- comparing against the current Pearl News prompt system
- promoting missing voice rules, rhythm rules, or topic framing rules

**Current live comparison targets:**

- `pearl_news/prompts/README.md`
- `docs/PEARL_NEWS_WRITER_SPEC.md`
- `pearl_news/pipeline/template_selector.py`

### B. EI disclosure / positioning framework

**Path:** `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/preserved_candidates/EI_Enlightened_Intelligence_Framework.docx`

**Score:** `7/12`

**Use it for:**

- disclosure language
- landing-page framing
- EI positioning consistency

**Current live comparison targets:**

- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- `docs/PRODUCTION_100_PLAN.md`
- current EI marketing or landing-page docs identified through `docs/DOCS_INDEX.md`

### C. Somatic narration guide

**Path:** `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/preserved_candidates/somatic_narration_guide.docx`

**Score:** `6/12`

**Use it for:**

- voice/tone guidance only if it fits an active current subsystem

**Do not use it to:**

- revive the retired audiobook comparator subsystem

---

## 6. `/Users/ahjan/` Cleanup Policy

### Keep as archive, not live source

These should remain archived unless deliberately promoted:

- `/Users/ahjan/phoenix_workspace_archive_2026_03_28/user_home_loose_outputs/*`
- `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/consumed_precursors/*`
- `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/preserved_candidates/*`

### Safe cleanup rules

1. Do not keep new Phoenix outputs loose in `/Users/ahjan/`, Desktop, or Downloads.
2. If a file is generated output only, move it to the dated archive area, not into the repo root.
3. If a file is canonical and actively used, move or keep it in the repo and document the canonical path.
4. If a file is preserved only for comparison, keep it in the archive and reference it from a spec or audit note.
5. Do not hard-delete preserved candidates until there is a canonical replacement and a record of the decision.

### Current cleanup decisions

- `brand_onboarding_hub.html`
- `us_brand_admin_v32_briefing.html`
- `jp_brand_admin_v32_briefing.html`
- `writer_v32_quick_reference.html`

These already exist in the repo and should be treated as live enhancement targets, not copied again from archive.

- `PHOENIX_OMEGA_INVESTOR_DD.xlsx`

This exists in the repo root and should be explicitly classified:

- keep and refresh as canonical, or
- move to a clearer canonical home later

Do not leave its status ambiguous.

---

## 7. Recommended Execution Order

1. Pearl_Dev implements the V4 enforcement/reporting tranche.
2. Pearl_Writer / Pearl_Prez runs the brand-admin + investor enhancement tranche.
3. Pearl_Writer compares the preserved Gen Z prompt pack against the live Pearl News prompt stack.
4. Pearl_Writer compares the EI disclosure framework.
5. Cleanup decisions are recorded so `/Users/ahjan/` does not accumulate a second unsorted archive.

---

## 8. Definition Of Done

This promotion pass is successful when:

1. the highest-value dev enhancement from `old_chat_specs` is implemented in live code and tests
2. the strongest brand-admin / investor materials are improved in place rather than duplicated
3. the best `/Users/ahjan/` candidate files are either promoted, explicitly archived, or explicitly rejected
4. future agents can see one clear answer for what is canonical and what is only historical

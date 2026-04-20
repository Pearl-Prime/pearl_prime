# Localization process for user-facing content
_Exported on 4/16/2026 at 19:27:49 GMT+8 from Cursor (3.1.15)_

---

**User**

Yes. If the goal is **all English content in the repo that is meant to be user-facing / pipeline content**, then the prompt should be broader than “atoms only,” but it still must **not translate Python code, YAML keys, IDs, paths, tests, or operational docs blindly**. Otherwise we’ll break the repo.

Use this prompt:

```text
Act as Pearl_Localization + Pearl_Dev for Phoenix Omega.

Read first:

docs/SESSION_UNITY_PROTOCOL.md
docs/PEARL_ARCHITECT_STATE.md
docs/DOCS_INDEX.md
artifacts/coordination/ACTIVE_PROJECTS.tsv
artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv

Localization authority:
config/localization/locale_registry.yaml
config/localization/content_roots_by_locale.yaml
config/localization/translation_checklist.yaml
config/localization/translation_loop_config.yaml
config/localization/pipeline_templates_zh_TW.yaml
config/localization/quality_contracts/golden_translation_regression.yaml
docs/LOCALE_CATALOG_MARKETING_PLAN.md
docs/LOCALE_PERSONAS.md
docs/CJK_ATOM_TRANSLATION_QUEUE.md

Existing tooling:
scripts/localization/translate_atoms_to_locale.py
scripts/localization/run_translation_loop.py
scripts/localization/validate_translations.py
scripts/localization/locale_structural_gate.py
scripts/ci/report_translation_coverage.py

Prior audit:
artifacts/localization/ZH_TW_ATOM_TEMPLATE_GAP_AUDIT_2026_04_14.md
artifacts/localization/zh_tw_translation_manifest.json
artifacts/localization/ZH_TW_TRANSLATION_RUN_REPORT_2026_04_14.md

Emit STARTUP_RECEIPT, then execute.

TASK: Translate all English user-facing Phoenix Omega content into Taiwan Traditional Chinese (zh-TW) using Pearl Star local Qwen only.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: translation; core_pipeline; teacher_mode; marketing; release

INTENT:

The owner wants Taiwan Chinese coverage for all English content in the repo that the product/pipeline may show to readers, listeners, customers, or generated books.

Use Pearl Star only:
- Ollama/Qwen: http://192.168.1.112:11434
- Preferred installed model from prior audit: qwen2.5:14b
- Do NOT use Claude API, Google Translate, DashScope, ElevenLabs, or external paid APIs.

LOCALE:

Target locale: zh-TW
Language: Traditional Chinese for Taiwan
Tone: natural Taiwan Mandarin, therapeutic/self-help, emotionally warm, not Mainland/Simplified, not Hong Kong Cantonese.

PHASE 1: DEFINE TRANSLATABLE SCOPE

Create/update:

artifacts/localization/ZH_TW_REPO_WIDE_TRANSLATION_SCOPE_2026_04_14.md
artifacts/localization/zh_tw_repo_wide_translation_manifest.json

Scan the repo and classify English content into:

P0 — Translate now:
- atoms/**/CANONICAL.txt excluding */locales/*
- SOURCE_OF_TRUTH/teacher_banks/*/approved_atoms/*/*.yaml body fields
- registry/*.yaml prose fields only: content, purpose/title only if user-facing
- config/pearl_practice/component_templates.yaml prose strings
- config/pearl_practice/exercise_templates.yaml prose strings
- config/funnel/email_templates/*.yaml user-facing email copy
- config/freebies/**/*.yaml user-facing freebie copy if present
- config/catalog_planning/description_templates.yaml user-facing descriptions
- config/video/image_prompt_templates.yaml only if prompts are reader/customer-facing; otherwise mark P2
- template_expand/**/* prose-bearing YAML/MD/TXT files
- old_chat_specs/old_chat_pose_book_template.txt and old_chat_specs/old_claude_template_persona_stuff.txt only as reference/provenance; do not bulk translate unless needed as source material

P1 — Translate after path convention is confirmed:
- teacher-bank localized output if runtime loader path remains unresolved
- registry zh-TW mirrors if no existing convention exists
- legacy template libraries if no output convention exists

P2 — Do not translate automatically:
- Python code
- tests
- CI configs
- internal docs
- GitHub workflows
- shell scripts
- YAML keys, IDs, enum values, variant IDs, atom IDs, file paths, config keys
- prompt-engineering docs unless they are used as reader-facing source text
- old chat logs as whole files unless explicitly selected

For every translatable item, record:
```json
{
  "source_path": "...",
  "target_path": "...",
  "content_type": "persona_atom|teacher_atom|registry|practice_template|funnel_email|freebie|catalog_metadata|legacy_template|other_user_facing",
  "fields": ["body", "content"],
  "locale": "zh-TW",
  "status": "missing|present|too_short|blocked_path_convention|skip_internal",
  "priority": "P0|P1|P2"
}
```

PHASE 2: PEARL STAR/QWEN HEALTH CHECK

Run:

```bash
curl -sS http://192.168.1.112:11434/api/tags | tee artifacts/localization/zh_tw_qwen_tags_2026_04_14.json
```

Confirm `qwen2.5:14b` exists. If not, use the installed qwen model and document the exact model.

PHASE 3: RUN SAFE TRANSLATION BATCHES IN ORDER

Run P0 in this order.

1. Persona atoms first:

```bash
PYTHONPATH=. python3 scripts/localization/translate_atoms_to_locale.py \
  --locale zh-TW \
  --persona-atoms-only \
  --ollama-url http://192.168.1.112:11434 \
  --model qwen2.5:14b \
  --workers 2 \
  2>&1 | tee artifacts/localization/zh_tw_persona_atoms_translation_2026_04_14.log
```

2. Teacher atoms only if the canonical output path has been reconciled.

Preferred canonical path:
`SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms_localized/zh-TW/<SLOT>/<file>_zh-TW.yaml`

If script and loader are aligned, run:

```bash
PYTHONPATH=. python3 scripts/localization/translate_atoms_to_locale.py \
  --locale zh-TW \
  --teacher-banks-only \
  --ollama-url http://192.168.1.112:11434 \
  --model qwen2.5:14b \
  --workers 2 \
  2>&1 | tee artifacts/localization/zh_tw_teacher_atoms_translation_2026_04_14.log
```

If loader/script path conflict remains, do not translate teacher atoms. Record as blocker.

3. Practice templates, funnel emails, catalog descriptions, freebie copy, registry prose, and legacy templates:

If no existing script supports safe field-level translation, create:

scripts/localization/translate_repo_user_facing_to_locale.py

It must:
- read `zh_tw_repo_wide_translation_manifest.json`
- translate only fields marked P0
- preserve YAML keys and structure
- preserve placeholders exactly
- write locale mirrors, not overwrite English source
- skip already translated files
- produce a per-file trace

Run:

```bash
PYTHONPATH=. python3 scripts/localization/translate_repo_user_facing_to_locale.py \
  --locale zh-TW \
  --manifest artifacts/localization/zh_tw_repo_wide_translation_manifest.json \
  --ollama-url http://192.168.1.112:11434 \
  --model qwen2.5:14b \
  --workers 2 \
  2>&1 | tee artifacts/localization/zh_tw_repo_user_facing_translation_2026_04_14.log
```

PHASE 4: VALIDATION

Run:

```bash
PYTHONPATH=. python3 scripts/localization/validate_translations.py --locale zh-TW || true
PYTHONPATH=. python3 scripts/localization/locale_structural_gate.py --locale zh-TW || true
PYTHONPATH=. python3 scripts/ci/report_translation_coverage.py || true
PYTHONPATH=. python3 -m pytest tests/test_validate_translations.py tests/test_translation_pipeline_smoke.py -q
```

Also run custom checks:
- no `<think>` blocks
- no “Here is the translation”
- no dominant Simplified Chinese in zh-TW output
- placeholders preserved exactly
- YAML parses
- JSON parses
- no source English copied into translated prose except IDs / technical terms / names
- no code/config keys translated

PHASE 5: REPORT

Create/update:

artifacts/localization/ZH_TW_REPO_WIDE_TRANSLATION_RUN_REPORT_2026_04_14.md

Include:
- total scanned files
- total P0/P1/P2
- translated counts by category
- skipped counts
- blocked counts
- model used
- Pearl Star URL
- validation results
- known risks
- next actions

PHASE 6: GIT WORKFLOW

Start clean:

```bash
git fetch origin
git checkout -b agent/zh-tw-repo-wide-translation origin/main
```

Commit plan:
1. `docs: audit repo-wide zh-TW translation scope`
2. `fix: align zh-TW teacher atom translation path` if needed
3. `feat: translate zh-TW persona atoms`
4. `feat: translate zh-TW teacher atoms` only if path is safe
5. `feat: translate zh-TW user-facing templates`
6. `docs: record zh-TW repo-wide translation run`

WRITE_SCOPE:
- artifacts/localization/ZH_TW_REPO_WIDE_TRANSLATION_SCOPE_2026_04_14.md
- artifacts/localization/zh_tw_repo_wide_translation_manifest.json
- artifacts/localization/*zh_tw*2026_04_14*.log
- artifacts/localization/ZH_TW_REPO_WIDE_TRANSLATION_RUN_REPORT_2026_04_14.md
- atoms/**/locales/zh-TW/CANONICAL.txt
- SOURCE_OF_TRUTH/teacher_banks/**/approved_atoms_localized/zh-TW/**/*.yaml if path is safe
- config/pearl_practice/locales/zh-TW/**
- locale mirror paths for funnel/freebie/catalog/template files, if defined in manifest
- scripts/localization/translate_atoms_to_locale.py if path fix is required
- scripts/localization/translate_repo_user_facing_to_locale.py if needed
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

OUT_OF_SCOPE:
- Do not translate code.
- Do not translate tests.
- Do not translate YAML keys, IDs, enum labels, paths, or placeholders.
- Do not overwrite English source files.
- Do not translate zh-CN, zh-HK, zh-SG, ja-JP, ko-KR.
- Do not use external APIs.
- Do not translate old chat logs wholesale unless explicitly selected as source templates.

NON-NEGOTIABLE:
- Pearl Star / local Qwen only.
- zh-TW means Taiwan Traditional Chinese.
- Preserve placeholders exactly.
- Preserve file structure and source provenance.
- Idempotent and resumable.
- If output path convention is ambiguous, block that category and report it.
- If generated diff is massive, still check deletion count before PR.
- If deletions exceed 50 files, STOP and ask owner.

PREFLIGHT BEFORE PUSH:

```bash
git status --short
git diff origin/main...HEAD --stat
python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
```

BEFORE MERGE:

```bash
gh pr diff <PR_NUMBER> --stat | tail -1
```
```

---

**Cursor**

Understood — I’ll execute this end-to-end as a safe repo-wide zh-TW localization run, starting by reading the required protocol/authority docs and then building a strict P0/P1/P2 scope manifest before any translation writes. I’ll report blockers immediately if path conventions or model availability don’t line up.

I’ve finished the required session/provenance files and found active translation-related workstreams, so next I’m reading localization authority/config docs plus existing scripts to ensure the scope and path conventions are safe before writing manifests.

I’m now emitting the required startup receipt and then I’ll continue with scope scanning plus script/path verification before running any translation commands.

`STARTUP_RECEIPT`  
`AGENT: Pearl_Localization + Pearl_Dev`  
`TASK: Repo-wide zh-TW translation of user-facing/pipeline content with safe field-level scope`  
`PROJECT_ID: proj_state_convergence_20260328`  
`SUBSYSTEM: translation; core_pipeline; teacher_mode; marketing; release`  
`AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; config/localization/locale_registry.yaml; config/localization/content_roots_by_locale.yaml; config/localization/translation_checklist.yaml; config/localization/translation_loop_config.yaml; config/localization/pipeline_templates_zh_TW.yaml`  
`READ_PATH_COMPLETE: no (reading remaining listed localization docs + audits now)`  
`WRITE_SCOPE: artifacts/localization/*; locale mirror outputs for zh-TW; scripts/localization/translate_repo_user_facing_to_locale.py (if required); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`  
`OUT_OF_SCOPE: Python logic unrelated to localization, tests logic, CI/workflows, operational docs, YAML keys/IDs/paths/placeholders`  
`BLOCKERS: none yet`  
`READY_STATUS: ready`

I confirmed prior audits already identified key teacher-path and registry/template convention blockers; next I’m inspecting localization scripts, then I’ll generate the new repo-wide P0/P1/P2 scope + manifest and run the requested health/translation commands in safe order.

I hit timeouts using broad recursive globbing, so I’m switching to a targeted Python scanner to classify P0/P1/P2 paths directly and write the two requested scope artifacts in one pass (safer and faster on this large repo).

Scope/manifest artifacts are now generated with full P0/P1/P2 classification. Next I’m running the Pearl Star model health check and then starting translation batches in the requested order, with blockers logged when conventions are unsafe.

The persona translation batch is running, but output is buffered through `tee`, so I’m not yet seeing progress lines. I’m giving it a bit more time to confirm whether it’s actively translating or stuck before deciding whether to restart unbuffered.

I found no existing safe field-level translator for the non-atom user-facing files, so I’m adding `scripts/localization/translate_repo_user_facing_to_locale.py` now to consume the manifest, preserve YAML structure/placeholders, write locale mirrors only, and emit per-file traces.

I detected an already-running persona translation process from before this session and avoided duplicate writes by stopping the one I just spawned; I’m now letting the existing process continue and monitoring the new user-facing translation worker via its trace output.

I need your direction before I continue.

`git status --short` now shows a large set of unexpected changes outside the localization scope (many `.claude/worktrees/*` entries plus `_wt_*`), which I did **not** edit directly in this run. Per your repo safety rules, I’m stopping immediately instead of proceeding with more writes/commits.

Current safe progress already completed:
- Created scope + manifest:
  - `artifacts/localization/ZH_TW_REPO_WIDE_TRANSLATION_SCOPE_2026_04_14.md`
  - `artifacts/localization/zh_tw_repo_wide_translation_manifest.json`
- Saved Pearl Star model tags:
  - `artifacts/localization/zh_tw_qwen_tags_2026_04_14.json` (confirms `qwen2.5:14b` present)
- Added translation script:
  - `scripts/localization/translate_repo_user_facing_to_locale.py`
- Validation/tests run:
  - `tests/test_validate_translations.py` + `tests/test_translation_pipeline_smoke.py` => `31 passed`

Two translation processes are/were active:
- A pre-existing persona-atoms run from before this turn (same command/log path).
- The new user-facing manifest run (currently slow, with at least one file translated).

How do you want to proceed?
1. I stop all running translation processes and continue only with deterministic artifacts/reporting.
2. I keep the runs going and only monitor/report (no more structural edits).
3. I stop everything, cleanly isolate just this work on a fresh branch/worktree, and rerun.


# Pearl News 5-Variation Atom Expansion — Agent Brief

You are one of 10 parallel agents authoring teacher × topic packs for Pearl News. This document is the shared brief; your per-agent prompt names your specific teacher and topics.

## Why this work exists

Operator directive 2026-05-17:

> Deterministic atoms for each teacher have five variations. Vary the use of the five atoms. Keep track. Use them so that we have the fewest repeats.

> There should not be separate authors for Pearl News. The authors should come from Pearl Prime.

Two helpers are already live on `main`:

1. `pearl_news/pipeline/teacher_authority.py` — overlays each pack's `identity:` block with the canonical values from `SOURCE_OF_TRUTH/teacher_banks/<id>/doctrine/doctrine.yaml`. No pack rewrites needed.
2. `pearl_news/pipeline/atom_usage_tracker.py` — LRU selector. With 5 atoms per slot, guarantees no repeat within a 4-pick window per `(teacher, topic, slot)`.

The LRU mechanism only delivers variety **if the packs actually have 5 options per slot**. That is your job.

## Reference cells (already on main)

Use these two cells as your structural template (NOT for voice — voice comes from YOUR teacher's doctrine):

- `pearl_news/teacher_topic_packs/teachers/junko/mental_health.yaml` (PR #1158)
- `pearl_news/teacher_topic_packs/teachers/junko/education.yaml` (PR #1160)
- `pearl_news/teacher_topic_packs/locales/ja/teachers/junko/{mental_health,education}.yaml`
- `pearl_news/teacher_topic_packs/locales/zh-cn/teachers/junko/{mental_health,education}.yaml`

## Per-cell output contract

For EVERY topic in your list, deliver three files:

### 1. EN base pack
Path: `pearl_news/teacher_topic_packs/teachers/<teacher_id>/<topic>.yaml`

11 slots, each with EXACTLY 5 options. Slots:
- `hook_personal` — 5 × `line`
- `hook_big_picture` — 5 × `line`
- `teacher_intro` — 5 × `line`
- `youth_somatic` — 5 × `line`
- `teacher_witness` — 5 × `line`
- `turnaround` — 5 × `stat_line_1` + `stat_line_2`
- `bridge` — 5 × `line` + `hidden_capacity`
- `teacher_perspective` — 5 × `paragraphs` (3 paragraphs each) + `header`
- `practice` — 5 × `display_name` + `duration` + `announcement_line` + `relief_lines` (2 items) + `relief_register` + `derived_from_frame`
- `cta` — 5 × `org` + `line`
- `title_system.headline_layer_2` — 5 × `line`

**CRITICAL:** Every option's `metadata.semantic_family` MUST be unique within its slot. The pack-level `variation_policy.avoid_same_semantic_family_within_article: true` will collapse the candidate pool if two options share a family.

### 2. ja overlay
Path: `pearl_news/teacher_topic_packs/locales/ja/teachers/<teacher_id>/<topic>.yaml`

Mirror all 5 EN options by `id`. Carry ONLY the text fields:
- `line`, `paragraphs`, `stat_line_1`, `stat_line_2`, `announcement_line`, `relief_lines`, `display_name`, `header`, `hidden_capacity`

Do NOT include `metadata` (that lives in the EN base only).

### 3. zh-cn overlay
Path: `pearl_news/teacher_topic_packs/locales/zh-cn/teachers/<teacher_id>/<topic>.yaml`

Same structure as ja, in zh-cn.

## ID naming

`<teacher_id>_<topic_short>_<slot_short>_<NN>`

Topic shorts: `climate=clim`, `economy_work=eco`, `education=edu`, `mental_health=mh`, `peace_conflict=peace`, `partnerships=part`, `inequality=ineq`

Slot shorts: `hook_personal=hook_personal`, `hook_big_picture=hook_big`, `teacher_intro=intro`, `youth_somatic=somatic`, `teacher_witness=witness`, `turnaround=turnaround`, `bridge=bridge`, `teacher_perspective=perspective`, `practice=practice`, `cta=cta`, `headline_layer_2=headline`

Example: `master_feung_clim_hook_personal_03`

If existing pack already has `option_01` and `option_02`, preserve them and add `option_03/04/05` with new unique `semantic_family` values.

## Doctrine compliance — non-negotiable

BEFORE authoring, READ:
- `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/doctrine.yaml`
- Existing packs: `pearl_news/teacher_topic_packs/teachers/<teacher_id>/<topic>.yaml` for each of your topics

Honor:
- `tradition` — use the teacher's actual lineage. Do NOT generic-Buddhist or generic-Asian-wisdom anyone.
- `tone_profile` — speaker register.
- `forbidden_claims` — explicit no-fly zones.
- `tone_boundaries` — what the voice does and does not do.
- `prohibited_outcomes` — entire angles to avoid.

The pack's `identity:` block may say something different from the doctrine (drift from earlier authoring). Doctrine WINS at runtime via `teacher_authority.py` — but write the pack to match doctrine anyway for clarity.

## YAML gotcha — read this BEFORE writing prose

In unquoted block-list-item strings (especially inside `paragraphs:` lists), NEVER use `: ` (colon + space). YAML interprets it as a key-value mapping and errors out:

```yaml
# BREAKS:
paragraphs:
- The shift happens here: not through force but through reception.

# FIX A (em-dash):
paragraphs:
- The shift happens here — not through force but through reception.

# FIX B (single-quoted block):
paragraphs:
- 'The shift happens here: not through force but through reception.'
```

The same applies to ANY plain block scalar — `line:`, `stat_line_2:`, `announcement_line:`. If your text contains `: `, either rewrite or wrap in single quotes (and double any internal single quotes).

## Real stats policy

`turnaround.stat_line_1` and `stat_line_2` ARE shown to readers. They MUST be real, defensible, tied to real organizations. NO fabrication.

Reference stats from junko packs (you can use these if topic-relevant, or find others):
- UNICEF Global Coalition for Youth Mental Health (June 2025) — 5,600 youth, 7 countries, 6 in 10 overwhelmed
- WHO Europe Child & Adolescent Health Strategy 2026-2030 (adopted October 2025, 53 member states)
- 988 Suicide & Crisis Lifeline — 14M contacts since 2022 launch
- JED Campus / The Jed Foundation — 488 universities
- Active Minds — 650+ peer-led chapters on US campuses
- UNESCO SDG 4 monitoring — 244M children/youth out of school worldwide
- UNICEF Learning Recovery 2024 — ~65% of grade-10 reach basic proficiency
- Education Cannot Wait (UN-hosted) — $1B mobilized since 2016
- IPCC AR6 (2023) — 1.5°C threshold approached
- ILO World Employment and Social Outlook 2024 — ~73 million young people unemployed
- UNHCR Global Trends 2024 — 117M+ forcibly displaced
- UN-Habitat — 1.6 billion in inadequate housing

For your specific topic, find 5 topic-appropriate stats with real anchors.

## CTA policy

5 distinct real organizations relevant to your topic. Each option:
```yaml
- id: <id>
  org: <organization name>
  line: 'One-sentence why-to-engage + concrete door-in (URL, hotline, text code). Door in: <url-or-instruction>'
  metadata:
    semantic_family: door-in-<org-short>
    article_types:
    - hard_news_spiritual_response
```

No two CTAs may have the same `org`. No fabricated organizations.

## No UN affiliation claims

Pearl News is an independent nonprofit. NEVER write "Pearl News works with the UN" or imply affiliation. Cite organizations + door-in URLs only.

The pack's `sdg.fallback_un_tie.line` already carries the disclaimer — preserve it.

## After authoring — required validation

### Smoke test

Copy `artifacts/pearl_news/_smoke_junko_education_20260517.py` to `artifacts/pearl_news/_smoke_<teacher_id>_20260517.py`. Edit:
- Change `TEACHER` and `TOPIC` to iterate over YOUR topics
- Run it. ALL topics × 3 locales MUST pass.

If any cell fails, fix it. Do not push a failing pack.

### Preflight (MUST all pass)

```bash
PYTHONPATH=. python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
python3 scripts/ci/audit_llm_callers.py
```

Push-guard OK. Preflight OK. LLM audit violation_count: 0.

## Git flow

Your branch is `agent/<teacher_id>-5-variations-20260517`. You are already on it.

1. Stage only the pack files + your smoke test:
   ```bash
   git add pearl_news/teacher_topic_packs/teachers/<teacher_id>/*.yaml \
           pearl_news/teacher_topic_packs/locales/ja/teachers/<teacher_id>/*.yaml \
           pearl_news/teacher_topic_packs/locales/zh-cn/teachers/<teacher_id>/*.yaml \
           artifacts/pearl_news/_smoke_<teacher_id>_20260517.py
   ```
   Do NOT add `artifacts/pearl_news/_qwen_debug/`, `atom_usage_log.json`, `qa_*` directories, or any unrelated files.

2. Commit (template — adapt per your teacher):
   ```
   feat(pearl-news): <teacher_id> 5-variation atom expansion (<N> cells)
   
   Wave X, cells N-M of 45 per docs/PEARL_NEWS_5_VARIATION_EXPANSION_PROGRAM.md.
   
   Following the junko x mental_health template (PR #1158 / 833b8d89c) and
   junko x education (PR #1160). Each slot has 5 distinct options with 5
   distinct semantic_family values. All options authored under <teacher_id>'s
   doctrine: <one-line doctrine summary>.
   
   Topics shipped: <list>
   
   Smoke test artifacts/pearl_news/_smoke_<teacher_id>_20260517.py PASSES
   all cells × 3 locales.
   
   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
   ```

3. Push: `git push -u origin <branch>`

4. Open PR with `gh pr create`. Title: `feat(pearl-news): <teacher_id> 5-variation expansion (<N> cells)`. Body: see junko PRs #1158 and #1160 as templates.

5. **DO NOT MERGE.** The root agent will admin-merge.

## Report back

When you finish, report:
- PR URL
- Commit SHA
- Smoke-test summary (e.g., "5/5 topics × 3 locales PASS")
- Any deviations or notes (e.g., a topic already had 3+ options)

## What NOT to do

- Do not modify files outside your teacher's namespace
- Do not modify the program doc (`docs/PEARL_NEWS_5_VARIATION_EXPANSION_PROGRAM.md`)
- Do not modify the helpers (`teacher_authority.py`, `atom_usage_tracker.py`, `deterministic_teacher_topic.py`)
- Do not modify `assemble_v52.py` or any prompt under `pearl_news/prompts/`
- Do not modify other teachers' packs
- Do not admin-merge your own PR
- Do not bypass push-guard or preflight

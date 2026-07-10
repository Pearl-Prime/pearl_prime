# CI Workflow Banned-Key Fix + Audit-Gate Coverage Gap (2026-07-10)

Follow-up from `artifacts/qa/JA_JP_TRANSLATION_CLOSEOUT_2026-07-10.md` ("Follow-ups" item 3).

## What was found

`.github/workflows/translate-bestseller-atoms.yml` injected `TOGETHER_API_KEY` (preferred) and
`DASHSCOPE_API_KEY`/`DASHSCOPE_BASE_URL`/`DASHSCOPE_MODEL` (fallback) from repo secrets into
`scripts/localization/run_translation_loop.py`. Both Together and DashScope-cloud are on
CLAUDE.md's BANNED paid-LLM-API list. This was a standing, checked-in violation.

`scripts/ci/audit_llm_callers.py` reports 0 violations repo-wide despite this, because
`config/governance/banned_llm_patterns.yaml`'s `workflow_paid_key_injection` rule — the one rule
that scans for exactly this class of issue (banned keys injected into workflow YAML env blocks) —
explicitly and deliberately excluded `TOGETHER_API_KEY` and `DASHSCOPE_API_KEY` from its regex,
per its own inline comment: *"DashScope/Qwen (Tier-2) and Together (present in
translate-bestseller-atoms.yml, pending separate review) are intentionally NOT listed here."* The
gap was known and documented, not accidental — this is exactly that deferred review.

Root cause the workflow inherited: `scripts/localization/run_translation_loop.py` (the script the
workflow calls) has its own hard preflight gate requiring `TOGETHER_API_KEY` or
`DASHSCOPE_API_KEY` — unlike `scripts/translate_atoms_all_locales_cloud.py`, which PR #5496 fixed
this session to also accept free Ollama mode via `_is_ollama_endpoint()`. `run_translation_loop.py`
never got that fix; both scripts wrap the same `scripts/localization/llm_client.py`, which already
supports Ollama.

## Fixes landed

1. **`scripts/localization/run_translation_loop.py`** — preflight gate now also accepts
   `_is_ollama_endpoint()` (same fix pattern as PR #5496), so the script itself is policy-compliant
   and usable for free local translation via Pearl Star, not just paid cloud keys.

2. **`config/governance/banned_llm_patterns.yaml`** — added `TOGETHER_API_KEY` to the
   `workflow_paid_key_injection` regex. Together has zero legitimate Tier-2 use anywhere in this
   repo (grep confirms exactly one prior reference, the now-fixed workflow), so this is an
   unambiguous, safe addition — `audit_llm_callers.py` will now catch this class of violation if
   it recurs.

   **`DASHSCOPE_API_KEY` intentionally left out of this fix.** It's injected in 9 workflow files
   (`generate-and-translate-atoms.yml`, `marketing-briefs-and-proposals.yml`,
   `research-pipeline-run.yml`, `pearl-news-fill-qwen.yml`, `marketing_continuous.yml`,
   `max-quality-catalog.yml`, `translate-atoms-qwen-matrix.yml`, `catalog-book-pipeline.yml`, and
   the one fixed here), most via `secrets.DASHSCOPE_API_KEY || secrets.QWEN_API_KEY` — the same env
   var name is legitimately used when `QWEN_BASE_URL` resolves to an Ollama endpoint. Blanket-
   banning the key name would false-flag workflows that may already be compliant depending on what
   `QWEN_BASE_URL` secret is actually configured to. That requires a per-workflow audit of actual
   base_url resolution and runner reachability, not a one-line regex change. **Flagged as a
   separate follow-up task, not resolved here** (see spawned task).

3. **`.github/workflows/translate-bestseller-atoms.yml`** — disabled. The banned-key env block is
   removed entirely (no more `TOGETHER_API_KEY`/`DASHSCOPE_*` injection, so it's structurally
   impossible for this workflow to make a banned call even if the secrets remain configured at the
   repo level). The `translate` job is replaced with a `blocked` job that fails immediately with a
   clear `::error::` message pointing to the working interactive alternative
   (`scripts/localization/run_translation_loop.py` run against Pearl Star Ollama, as used in
   `artifacts/qa/JA_JP_TRANSLATION_CLOSEOUT_2026-07-10.md`).

   **Why disable rather than re-point at Ollama:** this job runs on GitHub-hosted `ubuntu-latest`,
   which cannot reach Pearl Star's Tailscale-only Ollama endpoint (`pearlstar.tail7fd910.ts.net`).
   Making this workflow itself compliant would require a self-hosted runner registered on that
   Tailscale network — an infrastructure decision for the operator, not made unilaterally here.
   `workflow_dispatch` inputs/metadata are kept (not deleted) so the shape is preserved if that
   infra decision is made later.

## Verification

- `python3 -c "import yaml; yaml.safe_load(...)"` — both YAML files valid
- `actionlint` — clean on the fixed workflow
- `python3 -c "import ast; ast.parse(...)"` — `run_translation_loop.py` valid Python
- Confirmed via grep: `TOGETHER_API_KEY` had exactly one prior reference in `.github/workflows/**`
  (the fixed file); `DASHSCOPE_API_KEY` has 9, all left untouched pending separate audit
- `audit_llm_callers.py` re-run against `.github/workflows/` after the pattern fix: still 0
  violations for this specific rule set, as expected — the fix here *removed* the violation from
  the workflow rather than leaving it for the gate to catch; the gate fix is forward-looking
  (catches recurrence), not retroactive detection of something already removed

## Scope

Tool + CI-config + one workflow file only. No `atoms/**/locales` content touched. No changes to
the 8 other `DASHSCOPE_API_KEY`-using workflows (out of scope, flagged separately).

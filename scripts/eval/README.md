# Agent-Eval Harness (`scripts/eval/`)

Self-hosted skill/agent evaluation harness for Phoenix Omega — **DeepEval + agentevals
on a LOCAL Gemma/Qwen judge**, zero paid LLM API.

- **Workstream:** `ws_agent_eval_harness_deepeval_agentevals_20260612`
  (project `PRJ-AGENT-SYSTEM-IMPROVEMENT-V2`, Pearl_Research)
- **Authority spec:** [`docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md`](../../docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md)
  — §3.2 (ratified eval stack), §5 (sequencing), §6 (Tier-2 compliance)
- **Roadmap item:** **P0-2** — "Run `skill-creator` evals on the 4 skills … record scores in the skill dirs."

> **Status: Phase-2 first increment.** This ships the **P0-2 baseline-eval runner**
> (`skill_eval_runner.py`), its case datasets, the local-judge config, and the
> requirements manifest. It is **dry-run-safe by default** and writes a baseline
> stub into each skill dir. The **CI-gate wiring** (emitting eval traces into the
> Langfuse/OTel store) is intentionally **out of scope here** — it is gated on
> **P0-4** (`ws_agent_observability_langfuse_pilot_20260612`) landing the trace
> substrate. See [Deferred work](#deferred-work).

---

## TL;DR

```bash
# 0. Dry-run + --check need only pyyaml (already pinned in repo-root requirements.txt).
#    Install the FULL harness deps (DeepEval/agentevals/openai client) only for --judge:
pip install -r scripts/eval/requirements-eval.txt

# 1. Validate the case datasets + judge config (no writes, no network):
PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py --check

# 2. Dry-run baseline (default): no judge, no network. Writes skills/<name>/eval/baseline.json
PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py

# 3. Live judged run (opt-in) against LOCAL Ollama on Pearl Star:
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"   # loads GEMMA_BASE_URL/QWEN_BASE_URL
PYTHONPATH=. python3 scripts/eval/skill_eval_runner.py --judge
```

---

## What it measures

Two metric families per skill — the same two `skill-creator` benchmarks the
roadmap names — recorded as `skills/<name>/eval/baseline.json`:

| Metric | Dry-run (default) | Judged (`--judge`) |
|---|---|---|
| **trigger-accuracy** | Deterministic token-overlap heuristic: does the skill's frontmatter `description` overlap each positive prompt above `--threshold`, and stay below it for negatives? `(TP+TN)/total`. | The **local Gemma/Qwen judge** is asked YES/NO whether the description should route each prompt; accuracy recomputed from judged decisions. |
| **task-score** | `null` (un-graded) — a real score needs a judge. The prompts + rubrics are still recorded. | Each real-task prompt is graded `0.0–1.0` by the local judge against its rubric. Mean reported. |

The four target skills (spec §2, P0-2): **`pearl-github`, `pearl-int`,
`deep-research`, `phoenix-isolation-pr`**.

Case datasets live in [`scripts/eval/cases/<skill>.cases.yaml`](cases/) — each has
a `trigger` block (`positives` that should fire the skill / `negatives` a sibling
skill owns) and a `tasks` block (real-task prompts + grading rubrics).

### Output schema (`skills/<name>/eval/baseline.json`)

```jsonc
{
  "schema": "skill-eval/baseline/v1",
  "skill": "pearl-github",
  "mode": "dry-run",                       // or "judged"
  "skill_description_present": true,
  "metrics": {
    "trigger_accuracy": { "accuracy": 0.86, "true_positives": 7, "false_positives": 0, "...": "..." },
    "task_score":       { "mean": null, "scored_count": 0, "total_count": 3, "tasks": [ /* ... */ ] }
  },
  "notes": "Dry-run baseline ... regenerate with --judge once Pearl Star Ollama is reachable."
}
```

A dry-run baseline is a **regression anchor**: re-run after editing a SKILL.md
`description` and diff the `trigger_accuracy` block to catch a description that
started mis-triggering (the first-ever skill regression guard, per spec §2 P0-2
"catches mis-triggering").

---

## Tier-2 compliance (NO paid LLM API)

This harness is wired so that it **cannot** reach a paid LLM API
(CLAUDE.md LLM Tier policy + `.github/workflows/llm-policy-enforcement.yml`):

1. **Default is dry-run** — no network, no judge, no credentials. Safe in CI and
   unattended.
2. **The judge is LOCAL Ollama only.** `--judge` reads the base URL from
   `$GEMMA_BASE_URL` (English) / `$QWEN_BASE_URL` (CJK6) — the canonical Pearl
   Star Ollama OpenAI-compatible endpoints (`…:11434/v1`). The runner
   **hard-refuses** any base URL containing `api.openai.com`, `anthropic.com`,
   `dashscope`, or `googleapis.com`.
3. **The `openai` package is a client only**, pointed at Ollama — exactly the
   pattern already sanctioned in `config/governance/banned_llm_patterns.yaml`
   (`openai_api_cloud` rule, `line_allow_substrings: ollama / 11434 / *_BASE_URL`).
4. Run the repo audit before pushing any change to this harness:
   ```bash
   PYTHONPATH=. python3 scripts/ci/audit_llm_callers.py --fail-on-violation
   ```

**DeepEval / agentevals judge backend must also be local.** When the libraries
are installed and `--judge` is set, point DeepEval's judge at the same Ollama
model (see [DeepEval local-model setup](#deepeval--agentevals-self-hosted-setup)).
Never let DeepEval default to a hosted judge.

---

## Self-hosted setup

### Prerequisites

- **Pearl Star Ollama** reachable (LAN `http://192.168.1.101:11434/v1` or
  Tailscale `http://pearlstar.tail7fd910.ts.net:11434/v1`), serving:
  - `gemma3:27b` — English judge (Tier-2)
  - `qwen2.5:14b` — CJK6 judge (Tier-2)
  - Reference: `artifacts/handoffs/HANDOFF_LLM_TWO_TIER_MIGRATION_20260420.md`,
    `skills/pearl-int/references/pearl_star_node_inventory.md`.
- Env loaded from Keychain (single source of truth):
  ```bash
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  ```
- Harness deps installed (operator-present / self-hosted runner only):
  ```bash
  pip install -r scripts/eval/requirements-eval.txt
  ```

### Local-judge config — `local_judge.config.yaml`

The judge backend is configured in
[`scripts/eval/local_judge.config.yaml`](local_judge.config.yaml). Key fields:

```yaml
judge:
  provider: ollama
  base_url_env: GEMMA_BASE_URL        # canonical env var read FIRST
  base_url_fallback: "http://192.168.1.101:11434/v1"
  model: gemma3:27b
  temperature: 0.0
judge_cjk:
  base_url_env: QWEN_BASE_URL
  model: qwen2.5:14b
```

The runner resolves the env var first, then the fallback. CJK6 rubrics route to
`judge_cjk` (Qwen).

### DeepEval + agentevals self-hosted setup

The ratified stack (spec §3.2): **DeepEval** (Apache-2.0; component/output
metrics) **+ agentevals** (MIT; plan/tool-path trajectory evaluators). Both are
thin OSS components this harness *shells in* — we do **not** vendor a framework
runtime (spec §6).

Point **DeepEval** at the local Ollama judge instead of its default hosted judge:

```bash
# DeepEval ships a local-model setter that targets any OpenAI-compatible endpoint.
deepeval set-local-model \
  --model-name "gemma3:27b" \
  --base-url "$GEMMA_BASE_URL" \
  --api-key "ollama"
```

…or wrap a `DeepEvalBaseLLM` whose `.generate()` calls the same OpenAI client the
runner builds in `_make_local_client()`. Either way the judge is the local model.

**agentevals** trajectory evaluators (`create_trajectory_llm_as_judge`) accept a
`judge` callable — pass the same local Ollama client. Set
`harness.agentevals.trajectory_match_mode` in the config (default `superset`).

> Until DeepEval/agentevals are installed, the runner **degrades to the
> deterministic dry-run heuristic** so a fresh checkout and CI still pass.

---

## Files in this directory

| File | Purpose |
|---|---|
| `skill_eval_runner.py` | P0-2 baseline-eval runner. Dry-run-safe; `--judge` for live local-judged grading. Writes `skills/<name>/eval/baseline.json`. |
| `local_judge.config.yaml` | Local Ollama (Gemma/Qwen) judge config + DeepEval/agentevals backend knobs. |
| `requirements-eval.txt` | Pinned deps. Dry-run needs only `pyyaml` (already pinned in the repo-root `requirements.txt`); the **judged** path additionally needs DeepEval, agentevals, and the openai client. |
| `cases/<skill>.cases.yaml` | Per-skill trigger positives/negatives + real-task prompts & rubrics. |

Generated artifact roots (not committed here): per-skill baselines under
`skills/<name>/eval/`, and an optional aggregate run summary under
`artifacts/agent_eval/deepeval_agentevals_20260612/` (pass `--summary-out`).

---

## Deferred work

- **CI-gate wiring** (fail a PR when a skill's trigger-accuracy regresses; emit
  eval results into the trace store) — **gated on P0-4**
  (`ws_agent_observability_langfuse_pilot_20260612`) providing the Langfuse/OTel
  substrate. Per spec §5.4 + §7, P0-2 is runnable now but the broader CI-gate
  wiring waits on P0-4.
- **Live judged baselines** — require Pearl Star Ollama reachable + deps
  installed; run `--judge` then commit the regenerated `skills/<name>/eval/baseline.json`.
- **RAGAS / CometKiwi domain companions** — added per-subsystem (ei_v2/pearl_news
  citation faithfulness; translation MT-QE), still on the local judge (spec §3.2).
- **agentevals trajectory cases** — the current `tasks` are single-turn prompts;
  multi-step trajectory fixtures (plan + tool-path) land with the P0-4 trace
  substrate that records real agent trajectories to score against.

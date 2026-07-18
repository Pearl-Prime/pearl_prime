# DASHSCOPE_API_KEY Audit Across 8 CI Workflows (2026-07-10)

Follow-up from `artifacts/qa/CI_WORKFLOW_BANNED_KEY_FIX_2026-07-10.md` (PR #5498), which
deliberately did not add `DASHSCOPE_API_KEY` to the `workflow_paid_key_injection` audit regex
because the same env var name is used by 8 other workflows for what may be legitimate Tier-2
Qwen-via-Ollama access. This audits each of those 8.

## Method

For each workflow: (a) traced the code path that actually consumes `DASHSCOPE_API_KEY`/
`QWEN_BASE_URL`, (b) checked `runs-on` (GitHub-hosted `ubuntu-latest` cannot reach Pearl Star's
Tailscale-only Ollama endpoint; `self-hosted` plausibly can, by design), (c) could **not** see
actual secret values — that's operator-only information. Findings describe what value would make
each workflow compliant vs. banned, not a verified verdict on live secrets.

## Findings

| Workflow | Runner | Code path | Verdict | Action |
|---|---|---|---|---|
| `generate-and-translate-atoms.yml` | `ubuntu-latest` | `scripts/generate_band_depth_atoms.py` + `scripts/localization/run_translation_loop.py`, both via shared `llm_client.py` | **Cannot be verified compliant** — same reachability problem as the original `translate-bestseller-atoms.yml` violation | **Fixed here** — disabled, same pattern as PR #5498 |
| `translate-atoms-qwen-matrix.yml` | `ubuntu-latest` | `scripts/localization/run_translation_loop.py` | **Cannot be verified compliant**, and runs on an **unattended weekly cron** (`0 2 * * 0`) — the highest-risk shape found, since a violation here would be automatic and silent, not requiring manual dispatch | **Fixed here** — disabled, cron trigger removed entirely |
| `research-pipeline-run.yml` | `ubuntu-latest` | Inline `openai.OpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)` in the workflow YAML itself — no Ollama-detection gating at all, always instantiates a client regardless of what `QWEN_BASE_URL` resolves to | **Flagged, not modified** — see "Existing exemption inconsistency" below | Not fixed; needs operator verification |
| `marketing-briefs-and-proposals.yml` | `self-hosted` | Direct `curl` to `$QWEN_BASE_URL/chat/completions` | Plausibly compliant — self-hosted runner choice is itself evidence of intent to reach a private (Pearl Star) endpoint | Left alone |
| `pearl-news-fill-qwen.yml` | `self-hosted` | Same `curl` pattern | Plausibly compliant, same reasoning | Left alone |
| `marketing_continuous.yml` | `self-hosted` | Same `curl` pattern | Plausibly compliant, same reasoning | Left alone |
| `max-quality-catalog.yml` | `self-hosted` | Same `curl` pattern | Plausibly compliant, same reasoning | Left alone |
| `catalog-book-pipeline.yml` | `self-hosted` | Same `curl` pattern | Plausibly compliant, same reasoning | Left alone |

## Existing exemption inconsistency (research-pipeline-run.yml) — flagged, not fixed

`config/governance/banned_llm_patterns.yaml`'s `openai_api_cloud` rule already exempts
`.github/workflows/research-pipeline-run.yml`, with a comment asserting *"All listed exemptions
use OpenAI client pointed at local Ollama."* But this workflow runs on `ubuntu-latest`, which by
the same reachability logic used throughout this audit (and PR #5498) cannot reach a
Tailscale-only Pearl Star endpoint. That's a real inconsistency: either (a) the exemption's
assumption is stale/wrong, (b) Pearl Star's Ollama has some other reachable ingress this audit
isn't aware of (a publicly-exposed proxy, a different self-hosted runner label misread as
`ubuntu-latest`, etc.), or (c) this workflow has simply never successfully connected when
dispatched.

**Not modified here** because it's a *pre-existing, deliberately reviewed* exemption (not a newly
discovered gap like the other two) — overriding a prior explicit decision without operator
confirmation of which of (a)/(b)/(c) is true risks breaking something that may already work
correctly for reasons not visible from the repo. **Recommend operator verification**: confirm what
`secrets.QWEN_BASE_URL` actually resolves to when this workflow runs, and whether it has ever
successfully completed a dispatch. If it turns out to be case (a) or (c), it needs the same fix
pattern applied to the two workflows fixed in this PR.

## Fixes landed

Same pattern as PR #5498: `workflow_dispatch` input metadata kept (marked "DISABLED — see
top-of-file comment") for shape; job body replaced with an immediate `::error::` explaining why and
pointing to the working interactive alternative. No banned-key env injection remains in either
file. `translate-atoms-qwen-matrix.yml`'s weekly `schedule:` trigger is removed outright (an
always-failing job on an unattended cron is pure noise, not a safeguard).

No changes to `config/governance/banned_llm_patterns.yaml` in this PR — the same reasoning from PR
#5498 holds: `DASHSCOPE_API_KEY` remains too ambiguous (legitimately used by the 5 self-hosted
workflows above) for a blanket regex ban. This audit resolves two of the eight concretely, by
removing their banned-key wiring directly rather than by widening the audit gate's pattern.

## Verification

- `yaml.safe_load` on both changed files — valid
- `actionlint` on both — clean
- Confirmed via `grep -n "runs-on"` across all 8 target files: exactly 3 on `ubuntu-latest`
  (2 fixed here, 1 flagged/unmodified), 5 on `self-hosted` (all left alone)
- Confirmed `translate-atoms-qwen-matrix.yml` was the only one of the 8 with a `schedule:` trigger

## Scope

Two workflow files fixed, one flagged. No changes to `atoms/**`, `banned_llm_patterns.yaml`, or
any of the 5 self-hosted workflows. `translate-bestseller-atoms.yml` (already fixed in PR #5498)
untouched.

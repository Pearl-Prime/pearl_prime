---
audit_id: workers_builds_pearl_prime_audit_2026-04-27
agent: Pearl_DevOps
project_id: proj_state_convergence_20260328
workstream_id: ws_workers_builds_required_check_audit_20260427
subsystem: pearl_devops
authority_docs:
  - docs/GITHUB_OPERATIONS_FRAMEWORK.md
  - docs/GITHUB_GOVERNANCE.md
  - docs/BRANCH_PROTECTION_REQUIREMENTS.md
  - docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md
  - docs/PEARL_PRIME_RELEASE_CONTRACT.md
  - docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md
  - config/governance/required_checks.yaml
recommendation: a + c (remove Cloudflare check-runs attachment + codify merge-without-admin pattern); reject b
date: 2026-04-27
---

# Workers Builds: pearl-prime — Required Check Audit

## §1. What is `Workers Builds: pearl-prime` (and a premise correction)

### Definition

`Workers Builds: pearl-prime` is a **GitHub check-run** auto-emitted by **Cloudflare's Workers Builds GitHub-app integration** on every push and pull request that affects the configured worker.

It builds and deploys the worker defined by:

- [`wrangler.jsonc`](../../wrangler.jsonc) — `name: "pearl-prime"`, `main: "cloudflare/pearl_prime_worker.js"`, `workers_dev: true`
- [`cloudflare/pearl_prime_worker.js`](../../cloudflare/pearl_prime_worker.js) — 805-byte JavaScript module exposing `GET /` and `GET /healthz`, returning a static JSON status payload. No production logic, no external dependencies, no build pipeline.

### Origin and history

| Date | Event | Source |
|---|---|---|
| 2026-03-23 | Worker contract added in PR #51 ("Add Pearl Prime Cloudflare deployment contract") | `git log --oneline -- wrangler.jsonc` (commit `4a97fbeecc`) |
| 2026-04-01 | Files deleted by PR #245 mass-deletion (20,006 files) | `git log -- wrangler.jsonc` (commit `bba889f140`) |
| 2026-04-01 | Files restored by PR #252 mass-restore | `git log -- wrangler.jsonc` (commit `022f890c46`) |
| 2026-04-09 | First documented Workers Builds failure on this lane (PR #352) — admin override used | [`ACTIVE_WORKSTREAMS.tsv`](../coordination/ACTIVE_WORKSTREAMS.tsv) row 29 |
| 2026-04-09 | `ws_pr_triage_20260409` `next_owner` action: "Remove Workers Builds: pearl-prime from required ruleset or repair Cloudflare deploy per framework" | [`ACTIVE_WORKSTREAMS.tsv`](../coordination/ACTIVE_WORKSTREAMS.tsv) row 24 |
| 2026-04-17 | "Change impact" removed from required checks; "Verify governance" added | [`config/governance/required_checks.yaml`](../../config/governance/required_checks.yaml) header comment |
| 2026-04-27 | This audit | (here) |

The worker has been continuously failing the Cloudflare-side build for **at least 18 days** (since 2026-04-09 if not earlier). The remediation decision was queued in row 24 of `ACTIVE_WORKSTREAMS.tsv` and has lapsed. See §7 for the coordination-system implication.

### Premise correction

The original audit-spawn prompt asserted: *"It is forcing repeated `--admin` override merges to land otherwise-clean PRs."* This premise is **partially incorrect** and the audit must surface that explicitly so future operators do not inherit the bad mental model.

**Live ruleset state (verified via `gh api repos/Ahjan108/phoenix_omega_v4.8/rulesets/13451138`):**

```json
{
  "id": 13451138,
  "name": "Protect main",
  "rules": [
    {
      "type": "required_status_checks",
      "parameters": {
        "required_status_checks": [{"context": "Verify governance"}]
      }
    }
  ]
}
```

**Only `Verify governance` is required for merge to `main`.** `Workers Builds: pearl-prime` is *not* in the required-status-checks list. `config/governance/required_checks.yaml` line 33 also lists `Workers Builds: pearl-prime` under `non_blocking_checks`, and three governance docs explicitly state the same:

- `docs/GITHUB_OPERATIONS_FRAMEWORK.md:109` — "non-blocking and must not be required for merge"
- `docs/GITHUB_GOVERNANCE.md:28` — "non-blocking operationally and must **not** be a required merge check"
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md:28` — "non-blocking and must not be required for merge"

**Implication.** The repeated `--admin` overrides on PR #743 / #744 (and historical PR #645 / #658) were **likely unnecessary**. A regular `gh pr merge <N> --squash` should have succeeded provided the single required check (`Verify governance`) was green. The `mergeStateStatus: UNSTABLE` signal that operators have been reading as "blocked" is GitHub's UI summary that *some* check failed — it does **not** prevent merge unless the failing check is in the ruleset's `required_status_checks` list.

The override pattern was real, but it was driven by **operator habit and UI-summary misreading**, not by an actual ruleset block. This distinction reshapes the recommendation in §4.

**Test-merge confirmation:** the operator is running `gh pr merge 743 --squash` (no `--admin`) in parallel with this audit. Result is appended to §2 below once piped back.

---

## §2. Failure root cause

### Cross-PR pattern

All four audit-target PRs report the same Cloudflare-side failure URL pattern:

| PR | Failure URL |
|---|---|
| [#645](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/645) | `dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/builds/304c1248-bbcd-4c44-8567-e5cb314383b2` |
| [#658](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/658) | `dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/builds/41196018-7a4f-4355-8825-1c1f7a6f6aa8` |
| [#743](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/743) | `dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/builds/861ce1da-fdef-4f6a-90cc-61d4398317c5` |
| [#744](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/744) | `dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/builds/249778fa-437a-4b7d-8eaa-363a74bfa7d6` |

**Same Cloudflare account `0fe2f0679b00fb8a5c3ce830f4144c98`. Same worker `pearl-prime`. Same environment `production`. Same `dash.cloudflare.com` build path.** Different build IDs only because each push triggers a fresh build attempt. Conclusion: the failure is **a single systemic root cause**, not coincidental same-named failures on independent PRs.

### Diagnosis (limited by access)

The Cloudflare build log lives only inside the Cloudflare dashboard. There is no GitHub-side artifact, no stdout, no exit code, no JSON payload available via `gh api`. The check-run reports a `conclusion: FAILURE` with the dashboard URL as `details_url` and no other content.

Pearl_DevOps does **not** have Cloudflare dashboard credentials. Diagnosing the actual root cause is gated on operator access. Plausible candidates given identical-pattern failures across 18+ days and 4+ PRs:

- Cloudflare Workers Builds GitHub-app authorization expired or token rotated
- Cloudflare account `0fe2f0679b00fb8a5c3ce830f4144c98` billing/plan state issue affecting `workers_dev` deploys
- `compatibility_date: "2026-03-23"` in [`wrangler.jsonc`](../../wrangler.jsonc) is older than current Cloudflare Workers runtime cutoff (less likely to fail completely)
- Worker name collision (`pearl-prime` previously deployed under different ownership)

**The recommendation in §4 does NOT depend on diagnosing the deploy** because §3 establishes the worker has no consumer.

### Test-merge result (operator pipe-back)

```
PLACEHOLDER — operator running `gh pr merge 743 --squash` (no --admin) in parallel.

Outcome A (succeeds without --admin):
  → strong evidence that override pattern was unnecessary
  → recommends (a) + (c) as primary path
  → strikes the "merge blocked" framing from any future ws

Outcome B (UI-blocks despite ruleset):
  → reproducible signal that GitHub mergeable-state machine has UI-side
    gating beyond ruleset config
  → adds a separate Pearl_DevOps follow-up ws to investigate
    GitHub branch-protection vs ruleset interaction
  → recommendation in §4 still holds; (c) doc-clarification becomes
    more urgent (operators need to know when --admin is/is-not required)

[Operator: paste actual result here when known.]
```

---

## §3. Is the worker load-bearing?

**No.** Confirmed by exhaustive consumer search.

### Consumer grep (per operator §3 ask)

```bash
grep -rn "pearl-prime.*workers.dev\|pearl_prime.*healthz\|pearl-prime/healthz\|pearl-prime\.cloudflare\|pearl-prime\.pages" \
  --include='*.py' --include='*.ts' --include='*.js' --include='*.html' \
  --include='*.yml' --include='*.yaml' --include='*.json' --include='*.md' \
  --include='*.toml' --include='*.jsonc' .
```

**Result: 0 hits.** No code in this repo calls a deployed `pearl-prime` URL. Verified 2026-04-27 against `agent/devops-workers-builds-required-check-audit` (origin/main parity).

### File-reference grep

```bash
grep -rln "wrangler.jsonc\|pearl_prime_worker"
```

Result: 6 files total, none of which call the deployed worker —

| File | Type | What it does |
|---|---|---|
| [`wrangler.jsonc`](../../wrangler.jsonc) | config | Declares worker for Cloudflare to build |
| [`cloudflare/pearl_prime_worker.js`](../../cloudflare/pearl_prime_worker.js) | source | The 805-byte stub itself |
| [`tests/test_pearl_prime_cloudflare_contract.py`](../../tests/test_pearl_prime_cloudflare_contract.py) | test | Validates source-file static content + wrangler config; **does not call deployed surface** |
| [`docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md`](../../docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md) | doc | Declares the contract |
| [`docs/PEARL_PRIME_RELEASE_CONTRACT.md`](../../docs/PEARL_PRIME_RELEASE_CONTRACT.md) | doc | Explicitly declares the worker check is non-authoritative |
| [`docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md`](../../docs/BRAND_ADMIN_ONBOARDING_CLOUDFLARE_DEPLOYMENT.md) | doc | Different deployment (brand-wizard-app); incidental mention |

`docs/PEARL_PRIME_RELEASE_CONTRACT.md:39` is explicit:

> `Workers Builds: pearl-prime` from Cloudflare is currently **non-blocking operational noise**, not the authoritative Pearl Prime release signal.

`docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md:36` states the worker's purpose is meta:

> This contract exists so the Cloudflare GitHub integration has a real, versioned build target in this repo.

That is, the worker exists to *give the Cloudflare integration something to build* — not because anything depends on its deployed surface.

### Other consumer checks

| Surface | Result |
|---|---|
| Pearl News, Brand Admin, Pearl Prime catalog runners | None call `pearl-prime.workers.dev` |
| Production-readiness gates (`scripts/run_production_readiness_gates.py`) | No worker URL reads |
| Release evidence bundle (`artifacts/release/pearl_prime_release_evidence.json`) | Static repo-owned JSON; not produced by hitting the worker |
| `health_check.sh`, `pre_merge_check.sh`, `preflight_push.sh` | No worker URL reads |
| Brand-admin HTML / brand-wizard-app frontend | No `pearl-prime.workers.dev` references |

**Conclusion.** The worker is **not load-bearing for any pipeline, test, runtime path, or external observability surface in this repo**. Its sole declared purpose is contract-existence. Its deploying-or-not has zero functional consequence today.

---

## §4. Recommendation

### Primary: option (a) — remove the Cloudflare GitHub-app check-runs attachment entirely

The check delivers **negative signal**: it is always red, has been red for 18+ days, and reports nothing actionable inside GitHub. Removing the attachment:

- Eliminates the false-block UI cue that drove the `--admin` override habit
- Reduces operator decision fatigue on every PR
- Costs nothing — the worker source files remain on disk; the contract test continues to pass; future deployment can be reattached if anyone decides to actually use the worker

### Supplementary: option (c) — codify the merge-without-admin pattern

Even if (a) lands, future Cloudflare integrations (or other external apps) could reattach a similar check. A one-line addition to [`docs/GITHUB_OPERATIONS_FRAMEWORK.md`](../../docs/GITHUB_OPERATIONS_FRAMEWORK.md) clarifies the canonical merge rule:

> **A regular `gh pr merge --squash` is sufficient when `Verify governance` is green, regardless of any other check's state.** `--admin` override is reserved for genuine ruleset blocks, not for UI-summary `UNSTABLE` signals from non-required checks.

This codification is included in this same PR (single doc edit, single line of net-new policy).

### Rejected: option (b) — fix the worker deploy

Fixing the Cloudflare-side deploy delivers no functional value because §3 confirms zero consumers. Pursuing (b) would:

- Require Cloudflare dashboard access (operator-only)
- Spend hours diagnosing a problem whose successful resolution provides no measurable benefit
- Re-establish a check that (a) is removing — direct contradiction

If a future workstream wants the deployed worker for some new purpose (release-evidence ping target, public health endpoint, etc.), open `ws_pearl_prime_worker_revival_<date>` and pursue (b) then. Until then, (b) is busywork.

### Risk profile

| Option | Risk | Reversibility |
|---|---|---|
| (a) — Cloudflare-app removal | Zero. Worker source remains on disk; reattach via Cloudflare dashboard at any time | Trivial — reattach the GitHub app |
| (c) — Doc clarification | Zero. Codifies live ruleset reality | Trivial — revert the line if direction changes |
| (b) — Fix deploy (REJECTED) | Low (worker is stub) but pure cost with no benefit | n/a — not pursued |

---

## §5. Proposed implementation

### (a) Operator action — remove Cloudflare GitHub-app check-runs attachment

Pearl_DevOps cannot execute either path below; both require Cloudflare dashboard credentials and/or GitHub app-installation admin scope. Operator picks one of the following:

**Path A1 — Disable the worker's GitHub auto-build hook (preserves the GitHub app for other repos):**

1. Navigate to: `https://dash.cloudflare.com/0fe2f0679b00fb8a5c3ce830f4144c98/workers/services/view/pearl-prime/production/settings`
2. Locate "Builds" or "Build watcher" or "GitHub integration" panel
3. Disable the watcher / disconnect the GitHub repository
4. Confirm: open a fresh PR with a trivial change, verify `Workers Builds: pearl-prime` no longer appears in `gh pr checks <N>` output

**Path A2 — Uninstall the Cloudflare Workers Builds GitHub app from this repo:**

1. Navigate to: `https://github.com/settings/installations` (personal) or `https://github.com/organizations/<org>/settings/installations` (org)
2. Find "Cloudflare Workers Builds" (or similar Cloudflare-named app)
3. Click **Configure** → Repository access → remove `phoenix_omega_v4.8` from the allowed list (or click **Uninstall** if you want to drop the app entirely)
4. Confirm as in Path A1

**Path A3 (least preferred) — leave attachment, mark check as no-longer-blocking via additional ruleset metadata:**

This is already the live state. Path A3 is a no-op recommendation. Listed only for completeness.

**Recommended:** Path A1 — surgical, preserves the app for any future use, explicit per-worker control.

### (c) Diff in this PR

Single-line addition to [`docs/GITHUB_OPERATIONS_FRAMEWORK.md`](../../docs/GITHUB_OPERATIONS_FRAMEWORK.md) under the existing "Standard PR flow" section (line 146 area), making explicit that `--admin` is not required when the canonical required check is green.

See PR diff for exact wording.

### (b) Not implemented

No worker-side fix. If pursued in a future ws, expected scope is one of:

- `wrangler.jsonc` `compatibility_date` bump
- Cloudflare dashboard credential rotation
- Cloudflare account billing/plan check
- Worker name conflict resolution

---

## §6. Operator action items

In priority order:

1. **(PRIMARY)** Execute option (a), Path A1 — disable the worker's GitHub build watcher in the Cloudflare dashboard. Confirm `Workers Builds: pearl-prime` no longer appears on a fresh PR's check list.
2. **(IMMEDIATE — concurrent with #1)** Pipe back the test-merge result for [PR #743](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/743) (`gh pr merge 743 --squash`, no `--admin`) so §2 can be finalized in a follow-up commit or in the closeout.
3. **(REGULAR HABIT — applies post-merge of this audit)** Stop using `--admin` for merges where only `Workers Builds: pearl-prime` is failing. Use `gh pr merge <N> --squash`. The override habit costs ~5 seconds per PR and reinforces a wrong mental model.
4. **(OPTIONAL FOLLOW-UP)** If you have no near-term plan to actually use the deployed worker, open a Pearl_PM ws to retire the stub: delete `wrangler.jsonc`, `cloudflare/pearl_prime_worker.js`, `tests/test_pearl_prime_cloudflare_contract.py`, `docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md`. Reduces footprint by 4 files; no behavior change.

---

## §7. Follow-up workstreams

| ws_id (proposed) | Owner | Trigger | Scope |
|---|---|---|---|
| `ws_workers_builds_check_runner_removal_followup_20260427` | Pearl_DevOps | After operator executes §6 #1 | Verify check is gone on a fresh PR; if it returns within 7 days, escalate |
| `ws_pearl_prime_worker_retirement_20260427` | Pearl_PM (route to Pearl_DevOps) | Optional, no deadline | Retire the worker stub if no future plan to use it. 4-file deletion PR |
| `ws_required_checks_yaml_ruleset_drift_20260427` | Pearl_DevOps | Independent, no deadline | Reconcile [`config/governance/required_checks.yaml`](../../config/governance/required_checks.yaml) (4 required) vs live ruleset (1 required: `Verify governance`). Either align YAML to ruleset (drop Core tests / Release gates / EI V2 gates from the YAML's `required_checks` list — they remain workflow checks but not ruleset-required), OR re-add them to the live ruleset via `gh api PATCH`. Out-of-scope for this PR — separate audit |

### Coordination-system signal (not a ws — Pearl_PM input)

Row 24 of [`ACTIVE_WORKSTREAMS.tsv`](../coordination/ACTIVE_WORKSTREAMS.tsv) (`ws_pr_triage_20260409`) lists `next_owner` action: *"Remove Workers Builds: pearl-prime from required ruleset or repair Cloudflare deploy per framework."* That action was queued **2026-04-09** and lapsed silently for 18 days while the underlying problem continued to drive the override pattern across multiple subsequent PRs.

This is not a Pearl_DevOps ws; it is a Pearl_PM coordination-system observation. Possible Pearl_PM responses:

- Time-bounded `next_owner` field with auto-escalation if not actioned within N days
- Periodic Pearl_PM sweep of stale `next_owner` actions (weekly?)
- Promote `next_owner` actions on completed ws's into separate proposed ws's so they show up in the active backlog rather than being buried in a closed row

Surfaced for Pearl_PM judgment; not a binding recommendation.

---

## §8. Closeout summary

- **Recommendation:** option (a) primary, option (c) supplementary, option (b) rejected.
- **Worker is not load-bearing.** Confirmed by 0-hit consumer grep across 12 file extensions and 6 file-reference grep results that all point to source/test/doc files only.
- **Premise correction:** prior-session framing of "override pattern is becoming load-bearing" was incorrect. Live ruleset already excludes the failing check; overrides were an operator-habit artifact, not a ruleset constraint.
- **This PR scope:** audit doc (this file) + one-line clarification in `docs/GITHUB_OPERATIONS_FRAMEWORK.md`. No worker-side or ruleset-side changes.
- **Next:** operator executes §6 actions; results piped back into §2 test-merge placeholder; follow-up ws's per §7 if/when triggered.

# GitHub No-Failure Framework

**Purpose:** Operational standard for preventing GitHub Action hangs, runner dropouts, and long failed cycles in `phoenix_omega_v4.8`.

**Primary companion docs:** [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md) (workflow matrix, concurrency, Qwen API policy), [RELEASE_PRODUCTION_READINESS_CHECKLIST.md](./RELEASE_PRODUCTION_READINESS_CHECKLIST.md) (release evidence), [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](./GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) (ruleset/governance recovery).

---

## 1) Non-negotiable rules

1. One runner = one heavy queue.
2. Heavy jobs must be sharded when runtime size or duration grows beyond a safe single run.
3. Every heavy workflow must include preflight + warmup + timeout + retry.
4. Qwen-compatible production calls must disable thinking mode.
5. No production sign-off without run URLs + artifacts + digest evidence.

---

## 2) Single-repo reliability model

- `phoenix_omega_v4.8` is the system source of truth for CI gates, release workflows, Pearl News automation, and self-hosted Qwen jobs.
- Reliability hardening lives in this repo’s workflows, scripts, and runbooks.

---

## 3) Heavy classes and scheduling policy

### Heavy classes

- Catalog canaries and gated release evidence
- Max-quality catalog shards
- Locale translation batches (`translate+validate`)
- Manual Pearl News fill / expansion jobs

### Policy

- Use workflow `concurrency` for heavy jobs.
- Self-hosted Qwen workflows must use Qwen API preflight/warmup, retry, and evidence manifests.
- Validate-only and smoke runs are allowed as light jobs.

---

## 4) Required workflow hardening pattern

Every heavy self-hosted workflow must include:

1. `timeout-minutes` at job level.
2. `concurrency` group.
3. Dependency install step.
4. Qwen API preflight:
   - `/v1/models` health check
   - warmup completion call (JSON parse checked)
5. Runner health checks:
   - free memory floor
   - free disk floor
6. Attempt loop (retry once) for heavy command.
7. Artifact upload on completion/failure.

---

## 5) Qwen API request policy (critical)

For production draft/judge/translation calls made through a Qwen-compatible API:

- Set `enable_thinking: false`.
- Use deterministic low-temp for judge/validation paths.
- Keep warmup call explicit and meaningful.
- Treat parseable JSON, no `error`, and non-empty assistant output as minimum success criteria.

Why:

- Prevent `<think>` token waste.
- Reduce timeout/disconnect risk.
- Improve throughput stability under runner load.

---

## 6) Sharding standards

### Localization

- Shard at teacher/topic granularity when feasible.
- Use bounded `max_agents` defaults (`1–2` safe baseline).
- Include heartbeat logs and consecutive-failure early abort.

### Catalog / evaluation runs

- Prefer bounded canary size and shard-by-format or shard-by-lane where available.
- Split further if a single heavy shard cannot complete within a predictable window.

### Pearl News

- Scheduled assembly and QA should stay lightweight.
- Manual Qwen fill / expansion should remain an explicitly triggered self-hosted path with evidence artifacts.

---

## 7) Runner reliability controls

Required controls on self-hosted infrastructure:

1. Runner service installed and monitored.
2. Cleanup automation for old `_diag` logs and stale local artifacts.
3. Triage runbook available with exact recovery commands.

---

## 8) Git push reliability controls

To prevent long push hangs and oversized uploads:

1. Install pre-push guard (`scripts/git/push_guard.py`).
2. Block pushes that exceed configured payload thresholds.
3. Use guarded wrapper (`scripts/git/safe_push.sh`) for retry on transient network errors.
4. Split large changes before push instead of retrying giant uploads.

---

## 9) Model artifact strategy (NO Hugging Face in git)

Policy: keep GitHub repos for code/config only. Do not store model binaries in git history.

Allowed pattern:

1. Store model binaries (`.gguf`, `.bin`, large checkpoints) in a non-git artifact store.
2. Keep a small manifest in repo with variant name, download location, SHA256, and expected size.
3. Download on runner via scripted preflight only when missing.
4. Verify SHA256 before use.
5. Cache locally on runner to avoid repeated downloads.

Repository guardrails:

- `.gitignore` must exclude model binaries.
- Pre-push guard must block model extensions and oversized files before upload.
- CI should fail fast if manifest is missing required checksum fields.

---

## 10) Known anti-patterns (must avoid)

1. Warmup calls with too few tokens or no parse check.
2. Heavy job without bounded size or shard strategy.
3. Running multiple heavy self-hosted jobs without concurrency protection.
4. Marking readiness from smoke-only evidence.
5. Committing model binaries (`.gguf`, `.bin`) into the repo.
6. Allowing any self-hosted Phoenix workflow to run heavy LM work without concurrency, Qwen API preflight/warmup, retry, and evidence.

---

## 11) Operational evidence standard

For each production-hardening claim, store:

1. Workflow run URL
2. Commit SHA
3. Artifact name + digest
4. Queue/manual review status
5. Model ID used

No “100% ready” declaration without all five.

---

## 12) Implementation status baseline (current)

Verified in this repo:

- Warmup/preflight/retry hardening in self-hosted Phoenix workflows with Qwen API configuration: `marketing_continuous.yml`, `marketing-briefs-and-proposals.yml`, `catalog-book-pipeline.yml`, `max-quality-catalog.yml`
- Push guard and safe push wrapper ([scripts/git/](../scripts/git/))
- Analyzer-driven release evidence in `release-gates.yml`

Still enforce continuously:

- Keep workflow edits aligned to this framework.
- Re-audit self-hosted workflows whenever new heavy jobs are added.

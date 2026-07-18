# Cloud-Native Agents — Phoenix Omega

**Status:** Layer 1 active (this PR).
**Owner:** Pearl_GitHub + Pearl_INT.
**Why this exists:** Multiple disk-full incidents on the operator's laptop
(2026-04-25) caused by agents creating ~3 GB git worktrees per task in
`.claude/worktrees/`. Aggregate hit 32 GB and ENOSPC blocked all tool calls.

## Three layers

| Layer | What | Status |
|---|---|---|
| **1** | Codespaces config + remote-mode guard + nightly stale-branch cleanup | this PR |
| **2** | Cloudflare R2 for binary artifacts (renders, portraits, QA outputs) | next PR |
| **3** | Pearl_GitHub + Pearl_INT remote-mode enforcement on Pearl Star | after Layer 2 |

After Layer 1: agent work happens in a **Codespaces VM** with 32 GB ephemeral
disk that dies when you close it. Your laptop never grows worktrees again.

After Layer 2: rendered books, character portraits, and QA-run artifacts move
to **Cloudflare R2** (10 GB free tier). The repo holds only manifests with
SHAs pointing at R2 keys. The `.git` dir stops growing.

After Layer 3: Pearl Star (the Tailnet-attached RTX 5070 Ti) writes renders
straight to R2 instead of the local FS. All hosts that produce artifacts
push to one canonical store.

## How to work after Layer 1 lands

### From your laptop

Don't run agents locally. Open a Codespace:

```
https://github.com/Ahjan108/phoenix_omega_v4.8/codespaces
```

Click **Create codespace on main** (or on whatever branch you want). The
post-create script provisions Python deps, gh CLI, wrangler, and the
Claude Code CLI / VS Code extension. ~90 seconds first time, ~10 seconds
on subsequent opens (Codespaces caches the image).

### Inside the Codespace

Claude Code runs there exactly as on your laptop — same subscription, same
operator-present model. You drive it via the VS Code chat panel or the
terminal. Branch from main, push, open PR. All ephemeral state stays in
the VM. Closing the browser tab pauses the VM; you can resume later.
Codespaces auto-stops after 30 minutes idle.

### Cost on free tier

GitHub free Codespaces gives you **60 hours/month** of 2-core / 8 GB usage
(120 hours with pre-builds, which we don't enable on free tier). Plenty
for daily agent work — most sessions run 1–3 hours. Storage caps at 15 GB
across all your codespaces; the cleanup workflow keeps remote `agent/*`
branches pruned so the codespace doesn't have to fetch 32 GB of stale
branches on resume.

## What enforces this

### `scripts/agent/assert_remote.py`

Single chokepoint. Agent scripts call:

```python
from scripts.agent.assert_remote import assert_remote
assert_remote()
```

Detects whether you're in:
- `codespaces` — `$CODESPACES=true` or `$PHOENIX_OMEGA_REMOTE=codespaces`
- `github-actions` — `$GITHUB_ACTIONS=true` or `$PHOENIX_OMEGA_REMOTE=github-actions`
- `cloudflare` — `$CF_PAGES=1` or `$CF_WORKER` set
- `pearl-star` — marker file `~/.phoenix_omega_pearl_star`
- `local` — none of the above → raises `RemoteModeViolation`

Override (for emergencies only):

```bash
PHOENIX_OMEGA_REMOTE=local-override python scripts/...
```

Prints a loud warning. Do not commit results from override mode.

### `.github/workflows/cleanup-stale-worktrees.yml`

Runs nightly at 03:17 UTC. For every remote `agent/*` branch whose PR has
been **merged or closed for >7 days**, deletes the branch. Open PRs are
always kept. Dry-run mode available via `workflow_dispatch`.

## What's NOT in scope here

- **Autonomous LLM agents in CI.** Phoenix Omega's `llm-policy-enforcement.yml`
  bans paid LLM API reads from repo code. Codespaces preserves the
  operator-present model — Claude Code subscription, you driving it. Actions
  workflows here are deterministic helpers (cleanup, validation, deploy),
  not LLM-driven.
- **Replacing Pearl Star.** The RTX 5070 Ti rig keeps doing FLUX renders on
  Tailnet. Layer 3 just adds an R2 push step so renders end up canonical
  instead of stuck on Pearl Star's local disk.
- **Migrating live worktrees.** Existing `.claude/worktrees/*` on your laptop
  with open PRs are preserved. Cleanup workflow only touches the remote;
  local worktree cleanup is your call (use `git worktree remove`).

## Related docs

- `CLAUDE.md` § LLM Tier Policy — the operator-present rule this honors
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` — single source of truth for env vars
- `skills/pearl-int/SKILL.md` — how Pearl_INT navigates dev portals
- `skills/pearl-github/SKILL.md` — how Pearl_GitHub manages branches
- `docs/AGENT_FILE_PERSISTENCE_PROTOCOL.md` — file-persistence enforcement

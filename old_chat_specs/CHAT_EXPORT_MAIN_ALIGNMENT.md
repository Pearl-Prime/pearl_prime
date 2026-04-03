# Chat export alignment with `main` (Ahjan108/phoenix_omega_v4.8)

**Verified:** 2026-04-03 (local `git` + `gh` against `origin`).

These files under `old_chat_specs/` are **Cursor export transcripts**. Timestamps and mid-session claims (e.g. “PR still open”, “PhoenixControl missing”) can be **stale** even when GitHub `main` has already moved on.

## Answer: are the branches/PRs from those chats merged?

**The PR numbers repeatedly cited in those threads (examples: #78–#89, #93–#94, #103–#113, #121–#124, #130, #134, #138–#139, #144–#145, #179, #181, #184, #187–#188, #211, #241–#244, #250, #252) are merged on GitHub** as of this check.

**Repo facts on current `origin/main`:**

- `PhoenixControl/` is **present** (restored after PR #245; bulk restore PR #252 merged 2026-04-02).
- PR **#245** and **#250** are **MERGED** (contract tightening and CI workflow restore).

## Remote branches that were *not* fully represented by those merges

| Remote branch | Situation | Action taken |
|---------------|-----------|----------------|
| `agent/restore-deleted-files` | PR **#252** merged (squash); tip not an ancestor of `main` | **Deleted** on `origin` (hygiene). |
| `agent/locale-parity-report` | PR **#248** **closed without merge**; branch would **revert** newer `main` index / RunComfy registry rows if merged blindly | **Deleted** on `origin` (avoid mistaken merge). Parity artifact path already exists on `main`. |
| `agent/brand-media-pr-b-visual-identity-ready` | **No PR**; ~54-file slice (visual identity docs, RunComfy cover script, integration env helpers) **not** on `main` | **PR #256** opened for review/rebase: https://github.com/Ahjan108/phoenix_omega_v4.8/pull/256 |

## How to use the listed `.md` exports

Treat them as **narrative history**. For execution, always branch from `origin/main`, run push-guard + preflight from a non-`main` branch, and confirm PR state with `gh pr view <n>`.

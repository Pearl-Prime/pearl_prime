# Agent Commit Identity Remediation Spec

**Purpose:** Resolve the two commit-identity gaps flagged by
`~/.claude/stop-hook-git-check.sh` on `claude/laughing-hawking-vslpdv`
(session `0139k7yQmsM4DUciRDkGeWZh`, 2026-07-22/23):

- (a) agent commits show as **Unverified** on GitHub because no signing key
  is configured in the session environment
- (b) four pre-existing commits already on `origin/main`
  (`9c71488f37`, `9b83905f44`, `505512d91e`, `5fe2c9fdbc`, committer
  `noreply@github.com`) also show Unverified, but are shared upstream
  history authored by other sessions/PRs — not something this session may
  rewrite unilaterally

**Status:** Open. Blocked on infra/credential provisioning outside repo
scope (see §1) and a governance decision (see §2). Not started.

**Primary owner:** Pearl_GitHub, with Pearl_PM sign-off required before any
work under §2 begins.

**Related:** this same session is also blocked on a separate, likely-related
infra issue — `403 Resource not accessible by integration` on every
branch-ref-creation attempt (`git push` to a new branch, and the
`create_branch` / `push_files` / `create_or_update_file` GitHub MCP tools all
fail identically). That is tracked as its own item, not part of this spec,
because it blocks *landing* work rather than *signing* it — but the same
GitHub App installation is the likely fix point for both, so whoever
provisions credentials for §1 should check installation permissions
(`contents: write`, ref creation) at the same time.

---

## 1. Goal (a): commit-signing credentials in the session environment

### Problem

Claude Code sessions in this environment commit as `Claude
<noreply@anthropic.com>` (author + committer identity is already correct)
but have no GPG or SSH signing key configured. Per this session's operating
rules, `git commit --no-gpg-sign` / disabling signature verification is
never used to paper over this — the fix has to be a real key, provisioned
once at the environment level, not a per-session workaround.

### Acceptance criteria

1. A signing key (GPG or SSH, whichever this org's GitHub org/repo settings
   accept — check **Settings → SSH and GPG keys** requirements for the
   `48social` / `Pearl-Prime` org) exists and is available inside the
   Claude Code Remote session container for every session working in this
   repo, not just this one.
2. `git config --global commit.gpgsign true` (or `gpg.format ssh` +
   `user.signingkey` for SSH signing) is set as part of session bootstrap —
   either baked into the environment image/setup script, or injected via
   the same mechanism that currently sets `user.name` /
   `user.email` for agent commits.
3. A fresh session's first commit in this repo shows **Verified** on
   GitHub without any manual step by the agent.
4. `~/.claude/stop-hook-git-check.sh` stops flagging new agent commits as
   `N` (no signature).

### Non-goals / explicit exclusions

- This does **not** cover signing commits authored by *other* sessions,
  humans, or CI bots (e.g. the `noreply@github.com` committer seen in
  merged PRs) — those are out of scope; see §2 for why those are handled
  differently.
- Do not implement this by disabling signature *requirements* on the
  `main` branch ruleset to make the warning go away — that weakens
  verification for everyone. The fix is a real key, not a lowered bar.

### Suggested implementation path (for whoever provisions this)

1. Generate (or reuse an existing) signing identity for the `Claude
   <noreply@anthropic.com>` commit identity used by Claude Code Remote
   sessions.
2. Register the public key against the GitHub account/App that owns commits
   in this repo (`48social`, per `mcp__github__get_me` in this session).
3. Add the private key material + `git config` invocation to this
   environment's session bootstrap (wherever `user.name`/`user.email` are
   currently injected — that mechanism already exists, since every session
   in this repo starts with correct author identity).
4. Verify with a throwaway commit on a scratch branch, confirm "Verified"
   badge on GitHub, then delete the scratch branch.

---

## 2. Goal (b): pre-existing Unverified commits already on `origin/main`

### Problem

`9c71488f37`, `9b83905f44`, `505512d91e`, `5fe2c9fdbc` are commits from
already-merged PRs (other Claude Code sessions' work, committer
`noreply@github.com`) that this session's local `claude/laughing-hawking-vslpdv`
branch picked up via a fast-forward merge from `origin/main`. They predate
this session, are already shared upstream history, and are not this
session's commits to rewrite.

### Why this is a governance decision, not a mechanical fix

Rewriting already-merged commits on `origin/main` (via `git commit --amend
--reset-author` + `git rebase --exec` per the stop-hook's own suggested
recovery, followed by a force-push) means:

- **Changing SHAs of commits other PRs/branches may already be based on** —
  any branch that forked after those commits would need to be rebased too,
  or its history silently diverges from `main`.
- **A force-push to `main`**, which `docs/BRANCH_PROTECTION_REQUIREMENTS.md`
  and `skills/pearl-github/SKILL.md` both list as a non-negotiable "never do
  this" (`main` requires PR-only merges, no force pushes, no admin bypass).
- Losing the original commit's verification/provenance trail for commits
  that may already be referenced in `docs/BRANCH_INVENTORY_*.md`, PR links,
  or `artifacts/qa/*` closeout receipts by SHA.

None of this is appropriate for a single session to decide unilaterally
just because a local stop-hook flagged it. It needs explicit,
repo-owner-level sign-off before any agent attempts it.

### Acceptance criteria (if and only if approved)

1. Pearl_PM (or the repo owner, Nihala/Ma'at per
   `skills/pearl-github/SKILL.md` §Identity) explicitly authorizes rewriting
   history on `main` for these specific commits, in writing, in this file
   or a linked decision doc.
2. A full inventory of what references these SHAs by hash (other branches,
   `docs/BRANCH_INVENTORY_*.md`, QA closeout receipts, PR descriptions) is
   completed and each reference is either updated or confirmed
   SHA-independent, **before** the rewrite.
3. The rewrite happens via a single coordinated maintenance window: fetch
   latest `origin/main`, `git rebase --exec "git commit --amend --no-edit
   --reset-author"` from the parent of the oldest flagged commit forward,
   force-push with `--force-with-lease` (never plain `--force`), and
   immediately verify no other open branch/PR was based on the rewritten
   range without being rebased in the same window.
4. Post-rewrite, confirm all four commits show **Verified** (requires §1's
   signing key to be available at rewrite time) and that
   `stop-hook-git-check.sh` is clean for the full `main` history it checks.

### Recommended default if no sign-off is given

Leave the four commits as Unverified permanently. An Unverified badge on
already-merged, already-reviewed history is a cosmetic/provenance issue,
not a security one (the commits are already on `main`, already passed
required status checks and review at merge time). This is very likely the
right default — §2 should only proceed if Pearl_PM has a concrete reason
(e.g. an external compliance requirement) that outweighs the force-push
risk above.

---

## 3. Verification checklist

- [ ] §1: fresh Claude Code Remote session's first commit in this repo
      shows Verified on GitHub, no agent action required
- [ ] §1: `stop-hook-git-check.sh` no longer flags new agent commits
- [ ] §2: explicit sign-off obtained and recorded here, **or** this
      section is closed as "declined, cosmetic-only" by Pearl_PM
- [ ] (if §2 proceeds) reference inventory completed and confirmed clean
      post-rewrite
- [ ] Related branch-ref-creation permission issue (see header) checked
      against whatever credential/App-permission change resolves §1

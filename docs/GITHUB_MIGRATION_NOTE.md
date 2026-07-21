# GitHub Account Migration — 2026-07-21

`origin` (`Ahjan108/phoenix_omega_v4.8`) remained 403/suspended as of this date.
Full repo history was migrated to `Pearl-Prime/pearl_prime` under a partner account
(a different email/identity, per GitHub's multi-account policy — not a suspension
workaround for the same identity).

## Method
History landed in incremental checkpoints (the 44GB `.git` — 24GB objects + 19GB
LFS — was too large for a single push). One merge commit in the chain
(`97aab39367bc2e255116eaa06a5875f7ee19054c`, merging PR #5175
`codex/phoenix-worktree-cleanup`) reproducibly failed to transfer
(`did not receive expected object 0140d761c03829b4f3e58ec91e4cb5dc0640aa0b`)
across every variant tried (`--no-thin`, HTTP/1.1, fresh branch, larger buffers).
Root cause undetermined at landing time — under separate investigation.

To keep landing content, everything from that point to the local HEAD
(`a1ced02986...`) was squashed into one synthetic commit
(`beba62561b17d1c032005215c2c7b90fc390158a`) carrying the exact same file tree as
HEAD (`9a4decbf5b5ca86a18443128fd379e1c8bd048ae` — verified byte-identical against
the remote via the GitHub API), with clean history up to that point. Full
commit-by-commit history for the ~2026-06-30 to 2026-07-21 span is preserved
locally and on `pearlstar_offline`; it can be replayed once the underlying object
issue is understood.

## Remotes
- `origin` — `Ahjan108/phoenix_omega_v4.8` (suspended, kept for possible appeal/recovery)
- `origin` now points to `Pearl-Prime/pearl_prime` (primary, per operator decision 2026-07-21)

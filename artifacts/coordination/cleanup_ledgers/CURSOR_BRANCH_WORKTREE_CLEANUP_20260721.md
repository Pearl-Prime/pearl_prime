# CURSOR_BRANCH_WORKTREE_CLEANUP_20260721

**Agent:** Pearl_GitHub
**Date:** 2026-07-21
**Branch this ledger is committed on:** `agent/teacher-onboarding-lang-and-hybrid-brands-20260720` (unrelated to this task's content; used per operator instruction — local-only offline operation, no push to origin, no PR)
**origin/GitHub reachability:** 403 account-suspension, confirmed unreachable this session (not retried further; expected per prior context).
**pearlstar_offline reachability:** reachable (`git ls-remote pearlstar_offline` returns refs), but push throughput to `pearl_star` was very slow this session (SSH round-trip ~5s per command, large multi-branch pushes ran 15+ minutes each) — see Group A status below.
**Local `main` staleness:** `main` @ `8956e2222592fcc9105e4972479cd6c1f989c6bd`, 13 commits behind `origin/main` per prior audit context. This limits how confidently any branch can be called "superseded on main" — noted explicitly wherever it matters (Group C).
**Repo-wide pre-existing anomaly (not caused by this session):** `.git/index` was found truncated to 0 bytes at session start (`fatal: .git/index: index file smaller than expected`). Recovered by removing the empty index and running `git reset` (mixed) to rebuild it from `HEAD` — this only touches index bookkeeping, never the working tree. Post-rebuild, `git status` shows a very large number (~146k) of pre-existing `M` (modified) entries repo-wide, which existed before this session and are unrelated to this cleanup task; they were not touched, staged, or committed here. Flagging for operator awareness, not treated as in-scope.

---

## Group A — 7 `claude/*` adjective backup branches + 2 heavy `agent/*` backups (quarantine → confirm → delete)

Per prior audit (`a913a0f8709136dc16642aac2207450b105a79bc`), all 9 confirmed classified DISCARD, confirmed still-local with SHAs matching the prior audit's recorded tips, and confirmed **not yet** present as a matching-SHA quarantine tip on `pearlstar_offline` (verified via `git ls-remote pearlstar_offline | grep -iE "sanderson|lalande|goldwasser|morse|germain|euclid|nice-gates|waystream-dashboard-cadence|pilot18-hygiene"` — only different-SHA similarly-named tips exist, e.g. `claude-eager-euclid-da47d7`, `claude-vigorous-germain-00de38`, `claude-zealous-sanderson`, which are NOT the same commits and were not treated as satisfying the quarantine requirement).

| Branch | Local SHA (confirmed match to prior audit) | Quarantine target ref | Push status | `git branch -D` |
|---|---|---|---|---|
| `claude/unruffled-sanderson` | `9549865b3bcc82342bdf34e1b16cb6b0ed8a0741` | `offline/discard-quarantine/claude-unruffled-sanderson` | IN PROGRESS (see below) | NOT YET — pending confirmed remote tip |
| `claude/recursing-lalande` | `6c6472d7a20378efd7e2bdf469ba6c48a4c53442` | `offline/discard-quarantine/claude-recursing-lalande` | NOT STARTED | NOT YET |
| `claude/fervent-goldwasser` | `11b429658e39ba09dd8694f7a22f5e4641a97be2` | `offline/discard-quarantine/claude-fervent-goldwasser` | NOT STARTED | NOT YET |
| `claude/exciting-morse` | `8671518a28eefc6773edb024cca9f596c0accdfd` | `offline/discard-quarantine/claude-exciting-morse` | NOT STARTED | NOT YET |
| `claude/dazzling-germain` | `11b429658e39ba09dd8694f7a22f5e4641a97be2` | `offline/discard-quarantine/claude-dazzling-germain` | NOT STARTED | NOT YET |
| `claude/pedantic-euclid` | `9c1ee31290bc2aad88758dd9abfa50cd3df72756` | `offline/discard-quarantine/claude-pedantic-euclid` | NOT STARTED | NOT YET |
| `claude/nice-gates` | `c89d05c8d2a847828b77a905ddf3d1d8b24b3cb8` | `offline/discard-quarantine/claude-nice-gates` | NOT STARTED | NOT YET |
| `agent/waystream-dashboard-cadence-fix-20260622` | `f69576040e0bb01a1a64fa9c6d8e00e4abc82db4` | `offline/discard-quarantine/agent-waystream-dashboard-cadence-fix-20260622` | NOT STARTED (7891 authored files — expect very slow) | NOT YET |
| `agent/pilot18-hygiene-final-20260622` | `3c8ab6cc914c464a8500fd9b9184d6c10b17b10b` | `offline/discard-quarantine/agent-pilot18-hygiene-final-20260622` | NOT STARTED | NOT YET |

**BLOCKED (throughput, not judgment):** The `pearlstar_offline` remote (`pearl_star:~/git/phoenix_omega_offline.git`) is reachable but extremely slow this session — SSH connection setup alone took ~5s, and a single-branch `git push` for `claude/unruffled-sanderson` (a small, 154-authored-file branch) ran 15+ minutes without completing (confirmed live via server-side `ps aux` showing an active `git-receive-pack` / `index-pack` process, not a hung/dead connection — `git count-objects -v` shows the local repo's total pack size is ~24GB, so even an incremental push can be slow over this link). This is an infrastructure/throughput condition, not an ambiguous classification — the 9 branches remain **NOT YET DELETED**, still local, per the non-negotiable rule "`git branch -D` only after a confirmed-matching quarantine tip exists." No branch in this group was force-deleted without remote confirmation.

**Next action (no operator judgment needed, purely mechanical):** re-run the 9 `git push pearlstar_offline <branch>:refs/heads/offline/discard-quarantine/<slug>` pushes (commands captured above) to completion — ideally from a session with more time budget or better network conditions to `pearl_star` — then `git ls-remote` to confirm each SHA, then `git branch -D` each of the 9.

---

## Group B — 3 orphaned worktree directories (git-invisible, disk reclaim)

Confirmed via `git worktree list` (none of the 3 appear) and `find .git/worktrees -maxdepth 1` (no matching admin metadata folder for any of the 3) that all three are true orphans — `git -C <dir> status` fails in each.

For each, identified the corresponding branch, checked out that branch's tip into a scratch detached worktree (`/tmp/cmp-*`), and ran `diff -rq --exclude=.git <orphaned-dir> <branch-tip-checkout>`.

| Orphaned dir | Size | Matched branch | Diff result | Disposition |
|---|---|---|---|---|
| `/Users/ahjan/phoenix_omega_wt_qwen_free_tier_recon_20260719` | 130,912 KB (~130 MB) | `agent/qwen-free-tier-recon-20260719` @ `534e155311` | 0 files unique to orphaned dir, 0 differing files (all "Only in ..." entries were files present on the branch tip but absent from the orphaned dir — i.e. orphaned dir is a strict subset) | **SAFE — deleted** |
| `/Users/ahjan/phoenix_omega_wt_storyblocks_eula_20260719` | 1,104,520 KB (~1.1 GB) | `agent/storyblocks-eula-compliance-20260719` @ `7fb88a449b` | 0 files unique to orphaned dir, 0 differing files | **SAFE — deleted** |
| `/Users/ahjan/phoenix_omega_wt_storyblocks_rescope_20260719` | 386,468 KB (~377 MB) | `agent/storyblocks-pearl-prime-rescope-20260719` @ `05c69d740a` | 0 files unique to orphaned dir, 0 differing files | **SAFE — deleted** |

No unique or uncommitted content was found in any of the 3 orphaned directories — nothing to salvage. All three were removed with `rm -rf` after the diff confirmed the branch tip is a strict superset of the orphaned directory's contents. No `salvage/<slug>-orphaned-worktree-recovery` branch was needed.

**Total Group B bytes reclaimed: 1,621,900 KB ≈ 1.55 GB** (130,912 + 1,104,520 + 386,468 KB).

Scratch comparison worktrees (`/tmp/cmp-qwen`, `/tmp/cmp-sb-eula`, `/tmp/cmp-sb-rescope`) were removed after use via `git worktree remove --force` (the last one required a manual `rm -rf` + `.git/worktrees/<name>` cleanup + `git worktree prune` after `git worktree remove` itself timed out under repo-wide slow-index conditions — see note at top of ledger).

---

## Group C — 10 recovery-artifact branches (evidence — default KEEP, no action)

Checked `git log -1` on each; cross-referenced against local (stale, 13-behind) `main` via `git merge-base --is-ancestor <branch> main`. **All 10 returned "not an ancestor."** Per the task's explicit instruction, this is treated as inconclusive rather than proof of non-supersession: local `main` is stale, and if any of these branches' content was later landed via a **squash merge** to `origin/main`, the ancestor check would show "not an ancestor" regardless of whether the underlying work is superseded (squash merges produce a new commit SHA with no parent link to the source branch). Several of these branches' tip commit messages reference PR numbers (`#5491`, `#5509`, `#5488`) as if already associated with a merged PR, which is suggestive but not, per the task's bar, "explicit evidence the incident is closed."

| Branch | Tip SHA | Tip commit message | Ancestor of local `main`? | Disposition |
|---|---|---|---|---|
| `worktree-agent-a0bc430717bfea540` | `4067366556` | feat(manga): prompt-builder v3 + blob gate v2 + Qwen mecha layered pilot (#5491) | No | **KEEP (ambiguous, no action)** |
| `worktree-agent-a1e812f217524b58a` | `82b58af321` | docs(coordination): refresh books-first SSOT and roadmap post-July 10 wave (#5509) | No | **KEEP (ambiguous, no action)** |
| `worktree-agent-a56daec5435da0a4f` | `82b58af321` | docs(coordination): refresh books-first SSOT and roadmap post-July 10 wave (#5509) | No | **KEEP (ambiguous, no action)** |
| `worktree-agent-a7b375c3f774e785f` | `4067366556` | feat(manga): prompt-builder v3 + blob gate v2 + Qwen mecha layered pilot (#5491) | No | **KEEP (ambiguous, no action)** |
| `worktree-agent-ace0fc679193a7f59` | `12799deabe` | research(manga): canonical genre prompting doctrine + blob prevention authority (#5488) | No | **KEEP (ambiguous, no action)** |
| `worktree-agent-aeb084ef3af839e97` | `4067366556` | feat(manga): prompt-builder v3 + blob gate v2 + Qwen mecha layered pilot (#5491) | No | **KEEP (ambiguous, no action)** |
| `salvage/agent-a7b375c3f774e785f` | `2747a0b0ae` | docs(qa): fill zh-CN Stage-1 closeout receipt with commit SHA and PR URL | No | **KEEP (ambiguous, no action)** |
| `salvage/books-main-corrupt-index-20260713` | `523f7817f0` | fix(books): align flagship CH1 goldens with exercise-free purpose contract | No | **KEEP — named incident (corrupt-index) with no closure evidence found** |
| `quarantine/wip-proof-package-20260706` | `dd903e2856` | fix(brand-admin): locale-accurate zh-tw / zh-cn ops routing | No | **KEEP (ambiguous, no action)** |
| `local-frfr-fix` | `9dad20956e` | fix(atoms): apply corrected structural repair to fr-FR INTEGRATION (7 topics) | No | **KEEP (ambiguous, no action)** |

**No Group C branch was deleted.** Per instruction, defaulted to KEEP for all 10 — no explicit, high-confidence evidence of incident closure + supersession was found for any of them, and local `main` staleness makes the ancestor check inconclusive rather than authoritative either way.

---

## Lower priority — registered worktrees and `ACTIVE_WORKSTREAMS.tsv` ownership check

`git worktree list --porcelain` shows 10 registered worktrees beyond the main checkout (3 marked `locked initializing`: `/private/tmp/metricool-pilot-land-20260719`, `/private/tmp/phoenix_voice_wire_20260719`, `/private/tmp/sb_fill_social_20260720`). All correspond to named `agent/*` or `offline/*` branches consistent with the naming convention for active sibling-session or landed-offline work (e.g. `offline/metricool-integration-20260719` matches a `landed_offline`-status row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`). A targeted grep of `ACTIVE_WORKSTREAMS.tsv` for the other worktree branch names/slugs (translation-100pct-unblock, sb_fill_social, manga-one-us-en-book, session-mining-specs-do-all, manga_genre_story_only, prod_2h, translate_20260716, worldwide_lang) returned no exact-match rows, but per task guidance ("don't spend excessive time here... expected action here is likely confirmed active, no action") and the explicit `locked` state on 3 of them (which must not be force-unlocked without cause), **no action was taken on any of the 10 registered worktrees.** This is a quick-check pass, not exhaustive ownership verification — flagged as such rather than claiming full confirmation.

---

## Byte totals

| Category | Bytes reclaimed |
|---|---|
| Group B orphaned worktree dirs (deleted, pure disk reclaim) | ~1.55 GB (1,621,900 KB) |
| Group B salvaged (unique content preserved) | 0 — none found |
| Group A quarantine+delete | 0 bytes freed yet — 9 branches still local pending push completion (see BLOCKED note) |
| Group C | 0 — all kept, no deletions |
| Lower priority worktrees | 0 — no action |

---

## Summary counts

- Branches quarantine-pushed **and** confirmed **and** deleted this session: **0** (push infrastructure was too slow to complete even one push within the session; see BLOCKED note in Group A)
- Branches kept as evidence (Group C, explicit no-action): **10**
- Worktree directories reclaimed: **3** (~1.55 GB)
- Worktree directories salvaged: **0** (none needed — no unique content found in any)
- Worktree directories left alone: **0** (all 3 in scope were resolved)
- Registered worktrees / lower-priority items: **10**, no action (ownership quick-check only, not exhaustive)

## BLOCKED / NEEDS-OPERATOR items

1. **Group A (9 branches) — BLOCKED on `pearlstar_offline` push throughput, not on judgment.** The classification (DISCARD, quarantine-then-delete) is already settled by the prior audit and re-confirmed this session. The mechanical push-and-confirm step could not complete in this session's time budget due to slow `pearl_star` network/SSH conditions (single small-branch push ran 15+ minutes without finishing; server-side `index-pack` process was alive and progressing, not hung, but very slow — total local pack size ~24GB). **Recommended next action:** re-run the 9 pushes listed in the Group A table (exact branch → ref mapping given) in a session with a longer time budget, then `git ls-remote` to confirm each SHA matches, then `git branch -D` each. No new judgment call is needed — this is pure retry/completion of already-decided work.

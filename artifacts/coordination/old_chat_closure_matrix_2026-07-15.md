# Old Chat Closure Matrix - 2026-07-15

Dispatcher: Pearl_PM_Dispatcher
Prompt pack: `docs/agent_prompt_packs/20260715_old_chat_closure_audit/`
Live `origin/main`: `319ad84af8c3dfd3770bf3b08acd3bf6cfa6b44b`
Open PR count: `1611`
Worktrees registered: `50`
Disk tier: emergency-low for local execution (`/System/Volumes/Data` showed `11Gi` available, 98% used during unblock-wave lane 01).

## Dispatcher Finding

This pack cannot close as MERGED in the local checkout. The root worktree was already heavily dirty and then changed branches during read-only dispatch probes:

- initial root during fetch/worktree probe: `codex/harbor-line-kamiko-fix` at `fea3c26547`
- later root during status probe: `codex/registry-40x14-waystream` at `45eda6ddf0`
- current root dirty entries during final status: 247

Because the prompt pack requires no local-only finish, no broad cleanup, no branch mutation in a dirty shared tree, and no new worktrees under 50Gi free, every implementation/cleanup lane is terminal BLOCKED until a clean cloud or sparse branch is used.

## Live PR Truth

| PR | Live state | Check/merge state | Dispatcher action |
| --- | --- | --- | --- |
| #5206 | OPEN | CONFLICTING, checks SUCCESS | BLOCKED: stale evidence-only PR; do not merge without split/rebase. |
| #5237 | OPEN | CONFLICTING, checks FAILURE | BLOCKED: broad craft lane plus red checks and poisoned local reconcile worktree. |
| #5295 | OPEN | CONFLICTING, checks SUCCESS | HOLD: owner/operator-gated in PROGRAM_STATE. |
| #5518 | OPEN | CONFLICTING, checks FAILURE | BLOCKED: agent fabric docs absent from `origin/main`; not live authority. |
| #5581 | OPEN | MERGEABLE, checks SUCCESS | HOLD: not processed because lane 02 smoke gate failed first. |
| #5585 | OPEN | MERGEABLE, checks SUCCESS | HOLD: not processed because lane 02 smoke gate failed first. |
| #5596 | OPEN | MERGEABLE, checks SUCCESS | HOLD: not processed because lane 02 smoke gate failed first. |
| #5629 | OPEN | mergeability UNKNOWN from live API, checks SUCCESS | BLOCKED for lane 04: live PR file list still spans research scripts, docs, examples, workflow, and skill files; replace with a narrower research successor before merge. |
| #5636 | OPEN | DRAFT, mergeability UNKNOWN, checks SUCCESS except skipped auto-merge | BLOCKED: freebie post-experience work remains preserved on remote branch/PR but cannot merge while draft. |
| #5645 | OPEN | mergeability UNKNOWN from live API, Core tests FAIL | BLOCKED: lane 02 smoke merge candidate is not green. |

Already merged and not to requeue: #5539, #5576, #5578, #5582, #5592, #5598, #5599, #5600, #5601, #5602, #5603, #5604, #5605, #5606, #5620, #5627, #5630, #5632, #5633, #5635, #5637, #5639, #5640, #5641, #5642, #5643, #5644, #5646.

## Worktree Truth

| Path | Branch | HEAD | Status count | Verdict |
| --- | --- | --- | ---: | --- |
| `/Users/ahjan/phoenix_omega` | branch changed during run | `fea3c26547` then `45eda6ddf0` | 247-254 | HOLD: active shared checkout, do not mutate. |
| `/Users/ahjan/phoenix_omega_worktrees/freebie-post-experience-capture-pr-update` | `codex/freebie-post-experience-capture-pr` | `8096cbaeef` | 0 | HOLD: backs open draft/conflicting #5636. |
| `/Users/ahjan/phoenix_omega_worktrees/pr5237_atom_cohesion_reconcile_20260714` | `codex/pr5237_atom_cohesion_reconcile_20260714` | `7914b45693` | 286278 | BLOCKED/HOLD: poisoned checkout shape; preservation-first recovery required. |
| `/Users/ahjan/phoenix_omega_worktrees/pr5581-config-validation-fix-20260715` | `codex/pr5581-config-validation-fix-20260715` | `33249da925` | 0 | HOLD: backs an open mergeable PR. |
| `/Users/ahjan/phoenix_omega_worktrees/pr5585-conflict-fix-20260715` | `codex/pr5585-conflict-fix-20260715` | `e2b9e1ff87` | 0 | HOLD: backs an open mergeable PR. |
| `/Users/ahjan/phoenix_omega_worktrees/pr5596-conflict-fix-20260715` | `codex/pr5596-conflict-fix-20260715` | `c9c2cdc66e` | 0 | HOLD: backs an open mergeable PR. |
| `/Users/ahjan/phoenix_omega_worktrees/manga-100pct-dispatch-run-20260714` | `codex/manga-100pct-audit-refresh-20260714` | `0a84d1ddc1` | 3 | HOLD: possible local manga audit residue. |
| `/Users/ahjan/phoenix_omega_worktrees/mecha-native-proof-20260710` | `agent/pr5237-cloud-reconcile-20260710` | `321379f8f8` | 20 | HOLD: stale but dirty; do not delete. |
| `/Users/ahjan/phoenix_omega_worktrees/ws-manga-true-layered-webtoon-proof-20260710` | `agent/ws-manga-true-layered-webtoon-proof-20260710` | `2d9ada1e21` | 620 | HOLD: dirty proof worktree; do not delete. |
| `/Users/ahjan/phoenix_omega_worktrees/final-books-first-auditor-20260714` | `codex/final-books-first-auditor-20260714` | `19edc45e0b` | 2 | HOLD: small dirty residue; verify before deletion. |

No worktrees were removed. No branches were deleted. No cleanup was attempted because the checkout was actively changing and disk was emergency-low.

## Old Chat Claim Matrix

| Chat | Evidence lines | Subsystem | Owner | Current live state | Required action | Lane |
| --- | --- | --- | --- | --- | --- | --- |
| `Untitled 315.txt` | lines 2-15, 31-100, 213-217, 439 | brand_admin, localization | Pearl_Brand, Pearl_Localization | Harbor Line #5639 is merged at `322aefb4df...`; `stabilizer_en_us` assigns Kamiko Parker and delivery JSON truthfully says production files pending. #5635/#5643/#5646 are merged. | Do not reimplement Harbor or zh-TW fallback work. HOLD root worktree until unrelated dirty state is preserved. | 06, 03 |
| `Untitled 317.txt` | lines 5-7 | books-first, repo coordination | Pearl_PM, Pearl_GitHub | Books-first wave merge receipts are mostly live; #5206 and #5237 remain blocked. | Keep #5206/#5237 blocked with remote surfaces; do not batch-merge. | 02, 03 |
| `Untitled 318.txt` | lines 5-9 | books-first, repo coordination | Pearl_PM, Pearl_GitHub | Same as chat 317, with cleanup incomplete for blocked reconcile lanes. | Preserve blockers; cleanup only after poisoned worktrees are audited. | 02, 03 |
| `Untitled 319.txt` | lines 7-149 | research | Pearl_Research | Research prompt-generation layer exists locally/untracked; absent from `origin/main`. #5629 is not a safe narrow carrier. | Create clean branch from `origin/main` in cloud/sparse checkout, cherry-pick only research files, test, PR. | 04 |
| `Untitled 320.txt` | lines 77-106, 190-204 | research | Pearl_Research | Confirms local implementation was not committed/PR'd/merged. | Same as chat 319. | 04 |
| `Untitled 321.txt` | lines 1-90 | brand_admin, freebies | Pearl_Brand | Freebie post-experience capture remains #5636, open draft/conflicting/no checks. | Resolve #5636 conflicts on remote branch or split successor PR; do not force-merge. | 06 |
| `Untitled 322.txt` | lines 5-18, 78-85, 112-162 | pearl_prime QA | Pearl_Prime | Stress runner is local/untracked; #5633 and #5644 merged; #5645 red Core tests; 1k run is unsafe locally. | Fix #5645 Core failure or replace with narrow successor; then rerun bounded smoke/pilot in cloud. | 05 |
| `Untitled 323.txt` | lines 73-117, 155-223, 329-396 | router, books100, manga prompt pack | Pearl_PM, Pearl_GitHub | Router v4 is in `agent_brief`; #5598-#5606 are merged; #5620 manga prompt pack is merged. | No requeue for those PRs; keep prompt-pack cleanup as follow-up only. | 01, 07, 09 |
| `Untitled 324.txt` | lines 5-18, 47-85, 113-178 | pearl_prime QA | Pearl_Prime | Duplicate stress-run thread; local runner still unmerged. | Same as chat 322. | 05 |
| `Untitled 325.txt` | lines 4-89, 100-119, 148-220, 255-262 | manga_pipeline | Pearl_Dev | V5 structural assembly bridge #5582 is merged; old prompt-pack work has later #5620. | Do not reimplement V5 bridge; cleanup/HOLD stale manga worktrees after preservation. | 07, 03 |
| `Untitled 326.txt` | lines 5-63 | GitHub, enhancement contract | Pearl_GitHub | #5592 is merged at `0406c643...`. | No action except cleanup of stale branches if safe. | 02, 03 |
| `Untitled 327.txt` | lines 6-31, 65-79 | enhancement contract | Pearl_Prime | #5578 is merged at `f986fa7c...`. | No action except cleanup of stale proof worktree if safe. | 02, 03, 07 |
| `Untitled 328.txt` | lines 1-99 and result block | manga_pipeline | Pearl_Dev | A/B/C manga prerequisite PR #5576 is merged at `fd96785f...`; overall manga GREEN still not proven. | No reimplementation; keep PROVEN-AT-BAR/operator read separate. | 07 |
| `Untitled 329.txt` | lines 88-194, 320-565 | manga, external skills audit | Pearl_PM, Pearl_Research | Manga cloud/bar claims remain operator/auth gated; Matt Pocock skills audit artifacts exist locally/untracked. | Record blocker; do not vendor external repo or claim manga bar green. | 07, 08 |
| `Untitled 330.txt` | lines 9-31, 44-132 | manga cloud, teacher/music | Pearl_Int, Pearl_Dev | #5539 cloud substrate closeout merged; #5541/#5543 referenced as merged in old chat but not in pack PR set. | Rerun cloud substrate only after real auth; do not use dirty local fallback. | 07 |
| `Untitled 331.txt` | lines 1-194, 387-453 | pearl_prime book path | Pearl_Prime | Book-path exploratory prompts, no clear current merge target in pack. | Treat as evidence for dev-content salvage; no local render under low disk. | 08 |
| `Untitled 332.txt` | lines 7-65, 77-129, 237-346 | manga_pipeline | Pearl_Dev, Pearl_Research | Human readability/stillness gap work partly represented on main, but local-only artifacts/worktrees remain dirty. | Verify from clean checkout; do not claim PROVEN-AT-BAR. | 07 |
| `Untitled 333.txt` | lines 1-40 | pearl_prime CLI | Pearl_Prime | Historical CLI verification question; current PROGRAM_STATE supersedes. | No implementation; route future CLI truth checks to PROGRAM_STATE plus live `origin/main`. | 08, 09 |
| `Untitled 334.txt` | line 68 | repo hygiene | Pearl_GitHub | Old cleanup advice conflicts with current active dirty worktrees. | Do not delete Claude/Cursor/worktrees without preservation manifest. | 03 |
| `Untitled 335.txt` | lines 3-143, 197-218, 321-621 | audiobook_pipeline | Pearl_Dev | Legacy audiobook templates may be valuable but are not proven ingested; `/tmp` provenance unresolved. | Preserve with manifest from source zips; no repo import without license/provenance. | 08 |
| `Untitled 336.txt` | lines 12-15, 48-80, 93-157, 227-280, 331 | video_pipeline | Pearl_Video/Pearl_Dev | Video lane had branch drift and dirty-worktree issues; no safe current implementation lane in this pack. | Recreate narrow cloud/sparse continuation from authority docs and handoff; do not use dirty root. | 08 |
| `Untitled 337.txt` | lines 69-101, 229-245, 429-508 | series quality | Pearl_Dev | Series quality gate plan appears prompt/spec-level, not merged implementation. | Split into narrow tests/config PR after live authority read. | 08 |
| `Untitled 338.txt` | lines 2-99, 122-222 | content layering | Pearl_Prime/Pearl_Editor | Layering spec/audit is not confirmed as landed on main. | Route to content-system salvage, not broad rewrite. | 08 |
| `Untitled 339.txt` | lines 34-81, 155-168, 181-256, 346-463 | pearl_prime stress recovery | Pearl_PM, Pearl_Prime | #5633 and #5644 merged; #5645 open with Core tests failing. | Fix #5645 or successor before stress recovery can proceed. | 05, 02 |

## Lane Launch Gates

| Lane | Terminal | Reason |
| --- | --- | --- |
| 01 | BLOCKED | Matrix written locally, but durable merge/PR surface is blocked by active branch churn and dirty shared checkout. |
| 02 | BLOCKED | Smoke PR #5645 has red Core tests; #5636 draft/conflicting; broad conflicting PRs remain unsafe. |
| 03 | BLOCKED | Emergency-low disk, active root branch churn, and poisoned/dirty worktrees prevent safe cleanup. |
| 04 | BLOCKED | Research layer absent from main, present locally/untracked; #5629 is polluted and not safe to merge. |
| 05 | BLOCKED | #5645 failing; no safe local stress pilot under disk limit. |
| 06 | BLOCKED | Harbor verified merged, but freebie #5636 is draft/conflicting/no checks. |
| 07 | BLOCKED | Manga merged items verified, but cloud auth/proof-bar and dirty worktree cleanup remain blockers. |
| 08 | BLOCKED | Legacy video/audiobook/series/layering salvage requires clean substrate and provenance. |
| 09 | BLOCKED | State/router edits cannot proceed until blocked lanes have clean remote surfaces. |
| 10 | BLOCKED | Final audit rejects incomplete cleanup and upstream blocked lanes. |

## Signals

- `old-chat-claim-matrix-terminal=blocked`
- `old-chat-pr-reconcile-terminal=blocked`
- `old-chat-worktree-cleanup-terminal=blocked`
- `research-prompt-layer-terminal=blocked`
- `prime-stress-story-surface-terminal=blocked`
- `brand-freebie-closeout-terminal=blocked`
- `manga-cloud-v5-bar-terminal=blocked`
- `dev-content-salvage-terminal=blocked`
- `state-router-hygiene-terminal=blocked`
- `old-chat-100pct-final-terminal=blocked`

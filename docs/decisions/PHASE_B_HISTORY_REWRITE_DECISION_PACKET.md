# Phase B History-Rewrite Decision Packet — LFS→R2 Program

**Status:** PROPOSED — awaiting operator ratification. Delivering this packet = `decision-packet-delivered`.
It is NOT `bestseller`/`shippable`/"Phase B approved"; a gate PASS on the docs PR carrying this packet
is not a ratification of the rewrite itself.

**Author:** Pearl_Architect · **Date:** 2026-07-24 · **Repo:** `Pearl-Prime/pearl_prime` (origin)
**Depends on:** Lane A (R2 program reconciliation) — **MERGED**, PR #336, squash `34cd37562c0aaf0eeaba9c0dbd9a17f65741fb6f`.
Lane B (R2 durability verifier wiring) — **PR #351 OPEN, CODE-WIRED, not yet proven green** (blocked on
GitHub Actions secrets provisioning; see `artifacts/coordination/handoffs/r2-durability-verify_2026-07-24.md`).
This packet is authored against best-available state per the pack's own fallback instruction ("if A/B
aren't merged, note it and author against best-available state, flagging the dependency") — **the R2-baseline
retrievability claim below rests on a local, non-vacuous, human-triggered proof (Lane B's local
`--head-only` run), not yet on a continuously-scheduled CI proof.** Re-run this packet's risk section once
PR #351 reaches system-working.

---

## 1. Decision asked

> Do we execute the LFS history rewrite (`git lfs migrate import --everything` on the extension list below)
> in a scheduled maintenance window, accepting a force-push to protected `main` plus a mandatory re-clone
> for every collaborator, agent worktree, and CI checkout?

**Recommended answer: DEFER — not GO now, not a hard NO-GO.** Confidence: **low-to-medium**, and that low
confidence is itself the headline finding of this packet (§2). Trigger conditions for revisiting are in §7.

---

## 2. Benefit — and why it cannot be stated with confidence today

This is the packet's most important finding: **this session could not produce one trustworthy reclaimable-
bytes number.** Five different measurements, five different orders of magnitude:

| Source | Method | Date | `.git`/pack size |
|---|---|---|---|
| `artifacts/audit/repo_size_audit.md` | local `du` + `git count-objects` | 2026-04-10 | 59 GB `.git`, 55.6 GB pack |
| Prior session handoff (`disk_r2_offload_session_2026-07-23.md`, cited in the closeout handoff) | unspecified | 2026-07-23 | "~76 GB / ~994k files" |
| This session, local `.git` on disk (`du -sh .git`) | `/Users/ahjan/phoenix_omega` | 2026-07-24 | **33 GB** total (`.git/lfs` local smudge cache **18 GB** + `.git/objects` **13 GB** + `.git/worktrees` admin **0.7 GB**) |
| This session, `git count-objects -vH` | same local clone | 2026-07-24 | **12.24 GiB** size-pack (+ 596 MB flagged `garbage`, + a `tmp_pack_Y9FTa2` warning — an interrupted pack operation left debris) |
| This session, GitHub API `GET /repos/Pearl-Prime/pearl_prime` → `size` | server-side, canonical | 2026-07-24 | **0.9 GB** (921 MiB) |

None of these agree, and the two measurements taken **in the same session, minutes apart** (local pack
12.2 GB vs. GitHub-reported 0.9 GB) differ by **>13×**. Plausible explanations, none confirmed this
session: (a) this local clone (`/Users/ahjan/phoenix_omega`) has 20 linked worktrees and 699 remote-tracking
branches fetched into it — its pack may include ref/reachability debris no longer present on a clean
mirror of `origin`; (b) GitHub's `size` API field is documented as sometimes-stale/cached and may exclude
categories of storage; (c) the April/July prior estimates may have measured a different, larger local
clone state (33 GB local `.git` ⊃ 18 GB LFS smudge cache, which a **history rewrite does not touch or
reclaim at all** — LFS objects already live outside git history by design — so any prior estimate that
folded `.git/lfs` into "history bloat" **overstated the Phase B benefit**).

**A `git lfs migrate info --everything --include=<Phase B extension list>` dry-run (read-only, the
correct way to get a real per-type reclaimable-bytes number) was started this session and left running
in the background; it was still in its commit-graph-sort phase after 12+ minutes against this repo's
699-branch, ~1M-object local clone (confirmed via `ps` to be actively consuming CPU across ~40 concurrent
LFS filter-process workers, not hung — just slow at this scale). It did not finish within this session's
practical window. See `docs/GIT_LFS_MIGRATION_PLAN.md`'s 2026-04-10 numbers below as the last full
per-type breakdown that *did* complete, but treat them as **stale and now unverifiable pending a fresh
run**, not as the benefit number to decide on:

| File type (2026-04-10 estimate) | Est. reclaim |
|---|---:|
| pearl_star/ ISO + .deb (history incident) | ~7 GB |
| Video renders (mp4/mov/etc.) | ~2 GB |
| Cover art (png/jpg revisions) | ~500 MB |
| Audio (mp3/wav/etc.) | ~1 GB |
| **Total (2026-04-10 estimate)** | **~10.5 GB**, against a then-measured ~56 GB clone |

**Recommendation on this point:** before any Phase B window is scheduled, re-run `git lfs migrate info
--everything --include=...` to completion from a **fresh `git clone --mirror`** (not this laptop's
20-worktree, 699-branch local clone) — ideally in a Codespace per CLAUDE.md's cloud-first default — and
reconcile against the GitHub API `size` field. Until benefit is a real, reproducible number, the cost/
benefit case in §3 cannot be honestly closed.

**Non-size benefits (qualitative, still real even if GB estimate is unresolved):** clone/Codespace
spin-up time; per-agent-worktree disk pressure (`project_worktree_disk_constraint` memory: ~3.2 GB/worktree
LFS smudge, and this session independently observed 20 concurrent worktrees); Cursor/indexer load on a
large `.git`; the `tmp_pack_Y9FTa2` / `garbage: 596.50 MiB` / `prune-packable: 3723` debris found in the
local pack this session suggests general repo-hygiene value in *any* eventual `gc --aggressive`, independent
of the LFS-migrate benefit specifically.

---

## 3. Cost / blast radius

- **Force-push to a PROTECTED `main`.** Confirmed live this session: ruleset `"Protect main"` (id
  `19645211`), `enforcement: active`, rules include `non_fast_forward` (blocks force-push outright) and
  `required_status_checks` (`Verify governance`, `parse-sweep`), `current_user_can_bypass: never`, zero
  bypass actors configured. **A Phase B force-push cannot happen without an owner temporarily editing or
  disabling this ruleset** — that is itself a privileged, auditable, reversible-only-by-the-owner action
  and should be scheduled as its own step in the runbook (§5), not assumed away.
- **Every collaborator, every agent worktree, every CI clone must re-clone.** This session alone found
  **20 active local worktrees** tied to this one laptop's checkout (`.claude/worktrees/×3`,
  `.worktrees/×2`, `phoenix_omega_worktrees/×6`, and 9 more standalone `phoenix_omega_wt_*` /
  `/tmp/*` worktrees/clones — see full `git worktree list` output in the discovery report, §6). Every one
  of those has stale objects post-rewrite and needs `git worktree remove` + fresh `worktree add` (or full
  re-clone); a rewritten-history pull into an existing worktree without that step will desync badly.
  Multiply by however many CI runners and any other collaborator machines are not visible from this
  laptop's local state.
- **Window during which no one may push.** All 6 currently-open PRs (§4) must land or close first, and no
  new work should branch from the old `main` history once the rewrite starts (anyone who does creates a
  second history to reconcile).
- **Irreversibility of a botched force-push.** `git push --force-with-lease` reduces (does not eliminate)
  the risk of clobbering concurrent pushes, but a rewritten-and-pushed history cannot be un-pushed once
  even one collaborator/CI system has re-cloned onto it — recovery at that point means asking everyone to
  re-clone *again* onto whatever the corrected state is. This repo's own memory flags PR #245 (20,006-file
  mass deletion, hundreds of recovery hours) as the standing precedent for irreversible mass git operations
  here; a history rewrite is a strictly more invasive class of operation than a bad merge.

---

## 4. Prerequisites checklist

| # | Prerequisite | Status (2026-07-24, this session) |
|---|---|---|
| 1 | All open PRs merged or closed | **NOT MET** — `gh pr list --state open` = **6 open**: #351 (this program's own Lane B, open), #347 (pt_BR catalog batch), #346 (manga bank demand rollup), #342 (arc_storyboard schema fix), #339 (manga video pose-bank coordination), #327 (social TTS pack). None are long-lived (all opened 2026-07-24); draining 6 active PRs is realistic but not instantaneous, and Pearl_GitHub does not control their authors' timelines. |
| 2 | `.git.backup` taken | **NOT MET** — correctly so; this is an owner-window step (§5), not a Lane C action. Lane C did not touch `.git`. |
| 3 | R2 copies proven retrievable (why C depends on B) | **PARTIALLY MET** — non-vacuous **local** proof only (`deep_verify_r2_offload.py --head-only` → `PASS (6 manifest(s))` with live Keychain-sourced credentials, this session via Lane B). The **continuous/scheduled** CI proof Lane B was built to provide is not yet green (PR #351 open, blocked on GitHub Actions secrets — see Lane B handoff). Do not schedule a Phase B window until PR #351 is merged AND has at least one green non-vacuous `workflow_dispatch`/scheduled run — a rewrite should not proceed on a same-day manual spot-check alone. |
| 4 | Collaborators + concurrent agent sessions notified, scheduled UTC window | **NOT MET** — no window has been proposed; this packet is the first artifact that could anchor that conversation. |
| 5 | Branch-protection lift plan + re-enable plan | **NOT MET** — no plan exists yet; §5 sketches the shape but the actual lift/re-enable is an owner action requiring repo-admin on the `"Protect main"` ruleset. |
| 6 | Trustworthy benefit number | **NOT MET** — see §2; this is a prerequisite this packet adds beyond the pack's original checklist, because the measurement instability found this session is itself disqualifying for an honest GO. |

---

## 5. Execution runbook (for the owner window — **DO NOT RUN outside an owner-approved window**)

```bash
# DO NOT RUN outside an owner-approved, scheduled maintenance window.
# Prerequisites (§4) must ALL be met first, including a fresh, trustworthy
# git lfs migrate info dry-run from a clean mirror clone (not a 20-worktree laptop checkout).

# 0. Freeze: announce window; block new merges to main for the duration (owner: pause/tighten
#    the "Protect main" ruleset's PR-merge path, or coordinate via ACTIVE_WORKSTREAMS.tsv freeze
#    signal so agents stand down).

# 1. Backup (from a CLEAN mirror clone, not a worktree-laden laptop checkout)
git clone --mirror https://github.com/Pearl-Prime/pearl_prime.git phoenix_omega_mirror_backup
cp -r phoenix_omega_mirror_backup phoenix_omega_mirror_backup.git.backup

# 2. Dry run again, on the mirror, to get final numbers immediately before executing
cd phoenix_omega_mirror_backup
git lfs migrate info --everything \
  --include="*.mp3,*.mp4,*.wav,*.png,*.jpg,*.jpeg,*.zip,*.lpf,*.pdf,*.xlsx,*.docx,*.iso,*.deb,*.m4a,*.ogg,*.flac,*.mov,*.avi,*.webm"
# Compare against §2's numbers. If wildly different again, STOP and re-open this decision —
# do not proceed on an unstable number a second time.

# 3. Execute migration (mirror clone; irreversible past this point without the backup)
git lfs migrate import --everything \
  --include="*.mp3,*.mp4,*.wav,*.png,*.jpg,*.jpeg,*.zip,*.lpf,*.pdf,*.xlsx,*.docx,*.iso,*.deb,*.m4a,*.ogg,*.flac,*.mov,*.avi,*.webm"

# 4. Aggressive GC to reclaim space
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Verify BEFORE pushing: LFS pointers resolve, and a sample of migrated blobs fetch correctly
git lfs fsck
# spot-check N sample files across each migrated extension: `git show <rev>:<path> | git lfs smudge`
# or `git lfs pull --include=<sample path>` and diff bytes/sha256 against the pre-migration blob.

# 6. Owner: temporarily adjust ruleset 19645211 ("Protect main") to permit a non-fast-forward
#    push for this operation ONLY, for the duration of step 7. Re-enable immediately after.

# 7. Force push (DANGEROUS — owner-present, owner-approved; --force-with-lease not --force)
git push --force-with-lease origin main

# 8. Re-enable "Protect main" exactly as it was (non_fast_forward rule back on).

# 9. All collaborators + every agent worktree/CI clone must re-clone (git worktree remove +
#    fresh git worktree add / git clone). Do NOT git pull an existing worktree onto rewritten
#    history — desync risk. See §3's worktree inventory for the known list to notify.

# 10. Post-rewrite verification: re-run scripts/ci/deep_verify_r2_offload.py (full sha256) and
#     confirm PASS; re-run the full CI suite on a fresh clone of the new main.
```

---

## 6. Discovery report (raw evidence for §2–§4)

- **Open PRs (`gh pr list --state open`, 2026-07-24):** 6 — #351, #347, #346, #342, #339, #327 (all opened same day; see §4 row 1).
- **`git count-objects -vH`** (local clone, `/Users/ahjan/phoenix_omega`): `count: 6828, size: 56.09 MiB, in-pack: 997217, packs: 25, size-pack: 12.24 GiB, prune-packable: 3723, garbage: 1, size-garbage: 596.50 MiB` — plus a `warning: garbage found: .git/objects/pack/tmp_pack_Y9FTa2` (evidence of an interrupted pack operation on this local clone at some point; independent repo-hygiene finding, not itself a Phase B blocker).
- **`du -sh .git` breakdown** (local clone): total 33 GB = `.git/lfs` 18 GB (local LFS smudge cache — **not** git history, **not** reclaimed by Phase B) + `.git/objects` 13 GB (the actual history pack — this is what Phase B targets) + `.git/worktrees` 0.7 GB (admin metadata for the 20 linked worktrees below).
- **GitHub API `GET /repos/Pearl-Prime/pearl_prime` → `size`:** `943170` KB = **0.9 GB**. Server-side, canonical, but see §2 for the unresolved discrepancy against the local 13 GB pack figure.
- **`git lfs migrate info --everything --include=<Phase B list>`:** started, did not complete in-session (12+ min, actively running — not hung, confirmed via `ps` showing ~40 concurrent `git-lfs filter-process` workers consuming real CPU against 699 branches / ~1M objects).
- **Remote branch count:** `git branch -r | wc -l` = **699**. This is itself worth flagging to the operator independent of Phase B — a repo with 699 remote branches is a plausible contributor to both the slow local git operations observed throughout this session (see Lane B's closeout notes: a full working-tree `git checkout` of this repo did not complete even after ~2.5 hours in one attempt this session) and to pack-size instability; branch hygiene (`scripts/git/branch_hygiene_sweep` / the existing `branch-hygiene-sweep.yml` cron) may be a higher-leverage near-term action than history rewrite.
- **Worktree / clone inventory (`git worktree list`, 2026-07-24, this laptop only — does not include any collaborator machines or CI runners not visible locally):** 20 linked worktrees beyond the main checkout, spanning `.claude/worktrees/` (3), `.worktrees/` (2), `phoenix_omega_worktrees/` (6), and 9 standalone `phoenix_omega_wt_*` / `/tmp/*` worktrees, each tracking its own agent branch (e.g. `agent/zhtw-name-registry-20260722`, `agent/manga-bank-demand-rollup-20260724`, `agent/translation-100pct-unblock-clean`, etc.). Each is a re-clone/re-add cost on Phase B day; several are marked `locked` (actively in use by another session as of this session's snapshot) — a scheduled window must land when as many of these as possible are idle or already merged/removed.
- **R2 baseline (Lanes A+B):** Wave 3 (267 files, PR #151 `b702de43f9`) and Wave 4 (79 files, PR #161 `bccb188535`) landed on `main`, reconciled by Lane A (PR #336, `34cd37562c`). Durability verifier CODE-WIRED by Lane B (PR #351, open) with a non-vacuous local retrievability proof (6/6 manifests) but no green scheduled CI proof yet.

---

## 7. Rollback

- **Before push (step 7 in §5):** trivial — discard the mirror clone, nothing on `origin` has changed.
- **After push, before any collaborator re-clones:** restore from `phoenix_omega_mirror_backup.git.backup`
  (`git push --force-with-lease origin main` from the backup mirror) — the point of no return is the FIRST
  collaborator or CI system that re-clones/re-fetches onto the rewritten history.
- **After collaborators start re-cloning:** rollback cost rises sharply — you are now asking everyone to
  re-clone a SECOND time onto the restored-original history, and any work committed against the rewritten
  history in the interim needs manual reconciliation (cherry-pick onto the restored line). This is the
  "point of no return" named per the pack's requirement; treat step 7→9 in §5 as a narrow, fast, monitored
  window specifically to minimize the number of parties who re-clone before a rollback decision could be made.
- **If `git lfs fsck` or the post-push sample-fetch check (§5 step 5) fails before push:** abort, do not
  push; the mirror clone is disposable.

---

## 8. Recommendation + go/no-go gate

**Architect recommendation: DEFER**, trigger conditions to revisit:
1. A fresh `git lfs migrate info --everything` dry-run completes from a clean mirror clone (not this
   laptop's 20-worktree state) and produces a reclaimable-bytes number that is reconciled against the
   GitHub API `size` field (i.e., the two agree within a sane margin, or the discrepancy is explained).
2. PR #351 (Lane B) is merged AND has at least one green, non-vacuous scheduled/`workflow_dispatch` run of
   `r2-offload-deep-verify.yml` (not just the local spot-check this session produced).
3. The 6 currently-open PRs have drained to zero (or the operator explicitly accepts scheduling the window
   around a smaller, named residual set).
4. An owner-approved UTC window + collaborator/agent-worktree notification plan exists (this packet can be
   the seed of that announcement once trigger 1–3 are met).

**Confidence in this recommendation:** medium-high that DEFER (not GO) is correct *right now*, precisely
because the benefit number is unresolved — a rewrite whose benefit could be anywhere from ~1 GB to ~50+ GB
depending on which measurement is trusted is not a decision that should be forced today. Confidence in the
eventual GO/DEFER-longer split, once triggers 1–4 are met, is not assessed here — that is next packet's job.

**OPERATOR DECISION:** ________________________________________ (GO / GO-after-\<trigger\> / DEFER-until-\<trigger\> / NO-GO) · Date: __________ · Signature/handle: __________

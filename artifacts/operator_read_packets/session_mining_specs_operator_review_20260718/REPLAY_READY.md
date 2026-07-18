# REPLAY_READY — Session-Mining Specs GitHub Restore

Run this **exact** command block when GitHub access is restored.
Derived from `replay_command_sequence.md` + `GITHUB_REINSTATEMENT_REPLAY_PACKET.md`
(re-validated 2026-07-18; do not paraphrase from memory).

Prerequisites:

1. `DECISION_RECORD.md` = **approve** (Q-OC7-01) — already filled.
2. GitHub account / `origin` fetch + push working (not 403 suspended).
3. Truth ref still at `15849b09c7d6d53d0c327bceeda5b216d855bd98` (re-check `ls-remote` below).
4. In-band discipline: never `git add -A` / `git add .`; no force push; no live queues;
   no publish; no prune/offload; no catalog scale; Rule 0 (>50 deletions ⇒ STOP).

```bash
cd /Users/ahjan/phoenix_omega
git remote get-url pearlstar_offline || git remote add pearlstar_offline pearl_star:~/git/phoenix_omega_offline.git
git fetch origin main
git fetch pearlstar_offline refs/heads/offline/session-mining-specs-do-all-implementation-20260718
git ls-remote pearlstar_offline refs/heads/offline/session-mining-specs-do-all-implementation-20260718
git rev-parse --verify 15849b09c7d6d53d0c327bceeda5b216d855bd98^{commit}
```

Confirm the `ls-remote` output is exactly:

```text
15849b09c7d6d53d0c327bceeda5b216d855bd98	refs/heads/offline/session-mining-specs-do-all-implementation-20260718
```

Create a clean replay worktree:

```bash
cd /Users/ahjan/phoenix_omega
export GIT_LFS_SKIP_SMUDGE=1
export REPLAY_BRANCH=codex/session-mining-specs-do-all-replay-20260718
export REPLAY_WT=/Users/ahjan/phoenix_omega_worktrees/session-mining-specs-github-replay-20260718
git worktree add -b "$REPLAY_BRANCH" "$REPLAY_WT" origin/main
cd "$REPLAY_WT"
```

Cherry-pick the offline chain. If the foundation commit is already in restored `origin/main`, cherry-pick only the implementation commit. If it is not, cherry-pick the foundation commit first.

```bash
if git merge-base --is-ancestor e0adcfa06bd87d2c8672b482a326768c7d26f6d4 origin/main; then
  git cherry-pick 15849b09c7d6d53d0c327bceeda5b216d855bd98
else
  git cherry-pick e0adcfa06bd87d2c8672b482a326768c7d26f6d4
  git cherry-pick 15849b09c7d6d53d0c327bceeda5b216d855bd98
fi
```

If a cherry-pick conflicts:

```bash
git cherry-pick --abort
git status --short --untracked-files=no
```

Then stop and write a blocker handoff with the exact conflict output.

Verify scope before any push:

```bash
git diff --stat origin/main...HEAD
git diff --name-only origin/main...HEAD
git diff --check origin/main...HEAD
```

Run the proof checks:

```bash
PYTHONPATH=. python3 -m pytest tests/test_tuple_viability_story_fallback.py tests/test_run_pipeline_word_ceiling_clamp.py tests/test_bisac_topic_map.py tests/test_required_docs_index.py tests/test_surface_inventory_variation_manifest.py tests/test_prose_integrity_gap_map.py tests/test_plantime_chapter_contract.py tests/test_human_judge_packet.py tests/test_store_series_naming.py tests/test_build_marketing_feed.py tests/test_artifact_retention_policy.py tests/test_render_job_discovery_dryrun.py tests/manga/test_serial_spine_multivolume_dry_run.py -q
PYTHONPATH=. python3 -m pytest tests/test_register_gate.py tests/test_register_gate_voice.py -q
```

Mandatory preflight before push/PR (repo golden pattern):

```bash
git branch --show-current
git status --short
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py
```

Sibling-PR search, then push without force only after the diff and tests are clean:

```bash
gh pr list --search "session-mining-specs-do-all-replay" --state all
git push -u origin "$REPLAY_BRANCH"
gh pr create --draft --title "Replay offline session-mining specs implementation" --body-file artifacts/operator_read_packets/session_mining_specs_operator_review_20260718/GITHUB_REINSTATEMENT_REPLAY_PACKET.md
```

Before merge: `gh pr diff <n> --stat | tail -1` — if deletions >50, STOP (Rule 0).
Poll required checks ≤10-min intervals to green; run `post_replay_checks.tsv`;
squash-merge on green; delete remote replay branch after merge.
Signal on success: `session-mining-replay=<merge-shas>`.

Never use `--force`, never run catalog scale, never write live queues, never publish, and never prune/offload as part of replay.

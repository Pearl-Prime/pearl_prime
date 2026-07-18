# Manga 100% Cloud Dispatch

This is the repo-native execution contract for the Phoenix Omega manga 100% program.

## Foundation gate

No implementation agent may run until PR #5597 is merged. The watchdog must write:

`artifacts/qa/manga_100pct_foundation_pr_5597_receipt_2026-07-14.json`

The receipt is dispatchable only when:

- the expected PR head SHA matches;
- every non-optional check has completed successfully;
- PR #5597 is merged;
- a valid 40-character merge SHA is recorded; and
- `dispatch_allowed` is `true`.

A draft PR, permission failure, pending check, skipped required check, failed check, missing merge SHA, or head-SHA drift blocks dispatch.

## Watchdog

```bash
PYTHONPATH=.:scripts/manga python3 scripts/manga/manga_100pct_watchdog.py \
  --repo Ahjan108/phoenix_omega_v4.8 \
  --pr 5597 \
  --expected-head-sha 45fe6c85b70d696eec9b41e9ae2fc5efbd34f6bb \
  --optional-check "Auto-merge bot-fix" \
  --allow-ready \
  --allow-merge \
  --max-polls 0 \
  --receipt artifacts/qa/manga_100pct_foundation_pr_5597_receipt_2026-07-14.json
```

Run this only under an identity allowed to mark the PR ready and merge it. The script uses `--match-head-commit` when merging so head drift fails safely.

## Render the dispatch packet

```bash
PYTHONPATH=.:scripts/manga python3 scripts/manga/manga_100pct_cloud_dispatch.py \
  --config config/manga/manga_100pct_cloud_dispatch.yaml \
  --foundation-receipt artifacts/qa/manga_100pct_foundation_pr_5597_receipt_2026-07-14.json \
  --output-dir artifacts/analysis/manga_100pct_cloud_dispatch_2026-07-14
```

The command exits `2` and writes `BLOCKED.md` when the foundation is not merged. It emits agent prompts only after the receipt passes.

## Agent mapping

| Cloud agent | Repo lanes from PR #5597 |
|---|---|
| Pearl_ArtPipeline | A, B, E |
| Pearl_Story | C, J |
| Pearl_Mode | D |
| Pearl_LetteringLayout | F |
| Pearl_ProofOps | G, H, M |
| Pearl_Catalog | L |
| Pearl_QA | I |

This mapping avoids duplicate agents reimplementing the A-M package already established by PR #5597.

## Final truth audit

After all lane PRs are merged and real evidence is present:

```bash
PYTHONPATH=.:scripts/manga python3 scripts/manga/manga_100pct_truth_audit.py \
  --repo-root . \
  --config config/manga/manga_100pct_truth_audit.yaml \
  --verify-github \
  --json-out artifacts/qa/manga_100pct_truth_audit_2026-07-14.json \
  --markdown-out artifacts/analysis/MANGA_100PCT_TRUTH_AUDIT_2026-07-14.md
```

The audit verifies concrete files, JSON values, proof images, merge SHAs, scorecards, operator approval, and forbidden local paths. It does not accept closeout prose as sufficient evidence.

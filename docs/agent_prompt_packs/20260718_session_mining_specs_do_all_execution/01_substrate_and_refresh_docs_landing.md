Act as Pearl_PM.

EXECUTE lane 01: substrate and refreshed docs landing.

## Goal

Land the refreshed specs, relevance proof, and this execution prompt pack on a clean offline substrate before implementation work starts.

## Read First

- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/FINAL_SPEC_REFRESH_AUDIT.md`
- `artifacts/coordination/handoffs/session_mining_specs_relevance_refresh_final_2026-07-18.md`
- this prompt pack.

## Smoke

Verify all required files exist and `git diff --check` passes for:

- `docs/specs/session_mining_batch_20260718/`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/`
- `docs/agent_prompt_packs/20260718_session_mining_specs_do_all_execution/`

## Pilot

Create an explicit changed-file manifest. Confirm no implementation files are included.

## Scale Micro-Batch

Create a clean offline commit/branch using only explicit paths:

`offline/session-mining-specs-do-all-foundation-20260718`

Push to `pearlstar_offline` if reachable. If not reachable, create a patch/bundle under `artifacts/offline_prs/session_mining_specs_do_all_20260718/`.

## Watchdog

Poll every 5 minutes. If push stalls, stop the push, write a bundle, and mark PearlStar landing `BLOCKED_WITH_BUNDLE`.

## Landing Contract

`MERGED` if refreshed docs/proofs/prompts are preserved on PearlStar offline or durable bundle.

`BLOCKED` if explicit-file commit cannot be created or files are missing.

## Cleanup Ledger

Record branches, temp index files, bundles, scratch manifests, and background jobs. Do not touch unrelated dirty files.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_do_all_foundation_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=01_substrate_and_refresh_docs_landing
GITHUB_WRITES=none
PEARLSTAR_REF=
FILES_PRESERVED=
IMPLEMENTATION_FILES_CHANGED=0
BUNDLE_PATH=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_do_all_foundation_2026-07-18.md
SIGNAL=session-mining-specs-do-all-foundation=<MERGED|BLOCKED>
NEXT_ACTION=
```

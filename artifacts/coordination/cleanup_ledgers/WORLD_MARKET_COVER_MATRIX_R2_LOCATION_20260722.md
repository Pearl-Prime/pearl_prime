# World-Market Cover Matrix — Confirmed Location on R2 (2026-07-22)

**Status:** RECOVERED — never lost. The 39×14×17 world-market cover contact
matrix (`artifacts/covers/world_market_coverage_20260719/`, confirmed absent
from the operator's local working tree) is on Cloudflare R2, migrated there
2026-07-21 by a disk-pressure-relief pass (a sibling agent session moved all
of `artifacts/covers/` — 13,138 files, ~5.30 GB — to R2 under
`local-disk-offload/artifacts_covers_20260721/` after byte-exact sha256
verification, then deleted it from the local disk; that session's own ledger,
`R2_ARTIFACTS_MIGRATION_20260721.md`, is on a different branch
(`agent/bestseller-atom-flow-lanes-20260721` @ `969cbecf36`) and not yet on
`main` as of this writing — not duplicated here; ask Pearl_GitHub/Pearl_PM to
land that branch if the full migration record is needed on `main`). This doc
narrows that migration down to the cover-matrix subtree specifically and
re-verifies its completeness against the 9,282-cover expectation.

## R2 location

```
Bucket:  phoenix-omega-artifacts
Prefix:  local-disk-offload/artifacts_covers_20260721/world_market_coverage_20260719/
Access:  rclone remote `r2` on Pearl Star (~/.config/rclone/rclone.conf),
         same remote as docs/INTEGRATION_CREDENTIALS_REGISTRY.md §5R.
```

## Verification (2026-07-22, Pearl_Int)

- `rclone lsf … -R --files-only | wc -l` → **9,639 objects** under the prefix
  (cover PNGs plus a handful of proof PDFs/PNGs, logs, and manifest/status
  JSON — not 9,639 distinct "books"; see `STATUS.json` below for the
  book-level count).
- `STATUS.json` (read via `rclone cat`) at the root of the prefix reports:

  ```json
  {
    "engine": "lean PIL + brand_covers.assignment fingerprints",
    "resolution": "800x1280",
    "brands": 39,
    "locales": 14,
    "topics": 17,
    "authors": {"expected": 241, "on_disk": 241, "coverage_pct": 100.0},
    "books":   {"expected": 9282, "on_disk": 9282, "coverage_pct": 100.0},
    "acceptance_layer": "EXECUTED-REAL 100% lean contact matrix",
    "note": "Half-res contact covers with per-author fingerprint DNA. Full KDP path: world_market_cover_coverage.py fill --fast"
  }
  ```

  **9,282 / 9,282 books present (100%)** — matches the 39×14×17 expectation
  exactly. This is a self-reported manifest from the matrix-fill run, not an
  independent per-file recount; treat book-count = 9,282 as EXECUTED-REAL per
  the note's own acceptance-layer label (lean/half-res contact sheet quality,
  not the full KDP-resolution render — see `note` field above), not a
  from-scratch Pearl_Int recount of every individual cover.

## What this is NOT

- This is **not** a re-render. No new covers were generated to produce this
  finding; the matrix that already existed (rendered 2026-07-19, migrated to
  R2 2026-07-21) was located and its existing self-reported manifest read.
- The images themselves were **not** copied back into the git working tree or
  into `artifacts/covers/` locally — per this repo's disk-offload convention,
  large binary artifact directories live in R2, not git, once migrated. This
  doc is the manifest/index pointer requested in lieu of re-landing 9,639
  binary files in git.

## To pull it back locally (if ever needed)

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
rclone copy r2:phoenix-omega-artifacts/local-disk-offload/artifacts_covers_20260721/world_market_coverage_20260719/ \
  artifacts/covers/world_market_coverage_20260719/
```

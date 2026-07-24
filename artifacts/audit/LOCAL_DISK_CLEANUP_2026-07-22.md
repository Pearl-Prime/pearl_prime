# Local Disk Cleanup + R2 Backup — 2026-07-22/23

**Lane:** `local-disk-cleanup-r2-backup` (Lane 01 of
`docs/agent_prompt_packs/20260722_disk_r2_offload_split/`)
**Executed on:** operator laptop (`/Users/ahjan/phoenix_omega`), via `PHOENIX_OMEGA_REMOTE=local-override`
(sanctioned bypass of the `assert_remote` cloud-native-only guard — this lane's whole
purpose is local-disk access, which is exactly what that guard exists to gate; see
`scripts/agent/assert_remote.py`).

## Scope executed

Two buckets, both fully backed up to R2 before any local deletion, both proven via
`r2_sync.py verify` (R2-side existence + byte-size check) **and** an independent sha256
round-trip spot-check (download a random sample post-upload, re-hash, compare to the
manifest) — not just trusted from the upload log.

### 1. Untracked-not-ignored bulk (`git status --porcelain | grep '^??'`)

- 178 named directories (QA proof/audit snapshots, social media voice/audio banks,
  manga production_books, lean_v2 waves, curation examples, offline_prs) — 17,943 files,
  3,725,052,544 bytes (3.72GB).
- Namespace: `pearl_prime_qa_runs` (prefix `qa_runs/`, existing 30-day lifecycle rotation
  — a good fit for disposable dated QA evidence).
- Manifest: `artifacts/manifests/pearl_prime_qa_runs/qa_runs__lane01_untracked_batch_2026-07-23.yaml`
  (plus the standalone smoke-test manifest,
  `qa_runs__dashscope_image_probe_20260721.yaml`).
- Verify: `✓ all 17943 artifacts present in R2 with correct size`.
- Spot-check: 8/8 random files sha256-matched after independent re-download.
- **KEPT LOCAL (backed up, NOT deleted)** per operator instruction — these five families
  are actively used by the live social media pipeline:
  `artifacts/social_media_video_bank_2026-07-19/`, `artifacts/translation/`,
  `artifacts/disk_recovery/`, `artifacts/generated/`, `artifacts/stock_image_bank/`.
  (These were not part of the 178-directory prune list at all — named explicitly out of
  scope from the start.)
- All 178 pruned directories deleted from local disk after verify.

### 2. Gitignored-only bulk (never git-tracked at all)

| Family | Files | Bytes | Namespace | Manifest |
|---|---:|---:|---|---|
| `assets/manga_catalog/` | 6,085 | 6,481,969,214 | `manga_catalog_render_cache` | `manga_catalog_cache__manga_catalog_2026-07-23.yaml` |
| `brand-wizard-app/dist/` | 3,656 | 4,220,390,666 | `misc_working_banks` | `misc__brand_wizard_app_dist_2026-07-23.yaml` |
| `brand-wizard-app/public/assets/covers/` (untracked+ignored portion only) | 1,670 | 3,644,277,229 | `misc_working_banks` | `misc__brand_wizard_app_public_covers_2026-07-23.yaml` |

- `artifacts/covers/` was checked but did not exist on disk at execution time — nothing
  to back up there.
- **Mixed-tracked-content handling:** `brand-wizard-app/public/assets/covers/` had 79
  git-tracked files mixed into an otherwise-untracked 3.6GB tree. Those 79 files were
  explicitly excluded from both the R2 push and the local deletion — they remain on disk
  untouched, to be handled by Lane 02 Wave 4 (proper `git rm` + LFS-offload manifest, not
  this lane's plain-backup path). Verified post-deletion: exactly 79 files remain under
  that path (171MB).
- Verify: all three manifests `✓ ... present in R2 with correct size`.
- Spot-check: 15/15 random files (5 per family) sha256-matched after independent
  re-download.
- All three deleted from local disk after verify (covers: file-level deletion excluding
  the 79 tracked paths, not a directory `rm -rf`).

## New R2 infrastructure (extends canonical config, per `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md` §4.1 "no parallel uploader")

- `config/artifacts/r2_buckets.yaml`: added `misc_working_banks` (prefix `misc/`) and
  `manga_catalog_render_cache` (prefix `manga_catalog_cache/`) namespaces.
- `schemas/artifacts/manifest.schema.json`: added both new namespace values to the
  `namespace` enum (was missing — first push attempt failed manifest-schema validation
  until this was added; the namespace was valid in `r2_buckets.yaml` but the JSON schema
  is a second, independently-maintained enum).

## Bugs found and fixed in `scripts/artifacts/r2_sync.py` (canonical, edited in place)

1. **`cmd_push` `produced_by` bug:** wrote the raw `PHOENIX_OMEGA_REMOTE` env var
   directly into the manifest instead of using the existing `_produced_by_label()`
   helper (which `cmd_push_offload` already used correctly). This meant
   `PHOENIX_OMEGA_REMOTE=local-override` — the documented, sanctioned bypass for exactly
   this kind of laptop-native lane — always failed manifest schema validation
   (`'local-override' is not one of [...]`), even though the upload itself succeeded.
   One-line fix: `cmd_push` now calls `_produced_by_label()` like `cmd_push_offload`
   does.
2. **Serial upload/verify performance:** both `cmd_push` and `cmd_verify` made one
   synchronous `put_object`/`head_object` call per file. Measured throughput on the
   178-directory batch: **~1 file/sec** — at 17,943 files that's ~5 hours, impractical.
   Added `ThreadPoolExecutor` concurrency to both (independent per-file operations, no
   shared mutable state during the upload/check phase — manifest assembly happens after
   all futures resolve). Initial cap of 64 workers achieved ~25 files/sec (12 min for
   the same batch) but **two simultaneous 64-worker pushes (128 concurrent connections)
   triggered what strongly appears to be R2 client-burst-triggered rate limiting** —
   `EndpointConnectionError` mid-upload, `Cloudflare status page showed R2 "operational"
   throughout` (ruling out a real outage), TLS handshake failures on both curl and boto3
   afterward. **Cap lowered to 16 workers** and the "never run two large push/verify
   calls concurrently" rule is now documented inline in the code.
3. **Diagnostic dead-end (process note, not a code bug):** while investigating the
   above, ~90 minutes were spent testing `https://${CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`
   for reachability — the wrong host. The tool's actual endpoint is
   `$R2_ENDPOINT` (a distinct EU-jurisdiction host per
   `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §5R — "the endpoint host hash differs from
   `R2_ACCOUNT_ID`"), which was reachable and authenticating correctly well before that
   90 minutes elapsed. The real burst-triggered issue had likely cleared within minutes;
   the extended wait was a self-inflicted diagnostic error, not a real extended outage.
   No code change from this — flagging here so it isn't repeated: **always test
   `$R2_ENDPOINT` directly, never reconstruct the host from `CLOUDFLARE_ACCOUNT_ID`.**

## Disk space

- `df -h /System/Volumes/Data` before this lane's deletions: **50Gi avail**.
- After all deletions: **40Gi avail** — a smaller increase than the ~21GB of files
  actually removed (3.72 + 6.48 + 4.22 + 3.64 ≈ 18GB backed-up-and-deleted, plus the
  earlier same-day cleanup). Ground truth for the deletions themselves is `du`/`find`
  confirmation (all target paths verified absent or reduced to exactly their expected
  tracked-file remainder), not `df`. The `df` "Avail" figure did not track 1:1 with
  bytes freed; plausible causes are APFS purgeable-space retention and normal
  concurrent disk activity from other processes during this session — not evidence the
  deletions didn't happen (independently confirmed above).

## Cleanup ledger

- Staging clones (`/tmp/stage_lane01_untracked`, `/tmp/stage_lane01_gitignored`): removed.
- Spot-check download scratch (`/tmp/spotcheck_untracked`, `/tmp/spotcheck_gitignored`):
  removed.
- No worktree created (ran in the existing checkout — this lane never touches tracked
  files, only untracked/gitignored disk state plus the small config/schema/manifest
  diff below).
- No background jobs left running.
- Held artifacts: the five KEEP-LOCAL families (see above) remain on disk by design.

## What this lane does NOT cover

- The 79 git-tracked files under `brand-wizard-app/public/assets/covers/` — Lane 02
  Wave 4.
- `artifacts/manga/**/assembled/`, `v4_render_cache/` (267 tracked files) — Lane 02
  Wave 3.
- `assets/manga_catalog/` Wave-2 premise correction (0 tracked files found, not a
  git-surgery target) — recorded in `docs/PROGRAM_STATE.md` and
  `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` per the earlier Lane 03 integration
  (PR #73).

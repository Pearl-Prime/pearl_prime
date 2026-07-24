# Lane 01 — Local Disk Cleanup + R2 Backup (no git-history risk)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_DevOps for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from the operator's existing local checkout at /Users/ahjan/phoenix_omega
(branch agent/bestseller-atom-flow-lanes-20260721 at the time this prompt was authored —
RE-VERIFY, do not trust this). This lane does NOT require a fresh worktree: it only
touches untracked/gitignored local files plus new manifest files, and pushes a small
manifest-only commit.

STARTUP_RECEIPT:
- AGENT=Pearl_DevOps
- LANE=local-disk-cleanup-r2-backup
- EXECUTION_MODE=local_fallback (R2 upload is network I/O, not a remote compute dispatch)
- BACKGROUND_SAFE=yes (uploads can run long; poll, do not block)
- RUNTIME_HOST=operator laptop
- PERSISTENCE_SURFACES=R2 bucket phoenix-omega-artifacts; small PR for new manifest files
- RESUME_SURFACE=artifacts/coordination/handoffs/local-disk-cleanup-r2-backup_2026-07-22.md

READ FIRST:
- docs/PROGRAM_STATE.md (SSOT — ground here first; re-verify "LAST VERIFIED @ origin/main" line)
- docs/agent_brief.txt (Router Operating Principles — this prompt was authored against v3
  as literally present in the file; if the file has since changed, that file wins)
- config/artifacts/r2_buckets.yaml (canonical bucket/namespace registry — EXTEND, do not fork)
- scripts/artifacts/r2_sync.py (canonical uploader — the ONLY uploader; §9 forbids a parallel one)
- docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md (sibling spec; this lane is NOT that spec's git-surgery
  workflow — these files were never git-tracked in the first place, so use `push`, not
  `push-offload`, which writes the git-offload-specific TSV contract)
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (pearl_devops row: authority docs =
  docs/GITHUB_OPERATIONS_FRAMEWORK.md, docs/GITHUB_GOVERNANCE.md,
  docs/BRANCH_PROTECTION_REQUIREMENTS.md, CLAUDE.md)

LIVE STATE RECONCILIATION:
- `git fetch origin`; re-derive current branch, HEAD, and origin/main SHA — do not copy
  the branch name/SHA claims above.
- This lane's TRUE scope is "everything under artifacts/, brand-wizard-app/, assets/
  that is NOT git-tracked" — that is TWO git-status categories, not one:
  - untracked-not-ignored: `git ls-files --others --exclude-standard <dir>`
    (2026-07-22 snapshot: ~5.7GB / ~50,600 files combined across the 3 roots — this is
    real uncommitted work product, treat with care per the KEEP/PRUNE split below)
  - gitignored (never tracked at all): `git ls-files --others --ignored --exclude-standard <dir>`
    (2026-07-22 snapshot: ~17.4GB / ~23,800 files combined — render caches, generated
    covers, working-copy trees already excluded from git; this is the majority of the
    disk bloat and was MISSED by an earlier pass of this lane that only checked
    `git status --porcelain | grep '^??'`, which silently hides gitignored files)
  Regenerate BOTH lists live for each of the 3 roots — do not assume the 2026-07-22
  byte/file counts above still hold.
- **Mixed-tracked-content warning:** at least one target directory
  (`brand-wizard-app/public/assets/covers/`) has a SMALL number of git-tracked files
  (79 at authoring time) sitting inside an otherwise gitignored/untracked 3.6GB tree.
  For any directory like this, do NOT `rm -rf` the whole directory — enumerate the
  untracked+ignored files specifically (`git ls-files --others --ignored --exclude-standard`
  minus tracked paths) and delete only those, leaving every git-tracked file's on-disk
  copy untouched (a git-tracked file's local copy going missing shows as an uncommitted
  deletion — that is Lane 02's concern via a proper `git rm`, never this lane's).
- Confirm R2 credentials are still loadable:
  `eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` then check
  `CLOUDFLARE_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` are non-empty. If
  any are missing, STOP — BLOCKED (credential gap), do not prompt for or hardcode secrets.
- Confirm free disk space (`df -h /System/Volumes/Data`) before and after — this whole
  lane's purpose is measurably reducing local disk usage; if it doesn't, that's a finding
  to report, not to hide.

PRE-REQUISITE CHECKS:
- r2-creds-present=<CLOUDFLARE_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY all set>
  — if missing, STOP and report BLOCKED.
- untracked-scope-confirmed=<live regenerated untracked-not-ignored list under artifacts/,
  brand-wizard-app/, assets/ matches the operator-confirmed KEEP/PRUNE split below>. If
  the live list looks materially different in size or composition from the 2026-07-22
  snapshot (~5.7GB / ~50,600 files) — e.g. 3x larger, or dominated by a family not
  mentioned below — STOP and treat it as a stale-premise correction: report the delta,
  do not silently prune something new the operator hasn't seen.
- gitignored-scope-confirmed=<live regenerated gitignored list under the same 3 roots
  matches the ~17.4GB / ~23,800-file 2026-07-22 snapshot, dominated by
  `assets/manga_catalog/` (~6GB), `brand-wizard-app/dist/` (~3.9GB),
  `brand-wizard-app/public/assets/covers/` (~3.6GB, MOSTLY gitignored but see the
  mixed-tracked-content warning above), `artifacts/covers/`>. Same stale-premise rule
  applies if materially different.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA + current branch SHA + divergence count
  (`git rev-list --left-right --count origin/main...HEAD`);
- live inventory (path, size, last-modified date) for BOTH the untracked-not-ignored
  AND the gitignored file sets under artifacts/, brand-wizard-app/, assets/ — this lane
  is not done until both buckets are addressed, not just the smaller one;
- confirm no open PR or active workstream currently writes to
  config/artifacts/r2_buckets.yaml or scripts/artifacts/r2_sync.py
  (`gh pr list --search "r2_buckets" --state open`, `gh pr list --search "r2_sync" --state open`);
- proposed smallest safe batch (see SMALLEST SAFE BATCH below).

PROVENANCE:
- research: NONE (this is an operational disk-hygiene action, not a new capability)
- documents: config/artifacts/r2_buckets.yaml; scripts/artifacts/r2_sync.py; CLAUDE.md
  (untracked-work-wipe caution); this pack's INDEX.md
- builds_on: scripts/artifacts/r2_sync.py `push` subcommand (canonical, extend the
  namespace registry in r2_buckets.yaml — do not add a new uploader)
- inventory: EXTENDS (config/artifacts/r2_buckets.yaml gets new namespace rows; nothing
  existing is reduced/removed)

MISSION:
Back up the operator-confirmed-safe-to-prune local bulk under artifacts/,
brand-wizard-app/, assets/ — BOTH the untracked-not-ignored bucket (~5.7GB) AND the
gitignored bucket (~17.4GB, the bigger of the two and the part an earlier pass of this
lane missed) — to R2 via `scripts/artifacts/r2_sync.py push`, verify the upload, THEN
delete the local copies — reducing this laptop's disk footprint without losing any of
the content (it becomes pull-on-demand from R2). Explicitly preserve (back up but do NOT
delete locally) the five families the operator named as actively used by the live
social media pipeline. This lane is NOT complete if it only handles one of the two
buckets.

KEEP LOCAL (back up to R2 as a durable copy, but do NOT delete from disk):
- artifacts/social_media_video_bank_2026-07-19/
- artifacts/translation/
- artifacts/disk_recovery/
- artifacts/generated/
- artifacts/stock_image_bank/

SAFE TO BACK UP THEN DELETE LOCALLY (per operator's 2026-07-22 confirmation; re-verify
these still exist and still look like disposable QA/working output, not something that
changed character since):
- artifacts/qa/*_2026071[7-9]*, artifacts/qa/*_202607[2-9][0-9]* (dated QA proof/audit
  snapshot dirs — mecha layering proofs, social visual rebuild checks, catalog
  completeness audits, etc.)
- artifacts/social_media_voice_bank_2026-07-19/
- artifacts/social_media_audio_bank_2026-07-19/
- artifacts/manga/production_books/
- artifacts/manga/**/assembled/ep_*_pearlstar_redo_*/ (dated one-off render-redo trees)
- artifacts/waves/lean_v2_lane03_* , artifacts/qa/lean_line_handoff_import_*
  (including *_sample_tmp_* — these are explicitly temp-suffixed)
- artifacts/curation/waystream_image_winners_20260715/examples/
- artifacts/offline_prs/
- any other untracked-not-ignored path under these three roots that is NOT in the
  KEEP LOCAL list above AND is NOT something the live discovery pass flags as
  looking like it might be someone's in-progress uncommitted work (if genuinely
  unsure about one specific path, list it in OPEN OPERATOR QUESTIONS rather than
  guessing — do not silently keep OR silently delete an ambiguous path).

GITIGNORED BUCKET — SAFE TO BACK UP THEN DELETE LOCALLY (this is the ~17.4GB / ~23,800
file bucket that an earlier pass of this lane missed entirely; it is regenerable
working/cache output by construction — that's WHY it's gitignored — but back it up
before deleting anyway, since "regenerable in principle" and "cheap to regenerate today"
are not the same claim, and this lane does not get to assume the latter):
- `assets/manga_catalog/` (~6GB) — fully gitignored (0 git-tracked files, re-verify),
  local manga catalog render cache.
- `brand-wizard-app/dist/` (~3.9GB) — fully gitignored (0 git-tracked files, re-verify),
  build output, should be regenerable via the app's own build command; still back up
  first in case current `dist/` reflects something not trivially rebuildable.
- `brand-wizard-app/public/assets/covers/` (~3.6GB total, but see the
  MIXED-TRACKED-CONTENT WARNING above — only 79 files here are git-tracked; back up and
  delete the untracked+ignored ~3.6GB remainder, leave the 79 tracked files' local
  copies alone for Lane 02 / Wave 4 to handle via proper `git rm`).
- `artifacts/covers/` — fully gitignored (0 git-tracked files, re-verify), generated
  book covers.
- any other gitignored path under these three roots discovered live, following the same
  ambiguous-path escalation rule as the untracked bucket above.

NAMESPACE DECISION (Q-LANE01-01, recommended default — log to
artifacts/coordination/operator_decisions_log.tsv, do not block on escalation):
- Reuse the existing `pearl_prime_qa_runs` namespace (prefix `qa_runs/`, 30-day
  lifecycle rotation already configured in r2_buckets.yaml) for all `artifacts/qa/*`
  dated proof/audit dirs — the existing rotation policy is actually a perfect fit for
  disposable dated QA evidence.
- Add ONE new namespace `misc_working_banks` (prefix `misc/`) to
  `config/artifacts/r2_buckets.yaml` for the catch-all (social media voice/audio banks,
  production_books, lean_v2 waves, curation examples, offline_prs) — extends the
  registry per agent_brief.txt §9, does not fork a parallel system. No lifecycle rule
  (these are backups of real content, not scratch — do not auto-expire).
- Add a second new namespace `manga_catalog_render_cache` (prefix `manga_catalog_cache/`)
  for `assets/manga_catalog/`, and reuse `manga_rendered_books` (already exists, prefix
  `manga/rendered_books/`) for anything under `brand-wizard-app/public/assets/covers/`
  and `artifacts/covers/` that reads as manga/book cover art specifically — otherwise
  fall back to `misc_working_banks`.
- Escalate only if you find a path that doesn't cleanly fit any bucket and isn't
  obviously scratch either.

DELIVERABLES:
- `config/artifacts/r2_buckets.yaml` updated with the `misc_working_banks` and
  `manga_catalog_render_cache` namespaces.
- One or more `r2_sync.py push` runs producing YAML manifests under
  `artifacts/manifests/<namespace>/...` for every backed-up directory (KEEP-LOCAL and
  PRUNE families alike — back EVERYTHING up, prune only the PRUNE list).
- `r2_sync.py verify --manifest <path>` (or equivalent head_object check) passing for
  every manifest before any local deletion.
- Local deletion of only the PRUNE-list paths, only after their manifest verifies.
- `artifacts/audit/LOCAL_DISK_CLEANUP_2026-07-22.md`: before/after `df -h`, per-path
  backed-up-size table, per-path deleted-or-kept decision + why, R2 manifest paths.

SMALLEST SAFE BATCH:
- smoke: pick the single smallest PRUNE-list directory, push to R2, verify, delete
  locally, confirm `pull-on-demand`-equivalent restore works (for plain `push`/`pull`,
  that's `r2_sync.py pull --manifest <path>` into a scratch dir + diff/sha256 check),
  THEN re-delete the scratch restore copy.
- pilot: next 3-5 directories from the PRUNE list, same push -> verify -> delete
  sequence, confirming disk usage actually drops each time (`df -h` before/after).
- scale: remaining PRUNE-list directories, same pattern, largest last (so an early
  failure doesn't waste time uploading the biggest trees first).
- Never `rm -rf` a directory whose manifest hasn't been verified. Never batch "push
  everything then delete everything" — verify-then-delete per directory.

HANG PREVENTION:
- poll interval: 2 minutes per R2 upload batch (these are GB-scale, not instant).
- no-progress rule: inspect `r2_sync.py` output / network activity after two unchanged
  polls (is it actually uploading, or hung on auth/DNS?).
- hard stall rule: BLOCKED (or reduce batch size / retry smaller) after three unchanged
  polls.
- max window: 90 minutes total for this lane; if the bulk upload alone would clearly
  exceed that, checkpoint progress (which dirs are done) into the handoff and continue
  in a follow-up turn rather than silently truncating scope.

TESTS/PROOFS:
- `python3 scripts/artifacts/r2_sync.py verify --manifest <path>` per pushed directory.
- `df -h / /System/Volumes/Data` before and after, in the audit doc.
- spot-check restore: for at least one deleted directory, `pull` it back to a scratch
  path and confirm file count + total size match the pre-delete measurement, then
  remove the scratch restore (this proves the backup is real, not just "upload
  succeeded" per HTTP 200).
- Proof root: `artifacts/audit/LOCAL_DISK_CLEANUP_2026-07-22.md`.

DO NOT:
- Do NOT delete anything in the KEEP LOCAL list. Back it up; leave the local copy alone.
- Do NOT delete any git-tracked file in this lane (that's lane 02's job, and lane 02
  requires a PR + owner approval for >50 deletions — this lane is untracked-only).
- Do NOT run `git add -A` / `git add .` / `git clean -fd` anywhere near these directories
  — this repo has a documented "aborted-checkout leaves ~262k phantom deletions staged"
  poison-protocol risk (agent_brief.txt §4); this lane's git footprint should be limited
  to the small, explicit `config/artifacts/r2_buckets.yaml` edit and any new manifest
  files — `git add` those exact paths only.
- Do NOT invent a new uploader/script — `r2_sync.py push` is canonical; extend it if it
  is missing something you need (e.g. `--include-exts` too narrow for non-image content
  like .mp3/.mp4/.html/.json — check `cmd_push`'s actual extension-filtering behavior
  before assuming `push-offload`'s image-only default applies to `push` too), do not
  write a parallel upload script.
- Do NOT delete a directory whose manifest verify step failed or was skipped.
- Do NOT treat "I ran push" as done without a verify step and (for at least one
  directory) a restore spot-check.

LANDING CONTRACT:
- MERGED: the `config/artifacts/r2_buckets.yaml` + new manifest files land via a small
  PR (squash-merged, required checks green) — this IS a "lane that writes files," so it
  ends MERGED or BLOCKED like any other, even though the bulk of the work is local
  filesystem + R2, not code.
- BLOCKED: exact blocker (e.g. credential gap, an ambiguous path the operator needs to
  rule on, an R2 upload failure), evidence, and — critically — if you've already deleted
  some local directories and are blocked mid-lane, that partial state (what's deleted,
  what's backed up, what's pending) must be in the handoff so nothing is silently lost.

CLEANUP LEDGER REQUIRED:
- worktree: none created for this lane (works in the existing checkout).
- local branch: name the small branch used for the r2_buckets.yaml + manifest PR;
  delete after merge.
- remote branch: deleted after squash-merge.
- scratch files: any scratch restore-verification copies must be removed after the
  spot-check; name them explicitly if any are intentionally left.
- background jobs: none should be left running; if an R2 upload is still in flight at
  turn end, that violates the landing contract — see it through or report BLOCKED with
  the in-flight state named.
- held artifacts: the KEPT-LOCAL five families remain on disk by design — declare this
  explicitly in the handoff as an intentional, not a mess.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/local-disk-cleanup-r2-backup_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_DevOps
- LANE: local-disk-cleanup-r2-backup
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: disk-cleanup-r2-backup=<count of directories backed up, untracked+gitignored combined>
- PROOF_ROOT: artifacts/audit/LOCAL_DISK_CLEANUP_2026-07-22.md
- TESTS: <verify + restore spot-check results>
- CLEANUP: <ledger above>
- HANDOFF: artifacts/coordination/handoffs/local-disk-cleanup-r2-backup_2026-07-22.md
- NEXT_ACTION: <e.g. "lane 02 (LFS offload waves 2-4) is independent and may already be
  in flight; lane 03 (devops policy doc) waits for both 01 and 02 to reach terminal
  state">
```

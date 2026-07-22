# Laptop-Disk R2 Offload + DevOps Policy Split — Prompt Pack

## Program

- Goal: (1) back up + prune ALL non-git-tracked disk bloat under `artifacts/`,
  `brand-wizard-app/`, `assets/` on the operator's laptop that was driving Cursor
  extension-host/watcher memory blowups — this is TWO buckets, not one: ~5.7GB
  untracked-not-ignored (real uncommitted work, handle carefully) PLUS ~17.4GB
  gitignored-only (render caches, `assets/manga_catalog/`, `brand-wizard-app/dist/`,
  `artifacts/covers/`, etc. — the larger bucket, and the one an earlier scoping pass
  missed by only checking `git status --porcelain`); (2) execute the LFS→R2 offload
  Waves that actually have git-tracked content, per the already-ratified
  `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md` (Wave 1 pilot merged 2026-07-09, PR #5306) —
  live verification at authoring time found the spec's own "Wave 2 = assets/manga_catalog"
  target has ZERO tracked files (it's 100% gitignored already, so it's actually a Lane-01
  job, not a git-surgery job); the real git-surgery scope is Wave 3
  (artifacts/manga/**/assembled/, v4_render_cache/ — 267 tracked files) and Wave 4
  (brand-wizard-app/public/assets/covers/ — 79 tracked files), totaling ~863MB across all
  three directories combined, far smaller than the spec's ~9.5GB wave estimate (which
  conflated total-directory-size with tracked-file-size); (3) codify a "what runs where"
  policy (laptop=edit-only, Pearl Star=GPU/LLM via `pscli`/RAP, GitHub
  Actions=orchestration incl. self-hosted Pearl Star runner, R2=binary store) into the
  canonical DevOps authority doc; (4) extend the existing RAP compliance gate to flag
  local artifact writes that bypass R2/pscli.
- Source request: operator (laptop RAM/disk investigation → "move dev+prod off my
  laptop" → "yes, and /piper prompts to do all this right").
- Router date: 2026-07-22.
- Live origin/main: `159434e89a34305336583e7dcf593cb08af6d584` (verify live — see below).
- Prompt count: 3 execution lanes + 1 dispatcher.
- Master dispatcher: `00_MASTER_DISPATCH_PROMPT.md`.

## Wave Order

- Wave 1 (parallel, no git risk): `01_LOCAL_DISK_CLEANUP_R2_BACKUP.md` — covers BOTH the
  untracked-not-ignored (~5.7GB) AND gitignored-only (~17.4GB) buckets; also absorbs
  Wave 2 of the LFS spec if live-verification confirms it still has 0 tracked files.
- Wave 1 (parallel, independent branch/PR): `02_LFS_R2_OFFLOAD_WAVES_2_4.md` — real git
  surgery (LFS `git rm` across ~346 tracked files: 267 in Wave 3 + 79 in Wave 4; Wave 2
  is conditional, see the lane file's KNOWN STALE PREMISE note); own reviewed PR; owner
  approval required before merge per CLAUDE.md Non-Negotiable Git Rule 0 (>50-file
  deletions).
- Wave 2 (starts only after Wave 1 lanes 01+02 both report a terminal state —
  MERGED/BLOCKED — so the policy doc can cite real evidence paths, not projected ones):
  `03_DEVOPS_POLICY_DOC_AND_RAP_GATE_EXTENSION.md`.

## Lane Matrix

| Prompt | Agent | Lane | Owner | Substrate | Depends on | Output tags | Hot files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | Pearl_DevOps | local-disk-cleanup | Pearl_DevOps | local laptop + R2 (no git commit required except the manifest) | none | `disk-cleanup-r2-backup=<manifest-count>` | `config/artifacts/r2_buckets.yaml`; `artifacts/manifests/**` (new files only) |
| 02 | Pearl_DevOps | lfs-r2-offload-waves-2-4 | Pearl_DevOps | GitHub PR (forward-only, no history rewrite) | none (independent of 01) | `lfs-offload-wave2-4=<merge-sha>` | `.gitattributes`; `artifacts/manifests/lfs_offload/**`; `scripts/ci/check_render_progress_bytes.py` (verify only, no logic change expected) |
| 03 | Pearl_DevOps | devops-what-runs-where-policy | Pearl_DevOps | GitHub PR | 01 + 02 terminal | `devops-runs-where-policy=<merge-sha>` | `docs/GITHUB_OPERATIONS_FRAMEWORK.md`; `scripts/ci/check_rap_compliance.py`; `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (ws_lfs_setup_20260410 update) |

## Deconfliction

- Open PRs checked (2026-07-22 live): #56, #55, #53, #50, #49, #42 — none touch
  `r2_sync.py`, `r2_buckets.yaml`, `GITHUB_OPERATIONS_FRAMEWORK.md`,
  `check_rap_compliance.py`, or `LFS_TO_R2_OFFLOAD_V1_SPEC.md`. Merged #28
  (`agent/cover-matrix-r2-location-20260722`) touched R2 cover-matrix *location*
  documentation only — no file overlap, no conflict.
- Active workstreams checked: `ws_lfs_setup_20260410` (status=active, owner
  Pearl_Dev+Pearl_GitHub) is the exact parent workstream for lanes 01/02/03 — update its
  row, do not fork a parallel workstream. Its only recorded blocker is **Phase B history
  rewrite** (owner-gated) — Waves 2–4 here are explicitly forward-only per spec §0, so
  they are NOT blocked by that.
- Shared files: `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`,
  `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`,
  `docs/PROGRAM_STATE.md` — one git-ops driver at a time; if two lanes need to touch the
  same row/section, serialize (01 and 03 do not overlap; 02 and 03 both may touch
  ACTIVE_WORKSTREAMS.tsv — 03 must re-fetch and rebase its edit onto whatever 02 landed).
- Serialization rule: 03 STARTS only after 01 and 02 both reach MERGED or BLOCKED
  (needs their real evidence paths/signals to write an accurate policy + gate).

## Evidence Requirements

- Tests: `pytest tests/artifacts/` (r2_sync coverage, if present) or targeted smoke per
  lane; `scripts/ci/check_render_progress_bytes.py --require-images` must stay green
  post-Wave-2-4; `scripts/ci/check_rap_compliance.py` must still pass on its own repo
  (mutation-test the new check per agent_brief.txt §14: deliberately add a local-write
  violation, confirm it goes RED, then remove it).
- Proof roots: `artifacts/audit/LFS_OFFLOAD_WAVE_2_4_PROOF_2026-07-22.json` (sha256
  round-trip proof, lane 02); manifest paths under `artifacts/manifests/` (lane 01, new
  namespace backup manifests); `artifacts/manifests/lfs_offload/*.tsv` (lane 02, per
  family).
- PR/merge signals: `disk-cleanup-r2-backup=<manifest-count>`,
  `lfs-offload-wave2-4=<merge-sha>`, `devops-runs-where-policy=<merge-sha>`.
- Operator approvals: lane 02 MUST get explicit owner sign-off before merge if the PR
  diff shows >50 tracked-file deletions (CLAUDE.md Non-Negotiable Git Rule 0) — this is
  expected and required, not a blocker to route around.
- Final audit: lane 03's CLOSEOUT should link back to 01's and 02's CLOSEOUT_RECEIPTs.

## Cleanup Requirements

Every lane must report:

- worktree removed or HOLD path/reason;
- local branch deleted or HOLD reason;
- remote branch deleted after merge or HOLD reason;
- scratch files removed (note: the operator-facing size listing used to scope lane 01,
  `/private/tmp/claude-501/.../scratchpad/untracked_review.txt`, is a session scratch
  file, NOT a durable source — lane 01 MUST regenerate its own live `git status
  --porcelain` listing rather than trust that snapshot, per agent_brief.txt §11);
- background jobs stopped or declared;
- handoff file path (`artifacts/coordination/handoffs/<lane_id>_2026-07-22.md`).

## Final Status

- Status: NOT YET DISPATCHED — this pack is the paste-ready next action.
- Blockers: none known at authoring time; live-truth re-check is mandatory at each
  lane's startup per agent_brief.txt §11 (branch/SHA/PR counts above are a 2026-07-22
  snapshot, not ground truth for the executing agent).
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead agent, OR run lanes 01
  and 02 directly in parallel chats (they have no dependency on each other) and hold 03
  for after both land.

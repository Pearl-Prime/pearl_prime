# Lane 02 — Execute LFS→R2 Offload Waves 2-4 (forward-only git surgery)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_DevOps for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a CLEAN checkout of latest origin/main — NOT the operator's dirty root
checkout at /Users/ahjan/phoenix_omega. That root checkout was measured at authoring
time with ~283,000 `git status --short` entries (a known worktree-shared-inode artifact
tracked in ws_pearl_devops_tooling_maintenance_20260505, item 3) and is 46 commits behind
/ 4 ahead of origin/main. Do not attempt this lane's `git rm` surgery against that tree.
Use either a fresh `git clone`/worktree of origin/main, or the plumbing pattern (temp
index built off `origin/main^{tree}`, per agent_brief.txt §4) if disk space is tight.

STARTUP_RECEIPT:
- AGENT=Pearl_DevOps
- LANE=lfs-r2-offload-waves-2-4
- EXECUTION_MODE=github_actions (lands as a reviewed PR)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=fresh clone/worktree (NOT the operator's dirty root checkout)
- PERSISTENCE_SURFACES=branch + PR
- RESUME_SURFACE=artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_2026-07-22.md

READ FIRST:
- docs/PROGRAM_STATE.md — SSOT; re-verify the DevOps/repo-hygiene section's current
  wording on LFS→R2 status before writing anything ("V1 pilot only; full
  assets/manga_catalog Wave-2 offload remains a follow-on lane" as of 2026-07-22 — you
  are that follow-on lane).
- docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md — THE authority for this lane's mechanics.
  Read it in full; it is short. §6 (pilot) is already done; §7 (wave plan) is your scope.
- scripts/artifacts/r2_sync.py — read `cmd_push_offload` and `cmd_verify` before running
  anything; confirm the CLI flags below still match the live source (this prompt is a
  snapshot).
- artifacts/manifests/lfs_offload/stillness_press_alarm_composed_v4_ep_001.tsv — the one
  existing manifest; match its exact schema/header format for new manifests.
- .gitattributes — read the existing per-family narrowing block near
  "LFS→R2 offload V1 pilot" (search for that comment) before adding new blocks; append,
  do not restructure.
- agent_brief.txt §4 (worktree/disk/poison discipline) and §17 (landing contract) — this
  lane both creates a worktree/clone AND commits git-surgery deletions; both sections
  apply directly.
- CLAUDE.md "Non-Negotiable Git Rules" item 0 — check the PR diff stat before even
  proposing merge; >50 file deletions requires explicit owner approval, no exceptions.

LIVE STATE RECONCILIATION:
- `git fetch origin`; confirm origin/main SHA (do not trust the 2026-07-22 snapshot SHA
  in this pack's INDEX.md).
- `gh pr list --search "r2 offload" --state all` and `gh pr list --search "manga_catalog
  offload" --state all` — confirm no sibling PR has already done Wave 2/3/4 since this
  prompt was authored. If one has, stand down, reconcile, and report the delta — do not
  duplicate.
- Confirm R2 credentials loadable per the same Keychain command as lane 01.
- **KNOWN STALE PREMISE — verify before starting Wave 2:** at authoring time (2026-07-22)
  `git ls-files assets/manga_catalog | wc -l` returned **0**. `assets/manga_catalog/` is
  100% gitignored (`.gitignore:128`) — there is currently nothing git-tracked there for
  this lane to `git rm`/offload. If this is STILL true when you run this lane, **Wave 2
  as scoped in the spec does not apply as a git-surgery job** — the entire
  `assets/manga_catalog/` family (~6GB) belongs to Lane 01 (plain R2 backup + local
  delete, no PR, no `.gitattributes` change), not this lane. In that case: (a) do NOT
  attempt Wave 2 here, (b) correct `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md` §7's wave
  table in this PR to mark Wave 2 as "N/A — target has 0 tracked files as of <date>,
  handled instead by Lane 01 R2 backup (see <lane 01 handoff path>)" per
  agent_brief.txt §11's corollary (correct the source, don't let the false premise
  reproduce), (c) proceed directly to Wave 3 and Wave 4, which DO have real tracked
  content (267 tracked files under `artifacts/manga/**/assembled/` +
  `v4_render_cache/` for Wave 3; 79 tracked files under
  `brand-wizard-app/public/assets/covers/` for Wave 4, at authoring time — re-verify
  both live too). If Wave 2's target has since GAINED tracked files (someone committed
  into it since 2026-07-22), then it IS a real target — proceed with it normally and
  note the premise was correct after all.
- Re-measure the actual size/file-count of EVERY wave's target family via
  `git ls-files <path> | wc -l` (tracked count — this is what actually matters for this
  lane, not `du -sh`, which counts gitignored/untracked bytes too and will overstate
  scope). At authoring time, TOTAL tracked bytes across all of artifacts/,
  brand-wizard-app/, assets/ combined was only ~863MB (123MB + 554MB + 186MB) — far
  smaller than the spec's ~9.5GB wave-size estimates, because those estimates conflated
  total-directory-size with tracked-file-size. Re-derive live; do not assume the spec's
  GB figures describe what you'll actually be `git rm`-ing.

PRE-REQUISITE CHECKS:
- r2-creds-present=<all three R2 env vars set> — STOP/BLOCKED if missing.
- no-sibling-pr-in-flight=<gh pr search above returns nothing overlapping> — if a sibling
  PR exists, STOP, do not duplicate; report which PR and stand down or coordinate.
- spec-still-current=<docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md §7 wave table still lists
  Waves 2-4 as open (not already landed)> — re-verify against PROGRAM_STATE.md, not just
  the spec file (specs can go stale; PROGRAM_STATE is SSOT per agent_brief.txt §10).
- wave-2-applicability=<live `git ls-files assets/manga_catalog | wc -l` — if 0, Wave 2
  is out of scope for THIS lane per the stale-premise correction above; do not block the
  whole lane on this, just skip Wave 2 here and note the redirect>.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- for each of the 3 waves: live file count + total bytes for the target family, and
  confirmation that none of it falls under SOURCE_OF_TRUTH/ or atoms/ (spec's hard
  NEVER-move list);
- confirm `check_render_progress_bytes.py` (or the relevant gate for non-manga families
  in Wave 4) currently reads these files from disk, and understand exactly how its
  manifest-verify fallback path works, BEFORE removing any file from the index;
  smallest safe batch proposal (below).

PROVENANCE:
- research: NONE (executing an already-ratified spec, not researching a new capability)
- documents: docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md (full authority); this pack's INDEX.md
- builds_on: scripts/artifacts/r2_sync.py `push-offload`/`pull-on-demand`/`verify`
  subcommands (canonical, per spec §4.1 — "no parallel uploader"); config/artifacts/
  r2_buckets.yaml `manga_rendered_books` namespace; scripts/ci/check_render_progress_bytes.py
  manifest-verify fallback (spec §4.2, already built for exactly this)
- inventory: EXTENDS (adds manifest rows + narrows .gitattributes per family; does not
  change check_render_progress_bytes.py's logic — that extension already shipped in the
  pilot per spec §4.2. If you find it does NOT already support manifest-verify, that's a
  stale-premise correction: fix the doc/spec claim in the same PR, then decide whether to
  build the missing logic here or split it into its own blocking prereq lane.)

MISSION:
Execute Wave 3 (remaining artifacts/manga/**/assembled/, v4_render_cache/ — 267 tracked
files at authoring time) and Wave 4 (brand-wizard-app/public/assets/covers/ — 79 tracked
files at authoring time) of the LFS→R2 offload per spec §7, using the exact forward-only
mechanics already proven in the Wave-1 pilot (§6): for each family — upload via
`push-offload`, write the TSV manifest, prove round-trip sha256 match, narrow
`.gitattributes`, `git rm` the binaries from the index, confirm the relevant gate stays
green via manifest-verify, THEN move to the next family. Wave 2
(assets/manga_catalog/**) is CONDITIONAL — see the KNOWN STALE PREMISE note in LIVE
STATE RECONCILIATION above: at authoring time it has 0 git-tracked files, meaning
there is no git-surgery job there; re-verify live, and if still 0, skip Wave 2 in this
lane entirely (redirect it to Lane 01) and correct the spec's wave table instead of
attempting a no-op offload. Do each applicable wave as its own commit (or its own small
PR if that reduces risk / review size); do not do all waves in one giant commit.

DELIVERABLES (per wave, repeat 3x):
- `artifacts/manifests/lfs_offload/<slug>.tsv` per family (schema matches the existing
  pilot manifest exactly: `repo_path`, `r2_key`, `bytes`, `sha256` columns + the 4-line
  header comment block).
- `.gitattributes` narrowed for the family, appended after the existing generic LFS
  rules and after the Wave-1 pilot block (last-match-wins ordering matters — verify with
  `git check-attr filter -- <sample-file>` before and after).
- Binaries `git rm --cached` (or full `git rm` if not needed working-tree-side) from the
  index, ONLY after the round-trip proof below passes.
- `artifacts/audit/LFS_OFFLOAD_WAVE_2_4_PROOF_2026-07-22.json` — one round-trip proof
  entry per wave (upload → manifest → delete local copy → `pull-on-demand` → sha256
  match), same shape as the pilot's `LFS_OFFLOAD_PILOT_PROOF_2026-07-09.json` if that
  file exists (read it first as the format reference; if it doesn't exist, define the
  shape from spec §8's acceptance checklist and note that in the PR).
- Updated `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` row for `ws_lfs_setup_20260410`
  (task/evidence_paths fields — append, do not overwrite prior wave-1 evidence).
- Updated `docs/PROGRAM_STATE.md` DevOps/repo-hygiene section reflecting Waves 2-4
  landed (per agent_brief.txt §5, PROGRAM_STATE updates at every milestone merge).

SMALLEST SAFE BATCH:
- smoke: within Wave 3 (artifacts/manga/**/assembled/, v4_render_cache/), pick the
  smallest sub-slug (a single series/episode directory), full push-offload → verify →
  gate-check → git rm cycle, end to end, before touching anything else. This proves the
  pattern still works end-to-end post-pilot before committing to the rest of Wave 3.
  (If Wave 2 turns out to still be a live tracked-file target after re-verification,
  smoke it first instead, same pattern, smallest sub-slug.)
- pilot: expand to the rest of Wave 3 once smoke passes gate-check green.
- scale: Wave 4 next, starting with its own smallest sub-slug smoke first (Wave 4 is
  only 79 tracked files total, so "smoke" and "pilot" may collapse into one small batch
  here — use judgment, but still verify before scaling to all 79). Do not start Wave 4
  until Wave 3's PR has merged (or is at minimum proven green in CI on its own branch) —
  waves are sequential, not parallel, because each narrows .gitattributes further and a
  merge-order surprise could silently un-narrow a prior wave.

HANG PREVENTION:
- poll interval: 3 minutes per family upload (these are GB-scale).
- no-progress rule: inspect upload/CI logs after two unchanged polls.
- hard stall rule: BLOCKED (or split the family into smaller sub-batches) after three
  unchanged polls.
- max window: this is a multi-hour lane at true GB scale; checkpoint per-wave into the
  handoff so a later turn can resume from "Wave 2 done, Wave 3 in progress" rather than
  restarting. A single turn completing at least Wave 2 fully (smoke+pilot+merged) is an
  acceptable partial-progress stopping point IF reported as such, not silently dropped.

TESTS/PROOFS:
- `python3 scripts/ci/check_render_progress_bytes.py --require-images
  --offload-manifest-dir artifacts/manifests/lfs_offload` — must stay green (manifest-
  verify path) for every affected family after its binaries are removed from disk/index.
- `python3 scripts/artifacts/r2_sync.py verify --manifest <path>` per family.
- sha256 round-trip: push → note sha256 → delete local → `pull-on-demand --slug <slug>`
  → re-hash → must match. This is the mutation test for this lane (agent_brief.txt §14):
  if you skip it and just trust the upload succeeded, that's not proof.
- `git diff --cached --stat origin/main` before every commit — the Poison Protocol gate
  (agent_brief.txt §4): must show EXACTLY the intended file list (manifest additions +
  .gitattributes + the specific binaries removed), nothing else. If it shows unrelated
  files (e.g. phantom deletions from a bad worktree checkout), STOP, reset the index off
  `origin/main`, and redo — do not commit through a poisoned diff.
- Proof root: `artifacts/audit/LFS_OFFLOAD_WAVE_2_4_PROOF_2026-07-22.json`.

DO NOT:
- Do NOT touch SOURCE_OF_TRUTH/ or atoms/ under any circumstance (spec §1 Q-LFS-01 hard
  NEVER list) — these are excluded from all 4 waves in the spec's own wave table.
- Do NOT rewrite git history (`git lfs migrate`, BFG, `filter-branch`, `filter-repo`) —
  forward-only per spec §0. Existing LFS blobs stay in history untouched; only new
  commits stop tracking them.
- Do NOT weaken `check_render_progress_bytes.py`'s 50KB floor or any other gate to make
  this pass — if a gate goes red, the fix is a correct manifest/upload, never a threshold
  change (agent_brief.txt §15).
- Do NOT merge a PR with >50 tracked-file deletions without explicit owner approval —
  check `gh pr diff <number> --stat | tail -1` before proposing merge, every time, per
  CLAUDE.md. Wave 3 alone (267 tracked files at authoring time) already exceeds the
  50-file threshold, so assume this gate WILL fire for Wave 3 (and likely Wave 4, 79
  files) and plan to surface the diff stat to the operator rather than being surprised
  by it — do not be lulled by the corrected, much-smaller total-byte estimate (~863MB
  vs the spec's ~9.5GB) into assuming file COUNT is also small.
- Do NOT commit from the operator's dirty root checkout (283k dirty entries at
  authoring time) — use a fresh clone/worktree per the STARTUP_RECEIPT instruction above.
- Do NOT bundle all three waves into one commit/PR — per-wave commits (or PRs) so a
  problem in Wave 4 doesn't block or entangle Wave 2/3 that already proved green.
- Do NOT invent a new manifest schema or a new uploader script — extend
  `r2_sync.py`/the existing TSV schema exactly (spec §3, §4.1).

LANDING CONTRACT:
- MERGED: PR(s) opened, required checks green (including
  `check_render_progress_bytes.py` gate), squash-merged, signal emitted. If owner
  approval was required for the deletion count, that approval is the operator's explicit
  "yes, merge" in chat — capture it in the PR description/CLOSEOUT, do not infer consent.
- BLOCKED: exact blocker (e.g. gate red, sha256 mismatch, owner-approval pending),
  evidence, and the work pushed to a remote branch (never left only local).

CLEANUP LEDGER REQUIRED:
- worktree: the fresh clone/worktree used for this lane — removed (`git worktree remove`
  + prune) once merged, or named as a HOLD if kept for a follow-up wave.
- local branch: deleted after merge.
- remote branch: deleted after squash-merge.
- scratch files: any local scratch copies used for the sha256 round-trip proof (the
  "delete local, pull-on-demand, re-hash" step) — removed after the proof completes;
  name any intentionally kept.
- background jobs: none left running.
- held artifacts: none expected; if a wave is deliberately left for a follow-up turn,
  declare it by name (e.g. "Wave 4 held, Wave 2-3 merged") rather than silently stopping.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_DevOps
- LANE: lfs-r2-offload-waves-2-4
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL: lfs-offload-wave2-4=<merge-sha, or per-wave SHAs if split into 3 PRs>
- PROOF_ROOT: artifacts/audit/LFS_OFFLOAD_WAVE_2_4_PROOF_2026-07-22.json
- TESTS: <gate results + sha256 round-trip results, per wave>
- CLEANUP: <ledger above>
- HANDOFF: artifacts/coordination/handoffs/lfs-r2-offload-waves-2-4_2026-07-22.md
- NEXT_ACTION: <e.g. "lane 03 (devops policy doc) can now proceed, citing these merge
  SHAs as evidence" or, if a wave was held, "Wave N remains open, resume via this handoff">
```

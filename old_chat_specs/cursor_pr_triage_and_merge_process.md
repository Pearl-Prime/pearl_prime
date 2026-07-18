# PR triage and merge process
_Exported on 4/9/2026 at 15:47:34 GMT+8 from Cursor (2.6.22)_

---

**User**

Act as Pearl_GitHub + Pearl_PM for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/GITHUB_OPERATIONS_FRAMEWORK.md
- docs/GITHUB_GOVERNANCE.md
- docs/BRANCH_PROTECTION_REQUIREMENTS.md
- skills/pearl-github/references/git_system.md
- skills/pearl-github/references/repo_memory.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- docs/PEARL_ARCHITECT_STATE.md
- docs/DOCS_INDEX.md

Emit a STARTUP_RECEIPT then execute.

TASK: Triage all 8 open PRs, merge what's ready, close what's stale,
rebase what's salvageable, unblock the merge queue, then hand off
clean state for next feature work.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: repo coordination, all subsystems (triage scope)

───────────────────────────────────────────────────────────────────────

PRIOR SESSION CONTEXT:

Voice pipeline LANDED:
  PR #312 — CLOSED (contaminated)
  PR #313 — MERGED (clean 8-file voice payload) → df3a41628d
  PR #315 — MERGED (workstream TSV update) → 81d8feb480

Branches DELETED: agent/voice-pipeline-activation, agent/voice-pipeline-clean

SYSTEMIC BLOCKER: Workers Builds: pearl-prime fails on ALL PRs.
  This is a Cloudflare infrastructure issue, NOT caused by any PR.
  GITHUB_GOVERNANCE.md says Workers is non-blocking, but the GitHub
  ruleset currently REQUIRES it. This blocks ALL merges via API.
  Owner must either:
    a) Fix the Cloudflare Workers build, OR
    b) Remove Workers from required checks in repo settings, OR
    c) Merge with admin bypass from GitHub UI

───────────────────────────────────────────────────────────────────────

ALL 8 OPEN PRs — CURRENT STATE (as of 2026-04-09):

READY TO MERGE (all real checks green, only Workers red):

  #314 [BLOCKED by ruleset] agent/marketing-validator-gen-z-student
    "fix(marketing): validate gen_z_student invisible scripts grid"
    Core tests: ✅  Release gates: ✅  EI V2: ✅  Governance: ✅
    Workers: ❌ (infra — not our code)
    → MERGE with admin bypass. CI prerequisite for other PRs.

  #316 [BLOCKED by ruleset] agent/video-hardening-docs
    "docs: video pipeline handoff + CJK narration wiring"
    Core tests: ✅  Release gates: ✅  EI V2: ✅  Governance: ✅  docs-governance: ✅
    Workers: ❌ (infra)
    → MERGE with admin bypass. 4 video docs only.

NEEDS REBASE (merge conflicts with main — DIRTY):

  #300 [DIRTY] agent/branch-cleanup-promo
    "chore: branch consolidation — gitignore fix + 27 stale branches deleted"
    Core tests: ❌  Release gates: ❌
    Created: 2026-04-08
    → INVESTIGATE: Is this still relevant? 27 branches may already be
    deleted by other cleanup work. If stale, CLOSE. If needed, rebase.

  #308 [DIRTY] agent/voice-narrator-research
    "feat: voice narrator research + assignments for all brands worldwide"
    Core tests: ❌  Release gates: ❌
    Created: 2026-04-09
    → LIKELY SUPERSEDED by PR #313 (merged voice pipeline). Check if
    #308 has content NOT in #313. If fully superseded, CLOSE with
    comment explaining #313 replaced it. If has unique research docs,
    extract onto clean branch.

BLOCKED (CI failures + Workers):

  #307 [BLOCKED] agent/locale-native-pipeline
    "feat: locale-native book assembly — --locale flag for CJK pipeline"
    Core tests: ❌  Release gates: ❌  locale-gate: ✅
    Created: 2026-04-08
    → INVESTIGATE: This is real feature work (CJK locale pipeline).
    Core test failures may be the same gen_z_student / marketing
    issues that #314 fixes. After merging #314, rebase #307 onto
    main and re-run CI. If tests pass, merge.

  #309 [BLOCKED] agent/full-catalog-analysis
    "feat(catalog): full catalog analysis bundle and reports"
    Core tests: ❌  Release gates: ❌
    Created: 2026-04-09
    → INVESTIGATE: Read the PR description. Is this analysis reports
    (docs/artifacts) or code changes? If docs-only, rebase after
    #314 lands and check if CI passes. If code, check scope.

  #310 [BLOCKED] agent/generate-full-catalog-12x37-alignment
    "feat(catalog): align generate_full_catalog with 12×37 planning grid"
    Core tests: ❌  Release gates: ❌
    Created: 2026-04-09
    → INVESTIGATE: This touches catalog generation code. Check if it
    conflicts with recent merges. May need rebase + test fix.

  #311 [BLOCKED] agent/catalog-bundle-discoverability
    "docs(test): catalog analysis bundle discoverability + smoke tests"
    Core tests: ❌  Release gates: ❌  docs-governance: ❌
    Created: 2026-04-09
    → INVESTIGATE: Depends on #309/#310? If so, must land those first.
    docs-governance failure suggests doc structure issues.

───────────────────────────────────────────────────────────────────────

PHASE 1: MERGE THE GREEN PRs (Owner/Admin Action)

These require admin bypass because Workers Builds is required but broken:

  # Option A: Merge from GitHub UI with admin bypass
  # Option B: Fix ruleset (remove Workers from required checks)
  # Option C: CLI with --admin flag
  gh pr merge 314 --squash --admin
  gh pr merge 316 --squash --admin

  After merge:
  git push origin --delete agent/marketing-validator-gen-z-student
  git push origin --delete agent/video-hardening-docs

  Verify main is green:
  gh run list -b main -L 3 --json name,conclusion -q '.[]|"\(.name): \(.conclusion)"'

───────────────────────────────────────────────────────────────────────

PHASE 2: TRIAGE #300 AND #308 (Likely stale)

  # PR #300 — branch consolidation
  gh pr view 300 --json files --jq '.files[].path' | head -20
  # Check: are the 27 branches it deletes already gone?
  git branch -r | grep -c 'agent/' 
  # If most cleanup already happened via other sessions → CLOSE
  # If unique cleanup remains → rebase onto main, fix CI, push

  # PR #308 — voice narrator research
  gh pr view 308 --json files --jq '.files[].path' | sort
  # Compare against files in #313 (already merged):
  # config/tts/voice_clone_reference_library.yaml
  # config/tts/narrator_voice_assignments.yaml
  # config/tts/manga_character_voice_bank.yaml
  # config/tts/voice_diversity_matrix.yaml
  # docs/VOICE_MEDIUM_PERSONA_TOPIC_RESEARCH.md
  #
  # If #308 files are subset of #313 → CLOSE as superseded
  # If #308 has docs/VOICE_MEDIUM_PERSONA_TOPIC_RESEARCH.md
  # that #313 doesn't → extract that one file onto clean branch

  For each CLOSE:
  gh pr close <NUMBER> --comment "$(cat <<'EOF'
  Closing as superseded. This work was landed via PR #313 (voice pipeline
  activation, merged df3a41628d) and PR #315 (workstream update).
  
  If any unique content from this branch is needed, it can be cherry-picked
  from the branch history before branch deletion.
  EOF
  )"

───────────────────────────────────────────────────────────────────────

PHASE 3: REBASE #307, #309, #310, #311 AFTER #314 LANDS

After #314 is merged (CI fixes on main), rebase each surviving PR:

  For each PR in [307, 309, 310, 311]:
    git fetch origin
    git checkout <branch>
    git rebase origin/main

    # If rebase conflicts:
    #   - Check if conflict is in files #314 fixed (marketing config,
    #     test fixtures, cover art registry, freebies)
    #   - Resolve by keeping main's version for those files
    #   - Keep the PR's changes for its own files
    git rebase --continue

    # Run CI locally first:
    PYTHONPATH=. python3 scripts/git/push_guard.py
    scripts/ci/preflight_push.sh

    # If tests pass:
    git push --force-with-lease
    # Wait for GitHub CI to confirm

    # If tests STILL fail:
    #   - Read the failure output
    #   - Determine if the fix is trivial (missing fixture, config key)
    #   - Fix and amend, or document the blocker

  PRIORITY ORDER for rebasing:
    1. #307 (locale pipeline — real feature, most likely to pass after #314)
    2. #309 (catalog analysis — check scope first)
    3. #310 (catalog 12×37 — depends on #309?)
    4. #311 (discoverability — depends on #309/#310?)

  CHECK DEPENDENCY CHAIN:
    git log --oneline origin/main..origin/agent/full-catalog-analysis | head -5
    git log --oneline origin/main..origin/agent/generate-full-catalog-12x37-alignment | head -5
    git log --oneline origin/main..origin/agent/catalog-bundle-discoverability | head -5
    # If #311 depends on #309/#310 commits, they must merge first.

───────────────────────────────────────────────────────────────────────

PHASE 4: WORKERS BUILDS INVESTIGATION

The Workers Builds: pearl-prime failure blocks ALL PRs. Investigate:

  # Check if it fails on main too (pre-existing)
  gh run list -b main -w "Workers Builds" -L 3 --json conclusion,createdAt

  # Check the Cloudflare error
  gh run view $(gh run list -w "" -L 10 --json databaseId,name,conclusion \
    -q '[.[]|select(.name=="Workers Builds: pearl-prime")][0].databaseId') \
    --log-failed 2>/dev/null | tail -30

  IF failure is Cloudflare-side (deploy config, wrangler version, etc.):
    → Document the root cause
    → Recommend fix (update wrangler.toml, fix Cloudflare API token, etc.)
    → OR recommend removing Workers from required checks

  IF failure is code-side:
    → Identify the failing file
    → Fix if trivial, or document for Pearl_Dev

  DELIVERABLE: Brief diagnosis in PR comment or doc update.

───────────────────────────────────────────────────────────────────────

PHASE 5: POST-TRIAGE STATE REPORT

After all actions, produce a clean state report:

  artifacts/coordination/PR_TRIAGE_REPORT_2026_04_09.md (NEW)

  Structure:
  ## PR Triage Report — 2026-04-09

  ### Merged this session
  | PR | Title | Merge SHA | Action |
  |...

  ### Closed (superseded/stale)
  | PR | Title | Reason | Replacement |
  |...

  ### Rebased and re-queued
  | PR | Title | New CI status | Blocker if any |
  |...

  ### Still blocked
  | PR | Title | Blocker | Owner action needed |
  |...

  ### Workers Builds diagnosis
  - Root cause: ...
  - Recommended fix: ...

  ### Branch cleanup
  - Branches deleted: ...
  - Branches remaining: ...

  Update artifacts/coordination/ACTIVE_WORKSTREAMS.tsv:
    - ws_video_hardening_docs_20260409 → completed (after #316 merges)
    - Add ws_pr_triage_20260409 → completed

───────────────────────────────────────────────────────────────────────

PHASE 6: HANDOFF SUMMARY FOR NEXT SESSIONS

After triage is complete, emit a handoff that lists:

  CLEAN STATE ON MAIN:
    - Last merge SHA
    - All required CI checks status
    - Count of open PRs remaining

  READY FOR NEXT FEATURE WORK:
    1. Podcast pipeline build (scripts/podcast/ — 5 scripts)
       Prompt: ready (generated in prior session)
       Branch: agent/podcast-pipeline-build (create from main)
    2. Pearl News LLM routing (CJK→Qwen, EN→Claude)
       Prompt: ready
       Branch: agent/pearl-news-llm-routing
    3. Podcast branding + marketing research
       Prompt: ready
       Branch: agent/podcast-branding-research
    4. EI v2 whole-repo audit
       Prompt: ready
       Branch: agent/ei-v2-audit

  DEFERRED:
    - Replace Libri voice stand-ins with CJK corpus clips
    - CosyVoice2 smoke test on Pearl Star
    - Scale authors beyond 480 if catalog requires

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:
No new feature branch needed for triage — work directly on existing
PR branches (rebase + push) and main (merge).

WRITE_SCOPE:
  Rebase existing PR branches (force-push with lease)
  artifacts/coordination/PR_TRIAGE_REPORT_2026_04_09.md (NEW)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (UPDATE)
  Remote branch deletes (merged/closed PRs only)

OUT_OF_SCOPE: New feature code; brand-wizard-app/; phoenix_v4/ feature
work; pearl_news/; config changes beyond CI fixes; docs content changes

NON-NEGOTIABLE:
  NEVER merge a PR that deletes more than 50 files without owner approval.
  Do NOT close PRs without checking for unique content first.
  Do NOT delete branches for open PRs.
  Do NOT force-merge past governance blocks without admin authority.
  Workers Builds is a KNOWN infra issue — do not waste time trying to
  fix it in PR code. Diagnose root cause and recommend fix separately.
  Rebase conflicts: keep main's version for files touched by #314.
  Run push-guard + preflight before every force-push.
  Check dependency chains before rebase ordering (#309→#310→#311).
  Emit CLOSEOUT_RECEIPT with full PR disposition table.


---

**Cursor**


Reading required docs and coordination artifacts, then triaging open PRs with `gh` and git.




Noting 9 open PRs (includes #317). Gathering PR check status, diff stats for mass-deletion risk, and attempting merges.




Merging PR #317 (Core/Release/EI/docs-governance green). Rebasing PR #300 onto main — `.wrangler/` isn't on main yet; the branch remains valuable.




Resolving the rebase conflict by keeping main's workstream rows and appending the `ws_branch_cleanup_20260408` row.




STARTUP_RECEIPT  
AGENT: Pearl_GitHub + Pearl_PM  
TASK: Triage open PRs, merge ready, close stale, rebase salvageable, unblock queue, hand off clean state  
PROJECT_ID: proj_state_convergence_20260328  
SUBSYSTEM: repo coordination (triage scope; all touched PR areas)  
AUTHORITY_DOCS: docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; docs/GITHUB_GOVERNANCE.md; docs/BRANCH_PROTECTION_REQUIREMENTS.md; skills/pearl-github/references/git_system.md; skills/pearl-github/references/repo_memory.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; docs/PEARL_ARCHITECT_STATE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_PROJECTS.tsv  
READ_PATH_COMPLETE: yes  
WRITE_SCOPE: artifacts/coordination/PR_TRIAGE_REPORT_2026_04_09.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; existing PR branches (rebase + force-push); remote branch deletes for merged/closed PRs  
OUT_OF_SCOPE: new feature code; brand-wizard-app/; phoenix_v4/ greenfield; pearl_news/ feature beyond triage; unrelated docs  
BLOCKERS: `Workers Builds: pearl-prime` still required on ruleset but failing (Cloudflare); merges used `--admin` where needed  
READY_STATUS: completed  

---

## Execution summary

- **Merged (squash, admin where Workers blocked):** [#314](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/314) `5df7a051`, [#316](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/316) `35eea0ebe`, [#317](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/317) `de87238e61`, [#300](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/300) `9322c319cb`, [#309](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/309) `c8aaa44f93`, [#310](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/310) `cb53020932`, [#311](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/311) `49b2a6fcc2`, [#307](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/307) `6bba146b78`.
- **Closed:** [#308](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/308) (superseded by #313).
- **Extra bookkeeping on main:** [#318](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/318) `6a52c8de4a` — adds `artifacts/coordination/PR_TRIAGE_REPORT_2026_04_09.md` and updates `ACTIVE_WORKSTREAMS.tsv` (Pearl News routing → **completed**, `ws_pr_triage_20260409` → **completed**).
- **Open PRs:** `[]` (zero). **Merge tip:** `6a52c8de4abe67ef1cb3583917a8fdf7e73d6110`.
- **Workers:** Confirms prior diagnosis — check is **Cloudflare Workers** (`pearl-prime`), **not** the four canonical GitHub required checks. **Recommendation:** align the live ruleset with [docs/GITHUB_GOVERNANCE.md](docs/GITHUB_GOVERNANCE.md) / [config/governance/required_checks.yaml](config/governance/required_checks.yaml) (drop Workers from required) and/or fix Cloudflare deploy.
- **Note:** Triage ran over **nine** pre-existing open PRs (your list plus **#317**). Remote branches for merged/closed work were deleted as safe.

---

## PR disposition (full table)

| PR | Disposition | Merge / close SHA or note |
|----|-------------|----------------------------|
| 314 | Merged (admin) | `5df7a05142106af86007af3cb291408b63d32919` |
| 316 | Merged (admin) | `35eea0ebecbadd6e99ac78b11d835b3e09e606e2` |
| 317 | Merged (admin) | `de87238e61c5a9174a886d33b014d808db967601` |
| 300 | Merged (admin) | `9322c319cbc2383c1480bbeeb86b60cfb41a2f64` |
| 308 | Closed | Superseded by #313 |
| 307 | Merged (admin, after rebase on catalog stack) | `6bba146b7838963751b26f21c841c801dbf04fe1` |
| 309 | Merged (admin) | `c8aaa44f9379e2c1693a7ed77bf7eec23ed403a5` |
| 310 | Merged (admin) | `cb530209320c4f09b86de0825345f0c8e0693a4f` |
| 311 | Merged (admin; script conflict resolved) | `49b2a6fcc2b25fb93358e82d4c9b748ccc9274cd` |
| 318 | Merged (coordination artifact) | `6a52c8de4abe67ef1cb3583917a8fdf7e73d6110` |

---

## Handoff for next sessions

**Clean `main`:** `6a52c8de4abe67ef1cb3583917a8fdf7e73d6110` · **open PRs:** 0 · **canonical CI:** green on merged PRs; **Workers** still red (infra/ruleset).

**Ready (branch from `origin/main`):**

1. Podcast pipeline — `agent/podcast-pipeline-build`  
2. Pearl News follow-ups — as needed (routing landed in #317)  
3. Podcast branding + marketing research — `agent/podcast-branding-research`  
4. EI v2 whole-repo audit — `agent/ei-v2-audit`  

**Deferred:** Libri → CJK voice clips; CosyVoice2 smoke on Pearl Star; scale authors beyond 480 if required.

---

CLOSEOUT_RECEIPT  
AGENT: Pearl_GitHub + Pearl_PM  
TASK: PR triage + merge queue unblock (proj_state_convergence_20260328)  
COMMIT_SHA: `6a52c8de4abe67ef1cb3583917a8fdf7e73d6110` (tip of `main` after coordination PR #318)  
FILES_WRITTEN: `artifacts/coordination/PR_TRIAGE_REPORT_2026_04_09.md` (on main via #318); `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (Pearl News routing completed, `ws_pr_triage_20260409` added, on main via #318)  
FILES_READ: SESSION_UNITY_PROTOCOL; GITHUB_OPERATIONS_FRAMEWORK; GITHUB_GOVERNANCE; BRANCH_PROTECTION_REQUIREMENTS; git_system; repo_memory; ACTIVE_WORKSTREAMS; SUBSYSTEM_AUTHORITY_MAP; PEARL_ARCHITECT_STATE; DOCS_INDEX; ACTIVE_PROJECTS  
STATUS: completed  
HANDOFF_TO: Pearl_Dev / Pearl_PM (next feature branches above)  
NEXT_ACTION: Fix **ruleset** (remove `Workers Builds: pearl-prime` from required checks) or **Cloudflare** deploy so normal merges do not require admin bypass; optional: pull `main` locally and drop stale temp refs `rebase-tmp-309`, `rebase/tmp-310`, `rebase/tmp-311`, `rebase/tmp-307` if present.


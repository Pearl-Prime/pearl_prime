# EXECUTE — Lane 01 — Land stranded manga wiring + reconcile audit/PR truth

**AGENT:** Pearl_GitHub · **SUBSYSTEM:** manga_pipeline / pearl_devops · **WAVE:** 0

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE. No stopping at summary, plan, PR-open, or tests-running. Turn ends only on the signal
  token or ONE concrete BLOCKER (evidence + pushed work + NEXT_ACTION).
- STARTUP_RECEIPT first (`docs/SESSION_UNITY_PROTOCOL.md`); CLOSEOUT_RECEIPT last.
- Every SHA/PR/premise below is a CLAIM — re-verify live (`git fetch origin`; `gh pr list`).
  Already-done = SUCCESS: reconcile, report delta, stand down on that item.
- DISCOVERY REPORT before writes; sibling-PR search (`gh pr list --search "<title>" --state all`).
- Substrate: plumbing pattern (temp index off `origin/main^{tree}`, `GIT_LFS_SKIP_SMUDGE=1`,
  explicit paths only, staged-diff gate `git diff --cached --stat origin/main` = exact file list).
  NEVER `git add -A`. No full worktrees.
- Preflight before any push: `PYTHONPATH=. python3 scripts/git/push_guard.py` +
  `scripts/ci/preflight_push.sh`.
- Landing: MERGED (checks read + NAMED per `bash scripts/git/pre_merge_check.sh <n>` — never "all
  checks pass") or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane01_2026-07-24.md`.
- Layer-honest closeout. PROVENANCE: research=NONE-needed (landing already-researched work);
  documents=`MANGA_LAYER_RENDER_CONTRACT_SPEC.md`, `MANGA_ARC_STORYBOARD_CONTRACT.md`;
  builds_on=`manga_bank_assembler`, `manga_composition_grammar`; inventory=EXTENDS.

## READ FIRST
`docs/PROGRAM_STATE.md` (Manga row), `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md`
(§0/§5 + R3), `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md`,
`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`, `scripts/ci/check_manga_wiring.py` (KNOWN_UNWIRED
notes), CLAUDE.md (git rules + preflight).

## MISSION
1. **Land the genre-aware bubble wiring.** Commit `aad5cf2152` on
   `agent/bestseller-atom-flow-lanes-20260721` wires `bubble_render_v2` into
   `scripts/manga/assemble_from_bank.py` (tested 33 pass/2 skip) but has NO open PR — main still
   calls the legacy renderer. Cherry-pick/plumbing-extract exactly that change onto a clean branch
   off `origin/main` (`agent/manga-bubble-v2-landing-20260724`), re-run the assemble tests, open
   PR, land it. If a sibling already landed it (check `git log origin/main -- scripts/manga/assemble_from_bank.py`
   + PR search "bubble"), reconcile and skip.
2. **Land `scripts/ci/check_manga_arc_storyboard.py`** (exists on the same branch, not on main)
   with the same procedure, wired as advisory in `scripts/run_production_readiness_gates.py`
   (append next free gate number — re-derive live; PROGRAM_STATE showed 45+ in July) — advisory
   first, promotion to required happens in Lane 07's gate pass.
3. **Reconcile the R3 vessel-wiring discrepancy at the SOURCE.** The 07-22 vision audit scores R3
   "vessels unwired" (25%), but `story_architect.apply_mode_vessel` + `chapter/writer.
   _mode_vessel_prompt_block` consume `manga_mode_vessels.yaml` (M4 #4616 per check_manga_wiring
   notes). Verify what is actually on `origin/main` (`git show origin/main:phoenix_v4/manga/series/story_architect.py | grep -n vessel`).
   Then correct whichever source is wrong — the audit doc (add a dated correction block, do NOT
   rewrite history) and/or PROGRAM_STATE's manga row via the dispatcher. A false "unwired" premise
   left standing will re-spawn duplicate wiring lanes.
4. **PR reconnaissance (report, do not hijack):** current live state of #295, #243, #95-successor
   branches; flag to the dispatcher which are merge-ready vs operator-gated. One actor per
   resource: you NEVER merge #295 — operator ruling Q-MPU-02 (2026-07-24) is REWORK: Lanes 05/06
   absorb its content and the dispatcher closes it as superseded afterward. #243 you may merge
   only if its governance verdict is green and diff ≤ 50 deletions and no sibling session is
   driving it (check for fresh commits < 24 h).

## DELIVERABLES
PR(s) landing items 1–2; audit-correction commit for item 3; recon table for item 4 in the handoff.

## WRITE SCOPE
`scripts/manga/assemble_from_bank.py` (+ its tests), `scripts/ci/check_manga_arc_storyboard.py`,
`scripts/run_production_readiness_gates.py` (one gate row), `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md`
(dated correction block only), handoff file. **OUT OF SCOPE:** story content, configs, skills,
PROGRAM_STATE (dispatcher owns), anything on #295's branch.

## GOTCHAS
- `zsh` `$VAR:path` refspec mangling — brace every `${VAR}:path` (repo memory: this silently
  corrupted a TSV union before).
- Core tests on main are chronically red at first-failure (`pytest -x` cascade) — name it, don't
  hide it, don't let it block a docs/CI-script PR that can't affect it.
- Drift detectors is a REQUIRED check — if your gate edit trips `check_canonical_pipeline_path.py`
  or the manga gates, fix your diff, never weaken a gate.

## SIGNAL
`manga-stranded-landed=<full merge SHA of item-1 PR>` (emit in PR comment + closeout; if items
split across 2 PRs, emit on the bubble PR and list both SHAs in the closeout).

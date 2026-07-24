# Lane 01 — Ground-Truth Baseline + Research / Source-Authority Landing

~~~text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub (+ Pearl_Architect for the spec-line fix) for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime. Substrate: fresh branch off latest origin/main
(agent/social-research-landing-20260724). The shared checkout is DIRTY — stage explicit paths only,
never `git add -A`/`git add .`; verify `git diff --cached --stat origin/main` shows exactly the
intended files before commit. GIT_LFS_SKIP_SMUDGE=1 on any checkout.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=social_research_landing_20260724
- EXECUTION_MODE=local_fallback (git ops) ; BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=branch/PR/handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/social_research_landing_2026-07-24.md

READ FIRST:
- docs/PROGRAM_STATE.md (§Social Media Atom Bank)
- docs/SESSION_UNITY_PROTOCOL.md ; docs/agent_brief.txt
- docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md (gap #8 — this lane executes it)
- artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md

LIVE STATE RECONCILIATION (everything below is a 2026-07-24 CLAIM — re-derive):
- git fetch origin && git rev-parse origin/main
- Re-verify per file with: git cat-file -e "origin/main:<path>" (absent = land it).
- CLAIMED absent on origin/main: docs/social_media_YT1.txt … YT6.txt;
  docs/rakuten_research_social_media_templates_jap_tw_kr.txt;
  "docs/Calibrating the Algorithm_ Aligning a Deterministic Social Media System with Audience
  Resonance Across China, Hong Kong, and Singapore.pdf".
- CLAIMED DANGLING: phoenix_v4/social/deterministic_social.py build_source_lock() on origin/main
  cites the rakuten-templates txt + the Calibrating PDF — committed code citing uncommitted research.
- CLAIMED already tracked byte-identical (do NOT re-land; local `??` is a stale-branch artifact):
  gemini_research_social_media_englis.txt, quen_research_…txt, rakuten_research_…writing…txt.txt,
  research_gemini_social_media_templates_english.txt, research_social_media.txt,
  PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md, SOCIAL_VISUAL_PUBLISHABLE_QUALITY_SPEC_2026-07-18.md,
  "Storyblocks API Agreement - 48 Social.pdf".
- CLAIMED tracked-and-locally-modified: docs/STORYBLOCKS_SOCIAL_BANK.md (+2 cross-ref lines) —
  include the delta if still present and coherent.

DISCOVERY REPORT before action: current origin/main SHA; per-file presence table (the baseline TSV
deliverable); open PR overlaps (gh pr list --search "research" --search "social").

PROVENANCE:
- research: docs/social_media_YT1–6.txt (the artifacts being landed) + RESEARCH_CURRENCY_AUDIT.md
- documents: SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md gap #8
- builds_on: evergreen_social_atom_bank (registry), social_media subsystem authority row
- inventory: EXTENDS (adds tracked research; changes no code)

MISSION (narrow):
1. Emit the verified baseline TSV: artifacts/qa/social_ground_truth_20260724/BASELINE.tsv —
   one row per social research/spec/pack artifact: path, on-origin-main yes/no, cited-by (file:line),
   action taken. Include verification of: PR #75/#96/#123/#143/#201 merge states; whether
   check_social_post_variation.py is CI-wired on main; visual-gate artifact presence
   (artifacts/qa/deterministic_social_visual_gate_20260718/ — CLAIMED absent from disk).
2. Land the local-only research to docs/ (exact paths above; PDF via LFS if >5 MB policy applies).
3. Land the 5 executed-but-untracked social prompt packs under docs/agent_prompt_packs/
   (20260718_deterministic_social_media_system_100pct, 20260718_pearl_social_media_writer_atom_bank,
   20260718_social_finish_mp4_evergreen, 20260722_social_media_audit_100pct_plan,
   20260722_social_writer_agent_deep_research_repair) — institutional memory; verify each is inert
   documentation (no secrets: grep for key/token/Bearer before staging).
4. Fix the now-stale line in docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md §gap-8
   ("exist only as untracked local files" — the two research_*.txt are now tracked) — 1-line surgical
   edit, cite this lane.
5. Add a short SOURCE AUTHORITY note (docs/SOCIAL_RESEARCH_SOURCE_AUTHORITY.md) listing every tracked
   research artifact with role — mirror of build_source_lock() rows + YT1–6 with one-line summaries
   (competitor scouting / outlier detection / remix flywheel / hook-and-demo / carousel system /
   content-team-of-agents). This is the durable answer to "is all the good stuff from research in
   docs/?".

SMALLEST SAFE BATCH:
- smoke: land YT1.txt alone + BASELINE.tsv, verify CI green on the PR.
- pilot: add YT2–6 + the two dangling files.
- scale: pack dirs + spec-line fix + source-authority note. One PR total is fine (docs-only), but
  stage/verify in these increments.

HANG PREVENTION: poll CI every 5 min; two unchanged polls → inspect logs; three → BLOCKED with
evidence. Max window 90 min.

TESTS/PROOFS: PR checks green (docs-only should not trip Core); `git diff --cached --stat
origin/main` snapshot in handoff; secret-scan output for pack dirs.

DO NOT: re-land byte-identical tracked files; edit any code; touch PROGRAM_STATE/ACTIVE_WORKSTREAMS
(Lane 08 owns); exceed ~200 files in the PR (governance warns >200 — the pack dirs are small; if
total exceeds 180, split pack-dirs into a second PR); no gate weakening; no local-only finish.

LANDING CONTRACT:
- MERGED: PR opened (title: "docs(social): land YT research + dangling source-lock files +
  executed pack dirs + baseline TSV"), required checks green, squash-merged, signal emitted,
  remote branch deleted.
- BLOCKED: exact blocker + evidence + pushed branch + handoff.

CLEANUP LEDGER: worktree (if any) removed; local+remote branch deleted post-merge; no scratch left;
declare any HOLD path.

HANDOFF: artifacts/coordination/handoffs/social_research_landing_2026-07-24.md

CLOSEOUT_RECEIPT: AGENT / LANE / STATUS / BRANCH / PR / MERGE_SHA (full) / TESTS / PROOF_ROOT
(artifacts/qa/social_ground_truth_20260724/) / CLEANUP / HANDOFF / NEXT_ACTION
SIGNAL: social-research-landed=<full merge SHA>
ACCEPTANCE LAYER: research artifacts move ABSENT→CODE-WIRED-equivalent (tracked+cited); this is
substrate, not a quality claim.
~~~

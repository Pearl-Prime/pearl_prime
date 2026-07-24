```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev (manga catalog/story lane) for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=manga_roadmap_m2_m3_20260722
- EXECUTION_MODE=local_fallback (Pearl_Writer prose authoring is Tier 1,
  operator-present, per CLAUDE.md LLM Tier Policy — no cloud/paid LLM calls)
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local checkout
- PERSISTENCE_SURFACES=branch/PR/artifact
- RESUME_SURFACE=docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md

READ FIRST:
- docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md — read in full,
  especially §0 (R-axis table), M1, M2, M3 sections.
- artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md if Lane 1 of
  this pack has landed by the time you start (prefer its numbers); fall
  back to the 2026-07-03 audit + your own live re-check of M1/M2/M3
  prerequisites if not yet available.
- CLAUDE.md manga doctrine (six-layer taxonomy; layered-assembly rule;
  stories-first sequencing law — "STORIES FIRST → per-series IMAGE BANKS →
  layered assembly at scale → locale rollout")
- specs/MANGA_CATALOG_RECONCILIATION_SPEC.md (Phase 2X reconciliation
  authority — the 37-brand/5-locale/15-genre SSOT this roadmap routes
  through)
- docs/MANGA_MARKET_INTEGRATION_V1_SPEC.md (R1 vehicle referenced by M2)
- config/manga/genre_prompt_cookbook.yaml (research-backed, #5488) — the
  craft-bible/genre research this milestone must cite per-line, not
  genre_prompt_cookbook_v2.yaml (older, pre-research — see Lane 4 of this
  pack for the live-vs-stale resolution; if Lane 4 has landed, use its
  verdict on which file is canonical before citing either)

LIVE STATE RECONCILIATION:
- `git fetch origin`; check whether M1's rails
  (check_render_progress_bytes.py, check_manga_wiring.py, story-authored
  gate) are actually merged on main — the roadmap marks them "dispatchable
  NOW" as of 2026-07-03, re-verify they exist and are wired into CI
  (`.github/workflows/`) rather than assuming from the roadmap doc's prose.
- Check `config/manga/locale_genre_allocations.yaml` — does it exist yet?
  The roadmap's M2 step 1 requires authoring it; if it already exists,
  DO NOT recreate it — read it, verify it against the 13-locale requirement,
  and extend/fix only real gaps.
- Check `market_catalog_registry` for the C-1/C-2 flags (zh_TW, fr_FR manga
  tracks missing from registry) the roadmap's M2 step 3 names — confirm
  these are still open before "fixing" something already fixed.
- Check `gh pr list` for any open PR already working M2 or M3 — do not
  duplicate.

PRE-REQUISITE CHECKS:
- m1_rails_status=<merged|missing> — if missing, that changes scope: M2/M3
  work should still proceed (roadmap marks both "Blocked on: nothing"), but
  flag the M1 gap loudly in your discovery report rather than silently
  building on ungated rails.
- If a PR is already open covering M2 or M3, STOP and report BLOCKED with
  the PR number — do not fork parallel work.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- M1 rails: merged or not, with evidence;
- M2 step 1 (locale_genre_allocations.yaml): exists or not;
- M2 step 3 (C-1/C-2 registry flags): still open or already closed;
- any open PR overlap;
- proposed smallest safe batch — this milestone spans 13 locales; do not
  attempt all 13 in one PR (see SMALLEST SAFE BATCH below).

PROVENANCE:
- research: cite the exact research doc + section per allocation line, per
  the roadmap's own "R1's verifiable chain" requirement — do not write an
  allocation without a citation.
- documents: docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md,
  docs/MANGA_MARKET_INTEGRATION_V1_SPEC.md, docs/CJK_CATALOG_PLAN.md,
  docs/US_CATALOG_PLAN.md
- builds_on: scripts/manga/generate_catalog_plan_from_strategic.py (Phase
  2X.4 vehicle — extend, do not fork a parallel generator)
- inventory: EXTENDS — new allocation config + generator extension; no
  reduction.

MISSION:
Advance Milestone M2 (R1 allocation chain) from the 100% production
roadmap: author the per-locale genre allocation config with research
citations, extend the existing Phase 2X.4 generator to consume it, and
close the C-1/C-2 registry flags — OR, if M2 is already substantially
landed on a re-check, advance to M3's first concrete step (craft-bible
completion for the highest-priority uncovered genres) instead. Report
which milestone you actually advanced and why, based on live state, not
the roadmap doc's 2026-07-03 assumption of where things stood.

DELIVERABLES (M2 path, if not already landed):
- config/manga/locale_genre_allocations.yaml — 13 locale blocks, each genre
  mix line citing its research source, encoding the CJK-genre-led vs
  Western-intent-led split (Q-MANGA-02).
- Missing research commissioned or flagged as a named follow-on blocker for
  it_IT / zh_SG / hu_HU / zh_HK if it cannot be produced Tier-1 in this
  lane (do not fabricate research to fill the gap).
- generate_catalog_plan_from_strategic.py extended to consume the
  allocation file; a diff showing allocation-driven genre mixes on a real
  run.
- C-1/C-2 flags closed in the registry, or confirmed already closed with
  evidence.
- Registry row added for the new allocation config (NEW-ARTIFACT-JUSTIFIED
  per this repo's anti-duplication convention).

DELIVERABLES (M3 fallback path, only if M2 is already done):
- Craft-bible entries for the highest-priority uncovered genres (per the
  roadmap's 44-uncovered-genre gap), Tier-1 Pearl_Writer authored — read
  the roadmap's M3 section in full for exact scope/acceptance before
  starting; this prompt does not duplicate that section's detail, defer to
  it.

SMALLEST SAFE BATCH:
- smoke: author ONE locale's allocation block (pick the locale with the
  most complete existing research triad) and confirm the generator
  consumes it correctly end-to-end.
- pilot: 3-4 more locales, prioritizing ones with existing research over
  ones needing fresh commissioning.
- scale: remaining locales — only after smoke+pilot both produce a clean
  generator diff with no regressions on already-covered locales.

HANG PREVENTION:
- poll interval: 10 minutes
- no-progress rule: inspect logs after two unchanged polls
- hard stall rule: BLOCKED or reduce to whatever locales are actually
  landable after three unchanged polls
- max window: 4 hours

TESTS/PROOFS:
- generator run showing allocation-driven diff (before/after)
- any existing manga catalog-plan tests (grep for
  test_generate_catalog_plan or similar) — must stay green
- proof root: artifacts/qa/manga_roadmap_m2_2026-07-22/ (or m3_ variant if
  fallback path taken)

DO NOT:
- no gate weakening;
- no stale metrics;
- no fake proof — do not claim a locale's allocation is "research-backed"
  without a citable source doc+section;
- no local-only finish;
- no giant batch first (do not do all 13 locales in one PR);
- do not fabricate missing research to hit a locale count — flag the gap
  and move on.

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, pushed remote branch if useful, handoff
  written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/manga_roadmap_m2_m3_2026-07-22.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Dev
- LANE: manga_roadmap_m2_m3_20260722
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL:
- PROOF_ROOT:
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```

# Social Craft Bar + Competitive Learning Loop — Prompt Pack

## Program

- **Goal:** Close the two social-media territories no existing lane owns: (1) an **enforced post-craft
  bar** (the reason posts read as template prose vs platform-native content), and (2) the
  **competitive-intelligence flywheel** (scout → outlier-detect → transcribe → remix) that 4 of the 6
  operator-supplied YT research transcripts treat as the core engine and which is entirely ABSENT from
  the repo. Plus: land the dangling/untracked research substrate, execute two already-authorized but
  never-executed plan gaps (weekly-refresh recurrence, visual flag-flip per PR #96 OPD).
- **Source request:** operator 2026-07-24 — "verify all the good stuff from social media research is in
  docs/ and specs/; are we doing social media pipelines best?; the posts still look crappy compared to
  the good stuff i see in the social media platforms, why if we're building from research?; how can we
  improve pipeline? how can we improve social media posts?" + attached docs/social_media_YT1–6.txt.
- **Router date:** 2026-07-24
- **Live origin/main at authoring:** `90e7d1e775be6f7d117b81b5d4384b9f0e2b3046` (Pearl-Prime/pearl_prime)
  — a CLAIM; every lane re-derives live before acting.
- **Prompt count:** 8 lanes + master dispatcher
- **Master dispatcher:** `00_MASTER_DISPATCH_PROMPT.md`

## Discovery grounding (verified 2026-07-24, read-only fan-out, 6 agents)

- **Research→docs conformance:** of 17 social research artifacts, 9 ARE tracked on origin/main
  (byte-identical; local `??` status is a stale-branch artifact). **8 are LOCAL-ONLY:**
  `docs/social_media_YT1–6.txt` (zero committed references),
  `docs/rakuten_research_social_media_templates_jap_tw_kr.txt` and
  `docs/Calibrating the Algorithm_….pdf` — the last two are **DANGLING**: committed code on main
  (`phoenix_v4/social/deterministic_social.py` `build_source_lock()`) cites them as read sources.
- **Technique conformance (YT1–6, 18 techniques):** FORMAT/DISCIPLINE techniques are SPECCED+CODE-WIRED
  (per-platform adaptation, hook-first, carousels, faceless video, voice grounding, human review,
  anti-clone gate). The **competitive-intelligence loop is ABSENT**: creator scouting DB, outlier-video
  detection vs channel average, scrape+transcribe winners, remix-what-works, thumbnail reference-remix,
  account warm-up — all grep-empty.
- **Why posts look crappy (evidence-backed):** (1) one rigid five-beat template on every post
  ("…is not the whole story" hook → "The mechanism is simple:" → "Try this:" → "Save this:" →
  token-swapped CTA), literal "Mechanism:" labels and "Free guide in bio" placeholders in Path-A
  captions; (2) **no craft gate exists in code** — `validate_copy_package` checks length/hashtags/banned
  phrases only, `validate_asset` text_fit/contrast are hardcoded `pass`, `validator_contract.md` is a
  draft spec; (3) **zero external performance learning** anywhere; (4) APAC posts embed writer
  stage-directions in post_text while bodies stay English; (5) all visuals resolve
  INTERIM_PREVIEW_ONLY (zero look_gate=PASS rows; 0/405 production-ready despite #96 approval OPD).
- **Prior packs:** all 5 social packs (2026-07-18/-22) executed to closure; outputs landed via
  #27/#36/#40/#41/#75/#79/#96/#114–#117/#123/#125/#127/#143; the pack dirs themselves are untracked.

## Wave Order

- **Wave 0:** Lane 01 (ground-truth baseline + research/source-authority landing)
- **Wave 1 (parallel):** Lane 06 (weekly-refresh recurrence), Lane 07 (visual flag-flip per #96)
- **Wave 2 (after `social-research-landed`):** Lane 02 (craft gate), Lane 05 (competitive-intel spec —
  operator-gated)
- **Wave 3 (after `social-craft-gate-live`):** Lane 03 (assembly variety repair)
- **Wave 4 (after `social-variety-repair-landed`):** Lane 04 (blind-judge Layer-4 packet)
- **Wave 5:** Lane 08 (final pack audit + coordination-row updates, serial)

## Lane Matrix

| Prompt | Agent | Lane | Substrate | Depends on | Signal token | Hot files |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Pearl_GitHub + Pearl_Architect | ground-truth + research landing | plumbing branch off origin/main | none | `social-research-landed=<merge-sha>` | docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN (1-line stale fix) |
| 02 | Pearl_Dev + Pearl_QA | post-copy craft gate | branch off origin/main | 01 | `social-craft-gate-live=<merge-sha>` | scripts/run_production_readiness_gates.py; phoenix_v4/social/deterministic_social.py |
| 03 | Pearl_Social_Media_Writer | assembly variety repair | branch off origin/main | 02 | `social-variety-repair-landed=<merge-sha>` | phoenix_v4/social/deterministic_social.py; config/social/words_bank.yaml; atom bank |
| 04 | Pearl_QA | blind-judge Layer-4 packet | branch off origin/main | 03 | `social-blind10-packet-ready=<merge-sha>` | none (new artifacts only) |
| 05 | Pearl_Research + Pearl_Architect | competitive-intel loop SPEC | branch off origin/main | 01 + Q-SOCIAL-COMPETITIVE-INTEL-01 | `social-competitive-loop-spec-landed=<merge-sha>` | docs/specs/ (new spec only) |
| 06 | Pearl_DevOps | weekly-refresh recurrence | branch off origin/main | none | `social-weekly-refresh-wired=<merge-sha>` | .github/workflows/ (new file) |
| 07 | Pearl_QA + Pearl_GitHub | visual gate flag-flip per #96 | branch off origin/main | none | `social-visual-flags-flipped=<merge-sha>` | media bank TSVs; golden freeze |
| 08 | Pearl_PM | final pack audit + SSOT rows | branch off origin/main | all above terminal | `social-craft-pack-audit-complete=<merge-sha>` | PROGRAM_STATE.md; ACTIVE_WORKSTREAMS.tsv (SERIAL) |

## Deconfliction

- **Open PRs checked (2026-07-24):** #310 (DashScope governance — out of scope), #295/#245/#243/#215/
  #213/#211/#200/#142/#120/#104/#100/#95/#94/#89/#60/#50 — none touches phoenix_v4/social,
  config/social, or the atom bank. Re-check at dispatch.
- **Active workstreams checked:** no live social_media rows in ACTIVE_WORKSTREAMS.tsv; the social
  project has NO ACTIVE_PROJECTS row (a gap Lane 08 closes).
- **Do NOT re-do (already landed / owned elsewhere):** phoenix_v4/social landing (#75); atom bank
  creation/scale/repair; agent+skill standup (#115); research refresh + currency audit (#114 +
  `artifacts/qa/social_research_currency_audit_20260722/`); assembler/gate fixes (#117/#123/#125/#143);
  the 100% plan doc (#79 — UPDATE, never re-author); live-scheduling investigation (ratified non-goal);
  plan gap #3 Storyblocks fill (Pearl_Int), gap #5 APAC review artifact, gap #6 density audit, gap #7
  citation repair — plan-owned lanes, cite gap IDs if touched.
- **Shared files / serialization:** `deterministic_social.py` is touched by Lanes 02 then 03 —
  STRICTLY serial (03 gates on 02's merge). Coordination hot files (PROGRAM_STATE.md,
  ACTIVE_WORKSTREAMS.tsv, operator_decisions_log.tsv) are written ONLY by Lane 08, one serial PR.
- **LLM tier policy:** all prose/spec work = Tier 1 (Claude, operator-present). Lane 06's scheduled
  workflow may only dispatch Tier-2 (Pearl Star Gemma/Qwen) or non-LLM steps — no paid APIs
  (`scripts/ci/audit_llm_callers.py` must stay green). Lane 03 adds NO runtime LLM to the deterministic
  assembly path — variety is authored into config/atoms, not generated at build time.

## Evidence Requirements

- Tests: `pytest` targeted suites per lane; `python3 scripts/ci/audit_llm_callers.py`;
  mutation-test every new gate (deliberately break → RED → revert).
- Proof roots: `artifacts/qa/social_craft_gate_20260724/`, `artifacts/qa/social_variety_repair_20260724/`,
  `artifacts/operator_read_packets/social_blind10_20260724/`, lane handoffs.
- PR/merge signals: each lane's greppable token above, emitted with FULL merge SHA.
- Operator approvals: Q-SOCIAL-COMPETITIVE-INTEL-01 (Lane 05 gate), Q-SOCIAL-BLIND10-READ-01
  (Lane 04 read), #96 OPD re-verification (Lane 07).
- Final audit: Lane 08 verifies every signal on a durable surface + updates SSOT.

## Open operator questions (batch-ratify; defaults recommended)

- **Q-SOCIAL-COMPETITIVE-INTEL-01** — Authorize the competitive-intelligence loop as SPEC scope?
  It touches the writer spec's "no scraping private accounts" non-goal boundary.
  **Default: authorize SPEC-ONLY** with a hard envelope: public metadata + official APIs/oEmbed only,
  no login-required automation, no private-account scraping, no ToS-violating collection; CODE remains
  gated on a second ratification after the spec is read.
- **Q-SOCIAL-BLIND10-READ-01** — Operator performs the Layer-4 blind read of the 10-post packet
  (10 repaired posts + 10 platform-native controls, unlabeled)? **Default: yes** — this is the only
  path to the subsystem's first PROVEN-AT-BAR claim.
- **Existing plan Q-gates** (not this pack's to decide): Q-SOCIAL-STORYBLOCKS-VOLUME-01,
  Q-SOCIAL-LIVE-SCHEDULING-NONGOAL-CONFIRM-01 — surface for batch ratification at dispatch.

## Cleanup Requirements

Every lane reports: worktree removed or HOLD+reason; local branch deleted; remote branch deleted after
squash-merge; scratch files removed or committed as proof artifacts; background jobs stopped or
declared; handoff at `artifacts/coordination/handoffs/<lane>_2026-07-24.md`.

## Final Status

- Status: AUTHORED (this pack) — not yet dispatched.
- Blockers: none to dispatch Wave 0/1.
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead (Pearl_PM dispatcher) agent.

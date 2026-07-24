# Phoenix Omega — Systems State (Pearl_PM × Pearl_Architect joint snapshot)

**Date:** 2026-07-24 · **Author:** Piper (router), synthesizing Pearl_PM program view + Pearl_Architect architecture view
**Grounding:** all 2026-07-22→24 session handoffs (docs/, docs/sessions/, docs/handoffs/, artifacts/coordination/handoffs/), PROGRAM_STATE.md (verified 2026-07-22 @ `a08b8af17b`), PEARL_ARCHITECT_STATE.md (cap `SOCIAL-ATOM-BANK-VIBE-01`, 2026-07-21), coordination TSVs, live `gh` state at authoring time (origin/main `67e5869d8d`).
**Standing caveat:** every PR number/SHA below is a CLAIM at authoring time. This repo merges hourly — re-verify live before acting.

## 1. Per-track state (layer-honest)

| Track | State | Acceptance layer |
|---|---|---|
| Flagship book (gen_z×anxiety) | Operator Layer-4 approved 2026-07-07; goldens frozen; live gate re-score FAILs F6/F7 (human verdict stands) | **PROVEN-AT-BAR (bestseller register)** |
| en_US catalog | 1,519 listings authored, 12,138 plannable; EPUBs ≈ 124; listings ≠ books | Listings DONE; content **authored candidate** at best |
| Waystream | 800/800/800 titles locked; 89 EPUB artifacts on R2 chain (#1930/#1934 CI-native) | **system working** (micro-wave, not catalog-scale) |
| zh-TW quality program | COMPLETE & MERGED: contamination 872/880 (#81–86), CI ratchet (#175), 14/14 name families, retranslation waves (#152–155), 863-row authoring backlog (#162) | **system working**; content backlog remains authored-not-done |
| zh-TW Waystream 100 books | Zero books complete end-to-end. Pack exists (`docs/agent_prompt_packs/20260723_waystream_zhtw_100_books/`, local commit `cd70b60924`, unpushed). Blocker chain COLLAPSED: #234 MERGED replaces #131; remaining gate = PR #223 (locale-aware EXERCISE classifier) | **ABSENT→ready-to-smoke** |
| zh-CN | Wave-1 shards branches exist; compassion_fatigue stub defect FIXED on main via **PR #234 (merged 2026-07-23T18:17Z)**; #131/#231/#235 superseded — close, don't merge | coverage ~43%, **in progress** |
| Manga | 3 pilot cells / 37 episodes byte-verified on origin/main (10 PRs merged, incl. #275 fixing the ep_001 landing gap). Vision re-audit axes R1–R8 range 8–47%. Genre-bubble wiring stranded on `agent/bestseller-atom-flow-lanes-20260721` (`aad5cf2152`, no PR). Outfit-continuity tested, unpushed (`61f9a8fb85`, handoff `f6e40c62be`). Scale gated on operator read-approval | **EXECUTED-REAL** (pilot); nothing PROVEN-AT-BAR |
| Social media atom bank | ~1,952 atom rows EXECUTED-REAL; 0 PROVEN-AT-BAR; 98.7% boilerplate citations; no authority-map row | **EXECUTED-REAL / unwired governance** |
| Brand wizard | PR #166 merged but REGRESSED: deleted `pearl_prime_entry.html` (14-lane routing incl. pt_BR) → `test_wizard_locale_routing.py` 3/7 red. Deploys failing since 07-22 (missing `CLOUDFLARE_API_TOKEN` secret). #58 (assignment.js canonical-vs-R2 fix) CLOSED-unmerged, bug possibly live | **REGRESSED — needs repair** |
| Storefront / GHL | Live (72-SKU CF #1791; 793 feed entries; 2 paid attaches) | **system working** (listings-scale) |
| TTS / media | EN CosyVoice bank shipped 07-19; CJK6 routing-ready, never run; DashScope blocked account-wide (billing arrearage — operator); Storyblocks cover bank 24/24 | **CONFIG-EXISTS→EXECUTED-REAL (EN only)** |
| CI / governance | **main has NO branch protection (live 404 confirmed)** — convention-only. Core tests red (enhancement_contract_v21) + Release gates flaky (missing `opencc` on runner). New live CI-status pre-merge gate landed (PR #199 merged). 31/31 production readiness gates reported green 07-23 | **at risk — Lane 02 target** |

## 2. Merge queue truth table (33 open PRs, live at authoring)

- **Superseded → CLOSE after file-diff verify:** #131, #231 (dup of merged #234), #235 (baseline approach vs #234's real prose), #55 (superseded by #54/#75/#201/#175), #53 (verify remainder vs main first).
- **Ready/near-ready → MERGE (Rule-0 + governance + CI gate):** #50, #56, #60, #62, #73, #74, #76, #89, #93, #94, #95, #97, #100, #104, #107, #120, #142, #200, #211 (as docs record), #213, #215, #223, #246, #271, #272, #274, #276.
- **HOLD for operator read:** #243, #245 (zh_TW manga smoke cell — dispatch doctrine forbids solo merge without operator quality read).
- **Closed-unmerged needing decision:** #58 (re-land if bug live — Lane 05), #68 (zh-TW retranslate — superseded by #152–155; verify then discard branch).

## 3. Worktree / branch disposition (survey 2026-07-24)

**Delete (merged or empty; 9):** `wt-zhtw-registry`†, `gov-exception-wt`† (†dirs gone, metadata only), `.claude/worktrees/agent-a1ee798b347ab3a6f` (bare main), `agent-a44a14eb8ebd93d42` (#147 merged), `fervent-shaw-761791` (#201 merged), `.worktrees/teacher-ob-20260721` (#18 merged), `zh-cn-phase3` (#77 merged), `social-atom-scaleup-wave3-20260721` (#13 merged), `main-ci-unbreak-20260722` (poisoned, no content).
**Rescue then delete (real unmerged work; 8):** `translation-100pct-unblock` (1 commit; worktree poisoned — cherry-pick from clean checkout), `manga-one-us-en-book-20260716` (2), `session-mining-specs-do-all-20260718` (3), `prod_2h_20260719` (7 — Perfect Books waves), `translate_20260716` (13 — locale waves; dedupe vs merged retranslation first), `manga-genre-story-only` (1), `outfit_continuity` (1), `zhtw-clean-retranslate-20260722` (**verify-then-discard**: batches 015–020 phantom-delete-broken per ZHTW_TRANSLATION_QUALITY_HANDOFF_20260724; committed batches 1–8 likely superseded by merged #152–155).
**Inspect uncommitted WIP (2):** `agent-fix-ci-two-gates-20260722` (7 mod + 10 untracked: manga gates, register_output_strengthen), `worldwide_lang_20260720` (spec + 4 scripts, all untracked).
**Current branch** `agent/bestseller-atom-flow-lanes-20260721`: 9 commits ahead of origin/main (handoffs `6756fe5fe1`,`f551bb48ec`,`b0323b81ca` + waystream pack `cd70b60924` + genre-bubble `aad5cf2152`) — land via clean cherry-pick branch, never push the dirty tree.
**Local branches:** ~980 total; most map to squash-merged PRs — verify-ahead-not-stale (`git diff origin/main` empty ⇒ delete).

## 4. Coordination-registry drift (Lane 04 targets)

1. `ACTIVE_WORKSTREAMS.tsv` references 4 project_ids absent from `ACTIVE_PROJECTS.tsv`: `PRJ-JAPAN-MANGA-ONLY-CATALOG-V1`, `PRJ-PEARL-PRIME-Q-GATES`, `proj_integrations_20260719`, `proj_manga_100pct_certification_20260703`.
2. `SUBSYSTEM_AUTHORITY_MAP.tsv` has no `social_media` row (PROGRAM_STATE admits this).
3. `DOCS_INDEX.md` last updated 2026-06-17 — 5+ weeks stale.
4. `PROGRAM_STATE.md` verified 07-22; missing: #234 supersession, manga pilot completion (#275), zh-TW program completion, brand-wizard regression.
5. PROGRAM_STATE's own flag: ex-#5237/#5206 PR numbers no longer resolve.

## 5. Security / operator-tier (see OPERATOR_ACTIONS.md)

R2/Cloudflare key rotation (leaked 07-21, deferred); `CLOUDFLARE_API_TOKEN` GitHub secret missing; DashScope billing arrearage; branch-protection enablement approval; manga/zh-TW quality reads.

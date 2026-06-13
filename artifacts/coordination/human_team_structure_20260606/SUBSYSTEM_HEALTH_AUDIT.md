# Phoenix Omega — Subsystem Health & Maintenance-Burden Audit

**Date:** 2026-06-09
**Author:** Pearl_Architect
**Session:** `pearl-architect-human-team-structure-20260606`
**Companion:** `HUMAN_TEAM_STRUCTURE.md` (this audit drives role design there)

---

## Purpose

Audit every subsystem in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` to size human-team demand. For each: current health, in-flight ws count, complexity, maintenance burden (hr/week sustained), gap risk if unowned, top 3 in-flight items, required human role(s). The aggregate hr/week roll-up calibrates the **lean-team headcount ceiling** and the **endless-team role roster width**.

Method:

- Health = column 5 in `SUBSYSTEM_AUTHORITY_MAP.tsv` (active / proposed / backlog).
- In-flight ws count = non-completed ws's whose `subsystem` column 6 mentions the subsystem (per-row tokenization on `;`).
- Complexity = 1-5 read of the authority doc(s): depth of contract, number of integration surfaces, model/pipeline coupling, drift frequency observed in cap-entry history.
- Maintenance burden = hr/week to sustain WITHOUT new-feature work: ongoing prompt-tuning, atom-bank curation, CI gate calibration, credential rotation, locale parity drift, etc.
- Gap risk = first-order operational consequence if no human owns it for 2 weeks.

---

## Per-Subsystem Audit Table

| # | subsystem_id | owner_agent | health | active ws | complexity (1-5) | maintenance hr/wk | gap risk if unowned | top 3 in-flight items | required human role(s) |
|--:|-------------|-------------|--------|----------:|-----------------:|------------------:|---------------------|----------------------|------------------------|
| 1 | core_pipeline | Pearl_Prime | active | 29 | 5 | 35-45 | Catastrophic — gates every book ship; bestseller-grade output regresses across catalog | bestseller pipeline default Path B; register-gate F11/F12 detectors; teacher-mode wrapper semantics | Senior Engineer (core_pipeline); QA (prose quality); Pearl_Prime shadow |
| 2 | manga_pipeline | Pearl_Dev | active | 26 | 5 | 30-40 | Manga catalog halts; ep_002 stalls; 37-brand × 4-locale matrix freezes | Manga V2 layered pipeline (5 phases); ep_002 V5.1 pose library; zh_TW/zh_CN blocked_lora drain | **Manga Tech Lead** (operator-named); Senior Engineer (manga); QA (panel review); Pearl_Author shadow |
| 3 | pearl_prime | Pearl_Prime | active | 15 | 4 | 20-25 | Bestseller pipeline regresses; storefront launch blocked | Pearl Prime acceptance scorecard promotion; ship-readiness aggregator; pipeline-mode default flip to spine | Senior Engineer (core_pipeline shared); QA (prose); Pearl_Prime shadow |
| 4 | brand_admin | Pearl_Prez (de facto: Pearl_Brand) | active | 11 | 3 | 15-20 | Operator weekly surface goes stale; brand-admin v2 dashboard drifts; weekly cron breaks | Per-platform download route; brand-admin v2 cron wireup; planned-volumes per-brand backfill | Marketing/Brand Ops; Senior Engineer (brand_admin); Pearl_Brand shadow |
| 5 | teacher_mode | Pearl_Editor | active | 6 | 5 | 15-20 | Atom-bank drift; teacher voice corrupts; HOOK scene-first regression | HOOK P2 rewrite batch; teacher wrapper intro variants; ahjan teacher-bank framing re-author | Research/Editor; Pearl_Editor shadow; Pearl_Writer shadow |
| 6 | marketing | Pearl_Marketing | active | 6 | 3 | 10-15 | Funnel decay; freebie→book route breaks; 25-brand themes unauthored | Catalog generator v1.1 25-brand authoring; music freebie funnel; warrior_calm ja_JP tentpole | Marketing/Brand Ops; Pearl_Marketing shadow |
| 7 | integrations | Pearl_Int | active | 6 | 2 | 8-12 | API/credential rot; CJK locale ships blocked; RunComfy spend creeps | RunComfy wiring + spend ledger; HF token rotation; Japan platforms hub | DevOps/Integrations; Pearl_Int shadow |
| 8 | pearl_devops | Pearl_DevOps (proposed row) | active | 5 | 4 | 15-20 | Merge gate failures; LFS contention; CI red blocks every PR | Brand-admin v2 weekly cron; release gates Phase 3; tooling maintenance (pre_merge_check, audit_llm_callers) | DevOps/CI/Governance; Pearl_DevOps shadow |
| 9 | translation | Pearl_Localization | active | 2 | 3 | 10-15 | CJK6 locale launches delayed; ja_JP/zh_TW/zh_CN ship blocks | CJK atom translation Qwen2.5; Japan manga-only catalog; locale-12 expansion regen-check | Localization (per-locale); Pearl_Localization shadow |
| 10 | video_pipeline | Pearl_Video | active | 2 | 4 | 15-20 | 30s teacher-manga stalls; audiobook video drift; soundtrack stage hardening regresses | Teacher × manga 30s video V1 (12-13 deliverables); audiobook video pipeline; CJK narration wiring | **Video Productionization Lead** (operator-named); Pearl_Video shadow |
| 11 | music_mode | Pearl_Editor | active | 2 | 3 | 8-12 | 38+ music brands sit dormant; first-real-artist seed never lands | Music brand integration V1 (catalog generator + wizard + live route); first-real-artist musician_banks seed | Music Mode Curation; Pearl_Editor shadow |
| 12 | ei_v2 | Pearl_Research | active | 2 | 3 | 6-10 | Quality scoring drifts; learner feedback stale; KB activation reverts | EI v2 KB activation drift; learner feedback queue; ei_article_scorer for Pearl News | Research/Editor; Pearl_Research shadow |
| 13 | dashboard | Pearl_Brand (per DASH-02 cap) | active | 1 | 3 | 6-10 | Brand-admin v2 + onboarding hub drift; navigation breaks for operator | Brand-admin v2 navigate link; teacher_showcase media wiring; v2 axes_present field maintenance | Marketing/Brand Ops; Pearl_Brand shadow |
| 14 | pearl_news | Pearl_News | active | 1 | 4 | 12-18 | Daily news cadence breaks; editorial firewall lapses; CJK→Qwen routing fails | Pearl News publisher wiring (D-PN-1); 14-slot re-QA (D-PN-2); sidebar (PR #853 anchor) | **Pearl News Editor + Translator** (paired); Pearl_News shadow |
| 15 | recommendations | Pearl_PM | backlog | 1 | 3 | 4-8 | Reactive only; scoring weights stale; recommender promotion never completes | recommender promotion queue; scoring weight tuning | (subsumed by Senior Engineer (core_pipeline) at lean tier); Pearl_PM shadow |
| 16 | audiobook_pipeline | Pearl_Dev | active | 0 (subsumed in `brand_admin_v2_real_content_build_audiobook_axis`) | 3 | 10-15 | Per-locale ops drift; platform refund rate creeps; M4B + chapter markers regress | Brand-admin v2 audiobook axis (M4B + chapter markers × 37 brands); CosyVoice2 Pearl Star smoke; refund-rate review | **Audiobook Voice + Mix** (operator-named); Pearl_Audio shadow |
| 17 | podcast_pipeline | Pearl_Prime | proposed | 0 (subsumed in `brand_admin_v2_real_content_build_podcast_axis`) | 4 | 10-15 | Weekly cadence breaks; RSS feed rot; ID3/loudness regresses | Brand-admin v2 podcast axis (MP3 + show notes × 37 brands); Spotify/Apple feed health; ID3 tag + loudness | Audiobook Voice + Mix (shared); Senior Engineer (integrations) |
| 18 | ite | Pearl_Dev | active | 0 (rolled into manga_pipeline) | 3 | 4-8 | Manga gate drift (silent regressions on register_gate F11) | F11 hardening; gate_registry maintenance | Senior Engineer (manga) shared |
| 19 | trend_feeds | Pearl_Int | active | 0 (rolled into integrations) | 4 | 8-12 | RSS source health drift; budget_guard regresses; trend keywords stale | trend keywords curation; budget_guard tuning | DevOps/Integrations shared |

**Total non-completed workstreams across all subsystems:** ~94 (after de-duplication of multi-subsystem ws's).

---

## Aggregate Weekly Hours Demand

| Tier | Subsystems | hr/wk midpoint |
|------|-----------|---------------:|
| Tier 1 (load-bearing) | core_pipeline, manga_pipeline | 65-85 |
| Tier 2 (program-critical) | pearl_prime, brand_admin, teacher_mode, video_pipeline, pearl_devops, pearl_news | 90-115 |
| Tier 3 (steady-state) | marketing, integrations, translation, audiobook_pipeline, podcast_pipeline, music_mode, ei_v2, dashboard | 70-100 |
| Tier 4 (reactive) | recommendations, ite, trend_feeds (subsumed) | 16-28 |
| **Aggregate** | **19 subsystems** | **240-310 hr/wk** |

**Calibration consequence:**

- At 40 hr/wk per FTE: ~6.0-7.8 FTE just to **sustain** what exists (no new features). Plus 2.0-3.0 FTE for active Phase A/B program execution (storefront V1, manga V2 Phase A-E, teacher-30s video, etc.). → endless team realistic floor ~ **10-15 FTE**.
- Lean team at 5 FTE × 40 hr/wk = 200 hr/wk → covers ~80-83% of sustain demand; **forces deprioritization of Tier 4 + parts of Tier 3** (recommendations stays reactive; podcast cadence slows; music_mode V1 holds steady-state only).

---

## Per-Role Demand Summary (drives endless-team roster width)

Roll-up of `required human role(s)` column above, weighted by ws count:

| Role family | Subsystems served | Weighted demand (hr/wk) | Headcount at endless | Headcount at lean |
|------------|-------------------|------------------------:|---------------------:|------------------:|
| Project Manager (overall) | all 19 (coordination) | 30-40 | 1.0 | 1.0 |
| Manga Tech Lead | manga_pipeline, ite | 30-40 | 1.0 | 0.0 (rolled into Senior Dev) |
| Video Productionization Lead | video_pipeline, podcast_pipeline (shared) | 20-30 | 0.5-1.0 | 0.0 (rolled into Senior Dev) |
| Senior Engineer (core_pipeline) | core_pipeline, pearl_prime, recommendations, ei_v2 | 60-80 | 1.5-2.0 | 0.5 |
| Senior Engineer (manga) | manga_pipeline, ite | 30-40 | 1.0 | (covered by Manga Tech Lead) |
| Senior Engineer (integrations) | integrations, trend_feeds, podcast_pipeline | 20-30 | 0.5-1.0 | 0.0 (rolled into Senior Dev) |
| Senior Engineer (brand_admin) | brand_admin, dashboard | 15-25 | 0.5-1.0 | 0.0 (rolled into Senior Dev) |
| QA (prose quality) | core_pipeline, pearl_prime, teacher_mode | 15-25 | 0.5-1.0 | 0.5 |
| QA (manga panel review) | manga_pipeline, video_pipeline (manga 30s) | 15-25 | 0.5-1.0 | 0.5 |
| QA (audiobook listening) | audiobook_pipeline, podcast_pipeline | 10-15 | 0.5 | 0.0 (rolled into single QA) |
| QA (storefront purchase smoke) | storefront (proposed subsystem), brand_admin | 10-15 | 0.5 | 0.0 (rolled into single QA) |
| Marketing/Brand Ops | brand_admin, marketing, dashboard, music_mode | 20-30 | 1.0-1.5 | 1.0 |
| Business Analyst | catalog economics, 800-config decisions, pricing | 10-15 | 0.5-1.0 | 0.0 (PM doubles) |
| Research/Editor | teacher_mode, ei_v2, pearl_news, atom authoring | 30-45 | 1.0-1.5 | 0.5 |
| Localization (per-locale) | translation, pearl_news translation, ja_JP/zh/ko stack | 25-40 | 1.5-2.0 (ja_JP + CJK + ko) | 0.0 (contract per-batch) |
| Generalist / Reader-Reviewer | reading QA, basic marketing, simple ops | 10-20 | 1.0-2.0 (cohort) | 0.0 |
| DevOps / CI / Governance | pearl_devops, integrations | 20-30 | 1.0 | 0.5 (PM/Senior Dev rotate) |
| Pearl News Editor + Translator | pearl_news | 12-18 | 1.0-1.5 (editor + translator pair) | 0.0 (reactive only) |
| Audiobook Voice + Mix | audiobook_pipeline, podcast_pipeline | 15-25 | 1.0 | 0.0 (contract per-batch) |
| Storefront E-commerce Ops | storefront (proposed subsystem) | 10-15 | 0.5-1.0 | 0.0 (PM doubles at launch) |
| Music Mode Curation | music_mode | 8-12 | 0.5 | 0.0 |
| **Aggregate (endless)** | | **240-310** | **~15-20 FTE** | **~5-6 FTE** |

---

## Notes on Reading the Audit

1. **Maintenance hr/wk is steady-state.** It does NOT include net-new program execution (storefront V1, manga V2 ramp, video productionization). Add ~3-4 FTE on top for active program throughput at endless tier.
2. **Active ws count is a lagging indicator.** Pearl_Dev's 49-ws backlog signals dev overload AND the fact that Pearl_Dev sweeps multiple subsystems. The endless team breaks Pearl_Dev's surface area across 3-4 Senior Engineers + Manga Tech Lead + Video Lead.
3. **Subsystems with active ws = 0** (audiobook_pipeline, podcast_pipeline, ite, trend_feeds) are NOT dormant — they're rolled into multi-subsystem ws's owned by parent agents (brand_admin v2 axis ws's for audiobook/podcast; manga_pipeline for ite; integrations for trend_feeds). Sustain hr/wk is still real.
4. **Pearl_Brand, Pearl_Author, Pearl_Audio, Pearl_DevOps** are observed as `owner_agent` in workstreams but absent from the 14-agent canonical `agent_registry.yaml`. → governance-amendment territory; surfaced in `HUMAN_TEAM_STRUCTURE.md` §7 open questions.
5. **storefront** is real (7+ in-flight branches) but has **no row in `SUBSYSTEM_AUTHORITY_MAP.tsv` and no spec at `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md`.** → §7 open question; cap-entry amendment recommended.

---

## Cross-References

- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` (19-row source of truth)
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` (12 active projects)
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (210 ws rows; 116 completed)
- `config/agents/agent_registry.yaml` (14-agent canonical roster)
- `docs/AGENT_SYSTEM_AUDIT_2026_04.md` (prior audit; this work extends to human counterparts)
- `docs/PEARL_ARCHITECT_STATE.md` (cap-entry index; routing memory)
- `docs/PEARL_PM_STATE.md` (Phase 1 → Phase 2 P0 snapshot, 2026-05-10)
- `HUMAN_TEAM_STRUCTURE.md` (this audit's downstream consumer)

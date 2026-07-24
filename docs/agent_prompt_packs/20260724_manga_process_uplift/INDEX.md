# Manga Process Uplift — Prompt Pack (2026-07-24)

**Program goal:** put enforced process around the manga program end-to-end — marketing-verified
genre assignment → researched durations/cadence → 100-episode master planning → per-arc episode
planning → checklist-gated story writing → editor QA → storyboard → bank demand analysis →
assembly — using the machinery that already exists, extending it in place, and promoting every
checklist to a gate.

**Live truth anchor (router, 2026-07-24):** `origin/main` = `59c61a2718409ba9180b6ec0c3109948683394b3`.
Open manga PRs at authoring time: **#295** (draft: 4-arc plans + 10 craft bibles,
`claude/manga-12ep-arc-authoring-egnwqf`), **#243** (roadmap drift fix + 48ep program registration).
Stranded on `agent/bestseller-atom-flow-lanes-20260721`: genre-aware bubble wiring `aad5cf2152`
(tested, no PR). Every lane re-verifies these claims live before acting.

**Source request:** operator 2026-07-24 — more process around manga: marketing decides genres;
verify research for durations (manga / webtoon / US illustrated self-help books), arc cadence,
bestseller story elements, enduring main characters; plan 100 episodes with genre-nuanced arcs;
per-arc 12-episode planning pass with per-episode checks (self-help topic, teacher/music arc);
checklist-gated story writing with editor QA; storyboard agent selecting bank layers; bank demand
analysis from the plan; assembly with genre panel grammar; genre/editor/QA agents throughout.
**"Research trumps any of my ideas, but if any of my ideas can help, use them."**

## Operator-idea disposition (research vs request — ruled per the discovery pass)

| Operator idea | Research/repo verdict | Disposition |
|---|---|---|
| Marketing decides genre→brand | Already the system: `docs/GENRE_PORTFOLIO_PLAN.md` per-brand allocation grounded in `artifacts/research/marketing_grounded_per_genre_allocation_2026-05-13.md` + `popular_genre_ranking_2026-05-02.md` (Oricon/Circana/Ken sourced) | **VERIFY + refresh currency (Lane 04)** — do not redo |
| Durations per genre | Manga/webtoon: DEEP (`config/manga/manga_pacing_by_genre.yaml`, 22 families; webtoon technical reference). US illustrated self-help: **real gap** | **Research only the gap (Lane 02)** |
| Arc every 12 eps — "doesn't have to be 12; research it" | Craft bibles §7 carry genre arc shapes (webtoon romance ~25-ep seasons; iyashikei 4-vol cycles) but no sourced cadence study exists | **ADOPTED — Lane 03 produces the empirical cadence study; arc lengths become genre-derived, never fixed-12** |
| Plan 100 episodes up front | No research against it; live program is 48-ep (4×12, PRs #295/#243, ja_JP pilot read-approved #196). 100-ep master planning is cheap (planning-only) and de-risks arc direction | **ADOPTED as a master-plan layer (Lane 06)** wrapping — not replacing — the live 48-ep program |
| Manga editor / story QA agents | Story Excellence Realization Gate is CODE-WIRED (threshold 85); `manga_arc_storyboard_planner.md` agent exists; **no manga skill exists** | **ADOPTED (Lane 08)** — thin skills binding existing canonical gates/contracts |
| Storyboard agent picks bank layers | Contract + schema + CI check exist; **nothing downstream consumes arc_storyboard yet** | **ADOPTED as wiring (Lane 10)** — consume, don't re-spec |
| Bank demand analysis from the plan | `scripts/manga/generate_bank_contracts_from_script.py` exists (M5-prep), per-episode only | **ADOPTED as extension (Lane 09)** — series-level rollup |
| Per-genre sub-agents (25 genres) | 25 parallel agents = drift surface; checklists can parameterize one agent | **MODIFIED** — one editor/writer/storyboarder skill each, parameterized by per-genre checklist files (Q-MPU-04) |
| "Past stories were stupid — scenes, not stories" | Confirmed by history; the 2026-07-18 excellence-gate lane is the enforcement answer; craft grade at scale still unverified (R2 ~47%) | Lanes 05/07/11 close it: bibles complete → checklists machine-readable + gated → pilot proves the loop |

## Prompt count and wave order

12 lane prompts + this INDEX + `00_MASTER_DISPATCH_PROMPT.md` (Pearl_PM dispatcher — REQUIRED entry point).

| Wave | Lane | Owner | Mission (one line) | Gates on |
|---|---|---|---|---|
| 0 | 01_land_stranded_and_reconcile | Pearl_GitHub | Land `aad5cf2152` bubble wiring + `check_manga_arc_storyboard.py` to main; reconcile R3 vessel-audit discrepancy at the source; reconcile #295/#243 | — |
| 1 | 02_research_us_illustrated_formats | Pearl_Research | US illustrated self-help book category study: page counts, art:text ratio, trim, comps | — |
| 1 | 03_research_arc_cadence | Pearl_Research | Sourced per-genre arc-cadence study (arc break every N eps) → `arc_cadence` block in pacing SSOT | — |
| 1 | 04_research_mc_endurance_and_market_refresh | Pearl_Research | Enduring-protagonist commercial-traits study per genre + 2026 market-data currency refresh | — |
| 1.5 | 05_craft_bibles_completion | Pearl_Writer | Fill 3 stub bibles (isekai, psychological_horror, school_coming_of_age) + wave-2 drawing-tradition items 1/2/4 | — |
| 2 | 06_series_master_plan_contract | Pearl_Architect + Pearl_Dev | 100-episode Series Master Plan contract: genre-cadence arcs, mode-arc (teacher/music/topic) per arc, per-arc episode-planning pass, validator | 03 |
| 2 | 07_genre_checklists_wired | Pearl_Dev + Pearl_Editor | Compile bibles → machine-readable per-genre checklists; wire into excellence gate + storyboard lint | 04, 05 |
| 2 | 08_manga_skills | Pearl_Architect | `skills/manga-editor` + `skills/manga-story-writer` + `skills/manga-storyboarder` (thin, binding canonical contracts) | 07 |
| 2 | 09_bank_demand_rollup | Pearl_Dev | Series-level image-bank demand rollup (plan → union of backdrops/poses/objects → bank contract + PuLID/LoRA plan) | 06 (schema only) |
| 2 | 10_storyboard_consumption_wiring | Pearl_Dev | Make panel-prompt/assembly path consume `arc_storyboard` (storyboard drives layer selection) | 01 |
| 3 | 11_pilot_end_to_end | Pearl_Writer + Pearl_Editor | ONE series through the full new loop: master plan → arc pass → 2 episodes → checklists+gates → storyboard → bank delta → assembly | 06, 07 (09/10 best-effort) |
| 4 | 12_final_audit_ssot | Pearl_PM | Verify every lane's signal, update PROGRAM_STATE manga row + workstreams, name acceptance layers honestly | all |

**Dependencies are signal-gated, never narrative.** Signal tokens (each `=<full merge SHA>`, durable on the merged PR / PROGRAM_STATE):
`manga-stranded-landed`, `us-illustrated-format-research-merged`, `manga-arc-cadence-research-merged`,
`manga-mc-endurance-research-merged`, `manga-craft-bibles-complete`, `manga-series-master-plan-contract-merged`,
`manga-genre-checklists-wired`, `manga-skills-registered`, `manga-bank-demand-rollup-merged`,
`manga-storyboard-consumed`, `manga-process-pilot-system-working`, `manga-process-uplift-audited`.

## Owners / subsystem authority

Subsystem `manga_pipeline` (owner **Pearl_Dev**; authority `specs/AI_MANGA_PIPELINE_SUMMARY.md`,
`docs/MANGA_IMPLEMENTATION_OUTLINE.md`). Research lanes = Pearl_Research; prose = Pearl_Writer
(Tier-1 Claude; **never Qwen for zh-TW**, Qwen = CJK6 unattended only); coordination = Pearl_PM;
git ops = Pearl_GitHub. Strategy canon: `docs/GENRE_PORTFOLIO_PLAN.md`, `docs/CJK_CATALOG_PLAN.md`,
`docs/US_CATALOG_PLAN.md`, `docs/MANGA_MODE_STRATEGY.md`. Roadmap:
`docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` (this pack advances M3/M4/M5/M6 inputs).

## Substrate (every lane)

Shared checkout is DIRTY and sibling sessions are live. No full worktrees (262k files, ~3.2 GB LFS
smudge). Docs/config lanes use the plumbing pattern (temp index off `origin/main^{tree}`,
`GIT_LFS_SKIP_SMUDGE=1`, explicit paths, staged-diff gate). Code lanes may use a sparse-cone
worktree ≥20 GB free — poison protocol mandatory. Pearl Star GPU work: RAP queue-first (`pscli`);
none expected in this pack (Lane 11 assembly is offline/INTERIM-tolerant).

## Hot-file collision map (serialize; ONE writer at a time)

- `docs/research/manga_craft/index.md` — Lanes 04/05/07 all touch it. **Serial order 05 → 04 → 07.** Known prior collision (dup numbering, 2026-07-24 session) — re-read before edit, grep for dup numbers after.
- `config/manga/manga_pacing_by_genre.yaml` — Lane 03 adds `arc_cadence`; Lane 06 reads it. 03 lands first.
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`, `docs/PROGRAM_STATE.md`, `CANONICAL_ARTIFACTS_REGISTRY.tsv`, `docs/DOCS_INDEX.md` — dispatcher/Lane 12 are the serial owners; other lanes REQUEST rows via their closeouts.
- `config/manga/gate_registry.yaml`, `story_excellence_gates.yaml` — Lane 07 only.
- PRs #295/#243 and branch `agent/bestseller-atom-flow-lanes-20260721` — Lane 01 only (one actor
  per resource). Exception per Q-MPU-02 ruling: Lanes 05/06 READ `claude/manga-12ep-arc-authoring-egnwqf`
  as an absorb-source (read-only; land via their own PRs); only the dispatcher closes #295.

## Operator questions — RESOLVED (operator ruling 2026-07-24; dispatcher logs OPD rows for all four)

- **Q-MPU-01 RESOLVED = flagship-first (default ratified):** en_US wave-1 series get full master
  plans (eps 1–48 detailed via existing arc plans, 49–100 outline-level); other cells stay on the
  standing 48-ep cadence until wave 2.
- **Q-MPU-02 RESOLVED = REWORK UNDER NEW CONTRACT (operator override — do NOT merge #295):**
  PR #295 stays unmerged. Its content is absorbed by this pack: **Lane 05 absorbs the 10 craft
  bibles** from branch `claude/manga-12ep-arc-authoring-egnwqf` (verify → adapt → land via Lane
  05's own PR, source-credited); **Lane 06 absorbs the 20 arc plans as rework inputs** (migrated
  into master-plan-contract-conformant artifacts, flagship-first). After BOTH lanes' signals
  exist, the dispatcher closes #295 as superseded with an evidence comment linking the landing
  SHAs. No lane merges #295 itself.
- **Q-MPU-03 RESOLVED = BOTH frames (operator override):** the US illustrated lane gets a
  book-format planning contract (chapters/page-count/art-ratio, parameterized by Lane 02) AND an
  episode/series master-plan variant for illustrated content that IS serialized (e.g.
  webtoon-style illustrated self-help). Lane 06's §US-illustrated addendum specs both and states
  the routing rule (product format decides the frame, per series_plan `format`/`master_format`).
- **Q-MPU-04 RESOLVED = one skill per role (default ratified):** editor/writer/storyboarder
  skills parameterized by per-genre checklist files — not 25 per-genre agents.

## Terminal state required

Every writing lane ends MERGED or BLOCKED (work pushed + NEXT_ACTION) — no third state. Cleanup
ledger + handoff `.md` per lane. Final audit (Lane 12) updates PROGRAM_STATE and names the honest
acceptance layer for every deliverable: research=RESEARCHED, contracts=SPECCED/CODE-WIRED,
pilot=at most **system working**. Nothing in this pack claims PROVEN-AT-BAR — that stays gated on
blind-10 judged scorecards (M6), which this pack feeds but does not satisfy.

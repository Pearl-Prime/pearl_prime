# Manga Story Bestseller Embed Audit — 2026-07-11

**Lane:** `ws_manga_story_bestseller_embed_audit_20260711`  
**Agent:** Pearl_Research  
**Acceptance layer:** research / traceability audit (not PROVEN-AT-BAR; not a product ship)  
**Audit class:** AUDIT / TRACEABILITY / DRIFT — no system “improvement” in this PR

## Executive verdict

**Manga today does NOT carry the full bestseller + subtle-embed doctrine end-to-end.**

- Genre-first wellness-in-shell is research/portfolio-authoritative (`docs/GENRE_PORTFOLIO_PLAN.md`) and only partially enforced post-hoc via manga story-engine / bestseller QC. Automated series setup builds thin genre blueprints + deterministic beat templates; production craft lives mainly in hand-authored `chapter_script_writer_handoff` YAMLs.
- Subtle self-help embedding is doctrine-true in research/specs and partially present as catalog `topic` + optional `topic_strategy_map` pinning in `story_architect` — NOT the book enrichment / story-schedule / exercise-journey chord. No fail-closed overt-teaching guard equivalent to book STORY/PIVOT craft gates for manga auto-writer output.
- Teacher-mode for books is wired (`--teacher` → enrichment + wrappers). For manga it is a forked vessel path (`mode: teacher` + `manga_mode_vessels.yaml`) that is code-reachable but NOT on the default emit path (`emit_series_setup` never passes `mode=`). `resolve_teacher_for_brand` is metadata/render identity, not doctrine embedding.
- Music-mode for books is wired (post-render manuscript overlay). For manga it is SPECCED + vessel-wired when `mode=music`, with hand-authored music pilot script on main — NOT book `music_overlay`, and NOT activated by default series emit.
- Manga story doctrine is a parallel fork, not a shared spine with `story_planner` / `enrichment_select` / `music_overlay` / `run_pipeline --pipeline-mode spine`.

**Bottom line:** research → portfolio/spec doctrine is strong; live manga runtime inherits names and optional vessels, not the book bestseller chord. Default automated path = stub/strategy beats + post-hoc gates; flagship craft = Tier-1 hand authoring.

## Live audit anchor

| Field | Value |
|--------|--------|
| Live origin/main SHA | `f7bbb0570f5a3720a8cc14cc5a49d65e1c39bf66` |
| Audit date | 2026-07-11 |
| PROGRAM_STATE last verified (doc) | `d8532d2d43874051b90201bda8b07eab5c1ce817` (ancestor of live main; ProPrime modes A/B/C/D book verification) |
| Exact workstream ownership of this artifact path | None on ACTIVE_WORKSTREAMS.tsv |
| Open-PR overlap | No open PR owns this audit. Adjacent: catalog skeletons; unrelated book PRs. |
| Singleton/authority files touched | None — audit-only under artifacts/qa/ |

### Mandated discovery report

1. live origin/main SHA: f7bbb0570f5a3720a8cc14cc5a49d65e1c39bf66
2. open-PR overlap: none for this exact audit
3. active workstream overlap: no owner of this artifact path; related active manga ws = weekly rollout / post-#478 activation / catalog reconciliation (proposed) — orthogonal
4. singleton/authority files touched: none
5. shared vs forked: FORKED — manga DAG under phoenix_v4/manga/*; book chord under phoenix_v4/planning/* + scripts/run_pipeline.py
6. teacher/music as pipeline inputs: books = real CLI inputs; manga = optional mode vessel inputs when set — default emit omits mode → vessels dormant

## Authority stack used

Coordination: PROGRAM_STATE, SESSION_UNITY_PROTOCOL, PEARL_ARCHITECT_STATE, agent_brief.txt, ACTIVE_PROJECTS.tsv, ACTIVE_WORKSTREAMS.tsv, SUBSYSTEM_AUTHORITY_MAP.tsv

Required set on live main:
- docs/MANGA_BESTSELLER_STORY_WRITING_GUIDE.md — MISSING on origin/main
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md — present
- docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md — present
- docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md — present
- specs/PHOENIX_V4_5_WRITER_SPEC.md — present
- specs/AI_MANGA_PIPELINE_SUMMARY.md — present
- docs/MANGA_IMPLEMENTATION_OUTLINE.md — present
- docs/GENRE_PORTFOLIO_PLAN.md — present
- docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md — present
- docs/specs/MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md — present
- docs/specs/MUSIC_ONBOARDING_SONG_KIT_V1_SPEC.md — present
- docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md — present
- config/manga/manga_mode_vessels.yaml — present
- config/manga/story_engines.yaml — present

Live modules: story_planner.py, enrichment_select.py, music_overlay.py, section_packet_composer.py, run_pipeline.py, run_manga_pipeline.py, emit.py, story_architect.py, writer.py, writer_stub.py, vessels.py, bestseller_gate.py, genre_engine_gate.py, check_manga_story_authored.py

## Per-domain findings

### A. Genre-story doctrine — status: partial
Research: genre shell facade; wellness interior (GENRE_PORTFOLIO_PLAN). Spec: Genre→Architect→Writer; story engines. Live: thin build_genre_blueprint; strategy banks or hardcoded beat templates; post-hoc genre_engine_gate + bestseller_gate; check_manga_story_authored is entry floor only (≥6 panels), not craft.

### B. Subtle self-help embedding — status: partial
Topic + optional resolve_topic_strategy pin. No enrichment schedule / exercise journeys. Teacher-name ban in authored gate. No fail-closed subtle-embed planner. Book path NOT used.

### C. Teacher embedding — status: partial (manga) / wired (books)
Books: --teacher wired. Manga: mode:teacher vessels code-reachable; emit.py omits mode=; resolve_teacher_for_brand is identity only.

### D. Music embedding — status: partial (manga) / wired (books)
Books: music_overlay wired. Manga: MUSIC_MODE_MANGA_V1 + vessels when mode=music; pilot script ahjan_music__rena_vale…/ep_001.yaml; default emit omits mode; zero manga callers of book music_overlay.

### E. Manga-specific integration — status: partial
Zero imports of story_planner/enrichment_select/music_overlay under manga tree. Parallel DAG. quality_profile name collision with book chord.

## Contradiction table

| # | Research (X) | Spec (Y) | Live (Z) | Status |
|---|--------------|----------|----------|--------|
| 1 | Genre-first excellent craft | Story engines + bestseller gates | Thin blueprint + templates + post-hoc gates; craft=hand-author | partial |
| 2 | Wellness never facade | Felt transmission | Topic metadata + optional strategy pin; no fail-closed | partial |
| 3 | Teacher doctrine diegetic | M4 vessels XOR | Vessels if mode set; emit omits mode | drift |
| 4 | Music via motif | MUSIC_MODE_MANGA_V1 | Vessel path + rare hand scripts; default off | partial |
| 5 | Shared bestseller overlay | Book overlay + manga sibling gate | Sibling QC only; no shared planner | contradicted |
| 6 | MANGA_BESTSELLER_STORY_WRITING_GUIDE | Referenced | File missing on origin/main | missing |
| 7 | Teaching atoms → writer | Outline aspirational | Speech atoms/vessels; not book enrichment | documented_only |
| 8 | Seven-agent live LLM writer | Pipeline summary | Stub/replay + hand-author dominant | documented_only |

## What is actually in the pipeline today
Governed manga: run_manga_pipeline, emit, story_architect, story_strategy_loader, story_engine_loader, genre_engine_gate, mode/vessels, writer/writer_stub, bestseller_gate family, check_manga_story_authored, hand-authored chapter_scripts.

Book-only: story_planner, enrichment_select, music_overlay, music_manuscript_overlay, section_packet_composer teacher/journey stack, run_pipeline four-piece chord.

Drift/weak/missing: missing writing guide; emit mode omission; craft bibles not auto-loaded; writer_stub default; PROVEN-AT-BAR unproven.

## What is only promised
Full genre-craft auto-writer; catalog-scale teacher/music diegesis via series mode; shared book enrichment inheritance; ghost writing guide; teaching-library atoms→writer; Layer-4 blind proof.

## Top blockers
1. Entrypoint disconnect from book bestseller chord
2. mode not plumbed through emit_series_setup / series_plan SSOT
3. Missing manga bestseller writing guide on main
4. No fail-closed subtle-embed / anti-lecture planner for auto scripts
5. Stub/default writer remains automated substance path
6. PROVEN-AT-BAR gap

## Next implementation lane
ws_manga_mode_emit_plumbing_20260711 — plumb mode (+ musician_id XOR teacher vessel) from series_plan → emit_series_setup → build_story_architecture_internal(mode=…) → writer handoff; CI when mode declared but vessel beats absent; land or retire MANGA_BESTSELLER_STORY_WRITING_GUIDE.md pointer. Do not claim shared enrichment until ratified bridge spec.

## Status rollup
genre-story=partial; self-help=partial; teacher=partial; music=partial; manga-integration=partial

## Local validation
git fetch + rev-parse origin/main; cat-file presence checks; zero manga imports of book planners; emit omits mode; music pilot script exists; gh pr list overlap; ACTIVE_WORKSTREAMS scan.

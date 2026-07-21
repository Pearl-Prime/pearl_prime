# RANKED_FINDINGS — Archived Sessions >30d Idea Audit (2026-07-22)
Audit of Cursor agent transcripts with **mtime before 2026-06-22** (569 sessions), plus 16 uncovered `old_chat_specs` exports and 78 older Claude memory titles.
**Not re-audited:** last-30-days sessions (Untitled 386 / `20260721_archived_session_followup`) and already-extracted session-mining specs (2026-07-18).
## Corpus summary
- Catalogued: **569** sessions (months {'2026-02': 31, '2026-03': 216, '2026-04': 152, '2026-05': 167, '2026-06': 3})
- Triage: `{'DEEP': 135, 'ALREADY_MINED': 8, 'SKIM': 332, 'SKIP': 94}`
- Curated idea rows: **50** · status `{'PARTIAL': 23, 'LIKELY_LANDED': 2, 'TRULY_MISSING': 18, 'DUPLICATE_OF_PRIOR_MINING': 5, 'OPERATOR_GATE': 2}`
- High-leverage keepers below: **35**
## Top keepers (good + still useful)
1. **I042 — Manga structural-composition MVP**  
   Status: `TRULY_MISSING` · theme `manga` · repo=5 pipeline=5  
   Source: `old_chat_specs` export_357  
   Signal: Implement the strongest parts of the Structural Composition MVP.  
   Evidence: `(no path hit)`  
   Note: CODE-WIRED vs EXECUTED-REAL
2. **I043 — Manga PassB reading-graph + spread + JLREQ SFX lettering proof**  
   Status: `TRULY_MISSING` · theme `manga` · repo=5 pipeline=5  
   Source: `old_chat_specs` export_362  
   Signal: BLOCKED** — bar packet not assembled. Doctrine is on main; implementation + proof-wave prerequisites are not.  
   Evidence: `(no path hit)`  
   Note: Export BLOCKED — bar packet not assembled
3. **I045 — Books-first leftovers: STORY seeding + 4-cell rebuild**  
   Status: `TRULY_MISSING` · theme `pipeline_gates` · repo=5 pipeline=5  
   Source: `old_chat_specs` export_366  
   Signal: Next step 1: remaining engine-keyed STORY seeding + 4-cell rebuild proof; false_alarm governance resolved; NO_BINDING-only binding calls; optional REFLECTION parse-depth  
   Evidence: `(no path hit)`  
   Note: Closeout next-step after #5530 era
4. **I001 — Author resolution wiring into assembly pipeline**  
   Status: `PARTIAL` · theme `pipeline_gates` · repo=5 pipeline=5  
   Source: [Author resolution wiring into assembly p](2431a4be-0130-4f71-a01d-8f053f615500)  
   Signal: implemented. The QA directory has 9 validators, but they cover structural integrity (plan schema, emotional curve, duplication, arc alignment, engine resolution). The narrative int  
   Evidence: `docs/;phoenix_v4/`  
   Note: Cross-check author system memory
5. **I002 — Unified personas readiness: atoms left for writing books**  
   Status: `PARTIAL` · theme `catalog_atoms` · repo=5 pipeline=5  
   Source: [Unified personas readiness: atoms left f](9ad29a26-308d-4302-9ed7-9b934922736f)  
   Signal: missing. analzye all atoms. what is left for writing team for system to be able to write books for all personas?  
   Evidence: `SOURCE_OF_TRUTH/;config/`  
   Note: Atom cohesion / coverage
6. **I025 — Atom gap analysis: cohesive flow, bridges, bestseller structure**  
   Status: `PARTIAL` · theme `catalog_atoms` · repo=5 pipeline=5  
   Source: [Atom gap analysis: cohesive flow, bridge](fc9e7c1f-8ba7-434e-b1c1-9da7aa3b0535)  
   Signal: missing bridge/transition atoms between scene→story, story→exercise, data→teaching. Recommend new atom types that would improve bestseller-grade reading experience.  
   Evidence: `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md;docs/specs/session_mining_batch_20260718/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`  
   Note: SPEC-1 + bestseller doctrine
7. **I026 — Music-mode brand integration + freebie funnel**  
   Status: `TRULY_MISSING` · theme `social_video` · repo=5 pipeline=4  
   Source: [Music-mode brand integration + freebie f](44b6d363-0f19-4fc0-b814-6ab93f3072b8)  
   Signal: Implementation MUST consume the brand_wizard YAML + musician_reflections_survey YAML to drive freebie selection (not hardcoded)  
   Evidence: `(no path hit)`  
   Note: Music-mode pack undispached
8. **I029 — Manga V2 lettering / bubble layer (audit P0-2)**  
   Status: `PARTIAL` · theme `manga` · repo=5 pipeline=5  
   Source: [Manga V2 lettering / bubble layer (audit](5fab9ed4-236f-4a37-a840-d1afccc4c8e3)  
   Signal: implementation > 1500 LOC (re-scope);  
   Evidence: `scripts/manga/`  
   Note: Lettering proof wave blocked in exports
9. **I048 — Atom cohesion chunked plan execution**  
   Status: `PARTIAL` · theme `catalog_atoms` · repo=5 pipeline=5  
   Source: `memory:project_atom_cohesion_chunked_plan`  
   Signal: --- name: project_atom_cohesion_chunked_plan description: "Atom-cohesion A–F chunked plan — fix jarring/choppy books by making atom selection adjacency-aware; dispatch order, gates  
   Evidence: `docs/specs/session_mining_batch_20260718/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`  
   Note: Pairs I025 / SPEC-1
10. **I006 — family_id enum drift silent corruption fix**  
   Status: `TRULY_MISSING` · theme `pipeline_gates` · repo=4 pipeline=5  
   Source: [family_id enum drift silent corruption f](754099c5-3f08-48ef-b54b-594e0acedaf2)  
   Signal: implement those plus runtime registry drift checks in CI, you eliminate the highest-frequency silent failure class at scale.  
   Evidence: `(no path hit)`  
   Note: Confirm dedicated CI gate
11. **I032 — Feature-knob angle_id registry join**  
   Status: `TRULY_MISSING` · theme `catalog_atoms` · repo=4 pipeline=5  
   Source: [Feature-knob angle_id registry join](59da2ac9-6a72-4a30-b1ca-59524048c83a)  
   Signal: missing angle_id raises explicit error  
   Evidence: `(no path hit)`  
   Note: PR #974 era
12. **I005 — Author signature / blueprint cover-pic system**  
   Status: `PARTIAL` · theme `covers_brand` · repo=5 pipeline=4  
   Source: [Author signature / blueprint cover-pic s](ba905820-ac1c-4ad6-babb-878522329c71)  
   Signal: implemented yet (your note says this, which is right): [AUTHOR_COVER_ART_SPEC.md](/Users/ahjan/phoenix_omega/specs/AUTHOR_COVER_ART_SPEC.md).  
   Evidence: `docs/NAMING_COVER_SYSTEM_37x14.md;docs/specs/COVER_FIVE_LAYER_UNIQUENESS_V1_SPEC.md`  
   Note: Cover five-layer spec exists; uniqueness offline in last-30d
13. **I010 — Pearl News editorial article structure / org wiring**  
   Status: `PARTIAL` · theme `pearl_news` · repo=5 pipeline=4  
   Source: [Pearl News editorial article structure /](5643f03a-ce02-4c54-91c6-c56e9072d12e)  
   Signal: missing) + WordPress env example.  
   Evidence: `docs/PEARL_NEWS_WRITER_SPEC.md;docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md`  
   Note: Sidebar later; editorial gaps may remain
14. **I033 — Manga brand×locale gap matrix (LFS pointer vs present)**  
   Status: `PARTIAL` · theme `manga` · repo=5 pipeline=4  
   Source: [Manga brand×locale gap matrix (LFS point](d914dcda-7359-4346-8ca2-81e3edbe0967)  
   Signal: IMPLEMENTATION_OUTLINE.md; config/manga/canonical_brand_list.yaml; config/manga/brand_lora_plans.yaml  
   Evidence: `docs/specs/session_mining_batch_20260718/ARTIFACTS_RETENTION_POLICY_V1_SPEC.md`  
   Note: SPEC-8 overlap
15. **I034 — Book + audiobook buying platform storefront spec**  
   Status: `TRULY_MISSING` · theme `research_tooling` · repo=5 pipeline=3  
   Source: [Book + audiobook buying platform storefr](fef9c8bd-10bc-43d3-9480-647ea7ae84a3)  
   Signal: next steps for them to use our books, to buy our books So that's gonna be Pearl Writer that has to go in and find those next step a- atoms, and where we are suggesting somebody els  
   Evidence: `(no path hit)`  
   Note: Snipcart/Stripe operator gate; platform thin
16. **I049 — Brand registry 37×14 unification completion**  
   Status: `PARTIAL` · theme `covers_brand` · repo=5 pipeline=4  
   Source: `memory:project_brand_registry_37x14_unification`  
   Signal: --- name: project_brand_registry_37x14_unification description: The brands unify to 39×14 (PR metadata: node_type: memory type: project originSessionId: 73531c5b-5b7c-48af-afc2-c59  
   Evidence: `docs/NAMING_COVER_SYSTEM_37x14.md`  
   Note: Naming cover system doc
17. **I018 — Brand media generation canonical path**  
   Status: `TRULY_MISSING` · theme `covers_brand` · repo=4 pipeline=4  
   Source: [Brand media generation canonical path](f315b072-2b32-4be9-9e36-d8d47b0d75fb)  
   Signal: not yet renderable inline.</div>  
   Evidence: `(no path hit)`  
   Note: IMG_RENDER dual path later
18. **I030 — Catalog 800 auto-generator**  
   Status: `TRULY_MISSING` · theme `catalog_atoms` · repo=4 pipeline=4  
   Source: [Catalog 800 auto-generator](2e48dda5-b26f-47c1-988f-ab0118a6fe3f)  
   Signal: recommended for the PR).  
   Evidence: `(no path hit)`  
   Note: project_800 memory
19. **I015 — Continuous deep research plane (scheduled, not one-shot)**  
   Status: `PARTIAL` · theme `research_tooling` · repo=5 pipeline=3  
   Source: [Continuous deep research plane (schedule](7654d26d-7dbb-41ee-8890-90e8c22c49ba)  
   Signal: missing real youth signals  
   Evidence: `scripts/research/research_prompt_builder.py;docs/research/PEARL_RESEARCH_PROMPT_GENERATION_LAYER.md`  
   Note: Builder exists; continuous plane missing
20. **I003 — Teacher-mode strict + fallback plan completion**  
   Status: `PARTIAL` · theme `pipeline_gates` · repo=4 pipeline=4  
   Source: [Teacher-mode strict + fallback plan comp](0acf3b70-d113-421a-a504-d0267a661d4f)  
   Signal: Missing STORY | Hard fail |  
   Evidence: `teachers/`  
   Note: Teacher onboarding packs later
21. **I007 — Catalog knob usage-percent analyzer**  
   Status: `PARTIAL` · theme `research_tooling` · repo=4 pipeline=4  
   Source: [Catalog knob usage-percent analyzer](f42cad21-d24d-469a-b9ff-84f9a1ac5103)  
   Signal: @docs/DOCS_INDEX.md look at the catalog and book planner for english. create a .py analyzer to report the useage percert of each knob like: book format (include v4, or pearl, arc,   
   Evidence: `scripts/audit/build_pipeline_matrix.py`  
   Note: Pipeline matrix exists; usage-% analyzer thin
22. **I009 — Pearl Prime book-template bridge into freebies/immersion**  
   Status: `PARTIAL` · theme `pipeline_gates` · repo=4 pipeline=4  
   Source: [Pearl Prime book-template bridge into fr](61d46e39-b8db-4387-a443-2e308be81948)  
   Signal: implemented in `teaching_bridges.py` and documented. Wiring a TEACHING slot type into the render loop (when you add it) will use this pool via `select_teaching_wrapper` or `render_  
   Evidence: `docs/agent_prompt_packs/20260715_old_chat_closure_audit/06_Pearl_Brand_freebie_harbor_closeout.md`  
   Note: Freebie harbor pack
23. **I019 — Brand-wizard-app UX continuation**  
   Status: `TRULY_MISSING` · theme `covers_brand` · repo=4 pipeline=3  
   Source: [Brand-wizard-app UX continuation](9ca9742d-eff0-4eb0-a554-98df63884ea5)  
   Signal: Implement party mode feature  
   Evidence: `(no path hit)`  
   Note: Last-30d offline
24. **I020 — Video pipeline handoff / series assembly resume**  
   Status: `PARTIAL` · theme `social_video` · repo=4 pipeline=4  
   Source: [Video pipeline handoff / series assembly](59d869bd-efca-4c48-9aec-3d7ed5bdeff8)  
   Signal: missing from this checkout; multilayer render currently falls back; caption wrapping and meditation/music wiring remain incomplete  
   Evidence: `artifacts/audio/presenter/`  
   Note: Presenter audio exists
25. **I021 — 13 teacher YouTube video banks assembly**  
   Status: `PARTIAL` · theme `social_video` · repo=4 pipeline=4  
   Source: [13 teacher YouTube video banks assembly](f4ec4722-cc2d-48b0-96e8-c9095ad7cd75)  
   Signal: Here's your paste-ready prompt to generate all 13 teacher YouTube video banks and assemble the videos: AGENT: Pearl_Video — YouTube Teacher Video Production (13 Teachers × 20 Image  
   Evidence: `teachers/`  
   Note: Partial likely
26. **I023 — CJK teacher topic-pack overlays + per-language system prompts**  
   Status: `PARTIAL` · theme `translation` · repo=4 pipeline=4  
   Source: [CJK teacher topic-pack overlays + per-la](7b85b693-d534-4b47-953c-09442482e422)  
   Signal: next steps / concrete action  
   Evidence: `config/localization/`  
   Note: CJK6 doctrine evolved
27. **I028 — Manga V2 character individuation prompt-builder**  
   Status: `PARTIAL` · theme `manga` · repo=4 pipeline=4  
   Source: [Manga V2 character individuation prompt-](9762773d-5c66-4089-a051-887ef97428c9)  
   Signal: ROLE: Pearl_Dev — V2 Phase C deep prompt-builder integration SESSION_TYPE: pure code; extends scripts/manga/character_individuation/ prompt_builder.py to consume the full research   
   Evidence: `scripts/manga/character_individuation`  
   Note: Dir exists; completeness unknown
28. **I031 — Localization quality contracts CI enforcement depth**  
   Status: `PARTIAL` · theme `translation` · repo=4 pipeline=4  
   Source: [Localization quality contracts CI enforc](643f74db-c0a7-47f8-a054-593a0bbf90e6)  
   Signal: not yet usable for commit/PR.  
   Evidence: `config/localization/quality_contracts/`  
   Note: Contracts folder exists
29. **I041 — Waystream cover durable delta-queue**  
   Status: `PARTIAL` · theme `covers_brand` · repo=4 pipeline=4  
   Source: `old_chat_specs` export_355  
   Signal: missing/invalid work unless --force-rerender is explicitly passed  
   Evidence: `docs/NAMING_COVER_SYSTEM_37x14.md`  
   Note: Authority docs; delta lane thin
30. **I013 — EI V2 hybrid system completeness**  
   Status: `TRULY_MISSING` · theme `pipeline_gates` · repo=3 pipeline=4  
   Source: [EI V2 hybrid system completeness](2c37ac68-b3f3-4366-b362-d8876dea9752)  
   Signal: TODOs, (5) any imports that might fail.  
   Evidence: `(no path hit)`  
   Note: May be superseded
31. **I017 — Video thumbnail contract (thumb.jpg beside video.mp4)**  
   Status: `TRULY_MISSING` · theme `social_video` · repo=3 pipeline=4  
   Source: [Video thumbnail contract (thumb.jpg besi](e376fbc9-8821-4b07-892e-d40d1c4ee80a)  
   Signal: missing; lines 128–135, 163–166, 224–228).  
   Evidence: `(no path hit)`  
   Note: Thumb contract enforcement
32. **I012 — Full-repo core-function operator UI / system status console**  
   Status: `PARTIAL` · theme `research_tooling` · repo=4 pipeline=3  
   Source: [Full-repo core-function operator UI / sy](aba05c79-3746-4a0e-837b-5586d9bb6f86)  
   Signal: Implemented and pushed to `main` (commit `8815782e`):  
   Evidence: `PhoenixControl/`  
   Note: PhoenixControl restored; 100% aspirational
33. **I014 — V4 freebies + immersion ecosystem completion**  
   Status: `PARTIAL` · theme `social_video` · repo=4 pipeline=3  
   Source: [V4 freebies + immersion ecosystem comple](6b3eac83-d16e-41b0-86b3-61a827bcea0f)  
   Signal: implemented and verified:  
   Evidence: `docs/agent_prompt_packs/20260715_old_chat_closure_audit/06_Pearl_Brand_freebie_harbor_closeout.md`  
   Note: Freebie harbor pack
34. **I038 — Pearl News per-brand mapping leftover**  
   Status: `PARTIAL` · theme `pearl_news` · repo=4 pipeline=3  
   Source: [Pearl News per-brand mapping leftover](eac25063-e75d-4893-b315-f984e0b14427)  
   Signal: You are Pearl_Dev. Complete the Pearl_News per-brand mapping that was flagged as "not yet per-brand mapped" in the OPD-119/121 PR (#1251) closeout. This finishes the brand admin we  
   Evidence: `docs/PEARL_NEWS_WRITER_SPEC.md`  
   Note: OPD-119/121 leftover
35. **I047 — Anti-reinvention architecture enforcement**  
   Status: `PARTIAL` · theme `governance_ci` · repo=4 pipeline=3  
   Source: `memory:project_anti_reinvention_architecture`  
   Signal: --- name: project-anti-reinvention-architecture description: 3-layer anti-reinvention system (router principle 9 + Canonical Artifacts Registry + reinvention CI guard) to stop agen  
   Evidence: `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`  
   Note: Authority map exists
## By theme (keepers)
- `pipeline_gates`: 6
- `manga`: 5
- `catalog_atoms`: 5
- `social_video`: 5
- `covers_brand`: 5
- `research_tooling`: 4
- `pearl_news`: 2
- `translation`: 2
- `governance_ci`: 1
## Operator gates (not agent-missed)
1. **I044 — Cloud/Codespaces substrate fanout for manga**  
   Status: `OPERATOR_GATE` · theme `governance_ci` · repo=3 pipeline=3  
   Source: `old_chat_specs` export_361  
   Signal: blocked; landing the blocked closeout on main for a durable resume surface.  
   Evidence: `(no path hit)`  
   Note: OPERATOR_GATE
2. **I039 — Metricool X/Twitter channel decision ($5 add-on)**  
   Status: `OPERATOR_GATE` · theme `social_video` · repo=3 pipeline=2  
   Source: `old_chat_specs` export_303  
   Signal: Facebook, Instagram, Threads, LinkedIn, TikTok, YouTube, Pinterest, BlueSky. So it does everything except for X, which anyways, five extra dollars on Metricool, so I don't know if   
   Evidence: `(no path hit)`  
   Note: OPERATOR_GATE
## Interesting but lower priority (parked)
1. `I022` TikTok body-awareness shot plans for teachers — `TRULY_MISSING` (r3/p3)
2. `I027` Musician survey → music mode implementation — `TRULY_MISSING` (r3/p3)
3. `I036` RunComfy cost-alert widget on brand_admin — `TRULY_MISSING` (r3/p3)
4. `I046` ProPrime modes 100% merge wave — `TRULY_MISSING` (r3/p3)
5. `I037` US marketing plan consolidation — `TRULY_MISSING` (r3/p2)
6. `I035` Church/brand/payment plans integration — `TRULY_MISSING` (r2/p2)
## Do not reopen
These are already covered by prior mining packs/specs, or scaffolding is already on disk as LIKELY_LANDED:
- `I011` AI-assisted therapeutic book assembly beyond metadata — `DUPLICATE_OF_PRIOR_MINING` (SPEC-4 merge)
- `I024` Iterative catalog quality refinement loop — `DUPLICATE_OF_PRIOR_MINING` (SPEC-4 merge)
- `I008` DOCS_INDEX completeness / V4 wiring gate — `DUPLICATE_OF_PRIOR_MINING` (session_mining RN-9)
- `I016` Marketing system wiring for monetization completeness — `DUPLICATE_OF_PRIOR_MINING` (SPEC-6)
- `I004` English catalog creation without assembling books — `LIKELY_LANDED` (Catalog evolved since Feb)
- `I040` Catalog PLAN-completeness audit 14×39 — `DUPLICATE_OF_PRIOR_MINING` (Last-30d PLAN green offline)
- `I050` Devotion Path catalog readiness (flagged not ready) — `LIKELY_LANDED` (Dashboards ≠ readiness)
## Highest-leverage next actions (operator pick)
1. **Manga bar / lettering / structural composition** — I042, I043, I029 (exports already marked BLOCKED; do not fake EXECUTED-REAL).
2. **Books-first STORY seeding + 4-cell rebuild** — I045 (explicit leftover from export 366 closeout).
3. **Music-mode freebie funnel** — I026 (pack may already exist undispached; land rather than re-spec).
4. **Buying platform / storefront spec** — I034 (distinct from Snipcart key operator gate).
5. **Continuous research plane** — I015 (builder exists; schedule/cadence does not).
6. **Atom cohesion / gap / bestseller structure** — I025, I048 (merge into SPEC-1 lane; do not fork).
7. **Cover five-layer / 37×14 registry** — I005, I049 (spec on disk; uniqueness still a live complaint in last-30d).
## Artifacts
- `SESSION_CATALOG.tsv`
- `IDEA_BACKLOG.tsv` / `IDEA_BACKLOG_ENRICHED.json`
- `IDEA_BACKLOG_RAW.jsonl` (machine signals from DEEP sessions)
- `DEDUP_LEDGER.tsv`
- `SECONDARY_PASS.json`
- `WAVE_PROGRESS.md`
- Scanner: `scripts/audit/archived_session_gt30d_scanner.py`
- Extractor: `scripts/audit/archived_session_gt30d_deep_extract.py`
- Finalize: `scripts/audit/archived_session_gt30d_finalize.py`

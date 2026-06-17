# Phoenix Omega — Total Repo Audit Summary

**Date:** 2026-06-17
**Author:** Pearl_Architect (read-only audit; only writes = these 5 artifacts + a do-NOT-merge PR)
**Baseline:** `origin/main` @ `29c3fd76bc21f456953f7232df7272e436c4b474`
**Artifacts in this bundle:**
1. `REPO_FUNCTION_MAP.md` — 22 subsystems + cross-cutting, with status + gaps
2. `DOCS_TIED_TO_FUNCTION.tsv` — all 518 tracked `.md`, classified
3. `DELETION_CANDIDATES.tsv` — proposal-only, ranked by confidence, with PROTECTED list
4. `NEEDS_CODING.tsv` — 24 spec'd-but-not-built / known-broken items, prioritized
5. `AUDIT_SUMMARY.md` — this file

---

## The single biggest source of agent confusion (headline finding)

**Commit `30bd4dd6af` (2026-05-29) touched 57,017 files** — a mass re-import/normalization that reset `git log` last-commit dates for **468 of 518** tracked markdown files to a single day. Any agent using `git log <doc>` to judge "is this doc current?" gets a **false 2026-05-29 signal** for ~90% of docs. This is why stale 2026-04 audits, dead session handoffs, and superseded specs *look* recent.

**Rule for all agents going forward:** judge doc currency by (a) membership in the canonical authority set — DOCS_INDEX + PEARL_ARCHITECT_STATE + SUBSYSTEM_AUTHORITY_MAP + CANONICAL_ARTIFACTS_REGISTRY + ACTIVE_WORKSTREAMS + CLAUDE.md/skills — (b) in-file `Last updated` / SUPERSEDES headers, and (c) code/CI references. NOT by `git log` date. This audit did exactly that.

**Secondary confusion source:** `docs/DOCS_INDEX.md` is itself dated 2026-05-29 and indexes ~80% of pre-May surface and ~0% of the newest specs (storefront V1, devotion-path reconciliation, video frame-selector, the 1000-book program, brand-registry 37×14). DOCS_INDEX is still the best map but is **trailing the frontier by ~3 weeks** and should be refreshed.

---

## Headline counts

| Metric | Count |
|---|---:|
| Tracked `.md` files audited (docs/ + specs/ + root) | **518** |
| — CURRENT | 347 |
| — STALE | 168 |
| — SUPERSEDED (explicit pair) | 3 |
| Governed subsystems (SUBSYSTEM_AUTHORITY_MAP) | 22 |
| — done / done-but-high-drift | 5–6 |
| — partial | 14 |
| — not-started (proposed/backlog) | 3 |
| `.github/workflows/` | 88 |
| Active workstream rows (ACTIVE_WORKSTREAMS.tsv) | 257 |
| Open PRs (many DO-NOT-MERGE proposals) | ~60 |
| Deletion candidates — HIGH confidence | 7 rows |
| Deletion candidates — MED confidence | 10 rows |
| Deletion candidates — LOW confidence | 9 rows (mostly multi-file dated-historical) |
| NEEDS_CODING — P0 / P1 / P2 / P3 | 4 / 6 / 7 / 7 |

---

## Highest-confidence deletions (operator review — nothing deleted by this audit)

These 7 are HIGH confidence: zero code/CI references, verified by `git grep`.

1. `.pr-body-governance-100.md` — stray PR-body scratch file at root.
2. `specs/PHOENIX_OMEGA_V4_COMPLETE_SPEC (1).md` — a `(1)`-dup of an **already-archived superseded spec**, left in the live `specs/` dir.
3. `phoenix_catalog_1008.json`, `phoenix_catalog_v4_1008.json`, `us_catalog_sample.json` — root legacy catalog exports, superseded by `config/source_of_truth/`.
4. `bold modern.jpg`, `premium.jpg` — root stray scratch images, unreferenced.

**MED-confidence next tier (verify the one-line caveat first):** root `phoenix_title_engine.py` + `_v3.py` (v4 is the canonical imported one — fix the `system_registry.yaml` glob first), `revenue_dashboard.jsx`, `regen_files.py`, the nested `salvage/.../session_2026_03_28_worktree_snapshot/` self-duplicate, the three `talp/.../* (1).md` macOS dup files, and the raw-intake dirs `de_chats_to_analyze/` + `old_chats/` (ask_owner).

**LOW-confidence bulk (historical, low value but possibly worth lineage):** the 8 dated `docs/SESSION_HANDOFF_2026_04_*.md`, the 5 `docs/FULL_REPO_*_2026-04-26.md` predecessor-audit docs (superseded by this audit + the 2026-06-09 health audit), and dated manga-catalog/launch/validation reports now superseded by the live SSOT.

**PROTECTED — must NOT be deleted (called out to prevent accidents):** `Qwen/`, `Qwen-Agent/` (submodules); `.claude/worktrees/**` (committed to main, ~110GB, disk-poison + mass-deletion hazard); `brand_admin.html` (still wired; its retirement PR #1628 is OPEN); `brand-wizard-app/node_modules/` (6,984 tracked files; >50-file deletion needs owner approval); `archive/` + `deprecated/` (intentional reference dirs with README markers); `talp/` (live content source).

---

## Biggest not-done gaps (the coding frontier)

**P0 — load-bearing, blocks the catalog $-maker:**
- **register_gate/ship_readiness not wired into `run_pipeline.py`** (PR #1536 open). The spine default flipped but the quality gate is still a separate call.
- **Production books HARD_FAIL register + word-budget** (9/9 in the pilot). Root cause is **composer scaffolding-repetition** (verbatim cross-book transitions, unfilled doctrine-prefix tails, HOOK stubs) — NOT atom scarcity. This is *the* bestseller frontier (#1589/#1590; #1601 cleared one HARD_FAIL).
- **Atom cohesion** — atoms are slotted with no adjacency model → jarring/choppy books. Chunked A–F plan; A+E dispatched, B/C/D/F gated.
- **CJK localizer truncation bug** — `translate_atoms_to_locale.py` drops `##` variants >8000 chars across all CJK locales, likely contaminating prior sprints (PR #1658 open).

**P1 — program-critical:** Manga V2 Phases C/D/E (register/genre LoRAs, anatomical, re-render); ep_002 V5.1 + CJK manga LoRA/score drain; video `assemble_mixed.py` (PR #1663) + the stranded local-only 3-stage best-video method; Pearl Prime ONE-PATH phases 1–4 + dwell-beat gate wiring; devotion_path re-point (blocked on operator A′-shape pick + composer F-COHERENCE co-gate).

**P2/P3 — productionization:** EI v2 is still an advisory SCORER, not the spec'd synthesis engine (no GA, not wired to planners — #1516/#1578); music-mode (~38 dormant brands, live route + first-real-artist seed missing); storefront is mockups not a live store; brand-admin v2 director-screen data is PLACEHOLDER; audiobook duration labels are hand-set not derived (spec exists, not consumed); podcast/music-companions/sangha/recommender are proposed-or-absent.

**Structural reality check:** Everything *customer-facing* — storefront, brand-admin director data, music live route, video assembler — is mockup/scaffold-stage. The two load-bearing engines (core_pipeline, manga) are `partial` with concrete blocking gaps. "Done" subsystems are the plumbing (integrations, naming, CI, pearl_news).

---

## Recommended cleanup / coding sequence

**Cleanup (low-risk, do first — unblocks doc trust):**
1. Operator approves the 7 HIGH deletions (all zero-ref scratch/dup files). Single small PR.
2. **Refresh `docs/DOCS_INDEX.md`** to index the post-May frontier (storefront V1, devotion-path, video frame-selector, 1000-book program, brand-registry 37×14) and bump `Last updated`. This is the highest-leverage cleanup — it's the map every agent reads.
3. Mark the 3 SUPERSEDED specs in-file (ANGLE_REGISTRY V1, Chinese Writer v1.0/v2.0) with a one-line SUPERSEDED-BY header so future agents don't re-read them. (V1 already declares this; v1.0/v2.0 do not.)
4. After PR #1628 merges, the `brand_admin.html` cleanup becomes safe.
5. Defer the LOW-confidence dated-historical bulk to a batched operator-reviewed sweep (or relocate under `archive/`).

**Coding (gate each on the prior):**
1. **P0 register_gate wire (#1536)** — merge first; it's the gate everything else is measured against.
2. **P0 composer scaffolding-repetition fix** (#1589/#1590 frontier) — the actual bestseller blocker.
3. **P0 localizer truncation fix (#1658)** — stops further CJK contamination; cheap, isolated.
4. **P0 atom cohesion** B/C/D/F (after schema A lands) — fixes choppiness, the operator's recurring craft concern, alongside dwell-beat.
5. **P1 video assemble_mixed (#1663)** + **manga V2 C/D/E** in parallel (different owners).
6. **P2 productionization** (storefront, brand-admin v2 real data, EI engine, music live route) once the P0 quality floor is green.

**Serialization caution:** PRs that append to `PEARL_ARCHITECT_STATE.md` must be serialized (hot governance file); new-file + cap-gated PRs ride parallel. Self-merge clean class needs only the "Verify governance" required check (Core/Release red on push does not block — verify test health manually).

---

## What this audit did NOT reach (time-box honesty)

- **Per-file content read of all 518 docs** — I classified by authority-set membership + filename pattern + first-heading purpose + SUPERSEDES-marker grep, NOT by reading every body. The 168 STALE and 347 CURRENT verdicts are high-confidence in aggregate but individual LOW-confidence borderline docs (esp. the 77 `misc`-bucketed and the `docs/research/`, `docs/email_sequences/` trees) were not body-verified one-by-one.
- **Non-`.md` config/code drift** — I mapped code *entry points* per subsystem and verified deletion-candidate references, but did not audit every `config/*.yaml` for staleness/duplication (e.g. duplicate CJK constants in two sites, noted in memory, not re-verified here).
- **`artifacts/` tree beyond coordination/audit** — `artifacts/` has hundreds of generated outputs; I sampled (research, qa, analysis, weekly_packages) but did not classify it exhaustively. Generated artifacts are mostly disposable-by-design.
- **`old_chat_specs/` (167 files)** — flagged historically as ask_owner; not individually triaged here.
- **Test reality** — I confirmed `pytest.ini testpaths=tests` and the parallel test-root question, but did not run the suite or audit per-test currency (covered by prior `q9_test_reality.md`).
- **Open-PR mergeability sweep** — I read titles/states for the ~15 PRs cited in NEEDS_CODING but did not triage all ~60 open PRs for conflict/staleness (prior `PR_TRIAGE_REPORT` + babysit-prs lane owns that).

**Prior art this supersedes / builds on:** `artifacts/audit/q1–q11*` (2026-04-29, Pearl_GitHub) and `artifacts/coordination/human_team_structure_20260606/SUBSYSTEM_HEALTH_AUDIT.md` (2026-06-09). This audit refreshes their subsystem-status and cruft findings to the current `origin/main` and adds the doc-currency map + deletion-candidate verification the older passes lacked.

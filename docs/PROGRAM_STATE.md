# Program State — Single Source of Truth

**LAST VERIFIED:** 2026-07-11 @ `origin/main` `4c896efb8ab0038e73906841ab82bb19c47b9eb3` (post-#5525 books-first SSOT refresh; #5490 spine lock + #5501 ja-JP teacher-bank + #5525 workstream closeout already on `main`; tip includes #5526 manga closeout docs)

> **RULE:** Verify against `origin/main`, never git date or the working tree (shared-tree branch-churn shows
> other-branch/stale state). This is the entry point — if another doc disagrees with this, this wins or that doc is stale.

> **GLOSSARY (read this — it has caused repeated confusion):**
> **Listing** = catalog metadata (title/subtitle/description/cover/dashboard — what a book is *about*).
> **EPUB** = the actual readable, sellable file a customer downloads.
> We have **~1,519 listings** and **1 catalog EPUB assembled** (first Waystream EPUB, #1923 — see Production-Gate).
> "Books" in most docs means *listings* — do NOT read it as "readable/sellable books."

## Current Status by Track

### Flagship book (gen_z_professionals × anxiety) — PROVEN-AT-BAR
**OPD-20260707-FLAGSHIP-L4** — operator Layer-4 blind-read **APPROVED** the full 12-chapter book
(build 9, `extended_book_2h`, seed `flagship_phase2_layer6`, 21,012w). First PROVEN-AT-BAR book in
program history. Both goldens now live + byte-frozen:
- **Golden #1 (ch1):** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt` — CI-enforced.
- **Golden #2 (full book):** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt` (sha `fd0c49ec26…`) —
  ratified this cycle; `check_flagship_book_parity.py --snapshot full` flipped DORMANT→live/required.
- **Required gates (approved):** exercise five-layer integrity + pick diversity + F7 precision fix —
  wired into Drift detectors + readiness gates 30/31. Ch1 parity stays byte-identical.
- **Door-back (rider):** this cell is `extended_book_2h` by deliberate decision (Option A
  mass-architecture retarget). The `deep_book_6h` variant is retired for **this cell only**
  (xfail scoped to gen_z×anxiety×6h; the 40k floor stays live for every other cell/format). If a 6h
  flagship is ever commissioned here it is a **content program** (more chapters/objects) and
  **per-format exercise picks** is the designed mechanism — the xfail XPASSes and flags for un-retiring.

### en_US Listings
- **Status:** **DONE**
- **Details:** **1,519 LISTINGS** (storefront metadata — NOT readable EPUBs) across 26 brands + Waystream (800),
  on `main` (PR #1801–#1839). **Total counts:** 2,187 `book_plans_en_us` + 28 brand dashboards.
- **Wave 2026-06-25:** +462 **plannable** books from arc seeding (educators 1→11 arcs, nyc_executives 4→13 arcs;
  PR #1913). **Total plannable: 12,138.** ⚠ "Buildable" here = *arc + listing exist*, NOT spine-buildable: a 4-cell
  rebuild (#1922) shows these educators/nyc_executives cells still **fail tuple-viability preflight** (see
  Production-Gate caveat) — they are not yet renderable EPUBs.

### Waystream titles / cover↔title
- **Status:** **DONE (deduped + hard-gated on main)**
- **Details:** Waystream is **800 distinct titles / 800 distinct subtitles / 800 distinct (title,subtitle) pairs** on
  `main` (verified from `config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml` → catalog CSV/JSON →
  covers). The previously-stranded dedup landed; the prior "186/800" figure was stale SSOT carryover. A **hard-gate**
  now blocks regression: `scripts/ci/check_waystream_catalog_uniqueness.py` (asserts 800 distinct titles + subtitles +
  pairs against the plan SSOT, with a dry-run achievability path for template-only PRs) is wired as **gate #20** in
  `scripts/run_production_readiness_gates.py`. **Covers are 100% resynced** to current titles — verified by
  `scripts/publish/waystream_covers/verify_resync.py` (`plans=800 csv=800 covers=800 dashboard=800`, 0 structural
  errors, `--ocr` confirms cover text matches title); covers are gitignored local artifacts (slug-keyed, two-stage
  PIL-over-FLUX), not committed. Localization can inherit clean titles.

### Production-Gate / Real-EPUBs
- **Status:** **FIRST EPUB SHIPPED — durable on `main` (1 EPUB); validated brand generalizes across 4 cells**
- **Details:** Book assembly is **deterministic atom-composition** (no LLM at build; thin pools must raise
  `InsufficientVariantsError` → fix by adding atoms, never LLM-expand — verify `pearl_writer_expand.py` is NOT on the
  spine/production path). ✅ **F1/F4 + F2/F7 precision all on `main`** via PR #1919 (`ae4991bd3a`). **First gate-passing
  Waystream EPUB SHIPPED** (PR #1923, `4e6320b19c`): `corporate_managers × burnout × overwhelm`, register **PASS**,
  ei_v2 0.62, 13,759 words, 1.7 MB → `artifacts/epubs/way_stream_sanctuary/`. **3 generalization cells**
  (anxiety/false_alarm, boundaries/shame, boundaries/comparison) all register-PASS, ei_v2 0.62–0.64 — corporate_managers
  scales with **zero engine work** (loop spine CLI over the F006 arc matrix + `build_epub.py`).
  **1 catalog EPUB assembled** (was 0).
- ⚠ **Thin-persona caveat (the next lane):** **canonical atom repair MERGED** (#5489, 2026-07-10) — educators/nyc
  slot-keyed gaps partially closed. **#5530 (2026-07-11) closed one more downstream blocker**: `educators ×
  imposter_syndrome` full spine render was still hard-failing with `EnrichmentGapError` on `REFLECTION` (ch7) even
  after #5489 — root cause was **not** pool thinness but a parser quirk in `registry_resolver._parse_canonical_txt`
  (single-delimiter atom blocks silently parse to **zero** real atoms; header count is not a reliable depth proxy for
  this file family — the same silent-drop pattern is likely present in other REFLECTION pools across personas/topics,
  **not yet audited catalog-wide**, flagged as a residual finding). Fixed for this one cell only (15 new atoms in the
  verified two-delimiter shape); also removed a stale `false_alarm`/`imposter_syndrome` contradiction in
  `topic_engine_bindings.yaml` (`forbidden_engines` had it, `allowed_engines` already had it too — `allowed_engines`
  is the side the gate reads and the side #5489's shipped content already assumed). Full production spine proof:
  `artifacts/qa/thin_persona_buildability_2026-07-11/`. Remaining blockers before spine-buildable EPUBs at catalog
  scale: **engine-keyed** STORY pools (`atoms/<p>/<t>/<engine>/CANONICAL.txt`) for the rest of the thin-persona cells;
  4-cell rebuild (#1922 pattern) must re-run to confirm tuple-viability PASS; `nyc × anxiety/false_alarm` may still
  need **one band-1 STORY atom**; a catalog-wide REFLECTION-pool parse audit (the #5530 finding) is a new, separate,
  not-yet-scoped lane. Next = engine-keyed STORY-pool seeding (≥12 banded variants/cell) + Waystream-scale EPUB wave.
- **Wave 2026-06-25 (teacher-bank unblock):** 12 teachers now have `TEACHER_DOCTRINE` atoms (PR #1914) — all 26
  brands unblocked from the `library_34` fallback. 29 `CANONICAL.txt` files backfilled for educators + nyc_executives
  thin slots (PR #1915); 69/69 tests pass.
- **Infra gaps RESOLVED (#1924, `68163beab1`):** `sai_ma` `positioning_profile` was a **dangling ref** — added the
  `devotional_companion` profile to `author_positioning_profiles.yaml`. `kenjin` added to
  `config/catalog_planning/teacher_persona_matrix.yaml` (mirrors joshin's guardrails). **Q-KENJIN-01 OPEN:** the matrix
  has no `active`/`tier` field, so kenjin is a first-class entry = active-by-presence — **operator to confirm**.

### GHL marketing feed
- **Status:** **LIVE** — **first paid EPUB attached** (PR **#1947**, `89a11d5387`, 2026-06-26)
- **Details:** `marketing_feed.json` published on brand-admin Pages (public HTTPS) (#1866/#1867/#1875/#1882); R2
  provisioned; 15-topic integration; all 15 funnel landings → GHL capture. Design: paid items gate on **real attached
  asset** (`pending_asset` until then), free items on **asset-exists**; **free-content-first** — paid auto-promotes on
  attach. Funnel is live on free content + listings. **First paid attach:** Waystream
  `corporate_managers × burnout × overwhelm` EPUB in `brand_deliveries/way_stream_sanctuary.json` week 2026-W26
  (`way_stream_sanctuary__default_teacher__corporate_managers__burnout__overwhelm.epub`, R2-backed download URL) per
  #1947 — satisfies the GHL paid-slot attach row (OPD-20260630-002 / Q-DRIFT-02).

### Localization
- **Status:** **IN PROGRESS (pilot execution on `main`; not catalog-scale)** — Waystream titles are distinct + hard-gated
  on `main` (see above). **14-locale translation source pack — MERGED** (#5480, 2026-07-09). **July 10 execution wave
  landed on `main`:** ja-JP / zh-TW / zh-CN Stage-1 pilots (#5496, #5499, #5500), non-CJK Wave 1 pt-BR + es-US (#5495),
  ko-KR Stage-1 gen_z×anxiety slice (#5504), translation CI depth fix + banned-key closeout (#5497, #5498), overthinking
  stub prose + locale retranslations (#5503, #5507), parse-sweep stub gate (#5508). Live bestseller-atom coverage (post
  #5497 depth fix): ja-JP ~84%, zh-TW ~96%, zh-CN ~43%, ko-KR ~6% — **pilot cells only**; zero locale-native sellable
  Pearl Prime catalog EPUBs at scale. **#5501 ja-JP teacher-bank MERGED** (`45e511ab963b070de82ec84d53386521e67c2194`, 2026-07-10). **Not started
  at catalog scale:** Phase B–D locale waves, localized EPUB assembly, storefront Phase A smoke with real downloads.

### Manga (all locales)
- **Status:** **VISION-CERTIFIED 2026-07-03 — one series end-to-end real; scaffold everywhere else; July 10 mecha native bank + honest proof lane MERGED on `main`**
- **Details:** R1–R8 conformance: R1 30% / R2 45% / R3 25% / R4 8% / R5 34% / R6 40% / R7 5% / R8 35%
  (six-layer taxonomy, adversarially refuted; authority: `artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-03.md`
  + `artifacts/qa/manga_vision_conformance_20260703.tsv`). Grid: 1,345 series plans across 5 locales
  (1,344 titled — title-blank prior REFUTED), 8 registry locales at zero; 16 authored scripts; render-real on main =
  the April "alarm is lying" tree only (386 files, 212.8MB; sleep/somatic TSVs reference box-side files absent from
  main). Deterministic bank-assembly lane LANDED (`scripts/manga/assemble_from_bank.py` + manifest schema + 6-panel
  demo strip from real L0/L2 bank + INTERIM sprites, provenance-labeled). Roadmap to 100%:
  `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` (M1 enforcement rails → M2 locale allocations →
  M3 stories-first waves → M4 vessel wiring → M5 banks/GPU → M6 blind-10 pro-bar → M7 locale rollout).
  Supersedes `docs/MANGA_RECOVERY_AUDIT.md` as current state. Pearl Star unreachable during cert (box-side
  UNVERIFIED); GPU stays CJK-priority (OPD-20260629-003).
- **July 9 merge wave (production truth on `main` only — do not conflate with local-only renders):**
  - **Stillness ep_001 HR-U16 continuity + room-capable L2 wiring — MERGED** (#5428, `c6a0622c64ea52e4111fbb78d4484fd6b9761368`).
    Room-capable L2 manifest wiring for `ep001_008` / `ep001_013` is on `main`. Authority:
    `artifacts/qa/MANGA_STILLNESS_HR_U16_REPAIR_CLOSEOUT_2026-07-09.md`. Prior blocked proof packet
    (`MANGA_STILLNESS_RULES_PROOF_PACKET_CLOSEOUT_2026-07-09.md`) is superseded provenance only.
  - **Mecha L0 composition sidecars + render-ledger reconcile — MERGED** (#5419, `9dd7a5f986d05f3cb2989c9f680f402640e2d53c`).
    L0 sidecars + ledger wiring are on `main`.
  - **Mecha native L2/L3 dispatch wiring + seated_cockpit REAL — MERGED** (#5482, `f7eac13bade7a4e62f1b1138a7200c12c144f38f`).
    `resolve_tradition_genre` / `prompt_authority.py` / crossgenre enqueue / render-request ledger / blob gate are on
    `main`. Native REAL `L2/seated_cockpit.png` is on `main` (LFS).
  - **Mecha native L2/L3 completion + human-readability proof — MERGED** (#5486, `06a15f29eb217a51ee90f658375b2a4df0b847b5`).
    Blob-gate PASS native assets on `main`: `L2/threshold_stand`, `L3/glove_pad`, `L3/telemetry_panel` + composition
    sidecars. Native-only `ep_001_from_continuity.yaml` + `assembled/ep_001_human_readability_proof/` with planning +
    chapter validators PASS (acceptance layer: **system working**; not PROVEN-AT-BAR). Authority:
    `artifacts/qa/MANGA_MECHA_HUMAN_READABILITY_PROOF_CLOSEOUT_2026-07-10.md`. July 9 blocker/repair audits carry
    superseded banners for stale L0-sidecar / zero-L2 claims.
  - **Manga prompt-builder v3 + blob gate v2 + Qwen mecha layered pilot — MERGED 2026-07-10** (ws
    `ws_manga_prompt_builder_v3_20260710`). `config/manga/genre_prompt_cookbook.yaml` (26 genres from research #5488),
    Qwen-primary `prompt_authority.py`, stipple blob heuristic, `t2i_qwen_image` worker implemented. Honest pilot:
    `artifacts/qa/manga_layered_visual_proof_2026-07-10/mecha_master_wu_pilot/composite.png` (EXECUTED-REAL; not
    PROVEN-AT-BAR). Prior strip/seated_cockpit stipple-blob “strongest proof” claims superseded.
  - **Human-readability rules artifact — MERGED earlier 2026-07-09** (#5323; ws `ws_manga_human_readability_rules_20260709`
    completed). Implementation closeout remains local-only until its lane merges.
- **Next manga blocker (post-wave):** stillness post-merge proof re-run (local-only artifacts must not be reported as
  landed). Mecha next step is operator blind-read / PROVEN-AT-BAR — v3 pilot is the current honest layered proof surface.

### DevOps / repo hygiene
- **Status:** **July 9 wave landed LFS→R2 pilot + GHA catalog-fanout queue guard on `main`**
- **Details:**
  - **LFS→R2 offload V1 spec + `composed_v4_qwen` pilot — MERGED** (#5306, `5b3f64e29954e252dc5b2dbc6a688dd2711612d8`).
    V1 pilot only; full `assets/manga_catalog` Wave-2 offload remains a follow-on lane. Parent ws `ws_lfs_setup_20260410`
    stays **active** (Phase B history rewrite still owner-gated).
  - **Spine-gates test-fixture false-positive repair — MERGED** (#5341, `0403332493e2e9dafe51a5798d02a1b105e37926`).
    Two genuine fixture blockers re-verified without flagship drift.
  - **GHA catalog-fanout queue-pressure guard — MERGED** (#5471, tip of `main` after wave). Fail-closed throttle on
    `catalog-fanout-*` workflows when queue is hot; authority: `artifacts/coordination/GHA_CATALOG_FANOUT_QUEUE_GUARD_CLOSEOUT_2026-07-09.md`.
    Supersedes manual queue-relief waves as the durable fix for catalog starvation of non-catalog PRs.

### Books-first roadmap (operator scan — 2026-07-11 post-#5525)
- **Authority:** `artifacts/analysis/PROPRIME_100PCT_PRODUCTION_AUDIT_2026-07-10/` (audit snapshot still useful; queue below is live GitHub truth)
- **Verdict:** Pearl Prime books **NOT catalog-scale production-ready** (1 EPUB + 1 flagship PROVEN-AT-BAR ≠ ~1,519 listings)
- **Landed (do not re-queue):** **#5490** spine-default lock (`2236c03a23`, 2026-07-10); **#5501** ja-JP teacher-bank (`45e511ab96`, 2026-07-10); **#5525** book-path workstream closeout (`1f4c3155d8`, 2026-07-10); **#5530** educators×imposter_syndrome REFLECTION parse-gap + binding contradiction repair (`2d9ada1e21`, 2026-07-11 — one cell only, see thin-persona caveat above; do not re-queue this exact cell, catalog-wide REFLECTION parse audit still open). Adjacency/transition/overlay already on `main`: #5156 / #5162 / #5298 / #5515 / #5516 / #5519.
- **Next books-first actions (live order):**
  1. **engine-keyed STORY pool seeding** for the remaining thin personas (educators/nyc) cells + **4-cell tuple-viability rebuild** (#1922 pattern). The `false_alarm`/`imposter_syndrome` binding-governance question is now resolved (#5530: `allowed_engines` side ratified, contradiction removed) — do not re-raise it. A new, separate, not-yet-scoped follow-on: catalog-wide audit of REFLECTION-pool real-parse depth (header count ≠ usable-atom count per #5530's finding).
  2. **Waystream EPUB wave** expansion from the proven spine CLI lane (#1923 pattern; chord: `--pipeline-mode spine --quality-profile production --exercise-journeys`)
  3. **GHL attach batch** for each newly shipped real EPUB
  4. **#5237** atom-cohesion craft lane — **OPEN but RED** (parse-sweep / Schema / Core / Drift / Release failing as of 2026-07-11); repair-needed follow-on, **not** a green next lane; re-evaluate scope against already-landed adjacency/transition/overlay fixes before fresh craft work
  5. **#5206** bestseller-conformance audit/evidence — **OPEN**; treat as evidence-only / partially stale context (do not treat as fresh implementation authority without live reconciliation)
- **Held / not now:** **#5295** (owner), **#3166** (operator budget), **#4861** (governance audit evidence)
- **Not books prerequisite / not live authority:** manga PROVEN-AT-BAR; **#5526** manga-only (already merged tip docs); **#5518** agent-execution-fabric docs — **OPEN/RED** and **absent from `origin/main`** (do not cite as live authority); **#5502** dashscope audit; ~150 catalog-skeleton listing PRs

### Open PR truth (owner/operator-gated — not merged)
| PR | State | Gate |
|----|-------|------|
| **#5237** | **OPEN**, CI **red** | Atom cohesion craft — repair-needed follow-on; **not green**; re-scope vs landed #5156/#5162/#5298/#5515–#5519 before rework |
| **#5206** | **OPEN**, checks green | Bestseller conformance audit/evidence — evidence-only; partially stale vs July 10 adjacency/atom merges |
| **#5518** | **OPEN**, CI **red** | Agent execution fabric v1 docs — **not on `origin/main`**; **not live authority** until merged |
| **#5295** | **OPEN**, checks green | Owner-gated full-repo redundancy/garbage sweep + Q-gated roadmap — **do not merge in this lane** |
| **#3166** | **OPEN**, **draft** | `ci(budget): lean content-PR gating` — **DO NOT MERGE until Jul 1 reset** (operator-gated) |

**Merged (removed from open table):** #5490, #5501, #5525 (book-path lockdown + closeout).

### Storefront
- **Status:** **LIVE (listings)** — **consumer paid-download scale still blocked** on asset depth
- **Details:** Pearl Prime Storefront renders sample/listing data. **GHL feed attach:** 1 real EPUB attached (#1947 —
  see GHL row above). **Storefront consumer paid downloads at scale:** still **0 beyond the single attached cell**
  until the attach pipeline runs for additional titles; Phase A smoke (5 locales × 4 product types) remains **stalled**
  until real asset depth exists. Do not conflate GHL attach (#1947) with full storefront Phase A go-live.

---

## Jul 1 Execution Runbook (plan-of-record)

**Ratified:** 2026-06-30 (OPD-20260630-001/002/003) · **Evidence:** `artifacts/audit/drift_audit_20260630/DRIFT_MATRIX.md`  
**Supersedes** session-handoff ordering for merge dispatch — handoff detail remains in
`docs/sessions/SESSION_HANDOFF_2026-06-29_worldwide_catalog_books_cjk_manga.md` §12 but **this section wins** for
cold-start execution order after the ~Jul 1 CI/budget reset.

| Step | Action | Notes |
|------|--------|-------|
| **0** | **Merge skeleton-freeze PR FIRST** — ensure `config/governance/skeleton_freeze.yaml` → `active: true` | CI enforcement live before any skeleton batch can re-merge |
| **1** | Merge **#3166** (lean-CI path-filter) | ~83% Actions burn reduction; required before flip campaign — **still OPEN/draft/operator-gated as of 2026-07-09** (see Open PR truth above) |
| **2** | Merge staged spine on green: **#3123** (content gaps), **#3127** (CJK recovery), **#3147** (CJK hardening); verify #3123 deletions < 50 | Also **#3110** if green (handoff §12) |
| **2.5** | Merge **delivery-gate stub-catch PR (#3787)** before flip→assemble | So no shipped EPUB carries a `[Persona-specific hook for …]` placeholder — `delivery_contract_gate` hard-fails bracket stubs |
| **3** | **Lane A:** warrior_calm flip pilot → on clean → full flip → assembly → **first R2 EPUB batch** | Split ~170 flip PRs across Jul+Aug per handoff §8 |
| **4** | **Lever A:** finish **#3199** arc-gen pilot → engine-keyed pools + batch-2 | Unblocks +462 thin-persona cells |
| **5** | Merge **#3598** + **#3605** on green | #3605 = plan-scale QA pilot evidence only — **no new QA scaffolding** after (OPD-20260630-003) |
| **6** | **Hold** new proposed-program specs (music v2, sangha, song-kit, teacher-manga-video, agent-system-v2) until first EPUB batch ships | Spec debt cap — see drift audit H2 |
| **7** | ~~Q-DRIFT-02 #1947↔SSOT reconcile~~ **DONE** (this runbook PR) | GHL attach row updated above; storefront row split GHL vs Phase A |

**Skeleton freeze lift:** after step 3 ships the first real R2 EPUB assembly batch, set
`config/governance/skeleton_freeze.yaml` → `active: false` (OPD-20260630-001 lift condition).

### Post-flip quality backlog (Atom Cohesion lane — gated, NOT on the Jul 1 critical path)

Authored 2026-06-30, persisted to `docs/sessions/cohesion_chunk_prompts_20260630/`. Rationale: the plan-scale QA
sweep found the chapter-thesis bank is keyed `intent → engine` only, so the same load-bearing thesis sentence is
reused across **128 (persona×topic) cells** — the top remaining quality lever. These fire **after** the flip
ships the first EPUB batch; they are not Jul 1 critical-path steps.

| Row | Chunk | Fire when | Owner | Prompt |
|-----|-------|-----------|-------|--------|
| **Q1** | Thesis de-templating (engine-keyed → topic-keyed) + fill spiral/overwhelm/comparison + pool depth | First R2 EPUB batch shipped (freeze lifted) | Pearl_Editor + Pearl_Writer | `docs/sessions/cohesion_chunk_prompts_20260630/cohesion_chunk_1_thesis_de_templating.md` |
| **Q2** | Adjacency-aware selector + dwell/integration-pacing craft gate | (a) first EPUB batch shipped **AND** (b) OPD-20260629-002 (#3110/#3123) landed — sequenced **after** Q1 | Pearl_Dev | `docs/sessions/cohesion_chunk_prompts_20260630/cohesion_chunk_2_adjacency_selector.md` |

Q2 is gated behind Q1 (adjacency penalty needs the varied thesis pools) and behind the composer lane landing
(both touch `enrichment_select.py` / `register_gate.py` — serialize, never parallel-edit).

---
*Supersedes all previous status reports and planning baselines (incl. the May 2026 worldwide plan). Latest session
detail: `docs/sessions/SESSION_HANDOFF_2026-06-29_worldwide_catalog_books_cjk_manga.md`.*

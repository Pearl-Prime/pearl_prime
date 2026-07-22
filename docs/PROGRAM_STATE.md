# Program State — Single Source of Truth

**LAST VERIFIED:** 2026-07-22 @ `origin/main` `a08b8af17b4e7b37ac36be7d4c1c8f6049e5ee37` (Pearl Prime pipeline audit 2026-07-22; prior 07-15 tip `8a0b09f9b0…` superseded for Flagship / Books-first / Open-PR / atom-coverage rows below)

> **RULE:** Verify against `origin/main`, never git date or the working tree (shared-tree branch-churn shows
> other-branch/stale state). This is the entry point — if another doc disagrees with this, this wins or that doc is stale.

> **GLOSSARY (read this — it has caused repeated confusion):**
> **Listing** = catalog metadata (title/subtitle/description/cover/dashboard — what a book is *about*).
> **EPUB** = the actual readable, sellable file a customer downloads.
> We have **~1,519 listings** and **89 tracked Waystream EPUB artifacts** under
> `artifacts/epubs/way_stream_sanctuary/` as of #5640/#5641; only cells with merged proof should be
> treated as real attached assets (see Production-Gate). This is still **not** catalog-scale readiness.
> "Books" in most docs means *listings* — do NOT read it as "readable/sellable books."

## Current Status by Track

### Flagship book (gen_z_professionals × anxiety) — PROVEN-AT-BAR
**OPD-20260707-FLAGSHIP-L4** — operator Layer-4 blind-read **APPROVED** the full 12-chapter book
(build 9, `extended_book_2h`, seed `flagship_phase2_layer6`). First PROVEN-AT-BAR book in
program history. Both goldens now live + byte-frozen (re-verified 2026-07-22 audit):
- **Golden #1 (ch1):** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt` — CI-enforced; SHA matches metadata.
- **Golden #2 (full book):** `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt` —
  `content_sha256=e015ddc30b86…`, **21,729w / 122,512 bytes**, metadata `status: ratified`.
  Self-parity via `check_flagship_book_parity.py --snapshot full --full-from-file <golden>` → BYTE-IDENTICAL.
  Live `register_gate` re-score on the golden currently FAILs F6/F7 (F14 share 8.98% under ceiling) —
  Layer-4 human verdict still stands; see `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md` Q-AUDIT-REG-01.
  `check_flagship_book_parity.py --snapshot full` flipped DORMANT→live/required.
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

### ProPrime modes (regular / composite / teacher / music) — VERIFIED 2026-07-11
**Lane:** `agent/proprime-modes-100pct-20260711` → PR **#5535** (`d8532d2d43`) + GHA flagship QA `29129940199`.
- **A regular mode:** PASS — Book flagship QA ladder on `main` (`extended_book_2h` × gen_z×anxiety, `--pipeline-mode spine --quality-profile production --exercise-journeys`) → Pass (chapter_flow/book_quality/ONTGP 0.63/EI 0.72). Artifacts: GHA run 29129940199; local mirror `artifacts/qa/proprime_modes_100pct_20260711/`. Durable Waystream EPUB remains on main (`artifacts/epubs/way_stream_sanctuary/...burnout__overwhelm.epub`, 1.7MB). Fresh Waystream rebuild on current main still hits `bracket_template_stub` on some burnout cells — do not treat that cell rebuild as green without a stub fix.
- **B composite doctrine (regular mode):** PASS — flagship `enrichment_audit.json` shows `slots_from_composite=12` with `source=composite_doctrine` / `COMPOSITE_DOCTRINE v01–v15` (not teacher-mode hybrid).
- **C teacher mode:** PASS under named production gates — `run_teacher_production_gates.py` PASS after #5535 kenjin EXERCISE seed; `pytest` teacher e2e smoke kenjin+joshin PASS (timeout 300s). Teacher teachings present in renders (`slots_from_teacher` 48–60). Full production book-quality Pass for every teacher×cell is **not** claimed (anxiety+joshin chapter_flow FAIL; some burnout cells stub-Reject).
- **D music mode:** PASS as overlay production lane — `pytest` music suite 12/12; spine render `--music-mode with-lyrics --musician-id ahjan` four-piece chord → book_quality Pass + `music_overlay_audit.json` applied with LYRIC_* + MUSIC_REFLECTION_* injections. Music V2 / MusicGen / first-external-musician remain **proposed/held** (PROGRAM_STATE hold #6); ahjan_music is reference kit only.

### Production-Gate / Real-EPUBs
- **Status:** **BOOKS-FIRST MICRO-WAVE SHIPPED — durable on `main` (89 Waystream EPUB artifacts; 2 newly verified + attached in the 2026-07-14 pack); not catalog-scale**
- **Details:** Book assembly is **deterministic atom-composition** (no LLM at build; thin pools must raise
  `InsufficientVariantsError` → fix by adding atoms, never LLM-expand — verify `pearl_writer_expand.py` is NOT on the
  spine/production path). ✅ **F1/F4 + F2/F7 precision all on `main`** via PR #1919 (`ae4991bd3a`). **First gate-passing
  Waystream EPUB SHIPPED** (PR #1923, `4e6320b19c`): `corporate_managers × burnout × overwhelm`, register **PASS**,
  ei_v2 0.62, 13,759 words, 1.7 MB → `artifacts/epubs/way_stream_sanctuary/`. **3 generalization cells**
  (anxiety/false_alarm, boundaries/shame, boundaries/comparison) all register-PASS, ei_v2 0.62–0.64 — corporate_managers
  scales with **zero engine work** (loop spine CLI over the F006 arc matrix + `build_epub.py`).
  **2026-07-14 books-first pack:** foundation #5627 (`7914b45693f`), thin-persona slate #5630
  (`3359ea161c`), no-op writer receipt #5632 (`8560a873fd`), four-cell tuple proof #5637 (`5576257ebe`),
  Waystream EPUB wave #5640 (`2039983797`), and GHL attach #5641 (`19edc45e0b`) all landed. #5640 added two
  new real EPUBs from proof-approved NYC executive anxiety cells:
  `way_stream_sanctuary__nyc_executives__anxiety__false_alarm.epub` (45,319 bytes) and
  `way_stream_sanctuary__nyc_executives__anxiety__watcher.epub` (47,187 bytes). Both passed hard production gates
  (chapter_flow/book_pass/book_quality/EI V2) with register_gate WARN(F13) and no bracket-stub matches; the current
  durable Waystream convention is coverless, so `validate_epub.py` records `missing_cover` as expected. The attempted
  `educators × imposter_syndrome × false_alarm` render did **not** ship because production mode failed
  chapter_flow/book_pass/book_quality gates. Final audit authority:
  `artifacts/qa/books_first_epub_wave_final_audit_20260714/SUMMARY.md`.
- ⚠ **Thin-persona caveat (the next lane):** **canonical atom repair MERGED** (#5489, 2026-07-10) — educators/nyc
  slot-keyed gaps partially closed. **#5530 (2026-07-11, `2d9ada1e21`) closed one more downstream blocker**: `educators ×
  imposter_syndrome` full spine render was still hard-failing with `EnrichmentGapError` on `REFLECTION` (ch7) even
  after #5489 — root cause was **not** pool thinness but a parser quirk in `registry_resolver._parse_canonical_txt`
  (single-delimiter atom blocks silently parse to **zero** real atoms; header count is not a reliable depth proxy for
  this file family). #5530 appended 15 two-delimiter REFLECTION atoms (0→15 real usable) + removed a stale
  `false_alarm` entry from `imposter_syndrome.forbidden_engines` (`false_alarm` remains legal in `allowed_engines`;
  production `check_tuple_viability` reads allowed only). Proof: educators×imposter×false_alarm F006 full spine
  render **structurally clear** (Layer 1) — `artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md`. Do **not**
  re-queue the stale “`false_alarm` not in allowed_engines” premise. Remaining blockers before spine-buildable EPUBs
  at catalog scale: broader **engine-keyed** STORY pools for remaining thin-persona cells; **4-cell rebuild proof**
  (#1922 pattern); `nyc × anxiety/false_alarm` may still need **one band-1 STORY atom**; **governance-only
  `NO_BINDING` cells** (distinct from repaired legal `false_alarm` cells): educators×boundaries×overwhelm,
  educators×burnout×shame, educators×compassion_fatigue×shame, nyc_executives×burnout×shame; a catalog-wide
  REFLECTION-pool parse audit (header count ≠ usable-atom count per #5530) is a new, separate, not-yet-scoped lane.
  The 2026-07-14 pack proved four legal tuples and shipped two NYC-executive EPUBs; next books-first work is another
  small, proof-approved EPUB batch and/or a focused fix for the failed educators gate, with binding calls only for true
  `NO_BINDING` cells.
- **Wave 2026-06-25 (teacher-bank unblock):** 12 teachers now have `TEACHER_DOCTRINE` atoms (PR #1914) — all 26
  brands unblocked from the `library_34` fallback. 29 `CANONICAL.txt` files backfilled for educators + nyc_executives
  thin slots (PR #1915); 69/69 tests pass.
- **Infra gaps RESOLVED (#1924, `68163beab1`):** `sai_ma` `positioning_profile` was a **dangling ref** — added the
  `devotional_companion` profile to `author_positioning_profiles.yaml`. `kenjin` added to
  `config/catalog_planning/teacher_persona_matrix.yaml` (mirrors joshin's guardrails). **Q-KENJIN-01 OPEN:** the matrix
  has no `active`/`tier` field, so kenjin is a first-class entry = active-by-presence — **operator to confirm**.

### GHL marketing feed
- **Status:** **LIVE** — **paid EPUB attach path expanded by the 2026-07-14 books-first micro-wave** (#5641, `19edc45e0b`)
- **Details:** `marketing_feed.json` published on brand-admin Pages (public HTTPS) (#1866/#1867/#1875/#1882); R2
  provisioned; 15-topic integration; all 15 funnel landings → GHL capture. Design: paid items gate on **real attached
  asset** (`pending_asset` until then), free items on **asset-exists**; **free-content-first** — paid auto-promotes on
  attach. Funnel is live on free content + listings. **First paid attach:** Waystream
  `corporate_managers × burnout × overwhelm` EPUB in `brand_deliveries/way_stream_sanctuary.json` week 2026-W26
  (`way_stream_sanctuary__default_teacher__corporate_managers__burnout__overwhelm.epub`, R2-backed download URL) per
  #1947 — satisfies the GHL paid-slot attach row (OPD-20260630-002 / Q-DRIFT-02). **2026-07-14 attach:**
  #5641 added the two new NYC executive anxiety EPUBs to `brand_deliveries/way_stream_sanctuary.json` and verified R2
  `head_object` for both keys; feed entries moved `791 -> 793` with proxy URLs
  `/download/way_stream_sanctuary__nyc_executives__anxiety__false_alarm?week=2026-W29` and
  `/download/way_stream_sanctuary__nyc_executives__anxiety__watcher?week=2026-W29`. No secrets or presigned URLs were
  persisted.

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
- **Status:** **July 9 wave landed LFS→R2 pilot + GHA catalog-fanout queue guard on `main`; July 15 old-chat unblock wave reduced stale PR requeue risk**
- **Details:**
  - **LFS→R2 offload V1 spec + `composed_v4_qwen` pilot — MERGED** (#5306, `5b3f64e29954e252dc5b2dbc6a688dd2711612d8`).
    V1 pilot only; full `assets/manga_catalog` Wave-2 offload remains a follow-on lane. Parent ws `ws_lfs_setup_20260410`
    stays **active** (Phase B history rewrite still owner-gated).
  - **Spine-gates test-fixture false-positive repair — MERGED** (#5341, `0403332493e2e9dafe51a5798d02a1b105e37926`).
    Two genuine fixture blockers re-verified without flagship drift.
  - **GHA catalog-fanout queue-pressure guard — MERGED** (#5471, tip of `main` after wave). Fail-closed throttle on
    `catalog-fanout-*` workflows when queue is hot; authority: `artifacts/coordination/GHA_CATALOG_FANOUT_QUEUE_GUARD_CLOSEOUT_2026-07-09.md`.
    Supersedes manual queue-relief waves as the durable fix for catalog starvation of non-catalog PRs.
  - **Old-chat unblock wave — MERGED/REDUCED 2026-07-15:** durable closeout #5652 (`b426f5c547`),
    #5645 successor #5655 (`b56ce80fc8`), #5629 clean research successor #5656 (`39e9c436e9`),
    and closeout handoffs #5658 (`2c4b4a5270`) are on `main`. Original PRs #5645 and #5629 were closed as
    superseded after their successors merged; #5636 had already merged (`73e4a6fbb6`). Do not requeue the old
    #5645 Core failure or the polluted #5629 batch; use the merged successors as authority. Local worktree cleanup
    remains preservation-blocked by low disk and dirty/untracked value, with the ledger in
    `artifacts/coordination/handoffs/05_preservation_first_worktree_cleanup_2026-07-15.md`.

### Books-first roadmap (operator scan — 2026-07-14 post-#5641)
- **Authority:** `artifacts/analysis/PROPRIME_100PCT_PRODUCTION_AUDIT_2026-07-10/` (audit snapshot still useful) + `artifacts/qa/thin_persona_buildability_2026-07-11/SUMMARY.md` + `artifacts/qa/books_first_epub_wave_final_audit_20260714/SUMMARY.md`
- **Verdict:** Pearl Prime books **NOT catalog-scale production-ready** (89 tracked Waystream EPUB artifacts + 1 flagship PROVEN-AT-BAR ≠ ~1,519 listings; the 2026-07-14 pack shipped/attached a two-EPUB micro-wave only)
- **Landed (do not re-queue):** **#5490** spine-default lock (`2236c03a23`, 2026-07-10); **#5501** ja-JP teacher-bank (`45e511ab96`, 2026-07-10); **#5525** book-path workstream closeout (`1f4c3155d8`, 2026-07-10); **#5527** books-first SSOT refresh (`b58cdba62e`, 2026-07-10); **#5489** thin-persona canonical atom repair; **#5530** educators×imposter_syndrome REFLECTION parse-gap + binding contradiction repair (`2d9ada1e21`, 2026-07-11 — one cell only, see thin-persona caveat above; do not re-queue this exact cell); **#5532** PROGRAM_STATE thin-persona reflection (`e11f44b5ab`, 2026-07-11); **#5627/#5630/#5632/#5637/#5640/#5641** books-first EPUB wave foundation → slate → no-op seed → tuple proof → two-EPUB ship → GHL/R2 attach. Adjacency/transition/overlay already on `main`: #5156 / #5162 / #5298 / #5515 / #5516 / #5519.
- **Next books-first actions (live order):**
  1. **story_atoms for EPUB workhorse cells** (esp. `corporate_managers` × top topics/engines) so research_fit can bind — 2026-07-22 audit: register-PASS books still ship unbound (`structurally_clear_only`). Authority: `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`.
  2. **Next proof-approved EPUB micro-wave:** either fix the failed `educators × imposter_syndrome × false_alarm` production gates or choose the next tuple-proof-approved cells; keep smoke→pilot→scale caps and do not promote anything until a real EPUB exists.
  3. **GHL attach each newly shipped real EPUB** using the existing `brand_deliveries/way_stream_sanctuary.json` + R2 proof convention; no paid promotion without asset-exists proof.
  4. **True governance-only `NO_BINDING` cells** still require a binding call; do not conflate them with already-legal/repaired `false_alarm` cells.
  5. **Atom-cohesion craft (ex-#5237):** PR number **no longer resolves** on this repo. Q1 thesis topic-overlay **partially landed** (8 topics in `chapter_thesis_bank.yaml`); Q2 adjacency/dwell craft gate **still open**. Do not cite `#5237`/`#5206` as live.
- **Landed 2026-07-21 (do not re-queue):** **#9** `feat(bestseller-atom-flow): research_fit honesty gate + acceptance-layer stamp + cell-aware driver + courage atoms` (`280597dacf`) — advisory CI gates 34/35 + Drift detectors wiring; courage story_atoms for millennial_women_professionals×false_alarm only.
- **Held / not now:** owner-gated hygiene / lean-CI drafts — re-derive via `gh pr list` (old #5295/#3166/#4861 numbers may be stale on this repo).
- **Not books prerequisite / not live authority:** manga PROVEN-AT-BAR; agent-execution-fabric docs until merged on `origin/main`.

### Open PR truth (re-derived 2026-07-22 — old #5237/#5206 DO NOT RESOLVE)
| PR / item | State | Gate |
|----|-------|------|
| **ex-#5237 atom-cohesion** | **STALE NUMBER** | Search by title/branch; Q1 partial / Q2 open per audit — do not cite #5237 |
| **ex-#5206 bestseller-conformance** | **STALE NUMBER** | Superseded by `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md` |
| **#56** | **OPEN** | Piper *prompt* for this audit only — not the audit report itself |
| **#9** | **MERGED** 2026-07-21 | bestseller-atom-flow honesty gates + courage atoms |

**Merged (removed from open table):** #5490, #5501, #5525 (book-path lockdown + closeout); #5527 (books-first SSOT); #5489/#5530 (thin-persona atom + residual buildability); #5532 (PROGRAM_STATE thin-persona reflection); #9 (bestseller-atom-flow 2026-07-21).

### Storefront
- **Status:** **LIVE (listings)** — **consumer paid-download scale still blocked** on asset depth
- **Details:** Pearl Prime Storefront renders sample/listing data. **GHL feed attach:** the original real EPUB attached
  by #1947 plus the two 2026-07-14 NYC executive anxiety EPUBs attached by #5641 (see GHL row above). **Storefront
  consumer paid downloads at scale:** still blocked on real asset depth; Phase A smoke (5 locales × 4 product types)
  remains **stalled** until deeper real-download coverage exists. Do not conflate GHL attach rows with full storefront
  Phase A go-live.

---

### Social Media Atom Bank
- **Status:** **ACTIVE project since 2026-07-21 — previously had NO row in this SSOT at all**, despite
  being an active project; that omission is itself one of the gaps closed by
  `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md` (full layer-honest plan + Q-gates there).
  **No component of this subsystem has reached PROVEN-AT-BAR.**
- **Details:**
  - **Atom bank:** `SOURCE_OF_TRUTH/social_media_atoms/` — ~1,952 total rows: 1,642 EN evergreen
    (`evergreen_en_us_atoms.jsonl`), 250 platform/surface (`platform_surface_atoms.jsonl`), 60 APAC
    localization (`apac_localization_atoms.jsonl`: ja-JP/zh-TW/ko-KR/zh-CN/zh-HK/en-SG). Registry row
    `evergreen_social_atom_bank` is durable in `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`.
    **EXECUTED-REAL**, not PROVEN-AT-BAR: 98.7% of rows
    share undifferentiated boilerplate `SRC_*` citations (only 1.3% are falsifiable quote+path citations,
    per `artifacts/qa/social_research_currency_audit_20260722/RESEARCH_CURRENCY_AUDIT.md`).
  - **Brand/author vibe schema** (`SOCIAL-ATOM-BANK-VIBE-01`, `docs/PEARL_ARCHITECT_STATE.md`) is durable
    on `origin/main`: the voice-profile catalog and deterministic assembler wiring both exist.
    **Anti-spam variation gate** (`scripts/ci/check_social_post_variation.py`) was wired into production
    readiness by PR #123; its corrected unique display number is gate 45 (formerly cited as gate 36).
    PR #75 is merged, and `social_media` is registered in `SUBSYSTEM_AUTHORITY_MAP.tsv`.
  - **Visual-license operator gate:** `artifacts/qa/deterministic_social_visual_gate_20260718/` — 3 source
    visuals license-verified, but **0 of 405 render rows production-ready**, `LIVE_PUBLISHING_AUTHORIZED=no`
    pending operator look-packet approval (`artifacts/operator_read_packets/deterministic_social_visual_gate_20260718/operator_look_packet.md`).
    Single largest concrete blocker between "atoms exist" and "a real post could ship with real visuals."
  - **Storyblocks visual b-roll bank:** 16 licensed assets across 8 of a planned 12 topics
    (`social_media_bank_storyblocks_20260720`); full 12-topic fill explicitly not yet claimed done.
  - **Weekly research-refresh cadence:** ran once (2026-07-18, digest + delta-atom promotion, both
    completed same-day) — **zero recurring mechanism** (no cron/workflow/scheduled-task) found anywhere
    in the repo; "weekly" is not yet mechanically enforced.
  - **APAC review-gate compliance:** 60/60 rows at `review_status=reviewed_candidate` (correctly not
    `draft`, but also not `production_ready`) — review evidence is one operator chat-level assertion
    (`OPD-OC7-02`), not a durable per-row native-reviewer sign-off artifact.
  - **Live scheduling:** correctly `NOT_AUTHORIZED` — a ratified spec non-goal (§Non-Goals), not a defect.
  - **Full plan, sequenced gap list, and Q-SOCIAL-* open questions:**
    `docs/specs/SOCIAL_MEDIA_100PCT_PRODUCTION_PLAN_2026-07-22.md`.


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

| Row | Chunk | Fire when | Owner | Prompt | Status 2026-07-22 |
|-----|-------|-----------|-------|--------|-------------------|
| **Q1** | Thesis de-templating (engine-keyed → topic-keyed) + fill spiral/overwhelm/comparison + pool depth | First R2 EPUB batch shipped (freeze lifted) | Pearl_Editor + Pearl_Writer | `docs/sessions/cohesion_chunk_prompts_20260630/cohesion_chunk_1_thesis_de_templating.md` | **PARTIAL** — freeze lifted; 7 engine baselines + `topics:` overlay for 8 topics; cross-cell identical chapter opens still observed in audit samples |
| **Q2** | Adjacency-aware selector + dwell/integration-pacing craft gate | (a) first EPUB batch shipped **AND** (b) OPD-20260629-002 (#3110/#3123) landed — sequenced **after** Q1 | Pearl_Dev | `docs/sessions/cohesion_chunk_prompts_20260630/cohesion_chunk_2_adjacency_selector.md` | **OPEN** — F13 dwell detector exists but WARN-only; no adjacency HARD gate |

Q2 is gated behind Q1 (adjacency penalty needs the varied thesis pools) and behind the composer lane landing
(both touch `enrichment_select.py` / `register_gate.py` — serialize, never parallel-edit).

### Atom coverage (en_US) — measured 2026-07-22
- `scripts/inventory/atom_coverage_audit.py`: **100%** CANONICAL presence on 13 personas × **15 core production topics**; **29.8%** on the script's full 57-topic list (221/741).
- `story_atoms/…/anchored/`: **6 personas / 9 persona×topic cells** (courage only for millennial_women_professionals×false_alarm). Authority: `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`.

---
*Supersedes all previous status reports and planning baselines (incl. the May 2026 worldwide plan). Latest session
detail: `docs/sessions/SESSION_HANDOFF_2026-06-29_worldwide_catalog_books_cjk_manga.md`.*

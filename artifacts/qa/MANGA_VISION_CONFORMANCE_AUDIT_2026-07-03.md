# Manga Vision-Conformance Certification — 2026-07-03

**Author:** Pearl_Architect (manga 100% certification lane, `agent/manga-100pct-certification-20260703`)
**Method:** 7-axis Workflow fan-out against **origin/main `7d2cdeb256ed3b53c0d4b5d95d90b8f0539f9f5e`** (never the working tree), one verifier per vision axis, followed by an adversarial refutation pass on every finding claimed at CODE-WIRED or above (41 agents total; 33 findings refuted/confirmed/downgraded). Every byte claim resolved via the git object DB with LFS pointer `size` fields.
**Supersedes:** `docs/MANGA_RECOVERY_AUDIT.md` and `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` as the current honest state (cited, not re-derived).
**Pearl Star:** UNREACHABLE this session (SSH timeout to 100.92.68.74, ComfyUI :8188 no response, `tailscale ping` no reply — local MagicSock health warning, may be Mac-side). All box-side claims are labeled UNVERIFIED-THIS-SESSION.

**Acceptance layers used throughout (never conflated):**
`ABSENT → RESEARCHED → SPECCED → CONFIG-EXISTS → CODE-WIRED → EXECUTED-REAL → PROVEN-AT-BAR`

---

## 1. The 60-second table — R1–R8 conformance

| Axis | Vision requirement | Honest % | Highest proven layer | The single blocking gap |
|---|---|---|---|---|
| **R1** | Market research → per-locale genre allocation → series plans, per locale | **30%** | RESEARCHED (10/13 locales) | Per-locale genre **allocation** config does not exist; GENRE_PORTFOLIO_PLAN.md is a global 12-genre × 37-brand matrix; the CJK-genre-led vs Western-intent-led split is researched but encoded nowhere |
| **R2** | Every series a bestseller-grade genre story first, topic as subtle inner arc | **45%** | EXECUTED-REAL (16 authored scripts) | No at-scale genre-expert writer lane: the wired pipeline's writer stage emits stub/proxy prose; only Tier-1 hand-authoring produces craft; 44/129 canonical genres lack craft bibles |
| **R3** | Teacher teachings via genre-native apparatus, never named | **25%** | CONFIG-EXISTS (30 vessels) | `manga_mode_vessels.yaml` is consumed by **no** story-generation code path; apparatus-per-genre research doc ABSENT |
| **R4** | Music-mode influence/lyrics/motifs threaded per genre | **8%** | CONFIG-EXISTS (15 music vessels) | Zero research, zero wiring, zero execution — needs the music×manga sub-spec first |
| **R5** | Per-series image bank + deterministic layered assembly (never single-shot pages) | **22% → 34% after this session** | EXECUTED-REAL (1 episode, Apr 2026 + this session's demo) | Zero REAL banked L1/L3/L4 assets (all sprites INTERIM); 0 trained LoRAs; PuLID nodes not installed (box-side, unverified); V5 spec's per-panel decompose drops cross-panel bank reuse — vision delta |
| **R6** | Stories first → banks → assembly at scale | **40%** | EXECUTED-REAL (1 series follows the doctrine) | Story authoring at scale: 10 authored episodes vs 1,345 planned series |
| **R7** | Judged at top-Japanese-pro bar | **5%** | SPECCED (rubric axes derivable) | No blind-judge protocol exists; **zero** artifacts are PROVEN-AT-BAR; gate-PASS instrumentation ≠ the bar |
| **R8** | Full grid: 13 locales × 37 brands planned/storied/banked/assembled | **35%** | EXECUTED-REAL (1,345 plans, 5 locales) | 8/13 registry locales have ZERO series plans (es_US, es_ES, fr_FR, de_DE, it_IT, hu_HU, zh_SG, zh_HK) |

Machine-readable: `artifacts/qa/manga_vision_conformance_20260703.tsv`

**One-sentence verdict:** the manga system is a well-specced, partially-wired scaffold with exactly **one** vision-conformant series executed end-to-end ("the alarm is lying": 16 authored scripts, 386 real rendered images, layered L0+L2 render cache, and — as of this session — a working deterministic bank-assembly lane); everything else is plans and configs awaiting stories, banks, wiring, and judgment.

---

## 2. Render truth (byte-verified, refutation-passed)

**On origin/main (the only render truth that counts):**

| Series | ok-rows claimed | REAL ≥50KB on main | Verdict |
|---|---|---|---|
| stillness_press__…__the_alarm_is_lying (April v4 tree) | n/a | **386 files, 212,790,093 bytes** (304 composed_v3 segs across ep_001–ep_010 + 35 composed_v4 ep_001 pages + 47 v4_render_cache layer assets incl. 5 L0 plates + 19 L2 poses with alpha cutouts) | **EXECUTED-REAL** — this is the entire real render estate |
| sleep_vol1 ep_001 | 34 ok (2.6–3.1MB each in TSV) | **0 — image paths do not exist on origin/main** | TSV metadata only; renders box-side, UNVERIFIED-THIS-SESSION |
| somatic_vol1 ep_001 | 34 ok | **0 — same** | same |
| bodyholds_vol1 (working tree, untracked) | 34 ok | 34 rows of **bytes=1 stubs** | the stub-as-done exhibit; never main-state |
| Contact sheets series2/3 | n/a | 2 files, 1,518,295 bytes | EXECUTED-REAL |
| image_bank/stillness_press/ | "6 anchor panels" (prior) | **0 PNGs — 9 metadata JSONs only** | prior REFUTED: bank is metadata-only on main |

**Correction to router priors:** the "real renders on main = sleep_vol1 + somatic_vol1 panels" prior is WRONG about location — their TSVs are on main, the panels are not. Conversely the April tree is far richer than the prior implied (all ten episodes have composed_v3 strips). The **1,344/1,345 titled** finding also REFUTES the "series_title blank everywhere" prior — title synthesis has since executed for all 5 planned locales.

**Pearl Star / queue state:** UNVERIFIED-THIS-SESSION (box unreachable). Documented state: manga GPU lane de-ranked below CJK atoms (OPD-20260629-003); dispatch bug (permission-denied + 333 zombie jobs) fix staged unmerged on `agent/pearl-star-manga-queue-unblock-20260629` (PR #3075, OPEN); queue reaper PR #4565 OPEN. Saturation snapshot branch `snapshot/pearl-star-manga-saturation-wip-20260702` (`b199122d26`) holds 8 new ops files (refiller + monitor + systemd units, 878 insertions, zero deletions) — REUSE candidate, review-gated, **never auto-merge** (killed-agent WIP).

---

## 3. Per-axis detail

### R1 — market-first genre allocation (30%, RESEARCHED)

The 13-locale × 3-stage truth table (research → allocation → plans), refutation-adjusted — full table in §7:

- Research exists for 10/13 locales (`research/2026-03-30_*` triad). **it_IT: zero research. zh_SG: zero research. hu_HU: low-confidence** (5/10 opportunity note inside the EU doc).
- A per-locale genre **allocation** exists NOWHERE. `docs/GENRE_PORTFOLIO_PLAN.md` is global. `config/localization/…lane_content_mix` encodes manga *share* per locale (e.g. ja_JP 70%, zh_TW 55%, fr_FR 30%) — share is not genre mix.
- The CJK-genre-led vs Western-intent-led split (the heart of R1) is explicit in research prose and encoded in **no** config or code (CONFIRMED).
- fr_FR and zh_TW carry declared manga slices yet the market catalog registry omits their manga tracks (MANGA_MARKET_INTEGRATION_V1_SPEC §C-1/C-2 flags C-1, C-2) — plans can't route to platforms.
- Refutation: V1's single CODE-WIRED claim ("series plans implement per-locale allocations") was DOWNGRADED to CONFIG-EXISTS — plans exist; nothing verifies them against an allocation.

### R2/R6 — story capability (45% / 40%, EXECUTED-REAL for 16 scripts)

- **The real path on main:** `.github/workflows/manga-pipeline.yml` (workflow_dispatch: brand/topic/genre) → `scripts/run_manga_pipeline.py::run_one_book()` → `emit_series_setup()` → `story_architecture_handoff.json` → chapter script → render prep. Refutation UPGRADED this from "no orchestrator" to CODE-WIRED end-to-end. **But** the automated chapter-writer stage is replay/stub (proxy dialogue); bestseller-grade prose exists only where Tier-1 (Pearl_Writer) hand-authored it.
- **16 authored chapter scripts on main** (byte-verified, 9–23KB real YAML each, with craft notes: pacing analysis, bubble register, failure_modes_avoided): 10 × "alarm is lying" ep_001–010, 3 × cognitive_clarity, 1 × warrior_calm_cultivation (mecha-burnout), 1 × stabilizer_healing (workplace), 1 other. CONFIRMED by refuter.
- **Internal craft screen** of 5 scripts (criteria pre-derived from craft bibles): 3 read as compete-grade genre stories, 1 competent draft, 1 scaffold. The refuter found metric errors in the judgment and it is **internal** — this is NOT PROVEN-AT-BAR and is recorded only as a positive signal.
- **Craft bibles:** 20 cover ~66% of the 129 canonical genre entries; 44 uncovered (isekai, horror variants, comedy, cultivation, medical…).
- `bestseller_gate.py` is post-hoc QC (panel-count floor, placeholder detection, register checks) — not writing guidance. CONFIRMED.
- R6 sequencing doctrine (stories→banks→assembly) is followed by the one executed series; there is no enforcement anywhere that renders cannot start before scripts exist.

### R3/R4 — teacher/music vessels (25% / 8%, CONFIG-EXISTS)

- `config/manga/manga_mode_vessels.yaml`: **30 vessels (15 genres × teacher+music)** — the prior's "32/16-genre" count was off by one genre. Quality: 3 A-grade apparatus (genre-native, wound→turn→renewal complete), 3 C-grade (apparatus clarity issues); sketched in-config, not research-derived.
- **Wiring: zero.** A loader exists; `story_architect.py` hardcodes beat templates and never consumes vessels (refuter DOWNGRADED "wired to loader" to CONFIG-EXISTS — a loader nobody calls is config). Integration points named: story_architect beat shaping, chapter-writer prompt assembly, contract_to_prompt_compiler visual doctrine.
- **Teacher-never-named:** scan of all authored scripts found **no violation** (the one claimed warrior_calm violation was REFUTED — metadata header, not in-story). The "therapist" in the alarm series is the vessel working exactly as the vision demands.
- **Music×manga:** 15 music vessels exist in the same config; zero research, zero code, zero scripts. Authority doc `MANGA_MODE_WRAPPER_DESIGN.md` is cited by the config and **does not exist on main**.
- Apparatus-per-genre research doc: ABSENT (CONFIRMED) — commissioning it is a roadmap milestone.

### R5 — layered image system (22% → 34%, EXECUTED-REAL ×1 + this session's lane)

- **The compositor void is REFUTED in one direction and CONFIRMED in another.** `scripts/manga/render_v4_episode.py::composite_panel()` (spec §10 math: tight-crop → min-scale → LANCZOS → centered paste, hard alpha) EXISTS and EXECUTED in April: 5 unique L0 plates + 19 L2 pose cutouts with alpha mattes → 35 composed ep_001 pages, all byte-real on main. What was truly ABSENT: the **L3 object-sprite scale/place lane** (V4.0 MVP skipped L3 explicitly), L1/L4 lanes in code, and any **standalone manifest-driven bank assembler** decoupled from GPU orchestration.
- **This session landed the missing lane** (see §6): `scripts/manga/assemble_from_bank.py` + `schemas/manga/assembly_manifest.schema.json` — all five layer classes, §4 z-order incl. L3 above/below-L2, §4.5 L4 screen-blend, mandatory REAL/INTERIM provenance, 9 passing tests, and a 6-panel strip assembled from the real April bank.
- **Asset truth:** image_bank dir = 9 metadata JSONs, zero PNGs (prior "6 real anchor panels" REFUTED). LoRAs: `brand_lora_plans.yaml` all "planned", zero .safetensors anywhere. PuLID: workflow JSONs exist on main; node install state UNVERIFIED-THIS-SESSION. Phase A individuation (constraint_solver/prompt_builder/qa_face_distance): code on main, refuter DOWNGRADED qa_face_distance to CONFIG-EXISTS as a pipeline stage (no production caller) — though it RUNS (this session executed it, §6).
- **Vision-vs-spec delta (needs operator eyes):** `MANGA_V5_LAYERED_ARCHITECTURE.md` supersedes V4's L0+L2 unique-render bank with **per-panel single-dispatch decompose** — architecturally simpler and better cutouts, but it drops the *cross-panel asset reuse* that is the core of the operator's "bank × assembly = thousands of stories" vision. Reconciliation (adopted by the roadmap): V5's per-panel decomposed layers (saved per spec §8 as re-edit assets) feed the **bank**; `assemble_from_bank.py` recombines them across panels. V5 renders once per unique need; the bank multiplies it.

### R7 — pro-grade bar (5%, SPECCED)

- Instrumentation that exists: manga QC gate suite (structural gates CODE-WIRED in the pipeline; refuter trimmed the "19 live gates" inventory), bestseller_gate (prose QC), validate_layer (cutout/composite QA), qa_face_distance (runnable, unwired), craft/quality-bar research corpus (8+ professional benchmarks documented).
- **Nothing on origin/main is PROVEN-AT-BAR. No blind-judge artifact exists** (CONFIRMED by absence sweep of artifacts/qa/).
- Rubric axes a pro review requires (derived from the craft bibles): panel-flow readability, page-turn/tobira placement, character consistency, lettering craft, genre-trope fluency, anatomy, tone/screentone quality, dialogue register. Instrumented today: character consistency (partially), cutout hygiene. Uninstrumented: everything else.
- **Proposed blind-judge protocol (manga blind-10 analog)** — PROPOSAL ONLY: sample 10 episodes across ≥4 genres, each paired with 2 published comparator excerpts (same genre/demographic); judges = operator-recruited human manga professionals (JP-market native for ja_JP lanes); pre-screen with Qwen2.5-VL on Pearl Star (free tier) to filter obvious failures before spending human attention; rubric = the 8 axes above, 1–5 anchored scale; PASS = median ≥4 on craft axes with no axis median <3; verdict artifact: `artifacts/qa/manga_blind10_<date>/VERDICT.md` + per-judge scorecards. Zero paid APIs.

### R8 — full grid (35%)

Master grid (machine-counted, refutation-passed) — full table §7: 37-brand canon frozen and EXECUTED as config; 5 locales carry 1,345 series plans (en_US 268, ja_JP 269, ko_KR 266, zh_CN 268, zh_TW 274), 1,344 titled; 10 episodes authored; 1 series rendered-real; 4 catalog CSVs (69 zh_CN rows blocked_lora — count corrected from the 153 prior); ko_KR whole-locale `hold_pending_market_clearance`. Eight locales zero across every column. Copy-across vs standalone: DOWNGRADED to SPECCED (platform-family config exists; no analysis doc decides which brands copy vs stand alone). Japan manga-only catalog: SPECCED (proposed), Q1/Q2 open (legal entity = operator-tier).

---

## 4. What failed in prior attempts → what now enforces against it

| Drift class (burned prior sessions) | Enforcement landed/proposed |
|---|---|
| **Stub-as-done** (bytes=1 rows marked ok; bodyholds_vol1) | `assemble_from_bank.py` refuses unlabeled layers; provenance table emitted on every run. **Roadmap M1 gate:** `check_render_progress_bytes.py` CI gate — any RENDER_PROGRESS row with `status=ok` and `bytes<50KB` fails the PR |
| **Listing-as-story** (1,345 plans ≠ 10 stories) | Audit + TSV count `storied` as a separate column forever. **Roadmap M1 gate:** story-authored gate — a series may not enter render queues without a chapter_script whose pages/panels parse and exceed the substance floor (reuse `bestseller_gate.py` substance checks as the entry gate) |
| **Unwired-config-as-working** (vessels, qa_face_distance) | Refutation pass institutionalized: CODE-WIRED requires a named entrypoint (CLI/CI/pipeline stage). **Roadmap M1 gate:** `check_manga_wiring.py` — configs in config/manga/ must have ≥1 non-test consumer or carry an explicit `status: unwired` header |
| **Interim-as-final art** | Manifest schema makes provenance mandatory; INTERIM rows carry the exact replacement command (`RESUME_COMMANDS.sh` pattern) |
| **Doc self-reports believed** | This audit supersedes; layer taxonomy mandatory in every status claim (CLAUDE.md-level rule proposed in roadmap) |

---

## 5. Open operator questions (Q-MANGA-01..07 — defaults stated, NOT decided)

| # | Question | Default applied in this audit |
|---|---|---|
| Q-MANGA-01 | Locale grid: registry has 13 (incl. zh-SG, **no pt-BR**); operator says 14 | Certified against registry-13; pt_BR addition is a roadmap milestone (exists only in do-not-merge PR #1604), not a silent registry edit |
| Q-MANGA-02 | Western product shape = illustrated self-help picture books (Gen Z/Alpha)? | YES per operator statement; encoded in the roadmap's per-locale allocation milestone; needs ratification into the allocation config |
| Q-MANGA-03 | GPU priority for manga renders | CJK lane keeps priority (OPD-20260629-003); this lane requests a bounded low-priority pilot (~2–4 GPU-h) — Phase D fallback used zero GPU this session |
| Q-MANGA-04 | PuLID-first vs LoRA-first for face lock | PuLID first (workflows authored, no training cost); LoRA for flagship series after |
| Q-MANGA-05 | ko_KR hold | Keep hold; grid treats ko_KR as plan-complete/ship-gated |
| Q-MANGA-06 | Tentpole D1 (ja_JP warrior_calm×battle, open since PR #771) | Present A/B/C in roadmap §Q; recommendation: (B) re-point warrior_calm ja_JP to the cultivation-burnout hybrid its authored script already proves; not self-ratified |
| Q-MANGA-07 | Japan manga-only catalog Q1/Q2 | Assume identical 37 brand IDs + same volumes until operator says otherwise; legal-entity item flagged operator-tier |

---

## 6. Phase D — layered assembly proof (delivered this session)

**The demanded demo exists:** a 6-panel webtoon strip, one scene arc (the ep_001 therapist/alarm/steam metaphor, beats 023→032, real Tier-1 script text), assembled **deterministically** from separate layers with zero GPU work:

- Code: `scripts/manga/assemble_from_bank.py` (implements MANGA_LAYER_RENDER_CONTRACT_SPEC §4 taxonomy/z-order + §10 math verbatim; slots under V5 §7 layer semantics; reuses `phoenix_v4` `render_bubbles_onto_panel` for lettering) + `scripts/manga/make_object_sprite.py` (INTERIM sprite derivation via the same rembg lane as V4 cutouts) + `schemas/manga/assembly_manifest.schema.json` + 9 passing unit tests (`scripts/manga/tests/test_assemble_from_bank.py`).
- Manifest: `artifacts/manga/stillness_press__…/assembly_manifests/demo_alarm_metaphor_6p.yaml`
- Output: `artifacts/manga/stillness_press__…/assembled/demo_alarm_metaphor_6p/` — 6 bubbled panels (2.1–2.3MB each) + `demo_alarm_metaphor_6p_strip.jpg` (1.8MB) + `_provenance.json/.md` + `RESUME_COMMANDS.sh`.

**Layer provenance (honest):**

| Layer | Assets | Provenance |
|---|---|---|
| L0 backdrops | 3 kitchen plates (1.9–2.1MB) | **REAL** — April v4_render_cache, byte-verified LFS |
| L2 character | 5 Mira pose cutouts with alpha (1.7–2.3MB) | **REAL** — same cache |
| L1 wall alarm sprite | 1 (reused at 3 scales) | **INTERIM** — rembg-cut from REAL composed_v3 seg_025; replacement command emitted |
| L3 kettle sprite | 1 (reused, incl. flip_h) | **INTERIM** — cut from REAL seg_027; replacement command emitted |
| L4 steam | 1 | **INTERIM** — procedural PIL; §4.5 black-backdrop render command emitted |
| Lettering | real ep_001 captions + dialogue | REAL script text, existing bubble_render |

**Character consistency (instrumented):** `qa_face_distance` pairwise across the 4 face-bearing L2 layers: **0.068–0.245 cosine distance (mean 0.165)** — all pairs deep inside the ≤0.4 same-identity band. (Caveat: facenet is photo-trained; treat as directional until the pro-bar protocol lands.)

**Honest defects visible in the demo** (what REAL banked assets fix): INTERIM kettle's metallic register clashes with the iyashikei watercolor; flat-cut sprite bottom edge floats; L2 cutout box edges visible at table intersections (the known cutout-precision problem, V5's decompose addresses it); L0 plates contain baked-in kettles (bank plates need object-free variants per §8.2 scene_inventory).

**GPU batch:** Pearl Star unreachable → the bounded render batch (kettle, 3 cup states, alarm, steam = ~8 images) is **queued as exact commands** in `RESUME_COMMANDS.sh`, low-priority per OPD-20260629-003. No interim layer is presented as final art.

---

## 7. Full verifier tables

### 7.1 V1 locale × chain-stage truth table

(as returned by V1, refutation-adjusted)

| Locale | (A) Research | (B) Per-locale genre allocation | (C) Series plans |
|---|---|---|---|
| en_US | RESEARCHED (us-persona-topic-market-fit) | ABSENT (global matrix + lane share only) | CONFIG-EXISTS (268 plans) |
| ja_JP | RESEARCHED (asian triad + CJK plan §1-6) | ABSENT (share 70% encoded; genre mix not) | CONFIG-EXISTS (269) |
| zh_CN | RESEARCHED | ABSENT | CONFIG-EXISTS (268; 69 blocked_lora) |
| zh_TW | RESEARCHED | ABSENT | CONFIG-EXISTS (274; registry omits manga track — flag C-1) |
| zh_HK | RESEARCHED (deferred per CJK plan) | ABSENT | ABSENT |
| ko_KR | RESEARCHED | ABSENT | CONFIG-EXISTS (266; whole-locale hold) |
| fr_FR | RESEARCHED (EU doc §3) | ABSENT | ABSENT (registry omits manga track — flag C-2) |
| de_DE | RESEARCHED (EU doc §4) | ABSENT | ABSENT |
| es_ES | RESEARCHED (EU doc §2) | ABSENT | ABSENT |
| es_US | RESEARCHED (EU doc §1) | ABSENT | ABSENT |
| it_IT | **ABSENT** | ABSENT | ABSENT |
| hu_HU | RESEARCHED (low-confidence, EU doc §5) | ABSENT | ABSENT |
| zh_SG | **ABSENT** | ABSENT | ABSENT |

### 7.2 R8 master grid

| Locale | Brands planned | Series plans | Titled | Episodes authored | Series rendered-real | Catalog CSV |
|---|---|---|---|---|---|---|
| en_US | 37/37 | 268 | 268 | 7 | 1 (+2 contact sheets) | YES |
| ja_JP | 36/37 | 269 | 268 | 1 | 0 | YES |
| ko_KR | 36/37 | 266 | 266 | 0 | 0 | NO (hold) |
| zh_CN | 36/37 | 268 | 268 | 1 | 0 | YES (69 blocked_lora) |
| zh_TW | 37/37 | 274 | 274 | 1 | 0 | YES |
| es_US / es_ES / fr_FR / de_DE / it_IT / hu_HU / zh_SG / zh_HK | 0/37 | 0 | 0 | 0 | 0 | NO |

### 7.3 Refutation ledger (33 refuters; every CODE-WIRED+ finding)

- CONFIRMED: 15 (incl. 37-brand canon, 1,345 plans, 1,344 titles, 16 authored scripts, orchestrator wiring, bestseller_gate role, PuLID workflow JSONs, render-real census)
- DOWNGRADED: 13 (vessels loader→CONFIG-EXISTS; qa_face_distance→CONFIG-EXISTS; per-locale plan implementation→CONFIG-EXISTS; "19 QC gates" trimmed; sleep/somatic TSV claims corrected; others)
- REFUTED: 4 (teacher-named violation — false; "no live orchestrator" — false, it exists; internal 5-script judgment as PROVEN-AT-BAR — internal-only with metric errors; copy-across as CODE-WIRED — SPECCED)
- 2 refuter agents failed structured output and returned null (their findings retain the verifier layer, flagged unadjudicated: V3 finding #2 quality-grade table; V5 finding #5 authored-episode count — the count was independently re-verified by V2's ledger).

**Evidence root:** full machine findings in `artifacts/qa/manga_vision_conformance_20260703.tsv`; raw fan-out results retained in session transcript (41 agents, 1.48M tokens).

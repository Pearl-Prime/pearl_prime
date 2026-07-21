# Pearl Prime Perfect Books Spec

**Date:** 2026-07-18  
**Authority inputs:** `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`, `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`, `artifacts/qa/pearl_prime_100book_analysis_20260718/ANALYSIS_REPORT.md`  
**Goal:** Make *every* production catalog book reach `system working`, and keep the system at Layer-4 `bestseller register` via recurring blind-10 — using enforceable mechanisms, not hope.

**Meta-rule:** Every lesson below must land as (1) a CI hard gate, (2) a can't-bypass default, or (3) a CLAUDE.md binding rule. Memory/docs alone are insufficient.

---

## 0. Acceptance contract (non-negotiable)

| Layer | Term | Proof | Owner |
|---|---|---|---|
| 1 | structurally clear | All Layer-1 hard gates PASS under production chord | Pearl_Dev / CI |
| 2 | authored candidate | Layer 1 + Layer 2 WARN budget (≤1 WARN) | Pearl_Dev |
| 3 | system working | Pearl_Editor ONTGP on Ch1 / mid / last (≥3 chapters) | Pearl_Editor |
| 4 | bestseller register | Operator blind-10 on rolling N=10 (≥7 assembled-no, ≥6 shelf-yes) | Operator + Pearl_PM |

**Forbidden language in closeouts/PRs without the matching layer proof:** "bestseller", "shippable", "production-ready", "register-PASS implies quality".

**Enforce (Q-ENFORCE-02):** CI grep on changed `CLOSEOUT*.md` / PR bodies: if `bestseller|register-?PASS|shippable` present, require an acceptance-layer term (`structurally clear|authored candidate|system working|bestseller register|Layer [1-4]`). **BLOCK** merge when missing.

---

## 1. Definition of "perfect" for a single book

A book is **catalog-perfect** only when:

1. Rendered with four-piece chord: `--pipeline-mode spine --quality-profile production --exercise-journeys` (+ `--render-book`).
2. Layer 1 PASS including `register_gate` (treat register as hard for catalog ship — today production already blocks on it).
3. Layer 2 ≤1 WARN.
4. Layer 3 ONTGP PASS on sampled chapters (human or Pearl_Editor — **not** keyword proxy).
5. No visible template seam in a 3-chapter spot check (exercise wrapper / shift phrase / foreign-persona registry bleed).

A **system** is perfect only when Layer 4 blind-10 is PASS on the current rolling window.

---

## 2. Ownership split (stop the wrong lever)

| Problem class | Owner | Wrong lever (banned) |
|---|---|---|
| Thin / missing atoms, foreign persona bleed, shallow STORY pools | Pearl_Editor + atom banks | Tuning composer topology |
| Inter-atom cohesion, chapter open Orient, motif/tool ledger | Flagship **line-edit lane** (Layer 3) | "Improve register_gate for catalog scale" |
| Renderer artifacts, F2 slots, injectors, F14 regressions | Pearl_Dev | Padding / dwell-beat injectors on default path |
| Catalog claims / acceptance language | Pearl_PM + CI | Counting gate PASSes as bestsellers |

**CLAUDE.md already bans composer-as-flagship-lever.** Keep it. Add: any PR whose description says "improve catalog register" without a Layer-3 packet **fails Q-ENFORCE-02-class review**.

---

## 3. Enforceable mechanisms (build list)

### A. Defaults that cannot be bypassed

| ID | Mechanism | Enforcement |
|---|---|---|
| D1 | Production render CLI defaults remain `spine` + `production`; `--exercise-journeys` required for catalog ship scripts | `scripts/ci/check_canonical_pipeline_path.py` BLOCK (exists); extend to `batch_catalog_epubs.py` / release wrappers |
| D2 | No post-render one-line beat injectors / word-floor padders on spine | Keep #4566 disable; F14 HARD (#46583); add regression test if `strengthen_register_craft_output` re-gains default-path calls |
| D3 | `quality-profile=draft/debug` outputs cannot enter catalog manifests / R2 ship paths | Gate in `batch_catalog_epubs.py` + manifest schema: reject `quality_profile != production|flagship` |
| D4 | Tuple must `check_tuple_viability` PASS before Stage 1 | Already hard; publish weekly viable-matrix artifact as catalog eligibility SSOT |

### B. New / tightened CI hard gates

| ID | Gate | Threshold | Blocks |
|---|---|---|---|
| G-F1H | Templated paragraph clusters (register F1) | HARD_FAIL when any cluster size ≥ 6 chapters (today often FAIL advisory-ish in mix — promote catalog ship to hard) | Catalog ship |
| G-WRAP | Exercise-wrapper spam | HARD_FAIL if same wrapper stem (e.g. "Now we are going to shift") appears in ≥ 4 chapters | Catalog ship |
| G-DEF4 | Foreign-persona registry sections | HARD_FAIL if render log / audit records DEFECT4 drops for the active `persona_id` above N=0 on production (fix bank routing; do not silence the detector) | Catalog ship |
| G-ORIENT | Chapter-1 Orient machine approx | WARN→escalate: Ch1 first 120 words must contain ≥1 body/scene anchor from approved lexicon OR SCENE atom provenance | Authored-candidate eligibility |
| G-ACCENT | Accent capability gaps | Production already blocks; add preflight matrix job that fails weekly if top-N catalog cells have `no_supply_pool` for budgeted accents | Catalog planning |
| G-CLAIM | Closeout claim language | Q-ENFORCE-02 regex BLOCK | PR merge |
| G-LAYER | Manifest acceptance column | Every shipped EPUB row must carry `acceptance_layer` enum; default `path_works`; shipping as `system working` without Layer-3 artifact path → BLOCK | Release |

### C. Content / bank completeness (upstream of composer)

| ID | Requirement | Enforcement |
|---|---|---|
| C1 | Every catalog persona×topic×engine in the ship matrix has STORY pool ≥ `min_story_pool_size` with required emotional bands | Tuple viability (exists); add CI on `config/catalog` ship lists vs viability PASS |
| C2 | Per-cell EXERCISE bank coverage for production (EXERCISE-BANK-RESOLUTION-01) — no silent practice_library-only books on flagship cells | Promote warning to HOLD/FAIL under production for flagship brand cells |
| C3 | Accent banks (`EXTERNAL_STORY`, `AUTHOR_COMMENTARY`, `WISDOM_ESSENCE`, `CITED_EVIDENCE`) stocked per topic for production budgets | Accent planner anti-spam already fails closed; track fill rate in weekly report |
| C4 | Kill Gen-Z-only registry depth as default fallback for other personas | Routing fix + G-DEF4 |

### D. Line-edit lane (the actual flagship register lever)

| ID | Process | Cadence | Artifact |
|---|---|---|---|
| L1 | Pick 1–3 flagship cells per brand (persona×topic×engine) | Per quarter + after any render-hardening merge | `artifacts/qa/flagship_line_edit/<date>/` |
| L2 | Human/Pearl_Editor ONTGP on Ch1, Ch5/6, last | Same | `ONTGP_VERDICT.md` with PASS/WEAK/FAIL per dimension |
| L3 | Fix via atom rewrite / seam paragraphs / chapter open — **not** composer retune unless ONTGP proves composer bottleneck | Same | Linked PR with acceptance layer `system working` only after L2 PASS |
| L4 | Promote winning seams into banks (reusable atoms), not one-off manuscript patches only | Same | Atom PRs |

### E. System-level Layer 4

| ID | Process | Enforcement |
|---|---|---|
| B1 | Operator blind-10 per `docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md` / `docs/PEARL_PRIME_BLIND_10_OPERATOR_GUIDE.md` | Pearl_PM calendar; catalog freeze if FAIL |
| B2 | Rolling window: every 10 newly shipped production books OR quarterly | Checklist in release contract |
| B3 | Blind-10 FAIL → open line-edit lane + bank tickets; **composer retune banned** as first response | CLAUDE.md + PM checklist |

---

## 4. Target SLOs (catalog)

Within one quarter of landing G-/D-/C- items:

| SLO | Target |
|---|---|
| Production-chord ship matrix cells Layer 1 + register PASS | ≥ 95% |
| Authored candidate among ships | ≥ 90% |
| Flagship cells `system working` (Layer 3) | 100% of designated flagships |
| Blind-10 (Layer 4) | PASS (≥7/10 not-assembled-feel; ≥6/10 shelf) |
| Unique persona×topic in active catalog matrix | Explicit matrix file; no silent skew to one persona |

---

## 5. Sequencing (smallest durable path)

1. **Ship G-CLAIM + G-LAYER** (stop lying in closeouts / manifests).  
2. **Ship G-WRAP + G-DEF4** (kill visible machinery / foreign persona bleed).  
3. **C1–C4 bank fill** for the published ship matrix (viability + accents + exercises).  
4. **Stand up L1–L4 line-edit lane** on 3 flagship cells; earn first true `system working`.  
5. **Run B1 blind-10** on the next 10 production ships; calibrate.  
6. Only then expand catalog breadth — diversity without Layer 3/4 is vanity count.

---

## 6. Explicit non-goals

- Do not weaken F14, chord CI, or tuple viability to improve pass rates.
- Do not re-enable dwell-beat / word-floor injectors on the default spine path.
- Do not treat heuristic ONTGP keyword proxies as Layer 3.
- Do not call a 100-book gate dashboard "bestseller validation."

---

## 7. Traceability to 2026-07-18 corpus findings

| Finding | Spec control |
|---|---|
| 0 / 100 bestseller register; 0 / 12 shelf proxy | B1–B3, acceptance contract |
| Layer-1 strict ~35%; register ~54% | D1–D4, G-F1H, C1–C3 |
| F6/F7/F1/F2/F4 dominate register fails | G-F1H, G-WRAP, line-edit lane (not composer churn) |
| DEFECT4 Gen-Z registry on other personas | G-DEF4, C4 |
| Accent `no_supply_pool` hard-stops | G-ACCENT, C3 |
| Disk corpus persona skew | Catalog eligibility matrix + C1; diversity SLO |
| Strong local prose + weak whole-book cohesion | L1–L4 line-edit lane |

---

## 8. Done when

- [x] Q-ENFORCE-02 (G-CLAIM) merged and required — Wave-1 2026-07-18 (`check_acceptance_claim_language.py` + Drift detectors)  
- [x] Ship manifests carry `acceptance_layer` (G-LAYER) — Wave-1 (`batch_catalog_epubs.py` + `check_catalog_manifest_acceptance_layer.py`)  
- [x] G-WRAP + G-DEF4 blocking on production ship path — Wave-1 (register F16 + enrichment `defect4_drops` + production SystemExit)  
- [ ] ≥3 flagship cells have Layer-3 `ONTGP_VERDICT.md` = PASS (`system working`) — Wave-2 attempted 3/3, all real evidenced **FAIL** (`SYSTEM_WORKING_CELLS=0`); stays unticked, not rounded up  
- [ ] One operator blind-10 PASS recorded under `artifacts/qa/` — Wave-2 Lane 05 **prepared** the packet (`artifacts/qa/perfect_books_wave2_20260718/blind10_packet/`, 10/10 real Layer-1-ceiling books, operator-unread); Layer-4 PENDING; stays unticked (operator-only box)  
- [x] G-F1H templated-cluster HARD_FAIL escalation — Wave-2 2026-07-18 (`scripts/ci/check_f1h_templated_cluster_hard.py`, 4/4 unit tests, mutation-checked, wired gate 38)  
- [x] G-ORIENT Ch1 body/scene anchor check — Wave-2 2026-07-18 (`scripts/ci/check_orient_ch1_scene_anchor.py` + `config/quality/orient_body_scene_lexicon.yaml` v1, 6/6 unit tests, mutation-checked, wired gate 39; lexicon is v1/58-words/English-only, recommend widening)  
- [x] G-ACCENT weekly accent-fill preflight matrix — Wave-2 2026-07-18 (`scripts/ci/check_accent_supply_preflight.py` + `.github/workflows/accent-supply-preflight.yml`, 5/5 unit tests, mutation-checked, wired gate 40; live run found 14/20 top cells with a real `no_supply_pool` gap — bank-fill signal, not a Lane-04 defect)  
- [x] CLAUDE.md still states gate-PASS ≠ bestseller; composer ≠ flagship lever — reinforced with G-CLAIM / G-LAYER pointers  

**Wave-1 implementation closeout:** `IMPLEMENTATION_CLOSEOUT.md` (`SIGNAL=pearl-prime-perfect-spec-impl=PARTIAL`).
**Wave-2 final audit closeout (offline, pending GitHub replay):** `artifacts/qa/perfect_books_wave2_20260718/FINAL_AUDIT.md` (`SIGNAL=perfect-books-wave2-final=PARTIAL`). Landed offline on `pearlstar_offline`, NOT yet on `origin/main` (GitHub still 403-suspended at time of this wave).

Until Layer-3/4 boxes above are checked, the honest catalog claim is at most **authored candidate** for machine-clean cells — never **bestseller register**.

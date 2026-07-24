# Pearl Prime Book Pipeline Audit — Bestseller Register + Cohesive Flow + Atom Utilization

**Date:** 2026-07-22  
**Lane:** `pearl-prime-bestseller-cohesion-atom-audit-20260722`  
**Verified against:** `origin/main` @ `a08b8af17b4e7b37ac36be7d4c1c8f6049e5ee37`  
**Authority taxonomy:** `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (4 layers) + CLAUDE.md Bestseller Quality Anti-Drift Doctrine  
**Method precedent:** six-layer honesty / adversarially refuted claims (manga audit methodology ported to books)  
**Evidence root:** `artifacts/qa/pearl_prime_pipeline_audit_20260722/evidence/`

> **Status language used below is scorecard-exact.** A `register_gate` PASS is at most **structurally clear**. No sampled non-flagship book is called bestseller, shippable, or done off gate-PASS alone.

---

## 0. Pre-requisite + stale-state reconciliation

| Check | Result |
|---|---|
| Reach `origin/main` | YES — tip `a08b8af17b…` (2026-07-22). `git fetch` succeeded. |
| Open PR covering this exact audit | **No duplicate audit PR.** Open `#56` is `docs(piper): Pearl Prime pipeline audit prompt` (prompt pack only). This report is the execution deliverable. |
| `check_research_fit_honesty.py` | EXISTS; wired advisory into Drift detectors + readiness gates 34 (verified). |
| `check_book_story_authored.py` | EXISTS; wired advisory into Drift detectors + readiness gates 35 (verified). |
| `atom_coverage_audit.py` | EXISTS; ran clean 2026-07-22 (see Axis 3). |
| Yesterday's lane `#9` / `280597dacf` | **MERGED** 2026-07-21 — research_fit honesty + story-authored + acceptance stamp + courage atoms. |
| PROGRAM_STATE LAST VERIFIED | Was **2026-07-15** @ `8a0b09f9b0…` — **stale by ≥1 week of merges**. Refreshed in this PR for Flagship / Production-Gate / Books-first / Open-PR rows that this audit re-derived. |
| Old `#5237` / `#5206` | **Do not resolve** on this repo (`gh pr view` → could not resolve). Numbers are stale; see Axis 2 for keyword search. |
| Memory "~97.7% en_US coverage" | **Not reproducible as stated** against today's `atom_coverage_audit.py` full topic list (57 topics → 29.8%). Core production 15 topics → **100%**. See Axis 3. |

---

## Axis 1 — Bestseller register

### 1.1 Flagship golden (the only PROVEN-AT-BAR book)

| Check | Result |
|---|---|
| Golden present | `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt` |
| Metadata status | `ratified` (`CANONICAL_FLAGSHIP_BOOK_METADATA.json`) |
| SHA match metadata | **YES** — `e015ddc30b86ad398401c1bab5a8a37bc8205aa8b8493fc96d944d815fdd5184` |
| Words / bytes | 21,729 / 122,512 (match metadata) |
| Self-parity gate | `check_flagship_book_parity.py --snapshot full --full-from-file <golden>` → **BYTE-IDENTICAL** (exit 0) |
| Ch1 golden | SHA match metadata — intact |

**Note on full pipeline rebuild:** invoking the parity gate *without* `--full-from-file` re-runs `run_pipeline.py` (≤600s). This audit verified frozen-golden integrity + gate wiring via self-parity; it did **not** claim a fresh deterministic rebuild byte-match (budget). That is a separate CI job responsibility.

**Live register re-score of the golden (honesty check):**  
`evaluate_register(..., quality_profile=production)` on the frozen golden → **FAIL** with `F6×1`, `F7×9`, F14 share **8.98%** (30/334 body paras) — under the 25% HARD ceiling.  
**Acceptance layer for the flagship remains `bestseller register` (Layer 4)** because operator blind-read **OPD-20260707-FLAGSHIP-L4** already approved it; machine re-score cannot revoke a Layer-4 human verdict. Finding: **register detectors have drifted relative to the ratified golden** (F6/F7 fire on the PROVEN-AT-BAR book). Do **not** "fix" by retuning thresholds in this lane — surface as:

> **Q-AUDIT-REG-01 (operator-tier):** Should F6/F7 be recalibrated against the ratified flagship golden, or should the golden be treated as a grandfathered Layer-4 exception in CI messaging?  
> **Recommended default:** leave HARD F14 + F2 alone; make F6/F7 fail-noise on the golden an explicit allowlist / informational diff in the parity job, and schedule a **line-edit lane** if F7 density is a real craft issue rather than a detector false positive.

Evidence: `evidence/flagship_golden_integrity.txt`, `evidence/flagship_parity_self.txt`, `evidence/f14_share_computed.json`.

### 1.2 Non-flagship samples (live gate re-score)

Samples chosen from recent production-profile proof roots (four-piece chord artifacts on disk; not restitched as "fresh proof" of rebuild — gate-checked live on existing `book.txt`).

| Cell | Words | `register_gate` (live) | F14 share | F-codes (live) | `bestseller_craft` | `research_fit` | Scorecard layer (honest) |
|---|---:|---|---:|---|---:|---|---|
| `corporate_managers × anxiety × comparison` (`pearl_prime_next_micro_wave_20260716/…F006`) | 19,413 | **PASS** | **7.14%** (44/616) | none | 0.6754 PASS | **UNBOUND** (missing/`{}` legacy_planner) | **structurally clear only** (research_fit cap) — NOT authored candidate |
| `corporate_managers × burnout × overwhelm` (`bestseller_register_20260719/batch9/…`) | 23,337 | **WARN** | *uninformative* (0/12 — single-block chapters; see §2.3) | F13×8 WARN | (no quality_summary) / editorial ontgp 0.66 | **UNBOUND** empty `{}` — honesty FAIL | **path works** / structurally_clear_only — NOT authored candidate |
| `healthcare_rns × burnout` seed 43006 (`random_2h_books/…43006`) | 23,039 | **WARN** | *uninformative* (0/12 single-block) | F13×3 WARN | 0.6869 PASS | **BOUND** `research_fit_v1` (spine_pins=4) | **path works** — Layer 1 fails (`chapter_flow` FAIL, book_quality Reject) despite bound research_fit |

**Stored vs live drift:** burnout sample's *stored* `register_gate_report.json` was FAIL (F13×8 + **F15 FAIL**); live re-score is WARN (F13 only). Gate code moved; do not trust old report JSON without re-run.

**Honesty / story-authored gates (yesterday's rails):**

| Cell | `check_research_fit_honesty` | `check_book_story_authored` | Stamp |
|---|---|---|---|
| anxiety×comparison | FAIL — missing `research_fit` key | unbound → `structurally_clear_only` | stamped |
| burnout×overwhelm | FAIL — empty `{}` no skip_reason | unbound → `structurally_clear_only` | stamped by gate run |
| healthcare burnout 43006 | PASS (honest bound) | **bound** | `{research_fit_bound: true}` |

**Critical drift confirmation (seed-43001 class):** a book can **PASS register_gate** (anxiety×comparison) and still have **zero character through-line** because `research_fit` never bound. That is exactly the operator finding the 2026-07-21 lane mechanized — and it is still present on non-courage cells without story_atoms banks / without pipeline stamping.

**ONTGP (editorial proxy scores — not Layer-3 Pearl_Editor sample reviews):**

| Cell | editorial `ontgp_score` | notes |
|---|---:|---|
| anxiety×comparison | 0.6754 | grade PASS; **not** a logged Layer-3 ONTGP sample review |
| burnout×overwhelm | 0.66 | grade PASS |
| healthcare 43006 | 0.6869 | grade NEEDS_REVISION; flow_score 0.0 |

None of these may be reported as `system working` — no `ontgp_sample_review` artifact was supplied to `acceptance_layer.compute_acceptance_layer`.

Evidence: `evidence/sample_gate_bundle.json`, `evidence/register_live_*.json`, `evidence/f14_share_computed.json`.

### 1.3 Axis-1 layer summary

- **Flagship:** Layer 4 **bestseller register** (operator-ratified); golden byte-frozen; machine register now noisy on F6/F7.
- **Non-flagship samples:** at best **structurally clear only** (research_fit cap) or **path works** (hard gate fails). **Zero** sampled cells reach `authored candidate` / `system working` / `bestseller register` under the scorecard.

---

## Axis 2 — Cohesive flow

### 2.1 Live state of the old "atom-cohesion" / "#5237" lane

| Claim from stale PROGRAM_STATE (07-15) | Live re-derivation (2026-07-22) |
|---|---|
| `#5237` OPEN/RED/DIRTY | **PR number does not resolve** on this repo. Keyword search for `atom-cohesion` / `cohesion craft` / `thesis de-templating` did not surface a live successor PR under those titles (gh auth intermittent 401 on some queries; successful queries returned unrelated/localization/piper PRs). |
| `#5206` OPEN/DIRTY bestseller-conformance | **PR number does not resolve.** Treat as historical evidence only. |
| Q1 thesis de-templating OPEN | **PARTIALLY LANDED, not closed.** `chapter_thesis_bank.yaml` now has 7 engine columns + optional `topics:` overlay (8 topics). Baseline is still `intent → engine`. Overlay is thin vs catalog. |
| Q2 adjacency selector OPEN | **Still open / not landed as a craft gate.** Prompt remains gated in `docs/sessions/cohesion_chunk_prompts_20260630/cohesion_chunk_2_adjacency_selector.md`. No hard adjacency-selector CI gate found. |
| Skeleton freeze blocking Q1 | **Lifted** (`config/governance/skeleton_freeze.yaml` → `active: false`, lifted 2026-07-01). Q1 fire-gate is met; work is not fully executed. |

### 2.2 Thesis templating (Q1) — still a live lever

Bank contract (`config/planning/chapter_thesis_bank.yaml` header): lookup is (1) `topics[topic][intent][engine]` overlay → (2) `intents[intent][engine]` baseline.  
**Topics overlay present for only 8 topics** (`anxiety`, `boundaries`, `burnout`, `grief`, `overthinking`, `perfectionism`, `procrastination`, `self_worth`) — not catalog-wide.

**Cross-cell repetition still observable in rendered prose:** comparing chapter opens across `anxiety×comparison` vs `anxiety×overwhelm` (same persona) found **8 identical chapter-open paragraphs** shared across books (e.g. "Your direct report is struggling…", "The project deadline is two weeks away…" ×3). That is list-like reuse across cells, not topic-distinct thesis craft.

### 2.3 Dwell / integration pacing

| Mechanism | State |
|---|---|
| F13 dwell-starvation detector | **EXISTS** in `register_gate.py` (`_detect_f13_dwell_starvation`) — severity **WARN only; never HARD**. Comment in-file: F13 "only ever emits WARN (never gates)". |
| F14 beat-line ceiling | **EXISTS + HARD_FAIL** at 25% — the choppy-injector control. Wired. |
| Dedicated dwell craft / adjacency gate (Q2) | **ABSENT as a blocking gate.** Prompt authored; not CI-hard. |
| Operator concern "race no dwell" | **Still structurally open.** Samples show F13 WARN clusters (burnout×8, healthcare×3) while books can still register-PASS or WARN without hard block. |

### 2.4 Per-sample cohesion read

| Cell | F14 | Plain-language cohesion |
|---|---:|---|
| anxiety×comparison | 7.14% (PASS ceiling) | Paragraph-broken; register clean. Still reads **assembled / templated across cells** (shared opens with sibling anxiety×overwhelm). research_fit unbound → no character through-line. Representative lines: "Your phone buzzes during dinner…"; "The peer feedback came back…"; "Your direct report is struggling…". |
| burnout×overwhelm | F14 metric **broken by format** (12 giant chapter blobs → 12 body paras) | Dense single-block chapters defeat beat-line math. F13 WARN×8 = insight stacking without dwell. Opens are stronger/scene-led ("This Is Not Tiredness") but integration pacing still WARN-noisy. |
| healthcare 43006 | same single-block F14 caveat | research_fit **bound** (character spine present) yet chapter_flow FAIL / book_quality Reject — **atoms bound ≠ Layer-1 clear**. |

**Twelve-shape / word-mass gap:** flagship deliberately retargeted to `extended_book_2h` (~21.7k). A `deep_book_6h` fixture still reaches ~61k (`artifacts/qa/f1_depth_dedup_verify_20260615/fixed/deep_book_6h/book.txt`). The architecture diagnosis in `COHESIVE_FLOW_12x10x5_ARCHITECTURE_AUDIT.md` (depth-pass stacking vs more chapters) **still holds** — word mass is not an atom-count problem; 6h cohesion risk remains an assembly/depth-pass issue. Not re-litigated here.

### 2.5 Axis-2 layer summary

Cohesive-flow system state: **CONFIG-EXISTS / CODE-WIRED for F13(WARN)+F14(HARD)**; **NOT PROVEN-AT-BAR** for catalog cohesion. Q1 partially landed; Q2 not landed. Highest remaining craft lever remains **topic-keyed thesis authoring + adjacency/dwell craft** — not composer retuning.

---

## Axis 3 — Atom utilization

### 3.1 Fresh `atom_coverage_audit.py` (2026-07-22)

| Scope | Complete | Total | Coverage |
|---|---:|---:|---:|
| **All topics in canonical list (57)** × 13 personas | 221 | 741 | **29.8%** |
| **Core production 15 topics** × 13 personas | 195 | 195 | **100.0%** |
| Core 17 (15 + adhd_focus + mindfulness) | 221 | 221 | **100.0%** |

Evidence: `evidence/atom_coverage/atom_coverage_report.md`, `atom_coverage_matrix.json`.

**How to say this honestly (one number with scope):**

> **100% CANONICAL.txt presence across 13 personas × 15 core production topics** (anxiety…somatic_healing), measured by `scripts/inventory/atom_coverage_audit.py` on 2026-07-22.  
> **29.8%** if the audit's full 57-topic list is used (includes brand/specialty topics with zero banks).  
> The memory figure "~97.7%" is **not** what this script emits today on the full topic list — do not cite it.

This metric is **listing/bank existence** (CANONICAL.txt present), **not** "wired into render" and **not** "consumed by a real research_fit bind."

### 3.2 Listing vs bank vs wired vs consumed

| Layer | Finding |
|---|---|
| Listing exists | ~1,519 en_US listings (PROGRAM_STATE) — metadata, not EPUBs. |
| Atom bank exists (canonical) | Core 15 topics: 100% persona×topic CANONICAL presence. |
| story_atoms bank exists | **Only 6 personas**, **9 persona×topic cells** total (see §3.3). |
| Wired into render path | `build_story_schedule()` / story_planner loads `story_atoms/<persona>/anchored/<topic>/<engine>/…`. Missing dir → `[]` → skip. |
| Actually consumed | Only cells with banks **and** a planner path that stamps structured `research_fit`. Healthcare 43006 shows bound consumption; anxiety×comparison / burnout×overwhelm show **not consumed** (empty/missing). Readiness comments still note research_fit stamping is incomplete on some pipeline paths (advisory gates 34–35). |

### 3.3 story_atoms breadth (re-verified)

Personas with any `anchored/` bank (unchanged set of 6):  
`educators`, `first_responders`, `gen_z_professionals`, `healthcare_rns`, `millennial_women_professionals`, `working_parents`.

| Persona × topic | Engines | `v*.txt` files |
|---|---|---:|
| educators × anxiety | overwhelm | 12 |
| first_responders × burnout | overwhelm | 48 |
| gen_z_professionals × anxiety | overwhelm | 143 |
| gen_z_professionals × financial_anxiety | spiral | 48 |
| healthcare_rns × burnout | overwhelm | 55 |
| healthcare_rns × financial_stress | overwhelm | 48 |
| millennial_women_professionals × anxiety | watcher, overwhelm | 36 |
| millennial_women_professionals × **courage** | false_alarm | **16** (added by 07-21 lane) |
| working_parents × anxiety | overwhelm | 16 |

**Still zero:** courage for every persona except millennial_women_professionals×false_alarm; corporate_managers story_atoms (entire persona); vast majority of topic×engine cells.  
Corporate_managers is the EPUB workhorse persona — and it has **no** story_atoms banks → research_fit skip/unbound by construction on those cells.

### 3.4 Dup-fill / variant-index failure mode

Spot-check of `enrichment_select.py` for `variant_index` / `dup_fill` / `purpose_fill` identifiers: **no current hits**. `InsufficientVariantsError` still exists (lines ~135, ~2433) — thin-pool raise path intact.  
**Cannot confirm from available tooling in this turn** whether a silent variant-index fill path still exists under another name; no regression reproduced. Status: **inconclusive / likely mitigated by InsufficientVariants hard-raise doctrine** — do not claim "fixed" without a purpose-fill audit harness.

### 3.5 Axis-3 layer summary

Atom banks for core topics: **CONFIG-EXISTS / largely present**. story_atoms character banks: **thin (9 cells)**. Utilization into research_fit: **partially wired, sparsely consumed**. Honest utilization statement is the scoped 100%/29.8% pair above — not "atoms are done."

---

## Cross-axis synthesis

| Interaction | Example from this audit |
|---|---|
| Axis-3 bank present, Axis-1 unbound | Canonical atoms exist for corporate_managers×anxiety, but **no story_atoms** → register can PASS while research_fit is empty → structurally_clear_only. |
| Axis-3 story_atoms present + consumed, Axis-1 still fails | healthcare×burnout 43006 is research_fit **bound** yet chapter_flow FAIL / book_quality Reject — binding ≠ shippable. |
| Axis-2 cohesion failures ↔ Axis-3 thin pools | Thesis baseline still intent→engine; topic overlay only 8 topics; cross-book identical opens persist. F13 WARN without HARD dwell gate. |
| Flagship vs catalog | One Layer-4 golden does not generalize; catalog samples never leave Layer 1 (or fail it). |

### Single highest-leverage next fix

**Author + wire `story_atoms` banks for the EPUB workhorse cells (start: `corporate_managers` × top engines/topics), and keep research_fit binding advisory→visible until operator flips `--strict`.**  

Rationale: composer retuning is doctrine-forbidden for register; F14 already HARD-blocks choppy injector class; the operator-visible hole is **books that gate-PASS without a character through-line**. That is atom authoring (story_atoms) + ensuring the planner stamps bind/skip honestly — not threshold churn. Secondary parallel craft lane (after banks exist for the cells you render): finish Q1 topic-thesis overlays for those topics + Q2 adjacency/dwell craft (F13→craft gate), then **line-edit lane** on flagship-class cells for Layer 3/4.

---

## Operator questions (not decided here)

| ID | Question | Recommended default |
|---|---|---|
| **Q-AUDIT-RF-01** | Promote `check_research_fit_honesty.py` / `check_book_story_authored.py` from advisory to hard-block on production renders? | **Keep advisory** until corporate_managers (and other EPUB personas) have story_atoms banks for the cells in the render queue; otherwise CI/red renders block the books-first micro-wave. Flip `--strict` per-queue when banks exist. |
| **Q-AUDIT-REG-01** | F6/F7 now FAIL the ratified flagship golden on live re-score. Recalibrate detectors, allowlist golden, or line-edit? | **Do not retune composer/register for catalog.** Prefer informational golden-diff + optional line-edit lane; leave F14/F2 HARD. |

---

## What this turn did NOT cover

- Full catalog EPUB re-render with four-piece chord (budget).
- Full `run_pipeline.py` flagship rebuild byte-parity (used frozen golden self-parity + SHA).
- Exhaustive purpose-fill / dup-fill dynamic reproduction.
- Blind-10 Layer-4 on any non-flagship cell.
- Locale atom coverage (en_US only).

---

## Evidence index

| Path | Contents |
|---|---|
| `evidence/flagship_golden_integrity.txt` | SHA/words/bytes vs metadata |
| `evidence/flagship_parity_self.txt` | parity gate self-check |
| `evidence/atom_coverage/*` | fresh coverage matrix + report |
| `evidence/f14_share_computed.json` | F14 shares + register verdicts |
| `evidence/sample_gate_bundle.json` | honesty/story-authored/quality bundle |
| `evidence/register_live_*.json` | per-sample live register dumps |
| `config/planning/chapter_thesis_bank.yaml` | thesis keying + topics overlay |
| `docs/sessions/cohesion_chunk_prompts_20260630/*` | Q1/Q2 backlog prompts |
| `scripts/run_production_readiness_gates.py` §34–35 | advisory wiring |
| `.github/workflows/drift-detectors.yml` | CI advisory wiring |

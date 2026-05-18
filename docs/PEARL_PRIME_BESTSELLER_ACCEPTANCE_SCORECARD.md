# Pearl Prime Bestseller Acceptance Scorecard

**Last updated:** 2026-05-18
**Owner:** Pearl_Architect (vision) + Pearl_PM (acceptance verdict)
**Status:** read-first for any Pearl_Prime agent session
**Authority:** This doc defines what "acceptance" means for a Pearl Prime book at each layer. It is the canonical answer to "is this shippable?" Other docs (`PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`, `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, `PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`) describe HOW the system attempts each layer. This doc describes WHEN we accept it.

---

## Why this doc exists

The system has many gates that say PASS. The operator has read books that PASS those gates and still don't feel like the bestseller register Pearl Prime is targeting (Body Keeps the Score, Waking the Tiger, The Myth of Normal, What My Bones Know register — NOT KDP indie workbook register).

Without an explicit acceptance contract, three things keep happening:
1. Agents optimize for "gate PASS" and think the work is done.
2. The operator reads a passing book and reacts ad-hoc.
3. The system has no way to encode "delivery-grade ≠ bestseller-grade" into a checkable verdict.

This scorecard fixes that by NAMING the acceptance stack and the status language.

---

## Status language (use exactly these terms)

| Term | Meaning |
|---|---|
| **path works** | The pipeline ran end-to-end and produced `book.txt` + reports. Necessary, not sufficient. |
| **structurally clear** | All hard-blocker gates PASS (Layer 1). The book is well-formed; no obvious defects. |
| **authored candidate** | Structural + advisory craft reviews (Layers 1+2) are clean enough that a sampled Pearl_Editor chapter review (Layer 3) is worth running. |
| **system working** | All four layers PASS for this single book. Shippable as one unit. |
| **bestseller register** | A separate higher bar, validated only via the blind-listening system benchmark (Layer 4) on a corpus of N books. Distinct from any single book's `system working` verdict. |

**Do not say "shippable" without naming the layer.** Saying "delivery-grade" without the verdict layer is a leak that produces confusion.

---

## Acceptance stack — 4 layers

A book progresses through these layers in order. **Failure at any layer stops the book from advancing to the next.** No layer is optional. No layer auto-implies the next.

### Layer 1 — Hard blockers (machine gates)

These are the structural floor. Failing any one of these means the render did not even produce a coherent book; do not pass to Layer 2.

| Gate | Source | Verdict |
|---|---|---|
| `chapter_flow` | `phoenix_v4/quality/chapter_flow_gate.py` → `chapter_flow_report.json` | PASS required |
| `book_quality_gate` | `phoenix_v4/quality/book_quality_gate.py` → `book_quality_report.json` (`release_band: Pass`) | Pass required |
| `scene_anti_genericity` | `phoenix_v4/qa/scene_anti_genericity_gate.py` + `scene_anchor_density_report.json` | PASS / 0 violations required |
| `bestseller_craft` | `phoenix_v4/quality/bestseller_craft_gate.py` → `quality_summary.bestseller_craft.overall_score ≥ 0.55` | PASS required under `--quality-profile production` |
| `ei_v2` | `phoenix_v4/quality/ei_v2/` → `ei_v2_report.json` | PASS required |
| `transformation_arc` | `transformation_heatmap.json` | PASS required |
| `book_pass` | `phoenix_v4/qa/book_pass_gate.py` → `book_pass_report.json` (identity_stages all true) | PASS required |

**If Layer 1 passes:** the book is `structurally clear`. Proceed to Layer 2.
**If Layer 1 fails:** the verdict is `path works` (if `book.txt` exists) OR `path broken` (if pipeline halted earlier). Route the failure to the specific gate's lane (atom authoring / gate tuning / renderer fix).

### Layer 2 — Advisory craft review (machine-assisted)

Run after Layer 1 passes. These produce signals, not blockers — but ≥2 WARNs across this layer should escalate to Layer 3 with explicit operator decision.

| Signal | Source | Threshold for concern |
|---|---|---|
| Editorial flow | `editorial_report.json` | overall_flow ≥ 0.5; any chapter flow < 0.3 = WARN |
| Bestseller editor | `bestseller_editor_report.json` (if emitted) | per-chapter craft score floor TBD per series; surface |
| Memorable lines | `memorable_line_report.json` | ≥ 11/12 chapters have ≥2 quotable lines; less = WARN |
| Thesis drift | grep `chapter_flow_report` for `MISSING_CLEAR_POINT` / `WEAK_TRANSITIONS` warnings | 0 errors, ≤1 warning total |
| Recurrence report | `quality_summary.recurrence_report` | stripped clusters ≤ 30; > 30 = WARN (suggests upstream bank monotony) |
| Frame governor | `quality_summary.frame_governance_chapters` | `frame_compliant: true` per chapter; any `hard_fail` = STOP |

**If Layer 2 is clean:** the book is `authored candidate`. Proceed to Layer 3.
**If Layer 2 has ≤1 WARN:** still `authored candidate`; note for operator.
**If Layer 2 has ≥2 WARNs:** STOP at this layer. Surface to operator with the specific signals + recommended remediation (atom diversity / chapter content fix / etc.).

### Layer 3 — Pearl_Editor sampled chapter review

A human (or Pearl_Editor agent acting as proxy) reads sampled chapters and applies the ONTGP (Orient → Name → Turn → Give → Pull) chapter-pass rule.

**Sampling rule:** read Ch1, Ch5 or Ch6, Ch11 (or last). 3 chapters minimum. If any of those reads thin, read 1-2 more.

**ONTGP chapter pass rule per chapter:**
- **Orient** — Does the chapter open with body / scene / context, not abstract concept? PASS / WEAK / FAIL
- **Name** — Is at least one specific mechanism named (with topic-vocab, not generic stress/feelings)? PASS / WEAK / FAIL
- **Turn** — Is there a felt pivot point where something shifts (a Long Drop, an awe-pullback, a named-character beat)? PASS / WEAK / FAIL
- **Give** — Is at least one concrete tool/practice/insight given the reader can hold? PASS / WEAK / FAIL
- **Pull** — Does the chapter close with traction into the next chapter (or, for final chapter, integration)? PASS / WEAK / FAIL

**Chapter passes ONTGP if:** 0 FAILs across all 5 dimensions AND ≤ 2 WEAKs.
**Book passes Layer 3 if:** all sampled chapters pass ONTGP.

**Verdict if Layer 3 passes:** the book is `system working`. Shippable as a single unit.
**Verdict if Layer 3 fails:** route specific failure dimension to lane:
- Orient FAIL → opening atom authoring (Pearl_Editor + Pearl_Writer)
- Name FAIL → mechanism vocab in persona+registry (Pearl_Editor)
- Turn FAIL → beat structure in chapter_script or enrichment (Pearl_Dev + Pearl_Architect)
- Give FAIL → practice atom authoring (Pearl_Editor)
- Pull FAIL → chapter end overlay or registry handoff (Pearl_Dev)

### Layer 4 — System-level benchmark

Distinct from any single book's acceptance. Validates that the SYSTEM is producing bestseller register at scale, not that any individual book is good.

**Use `FIRST_10_BOOKS_EVALUATION_PROTOCOL`** (or its renamed successor) on a rolling window of N most-recently-rendered books (recommend N=10).

**Operator-attended.** Cannot be delegated to an agent. The operator reads or listens to ~10 books cold and answers per-book:
- **Did it feel assembled?** (yes / no)
- **Would I sit it next to a trade-pub bestseller in the same shelf?** (yes / no)
- **What's the strongest dimension?** (free text)
- **What's the weakest dimension?** (free text)

**System-level PASS:** ≥ 7 of 10 books say `felt assembled = yes` AND ≥ 6 of 10 say `shelf-next-to-trade-pub = yes`.
**System-level WARN:** 5-6 of 10 either metric.
**System-level FAIL:** < 5 of 10 either metric.

**Cadence:** every N=10 books rendered, or quarterly minimum. Whichever comes first. Run is non-negotiable — without it, the gates gradient-descent into "passes all checks but feels generated."

**The blind-10 verdict drives:**
- Anchor corpus refresh (which trade-pub paragraphs we compare against)
- Register gate calibration (which dimensions of voice get tuned)
- Vision-canonical refinement (which non-negotiables need sharper phrasing)
- Atom bank priorities (which content axes need authoring)

---

## What machine gates can prove

| Question | Machine answer |
|---|---|
| Is the book well-formed (paragraphs, transitions, flow)? | Yes (Layer 1) |
| Is the topic vocabulary present? | Yes (Layer 1 chapter_flow + Layer 2 thesis cues) |
| Is the mechanism named at sec 2/5/9? | Yes (Layer 1 BESTSELLER-INJECTIONS-MANDATORY-01) |
| Are named characters consistent? | Yes (Layer 1 transformation_arc + scene_anchor) |
| Is the chapter cadence respected? | Yes (Layer 1 chapter_flow + Layer 2 editorial) |
| Does the book have ≥2 quotable lines per chapter? | Yes (Layer 2 memorable_lines) |
| Is the doctrine on-frame? | Yes (Layer 2 frame_governor) |

## What machine gates CANNOT prove

| Question | Why not |
|---|---|
| Does this read like Body Keeps the Score? | No machine corpus of "good" register exists yet (see closed-loop step C — anchor corpus) |
| Did I (the reader) feel something shift? | Pure phenomenology; requires human listen |
| Would I recommend this to a friend? | Pure preference; requires human read |
| Is the chapter-end memorable enough to quote in a podcast? | Requires editorial judgment beyond N-gram quotable count |
| Is the prose embodied or explanatory? | Approximated by Layer 2 editorial; truly answered only by Layer 3 |

**This is the doctrinal limit.** Machine gates can prove `structurally clear` and contribute to `authored candidate`. They cannot prove `system working` alone — that requires Layer 3 human read. They cannot prove `bestseller register` alone — that requires Layer 4 blind-10.

Treat the gates accordingly. A book that passes Layer 1 + Layer 2 is **NOT** automatically shippable. It is `authored candidate`. The Pearl_Editor sample at Layer 3 is the deciding read.

---

## How agents should use this doc

**Pearl_Prime CLI session** (rendering a book):
- Run the canonical CLI per `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md §570-577`.
- Emit `quality_summary.json` + all per-gate reports.
- Layer 1 verdict computable from those reports.
- Layer 2 advisory signals surface in closeout.
- **Do not say "shippable" — say "structurally clear" or "authored candidate" depending on layers reached.**

**Pearl_Editor sample session** (Layer 3 review):
- Read Ch1 / Ch5-6 / Ch11 + 1-2 more if any read thin.
- Apply ONTGP per chapter; record PASS/WEAK/FAIL per dimension.
- If all sampled chapters pass: emit `system working` verdict.
- If any chapter fails ONTGP: route fix to the lane named in Layer 3.

**Pearl_PM coordination** (closeout):
- Use the status language exactly. `path works` is not `structurally clear` is not `authored candidate` is not `system working` is not `bestseller register`. Each is a distinct verdict at a distinct layer.

**Pearl_Architect proposing changes**:
- Any new gate / spec / cap entry must say which layer it affects and which acceptance term it advances.
- "Improves bestseller_craft score" is a Layer 1 claim and DOES NOT imply Layer 3 or 4 improvement.

---

## Verification — apply this scorecard to one real book + the blind-10 set

The doc has no teeth until applied. Two immediate uses:

1. **Single-book test**: apply layers 1-3 to the 2hr × ahjan × gen_z × anxiety × en-US book at `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T131809Z_round5/`. Emit a verdict MD at `artifacts/qa/ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`. This is step (A) of the closed loop.

2. **System-level test**: queue Layer 4 blind-10 on the next batch of 10 rendered books. Operator-attended. This is step (F) of the closed loop.

Without (1), the scorecard is theoretical. Without (2) on a cadence, the system drifts.

---

## Cross-references

- Vision (the felt-quality target): `docs/PEARL_PRIME_BOOKS_VISION_AND_DELIVERY_AUDIT.md` (when authored)
- HOW the system attempts each layer: `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`, `docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md`
- Authority caps: `docs/PEARL_ARCHITECT_STATE.md` (BG-PR-09, BESTSELLER-INJECTIONS-MANDATORY-01, TEACHER-MODE-WRAPPER-SEMANTICS-01, EXERCISE-BANK-RESOLUTION-01, TEMPLATE-UNIVERSAL-01, AUTO-PLAN-SSOT-01, PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01)
- System-level benchmark: `docs/FIRST_10_BOOKS_EVALUATION_PROTOCOL.md`
- Anchor corpus (when authored): `artifacts/reference/trade_pub_anchors/`
- Register gate (when specced): `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md`

---

## Change log

- 2026-05-18: initial draft authored as part of closed-loop step (B). Built from operator's described 4-layer structure + the synthesis from `PEARL_PRIME_BOOKS_VISION_AND_DELIVERY_AUDIT.md`. Promote to canonical after first calibration verdict (closed-loop step A) lands.

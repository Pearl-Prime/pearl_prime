# Our System vs. The Patterns — Gap Analysis

**Compiled:** 2026-06-11 | **Authority:** Pearl_Research
**Reads:** `BESTSELLER_PATTERN_CATALOG.md` (the 14 patterns). **Feeds:** `FIT_OUR_ATOMS_TO_PATTERNS_PLAN.md`.
**Method:** each catalog pattern adjudicated against Phoenix assembly with **file-level evidence** + cross-reference to the 8 craft failures (`docs/PEARL_PRIME_CRAFT_DEPTH_OVERLAY_PROPOSAL_2026-06-06.md`) and the 7-axis audit (`artifacts/qa/pearl_prime_audit_2026-06-06.md`).

---

## 0. The architecture in one screen (so the gaps are legible)

Phoenix assembles a book as **arc × spine × slot-grid × atom-pools**:

- **Arc** (`SOURCE_OF_TRUTH/master_arcs/*.yaml`) declares, per book: `emotional_curve` (BAND per chapter), `emotional_temperature_curve`, `chapter_intent`, `reflection_strategy_sequence`, **`cost_chapter_index`**, `motif`, `resolution_type`, and — critically — **`emotional_role_sequence`** (recognition→destabilization→reframe→stabilization→integration).
- **Spine** = 12 chapters (universal at registry layer), each a **10-slot grid** (`SOMATIC_10_SLOT_GRID`, `beatmap_compile.py:42-53`) with STORY at sec 2/5/9.
- **Slot grid** per chapter (gold-ref, 6-slot rendered form): `[HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION]` (+ PIVOT, TAKEAWAY, THREAD, PERMISSION as structural-upgrade slots).
- **Atom pools**: STORY atoms carry **named-character `arc_position` tags** (`recognition | mechanism_proof | turning_point | embodiment`) from `character_roster.yaml` (20 characters × 4 positions); other slots fill from persona engine banks / teacher banks / practice library via overlay waterfall.

**The crucial structural fact** (from reading the gold-ref `atom_ids`, `artifacts/wave_refresh/gen_z_professionals__anxiety__overwhelm__F002__wave_refresh2_01.json`):

> The arc-beat metadata that the bestseller patterns require **already exists** (`emotional_role_sequence` = a value-polarity track; STORY `arc_position` = a turning-point ladder) — **but the assembler selects atoms by slot-fill + dedup, not by arc-beat continuity.** The named-character arc-positions land in scrambled order; the value-polarity track is declared but not bound to STORY selection.

This single fact is the root of **6 of the 8 craft failures** and **8 of the 14 pattern breaks**. The gaps below trace each pattern to this root (or to a distinct cause where it differs).

---

## 1. Evidence exhibits (referenced throughout)

**EXHIBIT A — the scrambled character/arc-position sequence.** Gold-ref `atom_ids`, chapters 0–11 (STORY slot only):

| Ch | STORY atom (gold-ref) | character | arc_position |
|---:|----------------------|-----------|--------------|
| 0 | `…overwhelm_EMBODIMENT_PRIYA_v19` | Priya | **embodiment** |
| 1 | `…grief_RECOGNITION_v01` | (none) | recognition |
| 2 | `…overwhelm_EMBODIMENT_ALEX_v16` | Alex | **embodiment** |
| 3 | `…shame_RECOGNITION_v04` | (none) | recognition |
| 4 | `…watcher_EMBODIMENT_v05` | (none) | **embodiment** |
| 5 | `…comparison_MECHANISM_PROOF_v03` | (none) | mechanism_proof |
| 6 | `…false_alarm_TURNING_POINT_v03` | (none) | turning_point |
| 7 | `…comparison_TURNING_POINT_v04` | (none) | turning_point |
| 8 | `…false_alarm_TURNING_POINT_v05` | (none) | turning_point |
| 9 | `…shame_RECOGNITION_v02` | (none) | recognition |
| 10 | `…watcher_TURNING_POINT_v04` | (none) | turning_point |
| 11 | `…overwhelm_TURNING_POINT_JORDAN_v12` | Jordan | turning_point |

**Reading:** A bestseller character arc must run recognition→mechanism_proof→turning_point→embodiment *monotonically*. Here, **embodiment appears in ch0/2/4 (the beginning), recognition appears in ch1/3/9 (scattered), turning_point clusters at the end** — the arc is **inverted and shuffled**. Priya appears once (ch0, already resolved at embodiment) and never recurs. No character has a through-line. This is the literal assembly cause of craft-failure **F6** ("characters as illustrations, not stories") and pattern breaks **P5, P6**.

**EXHIBIT B — the value-polarity track is declared but unbound.** Same file: `emotional_role_sequence` = `[recognition, destabilization, destabilization, reframe, stabilization, stabilization, reframe, destabilization, reframe, stabilization, …, integration]`. This *is* a Story-Grid polarity curve (P5). But the STORY `arc_position` in Exhibit A does **not** track it (ch0 role=recognition but STORY=embodiment; ch3 role=reframe but STORY=recognition). The two arc layers are computed independently. Pattern break **P5**.

**EXHIBIT C — the flat spine.** Same file, `chapter_slot_sequence`: the identical `[HOOK,SCENE,STORY,REFLECTION,EXERCISE,INTEGRATION]` array repeats for **all** chapters with no part-boundary, no phase label, no macro-shape. Pattern break **P2** (no five-part spine). (Note: this gold-ref ran 30 chapters at F001/F002; the 12-chapter spine has the same flatness.)

**EXHIBIT D — intra-chapter slot-order collapse + render leak.** Assembled sample `artifacts/research/bestseller_benchmark/samples/internal_deep6h_ch03.txt`: a TEACHER_DOCTRINE wall (10 doctrine paragraphs, lines 1–40) precedes a SCENE wall (8 scenes, lines 42–96) precedes a REFLECTION wall precedes an EXERCISE wall — i.e., the chapter renders as *slot-type blocks*, not the *earn-the-insight interleave*. Plus raw artifacts: `SCENE v16` (line 57), `Helvetica-Bold;Helvetica;` (line 114), doubled words "The the street below traffic" (line 53). Pattern breaks **P13, P4**; craft-failures **F4, F5**.

---

## 2. Pattern-by-pattern adjudication

Legend: **FIT** (pattern already holds) · **PARTIAL** (primitive present, not enforced/sequenced) · **BREAK** (pattern actively violated). Each entry: verdict · evidence · root cause · craft-failure cross-ref.

---

### P1 — Single Promise · **PARTIAL**
- **Evidence:** arcs declare `motif` + `resolution_type` (`PHOENIX_ARC_FIRST_CANONICAL_SPEC §2.3`) but no `book_promise` string. `chapter_intent` sequence implies a journey; nothing validates all intents converge on one destination.
- **Root cause:** absent arc field. Cohesion-by-convergence is unspecified.
- **Cross-ref:** loosely F1/F2 (without a promise, chapters drift into restatement).

### P2 — Five-Part Self-Help Spine · **BREAK**  ⬅ highest-impact
- **Evidence:** EXHIBIT C — flat 12× grid, no phases. The audit confirms the spine is *universal-but-flat* (`pearl_prime_audit_2026-06-06.md §1 Claim 1`). `emotional_curve`/`emotional_temperature_curve` are the only macro signals and aren't bound to named phases.
- **Root cause:** the spine is a *repeated chapter template*, not a *staged macro-arc*. There is no Problem→History→Knowledge→Action→Maintenance mapping.
- **Cross-ref:** underlies F2 (no progression) at the *book* scale — chapters can't progress through phases that don't exist.

### P3 — One Question Per Chapter · **PARTIAL**
- **Evidence:** `docs/CHAPTER_THESIS_BANK.md` + arc `chapter_intent` exist (the primitive). Overlay `§11.2` ("no same chapter, different nouns") is **advisory in rubric scoring only** (per craft proposal F2). No validator detects adjacent-chapter thesis paraphrase.
- **Root cause:** thesis is selected but not (a) surfaced as a posed-and-answered question, nor (b) checked for distinctness from neighbors.
- **Cross-ref:** **F2** directly ("chapter 1 and chapter 2 both answer 'anxiety is rational under structural uncertainty'"). Craft proposal C1 + G1 already target this.

### P4 — Promise–Proof–Process · **PARTIAL (shape strong, landing weak)**
- **Evidence:** the atom grid encodes it (HOOK→STORY→PIVOT→REFLECTION→EXERCISE), and the Orient/Name/Turn/Give/Pull overlay (`PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC §4`) *is* Promise-Proof-Process. But the overlay's five moves are **"verified by Pearl_Editor," not gate-enforced** (overlay `§4` "Pearl_Editor must verify … If any move is missing or weak, the chapter fails *this overlay*" — but the overlay isn't wired as a blocking gate; audit A5 shows Move-4 books all `book_pass: FAIL`).
- **Root cause:** the shape is correct; the *landings* (Name/Turn/Give) aren't enforced at assembly (see P5/P11/P14).
- **Cross-ref:** F6 (Name doesn't land), F7 (Turn doesn't land).

### P5 — Value Shift Per Scene · **BREAK**  ⬅ keystone
- **Evidence:** EXHIBIT B — `emotional_role_sequence` (polarity track) and STORY `arc_position` (turning-point ladder) are both present but **computed independently and not aligned**. EXHIBIT A — STORY positions don't traverse a shift.
- **Root cause:** STORY atom selection is by slot-fill + cross-phase dedup (`story_planner.py`), *not* by "match this chapter's emotional_role / advance the turn." The "turn" is metadata, never sequenced into a polarity shift.
- **Cross-ref:** **F1** (repetition cascade = the symptom of no per-unit turn). The audit (`§3.9`) notes Move-4 "BESTSELLER" measured character *presence*, not *change* — i.e., no turn verified.

### P6 — Transformation Character Arc · **BREAK**  ⬅ keystone (pairs with P5)
- **Evidence:** EXHIBIT A — characters scrambled, no through-line; embodiment-before-recognition. Yet `character_roster.yaml` defines **20 characters × 4 full arc-positions** with authored `turning_point_brief` per character (e.g., Priya, Marcus, Maya, Aisha). The primitive is *rich*; the assembly *ignores* it.
- **Root cause:** no "spine character" concept; the selector treats each STORY slot independently and dedups by name *across* phases, which actively *prevents* a character recurring through their arc within one book.
- **Cross-ref:** **F6** verbatim ("David/Lisa/Kevin/Sarah/Tanya/Marcus mostly function as 'person who has the same point I just made' … only Tanya has transformation arc"). Also **F8b** (gender/pronoun continuity — `character_roster.yaml` defines pronouns; render drifts).

### P7 — Open Loop / Payoff Rhythm · **PARTIAL**
- **Evidence:** THREAD slot exists (`V4.5 §4.7a`) with a specificity contract ("names a specific unresolved tension … not vague"). But there's no **book-scope loop ledger** ensuring each THREAD is *paid off* by a later chapter, and no *cap* preventing every chapter ending on maximal tension.
- **Root cause:** THREAD is authored per-chapter in isolation; no cross-chapter open/close bookkeeping.
- **Cross-ref:** weakly F2 (without paid-off loops, forward pull is generic — overlay `§7.2` "THREAD diagnostic" is per-chapter, not book-scope).

### P8 — Reader-as-Hero / Author-as-Guide · **PARTIAL**
- **Evidence:** slot types *are* the three positions (SCENE=you/hero, STORY=witness, TEACHER_DOCTRINE=guide, REFLECTION=coach). But voices bleed across slots (craft F5). No rule binds voice/person to slot-type.
- **Root cause:** the overlay waterfall lets one voice fill a slot it shouldn't own (craft proposal C2: "the slot-resolver overlay waterfall lets one voice bleed into a slot it shouldn't own").
- **Cross-ref:** **F5** verbatim ("Am I reading Brené Brown? A Buddhist teacher? A management consultant?") + **F8** (Ahjan-as-generic-Buddhist).

### P9 — Named Mechanism / Single Big Idea · **PARTIAL**
- **Evidence:** REFLECTION names mechanisms; TAKEAWAY crystallizes the *chapter* thesis. But there's **no per-book `book_idea`** that recurs as the backbone. Mechanism terms are *capped against* over-repetition (`overlay §9.1`: max 4/chapter) — the opposite of "make one idea recur and compound."
- **Root cause:** the system optimizes *anti-repetition*; it has no construct for *the one privileged idea that should recur*.
- **Cross-ref:** prior research §Cross-Topic #2 ("named mechanism required for retention") — present at chapter scale, absent at book scale.

### P10 — Escalation Before Reassurance · **PARTIAL**
- **Evidence:** arcs declare **one** `cost_chapter_index` + an `emotional_temperature_curve` with hot spikes (gold-ref `dominant_band_sequence` rises 1→4). But no rule binds the *middle* to escalate or gates reassurance until after the cost peak.
- **Root cause:** escalation is single-point (one cost chapter), not a *rising middle*; reassurance isn't sequenced relative to cost.
- **Cross-ref:** craft `§11.1` "No flat middle" + `§11.4` "Escalation before reassurance" — authored as overlay rules, **not enforced**.

### P11 — Aha Cadence · **PARTIAL**
- **Evidence:** PIVOT slot (`V4.5 §4.3a`) *is* the aha-recognition beat; STORY carries aha-type intent (overlay `§6.1` types A/B/C). **But PIVOT is absent from the gold-ref 6-slot grid** (EXHIBIT C: `[HOOK,SCENE,STORY,REFLECTION,EXERCISE,INTEGRATION]` — no PIVOT, no TAKEAWAY, no THREAD as discrete slots). So the aha beat may not render at all in current production.
- **Root cause:** structural-upgrade slots (PIVOT/TAKEAWAY/THREAD/PERMISSION) aren't in the canonical compiled grid; STORY aha-type isn't required to be non-predictable.
- **Cross-ref:** **F6** (stories "reveal nothing new" = no aha) + the audit's note that PIVOT-class slots need pipeline support.

### P12 — Callback / Motif Through-Line · **BREAK** (counterintuitive)
- **Evidence:** metaphor registry (`overlay §9.1`, `§13.1`) is **cap-only** — a metaphor is *retired after 5 chapters*. There is no "plant in ch1 / echo in ch6 / pay off in ch12" requirement. The system *suppresses* recurrence; the pattern *requires orchestrated* recurrence.
- **Root cause:** the only motif machinery is a *ceiling*, with no *floor* and no *position contract*.
- **Cross-ref:** F3 (decorative-metaphor inflation) is the *over-use* failure; P12 is the *under-orchestration* failure — they're two ends of the same missing "motif plan."

### P13 — Earn-the-Insight Pacing · **PARTIAL → BREAK in render**
- **Evidence:** canonical slot order encodes it (SCENE→STORY→PIVOT→REFLECTION) + post-impact ceilings (`V4.5 §4.4`). **But** EXHIBIT D shows the renderer can emit slot-type *blocks* (doctrine wall → scene wall → reflection wall), inverting the order so insight precedes identification ("talking at me").
- **Root cause:** intra-chapter slot ordering is not guaranteed stable through render (the `internal_deep6h_ch03` sample is block-ordered, not interleaved).
- **Cross-ref:** **F4** (placeholder/render leak in same sample) + the validation-gap finding (insight-before-validation = "talking at me").

### P14 — Somatic Landing · **PARTIAL (strong native, enforcement-gapped)**
- **Evidence:** INTEGRATION (`V4.5 §4.6`), PERMISSION (`§4.8`), final-widening rule (`overlay §7.1`) all exist. But craft F-integration documents INTEGRATION "degrading into summaries wearing quiet clothes" (overlay `§7.1` names this exact failure), and the single-function landing isn't gate-enforced.
- **Root cause:** the landing contract is authored, not enforced; PERMISSION placement depends on `cost_chapter_index` which is single-point (see P10).
- **Cross-ref:** the EI rubric's `emotional_arc` dimension (close in a shifted state) — present as a rule, unenforced.

---

## 3. The gap, summarized

| Verdict | Patterns | Count |
|---------|----------|------:|
| **BREAK** (actively violated) | P2 (flat spine), P5 (no value-turn), P6 (scrambled character arc), P12 (motif suppressed not orchestrated) | 4 |
| **PARTIAL** (primitive present, unenforced/unsequenced) | P1, P3, P4, P7, P8, P9, P10, P11, P13, P14 | 10 |
| **FIT** (already holds) | — (none fully; P4/P13/P14 are the closest, strong-shape) | 0 |

**Mapping to the 8 craft failures** (proving this analysis is consistent with prior diagnosis, from a structural angle):

| Craft failure | Pattern(s) it violates | Assembly root |
|---------------|------------------------|---------------|
| F1 repetition cascade | P5 (no per-unit turn), P10 (flat middle) | STORY selected without arc-beat advance |
| F2 no progression | P2, P3 (no phases, no per-ch question) | flat spine + unchecked thesis paraphrase |
| F3 decorative metaphor | P12 (no motif *plan* → metaphors float) | metaphor cap without position contract |
| F4 placeholder leak | P13 (render integrity) | Stage-6 cleanup gap |
| F5 voice fragmentation | P8 (positions blur) | no voice/slot zoning |
| F6 illustration-not-story | P6, P5, P11 (no arc, no turn, no aha) | character-continuity ignored in selection |
| F7 anxiety mono-framed | P5, P11 (no turn = no signal/amplification distinction) | single-framing REFLECTION selection |
| F8 generic-Buddhist | P8, P12 (guide-voice not specific, no teacher motif) | TEACHER_DOCTRINE selection not specificity-gated |

**Conclusion.** Every break and every craft failure traces to **assembly-layer sequencing/selection**, not atom scarcity. The atoms encode the patterns' primitives; the assembler doesn't *order* them into the patterns. Nine of the audit's "what's broken" items (`§3`) are registry/format issues *orthogonal* to this — the bestseller-cohesion gap is specifically the **arc-beat → atom-selection binding**. That binding is the subject of the fit plan.

**What is genuinely missing at the atom layer (small, scoped):** signal-vs-amplification REFLECTION variants (F7/G6), Ahjan-specific TEACHER_DOCTRINE atoms (F8/C3), and EXERCISE backfill for ~10 combos (audit P2-A). These are *targeted authoring lanes*, not mass rewrites — flagged for Pearl_Editor/Pearl_Writer in the plan.

---

*End of gap analysis. Next: `FIT_OUR_ATOMS_TO_PATTERNS_PLAN.md` — the deterministic sequencing/selection rules, P0/P1/P2 prioritized.*

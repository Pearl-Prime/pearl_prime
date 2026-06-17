# Fit Our Atoms To Patterns — Plan

**Compiled:** 2026-06-11 | **Authority:** Pearl_Research (proposal — routing only; no spec/code authored here)
**Reads:** `BESTSELLER_PATTERN_CATALOG.md`, `OUR_SYSTEM_VS_PATTERNS_GAP.md`.
**Status:** RESEARCH PROPOSAL. Every item routes to Pearl_Architect (spec/cap) and/or Pearl_Editor/Pearl_Writer (atom authoring) and/or Pearl_Dev (gate). Nothing here is ratified.
**Authority order:** subordinate to `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (validators are structural-only) and `specs/PHOENIX_V4_5_WRITER_SPEC.md` (atom contracts). This plan adds **deterministic sequencing/selection** rules — fully compatible with the canonical spec's "only structural determinism belongs in validators" principle (§9). No emotional/quality simulation is proposed.

---

## 0. The one-paragraph thesis

Make atom-assembly **deterministically hit the proven patterns** by binding the **arc-beat metadata Phoenix already computes** (`emotional_role_sequence`, named-character `arc_position`, `cost_chapter_index`, `motif`) to **atom *selection* and slot *sequencing*** — instead of selecting by slot-fill + dedup. Bestseller cohesion is a sequencing problem over existing atoms; the fix is ~5 selection/ordering rules + 3 small arc fields + targeted atom backfill. This is squarely inside the canonical spec: it is *structural determinism* (which atom goes in which slot, in which order), not prose scoring.

**Design rule honored throughout (anti-reinvention, MEMORY):** every change **edits an existing construct** (the arc schema, the STORY selector, the metaphor registry, the slot grid). No new parallel "bestseller engine." Layer-2/3 reinvention-guard dispatch stays gated on `PEARL_ARCHITECT_STATE.md` cascade-settle.

---

## 1. The five deterministic fit-moves (the core)

These five rules, applied at compile/assembly, convert the BREAK patterns to FIT. They are ordered by leverage. Each = **what · how (deterministic mechanism) · which pattern/failure it closes · routing**.

---

### MOVE 1 — Bind the 12-spine to a 5-phase macro-arc (closes P2; root-fixes F2 at book scale)

**What.** Stop treating the 12-chapter spine as 12 identical templates. Declare a **`book_phase` per chapter** mapping the spine onto the canonical self-help macro-arc: **Problem → History → Knowledge → Action → Maintenance**.

**How (deterministic).** Add `book_phase` to the arc schema (`PHOENIX_ARC_FIRST_CANONICAL_SPEC §2.3`). A 12-chapter default mapping (illustrative; Pearl_Architect tunes per engine):

| Ch | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|----|---|---|---|---|---|---|---|---|---|----|----|----|
| Phase | Problem | Problem | History | History | Knowledge | Knowledge | Knowledge | Action | Action | Action | Maintenance | Maintenance |

The phase then *constrains* three already-existing arc fields so they stop being free-floating:
- `emotional_role` per chapter must be consistent with phase (Problem→recognition/destabilization; History→reframe; Knowledge→reframe/stabilization; Action→stabilization+embodiment-prep; Maintenance→integration).
- `book_phase` boundaries become the **anchor points** for MOVE 2 (character arc) and MOVE 4 (motif).
- The compiler validates phase monotonicity (no Maintenance before Action).

**Closes.** P2 (BREAK→FIT). Gives F2 ("no progression") a *structure to progress through*. Enables MOVE 2/4/5 to have boundary anchors.

**Routing.** Pearl_Architect (cap entry: `BOOK-PHASE-SPINE-01` — add `book_phase` to arc schema + 12→5 default map per engine). Pearl_Dev (compiler validation: phase monotonicity, ~30 LoC). **Zero new atoms.**

---

### MOVE 2 — Spine-character through-line selection (closes P6 + half of P5; root-fixes F6)

**What.** Designate **1–2 "spine characters" per book** whose four `arc_position` atoms (recognition→mechanism_proof→turning_point→embodiment) land **at the four phase boundaries, monotonically**, so the reader *watches one person change* across the book.

**How (deterministic).** At plan time, before slot-fill:
1. Select 1 primary spine character (+ optional secondary) from `character_roster.yaml` matching persona/topic/engine.
2. Pin their four arc-position STORY atoms to phase-aligned chapters:
   - **recognition** → a Problem-phase chapter (ch1–2)
   - **mechanism_proof** → a History/Knowledge chapter (ch3–5)
   - **turning_point** → the `cost_chapter_index` chapter (the cost peak)
   - **embodiment** → an Action/Maintenance chapter (ch10–12)
3. The existing cross-phase dedup (`story_planner.py`) is **inverted for the spine character**: instead of preventing recurrence, it *requires* the spine character to recur at exactly these four positions (and forbids them elsewhere). Non-spine STORY slots fill as today (different characters, no through-line required).

This directly fixes EXHIBIT A: instead of Priya appearing once at embodiment in ch0, Priya (or chosen spine char) appears at recognition→mechanism_proof→turning_point→embodiment across ch1→5→[cost]→11, monotonically.

**Closes.** P6 (BREAK→FIT). Resolves F6 ("only Tanya has a transformation arc" → every book now has ≥1 deliberate arc). Also delivers continuity for F8b (spine character's pronouns pinned from roster).

**Routing.** Pearl_Architect (cap: `SPINE-CHARACTER-THROUGHLINE-01`). Pearl_Dev (selector change in `story_planner.py` — invert dedup for spine char, pin to phase boundaries, ~60-80 LoC). Pearl_Editor (ensure the top ~5 characters per persona have all 4 arc-positions authored — audit notes Priya/Marcus/Maya/Aisha/Jordan need missing positions; `scene_injection_map.yaml §generation-priority` already lists this lane). **Mostly existing atoms + targeted backfill.**

---

### MOVE 3 — Align STORY/REFLECTION selection to the value-polarity track (closes the other half of P5 + P11; root-fixes F1, F7)

**What.** Make each chapter **"turn"** by binding atom selection to the arc's `emotional_role` for that chapter — so the non-spine STORY atoms and the REFLECTION advance the polarity shift instead of repeating.

**How (deterministic).**
1. **STORY ↔ role alignment.** For each chapter, the STORY `arc_position` must be *consistent with* `emotional_role` (recognition-role chapters draw recognition/mechanism_proof STORYs; reframe-role chapters draw turning_point STORYs; integration-role chapters draw embodiment STORYs). Reject selections where a destabilization chapter pulls an embodiment STORY (the EXHIBIT B mismatch).
2. **Conceptual non-repetition across adjacent chapters.** A local-embedding cosine check (P3/G1) rejects a STORY/REFLECTION whose body is within threshold of the prior 1–2 chapters' — forcing the *next* idea, not a reworded same idea. (Local embeddings only — `all-MiniLM-L6-v2` / `nomic-embed-text` on Pearl Star; Tier-2-safe per CLAUDE.md. This answers the craft proposal's open question G1.)
3. **Signal-vs-amplification REFLECTION (F7).** For introspective engines (spiral/overwhelm/shame/false_alarm/watcher), require each chapter's REFLECTION (or PIVOT) to carry the signal/amplification distinction — needs ~1 new REFLECTION variant per engine (small authoring lane).

**Closes.** P5 (BREAK→FIT, completing MOVE 2). P11 (PARTIAL→FIT, the aha turns become real). F1 (repetition cascade — the per-unit turn is the cure). F7 (mono-framing).

**Routing.** Pearl_Architect (cap: `STORY-ROLE-ALIGNMENT-01` + `CONCEPTUAL-REPETITION-GATE-01` — this *is* the craft proposal's G1, now with the embedding-model question resolved). Pearl_Dev (selection constraint + local-embedding gate, ~80-120 LoC; the gate already proposed as `chapter_progression_gate.py`). Pearl_Editor/Pearl_Writer (signal/amplification REFLECTION variants for 5 engines — the craft proposal's G6 lane, ~10-15 atoms).

---

### MOVE 4 — One orchestrated motif + one named book-idea (closes P12, P9; counters F3)

**What.** Convert the metaphor registry from **cap-only** (retire after 5 chapters) to **orchestrated recurrence**: one motif *planted* (Problem phase) → *echoed* (Knowledge/cost) → *paid off* (Maintenance). Plus declare one `book_idea` (the named model, e.g., "the stress cycle") that recurs in the phase-boundary TAKEAWAYs and compounds.

**How (deterministic).**
1. Add `book_motif` + `book_idea` to the arc schema.
2. `book_motif` gets a **position contract**: must appear in ch1–2 (plant), the cost chapter (echo, recontextualized), and ch11–12 (payoff). The existing ≤5-chapter cap *stays* for all *other* metaphors (anti-F3); the one `book_motif` is the privileged exception with a *floor* (≥3 placed) + position rule.
3. `book_idea` is exempt from the mechanism-term repetition cap (`overlay §9.1`) and is *required* in TAKEAWAY of each phase-boundary chapter — so the one model compounds (P9) instead of being suppressed.

**Closes.** P12 (BREAK→FIT — motif now orchestrated). P9 (PARTIAL→FIT — one idea backbone). Counters F3 by giving metaphors a *plan* (the float happens because no metaphor is privileged; now one is, the rest stay capped).

**Routing.** Pearl_Architect (cap: `BOOK-MOTIF-IDEA-01` — add fields + position contract + cap-exemption-for-one). Pearl_Dev (position validator + cap-exemption logic, ~40 LoC). Pearl_Editor (owns metaphor/idea registry per `§13.1`; selects the privileged motif+idea per topic — ~1 line per topic config). **Zero-to-minimal new atoms.**

---

### MOVE 5 — Slot-zoning + ordering integrity + loop ledger (closes P8, P13, P7; root-fixes F5, F4)

**What.** Three render-layer guarantees: (a) **voice is zoned to slot-type** (reader-as-hero/witness/guide stay legible), (b) **intra-chapter slot order never collapses to blocks**, (c) **every THREAD open-loop is paid off** and not every chapter maxes tension.

**How (deterministic).**
1. **Voice-zone (P8/F5).** Adopt craft proposal C2 **Option B (zone)**: SCENE=second-person reader; STORY=third-person witness; TEACHER_DOCTRINE=guide; REFLECTION=author-coach; EXERCISE=imperative coach. A Stage-6 lint flags voice/person out-of-zone (e.g., second-person in a STORY, doctrine voice in a SCENE).
2. **Order integrity (P13/F4).** Guarantee the renderer emits the *interleaved* slot order (HOOK→SCENE→STORY→PIVOT→REFLECTION→EXERCISE→INTEGRATION), never slot-type *blocks* (the EXHIBIT D failure). Add a render assertion: the emitted atom sequence per chapter equals the planned slot sequence. Also strip render artifacts (`SCENE v16`, `Helvetica-…`, doubled words) — the craft proposal's G3 placeholder gate.
3. **Loop ledger (P7).** Book-scope check: each chapter's THREAD names a tension that a *later* chapter's HOOK/STORY resolves (no orphan loops), and ≤N consecutive chapters end on maximal-tension THREADs (fatigue cap).

**Closes.** P8 (PARTIAL→FIT). P13 (render-BREAK→FIT). P7 (PARTIAL→FIT). F5 (voice fragmentation). F4 (render leak). 

**Routing.** Pearl_Architect (cap: ratify C2 Option B — this is the *one operator-tier ruling* the craft proposal already flagged). Pearl_Dev (voice-zone lint + order-integrity assertion + G3 placeholder strip + loop ledger; the proposal's G3 + a new ~50 LoC ledger). **Zero new atoms** (zoning uses existing atoms correctly).

---

## 2. How the five moves deliver the operator's frame

The operator's verbatim intent → which moves deliver it:

| Operator's words | Delivered by |
|------------------|--------------|
| "chapters make sense" (cohesion) | MOVE 1 (phases) + MOVE 4 (one motif/idea) + MOVE 3 (no adjacent repetition) |
| "readers feel they're learning AND earning" | MOVE 3 (the per-chapter turn = aha cadence) + MOVE 5b (earn-the-insight order intact) |
| "by the end they've learned/grown/derived value" | MOVE 2 (spine-character arc = felt growth) + MOVE 1 (Maintenance phase consolidates) + MOVE 4 (idea compounded) |
| "the book is engaging" | MOVE 5c (open-loop rhythm) + MOVE 3 (every unit turns, no flat middle) |
| "fit our atom-assembly into proven patterns → reliable bestseller cohesion" | all five = the arc-beat→selection binding |

**The deterministic guarantee:** with MOVES 1–5, a book *cannot* assemble into the F1–F8 failure shapes, because the selector refuses atoms that don't advance the phase/role/character/motif. Cohesion becomes a *property of the assembler*, not a lucky draw — which is exactly "consistently bestseller, not occasionally."

---

## 3. Prioritization (P0/P1/P2)

Sequenced by leverage × cost, honoring **validation-before-scaling** (MEMORY): land the gates, verify on the gold-ref combo + one fresh combo, *then* scale. Do NOT batch-regenerate the catalog on these until a validator confirms uplift on a single book.

### P0 — highest leverage, mostly sequencing (no/low new atoms) — **do first**
- **P0-1 = MOVE 1** (book_phase spine map). Unblocks MOVES 2/4. Arc-field + compiler validation. *Pearl_Architect cap + Pearl_Dev ~30 LoC.*
- **P0-2 = MOVE 2** (spine-character through-line). The single most visible quality jump (felt growth). *Pearl_Architect cap + Pearl_Dev ~80 LoC + Pearl_Editor backfill top-5 characters' missing arc-positions.*
- **P0-3 = MOVE 3 step 1** (STORY↔role alignment). Makes chapters turn. *Pearl_Dev selection constraint, ~40 LoC* (reuses MOVE 1's phase/role).

These three are the keystone. They convert 3 of 4 BREAK patterns (P2, P5, P6) and root-fix F1/F2/F6 — the majority of the craft critique — primarily by **sequencing atoms we already have**.

### P1 — high leverage, small gate + tiny config (Pearl_Dev-ready)
- **P1-1 = MOVE 4** (book_motif + book_idea orchestration). *Pearl_Architect cap + Pearl_Dev ~40 LoC + Pearl_Editor 1-line-per-topic registry pick.*
- **P1-2 = MOVE 5a/5b** (voice-zone lint + order-integrity + G3 placeholder strip). Requires the **one operator ruling**: C2 Option B. *Pearl_Architect ratify + Pearl_Dev ~60 LoC.* (G3 is already a standalone proposal — mechanical.)
- **P1-3 = MOVE 3 step 2** (conceptual-repetition gate, local embeddings). *Pearl_Dev ~80 LoC; resolves G1 embedding-model question (local Pearl Star).*

### P2 — targeted atom authoring (Pearl_Editor + Pearl_Writer lanes; the genuinely-missing atoms)
- **P2-1 = MOVE 3 step 3** signal/amplification REFLECTION variants × 5 introspective engines (~10-15 atoms). *Pearl_Writer; the craft proposal's G6 lane.*
- **P2-2 = MOVE 5c** loop-ledger + THREAD payoff authoring where orphan loops exist. *Pearl_Editor curation + Pearl_Dev ledger ~50 LoC.*
- **P2-3** Ahjan-specific TEACHER_DOCTRINE atoms (F8/C3) to fix guide-voice genericity (P8 depth). *Pearl_Editor via Qwen, CJK-safe / Pearl_Writer EN — ~per audit P2-C.*
- **P2-4** EXERCISE backfill for ~10 bestseller-grade combos (audit P2-A) — orthogonal but unblocks production-strict.

**Sequencing:** P0-1 → P0-2 ∥ P0-3 → verify on gold-ref combo → P1-1 ∥ P1-2 (needs C2 ruling) ∥ P1-3 → verify → P2 authoring lanes.

---

## 4. Verification protocol (gate scaling on this, not vibes — MEMORY)

After each move lands, verify on the **gold-reference combo** (`gen_z_professionals × anxiety × overwhelm × F002`) + one fresh combo, using the existing `flagship` profile + the new structural checks. The pass bar, expressed structurally (no quality simulation):

1. **MOVE 1:** every chapter has a `book_phase`; phases are monotonic; `emotional_role` consistent with phase.
2. **MOVE 2:** the spine character's four arc-position STORY atoms appear at the four phase boundaries, in order; appear nowhere else; pronouns match roster.
3. **MOVE 3:** every chapter's STORY `arc_position` is role-consistent; no adjacent-chapter body exceeds the conceptual-similarity threshold; introspective engines carry the signal/amplification distinction.
4. **MOVE 4:** `book_motif` appears at plant/echo/payoff positions; `book_idea` appears in phase-boundary TAKEAWAYs; all *other* metaphors stay ≤5 chapters.
5. **MOVE 5:** zero voice-out-of-zone lint hits; emitted slot order == planned order (no block collapse); zero render artifacts; zero orphan open-loops; ≤N consecutive max-tension THREADs.

Then — and only then — a Pearl_Editor read confirms the structural fix *reads* as cohesion/growth (the qualitative gate that the EI rubric + overlay `§13` already define). Scaling to catalog runs is gated on that read, per `feedback_validation_before_scaling`.

---

## 5. What this plan deliberately does NOT do

- **No new "bestseller engine."** Every move edits an existing construct (arc schema, STORY selector, metaphor registry, slot grid, render lint). Anti-reinvention honored.
- **No prose/quality simulation in validators.** Every check is structural-deterministic (which atom, which slot, which order, which position) — compatible with `PHOENIX_ARC_FIRST_CANONICAL_SPEC §9` ("only structural determinism belongs in validators"). The *one* semantic check (conceptual-repetition cosine) is a **local-embedding** structural gate, not a tone/quality heuristic, and runs Tier-2-safe.
- **No paid LLM API** anywhere in runtime (CLAUDE.md). Local embeddings on Pearl Star for the one semantic gate; all prose authoring is Pearl_Writer (Claude subagents, Tier-1 attended) or Qwen (CJK).
- **No mass atom regeneration.** The plan is ~5 selection/ordering rules + 3 arc fields + ~25-40 targeted atoms (signal/amplification, Ahjan-specific, EXERCISE backfill). The 16k+ existing atoms are *re-sequenced*, not rewritten.
- **No scaling before validation.** P2 authoring + catalog runs gate on the verification protocol passing on a single book first.

---

## 6. Routing summary (for the operator → Pearl_Architect → lanes)

| Move | Pearl_Architect (cap/ruling) | Pearl_Dev (LoC) | Pearl_Editor/Writer (atoms) |
|------|------------------------------|-----------------|------------------------------|
| 1 book_phase spine | `BOOK-PHASE-SPINE-01` | ~30 | — |
| 2 spine-character | `SPINE-CHARACTER-THROUGHLINE-01` | ~80 | backfill top-5 char arc-positions |
| 3 role-align + repetition + signal | `STORY-ROLE-ALIGNMENT-01`, `CONCEPTUAL-REPETITION-GATE-01` (=G1, model resolved) | ~120 | ~10-15 signal/amplification REFLECTIONs |
| 4 motif + idea | `BOOK-MOTIF-IDEA-01` | ~40 | registry pick per topic (~1 line) |
| 5 zone + order + loop | ratify **C2 Option B** (the one operator ruling) | ~110 + G3 | — |

**The one operator-tier decision** that unblocks the most: ratify **C2 voice-braid Option B (zone)** — already flagged in the craft proposal's decision items §9.1. Everything else is cap-entry + Pearl_Dev + targeted authoring.

**NEXT_ACTION for the operator:** review the deck → approve the fit-plan (especially MOVES 1+2 as P0 and the C2 Option B ruling) → Pearl_Architect specs `BOOK-PHASE-SPINE-01` + `SPINE-CHARACTER-THROUGHLINE-01` + the selection-binding caps → Pearl_Editor authors the targeted P2 atom lanes → verify on gold-ref combo → gate scaling.

---

*End of plan. Companion deck: `BESTSELLER_CONSISTENCY_DECK.pptx`.*

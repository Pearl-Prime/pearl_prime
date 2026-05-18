# Pearl Prime Acceptance Verdict — 2hr × ahjan × gen_z_professionals × anxiety × en_US

**Book under review:** `artifacts/pearl_prime/extended_book_2h/ahjan_gen_z_professionals_anxiety_en_US_20260518T131809Z_round5/book.txt` (22598 words / 12 chapters / extended_book_2h runtime)

**Scorecard authority:** `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` (4-layer acceptance stack)

**Closed-loop step:** (A) — the calibration read

**Date:** 2026-05-18

---

## §1 Executive verdict

**Layer 1 — Hard blockers: ✅ PASS** — all 7 required gates green (chapter_flow, bestseller_craft 0.6338, ei_v2 0.6733, scene_anchor_density, transformation_arc, book_pass, book_quality_gate `release_band: Pass`).

**Layer 2 — Advisory craft: ⚠ 2 WARNs** — editorial (flow polish) + memorable_lines (11/12 chapters ≥2 quotable). Per scorecard, ≥2 WARNs requires explicit Layer 3 verdict.

**Layer 3 — Pearl_Editor ONTGP sample: ❌ FAIL** — sampled Ch1 / Ch5 / Ch11. Ch1 passes (4 PASS / 1 WEAK). Ch5 fails (1 PASS / 2 WEAK / 2 FAIL). Ch11 fails (2 PASS / 2 WEAK / 1 FAIL). 2 of 3 sampled chapters FAIL ONTGP — book is NOT `system working` per scorecard.

**Layer 4 — System benchmark:** not run (operator-time blind-10).

**Final status (scorecard language):** the book is **structurally clear** — it produced a coherent book.txt and passes all machine gates. It is **NOT an authored candidate**, **NOT system working**, **NOT bestseller register**. Should not ship at trade-pub register without remediation.

**One-line synthesis:** The factory works. The book passes every machine gate. The Pearl_Editor read surfaces structural defects machine gates cannot detect — templated mechanism-block repetition, broken slot-template fragments, off-doctrine teacher-bank content, and named-character continuity breaks. These are exactly the failure modes the audit doc predicted would appear in books that "pass gates but don't feel bestseller."

---

## §2 Layer 1 quantitative recap (from `quality_summary.json`)

| Gate | Status | Score | Notes |
|---|---|---|---|
| chapter_flow | PASS | — | Ch1 + Ch11 fix landed via PR #1185 (thesis cue + transition cue) |
| bestseller_craft | PASS | 0.6338 | above 0.55 production floor |
| ei_v2 | PASS | 0.6733 composite | |
| scene_anchor_density | PASS | 0 violations | post-PR #1180 + #1183 + #1185 cluster diversification |
| transformation_arc | PASS | — | HARDSHIP→HELP→HEALING→HOPE arc tokens present |
| book_pass | PASS | identity_stages all true | |
| book_quality_gate | Pass | `release_band: Pass` | `quality_gate_failures: []` |
| **overall_status** | **WARN** | — | aggregate; editorial + memorable_lines WARNs |

**Verdict at Layer 1:** structurally clear. Pipeline produced a coherent 22598-word book in extended_book_2h format. Recurrence_report stripped 21 phrase clusters; exercise_slots_dropped at 11 (governance cap functioning).

---

## §3 Layer 2 advisory craft (from per-gate reports)

**editorial: WARN** — flow polish recommendation; not delivery-blocking.

**memorable_lines: WARN** — 11/12 chapters have ≥2 quotable lines. 1 chapter falls short.

**Recurrence_report (Layer 2 cap = 30 stripped clusters before WARN):** 21 stripped clusters. Under the WARN threshold but notable. The system's deduplication caught 21 patterns that would have been clusters; those patterns suggest the upstream banks have monotonic phrasing tendencies.

**Frame governor:** all chapters `frame_compliant: true`. Ch12 had a violation on `karma` (`absolute_claim` pattern) but `softened: []`, `stripped: []`, `hard_fail: []` — the violation was recorded but not enforced. The teacher_bank → frame_governor coupling needs review: violations should soften or strip under production profile.

**Verdict at Layer 2:** 2 WARNs → escalate to Layer 3 per scorecard rule.

---

## §4 Layer 3 — Pearl_Editor ONTGP sample (the deciding read)

**Sampling protocol:** read Ch1 (opening), Ch5 (mid-arc), Ch11 (late-arc). If thin, expand. Per ONTGP, chapter passes if 0 FAILs and ≤2 WEAKs across all 5 dimensions.

### Ch1 — "The Alarm That Won't Stop Ringing"

| Dimension | Score | Evidence |
|---|---|---|
| **Orient** | **PASS** | Opens: "The weirdest part is not that you are anxious but that part of you has started treating relief as suspicious. Your chest braces when good news arrives, as if the alarm knows something the message does not." Embodied, specific, gen-z-professional register. |
| **Name** | **PASS** | Names: "hypervigilance as trained response", "threat detection system", "elevated baseline", "vagus nerve", "cyclic sighing practice." Topic-vocab present. Caveat: register is pedagogical ("The mechanism I want to name is...") not embodied. |
| **Turn** | **PASS** | Named-character beat: "Priya submits the project update at 11:47pm. It is thorough. She has checked it three times. The Slack confirmation appears immediately." Concrete, specific, gen-z-detail (Slack, typo, laptop screen). |
| **Give** | **PASS** | Three concrete practices: cyclic sighing (Stanford-anchored), 90-second 3-step writing exercise, Friday 4pm "alarm ledger" Notion entry. Over-prescribed (one would have been stronger) but unambiguously gives the reader something to hold. |
| **Pull** | **WEAK** | Closing: "What remains is the next ordinary moment where the pattern tries to make the decision for you." Functional traction-out but generic; doesn't bait Ch2's specific scene. |
| **Chapter verdict** | **PASSES ONTGP** | 4 PASS / 1 WEAK / 0 FAIL — within cap of ≤2 WEAKs, 0 FAILs. |

**Ch1 register note:** The "In Ahjan's framework, the path begins with." fragment at line 7 of book.txt is a **broken slot template** — the teacher-frame block ends with `with.` and then jumps to generic content ("Attachment grows in darkness..."). This is a renderer artifact, not authored prose. Caught by reading; not caught by any current gate.

### Ch5 — "What Living On Alert Actually Costs"

| Dimension | Score | Evidence |
|---|---|---|
| **Orient** | **WEAK** | Opens with a strong line ("You used to have opinions about your work. They are harder to access than they used to be.") — but the orient is broken structurally by the line `"Ahjan's reading of this is precise: ."` (verbatim — trailing period after colon, no content). Pre-edit slot-template artifact. |
| **Name** | **FAIL** | Two TEMPLATED MECHANISM BLOCKS appear with only the mechanism name varying. Block A: "The mechanism is **identity anxiety when role is threatened**. This is what happens in the body of the professional when the unclear career path activates the system that was built for survival but now runs in the context of the workplace..." Block B (~6 paragraphs later): "The mechanism is **allostatic load from sustained activation**. This is what happens in the body of the professional when the gig economy precarity activates the system that was built for survival but now runs in the context of the workplace..." Structurally identical paragraphs. A reader recognizes this immediately as generated. |
| **Turn** | **FAIL** | Three Amara micro-scenes ("Amara sends the brief at 3:47pm..." / "Amara sends the deliverable and waits..." / "Amara sends a brief she knows is B-minus...") that don't add up to ONE turn. Then the chapter swerves to: "What Ahjan returns to again and again is this." followed by content that is NOT ahjan's doctrine but generic Buddhist/Krishna/Bhakti teacher content: "This direct transmission of light from teacher to student is a sacred and transformative aspect of many spiritual traditions... Krishna's teachings... Bhakti Yoga underscores the significance of self-love..." Off-doctrine. The audit's PRIMARY ROOT CAUSE (teacher_bank overriding persona+topic substance) is exactly visible here. |
| **Give** | **WEAK** | "Start with the pressure under the sternum. **still bracing.**" — incomplete sentence fragment. "Ahjan's the practice" appears as a 3-word slot artifact. The nasal-breathing paragraph appears (apparently a recurring template). The "alarm has a fee" callback is the strongest concrete give. Mixed quality. |
| **Pull** | **PASS** | "What remains is the moment after the alarm fires, when your body still wants to obey a prediction." Functional. |
| **Chapter verdict** | **FAILS ONTGP** | 1 PASS / 2 WEAK / 2 FAIL — exceeds caps (any FAIL fails the chapter). |

### Ch11 — "Living With The Alarm On Low"

| Dimension | Score | Evidence |
|---|---|---|
| **Orient** | **PASS** | "The all-hands started ten minutes ago. You are listening with one ear while you scan the agenda doc. Your camera is off. Your hand is on the mouse but not moving." + PR #1185's transition fix "In practice that looks like this: the camera goes off, the second screen comes up..." Solid embodied gen-z-pro register. |
| **Name** | **FAIL** | Same templated mechanism-block pattern as Ch5. "The mechanism is **anticipatory anxiety and pre-loading**. This is what happens in the body of the professional when the gig economy precarity activates the system..." — structurally IDENTICAL paragraph to Ch5's two blocks. Third firing of the same template across the book. Plus: "Where Ahjan departs from the usual framing is here." appears TWICE in Ch11 (lines 1130 + 1166), each followed by off-doctrine teacher content about "path to liberation accessible to all... martial arts, healing... Love Beyond Self and Relationships." |
| **Turn** | **PASS** | Three named-character scenes — Chris at his mother's table for Thanksgiving ("She asks how work is going. He says 'really well, actually.'"), Jordan with the budget narrative + tab count, Nia with the therapist log + the line "What is it like to feel the entries, rather than read them?" The Chris-mother scene + the therapist's question are the strongest authored prose in the book. Possibly over-stuffed (3 scenes when 1-2 would suffice) but each one works. |
| **Give** | **WEAK** | "Land for a moment. Feel what is different from when you started this chapter." okay. "Ahjan's the practice" appears again as a 3-word slot artifact. Then off-doctrine teacher content: "Successfully integrating these experiences confirms the validity of our spiritual practices. The Practice of Meditation and Mindfulness... The Influence of a Spiritual Teacher." Generic spiritual teacher-bank content, not specific. Mixed. |
| **Pull** | **PASS** | "Carry this forward: You are not going to become a person without an alarm. You are going to become a person who knows when the alarm is running and has a say in what happens next." Strong identity-statement close. **Caveat:** closing line "What remains is the moment after the alarm fires, when your body still wants to obey a prediction." is VERBATIM IDENTICAL to Ch5's closing line. Verbatim closing-line repetition across chapters in a serialized arc is a real defect. |
| **Chapter verdict** | **FAILS ONTGP** | 2 PASS / 2 WEAK / 1 FAIL — exceeds caps. |

### Sample summary: 1 PASS / 2 FAIL → Layer 3 FAILS

Per scorecard rule: book passes Layer 3 iff all sampled chapters pass ONTGP. Two of three fail. **Book FAILS Layer 3.**

---

## §5 Concrete failure modes (the calibration data for Step D)

These are the specific defects visible to a Pearl_Editor reader that no current machine gate caught. They are the targets the **register gate spec (closed-loop step D)** must measure against.

### F1 — Templated mechanism-block repetition

The pattern `"The mechanism is X. This is what happens in the body of the professional when [Y activates the system built for survival but now runs in the context of the workplace]..."` appears at least 3 times across the book (Ch5 ×2, Ch11 ×1; likely more). Only the mechanism name and one anchor-detail vary. The surrounding 5-sentence paragraph is copy-paste.

**What a reader notices:** "I've read this paragraph already."

**Gate dimension:** structural-paragraph-template similarity. Could be detected by computing pairwise paragraph cosine-similarity within a book; any two paragraphs above a similarity threshold = WARN; >2 paragraphs above threshold = FAIL.

### F2 — Broken slot-template fragments

Verbatim from the book:
- `"In Ahjan's framework, the path begins with."` (Ch1 line 7)
- `"Ahjan's reading of this is precise: ."` (Ch5 — trailing period after colon, no content)
- `"Ahjan's the practice"` (Ch5 and Ch11 — 3-word artifact)
- `"can explain the moment, the alarm has already chosen a meaning for it. That matters because..."` (Ch11 — sentence opens with `"can explain"` — missing subject)
- `"mechanism running continuously is written into your biology."` (multiple chapters — opens with lowercase noun phrase, missing the leading article)

**What a reader notices:** the slot-template machinery is visible. Reader trust collapses.

**Gate dimension:** sentence-start integrity. Every sentence-start (post-period or post-paragraph-break) should begin with a capital letter that is a complete grammatical subject OR a recognized framing word. Fragments like `"with."` as paragraph-end, `": ."` as content-absent slot, lowercase-noun-phrase sentence starts = HARD FAIL (any one of these = book-level FAIL).

### F3 — Off-doctrine teacher-bank content overrunning persona+topic substance

The audit's primary root cause manifests verbatim:

Ch5 contains:
> "This direct transmission of light from teacher to student is a sacred and transformative aspect of many spiritual traditions...Structured Pathways to LightIn some spiritual traditions, a structured approach is employed to guide practitioners toward a direct experience of the light..."

> "Therefore, channeling your focus into your work can significantly enhance your awareness and concentration. Consider work as a means of strengthening your mind and developing impeccable attention to detail...Bhakti Yoga underscores the significance of self-love, balanced relationships, and selfless affection in all forms..."

Ch11 contains:
> "Through their example, they show that the path to liberation is accessible to all...One of the key aspects of the enlightened ones is their ability to bring excellence and precision to every aspect of life. Whether they are engaged in martial arts, healing..."

> "Successfully integrating these experiences confirms the validity of our spiritual practices...The Practice of Meditation and Mindfulness — Meditation, through the cessation of thought, offers direct access to spiritual experiences..."

This is NOT ahjan's doctrine (Tantric Buddhist; alarm-systems / pause). This is generic-spiritual-teacher content — Krishna, Bhakti Yoga, Buddhist-transmission-of-light, mystical-martial-arts — being pasted in via teacher_bank wrapper without doctrinal validation against the specific teacher. The TEACHER-MODE-WRAPPER-SEMANTICS-01 cap entry locked the substance-vs-voice precedence but the **wrapper-line-budget rule is being violated**: the teacher-bank wrapper is providing PARAGRAPHS of off-doctrine content, not the ≤1-2 lines the cap entry specified.

**Gate dimension:** per-teacher doctrinal vocabulary compliance. For ahjan (Tantric Buddhist): tokens `Krishna`, `Bhakti`, `Sufi`, `Vedanta`, generic `enlightened ones`, `Brahman` etc. = WARN-per-token; >3 distinct off-doctrine tokens in one chapter = FAIL.

### F4 — Verbatim closing-line repetition across chapters

`"What remains is the moment after the alarm fires, when your body still wants to obey a prediction."` appears verbatim in Ch5 closing AND Ch11 closing. Likely the same template-slot firing per chapter with the closing-line slot not varying.

**Gate dimension:** closing-line uniqueness. Every chapter's last sentence must be unique across the book (full-string match). Repeat = WARN; >1 repeat = FAIL.

### F5 — Named-character continuity discontinuity

Ch1 protagonist: Priya. Ch5 protagonist: Amara. Ch11 protagonists: Chris, Jordan, Nia. The named-character roster shifts per chapter without bridge prose. Per `SOURCE_OF_TRUTH/story_atoms/character_roster.yaml` this may be by design (different scenarios), but the per-chapter rotation feels arbitrary; a reader cannot follow a single character's arc.

**Gate dimension:** named-character coverage. Either (a) one protagonist threads the whole book (Mira-style), OR (b) the cast is introduced as an ensemble in Ch1 and revisited consistently. Random per-chapter rotation = WARN.

### F6 — Pedagogical-cadence repetition

The 4-short-sentence rhythm `"The variables are real. The stakes are genuine. The uncertainty is not manufactured by your anxiety. It is manufactured by the conditions."` appears at structurally identical positions in Ch1, Ch5, Ch11. The same sentence-shape signaling the same beat each time.

**Gate dimension:** cadence-pattern repetition. Detect via 4-grams of sentence-length sequences; any 4-gram repeated more than once across chapters = WARN.

### F7 — Over-prescribed practices in a single chapter

Ch1 contains 3 distinct practices: cyclic sighing (Stanford-cited), 90-second 3-step writing exercise, Friday 4pm Notion alarm-ledger. A bestseller-grade chapter gives ONE practice and trusts the reader. Stacking 3 in one chapter is a generated-content tell — the system is trying to ensure SOMETHING lands rather than crafting the right one.

**Gate dimension:** practice-density per chapter. Count distinct prescribed-action paragraphs (sentences with imperative + concrete step); >2 distinct practices in one chapter = WARN.

### F8 — Citation grafting

`"Stanford researchers found it outperformed meditation for acute stress reduction. You do not need to believe that."` in Ch1. Body Keeps Score earns citations via embedded narrative; here the Stanford reference reads as inserted credibility.

**Gate dimension:** harder to detect automatically. Could approximate via: citation-density per chapter vs trade-pub anchor density (closed-loop step C — anchor corpus required).

---

## §6 What the existing gates correctly caught + what they missed

**Caught:**
- Ch1 + Ch11 chapter_flow defects (PR #1185 fix)
- ch5 + ch12 scene_anchor_density clusters (PR #1180 + PR #1183 fixes)
- Bestseller_craft hit production floor (0.6338 ≥ 0.55)
- Identity-stages registered as present (book_pass)

**Missed (this calibration found):**
- F1 templated-paragraph repetition (3+ instances of the same mechanism block template)
- F2 broken slot fragments (≥4 distinct artifacts across the book)
- F3 off-doctrine teacher-bank overrun (multiple paragraphs of Krishna / Bhakti / generic Buddhist content in an ahjan-Tantric book)
- F4 verbatim closing-line repetition across chapters
- F5 named-character continuity discontinuity
- F6 pedagogical-cadence repetition
- F7 over-prescribed practice density
- F8 citation grafting (hardest to auto-detect)

**Verdict:** the gap between Layer 1 PASS and Layer 3 FAIL is exactly what the synthesis doc predicted. F1-F8 are the dimensions a register gate (closed-loop step D) must measure.

---

## §7 Comparison to trade-pub register (anecdotal — full anchor corpus is step C)

The best authored prose in the book — Ch1's Priya scene, Ch11's Chris-mother Thanksgiving scene, Ch11's Nia-therapist exchange — reads at trade-pub register. Specific, concrete, restrained, the body doing the work.

The worst — Ch5's templated mechanism blocks, the Bhakti Yoga paste, "Ahjan's the practice" 3-word artifact, Ch11's "Where Ahjan departs from the usual framing is here" appearing twice in one chapter followed by off-doctrine content — reads at KDP indie workbook register at best, or at "generated content" register at worst.

The book contains BOTH. Currently mixed. The fix is to suppress the worst (via gate) while preserving the best.

---

## §8 Recommendations ranked by leverage

### LIFT-TO-BESTSELLER (highest impact × moderate effort)

1. **Fix F2 (broken slot fragments) — IMMEDIATE.** This is a HARD-FAIL gate candidate. Any sentence-start integrity violation should hard-fail production. Pearl_Dev session, small fix. Without this, every render leaks renderer artifacts.

2. **Fix F1 (templated mechanism-block repetition) — HIGH.** The system has the recurrence_report that strips short-phrase clusters but apparently doesn't catch paragraph-level structural-template repetition. Pearl_Dev: extend dedupe to detect structurally-similar paragraphs (e.g. cosine-similarity > 0.85 on sentence-by-sentence basis within a book). WARN at 1 instance; FAIL at 2+.

3. **Fix F3 (off-doctrine teacher-bank overrun) — HIGH.** TEACHER-MODE-WRAPPER-SEMANTICS-01 cap entry's wrapper-line-budget rule (HOOK ≤1, SCENE/STORY ≤2, others cadence-only) is currently NOT enforced. The teacher_bank wrapper is outputting paragraphs of off-doctrine content in voice slots — that's the explicit prohibition. Pearl_Dev: add per-slot wrapper-line-count enforcement in the renderer. Plus: per-teacher doctrinal vocabulary allowlist that hard-fails on token-class violations (`Krishna` etc. for ahjan).

4. **Fix F4 (verbatim closing-line repetition) — MEDIUM.** Trivial gate: closing-line uniqueness check. Pearl_Dev: 1-line addition.

### DOUBLE-DOWN (preserve what's working)

5. The Priya scene (Ch1), Chris-mother scene (Ch11), Nia-therapist exchange (Ch11) are at trade-pub register. Whatever atom + render pipeline produced those is doing the right thing — protect it. Could be the `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` engine-bank (per BESTSELLER-INJECTIONS-MANDATORY-01) — those scenes likely came from there.

### AUTHOR (Step C — anchor corpus)

6. **Pull 5-10 verbatim paragraphs from Body Keeps Score / Levine / Maté / Foo into `artifacts/reference/trade_pub_anchors/`** for register comparison. Operator picks. Without anchors, F8 (citation-grafting detection) and F3-F4-F6 thresholds are calibrated against vibes, not the actual target.

### RETIRE / RECONSIDER

7. The "Ahjan's framework / reading / departs from / returns to" template-frame block in the chapter overlay system is firing into empty content multiple times per book (F2). Either the slot must be guaranteed to land filled, or the overlay block should be removed from the pipeline. Pearl_Architect ratify.

8. Cyclic-sighing-with-Stanford-citation block appears verbatim in Ch1 (and possibly elsewhere if it's a template). Decide: is this a per-chapter practice or a per-book practice? If per-book, it should appear ONCE; if per-chapter, the citation needs to vary or be dropped after first appearance.

---

## §9 Operator-decision-required items

1. **Doctrinal frame governance.** Frame governor detected `karma` violation in Ch12 but did NOT enforce (softened/stripped/hard_fail all empty). Decision: should production-profile escalate detected absolute_claim violations from "recorded" to "softened" or "stripped"? Currently the violation is tolerated. (Recommend: STRIPPED under production.)

2. **Named-character roster strategy.** Single-protagonist (Mira-style across all 12 chapters) or per-chapter rotation (Priya/Amara/Chris/Jordan/Nia)? The current rendering does the latter without clear continuity. Per-roster_yaml convention vs author-craft tension.

3. **Teacher-bank wrapper enforcement.** TEACHER-MODE-WRAPPER-SEMANTICS-01 cap locked the rule. Implementation (`ws_teacher_wrapper_semantics_impl_20260517`) has not landed per last router-state check. The off-doctrine paragraphs F3 documents are direct evidence that the cap entry is currently aspirational, not enforced. Decision: prioritize that impl ws before scaling production renders.

4. **Vision canonical authority order.** When this verdict surfaces conflict between `PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md §2` ("12 chapters per book" — kept per recent revert) and the actual extended_book_2h's behavior with F006 12-chapter arc, which wins? Recommendation: amend canonical §2 OR explicitly document the per-runtime-format override convention. The drift is real.

---

## §10 Closed-loop status after this verdict

- (A) **Calibration: DONE** (this MD)
- (B) DONE last turn (PR #1191 — scorecard + drift fixes; partial revert by operator on drift-fix subset)
- (C) **Anchor corpus: BLOCKED on operator picks** — needs you to pull 5-10 verbatim paragraphs from Body Keeps Score / Levine / Maté / What My Bones Know into `artifacts/reference/trade_pub_anchors/`
- (D) **Register gate spec: NEXT** — author `docs/PEARL_PRIME_REGISTER_GATE_SPEC.md` keyed off F1-F8 with concrete failure-mode thresholds. Will be authored in same PR as this verdict.
- (E) **Wire scorecard emit: AFTER D** — Pearl_Dev session; ship_readiness aggregator
- (F) **Blind-10 cadence: operator-time** — schedule

---

## §11 Bottom line

The 2hr × ahjan × gen_z × anxiety book passes all machine gates. **It should not ship at trade-pub register.** The system is delivering at `structurally clear` not at `system working`.

The good news: the gap is identified, evidenced, and actionable. F1-F8 are specific, measurable defects. Step (D) — register gate spec — can be authored against this calibration data and will have teeth, not guesses. Step (C) — anchor corpus — needs your picks to calibrate the trade-pub register comparator.

After (C) + (D) + (E) land, every future render will emit a Layer 1 + Layer 2 + Layer 3 + register-gate verdict, not just a Layer 1 PASS. That closes the loop the synthesis doc named.

---

## Reproduction

This verdict was authored by reading book.txt chapters 1, 5, 11 in full + cross-referencing `quality_summary.json`, `chapter_flow_report.json`, `memorable_line_report.json`, `editorial_report.json` in the same output dir. To re-score the same book, sample the same 3 chapters and apply ONTGP per `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md §3` Layer 3.

To re-score a DIFFERENT book on the same scorecard, follow the same protocol with the new book's output dir.

# Bestseller Alignment Audit — research corpus vs. what the pipeline actually produces

**Agent:** Pearl_Editor (consulting EI v2)
**Date:** 2026-06-16
**Project:** proj_pearl_prime_bestseller_rebase_20260425
**Subsystem:** ei_v2 ; pearl_prime
**Chunk:** E of 5 (parallel, independent of chunk A — corpus-vs-output, no schema needed)
**Scope:** AUDIT + RECOMMENDATIONS only. No code/atom/spec edits.

---

## Operator's question (verbatim)

> "all the things we see in bestseller research — are we doing that, and is it making great books? Is there another way to make interesting, engaging, bestseller books?"

## One-paragraph answer

**We are *documenting* nearly every bestseller lever the research names, and the system can *render* several of them well at the local-paragraph level — but most of the high-value levers are enforced only by (a) a human Layer-3 read or (b) a *defect* gate that punishes bad prose without ever *selecting for* good prose.** The result is exactly what the operator reports: books that pass structural gates and contain genuinely good hooks and stories, yet "feel assembled." The dominant failure is **not** atom scarcity and **not** weak research — it is a **composition layer** that (1) stitches good atoms together with a large bank of generic, disembodied "bridge" lines and (2) reuses the same doctrine/REFLECTION atom near-verbatim across chapters when chapter-specific content runs thin. Both behaviors are precisely what the corpus tells us bestsellers must NOT do. The "another way" the operator is reaching for already exists in this repo as written specs (BESTSELLER_GAP_AUDIT §4–§5: 13 missing reader-experience atom types + 5 missing metadata fields) — it has simply never been wired. **The frontier is the composer + the selection schema, not the prose prompts.**

This audit independently reproduces the conclusion of `docs/BESTSELLER_GAP_AUDIT.md` (Pearl_Architect) from a different direction — by reading the rendered books and the gate code rather than the planner — and the two converge.

---

## Evidence base

| Source | What it gave this audit |
|---|---|
| `docs/BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md` (814 ln) | The 5 universal levers + per-topic 9/10 rubrics → the lever checklist (§1 below) |
| `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` | The craft HOW: Orient/Name/Turn/Give/Pull, hook friction, aha types, exercise setup, integration landing, scene specificity, repetition caps, cadence + §13 scoring rubric |
| `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` | The 4-layer acceptance contract; the canonical statement that machine gates prove `structurally clear` but NOT `bestseller register` |
| `docs/BESTSELLER_SPINE_WRITER_SPEC.md`, `docs/BESTSELLER_STRUCTURES.md`, `docs/BESTSELLER_ATOM_ROUTING.md`, `specs/SPEC_5_VARIANTS_AND_BESTSELLER_BEAT_WIRING.md` | Spine contract, 12 structures + THREAD-type taxonomy, beat-routing wiring status |
| `docs/BESTSELLER_GAP_AUDIT.md` (Pearl_Architect) | The independent planner-side diagnosis (theory/runtime gap; 13 missing atom types; schema-not-prose) |
| `phoenix_v4/quality/ei_v2/dimension_gates.py` | What EI v2 *actually* measures per chapter |
| `phoenix_v4/quality/register_gate.py` | What the register gate F1–F11 *actually* measures (defect detectors) |
| `phoenix_v4/rendering/chapter_composer.py` + `config/rendering/{bridge_transition,within_slot_bridge}_families.yaml` | The bridge-injection layer (the "assembled" feel source) |
| `artifacts/qa/duration_ladder_20260615/` (8 rendered books, same persona/topic = `gen_z_professionals`/`anxiety`, 12 ch each) | Output-vs-research evidence: register reports + the actual `book.txt` prose, read by eye |

**EI v2 note:** The QA dirs ship `register_report.json` per tier but **no `ei_v2_report.json`**. EI v2's per-chapter dimension gates (uniqueness/engagement/somatic/cohesion/listen) were read directly from `dimension_gates.py` to establish what EI v2 can and cannot measure. No paid API used; all evidence deterministic/local per guardrails.

---

# §1. The research's claimed bestseller levers — as a checklist

Distilled from the benchmark research (5 universal patterns + the per-topic rubrics) and the overlay spec (the craft execution layer). These are the levers a book must hit to read like *Body Keeps the Score / Burnout / Dare*, not KDP-indie-workbook register.

| # | Lever | What the research says it is | Where named |
|---|---|---|---|
| L1 | **Opening hook = productive discomfort** | First 500 words: specific sensory scene OR counterintuitive claim → brief normalization → promise of mechanism. Friction, specificity, or consequence-first. NOT topic-label / temporal-frame / definition openers. | Research §3, §Exec; Overlay §5 |
| L2 | **Validation before instruction** | Name the experience precisely ("that's exactly it") BEFORE offering any framework or exercise. | Research §Exec pattern 1 |
| L3 | **Named mechanism (memorable model)** | A concrete biological/psychological model the reader can name and redeploy (habit loop, stress cycle, amygdala/cortex split). Mechanism > motivation. | Research §Exec pattern 2; Overlay "Name" |
| L4 | **Within-chapter arc: Recognition → Mechanism → Practice** (= Orient/Name/Turn/Give/Pull) | Every chapter: place reader inside a moment → name the pattern with surprise → a felt turn/reframe → a usable tool → forward pull. | Research §1; Overlay §4 |
| L5 | **Real aha in STORY** (unpredicted consequence / visible mechanism / accumulating cost) | The story must *reveal* something the reader did not predict, not merely illustrate a known point. | Overlay §6.1 |
| L6 | **Story specificity (named people, concrete sensory detail)** | Named composites with concrete detail; ≥1 human story per chapter. Generic archetypes create no investment. | Research §Exec dim 1; §Pacing |
| L7 | **Author credibility via personal disclosure** | Intimate first-person disclosure of the problem as method, not testimony. Impersonal clinical writing underperforms. | Research §Exec pattern 3 |
| L8 | **Exercise design + setup** | 1 short exercise per chapter; named time, single-focus, somatic, defined end-state; preceded by a setup sentence naming the felt state so the action has stakes. | Research §4, §Exec pattern 4; Overlay §6.2 |
| L9 | **Permission granting** | Explicit, sparse, chapter-specific permission (to grieve, rest, feel afraid while acting). NOT generic reassurance. | Research §Exec dim 3; Overlay §11.4 |
| L10 | **Voice/register = warm-clinical** | Knowledgeable-friend-who's-been-there. Not cold-academic, not cheerleading. Embodied, specific, trustworthy. | Research §2 |
| L11 | **Chapter-end pull (THREAD)** | Light open question / named unresolved tension / door visibly ajar → momentum into next chapter. Articulable, not "more to explore." | Research §Pacing; Overlay §7.2 |
| L12 | **Integration landing (not summary)** | Chapter closes by naming what changed / what remains / grounding in the body — exactly one, ≤60 words. Never a summary slide. | Overlay §7.1 |
| L13 | **Pacing: story:mechanism:exercise ≈ 60:25:15** | Narrative-dominant. Too much theory breaks flow; the "dry/academic" complaint. | Research §Pacing |
| L14 | **Anti-genericity in SCENE** (3-detail rule) | ≥3 sensory details that could not appear in any other scene in the book. Specific lived detail over stock inventory. | Overlay §8 |
| L15 | **Repetition caps + anti-scaffolding** | No metaphor in >5 chapters; banned-word list (journey/powerful); phrase caps; "risk-marker" scaffolding phrases capped; freshness test on REFLECTION. | Overlay §9 |
| L16 | **Functional cadence** | Sentence rhythm serves emotional work (escalation/teaching/landing/exercise cadences), not just statistical variance. | Overlay §10 |
| L17 | **No flat middle / escalation before reassurance** | Middle deepens cost/contradiction/identity each time; relief is earned. Every 3rd chapter a stronger reward. | Overlay §11 |
| L18 | **Audiobook craft** (chapter length, breath pacing, exercise pause-bridging, somatic imperatives) | Chapters 18–28 min (~4–6k words); breath points; "pause here" before exercises; recap+bridge at chapter ends. | Research §5, §Exec pattern 5 |

---

# §2. Per-lever verdict — are we DOING it, and is it WORKING?

**Verdict legend:** `DOING+WORKING` (implemented and the rendered books show it landing) · `DOING+NOT-WORKING` (implemented but the rendered evidence shows it failing/degraded) · `NOT-DOING` (documented but not wired into the live spine path, or actively undermined).

**Methodology for "working":** read the actual `book.txt` for the standard / extended / deep tiers (same `gen_z`/`anxiety` content at increasing length); cross-checked against the register-gate findings and EI v2's measured dimensions.

| Lever | Doing? (impl / absent — file:line) | Working? (rendered-book + gate evidence) | **Verdict** |
|---|---|---|---|
| **L1 Hook = friction** | DOING. Recognition bank `config/content_banks/anxiety_genz_scene_recognition_bank.yaml` (40 variants); F11 detector guards scene-first openings `register_gate.py:520-700`. **BUT** the bank's BookSlotTracker routing is **pilot-path only**; on the main spine path it is a "no-op placeholder, not yet consumed" (`docs/BESTSELLER_ATOM_ROUTING.md:96-99`; `SPEC_5 §1` status table: "❌ NOT wired"). | **Working at the paragraph level for this one persona.** Standard-book Ch1 opens: *"You answered the message at 11pm… your chest would not let you not answer it. You checked for a reply at 11:14."* — textbook specificity hook (Overlay §5 Pattern 2). Ch11 opens on the "three dots" — concrete. F11 fired 0 abstract-opening WARNs on these books. | **DOING+WORKING** (for `gen_z×anxiety`; see L1-coverage caveat below) |
| **L2 Validation-before-instruction** | DOING via spine ordering: `BESTSELLER_SPINE_WRITER_SPEC` mandates recognition/legitimacy in ch1-2, first practice ≥ch5. | Spine respects it — Ch1 names the pattern before any ask. | **DOING+WORKING** |
| **L3 Named mechanism** | DOING. `BESTSELLER-INJECTIONS-MANDATORY-01` injects mechanism at sec 2/5/9; `selected_mechanism_resolver.yaml` fills `{selected_mechanism}`. | Present — "sensation vs. story" mechanism is named and re-used. **BUT** it is named *generically* ("the mechanism behind this pattern is small and stubborn") rather than as a *named, retellable model* — the research's bar (L3) is a model the reader can name back ("the stress cycle"). The books have a mechanism but not a **branded** one. | **DOING+NOT-WORKING** (present but not memorable/named per research bar) |
| **L4 Orient/Name/Turn/Give/Pull** | DOING as **documentation + human gate**: Overlay §4 + Scorecard Layer-3 ONTGP. **NOT** a machine gate — no code scores Turn/Give/Pull. EI v2 does not measure any of the 5 moves (`dimension_gates.py` measures uniqueness/engagement/somatic/cohesion/listen only). | **Partially working, unverifiable by machine.** Orient and Give are present in the prose; **Turn is the weak move** — chapters teach but rarely overturn the reader's self-model (matches Overlay §4 failure mode). No automated signal exists to catch a missing Turn; it relies entirely on a human read that the operator says isn't happening at scale. | **DOING+NOT-WORKING** (enforced only by a human read; Turn under-delivered) |
| **L5 Story aha** | NOT-DOING as enforced. Overlay §6.1 defines aha types A/B/C; "Story payoff classifier (aha type tagging)" is listed as a **future** validator (Overlay App. B). No code tags or requires an aha type. | STORY atoms themselves are decent (Priya at 11:47pm; Aisha's "friction" idea taken by the VP — a genuine Type-A unpredicted-consequence aha). So the *atoms* can carry aha. But nothing *guarantees* it, and nothing prevents a flat story shipping. | **DOING (atoms) + NOT-WORKING (unenforced)** |
| **L6 Story specificity** | DOING. STORY role taxonomy frozen (RECOGNITION/MECHANISM_PROOF/TURNING_POINT/EMBODIMENT); scene_anti_genericity gate + scene_anchor_density. | Working — named characters with concrete detail are present in every sampled chapter. | **DOING+WORKING** |
| **L7 Author disclosure / CONFESSION** | NOT-DOING. `BESTSELLER_GAP_AUDIT §4.12`: CONFESSION atom "missing — implied in research, not first-class." | The rendered books have **no** first-person author disclosure; voice is second-person throughout. The research's #3 universal pattern (intimate disclosure as method) is absent. | **NOT-DOING** |
| **L8 Exercise + setup** | PARTIAL. EXERCISE journeys exist (`enrichment_select.attach_exercise_journeys`) but attach **after** enrichment (`GAP_AUDIT §2.5`: "not yet a first-class planning concern"). Setup-sentence contract (Overlay §6.2) is **not** enforced by any gate. | **DOING+NOT-WORKING.** Exercises are present and somatic ("Sit somewhere quiet for two minutes…") but: (a) F7 fires **FAIL on 12/12 chapters** in standard/extended/deep — *over*-prescribed practice density, the opposite failure; (b) many exercises begin cold (no felt-state setup). Note F7's FAIL is partly a threshold artifact (≥4 prescribed-action paragraphs), but it shows exercise pacing is uncontrolled. | **DOING+NOT-WORKING** (over-dense; setup unenforced) |
| **L9 Permission** | PARTIAL. PERMISSION is a real slot (`_TEACHER_FALLBACK_SLOTS`), injected by structures that carry it. But `GAP_AUDIT §3.4`: PERMISSION coverage "medium-low," and the spec wants *sparse, chapter-specific* permission, which is unenforced. | Permission lines exist but read generic; no signal enforces chapter-specificity or sparseness (Overlay App.B "Permission specificity checker" = future). | **DOING+NOT-WORKING** |
| **L10 Voice = warm-clinical** | DOING via prohibited-terms guard (`topic_skins.yaml`; spine global ban list incl. journey/transform/empower) + teacher doctrine (F3 off-doctrine detector). | Working — the books avoid cheerleading and academic register; the doctrine REFLECTION ("weather of the body is not the climate of the self") is genuinely warm-clinical. | **DOING+WORKING** |
| **L11 Chapter-end pull (THREAD)** | PARTIAL/DETACHED. THREAD is a slot with a structure-assigned type (`BESTSELLER_STRUCTURES` THREAD-type column). **BUT** `GAP_AUDIT §4.7`: "THREAD is a slot label, not a propulsion class"; composer uses **hardcoded fallback THREAD keyword pools** (`chapter_composer.py:1926` `_FALLBACK_THREAD_KEYWORD_POOLS`) when atom routing is absent. | **DOING+NOT-WORKING.** Chapter ends do not reliably create *articulable* forward tension; the fallback generic THREAD options ("…awareness does not fix anything…") are interchangeable across chapters — exactly the "moveable to 10 other chapters" failure (Overlay §5/§7.2). | **DOING+NOT-WORKING** |
| **L12 Integration landing** | NOT-DOING as enforced. Overlay §7.1 defines the 3 allowed landing functions; no gate checks INTEGRATION does exactly one. | INTEGRATION blocks drift into summary (the §7.1 failure pattern). No machine catches it. | **NOT-DOING (unenforced)** |
| **L13 Pacing 60:25:15** | NOT-DOING. No ratio is measured anywhere. The 10-slot SOMATIC grid fixes *slot positions*, not story:mechanism:exercise *proportion*. | Unmeasured. Eyeball: the books are heavy on short disembodied bridge/REFLECTION fragments, light on sustained story — likely far from 60% narrative. | **NOT-DOING** |
| **L14 Scene 3-detail rule** | DOING. scene_anti_genericity_gate + scene_anchor_density_report (Scorecard Layer-1, "0 violations required"). | Working — scenes carry specific detail (the "oat-milk film," HVAC hum, "47 messages past your last reply" register). This is one of the better-wired levers. | **DOING+WORKING** |
| **L15 Repetition caps + anti-scaffolding** | DOING as **defect gate**: register F1 (templated paragraphs), F4 (closing-line repeats), F6 (cadence 4-gram). Overlay §9 word/phrase caps are mostly **not** machine-checked. | **DOING+NOT-WORKING — this is the dominant defect.** F1 fires **57 findings (7 FAIL) on standard, 191 (16 FAIL) on the 6h book**. Root cause is twofold and both are composition-layer, not atom-scarcity: (1) the composer injects generic **bridge lines** from a 256+840-entry bank (`within_slot_bridge_families.yaml` / `bridge_transition_families.yaml`); the composer's own docstring documents the bug — *"DEFECT 1… the hardcoded fallback pool fires"* (`chapter_composer.py:124-130`); (2) the same doctrine REFLECTION atom (`SOURCE_OF_TRUTH/composite_doctrine/anxiety/REFLECTION/CANONICAL.txt`) is reused **near-verbatim across ch1/2/8/9/11** (F1 cluster size 5). | **DOING+NOT-WORKING** (defect gate fires hard; cause = composer policy) |
| **L16 Functional cadence** | PARTIAL. EI v2 `gate_listen_experience` scores rhythm_variance / paragraph_breathing (phase ≥3 only). Overlay §10's *function-matched* cadence (different rhythm per atom type) is not measured. | Statistical variance is checked; functional cadence is not. The disembodied bridge lines actively flatten cadence (one-sentence aphorisms stacked). | **DOING+NOT-WORKING** |
| **L17 No flat middle / escalation** | NOT-DOING. No machine measures escalation or "every-3rd-chapter reward." transformation_arc/heatmap checks identity-stage progression, not reward density. | The mid-book reuses the same doctrine atom and bridge stack (Ch11 shows ~18 consecutive bridge lines) — the **flat middle** failure the overlay §11.1 names, made worse by reuse. | **NOT-DOING** |
| **L18 Audiobook craft** | PARTIAL. `duration_fit.py` + format word_ranges target chapter length; tts_readability scores TTS-safety. "pause here" exercise-bridging + recap+bridge chapter-ends are **not** systematically inserted. | Chapter length: the 12-chapter spine does NOT re-chapter per tier, so micro-book chapters are ~600 words (under the 18-28 min / 4-6k word target) and deep-book chapters are far over. Breath/pause-bridging absent. | **DOING+NOT-WORKING** |

### Scorecard tally

| Verdict | Count | Levers |
|---|---|---|
| **DOING+WORKING** | 5 | L1*, L2, L6, L10, L14 |
| **DOING+NOT-WORKING** | 9 | L3, L4, L5, L8, L9, L11, L15, L16, L18 |
| **NOT-DOING** | 4 | L7, L12, L13, L17 |

*L1 working only for the single `gen_z×anxiety` persona that has a recognition bank; 14 of 15 P1–P5 banks are unbuilt (`BESTSELLER_ATOM_ROUTING §8`), and even this one isn't routed on the main spine path.

### The structural finding behind the tally

Every `DOING+WORKING` lever is one that is enforced by a **Layer-1 structural gate that selects/guards content** (recognition bank, scene_anti_genericity, prohibited-terms, STORY taxonomy). Every `DOING+NOT-WORKING` or `NOT-DOING` lever is one that is enforced **only by**:
- a **human Layer-3 read** (L4, L12) that the operator says isn't happening at corpus scale, OR
- a **defect detector** that punishes bad output without ever *selecting for* the good version (L15 register F1/F4/F6; L8 F7), OR
- **nothing at all** (L13, L17).

This is the mechanical reason for the operator's lived experience. From the scorecard's own words: *"machine gates can prove `structurally clear`… they cannot prove `bestseller register`."* The gates that exist are **necessary-but-negative**. There is no positive bestseller-lever scorer in the loop, and EI v2 — despite the name — does **not** measure engagement in any bestseller sense (`gate_engagement` is literally `min(1.0, word_count/80)`).

---

# §3. Gaps + new levers — "another way to make interesting, engaging, bestseller books"

The operator asks two things: where are the gaps, and is there another way? The gaps are §2's right-hand columns. The "another way" is to **stop trying to fix this with prose prompts and instead make the highest-impact levers first-class in selection + composition.** Below are 5 concrete new levers, prioritized by impact ÷ effort, each tied to an owner and flagged for overlap with the atom-cohesion chunks (A–D) and the composer-frontier lane.

> **Impact/effort scale:** Impact = how much closer to `bestseller register` this moves the median book. Effort = build cost given what's already wired.

### NEW LEVER 1 — Kill the generic bridge-injection + doctrine-reuse policy (the "assembled" feel) ⭐ HIGHEST IMPACT, LOW EFFORT

**The gap:** The single biggest contributor to "feels assembled" is the composer stitching atoms with generic aphoristic bridges from a 1,096-entry bank, plus reusing the same doctrine REFLECTION across 5+ chapters. This is L15/L16/L17 and it dominates the F1 register findings (57→191 as books lengthen). The composer's own docstring admits the fallback fires because planner arc-role vocab ≠ bridge-bank emotional-job vocab (`chapter_composer.py:124-130`).

**The new lever:** (a) Fix the arc-role→bridge-job mapping so `_select_bridge_candidate` actually fires (eliminating the generic hardcoded fallback pool); (b) add a **book-level uniqueness budget** to the composer so no bridge line and no doctrine paragraph repeats >1× per book (the register F1/F4 thresholds become a *composition constraint*, not just a post-hoc complaint); (c) demote bridges from "every slot seam" to "only where the arc genuinely needs a transition."

**Owner:** **Pearl_Dev** (composer fix) + **Pearl_Architect** (uniqueness-budget policy as a cap).
**Overlap:** This **IS the composer-frontier lane** (MEMORY: project_composer_frontier_wave_outcome — #1589 engine / #1590 atoms). It is **distinct from atom-cohesion chunks A–D**: those raise atom *quality/coverage*; this fixes how atoms are *assembled*. The two are complementary — better atoms won't help while the bridge layer dilutes them.
**Why first:** Lowest effort (config + mapping fix on an already-identified defect), highest impact (directly clears the F1 HARD path and the dominant "assembled" signal).

### NEW LEVER 2 — Promote the §13 overlay rubric into a deterministic *positive* "authoring scorer" ⭐ HIGH IMPACT, MEDIUM EFFORT

**The gap:** L4/L5/L11/L12 are enforced only by a human Layer-3 read that isn't happening at scale. EI v2 measures the wrong things for this purpose. There is no machine signal that *rewards* a present Turn, a real aha, an articulable THREAD, or a clean integration landing — only signals that *punish* repetition.

**The new lever:** Build a deterministic **authoring scorer** (no LLM — heuristic, same engineering style as `register_gate.py`) that scores the Overlay §13 12-criterion rubric per chapter and emits a 0–1 "authoring score." Several criteria are already partly detectable (hook friction ≈ F11; integration landing ≈ a ≤60-word + no-summary-phrase check; THREAD articulability ≈ a specificity/uniqueness check). Wire it as an **advisory** EI-v2 dimension first (alongside listen_experience), then graduate the load-bearing ones (Turn-present, aha-present, THREAD-specific) to blockers under `--quality-profile flagship`.

**Owner:** **Pearl_Editor** (rubric → heuristic spec) + **Pearl_Dev** (scorer impl in `phoenix_v4/quality/`).
**Overlap:** Complements chunk A if A delivers a schema (the scorer can read aha-type / propulsion-type tags directly instead of re-deriving them) — **flag a dependency, not a conflict**. This is the missing *positive* half of what register_gate started as the *negative* half.
**Why second:** Turns the operator's "is it making great books?" from an un-checkable human judgment into a tracked metric — the prerequisite for any closed-loop improvement (Scorecard Layer-4 explicitly needs this to stop gates from gradient-descending into "passes all checks but feels generated").

### NEW LEVER 3 — Wire the 13 missing reader-experience atom types + 5 metadata fields (the GAP_AUDIT recommendation) — HIGH IMPACT, HIGH EFFORT

**The gap:** L5, L7, L11, L17 and the "Turn" half of L4 all fail for the same root reason `BESTSELLER_GAP_AUDIT §4–§5` names: the taxonomy is **section types, not reading-experience functions**. The selector cannot deliberately choose "desire-naming vs pain-naming," "objection-handling before practice," "story-turn," "confession," "myth-bust," "chapter-propulsion" — because none are first-class. Missing metadata: `proof_mode`, `tension_type`, `reader_objection`, `shame_level`, `propulsion_type`/`callback_role`.

**The new lever:** Exactly the GAP_AUDIT §5.4 recommendation — add the 5 metadata fields and the highest-value atom types (start with **STORY_TURN, OBJECTION_HANDLING, CHAPTER_PROPULSION, CONFESSION** — these map directly to the 4 NOT-DOING / weakest levers). Make exercise-journey + propulsion *govern* selection from the start rather than attach after enrichment.

**Owner:** **Pearl_Architect** (schema + cap) → **Pearl_Dev** (selector) → **Pearl_Editor + Pearl_Writer** (authoring the new atom classes).
**Overlap:** **This is the core of chunk A's territory (schema).** Flag as the **primary cross-chunk dependency**: Lever 2's scorer and Lever 3's schema should be designed together — the scorer consumes the tags the schema produces. Do NOT build them in conflicting passes.
**Why third:** Highest ceiling (it's the GAP_AUDIT's "single biggest reason books feel generic") but highest cost and longest lead time; gate it behind Levers 1–2 landing so the wins are visible before the big schema lift.

### NEW LEVER 4 — Per-tier re-chaptering so chapter length hits the 18–28 min audiobook window — MEDIUM IMPACT, LOW-MEDIUM EFFORT

**The gap:** L18. The 12-chapter spine is held constant across all 8 duration tiers (INDEX.md: "chapter count is 12 at every tier; the format scales per-slot word targets"). This means micro-book chapters are ~600 words (≈4 min — "rushed and disconnected" per Research §Exec pattern 5) and 6h-book chapters are ~4,300 words but stuffed with repeated bridges. The research's single most specific audiobook finding (18-28 min chapters) is structurally unreachable at most tiers.

**The new lever:** Decouple chapter *count* from the spine for short/long tiers — collapse the 12-role arc into fewer, fuller chapters at micro/short tiers (so each clears the ~4k-word / 18-min floor) and split at deep tiers. This is a planning change, not an atom change. Pair with breath-pacing + "pause here" exercise-bridging inserts (cheap, mechanical).

**Owner:** **Pearl_Architect** (re-chaptering policy per tier) + **Pearl_Dev** (planner).
**Overlap:** Touches the duration-ladder work (MEMORY: project_duration_per_platform / compact_subset_vs_chapter_count) — **flag coordination** with whoever owns format_registry word_ranges; independent of chunks A–D.
**Why fourth:** Real listener-experience win, modest effort, but lower ceiling than 1–3 and only bites at the tier extremes.

### NEW LEVER 5 — Build the anchor corpus → activate F8 (the only lever that compares us to *real* bestsellers) — MEDIUM IMPACT, MEDIUM EFFORT

**The gap:** Every gate today is *intrinsic* (does the book avoid defects?). **Nothing compares our prose to actual trade-pub bestseller prose.** Register F8 (citation grafting / corpus comparison) is **deferred pending `artifacts/reference/trade_pub_anchors/`** (`register_gate.py:17`, Scorecard §cross-refs). The Scorecard's Layer-4 blind-10 is the only true bestseller-register check and it's operator-attended/manual.

**The new lever:** Assemble the trade-pub anchor corpus (paragraph exemplars from the named bestsellers already cited in the research — Body Keeps the Score, Burnout, Dare, Feeling Good, etc.), then activate F8 + a register-distance metric: how far is our paragraph distribution (sentence-length, embodiment, abstraction ratio) from the anchor distribution? Deterministic, no LLM. This gives a *calibration target* the intrinsic gates can be tuned against.

**Owner:** **Pearl_Research** (corpus assembly) + **Pearl_Dev** (F8 + distance metric) + **Pearl_Editor** (anchor selection).
**Overlap:** Independent of chunks A–D and the composer lane; feeds the Scorecard Layer-4 closed loop (which the Scorecard says drives anchor-refresh, gate-calibration, and atom priorities).
**Why fifth:** Unlocks the only *external* yardstick and the closed loop the Scorecard demands — but it's a research-build with a longer payoff curve, so it rides behind the levers that move this week's books.

---

## §4. Direct answers to the operator

**"Are we doing the things bestseller research says?"**
Mostly on paper (5 docs are excellent and complete), partly in practice. 5 of 18 levers are genuinely wired and working; 9 are documented-but-degraded; 4 are documented-but-absent. The wired-and-working ones are exactly the levers a *content-selection gate* protects (hooks, scenes, named-character stories, voice). The failing ones are the levers left to a human read or a defect detector.

**"Is it making great books?"**
It's making **structurally clean books with good local prose and a persistent assembled feel.** The hooks and stories are real; the connective tissue and the chapter-level *turn/pull/landing* are not. By the Scorecard's own language the median book is `structurally clear`, occasionally `authored candidate`, and **not** `bestseller register`. The 8 QA books all HARD_FAIL the register gate — driven by F1 repetition (the bridge/doctrine reuse), not by missing content.

**"Is there another way?"**
Yes, and it's not "write better prompts." The highest-leverage path is **composition + schema**, in this order: (1) fix the bridge/reuse policy that dilutes good atoms [composer-frontier, this week], (2) build a *positive* authoring scorer so "great" becomes measurable [Pearl_Editor+Pearl_Dev], (3) make the 13 missing reader-experience atoms + 5 metadata fields first-class so the system can *intend* aha/turn/objection/propulsion [chunk-A schema], then (4) per-tier re-chaptering and (5) the real-bestseller anchor corpus. Levers 1–2 are low/medium effort and move the median book the most; 3 is the ceiling-raiser; 4–5 round it out.

---

## §5. Cross-chunk + lane coordination flags

| This audit's lever | Overlaps | Coordination note |
|---|---|---|
| NEW LEVER 1 (bridge/reuse fix) | **Composer-frontier lane** (#1589/#1590) | Same lane. Distinct from atom-cohesion A–D (assembly vs. atom quality). Sequence first. |
| NEW LEVER 2 (authoring scorer) | **Chunk A (schema)** | Design scorer to *consume* A's tags; dependency, not conflict. |
| NEW LEVER 3 (13 atoms + 5 metadata) | **Chunk A (schema) — core overlap** | This is largely A's territory; do not build a parallel/competing schema. Co-design with Lever 2. |
| NEW LEVER 4 (re-chaptering) | duration-ladder / format_registry owners | Coordinate word_range ownership; independent of A–D. |
| NEW LEVER 5 (anchor corpus / F8) | Scorecard Layer-4 closed loop | Feeds blind-10 calibration; independent of A–D + composer lane. |
| Atom-cohesion chunks A–D (general) | This audit | **A–D raise atom quality; this audit shows atom quality is NOT the binding constraint for the median book** — the composer assembly + missing-schema are. A–D are necessary for the ceiling (Lever 3) but will not, alone, clear the F1/"assembled" floor. Recommend A–D land *with* Lever 1, not instead of it. |

---

*End of audit. Deliverable per chunk-E scope: research-lever checklist (§1), per-lever doing/working verdict table (§2), gaps + 5 prioritized new levers with owners + overlap flags (§3). No code/atom/spec edits made.*

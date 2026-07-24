# Graphic Medicine / Therapeutic Essay — Style Bible

Touchstones: *Marbles: Mania, Depression, Michelangelo, and Me* (Ellen Forney), *Cancer Vixen* (Marisa Acocella Marchetto), *Epileptic* (David B.), *Stitches* (David Small), *El Deafo* (Cece Bell), *Tangles: A Story of Alzheimer's, My Mother, and Me* (Sarah Leavitt), *Taking Turns: Stories from HIV/AIDS Care Unit 371* (MK Czerwiec).

## 1. Market Contract

Readers are patients, caregivers, family members of the chronically or acutely ill, medical-community readers (a genuinely large secondary audience — nurses, med students, chaplains), and general readers seeking an honest account of a body in crisis. `graphic_medicine` shares its `parent_family` with `essay` (both are reflective/confessional registers built on `self_or_artifact_interaction`-adjacent grammar), but it is narrower and more load-bearing: the subject is always specifically illness, disability, or patient-care, and the genre's founding scholarship (MK Czerwiec and Ian Williams's `graphicmedicine.org`, the *Graphic Medicine Manifesto*) frames it explicitly as the intersection of comics and healthcare discourse — a form that can hold what clinical language cannot: the messy, embodied, subjective experience of being a patient (or a caregiver, or a clinician) that a chart or a portal message erases.

Per `main_character_interaction_grammar.yaml`, the genre is gated on `patient_care_or_family_pressure` — unlike `essay`'s solitary artifact-focus, graphic_medicine requires a living pressure axis: a clinician, a family member pushing a discharge timeline, a ward community. Per `modern_reader_story_doctrine.yaml`'s graphic_medicine block, the genre-native modern artifacts are body data, portals, appointments, charts, wearable metrics, pharmacy counters, and consent context — and the doctrine explicitly flags what to avoid: `miracle_cure`, `body_as_diagram_only`, `generic_hospital_scene`, `no_consent_axis`. Readers will reject inspiration-porn recovery arcs, clinical detachment that erases the patient's interior life, and any resolution that reads as medically dishonest. The contract is closer to `docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md`'s general anti-drift doctrine than most lanes: the body's actual, ongoing, unglamorous reality is the register, not a triumphant arc engineered for the reader's comfort.

## 2. Visual Rules

| Metric | Value |
|---|---|
| Words per page | 60–120 (`manga_pacing_by_genre.yaml::graphic_medicine`) |
| Words per balloon (max) | 35 |
| Silent-panel ratio | 0.20–0.40 |
| Reaction-shot frequency | Medium |
| Spread frequency | Rare — reserved for a diagnosis moment, a procedure, or a body finally seen/accepted |
| Narration tolerance | Moderate — lower than `essay`'s generous tolerance; the body's visual reality is allowed to carry more of the page than caption |
| SFX usage | Minimal |
| Background density | Moderate/clean — clinical spaces (exam rooms, wards, pharmacy counters) rendered with enough specificity to be legible as real institutional settings, without becoming procedural set-dressing |

**Medical-artifact rendering convention:** charts, scans, wearable-device readouts, and patient-portal text should be reproduced in-panel with enough fidelity to be readable as real documents (per the doctrine's `wearable_says_fine` and `patient_portal_message` catalysts) — a chart panel is doing the same structural work as the letter/photograph reproductions in `graphic_novel_us_literary`. The body itself is drawn with anatomical honesty appropriate to the condition (scars, asymmetry, a limb that moves differently, a face mid-seizure) rather than softened or symbolized away — the genre's founding premise is that the comics form can render subjective embodied experience that clinical illustration cannot, so the art should not retreat into diagram-only abstraction.

**Line weight:** steady and legible on clinical/procedural panels (medical accuracy matters — see failure mode 6); looser, more expressive on interior/somatic panels where the body's *felt* experience diverges from its clinical description (Forney's manic-episode pages vs. her flat clinical intake pages is the canonical contrast).

**Two-register panel discipline:** the genre routinely alternates between a *clinical register* panel (chart, scan, clean exam-room geometry, portal-message reproduction) and a *lived register* panel (the same information rendered through the patient's body/sensation) on facing or adjacent panels — the gap between the two is where the genre's meaning lives.

## 3. Pacing

**Page-turn triggers:** `mechanism_reveal`, `body_awareness_beat`, `reframe_moment`, `reader_mirror` (`manga_pacing_by_genre.yaml::graphic_medicine`). `mechanism_reveal` is genre-specific: the moment the reader (and often the patient) understands *how* the condition actually works in the body, rendered visually rather than lectured.

**Chapter hook family:** *clinical-vs-lived contrast opening.* Per the doctrine's catalysts, canonical openings include `wearable_says_fine` ("a wearable congratulates the protagonist on a normal day while their body knows the opposite") and `patient_portal_message` ("a patient-portal message arrives in language so clean it erases the messy thing the protagonist needs help saying"). The hook is the gap between institutional language and embodied truth, established in the first 1–3 panels.

**Chapter ending convention:** an honest status update, not a resolution — a plateau held, a small measurable gain, a setback named plainly. Never end a chapter on a miracle turn or a fully "solved" body. The genre's contract tolerates ongoing, open-ended illness/disability as a valid steady state, not only as a crisis awaiting cure.

**Scene-to-scene transitions:** clinical time markers (appointment dates, scan intervals, medication changes, ward shift-changes) rather than narrated prose skips — the medical calendar structures time the way the artifact's timestamp structures time in `essay`.

**Pacing rhythm within a chapter:** body-awareness beat (something felt or noticed) → clinical encounter (chart, appointment, procedure) → the gap between what was felt and what was said in the room → aftermath, alone with the information. The aftermath beat is mandatory — cutting straight from the clinical encounter to the next scene erases the patient's actual processing time, which is precisely what the genre exists to render.

## 4. Dialogue

**Two distinct registers that must not blur:**
- *Clinical-voice* — precise, procedural, sometimes accidentally cold; clinicians speak in options, percentages, protocol language. This voice is not villainized by default — per the genre's scholarship (Czerwiec is herself a nurse-cartoonist), clinicians are drawn with their own competence and limits, not as obstacles.
- *Patient-voice* — the messier, more particular, more embodied register; the patient's actual questions are rarely the clean ones the clinical encounter has room for. The genre's central dramatic engine is the gap between what a patient needs to ask and what the seven-minute appointment structure allows them to ask.

**Family/caregiver register:** distinct again — carries its own fear, often producing a "faster back to normal" pressure on the patient that is not malicious but is a genuine pressure axis per the `patient_care_or_family_pressure` gate (see the worked `body_memory_shojo` example: family visits "carrying their own fear, wanting a faster 'back to normal' than the body allows").

**Narration ratio:** moderate — lower than `essay`. Narration should clarify the gap between clinical and lived registers rather than replace either one; avoid narration that explains the diagnosis in advice-blog terms when the dialogue and body language could carry it.

**Portal/chart text as dialogue-adjacent:** written institutional language (portal messages, discharge instructions, chart notes) functions as a distinct "voice" in the page — reproduce it verbatim in its own lettering style, distinct from spoken dialogue, so its clinical cleanness is visually legible as a contrast to the patient's actual state.

## 5. Character

**Protagonist:** the patient (primary) or, in caregiver-register stories, the family member/caregiver themselves (Leavitt's *Tangles*, Czerwiec's *Taking Turns* both center the caregiver/nurse view). The protagonist's defining tension is dissociation from or renegotiation with their own body — a body that no longer does what it used to, or was never going to do what was expected.

**Clinical cast:** at least one clinician rendered with real competence and real limits — not a villain, not a savior. Per the genre's scholarship, the strongest work treats clinicians as people operating inside a system that itself has limits (time, protocol, resources), which is a more honest antagonist than any individual doctor.

**Ward/patient community:** where the setting supports it (inpatient, rehab, clinic-recurring), a community of fellow patients at different stages of the same condition — one further along, one further behind — functions as the protagonist's actual peer support, often more than family (see the worked `body_memory_shojo` example's rehab-ward roommates).

**Family/caregiver cast:** carries its own arc, not just a pressure function — a family member's exhaustion or fear should itself be drawn with the same non-judgmental specificity as the patient's experience.

**Cast density:** small-to-medium (4–8 named), because the genre needs room for both the clinical world and the domestic/caregiving world without either becoming generic.

## 6. Failure Modes

1. **Miracle cure** — a resolution where the condition is fully solved, especially via an event rather than sustained practice. Violates the doctrine's explicit `avoid: [miracle_cure]`.
2. **Body-as-diagram-only** — rendering the condition purely through clinical/anatomical illustration without ever showing the felt, subjective experience of living in that body. Violates `avoid: [body_as_diagram_only]`; defeats the genre's founding premise.
3. **Generic hospital scene** — a clinical setting rendered as undifferentiated set-dressing rather than a specific, researched space with real protocol and texture. Violates `avoid: [generic_hospital_scene]`.
4. **No consent axis** — patient decisions happening to the protagonist rather than with them; the genre requires the patient's agency and consent to be visible even in constrained circumstances. Violates `avoid: [no_consent_axis]`.
5. **Sanitized illness narrative** — softening symptoms, treatment side effects, or prognosis for reader comfort. The genre's credibility with its core (patient/caregiver/clinical) readership depends on medical specificity being accurate enough to be trusted.
6. **Advice-blog voice / inspiration-porn tone** — narration that turns the patient's experience into a lesson for the reader ("and that's how I learned to appreciate every day"), or frames disability/illness as existing primarily to teach able-bodied/healthy readers something.
7. **Clinician-as-villain shortcut** — making the doctor withholding or cruel to manufacture conflict, instead of the harder, truer conflict of a competent clinician working inside real institutional limits.
8. **Illness as pure metaphor** — using the condition symbolically without rendering its literal, physical reality; the genre's power is specifically in refusing to let the body become only a metaphor for something else.
9. **Caregiver erasure** — treating family/caregiver exhaustion as background noise rather than its own legitimate register (per `Tangles`, caregiver experience is a first-class subject, not scenery).
10. **Medical infodump** — explaining mechanism through dialogue lecture rather than through the `mechanism_reveal` page-turn trigger's visual/experiential rendering.

## 7. 48-Volume Shape

Graphic medicine's illness/care arc naturally maps onto a recovery-and-practice structure (per the worked `body_memory_shojo` rehab-ward example), generalized to any condition — acute, chronic, or degenerative:

**Volumes 1–12 — Onset / Admission:** the condition arrives or is diagnosed; dissociation from the body is the entry state; the clinical world (ward routine, first appointments, first portal messages) is established as the vessel. Family pressure begins here, carrying its own fear.

**Volumes 13–24 — Relearning / Living-With:** the spine of daily practice — therapy, medication management, monitoring — alternates small measurable gains with plateaus. The patient community (or caregiver community) deepens. Clinical pressure sharpens as institutional timelines (discharge readiness, insurance windows, protocol deadlines) collide with the body's actual pace.

**Volumes 25–36 — Setback:** a complication, relapse, or degenerative step forces renegotiation of everything built in the previous band. Family pressure peaks, often as exhaustion rather than malice (a caregiver pushing premature independence). The patient/ward community becomes the most reliable support system in this stretch.

**Volumes 37–48 — Practice, Not Finish Line:** functional stability (never "cure," even for acute conditions — the genre resists the closed loop) is reached and framed explicitly as an ongoing practice; the protagonist becomes an informal peer-support presence for someone newer to the same condition, closing the community loop without claiming the body is fixed. For degenerative or terminal conditions, this band instead resolves into an honest account of what continuity and care look like without a cure, following `Tangles`' and `Taking Turns`' precedent of caregiver/hospice registers that do not require survival to reach closure.

## 8. Panel Scaffolding

Per-panel fields (9):

1. `framing` — CU / MCU / MS / insert (chart, scan, wearable readout, portal-message reproduction) / clinical-wide (exam room, ward) / anatomical-detail
2. `beat_role` — one of {body_awareness, clinical_encounter, register_gap, family_pressure, ward_community, mechanism_reveal, aftermath, practice_beat}
3. `medical_artifact` — string or null; names the specific document/device in frame (`chart`, `scan`, `wearable_metric`, `patient_portal`, `pharmacy_bag`, `discharge_form`); when non-null, reproduce text/data with real fidelity
4. `voice_register` — one of {clinical, patient, family_caregiver, portal_text}; governs lettering style and diction; clinical and portal_text should read visually distinct from spoken patient/family dialogue
5. `body_state` — one of {dissociated, aware, in_procedure, post_procedure, fatigued, stable, relapsed}; governs anatomical rendering fidelity and line-weight looseness
6. `consent_axis_flag` — boolean; true on any panel where a medical decision is made or discussed, to enforce that the patient's agency/consent stays visibly present
7. `caption` — moderate narration, ≤25 words, clarifies clinical/lived gap rather than restating either register
8. `dialogue` — ≤20 words per speaker; clinical-voice trends terser than patient-voice
9. `silence_flag` — boolean; true on aftermath and register_gap panels, used to let the gap between clinical language and lived experience register without narration closing it prematurely

## 9. Locale Weighting

| Locale | Status | Notes |
|---|---|---|
| ja_JP | Active, distinct tradition | Japanese illness-manga (byōki-mono) exists but is culturally distinct from Western graphic medicine's patient-advocacy framing; localize toward `mechanism_reveal`/body-awareness beats already native to Japanese health-conscious seinen/josei readership; LINE Manga, ComicWalker viable |
| en_US | Origin market, thriving | Graphic medicine is an established Western category with real institutional infrastructure (`graphicmedicine.org`, med-school curricula use, Eisner-nominated scholarship); strongest natural home; Amazon manga digest, general graphic-novel trade channels |
| zh_TW | Active | Patient-advocacy and caregiving themes translate well; LINE Comics TW viable; family/caregiver register resonates with TW multi-generational household norms |
| zh_CN | Gray-zone per D-19 | Illness narrative generally lower political sensitivity than other gray-zone content, but specific conditions (mental health, HIV/AIDS, reproductive health) require case-by-case review; frame as body-awareness/wellness rather than systemic healthcare critique; AI disclosure required |
| ko_KR | Rendered + held per D-18 | Webtoon vertical-scroll format well-suited to chart/portal-message insert panels (single-artifact-per-scroll pacing); distribution held pending policy clarity |

---

*Sources: `docs/research/manga_craft/josei_adult_memoir.md` (structural/formatting template, full file); `docs/research/manga_craft/sports_competition.md` and `docs/research/manga_craft/supernatural_mystery.md` (9-section schema confirmation, Locale Weighting table format); `config/manga/manga_pacing_by_genre.yaml::graphic_medicine` lines 304–322 (words_per_page_range, silent_panel_ratio_range, page_turn_triggers, reference_corpus: "Cancer and the City (Graphic Medicine adjacent)", "Stitches", "El Deafo"); `config/manga/canonical_genre_list.yaml` graphic_medicine row lines 265–271 (label "Graphic Medicine / Therapeutic Essay", `parent_family: essay`, source_pacing yes); `config/manga/main_character_interaction_grammar.yaml` line 32 (`patient_care_or_family_pressure` gate); `config/manga/modern_reader_story_doctrine.yaml` lines 492–504 (graphic_medicine relevance_rule, catalysts `wearable_says_fine`/`patient_portal_message`, avoid list); `config/manga/canonical_genre_list.yaml` taxonomy_fallback lines 380–383 (default_emotional_engines: reflection/body_awareness/hope; default_visual_grammars: moderate_clean/intimate_realism); `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/procedural_medicine_family_food_social_historical.md` (`body_memory_shojo` worked example, rehab-ward 48-episode structure); WebSearch — GraphicMedicine.org / graphicmedicine.org "Graphic Medicine Manifesto" (MK Czerwiec, Ian Williams et al.); graphicmedicine.org comic review of *Epileptic* (David B.); Springer *Journal of Medical Humanities*, "Graphic Medicine and the Critique of Contemporary U.S. Healthcare" (2019); library-guide summaries (OHSU, UCSF, UC Irvine Graphic Medicine guides) confirming *Marbles* (Ellen Forney), *Cancer Vixen* (Marisa Acocella Marchetto), *Tangles* (Sarah Leavitt, 2010), *Taking Turns: Stories from HIV/AIDS Care Unit 371* (MK Czerwiec, 2017) as canonical touchstones.*

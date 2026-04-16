# Content Fragment Variation Writer Spec

Status: authoritative writer brief for duplicated, hard-coded, and off-topic book content
Date: 2026-04-15
Owner: Pearl_Content + Pearl_Editor
Applies to: registry atoms, renderer fallback prose, composer glue, enrichment gap repair, plan-layer content banks

## 1. Purpose

Phoenix Omega currently has several content quality failures that cannot be fixed by changing one phrase at a time. The same fragments are being reused across chapters, topics, personas, and books. Some fragments are also semantically wrong for the requested book, such as Buddhist enlightenment material appearing inside an anxiety book for Gen Z professionals.

This spec defines the writer-side replacement system. The writer must produce structured variant banks with enough range, metadata, and collision controls that the pipeline can render thousands of books without repeating the same scene anchor, practice instruction, transition, or doctrinal frame.

The goal is not to make one pilot sound better. The goal is to remove reusable content bottlenecks.

## 2. Confirmed Problem Locations

### 2.1 Renderer Scene Fallbacks

File: `phoenix_v4/rendering/book_renderer.py`

Confirmed issues:

- `_LOC_VAR_FALLBACKS` contains fixed fallback prose, including `weather_detail: soft daylight along the sill`.
- `_LOC_VAR_ROTATIONS` includes the same anchor as its first weather variant.
- `_normalize_generic_scene_lighting()` replaces generic light phrases with a fixed phrase instead of choosing from a large variant bank.
- `_FLOW_GLUE_VARIANTS` contains only four transition templates, so generated chapters repeat the same paragraph logic and cadence.

Observed output failure:

- `artifacts/pilots/plan_layer_verify/scene_anchor_density_report.json` flags repeated phrases such as `soft daylight along the sill` and `daylight along the sill`.

Writer action:

- Replace every hard-coded fallback family with a minimum viable variant bank.
- No global fallback may depend on one fixed sensory image.
- Each scene anchor family must have at least 20 variants before it is allowed to be used globally.

### 2.2 Composer Shaping Templates

File: `phoenix_v4/rendering/chapter_composer.py`

Confirmed issues:

- `_fallback_takeaway(thesis)` generates a single style of takeaway when source content is thin.
- `_shape_integration()` and `_shape_thread()` normalize content into recurring chapter endings.
- Existing mechanism text includes fixed explanatory prose such as `The nervous system does not distinguish between real threat and imagined threat... This is why knowing better rarely helps.`
- Generic scene light normalization still knows about `gray light through the window`.

Writer action:

- Supply variant banks for fallback takeaways, mechanism bridges, integration paragraphs, and chapter-thread closures.
- Each fallback family must include multiple rhetorical shapes, not only synonym swaps.

### 2.3 Enrichment Content Gaps

File: `phoenix_v4/planning/enrichment_select.py`

Confirmed issue:

- Missing slot content is rendered as visible markers such as `[CONTENT GAP: REFLECTION for anxiety ch7]`.

Observed output failure:

- The plan-layer pilot produced two REFLECTION gaps in chapters 7 and 8.

Writer action:

- Fill missing slot families before publication.
- Every required slot in every reference plan must have at least 10 topic-valid and persona-valid candidate atoms.
- Content gap markers are never publishable content. They are build failures.

### 2.4 Registry Duplicate Families

Files: `registry/*.yaml`

Confirmed issue examples:

- `registry/anxiety.yaml` repeats `The task is open. You have been looking at it for forty minutes...` across many chapters.
- Several registries repeat `Safety is not the absence of danger. It is the presence of connection...`
- Reflection prompts repeat across topics, including variations of `Where in your life do you run from what is difficult?`, `Notice a thought that repeats itself...`, and `What are you attached to...`
- Practice and integration instructions repeat across topics, including variants of `Sit quietly for five minutes...`, `Take one situation that usually triggers you...`, and `This week, return to one moment of clarity...`

Writer action:

- Treat each repeated family as a collision family.
- Rewrite the family into a structured bank, not a single replacement.
- Every full-content duplicate fingerprint must be reduced to one canonical atom or expanded into variants with distinct lexical signatures.

### 2.5 Off-Topic Doctrine Leakage

Files: `registry/anxiety.yaml`, `registry/somatic_healing.yaml`, `registry/imposter_syndrome.yaml`, `registry/depression.yaml`, `registry/overthinking.yaml`, `registry/self_worth.yaml`, `registry/financial_anxiety.yaml`, `registry/boundaries.yaml`, `registry/courage.yaml`

Confirmed issue examples:

- `Buddha's dialogue with Emperor Wu...`
- `Buddhist enlightenment is a journey...`
- `Dharmakaya`
- `enlightenment.Seeking Higher States...`
- generic Buddhist cosmology material appearing in books that did not request Buddhist teaching.

Writer action:

- Quarantine these atoms unless the book plan explicitly allows a Buddhist, dharma, contemplative, or comparative-religion frame.
- When a spiritual frame is allowed, rewrite the content so it serves the book's topic and persona rather than hijacking the chapter.
- Default self-help, anxiety, depression, financial anxiety, workplace, and Gen Z professional books must block these fragments.

## 3. Fragment Families Requiring Variant Banks

Each family below must be delivered as a structured bank. The writer must produce at least 10 publishable variants for each bank unless the bank is marked global, in which case the minimum is 20.

### 3.1 Global Scene Anchor Bank

Use when the renderer needs neutral sensory grounding.

Minimum: 20 variants.

Rules:

- Must fit any topic without changing the emotional meaning of the paragraph.
- Must not imply a specific city, weather event, season, class status, commute mode, or spiritual frame.
- Must not reuse the same noun image more than twice across the bank.
- Must avoid signature phrases longer than three words.

Example acceptable directions:

1. A room detail that is neutral and short.
2. A low-stakes sound in the environment.
3. A change in posture.
4. A screen, notebook, cup, bag, floor, window, desk, or hallway detail.
5. A breath or body detail that does not become therapeutic instruction.

### 3.2 Topic-Scene Recognition Bank

Use for opening scenes that let the reader feel recognized.

Minimum: 10 variants per topic-persona pair.

Rules:

- Must be specific to the topic and persona.
- Must not use fixed time stamps such as `forty minutes`.
- Must not pathologize the reader.
- Must not repeat the same setting across more than two variants.

Required for current priority:

- `anxiety + gen_z_professionals`
- `depression + gen_z_professionals`
- `imposter_syndrome + gen_z_professionals`
- `somatic_healing + gen_z_professionals`

### 3.3 Mechanism Bridge Bank

Use when moving from scene to explanation.

Minimum: 10 variants per mechanism family.

Rules:

- Must explain cause and effect without overclaiming.
- Must avoid miracle language, stealth transformation language, and one-size-fits-all neuroscience.
- Must vary sentence structure, paragraph length, and the order of observation, mechanism, and implication.

### 3.4 Flow Glue Bank

Use between atom slots and chapter sections.

Minimum: 20 global variants.

Rules:

- Must be short.
- Must not announce structure with phrases like `What this means is simple` in every chapter.
- Must not be reusable as a full paragraph across chapters.
- Must have a collision family tag so the renderer can avoid using adjacent variants with the same cadence.

### 3.5 Reflection Prompt Bank

Use in REFLECTION slots.

Minimum: 10 variants per topic-persona pair and book band.

Rules:

- Must ask only one thing at a time.
- Must not use moralizing language.
- Must not assume the reader is safe, resourced, partnered, employed, housed, or spiritually oriented.
- Must include depth bands:
  - Band 1: notice
  - Band 2: name
  - Band 3: connect
  - Band 4: choose

### 3.6 Practice and Integration Bank

Use in PRACTICE, INTEGRATION, and callback-completion slots.

Minimum: 10 variants per topic-persona pair.

Rules:

- Must be doable in under five minutes unless the plan requests a longer practice.
- Must include a no-equipment version.
- Must not prescribe breathwork, meditation, journaling, or body scanning as the only route.
- Must support accessibility: seated, standing, quiet, public, private, screen-based, and no-screen options.

### 3.7 Chapter Takeaway Bank

Use when source content is too thin or a chapter needs a closing synthesis.

Minimum: 10 variants per runtime template.

Rules:

- Must close the chapter without sounding like a summary slide.
- Must not repeat the thesis verbatim.
- Must not promise permanent transformation.
- Must prepare the next chapter when applicable.

### 3.8 Spiritual or Philosophical Teaching Bank

Use only when the plan explicitly allows that frame.

Minimum: 10 variants per teaching lineage or frame.

Rules:

- Must be tagged with exact allowed frames.
- Must include `topic_blocklist` for topics where the frame would feel intrusive.
- Must translate the teaching into the book's topic and persona.
- Must avoid dropping named traditions into secular books unless explicitly requested.

### 3.9 Content Gap Repair Bank

Use to fill missing slot types discovered by enrichment.

Minimum: 10 variants per missing slot family.

Current required repairs:

- REFLECTION for anxiety, Gen Z professionals, late-book chapters.

Rules:

- Must match the chapter's band, intensity, ONTGP move, and EI V2 target.
- Must be valid without knowing the previous paragraph.
- Must include metadata that lets the selector avoid repeating the same idea elsewhere.

## 4. Required Variant Record Format

Writers must deliver content as YAML-ready records. Each record must include these fields:

```yaml
variant_id: anxiety_genz_scene_recognition_001
slot_type: SCENE_RECOGNITION
body: "..."
topic_allowlist: ["anxiety"]
topic_blocklist: []
persona_allowlist: ["gen_z_professionals"]
frame_allowlist: ["secular", "nervous_system", "workplace"]
frame_blocklist: ["buddhist", "christian", "law_of_attraction", "manifestation"]
runtime_allowlist: ["quick_book_1h", "deep_book_6h"]
band: 1
intensity: 2
mechanism_depth: 2
ontgp_move: "name_pattern"
ei_v2_targets:
  specificity: 0.70
  embodiment: 0.55
  practical_transfer: 0.65
collision_family: "open_task_freeze"
signature_phrases:
  - "task is open"
forbidden_terms:
  - "enlightenment"
  - "Dharmakaya"
notes_for_selector: "Do not use within three chapters of another open-task-freeze scene."
```

## 5. Lexical Collision Rules

Every variant bank must pass these rules before it can enter the registry:

1. No exact sentence can appear in two variants.
2. No four-word phrase can appear in more than two variants in the same bank.
3. No five-word phrase can appear in more than one variant in the same bank.
4. No full paragraph may be reused across topics unless `reusable_scope: global_micro_glue` is set.
5. A global micro-glue record must be under 20 words.
6. A sensory image cannot appear in more than two variants in the same bank.
7. A setting cannot appear in more than three variants in the same bank unless the persona requires it.
8. A doctrine, spiritual figure, named tradition, or religious term must be blocked by default.
9. A practice instruction must vary the mode of action, not only the wording.
10. A reflection prompt must vary the cognitive operation, not only the question phrasing.

## 6. Content Correctness Rules

### 6.1 Off-Topic Content

Wrong content is any atom or fallback that introduces a frame the plan did not request. Examples:

- Buddhist doctrine in a secular anxiety book.
- Financial scarcity language in a grief book.
- Trauma recovery claims in a productivity book.
- Workplace scenes in a retired-persona book.
- Parent or partner assumptions in a single-adult persona book.

### 6.2 Overclaiming

Block variants that promise:

- permanent healing
- total safety
- identity-level rebirth
- instant calm
- medical cure
- spiritual awakening
- guaranteed professional success

### 6.3 Generic Therapeutic Mush

Block variants that rely on vague comfort without mechanism or specificity. Examples:

- `You are enough` as a standalone teaching.
- `Everything happens for a reason.`
- `Just breathe and let go.`
- `Your body knows the way` without context.

## 7. Required Writer Deliverables

For each duplicate or hard-coded fragment family, the writer must deliver:

1. A short problem label.
2. The original fragment or collision family.
3. The source location or registry family where it appears.
4. A replacement bank of at least 10 variants, or 20 for global fallbacks.
5. Metadata for each variant using the required record format.
6. A one-paragraph selector note explaining when the bank should and should not be used.
7. A list of signature phrases that must be blocked after the rewrite.

Priority deliverables:

1. `global_scene_anchor_bank`
2. `global_flow_glue_bank`
3. `anxiety_genz_scene_recognition_bank`
4. `anxiety_genz_reflection_late_book_bank`
5. `anxiety_genz_practice_integration_bank`
6. `mechanism_bridge_anxiety_nervous_system_bank`
7. `chapter_takeaway_deep_book_bank`
8. `spiritual_doctrine_quarantine_rewrite_bank`

## 8. Ten-Version Minimum Examples

These examples show the level of variety expected. They are not a complete final bank and must be metadata-wrapped before registry import.

### 8.1 Scene Anchor Directions

1. A notification fades before the reader reacts.
2. A hand rests on the edge of a desk.
3. The room stays ordinary around the charged moment.
4. A bag strap slips lower on one shoulder.
5. The cursor waits in a blank field.
6. A chair shifts against the floor.
7. A cup has gone cool nearby.
8. A hallway noise passes and disappears.
9. The reader notices they are bracing.
10. The screen brightness feels too sharp.

### 8.2 Anxiety Recognition Openers

1. The message is short, but your body reads it like a verdict.
2. You know the task is manageable, and still your hands hover above it.
3. Nothing has happened yet, but your calendar already feels loud.
4. You reread the same line and cannot tell whether you missed something.
5. The meeting starts in ten minutes, and your mind is already defending you.
6. You open the app to check one thing and leave with a tighter chest.
7. The decision is small, but your body treats it like a fork in your life.
8. You answer calmly and then replay every word afterward.
9. A normal delay starts to feel like information.
10. You are not confused about what to do. You are overloaded by what it might mean.

### 8.3 Flow Glue Variants

1. This is the pattern underneath the moment.
2. That reaction has a sequence.
3. The important part is the order.
4. Here is where the loop starts to show.
5. The body is not arguing. It is predicting.
6. The next move is smaller than the fear says.
7. This is easier to work with when it is named.
8. The signal makes more sense in context.
9. Once you see the sequence, it becomes less mysterious.
10. The shift begins before the feeling disappears.

### 8.4 Mechanism Bridge Variants

1. Anxiety often turns uncertainty into urgency before you have enough information.
2. The nervous system can treat possibility as proximity.
3. Prediction is useful until it starts impersonating proof.
4. A threat response does not wait for a final answer.
5. Your mind may be trying to lower risk by rehearsing every version.
6. The alarm is not a character flaw. It is a fast interpretation.
7. When stakes feel social, the body can respond before logic catches up.
8. Avoidance works briefly because it removes the signal, not because it solves the pattern.
9. Reassurance can calm one loop while training the next one to ask louder.
10. The goal is not to win an argument with the alarm. The goal is to change what happens next.

### 8.5 Reflection Prompt Variants

1. Name the moment when your body first decided this was urgent.
2. Notice what your mind is trying to prevent.
3. Separate the fact in front of you from the prediction attached to it.
4. Find the smallest action that would still count as participation.
5. Ask what support would make this one step less lonely.
6. Identify the part of the situation that is real and the part that is rehearsal.
7. Choose one signal you can respect without obeying.
8. Write the sentence your alarm is trying to finish.
9. Mark the difference between discomfort and danger.
10. Find one place where waiting for certainty has become the task.

### 8.6 Practice and Integration Variants

1. Before replying, place one sentence in a draft and wait one minute.
2. Turn the next task into a visible first step that takes less than two minutes.
3. Move one decision from your head into a note with two columns: known and guessed.
4. Let one message stay unread until you choose the time to answer it.
5. Say the feared outcome in plain words, then name the evidence you actually have.
6. Choose one object near you and use it as a cue to unclench your jaw.
7. Send the smaller honest response instead of the perfect delayed one.
8. Set a timer for three minutes and do only the opening motion of the task.
9. Ask one clarifying question instead of filling the silence with prediction.
10. Close the loop on one tiny obligation before checking for new ones.

### 8.7 Chapter Takeaway Variants

1. The work is not to erase the signal. It is to stop letting the signal choose the whole day.
2. A calmer life begins with a more accurate next step.
3. You do not need certainty before you can act with care.
4. The pattern loses force when it has to become specific.
5. Anxiety gets louder in vagueness. It softens when the next move is clear.
6. The body can learn from repetition that does not abandon it.
7. The point is not bravery as a mood. The point is participation with support.
8. You can respect the alarm and still decline its timeline.
9. The smallest honest action is often where trust starts again.
10. This chapter is not asking you to feel ready. It is asking you to become reachable.

### 8.8 Spiritual Doctrine Replacement Directions

1. Replace named doctrine with the chapter's secular mechanism.
2. Translate impermanence into uncertainty tolerance only if the plan allows that bridge.
3. Remove named teachers unless the teacher profile requests them.
4. Replace cosmic claims with grounded reader action.
5. Replace enlightenment language with learning, practice, or repair.
6. Replace universal metaphysics with topic-specific observation.
7. Keep humility without importing a lineage.
8. Keep awe only when the book's emotional arc calls for it.
9. Use contemplative language only with explicit frame allowance.
10. Prefer concrete lived examples over doctrinal exposition.

## 9. Acceptance Gates

A writer delivery is complete only when all gates pass:

1. Duplicate gate: no full-content duplicate appears more than once in the target topic-persona registry.
2. Phrase gate: no four-word phrase from a global fallback appears more than twice in a chapter.
3. Book-level anchor gate: no scene anchor family appears in more than two chapters of the same book.
4. Doctrine gate: blocked spiritual and philosophical terms do not appear unless explicitly allowed by the plan.
5. Slot coverage gate: every required slot type has at least 10 valid candidates for the plan.
6. Topic fit gate: every atom has topic allowlist or topic blocklist metadata.
7. Persona fit gate: every atom has persona allowlist or persona blocklist metadata.
8. EI V2 fit gate: every atom maps to the EI V2 dimension it is meant to serve.
9. ONTGP fit gate: every atom declares its ONTGP move.
10. Runtime fit gate: quick-book atoms and deep-book atoms are not blindly interchangeable.

## 10. Writer Prompt

Use this prompt when assigning the rewrite:

```text
You are writing Phoenix Omega content variant banks, not a finished chapter.

Your task is to replace duplicated, hard-coded, or off-topic fragment families with structured variants that can scale across thousands of generated books.

For each fragment family:
1. Identify the collision family and the original phrase pattern.
2. Produce at least 10 variants. Produce at least 20 variants for global fallback families.
3. Make each variant meaningfully different in scene, syntax, action, and emotional function.
4. Attach metadata for topic, persona, frame, runtime, band, intensity, mechanism depth, ONTGP move, EI V2 targets, collision family, signature phrases, and forbidden terms.
5. Block spiritual, doctrinal, medical, miracle, and identity-transformation language unless the plan explicitly allows it.
6. Ensure no exact sentence repeats across variants and no four-word phrase appears more than twice in the same bank.
7. Do not write content that only sounds good in one paragraph. Each variant must survive being selected in any valid chapter slot for its metadata.

Return YAML-ready records plus a short selector note for each bank.
```

## 11. Implementation Handoff Notes

After the writer delivers the banks, engineering should:

1. Move global fallback prose out of renderer constants and into plan-addressable content banks.
2. Add collision-family tracking during selection and rendering.
3. Treat visible `[CONTENT GAP: ...]` markers as hard failures in publishable runs.
4. Add a registry audit that reports duplicate fingerprints by topic, persona, slot, and collision family.
5. Enforce doctrine/topic allowlists before slot fill, not after composition.
6. Record selected `variant_id` values in render artifacts for post-run auditing.

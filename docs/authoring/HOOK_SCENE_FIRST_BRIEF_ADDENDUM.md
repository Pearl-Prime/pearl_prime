# HOOK Scene-First Brief Addendum

**Authority:** `HOOK-SCENE-FIRST-01` (`docs/PEARL_ARCHITECT_STATE.md`) · **OPD-144** (`artifacts/coordination/operator_decisions_log.tsv`)  
**Workstream:** `ws_pearl_editor_hook_scene_first_brief_addendum_20260523`  
**Status:** ratified authoring rule (binding for new atoms; existing corpus tagged, not rewritten in this ws)

---

## 1. Rule (binding)

The **first paragraph** of every `HOOK` and `ANGLE_DEFINITION` atom must be **scene-first**:

| Required element | What it means | Failure mode |
|---|---|---|
| **(1) Specific person** | A concrete human subject the reader can picture — named character, second-person *you* in a lived moment, or definite *she/he/they* in a specific role | Abstract *people*, universal *the listener*, or no human subject |
| **(2) Specific situation** | A place, time, or event anchor — not a topic label | Pure mood ("nightfall," "the interior speaks") with no setting |
| **(3) Specific body posture** | Observable somatic state or physical action — breath, grip, slumped shoulders, phone against thigh, lowered voice, night sweat, jaw clench | Emotion labels without embodiment ("anxious," "overwhelmed") |

**Philosophy and abstraction may appear only AFTER the scene** in the same atom (second paragraph onward). Never lead with thesis, metaphor-of-the-universe, or aphorism chains before the reader has a body in a room.

**Scope:**

| Atom type | Path |
|---|---|
| `HOOK` | `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` (classify **v01** first paragraph) |
| `ANGLE_DEFINITION` | `atoms/<persona>/<topic>/ANGLE_DEFINITION/**/CANONICAL.txt` |

---

## 2. Verbatim exemplars (operator AUTHORED references)

### PASS — Miki, scene-first (`artifacts/pipeline_examples/miki/book_miki_imposter_syndrome_15min.txt:26`)

> Somewhere right now, a person is sitting in a bathroom stall at their new job, pressing their phone against their thigh so nobody hears the screen light up, breathing through their mouth because their nose is too congested from the silent crying they did in the car on the way here.

- **Person:** a person at their new job  
- **Situation:** bathroom stall, phone secrecy  
- **Posture:** sitting, pressing phone against thigh, breathing through mouth  

Reader recognition in sentence 1.

### FAIL — Omote, philosophy-first (`artifacts/pipeline_examples/omote/book_omote_sleep_anxiety_15min.txt:27`)

> Nightfall strips the surface away. This happens automatically, without consent and without ceremony. The lights go off. The room darkens. The sounds of the day recede — traffic, conversation, the hum of machines and obligations and schedules and the low buzz of perpetual performance. And in the sudden quiet, the interior speaks.

- **Person:** none in paragraph 1  
- **Situation:** abstract nightfall, not a specific room or night  
- **Posture:** none  

Concrete recognition deferred until paragraph 4 ("The email that went unanswered…"). Operator: *"The Omote book ch1 is not as good as the Miki book."*

### Corpus sample (5 HOOK atoms, pre-tagging discovery)

| Path | v01 opening (truncated) | Expected class |
|---|---|---|
| `atoms/midlife_women/anxiety/HOOK/CANONICAL.txt` | Diane woke at 3:14am with her heart already ahead of her… | SCENE_FIRST |
| `atoms/entrepreneurs/anxiety/HOOK/CANONICAL.txt` | Your chest tightens when the client goes silent… | SCENE_FIRST |
| `atoms/midlife_women/imposter_syndrome/HOOK/CANONICAL.txt` | She… lowers her voice slightly when she speaks in the Monday meeting… | SCENE_FIRST |
| `atoms/midlife_women/sleep_anxiety/HOOK/CANONICAL.txt` | She wakes at 3:17am and the night sweats have already passed… | SCENE_FIRST |
| `atoms/entrepreneurs/overthinking/HOOK/CANONICAL.txt` | Your worth is your business. Your business is your worth… | PHILOSOPHY_FIRST |

---

## 3. Mini-templates (common HOOK shapes)

Use these as **first-paragraph scaffolds** only — vary persona, topic mechanism, and diction. Philosophy comes in paragraph 2+.

### A. At work (meeting / screen / shift)

> **[Person]** is **[posture]** in **[specific workplace moment]** — **[one concrete detail that carries the topic mechanism]**.

*Example axis:* `entrepreneurs × anxiety` — chest tightens when the client goes silent; invoice unopened.

### B. At home (night / kitchen / bed)

> **[Person]** **[wakes / lies / stands]** at **[clock time]** in **[room]** — **[body state]** before **[the thought loop that names the topic]**.

*Example axis:* `midlife_women × sleep_anxiety` — 3:17am wake, night sweats passed, thoughts arriving with precision.

### C. Mid-action (stall / car / hallway / before send)

> Somewhere right now, **[person]** is **[verb-ing]** in **[tight physical setting]**, **[posture + sensory detail]**, because **[situation stakes]**.

*Example axis:* Miki imposter reference — bathroom stall, phone against thigh, breathing through mouth.

---

## 4. Wrapper-line guidance (`TEACHER-MODE-WRAPPER-SEMANTICS-01`)

When teacher voice augments a HOOK:

- **≤1 line** of teacher framing at the **opening** of the HOOK slot only.  
- Wrapper is **cadence/register**, not substance — it must not replace or precede the scene-first paragraph.  
- Substance body (person + situation + posture) still comes from `atoms/<persona>/<topic>/HOOK/*` → `registry/<topic>.yaml`.  
- Teacher HOOK atoms are **fallback only** when persona + registry pools are empty.

**Anti-pattern:** Opening with teacher doctrine ("Every person carries the capacity for awakening…") before the persona scene — this is the audit §6 smoking gun; scene-first rule forbids it regardless of wrapper budget.

---

## 5. Classification labels (corpus tagging)

| Label | Meaning | Rewrite queue |
|---|---|---|
| `SCENE_FIRST` | All three elements present in v01 paragraph 1 | None (P2 = no rewrite) |
| `MIXED` | Two of three elements, or embodied scene with residual abstract lead | Yes — priority by persona×topic prominence |
| `PHILOSOPHY_FIRST` | Aphorism / abstract lead; embodied scene absent or deferred | Yes — highest priority when persona×topic is flagship |

**Rewrite priority (non–scene-first only):**

- **P0** — Move 4 bestseller sweep persona×topic OR flagship persona (`entrepreneurs`, `gen_z_professionals`, `millennial_women_professionals`, `midlife_women`) × flagship topic (`anxiety`, `burnout`, `imposter_syndrome`, `sleep_anxiety`, `overthinking`, `social_anxiety`, `boundaries`)  
- **P1** — All other production persona×topic tuples with `MIXED` or `PHILOSOPHY_FIRST`  
- **P2** — `SCENE_FIRST` (no rewrite) or low-prominence personas (`educators`, `nyc_executives`, `gen_alpha_students`) with violations  

Full corpus artifact: `artifacts/qa/HOOK_SCENE_FIRST_TAGGING_<YYYYMMDD>.tsv` (columns: `atom_path`, `classification`, `first_paragraph_excerpt`, `rewrite_priority`).

**This ws tags only.** Atom rewrites are a downstream Pearl_Editor workstream gated on this addendum + tagging artifact landing on `main`.

---

## 6. Cross-references

- `docs/PEARL_ARCHITECT_STATE.md` — **HOOK-SCENE-FIRST-01**  
- `docs/PEARL_ARCHITECT_STATE.md` — **TEACHER-MODE-WRAPPER-SEMANTICS-01** (HOOK ≤1 wrapper line)  
- `artifacts/coordination/operator_decisions_log.tsv` — **OPD-144**  
- `ws_pearl_dev_register_gate_f11_hook_abstract_detector_20260523` — register-gate WARN detector (Pearl_Dev; soft dep on this tagging pass)

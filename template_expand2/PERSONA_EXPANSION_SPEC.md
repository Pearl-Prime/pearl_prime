# PERSONA EXPANSION SPEC — PHASE 2
## Phoenix Omega V4

---

## CURRENT STATE

| Metric | Count |
|--------|-------|
| Personas complete | 3 |
| Topics per persona | 8 |
| Atoms per persona | 520 |
| **Total atoms** | **1,560** |

### Completed Personas

| Persona | Atoms | Status |
|---------|-------|--------|
| gen_alpha_students | 520 | ✅ DONE |
| healthcare_rns | 520 | ✅ DONE |
| gen_z_professionals | 520 | ✅ DONE |

---

## TARGET STATE

| Metric | Count |
|--------|-------|
| Personas complete | 8 |
| Topics per persona | 8 |
| Atoms per persona | 520 |
| **Total atoms** | **4,160** |

---

## NEW PERSONAS (5)

| Phase | Persona ID | Label | Atoms |
|-------|------------|-------|-------|
| 1 | parents_teens | Parents of Teenagers | 520 |
| 2 | educators | Teachers/Educators | 520 |
| 3 | college_earlycareer | College & Early Career | 520 |
| 4 | remote_tech | Remote Tech Workers | 520 |
| 5 | sf_founders | SF Founders/Startup | 520 |

**Total new atoms: 2,600**

---

## GLOBAL RULE

> **Engines are locked. Topics are locked. Only surface nouns change.**

If you're inventing new psychology, stop. You're doing it wrong.

---

## TOPIC × ENGINE MATRIX (UNCHANGED)

Every persona gets the same topic → engine routing:

| Topic | Engines | Atoms |
|-------|---------|-------|
| anxiety | false_alarm, spiral, watcher, overwhelm, shame, comparison, grief | 140 |
| boundaries | shame, comparison, false_alarm | 60 |
| financial_stress | overwhelm, spiral, shame | 60 |
| courage | false_alarm, shame, spiral | 60 |
| compassion_fatigue | overwhelm, watcher, grief | 60 |
| depression | watcher, grief, overwhelm | 60 |
| self-worth | shame, comparison | 40 |
| grief (topic) | grief, watcher | 40 |
| **Total per persona** | — | **520** |

---

## PERSONA SPECIFICATIONS

### PHASE 1: parents_teens

**ID:** `parents_teens`
**Label:** Parents of Teenagers
**Atoms:** 520

**Who they are:**
- Parents with kids ages 13-19
- Juggling work, home, relationship with teen
- Watching child become independent
- Often feeling out of control, second-guessing

**Surface nouns (allowed):**
- Teen's room, school calls, college prep
- Silent dinners, slammed doors
- Text conversations that end abruptly
- Parent-teacher conferences
- Driving lessons, curfew negotiations
- Empty nest approaching
- Spouse/partner co-parenting friction

**Forbidden content:**
- ❌ Parenting advice
- ❌ "They'll thank you later"
- ❌ Discipline strategies
- ❌ Teen psychology explanations
- ❌ "It's just a phase"
- ❌ Comparison to other parents
- ❌ Success/failure framing of parenting

**Portable from:** gen_z_professionals (adult concerns, work-life overlap)

---

### PHASE 2: educators

**ID:** `educators`
**Label:** Teachers/Educators
**Atoms:** 520

**Who they are:**
- K-12 teachers, college instructors
- Managing classrooms + admin + parents
- Carrying students' struggles home
- Under-resourced, over-expected

**Surface nouns (allowed):**
- Classroom, lesson plans, grading
- Staff meetings, parent emails
- Student who's struggling
- Standardized tests, evaluations
- Summer break anticipation
- Supplies bought with own money
- The one student you can't reach

**Forbidden content:**
- ❌ Hero framing ("they do it for the kids")
- ❌ Sacrifice language
- ❌ System critique / education policy
- ❌ "Teachers are underpaid" discourse
- ❌ Burnout as identity
- ❌ Martyrdom narratives

**Portable from:** healthcare_rns (caregiving, emotional labor, institutional pressure)

---

### PHASE 3: college_earlycareer

**ID:** `college_earlycareer`
**Label:** College & Early Career
**Atoms:** 520

**Who they are:**
- Ages 18-24
- College students or first 1-3 years of work
- Between dependence and independence
- First real failures, first real stakes

**Surface nouns (allowed):**
- Dorm, roommate, dining hall
- First apartment, first lease
- Entry-level job, internship
- Student loans, part-time work
- Parents who still help (or don't)
- Relationships getting serious
- Career uncertainty, major changes

**Forbidden content:**
- ❌ "Best years of your life"
- ❌ "Finding yourself"
- ❌ Coming-of-age narrative
- ❌ Advice about majors/careers
- ❌ Comparison to peers' paths
- ❌ Success/failure framing

**Portable from:** gen_alpha_students (school context) + gen_z_professionals (work context)

---

### PHASE 4: remote_tech

**ID:** `remote_tech`
**Label:** Remote Tech Workers
**Atoms:** 520

**Who they are:**
- Software engineers, PMs, designers
- Fully remote or hybrid
- Slack/Zoom as primary connection
- Blurred home/work boundaries

**Surface nouns (allowed):**
- Home office, standing desk, second monitor
- Slack channels, async communication
- Video calls, camera on/off
- Time zones, "quick sync"
- Deliverables, sprints, deadlines
- Loneliness of remote work
- Roommates/family during work hours

**Forbidden content:**
- ❌ "Remote work is the future" discourse
- ❌ Productivity optimization
- ❌ Work-life balance advice
- ❌ Tech company culture critique
- ❌ Hustle praise or anti-hustle
- ❌ "Digital nomad" romanticism

**Portable from:** gen_z_professionals (work patterns, same engines)

---

### PHASE 5: sf_founders

**ID:** `sf_founders`
**Label:** SF Founders/Startup
**Atoms:** 520

**Who they are:**
- Startup founders, early employees
- High stakes, high uncertainty
- Investor pressure, runway anxiety
- Identity tied to company success

**Surface nouns (allowed):**
- Pitch decks, investor meetings
- Runway, burn rate, fundraising
- Co-founder relationships
- Hiring, firing, pivoting
- Product launches, user metrics
- Sleepless nights before deadlines
- The idea that might fail

**Forbidden content:**
- ❌ Hustle culture praise
- ❌ "Grind now, rest later"
- ❌ Success stories as motivation
- ❌ VC/investor advice
- ❌ "Move fast and break things"
- ❌ Founder as hero narrative

**Portable from:** gen_z_professionals (work pressure) + remote_tech (tech context)

---

## PRODUCTION ORDER

Write personas in this order to maximize reuse:

### Phase 1: parents_teens (520 atoms)

| Topic | Engines | Batches | Atoms |
|-------|---------|---------|-------|
| anxiety | 7 | 7 | 140 |
| boundaries | 3 | 3 | 60 |
| financial_stress | 3 | 3 | 60 |
| courage | 3 | 3 | 60 |
| compassion_fatigue | 3 | 3 | 60 |
| depression | 3 | 3 | 60 |
| self-worth | 2 | 2 | 40 |
| grief (topic) | 2 | 2 | 40 |
| **Subtotal** | — | **26** | **520** |

### Phase 2: educators (520 atoms)

Same structure as above. 26 batches, 520 atoms.

### Phase 3: college_earlycareer (520 atoms)

Same structure. 26 batches, 520 atoms.

### Phase 4: remote_tech (520 atoms)

Same structure. 26 batches, 520 atoms.

### Phase 5: sf_founders (520 atoms)

Same structure. 26 batches, 520 atoms.

---

## TOTALS

| Metric | Count |
|--------|-------|
| New personas | 5 |
| Batches per persona | 26 |
| **Total new batches** | **130** |
| Atoms per persona | 520 |
| **Total new atoms** | **2,600** |

---

## STRIP TEST (MANDATORY)

For each persona, validate portability:

1. Take 5 atoms from the new persona
2. Remove all persona-specific nouns
3. Replace with generic task nouns
4. If engine weakens → atom is wrong

**Engines must survive persona transfer without mutation.**

---

## FILE NAMING CONVENTION

```
{persona}__{topic}__{engine}__CANONICAL.txt
```

Examples:
```
parents_teens__anxiety__false_alarm__CANONICAL.txt
educators__boundaries__shame__CANONICAL.txt
college_earlycareer__courage__spiral__CANONICAL.txt
remote_tech__depression__watcher__CANONICAL.txt
sf_founders__grief_topic__grief__CANONICAL.txt
```

---

## DELIVERY FORMAT (PER BATCH)

- 20 atoms
- 5/5/5/5 role distribution
- 2-3 sentence drift note

No reflections. No justifications.

---

## STOP CONDITIONS

Stop immediately if:
- Atoms feel like parenting/teaching/career advice
- Tone becomes aspirational or motivational
- You want to "help" the character
- Surface becomes the psychology (e.g., "parenting is hard")

That's drift. Rewrite.

---

## ESTIMATED TIME

| Metric | Value |
|--------|-------|
| Batches | 130 |
| Time per batch | ~10 min |
| **Total time** | ~22 hours |

---

## COMPLETION CHECKPOINT

When all 5 personas are done:

| Persona | Atoms | Status |
|---------|-------|--------|
| gen_alpha_students | 520 | ✅ |
| healthcare_rns | 520 | ✅ |
| gen_z_professionals | 520 | ✅ |
| parents_teens | 520 | ⏳ |
| educators | 520 | ⏳ |
| college_earlycareer | 520 | ⏳ |
| remote_tech | 520 | ⏳ |
| sf_founders | 520 | ⏳ |
| **TOTAL** | **4,160** | — |

---

## START COMMAND

When ready, say:

> "Write parents_teens × anxiety × false_alarm (20 atoms)"

System produces batch. Repeat 130 times. Done.

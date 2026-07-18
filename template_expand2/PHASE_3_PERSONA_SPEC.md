# PERSONA EXPANSION SPEC — PHASE 3
## Phoenix Omega V4

---

## CURRENT STATE (PHASE 2 COMPLETE)

| Persona | Atoms | Status |
|---------|-------|--------|
| gen_alpha_students | 520 | ✅ |
| healthcare_rns | 520 | ✅ |
| gen_z_professionals | 520 | ✅ |
| remote_tech | 520 | ✅ |
| educators | 520 | ✅ |
| parents_teens | 520 | ✅ |
| sf_founders | 520 | ✅ |
| college_earlycareer | 520 | ✅ |
| **TOTAL** | **4,160** | ✅ |

---

## TARGET STATE (PHASE 3)

| Metric | Count |
|--------|-------|
| Personas complete | 12 |
| Topics per persona | 8 |
| Atoms per persona | 520 |
| **Total atoms** | **6,240** |

---

## NEW PERSONAS (4)

| Phase | Persona ID | Label | Atoms |
|-------|------------|-------|-------|
| 3.1 | nyc_executives | NYC Executives | 520 |
| 3.2 | creatives_freelancers | Creatives/Freelancers | 520 |
| 3.3 | midlife_women | Midlife Women | 520 |
| 3.4 | smb_owners | Small Business Owners | 520 |

**Total new atoms: 2,080**

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

### PHASE 3.1: nyc_executives

**ID:** `nyc_executives`
**Label:** NYC Executives
**Atoms:** 520

**Who they are:**
- Finance, law, consulting professionals
- Mid-to-senior career, high pressure
- Performance-driven environments
- Manhattan/Brooklyn commute culture

**Surface nouns (allowed):**
- Corner office, conference room, client calls
- Quarterly earnings, deal closings, billable hours
- Partner track, managing director, equity stake
- Black car service, late nights, working dinners
- Dry cleaning, doorman building, weekend emails
- The associate who's struggling
- Bonus season, year-end reviews

**Forbidden content:**
- ❌ "Wall Street greed" framing
- ❌ Luxury as compensation for suffering
- ❌ "Golden handcuffs" discourse
- ❌ Work-life balance advice
- ❌ Success = happiness messaging
- ❌ Class critique or privilege acknowledgment

**Portable from:** sf_founders (high stakes), gen_z_professionals (work patterns)

---

### PHASE 3.2: creatives_freelancers

**ID:** `creatives_freelancers`
**Label:** Creatives/Freelancers
**Atoms:** 520

**Who they are:**
- Designers, writers, artists, photographers
- Gig-based or self-employed
- Irregular income, project-to-project
- Identity tied to creative output

**Surface nouns (allowed):**
- Portfolio, client briefs, revision rounds
- Invoice, late payment, scope creep
- Coffee shop office, coworking day pass
- Creative block, blank page, the piece that won't come
- The client who ghosts, the project that fell through
- Side hustle, passion project, "real job" pressure
- Instagram grid, follower count, the algorithm

**Forbidden content:**
- ❌ "Starving artist" romanticism
- ❌ Hustle culture praise
- ❌ "Do what you love" messaging
- ❌ Creativity as therapy framing
- ❌ Success stories as motivation
- ❌ Platform critique (Instagram, etc.)

**Portable from:** remote_tech (isolation, gig patterns), sf_founders (identity tied to work)

---

### PHASE 3.3: midlife_women

**ID:** `midlife_women`
**Label:** Midlife Women
**Atoms:** 520

**Who they are:**
- Women ages 40-60
- Juggling multiple roles (career, caregiving, self)
- Body changes, identity shifts
- Invisible labor, sandwich generation

**Surface nouns (allowed):**
- Aging parents, adult children, empty nest approaching
- Perimenopause, sleep changes, body that's different
- Career plateau, passed over, starting over
- Marriage maintenance, divorce recovery, dating again
- The friend group that scattered, the friendships that faded
- Reflection on choices made, paths not taken
- The face in the mirror, the energy that's different

**Forbidden content:**
- ❌ "Midlife crisis" framing
- ❌ Anti-aging messaging
- ❌ "Best years ahead" positivity
- ❌ Hormone/supplement advice
- ❌ Reinvention narratives
- ❌ Comparison to younger self as failure

**Portable from:** parents_teens (caregiving), healthcare_rns (invisible labor)

---

### PHASE 3.4: smb_owners

**ID:** `smb_owners`
**Label:** Small Business Owners
**Atoms:** 520

**Who they are:**
- Own/operate small businesses (retail, service, local)
- 1-50 employees, often family involved
- Cash flow pressure, wearing all hats
- Community-embedded, reputation-dependent

**Surface nouns (allowed):**
- Payroll Friday, the register, inventory counts
- Lease renewal, landlord, the loan payment
- Employee who called out, the one who quit
- Yelp review, Google rating, word of mouth
- Slow season, holiday rush, weather affecting traffic
- The books, the accountant, quarterly taxes
- Closed sign, open sign, the hours that never end

**Forbidden content:**
- ❌ Entrepreneurship romanticism
- ❌ "Be your own boss" messaging
- ❌ Growth/scale advice
- ❌ Franchise vs. independent discourse
- ❌ Success stories as motivation
- ❌ "Small business is the backbone" framing

**Portable from:** sf_founders (ownership pressure), parents_teens (always-on caregiving)

---

## PRODUCTION ORDER

Write personas in this order to maximize reuse:

### Phase 3.1: nyc_executives (520 atoms)

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

### Phase 3.2: creatives_freelancers (520 atoms)

Same structure. 26 batches, 520 atoms.

### Phase 3.3: midlife_women (520 atoms)

Same structure. 26 batches, 520 atoms.

### Phase 3.4: smb_owners (520 atoms)

Same structure. 26 batches, 520 atoms.

---

## TOTALS

| Metric | Count |
|--------|-------|
| New personas | 4 |
| Batches per persona | 26 |
| **Total new batches** | **104** |
| Atoms per persona | 520 |
| **Total new atoms** | **2,080** |

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
nyc_executives__anxiety__false_alarm__CANONICAL.txt
creatives_freelancers__boundaries__shame__CANONICAL.txt
midlife_women__courage__spiral__CANONICAL.txt
smb_owners__grief_topic__grief__CANONICAL.txt
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
- Atoms become lifestyle commentary
- Tone becomes sympathetic to "their situation"
- Surface starts explaining the persona's challenges
- You want to acknowledge how hard they have it

That's drift. Rewrite.

---

## ESTIMATED TIME

| Metric | Value |
|--------|-------|
| Batches | 104 |
| Time per batch | ~10 min |
| **Total time** | ~17 hours |

---

## COMPLETION CHECKPOINT

When all 4 personas are done:

| Persona | Atoms | Status |
|---------|-------|--------|
| gen_alpha_students | 520 | ✅ |
| healthcare_rns | 520 | ✅ |
| gen_z_professionals | 520 | ✅ |
| remote_tech | 520 | ✅ |
| educators | 520 | ✅ |
| parents_teens | 520 | ✅ |
| sf_founders | 520 | ✅ |
| college_earlycareer | 520 | ✅ |
| nyc_executives | 520 | ⏳ |
| creatives_freelancers | 520 | ⏳ |
| midlife_women | 520 | ⏳ |
| smb_owners | 520 | ⏳ |
| **TOTAL** | **6,240** | — |

---

## START COMMAND

When ready, say:

> "Write nyc_executives × anxiety × false_alarm (20 atoms)"

System produces batch. Repeat 104 times. Done.

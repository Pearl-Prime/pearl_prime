# Pearl Prime Exercise Dual-System V1

**Status:** Canonical behavior; 12-chapter analyzer/planner is SPECCED, not yet implemented.

| System | What it is | Rule |
|---|---|---|
| A. 311 five-layer practice | Guided practice from canonical practice/teacher EXERCISE banks | Always supplies the exercise body |
| B. Journey wrap | `--exercise-journeys` awareness→regulation framing around §§4/8 | Optional sequencing layer; never invents the body |
| C. 12-chapter book plan | Ordered practice IDs for persona×topic×locale, with justified engine override | Required for production cells |

## Plan contract

```yaml
schema_version: "1.0"
plan_id: gen_z_professionals__anxiety__en_US
persona: gen_z_professionals
topic: anxiety
locale: en_US
engine_override: null
chapters:
  - chapter: 1
    exercise_id: canonical_practice_id
    phase: awareness
    rationale: "Why this real practice belongs here"
```

- Exactly 12 ordered chapter entries for a 12-chapter format; other formats declare their own exact count.
- Every `exercise_id` must resolve to a real canonical 311/teacher practice.
- Analyzer reports missing IDs, duplicates, phase discontinuity, persona/topic mismatch, and unjustified engine overrides.
- Journey wrapping may still apply after plan resolution.
- The plan never replaces the practice body; the journey never replaces the plan.
- Flagship twelve-shape plans are the implementation precedent, not a second exercise SSOT.

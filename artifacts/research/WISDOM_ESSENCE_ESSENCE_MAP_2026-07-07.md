# Wisdom Essence — Essence Map (Research)

**Date:** 2026-07-07  
**Authority:** Pearl_Research  
**Status:** RESEARCHED → feeds `WISDOM_ESSENCE` accent class spec + pilot bank  
**Method:** Corpus convergence analysis across six teacher-mode teachers + EI v2 `domain_thesis_similarity` offline scoring

---

## STEP 0 — Grounding summary

### Teacher registry resolution (six named teachers)

| Operator name | Registry key | Resolves | Notes |
|---------------|--------------|----------|-------|
| Ahjan | `ahjan` | YES | 19 TEACHER_DOCTRINE atoms; full authoring-layer intake |
| Master Wu | `master_wu` | YES | 4 TEACHER_DOCTRINE; doctrine.yaml only |
| Master Feung | `master_feung` | YES | 4 TEACHER_DOCTRINE; doctrine.yaml only |
| Junko | `junko` | YES | 4 TEACHER_DOCTRINE; doctrine.yaml only |
| Sai Maa | `sai_ma` | YES | 12 TEACHER_DOCTRINE; **teacher-mode-only, never author-attributed** |
| Master Shah | `master_sha` | YES (spelling) | Operator said "Shah"; registry SSOT is **Master Sha** |

**None unresolved.**

### Tradition-attribution bank

**NOT FOUND** as dedicated bank. Wrapper templates in `config/catalog_planning/teacher_wrapper_templates.yaml`; 9 scattered `In the … tradition` atoms repo-wide.

### Mode-bleed gate (untouchable)

OPD-115 Phase B in `phoenix_v4/planning/enrichment_select.py`. WISDOM_ESSENCE enters composite books **only** via planner-placed `accent_beats`.

### EI v2 role

Offline scorer only (`domain_thesis_similarity`). Not a generator. Not planner-wired.

---

## STEP 1 — Essence Map

Corpus per teacher: TEACHER_DOCTRINE + REFLECTION + PERMISSION + COMPRESSION + doctrine.yaml.  
Scoring: persona `gen_z_professionals`, topic `anxiety`. All themes ≥3/6 teachers at EI v2 ≥0.35.

| Theme | Supporting | Key source refs | EI v2 avg |
|-------|------------|-----------------|-----------|
| body_first_awareness | 6/6 | ahjan_TD_000, junko_TD_001, sai_ma_TD_000 | 0.699 |
| noticing_without_fixing | 6/6 | ahjan_TD_001, sai_ma_TD_006 | 0.667 |
| bracing_cost | 6/6 | ahjan_TD_002, sai_ma_TD_006 | 0.699 |
| self_compassion_worth | 6/6 | sai_ma_TD_000, master_feung_TD_000 | 0.715 |
| impermanence_weather | 6/6 | sai_ma_TD_006, master_feung_TD_001 | 0.638 |
| observing_self | 6/6 | junko_TD_000, ahjan_TD_001 | 0.638 |
| already_complete | 6/6 | master_feung_TD_000 | 0.638 |
| suffering_as_pigment | 6/6 | master_feung_TD_001 | 0.638 |
| transmission_beyond_mind | 6/6 | junko_TD_001, master_sha_TD_000 | 0.640 |
| ordinary_life_practice | 6/6 | ahjan doctrine, master_feung_TD_000 | 0.652 |

### Excluded (non-convergent / non-secular)

Dragon Vein geomancy (master_wu-specific); light language mechanics (junko); Jagadguru lineage (sai_ma); Tao Calligraphy frequency field (master_sha).

### Placement recommendation

**Default:** `after_REFLECTION` coda. Alternate: `before_THREAD` grace note.

---

## Operator questions (recommendations)

| ID | Question | Recommendation |
|----|----------|----------------|
| Q-WISDOM-01 | Dosage default secular | Max 2/book; most 0–1 |
| Q-WISDOM-02 | Variant (c) in secular? | (b) only secular; (c) teacher-mode |
| Q-WISDOM-03 | Placement default | post-REFLECTION coda |

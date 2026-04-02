# Atom Debt Repair — Dev Spec (Post-S8 follow-up)

**Purpose:** After source/bank repair (S0–S8, closed 2026-03-30 via PR #88), two categories of content debt remain: (A) **240 thin atoms** that passed structural checks but fall below §8 word-count thresholds, and (B) **6 personas** whose SCENE banks are cloned from `gen_z_professionals` and need voice re-localization. This spec defines a scoped Pearl_Writer workstream to resolve both.

**Authority:** [docs/SOURCE_BANK_REPAIR_DEV_SPEC.md](./SOURCE_BANK_REPAIR_DEV_SPEC.md) §8 acceptance criteria; [artifacts/source_bank_repair/s8_editorial_audit.md](../artifacts/source_bank_repair/s8_editorial_audit.md) §Flagged for tech lead; [artifacts/source_bank_repair/CLOSEOUT_RECEIPT.md](../artifacts/source_bank_repair/CLOSEOUT_RECEIPT.md) known debt items 1–2.

**Status:** Dev spec — execution PRs follow the slice table in §5.

---

## 1. Scope and non-goals

### In scope

- **Thin atom expansion:** 240 atom files below §8 thresholds (143 COMPRESSION, 46 HOOK, 51 SCENE) across all personas except `gen_z_professionals` (already repaired in S1–S4/S8).
- **Persona voice re-localization:** 6 personas × 2 topics (burnout, financial_anxiety) SCENE banks currently cloned from `gen_z_professionals`. Rewrite to match each persona's voice, lived experience, and workplace context.

### Explicitly out of scope

- **gen_z_professionals atoms** — already repaired in S0–S8; no further edits unless new hollowness found.
- **Teacher banks** — slot-family complete after S6/S7; voice quality is a separate future lane.
- **Location profiles** — complete for MVP after S0/S5.
- **Runtime / planner / renderer code** — no code changes in this workstream.
- **New personas or topics** — no taxonomy expansion.
- **Pipeline heuristic fix** (`_KEYLIKE_METADATA_RE` H:MM) — Pearl_Dev scope, separate PR.

---

## 2. Debt inventory

### 2.1 Thin atoms by slot type (from S8 audit)

| Slot type | Files failing threshold | Threshold (from §8) |
|-----------|------------------------|---------------------|
| COMPRESSION | 143 | ≥3 distinct variants OR ≥12 lines substantive prose |
| HOOK | 46 | ≥12 words per variant |
| SCENE | 51 | ≥40 words per scene body, ≥2 sentences |
| **Total** | **240** | |

### 2.2 Persona distribution (estimated)

Based on the S8 audit pattern — `gen_z_professionals` is clean, debt is spread across the remaining personas:

| Persona | Expected thin atoms | Notes |
|---------|-------------------|-------|
| corporate_managers | ~20–30 | COMPRESSION + HOOK heavy |
| educators | ~15–25 | Full audit needed |
| entrepreneurs | ~15–25 | Full audit needed |
| first_responders | ~20–30 | COMPRESSION + HOOK + SCENE |
| gen_alpha_students | ~20–30 | COMPRESSION + SCENE |
| gen_x_sandwich | ~20–30 | COMPRESSION + HOOK + SCENE |
| healthcare_rns | ~20–30 | COMPRESSION + HOOK + SCENE |
| millennial_women_professionals | ~10–20 | Full audit needed |
| nyc_executives | ~10–20 | Full audit needed |
| tech_finance_burnout | ~10–20 | Full audit needed |
| working_parents | ~20–30 | COMPRESSION + HOOK + SCENE |

**Note:** Exact per-persona counts require a fresh scan. The S8 audit gives aggregate totals. Each PR slice should begin with a targeted scan of its persona set.

### 2.3 Persona voice re-localization (from S8 fixes)

| Persona | Topics affected | Current state |
|---------|----------------|---------------|
| working_parents | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |
| healthcare_rns | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |
| gen_x_sandwich | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |
| gen_alpha_students | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |
| first_responders | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |
| corporate_managers | burnout, financial_anxiety | SCENE cloned from gen_z_professionals |

**12 SCENE CANONICAL.txt files** need voice rewrite. Each has 30 scenes. The prose structure (second-person, location tokens, 56–73 words/scene) is sound — what needs changing is the framing leads and contextual details to match each persona's world.

---

## 3. Voice guidance per persona

When rewriting thin atoms or re-localizing SCENE text, match these voice profiles:

| Persona | Voice register | Workplace/life context | Avoid |
|---------|---------------|----------------------|-------|
| working_parents | Warm, pragmatic, time-scarce | Daycare pickups, school schedules, split attention, guilt about balance | Assuming single-earner or stay-at-home partner |
| healthcare_rns | Clinical empathy, shift-aware | 12-hour shifts, patient load, emotional labor, break rooms, scrubs | Trivializing medical settings as backdrop |
| gen_x_sandwich | Stoic resilience, dual-care | Aging parents + teenage kids, financial pressure from both ends, middle management | Treating as "just older millennials" |
| gen_alpha_students | Digital-native, identity-forming | School pressure, social media, parental expectations, future anxiety | Adult workplace framing; condescending tone |
| first_responders | Direct, sensory-grounded | Sirens, radios, adrenaline crashes, debrief rooms, hypervigilance | Glorifying trauma; office/desk metaphors |
| corporate_managers | Strategic, high-accountability | Reports, stakeholders, board pressure, isolation of leadership | Assuming they're the source of others' stress |
| educators | Patient, systems-aware | Classrooms, grading, admin burden, student emotional needs | Reducing to "summer off" stereotypes |
| entrepreneurs | Driven, uncertainty-tolerant | Runway, pivots, solo decisions, founder loneliness | Assuming VC-funded tech startup only |
| millennial_women_professionals | Assertive, intersectional | Glass ceiling, pay equity, impostor dynamics, visibility labor | Patronizing or reductive gender framing |
| nyc_executives | High-tempo, status-conscious | Corner offices, board rooms, car services, social performance | Assuming all finance; ignoring creative/media |
| tech_finance_burnout | Analytical, depleted | Screens, Slack, sprints, on-call, golden handcuffs | This IS the gen_z_professionals voice — differentiate by seniority/cynicism |

---

## 4. Acceptance criteria

### 4.1 Thin COMPRESSION — "not thin"

Per SOURCE_BANK_REPAIR_DEV_SPEC §8.2: ≥3 distinct compression variants OR ≥12 lines of substantive prose (excluding comments and fences).

### 4.2 Thin HOOK — "not thin"

≥12 words per variant. Each hook should have a distinct entry angle — no repetitive phrasing across variants.

### 4.3 Thin SCENE — "not thin"

Per §8.1: every `## SCENE vNN` block has ≥40 words body, ≥2 sentences, second-person present tense, at least one location token where applicable.

### 4.4 Voice re-localization — "persona-distinct"

For each of the 12 re-localized SCENE files:
- Framing lead of each scene references persona-specific context (not generic workplace)
- At least 3 scenes per file use persona-unique vocabulary from §3 voice table
- No two personas share >50% identical phrasing across their 30-scene banks
- Location tokens preserved from original structure

### 4.5 No regressions

- Zero new hollow files introduced
- Zero placeholder stubs (`[Scene N for …]`, TODO, TBD, etc.)
- YAML integrity maintained (0 parse failures)
- gen_z_professionals atoms untouched

---

## 5. PR-sized slices

### Phase A: Voice re-localization (highest priority — cloned content)

| Slice | Contents | Est. files | Primary owner |
|-------|----------|-----------|---------------|
| **PR-D1** | SCENE re-localization: working_parents + healthcare_rns (burnout + financial_anxiety, 4 files × 30 scenes each) | 4 | Pearl_Writer |
| **PR-D2** | SCENE re-localization: gen_x_sandwich + first_responders (burnout + financial_anxiety) | 4 | Pearl_Writer |
| **PR-D3** | SCENE re-localization: gen_alpha_students + corporate_managers (burnout + financial_anxiety) | 4 | Pearl_Writer |

### Phase B: Thin COMPRESSION repair (largest debt category)

| Slice | Contents | Est. files | Primary owner |
|-------|----------|-----------|---------------|
| **PR-D4** | Thin COMPRESSION: working_parents + healthcare_rns + first_responders (all topics) | ~40–50 | Pearl_Writer |
| **PR-D5** | Thin COMPRESSION: gen_x_sandwich + gen_alpha_students + corporate_managers (all topics) | ~40–50 | Pearl_Writer |
| **PR-D6** | Thin COMPRESSION: educators + entrepreneurs + millennial_women_professionals + nyc_executives + tech_finance_burnout | ~40–50 | Pearl_Writer |

### Phase C: Thin HOOK + SCENE repair

| Slice | Contents | Est. files | Primary owner |
|-------|----------|-----------|---------------|
| **PR-D7** | Thin HOOK: all personas (expand variants to ≥12 words each) | ~46 | Pearl_Writer |
| **PR-D8** | Thin SCENE: all personas except burnout/financial_anxiety already handled in D1–D3 | ~40–50 | Pearl_Writer |

### Phase D: Editorial verification

| Slice | Contents | Est. files | Primary owner |
|-------|----------|-----------|---------------|
| **PR-D9** | Editorial pass across all D1–D8 changes. Produce audit log at `artifacts/atom_debt_repair/d9_editorial_audit.md` | varies | Pearl_Editor |

**Total:** 9 PRs (PR-D1 through PR-D9). D1–D3 can run in parallel. D4–D6 can run in parallel after D1–D3 land. D7–D8 can run in parallel. D9 runs last.

---

## 6. Execution order and dependencies

```
Phase A (parallel):  D1  D2  D3     ← voice re-localization
                      \   |   /
Phase B (parallel):   D4  D5  D6    ← thin COMPRESSION
                       \  |  /
Phase C (parallel):    D7   D8      ← thin HOOK + SCENE
                        \  /
Phase D:                D9          ← editorial verification
```

No slice depends on another within the same phase. Each phase depends on the previous phase being merged to main.

---

## 7. File scope

### 7.1 Voice re-localization (D1–D3)

Modify only:
```
atoms/<persona>/burnout/SCENE/CANONICAL.txt
atoms/<persona>/financial_anxiety/SCENE/CANONICAL.txt
```
for the 6 personas listed in §2.3.

### 7.2 Thin COMPRESSION (D4–D6)

Modify only:
```
atoms/<persona>/<topic>/COMPRESSION/CANONICAL.txt
```
for files identified as thin in the pre-PR scan.

### 7.3 Thin HOOK (D7)

Modify only:
```
atoms/<persona>/<topic>/HOOK/CANONICAL.txt
```
for files identified as thin.

### 7.4 Thin SCENE (D8)

Modify only:
```
atoms/<persona>/<topic>/SCENE/CANONICAL.txt
```
for files identified as thin, excluding burnout/financial_anxiety (handled in D1–D3).

### 7.5 Editorial audit (D9)

Create:
```
artifacts/atom_debt_repair/d9_editorial_audit.md
```

---

## 8. Stop conditions

1. **Do not** modify gen_z_professionals atoms — they are the baseline.
2. **Do not** change Python/renderer/planner code.
3. **Do not** modify teacher banks or location profiles.
4. **Do not** expand persona taxonomy (new persona folders).
5. **Do not** modify this spec file with prose content.
6. If scan reveals **more** thin atoms than the 240 estimate, re-scope: ship D1–D3 (voice) first, update §2 counts, then proceed with revised D4–D8.
7. If a persona has **no** existing CANONICAL.txt for a slot, create it using gen_z_professionals as structural template (not voice template).

---

## 9. Ownership routing

| Slice | Pearl_Writer | Pearl_Editor | Pearl_Dev | Pearl_PM |
|-------|--------------|--------------|-----------|----------|
| D1–D3 | **Lead** | Review | — | Track |
| D4–D8 | **Lead** | Review | — | Track |
| D9 | Draft | **Lead** | — | Track |

---

## 10. Workstream registration

Register in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`:

```
ws_atom_debt_repair_20260330	proj_state_convergence_20260328	active	Pearl_Writer	agent/d1-voice-reloc	atoms/	docs/ATOM_DEBT_REPAIR_DEV_SPEC.md	none	Pearl_Editor	2026-03-30
```

---

## 11. Closeout criteria

Workstream is complete when:

1. All 240 thin atoms meet §4 thresholds (verified by D9 scan)
2. All 12 voice-cloned SCENE files pass §4.4 persona-distinct check
3. Zero regressions (§4.5)
4. D9 editorial audit log produced and committed
5. ACTIVE_WORKSTREAMS.tsv updated to `completed`

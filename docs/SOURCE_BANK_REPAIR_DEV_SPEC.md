# Source / Bank Repair — Dev Spec (Pearl Prime follow-up lane)

**Purpose:** After Pearl Prime recovery PRs **#67–#76**, runtime on `main` is **honest**: hollow banks and missing location profiles fail visibly instead of silently drifting. This spec audits **remaining content debt** under `atoms/gen_z_professionals/`, **teacher banks**, and **location profiles**, then defines a **scoped repair lane**. **Default:** prose + YAML atom/teacher work only — **no planner/renderer changes**. **Exception:** **PR-S0** may add a **config** profile plus a **narrow resolver test** so `teacher_persona_matrix` and `render_location_profiles.yaml` stay aligned (not a runtime feature change).

**Authority:** [docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md](./PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md) §5 Follow-up Lane; [docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md](./PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md) §PR 4 — Source/Bank Repair; [specs/TEACHER_MODE_V4_CANONICAL_SPEC.md](../specs/TEACHER_MODE_V4_CANONICAL_SPEC.md); [specs/PHOENIX_V4_5_WRITER_SPEC.md](../specs/PHOENIX_V4_5_WRITER_SPEC.md) (slot contracts).

**Status:** Dev spec — **no atom prose** in the spec file itself. Execution PRs follow the slice table; **PR-S0** is config + test only.

**Audit recorded:** 2026-03-30 against repo layout at `origin/main` including merge `aa3a76cb` (post–PR #76).

---

## 1. Scope and non-goals

### In scope

- `atoms/gen_z_professionals/<topic>/*/` narrative and engine CANONICAL banks.
- `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/` slot coverage and atom counts.
- `config/localization/render_location_profiles.yaml` profile entries (content of YAML — **Pearl_Dev**).

### Explicitly out of scope (this lane)

- **Runtime / planner / renderer code** — recovery lane closed; any bug there is a **separate runtime corrective PR**, not mixed into source-bank repair.
- **Persona redesign** beyond identifying misaligned tone (e.g. “too tech-office”) and listing atoms for editorial pass.
- **Writing** the actual repaired prose inside this spec (stop condition).

### Runtime / config drift (PR-S0 — run **before** PR-S5)

**Resolved path:** [config/catalog_planning/teacher_persona_matrix.yaml](../config/catalog_planning/teacher_persona_matrix.yaml) lists `coastal_california` under `ahjan.preferred_locales`. That ID must exist in [config/localization/render_location_profiles.yaml](../config/localization/render_location_profiles.yaml) with the **same key set** as `nyc_metro`. **PR-S0** (Pearl_Dev) adds the `coastal_california` profile and a **resolver test** so matrix preference and YAML stay provably aligned. **Execute PR-S0 before PR-S5** (additional MVP profiles); do not mix this into atom-only PRs.

---

## 2. Full audit — `gen_z_professionals` (15 topics)

### 2.1 Topic inventory

All paths under `atoms/gen_z_professionals/`. **15 topics** (directories):

| # | topic_id |
|---|----------|
| 1 | anxiety |
| 2 | boundaries |
| 3 | burnout |
| 4 | compassion_fatigue |
| 5 | courage |
| 6 | depression |
| 7 | financial_anxiety |
| 8 | financial_stress |
| 9 | grief |
| 10 | imposter_syndrome |
| 11 | overthinking |
| 12 | self_worth |
| 13 | sleep_anxiety |
| 14 | social_anxiety |
| 15 | somatic_healing |

### 2.2 Slot presence (structural)

For every topic, the following **narrative** slots exist with `CANONICAL.txt`: **HOOK, SCENE, EXERCISE, COMPRESSION, REFLECTION, INTEGRATION** (6/6 for all 15). **Engine** slots (watcher, spiral, shame, false_alarm, overwhelm, grief, comparison) exist with `CANONICAL.txt` for all 15.

**Conclusion:** There are **no missing slot directories** for the standard layout; debt is **quality/hollowness**, not missing folders.

### 2.3 Hollowness — SCENE (critical)

**Method:** For each `SCENE/CANONICAL.txt`, split on `## SCENE vNN` blocks; after YAML `---` fences, require **≥ ~30 characters** of non-empty body prose per scene (same structural pattern as healthy banks).

| topic_id | SCENE status | Notes |
|----------|---------------|--------|
| **overthinking** | **HOLLOW (20/20 scenes)** | Headers + `scene_type` only; **zero** scene body prose. Sentinel failure; compare `anxiety/SCENE/CANONICAL.txt` for gold pattern (location tokens + dense second-person prose). |
| All other 14 topics | **Has prose per scene** | No header-only SCENE banks detected by this audit. |

**Hollow SCENE count:** **1 topic** (overthinking). **20** empty scene bodies to author.

### 2.4 Hollowness / thin — COMPRESSION

**Method:** Total lines and non-comment non-`---` non-empty lines in `COMPRESSION/CANONICAL.txt`.

| topic_id | Lines (approx) | Assessment |
|----------|----------------|------------|
| overthinking | 7, ~0 body | **Hollow** |
| sleep_anxiety | 7, ~0 body | **Hollow** |
| burnout | 10, ~5 body | **Thin** |
| financial_anxiety | 10, ~5 body | **Thin** |
| imposter_syndrome | 10, ~5 body | **Thin** |
| social_anxiety | 10, ~5 body | **Thin** |
| somatic_healing | 10, ~5 body | **Thin** |
| *other 8 topics* | larger bodies | **OK** at compression slice |

**Hollow COMPRESSION:** **2** (overthinking, sleep_anxiety). **Thin COMPRESSION:** **5**.

### 2.5 Other narrative slots — spot check

- **sleep_anxiety / HOOK:** Only **4** substantive non-metadata lines across variants — **thin**; editorial should expand or merge variants to meet “production hook” density (see §5.1).

No other topics failed the coarse “&lt;5 non-empty body lines” sweep for HOOK / EXERCISE / REFLECTION / INTEGRATION.

### 2.6 Tech-coded / audience-narrow atoms (editorial judgment)

**Method:** Grep for workplace-tech lexicon across `atoms/gen_z_professionals/**/*.txt` (e.g. standup, Slack, sprint, code review). **Finding:** Widespread **tech-workplace framing** appears in multiple topics (e.g. social_anxiety, self_worth, sleep_anxiety, imposter_syndrome, overthinking). This is **appropriate** for a **gen_z_professionals** persona **when** it matches the reader; it is **debt** when it **excludes** non-desk workers or reads like a single-industry caricature.

**Recommendation:** Pearl_Writer / Pearl_Editor **sample review** per topic (at least **2 engine + 1 SCENE + 1 HOOK**) and mark atoms as:

- **keep** — tone matches persona + topic;
- **rewrite** — accurate mechanism but wrong register or too narrow;
- **split** — add alternate CANONICAL variants for non-tech settings (future PR, optional).

**No file list is exhaustive** in this pass; treat **social_anxiety**, **self_worth**, **imposter_syndrome**, **overthinking** as **priority editorial** (highest tech-office density in sample grep).

### 2.7 Persona atom summary counts

| Category | Count |
|----------|-------|
| Topics | **15** |
| Hollow SCENE banks | **1** (overthinking; 20 scenes) |
| Hollow COMPRESSION | **2** |
| Thin COMPRESSION | **5** |
| Thin HOOK (flagged) | **1** (sleep_anxiety) |

---

## 3. Full audit — teacher banks

### 3.1 Layout

Root: [SOURCE_OF_TRUTH/teacher_banks/](../SOURCE_OF_TRUTH/teacher_banks/). **12 teacher IDs** (directories): `ahjan`, `joshin`, `junko`, `maat`, `master_feung`, `master_sha`, `master_wu`, `miki`, `omote`, `pamela_fellows`, `ra`, `sai_ma`. Plus meta files `README.md`, `CREATION_SUMMARY.md` (**not** teachers).

### 3.2 Approved atoms — what exists

Under `approved_atoms/`:

| teacher_id | Non-empty slot dirs (with ≥1 `.yaml`/`.yml`/`.json`) |
|------------|------------------------------------------------------|
| ahjan | **EXERCISE, QUOTE, STORY, TEACHING** |
| All other 11 | **EXERCISE, STORY** only |

### 3.3 Slot-family completeness (Teacher Mode arc)

**Reference default chapter slot row** (when plan does not override): [phoenix_v4/qa/report_teacher_gaps.py](../phoenix_v4/qa/report_teacher_gaps.py) uses  
`["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]` per chapter as a fallback pattern.

**Gap:** **None** of the 12 teachers have **HOOK, SCENE, REFLECTION, or INTEGRATION** YAML banks under `approved_atoms/`. **STORY** and **EXERCISE** exist (counts vary by file layout).

**Conclusion:** **0 / 12** teachers are **slot-family complete** relative to that canonical row. Teacher Mode may still compile by **falling back** to persona atoms for missing slots — which is **correct runtime behavior** but **not** “teacher bank complete.”

### 3.4 Counts (for follow-up tooling)

Pearl_Dev may add a CI report later; this spec records **structural** finding only: **expand approved_atoms** per teacher with optional HOOK/SCENE/REFLECTION/INTEGRATION **or** document intentional persona-only policy in TEACHER_MODE spec (spec amendment — out of scope here).

---

## 4. Full audit — location profiles

### 4.1 Governed profiles today

File: [config/localization/render_location_profiles.yaml](../config/localization/render_location_profiles.yaml).

| profile_id | Aliases (examples) | Geography |
|------------|-------------------|-----------|
| `nyc_metro` | nyc, manhattan, new_york_city, … | NYC |
| `nyc_grand_central` | grand_central, midtown_east, … | NYC (commute variant) |
| `coastal_california` | coastal_ca, santa_monica, venice_beach, la_coast, … | US Pacific coast (LA / SoCal) |

**Total at spec refresh:** **3** profiles (2 NYC + **coastal_california** after **PR-S0**). *Audit baseline (2026-03-30) was 2 profiles only.*

### 4.2 Runtime implication

Renderer + CLI enforce **known profiles**. Any `--location` value **without** a matching profile **fails** at render time (honest failure). **Debt:** production breadth requires **more profiles** with the **same schema keys** (`city_name`, `weather_detail`, `street_name`, `transit_line`, …) populated with non-generic, non-copy-paste values.

### 4.3 Reasonable production set (proposal — content in YAML only)

**Minimum viable (MVP) content-ready** for Pearl Prime **outside NYC-only marketing**:

1. **`coastal_california`** — **PR-S0** (before S5); aligns `teacher_persona_matrix` ahjan preference with render YAML.
2. **`generic_us_urban`** — non-coastal, non-NYC (e.g. Midwest/Sunbelt) with distinct tokens (avoid cloning NYC strings); **PR-S5** or later.
3. **`london_uk`** or **`toronto_ca`** — one **non-US** English locale if international Gen Z is in scope.

**Full set (later slices):** Secondary US metros (Chicago, Atlanta, Austin), remote/WFH-specific profile, suburban commuter variant; each must pass **anti-duplication** vs existing profiles.

---

## 5. Prioritized repair plan

### 5.1 Highest priority — production runs & sentinel

1. **`overthinking/SCENE/CANONICAL.txt`** — **P0** (blocks quality for the recovery sentinel topic; 20 scenes).
2. **`overthinking/COMPRESSION/CANONICAL.txt`** + **`sleep_anxiety/COMPRESSION/CANONICAL.txt`** — **P0** (hollow).
3. **Thin COMPRESSION** (burnout, financial_anxiety, imposter_syndrome, social_anxiety, somatic_healing) — **P1**.
4. **`sleep_anxiety/HOOK/CANONICAL.txt`** — **P1** (thin).
5. **Location MVP** — **P1**: **PR-S0** (`coastal_california`), then **PR-S5** (`generic_us_urban` + further profiles).
6. **Teacher slot expansion** — **P2** (per-teacher PRs; start with **ahjan** if Teacher Mode is primary demo).
7. **Editorial tech-coded pass** — **P2–P3** (topic batches; no code).

### 5.2 Minimum viable vs full repair

| Scope | Definition |
|-------|------------|
| **MVP “production content-ready”** | overthinking SCENE + all hollow/thin COMPRESSION + sleep HOOK strengthened; **PR-S0** lands `coastal_california` (matrix + YAML aligned); teacher banks unchanged **if** product accepts persona-fallback Teacher Mode **or** ahjan gets minimal HOOK/SCENE/REFLECTION/INTEGRATION set for one demo arc. |
| **Full repair** | All 15 topics pass editorial QA; all 12 teachers slot-complete vs TEACHER_MODE canonical row; **8+** distinct location profiles with review for duplication and token freshness. |

---

## 6. PR-sized slices (ordering)

| Slice | Contents | Primary owner |
|-------|----------|---------------|
| **PR-S0** | **`coastal_california`** profile in `config/localization/render_location_profiles.yaml` (full key parity with `nyc_metro`) + resolver test in `tests/test_location_passthrough.py`. **Land before PR-S5** so ahjan `preferred_locales` and render config agree. | Pearl_Dev |
| **PR-S1** | `atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt` (full fill, 20 bodies) | Pearl_Writer |
| **PR-S2** | `atoms/gen_z_professionals/overthinking/CANONICAL.txt` path **COMPRESSION** + `sleep_anxiety/COMPRESSION/CANONICAL.txt` | Pearl_Writer |
| **PR-S3** | Thin COMPRESSION five topics (single PR or 2× PRs by batch size) | Pearl_Writer |
| **PR-S4** | `sleep_anxiety/HOOK/CANONICAL.txt` expansion | Pearl_Writer |
| **PR-S5** | `config/localization/render_location_profiles.yaml` — **remaining** MVP profiles (`generic_us_urban`, optional intl) + alias lists; **no** change to `coastal_california` unless editorial tweak | Pearl_Dev |
| **PR-S6** | `SOURCE_OF_TRUTH/teacher_banks/ahjan/approved_atoms/` — add HOOK, SCENE, REFLECTION, INTEGRATION YAML set for one golden arc (minimal viable teacher completeness) | Pearl_Writer + Pearl_Dev (schema/validation) |
| **PR-S7** | Remaining teachers (one teacher per PR or paired small teachers) | Pearl_Writer |
| **PR-S8** | Editorial “tech-coded” batch (topic pair per PR, changelog table in PR body) | Pearl_Editor |

**Suggested count:** **9** PRs (**PR-S0** … **PR-S8**); can merge S3+S4 or split S8 by topic for reviewability.

**Pearl_PM:** Register workstream in `ACTIVE_WORKSTREAMS.tsv` (or equivalent) when lane starts; link this spec.

---

## 7. File scope (create / modify)

### 7.1 Atom prose (Pearl_Writer / Pearl_Editor)

- `atoms/gen_z_professionals/overthinking/SCENE/CANONICAL.txt` (**modify**)
- `atoms/gen_z_professionals/overthinking/COMPRESSION/CANONICAL.txt` (**modify**)
- `atoms/gen_z_professionals/sleep_anxiety/COMPRESSION/CANONICAL.txt` (**modify**)
- `atoms/gen_z_professionals/sleep_anxiety/HOOK/CANONICAL.txt` (**modify**)
- `atoms/gen_z_professionals/{burnout,financial_anxiety,imposter_syndrome,social_anxiety,somatic_healing}/COMPRESSION/CANONICAL.txt` (**modify**)
- Optional: additional `CANONICAL.txt` paths flagged in editorial passes (**modify**)

### 7.2 Location (Pearl_Dev)

- `config/localization/render_location_profiles.yaml` (**modify**) — **PR-S0** adds `coastal_california`; **PR-S5** adds further MVP profiles.
- `tests/test_location_passthrough.py` (**modify**) — **PR-S0** asserts `coastal_california` / alias resolution.

### 7.3 Teacher banks (Pearl_Writer + Pearl_Dev)

- `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/approved_atoms/<SLOT>/*.yaml` (**create**)
- Optional doctrine updates: `SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine/*.yaml` (**modify** — only if needed for MTA alignment)

### 7.4 Matrix ↔ YAML alignment

- **PR-S0** satisfies `ahjan.preferred_locales` → `coastal_california` by **adding** the profile (matrix unchanged). If a future teacher lists a locale with **no** profile, either add the profile (preferred) or remove the preference in `teacher_persona_matrix.yaml` in the **same PR** as the profile work.

---

## 8. Acceptance criteria

### 8.1 Atom / SCENE — “not hollow”

- Every `## SCENE vNN` block includes YAML frontmatter **and** a **body** paragraph (second-person present, **≥ 2 sentences** or **≥ 40 words**, with at least **one** location token from profile when run with `--location`, where applicable).
- **No** scene body may be empty or metadata-only.
- Spot-check: render one chapter using topic SCENE pool — no `LocationGroundingError` attributable to empty scene text.

### 8.2 Atom / COMPRESSION — “not hollow / not thin”

- **≥ 3** distinct compression variants OR **≥ 12** lines of substantive prose total (excluding `#` comments and `---` fences), whichever matches existing file conventions for “healthy” topics (e.g. anxiety baseline).

### 8.3 Teacher bank — “slot-family complete” (for a chosen arc)

For each chapter slot in the **target arc’s** `chapter_slot_sequence` row:

- If slot is **STORY** or **EXERCISE**: **≥ 1** approved atom per required band (for STORY) or **≥ required EXERCISE count** per [report_teacher_gaps.py](../phoenix_v4/qa/report_teacher_gaps.py) logic.
- If slot is **HOOK, SCENE, REFLECTION, INTEGRATION**: **≥ 1** approved teacher atom **or** documented intentional fallback to persona atoms (requires spec amendment — default for this lane is **populate teacher YAML**).

### 8.4 Location profile — “production-ready”

- New profile defines **all keys** present on `nyc_metro` (no `null` placeholders).
- **Distinct** prose tokens vs other profiles (no copy-paste NYC strings into “Chicago”).
- Aliases cover CLI/common variants; documented in PR body.
- **PR-S0:** `coastal_california` covered by `tests/test_location_passthrough.py` resolver assertions; extend the same test file for new profiles in **PR-S5**.

---

## 9. Stop conditions

1. **Do not** paste final atom prose into this spec — spec stays non-content.
2. **Do not** change Python/renderer/planner in this lane, except **PR-S0** / **PR-S5** may extend **`tests/test_location_passthrough.py`** for profile resolution smoke checks only.
3. **Do not** expand persona taxonomy (new persona folders) without PM/architect approval.
4. If audit shows **additional hollow banks** (e.g. after stricter QA), **re-scope MVP**: ship P0/P1, file follow-up spec revision **v1.1** with new counts.
5. If **runtime** bug found (e.g. profile load error), **stop** bank PR and file **runtime corrective**; do not patch code inside atom PRs.

---

## 10. Ownership routing (per slice)

| Slice | Pearl_Writer | Pearl_Editor | Pearl_Dev | Pearl_PM |
|-------|--------------|--------------|-----------|----------|
| S0, S5 | — | — | **Lead** | Track |
| S1–S4 | **Lead** | Review | — | Track |
| S6–S7 | **Lead** | Review | Schema/validation | Track |
| S8 | Draft | **Lead** | — | Track |

---

## 11. Closeout (this spec’s deliverable)

### 11.1 Audit summary

| Metric | Value |
|--------|-------|
| `gen_z_professionals` topics | **15** |
| Hollow SCENE topics | **1** (overthinking; **20** scenes) |
| Hollow COMPRESSION | **2** |
| Thin COMPRESSION | **5** |
| Thin HOOK (flagged) | **1** (sleep_anxiety) |
| Teacher dirs | **12** |
| Teachers slot-complete vs HOOK–INTEGRATION row | **0 / 12** |
| Location profiles in YAML | **2** at original audit (**both NYC**); **3** after **PR-S0** (`coastal_california`) |

### 11.2 PR slices

- **9** proposed ordered slices (**PR-S0** … **PR-S8**); **S0 before S5**; merge/split allowed for review size.

### 11.3 MVP vs full

- **MVP:** overthinking SCENE + hollow/thin compression fixes + sleep HOOK + location MVP + optional ahjan teacher expansion.
- **Full:** all topics editorially reviewed, all teachers slot-complete, **8+** geo-distinct profiles.

### 11.4 Surprises / larger-than-expected debt

- **Teacher gap is systemic:** only STORY+EXERCISE exist for 11/12 teachers; Teacher Mode “full bank” is far larger than atom-only repair.
- **Tech-office language** is pervasive — editorial effort may exceed single PR-S8; expect **multiple** editorial batches.
- **Config/runtime drift:** `coastal_california` in matrix without profile was a **product blocker** — address with **PR-S0** before **PR-S5**.

### 11.5 Follow-up lane readiness

**Source/bank repair** is **ready to execute** as prose/YAML PRs against this spec; **Pearl_PM** should register the workstream and assign owners per slice.

---

**Last updated:** 2026-03-30 (PR-S0 ordering + `coastal_california` profile path)

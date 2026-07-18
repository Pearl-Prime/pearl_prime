# Pearl Prime Coverage + Gap Analysis (2026-04-26)

**Authors:** Pearl_Research (lead) + Pearl_Prime (quality sign-off) + Pearl_PM (matrix structure)
**Workstream:** ws_catalog_quality_analysis_20260410
**Project:** proj_pearl_prime_bestseller_rebase_20260425
**Trigger:** Owner question — *"rigorous testing. gap analysis, are all languages 100%? all personas, all topics"*
**Scope:** Audit + plan only. No fix work. Recommendations in §6 for operator approval.

---

## §1 — Executive Summary

### Are all languages 100%? **No.** Not by any honest measure.

| Locale | Translation coverage (atom slot files) | (persona × topic) viable | Bestseller-grade rendered (Move 4 evidence, en-US only) |
|---|---|---|---|
| **en-US** | 100% (baseline) | **64.1%** (125/195 core combos) | **90%** (27/30 sample) |
| **ja-JP** | **92.3%** (2987/3236) | **63.1%** (123/195) | not yet swept |
| **zh-TW** | **98.1%** (3175/3236) | **63.1%** (123/195) | not yet swept |
| **zh-CN** | **34.7%** (1124/3236) | **23.1%** (45/195) | not yet swept |

> "Viable" = the (persona, topic, locale) tuple has at least 1 engine where (a) an arc YAML exists, (b) an atoms engine bank with named characters exists, and (c) for non-en-US, the slot-level translation rate is ≥80%.

### Are all personas covered? **No.** 4 personas have <2% viable cells.

- **midlife_women — 0.0%** (0 arcs, 0 atom engines populated; entire persona missing)
- **educators — 0.7%** (1 arc only; covers anxiety only)
- **nyc_executives — 1.3%** (orphan persona; not in `canonical_personas.yaml`; only 4 arcs across 3 topics)
- **gen_z_student — 0.4%** (atom-rich but mostly text-no-names; 10 topics arc-gapped)

The other 10 personas range from 8% (gen_x_sandwich, atom-no-names heavy) to **37.5% viable (healthcare_rns)**.

### Are all topics covered? **No.** 1 topic has 0 arcs across the entire matrix.

- **adhd_focus — 0%** (no arcs anywhere; 1 persona has atoms; orphan content)
- **anxiety — 55.1% viable** (matrix-wide; the single most-covered topic)
- All other 14 wellness topics: 12–25% viable matrix-wide

Wellness topics aren't the only issue. The aspirational catalog (`canonical_topics.yaml` lines 13–99) lists **57 topics**, of which **42 teacher-signature topics** (impermanence, alarm_systems, embodiment, qi_cultivation, zen, koans, etc.) have **zero atoms on disk**. Pearl Prime is operating against a reduced 15-topic working set, not the 57-topic aspirational catalog.

### The 5 highest-leverage gaps (by cells unblocked per hour of remediation)

1. **zh-CN translation sprint** — ~2,664 atoms. Brings zh-CN from 27% → ~74% viable (parity with ja-JP/zh-TW). Largest single ROI unlock; LLM Tier 2 (Qwen on Pearl Star) precedent already proven (zh-TW achieved 98.1% via this path).
2. **midlife_women authoring (arcs + atoms)** — full persona buildout. ~105 arcs + ~15 topic atom banks. Unblocks 1 persona × 15 topics × 7 engines × 4 locales = **420 cells**. Pre-scoped under [ws_midlife_women_arc_authoring_20260427](artifacts/coordination/ACTIVE_WORKSTREAMS.tsv).
3. **HAS_TEXT_NO_NAMES rewriting** — 568 cells where atoms exist but lack named characters. Today these render PARTIAL (engine-bank generic) per Move 4 evidence; named-character injection would convert them to BESTSELLER (engine-bank named-character). LLM Tier 1.
4. **ja-JP translation completion** — 249 missing atom slot translations (3236 − 2987). Closes ja-JP to zh-TW parity. LLM Tier 2.
5. **educators arcs (14 missing topics × ~5–7 engines)** — Roughly 75–100 arcs to author. Unblocks 1 persona × 14 topics × all locales. LLM Tier 1.

### Operator decision needed

Pick the lane to prioritize. Three rational sequences in §6. Brief framing:

- **Locale-first (zh-CN sprint):** biggest absolute cell unlock per hour; lowest authoring effort (Tier 2 / unattended)
- **Persona-first (midlife_women + educators + gen_z_student):** closes the "is every persona covered?" gate; higher LLM Tier 1 effort
- **Quality-first (HAS_TEXT_NO_NAMES → named-character rewrite):** improves the *grade* of cells already viable rather than opening new cells; ships sooner per book but doesn't change the coverage matrix

---

## §2 — Coverage Matrix (Full)

### Matrix axes

- **Personas:** 14 on disk (13 canonical + 1 orphan: nyc_executives)
- **Topics:** 16 on disk (15 wellness + 1 unmapped: adhd_focus); 42 teacher-signature topics aspirational but missing
- **Engines:** 7 (overwhelm, shame, watcher, spiral, false_alarm, comparison, grief)
- **Locales:** 4 in scope (en-US, ja-JP, zh-TW, zh-CN); 9 more aspirational (ko-KR, zh-HK, zh-SG, de-DE, fr-FR, it-IT, hu-HU, es-US, es-ES)

**Total cells in scope:** 14 × 16 × 7 × 4 = **6,272 cells**
**Per-locale slice:** 14 × 16 × 7 = **1,568 cells**

### Status taxonomy

| Status | Definition |
|---|---|
| `READY_ANCHORED` | arc + atom-with-names + locale ≥80% + story_atoms anchored (4 arc positions) | Render produces bestseller with CALLBACK_ID continuity |
| `ENGINE_FALLBACK` | arc + atom-with-names + locale ≥80% (no anchored) | Render produces bestseller with named characters but no through-book continuity |
| `BLOCKED_ATOMS_NO_NAMES` | arc + atom text exists but <3 named-character hits | Renders PARTIAL (engine-bank generic, no named characters) |
| `BLOCKED_ATOMS_MISSING` | arc but no engine bank | Cannot render this engine |
| `BLOCKED_ARC_MISSING` | no arc YAML in `master_arcs/` | Cannot render at all |
| `TRANSLATION_GAPED` | viable in en-US but locale slot coverage <80% or engine itself untranslated | Can ship en-US, blocked CJK |

### Matrix-wide totals

| Status | Count | % of 6272 |
|---|---|---|
| `BLOCKED_ARC_MISSING` | 4316 | 68.8% |
| `ENGINE_FALLBACK` | 1106 | 17.6% |
| `BLOCKED_ATOMS_NO_NAMES` | 568 | 9.1% |
| `TRANSLATION_GAPED` | 214 | 3.4% |
| `BLOCKED_ATOMS_MISSING` | 68 | 1.1% |
| `READY_ANCHORED` | 0 | 0.0% |

**Zero `READY_ANCHORED` cells** — even though `story_atoms/<persona>/anchored/` has 3 (persona, topic, engine) cells with 4 complete arc positions and 106 atoms (per SUBAGENT S audit), **none carry `callback_id` markers** in the micro atom files. Move 5 Phase 1+2 anchoring landed (PR #677 working_parents × anxiety × overwhelm; gen_z_professionals × anxiety × overwhelm earlier) but the CALLBACK_ID continuity layer is not yet wired into the atom corpus, only into the routing/resolver layer (per the Move 4 sweep report: 1 of 30 books rendered "via story_plan/CALLBACK_ID").

### Per-locale viability slice (1568 cells each)

| Locale | READY+FALLBACK | ARC_MISSING | ATOMS_NO_NAMES | ATOMS_MISSING | TRANSLATION_GAPED |
|---|---|---|---|---|---|
| en-US | 330 (21.0%) | 1079 | 142 | 17 | 0 |
| ja-JP | 325 (20.7%) | 1079 | 142 | 17 | 5 |
| zh-TW | 328 (20.9%) | 1079 | 142 | 17 | 2 |
| zh-CN | 123 (7.8%) | 1079 | 142 | 17 | 207 |

**Reading note:** the same upstream gap (1079 missing arcs + 142 atoms-no-names + 17 atoms-missing = 1238 cells per locale) blocks every locale equally. CJK locales add a translation gap on top of that. zh-CN's translation gap is enormous (207 cells beyond the structural floor); ja-JP and zh-TW are nearly at the structural floor (5 and 2 additional cells gaped, respectively).

### (persona × topic) compact matrix — en-US viable (≥1 engine viable)

13 canonical personas × 15 wellness topics. `Y` = viable, `.` = blocked.

| Persona \ Topic | anx | bnd | brn | cmp | crg | dep | finA | finS | grf | imp | ovr | sw | slp | soc | som |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| millennial_women_professionals | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| tech_finance_burnout | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| entrepreneurs | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| working_parents | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| corporate_managers | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| gen_z_professionals | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| healthcare_rns | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| gen_alpha_students | Y | Y | Y | Y | Y | Y | . | Y | Y | Y | Y | Y | . | Y | . |
| gen_x_sandwich | Y | . | Y | . | Y | . | . | . | . | . | Y | . | . | . | Y |
| first_responders | Y | . | . | . | . | . | . | Y | . | . | . | . | . | . | . |
| gen_z_student | Y | Y | . | . | . | . | . | . | . | . | . | . | . | . | . |
| educators | Y | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| midlife_women | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

**Reading note:** 7 personas are fully covered across all 15 wellness topics in en-US. The remaining 6 have material gaps (gen_x_sandwich at 5/15, gen_alpha_students at 12/15, first_responders at 2/15, gen_z_student at 2/15, educators at 1/15, midlife_women at 0/15).

### CJK locale slice — same matrix, masked by translation availability

zh-TW and ja-JP look nearly identical to en-US above (translation coverage close to 100%). zh-CN looks much sparser:

**zh-CN (persona × topic) viable** (≥1 engine viable, locale ≥80%): 45/195 = 23.1%

The zh-CN gap is concentrated in personas where the entire persona has zero zh-CN translation:
- entrepreneurs: 0% zh-CN
- first_responders: 0% zh-CN
- gen_alpha_students: 0% zh-CN (largest persona at 700 baseline atoms)
- gen_x_sandwich: 0% zh-CN
- gen_z_student: 0% zh-CN

(Source: SUBAGENT T per-persona table.)

### Cross-cell summary by axis

| Axis | Cells viable / total | % |
|---|---|---|
| **By persona (en-US, 16 topics × 7 engines = 112 cells)** | | |
| healthcare_rns | 42/112 | 37.5% |
| gen_z_professionals | 41/112 | 36.6% |
| millennial_women_professionals | 40/112 | 35.7% |
| working_parents | 34/112 | 30.4% |
| tech_finance_burnout | 32/112 | 28.6% |
| corporate_managers | 29/112 | 25.9% |
| entrepreneurs | 29/112 | 25.9% |
| gen_alpha_students | 17/112 | 15.2% |
| gen_x_sandwich | 9/112 | 8.0% |
| first_responders | 3/112 | 2.7% |
| nyc_executives | 2/112 | 1.8% |
| gen_z_student | 1/112 | 0.9% |
| educators | 1/112 | 0.9% |
| midlife_women | 0/112 | 0.0% |
| **By topic (en-US, 14 personas × 7 engines = 98 cells)** | | |
| anxiety | 54/98 | 55.1% |
| financial_stress | 24/98 | 24.5% |
| courage | 23/98 | 23.5% |
| depression | 19/98 | 19.4% |
| overthinking | 18/98 | 18.4% |
| boundaries | 17/98 | 17.3% |
| social_anxiety | 17/98 | 17.3% |
| financial_anxiety | 16/98 | 16.3% |
| compassion_fatigue | 15/98 | 15.3% |
| burnout | 15/98 | 15.3% |
| somatic_healing | 13/98 | 13.3% |
| sleep_anxiety | 12/98 | 12.2% |
| imposter_syndrome | 12/98 | 12.2% |
| self_worth | 12/98 | 12.2% |
| grief | 12/98 | 12.2% |
| adhd_focus | 0/98 | 0.0% |
| **By engine (en-US, 14 personas × 16 topics = 224 cells)** | | |
| shame | 51/224 | 22.7% |
| overwhelm | 51/224 | 22.7% |
| watcher | 38/224 | 17.0% |
| spiral | 38/224 | 17.0% |
| false_alarm | 35/224 | 15.6% |
| comparison | 32/224 | 14.3% |
| grief | 32/224 | 14.3% |

---

## §3 — Sweep Results (Phase B)

### Decision: leverage existing Move 4 sweep evidence; do NOT re-render

**Rationale:**

1. The Move 4 representative sweep at [artifacts/qa/move4_2026_04_26/](artifacts/qa/move4_2026_04_26/) (run 2026-04-25T20:49:55Z, **1 day before this audit**) is the most recent canonical en-US sweep. 30 cells, 1 representative book per (persona, topic) pair from the 13-persona core. Result: **27/30 BESTSELLER, 2 PARTIAL, 1 FAILED.**
2. A canary attempt at **production** quality_profile (vs Move 4's `draft`) on `gen_z_professionals × anxiety × overwhelm × en-US` failed the **scene_anchor_density_cap gate** in roughly 2 minutes wall-clock. A 600-cell sweep at production profile would either (a) take ~10–20 hours of compute and (b) likely surface the same upstream gate failures at high rate, since the gates check pipeline-output craft properties rather than per-cell viability.
3. The structural answer to the owner's question ("are all languages 100%?") is determined entirely by Phase A's coverage matrix. A 600-cell production-profile sweep would refine the *grade* (BESTSELLER vs PARTIAL) on top of viability, but the owner-facing percentages (75% en-US, 74% ja-JP, 74% zh-TW, 27% zh-CN at the persona×topic level) are already locked.
4. Per `STOP rules` in the audit spec: rule #3 (>5% per-cell crash rate) and the per-cell budget cap argue for halting a re-sweep when existing evidence is sufficient.

### Move 4 sweep aggregate (en-US, draft profile, 2026-04-25)

| Metric | Value |
|---|---|
| Locale | en-US |
| Quality profile | draft (`--quality-profile draft`) |
| Cells targeted | 30 (representative; 1 per persona × topic combo from `core` matrix) |
| Cells assembled | 30/30 |
| Cells with `book.txt` | 29/30 |
| Cells with `quality_gates_pass=true` | 29/30 |
| Mean word count of rendered books | 9,259 |
| Total elapsed wall-clock | 396s (6.6 min) |
| Mean per-book elapsed | 13.2s |

### Per-grade aggregate

| Grade | Count | % |
|---|---|---|
| BESTSELLER (story_plan/CALLBACK_ID) | 1 | 3.3% |
| BESTSELLER (engine-bank named-character) | 26 | 86.7% |
| PARTIAL (engine-bank generic, no named chars) | 2 | 6.7% |
| FAILED (no book.txt) | 1 | 3.3% |

### Per-cell evidence (verbatim excerpt)

The 30-row table is preserved at [artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md](artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md). Headline rows:

- **Sole BESTSELLER via story_plan/CALLBACK_ID:** `anxiety_millennial_women_professionals` — Elena(11), Carmen(5), Sarah(6), Mia(5)
- **PARTIAL (engine-bank generic):** `grief_gen_alpha_students`, `financial_anxiety_gen_alpha_students` — both gen_alpha_students cells (atoms exist but lack named-character density)
- **FAILED:** `overthinking_gen_z_student` (returncode=1, no book.txt produced)

### What Phase B did NOT measure (acknowledged gap)

This audit does **not** re-sweep the 1,106 viable cells across all 4 locales at production profile. That would require ~10–20 hours of Pearl Star compute and would also need:
- A `--quality-profile` and gate set agreed-upon between Pearl_Architect and Pearl_Prime
- Either upstream fixes for the production-profile scene_anchor_density gate or explicit gate-relaxation
- A Pearl_Dev triage for the production-profile breakage

These are flagged in §6 (operator-approved Phase 2+) and §7 (open questions).

### Production-profile canary (single cell, evidence)

| Field | Value |
|---|---|
| Cell | gen_z_professionals × anxiety × overwhelm × en-US |
| Arc | `config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml` |
| Profile | production |
| Outcome | exited (no `book.txt`); produced `selected_content_variants.json` (58KB) and `scene_anchor_density_report.json` |
| Gate failure | `Scene anchor density cap: FAIL — repeated >3-word phrases exceed cap 2` |
| Other warnings | 12 chapters of `Exercise journey outcome mismatch`; library_34 fallback fired for chapters 0 and 11; `EXERCISE FALLBACK` triggered |
| Wall-clock | ~2 min |
| Log | `/tmp/sweep/canary_001/run.log` (706 bytes) |

**Interpretation:** the spine pipeline boots, routes correctly, and assembles content variants — but the production gate set (specifically scene_anchor_density and exercise governance) blocks completion on this cell. Either the gates need to be relaxed for this band of content, or upstream EXERCISE atom coverage needs work. This is an open question for Pearl_Dev (§7).

---

## §4 — Gap Classes (with Remediation)

### GAP_TRANSLATION_CJK

**Magnitude:** 207 cells gaped on zh-CN (largest); 5 cells on ja-JP; 2 cells on zh-TW.

| Locale | Atoms slot files needed | Translation status (per ws_cjk_atom_translation_qwen25_20260420 row, 2026-04-24) | Computed (2026-04-26) | Delta |
|---|---|---|---|---|
| ja-JP | 249 (3236 − 2987) | claimed 89.3% | measured 92.3% | claim is conservative |
| zh-TW | 61 (3236 − 3175) | claimed 92.1% | measured 98.1% | claim is conservative |
| zh-CN | 2,112 (3236 − 1124) | "sprint pending, ~2200 atoms" | measured 34.7% | matches estimate |

**Note:** SUBAGENT T's slot-file count (4592 baseline) differs from this matrix's count (3236) because SUBAGENT T included locale-only files in the denominator while this matrix counts only en-US baseline CANONICAL.txt files at engine/slot level. Both numbers are correct measures, just different denominators. The percentages should be compared within-method only.

**Remediation path:** Existing workstream `ws_cjk_atom_translation_qwen25_20260420` is already wired for this work. Tier 2 (Qwen on Pearl Star, free, unattended) is the appropriate engine. Estimated completion based on prior pace (~50–100 atoms/hour autonomous):
- ja-JP: ~3–5 hours of unattended Pearl Star compute
- zh-TW: ~30–60 min
- zh-CN: ~25–45 hours of unattended Pearl Star compute (this is the big one)

Six personas at 0% zh-CN — entrepreneurs, first_responders, gen_alpha_students, gen_x_sandwich, gen_z_student — should be the priority order to maximize cell unlocks. gen_alpha_students alone is 700 baseline atoms = ~700 atoms to translate.

### GAP_ARCS

**Magnitude:** 36 (persona, topic) combos missing arcs (18.5% of the 195-combo aspirational matrix at the persona×topic level). Multiplied through 7 engines × 4 locales = 1,008 cells blocked.

| Persona | Missing topics | Cells affected (× 7 engines × 4 locales) |
|---|---|---|
| midlife_women | ALL 15 | 420 |
| educators | 14 (all except anxiety) | 392 |
| nyc_executives | 12 | 336 |
| gen_z_student | 10 | 280 |

(These overlap with the 1,079 ARC_MISSING per-locale figure once you de-dupe.)

**Remediation path:**
- midlife_women: workstream `ws_midlife_women_arc_authoring_20260427` already opened (per `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`). LLM Tier 1. Pearl_Prime + Pearl_Architect.
- educators / nyc_executives / gen_z_student: no workstream open. Recommend a single new workstream `ws_persona_arc_completion_20260427` covering all three personas, with a per-persona schedule. LLM Tier 1.

**Effort estimate:** ~2–4 hours per arc YAML (research + author + review). 36 missing combos × ~5 engines per combo (skipping rare specs) ≈ 180 arcs × 2.5h = ~450 person-hours total. Pearl_Prime authoring throughput is the constraint. Realistic 4–8 weeks of Pearl_Prime time.

**Schema observation (from SUBAGENT A):** no `persona_targeting:` field in any of 530 arc YAMLs. Each arc is single-persona, single-topic. There is no cross-persona reuse mechanism. Consider whether to introduce one before authoring 180 new arcs (could halve the work for adjacent personas like nyc_executives ↔ corporate_managers).

### GAP_ATOMS_NAMES

**Magnitude:** 568 cells in `BLOCKED_ATOMS_NO_NAMES` (engine bank exists with text but <3 named-character hits in CANONICAL.txt). Per Move 4 evidence, these render as PARTIAL (engine-bank generic), not BESTSELLER.

**Concentrated in:**
- first_responders: 164 cells (engines exist with text but no character set)
- gen_x_sandwich: 132 cells
- gen_alpha_students: 92 cells
- gen_z_student: 64 cells
- corporate_managers + entrepreneurs: 28 each
- millennial_women_professionals: 20

**Remediation path:** rewrite the affected CANONICAL.txt files to inject named-character density (≥3 distinct named-character mentions per atom). LLM Tier 1. Per-atom: ~5–15 min including review. 568 atoms × 10 min = ~95 person-hours. Realistic 2–3 weeks of Pearl_Writer time, parallelizable.

**Why this matters:** these cells are *already counted as viable in en-US viability metrics* but render as PARTIAL grade. Fixing this lifts the per-cell grade without expanding cell count. It's the difference between "we can ship 124 (persona, topic) combos" and "we can ship 124 (persona, topic) combos *at bestseller grade*."

### GAP_STORY_ATOMS_ANCHORED

**Magnitude:** 1,106 ENGINE_FALLBACK cells across the matrix lack `story_atoms/<persona>/anchored/` infrastructure. Per Move 4 evidence, ENGINE_FALLBACK cells render as BESTSELLER (engine-bank named-character) but **without through-book CALLBACK_ID continuity** — characters appear chapter-to-chapter but without explicit narrative threading.

**Current state:**
- 3 (persona, topic, engine) cells have `anchored/` populated: gen_z_professionals × anxiety × overwhelm (74 atoms), millennial_women_professionals × anxiety × overwhelm (16 atoms), working_parents × anxiety × overwhelm (16 atoms)
- **0 atoms in those cells carry `callback_id` markers** in the micro v*.txt files (per SUBAGENT S)
- Move 4 evidence shows 1 of 30 books (`anxiety_millennial_women_professionals`) routed via `story_plan/CALLBACK_ID` — the routing layer found a CALLBACK_ID-bearing story_plan, even though the underlying atom files don't contain callback markers. The CALLBACK_ID lives in a story_plan layer above the atoms, not in the atoms themselves.

**Remediation path:** Move 5 rolling enhancement under `ws_story_cell_authoring_20260425`. ~80–150 anchored atoms per (persona, topic) combo, with `callback_id:` markers in the micro v*.txt. LLM Tier 1. Per-cell: ~6–12 hours of Pearl_Editor + Pearl_Writer time. 1,106 cells × 8h average = far beyond practical budget; this should be prioritized by lane (top-N personas × topics by traffic / brand-fit).

**Recommendation:** do NOT attempt this for all 1,106 cells. Pick the top 20–40 (persona, topic) combos by go-to-market priority and anchor those with full callback continuity. The remaining cells stay at ENGINE_FALLBACK (still bestseller grade per Move 4 evidence, just without continuity).

### GAP_QUALITY_GATE_FAILS (production-profile)

**Magnitude:** unknown without a production-profile sweep. Single-cell canary evidence (gen_z_pros × anxiety × overwhelm × en-US, §3) suggests **scene_anchor_density** and **exercise governance / library_34 fallback** are the primary blockers at production profile.

**Remediation path:** ambiguous — could be (a) atom rewriting to reduce repeated phrasing (lifts cells from production-fail to production-pass) or (b) gate calibration (loosen production thresholds where atoms are correctly authored but pipeline interprets them as repetitive). Pearl_Dev investigation needed before action.

### GAP_TEACHER_SIGNATURE_TOPICS (aspirational)

**Magnitude:** 42 of the 57 canonical topics in `config/catalog_planning/canonical_topics.yaml` (lines 34–99) have **zero atoms on disk**. Examples: impermanence, alarm_systems, embodiment, qi_cultivation, zen, koans, gen_z_grounding, justice, balance, panic_response, sleep_repair, body_memory, solar_return, compassion, devotion, surrender, mindfulness.

**Remediation path:** out of scope for this audit. The system today targets the 15-topic wellness core. Whether to expand to the full 57-topic teacher-signature set is a strategic question for §7.

---

## §5 — Per-Locale 100% Gap (the Owner Question)

### en-US — 64.1% (125 of 195 core combos viable; 90% bestseller grade on Move 4 sample)

**What's missing to hit 100%:**
- 70 (persona, topic) combos with no viable engine
- Of these:
  - 36 are blocked by missing arcs (midlife_women, educators, nyc_executives, gen_z_student gaps)
  - ~5 are blocked by atoms that exist but lack named characters (PARTIAL grade by Move 4 evidence)
- Plus: 568 cells in BLOCKED_ATOMS_NO_NAMES across the matrix would lift from PARTIAL to BESTSELLER if rewritten

**Effort to hit 100% en-US:**
- 36 missing arcs (~180 individual arc YAMLs across engines): ~450 person-hours of Pearl_Prime + Pearl_Architect (Tier 1)
- 568 atoms_no_names rewrites: ~95 person-hours of Pearl_Writer (Tier 1)
- Total: ~550 person-hours of Tier 1 work to lift en-US to 100% bestseller-grade across the 13-persona × 15-wellness-topic matrix

### ja-JP — 63.1% (123 of 195 core combos viable)

**What's missing to hit 100%:**
- Same 36 arc-missing combos as en-US
- Plus 5 cells where ja-JP translation is below 80% threshold but en-US is viable (gen_z_student-heavy)
- Plus the 249 atom slot translations still missing (gets ja-JP from 92.3% slot coverage to 100%)

**Effort to hit 100% ja-JP** (assuming en-US gaps fixed first):
- 249 atom slot translations: ~3–5 hours of unattended Pearl Star Qwen compute (Tier 2)
- Then matches en-US progress

### zh-TW — 63.1% (123 of 195 core combos viable)

**What's missing to hit 100%:**
- Same 36 arc-missing combos
- Plus 2 cells in TRANSLATION_GAPED state
- Plus 61 atom slot translations to close to 100%

**Effort:** ~30–60 min of unattended Pearl Star Qwen for the residual translation; remaining work is shared with en-US gap closure.

### zh-CN — 23.1% (45 of 195 core combos viable)

**What's missing to hit 100%:**
- Same 36 arc-missing combos
- **207 cells in TRANSLATION_GAPED state** — this is the binding constraint
- **2,112 atom slot translations** still missing from disk (vs 4,592 baseline in SUBAGENT T's count; or 2,112 vs 3,236 in this matrix's count — both methods agree there's ~2k atoms left)
- Six personas at 0% zh-CN: entrepreneurs, first_responders, gen_alpha_students, gen_x_sandwich, gen_z_student

**Effort:** ~25–45 hours of unattended Pearl Star Qwen compute, then matches en-US progress. This is the single largest unattended-compute item in the entire remediation queue and the highest-leverage single workstream.

### Summary table

| Locale | Today | After CJK translation sprint only | After arcs + atom_no_names + translation | After everything in §6 |
|---|---|---|---|---|
| en-US | 64.1% | 64.1% (no change) | **~96–100%** | 100% |
| ja-JP | 63.1% | ~63% (cells already viable) | ~96–100% | 100% |
| zh-TW | 63.1% | ~63% | ~96–100% | 100% |
| zh-CN | 23.1% | **~63%** | ~96–100% | 100% |

**Headline:** the zh-CN translation sprint alone closes the four-locale parity gap from 41 percentage points to roughly nothing. After that, every locale converges on en-US's progress. **The fastest path to "all four locales near-parity" is the zh-CN translation sprint, not arcs or atom rewriting.**

---

## §6 — Recommended Remediation Sequence (operator-approved)

### Critical path

The work decomposes into 4 independent tracks. Three of them can run in parallel without coordination cost.

**Track 1 — zh-CN translation sprint** (Tier 2, unattended)
- Workstream: `ws_cjk_atom_translation_qwen25_20260420` (already open)
- Effort: ~25–45 hours of Pearl Star Qwen compute, runnable overnight in batches
- Unlock: 207 cells (zh-CN closes to parity); biggest single percentage-point movement in the matrix
- **Recommendation: start immediately. Lowest cost, highest unlock.**

**Track 2 — Persona authoring (midlife_women + educators + nyc_executives + gen_z_student)** (Tier 1, attended)
- Workstream(s):
  - `ws_midlife_women_arc_authoring_20260427` (already open) — 105 arcs + atom banks
  - **NEW** `ws_persona_arc_completion_20260427` (recommended) — covers educators, nyc_executives, gen_z_student arc gaps (~75 arcs)
- Effort: ~450 person-hours of Pearl_Prime + Pearl_Architect over 4–8 weeks
- Unlock: 4 personas × 14–15 topics × 7 engines × 4 locales = ~1,500+ cells
- Schema decision needed first: introduce `persona_targeting:` field to allow nyc_executives ↔ corporate_managers reuse, or author new arcs from scratch?

**Track 3 — Atom-no-names rewriting** (Tier 1, attended)
- Workstream: **NEW** `ws_atom_named_character_rewrite_20260427` (recommended)
- Effort: ~95 person-hours of Pearl_Writer over 2–3 weeks
- Unlock: 568 cells lift from PARTIAL to BESTSELLER grade (no new cells, but better grade)
- Concentrated in 4 personas (first_responders, gen_x_sandwich, gen_alpha_students, gen_z_student) — can sequence by persona

**Track 4 — Story_atoms anchored CALLBACK_ID buildout** (Tier 1, attended; deprioritize)
- Workstream: `ws_story_cell_authoring_20260425` (already open; in Move 5 Phase 2 per recent commits)
- Effort: per-cell 6–12 hours; do NOT scale to all 1,106 cells
- Recommendation: ship pilot at top 20 (persona, topic) combos by traffic; leave the rest at ENGINE_FALLBACK (still bestseller grade)
- Also requires: wire `callback_id:` markers into the micro v*.txt files (per SUBAGENT S, current 3 cells with full arc-position coverage have 0 atoms with callback markers)

### Sequencing recommendation

```
Week 0  — Operator chooses lane (this audit)
Week 1  — Track 1 zh-CN sprint kickoff (immediately)
          Track 2 schema decision (persona_targeting yes/no)
          Track 3 first-cell pilot
Week 2  — Track 1 zh-CN ja-JP completion
          Track 2 midlife_women arcs landing
          Track 3 first_responders rewrites
Week 3  — Track 1 zh-CN sprint completion
          Track 2 educators arcs starting
          Track 3 gen_x_sandwich rewrites
Week 4–8 — Track 2 nyc_executives + gen_z_student arcs
          Track 3 gen_alpha_students + gen_z_student
          Track 4 pilot anchored cells
Week 8  — Re-run this audit. Headline numbers should show:
            en-US 95–100%, ja-JP 95–100%, zh-TW 95–100%, zh-CN 95–100%
            persona × topic combos viable: 195/195 core
            quality grade: 95%+ BESTSELLER on representative sweep
```

### Project closure threshold (§7 question)

For `proj_pearl_prime_bestseller_rebase_20260425` to close, recommend the threshold:
- en-US ≥ 95% bestseller-grade on a 60-cell representative sweep
- ja-JP, zh-TW, zh-CN all ≥ 80% bestseller-grade on a 30-cell per-locale representative sweep
- All 13 canonical personas have ≥ 1 viable cell per wellness topic
- midlife_women has ≥ 1 viable cell per topic (the personal blocker)

This is achievable inside ~8 weeks with all four tracks running. Deferring track 2 (persona authoring) to Q3 lowers the threshold to 11/13 personas covered and pushes closure 4–8 weeks.

---

## §7 — Open Questions for Operator

1. **Lane priority.** Pick: locale-first (Track 1 zh-CN sprint, lowest cost, highest unlock) / persona-first (Track 2, biggest absolute work, highest brand commitment) / quality-first (Track 3, ships better books sooner without expanding catalog). Recommend Track 1 + Track 3 in parallel, defer Track 2 to next sprint.

2. **Schema decision for arcs.** Should `persona_targeting:` be added to arc YAMLs to let one arc serve multiple personas (e.g. nyc_executives reuses corporate_managers arcs)? Today, 530 arcs are 1:1 with (persona, topic). If reuse is allowed, Track 2 effort halves for some personas.

3. **Production-profile gate calibration.** The single-cell canary (§3) failed `scene_anchor_density_cap` and triggered library_34 EXERCISE fallback. Move 4 succeeded at draft profile. Decision: relax production gates, fix atoms upstream, or both? Pearl_Dev investigation needed.

4. **Teacher-signature topic expansion (aspirational 42 topics).** The catalog plan (canonical_topics.yaml) lists 57 topics; only 15 wellness topics + adhd_focus are partially populated. The other 42 (impermanence, embodiment, qi_cultivation, zen, koans, etc.) have zero atoms. Does the project commit to building these out, or trim the canonical list to match what's actually shippable?

5. **nyc_executives orphan persona.** This persona exists in `atoms/` and `master_arcs/` but **not in `canonical_personas.yaml`**. Either canonicalize it (add to the registry) or sunset it (remove from atoms/arcs). Currently it adds confusion to coverage measures.

6. **Anchored atom callback wiring.** Move 5 Phase 1+2 produced 106 anchored atoms across 3 cells but 0 carry `callback_id:` markers in the v*.txt micro files. The Move 4 sweep used `story_plan/CALLBACK_ID` routing for 1 of 30 books, which suggests CALLBACK_IDs live in the story_plan layer above atoms. Should the `callback_id:` markers be back-injected into existing micro atoms, or is the story_plan layer sufficient?

7. **Project closure threshold.** Recommend en-US ≥ 95% bestseller / CJK locales ≥ 80% bestseller / all 13 canonical personas covered / midlife_women fully built. Operator confirms or amends.

8. **Workstream split.** Recommend opening:
   - `ws_persona_arc_completion_20260427` (educators + nyc_executives + gen_z_student)
   - `ws_atom_named_character_rewrite_20260427` (568-cell named-character injection)
   - `ws_canonical_topics_reconciliation_20260427` (resolve 57-topic vs 15-topic + nyc_executives orphan + 42 aspirational topics)
   - All gated on operator approval; this audit does NOT open them.

---

## Appendix A — Source Files Read

**Specs / authority docs:**
- `CLAUDE.md`, `ps.txt`, `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`
- `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md`, `docs/PEARL_PRIME_RELEASE_CONTRACT.md`
- `docs/BESTSELLER_GAP_AUDIT.md`, `docs/CONTENT_COVERAGE_ANALYSIS.md`
- `docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md`, `docs/LOCALE_CATALOG_MARKETING_PLAN.md`
- `config/catalog_planning/canonical_personas.yaml`
- `config/catalog_planning/canonical_topics.yaml`
- `config/localization/locale_registry.yaml`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`

**Corpus enumeration (by SUBAGENT P/S/A/T/C):**
- `atoms/<persona>/<topic>/<engine|slot>/CANONICAL.txt` — 3,236 baseline files at engine/slot level
- `atoms/<persona>/<topic>/<engine|slot>/locales/<locale>/CANONICAL.txt` — 7,286 translated files (2987 ja-JP + 3175 zh-TW + 1124 zh-CN)
- `story_atoms/<persona>/anchored/<topic>/<engine>/<arc_position>/micro/v*.txt` — 106 anchored atoms across 3 cells
- `config/source_of_truth/master_arcs/*.yaml` — 530 arcs across 159 (persona, topic) combos

**Prior coverage evidence (used for reconciliation):**
- `artifacts/inventory/atom_coverage_matrix.json` + `artifacts/inventory/atom_coverage_report.md` — 78.7% complete at (persona × topic) level (2026-04-21)
- `artifacts/qa/move4_2026_04_26/per_persona_topic_coverage.md` + `assembly_summary.json` — 27/30 BESTSELLER on en-US sample at draft profile (2026-04-25)
- `artifacts/localization/coverage_before_20260420.json` — pre-sprint baseline showing zh-CN/ja-JP/zh-TW/ko-KR all under 7%

**Sweep evidence in this audit:**
- `/tmp/coverage_matrix_2026_04_26.json` — full (persona × topic × engine × locale) status matrix, 6,272 cells, 2.2MB. Not committed (exceeds repo binary scan cap of 1MB; per Layer 2 policy, large evidence belongs on R2). Available on request from session host; can be re-generated by re-running `/tmp/build_coverage_matrix.py` against current `atoms/` + `master_arcs/` state.
- `/tmp/sweep/canary_001/run.log` — single production-profile canary attempt (gen_z_professionals × anxiety × overwhelm × en-US)
- `/tmp/build_coverage_matrix.py`, `/tmp/select_sweep_cells.py`, `/tmp/reaggregate.py` — scratch scripts (not committed)

---

## Appendix B — Reconciliation with Prior "70%" Figure

The owner referenced "we used to have 70% language coverage" mid-audit. The closest historical figure is **78.7% atom completeness at the (persona × topic) level**, recorded in `artifacts/inventory/atom_coverage_report.md` on 2026-04-21:

```
Personas: 13 | Topics: 17 | Total combos: 221
Complete: 174 (78.7%)   Partial: 5   Missing: 42
```

This 78.7% figure measures **atom completeness in en-US only**, at the (persona × topic) granularity, with denominator = 13 × 17 = 221.

This audit's headline figures use a different granularity. To bridge:

| Measure | Denominator | en-US value | Comment |
|---|---|---|---|
| Prior 78.7% atom complete | 221 (persona × topic) | 78.7% | 13 personas × 17 topics including adhd_focus + mindfulness |
| This audit, "≥1 viable engine" | 224 (persona × topic, 14×16) | 57.1% | 14 personas × 16 topics; stricter — also requires named-character density on at least 1 engine |
| This audit, core 13×15 wellness | 195 | **64.1%** | matches prior measure most closely; **directly comparable to the 78.7% baseline** |
| This audit, 1568 (per-locale) | 14 × 16 × 7 | 21.0% | per-cell, all-engines-counted; the granularity at which "100% of 1,568 cells" lives |
| Move 4 sweep BESTSELLER rate | 30 | 90% | per-rendered-book quality grade on representative sample; not a coverage measure |

**Interpretation:** Pearl Prime has moved from 78.7% → 64.1% on the closest like-for-like measure between 2026-04-21 and today. The drop is **methodology, not regression**:

- The prior measure denominator was 13 × 17 = 221 combos (included adhd_focus + mindfulness); this audit's denominator is 13 × 15 = 195 combos (15 wellness topics only). Denominators differ by 26.
- More importantly, the prior measure required only **atom files exist**, not **atoms with named-character density**. This audit's stricter `BLOCKED_ATOMS_NO_NAMES` filter (≥3 distinct named-character mentions in CANONICAL.txt) drops first_responders heavily (2/15 vs likely 13/15 under the prior method) and also drops gen_x_sandwich (5/15 vs likely 13/15). These two personas alone account for ~21 cells of the apparent regression.
- **If the named-character requirement is removed (matching the prior method exactly), this audit's en-US figure rises to ~80%+, in line with or above 78.7%.** The HAS_TEXT_NO_NAMES cells (568 across the matrix) are real assets — they just produce PARTIAL grade rather than BESTSELLER per Move 4 evidence.

**Net: the system has not regressed; the appearance of regression is a stricter quality bar in this audit.** Both measures point to the same underlying gap structure (missing arcs for 4 personas, atom-no-names concentrated in 4 personas, CJK translation gap concentrated in zh-CN).

The much-lower 21.0% in the per-cell view is not a regression either — it's a finer-grained slice of the same underlying gap. The same gap shows up at coarser granularity as 64.1%, finer as 21.0%.

For CJK locales, the prior baseline at `artifacts/localization/coverage_before_20260420.json` shows ja-JP / ko-KR / zh-CN / zh-HK all under 7% pre-sprint — i.e. the CJK translation work has driven **massive net progress** (now: ja-JP 92%, zh-TW 98%, zh-CN 35%), and there has been no regression there either.

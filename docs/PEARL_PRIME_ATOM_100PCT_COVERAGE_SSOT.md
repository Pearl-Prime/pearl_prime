# Pearl Prime — Atom 100% Coverage SSOT

**Date:** 2026-06-06
**Author:** Pearl_Architect
**Status:** active — CANONICAL; supersedes every prior partial-coverage atom audit
**Authority:** Pearl_Architect (architecture) + Pearl_Editor (atom-authoring upstream per `PEARL-EDITOR-UPSTREAM-01`) + Pearl_Writer (engine-bank authoring) + Pearl_Localization (locale variants)
**Cap entry:** `ATOM-100PCT-COVERAGE-SSOT-V1-01` ([`PEARL_ARCHITECT_STATE.md`](./PEARL_ARCHITECT_STATE.md))
**Project:** `PRJ-PEARL-PRIME-FEATURE-UTILIZATION` + `proj_pearl_prime_bestseller_rebase_20260425`

---

## §1. Purpose + Operator Directive

**Operator directive (verbatim, 2026-06-06):**

> "I want 100% of atoms so I can write all books for all personas and topics and languages. Use existing docs that did this and update them with new findings."

**This doc is the canonical SSOT for the operator's 100%-atom-coverage gate.** It:

1. Defines the **100% coverage matrix** (dimensions, required vs optional cells, math).
2. Audits **current coverage** against the matrix (per-persona, per-topic, per-atom-type, per-locale).
3. Surfaces the **gap matrix** ([`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](../artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv)) — every missing (persona, topic, atom_type, locale, variants) tuple needed to hit 100%.
4. **Prioritizes** gaps into 6 tiers (P0-P5) per Phase A en-US launch gate + Phase B/C/D locale phases.
5. Routes authoring to child workstreams (Pearl_Editor, Pearl_Writer, Pearl_Localization, Pearl_Dev CI guard).
6. **Supersedes** every prior partial-coverage audit doc by cross-link (originals retained per [`AGENT_FILE_PERSISTENCE_PROTOCOL.md`](./AGENT_FILE_PERSISTENCE_PROTOCOL.md)).

**Anti-drift:** This doc is the single source of truth for "what 100% means" + "where we are vs target" + "who authors what next." Every child atom-authoring ws PR updates §9 (gap matrix) in place per the protocol in §13. CI guard (§14, Pearl_Dev ws) validates §9 nightly against `atoms/`.

---

## §2. The 100% Coverage Matrix

### Dimensions

| Dim | Symbol | Cardinality | Source-of-truth |
|---|---|---|---|
| Persona | P | **14** (on-disk; see §4) | `atoms/<persona>/` directory listing |
| Topic | T | **15** (canonical) | `registry/*.yaml` (15 files; see §5) |
| Atom type (persona-keyed) | A_pk | **16** per `PEARL-PRIME-ONE-PATH-V1-01` D8 | `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` §2 D8 — see §3 below |
| Atom type (directive subset audited) | A_d | **9** (the directive's named subset; covered fully in §3) | this SSOT — directive scope |
| Locale | L | **13** (official) | `config/localization/locale_registry.yaml` (en-US baseline + 12 non-baseline) — see §6 |
| Variant | V | floor ≥ **3**; ceiling ≤ **5** opt-in | `SPEC-739-THRESHOLD-01` cap entry |

> **Important framing note:** the operator directive named **9 atom types** as the audit scope (HOOK, COMPRESSION, REFLECTION, INTEGRATION, STORY, EXERCISE, QUOTE, TEACHER_DOCTRINE, PERMISSION_GRANT). The canonical ONE-PATH-V1-01 D8 requires **16 slot-type dirs** per persona×topic (adds SCENE, PIVOT, PERMISSION, TAKEAWAY, THREAD, TEACHER_DOCTRINE_INTRO, ANGLE_DEFINITION, ANGLE_CALLBACK). This SSOT audits the directive's 9 in §8 + §9; the remaining 7 slot-type dirs are covered as "legacy / non-directive" in **Q-Atom-DIRECTIVE-9-VS-CAP-16-01** (§12) — operator decides whether SSOT scope expands to 16 or stays at 9. If 16 wins, the gap matrix expands ≈ 1.78× (16/9); if 9 wins, the 7 remaining slot-types stay tracked under the existing cap entry routing.

### Math (target)

**Under directive scope (A=9):**

| Quantity | Formula | Value |
|---|---|---|
| Total matrix cells | P × T × A_d × L | 14 × 15 × 9 × 13 = **24,570** |
| Phase A en-US persona-keyed cells | P × T × 6 (HOOK/COMPRESSION/REFLECTION/INTEGRATION/STORY/EXERCISE) × 1 (en-US) | 14 × 15 × 6 × 1 = **1,260** |
| Phase A en-US overlay-routed cells | P × T × 3 (QUOTE/TEACHER_DOCTRINE/PERMISSION_GRANT) × 1 (en-US) | 14 × 15 × 3 × 1 = **630** |
| Phase A en-US total cells | P × T × A_d × 1 | 14 × 15 × 9 × 1 = **1,890** |
| Phase A minimum variants (≥3 floor) | 1,890 × 3 | **5,670** atoms |
| All-locale 100% (Phase D end-state) | 24,570 × 3 | **73,710** atoms minimum |

**Under ONE-PATH-V1-01 D8 cap-scope (A_pk=16; Q-Atom-DIRECTIVE-9-VS-CAP-16-01 = expand):**

| Quantity | Formula | Value |
|---|---|---|
| Total matrix cells | P × T × A_pk × L | 14 × 15 × 16 × 13 = **43,680** |
| Phase A en-US cells | P × T × 16 × 1 | 14 × 15 × 16 × 1 = **3,360** |
| Phase A minimum variants | 3,360 × 3 | **10,080** atoms |
| Scope-expansion factor vs directive | 16 / 9 | 1.78× |

### Required vs optional cells (production-profile catalog runs)

A cell is **REQUIRED** if a production-profile (`--quality-profile production`) catalog run for that (persona, topic, atom_type, locale) tuple would hard-fail at runtime without it. See §3 for which atom types are persona-keyed-required vs overlay-routed-required.

A cell is **OPTIONAL** if it adds variant richness but is not gate-blocking.

| Phase | Locale scope | Required cell shape | Phase-completion gate |
|---|---|---|---|
| **A** | en-US only | All 9 atom types × ALL personas × ALL topics × en-US | 1,890 cells × ≥3 variants = 5,670 atoms |
| **B** | + ja-JP | + 1,890 ja-JP cells × ≥3 variants | + 5,670 atoms |
| **C** | + zh-TW + zh-CN | + 3,780 cells × ≥3 variants | + 11,340 atoms |
| **D** | + ko-KR + extended (Q-Atom-LOCALE-SCOPE-01) | + remaining locales | gated on operator decision |

---

## §3. Atom Type Catalog (the 9)

The 9 atom types fall into two routing classes per the runtime overlay waterfall codified in `SPEC-739-VALIDATOR-AWARENESS` (cap entry; `PEARL_ARCHITECT_STATE.md:358-386`) and `QUOTE-ATOM-ROUTING-01` (cap entry; `PEARL_ARCHITECT_STATE.md:708-720`):

### Class 1 — Persona-keyed-required (6 types)

Required at `atoms/<persona>/<topic>/<atom_type>/CANONICAL.txt` per the runtime overlay path; ≥3 variants per cell per `SPEC-739-THRESHOLD-01`. Runtime fail-fast under production-profile if cell missing.

| # | Atom type | Section role | Required? | Authority |
|---|---|---|---|---|
| 1 | **HOOK** | Section 1 opener; scene-first per `HOOK-SCENE-FIRST-01` | YES | `SOMATIC_10_SLOT_GRID[0]`; `registry/<topic>.yaml` chapter_*.section_01 |
| 2 | **COMPRESSION** | Late-chapter tightening; rhythmic recap | YES | overlay role per `TEMPLATE-UNIVERSAL-01` |
| 3 | **REFLECTION** | Sections 3 + 7 of grid | YES | `SOMATIC_10_SLOT_GRID[2]`, `[6]` |
| 4 | **INTEGRATION** | Section 10 closer | YES | `SOMATIC_10_SLOT_GRID[9]` |
| 5 | **STORY** | Sections 2 + 5 + 9 of grid; named-character bestseller bank per `BESTSELLER-INJECTIONS-MANDATORY-01` | YES | `SOMATIC_10_SLOT_GRID[1]`, `[4]`, `[8]`; engine bank under `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` |
| 6 | **EXERCISE** | Sections 4 + 8 of grid; canonical exercise atom per `EXERCISE-BANK-RESOLUTION-01` Option 1 (strict-canonical for production) | YES | `SOMATIC_10_SLOT_GRID[3]`, `[7]`; falls through to `teacher_banks/<teacher>/approved_atoms/EXERCISE/` then `practice_library/store/practice_items.jsonl` per spec §4.5 [^exercise-component-lift] |

[^exercise-component-lift]: **Footnote (per AMENDMENT-2026-06-11 §17):** [PR #1486](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486) (`EXERCISE-COMPONENT-SCHEMA-LIFT-01`, 771e714e8) lifted PracticeItem schema v1 → v2 with parallel `components` field `{bridge, intro, description, aha, integration} × {full, lean}`. Renderer reads components when present; falls back to v1 `text` + teacher-config wrappers when components null. Per-format variant policy in [`config/practice/selection_rules.yaml`](../config/practice/selection_rules.yaml) `component_variant_by_format`: **full** for `{extended_book_2h, deep_book_4h, deep_book_6h}`; **lean** for 17 other runtime formats. See §17 for the full AMENDMENT block + A1-A6 acceptance criteria for Pearl_Dev review.

### Class 2 — Overlay-routed (3 types — NOT persona-keyed at runtime)

These types are resolved at runtime via overlay paths (teacher_banks, registry, story_atoms) rather than persona-keyed `atoms/<persona>/<topic>/<atom_type>/CANONICAL.txt` files. Per `QUOTE-ATOM-ROUTING-01` Option (d) — retire-as-orphan: persona-keyed `QUOTE/` atoms exist (~9 files, ahjan-only) but never load; canonical QUOTE injection is teacher-bank-routed.

| # | Atom type | Routing | Required source | Authority |
|---|---|---|---|---|
| 7 | **QUOTE** | overlay via `teacher_banks/<teacher>/approved_atoms/QUOTE/*.yaml` | per cell (P,T): at least one teacher's QUOTE bank covers the (persona, topic) combo per teacher_persona_compatibility | `QUOTE-ATOM-ROUTING-01`; `teacher_banks/<teacher>/approved_atoms/QUOTE/` |
| 8 | **TEACHER_DOCTRINE** | overlay via `teacher_banks/<teacher>/doctrine/*.txt` + persona-keyed `TEACHER_DOCTRINE_INTRO/` (10 files exist) | per cell: ≥1 doctrine file per teacher per topic | `SPEC-739-VALIDATOR-AWARENESS`; `PEARL-EDITOR-UPSTREAM-01`; `phoenix_v4/planning/injection_resolver.py` |
| 9 | **PERMISSION_GRANT** | runtime-rendered via `teacher_banks/<teacher>/approved_atoms/PERMISSION/*.yaml` | per cell: PERMISSION atom bank covers (P,T) combo | `TEACHER-POOL-SEMANTICS-01`; PERMISSION resolver |

**Persona-keyed gap status for Class 2 (en-US):**

- QUOTE: 210 of 210 (persona, topic) cells have **0** persona-keyed atoms — confirms `QUOTE-ATOM-ROUTING-01` retire-as-orphan ratification.
- TEACHER_DOCTRINE: 205 of 210 cells have **0** persona-keyed atoms (5 cells carry the new `TEACHER_DOCTRINE_INTRO/` directory).
- PERMISSION_GRANT: 209 of 210 cells have **0** (the legacy `PERMISSION/` dir = 1,760 files but is a different slot type; `PERMISSION_GRANT/` is the directive's name and persona-keyed-empty by design).

**For Class 2 100% coverage = overlay backing, not persona-keyed cells.** The gap matrix flags these rows with `status=overlay_routed_not_persona_keyed` so child ws's route to teacher-bank authoring (Pearl_Editor) rather than persona-keyed atom authoring. **Q-Atom-DIRECTIVE-9-VS-GRID-5-01 surfaces whether the directive's 9-type-cell framing should formally split into the 6-persona-keyed + 3-overlay-routed shape.**

---

## §4. Persona Enumeration

**14 personas on-disk under `atoms/`** (audited via `ls -d atoms/*/`):

| # | Persona | Atom cell count | Status |
|---|---|---|---|
| 1 | `corporate_managers` | 19 topic dirs (incl. legacy `anchored`, `people_pleasing`, `adhd_focus`, `trauma_recovery`) | FULL (15/15 canonical + 4 extras) |
| 2 | `educators` | 15 | 8 topic gaps per [`persona_atom_audit.md`](../artifacts/audit/persona_atom_audit.md) |
| 3 | `entrepreneurs` | 16 (+anchored) | FULL (15/15) |
| 4 | `first_responders` | 15 | FULL |
| 5 | `gen_alpha_students` | 17 (extras) | FULL |
| 6 | `gen_x_sandwich` | 15 | FULL |
| 7 | `gen_z_professionals` | 15 | FULL (GOLD reference per memory) |
| 8 | `gen_z_student` | 15 | 3 topic gaps per persona_atom_audit |
| 9 | `healthcare_rns` | 16 (+anchored) | FULL |
| 10 | `midlife_women` | 15 | 15/15 atom dirs exist but **0 master_arcs** per `system_size.md` axis A6; arc-blocked for catalog runs |
| 11 | `millennial_women_professionals` | 16 (+anchored) | FULL |
| 12 | `nyc_executives` | 15 | 7 topic gaps per persona_atom_audit |
| 13 | `tech_finance_burnout` | 15 | FULL |
| 14 | `working_parents` | 16 (+anchored) | FULL |

**`canonical_personas.yaml` lists 11 canonical personas** — educators + nyc_executives + midlife_women are on-disk but not declared canonical (per `persona_atom_audit.md` Note line 22). **Open: Q-Atom-PERSONA-SCOPE-01** for retire-vs-keep + canonical YAML reconciliation.

---

## §5. Topic Enumeration (15 canonical)

Per `registry/*.yaml` audit (15 files, all present):

`anxiety` · `boundaries` · `burnout` · `compassion_fatigue` · `courage` · `depression` · `financial_anxiety` · `financial_stress` · `grief` · `imposter_syndrome` · `overthinking` · `self_worth` · `sleep_anxiety` · `social_anxiety` · `somatic_healing`

Authority: `ws_topic_registries_20260409`, [`registry_coverage_vs_catalog.md`](../artifacts/audit/registry_coverage_vs_catalog.md).

---

## §6. Locale Enumeration

Per [`config/localization/locale_registry.yaml`](../config/localization/locale_registry.yaml) (schema_version: 1):

| # | Locale | Baseline? | Current atom coverage | Phase |
|---|---|---|---|---|
| 1 | `en-US` | YES | full (overlay waterfall) | Phase A |
| 2 | `ja-JP` | no | 4,241 atoms | Phase B |
| 3 | `zh-TW` | no | 4,531 atoms | Phase C |
| 4 | `zh-CN` | no | 1,928 atoms | Phase C |
| 5 | `ko-KR` | no | 227 atoms | Phase D |
| 6 | `zh-HK` | no | 243 atoms | Phase D (subset of CJK Traditional) |
| 7 | `zh-SG` | no | 243 atoms | Phase D (subset of CJK Simplified) |
| 8 | `es-US` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |
| 9 | `es-ES` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |
| 10 | `fr-FR` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |
| 11 | `de-DE` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |
| 12 | `it-IT` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |
| 13 | `hu-HU` | no | **0** | Q-Atom-LOCALE-SCOPE-01 |

**Per [`pearl_prime_audit_2026-06-06.md`](../artifacts/qa/pearl_prime_audit_2026-06-06.md) axis A6:** the operator-original "5 official locales" framing (en-US + ja-JP + zh-TW + zh-CN + ko-KR) covers Phase A-D. The 13-locale registry adds 8 European/Spanish locales declared but un-authored. **Open: Q-Atom-LOCALE-SCOPE-01** to set the 100% locale ceiling for SSOT acceptance criteria.

---

## §7. Variant Floor + Ceiling

Per `SPEC-739-THRESHOLD-01` cap entry (ratified 2026-04-28):

| Bound | Value | Authority | Runtime enforcement |
|---|---|---|---|
| **Floor** | ≥3 variants per atom-type cell | `SPEC-739-THRESHOLD-01` + `SOMATIC_10_SLOT_GRID` | **OFFLINE ONLY** today via `scripts/registry/validate_variant_coverage.py`; runtime selector does NOT assert ≥3 — see `ws_runtime_variant_floor_assertion_20260606` (proposed; `pearl_prime_audit_2026-06-06.md` §3 #7) |
| **Ceiling** | ≤5 opt-in via per-section `min_variants_required: 5` | `SPEC-739-THRESHOLD-01` | per-section override at `registry/<topic>.yaml` section level |

**Acceptance for §16 100%-coverage:** Phase A en-US passes when every cell has ≥3 variants. Variant enrichment to 5 (Tier P5) is post-launch optional.

---

## §8. Current Coverage (audit findings)

### §8.1 — Per-persona persona-keyed atom-type coverage (en-US)

For the 6 persona-keyed atom types (HOOK / COMPRESSION / REFLECTION / INTEGRATION / STORY / EXERCISE), per persona, how many of the 15 topics have the cell at `atoms/<persona>/<topic>/<atom_type>/CANONICAL.txt` (≥1 variant)?

| Persona | HOOK | COMP | REFL | INTEG | STORY | EXER | Topic-cells filled (of 15×6=90) | Notes |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---:|---|
| corporate_managers | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| educators | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | **48/90** | 7-topic gap |
| entrepreneurs | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| first_responders | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| gen_alpha_students | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| gen_x_sandwich | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| gen_z_professionals | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | GOLD reference |
| gen_z_student | 12/15 | 12/15 | 12/15 | 12/15 | 12/15 | 12/15 | **72/90** | 3-topic gap |
| healthcare_rns | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| **midlife_women** | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | atoms exist BUT **0 master_arcs** → arc-blocked |
| millennial_women_professionals | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| nyc_executives | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | **48/90** | 7-topic gap |
| tech_finance_burnout | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| working_parents | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | **90/90** | FULL |
| **TOTAL** | — | — | — | — | — | — | **1,176 / 1,260 (93.3%)** | **84-cell gap** |

**Persona-keyed type gap shape (en-US):** 84 cells short of 1,260; 100% achievable by authoring 17 persona×topic combos: educators (7 topics × 6 types = 42 cells), nyc_executives (42 cells), gen_z_student (3 topics × 6 types = 18 cells) — but gen_z_student is in the gap matrix as 18 already-filled cells with insufficient variants vs 0 cells; actual 100% en-US persona-keyed gap = **84 cells = 84 × 3 = 252 minimum variants** (Tier P1).

### §8.2 — Per-topic coverage

All 15 topics have registry files + ≥1 persona authoring per topic. No topic is uniformly empty. The 84-cell §8.1 gap is **persona×topic-skewed**, concentrated in 3 personas.

### §8.3 — Per-persona×topic 9-type completeness

Per discovery scan (210 P×T cells audited):

| 9-type sum (cells with N of 9 directive types) | Count | % |
|:---:|---:|---:|
| 9 of 9 | **0** | 0% |
| 8 of 9 | 1 | 0.5% |
| 7 of 9 | 4 | 1.9% |
| 6 of 9 | 176 | 83.8% |
| 5 of 9 | 29 | 13.8% |

**0 of 210 cells have all 9 directive types persona-keyed.** This is **EXPECTED** given §3 Class 2 routing — QUOTE/TEACHER_DOCTRINE/PERMISSION_GRANT are overlay-routed, not persona-keyed. The 176 cells at "6 of 9" carry all 6 persona-keyed types — the canonical complete state. Cells at "5 of 9" or below have a true persona-keyed-type gap.

### §8.4 — Locale coverage

Per locale, total atoms across the tree:

| Locale | Atoms | Coverage status |
|---|---:|---|
| en-US (baseline overlay) | 16,292 CANONICAL.txt | full (overlay waterfall) |
| ja-JP | 4,241 | ~26% of full en-US equivalent |
| zh-TW | 4,531 | ~28% |
| zh-CN | 1,928 | ~12% |
| ko-KR | 227 | ~1.4% |
| zh-HK | 243 | ~1.5% |
| zh-SG | 243 | ~1.5% |
| es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU | **0 each** | 0% — Phase D blocker / Q-Atom-LOCALE-SCOPE-01 |

### §8.5 — Variant-floor compliance

Sample variant counter (block + YAML marker max per file):

- 100% of audited persona-keyed cells with ≥1 variant clear the ≥3 floor at the en-US `CANONICAL.txt` level (HOOK files sample 120+ variant markers each; engine banks 27-40 each).
- Compliance failure is **missing cell** (84-cell gap §8.1), not low variant count within existing cells.
- **Runtime variant-floor assertion is NOT in the runtime path** (per `pearl_prime_audit_2026-06-06.md` §3 #7) — only the offline validator enforces ≥3. CI-side enforcement holds; runtime silently proceeds if a cell with <3 ever ships. See §14 CI guard spec + ws_runtime_variant_floor_assertion_20260606 follow-up.

### §8.6 — Named-character bestseller STORY bank coverage

Per [`pearl_prime_audit_2026-06-06.md`](../artifacts/qa/pearl_prime_audit_2026-06-06.md) §3 + [`agent6_system_size.md`](/tmp/pearl_prime_audit_2026-06-06/agent6_system_size.md) §5a:

- **1,375 named-character STORY atoms** observed across the 7 canonical engine names (shame, spiral, grief, false_alarm, overwhelm, comparison, watcher) × persona × topic — vs cap claim of 2,584 in `pool_index.py:7` (53% of the cap claim; ~1,000-atom discrepancy).
- **210 (P,T) cells × ≥3 named characters per cell = 630 minimum STORY engine variants** required for Phase A en-US per `BESTSELLER-INJECTIONS-MANDATORY-01` named-character STORY at sec 2/5/9.
- **Phase A en-US STORY bank: PASS** for 176 of 210 cells (existing engine banks deliver). The 34-cell short = the educators (7) + nyc_executives (7) + gen_z_student (3) zero-atom combos × multiple engines + midlife_women arc-blocked → Tier P1 fix via `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606`.

### §8.7 — Teacher-bank coverage

Per [`teacher_bank_audit.md`](../artifacts/audit/teacher_bank_audit.md) (2026-04-10) — confirmed by [`agent6_system_size.md`](/tmp/pearl_prime_audit_2026-06-06/agent6_system_size.md) §10:

- **13 teacher banks** under `SOURCE_OF_TRUTH/teacher_banks/` (15 dirs on disk; 2 docs + joshin / kenjin variants).
- **24 universal slot gaps** at the bank level: QUOTE = **0 atoms for 12 of 13 teachers** (ahjan-only at 9 atoms, below the 12 threshold). TEACHING = **0 for 12 of 13 teachers**.
- **Per-type total observed** ≈ STORY=280, EXERCISE=249, REFLECTION=237, COMPRESSION=235, THREAD=215, TAKEAWAY=215, PIVOT=215, PERMISSION=215, HOOK=186, SCENE=176, INTEGRATION=176, TEACHER_DOCTRINE=19 — confirms `agent6_system_size.md` correction that the cap claim "200 atoms per type per teacher × 13 teachers" overstates by ~13×.
- **Phase A teacher-bank required for Class 2 routing (QUOTE/TEACHER_DOCTRINE/PERMISSION_GRANT):** 13 teachers × 15 topics × 3 atom types × ≥3 variants = **1,755 teacher-bank atoms minimum** to back the Phase A en-US overlay path with ≥3-variant compliance.

---

## §9. Gap Matrix (§ data → [`pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](../artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv))

The full gap matrix is the canonical machine-readable evidence for §10 prioritization + §11 ownership routing. **20,803 rows** (each = one missing-or-thin cell tuple).

**Schema:**

```
persona | topic | atom_type | locale | required_variants | current_variants | gap_variants | priority_tier | owner_ws_proposed | estimated_hours | status
```

**Aggregate counts:**

| Cut | Row count | Estimated authoring hours (sum) |
|---|---:|---:|
| **Total rows** | **20,803** | **26,617.6** |
| Tier P0 (en-US persona-keyed for GOLD personas × priority topics) | 105 | 125.1 |
| Tier P1 (Phase A en-US balance) | 548 | 664.5 |
| Tier P2 (Phase B ja-JP) | 803 | 982.2 |
| Tier P3 (Phase C zh-TW + zh-CN) | 2,550 | 3,180.1 |
| Tier P4 (Phase D ko-KR + zh-HK + zh-SG) | 1,829 | 2,328.9 |
| Tier P5 (extended locales es-* / fr-FR / de-DE / it-IT / hu-HU + variant enrichment) | 14,968 | 19,336.8 |
| **en-US persona-keyed only** (HOOK/COMPRESSION/REFL/INTEG/STORY/EXERCISE) | 29 | (subset of P0+P1) |
| **en-US overlay-routed** (QUOTE/TEACHER_DOCTRINE/PERMISSION_GRANT) | 624 | (subset of P0+P1) |

**P0 atom-type cut:**

| Atom type | P0 rows |
|---|---:|
| QUOTE | 36 |
| PERMISSION_GRANT | 35 |
| TEACHER_DOCTRINE | 34 |

**P0 is entirely Class 2 overlay-routed** — the persona-keyed Class 1 types (HOOK/COMPRESSION/REFLECTION/INTEGRATION/STORY/EXERCISE) for the 6 priority personas × 6 priority topics × en-US are already at floor for the GOLD-reference combos. Tier P1 contains the persona-keyed Class 1 gaps for non-priority personas (educators 7-topic gap, nyc_executives 7-topic gap, gen_z_student 3-topic gap, midlife_women arc-block flag).

**Per-persona P0 distribution:** corporate_managers 18, first_responders 18, gen_x_sandwich 18, healthcare_rns 18, working_parents 18, gen_z_professionals 15. Total 105 (6 priority personas × 6 priority topics × 3 Class-2 types - 3 gen_z_prof skips where TEACHER_DOCTRINE persona-keyed exists per [`agent2_arcs_atoms.md`](/tmp/pearl_prime_audit_2026-06-06/agent2_arcs_atoms.md) §B).

---

## §10. Prioritization Tiers

Per the ONE-PATH-LOCKDOWN intent (aggregated from `TEMPLATE-UNIVERSAL-01` + `SPEC-739-THRESHOLD-01` + `PEARL-EDITOR-UPSTREAM-01` + `BESTSELLER-INJECTIONS-MANDATORY-01` + `CATALOG-800-PER-BRAND-01` + `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01` — see §15 + Q-Atom-ONE-PATH-SPEC-FILE-01).

| Tier | Definition | Row count | Hours | Gate semantics |
|---|---|---:|---:|---|
| **P0** | Gates Phase A en-US gold-reference book production for 6 priority personas × 6 priority topics (per Q-Atom-PRIORITY-PERSONAS-01 + Q-Atom-PRIORITY-TOPICS-01). Class 2 overlay-routed types only (QUOTE + TEACHER_DOCTRINE + PERMISSION_GRANT). Resolves via teacher_banks authoring per `QUOTE-ATOM-ROUTING-01` + `SPEC-739-VALIDATOR-AWARENESS`. | 105 | ~125 hr | HARD — production-profile catalog runs hard-reject if P0 cell missing per `PEARL-PRIME-ONE-PATH-V1` runtime fail-fast |
| **P1** | Completes Phase A en-US full breadth (all 14 personas × 15 topics). Persona-keyed Class 1 gaps (educators 7T, nyc_executives 7T, gen_z_student 3T, midlife_women arc-block) + overlay-routed for remaining 8 personas. | 548 | ~665 hr | HARD — gates non-priority persona/topic catalog launches |
| **P2** | Phase B ja-JP coverage. Locale variants of Tier P0 + P1 atoms via Pearl_Localization. | 803 | ~982 hr | HARD for ja-JP catalog launch |
| **P3** | Phase C zh-TW + zh-CN coverage. | 2,550 | ~3,180 hr | HARD for zh catalog launch |
| **P4** | Phase D ko-KR + zh-HK + zh-SG. | 1,829 | ~2,329 hr | HARD for ko + extended-CJK catalog launch |
| **P5** | Extended locales (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU) + variant enrichment (3 → 5 ceiling) for high-confidence configs. Gated on Q-Atom-LOCALE-SCOPE-01. | 14,968 | ~19,337 hr | SOFT — operator-tier decision per locale; per `CATALOG-800-PER-BRAND-01` top-5 includes 2 EU locales NOT currently authored |

**Tier-P0 priority personas (recommended; operator confirms via Q-Atom-PRIORITY-PERSONAS-01):** `gen_z_professionals` (GOLD reference per memory) · `corporate_managers` · `working_parents` · `first_responders` · `healthcare_rns` · `gen_x_sandwich`.

**Tier-P0 priority topics (recommended; operator confirms via Q-Atom-PRIORITY-TOPICS-01):** `anxiety` · `overthinking` · `burnout` · `boundaries` · `self_worth` · `depression`.

---

## §11. Authoring-Ownership Matrix

Per `PEARL-EDITOR-UPSTREAM-01` + `EXERCISE-BANK-RESOLUTION-01` + `QUOTE-ATOM-ROUTING-01`:

| Atom type | Owner | Target path | Phase A ws |
|---|---|---|---|
| HOOK | Pearl_Writer | `atoms/<persona>/<topic>/HOOK/CANONICAL.txt` | `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606` |
| COMPRESSION | Pearl_Writer | `atoms/<persona>/<topic>/COMPRESSION/CANONICAL.txt` | same |
| REFLECTION | Pearl_Writer | `atoms/<persona>/<topic>/REFLECTION/CANONICAL.txt` | same |
| INTEGRATION | Pearl_Writer | `atoms/<persona>/<topic>/INTEGRATION/CANONICAL.txt` | same |
| STORY (engine bank) | Pearl_Writer | `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` | same |
| STORY (named-character bestseller) | Pearl_Writer + Pearl_Editor co-author | `story_atoms/<persona>/anchored/<topic>/<engine>/<arc_position>/micro/v*.txt` | extends `ws_story_cell_authoring_20260425` (Phase 2+) |
| EXERCISE | Pearl_Editor | `atoms/<persona>/<topic>/EXERCISE/CANONICAL.txt` + `teacher_banks/<teacher>/approved_atoms/EXERCISE/*.yaml` + practice_library fallthrough | `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` |
| QUOTE | Pearl_Editor | `teacher_banks/<teacher>/approved_atoms/QUOTE/*.yaml` (NOT persona-keyed per `QUOTE-ATOM-ROUTING-01`) | `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` |
| TEACHER_DOCTRINE | Pearl_Editor | `teacher_banks/<teacher>/doctrine/*.txt` + `teacher_banks/<teacher>/approved_atoms/TEACHING/*.yaml` | same |
| PERMISSION_GRANT | Pearl_Editor | `teacher_banks/<teacher>/approved_atoms/PERMISSION/*.yaml` (canonical runtime location) | same |
| **All locale variants** | Pearl_Localization | `atoms/<persona>/<topic>/<atom_type>/locales/<locale>/*.txt` | `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606` (Phase B); P3/P4 ws's spawned after Phase A lands |
| **CI guard** | Pearl_Dev | `scripts/ci/check_atom_100pct_coverage.py` + `.github/workflows/atom_100pct_coverage.yml` | `ws_pearl_dev_atom_100pct_ci_guard_20260606` |

---

## §12. Open Operator Questions (Q-Atom-*)

> All defaults are **recommendations** — operator decides; this SSOT does NOT pre-resolve.

**Q-Atom-PERSONA-SCOPE-01** — Persona enumeration. **Options:** (a) keep all 14 + backfill all to 100% [**RECOMMEND** if launch is months away — preserves optionality]; (b) retire midlife_women + educators + nyc_executives (under-developed) + concentrate authoring on top 8; (c) staged — top 8 to 100% first, near-empty backfilled in Phase 2.

**Q-Atom-LOCALE-SCOPE-01** — Locale ceiling. **Options:** (a) ALL 13 official locales per `locale_registry.yaml`; (b) top-3 (en-US + ja-JP + zh-TW) per `AMENDMENT-2026-06-04.2` cascade recommended-default; (c) en-US only for Phase A; locales follow [**RECOMMEND** for SSOT acceptance criteria — anchor Phase A on en-US]; (d) add de-DE + fr-FR per audit A6 EU gap (operator vetoes `CATALOG-800-PER-BRAND-01` top-5 math) — multi-quarter cost.

**Q-Atom-LOCALE-PHASE-01** — Locale sequencing. **Options:** (a) en-US → ja-JP → zh-TW → zh-CN → ko-KR [**RECOMMEND** market priority]; (b) en-US + ja-JP parallel → zh-TW + zh-CN parallel → ko-KR; (c) operator-custom.

**Q-Atom-VARIANT-CEILING-01** — Variant ceiling. **Options:** (a) ≥3 floor + ≤5 ceiling per current `SPEC-739-THRESHOLD-01` + ONE-PATH-LOCKDOWN [**RECOMMEND**]; (b) ≥5 floor (raise the bar); (c) ≥3 floor + ≤7 ceiling.

**Q-Atom-PERSONA-KEYED-FALLBACK-01** — For Tier P1 personas without persona-keyed TEACHER_DOCTRINE yet — (a) BLOCK catalog runs until backfilled [**RECOMMEND** per ONE-PATH runtime fail-fast]; (b) allow generic teacher_banks/doctrine fallback during transition; (c) author placeholder persona-keyed atoms (lower-quality stopgap) + flag for revision.

**Q-Atom-STORY-BANK-EXPANSION-01** — Named-character bestseller bank. **Options:** (a) keep current ~1,375 atoms + expand only for new P×T cells; (b) expand to ≥3 named characters per P×T cell (target ≈ 630 STORY atoms minimum) [**RECOMMEND**]; (c) expand to ≥5 named characters per cell.

**Q-Atom-TEACHER-BANK-SCOPE-01** — Teacher-bank coverage (13 teachers × 15 topics × ~4 atom types). **Options:** (a) all 13 teachers × all 15 topics complete [**RECOMMEND**]; (b) staged per teacher priority; (c) reduce teacher roster to top 8.

**Q-Atom-PRIORITY-PERSONAS-01** — Tier P0 priority personas (5-6 to launch Phase A en-US). **Recommend:** gen_z_professionals (GOLD) + corporate_managers + working_parents + first_responders + healthcare_rns + gen_x_sandwich. Operator confirms.

**Q-Atom-PRIORITY-TOPICS-01** — Tier P0 priority topics (5-6 to launch Phase A en-US). **Recommend:** anxiety + overthinking + burnout + boundaries + self_worth + depression. Operator confirms.

**Q-Atom-EXERCISE-BANK-RESOLUTION-01** — Per `EXERCISE-BANK-RESOLUTION-01` Option 1 (strict-canonical for production) — confirm strict-canonical exercise atoms required for Tier P0 cells; gratitude_practices_v1 promotion to PRODUCTION_READY gated on SSOT?

**Q-Atom-MASTER-ARC-INTERACTION-01** — Per `pearl_prime_audit_2026-06-06.md` axis A2 — 449/531 master arcs declare `chapter_count: 20`. Atom authoring is per persona×topic per ONE-PATH compression strategy; arc shape does not change atom requirements. **Confirm: atom requirements per ONE-PATH are independent of arc `chapter_count`.**

**Q-Atom-CI-GUARD-SEVERITY-01** — `scripts/ci/check_atom_100pct_coverage.py` (§14). **Options:** (a) HARD FAIL on missing Tier P0 cells under production-profile catalog runs [**RECOMMEND** per ONE-PATH runtime fail-fast semantics]; (b) warn-only; (c) operator-tier-selectable per phase.

**Q-Atom-SSOT-UPDATE-CADENCE-01** — Per §13 update protocol. **Options:** (a) every atom-authoring ws PR auto-updates §9 gap matrix [**RECOMMEND**]; (b) weekly batch update; (c) per-tier-completion update only.

**Q-Atom-DE-DE-FR-FR-01** — de-DE / fr-FR locale gap. **Options:** (a) defer per `AMENDMENT-2026-06-04.2` recommended demote-to-top-3 [**RECOMMEND**]; (b) backfill (multi-quarter; high cost); (c) skip permanently — operator confirms.

**Q-Atom-ONE-PATH-SPEC-FILE-01** *(new — surfaced by discovery + reconciled)* — `docs/specs/PEARL_PRIME_ONE_PATH_LOCKDOWN_V1_SPEC.md` exists at `agent/pearl-architect-pearl-prime-one-path-lockdown-v1-20260606` (in this PR's parent merge lineage); cap entry `PEARL-PRIME-ONE-PATH-V1-01` status = **PROPOSAL** awaiting operator answers to 12 Q-OP-* (see `PEARL_ARCHITECT_STATE.md:2427-2490`). This SSOT subordinates to the ONE-PATH-V1-01 spec for the persona-keyed atom-type catalog (D8 = 16 slots) and operationalizes its Phase 3 content-backfill phase as the gap matrix + tier ordering. **Options:** (a) wait for ONE-PATH-V1-01 ratification (operator answers Q-OP-* on its PR thread) then ratify this SSOT in the same cycle [**RECOMMEND** — preserves anti-drift]; (b) ratify this SSOT independently — Phase A scope-of-work is well-defined regardless of ONE-PATH ratification; (c) operator-direct on sequencing.

**Q-Atom-DIRECTIVE-9-VS-CAP-16-01** *(new — surfaced by discovery)* — The directive's "9 atom types per cell" framing is a SUBSET of `PEARL-PRIME-ONE-PATH-V1-01` D8's "16 persona-keyed slot-type dirs per persona×topic" canonical (adds SCENE / PIVOT / PERMISSION / TAKEAWAY / THREAD / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK to the directive's 9). Discovery shows the 7 extra slot-types are largely covered already (PIVOT=1,757 / PERMISSION=1,760 / TAKEAWAY=1,760 / THREAD=1,749 / SCENE=609 / TEACHER_DOCTRINE_INTRO=10 / ANGLE_DEFINITION + ANGLE_CALLBACK observed in atoms/ tree). **Options:** (a) accept the §3 routing-class split as SSOT canonical — 6 persona-keyed + 3 overlay-routed = the directive's 9; track the other 7 slot-types under cap entry ONE-PATH-V1-01 D8 alone [**RECOMMEND**] — preserves directive scope without contradicting cap entry; (b) expand SSOT scope to all 16 per cap D8 — gap matrix expands 1.78× to ~36,990 rows; ~47,400 estimated hours; (c) shrink cap D8 to the directive's 9 (architectural change requiring separate Pearl_Architect cap-amendment ws).

**Q-Atom-LEGACY-ATOM-TYPES-01** *(new — surfaced by discovery)* — Per ONE-PATH-V1-01 D8: 16 persona-keyed slot-type dirs are canonical. The 7 dirs beyond the directive's 9 (SCENE / PIVOT / PERMISSION / TAKEAWAY / THREAD / TEACHER_DOCTRINE_INTRO / ANGLE_DEFINITION / ANGLE_CALLBACK) appear well-populated in discovery scans (PIVOT=1,757, PERMISSION=1,760, TAKEAWAY=1,760, THREAD=1,749, SCENE=609, TEACHER_DOCTRINE_INTRO=10). **Options:** (a) accept Q-Atom-DIRECTIVE-9-VS-CAP-16-01 (a) and track these 7 under ONE-PATH-V1-01 alone [**RECOMMEND** — minimizes SSOT scope-creep]; (b) expand SSOT scope to all 16 — pair-vote with Q-Atom-DIRECTIVE-9-VS-CAP-16-01 (b); (c) audit each of the 7 for runtime usage + decide individually.

**Total Q-Atom-***: **16** (above the ≥12 target).

---

### AMENDMENT-2026-06-11 cross-refs (3 RESOLVED via [PR #1486](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486) `EXERCISE-COMPONENT-SCHEMA-LIFT-01`):

- **Q-Atom-DRIFT-A-LIFT-01** (schema strategy: extend blocks OR parallel components) → **RESOLVED via PR #1486 (b)**: parallel `components` field added at v2; legacy `blocks` retained for back-compat.
- **Q-Atom-DRIFT-B-INGEST-01** (ab_tady_37 ingest enablement) → **RESOLVED via [`ws_pearl_dev_practice_ingest_components_lift_20260610`](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv)** (a): include in next ingest pass; 39 items → 311-row store post-merge.
- **Q-Atom-PER-SOURCE-LEAN-FULL-01** (format_registry picker) → **RESOLVED via [`config/practice/selection_rules.yaml`](../config/practice/selection_rules.yaml) `component_variant_by_format`**: full for deep_book_4h + extended_book_2h + deep_book_6h; lean for the 17 other runtime formats.

### AMENDMENT-2026-06-11 NEW Q-Atom-* (4 questions):

- **Q-Atom-SLOT-07-PRIORITY-01** — slot_07 supply backfill priority. **Options:** (a) breath_regulation first (39 ab_tady items already land here post-ingest; max coverage / min new authoring) [**RECOMMEND**]; (b) grounding_orientation; (c) body_awareness_scan; (d) operator-custom priority.
- **Q-Atom-AUDIT-PASS-THRESHOLD-01** — Pearl_Editor preservation audit pass threshold. **Options:** (a) ≥99% items zero-loss [**RECOMMEND**]; (b) 100% strict; (c) ≥95% with explicit per-item gap report.
- **Q-Atom-INCLUDE-PEARL-PM-ITER-3-01** — Include Pearl_PM Phase A tracker iter 3 update in this AMENDMENT PR? **Options:** (a) YES + add deliverable #4; (b) NO + defer to Pearl_PM's own iter session [**RECOMMEND** — preserves Pearl_PM ownership boundary].
- **Q-Atom-INCLUDE-SLOT-07-BACKFILL-WS-01** — Include optional slot_07 supply backfill ws row in this PR? **Options:** (a) YES — captures the future-track surface so it doesn't get lost [**RECOMMEND**]; (b) NO + defer.

**Total Q-Atom-* (post-AMENDMENT-2026-06-11):** 16 + 3 RESOLVED + 4 new = **20**.

---

## §13. SSOT Update Protocol

**Every child atom-authoring ws PR must update §9 gap matrix in place:**

1. ws PR authors atoms for N cells at Tier T.
2. Same PR re-runs `python3 scripts/build_atom_gap_matrix.py > artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` (script lives at `scripts/qa/` post Pearl_Dev ws — see §14).
3. PR diff shows N rows removed from §9 TSV (the cells now ≥3 variants).
4. CI guard (`scripts/ci/check_atom_100pct_coverage.py`) cross-validates §9 against `atoms/` tree; refuses PR merge if §9 and reality diverge.

**Per Q-Atom-SSOT-UPDATE-CADENCE-01, default = per-PR auto-update.**

---

## §14. CI Guard Spec — `scripts/ci/check_atom_100pct_coverage.py`

**Authored by:** Pearl_Dev under `ws_pearl_dev_atom_100pct_ci_guard_20260606`. This SSOT specs the contract; Pearl_Dev implements.

**Inputs:**

- `atoms/` tree (read-only)
- `SOURCE_OF_TRUTH/teacher_banks/` (read-only)
- `config/localization/locale_registry.yaml`
- `registry/*.yaml`
- This SSOT (§2 dimensions; §3 atom catalog; §10 priority tiers)
- `artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` (the §9 baseline)

**Behavior:**

1. Re-compute the gap matrix from `atoms/` + teacher_banks tree.
2. Diff against the committed §9 TSV.
3. **Severity per Q-Atom-CI-GUARD-SEVERITY-01:**
   - HARD FAIL: missing Tier P0 cell under production-profile catalog runs (the runtime fail-fast).
   - WARN: missing Tier P1 cell.
   - INFO: missing Tier P2+ cell.
4. **Output:**
   - GitHub-Actions summary: per-tier deltas (cells closed, cells still open).
   - Step output: PASS / WARN / FAIL.
   - Artifact: re-computed gap matrix TSV for diff.

**Schedule:** nightly on `main`; on-demand via workflow_dispatch; required check on PRs touching `atoms/**` or `SOURCE_OF_TRUTH/teacher_banks/**`.

**Gate:** Phase A launch (per `CATALOG-800-PER-BRAND-01`) requires Tier P0 gap count = 0 + Tier P1 gap count = 0.

---

## §15. Cross-References + Supersession

This SSOT supersedes every prior **partial-coverage** atom audit. The originals are retained per [`AGENT_FILE_PERSISTENCE_PROTOCOL.md`](./AGENT_FILE_PERSISTENCE_PROTOCOL.md) (no deletion); each gets a DEPRECATED-cross-link annotation:

| Prior doc | Status post-this-SSOT | Cross-link to SSOT §  |
|---|---|---|
| [`artifacts/audit/persona_atom_audit.md`](../artifacts/audit/persona_atom_audit.md) | DEPRECATED — superseded by SSOT §8.1 + §8.3 | §8.1 (per-persona table); §8.3 (9-type completeness) |
| [`artifacts/audit/teacher_bank_audit.md`](../artifacts/audit/teacher_bank_audit.md) | DEPRECATED — superseded by SSOT §8.7 | §8.7 |
| [`artifacts/audit/registry_coverage_vs_catalog.md`](../artifacts/audit/registry_coverage_vs_catalog.md) | DEPRECATED — superseded by SSOT §5 + §8 | §5 (topic enumeration); §8 (current coverage) |
| [`artifacts/audit/P1_HEALTH_REPORT_2026_04_10.md`](../artifacts/audit/P1_HEALTH_REPORT_2026_04_10.md) | LINEAGE — historical 2026-04-10 snapshot; persona-atom + teacher-bank lines superseded by SSOT §8.1 + §8.7 | §8.1, §8.7 |
| [`artifacts/qa/pearl_prime_audit_2026-06-06.md`](../artifacts/qa/pearl_prime_audit_2026-06-06.md) | LINEAGE — synthesis doc; axes A2 + A6 (atom + system size) findings folded into SSOT §8 + §10 | §8 + §10 |

**Cap entries cross-linked (existing + new):**

- New: `ATOM-100PCT-COVERAGE-SSOT-V1-01` (this SSOT)
- Aggregated: `TEMPLATE-UNIVERSAL-01` ([`PEARL_ARCHITECT_STATE.md:576`](./PEARL_ARCHITECT_STATE.md)), `SPEC-739-THRESHOLD-01` ([`:308`](./PEARL_ARCHITECT_STATE.md)), `PEARL-EDITOR-UPSTREAM-01`, `QUOTE-ATOM-ROUTING-01` ([`:708`](./PEARL_ARCHITECT_STATE.md)), `BESTSELLER-INJECTIONS-MANDATORY-01`, `EXERCISE-BANK-RESOLUTION-01`, `TEACHER-POOL-SEMANTICS-01`, `HOOK-SCENE-FIRST-01`, `CATALOG-800-PER-BRAND-01`, `AUTO-PLAN-SSOT-01-AMENDMENT`, `COHESIVE-FLOW-PATH-DEFAULT-SPINE-01`, `SPEC-739-VALIDATOR-AWARENESS`

**Spec files cross-linked:**

- [`specs/PHOENIX_V4_5_WRITER_SPEC.md`](../specs/PHOENIX_V4_5_WRITER_SPEC.md) §4 (atom-type canonical)
- [`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`](./PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md)
- [`docs/PEARL_EDITOR_BRIEF.md`](./PEARL_EDITOR_BRIEF.md)
- [`docs/SOURCE_BANK_REPAIR_DEV_SPEC.md`](./SOURCE_BANK_REPAIR_DEV_SPEC.md)
- [`specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md`](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md)

**Coordination cross-links:**

- [`artifacts/coordination/ACTIVE_PROJECTS.tsv`](../artifacts/coordination/ACTIVE_PROJECTS.tsv) — `PRJ-PEARL-PRIME-FEATURE-UTILIZATION` + `proj_pearl_prime_bestseller_rebase_20260425`
- [`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv) — 4 new ws rows; `ws_atom_gap_fill_20260410` marked SUPERSEDED
- [`artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) — atoms + teacher_mode + translation rows

---

## §16. Acceptance Criteria (when is 100% achieved?)

**Per priority tier:**

| Phase | Tier completion | Acceptance condition |
|---|---|---|
| Phase A en-US gold-reference launch | P0 cleared | 105 P0 cells filled (priority personas × priority topics × Class 2 overlay backing); CI guard PASS on Tier P0 |
| Phase A en-US full breadth | P0 + P1 cleared | 653 cells filled; §8.1 reaches 1,260/1,260 persona-keyed + §8.7 reaches 1,755/1,755 teacher-bank-backed; CI guard PASS on P0+P1; `CATALOG-800-PER-BRAND-01` en-US row unblocked |
| Phase B ja-JP | P2 cleared | 803 ja-JP cells at ≥3 variants |
| Phase C zh-TW + zh-CN | P3 cleared | 2,550 cells |
| Phase D ko-KR + zh-HK + zh-SG | P4 cleared | 1,829 cells |
| Phase E extended locales + variant enrichment | P5 cleared (gated on Q-Atom-LOCALE-SCOPE-01) | 14,968 cells |
| **TRUE 100% (matrix-complete)** | All tiers cleared | gap-matrix row count = 0; CI guard PASS at all severities |

**Operator-tier launch gates** per `CATALOG-800-PER-BRAND-01`:

- en-US catalog launch: requires Phase A complete.
- ja-JP catalog launch: requires Phase A + B complete.
- Full 5-locale `CATALOG-800-PER-BRAND-01` top-5 math: requires Phase A + B + C + D (ko-KR) complete; the audit-A6-flagged EU gap (de-DE + fr-FR) remains open per Q-Atom-DE-DE-FR-FR-01 + Q-Atom-LOCALE-SCOPE-01.

---

---

## §17. AMENDMENT-2026-06-11 — EXERCISE schema lift cross-link

### §17.1 Trigger

[PR #1486](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/1486) (`EXERCISE-COMPONENT-SCHEMA-LIFT-01`, commit `771e714e8`) landed in parallel to this SSOT (PR #1485) closing two real drifts in the EXERCISE backstop path. The two PRs are orthogonal subsystems — atom coverage (this SSOT) and practice library schema (PR #1486) — but the AMENDMENT cross-links both so operator reading the SSOT sees the schema-lift context, the cap-entry-level acceptance checklist is explicit, and Pearl_Editor preservation audit becomes a tracked workstream rather than informal NEXT_ACTION.

### §17.2 PR #1486 summary

- **5 files changed:** `specs/PRACTICE_ITEM_SCHEMA.md` (v1 → v2; parallel `components` field §2.5); `config/practice/validation.yaml` (v1 → v2; `components_schema` block); `config/practice/selection_rules.yaml` (v1 → v2; `component_variant_by_format`); `docs/PEARL_ARCHITECT_STATE.md` (APPEND cap entry `EXERCISE-COMPONENT-SCHEMA-LIFT-01`); `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (APPEND 2 ws rows).
- **2 Pearl_Dev ws's queued** (status=proposed; gated on PR #1486 merge): `ws_pearl_dev_practice_ingest_components_lift_20260610` (items 2+3: ingest fix + ab_tady_37 source branch) + `ws_pearl_dev_renderer_practice_components_consume_20260610` (item 4: renderer reads structured components; HARD-gated on ingest ws landing first).
- **Cap entry status:** ratified (Pearl_Architect cap layer; Pearl_Dev impl routed).

### §17.3 Acceptance criteria checklist (paired with §17.6 below)

When the 2 Pearl_Dev ws PRs from PR #1486 land, operator + reviewer apply the [A1-A6 checklist](#176-acceptance-criteria-verbatim) below as a deterministic merge gate. No A1-A6 row checked → do NOT merge.

### §17.4 Pearl_Editor preservation audit ws

`ws_pearl_editor_exercise_preservation_audit_20260611` (this AMENDMENT — status=proposed). Fires AFTER both Pearl_Dev ws's merge. Per-item diff inbox SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json against post-re-ingest `practice_items.jsonl` row content. Pass threshold = ≥99% items zero-loss per Q-Atom-AUDIT-PASS-THRESHOLD-01 default (a). Output: `artifacts/qa/exercise_preservation_audit_<UTC-YYYY-MM-DD>.{md,tsv}`. Verifies A1 + A2 + A3 + A4 + A6 of §17.6.

### §17.5 slot_07_PRACTICE supply backfill (follow-up — optional ws this PR)

PR #1486's schema lift unblocks the slot_07_PRACTICE supply gap (`config/practice/selection_rules.yaml` lists 11 content_types; current store carries 0 items for most; ab_tady_37's 39 items map to `breath_regulation` namespacing). Per Q-Atom-INCLUDE-SLOT-07-BACKFILL-WS-01 default (a), this AMENDMENT also appends `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` (status=proposed; gated on PR #1486 + 2 Pearl_Dev ws's merged). Target: ≥8 items per content_type × 11 types = 88 items minimum; staged authoring per Q-Atom-SLOT-07-PRIORITY-01 priority order.

### §17.6 Acceptance criteria (verbatim — also in cap entry)

**A1.** Schema accepts v2 components without losing v1 data (post-ingest spot-check 5 items diff matches inbox source files).

**A2.** Re-ingest produces **311 rows total (272 library_34 + 39 ab_tady_37)** vs current 272.

**A3.** Zero content loss verifiable via Pearl_Editor preservation audit ws — every inbox component field present in store row for **≥99% of items**; flagged items <1% with explicit per-item evidence.

**A4.** Renderer reads structured components for at least 1 production-profile smoke combo (`gen_z_professionals × anxiety × ahjan × deep_book_4h`) and produces **visible aha + integration text** in rendered output.

**A5.** `component_variant_by_format` selects **full** for `{deep_book_4h, extended_book_2h, deep_book_6h}`; **lean** for the 17 other runtime formats — confirmed via per-format dry-run.

**A6.** ab_tady_37 items render under slot_07_PRACTICE when bestseller-grade smoke targets a registry with slot_07 active (post-merge of `ws_pearl_editor_slot_07_practice_supply_backfill_20260611`).

### §17.7 New ws cross-refs

- `ws_pearl_editor_exercise_preservation_audit_20260611` — Pearl_Editor; verifies A1-A6 above; status=proposed.
- `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` — Pearl_Editor + Pearl_Writer; backfill 11 slot_07 content_types per Q-Atom-SLOT-07-PRIORITY-01 priority; status=proposed.

Both rows appended in this AMENDMENT's `ACTIVE_WORKSTREAMS.tsv` commit.

---

*End of SSOT v1 + AMENDMENT-2026-06-11. Update protocol: §13. Cap entries: `ATOM-100PCT-COVERAGE-SSOT-V1-01` + `EXERCISE-COMPONENT-SCHEMA-LIFT-01` (cross-linked). Operator answers Q-Atom-* → child ws's spawn per §10 + §11 + §17 → §9 gap matrix shrinks per §13 + EXERCISE component shape preserved per §17.6 A1-A6 → §16 acceptance gates Phase A launch.*

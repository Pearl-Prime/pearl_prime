# devotion_path reassembly — NEW BEST WAY proof wave (2026-06-17)

**Agent:** Pearl_Prime · **Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**Brand:** Open Vessel Press / "Waystream Sanctuary" · **Byline:** Sai Maa
**Build base:** clean `git archive origin/main` snapshot @ **bf69977a38** (cwd inside SNAP)
**Mode:** `run_pipeline --pipeline-mode spine` · **Profiles:** draft (reliable emit) + production (attempted) · **Determinism:** `--seed 4242`
**No paid API. No Pearl Star / FLUX / Qwen (GPU install in flight). PIL covers only.**

This wave SUPERSEDES the old #1676 W4 wave-1 assembly, which was built on the pre-fix
SHA **29c3fd76bc** (= #1677, before #1682 re-point and before the #1683 gate-hardening).

---

## 0. Headline — the upgrade is PROVEN on an identical cell

Same cell (`burnout/overwhelm/corporate_managers`), same seed, built on OLD code vs NEW code:

| Gate | OLD code (29c3fd76bc — what #1676 ran) | NEW code (bf69977a38) |
|---|---|---|
| **scene_anchor_density** | **FAIL** — chapter 4: phrase `"you are allowed to"` ×7 > cap 3 | **PASS** — #1670/#1683 reducer trimmed to ≤cap |
| chapter_flow | PASS | PASS |
| book_pass (overall) | PASS | PASS |
| angle_journey_coherence | PASS (angle `INVISIBLE_COST` already resolved for burnout) | PASS |
| book_quality | Hold (repeated-phrase density) | Hold (repeated-phrase density) |

**The decisive flip is `scene_anchor_density` FAIL → PASS.** In #1676 this gate was **0/3 PASS**
(every assembled book FAILED it) and was the reason all 3 buildable books landed Hold/Reject. The
#1670 cap + #1683 generalized reducer now clear it on every book in this wave.

### Honest scoping of the other claimed fixes
- **angle_journey (#1683 slug→concept-ID):** load-bearing for cells whose catalog ANGLE slug is NOT
  a registry key (e.g. courage `false_alarm`). For **burnout** the angle (`INVISIBLE_COST`) already
  resolved on the old code, so burnout's book_pass was already PASS — the #1683 angle fix is real but
  is **not** what flips burnout. It would be demonstrable on courage/imposter, which are atom-blocked
  (see §3), so it is verified by code-presence (`_resolve_angle_journey_id`, run_pipeline.py:757) +
  the report's resolved `angle_id`, not by an end-to-end courage build.
- **chapter_flow all-chapters (#1674/#1683), book_quality A2 (#1673):** present on the snapshot; flow
  passes on all 7 burnout cells. book_quality still lands **Hold** (advisory phrase-density) on every
  cell — this axis did not regress and was not the #1676 blocker.

---

## 1. Wave design (10 cells)

Spine prose varies by **(topic, persona)**; the **engine axis is prose-invariant** in the current
composer — the main `enrichment_per_section` path pulls atoms from `atoms/{persona}/{topic}/{SLOT}/`
(NOT engine-keyed); only the STORY-schedule slice (idx 2/5/9) reads the engine pool. This is the
documented **F-COHERENCE** defect (#1589/#1590) that the reconciliation spec §6/§8 gates W4 behind.
Therefore cells span (topic, persona) for genuine distinctness; the corporate_managers burnout trio
additionally spans engines for a 1:1 row-compare against #1676's 3 rows.

---

## 2. Results — 8/10 assembled, every assembled book clears the #1676-failing gates

| cell | persona | topic | engine | built | words | flow | ei_v2 | craft | book_pass | angle_journey | scene_density | book_quality |
|---|---|---|---|---|--:|---|--:|--:|---|---|---|---|
| burnout/overwhelm | corporate_managers | burnout | overwhelm | yes | 19942 | PASS | 0.65 | 0.52 | **PASS** | PASS | **PASS** | Hold |
| burnout/watcher | corporate_managers | burnout | watcher | yes | 19942 | PASS | 0.65 | 0.52 | **PASS** | PASS | **PASS** | Hold |
| burnout/grief | corporate_managers | burnout | grief | yes | 19942 | PASS | 0.65 | 0.52 | **PASS** | PASS | **PASS** | Hold |
| burnout/overwhelm | healthcare_rns | burnout | overwhelm | yes | 22000 | PASS | 0.61 | 0.56 | **PASS** | PASS | **PASS** | Hold |
| burnout/overwhelm | working_parents | burnout | overwhelm | yes | 19804 | PASS | 0.66 | 0.57 | **PASS** | PASS | **PASS** | Hold |
| burnout/grief | gen_z_professionals | burnout | grief | yes | 22000 | PASS | 0.66 | 0.55 | **PASS** | PASS | PASS(clean) | Hold |
| burnout/watcher | first_responders | burnout | watcher | yes | 18455 | PASS | 0.65 | 0.53 | **PASS** | PASS | **PASS** | Hold |
| imposter/shame | gen_z_professionals | imposter_syndrome | shame | yes | 19430 | **FAIL** | 0.64 | 0.60 | **PASS** | PASS | **PASS** | Reject |
| courage/false_alarm | corporate_managers | courage | false_alarm | **BLOCKED** | — | — | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |
| imposter/shame | corporate_managers | imposter_syndrome | shame | **BLOCKED** | — | — | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |

`PASS(reduced)` = the #1670 reducer trimmed over-cap phrases; `PASS(clean)` = no trim needed.
The 6 cross-persona burnout/imposter books have **distinct manuscripts** (distinct md5 + word counts
17.4k–22k); the corporate_managers burnout trio is byte-identical across engines (engine-invariance).

### vs #1676 (before → after)
- **#1676:** 3/8 assembled; **scene-anchor-density 0/3 PASS**; **0/3 ship-clean** (2 Hold, 1 Reject); 5/8 blocked (TEACHER_DOCTRINE).
- **This wave:** 8/10 assembled; **scene-anchor-density 8/8 PASS**; **book_pass 8/8 PASS**, **angle_journey 8/8 PASS**; book_quality 7× Hold / 1× Reject (imposter). 2/10 blocked (same TEACHER_DOCTRINE lane).
- **First buildable imposter_syndrome cell ever** (#1676 built 0/2 imposter). It clears book_pass+angle_journey+scene_density but still trips chapter_flow (`CHOPPY_SECTION_JUMPS`, ch 5+9) and lands book_quality Reject — a genuine residual in the imposter cohesion lane, not a regression.

### Production-profile attempt (B2 frontier)
`--quality-profile production` (gates **hard/blocking**) on `burnout/overwhelm/corporate_managers`:
**EMITTED a full 19942-word manuscript** with `quality_gate_failures: []` — chapter_flow PASS,
book_pass PASS, ei_v2 0.65 PASS, craft PASS; only book_quality Hold (advisory). The spec's B2
"production emits no manuscript / gates HARD_FAIL" blocker **appears cleared for the buildable burnout
surface** by these gate fixes. (Courage/imposter still atom-block upstream of gates regardless of profile.)

---

## 3. The persistent blocker (atom-bank lane — NOT a gate defect, NOT in Pearl_Prime scope)

`courage` (0/11 personas) and `imposter_syndrome` (1/11: only gen_z_professionals) lack
`TEACHER_DOCTRINE` atoms → hard `EnrichmentGapError`. This is the **identical** blocker that stopped
5/8 of #1676's cells, it is the "TEACHER_DOCTRINE ahjan-only" gap, and the gate fixes (#1670/#1673/
#1674/#1683) do **not** touch it (correctly — different lane). Reconciliation spec §8 tracks it as
the W2 atom lane.

**TEACHER_DOCTRINE coverage (buildable-now surface):** burnout 6/11 · courage 0/11 · imposter 1/11.

---

## 4. Artifacts produced

- **Manuscripts:** 8 `book.txt` under `artifacts/wave_proof/draft/<cell>/` (+ `prod_burnout/book.txt`).
- **EPUBs:** 8 KDP-ready under `artifacts/wave_proof/epubs/` — **validate ✅ all checks PASS** (1600×2560
  cover embedded, spine_length 3). (#1676's EPUBs failed only on missing cover; these pass.)
- **Covers (FREE/local PIL only):**
  - **4 REAL** imposter_syndrome type-dominant covers — `covers/real_pil_imposter/`.
  - **4 PIL placeholders** for burnout/courage (image-bearing/FLUX genres) — `covers/placeholder_flux_pending/`,
    with a visible "FLUX PENDING" imagery patch. **FLUX NOT RUN** (Pearl Star GPU off-limits).
- **Per-book gate reports:** `chapter_flow_report.json`, `book_pass_report.json`, `book_quality_report.json`,
  `ei_v2_report.json`, `quality_summary.json`, `scene_anchor_density_report.json` per cell.
- **FLUX handoff:** `covers/FLUX_QUEUE_HANDOFF.md`.

---

## 5. Full-catalog reassembly coverage + scaled job-queue handoff

- **Total legal cells:** **85** (per reconciliation spec; confirmed 85 plans on disk).
- **Assembled this bounded wave:** **8** distinct manuscripts + EPUBs (proof slice).
- **Buildable TODAY (TEACHER_DOCTRINE-backed):** ~**20 cells** = burnout (6 personas × 3 engines = 18) +
  imposter (gen_z_professionals × 2 engines = 2). Engine-invariance means ~6+1 = **7 genuinely-distinct
  burnout/imposter manuscripts** are reachable now; the rest are engine relabels until F-COHERENCE lands.
- **Remaining ~65 cells = SCALED job-queue run**, gated on:
  1. **TEACHER_DOCTRINE atoms** for courage (0/11) + imposter (10/11 missing) — atom-bank lane (W2).
  2. **F-COHERENCE** (#1589/#1590) so the **engine axis actually differentiates prose** (today it does not)
     and SCENE atoms stop emitting residual mid-sentence injection artifacts.
  3. **FLUX covers** (burnout 33 + courage 30 = 63 covers) once Pearl Star GPU install lands — see
     `covers/FLUX_QUEUE_HANDOFF.md`. imposter (22) stays PIL/free.

**Recommendation:** the scaled 85-cell run goes through the post-install job-queue, NOT a hand-driven
session. This bounded wave proves the gate-level upgrade; the scale-up is gated on the two atom/coherence
lanes above + the FLUX tranche.

---

## 6. Recommendation on #1676

Close **#1676** as **superseded** by this wave (do not merge it). It was built pre-#1683 with
scene-anchor-density failing on every book; this wave reproduces its slice on the fixed code and
clears that gate. (Flagged for the operator — this session does not close PRs.)

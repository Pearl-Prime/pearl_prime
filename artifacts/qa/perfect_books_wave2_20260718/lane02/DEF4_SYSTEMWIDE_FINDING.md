# C4 finding: `registry/{topic}.yaml` is single-persona-authored catalog-wide — DEF4 hard-stops nearly every non-matching persona in production

**Date:** 2026-07-18 (run 2026-07-19 local)
**Agent:** Pearl_Editor lane 02
**Severity:** HIGH — catalog-wide, not scoped to the 3 lane-02 cells
**Status:** ROOT-CAUSED with live-render evidence; NOT fixed in this lane (see "Why not fixed here")

## What was found

`registry/{topic}.yaml` (the section-registry stacking layer consumed by
`phoenix_v4/planning/enrichment_select.py::_registry_type_lists` /
`_extra_registry_variant_bodies` / depth-registry-variant paths) is **not**
persona-neutral. Each topic's registry file is authored end-to-end for **one single
persona label**, applied via `metadata.persona` on every section (90 sections: 12
chapters × ~7–10 sections/chapter):

```
registry/adhd_focus.yaml   {'corporate_managers': 90}
registry/anxiety.yaml      {'Gen Z': 90}
registry/boundaries.yaml   {'Gen Z': 90}
registry/burnout.yaml      {'Gen Z': 90}     <- the topic all 3 lane-02 cells use
registry/compassion_fatigue.yaml {'Gen Z': 90}
registry/courage.yaml      {'Gen Z': 90}
registry/depression.yaml   {'Gen Z': 90}
registry/financial_anxiety.yaml {'Gen Z': 90}
registry/financial_stress.yaml {'Gen Z': 90}
registry/grief.yaml        {'Gen Z': 90}
registry/imposter_syndrome.yaml {'Gen Z': 90}
registry/mindfulness.yaml  {'corporate_managers': 90}
registry/overthinking.yaml {'Gen Z': 90}
registry/self_worth.yaml   {'Gen Z': 90}
registry/sleep_anxiety.yaml {'Gen Z': 90}
registry/social_anxiety.yaml {'Gen Z': 90}
registry/somatic_healing.yaml {'Gen Z': 90}
```

14 of 16 checked topic registries are 100% `Gen Z`-labeled; only `adhd_focus` and
`mindfulness` are `corporate_managers`-labeled. **Every other persona rendering any
of those 14 topics under the Wave-1 G-DEF4 hard-stop will log foreign-persona drops
and hard-stop production render**, because `_registry_persona_matches` fail-CLOSES on
an explicit foreign label (correctly — that is the Wave-1 fix working as designed)
but the registry itself was authored for one persona only, with no neutral/multi-
persona alternative and no per-persona registry file variant.

## Live evidence (this lane, `burnout` topic)

Two of the three lane-02 cells were rendered with the real four-piece chord
(`--pipeline-mode spine --quality-profile production --exercise-journeys
--render-book`) against the CURRENT (pre-fill and post-fill; the registry itself was
untouched by this lane) `registry/burnout.yaml`:

| Cell | Exit code | DEF4 drops | Evidence |
|------|-----------|-----------:|----------|
| `corporate_managers × burnout × overwhelm` | 1 (SystemExit, production gate) | 106 | `renders/corporate_managers__burnout__overwhelm_run.log` |
| `tech_finance_burnout × burnout × overwhelm` | 1 (SystemExit, production gate) | 106 | `renders/tech_finance_burnout__burnout__overwhelm_run.log` |
| `healthcare_rns × burnout × overwhelm` | not independently rendered (time-boxed) | **inferred 106** — same registry file, same root cause, same section count | extrapolated from the identical `registry/burnout.yaml` shared by all 3 personas; see "Deferred" below |

Sample drop record from the actual run (`[PRODUCTION GATE / G-DEF4]` line):

```
106 foreign-persona registry drop(s) for persona_id='corporate_managers'.
sample: {'section_key': 'section_01', 'section_persona': 'Gen Z',
         'spine_persona_id': 'corporate_managers', 'site': 'registry_type_lists'}
```

Both renders hard-stop with `SystemExit(1)` **before** `enrichment_audit.json` is
written, so no per-book audit JSON artifact exists to attach — the run logs
(`*_run.log`) are the audit evidence for this finding.

## Why this is a genuine, previously-undetected regression risk

The 100-book corpus analysis (`ANALYSIS_REPORT.md`, 2026-07-18) that seeded this
Wave-2 pack reused **prior renders that predate the Wave-1 G-DEF4 hard-stop**
(`source_kind` = `pearl_prime_prior` / `reuse` for nearly all `corporate_managers`
rows, including `C048` itself). None of those prior renders would have hit this
hard-stop because it did not exist yet. The moment any of those same
persona×topic cells are **re-rendered today** under the canonical four-piece chord
(exactly what "catalog-perfect" in `PEARL_PRIME_PERFECT_BOOKS_SPEC.md` §1 requires),
they hard-stop on G-DEF4 — this includes the Q-W2-CELLS-01 **default** cell
(`corporate_managers × burnout × overwhelm`, the "#1923-proven shipping cell").
"Proven" here means proven under the pre-Wave-1 gate set, not under the current one.

## Why not fixed in this lane (scope discipline, not avoidance)

The dispatcher's HARD CONSTRAINTS for this lane are explicit: **"Composer/topology is
NOT the lever — FILL banks only"** and **"Do NOT silence DEF4/F16 or weaken tuple
viability / F14 / chord CI."** Two fix paths were evaluated and both fall outside
"fill banks only":

1. **Overwrite `registry/burnout.yaml` section content to `corporate_managers` /
   `tech_finance_burnout` / `healthcare_rns` labels.** Rejected: `load_registry(topic)`
   (`phoenix_v4/planning/registry_resolver.py`) has **no persona axis** — one file per
   topic. Relabeling the existing Gen-Z content would not add coverage, it would
   **move** the failure onto `gen_z_professionals × burnout` (a real, already-shipped
   MATRIX cell, `C027`), which is exactly the "no pool shrunk" violation the mission
   brief forbids ("inventory: EXTENDS ... never greenfield a parallel bank").
2. **Add a persona-aware registry lookup path** (e.g. `registry/{topic}/{persona}.yaml`
   fallback). Rejected for this lane: implementing it means editing
   `registry_resolver.py::load_registry` and its call sites in
   `enrichment_select.py` — that is composer/wiring code, not a bank/data file, and
   is explicitly the banned lever for this lane.

Both paths are legitimate future work; neither is "fill a bank in place."

## Recommended fix (for the next lane/wave, not claimed done here)

Author a genuine, distinct, persona-labeled registry file **per target persona per
topic** (mirroring the `adhd_focus.yaml` / `mindfulness.yaml` precedent, which are
already `corporate_managers`-labeled) and extend `load_registry()` to accept a
`persona` parameter with graceful fallback to the existing single-persona file when no
persona-specific file exists (additive, backward-compatible — does not touch or
shrink the existing Gen-Z pool). This is a `phoenix_v4/planning` + `registry/` change
that should go to **Pearl_Dev / composer-adjacent** ownership (Lane 04's disjoint
surface is CI/gate scripts, not this), or a dedicated future C4 lane with its own
routing-code write scope — explicitly larger than "fill banks" and should be
proposed to the dispatcher as its own tracked item.

## DEFERRED (honest, not silent)

- `healthcare_rns × burnout × overwhelm` DEF4 render was **not independently executed**
  in this pass (time-boxed after 2 corroborating runs on the same shared root cause).
  Tuple viability for this cell is PASS (see `tuple_viability_3cells.txt`); the DEF4
  block is inferred with high confidence from the identical shared `registry/burnout.yaml`
  every persona for this topic reads from.
- The other 13 Gen-Z-locked topic registries (`anxiety`, `boundaries`,
  `compassion_fatigue`, `courage`, `depression`, `financial_anxiety`,
  `financial_stress`, `grief`, `imposter_syndrome`, `overthinking`, `self_worth`,
  `sleep_anxiety`, `social_anxiety`, `somatic_healing`) were **not** audited
  persona-by-persona in this pass; only confirmed the same single-persona-per-topic
  authoring pattern holds catalog-wide via the same script.
- No registry files were edited in this lane (deliberately, per the ownership
  analysis above).

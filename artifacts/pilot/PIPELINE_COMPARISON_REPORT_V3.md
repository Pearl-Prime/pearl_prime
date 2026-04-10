# Pipeline comparison report V3 — Depth Pass v1

Date: 2026-04-11  
Project: `proj_state_convergence_20260328`  
Subsystem: `core_pipeline`

PR #379 (depth module map + `docs/DEPTH_MODULE_PROTOCOL.md`) was merged to `main` before this work. Depth Pass v1 runs **after** `select_enrichment()` and pulls **existing** content only (teacher atoms, persona CANONICAL, registry variants F2+, pearl_practice templates, phoenix standards, practice library, bridge templates) per `config/depth/depth_module_map.yaml`.

Word counts below use `wc -w` on `book.txt` unless noted. Per-chapter figures use `book_plan.json` chapter `total_words` (sum of slot bodies after depth pass).

---

## Depth Pass v1 Results

### Word count progression

| Topic | V1 (no depth) | V2 (compose-only pilot) | V3 (depth pass) | Baseline | V3 / Baseline |
|-------|---------------|---------------------------|-----------------|----------|---------------|
| anxiety | 2413 | 2500 | 8609 | 5033 | 171% |
| grief | 2768 | 2856 | 8333 | 7235 | 115% |
| burnout | 2347 | 2430 | 8218 | 4817 | 171% |

**Notes**

- **V1** totals are from `artifacts/audit/depth_gap_analysis.md` (pre-depth pilot audit totals).
- **V2** is the same spine → beatmap → enrichment → `compose_from_enriched_book` path without depth pass (`artifacts/pilot/{topic}_new/book.txt`).
- **V3** is `artifacts/pilot/{topic}_v3/book.txt` after `apply_depth_pass`.
- **Baseline** is registry fast-path output (`artifacts/pilot/{topic}_baseline/book.txt`).

V3 exceeds baseline on **total manuscript words** for anxiety and burnout because the depth pass drives each chapter toward the beatmap target (stop when per-chapter deficit ≤ 100 words), while baseline books reflect a different assembly path and section mix. Grief lands closer to baseline on totals but still differs by chapter (see below).

---

### Depth modules added

Source: `artifacts/pilot/{topic}_v3/enrichment_audit.json` → `depth_modules_added`.

Representative pattern (all three topics): multiple passes per chapter across `recognition_depth`, `story_scene`, `mechanism_depth`, `consequence_exposure`, `somatic_detail` / `practice_scaffold` (where allowed), `bridge_transition`, `integration_landing`, and topic-specific modules such as `witnessing_presence` for grief/burnout. Each entry records `chapter`, `module`, `source_type` (`teacher_atom`, `persona_atom`, `registry_variant`, `component_template`, `phoenix_standard`, `practice_library`, `exercise_atom`, `exercise_bridge`), `words_added`, and `remaining_deficit`.

---

### Per-chapter word count (V3 vs baseline)

Comparison uses chapter `total_words` from `artifacts/pilot/{topic}_v3/book_plan.json` vs `artifacts/pilot/{topic}_baseline/budget.json`.

**Anxiety** — no chapters were &gt;20% **below** baseline; ch07 is slightly below (809 vs 844, ~96% of baseline).

**Grief** — chapters **07** and **10** are &gt;20% **below** baseline (v3 244 vs 667; 375 vs 485). Other chapters meet or exceed baseline. Likely causes: mid/late priority modules with **chapter_affinity** or **banned_chapters** constraints that skip `practice_scaffold` for grief in early/mid chapters, plus thinner registry pulls for those beatmap shapes.

**Burnout** — no chapters were &gt;20% below baseline.

---

### Topic rule compliance

| Rule | Result |
|------|--------|
| Grief ch1–6: no `practice_scaffold`, no `somatic_detail` in depth pass | Yes — `depth_modules_added` contains no `practice_scaffold` or `somatic_detail` for chapters 1–6 on `grief_v3`. |
| Anxiety ch1–4: exercise density / early exercise ceiling | Yes — no `EXERCISE` slots in chapters 1–4 in `anxiety_v3` `book_plan.json`; no depth slots added those types in ch1–4. |
| Depression: exercises excluded from early chapters | Not exercised in this pilot (depression book not regenerated). Mark **N/A**. |

---

### Quality check (manual read of chapter 1)

| Question | Assessment |
|----------|--------------|
| Grief ch1 feels like witnessing, not fixing? | **Partially** — depth pass adds `witnessing_presence` and registry long variants; tone remains mixed with teacher doctrinal lines where the waterfall already selected short HOOKs. |
| Anxiety ch1 names the alarm pattern specifically? | **Mostly yes** — stacked recognition/story depth reinforces false-alarm framing; still read as slot concatenation vs fully composed baseline. |
| Burnout ch1 legitimizes exhaustion before reframing? | **Mostly yes** — recognition + consequence + witnessing modules add weight before late practice. |
| Depth modules add relevant content, not filler? | **Mostly yes** — content is drawn from approved atoms, persona CANONICAL, and alternate registry variants; bridge lines are short template pulls. Some repetition risk when multiple modules fire per chapter. |

---

### Remaining gaps

- **Grief ch7 / ch10** remain well below baseline in this comparison — investigate beatmap slot targets vs module affinity for those chapter roles and whether `witnessing_presence` / registry pulls exhaust before deficit closes.
- **Modules with no content** for a given chapter/source: depth pass skips silently when `_load_depth_content` returns `None` (logged only via empty audit entries for that attempt — future work: explicit “miss” telemetry).
- **Closing the gap** to registry parity still requires **composer-level** bridges, exercise assembly, and placeholder hydration (`clean_for_delivery`) — depth pass addresses **volume**, not full structural parity with the legacy renderer.

---

### Verdict

**Is the depth pass closing the gap?** **Yes, for aggregate word count** — V3 totals are in the same order of magnitude as baseline (and exceed it for anxiety/burnout) by filling toward beatmap targets. **No, for uniform chapter-level parity** — grief still shows two chapters sharply under baseline, and all topics still read as **stacked slots** vs continuous baseline prose.

**How much further to go?** Wire **full chapter compose** + **delivery hygiene**, consider **per-chapter cap** on depth slots to reduce redundancy, and add **explicit miss logging** when no source yields text for a module.

---

## Evidence paths

- V3 outputs: `artifacts/pilot/{anxiety,grief,burnout}_v3/`
- Baseline: `artifacts/pilot/{topic}_baseline/`
- Pre-depth pilot: `artifacts/pilot/{topic}_new/`
- Implementation: `phoenix_v4/planning/enrichment_select.py` (`apply_depth_pass`, `_load_depth_content`), `scripts/pilot/run_spine_pipeline.py`
- Tests: `tests/test_enrichment_select.py` (depth pass tests included)

# Pearl_Dev Agent Prompt — Implicit Therapeutic Engine Implementation

## Identity

You are Pearl_Dev working in the Phoenix Omega repo. Your task is to implement the **Implicit Therapeutic Engine (ITE)** defined in `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`.

## Mandatory startup

1. Read these files in order before any work:
   - `docs/ONBOARDING_START_HERE.md`
   - `ps.txt`
   - `docs/DOCS_INDEX.md`
   - `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` (full — 1,004 lines, the authority spec)
   - `specs/AI_MANGA_PIPELINE_SUMMARY.md` (dependency — existing pipeline)
   - `specs/MANGA_GENRE_AGENT_SPEC.md` (dependency — Genre Agent somatic_targets)
   - `config/quality/ei_v2_config.yaml` (dependency — EI v2 existing config)
   - `config/manga/gate_registry.yaml` (dependency — existing QC gates)

2. Return a STARTUP_RECEIPT as your first reply showing files read, current state assessment, and any blockers.

3. Route any git branch/commit/push/PR work to Pearl_GitHub — do not run git mutations yourself.

## Task: Implement ITE in two phases

### Phase 1 — Minimum Viable ITE (spec §18.1)

Implement these 10 acceptance criteria:

**Config & schema work:**
1. Extend `config/quality/ei_v2_config.yaml` — add `visual_therapeutic` module group with 4 new dimensions (`vt_parasympathetic`, `vt_processing`, `vt_somatic`, `vt_stealth`) per spec §12.4. Include weights, warn/fail thresholds, inputs, forbidden_terms list, penalty_weight, and composite formula.

2. Extend Genre Agent `somatic_targets` schema — add 6 new ITE target blocks (`fractal_regulation`, `color_arc`, `breath_sequences`, `gutter_therapy`, `sabido_roles`, `soundtrack`) per spec §13.1. Create genre-specific ITE profiles for all 10 genres per §13.2 table (shonen, seinen, shojo, sports, horror, iyashikei, cultivation, manhwa, webtoon_romance, isekai). File: the Genre Agent's config YAML or schema, likely in `config/manga/` or `schemas/manga/`.

3. Define `gutter_classes` in Visual Identity Agent output schema — 5 classes (tight=0.5x, standard=1.0x, processing=2.0x, therapeutic=3.0x, breath=4.0x) per spec §8.1.

4. Define `color_arc` in Visual Identity Agent output schema — 5-phase structure (hook/tension/turn/resolution/afterglow) with temp ranges, sat ranges, and genre override keys per spec §6.4.

**Agent output extensions (artifact schema changes):**
5. Extend `panel_prompts.json` schema — add per-panel `fractal_target` (fd_range, source_category, coverage_pct, therapeutic_role) per §7.4, and per-chapter `breath_map` (breath_sequences array with page_range, phase_panels, target_state, chapter_section) per §5.4.

6. Extend `style_bible.json` schema — add `color_arc`, `fractal_palette`, `gutter_classes`, `breath_visual_grammar` per §14.1.

7. Extend `genre_blueprint.json` schema — add `sabido_map` with three roles (positive_model, negative_model, transitional) per §9.3, including `dialogue_prohibition` list.

**CI scripts (6 new scripts, all in `scripts/ci/`):**
8. `ite_gutter_check.py` — validates gates T-01 (post-band-4 gutter ≥ processing), T-02 (post-band-5 gutter ≥ therapeutic), T-03 (≤5 consecutive tight gutters), T-15 (no tight in resolution). Input: `panel_prompts.json` + `lettering_spec.json`. Exit 1 on any BLOCKER fail.

9. `ite_stealth_scan.py` — validates gate T-04. Scans `chapter_script.json` dialogue + captions for forbidden terms list from §12.2 (`therapy, mindfulness, grounding, breathing exercise, meditation, wellness, self-care, healing journey, inner peace, mental health, calm down, relax your body, take a breath`). Exit 1 if any found.

10. `ite_color_arc.py` — validates gates T-08 (resolution color temp ≥5500K), T-09 (resolution saturation ≤55%), T-14 (monotonic saturation decrease in resolution arc). Input: `panel_prompts.json` + `style_bible.json`. WARN only (exit 0 with warnings).

11. `ite_breath_check.py` — validates gates T-07 (≥1 breath sequence per chapter), T-10 (fractal in hold panels). Input: `panel_prompts.json`. WARN only.

12. `ite_soundtrack.py` — validates gates T-05 (no lyrics in resolution), T-06 (video ends on low arousal), T-11 (calming tempo ≤78 BPM), T-12 (≥8s silence per 5min), T-13 (pentatonic ratio). Input: `soundtrack_config.yaml` + audio metadata. Exit 1 on T-05 or T-06 BLOCKER.

13. `ite_composite.py` — validates gate T-19. Reads `ite_report.json`, computes ITE_score composite per §12.3 formula, exits 1 if ITE_score < 0.50. Input: `ite_report.json`.

**QC Agent extension:**
14. Extend QC Agent to emit `ite_report.json` per chapter per §16.2 schema. The report includes: ite_score, 4 dimension scores, breath_sequences, color_arc_compliance, fractal_coverage, gutter_compliance, stealth_scan, soundtrack metrics, gate pass/fail counts.

**Tests:**
15. Write tests for each CI script (test fixtures with known-pass and known-fail `panel_prompts.json`, `chapter_script.json`, `soundtrack_config.yaml`, `ite_report.json`). Place in `tests/test_ite_*.py`.

### Phase 2 — Full ITE (spec §18.2, lower priority)

After Phase 1 lands:
- Wire remaining INFO gates T-16 through T-20
- Activate EI v2 `visual_therapeutic` module in learner
- Implement video therapeutic engine (§10) — camera movement and edit rhythm validation
- Implement soundtrack therapeutic engine (§11) — tempo arc, silence placement, pentatonic ratio
- Cold read validation protocol tooling

## Write scope

```
config/quality/ei_v2_config.yaml          (extend — add visual_therapeutic block)
config/manga/genre_ite_profiles.yaml      (new — 10 genre ITE profiles)
schemas/manga/panel_prompts.schema.json   (extend — fractal_target, breath_map)
schemas/manga/style_bible.schema.json     (extend — color_arc, fractal_palette, gutter_classes, breath_visual_grammar)
schemas/manga/genre_blueprint.schema.json (extend — sabido_map, extended somatic_targets)
schemas/manga/ite_report.schema.json      (new — ITE report per chapter)
schemas/manga/soundtrack_config.schema.json (new — soundtrack therapeutic config)
scripts/ci/ite_gutter_check.py            (new)
scripts/ci/ite_stealth_scan.py            (new)
scripts/ci/ite_color_arc.py               (new)
scripts/ci/ite_breath_check.py            (new)
scripts/ci/ite_soundtrack.py              (new)
scripts/ci/ite_composite.py               (new)
phoenix_v4/manga/qc/ite_scorer.py         (new — ITE dimension scoring logic)
phoenix_v4/manga/qc/ite_report.py         (new — ITE report emitter)
tests/test_ite_gutter.py                  (new)
tests/test_ite_stealth.py                 (new)
tests/test_ite_color_arc.py               (new)
tests/test_ite_breath.py                  (new)
tests/test_ite_soundtrack.py              (new)
tests/test_ite_composite.py               (new)
tests/test_ite_scorer.py                  (new)
tests/fixtures/ite/                       (new — test fixture JSONs)
```

## Out of scope

- Git mutations (Pearl_GitHub lane)
- Consumer-facing copy or marketing claims
- Existing audiobook text pipeline (different spec)
- VR/AR content
- Biometric feedback loops
- Clinical outcome claims

## Architecture constraints

1. **ITE scoring is heuristic-first.** All 4 dimensions use rule-based scoring from artifact fields. No LLM calls in the scoring path. The `mode: heuristic` in config means deterministic computation from panel_prompts + style_bible + genre_blueprint + soundtrack_config.

2. **CI scripts are standalone.** Each reads JSON/YAML artifacts from a chapter output directory (passed as `--chapter-dir` arg). They emit structured JSON to stdout and exit 0/1. They do NOT import pipeline runtime code — they are pure artifact validators.

3. **Gate registry.** Register all 20 new gates (T-01 through T-20) in `config/manga/gate_registry.yaml` under category `therapeutic`, following the existing gate schema.

4. **Forbidden terms list** is maintained in ONE place: `config/quality/ei_v2_config.yaml` under `visual_therapeutic.dimensions.vt_stealth.forbidden_terms`. CI scripts load from there; do not duplicate.

5. **Genre ITE profiles** should be a separate config file (`config/manga/genre_ite_profiles.yaml`) cross-referenced by genre_id, NOT inlined into the Genre Agent spec. The Genre Agent loads the profile at runtime by genre_id.

6. **ITE report** is an artifact, not a log. It goes in the chapter output directory alongside `panel_prompts.json`, `style_bible.json`, etc.

## PR sequence (hand each to Pearl_GitHub)

- **PR-ITE-1:** Config + schemas (ei_v2_config extension, genre_ite_profiles, all schema files, gate_registry extension)
- **PR-ITE-2:** CI scripts + tests (6 scripts, 7 test files, test fixtures)
- **PR-ITE-3:** ITE scorer + report emitter (phoenix_v4/manga/qc/ modules)
- **PR-ITE-4:** Agent output extensions (wiring into Visual Identity, Genre, Visual, Lettering, Layout, QC agents)

## Key spec sections to reference during implementation

| What you're building | Read spec § |
|---|---|
| Gutter classes + rules | §8.1, §8.2, §8.3 |
| Breath sequences + PBE | §5.1–§5.4 |
| Color arc + genre overrides | §6.1–§6.4 |
| Fractal targets + placement | §7.1–§7.4 |
| Sabido character map | §9.1–§9.3 |
| EI v2 dimensions + scoring | §12.1–§12.4 |
| Genre ITE profiles | §13.1–§13.2 |
| QC gates (T-01→T-20) | §15.1–§15.3 |
| Artifact schemas | §16.1–§16.2 |
| CI scripts | §17.1–§17.2 |
| Acceptance criteria | §18.1 (Phase 1), §18.2 (Phase 2) |
| Video therapeutic engine | §10.1–§10.4 |
| Soundtrack therapeutic engine | §11.1–§11.4 |
| Forbidden terms + stealth scoring | §12.2 (vt_stealth) |

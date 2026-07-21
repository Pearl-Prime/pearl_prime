# Music Mode E2E Smoke — Ahjan (second cell)

Lane `music_mode_e2e_smoke_20260721`, Wave 2 of
`docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/`.

## Musician chosen

No real-external-musician nomination found for `Q-MM-V2-FIRST-REAL-MUSICIAN-01`
(`artifacts/coordination/operator_decisions_log.tsv` row `OPD-20260611-041` records the
question and its default recommendation, not an actual nomination). Per INDEX.md's
stated default, onboarded a **second Ahjan cell** — reuses the existing consented
reference musician (zero new-consent risk). Chose topic family
`self_worth_and_shame`, uncovered by Ahjan's existing reference kit (which covers
`presence_and_stillness`, `recovery_and_repair`, `quiet_courage`, `hope_and_renewal`
per `SOURCE_OF_TRUTH/musician_banks/ahjan/themes.yaml`'s header comment).

## Step 1 — wizard route (registry idempotency proof)

Ran the real `music_survey_save_handler.py` POST route (`FastAPI TestClient`, real
`brand-wizard-app/server/music_survey_routes.py` app, pointed at the REAL
`config/music/music_brand_registry.yaml` — not a tmp fixture) with Ahjan's real
survey content, flattened to the client's `musician_reflections_survey` shape
(`display_name`, `primary_genre`, `primary_themes`, ... — matching
`brandMatch.js`'s `MUSICIAN_REFLECTIONS_SCHEMA`, not the nested
`SURVEY_TEMPLATE.yaml` 8-block shape):

```
POST /wizard/music-survey/save {"wizard_session_id": "ahjan_music_resave_smoke", "survey_responses": {...flat...}}
-> 200 {"status": "saved", "next_step": "step5", "yaml_path": "brands/ahjan_music_resave_smoke.yaml"}
```

Registry diff confirmed:
- `brand_id` stayed `ahjan_music` — **the existing row was updated in place, never
  duplicated, never remapped to one of the 37** (matches mission 1(a)).
- `created: 2026-06-12` preserved unchanged (idempotent — the anti-drift invariant
  in `upsert_music_brand_registry_row` worked as designed).
- `archetype` and `notes` were overwritten with generically-derived values (the
  live POST route has no way to pass through the original curated `archetype`/
  `notes` strings — a minor, honest finding, not a bug: those two fields are pure
  documentation, not functional routing fields).
- `survey_yaml_pointer` was rewritten to the new session's scratch path
  (`brands/ahjan_music_resave_smoke.yaml`).

**This mutation was reverted** (registry restored to its pre-smoke state, scratch
YAML deleted) rather than committed — a real re-save from this exact session ID
isn't a legitimate persistent artifact, and committing it would have overwritten
the reference kit's original documentation fields with generic placeholders. The
functional proof (brand_id stability + idempotent `created` date + no
duplication/remap) stands regardless.

## Step 2 — song-kit generation (real Tier-1 engine, this session)

Wired `phoenix_v4.musician.lyric_mood_engine.TierRoutedEngine` +
`make_operator_authored_pearl_writer_fn` (lane 03) into
`phoenix_v4.musician.song_kit_generator.SongKitGenerator`, seeded with 18
operator-authored bodies (this session, Tier-1, no LLM API) — 6 pools × 3
variants — grounded in Ahjan's documented voice (`SOURCE_OF_TRUTH/musician_banks/
ahjan/themes.yaml`, `survey_responses/2026-06-12.yaml`: observational,
plain-spoken, body-based imagery, "the half-second of noticing", standing-down /
homecoming imagery; avoids spiritual triumph, catharsis, manifesting, karma-fuel)
applied to `self_worth_and_shame`'s themes ("unlearning the inner verdict", "worth
that is not earned", "meeting shame with plain language").

```
matched_families: ['self_worth_and_shame']
complete: True   (all 6 pools >= SPEC-739 floor of 3 variants)
fork: with-lyrics
```

**Collision avoided:** `SongKitGenerator` hardcodes atom_id as
`<musician_id>_<POOL>_01`. Ahjan's real reference kit already has `_01`/`_02`/`_03`
per pool on disk (verified before writing) — using the default `_01` id would have
**silently overwritten the real reference atoms**. Renamed each generated
`DraftAtom.atom_id` from `_01` to `_04` (the next free index, uniform across all 6
pools) before calling the bank writer. Verified via `git status` after writing:
only 6 new files, zero modified/deleted existing atom files.

Written via `phoenix_v4.musician.bank_writer.write_kit_to_bank` (lane 03) to:
- `SOURCE_OF_TRUTH/musician_banks/ahjan/approved_atoms/{LYRIC_OPENING,LYRIC_BESTSELLER_BEAT,LYRIC_CLOSING,MUSIC_REFLECTION_OPENING,MUSIC_REFLECTION_BESTSELLER_BEAT,MUSIC_REFLECTION_CLOSING}/ahjan_*_04.yaml`

`config/music/music_brand_registry.yaml`'s `ahjan_music` row is **unchanged** — it
already covers this musician; no duplicate row needed (mission's explicit
instruction for the Ahjan-second-cell path).

## Step 3 — diversity gate (real, lane 04's gate)

```
PYTHONPATH=. python3 scripts/ci/check_music_brand_diversity.py --brand-id ahjan_music --quality-profile production
```

```
overall=PASS
G1: n=12 (was 9) per pool, max_reuse=1, violation=False, for all 6 pools
G2-G8: skipped (Phase-A degraded mode, 0 catalog book-plan rows < N=50) — honest,
       not fabricated
```

`n=12` (9 existing + 3 new) with zero reuse violations across every pool confirms
the new content is genuinely distinct from the existing reference atoms — not
copy-paste. Report committed: `artifacts/qa/music_brand_diversity_report_ahjan_music_20260721.{md,json}`
(supersedes lane 04's pre-second-cell snapshot with the same filename).

## Step 4 — production render: **BLOCKED**, real infrastructure gap found

Mission requires rendering one smoke book via the four-piece chord
(`--pipeline-mode spine --quality-profile production --exercise-journeys`) for
`brand_id=ahjan_music`, relying on lane 02's auto-detection — explicitly **without**
passing `--music-mode`/`--musician-id` (that would only prove the old manual path).

**Finding: there is no CLI-reachable path in `scripts/run_pipeline.py` that
resolves `brand_id` to `ahjan_music` at all**, so lane 02's auto-detection code
(`apply_auto_detected_music_args`, verified correct and unit-tested) never gets a
chance to fire through the normal CLI surface:

- `run_pipeline.py`'s `main()` resolves `brand_id` via
  `phoenix_v4.planning.teacher_brand_resolver.resolve_teacher_brand(topic_id,
  persona_id, series_id)` (default) or `resolve_brand_for_teacher(--teacher)`
  (explicit override). Neither path is threaded to read
  `config/music/music_brand_registry.yaml` — that registry is an entirely separate
  system from `config/catalog_planning/{brand_teacher_matrix,brand_teacher_assignments}.yaml`
  (Path X's teacher/topic/persona → brand routing).
- `--teacher ahjan` does NOT resolve to `ahjan_music` — Ahjan is *also* a
  teacher-mode Path X teacher, and `brand_teacher_matrix.yaml` maps
  `primary_teacher: ahjan` to `stillness_press` (a different, existing 1-of-37
  brand). Confirmed via `grep -n "primary_teacher: ahjan" config/catalog_planning/brand_teacher_matrix.yaml`.
  `--teacher ahjan_music` would fail teacher-id validation (not a registered
  teacher).
  There is no `--brand-id`/`--brand` flag on `run_pipeline.py` (`--help` reviewed
  in full).
- `teacher_brand_resolver.resolve_teacher_brand()` DOES accept an optional
  `brand_id` override parameter internally (would preserve an explicit brand_id
  when no assignment row matches) — but `run_pipeline.py`'s call site never
  passes one; there is no CLI flag threading a value into it.
- `scripts/generate_full_catalog.py` (the real batch-catalog driver
  `CatalogPlanner.generate_for_brand` is proven wired to, per lane 02) derives its
  `--teacher <id>` subprocess flag from `_teacher_id_for_brand()`, which is itself
  keyed off `brand_teacher_matrix.yaml` — also has no `ahjan_music` entry, so it
  cannot dispatch a music-mode brand either.

**This is a real, out-of-scope gap**, not a reason to route around the DO NOT list
by passing `--music-mode`/`--musician-id` explicitly (that would prove nothing new)
or to invent an unauthorized `--brand-id` CLI flag mid-lane (none of lanes
01/02/03/04/05's hot-file lists include `scripts/run_pipeline.py`'s
brand-resolution call site, `teacher_brand_resolver.py`, or
`brand_teacher_matrix.yaml` — touching them now would be scope creep on an
unreviewed, structural routing decision, not "pure integration proof" per this
lane's own PROVENANCE section).

**Recommended next action** (not done here): add an optional `--brand-id` CLI
override on `run_pipeline.py`, threaded into
`resolve_teacher_brand(..., brand_id=args.brand_id)` (the function already
supports it), as its own small, reviewed follow-up lane — or register music-mode
brands in `brand_teacher_matrix.yaml`/`brand_teacher_assignments.yaml` if that's
judged the more architecturally correct home for brand routing going forward
(operator/architect call, not this lane's to make unilaterally).

## Acceptance-layer label (honest, per CLAUDE.md)

This smoke is **structurally clear** for steps 1–3 (survey→registry idempotency,
real Tier-1 kit generation with collision-safe writing, diversity gate PASS on
real data) — a `register_gate`-equivalent PASS at most, **not** a bestseller claim
of any kind. Step 4 (the actual book render proving auto-detection end-to-end) is
**BLOCKED**, so the pack's full "wizard → registry → song-kit → pipeline" loop is
**NOT proven closed** — three of four links are proven; the fourth (pipeline
auto-dispatch) is blocked on a real, disclosed infrastructure gap, not attempted
and not faked.

## Cleanup

- `music_brand_registry.yaml` step-1 mutation: reverted (see Step 1).
- `brands/ahjan_music_resave_smoke.yaml` scratch file: deleted.
- New bank atom files (`*_04.yaml`, 6 files): real, committed, not scratch.
- Updated diversity report: real, committed.

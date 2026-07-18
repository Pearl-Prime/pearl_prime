# Educators EXERCISE Gap Closure — 2026-07-10

Agent: Pearl_Writer
Task: educators EXERCISE gap closure (7 exact en-US cells)
Base: origin/main @ 82b58af321fece7697a69e5ac9edf9bff857f20b

## 1. Discovery reconciliation

### 1.1 Gap re-derivation (pearl_prime_atom_100pct_gap_matrix_20260606.tsv)

```
awk -F'\t' '$1=="educators" && $4=="en-US" && $3=="EXERCISE"' \
  artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv
```

Confirmed exactly 7 en-US EXERCISE gap rows for `educators`, `current_variants=0`,
`required_variants=3`, all `P1` / `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606`:

| topic | slot | locale | current | required | priority |
|---|---|---|---|---|---|
| burnout | EXERCISE | en-US | 0 | 3 | P1 |
| financial_anxiety | EXERCISE | en-US | 0 | 3 | P1 |
| imposter_syndrome | EXERCISE | en-US | 0 | 3 | P1 |
| overthinking | EXERCISE | en-US | 0 | 3 | P1 |
| sleep_anxiety | EXERCISE | en-US | 0 | 3 | P1 |
| social_anxiety | EXERCISE | en-US | 0 | 3 | P1 |
| somatic_healing | EXERCISE | en-US | 0 | 3 | P1 |

This matches the mission's target list exactly. No en-US EXERCISE gap rows exist for
educators beyond these 7. Gap matrix TSV itself was **not** modified (out of scope for
this lane) — this table is a read-derived summary only.

### 1.2 File-presence verification

All 7 target paths confirmed **absent** before this lane (`ls`/`test -f` on each):

- `atoms/educators/burnout/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/financial_anxiety/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/imposter_syndrome/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/overthinking/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/sleep_anxiety/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/social_anxiety/EXERCISE/CANONICAL.txt` — ABSENT
- `atoms/educators/somatic_healing/EXERCISE/CANONICAL.txt` — ABSENT

(`atoms/educators/{anxiety,boundaries,compassion_fatigue,courage,depression,
financial_stress,grief,self_worth}/EXERCISE/CANONICAL.txt` already existed, each with
30 variants — used as shape/tone reference.)

### 1.3 Open-PR collision check

`gh api search/issues?q=repo:...+type:pr+state:open+"atoms/educators"` and
`+"educators/burnout/EXERCISE"` — only PR #1812 matches the `atoms/educators` string
(in its body text); `gh pr diff 1812 --name-only | grep educators` returns nothing.
**No open PR touches any of the 7 target files.**

### 1.4 Tuple-viability re-run (NO_STORY_POOL premise)

```
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona educators --topic anxiety --engine false_alarm --format F006 --json
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona educators --topic burnout --engine overwhelm --format F006 --json
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona educators --topic imposter_syndrome --engine shame --format F006 --json
```

All three returned `TUPLE_VIABLE` (binding OK, arc OK, STORY pool OK, band coverage OK).
**`educators-no-story-pool-status = cleared-on-main`** — the stale "educators still
fails with NO_STORY_POOL" premise is confirmed false for all 3 router-cited tuples.
This lane proceeded strictly as an **EXERCISE-atom-authoring lane**, not a STORY-pool
lane, per the pre-requisite gate instructions.

### 1.5 Neighboring-file shape/tone reference

Read `atoms/educators/compassion_fatigue/EXERCISE/CANONICAL.txt`,
`atoms/educators/anxiety/EXERCISE/CANONICAL.txt`, and
`atoms/educators/financial_stress/EXERCISE/CANONICAL.txt` in full. Confirmed exact
byte-level block format:

```
## EXERCISE vNN
---

---
<practice-shaped body: imperative instructions, breath/press/count/notice cues>
---
```

parsed by `phoenix_v4/planning/registry_resolver.py::_parse_canonical_txt` (the real
loader `_load_persona_atoms` uses — confirmed by reading source, not assumed).

## 2. Authored content

All 7 files written matching the exact reference format, each with **20–24 real,
distinct variants** (well above the `required_variants=3` floor):

| file | variants (parsed) | pass `_filter_practice_pool` (strict shape gate) |
|---|---|---|
| `atoms/educators/burnout/EXERCISE/CANONICAL.txt` | 24 | 19 |
| `atoms/educators/financial_anxiety/EXERCISE/CANONICAL.txt` | 21 | 14 |
| `atoms/educators/imposter_syndrome/EXERCISE/CANONICAL.txt` | 20 | 14 |
| `atoms/educators/overthinking/EXERCISE/CANONICAL.txt` | 20 | 13 |
| `atoms/educators/sleep_anxiety/EXERCISE/CANONICAL.txt` | 20 | 16 |
| `atoms/educators/social_anxiety/EXERCISE/CANONICAL.txt` | 20 | 16 |
| `atoms/educators/somatic_healing/EXERCISE/CANONICAL.txt` | 20 | 15 |

Even under the strictest production gate (`_is_practice_atom` / `_filter_practice_pool`,
the OPD-107 / PR #612 shape contract), every file clears the `>= 3` requirement by a
wide margin. Content is original, educators-persona-native (classroom/grading/hallway/
staff-room/parent-conference framing woven through body-based somatic practice, matching
the established craft pattern in the 8 pre-existing educators EXERCISE files), topic-
specific to each of the 7 gaps, and contains no cross-persona borrowing and no topic
widening. Verified no `_RESIDUE_MARKERS` hits (no RTF/HTML/URL/affiliate-marketing
residue) in any file.

Parse validation:

```
PYTHONPATH=. python3 -c "
from phoenix_v4.planning.registry_resolver import _parse_canonical_txt
... " # 7/7 files parse cleanly, 20-24 atoms each, no parser errors
```

## 3. Production-path native-selection proof

### 3.1 Why not a full `--render-book` pipeline run

```
PYTHONPATH=. python3 scripts/run_pipeline.py --topic burnout --persona educators \
  --arc config/source_of_truth/master_arcs/educators__burnout__overwhelm__F006.yaml \
  --pipeline-mode spine --runtime-format F006 --quality-profile production \
  --exercise-journeys --no-job-check --render-book --render-dir <dir> --out <plan.json>
```

fails at the CLI's own pre-Stage-3 readiness gate:

```
Topic source readiness failed for requested topic 'burnout' ...
  - SCENE bank has no proseful entries at atoms/educators/burnout/SCENE/CANONICAL.txt
```

**All 7 target topics** are missing `atoms/educators/<topic>/SCENE/CANONICAL.txt`
(verified for all 7). This is a **pre-existing, out-of-scope gap** — SCENE is a
different content type from EXERCISE and authoring it is outside this lane's
`WRITE_SCOPE`. A direct `select_enrichment()` full-book compile independently confirms
the same underlying reality: it raises `EnrichmentGapError` on the first unfillable
non-EXERCISE slot (`REFLECTION`, chapter 8) — again orthogonal to EXERCISE.

### 3.2 Real-function, unmocked proof of persona-native EXERCISE selection

Rather than fabricate the other 9 slot types' content (out of scope) to force a full
book through, this lane isolated the EXERCISE-slot mechanism using the **exact same
real, unmocked production functions** `scripts/run_pipeline.py` →
`phoenix_v4.planning.enrichment_select.select_enrichment` calls internally for the
EXERCISE branch (`enrichment_select.py:2658-2780`), mirroring the sanctioned test
harness pattern already in the repo
(`tests/unit/planning/test_opd107_exercise_persona_fallthrough.py`):

1. `phoenix_v4.planning.registry_resolver._load_persona_atoms("educators", "burnout",
   engine="overwhelm")` — the real disk loader, unmocked.
2. `phoenix_v4.planning.enrichment_select._filter_practice_pool` /
   `_is_practice_atom` — the real OPD-107/PR#612 shape gate, unmocked.
3. `phoenix_v4.planning.enrichment_select._pick_primary_index_unseen` +
   `PersonaPoolRotationState` — the real deterministic slot-fill selector, unmocked.

Representative tuple: **`educators, burnout, overwhelm, F006`**

```json
{
  "tuple": "educators,burnout,overwhelm,F006",
  "raw_persona_exercise_pool_size": 24,
  "practice_shape_filtered_pool_size": 19,
  "practice_shape_pass_count": 19,
  "practice_shape_reject_count": 5,
  "resolved_source_for_slot": "persona_atom",
  "picked_atom_id": "EXERCISE v09",
  "picked_content_preview": "Rest your hands flat on your thighs. Press down firmly. Count to five. Release. Press again. Count to five. Release. Repeat four times. This is not one more tas",
  "would_fall_through_to_practice_library": false
}
```

`resolved_source_for_slot = "persona_atom"` — confirmed by the real code path: with
`tid=None` (no teacher overlay), `enrichment_select.py`'s EXERCISE branch reaches
`elif not _add_pieces and persona_atoms:` (line 2721), finds a non-empty
`_persona_ex_pool` after `_filter_practice_pool`, and **never reaches** the
`practice_library` fallback block (line 2774) — that block is only entered when
`_persona_ex_pool` is empty. **`educators-exercise-gap-native-proof = pass`.**

Confirmed for all 7 gap topics (real loader + real filter, non-empty in every case):

```
burnout:            raw=24 practice_shaped=19 -> persona_atom
financial_anxiety:  raw=21 practice_shaped=14 -> persona_atom
imposter_syndrome:  raw=20 practice_shaped=14 -> persona_atom
overthinking:        raw=20 practice_shaped=13 -> persona_atom
sleep_anxiety:       raw=20 practice_shaped=16 -> persona_atom
social_anxiety:      raw=20 practice_shaped=16 -> persona_atom
somatic_healing:     raw=20 practice_shaped=15 -> persona_atom
```

## 4. Scope discipline

- Did not touch `artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`.
- Did not touch `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`.
- Did not touch `SOURCE_OF_TRUTH/teacher_banks/**`.
- Did not touch any `nyc_executives` path.
- No planner/code changes. No fallback tuning. No translation. No manga.
- Did not author `atoms/educators/<topic>/SCENE/CANONICAL.txt` for any of the 7
  topics (flagged below as the next real gap, out of scope for this lane).

## 5. Cleanup ledger

- Scratch proof scripts written to session scratchpad only
  (`/private/tmp/.../scratchpad/educators_burnout_exercise_proof*.py`) — not committed,
  not part of repo tree.
- No temp files left in the repo working tree.

## 6. Known residual gap (informational, out of scope, not actioned here)

`atoms/educators/<topic>/SCENE/CANONICAL.txt` is absent for all 7 topics touched by
this lane (burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety,
social_anxiety, somatic_healing). This blocks a full `--render-book` production render
for these topics independent of EXERCISE. Recommend a separate SCENE-gap lane, scoped
and routed by Pearl_PM — not actioned here per `WRITE_SCOPE`.

# Lane 04 — Mutation checks (§14) — G-F1H / G-ORIENT / G-ACCENT

**Acceptance layer:** structurally clear (enforcement mechanisms; not a quality certification).

Protocol per gate: take a fixture that PASSes, deliberately mutate it into a
known violation, confirm the gate goes RED, revert the mutation, confirm the
gate returns to green. All three below were run interactively during
implementation (2026-07-19, PearlStar offline lane); commands and output are
reproduced verbatim.

## G-F1H — templated paragraph cluster ≥6 chapters HARD_FAIL

Fixture: a 5-paragraph-cluster book (chapters 1-5 share a templated opening
paragraph) — below the G-F1H limit (6) — then extended to 6 chapters.

```
$ PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py --book f1h_book.txt   # 5 chapters
G-F1H: PASS — f1h_book.txt has no cluster spanning >= 6 chapters
exit=0

# MUTATE: extend the same templated paragraph into a 6th chapter
$ PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py --book f1h_book.txt   # 6 chapters
G-F1H: HARD_FAIL
  - f1h_book.txt: G-F1H HARD_FAIL — templated paragraph cluster f1_cluster_000
    spans 6 chapters (>= 6) chapters=[1, 2, 3, 4, 5, 6] excerpt='You notice the
    tightness rise in your chest again today. It happens the same way every
    single time it arrives without wa...'
exit=1

# REVERT: back to 5 chapters
$ PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py --book f1h_book.txt
G-F1H: PASS — f1h_book.txt has no cluster spanning >= 6 chapters
exit=0
```

**Result: PASS -> mutate -> HARD_FAIL (RED, exit 1) -> revert -> PASS (green, exit 0).**
Permanent regression coverage: `tests/test_check_f1h_templated_cluster_hard.py`
(`test_cluster_below_limit_is_not_hard_fail`, `test_cluster_at_limit_is_hard_fail`,
`test_cluster_above_limit_is_hard_fail`).

## G-ORIENT — Ch1 first-120-words body/scene anchor (strict mode)

Fixture: a scene-first Ch1 opening (hand / phone / screen / bedroom / chest),
mutated into an abstract-philosophy-first opening with zero lexicon anchors.

```
$ PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book orient_book.txt --strict   # scene-first
G-ORIENT: PASS — Ch1 first 120 words satisfied via lexicon anchor 'hand'
exit=0

# MUTATE: rewrite Ch1 opening abstract-philosophy-first (no body/scene anchors)
$ PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book orient_book.txt --strict
G-ORIENT: FAIL (--strict)
  - orient_book.txt: G-ORIENT WARN — Ch1 first 120 words contain no approved
    body/scene lexicon anchor and no SCENE-atom provenance (authored-candidate
    eligibility at risk). window='Awareness is the foundation of every
    transformation a person can undertake in their life. Consciousness itself
    is the ground on which all growth occurs, philosophically speaking,
    across every traditio'
exit=1

# REVERT: restore the scene-first opening
$ PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book orient_book.txt --strict
G-ORIENT: PASS — Ch1 first 120 words satisfied via lexicon anchor 'hand'
exit=0
```

**Result: PASS -> mutate -> FAIL under --strict (RED, exit 1) -> revert -> PASS
(green, exit 0).** Default (non-strict) mode never blocks — matches spec's
"WARN->escalate to authored-candidate eligibility", not a Layer-1 hard gate.
Permanent regression coverage: `tests/test_check_orient_ch1_scene_anchor.py`.

## G-ACCENT — accent-fill preflight (capability gap detector)

Fixture: `corporate_managers x burnout` (the flagship pilot cell — known clean,
`accent_budget_overrides` in `config/accent/brand_accent_profiles.yaml`
guarantee full supply) checked against a `repo_root` copy with the
`SOURCE_OF_TRUTH` accent banks selectively symlinked to simulate a missing
supply pool.

```
$ python3 -c "... preflight_cell(persona_id='corporate_managers', topic_id='burnout', ..., repo_root=REAL_REPO) ..."
gaps: {}

# MUTATE: repo_root pointed at a copy of SOURCE_OF_TRUTH with a bank omitted
$ python3 -c "... preflight_cell(..., repo_root=MUTATED_REPO_COPY) ..."
gaps: {'ENCOURAGEMENT': 'no_supply_pool'}
has_gap: True

# REVERT: back to the real repo_root (mutated copy discarded)
$ python3 -c "... preflight_cell(..., repo_root=REAL_REPO) ..."
gaps: {}
```

**Result: no-gap -> mutate (bank pool hidden) -> gap detected (RED,
`has_gap=True`) -> revert -> no-gap (green) again.** This exercises the exact
`_capability_gaps()` function `validate_accent_plan()` calls at render time —
G-ACCENT does not re-implement gap detection, only orchestrates it across the
top-N MATRIX.tsv cells without a full render. Permanent regression coverage:
`tests/test_check_accent_supply_preflight.py`
(`test_known_clean_pilot_cell_has_no_gap`, `test_known_underfilled_cell_has_gap`).

Live (unmutated) run against the real top-20 MATRIX.tsv cells surfaced 14/20
cells with a real `no_supply_pool` gap for a budgeted accent class — see
`ACCENT_SUPPLY_PREFLIGHT_SAMPLE.json` in this directory. This is the exact
catalog-planning signal the spec's #3.B G-ACCENT row asked for
("Accent `no_supply_pool` hard-stops" finding in ANALYSIS_REPORT.md).

# Direct before/after — same cell, same seed, OLD code vs NEW code

Cell: burnout/overwhelm/corporate_managers · seed 4242 · `--pipeline-mode spine --quality-profile draft`

- OLD code = `git archive 29c3fd76bc` (#1677; the SHA #1676 built on; pre-#1683).
  `_resolve_angle_journey_id` ABSENT, scene-reducer "A1-generalize" ABSENT (verified grep count 0).
- NEW code = `git archive origin/main` @ bf69977a38 (post-#1683).

`OLD_scene_anchor_density_report_FAIL.json`: status FAIL — ch4 `"you are allowed to"` ×7 > cap 3.
`NEW_scene_anchor_density_report_PASS.json`: status PASS (reducer trimmed over-cap occurrences).

This is the gate the #1676 wave failed 0/3; the fix flips it to PASS.

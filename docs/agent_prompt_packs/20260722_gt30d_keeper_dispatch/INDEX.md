# gt30d Keeper Dispatch Pack — 2026-07-22

**Role split:** Claude writes/refreshes specs. Cursor implements code/CI against those specs.

**Source audit:** `artifacts/qa/archived_session_audit_gt30d_20260722/`

**Wave-A keepers (12):** I042, I043/I029, I034, I025/I048, I026, I005/I049, I006, I032, I045, I007, I001 (+ gated D06–D08).

**Excluded:** OPERATOR_GATE (I039, I044), DUPLICATE_OF_PRIOR_MINING (I008, I011, I016, I024, I040), parked Wave-B items.

## Lane matrix

| File | Owner | Wave | Keepers | Depends on | Signal |
|---|---|---|---|---|---|
| `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM | lead | — | — | paste this |
| `W0_Pearl_PM_reverify.md` | Pearl_PM | 0 | all 12 | none | `gt30d-keeper-reverify-terminal=<sha>` |
| `C01_manga_structural_composition_spec.md` | Claude | 1 | I042 | W0 | `gt30d-c01-spec-terminal=<sha>` |
| `C02_manga_passb_bar_packet_spec.md` | Claude | 1 | I043+I029 | W0 | `gt30d-c02-spec-terminal=<sha>` |
| `C03_storefront_buy_platform_spec.md` | Claude | 1 | I034 | W0 | `gt30d-c03-spec-terminal=<sha>` |
| `C04_atom_cohesion_spec1_refresh.md` | Claude | 1 | I025+I048 | W0 | `gt30d-c04-spec-terminal=<sha>` |
| `C05_music_mode_freebie_funnel_spec.md` | Claude | 1 | I026 | W0 | `gt30d-c05-spec-terminal=<sha>` |
| `C06_cover_five_layer_unify.md` | Claude | 1 | I005+I049 | W0 | `gt30d-c06-spec-terminal=<sha>` |
| `D01_family_id_enum_drift_gate.md` | Cursor | 2 | I006 | W0 | `gt30d-d01-code-terminal=<sha>` |
| `D02_angle_id_registry_join.md` | Cursor | 2 | I032 | W0 | `gt30d-d02-code-terminal=<sha>` |
| `D03_books_first_story_seeding.md` | Cursor | 2 | I045 | W0 | `gt30d-d03-code-terminal=<sha>` |
| `D04_catalog_knob_usage_analyzer.md` | Cursor | 2 | I007 | W0 | `gt30d-d04-code-terminal=<sha>` |
| `D05_author_resolution_wiring.md` | Cursor | 2 | I001 | W0 | `gt30d-d05-code-terminal=<sha>` |
| `D06_manga_structural_mvp_impl.md` | Cursor | 2g | I042 | C01 | `gt30d-d06-code-terminal=<sha>` |
| `D07_manga_lettering_bar_hooks.md` | Cursor | 2g | I029/I043 | C02 | `gt30d-d07-code-terminal=<sha>` |
| `D08_music_mode_freebie_wire.md` | Cursor | 2g | I026 | C05 | `gt30d-d08-code-terminal=<sha>` |
| `W3_Pearl_PM_final_audit.md` | Pearl_PM | 3 | all | all terminal | `gt30d-keeper-dispatch-final=<sha>` |
| `RUNNER_RESUME.md` | any | — | — | interrupted | resume |

## Operator order

1. Paste `00_MASTER_DISPATCH_PROMPT.md` into Pearl_PM.
2. Run W0.
3. Claude C01–C06 (max 3 concurrent).
4. Cursor D01–D05 after W0 (parallel OK).
5. Cursor D06–D08 only after matching Claude terminal SHA.
6. Run W3 final auditor.

## Wave-B (deferred — do not execute in this pack)

I015, I010, I030, I018, I003, I028, I031, I033, I041, I012, I038, I047, I019, I020, I021, I023.

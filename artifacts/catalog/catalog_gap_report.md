# Full Catalog Analysis Report

Generated: 2026-04-09T04:46:11Z

## Executive summary
- Live generator output: **8287** titles across **309** brand/lane pairs.
- Planned merged architecture: **37 brands/lane × 12 lanes = 444 brand instances**.
- Drift: generator is short by **135** brand/lane instances and still resolves legacy teacher brands rather than the merged 12×37 teacher-brand naming system.
- Missing global coverage: topics=0, personas=2, runtime_formats=4, content_types=deep_book.

## What was validated
- `scripts/catalog/generate_full_catalog.py` runs successfully on the clean branch.
- `phoenix_v4.ops.catalog_health_dashboard_builder` runs successfully and writes catalog health dashboard artifacts.
- `scripts/video/orchestrate_book_to_video.py --help` and `scripts/manga/run_chapter_production.py --help` both succeed, confirming live CLI entry points for video and manga assembly.
- Workstream state for `ws_brand_lane_architecture_20260407`: **completed** (Brand lane architecture (12×37), audiobook video pipeline, music bank, exercise system — PRs #295-298 all merged).

## Highest-signal gaps
- Missing topics globally: none.
- Missing personas globally: gen_alpha_students, gen_z_student.
- Missing runtime formats globally: deep_book_4h, deep_book_6h, extended_book_2h, micro_book_20.
- Missing content types globally: deep_book.

## Architecture drift
- Planned teacher brands missing from legacy generator: body_memory, cognitive_clarity, devotion_path, digital_ground, heart_balance, qi_foundation, relational_calm ...
- Legacy teacher brands not in new 12×37 plan: awakening_press, body_wisdom, cosmic_edge, gen_spark, gentle_wave, healing_ground_press, inner_light_press, iron_will ...

## Repurposing blockers
- practice_cli_missing_scripts_pearl_practice: 283 brand/lane rows
- brand_not_mapped_in_brand_cover_art_specs: 166 brand/lane rows
- brand_not_mapped_in_brand_series_plans: 166 brand/lane rows
- brand_not_mapped_in_brand_video_styles: 166 brand/lane rows

## Safe run posture
- Practice: `phoenix_v4.exercises.component_assembler.assemble_exercise_for_chapter` imports successfully, but the requested `scripts/pearl_practice/*` CLI surface is still absent on this branch; analysis can only mark template/library readiness.
- Video/audiobook video: config surface is present and mapped for current video lanes; actual media assembly still requires concrete audio/transcript inputs.
- Manga: merged planning/config surface exists, but many live catalog teacher brands do not map to the new manga plan brand IDs because the catalog generator is still on the legacy teacher-brand registry.

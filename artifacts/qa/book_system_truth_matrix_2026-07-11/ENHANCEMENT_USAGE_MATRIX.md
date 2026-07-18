# ENHANCEMENT_USAGE_MATRIX — book system truth matrix 2026-07-11

Operator-readable map of how each enhancement atom family shows up in **this** verification battery.
Tip: `8338e5f30dd9f7d9691179e359571f7d730ec100`. Acceptance max label: **system working** (not PROVEN-AT-BAR).

| Enhancement family | Mode / run that proves it | Source label (audit JSON) | Count(s) | Exact artifact path | Fresh current-main vs supporting mirror | What it does in the rendered book |
|---|---|---|---|---|---|---|
| `ANGLE_DEFINITION` | flagship regular | `source=angle_atom` / slot_type `ANGLE_DEFINITION` | 1 | `flagship_regular/section_packet_audit.json` | fresh current-main | Opens the book’s protective-alarm thesis once (source_id `angle_def:PROTECTIVE_ALARM`) so later chapters can callback to the same angle. |
| `ANGLE_CALLBACK` | flagship regular | `source=angle_atom` / slot_type `ANGLE_CALLBACK` | 11 | `flagship_regular/section_packet_audit.json` | fresh current-main | Re-anchors chapters 2–12 to the same angle layers (`angle_cb:PROTECTIVE_ALARM:L*`) without re-defining the thesis. |
| `STORY via story_plan` | flagship regular (+ music) | `source=story_plan` / slot_type `STORY` | 36 | `flagship_regular/section_packet_audit.json`; ids also in `enrichment_audit.json` → `book_slot_tracker_used_ids` / `story_schedule` | fresh current-main | Supplies twelve-shape recognition / mechanism / turning-point / embodiment story beats (Priya continuum) between doctrine and exercises. |
| `COMPOSITE_DOCTRINE / composite_doctrine` | flagship regular (+ music) | `source=composite_doctrine` / slot_type `REFLECTION`; enrichment `slots_from_composite` | 12 reflections; `slots_from_composite=12` | `flagship_regular/section_packet_audit.json`; `flagship_regular/enrichment_audit.json` | fresh current-main | Fills each chapter’s REFLECTION with composite doctrine prose (`COMPOSITE_DOCTRINE v03`) — the regular path still carries composite doctrine enhancements. |
| `EXERCISE_JOURNEYS` | flagship regular (`--exercise-journeys`) | enrichment key `exercise_journeys` | 12 journeys (all `2_step`) | `flagship_regular/enrichment_audit.json` | fresh current-main | Plans a two-step practice sequence per chapter (e.g. sensation_tracking → breath_anchor) so exercises follow an outcome journey rather than a lone drill. |
| `EXERCISE body source = practice_library` | flagship regular (+ music) | `source=practice_library` / slot_type `EXERCISE`; enrichment `slots_from_practice_library` | 12 | `flagship_regular/section_packet_audit.json`; `flagship_regular/enrichment_audit.json` | fresh current-main | Materializes each chapter EXERCISE body from the practice library (e.g. `med_007`), not from teacher/persona banks on this regular surface. |
| `EXERCISE body source = teacher_atom` | teacher compile smoke PASS; fresh teacher render FAIL; historical joshin mirror | enrichment `slots_from_teacher` (historical) | fresh anxiety×kenjin×extended_book_2h: **0 / blocked**; historical joshin mirror: `slots_from_teacher=48` | `teacher_kenjin/teacher_coverage_report.json`; supporting `artifacts/qa/proprime_modes_100pct_20260711/teacher_mode_render/enrichment_audit.json` (local mirror, not on tip) | compile = fresh tests; teacher EXERCISE atoms = supporting historical mirror only | On a covered teacher compile (burnout smoke), teacher-mode plans bind teacher atoms; on this anxiety×kenjin production chord the coverage gate blocks before render, so no fresh teacher EXERCISE bodies were produced. |
| `EXERCISE body source = persona_atom` | not on EXERCISE slots of proven flagship/music surfaces | n/a for EXERCISE (persona fills HOOK/SCENE/PIVOT/TAKEAWAY/INTEGRATION/THREAD) | EXERCISE persona_atom count = **0**; persona_atom non-EXERCISE = 72 slot rows / `slots_from_persona=108` | `flagship_regular/section_packet_audit.json`; `flagship_regular/enrichment_audit.json` | fresh current-main | Persona atoms drive the non-story spine slots; EXERCISE bodies on this surface come from `practice_library`, not persona. |
| `teacher_atom` outside EXERCISE | teacher compile smoke; historical joshin mirror | plan `teacher_mode=true` / historical enrichment | smoke: plan asserts teacher_mode + teacher_id; historical slots_from_teacher includes non-EXERCISE teacher fills | `teacher_pytest.txt`; historical `.../teacher_mode_render/enrichment_audit.json` | compile fresh; full outside-EXERCISE teacher fill = supporting mirror | Teacher-mode compile still wires `teacher_id` into the plan without placeholders; full outside-EXERCISE teacher slot fill is evidenced by the prior modes mirror, not by this blocked anxiety×kenjin chord render. |
| accent families on tested flagship | flagship regular + CLI accent truth gate | `accent_budget` / `assignment_counts` / `rendered_accent_audit.accents` | budget+assign: ENCOURAGEMENT 2, CITED_EVIDENCE 1, EXTERNAL_STORY 2, WISDOM_ESSENCE 1, AUTHOR_COMMENTARY 1 (total 7) | `flagship_regular/rendered_accent_audit.json`; `ACCENT_FLAGSHIP_TRUTH_GATE_fresh.json` | fresh current-main | Injects seven planner-placed accent beats (permission encouragements, cited evidence, external stories, wisdom essence, author commentary) at allowed positions around HOOK/turning_point/REFLECTION/THREAD. |
| `music_overlay` injections | music ahjan render | `music_overlay_audit.json` → `applied=true`, `injection_summary.injection_points` | 12 chapters × 6 markers = **72** injections (`with-lyrics` / musician `ahjan`) | `music_ahjan/music_overlay_audit.json` | fresh current-main | Overlays lyric + music-reflection markers at opening / bestseller_beat / closing for every chapter so the manuscript carries the music-mode surface. |
| durable EPUB packaging surface | Waystream burnout EPUB on tip | EPUB ZIP package (mimetype / container / OPF / xhtml) | 1 EPUB / 21 zip members / 12 chapters | `artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub`; inspection `waystream_epub_inspection.md` | tip artifact (not freshly rebuilt) | Proves packaging still yields a real readable EPUB (“After the Flame…”) without requiring a fresh burnout rebuild. |

### Accent IDs actually rendered (flagship fresh)

- `enc_gen_z_professionals_anxiety_permission_v12`
- `enc_gen_z_professionals_anxiety_permission_v18`
- `anx_emotion_differentiation_kashdan_2010`
- `ext_anx_ted_mcgonigal_stress_v01`
- `ext_anx_storycorps_911_v01`
- `we_anx_standing_down_permission_v01`
- `ac_ravi_anxiety_admission_body_lead_v01`

### Exercise journeys (flagship fresh)

- ch1: thesis=`unnamed_feeling` type=`2_step` ids=['sensation_tracking_v1', 'breath_anchor_v1']
- ch2: thesis=`unnamed_feeling` type=`2_step` ids=['sensation_tracking_v1', 'extended_exhale_v2']
- ch3: thesis=`emotional_overwhelm` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch4: thesis=`anxiety_spike` type=`2_step` ids=['sensation_tracking_v1', 'extended_exhale_v2']
- ch5: thesis=`unnamed_feeling` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch6: thesis=`anxiety_spike` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch7: thesis=`emotional_overwhelm` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch8: thesis=`emotional_overwhelm` type=`2_step` ids=['sensation_tracking_v1', 'extended_exhale_v2']
- ch9: thesis=`emotional_overwhelm` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch10: thesis=`unnamed_feeling` type=`2_step` ids=['sensation_tracking_v1', 'breath_anchor_v1']
- ch11: thesis=`emotional_overwhelm` type=`2_step` ids=['body_scan_v1', 'extended_exhale_v2']
- ch12: thesis=`emotional_overwhelm` type=`2_step` ids=['sensation_tracking_v1', 'breath_anchor_v1']

# US Illustrated Self-Help Pilot — Phase A registry note

**Date:** 2026-07-08 (recreated 2026-07-19 for D-4 closure)  
**Lane:** `western_intent_led` / `illustrated_self_help_picture_books`  
**Master format:** `direct_self_help_illustrated`  
**Authority consumers:** `config/manga/us_illustrated_pilot_cells.yaml`, `config/manga/western_cartoon_styles.yaml`, `scripts/ci/check_western_lane_format.py`

## Phase A (PLAN stubs — landed)

Five en_US pilot series plans with working titles:

| brand_id (short) | Path X / alias | working title | stub |
|------------------|----------------|---------------|------|
| stillness_press | stillness_press | The Alarm Is Lying | `stillness_press__en_US__iyashikei__illustrated_pilot01.yaml` |
| digital_ground | digital_ground | Notification-Free Zone | `digital_ground__en_US__workplace_drama__illustrated_pilot01.yaml` |
| cognitive_clarity | cognitive_clarity | Thought Loops: A Field Guide | `cognitive_clarity__en_US__psychological_thriller__illustrated_pilot01.yaml` |
| healing_ground | healing_ground_healing | The Midday Reset | `healing_ground__en_US__supernatural_mystery__illustrated_pilot01.yaml` |
| calm_student | calm_student_school | Before the Exam | `calm_student__en_US__school_coming_of_age__illustrated_pilot01.yaml` |

## Wave 2→3 expansion (PLAN — landed 2026-07-19)

- Fan-out pilots → illustrated-required western locales: `scripts/manga/fanout_illustrated_pilots.py`
- Full 37 Path X brands × illustrated-required locales: `scripts/manga/fanout_illustrated_all_brands.py`
- Matrix evidence: `artifacts/qa/worldwide_plan_completeness/LATEST/` (`illustrated` COMPLETE=296)

## Phase B (not claimed here)

Wire western cartoon styles into Pearl Star illustration dispatch; author chapter scripts; render illustrated-essay pages; blind-judge PROVEN-AT-BAR sample. **Out of scope for PLAN-complete worldwide.**

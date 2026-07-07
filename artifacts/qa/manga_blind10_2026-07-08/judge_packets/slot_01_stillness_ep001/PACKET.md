# Slot 01 — Judge packet assembly (stillness_press ep_001 pilot)

**Slot:** 01 · **Genre:** iyashikei · **Locale:** en_US
**Eligibility:** `prescreen_only` until M5 bank re-render at 0 INTERIM
**Render path:** `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v3_qwen/`

---

## Episode manifest

| Field | Value |
|---|---|
| series_id | `stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying` |
| episode | ep_001 |
| panel_count | 35 |
| panel_glob | `ep_001_seg_*.jpg` |
| script | `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml` |
| bytes verified | min 99,690 — all panels ≥ 50_000 |
| assembly note | Legacy V3 composed path (April tree). **Not** M5 bank assembly. Prefer slot_02 when available. |

---

## Operator assembly steps

1. **Pre-screen first** — `pre_screen/PRESCREEN_RUNBOOK.md` (Tier 2). Withhold from judges if FAIL.
2. Export 35 panels in story order (`seg_001` … `seg_035`) to `panels/` subfolder or single PDF.
3. Source comparators from `COMPARATOR_REGISTRY.yaml` slot `01` (Yotsuba&!, Barakamon excerpts).
4. Build blind triplet presentation; record `presentation_seed` in scorecard.
5. Distribute `README_FOR_JUDGE.md` + blank `TEMPLATE_scorecard.yaml` copy.
6. Collect ≥ 3 completed scorecards → `scorecards/`.

---

## Comparators (see parent registry)

- **comp_01_a:** Yotsuba&! Vol 1 Ch1 pages 5–8
- **comp_01_b:** Barakamon Vol 1 Ch1 pages 6–10

---

## Do not ship to judges

- `demo_alarm_metaphor_6p` (6-panel excerpt, INTERIM layers)
- `mira_pulid_character_strip` (character sheet, not episode)
- `composition_grammar_pilot` (4-panel grammar demo)

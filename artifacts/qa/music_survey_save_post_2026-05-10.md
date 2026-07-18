# QA — Music survey save POST (`ws_music_brand_survey_save_post_yaml_advance_20260509`)

**Date:** 2026-05-10  
**Branch:** `agent/music-survey-save-post-20260510`  
**Spec:** `docs/specs/MUSIC_MODE_BRAND_INTEGRATION_V1_SPEC.md` §3

## Implementation

- **Handler:** `brand-wizard-app/server/music_survey_save_handler.py` — validates `wizard_session_id` and `survey_responses`, loads `brands/<id>.yaml` (empty root if missing), shallow-merges into `musician_reflections`, writes YAML via temp file + `os.replace`.
- **HTTP:** `brand-wizard-app/server/music_survey_routes.py` — FastAPI `POST /wizard/music-survey/save`.
- **Tests:** `tests/brand_wizard/test_music_survey_save_handler.py` (8 cases).

## Run the API locally

From repository root:

```bash
uvicorn music_survey_routes:app --app-dir brand-wizard-app/server --reload --port 8787
```

YAML files are written under `brand-wizard-app/brands/` (directory created on first save).

## cURL sample

```bash
curl -sS -X POST "http://127.0.0.1:8787/wizard/music-survey/save" \
  -H "Content-Type: application/json" \
  -d '{
    "wizard_session_id": "music_demo_sess_01",
    "survey_responses": {
      "display_name": "River Stone",
      "primary_genre": "ambient",
      "ai_reflections_consent": true
    }
  }' | python3 -m json.tool
```

**Expected JSON:**

```json
{
  "status": "saved",
  "next_step": "step5",
  "yaml_path": "brands/music_demo_sess_01.yaml"
}
```

## Sample YAML after save

```yaml
musician_reflections:
  display_name: River Stone
  primary_genre: ambient
  ai_reflections_consent: true
```

A second POST with the same `wizard_session_id` merges new keys and overwrites overlapping keys in `musician_reflections`; other top-level wizard keys are preserved.

## Malformed input

- Non-object `survey_responses` → **422** with detail text.
- Invalid `wizard_session_id` (empty, path-like segments, or characters outside the allowed set) → **422**.

## pytest

```bash
PYTHONPATH=. python3 -m pytest tests/brand_wizard/test_music_survey_save_handler.py -q
```

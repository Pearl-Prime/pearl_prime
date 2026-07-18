# Music wizard live embed routing — QA / impl notes (2026-05-10)

Workstream: `ws_music_brand_wizard_live_embed_routing_20260509` (MUSIC-MODE-BRAND-INTEGRATION-V1-01 #975 amendment). Stacks on PR #1009 (`agent/music-survey-save-post-20260510`).

## Behavior

- **GET** `/wizard/step/music-survey` serves static musician reflections survey HTML with `?locale=en|ja|zh-tw|zh-cn` (default `en` when omitted).
- Resolution order (per root): `brand-wizard-app/dist/musician_reflections_survey-{locale}.html`, then for `en` also `musician_reflections_survey.html`, then for any supported locale a **synthesized** variant from `musician_reflections_survey.html` with `<meta name="pearl-music-survey-locale" content="…">` and adjusted `<html lang>`, so CI and shallow checkouts still get four locale responses when only the canonical English bundle exists.
- **Unknown** `?locale=` → **404**. **No bundle on disk** (with `BRAND_WIZARD_MUSIC_SURVEY_ROOT` + `BRAND_WIZARD_MUSIC_SURVEY_ROOT_EXCLUSIVE=1` used in tests) → **503** HTML stub (graceful degradation).
- **POST** `/wizard/music-survey/save` unchanged (#1009 handler).

## Frontend

- `brand-wizard-app/src/components/MusicSurveyPane.jsx` embeds the survey via **same-origin** `iframe` `src=/wizard/step/music-survey?locale=…` (wizard i18n `ja` → `ja`, `zh` → `zh-cn`, `tw` → `zh-tw`, default `en`).
- **Deprecated:** loading the survey via **`file://`** URLs (or any non-same-origin copy of the HTML) — breaks POST to `/wizard/music-survey/save`, bypasses wizard session context, and drifts from the served bundle. Prefer the live route above or a reverse-proxied path on the wizard origin.

## Ops / smoke

```bash
uvicorn music_survey_routes:app --app-dir brand-wizard-app/server --port 8787
curl -sS "http://127.0.0.1:8787/wizard/step/music-survey?locale=ja" | head
```

Expect `200` and HTML containing `pearl-music-survey-locale`.

## Tests

`PYTHONPATH=. python3 -m pytest tests/brand_wizard/test_music_survey_live_routing.py -v`

## Anti-drift (docs)

Any procedure that still references **`file://`** paths to `musician_reflections_survey*.html` should be treated as **deprecated** in favor of this route (or an equivalent same-origin proxied URL).

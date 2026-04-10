# Pearl Prime — Manga Pipeline (complete operator guide)

**Production:** `scripts/manga/run_chapter_production.py`  
**ITE:** `scripts/manga/ite_*.py`  
**Registry:** `config/pipeline_registry.yaml` → `pipelines.manga`  
**Specs:** `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`

---

## Before you start

1. `python3 scripts/pipeline/create_job.py --pipeline manga --teacher … --topic … --brand … --genre … --locale … --workspace <CHAPTER_ROOT>`
2. `python3 scripts/pipeline/acknowledge_guide.py --workspace <CHAPTER_ROOT>`
3. Run **chapter_production** then **ITE** stages in registry order.

---

## Stages

| Stage | Script | Notes |
|-------|--------|-------|
| chapter_production | `run_chapter_production.py` | Prompts, manifest, lettering |
| ite_breath | `ite_panel_breath.py` | Breath sequences |
| ite_gutter | `ite_gutter_therapy.py` | Gutter therapy |
| ite_color_arc | `ite_color_arc.py` | Color temperature arc |
| ite_fractal | `ite_fractal_check.py` | Fractal regulation |
| ite_qc | `ite_qc.py` | T-01–T-20 gates |
| webtoon_pack | `build_manga_webtoon.py` | Optional packaging |

---

## Config map

| Path | Role |
|------|------|
| `config/manga/teacher_character_prompts.yaml` | Per-teacher visual style |
| `config/manga/genre_ite_profiles.yaml` | Genre ITE parameters |
| `config/manga/panel_layouts.yaml` | Layout templates |
| `config/manga/brand_illustration_styles.yaml` | Brand visual tokens |

---

## Common mistakes

- Using **`noop`** backend then expecting real panels — use `replay` + real PNG map or remote image backend.
- Running **ITE QC** before gutter/breath/color artifacts exist.
- Ignoring **teacher_character_prompts** — style must match teacher + genre.

---

## Example

```bash
PYTHONPATH=. python3 scripts/manga/run_chapter_production.py chapter_script.json \
  --workspace artifacts/manga_samples/my_chapter/ --backend replay --replay-map map.json
```

Add `--workspace` (job directory) consistently for ITE scripts; default is parent of `-o`.

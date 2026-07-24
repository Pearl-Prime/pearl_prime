# Manga editor — Stage A evidence commands

Stage B only runs after Stage A PASS.

```bash
PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
  --story-handoff artifacts/manga/chapter_scripts/<series>/story_architecture_handoff.json \
  --chapter-script artifacts/manga/chapter_scripts/<series>/<ep>.yaml \
  --production --json --out artifacts/manga/editor_reviews/<series>/<ep>.gate_report.json
```

Story-authored precondition (writer should already have cleared this):

```bash
PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py \
  --series <series> --episode <ep>
```

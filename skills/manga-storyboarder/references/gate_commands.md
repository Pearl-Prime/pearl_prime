# Manga storyboarder — gate commands

```bash
PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \
  --arc-plan artifacts/manga/arc_storyboards/<series>/<ep>.arc_storyboard.yaml
```

Golden smoke (Lane 08 validation target):

```bash
PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \
  --arc-plan artifacts/manga/arc_storyboards/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.arc_storyboard.yaml
```

Bank demand rollup (Lane 09 tooling — after board + gaps exist):

```bash
PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \
  --help   # confirm --series-rollup flag on current main
```

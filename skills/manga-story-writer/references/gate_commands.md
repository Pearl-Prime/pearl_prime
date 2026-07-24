# Manga story-writer — gate commands

Series / episode tokens below are placeholders.

## Story-authored (render-entry)

```bash
PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py \
  --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \
  --episode ep_001
```

Or single file:

```bash
PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py \
  --chapter-script artifacts/manga/chapter_scripts/<series>/<ep>.yaml
```

## Excellence (Stage A — machine floor)

```bash
PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
  --story-handoff artifacts/manga/chapter_scripts/<series>/story_architecture_handoff.json \
  --chapter-script artifacts/manga/chapter_scripts/<series>/<ep>.yaml \
  --production
```

Exit: `0` PASS, `1` WARN/malformed, `2` BLOCKED. Production path requires ≥85 and
all hard gates (including `MANGA.STORY.GENRE_CRAFT_CHECKLIST`).

## Checklist sources (do not fork)

- `config/manga/genre_craft_checklists.yaml`
- `config/manga/mc_endurance_checklists.yaml` (via checklist `mc_items` keys)
- Spec: `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` §Editor pass

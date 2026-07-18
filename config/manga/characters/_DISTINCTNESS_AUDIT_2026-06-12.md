# Manga V2 Phase A — Character Distinctness Audit (2026-06-12)

**Harness:** `scripts/manga/character_individuation/constraint_solver.py` (spec §2.2 —
5-same-brand / 7-cross-brand locked-axis collision thresholds; lockout_minimum=9).
**Scope:** the named recurring teacher cast (12-core + 2 extended roster) + canonical Mira (`stillness_en_01`).

## Result: 14 / 14 ACCEPT — 100% collision-free (prompt-stack / axis distinctness)

Every character carries 9 locked axes and collides with **no** other character at the solver
thresholds. This is the **$0/local prompt-stack distinctness** — the design-axis proxy for the
spec's ~70% target (comfortably clears it at the design layer). It is NOT the facenet
face-distance % (spec §2.5), which needs rendered reference sheets and is Phase-B/endpoint-gated.

```
$ python3 scripts/manga/character_individuation/constraint_solver.py \
    --validate-all \
    --profiles-dir <13 new teacher designs + stillness_en_01.yaml> \
    --axes-config config/manga/character_design_axes.yaml

ACCEPT bright_presence_tw_seinen_01 (bright_presence_tw) — 9 locked axes
ACCEPT heart_transmission_en_01 (heart_transmission) — 9 locked axes
ACCEPT cognitive_clarity_seinen (cognitive_clarity) — 9 locked axes
ACCEPT heart_balance_maat_recurring (heart_balance) — 9 locked axes
ACCEPT qi_foundation_quiet_hands (qi_foundation_cultivation) — 9 locked axes
ACCEPT sleeprest_en_01 (sleep_restoration) — 9 locked axes
ACCEPT warrior_calm_cultivation (warrior_calm) — 9 locked axes
ACCEPT digital_ground_manhwa (digital_ground) — 9 locked axes
ACCEPT relational_calm_iyashikei (relational_calm) — 9 locked axes
ACCEPT body_memory_en_01 (body_memory) — 9 locked axes
ACCEPT somatic_wisdom_en_01 (somatic_wisdom) — 9 locked axes
ACCEPT solar_return_quiet_embers (solar_return) — 9 locked axes
ACCEPT devotion_path_shonen (devotion_path) — 9 locked axes
ACCEPT stillness_en_01 (stillness_press) — 9 locked axes
```

## Caveats / next
- These 13 designs are **operator-review-pending best-guess autofills** — see the per-axis
  `# OPERATOR-CONFIRM:` flags + `solver.operator_confirmation: required` in each
  `config/manga/characters/<id>.character_design.yaml` (8–26 flags/teacher).
- These live in `config/manga/characters/` as standalone teacher-design seeds; attaching them
  to series YAMLs (or pointing the catalog solver at this dir) is a follow-up.
- The facenet face-distance gate (spec §2.5) is the rendered-image check — Phase B, after PuLID
  reference sheets exist and Pearl Star is online. Deps: `requirements-manga-qa.txt`.

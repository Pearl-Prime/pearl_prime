# Lane 03 Handoff — Empirical Arc-Cadence Research (2026-07-24)

**Lane:** manga process uplift Lane 03 (Pearl_Research) · **Status:** landed (see PR referenced
in closeout) · **Signal:** `manga-arc-cadence-research-merged=<merge SHA in closeout>`

## What landed

1. `artifacts/research/manga_arc_cadence_study_2026-07-24.md` — empirical arc-cadence study:
   all 21 pacing genre families + webtoon lanes, ≥3 named series each from `reference_corpus[]`,
   roll-up table, per-family confidence, sources footer. Evidence tiers marked
   (live-verified vs corpus-derived).
2. `config/manga/manga_pacing_by_genre.yaml` — **additive `arc_cadence` block on all 21
   families** (0 existing lines changed; `diff` vs origin/main shows insertions only). Keys:
   `episodes_per_arc_range` [min,max], `episodes_per_arc_median`, `arc_pattern`
   (fixed|escalating|seasonal_cycle), `season_unit` (int or null + inline comment),
   `first_major_shift_by` (int or null), `arc_cadence_confidence` (high×6 / medium×11 / low×4),
   `arc_cadence_sources[]`, `notes`. Consumer test `tests/manga/test_manga_pacing_yaml.py`
   passes 8/8 unmodified.
3. Craft-bible §7 corrections (dated, one-block, additive — no silent rewrites):
   - `docs/research/manga_craft/webtoon_vertical_romance.md` §7 — "season of ~25 episodes"
     contradicted: verified platform seasons run 78–115+ eps (ToG S1=78, Lore Olympus S1=115,
     Solo Leveling S1≈110).
   - `docs/research/manga_craft/webtoon_vertical_drama.md` §7 — arc grain 20–30 eps confirmed;
     equating it with a platform *season* contradicted (78+ eps).
   No other §7 assertion was contradicted by the evidence (action_battle/sports/shojo/seinen/
   iyashikei §7 shapes are prescriptive groupings above the arc grain, or confirmed).

## For Lane 06 (100-episode master-plan contract) — the consumer this block gates

- Consume `episodes_per_arc_range` + `arc_pattern` + `first_major_shift_by` per family; the
  study's "Cross-family findings" section gives the segmentation logic: three cadence regimes
  (escalating / fixed-unit / calendar) need three segmentation functions.
- **`first_major_shift_by: null` is a semantics, not a gap** — healing, horror,
  supernatural_everyday, gag, essay have no status-quo-shift convention; forcing a shift breaks
  the genre contract. Branch on null; do not default it to a number.
- Monthly-chapter genres (fantasy, romance, school) have systematically lower arc episode-counts
  at equal story mass (40–60-page chapters); do not compare across serialization cadence 1:1.

## Named follow-ups (owner: dispatcher to route)

1. **No webtoon family row in `manga_pacing_by_genre.yaml`** — webtoon_vertical_romance/_drama
   exist as craft bibles only; webtoon-format series currently inherit print-family cadence.
   Evidence (season 78–115+ eps, arc 15–30 eps, cliff-per-episode) is in the study §Webtoon,
   ready to be turned into family rows + aliases if/when a webtoon lane ships.
2. **cultivation_martial confidence: low** — manhua arc boundaries are poorly indexed in English;
   verify `episodes_per_arc_range` against zh-language chapter indexes when zh lanes are active.
3. **essay / memoir / graphic_medicine confidence: low** — corpus is single/few-volume works; no
   100-episode long-runner exists in these families anywhere in the market evidence. Lane 06
   plans there are explicit inference; consider capping those families at shorter series
   contracts (24–48 eps) rather than 100.
4. `docs/research/manga_craft/index.md` "Canonical 48-volume shapes summary" repeats the
   webtoon ~25-ep season figure ("48 seasons × ~25 episodes") — index.md is a HOT FILE out of
   Lane 03 scope; request the one-line index correction via dispatcher (same citation set as the
   two bible corrections).

## Cleanup ledger

- Scratchpad only: `<scratchpad>/lane03/` (builder script, base snapshots, YAML variants) —
  session-local, auto-cleaned, nothing to remove from the repo.
- No temp branches beyond the PR branch; no worktrees created; shared checkout untouched
  (plumbing pattern — no branch switch, no working-tree writes).

## Verification receipts

- Additive-only gate: `diff <(git show origin/main:config/manga/manga_pacing_by_genre.yaml) <built>`
  → 0 removed lines (run at smoke, pilot, scale).
- `python3 -m pytest tests/manga/test_manga_pacing_yaml.py` → 8 passed (consumer test, unmodified).
- Schema self-check: all 21 families carry the 8 block keys; enum values validated; every family
  ≥2 sources.
- Live-verified anchors (2026-07-24): One Piece arc spans, Demon Slayer arc chapter ranges, JJK
  Shibuya 79–136, MHA PLW 253–306, Vinland Saga 1–54/55–99/100–166/167+, ToG S1=78,
  Lore Olympus S1=115, Solo Leveling S1≈110/179.

# Manga Story Excellence Realization Gate Spec

Status: v0.2 CODE-WIRED (EXECUTED-REAL for fixture/audit runs; not PROVEN-AT-BAR)
Owner: Pearl Research / Manga Story Governance
Created: 2026-07-18
Related QA: `artifacts/qa/manga_modern_reader_doctrine_verification_20260718/VERIFICATION_REPORT.md`
Implementation: `phoenix_v4/manga/story_quality/excellence_gate.py`, `scripts/manga/validate_story_excellence.py`, registry rows under `config/manga/gate_registry.yaml`

## Purpose

This spec closes the remaining story-quality gap: manga scripts can currently
validate as JSON and still read as bland, generic, or genre-wrong. The fix is a
post-writer, pre-visual production gate that proves the final script actually
realizes the research-backed story doctrine on the page.

The gate must enforce this formula:

```text
genre-core pleasure
+ contemporary reader-world catalyst
+ protagonist desire and cost
+ relationship / interaction pressure
+ page-one hook and page-two reversal or discovery
+ market-native specificity
+ no generic fallback language
```

This is not a replacement for the existing story strategy banks,
`modern_reader_context`, interaction grammar, scene templates, or chapter
writer prompt. It is the runtime proof that those upstream instructions made it
into the final story.

## Non-Goals

- Do not make one universal manga template.
- Do not force every genre to use an app, phone, train, or game.
- Do not let trend surfaces replace genre craft.
- Do not score "awesome" by schema validity alone.
- Do not block quiet genres for being quiet. Healing, memoir, essay, and
  slice-of-life pass through concrete low-arousal story movement, not explosions.

## Existing Authorities

The implementation must treat these as source-of-truth inputs:

- `config/manga/canonical_genre_list.yaml`: canonical 25-genre coverage.
- `config/manga/modern_reader_story_doctrine.yaml`: market/audience surfaces,
  genre catalysts, avoid lists, quality rubric.
- `phoenix_v4/manga/modern_reader_context.py`: runtime doctrine loader,
  validator, genre resolver, and deterministic catalyst builder.
- `config/source_of_truth/manga_story_strategies/*_strategies.yaml`: layered
  genre craft banks.
- `config/source_of_truth/manga_story_strategies/combinatorial_index.yaml`:
  strategy-bank coverage and anti-pattern index.
- `config/manga/main_character_interaction_grammar.yaml`: genre-native
  interaction and shot-distance grammar.
- `config/manga/genre_scene_templates/`: visual scene-template contracts where
  available.
- `phoenix_v4/manga/prompts/chapter_writer_prompt.txt`: writer-facing doctrine
  requirement.

## Pipeline Position

```text
research docs / strategy banks / doctrine
  -> story architect
  -> story_architecture_internal
  -> story_architecture_handoff
  -> chapter writer
  -> chapter_script_writer_handoff + chapter_script_internal_record
  -> STORY EXCELLENCE REALIZATION GATE
  -> prompt compiler / scene coverage / V5 render queue
  -> visual QA / publication package
```

Production rule:

```text
No production chapter may enter visual planning or rendering unless
MANGA.STORY.EXCELLENCE_REALIZATION returns PASS.
```

Stub/replay smoke runs may produce `WARN` reports, but production manifests
must mark them non-shipping.

## Artifact Contract

Add a new report artifact:

```text
artifact_type: manga_story_excellence_realization_report
schema_version: 1.0.0
```

Suggested path:

```text
<workspace>/story_excellence_realization_report.json
```

Suggested schema file:

```text
schemas/manga/story_excellence_realization_report.schema.json
```

Minimum JSON shape:

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "manga_story_excellence_realization_report",
  "status": "PASS",
  "production_blocking": false,
  "series_id": "series",
  "chapter_id": "ch01",
  "chapter_number": 1,
  "genre_id": "dark_fantasy",
  "strategy_genre": "dark_fantasy",
  "relevance_genre": "dark_fantasy",
  "target_market": "ja_JP",
  "target_audience": "gen_z",
  "score": 92,
  "threshold": 85,
  "gates": [
    {
      "gate_id": "MANGA.STORY.MODERN_READER_REALIZATION",
      "status": "PASS",
      "score": 100,
      "threshold": 100,
      "blocking": true,
      "issues": [],
      "evidence": [
        {
          "path": "pages[0].panels[1].dialogue[0].text",
          "text": "The app opens only after the last train leaves.",
          "reason": "selected catalyst object appears in page-one action"
        }
      ]
    }
  ],
  "repair_packet": null
}
```

Allowed top-level `status` values:

- `PASS`: all hard gates pass and score threshold is met.
- `WARN`: non-production or pilot-only concerns exist, no hard gate failed.
- `BLOCKED`: at least one hard gate failed.

## Gate IDs

### `MANGA.STORY.RESEARCH_DOCTRINE_COVERAGE`

Purpose: prove research-backed doctrine exists for the requested genre before
story generation is trusted.

Hard checks:

- canonical genre resolves to one of the 25 required genres;
- modern reader doctrine validates with `validate_modern_reader_doctrine()`;
- requested `reader_market` resolves to `en_US`, `ja_JP`, `zh_CN`, or `fr_FR`;
- requested audience resolves to `gen_z` or `gen_alpha`;
- genre row has `relevance_rule`, at least two catalysts, `ordinary_world_objects`,
  `genre_transmutation`, and `avoid`;
- strategy bank or approved alias exists for the genre;
- interaction grammar exists for the genre or approved alias.

Failure examples:

- `missing_modern_reader_genre_row`
- `missing_strategy_bank_or_alias`
- `missing_interaction_grammar`
- `malformed_doctrine`

### `MANGA.STORY.ARCHITECT_CONTEXT`

Purpose: prove the story architect actually carried doctrine into the writer
handoff.

Hard checks:

- `story_architecture_internal.modern_reader_context` exists;
- each chapter has `story_craft.modern_reader_context`;
- `story_architecture_handoff.modern_reader_context` exists;
- `reader_market` and `reader_audience` are preserved;
- `story_strategy_id` and `story_strategy_genre` are preserved;
- `chapter_writer_prompt` still contains the mandatory modern-reader language.

Failure examples:

- `missing_story_craft`
- `missing_modern_reader_context`
- `reader_market_dropped_in_transmission`

### `MANGA.STORY.ALIAS_COHERENCE`

Purpose: stop accidental drift between canonical genre, strategy genre, visual
genre, and relevance genre.

Add a small allowlist config:

```text
config/manga/story_genre_alias_coherence.yaml
```

Required row shape:

```yaml
- canonical_genre: mystery
  allowed_strategy_genres: [supernatural_mystery, mystery]
  allowed_relevance_genres: [mystery]
  allowed_vessel_genres: [supernatural_mystery]
  rationale: "Mystery currently uses supernatural-mystery story bank while retaining mystery-specific modern evidence logic."
```

Hard checks:

- `(canonical_genre, strategy_genre, relevance_genre)` must appear in the
  allowlist;
- if mode vessels are used, `(canonical_genre, vessel_genre)` must also be
  allowed;
- unresolved aliases are `BLOCKED`, not warnings.

### `MANGA.STORY.MODERN_READER_REALIZATION`

Purpose: prove the final script used the selected catalyst as story action, not
as a shallow name-drop.

Hard checks:

- first 1-2 pages contain at least one selected catalyst `ordinary_world_object`
  or approved market touchpoint;
- that object creates pressure, choice, cost, reversal, clue, intimacy,
  threat, or rule entry;
- `genre_transmutation` appears as visible action, dialogue pressure, or panel
  consequence;
- the modern object is not only in metadata, title, caption, or prompt text;
- at least one protagonist desire is visible before exposition-heavy lore;
- at least one social, system, body, or relationship cost appears by page two.

Shallow compliance examples that must fail:

- "She looked at her phone. Something shifted."
- "The train arrived and his adventure began."
- "They opened an app and entered a fantasy world" with no rule, cost, or choice.
- "A group chat existed" but no relationship pressure changed.

### `MANGA.STORY.GENRE_CORE_PLEASURE`

Purpose: prove the story gives the reader the thing that genre promises.

The implementation must use a per-genre core map. Initial required map:

| Genre | Required genre-core evidence |
|---|---|
| battle | trained body, rival/mentor/team pressure, public witness, visible cost |
| romance | proximity/delay, boundary, almost-confession or intimacy misread |
| workplace | institutional pressure, private mask leakage, coworker or system witness |
| healing | concrete ritual, low-arousal change, side-by-side attention, no lecture |
| mystery | evidence asymmetry, clue, witness/suspect pressure, timed reveal |
| horror | familiar thing made wrong, dread escalation before explanation |
| sports | body limitation, team/rival/coach axis, match/training cost |
| essay | visual artifact that structures self-interrogation |
| slice_of_life | tiny routine variation reveals care, belonging, or loneliness |
| fantasy_adventure | threshold, rule-bound world entry, quest cost |
| food | maker/eater/craft/taste memory between people |
| family | domestic task carrying role pressure and subtext |
| procedural | workflow evidence, method constraint, human/institutional cost |
| historical | period material culture, rank/duty constraint, historically bounded desire |
| comedy | setup, escalation, status flip, reaction consequence |
| cultivation | hierarchy, body discipline, false metric vs real breakthrough |
| mecha | pilot-machine-command triangle, cockpit body, mission cost |
| dark_fantasy | wound, oath/debt, survival choice, moral or bodily cost |
| sci_fi_cyberpunk | interface/system/body identity, privacy or algorithmic power |
| supernatural_everyday | liminal trace, etiquette, split perception, bittersweet residue |
| school | peer status weather, seating/chat/club pressure, belonging stakes |
| memoir | body state, memory artifact, revision, unresolved truth |
| social_issue | concrete access barrier, power relation, care network, named relationship |
| graphic_medicine | body evidence, care/clinic relationship, consent or agency |
| battle_internal | self-shadow, mirror/counterpart, body decision, moral turn |

Hard checks:

- at least two required evidence classes are present for the genre;
- no forbidden replacement occurs, such as "neon wallpaper" for cyberpunk or
  "therapy summary" for healing;
- genre-specific `avoid` items from `modern_reader_context.catalyst.avoid` are
  absent from the script text or prompt-facing scene notes.

### `MANGA.STORY.INTERACTION_REALIZATION`

Purpose: prove characters relate to each other in genre-native ways, and give
image planning enough interaction information.

Hard checks:

- main character has at least one genre-appropriate interaction archetype from
  `config/manga/main_character_interaction_grammar.yaml`;
- interaction target is explicit: dyad, rival, group, authority, team, family,
  crowd, patient/caregiver, machine/AI, system/interface, self/memory/body;
- shot distance or panel proximity matches the genre grammar when available;
- multi-character panels are declared as interaction scenes before visual prompt
  compilation;
- a story cannot pass with only solo internal narration unless the genre grammar
  explicitly allows it and a compensating artifact/system/self interaction is
  present.

Failure examples:

- `main_character_never_interacts`
- `romance_no_dyad_pressure`
- `sports_no_team_or_rival_axis`
- `mecha_no_machine_or_command_interaction`
- `social_issue_no_named_relationship`

### `MANGA.STORY.PAGE_ONE_HOOK`

Purpose: stop slow generic openings.

Hard checks:

- page one contains a concrete image, pressure, question, contradiction, or
  disruptive action;
- by the end of page two, the reader has a reason to turn the page: reversal,
  discovery, promise, threat, misread, challenge, or impossible object;
- opening cannot be only mood, weather, abstract theme, or backstory.

This gate may reuse and extend the existing `MANGA.CHAPTER.HOOK` behavior, but
must inspect the opening pages, not only the final hook.

### `MANGA.STORY.MARKET_NATIVE_SURFACE`

Purpose: make U.S., Japan, China, and France stories feel contemporary without
turning into stereotype, tourist scenery, or platform copy.

Hard checks:

- target market surface appears as concrete setting/object/social pressure;
- market guardrails are respected;
- no market-incoherent default is introduced;
- China market stories avoid direct political-system allegory in production
  unless explicitly approved;
- France market stories respect manga-literate/localized context rather than
  flat U.S. school import;
- Japan market stories avoid tourist-Japan default and preserve public/private
  register where relevant;
- U.S. market stories avoid fake-Japan surface when scene is U.S.-localized.

### `MANGA.STORY.BLAND_FALLBACK_LINT`

Purpose: block the exact failure mode where a story "passes" while sounding
like generic filler.

Hard checks:

- no canned stub dialogue markers;
- no repeated abstract closure phrases;
- no unresolved "something changed/shifted" lines without a concrete action;
- no chapter whose panel text is mostly generic emotional summary;
- no story where protagonist has no specific desire, choice, or cost.

Initial phrase bank should include configurable patterns such as:

```yaml
generic_phrases:
  - "something shifted"
  - "for the first time"
  - "the path ahead"
  - "a quiet strength"
  - "began to heal"
  - "everything changed"
  - "learned to trust"
  - "not alone anymore"
  - "a new dawn"
  - "the journey had only begun"
```

Important: phrase hits are not automatically fatal when surrounded by strong
specific action. They become fatal when the surrounding panel lacks concrete
object, choice, consequence, or relationship movement.

### `MANGA.STORY.REPAIR_PACKET`

Purpose: every blocked story must produce an executable repair brief.

For `BLOCKED`, report must include:

- failed gate IDs;
- exact script paths / panel locations;
- missing required evidence;
- selected catalyst and genre-core requirements;
- short repair instruction suitable for Pearl_Writer;
- `repair_scope`: `rewrite_opening_pages`, `rewrite_chapter`, or
  `regenerate_architecture`.

The repair packet must never say only "make it better."

## Scoring

Hard gates are binary blockers. The score is secondary and exists for ranking
pilot/scale quality.

Minimum production score:

```text
85/100 plus zero hard failures
```

Suggested weights:

| Dimension | Weight |
|---|---:|
| modern reader realization | 20 |
| genre-core pleasure | 20 |
| protagonist desire/cost/reversal | 15 |
| interaction realization | 15 |
| page-one/page-two hook | 10 |
| market-native specificity | 10 |
| anti-blandness / specificity | 10 |

Genre overrides are allowed. Example: healing may weight low-arousal ritual and
specificity above reversal intensity; battle may weight body/rival/cost higher.

## Text Extraction Rules

The validator must extract evidence from all common script shapes, because the
current JSON schema only guarantees `pages`.

Panel text sources:

- `panel.dialogue`
- `panel.dialogue_lines`
- `panel.narration`
- `panel.caption`
- `panel.sfx`
- `panel.scene`
- `panel.action`
- `panel.visual_description`
- `panel.prompt`
- nested `text`, `text_by_locale`, or locale maps

Evidence paths must use JSONPath-like strings:

```text
pages[0].panels[2].dialogue_lines[0].text
```

The gate must evaluate page order and panel order deterministically.

## Implementation Files

Add:

```text
config/manga/story_excellence_gates.yaml
config/manga/story_genre_alias_coherence.yaml
phoenix_v4/manga/story_quality/__init__.py
phoenix_v4/manga/story_quality/text_extract.py
phoenix_v4/manga/story_quality/excellence_gate.py
scripts/manga/validate_story_excellence.py
schemas/manga/story_excellence_realization_report.schema.json
tests/manga/test_story_excellence_gate.py
```

Update:

```text
phoenix_v4/manga/runner/chapter_runner.py
phoenix_v4/manga/chapter/writer.py
tests/manga/test_manga_chapter_runner_e2e_replay.py
docs/research/manga_craft/index.md
```

Optional later:

```text
scripts/manga/run_manga_chapter.py
scripts/manga/run_manga_pipeline.py
scripts/manga/plan_genre_scene_coverage.py
```

## Python API

Expose:

```python
def evaluate_story_excellence(
    *,
    story_handoff: Mapping[str, Any],
    writer_handoff: Mapping[str, Any],
    internal_record: Mapping[str, Any] | None = None,
    production: bool = True,
    config_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    ...
```

The function must:

- return a serializable report dict;
- never mutate inputs;
- never call an LLM;
- never call the network;
- fail closed when production is true and required doctrine is missing;
- include evidence paths for every pass and failure.

## CLI

Add:

```bash
PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
  --story-handoff <workspace>/story_architecture_handoff.json \
  --chapter-script <workspace>/chapter_script_writer_handoff.json \
  --internal-record <workspace>/chapter_script_internal_record.json \
  --production \
  --out <workspace>/story_excellence_realization_report.json
```

Exit codes:

- `0`: `PASS`
- `1`: `WARN` in production or malformed input
- `2`: `BLOCKED`

Flags:

- `--production`: hard enforcement.
- `--allow-warn`: exit `0` on `WARN` for smoke only.
- `--json`: print report JSON to stdout.
- `--repair-packet`: print only repair packet on blocked.

## Runner Integration

In `phoenix_v4/manga/runner/chapter_runner.py`:

1. Run the gate immediately after `_stage_writer()` creates or installs the
   script pair.
2. Write `story_excellence_realization_report.json` to the workspace.
3. In production writer mode, raise `RuntimeError` if report status is not
   `PASS`.
4. In explicit `writer_mode=stub`, allow `WARN`/`BLOCKED` only when the caller
   marks the run as non-shipping smoke. The report must still be written.
5. `_stage_visual()` must refuse to run when a production workspace lacks a
   PASS report.

This makes "valid JSON but bad story" stop before image spend.

## Test Fixtures

Add fixture categories:

```text
tests/fixtures/manga/story_excellence/pass/
tests/fixtures/manga/story_excellence/block/
```

Required blocking fixtures:

- missing `modern_reader_context`;
- phone/app/train mentioned but not transmuted into conflict;
- generic "something shifted" healing script;
- dark fantasy with portal but no cost/debt/wound;
- romance with no dyad pressure or boundary;
- sports with stats but no body/team/rival axis;
- social issue with issue poster language and no named relationship;
- France market script with flat U.S. high-school import;
- Japan market script with tourist-Japan default;
- China market script with unsafe direct system-allegory framing.

Required passing fixtures:

- dark fantasy / ja_JP / Gen Z: last-train or app threshold creates debt/cost;
- romance / en_US / Gen Z: unread-message pressure creates delayed intimacy;
- school / fr_FR / Gen Alpha: group chat or seating map creates belonging
  stakes;
- sci-fi cyberpunk / zh_CN / Gen Z: recommendation/feed interface creates
  body/social threat within guardrails;
- healing / ja_JP / Gen Z: dead phone/vending machine creates concrete
  low-arousal ritual without lecture;
- battle / en_US / Gen Alpha: clip/ranking pressure becomes public duel with
  body cost.

## Acceptance Criteria

Implementation is complete only when:

- `validate_modern_reader_doctrine(...) -> []`;
- the new report schema validates generated reports;
- all 25 canonical genres have coverage in the doctrine and gate config;
- all hard-gate blocking fixtures fail with `BLOCKED`;
- all passing fixtures pass with score `>=85`;
- `chapter_runner` writes a report for every chapter writer run;
- production runs cannot enter visual planning without a PASS report;
- the old `stillness_press_qa_run` style generic pass is reproduced as a
  fixture and blocked;
- tests include CLI and Python API coverage;
- docs index links this spec and the QA verification report.

Minimum test command:

```bash
PYTHONPATH=. python3 -m pytest \
  tests/manga/test_modern_reader_story_context.py \
  tests/manga/test_story_excellence_gate.py \
  tests/manga/test_manga_chapter_runner_e2e_replay.py \
  tests/test_manga_transmission.py -q
```

Recommended full story-governance command:

```bash
PYTHONPATH=. python3 -m pytest \
  tests/manga/test_modern_reader_story_context.py \
  tests/manga/test_all_genres_engine.py \
  tests/manga/test_story_engine_architect.py \
  tests/manga/test_story_excellence_gate.py \
  tests/test_manga_transmission.py -q
```

## Rollout Plan

### Smoke

- Run one deterministic fixture for each of the 25 genres.
- Use both `gen_z` and `gen_alpha` across the set.
- Cover all four markets at least twice.
- Do not render images.
- Output one consolidated QA report under:

```text
artifacts/qa/manga_story_excellence_gate_smoke_<YYYYMMDD>/
```

### Pilot

- Run 8 priority genres across 4 markets and 2 audiences.
- Include at least one authored Pearl_Writer script per market.
- Require zero hard failures.
- Allow score warnings only if repair packet is correct and no visual render is
  attempted.

Suggested priority genres:

```text
battle, romance, school, dark_fantasy, horror, sports, healing, sci_fi_cyberpunk
```

### Scale Micro-Batch

- Batch size starts at 10 chapters.
- Increase to 25 only after two consecutive clean batches.
- Increase to 50 only after four consecutive clean batches and no repeat issue
  code above 5%.
- Any hard-failure rate above 10% freezes scale and opens a repair lane.
- Any repeated alias-coherence failure freezes the affected genre only.

## Repair Routing

Repair scope decision:

- `rewrite_opening_pages`: modern catalyst/hook is missing but genre core exists.
- `rewrite_chapter`: genre core, protagonist desire, or interaction grammar is
  missing.
- `regenerate_architecture`: story handoff lacks doctrine, wrong genre routing,
  alias mismatch, or strategy bank conflict.

Repair handoff must include:

```text
genre_id
strategy_genre
relevance_genre
reader_market
reader_audience
selected catalyst
failed gate IDs
exact page/panel evidence
required genre-core evidence
specific rewrite instruction
```

## Production Invariants

- Schema validation is necessary but never sufficient.
- Prompt wording is necessary but never sufficient.
- Research docs are necessary but never sufficient.
- A story passes only when final script pages prove the doctrine.
- No production manga story may be accepted with generic fallback prose.
- Every block must produce an actionable repair packet.
- Image generation must never be used to hide story failure.

## Example Block

Input facts:

```text
genre_id: dark_fantasy
target_market: ja_JP
catalyst: cursed_app_at_last_train
```

Bad script:

```text
Page 1: A student checks an app on the train. Something shifted.
Page 2: He woke in another world and began his journey.
```

Required result:

```text
status: BLOCKED
failed gates:
- MANGA.STORY.MODERN_READER_REALIZATION
- MANGA.STORY.GENRE_CORE_PLEASURE
- MANGA.STORY.BLAND_FALLBACK_LINT
repair_scope: rewrite_opening_pages
```

Why:

- app is present but does not impose a rule, debt, wound, or cost;
- train is present but not used as a threshold with consequence;
- protagonist has no visible desire or choice;
- "something shifted" is generic fallback language.

## Example Pass Shape

```text
Page 1:
- Last train, phone at 1%, invite-only app opens without network.
- The app displays the protagonist's name with a debt already marked paid by
  someone else.
- They want to delete it because tomorrow is an exam / tryout / work shift.

Page 2:
- The station announcement calls a fantasy-world name only the protagonist's
  dead sibling used.
- A platform door opens to a battlefield road.
- Entering saves the sibling's name but burns the protagonist's return ticket.
```

Why it can pass:

- ordinary reader-world objects become the fantasy/dark-fantasy engine;
- protagonist desire is specific and immediate;
- cost arrives by page two;
- market surface is concrete;
- genre core is wound, debt, threshold, survival choice.

## Editor pass

**Added by Lane 07 (manga process uplift, 2026-07-24).** The automated gate proves
the machine-checkable floor; a bestseller read is not machine-decidable. Story QA is
therefore a **two-stage flow that shares one checklist source**, so the human read and
the machine gate never drift apart:

1. **Stage A — automated gate ≥ 85 (and all hard gates PASS), including
   `MANGA.STORY.GENRE_CRAFT_CHECKLIST`.** No editor time is spent on a chapter that
   has not cleared the machine floor; a BLOCKED report routes to the repair packet
   first. (Per the acceptance-layer doctrine, a gate PASS is at most `system working`
   / `structurally clear` — never a bestseller claim on its own.)

2. **Stage B — Pearl_Editor structured read against the SAME checklist file**
   (`config/manga/genre_craft_checklists.yaml` for the chapter's canonical genre, plus
   the `mc_items`-referenced rows resolved from `config/manga/mc_endurance_checklists.yaml`).
   The editor renders a **per-item verdict** — not a prose review — so the human read is
   diffable against the machine gate and reusable by downstream QA.

### Editor review artifact (schema)

Written to `artifacts/manga/editor_reviews/<series_id>/<chapter_id>.editor_review.yaml`:

```yaml
artifact_type: manga_chapter_editor_review
schema_version: "1.0"
series_id: <str>
chapter_id: <str>
genre: <canonical_genre_id>              # matches genre_craft_checklists.yaml key
checklist_source: config/manga/genre_craft_checklists.yaml
mc_endurance_source: config/manga/mc_endurance_checklists.yaml
gate_report: <path to story_excellence_realization_report.json>   # Stage A evidence
gate_status: PASS | WARN | BLOCKED       # copied from Stage A; Stage B runs only on PASS
verdicts:                                # ONE line per checklist item read
  - checklist: story_elements_must       # or story_elements_should / dialogue_rules /
                                         #   panel_grammar_items / failure_modes /
                                         #   mc_must_have / mc_should_have / mc_anti_patterns
    item: "<verbatim item text>"
    source: "<the item's source anchor>"
    verdict: PASS | WEAK | FAIL | NA     # NA only for genuinely inapplicable items
    note: "<one concrete line: where it lands on the page, or what is missing>"
overall: SHIP | REVISE | HOLD
editor: <name-or-agent-id>
reviewed_at: <ISO-8601>
```

**Binding rules.** Every `story_elements_must` item and every resolved `mc_items`
`must_have` item MUST have a verdict line; a `FAIL` on any must-item forces
`overall != SHIP`. `failure_modes` items are read as "absent?" (a PASS verdict means the
anti-pattern is absent). Verdicts are advisory to shipping — they do not mutate the gate —
but a chapter is not `bestseller register` (Layer 4) without a `SHIP` review on record.
`endurance_mechanics` items are read for **series-plan** review (100+-episode horizon),
not per-chapter, and are skipped (`NA`) for completion-first genres.

**Lane 08 binding.** The `manga-editor` skill consumes this section: it loads the genre's
block, resolves the `mc_items` reference, and emits exactly this artifact. Do not fork a
second checklist source for the human read.

## Test Fixtures

Add fixture categories:

```text
tests/fixtures/manga/story_excellence/pass/
tests/fixtures/manga/story_excellence/block/
```

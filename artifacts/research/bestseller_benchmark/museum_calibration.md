# Museum calibration — internal long-form probe

## Inputs

- **Detector bundle:** `phoenix_v4/quality/regression_museum` + `config/governance/regression_museum.yaml` (ported on this branch).  
- **Samples:** eleven chapter-sized files under `artifacts/research/bestseller_benchmark/samples/` (see `book_corpus.yaml` for provenance).  
- **Persona:** `gen_z_professionals` for off-persona vocabulary.

## Aggregate: which classes fire?

Counts across the **eleven** scored chapters (any hit = counted once per chapter):

| failure_class | chapters_with_hit (max 11) |
|---------------|-------------------------|
| doctrinal_exposition_inline | 10 |
| doubled_word | 10 |
| font_css_leak | 7 |
| mid_paragraph_format_break | 11 |
| off_persona_vocabulary | 9 |
| repeated_scene_anchor | 11 |

**Did not fire on any sample in this run:** `template_dict_artifact`, `cross_chapter_verbatim_duplication`, `verbatim_chapter_block_repeat`, `same_exercise_overuse`, `identical_opening_scene`, `generic_reader_address`.

### Single-chapter caveat

`cross_chapter_verbatim_duplication` and friends are **book-scale** detectors; this benchmark feeds **one chapter** per JSON run, so absence of cross-chapter hits is **expected**, not evidence those detectors are inactive globally.

## False-positive read (bestseller-oriented lens)

Even though these texts are **Phoenix drafts**, not the ten commercial titles, the firing pattern already tells us which classes will **nuke** legal self-help chapters:

1. **repeated_scene_anchor** — fires on **11 / 11** because the anchor phrase is literally present in the scratch manuscript (`soft daylight along the sill`). That is a **Phoenix regression needle**, not a universal literary sin. **Refinement:** treat as Phoenix-internal lint keyed to repo-specific anchors, or raise `max_occurrences_per_book` until cross-title calibration exists.

2. **doctrinal_exposition_inline** — fires on **10 / 11** because the scratch book uses Buddhist teaching vocabulary that trips doctrine + abstract noun heuristics. Real Western bestsellers in the anxiety lane still cite Buddhism occasionally; this detector **will false-positive** on legitimate memoir / self-help unless narrowed (e.g., require absence of proper-name scene anchors, or restrict to known bad templates).

3. **off_persona_vocabulary** — **9 / 11** hits on terms like “Dharma” / “Karma yoga” blocklist. That is correct for **gen_z_professionals** when those strings appear — but it is also a reminder that **persona-specific blocklists are not universal “bestseller bad” lists**; they are **brand-fit** lists.

4. **mid_paragraph_format_break** — **11 / 11** WARN-level hits from the soft regex (`[a-z,]\s*\n\s*\n`). Markdown / soft line wraps in prose can trip this without reader-visible defect. **Refinement:** tighten to require absence of closing punctuation **and** a capitalized continuation, or downgrade default severity.

5. **doubled_word** — **10 / 11** hits; some are true typos (“The the train”), others may be edge cases of legitimate repetition. Keep detector, but **expand exceptions** after sampling false positives on commercial chapters.

6. **font_css_leak** — **7 / 11** hits on the `Word;;` style pattern. Several hits coincide with `---` staccato assembly artifacts. **Refinement:** confirm each hit is actually CSS-like, not em-dash typography.

## Verdict on “12 failure classes” readiness

- **Confirmed high-signal (kept as merge blockers after refinement):** `template_dict_artifact` (not exercised here but obviously catastrophic), `cross_chapter_verbatim_duplication` / `verbatim_chapter_block_repeat` (book-scale; keep for multi-chapter CI), `doubled_word` (keep with better exceptions).  
- **Needs refinement before treating as bestseller-compatible CI:** `repeated_scene_anchor`, `doctrinal_exposition_inline`, `mid_paragraph_format_break`, `font_css_leak`.  
- **Persona-scoped (not universal bestseller gate):** `off_persona_vocabulary` — keep, but document as **brand contract**, not “commercial success detector.”

## Recommended next engineering steps

1. Re-run this scorer on **each legally sourced commercial chapter** when files exist; log hits per class with 120-character evidence windows.  
2. For each class with >20% hit rate on commercial set, either **tighten regex**, add **exemption clauses**, or **demote severity** to WARN until a second calibration sprint confirms.

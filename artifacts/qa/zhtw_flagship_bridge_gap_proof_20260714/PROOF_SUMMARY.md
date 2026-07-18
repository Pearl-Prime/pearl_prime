# zh-TW Flagship Bridge/Transition Gap — Fix + Proof (2026-07-14)

## Scope

Cell: `gen_z_professionals` × `anxiety`, engine `overwhelm`, flagship
`extended_book_2h` book (the same PROVEN-AT-BAR flagship read documented in
`docs/PROGRAM_STATE.md` under "Flagship book (gen_z_professionals × anxiety)").
This proof covers only the **zh-TW render** of that book; the frozen English
goldens (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`,
`CANONICAL_FLAGSHIP_BOOK.txt`) were not touched.

## Gap identified

The English atom bank already contains a purpose-built, cell-specific
chapter-to-chapter continuity chain used by the actual frozen English
flagship golden:

- `atoms/gen_z_professionals/anxiety/THREAD/CANONICAL.txt` — `THREAD v21`–`v31`
  (11 atoms), each tagged `cell: gen_z_professionals_anxiety`,
  `engine: overwhelm`, with a `note:` explicitly stating which chapter it
  seeds (e.g. "ch2 gap atom — seeds ch3 chronic_somatic_tension").
- `atoms/gen_z_professionals/anxiety/INTEGRATION/CANONICAL.txt` — `INTEGRATION
  v36`–`v46` (11 atoms), same cell/engine tagging, each the closing landing
  for one specific chapter (ch2 through ch12).

Confirmed (by grep) that these exact 22 atoms are the ones actually selected
in the frozen English golden book (`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt`),
e.g. the ch2→ch3 seam is verbatim `THREAD v21` / `INTEGRATION v36`.

**The zh-TW locale files for THREAD and INTEGRATION had NO translation of
any of these 22 atoms** — `THREAD/locales/zh-TW/CANONICAL.txt` stopped at
`v20`, `INTEGRATION/locales/zh-TW/CANONICAL.txt` stopped at `v25`. Neither
gap is listed in any `shard_zh-TW_*.json` translation-shard gap-list, so it
is not owned by the parallel Translation Shards phase — this is genuinely
new/never-before-translated bridge content, not general atom backlog.

### Consequence, proven from a real prior render

`artifacts/qa/book_100pct_production_readiness_20260713/builds/flagship_zhTW/`
(command in that dir's `command.txt`, an earlier zh-TW render of this exact
book) shows the actual effect of the gap: `selected_content_variants.json`
for that build only ever contains `THREAD v01`–`v20` and `INTEGRATION
v01`–`v25` — the composer had no cell-matched candidate to select, so it
silently fell back to generic, engine-agnostic variants. Concretely, at the
ch2→ch3 seam that build reads (English gloss in brackets):

> ...拼命奮鬥燒壞了引擎。在不以奮鬥為燃料的情況下，重建是什麼樣子... [The hustle
> burned the engine. What rebuilding looks like without the hustle as
> fuel...]
>
> Chapter 3
> 從星期二開始，你的肩膀就一直聱在耳朵旁邊。 [Since Tuesday, your shoulders have
> been up by your ears.]

The THREAD sentence promises a chapter about burnout/rebuilding; chapter 3
actually opens on shoulder tension. This is exactly the "same chapter,
different nouns" / mismatched-seam failure mode the writing overlay spec
(`docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` §11.2, §4 rubric
item 5 "Pull") calls out — the zh-TW reader gets an episodic, non-threaded
seam at exactly the chapter boundary the English reader gets a matched one.

## Fix

Authored zh-TW translations (by the author of this change, not machine
translation) of the 22 missing gap atoms, appended to the existing locale
files in the same format/metadata convention already used for the other
translated variants in those files (metadata block kept verbatim/untranslated
— it is composer-facing structured data, not prose; only the atom body prose
is translated):

- `atoms/gen_z_professionals/anxiety/THREAD/locales/zh-TW/CANONICAL.txt` — added `THREAD v21`–`v31`
- `atoms/gen_z_professionals/anxiety/INTEGRATION/locales/zh-TW/CANONICAL.txt` — added `INTEGRATION v36`–`v46`

## Proof: re-rendered the same book, same command, after the fix

`render_after/` in this directory is the full output of:

```
python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --pipeline-mode spine --quality-profile production --exercise-journeys \
  --runtime-format extended_book_2h --locale zh-TW \
  --seed book100_flagship_zhtw_20260713 --no-job-check --render-book \
  --render-dir <dir>
```

(identical seed/arc/command to the prior `flagship_zhTW` build, so this is
an apples-to-apples re-render, not a new build.)

`render_after/selected_content_variants.json` now shows the composer
selecting `THREAD v21`–`v31` and `INTEGRATION v36`–`v46` — the exact
cell-matched chain, matching the English golden's selection — instead of
falling back to the generic pool.

`render_after/book.txt` ch2→ch3 seam now reads:

> ...行事曆漩渦並非只存在於她的腦海裡。到了週四，她的肩膀仍未從週日的緊繃中放鬆下來。
> 下一章要從身體記帳的地方說起——那些會議結束後仍持續緊繃的肌肉。 [The calendar spiral
> wasn't only in her head. By Thursday her shoulders still hadn't come down
> from Sunday. The next chapter begins where the body keeps score — the
> muscles that stayed braced after the meetings ended.]
>
> Chapter 3
> 從星期二開始，你的肩膀就一直聱在耳朵旁邊。 [Since Tuesday, your shoulders have
> been up by your ears.]

The THREAD forward-pointer now names the exact thing chapter 3 opens with.
Same pattern holds at every other ch(n)→ch(n+1) seam from ch2 through ch12
(verified by reading `render_after/book.txt` chapter boundaries against the
`note:` field of each newly-added atom).

## Honest limitation: the automated chapter_flow_gate does not move

`render_after/chapter_flow_report.json` reports the **same** 7 failing
chapters, same `MISSING_CLEAR_POINT` / `WEAK_TRANSITIONS` errors, as the
prior build's `book_quality_report.json` (`fail_reasons: ["chapter flow
failed in 7 chapter(s)"]`, `release_band: Reject`). This is because
`chapter_flow_gate.py`'s `transition_hits` / `thesis_hits` heuristics are
English-discourse-marker keyword matches (phrases like "the next chapter",
thesis-echo phrasing) run against the composed text regardless of locale —
it is blind to Chinese-language transition and thesis cues, so it cannot
detect the qualitative seam repair demonstrated above. This is a pre-existing
CJK-locale gap in that gate, not something introduced or fixed by this
change, and this change does **not** touch `chapter_flow_gate.py` — per
the non-negotiable rule against weakening or gaming gates, the gate is left
exactly as it is. The improvement here is real and demonstrated at the
content/selection level, not asserted via a gate-score change.

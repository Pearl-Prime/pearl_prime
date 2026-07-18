# Book Identity Contracts

A **per-cell identity contract** is a one-page authored constraint that turns an
inventory of good atoms into *a book with one spine of meaning*. It fixes the
single most damaging finding of the external editor's read: the financial book
ran **seven competing metaphor systems** ("the weight," "the pile," "spreadsheet
vs chest," "numbers and nerves," …) so no image ever accreted into an identity.

Each contract declares, for one (topic × … ) cell:

| field | meaning |
|---|---|
| `primary_metaphor` | the ONE image the whole book returns to |
| `engine_metaphors` | the allowed sub-image per engine (overwhelm/spiral/shame…) — extensions of the primary, never rivals |
| `core_contrast` | the single either/or the book keeps re-drawing |
| `identity_line` | the sentence a reader could tattoo; lands in ch1 and the final chapter |
| `banned_phrases` | competing metaphors that must NOT appear — deprioritized at selection |

## Wiring status — WIRED (2026-07-05)

Enforcement lives in:
- `phoenix_v4/planning/book_identity_contract.py` — load + helpers
- `phoenix_v4/planning/enrichment_select.py` — HOOK soft-penalty for `banned_phrases`, engine metaphor bonus
- `phoenix_v4/rendering/chapter_composer.py` — `identity_line` guaranteed in ch1 + final chapter

Contracts with `status: wired` are active. Set `status: unwired` to disable without deleting YAML.

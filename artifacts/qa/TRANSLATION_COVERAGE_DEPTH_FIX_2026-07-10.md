# Translation Coverage Reporting Tool — Depth-Independence Fix (2026-07-10)

## Bug

`scripts/ci/report_translation_coverage.py`'s `_bestseller_translated_count()` derived
`(persona, topic, slot)` from fixed positional indices `rel.parts[0..2]` of the source path
relative to `atoms_root`, assuming every English source lives at exactly
`atoms/{persona}/{topic}/{slot_or_engine}/CANONICAL.txt` (4 levels). Real atom trees also nest
deeper — e.g. `atoms/{persona}/anchored/{topic}/{engine}/CANONICAL.txt` or
`atoms/{persona}/{topic}/{engine}/{SLOT}/CANONICAL.txt` — both present in `atoms/`. For those,
the fixed-index derivation built the wrong `atoms/.../locales/{locale}/CANONICAL.txt` path,
producing false "missing" and false "present" counts.

`_bestseller_english_sources()` was already depth-independent (`rglob` + a `len(rel.parts) >= 4`
depth *floor*, not an exact-4 assumption) — only the translated-count side had the bug.

Discovered 2026-07-10 during ja-JP backlog re-derivation for
`ws_cjk_atom_translation_qwen25_20260420` (`artifacts/qa/JA_JP_TRANSLATION_CLOSEOUT_2026-07-10.md`).

## Fix

`_bestseller_translated_count()` now derives the translated-file path directly from
`src.parent / "locales" / locale / "CANONICAL.txt"` — correct at any depth, since a translation
always lives as a sibling `locales/{locale}/` under the same atom-type directory as its English
source, regardless of how many path segments precede that directory. The now-unused `atoms_root`
parameter was dropped from the function and its call site.

## Verification — coverage numbers move for every CJK6 locale, as expected

Measured on the same on-disk `atoms/` tree, before and after, isolated from any working-tree
git state:

| locale | before (buggy) | after (fixed) | delta |
|---|---|---|---|
| ja-JP | 3297/3752 (87.9%) | 3156/3752 (84.1%) | **-141** (was over-counting) |
| ko-KR | 227/3752 (6.1%) | 227/3752 (6.1%) | 0 (no deep-path entries for this locale) |
| zh-CN | 1238/3752 (33.0%) | 1622/3752 (43.2%) | **+384** (was under-counting) |
| zh-HK | 243/3752 (6.5%) | 243/3752 (6.5%) | 0 |
| zh-SG | 243/3752 (6.5%) | 243/3752 (6.5%) | 0 |
| zh-TW | 3365/3752 (89.7%) | 3589/3752 (95.7%) | **+224** (was under-counting) |

Every locale's number changes except two with no affected entries on disk right now — consistent
with a depth-derivation bug that affects all locales' counts, not just ja-JP's. Notably, this
directly resolves the "zh-TW complete / 92.1%" reporting-drift question the sibling zh-TW
reconcile lane was tasked with investigating: **the honest current figure is 95.7% (3589/3752),
not 92.1%**, once the counting bug is fixed.

`_bestseller_english_sources()` unchanged — confirmed already depth-independent.

## Scope

Tool-only fix. No `atoms/**/locales` content touched (verified: shared working tree restored
byte-identical to `origin/main` before landing this change via a separate commit off
`origin/main`, not through the shared checkout).

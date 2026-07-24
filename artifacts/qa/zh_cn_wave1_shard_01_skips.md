# zh-CN Wave 1 — Shard 01 Skip Report

Branch: `agent/zh-cn-wave1-shard-01-20260723`
Base: `origin/main` @ `cf1512336e`
Model: `qwen3.7-max` (DashScope, Singapore intl endpoint)

## Summary

- Attempted: 20
- Accepted: 14
- Skipped: 6

## Skipped items (with reason)

1. **`atoms/midlife_women/compassion_fatigue/comparison/CANONICAL.txt`** (item `81949b5e82b7`)
   - Reason: **source path does not exist in `origin/main`**. The file is present
     only as an *untracked, uncommitted* artifact in the shared local
     `/Users/ahjan/phoenix_omega` checkout (`git status --short` shows `??`);
     `git ls-tree origin/main -- atoms/midlife_women/compassion_fatigue/` has no
     `comparison` entry (only the uppercase `COMPRESSION/EXERCISE/GRIEF/HOOK/
     INTEGRATION/OVERWHELM/PERMISSION/PIVOT/REFLECTION/STORY/TAKEAWAY/THREAD/
     WATCHER` shape dirs). Cannot treat uncommitted, unauthored working-tree
     cruft as a canonical English source — translating it risks shipping
     content that was never actually landed/approved. Recommend the coordinator
     either (a) confirm this file is genuinely intended and get it committed to
     `origin/main` first, or (b) drop it from the worklist as a stale artifact.

2. **`atoms/millennial_women_professionals/compassion_fatigue/COMPRESSION/CANONICAL.txt`** (item `6cc98eae2faa`)
   - Reason: **EN source is empty across all 30 variants.** Every `## COMPRESSION
     vNN` block (v01–v30) contains only a header, an empty frontmatter
     delimiter pair, and a bare `compression_family: CN` tag — zero prose body
     anywhere in the file. There is nothing to translate; producing zh-CN text
     here would mean inventing content the English source never authored.
     structural_validator correctly flags every block `untranslated_english`
     (no CJK present because there's no text at all). This belongs on the
     EN-source-authoring backlog (see `artifacts/qa/atom_authoring_backlog_20260722.tsv`
     pattern), not the translation queue.

3. **`atoms/gen_x_sandwich/compassion_fatigue/watcher/CANONICAL.txt`** (item `fa632dcce6a2`)
4. **`atoms/gen_x_sandwich/compassion_fatigue/overwhelm/CANONICAL.txt`** (item `f893ed06a0e8`)
5. **`atoms/gen_x_sandwich/compassion_fatigue/grief/CANONICAL.txt`** (item `b1c6da5309c1`)
   - Reason (same defect class, all three): **malformed EN source in the
     `RECOGNITION`/`MECHANISM_PROOF`/`TURNING_POINT`/`EMBODIMENT` v01/v03/v05
     "semantic-family" variants.** Each of these opens with a correct
     `## SHAPE v0N` header + real frontmatter (`path:`, `BAND:`,
     `SEMANTIC_FAMILY:`, `IDENTITY_STAGE:`), but the paired even-numbered
     variant (`v02`, `v04`) is not a real header at all — it's a bare orphan
     line (e.g. literally the text `RECOGNITION v02`, missing its own `##`
     prefix, its own frontmatter, and any body) sitting between the two
     properly-closed delimiter blocks. Net effect: 10 of the ~22 variants in
     each file have no translatable prose (only a slug-like `path:` value and
     the orphan fragment). The `v06+` "band_fill"/"capacity_fill"/"micro"
     variants later in the same files *do* have full narrative prose and
     translate cleanly — I translated those correctly, but because
     `structural_validator` validates the whole file as one unit and these
     files fail on the malformed variants (`untranslated_english` on the
     no-prose blocks, plus 2–3 genuine `glossary_violation:身份` hits I could
     have fixed), the file as a whole cannot pass. Per instructions I did not
     invent missing prose for the malformed variants. Recommend routing these
     3 files to the EN-source-authoring backlog; once the missing prose is
     authored for the v01/v03/v05 slots, re-run translation — the rest of each
     file (v06 onward) is already translation-ready.

6. **`atoms/gen_x_sandwich/compassion_fatigue/INTEGRATION/CANONICAL.txt`** (item `2ede20518451`)
   - Reason: **EN source has genuinely duplicate header IDs.** `## INTEGRATION
     v05`, `v06`, and `v07` each appear *twice* in the source file — once as an
     empty stub (frontmatter-only or fully blank) around lines 37–65, and again
     later (lines 65–95+) as fully-authored real content. This is a structural
     defect in the English source itself (duplicate variant numbering), not a
     translation issue — `structural_validator` correctly flags
     `duplicate_header_ids` and cannot be repaired without either (a)
     renumbering the source, which is out of scope for a translation shard, or
     (b) inventing which of the two same-numbered blocks is "the real v05" to
     keep, which risks silently dropping authored content. Recommend the
     EN-source-authoring backlog owner de-duplicate/renumber this file first.

## Systematic issue flagged to the coordinator (not a shard-01-only skip)

`analysis/zh_cn/glossary_project.yaml` locks **"compassion fatigue" → 共情耗竭**
(both `title_or_header` and `narrative_body` roles). DashScope's initial pass
on this shard used **同情疲劳** (86 occurrences) and **共情疲劳** (30
occurrences) almost everywhere instead — **zero** of the initial 19 raw
candidates used the locked term. This matches the cross-shard finding
surfaced by shard 04 (`structural_validator.py` only enforces glossary
`avoid`-lists, not `preferred`/locked terms — it does not catch drift to an
unlisted synonym). I corrected every occurrence in all 14 accepted files
before commit (global `同情疲劳`/`共情疲劳` → `共情耗竭` replace + manual
read-through), plus fixed 7 files' `glossary_violation:身份` hits (avoid-listed
per `glossary_core.yaml`'s "identity" entry) by rendering as `自我认同` in
context. Recommend the coordinator raise a follow-on ticket to add a
locked-term positive-match check to `structural_validator.py` so this isn't
manual-grep-dependent per shard.

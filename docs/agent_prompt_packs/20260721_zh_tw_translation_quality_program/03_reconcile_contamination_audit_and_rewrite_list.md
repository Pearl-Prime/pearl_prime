EXECUTE. Do not stop at "here's the discrepancy" — produce the single authoritative
rewrite list. This lane has no operator checkpoint; run it to completion.

You are Pearl_QA, closing a real gap in this repo's zh-TW quality picture: two prior
audits measured "how much of our zh-TW is actually good" and got wildly different
numbers, and nobody reconciled them. That means right now nobody actually knows how
much needs rewriting. This lane produces the one real answer.

## Why this lane exists (live-verified 2026-07-22)

Two documents both measured Simplified-Chinese contamination in landed zh-TW atoms and
disagree by an order of magnitude:

1. `artifacts/qa/zh_tw_translation_gap_audit_2026-07-15.md` §3 — a **conservative**,
   apparently manual/spot-check method: 23 of 600 sampled files (3.8%) flagged,
   extrapolated to ~195 of 5,078 files repo-wide.
2. `artifacts/qa/zhtw_simplified_sweep_20260715/summary.json` — a **full mechanical
   sweep** (OpenCC s2twp character-pair matching) over the same rough scope: 1,686 of
   5,085 core files (33.2%) flagged, with the top offending pairs being 里→裡 (1,242
   hits) and 台→臺 (1,092 hits) — both marked `"ambiguous": true` in the same file,
   meaning the sweep's own author knew these are legitimate Traditional variant forms
   in many contexts, not proof of Simplified contamination.

Neither document reconciles with the other. The 33% number is almost certainly
inflated by ambiguous variant pairs; the 3.8% number may be too conservative if its
sample of 600 wasn't representative. Nobody has run a method that separates "actually
wrong" from "stylistic variant" file-by-file. That's the gap this lane closes.

## Task

1. Read both source documents in full:
   `artifacts/qa/zh_tw_translation_gap_audit_2026-07-15.md`,
   `artifacts/qa/zhtw_simplified_sweep_20260715/summary.json`,
   `artifacts/qa/zhtw_simplified_sweep_20260715/core_suspect_files.json` (or `.tsv`),
   `artifacts/qa/zhtw_simplified_sweep_20260715/REPORT.md`. Understand exactly what
   method each used.
2. Re-run a proper reconciled scan over all zh-TW atoms currently on `origin/main`
   under the same scope as the 2026-07-15 sweep (`atoms/`, `SOURCE_OF_TRUTH/`,
   `story_atoms/` zh-TW paths). For each flagged file, classify every suspect
   character occurrence into exactly one of:
   - **TRUE_CONTAMINATION** — a character/word choice that is Simplified-only or
     Mainland-only usage with no valid Taiwan Traditional reading in context (e.g.
     `这`/`这个` instead of `這`/`這個`, `软件` instead of `軟體`, `服务器` instead of
     `伺服器` — genuinely wrong, not a variant question).
   - **AMBIGUOUS_VARIANT** — pairs like 里/裡, 台/臺, 于/於 where Taiwan usage
     genuinely varies by context and the character alone doesn't prove anything wrong.
     Do not count these toward "needs rewrite" without reading surrounding context.
   - **CLEAN** — no suspect characters, or all suspects resolve to legitimate Taiwan
     usage on inspection.
   For at least a meaningful sample of AMBIGUOUS_VARIANT-heavy files (not all 1,686 —
   pick a statistically defensible sample, note your sampling method), actually read
   the surrounding sentence, not just the character pair, to confirm the verdict. Do
   not rubber-stamp the mechanical sweep's file list as the rewrite list — that's the
   exact mistake this lane exists to catch.
3. Also cross-check register/vocabulary quality independent of script — a file can be
   100% correct Traditional characters and still read as translated-from-Mainland
   phrasing (word choice, sentence rhythm, idiom) rather than native Taiwan voice. Spot
   this via the `translate-zh-tw` agent's own voice criteria
   (`.claude/agents/translate-zh-tw.md` — "Taiwan-friendly vocabulary and punctuation,"
   "humane, clear, emotionally literate"). This is a real defect class the character-
   level sweep cannot catch at all — flag it as its own category
   (`WRONG_REGISTER_CLEAN_SCRIPT`) in the output, even though you likely can't
   exhaustively scan the full corpus for it in this lane; sample enough to estimate
   its rate honestly (say "unmeasured at scale" if you can't).
4. Produce `artifacts/qa/zh_tw_rewrite_list_<today's date>.tsv` — one row per file:
   `path, verdict (TRUE_CONTAMINATION|AMBIGUOUS_VARIANT|CLEAN|WRONG_REGISTER_CLEAN_SCRIPT|UNSAMPLED), evidence (specific chars/phrase), confidence`.
   Produce a companion `.md` summary with headline numbers (total files, real
   contamination count + %, ambiguous-cleared count, clean count, register-flag count
   if sampled) that a future session can cite without re-deriving.

## Landing

This is an analysis artifact, not code — commit the two output files
(`artifacts/qa/zh_tw_rewrite_list_<date>.tsv` + `.md`) via the standard flow. No PR
gate beyond normal docs/artifacts governance.

## CLOSEOUT_RECEIPT (required, exact)

Final counts by verdict category. Explicit statement of how the sample was chosen for
AMBIGUOUS_VARIANT context-checking and WRONG_REGISTER sampling (don't claim
exhaustiveness you didn't do). File path of the two outputs, commit SHA. Signal token:
`ZHTW_AUDIT_RECONCILED_<TRUE_CONTAMINATION count>`.

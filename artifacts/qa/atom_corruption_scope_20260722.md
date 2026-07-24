# zh-TW Atom Corruption — Full-Population Scope (2026-07-22)

Investigation-only. No files were fixed, translated, or rewritten in this lane.

## 0. Headline

Of **5,279** `atoms/**/locales/zh-TW/CANONICAL.txt` files in the current tree, **1,850
(35.0%)** are corrupted in one of three distinct ways. This is **not** a translation
gap and **not** zh-TW-specific:

- **1,020 of 1,850 (55%)** have a **clean English source** — a real translation
  job would fix these.
- **650 of 1,850 (35%)** have an **equally corrupted English source** — this is a
  pre-existing content-authoring gap, not a translation defect. Re-translating a
  broken source would ship the corruption in Chinese too.
- **165 (9%)** are structurally mixed / did not resolve cleanly to either bucket
  by this heuristic (see §5, `UNCLEAR_MIXED`).
- **0 files** had a missing English sibling (`EN_MISSING` never occurred).
- The same corruption signatures are independently confirmed in **ja-JP and
  zh-CN** at identical atom paths (§4) — this is a shared-pipeline defect, not
  a zh-TW translation-run failure.
- Root cause is traceable, by git blame, to **four specific commits** across
  three separate incidents between 2026-04-20 and 2026-06-15, accounting for
  **1,827 of 1,850 (98.8%)** of flagged files (§6).

The prior first-pass scan's ~1,160-file estimate significantly **undercounted**
the true population (this scan found 1,850) because it did not have a distinct
bucket for the largest single class found here: **UNTRANSLATED_ENGLISH** (582
files — real atom-shaped prose, just never translated, as opposed to raw
chat-completion leakage). That class did not exist in the prior taxonomy and
was likely folded into "unclear" or missed by the prior heuristic's phrase list.

## 1. Method (re-derived this session, not reused from the prior scan)

A block-level classifier (`scan2.py`) parses each `CANONICAL.txt` into its
`--- variant: vNN` / `## LABEL vNN` atom blocks, strips the optional
`---\nmetadata\n---` fence from each block, and classifies each block body by:

- **CJK-character ratio** of the body (post metadata-strip) — real Traditional
  Chinese atom prose reliably scores > 0.5; corrupted bodies score near 0.
- **Chat/meta-commentary phrase match** (~55 English discourse markers: "here
  is", "here's a breakdown", "I hear you", "this framework", "given your
  profile", markdown `##`/`**` headers, etc.) — distinguishes raw LLM chat
  output from plain untranslated prose.
- **Body length** — bodies under 8 characters after stripping the metadata
  fence are `EMPTY`.

File-level `defect_class` is assigned by **presence** of at least one bad block
(not majority-vote — this matches the prior session's own framing of "some
empty stub bodies," and was verified against the prior session's ~525/~533
figures: this session's raw block-presence counts for pure META and pure EMPTY
signals landed at 548 and 533 respectively before commentary/empty overlap
resolution, closely reproducing the prior scan's order of magnitude). Priority
on overlap: `META_COMMENTARY` > `EMPTY_STUB` > `UNTRANSLATED_ENGLISH` >
`UNCLEAR_MIXED`.

This was calibrated against ~20 hand-inspected files, both flagged and
CLEAN, including several that a naive whole-file phrase-scan (this session's
own first attempt) badly false-positived on — e.g. legitimately-translated
files using `## LABEL vNN` markdown-style headers or English YAML-style
metadata blocks (`path:`, `BAND:`, `IDENTITY_STAGE:`) were initially
misflagged at an 87%-of-corpus rate before the metadata-fence-stripping fix.
That first (wrong) pass is not reported here; only the calibrated result is.

## 2. Full population counts by defect class

| defect_class | count | % of 5,279 scanned | % of 1,850 flagged |
|---|---:|---:|---:|
| CLEAN | 3,429 | 65.0% | — |
| META_COMMENTARY | 593 | 11.2% | 32.1% |
| UNTRANSLATED_ENGLISH | 582 | 11.0% | 31.5% |
| EMPTY_STUB | 510 | 9.7% | 27.6% |
| UNCLEAR_MIXED | 165 | 3.1% | 8.9% |
| **Total flagged** | **1,850** | **35.0%** | **100%** |

`META_COMMENTARY` = raw LLM chat-completion output (analysis commentary,
refusals, "here's a breakdown of...") landed verbatim in place of translated
atom prose — either as the whole file (no atom header structure at all) or
inside individual variant blocks.

`UNTRANSLATED_ENGLISH` = proper atom header/metadata structure present, but
the body prose is English, not Chinese — a translation step that never ran
(or copied source through unchanged) rather than raw model chatter.

`EMPTY_STUB` = proper header structure present, but one or more variant
bodies are blank (metadata fence with nothing after it).

`UNCLEAR_MIXED` = files with a low-but-sub-threshold mix of the above defect
signals that didn't cleanly dominate any one bucket (frequently: files that
straddle two different header-format eras within the same file, see
`atoms/educators/compassion_fatigue/REFLECTION` for a concrete example of a
file with `## LABEL vNN`-style English-untranslated v01 blocks followed by
`--- variant: vNN`-style properly-translated later blocks).

## 3. Defect class × English-source status (the critical cross-tab)

| defect_class | EN_CLEAN_ZH_CORRUPTED | EN_ALSO_CORRUPTED | EN_MISSING |
|---|---:|---:|---:|
| META_COMMENTARY | 492 | 101 | 0 |
| UNTRANSLATED_ENGLISH | 537 | 45 | 0 |
| EMPTY_STUB | 20 | 490 | 0 |
| UNCLEAR_MIXED | 151 | 14 | 0 |
| **Total** | **1,200** | **650** | **0** |

(Note: §0 rounds `EN_CLEAN_ZH_CORRUPTED` to 1,020/1,850 by excluding
`UNCLEAR_MIXED`'s 151 from the headline "real translation gap" framing since
that bucket's zh-TW defect itself isn't cleanly established; the full,
unrounded table above is authoritative.)

**This is the single most important finding in this scope.** The two largest
defect classes split almost oppositely on English-source status:

- **META_COMMENTARY is overwhelmingly a translation-step failure** (492/593 =
  83% have a clean English source). The corruption was introduced specifically
  during/after the zh-TW write, not inherited.
- **EMPTY_STUB is overwhelmingly NOT a translation problem** (490/510 = 96%
  have an equally-corrupted English source). These are pre-existing
  content-authoring gaps — the English atom itself was never written (often a
  literal placeholder, e.g. `[Integration content for healthcare_rns ×
  financial_anxiety]`, or a generic filler sentence reused hundreds of times
  across pools, e.g. "The mechanism deepens. Stakes rise. The cost becomes
  clear." appears verbatim in 300 separate English `CANONICAL.txt` files, and
  "Crisis. Breakthrough. The moment of maximum intensity." in 437 — see §6.2).
  Re-translating these ships the same emptiness in Chinese; the actual fix is
  English-side authoring, upstream of any translation lane.
- **UNTRANSLATED_ENGLISH is also overwhelmingly a translation-step failure**
  (537/582 = 92% clean English source) — the body was simply never converted
  to Chinese, as distinct from META_COMMENTARY's raw-chatter leakage.

## 4. Other-locale contamination (checked for the full 1,850-file flagged set, not just a sample)

Checked ja-JP, zh-CN, ko-KR, zh-HK, zh-SG at the identical atom path for every
one of the 1,850 flagged zh-TW files, using an ASCII-heavy heuristic (>70% of
alphabetic characters are ASCII in a locale file whose target script is
CJK/Hangul — the same signature as the zh-TW corruption: raw English chatter
or untranslated English body where translated non-Latin prose is expected).

| locale | file exists at same path | of those, ASCII-heavy / suspect-corrupted |
|---|---:|---:|
| ja-JP | 1,580 / 1,850 (85%) | 409 (26% of existing) |
| zh-CN | 669 / 1,850 (36%) | 431 (64% of existing) |
| ko-KR | 141 / 1,850 (8%) | 7 (5% of existing) |
| zh-HK | 43 / 1,850 (2%) | 0 |
| zh-SG | 54 / 1,850 (3%) | 1 |

**806 of the 1,850 flagged zh-TW files (44%) have at least one sibling locale
(ja-JP and/or zh-CN) independently showing the same corruption signature at
the identical atom path.** Two hand-verified examples, confirming this isn't a
heuristic artifact:

- `atoms/nyc_executives/compassion_fatigue/REFLECTION/locales/ja-JP/CANONICAL.txt`
  — same untranslated-English-body defect as its zh-TW sibling.
- `atoms/corporate_managers/adhd_focus/HOOK/locales/zh-CN/CANONICAL.txt` —
  same raw meta-commentary ("These hooks are powerful because they bypass the
  superficial symptoms of 'busy-ness'...") as its zh-TW sibling.

**Conclusion: the corruption is not a zh-TW-specific translation-run failure.**
Where ja-JP and zh-CN files exist at the same coordinates, they show the same
defect at comparable or higher rates (zh-CN's existing-file suspect rate, 64%,
is actually *worse* than zh-TW's). This points to a shared upstream mechanism
— either a shared English source defect (consistent with §3's
`EN_ALSO_CORRUPTED` finding) or a single multi-locale batch job whose failure
mode was locale-agnostic (consistent with §6's root-cause commits, several of
which explicitly claim multi-locale scope in their own commit messages, e.g.
"zh-TW ≈100%, ja-JP ≈85%" and "CJK primary atom translation wave
(ja-JP+zh-TW+zh-CN)").
ko-KR/zh-HK/zh-SG have too little coverage at these specific paths (2-8%
file-exists rate) to confirm or rule out the same pattern for those locales.

## 5. Root cause — traced by git blame across all 1,850 flagged files (100% attributed)

Every one of the 1,850 flagged files' current content was written by exactly
one of 12 commits touching zh-TW `CANONICAL.txt` paths across the repo's
history (28 commits total ever touched this path pattern). Four commits
account for 1,827/1,850 (98.8%):

| commit | date | files | dominant defect | subject |
|---|---|---:|---|---|
| `85cd624e95` | 2026-04-20 | 752 | META_COMMENTARY (564) | research: 10-chapter bestseller benchmark harness — interim verdict (Scenario C) (#500) |
| `d2d79c4e93` | 2026-04-24 | 593 | UNTRANSLATED_ENGLISH (411) | feat(translation): recover CJK atom translations — zh-TW ≈100%, ja-JP ≈85% (5140 atoms) [owner override: additive-only, 0 deletions] |
| `0ac28088fc` | 2026-06-15 | 361 | EMPTY_STUB (361, 100%) | fix(pearl_prime): restore 1215 CANONICAL.txt pools over-matched by #1590 + CI parse-sweep guard (#1623) |
| `0d1cf1520d` | 2026-06-15 | 121 | EMPTY_STUB (102) | fix(pearl_prime): atom data repair — 1616 CANONICAL.txt headers (label-leak fix) + book#3 exercises (rebuild-proven, do-NOT-merge) (#1590) |
| (8 smaller commits) | various | 23 | mixed | edge cases from otherwise-legitimate translation batches |

### 5.1 Mechanism A — mega "auto backup" commit landed raw agent chat output (752 files, drives META_COMMENTARY)

`85cd624e9502282f491bbae2889095484e3cf5fe` (PR #500, merged 2026-04-20) is a
**4,667-file, purely-additive** commit (`557,942 insertions(+)`, 0 deletions).
Its message body contains a squashed sub-commit literally titled
`chore(backup): auto backup 2026-04-18 19:42:52`. This is the unambiguous
mechanism: **a raw, unreviewed local-agent-session backup/sync was merged into
the repo**, and it included saved chat-completion text — the analysis
commentary and refusal messages an LLM produces when responding
conversationally — written directly to `CANONICAL.txt` paths instead of a
parsed/extracted translated atom body. Nothing in the commit's actual stated
scope (a bestseller-benchmark research harness, `score_external_text.py`, a
presenter HTML page) explains touching thousands of unrelated zh-TW atom
files; those came along for the ride in the squashed backup. 12/12 randomly
sampled META_COMMENTARY files trace to this single commit with no exceptions.

### 5.2 Mechanism B — a "recovery" translation batch that self-reported ~100% but wasn't validated (593 files, drives UNTRANSLATED_ENGLISH)

`d2d79c4e93526070a6ac6f2cb3b0b7c4ea78d219` (2026-04-24, 4 days after #500) is
titled "feat(translation): recover CJK atom translations — zh-TW ≈100%,
ja-JP ≈85% (5140 atoms) [owner override: additive-only, 0 deletions]" — an
explicit **owner override**, meaning it bypassed normal review. Despite
claiming near-complete coverage, 411/593 (69%) of its own files landed as
`UNTRANSLATED_ENGLISH` and another 45 as `EMPTY_STUB`. Cross-referenced with
§3: 92% of this commit's `UNTRANSLATED_ENGLISH` output had a clean English
source available to translate from — so the failure is in the batch
translation step itself (didn't run, or ran and discarded its own output for
a subset of atoms) rather than an unfixable upstream content gap. No
post-hoc validation gate caught the shortfall before merge.

### 5.3 Mechanism C — a "do-NOT-merge" header-repair script merged anyway, then an incomplete restore (482 files combined, 100% EMPTY_STUB)

`0d1cf1520d90628e03b237580f8397cab20a5e88` (PR #1590, 2026-06-15) is titled
"atom data repair — 1616 CANONICAL.txt headers (label-leak fix) + book#3
exercises **(rebuild-proven, do-NOT-merge)**" — the commit's own subject line
says it should not have been merged. It ran an automated header-fixing regex
across 1,619 files and over-matched, corrupting bodies in the process. The
same-day follow-up `0ac28088fc2350d25cd05760afd94667e83584a0` (PR #1623)
explicitly says "restore 1215 CANONICAL.txt pools over-matched by #1590" —
but the restore itself left every one of its 361 touched files as
`EMPTY_STUB` (100%), meaning the "restore" cleared the over-matched damage
without actually recovering the original body content. This is a
governance/process failure (an unsafe script merged against its own stated
warning) compounded by an incomplete remediation.

### 5.4 Verdict

**Not a single mechanism.** Three independent incidents, ~2 months apart,
each contributing a materially different defect signature:
1. unreviewed backup dump → raw chat commentary (Apr 20)
2. unvalidated "recovery" batch → silently-partial translation (Apr 24)
3. an explicitly-unsafe repair script merged despite its own do-not-merge
   label, plus an incomplete restore → emptied bodies (Jun 15)

A later, smaller, well-scoped fix (`c64030ff38`, PR #3127, 2026-06-30,
"re-translate 52 held-back CJK atoms") shows the team was aware of *some*
of this and attempted targeted repair — but even that commit's own output
still shows 12 files with residual `UNCLEAR_MIXED`/`META_COMMENTARY` defects,
meaning even the deliberate fix pass wasn't fully validated either.

## 6. Worst-affected persona/topic pools

| persona pool | flagged | total zh-TW files | % flagged |
|---|---:|---:|---:|
| tech_finance_burnout | 449 | 579 | 77.5% |
| corporate_managers | 289 | 384 | 75.3% |
| working_parents | 188 | 372 | 50.5% |
| entrepreneurs | 177 | 365 | 48.5% |
| first_responders | 141 | 294 | 48.0% |
| gen_x_sandwich | 130 | 288 | 45.1% |
| healthcare_rns | 100 | 301 | 33.2% |
| educators | 50 | 225 | 22.2% |
| nyc_executives | 41 | 225 | 18.2% |
| millennial_women_professionals | 66 | 366 | 18.0% |
| gen_alpha_students | 127 | 720 | 17.6% |
| gen_z_professionals | 75 | 713 | 10.5% |
| gen_z_student | 11 | 234 | 4.7% |
| midlife_women | 6 | 213 | 2.8% |

This confirms the prior session's "concentrated in tech_finance_burnout,
corporate_managers, entrepreneurs, working_parents" observation for the top
two pools specifically (both >75% flagged — three-quarters of every zh-TW
file in these two pools is corrupted), and extends it: `first_responders` and
`gen_x_sandwich` are comparably bad (45-48%) but were not named in the prior
session's list. `working_parents` and `entrepreneurs` sit in the 48-51%
range. The four newer, larger persona pools (`gen_alpha_students`,
`gen_z_professionals`, `gen_z_student`, `midlife_women`) — all built more
recently and larger in raw file count — are comparatively much cleaner
(2.8%-17.6%), consistent with the root-cause commits (§5) predating those
pools' bulk build-out.

## 7. Outputs

- `artifacts/qa/atom_corruption_scope_20260722.tsv` — one row per flagged
  file: `path`, `defect_class`, `en_source_status`, `other_locales_affected`,
  `origin_commit`. 1,850 data rows.
- `artifacts/qa/atom_corruption_scope_20260722.md` — this report.

## 8. Explicitly out of scope / not done in this lane

No file was translated, rewritten, or fixed. No commit was made to any
`atoms/**` content. This is a scoping/classification deliverable only.

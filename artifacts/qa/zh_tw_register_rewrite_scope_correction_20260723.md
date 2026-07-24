# zh-TW Register Rewrite Lane — Scope Correction (2026-07-23)

**Author:** Pearl_GitHub / zh-TW register-rewrite session, branch
`agent/zh-tw-register-rewrite-scope-correction-20260723`
**Input:** `artifacts/qa/zh_tw_rewrite_list_20260722.tsv`, verdict ==
`WRONG_REGISTER_CLEAN_SCRIPT` (1,242 rows), as produced by
`agent/zh-tw-audit-reconcile-v2-20260722`.

## Headline finding

**The 1,242-file `WRONG_REGISTER_CLEAN_SCRIPT` bucket is not a register-editing
worklist. Zero files were rewritten this session, on purpose.**

The verdict name reads as "clean script, wrong register" (i.e. correct
Traditional characters, but Mainland-toned prose — the kind of defect a
native-speaker editorial pass fixes). That is what this rewrite lane was
scoped to do. But the audit's **own evidence column** tells a different story:
every one of the 1,242 rows carries `UNTRANSLATED_ENGLISH` (797 rows, 0% CJK)
or `PARTIAL_UNTRANSLATED` (445 rows, <40% CJK) evidence — a translation-
completeness metric, not a register-quality metric. The audit's companion doc
(`artifacts/qa/zh_tw_rewrite_list_20260722.md`) says this explicitly and was
evidently not read closely before this lane was scoped:

> "Neither prior audit could see this... untranslated English text contains
> zero Simplified Chinese characters — it passes every Simplified-detection
> sweep as 'clean.'" ... "Some fraction of these may be the LLM-meta-commentary
> failure mode, which likely needs the translation to be redone from the
> English source rather than 'fixed,' since no real zh-TW translation attempt
> exists in the file at all." (Recommended next action, Priority 1.)

The audit doc's own recommended next actions do **not** list a register-rewrite
pass for this bucket at all. Register work (Priority 2/3 in that doc) targets
the separate 880-file `TRUE_CONTAMINATION` and 445-file... no — re-read
correctly: Priority 2 = 880 `TRUE_CONTAMINATION` files (genuine Simplified
glyphs — already handled by the `zh-tw-rewrite-contam-*` branches per this
session's branch listing). The `WRONG_REGISTER_CLEAN_SCRIPT` bucket this
session was handed is the untranslated/stub bucket, explicitly *not*
recommended for a register pass.

## Independent verification (16 files hand-read, full side-by-side)

Before trusting either the audit list or its own companion doc, this session
hand-read 16 files spread across the bucket's sub-populations (not just the
first N rows):

| File | Bucket | What it actually contains |
|---|---|---|
| `SOURCE_OF_TRUTH/accent_banks/quotes/adhd_focus/zh_TW.yaml` | YAML quote bank | Fully correct classical-Chinese quotes (Confucius, Mencius); `status: unwired`. Density metric is fooled by English YAML keys (`text_en`, `quote_id`, `author`, `verified_via`). **Already fine — false positive.** |
| `atoms/gen_alpha_students/overthinking/COMPRESSION/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | Literal `# Status: TEMPLATE` / `# Content to be filled in`. **Genuine stub, needs authoring.** |
| `atoms/gen_alpha_students/self_worth/COMPRESSION/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | All section bodies empty between `---` markers. **Genuine stub.** |
| `atoms/gen_alpha_students/overthinking/spiral/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | ~64% of sections empty (RECOGNITION/TURNING_POINT), tail sections (EMBODIMENT/MECHANISM_PROOF) fully authored, coherent, no obvious register defect. **Mixed: partial authoring gap, not register.** |
| `atoms/corporate_managers/anchored/anxiety_comparison/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | Entire file is an LLM assistant's English meta-commentary ("I have processed and stored the Recognition v01-v05... How would you like to proceed? I can: ...") — **not Chinese content at all.** Confirmed same failure mode in 4 more `corporate_managers`/`tech_finance_burnout` files (`adhd_focus/HOOK`, `boundaries/spiral`, `boundaries/overwhelm/TAKEAWAY`, `imposter_syndrome/spiral/PIVOT`) — **5/5 sampled are this failure mode.** |
| `atoms/entrepreneurs/anchored/self_worth/grief/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | 100% authored (19/19 sections), coherent, natural-reading. Read closely against `translate-zh-tw` voice rules: **no Mainland-register markers found.** Flagged by the audit purely because English structural metadata (`path:`/`BAND:`/`MECHANISM_DEPTH:`/etc., present in every atom by design) pulls file-wide CJK density under 40%. |
| `atoms/tech_finance_burnout/depression/grief/locales/zh-TW/CANONICAL.txt` | atoms CANONICAL | 100% authored, full EN-source side-by-side read. Vocabulary is correctly Taiwan-register where it matters (試算表 for "spreadsheet," 臨在 for "presence" — both are the Taiwan-typical terms, not Mainland 表格/在场). Two isolated calque-y phrasings (熱情是看得見的; 重新聲明 for "reclaim") are generic translation-awkwardness, not Mainland-vs-Taiwan register drift. **Not a register-rewrite case; at most a light polish candidate, and not what this list was for.** |
| `SOURCE_OF_TRUTH/practice_library/locales/zh-TW/inbox/body_awareness_library_34_PRODUCTION_READY.json` | JSON practice library | Fully authored, natural-reading Chinese exercise text. Flagged only because the CJK-density script doesn't recognize `"text":` (JSON) as content. File is separately marked inert/unwired pending a loader change — unrelated to register. **False positive.** |
| `SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms_localized/zh-TW/EXERCISE/adi_da_EXERCISE_004_zh-TW.yaml` | teacher-bank YAML | Fully authored (`body:` field, not `text:` — another schema the density script doesn't recognize), natural-reading. **False positive.** |

**Net result of 16/16 hand-reads: 0 files needed a genuine Mainland-register
edit. 5 were pure LLM-meta-commentary garbage (need full re-authoring from the
English source, not editing). 2 were empty stubs. 1 was partially stub.
5 were fully-authored files mislabeled by a density metric that can't parse
their schema (YAML quote-bank, JSON practice library, teacher-bank YAML) —
already correct, no action needed. 3 were fully-authored atom files with no
register defect found on close read.**

## Full-bucket triage (scripted, all 1,242 rows)

To check whether the 16-file sample generalizes, this session wrote a
classifier (`scripts/qa/triage_zh_tw_wrong_register_bucket.py`) that, per
file, strips the structural/English metadata each schema is known to carry
(atom header blocks `path:`/`BAND:`/etc., YAML `text_en:`/`quote_id:`/etc.,
JSON `"text"`/`"body"` keys) and re-measures completeness on the actual body
content only. Full results: `artifacts/qa/zh_tw_wrong_register_bucket_triage_20260723.tsv`.

| Triage bucket | Count | Meaning |
|---|---:|---|
| `NO_SECTIONS` | 616 | No recognized atom header structure at all — the 5/5 hand-read sample here was 100% LLM-meta-commentary garbage. Needs re-authoring from EN source, or deletion + regeneration. **Not this lane's job.** |
| `AUTHORED_CANDIDATE` | 203 | All sections non-empty, body CJK density ≥50% after stripping metadata. Genuinely complete files — hand-read sample (3/3) found solid, coherent prose with no clear register defect. **The closest thing to a real register-review pool in this bucket, but still unverified for register at scale — see below.** |
| `AUTHORED_LOW_BODY_CJK` | 139 | Sections non-empty but body CJK density still <50% even after stripping known metadata — could be genuine code-switched/mixed content, or an unrecognized schema. Not individually verified this session. |
| `STUB_MAJORITY_EMPTY` | 105 | >50% of sections empty. Authoring-gap, not register. |
| `PARTIAL_SOME_EMPTY` | 97 | 5–50% of sections empty (the "spiral" pattern — some variants authored, some are bare stub headers with no body). Needs section-level authoring for the empty variants; the filled variants are unverified for register. |
| `YAML_TEXT_OK_STRUCTURAL_FALSE_POSITIVE` | 82 | SOURCE_OF_TRUTH yaml/json files (quote banks `text:`, teacher-bank `body:`, JSON practice-library `"text"`/`"body"`) where the actual content key is populated with CJK text. Hand-read samples (3/3: adhd_focus quote bank, body_awareness practice library, adi_da EXERCISE_004) were all genuinely fine. **Already correct — drop from any future rewrite list.** |

## Why no files were rewritten this session

Editing any of the `NO_SECTIONS` / `STUB_MAJORITY_EMPTY` / `PARTIAL_SOME_EMPTY`
files "for register" would mean fabricating Chinese content where none exists
today and calling it a register fix — that is exactly the "stub-as-done" drift
class this repo's CI already guards against in the manga domain
(`check_render_progress_bytes.py`), applied here to translation instead of
render bytes. Editing the `AUTHORED_CANDIDATE` / false-positive files under
this list's justification would be editing files that are already fine, per
both this session's and the original audit's own sampling (0/19 in the audit's
sample, 0/8 in this session's sample of fully-authored files showed Mainland
register drift). Neither is honest "genuine native-speaker editorial rewrite
of Mainland-register-but-correct-script prose" — the actual target category
this lane was supposed to work on.

## Where the real work is

1. **Untranslated/stub bucket (the ~820 `NO_SECTIONS` + `STUB_MAJORITY_EMPTY`
   files, concentrated in `corporate_managers` and `tech_finance_burnout` per
   the audit doc's own persona breakdown)** — this is a translation/authoring
   task, not a register task. It *may* overlap with
   `artifacts/qa/atom_authoring_backlog_20260722.tsv` (651 "EN_ALSO_CORRUPTED"
   rows, commit `386bf02beff9f88850e72f3f48d1cd4fa40fc91b`) — **but that commit
   is only on the local `agent/bestseller-atom-flow-lanes-20260721` branch, not
   on `origin/main`, and its scope is English-source corruption, which is a
   different defect from zh-TW-only untranslated content.** Check for actual
   path overlap before assuming they're the same list — this session did not
   have time to cross-reference the two TSVs row by row.
2. **Genuine Mainland-register drift, if it exists at scale, has not actually
   been measured.** The original audit's own doc is explicit: its 19-file
   register sample of the real `CLEAN` bucket (2,311 files, the ones that
   *are* fully translated and script-clean) found 0 hits and called the true
   rate "UNMEASURED AT SCALE." **If the operator wants the register-editing
   work this lane was framed around, the correct input list is a fresh,
   register-focused sample of the 2,311-file `CLEAN` bucket — not the
   1,242-file `WRONG_REGISTER_CLEAN_SCRIPT` bucket.** That sample does not
   exist yet and would need to be built (e.g. stratified read of 100-200
   `CLEAN` files against `translate-zh-tw` voice rules, flagging real
   Mainland-vocabulary/idiom hits) before a rewrite lane like this one could
   execute against it.
3. Two isolated polish-level phrasings were noted in passing
   (`atoms/tech_finance_burnout/depression/grief/locales/zh-TW/CANONICAL.txt`,
   TURNING_POINT v02 and EMBODIMENT v01/v02/v04 "重新聲明" for "reclaim") —
   left unedited this session since the file wasn't a confirmed register
   case and editing single files outside a defined, verified worklist risks
   more scope drift than it's worth. Flagged here for whoever builds the
   real register worklist in point 2.

## Resume marker / ledger

- **Files rewritten this session: 0** (by design — see above).
- **Files hand-verified: 16** (8 in the initial spot-check, 8 more spread
  across the scripted triage's buckets).
- **Files scripted-triaged: 1,242 / 1,242 (100% of the bucket)** —
  `artifacts/qa/zh_tw_wrong_register_bucket_triage_20260723.tsv`.
- **Next session should NOT** re-run this lane against
  `zh_tw_rewrite_list_20260722.tsv`'s `WRONG_REGISTER_CLEAN_SCRIPT` verdict as
  a register worklist. It should either (a) pick up the untranslated/stub
  reconciliation in "Where the real work is" §1, or (b) build and then work
  the register-focused `CLEAN`-bucket sample in §2 — whichever the operator
  prioritizes.
- **Glossary/registry used:** none applied this session (no edits made).
  For reference, the character-name registry the operator asked to be used
  for consistency once real edits happen: `analysis/character_name_registry_zh_tw.yaml`
  does not exist on `origin/main` yet. Its most-resolved form lives on open PR
  `#67` (`agent/zhtw-name-registry-resolutions-20260722`), built on top of PR
  `#61`. The task brief's premise that "PR #72 landed for corporate_managers"
  is incorrect as of this session — **PRs #61, #67, #69, #72, #78, #80 are
  all still OPEN, none merged**, per `gh pr list`/`gh pr view` checked live
  this session. Whoever does the real register edits in point 2 above should
  re-check merge state again before trusting this note, and should pull
  character names from PR #67's branch tip regardless of merge state, per the
  task's own collision-handling instruction.

## Signal token

`ZHTW_REGISTER_REWRITE_0_1242` — 0 files rewritten this session (correct
outcome: the 1,242-file input list does not contain the defect class this
lane was scoped to fix), full 1,242-row bucket triaged and categorized,
scope-correction + resume ledger delivered for the next session.

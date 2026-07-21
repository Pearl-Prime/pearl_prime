# ja-JP Teacher-Bank Translation Closure — 2026-07-10

**Agent:** Pearl_Localization
**Branch:** `agent/ja-jp-teacher-bank-translation-20260710` (from `origin/main` @ `4067366556fedfd99913fbd3806d78af53d32b5a`)
**Scope:** `SOURCE_OF_TRUTH/teacher_banks/**` ja-JP atom translation. This is a
**structurally separate body of work** from the persona/topic bestseller-atom
tree (`atoms/{persona}/{topic}/{slot}/CANONICAL.txt`, owned by
`ws_cjk_atom_translation_qwen25_20260420` / `scripts/translate_atoms_all_locales_cloud.py`).
Neither reads nor writes anything under `atoms/**`, `zh-TW`, or `zh-CN`.

## Honest status: PARTIAL, real, verified — not full closure

51 teacher-bank atoms genuinely translated to ja-JP this session (0 → 146 of
2,399 in-scope atoms, +51 net). One teacher (`kenjin`) taken from 0% to 100%.
One teacher (`junko`) newly seeded from 0% to 18% with two slots (HOOK,
PERMISSION) fully closed. `adi_da`'s previously-zero COMPRESSION slot closed
(now 20/20), moving that teacher from 36% to 44% overall. **13 of 15 teacher
banks remain untouched at 0% ja-JP.** This is a real, proven, quality-checked
first batch — not the full backlog, and not claimed as such.

## Pre-requisite checks (re-derived live, not trusted from the task brief)

1. **Live `origin/main` SHA:** `4067366556fedfd99913fbd3806d78af53d32b5a`
2. **Open-PR overlap:** `gh pr list --state open --search "teacher_bank OR ja_JP OR localization OR translation"`
   returned 30+ open PRs. Checked file lists of the two most relevant
   (`#5496` — ja-JP bestseller atoms, `#5499` — zh-TW bestseller atoms) via
   `gh pr view <n> --json files`: both touch only `atoms/{persona}/{topic}/{slot}/locales/**`
   and `scripts/translate_atoms_all_locales_cloud.py`. **No open PR touches
   `SOURCE_OF_TRUTH/teacher_banks/**`.** No overlap; safe to proceed.
3. **Re-derived backlog** via `python3 scripts/localization/teacher_bank_locale_parity.py --locales ja-JP --verbose`
   run live from a clean `origin/main` worktree — see table below. Confirms
   (does not just repeat) the task brief's figures: 14/15 teacher banks at 0%,
   `adi_da` at 36% (95/260) missing only `COMPRESSION`, before this session.
   **Correction to the brief's estimate:** the brief said "~1,900+ atoms
   (14 teachers × ~135 avg × up to 11 slots)". The exact re-derived total is
   **2,399 en-US atoms across all 15 teachers, of which 2,304 had zero ja-JP
   coverage** before this session (i.e. the real gap was larger than "~1,900",
   not smaller — ~1,900 undercounted `ahjan` at 315 and `adi_da`'s untranslated
   165/260).
4. **Path convention correction.** The task brief's assumed convention
   (`SOURCE_OF_TRUTH/teacher_banks/**/locales/ja-JP/*.yaml`) does **not** match
   what's on disk. The real, confirmed convention is:
   - English source: `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms/{SLOT}/{atom_id}.yaml`
   - ja-JP output: `SOURCE_OF_TRUTH/teacher_banks/{teacher}/approved_atoms_localized/ja-JP/{SLOT}/{atom_id}_ja-JP.yaml`

   (`{SLOT}` ∈ `COMPRESSION, EXERCISE, HOOK, INTEGRATION, PERMISSION, PIVOT,
   REFLECTION, SCENE, STORY, TAKEAWAY, THREAD` — `TEACHER_DOCTRINE` is
   deliberately excluded; it is reference doctrine material, not a per-atom
   translatable slot, and `teacher_bank_locale_parity.py`'s own `SLOT_TYPES`
   list excludes it too.) This is the convention `teacher_bank_locale_parity.py`
   already reads and the one the 95 pre-existing `adi_da` translations already
   follow — confirmed by inspecting real files on disk, not assumed.

## Decision: new narrow script, not an extension of `translate_atoms_all_locales_cloud.py`

Traced both candidate owners per the mission's step 5:

- `scripts/translate_atoms_all_locales_cloud.py`: `discover_atoms()` walks
  `atoms_root.rglob(f"{slot}/CANONICAL.txt")` and `output_path_for()` returns
  `atoms_root / persona / topic / slot_type / "locales" / locale / "CANONICAL.txt"`.
  Confirmed by direct grep — neither function contains the string
  `teacher_banks` anywhere in the file, and the whole file operates on
  plain-text, multi-variant `CANONICAL.txt` files parsed by a
  `## TYPE vNN` / `---` delimiter grammar (`parse_canonical`/`format_canonical`).
- `scripts/localization/run_translation_loop.py`: same story — `discover_atoms()`
  hardcodes `atoms_root = REPO_ROOT / "atoms"` and the same `locales/CANONICAL.txt`
  shape.
- Teacher-bank atoms are a **different file shape entirely**: one structured
  YAML file per atom, with a single `body` string plus a `teacher` block, and
  *slot-varying* extra metadata fields (`hook_type`, `story_origin`,
  `mechanism_depth`, `identity_stage`, `cost_type`, `compression_family`, etc.)
  that must be preserved byte-for-byte across the translation, not just a
  swapped-in prose body inside fixed delimiters.

**Decision:** built a narrow new script,
`scripts/localization/translate_teacher_bank_atoms.py`, rather than bending
the CANONICAL.txt-shaped script onto a YAML-shaped problem (which would have
meant a much larger, riskier rewrite of `parse_canonical`/`format_canonical`/
`validate_translation` to handle a fundamentally different grammar). It
**reuses, not duplicates**, the shared provider-routing engine
(`scripts.localization.llm_client.call_llm_with_meta` /
`get_client_config` — the exact fix landed in PR #5496/#5498 for the free
Ollama path) and the locale name table
(`scripts.translate_atoms_all_locales_cloud.LOCALE_NAMES`, imported not
copied).

## LLM Tier Policy compliance

- The script **hard-refuses** to run a real (non-dry-run) translation unless
  the resolved LLM client mode is `"ollama"`. It explicitly unsets all five
  banned-by-CLAUDE.md paid keys (`DEEPSEEK_API_KEY`, `TOGETHER_API_KEY`,
  `GOOGLE_AI_API_KEY`, `CLOUDFLARE_AI_API_TOKEN`, `DASHSCOPE_API_KEY`) for the
  process before resolving the client, so a leftover keychain-loaded key can
  never silently route to a paid provider (see `resolve_ollama_only_client()`).
- Verified live: `OLLAMA_HOST=http://pearlstar.tail7fd910.ts.net:11434`,
  `OLLAMA_MODEL=qwen2.5:14b` — reachable, `qwen2.5:14b` present via
  `/v1/models` — the same compliant Pearl Star endpoint and model used by the
  sibling PR #5499 (zh-TW) this session.
- `python3 scripts/ci/audit_llm_callers.py` — run before push; see
  CLOSEOUT_RECEIPT for the pass/fail result on this branch's diff.

## What shipped in this session

**51 new ja-JP teacher-bank atom translations**, real, spot-checked in full
(not just script-validated):

| Teacher | Slot | Count | Before → After (teacher, ja-JP) |
|---|---|---|---|
| `kenjin` | STORY | 4 | 0% → **100%** (4/4 — teacher fully closed) |
| `adi_da` | COMPRESSION | 20 | teacher 36% → 44% (COMPRESSION slot: 0/20 → 20/20) |
| `junko` | HOOK | 12 | slot 0/12 → 12/12 |
| `junko` | PERMISSION | 15 | slot 0/15 → 15/15 |

Teacher-level before/after (from `teacher_bank_locale_parity.py --json-out`,
re-run live before and after):

| Teacher | en-US total | ja-JP before | ja-JP after |
|---|---|---|---|
| kenjin | 4 | 0 (0%) | **4 (100%)** |
| adi_da | 260 | 95 (36%) | 115 (44%) |
| junko | 152 | 0 (0%) | 27 (18%) |
| (12 other teachers) | 2,152 | 0 | 0 (untouched — out of this batch's scope) |
| **Total (15 teachers)** | **2,399** | **95 (4.0%)** | **146 (6.1%)** |

All 51 output files live under
`SOURCE_OF_TRUTH/teacher_banks/{kenjin,adi_da,junko}/approved_atoms_localized/ja-JP/{STORY,COMPRESSION,HOOK,PERMISSION}/`.

## Real quality-gate catch during this session (not hypothetical)

The first pass surfaced two genuine defects the initial validator missed, both
in `junko` PERMISSION atoms:

1. `junko_PERMISSION_001` — the model appended a leaked self-correction note
   in English: `"(Note: There seems to be a slight issue with the last part
   of the sentence. Let me correct it for natural flow.)"` followed by a
   duplicated corrected sentence, plus a stray Simplified Chinese character
   (`承认`) mixed into the first (bad) attempt.
2. `junko_PERMISSION_003` — the model left the term "council" untranslated
   (misspelled "councill") and added an inline Japanese parenthetical
   explaining it couldn't translate the term directly — consistent across 3
   repeated attempts at the original prompt/temperature (verified by manually
   re-invoking `translate_one()` 3× — same failure every time).

**Fixed, not worked around:**
- Hardened `validate_translation()` in the new script: added an
  English-language leak-marker list, a Japanese-language leak-marker list
  (`直接翻訳`, `原文のまま`, `翻訳できない`, etc.), and an ASCII-letter-density
  heuristic (CJK6 output should be near-zero Latin-script; >20 or >15% ASCII
  letters is flagged as likely leaked commentary).
- Added validation-retry (not just transient-error retry) to `translate_one()`
  with escalating temperature per retry, since the failure was often
  deterministic at fixed low temperature.
- Strengthened `system_prompt()` with two explicit new rules: never comment
  inline on translation-difficulty (in either language), and translate
  ambiguous terms confidently (transliterate if needed) rather than leaving
  them in English or hedging.
- Re-ran both affected atoms after the fix: `junko_PERMISSION_001` passed
  clean on retry 1; `junko_PERMISSION_003` needed the prompt hardening (not
  just the validator) — passed clean on the first attempt after that change.
- **Full re-validation of all 51 written files** against the hardened
  validator, cross-checked against their English sources: **0 failures**.

This is the reason the batch scope (51, not more) is smaller than the
"~2 teachers fully" originally sketched — real time went into catching and
fixing this defect class rather than mechanically maximizing atom count.

## Quality-contract verification

- `python3 scripts/check_golden_translation.py --locales ja-JP zh-CN zh-TW ko-KR zh-HK zh-SG`
  → **Golden translation check OK (8 segments × 6 locale(s))**. (This gate is
  scoped to `atoms/**` only — confirmed by reading `ATOMS_ROOT` in
  `scripts/check_golden_translation.py` — so it does not cover teacher-bank
  atoms directly; it's included per the mission's explicit instruction and to
  prove this lane did not regress the bestseller-atom gate.)
- `python3 scripts/localization/teacher_bank_locale_parity.py --locales ja-JP --verbose --json-out artifacts/localization/teacher_bank_parity_after_20260710.json`
  → GATE PASS (advisory-only threshold, `min_teacher_bank_parity_cjk: 0.0` in
  `config/localization/quality_contracts/release_thresholds.yaml` — this was
  never a hard blocker, just an honesty check).
- Full re-validation of all 51 new files against source English (script-level
  `validate_translation()`, hardened) → **0 failures**.
- `python3 scripts/ci/audit_llm_callers.py` — see CLOSEOUT_RECEIPT.

## Residual backlog and exact resume path

**2,253 teacher-bank atoms remain at zero/partial ja-JP coverage** (2,399
total − 146 now translated), across 14 teachers (all except `kenjin`).
Nearest-complete teachers for a follow-up session:

- `adi_da`: 145/260 remaining (EXERCISE 28, HOOK 24, INTEGRATION 14, PERMISSION 15, PIVOT 12, REFLECTION 24, SCENE 14, STORY -10 [sic, over-translated legacy data — see note below], TAKEAWAY 12, THREAD 12)
- `junko`: 125/152 remaining (COMPRESSION 12, EXERCISE 12, INTEGRATION 12, PIVOT 15, REFLECTION 12, SCENE 12, STORY 20, TAKEAWAY 15, THREAD 15)
- 12 teachers still fully untouched (0%): `ahjan` (315), `joshin` (148),
  `maat`, `master_feung`, `master_sha`, `master_wu`, `miki`, `miyuki`,
  `omote`, `pamela_fellows`, `ra`, `sai_ma` (152 each).

**Note on adi_da STORY:** `teacher_bank_locale_parity.py` reports adi_da
STORY at 30 ja-JP files against 20 en-US source files — i.e. 10 more
localized files than source atoms exist. This predates this session (present
in the 95-atom baseline, not touched by this batch) and looks like a stale/
orphaned-file issue in the pre-existing translations, not a new defect. Flagged
as a follow-up (see below); not investigated further here (out of this
session's `approved_atoms_localized` write scope beyond the 3 teachers this
batch touched).

**Exact resume command** (same tool, continues where this session left off):

```bash
unset DASHSCOPE_API_KEY DEEPSEEK_API_KEY TOGETHER_API_KEY GOOGLE_AI_API_KEY CLOUDFLARE_AI_API_TOKEN
export OLLAMA_HOST="http://pearlstar.tail7fd910.ts.net:11434"
export OLLAMA_MODEL="qwen2.5:14b"
python3 scripts/localization/translate_teacher_bank_atoms.py \
  --locale ja-JP --resume --max-atoms 10 --rate-limit-s 1.0 \
  --checkpoint-path artifacts/localization/ja_jp_teacher_bank_20260710/checkpoint.jsonl \
  --output-log artifacts/localization/ja_jp_teacher_bank_20260710/output_log.jsonl
```

Omit `--teacher`/`--slot` to walk the full remaining manifest in discovery
order (alphabetical by teacher, then slot); pass `--teacher <id>` to target a
specific teacher. `--resume` skips anything already present on disk or in the
checkpoint. Run in `--max-atoms 10`–`20` chunks per invocation (observed
latency: ~3–12s/atom for short slots like COMPRESSION/HOOK/PERMISSION,
~30–45s/atom for long-form STORY atoms) — do not park a background Monitor
waiting on this; run it synchronously in chunks or accept it as a genuinely
multi-session backlog (2,253 atoms at even 10s/atom average is ~6.3 hours of
continuous unattended Ollama time).

## Follow-ups flagged (out of this lane's scope, not attempted here)

1. **adi_da STORY over-count** (30 ja-JP files vs 20 en-US source files) —
   needs investigation into whether 10 files are orphaned/stale or the parity
   script's counting has an edge case with this teacher's STORY directory.
   Not touched by this session.
2. **12 of 15 teacher banks remain fully untouched at 0% ja-JP** — this batch
   deliberately proved the pipeline end-to-end (new script + quality gate
   hardening) on 3 teachers rather than spreading thin across all 15. The
   resume command above walks the rest.
3. Consider promoting `min_teacher_bank_parity_cjk` in
   `config/localization/quality_contracts/release_thresholds.yaml` from its
   current advisory `0.0` to a real floor once coverage is meaningfully
   higher — not proposed as a change in this PR (would immediately fail CI at
   current ~6% coverage; a policy decision for the owner, not a drive-by
   change here).

# zh-TW Translation Reconcile — 2026-07-10

**Agent:** Pearl_Localization
**Workstream:** `ws_cjk_atom_translation_qwen25_20260420` (owner: Pearl_Localization, `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`)
**Branch:** `agent/zh-tw-translation-reconcile-20260710` (from `origin/main` @ `4067366556fedfd99913fbd3806d78af53d32b5a`)

## Honest status: TRUTH RECONCILED + PARTIAL real translation advance

The "zh-TW complete / 92.1%" claim is **reconciled with live evidence**, not
hand-waved. The 92.1% figure was accurate *at the time it was measured*
(2026-04-24, `PR #601` merge: 3,161/3,431 = 92.1%), but is now stale on two
independent axes:

1. **Corpus growth.** The English source corpus grew from 3,431 → 3,752 atom
   files between 2026-04-24 and today (topic-scaffolding additions — most of
   the residual is `adhd_focus` + `mindfulness`, added **2026-06-30**
   (`b06eb0f8e2`), 2+ months after the zh-TW translation wave landed). zh-TW
   translations also grew in that window (3,161 → 3,589 true count — see
   below) but did not fully keep pace with new English source additions.
2. **A real tool bug in the standing coverage reporter**, independently found
   and already fixed by a sibling session as **PR #5497**
   (`fix(ci): make translation coverage counting depth-independent`,
   `agent/translation-coverage-depth-fix-20260710`, based on the same
   `origin/main` SHA as this branch, **not yet merged**). `_bestseller_translated_count()`
   in `scripts/ci/report_translation_coverage.py` derived
   `(persona, topic, slot)` from fixed positional path indices
   (`rel.parts[0..2]`), assuming every English source sits at exactly
   `atoms/{persona}/{topic}/{slot_or_engine}/CANONICAL.txt` (4 levels deep).
   ~36% of the real atom tree nests one level deeper
   (`atoms/{persona}/{topic}/{subtopic}/{engine}/CANONICAL.txt`, e.g.
   `entrepreneurs/anchored/anxiety/comparison/CANONICAL.txt`), so the tool
   checked a nonexistent locale path for those entries and under-reported
   coverage. **This session independently derived and verified the identical
   bug and fix before the coordinator flagged PR #5497 already existed** — see
   "Independent verification" below. Per the coordinator's instruction, this
   branch does **not** duplicate that fix (would conflict with PR #5497 on the
   same file/lines); PR #5497 is cited as authority for the corrected reporter
   output.

### Independent verification (before PR #5497 was known)

Computed directly from the live `atoms/` tree in this worktree (no reliance on
`report_translation_coverage.py` at all — walked every English source and
checked for a sibling `locales/zh-TW/CANONICAL.txt` under the *same parent
directory as the source*, regardless of nesting depth):

| | Buggy reporter (pre-#5497, current `main`) | True / PR #5497-fixed |
|---|---|---|
| English source files (bestseller slots + 7 engines) | 3,752 | 3,752 |
| zh-TW translated | 3,365 | **3,589** |
| zh-TW coverage | 89.7% | **95.7%** |
| zh-TW missing | 387 (224 false negatives — real files exist 1 level deeper than the buggy check looked) | **163 (real, verified missing)** |

The 163 real-missing files are **100% at the standard 4-level depth**
(`persona/topic/slot/CANONICAL.txt`) — i.e. exactly the paths
`scripts/translate_atoms_all_locales_cloud.py`'s `discover_atoms()` /
`output_path_for()` already handle correctly; no tooling changes were needed
to execute translation for this residual.

**Verdict on the mission's question ("real missing translation, exempted
content, or stale reporting drift?"): all three, cleanly separated.**
- 224 of the originally-apparent 387 "missing" were **stale reporting drift**
  (the depth bug — PR #5497).
- The remaining **163 are real, un-exempted missing translation** — new
  English atoms added 2026-06-30, after the original translation wave, never
  translated into zh-TW. Not exempted content (no exemption list applies to
  bestseller PIVOT/TAKEAWAY/THREAD/PERMISSION/STORY/engine atoms).

## Open-PR overlap check (pre-req #2)

`gh pr list --state open --search "zh_TW OR localization OR translation"`
returned 31 open PRs. All `feat(catalog): zh_TW skeletons {brand} batch {N}`
PRs touch `config/source_of_truth/book_plans_zh_tw/*.yaml` (catalog listing
skeletons — a different subsystem). The only translation-execution PRs open
are `#5496` (ja-JP, `atoms/**/locales/ja-JP/**` only) and `#5495` (pt-BR/es-US).
**No open PR touches `atoms/**/locales/zh-TW/*.txt`.** Safe to proceed.

## What shipped in this session

**6 real zh-TW bestseller-atom translations**, translated via `qwen2.5:14b` on
Pearl Star (Ollama, free/Tier-2, CLAUDE.md-compliant — DashScope/DeepSeek/
Together/Google-AI/Cloudflare paid keys explicitly unset before every call;
verified provider resolution == `ollama` before dispatch):

- `atoms/corporate_managers/adhd_focus/PERMISSION/locales/zh-TW/CANONICAL.txt`
- `atoms/corporate_managers/adhd_focus/PIVOT/locales/zh-TW/CANONICAL.txt`
- `atoms/corporate_managers/adhd_focus/TAKEAWAY/locales/zh-TW/CANONICAL.txt`
- `atoms/corporate_managers/mindfulness/PERMISSION/locales/zh-TW/CANONICAL.txt`
- `atoms/corporate_managers/mindfulness/PIVOT/locales/zh-TW/CANONICAL.txt`
- `atoms/corporate_managers/mindfulness/TAKEAWAY/locales/zh-TW/CANONICAL.txt`

| | Before this session | After this session |
|---|---|---|
| English source files (bestseller slots + 7 engines) | 3,752 | 3,752 |
| zh-TW translated (true count) | 3,589 | **3,595** |
| zh-TW true coverage | 95.7% | **95.82%** |
| zh-TW true missing | 163 | **157** |

Spot-checked `atoms/corporate_managers/mindfulness/PIVOT/locales/zh-TW/CANONICAL.txt`
in full: 12/12 variants present, real Traditional Chinese prose (e.g. 「你的思緒正在重複練習你最害怕的QBR問題」),
not Simplified, not stub, not English-identical, headers preserved exactly
(`## PIVOT v01` etc., English, per spec).

Each file validated by `scripts/translate_atoms_all_locales_cloud.py`'s own
`validate_translation()` (variant count matches source, headers stay English,
prose is non-empty / non-identical-to-English / not header-only) before being
written — no unvalidated output landed.

**Driver:** a standalone script (not committed — kept out of `scripts/` to
avoid touching/conflicting with the shared `translate_atoms_all_locales_cloud.py`
tool file that sibling PR #5496 also modifies) that imports
`discover_atoms` / `run_job` / `RateLimiter` / `output_path_for` /
`validate_translation` directly from that module and drives them against
exactly the 163-key residual set derived above — same execution surface and
validation the canonical tool uses, just invoked without touching the shared
file.

## Blocker — Pearl Star hardware throughput (not policy, not tooling)

Same root cause independently confirmed by sibling PR #5496 (ja-JP): `qwen2.5:14b`
on Pearl Star is only partially GPU-offloaded. Measured in this session (6
completed atoms, `artifacts/localization/zh_tw_reconcile_20260710/output_log.jsonl`):
latency per atom was 56s, 148s, 197s, 250s, 287s, 261s — rising under sustained
concurrent dispatch (workers=4), consistent with GPU/VRAM self-contention on a
single partially-offloaded 14B model rather than true 4-way parallelism (same
conclusion as PR #5496's `/api/ps` finding of ~33% VRAM offload). Sustained
observed rate in this session: ~6 atoms / 50 minutes ≈ 8.3 min/atom average
under contention.

**Exact residual after this session: 157 files.** At the observed sustained
rate, closing the full 157-file residual requires roughly **13–20 hours of
continuous runtime** — within the Tier-2 "free, unattended" design intent
(this is meant to run unattended on a schedule, not be babysat synchronously
in one interactive session), but beyond what this session could complete.
The batch process was stopped cleanly (SIGKILL after the last successful
checkpoint write; `run_job` writes the output file and appends the checkpoint
line synchronously before returning, so no partial/corrupt file was left
on disk) rather than left running unattended past this session's close.

## Resume command (exact — verified working)

```bash
unset DASHSCOPE_API_KEY DEEPSEEK_API_KEY TOGETHER_API_KEY GOOGLE_AI_API_KEY CLOUDFLARE_AI_API_TOKEN
export OLLAMA_HOST="http://pearlstar.tail7fd910.ts.net:11434"
export OLLAMA_MODEL="qwen2.5:14b"
python3 scripts/translate_atoms_all_locales_cloud.py \
  --locale zh-TW --resume --batch-size 2 --rate-limit 0.2 \
  --checkpoint-path artifacts/localization/zh_tw_reconcile_20260710/checkpoint.jsonl \
  --output-log artifacts/localization/zh_tw_reconcile_20260710/output_log.jsonl
```

This is the **canonical tool** (not this session's driver) — safe because the
163-key residual is 100% at the 4-level depth the canonical tool already
handles correctly, and `--resume` skips anything already valid (matching the
checkpoint committed in this branch). `--batch-size 2` recommended over 4
given the partial-VRAM-offload contention observed (matches PR #5496's
finding).

## Quality checks

- [x] `python3 scripts/check_golden_translation.py --locales zh-CN zh-TW ja-JP ko-KR zh-HK zh-SG` → 8/8 segments × 6 locales, before and after this session's writes
- [x] Every written file passed `validate_translation()` (variant count match, English headers preserved, non-empty/non-English-identical prose)
- [x] Spot-checked translated files for real, coherent Traditional Chinese content (not stub/garbage/Simplified)
- [x] `python3 scripts/ci/audit_llm_callers.py --roots artifacts/localization scripts/translate_atoms_all_locales_cloud.py scripts/localization --fail-on-violation` → `{"violation_count": 0}` (full-repo unscoped run was pathologically slow in this sandbox — >10 min with no output on an otherwise-unmodified script; scoped the audit to the changed surfaces per the same pattern PR #5496 used, consistent with the mission's actual concern: no banned key introduced by this session's diff)
- [x] `PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py` → OK, no violations
- [x] No `translation execution scripts` touched (this session's duplicate fix to `report_translation_coverage.py` was reverted once PR #5497 was confirmed to already cover it)
- [x] `git status` scoped strictly to `atoms/**/locales/zh-TW/*.txt`, `artifacts/localization/zh_tw_reconcile_20260710/**`, and this closeout doc

## Scope discipline

- No ja-JP / zh-CN / zh-HK / zh-SG / ko-KR files touched.
- No manga or book-pipeline code touched.
- `docs/PROGRAM_STATE.md` and `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
  intentionally **not** edited (out of scope per task instructions) — this
  closeout doc is the durable evidence trail; the workstream row's "zh-TW
  COMPLETE (92.1%)" note should be updated by the owning PM lane to
  "95.7% true baseline (PR #5497) + N/163 closed this session, see this
  closeout" the next time that TSV is touched.

## Follow-ups (not fixed in this session — flagged, not hand-waved)

1. **PR #5497 merge** — the depth-independent coverage fix should land so the
   standing reporter stops mis-measuring all CJK6 locales (not just zh-TW).
2. **Full 157-file zh-TW closure** — resume command above; genuinely
   hardware-bound (Pearl Star qwen2.5:14b throughput), not blocked by policy
   or tooling. Same class of blocker as ja-JP (PR #5496) and likely zh-CN
   (much larger backlog, ~2,130 by the corrected count).
3. **zh-CN backlog is far larger than zh-TW** (`~2,130` missing by the
   PR #5497-corrected count vs zh-TW's 163) — out of scope for this lane
   (explicit OUT_OF_SCOPE), but worth flagging to whichever lane owns zh-CN
   next: the ACTIVE_WORKSTREAMS row's "~2,200 atoms" zh-CN estimate is close
   to the corrected number, unlike the zh-TW row which was stale on both
   axes described above.

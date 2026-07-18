# Pearl Translator 14-Locale Dispatch — Handoff

**Agent:** Pearl_PM_Dispatcher
**Date:** 2026-07-15
**Pack:** `docs/agent_prompt_packs/20260715_pearl_translator_14_locale_100pct/`
**`origin/main` at dispatch:** `e754cce3d4e635d69657490b02ad1ac9afdb64c4`
**Runtime host:** operator Mac (`darwin`), local checkout `/Users/ahjan/phoenix_omega`
**Proof root:** `artifacts/qa/pearl_translator_14_locale_scope_20260715/SCOPE_LOCK.md`

---

## Outcome

| Wave | Lane | Status |
|---|---|---|
| 0 | `01` scope lock + failure audit | **MERGED** |
| 0.5 | `02` worklist/gate substrate | **BLOCKED** — not launched |
| 1 | `03` ja-JP, `04` zh-CN, `05` zh-TW | **BLOCKED** — not launched |
| 2 | `06` zh-HK, `07` zh-SG, `08` ko-KR | **BLOCKED** — not launched |
| 3 | `09` es-US … `15` pt-BR | **BLOCKED** — not launched |
| 4 | `16` aggregate QA gate | **NOT RUN** — no lane produced new coverage |
| 5 | `17` final closeout | **NOT RUN** — Wave 4 precondition unmet |

**No translation lane was launched. This was deliberate and is contract-compliant**, per
`00_MASTER_DISPATCH_PROMPT.md`: *"If cloud agents cannot use Claude Sonnet, BLOCK before
translation rather than silently switching model family."* Both model paths are blocked
(scope lock §4), so blocking **before** translation — rather than after burning spend on a
pilot that cannot loop to zero — is the specified behaviour.

`DISPATCH RULES` also forbid launching any locale lane before Prompt 02 emits
`translation-worklist-substrate=<sha>`. Prompt 02 was not launched, so no locale lane was
ever eligible.

## Why (one paragraph)

39,474 file-translations remain across 13 locales — **~46.2M words of prose** (5,212 source
atoms, 6,095,281 words, ~1,170 words/atom, all measured). Path A (Sonnet, as the pack
mandates) is >100M output tokens and ~1,579 governance-gated PRs at the pack's own 25-file
batch size. Path B (Tier-2 Qwen on Pearl Star, per `CLAUDE.md` Tier Policy) measured **8.4
tok/s fully warm** (`load_duration` 0.08s) against `qwen2.5:14b` — vs 40–80 tok/s expected —
which is ~109 days of continuous single-stream GPU time. That 8.4 tok/s reproduces the
GPU-VRAM-saturation blocker diagnosed on **2026-07-11** and still unresolved. The pack's
process fixes are real improvements; they do not create throughput.

## Lane collision — read before re-dispatching

`ws_cjk_atom_translation_qwen25_20260420` is **active**, owner **Pearl_Localization**, branch
`agent/translation-cjk-qwen25-20260420`. It already owns this mission and has already paid for
the findings above. **Any re-dispatch must route through that owner, not around it.** Its
recorded, still-live findings:

- GPU/VRAM throughput blocker (the decisive one).
- Queue-first `pscli` dispatch is the clean Tier-2 path (Ollama-only, no cloud fallback).
- **93 of zh-TW's 157 remaining gaps are a `validate_cjk_atom.py` role-schema bug, not
  translation.** zh-TW is 95.9% — the only locale near a real 100% claim.
- `run_translation_loop.py` / `llm_client.py` cloud-first provider chain = live Tier-policy
  risk with DeepSeek/Together/DashScope keys in the operator env.
- Deployed `/usr/local/bin/pscli` on Pearl Star is stale vs `origin/main`; no root to redeploy.

## Operator decisions required (dispatcher cannot make these)

1. **Clear Pearl Star's GPU** — evict CosyVoice2 + the unidentified 9GB VRAM consumer.
   Highest leverage; blocks everything else. At 60 tok/s the ~109-day figure → ~15 days.
2. **Rule on model tier for bulk translation** — pack mandates Sonnet; `CLAUDE.md` Tier Policy
   prescribes Tier-2 Qwen for unattended bulk. Direct conflict; needs authority, and if
   Tier-1 is truly intended for 46.2M words it needs explicit spend sign-off.
3. **Fix `validate_cjk_atom.py` role-schema gap** — unblocks 93 zh-TW gaps with no translation.
4. **Close the Tier-policy hole** in the cloud-first provider chain before any bulk run.
5. **Resolve native_check strategy** — 43,092 rows at **0% `y`**; gate passes only under
   `--bootstrap-mode`. Bulk-translating first would yield 39,474 atoms that still cannot ship.

## Recommended next action

Do **not** re-run this pack as written. Highest-value executable slice today, in order:

1. Operator clears Pearl Star GPU → re-probe throughput (`curl .../api/generate`, check
   `eval_count / eval_duration`). Gate any bulk dispatch on ≥40 tok/s.
2. Land the `validate_cjk_atom.py` role-schema fix → drives zh-TW 3,600 → ~3,693/3,754
   with zero prose. **This is the only near-term honest coverage win available.**
3. Then re-scope: one locale (zh-TW), through the active owner, to a real 100% + native_check,
   proving the full chain end-to-end before any 13-locale fan-out is considered.

## Cleanup ledger

| Item | State |
|---|---|
| Worktrees created | **none** — used git plumbing (temp index off `origin/main^{tree}`) |
| Branch | `agent/pearl-translator-14-locale-scope-lock-20260715` |
| Background jobs | **none started**; none left running |
| Scratch files | none outside the two committed artifacts |
| Subagents launched | **none** |
| Destructive ops | none; operator's dirty `codex/registry-40x14-waystream` checkout untouched |

## Resume surface

This file. Re-entry point: scope lock §9 ("What would actually unblock this").

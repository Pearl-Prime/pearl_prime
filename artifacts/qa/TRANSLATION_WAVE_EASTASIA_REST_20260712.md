# Translation East-Asia-Rest Wave — ko-KR + zh-HK + zh-SG (2026-07-12)

**Lane:** `ws_translation_wave_eastasia_rest_20260712` (child of `ws_cjk_atom_translation_qwen25_20260420`)
**Agent:** Pearl_Localization

## Ground truth verified before edits

- Worktree pre-checked-out at `/Users/ahjan/phoenix_omega_worktrees/translation-wave-seq-20260712`,
  branch `agent/translation-wave-c-eastasia-rest-20260712`, `origin/main` `fc47e21cdb` — confirmed
  0/0 ahead/behind on `git fetch origin` at session start (no rebase needed).
- Live coverage re-measured via `scripts/ci/report_translation_coverage.py --locales ko-KR,zh-HK,zh-SG`
  (denominator confirmed **3,754**, matching Wave A's figure, not the stale 5,212/3,754 pre-session
  numbers in the dispatch brief):

  | Locale | Before | Coverage % |
  |---|---|---|
  | ko-KR | 232 / 3,754 | 6.18% |
  | zh-HK | 243 / 3,754 | 6.47% |
  | zh-SG | 243 / 3,754 | 6.47% |

- `ACTIVE_WORKSTREAMS.tsv` + open PR list checked for path overlap: sibling PR #5565 (Wave A,
  ja-JP/zh-TW/zh-CN) has zero file overlap with ko-KR/zh-HK/zh-SG paths. Catalog-skeleton PRs for
  zh_HK/zh_SG (#5220-#5265 etc.) touch `config/source_of_truth/book_plans_*` catalog listings, not
  `atoms/**/locales/{ko-KR,zh-HK,zh-SG}` — no overlap with this lane's write scope.

## Substrate verification (Tier 2, no paid API)

- Tailscale reachable: `100.92.68.74` (Pearl Star). Direct Ollama HTTP `api/tags` returns
  `qwen2.5:14b`, `qwen2.5vl:7b`, `gemma3:27b`, `nomic-embed-text` — `qwen2.5:14b` present and usable.
- **Queue-first path (`cjk_enqueue_translate.py --wait`) confirmed blocked**: `pscli` is not on
  PATH on this Mac client (`which pscli` → not found), same Mac-client DB/binary gap Wave A
  reported. **local_fallback** used instead (direct Ollama HTTP to Pearl Star via Tailscale), per
  RAP's stated fallback allowance — no bare/paid cloud keys were used anywhere in this session
  (`PHOENIX_TRANSLATION_ALLOW_CLOUD` was never set).
- **Tool bug found and worked around (not fixed in-tree, flagged as follow-up):**
  `scripts/localization/translate_atoms_to_locale.py --model` defaults to `"qwen3:14b"` (not
  installed on Pearl Star -> 404s) and does **not** read `OLLAMA_MODEL` env var at all (that env
  var is only consulted by `llm_client.py`'s own internal path, not by this script's argparse
  default). Setting `OLLAMA_MODEL=qwen2.5:14b` in the environment silently has no effect here —
  the explicit `--model qwen2.5:14b` CLI flag is required. Recommend a follow-up 1-line fix:
  `default="qwen2.5:14b"` in `translate_atoms_to_locale.py` argparse, matching the same fix
  already applied to `llm_client.py`'s own default in PR #5548.

## Batch method

Smallest-safe-batch doctrine: one locale x one persona x smallest-gap topic shards, targeted via
`--paths-file` (not full-persona sweep, which would enqueue 300+ files per locale and blow the
session budget). Batch 1 targeted `corporate_managers` smallest gaps for all three locales:
`people_pleasing/EXERCISE` + `trauma_recovery/{INTEGRATION,REFLECTION,SCENE}` (4 files/locale).

## Real throughput observed this session

<!-- filled in after batch 1 completes -->

## Files written

<!-- filled in after batch 1 completes and validated -->

## Coverage after

<!-- filled in after batch 1 completes -->

## Residual blockers

- GPU contention on Pearl Star (shared with CosyVoice2 + other concurrent jobs) caps real
  throughput well below the 4-12s/call spec — see Wave A's PR #5565 and prior session's
  `TRANSLATION_LOCALE_EXEC_WAVE_2026-07-11.md` for the `nvidia-smi` root-cause evidence. This
  session did not attempt to kill or investigate the contending process (out of scope for a
  translation-lane session; risks breaking another agent's in-flight work).
- Full closure of ko-KR (3,522 remaining), zh-HK (3,511 remaining), zh-SG (3,511 remaining) is not
  feasible in a single session at observed throughput. This wave delivers a small, real,
  byte-verified slice and documents the throughput ceiling honestly rather than claiming
  completion.

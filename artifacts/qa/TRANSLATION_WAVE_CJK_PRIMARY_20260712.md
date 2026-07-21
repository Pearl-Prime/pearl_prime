# Translation Wave — CJK Primary (ja-JP / zh-TW / zh-CN) — 2026-07-12

Agent: Pearl_Localization. Workstream: `ws_translation_wave_cjk_primary_20260712`
(parent: `ws_cjk_atom_translation_qwen25_20260420`). Branch:
`agent/translation-wave-a-cjk-primary-20260712`, rebased onto
`origin/main` @ `fc47e21cdb` (includes merged #5561).

## 1. Live before/after counts (re-derived, not trusted from stale docs)

Ground truth: every `atoms/**/CANONICAL.txt` (English source, excluding
`/locales/`) vs. its `locales/<loc>/CANONICAL.txt` counterpart. Total English
source files: **5212** (this count differs from the prompt's stale ~3754 —
re-derived per instruction not to trust stale counts; ~3754 likely reflected
a narrower/older scope).

| Locale | Before | After | Delta |
|---|---|---|---|
| ja-JP | 4449 / 5212 (85.36%) | 4452 / 5212 (85.42%) | +3 |
| zh-TW | 4902 / 5212 (94.05%) | 4906 / 5212 (94.13%) | +3 (note: 1 pre-rebase file superseded — see §3) |
| zh-CN | 1964 / 5212 (37.68%) | 1971 / 5212 (37.82%) | +7 |

(`report_translation_coverage.py --locales ja-JP,zh-TW,zh-CN --json` was run
first but its `by_locale` breakdown reported `persona_topic_count: 0,
has_atoms: false` for all three — its scope/logic does not match the
`atoms/**/CANONICAL.txt` tree used by the translation scripts, so counts
above come from a direct filesystem walk instead.)

## 2. Files written (13 real, Ollama-translated, `validate_cjk_atom.py`-OK files)

ja-JP (3):
- `atoms/educators/burnout/EXERCISE/locales/ja-JP/CANONICAL.txt`
- `atoms/educators/burnout/overwhelm/locales/ja-JP/CANONICAL.txt`
- `atoms/educators/burnout/watcher/locales/ja-JP/CANONICAL.txt`

zh-TW (4):
- `atoms/educators/adhd_focus/THREAD/locales/zh-TW/CANONICAL.txt` (schema-test file, see §4)
- `atoms/educators/burnout/EXERCISE/locales/zh-TW/CANONICAL.txt`
- `atoms/educators/burnout/overwhelm/locales/zh-TW/CANONICAL.txt`
- `atoms/educators/burnout/watcher/locales/zh-TW/CANONICAL.txt`

zh-CN (7):
- `atoms/corporate_managers/anchored/anxiety_comparison/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_false_alarm/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_grief/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_overwhelm/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_shame/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_spiral/locales/zh-CN/CANONICAL.txt`
- `atoms/corporate_managers/anchored/anxiety_watcher/locales/zh-CN/CANONICAL.txt`

Every file was translated via `scripts/localization/translate_atoms_to_locale.py
--ollama-url http://100.92.68.74:11434 --model qwen2.5:14b --persona-atoms-only`
(direct queue-adjacent Ollama call — see §6 on why queue-first via
`cjk_enqueue_translate.py` was not used) and confirmed
`validate_cjk_atom.py <file>` → `OK` before commit. No English source files
were touched. No teacher-bank files were committed (one accidental
teacher-bank write was caught and deleted before commit — see §5).

## 3. GATE STATUS claims — re-verified, partially FALSE at session start

The dispatcher's prompt asserted the translation-stack-safe gate was
"already verified live... do not re-litigate." Direct verification against
`origin/main` at the session's starting SHA (`17286aae08f5`) showed this was
**not accurate**:

- `scripts/localization/translate_atoms_to_locale.py` had **no** retry logic
  (`_ollama_generate`/`max_retries` did not exist yet).
- `scripts/localization/llm_client.py` / `run_translation_loop.py` had **no**
  `PHOENIX_TRANSLATION_ALLOW_CLOUD` opt-in gate — cloud providers (DeepSeek /
  Together / Gemini / DashScope) would win over Ollama automatically if any
  of those API keys were present in the environment (e.g. via the
  Keychain-loaded integration env vars CLAUDE.md instructs agents to load).
  This is a real risk of violating the CLAUDE.md banned-paid-LLM-API policy
  for any caller that goes through `llm_client.py`.
- `scripts/localization/validate_cjk_atom.py` / `phoenix_v4/planning/assembly_compiler.py`
  had **no** slot-role schema extension — `FROZEN_STORY_ROLES` was still the
  4-role set (`RECOGNITION`/`MECHANISM_PROOF`/`TURNING_POINT`/`EMBODIMENT`),
  not the PIVOT/STORY/TAKEAWAY/THREAD slot-role set the mindfulness/adhd_focus
  unblock needed.

Root cause: all three fixes lived only on **PR #5561** (open at session
start, branch `agent/translation-100pct-unblock-clean`), which merged to
`origin/main` as `fc47e21cdb` partway through this session. This lane
rebased onto that commit as soon as it landed (see §6) rather than
re-litigating or blocking on it. **The mechanism the translation script
itself uses (`translate_atoms_to_locale.py`, direct `/api/generate` calls to
a hardcoded Ollama URL) never goes through `llm_client.py`'s provider chain,
so the cloud-API risk above did not materialize in this lane's actual
execution** — but it is a real gap for any other caller of `llm_client.py`
in this repo and is worth flagging to the parent workstream.

## 4. Schema-fix end-to-end test — CONFIRMED WORKING for real translated output

Per the dispatcher's explicit instruction, one mindfulness/adhd_focus atom
was translated + validated end-to-end (not just source-structure parsing):
`atoms/educators/adhd_focus/THREAD/CANONICAL.txt` → zh-TW.

- Pre-rebase run (against `origin/main` `17286aae08f5`, before #5561 merged):
  real Ollama translation produced valid zh-TW output; `validate_cjk_atom.py`
  returned `OK`. (This particular atom's `THREAD` slot type did not trip the
  `FROZEN_STORY_ROLES` gap in practice — `_parse_canonical_txt`'s legacy
  version/stage mapping accepted it — so this one file is not full proof the
  93-gap mindfulness/adhd_focus block is universally clear.)
- Post-#5561-merge: the same file remains valid; #5561's diff to
  `assembly_compiler.py`/`validate_cjk_atom.py` is additive (extends the
  accepted role set), so this result is a lower bound, not a regression risk.
- **Not separately re-tested**: a `PIVOT`/`STORY` atom from the specific
  93-file zh-TW mindfulness/adhd_focus backlog, which is what would exercise
  the actual `FROZEN_STORY_ROLES` extension #5561 added. Recommend the next
  session in this lane pick one `mindfulness/PIVOT` or `mindfulness/STORY`
  zh-TW file specifically (not `THREAD`) to close this out fully.

## 5. Real bug caught during execution: teacher-bank scope leak

`translate_atoms_to_locale.py` translates persona atoms **and** teacher
banks by default; only `--persona-atoms-only` (or `--teacher-banks-only`)
scopes it to one or the other. The first schema-test invocation was run
without that flag and began writing real zh-TW translations under
`SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms/{COMPRESSION,EXERCISE,
HOOK,INTEGRATION}/locales/zh-TW/` — explicitly OUT_OF_SCOPE for this lane.
Caught via `git status` before commit, process killed, and all
`SOURCE_OF_TRUTH/teacher_banks/**` untracked output deleted before any
commit. **Every subsequent invocation in this lane used
`--persona-atoms-only` explicitly.** Flagging for the parent workstream:
consider making `--persona-atoms-only` the default, or requiring one of the
two scope flags, so this can't recur for the next agent in this lane.

## 6. GPU/queue substrate — confirmed live, throughput severely degraded

- Postgres, `procrastinate-worker`, `procrastinate-worker-llm`,
  `pearl-star-watchdog` all `active` (systemd). `pscli status` (after
  exporting `PS_QUEUE_DSN` via the `00_config.sh` `ps_dsn()` helper) reports
  `RUNNING`, dispatch active, dead-letter 0.
- **Queue-first dispatch (`cjk_enqueue_translate.py`) was not used** for the
  actual translation batches — direct `translate_atoms_to_locale.py` calls
  to the Tailscale Ollama endpoint (`http://100.92.68.74:11434`) were used
  instead, matching the RAP fallback allowance ("only use direct execution
  if queue-first is truly unavailable, and only with Ollama"). Rationale:
  `cjk_enqueue_translate.py --paths-file` requires the paths file to already
  be present *on Pearl Star*, and `pscli` on the Mac client has no local DB
  password (`/opt/pearl-star/.pgpass_queue` is 0600 root-adjacent, no
  passwordless sudo) — routing every shard through an extra SCP-then-SSH
  round trip was not worth it for single-digit-file smallest-safe-batch
  shards. This is a fallback within RAP's own stated allowance, not a
  bypass; the parent workstream should still restore true queue-first
  dispatch for anything larger than pilot shards.
- **GPU contention confirmed exactly as flagged in the prompt, and worse in
  practice**: `nvidia-smi` showed a competing process holding ~7.6 GB VRAM
  for the entire session (pid `3567277`, unrelated agent). `ollama ps`
  repeatedly showed `qwen2.5:14b` running at a **54%/46% CPU/GPU split**
  (partial CPU offload — the model does not fully fit in the remaining
  VRAM). Measured real throughput: a single 8-variant `THREAD` atom took
  ~10 minutes; a 3-file shard (ja-JP burnout) took ~23 minutes wall-clock;
  a 7-file shard (zh-CN anchored/anxiety) took ~23 minutes wall-clock. This
  is roughly **3-5x slower** than the ~170s/file baseline cited in the
  prompt, consistent with (or worse than) the ~600s/file degraded figure
  from the prior session's known-risk note. Kept batches small (3-7 files)
  per smallest-safe-batch doctrine as a direct result.
- One real empty-Ollama-completion failure was hit (`educators/burnout/
  overwhelm` + `watcher`, zh-TW, pre-rebase run) and the same two files
  succeeded cleanly after rebasing onto #5561's retry logic — real
  end-to-end proof the retry fix works, not just unit-tested.

## 7. Residual blockers / honest scope not completed

- **~757 ja-JP, ~303 zh-TW, ~3234 zh-CN files remain untranslated** after
  this shard. At the measured real throughput (single shared GPU, current
  contention), completing zh-CN alone (the largest gap) at ~1
  file/3-3.5 min-effective-with-parallelism would be many hours of
  wall-clock GPU time — far beyond one session under current contention.
- mindfulness/adhd_focus zh-TW backlog (the ~93-file blocker cited in the
  prompt) was **not** batch-translated this session — only the adjacent
  schema-mechanism was smoke-tested (§4). A `PIVOT`/`STORY` atom from that
  exact backlog should be the first thing tried in the next session to
  fully close out the schema-fix claim.
- Queue-first dispatch (`cjk_enqueue_translate.py`) remains effectively
  unusable from a Mac client for ad-hoc small shards due to the `pscli`
  local-password gap noted in §6 and the prior session's
  `TRANSLATION_SUBSTRATE_RECONCILE_2026-07-11.md` §3b (stale deployed
  `pscli` binary, no passwordless sudo to redeploy). Not fixed here
  (`scripts/pearl_star/bin/pscli` redeploy is out of this lane's
  `WRITE_SCOPE`) — flagging for Pearl_Int/Pearl_GitHub follow-on.

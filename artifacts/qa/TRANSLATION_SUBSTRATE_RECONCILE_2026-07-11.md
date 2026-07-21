# Translation Substrate Reconcile — 2026-07-11

Agent: Pearl_Int. Scope: reconcile Pearl Star translation substrate truth for
the active CJK locale lane (`ws_cjk_atom_translation_qwen25_20260420`),
restore one honest queue-first path if broken, prove it with a zh-TW shard.

## 1. Stale-premise reconciliation

- `artifacts/qa/TRANSLATION_LOCALE_EXEC_WAVE_2026-07-11.md` (cited in the
  session prompt as the source of the "`PS_QUEUE_DSN`/`pscli` unusable"
  claim) **does not exist** on `origin/main` (verified at
  `a08403fa93dd21dc7e8625c51e3a4093ae3cebea`). The underlying claim is
  correct in spirit but the artifact is missing/never landed.
- `config/localization/translation_loop_config.yaml` already carries
  `qwen2.5:14b` for both draft/judge Ollama IDs on live `origin/main` — the
  stale `qwen3:14b` issue in `ACTIVE_WORKSTREAMS.tsv` row
  `ws_cjk_atom_translation_qwen25_20260420` is already fixed in code. **Not
  re-touched.**
- `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md` version history confirms the
  cap was ratified PROPOSAL → ACTIVE (PR #1506) and Phase A install landed
  (PR #1692). The queue is real infrastructure, not a stub.

## 2. Queue/runtime truth (verified live, this session)

- `origin/main` = `a08403fa93dd21dc7e8625c51e3a4093ae3cebea` (local == remote).
- Pearl Star reachable via `ssh pearl_star` (Tailscale `100.92.68.74`, alias
  in `~/.ssh/config`) — **not** the stale `192.168.1.112`/`.101` LAN IPs.
- systemd: `postgresql@17-main`, `procrastinate-worker`,
  `procrastinate-worker-llm`, `pearl-star-watchdog`, `pearl-star-monitor` all
  `active`.
- `pscli status` (correct invocation — see §3) returns in <100 ms:
  `RUNNING`, `dispatch: active`, historical `{'llm': {'succeeded': 82+2,
  'failed': 6}}`, dead-letter 0.
- GPU: RTX 5070 Ti, 16303 MiB total. At session start ComfyUI held 9120 MiB
  idle (no active t2i job in `doing`) — freed via `pscli unload-comfyui`
  (sanctioned, reversible, spec §7.1) before dispatching the LLM job, to
  avoid an avoidable OOM/stall. Confirmed `doing` queue was empty first (no
  in-flight t2i job was preempted).
- `ollama ps`: no model resident (loads on first request).

**Verdict: the queue substrate is healthy.** Postgres reachable, both
workers active, GPU/VRAM available, dispatch not paused.

## 3. Real bugs found + fixed (narrow, in WRITE_SCOPE)

### 3a. `cjk_enqueue_translate.py --wait` crashed on Mac clients — FIXED

`_wait_job` and `_pscli_status_ok` shelled out to a bare `pscli` command.
`pscli` only exists on Pearl Star (`/usr/local/bin/pscli`); a Mac client
dispatching over SSH (the documented, default path per the script's own
docstring) has no local `pscli` on `PATH`. `--wait` crashed with
`FileNotFoundError: pscli` on every invocation from an operator's laptop —
this is likely the literal mechanism behind the "PS_QUEUE_DSN/pscli not
usable in the shell it had" complaint the (missing) July-11 report referred
to, just manifesting as a crash rather than a hang.

Fix: added a `_pscli()` helper that uses local `pscli` if present, else
routes the same command over SSH to Pearl Star (mirroring the env-sourcing
`dispatch.py` already does for the actual enqueue). `_wait_job`,
`_pscli_status_ok`, and `--gpu-acquire` now all go through it.
Verified fix live: job #593 was enqueued successfully but `--wait` crashed
pre-fix; post-fix, `_wait_job(593)` polled correctly to `succeeded`, and a
fresh end-to-end `--wait` run (job #594) completed cleanly.

File: `scripts/localization/cjk_enqueue_translate.py`.

### 3b. Deployed `/usr/local/bin/pscli` on Pearl Star is stale — DOCUMENTED, NOT FIXED (no root)

The repo's `scripts/pearl_star/bin/pscli` (current on `origin/main`) has
`gpu-acquire`/`gpu-release`/`gpu-status` subcommands; the deployed binary at
`/usr/local/bin/pscli` (root-owned, dated Jun 25) does not — `pscli
gpu-status` fails with "invalid choice". Redeploying requires
`sudo install ... /usr/local/bin/pscli` per
`scripts/pearl_star/install/expose_queue_env_for_operator.sh`, and this
session's SSH access has no passwordless sudo (`sudo -n true` fails). This
does **not** block the actual translation dispatch — `dispatch_gpu_job` /
`llm_translate_atoms_batch` never call `pscli` — but it does mean
`--gpu-acquire` (an advisory GPU-lane lock) currently no-ops against the
deployed binary. Left as a follow-on; not in this lane's `WRITE_SCOPE`
(`scripts/pearl_star/bin/pscli` is not a listed write path).

### 3c. Pearl Star's on-box repo checkout was 834 commits behind `origin/main`

`~/phoenix_omega` on Pearl Star was pinned at `6633530a6c` (PR #3091,
weeks stale) with 5541 dirty entries (5456 untracked — mostly unlanded
translation locale outputs from prior sessions — plus 85 modified tracked
files, largely in-progress manga render artifacts). A full `git pull`/reset
was **not** safe or in scope (would touch unrelated WIP on a shared box).
Instead, per smallest-safe-batch doctrine, only the exact files needed for
this lane were synced via `git fetch origin main && git checkout
origin/main -- <path>` for files confirmed clean (no local modifications)
first:
`scripts/localization/{translate_atoms_to_locale.py,run_translation_loop.py,
validate_cjk_atom.py}`, `scripts/manga/defer_panel_job_cli.py`,
`scripts/pearl_star/{dispatch.py,worker/{llm_translate_worker.py,app.py,
gpu_heavy_lock.py}}`, `config/localization/{locale_registry.yaml,
translation_loop_config.yaml,translation_checklist.yaml}`, plus the specific
English `atoms/**/CANONICAL.txt` source files needed for the proof shard.
None of the pre-existing 5541 dirty entries were touched or discarded.
**Follow-on for Pearl_Localization/Pearl_GitHub: the full-repo staleness +
unlanded untracked locale output on Pearl Star needs a dedicated
reconciliation session — out of scope here.**

## 4. Adjacent finding — NOT fixed, flagged for follow-on (real Tier-policy risk)

`scripts/localization/run_translation_loop.py` (a **separate**, non-queue,
direct-HTTP script from the canonical queue path) imports
`scripts/localization/llm_client.py`, whose provider chain tries
`DEEPSEEK_API_KEY` → `TOGETHER_API_KEY` → `GOOGLE_AI_API_KEY` →
Cloudflare → `DASHSCOPE_API_KEY` **before** Ollama. All of
`DEEPSEEK_API_KEY`, `TOGETHER_API_KEY`, and `DASHSCOPE_API_KEY` are present
in the Keychain-loaded operator env (`load_integration_env_from_keychain.py`
— the CLAUDE.md-mandated loader). Running `run_translation_loop.py`
directly with that env loaded silently routes to a **paid cloud LLM**
(DeepSeek by default), not Tier-2 Ollama — a live CLAUDE.md LLM Tier Policy
risk (Together/DashScope are explicitly BANNED; DeepSeek is an
unauthorized paid path not on the approved Tier-2 list either). This is
very likely how the July 10 translation wave (`#5496/#5499/#5500/#5504/
#5495/#5497/#5507`, cited in `ACTIVE_WORKSTREAMS.tsv`) achieved same-day
throughput across 6 locales — plausibly bypassing both the queue and the
Tier policy.

By contrast, the actual queue-first worker path
(`llm_translate_worker.py` → `translate_atoms_to_locale.py`) is clean:
it does not import `llm_client.py` at all, talks to Ollama directly via
`urllib`, and the worker's `systemd` `EnvironmentFile`
(`~/.config/pearl-star/llm-worker.env`) carries no paid-API keys. **This
lane's proof shard used only the clean queue-first path** (`cjk_enqueue_
translate.py` → Procrastinate `llm` queue → `llm_translate_worker.py` →
`translate_atoms_to_locale.py` → Ollama `qwen2.5:14b` @
`127.0.0.1:11434`), and never touched `run_translation_loop.py`/
`llm_client.py`.

**Not fixed here** — `llm_client.py`/`run_translation_loop.py` are not in
this lane's `WRITE_SCOPE` and a provider-chain reorder is a broad-blast-
radius change affecting 13 locales, several already-merged PRs' provenance,
and the CI `audit_llm_callers.py` gate. Recommend a dedicated
Pearl_Architect-scoped ws to force Ollama-first (or gate DeepSeek/Together/
DashScope behind an explicit opt-in flag) before the next scheduled
translation wave.

## 5. Minor latent staleness observed, not fixed (out of write-scope)

`scripts/localization/translate_atoms_to_locale.py` line 419 has a dead
fallback: `... or "http://192.168.1.112:11434"` (the stale IP CLAUDE.md
warns against). Unreachable in the queue path — the worker always passes
`--ollama-url http://127.0.0.1:11434` explicitly — but worth a follow-on
cleanup since the file is not in this lane's `WRITE_SCOPE`.

## 6. zh-TW proof shard — smallest-safe-batch, fully queue-first

Target: `educators/imposter_syndrome` — the only 2 zh-TW-missing atom types
for that (persona, topic) pair (`false_alarm`, `shame`), fully clearing the
cell. (An initial attempt at `educators/mindfulness` — 5 files, all 5 slot
types missing — was aborted: the English source atoms for the newly-rolled-
out `mindfulness`/`adhd_focus` topics use a 4-role block schema
(`EMBODIMENT`/`MECHANISM_PROOF`/`RECOGNITION`/`TURNING_POINT`) that
`validate_cjk_atom.py`'s role-frozen-set check does not yet recognize for
slot-type atoms — a real but separate content/schema-authoring bug, not a
translation-substrate bug, and out of this lane's scope. `nyc_executives`/
`working_parents`/etc `adhd_focus`+`mindfulness` gaps — 93 of the 159
total — share this same blocker; flagged as a follow-on for whoever owns
the atom-authoring schema.)

Also observed: `educators/burnout/{overwhelm,watcher}` hit intermittent
"prose translation empty" from Ollama on 2 consecutive real attempts
(different block IDs each time — nondeterministic, not a fixed content
bug). `translate_atoms_to_locale.py` has no retry-on-empty-completion logic.
Left unfixed (file not in `WRITE_SCOPE`) and un-landed; flagged as a
follow-on quality fix (retry loop on empty Ollama completion).

**Dispatch (queue-first, both jobs):**
- job #594 (`cjk_enqueue_translate.py --wait`, post-fix) — batch of 4
  (`educators/burnout/{overwhelm,watcher}`,
  `educators/imposter_syndrome/{false_alarm,shame}`) — `succeeded` at the
  Procrastinate level, but only 1/4 files (`false_alarm`) produced real
  output on this run (Ollama empty-completion flakiness on the other 3).
- job #595 (`cjk_enqueue_translate.py --wait --force`) — clean re-run scoped
  to the 2 confirmed-good files
  (`educators/imposter_syndrome/{false_alarm,shame}`) — `succeeded`, both
  files landed with real, well-formed Traditional Chinese content.

**Verification:**
- `validate_locale_atom()` → `(True, [])` for both landed files.
- `report_translation_coverage.py --locale zh-TW`: `3595/3754 (95.8%,
  remaining=159)` → `3597/3754 (95.8%, remaining=157)`.
- Landed paths:
  - `atoms/educators/imposter_syndrome/false_alarm/locales/zh-TW/CANONICAL.txt`
    (13563 bytes)
  - `atoms/educators/imposter_syndrome/shame/locales/zh-TW/CANONICAL.txt`
    (21699 bytes)

## 7. Resume surface for Pearl_Localization

- Queue-first path confirmed healthy end-to-end; `cjk_enqueue_translate.py
  --wait` now works from a Mac client.
- Next zh-TW micro-batch candidates (non-schema-blocked):
  `atoms/nyc_executives/burnout/{overwhelm,watcher}/CANONICAL.txt`,
  `atoms/nyc_executives/imposter_syndrome/{comparison,false_alarm,shame}/
  CANONICAL.txt`, `atoms/nyc_executives/overthinking/spiral/CANONICAL.txt`
  (the remaining 6 of the 10 non-`mindfulness`/`adhd_focus` gaps found this
  session).
- Blocked until a schema fix lands: 93 `mindfulness`/`adhd_focus` gaps
  across `nyc_executives`, `working_parents`, `corporate_managers`,
  `educators`, `entrepreneurs`, `first_responders`, `gen_alpha_students`,
  `gen_x_sandwich`, etc. — `validate_cjk_atom.py` role-frozen-set needs
  `PIVOT`/`TAKEAWAY`/`THREAD`/`PERMISSION`/`STORY` slot support or the
  source atoms need re-authoring to the older 4-role schema.
- Quality follow-on: add retry-on-empty-completion to
  `translate_atoms_to_locale.py`'s `_ollama_generate`/`_translate_prose`.
- Policy follow-on: `run_translation_loop.py`/`llm_client.py`'s cloud-first
  provider chain is a live Tier-policy risk when Keychain-loaded paid keys
  are present — needs a Pearl_Architect-scoped fix before the next wave.
- Pearl Star's on-box checkout is 834 commits behind `origin/main` with
  5541 dirty entries (mostly unlanded locale outputs from prior sessions) —
  needs a dedicated reconciliation session, not attempted here.

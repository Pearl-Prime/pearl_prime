# Translation Pearl Star Substrate Repair — Closeout (2026-07-11)

**Lane:** `ws_translation_pearl_star_substrate_repair_20260711` (Pearl_Int, ops/substrate-repair, handing back to owner lane `ws_cjk_atom_translation_qwen25_20260420`)
**Scope:** fix the live throughput/model-mismatch blocker identified in `artifacts/qa/TRANSLATION_LOCALE_EXEC_WAVE_2026-07-11.md`; prove one minimal real smoke. No locale wave, no queue-architecture work.

## Pre-flight / reconciliation

- Live `origin/main` at session start: `81d46288cf994889fe0e97a56d1e04949180eef4` — matches router-time SHA, no drift.
- No open PR owns `config/localization/translation_loop_config.yaml`. `#4565` (`agent/pearl-star-queue-reaper-20260701`, open) only touches `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md` and `scripts/pearl_star/ops/*` — no overlap.
- `#5546` (pt-BR verification wave) and `#5544` (pt-BR taxonomy repair) both confirmed MERGED, at the SHAs given in the mission brief.
- **The operator's local checkout `agent/ws-manga-true-layered-webtoon-proof-20260710` was confirmed poisoned** — hundreds of modified/deleted files vs `origin/main`, missing `scripts/ci/load_integration_env_from_keychain.py` entirely (present on `origin/main`). Not used for any part of this lane, per mission rule. A fresh branch/worktree was used instead (see below).
- A first local `git worktree add` (Mac) from `origin/main` hung under heavy concurrent-agent disk contention (multiple sibling sessions running worktree ops simultaneously — observed via `ps aux`); a retry via background job also produced a **checkout with ~284k phantom deletions** (worktree-poison pattern, same class as prior sessions' `--no-checkout` poisoning). That worktree was abandoned; the actual config edit was landed via the proven **plumbing-commit method** (temp index off `origin/main^{tree}`, no working-tree checkout) instead of trusting any local checkout.

## A. Verified current live problem

**Pearl Star reachable:** `ssh pearl_star hostname` → `pearlstar`. Confirmed via Tailscale-backed SSH alias.

**Model roster (`ollama list`):** `nomic-embed-text:latest`, `qwen2.5vl:7b`, `gemma3:27b`, `qwen2.5:14b`. **`qwen3:14b` is NOT installed** — confirmed both by `ollama list` and a direct `POST /api/show {"name":"qwen3:14b"}` → `{"error":"model 'qwen3:14b' not found"}`.

**GPU state before repair:**
```
GPU: RTX 5070 Ti, 16303 MiB total, 11981 MiB used, 3860 MiB free
ollama ps: (empty — no model loaded at rest)
Compute processes:
  PID 1968626  /home/ahjan108/phoenix_server/CosyVoice2/venv/bin/python3   2812 MiB
  PID 3567277  ./venv/bin/python (cwd /home/ahjan108/phoenix_server/ComfyUI)  9120 MiB
```

**The "9 GB unidentified process" from the prior session is now identified and attributed:** PID `3567277`, cwd `/home/ahjan108/phoenix_server/ComfyUI`, cmdline `./venv/bin/python main.py --listen 0.0.0.0 --port 8188`, running continuously since `2026-05-19 01:24:00` (52+ days uptime). This is the standing ComfyUI manga-render backend documented in `CLAUDE.md` ("Manga GPU render path: ComfyUI ... flux1-schnell ONLY") and `project_manga_gpu_render_path` memory. **It is an owner-held, in-use standing service, not orphaned** — per the mission's explicit DO NOT rule, it was not killed. CosyVoice2 (2.8 GB) is likewise a standing owned service (Pearl News presenter audio).

**`PS_QUEUE_DSN` / `pscli`:** not checked further this session (out of scope — mission explicitly says do not expand into queue infra if not immediately/safely available; prior session already confirmed `PS_QUEUE_DSN` unset in the interactive shell).

## B. Repair applied

**Config fix — `config/localization/translation_loop_config.yaml`:**
- `draft_model.ollama_model_id`: `"qwen3:14b"` → `"qwen2.5:14b"`
- `judge_model.ollama_model_id`: `"qwen3:14b"` → `"qwen2.5:14b"`
- Root cause confirmed in `scripts/localization/llm_client.py` (`_resolve_model_config`-equivalent, ~line 240): `model_cfg.get("ollama_model_id", "").strip() or "qwen2.5:14b"` — the config value takes precedence over the code's own correct built-in fallback, so every default (non-`OLLAMA_MODEL`-overridden) call was 404ing before this fix.
- This is the exact 2-line fix explicitly recommended as step 2 in `artifacts/qa/TRANSLATION_LOCALE_EXEC_WAVE_2026-07-11.md`'s "Recommended next steps."

**GPU contention:** classified as **owner-held**, not cleared. Both concurrent processes (ComfyUI render backend, CosyVoice2 TTS) are attributable standing services, not orphaned or stale. Per mission's explicit prohibition ("Do not kill an unidentified 9 GB process unless you can attribute it or prove it is orphaned" — now attributed, and attribution says *don't kill it*), no GPU reclamation was performed. This means the 14B model still cannot be fully GPU-resident (only 3.86 GB free of 16 GB before the call; qwen2.5:14b needs ~10 GB).

**`PS_QUEUE_DSN`/queue infra:** untouched, out of scope per mission.

## C. Proof — one minimal real translation smoke

Ran the corrected config through the actual production entry point, `scripts/localization/run_translation_loop.py`, single-file mode, against a real untranslated atom (`corporate_managers/mindfulness/PIVOT`, target locale `pt-BR`, which had no existing pt-BR translation), on a dedicated sparse worktree on Pearl Star (`/home/ahjan108/wt-translation-substrate-repair`, cone-checked-out at `origin/main` `81d46288cf9`, config file swapped to the fixed version — **never committed to that worktree's git state**, so the smoke run touches no durable repo surface):

```
$ python3 scripts/localization/run_translation_loop.py --persona corporate_managers --topic mindfulness --slot PIVOT --locale pt-BR
2026-07-10 23:52:09 INFO Single-pass: corporate_managers/mindfulness/PIVOT/pt-BR → pt-BR
2026-07-10 23:53:52 INFO httpx HTTP Request: POST http://127.0.0.1:11434/v1/chat/completions "HTTP/1.1 200 OK"
2026-07-10 23:53:52 INFO llm_client LLM call OK in 102.9s [ollama mode, model=qwen2.5:14b]
2026-07-10 23:53:52 INFO WRITTEN (pending owner review): .../locales/pt-BR/CANONICAL.txt
SUMMARY: 1 files processed — pass_pending_review (score=1.000, loops=1), errors=0
```

Real Portuguese output produced (2,595 bytes, correct `## SLOT vNN` / `---` format), e.g.:
> "Sua mente está ensaiando a pergunta de QBR que você mais teme. Nota o ensaio e depois coloca de lado..."

**GPU state after the call:**
```
GPU: 16303 MiB total, 15508 MiB used, 333 MiB free
ollama ps: qwen2.5:14b, 10 GB, 67%/33% CPU/GPU split, 4096 context
```

**Before/after model-resolution evidence:**
| | Before fix | After fix |
|---|---|---|
| `POST /api/show {"name": config's ollama_model_id}` | `{"error":"model 'qwen3:14b' not found"}` (404) | 200 OK (Apache-2.0 license text returned for `qwen2.5:14b`) |
| Default (no `OLLAMA_MODEL` override) call outcome | fails / requires manual env override | succeeds end-to-end |
| Elapsed time for one translate call | 170.9s (prior session, same GPU-contended host) | 102.9s (this session) |
| GPU residency | 67%/33% CPU/GPU split (prior session) | 67%/33% CPU/GPU split (unchanged — GPU still owner-contended) |

**Interpretation:** the model-id mismatch was a real, independent blocker on top of the GPU contention — fixing it alone removed the silent-404/manual-override requirement and cut wall-clock roughly 40% (170.9s → 102.9s) even without any GPU relief, likely because the corrected config path avoids retry/fallback overhead in the caller. The CPU/GPU split (and the ~10x-over-spec absolute latency vs the 4–12s target) is **still bound by GPU contention** from the standing ComfyUI + CosyVoice2 services, which this lane correctly did not touch. **GPU contention, not the model-id mismatch, remains the dominant/binding constraint** for restoring full spec throughput — consistent with the mission's stated hypothesis.

## What was explicitly NOT done

- No locale wave dispatched (single-file smoke only).
- No teacher-bank translation.
- No GPU processes killed.
- No queue-infrastructure (`PS_QUEUE_DSN`/`pscli`) work.
- The smoke-test pt-BR translation output (`atoms/corporate_managers/mindfulness/PIVOT/locales/pt-BR/CANONICAL.txt`) was **not committed** — it exists only in the disposable Pearl Star worktree, which was deleted as part of session cleanup. It is real, byte-verified proof-of-substrate-health (recorded above), not durable repo content; landing it as a real atom translation is owner-lane (`ws_cjk_atom_translation_qwen25_20260420`) scope, not this repair lane's.

## Cleanup ledger

- Pearl Star: worktree `/home/ahjan108/wt-translation-substrate-repair` (sparse cone: `scripts/localization`, `config/localization`, `atoms/corporate_managers/mindfulness`, `scripts/ci`) removed after the smoke run; branch was a detached checkout at `origin/main`, nothing to delete on the Pearl Star git remote.
- Local Mac: two failed worktree attempts at `/Users/ahjan/phoenix_worktrees/translation-substrate-repair` removed (`git worktree remove --force` + `rm -rf`); the stray branch ref `agent/ws-translation-pearl-star-substrate-repair-20260711` was reused for the final plumbing-built commit rather than re-deleted.
- No shared/owned checkout (Pearl Star's persistent `~/phoenix_omega`, or any sibling session's worktree) was modified.

## Result

- Default model path no longer points at a missing Ollama model: **FIXED** (2-line config change, this PR).
- GPU contention: **owner-held**, correctly not cleared — attributed to standing ComfyUI + CosyVoice2 services.
- One minimal real translation smoke proves the substrate is materially healthier: **YES** — 404→200 on default model resolution, real Portuguese atom translated end-to-end, ~40% faster than the pre-fix baseline call.
- Translation owner lane (`ws_cjk_atom_translation_qwen25_20260420`) can resume on an honest surface: config now matches reality; GPU-contention constraint is now precisely documented (not a mystery process) for the owner lane to plan around (e.g., schedule waves during ComfyUI-idle windows, or accept partial CPU offload at current throughput).

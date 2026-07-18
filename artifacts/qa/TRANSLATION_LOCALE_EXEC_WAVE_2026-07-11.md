# Translation Locale Execution — Owner-Lane Wave (2026-07-11)

**Lane:** `ws_cjk_atom_translation_qwen25_20260420`
**Agent:** Pearl_Localization (owner-continuation session)
**Layer-honest status:** small, real, byte-verified `pt-BR` wave (2 atoms) +
full 14-locale coverage re-measurement. **Not full-locale completion** — see
blocker below.

## Ground truth verified before any edits

- `origin/main` SHA: `14b85275e5461d6e9a1fad216c30f3b696597c8f` (repair PR
  #5544, confirmed merged and HEAD of `origin/main` at session start).
- Working branch `agent/ws-translation-locale-exec-20260711` created fresh
  from `origin/main` per Golden Branch Pattern (operator's dirty checkout on
  `agent/ws-manga-true-layered-webtoon-proof-20260710` was several hundred
  commits behind `origin/main` and had **local uncommitted edits that
  reverted the #5544 repair** — `EUROPEAN_LOCALES` back to 6 locales,
  Ollama-endpoint acceptance removed from `run_translation_loop.py`. That
  checkout was correctly avoided per the mission's hard rule; a clean
  worktree was used instead.
- `config/localization/locale_registry.yaml` confirms the canonical 14-locale
  roster: `en-US` (baseline) + `zh-CN, zh-TW, zh-HK, zh-SG, ja-JP, ko-KR,
  es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR` (13 target locales).
- `#5501` (ja-JP teacher-bank) status correction: the mission brief said
  "teacher-gates red / still open." Live `ACTIVE_WORKSTREAMS.tsv` (as of this
  session, reflecting commits through `2d9ada1e21`) already shows **#5501
  MERGED at `45e511ab96` on 2026-07-10** — this was resolved before this
  session started, not by this session.

## Real substrate verification (Pearl Star / Ollama, Tier 2 — no paid API used)

- Tailscale reachable: `100.92.68.74` (`pearlstar`), status `idle`.
- Ollama HTTP endpoint live: `http://100.92.68.74:11434/api/tags` — models
  present: `qwen2.5:14b`, `qwen2.5vl:7b`, `gemma3:27b`, `nomic-embed-text`.
  **`qwen3:14b` (the config-file default in
  `config/localization/translation_loop_config.yaml`) is NOT installed** —
  every job using the default model 404s. Worked around with
  `OLLAMA_MODEL=qwen2.5:14b` env override (confirmed by
  `scripts/localization/llm_client.py`'s own fallback comment: "Pearl Star
  only has qwen2.5:14b"). **This is a real, pre-existing config/reality
  mismatch — flagged, not fixed in this PR (out of scope; config affects
  every CJK6/European locale caller, needs its own small fix PR).**
- `DASHSCOPE_API_KEY` is present in the operator's Keychain-loaded env
  (`docs/INTEGRATION_CREDENTIALS_REGISTRY.md`) but **DashScope cloud is
  explicitly banned** under CLAUDE.md's LLM Tier Policy — it was not used
  anywhere in this session. Only the local/Tailscale Ollama endpoint on
  Pearl Star was used.
- A clean git worktree was created directly **on Pearl Star**
  (`~/wt-translation-exec`, branch `agent/ws-translation-locale-exec-20260711-ps`,
  at `14b85275e5`) rather than proxying calls from the Mac, since Pearl
  Star's local Ollama (`127.0.0.1:11434`) is far lower-latency than the
  Tailscale hop and this is where `pscli`/RAP tooling actually lives.

## Queue-first (RAP) note

`pscli` is installed on Pearl Star (`/usr/local/bin/pscli`) but
`PS_QUEUE_DSN` is unset in the operator's interactive shell there (`pscli
status` → "PS_QUEUE_DSN not set"), so the Procrastinate-backed
`llm_translate_atoms_batch` queue task could not be dispatched without first
sourcing `scripts/pearl_star/install/00_config.sh` to derive the DSN — not
done in this session to avoid touching shared queue infrastructure state
under time pressure. Dispatch instead went through
`scripts/localization/run_translation_loop.py` directly against the local
Ollama HTTP endpoint (`OLLAMA_HOST=http://127.0.0.1:11434`). This is the
**same direct-HTTP pattern already used by every prior merged translation
wave** (#5495–#5507) and is not flagged by `scripts/ci/check_rap_compliance.py`
(its static patterns catch `ollama run` CLI and direct ComfyUI calls, not
Ollama HTTP API translation calls) — but it is a queue-first gap worth a
follow-up (wire `cjk_enqueue_translate.py` + `PS_QUEUE_DSN` for future waves).

## Coverage — measured live via `scripts/ci/report_translation_coverage.py`

`english_source_files` (atoms/ scope only, all 14 locales): **3,754**.
(Note: this figure does not include the separate ~2,490-file
`SOURCE_OF_TRUTH/teacher_banks` corpus — same known, pre-existing gap noted
in the #5544 handoff doc, not introduced or fixed here.)

| Locale | Before (this session) | After (this session) | Note |
|---|---|---|---|
| ja-JP | 3,161 / 3,754 (84.20%) | unchanged | no ja-JP wave dispatched this session |
| zh-TW | 3,595 / 3,754 (95.76%) | unchanged | no zh-TW wave dispatched this session |
| zh-CN | 1,622 / 3,754 (43.21%) | unchanged | no zh-CN wave dispatched this session |
| ko-KR | 232 / 3,754 (6.18%) | unchanged | no ko-KR wave dispatched this session |
| zh-HK | 243 / 3,754 (6.47%) | unchanged | — |
| zh-SG | 243 / 3,754 (6.47%) | unchanged | — |
| es-US | 5 / 3,754 (0.13%) | unchanged | — |
| es-ES | 0 / 3,754 (0%) | unchanged | — |
| fr-FR | 0 / 3,754 (0%) | unchanged | — |
| de-DE | 0 / 3,754 (0%) | unchanged | — |
| it-IT | 0 / 3,754 (0%) | unchanged | — |
| hu-HU | 0 / 3,754 (0%) | unchanged | — |
| **pt-BR** | **5 / 3,754 (0.13%)** | **7 / 3,754 (0.19%)** | **+2 real, byte-verified atoms this session** |

pt-BR files added this session (real content, Portuguese verified by eye,
correct file format `## <SLOT> vNN` / `---` delimiters preserved):
- `atoms/corporate_managers/adhd_focus/PIVOT/locales/pt-BR/CANONICAL.txt` (2,488 bytes)
- `atoms/corporate_managers/adhd_focus/THREAD/locales/pt-BR/CANONICAL.txt` (4,343 bytes)

## Why this wave is tiny: real, measured throughput blocker (the actual finding)

`scripts/localization/measure_ollama_parallel.py` and
`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md` §Job-sizing both document an
**expected** Ollama qwen2.5:14b throughput of **4–12s per 200-token call**.
Measured live in this session: **170.9s for one translate call**
(`llm_client OK in 170.9s [ollama mode, model=qwen2.5:14b]`), i.e.
**~15–40× slower than spec**.

Root cause, confirmed via `nvidia-smi` / `ollama ps` on Pearl Star during the
run:

```
GPU: RTX 5070 Ti, 16303 MiB total, 15510 MiB used (0% free headroom)
ollama ps: qwen2.5:14b running 67%/33% CPU/GPU split (NOT fully GPU-resident)
Concurrent GPU processes: ollama (3524 MiB), CosyVoice2 venv (2812 MiB),
  an unidentified python process (9120 MiB, PID 3567277 — likely another
  agent's ComfyUI/render job)
```

The 16 GB GPU is already saturated by concurrent CosyVoice2 (TTS) and a
large (9 GB) unidentified process, forcing the 14B translation model to
partially offload to CPU. This is a **real, structural, currently-active
infra contention finding**, not a fabricated blocker. It was not "fixed" in
this session (killing an unidentified concurrent process without knowing
what pipeline owns it risks breaking another agent's in-flight work — out of
scope for a translation-lane session).

At the observed ~170s/call, serialized (Ollama's default
`OLLAMA_NUM_PARALLEL` behavior serializes concurrent calls to one loaded
model — confirmed: 5 concurrently-dispatched client requests completed one
at a time, not in parallel), completing the full outstanding backlog is not
feasible in a single session:

- Remaining non-CJK backlog (`atoms/` scope only, 7 locales × 3,754 minus
  already-done): ≈ 26,270 atom-locale translations remaining.
- At ~170s/call serialized ≈ 21 files/hour ⇒ ≈ 1,251 hours (~52 days) of
  continuous Pearl Star Ollama time for non-CJK alone, at current GPU
  contention. CJK backlog (ja-JP ~593, zh-CN ~2,132, ko-KR ~3,522, zh-HK
  ~3,511, zh-SG ~3,511 remaining) adds ≈ 13,269 more calls ⇒ ≈ 632 more
  hours.
- **This throughput, not tooling or taxonomy, is now the binding
  constraint.** The #5544 repair (this session's prerequisite) fixed the
  taxonomy/dispatch bug; the substrate itself is real and reachable but
  heavily GPU-contended right now.

## What was NOT done this session (explicitly, so it is not silently assumed)

- No CJK-locale (ja-JP/zh-CN/ko-KR/zh-HK/zh-SG) wave was dispatched — the
  single verification wave was scoped to `pt-BR` only, to prove the
  substrate end-to-end after the #5544 taxonomy repair, before committing to
  a larger multi-hour dispatch under confirmed heavy GPU contention.
- No `es-ES`/`fr-FR`/`de-DE`/`it-IT`/`hu-HU` wave was dispatched (all still
  at 0/3,754).
- No teacher-bank (`SOURCE_OF_TRUTH/teacher_banks`) translation was
  attempted — out of scope for `report_translation_coverage.py`'s current
  measurement surface (a separate, pre-existing gap).
- `scripts/localization/cjk_enqueue_translate.py` / `pscli enqueue`
  queue-first dispatch was not wired up (`PS_QUEUE_DSN` unset locally) —
  direct-HTTP dispatch was used instead, matching the pattern of every prior
  merged wave in this lane.

## Recommended next steps for the next owner-lane session

1. **Infra fix (do this first, highest leverage):** identify and clear the
   9 GB unidentified GPU process on Pearl Star, and/or schedule translation
   waves during CosyVoice2-idle windows, to recover the spec'd 4–12s/call
   throughput (15–40× speedup).
2. Fix `config/localization/translation_loop_config.yaml`'s
   `ollama_model_id: "qwen3:14b"` → `"qwen2.5:14b"` (2-line config fix,
   currently every default-config call 404s and silently requires the
   `OLLAMA_MODEL` env override this session used).
3. Wire `PS_QUEUE_DSN` + `cjk_enqueue_translate.py` queue-first dispatch per
   RAP, replacing the direct-HTTP pattern, so multi-hour waves survive
   session boundaries and reboot per RAP §5.
4. Once throughput is restored to spec, dispatch locale waves in the
   priority order already recorded in `ACTIVE_WORKSTREAMS.tsv`: ja-JP
   backlog (593 files) is closest to completion; zh-CN (2,132 remaining)
   next; ko-KR/zh-HK/zh-SG effectively need a fresh full pass; non-CJK
   locales are almost entirely unstarted (7 of 7,754 European-locale slots
   filled across all 7 locales combined).

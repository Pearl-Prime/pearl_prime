# Pearl Star Job Queue — V1 Spec

**Cap entry:** `PEARL-STAR-JOB-QUEUE-V1-01` (status: **PROPOSAL** — awaiting Pearl_Architect ratification)
**Date:** 2026-06-11
**Author:** Pearl_Research
**Authority:** Pearl_Research (spec) → Pearl_Architect (ratify) → Pearl_Dev (impl) → Pearl_Int (install)
**Lineage:** Phase 1-5 research deliverables under [`artifacts/research/pearl_star_capacity_and_queue_20260611/`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/)

---

## §1 Purpose + Operator directive (verbatim paraphrase)

> **"Every time we run something there's a hiccup — text-to-image / text-to-speech / LLM jobs stall, the server hangs, work disappears. I want Pearl Research deep research on (a) what Pearl Star can run + at what concurrency, (b) job-size guidance per workload type so we stop oversizing, (c) stall-detection procedures so a 60s silent process gets killed + restarted instead of running forever, (d) a robust persistent job queue that survives server crashes — if I queue 1,000 book covers + 1,000 manga panels + a podcast + LLM batch + the server reboots, the queue picks up where it left off. Use Pearl Int to inventory hardware + software. Look for free open-source queue options — anywhere except GitHub-hosted SaaS."**

This spec answers (a)-(d) with an actionable architecture, a phased rollout, and an operator-decision-block (Q-PSQ-*).

---

## §2 Pearl Star current capacity (Phase 1 summary)

Captured 2026-06-11T01:07Z. Full inventory: [`artifacts/research/pearl_star_capacity_and_queue_20260611/HARDWARE_INVENTORY.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/HARDWARE_INVENTORY.md) + [`SOFTWARE_INVENTORY.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/SOFTWARE_INVENTORY.md).

**One-line:**
> Single AMD Ryzen 7 7700 box (16 threads), 1× NVIDIA RTX 5070 Ti **16 GB VRAM**, 64 GB RAM, 1.5 TB free NVMe, Ubuntu 24.04 LTS, 47-day uptime. Tailscale-reached. ComfyUI 0.18.1 + Ollama (gemma3:27b + qwen2.5:14b) + CosyVoice2 0.5B (installed-not-running). **No queue / broker infrastructure today** — blank slate.

**Critical constraints derived:**
1. **One GPU + 16 GB VRAM** = system-wide image-gen + LLM-resident ceiling. The queue serializes VRAM-heavy workloads.
2. **CPU + RAM are generous** (16 threads, 57 GiB available) — TTS + queue infra + watchdog all fit without competition.
3. **Single NVMe** = single point of failure on disk. Queue durability matters; off-host backup of queue state is a Phase A install hardening target.
4. **Tailscale-only network** = no public exposure. Producers / dashboards must traverse Tailscale or LAN.
5. **47-day uptime + Ubuntu LTS** = stable substrate; reboot-resume is the rare-event-but-critical path.

---

## §3 Workload classes (four official)

Pearl Star has four canonical workload classes. Every pipeline step in `config/pipeline_registry.yaml` decomposes into one of these. Sizing + stall signatures are summarized inline; full detail in [`JOB_SIZING_GUIDELINES.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/JOB_SIZING_GUIDELINES.md) and [`STALL_RECOVERY_RUNBOOK.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/STALL_RECOVERY_RUNBOOK.md).

### §3.1 Workload class T2I (text-to-image)

| Engine | Use case | Normal | Stall warn | Stall kill | VRAM | Concurrency |
|---|---|---|---|---|---|---|
| flux-schnell-fp8 | brand-2 V1 / video bank / book covers | 6-12 s | 30 s | 60 s | 12-13 GB | **1** |
| flux-dev-fp8 (H1=A) | manga panels (canonical) | 25-50 s | 120 s | 180 s | 13-14 GB | **1** |
| Qwen-Image | seinen/josei distinctness; CJK speech bubbles | 90-240 s | 600 s | 900 s | 20 GB → offload | **1** |
| Animagine XL 4.0 | shojo/iyashikei | 12-25 s | 75 s | 120 s | 10-12 GB | **1** |

**Source of truth:** [`skills/pearl-int/references/manga_render_path_decision.md`](../../skills/pearl-int/references/manga_render_path_decision.md) (H1=A canonical config; FLUX engine routing).

### §3.2 Workload class TTS

| Engine | Use case | Normal | Stall warn | Stall kill | Resource | Concurrency |
|---|---|---|---|---|---|---|
| CosyVoice2 0.5B (cross-lingual) | CJK audiobook, podcast, video narration | 5-15 s / 10-s seg | 45 s | 90 s | 1-2 GB GPU + CPU | **2-4** |
| Piper | English audiobook draft, light voice | 1-3 s / sentence | 15 s | 30 s | CPU-only or <100 MB GPU | **8** |
| ElevenLabs | English narration (paid; off-Pearl-Star) | — | — | — | — | — |

**Source:** [`docs/AUDIOBOOK_PIPELINE_SPEC.md`](../AUDIOBOOK_PIPELINE_SPEC.md) + [`config/tts/engines.yaml`](../../config/tts/engines.yaml).

### §3.3 Workload class LLM

| Engine | Use case | Normal | Stall warn | Stall kill | VRAM | Concurrency |
|---|---|---|---|---|---|---|
| Ollama qwen2.5:14b | CJK6 atom authoring, Pearl News CJK | 4-12 s / 200-tok | 45 s | 75 s | 9 GB | **1-2** (OLLAMA_NUM_PARALLEL) |
| Ollama gemma3:27b | English long-context, complex outline | 8-25 s / 200-tok | 90 s | 150 s | 17 GB → partial CPU | **1** |
| (Phase B) vLLM batch | high-throughput LLM serving (10-24× Ollama) | varies | — | — | model-dependent | depends on batch config |

**Source:** [`docs/PEARL_NEWS_WRITER_SPEC.md`](../PEARL_NEWS_WRITER_SPEC.md) (LLM routing) + Tier policy in [`CLAUDE.md`](../../CLAUDE.md).

### §3.4 Workload class ORCH (orchestration / pipeline glue)

CPU-bound multi-stage orchestration that composes T2I + TTS + LLM jobs into higher-level deliverables:
- Pearl_Prime ebook assembly (LLM-heavy; ~30-100 LLM atoms + 1 cover + epub assembly)
- Manga chapter production (T2I-heavy; 12 panels per chapter)
- Audiobook (TTS-heavy; 100-500 segments)
- Podcast (TTS + occasional LLM for show notes; 60 TTS chunks per 30-min podcast)
- Video (T2I frames + TTS narration + LLM scripts + ffmpeg composite)

Stall envelope = pipeline-level (3-5 h for production-deep_book_4h); per-sub-job stall thresholds inherit from §3.1-§3.3.

---

## §4 Queue + scheduler architecture

Full research + scoring in [`QUEUE_RESEARCH.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/QUEUE_RESEARCH.md) (45 citations).

### §4.1 Recommended architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                Pearl_Star_queue V1 (Phase A install)                │
│                                                                     │
│  Producer side                Worker side                           │
│  ─────────────                ───────────                           │
│  Pearl_Prime CLI       ───►   t2i-worker      (concurrency=1)       │
│  Pearl News cron       ───►   llm-worker      (concurrency=1-2)     │
│  Manga dispatcher      ───►   tts-worker      (concurrency=2-4)     │
│  Pearl_PM tracker      ───►   orch-worker     (concurrency=2)       │
│  Operator CLI          ───►                                          │
│                                                                     │
│           ┌──────────────────────────────────────┐                  │
│           │  Procrastinate (Python)  ◄─ Postgres 17                 │
│           │  • jobs table (durable; ACID)        │                  │
│           │  • SKIP LOCKED dispatch              │                  │
│           │  • LISTEN/NOTIFY low-latency wake    │                  │
│           │  • Built-in retries + periodic + locks│                 │
│           └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼   (one-at-a-time per workload class)
┌─────────────────────────────────────────────────────────────────────┐
│  ComfyUI + Persistent-Queue  |  Ollama systemd  |  CosyVoice2 svc   │
│  (port 8188)                  |  (port 11434)    |  (port 9880)     │
│                                                                     │
│             Single RTX 5070 Ti 16 GB VRAM  ←  the bottleneck         │
└─────────────────────────────────────────────────────────────────────┘
```

### §4.2 Primary recommendation: **Procrastinate + Postgres**

**Why:**
- ACID durability — Pearl Star reboot WAL-replays jobs intact ✓ (operator's hard requirement)
- One dependency (Postgres) that earns its keep beyond the queue: Pearl_PM tracker, dashboard, Pearl News metadata can move into the same Postgres later
- Async-first Python — fits Pearl_Prime + audiobook comparator + manga dispatcher patterns
- MIT license — commercial-clean
- Operator-friendly — single broker, well-understood, no K8s

**Score (per [`QUEUE_RESEARCH.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/QUEUE_RESEARCH.md) §3): 91/125 — top of the matrix.**

### §4.3 Fallback recommendation: **Dramatiq + Redis (Valkey BSD fork)**

**Why fallback:**
- If the operator declines a Postgres dependency
- Dramatiq's reliability defaults (acks-when-done, hardcoded) eliminate the most common Python task queue foot-gun (Celery's acks-early default)
- Redis is lighter at idle than Postgres (~20 MB vs 200 MB)
- Use **Valkey** (Linux Foundation BSD fork of Redis pre-7.4) to keep licensing clean

**Score: 84/125.**

### §4.4 GPU overlay (both paths): **ComfyUI-Persistent-Queue** + native ComfyUI queue

Pearl_Star_queue owns the durable system-wide work-list. ComfyUI-Persistent-Queue is a Comfy custom_node that adds reboot-resume to ComfyUI's in-process queue. Together: belt-and-suspenders for the image-gen layer.

### §4.5 Persistence model

**Durable:** every job is committed to Postgres before its enqueue API call returns. Worker dispatch acquires `FOR UPDATE SKIP LOCKED`; result written; transaction committed. Survives:
- `kill -9` of a worker (job remains "pending" or "in_progress" with worker-lease-expiry; another worker picks it up after lease timeout)
- ComfyUI / Ollama / CosyVoice2 service crash (worker reports failure; retry policy fires)
- Pearl Star reboot (Postgres WAL replay; systemd-managed workers auto-resume)
- Kernel panic / power loss (Postgres replay from last committed checkpoint; max data loss = last fsync interval per `synchronous_commit` setting)

**Pearl_Research recommends `synchronous_commit = on`** (default Postgres) for spec-compliant durability. Q-PSQ-PERSISTENCE-LEVEL-01 covers override.

### §4.6 Reboot-resume protocol

Phase A install adds these systemd units (all `WantedBy=multi-user.target`):
- `postgresql.service` (broker)
- `ollama.service` (already present)
- `comfyui.service` (NEW — hardens ComfyUI manual-start)
- `cosyvoice.service` (NEW — hardens CosyVoice2 manual-start)
- `pearlstar-queue@t2i.service`, `pearlstar-queue@llm.service`, `pearlstar-queue@tts.service`, `pearlstar-queue@orch.service` (per-workload worker pool)
- `pearlstar-watchdog.service`

Post-reboot, all units come up, Procrastinate workers poll their assigned queues, and pending jobs auto-resume. **Acceptance test:** enqueue 100 mixed jobs, reboot, all 100 complete with zero permanently lost.

### §4.7 GPU-lock semantics

The queue dispatches GPU-heavy workloads (`t2i` + `llm`) through a **shared GPU-lock**. Implementation:
- Pearl_Star_queue defines a queue group `gpu_heavy` containing `t2i` and `llm` workers
- Procrastinate's per-queue concurrency cap = 1 (only one `gpu_heavy` job dispatches at a time)
- Before dispatching a `t2i → llm` switch (or vice versa), the queue calls `ComfyUI POST /free` to unload the resident checkpoint
- Workers `tts` and `orch` are NOT in the `gpu_heavy` group; they run their own pools concurrently

**Alternative considered (Q-PSQ-LOCK-MODEL-01):** advisory PG_TRY_ADVISORY_LOCK at the Postgres layer for cross-worker GPU semaphore. Rejected for V1 — Procrastinate's per-queue concurrency is simpler.

---

## §5 Stall detection contract

Full detail in [`STALL_RECOVERY_RUNBOOK.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/STALL_RECOVERY_RUNBOOK.md).

### §5.1 Heartbeat protocol

- Every active worker emits a heartbeat JSONL line every **30 seconds** (Q-PSQ-WATCHDOG-INTERVAL-01 default)
- Heartbeat path: `/run/pearlstar-queue/heartbeat/<worker_id>.jsonl` (tmpfs — low overhead) + flushed to `/var/log/pearlstar-queue/heartbeat/` every 60 s (forensics)
- Heartbeat fields: `ts`, `worker_id`, `job_id`, `phase`, `elapsed_s`, `vram_used_mb`, `vram_free_mb`, `gpu_util_pct`, `expected_total_s`, `stall_warn_at_s`, `stall_kill_at_s`, `comfyui_prompt_id` (for t2i)

### §5.2 Watchdog

`pearlstar-watchdog.service` runs every **60 s** (Q-PSQ-WATCHDOG-INTERVAL-01):
- Reads all heartbeat journals
- For each ACTIVE job: compare `elapsed_s` to `stall_warn_at_s` (2× expected) and `stall_kill_at_s` (3× expected)
- Heartbeat silent > 90 s = worker CRASHED → skip warn, go to KILL
- AUTO-KILL: SIGTERM → 10-s grace → SIGKILL → verify VRAM reclaim → mark queue row `auto_killed` + retry per policy

### §5.3 Auto-recovery rules

Retry budgets per workload class (Q-PSQ-RETRY-BUDGET-01):
- t2i: 1 retry, 30-60 s backoff
- llm: 2 retries, 15 → 60 s backoff
- tts: 1 retry, 30 s backoff
- orch: 3 retries, 30 → 60 → 120 s backoff

Non-retryable failures → dead-letter queue (Q-PSQ-DEAD-LETTER-01 default = operator-review).

### §5.4 Operator alerts

File-drop alerts in V1: `artifacts/coordination/operator_alerts/<UTC>_<type>.jsonl`. Phase C upgrades to Pearl_PM tracker integration.

Alert types: STALL_WARN, STALL_KILL, WORKER_CRASHED, DEAD_LETTER, QUEUE_DEPTH_HIGH, VRAM_SATURATED, BROKER_HEARTBEAT_MISS.

---

## §6 Job sizing contract per workload

Full detail in [`JOB_SIZING_GUIDELINES.md`](../../artifacts/research/pearl_star_capacity_and_queue_20260611/JOB_SIZING_GUIDELINES.md).

### §6.1 The sizing principle (one-line)

> **One job = one atomic GPU dispatch.** Never bundle 1,000 panels into 1 job. Make them 1,000 jobs.

### §6.2 Caps

| Workload | Max single-job | Chunk rule | Concurrency cap | Do NOT mix with |
|---|---|---|---|---|
| flux-schnell | 1 image / 1024×1536 | 1,000 covers = 1,000 jobs | 1 | flux-dev concurrent, Ollama-large |
| flux-dev-fp8 (H1=A) | 1 image / 1080×1920 | 12 panels/chapter = 12 jobs | 1 | any VRAM-heavy |
| Qwen-Image | 1 image / 1024² | 1 image per dispatch | 1 | anything VRAM-heavy |
| Animagine XL | 1 image / 1024² | 1 image per dispatch | 1 | other t2i, large LLM |
| CosyVoice2 | 30-s audio chunk | podcast = 60 × 30-s jobs | 2-4 | Qwen-Image (VRAM contention) |
| Piper | 1 sentence | sentence-level dispatch | 8 | n/a |
| Ollama qwen14b | 1 completion / 2048 tok | atom-level dispatch | 1-2 | flux-dev, Qwen-Image |
| Ollama gemma27b | 1 completion / 2048 tok | atom-level dispatch | 1 | any t2i |

### §6.3 The four canonical operator scenarios

1. **1,000 book covers** → 1,000 enqueued t2i_flux_schnell jobs; ~3 h wall-clock serial; reboot-safe
2. **1,000 manga panels** → 1,000 enqueued t2i_flux_dev_h1a jobs; ~8-10 h wall-clock; reboot-safe
3. **30-min podcast** → 60 enqueued tts_cosyvoice2 chunk jobs @ 4 parallel = ~2.5 min; reboot-safe
4. **Pearl News LLM batch** → 25-75 enqueued llm_qwen14b jobs; ~5-10 min depending on parallel; reboot-safe

Composite (all four scenarios at once) → ~12 h end-to-end, dominated by image-gen serialization.

---

## §7 Operator dashboard / control surface

### §7.1 Phase A CLI: `pscli`

V1 ships `scripts/queue/pscli.py` as the operator's queue interface (Q-PSQ-DASHBOARD-01 default = CLI-only Phase A).

```
pscli status                                        # queue depth + active workers + recent stalls + dead-letter count
pscli list --workload t2i --status pending          # filtered list
pscli inspect <job_id>                              # full job + heartbeat history + retries
pscli pause                                         # halt dispatch (current jobs complete)
pscli resume                                        # resume dispatch
pscli drain                                         # accept no new + finish current (pre-reboot helper)
pscli kill <job_id>                                 # manual SIGTERM → SIGKILL
pscli requeue <job_id>                              # auto_killed/dead_letter → pending
pscli archive <job_id>                              # remove from operator-action surface
pscli vram-snapshot                                 # nvidia-smi diff vs last call
pscli unload-comfyui                                # POST /free to ComfyUI
```

### §7.2 Phase C upgrade: web UI

Phase C adds a self-hosted web dashboard (Q-PSQ-DASHBOARD-01 candidate = Prefect 3 in observability mode OR custom Procrastinate dashboard). Surface:
- Real-time queue depth per workload class
- Per-worker activity + heartbeat trend
- VRAM utilization timeline (linked to nvidia-smi exports)
- Stall + dead-letter timeline
- Job-replay button + filter

### §7.3 Manual operator overrides

The CLI commands above cover all manual overrides. No GUI dependency for emergency operator action.

---

## §8 Phased rollout

### Phase A — Foundation (Pearl_Int session; ~3-4 h)

1. Install PostgreSQL 17 (`apt install postgresql-17 postgresql-contrib`)
2. Create database + schema (`CREATE DATABASE pearl_star_queue`)
3. Install Procrastinate (`pip install procrastinate[psycopg3] && procrastinate schema --apply`)
4. Install ComfyUI-Persistent-Queue custom node
5. Author + install `pearlstar-watchdog.service`, `pearlstar-queue@*.service`, `comfyui.service`, `cosyvoice.service` systemd units
6. Author + install `pscli.py`
7. Pick **ONE workload class** to dogfood (Q-PSQ-ROLLOUT-PHASE-A-WORKLOAD-01 recommends **t2i flux-schnell** — highest volume; book covers are the operator's stated $-maker)
8. Smoke-test: enqueue 10 jobs → workers dispatch → all complete → reboot mid-batch → verify resume

**Phase A acceptance (operator signs off):**
- 10/10 jobs complete cleanly
- Reboot mid-batch → all jobs eventually complete + 0 permanently lost
- Watchdog auto-kills an injected stall (`sleep 600`) → retry succeeds with real job
- `pscli status` returns in <2 s
- `pscli pause / resume` halts + restarts dispatch correctly

### Phase B — Three more workload classes (Pearl_Dev; ~4-6 h)

1. Add `llm` worker pool routing to Ollama
2. Add `tts` worker pool routing to CosyVoice2 + Piper
3. Add `orch` worker pool for pipeline glue (Pearl_Prime book assembly, manga chapter, audiobook, podcast, video)
4. Wire `config/pipeline_registry.yaml` stages into the queue
5. Migrate `scripts/manga/queue_panel_renders.py` and similar dispatchers from direct-HTTP to queue-enqueue
6. Optional: install vLLM as Ollama replacement for high-throughput LLM (Phase B sub-task)

**Phase B acceptance:**
- All 4 workload classes operational
- Composite scenario (covers + panels + podcast + LLM) runs to completion
- Cross-workload serialization works correctly (`/free` calls fire between t2i ↔ llm)

### Phase C — Operator dashboard (Pearl_Dev + Pearl_Int; ~6-8 h)

1. Install Prometheus + Grafana (self-hosted) on Pearl Star
2. Install `node_exporter` + `nvidia_dcgm_exporter` + custom `pearlstar_queue_exporter`
3. Provision Grafana dashboards
4. Wire Pearl_PM tracker integration (alerts surface as tracker rows)
5. Optional web UI (Prefect 3 OR custom)

**Phase C acceptance:**
- Real-time dashboard reachable via Tailscale
- 7-day historical metrics visible
- Pearl_PM tracker auto-receives DEAD_LETTER + WORKER_CRASHED events

### Phase D — Scale-out / autoscaling (FUTURE; Pearl_Research recommends NOT V1)

When Pearl Star alone becomes the bottleneck:
1. Add Pearl Star 2 / 3 (additional GPU boxes; same Tailscale network)
2. Procrastinate workers on each box poll the same Postgres
3. Per-machine `nvidia-smi` reporting fed to a node-aware scheduler
4. Optional: migrate to Ray for true multi-node GPU-aware scheduling (Q-PSQ-PHASE-D-RAY-01)

---

## §9 Open Operator Questions (Q-PSQ-*; recommend defaults; do NOT decide)

| ID | Question | Recommended default | Alternatives |
|---|---|---|---|
| **Q-PSQ-PRIMARY-QUEUE-01** | Primary queue framework | **Procrastinate + Postgres** | Dramatiq + Redis (fallback); Huey (lite); ARQ (asyncio-only) |
| **Q-PSQ-BROKER-01** | Queue broker backend | **Postgres 17** | Redis (Valkey BSD); NATS JetStream; SQLite (Huey) |
| **Q-PSQ-COMFYUI-COMPOSE-01** | ComfyUI in-process queue handling | **Compose (Pearl_Star_queue front-of-queue + ComfyUI-Persistent-Queue)** | Replace ComfyUI's queue entirely; per-workload decision |
| **Q-PSQ-WATCHDOG-INTERVAL-01** | Heartbeat interval / watchdog tick | **30 s emit / 60 s tick** | 60 s emit / 60 s tick; 15 s emit / 30 s tick |
| **Q-PSQ-STALL-MULTIPLIER-01** | Stall threshold N × normal-floor | **N=3** | N=2; N=5; per-workload-class override |
| **Q-PSQ-RETRY-BUDGET-01** | Per-job retry budget | **1 retry transient (t2i, tts); 2 retries (llm); 3 retries (orch)** | 1 across all; 2 across all; per-workload-class |
| **Q-PSQ-DEAD-LETTER-01** | Failed-permanent destination | **Dead-letter queue + operator-review surface** | Auto-delete with log; operator-tier alert |
| **Q-PSQ-DASHBOARD-01** | Operator dashboard phasing | **CLI-only Phase A → web UI Phase C** | Web UI from Phase A; defer to operator-attended Pearl_Prime monitor |
| **Q-PSQ-CONCURRENT-LIMITS-01** | Per-workload concurrency caps | **50% of Phase 2 measured value (safety headroom)** | Accept Phase 2 measured; operator-override |
| **Q-PSQ-ROLLOUT-PHASE-A-WORKLOAD-01** | First workload class to dogfood | **t2i flux-schnell** (highest volume; book covers) | Qwen-Image (highest stall risk); CosyVoice2 (audiobook); Ollama (Pearl News) |
| **Q-PSQ-PERSISTENCE-LEVEL-01** | Queue persistence guarantee | **fsync every commit (synchronous_commit=on)** | write-back caching (faster; loses last few jobs on crash); in-memory (explicit non-durable) |
| **Q-PSQ-OBSERVABILITY-01** | Metrics + logs | **Basic file logs + nvidia-smi snapshots Phase A → Prometheus + Grafana Phase C** | Prometheus from Phase A; defer entirely |
| **Q-PSQ-LICENSE-BROKER-01** | If Redis chosen, which fork | **Valkey (Linux Foundation BSD)** | Redis OSS pre-7.4 (legacy BSD); Redis 7.4+ (RSAL/SSPL; licensing risk) |
| **Q-PSQ-PHASE-D-RAY-01** | Phase D multi-node scaling | **Defer; revisit when Pearl Star 2 exists** | Plan Ray migration now; never (stay single-box) |
| **Q-PSQ-BACKPRESSURE-01** | Queue depth threshold for alert | **N=500 pending per workload** | 100; 1000; operator-set |
| **Q-PSQ-VLLM-OLLAMA-01** | LLM serving in Phase B | **Keep Ollama; track vLLM** | Migrate to vLLM Phase B; dual-host Ollama + vLLM |

**Recommended defaults are MY recommendations — operator decides.**

---

## §10 Cross-references (existing subsystems)

| Subsystem | Owner | How this spec composes |
|---|---|---|
| `scripts/pipeline/` + `config/pipeline_registry.yaml` | Pearl_Dev | Each pipeline stage decomposes into queue jobs per §3 + §6 |
| ComfyUI workflows (`scripts/image_generation/comfyui_workflows/`) | Pearl_Dev / Pearl_Int | Workflow JSONs become job-payloads dispatched via t2i-worker |
| Ollama (Pearl Star) | Pearl_Int | LLM worker dispatches to Ollama HTTP API; OLLAMA_NUM_PARALLEL governs concurrency |
| CosyVoice2 (Pearl Star) | Pearl_Int | tts-worker dispatches to CosyVoice2 HTTP API |
| Pearl_Prime ebook (`scripts/run_pipeline.py` + `specs/PHOENIX_V4_5_WRITER_SPEC.md`) | Pearl_Dev / Pearl_Writer | Book assembly orch-job enqueues atom-level LLM jobs |
| Manga V2 (`config/manga/`, `scripts/manga/`) | Pearl_Dev | Chapter-production orch-job enqueues per-panel t2i jobs |
| Audiobook (`docs/AUDIOBOOK_PIPELINE_SPEC.md`) | Pearl_Dev | Per-sentence/segment tts-jobs |
| Podcast (`docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md`) | Pearl_Prime | 30-s tts-chunk jobs + assembly orch |
| Video (`docs/VIDEO_PIPELINE_SPEC.md`) | Pearl_Video | 14-stage pipeline decomposes into mixed-workload jobs |
| Pearl News (`docs/PEARL_NEWS_WRITER_SPEC.md` + GH workflows) | Pearl_News | Daily article atoms enqueued via llm-worker; Pearl Star vs cloud routing per existing logic |
| Integration registry (`docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §0) | Pearl_Int | Pearl Star endpoints (`COMFYUI_URL` / `QWEN_BASE_URL` / `COSYVOICE_URL`) consumed by workers via Keychain eval |
| Pearl_PM tracker (`docs/PEARL_PM_STATE.md`) | Pearl_PM | DEAD_LETTER + WORKER_CRASHED + QUEUE_DEPTH_HIGH alerts surface as tracker rows in Phase C |

---

## §11 LLM Tier Policy compliance per `CLAUDE.md`

This spec is fully **Tier 2 compliant** for scheduled / unattended Pearl Star workloads:
- **Pearl Star LLM:** Ollama (gemma3:27b English / qwen2.5:14b CJK6) — FREE + LOCAL + UNATTENDED-SAFE ✓
- **Pearl Star T2I:** ComfyUI (flux-schnell / flux-dev-fp8 / Qwen-Image / Animagine XL) — FREE + LOCAL ✓ + all commercial-clean per `manga_render_path_decision.md §V2 license list` ✓
- **Pearl Star TTS:** CosyVoice2 (CJK) + Piper (EN) — FREE + LOCAL ✓
- **NO paid LLM API calls anywhere in queue code.** `audit_llm_callers.py` clean check is Phase A acceptance gate.

**Tier 1 attended (operator-present) usage:**
- This spec was authored Tier 1 (Claude Code session with operator standing by — allowed per `CLAUDE.md`)
- Phase A install execution is Tier 1 (Pearl_Int session with operator confirming)
- Phase B-C ongoing operations are **Tier 2 only**

---

## §12 Cap-entry proposal — `PEARL-STAR-JOB-QUEUE-V1-01`

```yaml
cap_id: PEARL-STAR-JOB-QUEUE-V1-01
status: PROPOSAL                                    # PROPOSAL → (Pearl_Architect ratify) → ACTIVE
title: Pearl Star Job Queue V1 — persistent, GPU-aware, stall-recovering work-list
date: 2026-06-11
owner_primary: Pearl_Architect
owner_secondary: Pearl_Dev (impl), Pearl_Int (install), Pearl_PM (tracker integration)

decision:
  primary_queue: Procrastinate + Postgres 17
  fallback_queue: Dramatiq + Redis/Valkey
  gpu_overlay: ComfyUI-Persistent-Queue (custom_node)
  watchdog: Pearl_Star_queue native (Python; systemd-managed)
  persistence: ACID (synchronous_commit=on)
  rollout: Phase A (1 workload) → Phase B (4 workloads) → Phase C (dashboard) → Phase D (multi-node future)

architecture:
  workers:
    - t2i  (concurrency=1; GPU-locked)
    - llm  (concurrency=1-2; GPU-locked; serial with t2i)
    - tts  (concurrency=2-4 CosyVoice2 / 8 Piper; CPU-friendly)
    - orch (concurrency=2; CPU-only)
  broker: Postgres 17 (database: pearl_star_queue)
  framework: Procrastinate (Python, MIT, async-first)
  gpu_overlay: ComfyUI-Persistent-Queue
  watchdog: /run/pearlstar-queue/heartbeat/ + 60-s tick + 3× threshold

scope_in:
  - Single Pearl Star box (RTX 5070 Ti 16 GB)
  - 4 workload classes (t2i / llm / tts / orch)
  - Reboot-resume durability
  - Stall detection + auto-kill + retry policy
  - Operator CLI (pscli)
  - Phased rollout A → B → C
  - All Tier 2 (free + local) workloads

scope_out:
  - Multi-node clustering (Phase D future)
  - Paid LLM API integration (banned per CLAUDE.md)
  - Custom GPU scheduler (use Procrastinate per-queue concurrency)
  - Self-rolled message broker (use Postgres or Redis/Valkey)
  - K8s deployment (single-box Ubuntu only for V1)

cross_refs:
  - docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md (this spec)
  - artifacts/research/pearl_star_capacity_and_queue_20260611/HARDWARE_INVENTORY.md
  - artifacts/research/pearl_star_capacity_and_queue_20260611/SOFTWARE_INVENTORY.md
  - artifacts/research/pearl_star_capacity_and_queue_20260611/CONCURRENCY_MATRIX.md
  - artifacts/research/pearl_star_capacity_and_queue_20260611/QUEUE_RESEARCH.md
  - artifacts/research/pearl_star_capacity_and_queue_20260611/STALL_RECOVERY_RUNBOOK.md
  - artifacts/research/pearl_star_capacity_and_queue_20260611/JOB_SIZING_GUIDELINES.md
  - skills/pearl-int/references/manga_render_path_decision.md  # H1=A T2I canon
  - docs/INTEGRATION_CREDENTIALS_REGISTRY.md §0                # Pearl Star endpoints
  - config/pipeline_registry.yaml                              # pipelines that consume the queue
  - CLAUDE.md                                                  # Tier policy

open_questions: Q-PSQ-* (15) in §9 — see spec

next_action:
  - operator reviews deck + answers Q-PSQ-*
  - Pearl_Architect ratifies cap (PROPOSAL → ACTIVE)
  - Pearl_Int Phase A install ws (Postgres + Procrastinate + ComfyUI-Persistent-Queue + watchdog + first workload smoke)
  - Pearl_PM tracker captures Phase A→D rollout in a new tracker doc

owner_at_status_change: Pearl_Architect (ratification)
```

---

## §13 Acceptance criteria — Phase A install

Phase A is acceptance-tested by the following six criteria. ALL must pass before Phase A is marked DONE and Phase B begins:

| # | Criterion | Test | Pass condition |
|---|---|---|---|
| 1 | **Reboot-resume** | Enqueue 100 mixed jobs → reboot Pearl Star → verify completion | 100/100 eventually complete; 0 permanently lost |
| 2 | **Stall detection (timeout)** | Inject `sleep 600` t2i-worker job → watchdog observes | Watchdog logs STALL_WARN at 2× threshold; STALL_KILL at 3×; retry fires; retry's real job completes |
| 3 | **Crash detection (worker SIGKILL)** | `kill -9` t2i-worker mid-job → watchdog observes | Heartbeat-silent > 90 s → CRASHED → fresh worker spawned → job re-dispatched + completes |
| 4 | **VRAM reclaim** | After AUTO-KILL of a t2i job → `nvidia-smi` polling | VRAM returns to baseline within 30 s of kill |
| 5 | **Operator CLI** | `pscli status / pause / resume / inspect / kill` | All commands return correctly; `status` in <2 s; `pause` halts dispatch |
| 6 | **Tier policy** | `python3 scripts/ci/audit_llm_callers.py` over Phase A queue code | Clean (zero paid LLM API references) |

Smoke test combined: enqueue 100 jobs across t2i / llm / tts / orch → simulate stall + crash mid-batch → reboot Pearl Star → all 100 complete + 0 lost. **Recorded as Phase A install evidence per `docs/PEARL_PRIME_RELEASE_CONTRACT.md` evidence-bundle pattern.**

---

## §14 Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Postgres version skew on Pearl Star vs spec (recommends 17) | Low | Low | `apt install postgresql-17` is canonical Ubuntu 24.04; verify in Phase A install |
| ComfyUI-Persistent-Queue extension stale / abandoned | Medium | Medium | Pinned commit SHA in Phase A install runbook; ALT plan = roll Pearl_Star_queue side-of-ComfyUI persistence |
| Procrastinate breaking API change | Low | Medium | Pin `procrastinate==2.X` in Phase A install; update via ws process |
| Operator wants multi-box BEFORE Phase A acceptance | Low | High | Spec explicitly defers Phase D to future; don't try to do both at once |
| Single NVMe failure | Low | Catastrophic | Phase A install includes: nightly `pg_dump` to `/var/backups/postgres/` + R2 mirror via `scripts/artifacts/r2_sync.py` |
| Pearl Star Tailscale outage cuts producer access | Medium | Low (queue keeps running locally) | Producers enqueue via local SSH-tunnel or wait for Tailscale recovery; queue continues to dispatch what's already queued |
| ComfyUI in-process queue + Pearl_Star_queue race | Low | Low | Composition model dispatches one-at-a-time; ComfyUI's queue is the downstream consumer |
| vLLM migration breaks Ollama integration (Phase B sub-task) | Medium (if attempted) | Medium | Optional in Phase B; keep Ollama path as fallback; smoke before flipping |

---

## §15 Open follow-up workstreams (after operator answers Q-PSQ-*)

1. **`ws_pearl_architect_ratify_pearl_star_queue_v1_20260612`** — Pearl_Architect ratifies cap entry; flips PROPOSAL → ACTIVE
2. **`ws_pearl_int_phase_a_install_pearl_star_queue_20260613`** — Pearl_Int executes Phase A install per §8; emits evidence bundle
3. **`ws_pearl_dev_phase_b_workloads_pearl_star_queue_20260620`** — Pearl_Dev adds remaining 3 workload classes + wires `config/pipeline_registry.yaml` stages
4. **`ws_pearl_dev_phase_c_dashboard_pearl_star_queue_20260701`** — Pearl_Dev installs Prometheus + Grafana + Pearl_PM tracker integration
5. **`ws_pearl_pm_tracker_pearl_star_rollout_20260612`** — Pearl_PM creates rollout tracker doc (sibling to atom-coverage tracker)
6. **(FUTURE) `ws_phase_d_pearl_star_cluster_evaluation_TBD`** — when/if Pearl Star 2 lands

---

## §16 Spec status + revision history

| Version | Date | Author | Status | Change |
|---|---|---|---|---|
| 1.0 | 2026-06-11 | Pearl_Research | PROPOSAL | Initial authorship; awaiting Pearl_Architect ratification |

---

**Spec ends. See deck + 6 research deliverables for the full picture.**

# Pearl Star Job Queue V1 — Procrastinate schema / contract note

**Status:** Phase A (Pearl_Int install kit). Authoring-only — the operator runs
the install on Pearl Star.
**Authority:** `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md` (§4.2, §4.5, §4.7, §5, §6).
**Tier:** All Tier-2 (free + local) per `CLAUDE.md`. No paid LLM API anywhere in
queue code.

This note pins the contract that the install scripts, systemd units, worker, and
`pscli` all agree on. If you change a name here, change it in
`scripts/pearl_star/install/00_config.sh` too — that script is the executable
source of truth; this is the human-readable one.

---

## 1. Broker + connection

| Thing | Value | Why |
|---|---|---|
| Engine | PostgreSQL 17 | spec §4.2 primary recommendation; Ubuntu 24.04 via PGDG |
| Database | `pearl_star_queue` | spec §4.2 |
| Login role | `pearl_star` | created in `01_postgres17.sh` |
| **Schema** | **`pearl_star_queue`** | handoff §5.2 — Procrastinate tables live here, NOT `public` |
| Host:port | `127.0.0.1:5432` | spec §2 constraint 4 — localhost only (Tailscale/LAN reach via SSH tunnel) |
| Driver | psycopg3 (`procrastinate[psycopg]`) | spec §8 step 3 |
| DSN env | `PS_QUEUE_DSN` | injected by systemd `EnvironmentFile=/etc/pearl-star/queue.env`; never committed |
| Durability | `synchronous_commit = on` | spec §4.5 — every job committed before enqueue returns; survives reboot/power-loss |

The role's `search_path` is set to `pearl_star_queue, public` in
`01_postgres17.sh`, so `procrastinate schema --apply` lands its tables
(`procrastinate_jobs`, `procrastinate_events`, …) inside the dedicated schema.

## 2. Python app

| Thing | Value |
|---|---|
| **venv** | **`/opt/pearl-star/venv`** (handoff §5.2) |
| App import path | `app.app:app` (env `PROCRASTINATE_APP`) |
| Deployed sources | `/opt/pearl-star/app/{app.py, flux_schnell_worker.py, watchdog.py, monitor.py}` |
| Operator CLI | `/usr/local/bin/pscli` |
| Procrastinate pin | `procrastinate[psycopg]==2.*` (spec §14 — breaking-API risk) |

## 3. Queues + concurrency (the GPU-lock contract — spec §4.7)

| Queue | Concurrency | GPU-heavy | Phase | Notes |
|---|---|---|---|---|
| `t2i` | **1** | yes | **A** | flux-schnell now; GPU-locked. The ONE workload Phase A dogfoods (spec §8 step 7). |
| `llm` | 1 | yes | B | serial with `t2i` (shared GPU); Pearl_Dev wires Ollama. |
| `tts` | 4 | no | B | CosyVoice2 / Piper; CPU-friendly, runs concurrently with GPU work. |
| `orch` | 2 | no | B | CPU-only pipeline glue. |

GPU-lock = the GPU-heavy queues run at worker-concurrency 1 (spec §4.7 rejects a
PG advisory-lock for V1). Before a `t2i -> llm` switch the dispatcher calls
ComfyUI `POST /free` (`pscli unload-comfyui`) to evict the resident checkpoint.

## 4. Task contract (Phase A)

One task is registered in Phase A:

```
t2i_flux_schnell(prompt, negative="", width=1024, height=1536, seed=42,
                 job_label="book_cover") -> {status, prompt_id, output, workload}
    queue   = "t2i"
    retry   = 1            # spec §5.3 t2i budget: 1 retry, 30-60 s backoff
```

**One job = one atomic GPU dispatch = one image** (spec §6.1). 1,000 covers =
1,000 jobs, never one bundled job. flux-schnell sizing: 1 image / 1024×1536,
steps=4, cfg=1.0, euler/simple (schnell is incompatible with steps≥8 / cfg>1 —
faithful to `flux_txt2img_manga_brand2_schnell.json`).

## 5. Retry budgets (spec §5.3) — for Phase B parity

| Queue | attempts | backoff (s) |
|---|---|---|
| t2i | 2 (1 retry) | 30, 60 |
| llm | 3 (2 retries) | 15, 30, 60 |
| tts | 2 (1 retry) | 30 |
| orch | 4 (3 retries) | 30, 60, 120 |

Non-retryable failures → dead-letter at `/var/lib/pearl-star/dlq/`
(Q-PSQ-DEAD-LETTER-01 default = operator-review). `pscli requeue` / `archive`
manage that surface.

## 6. Stall contract (spec §5.1–§5.2)

| Thing | Value |
|---|---|
| Heartbeat cadence | 30 s (`PS_HEARTBEAT_INTERVAL_S`) |
| Heartbeat tmpfs path | `/run/pearl-star/heartbeat/<worker_id>.jsonl` |
| Forensic flush | every 60 s → `/var/log/pearl-star/heartbeat/` |
| Heartbeat fields | `ts, worker_id, job_id, phase, elapsed_s, vram_used_mb, vram_free_mb, gpu_util_pct, expected_total_s, stall_warn_at_s, stall_kill_at_s, comfyui_prompt_id` |
| Watchdog tick | 60 s (`PS_WATCHDOG_TICK_S`) |
| STALL_WARN | `elapsed_s ≥ 2× expected` (flux-schnell: 30 s) |
| STALL_KILL | `elapsed_s ≥ 3× expected` (flux-schnell: 60 s) → SIGTERM → 10 s grace → SIGKILL → verify VRAM reclaim |
| CRASHED | heartbeat silent > 90 s (`PS_HEARTBEAT_SILENCE_KILL_S`) → skip WARN, go to KILL |
| `worker_id` format | `<hostname>-t2i-<pid>` (the pid tail is what the watchdog/pscli signal) |

## 7. Alerts (spec §5.4)

File-drop JSONL to `/var/lib/pearl-star/operator_alerts/<UTC>_<type>.jsonl`.
Types: `STALL_WARN, STALL_KILL, WORKER_CRASHED, DEAD_LETTER, QUEUE_DEPTH_HIGH,
VRAM_SATURATED, BROKER_HEARTBEAT_MISS`. Phase C upgrades to Pearl_PM tracker.

## 8. Reboot-resume (spec §4.6)

All units are `WantedBy=multi-user.target`. Order: `postgresql@17-main` (broker)
→ `comfyui` (render backend) → `procrastinate-worker` (Requires broker) →
`pearl-star-watchdog` + `pearl-star-monitor`. Post-reboot the worker polls `t2i`
and pending jobs auto-resume. `pscli drain` is the clean pre-reboot helper
(pause + wait for `doing == 0`). tmpfs heartbeat dir is recreated on boot via
`/etc/tmpfiles.d/pearl-star.conf`.

## 9. What Phase A does NOT do (deferred)

- llm / tts / orch worker pools (Phase B — Pearl_Dev).
- Migrating existing dispatchers (`scripts/manga/queue_panel_renders.py`, Pearl
  News cron) from direct-HTTP to queue-enqueue (Phase B).
- Web dashboard / Prometheus / Grafana (Phase C).
- Multi-node (Phase D — future, NOT V1).

> **Cap status:** `PEARL-STAR-JOB-QUEUE-V1-01` was materialized **ACTIVE**
> 2026-06-11 (PR #1506; `docs/PEARL_ARCHITECT_STATE.md`) with OPD-20260611-021→036.
> The spec doc header still reads "PROPOSAL" (doc-lag — the spec text wasn't
> updated when the cap was ratified into the architect state); the authoritative
> status is ACTIVE. This Phase A install kit is therefore unblocked.

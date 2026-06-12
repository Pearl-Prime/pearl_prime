# Pearl Star Stall Detection + Recovery Runbook (Phase 4)

**Owner:** Pearl_Research (authoring) → Pearl_Architect (ratification) → Pearl_Dev (Phase A impl) → Pearl_Int (Phase A install)
**Companion:** [QUEUE_RESEARCH.md](./QUEUE_RESEARCH.md), [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md), [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
**Operator directive (verbatim paraphrase):** "Every time we run something there's a hiccup — text-to-image / text-to-speech / LLM jobs stall, the server hangs, work disappears. We need procedures to check on it every minute, kill the stuck process, and continue."

---

## §1 Per-workload stall signatures

Each workload class has a NORMAL wall-clock envelope and a STALL threshold = 3× normal (default; see Q-PSQ-STALL-MULTIPLIER-01 for override). Below is the canonical table for Pearl Star RTX 5070 Ti / 16 GB VRAM. **Numbers marked [M] are MODELED** from inventory data + Pearl Star runbook history + framework documentation; numbers marked [E] are **EMPIRICAL** (from Phase 2 concurrency matrix). Empirical numbers supersede modeled numbers when Phase 2 lands.

| Workload | Job unit | Normal wall-clock | STALL threshold | AUTO-KILL threshold | Source |
|---|---|---|---|---|---|
| **flux-schnell** (1024², CFG 1.0, steps 4, euler/simple) | 1 image | 6-12 s [M] | **30 s** | **60 s** | RunComfy benchmark + Pearl Star manga audit `artifacts/qa/flux_workflow_fix_smoke_2026-04-30.md` |
| **flux-dev-fp8** (1024², CFG 3.5, steps 28, dpmpp_2m/karras = H1=A) | 1 image | 25-50 s [M] | **120 s** | **180 s** | `skills/pearl-int/references/manga_render_path_decision.md` + canonical H1=A |
| **Qwen-Image** (1024², default schedule, CPU-offloaded) | 1 image | 90-240 s [M] | **600 s (10 min)** | **900 s (15 min)** | Modeled from 20 GB checkpoint > 16 GB VRAM = offload penalty |
| **Animagine XL 4.0** (1024², SDXL-class) | 1 image | 12-25 s [M] | **75 s** | **120 s** | SDXL-class baseline + Animagine V1.0 install notes |
| **CosyVoice2** (10-sec English TTS, cross-lingual mode) | 1 segment | 5-15 s [M] | **45 s** | **90 s** | CosyVoice2 GitHub benchmarks + `~/phoenix_server/CosyVoice2/example.py` |
| **CosyVoice2** (long-form: 5-min audio, chunked 30s) | 10 segments | 80-200 s [M] | **600 s** | **900 s** | Chunked = N × single-segment time |
| **Piper TTS** (English, 30-sec sentence) | 1 segment | 1-3 s [M] | **15 s** | **30 s** | Piper benchmark + lightweight CPU op |
| **Ollama gemma3:27b** (200-token completion, model in VRAM) | 1 completion | 8-25 s [M] | **90 s** | **150 s** | Model size 17.4 GB > 16 GB → likely CPU-spill on Pearl Star |
| **Ollama qwen2.5:14b** (200-token completion, model in VRAM) | 1 completion | 4-12 s [M] | **45 s** | **75 s** | Model size 9 GB fits in VRAM cleanly |
| **Pearl_Prime production-deep_book_4h** | 1 book | 10800-18000 s (3-5 h) | **N/A — pipeline-level** | — | Pipeline split into atom-jobs; per-atom threshold applies |
| **Manga chapter (12 panels @ flux-dev)** | 1 chapter | 12 × 30 s = 360 s | **N/A — sub-job basis** | — | Stall on PANEL basis, not chapter |
| **Podcast 30-min CJK** | 1 podcast | ~600-1200 s (10-20 min for CosyVoice2 chunked) | **N/A — segment basis** | — | Stall on SEGMENT basis |

### Two interpretation notes for the table

- **"Normal" is the 95th-percentile envelope** — not "best case." Anything slower than that for any individual workload should trigger Pearl_Int investigation.
- **AUTO-KILL = the watchdog's intervention threshold.** Beyond AUTO-KILL, the job is killed + the failure is logged + retry-or-fail policy fires.

### What's NOT a stall

- A job in the queue but not yet picked up by a worker (= queue depth, not stall). Surface as backpressure alert (Q-PSQ-DASHBOARD-01), not as stall.
- A worker waiting on `ComfyUI /prompt` HTTP response while ComfyUI itself is processing the prior job: that is **back-pressure**, not stall. Only the actual active job's wall-clock counts toward stall threshold.
- A retry-after-transient-failure that hasn't completed its retry budget: the in-flight retry counts, but the failed attempt does not.

---

## §2 Heartbeat protocol (the "every minute" check)

The operator's quote — "we have to have procedures to check on it, you know, every minute" — translates to a **heartbeat emit + watchdog consume** pattern.

### §2.1 Heartbeat producer (worker side)

Every job-running worker emits a heartbeat line to `/var/log/pearlstar-queue/heartbeat/<worker_id>.jsonl` every **30 seconds** (Q-PSQ-WATCHDOG-INTERVAL-01 default):

```json
{
  "ts": "2026-06-11T01:30:00Z",
  "worker_id": "t2i-worker-0",
  "job_id": "j_a1b2c3d4",
  "phase": "comfyui.dispatch.in_flight",
  "elapsed_s": 87.3,
  "vram_used_mb": 11340,
  "vram_free_mb": 4963,
  "gpu_util_pct": 92,
  "expected_total_s": 50,
  "stall_warn_at_s": 120,
  "stall_kill_at_s": 180,
  "comfyui_prompt_id": "abc123def456"
}
```

**Implementation:**
- Worker spawns a sidecar thread on job start; sidecar reads job metadata + ticks every 30 s.
- Heartbeat log is in tmpfs (`/run/pearlstar-queue/` mounted to RAM) for low overhead; flushed to `/var/log/...` every 60 s for crash forensics.
- Heartbeat log is **rotated daily**, **30-day retention** (the operator can inspect "what was happening at 3 AM last Tuesday").

### §2.2 Watchdog consumer

A dedicated `pearlstar-watchdog.service` (systemd unit) runs continuously and:

1. **Reads heartbeat JSONL files every 60 seconds** (Q-PSQ-WATCHDOG-INTERVAL-01 default).
2. **For each ACTIVE job** (a worker reported a heartbeat in the last 90 s):
   - Compute `elapsed_s` from heartbeat timestamp.
   - Compare to `stall_warn_at_s` (= **2× expected_total_s**, capped at workload-class threshold from §1).
   - Compare to `stall_kill_at_s` (= **3× expected_total_s**, capped at workload-class threshold).
3. **If a worker's heartbeat is SILENT for > 90 s** (3× heartbeat interval), mark it CRASHED — not just stalled. Different escalation path (CRASHED skips warn → goes straight to KILL).
4. **For each STALL_WARN candidate** (elapsed > warn threshold, < kill threshold):
   - Log to `/var/log/pearlstar-queue/stall_warn.jsonl`.
   - Emit operator-alert (file-drop to `artifacts/coordination/operator_alerts/`).
   - Take no kill action yet.
5. **For each STALL_KILL candidate** (elapsed > kill threshold OR heartbeat silent > 90 s):
   - Issue SIGTERM to the worker's PID.
   - Wait 10 s grace period.
   - If still alive: issue SIGKILL.
   - Verify process exit via `kill -0`.
   - **Verify VRAM reclaim:** poll `nvidia-smi` until the worker's previous VRAM footprint is freed (CUDA processes don't always die cleanly; `nvidia-smi --gpu-reset` is the nuclear option — operator-only).
   - Mark job in queue as `auto_killed` + retry-eligible per Q-PSQ-RETRY-BUDGET-01.

### §2.3 Watchdog implementation skeleton (Python, for Phase A install)

```python
# scripts/queue/watchdog.py
"""Pearl Star queue watchdog. Runs as pearlstar-watchdog.service."""
import json, time, os, signal, subprocess, pathlib

HB_DIR = pathlib.Path("/run/pearlstar-queue/heartbeat")
KILL_GRACE_S = 10
WD_INTERVAL_S = 60

def watchdog_tick():
    now = time.time()
    for hb_file in HB_DIR.glob("*.jsonl"):
        try:
            with open(hb_file) as f:
                lines = f.readlines()
            if not lines:
                continue
            last = json.loads(lines[-1])
        except (json.JSONDecodeError, FileNotFoundError):
            continue

        hb_age_s = now - parse_ts(last["ts"])
        if hb_age_s > 90:  # heartbeat silent > 3× interval
            handle_silent(last, hb_age_s)
            continue

        elapsed = last["elapsed_s"]
        if elapsed > last["stall_kill_at_s"]:
            kill_worker(last, reason="stall_kill_threshold")
        elif elapsed > last["stall_warn_at_s"]:
            warn_worker(last, reason="stall_warn_threshold")

def kill_worker(hb, *, reason):
    # 1. SIGTERM the worker PID (recorded in the heartbeat sidecar).
    pid = hb.get("worker_pid")
    if pid: 
        os.kill(pid, signal.SIGTERM)
        time.sleep(KILL_GRACE_S)
        if pid_alive(pid):
            os.kill(pid, signal.SIGKILL)
    # 2. Verify VRAM reclaim.
    wait_for_vram_drop(target_free_mb=hb.get("vram_used_mb", 0))
    # 3. Update queue job status: auto_killed + retry per policy.
    procrastinate_mark_killed(hb["job_id"], reason=reason)
    # 4. Operator alert.
    emit_alert("AUTO_KILL", hb, reason)

if __name__ == "__main__":
    while True:
        try:
            watchdog_tick()
        except Exception as e:
            log_error(e)
        time.sleep(WD_INTERVAL_S)
```

Final implementation lives in `scripts/queue/watchdog.py` (Phase A scope; this runbook authors the spec, not the code).

---

## §3 Auto-recovery rules

When a job hits AUTO-KILL or its worker is detected CRASHED, the queue's retry policy decides what happens next.

### §3.1 Retry policy (per workload class)

| Workload class | Max retries | Retry backoff | Notes |
|---|---|---|---|
| t2i (flux-schnell / flux-dev / Animagine) | **1** | 30 s | Image-gen failures are often deterministic — retry once for transient VRAM/OOM, then surface |
| t2i (Qwen-Image, CPU-offloaded) | **1** | 60 s | Slower retry due to model reload cost |
| llm (Ollama) | **2** | 15 s → 60 s | LLM transients are common (model warmup, transient HTTP timeout) |
| tts (CosyVoice2) | **1** | 30 s | TTS retries cheap; preserve reference audio + seed |
| orchestration (pipeline-stage) | **3** | 30 s → 60 s → 120 s | Multi-stage pipelines have legitimate transient failures (filesystem, network) |
| All workload classes (default) | **1** | 60 s | Q-PSQ-RETRY-BUDGET-01 default |

### §3.2 Retryable vs non-retryable failures

**Retryable:**
- VRAM OOM after another job's checkpoint resident at job-start (re-dispatch after `/free`)
- Network blip to ComfyUI / Ollama / CosyVoice2 endpoint (HTTP timeout, ConnectionRefused on first retry, recovered on second)
- Watchdog AUTO-KILL where the cause was transient stall (resource contention)
- Worker process crash (CRASHED) — fresh worker spawned, job re-dispatched

**Non-retryable (permanent failure → dead-letter queue):**
- 3 consecutive OOMs on the same job (signals job-too-big — sizing problem, not transient)
- Auth failure (missing model file, broken config) — operator-action-required
- Missing input file (e.g., reference audio path doesn't exist) — operator-action-required
- Workflow JSON malformed (ComfyUI 422 — graph-shape mismatch per `manga_render_path_decision.md`)
- Workload runs > 5× normal AND watchdog AUTO-KILLs twice → mark dead-letter (extreme outlier; operator-investigate)

### §3.3 Dead-letter queue (Q-PSQ-DEAD-LETTER-01 default = operator-review queue)

Permanent failures land in `pearl_star_queue.dead_letter` Postgres table. Surface in operator dashboard with:
- Job ID, workload class, original payload (truncated if huge)
- Failure history (each retry attempt's stall log)
- Operator action: re-enqueue (after fixing root cause) / archive / delete

---

## §4 Operator alert surfaces

### §4.1 Alert types

| Alert | Trigger | Channel | Operator action |
|---|---|---|---|
| `STALL_WARN` | Heartbeat shows elapsed > 2× expected | File-drop → `artifacts/coordination/operator_alerts/stall_warn_<UTC>.jsonl` | Monitor; no action required |
| `STALL_KILL` | Watchdog auto-killed a stalled job | Same + Pearl_PM tracker integration (Phase C) | Review reason; verify retry succeeded |
| `WORKER_CRASHED` | Worker heartbeat silent > 90 s | Same | Investigate worker; may indicate VRAM corruption / kernel-driver issue |
| `DEAD_LETTER` | Permanent failure | Same | Manual triage; root-cause fix |
| `QUEUE_DEPTH_HIGH` | Queue > N pending (Q-PSQ-BACKPRESSURE-01) | Same | Decide: pause producers, add workers, or accept backlog |
| `VRAM_SATURATED` | nvidia-smi VRAM > 90% used for > 5 min | Same | Pause new t2i jobs; consider serial mode |
| `BROKER_HEARTBEAT_MISS` | Postgres unreachable from worker | systemd `pearlstar-watchdog.service` failure | Investigate broker; CRITICAL alert |

### §4.2 Alert delivery

V1 (Phase A): **file-drop alerts** to `artifacts/coordination/operator_alerts/<UTC>_<type>.jsonl`. Operator polls this directory (or wires a small cron to summarize daily).
Phase C: Web UI + Pearl_PM tracker integration. Phase D: notifications (Slack / email / iMessage).

---

## §5 Manual operator overrides

The operator MUST have a CLI to manage the queue without web UI dependency. V1 ships these commands as `scripts/queue/pscli.py`:

| Command | What it does |
|---|---|
| `pscli status` | Queue depth per workload class + active workers + last 5 stalls + dead-letter count |
| `pscli pause` | Stop dispatch (workers complete current jobs; no new) |
| `pscli resume` | Resume dispatch |
| `pscli drain` | Drain current + reject new (graceful Pearl Star shutdown helper) |
| `pscli kill <job_id>` | Manual SIGTERM → SIGKILL on a specific job |
| `pscli requeue <job_id>` | Move job back to pending (from auto_killed / dead_letter) |
| `pscli archive <job_id>` | Move to archive (no retry, no operator-action surface) |
| `pscli list --workload t2i --status pending` | Filter view |
| `pscli inspect <job_id>` | Full job + heartbeat history + retry attempts |
| `pscli vram-snapshot` | nvidia-smi diff vs last call (for forensics) |
| `pscli unload-comfyui` | Calls ComfyUI `/free` (operator-controlled checkpoint unload) |

CLI source of truth: queries Procrastinate's tables directly + heartbeat journals.

---

## §6 Reboot-resume protocol

Pearl Star reboot (planned or unplanned) MUST not lose work.

### §6.1 Pre-reboot (planned)

```bash
ssh pearl_star sudo pscli drain --wait-for-active
# Workers complete current jobs; new jobs queue but don't dispatch.
# After all active jobs complete:
ssh pearl_star sudo systemctl stop pearlstar-watchdog pearlstar-queue@* comfyui cosyvoice
# Postgres stays running; jobs durable in postgres.
ssh pearl_star sudo reboot
```

### §6.2 Post-reboot (planned OR unplanned)

systemd auto-starts (Phase A install adds these units):
1. `postgresql.service` (Postgres broker comes up with WAL replay; all pending jobs intact)
2. `ollama.service` (LLM model server; already systemd-managed)
3. `comfyui.service` (Phase A adds; loads ComfyUI on boot)
4. `cosyvoice.service` (Phase A adds; loads CosyVoice2 on boot)
5. `pearlstar-queue@t2i.service`, `pearlstar-queue@llm.service`, `pearlstar-queue@tts.service`, `pearlstar-queue@orch.service` (Phase A adds; per-workload Procrastinate workers)
6. `pearlstar-watchdog.service` (Phase A adds; heartbeat + stall detection)

After all units `active`, the queue resumes:
- Workers poll Procrastinate's `procrastinate_jobs` table for pending jobs.
- ComfyUI-Persistent-Queue restores its in-process queue from disk.
- Heartbeat journals start fresh (old journals archived to /var/log).

**Acceptance:** end-to-end test = enqueue 100 jobs of mixed workload classes → reboot Pearl Star mid-dispatch → verify all 100 eventually complete + 0 permanently lost. This is a Phase A install acceptance criterion (§12).

### §6.3 Crash-recovery (unplanned, partial-state)

If Pearl Star crashes WHILE a job is dispatched (worker process killed by SIGKILL, Pearl Star kernel panic, power loss):
1. Postgres WAL replays on restart; job's row reverts to "pending" if the worker hadn't committed the result yet.
2. The dispatching worker's heartbeat journal stays on disk (forensics).
3. The new worker pool dispatches the still-pending job.
4. `ComfyUI-Persistent-Queue` may resurface the job in ComfyUI's queue too — that's fine; idempotency at the workflow level (output filename includes job_id + seed) ensures the second dispatch overwrites cleanly.

---

## §7 Telemetry + observability (Q-PSQ-OBSERVABILITY-01)

**V1 (Phase A):**
- Per-job heartbeat JSONL @ `/var/log/pearlstar-queue/heartbeat/`
- Stall warn / kill / dead-letter JSONL @ `/var/log/pearlstar-queue/`
- nvidia-smi snapshot every 5 min @ `/var/log/pearlstar-queue/nvidia/`
- Procrastinate built-in query stats (jobs by status, by workload, by attempt)

**Phase C upgrade (operator dashboard):**
- Prometheus + Grafana on Pearl Star (free, self-hosted)
- Prometheus exporters: `node_exporter` (system) + `nvidia_dcgm_exporter` (GPU) + a custom `pearlstar_queue_exporter` (queue metrics)
- Grafana dashboards: per-workload-class throughput, per-worker stall rate, VRAM utilization timeline, queue depth trend

---

## §8 The "every minute we check" workflow embodied

Operator's quote unpacked into actionable runbook:

1. **The check happens automatically.** Watchdog runs every 60 s. Operator does not poll.
2. **The "this is not normal" detection is the stall_warn_at_s threshold.** When a job exceeds 2× expected, the watchdog flags it.
3. **"Let me stop it" is the watchdog's SIGTERM at the kill threshold.** Operator does not have to intervene; the killer is the watchdog.
4. **"Change something" is the auto-recovery + dead-letter pattern.** If retries succeed → keep going. If retries exhaust → dead-letter for operator review with full forensic trail.

The operator's "every minute" is now an SLA on the watchdog tick, not a chore on the operator's calendar.

---

## §9 Acceptance criteria for Phase A install (this runbook's contract)

The Phase A install is acceptance-tested by:

1. **Reboot-resume:** enqueue 100 mixed jobs → reboot Pearl Star → 0 permanently-lost jobs after recovery.
2. **Stall detection:** inject a `sleep 600` "job" into the t2i worker queue → watchdog flags at 120 s, kills at 180 s, retries once, retry succeeds (real job), dead-letter empty.
3. **Crash detection:** inject `kill -9` on a t2i worker mid-job → watchdog detects heartbeat-silent > 90 s, marks worker CRASHED, job re-dispatched to fresh worker, completes.
4. **VRAM reclaim:** after AUTO-KILL of a t2i job, `nvidia-smi` shows VRAM drops to baseline within 30 s of kill.
5. **Operator CLI:** `pscli status` returns valid output in <2 s; `pscli pause` halts dispatch; `pscli resume` restarts.
6. **No paid LLM API calls:** `audit_llm_callers.py` clean on Phase A queue code per `CLAUDE.md` Tier policy.

---

## §10 Cross-references

- Job sizing (Phase 5): [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md)
- Concurrency matrix (Phase 2): [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
- Queue research (Phase 3): [QUEUE_RESEARCH.md](./QUEUE_RESEARCH.md)
- V1 spec (Phase 6): [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md)
- Pearl_Int operational baseline: [`skills/pearl-int/SKILL.md`](../../../skills/pearl-int/SKILL.md)
- Tier policy: [`CLAUDE.md`](../../../CLAUDE.md) §LLM Tier Policy

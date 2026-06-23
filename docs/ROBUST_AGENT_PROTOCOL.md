# Robust Agent Protocol (RAP) — Pearl Star Execution

**Status:** ACTIVE (2026-06-23)
**Owner:** Pearl_Architect / Pearl_GitHub
**Authority:** `docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`
**Applicability:** Mandatory for `pearl-int`, `pearl_architect`, `pearl_github`, and all agents dispatching to Pearl Star.

## §1 The Problem
Agents often hang or fail silently when running long-running or VRAM-intensive tasks on Pearl Star (Ollama, ComfyUI, CosyVoice2). Raw Bash execution lacks stall detection, reboot-resume, and job-sizing enforcement.

## §2 The Solution: Queue-First Dispatch
Every agent request to Pearl Star must follow the **Queue-First** pattern. NEVER run a GPU/LLM task directly via Bash if it takes > 10 seconds.

### §2.1 Standard Dispatch Pattern
1. **PRE-CHECK**: Run `pscli status` to verify the queue is RUNNING and not PAUSED.
2. **ENQUEUE**: Use `pscli enqueue --task <task> --payload '<json>'` to hand work to the durable broker.
3. **POLL (Wait-with-Heartbeat)**: 
   - Periodically check `pscli inspect <job_id>` or `pscli status`.
   - Use a local session timeout (e.g., 2× expected duration) to avoid hanging the agent session.
4. **VERIFY**: Check output paths or result logs before reporting completion.

## §3 Job Sizing Rules
Agents must ensure jobs are "right-sized" per `PEARL_STAR_JOB_QUEUE_V1_SPEC.md §6`:
- **Atomic Dispatch**: One image, one completion, or one audio chunk per job.
- **No Bundling**: Do not bundle 1,000 images into one script. Make them 1,000 individual queue jobs.
- **VRAM Respect**: Respect the single GPU (16 GB VRAM) bottleneck.

## §4 Stall Detection & Intelligent Reacting
If a job stalls or fails, agents must not ignore it.

### §4.1 Stall Thresholds
| Workload | Stall Warn | Stall Kill | Expected |
|---|---|---|---|
| T2I (Flux-Schnell) | 30 s | 60 s | 6-12 s |
| T2I (Flux-Dev) | 120 s | 180 s | 25-50 s |
| LLM (Qwen-14b) | 45 s | 75 s | 4-12 s / 200 tok |
| TTS (CosyVoice2) | 45 s | 90 s | 5-15 s / seg |

### §4.2 Reaction Protocol
1. **Identify**: Run `pscli inspect <job_id>` to see heartbeat history and exit code.
2. **Audit**: If `failed`, check `/var/log/pearl-star/heartbeat/` or task-specific logs for errors (e.g., OOM, CUDA error).
3. **Act**:
   - **Transient (Network/Hiccup)**: `pscli requeue <job_id>`.
   - **Deterministic (Config/Code)**: Fix the underlying issue (edit config, repair script) then requeue or re-enqueue.
   - **Hardware (OOM/VRAM)**: Unload ComfyUI (`pscli unload-comfyui`) or reduce job size.
   - **Escalate**: If three retries fail, escalate to the operator with a full audit trace.

## §5 Reboot-Resume Protocol
The queue is ACID-compliant and survives server reboots.
- If Pearl Star reboots, do NOT re-enqueue existing jobs.
- Use `pscli status` to confirm jobs resumed automatically.
- Only re-enqueue if `pscli list --status pending` shows missing work.

## §6 Agent Skill Integration
- **Pearl_Int**: Use for installing/configuring queue services and monitoring health.
- **Pearl_GitHub**: Use for commits/PRs related to queue config and health checks.
- **Pearl_Architect**: Use for sizing decisions and workload decomposition.

---
*Reference: scripts/pearl_star/bin/pscli*

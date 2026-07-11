# Pearl Star Queue Health Packet — 2026-07-12

**Agent:** Pearl_Int  
**Workstream:** `ws_pearl_star_queue_health_packet_20260712`  
**Project:** `proj_manga_first_ship_20260425`  
**Probe timestamp (UTC):** `2026-07-11T22:22:16Z` (box) / packet land `2026-07-11T22:30:37Z`  
**Live anchor SHA:** `539b2e46641c480f68eafecc064203b6367dc892` (`origin/main` at land time)  
**Audit input anchor:** `bfb2ff40c0e4426630296a4657de7fc467adbb9e` (manga audit 2026-07-12) — **differs** from live tip (main advanced during this lane via `#5556`)

---

## STARTUP_RECEIPT

```
STARTUP_RECEIPT
AGENT: Pearl_Int
TASK: Pearl Star queue health packet + PR #4565 fit decision
PROJECT_ID: proj_manga_first_ship_20260425
WORKSTREAM_ID: ws_pearl_star_queue_health_packet_20260712
SUBSYSTEM: integrations;manga_pipeline;pearl_devops
AUTHORITY_DOCS: skills/pearl-int/SKILL.md (origin/main); docs/PROGRAM_STATE.md (origin/main); docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_PM_STATE.md (origin/main); docs/PEARL_ARCHITECT_STATE.md (origin/main queue/cap grep); artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (origin/main); docs/DOCS_INDEX.md; artifacts/analysis/MANGA_PIPELINE_RENDER_QUEUE_STATUS_AUDIT_2026-07-12.md; artifacts/analysis/MANGA_RENDER_SURFACE_INVENTORY_2026-07-12.tsv; docs/specs/MANGA_PRODUCTION_OPERATIONAL_V1_SPEC.md (origin/main); docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md (origin/main); docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md (origin/main); artifacts/coordination/MANGA_CLOUD_SUBSTRATE_REPAIR_CLOSEOUT_2026-07-11.md; artifacts/coordination/MANGA_CLOUD_FANOUT_IMPL_WAVE_CLOSEOUT_2026-07-11.md; gh pr view 4565
READ_PATH_COMPLETE: yes
WRITE_SCOPE: artifacts/coordination/PEARL_STAR_QUEUE_HEALTH_PACKET_2026-07-12.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (this row only)
OUT_OF_SCOPE: docs/PROGRAM_STATE.md; docs/PEARL_ARCHITECT_STATE.md; scripts/pearl_star/ops/queue_reaper.sh; scripts/pearl_star/ops/install_queue_reaper.sh; docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md; stillness proof; render-surface deletions; queue redesign
PROVENANCE: none (operations-class / bugfix-class)
EXECUTION_MODE: local_fallback
BACKGROUND_SAFE: no
RUNTIME_HOST: Ahjans-MacBook-Air.local (SSH probe target: pearlstar / 100.92.68.74)
PERSISTENCE_SURFACES: artifacts/coordination/PEARL_STAR_QUEUE_HEALTH_PACKET_2026-07-12.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv row; remote branch agent/pearl-star-queue-health-packet-20260712
RESUME_SURFACE: artifacts/coordination/PEARL_STAR_QUEUE_HEALTH_PACKET_2026-07-12.md
BLOCKERS: none for probe; merge of this packet subject to governance CI
READY_STATUS: ready
```

---

## Execution-mode honesty

| Field | Value |
|---|---|
| Preferred substrate | `pearl_star_remote` |
| Actual mode | **`local_fallback`** |
| Why | Operator laptop ran SSH probes against Pearl Star and wrote repo coordination artifacts locally; runtime persistence for this packet is git/GitHub, not box-side |
| BACKGROUND_SAFE | **no** (laptop session; SSH is not cloud-coding substrate) |
| Not claimed | Cursor Cloud / Codespaces / GHA coding agent (orthogonal; `ws_manga_cloud_substrate_repair_20260711` remains blocked) |

Execution-fabric docs (`AGENT_EXECUTION_FABRIC_V1_SPEC.md`, cloud-first runbook, surface matrix) remain **absent on `origin/main`** — not treated as live authority.

---

## Mandated discovery (pre-repair)

1. **Live `origin/main`:** `539b2e46641c480f68eafecc064203b6367dc892` — **differs** from audit anchor `bfb2ff40c0…` (main moved; atom PR `#5556`).
2. **Execution mode:** `local_fallback` / `BACKGROUND_SAFE=no` (see above).
3. **Overlap:** No ACTIVE_WORKSTREAMS row owns `PEARL_STAR_QUEUE_HEALTH_PACKET_2026-07-12.md`. Open PR **#4565** still exclusively owns `scripts/pearl_star/ops/queue_reaper.sh`, `install_queue_reaper.sh`, and queue-spec §16 doc edits. No stand-down conflict.
4. **Pearl Star reachability:** SSH OK → hostname `pearlstar`, user `ahjan108`.
5–8. See matrix / snapshot / diagnosis below.

---

## Box / service matrix

| Surface | State | Evidence |
|---|---|---|
| SSH | **up** | `ssh pearl_star` → `pearlstar`, uptime 78d, load ~0.06 |
| PostgreSQL 17 (`postgresql@17-main`) | **up** | `active (running)` since 2026-06-17; DB `pearl_star_queue` connections idle |
| ComfyUI HTTP `:8188` | **up** | `curl /system_stats` OK (ComfyUI 0.18.1, RTX 5070 Ti); `/queue` empty |
| ComfyUI systemd `comfyui.service` | **dead / drift** | unit `inactive` since 2026-05-06; live process is nohup PID `3567277` since May 19 (`~/phoenix_server/ComfyUI`) |
| Watchdog `pearl-star-watchdog` | **up** | active since 2026-06-17; recent AUTO-KILL heartbeats Jul 9–10 |
| Monitor `pearl-star-monitor` | **up** | active; recent `VRAM_SATURATED` alerts Jul 10–11 |
| Worker `procrastinate-worker` (t2i) | **up** | active since Jul 10 12:47 PDT; queues `t2i` concurrency 1 |
| Worker `procrastinate-worker-llm` | **up** | active since Jun 28 |
| Ollama | **up** | active |
| Heartbeat / lib paths | present | `/var/lib/pearl-star/` (`gpu_heavy.lock`, `operator_alerts/`, `dlq/`, `manga_out/`, `output/`); reaper log `~/.local/log/ps_queue_reaper.log` |
| GPU / VRAM | idle-ish | `10479 / 16303 MiB` used, util `0%` at probe (models resident; not actively rendering) |

---

## Queue snapshot (Postgres `procrastinate_jobs`)

| Metric | Value |
|---|---|
| Counts by status (all queues) | `succeeded=555`, `failed=40`, **todo=0**, **doing=0** |
| t2i | `succeeded=470`, `failed=34`, todo=0, doing=0 |
| llm | `succeeded=85`, `failed=6`, todo=0, doing=0 |
| Oldest `todo` age | **n/a** (empty) |
| Oldest `doing` age | **n/a** (empty) |
| Obvious zombie/orphan `doing` rows | **no** |
| Dead-letter / retry evidence | 7d events: `deferred_for_retry=41`, `failed=35`; recent failed cluster `t2i_flux_schnell` ids 556–570 @ 2026-07-09 ~13:39 PDT (historical, not live backlog) |
| Reaper log (live) | every `*/5` through probe window: `reaped=0 t2i_todo=0 t2i_doing=0` |
| Historical reaper action | `reaped_nonzero=7` (Jun 30, Jul 7); `WARN worker-starved` ×9 (Jul 7, Jul 9 23:30–Jul 10 00:05) — **cleared**; not present now |
| `gpu_heavy.lock` metadata | stale JSON for dead PID `1118072` (watchdog-killed Jul 10); **fcntl flock free** (kernel released on process death) — cosmetic, not blocking |
| `gpu_lane` | absent |
| Queue pause file | absent |

`pscli status` from interactive SSH without sourcing DSN fails (`PS_QUEUE_DSN not set`); queue truth taken via DSN from `~/.config/pearl-star/llm-worker.env` + `psql` (same source the reaper uses).

---

## Box-side reaper vs PR #4565

| Check | Result |
|---|---|
| Script present | **yes** — `~/.local/bin/ps_queue_reaper.sh` |
| Installer present on box repo path | **no** — `~/phoenix_omega/scripts/pearl_star/ops/install_queue_reaper.sh` absent |
| Cron present | **yes** — `*/5 * * * * /home/ahjan108/.local/bin/ps_queue_reaper.sh` |
| Alert env | **absent** — `~/.config/pearl-star/alert.env` missing (ntfy optional; starvation pushes currently no-op) |
| SHA256 box == PR #4565 file | **`c92f71d59940a62b110496ef4661bd8fd4f089e96f23fb4d48fc2af10ff5dbc8`** — **byte-identical** (`diff` empty) |
| On live `origin/main`? | **absent** — reaper scripts not in tip `539b2e46…` |
| PR #4565 state | **OPEN**, `MERGEABLE`, owns exact three paths (reaper + installer + spec §16) |

### Fit verdict: `match`

PR #4565 is the **right durable repo fix**: it lands in git what is already installed and running on the box (byte-identical reaper + installer + spec note). It does **not** need a duplicate PR. It is **not** required to clear a live drop (there is none). Optional gap after merge: operator creates `alert.env` with `PS_ALERT_NTFY_URL` so starvation pushes fire.

Not `absent` (script already on box). Not `drift` (hash match). Not `superseded` (still absent from main). Not `not-needed` for durability — main still lacks the scripts.

---

## Repair applied

**`pearl-star-queue-repair-applied=no`**

- No dead queue worker to restart (t2i + llm active).
- No zombie `doing` rows to requeue (reaper already idle-success).
- Cron already present; do not re-copy unmerged PR code onto the box.
- Stale `gpu_heavy.lock` JSON is cosmetic (flock free); file owned by `pearl-star` and not writable without sudo — clearing metadata is not required for dequeue health.
- Did **not** restart ComfyUI systemd over the live nohup process (risk of dual listeners / interrupt). Noted as follow-on substrate hygiene only.

---

## Direct answers

### Is the Pearl Star queue actually dropping work?

**No — not on the live probe.** Backlog is empty (`todo=0`, `doing=0`). Workers, Postgres, ComfyUI HTTP, watchdog, and reaper cron are up. Historical starvation (Jul 9–10) and failed t2i cluster (Jul 9) exist in logs/DB but are not a current drop. Perceived manga “work disappearing” is **not** explained by a live Pearl Star queue jam; look upstream (nothing enqueued / manga dispatch) or at historical Jul 9–10 worker crashes + VRAM saturation.

### Is PR #4565 the right fix, partially the right fix, or the wrong fix?

**Right durable fix (`match`) for keeping the already-proven on-box reaper in git + documenting install/alerts.** It is only a **partial** operational fix for past starvation (alerts need `alert.env`). It is the **wrong** fix if the goal is “make manga render progress right now” — the live queue is already healthy and empty.

---

## Root cause (one sentence)

The live Pearl Star Procrastinate queue is healthy and empty; prior orphan/`doing` starvation is already guarded by an on-box reaper that byte-matches open PR #4565, so the remaining durable gap is that those scripts are still unmerged to `main`, not a live drop pipeline.

---

## One exact next fix

**Merge open PR #4565** (`feat(pearl_star): queue reaper in git + ntfy starvation alerts`) — do not open a second PR touching `queue_reaper.sh` / `install_queue_reaper.sh`. After merge, operator optionally adds `~/.config/pearl-star/alert.env`. Manga render progress then resumes via enqueue/dispatch lanes (out of this packet’s scope), not via further queue-reaper authorship.

Follow-ons (named, not done here): re-bind ComfyUI to systemd (unit dead vs nohup live); optional stale lock metadata cleanup as `pearl-star`; PROGRAM_STATE refresh for manga (explicitly out of scope).

---

## Required output tags

```
pearl-star-queue-live-state=healthy
pearl-star-queue-rootcause=Live Pearl Star queue empty and healthy; on-box reaper already byte-matches PR #4565 — durable gap is unmerged scripts on main, not a live drop.
pearl-star-queue-reaper-fit=match
pearl-star-queue-repair-applied=no
pearl-star-queue-next-fix=Merge open PR #4565 (do not duplicate reaper files); optional alert.env after merge.
pearl-star-queue-health-packet=artifacts/coordination/PEARL_STAR_QUEUE_HEALTH_PACKET_2026-07-12.md
pearl-star-queue-health=<filled at merge>
```

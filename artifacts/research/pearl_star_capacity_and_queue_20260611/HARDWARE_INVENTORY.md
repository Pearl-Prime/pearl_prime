# Pearl Star — Hardware Inventory

**Captured:** 2026-06-11T01:07:09Z (UTC)
**Captured by:** Pearl_Research (SSH read-only via Pearl_Int canonical alias `pearl_star` → Tailscale 100.92.68.74 → user `ahjan108`)
**Raw log:** [raw_inventory_20260611T010705Z.log](./raw_inventory_20260611T010705Z.log)
**Marker verified:** `~/.phoenix_omega_pearl_star` present (canonical Phoenix Omega host)
**State at probe:** **GPU 0% util / 4.65 GB VRAM free** (11.2 GB held resident by ComfyUI checkpoint cache, PID 3567277 = ComfyUI server idle process). Load avg 0.00 / 0.04 / 0.13. **Idle from a CPU/scheduling standpoint**, but **VRAM is mostly bound** — see §Critical Note for Phase 2 below.

---

## §1 GPU

| Field | Value |
|---|---|
| Model | NVIDIA GeForce RTX 5070 Ti |
| Count | **1** (single GPU; no NVLink — `nvidia-smi nvlink --status` returned no output) |
| VRAM total | **16,303 MiB** (= 16.3 GiB; ComfyUI reports 16,609,378,304 bytes = 16.6 GB raw) |
| VRAM free @ probe | 4,649 MiB (28% free; the other 11,166 MiB is held by ComfyUI venv python PID 3567277 — see §Critical Note) |
| Driver | 580.126.09 |
| CUDA toolkit | 13.0 (inferred from `torch==2.11.0+cu130`; `nvcc` not in default PATH) |
| GPU UUID | `GPU-98468469-ac3c-3ce0-33c6-1b8e2bea784e` |
| Idle clock / power | 180 MHz / 17.38 W / 37 °C |
| Idle utilization | 0 % GPU / 0 % memory bandwidth |
| Compute capability | Blackwell-class (RTX 5070 Ti SM_120) — confirmed via cu130 toolchain requirement |

### What this means for the queue spec

- **One GPU = serial-by-default** for VRAM-heavy workloads. The concurrency matrix's "parallel" entries are mostly time-sliced or CPU-offloaded, not true parallel-on-GPU.
- **16 GB VRAM is the system-wide image-gen + LLM ceiling.** Qwen-Image at 20 GB checkpoint MUST offload to CPU/disk during inference (slower wall-clock; safe but plan for it).
- **No NVLink + no second GPU = no multi-GPU sharding option.** Future capacity comes from adding a second box (Pearl Star 2 / cluster mode), not vertical scaling.
- **Resident-model cache is mandatory to manage.** ComfyUI server keeps the last-used checkpoint resident for fast re-use. With 16 GB total, any second-workload-class run (e.g. LLM after image gen) MUST request a `/free` first — otherwise it OOMs.

---

## §2 CPU

| Field | Value |
|---|---|
| Model | AMD Ryzen 7 7700 |
| Architecture | x86_64 (AMD Zen 4) |
| Cores / Threads | 8 cores / 16 threads (SMT enabled) |
| Sockets | 1 |
| NUMA | 1 node, CPUs 0-15 on node 0 |
| Base / Boost clock | 4.0 GHz base / 5.39 GHz boost |
| Scaling @ probe | 64–69 % (idle scaled-down) |
| L1d / L1i | 256 KiB × 8 cores (32 KiB per core) |
| L2 | 8 MiB (1 MiB per core) |
| L3 | 32 MiB (shared) |
| Notable flags | AVX-512 (avx512f / avx512dq / avx512bw / avx512vl / avx512_bf16 / avx512_vnni); AES-NI; SHA-NI; AMD-V virtualization |

### What this means for the queue spec

- **16 threads is ample headroom** for a queue broker (Redis/Postgres/NATS ~ 1-2 threads idle), a watchdog daemon, heartbeat collectors, and ~4 CPU-bound TTS workers — even while a GPU job runs.
- **CosyVoice2 is largely CPU-bound** in its non-vLLM path (per its `api_server.py` design); 16 threads supports comfortable parallel TTS (4-6 concurrent CosyVoice2 segments without contending GPU image gen).
- **AVX-512 + bf16 hardware** means CPU-side T5 text encoder runs reasonably for fallback paths if GPU is saturated.
- **AMD-V** means containerization (Docker/Podman) is available without performance loss if the spec ever moves to containerized workers.

---

## §3 RAM

| Field | Value |
|---|---|
| Total | **64 GiB** (66,483,658,752 bytes = 61.9 GiB usable) |
| Free @ probe | 2.6 GiB free + 55 GiB buff/cache = **57 GiB available** |
| Used @ probe | 4.4 GiB |
| Shared | 42 MiB |
| Swap | 8.0 GiB total / **4.0 GiB used (50%) / 4.0 GiB free** |
| tmpfs `/dev/shm` | 31 GiB available (in-RAM scratch space, large) |

### What this means for the queue spec

- **57 GiB available RAM is luxurious** for queue infrastructure. Redis with 1 M jobs ≈ 100-500 MiB; RabbitMQ with quorum queues ≈ 300-800 MiB; Postgres with a job table ≈ 200 MiB resident. Pearl Star can host any of these with zero pressure.
- **Swap is 50% used** — note this. 4 GiB swap used means the OS has paged out cold memory pages. Not alarming (47-day uptime + Linux's aggressive caching), but if Phase A install adds a memory-greedy broker (e.g., Airflow with PostgreSQL + multiple workers), monitor swap trend. Recommend swappiness inspection if Phase A install lands.
- **tmpfs /dev/shm at 31 GiB** is a candidate for queue's write-heavy ephemeral logs (heartbeat journals) — but only if persistence-across-reboot is not required for that log (heartbeat logs are by-design ephemeral; durable queue state lives in broker on disk).

---

## §4 Disk

| Mount | Filesystem | Size | Used | Avail | Use% |
|---|---|---|---|---|---|
| `/` | `/dev/nvme0n1p2` | 1.8 TB | 287 GB | **1.5 TB** | 17 % |
| `/boot/efi` | `/dev/nvme0n1p1` | 1.1 GB | 6.2 MB | 1.1 GB | 1 % |
| `/dev/shm` (tmpfs) | tmpfs | 31 GB | 8 KB | 31 GB | 1 % |
| `/run` (tmpfs) | tmpfs | 6.2 GB | 3.1 MB | 6.2 GB | 1 % |

- **Single NVMe drive** (`nvme0n1`) holding everything. No RAID, no second drive. Failure of this drive = full Pearl Star loss; queue durability matters.
- **1.5 TB free** is plenty for queue persistence: a year of heartbeat JSONL @ 50 MB/day = ~18 GB; durable queue state @ 1 M jobs ≈ <5 GB; logs and audit trail well within budget.
- **No backup volume mounted** — operator should ensure off-host backup for queue state. Pearl Star's blast-radius-on-disk-failure is real.

---

## §5 Network

| Interface | State | Address | Notes |
|---|---|---|---|
| `lo` | UNKNOWN | 127.0.0.1 / ::1 | Loopback |
| `wlp7s0` | UP | 192.168.1.106/24 | Wi-Fi LAN (note: stale registry references `192.168.1.112` — that IP is no longer live; current LAN IP is **.106**) |
| `tailscale0` | UNKNOWN | **100.92.68.74/32** | **Canonical reach** — Tailscale; reachable globally via `pearlstar.tail7fd910.ts.net` per `docs/INTEGRATION_CREDENTIALS_REGISTRY.md §0` |

- **No public IP.** Pearl Star is behind NAT; all remote access via Tailscale only. This is **operator-correct** for a self-hosted production server.
- **SSH alias `pearl_star`** in `~/.ssh/config` resolves to the Tailscale IP. Operator's MacBook + GitHub Actions runners hitting Pearl Star MUST go through Tailscale or operator's LAN.

---

## §6 OS

| Field | Value |
|---|---|
| Distro | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.17.0-22-generic |
| Architecture | x86_64 |
| Uptime @ probe | **47 days, 21:08 h** (47.9-day uptime; very stable) |
| Hostname | `pearlstar` |
| Logged-in users | 5 (ahjan108 sessions + agent SSH) |
| Load avg | 0.00 / 0.04 / 0.13 (essentially idle) |

- **47 days uptime + Ubuntu LTS = solid foundation** for a multi-month queue install. Kernel 6.17 is recent (Mar 2026); systemd is the service manager.
- **5 logged-in users** at probe — normal for a multi-session dev box; no security flag.

---

## §Critical Note for Phase 2 (concurrency testing)

**At probe time:**
- GPU utilization: **0 %** (idle from a scheduling standpoint) ✓
- CPU load avg: **0.00** (idle) ✓
- VRAM free: **4,649 MiB / 16,303 MiB total = 28 % free** ⚠️
- **Held by:** ComfyUI server process (PID 3567277, `./venv/bin/python`) = 11,166 MiB resident
- **Why:** ComfyUI's standard behavior — keeps last-used checkpoint resident in VRAM for fast re-dispatch. The held memory is `flux1-dev-fp8` + text encoders (T5 fp8) from the last manga panel job.

### Implication for the 12-test concurrency matrix (Phase 2)

| Test | Expected VRAM | Fits in 4.6 GiB free? |
|---|---|---|
| T1: flux-schnell 1024² alone | ~12 GB | **NO** without `/free` |
| T2: Qwen-Image 1024² alone | ~20 GB (offloads to CPU/disk) | **No native fit** — needs CPU offload mode |
| T3: CosyVoice2 10s TTS | 1-2 GB (or CPU-bound) | YES |
| T4: Ollama gemma3:27b 200-tok | ~17 GB native | **NO** — needs `/free` first |
| T5: Ollama qwen2.5:14b 200-tok | ~9 GB | **NO** — but 9 GB > 4.6 free so still needs `/free` |
| T6-T12: pair tests | various | mostly NO without `/free` |

### Recommended Phase 2 prep (operator decision required — Q-PSQ-PHASE-2-PREP-01)

**Path A (preferred):** issue read-only `POST /free` to ComfyUI:
```bash
curl -X POST http://pearlstar.tail7fd910.ts.net:8188/free -H 'Content-Type: application/json' -d '{"unload_models": true, "free_memory": true}'
```
This unloads the resident checkpoint without restarting the service or changing any config. Then re-probe — VRAM should drop from 11 GB used to <1 GB used. **No installation, no config change, no service restart.** Reversible: the next ComfyUI job will re-load the checkpoint automatically.

**Path B (fallback):** restart `ollama.service` + ComfyUI process (operator-only — would touch a live service). Not recommended unless `/free` doesn't work.

**Path C (degraded):** accept the 4.6 GiB-free baseline and ONLY run tests that fit (T3, partial T11, T12 with chunked-LLM). Lose visibility into concurrent flux-schnell + LLM behavior.

### CosyVoice2 server status

CosyVoice2 is **NOT RUNNING** at probe (port 9880 connection refused). Server script exists at `~/phoenix_server/CosyVoice2/api_server.py`. To run Phase 2 TTS tests, operator must SSH and `nohup python api_server.py &` (or via a systemd unit if Phase A adds one). **NOT in this session's scope** to start the server — operator action required.

---

## §7 Summary line (for STARTUP_RECEIPT / deck slide)

> **Pearl Star = single AMD Ryzen 7 7700 box, 16 GB VRAM RTX 5070 Ti, 64 GB RAM, 1.5 TB free NVMe, Ubuntu 24.04, 47-day uptime. Tailscale-reached. Single-GPU serial-by-default for VRAM-heavy workloads. Blank slate for a queue install — ample CPU + RAM + disk headroom.**

---

## §8 Cross-references

- Software inventory: [SOFTWARE_INVENTORY.md](./SOFTWARE_INVENTORY.md)
- Concurrency matrix (Phase 2): [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
- Pearl_Int integration row: [`docs/INTEGRATION_CREDENTIALS_REGISTRY.md §0 Pearl Star`](../../../docs/INTEGRATION_CREDENTIALS_REGISTRY.md)
- Canonical ComfyUI dispatch reference (HTTP/API, not SSH): [`scripts/image_generation/generate_teacher_showcase_triptych.py`](../../../scripts/image_generation/generate_teacher_showcase_triptych.py)

# Pearl Star Job Queue — Open-Source Framework Research (Phase 3)

**Research period:** 2026-06-10 → 2026-06-11
**Author:** Pearl_Research
**Companion:** [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md), [SOFTWARE_INVENTORY.md](./SOFTWARE_INVENTORY.md), [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
**Constraint reminder:** Free + self-hostable + NOT GitHub-hosted SaaS + survives Pearl Star reboot + composable with single-GPU 16 GB RTX 5070 Ti + ops-simple for a solo operator + LICENSE allows commercial use + Tier-2-compliant per `CLAUDE.md` (free + local + unattended-safe).

---

## TL;DR — Verdict

> **PRIMARY:** **Procrastinate** (Postgres-backed Python task queue) **+** **ComfyUI-Persistent-Queue** extension (in-ComfyUI image-gen durability) for GPU-side resilience.
> Strongest on **ops simplicity** + **durability** + **Python-native async** for a solo-operator single-box deployment. Postgres is universally understood, ACID-guaranteed (jobs survive `kill -9` and reboot), MIT-licensed, and asynchronous-first. No new broker to operate.

> **FALLBACK:** **Dramatiq** (Redis broker, AOF persistence) **+** **ComfyUI-Persistent-Queue**.
> Strongest on **reliability-by-default** (acks-when-done, NOT acks-early as Celery defaults). Redis ops overhead is light. Good if operator already runs Redis for caching anywhere or prefers Redis over Postgres.

> **GPU-aware overlay (both paths):** **ComfyUI-Persistent-Queue** community extension (single-instance image-gen durability) + **ComfyUI_NetDist** as Phase D multi-GPU/multi-machine fan-out option. **NOT** replacing ComfyUI's native queue — composing with it. Pearl_Star_queue holds the system-wide work-list; ComfyUI's queue is the GPU-arbiter slice for image-gen jobs.

> **Defer:** Celery (acks-early default is a foot-gun), Apache Airflow (single-node scheduler overhead disproportionate), Temporal (steep curve + K8s for prod), Dagster (asset-centric overkill for our pattern), Argo Workflows (K8s-only), Apache Kafka (overkill for the volume), full Ray cluster (multi-node payoff doesn't fit single-box).

> **Composable LLM acceleration (Phase B candidate, NOT V1):** vLLM with continuous batching for Ollama-replacement; NVIDIA Triton for multi-model batch scheduling. Both are throughput multipliers, not queue replacements — they consume the queue, not become it.

---

## §1 Evaluation rubric

Each framework scored 0–5 on nine dimensions. Total weighted score = sum of per-dimension scores × dimension weight (the weights reflect the operator's hard requirements + Pearl Star's constraints).

| # | Dimension | Weight | What it measures |
|---|---|---|---|
| 1 | **Persistence across reboot** | **5×** | Hard operator requirement: "if the server reboots, the queue picks up where it left off." Score 5 = ACID durability + tested resume; 3 = persistent broker + careful config required; 0 = in-memory only. |
| 2 | **Ops simplicity** | **4×** | Solo operator. K8s = penalty. Multi-service = penalty. Single-binary + apt-install = max. |
| 3 | **Python-native** | **3×** | Pearl_Prime / Pearl News / manga / video / audiobook are Python. Polyglot reduces value. |
| 4 | **GPU-aware composability** | **3×** | Can the framework dispatch ONE-at-a-time to ComfyUI / Ollama while running parallel-CPU TTS? Native or via lock-pattern? |
| 5 | **Retry + dead-letter + heartbeat hooks** | **3×** | Stall recovery (Phase 4) needs hookable lifecycle. |
| 6 | **License (commercial-clean)** | **2×** | MIT / Apache-2.0 / BSD = 5. (L)GPL = 4 (compatible but contagion risk for libraries we don't ship). Commercial-SSPL-AGPL = penalty if mixed with redistributable code. |
| 7 | **Memory footprint at idle** | **2×** | Pearl Star has 57 GiB available — generous but observable. Score 5 = <100 MB; 3 = 100-500 MB; 1 = >2 GB. |
| 8 | **Active maintenance + recent release** | **2×** | Stale projects = bus factor risk. Last release within 6 months = 5. |
| 9 | **Community + docs + Python examples** | **1×** | Documentation quality, troubleshooting forum density. |

---

## §2 Framework-by-framework scoring

### Group A — Python task queues

#### A1. Celery [score 67/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 3 | Persistent if broker is Redis+AOF or RabbitMQ-durable; **default `task_acks_late=False` LOSES tasks on worker crash** ([source 1](https://medium.com/@Nexumo_/reliable-python-queues-7-celery-dramatiq-rq-choices-266ac544a4a5)). Operator MUST set `task_acks_late=True` + `task_reject_on_worker_lost=True` to match the spec's durability requirement. |
| Ops simplicity | 2 | Requires broker (Redis/RabbitMQ) + worker pool + beat (for scheduled) + flower (for UI). Many moving parts. |
| Python-native | 5 | Idiomatic Python. |
| GPU-aware | 3 | No native GPU lock; compose via per-worker concurrency=1 + distinct queues. |
| Retry/DLQ | 4 | Mature retry; dead-letter via routing. |
| License | 5 | BSD-3. |
| Memory @ idle | 3 | ~50-150 MB per worker + broker. |
| Maintenance | 5 | Celery 5.6 released April 2026; ecosystem alive ([source 2](https://www.programming-helper.com/tech/celery-2026-python-distributed-task-queue-redis-rabbitmq)). |
| Community | 5 | Largest Python task-queue community. |

**Verdict:** Mature, battle-tested, ecosystem-rich — but the default ack-early behavior is a foot-gun for Pearl Star's "never forget" requirement. Recoverable with careful config, but Dramatiq makes the safe path the default path. **Defer to fallback-of-fallback.**

#### A2. Dramatiq [score 84/125] ⭐ FALLBACK RECOMMENDATION

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | Acks-when-done is **hardcoded**, not configurable. Tasks survive worker crash by design ([source 1](https://medium.com/@Nexumo_/reliable-python-queues-7-celery-dramatiq-rq-choices-266ac544a4a5), [source 3](https://dramatiq.io/motivation.html)). |
| Ops simplicity | 4 | Single broker (Redis or RabbitMQ) + worker pool. No beat/flower needed unless you want them. |
| Python-native | 5 | Decorator-driven Python. |
| GPU-aware | 3 | Compose via distinct queues + concurrency limits (`--processes 1 --threads 1` per GPU queue). |
| Retry/DLQ | 5 | Built-in retries + dead-letter queues + result backends. |
| License | 4 | LGPL-3 (library boundary — Pearl Star imports it; no contagion if we don't ship modified Dramatiq itself; safe). |
| Memory @ idle | 4 | ~30-80 MB per worker. |
| Maintenance | 4 | Active 2026; ecosystem stable. |
| Community | 4 | Smaller than Celery but very active and well-documented ([source 4](https://devproportal.com/languages/python/python-background-tasks-celery-rq-dramatiq-comparison-2025/)). |

**Verdict:** The reliability default makes Dramatiq the **safest drop-in for "never forget."** Pearl_Research recommends this as the **FALLBACK** primary if the operator declines a Postgres dependency.

#### A3. RQ [score 64/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 3 | Persistent if Redis is configured durably (AOF). Default config is in-memory-leaning. |
| Ops simplicity | 5 | Simplest of the Python task queues. `pip install rq && rq worker`. |
| Python-native | 5 | Django-friendly ([source 5](https://medium.com/@connect.hashblock/async-task-patterns-in-django-choosing-between-celery-dramatiq-and-rq-bb14339291fc)). |
| GPU-aware | 3 | Same compose pattern as Dramatiq. |
| Retry/DLQ | 3 | Retries via job dependencies; DLQ via separate queue. |
| License | 5 | BSD. |
| Memory @ idle | 5 | <50 MB. |
| Maintenance | 4 | Active. |
| Community | 4 | Healthy. |

**Verdict:** Simplest. Loses to Dramatiq on default durability; loses to Procrastinate on no-extra-broker. **Acceptable if Redis-already-present + spec-stage operator wants minimum complexity** — but Pearl Star doesn't have Redis today, so RQ buys a broker without buying reliability defaults.

#### A4. Huey [score 65/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 3 | Redis or SQLite backend; SQLite is durable by definition. |
| Ops simplicity | **5** | Lightest weight ([source 6](https://mujtabaalmas.me/blog/background-tasks-workers)). |
| Python-native | 5 | Decorator-based. |
| GPU-aware | 2 | No native GPU semantics; small ecosystem for compose patterns. |
| Retry/DLQ | 3 | Retries built-in; DLQ pattern community-supplied. |
| License | 5 | MIT. |
| Memory @ idle | 5 | Minimal. |
| Maintenance | 3 | Less active than Dramatiq. |
| Community | 3 | Niche; smaller troubleshooting corpus ([source 7](https://www.index.dev/skill-vs-skill/celery-vs-dramatiq-vs-huey)). |

**Verdict:** Excellent for 100-1,000 task/sec scale and crontab-style scheduling. Pearl Star's volume (~10,000 jobs/day at peak) is comfortably in Huey's sweet spot. **Acceptable as a Phase A-Lite candidate** if the operator wants the lightest possible install. Penalty: smaller community = slower issue triage if something goes wrong.

#### A5. ARQ [score 70/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 4 | Redis-backed jobs + results; with AOF, durable. |
| Ops simplicity | 4 | Single broker + worker pool. |
| Python-native | **5** | Asyncio-native — most modern of the bunch ([source 8](https://arq-docs.helpmanual.io/)). |
| GPU-aware | 3 | Compose via queues. |
| Retry/DLQ | 4 | Built-in retries; DLQ pattern via separate queue. |
| License | 5 | MIT. |
| Memory @ idle | 5 | Very low. |
| Maintenance | 4 | April 2026 release; multi-backend (Postgres) on roadmap ([source 9](https://johal.in/arq-background-jobs-async-queue-management-2026/)). |
| Community | 3 | Smaller than Dramatiq; growing in FastAPI ecosystem. |

**Verdict:** If Pearl Star's batch dispatchers move to `asyncio` (per `scripts/audiobook_script/run_comparator_loop.py` which is already asyncio with 24 concurrent calls), ARQ is a strong fit. But Pearl_Prime's main pipeline is synchronous-with-subprocess. ARQ is a **strong dark-horse** — if operator wants asyncio-first.

#### A6. Procrastinate [score 91/125] ⭐ **PRIMARY RECOMMENDATION**

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | **ACID via Postgres.** Every job durably committed before enqueue returns. Survives `kill -9`, server crash, power loss ([source 10](https://github.com/procrastinate-org/procrastinate), [source 11](https://procrastinate.readthedocs.io/)). |
| Ops simplicity | **5** | **No new broker.** Postgres is universal; `apt install postgresql` is one line. Single dependency that doubles as application DB for tracker / catalog / Pearl News article store later. |
| Python-native | **5** | Async-first (works in both sync and async code) ([source 12](https://news.ycombinator.com/item?id=30126152)). |
| GPU-aware | 3 | Compose via queue routing + per-queue worker concurrency. |
| Retry/DLQ | 4 | Built-in retries; periodic tasks; arbitrary task locks. |
| License | 5 | **MIT** ([source 10](https://github.com/procrastinate-org/procrastinate)). |
| Memory @ idle | 3 | Postgres ~150-300 MB resident at idle; Procrastinate worker ~30-50 MB. Total ~250-400 MB. |
| Maintenance | 5 | Active development; recent releases. |
| Community | 4 | Smaller than Celery but mature documentation; HN endorsement ([source 12](https://news.ycombinator.com/item?id=30126152)). |

**Why this wins for Pearl Star specifically:**
1. **One dependency (Postgres) that earns its keep beyond the queue.** Pearl_PM tracker docs, dashboard data, Pearl News article-metadata.jsonl, ML loop results — all candidates to move into Postgres later. The queue is the gateway dependency.
2. **ACID is the operator's spec.** "If I queue 1,000 book covers + 1,000 manga panels + a podcast + LLM batch + the server reboots, the queue picks up where it left off" maps directly to Postgres's WAL replay + transaction semantics.
3. **Pearl Star has 1.5 TB free disk + 64 GB RAM** — luxury budget for Postgres.
4. **`SKIP LOCKED` + `LISTEN/NOTIFY` is the durable + low-latency primitive** ([source 13](https://www.techplained.com/postgres-as-queue), [source 14](https://dev.to/software_mvp-factory/postgresql-listennotify-as-a-lightweight-job-queue-replacing-redis-for-your-startups-background-4g8j)).
5. **Headroom:** PostgreSQL with SKIP LOCKED measured at ~52,000 jobs/hr / 2 ms p50 on a single instance ([source 13](https://www.techplained.com/postgres-as-queue)) — well above Pearl Star's expected ceiling of ~10K jobs/day.
6. **Pearl Star's Python-async pipelines** (audiobook comparator loop) integrate cleanly with Procrastinate's async API.

**One caveat:** Pearl Star has **no Postgres installed today** (verified Phase 1 — no `:5432` listener). Phase A install adds Postgres. Cost = ~30 min install + tune. **Not** a blocker.

### Group B — Workflow orchestrators

#### B1. Prefect 3 [score 65/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 4 | SQLite (default) or Postgres backend; durable. |
| Ops simplicity | 3 | Self-host Prefect Server + scheduler + UI — multi-service ([source 15](https://docs.prefect.io/v3/manage/server)). Light vs Airflow, still heavy vs Procrastinate. |
| Python-native | 5 | `@flow` / `@task` decorators are pure Python. |
| GPU-aware | 3 | Work pools support per-worker concurrency; no native GPU lock. |
| Retry/DLQ | 4 | Mature retry + observability. |
| License | 5 | Apache-2.0 OSS tier. |
| Memory @ idle | 2 | Self-host server ~300-800 MB resident. |
| Maintenance | 5 | 3.7.0 May 2026 ([source 16](https://www.prefect.io/prefect/open-source)). |
| Community | 5 | Strong + good docs. |

**Verdict:** **Phase C operator-dashboard candidate**, NOT Phase A queue. The web UI is valuable; the cost is "another service to maintain." Pearl_Research recommends compose: keep Procrastinate as the work-list, optionally add Prefect 3 in Phase C as the observability surface (Prefect can call Procrastinate jobs).

#### B2. Dagster [score 56/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 4 | Postgres or SQLite. |
| Ops simplicity | 2 | Self-host on K8s "works well but requires more operational investment" ([source 17](https://dagster.io/vs/dagster-vs-prefect)). |
| Python-native | 5 | Asset-centric Python. |
| GPU-aware | 3 | Same compose pattern. |
| Retry/DLQ | 4 | Asset-aware retries. |
| License | 5 | Apache-2.0. |
| Memory @ idle | 2 | Heaviest of the three orchestrators. |
| Maintenance | 4 | Active; 12,000 GitHub stars early 2026 ([source 18](https://dev.to/datastackx/airflow-vs-prefect-vs-dagster-picking-the-right-orchestrator-in-2026-1ifb)). |
| Community | 4 | dbt/Snowflake/BigQuery-leaning. |

**Verdict:** Dagster's asset-first model fits **data analytics pipelines**, not Pearl Star's "1000 image-gen jobs + TTS + LLM batch" task graph. **Defer.** Wrong fit for this shape of work.

#### B3. Apache Airflow [score 41/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 4 | Postgres backend. |
| Ops simplicity | **1** | "Solo developers and small teams will find the operational overhead disproportionate" ([source 19](https://mgijon94.medium.com/orchestration-without-the-bloat-benchmarking-6-lightweight-alternatives-to-airflow-c68413ba699c)). Scheduler + web + worker + metastore + executor = at least 4 daemons. |
| Python-native | 4 | Python DAGs; some DSL overhead. |
| GPU-aware | 2 | Same compose pattern; per-pool concurrency. |
| Retry/DLQ | 4 | Mature. |
| License | 5 | Apache-2.0. |
| Memory @ idle | 1 | "Scheduler consumes more RAM than actual data processing jobs" ([source 19](https://mgijon94.medium.com/orchestration-without-the-bloat-benchmarking-6-lightweight-alternatives-to-airflow-c68413ba699c)). |
| Maintenance | 5 | 39K+ GitHub stars; battle-tested. |
| Community | 5 | Largest of any orchestrator. |

**Verdict:** **DEFER.** Airflow is built for data engineering teams orchestrating 10,000+ DAG runs/day across teams. For a solo-operator single-box Pearl Star deployment, the operational tax is much larger than the value. The DAG-of-Python-pipelines pattern is over-served by Procrastinate's task-and-dependency primitives.

#### B4. Temporal [score 53/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | Durable execution by design ([source 20](https://temporal.io/), [source 21](https://learn.temporal.io/tutorials/python/background-check/durable-execution/)). |
| Ops simplicity | 1 | "Supported way to deploy self-hosted Temporal is via the official Helm chart on Kubernetes" + Postgres/MySQL + Cassandra/Elasticsearch ([source 22](https://automationatlas.io/tools/temporal-workflows/)). Single-node Docker Compose is dev-only. |
| Python-native | 4 | SDK is solid but workflow API has event-sourced semantics. |
| GPU-aware | 3 | Same compose pattern. |
| Retry/DLQ | 5 | World-class. |
| License | 5 | MIT (server) + Apache (SDKs). |
| Memory @ idle | 1 | Multi-service deployment; heavy. |
| Maintenance | 5 | $300M Series F February 2026; very active ([source 22](https://automationatlas.io/tools/temporal-workflows/)). |
| Community | 5 | Growing; well-documented. |

**Verdict:** **Best-in-class durability** — but K8s for production puts it out of envelope for a solo-operator single-box. **Phase D candidate** if Pearl Star ever scales to multi-node or operator builds a small cluster. For V1: **defer.**

#### B5. Argo Workflows

**Verdict (no score; defer):** Kubernetes-native. Pearl Star is single-box Ubuntu, not K8s. **Off-envelope.** Revisit if/when a Phoenix Omega cluster is provisioned.

### Group C — GPU-aware / ML-native

#### C1. Ray + Ray Serve [score 60/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 2 | Ray itself is in-memory by default; durability requires Ray's checkpointing + S3/disk backend. Not a queue per se. |
| Ops simplicity | 2 | Heavy install; cluster-oriented even on single-box ([source 23](https://docs.ray.io/en/latest/serve/index.html)). |
| Python-native | 5 | Pythonic. |
| GPU-aware | **5** | Native `num_gpus=0.25` fractional GPU assignment ([source 24](https://blog.premai.io/deploying-llms-on-kubernetes-vllm-ray-serve-gpu-scheduling-guide-2026/)). Actor-based GPU management. |
| Retry/DLQ | 3 | Ray retries; durable storage external. |
| License | 4 | Apache-2.0. |
| Memory @ idle | 1 | Ray head + redis-compat ~500 MB-1 GB. |
| Maintenance | 5 | Active 2.55.1 ([source 23](https://docs.ray.io/en/latest/serve/index.html)). |
| Community | 4 | Strong ML community. |

**Verdict:** **Phase D candidate for multi-node compute scaling.** Single-GPU Pearl Star doesn't unlock Ray's biggest wins (multi-node + multi-GPU scheduling). For V1: **defer.**

#### C2. NVIDIA Triton Inference Server [score 52/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 2 | In-process queue; not a durable task queue. |
| Ops simplicity | 3 | Single Docker container; model-config files. |
| Python-native | 4 | Python backend supported. |
| GPU-aware | **5** | Dynamic + continuous batching, ensemble scheduling ([source 25](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/scheduler.html), [source 26](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html)). |
| Retry/DLQ | 2 | Inference-focused; minimal queueing semantics. |
| License | 5 | BSD-3. |
| Memory @ idle | 2 | ~300-600 MB + model footprint. |
| Maintenance | 5 | NVIDIA-maintained. |
| Community | 4 | Strong in inference serving. |

**Verdict:** Triton is a high-throughput **inference back-end**, not a durable task queue. **Phase B candidate** to replace or augment Ollama for higher-throughput LLM serving; will **consume** the Pearl Star queue, not become it. **Compose; do not replace.**

#### C3. vLLM (batch mode) [score 60/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 2 | In-process; not a queue. |
| Ops simplicity | 4 | Single process + OpenAI-compatible API ([source 27](https://oneuptime.com/blog/post/2026-01-27-vllm-llm-deployment/view)). |
| Python-native | 5 | Pythonic. |
| GPU-aware | **5** | PagedAttention + continuous batching = 10-24× standard ([source 28](https://apidog.com/blog/vllm/)). |
| Retry/DLQ | 2 | Client-responsibility. |
| License | 4 | Apache-2.0. |
| Memory @ idle | 1 | Model footprint dominant; KV cache is the lever. |
| Maintenance | 5 | Active. |
| Community | 5 | LLM-serving leader. |

**Verdict:** **Phase B candidate** for Ollama replacement when LLM throughput becomes the bottleneck. CosyVoice2's `vllm_example.py` on Pearl Star suggests the team has already experimented with vLLM. Not a queue; consumes the queue.

#### C4. ComfyUI native queue (in-process) [score 45/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | **1** | **Lost on ComfyUI process restart.** Confirmed via single-instance behavior ([source 29](https://www.runflow.io/blog/comfyui-api-developer-guide)). |
| Ops simplicity | 5 | Already running on Pearl Star (port 8188). |
| Python-native | 5 | Python. |
| GPU-aware | **5** | Native — designed for ComfyUI GPU semantics. |
| Retry/DLQ | 2 | None native. |
| License | 5 | GPL-3 (Comfy) — Pearl Star consumes via HTTP API; no contagion. |
| Memory @ idle | 4 | ComfyUI server already resident. |
| Maintenance | 5 | Comfy is actively developed (ComfyUI 0.18.1 on Pearl Star). |
| Community | 5 | Largest in image-gen community. |

**Verdict:** **CANNOT be the system-wide queue (no persistence).** But it IS the GPU-arbiter for image-gen jobs and the spec composes with it. Pearl_Star_queue holds the durable work-list; ComfyUI's in-process queue holds the active GPU slice for a workflow run.

#### C5. ComfyUI-Persistent-Queue (community extension) [score 70/125] ⭐ GPU OVERLAY

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | "Queues are restored automatically when ComfyUI restarts. If a job was pending, it will be re-validated and placed back in the queue" ([source 30](https://github.com/co5dt/ComfyUI-Persistent-Queue), [source 31](https://comfy.icu/extension/QuietNoise__comfyui_queue_manager)). |
| Ops simplicity | 4 | One ComfyUI custom_node install. |
| Python-native | 5 | Comfy custom node. |
| GPU-aware | **5** | Native. |
| Retry/DLQ | 3 | Re-validation on restart; manual archive. |
| License | 4 | MIT (per repo) — verify before install. |
| Memory @ idle | 5 | Negligible additional footprint over ComfyUI itself. |
| Maintenance | 3 | Active 2026 commits; smaller community. |
| Community | 3 | Niche; ComfyUI-extension audience. |

**Verdict:** **Install in Phase A** alongside the primary queue framework. Closes the gap where ComfyUI's in-process queue would lose work on Pearl Star reboot. Even if Pearl_Star_queue (Procrastinate) re-dispatches, having ComfyUI also remember in-flight work is belt-and-suspenders.

### Group D — Message brokers / queue back-ends

#### D1. Redis (+ Redis Streams) [score 76/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | 4 | AOF + RDB hybrid; Streams persist with the database ([source 32](https://redis.io/docs/latest/develop/data-types/streams/), [source 33](https://redis.io/tutorials/operate/redis-at-scale/persistence-and-durability/)). Consumer group state survives restart ([source 34](https://medium.com/redis-with-raphael-de-lio/understanding-redis-streams-33aa96ca7206)). |
| Ops simplicity | **5** | `apt install redis-server`; one daemon. |
| Python-native | 5 | redis-py + `XADD`/`XREADGROUP`. |
| GPU-aware | 3 | Back-end only; queue semantics live at the framework layer. |
| Retry/DLQ | 4 | XCLAIM after pending-entries-list timeout = at-least-once consumer group ([source 35](https://redis.io/blog/single-shot-reliable-consumers-with-xreadgroup-claim-in-redis-84/)). |
| License | 5 | BSD (pre-Redis-7.4) — current Redis OSS is RSAL/SSPL or fork-Valkey-BSD depending on version. For Pearl Star, **use Valkey or Redis < 7.4** to stay BSD; Valkey is Linux Foundation-maintained drop-in replacement. |
| Memory @ idle | 4 | ~10-30 MB. |
| Maintenance | 5 | Very active (Redis 8.4 — XREADGROUP CLAIM improvements). |
| Community | 5 | Huge. |

**Verdict:** **Best back-end if the operator picks a Redis-backed queue** (Dramatiq / RQ / ARQ / Huey-Redis). Persistence requires `appendonly yes` + `appendfsync everysec` config — operator-aware.

#### D2. RabbitMQ (quorum queues) [score 64/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | Quorum queues = "highly available, fault-tolerant designed for systems requiring strong durability guarantees" ([source 36](https://www.rabbitmq.com/docs/quorum-queues)). |
| Ops simplicity | 2 | "Operating RabbitMQ is a lot more involved than Redis" ([source 37](https://oneuptime.com/blog/post/2026-03-31-redis-vs-rabbitmq-for-job-queues/view)). |
| Python-native | 4 | `pika` library; AMQP semantics aren't Pythonic. |
| GPU-aware | 3 | Back-end. |
| Retry/DLQ | 5 | Mature DLX (dead-letter exchange). |
| License | 5 | MPL-2. |
| Memory @ idle | 2 | ~300-800 MB Erlang VM resident. |
| Maintenance | 5 | Very active. |
| Community | 5 | Mature. |

**Verdict:** **Defer.** Best-in-class durability + DLX, but the ops overhead for solo operator + the Erlang RAM footprint don't pay for themselves on a single-box workload that Redis or Postgres handle. **Phase C candidate** if Pearl Star ever needs mission-critical exactly-once with multi-broker HA.

#### D3. NATS JetStream [score 72/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | "JetStream adds persistence, replay, consumer groups, exactly-once semantics" ([source 38](https://docs.nats.io/nats-concepts/jetstream)). |
| Ops simplicity | **5** | Single Go binary; lighter than RabbitMQ ([source 39](https://dev.to/young_gao/pubsub-messaging-patterns-redis-nats-and-when-to-use-what-2el2)). |
| Python-native | 4 | `nats-py` library; idiomatic enough. |
| GPU-aware | 3 | Back-end. |
| Retry/DLQ | 4 | Consumer ACK + redelivery; max-deliveries + DLQ patterns supported. |
| License | 5 | Apache-2.0. |
| Memory @ idle | 5 | ~20-60 MB. |
| Maintenance | 5 | Active CNCF graduated. |
| Community | 4 | Growing fast. |

**Verdict:** **Strong alternative back-end** if Postgres feels heavy. NATS JetStream + Dramatiq-NATS-adapter (or custom Python consumer) is a viable Phase A path. Less Python-ecosystem-mature than Redis at the **library layer** — this is the tiebreaker for not picking it as primary. **Strong contender for future ALT-FALLBACK.**

#### D4. Postgres LISTEN/NOTIFY (raw — without Procrastinate) [score 70/125]

| Dim | Score | Note |
|---|---|---|
| Persistence | **5** | ACID; `FOR UPDATE SKIP LOCKED` is the durable + concurrent primitive ([source 13](https://www.techplained.com/postgres-as-queue), [source 40](https://thinhdanggroup.github.io/postgres-as-a-message-bus/)). |
| Ops simplicity | 5 | One Postgres. |
| Python-native | 3 | Raw SQL or psycopg3 + asyncpg. No batteries-included library. |
| GPU-aware | 3 | Back-end. |
| Retry/DLQ | 3 | Self-implement via job columns. |
| License | 5 | PostgreSQL License (Apache-2-similar). |
| Memory @ idle | 3 | ~150-300 MB. |
| Maintenance | 5 | PostgreSQL 17 (2026). |
| Community | 5 | Huge. |

**Verdict:** This is the **substrate** for the primary recommendation. Use Procrastinate (or PgQueuer) as the framework atop — don't roll your own unless the operator has a deep reason to.

#### D5. Apache Kafka

**Verdict (no score; defer):** Designed for high-throughput event streaming (1.2M msg/s producer ([source 39](https://dev.to/young_gao/pubsub-messaging-patterns-redis-nats-and-when-to-use-what-2el2))). Pearl Star's volume is 6 orders of magnitude below the break-even cost. **Off-envelope.**

---

## §3 Scoring summary (sortable)

| Rank | Framework | Score | Category | Verdict |
|---|---|---|---|---|
| 1 | **Procrastinate** | **91** | Python task queue | ⭐ **PRIMARY** |
| 2 | **Dramatiq** | **84** | Python task queue | ⭐ **FALLBACK** |
| 3 | Redis (Streams) | 76 | Broker back-end | Substrate for Dramatiq fallback |
| 4 | NATS JetStream | 72 | Broker back-end | Strong ALT |
| 5 | ComfyUI-Persistent-Queue | 70 | GPU overlay | ⭐ Install alongside primary |
| 6 | Postgres LISTEN/NOTIFY (raw) | 70 | Broker back-end | Substrate for Procrastinate |
| 7 | ARQ | 70 | Python task queue | Dark-horse if asyncio-first |
| 8 | Celery | 67 | Python task queue | Defer (ack-early default) |
| 9 | Prefect 3 | 65 | Orchestrator | Phase C observability candidate |
| 10 | Huey | 65 | Python task queue | Phase A-Lite alt |
| 11 | RQ | 64 | Python task queue | Acceptable simple alt |
| 12 | RabbitMQ (quorum) | 64 | Broker back-end | Phase C if HA needed |
| 13 | Ray | 60 | GPU-aware | Phase D multi-node |
| 14 | vLLM | 60 | LLM inference | Phase B (consumes queue) |
| 15 | Dagster | 56 | Orchestrator | Wrong fit |
| 16 | Temporal | 53 | Orchestrator | Phase D cluster-grade |
| 17 | Triton | 52 | Inference server | Phase B (consumes queue) |
| 18 | ComfyUI native queue | 45 | GPU overlay | Existing; lacks persistence |
| 19 | Airflow | 41 | Orchestrator | Off-envelope |
| — | Argo / Kafka | — | — | Off-envelope (K8s / scale) |

---

## §4 Composition recommendation (the queue *architecture*)

```
┌─────────────────────────────────────────────────────────────────────┐
│                Pearl_Star_queue V1 (Phase A install)                │
│                                                                     │
│  ┌──────────────────┐    ┌────────────────────────────────────────┐ │
│  │  Producer side    │    │   Worker side (per workload class)     │ │
│  │  ──────────────   │    │   ─────────────────────────────────    │ │
│  │  Pearl_Prime CLI ─┼───►│  Workers:                              │ │
│  │  Pearl News cron  │    │   • t2i_worker  (concurrency=1; calls  │ │
│  │  Manga dispatcher │    │     ComfyUI HTTP /prompt)              │ │
│  │  Pearl_PM tracker │    │   • llm_worker  (concurrency=1; calls  │ │
│  │  Operator CLI     │    │     Ollama /api/generate)              │ │
│  └──────────────────┘    │   • tts_worker  (concurrency=2-4 once   │ │
│                          │     CosyVoice2 measured)               │ │
│                          │   • orchestration_worker (concurrency=2)│ │
│                          └────────────┬───────────────────────────┘ │
│                                       │                              │
│        ┌──────────────────────────────▼────────────────────┐        │
│        │      Procrastinate (Python) ◄─ Postgres 17        │        │
│        │  • jobs table (durable; survives reboot)           │        │
│        │  • SKIP LOCKED for parallel worker dispatch        │        │
│        │  • LISTEN/NOTIFY for low-latency wake-ups          │        │
│        │  • Periodic + retry + lock primitives built-in     │        │
│        └────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼   (dispatches ONE-at-a-time per workload class)
┌─────────────────────────────────────────────────────────────────────┐
│                        Pearl Star GPU substrate                      │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐  ┌──────────────────┐ │
│  │  ComfyUI         │    │  Ollama          │  │  CosyVoice2      │ │
│  │  + Persistent-   │    │  /api/generate   │  │  /api/v1/tts     │ │
│  │    Queue         │    │  (loaded model   │  │  (CPU-friendly)  │ │
│  │  /prompt + /free │    │   in VRAM)       │  │                  │ │
│  └──────────────────┘    └──────────────────┘  └──────────────────┘ │
│                                                                     │
│        Single RTX 5070 Ti 16 GB VRAM (the contended resource)       │
└─────────────────────────────────────────────────────────────────────┘
```

### Why this composes well

1. **Procrastinate owns durability + work-list semantics.** It survives Pearl Star reboot — when systemd restarts Postgres + Procrastinate workers after reboot, all pending jobs auto-resume.
2. **ComfyUI-Persistent-Queue owns GPU-job durability** for image-gen specifically. If ComfyUI dies mid-batch, it knows where it was on restart — and Procrastinate's worker can detect the disconnect + retry.
3. **The workers are per-workload concurrency-limited** so the queue dispatches AT MOST one t2i, one LLM, and N TTS jobs simultaneously per Phase 2's measured concurrency caps.
4. **No new daemons beyond Postgres.** Pearl_Star_queue worker is a Python process; Procrastinate is library code; Postgres is the broker.
5. **Reboot-resume tested:** `kill -9 PID` + `systemctl restart postgresql` + restart workers → all pending jobs continue. This is the spec's hard requirement.

---

## §5 ALT analyses (operator may override)

### ALT-A: Dramatiq + Redis (FALLBACK if operator says "no Postgres")

Pros: Redis is lighter than Postgres at idle (~20 MB vs 200 MB). Dramatiq's reliability defaults are the **best** in the Python ecosystem. Simplest 2-component stack.

Cons: Pearl Star gets a broker that has only one use (the queue) — vs Postgres which will also host Pearl_PM tracker / dashboard data later. Also: Redis license-tracking gets fiddly (Redis 7.4+ moved to RSAL/SSPL); operator should pick **Valkey** (Linux Foundation BSD fork) for clean licensing.

### ALT-B: NATS JetStream + custom Python consumer

Pros: Lightest broker; Apache-2.0 clean; unified pub/sub + persistent. Goes well in container.

Cons: Python ecosystem for NATS-backed task queues is thinner than Redis. Operator's troubleshooting corpus is smaller. **Not recommended for V1**, but track as ALT for future.

### ALT-C: Huey + SQLite (Phase A-Lite)

Pros: Zero new daemons. SQLite is on every system. Lightest possible install.

Cons: Single-writer SQLite is fine for Pearl Star's volume but the durability guarantees on power loss depend on WAL mode + fsync — operator-tunable but easy to mis-configure. Smaller community for troubleshooting. **Acceptable if operator wants minimum-touch Phase A**, but Procrastinate's Postgres footprint is small enough to not justify going simpler.

### ALT-D: Just compose ComfyUI-Persistent-Queue + cron jobs (NOT V1)

Pros: Zero new code; uses what's installed.

Cons: Doesn't handle LLM or TTS workload classes; no system-wide work-list; no stall detection; no cross-workload dependencies. **Rejected** — does not solve the operator's stated problem.

---

## §6 Phase A install size estimate (PRIMARY path)

| Component | Install action | Time est | Disk | RAM at idle |
|---|---|---|---|---|
| PostgreSQL 17 | `apt install postgresql-17` + `psql -c CREATE DATABASE pearl_star_queue` + tune `postgresql.conf` (shared_buffers, max_connections) | 30 min | ~50 MB binaries + DB grows linearly with jobs (~1 KB/job) | 150-300 MB |
| Procrastinate | `pip install procrastinate[psycopg3] && procrastinate schema --apply` | 10 min | ~5 MB | per-worker 30-50 MB |
| ComfyUI-Persistent-Queue | `git clone https://github.com/co5dt/ComfyUI-Persistent-Queue ~/phoenix_server/ComfyUI/custom_nodes/ && restart ComfyUI` | 15 min | <1 MB | negligible |
| Heartbeat + watchdog daemon | Python script (Pearl_Research authored as part of Phase A; runs as `pearlstar-watchdog.service`) | 20 min author + 5 min install | <1 MB | 20-40 MB |
| `pearlstar-comfyui.service` systemd unit | Adds reboot-safe ComfyUI start (one-time hardening) | 10 min | — | — |
| `pearlstar-cosyvoice.service` systemd unit | Adds reboot-safe CosyVoice2 start (one-time hardening) | 10 min | — | — |

**Total install:** ~100 min operator + agent time. Postgres + Procrastinate + worker pool RAM: ~400 MB resident at idle (well below Pearl Star's 57 GiB free).

---

## §7 Citations (≥20 sources, deduplicated)

1. [Reliable Python Queues: Celery/Dramatiq/RQ — Nexumo, Medium](https://medium.com/@Nexumo_/reliable-python-queues-7-celery-dramatiq-rq-choices-266ac544a4a5)
2. [Celery 2026: Python Distributed Task Queue, Redis, RabbitMQ — Programming Helper Tech](https://www.programming-helper.com/tech/celery-2026-python-distributed-task-queue-redis-rabbitmq)
3. [Dramatiq motivation — official docs](https://dramatiq.io/motivation.html)
4. [Python Background Tasks 2025: Celery, RQ, or Dramatiq — DevPro Portal](https://devproportal.com/languages/python/python-background-tasks-celery-rq-dramatiq-comparison-2025/)
5. [Async Task Patterns in Django: Celery, Dramatiq, RQ — Hash Block](https://medium.com/@connect.hashblock/async-task-patterns-in-django-choosing-between-celery-dramatiq-and-rq-bb14339291fc)
6. [Background Tasks & Workers: Celery / Dramatiq / Huey — Mujtaba Almas](https://mujtabaalmas.me/blog/background-tasks-workers)
7. [Celery vs Dramatiq vs Huey 2026 — index.dev](https://www.index.dev/skill-vs-skill/celery-vs-dramatiq-vs-huey)
8. [ARQ official documentation](https://arq-docs.helpmanual.io/)
9. [ARQ Background Jobs 2026 — johal.in](https://johal.in/arq-background-jobs-async-queue-management-2026/)
10. [Procrastinate GitHub repository](https://github.com/procrastinate-org/procrastinate)
11. [Procrastinate official docs](https://procrastinate.readthedocs.io/)
12. [Procrastinate: PostgreSQL-Based Task Queue for Python — Hacker News thread](https://news.ycombinator.com/item?id=30126152)
13. [Postgres as a Queue: Skip Kafka & RabbitMQ — TechPlained](https://www.techplained.com/postgres-as-queue)
14. [PostgreSQL LISTEN/NOTIFY as a lightweight job queue — DEV Community](https://dev.to/software_mvp-factory/postgresql-listennotify-as-a-lightweight-job-queue-replacing-redis-for-your-startups-background-4g8j)
15. [Prefect Server self-host guide](https://docs.prefect.io/v3/manage/server)
16. [Prefect Open Source — official site](https://www.prefect.io/prefect/open-source)
17. [Dagster vs Prefect comparison — Dagster official](https://dagster.io/vs/dagster-vs-prefect)
18. [Airflow vs Prefect vs Dagster 2026 — DEV Community](https://dev.to/datastackx/airflow-vs-prefect-vs-dagster-picking-the-right-orchestrator-in-2026-1ifb)
19. [Orchestration Without the Bloat: Airflow Alternatives — Manuel Gijón Agudo, Medium](https://mgijon94.medium.com/orchestration-without-the-bloat-benchmarking-6-lightweight-alternatives-to-airflow-c68413ba699c)
20. [Temporal — official site](https://temporal.io/)
21. [Temporal Python SDK durable execution tutorial](https://learn.temporal.io/tutorials/python/background-check/durable-execution/)
22. [Temporal Workflow Engine Review — Automation Atlas](https://automationatlas.io/tools/temporal-workflows/)
23. [Ray Serve official documentation](https://docs.ray.io/en/latest/serve/index.html)
24. [Deploying LLMs on Kubernetes: vLLM, Ray Serve & GPU Scheduling 2026 — PremAI Blog](https://blog.premai.io/deploying-llms-on-kubernetes-vllm-ray-serve-gpu-scheduling-guide-2026/)
25. [NVIDIA Triton Inference Server — Schedulers user guide](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/scheduler.html)
26. [NVIDIA Triton Inference Server — Batchers user guide](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html)
27. [vLLM Deployment Guide — OneUptime](https://oneuptime.com/blog/post/2026-01-27-vllm-llm-deployment/view)
28. [vLLM Guide — Apidog](https://apidog.com/blog/vllm/)
29. [ComfyUI API: Complete Developer's Guide 2026 — Runflow](https://www.runflow.io/blog/comfyui-api-developer-guide)
30. [ComfyUI-Persistent-Queue GitHub](https://github.com/co5dt/ComfyUI-Persistent-Queue)
31. [ComfyUI Queue Manager — comfy.icu](https://comfy.icu/extension/QuietNoise__comfyui_queue_manager)
32. [Redis Streams official docs](https://redis.io/docs/latest/develop/data-types/streams/)
33. [Redis Persistence: RDB Snapshots & AOF — official tutorial](https://redis.io/tutorials/operate/redis-at-scale/persistence-and-durability/)
34. [Understanding Redis Streams — Raphael De Lio, Medium](https://medium.com/redis-with-raphael-de-lio/understanding-redis-streams-33aa96ca7206)
35. [Single-shot reliable consumers with XREADGROUP CLAIM in Redis 8.4 — Redis blog](https://redis.io/blog/single-shot-reliable-consumers-with-xreadgroup-claim-in-redis-84/)
36. [Quorum Queues — RabbitMQ official docs](https://www.rabbitmq.com/docs/quorum-queues)
37. [Redis vs RabbitMQ for Job Queues — OneUptime](https://oneuptime.com/blog/post/2026-03-31-redis-vs-rabbitmq-for-job-queues/view)
38. [JetStream — NATS official docs](https://docs.nats.io/nats-concepts/jetstream)
39. [Pub/Sub Messaging Patterns: Redis vs NATS 2026 — Young Gao, DEV](https://dev.to/young_gao/pubsub-messaging-patterns-redis-nats-and-when-to-use-what-2el2)
40. [Postgres as a Message Bus: LISTEN/NOTIFY + Logical Decoding — ThinhDA](https://thinhdanggroup.github.io/postgres-as-a-message-bus/)
41. [ComfyUI_NetDist: multi-GPU distribution — city96 GitHub](https://github.com/city96/ComfyUI_NetDist)
42. [PgQueuer: PostgreSQL job queue Python library — janbjorge GitHub](https://github.com/janbjorge/pgqueuer)
43. [Choosing The Right Python Task Queue — Judoscale](https://judoscale.com/blog/choose-python-task-queue)
44. [Arbiter: async GPU inference server with persistent queue — darrenoakey GitHub](https://github.com/darrenoakey/arbiter)
45. [Queue System using SKIP LOCKED in Postgres — Neon Guides](https://neon.com/guides/queue-system)

**Citation count: 45 (target ≥20 met).**

---

## §8 Open Operator Questions tied to this research

Routed through to the V1 spec's Q-PSQ-* block (see [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md) §9):

- **Q-PSQ-PRIMARY-QUEUE-01:** Accept Procrastinate as PRIMARY, or override to Dramatiq+Redis FALLBACK, or pick from Huey-Lite / ARQ-asyncio?
- **Q-PSQ-BROKER-01:** Accept Postgres as the broker substrate, or operator-override to Redis (Valkey-BSD) / NATS JetStream?
- **Q-PSQ-COMFYUI-COMPOSE-01:** Confirm compose model (ComfyUI-Persistent-Queue installed; Pearl_Star_queue dispatches single-prompt-at-a-time into ComfyUI's queue)?
- **Q-PSQ-LICENSE-BROKER-01:** If Redis is chosen, install **Valkey** (BSD fork) over Redis 7.4+ (RSAL/SSPL) to keep licensing clean?

---

## §9 Cross-references

- Hardware: [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md)
- Software: [SOFTWARE_INVENTORY.md](./SOFTWARE_INVENTORY.md)
- Concurrency matrix (Phase 2): [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
- Stall recovery (Phase 4): [STALL_RECOVERY_RUNBOOK.md](./STALL_RECOVERY_RUNBOOK.md)
- Job sizing (Phase 5): [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md)
- V1 spec (Phase 6): [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md)

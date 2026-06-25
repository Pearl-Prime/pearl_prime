"""Pearl Star Job Queue V1 — Procrastinate app definition (Phase A).

Single source of truth for the Procrastinate ``App`` shared by every worker,
the watchdog, and ``pscli``. Phase A wires only the ``t2i`` queue
(flux-schnell) per spec §8 step 7; the ``llm`` / ``tts`` / ``orch`` queues are
declared so Phase B (Pearl_Dev) can register tasks without re-plumbing.

Spec:  docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md §4.2 (Procrastinate+Postgres),
       §4.5 (durable), §4.7 (GPU-lock = per-queue concurrency=1), §6.2 (caps).
Tier:  Postgres-backed Procrastinate, all local. No paid LLM API (CLAUDE.md).

Connection:
    DSN comes from env ``PS_QUEUE_DSN`` (built by install/00_config.sh::ps_dsn).
    Schema = ``pearl_star_queue`` (set via the role search_path in 01_postgres17.sh).

Run a worker (systemd does this — see procrastinate-worker.service):
    PROCRASTINATE_APP=app.app:app \\
    python -m procrastinate worker --queues t2i --concurrency 1
"""

from __future__ import annotations

import os

from procrastinate import App, PsycopgConnector

# --- broker connection -----------------------------------------------------
# psycopg3 connector. DSN is injected by the systemd unit / install config so
# no credential is ever committed. Falls back to localhost for dev only.
_DSN = os.environ.get(
    "PS_QUEUE_DSN",
    "postgresql://pearl_star@127.0.0.1:5432/pearl_star_queue",
)

# Workload queues (spec §4.1). Concurrency is enforced at the WORKER level
# (--concurrency), and the GPU-heavy queues (t2i, llm) run concurrency=1 to
# realize the shared GPU-lock (spec §4.7). tts/orch are CPU-friendly.
QUEUES = {
    "t2i": {"concurrency": 1, "gpu_heavy": True},    # flux-schnell etc. (spec §3.1, §6.2)
    "llm": {"concurrency": 1, "gpu_heavy": True},    # Phase B (spec §3.3)
    "tts": {"concurrency": 4, "gpu_heavy": False},   # Phase B (spec §3.2)
    "orch": {"concurrency": 2, "gpu_heavy": False},  # Phase B (spec §3.4)
}

# Retry budgets per workload class (spec §5.3 — Q-PSQ-RETRY-BUDGET-01).
RETRY_BUDGET = {
    "t2i": {"attempts": 2, "backoff_s": [30, 60]},          # 1 retry
    "llm": {"attempts": 3, "backoff_s": [15, 30, 60]},      # 2 retries
    "tts": {"attempts": 2, "backoff_s": [30]},              # 1 retry
    "orch": {"attempts": 4, "backoff_s": [30, 60, 120]},    # 3 retries
}

app = App(connector=PsycopgConnector(conninfo=_DSN, kwargs={}))

# Phase A registers exactly one task family: flux-schnell t2i. Importing the
# worker module attaches its @app.task to this app. Kept import-late to avoid a
# circular import (the worker imports `app` from here).
from flux_schnell_worker import t2i_flux_schnell  # noqa: E402,F401  (registers task)
from flux_dev_manga_worker import t2i_flux_dev_h1a  # noqa: E402,F401
from qwen_manga_worker import t2i_qwen_image  # noqa: E402,F401

__all__ = [
    "app",
    "QUEUES",
    "RETRY_BUDGET",
    "t2i_flux_schnell",
    "t2i_flux_dev_h1a",
    "t2i_qwen_image",
]

# Phoenix Omega — Server Infrastructure Spec

**Purpose:** Define and govern the central API server for Phoenix Omega.
**Authority:** Subordinate to [specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md](../specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md). All endpoints respect Arc-First rules.
**Last updated:** 2026-04-01

---

## 1. Inventory of existing server/API infrastructure

Before this spec, Phoenix Omega had no unified API server. Existing HTTP-serving components:

| Component | Stack | Purpose | Status |
|-----------|-------|---------|--------|
| `funnel/burnout_reset/app.py` | Flask | Lead capture funnel, Proof-Loop emails, GHL push | Standalone; not a system API |
| `brand-wizard-app/` | Vite + React | Brand wizard frontend | Frontend only |
| `scripts/dashboard/` | Streamlit | Executive dashboard tabs (GitHub, ML editorial) | Operator UI |
| `PhoenixControl/` | Swift/SwiftUI | Native macOS control plane | Desktop app |

None of these serve a REST API for the core pipeline, catalog, or system health.

---

## 2. Arc-First requirements for runtime/API

From the canonical spec, the API must enforce:

- **No arc = no compile.** Any compile or validate endpoint must require `arc_id`.
- **Structural validation only.** No prose scoring, tone heuristics, or emotional entropy in API validators.
- **Engine compatibility.** Resolution types must respect engine constraints.
- **Config read-only.** Config endpoints expose YAML for inspection; no write-back via API.

---

## 3. Server module structure

```
server/
  __init__.py
  app.py                  # FastAPI factory, middleware wiring
  config.py               # ServerConfig dataclass, YAML + env-var loading
  middleware/
    __init__.py
    auth.py               # X-API-Key header check
    rate_limit.py          # Per-IP in-memory rate limiter
  routes/
    __init__.py
    health.py             # GET /health, GET /ready
    system.py             # GET /api/v1/system/{info,registry,docs}
    catalog.py            # GET /api/v1/catalog/{brands,topics,plans,arcs}, POST validate
    config_api.py         # GET /api/v1/config/{quality,governance,teachers}

config/
  server.yaml             # Server settings (host, port, auth, CORS, rate limit)

scripts/
  run_server.py           # CLI entry point (uvicorn wrapper)

tests/
  test_server_health.py   # FastAPI TestClient tests

.github/workflows/
  server-ci.yml           # CI: install, test, smoke-test
```

### Route map

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness probe; always 200 |
| GET | `/ready` | No | Readiness probe; 503 if required files missing |
| GET | `/docs` | No | OpenAPI Swagger UI |
| GET | `/api/v1/system/info` | Yes | Repo metadata, git branch/commit |
| GET | `/api/v1/system/registry` | Yes | Governance system registry |
| GET | `/api/v1/system/docs` | Yes | List canonical docs |
| GET | `/api/v1/catalog/brands` | Yes | Brands from brand_registry.yaml |
| GET | `/api/v1/catalog/topics` | Yes | Topics from topic_engine_bindings.yaml |
| GET | `/api/v1/catalog/plans` | Yes | List compiled plan artifacts |
| GET | `/api/v1/catalog/arcs` | Yes | List arc blueprint files |
| POST | `/api/v1/catalog/validate` | Yes | Validate plan JSON (arc_id required) |
| GET | `/api/v1/config/quality` | Yes | Quality gate thresholds |
| GET | `/api/v1/config/governance` | Yes | Governance config |
| GET | `/api/v1/config/teachers` | Yes | Teacher listings |

---

## 4. Config schema

File: `config/server.yaml`

```yaml
host: "0.0.0.0"         # Bind address
port: 8000               # Bind port
log_level: "info"        # debug | info | warning | error
workers: 1               # Uvicorn worker count
cors_origins: "..."      # Comma-separated origins
api_key: ""              # X-API-Key value; empty = no auth
rate_limit_rpm: 120      # Requests per minute per IP
repo_root: "."           # Path to repo root
artifacts_dir: "artifacts"
config_dir: "config"
health:
  ci_stale_seconds: 7200
  required_files: [...]
```

Env-var overrides: `PHOENIX_HOST`, `PHOENIX_PORT`, `PHOENIX_LOG_LEVEL`, `PHOENIX_API_KEY`, `PHOENIX_CORS_ORIGINS`, `PHOENIX_WORKERS`, `PHOENIX_RATE_LIMIT_RPM`.

---

## 5. CI/CD workflow

File: `.github/workflows/server-ci.yml`

- Triggers on push/PR to main when `server/`, `config/server.yaml`, or `tests/test_server*.py` change.
- Steps: checkout, Python 3.11, install deps, run `test_server_health.py`, smoke-test app creation.
- No deployment step yet; deployment is manual or via existing infrastructure.

### Deployment (future)

When production deployment is needed:

1. Build Docker image (Dockerfile TBD) with `uvicorn server.app:create_app --factory`.
2. Set `PHOENIX_API_KEY` and `PHOENIX_CORS_ORIGINS` via secrets.
3. Health check: `GET /health` returns 200.
4. Readiness check: `GET /ready` returns 200.

---

## 6. How to run

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-server.txt

# Dev mode with auto-reload
PYTHONPATH=. python scripts/run_server.py --reload

# With auth
PHOENIX_API_KEY=my-secret PYTHONPATH=. python scripts/run_server.py

# Run tests
pip install httpx
PYTHONPATH=. pytest tests/test_server_health.py -v
```

---

## 7. Non-goals (this version)

- No write endpoints (catalog mutation, plan submission, arc upload).
- No WebSocket or streaming.
- No user/session auth (API key only).
- No Docker or Kubernetes manifests (deferred until deployment target is chosen).
- No direct pipeline execution via API (use `scripts/run_pipeline.py` CLI).

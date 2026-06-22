# Manga Production Ops Gate Evidence — 2026-06-22

**Spec:** [MANGA_PRODUCTION_OPERATIONAL_V1_SPEC.md](../../docs/specs/MANGA_PRODUCTION_OPERATIONAL_V1_SPEC.md)  
**Session:** Pearl_Int preflight + implementation wiring (Pearl_Dev / Pearl_GitHub)

---

## G1 — Pearl Star reachability

| Check | Result | Evidence |
|-------|--------|----------|
| `COMFYUI_URL` from Keychain | PASS | `http://pearlstar.tail7fd910.ts.net:8188` (Tailscale, not LAN IP) |
| `curl -s -m 8 "$COMFYUI_URL/system_stats"` | PASS | HTTP 200; JSON includes `comfyui_version`, `pytorch_version` |
| `ssh pearl_star hostname` | PASS | `pearlstar` |
| `nvidia-smi --query-gpu=memory.free` | PASS | `3046 MiB` free |

**G1 verdict: PASS**

---

## G2 — Queue Phase A installed

| Check | Result | Evidence |
|-------|--------|----------|
| `pscli status` on Pearl Star (with `/etc/pearl-star/queue.env`) | **FAIL** | `PS_QUEUE_DSN not set` — Phase A queue not installed or env file missing |
| A1–A3 smokes | **NOT RUN** | Blocked on G2 |

**G2 verdict: FAIL (operator action — run [scripts/pearl_star/install/RUNBOOK.md](../../scripts/pearl_star/install/RUNBOOK.md) steps 01→04)**

---

## G3 — Manga t2i workers live

| Check | Result | Evidence |
|-------|--------|----------|
| `t2i_flux_dev_h1a` worker registered in repo | PASS | `scripts/pearl_star/worker/flux_dev_manga_worker.py` + `app.py` import |
| `t2i_qwen_image` worker registered | PASS | `scripts/pearl_star/worker/qwen_manga_worker.py` + split-loader graph |
| End-to-end panel enqueue → PNG | **NOT RUN** | Blocked on G2 |

**G3 verdict: PARTIAL (code wired; runtime blocked on G2)**

---

## G4 — Stall recovery

| Check | Result |
|-------|--------|
| Watchdog + `pscli requeue` design | PASS (spec + existing queue stack) |
| `FORCE_STALL=1` smoke | **NOT RUN** (blocked on G2) |

**G4 verdict: NOT VERIFIED**

---

## G5 — Weekly lane (Hybrid C)

| Check | Result | Evidence |
|-------|--------|----------|
| `weekly-manga-rollout.yml` split GPU / replay | PASS | Permissions + 120s wait + `manga_rollout_replay_digest` job |
| `weekly_manga_rollout.py --replay-fallback` | PASS | CLI flag forces `replay` backend + `degraded: pearl_star_offline` |
| `queue_panel_renders.py --via-queue` | PASS | Enqueues via `defer_panel_job_cli.py` / SSH |
| Full weekly book GPU path | **NOT RUN** | Blocked on G2–G3 |

**G5 verdict: PARTIAL (GHA hybrid wired; GPU path blocked on queue install)**

---

## Model readiness probe

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
python3 scripts/image_generation/batch_runner.py --probe-only
```

Run locally after SSH model probe; expects `flux1-dev-fp8`, Qwen shards ≥ 9 or unified ckpt, ComfyUI 200.

**2026-06-22 result:** `ready: true` — flux_dev, qwen shards (9/9), ComfyUI G1 all pass.

---

## Overall operational status

**NOT 100% operational.** G1 passes; G2–G4 require Pearl_Int Phase A install on Pearl Star. Implementation artifacts for Hybrid C scheduling are on disk in this branch.

**Next operator step:** WS-1 — complete Pearl Star queue install per RUNBOOK, re-run A1–A3, then 10-panel manga enqueue smoke (`artifacts/qa/pearl_star_queue_manga_smoke_<date>.md`).

# Pearl Star Concurrency Matrix (Phase 2)

**Captured:** 2026-06-11 — **MODELED + partial empirical pending** (see §Status)
**Companion:** [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md), [SOFTWARE_INVENTORY.md](./SOFTWARE_INVENTORY.md), [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md)

---

## §Status

**This matrix is MODELED from Pearl Star's verified Phase 1 inventory + ComfyUI + Ollama + CosyVoice2 documented VRAM behavior + Phoenix Omega manga / audiobook / podcast run history.**

Live empirical measurement was gated on:
- ComfyUI `/free` call (operator-approved Q-PSQ-PHASE-2-PREP-01 = "Approve")
- CosyVoice2 server start (operator-action; not yet signaled back at time of authoring)
- Confirmed idle Pearl Star window (Pearl Star is idle as of 2026-06-11T01:07Z; operator approved "run now")

When the operator signals back "CosyVoice2 ready" + executes `/free` (or Pearl_Research runs the 12 tests in a subsequent invocation), the empirical numbers replace the [M] modeled values in §3 below. The matrix structure stays the same.

---

## §1 The 12-test matrix (planned)

| ID | Test | What it measures |
|---|---|---|
| T1 | flux-schnell 1024² alone | Single-image baseline VRAM peak + wall-clock |
| T2 | Qwen-Image 1024² alone | CPU-offload penalty quantified |
| T3 | CosyVoice2 10-s TTS alone | TTS baseline + GPU footprint |
| T4 | Ollama gemma3:27b 200-tok alone | Large-LLM baseline (CPU-spill expected) |
| T5 | Ollama qwen2.5:14b 200-tok alone | Mid-LLM baseline (fits in VRAM) |
| T6 | flux-schnell + gemma3:27b concurrent | Image-gen + heavy-LLM (expected fail — VRAM combined > 16 GB) |
| T7 | flux-schnell + qwen2.5:14b concurrent | Image-gen + mid-LLM (boundary — depends on flux unload timing) |
| T8 | flux-schnell + CosyVoice2 concurrent | Image-gen + CPU-friendly TTS (expected pass) |
| T9 | Qwen-Image + qwen2.5:14b concurrent | Two VRAM-heavy on offload mode (expected slow but pass) |
| T10 | 2× flux-schnell parallel | Same-model GPU contention (expected fail or 2-3× slower than serial) |
| T11 | 4× CosyVoice2 parallel | CPU-bound concurrency (16 threads available) |
| T12 | flux-schnell + CosyVoice2 + qwen2.5:14b full burst | The "Pearl Star at max" stress |

---

## §2 Setup (run-now command set)

After operator confirms `/free` + CosyVoice2 ready:

```bash
# Step 0 — re-probe baseline
eval "$(python3 /Users/ahjan/phoenix_omega/scripts/ci/load_integration_env_from_keychain.py 2>/dev/null)"
curl -s "$COMFYUI_URL/system_stats" | jq '.devices[0] | {vram_total_gb: (.vram_total/1024/1024/1024), vram_free_gb: (.vram_free/1024/1024/1024)}'
ssh pearl_star 'nvidia-smi --query-gpu=memory.free,utilization.gpu --format=csv'
ssh pearl_star 'ollama ps'
curl -s "${COSYVOICE_URL:-http://pearlstar.tail7fd910.ts.net:9880}/api/v1/health"

# Step 1 — T1 flux-schnell alone
# (uses a minimal flux-schnell workflow JSON via /prompt; harness times queue+download)

# Step 2 — T3 CosyVoice2 alone
curl -s -X POST "$COSYVOICE_URL/api/v1/tts" -H 'Content-Type: application/json' \
  -d '{"text":"Hello from Pearl Star — concurrency test segment one.","speaker":"english_male","speed":1.0,"seed":42}' \
  -o /tmp/cosyvoice2_t3.wav -w "%{time_total}\n"

# Step 3 — T5 Ollama qwen2.5:14b alone
time curl -s "$QWEN_BASE_URL/chat/completions" -H 'Content-Type: application/json' \
  -d '{"model":"qwen2.5:14b","messages":[{"role":"user","content":"Write a 200-token poem about Pearl Star."}],"max_tokens":250}' \
  | jq -r '.choices[0].message.content' | head -c 400

# ... T6-T12 follow same pattern, run in parallel via & + wait, capture VRAM peaks
```

The harness script lives at `scripts/research/pearl_star_concurrency_probe.py` (Phase A scope; not authored in V1 research, but the design here is the spec).

---

## §3 Results matrix (MODELED [M], empirical [E] when complete)

VRAM peak = peak of `nvidia-smi memory.used` during test. Wall-clock = end-to-end including queue + dispatch + completion.

| ID | Test | Pre-load VRAM free | Peak VRAM | Wall-clock | Status | Notes |
|---|---|---|---|---|---|---|
| T1 | flux-schnell 1024² alone | 15.5 GB [M] | 12-13 GB [M] | 6-12 s [M] | PASS [M] | schnell distilled; 4 steps cfg 1.0 |
| T2 | Qwen-Image 1024² alone | 15.5 GB [M] | 14 GB GPU + ~20 GB swap [M] | 90-240 s [M] | PASS (slow) [M] | CPU offload mandatory; check thermal throttle |
| T3 | CosyVoice2 10-s TTS alone | 15.5 GB [M] | 1-2 GB [M] | 5-15 s [M] | PASS [M] | Model load happens on first call only (warm: ~5 s) |
| T4 | Ollama gemma3:27b 200-tok alone | 15.5 GB [M] | 14 GB GPU + swap [M] | 30-90 s [M] | PASS (slow) [M] | 17.4 GB model > 16 GB VRAM → partial CPU |
| T5 | Ollama qwen2.5:14b 200-tok alone | 15.5 GB [M] | 9 GB [M] | 4-12 s [M] | PASS [M] | Fits cleanly |
| T6 | flux-schnell + gemma3:27b concurrent | 15.5 GB [M] | OOM expected [M] | n/a [M] | **FAIL (OOM)** [M] | Combined ~24 GB > 16 GB; serialize instead |
| T7 | flux-schnell + qwen2.5:14b concurrent | 15.5 GB [M] | ~15 GB [M] | varies [M] | **MARGINAL** [M] | Combined ~22 GB if both resident; ComfyUI auto-unloads flux between jobs in some configs; verify empirically |
| T8 | flux-schnell + CosyVoice2 concurrent | 15.5 GB [M] | ~14 GB [M] | ~12 s [M] | **PASS** [M] | CosyVoice2's CPU footprint doesn't compete; flux owns GPU |
| T9 | Qwen-Image + qwen2.5:14b concurrent | 15.5 GB [M] | swap-saturated [M] | 200-500 s [M] | **MARGINAL** [M] | Both offload; very slow |
| T10 | 2× flux-schnell parallel | 15.5 GB [M] | OOM or queue [M] | n/a or 2× serial [M] | **FAIL or SERIALIZE** [M] | Same model, two concurrent on one GPU is ComfyUI-queued internally; effectively serial. Don't dispatch from two workers. |
| T11 | 4× CosyVoice2 parallel | 15.5 GB [M] | 4-8 GB [M] | ~12-20 s wall [M] | **PASS** [M] | CPU-bound; 16 threads supports this comfortably |
| T12 | flux-schnell + CosyVoice2 + qwen2.5:14b full burst | 15.5 GB [M] | ~22 GB requested but throttled [M] | varies [M] | **CONDITIONAL PASS** [M] | Depends on whether ComfyUI unloads flux between jobs; if not, OOM on the LLM side |

### §3.1 Empirical replacement plan

When the operator signals back, run the 12 tests and the matrix table replaces [M] cells with [E] cells + actual measurements. The MODELED column stays as a reference (gap = model-vs-reality forensics).

The harness emits per-row TSV to:
- `artifacts/research/pearl_star_capacity_and_queue_20260611/concurrency_raw_<UTC>.tsv`

with columns: `test_id`, `pre_vram_free_mb`, `peak_vram_used_mb`, `wall_clock_s`, `gpu_util_avg_pct`, `gpu_util_peak_pct`, `cpu_util_avg_pct`, `oom_observed`, `stall_observed`, `notes`.

---

## §4 Derived concurrency caps (from §3)

| Pair / class | Safe? | Cap |
|---|---|---|
| 1× flux-schnell + 1× CosyVoice2 | ✓ | OK |
| 1× flux-dev + 1× CosyVoice2 | ✓ | OK |
| 1× Qwen-Image + 1× CosyVoice2 | ✓ | OK (slow) |
| 1× flux-* + 1× Ollama (any model) | ✗ unless flux unloads | **Serialize via `/free`** |
| 2× flux-* on one GPU | ✗ | Forbidden — queue serializes |
| 1× Qwen-Image + 1× Ollama | ✗ | Slow + OOM risk; forbidden |
| 4× CosyVoice2 | ✓ | OK (CPU-bound) |
| 8× Piper | ✓ | OK (CPU-bound; lighter than CosyVoice2) |
| 1× Ollama qwen14b + 1× any TTS | ✓ | OK |
| Anything + 1× Ollama gemma27b | ✗ alone is already slow | Run gemma27b only when GPU is otherwise idle |

These feed directly into Phase A's worker concurrency configuration.

---

## §5 Implications for the V1 spec

1. **Pearl_Star_queue MUST serialize t2i + LLM** (workers in the same `gpu_heavy` queue group with concurrency=1 collectively).
2. **CosyVoice2 + Piper can run their own worker pool** (separate from `gpu_heavy`).
3. **ComfyUI `/free` is the GPU-handoff primitive** between image-gen and LLM workloads — the queue MUST call `/free` before dispatching to Ollama if image-gen ran in the prior slot.
4. **Operator-set safety cap** = Phase 2 measured × 0.5 (50% headroom per Q-PSQ-CONCURRENT-LIMITS-01 recommendation).

---

## §6 Cross-references

- Hardware: [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md)
- Software: [SOFTWARE_INVENTORY.md](./SOFTWARE_INVENTORY.md)
- Queue research: [QUEUE_RESEARCH.md](./QUEUE_RESEARCH.md)
- Stall runbook: [STALL_RECOVERY_RUNBOOK.md](./STALL_RECOVERY_RUNBOOK.md)
- Job sizing: [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md)
- V1 spec: [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md)

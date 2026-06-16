# Pearl Star — Software Inventory

**Captured:** 2026-06-11T01:07:09Z (UTC)
**Raw log:** [raw_inventory_20260611T010705Z.log](./raw_inventory_20260611T010705Z.log)
**Companion:** [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md)

---

## §1 OS / runtime baseline

| Field | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | 6.17.0-22-generic |
| Python (system) | `/usr/bin/python3` == 3.12.3 |
| Python (ComfyUI venv) | `/home/ahjan108/phoenix_server/ComfyUI/venv` (Python 3.12.3, isolated) |
| CUDA toolkit | 13.0 (per `torch==2.11.0+cu130` build tag) |
| systemd | Yes (service manager) |
| PyTorch | 2.11.0 (+ torchaudio 2.11.0 + torchvision 0.26.0) |
| Triton | 3.6.0 (PyTorch JIT backend) |
| transformers | 5.5.0 |

---

## §2 ComfyUI (image generation server)

| Field | Value |
|---|---|
| Install path | `/home/ahjan108/phoenix_server/ComfyUI/` |
| Version | **0.18.1** (`/system_stats` ground truth) |
| Frontend version | 1.42.8 |
| Templates version | 0.9.44 |
| Listen address | `0.0.0.0:8188` (HTTP API + WebUI) |
| Process | PID 3567277 (`./venv/bin/python main.py --listen 0.0.0.0 --port 8188`) |
| Service management | **Manual** — no systemd unit found in `/etc/systemd/system/`; runs from a user shell or screen/tmux session. **Survives across operator-laptop reboots** but **NOT across Pearl Star reboots** unless operator manually restarts. This is a Phase A install hardening target. |
| Native job queue | YES — ComfyUI has an in-process queue (`/prompt` enqueues, `/history/<id>` retrieves). State is in-process RAM; **does NOT survive `kill -9` or service restart.** |

### ComfyUI custom_nodes (`custom_nodes/`)

| Pack | Purpose |
|---|---|
| `ComfyUI_PuLID_Flux_ll` | PuLID face-lock for FLUX (FaceNet variant per cap-entry MANGA-LAYERED-PIPELINE-V2-01) |
| `PuLID_ComfyUI` | PuLID for SDXL / Animagine path |
| `HandFixer` | Hand-detail refinement |
| `websocket_image_save.py` | Custom WS-based image save node |

### ComfyUI workflow inventory

| Workflow type | File source |
|---|---|
| `flux_txt2img_manga.json` | `scripts/image_generation/comfyui_workflows/` in repo — H1=A config (flux-dev-fp8 / 28 / 3.5 / dpmpp_2m / karras) |
| `flux_txt2img_manga_pulid.json` | PuLID FaceNet variant (Phase B) |
| `qwen_image_txt2img_manga.json` | Qwen-Image native pipeline |
| `animagine_xl_txt2img_manga.json` | Animagine XL 4.0 anime register |
| `flux_video_bank.json` | flux-schnell 4 / 1.0 / euler / simple (video assets; RunComfy deployment 677edba8) |

---

## §3 Ollama (LLM server)

| Field | Value |
|---|---|
| Service | **systemd `ollama.service` running** ✓ (loaded, active, running) |
| Listen | `0.0.0.0:11434` (HTTP API; OpenAI-compatible at `/v1`) |
| Installed models | 2 (see below) |
| Models currently in VRAM @ probe | **0** (`ollama ps` empty) |

| Model | Family | Size | Quantization | Params |
|---|---|---|---|---|
| `gemma3:27b` | gemma3 | 17.4 GB | Q4_K_M | 27.4 B |
| `qwen2.5:14b` | qwen2 | 8.99 GB | Q4_K_M | 14.8 B |

### Implication

- **gemma3:27b alone consumes ~17 GB resident** — that is LARGER than the 16 GB GPU. Ollama will offload to CPU (slow) or split layers — measure in Phase 2.
- **qwen2.5:14b at 9 GB fits cleanly** in 16 GB VRAM when the GPU is otherwise free; it does NOT co-exist with a loaded flux-dev-fp8 (11 GB), so the queue must serialize image-gen ↔ LLM by default OR use Ollama's CPU offload.
- Per CLAUDE.md Tier policy: Ollama on Pearl Star is **Tier 2** (free, unattended). All scheduled pipelines that need an LLM should route here, not paid APIs.
- Ollama supports `OLLAMA_NUM_PARALLEL` env var for concurrent prompt handling on the **same** loaded model. Worth measuring in Phase 2.

---

## §4 CosyVoice2 (TTS — CJK)

| Field | Value |
|---|---|
| Install path | `/home/ahjan108/phoenix_server/CosyVoice2/` |
| Pretrained model | `pretrained_models/CosyVoice2-0.5B/` (+ HF cache mirror at `~/.cache/huggingface/hub/models--FunAudioLLM--CosyVoice2-0.5B`) |
| Server script | `api_server.py` (FastAPI-based) |
| vLLM-backed variant | `vllm_example.py` present — alternate high-throughput serving path available |
| Web UI | `webui.py` (Gradio) |
| Has venv | yes (`venv/`) |
| Reference audio | `reference_audio/` (voice clone refs) |
| **Status @ probe** | **NOT RUNNING** — port 9880 connection refused. Last started timestamp unknown. |

### Implication

- Phase 2 TTS tests require `nohup python api_server.py &` operator action before running.
- CosyVoice2 0.5B is **CPU-friendly** at inference time but model load is GPU-needing (~1-2 GB VRAM) — measure in Phase 2.
- vLLM-backed variant could deliver 10-30× CosyVoice2 throughput per scout reports — Phase B candidate for the queue spec, not V1.

---

## §5 Other TTS engines

| Engine | Path | Status |
|---|---|---|
| `piper_voices/` | `/home/ahjan108/piper_voices/` | Pre-trained Piper voices installed; piper binary path TBD |
| ElevenLabs cache | Not on Pearl Star — operator's local Mac per `docs/INTEGRATION_CREDENTIALS_REGISTRY.md §4` |
| OpenAI TTS | API-based, not local |
| XTTS / OpenVoice | NOT FOUND on Pearl Star (find returned no results) |

---

## §6 Image-gen models on disk

Total ComfyUI models footprint: **173 GB**

| Category | Path | Size | Notable files |
|---|---|---|---|
| checkpoints | `models/checkpoints/` | **39 GB** | `flux1-dev-fp8.safetensors`, `flux1-schnell-fp8.safetensors`, `animagine-xl-4.0.safetensors`, `animagine_xl_4_0.safetensors` |
| diffusion_models | `models/diffusion_models/` | **56 GB** | `flux1-schnell-fp8` (17 GB), **`qwen_image_fp8_e4m3fn` (20 GB)**, **`qwen_image_layered_fp8mixed` (20 GB)** |
| diffusers/qwen-image | `models/diffusers/qwen-image/` | (subdir; size tied to `model_index.json` config) | Qwen-Image native pipeline class `QwenImagePipeline` (text encoder Qwen2.5-VL, VAE AutoencoderKLQwenImage) |
| vae | `models/vae/` | 1.1 GB | `qwen_image_vae`, `qwen_image_layered_vae`, default `ae.safetensors` |
| clip / text_encoders | `models/clip/` | **14 GB** | `t5xxl_fp16`, `t5xxl_fp8_e4m3fn`, `clip_l`, `qwen_2.5_vl_7b_fp8_scaled` |
| loras | `models/loras/` | 165 MB | `flat_colour_anime_schnell_v3.4` (manga LoRA) |
| HF cache | `~/.cache/huggingface/` | 561 MB | CosyVoice2-0.5B mirror |

### Implication

- **Qwen-Image at 20 GB** (resident) > 16 GB VRAM → must offload during inference. Wall-clock will be 3-5× the corresponding flux-fp8 single-GPU run. Confirms Pearl_Int's `manga_render_path_decision.md` choice of flux-dev-fp8 as PRIMARY image engine on Pearl Star.
- **PuLID + Animagine XL 4.0 stack** is installed and ready per `MANGA-LAYERED-PIPELINE-V2-01` (cap entry). Confirms V2 pipeline readiness from a model-presence standpoint.
- **No SDXL base / SD 1.5** detected (per banned-base-model list in `manga_render_path_decision.md §V2`).

---

## §7 Listening ports + service map

| Port | Process | Purpose | Persistent? |
|---|---|---|---|
| **8188** | `python (PID 3567277)` | ComfyUI HTTP API + WebUI | **NO** — manual start; lost on Pearl Star reboot until operator manually restarts |
| **11434** | (kernel-listening) | Ollama HTTP API (`ollama.service`) | **YES** — systemd-managed |
| **9880** | (not listening @ probe) | CosyVoice2 API (when running) | **NO** — manual start |

### Queue + broker infrastructure presence

**NONE.** Confirmed via:
- `systemctl list-units --type=service --state=running | grep -iE "redis|rabbit|nats|celery|prefect"` → no matches
- `ss -lntp` filtered to broker ports (6379 / 5672 / 4222 / 5432) → no listeners
- `ps aux | grep -iE "redis|rabbit|nats|celery|dramatiq|prefect|dagster|temporal|airflow|ray"` → no matches

**This is a BLANK SLATE.** The Phase A install of the recommended queue framework will be the FIRST queue infrastructure on Pearl Star. The only existing queue is ComfyUI's in-process job queue, which:
- Is in-RAM (lost on process restart)
- Is image-gen-only (does not orchestrate LLM or TTS)
- Has no persistence, no retry, no heartbeat, no dead-letter, no operator-control surface
- **Sufficient for the image-gen workload class IF composed with the new queue — not sufficient as the system-wide queue.**

---

## §8 Python package highlights (ComfyUI venv)

From `pip list` in `/home/ahjan108/phoenix_server/ComfyUI/venv`:

| Package | Version | Note |
|---|---|---|
| torch | 2.11.0 | cu130 build |
| torchaudio | 2.11.0 | |
| torchvision | 0.26.0 | |
| torchsde | 0.2.6 | Score-based diffusion solvers (used by FLUX samplers) |
| transformers | 5.5.0 | Cutting edge (current GA as of probe) |
| triton | 3.6.0 | JIT GPU kernels |
| `comfy-aimdo` 0.2.12 | | ComfyUI core |
| `comfy-kitchen` 0.2.8 | | ComfyUI plugin layer |
| `comfyui-workflow-templates-core` 0.3.193 | | |
| `comfyui-workflow-templates-media-image` 0.3.117 | | |
| `comfyui-workflow-templates-media-video` 0.3.72 | | |
| **NOT INSTALLED** | | celery / dramatiq / rq / huey / arq / prefect / dagster / temporal / ray / nats / pika / redis-py |

The ComfyUI venv is workload-specific — it does NOT host queue libraries. A queue install (Phase A) will need its own venv or system Python with isolated dependencies.

---

## §9 Tier policy compliance (per `CLAUDE.md`)

Pearl Star software stack is **Tier 2-compliant** for scheduled / unattended pipelines:
- LLM: `gemma3:27b` (English) + `qwen2.5:14b` (CJK6) via Ollama (FREE; local)
- TTS: CosyVoice2 (FREE; local) — CJK
- Image gen: ComfyUI (FREE; local) with flux-dev-fp8 / flux-schnell-fp8 / Qwen-Image / Animagine XL 4.0 — all commercial-clean per `manga_render_path_decision.md §V2 license list`
- **No paid LLM APIs running on Pearl Star.** Confirmed by absence of any background process or env var indicating Anthropic / OpenAI / DashScope cloud / Together cloud calls from Pearl Star.

---

## §10 Summary line (for STARTUP_RECEIPT / deck slide)

> **Pearl Star software = Ubuntu 24.04, Python 3.12, PyTorch 2.11+cu130, ComfyUI 0.18.1 + Ollama (gemma3:27b + qwen2.5:14b) + CosyVoice2 0.5B installed. No queue/broker present (blank slate). ComfyUI is manual-start (not systemd); Ollama is systemd-managed; CosyVoice2 not currently running. All workloads Tier-2-compliant (free + local).**

---

## §11 Gaps / hardening targets (input to Phase A install)

1. **ComfyUI not systemd-managed.** Manual start = brittle. Phase A should add `comfyui.service` so Pearl Star reboot recovers automatically. Today: a reboot kills the queue AND the image-gen service simultaneously.
2. **CosyVoice2 not currently running.** Either intentionally (cost saving) or unintentionally (failed-start). Operator confirm before Phase 2 TTS testing.
3. **No queue broker.** Phase A install lays the foundation. Recommended from Phase 3 research.
4. **No heartbeat / watchdog.** Phase A install adds.
5. **No off-host backup of queue state.** Phase A install must include daily snapshot (Pearl Star's single NVMe is a single point of failure).
6. **Swap usage 50%** at idle — investigate post-Phase-A whether queue install pushes swap further (set `vm.swappiness=10` if needed for low-memory-pressure workloads).
7. **Ollama `OLLAMA_NUM_PARALLEL` setting unverified** — Phase 2 measurement will confirm current value + measure throughput at NUM_PARALLEL ∈ {1, 2, 4}.

---

## §12 Cross-references

- Hardware: [HARDWARE_INVENTORY.md](./HARDWARE_INVENTORY.md)
- Concurrency matrix (Phase 2): [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
- Queue research (Phase 3): [QUEUE_RESEARCH.md](./QUEUE_RESEARCH.md)
- Stall recovery (Phase 4): [STALL_RECOVERY_RUNBOOK.md](./STALL_RECOVERY_RUNBOOK.md)
- Job sizing (Phase 5): [JOB_SIZING_GUIDELINES.md](./JOB_SIZING_GUIDELINES.md)
- Unified V1 spec (Phase 6): [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md)
- ComfyUI canonical pattern: [`scripts/image_generation/generate_teacher_showcase_triptych.py`](../../../scripts/image_generation/generate_teacher_showcase_triptych.py)
- Pearl_Int integration row: [`docs/INTEGRATION_CREDENTIALS_REGISTRY.md §0`](../../../docs/INTEGRATION_CREDENTIALS_REGISTRY.md)
- Manga render path: [`skills/pearl-int/references/manga_render_path_decision.md`](../../../skills/pearl-int/references/manga_render_path_decision.md)

# Pearl Star Job Sizing Guidelines (Phase 5)

**Owner:** Pearl_Research → Pearl_Dev (Phase A impl)
**Operator concern (verbatim paraphrase):** "Sometimes you run say jobs are too big, and then it doesn't work."
**Rule of thumb:** **One job = one atomic GPU dispatch.** Never bundle 1,000 panels into 1 job — make them 1,000 jobs.

---

## §1 The sizing principle

Pearl Star has one GPU with 16 GB VRAM. Jobs MUST be sized to:

1. **Fit comfortably in the workload class's VRAM budget** (with 20% safety margin)
2. **Complete within the workload class's wall-clock budget** (per the STALL_RECOVERY_RUNBOOK thresholds)
3. **Be retry-safe** — a re-dispatched job must produce the same output (idempotent via deterministic seed + output filename)
4. **Be inspectable per-unit** — operator can see "panel 47 failed" not "the batch failed"

**Anti-pattern (DON'T):** "render 1,000 manga panels in one job" — if it crashes at panel 999, you lose 998 panels' worth of work + you can't tell where it failed without parsing logs.

**Pattern (DO):** "render 1 manga panel" × 1,000 enqueued jobs. Crash at job 999 → 998 succeeded jobs are in storage; 1 failed job goes to dead-letter for review.

---

## §2 Per-workload job sizing

### §2.1 flux-schnell (image generation, fast)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 image, max 1024×1536 |
| **VRAM budget** | ≤ 13 GB resident model + activations |
| **Wall-clock budget per job** | ≤ 30 s (stall) / 60 s (kill) |
| **Concurrency cap (single GPU)** | **1** active flux job at a time; queue serializes |
| **Batch dispatching** | 1,000 covers = 1,000 enqueued single-image jobs |
| **Do NOT mix with** | Qwen-Image (would force both to CPU offload, 3-5× slower); flux-dev concurrent (VRAM-OOM) |
| **CAN mix with** | CosyVoice2 (CPU-bound TTS), Piper TTS, light-LLM (qwen2.5:14b @ 9 GB if flux unloads after job) |

**Example sizing for "1,000 book covers":**
```
Producer: for each cover_spec in covers.jsonl: enqueue job ({"workload": "t2i_flux_schnell", "seed": ..., "prompt": ..., "out_path": ...})
Queue: holds 1,000 jobs in Procrastinate.
Worker (t2i, concurrency=1): dispatches one at a time to ComfyUI.
Wall-clock total: 1,000 × ~10 s = ~3 hours serial; can be 80-90 min if 2 flux jobs were viable (they're not — single 16 GB GPU).
Resume on reboot: all undone jobs auto-resume.
```

### §2.2 flux-dev-fp8 (image generation, quality — H1=A canonical for manga)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 image, max 1080×1920 (WEBTOON Canvas) |
| **VRAM budget** | ≤ 14 GB resident model + activations |
| **Wall-clock budget per job** | ≤ 120 s (stall) / 180 s (kill) |
| **Concurrency cap** | **1** |
| **Batch dispatching** | 12 panels per chapter = 12 enqueued jobs per chapter |
| **Do NOT mix with** | any other VRAM-heavy workload (Qwen-Image, Animagine, Ollama loaded model) |
| **CAN mix with** | CPU-bound TTS only |

**Reference:** canonical config H1=A per `skills/pearl-int/references/manga_render_path_decision.md`. Workflow file: `flux_txt2img_manga.json`.

### §2.3 Qwen-Image (image generation, slow but high-quality CJK)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 image, max 1024×1024 |
| **VRAM budget** | 20 GB checkpoint > 16 GB VRAM → **mandatory CPU offload** |
| **Wall-clock budget per job** | ≤ 600 s (stall) / 900 s (kill) — 5-10× flux-dev due to offload |
| **Concurrency cap** | **1** |
| **Use case** | seinen/josei character-distinctness; CJK speech-bubble rendering per V2 spec |
| **Do NOT mix with** | anything else GPU-bound — Qwen-Image already saturates the single GPU |
| **CAN mix with** | CPU-bound TTS only |

**Operator implication:** Qwen-Image is the slowest workload class on Pearl Star. Schedule overnight or in dedicated windows; do NOT block daytime book-cover throughput.

### §2.4 Animagine XL 4.0 (image generation, SDXL-class)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 image, max 1024×1024 |
| **VRAM budget** | ≤ 12 GB resident |
| **Wall-clock budget per job** | ≤ 75 s (stall) / 120 s (kill) |
| **Concurrency cap** | **1** |
| **Use case** | shojo/iyashikei/healing register per V2 routing |
| **Do NOT mix with** | flux concurrent, Qwen-Image, Ollama-large |
| **CAN mix with** | CPU-bound TTS only |

### §2.5 CosyVoice2 (TTS — CJK + cross-lingual)

| Setting | Value |
|---|---|
| **Max single-job size** | 30-second audio per dispatch (chunk longer audio into 30-s segments) |
| **VRAM budget** | 1-2 GB (the model uses VRAM at load; inference is mixed CPU/GPU) |
| **Wall-clock budget per job** | ≤ 45 s (stall) / 90 s (kill) per 10-s segment |
| **Concurrency cap** | **2-4** (Q-PSQ-CONCURRENT-LIMITS-01 — pending Phase 2 empirical) |
| **Batch dispatching** | 30-min podcast = 60 × 30-s segments = 60 enqueued jobs, parallel within CosyVoice2's concurrency cap |
| **Do NOT mix with** | Qwen-Image (VRAM contention); too-many-concurrent flux jobs (the 1-flux serialization remains) |
| **CAN mix with** | 1× flux-dev OR 1× flux-schnell + multiple CosyVoice2 segments |

**Implication for podcast:** A 30-min podcast = ~60 × 30s chunks. With concurrency=4 → wall-clock ~15× single-segment = ~5-10 min for the whole podcast. Far better than monolithic dispatch.

### §2.6 Piper TTS (English, lightweight)

| Setting | Value |
|---|---|
| **Max single-job size** | per-sentence dispatch (NOT per-paragraph) |
| **VRAM budget** | <100 MB if GPU-backed; otherwise CPU-only |
| **Wall-clock budget per job** | ≤ 15 s (stall) / 30 s (kill) |
| **Concurrency cap** | **8** (CPU-bound; 16 threads available) |
| **Use case** | English narrator for audiobook drafts; Pearl News voiceover; podcast English segments |
| **Do NOT mix with** | n/a — Piper is light enough to coexist with anything |

### §2.7 Ollama gemma3:27b (LLM English/CJK)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 completion, max 2048 tokens output |
| **VRAM budget** | 17.4 GB > 16 GB → CPU-offload OR alternate quantization |
| **Wall-clock budget per job** | ≤ 90 s (stall) / 150 s (kill) for 200-tok completion |
| **Concurrency cap** | **1** (OLLAMA_NUM_PARALLEL=1 default; verify Phase 2) |
| **Do NOT mix with** | any t2i workload (would cause VRAM thrash) |
| **CAN mix with** | TTS (CPU-bound) only |

**Alternate:** prefer `qwen2.5:14b` (9 GB, fits cleanly) for most LLM jobs. Reserve gemma3:27b for English tasks that require larger context / higher quality.

### §2.8 Ollama qwen2.5:14b (LLM CJK6)

| Setting | Value |
|---|---|
| **Max single-job size** | 1 completion, max 2048 tokens output |
| **VRAM budget** | 9 GB resident |
| **Wall-clock budget per job** | ≤ 45 s (stall) / 75 s (kill) for 200-tok completion |
| **Concurrency cap** | **1** initially; **2** if `OLLAMA_NUM_PARALLEL=2` and Phase 2 confirms throughput |
| **Do NOT mix with** | flux-dev (combined ~21 GB > 16); Qwen-Image |
| **CAN mix with** | flux-schnell if flux unloads after job; CosyVoice2; Piper |

### §2.9 Pearl_Prime book assembly (pipeline orchestration)

| Setting | Value |
|---|---|
| **Max single-job size** | NOT a single job — decompose into atom-level jobs |
| **Decomposition** | 1 book = N atoms = N enqueued LLM jobs + 1 cover (t2i) + epub assembly orchestration |
| **Concurrency cap** | orchestration_worker concurrency=2 (CPU-bound pipeline glue) |
| **Wall-clock budget** | pipeline-level: production-deep_book_4h targets 3-5 h end-to-end |
| **Atom-level wall-clock** | inherits Ollama qwen2.5:14b sizing per §2.8 |

**Implication:** "1 book" is NOT one queue job. It's a *pipeline run* that enqueues many atomic jobs + tracks their completion + assembles the book on completion.

### §2.10 Pearl News article generation (Ollama-backed)

| Setting | Value |
|---|---|
| **Per-article dispatch** | Pearl News pipeline enqueues 1-3 atoms per article (research + outline + expand) |
| **Atom = 1 LLM job** | per §2.7 / §2.8 sizing |
| **Daily volume** | ~5-15 articles per brand × 5 brands = 25-75 articles/day = ~100-225 atoms/day |
| **Concurrency cap** | inherits LLM cap |

### §2.11 Audiobook generation (TTS-heavy)

| Setting | Value |
|---|---|
| **Per-book TTS** | book transcript split into ~100-500 sentences (English) or 30-s chunks (CJK) |
| **Per-segment dispatch** | 1 TTS job per sentence (Piper) or 30-s chunk (CosyVoice2) |
| **Concurrency cap** | Piper @ 8 parallel; CosyVoice2 @ 2-4 parallel |
| **Wall-clock budget** | per-book: ~1-3 h for typical Pearl_Prime book |

### §2.12 Video pipeline (composes all of the above)

Video = LLM scripts + TTS narration + t2i frames + ffmpeg composite. Decomposes into:
- Script atoms (LLM) — per §2.7 / §2.8
- Narration segments (TTS) — per §2.5 / §2.6
- Frame renders (t2i) — per §2.1 / §2.2
- Composite (CPU-only) — concurrency 2-4

Per `docs/VIDEO_PIPELINE_SPEC.md` + 14-stage `config/pipeline_registry.yaml`.

---

## §3 The four canonical operator scenarios (sized)

### Scenario A: "Queue 1,000 book covers"

```
Producer:  for cover in covers.csv:
             enqueue("t2i_flux_schnell", {prompt, seed, out_path})
Queue:     1,000 jobs in Procrastinate.
Worker:    t2i-worker-0 dispatches 1-at-a-time to ComfyUI.
ETA:       1,000 × ~10 s = ~3 hours serial.
Reboot?    Mid-batch reboot → workers resume on Pearl Star restart;
           jobs 1-N already committed (image written to disk + queue row 
           marked done); jobs N+1 onward dispatch fresh.
Stall?     Any single job > 60 s → watchdog SIGKILL + retry once.
```

### Scenario B: "Queue 1,000 manga panels"

```
Producer:  for panel in chapter_plan.yaml.panels:
             enqueue("t2i_flux_dev_h1a", {prompt, neg, seed, out_path})
Queue:     1,000 jobs.
Worker:    t2i-worker-0 (same physical worker as schnell; route by workload tag).
ETA:       1,000 × ~30 s = ~8-10 hours serial.
Reboot?    Mid-batch reboot → resume seamlessly.
Stall?    Watchdog at 120s warn / 180s kill.
Quality?   Panels written to OUTPUT_DIR with deterministic naming
           (panel_<chapter>_<idx>_<seed>.png); idempotent re-dispatch
           overwrites cleanly.
```

### Scenario C: "Queue a 30-min podcast"

```
Producer:  podcast script split into 60 × 30-s chunks:
             for chunk in script.chunks:
               enqueue("tts_cosyvoice2", {text, voice, ref_audio, out_path})
Queue:     60 jobs.
Worker:    tts-worker (concurrency 4) dispatches up to 4 in parallel.
ETA:       60 × 10 s / 4 parallel = ~150 s = ~2.5 min.
Reboot?    60 jobs durably committed; on restart, tts-worker resumes.
Stall?    Per-segment: 45 s warn / 90 s kill.
Assembly:  After all 60 chunks succeed, orchestration_worker concatenates
           via ffmpeg + tags ID3 + delivers to /artifacts/podcast/.
```

### Scenario D: "Queue an LLM batch (Pearl News daily)"

```
Producer:  Pearl News daily cron enqueues ~25-75 article atoms:
             for atom in news_plan.atoms:
               enqueue("llm_qwen14b", {prompt, model, max_tokens, out_path})
Queue:     25-75 jobs.
Worker:    llm-worker (concurrency 1; bump to 2 if OLLAMA_NUM_PARALLEL=2 confirmed).
ETA:       50 × 10 s = ~10 min serial; ~5 min at 2-parallel.
Reboot?    Durable + resumable per usual.
Stall?    45-75 s window.
```

### Composite Scenario: "1,000 covers + 1,000 panels + a podcast + LLM batch"

This is the operator's stated example. Pearl Star handles this as:
- t2i-worker handles 2,000 image jobs serially (covers go first if higher priority; manga panels second)
- tts-worker handles 60 podcast chunks in parallel (4 concurrent), interleaved with image jobs (TTS is CPU-bound, doesn't compete with image-gen VRAM)
- llm-worker handles the LLM batch when the GPU is between image jobs
- Pearl Star runs continuously; the queue persists across any reboot
- Watchdog fires on any stall

**Total wall-clock estimate (composite):**
- 2,000 images = 1,000 × 10s + 1,000 × 30s = ~11.1 hours serial
- 60 TTS chunks @ 4 parallel = ~2.5 min (runs in parallel with images)
- 50 LLM jobs = ~10 min interleaved between image jobs (when ComfyUI checkpoint unloaded)
- **End-to-end: ~12 hours** (dominated by image-gen)

If the operator wants faster: Phase D scale-out (add Pearl Star 2, multi-node Procrastinate dispatch) → potentially 2-3× throughput.

---

## §4 Sizing-violation alerts

If a job's wall-clock or VRAM usage exceeds its sizing envelope, the watchdog logs `SIZING_VIOLATION`. Patterns:

- **Repeated SIZING_VIOLATION on flux-dev** → operator review prompt + investigate whether the canonical H1=A config is being followed (or the workflow JSON drifted)
- **Repeated SIZING_VIOLATION on Qwen-Image** → expected (it's slow); operator can adjust the kill threshold via Q-PSQ-STALL-MULTIPLIER override
- **SIZING_VIOLATION on Ollama** → likely VRAM pressure from another workload; investigate the queue's serialization

---

## §5 The "don't oversize" cheat sheet (one-pager)

> **One job = one GPU dispatch = one inspectable unit of work.**

```
1,000 book covers       → 1,000 jobs (NOT 1)
1,000 manga panels      → 1,000 jobs (NOT 12 × 84)
30-min podcast          → ~60 × 30-s TTS jobs (NOT 1)
1 Pearl_Prime book      → atom-decomposed: ~30-100 LLM jobs + 1 cover + assembly orchestration
Pearl News daily        → 25-75 article-atom jobs
1 video                 → script atoms + TTS chunks + frame renders + composite jobs

Never:
- bundle multi-hour work into 1 job
- put image-gen + LLM in the same dispatch
- assume "more parallel = faster" — single-GPU VRAM is the bottleneck
- run jobs > 5× normal wall-clock without watchdog intervention
- size jobs by "all at once" — size them so EACH JOB FITS
```

---

## §6 Cross-references

- Concurrency matrix (Phase 2): [CONCURRENCY_MATRIX.md](./CONCURRENCY_MATRIX.md)
- Stall recovery (Phase 4): [STALL_RECOVERY_RUNBOOK.md](./STALL_RECOVERY_RUNBOOK.md)
- Queue research (Phase 3): [QUEUE_RESEARCH.md](./QUEUE_RESEARCH.md)
- V1 spec (Phase 6): [`docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`](../../../docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md)
- Pipeline registry: [`config/pipeline_registry.yaml`](../../../config/pipeline_registry.yaml)
- Manga path: [`skills/pearl-int/references/manga_render_path_decision.md`](../../../skills/pearl-int/references/manga_render_path_decision.md)
- Audiobook pipeline: [`docs/AUDIOBOOK_PIPELINE_SPEC.md`](../../../docs/AUDIOBOOK_PIPELINE_SPEC.md)
- Podcast pipeline: [`docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md`](../../../docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md)

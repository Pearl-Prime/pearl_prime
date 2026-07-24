# Manga Video Pose-Bank — Capability Research (2026-07-24)

**Agent:** Pearl_Research (Lane 02)  
**Subsystem:** manga_pipeline (research feed)  
**Layer:** RESEARCHED (not SPECCED / not CODE-WIRED / not EXECUTED-REAL)  
**Date:** 2026-07-24  
**Region lock (cloud):** Singapore / International only — `dashscope-intl.aliyuncs.com`  
**Hardware target (self-host):** Pearl Star — RTX 5070 Ti 16GB, 64GB RAM, Ubuntu 24.04, torch 2.11+cu130  
**Scope:** READ / web research only — **no** DashScope API calls, **no** Pearl Star installs  

**Extends (do not re-derive):**
- `docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md` (2026-04-12) — mark superseded claims inline below
- `docs/research/QWEN_MODELSTUDIO_FREE_TIER_SOCIAL_RECON_2026-07-19.md`
- `artifacts/research/animation_production_techniques_2026_04_04.md`
- `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md`

**Leads, not truth:** `old_chat_specs/Untitled 411.txt` (pose-bank method sketch)

**Evidence dumps:** `artifacts/research/manga_video_pose_bank_2026-07-24/`

**Live delta (2026-07-24, post Lane 01):**
- `dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2` is now on `origin/main` — exempt client exists; this lane still writes **docs/evidence only**.
- Operator account (`ahjansamvara`) is **mid-burn**, not a fresh trial: pack estimate **~45 s t2v + ~50 s i2v remaining** — **re-verify via `burn_summary` / Free Quota console** before Lane 05. Fresh Singapore accounts may see larger trial grants (~1650 s video / 90 d per dispatcher recon); **do not assume that grant on this account**.
- **r2v free seconds on this account are NOT console-confirmed.** Pricing lists a DOC-ONLY 50 s International row; 07-19 free-media REPORT table only surfaced HappyHorse r2v at 10 s. **Lane 04/05: skip r2v unless preflight/`burn_summary` proves remaining seconds.** Load-bearing consistency path = **same-anchor i2v + canonical Pearl Star still**.

---

## DISCOVERY REPORT (pre-write)

| Claim source | Status entering this lane | Action |
|--------------|---------------------------|--------|
| 07-19 recon: `wan2.7-r2v-2026-06-12` = **50 s** free intl | Listed in social recon; thin in free-media REPORT video table | **DOC-CONFIRM** pricing row; **ACCOUNT-UNCONFIRMED** remaining — skip r2v burn unless proven |
| Free-media REPORT: r2v only under HappyHorse 10 s | Incomplete vs pricing API existence | **SPLIT** — API exists; account free bucket unproven |
| 04-12: WAN 2.1/2.2 “65–80GB not viable” without Wan2GP | Predates common FP8/GGUF | **SUPERSEDE** — 1.3B/5B/14B-quant paths fit 16GB |
| Untitled 411: video→pose bank beats per-panel gen for clothing | Method lead | **KEEP** as architecture thesis; pilot identity = same-anchor i2v; scale = VACE |
| Untitled 411 / method lean on video-continuation | Needs API field proof | **CONFIRM** on `wan2.7-i2v` (`first_clip` / `last_frame`) |
| Existing exempt client (`dashscope_free_media.py`) | t2v/i2v only; `img_url` legacy field; now landed on main | **NOTE** — r2v + `media[]` in-place extension feasible; prefer i2v first |

---

## TL;DR — decision for Lane 03/04/05

| Role | Engine | Why |
|------|--------|-----|
| **Pilot** | Cloud free quota — **`wan2.7-i2v` + canonical external still** (± first/last; optional short continuation). **Defer r2v** until account seconds proven | Same `/video-synthesis` family as landed exempt client; ~50 s i2v remaining (pack estimate); r2v unconfirmed on `ahjansamvara` |
| **Scale** | Self-host **VACE 1.3B** (Apache-2.0, ~8 GB) ± quantized Wan 2.2 | Fits Pearl Star 16GB; identity+pose; REAL-eligible weights |
| **Do not treat as REAL-eligible without review** | FLUX.1-Kontext-dev (non-commercial), LTX-2.3 (community license, $10M cliff), Wan2GP wrapper (Community License 2.0), DashScope free-quota outputs | License / ToS / INTERIM policy |

**Hard constraint:** Pearl Star manga already peaks ~10.76 GB / ~25 min/panel. Any self-hosted video job **must** be queue-first (`pscli`) and scheduled in off-manga windows or it starves catalog render.

---

## A. Cloud free-tier truth

### A1. `wan2.7-r2v` free bucket (Singapore intl) — Q1

**Verdict (split):**
- **API EXISTS** on Singapore / intl async video family — models `wan2.7-r2v` / `wan2.7-r2v-2026-06-12` ([wan-video-to-video API reference](https://www.alibabacloud.com/help/en/model-studio/wan-video-to-video-api-reference), 2026-07-24). Same `video-synthesis` endpoint as landed exempt client → **in-place extension feasible**.
- **DOC-ONLY free row:** Model pricing International lists **50 seconds** for `wan2.7-r2v*` (fetched 2026-07-24).
- **ACCOUNT-UNCONFIRMED:** `ahjansamvara` remaining r2v free seconds were **not** proven in 07-19 REPORT (table showed r2v only under HappyHorse 10 s). **Lane 04: skip r2v** unless `burn_summary` / Free Quota preflight proves seconds remain. Pilot consistency = **i2v + canonical still**.

| Field | Truth (2026-07-24) | Source |
|-------|--------------------|--------|
| Model IDs | `wan2.7-r2v` / `wan2.7-r2v-2026-06-12` | [wan-video-to-video API](https://www.alibabacloud.com/help/en/model-studio/wan-video-to-video-api-reference); [Model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| Free quota (catalog) | **50 seconds** DOC-ONLY International | Pricing |
| Free quota (this account) | **UNCONFIRMED** — do not spend | Dispatcher live delta + 07-19 REPORT |
| Window | **90 days** after Model Studio activation (new-user intl); fresh accounts may see larger trial (~1650 s video class per dispatcher recon) — **not** assumed for mid-burn account | Pricing + live delta |
| Pack remaining (estimate) | **~45 s t2v + ~50 s i2v** — re-verify `burn_summary` | Live delta 2026-07-24 |
| After free | **$0.10/s @720P** (r2v input+output billable class) | Pricing |
| Rate limits | ~5 RPS / 5 concurrent (07-19 Wan class) | 07-19 recon |
| Region | International free rows only | Pricing |
| Account caveat | Prior `Arrearage` block (07-19); Lane 01 landed exception for free-media scripts on main | free-media REPORT + merge `1a683254…` |

**API shape (r2v):** async native:

- Endpoint: `POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- Header: `X-DashScope-Async: enable`
- Body sketch:

```json
{
  "model": "wan2.7-r2v",
  "input": {
    "prompt": "character1 walks toward character2 holding object from image3 …",
    "media": [
      {"type": "reference_video", "url": "https://…/role1.mp4"},
      {"type": "reference_video", "url": "https://…/role2.mp4"},
      {"type": "reference_image", "url": "https://…/object.png"}
    ]
  },
  "parameters": {
    "resolution": "720P",
    "duration": 10,
    "prompt_extend": false,
    "watermark": false
  }
}
```

Docs/community: up to **5** reference media total (images + videos); duration typically **2–10 s** for r2v (shorter than i2v’s 15 s max). Poll: `GET /api/v1/tasks/{task_id}`.

**Can the existing exempt client gain r2v in-place?**

| Check | Answer |
|-------|--------|
| Same endpoint family? | **YES** — `VIDEO_PATH = /services/aigc/video-generation/video-synthesis` (landed client on main) |
| Current client gap | CLI choices only `wan2.7-t2v` / `wan2.7-i2v`; i2v uses legacy `input.img_url`, not `media[]` |
| Extension size | Small: allow `wan2.7-r2v*`, accept `media` array. **No new DashScope call-site file** |
| Pilot policy | **Feasible but deferred** — skip r2v burn until account free seconds proven; prioritize i2v `media[]` (first/last/continuation) |

**Correction to free-media REPORT table:** API + pricing DOC-ONLY 50 s row exist for Wan r2v; REPORT’s HappyHorse-only r2v cell remains the **account-evidence** caution — catalog ≠ remaining balance.

---

### A2. First/last-frame + video-continuation on wan2.7 free tier — Q2

**Verdict: YES on `wan2.7-i2v` (and dated aliases). Features ride the same free-quota seconds bucket — not a separate grant.**

Official guide (fetched 2026-07-24): Wan 2.7 i2v supports three tasks via `input.media[]`:

| Task | `media[].type` combo | Notes |
|------|----------------------|-------|
| First-frame i2v | `first_frame` (± `driving_audio`) | Animate still |
| First + last frame | `first_frame` + `last_frame` (± audio) | Comic key-pose A→B |
| Video continuation | `first_clip` (± `last_frame`) | Extend clip; **input duration counts toward billed/output duration** |

Duration: **2–15 s** integer; 720P/1080P; inputs free, **successful output seconds** consume free quota / billing. Failed jobs do not consume free quota (pricing/guide).

**Implication for pose-bank method:** Untitled 411’s continuation lean is **API-real** on cloud i2v. Current exempt client has **none** of these fields — pilot tooling (Lane 04/05) must switch i2v to `media[]` (not only `img_url`).

Free-tier availability: same **50 s** on `wan2.7-i2v` International — using first/last or continuation **does not** unlock extra seconds; it spends the same bucket (and continuation can burn seconds faster because the seed clip duration is included in output length).

---

### A3. Still buckets + 90-day window + 2026-10-18 sunset — Q3

**DOC-CONFIRMED from Model pricing (2026-07-24 International free rows):**

| model_id | Free quota | Unit price after |
|----------|------------|------------------|
| `wan2.1-t2i-plus` | **200 images** | $0.05/image |
| `wan2.1-t2i-turbo` | **200 images** | $0.025/image |
| `wan2.2-t2i-plus` | **100 images** | $0.05/image |
| `wan2.2-t2i-flash` | **100 images** | $0.025/image |
| `qwen-image` / `qwen-image-2.0` / plus/max/pro variants | **100 images** each | $0.03–$0.075 |
| `wan2.7-image` / `wan2.7-image-pro` | **50 images** (07-19 recon + prior REPORT) | $0.03 / $0.075 |

**Window mechanics:**
- Grant type: **one-time new-user free quota**, valid **90 days** after Model Studio activation (International).
- **Not monthly recurring.**
- Pack / CLAUDE.md free-media exception **sunset 2026-10-18** = operator policy tied to free-quota expiry / program window — **confirm console remaining** before burn. 2026-10-18 is **not** printed as a SKU expiry on the pricing page; it is the Phoenix program sunset for this exception lane.

**Pilot use:** burn stills for **canonical anchors / turnarounds** (front/3⁄4/side/back), not production covers (Pearl Star FLUX already owns that).

---

### A4. i2v from EXTERNAL image URL / base64 — Q4

**Verdict: YES — public HTTP(S) URL **or** `data:{MIME};base64,…` **or** temporary OSS URL. DashScope-hosted still is NOT required.**

From Wan 2.7 i2v API reference (2026-07-24):

- `media[].url` accepts:
  - **Public URL** (HTTP/HTTPS) — e.g. Pearl Star / R2 / CDN anchor PNG
  - **Base64 data URI** — `data:image/png;base64,…`
  - **Temporary OSS** — `oss://dashscope-instant/…` (upload path)
- Image limits: JPEG/JPG/PNG (no alpha)/BMP/WEBP; side length [240, 8000]; aspect 1:8–8:1; ≤20 MB

**Load-bearing consistency mechanism for pose-bank:** render canonical character still on Pearl Star → publish a **stable public URL** (or base64 for small pilots) → `wan2.7-i2v` with `type: first_frame` (and optionally `last_frame` for key-pose pairs). This is DOC-CONFIRMED; live smoke remains Lane 05.

**Client note:** current `submit_video` passes `img_url` (older shape). Docs say newer multimodal path uses `media[]`; both may work depending on model revision — pilot should prefer **documented `media[]`** for first/last/continuation.

---

## B. Self-hosted on Pearl Star (16GB)

### B5. 2026 Wan open-weights on 16GB — Q5

**SUPERSEDES** `VIDEO_PIPELINE_DEEP_RESEARCH_V2.md` § “WAN 2.1/2.2 … 65–80GB / Not viable standalone.” That verdict predated FP8/GGUF + Wan2GP packing.

| Variant | VRAM (practical) | Throughput (order-of-magnitude) | Runtime | 16GB verdict |
|---------|------------------|----------------------------------|---------|--------------|
| Wan 2.1 T2V **1.3B** | ~6–9 GB FP16; GGUF lower | Fastest; seconds–low-minutes for ~2 s @480p | ComfyUI Wan nodes **or** Wan2GP | **USE** for smoke / draft motion |
| Wan 2.2 **TI2V-5B** | ~8–15 GB FP8 | Faster than 14B; solid 720p candidate | ComfyUI / Wan2GP | **USE** mid quality |
| Wan 2.1/2.2 **14B** FP16 full | ~54–65 GB (T5 on GPU) | N/A on 16GB | — | **SKIP full** |
| 14B **FP8 + T5 CPU offload** | ~14–16 GB @720p | Minutes per short clip | ComfyUI GGUF / Wan2GP | **EVALUATE** — edge of 16GB |
| 14B **GGUF Q5/Q4 + offload** | ~6–10 GB | Slower wallclock; quality trade | ComfyUI / Wan2GP | **USE** if quality OK |
| **Wan2GP** wrapper | Claims select models from **6 GB**; 16GB = “all models / longer / higher res” | UI + VRAM tricks; Bernini/ref paths need ~12–16 GB | Standalone Web UI (**not** ComfyUI-native) | **EVALUATE** for scale path; RAP still wraps jobs |

Sources: Wan2GP MODELS.md / README (2026 fetch); community VRAM guides (WillItRunAI Wan 2.2 VRAM, 2026); HF Wan 2.2 FP8 cards (16GB min).

**Throughput vs manga:** even “fast” 1.3B clips are multi-minute GPU occupations once you include load/offload. Budget **2–10 min/clip** for 480–720p short clips on 5070 Ti depending on steps/frames — empirical calibration is Lane 05+ self-host smoke, not this research.

---

### B6. VACE — identity + pose on 16GB — Q6

**Verdict: YES for VACE-1.3B on 16GB; YES Apache-2.0 on Wan-VACE weights.**

| Item | Truth | Source |
|------|-------|--------|
| What it is | Unified R2V / V2V / MV2V / FLF2V control framework on Wan | HF `Wan-AI/Wan2.1-VACE-1.3B`, ali-vilab VACE cards |
| Identity | Reference images (`src_ref_images`) as subject anchors (stronger than naïve i2v drift narrative in community writeups) | HF README + community comparisons |
| Pose/motion | Preprocess depth/pose/mask into `src_video` / `src_mask` for Animate-Anything-style control | VACE preprocess docs |
| 1.3B VRAM | Official ~**8.19 GB** T2V-class; 480p (~81×480×832); consumer-friendly | wan2.video / RunPod VACE notes |
| 14B VRAM | ~**35 GB** class for I2V — **not** native on 16GB without heavy quant/block-swap community recipes | Same |
| License (weights) | **Apache-2.0** | HF model cards |
| Pearl Star fit | **1.3B primary**; 14B only via GGUF+block-swap experiments (extra risk) | — |

**Scale recommendation:** VACE-1.3B is the open-weights analog of cloud r2v for the pose-bank: **reference identity + pose/depth motion** without spending DashScope seconds.

---

### B7. Alternatives (one paragraph each) — Q7

**LTX-Video / LTX-2.3.** Fast open video path previously recommended (2026-04-12) for cinematic inserts on 16GB (~12–16 GB class). **License changed for LTX-2.x:** LTX-2 Community License (2026-01-05) — free commercial use **below $10M annual revenue**; above that requires paid commercial license. Older “Apache-2.0 LTX” mental model is **stale** for 2.3. Still strong for atmospheric motion; weaker than VACE/r2v for multi-clip character identity. ComfyUI node packs exist. Treat outputs as **INTERIM or license-reviewed** until counsel/operator maps revenue cliff.

**FLUX.1-Kontext.** Best-in-class **still** identity edit (“same teacher, new pose”) via GGUF Q5 ~12–14 GB on Pearl Star (04-12 still valid). **License:** FLUX.1-dev / Kontext-dev = **non-commercial** BFL terms (`flux-1-dev-non-commercial-license`). Excellent for building **canonical still anchors** for later i2v; **not** REAL-eligible for commercial manga ship without a BFL commercial grant. Do not confuse “works on Star” with “provenance REAL.”

**AnimateDiff (Evolved).** Mature ComfyUI motion-module path; HF motion modules often **Apache-2.0**; quality ceiling largely superseded by Wan/LTX for character motion, still useful for **short atmospheric loops** (water, foliage) at 512-class. Low integration risk; weak as primary identity engine for pose-bank.

---

### B8. Queue contention vs ~25 min/panel — Q8

Empirical manga: **~25 min/panel** wallclock Image-to-Layers on 5070 Ti; peak ~10.76 GB (`MANGA_V5_COMPUTE_SCALING_OPTIONS.md`). RAP: all >10 s GPU work via `pscli` — no direct Comfy/Ollama bypass.

**Conservative capacity model (single GPU):**

| Policy | Manga panels/day (serial) | GPU hours left | Video seconds/day (illustrative) |
|--------|---------------------------|----------------|----------------------------------|
| Manga-first (20 h/day manga) | ~48 panels | ~4 h spare | If 5 min/clip → ~48 clips; if each clip yields ~5 “pose frames” after curation → **~240 candidate frames/day** before QA reject |
| Split shift (12 h manga / 8 h video) | ~28 panels | 8 h video | ~96 five-min clips theoretical — **unrealistic**; video jobs also contend with Ollama/TTS |
| Pilot cloud-first | Manga uninterrupted | Cloud burns free seconds | **Preferred for Wave 1** — zero Star contention |

**Recommendation:** Pilot pose-bank **on DashScope free seconds** (Lane 05). Self-host VACE only in **declared off-manga windows** or secondary GPU (Milestone H). Never inline video diffusion inside panel render jobs.

---

### B9. License → provenance — Q9

| Asset | License | Provenance implication (Manga Vision-Conformance) |
|-------|---------|-----------------------------------------------------|
| Wan 2.1/2.2 open weights | **Apache-2.0** | **REAL-eligible** (operator-approved commercial use of outputs) |
| Wan VACE 1.3B/14B weights | **Apache-2.0** | **REAL-eligible** |
| DashScope cloud free-tier outputs | API ToS; Model Library **trial UI** non-commercial language ≠ identical to API free quota — **legal-risk until operator confirms** | Tag **`INTERIM`** for free-quota burn (matches CLAUDE.md free-media exception) |
| Wan2GP **wrapper** | WanGP Community License 2.0 (free company use of outputs; **no** paid SaaS resale of WanGP itself) | Wrapper ≠ weights; weights stay Apache; still prefer ComfyUI-native if avoiding community-license productization layer |
| LTX-2.3 | Community license + $10M cliff | **INTERIM** / counsel until cleared |
| FLUX.1-Kontext-dev | Non-commercial | **INTERIM** for commercial catalog |
| AnimateDiff modules (typical) | Apache-2.0 | REAL-eligible if base model also clean |

**Rule of thumb:** Apache-2.0 open weights → may be labeled REAL after blind/QA bar; **cloud free-quota and non-commercial/community-cliff models → INTERIM** even when visually good.

---

## C. Method evidence

### C10. Cross-clip identity — Q10

| Method | Identity across clips | Public evidence grade | Pose-bank role |
|--------|----------------------|-----------------------|----------------|
| Per-clip **t2v** | Weak — fresh sample each time | High (inherent) | Smoke / style exploration only |
| Same-anchor **i2v** | Strong **within** clip; **drifts across clips** unless same first-frame URL reused | Official i2v = first-frame lock; community: drift over long motion | **Primary pilot** for motion families from one approved still |
| **First+last** i2v | Locks start/end comic keys; mid-arc can still morph | Official feature | Key-pose A→B arcs |
| **Continuation** (`first_clip`) | Temporal glue; seed clip billed into duration | Official guide | Extend usable motion without full reroll |
| Cloud **r2v** | Purpose-built multi-ref identity (≤5 media); **not a guarantee** | Alibaba product docs + production SOPs (community) | **Identity engine** for multi-clip same character |
| Open **VACE** R2V + pose | Reference subject + control video; community reports better face/clothes stability than naïve i2v | HF + RunPod/community | **Scale identity engine** on Star |

**Untitled 411 claims — verification:**

| Claim | Survive? |
|-------|----------|
| Video→curated pose bank beats independent panel gens for **clothing continuity** | **YES (architecture)** — temporal coupling preserves outfit better than i.i.d. stills |
| Video replaces LoRA | **NO** — bank is finite library; LoRA/reference still needed for novel poses/scenes |
| Hybrid (identity conditioner + curated bank + deterministic assemble) | **YES** — aligns with V5 layered doctrine |
| Any r2v/VACE “solves” identity forever | **NO** — steering + audit rubric required |

---

### C11. Capture-program design — Q11

**Goal:** manufacture a **curated pose bank**, not dump every frame.

**Comic-readable keys (sample each clip for):**
1. Neutral / rest  
2. Anticipation  
3. Contact / impact  
4. Follow-through / settle  
5. 3⁄4 turn + profile (head/body)  
6. Occlusion stress tests (hair over eye, arm across torso) — **expect failures**

**Sampling rates (starting recipe for Lane 03):**

| Clip length | Raw fps assume | Extract candidates | Keep after human/QA |
|-------------|----------------|--------------------|---------------------|
| 5 s @ 24–30 fps | 120–150 frames | **8–12** keyed samples (not every Nth blindly) | **4–6** banked cutouts |
| 10 s | 240–300 | **12–16** keyed | **6–8** |

Prefer **manual/key-pose picks** over uniform stride. Uniform `every 6th frame` floods near-duplicates and still misses anticipation peaks.

**Known failure modes (bank filters):**
- **Hands / fingers** — reject or crop  
- **Occlusion-reveal hallucination** on head turns (ear/eye/hair invent)  
- **Clothing mutation across cuts** (button count, sleeve length) — hard fail for bank admission  
- **Background bleed** into cutout — requires matting pass  
- **Identity drift mid-clip** — keep only early stable segment; don’t bank the morph  
- **Continuation billing trap** — long `first_clip` wastes free seconds  

**Program skeleton:** anchor still (Star FLUX/Kontext or approved panel) → cloud i2v motion family → optional r2v for hard identity → extract keys → matte → bank with provenance INTERIM → later VACE self-host for scale.

---

## Decision matrix (Lane 03 cite)

| Need | Pilot (free cloud) | Scale (Pearl Star) | Skip / defer |
|------|--------------------|--------------------|--------------|
| Identity across clips | **Same-anchor i2v** (reuse URL); r2v only if seconds proven | **VACE-1.3B** Apache | t2v-only; unproven r2v |
| Motion from approved still | `wan2.7-i2v` + external URL/base64 | Wan 2.2 5B / 14B-GGUF i2v | SVD (04-12 skip stands) |
| Key-pose A→B | i2v `first_frame`+`last_frame` | VACE FLF2V | — |
| Extend clip | i2v `first_clip` (budget carefully) | Local continuation recipes | Long continuation burns free s |
| Anchor stills | `wan2.1-t2i-*` 200 / qwen-image 100 | FLUX/Kontext on Star (Kontext=INTERIM commercially) | Paid DashScope unattended |
| Atmosphere loops | HappyHorse 10 s only if needed | AnimateDiff / LTX (license check) | — |
| Manga panels | Untouched | Existing Qwen-Image-Layered | Don’t mix queues |

---

## RECOMMENDATIONS (Lane 03 line-cite)

1. **Pilot engine = cloud free quota (`wan2.7-i2v` + canonical still)**, not Star video — protects ~25 min/panel manga throughput.  
2. **Spend order (this account):** (a) re-verify remaining via `burn_summary` / console; (b) 2–3× same-anchor `wan2.7-i2v` @5 s; (c) one first+last pair; (d) **at most one** short continuation; (e) **skip r2v** unless preflight proves r2v seconds remain.  
3. **Extend exempt client in-place** (same `video-synthesis` path): prefer `media[]` for i2v first/last/continuation; r2v model ids optional later — **no new DashScope file**.  
4. **Canonical anchors from Pearl Star** via **public URL or base64** into i2v — DOC-CONFIRMED supported ([i2v API](https://www.alibabacloud.com/help/en/model-studio/image-to-video-general-api-reference), 2026-07-24).  
5. **Scale engine rank:** (1) **VACE-1.3B** Apache (~8 GB) REAL-eligible path; (2) Wan 2.2 5B / quantized Wan; (3) 14B GGUF only if needed; (4) LTX-2.3 license-gated; (5) AnimateDiff atmospheric only.  
6. **Provenance:** free-quota cloud = **INTERIM**; Apache Wan/VACE self-host = **REAL-eligible** after QA; Kontext-dev / LTX-2.3 community cliff = **INTERIM**.  
7. **Capture program:** key-pose sampling (anticipation/impact/follow-through), not dump-all-frames; reject hands / clothing-mutation / occlusion-hallucination.  
8. **Lane 01 is MERGED** (`1a683254…`) — burn is operator-gated Lane 05; bank contract (Lane 03) can cite this doc now.  
9. **Do not assume fresh-account ~1650 s trial** on `ahjansamvara` — mid-burn ~45 s t2v / ~50 s i2v pack estimate only until `burn_summary` re-verify.  
10. **Sunset:** treat **2026-10-18** as hard stop for free-media exception planning; re-verify grants before that date.

---

## Sources (dated)

| ID | URL / path | Fetched / dated |
|----|------------|-----------------|
| S1 | https://www.alibabacloud.com/help/en/model-studio/model-pricing | 2026-07-24 |
| S2 | https://www.alibabacloud.com/help/en/model-studio/wan-image-to-video-guide | 2026-07-24 |
| S3 | https://www.alibabacloud.com/help/en/model-studio/image-to-video-general-api-reference | 2026-07-24 |
| S3b | https://www.alibabacloud.com/help/en/model-studio/wan-video-to-video-api-reference | 2026-07-24 |
| S4 | https://www.alibabacloud.com/help/en/model-studio/video-generate-edit-model | 2026-07-24 |
| S5 | https://www.alibabacloud.com/help/en/model-studio/new-free-quota | cited via prior recon + pricing notes |
| S6 | docs/research/QWEN_MODELSTUDIO_FREE_TIER_SOCIAL_RECON_2026-07-19.md | 2026-07-19 |
| S7 | artifacts/research/dashscope_free_media_2026-07-19/REPORT.md | 2026-07-19 |
| S8 | docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md | 2026-04-12 (partially superseded §Wan VRAM) |
| S9 | docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md | 2026-05-26 |
| S10 | docs/ROBUST_AGENT_PROTOCOL.md | active |
| S11 | HF Wan-AI/Wan2.1-VACE-1.3B (Apache-2.0) | 2026-07-24 |
| S12 | https://github.com/deepbeepmeep/Wan2GP (+ LICENSE.txt Community 2.0) | 2026-07-24 |
| S13 | HF Lightricks/LTX-2.3 LICENSE (community / $10M) | 2026-07-24 |
| S14 | HF black-forest-labs FLUX.1-Kontext-dev non-commercial | 2026-07-24 |
| S15 | old_chat_specs/Untitled 411.txt | leads only |

Evidence mirrors / excerpts: `artifacts/research/manga_video_pose_bank_2026-07-24/`.

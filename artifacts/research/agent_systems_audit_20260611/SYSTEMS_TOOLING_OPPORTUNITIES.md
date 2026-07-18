# Systems Tooling Opportunities — Free / OSS / GitHub / HuggingFace per Subsystem

**Date:** 2026-06-11
**Agent:** Pearl_Research
**Scope:** For each main subsystem in `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` (19 rows), find free / open-source / self-hostable tooling that would make it work better. **Hard filter:** must be self-hostable / free / Tier-2-compatible per `CLAUDE.md` — **no paid-LLM-API dependency in repo code.** (DashScope/ElevenLabs etc. that are *already integrated* stay; new recommendations are OSS-first.)

**Important Tier note:** Several great pipelines in the wild (e.g. open-source video dubbing) wire a *paid LLM* into the translation step. Where I cite such a pipeline, **I recommend only its Tier-2-safe components** (Whisper ASR, FFmpeg, Wav2Lip, NLLB/M2M, XTTS) and explicitly drop the paid-LLM step — our localization already uses Qwen/Gemma local.

**Effort key:** S = ≤1 day wire-up · M = a few days · L = multi-week / spec needed.
**`[verify]`** = promising but I couldn't fully confirm fit/licence from search; validate before adopting.

---

## 0. Top picks (the 5 highest-ROI, read this first)

| Rank | Tool | Subsystem(s) | Why it wins | License | Effort | Tier |
|------|------|--------------|-------------|---------|--------|------|
| **1** | **Langfuse** (or Arize Phoenix) | ALL agents + every pipeline | Closes our #1 gap: self-hosted OTel-native tracing/eval for every agent run + LLM call. One install, repo-wide observability. | Apache-2.0 | M | ✅ self-host |
| **2** | **DeepEval** + **agentevals** | ei_v2 / quality, core_pipeline, pearl_news, translation | 50+ metrics incl. hallucination/faithfulness, CI/CD-native; agentevals adds trajectory scoring. Turns "quality" from vibes into gated metrics. | Apache-2.0 / MIT | M | ✅ local judge (Gemma/Qwen) |
| **3** | **Kokoro-82M + F5-TTS** (alongside ElevenLabs) | audiobook_pipeline, video_pipeline | Kokoro = sub-0.3s CPU narration for drafts/scratch; F5-TTS = OSS voice-cloning fallback if ElevenLabs quota/cost bites. MOS gap to commercial now 0.1–0.3. | Apache-2.0 (Kokoro) / MIT (F5) | M | ✅ self-host |
| **4** | **RAGAS / CometKiwi** | ei_v2 (citations), translation | RAGAS = reference-free claim-level faithfulness for our citation cascade; CometKiwi = reference-free MT quality estimation to gate localization without human refs. | Apache-2.0 / MIT | M | ✅ local |
| **5** | **PuLID-Flux II + InstantID** (already partly in manga spec) | manga_pipeline, ite | Confirms our face-lock choice is current SOTA; InstantID/EcomID as alternates for angle-robustness where PuLID drops likeness. Validates anchors registry. | Apache-2.0 (models) | S–M | ✅ self-host |

---

## 1. Per-subsystem tooling tables

### core_pipeline / pearl_prime (book pipeline — Pearl_Prime)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **DeepEval** (CI eval gates) | Chapter/atom quality as pass/fail metrics (coherence, instruction-following, custom rubric) in CI, not manual read | Apache-2.0 | M | ✅ local judge |
| **Qwen3 / Gemma 4 via Ollama or vLLM** | Tier-2 unattended drafting; Qwen3 Apache-2.0 no commercial cap; vLLM for batched OpenAI-compatible serving (faster than Ollama at scale) | Apache-2.0 | M | ✅ self-host |
| **evaluator-optimizer loop** (pattern, not a tool) | Wire existing quality gates as generator→critic→regenerate so a chapter auto-revises until it passes | n/a | L | ✅ |
| **outlines / guidance** (structured-gen) `[verify]` | Constrain Tier-2 model output to your atom/manuscript JSON schema deterministically | Apache-2.0 | M | ✅ local |

### manga_pipeline / ite (Pearl_Dev)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **PuLID-Flux II** | Face identity injection preserving art style — matches our anchors-registry choice; current SOTA for style-preserving character lock | Apache-2.0 | S | ✅ self-host |
| **InstantID / EcomID** | Angle-robust face swap where PuLID drops likeness; alternate face-lock for non-frontal panels | Apache-2.0 | M | ✅ self-host |
| **ComfyUI + IP-Adapter (ViT-H CLIP-Vision)** | Reference-image character consistency in node graphs we already run; note 24GB VRAM on some IP-Adapter configs | GPL-3.0 (ComfyUI) | S | ✅ self-host |
| **Animagine XL** (we use 4.0) | Confirmed top open anime model w/ Danbooru-tag prompting for B&W panels — keep | Fair-AI license `[verify]` | — | ✅ self-host |
| **FLUX.2 (10-ref)** `[verify]` | If/when licensing allows: single-pass multi-reference identity+style preservation could simplify the 5-model stack | check BFL licence | L | ✅ self-host |

### audiobook_pipeline (Pearl_Dev) + video_pipeline narration
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **Kokoro-82M** | Ultra-fast (<0.3s), CPU-capable narration for drafts/proofs before spending ElevenLabs credits; CLI supports EPUB/PDF | Apache-2.0 | M | ✅ self-host |
| **F5-TTS** | OSS zero-shot voice cloning fallback; high-fidelity expressive speech | MIT | M | ✅ self-host |
| **XTTS v2** | 17-lang zero-shot cloning from 6s ref — multilingual audiobook coverage without per-lang vendor | Coqui Public Model License `[verify]` | M | ✅ self-host |
| **Chatterbox** | Cloning on a single gaming GPU from ~10s audio | MIT `[verify]` | M | ✅ self-host |
| **whisperX / faster-whisper** | Forced-alignment + word timestamps for audiobook chaptering & caption sync | MIT/BSD | S | ✅ self-host |

### video_pipeline (Pearl_Video)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **Whisper / faster-whisper** | ASR for auto-subtitles, dub alignment, caption burn-in | MIT | S | ✅ self-host |
| **FFmpeg** | Already core; lean on filtergraph for caption burn, concat, loudness norm (EBU R128) | LGPL/GPL | S | ✅ self-host |
| **Wav2Lip / SadTalker / LivePortrait** | Lip-sync on existing footage (Wav2Lip), one-image talking avatar (SadTalker fast / LivePortrait premium) for narrator/teacher faces | MIT-ish `[verify]` per repo | M | ✅ self-host |
| **M2M-100 / NLLB** (dub translation) | Replace the paid-LLM translate step in OSS dub pipelines with Tier-2 MT (or reuse our Qwen/Gemma) | MIT / CC-BY-NC→open ckpts | M | ✅ self-host |
| **Manim** `[verify]` | Programmatic explainer/diagram animation for educational video segments | MIT | M | ✅ self-host |

### translation (Pearl_Localization)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **CometKiwi** | **Reference-free** MT quality estimation — gate locale output without a human reference (fits our quality_contracts) | Apache-2.0 `[verify]` | M | ✅ local |
| **NLLB-200 (open ckpts) / MADLAD-400** | NLLB-200 3.3B beat Mistral/Llama on BLEU/chrF++/COMET in cited study; MADLAD covers 400+ langs incl. long-tail/dialect | open ckpts / Apache-2.0 | M | ✅ self-host |
| **MQM rubric** (framework) | Structured error taxonomy (accuracy/fluency/style) for localization QA contracts | open spec | S | ✅ |
| **COMET / chrF++ / sacreBLEU** | Standard automatic MT metrics for regression-testing locale quality in CI | MIT/Apache | S | ✅ local |

### ei_v2 / quality (Pearl_Research) + recommendations
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **RAGAS** | Reference-free, claim-level **faithfulness + correctness** decomposition — directly strengthens the citation-gap cascade (every factual claim scored) | Apache-2.0 | M | ✅ local judge |
| **DeepEval** | Hallucination detection + 50+ metrics, CI/CD gates for EI/quality | Apache-2.0 | M | ✅ local |
| **TruLens** | Feedback functions + OTel tracing if we want runtime monitoring of quality, not just batch eval | MIT | M | ✅ local |
| **agentevals** | Trajectory scoring for the research agent's own plan/tool path | MIT | S | ✅ local |

### pearl_news (Pearl_News)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **RAGAS + DeepEval** | Faithfulness/grounding gates for civic-journalism claims (no fabricated sources) | Apache-2.0 | M | ✅ local |
| **trafilatura / newspaper3k** `[verify]` | Robust article extraction for the deep-research engine feeds | Apache-2.0/MIT | S | ✅ self-host |
| **Qwen deep-research engine** (we have) | Keep; add a RAGAS verification pass on its output | — | S | ✅ self-host |

### trend_feeds / integrations (Pearl_Int)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **RSSHub** `[verify]` | Self-hosted universal feed generator — turns sites without RSS into feeds for trend monitoring | MIT | M | ✅ self-host |
| **MCP Inspector** (`npx @modelcontextprotocol/inspector`) | Test/validate our MCP integrations + new tool defs before wiring | MIT | S | ✅ |
| **Playwright** | Deterministic scrapers for portals without APIs (we already do browser automation) | Apache-2.0 | M | ✅ self-host |

### brand_admin / dashboard / marketing (Pearl_Prez / Pearl_Brand / Pearl_Marketing)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **Observable Plot / Chart.js / ECharts** | Better, lighter dashboard charts than hand-rolled; self-contained HTML (matches our brand_admin.html approach) | ISC/MIT | S | ✅ self-host |
| **Lighthouse CI** | Automated perf/a11y budgets for brand-admin + storefront pages in CI | Apache-2.0 | S | ✅ self-host |
| **DataTables / AG-Grid Community** | Sortable/filterable catalog tables in the dashboard | MIT | S | ✅ self-host |

### music_mode (Pearl_Editor)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **ACE-Step 1.5** | Local Suno-class generation; 4-min song in ~20s on one GPU; strong structure — the safe self-hosted answer after the Suno/Udio lawsuits | Apache-2.0 `[verify]` | M | ✅ self-host |
| **YuE** | Open lyrics→full-song (vocal + accompaniment), Apache-2.0 | Apache-2.0 | M | ✅ self-host |
| **MusicGen / Stable Audio Open** | Melody-conditioned / SFX & beds; Stable Audio's VAE underpins many 2026 models | MIT / Stability community | M | ✅ self-host |

### github_operations / pearl_devops (Pearl_GitHub / Pearl_DevOps)
| Tool | What it improves | License | Effort | Tier |
|------|------------------|---------|--------|------|
| **OpenTelemetry GenAI + Langfuse** | Trace agent git-sessions; see where push-guard/preflight time goes | Apache-2.0 | M | ✅ self-host |
| **pre-commit framework** `[verify]` | Standardize the preflight/push-guard hooks under one runner | MIT | S | ✅ self-host |
| **act** (`nektos/act`) `[verify]` | Run GitHub Actions locally to validate the LLM-policy + governance workflows before push | MIT | S | ✅ self-host |

---

## 2. Cross-cutting observations

1. **One observability install serves the whole repo.** Langfuse/Phoenix is the highest-leverage single addition — it's the substrate the eval tools (DeepEval, RAGAS, agentevals) emit into, and it closes the agent-trajectory + tracing gaps from `AGENTS_BEST_PRACTICE_AUDIT.md` (#16, #17) simultaneously.
2. **Eval frameworks all run on a *local judge*.** RAGAS/DeepEval/TruLens use LLM-as-judge — we point them at Gemma/Qwen (Tier-2), so they're fully policy-compliant and unattended-safe.
3. **The TTS gap to commercial is nearly closed** (MOS within 0.1–0.3). Kokoro/F5/XTTS as a *draft + fallback* tier reduces ElevenLabs spend without quality cliff on final renders.
4. **Our manga face-lock stack is current.** PuLID/InstantID search confirms the anchors-registry choices (Qwen-Image faces, PuLID-FLUX face-lock) are 2025–2026 SOTA — no change needed, just validation + InstantID as an angle-robust alternate.
5. **Music-mode should standardize on Apache-2.0 local models** (ACE-Step/YuE) — the Suno/Udio litigation makes self-hosting the risk-correct posture, which aligns with our Tier policy anyway.

---

## Sources (accessed 2026-06-11)
- BentoML — Open-Source Image Generation Models guide. https://www.bentoml.com/blog/a-guide-to-open-source-image-generation-models
- MyAIForce — Hyper LoRA vs InstantID vs PuLID vs ACE Plus. https://myaiforce.com/hyperlora-vs-instantid-vs-pulid-vs-ace-plus/
- RunComfy — PuLID Flux II consistent character. https://www.runcomfy.com/comfyui-workflows/pulid-flux-ii-in-comfyui-consistent-character-ai-generation
- Inferless — 12 Best Open-Source TTS Models Compared (2025). https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2
- DigitalOcean — Best TTS Models: F5-TTS, Kokoro, SparkTTS, Sesame CSM. https://www.digitalocean.com/community/tutorials/best-text-to-speech-models
- Kokoro TTS. https://kokorottsai.com/  · kokoro-tts CLI (EPUB/PDF). https://github.com/nazdridoy/kokoro-tts
- Picovoice — Open-Source Translation Models 2025. https://picovoice.ai/blog/open-source-translation/
- Open-NLLB checkpoints. https://github.com/gordicaleksa/Open-NLLB  · Meta NLLB-200. https://ai.meta.com/blog/nllb-200-high-quality-machine-translation/
- Slator — Traditional MT vs LLM AI translation (NLLB-200 3.3B vs LLMs). https://slator.com/research-pits-traditional-machine-translation-against-llm-powered-ai-translation/
- Atlan — RAGAS, TruLens, DeepEval compared. https://atlan.com/know/llm-evaluation-frameworks-compared/
- DeepEval — RAG Evaluation guide. https://deepeval.com/guides/guides-rag-evaluation
- Union.ai — Open-Source Video Dubbing (Whisper/M2M/XTTS/SadTalker). https://www.union.ai/blog-post/open-source-video-dubbing-using-whisper-m2m-coqui-xtts-and-sad-talker
- pixazo — Best Open-Source Lip-Sync Models 2026. https://www.pixazo.ai/blog/best-open-source-lip-sync-models
- HuggingFace — Best Open-Source LLM Models 2026 (Qwen3/Gemma4). https://huggingface.co/blog/daya-shankar/open-source-llms
- ACE-Step 1.5 (GitHub). https://github.com/ace-step/ACE-Step-1.5  · YuE (GitHub). https://github.com/multimodal-art-projection/YuE
- Spheron — Deploy OSS Music Generation (YuE/ACE-Step/MusicGen/Stable Audio). https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/
- Langfuse (GitHub). https://github.com/langfuse/langfuse  · Arize Phoenix (GitHub). https://github.com/arize-ai/phoenix
- OpenTelemetry — AI Agent Observability. https://opentelemetry.io/blog/2025/ai-agent-observability/
- MCP Spec 2025-11-25 (Inspector, tool best-practices). https://modelcontextprotocol.io/specification/2025-11-25

# Self-host 16GB notes (Q5–Q9)

**Date:** 2026-07-24 | **Target:** Pearl Star RTX 5070 Ti 16GB

## Q5 — Wan open-weights (SUPERSEDES 2026-04-12 65–80GB skip)

| Variant | Practical VRAM | Verdict |
|---------|----------------|---------|
| Wan 2.1 1.3B | ~6–9 GB | USE smoke/draft |
| Wan 2.2 5B | ~8–15 GB FP8 | USE mid |
| 14B FP16 full | ~54–65 GB | SKIP |
| 14B FP8/GGUF + offload | ~6–16 GB | EVALUATE |
| Wan2GP | 6GB+ claimed; 16GB headroom | EVALUATE (Community License 2.0 wrapper) |

## Q6 — VACE

- ali-vilab/VACE + Wan-AI/Wan2.1-VACE-1.3B: **Apache-2.0**
- 1.3B ~8 GB friendly; 480p; reference identity + pose/depth control
- 14B needs substantially more VRAM (~35 GB class without quant)
- **Pearl Star preference: VACE 1.3B** (or quantized Wan), not 14B native

## Q7 — Alternatives

- LTX-2.3: fast inserts; **community license + $10M revenue cliff** → INTERIM until cleared
- FLUX.1-Kontext-dev: still identity; **non-commercial** → INTERIM commercially
- AnimateDiff: Apache modules typical; atmospheric loops; weak primary identity

## Q8 — Queue contention

- Manga ~25 min/panel, ~10.76 GB peak
- RAP: pscli queue-first for all >10s GPU
- Pilot video on **cloud** to avoid starving manga
- Self-host video only in declared off-manga windows

## Q9 — License → provenance

| Weights | License | Provenance |
|---------|---------|------------|
| Wan / VACE | Apache-2.0 | REAL-eligible after QA |
| DashScope free outputs | API ToS / free-media exception | INTERIM |
| LTX-2.3 / Kontext-dev | community / non-commercial | INTERIM |

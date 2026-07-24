# Evidence index — manga video pose-bank capability research

**Date:** 2026-07-24  
**Lane:** 02 Pearl_Research  
**Parent doc:** `docs/research/MANGA_VIDEO_POSE_BANK_CAPABILITY_RESEARCH_2026-07-24.md`

## Primary URLs (fetched / cited 2026-07-24)

| ID | URL | What it proves |
|----|-----|----------------|
| E1 | https://www.alibabacloud.com/help/en/model-studio/wan-video-to-video-api-reference | wan2.7-r2v / wan2.7-r2v-2026-06-12 API exists; Singapore workspace; async video-synthesis family |
| E2 | https://www.alibabacloud.com/help/en/model-studio/model-pricing | International free quota rows: wan2.7-r2v* 50s DOC-ONLY; wan2.7-i2v/t2v 50s; wan2.1-t2i 200 imgs; wan2.2-t2i 100; qwen-image 100; 90-day note |
| E3 | https://www.alibabacloud.com/help/en/model-studio/wan-image-to-video-guide | first/last frame + video continuation on wan2.7-i2v |
| E4 | https://www.alibabacloud.com/help/en/model-studio/image-to-video-general-api-reference | media[] types; public URL + base64 + oss:// inputs |
| E5 | https://www.alibabacloud.com/help/en/model-studio/video-generate-edit-model | model card matrix t2v/i2v/r2v/edit |
| E6 | https://huggingface.co/Wan-AI/Wan2.1-VACE-1.3B | VACE 1.3B Apache-2.0; ~8GB-class / 480p |
| E7 | https://huggingface.co/ali-vilab/VACE-Wan2.1-1.3B-Preview | ali-vilab VACE Apache-2.0 |
| E8 | https://github.com/deepbeepmeep/Wan2GP | Wan2GP low-VRAM path; Community License 2.0 (wrapper) |
| E9 | https://huggingface.co/Lightricks/LTX-2.3 | LTX-2.3 community license / $10M cliff |
| E10 | HF black-forest-labs FLUX.1-Kontext-dev | non-commercial license |

## Prior Phoenix artifacts

| Path | Role |
|------|------|
| `artifacts/research/dashscope_free_media_2026-07-19/REPORT.md` | Live Arrearage probe; incomplete r2v table (HappyHorse caution) |
| `docs/research/QWEN_MODELSTUDIO_FREE_TIER_SOCIAL_RECON_2026-07-19.md` | Per-model free grants DOC-ONLY |
| `docs/VIDEO_PIPELINE_DEEP_RESEARCH_V2.md` | 2026-04-12 — Wan 65–80GB claim SUPERSEDED |
| `docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md` | ~25 min/panel; 10.76 GB peak |
| `old_chat_specs/Untitled 411.txt` | Method LEADS only |

## Account / pack live delta (dispatcher 2026-07-24)

- Lane 01 merged: `dashscope-free-media-landed=1a683254959710ec85033dce0a164ee18ace4cb2`
- Mid-burn estimate: ~45s t2v + ~50s i2v remaining — re-verify `burn_summary`
- Fresh-account ~1650s video trial / 90d Singapore — **not** assumed for ahjansamvara
- r2v free remaining: **UNCONFIRMED** → skip unless preflight proves

## Files in this directory

- `SOURCES.md` — this index
- `QUOTAS_AND_API_NOTES.md` — condensed Q1–Q4 cloud notes
- `SELFHOST_16GB_NOTES.md` — condensed Q5–Q9 notes
- `METHOD_CAPTURE_NOTES.md` — condensed Q10–Q11 notes

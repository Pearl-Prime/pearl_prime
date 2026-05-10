# Phase 2 P0 — text-free image renders (negative prompt)

**Project:** PRJ-DUAL-PATH-IMAGE-RENDER-V1  
**Date:** 2026-05-10  
**Context:** PR #1020 activation — operator visual review: unwanted **text / words / typography** in many panels. Image generation must stay **text-free**; lettering is applied in a downstream pipeline.

## Code changes

Static text-suppression terms are appended after `{{negative_prompt}}` in the CLIP negative encode node of:

- `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json`
- `scripts/image_generation/comfyui_workflows/animagine_xl_txt2img_manga.json`
- `scripts/image_generation/comfyui_workflows/qwen_image_txt2img_manga.json` (includes extra CJK script negations for Qwen-Image)

`scripts/image_generation/manga_teacher_batch.py` now substitutes the placeholder with **`.replace("{{negative_prompt}}", …)`** so runtime negatives from `panel_prompts` are preserved **and** the new static suffix stays on the wire (full-string assignment would have dropped the suffix).

Terms mirrored from the brief (bare `characters` avoided so figure/character art is not suppressed; **text characters** used instead):  
`text, words, letters, captions, watermark, signature, signs, writing, typography, text characters, font, lettering, logos, subtitles, calligraphy`  
Qwen-only: `chinese characters, japanese characters, kanji, hiragana, katakana, hangul`.

## Before / after (visual)

| Role | Path |
|------|------|
| **Before (PR #1020 / pre-fix)** | Operator-captured renders from PR #1020 activation (text in frame). Use those PNGs as the “before” column next to the after image below. |
| **After (this branch, FLUX schnell)** | `artifacts/manga/negative_prompt_test_2026-05-10/flux_schnell_smoke_after.png` |

## Verification (FLUX schnell smoke, RunComfy)

- **Workflow:** `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json` (patched negative slot + `_build_workflow` `.replace` so the static suffix survives injection).
- **API:** RunComfy `POST …/inference` with JSON field **`workflow_api_json`** (v1 `workflow` key returns 422 on current API).
- **Positive:** manga-style slice-of-life courtyard panel (includes a unique `seed{unix}` fragment in the prose to avoid ComfyUI **ExecutionWithoutNewYield** cache skips when iterating).
- **Runtime negative:** `low quality, blurry, bad anatomy, extra fingers` — concatenated in-node with the new static text-suppression list from the workflow template.
- **Latest successful run (evidence for this artifact):** `request_id=aa5e941b-74cd-4fc8-bbf7-d7baa9b27b2b` (~2.2 MiB PNG committed at the path above).

`batch_runner --activate` does not exist in-tree; this verification used the same graph and RunComfy credentials as the dual-path wiring docs (`artifacts/qa/runcomfy_pearl_int_wiring_2026-05-10.md`).

**Operator verdict (pending):** open `flux_schnell_smoke_after.png` beside the worst text-heavy PR #1020 frame and confirm reduced/absent incidental typography (lettering still belongs in the downstream lettering layer).

# Cloud quotas + API notes (Q1–Q4)

**Date:** 2026-07-24 | **Status:** DOC-CONFIRMED API/pricing; ACCOUNT remaining = OPERATOR-VERIFY

## Q1 — wan2.7-r2v

- API: EXISTS — https://www.alibabacloud.com/help/en/model-studio/wan-video-to-video-api-reference (2026-07-24)
- Models: `wan2.7-r2v`, `wan2.7-r2v-2026-06-12`
- Endpoint family: same async `…/video-generation/video-synthesis` as `scripts/social/dashscope_free_media.py`
- Pricing free row (International): 50 seconds DOC-ONLY
- Account free remaining: **UNCONFIRMED** (07-19 REPORT lacked Wan r2v free evidence)
- **Action:** Lane 04 skip r2v unless burn_summary/preflight proves seconds

## Q2 — first/last + continuation

- On `wan2.7-i2v` via `media[]`:
  - `first_frame` / `last_frame`
  - `first_clip` (± `last_frame`) for continuation
- Guide: https://www.alibabacloud.com/help/en/model-studio/wan-image-to-video-guide (2026-07-24)
- Free spend: same i2v seconds bucket; continuation includes seed duration in output length

## Q3 — still buckets

| Model | Free (intl, 90d one-time) |
|-------|---------------------------|
| wan2.1-t2i-plus / turbo | 200 images |
| wan2.2-t2i-plus / flash | 100 images |
| qwen-image* | 100 images |
| Program sunset | 2026-10-18 (Phoenix free-media exception) |

Source: https://www.alibabacloud.com/help/en/model-studio/model-pricing (2026-07-24)

## Q4 — external image into i2v

- Public HTTPS URL: YES
- Base64 `data:{MIME};base64,…`: YES
- oss:// temporary: YES
- DashScope-hosted still: NOT required
- Source: https://www.alibabacloud.com/help/en/model-studio/image-to-video-general-api-reference (2026-07-24)

## Pack account estimate (re-verify)

- ~45s t2v + ~50s i2v remaining (dispatcher 2026-07-24)
- Do not assume fresh-account ~1650s trial on ahjansamvara

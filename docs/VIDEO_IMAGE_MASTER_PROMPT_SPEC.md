# Video Image Master Prompt Spec

Canonical template and API flow for generating a single test image (master prompt QA). Source: [docs/flux_shnell_research.rtf](flux_shnell_research.rtf), [config/video/brand_style_tokens.yaml](../config/video/brand_style_tokens.yaml), [config/video/prompt_constraints.yaml](../config/video/prompt_constraints.yaml).

**Authority:** This spec MUST comply with [docs/VIDEO_PIPELINE_VISUAL_BRIEF.md](VIDEO_PIPELINE_VISUAL_BRIEF.md). If this spec and the visual brief conflict, **the visual brief wins**.

## Template structure (research file)

Three-part prompt, then negative block:

1. **Foreground (illustration)** — One sentence: style + subject + composition. Use palette `prompt_name` values from `brand_style_tokens.yaml` for the chosen topic/band (no raw hex in prompt). When `prompt_rules.require_dark_anchor` is set for a topic, append a grounding phrase (e.g. dark wood, charcoal textile, deep shadow) so pale palettes do not wash out.
2. **Background:** — One sentence: atmospheric abstract gradient, palette names, **soft depth, clean edges, gentle tonal separation, solid surfaces** — not blur or haze.
3. **Overall lighting:** — One sentence: **soft ambient light, no overexposure, grounded** mood, end with `9:16, highly detailed but soft.**

Negative block: per-band `never_rules` from `brand_style_tokens.bands.<band>.never_rules` + topic `prompt_rules.never` (if any) + `prompt_constraints.yaml` shared (`no_adoration` + `shared_negatives`).

## Anti-washout rules

- **Never use in positive prompts:** haze, hazy, ethereal, translucent, foggy, misty, volumetric haze, soft blur as a global effect, or language that implies see-through or diffusion across the whole frame.
- **Always ensure:** solid surfaces are visible; the subject is identifiable at thumbnail size; at least one **dark anchor** element when a topic uses a pale palette (see `brand_style_tokens.yaml` — e.g. anxiety `prompt_rules` and `dark anchor` in the palette list).
- **Color rule:** Even “pale mist” palettes need at least one dark anchor element so the image does not read as all highlight.
- **Test:** If you squint at the image and cannot tell what it is, it fails the visual brief legibility bar (&lt;0.5 s).

## Example: anxiety, hands holding tea by window

- **Band:** cool_calm  
- **Topic:** anxiety  
- **Palette prompt_names:** slate blue grey, pale mist blue, pale mist, dark anchor  
- **Never rules (cool_calm):** high contrast, forced brightness, saturated accent on grief/depression  
- **Topic prompt_rules.never (anxiety):** all-white background, pure mist, nothing but light  
- **Shared:** no adoration phrases + shared_negatives  

Positive prompt (template filled):

```
A soft hand-painted gouache illustration of a person's hands holding a cup of tea by a window, in slate blue grey, pale mist blue, pale mist and dark anchor, soft brush texture, gentle paper-like grain, centered composition, generous negative space, no faces, contemplative mood. Include dark wooden surface, charcoal textile, or deep shadow area.

Background: an atmospheric abstract gradient of slate blue grey, pale mist blue, pale mist and dark anchor, with gentle depth, clean edges, soft tonal separation.

Overall lighting: soft ambient light, quiet and undramatic, no overexposure, grounded, 9:16, highly detailed but soft.
```

Negative prompt (cool_calm never_rules + topic never + no_adoration + shared_negatives):

```
high contrast, forced brightness, saturated accent on grief/depression, all-white background, pure mist, nothing but light, no dramatic light rays from above, no figure silhouetted against bright sky, no hands reaching upward, no golden hour backlighting on figure, no divine or spiritual glow, no anime style, no full faces, no high contrast comic lines, no busy patterned background, no sharp geometric shapes, no flat vector, no sharp comic lines, washed out, overexposed, blown highlights, translucent, see-through, foggy, hazy, ethereal glow, volumetric haze, soft focus everywhere, blurry edges, no contrast
```

## API: Cloudflare Workers AI FLUX

- **Endpoint:** `POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-2-dev`
- **Auth:** `Authorization: Bearer {API_TOKEN}`
- **Body:** multipart/form-data: `prompt`, `width`, `height`, optional `steps`, `guidance`, `seed`
- **9:16:** e.g. width=576 height=1024 (or 1080×1920 if supported)
- **Output:** JSON with base64 image (decode and save as PNG/JPEG for QA)

**Credentials:** Set env vars `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` (or `CLOUDFLARE_AI_API_TOKEN`). Or put them in a key file at repo root: `cloudflare_workers_ai.txt` or `11.txt` with lines `CLOUDFLARE_ACCOUNT_ID=...` and `CLOUDFLARE_API_TOKEN=...`. Or use a `.env` at repo root. **Full steps (dashboard, key file, troubleshooting):** [docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md](VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md).

## Script

[scripts/video/run_flux_generate.py](../scripts/video/run_flux_generate.py) builds the prompt from config, calls the API, writes the image to `image_bank/` or `--out` path.

Primary image generation on Pearl Star uses ComfyUI; see `scripts/video/flux_client.py` (`call_comfyui`, `COMFYUI_URL`).

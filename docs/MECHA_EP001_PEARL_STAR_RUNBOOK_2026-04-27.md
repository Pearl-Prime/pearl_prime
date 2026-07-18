# Mecha ep_001 — Pearl Star Render Runbook

**Operator-attended runbook** for rendering all 35 panels of `pilot_anchor_mecha × master_wu × burnout × the_chassis_is_listening ep_001` via Pearl Star ComfyUI (FLUX-schnell-fp8, free local GPU).

**Authority:** PR #723 (mecha ep_001 chapter script + FLUX prompts) · `docs/sessions/SESSION_HANDOFF_2026-04-25.md` runbook §5 · `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` Pearl Star section.

**Estimated wall-clock:** 35 panels × ~2-3 min/panel on FLUX-schnell-fp8 = **70-105 min** continuous render time.

---

## 0. Pre-flight (operator does this on Pearl Star)

SSH to Pearl Star (`pearlstar.tail7fd910.ts.net`) and verify:

```bash
# 0.1 Confirm the rig is up + ComfyUI reachable
curl -sS http://192.168.1.112:8188/system_stats | head -3

# 0.2 If ComfyUI is NOT running, start it:
cd ~/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188 &

# 0.3 Confirm FLUX-schnell-fp8 model is loaded:
curl -sS http://192.168.1.112:8188/object_info/CheckpointLoaderSimple | python3 -c "import json,sys; d=json.load(sys.stdin); print('models:', d['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0][:5])"

# 0.4 Confirm sufficient disk space (~100 MB minimum)
df -h ~/ComfyUI/output | tail -1
```

If all 4 checks pass, proceed.

---

## 1. Sync repo + verify panel prompts JSON

```bash
cd ~/phoenix_omega
git fetch origin && git checkout main && git pull --ff-only

ls -la artifacts/manga/panel_prompts/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/ep_001.panel_prompts.json
# Expected: ~70 KB / 393 lines
```

---

## 2. Smoke test — render ONE panel first

```bash
export COMFYUI_URL=http://192.168.1.112:8188

python3 scripts/manga/queue_panel_renders.py \
    --panel-prompts artifacts/manga/panel_prompts/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/ep_001.panel_prompts.json \
    --only-panel ep001_001
```

Expected output:
```
queue: 1 panel(s) · series=pilot_anchor_mecha__... · chapter=ep_001
output dir: ~/phoenix_omega/artifacts/manga/pilot_anchor_mecha__.../panels/ep_001
comfy URL: http://192.168.1.112:8188
  OK   ep001_001: wrote ep001_001.png (X,XXX,XXX bytes)

result: 1 ok · 0 failed · 0 skipped (of 1 total)
```

Verify locally:
```bash
open artifacts/manga/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/panels/ep_001/ep001_001.png
```

The image should show pilot Kaede Sorano in a hangar pre-launch with brass meridian-line tracery on the chassis spine, warm cockpit-amber + cool industrial palette. **Do NOT proceed to step 3 if the image looks wrong.**

---

## 3. Full chapter render (35 panels; ~70-105 min)

```bash
python3 scripts/manga/queue_panel_renders.py \
    --panel-prompts artifacts/manga/panel_prompts/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/ep_001.panel_prompts.json \
    --skip-existing \
    2>&1 | tee /tmp/mecha_ep001_render.log
```

`--skip-existing` resumes from step 2's smoke-test panel + lets you safely re-run.

Expected: 35 lines total (1 SKIP from smoke test + 34 OK).

---

## 4. Visual QA via thumbnail grid

```bash
python3 scripts/manga/build_thumbnail_review_grid.py \
    --input-dir artifacts/manga/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/panels/ep_001/ \
    --output-html artifacts/manga/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/review/ep_001_thumbnail_grid.html

open artifacts/manga/pilot_anchor_mecha__master_wu__en_US__burnout__the_chassis_is_listening/review/ep_001_thumbnail_grid.html
```

Walk all 35 thumbnails. Spot-check:
- Color palette consistency
- Character continuity (Kaede looks like Kaede across panels)
- Composition variety (mix of close-up cockpit + chassis exterior + instrument detail)
- Mecha look correct (Evangelion-tonal NOT Gundam-action; brass meridian tracery visible)
- Beat-type matches visible content

If any panel needs re-render: delete its PNG and re-run step 3 — `--skip-existing` keeps the others.

---

## 5. Next steps after panels approved

| Step | What | Where |
|------|------|-------|
| Bubble compose (en_US) | Overlay text bubbles on panels | `phoenix_v4/manga/chapter/bubble_render.py` |
| Bubble compose (ja_JP) | Same panels + ja_JP text | (same script; `--locale ja_JP`) |
| Webtoon vertical strip | Stack panels into scrolling format | `phoenix_v4/manga/chapter/webtoon_compose.py` |
| R2 upload | Cloud storage for delivery | `scripts/artifacts/r2_sync.py` |
| WEBTOON Canvas package | Final publish-ready bundle | `scripts/publish/webtoon_canvas_upload.py` |

These are out of scope for this runbook — they're `proj_manga_first_ship_20260425` next-steps territory.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `urllib.error.URLError` on submit | ComfyUI not running OR wrong URL | Verify step 0.1; check `COMFYUI_URL` env |
| Poll timeout (5 min/panel) | GPU OOM or slow steps setting | Reduce `DEFAULT_STEPS` from 22 to 18 in script |
| All renders fail same error | Workflow template bug | Inspect `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json` |
| Image looks wrong | FLUX prompt OR wrong model loaded | Re-read PR #723; verify FLUX-schnell-fp8 not FLUX-dev |
| Some OK, some FAIL | Per-panel prompt issue | Inspect failed panel in `ep_001.panel_prompts.json` |

---

## 7. Cost note

Pearl Star is **operator-owned local GPU** — $0 marginal cost. RunComfy cloud fallback (if Pearl Star unavailable) would charge $0.05-$0.20 per panel = $1.75-$7 for the full chapter. See `scripts/image_generation/runcomfy_batch.py` for cloud driver.

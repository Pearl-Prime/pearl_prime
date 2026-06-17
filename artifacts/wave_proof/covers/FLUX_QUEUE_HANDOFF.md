# FLUX cover tranche — DEFERRED to post-install job-queue run

**Generated:** 2026-06-17 by Pearl_Prime (devotion_path NEW-BEST-WAY proof wave)
**Why deferred:** Pearl Star's GPU is mid-install (job-queue install in flight, reboot imminent).
This session is forbidden from invoking Pearl Star / FLUX / Qwen (GPU contention). All burnout +
courage covers below are **PIL placeholders** with a visible "FLUX PENDING" imagery patch; final art
must be rendered by FLUX once the GPU install lands.

## Cover split (per `scripts/publish/render_kdp_cover.py:20-24` + `config/publishing/bestseller_templates.yaml`)

| genre | type | this session | post-install action |
|---|---|---|---|
| `imposter_syndrome` | TYPE-DOMINANT (no FLUX) | **4 REAL PIL covers** (`real_pil_imposter/`) | none — final |
| `burnout` | IMAGE-BEARING (FLUX) | PIL placeholder (`placeholder_flux_pending/`) | **QUEUE FLUX** imagery_zone x[35,65] y[58,80] |
| `courage` | IMAGE-BEARING (FLUX) | PIL placeholder (`placeholder_flux_pending/`) | **QUEUE FLUX** imagery_zone x[0,100] y[62,88] |

## Post-install FLUX queue run (do NOT run in a GPU-contended session)

Two-stage cover pipeline (text is PIL-composited, never in the FLUX prompt — see memory
"Cover text-overlay two-stage"):

```
# Stage 1 (FLUX imagery only, on Pearl Star after GPU install):
python3 scripts/publish/render_imagery_for_template.py --genre burnout  --book <book_id> ...
python3 scripts/publish/render_imagery_for_template.py --genre courage  --book <book_id> ...
# Stage 2 (PIL composite — this is what this session ran with placeholder imagery):
python3 scripts/publish/render_kdp_cover.py --illustration <flux_render.png> \
  --title "<naming-engine title>" --subtitle "<persona subtitle>" \
  --author "Sai Maa" --publisher "Open Vessel Press" --genre <burnout|courage> --output <cover.png>
```

## FLUX-tranche count for the bounded proof wave

- burnout cells in this wave: 7 distinct (persona,topic) builds → **7 burnout covers need FLUX**
- courage cells: atom-blocked this wave (TEACHER_DOCTRINE gap), but the full-catalog FLUX tranche is:
  - burnout: 33 cells → 33 FLUX covers
  - courage: 30 cells → 30 FLUX covers
  - **Total FLUX-tranche for full 85-cell catalog = 63 covers** (imposter 22 stay PIL).

This handoff pairs with the scaled job-queue catalog run (see WAVE_PROOF_REPORT.md).

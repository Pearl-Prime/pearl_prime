# stillness_press Manga — Brand-1 Deep Build Manifest

**Layer 2 validation.** 3 series scripted; **all 3 ep_001 now RENDERED** on Pearl Star ComfyUI
(series 1 = 35 panels reused from main; series 2 + 3 rendered 2026-05-28 via the live Tailscale
endpoint, disproving the prior "Pearl Star unreachable" stub).

## Series scripted + rendered (ep_001 each)

| # | Series | title_id | character | topic | script | render |
|---|---|---|---|---|---|---|
| 1 | What the Body Holds | `stillness_press_anxiety_vol1` | Mira / Hana | anxiety | `scripts/series1_what_the_body_holds_ep001.md` | **RENDERED** (35 panels) + assembled (on main) |
| 2 | The Night Before You Sleep | `stillness_press_sleep_vol1` | Yuki | sleep_anxiety | `scripts/series2_the_night_before_you_sleep_ep001.md` | **RENDERED** (34 panels) + assembled 2026-05-28 |
| 3 | Hands, Shoulders, Breath | `stillness_press_somatic_vol1` | Mei | somatic_healing | `scripts/series3_hands_shoulders_breath_ep001.md` | **RENDERED** (34 panels) + assembled 2026-05-28 |

This covers all 3 of the stillness_press `active_series_target` (per `config/manga/manga_brand_series_plan.yaml`: anxiety=1, sleep_anxiety=1, somatic_healing=1).

## Series 2 + 3 render (NEW — Pearl Star ComfyUI, this session)

Rendered with `render_series_panels.py` (parses each render-ready markdown script → text-free
iyashikei FLUX prompts → `flux1-schnell-fp8` 4-step, 1080×1920 WEBTOON-vertical, per-panel
deterministic seed). Backend: **Pearl Star ComfyUI over Tailscale** (`$COMFYUI_URL`, load via
`scripts/ci/load_integration_env_from_keychain.py` — NOT the stale 192.168.1.112). $0 spend.

Per-panel source PNGs (~2 MB each) are **git-ignored** (`rendered/.gitignore`) because brand1_deep
ships raw blobs and they exceed the 1 MB no-binary-blobs cap; they are reproducible from the scripts.
Committed in-repo proof: `rendered/series{2,3}_contact_sheet.png` (downscaled grids, <1 MB) +
`rendered/<series>/ep_001/RENDER_PROGRESS.tsv`. Assemble deliverables with `assemble_series.py`:

| Deliverable | Size | Reproduce |
|---|---|---|
| `assembled/series2_ep001/kdp.pdf` | ~5.3 MB, 34pp | `assemble_series.py --series 2` [LOCAL] |
| `assembled/series2_ep001/webtoon_strip.png` | ~43 MB, 800px | `assemble_series.py --series 2` [LOCAL] |
| `assembled/series3_ep001/kdp.pdf` | ~5 MB, 34pp | `assemble_series.py --series 3` [LOCAL] |
| `assembled/series3_ep001/webtoon_strip.png` | ~40 MB, 800px | `assemble_series.py --series 3` [LOCAL] |

## Series 1 rendered assets (REUSED — already on main)

- **Source panels (35):** `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/ep001_001.png … ep001_035.png` (1080×1920, render_source `V4_composed_v4_qwen`).
- **Panel prompts:** `artifacts/manga/panel_prompts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.panel_prompts.json`.

The series-1 chapter script (`series1_what_the_body_holds_ep001.md`) maps lettering/captions/dialogue 1:1 to these 35 rendered panels.

## Assembled deliverables (LOCAL — not committed)

Assembled in `manga/assembled/` for operator review. **NOT committed to git** (each exceeds the
`no-binary-blobs.yml` 1 MB cap and the GitHub LFS budget is exhausted — see `.gitattributes`
teacher_pics note). They are deterministically reproducible from the source panels:

| Deliverable | Size | Dims/pages | Reproduce |
|---|---|---|---|
| `assembled/series1_ep001_kdp.pdf` | 5.6 MB | 35 pages | PIL: `imgs[0].save(pdf, "PDF", save_all=True, append_images=imgs[1:], resolution=150)` |
| `assembled/series1_ep001_webtoon_strip.png` | 28 MB | 800×49770 | PIL: vertical concat of 35 panels scaled to 800px width |

A prior identical assembly already ships in the W22 weekly package:
`artifacts/weekly_packages/stillness_press/2026-W22/kdp/stillness_press_2026-W22_manga.pdf` (35pp, 5.6 MB)
and `…/webtoon/stillness_press_2026-W22_manga.png` (68 MB, full-res). For production distribution,
push assembled binaries to Cloudflare R2 via `scripts/artifacts/r2_sync.py` (Layer 2 pattern).

## Lettering / ja_JP continuation

The rendered panels are language-agnostic art. The lettering layer (captions/dialogue/SFX from
each markdown script) is composited downstream; the ja_JP lettering re-translates only the text
layer via Qwen on Pearl Star (Tier 2). Per the series plans, ja webtoon cadence is bi-weekly.

For higher-fidelity character-locked renders (named cast face-lock), the V4 layered pipeline
(`scripts/manga/render_v4_episode.py`, needs per-panel `continuity_state` YAMLs) remains the
production path; this session used the lighter txt2img path to validate that series 2 + 3 render
end-to-end on the live Pearl Star endpoint. $0 spend (Pearl Star primary, RTX 5070 Ti).

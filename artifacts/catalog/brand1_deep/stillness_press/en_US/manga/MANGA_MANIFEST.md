# stillness_press Manga — Brand-1 Deep Build Manifest

**Layer 2 validation.** 3 series scripted; series 1 fully rendered (35 panels) + assembled to KDP PDF + WEBTOON strip.

## Series scripted (ep_001 each)

| # | Series | title_id | character | topic | script | render |
|---|---|---|---|---|---|---|
| 1 | What the Body Holds | `stillness_press_anxiety_vol1` | Mira / Hana | anxiety | `scripts/series1_what_the_body_holds_ep001.md` | **RENDERED** (35 panels) + assembled |
| 2 | The Night Before You Sleep | `stillness_press_sleep_vol1` | Yuki | sleep_anxiety | `scripts/series2_the_night_before_you_sleep_ep001.md` | script-only (render-ready) |
| 3 | Hands, Shoulders, Breath | `stillness_press_somatic_vol1` | Mei | somatic_healing | `scripts/series3_hands_shoulders_breath_ep001.md` | script-only (render-ready) |

This covers all 3 of the stillness_press `active_series_target` (per `config/manga/manga_brand_series_plan.yaml`: anxiety=1, sleep_anxiety=1, somatic_healing=1).

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

## Render continuation (series 2 + 3)

Series 2 and 3 ep_001 are scripted with render-ready panel descriptions (~35 panels each).
To render: feed each script's panel descriptions through `scripts/manga/build_panel_prompts_v2.py`
→ `scripts/manga/render_v4_episode.py` against Pearl Star ComfyUI (`http://192.168.1.112:8188`,
RTX 3060). **Pearl Star was UNREACHABLE from this session** (local network); rendering deferred
to an operator-present session on the Pearl Star LAN. $0 expected (Pearl Star primary).

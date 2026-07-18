# stillness_press Image Bank — Brand-1 Deep Build Manifest

**Layer 2 validation.** Inventory of image assets backing the brand-1 deep build.
**Spend this session: $0** — all reuse of existing renders + PIL composites. RunComfy ledger
unchanged at $0.137/$10 month (`artifacts/qa/runcomfy_monthly_spend.tsv`). Pearl Star ComfyUI
(`http://192.168.1.112:8188`) was UNREACHABLE from this session (local LAN), so no new GPU renders.

## Committed in this build (real bytes in git, <110 KB each, raw blobs)

| Asset | Path | Source |
|---|---|---|
| 4 book covers (1600×2560) | `../books/covers/cover_*.png` | PIL typographic, iyashikei palette (`../books/make_covers.py`) |

Cover imagery is the PIL text layer per the COVER-TEXT-OVERLAY two-stage rule (FLUX renders
imagery, PIL composites text). The FLUX imagery layer is deferred (Pearl Star unreachable) — the
current covers are clean typographic-on-gradient, valid for KDP, and embedded in the EPUBs
(all pass `scripts/publish/validate_epub.py` with 0 errors).

## Reused (already on main; >1 MB so referenced, NOT re-committed)

| Asset group | Count | Path | Notes |
|---|---|---|---|
| Series-1 composed panels | 35 | `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/ep001_*.png` | 1080×1920, render_source `V4_composed_v4_qwen`. ~1.8-2.5 MB each. Back the series-1 manga chapter + KDP PDF + WEBTOON strip. |
| Final page composites | 3 | `artifacts/manga/stillness_press_qa_run/final_page_composite/page_00{1,2,3}.png` | QA-run page composites. |
| Character image bank (Ahjan) | ~30+ logged | `artifacts/manga/image_bank/stillness_press/` (GENERATION_PROGRESS.tsv) | Anchors, model sheets, expressions, poses — logged "completed" but PNG bytes are R2-offloaded locally; only metadata JSON present on disk. |

## Image-generation continuation (deferred — Pearl Star LAN required)

Tier policy: **Pearl Star primary ($0)**; RunComfy fallback only within $5 cap (~$9.86 headroom).
Pearl Star was unreachable from this session. The following render jobs are queued for an
operator-present session on the Pearl Star LAN:

1. **Cover imagery layer** — render iyashikei field backgrounds for the 4 book covers via
   `scripts/image_generation/generate_bestseller_covers.py` against Pearl Star; recomposite text
   via `../books/make_covers.py` (swap gradient for rendered field).
2. **Series 2 + 3 manga panels** — ~35 panels each from the ep_001 scripts
   (`../manga/scripts/series2_*.md`, `series3_*.md`) via `scripts/manga/build_panel_prompts_v2.py`
   → `scripts/manga/render_v4_episode.py`.
3. **Character model sheets for Yuki (series 2) and Mei (series 3)** — the anxiety series has
   Mira/Hana sheets; sleep + somatic series need their own character locks before panel render.

All deferred work is $0 on Pearl Star. No RunComfy spend was incurred or is required for the
committed deliverables.

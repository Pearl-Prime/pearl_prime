# Manga CJK Text Shaping (Phase 2 #13 of PR #631)

**Status:** Module shipped + Pillow-fallback path active. HarfBuzz
upgrade opt-in via `pip install uharfbuzz` on the renderer host.

**Authority:** [`phoenix_v4/manga/chapter/cjk_text_shaper.py`](../phoenix_v4/manga/chapter/cjk_text_shaper.py)
**Tests:** [`tests/manga/test_cjk_text_shaper.py`](../tests/manga/test_cjk_text_shaper.py)

## Why this exists

PR #631 §13 named Pillow's text-drawing primitives as a CJK ship-quality
gap. Pillow can render any font, but it doesn't apply:

- Optical kerning (CJK characters need it less than Latin, but proper
  punctuation kerning still matters)
- Contextual substitution (e.g. half-width / full-width form switching
  in Japanese mixed-script text)
- Vertical CJK (縦書き) — required for B&W page-manga flatten exports
  in ja_JP and zh_TW
- Furigana ruby annotations
- Per-glyph positional adjustments for combined diacritics

Without proper shaping, CJK lettering looks **AI-rendered** — exactly
the failure mode PR #631 risk register R-8 calls out as a downranking
risk on LINE Manga / Piccoma / Naver.

## What ships in this PR

A **module + integration point** that bubble_render and page_compose
can call without changing their signature. The module:

1. Detects CJK locales (`is_cjk_locale("ja_JP") → True`)
2. Selects the right font for the locale + role (consults
   `fonts/manga/FONT_REGISTRY.yaml` from PR #647)
3. Routes shaping through HarfBuzz when available, Pillow when not
4. Never raises — defensive fallback so a single CJK-shaping miss
   doesn't abort an episode render

## Render path

```python
from phoenix_v4.manga.chapter.cjk_text_shaper import render_text_to_pil

render_text_to_pil(
    draw,                  # PIL ImageDraw instance
    "やあ",                # text in target locale
    x=10, y=20,
    font=pil_font,         # PIL ImageFont (loaded with the right CJK font)
    locale="ja_JP",        # routes through HarfBuzz if available
    fill=(0, 0, 0, 255),
)
```

Behavior matrix:

| Locale | uharfbuzz | Font installed | Path |
|---|---|---|---|
| en_US | (any) | (any) | Pillow direct (current behavior) |
| ja_JP | ❌ | (any) | Pillow fallback — same output as today |
| ja_JP | ✅ | ❌ | Pillow fallback |
| ja_JP | ✅ | ✅ | HarfBuzz shaping |

## Operator activation

To upgrade a host to the HarfBuzz path:

```bash
pip install uharfbuzz
bash scripts/manga/install_manga_fonts.sh
python3 -c "from phoenix_v4.manga.chapter.cjk_text_shaper import diagnose; print(diagnose())"
```

Expected diagnostic output after activation:

```python
{
  "uharfbuzz_available": True,
  "registered_locales": ["en_US", "ja_JP", "ko_KR", "zh_CN", "zh_TW"],
  "fonts_count": 12,
}
```

## Force fallback for testing

```bash
PHOENIX_OMEGA_PILLOW_ONLY=1 python3 your_render_script.py
```

Useful when:
- Reproducing a CI environment locally (CI runs with Pillow only)
- A/B comparing HarfBuzz output against the baseline
- Debugging an unexpected glyph difference

## CI policy

CI runs on `ubuntu-latest` without `uharfbuzz` installed. All 268+ manga
tests pass through the Pillow fallback path. Adding `uharfbuzz` to
`requirements.txt` is intentionally **not** part of this PR — keeping
the CI dependency surface flat and the test environment deterministic.

If a future PR wants to test the HarfBuzz path in CI, add a separate
job with `pip install uharfbuzz` + a tagged test marker, similar to
the `--strict` mode for `check_font_registry.py`.

## Why "module + opt-in" instead of "rewrite bubble_render"

PR #631 §13 says full HarfBuzz/Cairo migration is a larger surface
change. The right ordering:

1. **Phase 2A (this PR):** Ship the module + the contract bubble_render
   will eventually call. Existing code unchanged. All tests still pass.
2. **Phase 2B (follow-up):** bubble_render replaces its `_render_text_in_bubble`
   internals to call `render_text_to_pil` for CJK locales. Verified
   against actual rendered samples.
3. **Phase 2C (follow-up):** page_compose adds vertical-CJK support
   for ja_JP / zh_TW B&W flatten exports — needs full Cairo for
   real layout, not just shaping.

This PR is Phase 2A. Phase 2B and 2C ship after operator-tested with
real CJK fonts on real panels.

## Out of scope (follow-ups)

- **bubble_render integration** — replace `draw.text()` calls with
  `render_text_to_pil()` for CJK locales. Tiny edit; lands after this.
- **Vertical CJK (縦書き)** — required for B&W ja_JP page manga.
  Needs a different layout path that walks columns right-to-left.
- **Furigana** — small ruby annotations above kanji. Phase 3.
- **Cairo rasterization** — current implementation rasterizes via
  Pillow even on the HarfBuzz path. Full migration to Cairo gives
  per-glyph positional control + better hinting on small text. Phase 2C.

## Related

- PR #631 §13 — the why
- PR #647 (FONT_REGISTRY v2) — which fonts to load
- PR #648 (bubble_render ↔ locale_resolver) — the integration point this prepares for
- PR #650 (webtoon_compose) — calls bubble_render's output as composer input
- `CLAUDE.md` § LLM Tier Policy — this PR ships infra, no LLM calls

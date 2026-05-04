# Pearl News Layout System — Governing Spec

**Authority:** This is the canonical spec for Pearl News article-page layout variants. Any future refactor of `pearl_news/pipeline/assemble_v52.py` that touches layout, sidebar position, or canvas widths must preserve the contract below. Linked from [`docs/DOCS_INDEX.md`](DOCS_INDEX.md).

**Date:** 2026-05-04
**Owner:** Pearl News subsystem
**Anti-regression — read this if tempted to "simplify":** the layout system has been mis-fixed >10 times because reviewers consolidated variants without understanding what each one does. Every variant exists for a different reading mode. **Do not consolidate. Do not "tidy up" by removing variants. Do not move logic out of `assemble_v52.py` into a separate template engine.** Read [Section 5 — Historical regression](#5-historical-regression) before proposing changes.

---

## 1. The five-layout system, summarized

Pearl News supports **five mutually-exclusive page layouts** for the long-form article view. The variant is a per-article `meta["layout"]` value consumed by [`pearl_news/pipeline/assemble_v52.py:777`](../pearl_news/pipeline/assemble_v52.py:777). The operator's mental model is **three sidebar positions** (left / right / bottom); two additional canvas-width variants exist for editorial and immersive reading.

| `meta["layout"]` value | Sidebar position | Canvas width | Use for |
|---|---|---|---|
| `default` | **right** (360px column) | 1100px | Standard article. The fallback when nothing else is requested. |
| `dock` | **left** (280px sticky rail with section nav + compact cards) | 1100px | Long reads where a TOC + persistent practice timer add value. |
| `wide` | **bottom** (sidebar reflows as horizontal flex card strip below article body) | 1280px (body 900px centered) | The widest reading canvas — content gets full real estate, cards become a closing "Practice & Engage" section. |
| `editorial` | right (280px) | **1280px** (body 860px) | Wider canvas variant of `default` — for high-attention pieces where sidebar is still useful. |
| `scroll_story` | **none** (sidebar hidden; cards appear inline as interstitials between sections) | 720px reading column | Immersive scroll-driven story format. |

`LAYOUT_VARIANTS` is exported from [`pearl_news/pipeline/assemble_v52.py:36`](../pearl_news/pipeline/assemble_v52.py:36) as a `frozenset` of these five strings. Validation at [line 777](../pearl_news/pipeline/assemble_v52.py:777) falls back to `"default"` and emits a `logger.warning` for unknown values.

---

## 2. Visual reference

QA renders captured 2026-05-03 at desktop 1440×900 and mobile 375×812. All ten screenshots live at [`artifacts/qa/pearl_news_layout_screenshots_2026-05-03/`](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/).

| Variant | Desktop | Mobile |
|---|---|---|
| `default` (right) | [desktop_default.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/desktop_default.png) | [mobile_default.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/mobile_default.png) |
| `dock` (left) | [desktop_dock.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/desktop_dock.png) | [mobile_dock.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/mobile_dock.png) |
| `wide` (bottom) | [desktop_wide.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/desktop_wide.png) | [mobile_wide.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/mobile_wide.png) |
| `editorial` | [desktop_editorial.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/desktop_editorial.png) | [mobile_editorial.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/mobile_editorial.png) |
| `scroll_story` | [desktop_scroll_story.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/desktop_scroll_story.png) | [mobile_scroll_story.png](../artifacts/qa/pearl_news_layout_screenshots_2026-05-03/mobile_scroll_story.png) |

Re-render via:

```bash
python3 -c "
from pearl_news.pipeline.assemble_v52 import assemble_v52
import json, pathlib
article = json.loads(pathlib.Path('artifacts/pearl_news/qa_cli/article_571ce81ad02e5493.json').read_text())
for layout in ['default','scroll_story','dock','editorial','wide']:
    meta = {'teacher':'junko','topic':'mental_health','sdg':'3','template':'hard_news_spiritual_response','date':'2026-04-22','news_event':'QA','hero_image_url':'','layout':layout}
    pathlib.Path(f'/tmp/qa_{layout}.html').write_text(assemble_v52(article, meta, standalone=True))
"
```

---

## 3. The selector mechanism

Variant is set per-article on the `meta` dict and consumed exactly once by `assemble_v52()`:

- **CLI flag (`--layout`)** in:
  - [`pearl_news/pipeline/run_article_pipeline.py`](../pearl_news/pipeline/run_article_pipeline.py) — choices restricted to the five values; threaded into `v52_meta["layout"]` at the assembler call site
  - [`scripts/run_pearl_news_teacher_batch.py`](../scripts/run_pearl_news_teacher_batch.py) — same flag, threaded through `_render_article_payload(item, layout=args.layout)`
- **Programmatic** — any caller of `assemble_v52(article_json, metadata)` that sets `metadata["layout"]` to one of the five strings.

There is **no URL param, body class, query string, or runtime variant switcher**. The variant is decided at article-build time and baked into the static HTML.

```python
# pearl_news/pipeline/assemble_v52.py:777
layout = meta.get("layout", "default")  # "default" | "scroll_story" | "dock" | "editorial" | "wide"
if layout not in LAYOUT_VARIANTS:
    logger.warning("assemble_v52: unknown layout %r — falling back to 'default'", layout)
    layout = "default"
```

The variant drives a single CSS injection at line ~1005:

```python
_layout_css = ""
if layout == "scroll_story": _layout_css = CSS_SCROLL_STORY
elif layout == "dock":       _layout_css = CSS_DOCK
elif layout == "editorial":  _layout_css = CSS_EDITORIAL
elif layout == "wide":       _layout_css = CSS_WIDE
# `default` injects nothing extra — relies on CSS_BLOCK alone
```

---

## 4. CSS structure

All variant CSS is scoped under `.pn-article-root` so it cannot leak into the WordPress (Newspaper) theme. The article wrapper carries a `lang` attribute that drives lang-aware overrides (e.g. localized strip headers).

| Constant | File location | What it does |
|---|---|---|
| `CSS_BLOCK` | [assemble_v52.py:~1400](../pearl_news/pipeline/assemble_v52.py) | Base styles. Always emitted. Defines the `default` layout (1fr 360px grid, 1100px max). |
| `CSS_SCROLL_STORY` | ~1497 | Single-column block layout, sidebar hidden, inline interstitial cards. |
| `CSS_DOCK` | ~1547 | Left sticky 280px rail. Mobile: rail hidden, `.sidebar` reveals as a stacked column below article. |
| `CSS_EDITORIAL` | ~1612 | Wider 1280px canvas, 860px article body, 280px sidebar, slightly larger type. |
| `CSS_WIDE` | ~1647 | `display: block` container, body 900px centered, `.sidebar` reflows as horizontal flex strip with localized "Practice & Engage" `::before` label (en/ja/zh/ko). |

Lang-aware strip-header overrides (en is the default `content`):

```css
.pn-article-root[lang="ja"] .sidebar::before { content: "実践と参加"; }
.pn-article-root[lang="zh"] .sidebar::before { content: "练习与参与"; }
.pn-article-root[lang="ko"] .sidebar::before { content: "실천과 참여"; }
```

---

## 5. Historical regression

**SHA where layouts were authored:** `d6ead3af7a8798c5c2d7da49f2052d293e2f44d4` (2026-04-23, on `agent/fix-pearl-news-deterministic-slots`)
**Branch where work stalled:** `agent/fix-pearl-news-deterministic-slots`
**PR that bundled it:** [#587](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/587) (open since 2026-04-23, never merged, blocked by an unrelated `test_injection_resolver.py` failure)

**One-paragraph root cause.** The five-layout system was committed under a misleading commit subject ("`use item title as headline fallback instead of 'Untitled'`") that did not advertise the layout work. PR #587's title said only "wire deterministic teacher slots" — reviewers and downstream agents never realized the layout system was bundled inside. Subsequent operator complaints about "the sidebar is stuck in the bottom variant with collapsed real estate" were diagnosed as bugs in the **default** layout's mobile-collapse CSS on `main`, where there was nothing wrong to fix. Multiple agents re-authored variations of the layout system on different branches without finding the existing implementation. The fix was always there — in PR #587 — and just needed cherry-picking + the publisher wiring (`--layout` flag) which was missing.

This was [`failure mode #2`](../artifacts/audit/pearl_news_layout_archaeology_2026-05-03.md) from the brief: stranded work on an unmerged branch presenting as a regression on `main`.

---

## 6. Test surface

Layout regression tests live at [`tests/test_pearl_news_sidebar_v52.py`](../tests/test_pearl_news_sidebar_v52.py). Coverage:

| Test | Asserts |
|---|---|
| `test_layout_variants_constant_has_five` | `LAYOUT_VARIANTS == frozenset({...})` exactly the five. |
| `test_default_layout_renders_right_sidebar` | `default` injects no override CSS; `1fr 360px` grid present. |
| `test_dock_layout_renders_left_sticky_sidebar` | `sidebar-dock` + `position: sticky` + `280px 1fr` grid. |
| `test_wide_layout_renders_bottom_strip` | `flex-direction: row` + `"PRACTICE & ENGAGE"` + `実践と参加` (JA fallback). |
| `test_wide_layout_lang_attribute_threads_through` | `lang="ja"` reaches `.pn-article-root`. |
| `test_editorial_layout_renders_wider_canvas` | `1280px` canvas + `1fr 280px` grid. |
| `test_scroll_story_layout_hides_sidebar` | `.sidebar { display: none; }`. |
| `test_unknown_layout_falls_back_to_default` | Unknown value → default + `logger.warning`. |
| `test_dock_mobile_surfaces_sidebar_cards` | Mobile dock breakpoint reveals `.pn-article-root .sidebar` (otherwise dock-mobile users lose practice timer + CTAs). |

To render and visually QA all five variants in a browser, follow the recipe in Section 2 and load each `/tmp/qa_<variant>.html`. Re-screenshot at 1440×900 and 375×812 if any layout CSS changes.

---

## 7. Anti-regression checklist

Future PRs touching Pearl News article rendering must preserve every item below. Reviewers: if a PR breaks any of these, request changes.

- [ ] **Five distinct layouts.** `LAYOUT_VARIANTS` enumerates exactly `{default, scroll_story, dock, editorial, wide}`. Adding a sixth is a feature; removing one is a regression.
- [ ] **Variant strings are stable.** `default | scroll_story | dock | editorial | wide`. These names appear in operator-facing CLI flags, config files, and stored article metadata. Renaming any one of them requires a coordinated migration.
- [ ] **CSS scoping.** Every variant rule lives under `.pn-article-root`. No global selectors. No leakage into the WP Newspaper theme. (The base `CSS_BLOCK` has some unscoped rules for backwards-compat — do NOT add more.)
- [ ] **Selector unity.** Variant is selected ONLY via `meta["layout"]`. Do not introduce parallel selectors (URL param, body class, theme template flag). One source of truth.
- [ ] **Lang attribute.** `.pn-article-root` carries `lang="<two-letter-code>"`. Lang-aware CSS overrides are keyed off this attribute. New text strings (e.g. another section header) must add ja/zh/ko overrides if visible.
- [ ] **Mobile parity.** Every desktop variant must render usefully on mobile (≤768px). No variant may leave mobile users without access to practice/CTA cards. The `dock` mobile fallback specifically depends on `@media (max-width: 768px)` revealing `.pn-article-root .sidebar`.
- [ ] **Publisher wiring.** Any caller of `assemble_v52()` that publishes to WordPress MUST pass `meta["layout"]`. Both [`run_article_pipeline.py`](../pearl_news/pipeline/run_article_pipeline.py) and [`scripts/run_pearl_news_teacher_batch.py`](../scripts/run_pearl_news_teacher_batch.py) thread `--layout` through; new publishers must too.
- [ ] **Validation + warning.** Unknown layout values fall back to `default` with a `logger.warning`. Do not silently accept arbitrary strings.
- [ ] **Tests stay green.** All 9 layout tests in `tests/test_pearl_news_sidebar_v52.py` pass. Adding a layout = adding tests.
- [ ] **Visual sign-off.** Any change to `CSS_*` constants requires re-rendering the screenshots in `artifacts/qa/pearl_news_layout_screenshots_<date>/` and operator review of all 10 (5 desktop + 5 mobile).
- [ ] **Do not consolidate variants into a single template with conditional class.** This was tried; it was a regression. Each variant is a separate `CSS_*` constant for a reason — the rules diverge enough that conditional CSS becomes harder to read than five distinct blocks.
- [ ] **Do not move layout selection out of `assemble_v52.py` into a template engine.** It was tried; it didn't help. The function is a single source of truth and should stay that way.

---

## 8. Indexing

This doc is tagged as a **governing spec** in [`docs/DOCS_INDEX.md`](DOCS_INDEX.md) under the Pearl News section. If you are auditing repo-wide governing specs (e.g. via the `Pearl_PM` or `Pearl_Architect` workflows), this doc is in scope.

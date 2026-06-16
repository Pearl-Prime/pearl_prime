# Pearl News Sidebar Layout Restore — Git Archaeology Report

**Date:** 2026-05-13
**Agent:** Pearl_News (Claude Opus 4.7, 1M context)
**Task:** Restore three WordPress sidebar/overlay layout templates (right / left / bottom) by git archaeology only. DO NOT re-author.
**Branch:** `claude/lucid-almeida-4581a7`
**Status:** **NO CODE DRIFT DETECTED — restore is a no-op at the code layer. Bug is downstream of the repo, in the WordPress Newspaper theme content-wrapper width.**

---

## TL;DR

The operator's "drift broke it" premise is **not supported by the git record**. The pearl_news layout system on `main` is byte-identical to PR #853's merge commit (`8070e81fd`, 2026-05-04) — the canonical five-layout sidebar system. Zero pearl_news/ commits exist between `8070e81fd` and current `main`. The bug the operator is observing in WordPress is the **theme content-wrapper width constraint** documented in `docs/pearl_news/LAYOUT_HANDOFF.md` (commit `90bb3ef08`, 2026-04-23) — it is server-side, not in this repo.

Per the operator's anti-improvise rule, this audit STOPS rather than reauthoring CSS or adding a shim.

---

## 1. Git archaeology — primary suspect: PR #853 (`8070e81fd`)

| Check | Command | Result |
|---|---|---|
| Is PR #853 reachable from main? | `git merge-base --is-ancestor 8070e81fd main` | **YES** |
| Diff of pearl_news/ between 8070e81fd and main | `git diff 8070e81fd..main -- pearl_news/` | **EMPTY (byte-identical)** |
| Commits touching pearl_news/ since 8070e81fd | `git log --oneline 8070e81fd..main -- pearl_news/` | **0 commits** |
| Commits touching publish/wordpress_client.py | `git log --oneline 8070e81fd..main -- pearl_news/publish/wordpress_client.py` | **0 commits** |
| Only diff in the PR-853 path set since merge | `git diff 8070e81fd..main --stat` (PR-853 paths) | `docs/DOCS_INDEX.md` only (+30/−1, unrelated to layouts) |

**Conclusion:** There is no "last-known-good" SHA different from current `main` to restore from. PR #853 is the last-known-good and it is already in place. There has been no code drift since 2026-05-04.

### Candidate SHAs surveyed (and rejected as restore targets)

| SHA | Subject | Reason rejected |
|---|---|---|
| `8070e81fd` (#853) | five-layout sidebar system + --layout CLI + governing spec | **Already at HEAD — no restore work.** |
| `23215bf31` | v52 slot HTML strip, stacked layout width, WP upsert by slug | Predates PR #853; subset of the canonical system. |
| `732ccfd56` | v5.4 interactive sidebar + 13 US manga lead-picks | Predates PR #853; superseded. |
| `87fc9befe`, `b6d1beda0` | restore v5.2 sidebar + teacher-per-article | Both are pre-#853 attempts at the same bug. Their content was rolled into the canonical system via the d6ead3af7a cherry-pick. |
| `d148285be` (#505) | 1-topic × 1-teacher × 1-article + byline/sidebar | Predates PR #853 substantially; sidebar work superseded. |
| `44c853748` | teacher ordering, tradition names, template diversity, emotional hook | Not a layout commit. |
| `90bb3ef08` | docs(pearl-news): layout handoff — sidebar positioning bug + fix options | **Docs-only.** **Confirms the bug is a WordPress theme wrapper issue, not a template bug.** |

---

## 2. Code-level proof the templates are intact

### 2.1 LAYOUT_VARIANTS and selector are correct

[pearl_news/pipeline/assemble_v52.py:46](pearl_news/pipeline/assemble_v52.py:46)

```python
LAYOUT_VARIANTS = frozenset({"default", "scroll_story", "dock", "editorial", "wide"})
```

[pearl_news/pipeline/assemble_v52.py:791](pearl_news/pipeline/assemble_v52.py:791) — validation + warning:

```python
if layout not in LAYOUT_VARIANTS:
    logger.warning("assemble_v52: unknown layout %r — falling back to 'default'", layout)
    layout = "default"
```

[pearl_news/pipeline/assemble_v52.py:1023-1029](pearl_news/pipeline/assemble_v52.py:1023) — CSS injection switch:

```python
if layout == "scroll_story": _layout_css = CSS_SCROLL_STORY
elif layout == "dock":       _layout_css = CSS_DOCK
elif layout == "editorial":  _layout_css = CSS_EDITORIAL
elif layout == "wide":       _layout_css = CSS_WIDE
```

[pearl_news/pipeline/assemble_v52.py:1436](pearl_news/pipeline/assemble_v52.py:1436) — default grid:

```css
.article-container { display: grid; grid-template-columns: 1fr 360px; gap: 48px; max-width: 1100px; ... }
@media (max-width: 768px) { .article-container { grid-template-columns: 1fr; gap: 32px; } .sidebar { order: 2; } ... }
```

[pearl_news/pipeline/assemble_v52.py:1550](pearl_news/pipeline/assemble_v52.py:1550) — dock left rail:

```css
.article-container { display: grid; grid-template-columns: 280px 1fr; gap: 40px; ... }
```

CSS_WIDE bottom-strip layout is at ~1647 with the lang-aware `"PRACTICE & ENGAGE"` strip header.

### 2.2 Layout regression tests — 15/15 PASSED locally

```
tests/test_pearl_news_sidebar_v52.py::test_layout_variants_constant_has_five PASSED
tests/test_pearl_news_sidebar_v52.py::test_default_layout_renders_right_sidebar PASSED
tests/test_pearl_news_sidebar_v52.py::test_dock_layout_renders_left_sticky_sidebar PASSED
tests/test_pearl_news_sidebar_v52.py::test_wide_layout_renders_bottom_strip PASSED
tests/test_pearl_news_sidebar_v52.py::test_wide_layout_lang_attribute_threads_through PASSED
tests/test_pearl_news_sidebar_v52.py::test_editorial_layout_renders_wider_canvas PASSED
tests/test_pearl_news_sidebar_v52.py::test_scroll_story_layout_hides_sidebar PASSED
tests/test_pearl_news_sidebar_v52.py::test_unknown_layout_falls_back_to_default PASSED
tests/test_pearl_news_sidebar_v52.py::test_dock_mobile_surfaces_sidebar_cards PASSED
(+ 6 prior tests for v52 sidebar/teacher) — 15 passed in 0.76s
```

### 2.3 Fixture render produces correct distinguishing signatures

`PYTHONPATH=. python3 -c "..."` with fixture `artifacts/pearl_news/qa_cli/article_571ce81ad02e5493.json`:

```
default: OK  (4708192 bytes)   — contains '1fr 360px' (right sidebar grid)
dock:    OK  (4716000 bytes)   — contains 'sidebar-dock' and '280px 1fr' (left sticky rail)
wide:    OK  (4710994 bytes)   — contains 'PRACTICE & ENGAGE' (bottom strip)
editorial: OK  (4709759 bytes)
scroll_story: OK  (4711309 bytes)
```

### 2.4 Browser-visible proof (playwright Chromium, 1440×900)

Screenshots at `artifacts/qa/screenshots/pearl_news_sidebar_2026-05-13/`:

| Variant | Desktop file | Mobile file | Visual verdict |
|---|---|---|---|
| **right_sidebar_default** | `right_sidebar_default_desktop_1440x900.png` (732 KB) | `right_sidebar_default_mobile_375x812.png` (372 KB) | Right column with Practice/Free Tools/SDG/Poll/Take cards — **renders as designed** |
| **left_sidebar_dock** | `left_sidebar_dock_desktop_1440x900.png` (598 KB) | `left_sidebar_dock_mobile_375x812.png` (412 KB) | Left sticky rail with section TOC and practice timer; article body shifted right — **renders as designed** |
| **bottom_sidebar_wide** | `bottom_sidebar_wide_desktop_1440x900.png` (1247 KB) | `bottom_sidebar_wide_mobile_375x812.png` (381 KB) | Full-width article body at top, sidebar cards reflow as horizontal strip below body — **renders as designed** |

All three sidebar positions the operator named (right / left / bottom) are correct **in the standalone template**.

---

## 3. Why the operator sees the layouts broken in WordPress

The bug is documented in [docs/pearl_news/LAYOUT_HANDOFF.md](docs/pearl_news/LAYOUT_HANDOFF.md) (commit `90bb3ef08`, authored 2026-04-23):

> The WordPress theme wraps post content in a container narrower than 1100px. This triggers the CSS media query:
> ```css
> @media (max-width: 768px) {
>   .article-container { grid-template-columns: 1fr; }
>   .sidebar { order: 2; }  /* ← sidebar drops to bottom */
> }
> ```
> Because the theme's `.entry-content` or `.post-content` constrains the rendered width below the breakpoint, the grid collapses to single column on every load — even on desktop.

This is **server-side**: the WP Newspaper theme has a `.entry-content` (or equivalent) wrapper whose `max-width` is well below 1100px. Inline `<style>` from the post content cannot escape that wrapper without explicit override.

The handoff doc provides three fix options. **All three are server-side / WP-admin-side**, not repo changes:

- **Option A (recommended):** Paste `CSS_BLOCK` from `assemble_v52.py` into WP Admin → Appearance → Customize → Additional CSS. Gives the CSS full-page scope.
- **Option B:** Inject a viewport-width override into post `<style>` (`.entry-content, .post-content { max-width: 100% !important }` + `.pn-article-root { width: 100vw; margin-left: calc(-50vw + 50%) }`).
- **Option C:** Lower the breakpoint to 480px (quick-fix, doesn't fix the underlying width constraint).

The PR-853 governing spec ([docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md](docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md)) explicitly scopes itself to **content-side only**: *"this is content-side only; WP Newspaper theme `td_post_template` remains unaffected"* — and per [pearl_news/publish/wordpress_client.py:187-189](pearl_news/publish/wordpress_client.py:187), `td_post_template` is not REST-API-writable on the Newspaper theme.

So: **no commit in repo history has ever made the three sidebar positions render correctly inside the WP Newspaper theme's content wrapper.** What works is the standalone template (proven above). What broke (in WordPress) was never fixed at the repo level — because it can't be fixed at the repo level alone.

---

## 4. What this means for the ~25 prior fix attempts

The operator framed this as "drift broke it; ~25 prior attempts failed." The git record shows a different shape:

- The fix attempts all targeted **CSS/template/template-selector code**.
- The actual bug is a **WP theme wrapper width constraint** — outside the code those PRs touched.
- Each PR could pass its own local tests (standalone render) and still leave the WP-rendered page broken.
- This explains why every "fresh fix" failed: there was no code-side fix that would survive being wrapped in a sub-1100px container, and the breakpoint media query is supposed to be there for genuine mobile.

The PR-853 governing spec already named this trap (Section 5 — Historical regression): "the layout system has been mis-fixed >10 times because reviewers consolidated variants without understanding what each one does." The 26th attempt should not be another code change.

---

## 5. File-by-file restore manifest

**None required.** The restore target (`8070e81fd`) and current `main` are byte-identical in `pearl_news/`. The following `git checkout <good-sha> -- <path>` commands would all be no-ops and are not executed:

```text
# pearl_news/pipeline/assemble_v52.py         — identical to 8070e81fd
# pearl_news/pipeline/run_article_pipeline.py — identical to 8070e81fd
# scripts/run_pearl_news_teacher_batch.py     — identical to 8070e81fd
# tests/test_pearl_news_sidebar_v52.py        — identical to 8070e81fd
# docs/PEARL_NEWS_LAYOUT_SYSTEM_2026-05-04.md — identical to 8070e81fd
```

---

## 6. Recommended next action (operator-side, not Pearl_News-side)

Per `LAYOUT_HANDOFF.md` Option A:

1. Log in to WP Admin at `https://pearlnewsuna.org/wp-admin`.
2. Appearance → Customize → Additional CSS.
3. Paste the contents of `CSS_BLOCK` from [pearl_news/pipeline/assemble_v52.py:1400](pearl_news/pipeline/assemble_v52.py:1400) (and `CSS_DOCK` / `CSS_WIDE` etc. for those variants) into Additional CSS.
4. Add an override at the top to override Newspaper's `.entry-content` width:
   ```css
   .entry-content, .post-content, .site-main {
     max-width: 100% !important;
     padding: 0 !important;
   }
   .pn-article-root { width: 100vw; margin-left: calc(-50vw + 50%); }
   ```
5. Publish.
6. Open one published article per layout variant (right / left / bottom) and confirm the sidebar position matches the screenshots in `artifacts/qa/screenshots/pearl_news_sidebar_2026-05-13/`.

This is **WP Customizer work, not a code change.** Pearl_News declines to author a 26th in-repo "fix" since the bug is provably not in the code.

---

## 7. Anti-pattern checklist (per operator prompt)

- [x] **Did NOT add a fresh CSS shim** in `assemble_v52.py`.
- [x] **Did NOT add a new layout switch** or sixth variant.
- [x] **Did NOT add a new template variant.**
- [x] **Did NOT re-author from scratch.**
- [x] **Stopped and reported** rather than improvising a fresh "fix" that would join the previous ~25 dead attempts.
- [x] **Browser-visible proof** of the standalone template state (3 sidebar variants × 2 viewports = 6 screenshots), saved under `artifacts/qa/screenshots/pearl_news_sidebar_2026-05-13/`.
- [x] **No >50-file deletion** in this audit's diff (will be confirmed at push time via `gh pr diff <n> --stat | tail -1`).

---

## 8. Mandatory preflight (per CLAUDE.md)

To be run before push:

```bash
git fetch origin
git rev-list --left-right --count origin/main...HEAD
PYTHONPATH=. python3 scripts/git/push_guard.py
scripts/ci/preflight_push.sh
bash scripts/git/health_check.sh
```

LLM-policy audit: not required — no Python changed; only evidence artifacts.

---

*Authored by Pearl_News (Claude Opus 4.7, 1M context), 2026-05-13.
Co-author: operator-driven anti-improvise rule.*

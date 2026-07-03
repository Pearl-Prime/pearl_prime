#!/usr/bin/env python3
"""Story-authored entry gate — no series renders without an authored script.

The listing-as-story kill. Prior manga sessions conflated a *series_plan* YAML
(catalog metadata — a listing) with an *authored chapter_script* (the actual
panel-by-panel story text), and dispatched renders for cells that had only a
plan. This gate is the entry precondition to the render queue: a (series,
episode) may not be rendered unless a chapter_script exists that (a) is a real
`chapter_script_writer_handoff`, (b) has >= the panel floor of real panels, and
(c) carries no unfilled stub markers.

Reuses the genuine substance primitives from the bestseller gate — the
`_STUB_RE` placeholder/TODO detector and the `_MIN_PANELS` floor — but at the
ENTRY threshold, not the bestseller-quality threshold. The full bestseller gate
adds print-page-count and closing-hook rules that are webtoon-incompatible
(a vertical-scroll episode is legitimately one page of 35 panels) and belong to
the pro-bar lane (roadmap M6), not to render entry. Entry only asks: is there an
authored story here, or just a plan/stub?

Two roles, one file:
  - `assert_story_authored(path)` / `check_series_episode(series, ep)` — import
    into the render dispatch as the enqueue-time precondition.
  - CLI — enqueue-time single check (`--series … --episode …`), single-file
    check (`--chapter-script …`), or PR scan of changed chapter_scripts
    (`--base origin/main`).

Run:
    # enqueue-time precondition (the roadmap exit proof — plan-only → non-zero):
    PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py \\
        --series stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying \\
        --episode ep_001
    # PR scan of changed chapter_scripts:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_story_authored.py \\
        --base origin/main --head HEAD

Exit: 0 authored; 1 not-authored / thin / stubbed (named reason).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root for phoenix_v4 import
sys.path.insert(0, str(Path(__file__).resolve().parent))       # scripts/ci for drift_detector_git
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

# Substance primitives are REUSED from the bestseller gate when phoenix_v4 is
# importable (readiness runner, render-dispatch precondition). The Drift
# detectors CI job is deliberately dependency-light (no phoenix_v4 deps), so we
# fall back to inline mirrors of the SAME constants — kept byte-identical to
# phoenix_v4/manga/qc/bestseller_gate.py; if you change them there, change them
# here (a test asserts they match when phoenix_v4 is available).
try:
    from phoenix_v4.manga.qc._script_shape import iter_panels  # noqa: F401
    from phoenix_v4.manga.qc.bestseller_gate import _MIN_PANELS, _STUB_RE
except Exception:  # pragma: no cover - exercised only in the light CI env
    _MIN_PANELS = 6
    _STUB_RE = re.compile(
        r"\{[a-z_]+\}"
        r"|\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b"
        r"|\bHOOK\b|\bPLACEHOLDER\b|\bLOREM IPSUM\b|\bCHAPTER_END_HOOK\b",
        re.IGNORECASE,
    )

    def iter_panels(chapter_script: Mapping[str, Any]):
        chapters = chapter_script.get("chapters")
        pages: list = []
        if isinstance(chapters, list) and chapters:
            for ch in chapters:
                if isinstance(ch, dict):
                    pages.extend(ch.get("pages") or [])
        else:
            pages = chapter_script.get("pages") or []
        for page in pages:
            if isinstance(page, dict):
                for panel in page.get("panels") or []:
                    if isinstance(panel, dict):
                        yield panel

REPO_ROOT = repo_root_from_script(Path(__file__))
CHAPTER_SCRIPTS_DIR = "artifacts/manga/chapter_scripts"
_HANDOFF_TYPE = "chapter_script_writer_handoff"


class StoryNotAuthoredError(Exception):
    """Raised when a (series, episode) cannot enter the render queue."""


def _locale_values(v: Any) -> str:
    """Flatten a *_by_locale dict (or plain str) to one text blob."""
    if isinstance(v, dict):
        return " ".join(str(x) for x in v.values() if x)
    return str(v or "")


def panel_authored_text(panel: Mapping[str, Any]) -> str:
    """All reader-facing + art-direction text of a panel across the real
    chapter_script schema (scene / narrator_caption_by_locale / dialogue_lines
    text_by_locale) AND the older narration/caption/dialogue schema."""
    parts: list[str] = [str(panel.get("scene") or "")]
    parts.append(_locale_values(panel.get("narrator_caption_by_locale")))
    parts.append(_locale_values(panel.get("sfx_by_locale")))
    for line in panel.get("dialogue_lines") or []:
        if isinstance(line, dict):
            parts.append(_locale_values(line.get("text_by_locale")))
            parts.append(str(line.get("text") or ""))
    # older schema fallthrough
    for key in ("narration", "caption", "action", "description"):
        if panel.get(key):
            parts.append(str(panel[key]))
    dlg = panel.get("dialogue")
    if isinstance(dlg, list):
        for d in dlg:
            parts.append(str(d.get("text") if isinstance(d, dict) else d or ""))
    return " ".join(p for p in parts if p.strip())


def evaluate_authored(chapter_script: Mapping[str, Any]) -> tuple[bool, str]:
    """Return (authored_ok, reason). reason is '' on pass."""
    if chapter_script.get("artifact_type") != _HANDOFF_TYPE:
        return False, (f"artifact_type is {chapter_script.get('artifact_type')!r}, "
                       f"not {_HANDOFF_TYPE!r} — this is a plan/listing, not an "
                       f"authored script")
    panels = list(iter_panels(chapter_script))
    real = [p for p in panels if panel_authored_text(p).strip()]
    if len(real) < _MIN_PANELS:
        return False, (f"only {len(real)} authored panel(s) (need >= {_MIN_PANELS}); "
                       f"{len(panels)} total panel slots — plan skeleton, not a story")
    blob = "\n".join(panel_authored_text(p) for p in real)
    m = _STUB_RE.search(blob)
    if m:
        return False, f"unfilled stub marker {m.group(0)!r} in panel text"
    return True, ""


def assert_story_authored(chapter_script_path: Path) -> None:
    """Raise StoryNotAuthoredError unless the path is an authored, non-stub
    chapter_script above the entry floor. Import this into the render dispatch."""
    if not chapter_script_path.is_file():
        raise StoryNotAuthoredError(
            f"no chapter_script at {chapter_script_path} — a series_plan is a "
            f"listing, not a story; author the script before rendering")
    import yaml  # lazy: only needed when a script actually exists to parse
    try:
        data = yaml.safe_load(chapter_script_path.read_text())
    except yaml.YAMLError as e:
        raise StoryNotAuthoredError(f"{chapter_script_path}: unparseable YAML: {e}")
    if not isinstance(data, dict):
        raise StoryNotAuthoredError(f"{chapter_script_path}: not a mapping")
    ok, reason = evaluate_authored(data)
    if not ok:
        raise StoryNotAuthoredError(f"{chapter_script_path}: {reason}")


def resolve_chapter_script(repo_root: Path, series_id: str, episode_id: str) -> Path:
    return repo_root / CHAPTER_SCRIPTS_DIR / series_id / f"{episode_id}.yaml"


def check_series_episode(repo_root: Path, series_id: str, episode_id: str) -> tuple[bool, str]:
    path = resolve_chapter_script(repo_root, series_id, episode_id)
    try:
        assert_story_authored(path)
        return True, ""
    except StoryNotAuthoredError as e:
        return False, str(e)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Story-authored render-entry gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--series", default=None, help="series_id (enqueue-time check)")
    ap.add_argument("--episode", default=None, help="episode_id e.g. ep_001")
    ap.add_argument("--chapter-script", type=Path, default=None,
                    help="explicit chapter_script path")
    ap.add_argument("--base", default=None, help="git base ref (scan changed scripts)")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--paths", nargs="*", default=None, help="explicit paths (tests)")
    args = ap.parse_args(argv)

    # Mode 1: single enqueue-time check
    if args.series and args.episode:
        ok, reason = check_series_episode(args.repo_root, args.series, args.episode)
        if ok:
            print(f"STORY-AUTHORED: PASS ({args.series} {args.episode})", file=sys.stderr)
            return 0
        print(f"RENDER BLOCKED: {reason}", file=sys.stderr)
        return 1

    # Mode 2: single explicit file
    if args.chapter_script:
        try:
            assert_story_authored(args.chapter_script)
            print(f"STORY-AUTHORED: PASS ({args.chapter_script})", file=sys.stderr)
            return 0
        except StoryNotAuthoredError as e:
            print(f"RENDER BLOCKED: {e}", file=sys.stderr)
            return 1

    # Mode 3: scan changed / explicit chapter_scripts
    if args.paths is not None:
        targets = list(args.paths)
    elif args.base:
        targets = [p for p in changed_paths(args.base, args.head, args.repo_root)
                   if p.startswith(CHAPTER_SCRIPTS_DIR) and p.endswith(".yaml")]
    else:
        targets = []
    failures: list[str] = []
    for rel in sorted(set(targets)):
        try:
            assert_story_authored(args.repo_root / rel)
        except StoryNotAuthoredError as e:
            failures.append(str(e))
    if not failures:
        print(f"STORY-AUTHORED: PASS ({len(set(targets))} changed script(s))",
              file=sys.stderr)
        return 0
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    print(f"STORY-AUTHORED: {len(failures)} violation(s) — blocking", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

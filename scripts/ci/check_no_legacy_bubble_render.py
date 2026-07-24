#!/usr/bin/env python3
"""Drift detector: production paths must use bubble_render_v2, not legacy v1.

Genre-aware lettering lives in ``phoenix_v4.manga.chapter.bubble_render_v2``
(+ ``config/manga/genre_bubble_styles.yaml``). The legacy module
``bubble_render.py`` remains on disk for internal reuse by v2, but production
callers under ``scripts/`` and ``phoenix_v4/`` must not import it directly.

Allowlist:
  - ``phoenix_v4/manga/chapter/bubble_render_v2.py`` (imports v1 as helpers)
  - ``phoenix_v4/manga/chapter/bubble_render.py`` (the legacy module itself)
  - any path under ``tests/`` or matching ``*test*.py``

Ratchet (2026-07-24): six pre-v2 production callers are grandfathered in
``KNOWN_LEGACY_CALLERS`` — they predate bubble_render_v2 and are reported as
WARN, not FAIL, until the migration lane lands. Do NOT add new entries; new
legacy imports FAIL. Shrink this set as callers migrate to v2.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_no_legacy_bubble_render.py

Exit: 0 clean (grandfathered callers may WARN); 1 if any non-allowlisted,
non-grandfathered production file imports legacy bubble_render.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from drift_detector_git import repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))
SCAN_ROOTS = ("scripts", "phoenix_v4")

# Paths relative to repo root that may still import legacy bubble_render.
ALLOWLIST_FILES = {
    "phoenix_v4/manga/chapter/bubble_render_v2.py",
    "phoenix_v4/manga/chapter/bubble_render.py",
    "scripts/ci/check_no_legacy_bubble_render.py",
}

# Grandfathered pre-v2 production callers (ratchet baseline, 2026-07-24 —
# manga process uplift Lane 10). These predate bubble_render_v2 and WARN
# instead of FAIL. Do NOT add entries; migrate callers to v2 and delete rows.
KNOWN_LEGACY_CALLERS = {
    "phoenix_v4/manga/chapter/chapter_production.py",
    "scripts/manga/compose_episode_from_renders.py",
    "scripts/manga/ja_jp_phase1_smoke.py",
    "scripts/manga/ja_jp_phase2_bulk.py",
    "scripts/manga/render_episode_strip.py",
    "scripts/manga/run_bubble_compose_v31.py",
}

# Import forms that count as legacy production use.
_IMPORT_PATTERNS = (
    re.compile(
        r"from\s+phoenix_v4\.manga\.chapter\.bubble_render\s+import\b"
    ),
    re.compile(
        r"from\s+phoenix_v4\.manga\.chapter\s+import\s+bubble_render\b"
    ),
    re.compile(r"import\s+phoenix_v4\.manga\.chapter\.bubble_render\b"),
)


def _is_test_path(rel: str) -> bool:
    parts = Path(rel).parts
    if "tests" in parts:
        return True
    name = Path(rel).name
    return name.startswith("test_") or name.endswith("_test.py")


def _ast_imports_legacy(path: Path) -> list[str]:
    """Return human-readable import hits via AST (catches multi-line imports)."""
    hits: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "phoenix_v4.manga.chapter.bubble_render":
                names = ", ".join(a.name for a in node.names)
                hits.append(f"L{node.lineno}: from {mod} import {names}")
            elif mod == "phoenix_v4.manga.chapter":
                for alias in node.names:
                    if alias.name == "bubble_render":
                        hits.append(
                            f"L{node.lineno}: from {mod} import bubble_render"
                        )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "phoenix_v4.manga.chapter.bubble_render":
                    hits.append(f"L{node.lineno}: import {alias.name}")
    return hits


def scan() -> list[tuple[str, list[str]]]:
    violations: list[tuple[str, list[str]]] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel in ALLOWLIST_FILES or _is_test_path(rel):
                continue
            # Skip scripts/ci self-reference already allowlisted; also skip
            # any nested venv or __pycache__.
            if "__pycache__" in path.parts:
                continue
            hits = _ast_imports_legacy(path)
            if not hits:
                # Text fallback for dynamic/string forms that AST may miss.
                text = path.read_text(encoding="utf-8", errors="replace")
                for i, line in enumerate(text.splitlines(), 1):
                    if line.lstrip().startswith("#"):
                        continue
                    for pat in _IMPORT_PATTERNS:
                        if pat.search(line):
                            hits.append(f"L{i}: {line.strip()}")
                            break
            if hits:
                violations.append((rel, hits))
    return violations


def main() -> int:
    violations = scan()
    grandfathered = [(rel, hits) for rel, hits in violations if rel in KNOWN_LEGACY_CALLERS]
    new_violations = [(rel, hits) for rel, hits in violations if rel not in KNOWN_LEGACY_CALLERS]
    for rel, hits in grandfathered:
        print(f"WARN: grandfathered legacy bubble_render caller (migrate to v2): {rel}")
        for h in hits:
            print(f"    {h}")
    if not new_violations:
        print("PASS: no new production imports of legacy bubble_render "
              f"({len(grandfathered)} grandfathered WARN)")
        return 0
    print("FAIL: production paths still import legacy bubble_render.py")
    print("Use phoenix_v4.manga.chapter.bubble_render_v2 "
          "(render_bubbles_onto_panel_v2 / render_bubbles_on_panels_v2).")
    for rel, hits in new_violations:
        print(f"  {rel}")
        for h in hits:
            print(f"    {h}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

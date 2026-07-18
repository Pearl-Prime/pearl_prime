#!/usr/bin/env python3
"""Guard against manga-render overwrites of teacher_pics directories.

Background: PR #773 (commit 4ca81057d) inadvertently replaced multiple real
teacher photos under ``teacher_pics/`` and ``brand-wizard-app/public/teacher_pics/``
with 800x1000 manga-render PNGs cross-written from ``manga_covers/``.
Last-known-good SHA: ``c513ac18d`` (2026-04-26 backup; restored 2026-05-15).

This check is a binary tripwire. It fails CI if any PNG under the two guarded
directories matches the manga-render signature:

1. Exact dimensions 800x1000 (the standard FLUX/ComfyUI manga output size for
   this repo). Real teacher photos are camera-shot at varied real-world
   resolutions and never collide with this exact pair.
2. PNG iTXt/tEXt metadata contains generative-AI provenance keys
   (``parameters``, ``prompt``, ``Comfy``, ``ComfyUI``, ``workflow``). Real
   camera photos do not carry these keys.

Cross-reference: ``~/.claude/.../memory/project_known_good_anchors.md`` ->
"Teacher real photos" section.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, UnidentifiedImageError
    from PIL.PngImagePlugin import PngImageFile
except ImportError as exc:  # pragma: no cover - environment misconfiguration
    sys.stderr.write(
        f"Pillow not installed ({exc}); install with `pip install Pillow` before running.\n"
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[2]
GUARDED_DIRS: tuple[Path, ...] = (
    REPO_ROOT / "teacher_pics",
    REPO_ROOT / "brand-wizard-app" / "public" / "teacher_pics",
)
MANGA_DIMS: tuple[int, int] = (800, 1000)
METADATA_AI_KEYS: tuple[str, ...] = (
    "parameters",
    "prompt",
    "Comfy",
    "ComfyUI",
    "workflow",
)
RESTORE_SHA: str = "c513ac18d"


_LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def is_lfs_pointer(path: Path) -> bool:
    """True if ``path`` is a git-LFS pointer file (object not pulled locally)."""
    try:
        # LFS pointers are < ~200 bytes. Real PNGs start with the 8-byte
        # PNG signature, not the LFS spec URL.
        if path.stat().st_size > 1024:
            return False
        with path.open("rb") as fh:
            head = fh.read(len(_LFS_POINTER_PREFIX))
        return head == _LFS_POINTER_PREFIX
    except OSError:
        return False


def check_file(path: Path) -> tuple[list[str], bool]:
    """Return ``(drift_messages, was_lfs_pointer)`` for ``path``.

    ``drift_messages`` is empty when the file is clean. ``was_lfs_pointer``
    is True if the file was a git-LFS pointer (object not pulled in this
    environment) — the check is then a no-op and the caller should WARN
    rather than fail (real protection lives in pre-commit / dev environments
    where LFS objects are available).
    """
    if is_lfs_pointer(path):
        return [], True
    issues: list[str] = []
    try:
        with Image.open(path) as img:
            img.load()
            size = img.size
            info_keys = {str(k) for k in (img.info or {}).keys()}
            is_png = isinstance(img, PngImageFile)
    except (UnidentifiedImageError, OSError) as exc:
        issues.append(f"unreadable image: {exc}")
        return issues, False

    if size == MANGA_DIMS:
        issues.append(
            f"dimensions {size[0]}x{size[1]} match manga-render signature "
            "(real photos are varied camera resolutions)"
        )

    if is_png:
        ai_keys_found = sorted(
            {key for key in info_keys if key.lower() in {k.lower() for k in METADATA_AI_KEYS}}
        )
        if ai_keys_found:
            issues.append(
                "PNG metadata contains generative-AI keys: "
                + ", ".join(f"'{k}'" for k in ai_keys_found)
                + " (real camera photos do not carry these)"
            )

    return issues, False


def iter_targets(dirs: Iterable[Path]) -> Iterable[Path]:
    for guard_dir in dirs:
        if not guard_dir.is_dir():
            continue
        for png in sorted(guard_dir.glob("*.png")):
            yield png


def main(argv: list[str]) -> int:
    failures: list[tuple[str, str]] = []
    pointer_skipped: list[str] = []
    seen = 0

    for png in iter_targets(GUARDED_DIRS):
        seen += 1
        issues, was_pointer = check_file(png)
        rel = str(png.relative_to(REPO_ROOT))
        if was_pointer:
            pointer_skipped.append(rel)
            continue
        for issue in issues:
            failures.append((rel, issue))

    if seen == 0:
        print(
            "WARN: no PNGs found in any guarded teacher_pics directory; "
            "check repo layout."
        )
        return 0

    if failures:
        print(
            f"FAIL: {len(failures)} drift signal(s) across {seen} files "
            f"in {len(GUARDED_DIRS)} guarded directories.\n"
        )
        for rel_path, issue in failures:
            print(f"  - {rel_path}: {issue}")
        print()
        print("Restore recipe (last-known-good SHA = {sha}):".format(sha=RESTORE_SHA))
        print(
            f"    git checkout {RESTORE_SHA} -- "
            "teacher_pics/ brand-wizard-app/public/teacher_pics/"
        )
        print(
            "    git lfs pull --include="
            "'teacher_pics/*,brand-wizard-app/public/teacher_pics/*'"
        )
        print(
            "See ~/.claude/.../memory/project_known_good_anchors.md "
            "(Teacher real photos) for the drift autopsy."
        )
        return 1

    if pointer_skipped:
        print(
            f"WARN: {len(pointer_skipped)} of {seen} files are git-LFS pointers "
            f"(objects not pulled in this environment); drift check skipped "
            f"for those. Run locally with `git lfs pull` for full coverage."
        )
        checked = seen - len(pointer_skipped)
        if checked > 0:
            print(f"OK: {checked} non-pointer photos clean.")
        return 0

    print(
        f"OK: {seen} teacher photos clean across {len(GUARDED_DIRS)} guarded directories."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

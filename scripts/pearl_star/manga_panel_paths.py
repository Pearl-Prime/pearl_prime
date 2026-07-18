"""Pearl Star–writable paths for manga panel PNG output.

The t2i worker runs as ``pearl-star``; operator repo trees under
``/home/ahjan108/phoenix_omega/`` are not writable. All queue dispatches map
repo-relative panel paths into ``PS_MANGA_OUT_ROOT`` (default
``/var/lib/pearl-star/manga_out/``) so renders land without PermissionError.

Spec: PEARL_STAR_JOB_QUEUE_V1_SPEC.md §4.7; OPD-20260629-003.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_DEFAULT_MANGA_OUT = "/var/lib/pearl-star/manga_out"
_DEFAULT_PS_REPO = "/home/ahjan108/phoenix_omega"


def manga_out_root() -> Path:
    return Path(os.environ.get("PS_MANGA_OUT_ROOT", _DEFAULT_MANGA_OUT))


def phoenix_repo_on_star() -> Path:
    return Path(os.environ.get("PS_PHOENIX_REPO", _DEFAULT_PS_REPO))


def local_phoenix_repo() -> Path:
    return Path(os.environ.get("PS_LOCAL_REPO", str(REPO_ROOT)))


def _linux_dest_path(path: Path) -> Path:
    """Normalize a Pearl Star destination path for Linux (no macOS /private/var leak).

    Mac clients resolve ``/var`` → ``/private/var`` via ``Path.resolve()``; Pearl
    Star Linux has no ``/private/var``.  Strip that prefix when present.
    """
    s = os.path.normpath(str(path))
    if s.startswith("/private/var/"):
        s = "/var/" + s[len("/private/var/") :]
    elif s == "/private/var":
        s = "/var"
    return Path(s)


def _join_pearl_star_path(base: Path, *parts: str) -> Path:
    """Join Pearl Star Linux paths without ``Path.resolve()`` (avoids /var symlink)."""
    joined = base
    for part in parts:
        joined = joined / part
    return _linux_dest_path(joined)


def pearl_star_writable_dest(out_path: Path) -> Path:
    """Map a panel output path to a pearl-star-owned destination on Pearl Star."""
    out_resolved = out_path.resolve()
    root = manga_out_root()  # Linux path — never .resolve() (macOS /var → /private/var)
    for base in (local_phoenix_repo(), phoenix_repo_on_star()):
        try:
            rel = out_resolved.relative_to(base.resolve())
            return _join_pearl_star_path(root, *rel.parts)
        except ValueError:
            continue
    # Already under manga_out or an explicit absolute outside the repo.
    try:
        out_resolved.relative_to(_linux_dest_path(root))
        return _linux_dest_path(out_resolved)
    except ValueError:
        return _join_pearl_star_path(root, out_resolved.name)


def pearl_star_dest_path(out_path: Path) -> str:
    """String dest_path for Procrastinate payload (queue_panel_renders contract)."""
    return str(pearl_star_writable_dest(out_path))

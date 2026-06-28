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


def pearl_star_writable_dest(out_path: Path) -> Path:
    """Map a panel output path to a pearl-star-owned destination on Pearl Star."""
    out_path = out_path.resolve()
    root = manga_out_root()
    for base in (local_phoenix_repo(), phoenix_repo_on_star()):
        try:
            rel = out_path.relative_to(base.resolve())
            return (root / rel).resolve()
        except ValueError:
            continue
    # Already under manga_out or an explicit absolute outside the repo.
    try:
        out_path.relative_to(root.resolve())
        return out_path
    except ValueError:
        return root / out_path.name


def pearl_star_dest_path(out_path: Path) -> str:
    """String dest_path for Procrastinate payload (queue_panel_renders contract)."""
    return str(pearl_star_writable_dest(out_path))

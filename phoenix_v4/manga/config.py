"""Config loaders for the manga kernel."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = REPO_ROOT / "config" / "manga"
STYLE_ARCHETYPES_PATH = CONFIG_ROOT / "style_archetypes.yaml"
PANEL_LAYOUTS_PATH = CONFIG_ROOT / "panel_layouts.yaml"
MANGA_GATES_PATH = CONFIG_ROOT / "manga_gates.yaml"
SEED_ATOMS_PATH = CONFIG_ROOT / "teaching_library" / "atoms" / "seed_atoms.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for manga config loading.")
    if not path.exists():
        raise FileNotFoundError(f"Manga config not found: {path}")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=None)
def load_style_archetypes(path: Path | None = None) -> dict[str, dict[str, str]]:
    data = _load_yaml(path or STYLE_ARCHETYPES_PATH)
    return dict(data.get("style_archetypes") or {})


@lru_cache(maxsize=None)
def load_panel_layouts(path: Path | None = None) -> dict[str, dict[str, Any]]:
    data = _load_yaml(path or PANEL_LAYOUTS_PATH)
    return dict(data.get("atom_panel_map") or {})


@lru_cache(maxsize=None)
def load_manga_gates(path: Path | None = None) -> dict[str, Any]:
    return _load_yaml(path or MANGA_GATES_PATH)


@lru_cache(maxsize=None)
def load_seed_atoms(path: Path | None = None) -> dict[str, dict[str, Any]]:
    data = _load_yaml(path or SEED_ATOMS_PATH)
    atoms = data.get("atoms") or []
    return {str(atom["atom_id"]): dict(atom) for atom in atoms if atom.get("atom_id")}

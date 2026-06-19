"""Story strategy loader — loads genre-specific manga story structure templates.

Reads ``config/source_of_truth/manga_story_strategies/{genre}_strategies.yaml``
and applies deterministic SHA-256 hash-seeded selection to choose one strategy
and one variant per layer.

The selection algorithm mirrors ``_deterministic_int`` from ``story_architect.py``
so that the same (series_id, arc_id, genre) always produces the same output.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

_REPO_ROOT: Path | None = None
_STRATEGY_CACHE: dict[str, dict] = {}


def _repo_root() -> Path:
    global _REPO_ROOT
    if _REPO_ROOT is None:
        _REPO_ROOT = Path(__file__).resolve().parents[2]
    return _REPO_ROOT


def _h(seed: str, n: int) -> int:
    """Stable integer in [0, n) from a seed string."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max(1, n)


def _load_strategies_yaml(genre: str) -> dict[str, Any]:
    """Load (and cache) the genre strategies YAML file."""
    if genre in _STRATEGY_CACHE:
        return _STRATEGY_CACHE[genre]

    root = _repo_root()
    p = root / "config" / "source_of_truth" / "manga_story_strategies" / f"{genre}_strategies.yaml"
    if not p.is_file():
        return {}

    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML required to load story strategies") from e

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    _STRATEGY_CACHE[genre] = data
    return data


def _load_combinatorial_index() -> dict[str, Any]:
    """Load the combinatorial index (anti-pattern rules, seed formula)."""
    root = _repo_root()
    p = root / "config" / "source_of_truth" / "manga_story_strategies" / "combinatorial_index.yaml"
    if not p.is_file():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _normalise_genre(raw: str) -> str:
    return (
        raw.lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("ō", "o")
        .replace("ū", "u")
        .replace("shōnen", "shonen")
        .replace("shōjo", "shojo")
        .replace("seinen", "seinen")
    )


def list_available_genres() -> list[str]:
    """Return genres for which a strategies YAML file exists."""
    root = _repo_root()
    d = root / "config" / "source_of_truth" / "manga_story_strategies"
    if not d.is_dir():
        return []
    return [
        p.stem.replace("_strategies", "")
        for p in sorted(d.glob("*_strategies.yaml"))
    ]


def resolve_topic_strategy(genre: str, topic: str) -> str | None:
    """Return the strategy_id a genre maps a topic to (``topic_strategy_map``).

    Lets the embedding map drive which device carries an inner state — e.g.
    mecha + ``burnout`` -> the failing-chassis strategy. Returns ``None`` when
    the genre/topic pairing is unmapped (caller falls back to hash selection).
    """
    if not topic:
        return None
    data = _load_strategies_yaml(_normalise_genre(genre))
    mapping = data.get("topic_strategy_map") or {}
    if isinstance(mapping, dict):
        sid = mapping.get(topic) or mapping.get(_normalise_genre(topic))
        return str(sid) if sid else None
    return None


def load_story_strategy(
    genre: str,
    *,
    strategy_id: str | None = None,
    series_id: str = "",
    arc_id: str = "",
) -> dict[str, Any]:
    """Load a story strategy for the given genre.

    If ``strategy_id`` is provided, return that specific strategy.
    Otherwise, select deterministically using ``hash(series_id + arc_id + genre)``.

    Returns a dict with keys:
      - ``strategy_id``  — the selected strategy's key name
      - ``strategy``     — the full strategy dict (all 5 layers)
      - ``genre``
      - ``seed``         — the seed used for selection
      - ``available_strategies`` — list of all strategy key names in this genre

    Returns an empty dict if the genre is not found.
    """
    genre_norm = _normalise_genre(genre)
    data = _load_strategies_yaml(genre_norm)

    strategies: dict[str, Any] = data.get("strategies") or {}
    if not strategies:
        return {}

    strategy_keys = list(strategies.keys())
    seed = f"{series_id}:{arc_id}:{genre_norm}"

    if strategy_id is not None:
        if strategy_id not in strategies:
            raise KeyError(f"Strategy '{strategy_id}' not found for genre '{genre_norm}'. "
                           f"Available: {strategy_keys}")
        chosen_key = strategy_id
    else:
        chosen_key = strategy_keys[_h(seed + ":strategy", len(strategy_keys))]

    return {
        "strategy_id": chosen_key,
        "strategy": dict(strategies[chosen_key]),
        "genre": genre_norm,
        "seed": seed,
        "available_strategies": strategy_keys,
    }


def select_layer_variants(
    strategy_data: dict[str, Any],
    *,
    series_id: str = "",
    arc_id: str = "",
    genre: str = "",
    layer_count: int = 5,
) -> dict[str, Any]:
    """Pick one variant per layer from the strategy, hash-seeded.

    Each layer key is ``layer_N_variants`` (a list) or ``layer_N_plot`` etc.
    Falls back to the full layer dict when no explicit variants list exists.

    Returns a dict mapping ``layer_1`` … ``layer_N`` → selected variant.
    """
    strategy = strategy_data.get("strategy") or strategy_data
    seed = strategy_data.get("seed") or f"{series_id}:{arc_id}:{genre}"
    selected: dict[str, Any] = {}

    for i in range(1, layer_count + 1):
        # Try layer_i_variants list first
        variants_key = f"layer_{i}_variants"
        if variants_key in strategy and isinstance(strategy[variants_key], list):
            variants = strategy[variants_key]
        else:
            # Use the full layer dict as a single "variant"
            layer_keys = [
                f"layer_{i}_plot", f"layer_{i}_emotional",
                f"layer_{i}_dialogue", f"layer_{i}_visual", f"layer_{i}_pacing",
            ]
            found = next((strategy[k] for k in layer_keys if k in strategy), None)
            variants = [found] if found is not None else [{}]

        idx = _h(seed + f":layer{i}", len(variants)) if len(variants) > 1 else 0
        selected[f"layer_{i}"] = variants[idx]

    return selected


def check_anti_patterns(
    genre: str,
    strategy_id: str,
    layer_selection: dict[str, Any],
) -> list[str]:
    """Check selected layers against anti-pattern rules.

    Returns a list of violation descriptions (empty = clean).
    """
    idx = _load_combinatorial_index()
    violations: list[str] = []

    cross_rules = list(idx.get("cross_genre_anti_patterns") or [])
    genre_rules: list[dict[str, Any]] = []

    genre_norm = _normalise_genre(genre)
    genre_data = _load_strategies_yaml(genre_norm)
    genre_rules = list(genre_data.get("anti_pattern_rules") or [])

    for rule in cross_rules + genre_rules:
        forbidden = rule.get("forbidden_combination") or rule.get("forbidden") or []
        reason = rule.get("reason") or ""
        if not isinstance(forbidden, list):
            continue
        # Simple keyword match: if all keywords appear in strategy_id or layer repr
        layer_repr = str(strategy_id) + " " + str(layer_selection)
        match = all(str(kw).lower() in layer_repr.lower() for kw in forbidden if kw != "any_genre")
        if match:
            violations.append(reason)

    return violations


def get_combinatorial_count(genre: str) -> int:
    """Return the documented number of unique combinations for the genre."""
    idx = _load_combinatorial_index()
    counts = idx.get("combinations_per_genre") or {}
    genre_norm = _normalise_genre(genre)
    val = counts.get(genre_norm)
    if isinstance(val, dict):
        return int(val.get("total_combinations") or 0)
    return int(val or 0)

"""Modern-reader story relevance doctrine for manga generation."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DOCTRINE = REPO / "config" / "manga" / "modern_reader_story_doctrine.yaml"
DEFAULT_CANONICAL = REPO / "config" / "manga" / "canonical_genre_list.yaml"

_CACHE: dict[str, Any] | None = None


class ModernReaderDoctrineError(RuntimeError):
    """Raised when modern-reader story doctrine is missing or malformed."""


def _normalise(raw: str) -> str:
    return (raw or "").strip().lower().replace("-", "_").replace(" ", "_")


def _h(seed: str, n: int) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max(1, n)


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ModernReaderDoctrineError("PyYAML required for modern reader doctrine")
    if not path.is_file():
        raise ModernReaderDoctrineError(f"modern reader doctrine not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_modern_reader_doctrine(path: Path | None = None) -> dict[str, Any]:
    """Load the modern-reader story doctrine YAML."""
    global _CACHE
    if path is None and _CACHE is not None:
        return _CACHE
    doc = _load_yaml(path or DEFAULT_DOCTRINE)
    if path is None:
        _CACHE = doc
    return doc


def canonical_genre_ids(path: Path = DEFAULT_CANONICAL) -> list[str]:
    doc = _load_yaml(path)
    return [
        str(row["id"])
        for row in doc.get("genres") or []
        if row.get("must_include") and row.get("alias_of") is None
    ]


def resolve_relevance_genre(
    genre_id: str,
    *,
    strategy_genre: str | None = None,
    doctrine: dict[str, Any] | None = None,
) -> str:
    """Resolve a runtime genre/strategy id to a canonical relevance row."""
    doc = doctrine or load_modern_reader_doctrine()
    genres = doc.get("genres") or {}
    aliases = {_normalise(k): _normalise(v) for k, v in (doc.get("aliases") or {}).items()}

    for candidate in (_normalise(genre_id), _normalise(strategy_genre or "")):
        if not candidate:
            continue
        if candidate in genres:
            return candidate
        if aliases.get(candidate) in genres:
            return aliases[candidate]
    return _normalise(genre_id)


def validate_modern_reader_doctrine(
    doctrine: dict[str, Any] | None = None,
    *,
    canonical_path: Path = DEFAULT_CANONICAL,
) -> list[str]:
    """Return validation errors; empty list means PASS."""
    doc = doctrine or load_modern_reader_doctrine()
    errors: list[str] = []
    if doc.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")

    markets = doc.get("reader_markets") or {}
    for key in ("en_US", "ja_JP", "zh_CN", "fr_FR"):
        row = markets.get(key)
        if not isinstance(row, dict):
            errors.append(f"missing reader market {key}")
            continue
        if not row.get("surface_rule"):
            errors.append(f"{key}: surface_rule required")
        if not row.get("ordinary_touchpoints"):
            errors.append(f"{key}: ordinary_touchpoints required")

    audiences = doc.get("audiences") or {}
    for key in ("gen_z", "gen_alpha"):
        row = audiences.get(key)
        if not isinstance(row, dict):
            errors.append(f"missing audience {key}")
            continue
        if not row.get("story_rule"):
            errors.append(f"{key}: story_rule required")
        if not row.get("touchpoints"):
            errors.append(f"{key}: touchpoints required")

    expected = set(canonical_genre_ids(canonical_path))
    genres = doc.get("genres") or {}
    actual = set(str(k) for k in genres)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"missing canonical genre rows: {missing}")
    if extra:
        errors.append(f"unknown genre rows: {extra}")

    for genre_id, row in genres.items():
        if not isinstance(row, dict):
            errors.append(f"{genre_id}: row must be mapping")
            continue
        if not row.get("relevance_rule"):
            errors.append(f"{genre_id}: relevance_rule required")
        catalysts = row.get("catalysts")
        if not isinstance(catalysts, list) or not catalysts:
            errors.append(f"{genre_id}: catalysts required")
            continue
        seen_ids: set[str] = set()
        for catalyst in catalysts:
            if not isinstance(catalyst, dict):
                errors.append(f"{genre_id}: catalyst must be mapping")
                continue
            cid = str(catalyst.get("id") or "")
            if not cid:
                errors.append(f"{genre_id}: catalyst.id required")
            if cid in seen_ids:
                errors.append(f"{genre_id}: duplicate catalyst id {cid}")
            seen_ids.add(cid)
            for key in ("logline", "ordinary_world_objects", "genre_transmutation", "avoid"):
                if not catalyst.get(key):
                    errors.append(f"{genre_id}.{cid}: {key} required")

    return errors


def build_modern_reader_context(
    *,
    genre_id: str,
    strategy_genre: str | None = None,
    topic: str = "",
    series_id: str = "",
    arc_id: str = "",
    target_market: str = "en_US",
    target_audience: str = "gen_z",
    doctrine: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select a deterministic modern-reader catalyst for a story run."""
    doc = doctrine or load_modern_reader_doctrine()
    errors = validate_modern_reader_doctrine(doc)
    if errors:
        raise ModernReaderDoctrineError("; ".join(errors))

    markets = doc["reader_markets"]
    audiences = doc["audiences"]
    market_key = target_market if target_market in markets else "en_US"
    audience_key = target_audience if target_audience in audiences else "gen_z"
    relevance_genre = resolve_relevance_genre(
        genre_id, strategy_genre=strategy_genre, doctrine=doc,
    )
    genre_row = doc["genres"].get(relevance_genre)
    if not isinstance(genre_row, dict):
        raise ModernReaderDoctrineError(
            f"no modern reader genre row for {genre_id!r} "
            f"(strategy {strategy_genre!r}, resolved {relevance_genre!r})"
        )

    catalysts = genre_row["catalysts"]
    seed = ":".join(
        [
            str(series_id),
            str(arc_id),
            str(genre_id),
            str(strategy_genre or ""),
            str(topic),
            market_key,
            audience_key,
        ]
    )
    catalyst = dict(catalysts[_h(seed + ":modern_catalyst", len(catalysts))])
    market = markets[market_key]
    audience = audiences[audience_key]
    craft_directive = (
        f"Fuse the genre engine with a contemporary reader-world entrypoint. "
        f"Market={market_key}; audience={audience_key}. "
        f"Use catalyst '{catalyst['id']}': {catalyst['logline']} "
        f"Transmutation: {catalyst['genre_transmutation']} "
        f"Market surface: {market['surface_rule']} "
        f"Audience rule: {audience['story_rule']} "
        "Use concrete objects and social pressure on page one; do not name-drop trends."
    )

    return {
        "schema_version": doc["schema_version"],
        "target_market": market_key,
        "target_audience": audience_key,
        "genre_id": genre_id,
        "strategy_genre": strategy_genre,
        "relevance_genre": relevance_genre,
        "market_surface_rule": market["surface_rule"],
        "market_touchpoints": list(market.get("ordinary_touchpoints") or []),
        "market_guardrails": list(market.get("localization_guardrails") or []),
        "audience_story_rule": audience["story_rule"],
        "audience_touchpoints": list(audience.get("touchpoints") or []),
        "genre_relevance_rule": genre_row["relevance_rule"],
        "catalyst": catalyst,
        "quality_rubric": dict(doc.get("quality_rubric") or {}),
        "craft_directive": craft_directive,
    }

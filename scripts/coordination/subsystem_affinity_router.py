"""Deterministic subsystem routing from WRITE_SCOPE paths to review boards."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBSYSTEM_MAP_PATH = REPO_ROOT / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv"
AGENT_REGISTRY_PATH = REPO_ROOT / "config" / "agents" / "agent_registry.yaml"

MARKETING_SUBSYSTEMS = frozenset({"marketing"})
RESEARCH_SUBSYSTEMS = frozenset({"ei_v2", "trend_feeds", "recommendations"})
RESEARCH_PATH_MARKERS = ("/research/", "marketing_deep_research/", "phoenix_v4/quality/ei_v2/")


@dataclass(frozen=True)
class SubsystemRow:
    subsystem_id: str
    authority_docs: tuple[str, ...]
    config_paths: tuple[str, ...]
    owner_agent: str
    status: str


@dataclass
class ReviewBoard:
    owner: str
    reviewers: list[str] = field(default_factory=list)
    authority_docs: list[str] = field(default_factory=list)
    adjacent_subsystems: list[str] = field(default_factory=list)


def _normalize_path(path: str) -> str:
    cleaned = path.strip().replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned.lstrip("/")


def _split_semicolon(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(";") if part.strip())


@lru_cache(maxsize=1)
def load_subsystem_rows() -> tuple[SubsystemRow, ...]:
    rows: list[SubsystemRow] = []
    with SUBSYSTEM_MAP_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for raw in reader:
            rows.append(
                SubsystemRow(
                    subsystem_id=raw["subsystem_id"].strip(),
                    authority_docs=_split_semicolon(raw["authority_doc"]),
                    config_paths=_split_semicolon(raw["config_path"]),
                    owner_agent=raw["owner_agent"].strip(),
                    status=raw.get("status", "").strip(),
                )
            )
    return tuple(rows)


def _path_matches_config(path: str, config_entry: str) -> bool:
    norm_path = _normalize_path(path)
    norm_cfg = _normalize_path(config_entry)
    if not norm_cfg:
        return False
    if norm_cfg.endswith("/"):
        return norm_path == norm_cfg.rstrip("/") or norm_path.startswith(norm_cfg)
    if norm_path == norm_cfg:
        return True
    return norm_path.startswith(norm_cfg + "/")


def _match_score(path: str, config_entry: str) -> int:
    if not _path_matches_config(path, config_entry):
        return -1
    return len(_normalize_path(config_entry))


def get_subsystems_for_path(path: str) -> list[str]:
    """Return all subsystem_ids whose config_path matches path (best-first)."""
    scored: list[tuple[int, str, str]] = []
    for row in load_subsystem_rows():
        best = max((_match_score(path, cfg) for cfg in row.config_paths), default=-1)
        if best >= 0:
            scored.append((best, row.subsystem_id, row.subsystem_id))
    scored.sort(key=lambda item: (-item[0], item[1]))
    seen: set[str] = set()
    ordered: list[str] = []
    for _, sid, _ in scored:
        if sid not in seen:
            seen.add(sid)
            ordered.append(sid)
    return ordered


def get_subsystem_for_path(path: str) -> str | None:
    matches = get_subsystems_for_path(path)
    return matches[0] if matches else None


def _subsystem_row(subsystem_id: str) -> SubsystemRow | None:
    for row in load_subsystem_rows():
        if row.subsystem_id == subsystem_id:
            return row
    return None


def route_for_subsystem(subsystem_id: str) -> ReviewBoard:
    row = _subsystem_row(subsystem_id)
    if row is None:
        return ReviewBoard(owner="Pearl_Architect", reviewers=[], authority_docs=[], adjacent_subsystems=[])
    return ReviewBoard(
        owner=row.owner_agent,
        reviewers=[],
        authority_docs=list(row.authority_docs),
        adjacent_subsystems=[],
    )


def _dedupe_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def route_for_paths(paths: list[str]) -> ReviewBoard:
    subsystem_counts: dict[str, int] = {}
    for path in paths:
        for sid in get_subsystems_for_path(path):
            subsystem_counts[sid] = subsystem_counts.get(sid, 0) + 1

    if not subsystem_counts:
        return ReviewBoard(owner="Pearl_Architect", reviewers=[], authority_docs=[], adjacent_subsystems=[])

    ordered_subsystems = sorted(
        subsystem_counts.keys(),
        key=lambda sid: (-subsystem_counts[sid], sid),
    )
    primary = ordered_subsystems[0]
    primary_row = _subsystem_row(primary)
    owner = primary_row.owner_agent if primary_row else "Pearl_Architect"

    authority_docs: list[str] = []
    owners: list[str] = []
    for sid in ordered_subsystems:
        row = _subsystem_row(sid)
        if row is None:
            continue
        authority_docs.extend(row.authority_docs)
        owners.append(row.owner_agent)

    reviewers = _dedupe_preserve(agent for agent in owners if agent != owner)
    adjacent = ordered_subsystems[1:]

    return ReviewBoard(
        owner=owner,
        reviewers=reviewers,
        authority_docs=_dedupe_preserve(authority_docs),
        adjacent_subsystems=adjacent,
    )


def marketing_or_research_touched(paths: list[str]) -> bool:
    for path in paths:
        norm = _normalize_path(path)
        subsystems = get_subsystems_for_path(path)
        if any(sid in MARKETING_SUBSYSTEMS for sid in subsystems):
            return True
        if any(sid in RESEARCH_SUBSYSTEMS for sid in subsystems):
            return True
        if any(marker in norm for marker in RESEARCH_PATH_MARKERS):
            return True
    return False


def load_agent_display_names() -> dict[str, str]:
    if yaml is None or not AGENT_REGISTRY_PATH.is_file():
        return {}
    data = yaml.safe_load(AGENT_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    agents = data.get("agents") or {}
    out: dict[str, str] = {}
    for key, payload in agents.items():
        if isinstance(payload, dict):
            out[key] = payload.get("display_name") or key
    return out

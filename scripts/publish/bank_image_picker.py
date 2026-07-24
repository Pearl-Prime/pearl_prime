#!/usr/bin/env python3
"""Deterministic, licensed, topic-matched cover image selection.

Storyblocks is the only production provider. Legacy banks are available only
under an explicit QA escape hatch and are never silently selected.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from scripts.storyblocks.consumer_guard import assert_storyblocks_licensed_for_consumer
from scripts.storyblocks.license_store import DEFAULT_INDEX_PATH, LicenseStore

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TOPIC_MAP = REPO_ROOT / "config/publishing/storyblocks_cover_topic_map.yaml"


class CoverBankPickError(RuntimeError):
    """No safe, licensed, on-topic cover image is available."""


@dataclass(frozen=True)
class CoverImagePick:
    path: Path
    topic: str
    provider: str
    stock_id: str
    work_unit_id: str
    attribution_label: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def load_topic_map(path: Path = DEFAULT_TOPIC_MAP) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("topics"), dict):
        raise CoverBankPickError(f"Invalid cover topic map: {path}")
    return data


def _tokens(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    return " ".join(str(value or "").lower().replace("_", " ").split())


def validate_candidate(row: dict[str, Any], topic: str, topic_map: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    policy = topic_map.get("policy") or {}
    rule = (topic_map.get("topics") or {}).get(topic)
    if rule is None:
        return [f"unknown canonical topic: {topic}"]
    meta = row.get("metadata") or {}
    if str(row.get("source_provider", "")).lower() != "storyblocks": reasons.append("provider is not storyblocks")
    if row.get("media_type") != policy.get("required_media_type", "image"): reasons.append("media_type is not image")
    if row.get("surface") != policy.get("required_surface", "cover"): reasons.append("surface is not cover")
    topic_keys = {_tokens(x).replace(" ", "_") for x in meta.get("topic_keys", [])}
    if topic not in topic_keys: reasons.append(f"metadata.topic_keys lacks exact topic {topic}")
    if policy.get("require_topic_verified", True) and meta.get("topic_verified") is not True: reasons.append("metadata.topic_verified is not true")
    # NOTE: intentionally excludes metadata.keywords/topic_keys from the haystack.
    # Those fields are mechanical tags already checked above (topic_keys exact-match);
    # folding them into the positive-cue haystack would make this check vacuous for
    # any candidate that is merely tagged with the topic name, defeating its purpose
    # of requiring genuine descriptive (title/description/free-text tag) evidence of
    # topic relevance as a second, independent fail-closed signal.
    haystack = _tokens([meta.get("title"), meta.get("description"), meta.get("tags")])
    positives = [_tokens(x) for x in rule.get("positive", [])]
    excluded = [_tokens(x) for x in rule.get("exclude", [])]
    if not any(term and term in haystack for term in positives): reasons.append("descriptive metadata has no topic-positive cue")
    hits = [term for term in excluded if term and term in haystack]
    if hits: reasons.append("excluded cue(s): " + ", ".join(hits))
    path = Path(str(row.get("local_uri") or ""))
    if not path.is_file(): reasons.append("licensed local image is missing")
    return reasons


def read_index(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        try: rows.append(json.loads(line))
        except json.JSONDecodeError as exc: raise CoverBankPickError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
    return rows


def pick_image(topic: str, *, seed: str = "", index_path: Path = DEFAULT_INDEX_PATH,
               topic_map_path: Path = DEFAULT_TOPIC_MAP, license_store: LicenseStore | None = None,
               allow_legacy_bank: bool = False, legacy_candidates: Iterable[dict[str, Any]] = ()) -> CoverImagePick:
    """Pick a licensed Storyblocks cover deterministically or fail closed."""
    topic_map = load_topic_map(topic_map_path)
    if topic not in topic_map["topics"]:
        raise CoverBankPickError(f"Unknown canonical cover topic: {topic}")
    store = license_store or LicenseStore(index_path=index_path)
    valid: list[dict[str, Any]] = []
    for row in read_index(index_path):
        if validate_candidate(row, topic, topic_map): continue
        assert_storyblocks_licensed_for_consumer(row, work_unit_id=row.get("work_unit_id"), license_store=store)
        valid.append(row)
    if valid:
        chosen = min(valid, key=lambda r: hashlib.sha256(f"{seed}|{topic}|{r.get('storyblocks_stock_id')}".encode()).hexdigest())
        return CoverImagePick(Path(chosen["local_uri"]), topic, "storyblocks", str(chosen["storyblocks_stock_id"]),
                              str(chosen["work_unit_id"]), str(chosen.get("attribution_label") or "Stock media via Storyblocks"), chosen.get("metadata") or {})
    legacy_enabled = allow_legacy_bank or os.getenv("COVER_ALLOW_LEGACY_BANK") == "1"
    if legacy_enabled:
        for row in legacy_candidates:
            if topic in row.get("topic_keys", []) and row.get("topic_verified") is True and Path(str(row.get("path"))).is_file():
                return CoverImagePick(Path(row["path"]), topic, "legacy", str(row.get("asset_id", "legacy")), "qa-only", str(row.get("attribution_label", "")), row)
    raise CoverBankPickError(f"No licensed, topic-verified Storyblocks cover image for {topic}; production fallback is disabled")

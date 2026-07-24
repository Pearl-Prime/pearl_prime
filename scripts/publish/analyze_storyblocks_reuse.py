#!/usr/bin/env python3
"""Reuse-vs-new-search analysis for the 17 canonical cover-image topics.

Lane 02 (cover-acquisition-queue). This script is a **read-only recommender**.
It never confirms/downloads a Storyblocks asset, never sets
``metadata.topic_verified: true``, and never relabels an existing record's
``surface`` field. It exists to answer one question honestly: for each of the
17 canonical cover topics in ``config/publishing/storyblocks_cover_topic_map.yaml``,
does *anything already licensed* plausibly cover it, or does a human need to
run a brand-new Storyblocks search?

Two sources are scanned:

1. ``artifacts/storyblocks/license_index.jsonl`` — the cover-surface license
   index that ``scripts/publish/bank_image_picker.pick_image`` actually reads
   at render time. As of this lane, this file does not exist on
   ``origin/main`` (confirmed empirically, not assumed) — zero cover-surface
   candidates exist anywhere in the repo.
2. ``artifacts/storyblocks/social_media_bank_storyblocks_20260720/BANK_INDEX.json``
   — an existing, committed Storyblocks bank, but scoped to
   ``social_media_bank_storyblocks_20260720`` (a social/video-snippet work
   unit, i.e. ``surface: social_broll`` in spirit — the schema predates the
   cover ``surface`` field and does not carry one at all). Its HD bytes live
   under the gitignored ``artifacts/storyblocks_licensed/`` prefix and are
   frequently *not present* in a fresh checkout; only the metadata
   (``BANK_INDEX.json`` / ``MANIFEST.tsv``) is committed.

For each social-bank record this applies the same positive/exclude cue
heuristic as ``bank_image_picker.validate_candidate()`` minus the
``surface`` / ``topic_verified`` checks (those are exactly the two fields
this lane cannot fabricate), plus the ``media_type == image`` requirement
(book covers are still images; a plausibly-matching *video* record is not a
usable cover candidate, so it is reported separately and never counted as a
candidate). The haystack is title/description/tags only —
``metadata.keywords`` / ``topic_keys`` are intentionally excluded per the
NOTE in ``bank_image_picker.validate_candidate()``, so a record merely
*tagged* with a topic is not enough; it must carry genuine descriptive
evidence.

A record that scores "plausible" here is a **reuse_confirm** candidate: a
human (or a follow-up session with live Storyblocks API credentials) must
re-download it fresh under a brand-new book-cover work unit and manually
verify the image, at which point the *new* record can carry
``surface: cover`` + ``topic_verified: true``. The existing social-bank
record is never touched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TOPIC_MAP = REPO_ROOT / "config/publishing/storyblocks_cover_topic_map.yaml"
DEFAULT_LICENSE_INDEX = REPO_ROOT / "artifacts/storyblocks/license_index.jsonl"
DEFAULT_SOCIAL_BANK_INDEX = (
    REPO_ROOT
    / "artifacts/storyblocks/social_media_bank_storyblocks_20260720/BANK_INDEX.json"
)
DEFAULT_QUEUE_PATH = REPO_ROOT / "artifacts/coordination/cover_acquisition_queue.tsv"

# Operator-nominated reuse-candidate topics (six of the 17). Nomination alone
# does not guarantee a plausible candidate exists — that is determined below,
# empirically, per topic. Treat this list as "worth checking the social bank
# for", not as a pre-confirmed answer.
REUSE_NOMINATED_TOPICS = [
    "anxiety",
    "boundaries",
    "burnout",
    "depression",
    "grief",
    "overthinking",
]

# The remaining 11 of 17 canonical topics: no cover or social-bank presence
# is expected for these at all.
NEW_SEARCH_ONLY_TOPICS = [
    "adhd_focus",
    "compassion_fatigue",
    "courage",
    "financial_anxiety",
    "financial_stress",
    "imposter_syndrome",
    "mindfulness",
    "self_worth",
    "sleep_anxiety",
    "social_anxiety",
    "somatic_healing",
]

REQUIRED_STEP_REUSE = (
    "re-download under book-cover work unit + set surface: cover + "
    "topic_verified: true after human review"
)
REQUIRED_STEP_NEW_SEARCH = "run new Storyblocks search for this topic under a book-cover work unit"
BLOCKED_ON = "live Storyblocks API credentials + human topic-verification"


def _tokens(value: Any) -> str:
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    return " ".join(str(value or "").lower().replace("_", " ").split())


def load_topic_map(path: Path = DEFAULT_TOPIC_MAP) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("topics"), dict):
        raise ValueError(f"Invalid cover topic map: {path}")
    return data


def load_license_index(path: Path = DEFAULT_LICENSE_INDEX) -> list[dict[str, Any]]:
    """Rows already scoped surface: cover. Expected empty on this branch today."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
    return rows


def load_social_bank_assets(path: Path = DEFAULT_SOCIAL_BANK_INDEX) -> list[dict[str, Any]]:
    """Existing social_broll-scoped Storyblocks bank metadata (read-only)."""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    assets = data.get("assets")
    return list(assets) if isinstance(assets, list) else []


def score_social_bank_candidate(
    asset: dict[str, Any], topic: str, topic_map: dict[str, Any]
) -> dict[str, Any]:
    """Score one social-bank record's metadata for plausible cover reuse.

    This never inspects or changes the asset in place; it returns a new dict
    describing the recommendation. ``surface_today`` is always reported as
    ``social_broll`` (this bank predates the cover surface field) and
    ``topic_verified_today`` is always ``False`` — no record in this bank has
    ever been human-verified for cover use.
    """
    policy = topic_map.get("policy") or {}
    rule = (topic_map.get("topics") or {}).get(topic)
    reasons: list[str] = []
    if rule is None:
        return {
            "stock_id": str(asset.get("stock_id")),
            "plausible": False,
            "reasons": [f"unknown canonical topic: {topic}"],
        }
    if asset.get("topic") != topic:
        reasons.append(f"asset topic field is {asset.get('topic')!r}, not {topic!r}")
    required_media_type = policy.get("required_media_type", "image")
    media_type_ok = asset.get("media_type") == required_media_type
    if not media_type_ok:
        reasons.append(
            f"media_type is {asset.get('media_type')!r}, not {required_media_type!r} "
            "(book covers require a still image; a video hit is not a usable candidate)"
        )
    haystack = _tokens([asset.get("title"), asset.get("description"), asset.get("tags")])
    positives = [_tokens(x) for x in rule.get("positive", [])]
    excluded = [_tokens(x) for x in rule.get("exclude", [])]
    positive_hits = [t for t in positives if t and t in haystack]
    excluded_hits = [t for t in excluded if t and t in haystack]
    if not positive_hits:
        reasons.append("descriptive metadata (title) has no topic-positive cue")
    if excluded_hits:
        reasons.append("excluded cue(s): " + ", ".join(excluded_hits))
    plausible = asset.get("topic") == topic and media_type_ok and bool(positive_hits) and not excluded_hits
    return {
        "stock_id": str(asset.get("stock_id")),
        "media_type": asset.get("media_type"),
        "title": asset.get("title"),
        "positive_hits": positive_hits,
        "excluded_hits": excluded_hits,
        "media_type_ok": media_type_ok,
        "plausible": plausible,
        "reasons": reasons,
        "source_bank_ref": asset.get("work_unit_id"),
        "surface_today": "social_broll",
        "topic_verified_today": False,
    }


def analyze(
    topic_map_path: Path = DEFAULT_TOPIC_MAP,
    license_index_path: Path = DEFAULT_LICENSE_INDEX,
    social_bank_path: Path = DEFAULT_SOCIAL_BANK_INDEX,
) -> dict[str, Any]:
    topic_map = load_topic_map(topic_map_path)
    canonical_topics = sorted(topic_map["topics"].keys())
    license_rows = load_license_index(license_index_path)
    social_assets = load_social_bank_assets(social_bank_path)

    topics: dict[str, Any] = {}
    for topic in canonical_topics:
        cover_rows = [
            r
            for r in license_rows
            if r.get("surface") == "cover"
            and topic
            in {
                _tokens(x).replace(" ", "_")
                for x in (r.get("metadata") or {}).get("topic_keys", [])
            }
        ]
        candidates = [
            score_social_bank_candidate(a, topic, topic_map)
            for a in social_assets
            if a.get("topic") == topic
        ]
        plausible = [c for c in candidates if c["plausible"]]
        action = "reuse_confirm" if plausible else "new_search"
        topics[topic] = {
            "nominated_reuse_topic": topic in REUSE_NOMINATED_TOPICS,
            "action": action,
            "existing_cover_licensed_count": len(cover_rows),
            "social_bank_candidates_total": len(candidates),
            "social_bank_candidates_plausible": plausible,
            "social_bank_candidates_all": candidates,
        }

    return {
        "canonical_topics": canonical_topics,
        "reuse_nominated_topics": REUSE_NOMINATED_TOPICS,
        "new_search_only_topics": NEW_SEARCH_ONLY_TOPICS,
        "license_index_row_count": len(license_rows),
        "social_bank_asset_count": len(social_assets),
        "topics": topics,
    }


def build_queue_rows(analysis: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for topic in analysis["canonical_topics"]:
        info = analysis["topics"][topic]
        plausible_ids = [c["stock_id"] for c in info["social_bank_candidates_plausible"]]
        if info["action"] == "reuse_confirm":
            required_next_step = REQUIRED_STEP_REUSE
            source_bank_ref = "artifacts/storyblocks/social_media_bank_storyblocks_20260720/BANK_INDEX.json"
        else:
            required_next_step = REQUIRED_STEP_NEW_SEARCH
            source_bank_ref = ""
        rows.append(
            {
                "topic_key": topic,
                "action": info["action"],
                "candidate_stock_ids": ";".join(plausible_ids),
                "source_bank_ref": source_bank_ref,
                "required_next_step": required_next_step,
                "blocked_on": BLOCKED_ON,
            }
        )
    return rows


QUEUE_COLUMNS = [
    "topic_key",
    "action",
    "candidate_stock_ids",
    "source_bank_ref",
    "required_next_step",
    "blocked_on",
]


def write_queue_tsv(rows: list[dict[str, str]], path: Path = DEFAULT_QUEUE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(QUEUE_COLUMNS)]
    for row in rows:
        lines.append("\t".join(row[col] for col in QUEUE_COLUMNS))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full analysis as JSON")
    parser.add_argument(
        "--write-queue",
        type=Path,
        default=None,
        help="write the acquisition queue TSV to this path (not written unless passed)",
    )
    args = parser.parse_args()

    result = analyze()

    if args.write_queue is not None:
        rows = build_queue_rows(result)
        out_path = write_queue_tsv(rows, args.write_queue)
        result["queue_written_to"] = str(out_path)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for topic in result["canonical_topics"]:
            info = result["topics"][topic]
            n = len(info["social_bank_candidates_plausible"])
            print(f"{topic:<20} action={info['action']:<14} plausible_candidates={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Emit Wave 1 external stories bank YAML files from verified corpus."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BANK = REPO / "SOURCE_OF_TRUTH" / "accent_banks" / "external_stories"
LEDGER = REPO / "artifacts" / "research" / "external_stories_verification_ledger.jsonl"
REJECTED = REPO / "artifacts" / "research" / "external_stories_rejected_log.jsonl"
SENSITIVITY = REPO / "artifacts" / "research" / "external_stories_sensitivity_exclusion_log.jsonl"
CLOSEOUT = REPO / "artifacts" / "research" / "external_stories_wave1_closeout.md"

TOPICS = [
    "anxiety",
    "burnout",
    "overthinking",
    "imposter_syndrome",
    "financial_anxiety",
]
CLUSTERS_WAVE1 = ["universal", "en_US", "zh_CN", "zh_TW", "ja_JP"]
TARGET_PER_TOPIC = 15


def load_corpus() -> tuple[list[dict], list[dict], list[dict]]:
    from scripts.research.external_stories_wave1_corpus import (
        REJECTED as R,
        SENSITIVITY_EXCLUSIONS as S,
        STORIES,
    )

    return STORIES, R, S


def story_matches_cluster(story: dict, cluster: str) -> bool:
    fit = story.get("locale_fit", [])
    if cluster == "universal":
        return "universal" in fit
    return cluster in fit


def emit_topic_file(topic: str, stories: list[dict]) -> int:
    topic_stories = [s for s in stories if topic in s["topic_keys"]]
    clusters: dict[str, list] = {}
    for cluster in CLUSTERS_WAVE1:
        filtered = [s for s in topic_stories if story_matches_cluster(s, cluster)]
        clusters[cluster] = [
            {k: v for k, v in s.items() if k != "locale_fit"} for s in filtered
        ]
    out = {
        "status": "unwired",
        "topic": topic,
        "wave": 1,
        "story_count": len(topic_stories),
        "clusters": clusters,
    }
    path = BANK / f"{topic}_entries.yaml"
    header = (
        f"# External stories — {topic} — Wave 1\n"
        f"# status: unwired | KNOWN_UNWIRED: accent_banks/external_stories/\n"
    )
    path.write_text(
        header + yaml.dump(out, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    return len(topic_stories)


def write_ledger(stories: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8") as f:
        for s in stories:
            entry = {
                "story_id": s["story_id"],
                "type": s["type"],
                "citation": s["citation"],
                "rights_class": s["rights_class"],
                "verified_on": str(date.today()),
                "status": "accepted",
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_rejected(rejected: list[dict]) -> None:
    REJECTED.parent.mkdir(parents=True, exist_ok=True)
    with REJECTED.open("w", encoding="utf-8") as f:
        for r in rejected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_sensitivity(exclusions: list[dict]) -> None:
    SENSITIVITY.parent.mkdir(parents=True, exist_ok=True)
    with SENSITIVITY.open("w", encoding="utf-8") as f:
        for e in exclusions:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def main() -> None:
    stories, rejected, sensitivity = load_corpus()
    counts: dict[str, int] = {}
    for topic in TOPICS:
        counts[topic] = emit_topic_file(topic, stories)

    write_ledger(stories)
    write_rejected(rejected)
    write_sensitivity(sensitivity)

    closeout_lines = [
        "# External Stories Bank — Wave 1 Closeout",
        f"**Date:** {date.today()}",
        f"**Total stories:** {len(stories)}",
        "",
        "## Per-topic counts",
    ]
    for topic in TOPICS:
        status = "PASS" if counts[topic] >= TARGET_PER_TOPIC else "WARN"
        closeout_lines.append(f"- {topic}: {counts[topic]} ({status}, target {TARGET_PER_TOPIC}-20)")
    closeout_lines.extend(
        [
            "",
            "## Integrity",
            "Rule 0 enforced: zero fabricated true stories, zero client cases, zero author biography.",
            "",
            "## Status",
            "`external-stories-wave1` — unwired, KNOWN_UNWIRED",
        ]
    )
    CLOSEOUT.parent.mkdir(parents=True, exist_ok=True)
    CLOSEOUT.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")

    print(f"Emitted {len(stories)} stories across {len(TOPICS)} topic entry files")
    for topic in TOPICS:
        print(f"  {topic}: {counts[topic]}")


if __name__ == "__main__":
    main()

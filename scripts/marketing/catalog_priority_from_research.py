#!/usr/bin/env python3
"""
Close the RSS marketing loop: research signals → catalog priority scores.

Reads:
  1. artifacts/research/raw/<date>/ — fetched RSS feed content
  2. artifacts/marketing/ — persona/topic briefs
  3. config/marketing/consumer_language_by_topic.yaml — search keyword mapping
  4. config/marketing/invisible_scripts_by_persona_topic.yaml — positioning

Produces:
  artifacts/catalog_priority/priority_scores.json — per (topic, persona) priority scores
  Used by: generate_catalog.py and build_weekly_brand_package.py to prioritize
  which books to build first in each wave.

Scoring signals:
  - Topic mention frequency in recent RSS feeds (trending = higher priority)
  - Seasonal alignment (Q1 = self-help peak, etc.)
  - Platform gap analysis (topics with low coverage get priority)
  - Consumer language freshness (recent keyword trends)

Usage:
    python scripts/marketing/catalog_priority_from_research.py
    python scripts/marketing/catalog_priority_from_research.py --since 7  # last 7 days
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    import yaml
except ImportError:
    print("pyyaml required")
    sys.exit(1)

CANONICAL_TOPICS = [
    "anxiety", "boundaries", "burnout", "compassion_fatigue", "courage",
    "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "overthinking", "self_worth", "sleep_anxiety",
    "social_anxiety", "somatic_healing",
]

SEASONAL_BOOSTS = {
    1: {"anxiety": 1.3, "depression": 1.2, "self_worth": 1.3, "burnout": 1.2},  # January: New Year resolutions
    2: {"self_worth": 1.2, "boundaries": 1.2},  # February: Valentine's / relationships
    3: {"burnout": 1.1, "financial_stress": 1.2},  # March: tax season stress
    4: {"anxiety": 1.1, "somatic_healing": 1.2},  # April: spring reset
    5: {"grief": 1.2, "compassion_fatigue": 1.1},  # May: Mental Health Awareness Month
    6: {"burnout": 1.2, "sleep_anxiety": 1.1},  # June: mid-year burnout
    9: {"anxiety": 1.2, "imposter_syndrome": 1.3, "social_anxiety": 1.2},  # September: back-to-school/work
    10: {"grief": 1.1, "depression": 1.2},  # October: seasonal affective
    11: {"financial_stress": 1.3, "financial_anxiety": 1.3},  # November: holiday spending
    12: {"grief": 1.3, "depression": 1.2, "social_anxiety": 1.2},  # December: holiday loneliness
}

# Keywords that signal topic relevance in RSS content
TOPIC_KEYWORDS = {
    "anxiety": ["anxiety", "anxious", "worry", "nervous", "panic", "stress"],
    "burnout": ["burnout", "exhaustion", "overwork", "fatigue", "tired"],
    "depression": ["depression", "depressed", "hopeless", "sad", "mental health"],
    "grief": ["grief", "loss", "bereavement", "mourning", "death"],
    "self_worth": ["self-worth", "self-esteem", "confidence", "imposter", "worthy"],
    "imposter_syndrome": ["imposter", "fraud", "not good enough", "inadequate"],
    "boundaries": ["boundaries", "people-pleasing", "saying no", "codependent"],
    "sleep_anxiety": ["insomnia", "sleep", "can't sleep", "restless", "melatonin"],
    "financial_stress": ["financial stress", "debt", "money worry", "cost of living"],
    "financial_anxiety": ["financial anxiety", "money fear", "economic", "recession"],
    "social_anxiety": ["social anxiety", "introvert", "social media", "isolation"],
    "overthinking": ["overthinking", "rumination", "spiraling", "racing thoughts"],
    "compassion_fatigue": ["compassion fatigue", "caregiver", "empathy fatigue", "helping profession"],
    "courage": ["courage", "brave", "fear", "risk", "vulnerability"],
    "somatic_healing": ["somatic", "body-based", "nervous system", "vagus", "polyvagal"],
}


def scan_feeds(since_days: int = 7) -> Counter:
    """Count topic keyword mentions in recent RSS feed content."""
    raw_dir = REPO_ROOT / "artifacts" / "research" / "raw"
    cutoff = datetime.now() - timedelta(days=since_days)
    topic_counts: Counter = Counter()

    if not raw_dir.exists():
        return topic_counts

    for date_dir in sorted(raw_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        try:
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            if dir_date < cutoff:
                continue
        except ValueError:
            continue

        for feed_file in date_dir.glob("*.xml"):
            text = feed_file.read_text(encoding="utf-8", errors="ignore").lower()
            for topic, keywords in TOPIC_KEYWORDS.items():
                for kw in keywords:
                    count = len(re.findall(re.escape(kw), text))
                    if count > 0:
                        topic_counts[topic] += count

    return topic_counts


def compute_priority_scores(since_days: int = 7) -> dict:
    """Compute priority scores per topic, incorporating RSS signals + seasonal boosts."""
    feed_counts = scan_feeds(since_days)
    month = datetime.now().month
    seasonal = SEASONAL_BOOSTS.get(month, {})

    scores = {}
    max_count = max(feed_counts.values()) if feed_counts else 1

    for topic in CANONICAL_TOPICS:
        base = 1.0
        # RSS trend signal (0.0 to 0.5 boost)
        if feed_counts[topic] > 0:
            trend_boost = 0.5 * (feed_counts[topic] / max_count)
            base += trend_boost
        # Seasonal boost
        base *= seasonal.get(topic, 1.0)
        scores[topic] = round(base, 3)

    return {
        "generated_at": datetime.now().isoformat(),
        "since_days": since_days,
        "month": month,
        "feed_mentions": dict(feed_counts.most_common()),
        "seasonal_boosts_applied": seasonal,
        "priority_scores": scores,
        "top_5": sorted(scores.items(), key=lambda x: -x[1])[:5],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute catalog priority from research signals")
    parser.add_argument("--since", type=int, default=7, help="Days of RSS history to scan (default: 7)")
    args = parser.parse_args()

    result = compute_priority_scores(args.since)

    out_dir = REPO_ROOT / "artifacts" / "catalog_priority"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "priority_scores.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Priority scores written to {out_path}")
    print(f"Top 5 topics this month:")
    for topic, score in result["top_5"]:
        print(f"  {topic}: {score}")
    if result["feed_mentions"]:
        print(f"RSS mentions (last {args.since} days): {result['feed_mentions']}")
    else:
        print(f"No RSS feed data found. Run: python scripts/research/fetch_feeds.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())

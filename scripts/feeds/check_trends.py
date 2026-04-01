#!/usr/bin/env python3
"""
Pearl_Int — Google Trends Checker via SerpApi.
Checks keyword tiers against Google Trends. Budget-guarded.

Usage:
  python scripts/feeds/check_trends.py              # run today's tiers
  python scripts/feeds/check_trends.py --tier 1     # run tier 1 only
  python scripts/feeds/check_trends.py --dry-run    # show what would be checked
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.feeds.budget_guard import BudgetGuard

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


CONFIG_DIR = REPO_ROOT / "config" / "trend_keywords"


def get_serpapi_key() -> Optional[str]:
    """Get SerpApi key from env."""
    key = os.getenv("SERPAPI_KEY")
    if not key:
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("SERPAPI_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key


def serpapi_google_trends(keywords: list[str], api_key: str, date: str = "today 3-m") -> Optional[dict]:
    """Call SerpApi Google Trends engine. Returns JSON response or None on error."""
    q = ",".join(keywords[:5])  # max 5 per call
    params = {
        "engine": "google_trends",
        "q": q,
        "data_type": "TIMESERIES",
        "date": date,
        "api_key": api_key,
    }
    url = f"https://serpapi.com/search?{urlencode(params)}"
    try:
        req = Request(url, headers={"User-Agent": "PearlInt/1.0"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  [ERROR] SerpApi call failed: {e}")
        return None


def extract_trend_data(response: dict, keywords: list[str]) -> list[dict]:
    """Extract interest-over-time data from SerpApi response."""
    results = []
    interest = response.get("interest_over_time", {})
    timeline = interest.get("timeline_data", [])
    if not timeline:
        return results

    for i, kw in enumerate(keywords):
        values = []
        for point in timeline:
            val_list = point.get("values", [])
            if i < len(val_list):
                raw = val_list[i].get("extracted_value", 0)
                values.append(raw)

        if not values:
            continue

        recent_7d = values[-7:] if len(values) >= 7 else values
        prev_7d = values[-14:-7] if len(values) >= 14 else values[:len(values)//2]

        avg_recent = sum(recent_7d) / len(recent_7d) if recent_7d else 0
        avg_prev = sum(prev_7d) / len(prev_7d) if prev_7d else 0
        pct_change = ((avg_recent - avg_prev) / avg_prev * 100) if avg_prev > 0 else 0

        results.append({
            "keyword": kw,
            "current_interest": round(avg_recent, 1),
            "prev_interest": round(avg_prev, 1),
            "pct_change_7d": round(pct_change, 1),
            "spike": pct_change > 20,
            "max_interest": max(values) if values else 0,
            "min_interest": min(values) if values else 0,
            "data_points": len(values),
        })

    return results


def get_tier1_keywords() -> list[str]:
    """Load tier 1 primary keywords."""
    data = _load_yaml(CONFIG_DIR / "tier1_primaries.yaml")
    return [e["keyword"] for e in data.get("keywords", []) if isinstance(e, dict) and "keyword" in e]


def get_tier2_keywords_for_today(now: Optional[datetime] = None) -> list[str]:
    """Load today's rotation batch from tier 2 (UTC ``now`` defaults to real clock)."""
    now = now or datetime.now(timezone.utc)
    data = _load_yaml(CONFIG_DIR / "tier2_rotation.yaml")
    keywords = [e["keyword"] for e in data.get("keywords", []) if isinstance(e, dict) and "keyword" in e]
    rotation_size = data.get("rotation_size", 5)
    day_of_year = now.timetuple().tm_yday
    start = (day_of_year * rotation_size) % len(keywords) if keywords else 0
    return keywords[start:start + rotation_size] if keywords else []


def get_tier3_keywords_for_today(now: Optional[datetime] = None) -> list[str]:
    """Load today's persona keywords from tier 3 (UTC ``now`` defaults to real clock)."""
    now = now or datetime.now(timezone.utc)
    data = _load_yaml(CONFIG_DIR / "tier3_persona.yaml")
    groups = data.get("persona_groups", {})
    all_groups = list(groups.values())
    if not all_groups:
        return []
    rotation_size = data.get("rotation_size", 2)
    day_of_year = now.timetuple().tm_yday
    group_idx = day_of_year % len(all_groups)
    group = all_groups[group_idx]
    keywords = group.get("keywords", [])[:rotation_size]
    return keywords


def load_tier4_schedule() -> dict:
    """Tier 4 weekday and batch metadata from config (not prose docs)."""
    data = _load_yaml(CONFIG_DIR / "tier4_emerging.yaml")
    return {
        "check_day": str(data.get("check_day") or "sunday").lower(),
        "batch_size": int(data.get("batch_size") or 10),
        "keyword_count": len(
            [e for e in data.get("keywords", []) if isinstance(e, dict) and e.get("keyword")]
        ),
    }


def get_tier4_keywords_at(now: Optional[datetime] = None) -> list[str]:
    """Tier 4 emerging keywords only on ``check_day`` from tier4_emerging.yaml (UTC)."""
    now = now or datetime.now(timezone.utc)
    data = _load_yaml(CONFIG_DIR / "tier4_emerging.yaml")
    check_day = str(data.get("check_day") or "sunday").lower()
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if day_names[now.weekday()] != check_day:
        return []
    return [e["keyword"] for e in data.get("keywords", []) if isinstance(e, dict) and "keyword" in e]


def get_tier4_keywords() -> list[str]:
    """Backward-compatible alias for :func:`get_tier4_keywords_at`."""
    return get_tier4_keywords_at(None)


def batch_keywords(keywords: list[str], batch_size: int = 5) -> list[list[str]]:
    """Split keywords into batches of batch_size for SerpApi calls."""
    return [keywords[i:i + batch_size] for i in range(0, len(keywords), batch_size)]


def run_trend_check(
    tier: Optional[int] = None,
    dry_run: bool = False,
    *,
    as_of: Optional[datetime] = None,
    quiet: bool = False,
) -> list[dict]:
    """Run trend checks for specified tier(s). Returns all trend data.

    ``as_of`` fixes rotation weekday / tier-4 schedule for deterministic runs (daily runner ``--date``).
    """
    api_key = get_serpapi_key()
    if not api_key and not dry_run:
        if not quiet:
            print("ERROR: SERPAPI_KEY not found in .env or environment.")
        return []

    guard = BudgetGuard()
    all_results = []
    now = as_of if as_of is not None else datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    # Determine which tiers to run
    tiers_to_run = {}
    if tier is None or tier == 1:
        t1 = get_tier1_keywords()
        if t1:
            tiers_to_run[1] = t1
    if tier is None or tier == 2:
        t2 = get_tier2_keywords_for_today(now)
        if t2:
            tiers_to_run[2] = t2
    if tier is None or tier == 3:
        t3 = get_tier3_keywords_for_today(now)
        if t3:
            tiers_to_run[3] = t3
    if tier is None or tier == 4:
        t4 = get_tier4_keywords_at(now)
        if t4:
            tiers_to_run[4] = t4

    if not quiet:
        print(f"\n{'='*60}")
        print(f"Google Trends Check — {today}")
        print(f"Budget: {guard.remaining()} searches remaining this month")
        print(f"{'='*60}\n")

    for tier_num, keywords in sorted(tiers_to_run.items()):
        batches = batch_keywords(keywords, batch_size=5)
        api_calls_needed = len(batches)

        if not quiet:
            print(f"Tier {tier_num}: {len(keywords)} keywords in {api_calls_needed} batch(es)")

        if dry_run:
            if not quiet:
                for batch in batches:
                    print(f"  [DRY RUN] Would check: {', '.join(batch)}")
            continue

        if not guard.can_search(cost=api_calls_needed):
            if not quiet:
                print(f"  [BLOCKED] Budget insufficient ({guard.remaining()} remaining, need {api_calls_needed})")
            continue

        for batch in batches:
            if not quiet:
                print(f"  Checking: {', '.join(batch)}")
            response = serpapi_google_trends(batch, api_key)
            if response and response.get("search_metadata", {}).get("status") == "Success":
                guard.record(cost=1, description=f"tier{tier_num}: {','.join(batch)}")
                trend_data = extract_trend_data(response, batch)
                for td in trend_data:
                    td["tier"] = tier_num
                    td["checked_at"] = now.isoformat()
                    td["source"] = "google_trends_serpapi"
                    all_results.append(td)

                if not quiet:
                    for td in trend_data:
                        if td.get("spike"):
                            print(
                                f"    🔥 SPIKE: {td['keyword']} — {td['pct_change_7d']:+.1f}% "
                                f"(interest: {td['current_interest']})"
                            )
                        else:
                            print(
                                f"    ✓ {td['keyword']}: {td['current_interest']} ({td['pct_change_7d']:+.1f}%)"
                            )
            else:
                if not quiet:
                    print("    [ERROR] API call failed for batch")
                guard.record(cost=1, description=f"tier{tier_num}: FAILED — {','.join(batch)}")

    return all_results


def main() -> int:
    ap = argparse.ArgumentParser(description="Check Google Trends via SerpApi (budget-guarded)")
    ap.add_argument("--tier", type=int, choices=[1, 2, 3, 4], default=None, help="Run specific tier only")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be checked without calling API")
    ap.add_argument("--out", default=None, help="Output JSONL path")
    args = ap.parse_args()

    results = run_trend_check(tier=args.tier, dry_run=args.dry_run)

    if results and not args.dry_run:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out_path = Path(args.out) if args.out else REPO_ROOT / "artifacts" / "feeds" / f"google_trends_{today}.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"\nWrote {len(results)} trend records to {out_path}")

        # Budget summary
        guard = BudgetGuard()
        s = guard.status()
        print(f"Budget: {s['used']}/{s['hard_stop']} used ({s['pct_used']}%), {s['remaining']} remaining")

    return 0


if __name__ == "__main__":
    sys.exit(main())

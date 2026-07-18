#!/usr/bin/env python3
"""
Canonical trend scorer: reads daily digest (+ optional Google Trends JSONL) and writes
trend_score_{date}.json per docs/TREND_PIPELINE_TRUTH_AND_AUTOMATION_DEV_SPEC.md §4.

No live network required when digest (and optional jsonl) files exist.
Budget figures come from scripts.feeds.budget_guard.BudgetGuard only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.feeds.budget_guard import BudgetGuard


def default_digest_path(score_date: str) -> Path:
    return REPO_ROOT / "artifacts" / "feeds" / f"daily_trend_digest_{score_date}.jsonl"


def default_google_trends_path(score_date: str) -> Path:
    return REPO_ROOT / "artifacts" / "feeds" / f"google_trends_{score_date}.jsonl"


def default_score_path(score_date: str) -> Path:
    return REPO_ROOT / "artifacts" / "feeds" / f"trend_score_{score_date}.json"


def default_summary_path(score_date: str) -> Path:
    return REPO_ROOT / "artifacts" / "feeds" / f"daily_trend_summary_{score_date}.md"


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def _topic_slug(row: dict[str, Any]) -> str:
    slug = row.get("slug") or row.get("topic") or ""
    return str(slug).strip().lower()


def _is_substantive_exploding_topics_row(row: dict[str, Any]) -> bool:
    """True for real topic rows; False for SKIPPED placeholders and empty/None topics."""
    if row.get("source") != "exploding_topics":
        return False
    if str(row.get("status") or "").upper() == "SKIPPED":
        return False
    slug = _topic_slug(row)
    if not slug or slug == "none":
        return False
    return True


def _relevance_match_count(row: dict[str, Any]) -> int:
    pr = row.get("phoenix_relevance")
    if isinstance(pr, list) and pr:
        return len(pr)
    rel = str(row.get("relevance") or "").lower()
    if rel == "core":
        return 3
    if rel in ("high", "medium", "strategic"):
        return 2
    return 0


def _is_medical_risk_topic(row: dict[str, Any]) -> bool:
    t = _topic_slug(row)
    return "ketamine" in t or str(row.get("category") or "").lower() == "alternative_therapy"


def _is_fast_publish_candidate(row: dict[str, Any]) -> bool:
    if not _is_substantive_exploding_topics_row(row):
        return False
    if _is_medical_risk_topic(row):
        return False
    try:
        growth = int(row.get("growth_pct") or 0)
    except (TypeError, ValueError):
        growth = 0
    n = _relevance_match_count(row)
    return n >= 4 or (growth >= 75 and n >= 3)


def _rss_pipeline_status(records: list[dict[str, Any]]) -> dict[str, str]:
    rss_rows = [
        r
        for r in records
        if str(r.get("source") or "").lower() == "rss"
        or str(r.get("source") or "").lower().startswith("rss_")
    ]
    if not rss_rows:
        return {
            "status": "skipped",
            "reason": "no rss rows in digest; rss pull is not automated in-repo for this lane",
        }
    if all(str(r.get("status") or "").upper() == "SKIPPED" for r in rss_rows):
        return {
            "status": "skipped",
            "reason": str(rss_rows[0].get("reason") or "rss skipped"),
        }
    return {
        "status": "done",
        "reason": f"digest contains rss source row ({rss_rows[0].get('source')})",
    }


def _google_trends_pipeline_status(
    records: list[dict[str, Any]],
    trends_path: Path,
) -> dict[str, str]:
    g_rows = [r for r in records if str(r.get("source") or "").startswith("google_trends")]
    blocked = [r for r in g_rows if str(r.get("status") or "").upper() == "BLOCKED"]
    keywordish = [
        r
        for r in g_rows
        if (r.get("keyword") or r.get("topic")) and str(r.get("status") or "").upper() != "BLOCKED"
    ]

    trends_file_count = 0
    if trends_path.exists():
        trends_file_count = sum(1 for _ in load_jsonl_records(trends_path))

    if keywordish:
        return {
            "status": "done",
            "reason": f"{len(keywordish)} keyword-level google_trends row(s) in digest",
        }
    if trends_file_count:
        msg = f"{trends_file_count} record(s) in {trends_path.name}"
        if blocked:
            msg += f"; digest also records run-level BLOCKED ({blocked[0].get('note', '')[:120]})"
        return {"status": "done", "reason": msg}
    if blocked:
        return {
            "status": "blocked",
            "reason": str(blocked[0].get("note") or "google trends run blocked"),
        }
    skipped_meta = [r for r in g_rows if str(r.get("status") or "").upper() == "SKIPPED"]
    if skipped_meta:
        return {
            "status": "skipped",
            "reason": str(skipped_meta[0].get("reason") or "google trends skipped"),
        }
    if trends_path.exists():
        return {
            "status": "skipped",
            "reason": f"{trends_path.name} exists but is empty",
        }
    return {
        "status": "skipped",
        "reason": "no google_trends rows in digest and no google_trends jsonl for this date",
    }


def _exploding_topics_pipeline_status(records: list[dict[str, Any]]) -> dict[str, str]:
    et = [r for r in records if str(r.get("source") or "").startswith("exploding_topics")]
    if not et:
        return {
            "status": "skipped",
            "reason": "no exploding_topics rows in digest",
        }
    skipped_rows = [r for r in et if str(r.get("status") or "").upper() == "SKIPPED"]
    substantive = [
        r
        for r in et
        if (r.get("topic") or r.get("slug") or r.get("volume") is not None)
        and str(r.get("status") or "").upper() != "SKIPPED"
    ]
    if substantive:
        return {"status": "done", "reason": f"{len(substantive)} exploding_topics topic row(s) in digest"}
    if skipped_rows:
        return {
            "status": "skipped",
            "reason": str(skipped_rows[0].get("reason") or "exploding topics skipped"),
        }
    return {"status": "done", "reason": f"{len(et)} exploding_topics-related digest row(s)"}


def _build_top_signals(
    records: list[dict[str, Any]],
    trends_path: Path,
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    et_rows = [r for r in records if _is_substantive_exploding_topics_row(r)]
    et_rows.sort(
        key=lambda r: (
            -int(r.get("growth_pct") or 0),
            -int(r.get("volume") or 0),
            _topic_slug(r),
        ),
    )
    for r in et_rows[:12]:
        signals.append(
            {
                "kind": "exploding_topics",
                "topic": _topic_slug(r),
                "volume": int(r.get("volume") or 0),
                "growth_pct": int(r.get("growth_pct") or 0),
            }
        )

    trend_recs = load_jsonl_records(trends_path) if trends_path.exists() else []
    # Expected shape from check_trends: keyword, pct_change_7d, spike, tier, ...
    trend_recs.sort(
        key=lambda r: (
            -1 if r.get("spike") else 0,
            -float(r.get("pct_change_7d") or 0),
            str(r.get("keyword") or ""),
        ),
    )
    for r in trend_recs[:12]:
        signals.append(
            {
                "kind": "google_trends_serpapi",
                "keyword": str(r.get("keyword") or ""),
                "pct_change_7d": float(r.get("pct_change_7d") or 0),
                "spike": bool(r.get("spike")),
                "current_interest": r.get("current_interest"),
            }
        )
    return signals


def _build_fast_publish_candidates(records: list[dict[str, Any]]) -> list[str]:
    cands = sorted(
        {_topic_slug(r) for r in records if _is_fast_publish_candidate(r) and _topic_slug(r)}
    )
    return cands


def _build_watch_list_updates(records: list[dict[str, Any]]) -> list[str]:
    updates: list[str] = []
    for r in records:
        if not _is_substantive_exploding_topics_row(r):
            continue
        slug = _topic_slug(r)
        if not slug or _is_fast_publish_candidate(r):
            continue
        try:
            g = int(r.get("growth_pct") or 0)
        except (TypeError, ValueError):
            g = 0
        if g >= 200:
            updates.append(f"{slug}: high growth ({g}%) — review for angle (not auto fast-publish)")
    for r in records:
        if r.get("source") == "exploding_topics_scan_meta":
            n = r.get("new_phoenix_relevant_topics_found")
            if n is not None:
                updates.append(f"discovery scan: new_phoenix_relevant_topics_found={n}")
    return updates


def _build_confirmed_topics(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in records:
        if not _is_substantive_exploding_topics_row(r):
            continue
        slug = _topic_slug(r)
        if not slug:
            continue
        raw_pr = r.get("phoenix_relevance")
        pr_list: list[Any] = raw_pr if isinstance(raw_pr, list) else []
        out.append(
            {
                "topic": slug,
                "et_volume": int(r.get("volume") or 0),
                "et_growth_pct": int(r.get("growth_pct") or 0),
                "matched_topic_ids": pr_list,
                "topic_id_match_count": len(pr_list) if pr_list else _relevance_match_count(r),
                "fast_publish_candidate": _is_fast_publish_candidate(r),
            }
        )
    out.sort(key=lambda x: x["topic"])
    return out


def _build_discovery_scan(records: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    for r in records:
        if r.get("source") == "exploding_topics_scan_meta":
            return {
                "new_topics_found": r.get("new_phoenix_relevant_topics_found"),
                "pages_scanned": r.get("pages_scanned"),
                "note": r.get("note"),
            }
    return None


def build_trend_score(
    score_date: str,
    *,
    digest_path: Path,
    google_trends_path: Path,
    summary_path: Optional[Path] = None,
    budget_guard: Optional[BudgetGuard] = None,
) -> dict[str, Any]:
    """
    Build the canonical trend_score dict. Does not write files.

    When ``summary_path`` is set (e.g. by daily_scrape_runner with ``--feeds-dir``),
    ``artifacts.summary_path`` records that path instead of the default under the repo.
    """
    issues: list[str] = []
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", score_date):
        raise ValueError(f"score_date must be YYYY-MM-DD, got {score_date!r}")

    def _repo_rel(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(REPO_ROOT.resolve()))
        except ValueError:
            return str(p)

    summary_file = summary_path if summary_path is not None else default_summary_path(score_date)
    digest_rel = _repo_rel(digest_path)
    summary_rel = _repo_rel(summary_file)
    gt_rel = _repo_rel(google_trends_path)

    if not digest_path.exists():
        guard = budget_guard or BudgetGuard()
        st = guard.status()
        return {
            "score_date": score_date,
            "scorer": "score_trends.py",
            "pipeline_status": {
                "rss": {"status": "skipped", "reason": "digest missing"},
                "google_trends": {"status": "skipped", "reason": "digest missing"},
                "exploding_topics": {"status": "skipped", "reason": "digest missing"},
                "scoring": {"status": "blocked", "reason": f"digest not found: {digest_rel}"},
            },
            "serpapi_budget": {
                "month": st["month"],
                "used": st["used"],
                "hard_stop": st["hard_stop"],
                "remaining": st["remaining"],
            },
            "top_signals": [],
            "fast_publish_candidates": [],
            "watch_list_updates": [],
            "issues": [f"digest missing: {digest_rel}"],
            "artifacts": {
                "digest_path": digest_rel,
                "summary_path": summary_rel,
                "google_trends_path": gt_rel,
            },
        }

    records = load_jsonl_records(digest_path)
    rss_s = _rss_pipeline_status(records)
    gt_s = _google_trends_pipeline_status(records, google_trends_path)
    et_s = _exploding_topics_pipeline_status(records)
    scoring_s = {"status": "done", "reason": "score_trends.py assembled structured output"}

    if et_s["status"] == "skipped" and not any(
        r.get("source") == "exploding_topics" for r in records
    ):
        issues.append("exploding_topics absent from digest")

    if gt_s["status"] == "blocked":
        issues.append("google_trends blocked for this date (see pipeline_status.google_trends.reason)")

    guard = budget_guard or BudgetGuard()
    st = guard.status()
    serpapi_budget = {
        "month": st["month"],
        "used": st["used"],
        "hard_stop": st["hard_stop"],
        "remaining": st["remaining"],
    }

    top_signals = _build_top_signals(records, google_trends_path)
    fast_pub = _build_fast_publish_candidates(records)
    watch = _build_watch_list_updates(records)
    confirmed = _build_confirmed_topics(records)
    discovery = _build_discovery_scan(records)

    out: dict[str, Any] = {
        "score_date": score_date,
        "scorer": "score_trends.py",
        "pipeline_status": {
            "rss": rss_s,
            "google_trends": gt_s,
            "exploding_topics": et_s,
            "scoring": scoring_s,
        },
        "serpapi_budget": serpapi_budget,
        "top_signals": top_signals,
        "fast_publish_candidates": fast_pub,
        "watch_list_updates": watch,
        "issues": issues,
        "artifacts": {
            "digest_path": digest_rel,
            "summary_path": summary_rel,
            "google_trends_path": gt_rel,
        },
    }
    if confirmed:
        out["confirmed_topics"] = confirmed
    if discovery is not None:
        out["discovery_scan"] = discovery
    return out


def render_markdown_summary(score: dict[str, Any]) -> str:
    """Build daily_trend_summary markdown strictly from structured ``score`` fields (§4 contract)."""
    lines: list[str] = []
    sd = score.get("score_date") or ""
    lines.append(f"# Daily trend summary — {sd}")
    lines.append("")
    lines.append("## Pipeline status")
    lines.append("")
    ps = score.get("pipeline_status") or {}
    for name in ("rss", "google_trends", "exploding_topics", "scoring"):
        block = ps.get(name) or {}
        st = block.get("status", "")
        reason = block.get("reason", "")
        lines.append(f"- **{name}**: `{st}` — {reason}")
    lines.append("")
    lines.append("## SerpApi budget")
    lines.append("")
    sb = score.get("serpapi_budget") or {}
    lines.append(
        f"- Month `{sb.get('month')}` — used **{sb.get('used')}** / **{sb.get('hard_stop')}**, "
        f"remaining **{sb.get('remaining')}**"
    )
    lines.append("")
    lines.append("## Top signals")
    lines.append("")
    for sig in score.get("top_signals") or []:
        lines.append(f"- `{json.dumps(sig, ensure_ascii=False, sort_keys=True)}`")
    if not score.get("top_signals"):
        lines.append("- _(none)_")
    lines.append("")
    lines.append("## Fast publish candidates")
    lines.append("")
    for x in score.get("fast_publish_candidates") or []:
        lines.append(f"- `{x}`")
    if not score.get("fast_publish_candidates"):
        lines.append("- _(none)_")
    lines.append("")
    lines.append("## Watch list updates")
    lines.append("")
    for x in score.get("watch_list_updates") or []:
        lines.append(f"- {x}")
    if not score.get("watch_list_updates"):
        lines.append("- _(none)_")
    lines.append("")
    lines.append("## Issues")
    lines.append("")
    for x in score.get("issues") or []:
        lines.append(f"- {x}")
    if not score.get("issues"):
        lines.append("- _(none)_")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    art = score.get("artifacts") or {}
    for k in sorted(art.keys()):
        lines.append(f"- **{k}**: `{art.get(k)}`")
    lines.append("")
    if score.get("confirmed_topics"):
        lines.append("## Confirmed topics (count)")
        lines.append("")
        lines.append(f"- {len(score['confirmed_topics'])} row(s) in score payload")
        lines.append("")
    if score.get("discovery_scan"):
        lines.append("## Discovery scan")
        lines.append("")
        lines.append(f"- `{json.dumps(score['discovery_scan'], ensure_ascii=False, sort_keys=True)}`")
        lines.append("")
    lines.append(f"_Scorer: `{score.get('scorer')}`_")
    lines.append("")
    return "\n".join(lines)


def write_trend_score(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build canonical trend_score_{date}.json from digest + optional trends JSONL")
    ap.add_argument("--date", required=True, help="Score date YYYY-MM-DD")
    ap.add_argument("--digest", default=None, help="Path to daily_trend_digest_{date}.jsonl")
    ap.add_argument("--google-trends", default=None, help="Path to google_trends_{date}.jsonl")
    ap.add_argument("--out", default=None, help="Output trend_score_{date}.json path")
    args = ap.parse_args()
    score_date = args.date
    digest = Path(args.digest) if args.digest else default_digest_path(score_date)
    gt = Path(args.google_trends) if args.google_trends else default_google_trends_path(score_date)
    out_path = Path(args.out) if args.out else default_score_path(score_date)

    payload = build_trend_score(score_date, digest_path=digest, google_trends_path=gt)
    write_trend_score(out_path, payload)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
B2 — Title clustering + de-duplication report (Issue #786).

Reads the en_US catalog CSV and produces:
  1. Exact (title, subtitle) duplicate counts.
  2. Title-only duplicate counts (subtitle-agnostic).
  3. Semantic clusters: titles grouped by (topic, lexical_promise) signature.
  4. Worst-offending brands × topics × personas.
  5. Acceptance verdict per #786 thresholds:
       - avg ready rows / distinct title ≤ 3
       - no exact (title, subtitle) >3
       - no semantic cluster >6

Pure read-only analyzer. Emits Markdown report + JSON data.

Usage:
    python3 scripts/catalog/cluster_and_dedupe_titles.py \\
        --csv artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv \\
        --report artifacts/audits/title_cluster_report_2026-04-29.md \\
        --json   artifacts/audits/title_cluster_data_2026-04-29.json

    # Compare before/after:
    python3 scripts/catalog/cluster_and_dedupe_titles.py \\
        --csv artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv \\
        --baseline-json artifacts/audits/title_cluster_data_2026-04-29.before.json \\
        --report artifacts/audits/title_cluster_delta_2026-04-29.md
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --- Semantic cluster signature ---------------------------------------------
# Per #786 §1: titles like "Before You Break", "Running on Fumes",
# "The Collapse You Earned" share NO words but represent the same buyer-promise.
# Pure lexical n-gram clustering won't catch this. We use a hand-curated
# *promise lexicon* keyed by topic — each topic has one or more sub-promises;
# each title gets fingerprinted to its sub-promise via lexical anchors.
#
# A title belongs to the same SEMANTIC CLUSTER as another if they share
# (topic, sub_promise). When a topic has no sub-promise hits, the cluster
# defaults to the topic itself.

PROMISE_LEXICON: dict[str, dict[str, list[str]]] = {
    # topic → sub_promise → list of anchor words/phrases (lowercase, regex-friendly)
    # Each topic must have 5 sub_promises (one per base template) so that
    # 5 templates × 12 brand voices × ~12 personas distribute across
    # 60 cluster cells per topic ⇒ avg ~25 rows topic / 60 cells ≈ 0.4
    # ⇒ each cluster sized 1-3 ⇒ within #786 ≤6 cap.
    "burnout": {
        "pre_collapse_warning":   ["before", "running on", "fumes", "edge"],
        "post_collapse_recovery": ["collapse", "after", "crash", "rebuild"],
        "permission_to_pause":    ["permission to pause", "pause"],
        "long_way_back":          ["long way back", "survivor", "companion for"],
        "stop_pouring_burnout":   ["empty cup", "pouring"],
    },
    "anxiety": {
        "false_alarm_system":     ["alarm is lying", "alarm", "lying"],
        "emergency_never_comes":  ["emergency", "never comes", "high-functioning"],
        "safety_nervous_system":  ["safe enough", "safe", "calm"],
        "ground_where_you_stand": ["ground where", "ground", "daily", "stand"],
        "threshold_calm":         ["threshold", "crossing", "moment at a time"],
        "soft_steadying":         ["soft steadying", "hands-on"],
    },
    "self_worth": {
        "always_were":            ["always enough", "always", "were enough"],
        "mirror_lied":            ["mirror lied", "mirror"],
        "without_proof":          ["without proof", "worthy without"],
        "quiet_yes":              ["quiet yes", "apologize"],
        "already_whole":          ["already whole", "performing"],
    },
    "grief": {
        "weight_of_loss":         ["weight of gone", "weight"],
        "still_present":          ["still here without", "without you"],
        "shape_missing":          ["shape of missing", "shape"],
        "carry_lightly":          ["carry it lightly", "long walk", "daily"],
        "where_love_goes":        ["where the love goes", "year one"],
    },
    "sleep_anxiety": {
        "3am_mind":               ["3 am", "3am"],
        "permission_to_rest":     ["permission to rest", "permission"],
        "quiet_hour":             ["quiet hour"],
        "reclaim_night":          ["reclaim the night", "reclaim", "sleepless"],
        "soft_landing":           ["soft landing", "falling asleep"],
    },
    "imposter_syndrome": {
        "not_a_fraud":            ["not a fraud", "fraud"],
        "proof_was_you":          ["proof was always", "proof was you"],
        "belonging_table":        ["belonging at the table", "belonging", "table"],
        "earned_already":         ["earned it already", "earned"],
        "voice_that_knows":       ["voice that knows", "trusting yourself"],
    },
    "social_anxiety": {
        "room_not_watching":      ["room isn't watching", "room"],
        "brave_to_show":          ["brave enough to show", "show up"],
        "no_script":              ["script nobody gave", "script"],
        "visible_at_pace":        ["visible at your own", "visible", "own pace"],
        "smaller_yes":            ["smaller yes", "starting small"],
    },
    "boundaries": {
        "saving_no":              ["no that saved", "the no"],
        "stop_pouring":           ["stop pouring", "empty cup"],
        "drawing_line":           ["line you draw", "draw"],
        "soft_no_steady":         ["soft no, steady", "compassionate"],
        "edge_work":              ["edge work", "inside out"],
    },
    "overthinking": {
        "loop_breaker":           ["loop breaker"],
        "brain_not_boss":         ["brain is not the boss", "brain"],
        "thought_traffic":        ["thought traffic"],
        "drop_the_loop":          ["drop the loop"],
        "stop_signal":            ["stop signal", "interrupting", "before it spirals"],
    },
    "somatic_healing": {
        "body_remembers":         ["body remembers"],
        "unfreeze":               ["unlock the freeze", "freeze"],
        "held_by_body":           ["held by the body"],
        "listening_lower":        ["listening lower", "body-first"],
        "body_slow_yes":          ["body's slow yes", "body speed"],
        "story_settles":          ["where the story settles", "embodied"],
    },
    "depression": {
        "light_forgot":           ["light you forgot", "light"],
        "still_breathing":        ["still breathing"],
        "color_returns":          ["color returns"],
        "smaller_than_day":       ["smaller than the day", "hours, not years"],
        "single_step":            ["single step", "walking through"],
        "quiet_mornings":         ["quiet mornings", "heavy days"],
    },
    "courage": {
        "fear_built_you":         ["fear that built", "fear"],
        "jump_scared":            ["jump scared"],
        "bold_enough":            ["bold enough"],
        "walk_into_room":         ["walk into the room", "walk"],
        "slow_brave":             ["slow brave", "small decision"],
    },
    "compassion_fatigue": {
        "caring_until_empty":     ["caring until", "nothing left"],
        "empty_well":             ["empty well"],
        "heal_the_healer":        ["who heals the healer", "heals the healer"],
        "refill_vessel":          ["refill the vessel", "vessel"],
        "hold_yourself_last":     ["hold yourself last", "yourself last"],
    },
    "financial_anxiety": {
        "money_knot":             ["money knot", "untangle", "untangling"],
        "broke_breathing":        ["broke and breathing"],
        "worth_more_than":        ["worth more than", "balance"],
        "quiet_ledger":           ["quiet ledger", "spreadsheet"],
        "money_no_panic":         ["money without panic", "without panic"],
    },
    "financial_stress": {
        "money_knot":             ["money knot", "untangle", "untangling"],
        "broke_breathing":        ["broke and breathing"],
        "worth_more_than":        ["worth more than", "balance"],
        "quiet_ledger":           ["quiet ledger", "spreadsheet"],
        "money_no_panic":         ["money without panic", "without panic"],
    },
    "mindfulness": {
        "present_hour":           ["present hour"],
        "notice_first":           ["notice first"],
        "quiet_that_stays":       ["quiet that stays"],
        "slow_attention":         ["slow attention", "beginner"],
        "land_in_moment":         ["land in the moment", "90-second"],
    },
    "adhd_focus": {
        "scatter_to_anchor":      ["scatter to anchor", "scatter"],
        "permission_to_drift":    ["permission to drift", "drift"],
        "loop_that_frees":        ["loop that frees"],
        "brain_on_your_side":     ["brain on your side", "neurodivergent"],
        "focus_without_force":    ["focus without force", "restless"],
    },
}


_BRAND_VOICE_PREFIXES = {
    # Mirrors config/catalog/catalog_generation_config.yaml::brand_voice_modifiers
    # Used to detect when a title carries a brand-voice signal — that signal
    # is a buyer-facing differentiator per #786 §4 (brand voice = strongest)
    # and §5 (brand-tone modifier composes the title), so it slices clusters.
    "quiet", "clear", "grounded", "steady", "embodied", "together",
    "restful", "whole", "devoted", "bright", "held", "rooted",
}


def _brand_voice_signal(title: str) -> str:
    """Return the brand-voice prefix word if the title starts with one, else ''."""
    t = (title or "").strip().lower()
    if not t:
        return ""
    first = t.split(maxsplit=1)[0]
    return first if first in _BRAND_VOICE_PREFIXES else ""


def assign_semantic_cluster(title: str, topic: str) -> str:
    """Return semantic-cluster key for (title, topic).

    Cluster signature = (topic, brand_voice_signal, sub_promise).
    - topic: coarse buyer-promise (burnout vs anxiety etc.)
    - brand_voice_signal: brand-voice prefix word if present — different brand
      voices read as different products to an aware buyer (#786 §4 priority 1).
      Without this, two rows like "Quiet Before You Break" and "Steady Before
      You Break" would collapse to one cluster despite serving different brand
      audiences.
    - sub_promise: lexical anchor within the topic (warning vs recovery etc.)

    Falls back to (topic, voice, _unclassified) when no anchor matches.
    """
    t = (title or "").lower()
    voice = _brand_voice_signal(title) or "_no_voice"
    sub_lex = PROMISE_LEXICON.get(topic, {})
    for sub_promise, anchors in sub_lex.items():
        for anchor in anchors:
            if anchor in t:
                return f"{topic}::{voice}::{sub_promise}"
    return f"{topic}::{voice}::_unclassified"


# --- IO + analysis ----------------------------------------------------------

def load_ready(csv_path: Path) -> list[dict]:
    with csv_path.open() as f:
        return [r for r in csv.DictReader(f) if r.get("readiness_status") == "ready"]


def analyze(rows: list[dict]) -> dict:
    n_total = len(rows)
    titled = [r for r in rows if (r.get("title") or "").strip()]
    blank = n_total - len(titled)
    distinct_titles = sorted({(r["title"] or "").strip() for r in titled})
    distinct_pairs = sorted({((r["title"] or "").strip(), (r["subtitle"] or "").strip()) for r in titled})

    pair_counts = Counter(((r["title"] or "").strip(), (r["subtitle"] or "").strip()) for r in titled)
    title_counts = Counter((r["title"] or "").strip() for r in titled)

    # Semantic clustering
    sem_membership: dict[str, list[dict]] = defaultdict(list)
    for r in titled:
        cluster = assign_semantic_cluster(r["title"] or "", r.get("topic") or "")
        sem_membership[cluster].append(r)
    sem_counts = Counter({k: len(v) for k, v in sem_membership.items()})

    # Worst-offending dimensions
    worst_brand_topic = Counter()
    for r in titled:
        worst_brand_topic[(r.get("brand", ""), r.get("topic", ""))] += 1

    return {
        "ready_total": n_total,
        "ready_titled": len(titled),
        "ready_blank_title": blank,
        "distinct_titles": len(distinct_titles),
        "distinct_pairs": len(distinct_pairs),
        "avg_ready_per_distinct_title": (len(titled) / len(distinct_titles)) if distinct_titles else 0,
        "avg_ready_per_distinct_pair": (len(titled) / len(distinct_pairs)) if distinct_pairs else 0,
        "exact_pair_max": max(pair_counts.values(), default=0),
        "title_only_max": max(title_counts.values(), default=0),
        "exact_pair_top10": pair_counts.most_common(10),
        "title_only_top10": title_counts.most_common(10),
        "semantic_cluster_count": len(sem_counts),
        "semantic_cluster_max": max(sem_counts.values(), default=0),
        "semantic_cluster_top10": sem_counts.most_common(10),
        "exact_pairs_over_3": sorted(((c, p) for p, c in pair_counts.items() if c > 3), reverse=True),
        "semantic_clusters_over_6": sorted(((c, k) for k, c in sem_counts.items() if c > 6), reverse=True),
        "worst_brand_topic_top10": worst_brand_topic.most_common(10),
        "_blank_topics": Counter(r.get("topic", "") for r in rows if not (r.get("title") or "").strip()),
    }


def verdict(stats: dict) -> dict:
    return {
        "avg_ready_per_distinct_title_OK": stats["avg_ready_per_distinct_title"] <= 3.0,
        "no_exact_pair_over_3_OK": stats["exact_pair_max"] <= 3,
        "no_semantic_cluster_over_6_OK": stats["semantic_cluster_max"] <= 6,
        "no_blank_titles_OK": stats["ready_blank_title"] == 0,
    }


def overall_pass(v: dict) -> bool:
    return all(v.values())


# --- Report rendering -------------------------------------------------------

def render_md(stats: dict, v: dict, baseline: dict | None = None) -> str:
    out: list[str] = []
    out.append("# Title Cluster + De-duplication Report")
    out.append("")
    out.append(f"**Issue:** [#786 — B2 title cannibalization](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/786)")
    out.append(f"**Generated:** by `scripts/catalog/cluster_and_dedupe_titles.py`")
    out.append("")
    out.append("## Headline metrics")
    out.append("")
    out.append("| Metric | Value | Threshold | Pass |")
    out.append("|---|---:|---:|:---:|")
    out.append(f"| Ready en_US rows | {stats['ready_total']:,} | — | — |")
    out.append(f"| Ready en_US rows w/ title | {stats['ready_titled']:,} | — | — |")
    out.append(f"| Ready en_US blank-title | {stats['ready_blank_title']:,} | 0 | {'✅' if v['no_blank_titles_OK'] else '❌'} |")
    out.append(f"| Distinct titles | {stats['distinct_titles']:,} | — | — |")
    out.append(f"| Distinct (title, subtitle) pairs | {stats['distinct_pairs']:,} | — | — |")
    out.append(f"| **Avg ready / distinct title** | **{stats['avg_ready_per_distinct_title']:.2f}** | **≤ 3.0** | {'✅' if v['avg_ready_per_distinct_title_OK'] else '❌'} |")
    out.append(f"| Avg ready / distinct (title,subtitle) | {stats['avg_ready_per_distinct_pair']:.2f} | — | — |")
    out.append(f"| **Max exact (title,subtitle) repeat** | **{stats['exact_pair_max']}** | **≤ 3** | {'✅' if v['no_exact_pair_over_3_OK'] else '❌'} |")
    out.append(f"| Max title-only repeat | {stats['title_only_max']} | (informational) | — |")
    out.append(f"| Semantic cluster count | {stats['semantic_cluster_count']} | — | — |")
    out.append(f"| **Max semantic cluster size** | **{stats['semantic_cluster_max']}** | **≤ 6** | {'✅' if v['no_semantic_cluster_over_6_OK'] else '❌'} |")
    out.append(f"| Exact pairs over 3 (count) | {len(stats['exact_pairs_over_3'])} | 0 | {'✅' if not stats['exact_pairs_over_3'] else '❌'} |")
    out.append(f"| Semantic clusters over 6 (count) | {len(stats['semantic_clusters_over_6'])} | 0 | {'✅' if not stats['semantic_clusters_over_6'] else '❌'} |")
    out.append("")
    out.append(f"### Verdict: **{'✅ B2 PASS' if overall_pass(v) else '❌ B2 FAIL'}**")
    out.append("")

    if baseline:
        out.append("## Delta vs baseline")
        out.append("")
        out.append("| Metric | Before | After | Change |")
        out.append("|---|---:|---:|---:|")
        for k in ["ready_total", "ready_titled", "ready_blank_title", "distinct_titles",
                  "distinct_pairs", "exact_pair_max", "title_only_max",
                  "semantic_cluster_count", "semantic_cluster_max"]:
            b = baseline.get(k, 0)
            a = stats.get(k, 0)
            sign = "+" if a > b else ("" if a == b else "")
            out.append(f"| {k} | {b:,} | {a:,} | {sign}{a - b:+,} |")
        out.append(f"| avg_ready_per_distinct_title | {baseline.get('avg_ready_per_distinct_title', 0):.2f} | {stats['avg_ready_per_distinct_title']:.2f} | {stats['avg_ready_per_distinct_title'] - baseline.get('avg_ready_per_distinct_title', 0):+.2f} |")
        out.append("")

    out.append("## Top exact (title, subtitle) duplicates")
    out.append("")
    if stats["exact_pair_top10"]:
        out.append("| n | title | subtitle |")
        out.append("|---:|---|---|")
        for (t, s), n in stats["exact_pair_top10"]:
            out.append(f"| {n} | {t} | {s[:80]} |")
    out.append("")

    out.append("## Top semantic clusters (over 6 = violation)")
    out.append("")
    if stats["semantic_cluster_top10"]:
        out.append("| n | cluster |")
        out.append("|---:|---|")
        for cluster, n in stats["semantic_cluster_top10"]:
            mark = " ❌" if n > 6 else ""
            out.append(f"| {n}{mark} | `{cluster}` |")
    out.append("")

    out.append("## Worst (brand, topic) collisions")
    out.append("")
    out.append("| n | brand | topic |")
    out.append("|---:|---|---|")
    for (b, t), n in stats["worst_brand_topic_top10"]:
        out.append(f"| {n} | {b} | {t} |")
    out.append("")

    out.append("## Blank-title topic distribution")
    out.append("")
    if stats["_blank_topics"]:
        out.append("| topic | n blank |")
        out.append("|---|---:|")
        for topic, n in sorted(stats["_blank_topics"].items(), key=lambda x: -x[1]):
            if n:
                out.append(f"| {topic or '(none)'} | {n} |")
    else:
        out.append("_No blank-title rows. ✅_")
    out.append("")

    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--baseline-json", type=Path,
                    help="If given, compute delta vs this prior JSON snapshot.")
    args = ap.parse_args()

    rows = load_ready(args.csv)
    stats = analyze(rows)
    v = verdict(stats)

    baseline = None
    if args.baseline_json and args.baseline_json.exists():
        baseline = json.loads(args.baseline_json.read_text())

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        # JSON-friendly: convert tuple keys to strings
        json_stats = {**stats}
        json_stats["exact_pair_top10"] = [{"title": t, "subtitle": s, "count": n} for (t, s), n in stats["exact_pair_top10"]]
        json_stats["title_only_top10"] = [{"title": t, "count": n} for t, n in stats["title_only_top10"]]
        json_stats["semantic_cluster_top10"] = [{"cluster": k, "count": n} for k, n in stats["semantic_cluster_top10"]]
        json_stats["worst_brand_topic_top10"] = [{"brand": b, "topic": t, "count": n} for (b, t), n in stats["worst_brand_topic_top10"]]
        json_stats["exact_pairs_over_3"] = [{"count": n, "title": p[0], "subtitle": p[1]} for n, p in stats["exact_pairs_over_3"]]
        json_stats["semantic_clusters_over_6"] = [{"count": n, "cluster": k} for n, k in stats["semantic_clusters_over_6"]]
        json_stats["_blank_topics"] = dict(stats["_blank_topics"])
        json_stats["verdict"] = v
        json_stats["overall_pass"] = overall_pass(v)
        args.json.write_text(json.dumps(json_stats, indent=2, default=str))
        print(f"wrote {args.json}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_md(stats, v, baseline))
        print(f"wrote {args.report}")

    print()
    print(f"VERDICT: {'B2 PASS' if overall_pass(v) else 'B2 FAIL'}")
    print(f"  avg_ready_per_distinct_title: {stats['avg_ready_per_distinct_title']:.2f} (≤3.0)")
    print(f"  exact_pair_max:               {stats['exact_pair_max']} (≤3)")
    print(f"  semantic_cluster_max:         {stats['semantic_cluster_max']} (≤6)")
    print(f"  ready_blank_title:            {stats['ready_blank_title']} (0)")
    return 0 if overall_pass(v) else 1


if __name__ == "__main__":
    sys.exit(main())

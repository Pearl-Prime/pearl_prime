#!/usr/bin/env python3
"""
Native zh_CN (Simplified Chinese) manga title / topic / EI-author synthesis.
=============================================================================

Fills the `title` / `localized_titles.zh_CN` / `topic` / `manga_author` fields
(currently `TBD`) on the ~272 live zh_CN series plans at
``config/source_of_truth/manga_series_plans/zh_CN/*.yaml``.

Mirrors the ja_JP precedent (``synthesize_manga_titles_jajp.py``, MERGED as
PR #1772): same ``apply_edits`` targeted line-replacement, same topic
round-robin, same clinical-leak filter + within-brand / global uniqueness.

Per-field provenance (LLM tier policy compliant — NO paid API, NO Qwen/Ollama):
  - title          → AUTHORED by Claude (Tier-1, operator-reviewed via PR).
                     Native Simplified Chinese, genre-faithful, the wellness
                     ``topic`` kept as INTERIOR architecture (Genre Shell
                     thesis) — never an explicit self-help / clinical label.
                     The titles live in the side map ``zhcn_titles.json`` next
                     to this script; this script only validates + applies them.
  - topic          → deterministic round-robin of the brand's primary +
                     secondary topics across its series (covers all topics).
                     No LLM. (Mecha series already have a topic → left as-is.)
  - manga_author   → generate_manga_author.generate_display_name (deterministic
                     zh_CN name pools). No LLM. (Mecha series already have an
                     author → left as-is.)

In-place, idempotent: only `: TBD` lines are rewritten, so partial runs resume
and re-runs never clobber filled values. File comments / field order preserved
(targeted line replacement, not a YAML round-trip).

This does NOT render, call any LLM/API, or touch any other locale.

Usage:
  python3 scripts/manga/synthesize_manga_titles_zhcn.py            # all
  python3 scripts/manga/synthesize_manga_titles_zhcn.py --dry-run  # validate only
  python3 scripts/manga/synthesize_manga_titles_zhcn.py --brand stillness_press
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from generate_manga_author import generate_display_name  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
ROOT = _MAIN_REPO if (not (REPO_ROOT / "config").exists()
                      and (_MAIN_REPO / "config").exists()) else REPO_ROOT

SERIES_DIR = ROOT / "config" / "source_of_truth" / "manga_series_plans" / "zh_CN"
CANONICAL_BRANDS = ROOT / "config" / "manga" / "canonical_brand_list.yaml"
TITLE_MAP = SCRIPT_DIR / "zhcn_titles.json"
REVIEW_OUT = ROOT / "artifacts" / "catalog" / "manga" / "ssot_rollup" / "zh_CN_title_synthesis_review.csv"

# Clinical / self-help stems that must never appear in a title (topic-leak guard).
# zh_CN equivalents of the ja_JP CLINICAL_STEMS set. Deliberately excludes soft
# words (心, 梦, 静, 安) that are legitimate manga vocabulary.
CLINICAL_STEMS = (
    "焦虑", "疗愈", "療愈", "治愈", "倦怠", "自我价值", "自尊", "创伤",
    "心理治疗", "心理咨询", "抑郁", "忧郁", "自我肯定", "注意力", "专注力",
    "多动", "拖延", "羞耻", "失眠症", "心理健康", "综合征", "症候群",
    "咨询师", "治疗师", "自我疗愈", "正念", "社交焦虑", "冒充者",
    "边界感", "自我关怀", "康复治疗",
)


def _leaks_topic(title: str) -> bool:
    return any(s in title for s in CLINICAL_STEMS)


def _has_cjk(s: str) -> bool:
    return any("一" <= c <= "鿿" for c in s)


def _load_yaml(p: Path) -> Any:
    with open(p, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def assign_topics(brand_info: dict, series_list: list[dict]) -> None:
    """Round-robin the brand's [primary]+secondary topics across its series.

    Mirrors the ja_JP precedent exactly: sort by (genre, series_index), then
    cycle [primary] + secondary_topics. Series that already carry a non-TBD
    topic (e.g. mecha) keep their own value.
    """
    topics = [brand_info.get("primary_topic", "")] + list(brand_info.get("secondary_topics", []) or [])
    topics = [t for t in topics if t] or ["self_worth"]
    for i, sp in enumerate(sorted(series_list, key=lambda r: (r["genre"], r["series_index"]))):
        rotated = topics[i % len(topics)]
        sp["_topic"] = rotated if sp["topic_is_tbd"] else sp["existing_topic"]


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def apply_edits(path: Path, *, title: str, topic: str, author: str) -> bool:
    """Replace `: TBD` lines in place. Idempotent. Returns True if changed.

    Only ever rewrites a line whose value is literally ``TBD`` — so an
    already-filled field (mecha topic/author) is never touched.
    """
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    in_localized = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if re.match(r"^title:\s*TBD\s*$", stripped):
            lines[i] = f"title: {_yaml_quote(title)}\n"; changed = True
        elif re.match(r"^localized_titles:\s*$", stripped):
            in_localized = True
        elif in_localized and re.match(r"^\s+zh_CN:\s*TBD\s*$", stripped):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}zh_CN: {_yaml_quote(title)}\n"; changed = True; in_localized = False
        elif re.match(r"^topic:\s*TBD\s*$", stripped):
            lines[i] = f"topic: {topic}\n"; changed = True
        elif re.match(r"^manga_author:\s*TBD\s*$", stripped):
            lines[i] = f"manga_author: {_yaml_quote(author)}\n"; changed = True
        elif stripped and not line.startswith((" ", "\t")) and in_localized:
            in_localized = False
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", help="Restrict to one brand_id")
    ap.add_argument("--limit", type=int, help="Process at most N series")
    ap.add_argument("--dry-run", action="store_true", help="Validate only; no writes")
    ap.add_argument("--no-write", action="store_true", help="Compute but do not edit YAML")
    args = ap.parse_args()

    title_map: dict[str, str] = json.loads(TITLE_MAP.read_text(encoding="utf-8"))
    brands = (_load_yaml(CANONICAL_BRANDS) or {}).get("brands", {})

    plans: list[dict] = []
    for p in sorted(SERIES_DIR.glob("*.yaml")):
        sp = _load_yaml(p) or {}
        sid = sp.get("series_id", p.stem)
        plans.append({
            "path": p, "brand_id": sp.get("brand_id", ""), "genre": sp.get("genre", ""),
            "demographic": sp.get("demographic", "general"), "series_id": sid,
            "series_index": sid.split("__")[-1],
            "title_is_tbd": str(sp.get("title", "")).strip().upper() == "TBD",
            "topic_is_tbd": str(sp.get("topic", "")).strip().upper() == "TBD",
            "author_is_tbd": str(sp.get("manga_author", "")).strip().upper() == "TBD",
            "existing_topic": sp.get("topic"),
            "existing_author": sp.get("manga_author"),
        })

    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in plans:
        by_brand[r["brand_id"]].append(r)
    for b, lst in by_brand.items():
        assign_topics(brands.get(b, {}), lst)

    # ── Pre-flight validation of the authored title map ─────────────────────
    sids = {r["series_id"] for r in plans}
    errors: list[str] = []
    missing = sids - set(title_map)
    if missing:
        errors.append(f"{len(missing)} series have no authored title: {sorted(missing)[:5]}")
    gdupes = {t: n for t, n in Counter(title_map.values()).items() if n > 1}
    if gdupes:
        errors.append(f"{len(gdupes)} GLOBAL duplicate titles: {list(gdupes)[:5]}")
    wb = defaultdict(list)
    sid2brand = {r["series_id"]: r["brand_id"] for r in plans}
    for sid, t in title_map.items():
        if sid in sid2brand:
            wb[sid2brand[sid]].append(t)
    for b, ts in wb.items():
        d = {k: v for k, v in Counter(ts).items() if v > 1}
        if d:
            errors.append(f"within-brand dup in {b}: {d}")
    for sid, t in title_map.items():
        if sid in sids:
            if not _has_cjk(t):
                errors.append(f"non-CJK title {sid}: {t!r}")
            if _leaks_topic(t):
                errors.append(f"clinical leak {sid}: {t!r}")
    if errors:
        for e in errors:
            print(f"VALIDATION ERROR: {e}", file=sys.stderr)
        return 2
    print(f"validation OK: {len(title_map)} titles, 0 dup, 0 leak, 0 non-CJK")

    todo = [r for r in plans if (not args.brand or r["brand_id"] == args.brand)]
    todo.sort(key=lambda r: (r["brand_id"], r["genre"], r["series_index"]))
    if args.limit:
        todo = todo[: args.limit]

    review_rows: list[dict] = []
    filled = skipped = 0
    t0 = time.time()
    for r in todo:
        title = title_map[r["series_id"]]
        topic = r["_topic"]
        author = (r["existing_author"] if not r["author_is_tbd"]
                  else generate_display_name(genre=r["genre"], locale="zh_CN",
                                             brand_id=r["brand_id"], topic=topic,
                                             demographic=r["demographic"]))
        wrote = False
        if not args.dry_run and not args.no_write:
            wrote = apply_edits(r["path"], title=title, topic=topic, author=author)
        if wrote or args.dry_run or args.no_write:
            filled += 1
        else:
            skipped += 1
        review_rows.append({
            "brand_id": r["brand_id"], "genre": r["genre"], "series_id": r["series_id"],
            "topic": topic, "title_zh": title, "manga_author": author, "written": wrote,
        })

    if review_rows and not args.dry_run:
        REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(REVIEW_OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(review_rows[0].keys()))
            w.writeheader(); w.writerows(review_rows)
        print(f"review sidecar → {REVIEW_OUT.relative_to(ROOT)}")
    print(f"DONE filled={filled} skipped(already-filled)={skipped} in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

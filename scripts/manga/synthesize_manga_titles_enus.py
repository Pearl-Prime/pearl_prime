#!/usr/bin/env python3
"""Native en_US manga title / topic / EI-author synthesis for the live SSOT.
=========================================================================

Fills the `title` / `localized_titles.en_US` / `topic` / `manga_author` fields
(currently `TBD`) on the live en_US series plans at
``config/source_of_truth/manga_series_plans/en_US/*.yaml``.

Per-field provenance (LLM tier policy compliant):
  - title          → AUTHORED by Claude (Tier-1, operator-reviewed) and stored in
                     ``scripts/manga/en_us_manga_titles.py``. No LLM API call is
                     made at synthesis time (the operator asked Claude to write the
                     en_US titles directly). Native English, genre-faithful, the
                     wellness topic kept as INTERIOR architecture (Genre Shell
                     thesis) — never an explicit self-help / clinical label.
  - topic          → deterministic rotation of the brand's primary + secondary
                     topics across its series (covers all topics). No LLM.
                     Series whose topic is already set (e.g. mecha) keep it.
  - manga_author   → generate_manga_author.generate_display_name (deterministic
                     English name pools). No LLM. Series whose author is already
                     set (e.g. mecha) keep it.

This mirrors ``synthesize_manga_titles_jajp.py`` (apply_edits, leak filter, dedup)
exactly, swapping the Qwen generator for the authored-title table.

In-place, idempotent: only `: TBD` lines are rewritten, so partial runs resume and
re-runs never clobber filled values. File comments / field order are preserved
(targeted line replacement, not a YAML round-trip).

This does NOT render, call any paid API, or touch any other locale.

Usage:
  python3 scripts/manga/synthesize_manga_titles_enus.py            # all
  python3 scripts/manga/synthesize_manga_titles_enus.py --brand stillness_press
  python3 scripts/manga/synthesize_manga_titles_enus.py --check    # QA only, no writes
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from generate_manga_author import generate_display_name  # noqa: E402
from en_us_manga_titles import TITLES  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
ROOT = _MAIN_REPO if (not (REPO_ROOT / "config").exists()
                      and (_MAIN_REPO / "config").exists()) else REPO_ROOT

SERIES_DIR = ROOT / "config" / "source_of_truth" / "manga_series_plans" / "en_US"
CANONICAL_BRANDS = ROOT / "config" / "manga" / "canonical_brand_list.yaml"
REVIEW_OUT = ROOT / "artifacts" / "catalog" / "manga" / "ssot_rollup" / "en_US_title_synthesis_review.csv"

# ── Topic flavour (en_US INTERIOR-theme phrase, for the leak guard) ──────────
# Each maps the wellness topic to the explicit clinical/self-help word(s) that
# must NEVER appear in a title. Deliberately excludes soft, legitimate manga
# vocabulary (e.g. "quiet", "calm", "rest") that is allowed as genre flavour.
TOPIC_LEAK_WORDS: dict[str, list[str]] = {
    "anxiety": ["anxiety", "anxious", "anxieties"],
    "sleep": ["insomnia", "insomniac"],
    "burnout": ["burnout", "burnt out", "burned out"],
    "overthinking": ["overthinking", "overthink", "overthinker"],
    "grief": ["bereavement"],
    "somatic_healing": ["somatic"],
    "social_anxiety": ["social anxiety"],
    "self_worth": ["self-worth", "self worth", "low self-esteem", "self-esteem", "self esteem"],
    "imposter_syndrome": ["imposter syndrome", "impostor syndrome", "imposter-syndrome"],
    "trauma_recovery": ["trauma", "traumatic", "ptsd"],
    "shame": ["self-loathing"],
    "boundaries": ["codependency", "codependent"],
    "courage": [],
    "compassion": ["self-compassion", "self compassion"],
    "financial_anxiety": ["financial anxiety", "money anxiety"],
    "adhd_focus": ["adhd", "a.d.h.d", "attention deficit", "hyperactivity"],
    "self_compassion": ["self-compassion", "self compassion"],
}

# Clinical / self-help / therapy stems that must never appear in ANY title,
# regardless of topic (a hard global leak guard). Word-boundary matched.
GLOBAL_CLINICAL_STEMS: list[str] = [
    "anxiety", "anxious", "burnout", "depression", "depressed", "trauma", "traumatic",
    "ptsd", "therapy", "therapist", "therapeutic", "self-help", "self help",
    "mental health", "mental-health", "wellness", "wellbeing", "well-being",
    "healing", "heal", "cure", "diagnosis", "disorder", "syndrome", "clinical",
    "psychiatric", "psychotherapy", "counseling", "counselling", "counselor",
    "self-worth", "self worth", "self-esteem", "self esteem", "self-care", "self care",
    "self-love", "self-compassion", "self compassion", "imposter syndrome",
    "impostor syndrome", "insomnia", "overthinking", "somatic", "adhd",
    "recovery", "recover", "mindfulness", "meditation",
]


def _word_in(title: str, needle: str) -> bool:
    """Whole-word / phrase membership, case-insensitive."""
    pat = r"\b" + re.escape(needle.lower()) + r"\b"
    return re.search(pat, title.lower()) is not None


def leaks_topic(title: str, topic: str) -> list[str]:
    """Return the list of leak stems found in `title` (empty = clean)."""
    found: list[str] = []
    for stem in GLOBAL_CLINICAL_STEMS:
        if _word_in(title, stem):
            found.append(stem)
    for stem in TOPIC_LEAK_WORDS.get(topic, []):
        if _word_in(title, stem) and stem not in found:
            found.append(stem)
    return found


def _load_yaml(p: Path) -> Any:
    with open(p, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def assign_topics(brand_info: dict, series_list: list[dict]) -> None:
    """Round-robin the brand's [primary]+secondary topics across its series.

    Series whose topic is already set (not TBD) keep it and are skipped in the
    rotation index advance only for the slot they occupy — to match ja_JP, the
    rotation is computed over the brand's full sorted series list and a series
    keeps its pre-filled topic if present.
    """
    topics = [brand_info.get("primary_topic", "")] + list(brand_info.get("secondary_topics", []) or [])
    topics = [t for t in topics if t] or ["self_worth"]
    for i, sp in enumerate(sorted(series_list, key=lambda r: (r["genre"], r["series_index"]))):
        sp["_topic"] = sp["topic_filled"] if not sp["topic_is_tbd"] else topics[i % len(topics)]


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def apply_edits(path: Path, *, title: str, topic: str, author: str) -> bool:
    """Replace `: TBD` lines in place. Idempotent. Returns True if changed."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    in_localized = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if re.match(r"^title:\s*TBD\s*$", stripped):
            lines[i] = f"title: {_yaml_quote(title)}\n"; changed = True
        elif re.match(r"^localized_titles:\s*$", stripped):
            in_localized = True
        elif in_localized and re.match(r"^\s+en_US:\s*TBD\s*$", stripped):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}en_US: {_yaml_quote(title)}\n"; changed = True; in_localized = False
        elif re.match(r"^topic:\s*TBD\s*$", stripped):
            lines[i] = f"topic: {topic}\n"; changed = True
        elif re.match(r"^manga_author:\s*TBD\s*$", stripped):
            lines[i] = f"manga_author: {_yaml_quote(author)}\n"; changed = True
        elif stripped and not line.startswith((" ", "\t")) and in_localized:
            in_localized = False
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def load_plans() -> list[dict]:
    plans: list[dict] = []
    for p in sorted(SERIES_DIR.glob("*.yaml")):
        sp = _load_yaml(p) or {}
        sid = sp.get("series_id", p.stem)
        topic_raw = str(sp.get("title", "")).strip()
        plans.append({
            "path": p, "name": p.name, "brand_id": sp.get("brand_id", ""),
            "genre": sp.get("genre", ""), "demographic": sp.get("demographic", "general"),
            "series_id": sid, "series_index": sid.split("__")[-1],
            "title_is_tbd": topic_raw.upper() == "TBD",
            "title_filled": topic_raw,
            "topic_is_tbd": str(sp.get("topic", "")).strip().upper() == "TBD",
            "topic_filled": str(sp.get("topic", "")).strip(),
            "author_is_tbd": str(sp.get("manga_author", "")).strip().upper() == "TBD",
        })
    return plans


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", help="Restrict to one brand_id")
    ap.add_argument("--limit", type=int, help="Process at most N series")
    ap.add_argument("--check", action="store_true", help="QA only — validate, do not write")
    ap.add_argument("--no-write", action="store_true", help="Generate but do not edit YAML (review only)")
    args = ap.parse_args()

    brands = (_load_yaml(CANONICAL_BRANDS) or {}).get("brands", {})
    plans = load_plans()

    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in plans:
        by_brand[r["brand_id"]].append(r)
    for b, lst in by_brand.items():
        assign_topics(brands.get(b, {}), lst)

    todo = [r for r in plans if (not args.brand or r["brand_id"] == args.brand)]
    todo.sort(key=lambda r: (r["brand_id"], r["genre"], r["series_index"]))
    if args.limit:
        todo = todo[: args.limit]

    # ── Pre-flight validation: every TBD-title series must have an authored title,
    #    leak-free, globally + within-brand unique ─────────────────────────────
    errors: list[str] = []
    used_global: dict[str, str] = {}              # title(lower) -> series_id
    used_by_brand: dict[str, dict[str, str]] = defaultdict(dict)
    review_rows: list[dict] = []
    filled = skipped = failed = 0
    t0 = time.time()

    for r in todo:
        if not r["title_is_tbd"]:
            skipped += 1
            continue
        title = TITLES.get(r["name"])
        if not title:
            errors.append(f"MISSING authored title: {r['name']}")
            failed += 1
            continue
        topic = r["_topic"]
        # leak guard
        leaks = leaks_topic(title, topic)
        if leaks:
            errors.append(f"LEAK {r['name']}: '{title}' contains {leaks}")
            failed += 1
            continue
        # within-brand uniqueness
        tl = title.lower()
        if tl in used_by_brand[r["brand_id"]]:
            errors.append(f"BRAND-DUP {r['brand_id']}: '{title}' also in "
                          f"{used_by_brand[r['brand_id']][tl]}")
            failed += 1
            continue
        # global uniqueness
        if tl in used_global:
            errors.append(f"GLOBAL-DUP: '{title}' in {r['name']} also in {used_global[tl]}")
            failed += 1
            continue
        used_by_brand[r["brand_id"]][tl] = r["series_id"]
        used_global[tl] = r["series_id"]

        author = generate_display_name(genre=r["genre"], locale="en_US",
                                       brand_id=r["brand_id"], topic=topic,
                                       demographic=r["demographic"])
        review_rows.append({
            "brand_id": r["brand_id"], "genre": r["genre"], "series_id": r["series_id"],
            "topic": topic, "topic_was_tbd": r["topic_is_tbd"],
            "title": title, "manga_author": author, "author_was_tbd": r["author_is_tbd"],
            "_path": r["path"], "_topic_is_tbd": r["topic_is_tbd"],
            "_author_is_tbd": r["author_is_tbd"],
        })

    # Also cross-check pre-filled titles (the already-titled stillness series) for
    # global collision with the authored set.
    for r in todo:
        if r["title_is_tbd"]:
            continue
        tl = r["title_filled"].lower()
        if tl and tl in used_global and used_global[tl] != r["series_id"]:
            errors.append(f"GLOBAL-DUP vs pre-filled: '{r['title_filled']}' "
                          f"({r['series_id']}) collides with {used_global[tl]}")
            failed += 1

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        print(f"\n{len(errors)} error(s). No files written.")
        return 1

    # ── Write phase ─────────────────────────────────────────────────────────
    if not args.check and not args.no_write:
        for row in review_rows:
            topic_to_write = row["topic"] if row["_topic_is_tbd"] else None
            author_to_write = row["manga_author"] if row["_author_is_tbd"] else None
            # apply_edits only rewrites `: TBD` lines, so passing the value is safe
            # even when the field is already filled (the regex won't match).
            wrote = apply_edits(
                row["_path"], title=row["title"],
                topic=(topic_to_write or row["topic"]),
                author=(author_to_write or row["manga_author"]),
            )
            row["written"] = wrote
            if wrote:
                filled += 1
    else:
        filled = len(review_rows)

    if review_rows:
        REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
        cols = ["brand_id", "genre", "series_id", "topic", "topic_was_tbd",
                "title", "manga_author", "author_was_tbd"]
        with open(REVIEW_OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(review_rows)
        print(f"review sidecar → {REVIEW_OUT.relative_to(ROOT)}")

    mode = "CHECK" if (args.check or args.no_write) else "WRITE"
    print(f"DONE [{mode}] authored={len(review_rows)} written={filled} "
          f"skipped={skipped} failed={failed} leaks=0 dups=0 in {time.time()-t0:.1f}s")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

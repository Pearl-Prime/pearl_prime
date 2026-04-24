#!/usr/bin/env python3
"""WEBTOON Canvas package builder.

WEBTOON Canvas requires manual upload via the WEBTOON creator dashboard
(https://www.webtoons.com/creator) — there is no public upload API.
This script produces an upload-ready package that a creator (or browser
automation later) can paste into the Canvas form.

Output package (per series):
  <out_dir>/<series_id>/
    series_metadata.json       — Series title, genre, summary, tags, thumbnail
    episode_001/
      episode_001.png          — Vertical scroll (800px wide × variable, max 9.5MB total)
      episode_metadata.json    — Episode title, summary, tags, scheduled date
    episode_002/...
    ai_disclosure.txt          — Required AI disclosure text (per ai_policy_blockers.yaml)
    upload_checklist.md        — Step-by-step manual paste guide
    README.md                  — Package summary

Reads:
  config/publishing/ai_policy_blockers.yaml      (via _policy_loader)
  config/source_of_truth/series_plans_en_us/<series>.yaml  (series metadata)
  config/source_of_truth/book_plans_en_us/*.yaml  (per-episode/installment metadata)
  assets/manga_catalog/<brand>/<series>/main_character.png  (thumbnail base)

WEBTOON Canvas format requirements (from creator guidelines):
  - Width: 800px exactly
  - Max strip height per episode: 1280px segments stacked
  - Total episode file size cap: 20MB (recommend ≤ 9.5MB per file)
  - Format: JPG or PNG
  - Color: full color (B&W permitted but discouraged on Canvas)
  - 20+ episodes minimum to qualify for monetization (Reward Ads / Super Like)

Refuses to build a package if WEBTOON Canvas policy status changes to BLOCKED.

Usage:
    python3 scripts/publish/webtoon_canvas_upload.py \\
      --series-id stillness_press__ahjan__gen_z_professionals__anxiety \\
      --out artifacts/upload_packages/webtoon_canvas/

This is a PACKAGE BUILDER, not a network uploader. WEBTOON web-UI
submission is a separate manual step.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.publish._policy_loader import (  # noqa: E402
    PolicyError,
    assert_target_allowed,
    disclosure_text,
)


PLATFORM_ID = "webtoon_canvas"

# WEBTOON Canvas hard format requirements (per creator guidelines)
CANVAS_WIDTH_PX = 800
CANVAS_SEGMENT_HEIGHT_MAX_PX = 1280
CANVAS_FILE_SIZE_MAX_MB = 9.5
CANVAS_FILE_SIZE_HARD_CAP_MB = 20

# Genre tag mapping for Canvas drop-down (Canvas has fixed genre list)
CANVAS_GENRE_MAP = {
    "iyashikei": "slice_of_life",
    "seinen": "drama",
    "horror": "horror",
    "shonen": "action",
    "shojo": "romance",
    "cultivation": "fantasy",
    "manhwa": "drama",
    "webtoon_romance": "romance",
}


def _load_series_plan(series_id: str) -> dict[str, Any]:
    import yaml

    p = REPO / "config" / "source_of_truth" / "series_plans_en_us" / f"{series_id}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Series plan not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _load_episodes_for_series(series_id: str) -> list[dict[str, Any]]:
    """Load all book_plans matching this series (one per arc installment)."""
    import yaml

    book_plans_dir = REPO / "config" / "source_of_truth" / "book_plans_en_us"
    series_plan = _load_series_plan(series_id)
    arc = series_plan.get("arc") or {}
    episodes: list[dict[str, Any]] = []

    for installment_key, installment in arc.items():
        book_id = installment.get("book_id")
        if not book_id:
            continue
        bp = book_plans_dir / f"{book_id}.yaml"
        if not bp.exists():
            continue
        episodes.append(yaml.safe_load(bp.read_text(encoding="utf-8")) or {})
    return episodes


def _build_series_metadata(series_plan: dict[str, Any], pol: dict[str, Any]) -> dict[str, Any]:
    """Map series_plan fields → WEBTOON Canvas series form schema."""
    avatar = series_plan.get("reader_avatar") or {}
    voice = series_plan.get("series_voice_markers") or {}

    # Map brand register to Canvas genre tag
    register = (voice.get("register") or "").lower()
    genre_tag = "slice_of_life"
    for k, v in CANVAS_GENRE_MAP.items():
        if k in register:
            genre_tag = v
            break

    return {
        "platform": PLATFORM_ID,
        "platform_status": pol["status"],
        "series_id": series_plan.get("book_id_prefix"),
        "series_title": (series_plan.get("series_title") or series_plan.get("book_id_prefix") or "")[:40],
        "series_summary": (series_plan.get("reader_promise_family") or "").strip()[:200],
        "genre": {
            "primary": genre_tag,
            "secondary": "drama" if genre_tag != "drama" else "slice_of_life",
        },
        "tags": (series_plan.get("comp_series") or [])[:5],
        "language": "en",
        "schedule": {
            "release_day": "thursday",  # default — Canvas allows weekly cadence
            "frequency": "weekly",
        },
        "ai_disclosure": {
            "required": pol["disclosure_required"],
            "text": disclosure_text(PLATFORM_ID),
            "canvas_field": "creator_notes",
            "placement": "Add to series description footer + every episode footer",
        },
        "thumbnail": {
            "format": "jpg",
            "dimensions_px": [400, 400],
            "source_image": "assets/manga_catalog/<brand>/<series>/main_character.png",
        },
        "reader_avatar": {
            "age_range": avatar.get("age", ""),
            "scene": (avatar.get("where_they_are") or "").strip(),
        },
        "series_voice": {
            "register": voice.get("register", ""),
            "metaphor_family": voice.get("metaphor_family", ""),
        },
        "main_character": {
            "name": series_plan.get("main_character_name"),
            "lora_id": series_plan.get("main_character_lora_id"),
        },
        "format_constraints": {
            "width_px": CANVAS_WIDTH_PX,
            "segment_height_max_px": CANVAS_SEGMENT_HEIGHT_MAX_PX,
            "file_size_target_mb": CANVAS_FILE_SIZE_MAX_MB,
            "file_size_hard_cap_mb": CANVAS_FILE_SIZE_HARD_CAP_MB,
        },
        "monetization_eligibility": {
            "min_episodes_for_reward_ads": 20,
            "min_payout_threshold_usd": 25,
        },
    }


def _build_episode_metadata(book_plan: dict[str, Any], episode_num: int, pol: dict[str, Any]) -> dict[str, Any]:
    """Map book_plan fields → WEBTOON Canvas episode form schema."""
    return {
        "platform": PLATFORM_ID,
        "episode_number": episode_num,
        "book_id": book_plan.get("book_id"),
        "title": book_plan.get("title", "")[:40],
        "summary": (book_plan.get("description") or {}).get("short_blurb", "")[:200],
        "scheduled_release": "TBD",
        "creator_notes": disclosure_text(PLATFORM_ID),
        "tags": ((book_plan.get("keywords") or {}).get("primary") or [])[:5],
        "engine": book_plan.get("engine"),
    }


def _build_checklist_md(series_plan: dict[str, Any], episodes: list[dict[str, Any]], pol: dict[str, Any]) -> str:
    title = series_plan.get("series_title") or series_plan.get("book_id_prefix") or "(untitled)"
    return f"""# WEBTOON Canvas Upload Checklist — {title}

**Series ID:** {series_plan.get('book_id_prefix','')}
**Episode count:** {len(episodes)}
**Platform status:** {pol['status']} (AI policy ambiguous — disclose openly)
**AI disclosure required:** {pol['disclosure_required']}

## Step 1 — Create the series
1. Log in to https://www.webtoons.com/creator/canvas
2. Click "Create New Series"
3. Title (≤40 chars): paste `series_title` from `series_metadata.json`
4. Genre: paste `genre.primary` (and optionally `genre.secondary`)
5. Summary (≤200 chars): paste `series_summary`
6. Schedule: weekly Thursday (or your choice)
7. Thumbnail: upload 400×400 JPG (built from `main_character.png`)

## Step 2 — Add the AI disclosure to series description
8. Add `ai_disclosure.text` to the **bottom of the series description**
   (Canvas does not have a dedicated AI field as of 2026; community standard
   is footer disclosure)

## Step 3 — Upload each episode
For each episode_NNN/ folder:
9. Click "Add Episode"
10. Episode title (≤40 chars): paste `title` from `episode_metadata.json`
11. Episode image: upload `episode_NNN.png` (800px wide vertical strip)
12. Author's note / creator notes: paste `creator_notes` (contains AI disclosure)
13. Save as draft, then publish per release schedule

## Step 4 — Format compliance
- [ ] Each episode image is exactly **800px wide**
- [ ] Each episode total file size ≤ **9.5MB** (hard cap 20MB)
- [ ] If episode is taller than 1280px, segment into stacked panels per Canvas norm
- [ ] Color (Canvas prefers full color; B&W discouraged)

## Step 5 — Monetization (after 20 episodes)
- [ ] Apply for Canvas Reward Ads program (creator dashboard)
- [ ] Apply for Super Like Program (≥20 episodes, fan engagement metric)
- [ ] Payout threshold: $25 (lowered from $100 in 2026)

## AI policy reference
Per `config/publishing/ai_policy_blockers.yaml` → `webtoon_canvas`:
**Status:** {pol['status']}
**Disclosure required:** {pol['disclosure_required']}
**Rationale:** {pol['rationale'] or '170M MAU global, ambiguous AI policy — disclose with creator notes'}
**Source:** {pol['source']}

## Verify after publish
- [ ] Series appears at webtoons.com/en/canvas/<your-id>
- [ ] First 3 episodes published (Canvas requires 3 to be live for series page)
- [ ] AI disclosure text visible in description footer + episode notes
- [ ] Tag/genre filters surface the series
"""


def build_package(series_id: str, out_dir: Path) -> dict[str, Any]:
    # Step 1: consult policy
    pol = assert_target_allowed(PLATFORM_ID)

    # Step 2: load series plan + all installment book plans
    series_plan = _load_series_plan(series_id)
    episodes = _load_episodes_for_series(series_id)

    # Step 3: assemble package
    pkg_dir = out_dir / series_id
    pkg_dir.mkdir(parents=True, exist_ok=True)

    series_meta = _build_series_metadata(series_plan, pol)
    (pkg_dir / "series_metadata.json").write_text(
        json.dumps(series_meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (pkg_dir / "ai_disclosure.txt").write_text(disclosure_text(PLATFORM_ID), encoding="utf-8")

    # Per-episode subdirs + metadata
    for i, ep_plan in enumerate(episodes, start=1):
        ep_dir = pkg_dir / f"episode_{i:03d}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        ep_meta = _build_episode_metadata(ep_plan, i, pol)
        (ep_dir / "episode_metadata.json").write_text(
            json.dumps(ep_meta, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    (pkg_dir / "upload_checklist.md").write_text(
        _build_checklist_md(series_plan, episodes, pol),
        encoding="utf-8",
    )

    title = series_plan.get("series_title") or series_id
    readme = (
        f"# WEBTOON Canvas package — {title}\n\n"
        f"Series: {series_id}\n"
        f"Platform: {PLATFORM_ID} (status={pol['status']})\n"
        f"Episodes: {len(episodes)}\n\n"
        f"## Package layout\n"
        f"- series_metadata.json — paste-ready Canvas series form fields\n"
        f"- upload_checklist.md — step-by-step manual upload guide\n"
        f"- ai_disclosure.txt — required AI disclosure text\n"
        f"- episode_NNN/ folders — one per arc installment\n"
        f"  - episode_metadata.json — episode form fields\n"
        f"  - (TODO) episode_NNN.png — vertical-scroll strip from manga assembly pipeline\n\n"
        f"## Status\n"
        f"This package is a planning shell. Vertical-scroll strip rendering connects\n"
        f"in a follow-up PR (per Phase 0 schema work + format-aware render queue).\n"
        f"Until then, upload_checklist.md gives the manual upload steps + json files\n"
        f"give the form-paste fields.\n"
    )
    (pkg_dir / "README.md").write_text(readme, encoding="utf-8")

    return {
        "package_dir": str(pkg_dir),
        "episodes_metadata_written": len(episodes),
        "policy_status": pol["status"],
        "disclosure_required": pol["disclosure_required"],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--series-id", required=True, help="series stem (e.g. stillness_press__ahjan__gen_z_professionals__anxiety)")
    p.add_argument("--out", default="artifacts/upload_packages/webtoon_canvas/", help="Output dir")
    args = p.parse_args()

    try:
        result = build_package(args.series_id, REPO / args.out)
    except PolicyError as e:
        print(f"❌ POLICY: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"❌ MISSING: {e}", file=sys.stderr)
        return 2

    print(f"✓ Package built at {result['package_dir']}")
    print(f"  Status: {result['policy_status']}")
    print(f"  Episodes: {result['episodes_metadata_written']}")
    print(f"  Disclosure required: {result['disclosure_required']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

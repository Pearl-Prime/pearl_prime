#!/usr/bin/env python3
"""One-off sample generator for Lane E self-QA (not a CI gate, not imported anywhere).

Writes a hand-verifiable sample of each of the 4 new formats
(story_led / carousel_atoms / thread_atoms / video_beat_atoms) using the real Lane C
promoted atom rows, for both fully-covered pilot cells.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.social.deterministic_social import (  # noqa: E402
    build_atom_carousel_package,
    build_atom_thread_package,
    build_atom_video_beat_script,
    generate_story_led_copy_package,
)

OUT = REPO_ROOT / "artifacts/qa/social_atom_composition_pilot_20260721/lane_e_new_format_samples_20260723"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    samples = {
        "story_led__burnout_corporate_managers": generate_story_led_copy_package(
            "corporate_managers", "burnout", "instagram_feed_portrait"
        ),
        "carousel_atoms__burnout_corporate_managers": build_atom_carousel_package(
            "corporate_managers", "burnout", "instagram_carousel"
        ),
        "thread_atoms__anxiety_gen_z_professionals": build_atom_thread_package(
            "gen_z_professionals", "anxiety", "x_image"
        ),
        "video_beat_atoms__burnout_corporate_managers": build_atom_video_beat_script(
            "corporate_managers", "burnout", "tiktok_reels_shorts_vertical"
        ),
    }
    (OUT / "samples.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Lane E — new-format assembly samples (2026-07-23)", ""]
    lines.append(
        "Real output from the 4 newly-wired atom-backed formats, generated from the actual "
        "promoted rows in `SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl` "
        "(Lane C, 2026-07-23). Hand-verify each reads as one authored voice."
    )
    lines.append("")

    s = samples["story_led__burnout_corporate_managers"]
    lines += [
        "## 1. story_led — burnout x corporate_managers (MICRO_STORY -> CASE_PROOF -> TOOL_STEP -> CTA_ANCHOR)",
        "",
        f"Chain complete: `{s['story_led_chain_complete']}` | atoms: `{s['selected_atom_ids']}`",
        "",
        "```",
        s["caption"],
        "```",
        "",
    ]

    c = samples["carousel_atoms__burnout_corporate_managers"]
    lines += [
        "## 2. carousel_atoms — burnout x corporate_managers (6-slide open-loop arc)",
        "",
        f"Chain complete: `{c['chain_complete']}` | slide_count: `{c['slide_count']}`",
        "",
    ]
    for slide in c["slides"]:
        lines.append(f"- **Slide {slide['index']}** (`{slide['atom_id']}`): {slide['text']}")
    lines.append("")

    t = samples["thread_atoms__anxiety_gen_z_professionals"]
    lines += [
        "## 3. thread_atoms — anxiety x gen_z_professionals (Hook -> Context -> Position -> Invitation)",
        "",
        f"Chain complete: `{t['chain_complete']}` | post_count: `{t['post_count']}`",
        "",
    ]
    for post in t["posts"]:
        lines.append(f"- **Post {post['index']}/{ t['post_count']}** (`{post['atom_id']}`, {post['char_count']} chars): {post['text']}")
    lines.append("")

    v = samples["video_beat_atoms__burnout_corporate_managers"]
    lines += [
        "## 4. video_beat_atoms — burnout x corporate_managers (0-3s hook / 3-8s agitation / 8-20s value / 20-25s proof / final CTA)",
        "",
        f"Chain complete: `{v['chain_complete']}` | beat_count: `{v['beat_count']}`",
        "",
    ]
    for beat in v["beats"]:
        lines.append(f"- **{beat['beat_role']}** ({beat['start_s']}s-{beat['end_s']}s, `{beat['atom_id']}`): {beat['text']}")
    lines.append("")

    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'samples.json'} and {OUT / 'README.md'}")


if __name__ == "__main__":
    main()

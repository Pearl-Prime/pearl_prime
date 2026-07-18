#!/usr/bin/env python3
"""Build and validate the final manga blind-read packet.

The packet is always blocked until a human scorecard and explicit operator approval
exist. Automated checks cannot supply those decisions.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

REQUIRED_SCORE_FIELDS = (
    "reader_id",
    "episode_id",
    "story_flow_score",
    "genre_hook_score",
    "subtle_embed_score",
    "lettering_readability_score",
    "layout_readability_score",
    "visual_composition_score",
    "approve",
)
CHECKLISTS = (
    "no_floating_or_unclear_layered_panels",
    "coherent_story_flow",
    "genre_hook_works",
    "subtle_embed_without_lecture",
    "teacher_music_diegetic_if_enabled",
    "lettering_readable",
    "page_webtoon_layout_readable",
)


def scorecard_template(episode_id: str = "") -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "reader_id": "",
        "episode_id": episode_id,
        "story_flow_score": None,
        "genre_hook_score": None,
        "subtle_embed_score": None,
        "lettering_readability_score": None,
        "layout_readability_score": None,
        "visual_composition_score": None,
        "checklist": {key: None for key in CHECKLISTS},
        "approve": None,
        "notes": "",
    }


def validate_human_bar(
    *,
    scorecards: list[Path],
    operator_approval: Path | None,
    minimum_score: int = 4,
) -> dict[str, Any]:
    failures: list[str] = []
    cards: list[dict[str, Any]] = []
    if not scorecards:
        failures.append("judge_scorecards_missing")
    for path in scorecards:
        if not path.is_file():
            failures.append(f"scorecard_missing:{path}")
            continue
        card = json.loads(path.read_text(encoding="utf-8"))
        cards.append(card)
        for field in REQUIRED_SCORE_FIELDS:
            if card.get(field) in (None, ""):
                failures.append(f"{path.name}:missing:{field}")
        for key in CHECKLISTS:
            if (card.get("checklist") or {}).get(key) is not True:
                failures.append(f"{path.name}:checklist_not_true:{key}")
        for field in (
            "story_flow_score",
            "genre_hook_score",
            "subtle_embed_score",
            "lettering_readability_score",
            "layout_readability_score",
            "visual_composition_score",
        ):
            value = card.get(field)
            if not isinstance(value, (int, float)) or value < minimum_score:
                failures.append(f"{path.name}:score_below_bar:{field}")
        if card.get("approve") is not True:
            failures.append(f"{path.name}:reader_did_not_approve")

    approval_present = bool(operator_approval and operator_approval.is_file())
    if not approval_present:
        failures.append("operator_approval_missing")
    else:
        approval = json.loads(operator_approval.read_text(encoding="utf-8"))
        if approval.get("approved") is not True:
            failures.append("operator_approval_not_true")
        if not approval.get("operator_id"):
            failures.append("operator_id_missing")

    return {
        "blind-read-bar": "green" if not failures else "blocked",
        "operator-approval": "present" if approval_present else "missing",
        "judge-scorecards": "present" if cards else "missing",
        "manga-100pct-final": "GREEN" if not failures else "NOT_GREEN",
        "scorecard_count": len(cards),
        "failures": failures,
    }


def build_packet(
    *,
    completed_output: Path,
    proof_packet: Path,
    out_dir: Path,
    episode_id: str,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    links = {
        "completed_output": str(completed_output),
        "proof_packet": str(proof_packet),
    }
    (out_dir / "reading_order.md").write_text(
        "# Reading order\n\n"
        "1. Read the completed page sequence in its declared direction.\n"
        "2. Read the webtoon strip separately when present.\n"
        "3. Complete the scorecard without consulting technical gate results.\n",
        encoding="utf-8",
    )
    (out_dir / "comparator_rubric.md").write_text(
        "# Comparator rubric\n\n"
        "- 1: not readable / not functioning\n"
        "- 2: major revision\n"
        "- 3: understandable but below release bar\n"
        "- 4: release-ready for the scoped audience\n"
        "- 5: exceptional\n",
        encoding="utf-8",
    )
    (out_dir / "story_doctrine_checklist.md").write_text(
        "# Story and doctrine checklist\n\n"
        "- [ ] Coherent story flow\n"
        "- [ ] Genre hook works\n"
        "- [ ] Subtle embed works without lecture\n"
        "- [ ] Teacher/music mode feels diegetic when enabled\n",
        encoding="utf-8",
    )
    (out_dir / "lettering_layout_checklist.md").write_text(
        "# Lettering and layout checklist\n\n"
        "- [ ] Lettering is readable\n"
        "- [ ] Reading order is unambiguous\n"
        "- [ ] Page layout is readable\n"
        "- [ ] Webtoon layout is readable\n",
        encoding="utf-8",
    )
    (out_dir / "visual_composition_checklist.md").write_text(
        "# Visual composition checklist\n\n"
        "- [ ] No floating subjects\n"
        "- [ ] No unclear layered panels\n"
        "- [ ] Support/contact reads naturally\n"
        "- [ ] Panel purpose is visually legible\n",
        encoding="utf-8",
    )
    template = scorecard_template(episode_id)
    (out_dir / "judge_scorecard_TEMPLATE.json").write_text(
        json.dumps(template, indent=2) + "\n",
        encoding="utf-8",
    )
    payload = {
        "episode_id": episode_id,
        "links": links,
        "blind-read-bar": "blocked",
        "operator-approval": "missing",
        "judge-scorecards": "missing",
        "manga-100pct-final": "NOT_GREEN",
        "blocker": "human scorecard and operator approval not yet present",
    }
    (out_dir / "packet_manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--completed-output", required=True, type=Path)
    build.add_argument("--proof-packet", required=True, type=Path)
    build.add_argument("--out-dir", required=True, type=Path)
    build.add_argument("--episode-id", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--scorecard", action="append", type=Path, default=[])
    verify.add_argument("--operator-approval", type=Path)
    verify.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.command == "build":
        result = build_packet(
            completed_output=args.completed_output,
            proof_packet=args.proof_packet,
            out_dir=args.out_dir,
            episode_id=args.episode_id,
        )
        print(json.dumps(result, indent=2))
        return 2

    result = validate_human_bar(
        scorecards=args.scorecard,
        operator_approval=args.operator_approval,
    )
    text = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["blind-read-bar"] == "green" else 2


if __name__ == "__main__":
    raise SystemExit(main())

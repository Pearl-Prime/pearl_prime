#!/usr/bin/env python3
"""Build an advisory human-judge rating packet from existing local artifacts."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718" / "spec4_human_judge_packet"

CHAPTER_RE = re.compile(r"(?m)^(?:#\s*)?Chapter\s+(\d+)\b.*$")

RUBRIC = [
    "story_event_stake_turn_cost_residue",
    "same_person_continuity",
    "reader_state_entry_exit_change",
    "atom_depth_beyond_bullets",
    "exercise_tool_aha_integration",
    "source_quote_composite_bridge_truth",
    "prose_naturalness_register_non_template",
    "production_boundary_awareness",
]


def split_chapters(text: str) -> list[tuple[str, str]]:
    matches = list(CHAPTER_RE.finditer(text or ""))
    if not matches:
        stripped = (text or "").strip()
        return [("chapter_001", stripped)] if stripped else []
    chapters: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        label = f"chapter_{int(match.group(1)):03d}"
        chapters.append((label, text[match.start() : end].strip()))
    return chapters


def discover_samples(repo_root: Path = REPO_ROOT, *, max_samples: int = 20) -> list[dict[str, Any]]:
    paths = sorted((repo_root / "artifacts" / "qa").glob("**/book.txt"))
    samples: list[dict[str, Any]] = []
    target_slices = ("strong_candidate", "mixed_candidate", "weak_candidate")
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for chapter_label, chapter_text in split_chapters(text):
            if len(chapter_text.split()) < 120:
                continue
            rel = str(path.relative_to(repo_root))
            sample_id = f"HCJ-{len(samples) + 1:03d}"
            samples.append(
                {
                    "sample_id": sample_id,
                    "source_artifact": rel,
                    "chapter_label": chapter_label,
                    "target_slice": target_slices[len(samples) % len(target_slices)],
                    "rating_status": "operator_rating_needed",
                    "rater": "",
                    "rating_date": "",
                    "rating_kind": "",
                    "word_count": len(chapter_text.split()),
                    "text_excerpt": chapter_text[:1600],
                }
            )
            if len(samples) >= max_samples:
                return samples
    return samples


def build_packet(repo_root: Path = REPO_ROOT, *, max_samples: int = 20) -> dict[str, Any]:
    samples = discover_samples(repo_root, max_samples=max_samples)
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_spec": "docs/specs/session_mining_batch_20260718/HUMAN_CALIBRATED_JUDGE_V1_SPEC.md",
        "hard_ship_gate_created": False,
        "production_public_release_authorized": False,
        "operator_ratings_needed": True,
        "rubric_dimensions": RUBRIC,
        "score_scale": {
            "1": "fails the dimension or creates release risk",
            "2": "weak or partial",
            "3": "structurally present but not persuasive",
            "4": "strong with minor reservations",
            "5": "operator-ready exemplar for this dimension",
        },
        "samples": samples,
        "stats": {"chapters_selected": len(samples)},
    }


def write_packet(packet: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "sample_manifest.json"
    rubric_path = output_dir / "rating_rubric.json"
    contract_path = output_dir / "advisory_judge_contract.json"
    readme_path = output_dir / "README_FOR_OPERATOR.md"
    manifest_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rubric_path.write_text(
        json.dumps(
            {
                "rubric_dimensions": packet["rubric_dimensions"],
                "score_scale": packet["score_scale"],
                "operator_ratings_needed": True,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    contract_path.write_text(
        json.dumps(
            {
                "artifact_type": "advisory_judge_contract",
                "hard_ship_gate_created": False,
                "model_score_is_authority": False,
                "operator_read_required_for_release": True,
                "production_public_release_authorized": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    readme_path.write_text(
        "# Human Judge Packet\n\n"
        "Score each sample 1-5 on every rubric dimension. This packet is advisory only. "
        "It does not authorize public release, storefront use, or bestseller-readiness claims.\n",
        encoding="utf-8",
    )
    return {
        "manifest": manifest_path,
        "rubric": rubric_path,
        "contract": contract_path,
        "readme": readme_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build advisory human judge packet")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--max-samples", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    packet = build_packet(args.repo_root, max_samples=args.max_samples)
    paths = write_packet(packet, args.output_dir)
    print(f"Human judge sample manifest written: {paths['manifest']}")
    print(f"Chapters selected: {packet['stats']['chapters_selected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

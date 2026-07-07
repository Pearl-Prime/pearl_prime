#!/usr/bin/env python3
"""Before/after proof for EI v2 within-book semantic-dedup calibration."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

REPO = Path(__file__).resolve().parents[2]

PROOF_CELLS = [
    {
        "label": "burnout_overwhelm__corporate_managers",
        "path": REPO / "artifacts/wave_proof/draft/burnout_overwhelm__corporate_managers/book.txt",
    },
    {
        "label": "burnout_watcher__corporate_managers",
        "path": REPO / "artifacts/wave_proof/draft/burnout_watcher__corporate_managers/book.txt",
    },
    {
        "label": "burnout_grief__corporate_managers",
        "path": REPO / "artifacts/wave_proof/draft/burnout_grief__corporate_managers/book.txt",
    },
]


def _legacy_uniqueness(chapter_text: str, chapter_index: int, chapters: list[str]) -> float:
    from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates

    others = [t for i, t in enumerate(chapters) if i != chapter_index and t.strip()]
    if not others:
        return 1.0
    dupes = detect_semantic_duplicates(
        [chapter_text] + others[:5],
        [f"ch{chapter_index}"] + [f"other{i}" for i in range(len(others[:5]))],
    )
    max_sim = max((d["similarity"] for d in dupes), default=0.0)
    return max(0.0, 1.0 - max_sim * 2)


def _score_book(path: Path, scorer) -> dict:
    from phoenix_v4.quality.content_uniqueness_truth import split_shipped_book_chapters

    chapters = split_shipped_book_chapters(path.read_text(encoding="utf-8"))
    per_ch = [scorer(chapters[i], i, chapters) for i in range(len(chapters))]
    return {
        "chapter_count": len(chapters),
        "content_uniqueness_avg": round(mean(per_ch), 4),
        "content_uniqueness_min": round(min(per_ch), 4),
        "content_uniqueness_max": round(max(per_ch), 4),
        "per_chapter": [round(x, 4) for x in per_ch],
    }


def build_proof() -> dict:
    import sys

    sys.path.insert(0, str(REPO))
    from phoenix_v4.quality.ei_v2.semantic_dedup import analyze_chapter_content_uniqueness
    from scripts.ci.run_ei_v2_rigorous_eval import evaluate_chapter

    cells = []
    for cell in PROOF_CELLS:
        if not cell["path"].exists():
            raise FileNotFoundError(cell["path"])
        chapters = cell["path"].read_text(encoding="utf-8")
        from phoenix_v4.quality.content_uniqueness_truth import split_shipped_book_chapters

        chs = split_shipped_book_chapters(chapters)
        before = _score_book(cell["path"], _legacy_uniqueness)
        after_ev = [
            evaluate_chapter(chs[i], i, {}, "corporate_managers", "burnout", chs)
            for i in range(len(chs))
        ]
        after_scores = [ev.content_uniqueness for ev in after_ev]
        ch0_before = analyze_chapter_content_uniqueness(chs[0], 0, chs, cfg={})
        # legacy evidence via old formula on ch0
        others = [t for i, t in enumerate(chs) if i != 0 and t.strip()]
        from phoenix_v4.quality.ei_v2.semantic_dedup import detect_semantic_duplicates

        legacy_dupes = detect_semantic_duplicates(
            [chs[0]] + others[:5],
            ["ch0"] + [f"other{i}" for i in range(len(others[:5]))],
        )
        cells.append(
            {
                "label": cell["label"],
                "before": before,
                "after": {
                    "content_uniqueness_avg": round(mean(after_scores), 4),
                    "content_uniqueness_min": round(min(after_scores), 4),
                    "content_uniqueness_max": round(max(after_scores), 4),
                    "per_chapter": [round(x, 4) for x in after_scores],
                },
                "chapter0_pair_evidence_before": {
                    "formula": "1 - max_composite*2 (others[:5], beat+structure weighted)",
                    "top_pairs": legacy_dupes[:3],
                },
                "chapter0_pair_evidence_after": {
                    "scoring_mode": ch0_before["scoring_mode"],
                    "worst_pair": ch0_before["worst_pair"],
                    "max_ngram_overlap": ch0_before["max_ngram_overlap"],
                    "max_prose_similarity": ch0_before["max_prose_similarity"],
                },
            }
        )

    duplicate_control = "IDENTICAL_CHAPTER" * 200
    control_chapters = [duplicate_control, duplicate_control, "Different prose entirely. " * 50]
    control_ev = evaluate_chapter(control_chapters[0], 0, {}, "p", "burnout", control_chapters)

    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "lane": "semantic-dedup within-book prose-first",
        "root_cause": (
            "Legacy chapter eval used atom-pool composite (35% ngram + 25% structure + "
            "25% beat) with max_sim*2 penalty over others[:5]. Shipped books share "
            "therapeutic beat markers and paragraph rhythm; word n-gram overlap stays "
            "~0.01 (trigram uniqueness=1.0). Beat similarity=1.0 inflated composite to "
            "~0.42 → content_uniqueness≈0.16 uniformly."
        ),
        "fix": "within_book_chapter prose-first scorer in semantic_dedup.py; compare all chapters; penalize prose n-gram/char overlap only",
        "proof_cells": cells,
        "duplicate_control": {
            "content_uniqueness_ch0": control_ev.content_uniqueness,
            "still_flagged": control_ev.content_uniqueness < 0.2,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=REPO / "artifacts/qa/semantic_dedup_20260708")
    args = ap.parse_args()
    proof = build_proof()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "PROOF.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
    (args.out_dir / "CLOSEOUT.md").write_text(_closeout(proof), encoding="utf-8")
    print(
        "before_avg",
        proof["proof_cells"][0]["before"]["content_uniqueness_avg"],
        "after_avg",
        proof["proof_cells"][0]["after"]["content_uniqueness_avg"],
    )
    return 0


def _closeout(proof: dict) -> str:
    lines = [
        "# Semantic-dedup closeout (2026-07-08)",
        "",
        "**Lane:** shipped-book EI v2 `content_uniqueness` calibration",
        "",
        "## Root cause",
        "",
        proof["root_cause"],
        "",
        "## Burnout proof cells",
        "",
        "| Cell | before avg | after avg |",
        "|------|----------:|----------:|",
    ]
    for c in proof["proof_cells"]:
        lines.append(
            f"| {c['label']} | {c['before']['content_uniqueness_avg']} | {c['after']['content_uniqueness_avg']} |"
        )
    lines.extend(
        [
            "",
            f"Duplicate control still flagged: {proof['duplicate_control']['still_flagged']} "
            f"(score={proof['duplicate_control']['content_uniqueness_ch0']})",
            "",
            "## Non-claims",
            "",
            "- No writer/prose edits",
            "- No registry-scoring changes",
            "- Atom-pool dedup weights unchanged",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build proof roots for the manga A/B/C prerequisite wave."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.bubble_render_v2 import render_bubbles_onto_panel_v2
from phoenix_v4.manga.chapter.page_frame import render_framed_page
from phoenix_v4.manga.chapter.reading_graph import analyze_page_reading_graph
from phoenix_v4.manga.chapter.spread_layout_solver import solve_page_layout

DATE_TAG = "2026-07-12"
QA_ROOT = REPO / "artifacts" / "qa"

A_ROOT = QA_ROOT / f"manga_passb_reading_graph_{DATE_TAG}"
B_ROOT = QA_ROOT / f"manga_spread_layout_solver_{DATE_TAG}"
C_ROOT = QA_ROOT / f"manga_jlreq_sfx_lettering_{DATE_TAG}"


def _reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _repo_rel(value: str | Path) -> str:
    text = str(value)
    candidate = Path(text)
    if candidate.is_absolute():
        try:
            return candidate.relative_to(REPO).as_posix()
        except ValueError:
            return text
    return text


def _relativize_paths(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {str(k): _relativize_paths(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [_relativize_paths(v) for v in payload]
    if isinstance(payload, Path):
        return _repo_rel(payload)
    if isinstance(payload, str) and payload.startswith("/"):
        return _repo_rel(payload)
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_relativize_paths(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _build_spread_proof() -> dict:
    _reset_dir(B_ROOT)
    support = B_ROOT / "support"
    support.mkdir(parents=True, exist_ok=True)

    panel_specs = [
        ("p01", (235, 90, 90), {"panel_function": "climactic_spread", "aspect_hint": "wide_16_9"}),
        ("p02", (85, 125, 225), {"panel_function": "reaction", "aspect_hint": "portrait_4_5"}),
        ("p03", (95, 185, 125), {"panel_function": "reaction", "aspect_hint": "portrait_4_5"}),
        ("p04", (245, 205, 95), {"panel_function": "detail", "aspect_hint": "square_1_1"}),
    ]
    images: list[Image.Image] = []
    page_panels: list[dict[str, str]] = []
    for pid, rgb, meta in panel_specs:
        path = support / f"{pid}.png"
        Image.new("RGB", (960, 1400), color=rgb).save(path)
        images.append(Image.open(path).convert("RGBA"))
        page_panels.append({"panel_id": pid, **meta})

    decision = solve_page_layout(
        {
            "page_type": "double_spread",
            "reading_direction": "rtl",
            "panels": page_panels,
        },
        genre="shonen",
    )
    page = render_framed_page(
        images,
        page_type="double_spread",
        genre="shonen",
        reading_direction="rtl",
        layout_decision=decision,
        panel_metadata=page_panels,
    )
    page_path = B_ROOT / "spread_page.png"
    page.save(page_path, format="PNG")
    for image in images:
        image.close()
    page.close()

    if not bool(decision.get("validation", {}).get("valid")):
        failures = decision.get("validation", {}).get("failures") or []
        raise RuntimeError(
            f"spread proof invalid; refusing to emit EXECUTED-REAL summary (failures={failures})"
        )

    summary = {
        "artifact": "manga-spread-layout-solver",
        "status": "EXECUTED-REAL",
        "decision_path": (B_ROOT / "spread_layout_decision.json").relative_to(REPO).as_posix(),
        "render_path": page_path.relative_to(REPO).as_posix(),
        "resolved_page_type": decision["resolved_page_type"],
        "spread": decision["spread"],
        "validation": decision["validation"],
    }
    _write_json(B_ROOT / "spread_layout_decision.json", decision)
    _write_json(B_ROOT / "PROOF_SUMMARY.json", summary)
    _write_text(
        B_ROOT / "PROOF.md",
        "\n".join(
            [
                "# Spread Layout Solver Proof",
                "",
                f"- Status: {summary['status']}",
                f"- Resolved page type: `{decision['resolved_page_type']}`",
                f"- Spread cells: `{decision['cells']}`",
                f"- Render: `{page_path.relative_to(REPO)}`",
            ]
        ),
    )
    return decision


def _build_reading_graph_proof(layout_decision: dict) -> None:
    _reset_dir(A_ROOT)
    bubble_layouts_by_panel = {
        "p01": {
            "panel_size": (960, 1400),
            "bubbles": [
                {"type": "dialogue", "text": "最初", "bbox": [640, 120, 900, 420]},
                {"type": "dialogue", "text": "次", "bbox": [150, 560, 420, 860]},
            ],
        },
        "p02": {
            "panel_size": (960, 1400),
            "bubbles": [
                {"type": "dialogue", "text": "右ページ下", "bbox": [580, 200, 860, 520]},
            ],
        },
        "p03": {
            "panel_size": (960, 1400),
            "bubbles": [
                {"type": "dialogue", "text": "左ページ上", "bbox": [520, 180, 860, 520]},
            ],
        },
    }
    graph = analyze_page_reading_graph(
        page_number=1,
        panel_assignments=layout_decision["panel_assignments"],
        bubble_layouts_by_panel=bubble_layouts_by_panel,
        reading_direction="rtl",
    )
    if not bool(graph.get("validation", {}).get("ok")):
        issues = graph.get("validation", {}).get("issues") or []
        raise RuntimeError(
            f"reading-graph proof invalid; refusing to emit EXECUTED-REAL summary (issues={issues})"
        )
    summary = {
        "artifact": "manga-passb-reading-graph",
        "status": "EXECUTED-REAL",
        "graph_path": (A_ROOT / "reading_graph.json").relative_to(REPO).as_posix(),
        "ok": graph["validation"]["ok"],
        "metrics": graph["validation"]["metrics"],
    }
    _write_json(A_ROOT / "reading_graph.json", graph)
    _write_json(A_ROOT / "PROOF_SUMMARY.json", summary)
    _write_text(
        A_ROOT / "PROOF.md",
        "\n".join(
            [
                "# Pass-B Reading Graph Proof",
                "",
                f"- Status: {summary['status']}",
                f"- Validation ok: `{graph['validation']['ok']}`",
                f"- Nodes: `{len(graph['nodes'])}`",
                f"- Edges: `{len(graph['edges'])}`",
            ]
        ),
    )


def _build_jlreq_proof() -> None:
    _reset_dir(C_ROOT)
    panel_path = C_ROOT / "support_panel.png"
    Image.new("RGB", (720, 960), color=(248, 246, 238)).save(panel_path)
    bubbled_path = C_ROOT / "jlreq_bubbled.png"
    manifest_path = C_ROOT / "jlreq_lettering_manifest.json"

    layout = render_bubbles_onto_panel_v2(
        panel_path,
        [
            {
                "speaker": "A",
                "text_by_locale": {"ja_JP": "静かな夜だ"},
                "vertical_kanji": True,
                "bubble_style": "round_normal",
            },
            {
                "speaker": "B",
                "text_by_locale": {"ja_JP": "東京"},
                "vertical_kanji": True,
                "furigana": [{"base": "東京", "reading": "とうきょう"}],
                "bubble_style": "shojo_soft",
            },
        ],
        sfx=["ドン"],
        narrator_caption="間",
        out_path=bubbled_path,
        manifest_out_path=manifest_path,
        locale="ja_JP",
    )
    summary = {
        "artifact": "manga-jlreq-sfx-lettering",
        "status": "EXECUTED-REAL",
        "layout_path": (C_ROOT / "jlreq_layout.json").relative_to(REPO).as_posix(),
        "image_path": bubbled_path.relative_to(REPO).as_posix(),
        "manifest_path": manifest_path.relative_to(REPO).as_posix(),
        "dialogue_runtime_statuses": [
            row.get("jlreq_plan", {}).get("runtime_status")
            for row in layout["bubbles"]
            if row.get("type") == "dialogue"
        ],
        "sfx_writing_modes": [
            row.get("placement_plan", {}).get("writing_mode")
            for row in layout["bubbles"]
            if row.get("type") == "sfx"
        ],
    }
    _write_json(C_ROOT / "jlreq_layout.json", layout)
    _write_json(C_ROOT / "PROOF_SUMMARY.json", summary)
    _write_text(
        C_ROOT / "PROOF.md",
        "\n".join(
            [
                "# JLREQ + SFX Lettering Proof",
                "",
                f"- Status: {summary['status']}",
                f"- Dialogue runtime statuses: `{summary['dialogue_runtime_statuses']}`",
                f"- SFX writing modes: `{summary['sfx_writing_modes']}`",
                f"- Image: `{bubbled_path.relative_to(REPO)}`",
            ]
        ),
    )


def main() -> int:
    QA_ROOT.mkdir(parents=True, exist_ok=True)
    decision = _build_spread_proof()
    _build_reading_graph_proof(decision)
    _build_jlreq_proof()
    print(str(A_ROOT))
    print(str(B_ROOT))
    print(str(C_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

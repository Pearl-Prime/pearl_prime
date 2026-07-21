"""Tests for the pass-B manga reading graph validator."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.reading_graph import analyze_page_reading_graph  # type: ignore


def test_reading_graph_accepts_rtl_panel_and_bubble_flow():
    graph = analyze_page_reading_graph(
        page_number=1,
        reading_direction="rtl",
        panel_assignments=[
            {"panel_id": "p1", "bbox_norm": [0.5, 0.0, 0.5, 1.0]},
            {"panel_id": "p2", "bbox_norm": [0.0, 0.0, 0.5, 1.0]},
        ],
        bubble_layouts_by_panel={
            "p1": {
                "panel_size": (100, 100),
                "bubbles": [
                    {"type": "dialogue", "text": "A", "bbox": [60, 10, 95, 40]},
                    {"type": "dialogue", "text": "B", "bbox": [10, 45, 45, 80]},
                ],
            },
            "p2": {
                "panel_size": (100, 100),
                "bubbles": [
                    {"type": "dialogue", "text": "C", "bbox": [55, 12, 90, 42]},
                ],
            },
        },
    )
    assert graph["validation"]["ok"] is True
    assert graph["validation"]["metrics"]["bubble_count"] == 3


def test_reading_graph_flags_panel_order_backtrack():
    graph = analyze_page_reading_graph(
        page_number=2,
        reading_direction="rtl",
        panel_assignments=[
            {"panel_id": "p1", "bbox_norm": [0.0, 0.0, 0.5, 1.0]},
            {"panel_id": "p2", "bbox_norm": [0.5, 0.0, 0.5, 1.0]},
        ],
        bubble_layouts_by_panel={},
    )
    assert graph["validation"]["ok"] is False
    assert graph["validation"]["issues"][0]["rule_id"] == "panel_order_mismatch"


def test_reading_graph_flags_bubble_order_backtrack():
    graph = analyze_page_reading_graph(
        page_number=3,
        reading_direction="rtl",
        panel_assignments=[
            {"panel_id": "p1", "bbox_norm": [0.5, 0.0, 0.5, 1.0]},
        ],
        bubble_layouts_by_panel={
            "p1": {
                "panel_size": (100, 100),
                "bubbles": [
                    {"type": "dialogue", "text": "late", "bbox": [10, 60, 40, 90]},
                    {"type": "dialogue", "text": "early", "bbox": [60, 10, 90, 35]},
                ],
            }
        },
    )
    assert graph["validation"]["ok"] is False
    assert graph["validation"]["issues"][0]["rule_id"] == "bubble_order_mismatch"


def test_reading_graph_scales_bubbles_into_small_normalized_panel_cells():
    graph = analyze_page_reading_graph(
        page_number=4,
        reading_direction="rtl",
        panel_assignments=[
            {"panel_id": "p1", "bbox_norm": [0.5, 0.0, 0.25, 0.25]},
        ],
        bubble_layouts_by_panel={
            "p1": {
                "panel_size": (100, 100),
                "bubbles": [
                    {"type": "dialogue", "text": "tiny", "bbox": [50, 10, 90, 40]},
                ],
            }
        },
    )
    bubble = next(row for row in graph["nodes"] if row["id"].startswith("bubble:"))
    x0, y0, x1, y1 = bubble["bbox"]
    assert 0.5 <= x0 < 0.75
    assert 0.0 <= y0 < 0.25
    assert x1 <= 0.75 + 1e-6
    assert y1 <= 0.25 + 1e-6

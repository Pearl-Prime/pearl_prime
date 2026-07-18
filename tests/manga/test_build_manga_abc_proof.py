from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.manga import build_manga_abc_proof as mod  # type: ignore


def test_relativize_paths_rewrites_repo_absolute_paths():
    payload = {
        "a": str(mod.REPO / "artifacts" / "qa" / "x.json"),
        "nested": [
            {"b": str(mod.REPO / "foo" / "bar.png")},
            "/outside/repo/example",
        ],
    }
    rel = mod._relativize_paths(payload)
    assert rel["a"] == "artifacts/qa/x.json"
    assert rel["nested"][0]["b"] == "foo/bar.png"
    assert rel["nested"][1] == "/outside/repo/example"


def test_build_spread_proof_fails_closed_on_invalid_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(mod, "B_ROOT", tmp_path / "spread")

    def _bad_decision(*args, **kwargs):
        return {
            "resolved_page_type": "double_spread",
            "spread": True,
            "cells": [[0.0, 0.0, 1.0, 1.0]],
            "panel_assignments": [],
            "genre_profile": {},
            "page_type_rule": {},
            "validation": {"valid": False, "failures": ["spine_safety"]},
        }

    monkeypatch.setattr(mod, "solve_page_layout", _bad_decision)
    with pytest.raises(RuntimeError, match="refusing to emit EXECUTED-REAL"):
        mod._build_spread_proof()


def test_build_reading_graph_proof_fails_closed_on_invalid_graph(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(mod, "A_ROOT", tmp_path / "reading")

    def _bad_graph(*args, **kwargs):
        return {
            "nodes": [],
            "edges": [],
            "validation": {
                "ok": False,
                "issues": [{"rule_id": "panel_order_mismatch"}],
                "metrics": {},
            },
        }

    monkeypatch.setattr(mod, "analyze_page_reading_graph", _bad_graph)
    with pytest.raises(RuntimeError, match="refusing to emit EXECUTED-REAL"):
        mod._build_reading_graph_proof({"panel_assignments": []})


def test_write_json_sanitizes_absolute_repo_paths(tmp_path: Path):
    out = tmp_path / "proof.json"
    payload = {
        "graph_path": str(mod.REPO / "artifacts" / "qa" / "graph.json"),
        "deep": {"image_path": str(mod.REPO / "artifacts" / "qa" / "img.png")},
    }
    mod._write_json(out, payload)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["graph_path"] == "artifacts/qa/graph.json"
    assert data["deep"]["image_path"] == "artifacts/qa/img.png"

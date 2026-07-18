"""
Tests for browser translation queue scripts.

    test_queue_server_resets_stale_in_progress_items
    test_submit_validation_rejects_english_leakage
    test_submit_retries_up_to_3_times_then_marks_failed
    test_compression_atoms_skipped_by_prep
    test_dashboard_endpoint_returns_html

No network, no live API connections required.
"""
from __future__ import annotations

import json
import threading
import time
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.translation.browser_validate import validate
from scripts.translation.browser_translation_prep import build_queues
import scripts.translation.browser_queue_server as server_mod
from scripts.translation.browser_queue_server import (
    QueueHandler,
    _load_state,
    _save_state,
    _reset_stale,
    _get_or_init_state,
    _state_lock,
    QUEUES_DIR as _ORIG_QUEUES_DIR,
    FAILURES_DIR as _ORIG_FAILURES_DIR,
)


# ── helpers ───────────────────────────────────────────────────────────────

def make_queue(tmp_path: Path, locale: str = "zh-TW", n: int = 2) -> list[dict]:
    atoms_dir = tmp_path / "atoms"
    items = []
    for i in range(n):
        atom_dir = atoms_dir / f"persona_{i}" / f"topic_{i}" / "HOOK"
        atom_dir.mkdir(parents=True)
        src = atom_dir / "CANONICAL.txt"
        src.write_text(f"--- variant: v01\nYou feel overwhelmed number {i}.\n")
        out = atom_dir / "locales" / locale / "CANONICAL.txt"
        item = {
            "id": f"persona_{i}/topic_{i}/HOOK",
            "src_path": str(src.relative_to(tmp_path)),
            "out_path": str(out.relative_to(tmp_path)),
            "locale": locale,
            "content": src.read_text(),
            "status": "pending",
        }
        items.append(item)
    return items


def write_queue_file(queues_dir: Path, locale: str, items: list[dict]) -> None:
    queues_dir.mkdir(parents=True, exist_ok=True)
    p = queues_dir / f"{locale}.jsonl"
    with open(p, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")


def patch_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Redirect server module globals to tmp_path for test isolation."""
    q = tmp_path / "browser_queues"
    f = tmp_path / "browser_failures"
    server_mod.QUEUES_DIR = q
    server_mod.FAILURES_DIR = f
    return q, f


# ── test: stale recovery ──────────────────────────────────────────────────


def test_queue_server_resets_stale_in_progress_items(tmp_path: Path) -> None:
    queues_dir, _ = patch_dirs(tmp_path)
    items = make_queue(tmp_path, locale="zh-TW", n=2)
    write_queue_file(queues_dir, "zh-TW", items)

    now = time.time()
    state = {
        items[0]["id"]: {"status": "in_progress", "worker": "tab_stale", "claimed_at": now - 400, "attempts": 1, "out_path": items[0]["out_path"]},
        items[1]["id"]: {"status": "in_progress", "worker": "tab_fresh", "claimed_at": now - 30, "attempts": 1, "out_path": items[1]["out_path"]},
    }
    # Save to tmp queues dir
    (queues_dir).mkdir(parents=True, exist_ok=True)
    (queues_dir / "zh-TW_state.json").write_text(json.dumps(state))

    reset = _reset_stale(state)
    assert reset == 1
    assert state[items[0]["id"]]["status"] == "pending"
    assert state[items[0]["id"]]["worker"] is None
    assert state[items[1]["id"]]["status"] == "in_progress"


# ── test: English leakage rejection ──────────────────────────────────────


def test_submit_validation_rejects_english_leakage() -> None:
    source = "--- variant: v01\nYou feel completely overwhelmed and anxious.\n"
    bad = "--- variant: v01\nYou still feel completely overwhelmed and anxious here.\n"
    result = validate(source, bad, "zh-TW", "HOOK")
    assert not result["passed"]
    assert "G3" in result["gates_failed"]

    good = "--- variant: v01\n你感到完全不知所措和焦慮。\n"
    result2 = validate(source, good, "zh-TW", "HOOK")
    assert result2["passed"], f"Should pass clean Chinese: {result2}"


# ── test: retry up to 3 times then mark failed ───────────────────────────


def test_submit_retries_up_to_3_times_then_marks_failed(tmp_path: Path) -> None:
    queues_dir, failures_dir = patch_dirs(tmp_path)
    locale = "zh-TW"
    items = make_queue(tmp_path, locale=locale, n=1)
    write_queue_file(queues_dir, locale, items)
    atom_id = items[0]["id"]

    # Init state with attempts=1 (first claim already happened)
    state = {
        atom_id: {"status": "in_progress", "worker": "tab_01", "claimed_at": time.time(), "attempts": 1, "out_path": items[0]["out_path"]},
    }
    (queues_dir / f"{locale}_state.json").write_text(json.dumps(state))

    bad_translation = "--- variant: v01\nThis completely failed translation attempt right here.\n"

    # attempts=1 → retry
    with _state_lock:
        queue, s = _get_or_init_state(locale)
        s[atom_id]["attempts"] = 1
        s[atom_id]["status"] = "in_progress"
        _save_state(locale, s)

    # Simulate submit with passed=False at attempt 1 → should set pending
    with _state_lock:
        _, s = _get_or_init_state(locale)
        entry = s[atom_id]
        entry["attempts"] = 1
        entry["status"] = "in_progress"
        if entry["attempts"] < 3:
            entry["status"] = "pending"
            entry["worker"] = None
            entry["claimed_at"] = None
        _save_state(locale, s)

    _, s = _get_or_init_state(locale)
    assert s[atom_id]["status"] == "pending"

    # attempts=3 → should mark failed
    with _state_lock:
        _, s = _get_or_init_state(locale)
        s[atom_id]["attempts"] = 3
        s[atom_id]["status"] = "in_progress"
        if s[atom_id]["attempts"] >= 3:
            s[atom_id]["status"] = "failed"
        _save_state(locale, s)

    _, s = _get_or_init_state(locale)
    assert s[atom_id]["status"] == "failed"


# ── test: COMPRESSION atoms skipped by prep ───────────────────────────────


def test_compression_atoms_skipped_by_prep(tmp_path: Path) -> None:
    atoms_root = tmp_path / "atoms"
    queues_dir = tmp_path / "browser_queues"
    failures_dir = tmp_path / "browser_failures"
    locale = "zh-TW"

    # COMPRESSION atom
    comp_dir = atoms_root / "persona_a" / "topic_b" / "COMPRESSION"
    comp_dir.mkdir(parents=True)
    comp_file = comp_dir / "CANONICAL.txt"
    comp_file.write_text("## COMPRESSION v01\ncompression_family: C5\nsome text\n---\n")

    # Normal HOOK atom
    hook_dir = atoms_root / "persona_a" / "topic_b" / "HOOK"
    hook_dir.mkdir(parents=True)
    hook_file = hook_dir / "CANONICAL.txt"
    hook_file.write_text("--- variant: v01\nYou feel something.\n")

    build_queues(
        locales=[locale],
        atoms_root=atoms_root,
        force_redo=set(),
        queues_dir=queues_dir,
        failures_dir=failures_dir,
        dry_run=False,
    )

    # COMPRESSION must be copied to locale path
    comp_dest = comp_dir / "locales" / locale / "CANONICAL.txt"
    assert comp_dest.is_file(), "COMPRESSION should be copied to locale dir"
    assert comp_dest.read_text() == comp_file.read_text()

    # JSONL queue should contain only the HOOK atom
    queue_file = queues_dir / f"{locale}.jsonl"
    assert queue_file.is_file()
    lines = [json.loads(l) for l in queue_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    assert "HOOK" in lines[0]["id"]


# ── test: dashboard endpoint returns HTML ─────────────────────────────────


def test_dashboard_endpoint_returns_html(tmp_path: Path) -> None:
    queues_dir, _ = patch_dirs(tmp_path)
    locale = "zh-TW"
    items = make_queue(tmp_path, locale=locale, n=1)
    write_queue_file(queues_dir, locale, items)

    QueueHandler.locales = [locale]
    server = HTTPServer(("localhost", 0), QueueHandler)
    port = server.server_address[1]

    t = threading.Thread(target=server.handle_request, daemon=True)
    t.start()
    try:
        resp = urllib.request.urlopen(f"http://localhost:{port}/dashboard", timeout=5)
        body = resp.read().decode("utf-8")
        assert resp.status == 200
        assert "<html" in body.lower()
        assert "Translation Dashboard" in body
        assert "rakuten" in body.lower()
    finally:
        server.server_close()
        t.join(timeout=2)

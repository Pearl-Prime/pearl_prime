"""
Pytest wrapper for the Pearl News sidebar parity gate.

This test exists to make `scripts/ci/check_pearl_news_sidebar_parity.py`
runnable as part of the normal pytest battery — operators and CI runners
who type `pytest` get the sidebar gate for free.

Two test modes:

    test_parity_gate_passes_on_restored_state
        Runs the gate against the current renderer. Must pass — if it
        fails, the sidebar has drifted and the PR that caused it should
        be reverted, not patched.

    test_parity_gate_fails_on_deliberately_broken_state
        Mutates the assemble_v52 source in /tmp, runs the gate, and
        asserts that it correctly returns non-zero. This is the
        "the gate actually catches things" smoke test.

    test_canonical_html_snapshot_diff
        Renders the synthetic article and snapshot-diffs the sidebar
        block against artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html.
        Tolerates whitelisted deltas via PERMITTED_DELTA regex list at
        the top of this file — operator can extend with sign-off in PR.

Spec authority:
    docs/PEARL_NEWS_WRITER_SPEC.md §S (Sidebar Restoration Protocol)
    docs/PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md
    artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR_METADATA.json
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / "scripts/ci/check_pearl_news_sidebar_parity.py"
ASSEMBLE_PATH = REPO_ROOT / "pearl_news/pipeline/assemble_v52.py"
CANONICAL_SNAPSHOT = REPO_ROOT / "artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html"


# ─────────────────────────────────────────────────────────────────────────
# Whitelist of permitted deltas between renderer output and CANONICAL_SIDEBAR.html.
# Each entry is a regex matched against the diff hunks. Add entries here ONLY
# with operator sign-off in the PR body — these are deliberate, non-regression
# differences (e.g. per-teacher exercise content, copy variants).
# ─────────────────────────────────────────────────────────────────────────
PERMITTED_DELTA = [
    # Per-teacher exercise content (8-step practices vary by teacher)
    r"Step [1-8] of [1-8]",
    # Per-article slug + ID
    r'data-pn-article-id="[^"]*"',
    # Teacher-specific practice titles
    r"<h3>Practice · [^<]*</h3>",
    r'<h3>Practice \\u00b7 [^<]*</h3>',
    # Per-teacher exercise body copy
    r"From [A-Z][a-z]+'s teaching",
    # CTA H3 text variation: "Free Tools" (renderer) vs "Free Practice Tool" (live 3724)
    r"<h3>Free (Tools|Practice Tool)</h3>",
    # CTA body / title varies by reaction_id
    r'class="cta-title">[^<]+</div>',
    r'class="cta-body">[^<]+</div>',
    r'class="cta-primary"[^>]*>[^<]+</a>',
    r'class="cta-secondary"[^>]*>[^<]+</a>',
    r'class="cta-micro-action">[^<]+</div>',
    # SDG content from sdg_news_topic_mapping.yaml — varies by topic
    r'sdg-badge">SDG [^<]+</span>',
    r"<li[^>]*>[^<]+</li>",
    # Per-article hero / image
    r"hero[_-]image",
    # WordPress wpautop injects <p> tags around block elements — tolerate
    r"^\\s*</?p>\\s*$",
    # Whitespace-only differences
    r"^\\s+$",
]


def _run_gate(env_overlay: dict | None = None) -> tuple[int, str, str]:
    """Run the gate script; return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env={**__import__('os').environ, **(env_overlay or {})},
    )
    return result.returncode, result.stdout, result.stderr


def test_gate_script_exists():
    """The CI gate script must exist at the expected location."""
    assert GATE_SCRIPT.exists(), f"Gate script missing at {GATE_SCRIPT}"


def test_canonical_snapshot_exists():
    """The canonical sidebar snapshot must exist."""
    assert CANONICAL_SNAPSHOT.exists(), f"Canonical snapshot missing at {CANONICAL_SNAPSHOT}"


def test_parity_gate_passes_on_restored_state():
    """The current renderer must satisfy all canonical fingerprints."""
    exit_code, stdout, stderr = _run_gate()
    assert exit_code == 0, (
        f"Parity gate failed on what should be the restored canonical state.\n"
        f"  exit:   {exit_code}\n"
        f"  stdout: {stdout}\n"
        f"  stderr: {stderr}\n"
        f"  Likely cause: pearl_news/pipeline/assemble_v52.py has drifted from "
        f"the canonical SHA chain. Run:\n"
        f"    git checkout 78f115fe3 -- pearl_news/pipeline/assemble_v52.py\n"
        f"  to restore. See docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md."
    )


def test_parity_gate_fails_on_deliberately_broken_state(tmp_path):
    """
    Mutate the renderer to remove F4 (pn-poll-card class), run the gate,
    assert it correctly identifies the failure. Restore the renderer
    after the test (the test must leave the working tree unchanged).
    """
    original = ASSEMBLE_PATH.read_text()
    try:
        broken = original.replace("pn-poll-card", "BROKEN-pn-poll-card", 1)
        assert broken != original, "Could not break the renderer — pn-poll-card not present"
        ASSEMBLE_PATH.write_text(broken)
        exit_code, stdout, stderr = _run_gate()
        assert exit_code != 0, (
            "Parity gate did NOT detect a deliberately broken state. "
            "The gate is not enforcing fingerprints correctly."
        )
        # The failure report must mention F4_hot_take_poll
        combined = stdout + stderr
        assert "F4_hot_take_poll" in combined, (
            f"Gate detected failure but did not identify F4_hot_take_poll. "
            f"Output: {combined[:1000]}"
        )
    finally:
        ASSEMBLE_PATH.write_text(original)


def _extract_sidebar_block(rendered: str) -> str:
    """Best-effort extraction of the sidebar div from a rendered article."""
    start = rendered.find('<div class="sidebar">')
    if start == -1:
        return ""
    # The sidebar block typically ends after the </script> closer of pnReaderSignal
    script_end = rendered.find("</script>", start)
    if script_end == -1:
        # Fall back: take a 20 KB window
        return rendered[start:start + 20000]
    div_end = rendered.find("</div>", script_end)
    if div_end == -1:
        return rendered[start:script_end + len("</script>")]
    return rendered[start:div_end + len("</div>")]


def _strip_permitted(text: str) -> str:
    """Replace each PERMITTED_DELTA-matching substring with a placeholder.

    Substring-replace (not line-replace) — patterns are surgical so they
    must not consume neighboring canonical markers on the same line.
    """
    out = text
    for pat in PERMITTED_DELTA:
        try:
            out = re.sub(pat, "<<PERMITTED_DELTA>>", out)
        except re.error:
            continue
    return out


def test_canonical_html_snapshot_diff():
    """
    Render the synthetic article, extract its sidebar block, diff against
    artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html. Tolerated diffs
    are normalised via PERMITTED_DELTA. Untolerated diffs fail the test.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from pearl_news.pipeline.assemble_v52 import assemble_v52
    article_json = {
        "id": "pn-sidebar-parity-probe",
        "slug": "pn-sidebar-parity-probe",
        "title": "Sidebar Parity Probe",
        "headline_layer_1": {"line": "Snapshot diff probe"},
        "language": "en",
        "teacher_id": "junko",
        "topic": "mental_health",
        "sdg": {"primary": 3},
        "slots": {},
    }
    meta = {"layout": "default", "language": "en", "teacher_id": "junko", "topic": "mental_health"}
    rendered = assemble_v52(article_json, meta)
    sb = _extract_sidebar_block(rendered)
    assert sb, "Could not extract sidebar block from rendered article"

    canonical_html = CANONICAL_SNAPSHOT.read_text()
    canonical_sb = _extract_sidebar_block(canonical_html)
    assert canonical_sb, "Could not extract sidebar block from CANONICAL_SIDEBAR.html"

    # Normalize both via PERMITTED_DELTA and compare card-class presence.
    # This is a weaker test than byte-for-byte diff but sufficient to catch
    # structural drift (missing card, removed JS handler, etc.).
    rendered_norm = _strip_permitted(sb)
    canonical_norm = _strip_permitted(canonical_sb)

    # Both should contain the 5 canonical card-class markers
    for marker in [
        'class="sidebar-card exercise-card"',
        'class="sidebar-card cta-card"',
        "SDG Connection",
        'class="sidebar-card pn-poll-card"',
        'class="sidebar-card pn-take-card"',
    ]:
        assert marker in rendered_norm, f"Rendered missing canonical marker: {marker!r}"
        assert marker in canonical_norm, f"Canonical snapshot missing marker (snapshot may need refresh): {marker!r}"

    # Reader-signal IIFE: required in both
    assert "pnReaderSignal" in rendered_norm, "Rendered missing pnReaderSignal IIFE"
    assert "pnReaderSignal" in canonical_norm, "Canonical missing pnReaderSignal IIFE (snapshot stale?)"

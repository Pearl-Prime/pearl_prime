"""Tests for the zh-TW Simplified contamination delta gate.

The two load-bearing properties:
  1. It FAILS on newly-introduced Simplified in a changed zh-TW file.
  2. It PASSES on the existing 869-file baseline (so main stays green and the
     gate does not block unrelated PRs).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))

from check_zh_tw_simplified_contamination import (  # noqa: E402
    BASELINE_PATH,
    distinct_simplified,
    evaluate,
    is_zh_tw_atom,
    load_baseline,
)
from zh_tw_simplified_charset import (  # noqa: E402
    BIG5_ENCODABLE_VARIANT_CHARS,
    SIMPLIFIED_ONLY_CHARS,
    severity_for,
)

ZH = "atoms/demo_persona/burnout/STORY/locales/zh-TW/CANONICAL.txt"

TRADITIONAL = "她寫下今天的感受，然後把筆記本闔上。窗外的光線很柔和。"
SIMPLIFIED = "她写下今天的感受，然后把笔记本合上。这个窗外的光线很柔和。"


# --------------------------------------------------------------------------
# Detector calibration — the load-bearing Big5 leg
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ch", "台吃游群床")
def test_legitimate_taiwan_usage_is_never_flagged(ch: str) -> None:
    """s2t alone false-flags these across 1,651 legitimate files. Big5 saves them."""
    assert ch not in SIMPLIFIED_ONLY_CHARS
    assert ch in BIG5_ENCODABLE_VARIANT_CHARS


@pytest.mark.parametrize("ch", "学说这个财双变录来续")
def test_true_simplified_is_flagged(ch: str) -> None:
    assert ch in SIMPLIFIED_ONLY_CHARS


def test_known_false_negative_is_documented_not_silent() -> None:
    """极 sits inside Big5, so the precision-tuned rule misses it. Accepted."""
    assert "极" not in SIMPLIFIED_ONLY_CHARS


def test_traditional_prose_is_clean() -> None:
    assert distinct_simplified(TRADITIONAL) == (0, "")


def test_simplified_prose_is_detected() -> None:
    n, chars = distinct_simplified(SIMPLIFIED)
    assert n > 0
    assert set(chars) <= SIMPLIFIED_ONLY_CHARS


@pytest.mark.parametrize("n,expected", [
    (1, "SPOT_LEAK"), (2, "SPOT_LEAK"),
    (3, "PARTIAL"), (9, "PARTIAL"),
    (10, "WHOLE_FILE"), (188, "WHOLE_FILE"),
])
def test_severity_tiers(n: int, expected: str) -> None:
    assert severity_for(n) == expected


def test_path_scoping_ignores_other_locales() -> None:
    assert is_zh_tw_atom(ZH)
    assert not is_zh_tw_atom("atoms/x/y/STORY/locales/zh-CN/CANONICAL.txt")
    assert not is_zh_tw_atom("atoms/x/y/STORY/CANONICAL.txt")
    assert not is_zh_tw_atom("docs/zh-TW-notes.md")


# --------------------------------------------------------------------------
# Property 1 — FAILS on newly-introduced Simplified
# --------------------------------------------------------------------------

def _write(tmp_path: Path, rel: str, text: str) -> None:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_gate_fails_on_new_contamination(tmp_path: Path) -> None:
    _write(tmp_path, ZH, SIMPLIFIED)
    violations, _ = evaluate([(ZH, None)], baseline={}, head=None, repo_root=tmp_path)
    assert len(violations) == 1
    assert violations[0].kind == "NEW_CONTAMINATION"
    assert violations[0].allowed == 0
    assert violations[0].found > 0


def test_gate_fails_when_baselined_file_gets_worse(tmp_path: Path) -> None:
    _write(tmp_path, ZH, SIMPLIFIED)
    found, _ = distinct_simplified(SIMPLIFIED)
    violations, _ = evaluate([(ZH, None)], baseline={ZH: found - 1},
                             head=None, repo_root=tmp_path)
    assert len(violations) == 1
    assert violations[0].kind == "WORSENED"


def test_gate_passes_on_clean_traditional_prose(tmp_path: Path) -> None:
    _write(tmp_path, ZH, TRADITIONAL)
    violations, _ = evaluate([(ZH, None)], baseline={}, head=None, repo_root=tmp_path)
    assert violations == []


# --------------------------------------------------------------------------
# Property 2 — PASSES on the existing baseline (main must not redden)
# --------------------------------------------------------------------------

def test_gate_tolerates_unchanged_baseline_debt(tmp_path: Path) -> None:
    """A pre-existing contaminated file, untouched, must not fail the gate."""
    _write(tmp_path, ZH, SIMPLIFIED)
    found, _ = distinct_simplified(SIMPLIFIED)
    violations, repaired = evaluate([(ZH, None)], baseline={ZH: found},
                                    head=None, repo_root=tmp_path)
    assert violations == []
    assert repaired == []


def test_gate_reports_repair_and_never_fails_on_improvement(tmp_path: Path) -> None:
    _write(tmp_path, ZH, TRADITIONAL)
    violations, repaired = evaluate([(ZH, None)], baseline={ZH: 5},
                                    head=None, repo_root=tmp_path)
    assert violations == []
    assert len(repaired) == 1


def test_rename_inherits_baseline_debt(tmp_path: Path) -> None:
    """Moving a contaminated file must not read as brand-new debt."""
    old = "atoms/old_persona/burnout/STORY/locales/zh-TW/CANONICAL.txt"
    _write(tmp_path, ZH, SIMPLIFIED)
    found, _ = distinct_simplified(SIMPLIFIED)
    violations, _ = evaluate([(ZH, old)], baseline={old: found},
                             head=None, repo_root=tmp_path)
    assert violations == []


# --------------------------------------------------------------------------
# The shipped baseline itself
# --------------------------------------------------------------------------

def test_shipped_baseline_matches_audited_corpus() -> None:
    """The baseline records exactly the 8 remaining audited files (down from an
    original 869 as parallel zh-TW decontamination work has landed repairs —
    the baseline "may only shrink" per its own header). It may only shrink further."""
    baseline = load_baseline(BASELINE_PATH)
    assert len(baseline) == 8
    assert all(is_zh_tw_atom(p) for p in baseline)
    assert all(v >= 1 for v in baseline.values())


def test_shipped_baseline_severity_distribution() -> None:
    """Pins lane-02's distinct-char tiering for the current 8-file baseline:
    2 WHOLE_FILE / 5 PARTIAL / 1 SPOT_LEAK (was 42/321/506 against the original
    869-file corpus before parallel zh-TW decontamination repairs landed)."""
    baseline = load_baseline(BASELINE_PATH)
    dist: dict[str, int] = {}
    for n in baseline.values():
        dist[severity_for(n)] = dist.get(severity_for(n), 0) + 1
    assert dist == {"WHOLE_FILE": 2, "PARTIAL": 5, "SPOT_LEAK": 1}


def test_no_zh_tw_files_changed_is_a_noop(tmp_path: Path) -> None:
    """The overwhelming majority of PRs touch no zh-TW atoms; the gate must no-op."""
    violations, repaired = evaluate([], baseline={ZH: 3}, head=None, repo_root=tmp_path)
    assert violations == []
    assert repaired == []

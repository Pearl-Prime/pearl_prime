#!/usr/bin/env python3
"""Regression tests for the scene_anchor_density gate (roadmap B.1 P0 — L2).

Root cause (verified 2026-06-12, see
docs/qa/SCENE_ANCHOR_DENSITY_ROOTCAUSE_2026-06-12.md):

The en_US catalog bestseller audit (artifacts/qa/en_us_catalog_bestseller_audit
_2026-05-13.md) reported 168/200 (84%) of BookSpecs rejected by
`scene_anchor_density` *before* render. That snapshot was taken at the legacy
per-chapter cap=2. PR #1091 then raised the default cap 2→3 and centralized it
in config/quality/scene_anchor_density_config.yaml, because an empirical sweep
of all 168 failing reports showed 156 of them were a SINGLE paragraph over
cap=2 (natural rhetorical motifs), and only 12 had genuine 4+ paragraph
repetition. The audit artifact was never regenerated, so the stale 84% figure
kept presenting an already-fixed gate as the #1 open blocker.

These tests lock the two load-bearing invariants so the gate cannot silently
regress:

  1. The live default cap sourced from config is >= 3 (the PR #1091 floor).
  2. The gate predicate flips a "max paragraph_count == 3" book from FAIL@cap2
     to PASS@cap3, while a "max paragraph_count >= 4" book STAYS FAIL@cap3 —
     i.e. the cap raise recovers the natural-motif yield WITHOUT lowering the
     genuine-duplication catch.

Run:
  PYTHONPATH=. python3 scripts/pearl_prime_en_us/tests/test_scene_anchor_density_gate.py
or under pytest:
  PYTHONPATH=. pytest scripts/pearl_prime_en_us/tests/test_scene_anchor_density_gate.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_run_pipeline():
    """Import scripts/run_pipeline.py as a module without executing main()."""
    path = REPO_ROOT / "scripts" / "run_pipeline.py"
    spec = importlib.util.spec_from_file_location("_rp_for_test", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        # run_pipeline.py guards its CLI behind __main__; import is side-effect free.
        pass
    return mod


def _chapter(phrase: str, n_paras: int) -> str:
    """One registry-style chapter where `phrase` (a 4-word anchor) recurs in
    exactly `n_paras` distinct paragraphs (so max paragraph_count == n_paras).

    Each paragraph carries unique filler tokens so NO other 4..8-gram exceeds
    the cap — the recurring `phrase` is the sole offender, giving a clean
    max-paragraph-count signal.
    """
    paras = []
    for i, uniq in zip(range(n_paras), "abcdefghijklmnop"):
        paras.append(f"Distinct lead {uniq}{i}. {phrase} then trailing token {uniq}{i} end.")
    body = "\n\n".join(paras)
    return f"Chapter 1\n\n{body}"


def _max_paragraph_count(violations) -> int:
    pcs = [o["paragraph_count"] for ch in violations for o in ch["offenders"]]
    return max(pcs) if pcs else 0


def test_live_default_cap_is_at_least_three():
    """The config-sourced default cap must not regress below the PR #1091 floor."""
    rp = _load_run_pipeline()
    cap = int(rp._load_scene_anchor_density_config().get("default_cap_per_chapter", 0))
    assert cap >= 3, (
        f"default_cap_per_chapter is {cap}; PR #1091 set it to 3. A value < 3 "
        f"re-introduces the 84% false-reject (156/168 failures were 1 paragraph "
        f"over the legacy cap=2)."
    )


def test_aggregator_reports_live_cap():
    """The bestseller aggregator must source the cap live (not hardcode cap=2)."""
    path = REPO_ROOT / "scripts" / "pearl_prime_en_us" / "aggregate_bestseller_audit.py"
    spec = importlib.util.spec_from_file_location("_agg_for_test", path)
    assert spec and spec.loader
    agg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agg)
    assert agg.live_scene_anchor_cap() >= 3, (
        "aggregate_bestseller_audit.live_scene_anchor_cap() must reflect the live "
        "config (>=3), so the audit narrative cannot drift back to the stale cap=2 claim."
    )


def test_max_pc_three_flips_fail_to_pass():
    """A single-paragraph-over-cap2 motif (max pc == 3) must FAIL@2 and PASS@3.

    This is the 156/168 case that PR #1091 deliberately recovers.
    """
    rp = _load_run_pipeline()
    prose = _chapter("you say yes before", n_paras=3)

    v2 = rp._scene_anchor_density_violations(prose, 2)
    assert v2, "max pc==3 must be a violation at cap=2"
    assert _max_paragraph_count(v2) == 3

    v3 = rp._scene_anchor_density_violations(prose, 3)
    assert not v3, (
        "max pc==3 must PASS at cap=3 — this is the natural-motif yield PR #1091 recovers"
    )


def test_genuine_repetition_stays_blocked_at_cap_three():
    """4+ paragraph repetition (real overuse) must remain a FAIL even at cap=3.

    Guards against the cap raise being mistaken for 'just disable the gate'.
    """
    rp = _load_run_pipeline()
    for n in (4, 5):
        prose = _chapter("the loop is easier than", n_paras=n)
        v3 = rp._scene_anchor_density_violations(prose, 3)
        assert v3, f"max pc=={n} must STILL FAIL at cap=3 (genuine repetition kept)"
        assert _max_paragraph_count(v3) == n


def _run_all():
    tests = [
        test_live_default_cap_is_at_least_three,
        test_aggregator_reports_live_cap,
        test_max_pc_three_flips_fail_to_pass,
        test_genuine_repetition_stays_blocked_at_cap_three,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())

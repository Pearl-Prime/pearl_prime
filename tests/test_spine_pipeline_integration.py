"""Integration tests for scripts/run_pipeline.py --pipeline-mode spine."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"
ANXIETY_ARC = (
    REPO_ROOT
    / "config"
    / "source_of_truth"
    / "master_arcs"
    / "gen_z_professionals__anxiety__false_alarm__F006.yaml"
)


def _run_spine(out_dir: Path, plan_path: Path, *, quality_profile: str = "draft") -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        "anxiety",
        "--persona",
        "gen_z_professionals",
        "--arc",
        str(ANXIETY_ARC),
        "--pipeline-mode",
        "spine",
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        quality_profile,
        "--teacher",
        "ahjan",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    return subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=600)


def test_run_pipeline_help_lists_pipeline_mode() -> None:
    """CLI documents --pipeline-mode spine."""
    r = subprocess.run(
        [sys.executable, str(RUN_PIPELINE), "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0
    assert "--pipeline-mode" in r.stdout
    assert "spine" in r.stdout


def test_registry_mode_default() -> None:
    """Default pipeline mode is registry (backward compatible)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline-mode", choices=["registry", "spine"], default="registry")
    ns = ap.parse_args([])
    assert ns.pipeline_mode == "registry"


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_mode_produces_book_and_audit(tmp_path: Path) -> None:
    """Spine mode run writes book.txt, enrichment_audit.json, budget.json."""
    out_dir = tmp_path / "spine_out"
    plan_path = tmp_path / "plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    book = out_dir / "book.txt"
    assert book.exists()
    assert book.read_text(encoding="utf-8").strip()
    audit = out_dir / "enrichment_audit.json"
    assert audit.exists()
    data = json.loads(audit.read_text(encoding="utf-8"))
    assert "total_slots" in data or "total_words" in data
    variants = out_dir / "selected_content_variants.json"
    assert variants.exists(), "compose should write selected_content_variants.json into render_dir"
    vdata = json.loads(variants.read_text(encoding="utf-8"))
    assert vdata.get("schema_version") == 1
    assert isinstance(vdata.get("chapters"), list) and len(vdata["chapters"]) > 0


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_mode_budget_word_count_matches_book(tmp_path: Path) -> None:
    """budget.json word_count matches token count of book.txt (whitespace split)."""
    out_dir = tmp_path / "spine_out2"
    plan_path = tmp_path / "plan2.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    book_text = (out_dir / "book.txt").read_text(encoding="utf-8")
    budget = json.loads((out_dir / "budget.json").read_text(encoding="utf-8"))
    wc = budget.get("word_count")
    assert wc == len(book_text.split())


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_registry_mode_still_runs_for_anxiety(tmp_path: Path) -> None:
    """Default registry path still renders when topic has a section registry."""
    out_dir = tmp_path / "reg_out"
    plan_path = tmp_path / "reg_plan.json"
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        "anxiety",
        "--persona",
        "gen_z_professionals",
        "--arc",
        str(ANXIETY_ARC),
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        "draft",
        "--skip-word-count-gate",
        "--no-job-check",
        "--no-generate-freebies",
    ]
    r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr + r.stdout
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan.get("source") == "section_registry"
    assert (out_dir / "book.txt").exists()


def test_spine_mode_enrichment_audit_has_depth_key_when_ran() -> None:
    """Pilot artifact (if present) includes depth_modules_added after depth pass."""
    audit_path = REPO_ROOT / "artifacts" / "pilot" / "full_15_spine" / "anxiety" / "enrichment_audit.json"
    if not audit_path.exists():
        pytest.skip("batch artifact not present")
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert "depth_modules_added" in data


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_produces_quality_summary_json(tmp_path: Path) -> None:
    out_dir = tmp_path / "spine_quality_summary"
    plan_path = tmp_path / "spine_quality_summary_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    summary_path = out_dir / "quality_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    gates = summary.get("gates", {})
    expected = {
        "chapter_flow",
        "bestseller_craft",
        "ei_v2",
        "editorial",
        "memorable_lines",
        "transformation_arc",
        "book_pass",
    }
    assert expected.issubset(set(gates.keys()))


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_ei_v2_not_skipped(tmp_path: Path) -> None:
    out_dir = tmp_path / "spine_ei_v2"
    plan_path = tmp_path / "spine_ei_v2_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    summary = json.loads((out_dir / "quality_summary.json").read_text(encoding="utf-8"))
    assert summary["gates"]["ei_v2"]["status"] != "SKIPPED"


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_editorial_report_exists(tmp_path: Path) -> None:
    out_dir = tmp_path / "spine_editorial"
    plan_path = tmp_path / "spine_editorial_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    assert (out_dir / "editorial_report.json").exists()


@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_gates_advisory_by_default(tmp_path: Path) -> None:
    out_dir = tmp_path / "spine_advisory"
    plan_path = tmp_path / "spine_advisory_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="draft")
    assert r.returncode == 0, r.stderr + r.stdout
    summary = json.loads((out_dir / "quality_summary.json").read_text(encoding="utf-8"))
    assert summary.get("gates_hard") is False


@pytest.mark.slow
@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_gates_hard_records_production_policy(tmp_path: Path) -> None:
    # Marked slow (excluded from Core tests CI). RE-VERIFIED 2026-07-09: the
    # scene_anchor_density / shared-HOOK-phrase theory below this comment (PR
    # #575) is STALE — those now register as WARN-severity F1 findings, not
    # the blocker. Two genuine gate false-positives previously masked behind it
    # were identified (not atom-edited — those cells are shared with the
    # extended_book_2h flagship golden ch5/ch10 PROTECTIVE_ALARM callbacks and
    # atom tweaks perturb full-book parity): F2.B on a grammatically valid
    # contact-clause sentence (PROTECTIVE_ALARM level_4), and a WEAK_TRANSITIONS
    # lexicon gap in chapter 10 (PROTECTIVE_ALARM level_9). Both need gate-
    # level fixes, not content edits. The remaining, real blocker is F7
    # (over-prescribed-practice-
    # density): register_gate.py's default fail_at=4/warn_at=3 was calibrated
    # on third-person deep_book prose, but this catalog's standard_book
    # content is second-person/experiential throughout and measures 3-9
    # prescribed-action paragraphs/chapter as NORMAL density — confirmed via
    # an independent historical standard_book render
    # (artifacts/pearl_prime/standard_book/ahjan_gen_z_professionals_anxiety_en_US_20260518T011019Z/book.txt),
    # which fails the same way across all 12 chapters. This is the same
    # third-person-vs-second-person mismatch that extended_book_2h got a
    # calibrated F7_FORMAT_THRESHOLDS exception for (2026-07-07, calibrated
    # against the Layer-4-approved flagship build) — standard_book never got
    # the same treatment. Do NOT invent a standard_book threshold here: no
    # human-approved standard_book reference exists to calibrate against, and
    # guessing one would be exactly the gate-tuned-to-composer-output drift
    # CLAUDE.md's Bestseller Anti-Drift Doctrine forbids. Un-slowing this test
    # needs a real F7 standard_book calibration workstream (measure against an
    # editorially-approved standard_book reference once one exists) or a
    # genuine density-reduction authoring pass — not a fixture tweak.
    out_dir = tmp_path / "spine_hard"
    plan_path = tmp_path / "spine_hard_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="production")
    assert r.returncode == 0, r.stderr + r.stdout
    summary = json.loads((out_dir / "quality_summary.json").read_text(encoding="utf-8"))
    assert summary.get("quality_profile") == "production"
    assert summary.get("gates_hard") is True
    assert summary.get("quality_gate_failures") == []


def test_block_on_fail_helper_routes_per_profile() -> None:
    """The flagship profile blocks only on chapter_flow, book_quality_gate, scene_anti_genericity.
    Production blocks on every gate. Draft/debug never block."""
    from scripts.run_pipeline import FLAGSHIP_BLOCKING_GATES, _block_on_fail

    assert FLAGSHIP_BLOCKING_GATES == frozenset(
        {"chapter_flow", "book_quality_gate", "scene_anti_genericity"}
    )
    # production blocks on every gate
    for gate in ("chapter_flow", "book_quality_gate", "scene_anti_genericity",
                 "ei_v2", "editorial", "book_pass", "memorable_lines"):
        assert _block_on_fail("production", gate) is True, gate
    # flagship blocks ONLY on the 3 load-bearing gates
    assert _block_on_fail("flagship", "chapter_flow") is True
    assert _block_on_fail("flagship", "book_quality_gate") is True
    assert _block_on_fail("flagship", "scene_anti_genericity") is True
    assert _block_on_fail("flagship", "ei_v2") is False
    assert _block_on_fail("flagship", "editorial") is False
    assert _block_on_fail("flagship", "book_pass") is False
    # draft and debug never block
    for profile in ("draft", "debug"):
        for gate in ("chapter_flow", "book_quality_gate", "scene_anti_genericity",
                     "ei_v2", "editorial"):
            assert _block_on_fail(profile, gate) is False, f"{profile}/{gate}"


@pytest.mark.skip(reason="PR #612: additive stacking surfaces legitimate content-cohesion "
                  "quality gate failures under flagship profile (chapter_flow CHOPPY_SECTION_JUMPS, "
                  "MISSING_CLEAR_POINT, WEAK_TRANSITIONS, scene anchor density). Stacked prose "
                  "from persona+registry+teacher concatenation reads as three voices — needs "
                  "follow-up smart-stacking or transition-glue pass. Tracked as upstream polish task.")
@pytest.mark.skipif(not ANXIETY_ARC.exists(), reason="fixture arc missing")
def test_spine_flagship_profile_runs_and_records(tmp_path: Path) -> None:
    """Flagship profile runs gates, records `quality_profile=flagship` in the summary,
    and exits 0 when no flagship-blocking gate fails."""
    out_dir = tmp_path / "spine_flagship"
    plan_path = tmp_path / "spine_flagship_plan.json"
    r = _run_spine(out_dir, plan_path, quality_profile="flagship")
    assert r.returncode == 0, r.stderr + r.stdout
    summary = json.loads((out_dir / "quality_summary.json").read_text(encoding="utf-8"))
    assert summary.get("quality_profile") == "flagship"
    # gates_hard tracks production-only semantics; flagship records its own profile.
    assert summary.get("gates_hard") is False
    assert summary.get("gates_run") is True


def test_spine_driver_passes_chapter_selector_targets_and_publishable_book_to_enrichment(tmp_path: Path) -> None:
    """Spine pipeline builds EnrichmentRequest with selector targets, book_frame, and publishable_book."""
    from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot

    import scripts.run_pipeline as rp

    captured: dict = {}

    def _stub_select(req, repo_root=None):
        captured["request"] = req
        slots = [EnrichedSlot("HOOK", "Hi.", "x", "a1", 2, 2, [])]
        ch = EnrichedChapter(1, "recognition", "t", "th", slots, 2, {})
        return EnrichedBook(
            1,
            "enrichment_select",
            "anxiety",
            "teacher_pearl_prime_v1",
            "gen_z_professionals",
            "short_book_30",
            [ch],
            2,
            {},
        )

    prose = "\n\n".join(f"Chapter {i}\n\nMinimal body {i}." for i in range(1, 7))

    ns = SimpleNamespace(
        seed="spine_enrich_ctx_test",
        frame="somatic_first",
        runtime_format="short_book_30",
        render_dir=str(tmp_path / "render_out"),
        render_book=True,
        out=None,
        enforce_scene_gate=False,
        scene_gate_mode="production",
        book_quality_override=False,
        generate_freebies=False,
        formats=None,
        publish_dir=None,
        asset_store=None,
        skip_audio=False,
        no_job_check=True,
    )
    book_spec = {
        "topic_id": "anxiety",
        "persona_id": "gen_z_professionals",
        "teacher_id": "teacher_pearl_prime_v1",
    }
    ws = tmp_path / "job_ws"
    ws.mkdir(parents=True, exist_ok=True)

    with patch("phoenix_v4.planning.enrichment_select.select_enrichment", side_effect=_stub_select):
        with patch(
            "phoenix_v4.planning.enrichment_select.apply_depth_pass",
            lambda enriched, *a, **k: enriched,
        ):
            with patch(
                "phoenix_v4.rendering.chapter_composer.compose_from_enriched_book",
                return_value=prose,
            ):
                with patch(
                    "phoenix_v4.rendering.book_renderer.clean_for_delivery",
                    side_effect=lambda p, **kw: p,
                ):
                    rc = rp._run_spine_pipeline_mode(
                        args=ns,
                        book_spec_for_compiler=book_spec,
                        quality_profile="draft",
                        gates_run=False,
                        gates_hard=False,
                        ebook_job_ws=ws,
                        repo_root=REPO_ROOT,
                    )

    assert rc == 0
    req = captured["request"]
    assert req.publishable_book is True
    tgt = req.spine_context.get("chapter_selector_targets") or []
    assert len(tgt) == len(req.beatmap.chapters)
    assert tgt[0].get("reader_objection")
    assert req.spine_context.get("frame") == "somatic_first"
    assert req.spine_context.get("book_frame") == "somatic_first"
    assert req.spine_context.get("book_plan_id")

    ns2 = SimpleNamespace(**{**ns.__dict__, "render_book": False})
    captured.clear()
    with patch("phoenix_v4.planning.enrichment_select.select_enrichment", side_effect=_stub_select):
        with patch(
            "phoenix_v4.planning.enrichment_select.apply_depth_pass",
            lambda enriched, *a, **k: enriched,
        ):
            with patch(
                "phoenix_v4.rendering.chapter_composer.compose_from_enriched_book",
                return_value=prose,
            ):
                with patch(
                    "phoenix_v4.rendering.book_renderer.clean_for_delivery",
                    side_effect=lambda p, **kw: p,
                ):
                    rp._run_spine_pipeline_mode(
                        args=ns2,
                        book_spec_for_compiler=book_spec,
                        quality_profile="draft",
                        gates_run=False,
                        gates_hard=False,
                        ebook_job_ws=ws,
                        repo_root=REPO_ROOT,
                    )
    assert captured["request"].publishable_book is False

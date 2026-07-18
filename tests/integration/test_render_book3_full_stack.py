"""
Full-stack integration: gen_z_professionals × anxiety × ahjan × deep_book_6h (Book 3).

Validates OPD-107 through OPD-118 and Angle Registry v2 features together in one
production-profile render. Expensive (~5–10 min); gated with @pytest.mark.integration.

Defect refs: OPD-107, OPD-108, OPD-109, OPD-112–118, Angle Registry v2 (#1246).
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

from ._helpers import (
    BRIDGE_SIGNATURE_PHRASES,
    CROSS_PERSONA_MARKERS,
    F2_BROKEN_FRAGMENT,
    allowed_persona_atom_ids,
    count_pattern,
    gate_status,
    parse_audit,
    persona_pool_source_ids,
    render_book,
    top_repeated_phrase_count,
    verbatim_gate_reports,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "integration" / "book3_full_stack"
PERSONA = "gen_z_professionals"
TOPIC = "anxiety"
TEACHER = "ahjan"
ANGLE_ID = "PROTECTIVE_ALARM"
WORD_MIN = 50_000
WORD_MAX = 72_000
BRIDGE_MIN_TOTAL = 5
PHRASE_CAP = 12


@pytest.fixture(scope="module")
def book3_render() -> dict:
    """One production render reused by all assertions in this module."""
    out_dir = ARTIFACTS_ROOT / "latest"
    t0 = time.monotonic()
    proc = render_book(out_dir=out_dir)
    elapsed = time.monotonic() - t0
    parsed = parse_audit(out_dir)
    parsed["render_seconds"] = round(elapsed, 1)
    parsed["returncode"] = proc.returncode
    parsed["stderr_tail"] = (proc.stderr or "")[-4000:]
    parsed["stdout_tail"] = (proc.stdout or "")[-4000:]
    if proc.returncode != 0:
        pytest.fail(
            f"run_pipeline exited {proc.returncode} after {elapsed:.1f}s\n"
            f"stderr:\n{proc.stderr[-8000:]}\nstdout:\n{proc.stdout[-4000:]}"
        )
    return parsed


@pytest.mark.integration
@pytest.mark.timeout(7200)
class TestBook3FullStackIntegration:
    """End-to-end Book 3 render with all session architecture features enabled."""

    def test_pipeline_exit_zero(self, book3_render: dict) -> None:
        assert book3_render["returncode"] == 0

    def test_all_quality_gates_pass(self, book3_render: dict) -> None:
        failures: list[str] = []
        for gate_key, report_key in (
            ("book_pass", "book_pass_report"),
            ("book_quality", "book_quality_report"),
            ("chapter_flow", "chapter_flow_report"),
            ("scene_anchor_density", "scene_anchor_density_report"),
        ):
            status = gate_status(book3_render.get(report_key))
            if status != "PASS":
                failures.append(f"{gate_key}: {status}")

        book_pass = book3_render.get("book_pass_report") or {}
        checks = book_pass.get("checks") or {}
        for sub in (
            "band_distribution",
            "identity_stages",
            "callback_completion",
            "word_budget",
        ):
            sub_status = str((checks.get(sub) or {}).get("status") or "MISSING").upper()
            if sub_status != "PASS":
                failures.append(f"book_pass.{sub}: {sub_status}")

        bq = book3_render.get("book_quality_report") or {}
        band = str(bq.get("release_band") or "").strip()
        if band and band not in ("Pass", "PASS"):
            failures.append(f"book_quality_gate release_band: {band}")

        if failures:
            pytest.fail(
                "Gate failures:\n"
                + "\n".join(f"  - {f}" for f in failures)
                + "\n\n"
                + verbatim_gate_reports(book3_render)
            )

    def test_word_count_in_range(self, book3_render: dict) -> None:
        wc = int(book3_render.get("word_count") or 0)
        assert WORD_MIN <= wc <= WORD_MAX, (
            f"word_count {wc} outside [{WORD_MIN}, {WORD_MAX}]"
        )

    def test_no_cross_persona_contamination(self, book3_render: dict) -> None:
        book_txt = book3_render.get("book_txt") or ""
        for marker in CROSS_PERSONA_MARKERS:
            hits = count_pattern(book_txt, re.escape(marker))
            assert hits == 0, (
                f"OPD-118: cross-persona marker {marker!r} found {hits} times"
            )

    def test_angle_definition_ch1_or_fallback_logged(
        self, book3_render: dict
    ) -> None:
        audit = book3_render.get("enrichment_audit") or {}
        spa = audit.get("section_packet_audit") or []
        ch1_angle_def = [
            r
            for r in spa
            if int(r.get("chapter") or 0) == 1
            and str(r.get("slot_type") or "").upper() == "ANGLE_DEFINITION"
        ]
        warnings = audit.get("angle_journey_fallback_warnings") or []
        angle_def_warn = [w for w in warnings if "ANGLE_DEFINITION" in str(w)]
        assert ch1_angle_def or angle_def_warn, (
            "OPD-116: no Ch1 ANGLE_DEFINITION slot and no fallback warning in "
            "enrichment_audit.angle_journey_fallback_warnings"
        )

    def test_angle_callback_ch2_through_12_or_fallback_logged(
        self, book3_render: dict
    ) -> None:
        audit = book3_render.get("enrichment_audit") or {}
        spa = audit.get("section_packet_audit") or []
        callback_chapters = {
            int(r.get("chapter") or 0)
            for r in spa
            if str(r.get("slot_type") or "").upper() == "ANGLE_CALLBACK"
            and int(r.get("chapter") or 0) >= 2
        }
        warnings = audit.get("angle_journey_fallback_warnings") or []
        callback_warn = [w for w in warnings if "ANGLE_CALLBACK" in str(w)]
        expected = set(range(2, 13))
        missing = expected - callback_chapters
        assert not missing or callback_warn, (
            f"OPD-117: ANGLE_CALLBACK missing chapters {sorted(missing)} "
            f"and no ANGLE_CALLBACK fallback warnings"
        )

    def test_bridges_present_in_book(self, book3_render: dict) -> None:
        book_txt = book3_render.get("book_txt") or ""
        total = sum(book_txt.count(phrase) for phrase in BRIDGE_SIGNATURE_PHRASES)
        assert total >= BRIDGE_MIN_TOTAL, (
            f"OPD-109/112: expected >= {BRIDGE_MIN_TOTAL} bridge signature hits, "
            f"got {total} ({BRIDGE_SIGNATURE_PHRASES})"
        )

    def test_no_f2_broken_slot_fragments(self, book3_render: dict) -> None:
        book_txt = book3_render.get("book_txt") or ""
        assert F2_BROKEN_FRAGMENT not in book_txt, (
            f"F2 fragment {F2_BROKEN_FRAGMENT!r} present in rendered book"
        )

    def test_repeated_phrase_density_cap(self, book3_render: dict) -> None:
        book_txt = book3_render.get("book_txt") or ""
        top = top_repeated_phrase_count(book_txt)
        assert top <= PHRASE_CAP, (
            f"book-wide phrase cap: top phrase count {top} > {PHRASE_CAP}"
        )

    def test_persona_pool_atoms_isolated(self, book3_render: dict) -> None:
        audit = book3_render.get("enrichment_audit") or {}
        assert str(audit.get("persona_id") or "") == PERSONA
        rows = persona_pool_source_ids(audit)
        assert rows, "no persona_atom rows in section_packet_audit"
        allowed = allowed_persona_atom_ids(PERSONA, TOPIC)
        bad: list[str] = []
        for row in rows:
            sid = str(row.get("source_id") or "")
            for part in sid.split("+"):
                part = part.strip()
                if not part:
                    continue
                if part.startswith("persona_") and part not in allowed:
                    bad.append(part)
                for persona in (
                    "tech_finance_burnout",
                    "first_responders",
                    "corporate_managers",
                ):
                    if persona in sid:
                        bad.append(f"{sid} (contains {persona})")
        assert not bad, (
            "OPD-118 persona-isolation: persona_atom source_id traces outside "
            f"atoms/{PERSONA}/{TOPIC}/: " + ", ".join(bad[:10])
        )

    def test_render_time_logged(self, book3_render: dict, capsys: pytest.CaptureFixture) -> None:
        """Surface render duration for operator awareness (always passes if render ran)."""
        secs = book3_render.get("render_seconds")
        print(f"\n[integration] Book 3 full-stack render time: {secs}s")
        assert secs is not None and secs > 0

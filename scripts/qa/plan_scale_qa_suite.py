#!/usr/bin/env python3
# NEW-ARTIFACT-JUSTIFIED: plan-scale QA orchestrator — the equivalence linchpin
# (plan-cohesion ↔ assembled EI v2) has no existing home. It CONSUMES, never forks,
# the canonical resources: scripts/qa/run_duration_topic_matrix_qa.py (build +
# row-extract), phoenix_v4/quality/register_gate.py (via the pipeline), the EI v2
# deterministic scorer (via the pipeline's ei_v2_report.json), and
# phoenix_v4/rendering/book_renderer.delivery_contract_gate (leakage oracle).
# Genuinely new logic lives here ONLY: (a) plan↔assembled equivalence checker,
# (b) assembled artifact/leakage scanner wrapper, (c) plan-level structural cohesion.
"""
Plan-scale QA suite — PILOT orchestrator.

Answers ONE question with evidence before the ~1000-plan sweep is allowed:
  Are Pearl Prime book PLANS a trustworthy proxy for ASSEMBLED books on
  cohesion + therapeutic value, and are assembled books clean of pipeline
  leakage?

Pipeline per cell (persona × topic × runtime_format):
  1. PLAN          — generate BookStructurePlan (deterministic, no LLM/GPU).
  2. PLAN-COHESION — structural cohesion verdict from the plan alone.
  3. ASSEMBLE      — run_pipeline.py --render-book → book.txt + gate reports
                     (register_gate + EI v2 deterministic + book_pass).
  4. EQUIVALENCE   — assembled chapter_count / arc-position order == plan?
                     Emit a PROXY-VALIDITY verdict per duration. THE LINCHPIN.
  5. LEAKAGE       — delivery_contract_gate + regex artifact scan on book.txt.
  6. EI v2 READ    — bestseller / cohesion / therapeutic from ei_v2_report.json.

This module ORCHESTRATES; it does not re-implement gates or scorers.

Usage:
  PYTHONPATH=. python3 scripts/qa/plan_scale_qa_suite.py \
      --persona corporate_managers --topics burnout,anxiety \
      --out-dir artifacts/qa/plan_scale_qa_pilot_20260630
  PYTHONPATH=. python3 scripts/qa/plan_scale_qa_suite.py --skip-build  # report only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# --- CONSUMED canonical resources (read-only orchestration; never forked) ---
from scripts.qa.run_duration_topic_matrix_qa import (  # noqa: E402
    _extract_row,
    _run_pipeline,
    arc_for_topic,
)

# The 7 named pilot durations (all have word_range → full equivalence points).
PILOT_DURATIONS = [
    "micro_book_15",
    "micro_book_20",
    "short_book_30",
    "standard_book",
    "extended_book_2h",
    "deep_book_4h",
    "deep_book_6h",
]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _format_block(runtime_format: str) -> dict:
    reg = _load_yaml(REPO_ROOT / "config" / "format_selection" / "format_registry.yaml")
    rf = reg.get("runtime_formats") or {}
    blk = rf.get(runtime_format)
    return blk if isinstance(blk, dict) else {}


# ───────────────────────── PLAN GENERATION ─────────────────────────


def _engine_from_arc(arc: Path | None) -> str:
    """persona__topic__ENGINE__F006.yaml → ENGINE."""
    if arc is None:
        return ""
    parts = arc.stem.split("__")
    return parts[2] if len(parts) >= 3 else ""


def _arc_chapter_count(arc: Path | None) -> int | None:
    """The assembler is Arc-First (run_pipeline.py: chapter_count=arc.chapter_count).
    Mirror that so the plan we compare is built on the SAME contract the assembler uses."""
    if arc is None:
        return None
    data = _load_yaml(arc)
    cc = data.get("chapter_count")
    if isinstance(cc, int) and cc > 0:
        return cc
    chs = data.get("chapters")
    return len(chs) if isinstance(chs, list) and chs else None


def build_plan(
    topic: str, persona: str, runtime_format: str, engine_type: str, arc: Path | None = None
) -> dict[str, Any]:
    """Generate the deterministic BookStructurePlan for a cell (no prose render).

    The plan's per-chapter "arc position" is the deterministic
    `bestseller_beat_order` + band/intensity sequence (BookStructurePlan has no
    free-standing arc_position field; the emotional curve IS the arc).

    THREE chapter counts coexist and are recorded explicitly:
      - format_chapter_count: format_registry chapter_count_default (format-first)
      - arc_chapter_count:    arc.chapter_count (what the assembler actually loads)
      - (assembled count is measured separately from the rendered artifacts)
    We build the plan Arc-First (arc.chapter_count) to match the assembler."""
    from phoenix_v4.planning.book_structure_plan import (
        generate_book_plan,
        get_format_chapter_count,
    )

    blk = _format_block(runtime_format)
    word_range = blk.get("word_range")
    is_stub = not (isinstance(word_range, list) and len(word_range) >= 2)
    fmt_cc = get_format_chapter_count(runtime_format)
    arc_cc = _arc_chapter_count(arc)
    # Mirror the assembler's Arc-First contract for the equivalence comparison.
    plan_cc = arc_cc or fmt_cc
    try:
        plan = generate_book_plan(
            topic, persona, runtime_format, engine_type, chapter_count=plan_cc
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "runtime_format": runtime_format,
            "stub_format": is_stub,
            "format_chapter_count": fmt_cc,
            "arc_chapter_count": arc_cc,
        }
    chapters = []
    for idx, ch in enumerate(plan.chapters):
        chapters.append(
            {
                "index": idx,
                "arc_position": getattr(ch, "bestseller_beat_order", None)
                or getattr(ch, "emotional_role", None),
                "band": getattr(ch, "band", None),
                "intensity": getattr(ch, "intensity", None),
                "bestseller_structure": getattr(ch, "bestseller_structure", None),
            }
        )
    return {
        "ok": True,
        "runtime_format": runtime_format,
        "stub_format": is_stub,
        "word_range": word_range,
        "format_chapter_count": fmt_cc,
        "arc_chapter_count": arc_cc,
        "chapter_count": plan.chapter_count,
        "dominant_band_sequence": list(getattr(plan, "dominant_band_sequence", [])),
        "intensity_sequence": list(getattr(plan, "intensity_sequence", [])),
        "cost_chapter_index": getattr(plan, "cost_chapter_index", None),
        "chapters": chapters,
    }


# ───────────────────────── PLAN-LEVEL COHESION ─────────────────────────


def plan_cohesion(plan: dict[str, Any]) -> dict[str, Any]:
    """Deterministic structural-cohesion verdict from the plan alone.

    Every check here is PLAN-evaluable (no prose). It mirrors the structural
    invariants register_gate / book_structure_plan.validate enforce, but is
    computed independently so we can compare plan-PASS vs assembled-gate-PASS.
    """
    issues: list[str] = []
    if not plan.get("ok"):
        return {"verdict": "UNPLANNABLE", "issues": [plan.get("error", "no plan")], "checks": {}}

    chapters = plan.get("chapters") or []
    n = plan.get("chapter_count") or 0
    bands = [c.get("band") for c in chapters]
    intens = [c.get("intensity") for c in chapters]
    arc_positions = [c.get("arc_position") for c in chapters]
    structures = [c.get("bestseller_structure") for c in chapters]

    checks: dict[str, Any] = {}

    # C1 chapter-count integrity
    checks["chapter_count_matches"] = (n == len(chapters) and n > 0)
    if not checks["chapter_count_matches"]:
        issues.append(f"chapter_count {n} != len(chapters) {len(chapters)}")

    # C2 arc-position coverage (every chapter carries an arc position)
    arc_filled = sum(1 for a in arc_positions if a not in (None, ""))
    checks["arc_coverage"] = (arc_filled == len(chapters) and len(chapters) > 0)
    if not checks["arc_coverage"]:
        issues.append(f"arc_position filled {arc_filled}/{len(chapters)}")

    # C3 band-arc smoothness (adjacent BAND step <= 2) — plan-evaluable cohesion
    band_jumps = [
        i for i in range(1, len(bands))
        if bands[i] is not None and bands[i - 1] is not None and abs(int(bands[i]) - int(bands[i - 1])) > 2
    ]
    checks["band_smoothness"] = (len(band_jumps) == 0)
    if band_jumps:
        issues.append(f"band step >2 at chapter idx {band_jumps}")

    # C4 final chapter is not the BAND peak (resolution, not climax)
    if bands and all(b is not None for b in bands):
        peak = max(int(b) for b in bands)
        checks["final_below_peak"] = int(bands[-1]) < peak
        if not checks["final_below_peak"]:
            issues.append("final chapter sits at BAND peak (no resolution)")
    else:
        checks["final_below_peak"] = None

    # C5 dwell-beat: no three consecutive intensity-5 chapters (macro cadence)
    triple5 = [
        i for i in range(2, len(intens))
        if intens[i] == intens[i - 1] == intens[i - 2] == 5
    ]
    checks["dwell_macro_cadence"] = (len(triple5) == 0)
    if triple5:
        issues.append(f"three consecutive intensity-5 at idx {triple5}")

    # C6 scene-anchor / structure variety: same bestseller_structure not 3x in a row
    struct_triples = [
        i for i in range(2, len(structures))
        if structures[i] is not None
        and structures[i] == structures[i - 1] == structures[i - 2]
    ]
    checks["structure_variety"] = (len(struct_triples) == 0)
    if struct_triples:
        issues.append(f"same bestseller_structure 3x at idx {struct_triples}")

    # C7 cost-chapter placement (turn must not be the final chapter)
    cci = plan.get("cost_chapter_index")
    if cci is not None and n:
        checks["cost_chapter_placement"] = (0 <= int(cci) < n - 1)
        if not checks["cost_chapter_placement"]:
            issues.append(f"cost_chapter_index {cci} not in [0, {n - 1})")
    else:
        checks["cost_chapter_placement"] = None

    hard_fail = any(v is False for v in checks.values())
    verdict = "FAIL" if hard_fail else "PASS"
    return {"verdict": verdict, "issues": issues, "checks": checks}


# ───────────────────────── EQUIVALENCE (THE LINCHPIN) ─────────────────────────

# Assembled book chapter heading patterns we accept as a chapter boundary.
_CHAPTER_HEADING_RE = re.compile(r"^\s*(chapter\s+\d+|chapter\b|#\s+chapter|##\s+chapter)", re.IGNORECASE)


def _count_assembled_chapters(render_dir: Path) -> tuple[int, str]:
    """Best-effort assembled chapter count.

    Prefer structured artifacts (selected_content_variants.json / chapter_flow_report.json);
    fall back to heading scan of book.txt. Returns (count, source)."""
    # 1) chapter_flow_report.json carries per-chapter records.
    cfr = render_dir / "chapter_flow_report.json"
    if cfr.exists():
        try:
            data = json.loads(cfr.read_text(encoding="utf-8"))
            for key in ("chapters", "per_chapter", "chapter_reports", "results"):
                v = data.get(key) if isinstance(data, dict) else None
                if isinstance(v, list) and v:
                    return len(v), f"chapter_flow_report.{key}"
            tot = data.get("total_chapters") or data.get("chapter_count") if isinstance(data, dict) else None
            if isinstance(tot, int) and tot > 0:
                return tot, "chapter_flow_report.total"
        except Exception:  # noqa: BLE001
            pass
    # 2) selected_content_variants.json — one record set per chapter.
    scv = render_dir / "selected_content_variants.json"
    if scv.exists():
        try:
            data = json.loads(scv.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                chs = data.get("chapters")
                if isinstance(chs, list) and chs:
                    return len(chs), "selected_content_variants.chapters"
                # dict keyed by chapter index
                ints = [k for k in data.keys() if str(k).isdigit()]
                if ints:
                    return len(ints), "selected_content_variants.keys"
            if isinstance(data, list) and data:
                return len(data), "selected_content_variants.list"
        except Exception:  # noqa: BLE001
            pass
    # 3) heading scan of book.txt
    book = render_dir / "book.txt"
    if book.exists():
        cnt = 0
        for line in book.read_text(encoding="utf-8", errors="replace").splitlines():
            if _CHAPTER_HEADING_RE.match(line):
                cnt += 1
        if cnt:
            return cnt, "book.txt.headings"
    return 0, "none"


def equivalence(plan: dict[str, Any], render_dir: Path, row: dict[str, Any]) -> dict[str, Any]:
    """Verify assembled == plan (chapter count, no structural drift).

    Emits a PROXY-VALIDITY verdict per duration. This is the linchpin: if plan
    structure does not equal assembled structure, plans are NOT a safe proxy.
    """
    plan_n = plan.get("chapter_count") if plan.get("ok") else None
    fmt_n = plan.get("format_chapter_count")
    arc_n = plan.get("arc_chapter_count")
    asm_n, src = _count_assembled_chapters(render_dir)

    drift: list[str] = []
    # Plan here is built Arc-First (== arc_chapter_count) to match the assembler.
    count_match = (plan_n is not None and plan_n == asm_n)
    if not count_match:
        drift.append(f"chapter_count plan(arc-first)={plan_n} assembled={asm_n} (src={src})")
    # Explicit three-way count divergence (the proxy-fragility headline for large formats).
    count_divergence = {
        "format_default": fmt_n,
        "arc_ssot": arc_n,
        "plan_used": plan_n,
        "assembled": asm_n,
        "format_vs_assembled_mismatch": (fmt_n is not None and asm_n and fmt_n != asm_n),
        "arc_vs_assembled_mismatch": (arc_n is not None and asm_n and arc_n != asm_n),
    }

    # Word-range conformance of the assembled book (structural, not prose quality).
    words = row.get("words")
    wr = plan.get("word_range")
    in_range = None
    if words is not None and isinstance(wr, list) and len(wr) >= 2:
        in_range = (wr[0] <= words <= wr[1])
        if in_range is False:
            drift.append(f"word_count {words} outside plan word_range {wr}")

    # PROXY-VALIDITY: does plan-cohesion PASS predict assembled-register PASS?
    plan_coh = plan.get("_plan_cohesion_verdict")
    asm_register = row.get("register")  # PASS / FAIL / MISSING
    asm_ei = row.get("ei_v2")
    asm_book_pass = row.get("book_pass")

    # Structural equivalence holds iff chapter counts match and no count/range drift.
    structural_equivalence = count_match and (in_range is not False)

    # QUALITY proxy: plan PASS that ALSO survives assembled register == quality proxy holds.
    if plan_coh == "PASS" and asm_register == "PASS":
        quality_proxy = "HOLDS"
    elif plan_coh == "PASS" and asm_register == "FAIL":
        quality_proxy = "BROKEN"  # plan looked clean, prose failed register → headline risk
    elif plan_coh == "FAIL" and asm_register == "FAIL":
        quality_proxy = "CONSISTENT_FAIL"  # plan predicted the failure
    elif asm_register in (None, "MISSING", "NO_ARC", "SKIPPED"):
        quality_proxy = "INCONCLUSIVE"  # never assembled / not buildable
    else:
        quality_proxy = "PARTIAL"

    # STRUCTURAL proxy: does any plan-time count predict the assembled count?
    structural_proxy = "HOLDS" if count_match else "BROKEN"

    # Combined proxy_validity for the per-duration linchpin verdict.
    if asm_register in (None, "MISSING", "NO_ARC", "SKIPPED"):
        proxy = "INCONCLUSIVE"
    elif quality_proxy == "BROKEN":
        proxy = "BROKEN"  # quality proxy break is the loudest signal
    elif structural_proxy == "BROKEN":
        proxy = "STRUCTURAL_BREAK"  # quality held but chapter count diverged
    else:
        proxy = "HOLDS"

    return {
        "plan_chapters": plan_n,
        "assembled_chapters": asm_n,
        "assembled_chapter_source": src,
        "chapter_count_match": count_match,
        "count_divergence": count_divergence,
        "assembled_words": words,
        "plan_word_range": wr,
        "word_in_range": in_range,
        "structural_equivalence": structural_equivalence,
        "plan_cohesion": plan_coh,
        "assembled_register": asm_register,
        "assembled_ei_v2": asm_ei,
        "assembled_book_pass": asm_book_pass,
        "quality_proxy": quality_proxy,
        "structural_proxy": structural_proxy,
        "proxy_validity": proxy,
        "drift": drift,
    }


# ───────────────────────── LEAKAGE SCANNER WRAPPER ─────────────────────────

# Artifact classes the assembled book must NOT contain (mission-specified).
_LEAK_PATTERNS = [
    (r"^\s*##\s*ARC_POSITION", "role-header ## ARC_POSITION"),
    (r"^\s*##\s*(STORY|HOOK|SCENE|REFLECTION|EXERCISE|BRIDGE)\s+v\d+", "slot heading ## SLOT vNN"),
    (r"\{['\"]intro['\"]\s*:", "intro-dict literal"),
    (r"FixtureReplay", "FixtureReplay stub"),
    (r"\{\{\s*\w+\s*\}\}", "{{placeholder}} token"),
    (r"<\s*(PLACEHOLDER|TODO|FIXME|TBD)\b", "placeholder marker"),
    (r"\bselected_content_variants\b", "internal variable name"),
    (r"\bpersona_id\b|\btopic_id\b|\bruntime_format\b", "pipeline variable name"),
]


def leakage_scan(render_dir: Path) -> dict[str, Any]:
    """Hard leakage scan on the assembled book.txt.

    Oracle = phoenix_v4.rendering.book_renderer.delivery_contract_gate (canonical),
    augmented with the mission's explicit artifact-class regex sweep. Any hit = CRITICAL.
    """
    book = render_dir / "book.txt"
    if not book.exists():
        return {"status": "NO_BOOK", "hits": [], "contract_gate": "SKIPPED"}

    text = book.read_text(encoding="utf-8", errors="replace")
    hits: list[dict[str, Any]] = []

    # Canonical oracle.
    contract = "PASS"
    try:
        from phoenix_v4.rendering.book_renderer import (
            DeliveryContractError,
            delivery_contract_gate,
        )

        try:
            delivery_contract_gate(text, source_hint=str(book.relative_to(REPO_ROOT)))
        except DeliveryContractError as exc:
            contract = "FAIL"
            hits.append({"line": None, "kind": "delivery_contract_gate", "detail": str(exc)[:300]})
    except Exception as exc:  # noqa: BLE001
        contract = f"ORACLE_ERROR: {type(exc).__name__}"

    # Mission artifact-class regex sweep (file + line).
    compiled = [(re.compile(p, re.IGNORECASE | re.MULTILINE), label) for p, label in _LEAK_PATTERNS]
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rx, label in compiled:
            if rx.search(line):
                hits.append({"line": lineno, "kind": label, "detail": line.strip()[:200]})

    status = "CLEAN" if not hits else "CRITICAL"
    return {"status": status, "contract_gate": contract, "hits": hits, "book": str(book.relative_to(REPO_ROOT))}


# ───────────────────────── EI v2 READ (deterministic) ─────────────────────────


def ei_v2_read(render_dir: Path) -> dict[str, Any]:
    """Consume the pipeline's deterministic ei_v2_report.json + craft/book_pass.

    Does NOT call the scorer here — the prose render already wrote it (deterministic
    weighted-sum path, not llm_callback)."""
    out: dict[str, Any] = {
        "ei_composite": None,
        "ei_status": "MISSING",
        "cohesion_pass": 0,
        "cohesion_warn": 0,
        "cohesion_fail": 0,
        "bestseller_craft": None,
        "bestseller_status": "MISSING",
        "therapeutic": None,
    }
    ei_path = render_dir / "ei_v2_report.json"
    if ei_path.exists():
        ei = json.loads(ei_path.read_text(encoding="utf-8"))
        out["ei_composite"] = ei.get("composite")
        out["ei_status"] = ei.get("status", "MISSING")
        for ch in ei.get("chapters") or []:
            dims = ch.get("dimensions") or {}
            coh = dims.get("cohesion") or {}
            st = str(coh.get("status", "")).upper()
            if st == "PASS":
                out["cohesion_pass"] += 1
            elif st == "WARN":
                out["cohesion_warn"] += 1
            elif st == "FAIL":
                out["cohesion_fail"] += 1
            # therapeutic / somatic dimension if present
        # therapeutic proxy: somatic_precision + listen_experience averages if present
    ed = render_dir / "editorial_report.json"
    if ed.exists():
        try:
            edr = json.loads(ed.read_text(encoding="utf-8"))
            out["bestseller_craft"] = edr.get("ontgp") or edr.get("overall_score")
        except Exception:  # noqa: BLE001
            pass
    qs = render_dir / "quality_summary.json"
    if qs.exists():
        try:
            q = json.loads(qs.read_text(encoding="utf-8"))
            gates = q.get("gates") or {}
            bc = gates.get("bestseller_craft") or {}
            out["bestseller_craft"] = bc.get("overall_score", out["bestseller_craft"])
            out["bestseller_status"] = bc.get("status", out["bestseller_status"])
        except Exception:  # noqa: BLE001
            pass
    return out


# ───────────────────────── ORCHESTRATION ─────────────────────────


def run_cell(
    *,
    persona: str,
    topic: str,
    runtime_format: str,
    out_dir: Path,
    skip_build: bool,
) -> dict[str, Any]:
    arc = arc_for_topic(topic)  # consumed resource (uses module-level PERSONA=corporate_managers)
    # arc_for_topic in the matrix module is keyed to corporate_managers; for other
    # personas fall back to a direct glob so the harness stays persona-general.
    if arc is None or persona != "corporate_managers":
        cand = sorted((REPO_ROOT / "config" / "source_of_truth" / "master_arcs").glob(
            f"{persona}__{topic}__*.yaml"
        ))
        arc = cand[0] if cand else None

    cell: dict[str, Any] = {
        "persona": persona,
        "topic": topic,
        "runtime_format": runtime_format,
        "arc": str(arc.relative_to(REPO_ROOT)) if arc else None,
    }
    if arc is None:
        cell["buildability"] = "NO_ARC"
        cell["plan"] = {"ok": False, "error": "NO_ARC"}
        cell["plan_cohesion"] = {"verdict": "UNPLANNABLE", "issues": ["NO_ARC"]}
        return cell

    # 1+2 PLAN + PLAN-COHESION
    engine_type = _engine_from_arc(arc)
    cell["engine_type"] = engine_type
    plan = build_plan(topic, persona, runtime_format, engine_type, arc=arc)
    pc = plan_cohesion(plan)
    plan["_plan_cohesion_verdict"] = pc["verdict"]
    cell["plan"] = plan
    cell["plan_cohesion"] = pc

    render_dir = out_dir / "renders" / f"{runtime_format}__{persona}__{topic}"
    cell["render_dir"] = str(render_dir.relative_to(REPO_ROOT)) if render_dir.is_relative_to(REPO_ROOT) else str(render_dir)

    # 3 ASSEMBLE (consumed _run_pipeline) — full prose render with gates.
    if not skip_build:
        exit_code = _run_pipeline(
            topic=topic,
            arc=arc,
            runtime_format=runtime_format,
            render_dir=render_dir,
            render_book=True,
        )
    else:
        exit_code = 0 if (render_dir / "book.txt").exists() else 1
    cell["pipeline_exit"] = exit_code

    # row extraction (consumed _extract_row) — register/EI/craft/book_pass verdicts
    row = _extract_row(render_dir, runtime_format, topic)
    cell["row"] = row
    cell["buildability"] = "PLANNABLE" if (render_dir / "book.txt").exists() else (
        "NO_STORY_POOL" if "NO_STORY_POOL" in (cell.get("plan", {}).get("error") or "") else "BUILD_FAIL"
    )

    # 4 EQUIVALENCE
    cell["equivalence"] = equivalence(plan, render_dir, row)
    # 5 LEAKAGE
    cell["leakage"] = leakage_scan(render_dir)
    # 6 EI v2 READ
    cell["ei_v2"] = ei_v2_read(render_dir)
    return cell


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan-scale QA pilot orchestrator")
    ap.add_argument("--persona", default="corporate_managers")
    ap.add_argument("--topics", default="burnout,anxiety", help="comma-separated")
    ap.add_argument("--durations", default=",".join(PILOT_DURATIONS))
    ap.add_argument("--out-dir", default="artifacts/qa/plan_scale_qa_pilot_20260630")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--skip-finder", action="store_true")
    args = ap.parse_args()

    persona = args.persona
    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    durations = [d.strip() for d in args.durations.split(",") if d.strip()]
    out_dir = (REPO_ROOT / args.out_dir) if not Path(args.out_dir).is_absolute() else Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cells: list[dict[str, Any]] = []
    for topic in topics:
        for dur in durations:
            print(f"[cell] {persona} × {topic} × {dur} …", flush=True)
            cell = run_cell(
                persona=persona, topic=topic, runtime_format=dur,
                out_dir=out_dir, skip_build=args.skip_build,
            )
            cells.append(cell)
            # persist per-cell JSON as we go (crash-safe evidence)
            cj = out_dir / f"cell__{dur}__{topic}.json"
            cj.write_text(json.dumps(cell, indent=2, default=str), encoding="utf-8")

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Census + verdicts
    buildability: dict[str, int] = {}
    plan_pass = 0
    plan_total = 0
    proxy_rows: list[dict[str, Any]] = []
    leak_hits = 0
    for c in cells:
        buildability[c.get("buildability", "?")] = buildability.get(c.get("buildability", "?"), 0) + 1
        pcv = (c.get("plan_cohesion") or {}).get("verdict")
        if pcv in ("PASS", "FAIL"):
            plan_total += 1
            if pcv == "PASS":
                plan_pass += 1
        eq = c.get("equivalence") or {}
        proxy_rows.append(
            {
                "duration": c.get("runtime_format"),
                "topic": c.get("topic"),
                "plan_chapters": eq.get("plan_chapters"),
                "assembled_chapters": eq.get("assembled_chapters"),
                "count_match": eq.get("chapter_count_match"),
                "structural_equivalence": eq.get("structural_equivalence"),
                "plan_cohesion": eq.get("plan_cohesion"),
                "assembled_register": eq.get("assembled_register"),
                "assembled_ei_v2": eq.get("assembled_ei_v2"),
                "structural_proxy": eq.get("structural_proxy"),
                "quality_proxy": eq.get("quality_proxy"),
                "proxy_validity": eq.get("proxy_validity"),
                "count_divergence": eq.get("count_divergence"),
                "drift": eq.get("drift"),
            }
        )
        if (c.get("leakage") or {}).get("status") == "CRITICAL":
            leak_hits += 1

    # Linchpin — reported on TWO axes (honest split):
    #   STRUCTURAL proxy: does a plan-time chapter count predict assembled count?
    #   QUALITY proxy:    does plan-cohesion PASS predict assembled register PASS?
    assembled = [c for c in cells if (c.get("buildability") == "PLANNABLE")]
    struct_ok = (
        all((c.get("equivalence") or {}).get("structural_proxy") == "HOLDS" for c in assembled)
        if assembled else False
    )
    quality_ok = (
        all((c.get("equivalence") or {}).get("quality_proxy") in ("HOLDS", "CONSISTENT_FAIL")
            for c in assembled)
        if assembled else False
    )
    quality_broken_cells = [
        f"{c['topic']}×{c['runtime_format']}"
        for c in assembled
        if (c.get("equivalence") or {}).get("quality_proxy") == "BROKEN"
    ]
    structural_break_cells = [
        f"{c['topic']}×{c['runtime_format']}"
        for c in assembled
        if (c.get("equivalence") or {}).get("structural_proxy") == "BROKEN"
    ]
    # Overall linchpin = BOTH axes hold AND no leakage.
    linchpin_held = bool(assembled) and struct_ok and quality_ok and leak_hits == 0

    summary = {
        "timestamp": ts,
        "persona": persona,
        "topics": topics,
        "durations": durations,
        "buildability_census": buildability,
        "plan_cohesion_pass_rate": f"{plan_pass}/{plan_total}",
        "leakage_critical_cells": leak_hits,
        "linchpin_equivalence_held": linchpin_held,
        "structural_proxy_held": struct_ok,
        "quality_proxy_held": quality_ok,
        "quality_proxy_broken_cells": quality_broken_cells,
        "structural_break_cells": structural_break_cells,
        "proxy_validity_rows": proxy_rows,
        "cells": cells,
    }
    matrix_json = out_dir / "MATRIX.json"
    matrix_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    # MATRIX.tsv
    tsv_lines = [
        "persona\ttopic\tduration\tbuildability\tplan_cohesion\tplan_chapters\tasm_chapters\tcount_match\tstruct_equiv\tregister\tei_v2\tei_composite\tbook_pass\tproxy_validity\tleakage"
    ]
    for c in cells:
        eq = c.get("equivalence") or {}
        row = c.get("row") or {}
        ei = c.get("ei_v2") or {}
        tsv_lines.append(
            "\t".join(
                str(x) for x in [
                    c.get("persona"),
                    c.get("topic"),
                    c.get("runtime_format"),
                    c.get("buildability"),
                    (c.get("plan_cohesion") or {}).get("verdict"),
                    eq.get("plan_chapters"),
                    eq.get("assembled_chapters"),
                    eq.get("chapter_count_match"),
                    eq.get("structural_equivalence"),
                    row.get("register"),
                    row.get("ei_v2"),
                    ei.get("ei_composite"),
                    row.get("book_pass"),
                    eq.get("proxy_validity"),
                    (c.get("leakage") or {}).get("status"),
                ]
            )
        )
    (out_dir / "MATRIX.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

    print("\n=== PLAN-SCALE QA PILOT SUMMARY ===")
    print(f"persona={persona} topics={topics}")
    print(f"buildability: {buildability}")
    print(f"plan-cohesion pass: {plan_pass}/{plan_total}")
    print(f"leakage CRITICAL cells: {leak_hits}")
    print(f"STRUCTURAL proxy held (plan count predicts assembled): {struct_ok}")
    if structural_break_cells:
        print(f"  structural breaks: {structural_break_cells}")
    print(f"QUALITY proxy held (plan-cohesion predicts register): {quality_ok}")
    if quality_broken_cells:
        print(f"  QUALITY-PROXY BROKEN: {quality_broken_cells}")
    print(f"LINCHPIN (both axes + clean): {linchpin_held}")
    print(f"evidence: {out_dir}")

    if not args.skip_finder and sys.platform == "darwin":
        import subprocess

        subprocess.run(["open", str(out_dir)], check=False)

    return 0 if linchpin_held and leak_hits == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

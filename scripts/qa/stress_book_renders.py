#!/usr/bin/env python3
"""Pearl Prime book render stress audit runner.

Runs canonical production spine renders into isolated /tmp work dirs, captures
compact gate/report artifacts, and scrubs manuscript text from the audit output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for stress_book_renders.py") from exc


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
ATOMS_ROOT = REPO_ROOT / "atoms"
FORMAT_REGISTRY = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"

REPORT_NAMES = (
    "book_pass_report.json",
    "book_quality_report.json",
    "chapter_flow_report.json",
    "register_gate_report.json",
    "editorial_report.json",
    "transformation_heatmap.json",
    "enhancement_contract.json",
    "rendered_accent_audit.json",
    "book_outline.json",
    "quality_summary.json",
    "budget.json",
    "enrichment_audit.json",
    "enrichment_strategy_report.json",
    "bestseller_alignment_report.json",
    "section_packet_audit.json",
    "scene_anchor_density_report.json",
    "ei_v2_report.json",
    "memorable_line_report.json",
)

BUCKETS = (
    "atom_bank_depth",
    "missing_story_pool",
    "schema/config",
    "tuple_not_viable",
    "exercise_journey_mismatch",
    "register_gate",
    "chapter_flow",
    "transformation_arc",
    "editorial_quality",
    "enhancement_planning",
    "enhancement_rendering",
    "locale_fallback",
    "selected_content_repetition",
    "renderer_exception",
    "CLI/config ergonomics",
)

HIGH_RISK_PAIRS = (
    ("gen_z_professionals", "anxiety"),
    ("corporate_managers", "burnout"),
    ("educators", "anxiety"),
)

PREFERRED_ENGINE_ORDER = (
    "grief",
    "spiral",
    "watcher",
    "overwhelm",
    "false_alarm",
    "comparison",
    "shame",
)

RUNTIME_BY_STRUCTURAL = {
    "F003": "short_book_30",
    "F015": "micro_book_15",
    "F013": "deep_book_4h",
    "F004": "deep_book_4h",
    "F009": "deep_book_4h",
    "F002": "standard_book",
    "F006": "standard_book",
    "F007": "standard_book",
    "F010": "standard_book",
    "F011": "standard_book",
    "F014": "standard_book",
}


@dataclass(frozen=True)
class ArcCandidate:
    persona: str
    topic: str
    engine: str
    structural_format: str
    arc_path: str
    atom_file_count: int
    atom_slot_count: int
    story_bank_count: int
    locale_count: int
    locales: tuple[str, ...]

    @property
    def key(self) -> str:
        return f"{self.persona}__{self.topic}__{self.engine}__{self.structural_format}"


@dataclass(frozen=True)
class RenderJob:
    candidate: ArcCandidate
    locale: str
    seed: str
    runtime_format: str
    sample_reason: str

    @property
    def run_id(self) -> str:
        raw = f"{self.candidate.key}__{self.locale}__{self.runtime_format}__{self.seed}"
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
        safe_locale = self.locale.replace("-", "_")
        return f"{self.candidate.key}__{safe_locale}__{self.runtime_format}__{digest}"

    def tuple_label(self) -> str:
        return (
            f"{self.candidate.persona} × {self.candidate.topic} × "
            f"{self.candidate.engine} × {self.candidate.structural_format} × "
            f"{self.locale} × {self.runtime_format} × {self.seed}"
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _parse_arc_path(path: Path) -> tuple[str, str, str, str] | None:
    parts = path.stem.split("__")
    if len(parts) != 4:
        return None
    persona, topic, engine, structural = (p.strip() for p in parts)
    if not persona or not topic or not engine or not structural:
        return None
    return persona, topic, engine, structural


def _atom_stats(persona: str, topic: str) -> tuple[int, int, int, tuple[str, ...]]:
    base = ATOMS_ROOT / persona / topic
    if not base.exists():
        return 0, 0, 0, tuple()
    canonical_paths = list(base.rglob("CANONICAL.txt"))
    root_canonicals = [p for p in canonical_paths if "/locales/" not in p.as_posix()]
    slots = {
        p.relative_to(base).parts[0]
        for p in root_canonicals
        if p.relative_to(base).parts
    }
    story_count = 0
    for p in root_canonicals:
        rel = p.relative_to(base).parts
        if rel and rel[0] in {"STORY", "story"} | set(PREFERRED_ENGINE_ORDER):
            story_count += 1
    locales = sorted(
        {
            p.relative_to(base).parts[p.relative_to(base).parts.index("locales") + 1]
            for p in canonical_paths
            if "locales" in p.relative_to(base).parts
            and len(p.relative_to(base).parts) > p.relative_to(base).parts.index("locales") + 1
        }
    )
    return len(root_canonicals), len(slots), story_count, tuple(locales)


def build_inventory() -> list[ArcCandidate]:
    candidates: list[ArcCandidate] = []
    for arc_path in sorted(ARCS_ROOT.rglob("*.yaml")):
        parsed = _parse_arc_path(arc_path)
        if not parsed:
            continue
        persona, topic, engine, structural = parsed
        atom_file_count, atom_slot_count, story_bank_count, locales = _atom_stats(persona, topic)
        candidates.append(
            ArcCandidate(
                persona=persona,
                topic=topic,
                engine=engine,
                structural_format=structural,
                arc_path=str(arc_path.relative_to(REPO_ROOT)),
                atom_file_count=atom_file_count,
                atom_slot_count=atom_slot_count,
                story_bank_count=story_bank_count,
                locale_count=len(locales),
                locales=locales,
            )
        )
    return candidates


def _runtime_for(candidate: ArcCandidate, ordinal: int) -> str:
    # Exercise runtime variety without moving off the canonical spine path.
    if ordinal % 11 == 0 and candidate.structural_format in {"F003", "F006", "F007", "F011"}:
        return "one_hour_book"
    return RUNTIME_BY_STRUCTURAL.get(candidate.structural_format, "standard_book")


def _preferred_sort_key(candidate: ArcCandidate) -> tuple[int, str]:
    try:
        engine_rank = PREFERRED_ENGINE_ORDER.index(candidate.engine)
    except ValueError:
        engine_rank = len(PREFERRED_ENGINE_ORDER)
    return engine_rank, candidate.key


def _pick_first(
    candidates: list[ArcCandidate],
    *,
    persona: str,
    topic: str,
    used: set[str],
) -> ArcCandidate | None:
    pool = [
        c
        for c in candidates
        if c.persona == persona and c.topic == topic and c.key not in used
    ]
    if not pool:
        return None
    pool.sort(key=_preferred_sort_key)
    picked = pool[0]
    used.add(picked.key)
    return picked


def _round_robin_candidates(candidates: list[ArcCandidate], used: set[str]) -> Iterable[ArcCandidate]:
    viable = [c for c in candidates if c.key not in used and c.atom_file_count > 0]
    viable.sort(key=lambda c: (c.persona, c.topic, _preferred_sort_key(c)))
    by_persona: dict[str, list[ArcCandidate]] = {}
    for c in viable:
        by_persona.setdefault(c.persona, []).append(c)
    personas = sorted(by_persona)
    while personas:
        next_personas = []
        for persona in personas:
            bucket = by_persona[persona]
            if not bucket:
                continue
            candidate = bucket.pop(0)
            if candidate.key not in used:
                used.add(candidate.key)
                yield candidate
            if bucket:
                next_personas.append(persona)
        personas = next_personas


def build_jobs(
    candidates: list[ArcCandidate],
    *,
    limit: int,
    locales: list[str],
    seed_prefix: str,
) -> list[RenderJob]:
    used: set[str] = set()
    ordered: list[tuple[ArcCandidate, str]] = []
    for persona, topic in HIGH_RISK_PAIRS:
        picked = _pick_first(candidates, persona=persona, topic=topic, used=used)
        if picked is not None:
            ordered.append((picked, "high_risk_known_tuple"))

    wants_zh_tw = "zh-TW" in locales
    if wants_zh_tw and not any(reason == "locale_coverage_zh_TW" for _, reason in ordered):
        zh_pool = [
            c
            for c in candidates
            if c.key not in used
            and "zh-TW" in c.locales
            and c.atom_file_count > 0
            and c.story_bank_count > 0
        ]
        zh_pool.sort(key=lambda c: (0 if (c.persona, c.topic) in HIGH_RISK_PAIRS else 1, c.persona, c.topic, c.engine))
        if zh_pool:
            picked = zh_pool[0]
            used.add(picked.key)
            ordered.append((picked, "locale_coverage_zh_TW"))

    for candidate in _round_robin_candidates(candidates, used):
        if len(ordered) >= limit:
            break
        ordered.append((candidate, "persona_topic_round_robin"))

    jobs: list[RenderJob] = []
    for idx, (candidate, reason) in enumerate(ordered[:limit], start=1):
        locale = locales[0]
        if reason == "locale_coverage_zh_TW" and "zh-TW" in locales:
            locale = "zh-TW"
        elif idx % 13 == 0 and len(locales) > 1:
            for loc in locales[1:]:
                if loc in candidate.locales:
                    locale = loc
                    break
        runtime = _runtime_for(candidate, idx)
        jobs.append(
            RenderJob(
                candidate=candidate,
                locale=locale,
                seed=f"{seed_prefix}_{idx:04d}",
                runtime_format=runtime,
                sample_reason=reason,
            )
        )
    return jobs


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_inventory(out_root: Path, candidates: list[ArcCandidate]) -> None:
    rows = []
    for c in candidates:
        row = asdict(c)
        row["locales"] = ",".join(c.locales)
        rows.append(row)
    _write_json(out_root / "candidate_inventory.json", rows)
    _write_tsv(
        out_root / "candidate_inventory.tsv",
        rows,
        [
            "persona",
            "topic",
            "engine",
            "structural_format",
            "arc_path",
            "atom_file_count",
            "atom_slot_count",
            "story_bank_count",
            "locale_count",
            "locales",
        ],
    )


def _interesting_lines(text: str, *, max_lines: int = 240) -> list[str]:
    pattern = re.compile(
        r"(warn|warning|error|fail|failed|blocked|reject|hold|traceback|exception|gate|skipped)",
        re.IGNORECASE,
    )
    lines = []
    for line in text.splitlines():
        if pattern.search(line):
            cleaned = line.strip()
            if len(cleaned) > 700:
                cleaned = cleaned[:697] + "..."
            lines.append(cleaned)
    if len(lines) > max_lines:
        return lines[: max_lines // 2] + ["..."] + lines[-max_lines // 2 :]
    return lines


def _tail(text: str, *, max_lines: int = 60) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "UNREADABLE", "reason": str(exc)}


def _status_of(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("status", "overall_status", "release_band", "grade", "verdict"):
            value = payload.get(key)
            if value is not None:
                return str(value)
    return "MISSING"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _chapter_count(text: str) -> int:
    hits = re.findall(r"(?m)^\s*(?:##\s*)?Chapter\s+\d+\b", text)
    return len(hits)


def _cjk_ratio(text: str) -> tuple[int, float]:
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    letters = len(re.findall(r"[A-Za-z\u3400-\u9fff]", text))
    return cjk, (cjk / letters if letters else 0.0)


def _copy_reports(render_dir: Path, compact_dir: Path) -> dict[str, str]:
    copied: dict[str, str] = {}
    reports_dir = compact_dir / "reports"
    for name in REPORT_NAMES:
        src = render_dir / name
        if src.exists():
            reports_dir.mkdir(parents=True, exist_ok=True)
            dst = reports_dir / name
            shutil.copy2(src, dst)
            copied[name] = str(dst)
    return copied


def _scrub_render_text(render_dir: Path) -> list[str]:
    scrubbed = []
    for pattern in ("book.txt", "golden_chapter*.txt", "*.epub", "*.pdf", "*.docx"):
        for path in render_dir.glob(pattern):
            if path.is_file():
                scrubbed.append(str(path))
                path.unlink()
    return scrubbed


def _command_for(job: RenderJob, render_dir: Path, plan_path: Path) -> list[str]:
    return [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--topic",
        job.candidate.topic,
        "--persona",
        job.candidate.persona,
        "--arc",
        str(REPO_ROOT / job.candidate.arc_path),
        "--pipeline-mode",
        "spine",
        "--runtime-format",
        job.runtime_format,
        "--quality-profile",
        "production",
        "--exercise-journeys",
        "--no-job-check",
        "--render-book",
        "--render-dir",
        str(render_dir),
        "--out",
        str(plan_path),
        "--no-generate-freebies",
        "--no-update-freebie-index",
        "--locale",
        job.locale,
        "--seed",
        job.seed,
    ]


def _shell_join(cmd: list[str]) -> str:
    import shlex

    return " ".join(shlex.quote(part) for part in cmd)


def _free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024 ** 3)


def _summarize_reports(report_dir: Path) -> dict[str, Any]:
    loaded = {name: _load_json(report_dir / name) for name in REPORT_NAMES}
    summary: dict[str, Any] = {
        "report_statuses": {
            name: _status_of(payload)
            for name, payload in loaded.items()
            if payload is not None
        }
    }
    budget = loaded.get("budget.json")
    if isinstance(budget, dict):
        summary["budget_word_count"] = budget.get("word_count")
        summary["body_word_count"] = budget.get("body_word_count")
        summary["budget_chapter_count"] = budget.get("chapter_count")
    qsum = loaded.get("quality_summary.json")
    if isinstance(qsum, dict):
        summary["overall_status"] = qsum.get("overall_status")
        summary["quality_gate_failures"] = qsum.get("quality_gate_failures") or []
    book_quality = loaded.get("book_quality_report.json")
    if isinstance(book_quality, dict):
        summary["book_quality_release_band"] = book_quality.get("release_band") or book_quality.get("status")
        summary["book_quality_fail_reasons"] = book_quality.get("fail_reasons") or []
        summary["book_quality_hold_reasons"] = book_quality.get("hold_reasons") or []
    register = loaded.get("register_gate_report.json")
    if isinstance(register, dict):
        summary["register_failure_counts_by_id"] = register.get("failure_counts_by_id") or {}
        summary["register_verdict"] = register.get("verdict")
    book_pass = loaded.get("book_pass_report.json")
    if isinstance(book_pass, dict):
        summary["book_pass_failures"] = book_pass.get("failures") or []
    flow = loaded.get("chapter_flow_report.json")
    if isinstance(flow, dict):
        summary["chapter_flow_failed_chapters"] = flow.get("failed_chapters")
        summary["chapter_flow_chapter_count"] = flow.get("chapter_count")
    accent = loaded.get("rendered_accent_audit.json")
    if isinstance(accent, dict):
        accents = accent.get("accents") or []
        if isinstance(accents, list):
            summary["accent_count"] = len(accents)
            summary["accent_missing_from_manuscript"] = sum(
                1 for row in accents if isinstance(row, dict) and row.get("present_in_manuscript") is False
            )
    return summary


def classify_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    buckets: list[dict[str, Any]] = []
    stderr_blob = "\n".join(result.get("stderr_warnings_errors") or []) + "\n" + str(result.get("stderr_tail") or "")
    stdout_blob = "\n".join(result.get("stdout_warnings_errors") or []) + "\n" + str(result.get("stdout_tail") or "")
    combined = f"{stdout_blob}\n{stderr_blob}"
    statuses = result.get("report_statuses") or {}
    q_failures = set(result.get("quality_gate_failures") or [])
    reached_render_or_gates = bool(statuses) or result.get("delivered_word_count") is not None
    # A book that rendered to full length AND passed the book_quality gate did not
    # actually starve on atoms — per-slot "no enrichable content" style messages on
    # such a book are non-fatal enrichment fallbacks, not systemic depth failures.
    book_ok = bool(result.get("delivered_word_count")) and str(
        result.get("book_quality_release_band") or ""
    ).lower() in ("pass", "accept")

    def add(bucket: str, severity: str, evidence: str) -> None:
        if bucket not in BUCKETS:
            bucket = "schema/config"
        buckets.append({"bucket": bucket, "severity": severity, "evidence": evidence[:900]})

    rc = int(result.get("returncode", 0) or 0)
    if rc != 0:
        if re.search(r"POOL_TOO_SHALLOW|BAND_DEFICIT|NO_BINDING", combined):
            # Tuple viability preflight aborts BEFORE any render. This is a
            # "this specific tuple is not buildable" signal (skip it), NOT a
            # systemic schema or atom-depth failure of the pipeline. Classify it
            # as its own pre-render category so the pass-rate denominator stays
            # honest instead of inflating schema/config + atom_bank_depth.
            add("tuple_not_viable", "HIGH", "tuple viability preflight abort (pre-render): pool/band/binding deficit")
        elif "Tuple viability:" in combined:
            # Healthy tuple-viability summary line on a nonzero exit for some
            # other reason — do not classify off the bare prefix.
            pass
        elif re.search(r"CanonicalParseError|Malformed CANONICAL\.txt", combined):
            add("schema/config", "HIGH", "canonical atom parse/schema error")
        elif re.search(r"EnrichmentGapError|No enrichable content for slot|Add atoms upstream", combined):
            add("atom_bank_depth", "HIGH", "enrichment source gap raised before render")
        elif "[PRODUCTION GATE]" in combined:
            # Domain production gates intentionally exit nonzero; classify them
            # by their specific evidence below rather than as renderer crashes.
            pass
        elif re.search(r"Traceback|Exception|ModuleNotFoundError|ImportError|AttributeError|TypeError|ValueError", combined):
            add("renderer_exception", "HIGH", f"nonzero exit {rc}; exception-like output")
        elif "BLOCKED:" in combined or q_failures:
            # "BLOCKED" only means *some* production gate failed. The specific
            # gate (register_gate, chapter_flow, book_pass, book_quality,
            # exercise_journeys, enhancement_contract) is classified into its own
            # bucket by the handlers below — do NOT also attribute it to
            # editorial_quality, or a register-only block gets triple-counted.
            _specific = {"register_gate", "chapter_flow", "book_pass", "book_quality",
                         "exercise_journeys", "exercise_journey", "enhancement_contract"}
            _editorial_like = sorted(f for f in q_failures if f not in _specific)
            if _editorial_like:
                add("editorial_quality", "HIGH", f"production blocked by editorial gates: {_editorial_like}")
        else:
            add("renderer_exception", "HIGH", f"nonzero exit {rc} without complete gate classification")

    if re.search(r"Exercise journey outcome mismatch", combined, re.I):
        add("exercise_journey_mismatch", "HIGH" if rc else "MEDIUM", "exercise journey outcome thresholds missed")
    if re.search(
        r"Accent planner anti-spam|Supported accent underfill|capability_gap.*no_supply_pool|no_supply_pool with budget",
        combined,
        re.I,
    ):
        add("enhancement_planning", "HIGH" if rc else "MEDIUM", "accent planner supply/capability production gate")
    if re.search(r"Malformed CANONICAL\.txt|CanonicalParseError|header present but no usable prose", combined, re.I):
        add("schema/config", "HIGH", "malformed CANONICAL atom shape")
    if not book_ok and re.search(r"No enrichable content for slot|Add atoms upstream|no usable prose|no ARC blocks parsed", combined, re.I):
        add("atom_bank_depth", "HIGH" if rc else "MEDIUM", "no usable/enrichable atom prose for selected slot")
    # NOTE: the registry/auto-plan fallback signals ("Book planning layer: no
    # pre-authored plan", "Content bank registry unavailable", "DEFECT4:
    # dropping registry section") are the NORMAL path when a tuple has no
    # pre-authored book plan — the pipeline auto-plans from atoms and renders to
    # full length (verified: books emitting these hit book_quality PASS). They
    # are intentionally NOT classified as schema/config failures. Real schema
    # problems are caught by the canonical-parse and compatibility regexes.

    if not book_ok and re.search(r"Content gaps|under-length|thin-pool|word floor|word_budget", combined, re.I):
        # NOTE: "supported accent underfill" / bare "underfill" were removed here —
        # those are the accent/enhancement planner gate (classified as
        # enhancement_planning above), not an atom-depth signal. Keeping them here
        # double-counted every accent-underfill book as atom_bank_depth too.
        add("atom_bank_depth", "HIGH" if rc else "MEDIUM", "thin pool / underfill / word-budget signal in stderr")
    if re.search(r"Missing prose|STORY bank|story pool|no proseful|CONTENT GAP", combined, re.I):
        add("missing_story_pool", "HIGH", "missing prose/story/content-gap signal")
    # POOL_TOO_SHALLOW / BAND_DEFICIT are pre-render viability aborts and are
    # classified as tuple_not_viable above; do not also count them as a
    # systemic atom_bank_depth failure of books that actually rendered.
    if re.search(
        r"Capability check failed|Arc/format|unsupported|blocked under V4 freeze|"
        r"Book planning layer: FAIL|validation failed|input file not found|arc file not found",
        combined,
        re.I,
    ):
        # NOTE: bare "Tuple viability:" and "NO_BINDING" were removed here — the
        # first matches the healthy summary line on every book, and NO_BINDING is
        # a pre-render viability abort (tuple_not_viable), not a schema failure.
        add("schema/config", "HIGH" if rc else "MEDIUM", "schema/config/compatibility signal in CLI output")
    if re.search(r"EXERCISE-BANK|exercise.*fallback|exercise.*dropped|practice_library", combined, re.I):
        # NOTE: bare "F7" was removed here — F7 is a register-gate failure id and
        # its counts appear in register output, which falsely tagged every
        # register-F7 book as an exercise-journey mismatch. Genuine exercise
        # mismatches are caught by the "Exercise journey outcome mismatch" regex.
        add("exercise_journey_mismatch", "HIGH" if rc else "MEDIUM", "exercise journey or strict canonical signal")
    if re.search(
        r"usage:|unrecognized arguments|argparse|Error: .*--|"
        r"--pipeline-mode registry is legacy|quality-profile .*invalid",
        combined,
        re.I,
    ):
        add("CLI/config ergonomics", "LOW", "CLI warning/ergonomic signal")

    if statuses.get("chapter_flow_report.json") not in (None, "PASS"):
        add("chapter_flow", "HIGH", f"chapter_flow_report status={statuses.get('chapter_flow_report.json')}")
    if "chapter_flow" in q_failures:
        add("chapter_flow", "HIGH", "quality_summary blocks on chapter_flow")

    reg_status = statuses.get("register_gate_report.json")
    reg_counts = result.get("register_failure_counts_by_id") or {}
    if reg_status and reg_status not in ("PASS", "ADVISORY"):
        add("register_gate", "HIGH" if reg_status == "FAIL" else "MEDIUM", f"register status={reg_status}, counts={reg_counts}")
    if any(str(k).upper() in {"F1", "F6"} and int(v or 0) > 0 for k, v in reg_counts.items()):
        add("selected_content_repetition", "MEDIUM", f"register repetition/cadence counts={reg_counts}")

    book_pass_failures = set(result.get("book_pass_failures") or [])
    if statuses.get("book_pass_report.json") == "FAIL" or "book_pass" in q_failures:
        if "word_budget" in book_pass_failures:
            add("atom_bank_depth", "HIGH", "book_pass word_budget failed")
        if book_pass_failures & {"angle_journey_coherence", "callback_completion", "identity_stages", "band_distribution"}:
            add("transformation_arc", "HIGH", f"book_pass failures={sorted(book_pass_failures)}")
        if not book_pass_failures:
            add("transformation_arc", "HIGH", "book_pass failed")

    transform_status = statuses.get("transformation_heatmap.json")
    if transform_status and transform_status not in ("PASS",):
        add("transformation_arc", "MEDIUM" if transform_status == "WARN" else "HIGH", f"transformation_heatmap status={transform_status}")

    editorial_status = statuses.get("editorial_report.json")
    if editorial_status and editorial_status not in ("PASS",):
        add("editorial_quality", "MEDIUM" if editorial_status in {"WARN", "NEEDS_REVISION"} else "HIGH", f"editorial status={editorial_status}")

    bq_band = result.get("book_quality_release_band") or statuses.get("book_quality_report.json")
    if bq_band and bq_band not in ("Pass", "PASS", "Accept", "MISSING"):
        add("editorial_quality", "HIGH" if str(bq_band).lower() in {"reject", "fail"} else "MEDIUM", f"book_quality release_band/status={bq_band}")
    bq_reasons = " ".join(map(str, (result.get("book_quality_fail_reasons") or []) + (result.get("book_quality_hold_reasons") or [])))
    if re.search(r"repeat|duplicate|recurr|similar|overlap|scene anchor", bq_reasons, re.I):
        add("selected_content_repetition", "MEDIUM", bq_reasons)

    # NOTE: quality_summary.json is an AGGREGATE of the hard gates (register,
    # chapter_flow, book_pass, book_quality, ...). Its FAIL merely mirrors
    # whichever specific gate failed, which is already classified into its own
    # bucket above. Mapping the aggregate to editorial_quality double-counted the
    # real failure (e.g. a register-only block also showed as editorial_quality).
    # editorial_quality is now driven only by editorial_report.json /
    # book_quality release_band below.

    if reached_render_or_gates and "enhancement_contract.json" not in statuses:
        add("enhancement_planning", "MEDIUM", "enhancement_contract.json was not emitted")
    enhancement_status = statuses.get("enhancement_contract.json")
    if enhancement_status and enhancement_status not in ("PASS", "Pass", "MISSING"):
        add("enhancement_planning", "HIGH" if enhancement_status == "FAIL" else "MEDIUM", f"enhancement_contract status={enhancement_status}")
    if reached_render_or_gates and "rendered_accent_audit.json" not in statuses:
        add("enhancement_rendering", "MEDIUM", "rendered_accent_audit.json was not emitted")
    missing_accents = int(result.get("accent_missing_from_manuscript") or 0)
    if missing_accents:
        add("enhancement_rendering", "MEDIUM", f"{missing_accents} planned accents marked absent from manuscript")

    if reached_render_or_gates and result.get("locale") != "en-US":
        cjk_count = int(result.get("cjk_char_count") or 0)
        cjk_ratio = float(result.get("cjk_ratio") or 0.0)
        if result.get("locale") in {"zh-TW", "zh-CN", "zh-HK", "zh-SG", "ja-JP"} and (cjk_count < 100 or cjk_ratio < 0.05):
            add("locale_fallback", "HIGH", f"{result.get('locale')} render has low CJK signal: chars={cjk_count}, ratio={cjk_ratio:.4f}")
        if re.search(r"locale.*skipped|fallback|localize", combined, re.I):
            add("locale_fallback", "MEDIUM", "locale fallback/localization warning in output")

    if "scene_anchor_density_report.json" in statuses and statuses.get("scene_anchor_density_report.json") != "PASS":
        add("selected_content_repetition", "MEDIUM", f"scene_anchor_density status={statuses.get('scene_anchor_density_report.json')}")
    if re.search(r"dedupe|recurrence|repeated|duplicate|similarity|ngram", combined, re.I):
        add("selected_content_repetition", "LOW", "dedupe/repetition signal in output")

    # De-duplicate bucket entries while preserving the strongest severity.
    sev_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    merged: dict[str, dict[str, Any]] = {}
    for entry in buckets:
        bucket = entry["bucket"]
        existing = merged.get(bucket)
        if existing is None or sev_rank.get(entry["severity"], 0) > sev_rank.get(existing["severity"], 0):
            merged[bucket] = dict(entry)
        elif existing is not None and entry["evidence"] not in existing["evidence"]:
            existing["evidence"] = (existing["evidence"] + " | " + entry["evidence"])[:900]
    return list(merged.values())


FIX_MAP = {
    "atom_bank_depth": (
        "atoms/<persona>/<topic>/*/CANONICAL.txt; phoenix_v4/planning/enrichment_select.py depth budget",
        "Add proseful, thesis-specific atoms in the underfilled slots and keep the spine word-floor padder disabled; fix depth/source shape instead of padding.",
    ),
    "missing_story_pool": (
        "atoms/<persona>/<topic>/STORY and atoms/<persona>/<topic>/<engine>",
        "Backfill story/engine pools with proseful entries and add a preflight that fails before render when a chosen arc has no usable story supply.",
    ),
    "schema/config": (
        "config/source_of_truth/master_arcs; config/format_selection; book_structure_plan/spine configs",
        "Normalize arc/runtime compatibility and add a fast tuple preflight that reports config gaps without starting a full render.",
    ),
    "exercise_journey_mismatch": (
        "atoms/<persona>/<topic>/EXERCISE; phoenix_v4/planning/enrichment_select.py attach_exercise_journeys",
        "Backfill canonical EXERCISE atoms and align journey selectors with thesis/runtime contracts so production never falls through to generic practice pools.",
    ),
    "register_gate": (
        "phoenix_v4/rendering/register_output_strengthen.py; phoenix_v4/quality/register_gate.py",
        "Tune output strengthening and atom-bank phrasing to satisfy F-gates without weakening register thresholds.",
    ),
    "chapter_flow": (
        "phoenix_v4/rendering/book_renderer.py flow cues; phoenix_v4/quality/chapter_flow_gate.py",
        "Strengthen chapter clear-point/transition realization and fix source-slot sequencing where chapters cannot form a coherent movement.",
    ),
    "transformation_arc": (
        "phoenix_v4/planning/angle_journey.py; phoenix_v4/quality/transformation_heatmap.py; arc YAML",
        "Repair angle/callback/stage propagation from master arc to enriched slots so the ending pays off the named transformation.",
    ),
    "editorial_quality": (
        "phoenix_v4/quality/book_quality_gate.py; phoenix_v4/qa/editorial_report.py; atom banks",
        "Improve rendered chapter substance, specificity, and thesis continuity at the source/render-strengthening layer while keeping production gates hard.",
    ),
    "enhancement_planning": (
        "phoenix_v4/planning/accent_planner.py; phoenix_v4/qa/enhancement_contract.py",
        "Make enhancement contracts mandatory, complete, and preflighted for every renderable tuple.",
    ),
    "enhancement_rendering": (
        "phoenix_v4/rendering/chapter_composer.py; rendered_accent_audit emission",
        "Close the planner-to-renderer gap so every planned accent has a rendered body and present_in_manuscript=true evidence.",
    ),
    "locale_fallback": (
        "atoms/*/*/*/locales/<locale>; phoenix_v4/rendering/locale_templates.py",
        "Backfill locale atoms/templates and add a locale-language ratio gate to catch silent English fallback on localized renders.",
    ),
    "selected_content_repetition": (
        "phoenix_v4/content_banks/selector.py; phoenix_v4/rendering/register_output_strengthen.py; atom phrasing",
        "Increase variant diversity and add selector memory/caps for repeated scene anchors, bridges, and cadence before register/book quality gates run.",
    ),
    "renderer_exception": (
        "scripts/run_pipeline.py and immediate traceback locus",
        "Fix the thrown exception and add a unit/CLI regression around the exact tuple command.",
    ),
    "CLI/config ergonomics": (
        "scripts/run_pipeline.py CLI and docs/canonical invocation",
        "Make production render options self-validating with actionable messages and fewer contradictory freeze/runtime hints.",
    ),
}


def build_backlog(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_bucket: dict[str, dict[str, Any]] = {}
    sev_score = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    for result in results:
        for issue in result.get("issues") or []:
            bucket = issue["bucket"]
            entry = by_bucket.setdefault(
                bucket,
                {
                    "bucket": bucket,
                    "frequency": 0,
                    "max_severity": "LOW",
                    "affected_tuples": [],
                    "evidence": [],
                },
            )
            entry["frequency"] += 1
            if sev_score[issue["severity"]] > sev_score[entry["max_severity"]]:
                entry["max_severity"] = issue["severity"]
            label = result.get("tuple_label") or result.get("run_id")
            if label not in entry["affected_tuples"] and len(entry["affected_tuples"]) < 30:
                entry["affected_tuples"].append(label)
            if issue.get("evidence") and len(entry["evidence"]) < 8:
                entry["evidence"].append(issue["evidence"])
    total = max(1, len(results))
    backlog = []
    for bucket, entry in by_bucket.items():
        locus, fix = FIX_MAP.get(bucket, ("unknown", "Investigate and add a narrow regression."))
        entry["frequency_pct"] = round(entry["frequency"] / total, 4)
        entry["likely_code_content_config_locus"] = locus
        entry["recommended_fix"] = fix
        entry["one_fix_helps_many_books"] = entry["frequency"] > 1
        backlog.append(entry)
    backlog.sort(key=lambda e: (sev_score[e["max_severity"]], e["frequency"]), reverse=True)
    return backlog


def build_regression_set(results: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    rows = []
    seen_buckets: set[str] = set()
    used_tuples: set[str] = set()
    failing = [r for r in results if r.get("issues")]
    failing.sort(key=lambda r: (-len(r.get("issues") or []), r.get("run_id", "")))

    def add_result(result: dict[str, Any]) -> bool:
        if len(rows) >= limit:
            return False
        tuple_label = result.get("tuple_label")
        if tuple_label in used_tuples:
            return False
        buckets = [i["bucket"] for i in result.get("issues") or []]
        used_tuples.add(str(tuple_label))
        seen_buckets.update(buckets)
        rows.append(
            {
                "tuple": tuple_label,
                "buckets": ",".join(buckets),
                "command": result.get("command"),
                "expected_gate_outcome_after_fixes": (
                    "production command exits 0; implicated reports move to PASS/Accept; "
                    "no WARN/FAIL remains for these buckets"
                ),
            }
        )
        return True

    for result in failing:
        if result.get("locale") != "en-US":
            add_result(result)
            break
    for result in failing:
        if result.get("sample_reason") == "high_risk_known_tuple":
            add_result(result)

    for result in failing:
        buckets = [i["bucket"] for i in result.get("issues") or []]
        if not any(b not in seen_buckets for b in buckets) and len(rows) >= min(limit, len(failing)):
            continue
        add_result(result)
        if len(rows) >= limit:
            return rows
    for result in results:
        if len(rows) >= limit:
            break
        if result.get("tuple_label") in used_tuples:
            continue
        rows.append(
            {
                "tuple": result.get("tuple_label"),
                "buckets": ",".join(i["bucket"] for i in result.get("issues") or []) or "none_observed",
                "command": result.get("command"),
                "expected_gate_outcome_after_fixes": "production command exits 0 and all required gate reports are PASS/Accept",
            }
        )
    return rows[:limit]


def load_existing_results(out_root: Path) -> dict[str, dict[str, Any]]:
    path = out_root / "results.jsonl"
    existing: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return existing
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        run_id = str(row.get("run_id") or "")
        if run_id:
            row["issues"] = classify_result(row)
            existing[run_id] = row
    return existing


def append_result(out_root: Path, result: dict[str, Any]) -> None:
    path = out_root / "results.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")


def run_job(
    job: RenderJob,
    *,
    out_root: Path,
    work_root: Path,
    timeout: int,
    keep_raw_renders: bool,
) -> dict[str, Any]:
    compact_dir = out_root / "renders" / job.run_id
    render_dir = work_root / job.run_id
    plan_path = compact_dir / "plan.json"
    compact_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    cmd = _command_for(job, render_dir, plan_path)
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        stderr = (stderr or "") + f"\nTIMEOUT after {timeout}s"
    elapsed = round(time.time() - started, 3)

    book_path = render_dir / "book.txt"
    delivered_word_count = None
    delivered_chapter_count = None
    cjk_count = 0
    cjk_ratio = 0.0
    if book_path.exists():
        text = book_path.read_text(encoding="utf-8", errors="replace")
        delivered_word_count = _word_count(text)
        delivered_chapter_count = _chapter_count(text)
        cjk_count, cjk_ratio = _cjk_ratio(text)

    copied = _copy_reports(render_dir, compact_dir)
    report_summary = _summarize_reports(compact_dir / "reports")
    scrubbed = _scrub_render_text(render_dir)
    if not keep_raw_renders:
        shutil.rmtree(render_dir, ignore_errors=True)

    result = {
        "run_id": job.run_id,
        "tuple_label": job.tuple_label(),
        "persona": job.candidate.persona,
        "topic": job.candidate.topic,
        "engine": job.candidate.engine,
        "arc": job.candidate.arc_path,
        "structural_format": job.candidate.structural_format,
        "locale": job.locale,
        "seed": job.seed,
        "runtime_format": job.runtime_format,
        "sample_reason": job.sample_reason,
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "command": _shell_join(cmd),
        "reports_copied": copied,
        "delivered_word_count": delivered_word_count,
        "delivered_chapter_count": delivered_chapter_count,
        "cjk_char_count": cjk_count,
        "cjk_ratio": round(cjk_ratio, 5),
        "stdout_warnings_errors": _interesting_lines(stdout),
        "stderr_warnings_errors": _interesting_lines(stderr),
        "stdout_tail": _tail(stdout),
        "stderr_tail": _tail(stderr),
        "scrubbed_render_text_paths": scrubbed,
        "compact_dir": str(compact_dir),
        **report_summary,
    }
    result["issues"] = classify_result(result)
    _write_json(compact_dir / "result.json", result)
    return result


def write_summaries(out_root: Path, results: list[dict[str, Any]], *, early_stop: dict[str, Any] | None) -> None:
    for result in results:
        result["issues"] = classify_result(result)
        compact_dir = Path(str(result.get("compact_dir") or out_root / "renders" / str(result.get("run_id") or "")))
        if compact_dir.name:
            _write_json(compact_dir / "result.json", result)
    with (out_root / "results.jsonl").open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")

    backlog = build_backlog(results)
    regression = build_regression_set(results)
    bucket_counts: dict[str, int] = {}
    passed_all = 0
    failed_or_warned = 0
    for result in results:
        issue_buckets = {issue["bucket"] for issue in result.get("issues") or []}
        for bucket in issue_buckets:
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        if result.get("returncode") == 0 and not result.get("issues"):
            passed_all += 1
        else:
            failed_or_warned += 1
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_root": str(out_root),
        "renders_attempted": len(results),
        "renders_passed_all_gates": passed_all,
        "renders_failed_or_warned": failed_or_warned,
        "bucket_counts": bucket_counts,
        "systemic_backlog": backlog,
        "representative_regression_tuples": regression,
        "early_stop": early_stop,
    }
    _write_json(out_root / "summary.json", summary)
    _write_json(out_root / "systemic_backlog.json", backlog)
    _write_json(out_root / "regression_set.json", regression)
    _write_tsv(
        out_root / "summary.tsv",
        [
            {
                "renders_attempted": len(results),
                "renders_passed_all_gates": passed_all,
                "renders_failed_or_warned": failed_or_warned,
                "bucket": bucket,
                "count": count,
                "pct": round(count / max(1, len(results)), 4),
            }
            for bucket, count in sorted(bucket_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        ["renders_attempted", "renders_passed_all_gates", "renders_failed_or_warned", "bucket", "count", "pct"],
    )
    failure_rows = []
    for result in results:
        for issue in result.get("issues") or []:
            failure_rows.append(
                {
                    "run_id": result.get("run_id"),
                    "tuple": result.get("tuple_label"),
                    "bucket": issue.get("bucket"),
                    "severity": issue.get("severity"),
                    "evidence": issue.get("evidence"),
                    "command": result.get("command"),
                }
            )
    _write_tsv(
        out_root / "failures.tsv",
        failure_rows,
        ["run_id", "tuple", "bucket", "severity", "evidence", "command"],
    )
    _write_tsv(
        out_root / "regression_set.tsv",
        regression,
        ["tuple", "buckets", "command", "expected_gate_outcome_after_fixes"],
    )


def systemic_stop(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    if len(results) < 5:
        return None
    counts: dict[str, int] = {}
    for result in results:
        for bucket in {issue["bucket"] for issue in result.get("issues") or []}:
            counts[bucket] = counts.get(bucket, 0) + 1
    for bucket, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        pct = count / len(results)
        if pct > 0.20:
            return {
                "reason": "systemic_failure_over_20pct",
                "bucket": bucket,
                "count": count,
                "attempted": len(results),
                "pct": round(pct, 4),
            }
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Stress audit Pearl Prime book renders.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum total candidate renders to attempt.")
    parser.add_argument(
        "--locale",
        default="en-US",
        help="Locale or comma-separated locales to sample. First locale is default; include zh-TW for one localized render.",
    )
    parser.add_argument("--seed-prefix", default="book_stress", help="Deterministic seed prefix.")
    parser.add_argument(
        "--out",
        default=None,
        help="Compact artifact root. Defaults to /tmp/pearl_book_stress_<timestamp>.",
    )
    parser.add_argument("--timeout", type=int, default=900, help="Per-render timeout in seconds.")
    parser.add_argument("--min-free-gb", type=float, default=5.0, help="Stop before render if /tmp free space drops below this.")
    parser.add_argument("--keep-raw-renders", action="store_true", help="Keep raw render dirs after scrubbing manuscript files.")
    parser.add_argument("--no-stop-on-systemic", action="store_true", help="Do not stop when a bucket exceeds 20%% of attempted renders.")
    args = parser.parse_args()

    if args.limit <= 0:
        parser.error("--limit must be positive")
    locales = [loc.strip() for loc in str(args.locale).split(",") if loc.strip()]
    if not locales:
        locales = ["en-US"]
    if "en-US" not in locales:
        locales.insert(0, "en-US")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = Path(args.out) if args.out else Path(tempfile.gettempdir()) / f"pearl_book_stress_{timestamp}"
    out_root = out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    work_root = (out_root / "_render_work").resolve()
    work_root.mkdir(parents=True, exist_ok=True)

    candidates = build_inventory()
    write_inventory(out_root, candidates)
    jobs = build_jobs(candidates, limit=args.limit, locales=locales, seed_prefix=args.seed_prefix)
    _write_json(
        out_root / "job_plan.json",
        [
            {
                "run_id": job.run_id,
                "tuple": job.tuple_label(),
                "sample_reason": job.sample_reason,
                "command": _shell_join(_command_for(job, work_root / job.run_id, out_root / "renders" / job.run_id / "plan.json")),
            }
            for job in jobs
        ],
    )

    existing = load_existing_results(out_root)
    results = list(existing.values())
    early_stop = systemic_stop(results) if not args.no_stop_on_systemic else None
    for idx, job in enumerate(jobs, start=1):
        if early_stop:
            break
        if job.run_id in existing:
            print(f"[{idx}/{len(jobs)}] skip existing {job.run_id}")
            continue
        free_gb = _free_gb(Path(tempfile.gettempdir()))
        if free_gb < args.min_free_gb:
            early_stop = {
                "reason": "disk_free_below_threshold",
                "free_gb": round(free_gb, 3),
                "threshold_gb": args.min_free_gb,
                "attempted": len(results),
            }
            break
        print(f"[{idx}/{len(jobs)}] render {job.tuple_label()} free_gb={free_gb:.1f}")
        result = run_job(
            job,
            out_root=out_root,
            work_root=work_root,
            timeout=args.timeout,
            keep_raw_renders=args.keep_raw_renders,
        )
        append_result(out_root, result)
        existing[job.run_id] = result
        results.append(result)
        print(
            f"    rc={result['returncode']} elapsed={result['elapsed_seconds']}s "
            f"issues={','.join(i['bucket'] for i in result.get('issues') or []) or 'none'}"
        )
        if not args.no_stop_on_systemic:
            early_stop = systemic_stop(results)

    if not args.keep_raw_renders:
        shutil.rmtree(work_root, ignore_errors=True)
    results = list(load_existing_results(out_root).values())
    write_summaries(out_root, results, early_stop=early_stop)
    print(f"artifact_root={out_root}")
    if early_stop:
        print(f"early_stop={json.dumps(early_stop, ensure_ascii=False)}")
    return 0 if not early_stop or early_stop.get("reason") == "systemic_failure_over_20pct" else 2


if __name__ == "__main__":
    raise SystemExit(main())

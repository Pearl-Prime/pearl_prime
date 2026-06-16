"""Shared helpers for full-stack Book 3 integration renders."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_PIPELINE = REPO_ROOT / "scripts" / "run_pipeline.py"

# Cross-persona contamination markers (OPD-118 decoy personas).
CROSS_PERSONA_MARKERS = ("fire_station", "trading_floor", "executive_reorg")

# Within-slot / cross-stream bridge signatures (OPD-109 / OPD-112).
BRIDGE_SIGNATURE_PHRASES = (
    "Behind that observation",
    "Watch how the same shape",
    "Another version of this turn",
    "The same pattern shows up",
    "What this means is",
)

# F2 broken wrapper fragment (OPD-20260518-002).
F2_BROKEN_FRAGMENT = "keeps pointing toward is."

GATE_REPORT_FILES = (
    "book_pass_report.json",
    "book_quality_report.json",
    "chapter_flow_report.json",
    "scene_anchor_density_report.json",
)


def render_book(
    *,
    out_dir: Path,
    topic: str = "anxiety",
    persona: str = "gen_z_professionals",
    teacher: str = "ahjan",
    arc: str | None = None,
    angle: str = "PROTECTIVE_ALARM",
    runtime_format: str = "deep_book_6h",
    quality_profile: str = "production",
    seed: str = "integration_book3_full_stack",
    timeout_sec: int = 7200,
) -> subprocess.CompletedProcess[str]:
    """Run scripts/run_pipeline.py spine render; return CompletedProcess."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    arc_path = arc or (
        "config/source_of_truth/master_arcs/"
        "gen_z_professionals__anxiety__spiral__F006.yaml"
    )
    plan_path = out_dir / "plan.json"
    cmd = [
        sys.executable,
        str(RUN_PIPELINE),
        "--topic",
        topic,
        "--persona",
        persona,
        "--teacher",
        teacher,
        "--angle",
        angle,
        "--arc",
        arc_path,
        "--pipeline-mode",
        "spine",
        "--runtime-format",
        runtime_format,
        "--render-book",
        "--render-dir",
        str(out_dir),
        "--out",
        str(plan_path),
        "--quality-profile",
        quality_profile,
        "--seed",
        seed,
        "--no-generate-freebies",
        "--no-update-freebie-index",
        "--no-job-check",
    ]
    run_env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env=run_env,
        check=False,
    )


def parse_audit(out_dir: Path) -> dict[str, Any]:
    """Load enrichment_audit and gate reports from a render directory."""
    out_dir = Path(out_dir)
    result: dict[str, Any] = {"render_dir": str(out_dir)}

    audit_path = out_dir / "enrichment_audit.json"
    if audit_path.exists():
        result["enrichment_audit"] = json.loads(audit_path.read_text(encoding="utf-8"))
    else:
        result["enrichment_audit"] = {}

    for name in GATE_REPORT_FILES:
        path = out_dir / name
        if path.exists():
            result[name.replace(".json", "")] = json.loads(
                path.read_text(encoding="utf-8")
            )

    qs_path = out_dir / "quality_summary.json"
    if qs_path.exists():
        result["quality_summary"] = json.loads(qs_path.read_text(encoding="utf-8"))

    book_path = out_dir / "book.txt"
    if book_path.exists():
        result["book_txt"] = book_path.read_text(encoding="utf-8")
        result["word_count"] = len(result["book_txt"].split())

    return result


def count_pattern(text: str, pattern: str, *, flags: int = re.IGNORECASE) -> int:
    """Return occurrence count of regex pattern in text."""
    return len(re.findall(pattern, text, flags=flags))


def gate_status(payload: dict[str, Any] | None) -> str:
    if not payload:
        return "MISSING"
    return str(payload.get("status") or "UNKNOWN").upper()


def verbatim_gate_reports(parsed: dict[str, Any]) -> str:
    """Format gate JSON for failure messages."""
    chunks: list[str] = []
    for key in (
        "book_pass_report",
        "book_quality_report",
        "chapter_flow_report",
        "scene_anchor_density_report",
        "quality_summary",
    ):
        if key in parsed:
            chunks.append(f"=== {key} ===\n{json.dumps(parsed[key], indent=2)}")
    return "\n\n".join(chunks)


def persona_pool_source_ids(enrichment_audit: dict[str, Any]) -> list[dict[str, Any]]:
    """Return section_packet_audit rows sourced from persona_atom."""
    spa = enrichment_audit.get("section_packet_audit") or []
    return [row for row in spa if str(row.get("source") or "") == "persona_atom"]


def allowed_persona_atom_ids(persona: str, topic: str, repo_root: Path | None = None) -> set[str]:
    """Collect atom_id headers from atoms/{persona}/{topic}/ CANONICAL files."""
    root = repo_root or REPO_ROOT
    persona_root = root / "atoms" / persona / topic
    ids: set[str] = set()
    if not persona_root.exists():
        return ids
    for canonical in persona_root.rglob("CANONICAL.txt"):
        try:
            text = canonical.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            if line.startswith("## "):
                ids.add(line[3:].strip())
    return ids


def top_repeated_phrase_count(book_txt: str, cap_ngrams: tuple[int, ...] = (4, 5, 6)) -> int:
    """Book-wide max n-gram count (mirrors book_quality_gate tokenization)."""
    from phoenix_v4.quality.book_quality_gate import _repeated_phrase_violations

    violations = _repeated_phrase_violations(book_txt)
    if not violations:
        words = re.findall(r"[a-z0-9']+", book_txt.lower())
        counts: dict[str, int] = {}
        for n in cap_ngrams:
            for i in range(0, max(0, len(words) - n + 1)):
                phrase = " ".join(words[i : i + n])
                counts[phrase] = counts.get(phrase, 0) + 1
        return max(counts.values()) if counts else 0
    return max(int(v.get("count") or 0) for v in violations)

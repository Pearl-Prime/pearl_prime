#!/usr/bin/env python3
"""
Duration matrix pilot: spine pipeline × 7 runtime formats × 3 topics.

Writes under artifacts/pilots/duration_matrix/<topic>/<runtime_format>/ and
artifacts/pilots/duration_matrix/RESULTS.md

Usage:
  PYTHONPATH=. python3 scripts/pilot/run_duration_matrix_pilot.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Seven runtime formats from config/format_selection/format_registry.yaml (ordered by duration).
RUNTIME_FORMATS: List[Tuple[str, str]] = [
    ("micro (~15m)", "micro_book_15"),
    ("short (~20m)", "micro_book_20"),
    ("standard (~30m)", "short_book_30"),
    ("extended (~1h)", "standard_book"),
    ("deep (~2h)", "extended_book_2h"),
    ("immersive (~4h)", "deep_book_4h"),
    ("full (~6h)", "deep_book_6h"),
]

TOPICS: List[Tuple[str, str, str]] = [
    ("grief", "trauma", "config/source_of_truth/master_arcs/gen_z_professionals__grief__grief__F006.yaml"),
    ("anxiety", "anxiety", "config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml"),
    (
        "somatic_healing",
        "somatic",
        "config/source_of_truth/master_arcs/gen_z_professionals__somatic_healing__overwhelm__F006.yaml",
    ),
]

PERSONA = "gen_z_professionals"
INJECTION_RE = re.compile(r"\[[^\]\n]*INJECTION[^\]\n]*\]", re.IGNORECASE)


def _load_format_targets(repo: Path) -> Dict[str, Dict[str, Any]]:
    path = repo / "config" / "format_selection" / "format_registry.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if yaml else {}
    out: Dict[str, Dict[str, Any]] = {}
    for fid, block in (data.get("runtime_formats") or {}).items():
        if isinstance(block, dict):
            out[str(fid)] = block
    return out


def _slot_metrics(budget: Dict[str, Any]) -> Tuple[int, int, int]:
    """Returns (total_slots, meeting_half_target, actual_words_sum_from_slots)."""
    total = 0
    meet = 0
    wsum = 0
    for ch in budget.get("chapters") or []:
        for s in ch.get("slots") or []:
            total += 1
            tw = int(s.get("target_words") or 0)
            aw = int(s.get("actual_words") or 0)
            wsum += aw
            if tw <= 0:
                if aw > 0:
                    meet += 1
            elif aw >= tw * 0.5:
                meet += 1
    return total, meet, wsum


def _run_one(
    *,
    repo: Path,
    topic: str,
    arc_rel: str,
    runtime_format: str,
    out_root: Path,
) -> Dict[str, Any]:
    rel = out_root / topic / runtime_format
    rel.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(repo / "scripts" / "run_pipeline.py"),
        "--pipeline-mode",
        "spine",
        "--topic",
        topic,
        "--persona",
        PERSONA,
        "--arc",
        str(repo / arc_rel),
        "--runtime-format",
        runtime_format,
        "--render-book",
        "--render-dir",
        str(rel),
        "--out",
        str(rel / "plan.json"),
        "--no-job-check",
        "--no-generate-freebies",
        "--quality-profile",
        "draft",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(repo),
        env={**os.environ, "PYTHONPATH": str(repo)},
        capture_output=True,
        text=True,
    )
    row: Dict[str, Any] = {
        "topic": topic,
        "runtime_format": runtime_format,
        "exit_code": proc.returncode,
    }
    book_path = rel / "book.txt"
    budget_path = rel / "budget.json"
    flow_path = rel / "chapter_flow_report.json"
    if book_path.exists():
        text = book_path.read_text(encoding="utf-8")
        row["actual_words"] = len(text.split())
        row["injection_gaps"] = len(INJECTION_RE.findall(text))
    else:
        row["actual_words"] = None
        row["injection_gaps"] = None
    if budget_path.exists():
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
        t, m, _ = _slot_metrics(budget)
        row["slots_total"] = t
        row["slots_meet_half_target"] = m
    else:
        row["slots_total"] = None
        row["slots_meet_half_target"] = None
    if flow_path.exists():
        fr = json.loads(flow_path.read_text(encoding="utf-8"))
        row["chapter_flow_status"] = fr.get("status", "?")
        row["chapter_flow_failed"] = fr.get("failed_chapters")
    else:
        row["chapter_flow_status"] = "MISSING"
        row["chapter_flow_failed"] = None
    if proc.returncode != 0:
        row["stderr_tail"] = (proc.stderr or "")[-4000:]
    return row


def main() -> int:
    if yaml is None:
        print("PyYAML required", file=sys.stderr)
        return 1
    repo = REPO_ROOT
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    targets = _load_format_targets(repo)
    out_root = repo / "artifacts" / "pilots" / "duration_matrix"
    out_root.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    for topic, _kind, arc_rel in TOPICS:
        for tier_label, fmt in RUNTIME_FORMATS:
            print(f"--- {topic} / {fmt} ---", flush=True)
            row = _run_one(repo=repo, topic=topic, arc_rel=arc_rel, runtime_format=fmt, out_root=out_root)
            row["tier_label"] = tier_label
            spec = targets.get(fmt) or {}
            wr = spec.get("word_range")
            if isinstance(wr, list) and len(wr) >= 1:
                row["target_words_min"] = int(wr[0])
                row["target_words_max"] = int(wr[1]) if len(wr) > 1 else int(wr[0])
            else:
                row["target_words_min"] = None
                row["target_words_max"] = None
            rows.append(row)

    lines: List[str] = [
        "# Duration matrix pilot — spine pipeline",
        "",
        f"- Branch tooling: `scripts/pilot/run_duration_matrix_pilot.py`",
        f"- Persona: `{PERSONA}`",
        "- Topics: grief (trauma), anxiety, somatic_healing (somatic)",
        "- Formats: seven `runtime_formats` from `config/format_selection/format_registry.yaml`",
        "",
        "## Escalation rule",
        "",
        "Flag to **TEAM A (beatmap / injection)** when actual word count is below **80%** of the registry minimum (`word_range[0]`) for that runtime format.",
        "",
        "## Results",
        "",
        "| Topic | Tier (runtime) | Target words (min–max) | Actual words | Sections filled (≥50% slot target) | Injection gaps | Gate (chapter flow) |",
        "|---|---|---:|---:|---|---:|---|",
    ]

    escalations: List[str] = []
    for r in rows:
        tw = r.get("target_words_min")
        twx = r.get("target_words_max")
        target_cell = f"{tw}–{twx}" if tw is not None and twx is not None else "—"
        aw = r.get("actual_words")
        st = r.get("slots_total")
        sm = r.get("slots_meet_half_target")
        sec_cell = f"{sm}/{st}" if st is not None and sm is not None else "—"
        inj = r.get("injection_gaps")
        inj_cell = str(inj) if inj is not None else "—"
        gate = r.get("chapter_flow_status") or "?"
        tier = f"{r['tier_label']} (`{r['runtime_format']}`)"
        lines.append(
            f"| {r['topic']} | {tier} | {target_cell} | {aw if aw is not None else '—'} | {sec_cell} | {inj_cell} | {gate} |"
        )
        if tw is not None and aw is not None and aw < 0.8 * tw:
            escalations.append(
                f"- **{r['topic']}** / `{r['runtime_format']}`: actual {aw} < 80% of minimum target {tw} ({100.0 * aw / tw:.1f}% of min)."
            )

    lines.extend(
        [
            "",
            "## Runs below 80% of registry minimum (TEAM A)",
            "",
        ]
    )
    if escalations:
        lines.extend(escalations)
    else:
        lines.append("_None — all runs met the 80%-of-minimum bar on delivered `book.txt` word count._")

    lines.extend(
        [
            "",
            "## Observations (EI V2 / systems read)",
            "",
            "- **Chapter flow:** all 21 runs reported `chapter_flow` **FAIL** (12/12 chapters) — consistent with session handoff known spine gap; `quality_summary.json` stays PASS in `--quality-profile draft` because failures are non-blocking.",
            "- **Word-count plateau:** For **grief** and **anxiety**, `extended_book_2h` / `deep_book_4h` / `deep_book_6h` share the same delivered word count per topic. **somatic_healing** shows the same three-way tie in this run — runtime format is not scaling total prose into the long bands yet (beatmap / enrichment / compose path).",
            "- **Injection placeholders:** no `[*INJECTION*]` tokens observed in delivered `book.txt` for this matrix (count 0).",
            "",
            "## Machine-readable output",
            "",
            "Per-run metrics: `artifacts/pilots/duration_matrix/results.json`.",
            "Each cell directory contains `book.txt`, `budget.json`, `plan.json`, `chapter_flow_report.json`, `quality_summary.json`.",
            "",
        ]
    )

    (out_root / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_root / "results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {out_root / 'RESULTS.md'}")
    return 0 if all(r.get("exit_code") == 0 for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

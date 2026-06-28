#!/usr/bin/env python3
"""
Duration × topic bestseller + cohesion QA matrix (local, production profile).

Builds one book per runtime_format (with word_range), sweeps all canonical topics
at standard_book_60min, extracts honest gate verdicts, writes EPUBs for duration
tier QA, and opens artifacts/qa/ in Finder (macOS).

Usage:
  PYTHONPATH=. python3 scripts/qa/run_duration_topic_matrix_qa.py
  PYTHONPATH=. python3 scripts/qa/run_duration_topic_matrix_qa.py --skip-build  # report only
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None

PERSONA = "corporate_managers"
QA_ROOT = REPO_ROOT / "artifacts" / "qa"
DURATION_SWEEP_DIR = QA_ROOT / "duration_sweep"
TOPIC_SWEEP_DIR = QA_ROOT / "topic_sweep_60min"


def _load_yaml(path: Path) -> dict:
    if not path.exists() or not yaml:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def enumerate_durations() -> list[dict[str, Any]]:
    reg = _load_yaml(REPO_ROOT / "config" / "format_selection" / "format_registry.yaml")
    out: list[dict[str, Any]] = []
    for fmt_id, block in (reg.get("runtime_formats") or {}).items():
        if not isinstance(block, dict):
            continue
        wr = block.get("word_range")
        if not wr or not isinstance(wr, list) or len(wr) < 2:
            continue
        out.append(
            {
                "id": fmt_id,
                "word_range": [int(wr[0]), int(wr[1])],
                "chapter_count": block.get("chapter_count_default"),
            }
        )
    out.sort(key=lambda x: x["word_range"][0])
    return out


def enumerate_topics() -> list[str]:
    cfg = _load_yaml(REPO_ROOT / "config" / "catalog" / "catalog_generation_config.yaml")
    return list(cfg.get("topics") or [])


def arc_for_topic(topic: str) -> Path | None:
    """Pick a buildable arc — prefer engines with atom bindings (overwhelm first)."""
    arcs_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
    matches = list(arcs_dir.glob(f"{PERSONA}__{topic}__*.yaml"))
    if not matches:
        return None
    bindings = _load_yaml(REPO_ROOT / "config" / "topic_engine_bindings.yaml")
    topic_cfg = bindings.get(topic) if isinstance(bindings.get(topic), dict) else {}
    allowed = topic_cfg.get("allowed_engines") or []
    preferred = [e for e in ("overwhelm", "grief", "false_alarm", "shame", "spiral", "watcher") if e in allowed]
    preferred += [e for e in allowed if e not in preferred]

    def _engine_from_path(p: Path) -> str:
        # corporate_managers__topic__engine__F006.yaml
        parts = p.stem.split("__")
        return parts[2] if len(parts) >= 3 else ""

    for eng in preferred:
        for p in matches:
            if _engine_from_path(p) == eng:
                return p
    # Fallback: any arc whose engine appears in allowed_engines
    for p in sorted(matches):
        if _engine_from_path(p) in allowed:
            return p
    return sorted(matches)[0]


def _cohesion_verdict(register_report: dict, ei_report: dict) -> tuple[str, list[str]]:
    """Integration/dwell + adjacency cohesion — honest operator bar."""
    issues: list[str] = []
    f_counts = register_report.get("failure_counts_by_id") or {}
    f13 = int(f_counts.get("F13", 0))
    f4 = int(f_counts.get("F4", 0))
    f6 = int(f_counts.get("F6", 0))
    f1 = int(f_counts.get("F1", 0))

    if f13 > 0:
        issues.append(f"F13 dwell-starvation ({f13})")
    if f4 > 0:
        issues.append(f"F4 closing-line repetition ({f4})")
    if f6 > 0:
        issues.append(f"F6 cadence repetition ({f6})")
    if f1 > 0:
        issues.append(f"F1 template repetition ({f1})")

    # EI V2 cohesion dimension (adjacency-aware lexical overlap)
    ei_chapters = (ei_report.get("chapters") or []) if isinstance(ei_report, dict) else []
    cohesion_fails = 0
    cohesion_warns = 0
    for ch in ei_chapters:
        dims = ch.get("dimensions") or {}
        coh = dims.get("cohesion") or {}
        st = str(coh.get("status", "")).upper()
        if st == "FAIL":
            cohesion_fails += 1
        elif st == "WARN":
            cohesion_warns += 1
    if cohesion_fails:
        issues.append(f"EI cohesion FAIL in {cohesion_fails} chapter(s)")
    if cohesion_warns:
        issues.append(f"EI cohesion WARN in {cohesion_warns} chapter(s)")

    if f13 > 0 or cohesion_fails > 0:
        return "FAIL", issues
    if f4 > 0 or f6 > 0 or f1 > 0 or cohesion_warns > 0:
        return "ADVISORY", issues
    return "PASS", issues


def _cell_verdict(row: dict[str, Any]) -> str:
    hard = [
        row.get("chapter_flow"),
        row.get("register"),
        row.get("book_pass"),
    ]
    if any(x == "FAIL" for x in hard):
        return "FAIL"
    if row.get("cohesion") == "FAIL":
        return "FAIL"
    soft = [row.get("ei_v2"), row.get("craft"), row.get("cohesion")]
    if any(x in ("FAIL", "WARN", "ADVISORY") for x in soft):
        return "ADVISORY"
    if any(x in ("SKIPPED", "MISSING", None) for x in hard + soft):
        return "INCOMPLETE"
    return "PASS"


def _extract_row(render_dir: Path, duration: str, topic: str) -> dict[str, Any]:
    qs_path = render_dir / "quality_summary.json"
    row: dict[str, Any] = {
        "duration": duration,
        "topic": topic,
        "render_dir": str(render_dir.relative_to(REPO_ROOT)),
        "pipeline_exit": None,
        "words": None,
        "chapter_flow": "MISSING",
        "register": "MISSING",
        "register_verdict": "",
        "register_f_counts": {},
        "ei_v2": "MISSING",
        "ei_composite": None,
        "craft": "MISSING",
        "craft_score": None,
        "book_pass": "MISSING",
        "cohesion": "MISSING",
        "cohesion_issues": [],
        "verdict": "INCOMPLETE",
        "quality_gate_failures": [],
        "overall_status": "MISSING",
    }

    book_path = render_dir / "book.txt"
    if book_path.exists():
        row["words"] = len(book_path.read_text(encoding="utf-8").split())

    if not qs_path.exists():
        return row

    qs = json.loads(qs_path.read_text(encoding="utf-8"))
    gates = qs.get("gates") or {}
    row["chapter_flow"] = (gates.get("chapter_flow") or {}).get("status", "MISSING")
    reg = gates.get("register_gate") or {}
    row["register"] = reg.get("status", "MISSING")
    row["register_verdict"] = reg.get("verdict", "")
    row["register_f_counts"] = reg.get("failure_counts_by_id") or {}
    row["ei_v2"] = (gates.get("ei_v2") or {}).get("status", "MISSING")
    row["ei_composite"] = (gates.get("ei_v2") or {}).get("composite")
    row["craft"] = (gates.get("bestseller_craft") or {}).get("status", "MISSING")
    row["craft_score"] = (gates.get("bestseller_craft") or {}).get("overall_score")
    row["book_pass"] = (gates.get("book_pass") or {}).get("status", "MISSING")
    row["quality_gate_failures"] = qs.get("quality_gate_failures") or []
    row["overall_status"] = qs.get("overall_status", "MISSING")

    reg_report: dict = {}
    reg_path = render_dir / "register_gate_report.json"
    if reg_path.exists():
        reg_report = json.loads(reg_path.read_text(encoding="utf-8"))
    ei_report: dict = {}
    ei_path = render_dir / "ei_v2_report.json"
    if ei_path.exists():
        ei_report = json.loads(ei_path.read_text(encoding="utf-8"))

    cohesion, issues = _cohesion_verdict(reg_report, ei_report)
    row["cohesion"] = cohesion
    row["cohesion_issues"] = issues
    row["verdict"] = _cell_verdict(row)
    return row


def _run_pipeline(
    *,
    topic: str,
    arc: Path,
    runtime_format: str,
    render_dir: Path,
    render_book: bool,
) -> int:
    render_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--pipeline-mode",
        "spine",
        "--quality-profile",
        "production",
        "--persona",
        PERSONA,
        "--topic",
        topic,
        "--arc",
        str(arc),
        "--runtime-format",
        runtime_format,
        "--render-dir",
        str(render_dir),
        "--no-job-check",
        "--no-generate-freebies",
    ]
    if render_book:
        cmd.append("--render-book")
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    log_path = render_dir / "pipeline.log"
    log_path.write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr, encoding="utf-8")
    return proc.returncode


def _build_epub(render_dir: Path, topic: str, duration: str) -> Path | None:
    book_path = render_dir / "book.txt"
    if not book_path.exists():
        return None
    title = topic.replace("_", " ").title()
    out = render_dir / f"{duration}__{topic}.epub"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "release" / "build_epub.py"),
        "--input",
        str(book_path),
        "--title",
        f"QA {title}",
        "--subtitle",
        f"{duration} · corporate_managers · production QA",
        "--author",
        "Phoenix Omega QA",
        "--publisher",
        "Phoenix Omega",
        "--topic",
        topic,
        "--output",
        str(out),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        (render_dir / "epub_build.log").write_text(proc.stderr, encoding="utf-8")
        return None
    return out


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    hdr = "| duration | topic | words | chapter_flow | register | EI V2 | craft | book_pass | COHESION | VERDICT |"
    sep = "|---|---|---:|---|---|---|---|---|---|---|"
    lines = [hdr, sep]
    for r in rows:
        ei = r.get("ei_v2", "?")
        if r.get("ei_composite") is not None:
            ei = f"{ei} ({r['ei_composite']:.2f})"
        craft = r.get("craft", "?")
        if r.get("craft_score") is not None:
            craft = f"{craft} ({r['craft_score']:.2f})"
        lines.append(
            "| {duration} | {topic} | {words} | {chapter_flow} | {register} | {ei} | {craft} | {book_pass} | {cohesion} | {verdict} |".format(
                duration=r.get("duration", ""),
                topic=r.get("topic", ""),
                words=r.get("words") if r.get("words") is not None else "—",
                chapter_flow=r.get("chapter_flow", "?"),
                register=r.get("register", "?"),
                ei=ei,
                craft=craft,
                book_pass=r.get("book_pass", "?"),
                cohesion=r.get("cohesion", "?"),
                verdict=r.get("verdict", "?"),
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Duration × topic production QA matrix")
    parser.add_argument("--skip-build", action="store_true", help="Report from existing artifacts only")
    parser.add_argument("--skip-finder", action="store_true", help="Do not open Finder")
    args = parser.parse_args()

    durations = enumerate_durations()
    topics = enumerate_topics()
    topic_arc: dict[str, Path] = {}
    for t in topics:
        arc = arc_for_topic(t)
        if arc:
            topic_arc[t] = arc

    QA_ROOT.mkdir(parents=True, exist_ok=True)
    duration_rows: list[dict[str, Any]] = []
    topic_rows: list[dict[str, Any]] = []

    # Step 2 — one book per duration, different topic each
    topics_with_arcs = [t for t in topics if t in topic_arc]
    for i, dur in enumerate(durations):
        fmt_id = dur["id"]
        topic = topics_with_arcs[i % len(topics_with_arcs)]
        arc = topic_arc[topic]
        render_dir = DURATION_SWEEP_DIR / f"{fmt_id}__{topic}"
        if not args.skip_build:
            print(f"[duration sweep] {fmt_id} + {topic} …", flush=True)
            exit_code = _run_pipeline(
                topic=topic,
                arc=arc,
                runtime_format=fmt_id,
                render_dir=render_dir,
                render_book=True,
            )
        else:
            exit_code = 0 if (render_dir / "quality_summary.json").exists() else 1

        row = _extract_row(render_dir, fmt_id, topic)
        row["pipeline_exit"] = exit_code
        row["word_range"] = dur["word_range"]
        row["chapter_count_default"] = dur["chapter_count"]
        if not args.skip_build and (render_dir / "book.txt").exists():
            _build_epub(render_dir, topic, fmt_id)
        duration_rows.append(row)

    # Step 4 — all topics at standard_book_60min (gates only)
    fmt_60 = "standard_book_60min"
    for topic in topics:
        render_dir = TOPIC_SWEEP_DIR / topic
        if topic not in topic_arc:
            topic_rows.append(
                {
                    "duration": fmt_60,
                    "topic": topic,
                    "words": None,
                    "chapter_flow": "NO_ARC",
                    "register": "NO_ARC",
                    "ei_v2": "NO_ARC",
                    "craft": "NO_ARC",
                    "book_pass": "NO_ARC",
                    "cohesion": "NO_ARC",
                    "verdict": "NO_ARC",
                    "cohesion_issues": ["no corporate_managers master arc"],
                }
            )
            continue
        arc = topic_arc[topic]
        if not args.skip_build:
            print(f"[topic sweep 60min] {topic} …", flush=True)
            exit_code = _run_pipeline(
                topic=topic,
                arc=arc,
                runtime_format=fmt_60,
                render_dir=render_dir,
                render_book=True,
            )
        else:
            exit_code = 0 if (render_dir / "quality_summary.json").exists() else 1
        row = _extract_row(render_dir, fmt_60, topic)
        row["pipeline_exit"] = exit_code
        topic_rows.append(row)

    all_rows = duration_rows + topic_rows
    pass_count = sum(1 for r in all_rows if r.get("verdict") == "PASS")
    total = len(all_rows)

    # Root cause tally
    fail_reasons: dict[str, int] = {}
    for r in all_rows:
        for g in r.get("quality_gate_failures") or []:
            fail_reasons[g] = fail_reasons.get(g, 0) + 1
        if r.get("chapter_flow") == "FAIL":
            fail_reasons["chapter_flow_status"] = fail_reasons.get("chapter_flow_status", 0) + 1
        fc = r.get("register_f_counts") or {}
        if fc.get("F1"):
            fail_reasons["register_F1"] = fail_reasons.get("register_F1", 0) + 1
        if fc.get("F6"):
            fail_reasons["register_F6"] = fail_reasons.get("register_F6", 0) + 1
        if fc.get("F13"):
            fail_reasons["register_F13_dwell"] = fail_reasons.get("register_F13_dwell", 0) + 1
        if r.get("cohesion") == "FAIL":
            fail_reasons["cohesion_lane"] = fail_reasons.get("cohesion_lane", 0) + 1

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = QA_ROOT / f"BESTSELLER_COHESION_MATRIX_{ts}.md"
    json_path = QA_ROOT / f"bestseller_cohesion_matrix_{ts}.json"

    lines = [
        "# Pearl Prime — Duration × Topic Bestseller + Cohesion Matrix",
        "",
        f"Generated: {ts} (local, production profile, persona `{PERSONA}`)",
        "",
        "## Step 1 — Matrix enumeration",
        "",
        "### Durations (runtime_formats with word_range)",
        "",
        "| format | word_range | chapter_count_default |",
        "|---|---:|---:|",
    ]
    for d in durations:
        lines.append(f"| {d['id']} | {d['word_range'][0]}–{d['word_range'][1]} | {d['chapter_count']} |")
    lines += [
        "",
        f"### Topics ({len(topics)} canonical)",
        "",
        ", ".join(f"`{t}`" for t in topics),
        "",
        f"Arc coverage for `{PERSONA}`: {len(topic_arc)}/{len(topics)} topics",
        "",
        "## Step 2 — One book per duration (QA EPUBs)",
        "",
        _markdown_table(duration_rows),
        "",
        "## Step 4 — Topic sweep at standard_book_60min",
        "",
        _markdown_table(topic_rows),
        "",
        "## Bottom line",
        "",
        f"**{pass_count}/{total} cells meet the full production bestseller + cohesive bar (VERDICT=PASS).**",
        "",
        "This is expected to be **below 100%** while assembly-P0 (chapter_flow, register F1/F6, "
        "ARC_POSITION / BookStructurePlan) and cohesion lanes (F13 dwell-integration, adjacency "
        "atom selector) remain open per OPD-20260627-001.",
        "",
        "### Systemic failure tally",
        "",
    ]
    for k, v in sorted(fail_reasons.items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} cell(s)")
    lines += [
        "",
        "### Cohesion detail (cells with issues)",
        "",
    ]
    for r in all_rows:
        if r.get("cohesion_issues"):
            lines.append(
                f"- **{r.get('duration')} / {r.get('topic')}**: {r.get('cohesion')} — "
                + "; ".join(r["cohesion_issues"])
            )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "timestamp": ts,
                "persona": PERSONA,
                "durations": durations,
                "topics": topics,
                "duration_rows": duration_rows,
                "topic_rows": topic_rows,
                "pass_count": pass_count,
                "total_cells": total,
                "fail_reasons": fail_reasons,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n" + _markdown_table(duration_rows))
    print("\n--- topic sweep ---\n")
    print(_markdown_table(topic_rows))
    print(f"\nBottom line: {pass_count}/{total} PASS")
    print(f"Report: {report_path}")

    if not args.skip_finder and sys.platform == "darwin":
        subprocess.run(["open", str(QA_ROOT)], check=False)

    return 0 if pass_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

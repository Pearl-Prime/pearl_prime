#!/usr/bin/env python3
"""Run the final Pearl Prime books-to-100 proof matrix without bypasses."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


TARGETS = (
    {
        "id": "en_genz_anxiety",
        "persona": "gen_z_professionals",
        "topic": "anxiety",
        "engine": None,
        "locale": "en-US",
        "contract": True,
    },
    {
        "id": "zhtw_genz_anxiety",
        "persona": "gen_z_professionals",
        "topic": "anxiety",
        "engine": None,
        "locale": "zh-TW",
    },
    {
        "id": "corporate_burnout_overwhelm",
        "persona": "corporate_managers",
        "topic": "burnout",
        "engine": "overwhelm",
        "locale": "en-US",
    },
    {
        "id": "educator_anxiety",
        "persona": "educators",
        "topic": "anxiety",
        "engine": None,
        "locale": "en-US",
    },
)


def _discover_arc(repo: Path, persona: str, topic: str, engine: str | None) -> Path | None:
    root = repo / "config/source_of_truth/master_arcs"
    patterns = []
    if engine:
        patterns.append(f"{persona}__{topic}__{engine}__*.yaml")
    patterns.extend([
        f"{persona}__{topic}__*__F006.yaml",
        f"{persona}__{topic}__*.yaml",
    ])
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(sorted(root.glob(pattern)))
        if candidates:
            break
    if not candidates:
        return None
    preferred = [
        path for path in candidates
        if any(token in path.name for token in ("false_alarm", "overwhelm"))
    ]
    return (preferred or candidates)[0]


def _run(repo: Path, command: list[str], log: Path) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": "."},
        check=False,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(proc.stdout, encoding="utf-8")
    return {
        "command": command,
        "exit_code": proc.returncode,
        "log": str(log.relative_to(repo)),
    }


def _quality_summary(render_dir: Path) -> dict[str, Any]:
    path = render_dir / "quality_summary.json"
    if not path.is_file():
        return {"status": "MISSING", "path": str(path)}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "INVALID", "error": str(exc), "path": str(path)}
    value["_path"] = str(path)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/qa/final_books_100_20260714"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)

    required_scripts = [
        repo / "scripts/run_pipeline.py",
        repo / "scripts/qa/audit_atom_bank_health.py",
        repo / "scripts/localization/build_14_locale_worklist.py",
        repo / "scripts/ci/check_enhancement_contract_v21.py",
    ]
    missing = [str(path.relative_to(repo)) for path in required_scripts if not path.is_file()]
    if missing:
        payload = {
            "production_ready_100": False,
            "status": "BLOCKED",
            "blockers": ["missing prerequisite scripts: " + ", ".join(missing)],
            "books": [],
        }
        (out / "proof_matrix.json").write_text(json.dumps(payload, indent=2) + "\n")
        return 3

    books = []
    for target in TARGETS:
        arc = _discover_arc(
            repo, target["persona"], target["topic"], target["engine"]
        )
        if arc is None:
            books.append({
                **target,
                "status": "BLOCKED",
                "blocker": "matching master arc not found",
            })
            continue
        render_name = (
            f"{target['id']}_enhancement_contract"
            if target.get("contract")
            else target["id"]
        )
        render_dir = out / "renders" / render_name
        command = [
            sys.executable,
            "scripts/run_pipeline.py",
            "--topic", target["topic"],
            "--persona", target["persona"],
            "--arc", str(arc.relative_to(repo)),
            "--pipeline-mode", "spine",
            "--runtime-format", "extended_book_2h",
            "--quality-profile", "production",
            "--exercise-journeys",
            "--no-job-check",
            "--render-book",
            "--render-dir", str(render_dir.relative_to(repo)),
        ]
        if target["locale"] != "en-US":
            command.extend(["--locale", target["locale"]])
        result = _run(repo, command, out / "logs" / f"{target['id']}.log")
        quality = _quality_summary(render_dir)
        books.append({
            **target,
            "arc": str(arc.relative_to(repo)),
            "render_dir": str(render_dir.relative_to(repo)),
            "command": result,
            "quality_summary": quality,
            "status": "PASS" if result["exit_code"] == 0 else "FAIL",
        })

    atom = _run(
        repo,
        [sys.executable, "scripts/qa/audit_atom_bank_health.py",
         "--artifact-root", str((out / "atom_bank_health").relative_to(repo))],
        out / "logs/atom_bank_health.log",
    )
    localization = _run(
        repo,
        [sys.executable, "scripts/localization/build_14_locale_worklist.py",
         "--out", str((out / "localization_14").relative_to(repo))],
        out / "logs/localization_14.log",
    )

    flagship_row = next(
        (row for row in books if row.get("id") == "en_genz_anxiety"),
        None,
    )
    flagship = (
        repo / str(flagship_row["render_dir"]) / "enhancement_contract.json"
        if flagship_row and flagship_row.get("render_dir")
        else out / "renders/en_genz_anxiety/enhancement_contract.json"
    )
    if flagship.is_file():
        enhancement = _run(
            repo,
            [sys.executable, "scripts/ci/check_enhancement_contract_v21.py",
             str(flagship.relative_to(repo)), "--quality-profile", "production"],
            out / "logs/enhancement_contract.log",
        )
    else:
        enhancement = {
            "command": [],
            "exit_code": 3,
            "log": "",
            "blocker": "flagship enhancement_contract.json missing",
        }

    books_passed = [row["id"] for row in books if row["status"] == "PASS"]
    blockers = []
    for row in books:
        if row["status"] != "PASS":
            blockers.append(f"{row['id']}:{row.get('blocker') or 'production command failed'}")
    if atom["exit_code"] != 0:
        blockers.append("atom_bank_health_high_risk_or_failed")
    if localization["exit_code"] != 0:
        blockers.append("14_locale_coverage_incomplete")
    if enhancement["exit_code"] != 0:
        blockers.append("enhancement_contract_not_pass")

    payload = {
        "schema_version": "1.0.0",
        "production_ready_100": not blockers,
        "status": "PASS" if not blockers else "NOT_READY",
        "proof_root": str(out.relative_to(repo)),
        "books": books,
        "books_passed": books_passed,
        "atom_bank_health": atom,
        "localization_14": localization,
        "enhancement_contract": enhancement,
        "remaining_true_blockers": blockers,
        "bypasses": {
            "draft_mode": False,
            "skip_quality_gates": False,
            "stale_proof_accepted": False,
        },
    }
    (out / "proof_matrix.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Final Books 100 Proof Matrix",
        "",
        f"- Production ready 100: **{'YES' if payload['production_ready_100'] else 'NO'}**",
        f"- Books passed: {', '.join(books_passed) or 'none'}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in blockers)
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["production_ready_100"] else 3


if __name__ == "__main__":
    raise SystemExit(main())

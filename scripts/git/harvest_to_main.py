#!/usr/bin/env python3
"""
Harvest-to-main reporting lane (Workstream B).

Report-only: classifies codex/* and spec-backed recovery work vs origin/main.
Never merges branches or mutates the repo.

Authority (read by humans; embedded slices mirror these paths):
- docs/REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md
- docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md
- docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md
- docs/BRANCH_DISPOSITION_2026_03_20.md
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "artifacts" / "governance" / "main_harvest"
DISPOSITION_PATH = REPO_ROOT / "docs" / "BRANCH_DISPOSITION_2026_03_20.md"
PEARL_RECOVERY_SPEC = REPO_ROOT / "docs" / "PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md"
PEARL_AUDIT_SPEC = REPO_ROOT / "docs" / "PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md"

# Primary convergence branch named in Pearl Prime recovery + salvage audit.
CONVERGENCE_BRANCH = "codex/state-convergence-20260328"

MERGE_POLICY_NOTE = (
    "Do not merge any codex/* convergence branch directly to main. "
    "Cut a clean agent/* branch from origin/main and transplant only the listed files."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), check=False, capture_output=True, text=True)


def parse_disposition_table(path: Path) -> dict[str, str]:
    """Map codex short branch name -> disposition label from disposition doc."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    row_re = re.compile(
        r"\|\s*`origin/codex/([^`]+)`\s*\|\s*`[^`]*`\s*\|\s*`([^`]+)`\s*\|",
    )
    for m in row_re.finditer(text):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def ref_exists(ref: str) -> bool:
    proc = safe_run(["git", "rev-parse", "-q", "--verify", ref])
    return proc.returncode == 0


def merge_base_symmetric_diff_files(left: str, right: str) -> tuple[list[str] | None, str | None]:
    """Files differing between merge-base(left,right) and tips (git diff three-dot)."""
    proc = safe_run(["git", "diff", "--name-only", f"{left}...{right}"])
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout or "").strip()
    files = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return files, None


def rev_list_count(range_spec: str) -> int | None:
    proc = safe_run(["git", "rev-list", "--count", range_spec])
    if proc.returncode != 0:
        return None
    try:
        return int(proc.stdout.strip())
    except ValueError:
        return None


def is_ancestor(desc: str, anc: str) -> bool | None:
    proc = safe_run(["git", "merge-base", "--is-ancestor", desc, anc])
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    return None


@dataclass
class PRSlice:
    """One governed clean-PR slice (spec-backed)."""

    slice_id: str
    title: str
    source_branch: str
    target: str
    recommended_branch: str
    files: list[str]
    required_tests: list[str]
    blocking_dependencies: list[str]
    spec_reference: str
    merge_policy: str = MERGE_POLICY_NOTE


@dataclass
class BranchHarvestItem:
    ref_name: str
    short_name: str
    classification: str
    rationale: str
    disposition: str | None
    commits_ahead_of_main: int | None
    commits_behind_main: int | None
    main_ancestor_of_tip: bool | None
    tip_ancestor_of_main: bool | None
    diff_files_sample: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class HarvestReport:
    started_at: str
    repo_root: str
    run_label: str | None
    mode: str
    merge_target: str
    notes: list[str] = field(default_factory=list)
    branch_items: list[BranchHarvestItem] = field(default_factory=list)


def pearl_prime_slices_from_spec() -> list[PRSlice]:
    """Static slices transcribed from docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5."""
    return [
        PRSlice(
            slice_id="pearl_prime_pr1",
            title="Runtime identity + location truth",
            source_branch=CONVERGENCE_BRANCH,
            target="origin/main",
            recommended_branch="agent/pearl-prime-runtime-truth",
            files=[
                "scripts/run_pipeline.py",
                "phoenix_v4/planning/catalog_planner.py",
                "phoenix_v4/rendering/book_renderer.py",
                "config/localization/render_location_profiles.yaml",
                "tests/test_book_renderer.py",
                "tests/test_book_renderer_location_fallbacks.py",
                "tests/test_topic_identity_resolution.py",
            ],
            required_tests=[
                "PYTHONPATH=. python3 -m pytest tests/test_topic_identity_resolution.py "
                "tests/test_book_renderer_location_fallbacks.py tests/test_book_renderer.py "
                "tests/test_location_passthrough.py -q",
            ],
            blocking_dependencies=[],
            spec_reference="docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 1",
        ),
        PRSlice(
            slice_id="pearl_prime_pr2",
            title="Bestseller composition + editorial runtime",
            source_branch=CONVERGENCE_BRANCH,
            target="origin/main",
            recommended_branch="agent/pearl-prime-bestseller-runtime",
            files=[
                "phoenix_v4/rendering/chapter_composer.py",
                "phoenix_v4/rendering/book_renderer.py",
                "phoenix_v4/quality/chapter_flow_gate.py",
                "phoenix_v4/qa/bestseller_editor.py",
                "phoenix_v4/planning/slot_resolver.py",
                "phoenix_v4/planning/assembly_compiler.py",
                "tests/test_chapter_composer.py",
                "tests/test_chapter_flow_gate.py",
            ],
            required_tests=[
                "PYTHONPATH=. python3 -m pytest tests/test_chapter_composer.py "
                "tests/test_chapter_flow_gate.py tests/test_book_renderer.py -q",
            ],
            blocking_dependencies=[
                "Branch from agent/pearl-prime-runtime-truth (PR 1 head) or from updated "
                "origin/main after PR 1 merges; do not open standalone from main while PR 1 "
                "would conflict on book_renderer.py (per recovery spec §5 PR 2).",
            ],
            spec_reference="docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 2",
        ),
        PRSlice(
            slice_id="pearl_prime_pr3",
            title="Governing Pearl Prime recovery docs",
            source_branch=CONVERGENCE_BRANCH,
            target="origin/main",
            recommended_branch="agent/pearl-prime-recovery-docs",
            files=[
                "docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md",
                "docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md",
                "docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md",
                "docs/DOCS_INDEX.md",
            ],
            required_tests=["PYTHONPATH=. python3 scripts/ci/check_docs_governance.py"],
            blocking_dependencies=[
                "Prefer origin/main after PR 2 merges (or stack on PR 2 head if cleaner).",
            ],
            spec_reference="docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 PR 3",
        ),
    ]


def classify_disposition_branch(
    _short: str,
    disp: str | None,
    *,
    ahead: int | None,
    behind: int | None,
    tip_is_ancestor_of_main: bool | None,
    _main_is_ancestor_of_tip: bool | None,
) -> tuple[str, str]:
    if tip_is_ancestor_of_main is True:
        return "already_on_main", "Tip is an ancestor of origin/main (fully merged lineage)."
    if ahead == 0 and tip_is_ancestor_of_main is True:
        return "already_on_main", "No commits on tip not in origin/main; tip is ancestor of main."

    if not disp:
        return (
            "blocked",
            "No row in docs/BRANCH_DISPOSITION_2026_03_20.md; human triage before harvest.",
        )

    if disp in {"keep-open", "keep-audit"}:
        return "keep_open", f"Disposition `{disp}`: keep for audit/review; no wholesale merge."

    if disp == "delete":
        return "superseded", f"Disposition `delete`: do not merge; branch marked for removal."

    if disp == "harvest":
        return (
            "needs_clean_pr",
            "Disposition `harvest`: selective slices only; file list not machine-bound here—"
            "use disposition section notes and a fresh branch from origin/main.",
        )

    return "blocked", f"Unknown disposition `{disp}`."


def resolve_convergence_ref() -> tuple[str | None, str | None]:
    for ref in (CONVERGENCE_BRANCH, f"origin/{CONVERGENCE_BRANCH}"):
        if ref_exists(ref):
            return ref, None
    return None, f"Neither {CONVERGENCE_BRANCH} nor origin/{CONVERGENCE_BRANCH} exists."


def slice_divergent_files(slice_files: list[str], source_ref: str) -> list[str]:
    out: list[str] = []
    for rel in slice_files:
        proc = safe_run(["git", "diff", "--name-only", "origin/main", source_ref, "--", rel])
        if proc.returncode != 0:
            continue
        if proc.stdout.strip():
            out.append(rel)
    return out


def enrich_pearl_slices(source_ref: str | None) -> list[dict[str, Any]]:
    slices = pearl_prime_slices_from_spec()
    payload: list[dict[str, Any]] = []
    for s in slices:
        d = asdict(s)
        if source_ref:
            divergent = slice_divergent_files(s.files, source_ref)
            d["files_still_divergent_from_main"] = divergent
            if divergent:
                d["classification"] = "needs_clean_pr"
            else:
                d["classification"] = "already_on_main"
                d["classification_note"] = (
                    "No diff vs origin/main for listed paths on source ref "
                    f"(verify manually if main advanced partially)."
                )
        else:
            d["files_still_divergent_from_main"] = []
            d["classification"] = "blocked"
            d["classification_note"] = "Source convergence ref missing; cannot diff."
        payload.append(d)
    return payload


def collect_codex_branches() -> tuple[set[str], str | None]:
    """Short names codex/foo from local heads and origin/codex/*."""
    names: set[str] = set()
    proc = safe_run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/codex"])
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("codex/"):
                names.add(line)
    proc_r = safe_run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/codex"],
    )
    err = None
    if proc_r.returncode != 0:
        err = (proc_r.stderr or proc_r.stdout or "").strip()
    else:
        for line in proc_r.stdout.splitlines():
            line = line.strip()
            if line.startswith("origin/codex/"):
                names.add("codex/" + line.removeprefix("origin/codex/"))
    return names, err


def build_branch_items(disposition_map: dict[str, str]) -> list[BranchHarvestItem]:
    names, ref_err = collect_codex_branches()
    items: list[BranchHarvestItem] = []
    if ref_err:
        items.append(
            BranchHarvestItem(
                ref_name="(enumeration)",
                short_name="origin/codex/*",
                classification="blocked",
                rationale="Could not list remote-tracking codex refs.",
                disposition=None,
                commits_ahead_of_main=None,
                commits_behind_main=None,
                main_ancestor_of_tip=None,
                tip_ancestor_of_main=None,
                notes=[ref_err],
            ),
        )
        return items

    for short in sorted(names):
        short_name = short.removeprefix("codex/")
        disp = disposition_map.get(short_name)
        local_ref = short if ref_exists(short) else None
        remote_ref = f"origin/{short}" if ref_exists(f"origin/{short}") else None
        tip = local_ref or remote_ref
        ref_name = tip or short

        if not tip:
            items.append(
                BranchHarvestItem(
                    ref_name=ref_name,
                    short_name=short,
                    classification="blocked",
                    rationale="Ref not present locally or as origin remote-tracking branch.",
                    disposition=disp,
                    commits_ahead_of_main=None,
                    commits_behind_main=None,
                    main_ancestor_of_tip=None,
                    tip_ancestor_of_main=None,
                ),
            )
            continue

        ahead = rev_list_count(f"origin/main..{tip}")
        behind = rev_list_count(f"{tip}..origin/main")
        tip_anc_main = is_ancestor(tip, "origin/main")
        main_anc_tip = is_ancestor("origin/main", tip)

        if short_name == "state-convergence-20260328":
            cls, why = (
                "needs_clean_pr",
                "Primary Pearl Prime convergence carrier; use governed PR slices only "
                "(see pearl_prime_slices in report).",
            )
        else:
            cls, why = classify_disposition_branch(
                short_name,
                disp,
                ahead=ahead,
                behind=behind,
                tip_is_ancestor_of_main=tip_anc_main,
                _main_is_ancestor_of_tip=main_anc_tip,
            )

        diff_files, diff_err = merge_base_symmetric_diff_files("origin/main", tip)
        sample = (diff_files or [])[:40]

        notes: list[str] = []
        if diff_err:
            notes.append(diff_err)
        if short_name == "state-convergence-20260328":
            notes.append(f"Spec: {PEARL_RECOVERY_SPEC.name}, {PEARL_AUDIT_SPEC.name}")

        items.append(
            BranchHarvestItem(
                ref_name=ref_name,
                short_name=short,
                classification=cls,
                rationale=why,
                disposition=disp,
                commits_ahead_of_main=ahead,
                commits_behind_main=behind,
                main_ancestor_of_tip=main_anc_tip,
                tip_ancestor_of_main=tip_anc_main,
                diff_files_sample=sample,
                notes=notes,
            ),
        )
    return items


def auxiliary_harvest_items() -> list[dict[str, Any]]:
    """Non-codex items named in salvage audit (report-first)."""
    out: list[dict[str, Any]] = []
    out.append(
        {
            "id": "pearl_prime_followup_source_repair",
            "classification": "blocked",
            "title": "Source/bank repair lane (not a branch cherry-pick)",
            "rationale": (
                "docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 follow-up: hollow atoms, "
                "teacher coverage, persona/location catalog work—new implementation, not salvage PR."
            ),
            "spec_reference": "docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md §5 Follow-up Lane",
        },
    )
    signoff_path = "artifacts/governance/bestseller_100_signoff_2026-03-26.md"
    proc = safe_run(["git", "cat-file", "-e", f"origin/main:{signoff_path}"])
    on_main = proc.returncode == 0
    signoff_branch = "origin/agent/bestseller-100-signoff-clean"
    signoff_ref = signoff_branch if ref_exists(signoff_branch) else None
    item: dict[str, Any] = {
        "id": "bestseller_100_signoff_branch",
        "title": "Bestseller 100 signoff evidence (narrow artifact)",
        "classification": "already_on_main" if on_main else "needs_clean_pr",
        "source_branch": signoff_branch,
        "target": "origin/main",
        "recommended_branch": "agent/bestseller-100-signoff",
        "files": [signoff_path],
        "required_tests": [],
        "blocking_dependencies": [],
        "spec_reference": "docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md § B (agent branch)",
        "merge_policy": MERGE_POLICY_NOTE,
        "rationale": (
            "Salvage audit: `origin/agent/bestseller-100-signoff-clean` carries signoff evidence only. "
            "If the signoff markdown is not on `origin/main`, open a narrow PR from a clean `agent/*` "
            "branch—do not merge the agent branch wholesale."
        ),
        "note": (
            "If the signoff ref is missing locally, fetch origin before relying on divergence fields."
        ),
    }
    if not on_main and signoff_ref:
        div = slice_divergent_files([signoff_path], signoff_ref)
        item["files_still_divergent_from_main"] = div
    elif not on_main:
        item["files_still_divergent_from_main"] = []
        item["note"] = (
            item["note"] + " Signoff branch ref not present locally; fetch origin before diffing."
        )
    out.append(item)
    return out


def build_report(*, run_label: str | None) -> HarvestReport:
    notes: list[str] = []
    mode = "online_live"
    fetch = safe_run(["git", "fetch", "origin", "--prune"])
    if fetch.returncode != 0:
        mode = "offline_degraded"
        notes.append(
            "git fetch failed; branch distance and diffs may use stale refs: "
            + (fetch.stderr or fetch.stdout or "").strip(),
        )

    if not ref_exists("origin/main"):
        mode = "offline_degraded"
        notes.append("origin/main missing; cannot classify vs production main.")

    disposition_map = parse_disposition_table(DISPOSITION_PATH)
    branch_items = build_branch_items(disposition_map)
    _conv_ref, conv_err = resolve_convergence_ref()
    if conv_err:
        notes.append(conv_err)

    return HarvestReport(
        started_at=utc_now(),
        repo_root=str(REPO_ROOT),
        run_label=run_label,
        mode=mode,
        merge_target="origin/main",
        notes=notes,
        branch_items=branch_items,
    )


def build_report_payload(report: HarvestReport, pearl_json: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "started_at": report.started_at,
        "repo_root": report.repo_root,
        "run_label": report.run_label,
        "mode": report.mode,
        "merge_target": report.merge_target,
        "merge_policy": MERGE_POLICY_NOTE,
        "notes": report.notes,
        "branch_candidates": [asdict(b) for b in report.branch_items],
        "pearl_prime_slices": pearl_json,
        "auxiliary_items": auxiliary_harvest_items(),
        "authority_docs": [
            "docs/REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md",
            "docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md",
            "docs/PEARL_PRIME_SALVAGE_AUDIT_2026_03_29.md",
            "docs/BRANCH_DISPOSITION_2026_03_20.md",
        ],
    }


def write_report(payload: dict[str, Any], report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = report_dir / f"main_harvest_{stamp}.json"
    md_path = report_dir / f"main_harvest_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Main harvest report (report-only)",
        "",
        f"- Started: `{payload['started_at']}`",
        f"- Repo: `{payload['repo_root']}`",
        f"- Run label: `{payload.get('run_label') or 'none'}`",
        f"- Mode: `{payload['mode']}`",
        f"- Merge target: `{payload['merge_target']}`",
        "",
        "## Policy",
        "",
        payload["merge_policy"],
        "",
        "## Pearl Prime governed PR slices",
        "",
    ]
    for s in payload.get("pearl_prime_slices", []):
        lines.append(f"### {s.get('slice_id')}: {s.get('title')}")
        lines.append("")
        lines.append(f"- **Classification:** `{s.get('classification')}`")
        if s.get("classification_note"):
            lines.append(f"- **Note:** {s['classification_note']}")
        lines.append(f"- **Source (material):** `{s.get('source_branch')}`")
        lines.append(f"- **Target:** `{s.get('target')}`")
        lines.append(f"- **Recommended clean branch:** `{s.get('recommended_branch')}`")
        lines.append(f"- **Spec:** `{s.get('spec_reference')}`")
        if s.get("blocking_dependencies"):
            lines.append("- **Blocking dependencies:**")
            for b in s["blocking_dependencies"]:
                lines.append(f"  - {b}")
        lines.append("- **Files (governed list):**")
        for f in s.get("files", []):
            lines.append(f"  - `{f}`")
        if s.get("files_still_divergent_from_main"):
            lines.append("- **Still divergent vs origin/main (per-path diff):**")
            for f in s["files_still_divergent_from_main"]:
                lines.append(f"  - `{f}`")
        lines.append("- **Required tests:**")
        for t in s.get("required_tests", []):
            lines.append(f"  - `{t}`")
        lines.append("")

    lines.extend(
        [
            "## Codex branch candidates",
            "",
        ],
    )
    for b in payload.get("branch_candidates", []):
        lines.append(f"- **`{b['short_name']}`** (`{b['ref_name']}`): `{b['classification']}` — {b['rationale']}")
        if b.get("disposition"):
            lines.append(f"  - disposition doc: `{b['disposition']}`")
        if b.get("commits_ahead_of_main") is not None:
            lines.append(f"  - commits ahead of origin/main: `{b['commits_ahead_of_main']}`")
        if b.get("diff_files_sample"):
            lines.append("  - diff sample (first 40 paths, symmetric):")
            for p in b["diff_files_sample"][:10]:
                lines.append(f"    - `{p}`")
            if len(b["diff_files_sample"]) > 10:
                lines.append("    - …")
        lines.append("")

    lines.extend(["## Auxiliary items", ""])
    for a in payload.get("auxiliary_items", []):
        aid = a.get("id", "item")
        title = (a.get("title") or "").strip() or aid.replace("_", " ")
        lines.append(f"- **{title}** (`{aid}`) — `{a.get('classification')}`")
        rationale = (a.get("rationale") or "").strip()
        if rationale:
            lines.append(f"  - {rationale}")
        extra = (a.get("note") or "").strip()
        if extra and extra != rationale:
            lines.append(f"  - *Note:* {extra}")
        lines.append("")

    if payload.get("notes"):
        lines.extend(["## Notes", ""])
        lines.extend(f"- {n}" for n in payload["notes"])
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_j = report_dir / "latest_main_harvest.json"
    latest_m = report_dir / "latest_main_harvest.md"
    shutil.copy2(json_path, latest_j)
    shutil.copy2(md_path, latest_m)
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Harvest-to-main report (Workstream B, report-only)")
    p.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for JSON/Markdown reports",
    )
    p.add_argument(
        "--report-label",
        default=None,
        metavar="LABEL",
        help="Optional label recorded in the report",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(run_label=args.report_label)
    conv_ref, _ = resolve_convergence_ref()
    pearl_json = enrich_pearl_slices(conv_ref)
    payload = build_report_payload(report, pearl_json)
    json_path, md_path = write_report(payload, Path(args.report_dir))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if payload["mode"] == "offline_degraded":
        print("WARNING: mode=offline_degraded — verify refs before acting.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

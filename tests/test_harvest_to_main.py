from __future__ import annotations

import json

from scripts.git.harvest_to_main import (
    MERGE_POLICY_NOTE,
    BranchHarvestItem,
    HarvestReport,
    build_report_payload,
    enrich_pearl_slices,
    parse_disposition_table,
    pearl_prime_slices_from_spec,
    write_report,
)


def test_parse_disposition_finds_runtime_consolidation() -> None:
    from pathlib import Path

    from scripts.git import harvest_to_main as h

    path = Path(h.__file__).resolve().parents[2] / "docs" / "BRANCH_DISPOSITION_2026_03_20.md"
    m = parse_disposition_table(path)
    assert m.get("runtime-consolidation") == "keep-open"


def test_pearl_prime_slices_count_and_merge_policy() -> None:
    slices = pearl_prime_slices_from_spec()
    assert len(slices) == 3
    pr1_files = slices[0].files
    assert "phoenix_v4/planning/catalog_planner.py" in pr1_files
    for s in slices:
        assert s.target == "origin/main"
        assert MERGE_POLICY_NOTE in s.merge_policy
        assert "codex/state-convergence-20260328" == s.source_branch


def test_enrich_pearl_slices_includes_classifications() -> None:
    out = enrich_pearl_slices(None)
    assert len(out) == 3
    assert all("classification" in x for x in out)
    blocked = [x for x in out if x["classification"] == "blocked"]
    assert len(blocked) == 3


def test_write_report_creates_latest_aliases(tmp_path) -> None:
    report = HarvestReport(
        started_at="2026-03-29T12:00:00Z",
        repo_root=str(tmp_path),
        run_label="unit",
        mode="online_live",
        merge_target="origin/main",
        branch_items=[
            BranchHarvestItem(
                ref_name="codex/example",
                short_name="codex/example",
                classification="blocked",
                rationale="fixture",
                disposition=None,
                commits_ahead_of_main=None,
                commits_behind_main=None,
                main_ancestor_of_tip=None,
                tip_ancestor_of_main=None,
            ),
        ],
    )
    pearl = enrich_pearl_slices(None)
    payload = build_report_payload(report, pearl)
    json_path, md_path = write_report(payload, tmp_path)
    latest = tmp_path / "latest_main_harvest.json"
    assert latest.exists()
    assert latest.read_text(encoding="utf-8") == json_path.read_text(encoding="utf-8")
    data = json.loads(latest.read_text(encoding="utf-8"))
    assert data["merge_policy"] == MERGE_POLICY_NOTE
    assert len(data["pearl_prime_slices"]) == 3
    assert "branch_candidates" in data

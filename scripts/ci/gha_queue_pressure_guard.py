#!/usr/bin/env python3
"""Fail-closed guard for catalog fanout workflows when GitHub Actions is congested.

Samples recent workflow runs via ``gh run list`` and blocks fanout dispatch when
queue pressure would starve non-catalog PR throughput. Used by catalog-fanout-*
workflows before spawning PR waves.

Exit 0 = safe to proceed; exit 1 = queue hot (unless --force).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass


DEFAULT_SAMPLE_LIMIT = 200
DEFAULT_QUEUED_TOTAL_HOT = 80
DEFAULT_CATALOG_QUEUED_HOT = 60
DEFAULT_STARVATION_RATIO = 5.0


@dataclass(frozen=True)
class QueueSnapshot:
    queued_total: int
    catalog_queued: int
    non_catalog_queued: int

    @property
    def catalog_ratio(self) -> float:
        if self.queued_total == 0:
            return 0.0
        return self.catalog_queued / self.queued_total


@dataclass(frozen=True)
class GuardDecision:
    blocked: bool
    reason: str
    snapshot: QueueSnapshot


def _is_catalog_branch(branch: str) -> bool:
    b = (branch or "").lower()
    return b.startswith("ci/catalog-") or "/catalog-" in b


def assess_queue_pressure(
    snapshot: QueueSnapshot,
    *,
    queued_total_hot: int = DEFAULT_QUEUED_TOTAL_HOT,
    catalog_queued_hot: int = DEFAULT_CATALOG_QUEUED_HOT,
    starvation_ratio: float = DEFAULT_STARVATION_RATIO,
) -> GuardDecision:
    if snapshot.queued_total >= queued_total_hot:
        return GuardDecision(
            blocked=True,
            reason=(
                f"queued_total={snapshot.queued_total} >= hot threshold {queued_total_hot}"
            ),
            snapshot=snapshot,
        )
    if snapshot.catalog_queued >= catalog_queued_hot:
        return GuardDecision(
            blocked=True,
            reason=(
                f"catalog_queued={snapshot.catalog_queued} "
                f">= hot threshold {catalog_queued_hot}"
            ),
            snapshot=snapshot,
        )
    if (
        snapshot.non_catalog_queued > 0
        and snapshot.catalog_queued
        >= starvation_ratio * snapshot.non_catalog_queued
    ):
        return GuardDecision(
            blocked=True,
            reason=(
                f"non-catalog starvation: catalog_queued={snapshot.catalog_queued} "
                f"vs non_catalog_queued={snapshot.non_catalog_queued} "
                f"(ratio >= {starvation_ratio})"
            ),
            snapshot=snapshot,
        )
    return GuardDecision(
        blocked=False,
        reason="queue pressure within safe bounds",
        snapshot=snapshot,
    )


def snapshot_from_runs(runs: list[dict]) -> QueueSnapshot:
    queued = [r for r in runs if r.get("status") == "queued"]
    catalog = [r for r in queued if _is_catalog_branch(r.get("headBranch", ""))]
    return QueueSnapshot(
        queued_total=len(queued),
        catalog_queued=len(catalog),
        non_catalog_queued=len(queued) - len(catalog),
    )


def fetch_runs_via_gh(limit: int) -> list[dict]:
    proc = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--limit",
            str(limit),
            "--json",
            "status,headBranch,workflowName",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh run list failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout or "[]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Proceed even when queue pressure is hot (manual override).",
    )
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--queued-total-hot", type=int, default=DEFAULT_QUEUED_TOTAL_HOT)
    parser.add_argument("--catalog-queued-hot", type=int, default=DEFAULT_CATALOG_QUEUED_HOT)
    parser.add_argument(
        "--starvation-ratio",
        type=float,
        default=DEFAULT_STARVATION_RATIO,
    )
    parser.add_argument(
        "--json-runs",
        help="Optional path to gh run list JSON (for tests); skips live gh call.",
    )
    args = parser.parse_args(argv)

    runs = (
        json.loads(open(args.json_runs, encoding="utf-8").read())
        if args.json_runs
        else fetch_runs_via_gh(args.sample_limit)
    )
    snapshot = snapshot_from_runs(runs)
    decision = assess_queue_pressure(
        snapshot,
        queued_total_hot=args.queued_total_hot,
        catalog_queued_hot=args.catalog_queued_hot,
        starvation_ratio=args.starvation_ratio,
    )

    print(
        "gha_queue_pressure_guard: "
        f"queued_total={snapshot.queued_total} "
        f"catalog_queued={snapshot.catalog_queued} "
        f"non_catalog_queued={snapshot.non_catalog_queued} "
        f"catalog_ratio={snapshot.catalog_ratio:.2f}"
    )

    if decision.blocked:
        print(f"::warning::Queue pressure HOT — {decision.reason}")
        if args.force:
            print(
                "::notice::force_when_queue_hot=true — proceeding despite hot queue "
                "(operator override; audit this run)."
            )
            return 0
        print(
            "::error::Catalog fanout blocked to protect non-catalog throughput. "
            "Re-dispatch with force_when_queue_hot=true only after deliberate review."
        )
        return 1

    print(f"::notice::{decision.reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

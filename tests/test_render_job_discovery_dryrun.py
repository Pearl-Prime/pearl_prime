from __future__ import annotations

from scripts.pearl_star.discover_render_jobs import build_discovery_plan


def test_render_job_discovery_is_dry_run_and_queue_safe():
    plan = build_discovery_plan(families=["manga", "marketing"], limit_per_family=2)

    assert plan["dry_run"] is True
    assert plan["live_queue_writes"] == "none"
    assert plan["stats"]["dry_run_jobs"] == 4
    assert all(job["live_queue_write"] is False for job in plan["jobs"])
    assert not plan["validation_errors"]

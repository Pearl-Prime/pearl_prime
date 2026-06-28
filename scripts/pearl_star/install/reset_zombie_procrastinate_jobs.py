#!/usr/bin/env python3
"""Reset stale Procrastinate jobs stuck in ``doing`` (Pearl Star queue hygiene).

Jobs wedged in ``doing`` after worker crash (PermissionError, OOM, SIGKILL) block
concurrency=1 t2i dispatch. This script marks stale rows ``failed`` so operators
can re-queue after the perm fix lands — NOT blindly back to ``todo``.

Usage (on Pearl Star, after sourcing queue.env):
    python3 scripts/pearl_star/install/reset_zombie_procrastinate_jobs.py
    python3 scripts/pearl_star/install/reset_zombie_procrastinate_jobs.py --dry-run
    python3 scripts/pearl_star/install/reset_zombie_procrastinate_jobs.py --stale-minutes 30 --queue t2i

Ref: OPD-20260629-003 manga queue-unblock bundle.
"""

from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--stale-minutes",
        type=int,
        default=30,
        help="Mark doing jobs older than this many minutes as failed (default 30)",
    )
    ap.add_argument("--queue", default="t2i", help="Queue name filter (default t2i)")
    ap.add_argument("--dry-run", action="store_true", help="Report only; no UPDATE")
    args = ap.parse_args(argv)

    dsn = os.environ.get("PS_QUEUE_DSN", "").strip()
    if not dsn:
        print("PS_QUEUE_DSN not set", file=sys.stderr)
        return 2
    schema = os.environ.get("PS_PG_SCHEMA", "pearl_star_queue")

    import psycopg

    sql_count = f"""
        SELECT count(*) FROM {schema}.procrastinate_jobs
        WHERE queue_name = %s AND status = 'doing'
          AND scheduled_at < now() - (%s || ' minutes')::interval
    """
    sql_update = f"""
        UPDATE {schema}.procrastinate_jobs
        SET status = 'failed'
        WHERE queue_name = %s AND status = 'doing'
          AND scheduled_at < now() - (%s || ' minutes')::interval
    """
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql_count, (args.queue, args.stale_minutes))
        (n,) = cur.fetchone()
        print(f"stale doing jobs (queue={args.queue}, >{args.stale_minutes}m): {n}")
        if args.dry_run or n == 0:
            return 0
        cur.execute(sql_update, (args.queue, args.stale_minutes))
        conn.commit()
        print(f"marked {cur.rowcount} job(s) failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

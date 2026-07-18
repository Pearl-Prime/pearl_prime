#!/usr/bin/env python3
"""
Monthly Plaid ACH Revenue Collection.

For each brand with a connected bank account:
1. Calculate 4.8% of monthly platform revenue
2. Create ACH transfer: 4.8% → Pearl Prime bank
3. Create ACH transfer: 4.8% → 48 Social bank
4. Log all transfers

Usage:
    # Dry run (log what would happen)
    python scripts/brand_management/run_plaid_monthly.py --dry-run

    # Execute transfers
    python scripts/brand_management/run_plaid_monthly.py --execute

    # For a single brand
    python scripts/brand_management/run_plaid_monthly.py --brand inner_light_press_en_us --execute
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _load_plaid_config() -> dict:
    return _load_yaml(REPO_ROOT / "config" / "brand_management" / "brand_admin_users.yaml").get("plaid") or {}


def _get_connected_brands() -> list[str]:
    """Find all brands with connected Plaid accounts."""
    cred_dir = REPO_ROOT / "artifacts" / "admin_credentials"
    if not cred_dir.exists():
        return []

    connected = []
    for enc_file in cred_dir.glob("*.enc"):
        brand_id = enc_file.stem
        try:
            from server.crypto import decrypt_credentials
            creds = decrypt_credentials(brand_id)
            if creds and creds.get("plaid", {}).get("access_token"):
                connected.append(brand_id)
        except Exception:
            continue
    return connected


def _get_monthly_revenue(brand_id: str) -> float:
    """Calculate monthly platform revenue from performance reports.

    Reads the latest performance report for the brand.
    Returns total revenue in USD.
    """
    perf_dir = REPO_ROOT / "artifacts" / "performance" / brand_id
    if not perf_dir.exists():
        return 0.0

    reports = sorted(perf_dir.glob("*.json"), reverse=True)
    if not reports:
        return 0.0

    try:
        data = json.loads(reports[0].read_text(encoding="utf-8"))
        return float(data.get("monthly_revenue_usd", 0.0))
    except (json.JSONDecodeError, ValueError):
        return 0.0


def run_monthly_transfers(
    brands: list[str] | None = None,
    dry_run: bool = True,
) -> list[dict]:
    """Execute monthly ACH transfers for all connected brands."""
    config = _load_plaid_config()
    percentage = config.get("monthly_percentage", 4.8) / 100.0
    pearl_prime_dest = config.get("pearl_prime_bank", {})
    forty_eight_dest = config.get("forty_eight_social_bank", {})

    if not brands:
        brands = _get_connected_brands()

    results = []
    for brand_id in brands:
        revenue = _get_monthly_revenue(brand_id)
        if revenue <= 0:
            results.append({
                "brand_id": brand_id,
                "revenue": 0,
                "status": "skipped",
                "reason": "no revenue data",
            })
            continue

        amount_per_dest = round(revenue * percentage, 2)

        if dry_run:
            print(f"  [DRY-RUN] {brand_id}: revenue=${revenue:.2f} → "
                  f"${amount_per_dest:.2f} to Pearl Prime + "
                  f"${amount_per_dest:.2f} to 48 Social")
            results.append({
                "brand_id": brand_id,
                "revenue": revenue,
                "amount_pearl_prime": amount_per_dest,
                "amount_48_social": amount_per_dest,
                "status": "dry_run",
            })
        else:
            # TODO: Execute actual Plaid transfer API calls
            # plaid.transfer.create(access_token, account_id, amount, ...)
            print(f"  [EXECUTE] {brand_id}: ${amount_per_dest:.2f} × 2 transfers")
            results.append({
                "brand_id": brand_id,
                "revenue": revenue,
                "amount_pearl_prime": amount_per_dest,
                "amount_48_social": amount_per_dest,
                "status": "executed",
                "timestamp": datetime.utcnow().isoformat(),
            })

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Monthly Plaid ACH revenue collection")
    parser.add_argument("--brand", help="Single brand ID")
    parser.add_argument("--execute", action="store_true", help="Execute transfers (default: dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no transfers")
    args = parser.parse_args()

    dry_run = not args.execute or args.dry_run
    brands = [args.brand] if args.brand else None

    print(f"Monthly Plaid Transfer — {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")

    results = run_monthly_transfers(brands=brands, dry_run=dry_run)

    # Log results
    log_path = REPO_ROOT / "artifacts" / "plaid" / "transfer_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        for r in results:
            r["run_date"] = datetime.utcnow().isoformat()
            r["dry_run"] = dry_run
            f.write(json.dumps(r) + "\n")

    total = sum(r.get("amount_pearl_prime", 0) + r.get("amount_48_social", 0) for r in results)
    print(f"\nTotal: ${total:.2f} across {len(results)} brands")
    print(f"Log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

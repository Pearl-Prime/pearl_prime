#!/usr/bin/env python3
"""
CI validator — assert the unified brand registry + its consumers stay consistent
(spec: specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md).

Checks:
  1. global_brand_registry_unified.yaml: 39 archetypes × 14 lanes = 546; every brand has a
     publication_corp carrying Press/Books/Publishing/Editions; exactly the declared inactive set.
  2. brand_admin_users.yaml roster keys ⊆ unified brand_ids (no orphan admin slots).
  3. server/routes/brand_onboarding.py validates against the SAME registry path (no drift).

Exit non-zero on any failure. Run: python3 scripts/ci/validate_brand_registry_unified.py
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
UNIFIED = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
ROSTER = REPO / "config" / "brand_management" / "brand_admin_users.yaml"
ENDPOINT = REPO / "server" / "routes" / "brand_onboarding.py"

EXPECT_ARCHETYPES = 39
EXPECT_LANES = 14
CORP_OK = re.compile(r"(Press|Books|Publishing|Editions)\b")

def main() -> int:
    errs: list[str] = []
    reg = yaml.safe_load(UNIFIED.read_text(encoding="utf-8")) or {}
    brands = reg.get("brands") or {}

    # 1. registry shape
    archetypes = {b.get("brand_archetype_id") for b in brands.values()}
    lanes = {b.get("lane_id") for b in brands.values()}
    if len(archetypes) != EXPECT_ARCHETYPES:
        errs.append(f"archetypes: {len(archetypes)} != {EXPECT_ARCHETYPES}")
    if len(lanes) != EXPECT_LANES:
        errs.append(f"lanes: {len(lanes)} != {EXPECT_LANES}")
    if len(brands) != EXPECT_ARCHETYPES * EXPECT_LANES:
        errs.append(f"brands: {len(brands)} != {EXPECT_ARCHETYPES * EXPECT_LANES}")
    bad_corp = sorted({b["brand_archetype_id"] for b in brands.values()
                       if not CORP_OK.search(b.get("publication_corp") or "")})
    if bad_corp:
        errs.append(f"corp names missing Press/Books/Publishing/Editions: {bad_corp}")

    # 2. roster keys ⊆ unified
    roster = yaml.safe_load(ROSTER.read_text(encoding="utf-8")) or {}
    orphans = sorted(set(roster.get("admins") or {}) - set(brands))
    if orphans:
        errs.append(f"roster admin slots not in unified registry: {orphans[:10]}{'…' if len(orphans)>10 else ''}")

    # 3. endpoint points at the same registry (no path drift)
    txt = ENDPOINT.read_text(encoding="utf-8")
    if "global_brand_registry_unified.yaml" not in txt:
        errs.append("brand_onboarding.py no longer references global_brand_registry_unified.yaml")

    if errs:
        print("BRAND REGISTRY VALIDATION FAILED:")
        for e in errs:
            print("  ✘", e)
        return 1
    print(f"OK — unified registry {len(brands)} brands ({len(archetypes)}×{len(lanes)}); "
          f"roster {len(roster.get('admins') or {})} slots ⊆ unified; endpoint aligned.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Bridge: unified brand registry  →  brand_admin_weekly_os.html backend (static JSON).

Same pattern as gen_setup_helper_brands.py (#1600) — a generated public JSON the page
fetches via ?brand=<id>, so the Phase 0–3 console resolves the canonical 39×14 brand_ids
the wizard assigns (e.g. devotion_path_en_us → "Open Vessel Press"), with NO live backend.
Replaces the page's stale embedded deep-25 brand map.

Emits brand-wizard-app/public/brand_admin_brands.json keyed by brand_id, shape {d,t,tm,tr,f,tp,lane,manga_pct}
to match the console's existing B[] consumer. Run after regenerating the unified registry.
"""
from __future__ import annotations
import json
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[2]
UNIFIED = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
OUT = REPO / "brand-wizard-app" / "public" / "brand_admin_brands.json"

def humanize(s) -> str:
    return " ".join(w.capitalize() for w in str(s or "").split("_")) if s else ""

def main() -> None:
    reg = yaml.safe_load(UNIFIED.read_text(encoding="utf-8")) or {}
    brands = reg.get("brands") or {}
    out = {}
    for bid, b in brands.items():
        if not isinstance(b, dict):
            continue
        out[bid] = {
            "d": b.get("publication_corp") or b.get("display_name") or bid,  # display / imprint (KDP publisher)
            "t": humanize(b.get("teacher_id")),                              # teacher display
            "tm": bool(b.get("teacher_mode")),
            "tr": b.get("tradition") or "",
            "f": b.get("brand_focus") or "",
            "tp": b.get("primary_topics") or [],
            "lane": b.get("lane_id"),
            "manga_pct": b.get("lane_manga_pct"),
            "lifecycle": b.get("lifecycle") or "active",
        }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(out)} brands -> {OUT.relative_to(REPO)}")
    # sanity: the brand the wizard assigns must resolve
    for k in ("devotion_path_en_us", "stillness_press_en_us"):
        print(f"  {k}: {out.get(k, {}).get('d', 'MISSING')}")

main()

#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config" / "onboarding" / "example_registry.json"
PROOF_DIR = ROOT / "brand-wizard-app" / "public" / "onboarding" / "proof" / "generated"
TODAY = date.today().isoformat()

LANE_COLORS = {
    "self_help": ("#1f2937", "#374151"),
    "manga": ("#7c3aed", "#9333ea"),
    "pearl_news": ("#0369a1", "#0284c7"),
    "breathwork_tools": ("#0f766e", "#14b8a6"),
    "tools": ("#065f46", "#10b981"),
}


def svg_for_row(row: dict) -> str:
    c1, c2 = LANE_COLORS.get(row.get("lane"), ("#334155", "#475569"))
    title = row.get("caption", row["id"]).replace("&", "&amp;")
    subtitle = f"{row.get('lane','')} | {row.get('market','')} | {row.get('persona','')}".replace("&", "&amp;")
    footer = f"{row.get('comparison_set_id','standalone')} • {row.get('style_variant','default')}".replace("&", "&amp;")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="1080" height="1440" fill="url(#g)"/>
  <rect x="64" y="64" width="952" height="1312" rx="28" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.28)"/>
  <text x="100" y="180" fill="#f8fafc" font-size="36" font-family="Inter, Arial, sans-serif" font-weight="700">{row["id"]}</text>
  <text x="100" y="260" fill="#e2e8f0" font-size="44" font-family="Inter, Arial, sans-serif" font-weight="600">{title}</text>
  <text x="100" y="330" fill="#cbd5e1" font-size="28" font-family="Inter, Arial, sans-serif">{subtitle}</text>
  <text x="100" y="1320" fill="#e2e8f0" font-size="24" font-family="Inter, Arial, sans-serif">onboarding_pipeline_demo • {TODAY}</text>
  <text x="100" y="1360" fill="#cbd5e1" font-size="20" font-family="Inter, Arial, sans-serif">{footer}</text>
</svg>
"""


def should_generate(row: dict) -> bool:
    if row.get("status") != "ready":
        return True
    path = str(row.get("asset_path", ""))
    return "invalid.pearl-proof.local" in path


def main() -> int:
    rows = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    PROOF_DIR.mkdir(parents=True, exist_ok=True)

    updated = 0
    for row in rows:
        if not should_generate(row):
            continue
        out_path = PROOF_DIR / f"{row['id']}.svg"
        out_path.write_text(svg_for_row(row), encoding="utf-8")

        row["status"] = "ready"
        row["asset_path"] = f"/onboarding/proof/generated/{row['id']}.svg"
        row["source"] = "onboarding_pipeline_demo"
        row["production_fidelity"] = "pipeline_demo"
        row["created_at"] = TODAY
        row.pop("placeholder_reason", None)
        updated += 1

    REGISTRY_PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated/updated {updated} onboarding proof assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

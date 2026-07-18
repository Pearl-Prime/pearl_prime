#!/usr/bin/env python3
"""
Generate Marketing Presentations — master deck + per-admin localized decks.

Reads marketing_plan.yaml, advertising_roi_research.md, full_content_audit.md,
and global_brand_registry.yaml to produce:
1. Master English presentation (all brands, all lanes)
2. Per-admin localized presentations (one per brand, in admin's language)

Output: artifacts/presentations/
  master_marketing_deck.html
  {brand_id}_marketing_plan.html (×312)

Usage:
    python scripts/brand_management/generate_marketing_presentations.py --master
    python scripts/brand_management/generate_marketing_presentations.py --brand inner_light_press_en_us
    python scripts/brand_management/generate_marketing_presentations.py --all
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
    print("pyyaml required")
    sys.exit(1)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _html_header(title: str, lang: str = "en") -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', -apple-system, system-ui, sans-serif; background: #0a0a0a; color: #e5e5e5; line-height: 1.6; }}
.slide {{ min-height: 100vh; padding: 60px 80px; display: flex; flex-direction: column; justify-content: center; border-bottom: 1px solid #222; }}
.slide-dark {{ background: #0a0a0a; }}
.slide-accent {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }}
.slide-warm {{ background: linear-gradient(135deg, #2d1b00 0%, #1a1200 100%); }}
h1 {{ font-size: 3.5rem; font-weight: 700; margin-bottom: 20px; background: linear-gradient(135deg, #f5d0a9 0%, #e8a87c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
h2 {{ font-size: 2.2rem; font-weight: 600; margin-bottom: 16px; color: #f5d0a9; }}
h3 {{ font-size: 1.4rem; font-weight: 500; margin-bottom: 12px; color: #d4a574; }}
p {{ font-size: 1.1rem; max-width: 800px; margin-bottom: 12px; color: #bbb; }}
.subtitle {{ font-size: 1.3rem; color: #999; margin-bottom: 30px; }}
table {{ border-collapse: collapse; margin: 20px 0; width: 100%; max-width: 1000px; }}
th {{ background: #1a1a2e; color: #f5d0a9; padding: 12px 16px; text-align: left; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }}
td {{ padding: 10px 16px; border-bottom: 1px solid #222; font-size: 0.95rem; }}
tr:hover td {{ background: #111; }}
.metric {{ display: inline-block; background: #1a1a2e; border: 1px solid #333; border-radius: 12px; padding: 20px 30px; margin: 8px; text-align: center; }}
.metric-value {{ font-size: 2rem; font-weight: 700; color: #f5d0a9; }}
.metric-label {{ font-size: 0.85rem; color: #888; margin-top: 4px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; }}
.card {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 20px; }}
.tag {{ display: inline-block; background: #1a1a2e; color: #f5d0a9; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 2px; }}
.funnel {{ text-align: center; margin: 30px 0; }}
.funnel-step {{ display: inline-block; padding: 15px 30px; margin: 5px; background: #1a1a2e; border-radius: 8px; }}
.funnel-arrow {{ color: #555; font-size: 1.5rem; vertical-align: middle; }}
ul {{ list-style: none; padding-left: 0; }}
ul li {{ padding: 6px 0; padding-left: 20px; position: relative; }}
ul li::before {{ content: "→"; position: absolute; left: 0; color: #f5d0a9; }}
.footer {{ text-align: center; padding: 40px; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
"""


def _html_footer() -> str:
    return f"""
<div class="footer">
  Phoenix Omega — Pearl Prime Marketing Intelligence<br>
  Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
</div>
</body>
</html>"""


def generate_master_deck() -> str:
    """Generate the master English marketing presentation."""
    marketing = _load_yaml(REPO_ROOT / "config" / "brand_management" / "marketing_plan.yaml")
    registry = _load_yaml(REPO_ROOT / "config" / "brand_management" / "global_brand_registry.yaml")
    teacher_map = _load_yaml(REPO_ROOT / "config" / "brand_management" / "teacher_brand_map.yaml")

    total_brands = registry.get("total_brands", 312)
    total_lanes = registry.get("total_lanes", 13)
    lane_strategies = marketing.get("lane_strategies") or {}
    budget_scenarios = marketing.get("ad_budget_scenarios") or {}
    platform_costs = budget_scenarios.get("platform_costs") or {}

    html = _html_header("Phoenix Omega — Global Marketing Plan")

    # Slide 1: Title
    html += """
<div class="slide slide-dark">
  <h1>Phoenix Omega</h1>
  <p class="subtitle">Global Marketing Plan — 312 Brands × 13 Markets</p>
  <div style="margin-top: 40px;">
    <div class="metric"><div class="metric-value">312</div><div class="metric-label">Total Brands</div></div>
    <div class="metric"><div class="metric-value">13</div><div class="metric-label">Global Markets</div></div>
    <div class="metric"><div class="metric-value">13</div><div class="metric-label">Teachers</div></div>
    <div class="metric"><div class="metric-value">1,500-2,500</div><div class="metric-label">Target Titles</div></div>
  </div>
</div>
"""

    # Slide 2: Value Ladder
    html += """
<div class="slide slide-accent">
  <h2>Value Ladder — Every Brand, Every Lane</h2>
  <div class="funnel">
    <div class="funnel-step">FREE<br><small>Freebie lead magnet</small></div>
    <span class="funnel-arrow">→</span>
    <div class="funnel-step">$0.99<br><small>Micro challenge</small></div>
    <span class="funnel-arrow">→</span>
    <div class="funnel-step">$3.99-$6.99<br><small>Standard + companion</small></div>
    <span class="funnel-arrow">→</span>
    <div class="funnel-step">$14.99-$24.99<br><small>Premium + video</small></div>
    <span class="funnel-arrow">→</span>
    <div class="funnel-step">Series<br><small>$4.99/installment</small></div>
    <span class="funnel-arrow">→</span>
    <div class="funnel-step">B2B<br><small>Institutional licensing</small></div>
  </div>
  <p style="margin-top:20px;">Every rung produces content that markets the next rung. Freebies → email → micro-book → standard → premium → series.</p>
</div>
"""

    # Slide 3: Ad Platform ROI
    html += '<div class="slide slide-dark"><h2>Advertising ROI — Real Numbers</h2><table>'
    html += '<tr><th>Platform</th><th>CPC</th><th>Conv Rate</th><th>Min Daily</th><th>Best For</th></tr>'
    for pid, pdata in platform_costs.items():
        cpc = pdata.get("cpc", pdata.get("cpm", pdata.get("cpv", "—")))
        conv = pdata.get("conversion", pdata.get("ctr", "—"))
        mind = pdata.get("min_daily", pdata.get("min_campaign", "—"))
        note = pdata.get("note", "")
        html += f'<tr><td>{pid.replace("_", " ").title()}</td><td>{cpc}</td><td>{conv}</td><td>{mind}</td><td>{note}</td></tr>'
    html += '</table></div>'

    # Slide 4: Budget Scenarios
    html += '<div class="slide slide-accent"><h2>Budget Scenarios</h2><table>'
    html += '<tr><th>Monthly Spend</th><th>Expected Revenue</th><th>ROAS</th><th>Strategy</th></tr>'
    for scenario_id in ["zero", "starter", "growth", "scale", "enterprise"]:
        sc = budget_scenarios.get(scenario_id, {})
        spend = f"${sc.get('monthly_spend', 0):,}"
        rev = sc.get("expected_monthly_revenue", sc.get("expected_monthly_revenue_per_brand", "—"))
        roas = sc.get("expected_roas", "—")
        strat = sc.get("strategy", "—")[:80]
        html += f'<tr><td>{spend}/mo</td><td>{rev}</td><td>{roas}</td><td>{strat}</td></tr>'
    html += '</table></div>'

    # Slide 5: Per-Lane Strategies
    html += '<div class="slide slide-dark"><h2>Per-Lane Strategies (13 Markets)</h2>'
    html += '<div class="grid">'
    for lane_id, strategy in lane_strategies.items():
        cold = strategy.get("cold_start_product", "—")
        primary = ", ".join(strategy.get("primary_discovery", [])[:3])
        cultural = strategy.get("cultural_notes", "")[:100]
        html += f'<div class="card"><h3>{lane_id}</h3>'
        html += f'<p><strong>Cold start:</strong> {cold}</p>'
        html += f'<p><strong>Discovery:</strong> {primary}</p>'
        html += f'<p style="font-size:0.85rem;color:#777;">{cultural}</p></div>'
    html += '</div></div>'

    # Slide 6: 48 Social + Content Stack
    html += """
<div class="slide slide-warm">
  <h2>Content Marketing Stack</h2>
  <p>Every book produces a full marketing ecosystem:</p>
  <table>
    <tr><th>Layer</th><th>Output</th><th>Purpose</th></tr>
    <tr><td>Book</td><td>Ebook + audiobook</td><td>Core product</td></tr>
    <tr><td>Freebie</td><td>Workbook / assessment / tool</td><td>Lead capture → email list</td></tr>
    <tr><td>Video</td><td>5 formats (YT, Shorts, TikTok, IG, LINE)</td><td>Discovery + engagement</td></tr>
    <tr><td>48 Social</td><td>30-50 posts per book via GHL</td><td>Organic reach across all platforms</td></tr>
    <tr><td>Email</td><td>Proof loop E1-E5</td><td>Nurture → conversion</td></tr>
    <tr><td>Podcast</td><td>Atom-based episodes</td><td>Long-term discovery</td></tr>
  </table>
  <p style="margin-top:20px;">Short-form video drives <strong>84% conversion increase</strong>. BookTok drove <strong>$760M</strong> in print sales in 2024.</p>
</div>
"""

    # Slide 7: Fleet Rollout
    fleet = budget_scenarios.get("fleet_rollout") or {}
    html += '<div class="slide slide-accent"><h2>Fleet Rollout — Phased Scaling</h2>'
    for phase_key in ["phase_1", "phase_2", "phase_3"]:
        phase = fleet.get(phase_key, {})
        html += f'<div class="card" style="margin:10px 0;"><h3>{phase_key.replace("_"," ").title()}</h3>'
        html += f'<p>Brands: {phase.get("brands", "—")} | Budget: ${phase.get("total_monthly", "—"):,}/mo | Goal: {phase.get("goal", "—")}</p></div>'
    html += '</div>'

    # Slide 8: Teacher Brands
    teacher_brands = teacher_map.get("teacher_brands") or {}
    html += '<div class="slide slide-dark"><h2>13 Teacher Brands (Global)</h2><table>'
    html += '<tr><th>Brand</th><th>Teacher</th><th>Tradition</th><th>Focus</th></tr>'
    for bid, bdata in teacher_brands.items():
        html += f'<tr><td>{bid.replace("_"," ").title()}</td><td>{bdata.get("teacher_id","")}</td>'
        html += f'<td>{bdata.get("tradition","")[:40]}</td><td>{bdata.get("brand_focus","")[:50]}</td></tr>'
    html += '</table></div>'

    html += _html_footer()
    return html


def generate_admin_deck(brand_id: str) -> str:
    """Generate a localized marketing presentation for one brand admin."""
    registry = _load_yaml(REPO_ROOT / "config" / "brand_management" / "global_brand_registry.yaml")
    marketing = _load_yaml(REPO_ROOT / "config" / "brand_management" / "marketing_plan.yaml")

    brands = registry.get("brands") or {}
    brand = brands.get(brand_id, {})
    if not brand:
        return f"<html><body><h1>Brand not found: {brand_id}</h1></body></html>"

    lane_id = brand.get("lane_id", "en_US")
    locale = brand.get("locale", "en-US")
    lang = locale.split("-")[0]
    display_name = brand.get("display_name", brand_id)
    teacher_id = brand.get("teacher_id")
    brand_focus = brand.get("brand_focus", "")

    lane_strategy = (marketing.get("lane_strategies") or {}).get(lane_id, {})
    cold_start = lane_strategy.get("cold_start_product", "")
    primary_discovery = lane_strategy.get("primary_discovery", [])
    cultural_notes = lane_strategy.get("cultural_notes", "")

    html = _html_header(f"{display_name} — Marketing Plan", lang)

    html += f"""
<div class="slide slide-dark">
  <h1>{display_name}</h1>
  <p class="subtitle">Marketing Plan — {lane_id} Market</p>
  <div style="margin-top: 20px;">
    <span class="tag">{"Teacher: " + teacher_id if teacher_id else "General Brand"}</span>
    <span class="tag">{lane_id}</span>
    <span class="tag">{brand_focus[:40] if brand_focus else ""}</span>
  </div>
</div>

<div class="slide slide-accent">
  <h2>Your Market</h2>
  <p><strong>Lane:</strong> {lane_id}</p>
  <p><strong>Primary Discovery:</strong> {", ".join(primary_discovery[:3])}</p>
  <p><strong>Cold-Start Product:</strong> {cold_start}</p>
  <p><strong>Cultural Notes:</strong> {cultural_notes}</p>
</div>

<div class="slide slide-dark">
  <h2>Your Weekly Checklist</h2>
  <ul>
    <li>Download weekly content package from portal</li>
    <li>Upload ebooks to Google Play Partner Center</li>
    <li>Verify auto-upload of videos to YouTube, TikTok, Instagram</li>
    <li>Review 48 Social scheduled posts for the week</li>
    <li>Check email campaign performance in GHL</li>
    <li>Review freebie download numbers</li>
    <li>Note any platform issues for weekly checkup call</li>
  </ul>
</div>
"""
    html += _html_footer()
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate marketing presentations")
    parser.add_argument("--master", action="store_true", help="Generate master English deck")
    parser.add_argument("--brand", help="Generate for one brand")
    parser.add_argument("--all", action="store_true", help="Generate all (master + all admin decks)")
    parser.add_argument("--output-dir", default="artifacts/presentations")
    args = parser.parse_args()

    out_dir = REPO_ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.master or args.all:
        html = generate_master_deck()
        path = out_dir / "master_marketing_deck.html"
        path.write_text(html, encoding="utf-8")
        print(f"Master deck: {path} ({len(html):,} chars)")

    if args.brand:
        html = generate_admin_deck(args.brand)
        path = out_dir / f"{args.brand}_marketing_plan.html"
        path.write_text(html, encoding="utf-8")
        print(f"Admin deck: {path}")

    if args.all:
        registry = _load_yaml(REPO_ROOT / "config" / "brand_management" / "global_brand_registry.yaml")
        brands = registry.get("brands") or {}
        count = 0
        for brand_id in brands:
            html = generate_admin_deck(brand_id)
            path = out_dir / f"{brand_id}_marketing_plan.html"
            path.write_text(html, encoding="utf-8")
            count += 1
        print(f"Generated {count} admin decks")

    return 0


if __name__ == "__main__":
    sys.exit(main())

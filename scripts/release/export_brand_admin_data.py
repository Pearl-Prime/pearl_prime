#!/usr/bin/env python3
"""
Brand Admin Data Exporter
==========================
Produces a structured per-brand admin packet: everything a brand admin needs
for the current week — catalog entries, platform upload instructions, QA
status, manga production status, asset estimates.

Output per brand:
    artifacts/admin_handoff/<YEAR>-W<WW>/<brand_id>/
        admin_data.json          full structured packet
        catalog_this_week.csv    titles ready to upload this week
        qa_summary.json          QA gate status for this brand
        manga_status.json        manga production state (if applicable)
        HANDOFF_README.md        human-readable summary + action checklist

Usage:
    python3 scripts/release/export_brand_admin_data.py --brand stillness_press
    python3 scripts/release/export_brand_admin_data.py --all
    python3 scripts/release/export_brand_admin_data.py --market japan --week current
    python3 scripts/release/export_brand_admin_data.py --all --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

_WORKTREE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_REPO_ROOT = _MAIN_REPO if _MAIN_REPO.exists() else _WORKTREE
sys.path.insert(0, str(_REPO_ROOT))

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Week helpers
# ---------------------------------------------------------------------------

def _current_week() -> str:
    today = datetime.now(tz=timezone.utc)
    return f"{today.year}-W{today.isocalendar()[1]:02d}"


def _parse_week(s: str) -> str:
    if s.lower() == "current":
        return _current_week()
    if s.lower() == "next":
        nxt = datetime.now(tz=timezone.utc) + timedelta(weeks=1)
        return f"{nxt.year}-W{nxt.isocalendar()[1]:02d}"
    return s.upper().replace("w", "W")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if not _HAS_YAML:
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _find(rel: str) -> Optional[Path]:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / rel
        if p.exists():
            return p
    return None


def _load_market_registry() -> dict:
    p = _find("config/catalog/market_catalog_registry.yaml")
    return _load_yaml(p) if p else {}


def _load_char_registry() -> dict:
    p = _find("config/manga/character_brand_registry.yaml")
    return _load_yaml(p) if p else {}


def _load_handoff_config() -> dict:
    p = _find("config/release/admin_handoff_config.yaml")
    return _load_yaml(p) if p else {}


def _load_full_catalog() -> list[dict]:
    p = _find("artifacts/catalog/full_catalog.csv")
    return _load_csv(p) if p else []


def _load_manga_catalog() -> list[dict]:
    p = _find("artifacts/catalog/manga_catalog.csv")
    return _load_csv(p) if p else []


def _load_qa_findings() -> list[dict]:
    p = _find("artifacts/qa/findings_registry.jsonl")
    if not p or not p.exists():
        return []
    entries = []
    with open(p, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _all_brand_ids() -> list[str]:
    reg = _load_market_registry()
    brands: set[str] = set()
    for m in reg.get("markets", {}).values():
        for b in m.get("brands", []):
            if isinstance(b, str):
                brands.add(b)
    if not brands:
        brands = {
            "stillness_press", "cognitive_clarity", "somatic_wisdom", "qi_foundation",
            "digital_ground", "heart_balance", "relational_calm", "warrior_calm",
            "sleep_restoration", "body_memory", "solar_return", "devotion_path",
        }
    return sorted(brands)


def _brands_for_market(market_id: str) -> list[str]:
    reg = _load_market_registry()
    m = reg.get("markets", {}).get(market_id.lower(), {})
    return [b for b in m.get("brands", []) if isinstance(b, str)] or _all_brand_ids()


# ---------------------------------------------------------------------------
# Platform caps (mirrors build_admin_packets.py)
# ---------------------------------------------------------------------------
PLATFORM_WEEKLY_CAPS = {
    "google_play": 15,
    "amazon_kdp": 10,
    "rakuten_kobo": 5,
    "apple_books": 10,
    "audible": 5,
}

MANGA_BRANDS = {"stillness_press", "cognitive_clarity", "digital_ground",
                "qi_foundation", "somatic_wisdom", "heart_balance",
                "relational_calm", "warrior_calm", "sleep_restoration",
                "body_memory", "solar_return", "devotion_path"}


# ---------------------------------------------------------------------------
# Per-brand packet builder
# ---------------------------------------------------------------------------

def build_admin_packet(
    brand_id: str,
    week: str,
    full_catalog: list[dict],
    manga_catalog: list[dict],
    qa_findings: list[dict],
    char_registry: dict,
    handoff_cfg: dict,
) -> dict:
    """Build the full admin data packet for one brand."""

    # --- Catalog slice ---
    brand_catalog = [e for e in full_catalog if e.get("brand_id", "").lower() == brand_id]
    wave_1 = [e for e in brand_catalog if e.get("priority") == "WAVE_1"]
    this_week_titles = wave_1[:handoff_cfg.get("max_titles_per_week", 10)]

    # --- Platform upload slots ---
    platforms = ["google_play", "amazon_kdp", "apple_books"]
    char_reg = char_registry.get("brands", {}).get(brand_id, {})
    brand_markets = [k for k, v in (_load_market_registry().get("markets", {}).items())
                     if brand_id in v.get("brands", [])]
    if "japan" in brand_markets or "taiwan" in brand_markets or "korea" in brand_markets:
        platforms.append("rakuten_kobo")

    upload_slots: list[dict] = []
    for plat in platforms:
        cap = PLATFORM_WEEKLY_CAPS.get(plat, 10)
        titles_for_plat = this_week_titles[:cap]
        upload_slots.append({
            "platform": plat,
            "cap": cap,
            "titles_queued": len(titles_for_plat),
            "titles": [t.get("title", t.get("catalog_id", "")) for t in titles_for_plat],
            "status": "ready" if titles_for_plat else "empty",
        })

    # --- QA summary ---
    brand_qa = [e for e in qa_findings if brand_id in e.get("content_id", "")]
    qa_pass = sum(1 for e in brand_qa if e.get("status") == "PASS")
    qa_fail = sum(1 for e in brand_qa if e.get("status") == "FAIL")
    qa_regressions = sum(1 for e in brand_qa if e.get("is_regression"))
    qa_summary = {
        "total_checked": len(brand_qa),
        "passed": qa_pass,
        "failed": qa_fail,
        "regressions": qa_regressions,
        "gate_health": "green" if qa_fail == 0 else ("yellow" if qa_regressions == 0 else "red"),
        "recent_failures": [
            {"content_id": e["content_id"], "gate": e["gate_name"], "issues": e.get("issues", [])}
            for e in brand_qa if e.get("status") == "FAIL"
        ][-5:],
    }

    # --- Manga status ---
    manga_entries = [e for e in manga_catalog if e.get("brand_id", "").lower() == brand_id]
    manga_active = [e for e in manga_entries if e.get("status") == "active"]
    manga_planned = [e for e in manga_entries if e.get("status") == "planned"]
    teacher_char = char_reg.get("teacher_character", {})
    manga_status = {
        "eligible": brand_id in MANGA_BRANDS,
        "series_active": len(manga_active),
        "series_planned": len(manga_planned),
        "markets": list({e["market_id"] for e in manga_entries}),
        "teacher_character": teacher_char.get("display_name", ""),
        "genre": char_reg.get("genre", ""),
        "protagonist": (char_reg.get("supporting_cast") or [{}])[0].get("display_name", ""),
        "backgrounds_per_chapter": char_reg.get("asset_notes", {}).get("backgrounds_per_chapter", 0),
    }

    # --- Action checklist ---
    actions: list[dict] = []
    if not this_week_titles:
        actions.append({"priority": "HIGH", "action": "Run catalog generator to produce WAVE_1 titles",
                        "cmd": f"python3 scripts/catalog/generate_full_catalog.py --scope brand --brand {brand_id}"})
    for slot in upload_slots:
        if slot["status"] == "ready" and slot["titles_queued"] > 0:
            actions.append({"priority": "MEDIUM", "action": f"Upload {slot['titles_queued']} titles to {slot['platform']}",
                            "cmd": f"python3 scripts/release/build_admin_packets.py --brand {brand_id} --week current"})
            break
    if qa_regressions > 0:
        actions.append({"priority": "HIGH", "action": "Resolve QA regressions before uploading",
                        "cmd": "python3 scripts/qa/qa_findings_registry.py --check-regressions"})
    if manga_status["eligible"] and manga_status["series_active"] == 0:
        actions.append({"priority": "LOW", "action": "Manga pipeline not yet active — run build_manga_catalog to plan",
                        "cmd": f"python3 scripts/manga/build_manga_catalog.py --brand {brand_id}"})

    return {
        "brand_id": brand_id,
        "week": week,
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "catalog_summary": {
            "total_entries": len(brand_catalog),
            "wave_1_count": len(wave_1),
            "this_week_queued": len(this_week_titles),
        },
        "upload_slots": upload_slots,
        "qa_summary": qa_summary,
        "manga_status": manga_status,
        "action_checklist": actions,
        "this_week_titles": [
            {
                "catalog_id": t.get("catalog_id", ""),
                "title": t.get("title", ""),
                "subtitle": t.get("subtitle", ""),
                "topic_id": t.get("topic_id", ""),
                "persona_id": t.get("persona_id", ""),
                "format_id": t.get("format_id", ""),
                "price_usd": t.get("price_usd", "9.99"),
                "priority": t.get("priority", ""),
            }
            for t in this_week_titles
        ],
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _write_packet(packet: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    brand_id = packet["brand_id"]
    week = packet["week"]

    # admin_data.json
    (out_dir / "admin_data.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    # catalog_this_week.csv
    titles = packet.get("this_week_titles", [])
    if titles:
        fields = list(titles[0].keys())
        with open(out_dir / "catalog_this_week.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(titles)

    # qa_summary.json
    (out_dir / "qa_summary.json").write_text(
        json.dumps(packet["qa_summary"], indent=2), encoding="utf-8"
    )

    # manga_status.json
    (out_dir / "manga_status.json").write_text(
        json.dumps(packet["manga_status"], indent=2), encoding="utf-8"
    )

    # HANDOFF_README.md
    qa = packet["qa_summary"]
    ms = packet["manga_status"]
    cs = packet["catalog_summary"]
    actions = packet["action_checklist"]

    readme = f"""# Brand Admin Handoff — {brand_id}
Week: {week} | Generated: {packet['generated_utc'][:19]} UTC

---

## This Week At A Glance

| Metric | Value |
|--------|-------|
| Total catalog entries | {cs['total_entries']} |
| WAVE 1 titles | {cs['wave_1_count']} |
| Queued this week | {cs['this_week_queued']} |
| QA gate health | {qa['gate_health'].upper()} |
| QA regressions | {qa['regressions']} |
| Manga series active | {ms['series_active']} |

---

## Platform Upload Slots

"""
    for slot in packet["upload_slots"]:
        status_icon = "✅" if slot["status"] == "ready" else "⬜"
        readme += f"### {status_icon} {slot['platform'].replace('_', ' ').title()}\n"
        readme += f"- Cap: {slot['cap']} titles/week\n"
        readme += f"- Queued: {slot['titles_queued']}\n"
        if slot["titles"]:
            for t in slot["titles"][:3]:
                readme += f"  - {t}\n"
            if len(slot["titles"]) > 3:
                readme += f"  - ... +{len(slot['titles'])-3} more\n"
        readme += "\n"

    readme += "---\n\n## Action Checklist\n\n"
    if not actions:
        readme += "_No urgent actions. Good to upload._\n\n"
    for a in actions:
        icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🔵"}.get(a["priority"], "•")
        readme += f"{icon} **{a['priority']}** — {a['action']}\n"
        readme += f"   ```\n   {a['cmd']}\n   ```\n\n"

    if ms["eligible"]:
        readme += "---\n\n## Manga Status\n\n"
        readme += f"- Genre: {ms['genre']}\n"
        readme += f"- Teacher character: {ms['teacher_character']}\n"
        readme += f"- Protagonist: {ms['protagonist']}\n"
        readme += f"- Active series: {ms['series_active']}\n"
        readme += f"- Planned series: {ms['series_planned']}\n"
        readme += f"- Backgrounds per chapter: {ms['backgrounds_per_chapter']}\n"
        readme += f"- Markets: {', '.join(ms['markets']) or 'none yet'}\n\n"

    readme += "---\n\n## CLI Quick Reference\n\n"
    readme += f"```bash\n"
    readme += f"# Generate catalog\n"
    readme += f"PYTHONPATH=. python3 scripts/catalog/generate_full_catalog.py --scope brand --brand {brand_id}\n\n"
    readme += f"# Build platform packets\n"
    readme += f"PYTHONPATH=. python3 scripts/release/build_admin_packets.py --brand {brand_id} --week current\n\n"
    readme += f"# Check QA\n"
    readme += f"PYTHONPATH=. python3 scripts/qa/run_bestseller_analysis.py --brand {brand_id}\n\n"
    readme += f"# Re-export this handoff\n"
    readme += f"PYTHONPATH=. python3 scripts/release/export_brand_admin_data.py --brand {brand_id}\n"
    readme += "```\n"

    (out_dir / "HANDOFF_README.md").write_text(readme, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Brand Admin Data Exporter")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--brand", type=str)
    scope.add_argument("--all", action="store_true")
    scope.add_argument("--market", type=str)
    parser.add_argument("--week", type=str, default="current")
    parser.add_argument("--output-base", type=str, default="artifacts/admin_handoff")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    week = _parse_week(args.week)
    print(f"Brand Admin Data Exporter — week {week}")
    if args.dry_run:
        print("[DRY-RUN]")

    # Load shared data once
    full_catalog = _load_full_catalog()
    manga_catalog = _load_manga_catalog()
    qa_findings = _load_qa_findings()
    char_registry = _load_char_registry()
    handoff_cfg = _load_handoff_config()

    print(f"  Catalog: {len(full_catalog)} entries | Manga: {len(manga_catalog)} rows | QA: {len(qa_findings)} findings")

    # Determine brands
    if args.brand:
        brand_ids = [args.brand]
    elif args.market:
        brand_ids = _brands_for_market(args.market)
        print(f"  Market '{args.market}': {len(brand_ids)} brands")
    else:
        brand_ids = _all_brand_ids()
        print(f"  All brands: {len(brand_ids)}")

    for base in [_WORKTREE, _REPO_ROOT]:
        out_base = base / args.output_base
        if out_base.parent.exists():
            break

    for brand_id in brand_ids:
        packet = build_admin_packet(
            brand_id, week, full_catalog, manga_catalog,
            qa_findings, char_registry, handoff_cfg,
        )
        out_dir = out_base / week / brand_id
        cs = packet["catalog_summary"]
        qa = packet["qa_summary"]
        ms = packet["manga_status"]
        print(f"  {brand_id}: {cs['this_week_queued']} titles | QA={qa['gate_health']} | manga_active={ms['series_active']}")
        if not args.dry_run:
            _write_packet(packet, out_dir)

    if not args.dry_run:
        print(f"\nHandoff packets written to: {out_base / week}/")
    else:
        print(f"\n[DRY-RUN] Would write packets to {out_base / week}/")


if __name__ == "__main__":
    main()

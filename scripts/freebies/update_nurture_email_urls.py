#!/usr/bin/env python3
"""Fix E1 funnel slugs and E2 unlocked somatic URLs in nurture email templates."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "config/funnel/email_templates"
ASSIGNMENTS = REPO / "config/freebies/archetype_assignments.yaml"

# topic (template file prefix) -> (e1 slug path, e2 somatic file from archetype)
TOPIC_ROUTES = {
    "anxiety": ("anxiety-nervous-system-reset", "ex13_body_scan.html"),
    "compassion_fatigue": ("compassion-fatigue-audit", "app22_tonglen.html"),
    "overthinking": ("overthinking-thought-sorter", "ex02_box_breathing.html"),
    "financial_anxiety": ("financial-anxiety-check-in", "ex04_extended_exhale.html"),
    "courage": ("courage-decision-map", "ex15_intention_quadrant.html"),
    "burnout": ("burnout-energy-audit", "ex02_box_breathing.html"),
    "sleep_anxiety": ("sleep-anxiety-wind-down", "ex13_body_scan.html"),
}


def _load_yaml(p: Path) -> dict:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _dump_yaml(p: Path, data: dict) -> None:
    import yaml
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _merge_archetypes() -> dict[str, tuple[str, str]]:
    routes = dict(TOPIC_ROUTES)
    data = _load_yaml(ASSIGNMENTS)
    for topic, row in (data.get("topics") or {}).items():
        slug = row.get("funnel_slug")
        app = row.get("e2_somatic_app")
        if slug and app:
            routes[topic] = (slug, app)
    return routes


def main() -> int:
    routes = _merge_archetypes()
    updated = 0
    for path in sorted(TEMPLATES.glob("*_nurture_5.yaml")):
        topic = path.name.replace("_nurture_5.yaml", "")
        if topic not in routes:
            continue
        slug, e2_app = routes[topic]
        doc = _load_yaml(path)
        emails = doc.get("emails") or {}
        e1 = emails.get("e1_download") or {}
        e2 = emails.get("e2_mechanism") or {}
        e1_cta = e1.get("cta") or {}
        e2_cta = e2.get("cta") or {}
        new_e1 = f"{{base_url}}/free/{slug}/"
        new_e2 = (
            f"{{base_url}}/somatic_exercise_freebee_apps/{e2_app}"
            "?unlock=1&cid={{contact_id}}"
        )
        changed = False
        if e1_cta.get("url_template") != new_e1:
            e1_cta["url_template"] = new_e1
            changed = True
        if e2_cta.get("url_template") != new_e2:
            e2_cta["url_template"] = new_e2
            changed = True
        if changed:
            e1["cta"] = e1_cta
            e2["cta"] = e2_cta
            emails["e1_download"] = e1
            emails["e2_mechanism"] = e2
            doc["emails"] = emails
            # post-purchase workbook slot (buyer tag only)
            if "post_purchase_workbook" not in emails:
                emails["post_purchase_workbook"] = {
                    "delay_hours": 0,
                    "trigger_tag": "buyer",
                    "subject": "Your companion workbook is ready",
                    "preview_text": "Post-purchase only — not sent in pre-buy nurture.",
                    "body": (
                        "Thank you for getting the book. Your companion workbook is attached "
                        "and ready to download. This delivers only after the buyer tag is applied."
                    ),
                    "cta": {
                        "text": "Download your workbook",
                        "url_template": "{workbook_download_url}",
                    },
                    "requires_buyer_tag": True,
                }
                doc["emails"] = emails
            _dump_yaml(path, doc)
            updated += 1
            print(f"updated {path.name}")
    print(f"done: {updated} templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

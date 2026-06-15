#!/usr/bin/env python3
"""
Bridge: brand-config YAML  →  Platform Setup Helper prefill.

Scans brand-config YAMLs (any file with a top-level `brand_admin:` key, e.g.
`way_stream_sanctuary_brand-config.yaml`) and emits two things:

  1. brand-wizard-app/public/platform_setup_helper_brands.json  (PUBLIC, no PII)
       { "<brand_id>": {name, focus, desc, slug, market} }
     → the helper reads this so `?brand=<id>` alone auto-prefills name/focus/desc/slug/market.
     Deliberately NO email/phone here — it would publish every brand's contact email on a
     public URL. Email rides only on a per-brand launch link (below).

  2. artifacts/onboarding/setup_helper_brand_links.tsv  (GITIGNORED, operator only)
       id · name · email · capture_url(local, incl. brand_email) · guidance_url(public)
     → one-click launch per brand. The local capture URL carries `brand_email` so the
       operator's capture screen and the steps show the real address (the {brand_email}
       placeholder resolves to the brand's own address from the per-brand link).

Brand id = filename stem minus `_brand-config`. Optional explicit overrides in the YAML
(`brand_admin.brand_name|brand_focus|brand_desc|brand_slug`) win over derivation.

Usage: python3 scripts/onboarding/gen_setup_helper_brands.py [--check]
Re-run after adding/editing a brand config.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import urllib.parse
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent.parent
PUBLIC = REPO / "brand-wizard-app" / "public" / "platform_setup_helper_brands.json"
OPLINKS = REPO / "artifacts" / "onboarding" / "setup_helper_brand_links.tsv"
PUBLIC_BASE = "https://brand-admin-onboarding.pages.dev/platform_setup_helper"
LOCAL_BASE = "http://localhost:5174/platform_setup_helper.html"

SCAN_GLOBS = [
    str(REPO / "*_brand-config.yaml"),
    str(REPO / "brand-wizard-app" / "brands" / "*.yaml"),
    str(REPO / "config" / "brand_management" / "brand_configs" / "*.yaml"),
]


def humanize(s) -> str:
    return str(s or "").replace("_", " ").replace("-", " ").strip()


def brand_id_from_path(p: Path) -> str:
    stem = p.stem
    if stem.endswith("_brand-config"):
        stem = stem[: -len("_brand-config")]
    return stem


def derive(cfg: dict, pid: str) -> dict:
    ba = cfg.get("brand_admin") or {}
    name = (ba.get("brand_name")
            or " ".join(x for x in [ba.get("first_name"), ba.get("last_name")] if x).strip()
            or pid.replace("_", " ").title())
    email = (ba.get("email") or "").strip()
    pos = ba.get("brand_positioning") or {}
    angle = pos.get("brand_angle") or ""
    persona = pos.get("persona") or ""
    tags = ba.get("topic_tags") or []
    mkt_raw = (ba.get("onboarding_market") or "us").lower()
    market = "ja" if mkt_raw in {"jp", "ja", "japan"} else "en"
    focus = ba.get("brand_focus") or humanize(angle) or (humanize(tags[0]) if tags else "")
    if ba.get("brand_desc"):
        desc = ba["brand_desc"]
    else:
        desc = humanize(angle) or focus
        if persona:
            desc = (f"{desc} for {humanize(persona)}s" if desc else humanize(persona))
    slug = (ba.get("brand_slug")
            or (email.split("@")[0] if "@" in email else None)
            or pid.replace("-", "_"))
    return {"id": pid, "name": name, "focus": focus, "desc": desc,
            "slug": slug, "market": market, "email": email}


def launch_url(base: str, b: dict, with_email: bool) -> str:
    q = {"brand": b["id"], "brand_name": b["name"], "brand_focus": b["focus"],
         "brand_desc": b["desc"], "brand_slug": b["slug"], "market": b["market"]}
    if with_email and b["email"]:
        q["brand_email"] = b["email"]
    return base + "?" + urllib.parse.urlencode(q)


def build() -> dict:
    files = []
    for g in SCAN_GLOBS:
        files += glob.glob(g)
    brands: dict[str, dict] = {}
    for f in sorted(set(files)):
        p = Path(f)
        try:
            cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if not isinstance(cfg, dict) or "brand_admin" not in cfg:
            continue
        b = derive(cfg, brand_id_from_path(p))
        brands[b["id"]] = b
    return brands


def render_public(brands: dict) -> str:
    public = {bid: {k: b[k] for k in ("name", "focus", "desc", "slug", "market")}
              for bid, b in brands.items()}
    return json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if public JSON is stale")
    args = ap.parse_args()

    brands = build()
    public_str = render_public(brands)

    if args.check:
        cur = PUBLIC.read_text(encoding="utf-8") if PUBLIC.exists() else ""
        if cur != public_str:
            sys.stderr.write(f"STALE: {PUBLIC} differs. Re-run without --check.\n")
            return 1
        print(f"OK: {PUBLIC} up to date ({len(brands)} brands).")
        return 0

    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC.write_text(public_str, encoding="utf-8")

    OPLINKS.parent.mkdir(parents=True, exist_ok=True)
    lines = ["id\tname\temail\tcapture_url_local\tguidance_url_public"]
    for bid, b in brands.items():
        lines.append("\t".join([bid, b["name"], b["email"],
                                launch_url(LOCAL_BASE, b, True),
                                launch_url(PUBLIC_BASE, b, False)]))
    OPLINKS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{len(brands)} brand(s) → {PUBLIC.name} (public, no email) + {OPLINKS} (operator, gitignored)")
    for bid in brands:
        print("  -", bid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

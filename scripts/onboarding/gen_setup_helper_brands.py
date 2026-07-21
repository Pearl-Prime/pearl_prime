#!/usr/bin/env python3
"""
Bridge: brand-config YAML + unified brand registry  →  Platform Setup Helper prefill.

Emits two things:

  1. brand-wizard-app/public/platform_setup_helper_brands.json  (PUBLIC, no PII)
       { "<brand_id>": {name, focus, desc, slug, market, publisher} }
     → the helper reads this so `?brand=<id>` alone auto-prefills the fields AND shows the
       PUBLICATION CORP / IMPRINT name (KDP "Published by") — e.g. stillness_press_en_us →
       "Stillness Press", devotion_path_en_us → "Open Vessel Press".
     Two sources are merged:
       • operator brand-config YAMLs (any file with a top-level `brand_admin:` key, e.g.
         `way_stream_sanctuary_brand-config.yaml`) → name/focus/desc/slug/market.
       • the canonical 40×14 unified registry (config/brand_management/
         global_brand_registry_unified.yaml) → a `publisher`-only entry per brand_id so the
         wizard-assigned ids resolve their imprint even without a per-brand config.
     The `publisher` label is resolved by the SAME longest-prefix corp lookup #1611 uses
     in scripts/onboarding/gen_brand_admin_brands.py — the registry's `publication_corp`
     (longest-prefix base→imprint already baked at registry-build time), with a longest-prefix
     fallback against brand_display_names.yaml for ids absent from the registry.
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
Re-run after adding/editing a brand config or rebuilding the unified registry.
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

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from brand_director_assignments import director_for, load_director_assignments

REPO = Path(__file__).resolve().parent.parent.parent
PUBLIC = REPO / "brand-wizard-app" / "public" / "platform_setup_helper_brands.json"
OPLINKS = REPO / "artifacts" / "onboarding" / "setup_helper_brand_links.tsv"
UNIFIED = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
DISPLAY_NAMES = REPO / "config" / "catalog_planning" / "brand_display_names.yaml"
PUBLIC_BASE = "https://brand-admin-onboarding-bu2.pages.dev/platform_setup_helper"
LOCAL_BASE = "http://localhost:5174/platform_setup_helper.html"

SCAN_GLOBS = [
    str(REPO / "*_brand-config.yaml"),
    str(REPO / "brand-wizard-app" / "brands" / "*.yaml"),
    str(REPO / "config" / "brand_management" / "brand_configs" / "*.yaml"),
]


def humanize(s) -> str:
    return str(s or "").replace("_", " ").replace("-", " ").strip()


# ── Publisher / imprint (KDP "Published by") resolver — same source of truth as #1611 ──
# (scripts/onboarding/gen_brand_admin_brands.py): the unified registry's `publication_corp`,
# keyed by full brand_id, where longest-prefix base→imprint is already baked at build time.
# For ids absent from the registry (e.g. operator demo configs) we fall back to a longest-
# prefix match against brand_display_names.yaml, then to the brand's own humanized name.

def _load_corp_index() -> dict:
    """brand_id -> publication corp/imprint name, from the unified 40×14 registry."""
    if not UNIFIED.exists():
        return {}
    reg = (yaml.safe_load(UNIFIED.read_text(encoding="utf-8")) or {}).get("brands") or {}
    out = {}
    for bid, b in reg.items():
        if isinstance(b, dict):
            corp = b.get("publication_corp") or b.get("display_name")
            if corp:
                out[bid] = corp
    return out


def _load_imprint_by_base() -> dict:
    """base archetype id -> imprint name, for longest-prefix fallback (ids not in registry)."""
    if not DISPLAY_NAMES.exists():
        return {}
    dn = yaml.safe_load(DISPLAY_NAMES.read_text(encoding="utf-8")) or {}
    out = {}
    for sect in ("teacher_brands", "standard_brands"):
        for base, info in (dn.get(sect) or {}).items():
            if isinstance(info, dict) and info.get("display_name"):
                out[base] = info["display_name"]
    return out


def resolve_publisher(brand_id: str, corp_by_id: dict, imprint_by_base: dict,
                      fallback_name: str = "") -> str:
    """Publisher/imprint label for a brand_id (reuses #1611's publication_corp source)."""
    # 1) exact full-id hit from the unified registry (canonical 40×14 — longest-prefix baked)
    corp = corp_by_id.get(brand_id)
    if corp:
        return corp
    # 2) longest-prefix against brand_display_names base ids (ids absent from the registry)
    parts = str(brand_id or "").split("_")
    for cut in range(len(parts), 0, -1):
        base = "_".join(parts[:cut])
        if base in imprint_by_base:
            return imprint_by_base[base]
    # 3) the brand's own display name, else a humanized id
    return fallback_name or " ".join(w.capitalize() for w in str(brand_id or "").split("_"))


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
    corp_by_id = _load_corp_index()
    imprint_by_base = _load_imprint_by_base()
    directors = load_director_assignments()

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
        b["publisher"] = resolve_publisher(b["id"], corp_by_id, imprint_by_base,
                                            fallback_name=b["name"])
        b.update(director_for(brand_id=b["id"], assignments=directors, allow_base=False))
        brands[b["id"]] = b

    # Seed the canonical 40×14 brand_ids the wizard assigns (e.g. stillness_press_en_us)
    # with a publisher-only entry, so `?brand=<id>` resolves its imprint even when no
    # operator brand-config exists yet. Operator configs above win (don't overwrite).
    for bid, corp in corp_by_id.items():
        if bid not in brands:
            entry = {"id": bid, "publisher": corp}
            entry.update(director_for(brand_id=bid, assignments=directors, allow_base=False))
            brands[bid] = entry
    return brands


def render_public(brands: dict) -> str:
    public = {}
    for bid, b in brands.items():
        entry = {k: b[k] for k in ("name", "focus", "desc", "slug", "market") if k in b}
        if b.get("publisher"):
            entry["publisher"] = b["publisher"]
        for k in ("brand_director_name", "brand_director_id", "brand_director_status"):
            if b.get(k):
                entry[k] = b[k]
        public[bid] = entry
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

    # Operator launch links only for brands with a full operator config (carry name/email).
    # Registry-seeded publisher-only entries have no contact info and get no launch link.
    op_brands = {bid: b for bid, b in brands.items() if "name" in b}
    OPLINKS.parent.mkdir(parents=True, exist_ok=True)
    lines = ["id\tname\temail\tcapture_url_local\tguidance_url_public"]
    for bid, b in op_brands.items():
        lines.append("\t".join([bid, b["name"], b.get("email", ""),
                                launch_url(LOCAL_BASE, b, True),
                                launch_url(PUBLIC_BASE, b, False)]))
    OPLINKS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    seeded = len(brands) - len(op_brands)
    print(f"{len(op_brands)} operator brand(s) + {seeded} registry publisher entries "
          f"→ {PUBLIC.name} (public, no email) + {OPLINKS} (operator, gitignored)")
    for bid in op_brands:
        print("  -", bid, "→", op_brands[bid].get("publisher", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

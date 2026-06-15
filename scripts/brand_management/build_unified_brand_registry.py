#!/usr/bin/env python3
"""
Build the UNIFIED brand registry — 39 brands × 14 lanes (per
specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md, decisions locked 2026-06-15).

Merges the canonical-37 identity (teacher_brand_archetypes 13 + brand_archetype_registry
24) + adi_da/joshin (38-39) and PORTS the deep data (primary_topics/personas/mission)
from global_brand_registry by the teacher rename map. Corp/publication name = the imprint
name from brand_display_names.yaml (has Press/Books). Manga is a per-lane % (lane_content_mix).

Output: config/brand_management/global_brand_registry_unified.yaml  (NEW file — does NOT
overwrite the live 25-brand registry until approved). Review, then the migration (spec §9)
re-points consumers + re-keys the roster.

    python3 scripts/brand_management/build_unified_brand_registry.py
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required"); sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
def L(rel):
    p = REPO / rel
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.is_file() else {}

# ── Locked decisions ───────────────────────────────────────────────────────
LANES = ["en_US","zh_TW","zh_HK","zh_CN","zh_SG","ja_JP","ko_KR",
         "es_US","es_ES","fr_FR","de_DE","it_IT","hu_HU","pt_BR"]   # 14 (+pt_BR)
INACTIVE = {"cognitive_clarity"}                                    # kenjin not activated

# canonical teacher id -> deep archetype id (port deep data by this map)
TEACHER_PORT = {
    "stillness_press":"inner_light_press", "somatic_wisdom":"body_wisdom",
    "qi_foundation":"vitality_path", "digital_ground":"gen_spark",
    "relational_calm":"zen_clarity", "warrior_calm":"iron_will",
    "sleep_restoration":"soul_repair", "heart_balance":"truth_compass",
    "solar_return":"cosmic_edge", "body_memory":"gentle_wave",
    "devotion_path":"healing_ground_press", "heart_transmission":"heart_transmission",
    # cognitive_clarity: no deep source (inactive)
    # adi_da/joshin: canonical id == deep id (added 38-39)
    "awakening_press":"awakening_press", "still_forest":"still_forest",
}
# imprint-name fallbacks where brand_display_names.yaml has no entry (must carry Press/Books)
IMPRINT_FALLBACK = {
    "heart_transmission":"Heart Transmission Press",
    "awakening_press":"Awakening Press",
    "still_forest":"Still Forest Press",   # proposed — operator may rename
}

def main():
    ta   = L("config/catalog_planning/teacher_brand_archetypes.yaml")
    bar  = L("config/catalog_planning/brand_archetype_registry.yaml")
    deep = L("config/brand_management/global_brand_registry.yaml").get("brands", {})
    dn   = L("config/catalog_planning/brand_display_names.yaml")
    manga= L("config/manga/canonical_brand_list.yaml").get("brands", {})
    lcm  = L("config/catalog/catalog_generation_config.yaml").get("lane_content_mix", {})
    locr = L("config/localization/locale_registry.yaml")

    # imprint (corp/publication) name by canonical id, from brand_display_names
    imprint = {}
    for sect in ("teacher_brands","standard_brands"):
        for bid, info in (dn.get(sect) or {}).items():
            if info and info.get("display_name"): imprint[bid] = info["display_name"]

    # deep data keyed by deep archetype id (en_US lane carries the base record)
    deep_en = {v["brand_archetype_id"]: v for v in deep.values() if v.get("lane_id")=="en_US"}

    # gtm fallback (deep build-out of thin brands): persona + focus from the archetype sources
    gtm = {}  # canon_id -> {persona, focus}
    for b in ta.get("teacher_brand_archetypes", []):
        g = b.get("gtm_identity") or {}
        gtm[b["brand_id"]] = {"persona": g.get("persona"),
                              "focus": "; ".join(x for x in [g.get("functional_job"), g.get("emotional_job")] if x)}
    _std_key = next((k for k,v in bar.items() if isinstance(v,list) and v and isinstance(v[0],dict) and "brand_id" in v[0]), None)
    for b in (bar.get(_std_key) or []):
        g = b.get("gtm_identity") or {}
        gtm.setdefault(b["brand_id"], {"persona": g.get("persona"),
                                       "focus": "; ".join(x for x in [g.get("functional_job"), g.get("emotional_job")] if x)})

    # canonical-37 topic fallback via manga canon (longest-prefix base match)
    def manga_topics(canon_id):
        for cid, m in manga.items():
            base = cid
            parts = cid.split("_")
            for cut in range(len(parts),0,-1):
                if "_".join(parts[:cut]) == canon_id:
                    tops = [m.get("primary_topic")] + (m.get("secondary_topics") or [])
                    return [t for t in tops if t]
        return []

    # ── assemble the 39 canonical archetypes ──
    archetypes = []  # (canon_id, teacher_id|None, teacher_mode)
    for b in ta.get("teacher_brand_archetypes", []):
        archetypes.append((b["brand_id"], b.get("teacher"), True))
    # +adi_da/joshin (38-39), pulled from deep
    for did, tid in (("awakening_press","adi_da"), ("still_forest","joshin")):
        archetypes.append((did, tid, True))
    std_key = next(k for k,v in bar.items() if isinstance(v,list) and v and isinstance(v[0],dict) and "brand_id" in v[0])
    for b in bar[std_key]:
        archetypes.append((b["brand_id"], None, False))

    def deep_for(canon_id, teacher_mode):
        src_id = TEACHER_PORT.get(canon_id, canon_id) if teacher_mode else canon_id
        return deep_en.get(src_id, {})

    def archetype_record(canon_id, teacher_id, teacher_mode):
        d = deep_for(canon_id, teacher_mode)
        g = gtm.get(canon_id, {})
        disp = imprint.get(canon_id) or IMPRINT_FALLBACK.get(canon_id) or canon_id.replace("_"," ").title()
        topics = d.get("primary_topics") or manga_topics(canon_id)
        personas = d.get("primary_personas") or ([g["persona"]] if g.get("persona") else [])
        return {
            "brand_archetype_id": canon_id,
            "display_name": disp,
            "publication_corp": disp,           # nonprofit publication corp = imprint name (Press/Books)
            "teacher_id": teacher_id,
            "teacher_mode": bool(teacher_mode),
            "tradition": d.get("tradition") or "",
            "brand_focus": d.get("brand_focus") or g.get("focus") or "",
            "primary_topics": topics,
            "primary_personas": personas,
            "content_families": d.get("content_families") or [],
            "mission": d.get("mission") or "To elevate people, especially the youth, helping them with their life challenges and aspirations.",
            "lifecycle": "inactive" if canon_id in INACTIVE else "active",
            "_deep_ported": bool(d),            # False => thin brand (topics from manga canon only)
            "_manga_axis": canon_id,            # cross-ref canonical_brand_list.yaml
        }

    base = {a[0]: archetype_record(*a) for a in archetypes}

    # ── expand × 14 lanes with per-lane manga% ──
    brands = {}
    for lane in LANES:
        loc = lane.replace("_","-")
        mix = lcm.get(lane, lcm.get("_default", {}))
        manga_pct = round(sum(v for k,v in mix.items() if "manga" in k), 3) if isinstance(mix, dict) else None
        for canon_id, rec in base.items():
            bid = f"{canon_id}_{lane.lower()}"
            brands[bid] = {
                "brand_id": bid, "lane_id": lane, "locale": loc,
                "lane_manga_pct": manga_pct,
                **rec,
            }

    out = {
        "schema_version": "2.0",
        "generated_by": "build_unified_brand_registry.py",
        "spec": "specs/BRAND_REGISTRY_RECONCILIATION_37x14_SPEC.md",
        "total_brand_archetypes": len(base),
        "total_lanes": len(LANES),
        "total_brands": len(brands),
        "inactive_archetypes": sorted(INACTIVE),
        "thin_archetypes_topics_from_manga_only": sorted([k for k,v in base.items() if not v["_deep_ported"]]),
        "lanes": LANES,
        "brands": brands,
    }
    outp = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
    outp.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"archetypes={len(base)} lanes={len(LANES)} brands={len(brands)} -> {outp.relative_to(REPO)}")
    print("inactive:", sorted(INACTIVE))
    print("thin (topics from manga only):", out["thin_archetypes_topics_from_manga_only"])
    # sanity: every archetype has an imprint corp name
    bad = [k for k,v in base.items() if not v["publication_corp"]]
    print("archetypes missing corp name:", bad or "none")

main()

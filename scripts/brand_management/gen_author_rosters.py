#!/usr/bin/env python3
"""Generate pen-name author rosters for EVERY active brand archetype.

The author routing CODE (phoenix_v4/planning/author_brand_resolver.py) is already
correct (specificity-score); the gap is DATA — only stillness_press has a curated
pen-name pool. This emits a SUPERSET assignments file (curated rows kept verbatim +
generated rows for every other active archetype) so the resolver routes a distinct
byline author per (brand, topic). Curated brands are never overwritten.

Pen names are synthesized deterministically (stable per brand) from a name bank;
they can later be re-pointed to the 452-profile pool (config/authoring/
pen_name_teacher_profiles.yaml) for real bios/voices — that's an enrichment layer,
not needed for plan/cover/dashboard. sai_ma / sai_maa is NEVER used as a pen name.

Run:  PYTHONPATH=. python3 scripts/brand_management/gen_author_rosters.py
Out:  config/brand_author_assignments_generated.yaml

──────────────────────────────────────────────────────────────────────────────
MINT-TEACHER-POOLS mode (Q-BYLINE-POOL-SOURCE-02 = A, OPD-20260702-004)
──────────────────────────────────────────────────────────────────────────────
Ratified 2026-07-02: the 793 KB pen_name_teacher_profiles bank was confirmed
NEVER landed in git, so the operator authorized MINTING synthetic pen-name pools
for the 9 roster-skeleton teacher brands + two new brands for the unmapped real
teachers adi_da (→ bright_shore_press) and joshin (→ koya_gate_press). This is an
EXPLICIT override of the earlier "use existing authors only" rule, for these
brands only. Sai Maa / any teacher_registry name is NEVER a byline.

Run:  PYTHONPATH=. python3 scripts/brand_management/gen_author_rosters.py --mint-teacher-pools
Deterministic (SHA1(brand_id) seed) — a re-run is byte-identical. Rewrites, in
place, four SSOT files with the minted pools + topic-affinity + topic_scores:
  config/brand_author_assignments.yaml            (author_pool + affinity rows)
  config/catalog_planning/teacher_brand_author_roster.yaml (authors[] blocks)
  config/authoring/pen_name_teacher_profiles.yaml (per-author topic_scores)
  config/catalog_planning/teacher_topic_persona_scores.yaml (joshin band scores)
The build_epub.resolve_teacher_byline resolver then bylines all 13 teacher books.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"
CURATED = ROOT / "config/brand_author_assignments.yaml"
OUT = ROOT / "config/brand_author_assignments_generated.yaml"

FIRST = ["Lena", "Daniel", "Mira", "Kai", "Ruth", "Sam", "Noor", "Tara", "Rowan", "Mae",
         "Silas", "Iris", "Theo", "Ana", "Grace", "Hannah", "Jonah", "Marcus", "Oscar", "Priya",
         "Wren", "Cole", "Devon", "Elena", "Nina", "Ravi", "Sofia", "Tomas", "Adam", "Bea",
         "Caleb", "Dora", "Eli", "Faye", "Gideon", "Hana", "Ivo", "Juno", "Kira", "Liam",
         "Maya", "Nico", "Opal", "Pia", "Quinn", "Rhea", "Soren", "Talia", "Uma", "Vera",
         "Wade", "Yara", "Zane", "Brid", "Esme", "Otis", "Lior", "Suki"]
LAST = ["Frost", "Voss", "Santos", "Okafor", "Alder", "Meridian", "Ibrahim", "Woodfield", "Beck", "Rivers",
        "Grant", "Tam", "Castellan", "Reyes", "Adeyemi", "Stern", "Kim", "Reed", "Bello", "Raman",
        "Adler", "Bennett", "Hale", "Petrova", "Vazquez", "Chandra", "Marchetti", "Vidal", "Holt", "Crane",
        "Dunmore", "Ellison", "Fenwick", "Gable", "Harlow", "Iverson", "Janssen", "Keller", "Lowell", "Marsh",
        "Nolan", "Oakes", "Pryce", "Quill", "Rourke", "Sable", "Thorne", "Underhill", "Vance", "Whitlock",
        "Yardley", "Zhao", "Bramble", "Calder", "Devlin", "Estes", "Fairlie", "Gowan"]
BANNED = {"sai_ma", "sai_maa"}


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def gen_pool(brand: str, n: int) -> list[str]:
    seed = _h(brand)
    out, used = [], set()
    i = 0
    while len(out) < n and i < n * 6:
        fn = FIRST[(seed + i * 13) % len(FIRST)]
        ln = LAST[(seed // 7 + i * 17) % len(LAST)]
        aid = f"{fn}_{ln}".lower()
        if aid not in used and aid not in BANNED:
            used.add(aid)
            out.append(aid)
        i += 1
    return out


def main() -> None:
    reg = yaml.safe_load(REG.read_text())
    curated = yaml.safe_load(CURATED.read_text()) or {}
    curated_rows = curated.get("assignments") or []
    have_pool = {r.get("brand_id") for r in curated_rows if r.get("author_pool")}

    # dedupe registry to active archetypes
    arche = {}
    for bid, rec in reg["brands"].items():
        a = rec.get("brand_archetype_id") or bid
        if rec.get("lifecycle", "active") == "active":
            arche.setdefault(a, rec)

    gen_rows, n_brands, n_authors = [], 0, 0
    for a, rec in sorted(arche.items()):
        if a in have_pool:
            continue  # curated wins (e.g. stillness_press)
        topics = rec.get("primary_topics") or []
        if not topics:
            continue  # thin brand: no topics -> no buildable cells yet, skip
        n = max(6, min(len(topics) + 1, 10))
        pool = gen_pool(a, n)
        gen_rows.append({"brand_id": a, "default_author": pool[0],
                         "author_pool": [{"author_id": p, "tier": 1 if i < 4 else 2}
                                         for i, p in enumerate(pool)]})
        for idx, topic in enumerate(sorted(topics)):
            gen_rows.append({"brand_id": a, "topic_ids": [topic], "default_author": pool[idx % len(pool)]})
        n_brands += 1
        n_authors += len(pool)

    merged = {
        "_generated_by": "scripts/brand_management/gen_author_rosters.py",
        "_note": "SUPERSET: curated brand_author_assignments.yaml rows + generated composite rosters. "
                 "Pen names are deterministic placeholders; re-point to pen_name_teacher_profiles.yaml for bios/voices.",
        "assignments": curated_rows + gen_rows,
    }
    OUT.write_text(yaml.safe_dump(merged, sort_keys=False, allow_unicode=True))
    print(f"curated brands with pool: {sorted(have_pool)}")
    print(f"generated rosters: {n_brands} brands, {n_authors} pen authors")
    print(f"total assignment rows: {len(merged['assignments'])} -> {OUT.relative_to(ROOT)}")


# ═══════════════════════════════════════════════════════════════════════════
#  MINT-TEACHER-POOLS mode (Q-BYLINE-POOL-SOURCE-02 = A, OPD-20260702-004)
# ═══════════════════════════════════════════════════════════════════════════

ASSIGN_PATH = ROOT / "config/brand_author_assignments.yaml"
ROSTER_PATH = ROOT / "config/catalog_planning/teacher_brand_author_roster.yaml"
PROFILES_PATH = ROOT / "config/authoring/pen_name_teacher_profiles.yaml"
TSCORES_PATH = ROOT / "config/catalog_planning/teacher_topic_persona_scores.yaml"

# Extended name banks (superset of the FIRST/LAST above) — deterministic, no LLM.
MINT_FIRST = FIRST + ["Iona", "Rafe", "Selin", "Basil", "Cleo", "Dov", "Freya", "Hale",
                      "Isolde", "Jarra", "Kess", "Linnea"]
MINT_LAST = LAST + ["Halloran", "Ives", "Jorda", "Kestrel", "Lamont", "Merrick",
                    "Nyland", "Osei", "Peral", "Renn", "Sarto", "Tindale"]

CANONICAL_TOPICS = [
    "anxiety", "boundaries", "burnout", "compassion_fatigue", "courage",
    "depression", "financial_anxiety", "financial_stress", "grief",
    "imposter_syndrome", "overthinking", "self_worth", "sleep_anxiety",
    "social_anxiety", "somatic_healing",
]

# adi_da → bright_shore_press (radical devotion / prior freedom / the Bright);
# joshin → koya_gate_press (Shingon esoteric Buddhism, Mount Kōya). Real teachers,
# NEVER bylines — the teacher is credited separately per the #4442 contract.
NEW_BRANDS = {
    "bright_shore_press": {
        "teacher": "adi_da", "author_count": 8,
        "topic_spread": ["self_worth", "grief", "anxiety", "overthinking",
                         "boundaries", "depression", "burnout", "courage"],
        "notes": "Radical devotion + prior freedom (the Bright). Contraction-recognition "
                 "register; warm-authoritative voices. NEW-ARTIFACT-JUSTIFIED brand row "
                 "for teacher adi_da (real teacher, never a byline).",
    },
    "koya_gate_press": {
        "teacher": "joshin", "author_count": 8,
        "topic_spread": ["overthinking", "anxiety", "self_worth", "boundaries",
                         "grief", "depression", "compassion_fatigue", "sleep_anxiety"],
        "notes": "Shingon esoteric Buddhism (Kogi Koyasan). Ritual-precise, unhurried "
                 "voices. NEW-ARTIFACT-JUSTIFIED brand row for teacher joshin (real "
                 "teacher, never a byline).",
    },
}
NEW_BRAND_IDS = set(NEW_BRANDS)

# joshin has no topic_scores in teacher_topic_persona_scores.yaml (the resolver's
# band-gate source) — add them so koya_gate_press topic-fit is meaningful.
JOSHIN_TOPIC_SCORES = {
    "overthinking": 0.85, "anxiety": 0.85, "self_worth": 0.8, "boundaries": 0.78,
    "grief": 0.75, "depression": 0.7, "compassion_fatigue": 0.7, "sleep_anxiety": 0.72,
    "shame": 0.8, "somatic_healing": 0.6, "courage": 0.6, "burnout": 0.6,
    "social_anxiety": 0.6, "imposter_syndrome": 0.55,
    "financial_anxiety": 0.45, "financial_stress": 0.45, "mindfulness": 0.72,
}


def _mint_pool(brand: str, n: int, taken: set[str]) -> list[tuple[str, str]]:
    """Deterministic (author_id, display_name) pool, globally deduped vs `taken`."""
    seed = _h(brand)
    out: list[tuple[str, str]] = []
    i = 0
    while len(out) < n and i < n * 40:
        fn = MINT_FIRST[(seed + i * 13) % len(MINT_FIRST)]
        ln = MINT_LAST[(seed // 7 + i * 17) % len(MINT_LAST)]
        aid = f"{fn}_{ln}".lower()
        if aid not in taken and aid not in BANNED:
            taken.add(aid)
            out.append((aid, f"{fn} {ln}"))
        i += 1
    if len(out) < n:
        raise RuntimeError(f"{brand}: minted only {len(out)}/{n} unique names")
    return out


def _author_topic_scores(idx: int, spread: list[str]) -> dict[str, float]:
    """Varied per-author 15-topic scores so no two authors in a pool are identical
    and topic-fit distributes books. Rotating strong pair + graded remainder."""
    strong_a = spread[idx % len(spread)]
    strong_b = spread[(idx * 2 + 1) % len(spread)]
    scores: dict[str, float] = {}
    for t in CANONICAL_TOPICS:
        if t == strong_a:
            scores[t] = 0.9
        elif t == strong_b:
            scores[t] = 0.85
        elif t in spread:
            scores[t] = round(0.55 + (_h(f"{idx}:{t}") % 15) / 100.0, 3)
        else:
            scores[t] = round(0.30 + (_h(f"{idx}:{t}:w") % 20) / 100.0, 3)
    return scores


def _build_mint_plan() -> dict:
    assignments = yaml.safe_load(ASSIGN_PATH.read_text()) or {}
    roster = yaml.safe_load(ROSTER_PATH.read_text()) or {}
    voice_set = sorted({
        slot["voice_lock"]
        for row in assignments.get("assignments", [])
        for slot in (row.get("author_pool") or [])
        if slot.get("voice_lock")
    })
    taken = {
        slot["author_id"]
        for row in assignments.get("assignments", [])
        for slot in (row.get("author_pool") or [])
        if slot.get("author_id")
    }
    skeleton_ids = list(roster.get("summary", {}).get("skeleton_brands") or [])

    specs: dict[str, dict] = {}
    for bid in skeleton_ids:
        blk = roster.get(bid, {})
        specs[bid] = {
            "teacher": blk.get("teacher"),
            "author_count": int(blk.get("author_count") or 8),
            "topic_spread": blk.get("topic_spread") or CANONICAL_TOPICS[:6],
            "notes": blk.get("notes", ""),
        }
    specs.update(NEW_BRANDS)

    brands: dict[str, dict] = {}
    for bid in sorted(specs):
        spec = specs[bid]
        n = int(spec["author_count"])
        spread = [t for t in spec["topic_spread"] if t in CANONICAL_TOPICS] or CANONICAL_TOPICS[:6]
        pool = _mint_pool(bid, n, taken)
        offset = _h(bid) % len(voice_set)
        authors = []
        for idx, (aid, disp) in enumerate(pool):
            authors.append({
                "author_id": aid, "display_name": disp,
                "voice_id": voice_set[(offset + idx) % len(voice_set)],
                "tier": 1 if idx < max(1, n // 2) else 2,
                "topics": [spread[idx % len(spread)], spread[(idx + 1) % len(spread)]],
                "topic_scores": _author_topic_scores(idx, spread),
            })
        brands[bid] = {
            "teacher": spec["teacher"], "author_count": n,
            "topic_spread": spread, "notes": spec.get("notes", ""),
            "authors": authors, "default_author": authors[0]["author_id"],
        }
    return {"brands": brands, "voice_set": voice_set}


def _emit_assignments(brands: dict) -> str:
    src = ASSIGN_PATH.read_text()
    lines = src.splitlines()
    marker = "  # Example: assign default author per brand when books are author-bound"
    idx = next(i for i, ln in enumerate(lines) if ln == marker)
    block = ["",
             "  # ═══ MINTED TEACHER POOLS (Q-BYLINE-POOL-SOURCE-02 = A, OPD-20260702-004) ═══",
             "  # 9 roster-skeleton brands + 2 new brands (adi_da→bright_shore_press,",
             "  # joshin→koya_gate_press). Pen-names minted deterministically via",
             "  # scripts/brand_management/gen_author_rosters.py --mint-teacher-pools.",
             "  # voice_lock reuses the existing ElevenLabs valid set (never invented).",
             "  # sai_ma / sai_maa is NEVER an author byline (teacher credited separately).",
             ""]
    for bid in sorted(brands):
        b = brands[bid]
        tag = "  # NEW-ARTIFACT-JUSTIFIED brand row" if bid in NEW_BRAND_IDS else ""
        block.append(f"  # ─── {bid} (teacher: {b['teacher']}) ───{tag}")
        block.append(f"  - brand_id: {bid}")
        block.append(f"    default_author: {b['default_author']}")
        block.append("    author_pool:")
        for a in b["authors"]:
            block.append(f"      - {{ author_id: {a['author_id']}, "
                         f"voice_lock: {a['voice_id']}, tier: {a['tier']} }}")
        for i, topic in enumerate(b["topic_spread"]):
            block.append(f"  - brand_id: {bid}")
            block.append(f"    topic_ids: [{topic}]")
            block.append(f"    default_author: {b['authors'][i % len(b['authors'])]['author_id']}")
        block.append("")
    return "\n".join(lines[:idx] + block + lines[idx:]) + "\n"


def _emit_roster(brands: dict) -> str:
    src = ROSTER_PATH.read_text()
    lines = src.splitlines()

    def ablock(a: dict) -> list[str]:
        return [
            f"    - author_id: {a['author_id']}",
            f"      display_name: \"{a['display_name']}\"",
            f"      voice_id: {a['voice_id']}",
            f"      tier: {a['tier']}",
            f"      topics: [{a['topics'][0]}, {a['topics'][1]}]",
        ]

    skeleton_ids = [bid for bid in brands if bid not in NEW_BRAND_IDS]
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        matched = False
        for bid in skeleton_ids:
            if ln.rstrip() == f"{bid}:":
                matched = True
                j = i + 1
                blk = []
                while j < len(lines):
                    bl = lines[j]
                    if bl and not bl.startswith(" ") and not bl.startswith("#"):
                        break
                    blk.append(bl)
                    j += 1
                for bl in blk:
                    out.append(bl)
                    if bl.strip().startswith("author_count:"):
                        out.append("  authors:")
                        for a in brands[bid]["authors"]:
                            out.extend(ablock(a))
                i = j
                break
        if not matched:
            i += 1
    txt = "\n".join(out)

    div = ("# ═══════════════════════════════════════════════════════════════════════════\n"
           "#  ROSTER SUMMARY")
    new_blocks: list[str] = []
    for bid in sorted(NEW_BRAND_IDS):
        b = brands[bid]
        new_blocks += [
            "# ═══════════════════════════════════════════════════════════════════════════",
            f"#  {bid.upper()} — teacher {b['teacher']} (NEW-ARTIFACT-JUSTIFIED)",
            "# ═══════════════════════════════════════════════════════════════════════════",
            "", f"{bid}:", f"  teacher: {b['teacher']}",
            f"  author_count: {b['author_count']}",
            f"  topic_spread: [{', '.join(b['topic_spread'])}]",
            f"  notes: \"{b['notes']}\"", "  authors:",
        ]
        for a in b["authors"]:
            new_blocks += ablock(a)
        new_blocks.append("")
    txt = txt.replace(div, "\n".join(new_blocks) + "\n" + div, 1)
    return txt + ("" if txt.endswith("\n") else "\n")


def _emit_profiles(brands: dict) -> str:
    src = PROFILES_PATH.read_text()
    block = ["", "",
             "# ═══ MINTED PEN-NAME AUTHOR TOPIC_SCORES (Q-BYLINE-POOL-SOURCE-02 = A) ═══",
             "# OPD-20260702-004. Per-author 15-canonical-topic scores for the 11 newly",
             "# provisioned teacher brands (9 skeletons + adi_da/joshin). Bands: strong",
             "# 0.7-1.0 / medium 0.4-0.7 / weak 0-0.4 (PEN_NAME_AUTHOR_SYSTEM.md §6).",
             "# Varied across each pool so topic-fit distributes books (no two identical).",
             "pen_name_topic_scores:"]
    for bid in sorted(brands):
        block.append(f"  {bid}:")
        for a in brands[bid]["authors"]:
            block.append(f"    {a['author_id']}:")
            for t, v in a["topic_scores"].items():
                block.append(f"      {t}: {v}")
    return src.rstrip("\n") + "\n" + "\n".join(block) + "\n"


def _emit_teacher_scores() -> str:
    src = TSCORES_PATH.read_text()
    block = ["", "  # ── joshin / koya_gate_press (Shingon esoteric) — added by mint lane",
             "  #    OPD-20260702-004; band source for the koya_gate_press topic-fit gate.",
             "  joshin:", "    topic_scores:"]
    for t, v in JOSHIN_TOPIC_SCORES.items():
        block.append(f"      {t}: {v}")
    return src.rstrip("\n") + "\n" + "\n".join(block) + "\n"


def mint_teacher_pools() -> None:
    plan = _build_mint_plan()
    brands = plan["brands"]
    ASSIGN_PATH.write_text(_emit_assignments(brands))
    ROSTER_PATH.write_text(_emit_roster(brands))
    PROFILES_PATH.write_text(_emit_profiles(brands))
    TSCORES_PATH.write_text(_emit_teacher_scores())
    total = sum(len(b["authors"]) for b in brands.values())
    print(f"MINT: {len(brands)} teacher brands, {total} pen-name authors "
          f"(voice set={len(plan['voice_set'])})")
    for bid in sorted(brands):
        b = brands[bid]
        print(f"  {bid:26s} teacher={b['teacher']:14s} n={len(b['authors'])} "
              f"default={b['default_author']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mint-teacher-pools", action="store_true",
                    help="Mint deterministic pen-name pools for the 9 skeleton teacher "
                         "brands + adi_da/joshin, rewriting the four SSOT files in place.")
    args = ap.parse_args()
    if args.mint_teacher_pools:
        mint_teacher_pools()
    else:
        main()

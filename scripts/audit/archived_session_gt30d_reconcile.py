#!/usr/bin/env python3
"""Reconcile curated gt30d ideas against targeted repo paths (no recursive globs)."""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(".")
OUT = Path("artifacts/qa/archived_session_audit_gt30d_20260722")


def exists(p: str) -> bool:
    return (ROOT / p).exists()


def rg_files(pattern: str, max_hits: int = 5) -> list[str]:
    """Filename search via rg --files -g; fast enough for this audit."""
    try:
        proc = subprocess.run(
            ["rg", "--files", "-g", pattern],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    hits = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return hits[:max_hits]


def quote_for(raw_by_session: dict, sid: str, fallback: str) -> str:
    ideas = raw_by_session.get(sid) or []
    for idea in ideas:
        q = idea.get("quote_or_signal") or ""
        if re.search(
            r"(?i)not yet|missing|should|proposal|implement|next step|TODO|never",
            q,
        ):
            return q[:240]
    if ideas:
        return (ideas[0].get("quote_or_signal") or ideas[0].get("first_user") or fallback)[
            :240
        ]
    return fallback[:240]


CANDIDATES = [
    dict(
        id="I001",
        title="Author resolution wiring into assembly pipeline",
        theme="pipeline_gates",
        source="2431a4be",
        paths=["docs/", "phoenix_v4/"],
        name_globs=["*author*resol*", "*AUTHOR_RESOLUTION*"],
        prior="Cross-check Claude memory project_author_system_real_state",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I002",
        title="Unified personas readiness: atoms left for writing books",
        theme="catalog_atoms",
        source="9ad29a26",
        paths=["SOURCE_OF_TRUTH/", "config/"],
        name_globs=["*unified_persona*", "*personas*.yaml"],
        prior="Related to atom cohesion / coverage memory notes",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I003",
        title="Teacher-mode strict + fallback plan completion",
        theme="pipeline_gates",
        source="0acf3b70",
        paths=["teachers/"],
        name_globs=["*teacher*mode*", "*teacher_mode*"],
        prior="Later teacher onboarding packs may cover parts",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I004",
        title="English catalog creation without assembling books",
        theme="catalog_atoms",
        source="2005e463",
        paths=["artifacts/catalog_visibility/", "config/"],
        name_globs=["*skeleton*"],
        prior="Catalog evolved heavily since Feb — likely LIKELY_LANDED scaffolding",
        repo=3,
        pipe=3,
    ),
    dict(
        id="I005",
        title="Author signature / blueprint cover-pic system",
        theme="covers_brand",
        source="ba905820",
        paths=["docs/NAMING_COVER_SYSTEM_37x14.md"],
        name_globs=["*COVER*FIVE*LAYER*", "*cover*signature*", "*COVER*BLUEPRINT*"],
        prior="Last-30d audit flagged cover uniqueness offline/not on main",
        repo=5,
        pipe=4,
    ),
    dict(
        id="I006",
        title="family_id enum drift silent corruption fix",
        theme="pipeline_gates",
        source="754099c5",
        paths=[],
        name_globs=["*family_id*", "*check*family*"],
        prior="Likely partially fixed; confirm CI gate",
        repo=4,
        pipe=5,
    ),
    dict(
        id="I007",
        title="Catalog knob usage-percent analyzer",
        theme="research_tooling",
        source="f42cad21",
        paths=[],
        name_globs=["*knob*usage*", "*catalog*knob*"],
        prior="FEATURE-KNOB-CATALOG-VARIATION era; analyzer may still be thin",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I008",
        title="DOCS_INDEX completeness / V4 wiring gate",
        theme="governance_ci",
        source="f067a5d7",
        paths=["docs/DOCS_INDEX.md"],
        name_globs=["*check_docs_index*", "*docs_index*completeness*"],
        prior="DUPLICATE of session_mining RN-9",
        repo=4,
        pipe=3,
        status_override="DUPLICATE_OF_PRIOR_MINING",
    ),
    dict(
        id="I009",
        title="Pearl Prime book-template bridge into freebies/immersion",
        theme="pipeline_gates",
        source="61d46e39",
        paths=[],
        name_globs=["*freebie*", "*immersion*"],
        prior="Later freebie harbor closeout pack",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I010",
        title="Pearl News editorial article structure / org wiring",
        theme="pearl_news",
        source="5643f03a",
        paths=["docs/PEARL_NEWS_WRITER_SPEC.md"],
        name_globs=["*PEARL_NEWS*", "*pearl_news*"],
        prior="Sidebar canonical later; editorial gaps may remain",
        repo=5,
        pipe=4,
    ),
    dict(
        id="I011",
        title="AI-assisted therapeutic book assembly beyond metadata matching",
        theme="pipeline_gates",
        source="cf278b1b",
        paths=[],
        name_globs=["*human*calibrated*judge*", "*register_gate*"],
        prior="MERGE with SPEC-4; do not build parallel judge",
        repo=4,
        pipe=5,
        status_override="DUPLICATE_OF_PRIOR_MINING",
    ),
    dict(
        id="I012",
        title="Full-repo core-function operator UI / system status console",
        theme="research_tooling",
        source="aba05c79",
        paths=["PhoenixControl/"],
        name_globs=["*brand_admin*", "*operator*dashboard*"],
        prior="PhoenixControl restored; 100% console still aspirational",
        repo=4,
        pipe=3,
    ),
    dict(
        id="I013",
        title="EI V2 hybrid system completeness audit",
        theme="pipeline_gates",
        source="2c37ac68",
        paths=[],
        name_globs=["*ei_v2*", "*EI*V2*"],
        prior="May be superseded by later quality stacks",
        repo=3,
        pipe=4,
    ),
    dict(
        id="I014",
        title="V4 freebies + immersion ecosystem completion",
        theme="social_video",
        source="6b3eac83",
        paths=[],
        name_globs=["*freebie*", "*immersion*"],
        prior="20260715 freebie harbor pack",
        repo=4,
        pipe=3,
    ),
    dict(
        id="I015",
        title="Continuous deep research plane (scheduled, not one-shot)",
        theme="research_tooling",
        source="7654d26d",
        paths=["docs/research/", "scripts/research/research_prompt_builder.py"],
        name_globs=["*PEARL_RESEARCH*", "*research_prompt_builder*"],
        prior="Builder exists; continuous GitHub research plane may still be missing",
        repo=5,
        pipe=3,
    ),
    dict(
        id="I016",
        title="Marketing system wiring for monetization completeness",
        theme="social_video",
        source="eef58738",
        paths=[],
        name_globs=["*FREE_TO_PAID*", "*metricool*", "*GHL*"],
        prior="Overlaps SPEC-6 free-to-paid ladder",
        repo=4,
        pipe=3,
        status_override="DUPLICATE_OF_PRIOR_MINING",
    ),
    dict(
        id="I017",
        title="Video thumbnail contract (thumb.jpg beside video.mp4)",
        theme="social_video",
        source="e376fbc9",
        paths=[],
        name_globs=["*thumbnail*", "*thumb.jpg"],
        prior="Verify video pipeline enforces thumb contract",
        repo=3,
        pipe=4,
    ),
    dict(
        id="I018",
        title="Brand media generation canonical path",
        theme="covers_brand",
        source="f315b072",
        paths=[],
        name_globs=["*IMG_RENDER*", "*brand_media*"],
        prior="IMG_RENDER_DUAL_PATH later",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I019",
        title="Brand-wizard-app UX continuation",
        theme="covers_brand",
        source="9ca9742d",
        paths=[],
        name_globs=["*brand*wizard*", "*wizard*"],
        prior="Last-30d: brand-wizard fixes offline",
        repo=4,
        pipe=3,
    ),
    dict(
        id="I020",
        title="Video pipeline handoff / series assembly resume",
        theme="social_video",
        source="59d869bd",
        paths=["artifacts/audio/presenter/"],
        name_globs=["*video*pipeline*", "*presenter*"],
        prior="Teacher YouTube / CosyVoice2 path evolved later",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I021",
        title="13 teacher YouTube video banks assembly",
        theme="social_video",
        source="f4ec4722",
        paths=["teachers/"],
        name_globs=["*youtube*", "*teacher*video*"],
        prior="Partial execution likely",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I022",
        title="TikTok body-awareness shot plans for teachers",
        theme="social_video",
        source="c4a47e5a",
        paths=[],
        name_globs=["*body*awareness*", "*tiktok*"],
        prior="Ahjan QA then scale to teachers",
        repo=3,
        pipe=3,
    ),
    dict(
        id="I023",
        title="CJK teacher topic-pack overlays + per-language system prompts",
        theme="translation",
        source="7b85b693",
        paths=["config/localization/"],
        name_globs=["*topic*pack*", "*system_prompt*"],
        prior="CJK6 / translate-* doctrine evolved",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I024",
        title="Iterative catalog quality refinement loop (judge + auto-adjust)",
        theme="pipeline_gates",
        source="2fe91134",
        paths=[],
        name_globs=["*HUMAN_CALIBRATED_JUDGE*", "*catalog*quality*"],
        prior="MERGE with SPEC-4",
        repo=4,
        pipe=5,
        status_override="DUPLICATE_OF_PRIOR_MINING",
    ),
    dict(
        id="I025",
        title="Atom gap analysis: cohesive flow, bridges, bestseller structure",
        theme="catalog_atoms",
        source="fc9e7c1f",
        paths=["docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md"],
        name_globs=["*ATOM_SURFACE*", "*atom*gap*", "*atom*depth*"],
        prior="Overlaps SPEC-1 atom depth manifest",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I026",
        title="Music-mode brand integration + freebie funnel",
        theme="social_video",
        source="44b6d363",
        paths=[],
        name_globs=["*MUSIC*MODE*", "*music*mode*"],
        prior="Last-30d: music-mode wizard pack authored but undispached",
        repo=5,
        pipe=4,
    ),
    dict(
        id="I027",
        title="Musician survey → music mode implementation",
        theme="social_video",
        source="8175c0a0",
        paths=[],
        name_globs=["*musician*survey*", "*music*mode*"],
        prior="Pairs with I026",
        repo=3,
        pipe=3,
    ),
    dict(
        id="I028",
        title="Manga V2 character individuation prompt-builder",
        theme="manga",
        source="9762773d",
        paths=["scripts/manga/"],
        name_globs=["*character_individuation*"],
        prior="Check CODE-WIRED vs complete",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I029",
        title="Manga V2 lettering / bubble layer (audit P0-2)",
        theme="manga",
        source="5fab9ed4",
        paths=["scripts/manga/"],
        name_globs=["*lettering*", "*webtoon_compositing*"],
        prior="Export 362/363 blocked on JLREQ/SFX lettering proof",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I030",
        title="Catalog 800 auto-generator (vs hand-edited high_confidence)",
        theme="catalog_atoms",
        source="2e48dda5",
        paths=[],
        name_globs=["*high_confidence*", "*catalog*800*"],
        prior="project_800_high_confidence_configs memory",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I031",
        title="Localization quality contracts CI enforcement depth",
        theme="translation",
        source="643f74db",
        paths=["config/localization/quality_contracts/"],
        name_globs=["*quality_contracts*"],
        prior="Folder exists — verify gate depth",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I032",
        title="Feature-knob catalog variation: explicit angle_id registry join",
        theme="catalog_atoms",
        source="59da2ac9",
        paths=[],
        name_globs=["*angle*registry*", "*angle_id*"],
        prior="PR #974 era",
        repo=4,
        pipe=5,
    ),
    dict(
        id="I033",
        title="Manga brand×locale gap matrix (LFS pointer vs present)",
        theme="manga",
        source="d914dcda",
        paths=[],
        name_globs=["*gap*matrix*", "*lfs*pointer*"],
        prior="Overlaps SPEC-8 retention / LFS policy",
        repo=5,
        pipe=4,
    ),
    dict(
        id="I034",
        title="Book + audiobook buying platform (storefront/marketplace) spec",
        theme="research_tooling",
        source="fef9c8bd",
        paths=[],
        name_globs=["*storefront*", "*snipcart*", "*buy*platform*"],
        prior="Last-30d: Snipcart/Stripe keys are operator gate; platform spec may still be thin",
        repo=5,
        pipe=3,
    ),
    dict(
        id="I035",
        title="Church/brand/payment plans integration",
        theme="covers_brand",
        source="4286531d",
        paths=[],
        name_globs=["*church*", "*payment*plan*"],
        prior="Niche — confirm still desired",
        repo=2,
        pipe=2,
    ),
    dict(
        id="I036",
        title="RunComfy cost-alert dashboard widget on brand_admin",
        theme="covers_brand",
        source="80df403d",
        paths=[],
        name_globs=["*brand_admin*", "*runcomfy*cost*"],
        prior="ws_runcomfy_cost_alert_dashboard_20260509",
        repo=3,
        pipe=3,
    ),
    dict(
        id="I037",
        title="US marketing plan consolidation",
        theme="social_video",
        source="7a45b126",
        paths=[],
        name_globs=["*US*marketing*", "*marketing*plan*"],
        prior="May be superseded by GHL/free-to-paid",
        repo=3,
        pipe=2,
    ),
    dict(
        id="I038",
        title="Pearl News per-brand mapping leftover",
        theme="pearl_news",
        source="eac25063",
        paths=["docs/PEARL_NEWS_WRITER_SPEC.md"],
        name_globs=["*pearl_news*"],
        prior="OPD-119/121 closeout leftover",
        repo=4,
        pipe=3,
    ),
    dict(
        id="I039",
        title="Metricool X/Twitter channel decision ($5 add-on)",
        theme="social_video",
        source="export_303",
        paths=[],
        name_globs=["*metricool*"],
        prior="Operator taste / billing",
        repo=3,
        pipe=2,
        status_override="OPERATOR_GATE",
    ),
    dict(
        id="I040",
        title="Catalog PLAN-completeness audit 14×39",
        theme="catalog_atoms",
        source="export_351",
        paths=[],
        name_globs=["*PLAN*completeness*", "*plan*audit*"],
        prior="Last-30d: Wave 3 PLAN green offline — do not reopen as unread",
        repo=3,
        pipe=3,
        status_override="DUPLICATE_OF_PRIOR_MINING",
    ),
    dict(
        id="I041",
        title="Waystream cover durable delta-queue (no blind rerender)",
        theme="covers_brand",
        source="export_355",
        paths=["docs/NAMING_COVER_SYSTEM_37x14.md"],
        name_globs=["*waystream*", "*force-rerender*"],
        prior="Authority docs exist; durable delta lane may be thin",
        repo=4,
        pipe=4,
    ),
    dict(
        id="I042",
        title="Manga structural-composition MVP",
        theme="manga",
        source="export_357",
        paths=[],
        name_globs=["*structural*composition*", "*contact*region*"],
        prior="Check CODE-WIRED vs EXECUTED-REAL under manga doctrine",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I043",
        title="Manga PassB reading-graph + spread layout + JLREQ SFX lettering proof",
        theme="manga",
        source="export_362",
        paths=[],
        name_globs=["*reading*graph*", "*spread*layout*", "*jlreq*"],
        prior="Export BLOCKED — bar packet not assembled",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I044",
        title="Cloud/Codespaces substrate fanout for manga",
        theme="governance_ci",
        source="export_361",
        paths=[],
        name_globs=["*MANGA_CLOUD_FANOUT*"],
        prior="Operator gh auth / Cursor Cloud",
        repo=3,
        pipe=3,
        status_override="OPERATOR_GATE",
    ),
    dict(
        id="I045",
        title="Books-first leftovers: engine-keyed STORY seeding + 4-cell rebuild",
        theme="pipeline_gates",
        source="export_366",
        paths=[],
        name_globs=["*books*first*", "*STORY*"],
        prior="Closeout next-step after PR #5530 era",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I046",
        title="ProPrime modes 100% merge wave",
        theme="pipeline_gates",
        source="export_365",
        paths=[],
        name_globs=["*proprime*", "*PROPRIME*"],
        prior="Verify whether still an active program",
        repo=3,
        pipe=3,
    ),
    dict(
        id="I047",
        title="Anti-reinvention architecture enforcement",
        theme="governance_ci",
        source="memory:project_anti_reinvention_architecture",
        paths=["artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv"],
        name_globs=["*anti*reinvention*"],
        prior="Authority map exists; enforcement may be soft",
        repo=4,
        pipe=3,
    ),
    dict(
        id="I048",
        title="Atom cohesion chunked plan execution",
        theme="catalog_atoms",
        source="memory:project_atom_cohesion_chunked_plan",
        paths=[],
        name_globs=["*atom*cohesion*", "*ATOM_SURFACE*"],
        prior="Pairs with I025 / SPEC-1",
        repo=5,
        pipe=5,
    ),
    dict(
        id="I049",
        title="Brand registry 37×14 unification completion",
        theme="covers_brand",
        source="memory:project_brand_registry_37x14_unification",
        paths=["docs/NAMING_COVER_SYSTEM_37x14.md"],
        name_globs=["*37x14*", "*brand*registry*"],
        prior="Naming cover system doc exists",
        repo=5,
        pipe=4,
    ),
    dict(
        id="I050",
        title="Devotion Path catalog readiness (flagged not ready)",
        theme="catalog_atoms",
        source="memory:project_devotion_path_catalog_not_ready",
        paths=[],
        name_globs=["*devotion_path*"],
        prior="Dashboards ≠ catalog readiness",
        repo=3,
        pipe=3,
    ),
]


def main() -> int:
    raw_by_session: dict[str, list[dict]] = {}
    for line in (OUT / "IDEA_BACKLOG_RAW.jsonl").read_text(encoding="utf-8").splitlines():
        o = json.loads(line)
        raw_by_session.setdefault(o["source_session"], []).append(o)

    catalog: dict[str, list[str]] = {}
    for line in (OUT / "SESSION_CATALOG.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split("\t")
        catalog[cols[0]] = cols
        catalog[cols[0][:8]] = cols

    sec = json.loads((OUT / "SECONDARY_PASS.json").read_text(encoding="utf-8"))

    def resolve_source(src: str) -> tuple[str, str]:
        if src.startswith("export_") or src.startswith("memory:"):
            return src, src
        if src in catalog:
            cols = catalog[src]
            return cols[0], cols[4]
        for k, cols in catalog.items():
            if len(k) == 36 and k.startswith(src):
                return k, cols[4]
        return src, ""

    rows: list[dict] = []
    for c in CANDIDATES:
        sid, title_prev = resolve_source(c["source"])
        found = [p for p in c.get("paths") or [] if exists(p)]
        name_hits: list[str] = []
        for g in c.get("name_globs") or []:
            name_hits.extend(rg_files(g, max_hits=3))
        name_hits = name_hits[:6]

        if c.get("status_override"):
            status = c["status_override"]
        elif name_hits and found:
            status = "PARTIAL"
        elif name_hits or found:
            status = "PARTIAL" if c["repo"] >= 4 else "LIKELY_LANDED"
        else:
            status = "TRULY_MISSING"

        prior = c.get("prior") or ""
        q = ""
        if sid.startswith("export_"):
            for er in sec["uncovered_exports"]:
                if er["id"] == sid:
                    q = (er.get("signals") or [er.get("preview", "")])[0][:240]
                    break
        elif sid.startswith("memory:"):
            for mr in sec["memory_titles"]:
                if mr["id"] == sid:
                    q = mr.get("preview", "")[:240]
                    break
        else:
            q = quote_for(raw_by_session, sid, title_prev or c["title"])

        evidence = ";".join((found + name_hits)[:6]) or "(no path hit)"
        score = (
            c["repo"]
            + c["pipe"]
            + (2 if status == "TRULY_MISSING" else 1 if status == "PARTIAL" else 0)
        )
        rows.append(
            {
                "idea_id": c["id"],
                "title": c["title"],
                "theme": c["theme"],
                "source_session": sid,
                "quote_or_signal": (q or c["title"]).replace("\t", " ").replace("\n", " "),
                "status_guess": status,
                "repo_relevance": c["repo"],
                "pipeline_relevance": c["pipe"],
                "evidence_paths": evidence.replace("\t", " "),
                "prior_note": prior.replace("\t", " ").replace("\n", " "),
                "score": score,
            }
        )
        print(f"reconciled {c['id']} -> {status}", flush=True)

    rows_sorted = sorted(rows, key=lambda r: (-r["score"], -r["repo_relevance"], r["idea_id"]))
    cols = [
        "idea_id",
        "title",
        "theme",
        "source_session",
        "quote_or_signal",
        "status_guess",
        "repo_relevance",
        "pipeline_relevance",
        "evidence_paths",
    ]
    with (OUT / "IDEA_BACKLOG.tsv").open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows_sorted:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")

    with (OUT / "DEDUP_LEDGER.tsv").open("a", encoding="utf-8") as f:
        for r in rows:
            if r["status_guess"] in (
                "DUPLICATE_OF_PRIOR_MINING",
                "OPERATOR_GATE",
                "SUPERSEDED",
            ):
                f.write(
                    "\t".join(
                        [
                            f"idea:{r['idea_id']}",
                            r["source_session"],
                            r["title"][:120],
                            r["status_guess"],
                            r.get("prior_note", "")[:200],
                        ]
                    )
                    + "\n"
                )

    (OUT / "IDEA_BACKLOG_ENRICHED.json").write_text(
        json.dumps(rows_sorted, indent=2), encoding="utf-8"
    )
    print("STATUS", dict(Counter(r["status_guess"] for r in rows)))
    print("wrote", OUT / "IDEA_BACKLOG.tsv", "n=", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Finalize IDEA_BACKLOG + RANKED_FINDINGS + WAVE_PROGRESS without filesystem walks."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

OUT = Path("artifacts/qa/archived_session_audit_gt30d_20260722")

# Evidence from the completed path probe (no further find/rg).
EVIDENCE = {
    "I001": ["docs/", "phoenix_v4/"],
    "I002": ["SOURCE_OF_TRUTH/", "config/"],
    "I003": ["teachers/"],
    "I004": ["artifacts/catalog_visibility/", "config/"],
    "I005": [
        "docs/NAMING_COVER_SYSTEM_37x14.md",
        "docs/specs/COVER_FIVE_LAYER_UNIQUENESS_V1_SPEC.md",
    ],
    "I006": [],
    "I007": ["scripts/audit/build_pipeline_matrix.py"],
    "I008": ["docs/DOCS_INDEX.md"],
    "I009": [
        "docs/agent_prompt_packs/20260715_old_chat_closure_audit/06_Pearl_Brand_freebie_harbor_closeout.md"
    ],
    "I010": [
        "docs/PEARL_NEWS_WRITER_SPEC.md",
        "docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md",
    ],
    "I011": [
        "docs/specs/session_mining_batch_20260718/HUMAN_CALIBRATED_JUDGE_V1_SPEC.md",
        "phoenix_v4/quality/register_gate.py",
    ],
    "I012": ["PhoenixControl/"],
    "I013": [],
    "I014": [
        "docs/agent_prompt_packs/20260715_old_chat_closure_audit/06_Pearl_Brand_freebie_harbor_closeout.md"
    ],
    "I015": [
        "scripts/research/research_prompt_builder.py",
        "docs/research/PEARL_RESEARCH_PROMPT_GENERATION_LAYER.md",
    ],
    "I016": [
        "docs/specs/session_mining_batch_20260718/FREE_TO_PAID_LADDER_V1_SPEC.md"
    ],
    "I017": [],
    "I018": [],
    "I019": [],
    "I020": ["artifacts/audio/presenter/"],
    "I021": ["teachers/"],
    "I022": [],
    "I023": ["config/localization/"],
    "I024": [
        "docs/specs/session_mining_batch_20260718/HUMAN_CALIBRATED_JUDGE_V1_SPEC.md"
    ],
    "I025": [
        "docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md",
        "docs/specs/session_mining_batch_20260718/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md",
    ],
    "I026": [],
    "I027": [],
    "I028": ["scripts/manga/character_individuation"],
    "I029": ["scripts/manga/"],
    "I030": [],
    "I031": ["config/localization/quality_contracts/"],
    "I032": [],
    "I033": [
        "docs/specs/session_mining_batch_20260718/ARTIFACTS_RETENTION_POLICY_V1_SPEC.md"
    ],
    "I034": [],
    "I035": [],
    "I036": [],
    "I037": [],
    "I038": ["docs/PEARL_NEWS_WRITER_SPEC.md"],
    "I039": [],
    "I040": [],
    "I041": ["docs/NAMING_COVER_SYSTEM_37x14.md"],
    "I042": [],
    "I043": [],
    "I044": [],
    "I045": [],
    "I046": [],
    "I047": ["artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv"],
    "I048": [
        "docs/specs/session_mining_batch_20260718/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md"
    ],
    "I049": ["docs/NAMING_COVER_SYSTEM_37x14.md"],
    "I050": [
        "artifacts/catalog_visibility/devotion_path_unified_catalog_dashboard.html"
    ],
}

FORCED = {
    "I008": "DUPLICATE_OF_PRIOR_MINING",
    "I011": "DUPLICATE_OF_PRIOR_MINING",
    "I016": "DUPLICATE_OF_PRIOR_MINING",
    "I024": "DUPLICATE_OF_PRIOR_MINING",
    "I040": "DUPLICATE_OF_PRIOR_MINING",
    "I039": "OPERATOR_GATE",
    "I044": "OPERATOR_GATE",
}

META = [
    ("I001", "Author resolution wiring into assembly pipeline", "pipeline_gates", "2431a4be", 5, 5, "Cross-check author system memory"),
    ("I002", "Unified personas readiness: atoms left for writing books", "catalog_atoms", "9ad29a26", 5, 5, "Atom cohesion / coverage"),
    ("I003", "Teacher-mode strict + fallback plan completion", "pipeline_gates", "0acf3b70", 4, 4, "Teacher onboarding packs later"),
    ("I004", "English catalog creation without assembling books", "catalog_atoms", "2005e463", 3, 3, "Catalog evolved since Feb"),
    ("I005", "Author signature / blueprint cover-pic system", "covers_brand", "ba905820", 5, 4, "Cover five-layer spec exists; uniqueness offline in last-30d"),
    ("I006", "family_id enum drift silent corruption fix", "pipeline_gates", "754099c5", 4, 5, "Confirm dedicated CI gate"),
    ("I007", "Catalog knob usage-percent analyzer", "research_tooling", "f42cad21", 4, 4, "Pipeline matrix exists; usage-% analyzer thin"),
    ("I008", "DOCS_INDEX completeness / V4 wiring gate", "governance_ci", "f067a5d7", 4, 3, "session_mining RN-9"),
    ("I009", "Pearl Prime book-template bridge into freebies/immersion", "pipeline_gates", "61d46e39", 4, 4, "Freebie harbor pack"),
    ("I010", "Pearl News editorial article structure / org wiring", "pearl_news", "5643f03a", 5, 4, "Sidebar later; editorial gaps may remain"),
    ("I011", "AI-assisted therapeutic book assembly beyond metadata", "pipeline_gates", "cf278b1b", 4, 5, "SPEC-4 merge"),
    ("I012", "Full-repo core-function operator UI / system status console", "research_tooling", "aba05c79", 4, 3, "PhoenixControl restored; 100% aspirational"),
    ("I013", "EI V2 hybrid system completeness", "pipeline_gates", "2c37ac68", 3, 4, "May be superseded"),
    ("I014", "V4 freebies + immersion ecosystem completion", "social_video", "6b3eac83", 4, 3, "Freebie harbor pack"),
    ("I015", "Continuous deep research plane (scheduled, not one-shot)", "research_tooling", "7654d26d", 5, 3, "Builder exists; continuous plane missing"),
    ("I016", "Marketing system wiring for monetization completeness", "social_video", "eef58738", 4, 3, "SPEC-6"),
    ("I017", "Video thumbnail contract (thumb.jpg beside video.mp4)", "social_video", "e376fbc9", 3, 4, "Thumb contract enforcement"),
    ("I018", "Brand media generation canonical path", "covers_brand", "f315b072", 4, 4, "IMG_RENDER dual path later"),
    ("I019", "Brand-wizard-app UX continuation", "covers_brand", "9ca9742d", 4, 3, "Last-30d offline"),
    ("I020", "Video pipeline handoff / series assembly resume", "social_video", "59d869bd", 4, 4, "Presenter audio exists"),
    ("I021", "13 teacher YouTube video banks assembly", "social_video", "f4ec4722", 4, 4, "Partial likely"),
    ("I022", "TikTok body-awareness shot plans for teachers", "social_video", "c4a47e5a", 3, 3, "Ahjan QA then scale"),
    ("I023", "CJK teacher topic-pack overlays + per-language system prompts", "translation", "7b85b693", 4, 4, "CJK6 doctrine evolved"),
    ("I024", "Iterative catalog quality refinement loop", "pipeline_gates", "2fe91134", 4, 5, "SPEC-4 merge"),
    ("I025", "Atom gap analysis: cohesive flow, bridges, bestseller structure", "catalog_atoms", "fc9e7c1f", 5, 5, "SPEC-1 + bestseller doctrine"),
    ("I026", "Music-mode brand integration + freebie funnel", "social_video", "44b6d363", 5, 4, "Music-mode pack undispached"),
    ("I027", "Musician survey → music mode implementation", "social_video", "8175c0a0", 3, 3, "Pairs I026"),
    ("I028", "Manga V2 character individuation prompt-builder", "manga", "9762773d", 4, 4, "Dir exists; completeness unknown"),
    ("I029", "Manga V2 lettering / bubble layer (audit P0-2)", "manga", "5fab9ed4", 5, 5, "Lettering proof wave blocked in exports"),
    ("I030", "Catalog 800 auto-generator", "catalog_atoms", "2e48dda5", 4, 4, "project_800 memory"),
    ("I031", "Localization quality contracts CI enforcement depth", "translation", "643f74db", 4, 4, "Contracts folder exists"),
    ("I032", "Feature-knob angle_id registry join", "catalog_atoms", "59da2ac9", 4, 5, "PR #974 era"),
    ("I033", "Manga brand×locale gap matrix (LFS pointer vs present)", "manga", "d914dcda", 5, 4, "SPEC-8 overlap"),
    ("I034", "Book + audiobook buying platform storefront spec", "research_tooling", "fef9c8bd", 5, 3, "Snipcart/Stripe operator gate; platform thin"),
    ("I035", "Church/brand/payment plans integration", "covers_brand", "4286531d", 2, 2, "Niche"),
    ("I036", "RunComfy cost-alert widget on brand_admin", "covers_brand", "80df403d", 3, 3, "Cost alert dashboard ws"),
    ("I037", "US marketing plan consolidation", "social_video", "7a45b126", 3, 2, "May be superseded"),
    ("I038", "Pearl News per-brand mapping leftover", "pearl_news", "eac25063", 4, 3, "OPD-119/121 leftover"),
    ("I039", "Metricool X/Twitter channel decision ($5 add-on)", "social_video", "export_303", 3, 2, "OPERATOR_GATE"),
    ("I040", "Catalog PLAN-completeness audit 14×39", "catalog_atoms", "export_351", 3, 3, "Last-30d PLAN green offline"),
    ("I041", "Waystream cover durable delta-queue", "covers_brand", "export_355", 4, 4, "Authority docs; delta lane thin"),
    ("I042", "Manga structural-composition MVP", "manga", "export_357", 5, 5, "CODE-WIRED vs EXECUTED-REAL"),
    ("I043", "Manga PassB reading-graph + spread + JLREQ SFX lettering proof", "manga", "export_362", 5, 5, "Export BLOCKED — bar packet not assembled"),
    ("I044", "Cloud/Codespaces substrate fanout for manga", "governance_ci", "export_361", 3, 3, "OPERATOR_GATE"),
    ("I045", "Books-first leftovers: STORY seeding + 4-cell rebuild", "pipeline_gates", "export_366", 5, 5, "Closeout next-step after #5530 era"),
    ("I046", "ProPrime modes 100% merge wave", "pipeline_gates", "export_365", 3, 3, "Verify still active"),
    ("I047", "Anti-reinvention architecture enforcement", "governance_ci", "memory:project_anti_reinvention_architecture", 4, 3, "Authority map exists"),
    ("I048", "Atom cohesion chunked plan execution", "catalog_atoms", "memory:project_atom_cohesion_chunked_plan", 5, 5, "Pairs I025 / SPEC-1"),
    ("I049", "Brand registry 37×14 unification completion", "covers_brand", "memory:project_brand_registry_37x14_unification", 5, 4, "Naming cover system doc"),
    ("I050", "Devotion Path catalog readiness (flagged not ready)", "catalog_atoms", "memory:project_devotion_path_catalog_not_ready", 3, 3, "Dashboards ≠ readiness"),
]


def resolve(catalog, src):
    if src.startswith(("export_", "memory:")):
        return src, src
    if src in catalog:
        c = catalog[src]
        return c[0], c[4]
    for k, c in catalog.items():
        if len(k) == 36 and k.startswith(src):
            return k, c[4]
    return src, ""


def quote(raw_by_session, sid, fallback):
    ideas = raw_by_session.get(sid) or []
    for idea in ideas:
        q = idea.get("quote_or_signal") or ""
        if re.search(r"(?i)not yet|missing|should|proposal|implement|next step|TODO|never", q):
            return q[:240]
    if ideas:
        return (ideas[0].get("quote_or_signal") or ideas[0].get("first_user") or fallback)[:240]
    return fallback[:240]


def main() -> int:
    raw_by_session = {}
    for line in (OUT / "IDEA_BACKLOG_RAW.jsonl").read_text(encoding="utf-8").splitlines():
        o = json.loads(line)
        raw_by_session.setdefault(o["source_session"], []).append(o)

    catalog = {}
    for line in (OUT / "SESSION_CATALOG.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split("\t")
        catalog[cols[0]] = cols
        catalog[cols[0][:8]] = cols

    sec = json.loads((OUT / "SECONDARY_PASS.json").read_text(encoding="utf-8"))
    cat_sum = json.loads((OUT / "CATALOG_SUMMARY.json").read_text(encoding="utf-8"))

    rows = []
    for iid, title, theme, src, repo, pipe, prior in META:
        sid, prev = resolve(catalog, src)
        evid = EVIDENCE.get(iid) or []
        if iid in FORCED:
            status = FORCED[iid]
        elif not evid:
            status = "TRULY_MISSING"
        elif repo >= 4:
            status = "PARTIAL"
        else:
            status = "LIKELY_LANDED"

        if sid.startswith("export_"):
            q = ""
            for er in sec["uncovered_exports"]:
                if er["id"] == sid:
                    q = (er.get("signals") or [er.get("preview", "")])[0][:240]
                    break
        elif sid.startswith("memory:"):
            q = ""
            for mr in sec["memory_titles"]:
                if mr["id"] == sid:
                    q = mr.get("preview", "")[:240]
                    break
        else:
            q = quote(raw_by_session, sid, prev or title)

        score = repo + pipe + (
            2 if status == "TRULY_MISSING" else 1 if status == "PARTIAL" else 0
        )
        rows.append(
            {
                "idea_id": iid,
                "title": title,
                "theme": theme,
                "source_session": sid,
                "quote_or_signal": (q or title).replace("\t", " ").replace("\n", " "),
                "status_guess": status,
                "repo_relevance": repo,
                "pipeline_relevance": pipe,
                "evidence_paths": (";".join(evid[:6]) if evid else "(no path hit)"),
                "prior_note": prior,
                "score": score,
            }
        )

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
                            r["prior_note"][:200],
                        ]
                    )
                    + "\n"
                )

    (OUT / "IDEA_BACKLOG_ENRICHED.json").write_text(
        json.dumps(rows_sorted, indent=2), encoding="utf-8"
    )

    # WAVE_PROGRESS
    (OUT / "WAVE_PROGRESS.md").write_text(
        f"""# WAVE_PROGRESS — archived session audit >30d (2026-07-22)

Cutoff: **2026-06-22** (mtime). Corpus: Cursor `agent-transcripts`.

| Wave | Scope | Status | Notes |
|---|---|---|---|
| Phase 0 | Catalog 569 sessions | DONE | `SESSION_CATALOG.tsv` |
| Phase 1 | Triage | DONE | DEEP={cat_sum['disposition_counts'].get('DEEP')} SKIM={cat_sum['disposition_counts'].get('SKIM')} SKIP={cat_sum['disposition_counts'].get('SKIP')} ALREADY_MINED={cat_sum['disposition_counts'].get('ALREADY_MINED')} |
| W1 | 2026-02 (31) | DONE | all non-SKIP deep-extracted |
| W2 | 2026-03 (216 → top 40 DEEP) | DONE | capped DEEP |
| W3 | 2026-04 (152 → top 35 DEEP) | DONE | capped DEEP |
| W4 | 2026-05 (167 → top 35 DEEP) | DONE | capped DEEP |
| W5 | 2026-06 pre-cutoff (3) | DONE | 1 DEEP |
| W6 | 16 uncovered exports + 78 old memory titles | DONE | `SECONDARY_PASS.json` |
| Phase 3–4 | Reconcile + ranked findings | DONE | `IDEA_BACKLOG.tsv`, `RANKED_FINDINGS.md` |

Raw signal volume: `{sum(1 for _ in (OUT/'IDEA_BACKLOG_RAW.jsonl').open())}` lines in `IDEA_BACKLOG_RAW.jsonl`.
Curated keepers: 50 rows in `IDEA_BACKLOG.tsv`.

Resume pointer: **audit complete** — next operator action is pick keepers from `RANKED_FINDINGS.md` (ask Piper for packs if desired).
""",
        encoding="utf-8",
    )

    # RANKED_FINDINGS
    keepers = [
        r
        for r in rows_sorted
        if r["status_guess"] in ("TRULY_MISSING", "PARTIAL", "OPERATOR_GATE")
        and (r["repo_relevance"] + r["pipeline_relevance"]) >= 7
    ]
    parked = [
        r
        for r in rows_sorted
        if r["status_guess"] in ("TRULY_MISSING", "PARTIAL")
        and (r["repo_relevance"] + r["pipeline_relevance"]) < 7
    ]
    noreopen = [
        r
        for r in rows_sorted
        if r["status_guess"]
        in ("DUPLICATE_OF_PRIOR_MINING", "LIKELY_LANDED", "SUPERSEDED")
    ]
    opgate = [r for r in rows_sorted if r["status_guess"] == "OPERATOR_GATE"]

    def fmt(r, n):
        sid = r["source_session"]
        if sid.startswith("export_"):
            link = f"`old_chat_specs` {sid}"
        elif sid.startswith("memory:"):
            link = f"`{sid}`"
        else:
            short = sid[:8] if len(sid) >= 8 else sid
            link = f"[{r['title'][:40]}]({sid})"
        return (
            f"{n}. **{r['idea_id']} — {r['title']}**  \n"
            f"   Status: `{r['status_guess']}` · theme `{r['theme']}` · "
            f"repo={r['repo_relevance']} pipeline={r['pipeline_relevance']}  \n"
            f"   Source: {link}  \n"
            f"   Signal: {r['quote_or_signal'][:180]}  \n"
            f"   Evidence: `{r['evidence_paths'][:160]}`  \n"
            f"   Note: {r['prior_note']}\n"
        )

    themes = Counter(r["theme"] for r in keepers)
    status_c = Counter(r["status_guess"] for r in rows)

    md = []
    md.append("# RANKED_FINDINGS — Archived Sessions >30d Idea Audit (2026-07-22)\n")
    md.append(
        "Audit of Cursor agent transcripts with **mtime before 2026-06-22** "
        "(569 sessions), plus 16 uncovered `old_chat_specs` exports and 78 older "
        "Claude memory titles.\n"
    )
    md.append(
        "**Not re-audited:** last-30-days sessions (Untitled 386 / "
        "`20260721_archived_session_followup`) and already-extracted "
        "session-mining specs (2026-07-18).\n"
    )
    md.append("## Corpus summary\n")
    md.append(
        f"- Catalogued: **{cat_sum['total_sessions']}** sessions "
        f"(months {cat_sum['months']})\n"
        f"- Triage: `{cat_sum['disposition_counts']}`\n"
        f"- Curated idea rows: **{len(rows)}** · status `{dict(status_c)}`\n"
        f"- High-leverage keepers below: **{len(keepers)}**\n"
    )
    md.append("## Top keepers (good + still useful)\n")
    for i, r in enumerate(keepers[:35], 1):
        md.append(fmt(r, i))

    md.append("## By theme (keepers)\n")
    for t, n in themes.most_common():
        md.append(f"- `{t}`: {n}\n")

    md.append("## Operator gates (not agent-missed)\n")
    if not opgate:
        md.append("- (none in curated set beyond those in keepers)\n")
    for i, r in enumerate(opgate, 1):
        md.append(fmt(r, i))

    md.append("## Interesting but lower priority (parked)\n")
    for i, r in enumerate(parked[:12], 1):
        md.append(
            f"{i}. `{r['idea_id']}` {r['title']} — `{r['status_guess']}` "
            f"(r{r['repo_relevance']}/p{r['pipeline_relevance']})\n"
        )

    md.append("## Do not reopen\n")
    md.append(
        "These are already covered by prior mining packs/specs, or scaffolding "
        "is already on disk as LIKELY_LANDED:\n"
    )
    for r in noreopen:
        md.append(
            f"- `{r['idea_id']}` {r['title']} — `{r['status_guess']}` "
            f"({r['prior_note']})\n"
        )

    md.append("## Highest-leverage next actions (operator pick)\n")
    md.append(
        "1. **Manga bar / lettering / structural composition** — I042, I043, I029 "
        "(exports already marked BLOCKED; do not fake EXECUTED-REAL).\n"
        "2. **Books-first STORY seeding + 4-cell rebuild** — I045 "
        "(explicit leftover from export 366 closeout).\n"
        "3. **Music-mode freebie funnel** — I026 "
        "(pack may already exist undispached; land rather than re-spec).\n"
        "4. **Buying platform / storefront spec** — I034 "
        "(distinct from Snipcart key operator gate).\n"
        "5. **Continuous research plane** — I015 "
        "(builder exists; schedule/cadence does not).\n"
        "6. **Atom cohesion / gap / bestseller structure** — I025, I048 "
        "(merge into SPEC-1 lane; do not fork).\n"
        "7. **Cover five-layer / 37×14 registry** — I005, I049 "
        "(spec on disk; uniqueness still a live complaint in last-30d).\n"
    )
    md.append("## Artifacts\n")
    md.append(
        "- `SESSION_CATALOG.tsv`\n"
        "- `IDEA_BACKLOG.tsv` / `IDEA_BACKLOG_ENRICHED.json`\n"
        "- `IDEA_BACKLOG_RAW.jsonl` (machine signals from DEEP sessions)\n"
        "- `DEDUP_LEDGER.tsv`\n"
        "- `SECONDARY_PASS.json`\n"
        "- `WAVE_PROGRESS.md`\n"
        "- Scanner: `scripts/audit/archived_session_gt30d_scanner.py`\n"
        "- Extractor: `scripts/audit/archived_session_gt30d_deep_extract.py`\n"
        "- Finalize: `scripts/audit/archived_session_gt30d_finalize.py`\n"
    )

    (OUT / "RANKED_FINDINGS.md").write_text("".join(md), encoding="utf-8")
    print("STATUS", dict(status_c))
    print("keepers", len(keepers))
    print("wrote", OUT / "IDEA_BACKLOG.tsv")
    print("wrote", OUT / "RANKED_FINDINGS.md")
    print("wrote", OUT / "WAVE_PROGRESS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

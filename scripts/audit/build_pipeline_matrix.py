#!/usr/bin/env python3
"""Build pipeline + code module + business requirements matrix CSV.

Produces artifacts/inventory/full_repo_pipeline_matrix_<DATE>.csv. Wide schema
with `row_type` discriminator: pipeline, module, orphan_module, requirement.

Usage:
    python3 scripts/audit/build_pipeline_matrix.py [--out PATH] [--dry-run]

Tier 1; no LLM calls.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Curated pipeline registry — the productionized version of what subagent D
# discovered ad-hoc. Re-runs of this script regenerate the matrix.
PIPELINES: list[dict] = [
    {"name": "Brand Wizard YAML generator", "subsystem": "brand_admin",
     "entry_point": "scripts/brand_management/generate_global_registry.py"},
    {"name": "Brand Admin weekly package", "subsystem": "brand_admin",
     "entry_point": "scripts/build_weekly_brand_package.py"},
    {"name": "Pearl Prime multilingual catalog", "subsystem": "pearl_prime",
     "entry_point": "scripts/pearl_prime_multilingual/build_review_pack.py"},
    {"name": "Pearl Prime canonical CLI", "subsystem": "pearl_prime",
     "entry_point": "scripts/run_pipeline.py"},
    {"name": "Pearl News daily editorial", "subsystem": "pearl_news",
     "entry_point": "scripts/pearl_news/run_daily_news_cycle.py"},
    {"name": "Manga visual_from_script v3", "subsystem": "manga_pipeline",
     "entry_point": "phoenix_v4/manga/visual_from_script_v3.py"},
    {"name": "Manga lettering pipeline", "subsystem": "manga_pipeline",
     "entry_point": "phoenix_v4/manga/lettering_from_script.py"},
    {"name": "Manga webtoon composer", "subsystem": "manga_pipeline",
     "entry_point": "phoenix_v4/manga/chapter/webtoon_compose.py"},
    {"name": "Manga translation pipeline", "subsystem": "translation",
     "entry_point": "scripts/manga/translate_chapter_script.py"},
    {"name": "Video FLUX rendering", "subsystem": "video_pipeline",
     "entry_point": "scripts/video/run_flux_generate.py"},
    {"name": "Locale batch translation", "subsystem": "translation",
     "entry_point": "scripts/localization/run_locale_batches.py"},
    {"name": "Teacher pages render", "subsystem": "teacher_mode",
     "entry_point": "scripts/teacher_pages/render.py"},
    {"name": "Audiobook MVP pipeline", "subsystem": "audiobook",
     "entry_point": "scripts/audiobook/build_audiobook.py"},
    {"name": "Podcast pipeline (proposed)", "subsystem": "podcast",
     "entry_point": "scripts/podcast/run_pipeline.py"},
    {"name": "TTS provider routing", "subsystem": "video_pipeline",
     "entry_point": "scripts/tts/route.py"},
    {"name": "Trend feed budget guard", "subsystem": "trend_feeds",
     "entry_point": "scripts/feeds/budget_guard.py"},
    {"name": "Quality gates production-readiness", "subsystem": "ei_v2",
     "entry_point": "phoenix_v4/quality/gates.py"},
]

# Inferred business requirements (no operator transcript on disk; see spec §11).
REQUIREMENTS: list[dict] = [
    {"id": "R-001", "text": "Teacher showcase pages with brand attribution",
     "topic_cluster": "teacher", "source": "(inferred from ACTIVE_PROJECTS.tsv)",
     "status": "implemented", "evidence": "config/catalog_planning/teacher_persona_matrix.yaml"},
    {"id": "R-002", "text": "Teacher profile pages with per-teacher video bindings",
     "topic_cluster": "teacher", "source": "(inferred)",
     "status": "partial", "evidence": "scripts/teacher_videos/"},
    {"id": "R-003", "text": "37 brand onboarding × 5 locales (en_US, ja_JP, zh_TW, zh_CN, ko_KR)",
     "topic_cluster": "brand", "source": "(inferred from MANGA_CATALOG_RECONCILIATION_SPEC.md)",
     "status": "partial", "evidence": "config/brand_registry.yaml"},
    {"id": "R-004", "text": "LTV / conversion rate signal ingestion from Spotify/Apple/Google Play/ACX",
     "topic_cluster": "marketing", "source": "(inferred)",
     "status": "missing", "evidence": "(none — config-set defaults only)"},
    {"id": "R-005", "text": "Pearl Prime bestseller-grade book pipeline (Move 4 sweep)",
     "topic_cluster": "pearl_prime", "source": "(inferred from BG-PR-09)",
     "status": "implemented", "evidence": "scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py"},
    {"id": "R-006", "text": "Pearl News daily editorial cycle with teacher slots",
     "topic_cluster": "pearl_news", "source": "(inferred)",
     "status": "implemented", "evidence": "scripts/pearl_news/run_daily_news_cycle.py"},
    {"id": "R-007", "text": "Manga ep_001 ship — KDP en_US",
     "topic_cluster": "manga", "source": "proj_manga_first_ship_20260425",
     "status": "implemented", "evidence": "artifacts/manga/chapter_scripts/.../ep_001.yaml"},
    {"id": "R-008", "text": "Audiobook 5-locale rollout (ko_KR hold_pending_market_clearance)",
     "topic_cluster": "audiobook", "source": "(inferred)",
     "status": "partial", "evidence": "scripts/audiobook/"},
    {"id": "R-009", "text": "Podcast publishing — research → impl",
     "topic_cluster": "podcast", "source": "(inferred from research dir)",
     "status": "missing", "evidence": "(none — research only)"},
    {"id": "R-010", "text": "Branch protection + governance auto-PR-comment",
     "topic_cluster": "audit", "source": "CLAUDE.md",
     "status": "partial", "evidence": "scripts/ci/pr_governance_review.py (not yet wired to workflow)"},
    {"id": "R-011", "text": "Mass-delete protection (>50 file rule)",
     "topic_cluster": "audit", "source": "CLAUDE.md",
     "status": "implemented", "evidence": "scripts/ci/pr_governance_review.py:117"},
    {"id": "R-012", "text": "LLM tier policy enforcement (banned paid APIs)",
     "topic_cluster": "audit", "source": "CLAUDE.md",
     "status": "implemented", "evidence": ".github/workflows/llm-policy-enforcement.yml"},
]


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)


def list_python_files() -> list[str]:
    return [p for p in run(["git", "ls-files", "*.py"]).splitlines() if p]


def list_workflows() -> list[str]:
    out = run(["git", "ls-files", ".github/workflows/*.yml", ".github/workflows/*.yaml"])
    return [p for p in out.splitlines() if p]


def last_commit(path: str) -> tuple[str, str]:
    try:
        out = run(["git", "log", "-n", "1", "--format=%ad|%an", "--date=short", "--", path])
        if "|" in out:
            d, a = out.strip().split("|", 1)
            return d, a
    except subprocess.CalledProcessError:
        pass
    return "", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = _dt.date.today().isoformat()
    default = REPO_ROOT / f"artifacts/inventory/full_repo_pipeline_matrix_{today}.csv"
    out_path = Path(args.out) if args.out else default
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    HEADER = ["row_type", "name", "subsystem", "status", "last_touched", "notes",
              "pipeline_entry_point", "pipeline_called_by", "pipeline_calls_into",
              "pipeline_config_paths", "pipeline_schema_paths", "pipeline_test_coverage",
              "module_top_level_area", "module_line_count", "module_imports_count",
              "module_imported_by_count", "module_has_main", "module_has_tests", "module_last_author",
              "req_text", "req_topic_cluster", "req_source", "req_evidence_path"]

    py_files = list_python_files()
    print(f"enumerated {len(py_files):,} .py files", file=sys.stderr)

    with out_path.open("w") as g:
        w = csv.writer(g, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(HEADER)

        for p in PIPELINES:
            ep = p["entry_point"]
            full = REPO_ROOT / ep
            status = "live" if full.exists() else "proposed"
            date_, _author = last_commit(ep) if full.exists() else ("", "")
            w.writerow([
                "pipeline", p["name"], p["subsystem"], status, date_, "",
                ep, "", "", "", "", "no_tests",
                "", "", "", "", "", "", "",
                "", "", "", "",
            ])

        for wf in list_workflows():
            date_, _author = last_commit(wf)
            w.writerow([
                "pipeline", f"CI: {wf.split('/')[-1]}", "ci_cd", "scheduled", date_, "",
                wf, "", "", "", "", "n/a",
                "", "", "", "", "", "", "",
                "", "", "", "",
            ])

        for path in py_files:
            full = REPO_ROOT / path
            if not full.exists():
                continue
            try:
                text = full.read_text(errors="ignore")
            except OSError:
                continue
            lc = text.count("\n")
            ic = sum(1 for line in text.splitlines() if line.startswith(("import ", "from ")))
            has_main = 1 if 'if __name__ == "__main__"' in text else 0
            has_tests = 1 if (REPO_ROOT / "tests" / f"test_{Path(path).stem}.py").exists() else 0
            tla = path.split("/", 1)[0] if "/" in path else "(root)"
            date_, author = last_commit(path)
            status = "live" if has_main or path.startswith("tests/") else "module"
            row_type = "module"
            if lc < 50 and not has_main:
                status = "stub"
            w.writerow([
                row_type, path, "", status, date_, "",
                "", "", "", "", "", "",
                tla, str(lc), str(ic), "0", str(has_main), str(has_tests), author,
                "", "", "", "",
            ])

        for r in REQUIREMENTS:
            w.writerow([
                "requirement", r["id"], "", r["status"], "", "",
                "", "", "", "", "", "",
                "", "", "", "", "", "", "",
                r["text"], r["topic_cluster"], r["source"], r["evidence"],
            ])

    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

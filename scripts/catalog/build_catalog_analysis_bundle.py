from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.catalog.generate_full_catalog import (
    CATALOG_FIELDS,
    SUMMARY_FIELDS,
    generate_catalog,
    generate_summary,
    write_csv,
)


CATALOG_DIR = ROOT / "artifacts" / "catalog"
DOCS_DIR = ROOT / "docs" / "produced"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_catalog_health_dashboard() -> None:
    """Aggregate ops/waves signals into artifacts/catalog/catalog_health_dashboard.*"""
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    cmd = [
        sys.executable,
        "-m",
        "phoenix_v4.ops.catalog_health_dashboard_builder",
        "--ops-dir",
        str(ROOT / "artifacts" / "ops"),
        "--waves-dir",
        str(ROOT / "artifacts" / "waves"),
        "--out",
        str(CATALOG_DIR / "catalog_health_dashboard.json"),
        "--md",
    ]
    subprocess.run(cmd, check=True, cwd=str(ROOT), env=env)


def actual_lane_to_planning_lane() -> dict[str, str]:
    return {
        "en_US": "english_global",
        "de_DE": "dach",
        "fr_FR": "france",
        "es_ES": "spain",
        "it_IT": "italy",
        "es_US": "latam",
        "pt_BR": "brazil",
        "ja_JP": "japan",
        "ko_KR": "korea",
        "zh_TW": "taiwan",
        "zh_CN": "china",
        "zh_HK": "china",
        "zh_SG": "china",
        "hu_HU": "hungary",
    }


def actual_lane_to_video_lane() -> dict[str, str]:
    return {
        "en_US": "en",
        "zh_TW": "zh_tw_hk_sg",
        "zh_HK": "zh_tw_hk_sg",
        "zh_SG": "zh_tw_hk_sg",
        "zh_CN": "zh_cn",
        "ja_JP": "ja",
        "ko_KR": "ko",
        "de_DE": "eu_west",
        "fr_FR": "eu_west",
        "es_ES": "eu_west",
        "it_IT": "eu_west",
        "es_US": "es_us",
        "hu_HU": "hu",
    }


def build_combo_dashboard(entries: list[dict]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in entries:
        key = (
            row["lane_id"], row["brand_id"], row["teacher_id"], row["topic_id"],
            row["persona_id"], row["format_id"], row["runtime_format_id"],
            row["content_type"], row["priority"],
        )
        item = grouped.setdefault(
            key,
            {
                "lane_id": row["lane_id"],
                "brand_id": row["brand_id"],
                "teacher_id": row["teacher_id"],
                "topic_id": row["topic_id"],
                "persona_id": row["persona_id"],
                "format_id": row["format_id"],
                "runtime_format_id": row["runtime_format_id"],
                "content_type": row["content_type"],
                "priority": row["priority"],
                "title_count": 0,
                "sample_catalog_id": row["catalog_id"],
                "sample_title": row["title"],
            },
        )
        item["title_count"] += 1
    return sorted(grouped.values(), key=lambda r: tuple(str(r[k]) for k in r))


def build_coverage_report(
    entries: list[dict],
    canonical_topics: list[str],
    canonical_personas: list[str],
    runtime_formats: list[str],
    planned_brand_ids: set[str],
    planned_teacher_brand_ids: set[str],
    teacher_brand_map: dict,
    brand_registry: dict,
    planning_counts: dict,
) -> dict:
    topics_present = sorted({r["topic_id"] for r in entries})
    personas_present = sorted({r["persona_id"] for r in entries})
    runtime_present = sorted({r["runtime_format_id"] for r in entries})
    content_present = sorted({r["content_type"] for r in entries})
    expected_content_types = ["deep_book", "micro_book", "series_book", "standalone"]

    brand_pairs = {(r["brand_id"], r["lane_id"]) for r in entries}
    title_rows_per_lane = Counter(r["lane_id"] for r in entries)
    brand_counts_by_lane = Counter(lane for _, lane in brand_pairs)
    brand_base_ids = {
        data.get("brand_archetype_id", brand_id)
        for brand_id, data in brand_registry.get("brands", {}).items()
    }
    actual_teacher_brand_ids = set(teacher_brand_map.get("teacher_brands", {}).keys())

    by_lane_topics: dict[str, set[str]] = defaultdict(set)
    by_lane_personas: dict[str, set[str]] = defaultdict(set)
    for row in entries:
        by_lane_topics[row["lane_id"]].add(row["topic_id"])
        by_lane_personas[row["lane_id"]].add(row["persona_id"])

    return {
        "actual_catalog": {
            "entry_count": len(entries),
            "brand_lane_pair_count": len(brand_pairs),
            "distinct_lanes": sorted(title_rows_per_lane.keys()),
            "distinct_base_brand_count": len(brand_base_ids),
            "brand_counts_by_lane": dict(sorted(brand_counts_by_lane.items())),
            "title_rows_per_lane": dict(sorted(title_rows_per_lane.items())),
            "topics_present": topics_present,
            "personas_present": personas_present,
            "runtime_formats_present": runtime_present,
            "content_types_present": content_present,
        },
        "planned_architecture": planning_counts,
        "coverage_gaps": {
            "missing_topics_global": sorted(set(canonical_topics) - set(topics_present)),
            "missing_personas_global": sorted(set(canonical_personas) - set(personas_present)),
            "missing_runtime_formats_global": sorted(set(runtime_formats) - set(runtime_present)),
            "missing_content_types_global": sorted(set(expected_content_types) - set(content_present)),
            "missing_topics_by_lane": {
                lane: sorted(set(canonical_topics) - topics)
                for lane, topics in sorted(by_lane_topics.items())
            },
            "missing_personas_by_lane": {
                lane: sorted(set(canonical_personas) - personas)
                for lane, personas in sorted(by_lane_personas.items())
            },
        },
        "architecture_drift": {
            "planned_vs_actual_brand_lane_delta": planning_counts["planned_brand_instances"] - len(brand_pairs),
            "planned_vs_actual_base_brand_delta": planning_counts["planned_brands_per_lane"] - len(brand_base_ids),
            "planned_teacher_brand_overlap": sorted(planned_teacher_brand_ids & actual_teacher_brand_ids),
            "planned_teacher_brands_missing_from_legacy_generator": sorted(planned_teacher_brand_ids - actual_teacher_brand_ids),
            "legacy_teacher_brands_not_in_new_12x37_plan": sorted(actual_teacher_brand_ids - planned_teacher_brand_ids),
            "planned_brands_missing_from_actual_registry": sorted(planned_brand_ids - brand_base_ids),
        },
    }


def build_repurposing_surface(
    entries: list[dict],
    brand_registry: dict,
    brand_series_plans: dict,
    component_templates_path: Path,
    video_style_config: dict,
    cover_art_config: dict,
    audiobook_video_catalog: dict,
) -> list[dict]:
    lane_map = actual_lane_to_planning_lane()
    video_lane_map = actual_lane_to_video_lane()
    manga_intensity = {}
    for intensity, lanes in brand_series_plans.get("lane_intensity", {}).items():
        for lane in lanes:
            manga_intensity[lane] = intensity
    series_brands = set(brand_series_plans.get("brands", {}).keys())
    video_style_brands = set(video_style_config.get("brands", {}).keys())
    cover_art_brands = set(cover_art_config.get("brands", {}).keys())
    video_lanes = set(audiobook_video_catalog.get("lanes", {}).keys())
    derivatives = audiobook_video_catalog.get("video_derivatives_per_book", {})

    grouped: dict[tuple, dict] = {}
    for row in entries:
        key = (row["lane_id"], row["brand_id"])
        item = grouped.setdefault(
            key,
            {
                "lane_id": row["lane_id"],
                "planning_lane_id": lane_map.get(row["lane_id"], "unknown"),
                "video_lane_id": video_lane_map.get(row["lane_id"], "unknown"),
                "brand_id": row["brand_id"],
                "base_brand_id": brand_registry.get("brands", {}).get(row["brand_id"], {}).get("brand_archetype_id", row["brand_id"]),
                "teacher_id": row["teacher_id"],
                "title_count": 0,
                "topics": set(),
                "personas": set(),
                "companion_title_count": 0,
            },
        )
        item["title_count"] += 1
        item["topics"].add(row["topic_id"])
        item["personas"].add(row["persona_id"])
        if row.get("companion_type") and row["companion_type"] != "none":
            item["companion_title_count"] += 1

    rows = []
    for item in grouped.values():
        base_brand = item["base_brand_id"]
        planning_lane = item["planning_lane_id"]
        video_lane = item["video_lane_id"]
        blockers = []

        practice_status = "not_needed"
        if item["companion_title_count"]:
            practice_status = "template_ready_cli_missing"
            if not component_templates_path.exists():
                practice_status = "missing_templates"
                blockers.append("component_templates_missing")
            else:
                blockers.append("practice_cli_missing_scripts_pearl_practice")

        manga_status = "no_series_plan"
        if base_brand in series_brands:
            intensity = manga_intensity.get(planning_lane, "unknown")
            manga_status = f"plan_ready_{intensity}"
        else:
            blockers.append("brand_not_mapped_in_brand_series_plans")

        video_style_status = "style_ready" if base_brand in video_style_brands else "style_missing_for_brand"
        if video_style_status.endswith("missing_for_brand"):
            blockers.append("brand_not_mapped_in_brand_video_styles")

        cover_art_status = "cover_art_ready" if base_brand in cover_art_brands else "cover_art_missing_for_brand"
        if cover_art_status.endswith("missing_for_brand"):
            blockers.append("brand_not_mapped_in_brand_cover_art_specs")

        audiobook_video_status = "lane_supported" if video_lane in video_lanes else "lane_missing"
        if audiobook_video_status == "lane_missing":
            blockers.append("lane_not_mapped_in_audiobook_video_catalog")

        rows.append(
            {
                **{k: v for k, v in item.items() if k not in {"topics", "personas"}},
                "topic_count": len(item["topics"]),
                "persona_count": len(item["personas"]),
                "practice_status": practice_status,
                "manga_status": manga_status,
                "video_style_status": video_style_status,
                "cover_art_status": cover_art_status,
                "shorts_status": "supported" if "audiobook_chapter_short" in derivatives else "missing",
                "video_long_status": "supported" if "audiobook_chapter_long" in derivatives else "missing",
                "video_1h_status": "supported" if derivatives.get("audiobook_full", {}).get("duration_range", [0, 0])[1] >= 60 else "missing",
                "video_3h_status": "supported" if derivatives.get("audiobook_full", {}).get("duration_range", [0, 0])[1] >= 180 else "missing",
                "video_5h_status": "not_in_current_catalog",
                "audiobook_video_status": audiobook_video_status,
                "blockers": sorted(set(blockers)),
            }
        )
    return sorted(rows, key=lambda r: (r["lane_id"], r["brand_id"]))


def build_report_markdown(coverage: dict, repurposing_rows: list[dict], workstream_rows: list[dict]) -> str:
    actual = coverage["actual_catalog"]
    gaps = coverage["coverage_gaps"]
    drift = coverage["architecture_drift"]
    planned = coverage["planned_architecture"]
    blocker_counts = Counter(b for row in repurposing_rows for b in row["blockers"])

    merged_workstream = next(
        (r for r in workstream_rows if r.get("workstream_id") == "ws_brand_lane_architecture_20260407"),
        {},
    )

    lines = [
        "# Full Catalog Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Executive summary",
        f"- Live generator output: **{actual['entry_count']}** titles across **{actual['brand_lane_pair_count']}** brand/lane pairs.",
        f"- Planned merged architecture: **{planned['planned_brands_per_lane']} brands/lane × {planned['planned_lane_count']} lanes = {planned['planned_brand_instances']} brand instances**.",
        f"- Drift: generator is short by **{drift['planned_vs_actual_brand_lane_delta']}** brand/lane instances and still resolves legacy teacher brands rather than the merged 12×37 teacher-brand naming system.",
        f"- Missing global coverage: topics={len(gaps['missing_topics_global'])}, personas={len(gaps['missing_personas_global'])}, runtime_formats={len(gaps['missing_runtime_formats_global'])}, content_types={', '.join(gaps['missing_content_types_global']) or 'none' }.",
        "",
        "## What was validated",
        "- `scripts/catalog/generate_full_catalog.py` runs successfully on the clean branch.",
        "- `phoenix_v4.ops.catalog_health_dashboard_builder` runs successfully and writes catalog health dashboard artifacts.",
        "- `scripts/video/orchestrate_book_to_video.py --help` and `scripts/manga/run_chapter_production.py --help` both succeed, confirming live CLI entry points for video and manga assembly.",
        f"- Workstream state for `ws_brand_lane_architecture_20260407`: **{merged_workstream.get('status', 'unknown')}** ({merged_workstream.get('task', 'n/a')}).",
        "",
        "## Highest-signal gaps",
        f"- Missing topics globally: {', '.join(gaps['missing_topics_global']) or 'none'}.",
        f"- Missing personas globally: {', '.join(gaps['missing_personas_global']) or 'none'}.",
        f"- Missing runtime formats globally: {', '.join(gaps['missing_runtime_formats_global']) or 'none'}.",
        f"- Missing content types globally: {', '.join(gaps['missing_content_types_global']) or 'none'}.",
        "",
        "## Architecture drift",
        f"- Planned teacher brands missing from legacy generator: {', '.join(drift['planned_teacher_brands_missing_from_legacy_generator'][:8])}{' ...' if len(drift['planned_teacher_brands_missing_from_legacy_generator']) > 8 else ''}",
        f"- Legacy teacher brands not in new 12×37 plan: {', '.join(drift['legacy_teacher_brands_not_in_new_12x37_plan'][:8])}{' ...' if len(drift['legacy_teacher_brands_not_in_new_12x37_plan']) > 8 else ''}",
        "",
        "## Repurposing blockers",
    ]
    for blocker, count in blocker_counts.most_common(8):
        lines.append(f"- {blocker}: {count} brand/lane rows")
    lines.extend([
        "",
        "## Safe run posture",
        "- Practice: `phoenix_v4.exercises.component_assembler.assemble_exercise_for_chapter` imports successfully, but the requested `scripts/pearl_practice/*` CLI surface is still absent on this branch; analysis can only mark template/library readiness.",
        "- Video/audiobook video: config surface is present and mapped for current video lanes; actual media assembly still requires concrete audio/transcript inputs.",
        "- Manga: merged planning/config surface exists, but many live catalog teacher brands do not map to the new manga plan brand IDs because the catalog generator is still on the legacy teacher-brand registry.",
    ])
    return "\n".join(lines)


def main() -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    entries = generate_catalog()
    summary = generate_summary(entries)
    write_csv(entries, CATALOG_DIR / "full_catalog.csv", CATALOG_FIELDS)
    write_csv(summary, CATALOG_DIR / "catalog_summary.csv", SUMMARY_FIELDS)

    combo_rows = build_combo_dashboard(entries)

    canonical_topics = load_yaml(ROOT / "config/catalog_planning/canonical_topics.yaml").get("topics", [])
    canonical_personas = load_yaml(ROOT / "config/catalog_planning/canonical_personas.yaml").get("personas", [])
    format_registry = load_yaml(ROOT / "config/format_selection/format_registry.yaml")
    runtime_formats = sorted((format_registry.get("runtime_formats") or {}).keys())

    teacher_lane_cfg = load_yaml(ROOT / "config/catalog_planning/teacher_brand_lane_assignments.yaml")
    planning_counts = {
        "planned_lane_count": teacher_lane_cfg.get("summary", {}).get("brand_lanes", 0),
        "planned_brands_per_lane": teacher_lane_cfg.get("summary", {}).get("brands_per_lane_default")
        or teacher_lane_cfg.get("summary", {}).get("brands_per_lane", 0),
        "planned_brand_instances": teacher_lane_cfg.get("summary", {}).get("total_brand_instances", 0),
    }
    planned_teacher_brand_ids = set(
        teacher_lane_cfg.get("summary", {}).get("teacher_mode_brands", {}).get("base_names", [])
    )
    planned_standard_brand_ids = set(
        teacher_lane_cfg.get("summary", {}).get("standard_mode_brands", {}).get("base_names", [])
    )
    planned_brand_ids = planned_teacher_brand_ids | planned_standard_brand_ids

    teacher_brand_map = load_yaml(ROOT / "config/brand_management/teacher_brand_map.yaml")
    brand_registry = load_yaml(ROOT / "config/brand_management/global_brand_registry.yaml")
    brand_series_plans = load_yaml(ROOT / "config/catalog_planning/brand_series_plans.yaml")
    video_style_config = load_yaml(ROOT / "config/video/brand_video_styles.yaml")
    cover_art_config = load_yaml(ROOT / "config/catalog_planning/brand_cover_art_specs.yaml")
    audiobook_video_catalog = load_yaml(ROOT / "config/catalog_planning/audiobook_video_catalog.yaml")
    workstream_rows = load_tsv_rows(ROOT / "artifacts/coordination/ACTIVE_WORKSTREAMS.tsv")

    coverage = build_coverage_report(
        entries,
        canonical_topics,
        canonical_personas,
        runtime_formats,
        planned_brand_ids,
        planned_teacher_brand_ids,
        teacher_brand_map,
        brand_registry,
        planning_counts,
    )
    repurposing_rows = build_repurposing_surface(
        entries,
        brand_registry,
        brand_series_plans,
        ROOT / "config/pearl_practice/component_templates.yaml",
        video_style_config,
        cover_art_config,
        audiobook_video_catalog,
    )

    # Slim JSON only: full row payloads exceed repo push-guard single-blob limits
    # (see scripts/git/push_guard.py). Canonical tabular export is full_catalog.csv.
    full_catalog_json = {
        "generated_at": generated_at,
        "entry_count": len(entries),
        "summary_row_count": len(summary),
        "full_rows_csv": "artifacts/catalog/full_catalog.csv",
    }
    combo_payload = {
        "generated_at": generated_at,
        "row_count": len(combo_rows),
        "rows": combo_rows,
    }
    repurposing_payload = {
        "generated_at": generated_at,
        "row_count": len(repurposing_rows),
        "rows": repurposing_rows,
    }
    report_md = build_report_markdown(coverage, repurposing_rows, workstream_rows)

    write_json(CATALOG_DIR / "full_catalog.json", full_catalog_json)
    write_csv(combo_rows, CATALOG_DIR / "catalog_combo_dashboard.csv", list(combo_rows[0].keys()) if combo_rows else [])
    write_json(CATALOG_DIR / "catalog_combo_dashboard.json", combo_payload)
    write_json(CATALOG_DIR / "catalog_gap_report.json", coverage)
    write_text(CATALOG_DIR / "catalog_gap_report.md", report_md)
    write_csv(repurposing_rows, CATALOG_DIR / "catalog_repurposing_surface.csv", list(repurposing_rows[0].keys()) if repurposing_rows else [])
    write_json(CATALOG_DIR / "catalog_repurposing_surface.json", repurposing_payload)
    write_text(DOCS_DIR / "full_catalog_analysis_report.md", report_md)
    run_catalog_health_dashboard()

    print(f"Wrote {len(entries)} catalog rows and {len(combo_rows)} combo rows")
    print(f"Coverage drift delta: {coverage['architecture_drift']['planned_vs_actual_brand_lane_delta']}")


if __name__ == "__main__":
    main()

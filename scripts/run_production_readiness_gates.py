#!/usr/bin/env python3
"""
Run V4.5 Production Readiness gates (29 conditions).
Gate 16 + 16b: freebie governance — validate_freebie_density and cta_signature_caps run with same index (single scope).
Usage: from repo root: python scripts/run_production_readiness_gates.py
       or: python -m scripts.run_production_readiness_gates
"""
from __future__ import annotations

import os
import subprocess
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

RESULTS = []


def gate(name: str, passed: bool, detail: str = "", skip: bool = False):
    status = "SKIP" if skip else ("PASS" if passed else "FAIL")
    RESULTS.append((name, status, detail))
    return passed


def _summarize_story_band_gaps(persona_id: str, topic_id: str, arc_path: Path) -> str:
    """
    Build an actionable content-gap summary for STORY band coverage.
    Returns empty string when summary cannot be computed.
    """
    try:
        from phoenix_v4.planning.pool_index import PoolIndex
    except Exception:
        return ""
    try:
        pool_index = PoolIndex()
        story_pool = pool_index.get_pool("STORY", persona_id, topic_id, None)
        band_counts: dict[int, int] = {}
        for e in story_pool:
            b = int((e.metadata or {}).get("band", 3))
            band_counts[b] = band_counts.get(b, 0) + 1
        if not arc_path.exists():
            return ""
        arc = yaml.safe_load(arc_path.read_text()) or {}
        curve = arc.get("emotional_curve") or []
        if not isinstance(curve, list) or not curve:
            return ""
        available = set(band_counts.keys())
        missing = [
            f"ch{idx + 1}->B{required}"
            for idx, required in enumerate(curve)
            if isinstance(required, int) and required not in available
        ]
        counts_str = ", ".join(f"B{k}:{band_counts[k]}" for k in sorted(band_counts))
        if not missing:
            return f"story band coverage ok for arc; pool bands: {counts_str or 'none'}"
        missing_str = ", ".join(missing[:12])
        extra = f" (+{len(missing) - 12} more)" if len(missing) > 12 else ""
        return (
            "content gap: STORY band coverage missing for required arc chapters: "
            f"{missing_str}{extra}; pool bands: {counts_str or 'none'}. "
            "Add STORY atoms for missing BAND(s) or adjust arc emotional_curve."
        )
    except Exception:
        return ""


def main() -> int:
    failed = 0

    # --- 1. Canonical Spec Is Single Source of Truth ---
    writer_spec = REPO_ROOT / "specs" / "PHOENIX_V4_5_WRITER_SPEC.md"
    canonical_spec = REPO_ROOT / "specs" / "PHOENIX_V4_CANONICAL_SPEC.md"
    if not gate(
        "1. Canonical Spec Is Single Source of Truth",
        writer_spec.exists() and canonical_spec.exists(),
        "Writer + Canonical specs exist",
    ):
        failed += 1
    if writer_spec.exists():
        text = writer_spec.read_text()
        has_s16 = "## 16." in text or "# 16. Emotional QA" in text
        if not gate("1b. Writer Spec Section 16 (Emotional QA) exists", has_s16, "§16 present"):
            failed += 1

    # --- 2. SOURCE_OF_TRUTH Coverage Is Complete ---
    atoms_dir = REPO_ROOT / "atoms"
    atoms_structure_ok = atoms_dir.exists()
    personas = []
    if atoms_structure_ok:
        personas = [d.name for d in atoms_dir.iterdir() if d.is_dir()]
        atoms_structure_ok = len(personas) >= 1
    gate(
        "2. SOURCE_OF_TRUTH Coverage (atoms layout)",
        atoms_structure_ok,
        f"atoms/ exists, personas: {personas or 'none'}",
    )
    if not atoms_structure_ok:
        failed += 1
    # K-table / coverage enforcement in CI (PLANNING_STATUS: coverage checker)
    try:
        from phoenix_v4.planning.coverage_checker import run_coverage_check
        coverage_ok, coverage_errors = run_coverage_check(mode="relaxed")
        if not gate("2b. K-table coverage (coverage_checker)", coverage_ok, "; ".join(coverage_errors[:3]) if coverage_errors else "All persona×topic pass"):
            failed += 1
    except Exception as e:
        if not gate("2b. K-table coverage (coverage_checker)", False, str(e)):
            failed += 1

    # --- 3. K-Table Thresholds Are Enforced ---
    qa_rules = REPO_ROOT / "phoenix_v4" / "qa" / "emotional_governance_rules.yaml"
    k_tables_dir = REPO_ROOT / "phoenix_v4" / "policy" / "k_tables"
    gate(
        "3. K-Table / governance rules exist",
        qa_rules.exists(),
        "emotional_governance_rules.yaml present" + ("; k_tables/ optional" if not k_tables_dir.exists() else ""),
    )
    if not qa_rules.exists():
        failed += 1

    # --- 4. Assembly Is Deterministic ---
    gate("4. Assembly Is Deterministic", True, "Spec-defined; verify with same seed → same plan hash", skip=True)

    # --- 5. Emotional QA (Section 16) Passes ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            has_chapter = "chapter_level" in data
            has_volatile = "chapter_level" in data and "volatile_requirement" in data.get("chapter_level", {})
            has_cog_body = "chapter_level" in data and "cognitive_body_ratio" in data.get("chapter_level", {})
            gate(
                "5. Emotional QA rules (chapter_level)",
                has_chapter and (has_volatile or has_cog_body),
                "chapter_level + volatile/cognitive_body present",
            )
            if not has_chapter:
                failed += 1
        except Exception as e:
            gate("5. Emotional QA rules", False, str(e))
            failed += 1
    else:
        gate("5. Emotional QA rules", False, "emotional_governance_rules.yaml missing")
        failed += 1

    # --- 6. TTS Rhythm Governance Passes ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            tts = data.get("tts_rhythm", {})
            gate("6. TTS Rhythm in governance", bool(tts), "tts_rhythm section present")
            if not tts:
                failed += 1
        except Exception as e:
            gate("6. TTS Rhythm", False, str(e))
            failed += 1

    # --- 7. Drift Detection Passes (Book-Level) ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            bl = data.get("book_level", {})
            gate("7. Drift / book_level rules", bool(bl), "book_level section present")
            if not bl:
                failed += 1
        except Exception:
            gate("7. Drift book_level", False, "YAML error")
            failed += 1

    # --- 8. Structural Similarity Limits Pass ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            cat = data.get("catalog_level", {})
            gate("8. Catalog-level similarity rules", bool(cat), "catalog_level section present")
            if not cat:
                failed += 1
        except Exception:
            gate("8. Catalog-level", False, "YAML error")
            failed += 1

    # --- 9. Persona Hydration Is Enforced ---
    topic_skins = REPO_ROOT / "config" / "topic_skins.yaml"
    bindings = REPO_ROOT / "config" / "topic_engine_bindings.yaml"
    gate(
        "9. Persona / topic config (topic_skins, bindings)",
        topic_skins.exists() and bindings.exists(),
        "config/topic_skins.yaml + topic_engine_bindings.yaml",
    )
    if not (topic_skins.exists() and bindings.exists()):
        failed += 1

    # --- 10. No Forbidden Resolution Language ---
    gate("10. No Forbidden Resolution Language", True, "Spec §11 + Canonical §4.4; CI gate", skip=True)

    # --- 11. CI Failure Protocol Is Active ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            fp = data.get("failure_protocol", {})
            gate("11. CI failure_protocol defined", bool(fp), "failure_protocol in emotional_governance_rules")
            if not fp:
                failed += 1
        except Exception:
            gate("11. failure_protocol", False, "YAML error")
            failed += 1

    # --- 12. Release Simulation Passes ---
    run_sim = REPO_ROOT / "simulation" / "run_simulation.py"
    gate("12. Release simulation script exists", run_sim.exists(), "simulation/run_simulation.py")
    if not run_sim.exists():
        failed += 1

    # --- 13. FMT Enforced for Full-Book Formats ---
    binge_spec = REPO_ROOT / "specs" / "V4_6_BINGE_OPTIMIZATION_LAYER.md"
    gate("13. FMT / Binge spec exists", binge_spec.exists(), "V4_6_BINGE_OPTIMIZATION_LAYER.md")
    if not binge_spec.exists():
        failed += 1

    # --- 14. Repo-Root config / registry / atoms Integrity ---
    registry_dir = REPO_ROOT / "registry"
    registry_ok = registry_dir.exists() and any(registry_dir.glob("*.yaml"))
    config_ok = (REPO_ROOT / "config" / "topic_engine_bindings.yaml").exists() and (REPO_ROOT / "config" / "topic_skins.yaml").exists()
    atoms_ok = atoms_dir.exists() and any((atoms_dir / p / t / e / "CANONICAL.txt").exists() for p in (atoms_dir.iterdir() if atoms_dir.exists() else []) for t in (p.iterdir() if p.is_dir() else []) for e in (t.iterdir() if t.is_dir() else []) if p.is_dir() and t.is_dir())
    # simpler atoms check
    canon_count = len(list(atoms_dir.rglob("CANONICAL.txt"))) if atoms_dir.exists() else 0
    atoms_ok = canon_count > 0
    gate(
        "14. config/registry/atoms integrity",
        config_ok and registry_ok and atoms_ok,
        f"config={config_ok} registry={registry_ok} atoms({canon_count} CANONICAL.txt)={atoms_ok}",
    )
    if not (config_ok and registry_ok and atoms_ok):
        failed += 1

    # --- 15. Full pipeline (Stage 1→2→3) runnable ---
    pipeline_script = REPO_ROOT / "scripts" / "run_pipeline.py"
    catalog_planner = REPO_ROOT / "phoenix_v4" / "planning" / "catalog_planner.py"
    assembly_compiler = REPO_ROOT / "phoenix_v4" / "planning" / "assembly_compiler.py"
    gate15_detail = "run_pipeline.py + catalog_planner + assembly_compiler; one run produces valid CompiledBook"
    pipeline_ok = pipeline_script.exists() and catalog_planner.exists() and assembly_compiler.exists()
    if pipeline_ok:
        arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "nyc_executives__self_worth__shame__F006.yaml"
        if not arc_path.exists():
            pipeline_ok = False
        else:
            try:
                out_path = REPO_ROOT / "artifacts" / "golden_plans" / "_gate_pipeline_out.json"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                # Remove stale output so a cached file can't mask a real failure
                try:
                    if out_path.exists():
                        out_path.unlink()
                except OSError:
                    pass  # Sandbox/permission restriction; proceed anyway
                r = subprocess.run(
                    [
                        sys.executable, str(pipeline_script),
                        "--topic", "self_worth", "--persona", "nyc_executives",
                        "--arc", str(arc_path),
                        "--pipeline-mode", "registry",
                        "--out", str(out_path),
                        "--no-update-freebie-index",
                        "--skip-quality-gates",
                        "--no-job-check",
                    ],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if r.returncode == 0 and out_path.exists():
                    import json
                    data = json.loads(out_path.read_text())
                    compiled_ok = isinstance(data.get("plan_hash"), str) and isinstance(data.get("atom_ids"), list)
                    registry_ok = (
                        data.get("source") == "section_registry"
                        and isinstance(data.get("chapter_count"), int)
                        and data.get("chapter_count", 0) >= 1
                        and isinstance(data.get("plan_id"), str)
                    )
                    pipeline_ok = compiled_ok or registry_ok
                else:
                    pipeline_ok = False
                    # Surface the real error so it's visible in gate output
                    if r.stderr.strip():
                        print(f"      [Gate 15 pipeline stderr]: {r.stderr.strip()[:300]}")
                    elif r.stdout.strip():
                        print(f"      [Gate 15 pipeline stdout]: {r.stdout.strip()[:300]}")
                    band_gap_summary = _summarize_story_band_gaps(
                        persona_id="nyc_executives",
                        topic_id="self_worth",
                        arc_path=arc_path,
                    )
                    if band_gap_summary:
                        gate15_detail = f"{gate15_detail}; {band_gap_summary}"
            except Exception as e:
                pipeline_ok = False
                print(f"      [Gate 15 exception]: {e}")
                gate15_detail = "run_pipeline.py + catalog_planner + assembly_compiler; one run produces valid CompiledBook"
    else:
        gate15_detail = "run_pipeline.py + catalog_planner + assembly_compiler; one run produces valid CompiledBook"
    gate(
        "15. Full pipeline (Stage 1→2→3) runnable",
        pipeline_ok,
        gate15_detail,
    )
    if not pipeline_ok:
        failed += 1

    # --- 16. Freebie governance (Phase 3): density + CTA signature caps, same scope/index ---
    # Criterion: run_production_readiness_gates.py must run BOTH validate_freebie_density and
    # cta_signature_caps with the same scope/index. No separate or optional gate.
    freebie_index = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
    if freebie_index.exists():
        lines = [ln for ln in freebie_index.read_text().strip().splitlines() if ln.strip()]
        if len(lines) >= 2:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            index_str = str(freebie_index)
            freebie_density_ok = False
            freebie_detail = ""
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "phoenix_v4.qa.validate_freebie_density", "--index", index_str],
                    cwd=str(REPO_ROOT),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                freebie_density_ok = r.returncode == 0
                freebie_detail = "Density within thresholds" if freebie_density_ok else (r.stderr.strip() or "validate_freebie_density.py FAIL")
            except Exception:
                freebie_detail = "validate_freebie_density.py FAIL"
            cta_caps_ok = False
            cta_detail = ""
            try:
                r2 = subprocess.run(
                    [sys.executable, "-m", "phoenix_v4.qa.cta_signature_caps", "--index", index_str],
                    cwd=str(REPO_ROOT),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                cta_caps_ok = r2.returncode == 0
                cta_detail = (r2.stderr.strip() or r2.stdout.strip() or "").strip() or ("CTA caps OK" if cta_caps_ok else "cta_signature_caps.py FAIL")
            except Exception:
                cta_detail = "cta_signature_caps.py FAIL"
            if not gate("16. Freebie density (wave)", freebie_density_ok, freebie_detail):
                failed += 1
            if not gate("16b. CTA signature caps (same index)", cta_caps_ok, cta_detail):
                failed += 1
        else:
            gate("16. Freebie density (wave)", True, f"Index has {len(lines)} row(s); need ≥2 for wave density check; skip", skip=True)
            gate("16b. CTA signature caps (same index)", True, "skip (same scope: index has <2 rows)", skip=True)
    else:
        gate("16. Freebie density (wave)", True, "No freebie index; skip", skip=True)
        gate("16b. CTA signature caps (same index)", True, "skip (same scope: no index)", skip=True)

    # --- 17. jsonschema required + ops artifact validation (CI must not skip) ---
    try:
        import jsonschema  # noqa: F401
        jsonschema_available = True
    except ImportError:
        jsonschema_available = False
    gate17_detail = "jsonschema installed" if jsonschema_available else "jsonschema not installed; pip install jsonschema"
    if not gate("17. jsonschema required (ops validation non-optional)", jsonschema_available, gate17_detail):
        failed += 1
    elif (REPO_ROOT / "artifacts" / "ops").exists() or (REPO_ROOT / "artifacts" / "waves").exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "validate_ops_artifacts.py")],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            ops_validation_ok = r.returncode == 0
            gate17_ops_detail = r.stderr.strip() or r.stdout.strip() or "validate_ops_artifacts exit non-zero"
        except Exception as e:
            ops_validation_ok = False
            gate17_ops_detail = str(e)
        if not gate("17b. Ops/waves schema validation (when dirs exist)", ops_validation_ok, gate17_ops_detail):
            failed += 1

    # --- 18. Author cover art: every launchable author has registry + PNG + style/palette ---
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "check_author_cover_art.py"), "--repo-root", str(REPO_ROOT)],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        cover_art_ok = r.returncode == 0
        gate18_detail = (r.stderr or r.stdout or "").strip() or "check_author_cover_art.py"
    except Exception as e:
        cover_art_ok = False
        gate18_detail = str(e)
    if not gate("18. Author cover art (launchable authors: registry + PNG + style/palette)", cover_art_ok, gate18_detail):
        failed += 1

    # --- 19. Pearl News sidebar parity (added 2026-06-04, sidebar restore PR) ---
    # Authority: docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md §16 (canonical SHA chain)
    #            docs/PEARL_NEWS_SIDEBAR_FUNCTION_INVENTORY.md (F1..F5 + INFRA)
    #            docs/PEARL_NEWS_WRITER_SPEC.md §S (Sidebar Restoration Protocol)
    # Why this gate: WP td_post_template silently no-ops via REST; sidebar
    # regressions don't surface until operator views the rendered page.
    # This gate catches drift at the pre-publish stage.
    sidebar_gate = REPO_ROOT / "scripts" / "ci" / "check_pearl_news_sidebar_parity.py"
    if sidebar_gate.exists():
        try:
            r = subprocess.run(
                [sys.executable, str(sidebar_gate)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            sidebar_ok = r.returncode == 0
            sidebar_detail = (r.stdout.splitlines()[0] if r.stdout else r.stderr.splitlines()[0] if r.stderr else "no output").strip()
        except Exception as e:
            sidebar_ok = False
            sidebar_detail = str(e)
        if not gate("19. Pearl News sidebar parity (5 cards + pnReaderSignal IIFE)", sidebar_ok, sidebar_detail):
            failed += 1
    else:
        gate("19. Pearl News sidebar parity", True, "gate script not present; skip", skip=True)

    # --- 20. Waystream catalog uniqueness (800 distinct titles + subtitles) ---
    waystream_gate = REPO_ROOT / "scripts" / "ci" / "check_waystream_catalog_uniqueness.py"
    if waystream_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(waystream_gate)],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=360,
            )
            ws_ok = r.returncode == 0
            ws_detail = (r.stdout or r.stderr or "").strip().splitlines()[-1] if (r.stdout or r.stderr) else "check_waystream_catalog_uniqueness"
        except Exception as e:
            ws_ok = False
            ws_detail = str(e)
        if not gate("20. Waystream catalog uniqueness (800 titles/subs/pairs)", ws_ok, ws_detail):
            failed += 1
    else:
        gate("20. Waystream catalog uniqueness", True, "gate script not present; skip", skip=True)

    # --- 21-23. Manga M1 enforcement rails (three drift-class kills) ---
    for num, script, label in (
        ("21", "check_render_progress_bytes.py",
         "Manga render-progress bytes (no stub-as-done)"),
        ("22", "check_manga_story_authored.py",
         "Manga story-authored (no listing-as-story)"),
        ("22c", "check_manga_serial_spine.py",
         "Manga serial spine (adopted series spine+continuity)"),
        ("22d", "check_manga_story_engine.py",
         "Manga story-engine architect probe (governed genres)"),
        ("22e", "check_spine_packet_integrity.py",
         "Spine packet integrity (planner duplicate guard)"),
        ("22f", "check_accent_plan_assignment.py",
         "Accent plan assignment (planner-owned accents only)"),
        ("23", "check_manga_wiring.py",
         "Manga config wiring (no unwired-config-as-working)"),
        ("23b", "check_western_lane_format.py",
         "Western lane format (en_US illustrated pilot routing)"),
        ("24", "check_manga_l2_cutout_alpha.py",
         "Manga L2 cutout alpha (no ghost-matte)"),
        ("25", "check_manga_visual_acceptance.py",
         "Manga L2 visual acceptance (eye bar on REAL assets)"),
    ):
        g = REPO_ROOT / "scripts" / "ci" / script
        if g.exists():
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{REPO_ROOT / 'scripts' / 'ci'}{os.pathsep}{REPO_ROOT}"
                r = subprocess.run(
                    [sys.executable, str(g)],
                    cwd=str(REPO_ROOT), env=env,
                    capture_output=True, text=True, timeout=360,
                )
                g_ok = r.returncode == 0
                out = (r.stderr or r.stdout or "").strip()
                g_detail = out.splitlines()[-1] if out else script
            except Exception as e:
                g_ok = False
                g_detail = str(e)
            if not gate(f"{num}. {label}", g_ok, g_detail):
                failed += 1
        else:
            gate(f"{num}. {label}", True, "gate script not present; skip", skip=True)

    # --- 26. 12-shape chapter object/character continuity ---
    g26 = REPO_ROOT / "scripts" / "ci" / "check_chapter_object_continuity.py"
    if g26.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(g26)],
                cwd=str(REPO_ROOT), env=env,
                capture_output=True, text=True, timeout=360,
            )
            g_ok = r.returncode == 0
            out = (r.stderr or r.stdout or "").strip()
            g_detail = out.splitlines()[-1] if out else "check_chapter_object_continuity"
        except Exception as e:
            g_ok = False
            g_detail = str(e)
        if not gate("26. 12-shape chapter object continuity", g_ok, g_detail):
            failed += 1
    else:
        gate("26. 12-shape chapter object continuity", True, "gate script not present; skip", skip=True)

    # --- 27. Enforced data dictionary (undocumented / orphan / unwired-knob / bypass) ---
    # CASCADE-BLOCK: this is the SSOT-integrity gate. A red here means the repo has
    # an undocumented file, a silent orphan, a selector-blind atom bank, or a
    # book-assembly path bypassing chapter_planner/book_pass_gate. A dependent
    # NEXT-5 lane MUST NOT declare "done" while this is red — the runner records
    # data_dict_red so any downstream aggregator can honor the cascade.
    data_dict_red = False
    g27 = REPO_ROOT / "scripts" / "ci" / "check_data_dictionary.py"
    if g27.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{REPO_ROOT / 'scripts' / 'ci'}{os.pathsep}{REPO_ROOT}"
            r = subprocess.run(
                [sys.executable, str(g27)],
                cwd=str(REPO_ROOT), env=env,
                capture_output=True, text=True, timeout=360,
            )
            g_ok = r.returncode == 0
            out = (r.stderr or r.stdout or "").strip()
            g_detail = out.splitlines()[-1] if out else "check_data_dictionary"
        except Exception as e:
            g_ok = False
            g_detail = str(e)
        if not gate("27. Enforced data dictionary (no undoc/orphan/unwired-knob/bypass)",
                    g_ok, g_detail):
            failed += 1
            data_dict_red = True
    else:
        gate("27. Enforced data dictionary", True, "gate script not present; skip", skip=True)

    # --- 32. No-lost-functions capability regression (§18 dictionary-diff gate) ---
    # A previously-WIRED capability that becomes orphaned/removed vs origin/main without
    # an explicit CAPABILITY-RETIREMENT-RATIFIED tag is a regression: new features never
    # bury old functions (docs/agent_brief.txt §18). Fail-open if origin/main's committed
    # dictionary is not readable on this checkout (a diff gate with no baseline is a no-op).
    g32 = REPO_ROOT / "scripts" / "ci" / "check_capability_regression.py"
    if g32.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{REPO_ROOT / 'scripts' / 'ci'}{os.pathsep}{REPO_ROOT}"
            r = subprocess.run(
                [sys.executable, str(g32), "--baseline-ref", "origin/main"],
                cwd=str(REPO_ROOT), env=env,
                capture_output=True, text=True, timeout=360,
            )
            g_ok = r.returncode == 0
            out = (r.stderr or r.stdout or "").strip()
            g_detail = out.splitlines()[-1] if out else "check_capability_regression"
        except Exception as e:
            g_ok = False
            g_detail = str(e)
        if not gate("32. No-lost-functions capability regression (WIRED→orphan/removed needs ratification)",
                    g_ok, g_detail):
            failed += 1
    else:
        gate("32. No-lost-functions capability regression", True, "gate script not present; skip", skip=True)

    # --- 28. Flagship CH1 golden parity (byte diff vs canonical snapshot) ---
    flagship_parity_gate = REPO_ROOT / "scripts" / "ci" / "check_flagship_book_parity.py"
    if flagship_parity_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(flagship_parity_gate)],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=900,
            )
            fp_ok = r.returncode == 0
            fp_detail = (r.stdout.splitlines()[0] if r.stdout else r.stderr.splitlines()[0] if r.stderr else "check_flagship_book_parity").strip()
        except Exception as e:
            fp_ok = False
            fp_detail = str(e)
        if not gate("28. Flagship CH1 golden parity (canonical snapshot byte diff)", fp_ok, fp_detail):
            failed += 1
    else:
        gate("28. Flagship CH1 golden parity", True, "gate script not present; skip", skip=True)

    # --- 29. Flagship CH1 executable contract (structural requirements) ---
    contract_gate = REPO_ROOT / "scripts" / "ci" / "check_flagship_contract.py"
    if contract_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(contract_gate)],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=900,
            )
            fc_ok = r.returncode == 0
            fc_detail = (r.stdout.splitlines()[0] if r.stdout else r.stderr.splitlines()[0] if r.stderr else "check_flagship_contract").strip()
        except Exception as e:
            fc_ok = False
            fc_detail = str(e)
        if not gate("29. Flagship CH1 executable contract (12-shape structural gates)", fc_ok, fc_detail):
            failed += 1
    else:
        gate("29. Flagship CH1 executable contract", True, "gate script not present; skip", skip=True)

    # --- 30. Flagship exercise five-layer integrity (self-renders the 2h book) ---
    five_layer_gate = REPO_ROOT / "scripts" / "ci" / "check_flagship_exercise_five_layer.py"
    if five_layer_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(five_layer_gate)],
                cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=900,
            )
            fl_ok = r.returncode == 0
            fl_detail = (r.stdout.splitlines()[0] if r.stdout else r.stderr.splitlines()[0] if r.stderr else "check_flagship_exercise_five_layer").strip()
        except Exception as e:
            fl_ok = False
            fl_detail = str(e)
        if not gate("30. Flagship exercise five-layer integrity (ch2-12 full compose survives)", fl_ok, fl_detail):
            failed += 1
    else:
        gate("30. Flagship exercise five-layer integrity", True, "gate script not present; skip", skip=True)

    # --- 31. Flagship exercise pick diversity (no all-one-library / sequential-run) ---
    diversity_gate = REPO_ROOT / "scripts" / "ci" / "check_flagship_exercise_diversity.py"
    if diversity_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(diversity_gate)],
                cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=120,
            )
            dv_ok = r.returncode == 0
            dv_detail = (r.stdout.splitlines()[0] if r.stdout else r.stderr.splitlines()[0] if r.stderr else "check_flagship_exercise_diversity").strip()
        except Exception as e:
            dv_ok = False
            dv_detail = str(e)
        if not gate("31. Flagship exercise pick diversity (>=5 libraries, no sequential-run)", dv_ok, dv_detail):
            failed += 1
    else:
        gate("31. Flagship exercise pick diversity", True, "gate script not present; skip", skip=True)

    # --- 33. Translation native-check contract ---
    # Bootstrap on readiness until companion lanes annotate corpus with native_check:y.
    # Ship acceptance for translated atoms uses --production-only (no bootstrap).
    native_check_gate = REPO_ROOT / "scripts" / "ci" / "check_native_check.py"
    if native_check_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(native_check_gate), "--bootstrap-mode"],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
            nc_ok = r.returncode == 0
            out = (r.stderr or r.stdout or "").strip()
            nc_detail = out.splitlines()[-1] if out else "check_native_check"
        except Exception as e:
            nc_ok = False
            nc_detail = str(e)
        if not gate(
            "33. Translation native-check contract (bootstrap; ship requires y)",
            nc_ok,
            nc_detail,
        ):
            failed += 1
    else:
        gate(
            "33. Translation native-check contract",
            True,
            "gate script not present; skip",
            skip=True,
        )

    # --- 34. Lean best-book golden integrity (operator Q-LEAN-BEST-01=A) ---
    lean_best_gate = REPO_ROOT / "scripts" / "ci" / "check_lean_best_book_parity.py"
    if lean_best_gate.exists():
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)
            r = subprocess.run(
                [sys.executable, str(lean_best_gate)],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            lb_ok = r.returncode == 0
            lb_detail = (
                r.stdout.splitlines()[0]
                if r.stdout
                else r.stderr.splitlines()[0]
                if r.stderr
                else "check_lean_best_book_parity"
            ).strip()
        except Exception as e:
            lb_ok = False
            lb_detail = str(e)
        if not gate(
            "34. Lean best-book golden integrity (CANONICAL_LEAN_BEST_BOOK sha lock)",
            lb_ok,
            lb_detail,
        ):
            failed += 1
    else:
        gate("34. Lean best-book golden integrity", True, "gate script not present; skip", skip=True)

    # --- 35–37. Pearl Prime perfect-books Wave-1 (G-CLAIM / G-LAYER / G-WRAP+G-DEF4) ---
    for gate_id, script_name, title, extra_env in (
        (
            "35",
            "check_acceptance_claim_language.py",
            "35. G-CLAIM / Q-ENFORCE-02 acceptance claim language",
            {"PYTHONPATH": str(REPO_ROOT / "scripts" / "ci") + os.pathsep + str(REPO_ROOT)},
        ),
        (
            "36",
            "check_catalog_manifest_acceptance_layer.py",
            "36. G-LAYER catalog manifest acceptance_layer",
            {"PYTHONPATH": str(REPO_ROOT)},
        ),
        (
            "37",
            "check_catalog_ship_wrap_defect4.py",
            "37. G-WRAP + G-DEF4 catalog ship detectors (integrity)",
            {"PYTHONPATH": str(REPO_ROOT)},
        ),
    ):
        script = REPO_ROOT / "scripts" / "ci" / script_name
        if not script.exists():
            gate(title, True, "gate script not present; skip", skip=True)
            continue
        try:
            env = os.environ.copy()
            env.update(extra_env)
            r = subprocess.run(
                [sys.executable, str(script)],
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            ok = r.returncode == 0
            detail = (
                (r.stdout or r.stderr or script_name).strip().splitlines() or [script_name]
            )[0][:240]
        except Exception as e:
            ok = False
            detail = str(e)
        if not gate(title, ok, detail):
            failed += 1

    # --- Report ---
    print("V4.5 Production Readiness — Pearl Prime Wave-1 gates included\n")
    for name, status, detail in RESULTS:
        sym = "✓" if status == "PASS" else ("○" if status == "SKIP" else "✗")
        print(f"  {sym} {status:4}  {name}")
        if detail:
            print(f"      {detail}")
    print()
    if data_dict_red:
        print("CASCADE-BLOCK: gate 27 (data dictionary) is RED — dependent NEXT-5 "
              "lanes may not declare done until the SSOT is documented/wired.")
    if failed > 0:
        print(f"FAILED: {failed} condition(s) not met.")
        return 1
    print("All automatable gates passed. Run simulation (--phase2 --phase3) and manual checks for full sign-off.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

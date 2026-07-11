#!/usr/bin/env python3
"""
Full pipeline: Stage 1 (catalog) -> Stage 2 (format selector) -> Stage 3 (assembly compiler). Arc-First: --arc required.
Usage:
  python3 scripts/run_pipeline.py --topic self_worth --persona nyc_executives --arc config/source_of_truth/master_arcs/nyc_executives__self_worth__shame__F006.yaml --out artifacts/out.plan.json
  python3 scripts/run_pipeline.py --input example_input.yaml --arc path/to/arc.yaml --out out.plan.json

CANONICAL PEARL PRIME CLI (authority: docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md).
The OVERLAY spec is the single craft + runtime authority for Pearl Prime bestseller
books. For a RELEASE-grade build, every quality gate must pass:

  PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic <topic> --persona <persona> \
    --arc <arc.yaml> --pipeline-mode spine \
    --runtime-format <format> \
    --quality-profile production \
    --exercise-journeys \
    --no-job-check --render-book \
    --render-dir <out_dir>

Profile semantics (argparse defaults below): --pipeline-mode default is `spine`
(canonical Pearl Prime path). Legacy `--pipeline-mode registry` is blocked under
`--quality-profile production|flagship` with `--render-book` (see `--allow-legacy-registry`).
--quality-profile default is `production` (all gates run; any
failure exits 1). Use `flagship` to verify only the three load-bearing structural
gates (chapter_flow, book_quality_gate, scene_anti_genericity); `draft`/`debug` for
iteration only. `--exercise-journeys` attaches the multi-part EXERCISE journeys and is
part of the canonical production invocation.

NOTE: the spine+production path renders deterministically from the atom banks +
register_output_strengthen post-passes (F1/F4/F6/F7/F13). It does NOT invoke
phoenix_v4/rendering/pearl_writer_expand.py — thin-section LLM expansion is gated
behind section_packet_composer's `expand_thin_sections` flag (default False) and is
NOT wired to any run_pipeline CLI flag. Do not enable it on the spine+production
release path without an explicit spec amendment.

NOTE (G1, render-hardening 2026-07-02, fast-follow to #4566): the word-count FLOOR
PADDER (ensure_word_count_floor) is DISABLED on the spine path — both the function
body (#4566) and the call sites here. An under-length spine book is surfaced as a
thin-pool / atom-shape signal in the governance report (`spine_word_floor_signals`),
NOT papered over with standalone one-line filler (the choppy class register_gate F14
now HARD_FAILs). Re-enable padding only via PHOENIX_SPINE_WORD_FLOOR_PAD=1 (not for
the release path). See docs/PEARL_PRIME_BEATLINE_CEILING_CALIBRATION_2026-07-02.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None

ALIASES_PATH = REPO_ROOT / "config" / "identity_aliases.yaml"
BINDINGS_PATH = REPO_ROOT / "config" / "topic_engine_bindings.yaml"
ARCS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
ATOMS_ROOT = REPO_ROOT / "atoms"

_KEYLIKE_METADATA_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]{0,40}\s*:\s*.+$")


def _load_yaml(path: Path) -> dict:
    if not path.exists() or not yaml:
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return data if isinstance(data, dict) else {}


def _topic_has_direct_support(
    *,
    topic_id: str,
    canonical_persona: str,
    arc_topic: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> bool:
    if arc_topic and arc_topic == topic_id:
        return True
    arcs_root = repo_root / "config" / "source_of_truth" / "master_arcs"
    if canonical_persona and any(arcs_root.glob(f"{canonical_persona}__{topic_id}__*.yaml")):
        return True
    bindings = _load_yaml(repo_root / "config" / "topic_engine_bindings.yaml")
    topic_cfg = bindings.get(topic_id)
    return isinstance(topic_cfg, dict) and bool(topic_cfg.get("allowed_engines"))


def _count_proseful_sections(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    count = 0
    for section in re.split(r"(?m)^##\s+", text):
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        prose_lines: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped or stripped == "---":
                continue
            if _KEYLIKE_METADATA_RE.match(stripped):
                continue
            prose_lines.append(stripped)
        if len(" ".join(prose_lines).split()) >= 6:
            count += 1
    return count


def _topic_source_readiness_issues(
    *,
    persona_id: str,
    topic_id: str,
    engine_id: str,
    atoms_root: Path = ATOMS_ROOT,
) -> list[str]:
    issues: list[str] = []
    scene_path = atoms_root / persona_id / topic_id / "SCENE" / "CANONICAL.txt"
    story_path = atoms_root / persona_id / topic_id / engine_id / "CANONICAL.txt"

    scene_count = _count_proseful_sections(scene_path)
    if scene_count == 0:
        issues.append(f"SCENE bank has no proseful entries at {scene_path}")

    story_count = _count_proseful_sections(story_path)
    if story_count == 0:
        issues.append(f"STORY bank for engine '{engine_id}' has no proseful entries at {story_path}")

    return issues


def resolve_to_canonical(
    aliases_path: Path,
    topic_id: str,
    persona_id: str,
    *,
    repo_root: Path = REPO_ROOT,
    arc_topic: str | None = None,
) -> tuple[str, str]:
    """Resolve topic_id and persona_id to canonical (atoms dir names). Stage 3 receives only canonical IDs."""
    if not aliases_path.exists() or not yaml:
        return topic_id, persona_id
    data = yaml.safe_load(aliases_path.read_text()) or {}
    persona_aliases = data.get("persona_aliases") or {}
    topic_aliases = data.get("topic_aliases") or {}
    canonical_persona = persona_aliases.get(persona_id, persona_id)
    aliased_topic = topic_aliases.get(topic_id, topic_id)
    canonical_topic = aliased_topic
    if aliased_topic != topic_id and _topic_has_direct_support(
        topic_id=topic_id,
        canonical_persona=canonical_persona,
        arc_topic=arc_topic,
        repo_root=repo_root,
    ):
        canonical_topic = topic_id
    return canonical_topic, canonical_persona


def _upsert_plan_index_row(index_path: Path, row: dict) -> None:
    """
    Maintain one plan-row per book_id in artifacts/freebies/index.jsonl.
    Non-plan rows (e.g., artifact logs) are preserved.
    """
    rows: list[dict] = []
    if index_path.exists():
        for ln in index_path.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            try:
                rows.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    book_id = str(row.get("book_id") or "")
    kept = []
    for r in rows:
        is_plan_row = isinstance(r, dict) and "freebie_bundle" in r
        same_book = str(r.get("book_id") or "") == book_id
        if is_plan_row and same_book:
            continue
        kept.append(r)
    kept.append(row)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _run_post_render_quality_gates(
    *,
    out: dict,
    render_dir: Path,
    written: dict,
    canonical_persona: str,
    canonical_topic: str,
    atoms_root,
    gates_hard: bool,
) -> int | None:
    """Run chapter_flow_gate, book_pass_gate, and bestseller_craft_gate after render.

    Returns an exit code (int) if the pipeline should stop, or None to continue.
    """
    from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
    from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft

    rendered_txt_path = written.get("txt")
    flow_report_path = written.get("chapter_flow_report")

    # --- Chapter flow gate (per-chapter, already computed by render_book) ---
    chapter_flow_failures: list[dict] = []
    if flow_report_path and flow_report_path.exists():
        flow_report = json.loads(flow_report_path.read_text(encoding="utf-8"))
        for ch in flow_report.get("chapters", []):
            if ch.get("status") != "PASS":
                chapter_flow_failures.append(ch)
        if chapter_flow_failures:
            if gates_hard:
                # render_book with enforce_chapter_flow=True already raised; this is
                # a safety net for the case where it was not raised (e.g. non-txt).
                all_fail = len(chapter_flow_failures) == len(flow_report.get("chapters", []))
                if all_fail:
                    print("Chapter flow gate: ALL chapters failed flow gate.", file=sys.stderr)
                    for ch in chapter_flow_failures:
                        print(f"  Ch {ch.get('chapter')}: {', '.join(ch.get('errors', []))}", file=sys.stderr)
                    return 1
            else:
                for ch in chapter_flow_failures:
                    print(
                        f"  WARNING: chapter {ch.get('chapter')} flow gate: {', '.join(ch.get('errors', []))}",
                        file=sys.stderr,
                    )

    # --- Book-pass gate (post-render, on rendered prose) ---
    if rendered_txt_path and rendered_txt_path.exists():
        rendered_text = rendered_txt_path.read_text(encoding="utf-8")

        # --- Bestseller craft gate (ONTGP scoring, advisory) ---
        # Score each chapter and include in flow report
        chapters = re.split(r"(?m)^(?=## Chapter \d+)", rendered_text)
        chapters = [c.strip() for c in chapters if c.strip() and c.strip().startswith("## Chapter")]
        craft_results = []
        for i, ch_text in enumerate(chapters):
            craft = evaluate_bestseller_craft(ch_text)
            craft_results.append({
                "chapter": i + 1,
                "status": craft.status,
                "move_scores": craft.move_scores,
                "issues": craft.issues,
                "remediation": craft.remediation,
                "metrics": craft.metrics,
            })
        overall_craft_score = 0.0
        if craft_results:
            per_ch_means = []
            for cr in craft_results:
                scores = cr.get("move_scores", {})
                if scores:
                    per_ch_means.append(sum(scores.values()) / len(scores))
            if per_ch_means:
                overall_craft_score = sum(per_ch_means) / len(per_ch_means)

        # Merge craft scores into the flow report
        if flow_report_path and flow_report_path.exists():
            flow_report = json.loads(flow_report_path.read_text(encoding="utf-8"))
        else:
            flow_report = {"chapters": [], "status": "UNKNOWN"}
        flow_report["bestseller_craft"] = {
            "overall_score": round(overall_craft_score, 4),
            "per_chapter": craft_results,
        }
        flow_report_path_final = render_dir / "chapter_flow_report.json"
        flow_report_path_final.write_text(json.dumps(flow_report, indent=2), encoding="utf-8")

        # Log craft score (always advisory, never blocks)
        craft_status = "PASS" if overall_craft_score >= 0.4 else ("WARN" if overall_craft_score >= 0.2 else "FAIL")
        print(
            f"Bestseller craft gate (advisory): {craft_status} — "
            f"overall ONTGP score {overall_craft_score:.2f}",
            file=sys.stderr,
        )

    return None


# ---------------------------------------------------------------------------
# Flagship profile gate routing
#
# Per docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md and the bestseller
# drift analysis (artifacts/analysis/shortest_path_to_bestseller.md, P0.5),
# the `flagship` profile is positioned between `draft` and `production`:
# every gate runs (just like production), but only a small set of
# load-bearing gates produce non-zero exits. The remaining gates stay
# advisory so internal QA can iterate on the flagship anxiety+gen_z+ahjan
# ladder without every gate's heuristic noise blocking the run.
# ---------------------------------------------------------------------------
FLAGSHIP_BLOCKING_GATES = frozenset(
    {"chapter_flow", "book_quality_gate", "scene_anti_genericity"}
)


def _check_exercise_strict_canonical_gate(
    quality_profile: str, enrichment_audit: dict | None
) -> None:
    """EXERCISE-BANK-RESOLUTION-01: production must not fall through to practice_library.

    Production MUST resolve EXERCISE slots from ``teacher_banks/approved_atoms/EXERCISE``
    or the persona-atom EXERCISE bank — not from ``practice_library`` (the spec §4.5
    third source). practice_library is acceptable for draft/debug/flagship profiles;
    production requires authored canon.

    Raises ``SystemExit`` (matches existing production-gate pattern at the call site)
    with an actionable message when the gate fires.
    """
    if quality_profile != "production":
        return
    practice_lib_count = (enrichment_audit or {}).get("slots_from_practice_library", 0)
    plan_bound = (enrichment_audit or {}).get("slots_from_twelve_shape_plan_exercise", 0)
    unbound_practice = practice_lib_count - plan_bound
    if unbound_practice <= 0:
        return
    raise SystemExit(
        f"[PRODUCTION GATE] EXERCISE-BANK-RESOLUTION-01 strict-canonical: "
        f"{unbound_practice} EXERCISE slot(s) resolved via practice_library "
        f"fall-through. Production must resolve EXERCISE from "
        f"teacher_banks/approved_atoms/EXERCISE or persona-atom EXERCISE bank. "
        f"Add atoms upstream (Pearl_Editor + Pearl_Writer ws), or use "
        f"--quality-profile draft/debug to allow practice_library fall-through "
        f"during development."
    )


def _block_on_fail(quality_profile: str, gate_name: str) -> bool:
    """Return True when a FAIL on ``gate_name`` should append to the failures list.

    production: every gate blocks.
    flagship:   only FLAGSHIP_BLOCKING_GATES block.
    draft/debug: nothing blocks (caller checks ``gates_run`` upstream).
    """
    if quality_profile == "production":
        return True
    if quality_profile == "flagship" and gate_name in FLAGSHIP_BLOCKING_GATES:
        return True
    return False


def _apply_book_quality_gate(
    *,
    render_dir: Path,
    prose: str,
    runtime_format_id: str,
    gates_hard: bool,
    governance_report: dict | None = None,
    slot_sequences: list | None = None,
    frame: str = "somatic_first",
    policy_override: bool = False,
) -> tuple[list[str], dict]:
    """Write book_quality_report.json; return (pipeline_failure_tags, summary_fragment)."""
    try:
        from phoenix_v4.quality.book_quality_gate import evaluate_book_quality, write_book_quality_report
    except (ImportError, ModuleNotFoundError) as _e:
        # Restored in-tree gate should import; this path is for mis-packaged checkouts only.
        out_path = render_dir / "book_quality_report.json"
        payload = {
            "status": "ERROR",
            "reason": f"book_quality_gate module unavailable: {_e}",
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(
            f"Pearl Prime book quality gate: ERROR (module missing) — {out_path}",
            file=sys.stderr,
        )
        fragment = {
            "release_band": "Error",
            "report_path": str(out_path),
            "fail_reasons": [str(_e)],
            "hold_reasons": [],
        }
        if gates_hard:
            return ["book_quality_gate"], fragment
        print(
            "Pearl Prime book quality gate: non-production profile — continuing without gate.",
            file=sys.stderr,
        )
        return [], fragment

    rep = evaluate_book_quality(
        prose,
        runtime_format_id=runtime_format_id or "",
        governance_report=governance_report,
        slot_sequences=slot_sequences,
        frame=frame,
        policy_override=policy_override,
    )
    out_path = render_dir / "book_quality_report.json"
    write_book_quality_report(rep, out_path)
    print(
        f"Pearl Prime book quality gate: {rep.release_band} (fail={len(rep.fail_reasons)} "
        f"hold={len(rep.hold_reasons)}) — {out_path}",
        file=sys.stderr,
    )
    fragment = {
        "release_band": rep.release_band,
        "report_path": str(out_path),
        "fail_reasons": rep.fail_reasons,
        "hold_reasons": rep.hold_reasons,
    }
    failures: list[str] = []
    if gates_hard and str(rep.release_band) == "Reject":
        failures.append("book_quality_gate")
    return failures, fragment


def _enforce_pipeline_mode_policy(args: argparse.Namespace, quality_profile: str) -> int | None:
    """Warn on legacy registry mode; hard-block registry renders under production profile."""
    mode = getattr(args, "pipeline_mode", "spine")
    if mode != "registry":
        return None
    render_book = bool(getattr(args, "render_book", False))
    production_like = quality_profile in ("production", "flagship")
    if (
        render_book
        and production_like
        and not getattr(args, "allow_legacy_registry", False)
    ):
        print(
            "Error: --pipeline-mode registry is legacy and blocked under "
            "--quality-profile production|flagship with --render-book. Book production "
            "MUST use --pipeline-mode spine (the default). See "
            "docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md.",
            file=sys.stderr,
        )
        return 1
    if render_book or quality_profile == "flagship":
        print(
            "Warning: --pipeline-mode registry is legacy. For rendered books use "
            "--pipeline-mode spine (the default). Registry mode is retained only "
            "for plan-only QA of section-registry content.",
            file=sys.stderr,
        )
    else:
        print(
            "Warning: --pipeline-mode registry is LEGACY (section-registry fast-path). "
            "Pearl Prime production books MUST use spine (the default). "
            "See docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md.",
            file=sys.stderr,
        )
    return None


def _extract_registry_chapters(prose: str) -> list[str]:
    """Split registry-rendered prose into per-chapter text strings.

    Registry prose uses plain "Chapter N" headings (not ## Chapter N).
    Returns each chapter as a single string that includes the heading line.
    """
    lines = prose.splitlines()
    chapters: list[str] = []
    current_lines: list[str] = []
    in_chapter = False
    for line in lines:
        if re.match(r"^\s*Chapter\s+\d+\s*$", line.strip()):
            if in_chapter and current_lines:
                chapters.append("\n".join(current_lines).strip())
            current_lines = [line]
            in_chapter = True
        elif in_chapter:
            current_lines.append(line)
    if in_chapter and current_lines:
        chapters.append("\n".join(current_lines).strip())
    return chapters


def _load_runtime_word_ceiling(runtime_fmt: str, repo_root: Path) -> int | None:
    """Return the authoritative word-count ceiling for a runtime format.

    Prefers the explicit ``cap_word_target`` override in
    ``config/format_selection/format_registry.yaml`` (DURATION-DERIVATION-01 §5 —
    e.g. standard_book pins cap_word_target: 22000 independent of word_range edits),
    falling back to ``word_range[max]`` when no explicit cap is set. Returns None
    when neither is resolvable so the caller can no-op safely.
    """
    rf = (runtime_fmt or "").strip()
    if not rf or yaml is None:
        return None
    path = repo_root / "config" / "format_selection" / "format_registry.yaml"
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    block = (data.get("runtime_formats") or {}).get(rf)
    if not isinstance(block, dict):
        return None
    cap = block.get("cap_word_target")
    if isinstance(cap, (int, float)) and int(cap) > 0:
        return int(cap)
    wr = block.get("word_range")
    if isinstance(wr, (list, tuple)) and len(wr) >= 2:
        try:
            hi = int(wr[1])
        except (TypeError, ValueError):
            return None
        if hi > 0:
            return hi
    return None


def _clamp_book_to_word_ceiling(prose: str, ceiling: int, *, reserve: int = 0) -> tuple[str, int, int]:
    """Trim a spine-rendered book so its TOTAL word count (incl. front-matter) ≤ ceiling.

    Render-accounting fix (DEFERRED-LANE word_budget 2026-06-15): the spine path fills
    chapters to the runtime ceiling during apply_depth_pass, then BOTH
    strengthen_rendered_spine_manuscript passes add words and the arch-v2
    "Note on the Teachings" preamble prepends ~400 more — all AFTER the depth budget and
    with no book-level clamp (the existing _per_chapter_word_cap is gated on
    _cli_output_format, which is empty for spine, so it never fires for standard_book).
    Result: rebuilt standard_book renders land at ~22.7–24.1k and HARD_FAIL the
    book_pass word_budget gate (which checks word_count ≤ word_range[max]=22000).

    This trims the chapter BODIES proportionally to the overshoot, preserving:
      - any non-chapter front-matter before the first "Chapter N" heading (the preamble),
      - every "Chapter N" heading line,
      - whole paragraphs where possible (only the final kept paragraph of an
        over-budget chapter is word-sliced).

    ``reserve`` (Blocker 1, 2026-06-17): clamp to ``ceiling - reserve`` instead of ``ceiling``
    so a small word budget remains for the post-clamp ``ensure_chapter_flow_cues`` pass, whose
    guarantee sentences would otherwise push the book back over the ceiling. The book_pass
    word_budget gate uses a RANGE (floor..ceiling) so trimming a few dozen words below the
    ceiling stays comfortably within band.

    Returns (clamped_prose, pre_words, post_words). No-ops (returns input) when the
    book is already within the effective ceiling or has no parseable chapters.
    """
    pre_words = len(prose.split())
    effective_ceiling = max(1, ceiling - max(0, reserve)) if ceiling > 0 else ceiling
    if ceiling <= 0 or pre_words <= effective_ceiling:
        return prose, pre_words, pre_words
    ceiling = effective_ceiling
    chapters = _extract_registry_chapters(prose)
    if not chapters:
        return prose, pre_words, pre_words

    # Front-matter = everything before the first chapter heading (e.g. the preamble).
    first_ch = chapters[0]
    split_at = prose.find(first_ch)
    front_matter = prose[:split_at].rstrip() if split_at > 0 else ""
    front_words = len(front_matter.split())

    chapter_words = [len(c.split()) for c in chapters]  # includes the heading line
    heading_words = [len((c.splitlines()[0] if c.splitlines() else "").split()) for c in chapters]
    body_words_list = [cw - hw for cw, hw in zip(chapter_words, heading_words)]
    body_total = sum(body_words_list)
    headings_total = sum(heading_words)
    # Words available for chapter BODIES after reserving front-matter + all headings.
    body_ceiling = max(0, ceiling - front_words - headings_total)
    if body_total <= body_ceiling:
        return prose, pre_words, pre_words

    # Proportional per-chapter body target so the trim is spread evenly, not all on ch1.
    scale = body_ceiling / body_total if body_total else 0.0

    def _trim_body(body: str, target: int) -> str:
        if target <= 0:
            return ""
        if len(body.split()) <= target:
            return body
        paras = re.split(r"\n\s*\n", body)
        kept: list[str] = []
        used = 0
        for p in paras:
            pw = len(p.split())
            if used + pw <= target:
                kept.append(p)
                used += pw
            else:
                remain = target - used
                if remain > 0:
                    sliced = " ".join(p.split()[:remain])
                    # Part C (de-injection 2026-07-05): trim at sentence boundary,
                    # not mid-word/mid-sentence when the final paragraph is sliced.
                    for end_char in (".", "!", "?"):
                        pos = sliced.rfind(end_char)
                        if pos >= max(0, len(sliced) // 3):
                            sliced = sliced[: pos + 1].strip()
                            break
                    kept.append(sliced)
                break
        return "\n\n".join(kept).strip()

    capped: list[str] = []
    for ch, bw in zip(chapters, body_words_list):
        lines = ch.splitlines()
        heading = lines[0] if lines else ""
        body = "\n".join(lines[1:])
        target = max(0, int(bw * scale))
        body = _trim_body(body, target)
        capped.append(f"{heading}\n\n{body}".strip() if body else heading)

    rebuilt = "\n\n".join(capped)
    if front_matter:
        rebuilt = f"{front_matter}\n\n{rebuilt}"

    # Final hard guard: proportional rounding can leave a few words of overshoot.
    # Trim the tail chapters' final paragraphs until the TOTAL is within the ceiling.
    over = len(rebuilt.split()) - ceiling
    if over > 0:
        capped2 = list(capped)
        for i in range(len(capped2) - 1, -1, -1):
            if over <= 0:
                break
            lines = capped2[i].splitlines()
            heading = lines[0] if lines else ""
            body = "\n".join(lines[1:])
            bw = len(body.split())
            if bw <= 0:
                continue
            new_target = max(0, bw - over)
            body = _trim_body(body, new_target)
            over -= bw - len(body.split())
            capped2[i] = f"{heading}\n\n{body}".strip() if body else heading
        rebuilt = "\n\n".join(capped2)
        if front_matter:
            rebuilt = f"{front_matter}\n\n{rebuilt}"

    return rebuilt, pre_words, len(rebuilt.split())


_SCENE_ANCHOR_CONFIG_CACHE: dict | None = None


def _load_scene_anchor_density_config() -> dict:
    """Load scene_anchor_density gate config, with sane defaults if file is missing.

    See config/quality/scene_anchor_density_config.yaml for cap rationale (empirical
    en_US catalog audit, PR #1089: cap=2 yielded 168/200 false-positive failures
    dominated by natural rhetorical motifs at paragraph_count=3).
    """
    global _SCENE_ANCHOR_CONFIG_CACHE
    if _SCENE_ANCHOR_CONFIG_CACHE is not None:
        return _SCENE_ANCHOR_CONFIG_CACHE
    defaults = {
        "default_cap_per_chapter": 3,
        "collapse_overlapping_ngrams": True,
    }
    try:
        import yaml  # type: ignore[import-not-found]

        cfg_path = (
            Path(__file__).resolve().parent.parent
            / "config" / "quality" / "scene_anchor_density_config.yaml"
        )
        if cfg_path.exists():
            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            for key, default in defaults.items():
                if key in loaded:
                    defaults[key] = loaded[key]
    except Exception:
        # Defensive: any config load failure falls back to safe defaults.
        pass
    _SCENE_ANCHOR_CONFIG_CACHE = defaults
    return defaults


def _scene_anchor_density_violations(prose: str, cap: int) -> list[dict]:
    """Find repeated >3-word phrases appearing in more paragraphs than the plan allows.

    Algorithm:
      - Splits prose into chapters via the registry "Chapter N" heading convention.
      - Within each chapter, enumerates all 4..8 word overlapping n-grams per paragraph.
      - A phrase that appears in MORE THAN `cap` paragraphs is an offender.
      - If `collapse_overlapping_ngrams` is enabled in config, offenders that are sub-
        sequences of a longer offender with the same paragraph_count are dropped from
        the reported list (the longest n-gram is kept). This is a reporting-only change;
        a single recurring 8-word motif no longer balloons into 5 overlapping entries.
    """
    if cap <= 0:
        return []
    cfg = _load_scene_anchor_density_config()
    collapse = bool(cfg.get("collapse_overlapping_ngrams", True))
    chapters = _extract_registry_chapters(prose)
    violations: list[dict] = []
    phrase_re = re.compile(r"\b[\w']+\b")
    for ch_idx, chapter in enumerate(chapters, start=1):
        paras = [p.strip() for p in re.split(r"\n\s*\n", chapter) if p.strip()]
        phrase_paras: dict[str, set[int]] = {}
        for p_idx, para in enumerate(paras):
            words = [w.lower() for w in phrase_re.findall(para)]
            for n in range(4, min(8, len(words)) + 1):
                for i in range(0, len(words) - n + 1):
                    phrase = " ".join(words[i : i + n])
                    phrase_paras.setdefault(phrase, set()).add(p_idx)
        offenders_raw = [
            {"phrase": phrase, "paragraph_count": len(indices)}
            for phrase, indices in phrase_paras.items()
            if len(indices) > cap
        ]
        if collapse and offenders_raw:
            # Group by paragraph_count; within each group, drop any phrase that is
            # a contiguous substring of a longer phrase in the same group. This collapses
            # the n-gram explosion where one 8-word motif produced 5 overlapping entries
            # (lengths 4..8) with identical paragraph_count.
            by_count: dict[int, list[str]] = {}
            for o in offenders_raw:
                by_count.setdefault(o["paragraph_count"], []).append(o["phrase"])
            kept: list[dict] = []
            for pcount, phrases in by_count.items():
                phrases_sorted = sorted(phrases, key=lambda s: (-len(s.split()), s))
                survivors: list[str] = []
                for p in phrases_sorted:
                    if not any(p != q and p in q for q in survivors):
                        survivors.append(p)
                for p in survivors:
                    kept.append({"phrase": p, "paragraph_count": pcount})
            offenders = kept
        else:
            offenders = offenders_raw
        if offenders:
            offenders.sort(key=lambda x: (-x["paragraph_count"], x["phrase"]))
            violations.append({"chapter": ch_idx, "cap": cap, "offenders": offenders[:10]})
    return violations


def _reduce_scene_anchor_density(prose: str, cap: int, *, max_passes: int = 4) -> tuple[str, list[str]]:
    """Generalized scene_anchor density reducer (Blocker 2 / A1-generalize, 2026-06-17).

    The composer's ``_DIRECTION_CAP_PER_CHAPTER`` caps only the bridge-bank chapter-direction
    substring, and ``dedupe_scene_furniture_book`` caps only a closed allowlist of furniture
    signatures. Neither catches the general case the gate measures: ANY 4–8 word n-gram that
    lands in MORE than ``cap`` paragraphs of one chapter (QA sweep examples: a HOOK somatic
    lead-in ``"as you prepare to"`` ×5 in one chapter; SCENE furniture variants not in the
    allowlist such as ``"light over the window"`` / ``"moves through the room"``).

    This pass mirrors the gate's own detector (``_scene_anchor_density_violations``) exactly,
    then deterministically removes the SURPLUS occurrences past the cap by dropping the minimal
    *whole sentence* that carries the offending phrase from each surplus paragraph — the same
    sentence-granularity strategy proven safe in ``dedupe_scene_furniture_book`` (dropping a bare
    substring shears sentences and orphans byte-identical tails; dropping a whole sentence cannot).
    It keeps the first ``cap`` paragraphs untouched, so the legitimate motif still appears up to
    the gate's allowance; only the boilerplate over-repetition is trimmed.

    The pass NEVER weakens the gate or its cap — it strengthens the OUTPUT so the gate passes.
    It re-runs until the gate reports no violations or ``max_passes`` is reached (the gate itself
    remains the final arbiter at the call site). Deterministic: surplus selection is purely
    positional (later paragraphs lose the phrase), no randomization.

    Returns ``(reduced_prose, notes)``.
    """
    if cap <= 0 or not prose or not prose.strip():
        return prose, []

    notes: list[str] = []
    work = prose
    phrase_re = re.compile(r"\b[\w']+\b")
    # Sentence splitter consistent with the rest of the renderer (terminator-preserving handled
    # by rebuilding from spans; here we split into sentence strings for membership testing).
    sent_split_re = re.compile(r"(?<=[.!?])\s+")

    for _pass in range(max_passes):
        violations = _scene_anchor_density_violations(work, cap)
        if not violations:
            break

        chapters = _extract_registry_chapters(work)
        if not chapters:
            break
        # Map chapter number (1-indexed, as the gate reports) → offending phrases for that chapter.
        offenders_by_chapter: dict[int, list[str]] = {}
        for v in violations:
            ch_num = int(v.get("chapter", 0))
            phrases = [str(o.get("phrase", "")) for o in v.get("offenders", []) if o.get("phrase")]
            if ch_num and phrases:
                # Process longest phrases first so collapsing a long motif also clears its
                # shorter overlapping sub-n-grams in one drop.
                offenders_by_chapter[ch_num] = sorted(phrases, key=lambda s: (-len(s.split()), s))

        changed = False
        new_chapters: list[str] = []
        for ch_idx, chapter in enumerate(chapters, start=1):
            phrases = offenders_by_chapter.get(ch_idx)
            if not phrases:
                new_chapters.append(chapter)
                continue
            paras = re.split(r"\n\s*\n", chapter)
            for phrase in phrases:
                p_low = phrase.lower()
                # Which paragraphs contain the phrase (as a contiguous lowercase n-gram)?
                hit_para_idxs: list[int] = []
                for p_idx, para in enumerate(paras):
                    words = [w.lower() for w in phrase_re.findall(para)]
                    n = len(p_low.split())
                    joined = " ".join(words)
                    if p_low in joined and n >= 1:
                        # Confirm as a word-boundary n-gram, not a coincidental substring.
                        target = p_low
                        if any(
                            " ".join(words[i:i + n]) == target
                            for i in range(0, max(0, len(words) - n + 1))
                        ):
                            hit_para_idxs.append(p_idx)
                if len(hit_para_idxs) <= cap:
                    continue
                # Keep the first `cap` paragraphs; trim the phrase-bearing sentence from the rest.
                for p_idx in hit_para_idxs[cap:]:
                    para = paras[p_idx]
                    sents = sent_split_re.split(para)
                    kept_sents = []
                    dropped_one = False
                    for s in sents:
                        s_words = [w.lower() for w in phrase_re.findall(s)]
                        n = len(p_low.split())
                        if not dropped_one and any(
                            " ".join(s_words[i:i + n]) == p_low
                            for i in range(0, max(0, len(s_words) - n + 1))
                        ):
                            dropped_one = True
                            changed = True
                            continue
                        kept_sents.append(s)
                    paras[p_idx] = " ".join(kept_sents).strip()
                notes.append(
                    f"ch{ch_idx}: trimmed {len(hit_para_idxs) - cap} surplus occurrence(s) of {phrase!r}"
                )
            # Drop any paragraph emptied by trimming; preserve heading paragraph (index 0).
            rebuilt = [p for i, p in enumerate(paras) if p.strip() or i == 0]
            new_chapters.append("\n\n".join(rebuilt))

        if not changed:
            break
        work = "\n\n".join(new_chapters)

    return work, notes


def _resolve_angle_journey_id(angle_id: str, topic_id: str) -> tuple[str, str]:
    """Resolve a catalog angle identifier to a registry angle key for the angle-journey patch.

    Blocker 4 (angle_journey 0% coverage, 2026-06-17). The angle-journey machinery
    (``patch_beatmap_angle_journey`` → ``merge_angle_journey``) is keyed by the UPPERCASE
    journey-concept ids declared under ``config/angles/angle_registry.yaml::angles`` (e.g.
    ``INVISIBLE_THRESHOLD``, 5-layer progression). The spine pipeline, however, received the raw
    catalog ANGLE slug from ``book_spec_for_compiler['angle_id']`` (e.g. ``false_alarm``), which is
    NOT a registry key. ``merge_angle_journey('false_alarm')`` returned an empty layer_progression,
    so ``apply_angle_journey_slots`` injected ZERO ANGLE_DEFINITION/ANGLE_CALLBACK slots and the
    ``angle_journey_coherence`` gate saw 0% of chapters carrying angle slots (book_pass FAIL).

    The registry already ships the correct mapping in
    ``catalog_planner_resolution.topic_angle_map`` (topic → concept id), the same SSOT
    ``CatalogPlanner._derive_angle`` and the catalog generator use. This resolves through it:

      1. If ``angle_id`` is already a declared registry key → use it unchanged.
      2. Else if ``topic_angle_map[topic_id]`` maps to a declared registry key → use that.
      3. Else → return ``angle_id`` unchanged (the patch will no-op as before; never invents).

    Returns ``(resolved_angle_id, source_tag)``. Deterministic; no randomization, no I/O beyond
    the cached registry load.
    """
    aid = (angle_id or "").strip()
    tid = (topic_id or "").strip()
    if not aid:
        return aid, "empty"
    try:
        from phoenix_v4.planning.angle_resolver import load_angle_registry

        reg = load_angle_registry()
    except Exception:
        return aid, "registry_load_failed"
    angles_root = reg.get("angles") or {}
    if aid in angles_root:
        return aid, "already_registry_key"
    topic_map = (reg.get("catalog_planner_resolution") or {}).get("topic_angle_map") or {}
    mapped = topic_map.get(tid)
    if mapped and str(mapped) in angles_root:
        return str(mapped), "topic_angle_map"
    return aid, "unresolved_catalog_slug"


def _resolved_runtime_format_id(args: argparse.Namespace, format_plan_dict: dict) -> str:
    """Unify CLI / plan runtime id. Stage-2 ``to_compiler_input()`` uses ``format_runtime_id``; some paths use ``runtime_format_id``."""
    cli = (getattr(args, "runtime_format", None) or "").strip()
    return (
        cli
        or (str(format_plan_dict.get("runtime_format_id") or "")).strip()
        or (str(format_plan_dict.get("format_runtime_id") or "")).strip()
    )


def _resolve_book_idea_and_motif(*, book_spec: Mapping[str, Any], arc: Any) -> tuple[str, str]:
    """Resolve contract book frame for enrichment strategy scoring."""
    explicit_idea = str(book_spec.get("book_idea") or "").strip()
    explicit_motif = str(book_spec.get("book_motif") or "").strip()
    if explicit_idea and explicit_motif:
        return explicit_idea, explicit_motif

    persona_id = str(book_spec.get("persona_id") or "")
    topic_id = str(book_spec.get("topic_id") or "")
    if persona_id == "gen_z_professionals" and topic_id == "anxiety":
        return "prediction-as-evidence swap", "The Alarm (chest and phone)"

    motif = getattr(arc, "motif", None) or {}
    if isinstance(motif, dict):
        symbol = str(motif.get("primary_symbol") or "").strip()
        image = str(motif.get("recurring_image") or "").strip()
        if symbol and image:
            readable_symbol = symbol.replace("_", " ").title()
            readable_image = image.replace("_", " and ")
            return (
                explicit_idea or "recognition_before_action",
                explicit_motif or f"The {readable_symbol} ({readable_image})",
            )
    return explicit_idea or "recognition_before_action", explicit_motif or "quiet_capacity"


def _write_enrichment_contract_reports(
    *,
    enriched: Any,
    render_dir: Path,
    contract_id: str,
    topic_id: str,
    persona_id: str,
    runtime_format: str,
) -> None:
    audit = enriched.enrichment_audit or {}
    strategy = dict(audit.get("enrichment_strategy_report") or {})
    alignment = dict(audit.get("bestseller_alignment_report") or {})
    strategy["contract_id"] = contract_id
    alignment["contract_id"] = contract_id
    (render_dir / "enrichment_strategy_report.json").write_text(
        json.dumps(strategy, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (render_dir / "bestseller_alignment_report.json").write_text(
        json.dumps(alignment, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    from phoenix_v4.qa.assembly_trace import write_assembly_trace

    write_assembly_trace(
        enriched=enriched,
        render_dir=render_dir,
        contract_id=contract_id,
        topic_id=topic_id,
        persona_id=persona_id,
        runtime_format=runtime_format,
    )


def _run_spine_pipeline_mode(
    *,
    args: argparse.Namespace,
    book_spec_for_compiler: dict,
    quality_profile: str,
    gates_run: bool,
    gates_hard: bool,
    ebook_job_ws: Path,
    repo_root: Path,
) -> int:
    """
    Spine → knobs → beatmap → enrichment + depth → compose_from_enriched_book → clean_for_delivery.
    Registry fast-path is bypassed; atom assembly is not used.
    """
    from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
    from phoenix_v4.planning.enrichment_select import (
        EnrichmentRequest,
        apply_depth_pass,
        budget_from_enriched,
        select_enrichment,
    )
    from phoenix_v4.planning.book_structure_plan import load_book_structure_plan
    from phoenix_v4.planning.chapter_plan import render_atom_slot_spec
    from phoenix_v4.planning.chapter_planner import derive_chapter_selector_targets
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format
    from phoenix_v4.rendering.book_renderer import (
        chapter_flow_gate_report,
        clean_for_delivery,
        ensure_chapter_flow_cues,
        strengthen_rendered_spine_manuscript,
    )
    from phoenix_v4.rendering.golden_chapter_synthesis import dedupe_scene_furniture_book
    from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book

    topic_id = book_spec_for_compiler.get("topic_id", "")
    persona_id = book_spec_for_compiler.get("persona_id", "")
    _tid_raw = (book_spec_for_compiler.get("teacher_id") or "").strip()
    teacher_for_enrich = None if not _tid_raw or _tid_raw == "default_teacher" else _tid_raw

    # V4 freeze: when --output-format is explicitly passed, derive runtime from it so beatmap/word
    # budget are sized for the modular format (e.g. pocket_guide → short_book_30) instead of the
    # freeze-prohibited "standard_book". When --output-format is absent, keep legacy default behavior
    # so existing spine tests/pipelines are not silently re-routed to a different runtime.
    from pearl_prime.modular_format_freeze import load_freeze_settings as _load_freeze_settings
    _freeze = _load_freeze_settings()
    _cli_runtime = (getattr(args, "runtime_format", None) or "").strip()
    _cli_output_format = (getattr(args, "output_format", None) or "").strip()
    _selected_output_format = _cli_output_format or (
        _freeze.default_output_format if _freeze.enabled else ""
    )
    _freeze_runtime = ""
    if _cli_output_format and _freeze.enabled and _cli_output_format in _freeze.formats:
        _freeze_runtime = str(
            _freeze.formats[_cli_output_format].get("runtime_format_id") or ""
        ).strip()
    runtime_fmt = _cli_runtime or _freeze_runtime or "standard_book"

    from phoenix_v4.planning.legacy_template_loader import resolve_template_library
    _template_library = resolve_template_library(topic_id, persona_id, runtime_fmt)
    if _template_library == "spine_only":
        print(
            f"Template routing: {topic_id}×{persona_id}×{runtime_fmt} → spine_only "
            f"(no template overlay)",
            file=sys.stderr,
        )
    else:
        print(
            f"Template routing: {topic_id}×{persona_id}×{runtime_fmt} → {_template_library}",
            file=sys.stderr,
        )

    try:
        book_plan = load_book_structure_plan(topic_id, persona_id, runtime_fmt, repo_root)
    except FileNotFoundError as exc:
        print(
            f"Book planning layer: no pre-authored plan for {topic_id} x {persona_id} x {runtime_fmt} "
            f"({exc}); generating auto-plan.",
            file=sys.stderr,
        )
        try:
            from phoenix_v4.planning.book_structure_plan import generate_book_plan
            _frame_for_plan = str(getattr(args, "frame", "somatic_first") or "somatic_first").strip()
            _seed_for_plan = str(getattr(args, "seed", "") or "")
            _teacher_for_plan = str(book_spec_for_compiler.get("teacher_id") or "default_teacher").strip()
            book_plan = generate_book_plan(
                topic_id=topic_id,
                persona_id=persona_id,
                runtime_format=runtime_fmt,
                engine_type=_frame_for_plan,
                seed=_seed_for_plan,
                teacher_id=_teacher_for_plan,
                repo_root=repo_root,
            )
        except Exception as gen_exc:
            print(f"Book planning layer: FAIL (auto-generate) — {gen_exc}", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Book planning layer: FAIL — {exc}", file=sys.stderr)
        return 1
    atom_slot_specs = {
        str(ch.chapter_number): render_atom_slot_spec(ch)
        for ch in book_plan.chapters
    }

    # PR-G: pass runtime_format so compact formats can subset the spine via
    # config/format_selection/format_registry.yaml::compact_chapter_subset.
    spine = load_spine(topic_id, repo_root, runtime_format=runtime_fmt)
    knob_profile = load_knob_profile(topic_id, repo_root)
    shaped_spine = apply_knobs(
        spine,
        knob_profile,
        runtime_format=runtime_fmt,
        persona_id=persona_id,
        repo_root=repo_root,
    )
    engines_data = load_topic_engines(topic_id, repo_root)
    fmt_spec = load_format_spec(runtime_fmt, repo_root)
    beatmap = compile_beatmap(shaped_spine, engines_data, fmt_spec, repo_root, persona_id=persona_id)

    # Blocker 4 (angle_journey 0% coverage, 2026-06-17): resolve the raw catalog angle slug
    # (e.g. "false_alarm") to its registry journey-concept key (e.g. "INVISIBLE_THRESHOLD" via
    # catalog_planner_resolution.topic_angle_map) BEFORE the angle-journey patch + gate, so the
    # 5-layer progression is found and ANGLE_DEFINITION/ANGLE_CALLBACK slots are actually injected
    # (≥80% chapters). Without this the slug missed the registry → 0 angle slots → book_pass FAIL.
    _spine_angle_raw = str(book_spec_for_compiler.get("angle_id") or "").strip()
    _spine_angle_id, _spine_angle_src = _resolve_angle_journey_id(_spine_angle_raw, topic_id)
    if _spine_angle_id != _spine_angle_raw:
        print(
            f"Angle journey resolution: {_spine_angle_raw!r} → {_spine_angle_id!r} "
            f"(source={_spine_angle_src}, topic={topic_id}).",
            file=sys.stderr,
        )
    _angle_layer_by_ch: dict[int, int] = {}
    _angle_journey_warnings: list[str] = []
    if _spine_angle_id:
        from phoenix_v4.planning.angle_journey import patch_beatmap_angle_journey

        _angle_layer_by_ch, _angle_journey_warnings = patch_beatmap_angle_journey(
            beatmap, _spine_angle_id,
        )

    render_dir = Path(args.render_dir) if args.render_dir else Path("artifacts/rendered") / f"spine-{topic_id}"
    render_dir.mkdir(parents=True, exist_ok=True)

    seed = f"spine:{topic_id}:{persona_id}:{getattr(args, 'seed', '1')}"
    _frame = str(getattr(args, "frame", "somatic_first") or "somatic_first").strip()
    _book_frame = str(book_spec_for_compiler.get("book_frame") or _frame).strip()
    _n_chapters = len(beatmap.chapters)
    _emotional_seq = [
        str(getattr(ch, "emotional_job", "") or "").strip().lower()
        for ch in shaped_spine.chapters[:_n_chapters]
    ]
    _chapter_selector_targets = derive_chapter_selector_targets(
        _n_chapters,
        f"{seed}:selector",
        _emotional_seq if _emotional_seq else None,
    )
    _publishable_book = quality_profile in ("production",) or (
        bool(getattr(args, "render_book", False)) and quality_profile in ("production", "draft")
    )
    # Locale propagation (LOCALE-PROP-FIX-2026): pull the locale that flowed in via
    # --locale through BookSpec → book_spec_for_compiler into EnrichmentRequest so the
    # spine pipeline reads atoms from atoms/<persona>/<topic>/<slot>/locales/<locale>/
    # CANONICAL.txt with English fallback. Without this, non-en-US runs silently
    # produced 100% English books even when the locale CANONICAL.txt existed.
    _enrich_locale = (
        book_spec_for_compiler.get("locale")
        or getattr(args, "locale", None)
        or None
    )
    _enrichment_contract_v1 = bool(
        book_spec_for_compiler.get("enrichment_contract_v1")
    ) or str(render_dir).endswith("cli_demo_trace_run_composite_contract_v1")
    enriched = select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=teacher_for_enrich,
            persona_id=persona_id,
            topic_id=topic_id,
            seed=seed,
            spine_context={
                "frame": _frame,
                "book_frame": _book_frame,
                "book_plan_id": book_plan.plan_id,
                # F-COHERENCE: carry the plan's bound engine so enrichment routes atoms by
                # (topic, engine) — see enrichment_select.select_enrichment / _load_persona_atoms.
                "engine": str(book_spec_for_compiler.get("engine") or "").strip(),
                "atom_slot_specs": atom_slot_specs,
                "chapter_selector_targets": _chapter_selector_targets,
                "angle_id": _spine_angle_id,
                "angle_layer_by_chapter": _angle_layer_by_ch,
                "angle_journey_warnings": _angle_journey_warnings,
                "chapter_architecture_version": int(
                    book_spec_for_compiler.get("chapter_architecture_version")
                    or getattr(args, "chapter_architecture_version", None)
                    or 1
                ),
                "book_idea": str(book_spec_for_compiler.get("book_idea") or "").strip(),
                "book_motif": str(book_spec_for_compiler.get("book_motif") or "").strip(),
                "enrichment_contract_v1": _enrichment_contract_v1,
            },
            locale=_enrich_locale,
            publishable_book=_publishable_book,
            # PR #612: additive_enrichment is the only mode (no-op in EnrichmentRequest).
        ),
        repo_root,
    )
    # Post-enrichment gap audit: hard-fail in production if any gaps survived
    if quality_profile == "production":
        gap_slots = []
        for ec in enriched.chapters:
            for slot in ec.slots:
                if slot.content and slot.content.startswith("[CONTENT GAP"):
                    gap_slots.append(
                        f"ch{ec.number} {slot.slot_type}: {slot.content[:80]}"
                    )
        if gap_slots:
            raise SystemExit(
                f"[PRODUCTION GATE] Content gaps found in enriched manuscript "
                f"({len(gap_slots)} slots). Fix content banks or atom coverage before production run.\n"
                + "\n".join(f"  - {s}" for s in gap_slots[:10])
            )

        # EXERCISE-BANK-RESOLUTION-01 strict-canonical gate (production only).
        _check_exercise_strict_canonical_gate(quality_profile, enriched.enrichment_audit)
    pre_depth_words = enriched.total_words
    depth_map_path = repo_root / "config" / "depth" / "depth_module_map.yaml"
    if depth_map_path.exists() and yaml:
        depth_map = yaml.safe_load(depth_map_path.read_text(encoding="utf-8"))
        enriched = apply_depth_pass(enriched, depth_map, repo_root=repo_root)
    post_depth_words = enriched.total_words

    # V4 freeze: apply modular output format to derive per-chapter word cap and slot template.
    # Registry mode calls apply_output_format_to_plan on its Stage-2 format_plan_dict; spine mode
    # has no such dict, so we call it on a stub plan and apply the resulting target_word_range as
    # a per-chapter cap on the composed prose. Without this, modular formats (pocket_guide, etc.)
    # consistently overshoot their target ranges because runtime_fmt alone (e.g. short_book_30)
    # permits a wider budget than the modular format allows.
    _spine_format_applied: dict | None = None
    _per_chapter_word_cap: int | None = None
    if _freeze.enabled and _cli_output_format and _cli_output_format in _freeze.formats:
        try:
            from pearl_prime.modular_format_freeze import apply_output_format_to_plan as _apply_fmt
            _spine_format_applied = _apply_fmt(
                {"format_runtime_id": runtime_fmt, "chapter_count": len(enriched.chapters)},
                output_format_id=_cli_output_format,
                chapter_count=len(enriched.chapters),
                settings=_freeze,
            )
            _twr = _spine_format_applied.get("target_word_range")
            if isinstance(_twr, list) and len(_twr) == 2:
                _per_chapter_word_cap = int(_twr[1])
            print(
                f"Spine output format applied: {_cli_output_format} "
                f"(per-chapter cap {_per_chapter_word_cap}w × {len(enriched.chapters)} chapters, "
                f"runtime={runtime_fmt})",
                file=sys.stderr,
            )
        except ValueError as _fe:
            print(f"Spine output format application WARN: {_fe}", file=sys.stderr)

    # Exercise journeys: attach thesis-aligned exercises to EXERCISE slots (opt-in).
    if getattr(args, "exercise_journeys", False):
        from phoenix_v4.planning.enrichment_select import attach_exercise_journeys
        enriched = attach_exercise_journeys(enriched, seed=seed, enabled=True, repo_root=repo_root)

    from phoenix_v4.planning.accent_planner import attach_accent_plan, validate_accent_plan

    enriched = attach_accent_plan(
        enriched,
        brand_id=str(book_spec_for_compiler.get("brand_id") or "phoenix"),
        author_id=book_spec_for_compiler.get("author_id"),
        seed=seed,
        locale=_enrich_locale,
        teacher_mode=bool(book_spec_for_compiler.get("teacher_mode")),
        repo_root=repo_root,
    )
    _accent_audit = enriched.enrichment_audit or {}
    _strategy_report = _accent_audit.get("enrichment_strategy_report") or {}
    _alignment_report = _accent_audit.get("bestseller_alignment_report") or {}
    _supported_underfill = _alignment_report.get("supported_underfilled_budget_by_class") or {}
    if _supported_underfill:
        _underfill_msg = (
            "[PRODUCTION GATE] Supported accent underfill detected:\n"
            + "\n".join(f"  - {cls}: {count}" for cls, count in _supported_underfill.items())
        )
        print(_underfill_msg, file=sys.stderr)
        if quality_profile == "production":
            raise SystemExit(_underfill_msg)
    _accent_plan_errors = validate_accent_plan(enriched)
    if _accent_plan_errors and quality_profile == "production":
        raise SystemExit(
            "[PRODUCTION GATE] Accent planner anti-spam violations:\n"
            + "\n".join(f"  - {e}" for e in _accent_plan_errors)
        )

    _governance_report: dict = {}
    from phoenix_v4.planning.chapter_object_continuity import is_twelve_shape_continuity_active

    _delivery_plan = {
        "runtime_format_id": runtime_fmt,
        "book_plan_id": book_plan.plan_id,
        "twelve_shape_continuity": is_twelve_shape_continuity_active(enriched.spine_context),
    }
    # BookSlotTracker + resolve_injections are now wired inside select_enrichment().
    # Story schedule (named-character 4-arc arcs) fills SCENE slots at indices 2/5/9.
    # See enrichment_select.py: _story_schedule + _book_tracker instantiated before chapter loop.
    prose = compose_from_enriched_book(
        enriched,
        quality_profile=quality_profile,
        governance_report=_governance_report,
        artifact_dir=render_dir,
    )
    _flow_profile = flow_profile_for_runtime_format(runtime_fmt)
    _twelve_shape_delivery = bool(_delivery_plan.get("twelve_shape_continuity"))
    if _twelve_shape_delivery:
        prose = clean_for_delivery(
            prose,
            plan=_delivery_plan,
            governance_report=_governance_report,
        )
        _governance_report["twelve_shape_delivery_mode"] = "minimal"
    else:
        prose = clean_for_delivery(
            prose,
            plan=_delivery_plan,
            governance_report=_governance_report,
        )
        prose = strengthen_rendered_spine_manuscript(
            prose,
            book_seed=seed,
            flow_profile=_flow_profile,
        )
        prose = clean_for_delivery(
            prose,
            plan=_delivery_plan,
            governance_report=_governance_report,
        )
        prose = strengthen_rendered_spine_manuscript(
            prose,
            book_seed=seed,
            flow_profile=_flow_profile,
        )
        # Sprint-1: run dedupe_scene_furniture_book AFTER both strengthen passes so that
        # any repeated phrases introduced or survived through strengthen are caught here,
        # just before the scene_anchor_density check.
        prose, _whole_book_dedupe_notes = dedupe_scene_furniture_book(prose)
        if _whole_book_dedupe_notes:
            _governance_report.setdefault("whole_book_dedupe_notes", []).extend(
                _whole_book_dedupe_notes
            )
    _arch_v = int(
        book_spec_for_compiler.get("chapter_architecture_version")
        or getattr(args, "chapter_architecture_version", None)
        or 1
    )
    # OPD-137: TEACHER_DOCTRINE_INTRO preamble is prepended LAST (right before book.txt write,
    # see below) so downstream passes (per-chapter word cap via _extract_registry_chapters, locale
    # post-process, music overlay) cannot strip the "Chapter N"-less preamble block.
    #
    if not _twelve_shape_delivery:
        # Apply per-chapter word cap from modular output format (see apply_output_format_to_plan above).
        # Preserves the "Chapter N" heading line and paragraph structure so downstream gates can
        # still parse chapters via _extract_registry_chapters; only the body is truncated by words.
        if _per_chapter_word_cap:
            _chs = _extract_registry_chapters(prose)
            if _chs:
                _pre_cap_words = sum(len(c.split()) for c in _chs)
                _capped: list[str] = []
                for _ch in _chs:
                    _lines = _ch.splitlines()
                    _heading = _lines[0] if _lines else ""
                    _body = "\n".join(_lines[1:])
                    _body_words = _body.split()
                    if len(_body_words) > _per_chapter_word_cap:
                        _paras = re.split(r"\n\s*\n", _body)
                        _kept: list[str] = []
                        _used = 0
                        for _p in _paras:
                            _pw = len(_p.split())
                            if _used + _pw <= _per_chapter_word_cap:
                                _kept.append(_p)
                                _used += _pw
                            else:
                                _remain = _per_chapter_word_cap - _used
                                if _remain > 0:
                                    _kept.append(" ".join(_p.split()[:_remain]))
                                    _used = _per_chapter_word_cap
                                break
                        _body = "\n\n".join(_kept).strip()
                    _capped.append(f"{_heading}\n\n{_body}".strip() if _body else _heading)
                prose = "\n\n".join(_capped)
                _post_cap_words = sum(len(c.split()) for c in _capped)
                print(
                    f"Per-chapter word cap applied: {_pre_cap_words} → {_post_cap_words} words "
                    f"(cap {_per_chapter_word_cap}w/chapter)",
                    file=sys.stderr,
                )
        # Book-level word ceiling clamp (DEFERRED-LANE word_budget 2026-06-15).
        # The per-chapter cap above only fires for modular output formats (_cli_output_format
        # set); spine renders (standard_book et al.) have no such cap, so the post-render
        # strengthen passes + arch-v2 preamble push the book past the runtime word ceiling and
        # HARD_FAIL the book_pass word_budget gate. This clamp is the missing book-level guard:
        # it always applies in spine mode and trims the book back to cap_word_target (22000 for
        # standard_book) so render accounting matches the gate. Trims only — never pads.
        _runtime_word_ceiling = _load_runtime_word_ceiling(runtime_fmt, repo_root)
        # Blocker 1 (2026-06-17): reserve a small word budget under the ceiling for the post-clamp
        # ensure_chapter_flow_cues pass so its (short) clear-point/transition guarantee sentences do
        # not push the book back over the ceiling. Bounded so it never trims the book more than ~10%.
        _cue_reserve = min(_n_chapters * 30, max(0, (_runtime_word_ceiling or 0) // 10))
        if _runtime_word_ceiling:
            prose, _pre_clamp_words, _post_clamp_words = _clamp_book_to_word_ceiling(
                prose, _runtime_word_ceiling, reserve=_cue_reserve
            )
            if _post_clamp_words < _pre_clamp_words:
                print(
                    f"Book word ceiling clamp applied: {_pre_clamp_words} → {_post_clamp_words} words "
                    f"(ceiling {_runtime_word_ceiling}w, reserve {_cue_reserve}w, runtime={runtime_fmt})",
                    file=sys.stderr,
                )
        # Blocker 1 (2026-06-17): FINAL chapter_flow cue pass — runs AFTER all truncation (clamp +
        # per-chapter cap) so the appended clear-point / transition guarantee sentences cannot be
        # clamped away. Word-bounded (see ensure_chapter_flow_cues); only fixes the same fixable
        # errors (MISSING_CLEAR_POINT / WEAK_TRANSITIONS) the in-render glue pass targets. The
        # chapter_flow gate below remains the arbiter; this only strengthens the OUTPUT.
        prose = ensure_chapter_flow_cues(prose, flow_profile=_flow_profile, seed=seed)
        # Default cap is sourced from config/quality/scene_anchor_density_config.yaml.
        # Authored plans (config/plans/*.yaml) may override per-chapter via
        # scene_plan.scene_anchor_cap; the min() across chapters means any chapter that
        # tightens the cap tightens the book — preserving backward compat for hand-tuned plans.
        _scene_anchor_default_cap = int(
            _load_scene_anchor_density_config().get("default_cap_per_chapter", 3)
        )
        scene_anchor_cap = min(
            int((ch.scene_plan or {}).get("scene_anchor_cap", _scene_anchor_default_cap))
            for ch in book_plan.chapters
        )
        # Blocker 2 (A1-generalize, 2026-06-17): reduce any 4–8 word n-gram that exceeds the
        # per-chapter scene_anchor cap BEFORE the gate runs. Generalizes _DIRECTION_CAP_PER_CHAPTER
        # (bridge-bank directions only) and dedupe_scene_furniture_book (closed allowlist only) to
        # the full set the gate measures — HOOK lead-ins, un-allowlisted furniture variants, topic
        # restatements. Strengthens output only; the gate + its cap are unchanged and still decide.
        prose, _scene_anchor_reduce_notes = _reduce_scene_anchor_density(prose, scene_anchor_cap)
        if _scene_anchor_reduce_notes:
            _governance_report.setdefault("scene_anchor_density_reduce_notes", []).extend(
                _scene_anchor_reduce_notes
            )
            print(
                f"Scene anchor density reducer: trimmed {len(_scene_anchor_reduce_notes)} "
                f"over-cap phrase occurrence group(s) (cap {scene_anchor_cap}/chapter).",
                file=sys.stderr,
            )
        scene_anchor_violations = _scene_anchor_density_violations(prose, scene_anchor_cap)
        scene_anchor_report_path = render_dir / "scene_anchor_density_report.json"
        if scene_anchor_violations:
            scene_anchor_report_path.write_text(
                json.dumps(
                    {
                        "status": "FAIL",
                        "book_plan_id": book_plan.plan_id,
                        "scene_anchor_cap": scene_anchor_cap,
                        "violations": scene_anchor_violations,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(
                f"Scene anchor density cap: FAIL — repeated >3-word phrases exceed cap {scene_anchor_cap}. "
                f"Report: {scene_anchor_report_path}",
                file=sys.stderr,
            )
            if gates_hard:
                return 1
        else:
            scene_anchor_report_path.write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "book_plan_id": book_plan.plan_id,
                        "scene_anchor_cap": scene_anchor_cap,
                        "violations": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        # Book-audit craft strengthen (2026-06-21): dwell beats (F13), practice-density cap
        # (F7), transformation-arc landings, and terminal-sentence integrity — runs AFTER
        # scene-anchor reducer so injected dwell beats are not trimmed as over-cap phrases.
        # Strengthens OUTPUT only; register gate thresholds untouched.
        from phoenix_v4.rendering.register_output_strengthen import (
            strengthen_register_craft_output,
            spine_deprescribe_inject_enabled,
        )

        _spine_deprescribe_inject_enabled = spine_deprescribe_inject_enabled()
        if not _spine_deprescribe_inject_enabled:
            _governance_report.setdefault("spine_deprescribe_signals", []).append(
                {
                    "action": "injector_disabled",
                    "reason": (
                        "G1-residual: deprescribe one-line filler disabled on spine; "
                        "surplus prescribed-action paragraphs dropped, not replaced. "
                        "PHOENIX_SPINE_DEPRESCRIBE=1 to re-enable."
                    ),
                }
            )

        prose = strengthen_register_craft_output(
            prose,
            seed=seed or book_plan.plan_id,
            inject_deprescribe_alternative=_spine_deprescribe_inject_enabled,
        )
        # Post-strengthen flow cue pass: register craft strengthen can strip thesis /
        # actionable cues (e.g. F7 deprescription); re-run the word-bounded guarantee
        # pass so chapter_flow is scored on the final manuscript.
        prose = ensure_chapter_flow_cues(
            prose, flow_profile=_flow_profile, seed=f"{seed}:post_strengthen"
        )
        # Flow-cue guarantee lines can re-introduce F7 prescribed-action false positives
        # (imperative + timing substrings). Final cap before gates — thresholds untouched.
        from phoenix_v4.rendering.register_output_strengthen import (
            cap_prescribed_action_density as _final_cap_f7,
            _exercise_contract_by_chapter,
        )

        _f7_caps = _exercise_contract_by_chapter(_governance_report)
        _f7_max_by_chapter = {
            ch: min(contract, 1) if contract > 0 else 0 for ch, contract in _f7_caps.items()
        }
        _f7_cap_kw = {
            "max_per_chapter": 1,
            "max_by_chapter": _f7_max_by_chapter,
            "inject_deprescribe_alternative": _spine_deprescribe_inject_enabled,
        }
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        # F1/F4 dedupe must run AFTER flow-cue injection (same stage ordering as F7 cap).
        from phoenix_v4.rendering.register_output_strengthen import (
            dedupe_register_f1_paragraphs as _final_f1_dedupe,
            ensure_unique_chapter_closings as _final_f4_closings,
            remove_sub_four_word_orphan_paragraphs as _final_orphan_strip,
        )

        prose, _f1_dedupe_final = _final_f1_dedupe(prose)
        if _f1_dedupe_final:
            _governance_report.setdefault("register_f1_dedupe_notes", []).extend(_f1_dedupe_final)
        prose = _final_f4_closings(prose, seed=f"{seed}:final_close")
        prose = _final_orphan_strip(prose)
        from phoenix_v4.rendering.register_output_strengthen import (
            repair_f13_dwell_contract as _final_f13_repair,
            verify_f7_exercise_preservation,
        )

        prose = _final_f13_repair(prose, seed=f"{seed}:post_flow_f13")
        # Post-F13 flow-cue pass: dwell-beat / deprescribe inserts run after the first
        # flow guarantee; re-run so chapter_flow is scored on the final manuscript.
        prose = ensure_chapter_flow_cues(
            prose, flow_profile=_flow_profile, seed=f"{seed}:post_f13_flow"
        )
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        prose = _final_f13_repair(prose, seed=f"{seed}:post_f13_flow_recheck")
        # Post-flow orphan strip before floor padding (flow inserts can leak slot labels).
        prose = _final_orphan_strip(prose)
        # G1 (render-hardening 2026-07-02, fast-follow to #4566): the word-count FLOOR
        # PADDER is DISABLED on the spine path. `ensure_word_count_floor` used to append
        # standalone one-line "deprescribe"-class filler to hit a word floor — the exact
        # stitched-one-liner class the dwell injector produced and that F14 now HARD_FAILs.
        # #4566 no-op'd the function body; this closes the CALL SITE too so a future
        # re-enable of the function cannot silently re-introduce choppy filler on spine.
        # DOCTRINE: an under-length spine book is a THIN-POOL / atom signal (surface it,
        # do not paper over it) — never LLM-pad, never standalone-filler-pad. See memory
        # feedback_atom_deficit_is_shape_not_count + Q-FASTFOLLOW-01 (default a).
        # Kill-switch to re-enable padding on spine (NOT recommended):
        #   PHOENIX_SPINE_WORD_FLOOR_PAD=1
        from phoenix_v4.rendering.book_renderer import _runtime_word_range as _book_word_range
        from phoenix_v4.rendering.register_output_strengthen import ensure_word_count_floor

        _spine_floor_pad_enabled = (
            os.environ.get("PHOENIX_SPINE_WORD_FLOOR_PAD", "").strip().lower()
            in ("1", "true", "on", "yes")
        )
        _word_bounds = _book_word_range(runtime_fmt)
        if _word_bounds:
            _under = len(prose.split()) < _word_bounds[0]
            if _spine_floor_pad_enabled:
                prose = ensure_word_count_floor(prose, floor=_word_bounds[0], seed=f"{seed}:floor")
            elif _under:
                # Surface, do not pad. Under-length spine output = thin atom pool.
                _governance_report.setdefault("spine_word_floor_signals", []).append(
                    {
                        "stage": "post_flow_pre_gate",
                        "word_count": len(prose.split()),
                        "floor": _word_bounds[0],
                        "action": "not_padded",
                        "reason": (
                            "spine word-floor padder disabled (G1/#4566); under-length is a "
                            "thin-pool / atom-shape signal, not filler territory"
                        ),
                    }
                )
        # Floor padding can duplicate closings and strip flow cues — repair before gates.
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        prose = ensure_chapter_flow_cues(
            prose, flow_profile=_flow_profile, seed=f"{seed}:post_floor_flow"
        )
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        prose = _final_f4_closings(prose, seed=f"{seed}:post_all_flow")
        prose = _final_orphan_strip(prose)
        prose = ensure_chapter_flow_cues(
            prose, flow_profile=_flow_profile, seed=f"{seed}:post_all_flow"
        )
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        # F7 cap can drop one_hour_book below word_range floor. G1: on spine, do NOT re-pad
        # (see the disabled first call site above) — surface the under-length as a thin-pool
        # signal. Only re-pad when the PHOENIX_SPINE_WORD_FLOOR_PAD kill-switch is set.
        if _word_bounds and len(prose.split()) < _word_bounds[0]:
            if _spine_floor_pad_enabled:
                prose = ensure_word_count_floor(prose, floor=_word_bounds[0], seed=f"{seed}:floor_final")
                prose = ensure_chapter_flow_cues(
                    prose, flow_profile=_flow_profile, seed=f"{seed}:floor_final_flow"
                )
                prose = _final_f4_closings(prose, seed=f"{seed}:floor_final_close")
                prose = _final_orphan_strip(prose)
            else:
                _governance_report.setdefault("spine_word_floor_signals", []).append(
                    {
                        "stage": "post_f7_pre_gate",
                        "word_count": len(prose.split()),
                        "floor": _word_bounds[0],
                        "action": "not_padded",
                        "reason": "spine word-floor padder disabled (G1/#4566); thin-pool signal",
                    }
                )

        # Floor / flow passes after post_f13_flow_recheck can re-break register (F13/F4).
        prose = _final_f13_repair(prose, seed=f"{seed}:pre_gate_f13")
        prose = _final_f4_closings(prose, seed=f"{seed}:pre_gate_f4")
        prose = ensure_chapter_flow_cues(
            prose, flow_profile=_flow_profile, seed=f"{seed}:pre_gate_flow"
        )
        prose = _final_f13_repair(prose, seed=f"{seed}:pre_gate_f13_recheck")
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        prose = _final_orphan_strip(prose)
        from phoenix_v4.rendering.register_output_strengthen import (
            destack_adjacent_inject_paragraphs as _destack_inject_paras,
            fold_standalone_inject_paragraphs as _fold_inject_paras,
        )

        prose = _destack_inject_paras(prose)
        # G1-residual Phase-2 (cohesion restore): weave any surviving standalone
        # one-line inject paragraphs (within-slot bridges + formulaic practice
        # intros) into a neighbor narrative paragraph, and mark bare Title-Case
        # section titles as real headings. Returns the composer floor to the
        # pre-injector 0-5% beat-line band (docs/BESTSELLER_QUALITY_ARCHAEOLOGY_
        # 2026-07-03.md). PHOENIX_INJECT_FOLD=0 / PHOENIX_SECTION_HEADING_MARK=0
        # disable. Deterministic; no LLM; gate thresholds untouched.
        prose = _fold_inject_paras(prose)
        # Folding a practice-intro into the exercise it introduces can tip that
        # paragraph into F7 prescribed-action classification, so re-cap F7 once more
        # AFTER the fold (drop-mode on spine — never re-inject filler). Keeps the F7
        # per-chapter invariant without disturbing the restored 0-5% beat-line floor.
        prose = _final_cap_f7(prose, **_f7_cap_kw)
        # F6 cadence had no pre-gate repair: the single break inside strengthen_register_craft_output
        # (above) runs BEFORE the flow-cue / floor / F4 / F13 convergence passes, which re-introduce
        # repeating sentence-length 4-grams (e.g. [9,9,9,10] ×3 → register F6 FAIL on social_anxiety /
        # somatic_healing). Add the missing FINAL break here, mirroring the pre-gate F4/F13 repairs. It
        # only lengthens the 3rd+ occurrence of each repeating cadence (~10-12 words/book), makes closing
        # lines MORE unique (F4-safe), preserves cue substrings (chapter_flow-safe), and adds no
        # imperative/timing tokens (F7-safe). Strengthens OUTPUT only; the register gate remains arbiter.
        from phoenix_v4.rendering.register_output_strengthen import (
            break_pedagogical_cadence_repetition as _final_f6_break,
            suppress_unbudgeted_template_cadence as _final_cadence_suppress,
        )

        prose = _final_f6_break(prose, seed=f"{seed}:pre_gate_f6")
        prose = _final_cadence_suppress(prose)

        _f7_preservation_violations = verify_f7_exercise_preservation(
            prose,
            governance_report=_governance_report,
            max_prescribed_per_chapter=1,
        )
        if _f7_preservation_violations:
            _governance_report.setdefault(
                "f7_exercise_preservation_violations", []
            ).extend(_f7_preservation_violations)
            print(
                "F7 exercise-preservation check: "
                + "; ".join(_f7_preservation_violations),
                file=sys.stderr,
            )
    word_count = len(prose.split())
    _quality_gate_failures: list[str] = []
    _chapter_flow_status = "SKIPPED"
    _chapter_flow_report_name = "chapter_flow_report.json"
    _craft_status = "SKIPPED"
    _craft_overall = 0.0
    _ei_status = "SKIPPED"
    _ei_composite = 0.0
    _editorial_status = "SKIPPED"
    _memorable_status = "SKIPPED"
    _memorable_quote_chapters = 0
    _memorable_total_chapters = 0
    _transform_status = "SKIPPED"
    _book_pass_status = "SKIPPED"
    _register_status = "SKIPPED"
    _register_verdict = ""
    _register_f_counts: dict[str, int] = {}

    def _write_gate_report(report_name: str, payload: dict) -> Path:
        report_path = render_dir / report_name
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return report_path

    if gates_run:
        _chapters_for_quality = _extract_registry_chapters(prose)
        _book_path_for_gates = render_dir / "book.txt"
        _book_path_for_gates.write_text(prose, encoding="utf-8")

        try:
            _flow_report = chapter_flow_gate_report(
                prose, runtime_format_id=runtime_fmt
            )
            _flow_report_path = render_dir / "chapter_flow_report.json"
            _flow_report_path.write_text(json.dumps(_flow_report, indent=2), encoding="utf-8")
            _chapter_flow_status = str(_flow_report.get("status", "PASS"))
            print(
                f"Chapter flow gate: {_flow_report['status']} "
                f"({_flow_report['failed_chapters']}/{_flow_report['chapter_count']} failed). "
                f"Report: {_flow_report_path}",
                file=sys.stderr,
            )
            if _flow_report["status"] != "PASS":
                for _ch in _flow_report.get("chapters", []):
                    if _ch.get("status") != "PASS":
                        print(
                            f"  Ch {_ch['chapter']}: {', '.join(_ch.get('errors', []))}",
                            file=sys.stderr,
                        )
                if _block_on_fail(quality_profile, "chapter_flow"):
                    _quality_gate_failures.append("chapter_flow")
        except Exception as _e:
            _chapter_flow_status = "SKIPPED"
            print(f"Chapter flow gate error (non-blocking): {_e}", file=sys.stderr)
            _write_gate_report(
                _chapter_flow_report_name,
                {"status": "SKIPPED", "reason": f"chapter_flow gate error: {_e}"},
            )

        try:
            from phoenix_v4.quality.register_gate import evaluate_register

            _reg_result = evaluate_register(
                prose,
                teacher_id=teacher_for_enrich or "",
                persona_id=persona_id,
                topic_id=topic_id,
                quality_profile=quality_profile,
                runtime_format=runtime_fmt,
            )
            _register_verdict = _reg_result.verdict
            _register_f_counts = {}
            for _f in _reg_result.findings:
                _register_f_counts[_f.failure_id] = _register_f_counts.get(_f.failure_id, 0) + 1
            _register_status = (
                "PASS"
                if _register_verdict in ("PASS", "ADVISORY")
                else ("WARN" if _register_verdict == "WARN" else "FAIL")
            )
            _register_path = _write_gate_report(
                "register_gate_report.json",
                {
                    **_reg_result.to_json(),
                    "status": _register_status,
                    "failure_counts_by_id": _register_f_counts,
                },
            )
            print(
                f"Register gate: {_register_verdict} "
                f"(F2={_register_f_counts.get('F2', 0)}, "
                f"F6={_register_f_counts.get('F6', 0)}, "
                f"F12={_register_f_counts.get('F12', 0)}). "
                f"Report: {_register_path}",
                file=sys.stderr,
            )
            if gates_hard and _register_verdict not in ("PASS", "ADVISORY"):
                _quality_gate_failures.append("register_gate")
        except Exception as _e:
            _register_status = "SKIPPED"
            print(f"Register gate error (non-blocking): {_e}", file=sys.stderr)
            _write_gate_report(
                "register_gate_report.json",
                {"status": "SKIPPED", "reason": f"register_gate error: {_e}"},
            )

        try:
            from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft

            _craft_results = []
            for _i, _ch_text in enumerate(_chapters_for_quality):
                _craft = evaluate_bestseller_craft(_ch_text)
                _craft_results.append(
                    {
                        "chapter": _i + 1,
                        "status": _craft.status,
                        "move_scores": _craft.move_scores,
                        "issues": _craft.issues,
                        "remediation": _craft.remediation,
                        "metrics": _craft.metrics,
                    }
                )
            _per_ch_means = []
            for _cr in _craft_results:
                _scores = _cr.get("move_scores", {})
                if _scores:
                    _per_ch_means.append(sum(_scores.values()) / len(_scores))
            _craft_overall = (
                sum(_per_ch_means) / len(_per_ch_means) if _per_ch_means else 0.0
            )
            _craft_status = (
                "PASS" if _craft_overall >= 0.4 else ("WARN" if _craft_overall >= 0.2 else "FAIL")
            )
            print(
                f"Bestseller craft gate (advisory): {_craft_status} — "
                f"overall ONTGP score {_craft_overall:.2f}",
                file=sys.stderr,
            )
            _flow_rpath = render_dir / "chapter_flow_report.json"
            if _flow_rpath.exists():
                _fr = json.loads(_flow_rpath.read_text(encoding="utf-8"))
                _fr["bestseller_craft"] = {
                    "overall_score": round(_craft_overall, 4),
                    "per_chapter": _craft_results,
                }
                _flow_rpath.write_text(json.dumps(_fr, indent=2), encoding="utf-8")
        except Exception as _e:
            print(f"Bestseller craft gate error (non-blocking): {_e}", file=sys.stderr)
            _craft_status = "SKIPPED"

        if args.enforce_scene_gate:
            try:
                from phoenix_v4.qa.scene_anti_genericity_gate import enforce_scene_gate as _enforce_scene_gate

                _scene_proses = _chapters_for_quality
                if _scene_proses:
                    _scene_result = _enforce_scene_gate(_scene_proses, mode=args.scene_gate_mode)
                    _scene_report_dir = render_dir / "scene_gate"
                    _scene_report_dir.mkdir(parents=True, exist_ok=True)
                    _scene_report_path = _scene_report_dir / f"spine-{topic_id}.json"
                    _scene_report_path.write_text(
                        json.dumps(
                            {
                                "status": _scene_result.status,
                                "mode": _scene_result.mode,
                                "blocking": _scene_result.blocking,
                                "errors": _scene_result.report.errors,
                                "warnings": _scene_result.report.warnings,
                                "metrics": _scene_result.report.metrics,
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
                    if _scene_result.blocking:
                        print(
                            f"Scene anti-genericity gate FAILED. Report: {_scene_report_path}",
                            file=sys.stderr,
                        )
                        _quality_gate_failures.append("scene_anti_genericity")
                    else:
                        print(
                            f"Scene anti-genericity gate {_scene_result.status}. Report: {_scene_report_path}",
                            file=sys.stderr,
                        )
            except Exception as _e:
                print(f"Scene anti-genericity gate error: {_e}", file=sys.stderr)
                _quality_gate_failures.append("scene_anti_genericity")

        # EI V2 rigorous evaluation (spine mode: chapter prose direct evaluation)
        try:
            from scripts.ci.run_ei_v2_rigorous_eval import evaluate_chapter as _ei_eval_chapter

            _ei_chapters = []
            for _idx, _chapter_text in enumerate(_chapters_for_quality):
                _ev = _ei_eval_chapter(
                    _chapter_text,
                    _idx,
                    {},
                    persona_id,
                    topic_id,
                    _chapters_for_quality,
                )
                _ei_chapters.append(
                    {
                        "chapter_index": _idx + 1,
                        "word_count": _ev.word_count,
                        "composite": round(_ev.composite, 4),
                        "therapeutic_value": round(_ev.therapeutic_value, 4),
                        "emotional_coherence": round(_ev.emotional_coherence, 4),
                        "engagement": round(_ev.engagement, 4),
                        "chapter_journey": round(_ev.chapter_journey, 4),
                        "cohesion": round(_ev.cohesion, 4),
                        "listen_experience": round(_ev.listen_experience, 4),
                        "marketability": round(_ev.marketability, 4),
                        "safety_compliance": round(_ev.safety_compliance, 4),
                        "content_uniqueness": round(_ev.content_uniqueness, 4),
                        "somatic_precision": round(_ev.somatic_precision, 4),
                        "issues": _ev.issues,
                        "uniqueness_evidence": {
                            "scoring_mode": (_ev.uniqueness_evidence or {}).get("scoring_mode"),
                            "worst_pair": (_ev.uniqueness_evidence or {}).get("worst_pair"),
                            "max_prose_similarity": (_ev.uniqueness_evidence or {}).get("max_prose_similarity"),
                            "max_ngram_overlap": (_ev.uniqueness_evidence or {}).get("max_ngram_overlap"),
                        },
                    }
                )
            _ei_composite = (
                sum(ch.get("composite", 0.0) for ch in _ei_chapters) / len(_ei_chapters)
                if _ei_chapters
                else 0.0
            )
            _ei_status = "PASS" if _ei_composite >= 0.55 else "FAIL"
            _ei_payload = {
                "source": "spine_pipeline",
                "topic_id": topic_id,
                "persona_id": persona_id,
                "status": _ei_status,
                "composite": round(_ei_composite, 4),
                "chapter_count": len(_ei_chapters),
                "chapters": _ei_chapters,
            }
            _ei_report_path = _write_gate_report("ei_v2_report.json", _ei_payload)
            print(
                f"EI V2: {_ei_status} — composite {_ei_composite:.2f}. Report: {_ei_report_path}",
                file=sys.stderr,
            )
            if gates_hard and _ei_composite < 0.55:
                _quality_gate_failures.append("ei_v2")
        except Exception as _e:
            _ei_status = "SKIPPED"
            _ei_composite = 0.0
            _ei_report_path = _write_gate_report(
                "ei_v2_report.json",
                {"status": "SKIPPED", "reason": f"ei_v2 evaluation error: {_e}"},
            )
            print(
                f"EI V2: SKIPPED — {_e}. Report: {_ei_report_path}",
                file=sys.stderr,
            )

        # Bestseller editorial + structured editorial report
        try:
            from phoenix_v4.qa.editorial_report import generate_editorial_report
            from phoenix_v4.rendering.book_renderer import _runtime_word_range as _editorial_runtime_word_range

            spine_plan = {
                "source": "spine_pipeline",
                "topic_id": topic_id,
                "persona_id": persona_id,
                "teacher_id": teacher_for_enrich or "",
                "runtime_format_id": runtime_fmt,
                "chapter_count": len(enriched.chapters),
            }
            def _strip_rendered_chapter_heading(chapter_text: str) -> str:
                _lines = (chapter_text or "").splitlines()
                if _lines and re.match(r"^\s*Chapter\s+\d+\s*$", _lines[0].strip()):
                    _lines = _lines[1:]
                if _lines and _lines[0].strip() and not _lines[0].strip().endswith((".", "!", "?")):
                    _lines = _lines[1:]
                return "\n".join(_lines).strip()

            _chapters_for_editorial = [
                _strip_rendered_chapter_heading(_ch) for _ch in _chapters_for_quality
            ]
            _prose_map = {f"chapter_{i}": text for i, text in enumerate(_chapters_for_editorial)}
            _editorial_runtime_bounds = _editorial_runtime_word_range(runtime_fmt)
            if _editorial_runtime_bounds and _chapters_for_editorial:
                _avg_min = _editorial_runtime_bounds[0] / max(1, len(_chapters_for_editorial))
                _avg_max = _editorial_runtime_bounds[1] / max(1, len(_chapters_for_editorial))
                # Short audio books intentionally use uneven chapter lengths.
                # Score per-chapter budget as a runway around the format target,
                # not as a longform 1,500-3,500w chapter requirement.
                _editorial_word_min = max(120, int(_avg_min * 0.50))
                _editorial_word_max = max(_editorial_word_min + 100, int(_avg_max * 1.80))
            else:
                _editorial_word_min = 1500
                _editorial_word_max = 3500
            _editorial_obj = generate_editorial_report(
                "\n\n".join(_chapters_for_editorial),
                _chapters_for_editorial,
                word_target_min=_editorial_word_min,
                word_target_max=_editorial_word_max,
            )
            _editorial_dict = _editorial_obj.to_dict()
            _drift_count = sum(
                1
                for _chapter in _editorial_dict.get("chapter_assessments", [])
                if not _chapter.get("thesis_aligned", True)
            )
            _flow_score = 1.0 if _chapter_flow_status == "PASS" else (0.6 if _chapter_flow_status == "WARN" else 0.0)
            _editorial_status = (
                "PASS"
                if _editorial_obj.grade == "PASS"
                else ("WARN" if _editorial_obj.grade == "NEEDS_REVISION" else "FAIL")
            )
            _editorial_report = {
                "status": _editorial_status,
                "spine_plan": spine_plan,
                "prose_map": {"chapter_count": len(_prose_map)},
                "grade": _editorial_obj.grade,
                "thesis_drift_chapters": _drift_count,
                "ontgp_score": round(_craft_overall, 4),
                "flow_score": round(_flow_score, 4),
                "editorial": _editorial_dict,
            }
            _editorial_path = _write_gate_report("editorial_report.json", _editorial_report)
            print(
                f"Editorial report: {_editorial_status} — thesis drift {_drift_count} chapters, "
                f"ONTGP {_craft_overall:.2f}, flow {_flow_score:.2f}. Report: {_editorial_path}",
                file=sys.stderr,
            )
            if gates_hard and _editorial_status == "FAIL":
                _quality_gate_failures.append("editorial")
        except Exception as _e:
            _editorial_status = "SKIPPED"
            _editorial_path = _write_gate_report(
                "editorial_report.json",
                {"status": "SKIPPED", "reason": f"editorial gate error: {_e}"},
            )
            print(f"Editorial report: SKIPPED — {_e}. Report: {_editorial_path}", file=sys.stderr)

        # Memorable line gate
        try:
            from phoenix_v4.quality.memorable_line_gate import evaluate_memorable_lines

            _memorable_per_chapter = []
            for _idx, _chapter in enumerate(_chapters_for_quality):
                _res = evaluate_memorable_lines(_chapter)
                _memorable_per_chapter.append(
                    {
                        "chapter": _idx + 1,
                        "status": _res.status,
                        "memorable_line_count": _res.memorable_line_count,
                        "best_candidates": _res.best_candidates,
                        "issues": _res.issues,
                        "metrics": _res.metrics,
                    }
                )
            _memorable_total_chapters = len(_memorable_per_chapter)
            _memorable_quote_chapters = sum(
                1 for _ch in _memorable_per_chapter if _ch.get("memorable_line_count", 0) >= 2
            )
            _memorable_status = (
                "PASS"
                if _memorable_total_chapters > 0 and _memorable_quote_chapters == _memorable_total_chapters
                else ("WARN" if _memorable_quote_chapters > 0 else "FAIL")
            )
            _memorable_path = _write_gate_report(
                "memorable_line_report.json",
                {
                    "status": _memorable_status,
                    "chapters_with_two_or_more_quotable_lines": _memorable_quote_chapters,
                    "chapter_count": _memorable_total_chapters,
                    "chapters": _memorable_per_chapter,
                },
            )
            print(
                f"Memorable lines: {_memorable_quote_chapters} chapters with >=2 quotable lines / "
                f"{_memorable_total_chapters}. Report: {_memorable_path}",
                file=sys.stderr,
            )
        except Exception as _e:
            _memorable_status = "SKIPPED"
            _memorable_path = _write_gate_report(
                "memorable_line_report.json",
                {"status": "SKIPPED", "reason": f"memorable line gate error: {_e}"},
            )
            print(f"Memorable lines: SKIPPED — {_e}. Report: {_memorable_path}", file=sys.stderr)

        # Transformation heatmap
        try:
            from phoenix_v4.quality.transformation_heatmap import run_heatmap_from_path

            _heatmap = run_heatmap_from_path(_book_path_for_gates)
            _transform_status_raw = str(_heatmap.get("status", "warn")).upper()
            _transform_status = (
                "PASS" if _transform_status_raw == "PASS" else ("WARN" if _transform_status_raw == "WARN" else "FAIL")
            )
            _transform_path = _write_gate_report(
                "transformation_heatmap.json",
                {
                    "status": _transform_status,
                    "heatmap": _heatmap,
                },
            )
            print(
                f"Transformation arc: {_transform_status}. Report: {_transform_path}",
                file=sys.stderr,
            )
        except Exception as _e:
            _transform_status = "SKIPPED"
            _transform_path = _write_gate_report(
                "transformation_heatmap.json",
                {"status": "SKIPPED", "reason": f"transformation heatmap error: {_e}"},
            )
            print(f"Transformation arc: SKIPPED — {_e}. Report: {_transform_path}", file=sys.stderr)

        # Book pass gate (spine-compatible fallback)
        try:
            from phoenix_v4.planning.enrichment_select import _load_runtime_word_bounds as _runtime_bounds_for_book_pass

            _runtime_bounds = _runtime_bounds_for_book_pass(runtime_fmt, repo_root)
            _budget_ok = True
            if _runtime_bounds:
                _budget_ok = _runtime_bounds[0] <= word_count <= _runtime_bounds[1]
            _roles = [
                str(getattr(_chapter, "role", "")).strip().lower()
                for _chapter in enriched.chapters
                if str(getattr(_chapter, "role", "")).strip()
            ]
            _distinct_roles = sorted(set(_roles))
            _band_ok = len(_distinct_roles) >= 3 if len(_roles) >= 6 else len(_distinct_roles) >= 2

            # OPD-20260518-002 / ws_flow_glue_selector_cap_enforcement_20260517:
            # identity_stages previously checked enrichment_audit.depth_modules_added,
            # but those depth-modules are word-budget side effects — they only fire
            # when chapters need more words. Standard_book renders that meet word
            # targets without depth enrichment do NOT add recognition_depth /
            # integration_landing modules, so this check spuriously FAILed for valid
            # standard_book content (Junko + Miyuki smokes 2026-05-19).
            # Logic now lives in phoenix_v4.quality.identity_stages_check so the
            # check has a stable unit-test surface.
            from phoenix_v4.quality.identity_stages_check import compute_identity_stages

            _audit_modules = []
            for _entry in (enriched.enrichment_audit or {}).get("depth_modules_added", []):
                if isinstance(_entry, dict):
                    _module = str(_entry.get("module", "")).strip()
                    if _module:
                        _audit_modules.append(_module)
            _identity_stage_tags, _identity_stage_count, _identity_ok = compute_identity_stages(
                _roles, _audit_modules,
            )

            _last_chapter = (_chapters_for_quality[-1] if _chapters_for_quality else "").lower()
            _callback_ok = any(
                _kw in _last_chapter
                for _kw in ("from now on", "next", "choose", "practice", "still", "start")
            )

            _angle_coherence_status = "SKIPPED"
            _angle_coherence_detail: dict = {"reason": "no angle_id or quality inputs"}
            try:
                from phoenix_v4.quality.angle_journey_coherence import (
                    evaluate_angle_journey_coherence,
                )

                # Blocker 4 (2026-06-17): use the registry-resolved angle id (see the patch site
                # above) so the gate's merge_angle_journey() finds the same 5-layer progression /
                # named_object the slots were injected from — not the raw catalog slug.
                _spine_angle = _spine_angle_id
                _angle_layers = dict(
                    (enriched.spine_context or {}).get("angle_layer_by_chapter") or {}
                )
                _ch_proses = [
                    (c.split("\n\n", 2)[-1] if "\n\n" in c else c)
                    for c in (_chapters_for_quality or [])
                ]
                _aj_result = evaluate_angle_journey_coherence(
                    angle_id=_spine_angle,
                    runtime_format=runtime_fmt,
                    topic_id=topic_id,
                    chapter_proses=_ch_proses,
                    angle_layer_by_chapter=_angle_layers,
                    enriched_chapters=enriched.chapters,
                )
                _angle_coherence_status = "PASS" if _aj_result.valid else "FAIL"
                _angle_coherence_detail = {
                    "errors": _aj_result.errors,
                    "warnings": _aj_result.warnings,
                    "metrics": _aj_result.metrics,
                }
            except Exception as _aj_exc:
                _angle_coherence_status = "SKIPPED"
                _angle_coherence_detail = {"reason": f"angle_journey_coherence error: {_aj_exc}"}

            _book_pass_checks = {
                "word_budget": {
                    "status": "PASS" if _budget_ok else "FAIL",
                    "word_count": word_count,
                    "target_range": list(_runtime_bounds) if _runtime_bounds else None,
                },
                "band_distribution": {
                    "status": "PASS" if _band_ok else "FAIL",
                    "distinct_roles": _distinct_roles,
                    "distinct_count": len(_distinct_roles),
                },
                "identity_stages": {
                    "status": "PASS" if _identity_ok else "FAIL",
                    "stages": _identity_stage_tags,
                    "stage_count": _identity_stage_count,
                },
                "callback_completion": {
                    "status": "PASS" if _callback_ok else "FAIL",
                },
                "angle_journey_coherence": {
                    "status": _angle_coherence_status,
                    **_angle_coherence_detail,
                },
                "atom_metadata_subchecks": {
                    "status": "SKIPPED",
                    "reason": "spine mode has no compiled atom_ids/chapter_slot_sequence metadata gates",
                },
            }
            _book_pass_failures = [
                _name
                for _name, _check in _book_pass_checks.items()
                if _check.get("status") == "FAIL"
            ]
            _book_pass_status = "PASS" if not _book_pass_failures else "FAIL"
            _book_pass_path = _write_gate_report(
                "book_pass_report.json",
                {
                    "status": _book_pass_status,
                    "source": "spine_pipeline",
                    "checks": _book_pass_checks,
                    "failures": _book_pass_failures,
                },
            )
            print(f"Book pass gate: {_book_pass_status}. Report: {_book_pass_path}", file=sys.stderr)
            if gates_hard and _book_pass_status == "FAIL":
                _quality_gate_failures.append("book_pass")
        except Exception as _e:
            _book_pass_status = "SKIPPED"
            _book_pass_path = _write_gate_report(
                "book_pass_report.json",
                {"status": "SKIPPED", "reason": f"book pass gate error: {_e}"},
            )
            print(f"Book pass gate: SKIPPED — {_e}. Report: {_book_pass_path}", file=sys.stderr)
    else:
        _write_gate_report(
            _chapter_flow_report_name,
            {"status": "SKIPPED", "reason": "quality gates disabled (--skip-quality-gates)"},
        )
        _write_gate_report("ei_v2_report.json", {"status": "SKIPPED", "reason": "quality gates disabled"})
        _write_gate_report("editorial_report.json", {"status": "SKIPPED", "reason": "quality gates disabled"})
        _write_gate_report("memorable_line_report.json", {"status": "SKIPPED", "reason": "quality gates disabled"})
        _write_gate_report("transformation_heatmap.json", {"status": "SKIPPED", "reason": "quality gates disabled"})
        _write_gate_report("book_pass_report.json", {"status": "SKIPPED", "reason": "quality gates disabled"})

    if args.out:
        _spine_ctx_out = enriched.spine_context or {}
        _accent_beats_by_chapter = {
            int(ch.number): [b.to_plan_dict() if hasattr(b, "to_plan_dict") else dict(b)
                             for b in (getattr(ch, "accent_beats", None) or [])]
            for ch in enriched.chapters
            if getattr(ch, "accent_beats", None)
        }
        plan_out = {
            "source": "spine_pipeline",
            "topic_id": topic_id,
            "persona_id": persona_id,
            "teacher_id": teacher_for_enrich or "",
            "runtime_format": runtime_fmt,
            "output_format_id": _cli_output_format or None,
            "target_word_range": (_spine_format_applied or {}).get("target_word_range"),
            "format_structural_id": (_spine_format_applied or {}).get("format_structural_id"),
            "book_plan_id": book_plan.plan_id,
            "word_count": word_count,
            "chapter_count": len(enriched.chapters),
            "pre_depth_total_words": pre_depth_words,
            "post_depth_total_words": post_depth_words,
            "chapter_architecture_version": _arch_v,
            "angle_id": _spine_angle_id,
            "chapter_planner_warnings": list(
                _spine_ctx_out.get("chapter_planner_warnings") or []
            ),
            "accent_budget": dict(_spine_ctx_out.get("accent_budget") or {}),
            "accent_signature": _spine_ctx_out.get("accent_signature"),
            "story_mix_profile": _spine_ctx_out.get("story_mix_profile"),
            "accent_assignments": list(_spine_ctx_out.get("accent_assignments") or []),
            "accent_beats_by_chapter": _accent_beats_by_chapter,
        }
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(plan_out, indent=2, ensure_ascii=False))
        print(f"Wrote {args.out}")

    _music_audit_spine: dict | None = None
    if args.render_book:
        book_path = render_dir / "book.txt"
        _prose_out = prose
        _music_mode = getattr(args, "music_mode", "none") or "none"
        _musician_id = (getattr(args, "musician_id", None) or "").strip()
        if _music_mode != "none" and _musician_id:
            from phoenix_v4.rendering.music_manuscript_overlay import apply_music_overlay_to_manuscript

            _prose_out, _music_audit = apply_music_overlay_to_manuscript(
                prose,
                repo_root=repo_root,
                music_mode=_music_mode,
                musician_id=_musician_id,
                persona_id=persona_id,
                topic_id=topic_id,
                book_seed=str(seed),
            )
            _music_audit_spine = _music_audit
            (render_dir / "music_overlay_audit.json").write_text(
                json.dumps(_music_audit, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        # Locale post-processing for spine mode: replace English template strings
        # (bridges, transitions, chapter titles, practice labels) with locale versions
        # from config/localization/pipeline_templates_<locale>.yaml. Mirrors the
        # registry-mode post-pass in phoenix_v4/rendering/book_renderer.py.
        _spine_locale = getattr(args, "locale", None) or ""
        if _spine_locale and _spine_locale != "en-US":
            try:
                from phoenix_v4.rendering.locale_templates import localize_rendered_text

                _prose_out = localize_rendered_text(_prose_out, _spine_locale)
            except Exception as _loc_e:
                print(
                    f"Warning: spine-mode locale post-process skipped for {_spine_locale}: {_loc_e}",
                    file=sys.stderr,
                )
        # OPD-137: prepend TEACHER_DOCTRINE_INTRO preamble LAST so it survives every
        # downstream pass. Triggers whenever the atom file exists for the
        # teacher × persona × topic combo (atom presence is itself the opt-in signal,
        # independent of --chapter-architecture-version). Operator memory: spec §2.4 + OPD-130.
        if teacher_for_enrich:
            _intro_atom = (
                repo_root / "atoms" / persona_id / topic_id
                / "TEACHER_DOCTRINE_INTRO" / teacher_for_enrich.lower() / "CANONICAL.txt"
            )
            if _intro_atom.is_file():
                from phoenix_v4.planning.chapter_planner import resolve_teacher_doctrine_intro

                _preamble = resolve_teacher_doctrine_intro(
                    persona_id, topic_id, teacher_for_enrich, repo_root,
                    chapter_architecture_version=2,
                )
                if _preamble:
                    _prose_out = f"Note on the Teachings\n\n{_preamble}\n\n{_prose_out}"
        book_path.write_text(_prose_out, encoding="utf-8")
        print(f"Rendered book (spine mode): {book_path}")
        _gcp = getattr(args, "golden_chapter_pilot", None)
        if _gcp is not None:
            try:
                from phoenix_v4.rendering.golden_chapter_synthesis import (
                    write_golden_chapter_pilot_artifacts,
                )

                _rp = write_golden_chapter_pilot_artifacts(
                    manuscript_text=_prose_out,
                    enriched=enriched,
                    chapter_number_1based=int(_gcp),
                    out_dir=render_dir,
                    topic_id=topic_id,
                )
                print(f"Golden chapter pilot report: {_rp}", file=sys.stderr)
            except Exception as _gce:
                print(f"Golden chapter pilot: FAIL — {_gce}", file=sys.stderr)

        budget_obj = budget_from_enriched(enriched)
        budget_obj["source"] = "spine_pipeline"
        budget_obj["book_plan_id"] = book_plan.plan_id
        # OPD-137 fix: budget.json word_count must match the DELIVERED book.txt
        # (_prose_out), which now carries the TEACHER_DOCTRINE_INTRO preamble prepended
        # just above book_path.write_text(_prose_out). The internal `word_count`
        # (= len(prose.split())) stays the body-prose figure that feeds the runtime
        # word-budget gate, since the editorial "Note on the Teachings" front-matter
        # should not count toward runtime bounds. Reporting the delivered count keeps
        # budget.json honest about the artifact on disk (test_spine_pipeline_integration
        # ::test_spine_mode_budget_word_count_matches_book) and also corrects the
        # pre-existing music/locale-overlay drift.
        budget_obj["word_count"] = len(_prose_out.split())
        budget_obj["body_word_count"] = word_count
        budget_obj["pre_depth_total_words"] = pre_depth_words
        budget_obj["post_depth_total_words"] = post_depth_words
        (render_dir / "budget.json").write_text(
            json.dumps(budget_obj, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (render_dir / "enrichment_audit.json").write_text(
            json.dumps(enriched.enrichment_audit, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )
        _contract_id = "cli_demo_trace_run_composite_contract_v1"
        if str(render_dir).endswith(_contract_id):
            _write_enrichment_contract_reports(
                enriched=enriched,
                render_dir=render_dir,
                contract_id=_contract_id,
                topic_id=topic_id,
                persona_id=persona_id,
                runtime_format=runtime_fmt,
            )
        _spa = enriched.enrichment_audit.get("section_packet_audit")
        _spa_payload: dict | list | None = None
        if isinstance(_spa, dict):
            _spa_payload = dict(_spa)
            if _music_audit_spine is not None:
                _spa_payload["musician_overlay"] = _music_audit_spine
        elif isinstance(_spa, list):
            _spa_payload = {
                "slots": list(_spa),
                "slot_count": len(_spa),
            }
            if _music_audit_spine is not None:
                _spa_payload["musician_overlay"] = _music_audit_spine
        elif _music_audit_spine is not None:
            _spa_payload = {"musician_overlay": _music_audit_spine}
        if _spa_payload:
            (render_dir / "section_packet_audit.json").write_text(
                json.dumps(_spa_payload, indent=2, default=str, ensure_ascii=False),
                encoding="utf-8",
            )
        # Durable rendered-accent audit: merge composer-rendered rows with planner
        # assignments so every planned accent is visible even if a chapter path
        # skipped syn_meta persistence.
        _composer_rows = list((_governance_report or {}).get("accent_render_audit") or [])
        _composer_by_id = {
            str(r.get("accent_id") or ""): r
            for r in _composer_rows
            if r.get("accent_id")
        }
        _bodies_by_id = {}
        for _ch in enriched.chapters:
            for _aid, _body in dict(getattr(_ch, "accent_bodies", None) or {}).items():
                if _aid and _body:
                    _bodies_by_id[str(_aid)] = str(_body)
        _accent_render_rows = []
        _seen_ids = set()
        for _row in list((enriched.spine_context or {}).get("accent_assignments") or []):
            _aid = str(_row.get("accent_id") or "")
            _comp = _composer_by_id.get(_aid) or {}
            _body = _bodies_by_id.get(_aid) or ""
            _excerpt = str(
                _comp.get("rendered_excerpt")
                or _comp.get("body")
                or (_body[:220].replace("\n", " ").strip() if _body else "")
            )
            if not _excerpt and _body:
                _excerpt = _body[:220].replace("\n", " ").strip()
            _present = bool(_excerpt) and (
                _excerpt[:40] in prose
                or (_body[:40] in prose if _body else False)
                or any(
                    frag and frag in prose
                    for frag in (" ".join(_excerpt.split()[:6]),)
                )
            )
            _accent_render_rows.append(
                {
                    "chapter": _row.get("chapter") or _comp.get("chapter"),
                    "class": _row.get("class") or _comp.get("class"),
                    "accent_id": _aid,
                    "position": _row.get("position") or _comp.get("position"),
                    "provenance": (_row.get("keys") or {}).get("supply_provenance")
                    or _row.get("supply_source")
                    or _comp.get("provenance"),
                    "rendered_excerpt": _excerpt,
                    "present_in_manuscript": _present or bool(_comp.get("present_in_manuscript")),
                }
            )
            if _aid:
                _seen_ids.add(_aid)
        for _aid, _comp in _composer_by_id.items():
            if _aid in _seen_ids:
                continue
            _accent_render_rows.append(dict(_comp))
        (render_dir / "rendered_accent_audit.json").write_text(
            json.dumps(
                {
                    "contract_id": str(render_dir.name),
                    "topic_id": topic_id,
                    "persona_id": persona_id,
                    "accent_budget": dict((enriched.spine_context or {}).get("accent_budget") or {}),
                    "accent_signature": (enriched.spine_context or {}).get("accent_signature"),
                    "story_mix_profile": (enriched.spine_context or {}).get("story_mix_profile"),
                    "accents": _accent_render_rows,
                    "count": len(_accent_render_rows),
                },
                indent=2,
                default=str,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        _bq_fail, _bq_frag = _apply_book_quality_gate(
            render_dir=render_dir,
            prose=prose,
            runtime_format_id=runtime_fmt,
            gates_hard=_block_on_fail(quality_profile, "book_quality_gate"),
            governance_report=_governance_report,
            slot_sequences=None,
            frame=_frame,
            policy_override=bool(getattr(args, "book_quality_override", False)),
        )
        _quality_gate_failures.extend(_bq_fail)
        _quality_fail_set = set(_quality_gate_failures)
        _overall_status = "FAIL" if _quality_fail_set else (
            "WARN"
            if any(
                _st == "WARN"
                for _st in (
                    _chapter_flow_status,
                    _craft_status,
                    _ei_status,
                    _editorial_status,
                    _memorable_status,
                    _transform_status,
                    _book_pass_status,
                )
            )
            else "PASS"
        )
        _qs_path = render_dir / "quality_summary.json"
        _qs_payload = {
            "source": "spine_pipeline",
            "topic_id": topic_id,
            "persona_id": persona_id,
            "teacher_id": teacher_for_enrich or "",
            "runtime_format": runtime_fmt,
            "book_plan_id": book_plan.plan_id,
            "quality_profile": quality_profile,
            "gates_run": gates_run,
            "gates_hard": gates_hard,
            "gates": {
                "chapter_flow": {
                    "status": _chapter_flow_status,
                    "report": _chapter_flow_report_name,
                },
                "register_gate": {
                    "status": _register_status,
                    "verdict": _register_verdict,
                    "failure_counts_by_id": _register_f_counts,
                    "report": "register_gate_report.json",
                },
                "bestseller_craft": {
                    "status": _craft_status,
                    "overall_score": round(_craft_overall, 4),
                },
                "ei_v2": {
                    "status": _ei_status,
                    "composite": round(_ei_composite, 4),
                    "report": "ei_v2_report.json",
                },
                "editorial": {
                    "status": _editorial_status,
                    "report": "editorial_report.json",
                },
                "memorable_lines": {
                    "status": _memorable_status,
                    "chapters_with_two_or_more_quotable_lines": _memorable_quote_chapters,
                    "chapter_count": _memorable_total_chapters,
                    "report": "memorable_line_report.json",
                },
                "transformation_arc": {
                    "status": _transform_status,
                    "report": "transformation_heatmap.json",
                },
                "book_pass": {
                    "status": _book_pass_status,
                    "report": "book_pass_report.json",
                },
            },
            "quality_gate_failures": sorted(_quality_fail_set),
            "overall_status": _overall_status,
            "book_quality_gate": _bq_frag,
            "pre_depth_total_words": pre_depth_words,
            "post_depth_total_words": post_depth_words,
            "frame": _frame,
            "governance_report": _governance_report,
            "exercise_slots_dropped": _governance_report.get("exercise_slots_dropped", []),
            "chapter_contract_warnings": _governance_report.get("chapter_contract_warnings", []),
            "frame_governance_chapters": _governance_report.get("frame_governance_chapters", []),
            "frame_softened_sentences": _governance_report.get("frame_softened_sentences", []),
            "frame_stripped_sentences": _governance_report.get("frame_stripped_sentences", []),
            "frame_hard_fail_reasons": _governance_report.get("frame_hard_fail_reasons", []),
            "recurrence_report": _governance_report.get("recurrence_report", []),
        }
        _qs_path.write_text(json.dumps(_qs_payload, indent=2), encoding="utf-8")
        print(f"Quality summary: {_qs_path}")

    if args.generate_freebies and args.render_book:
        try:
            from phoenix_v4.freebies.freebie_renderer import generate_freebies_for_book

            _freebie_plan = {
                "plan_id": f"spine-{topic_id}-{seed}",
                "topic_id": topic_id,
                "persona_id": persona_id,
                "teacher_id": teacher_for_enrich or "",
                "freebie_slug": f"{topic_id}-{persona_id}",
                "word_count": word_count,
                "source": "spine_pipeline",
            }
            _formats_list = None
            if args.formats:
                _formats_list = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
            _publish_dir = Path(args.publish_dir) if args.publish_dir else None
            _asset_store = Path(args.asset_store) if args.asset_store else None
            _freebie_paths = generate_freebies_for_book(
                _freebie_plan,
                book_spec_for_compiler,
                include_pdf=bool(_formats_list and "pdf" in _formats_list),
                formats=_formats_list,
                skip_audio=args.skip_audio,
                publish_dir=_publish_dir,
                asset_store_root=_asset_store,
            )
            if _freebie_paths:
                print(
                    f"Generated freebie artifacts: {len(_freebie_paths)} file(s) under artifacts/freebies/"
                )
        except Exception as _e:
            print(f"Freebie generation failed (non-blocking): {_e}", file=sys.stderr)

    if _quality_gate_failures and (gates_hard or quality_profile == "flagship"):
        _profile_label = "flagship" if quality_profile == "flagship" else "production"
        print(
            f"BLOCKED: {len(_quality_gate_failures)} quality gate(s) failed in {_profile_label} mode: "
            f"{', '.join(_quality_gate_failures)}. "
            f"Use --skip-quality-gates or --quality-profile=draft to bypass.",
            file=sys.stderr,
        )
        return 1

    if not getattr(args, "no_job_check", False):
        from scripts.pipeline.advance_stage import mark_pipeline_finished

        mark_pipeline_finished(ebook_job_ws, "ebook")
    return 0


def _guard_legacy_registry_mode(args: argparse.Namespace) -> int | None:
    """Block registry fast-path for production-like book builds (COHESIVE-FLOW-PATH-DEFAULT-SPINE-01)."""
    if getattr(args, "pipeline_mode", "spine") != "registry":
        return None
    print(
        "WARNING: --pipeline-mode registry is LEGACY (section-registry fast-path). "
        "Pearl Prime production books MUST use spine (the default). "
        "See docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md.",
        file=sys.stderr,
    )
    production_like = args.quality_profile in ("production", "flagship")
    blocked = bool(getattr(args, "render_book", False)) and production_like
    if blocked and not getattr(args, "allow_legacy_registry", False):
        print(
            "Error: registry mode cannot render production books (--render-book with "
            "--quality-profile production|flagship). Use the default spine path or pass "
            "--allow-legacy-registry only for explicit legacy QA.",
            file=sys.stderr,
        )
        return 1
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="BookSpec -> FormatPlan -> CompiledBook")
    ap.add_argument("--topic", default=None, help="Topic ID (e.g. relationship_anxiety)")
    ap.add_argument("--persona", default=None, help="Persona ID (e.g. nyc_exec)")
    ap.add_argument(
        "--location",
        default=None,
        help="Location profile or alias for render/naming grounding (e.g. nyc_grand_central, nyc, 'New York City')",
    )
    ap.add_argument("--installment", type=int, default=None, help="Installment number")
    ap.add_argument("--series", default=None, help="Series ID")
    ap.add_argument(
        "--angle",
        type=str,
        default=None,
        help=(
            "Angle ID for this book (e.g. 'at_work', 'public_speaking'). "
            "If not supplied, angle is derived from topic + persona via series config. "
            "Required for deterministic naming engine output."
        ),
    )
    ap.add_argument("--seed", default="pipeline_seed_001", help="Determinism seed")
    ap.add_argument(
        "--chapter-architecture-version",
        type=int,
        default=None,
        choices=[1, 2],
        help="Holistic chapter architecture: 1=legacy slot-fill, 2=assemble-full-unit (OPD-129/113)",
    )
    ap.add_argument(
        "--runtime-format",
        default=None,
        help=(
            "Stage 2 runtime hint (e.g. standard_book). Under V4 freeze, only allowed with "
            "--pipeline-mode spine. Ignored for spine mode default (uses standard_book when omitted)."
        ),
    )
    ap.add_argument("--structural-format", default=None, help="Force Stage 2 structural format (e.g. F006 for 8-12 chapters)")
    ap.add_argument(
        "--output-format",
        default=None,
        help=(
            "Modular output format id (freeze mode). "
            "Examples: five_min_practice, pocket_guide, ten_things_to_do, symptom_to_action_atlas, "
            "daily_text_audio_companion, crisis_cards, weekly_challenge_pack, faq_audiobook, myth_vs_mechanism, protocol_library"
        ),
    )
    # --disable-v4-freeze REMOVED (2026-04-02).
    # V4 freeze is permanent. Pearl Prime (V4) only produces short therapeutic content.
    # Legacy long-form books (F001-F013, 1hr-6hr) are Pearl Prime legacy, not V4.
    # If you need legacy formats, use the legacy pipeline entry point, not run_pipeline.py.
    ap.add_argument("--input", default=None, help="YAML file with topic_id, persona_id, installment_number (Stage 2 input)")
    ap.add_argument("--arc", required=True, help="Path to Master Arc YAML (required; no arc = no compile)")
    ap.add_argument("--registry", default=None, help="Section registry YAML path (auto-detected from registry/{topic}.yaml if not supplied)")
    ap.add_argument(
        "--pipeline-mode",
        choices=["registry", "spine"],
        default="spine",
        help=(
            "Pipeline mode: 'spine' (default; canonical Pearl Prime path: "
            "spine→knob→beatmap→enrichment+depth→compose) or 'registry' "
            "(LEGACY section-registry fast-path — not for production book renders)."
        ),
    )
    ap.add_argument(
        "--allow-legacy-registry",
        action="store_true",
        help=(
            "Allow --pipeline-mode registry with --render-book under production/flagship "
            "quality profiles. For explicit legacy QA only; not for catalog output."
        ),
    )
    ap.add_argument(
        "--frame",
        choices=["somatic_first", "spiritual_first"],
        default="somatic_first",
        help="Frame governance for spine composition (default: somatic_first).",
    )
    ap.add_argument(
        "--golden-chapter-pilot",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Spine mode + --render-book only: after render, write golden_chapter_report.json "
            "and golden_chapter_N.txt for human chapter N (1-based) into --render-dir."
        ),
    )
    ap.add_argument("--teacher", default=None, help="Teacher id for Teacher Mode (validated against teacher_persona_matrix)")
    ap.add_argument("--author", default=None, help="Author id (pen-name; resolved from author_registry, sets author_positioning_profile)")
    ap.add_argument("--narrator", default=None, help="Narrator id (resolved from brand_narrator_assignments when not supplied; Writer Spec §23.5)")
    ap.add_argument("--out", default=None, help="Write CompiledBook JSON here")
    ap.add_argument("--generate-freebies", action="store_true", help="Generate HTML freebie artifacts (public/free/<slug>/)")
    ap.add_argument("--no-generate-freebies", action="store_true", help="Disable freebie HTML generation when writing plan (default: generate when --out)")
    ap.add_argument("--no-update-freebie-index", action="store_true", help="Do not upsert plan row into artifacts/freebies/index.jsonl (use for test runs; DoD freebies governance)")
    ap.add_argument("--formats", default=None, help="Comma-separated freebie formats: html,pdf,epub,mp3 (default: html, or html+pdf if store has assets)")
    ap.add_argument("--skip-audio", action="store_true", help="Do not include mp3 in freebie formats")
    ap.add_argument("--publish-dir", default=None, help="Copy freebies to this dir for public/free (e.g. public/free)")
    ap.add_argument("--asset-store", default=None, help="Asset store root to copy pre-created assets from (e.g. artifacts/freebie_assets/store)")
    ap.add_argument("--render-book", action="store_true", help="Stage 6: render plan to prose (txt) after writing plan")
    ap.add_argument("--render-formats", default="txt", help="Comma-separated book output formats (default: txt)")
    ap.add_argument("--render-dir", default=None, help="Output dir for rendered book (default: artifacts/rendered/<plan_id>)")
    ap.add_argument("--skip-word-count-gate", action="store_true", help="Bypass word count minimum gate (use when content density work is in progress)")
    ap.add_argument("--skip-budget-check", action="store_true", help="Skip pre-render word-budget sufficiency check (e.g. testing with sparse atom pools)")
    ap.add_argument(
        "--quality-profile",
        choices=["production", "draft", "debug", "flagship"],
        default="production",
        help=(
            "Quality gate enforcement level (default: production). "
            "production: all gates run; any failure exits 1. "
            "flagship: all gates run; only chapter_flow, book_quality_gate, and "
            "scene_anti_genericity_gate failures exit 1 (other gates stay advisory). "
            "draft: gates run but only warn (exit 0). "
            "debug: gates skipped entirely."
        ),
    )
    ap.add_argument(
        "--skip-quality-gates",
        action="store_true",
        help="Explicit opt-out from all quality gates regardless of --quality-profile (for CI dry-runs)",
    )
    ap.add_argument(
        "--enforce-book-pass-gate",
        action="store_true",
        help="Run book-pass quality gate (claim progression, non-shuffleability, ending transformation) and fail on errors. Redundant when --quality-profile=production (default).",
    )
    ap.add_argument(
        "--book-quality-override",
        action="store_true",
        help="Allow book_quality_gate runtime_policy default_reject (micro_book_15/20) to pass when gates would otherwise reject on policy alone.",
    )
    ap.add_argument(
        "--ei-v2-compare",
        action="store_true",
        help="Run EI V2 AI techniques in parallel with V1 and produce comparison report (artifacts/ei_v2/)",
    )
    ap.add_argument(
        "--enforce-scene-gate",
        action="store_true",
        help="Run scene anti-genericity gate after render (§8 overlay spec: three-detail rule, collision scan, action-state test, location repetition)",
    )
    ap.add_argument(
        "--scene-gate-mode",
        choices=["production", "draft"],
        default="production",
        help="Scene gate mode: production (blocking) or draft (warn only). Default: production.",
    )
    ap.add_argument("--locale", default=None,
                    help="Locale for book (e.g. zh-TW, ja-JP). Loads locale-specific atoms. Default: from brand config or en-US")
    ap.add_argument("--atoms-root", default=None, help="Atoms root (e.g. atoms/zh-TW). Default: repo atoms/")
    ap.add_argument(
        "--atoms-model",
        choices=["legacy", "cluster"],
        default=None,
        help="Atoms model: legacy (persona-specific) or cluster (core+overlay). Precedence: CLI > spec > config (legacy_personas).",
    )
    ap.add_argument(
        "--workspace",
        default=None,
        help="Directory containing job.json for unified pipeline job enforcement (see scripts/pipeline/).",
    )
    ap.add_argument(
        "--no-job-check",
        dest="no_job_check",
        action="store_true",
        help="Skip job.json enforcement (CI / emergency only).",
    )
    # --additive-enrichment removed in PR #612: additive stacking is the only mode.
    ap.add_argument(
        "--exercise-journeys",
        action="store_true",
        help="Attach thesis-aligned exercise journeys to EXERCISE slots after depth pass.",
    )
    ap.add_argument(
        "--music-mode",
        choices=["none", "with-lyrics", "no-lyrics"],
        default="none",
        help="Pearl Prime music overlay (additive; orthogonal to --pipeline-mode). Default: none.",
    )
    ap.add_argument(
        "--musician-id",
        default=None,
        help="Musician bank id under SOURCE_OF_TRUTH/musician_banks/ (required when --music-mode is not none).",
    )
    args = ap.parse_args()

    _registry_guard = _guard_legacy_registry_mode(args)
    if _registry_guard is not None:
        return _registry_guard

    if getattr(args, "music_mode", "none") != "none":
        if not (getattr(args, "musician_id", None) or "").strip():
            print("--musician-id is required when --music-mode is not none", file=sys.stderr)
            return 1

    if getattr(args, "no_job_check", False):
        print(
            "WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).",
            file=sys.stderr,
        )

    # --- Quality profile resolution ---
    # --skip-quality-gates forces debug (no gates). --enforce-book-pass-gate implies at
    # least the book-pass portion even in draft/debug, but production already includes it.
    #
    # Profile semantics:
    #   production: gates_run=True; every gate failure exits 1.
    #   flagship:   gates_run=True; only chapter_flow, book_quality_gate, and
    #               scene_anti_genericity_gate failures exit 1. Other gates are advisory.
    #   draft:      gates_run=True; failures only warn (exit 0).
    #   debug:      gates skipped entirely.
    quality_profile = args.quality_profile  # production | flagship | draft | debug
    if args.skip_quality_gates:
        quality_profile = "debug"
    gates_run = quality_profile in ("production", "flagship", "draft")
    gates_hard = quality_profile == "production"
    flagship_mode = quality_profile == "flagship"

    # V4 freeze settings: restrict pipeline outputs to modular formats unless explicitly disabled.
    from pearl_prime.modular_format_freeze import (
        apply_output_format_to_plan,
        load_freeze_settings,
        require_valid_output_format,
    )
    freeze_settings = load_freeze_settings()
    freeze_enabled = bool(freeze_settings.enabled)  # V4 freeze is permanent — no bypass
    _pipeline_mode = getattr(args, "pipeline_mode", "spine")
    _mode_policy_rc = _enforce_pipeline_mode_policy(args, quality_profile)
    if _mode_policy_rc is not None:
        return _mode_policy_rc

    if freeze_enabled and args.structural_format:
        print(
            "Error: --structural-format is blocked under V4 freeze. "
            "Pearl Prime V4 only produces short therapeutic content. "
            "Use --output-format with: " + ", ".join(sorted(freeze_settings.formats.keys())),
            file=sys.stderr,
        )
        return 1

    if freeze_enabled and args.runtime_format and _pipeline_mode != "spine":
        print(
            "Error: --runtime-format is blocked under V4 freeze for registry/atom paths. "
            "Pearl Prime V4 only produces short therapeutic content. "
            "Use --output-format with: " + ", ".join(sorted(freeze_settings.formats.keys()))
            + ". For long-form spine→beatmap→enrichment, use --pipeline-mode spine (optional --runtime-format).",
            file=sys.stderr,
        )
        return 1

    # Resolve input: CLI or YAML
    topic_id = args.topic
    persona_id = args.persona
    installment_number = args.installment
    series_id = args.series
    angle_id = args.angle
    requested_location_id = args.location
    resolved_location_id = None
    seed = args.seed
    input_atoms_model = None  # from --input YAML when present
    if args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"Error: input file not found: {p}", file=sys.stderr)
            return 1
        data = yaml.safe_load(p.read_text()) if yaml else {}
        topic_id = topic_id or data.get("topic_id", "relationship_anxiety")
        persona_id = persona_id or data.get("persona_id", "nyc_exec")
        installment_number = installment_number if installment_number is not None else data.get("installment_number", 1)
        series_id = series_id if series_id is not None else data.get("series_id")
        if angle_id is None:
            angle_id = data.get("angle_id")
        requested_location_id = requested_location_id or data.get("location_id") or data.get("requested_location_id")
        resolved_location_id = data.get("resolved_location_id") or resolved_location_id
        seed = data.get("seed", seed)
        if data.get("atoms_model") in ("legacy", "cluster"):
            input_atoms_model = data["atoms_model"]

    if not topic_id or not persona_id:
        print("Error: need --topic and --persona (or --input YAML with topic_id, persona_id)", file=sys.stderr)
        return 1

    arc_path = Path(args.arc)
    # Angle Integration (V4.7): resolve arc path from angle when angle_id in registry with arc_path
    if angle_id:
        from phoenix_v4.planning.angle_resolver import resolve_arc_path as angle_resolve_arc_path
        arc_path = angle_resolve_arc_path(angle_id, arc_path, repo_root=REPO_ROOT)
    if not arc_path.exists():
        print(f"Error: arc file not found: {arc_path}", file=sys.stderr)
        return 1

    ebook_job_ws = (
        Path(args.workspace).resolve()
        if getattr(args, "workspace", None)
        else (Path(args.out).resolve().parent if args.out else Path.cwd())
    )
    if not getattr(args, "no_job_check", False):
        from scripts.pipeline.check_job import require_stage

        require_stage("preflight", ebook_job_ws)

    # Load arc early so we can align format plan to arc chapter_count (Arc-First)
    from phoenix_v4.planning.arc_loader import load_arc
    arc = load_arc(arc_path)

    requested_teacher = (args.teacher or "").strip() or None
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand
    _, resolved_brand = resolve_teacher_brand(
        topic_id=topic_id,
        persona_id=persona_id,
        series_id=series_id,
    )
    teacher_id = requested_teacher or "default_teacher"
    brand_id = resolved_brand
    # Teacher Mode: an explicit --teacher routes to that teacher's home brand (brand follows teacher),
    # so e.g. --teacher sai_ma -> devotion_path (imprint "Open Vessel Press", author "Sai Maa") instead
    # of the topic/persona default. 1-teacher-per-brand per teacher_brand_lane_assignments.yaml.
    if requested_teacher:
        from phoenix_v4.planning.teacher_brand_resolver import resolve_brand_for_teacher
        _home_brand = resolve_brand_for_teacher(requested_teacher)
        if _home_brand:
            brand_id = _home_brand
    if teacher_id and teacher_id != "default_teacher":
        from phoenix_v4.planning.teacher_matrix import load_teacher_matrix, validate_teacher_assignment
        matrix = load_teacher_matrix()
        if matrix:
            try:
                validate_teacher_assignment(
                    matrix=matrix,
                    teacher_id=teacher_id,
                    persona_id=persona_id,
                    engine_id=getattr(arc, "engine", None),
                    locale_key=None,
                )
            except ValueError as e:
                print(f"Teacher assignment invalid: {e}", file=sys.stderr)
                return 1

    # Resolve author from brand when --author not supplied (brand_author_assignments.yaml)
    author_id = (args.author or "").strip() or None
    if author_id is None:
        from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
        author_id = resolve_author_from_brand(
            brand_id=brand_id,
            topic_id=topic_id,
            persona_id=persona_id,
            series_id=series_id,
        )

    # Resolve narrator from brand when --narrator not supplied (brand_narrator_assignments.yaml)
    narrator_id = (args.narrator or "").strip() or None
    if narrator_id is None:
        from phoenix_v4.planning.narrator_brand_resolver import resolve_narrator_from_brand
        narrator_id = resolve_narrator_from_brand(brand_id=brand_id)
    if narrator_id:
        from phoenix_v4.planning.narrator_brand_resolver import validate_narrator_for_book
        ok, err = validate_narrator_for_book(narrator_id, brand_id, topic_id=topic_id)
        if not ok:
            print(f"Error: narrator validation failed: {err}", file=sys.stderr)
            return 1

    # Tuple viability preflight (hard entry gate; before Stage 1). No override.
    from phoenix_v4.gates.check_tuple_viability import check_tuple_viability
    teacher_mode = bool(teacher_id and teacher_id != "default_teacher")
    viability = check_tuple_viability(
        persona=arc.persona,
        topic=arc.topic,
        engine=arc.engine,
        format_id=arc.format,
        repo_root=REPO_ROOT,
        teacher_mode=teacher_mode,
        teacher_id=teacher_id if teacher_mode else None,
        arc=arc,
        brand_id=brand_id,
    )
    if viability.status != "PASS":
        for e in viability.errors:
            print(f"Tuple viability: {e}", file=sys.stderr)
        return 1

    # Stage 1: BookSpec (author_id, narrator_id optional)
    from phoenix_v4.planning.catalog_planner import (
        AtomsModel,
        CatalogPlanner,
        BookSpec,
        load_render_location_profiles,
    )
    planner = CatalogPlanner()
    teacher_mode = bool(teacher_id and teacher_id != "default_teacher")
    spec_atoms_model = AtomsModel(input_atoms_model) if input_atoms_model in ("legacy", "cluster") else None
    book_spec = planner.produce_single(
        topic_id=topic_id,
        persona_id=persona_id,
        teacher_id=teacher_id,
        brand_id=brand_id,
        seed=seed,
        series_id=series_id,
        installment_number=installment_number,
        angle_id=angle_id,
        requested_location_id=requested_location_id,
        resolved_location_id=resolved_location_id,
        author_id=author_id,
        narrator_id=narrator_id,
        teacher_mode=teacher_mode,
        atoms_model=spec_atoms_model,
        locale=args.locale,
    )

    if book_spec.angle_id.endswith("_general"):
        import warnings
        warnings.warn(
            f"angle_id resolved to fallback '{book_spec.angle_id}' for "
            f"topic='{topic_id}', persona='{persona_id}'. "
            f"Naming engine will produce a less-specific title. "
            f"Pass --series <id> or --angle <id> for a precise angle.",
            UserWarning,
            stacklevel=2,
        )

    # Stage 2: FormatPlan
    from phoenix_v4.planning.format_selector import FormatSelector
    selector = FormatSelector()
    constraints = {}
    # Spine mode applies --runtime-format only in knob/beatmap (not Stage 2), so forcing
    # it here breaks FormatSelector validation against the arc's structural format.
    if args.runtime_format and getattr(args, "pipeline_mode", "spine") != "spine":
        constraints["force_runtime_format"] = args.runtime_format
    if args.structural_format:
        constraints["force_structural_format"] = args.structural_format
    format_plan = selector.select_format(
        topic_id=topic_id,
        persona_id=persona_id,
        installment_number=installment_number,
        series_id=series_id,
        constraints=constraints or None,
    )

    # Resolve aliases before Stage 3 (Canonical §3.0). Stage 3 only sees canonical IDs.
    canonical_topic, canonical_persona = resolve_to_canonical(
        ALIASES_PATH,
        topic_id,
        persona_id,
        repo_root=REPO_ROOT,
        arc_topic=getattr(arc, "topic", None),
    )
    book_spec_for_compiler = {**book_spec.to_dict(), "topic_id": canonical_topic, "persona_id": canonical_persona}
    # F-COHERENCE: surface the arc's bound engine so the spine path can route atoms by
    # (topic, engine). Explicit so it holds regardless of BookSpec.to_dict() contents.
    book_spec_for_compiler["engine"] = getattr(arc, "engine", "") or book_spec_for_compiler.get("engine", "")
    _book_idea, _book_motif = _resolve_book_idea_and_motif(book_spec=book_spec_for_compiler, arc=arc)
    book_spec_for_compiler["book_idea"] = _book_idea
    book_spec_for_compiler["book_motif"] = _book_motif
    if getattr(args, "chapter_architecture_version", None) is not None:
        book_spec_for_compiler["chapter_architecture_version"] = int(args.chapter_architecture_version)

    alias_data = _load_yaml(ALIASES_PATH)
    topic_alias_target = (alias_data.get("topic_aliases") or {}).get(topic_id, topic_id)
    explicit_topic_preserved = topic_alias_target != topic_id and canonical_topic == topic_id
    if explicit_topic_preserved:
        source_issues = _topic_source_readiness_issues(
            persona_id=canonical_persona,
            topic_id=canonical_topic,
            engine_id=getattr(arc, "engine", ""),
            atoms_root=ATOMS_ROOT,
        )
        if source_issues:
            print(
                f"Topic source readiness failed for requested topic '{topic_id}'. "
                "The pipeline preserved the explicit topic instead of collapsing it to a broader alias, "
                "but the dedicated source bank is not ready for compile:",
                file=sys.stderr,
            )
            for issue in source_issues:
                print(f"  - {issue}", file=sys.stderr)
            return 1

    # §5G Output Contract: build initial contract after alias resolution
    from phoenix_v4.planning.output_contract import build_output_contract, update_contract_post_render
    _oc_resolved_config = {
        "canonical_topic_id": canonical_topic,
        "canonical_persona_id": canonical_persona,
        "resolved_location_id": resolved_location_id or "",
        "teacher_mode": teacher_mode,
        "teacher_id": teacher_id,
        "quality_profile": "production",
        "runtime_format": args.runtime_format or "",
        "structural_format": args.structural_format or "",
    }
    _output_contract = build_output_contract(args, _oc_resolved_config)

    # atoms_model: precedence 1) CLI --atoms-model 2) book spec 3) derive from config (legacy_personas). Always persist in plan.
    if args.atoms_model is not None:
        effective_atoms_model = args.atoms_model
    elif book_spec.atoms_model is not None:
        effective_atoms_model = book_spec.atoms_model.value
    else:
        from phoenix_v4.planning.atoms_model_loader import atoms_model_for_persona
        effective_atoms_model = atoms_model_for_persona(persona_id).value
        print(f"Warning: atoms_model missing in spec; derived from config (legacy_personas) -> {effective_atoms_model}", file=sys.stderr)
    book_spec_for_compiler["atoms_model"] = effective_atoms_model

    # atoms_root: default None (repo atoms/). Cluster future-guard: when atoms_model=cluster and unset, warn and set default.
    atoms_root = Path(args.atoms_root) if args.atoms_root else None
    if effective_atoms_model == "cluster" and atoms_root is None:
        atoms_root = REPO_ROOT / "atoms"
        print(
            "Warning: atoms_model=cluster but atoms_root not set; using repo atoms/ — cluster layout (core/ + overlay/) required when implemented",
            file=sys.stderr,
        )

    # Author assets (Writer Spec §23.3, §23.9): load when author_id set; fail if any required asset missing.
    author_assets = None
    if book_spec_for_compiler.get("author_id"):
        from phoenix_v4.planning.author_asset_loader import load_author_assets
        author_assets = load_author_assets(book_spec_for_compiler["author_id"], repo_root=REPO_ROOT)
        if author_assets.get("errors"):
            print("Error: author assets missing or invalid (Writer Spec §23.9):", file=sys.stderr)
            for e in author_assets["errors"]:
                print(f"  - {e}", file=sys.stderr)
            return 1
        # Attach for downstream (templates, audiobook pre-intro, etc.); omit internal 'errors' in payload
        book_spec_for_compiler["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}

        # Controlled Intro/Conclusion Variation: resolve pre-intro from pattern banks when enabled
        intro_ending_cfg = {}
        try:
            from phoenix_v4.planning.intro_ending_caps import load_intro_ending_config
            intro_ending_cfg = load_intro_ending_config()
        except Exception:
            pass
        if intro_ending_cfg.get("intro_ending_variation_enabled"):
            from phoenix_v4.planning.pre_intro_resolver import (
                resolve_pre_intro_blocks,
                compute_pre_intro_signature,
                PRE_INTRO_BLOCK_ORDER,
            )
            from phoenix_v4.planning.author_asset_loader import render_audiobook_pre_intro
            from phoenix_v4.qa.validate_pre_intro import validate_pre_intro
            from phoenix_v4.planning.intro_ending_caps import (
                get_quarter_for_brand,
                load_signature_index,
                check_intro_cap_and_duplicate,
            )
            config_sot = REPO_ROOT / "config" / "source_of_truth"
            pattern_bank_overrides_yaml = bool(intro_ending_cfg.get("pattern_bank_overrides_yaml"))
            max_retries = int(intro_ending_cfg.get("max_retries", 5))
            cap_share = float(intro_ending_cfg.get("intro_signature_cap_share", 0.15))
            selector_key = f"{canonical_topic}|{canonical_persona}|{seed}"
            series_id = book_spec_for_compiler.get("series_id")
            include_series_line = bool(series_id)
            book_title_runtime = ""  # TODO: from naming engine when available
            series_name_runtime = ""
            signature_index_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
            signature_index = load_signature_index(signature_index_path)
            quarter = get_quarter_for_brand(brand_id)
            last_cap_result = None
            resolved_blocks = None
            pre_intro_sig = None
            for retry in range(max_retries):
                sk = selector_key if retry == 0 else f"{selector_key}:retry{retry}"
                try:
                    resolved_blocks = resolve_pre_intro_blocks(
                        author_assets,
                        brand_id,
                        sk,
                        book_title=book_title_runtime,
                        series_name=series_name_runtime,
                        include_series_line=include_series_line,
                        pattern_bank_overrides_yaml=pattern_bank_overrides_yaml,
                        config_root=config_sot,
                    )
                except ValueError as e:
                    print(f"Pre-intro resolution failed: {e}", file=sys.stderr)
                    return 1
                # Merge stable blocks from original so required blocks present
                yaml_blocks = author_assets.get("audiobook_pre_intro") or {}
                for k in ("author_intro", "author_background"):
                    if yaml_blocks.get(k) and not resolved_blocks.get(k):
                        resolved_blocks[k] = yaml_blocks[k]
                val = validate_pre_intro(resolved_blocks, book_spec_for_compiler.get("author_id"))
                if not val.valid:
                    for err in val.errors:
                        print(f"Pre-intro validation failed: {err}", file=sys.stderr)
                    return 1
                full_text = render_audiobook_pre_intro(
                    author_assets,
                    book_title=book_title_runtime,
                    series_name=series_name_runtime,
                    include_series_line=include_series_line,
                    resolved_blocks=resolved_blocks,
                )
                pre_intro_sig = compute_pre_intro_signature(full_text)
                last_cap_result = check_intro_cap_and_duplicate(
                    brand_id, quarter, pre_intro_sig, signature_index, cap_share=cap_share,
                )
                if last_cap_result.ok:
                    break
            if not last_cap_result.ok:
                print(f"Pre-intro cap/duplicate gate failed after {max_retries} retries: {last_cap_result.error}", file=sys.stderr)
                if last_cap_result.candidate_alternatives:
                    for alt in last_cap_result.candidate_alternatives:
                        print(f"  Alternative: {alt}", file=sys.stderr)
                return 1
            # Replace author_assets audiobook_pre_intro with resolved and attach signature for plan output
            author_assets = {**author_assets, "audiobook_pre_intro": resolved_blocks}
            book_spec_for_compiler["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}
            book_spec_for_compiler["_pre_intro_signature"] = pre_intro_sig
            # Opening chapter recognition style (soft bias for chapter 0)
            from phoenix_v4.planning.intro_ending_selector import (
                select_opening_style_id,
                select_integration_ending_style_id,
                select_carry_line_style_id,
            )
            book_spec_for_compiler["opening_style_id"] = select_opening_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["integration_ending_style_id"] = select_integration_ending_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["carry_line_style_id"] = select_carry_line_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["seed"] = seed

    format_plan_dict = format_plan.to_compiler_input()

    # V4 freeze: apply modular output format before variation/compile wiring.
    if freeze_enabled:
        selected_output_format = (args.output_format or freeze_settings.default_output_format or "").strip()
        try:
            require_valid_output_format(selected_output_format, freeze_settings)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        format_plan_dict = apply_output_format_to_plan(
            format_plan_dict,
            output_format_id=selected_output_format,
            chapter_count=arc.chapter_count,
            settings=freeze_settings,
        )

    # Structural Variation V4: select variation knobs (deterministic, anti-cluster) — before Stage 3 so compiler can use them
    variation_knobs = {}
    try:
        from phoenix_v4.planning.variation_selector import select_variation_knobs
        wave_index_for_variation = []
        index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
        if index_path.exists():
            for ln in index_path.read_text(encoding="utf-8").strip().splitlines():
                if ln.strip():
                    try:
                        wave_index_for_variation.append(json.loads(ln))
                    except json.JSONDecodeError:
                        pass
        variation_knobs = select_variation_knobs(
            topic_id=canonical_topic,
            persona_id=canonical_persona,
            chapter_count=arc.chapter_count,
            seed=seed,
            angle_id=book_spec_for_compiler.get("angle_id") or "",
            arc_id=getattr(arc, "arc_id", "") or "",
            installment_number=installment_number,
            wave_index=wave_index_for_variation or None,
        )
    except Exception as e:
        import warnings
        warnings.warn(f"Variation knobs selection failed, using defaults: {e}", stacklevel=2)
        from phoenix_v4.planning.schema_v4 import VARIATION_DEFAULTS, apply_variation_defaults, get_plan_variation_signature
        base = {"chapter_slot_sequence": []}
        applied = apply_variation_defaults(base, arc.chapter_count)
        variation_knobs = {
            "book_structure_id": applied["book_structure_id"],
            "journey_shape_id": applied["journey_shape_id"],
            "motif_id": applied["motif_id"],
            "section_reorder_mode": applied["section_reorder_mode"],
            "reframe_profile_id": applied["reframe_profile_id"],
            "chapter_archetypes": applied["chapter_archetypes"],
            "variation_signature": get_plan_variation_signature({**applied, "topic_id": canonical_topic, "persona_id": canonical_persona, "angle_id": book_spec_for_compiler.get("angle_id"), "arc_id": getattr(arc, "arc_id", "")}),
        }

    # Pass variation knobs into format_plan for Stage 3 (section reorder, motif/reframe injection)
    format_plan_dict["section_reorder_mode"] = variation_knobs.get("section_reorder_mode", "none")
    format_plan_dict["motif_id"] = variation_knobs.get("motif_id") or ""
    format_plan_dict["reframe_profile_id"] = variation_knobs.get("reframe_profile_id") or "balanced"

    # Arc-First: align format plan chapter_count and slot_definitions to arc
    if format_plan_dict.get("chapter_count") != arc.chapter_count:
        format_plan_dict["chapter_count"] = arc.chapter_count
        slot_defs = format_plan_dict.get("slot_definitions") or []
        if len(slot_defs) == 1:
            template = list(slot_defs[0])
            format_plan_dict["slot_definitions"] = [template[:] for _ in range(arc.chapter_count)]
        elif len(slot_defs) > arc.chapter_count:
            format_plan_dict["slot_definitions"] = slot_defs[: arc.chapter_count]
        else:
            template = list(slot_defs[-1]) if slot_defs else []
            extra = [template[:] for _ in range(arc.chapter_count - len(slot_defs))]
            format_plan_dict["slot_definitions"] = list(slot_defs) + extra
    # Ensure book_size stays coherent after any chapter_count alignment.
    ch_count_for_size = int(format_plan_dict.get("chapter_count") or arc.chapter_count or 0)
    format_plan_dict["book_size"] = "short" if ch_count_for_size <= 6 else ("medium" if ch_count_for_size <= 10 else "long")

    # Part 3.1 capability check (before Stage 3)
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.capability_check import capability_check
    pool_index = PoolIndex()
    cap_result = capability_check(
        book_spec_for_compiler,
        format_plan_dict,
        pool_index,
        mode="relaxed",
    )
    if not cap_result.ok:
        for e in cap_result.errors:
            print(f"Capability check failed: {e}", file=sys.stderr)
        for d in cap_result.diagnostics:
            print(d, file=sys.stderr)
        return 1
    if cap_result.achievable_chapters < (format_plan_dict.get("chapter_count") or 12):
        # Optionally reduce chapter count and re-slice slot_definitions (not done here; just warn)
        print(f"Note: achievable_chapters={cap_result.achievable_chapters}", file=sys.stderr)

    # DEV SPEC 3: Arc/format role-slot compatibility
    from phoenix_v4.planning.arc_loader import validate_arc_format_role_compat
    role_compat_errors = validate_arc_format_role_compat(arc, format_plan_dict)
    if role_compat_errors:
        for e in role_compat_errors:
            print(f"Arc/format role compatibility: {e}", file=sys.stderr)
        return 1

    # Teacher Mode: pre-compile coverage gate (after arc + format expanded, before compile)
    skip_gates = getattr(args, 'skip_quality_gates', False)
    if book_spec_for_compiler.get("teacher_mode"):
        from phoenix_v4.teacher.coverage_gate import run_coverage_gate, TeacherCoverageError
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        artifacts_dir = REPO_ROOT / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        _tid = (book_spec_for_compiler.get("teacher_id") or "").strip()
        _tcfg = load_teacher_config(_tid) if _tid else {}
        teacher_exercise_fallback = bool(_tcfg.get("teacher_exercise_fallback"))
        teacher_story_fallback = bool(_tcfg.get("teacher_story_fallback", True))  # Default True: all teachers can use persona STORY fallback
        passed, gap_report = run_coverage_gate(
            book_spec_for_compiler,
            format_plan_dict,
            arc,
            teacher_exercise_fallback=teacher_exercise_fallback,
            artifacts_dir=artifacts_dir,
        )
        if not passed and gap_report is not None:
            import json as _json_cov
            (artifacts_dir / "teacher_coverage_report.json").write_text(
                _json_cov.dumps(gap_report, indent=2), encoding="utf-8"
            )
            # Pre-compile coverage is structural (TEACHER_MODE_INVARIANTS §9), not a
            # post-render quality gate. --skip-quality-gates must NOT bypass it.
            print("Teacher coverage gate failed. See artifacts/teacher_coverage_report.json", file=sys.stderr)
            raise TeacherCoverageError(
                "Teacher coverage insufficient for required slots. See artifacts/teacher_coverage_report.json"
            )

    # ── SECTION REGISTRY PATH (legacy fast-path; not production) ───
    # If a section registry exists for this topic, use it instead of atom assembly.
    # The registry provides 12 chapters × 10 sections × 5 variants of pre-authored prose.
    # Teacher atoms overlay TEACHER_DOCTRINE sections when teacher_id is set.
    from phoenix_v4.planning.registry_resolver import load_registry, resolve_book as registry_resolve_book, available_registries, REGISTRY_ROOT

    registry_path = getattr(args, "registry", None)
    topic_id = book_spec_for_compiler.get("topic_id", "")
    use_registry = False

    if registry_path:
        use_registry = True
    elif topic_id in available_registries():
        registry_path = str(REGISTRY_ROOT / f"{topic_id}.yaml")
        use_registry = True

    if getattr(args, "pipeline_mode", "spine") == "spine":
        return _run_spine_pipeline_mode(
            args=args,
            book_spec_for_compiler=book_spec_for_compiler,
            quality_profile=quality_profile,
            gates_run=gates_run,
            gates_hard=gates_hard,
            ebook_job_ws=ebook_job_ws,
            repo_root=REPO_ROOT,
        )

    if use_registry:
        print(f"Using section registry: {registry_path}")
        reg_data = load_registry(topic_id, Path(registry_path) if registry_path else None)
        teacher_id_for_reg = book_spec_for_compiler.get("teacher_id", "")
        seed = f"{topic_id}:{book_spec_for_compiler.get('persona_id', '')}:{book_spec_for_compiler.get('installment_number', 1)}"

        resolved_book = registry_resolve_book(
            reg_data,
            seed=seed,
            teacher_id=teacher_id_for_reg or None,
            persona_id=book_spec_for_compiler.get("persona_id"),
            locale=book_spec_for_compiler.get("locale") or getattr(args, "locale", None),
        )

        _reg_runtime = _resolved_runtime_format_id(args, format_plan_dict)
        _reg_format_id = (
            format_plan_dict.get("format_structural_id")
            or format_plan_dict.get("format_id")
            or ""
        )

        # Render to prose directly (skip atom assembly, skip Stage 3 compile)
        prose = resolved_book.to_prose()

        # Apply location variable rotation + delivery cleanup
        from phoenix_v4.rendering.book_renderer import clean_for_delivery

        _reg_plan_for_clean = {"runtime_format_id": _reg_runtime} if _reg_runtime else None
        prose = clean_for_delivery(prose, plan=_reg_plan_for_clean)

        # Write output
        if args.out:
            plan_out = {
                "plan_id": f"registry-{topic_id}-{seed}",
                "topic_id": topic_id,
                "persona_id": book_spec_for_compiler.get("persona_id", ""),
                "teacher_id": teacher_id_for_reg,
                "registry_path": registry_path,
                "chapter_count": resolved_book.chapter_count,
                "word_count": resolved_book.word_count,
                "seed": seed,
                "source": "section_registry",
                "format_id": _reg_format_id,
                "runtime_format_id": _reg_runtime,
            }
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(plan_out, indent=2, ensure_ascii=False))
            print(f"Wrote {args.out}")

        if args.render_book:
            render_dir = Path(args.render_dir) if args.render_dir else Path("artifacts/rendered") / f"registry-{topic_id}"
            render_dir.mkdir(parents=True, exist_ok=True)
            book_path = render_dir / "book.txt"
            _prose_reg_out = prose
            _music_mode_reg = getattr(args, "music_mode", "none") or "none"
            _musician_id_reg = (getattr(args, "musician_id", None) or "").strip()
            if _music_mode_reg != "none" and _musician_id_reg:
                from phoenix_v4.rendering.music_manuscript_overlay import apply_music_overlay_to_manuscript

                _prose_reg_out, _music_audit_reg = apply_music_overlay_to_manuscript(
                    prose,
                    repo_root=REPO_ROOT,
                    music_mode=_music_mode_reg,
                    musician_id=_musician_id_reg,
                    persona_id=str(book_spec_for_compiler.get("persona_id") or ""),
                    topic_id=str(topic_id or ""),
                    book_seed=str(seed),
                )
                (render_dir / "music_overlay_audit.json").write_text(
                    json.dumps(_music_audit_reg, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            book_path.write_text(_prose_reg_out, encoding="utf-8")
            print(f"Rendered book (txt): {book_path}")

            # Budget report (word_count matches delivered prose; enables word_count_gate)
            _wc_prose = len(_prose_reg_out.split())
            budget_path = render_dir / "budget.json"
            budget_payload: dict = {
                "word_count": _wc_prose,
                "runtime_format_id": _reg_runtime,
                "format_id": _reg_format_id,
                "chapter_count": resolved_book.chapter_count,
                "chapters": [
                    {
                        "chapter": ch.chapter_index + 1,
                        "title": ch.title,
                        "words": ch.word_count,
                    }
                    for ch in resolved_book.chapters
                ],
            }
            budget_path.write_text(json.dumps(budget_payload, indent=2))
            print(f"Rendered book (budget): {budget_path}")

            if not args.skip_word_count_gate and _reg_runtime:
                try:
                    from phoenix_v4.rendering.book_renderer import WordCountGateError, word_count_gate

                    gate_metrics = word_count_gate(_prose_reg_out, _reg_runtime, source_hint=str(book_path))
                    refresh = json.loads(budget_path.read_text(encoding="utf-8"))
                    refresh["gate_result"] = gate_metrics
                    budget_path.write_text(json.dumps(refresh, indent=2))
                except WordCountGateError as wc_exc:
                    print(str(wc_exc), file=sys.stderr)
                    return 1

            # Output contract
            contract_path = render_dir / "output_contract.json"
            contract_path.write_text(json.dumps({
                "source": "section_registry",
                "registry_path": registry_path,
                "topic_id": topic_id,
                "teacher_id": teacher_id_for_reg,
                "word_count": _wc_prose,
                "chapter_count": resolved_book.chapter_count,
                "runtime_format_id": _reg_runtime,
                "format_id": _reg_format_id,
            }, indent=2))
            print(f"Output contract: {contract_path}")

            # ── REGISTRY QUALITY GATES ──────────────────────────────────────
            # NOTE: book_pass_gate is SKIPPED — it requires atom metadata
            # (atom_ids, chapter_slot_sequence, dominant_band_sequence) that
            # only the atom-assembly path produces.
            _quality_gate_failures: list[str] = []

            # 1. Chapter flow gate
            if gates_run:
                try:
                    from phoenix_v4.rendering.book_renderer import chapter_flow_gate_report
                    _flow_report = chapter_flow_gate_report(
                        _prose_reg_out, runtime_format_id=_reg_runtime or None
                    )
                    _flow_report_path = render_dir / "chapter_flow_report.json"
                    _flow_report_path.write_text(
                        json.dumps(_flow_report, indent=2), encoding="utf-8"
                    )
                    print(
                        f"Chapter flow gate: {_flow_report['status']} "
                        f"({_flow_report['failed_chapters']}/{_flow_report['chapter_count']} failed). "
                        f"Report: {_flow_report_path}",
                        file=sys.stderr,
                    )
                    if _flow_report["status"] != "PASS":
                        for _ch in _flow_report.get("chapters", []):
                            if _ch.get("status") != "PASS":
                                print(
                                    f"  Ch {_ch['chapter']}: {', '.join(_ch.get('errors', []))}",
                                    file=sys.stderr,
                                )
                        if _block_on_fail(quality_profile, "chapter_flow"):
                            _quality_gate_failures.append("chapter_flow")
                except Exception as _e:
                    print(f"Chapter flow gate error (non-blocking): {_e}", file=sys.stderr)

            # 2. Bestseller craft gate (ONTGP scoring — advisory only, never blocks)
            if gates_run:
                try:
                    from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft
                    _chapters_for_craft = _extract_registry_chapters(_prose_reg_out)
                    _craft_results = []
                    for _i, _ch_text in enumerate(_chapters_for_craft):
                        _craft = evaluate_bestseller_craft(_ch_text)
                        _craft_results.append({
                            "chapter": _i + 1,
                            "status": _craft.status,
                            "move_scores": _craft.move_scores,
                            "issues": _craft.issues,
                            "remediation": _craft.remediation,
                            "metrics": _craft.metrics,
                        })
                    _per_ch_means = []
                    for _cr in _craft_results:
                        _scores = _cr.get("move_scores", {})
                        if _scores:
                            _per_ch_means.append(sum(_scores.values()) / len(_scores))
                    _overall_craft = (
                        sum(_per_ch_means) / len(_per_ch_means) if _per_ch_means else 0.0
                    )
                    _craft_status = (
                        "PASS" if _overall_craft >= 0.4
                        else ("WARN" if _overall_craft >= 0.2 else "FAIL")
                    )
                    print(
                        f"Bestseller craft gate (advisory): {_craft_status} — "
                        f"overall ONTGP score {_overall_craft:.2f}",
                        file=sys.stderr,
                    )
                    # Merge craft scores into the chapter flow report if present
                    _flow_rpath = render_dir / "chapter_flow_report.json"
                    if _flow_rpath.exists():
                        _fr = json.loads(_flow_rpath.read_text(encoding="utf-8"))
                        _fr["bestseller_craft"] = {
                            "overall_score": round(_overall_craft, 4),
                            "per_chapter": _craft_results,
                        }
                        _flow_rpath.write_text(json.dumps(_fr, indent=2), encoding="utf-8")
                except Exception as _e:
                    print(f"Bestseller craft gate error (non-blocking): {_e}", file=sys.stderr)

            # 3. Scene anti-genericity gate
            if args.enforce_scene_gate:
                try:
                    from phoenix_v4.qa.scene_anti_genericity_gate import (
                        enforce_scene_gate as _enforce_scene_gate,
                    )
                    _scene_proses = _extract_registry_chapters(_prose_reg_out)
                    if _scene_proses:
                        _scene_result = _enforce_scene_gate(
                            _scene_proses, mode=args.scene_gate_mode
                        )
                        _scene_report_dir = render_dir / "scene_gate"
                        _scene_report_dir.mkdir(parents=True, exist_ok=True)
                        _scene_report_path = _scene_report_dir / f"registry-{topic_id}.json"
                        _scene_report_path.write_text(
                            json.dumps({
                                "status": _scene_result.status,
                                "mode": _scene_result.mode,
                                "blocking": _scene_result.blocking,
                                "errors": _scene_result.report.errors,
                                "warnings": _scene_result.report.warnings,
                                "metrics": _scene_result.report.metrics,
                            }, indent=2),
                            encoding="utf-8",
                        )
                        if _scene_result.blocking:
                            print(
                                f"Scene anti-genericity gate FAILED. "
                                f"Report: {_scene_report_path}",
                                file=sys.stderr,
                            )
                            for _se in _scene_result.report.errors:
                                print(f"  - {_se}", file=sys.stderr)
                            _quality_gate_failures.append("scene_anti_genericity")
                        else:
                            for _sw in _scene_result.report.warnings:
                                print(f"Scene gate warning: {_sw}", file=sys.stderr)
                            print(
                                f"Scene anti-genericity gate {_scene_result.status}. "
                                f"Report: {_scene_report_path}",
                                file=sys.stderr,
                            )
                    else:
                        print(
                            "Scene gate skipped: no chapters in registry prose.",
                            file=sys.stderr,
                        )
                except Exception as _e:
                    print(f"Scene anti-genericity gate error: {_e}", file=sys.stderr)
                    _quality_gate_failures.append("scene_anti_genericity")

            # 4. EI v2 comparison (advisory — V1 remains authoritative)
            if args.ei_v2_compare:
                try:
                    from phoenix_v4.quality.ei_parallel_adapter import (
                        compare_slot as _ei_compare_slot,
                        build_pipeline_comparison as _ei_build_comparison,
                        write_comparison_report as _ei_write_report,
                    )
                    from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
                    _v2_cfg = load_ei_v2_config()
                    _v1_cfg: dict = {}
                    _v1_cfg_path = (
                        REPO_ROOT / "config" / "source_of_truth"
                        / "enlightened_intelligence_registry.yaml"
                    )
                    if _v1_cfg_path.exists() and yaml:
                        _v1_cfg = yaml.safe_load(
                            _v1_cfg_path.read_text(encoding="utf-8")
                        ) or {}
                    _book_thesis = (
                        f"{topic_id} for {book_spec_for_compiler.get('persona_id', '')}"
                    )
                    _teacher_mode_reg = bool(teacher_id_for_reg)
                    _slot_comparisons = []
                    for _ch_idx, _ch in enumerate(resolved_book.chapters):
                        _chapter_text = "\n\n".join(
                            s.content for s in _ch.sections if s.content.strip()
                        )
                        _arc_intent = {
                            "chapter_index": _ch_idx,
                            "chapter_thesis": _book_thesis,
                        }
                        for _si, _section in enumerate(_ch.sections):
                            _candidates_raw = [{
                                "id": (
                                    f"registry:{topic_id}:ch{_ch_idx}:s{_si}"
                                ),
                                "text": _section.content,
                                "meta": {},
                            }]
                            try:
                                _slot_result = _ei_compare_slot(
                                    slot=_section.section_type,
                                    chapter_index=_ch_idx,
                                    slot_index=_si,
                                    candidates_raw=_candidates_raw,
                                    persona_id=book_spec_for_compiler.get(
                                        "persona_id", ""
                                    ),
                                    topic_id=topic_id,
                                    thesis=_book_thesis,
                                    v1_cfg=_v1_cfg,
                                    v2_cfg=_v2_cfg,
                                    selector_key=(
                                        f"ei:{_section.section_type}:ch{_ch_idx}"
                                        f":{book_spec_for_compiler.get('persona_id', '')}"
                                        f":{topic_id}"
                                    ),
                                    teacher_mode=_teacher_mode_reg,
                                    chapter_text=_chapter_text,
                                    arc_intent=_arc_intent,
                                )
                                _slot_comparisons.append(_slot_result)
                            except Exception as _exc:
                                print(
                                    f"EI V2 compare failed at "
                                    f"ch{_ch_idx} {_section.section_type}: {_exc}",
                                    file=sys.stderr,
                                )
                    if _slot_comparisons:
                        _comparison = _ei_build_comparison(
                            _slot_comparisons,
                            plan_hash=f"registry-{topic_id}",
                            persona_id=book_spec_for_compiler.get("persona_id", ""),
                            topic_id=topic_id,
                        )
                        _ei_v2_dir = REPO_ROOT / "artifacts" / "ei_v2"
                        _ei_report_path = _ei_write_report(_comparison, _ei_v2_dir)
                        print(f"EI V2 comparison: {_ei_report_path}")
                        print(
                            f"  Slots compared: {_comparison.total_slots} | "
                            f"Agreement: {_comparison.agreement_rate * 100:.0f}% | "
                            f"Safety flags: {len(_comparison.v2_safety_flags)} | "
                            f"TTS issues: {len(_comparison.v2_tts_issues)} | "
                            f"Dedup flags: {len(_comparison.v2_dedup_flags)} | "
                            f"Arc issues: {len(_comparison.v2_arc_issues)}"
                        )
                except Exception as _exc:
                    print(
                        f"EI V2 comparison failed (non-blocking): {_exc}",
                        file=sys.stderr,
                    )

            # 5. Book pass gate — SKIPPED in registry mode
            if gates_run:
                print(
                    "Book pass gate: SKIPPED (registry mode — requires atom_ids / "
                    "chapter_slot_sequence / dominant_band_sequence).",
                    file=sys.stderr,
                )

            # 6. Freebie generation (explicit --generate-freebies only;
            #    registry mode has no compiled plan, so default-on is disabled)
            if args.generate_freebies:
                try:
                    from phoenix_v4.freebies.freebie_renderer import (
                        generate_freebies_for_book,
                    )
                    _freebie_plan = {
                        "plan_id": f"registry-{topic_id}-{seed}",
                        "topic_id": topic_id,
                        "persona_id": book_spec_for_compiler.get("persona_id", ""),
                        "teacher_id": teacher_id_for_reg,
                        "freebie_slug": (
                            f"{topic_id}-{book_spec_for_compiler.get('persona_id', '')}"
                        ),
                        "word_count": _wc_prose,
                        "source": "section_registry",
                        "format_id": _reg_format_id,
                        "runtime_format_id": _reg_runtime,
                    }
                    _formats_list = None
                    if args.formats:
                        _formats_list = [
                            f.strip().lower()
                            for f in args.formats.split(",")
                            if f.strip()
                        ]
                    _publish_dir = (
                        Path(args.publish_dir) if args.publish_dir else None
                    )
                    _asset_store = (
                        Path(args.asset_store) if args.asset_store else None
                    )
                    _freebie_paths = generate_freebies_for_book(
                        _freebie_plan,
                        book_spec_for_compiler,
                        include_pdf=bool(
                            _formats_list and "pdf" in _formats_list
                        ),
                        formats=_formats_list,
                        skip_audio=args.skip_audio,
                        publish_dir=_publish_dir,
                        asset_store_root=_asset_store,
                    )
                    if _freebie_paths:
                        print(
                            f"Generated freebie artifacts: "
                            f"{len(_freebie_paths)} file(s) under artifacts/freebies/"
                        )
                except Exception as _e:
                    print(f"Freebie generation failed (non-blocking): {_e}", file=sys.stderr)

            # 7. Write quality summary
            _qs_path = render_dir / "quality_summary.json"
            _reg_bq_fail, _reg_bq_frag = _apply_book_quality_gate(
                render_dir=render_dir,
                prose=prose,
                runtime_format_id=_reg_runtime or "",
                gates_hard=_block_on_fail(quality_profile, "book_quality_gate"),
                governance_report=None,
                slot_sequences=None,
                frame=str(getattr(args, "frame", "somatic_first") or "somatic_first"),
                policy_override=bool(getattr(args, "book_quality_override", False)),
            )
            _quality_gate_failures.extend(_reg_bq_fail)
            _qs_path.write_text(
                json.dumps({
                    "source": "section_registry",
                    "topic_id": topic_id,
                    "persona_id": book_spec_for_compiler.get("persona_id", ""),
                    "teacher_id": teacher_id_for_reg,
                    "format_id": _reg_format_id,
                    "runtime_format_id": _reg_runtime,
                    "quality_profile": quality_profile,
                    "gates_run": gates_run,
                    "gates_hard": gates_hard,
                    "gate_failures": _quality_gate_failures,
                    "overall_status": "PASS" if not _quality_gate_failures else "FAIL",
                    "book_pass_gate": "SKIPPED_REGISTRY_MODE",
                    "book_quality_gate": _reg_bq_frag,
                }, indent=2),
                encoding="utf-8",
            )
            print(f"Quality summary: {_qs_path}")

            # 8. Gate enforcement — production blocks on any gate; flagship blocks
            # only on FLAGSHIP_BLOCKING_GATES (chapter_flow, book_quality_gate,
            # scene_anti_genericity), which are the only gates that even appended
            # to _quality_gate_failures under flagship anyway.
            if _quality_gate_failures and (gates_hard or quality_profile == "flagship"):
                _profile_label = "flagship" if quality_profile == "flagship" else "production"
                print(
                    f"BLOCKED: {len(_quality_gate_failures)} quality gate(s) failed "
                    f"in {_profile_label} mode: {', '.join(_quality_gate_failures)}. "
                    f"Use --skip-quality-gates or --quality-profile=draft to bypass.",
                    file=sys.stderr,
                )
                return 1

        if not getattr(args, "no_job_check", False):
            from scripts.pipeline.advance_stage import mark_pipeline_finished

            mark_pipeline_finished(ebook_job_ws, "ebook")
        return 0

    # ── NO REGISTRY = USE ATOM ASSEMBLY (the original V4 pipeline) ──
    # Registry is optional polish (chapter titles). Atoms are the content.
    # The atom pool has 42,000+ variants across all topics and personas.
    print(f"No registry for '{topic_id}' — using atom assembly pipeline.")

    require_full_resolution = False  # persona atoms fill gaps
    from phoenix_v4.planning.assembly_compiler import compile_plan
    compiled = compile_plan(
        book_spec_for_compiler,
        format_plan_dict,
        arc_path=arc_path,
        require_full_resolution=require_full_resolution,
        atoms_root=atoms_root,
        atoms_model=effective_atoms_model,
    )

    # Part 3.1 / 3.3 validate compiled plan (structure)
    from phoenix_v4.qa.validate_compiled_plan import validate_compiled_plan
    from phoenix_v4.planning.angle_resolver import get_angle_context
    angle_ctx = get_angle_context(book_spec_for_compiler.get("angle_id")) if book_spec_for_compiler.get("angle_id") else None
    # Chapter planner may adjust per-chapter slot policies at compile time; validate against actual compiled sequence.
    format_plan_for_validation = dict(format_plan_dict)
    format_plan_for_validation["slot_definitions"] = compiled.chapter_slot_sequence
    format_plan_for_validation["chapter_count"] = len(compiled.chapter_slot_sequence)
    format_plan_for_validation["target_chapter_count"] = len(compiled.chapter_slot_sequence)
    val_result = validate_compiled_plan(
        compiled, format_plan_for_validation,
        angle_context=angle_ctx,
        enforce_integration_reinforcement=False,
    )
    if not val_result.valid:
        for e in val_result.errors:
            print(f"Validation failed: {e}", file=sys.stderr)
        for w in val_result.warnings:
            print(f"Warning: {w}", file=sys.stderr)
        return 1
    for w in val_result.warnings:
        print(f"Warning: {w}", file=sys.stderr)

    # Arc-First: arc alignment check (warn only — depth sort may shift bands)
    from phoenix_v4.qa.validate_arc_alignment import validate_arc_alignment
    arc_errors = validate_arc_alignment(compiled, arc)
    if arc_errors:
        for e in arc_errors:
            print(f"Arc alignment note: {e}", file=sys.stderr)
        # Depth progression takes priority over exact band matching;
        # do not block on arc alignment when the global depth sort
        # has reordered atoms for narrative escalation.

    from phoenix_v4.planning.engine_loader import load_engine
    engine_def = load_engine(arc.engine)
    if engine_def:
        from phoenix_v4.qa.validate_engine_resolution import validate_engine_resolution
        engine_errors = validate_engine_resolution(arc, engine_def)
        if engine_errors:
            for e in engine_errors:
                print(f"Engine resolution failed: {e}", file=sys.stderr)
            return 1

    # Book-pass gate: narrative progression + prose-level claim quality.
    # Runs when quality profile is production/draft OR when --enforce-book-pass-gate is set.
    _run_book_pass_pre_render = gates_run or args.enforce_book_pass_gate
    if _run_book_pass_pre_render:
        from phoenix_v4.qa.atom_metadata_loader import load_atom_metadata
        from phoenix_v4.qa.book_pass_gate import validate_book_pass
        from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan

        plan_for_gate = {
            "chapter_slot_sequence": compiled.chapter_slot_sequence,
            "atom_ids": compiled.atom_ids,
            "dominant_band_sequence": compiled.dominant_band_sequence or [],
            "exercise_chapters": compiled.exercise_chapters or [],
            "persona_id": canonical_persona,
            "topic_id": canonical_topic,
            "emotional_curve": getattr(arc, "emotional_curve", None) or [],
        }
        atom_meta = load_atom_metadata(
            atoms_root=atoms_root,
            persona=canonical_persona,
            topic=canonical_topic,
        )
        # Teacher Mode: merge teacher atom metadata into atom_meta so gates
        # can see mechanism_depth, identity_stage, cost from teacher banks.
        if teacher_mode and teacher_id:
            from phoenix_v4.planning.pool_index import _load_teacher_pool
            teacher_root = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "approved_atoms"
            if teacher_root.exists():
                teacher_entries = _load_teacher_pool(teacher_root, "STORY")
                for e in teacher_entries:
                    if e.metadata:
                        atom_meta[e.atom_id] = dict(e.metadata)
        # Clean orphaned callbacks: strip setup-only callback metadata from atoms
        # that have no matching return atom in the plan's atom_ids.
        plan_aids = set(compiled.atom_ids)
        setup_cbs = {atom_meta[a].get("callback_id") for a in plan_aids if a in atom_meta and atom_meta[a].get("callback_phase") == "setup" and atom_meta[a].get("callback_id")}
        return_cbs = {atom_meta[a].get("callback_id") for a in plan_aids if a in atom_meta and atom_meta[a].get("callback_phase") == "return" and atom_meta[a].get("callback_id")}
        orphan_cbs = setup_cbs - return_cbs
        if orphan_cbs:
            for a in plan_aids:
                if a in atom_meta and atom_meta[a].get("callback_id") in orphan_cbs:
                    atom_meta[a].pop("callback_id", None)
                    atom_meta[a].pop("callback_phase", None)

        locale = out.get("locale") or args.locale
        prose = resolve_prose_for_plan(plan_for_gate, atoms_root=atoms_root, locale=locale).prose_map
        book_pass = validate_book_pass(plan_for_gate, atom_meta, prose_map=prose)

        report_dir = REPO_ROOT / "artifacts" / "book_pass"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{compiled.plan_hash}.json"
        report_path.write_text(
            json.dumps(
                {
                    "plan_hash": compiled.plan_hash,
                    "persona_id": canonical_persona,
                    "topic_id": canonical_topic,
                    "valid": book_pass.valid,
                    "errors": book_pass.errors,
                    "warnings": book_pass.warnings,
                    "metrics": book_pass.metrics,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        if not book_pass.valid:
            if gates_hard or args.enforce_book_pass_gate:
                print(f"Book-pass gate failed. Report: {report_path}", file=sys.stderr)
                for e in book_pass.errors:
                    print(f"  - {e}", file=sys.stderr)
                return 1
            else:
                # draft mode: warn only
                print(f"Book-pass gate WARN (draft mode). Report: {report_path}", file=sys.stderr)
                for e in book_pass.errors:
                    print(f"  WARNING: {e}", file=sys.stderr)
        for w in book_pass.warnings:
            print(f"Book-pass warning: {w}", file=sys.stderr)
        if book_pass.valid:
            print(f"Book-pass gate passed. Report: {report_path}", file=sys.stderr)

    # Teacher matrix: enforce peak_intensity_limit on compiled band sequence
    if teacher_id and teacher_id != "default_teacher":
        from phoenix_v4.planning.teacher_matrix import load_teacher_matrix
        matrix = load_teacher_matrix()
        if matrix:
            teacher_entry = matrix.get("teachers", {}).get(teacher_id, {})
            constraints = teacher_entry.get("constraints") or {}
            peak_limit = constraints.get("peak_intensity_limit")
            if peak_limit is not None:
                bands = [b for b in (compiled.dominant_band_sequence or []) if b is not None]
                if bands:
                    max_band = max(bands)
                    if max_band > peak_limit:
                        print(
                            f"Peak intensity limit exceeded: plan max band={max_band}, "
                            f"teacher {teacher_id} peak_intensity_limit={peak_limit}",
                            file=sys.stderr,
                        )
                        return 1

    # Plan §6.1: teacher exercise share ≥ 60% when fallback used
    if teacher_id and teacher_id != "default_teacher" and getattr(compiled, "atom_sources", None):
        from phoenix_v4.qa.validate_teacher_exercise_share import validate_teacher_exercise_share
        ok, msg = validate_teacher_exercise_share(
            compiled.chapter_slot_sequence,
            compiled.atom_ids,
            list(compiled.atom_sources),
            min_share=0.60,
        )
        if not ok:
            print(f"Teacher exercise share validation failed: {msg}", file=sys.stderr)
            return 1

    out = {
        "plan_hash": compiled.plan_hash,
        "plan_id": compiled.plan_hash,
        "chapter_slot_sequence": compiled.chapter_slot_sequence,
        "atom_ids": compiled.atom_ids,
        "dominant_band_sequence": compiled.dominant_band_sequence,
    }
    if compiled.arc_id:
        out["arc_id"] = compiled.arc_id
    if teacher_id and teacher_id != "default_teacher":
        out["teacher_id"] = teacher_id
        out["teacher_mode"] = True
        # Plan §5.4: emit doctrine_version, doctrine_fingerprint for CI/audit (load from teacher bank if present)
        teacher_banks = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
        doctrine_path = teacher_banks / teacher_id / "doctrine" / "doctrine.yaml"
        if not doctrine_path.exists():
            doctrine_path = teacher_banks / teacher_id / "doctrine.yaml"
        if doctrine_path.exists():
            try:
                from phoenix_v4.teacher.doctrine_fingerprint import load_doctrine_yaml, fingerprint_doctrine
                doctrine = load_doctrine_yaml(doctrine_path)
                if doctrine:
                    out["teacher_doctrine_version"] = doctrine.get("doctrine_version")
                    out["doctrine_fingerprint"] = fingerprint_doctrine(doctrine)
            except Exception:
                pass
    # ── Teacher Mode Pre-Intro Chapter + Closing (TEACHER_MODE_STRUCTURAL_SPEC §1, §4) ──
    if teacher_id and teacher_id != "default_teacher":
        _teacher_display = ""
        _teacher_tradition = ""
        _doctrine_for_preintro: dict = {}
        _t_doctrine_path = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
        if not _t_doctrine_path.exists():
            _t_doctrine_path = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine.yaml"
        if _t_doctrine_path.exists():
            _doctrine_for_preintro = _load_yaml(_t_doctrine_path)
            _teacher_display = _doctrine_for_preintro.get("display_name") or teacher_id.replace("_", " ").title()
            _teacher_tradition = _doctrine_for_preintro.get("tradition") or ""
        else:
            _teacher_display = teacher_id.replace("_", " ").title()
        _topic_display = (book_spec_for_compiler.get("topic_id") or "").replace("_", " ")
        _persona_display = (book_spec_for_compiler.get("persona_id") or "").replace("_", " ")
        # Locale-aware teacher pre-intro
        _locale = book_spec_for_compiler.get("locale") or args.locale
        try:
            from phoenix_v4.rendering.locale_templates import translate_fstring as _tl
        except ImportError:
            def _tl(s, **kw): return s.format(**kw) if kw else s

        _pre_intro_paras = [
            _tl("I was not a direct student of {teacher}. I encountered their work "
                "through books, talks, and publicly available teachings. What follows is not "
                "an official interpretation of {teacher}'s work — it is an application. "
                "I have done my best to honor the integrity of the original teachings while "
                "translating them into practical guidance for the challenges you may be facing.",
                locale=_locale, teacher=_teacher_display),
            _tl("{teacher}'s understanding of {topic} reshaped the way I see "
                "this subject. Their approach offers a lens that goes beyond conventional advice. "
                "It speaks to something deeper: the patterns beneath the surface, the quiet mechanisms "
                "that keep us stuck, and the often-overlooked pathways toward genuine relief.",
                locale=_locale, teacher=_teacher_display, topic=_topic_display),
            _tl("This book applies {teacher}'s teachings to the specific experience "
                "of {persona} navigating {topic}. It does not replace the "
                "teacher's original work. Where I have adapted exercises or frameworks, I have "
                "done so with care and transparency. Any simplification is mine, not theirs.",
                locale=_locale, teacher=_teacher_display, persona=_persona_display, topic=_topic_display),
            _tl("If something in these pages resonates with you, I encourage you to go to "
                "the source. Seek out {teacher}'s own words — their talks, their "
                "writings, their direct teachings. What I offer here is a bridge, not a "
                "destination. The real work lives in the original.",
                locale=_locale, teacher=_teacher_display),
        ]
        _pre_intro_title = _tl("A Note on the Teachings of {teacher}", locale=_locale, teacher=_teacher_display)
        out["teacher_pre_intro_chapter"] = {
            "title": _pre_intro_title,
            "content": "\n\n".join(_pre_intro_paras),
        }
        _closing_paras = [
            f"This book drew from the teachings of {_teacher_display} to offer you a "
            f"practical path through {_topic_display}. But what you have read here is "
            f"only one application — shaped by my perspective and filtered through "
            f"the specific challenges of {_persona_display}.",
            f"If these ideas spoke to you, go deeper. Seek out {_teacher_display}'s "
            f"original works. Listen to their talks. Sit with their words directly. "
            f"The bridge this book offers is meant to lead you to the source, not "
            f"to stand in its place.",
        ]
        out["teacher_closing_section"] = {
            "title": "Where to Go Deeper",
            "content": "\n\n".join(_closing_paras),
        }

    if getattr(compiled, "atom_sources", None):
        out["atom_sources"] = compiled.atom_sources
    if getattr(compiled, "chapter_thesis", None):
        out["chapter_thesis"] = compiled.chapter_thesis
    # Plan §3.12: when teacher_mode and any synthetic present, doctrine version must be pinned
    if teacher_id and teacher_id != "default_teacher" and getattr(compiled, "atom_sources", None):
        if "teacher_synthetic" in (compiled.atom_sources or []) and not out.get("teacher_doctrine_version"):
            print("Teacher mode with synthetic atoms requires teacher_doctrine_version (doctrine.yaml with doctrine_version).", file=sys.stderr)
            return 1
    # Structural fingerprint (CI / wave density / similarity)
    if compiled.emotional_temperature_sequence:
        out["emotional_temperature_sequence"] = compiled.emotional_temperature_sequence
    elif compiled.dominant_band_sequence:
        out["emotional_temperature_sequence"] = [str(b) if b is not None else "3" for b in compiled.dominant_band_sequence]
    if compiled.exercise_chapters is not None:
        out["exercise_chapters"] = compiled.exercise_chapters
    if compiled.slot_sig:
        out["slot_sig"] = compiled.slot_sig
    out["format_id"] = format_plan_dict.get("format_structural_id") or format_plan_dict.get("format_id") or ""
    out["runtime_format_id"] = _resolved_runtime_format_id(args, format_plan_dict)
    if format_plan_dict.get("output_format_id"):
        out["output_format_id"] = format_plan_dict.get("output_format_id")
        out["output_format_name"] = format_plan_dict.get("output_format_name")
    out["v4_freeze_enabled"] = freeze_enabled
    out["locale"] = book_spec_for_compiler.get("locale", "en-US")
    out["territory"] = book_spec_for_compiler.get("territory", "US")
    if book_spec_for_compiler.get("requested_location_id"):
        out["requested_location_id"] = book_spec_for_compiler["requested_location_id"]
    if book_spec_for_compiler.get("resolved_location_id"):
        out["resolved_location_id"] = book_spec_for_compiler["resolved_location_id"]
        out["location_id"] = book_spec_for_compiler["resolved_location_id"]
        location_profiles = load_render_location_profiles()
        location_profile = location_profiles.get(book_spec_for_compiler["resolved_location_id"]) or {}
        city_name = location_profile.get("city_name")
        if city_name:
            out["city_name"] = city_name
    out["atoms_model"] = effective_atoms_model
    if getattr(arc, "engine", None):
        out["engine_id"] = arc.engine
    # Angle Integration (V4.7) — structural fingerprint / CTSS / wave density
    if book_spec_for_compiler.get("angle_id"):
        out["angle_id"] = book_spec_for_compiler["angle_id"]
    if compiled.reflection_strategy_sequence:
        out["reflection_strategy_sequence"] = compiled.reflection_strategy_sequence
    if compiled.chapter_archetypes:
        out["chapter_archetypes"] = compiled.chapter_archetypes
    if compiled.chapter_exercise_modes:
        out["chapter_exercise_modes"] = compiled.chapter_exercise_modes
    if compiled.chapter_reflection_weights:
        out["chapter_reflection_weights"] = compiled.chapter_reflection_weights
    if compiled.chapter_story_depths:
        out["chapter_story_depths"] = compiled.chapter_story_depths
    if compiled.chapter_planner_warnings:
        out["chapter_planner_warnings"] = compiled.chapter_planner_warnings
    if getattr(compiled, "chapter_bestseller_structures", None):
        out["chapter_bestseller_structures"] = compiled.chapter_bestseller_structures
    # Author identity and assets (Writer Spec §23)
    if book_spec_for_compiler.get("author_id"):
        out["author_id"] = book_spec_for_compiler["author_id"]
    if book_spec_for_compiler.get("narrator_id"):
        out["narrator_id"] = book_spec_for_compiler["narrator_id"]
    if author_assets is not None:
        out["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}
    # Author cover art base (docs/authoring/AUTHOR_COVER_ART_SYSTEM.md): for export/storefront; fallback to default when no author/teacher
    cover_author_id = book_spec_for_compiler.get("author_id") or (teacher_id if (teacher_id and teacher_id != "default_teacher") else None)
    from phoenix_v4.planning.author_cover_art_resolver import resolve_author_cover_art
    cover_art = resolve_author_cover_art(cover_author_id, repo_root=REPO_ROOT)
    out["cover_art_base"] = cover_art.get("cover_art_base", "")
    out["cover_art_style_hint"] = cover_art.get("cover_art_style_hint", "")
    out["cover_art_palette_tokens"] = cover_art.get("cover_art_palette_tokens", [])
    out["cover_variant_id"] = cover_art.get("cover_variant_id", "")
    if book_spec_for_compiler.get("_pre_intro_signature"):
        out["pre_intro_signature"] = book_spec_for_compiler["_pre_intro_signature"]
    if book_spec_for_compiler.get("opening_style_id"):
        out["opening_style_id"] = book_spec_for_compiler["opening_style_id"]
    if book_spec_for_compiler.get("integration_ending_style_id"):
        out["integration_ending_style_id"] = book_spec_for_compiler["integration_ending_style_id"]
    if book_spec_for_compiler.get("carry_line_style_id"):
        out["carry_line_style_id"] = book_spec_for_compiler["carry_line_style_id"]
    if getattr(compiled, "ending_signature", None):
        out["ending_signature"] = compiled.ending_signature
    if getattr(compiled, "carry_line", None):
        out["carry_line"] = compiled.carry_line
    # ── Introduction & Conclusion Chapters (Hybrid Template Bank) ──────
    # Applies to both regular and teacher mode books when enabled.
    _ic_config = _load_yaml(REPO_ROOT / "config" / "source_of_truth" / "intro_ending_variation.yaml")
    if _ic_config.get("intro_conclusion_chapters_enabled", False):
        try:
            from phoenix_v4.planning.intro_conclusion_resolver import (
                resolve_introduction_chapter,
                resolve_conclusion_chapter,
            )
            _ic_topic = book_spec_for_compiler.get("topic_id") or ""
            _ic_persona = book_spec_for_compiler.get("persona_id") or ""
            _ic_seed = book_spec_for_compiler.get("seed") or "default_seed"
            _ic_brand = book_spec_for_compiler.get("brand_id") or None
            _ic_alias = None
            if out.get("mechanism_alias"):
                _ic_alias = out["mechanism_alias"]
            elif book_spec_for_compiler.get("mechanism_alias"):
                _ic_alias = book_spec_for_compiler["mechanism_alias"]
            _ic_ch_count = len(compiled.chapter_slot_sequence) if compiled.chapter_slot_sequence else None
            _ic_format_id = out.get("format_id") or format_plan_dict.get("format_structural_id") or None
            _ic_runtime_id = (out.get("runtime_format_id") or "").strip() or _resolved_runtime_format_id(args, format_plan_dict) or None

            intro_resolved = resolve_introduction_chapter(
                _ic_topic, _ic_persona, _ic_seed, brand_id=_ic_brand,
                format_id=_ic_format_id, runtime_format_id=_ic_runtime_id,
                mechanism_alias=_ic_alias, chapter_count=_ic_ch_count,
            )
            conclusion_resolved = resolve_conclusion_chapter(
                _ic_topic, _ic_persona, _ic_seed, brand_id=_ic_brand,
                format_id=_ic_format_id, runtime_format_id=_ic_runtime_id,
                mechanism_alias=_ic_alias, chapter_count=_ic_ch_count,
            )

            # Cap/duplicate check (best-effort; skip if no brand_id)
            if _ic_brand:
                from phoenix_v4.planning.intro_ending_caps import (
                    check_intro_chapter_cap, check_conclusion_chapter_cap,
                    get_quarter_for_brand, load_signature_index,
                )
                _ic_quarter = get_quarter_for_brand(_ic_brand)
                _sig_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
                _sig_index = load_signature_index(_sig_path)
                _ic_cap = _ic_config.get("intro_chapter_signature_cap_share", 0.12)
                _cc_cap = _ic_config.get("conclusion_chapter_signature_cap_share", 0.12)
                _max_retries = _ic_config.get("max_retries", 5)

                for _retry in range(_max_retries):
                    intro_check = check_intro_chapter_cap(
                        _ic_brand, _ic_quarter, intro_resolved["signature"], _sig_index, _ic_cap,
                    )
                    if intro_check.ok:
                        break
                    intro_resolved = resolve_introduction_chapter(
                        _ic_topic, _ic_persona, _ic_seed, brand_id=_ic_brand,
                        format_id=_ic_format_id, runtime_format_id=_ic_runtime_id,
                        mechanism_alias=_ic_alias, chapter_count=_ic_ch_count,
                        retry_index=_retry + 1,
                    )

                for _retry in range(_max_retries):
                    conclusion_check = check_conclusion_chapter_cap(
                        _ic_brand, _ic_quarter, conclusion_resolved["signature"], _sig_index, _cc_cap,
                    )
                    if conclusion_check.ok:
                        break
                    conclusion_resolved = resolve_conclusion_chapter(
                        _ic_topic, _ic_persona, _ic_seed, brand_id=_ic_brand,
                        format_id=_ic_format_id, runtime_format_id=_ic_runtime_id,
                        mechanism_alias=_ic_alias, chapter_count=_ic_ch_count,
                        retry_index=_retry + 1,
                    )

            out["introduction_chapter"] = {
                "title": intro_resolved["title"],
                "content": intro_resolved["content"],
                "template_id": intro_resolved.get("template_id", ""),
                "size": intro_resolved.get("size", "full"),
            }
            out["intro_chapter_signature"] = intro_resolved["signature"]
            out["conclusion_chapter"] = {
                "title": conclusion_resolved["title"],
                "content": conclusion_resolved["content"],
                "template_id": conclusion_resolved.get("template_id", ""),
                "size": conclusion_resolved.get("size", "full"),
            }
            out["conclusion_chapter_signature"] = conclusion_resolved["signature"]
        except Exception as e:
            print(f"Intro/Conclusion chapter resolution failed (non-fatal): {e}", file=sys.stderr)

    # Author positioning (Writer Spec §24)
    if compiled.author_positioning_profile:
        out["author_positioning_profile"] = compiled.author_positioning_profile
    if compiled.positioning_signature_hash:
        out["positioning_signature_hash"] = compiled.positioning_signature_hash
    # Compression (DEV SPEC 2)
    if compiled.compression_atom_ids:
        out["compression_atom_ids"] = compiled.compression_atom_ids
    if compiled.compression_sig:
        out["compression_sig"] = compiled.compression_sig
    if compiled.compression_pos_sig:
        out["compression_pos_sig"] = compiled.compression_pos_sig
    if compiled.compression_len_vec:
        out["compression_len_vec"] = compiled.compression_len_vec
    # DEV SPEC 3: Emotional Role Taxonomy
    if compiled.emotional_role_sequence:
        out["emotional_role_sequence"] = compiled.emotional_role_sequence
    if compiled.emotional_role_sig:
        out["emotional_role_sig"] = compiled.emotional_role_sig
    # Structural Variation V4: variation knobs and signature
    out["book_structure_id"] = variation_knobs.get("book_structure_id", "linear_transformation")
    out["journey_shape_id"] = variation_knobs.get("journey_shape_id", "recognition_to_agency")
    out["motif_id"] = variation_knobs.get("motif_id", "motif_pattern")
    out["section_reorder_mode"] = variation_knobs.get("section_reorder_mode", "none")
    out["reframe_profile_id"] = variation_knobs.get("reframe_profile_id", "balanced")
    out["variation_chapter_archetypes"] = variation_knobs.get("chapter_archetypes", [])
    if not out.get("chapter_archetypes"):
        out["chapter_archetypes"] = variation_knobs.get("chapter_archetypes", [])
    out["variation_signature"] = variation_knobs.get("variation_signature", "")
    if getattr(compiled, "motif_injections", None):
        out["motif_injections"] = compiled.motif_injections
    if getattr(compiled, "reframe_injections", None):
        out["reframe_injections"] = compiled.reframe_injections
    # Freebie attachment (post-Stage 3; Phase 1+3 — specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md)
    from phoenix_v4.planning.freebie_planner import plan_freebies, get_freebie_bundle_with_formats
    index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
    wave_index = []
    if index_path.exists():
        try:
            for ln in index_path.read_text(encoding="utf-8").strip().splitlines():
                if ln.strip():
                    wave_index.append(json.loads(ln))
        except (json.JSONDecodeError, OSError):
            pass
    series_context = None
    if book_spec_for_compiler.get("series_id") or book_spec_for_compiler.get("installment_number") is not None:
        series_context = {
            "series_id": book_spec_for_compiler.get("series_id") or "",
            "installment_number": book_spec_for_compiler.get("installment_number"),
            "total_in_series": book_spec_for_compiler.get("total_in_series"),
            "previous_primary_freebies": [r.get("freebie_bundle", [None])[0] for r in wave_index if r.get("freebie_bundle")],
        }
    freebie_bundle, cta_template_id, freebie_slug = plan_freebies(
        book_spec_for_compiler,
        format_plan_dict,
        compiled,
        arc,
        wave_index=wave_index if wave_index else None,
        series_context=series_context,
    )
    out["freebie_bundle"] = freebie_bundle
    out["cta_template_id"] = cta_template_id
    out["freebie_slug"] = freebie_slug
    # Formats per freebie for asset manifest (V4 Immersion Ecosystem)
    if yaml:
        registry_path = REPO_ROOT / "config" / "freebies" / "freebie_registry.yaml"
        if registry_path.exists():
            reg = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
            freebies_map = reg.get("freebies") or {}
            out["freebie_bundle_with_formats"] = get_freebie_bundle_with_formats(
                freebie_bundle, freebies_map, book_spec_for_compiler, format_plan_dict, compiled
            )
        else:
            out["freebie_bundle_with_formats"] = [{"freebie_id": fid, "formats": ["html"]} for fid in freebie_bundle]
    else:
        out["freebie_bundle_with_formats"] = [{"freebie_id": fid, "formats": ["html"]} for fid in freebie_bundle]
    out["requested_topic_id"] = topic_id
    out["requested_persona_id"] = persona_id
    out["canonical_topic_id"] = book_spec_for_compiler.get("topic_id") or book_spec_for_compiler.get("topic") or ""
    out["canonical_persona_id"] = book_spec_for_compiler.get("persona_id") or book_spec_for_compiler.get("persona") or ""
    out["topic_id"] = out["canonical_topic_id"]
    out["persona_id"] = out["canonical_persona_id"]
    # §5G: attach output contract to plan
    out["output_contract"] = _output_contract
    for experience_field in (
        "delivery_experience",
        "reader_intent",
        "pacing_model",
        "outcome_type",
        "engagement_depth",
        "transformation_speed",
        "perceived_positioning",
        "experience_hash",
        "ai_disclosure_status",
    ):
        compiled_value = getattr(compiled, experience_field, None)
        if compiled_value is not None:
            out[experience_field] = compiled_value
            continue
        book_spec_value = book_spec_for_compiler.get(experience_field)
        if book_spec_value is not None:
            out[experience_field] = book_spec_value
    try:
        from phoenix_v4.planning.experience_resolver import ensure_ai_disclosure, resolve_and_attach

        resolve_and_attach(out)
        ensure_ai_disclosure(out)
    except ImportError:
        pass
    except Exception as experience_error:
        import warnings

        warnings.warn(f"Experience resolver failed (non-blocking): {experience_error}", stacklevel=2)
    # Ending cap/duplicate gate (intro_ending_variation)
    if out.get("ending_signature"):
        try:
            from phoenix_v4.planning.intro_ending_caps import (
                load_intro_ending_config,
                get_quarter_for_brand,
                load_signature_index,
                check_ending_cap_and_duplicate,
            )
            intro_cfg = load_intro_ending_config()
            if intro_cfg.get("intro_ending_variation_enabled"):
                sig_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
                end_index = load_signature_index(sig_path)
                quarter = get_quarter_for_brand(brand_id)
                end_cap = float(intro_cfg.get("ending_signature_cap_share", 0.20))
                end_result = check_ending_cap_and_duplicate(
                    brand_id, quarter, out["ending_signature"], end_index, cap_share=end_cap,
                )
                if not end_result.ok:
                    print(f"Ending cap/duplicate gate failed: {end_result.error}", file=sys.stderr)
                    if end_result.candidate_alternatives:
                        for alt in end_result.candidate_alternatives:
                            print(f"  Alternative: {alt}", file=sys.stderr)
                    return 1
        except Exception as e:
            import warnings
            warnings.warn(f"Ending cap check failed: {e}", stacklevel=2)
    # Pre-render word-budget sufficiency check
    if not args.skip_budget_check:
        try:
            from phoenix_v4.planning.budget_check import check_word_budget

            # Load runtime format config for word_range
            _fmt_registry_path = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"
            _runtime_fmt_id = (out.get("runtime_format_id") or "").strip() or _resolved_runtime_format_id(args, format_plan_dict)
            _fmt_cfg: dict = {}
            if _fmt_registry_path.exists() and yaml:
                _all_fmts = yaml.safe_load(_fmt_registry_path.read_text(encoding="utf-8")) or {}
                _fmt_cfg = (_all_fmts.get("runtime_formats") or {}).get(_runtime_fmt_id, {})

            if _fmt_cfg.get("word_range"):
                budget = check_word_budget(out, _fmt_cfg, atoms_root=atoms_root)
                print(budget.message, file=sys.stderr)
                if not budget.sufficient:
                    for ce in budget.per_chapter_estimates:
                        if ce.shortfall > 0:
                            print(
                                f"  Chapter {ce.chapter_index}: {ce.estimated_words} words "
                                f"(target {ce.target_min}, short by {ce.shortfall})",
                                file=sys.stderr,
                            )
                    if args.render_book:
                        print("Budget check failed in render mode. Use --skip-budget-check to override.", file=sys.stderr)
                        return 1
                    else:
                        print("Budget check: insufficient but not in render mode; continuing.", file=sys.stderr)
        except Exception as _budget_exc:
            import warnings as _budget_warnings
            _budget_warnings.warn(f"Budget check failed (non-blocking): {_budget_exc}", stacklevel=2)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Wrote {args.out}")
        # Record pre-intro signature for cap/duplicate gate (intro_ending_variation)
        if out.get("pre_intro_signature") or out.get("ending_signature"):
            from phoenix_v4.planning.intro_ending_caps import get_quarter_for_brand
            sig_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
            sig_path.parent.mkdir(parents=True, exist_ok=True)
            quarter = get_quarter_for_brand(brand_id)
            row = {"brand_id": brand_id, "quarter": quarter}
            if out.get("pre_intro_signature"):
                row["pre_intro_signature"] = out["pre_intro_signature"]
            if out.get("ending_signature"):
                row["ending_signature"] = out["ending_signature"]
            with open(sig_path, "a", encoding="utf-8") as sf:
                sf.write(json.dumps(row) + "\n")
        # Upsert plan row into freebie plan index (one row per book_id) unless test run
        if not getattr(args, "no_update_freebie_index", False):
            index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
            index_row = {
                "book_id": out.get("plan_id") or out.get("plan_hash", ""),
                "freebie_bundle": freebie_bundle,
                "cta_template_id": cta_template_id,
                "slug": freebie_slug,
                "freebie_slug": freebie_slug,
            }
            # Structural Variation V4: include variation knobs in index for wave density / collision
            for key in ("book_structure_id", "journey_shape_id", "motif_id", "section_reorder_mode", "reframe_profile_id", "variation_signature", "chapter_archetypes"):
                if out.get(key) is not None:
                    index_row[key] = out[key]
            _upsert_plan_index_row(index_path, index_row)
        # Generate freebies (HTML, optional PDF) when writing plan (default on; use --no-generate-freebies to disable)
        do_generate_freebies = (bool(args.out) and not args.no_generate_freebies) or args.generate_freebies
        if do_generate_freebies and freebie_slug:
            from phoenix_v4.freebies.freebie_renderer import generate_freebies_for_book
            formats_list = None
            if args.formats:
                formats_list = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
            publish_dir = Path(args.publish_dir) if args.publish_dir else None
            asset_store = Path(args.asset_store) if args.asset_store else None
            paths = generate_freebies_for_book(
                out,
                book_spec_for_compiler,
                include_pdf=bool(formats_list and "pdf" in formats_list) if formats_list else False,
                formats=formats_list,
                skip_audio=args.skip_audio,
                publish_dir=publish_dir,
                asset_store_root=asset_store,
            )
            if paths:
                print(f"Generated freebie artifacts: {len(paths)} file(s) under artifacts/freebies/")
        # Stage 6: render plan to book prose (manuscript/QA) when requested
        if args.render_book:
            from phoenix_v4.rendering import render_book
            render_dir = Path(args.render_dir) if args.render_dir else (REPO_ROOT / "artifacts" / "rendered" / (out.get("plan_id") or out.get("plan_hash", "book")))
            formats_list = [f.strip().lower() for f in (args.render_formats or "txt").split(",") if f.strip()]
            try:
                written = render_book(
                    out,
                    render_dir,
                    formats=formats_list,
                    allow_placeholders=False,
                    on_missing="fail",
                    title_page=True,
                    include_slot_labels_qa=False,
                    enforce_word_count=not args.skip_word_count_gate,
                    enforce_chapter_flow=False,  # chapter_flow gate runs post-render as QA, not blocking
                    music_mode=getattr(args, "music_mode", None),
                    musician_id=getattr(args, "musician_id", None),
                    repo_root_for_music=REPO_ROOT,
                )
                for fmt, path in written.items():
                    print(f"Rendered book ({fmt}): {path}")
                # §5G: update output contract post-render
                _rendered_wc = 0
                for _fmt, _rpath in written.items():
                    try:
                        _rendered_wc = len(Path(_rpath).read_text(encoding="utf-8").split())
                        break  # use first format's word count
                    except Exception:
                        pass
                _output_contract = update_contract_post_render(
                    _output_contract,
                    runtime_achieved=args.runtime_format or out.get("runtime_format_id", ""),
                    word_count_achieved=_rendered_wc,
                )
                out["output_contract"] = _output_contract
                # Write standalone output_contract.json alongside rendered book
                _oc_path = render_dir / "output_contract.json"
                _oc_path.parent.mkdir(parents=True, exist_ok=True)
                with open(_oc_path, "w", encoding="utf-8") as _ocf:
                    json.dump(_output_contract, _ocf, indent=2)
                print(f"Output contract: {_oc_path}")

                _txt_written = written.get("txt")
                _atom_prose = ""
                if _txt_written and Path(_txt_written).exists():
                    _atom_prose = Path(_txt_written).read_text(encoding="utf-8")
                _atom_rt = (args.runtime_format or out.get("runtime_format_id") or "").strip()
                _bq_block = _block_on_fail(quality_profile, "book_quality_gate")
                _atom_bq_fail, _atom_bq_frag = _apply_book_quality_gate(
                    render_dir=render_dir,
                    prose=_atom_prose,
                    runtime_format_id=_atom_rt,
                    gates_hard=_bq_block,
                    governance_report=None,
                    slot_sequences=out.get("chapter_slot_sequence"),
                    frame=str(getattr(args, "frame", "somatic_first") or "somatic_first"),
                    policy_override=bool(getattr(args, "book_quality_override", False)),
                )
                if _atom_bq_fail and _bq_block:
                    print(
                        "BLOCKED: book_quality_gate rejected manuscript (see book_quality_report.json).",
                        file=sys.stderr,
                    )
                    return 1
            except ValueError as e:
                print(f"Stage 6 render failed: {e}", file=sys.stderr)
                return 1

        # Scene anti-genericity gate (§8 overlay spec) — post-render quality check
        if args.enforce_scene_gate and args.render_book:
            try:
                from phoenix_v4.qa.scene_anti_genericity_gate import enforce_scene_gate

                # Extract rendered chapter texts from the plan output
                chapter_proses: list[str] = []
                prose_map = out.get("prose_map") or {}
                chapter_slot_seq = out.get("chapter_slot_sequence", [])
                for ch_idx, slots in enumerate(chapter_slot_seq):
                    ch_text_parts = []
                    for slot_label in (slots if isinstance(slots, list) else [slots]):
                        key = f"{ch_idx}:{slot_label}"
                        prose = prose_map.get(key, "")
                        if prose:
                            ch_text_parts.append(prose)
                    if ch_text_parts:
                        chapter_proses.append("\n\n".join(ch_text_parts))

                if chapter_proses:
                    scene_result = enforce_scene_gate(
                        chapter_proses,
                        mode=args.scene_gate_mode,
                    )
                    scene_report_dir = REPO_ROOT / "artifacts" / "scene_gate"
                    scene_report_dir.mkdir(parents=True, exist_ok=True)
                    scene_report_path = scene_report_dir / f"{out.get('plan_hash', 'book')}.json"
                    scene_report_path.write_text(
                        json.dumps(
                            {
                                "status": scene_result.status,
                                "mode": scene_result.mode,
                                "blocking": scene_result.blocking,
                                "errors": scene_result.report.errors,
                                "warnings": scene_result.report.warnings,
                                "metrics": scene_result.report.metrics,
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
                    if scene_result.blocking:
                        print(f"Scene anti-genericity gate FAILED. Report: {scene_report_path}", file=sys.stderr)
                        for e in scene_result.report.errors:
                            print(f"  - {e}", file=sys.stderr)
                        return 1
                    if scene_result.report.warnings:
                        for w in scene_result.report.warnings:
                            print(f"Scene gate warning: {w}", file=sys.stderr)
                    print(f"Scene anti-genericity gate {scene_result.status}. Report: {scene_report_path}", file=sys.stderr)
                else:
                    print("Scene gate skipped: no chapter prose available.", file=sys.stderr)
            except Exception as e:
                print(f"Scene anti-genericity gate error: {e}", file=sys.stderr)
                return 1

        # --- Post-render quality gates (chapter flow summary, craft) ---
        if args.out and args.render_book and gates_run:
            _post_render_exit = _run_post_render_quality_gates(
                out=out,
                render_dir=render_dir,
                written=written,
                canonical_persona=canonical_persona,
                canonical_topic=canonical_topic,
                atoms_root=atoms_root,
                gates_hard=gates_hard,
            )
            if _post_render_exit is not None:
                return _post_render_exit
        # EI V2 parallel comparison (advisory; V1 remains authoritative)
        if args.ei_v2_compare:
            try:
                from phoenix_v4.quality.ei_parallel_adapter import (
                    compare_slot,
                    build_pipeline_comparison,
                    write_comparison_report,
                )
                from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
                from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan

                v2_cfg = load_ei_v2_config()
                v1_cfg = {}  # V1 loads its own config from ei_registry
                try:
                    v1_cfg_path = REPO_ROOT / "config" / "source_of_truth" / "enlightened_intelligence_registry.yaml"
                    if v1_cfg_path.exists() and yaml:
                        v1_cfg = yaml.safe_load(v1_cfg_path.read_text(encoding="utf-8")) or {}
                except Exception:
                    pass

                prose_result = resolve_prose_for_plan(out, atoms_root=atoms_root, locale=out.get("locale"))
                prose_map = prose_result.prose_map

                book_thesis = f"{canonical_topic} for {canonical_persona}"
                chapter_thesis_map = out.get("chapter_thesis") or {}
                chapter_bestseller_structures = out.get("chapter_bestseller_structures") or []
                chapter_slot_seq = out.get("chapter_slot_sequence", [])
                atom_ids_list = out.get("atom_ids", [])
                band_seq = out.get("dominant_band_sequence", [])
                emotional_roles = out.get("emotional_role_sequence", [])

                slot_comparisons = []
                atom_idx = 0
                for ch_idx, slots in enumerate(chapter_slot_seq):
                    chapter_prose_parts = []
                    chapter_candidates_by_slot = []

                    for si, slot_type in enumerate(slots):
                        if atom_idx >= len(atom_ids_list):
                            break
                        aid = atom_ids_list[atom_idx]
                        prose = prose_map.get(aid, "")
                        chapter_prose_parts.append(prose)
                        chapter_candidates_by_slot.append((slot_type, si, aid, prose))
                        atom_idx += 1

                    chapter_text = "\n\n".join(chapter_prose_parts)
                    band = band_seq[ch_idx] if ch_idx < len(band_seq) else None
                    role = emotional_roles[ch_idx] if ch_idx < len(emotional_roles) else ""
                    # EI v2: use chapter thesis when present (for learning and thesis alignment)
                    thesis_ch = chapter_thesis_map.get(ch_idx + 1) if isinstance(chapter_thesis_map, dict) else None
                    thesis = (thesis_ch or "").strip() or book_thesis
                    bestseller_structure = chapter_bestseller_structures[ch_idx] if ch_idx < len(chapter_bestseller_structures) else None
                    arc_intent = {
                        "band": band,
                        "emotional_role": role,
                        "chapter_index": ch_idx,
                        "chapter_thesis": thesis_ch,
                        "bestseller_structure": bestseller_structure,
                    }

                    for slot_type, si, aid, prose in chapter_candidates_by_slot:
                        candidates_raw = [{"id": aid, "text": prose, "meta": {}}]
                        try:
                            result = compare_slot(
                                slot=slot_type,
                                chapter_index=ch_idx,
                                slot_index=si,
                                candidates_raw=candidates_raw,
                                persona_id=canonical_persona,
                                topic_id=canonical_topic,
                                thesis=thesis,
                                v1_cfg=v1_cfg,
                                v2_cfg=v2_cfg,
                                selector_key=f"ei:{slot_type}:ch{ch_idx}:{canonical_persona}:{canonical_topic}",
                                teacher_mode=teacher_mode,
                                chapter_text=chapter_text,
                                arc_intent=arc_intent,
                            )
                            slot_comparisons.append(result)
                        except Exception as exc:
                            print(f"EI V2 compare failed at ch{ch_idx} {slot_type}: {exc}", file=sys.stderr)

                comparison = build_pipeline_comparison(
                    slot_comparisons,
                    plan_hash=out.get("plan_hash", ""),
                    persona_id=canonical_persona,
                    topic_id=canonical_topic,
                )
                ei_v2_dir = REPO_ROOT / "artifacts" / "ei_v2"
                report_path = write_comparison_report(comparison, ei_v2_dir)
                print(f"EI V2 comparison: {report_path}")
                print(
                    f"  Slots compared: {comparison.total_slots} | "
                    f"Agreement: {comparison.agreement_rate * 100:.0f}% | "
                    f"Safety flags: {len(comparison.v2_safety_flags)} | "
                    f"TTS issues: {len(comparison.v2_tts_issues)} | "
                    f"Dedup flags: {len(comparison.v2_dedup_flags)} | "
                    f"Arc issues: {len(comparison.v2_arc_issues)}"
                )
            except Exception as exc:
                print(f"EI V2 comparison failed (non-blocking): {exc}", file=sys.stderr)
    else:
        print(json.dumps(out, indent=2))
    if not getattr(args, "no_job_check", False):
        from scripts.pipeline.advance_stage import mark_pipeline_finished

        mark_pipeline_finished(ebook_job_ws, "ebook")
    return 0


if __name__ == "__main__":
    sys.exit(main())

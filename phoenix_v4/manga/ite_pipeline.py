"""
Implicit Therapeutic Engine — shared pipeline logic for manga scripts.

Used by scripts/manga/ite_*.py and chapter_runner integration.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterator, Mapping

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_ite_merged_config(path: Path | None = None) -> dict[str, Any]:
    """Load ``config/manga/ite_config.yaml`` (empty dict if missing)."""
    p = path or (REPO_ROOT / "config" / "manga" / "ite_config.yaml")
    if not p.exists() or yaml is None:
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def iter_panels_from_chapter(chapter: Mapping[str, Any]) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (global_index, panel_dict) in reading order."""
    idx = 0
    for page in chapter.get("pages") or []:
        for panel in page.get("panels") or []:
            yield idx, panel
            idx += 1


def _get_band(panel: Mapping[str, Any]) -> int:
    for k in ("emotional_band", "emotional_intensity", "intensity_band"):
        v = panel.get(k)
        if v is not None:
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
    return 0


def annotate_panel_breath(
    chapter: dict[str, Any],
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Enrich chapter JSON with ``breath_phase`` on panels and ``breath_sequences`` summary.

    Cycle (~10s target): inhale → hold → exhale → pause (gutter marker on following transition).
    """
    cfg = cfg or load_ite_merged_config()
    be = cfg.get("breath_engine") or {}
    min_seq = int(be.get("placement_rules", {}).get("min_sequences_per_chapter", 1))
    first_page = int(be.get("placement_rules", {}).get("first_sequence_min_page", 4))
    mandatory_after = int(be.get("placement_rules", {}).get("mandatory_after_emotional_band_min", 4))
    genre = str(chapter.get("genre") or "").lower()
    max_seq = int(be.get("placement_rules", {}).get("max_sequences_per_chapter", 4))
    if genre == "iyashikei":
        max_seq = int(be.get("placement_rules", {}).get("iyashikei_max_sequences", 6))
    elif genre == "horror":
        max_seq = int(be.get("placement_rules", {}).get("horror_max_sequences", 1))

    out = json.loads(json.dumps(chapter))
    pages = out.get("pages") or []
    flat: list[dict[str, Any]] = []
    for page in pages:
        pn = int(page.get("page_number") or 1)
        for panel in page.get("panels") or []:
            p = dict(panel)
            p["_page_number"] = pn
            flat.append(p)

    if not flat:
        out["breath_sequences"] = []
        return out

    n = len(flat)
    for i, p in enumerate(flat):
        p.setdefault("width_pct", 15.0 + (i % 5) * 8.0)

    sequences: list[dict[str, Any]] = []
    used = set()
    seq_id = 0

    def _emit_at(start_idx: int, reason: str) -> None:
        nonlocal seq_id
        # Distinct six-panel window: 3 inhale + hold + 2 exhale (pause after final exhale).
        if len(sequences) >= max_seq or start_idx < 0 or start_idx + 5 >= n:
            return
        window = list(range(start_idx, start_idx + 6))
        if any(i in used for i in window):
            return
        seq_id += 1
        inhale_idxs = window[:3]
        hold_idx = window[3]
        exh_a, exh_b = window[4], window[5]
        for j in window:
            used.add(j)
        phases_present = ["inhale", "hold", "exhale", "pause"]
        for j, ph in zip(inhale_idxs, ["inhale", "inhale", "inhale"]):
            flat[j]["breath_phase"] = ph
            flat[j]["breath_sequence_id"] = seq_id
        flat[hold_idx]["breath_phase"] = "hold"
        flat[hold_idx]["breath_sequence_id"] = seq_id
        for j in (exh_a, exh_b):
            flat[j]["breath_phase"] = "exhale"
            flat[j]["breath_sequence_id"] = seq_id
        flat[exh_b]["breath_pause_after"] = True
        sequences.append({
            "sequence_id": seq_id,
            "start_panel_index": start_idx,
            "reason": reason,
            "phases_present": phases_present,
            "panel_indices": window,
            "valid": True,
        })

    # Mandatory after high intensity (first eligible)
    for i, p in enumerate(flat):
        pn = int(p.get("_page_number") or 1)
        if _get_band(p) >= mandatory_after and pn >= first_page:
            _emit_at(i, "post_high_intensity")
            break

    # Resolution / tail: ensure minimum count
    tail_start = max(0, int(n * 0.72))
    for i in range(tail_start, n):
        if len(sequences) >= min_seq:
            break
        pn = int(flat[i].get("_page_number") or 1)
        if pn >= first_page:
            _emit_at(i, "resolution_tail")
            break

    if len(sequences) < min_seq and n >= 6:
        placed = False
        for s in range(max(0, n - 6), -1, -1):
            before = len(sequences)
            _emit_at(s, "chapter_tail_fallback")
            if len(sequences) > before:
                placed = True
                break
        if not placed:
            _emit_at(0, "chapter_start_fallback")

    # Re-pack pages
    for page in pages:
        plist = page.get("panels") or []
        for j, panel in enumerate(plist):
            pid = str(panel.get("panel_id") or "")
            match = next((x for x in flat if str(x.get("panel_id")) == pid), None)
            if match:
                if "breath_phase" in match:
                    panel["breath_phase"] = match["breath_phase"]
                    panel["breath_sequence_id"] = match.get("breath_sequence_id")
                if match.get("breath_pause_after"):
                    panel["breath_pause_after"] = True

    out["breath_sequences"] = sequences
    out["artifact_type"] = out.get("artifact_type") or "chapter_ite_enriched"
    return out


def build_color_arc(
    chapter: Mapping[str, Any],
    panel_image_paths: Mapping[str, str | Path] | None,
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Per-panel color temperature targets and FFmpeg colorbalance-style params (stub gains)."""
    cfg = cfg or load_ite_merged_config()
    ca = cfg.get("color_arc") or {}
    phases = list(ca.get("phases") or [])
    genre = str(chapter.get("genre") or "").lower()
    overrides = (ca.get("genre_overrides") or {}).get(genre) or {}

    flat: list[dict[str, Any]] = []
    for page in chapter.get("pages") or []:
        for panel in page.get("panels") or []:
            flat.append(dict(panel))

    total = len(flat) or 1
    panels_out: list[dict[str, Any]] = []

    bias_k = float(overrides.get("global_warm_bias_k") or 0)
    cool_bias = float(overrides.get("phase_cool_bias_k") or 0)

    for i, panel in enumerate(flat):
        pct = 100.0 * (i / max(1, total - 1)) if total > 1 else 0.0
        target_k = 4500.0
        for ph in phases:
            lo, hi = ph.get("pct_range") or [0, 100]
            if float(lo) <= pct <= float(hi):
                tc = ph.get("temp_center_k") or 4500
                target_k = float(tc) + bias_k
                if genre == "horror" and pct >= 60:
                    target_k += cool_bias
                break
        # Map Kelvin-ish to rs/gs/bs gains (very rough heuristic)
        warm_norm = (6500.0 - min(6500.0, max(2500.0, target_k))) / 4000.0
        rs = round(0.08 * warm_norm, 4)
        bs = round(-0.06 * warm_norm, 4)
        gs = round(0.02 * (0.5 - warm_norm), 4)
        entry = {
            "panel_id": str(panel.get("panel_id") or f"panel_{i}"),
            "chapter_position_pct": round(pct, 2),
            "color_temp_target": round(target_k, 1),
            "ffmpeg_colorbalance": {"rs": rs, "gs": gs, "bs": bs},
        }
        pid = entry["panel_id"]
        if panel_image_paths and pid in panel_image_paths:
            entry["image_path"] = str(panel_image_paths[pid])
        panels_out.append(entry)

    return {
        "schema_version": "1.0.0",
        "artifact_type": "ite_color_arc",
        "genre": genre,
        "panels": panels_out,
    }


def annotate_gutter_therapy(
    chapter: dict[str, Any],
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assign ``gutter_class`` per panel (applied after panel in transition list)."""
    cfg = cfg or load_ite_merged_config()
    gu = cfg.get("gutter") or {}
    rules = gu.get("transition_rules") or {}
    max_tight = int(rules.get("max_consecutive_tight", 3))
    post4 = str(rules.get("post_band4_min_class", "wide")).lower()
    post5 = str(rules.get("post_band5_min_class", "breath")).lower()

    class_rank = {"tight": 0, "standard": 1, "wide": 2, "breath": 3, "page_break": 4}
    min_rank4 = class_rank.get(post4, 2)
    min_rank5 = class_rank.get(post5, 3)

    out = json.loads(json.dumps(chapter))
    transitions: list[dict[str, Any]] = []
    tight_run = 0
    page_count = len(out.get("pages") or [])
    panel_global = 0

    for pi, page in enumerate(out.get("pages") or []):
        panels = page.get("panels") or []
        page_num = int(page.get("page_number") or pi + 1)
        for idx, panel in enumerate(panels):
            band = _get_band(panel)
            nxt = panels[idx + 1] if idx + 1 < len(panels) else None
            phase = str(panel.get("breath_phase") or "")
            if phase == "exhale" and panel.get("breath_pause_after"):
                gclass = "breath"
            elif band >= 5:
                gclass = post5
            elif band >= 4:
                gclass = post4
            elif band >= 3:
                gclass = "wide"
            else:
                gclass = "standard"

            if gclass == "tight":
                tight_run += 1
                if tight_run > max_tight:
                    gclass = "standard"
                    tight_run = 0
            else:
                tight_run = 0

            res_threshold_page = max(1, int(math.ceil(page_count * 0.75)))
            if page_num >= res_threshold_page and gclass == "tight" and rules.get("resolution_forbid_tight", True):
                gclass = "standard"

            panel["gutter_after_class"] = gclass
            transitions.append({
                "after_panel_index": panel_global,
                "after_panel_id": str(panel.get("panel_id") or ""),
                "gutter_class": gclass,
                "emotional_band_after": band,
            })
            if nxt is not None:
                panel["gutter_class_to_next"] = gclass
            panel_global += 1

    out["gutter_transitions"] = transitions
    out["gutter_rules"] = {
        "post_band4_min_class": post4,
        "post_band5_min_class": post5,
        "max_consecutive_tight": max_tight,
    }
    return out


def _box_count_fd(image_path: Path) -> tuple[float | None, str]:
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None, "numpy_pil_unavailable"

    try:
        im = Image.open(image_path).convert("L")
        arr = np.asarray(im, dtype=np.float64)
        h, w = arr.shape
        sizes = []
        counts = []
        side = min(h, w)
        n_bins = 8
        for k in range(2, n_bins + 1):
            step = max(1, side // k)
            boxes = 0
            for y in range(0, h, step):
                for x in range(0, w, step):
                    slab = arr[y : y + step, x : x + step]
                    if slab.size == 0:
                        continue
                    if float(np.max(slab)) - float(np.min(slab)) > 15:
                        boxes += 1
            if boxes > 0:
                sizes.append(step)
                counts.append(boxes)
        if len(counts) < 2:
            return None, "insufficient_variation"
        xs = [math.log(1.0 / s) for s in sizes]
        ys = [math.log(c) for c in counts]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(xs, ys))
        den = sum((xi - mean_x) ** 2 for xi in xs) or 1e-9
        slope = num / den
        fd = 1.0 + max(0.0, min(2.0, slope))
        return float(fd), "ok"
    except Exception as exc:
        return None, str(exc)[:80]


def _panel_category(panel: Mapping[str, Any]) -> str:
    for k in ("background_category", "fractal_category", "category"):
        v = panel.get(k)
        if v:
            return str(v).lower()
    return ""


def run_fractal_check(
    panel_paths: Mapping[str, str | Path],
    chapter: Mapping[str, Any] | None,
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = cfg or load_ite_merged_config()
    frac = cfg.get("fractal") or {}
    lo, hi = frac.get("target_fd_range", [1.3, 1.5])
    lo, hi = float(lo), float(hi)
    warn_lo, warn_hi = frac.get("warn_fd_range", [1.1, 1.7])
    warn_lo, warn_hi = float(warn_lo), float(warn_hi)
    allowed = {str(x).lower() for x in (frac.get("source_categories") or [])}

    id_to_panel: dict[str, dict[str, Any]] = {}
    if chapter:
        for _i, p in iter_panels_from_chapter(chapter):
            pid = str(p.get("panel_id") or "")
            if pid:
                id_to_panel[pid] = dict(p)

    rows: list[dict[str, Any]] = []
    stub = False
    for pid, raw_path in panel_paths.items():
        path = Path(raw_path)
        cat = _panel_category(id_to_panel.get(str(pid), {}))
        if allowed and cat and cat not in allowed:
            cat_ok = False
        else:
            cat_ok = not allowed or not cat or cat in allowed
        fd, note = _box_count_fd(path)
        if note == "numpy_pil_unavailable":
            stub = True
            fd_est = 1.4
            compliant = cat_ok
            note = "stub_no_deps"
        elif fd is None:
            fd_est = 1.4
            compliant = False
        else:
            fd_est = fd
            compliant = cat_ok and lo <= fd_est <= hi
        warn = fd is not None and (fd_est < warn_lo or fd_est > warn_hi)
        rows.append({
            "panel_id": str(pid),
            "fd_estimate": round(fd_est, 4) if fd_est is not None else None,
            "source_category": cat or "unknown",
            "compliant": compliant,
            "warn_out_of_band": warn,
            "note": note,
        })

    # RELEASE/RESOLVE heuristic: final 30% panels must have ≥1 nature fractal compliant
    blocker_missing = False
    if chapter:
        flat = [p for _i, p in iter_panels_from_chapter(chapter)]
        n = len(flat)
        tail = flat[max(0, int(n * 0.7)) :] if n else []
        nature_tail = [
            p for p in tail
            if _panel_category(p)
            in {"arboreal", "aquatic", "atmospheric", "geological", "nature", "botanical"}
        ]
        found = False
        for p in nature_tail:
            pid = str(p.get("panel_id") or "")
            r = next((x for x in rows if x["panel_id"] == pid), None)
            if r and r.get("compliant"):
                found = True
                break
        if nature_tail and not found:
            blocker_missing = True

    return {
        "schema_version": "1.0.0",
        "artifact_type": "ite_fractal_report",
        "stub_mode": stub,
        "panels": rows,
        "blocker_no_fractal_nature_in_release_resolve": blocker_missing,
    }


def _gutter_rank(cls: str, gu_cfg: Mapping[str, Any]) -> float:
    w = gu_cfg.get("width_classes") or {}
    key = str(cls).lower()
    if key in w and isinstance(w[key], dict):
        return float(w[key].get("multiplier", 1.0))
    return {"tight": 0.5, "standard": 1.0, "wide": 2.0, "breath": 4.0, "page_break": 5.0}.get(key, 1.0)


def _collect_dialogue(chapter: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for page in chapter.get("pages") or []:
        for panel in page.get("panels") or []:
            dlg = panel.get("dialogue")
            if isinstance(dlg, list):
                parts.extend(str(x) for x in dlg)
            elif dlg:
                parts.append(str(dlg))
    return " ".join(parts)


def run_ite_qc(
    *,
    chapter_enriched: Mapping[str, Any],
    color_arc: Mapping[str, Any] | None,
    fractal_report: Mapping[str, Any] | None,
    breath_doc: Mapping[str, Any] | None = None,
    soundtrack: Mapping[str, Any] | None = None,
    animation_plan: Mapping[str, Any] | None = None,
    sabido_map: Mapping[str, Any] | None = None,
    cfg: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """ITE gates T-01 … T-20 per IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC §15."""
    cfg = cfg or load_ite_merged_config()
    gu = cfg.get("gutter") or {}
    qc_extra = cfg.get("ite_qc") or {}
    res_temp_k = float(qc_extra.get("resolution_temp_min_k", 5500))
    res_sat_max = float(qc_extra.get("resolution_sat_max_pct", 55))

    breath_data = breath_doc or chapter_enriched
    sequences = list(breath_data.get("breath_sequences") or [])
    transitions = list(chapter_enriched.get("gutter_transitions") or [])

    gates: list[dict[str, Any]] = []

    def add(gid: str, level: str, passed: bool, detail: str) -> None:
        gates.append({"id": gid, "level": level, "passed": passed, "detail": detail})

    blocking_failed = 0

    # T-01 post band-4 gutter ≥ processing (2.0x)
    t01_ok = True
    for tr in transitions:
        band_after = int(tr.get("emotional_band_after") or 0)
        if band_after >= 4:
            rk = _gutter_rank(str(tr.get("gutter_class") or "standard"), gu)
            if rk < 2.0 - 1e-6:
                t01_ok = False
                break
    add("T-01", "BLOCKER", t01_ok, "post band-4 gutter multiplier >= 2.0")
    blocking_failed += 0 if t01_ok else 1

    # T-02 post band-5 ≥ therapeutic 3.0x
    t02_ok = True
    for tr in transitions:
        if int(tr.get("emotional_band_after") or 0) >= 5:
            rk = _gutter_rank(str(tr.get("gutter_class") or "standard"), gu)
            if rk < 3.0 - 1e-6:
                t02_ok = False
                break
    add("T-02", "BLOCKER", t02_ok, "post band-5 gutter multiplier >= 3.0")
    blocking_failed += 0 if t02_ok else 1

    # T-03 consecutive tight > 5 (spec: BLOCKER)
    classes = [str(t.get("gutter_class") or "standard").lower() for t in transitions]
    run = max_run = 0
    for c in classes:
        if c == "tight":
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    t03_ok = max_run <= 5
    add("T-03", "BLOCKER", t03_ok, f"max consecutive tight = {max_run}")
    blocking_failed += 0 if t03_ok else 1

    # T-04 stealth vocabulary in dialogue
    from phoenix_v4.quality.ei_v2.visual_therapeutic import vt_stealth
    from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

    ei = load_ei_v2_config()
    dlg = _collect_dialogue(chapter_enriched)
    t04_ok = vt_stealth(dlg, cfg=ei) >= 0.999
    add("T-04", "BLOCKER", t04_ok, "no forbidden terms in dialogue")
    blocking_failed += 0 if t04_ok else 1

    # T-05 lyrics in resolution soundtrack
    t05_ok = True
    if soundtrack:
        lyrics_flag = bool(soundtrack.get("lyrics_in_resolution"))
        if lyrics_flag:
            t05_ok = False
    add("T-05", "BLOCKER", t05_ok, "no lyrics in resolution (if soundtrack present)")
    blocking_failed += 0 if t05_ok else 1

    # T-06 video ending arousal
    t06_ok = True
    if animation_plan:
        shots = animation_plan.get("shots") or []
        if shots and float(animation_plan.get("duration_s") or 0) >= 60:
            last_cut = shots[-1].get("cut_period_s")
            if last_cut is not None and float(last_cut) < 4.0:
                t06_ok = False
    add("T-06", "BLOCKER", t06_ok, "long-form video does not end on <4s cuts")
    blocking_failed += 0 if t06_ok else 1

    warn_failed = 0

    # T-07 breath sequence minimum (WARN if 0)
    t07_ok = len(sequences) >= 1
    add("T-07", "WARN", t07_ok, f"breath_sequences={len(sequences)}")
    warn_failed += 0 if t07_ok else 1

    # T-08 resolution color temp
    t08_ok = True
    if color_arc:
        plist = list(color_arc.get("panels") or [])
        if plist:
            n = len(plist)
            res_slice = plist[int(n * 0.65) : int(n * 0.85)] or plist[-max(1, n // 5) :]
            avg_k = sum(float(p.get("color_temp_target") or 0) for p in res_slice) / max(1, len(res_slice))
            t08_ok = avg_k >= res_temp_k
    add("T-08", "WARN", t08_ok, "resolution mean color temp")
    warn_failed += 0 if t08_ok else 1

    # T-09 resolution saturation (stub — no saturation in color_arc JSON)
    t09_ok = True
    add("T-09", "WARN", t09_ok, "resolution saturation <= cap (stub if absent)")

    # T-10 fractal hold
    t10_ok = True
    if breath_data and fractal_report:
        fds = {r["panel_id"]: r for r in (fractal_report.get("panels") or [])}
        for page in breath_data.get("pages") or []:
            for panel in page.get("panels") or []:
                if str(panel.get("breath_phase")) == "hold":
                    pid = str(panel.get("panel_id") or "")
                    row = fds.get(pid) or {}
                    if not row.get("compliant"):
                        t10_ok = False
    add("T-10", "WARN", t10_ok, "hold panels fractal FD in band")
    warn_failed += 0 if t10_ok else 1

    # T-11 calming tempo
    t11_ok = True
    if soundtrack:
        bpm = soundtrack.get("calming_avg_bpm")
        if bpm is not None and float(bpm) > 78:
            t11_ok = False
    add("T-11", "WARN", t11_ok, "calming tempo <= 78 BPM when specified")

    # T-12 strategic silence
    t12_ok = True
    if soundtrack:
        sil = soundtrack.get("silence_total_s")
        dur = float(soundtrack.get("duration_s") or 0)
        if sil is not None and dur >= 300 and float(sil) < 8.0:
            t12_ok = False
    add("T-12", "WARN", t12_ok, "silence budget per 5min (when audio metadata present)")

    # T-13 pentatonic ratio
    t13_ok = True
    if soundtrack:
        pr = soundtrack.get("pentatonic_ratio")
        if pr is not None and float(pr) < 0.5:
            t13_ok = False
    add("T-13", "WARN", t13_ok, "calming pentatonic mix (when specified)")

    # T-14 phase saturation monotonic (stub pass)
    t14_ok = True
    add("T-14", "WARN", t14_ok, "phase 2→4 saturation monotonic (stub)")

    # T-15 tight in final 25% — WARN in spec
    page_count = len(chapter_enriched.get("pages") or [])
    res_page = max(1, int(math.ceil(page_count * 0.75)))
    t15_ok = True
    for page in chapter_enriched.get("pages") or []:
        pn = int(page.get("page_number") or 0)
        if pn < res_page:
            continue
        for panel in page.get("panels") or []:
            if str(panel.get("gutter_after_class") or "").lower() == "tight":
                t15_ok = False
    add("T-15", "WARN", t15_ok, "no tight gutter in final 25% of pages")
    warn_failed += 0 if t15_ok else 1

    # INFO gates
    add("T-16", "INFO", True, "bilateral layout ratio stub 0.6")
    add("T-17", "INFO", True, "kishotenketsu rhythm stub 0.65")
    hz = None
    if soundtrack:
        hz = soundtrack.get("tuning_hz")
    add("T-18", "INFO", hz == 432, f"tuning_hz={hz}")

    artifacts_bundle = {
        "breath": breath_data,
        "color_arc": color_arc or {},
        "fractal": fractal_report or {},
        "gutter": {"transitions": transitions, "pages": chapter_enriched.get("pages")},
        "chapter": chapter_enriched,
    }
    from phoenix_v4.quality.ei_v2.visual_therapeutic import compute_visual_therapeutic_scores

    vt_scores = compute_visual_therapeutic_scores(artifacts_bundle, dialogue_text=dlg, cfg=ei)
    ite_score = float(vt_scores.get("ite_score") or 0.0)
    pass_min = float(qc_extra.get("composite_pass_min", 0.5))
    add("T-19", "INFO", ite_score >= pass_min, f"ITE_score={ite_score} dims={vt_scores}")

    roles = list((sabido_map or {}).keys()) if sabido_map else []
    add("T-20", "INFO", len(roles) >= 3, f"sabido roles present: {roles}")

    fractal_block = bool((fractal_report or {}).get("blocker_no_fractal_nature_in_release_resolve"))
    if fractal_block:
        blocking_failed += 1
        gates.append({
            "id": "T-FRACTAL-NATURE",
            "level": "BLOCKER",
            "passed": False,
            "detail": "no compliant fractal nature panel in release/resolve tail",
        })

    overall_pass = blocking_failed == 0
    return {
        "schema_version": "1.0.0",
        "artifact_type": "ite_qc_report",
        "ITE_score": ite_score,
        "dimensions": {k: vt_scores[k] for k in ("vt_parasympathetic", "vt_processing", "vt_somatic", "vt_stealth") if k in vt_scores},
        "gates": gates,
        "blocker_fail_count": blocking_failed,
        "warn_fail_count": warn_failed,
        "passed": overall_pass,
        "fractal_blocker": fractal_block,
    }


def ite_prompt_suffix(cfg: Mapping[str, Any] | None = None) -> str:
    """Short stealth-safe visual guidance appended to panel prompts."""
    cfg = cfg or load_ite_merged_config()
    lines = [
        "ITE: implicit pacing — vary panel scale and gutters; prefer organic backgrounds;",
        "natural branching detail; avoid grid, glitch, or tiled mechanical patterns.",
    ]
    fractal = cfg.get("fractal") or {}
    if fractal.get("source_categories"):
        lines.append(f"fractal-friendly categories: {', '.join(fractal['source_categories'])}.")
    return " ".join(lines)


# ── Schema validation helpers ───────────────────────────────────────


def validate_ite_color_arc(data: dict[str, Any]) -> None:
    """Validate an ITE color arc artifact against ``schemas/manga/ite_color_arc.schema.json``."""
    from phoenix_v4.manga.models.validation import validate_instance
    validate_instance(data, "ite_color_arc")


def validate_ite_fractal_report(data: dict[str, Any]) -> None:
    """Validate an ITE fractal report against ``schemas/manga/ite_fractal_report.schema.json``."""
    from phoenix_v4.manga.models.validation import validate_instance
    validate_instance(data, "ite_fractal_report")


def validate_ite_qc_report(data: dict[str, Any]) -> None:
    """Validate an ITE QC report against ``schemas/manga/ite_qc_report.schema.json``."""
    from phoenix_v4.manga.models.validation import validate_instance
    validate_instance(data, "ite_qc_report")

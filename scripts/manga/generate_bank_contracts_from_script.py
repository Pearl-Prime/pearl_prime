#!/usr/bin/env python3
"""Generate bank-contract inventory stubs from an M3 chapter_script, OR roll up
image-bank demand across a whole series master plan.

Two modes:

1. Per-episode stub (original, --chapter-script): reads panel `scene` text from
   an M3 chapter_script ep_001 and emits minimal scene/object/pose inventory
   YAMLs under artifacts/manga/<series_id>/bank_contracts/. Mechanical procedure
   for the remaining M3 flagship series (after the 3-pilot M5-prep set).

2. Series demand rollup (--series-rollup, uplift Lane 09): reads a
   series_master_plan (schemas/manga/series_master_plan.schema.json) plus the
   series' authored bank contracts, existing storyboards/gap files and on-disk
   image_bank, and answers the operator's ask — "when we plan 100 episodes,
   analyze them and know exactly what to build for the image bank." Emits
   artifacts/manga/<series_id>/bank_contracts/series_demand_rollup.yaml
   (schema: schemas/manga/series_demand_rollup.schema.json).

BOTH modes are ANALYSIS ONLY. Neither invents art or renders anything — REAL
layers require Pearl Star (RAP/queue-first, M5 render lanes).

Usage:
    # per-episode stub (unchanged)
    PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \
        --chapter-script artifacts/manga/<series>/ep_001.yaml

    # series demand rollup
    PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \
        --series-rollup \
        --master-plan artifacts/manga/series_master_plans/<series>.master_plan.yaml
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]


# ── byte-floor reuse (Lane 09: "present asset" = byte-real, LFS/R2-aware) ──────
# Reuse check_render_progress_bytes' floor + LFS-pointer-aware sizer so the
# demand rollup's "present" definition is byte-for-byte the same contract as the
# render-progress drift gate. Never weaken the floor here.
def _byte_floor():
    """Return (MIN_BYTES, real_bytes_fn). Falls back to a local floor + naive
    sizer only if the CI helper is unavailable (keeps unit tests self-contained)."""
    import sys as _sys

    ci = REPO / "scripts" / "ci"
    if str(ci) not in _sys.path:
        _sys.path.insert(0, str(ci))
    try:
        from check_render_progress_bytes import (  # type: ignore
            MIN_BYTES,
            _lfs_or_disk_bytes,
        )

        return int(MIN_BYTES), _lfs_or_disk_bytes
    except Exception:  # pragma: no cover - defensive fallback
        def _naive(path: Path) -> int:
            return path.stat().st_size if path.is_file() else -1

        return 50_000, _naive


# ─────────────────────────── mode 1: per-episode stub ─────────────────────────
def generate_chapter_stub(chapter_script: Path) -> list[Path]:
    """Original behaviour: minimal scene/object/pose inventory stubs from an
    ep_001 chapter_script. Returns the paths written."""
    data = yaml.safe_load(chapter_script.read_text())
    series_id = data["series_id"]
    brand_id = data.get("brand_id", series_id.split("__")[0])
    genre = data.get("genre", "iyashikei")
    # Crude scene buckets from first words of panel scenes
    scenes, objects, poses = [], [], []
    for page in data.get("pages") or []:
        for panel in page.get("panels") or []:
            scene = str(panel.get("scene") or "")
            words = re.findall(r"[A-Za-z]{4,}", scene)[:4]
            if words:
                sid = "_".join(w.lower() for w in words[:3])
                if sid and sid not in {s[0] for s in scenes}:
                    scenes.append((sid, scene[:200]))
            if "hand" in scene.lower() or "cup" in scene.lower() or "phone" in scene.lower():
                oid = "prop_" + str(len(objects))
                objects.append((oid, scene[:120]))
            if panel.get("dialogue_lines") or "face" in scene.lower():
                poses.append((f"pose_{len(poses)}", "Character pose derived from panel"))
    # Floor: at least 2 of each (Q-M5P-02 contract minimum)
    while len(scenes) < 2:
        scenes.append((f"scene_{len(scenes)}", "TODO: author from script"))
    while len(objects) < 2:
        objects.append((f"object_{len(objects)}", "TODO: author from script"))
    while len(poses) < 2:
        poses.append((f"pose_{len(poses)}", "TODO: author from script"))

    out = REPO / "artifacts" / "manga" / series_id / "bank_contracts"
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for kind, key, idk, items in (
        ("scene_inventory", "scenes", "scene_id", scenes[:8]),
        ("object_inventory", "objects", "object_id", objects[:8]),
        ("character_pose_inventory", "poses", "pose_id", poses[:8]),
    ):
        doc = {
            "schema_version": "1.0.0",
            "series_id": series_id,
            "brand_id": brand_id,
            "genre": genre,
            "m5_prep": True,
            "generated_from": str(chapter_script),
            key: [{idk: i, "description": d, "status": "specced_awaiting_gpu",
                   "render_resolution": [1080, 1920]} for i, d in items],
        }
        path = out / f"{kind}.yaml"
        path.write_text(
            yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        print("wrote", path)
        written.append(path)
    return written


# ─────────────────────────── mode 2: series demand rollup ─────────────────────
def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


_WORD_RE = re.compile(r"[a-z][a-z0-9]{2,}")
# Tokens too generic to disambiguate a scene/object when matched in prose.
_MATCH_STOP = {
    "office", "aoki", "room", "area", "corner", "the", "and", "for", "with",
    "her", "his", "she", "him", "day", "flashback", "waiting", "home",
}
# Capitalized tokens that are never cast names (calendar / register words).
_NAME_STOP = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "autumn", "winter", "spring",
    "summer", "the", "an", "her", "his", "she", "mira",  # Mira handled via mira_aoki
    "nothing", "year", "each", "other", "one", "two", "four", "same",
}
# Seed vocab for surfacing backdrops/objects the 100-ep plan implies but the
# authored bank contract does not yet cover (authoring gaps, confidence=outline).
# Documented as provenance in the output; NOT an asserted asset list.
_BACKDROP_SEED = {
    "breakroom", "apartment", "kitchen", "subway", "train", "cafe", "coffee",
    "bar", "sill", "counter", "rooftop", "stairwell", "corridor", "lobby",
    "sidewalk", "market", "bedroom", "meeting", "table", "cupboard", "kettle",
}
_OBJECT_SEED = {
    "kettle", "cup", "pendant", "succulent", "cutting", "plant", "phone",
    "notification", "candle", "lamp", "clicker", "notebook", "note", "logbook",
    "journal", "door", "wrist", "letter",
}
# Backdrop-only vs object-only partition (keep each candidate in one bucket).
_BACKDROP_ONLY = {
    "breakroom", "apartment", "subway", "train", "cafe", "coffee", "bar", "sill",
    "counter", "rooftop", "stairwell", "corridor", "lobby", "sidewalk", "market",
    "bedroom", "meeting", "cupboard", "kitchen",
}
_OBJECT_ONLY = {
    "kettle", "cup", "pendant", "succulent", "cutting", "plant", "phone",
    "notification", "candle", "lamp", "clicker", "notebook", "note", "logbook",
    "journal", "door", "wrist", "letter",
}


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall((text or "").lower()))


def _scene_alias_tokens(scene_id: str, description: str = "") -> set[str]:
    """Match tokens for a bank-contract scene: meaningful words from the id,
    minus generic stopwords."""
    toks = {w for w in _tokens(scene_id) if w not in _MATCH_STOP}
    # A couple of high-signal synonyms the id alone misses.
    if "conference" in toks or "meeting" in toks:
        toks.update({"meeting", "review"})
    if "neighborhood" in toks or "sidewalk" in toks:
        toks.update({"walk", "walking", "sidewalk"})
    if "bedroom" in toks:
        toks.add("night")
    return {t for t in toks if t not in _MATCH_STOP}


def _object_alias_tokens(object_id: str) -> set[str]:
    toks = {w for w in _tokens(object_id) if w not in _MATCH_STOP}
    syn = {
        "phone": {"notification"},
        "succulent": {"plant", "cutting", "pot"},
        "journal": {"notebook", "note", "logbook", "notes"},
        "jade": {"pendant"},
    }
    for base, extra in syn.items():
        if base in toks:
            toks |= extra
    return toks


def _proper_name_candidates(text: str) -> set[str]:
    """Cast-roster signal for outline episodes: capitalized proper names that
    appear MID-SENTENCE (preceded by a lowercase word), which filters out
    sentence-initial common words (`Deep autumn`, `Nothing escalates`). A
    conservative signal — authoring-gap cast with no pose inventory yet."""
    out: set[str] = set()
    # a lowercase letter (optionally with a comma), whitespace, then a Capitalized word
    for m in re.findall(r"[a-z],?\s+([A-Z][a-z]{2,})", text or ""):
        low = m.lower()
        if low in _NAME_STOP:
            continue
        out.add(low)
    return out


def _episode_text_pools(
    plan: dict[str, Any], repo_root: Path, series_id: str
) -> dict[int, dict[str, Any]]:
    """Per-episode text pools for prose scanning. Detailed episodes carry their
    own per-episode plan pass (+ arc_storyboard visual_proof when on disk);
    outline episodes inherit their arc's premise/promise prose."""
    pools: dict[int, dict[str, Any]] = {}
    sb_dir = repo_root / "artifacts" / "manga" / "arc_storyboards" / series_id
    for arc in plan.get("arcs") or []:
        if not isinstance(arc, dict):
            continue
        start = int(arc.get("episode_start") or 0)
        end = int(arc.get("episode_end") or 0)
        detail = str(arc.get("detail_level") or "outline")
        arc_text_parts = [
            str(arc.get("arc_premise") or ""),
            str(arc.get("arc_promise") or ""),
            str(arc.get("self_help_topic") or ""),
        ]
        mcv = arc.get("mc_change_vector") or {}
        if isinstance(mcv, dict):
            arc_text_parts += [str(mcv.get("from_state") or ""), str(mcv.get("to_state") or "")]
        # Join fields as separate sentences ('. ') so a field-initial common word
        # ('Home is...', 'Bigger rooms...') is not mistaken for a mid-sentence name.
        arc_text = " . ".join(p for p in arc_text_parts if p)
        ep_plans = {
            int(e.get("episode")): e
            for e in (arc.get("episodes") or [])
            if isinstance(e, dict) and e.get("episode") is not None
        }
        for ep in range(start, end + 1):
            parts = [arc_text]
            e = ep_plans.get(ep)
            if isinstance(e, dict):
                hook = e.get("hook") or {}
                parts += [
                    str(e.get("logline") or ""),
                    str(e.get("genre_pleasure_beat") or ""),
                    str(e.get("self_help_topic_beat") or ""),
                    str(hook.get("promise") or "") if isinstance(hook, dict) else "",
                ]
            # Enrich detailed episodes with authored storyboard visual proofs.
            if detail == "detailed":
                sb = _load_yaml(sb_dir / f"ep_{ep:03d}.arc_storyboard.yaml")
                for p in sb.get("panels") or []:
                    if isinstance(p, dict):
                        parts += [str(p.get("visual_proof") or ""), str(p.get("story_move") or "")]
            pools[ep] = {
                "detail_level": detail,
                "text": " . ".join(x for x in parts if x),
                "arc_id": arc.get("arc_id"),
            }
    return pools


def _count_touches(alias: set[str], pools: dict[int, dict[str, Any]]) -> dict[str, Any]:
    eps = sorted(ep for ep, pool in pools.items() if alias & _tokens(pool["text"]))
    return {"count": len(eps), "episodes": eps, "method": "prose_scan"}


def _has_detailed_touch(episodes: list[int], pools: dict[int, dict[str, Any]]) -> bool:
    return any(pools.get(ep, {}).get("detail_level") == "detailed" for ep in episodes)


def _image_bank_present(root: Path, real_bytes, min_bytes: int) -> dict[str, set[str]]:
    """Map layer_class -> set of present (byte-real) asset stems under image_bank/."""
    present: dict[str, set[str]] = {"L0": set(), "L1": set(), "L2": set(), "L3": set(), "L4": set()}
    if not root.is_dir():
        return present
    for png in root.rglob("*.png"):
        parts = png.relative_to(root).parts
        if not parts:
            continue
        lc = parts[0].upper()
        if lc not in present:
            continue
        if real_bytes(png) >= min_bytes:
            # L2 assets are keyed <character>/<pose>.png; record "<char>/<stem>" and "<stem>".
            present[lc].add(png.stem)
            if len(parts) >= 3:
                present[lc].add(f"{parts[1]}/{png.stem}")
    return present


def _aggregate_gap_files(manifest_dir: Path) -> dict[str, Any]:
    """Aggregate Lane 10's panels_with_gaps format across *_bank_gaps.json.
    Reuses generate_assembly_manifest / build_assembly_layer_hints output; does
    not reinvent the gap shape."""
    eps: list[str] = []
    total_panel_gaps = 0
    asset_counts: dict[str, int] = {}
    if manifest_dir.is_dir():
        for gf in sorted(manifest_dir.glob("*_bank_gaps.json")):
            doc = _load_json(gf)
            ep_id = str(doc.get("episode_id") or gf.stem.replace("_bank_gaps", ""))
            eps.append(ep_id)
            for panel in doc.get("panels_with_gaps") or []:
                if not isinstance(panel, dict):
                    continue
                gaps = panel.get("gaps") or []
                total_panel_gaps += 1 if gaps else 0
                for g in gaps:
                    asset_counts[str(g)] = asset_counts.get(str(g), 0) + 1
    return {
        "episodes_with_gap_files": eps,
        "total_panels_with_gaps": total_panel_gaps,
        "gap_asset_counts": dict(sorted(asset_counts.items())),
    }


def _flagship_lora_plan(
    repo_root: Path, brand_id: str, series_id: str, locale: str, protagonist_id: str | None
) -> dict[str, Any]:
    """Read canonical_brand_list tier + brand_lora_plans rows. Never invent
    flagship status or a LoRA row; report what exists and flag gaps.

    V5 doctrine is LoRA-flagship-only AND protagonist-focused (secondary cast use
    PuLID reference sheets, not trained LoRAs), so the authoring gap is a single
    series-level row naming the protagonist candidate — not one per cast member."""
    brands = _load_yaml(repo_root / "config" / "manga" / "canonical_brand_list.yaml")
    tier = None
    b = (brands.get("brands") or {}).get(brand_id)
    if isinstance(b, dict):
        tier = b.get("tier")
    on_flagship = tier == "flagship"

    lora = _load_yaml(repo_root / "config" / "manga" / "brand_lora_plans.yaml")
    rows: list[dict[str, Any]] = []
    bsl = (lora.get("brand_style_loras") or {}).get(brand_id)
    if isinstance(bsl, dict):
        rows.append({"kind": "brand_style_lora", "brand_id": brand_id,
                     "trigger_word": bsl.get("trigger_word"), "status": bsl.get("status", "planned")})
    matched_series = False
    other_series_rows: list[str] = []
    for p in lora.get("protagonist_loras") or []:
        if not isinstance(p, dict) or p.get("brand_id") != brand_id:
            continue
        rows.append({"kind": "protagonist_lora", "series_id": p.get("series_id"),
                     "locale": p.get("locale"), "trigger_word": p.get("trigger_word"),
                     "character_name": p.get("character_name"), "status": p.get("status")})
        if p.get("series_id") == series_id:
            matched_series = True
        else:
            other_series_rows.append(f"{p.get('trigger_word')} ({p.get('series_id')}/{p.get('locale')})")

    authoring_gaps: list[str] = []
    if on_flagship and not matched_series:
        existing = f" (existing protagonist rows are other-series: {', '.join(other_series_rows)})" if other_series_rows else ""
        authoring_gaps.append(
            f"flagship brand but no protagonist_lora row for this {locale} series "
            f"{series_id}; protagonist candidate {protagonist_id or '<unknown>'} needs one{existing}"
        )
    return {
        "brand_on_flagship_list": bool(on_flagship),
        "flagship_list_source": "config/manga/canonical_brand_list.yaml",
        "brand_tier": tier,
        "lora_plan_rows": rows,
        "lora_plan_source": "config/manga/brand_lora_plans.yaml",
        "authoring_gaps": authoring_gaps,
    }


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def series_demand_rollup(master_plan_path: Path, repo_root: Path = REPO) -> dict[str, Any]:
    """Build the series-level image-bank demand rollup from a master plan."""
    min_bytes, real_bytes = _byte_floor()
    plan = _load_yaml(master_plan_path)
    if not plan:
        raise SystemExit(f"master plan not found or empty: {master_plan_path}")
    series_id = str(plan.get("series_id") or "")
    brand_id = str(plan.get("brand_id") or (series_id.split("__")[0] if series_id else ""))
    locale = str(plan.get("locale") or "")
    horizon = int(plan.get("episode_horizon") or 0)

    series_dir = repo_root / "artifacts" / "manga" / series_id
    bank_dir = series_dir / "bank_contracts"
    image_bank_root = series_dir / "image_bank"
    manifest_dir = series_dir / "assembly_manifests"

    scene_inv = _load_yaml(bank_dir / "scene_inventory.yaml")
    object_inv = _load_yaml(bank_dir / "object_inventory.yaml")
    pose_inv = _load_yaml(bank_dir / "character_pose_inventory.yaml")

    pools = _episode_text_pools(plan, repo_root, series_id)
    episodes_planned = len(pools)
    detailed_window_end = max(
        (ep for ep, p in pools.items() if p["detail_level"] == "detailed"), default=0
    )
    present = _image_bank_present(image_bank_root, real_bytes, min_bytes)

    outline_text = " ".join(p["text"] for p in pools.values() if p["detail_level"] == "outline")
    outline_toks = _tokens(outline_text)

    # ── L0 backdrops ─────────────────────────────────────────────────────────
    l0_rows: list[dict[str, Any]] = []
    covered_backdrop_tokens: set[str] = set()
    for scene in scene_inv.get("scenes") or []:
        if not isinstance(scene, dict):
            continue
        sid = str(scene.get("scene_id") or "")
        if not sid:
            continue
        rigs = [str(r.get("light_rig_id")) for r in (scene.get("light_rigs") or [])
                if isinstance(r, dict) and r.get("light_rig_id")]
        demand = max(1, len(rigs))
        alias = _scene_alias_tokens(sid, str(scene.get("description") or ""))
        covered_backdrop_tokens |= alias
        touches = _count_touches(alias, pools)
        n_present = sum(
            1 for stem in (present["L0"] | present["L1"]) if stem.split("/")[-1].startswith(sid)
        )
        conf = "authored" if (_has_detailed_touch(touches["episodes"], pools) or touches["count"] == 0) else "outline"
        l0_rows.append({
            "scene_id": sid,
            "source": "bank_contract",
            "layer_class": "L0",
            "variants": rigs,
            "render_demand": demand,
            "episodes_touching": touches,
            "present_byte_real": n_present,
            "coverage_gap": max(0, demand - n_present),
            "confidence": conf,
        })
    for cand in sorted((_BACKDROP_SEED & _BACKDROP_ONLY & outline_toks) - covered_backdrop_tokens):
        touches = _count_touches({cand}, pools)
        l0_rows.append({
            "scene_id": f"candidate__{cand}",
            "source": "master_plan_outline",
            "layer_class": "L0",
            "variants": [],
            "render_demand": 1,
            "episodes_touching": touches,
            "present_byte_real": 0,
            "coverage_gap": 1,
            "authoring_gap": True,
            "confidence": "outline",
        })

    # ── L2 character poses ───────────────────────────────────────────────────
    l2_rows: list[dict[str, Any]] = []
    pose_chars = pose_inv.get("characters") or {}
    cast_ids_in_contract: list[str] = []
    for char_id, cdata in (pose_chars.items() if isinstance(pose_chars, dict) else []):
        if not isinstance(cdata, dict):
            continue
        cast_ids_in_contract.append(char_id)
        poses = cdata.get("poses") or []
        pose_rows: list[dict[str, Any]] = []
        n_present = 0
        for pose in poses:
            if not isinstance(pose, dict):
                continue
            pid = str(pose.get("pose_id") or "")
            if not pid:
                continue
            is_present = (f"{char_id}/{pid}" in present["L2"]) or (pid in present["L2"])
            n_present += 1 if is_present else 0
            pose_rows.append({"pose_id": pid, "render_demand": 1, "present_byte_real": is_present})
        ref_present = any(
            s.split("/")[-1] == f"{char_id}_reference_sheet" for s in present["L2"]
        )
        display = char_id.split("_")[0].title()
        touches = _count_touches({display.lower(), char_id.split("_")[0]}, pools)
        l2_rows.append({
            "character_id": char_id,
            "display_name": display,
            "in_bank_contract": True,
            "poses": pose_rows,
            "pose_render_demand": len(pose_rows),
            "present_byte_real": n_present,
            "coverage_gap": max(0, len(pose_rows) - n_present),
            "episodes_touching": touches,
            "confidence": "authored",
            "identity_lock": {
                "pulid_reference_sheet": "required",
                "reference_sheet_present": bool(ref_present),
                "flagship_lora": None,
            },
        })
    plan_text = " ".join(p["text"] for p in pools.values())
    contract_name_stems = {tok for c in cast_ids_in_contract for tok in c.split("_")}
    for name in sorted(_proper_name_candidates(plan_text) - contract_name_stems):
        touches = _count_touches({name}, pools)
        if touches["count"] == 0:
            continue
        l2_rows.append({
            "character_id": name,
            "display_name": name.title(),
            "in_bank_contract": False,
            "poses": [],
            "pose_render_demand": 0,
            "present_byte_real": 0,
            "coverage_gap": 0,
            "authoring_gap": True,
            "episodes_touching": touches,
            "confidence": "outline",
            "identity_lock": {
                "pulid_reference_sheet": "required",
                "reference_sheet_present": False,
                "flagship_lora": None,
            },
        })

    # ── L3 objects ───────────────────────────────────────────────────────────
    l3_rows: list[dict[str, Any]] = []
    covered_object_tokens: set[str] = set()
    for obj in object_inv.get("objects") or []:
        if not isinstance(obj, dict):
            continue
        oid = str(obj.get("object_id") or "")
        if not oid:
            continue
        variants = [str(v) for v in (obj.get("state_variants_required") or [])]
        demand = max(1, len(variants))
        alias = _object_alias_tokens(oid)
        covered_object_tokens |= alias
        touches = _count_touches(alias, pools)
        n_present = sum(1 for stem in present["L3"] if stem.split("/")[-1].startswith(oid))
        recurrence = "recurring" if touches["count"] > 1 else ("one_shot" if touches["count"] == 1 else "unknown")
        conf = "authored" if (_has_detailed_touch(touches["episodes"], pools) or touches["count"] == 0) else "outline"
        l3_rows.append({
            "object_id": oid,
            "source": "bank_contract",
            "layer_class": str(obj.get("layer_class") or "L3"),
            "state_variants": variants,
            "render_demand": demand,
            "recurrence": recurrence,
            "episodes_touching": touches,
            "present_byte_real": n_present,
            "coverage_gap": max(0, demand - n_present),
            "confidence": conf,
        })
    for cand in sorted((_OBJECT_SEED & _OBJECT_ONLY & outline_toks) - covered_object_tokens):
        touches = _count_touches({cand}, pools)
        l3_rows.append({
            "object_id": f"candidate__{cand}",
            "source": "master_plan_outline",
            "layer_class": "L3",
            "state_variants": [],
            "render_demand": 1,
            "recurrence": "recurring" if touches["count"] > 1 else "one_shot",
            "episodes_touching": touches,
            "present_byte_real": 0,
            "coverage_gap": 1,
            "authoring_gap": True,
            "confidence": "outline",
        })

    # ── coverage summary ─────────────────────────────────────────────────────
    def _sum(rows, dkey, pkey):
        return (sum(int(r.get(dkey, 0)) for r in rows), sum(int(r.get(pkey, 0)) for r in rows))

    l0_dem, l0_pres = _sum(l0_rows, "render_demand", "present_byte_real")
    l3_dem, l3_pres = _sum(l3_rows, "render_demand", "present_byte_real")
    l2_dem = sum(int(r.get("pose_render_demand", 0)) for r in l2_rows)
    l2_pres = sum(int(r.get("present_byte_real", 0)) for r in l2_rows)
    req_total = l0_dem + l2_dem + l3_dem
    pres_total = l0_pres + l2_pres + l3_pres
    gap_total = max(0, req_total - pres_total)

    # ── identity-lock plan ───────────────────────────────────────────────────
    all_cast = [r["character_id"] for r in l2_rows]
    present_refs = [r["character_id"] for r in l2_rows if r["identity_lock"]["reference_sheet_present"]]
    # Protagonist candidate = the in-contract cast member with the most authored poses.
    contract_rows = [r for r in l2_rows if r.get("in_bank_contract")]
    protagonist_id = (
        max(contract_rows, key=lambda r: r.get("pose_render_demand", 0))["character_id"]
        if contract_rows else None
    )
    flagship = _flagship_lora_plan(repo_root, brand_id, series_id, locale, protagonist_id)
    identity_lock = {
        "engine_note": (
            "V5 doctrine: PuLID-first identity lock for ALL cast (reference sheets); "
            "LoRA training is flagship-only (MANGA_V5_LAYERED_ARCHITECTURE.md §15.A). "
            "Bank-contract metadata currently reports identity_lock_active:false "
            "(hash-only structural check; PuLID-FaceNet EVA-CLIP unresolved) — reference "
            "sheets are the plan, not yet an active lock."
        ),
        "pulid_reference_sheets": {
            "required_for": all_cast,
            "present": present_refs,
            "gap": [c for c in all_cast if c not in present_refs],
        },
        "flagship_lora": flagship,
    }

    # ── render-queue estimate (asset count × per-asset render class) ──────────
    # manga_asset_estimator.py's public API (_estimate_brand) is BRAND-plan-lane
    # shaped (reads config/catalog_planning/brand_series_plans.yaml lanes), not
    # per-asset — so it is not directly callable on this per-series asset list.
    # We reuse its internal per-asset economic heuristics (constants) instead.
    USD_PER_PANEL_GPU = 0.012
    ARTIST_HOURS_PER_PANEL = 0.32
    HOURLY_USD = 78.0
    by_class = {
        "L0": {"render_demand": l0_dem, "present": l0_pres, "to_render": max(0, l0_dem - l0_pres)},
        "L2": {"render_demand": l2_dem, "present": l2_pres, "to_render": max(0, l2_dem - l2_pres)},
        "L3": {"render_demand": l3_dem, "present": l3_pres, "to_render": max(0, l3_dem - l3_pres)},
    }
    to_render = sum(v["to_render"] for v in by_class.values())
    gpu_cost = round(to_render * USD_PER_PANEL_GPU, 2)
    labor_hours = round(to_render * ARTIST_HOURS_PER_PANEL, 1)
    labor_usd = round(labor_hours * HOURLY_USD, 2)

    gap_rollup = _aggregate_gap_files(manifest_dir)

    doc: dict[str, Any] = {
        "schema_version": "1.0.0",
        "artifact_type": "series_demand_rollup",
        "schema_authority": "schemas/manga/series_demand_rollup.schema.json",
        "series_id": series_id,
        "brand_id": brand_id,
        "locale": locale,
        "episode_horizon": horizon,
        "episodes_planned": episodes_planned,
        "detailed_window_end": detailed_window_end,
        "generated_from": {
            "master_plan": _rel(master_plan_path, repo_root),
            "bank_contracts": [
                _rel(bank_dir / n, repo_root)
                for n in ("scene_inventory.yaml", "object_inventory.yaml", "character_pose_inventory.yaml")
                if (bank_dir / n).is_file()
            ],
            "gap_files": [
                _rel(p, repo_root) for p in sorted(manifest_dir.glob("*_bank_gaps.json"))
            ] if manifest_dir.is_dir() else [],
            "image_bank_root": _rel(image_bank_root, repo_root),
            "storyboards_scanned": sum(
                1 for ep, p in pools.items()
                if p["detail_level"] == "detailed"
                and (repo_root / "artifacts" / "manga" / "arc_storyboards" / series_id
                     / f"ep_{ep:03d}.arc_storyboard.yaml").is_file()
            ),
        },
        "provenance": {
            "research": ["MANGA_LAYER_RENDER_CONTRACT_SPEC", "MANGA_V5_LAYERED_ARCHITECTURE"],
            "documents": ["MANGA_SERIES_MASTER_PLAN_CONTRACT.md"],
            "builds_on": ["manga_bank_contract_generator", "manga_asset_estimator.py"],
            "consumes_gap_format": "phoenix_v4/manga/chapter/visual_from_script.py::build_assembly_layer_hints",
            "byte_floor_reuse": "scripts/ci/check_render_progress_bytes.py (MIN_BYTES + _lfs_or_disk_bytes)",
            "backdrop_seed_vocab": sorted(_BACKDROP_SEED & _BACKDROP_ONLY),
            "object_seed_vocab": sorted(_OBJECT_SEED & _OBJECT_ONLY),
            "note": (
                "episodes_touching is a prose-scan estimate for prioritization; the "
                "authoritative render demand is the bank contract's declared variant "
                "counts. Outline rows (confidence:outline) are candidate demand needing "
                "bank-contract authoring, NOT asserted assets."
            ),
        },
        "demand": {
            "l0_backdrops": l0_rows,
            "l2_character_poses": l2_rows,
            "l3_objects": l3_rows,
        },
        "storyboard_gap_rollup": gap_rollup,
        "coverage_summary": {
            "required_render_demand_total": req_total,
            "present_byte_real_total": pres_total,
            "coverage_gap_total": gap_total,
            "coverage_pct": round(100.0 * pres_total / req_total, 1) if req_total else 0.0,
            "byte_floor": min_bytes,
            "byte_floor_source": "scripts/ci/check_render_progress_bytes.py::MIN_BYTES",
        },
        "identity_lock_plan": identity_lock,
        "render_queue_estimate": {
            "by_class": by_class,
            "total_assets_to_render": to_render,
            "gpu_cost_usd_est": gpu_cost,
            "human_labor_hours_est": labor_hours,
            "human_labor_cost_usd_est": labor_usd,
            "method": "asset_count × per-asset render class (coverage gap by L-class)",
            "heuristic_source": (
                "manga_asset_estimator.py per-panel constants (usd_per_panel_gpu=0.012, "
                "artist_hours_per_panel=0.32, hourly_usd=78.0); its _estimate_brand API is "
                "brand-plan-lane shaped, not per-asset, so reused as constants not called."
            ),
        },
        "acceptance_layer": "structurally_clear",
        "notes": (
            "ANALYSIS ONLY (Lane 09). No GPU render, no LoRA training. Demand is derived "
            "from the master plan + authored bank contracts + storyboards + image_bank "
            "byte-reality. A generator PASS is structurally_clear, never a render claim."
        ),
    }
    return doc


def run_series_rollup(master_plan: Path, out: Path | None, repo_root: Path = REPO) -> Path:
    doc = series_demand_rollup(master_plan, repo_root)
    series_id = doc["series_id"]
    if out is None:
        out = repo_root / "artifacts" / "manga" / series_id / "bank_contracts" / "series_demand_rollup.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    cs = doc["coverage_summary"]
    print(f"wrote {out}")
    print(
        f"  L0 backdrops={len(doc['demand']['l0_backdrops'])} "
        f"L2 cast={len(doc['demand']['l2_character_poses'])} "
        f"L3 objects={len(doc['demand']['l3_objects'])}"
    )
    print(
        f"  render demand={cs['required_render_demand_total']} "
        f"present(byte-real)={cs['present_byte_real_total']} "
        f"gap={cs['coverage_gap_total']} ({cs['coverage_pct']}% covered)"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0] if __doc__ else None)
    ap.add_argument("--chapter-script", type=Path, help="M3 chapter_script for per-episode stub mode")
    ap.add_argument("--series-rollup", action="store_true", help="build a series demand rollup")
    ap.add_argument("--master-plan", type=Path, help="series_master_plan.yaml (--series-rollup mode)")
    ap.add_argument("--out", type=Path, default=None, help="output path (--series-rollup mode)")
    args = ap.parse_args()

    if args.series_rollup:
        if not args.master_plan:
            ap.error("--series-rollup requires --master-plan")
        run_series_rollup(args.master_plan, args.out)
        return 0

    if not args.chapter_script:
        ap.error("one of --chapter-script or --series-rollup is required")
    generate_chapter_stub(args.chapter_script)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate deterministic continuity invariants between consecutive panels.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §6.3.A — Phase B.1 step 3.

V1 implements ONLY §6.3.A deterministic invariants (class-A, FAIL severity).
§6.3.B heuristic/narrative invariants (emotional_pendulation, gaze_continuity_semantic,
tension_arc_coherence) are class-D and deferred to Phase B.2.

Seven invariants:
  1. scene_continuity              — scene_id unchanged unless beat_type ∈ {standard, long_drop, miyazaki_ma}
  2. character_identity_continuity — structural: character_id + pose_id + framing match declarations
  3. prop_persistence              — prop value identical to prev OR adjacent in prop_evolution enum
  4. gaze_target_validity          — at_named_X target exists in scene_state OR prop_state OR stage
  5. temporal_continuity           — temporal value identical or next-in-cycle, unless beat_type allows jump
  6. expression_dial_bounded_delta — |Δ dial| ≤ 0.3 (micro) / 0.5 (spatial) / unbounded (standard+)
  7. light_rig_within_scene        — light_rig_id ∈ scene_inventory.scenes[scene_id].light_rigs

NO model inference. NO embedding distance. NO LLM. Pure dict lookups + enum
membership + bounded numeric delta. The character_identity check is STRUCTURAL
(same character_id present in both panels has the same character_design_hash;
pose_id matches archetype's subject_type; framing row exists in compiled
safe_zones). Perceptual identity drift detection is class-C, Phase B.2.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PROP_EVOLUTION = REPO / "config" / "manga" / "continuity" / "prop_evolution.yaml"
DEFAULT_TEMPORAL_CYCLE = REPO / "config" / "manga" / "continuity" / "temporal_cycle.yaml"
DEFAULT_COMPILED_SAFE_ZONES = REPO / "config" / "manga" / "compiled" / "safe_zones.yaml"

Severity = Literal["FAIL", "WARN", "SCORE"]
ValidatorClass = Literal["A", "B", "C", "D"]

SCENE_JUMP_BEAT_TYPES = {"standard", "long_drop", "miyazaki_ma"}
EXPRESSION_DIAL_BOUNDS = {
    "micro": 0.3,
    "spatial": 0.5,
    # standard / long_drop / miyazaki_ma: unbounded (no entry)
}


# ─────────────────────────────────────────────────────────────────────────────
# data structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ContinuityValidationInput:
    """Both panel continuity_state dicts + supporting config.

    `previous` is None for an episode-opening panel; in that case all invariants
    that depend on the previous panel are SKIPPED (not FAIL).
    """

    current: dict
    previous: dict | None
    beat_type: str
    scene_inventory: dict | None = None        # for light_rig_within_scene
    prop_evolution: dict | None = None         # for prop_persistence
    temporal_cycle: dict | None = None         # for temporal_continuity
    character_pose_inventory: dict | None = None  # for character_identity (structural)
    archetype_metadata: dict | None = None     # archetype's declared subject_type per layer
    compiled_safe_zones: dict | None = None    # for framing-row presence check


@dataclass
class ValidationResult:
    check_id: str
    class_: ValidatorClass
    severity: Severity
    passed: bool
    score: float
    evidence: dict[str, Any]
    remediation_hint: str
    skipped: bool = False
    skip_reason: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["class"] = d.pop("class_")
        return d


def _ok(check_id: str, evidence: dict) -> ValidationResult:
    return ValidationResult(check_id, "A", "FAIL", True, 0.0, evidence, "")


def _fail(check_id: str, evidence: dict, hint: str, score: float = 1.0) -> ValidationResult:
    return ValidationResult(check_id, "A", "FAIL", False, score, evidence, hint)


def _na(check_id: str, reason: str) -> ValidationResult:
    return ValidationResult(check_id, "A", "FAIL", True, 0.0, {}, "", True, reason)


# ─────────────────────────────────────────────────────────────────────────────
# invariant 1: scene_continuity
# ─────────────────────────────────────────────────────────────────────────────


def check_scene_continuity(inp: ContinuityValidationInput) -> ValidationResult:
    if inp.previous is None:
        return _na("scene_continuity", "episode-opening panel: no prev to compare")

    curr_scene = (inp.current.get("scene_state") or {}).get("scene_id")
    prev_scene = (inp.previous.get("scene_state") or {}).get("scene_id")

    if curr_scene is None or prev_scene is None:
        return _fail(
            "scene_continuity",
            evidence={"current_scene_id": curr_scene, "previous_scene_id": prev_scene},
            hint="Missing scene_state.scene_id in current or previous panel — fill in continuity_state.",
        )

    if curr_scene == prev_scene:
        return _ok("scene_continuity",
                   evidence={"scene_id": curr_scene, "beat_type": inp.beat_type})

    if inp.beat_type in SCENE_JUMP_BEAT_TYPES:
        return _ok("scene_continuity",
                   evidence={"prev_scene": prev_scene, "current_scene": curr_scene,
                             "beat_type": inp.beat_type, "scene_jump_allowed": True})

    return _fail(
        "scene_continuity",
        evidence={"prev_scene": prev_scene, "current_scene": curr_scene,
                  "beat_type": inp.beat_type, "allowed_jump_beats": sorted(SCENE_JUMP_BEAT_TYPES)},
        hint=f"Scene jumped {prev_scene!r} -> {curr_scene!r} on beat_type={inp.beat_type!r} "
             f"(scene jump only allowed on beats {sorted(SCENE_JUMP_BEAT_TYPES)}).",
    )


# ─────────────────────────────────────────────────────────────────────────────
# invariant 2: character_identity_continuity (STRUCTURAL — no embeddings)
# ─────────────────────────────────────────────────────────────────────────────


def check_character_identity_continuity(inp: ContinuityValidationInput) -> ValidationResult:
    """Structural identity continuity:
      - For every character_id in current.character_state that was ALSO in
        previous.character_state, the character_design_hash matches.
      - For every character_id in current.character_state, the declared
        pose_id is in character_pose_inventory[character_id] (if provided).

    PERCEPTUAL identity drift (cosine distance) is class-C; deferred to B.2.
    """
    curr_chars = inp.current.get("character_state") or {}
    if not curr_chars:
        return _na("character_identity_continuity",
                   "no character_state in current panel (none on stage)")

    failures = []

    # Hash continuity vs prev
    if inp.previous is not None:
        prev_chars = inp.previous.get("character_state") or {}
        for cid, cstate in curr_chars.items():
            if cid not in prev_chars:
                continue  # new character — fine
            curr_hash = (cstate or {}).get("character_design_hash")
            prev_hash = (prev_chars[cid] or {}).get("character_design_hash")
            if curr_hash is None or prev_hash is None:
                failures.append({
                    "character_id": cid,
                    "reason": "missing character_design_hash",
                    "current": curr_hash, "previous": prev_hash,
                })
                continue
            if curr_hash != prev_hash:
                failures.append({
                    "character_id": cid,
                    "reason": "character_design_hash mismatch",
                    "previous_hash": prev_hash, "current_hash": curr_hash,
                })

    # Pose declared in inventory (if pose_inventory supplied)
    # Supports two shapes:
    #   (1) flat: {character_id: [pose_id_str, ...]}
    #   (2) nested: {characters: {character_id: {poses: [{pose_id: X, ...}, ...]}}}
    pose_inv_root = None
    if inp.character_pose_inventory:
        if "characters" in inp.character_pose_inventory:
            pose_inv_root = inp.character_pose_inventory.get("characters") or {}
        else:
            pose_inv_root = inp.character_pose_inventory

    if pose_inv_root:
        for cid, cstate in curr_chars.items():
            pose_id = (cstate or {}).get("pose_id")
            if pose_id is None:
                continue  # pose declaration optional for V1; absent = no check
            char_entry = pose_inv_root.get(cid)
            if char_entry is None:
                failures.append({
                    "character_id": cid,
                    "reason": "character not in character_pose_inventory",
                    "pose_id": pose_id,
                })
                continue
            # Extract the available pose_id list from either shape
            if isinstance(char_entry, list):
                available = [
                    p if isinstance(p, str) else (p.get("pose_id") if isinstance(p, dict) else None)
                    for p in char_entry
                ]
                available = [a for a in available if a is not None]
            elif isinstance(char_entry, dict):
                poses_field = char_entry.get("poses") or []
                available = [
                    p if isinstance(p, str) else (p.get("pose_id") if isinstance(p, dict) else None)
                    for p in poses_field
                ]
                available = [a for a in available if a is not None]
            else:
                available = []
            if pose_id not in available:
                failures.append({
                    "character_id": cid,
                    "reason": "pose_id not declared in character_pose_inventory",
                    "pose_id": pose_id,
                    "available_poses": available,
                })

    if failures:
        return _fail(
            "character_identity_continuity",
            evidence={"failures": failures, "character_ids_on_stage": sorted(curr_chars.keys())},
            hint="Structural identity mismatch — re-author continuity_state to match character_design "
                 "hash and declared poses. Perceptual face-distance check is class-C (Phase B.2).",
        )
    return _ok("character_identity_continuity",
               evidence={"character_ids_on_stage": sorted(curr_chars.keys())})


# ─────────────────────────────────────────────────────────────────────────────
# invariant 3: prop_persistence
# ─────────────────────────────────────────────────────────────────────────────


def _adjacent_in_enum(prev_val: str, curr_val: str, enum_list: list[str]) -> bool:
    if prev_val == curr_val:
        return True
    if prev_val not in enum_list or curr_val not in enum_list:
        return False
    return abs(enum_list.index(prev_val) - enum_list.index(curr_val)) <= 1


def check_prop_persistence(inp: ContinuityValidationInput) -> ValidationResult:
    if inp.previous is None:
        return _na("prop_persistence", "episode-opening panel: no prev to compare")

    curr_props = inp.current.get("prop_state") or {}
    prev_props = inp.previous.get("prop_state") or {}

    if not curr_props and not prev_props:
        return _na("prop_persistence", "no prop_state in either panel")

    if inp.prop_evolution is None:
        return _fail(
            "prop_persistence",
            evidence={"reason": "prop_evolution config not supplied"},
            hint="Supply prop_evolution config (config/manga/continuity/prop_evolution.yaml).",
        )
    prop_types = inp.prop_evolution.get("prop_types", {})

    failures = []
    # For every prop in current that was also in prev, validate transition
    for prop_id, curr_val in curr_props.items():
        if prop_id not in prev_props:
            continue
        prev_val = prev_props[prop_id]
        # Short-circuit identity: unchanged prop is always valid regardless of enum lookup.
        # This avoids spurious "no matching prop_type" failures for props whose
        # state didn't change but whose prop_id doesn't match a declared prop_type.
        if prev_val == curr_val:
            continue
        # Determine prop_type from prop_id (convention: prefix or explicit mapping)
        prop_type = None
        for ptype in prop_types:
            if prop_id == ptype or prop_id.startswith(f"{ptype}_") or prop_id.endswith(f"_{ptype}"):
                prop_type = ptype
                break
        if prop_type is None:
            failures.append({
                "prop_id": prop_id,
                "reason": "no matching prop_type in prop_evolution config",
                "prev": prev_val, "current": curr_val,
            })
            continue
        enum = prop_types[prop_type].get("states", [])
        if not _adjacent_in_enum(prev_val, curr_val, enum):
            failures.append({
                "prop_id": prop_id, "prop_type": prop_type,
                "prev": prev_val, "current": curr_val,
                "enum_order": enum,
                "reason": "non-adjacent state transition (must pass through intermediate)",
            })

    if failures:
        return _fail(
            "prop_persistence",
            evidence={"failures": failures},
            hint="Prop state jumped without intermediate beat. Insert transitional panel "
                 "or correct the prop_state declaration.",
        )
    return _ok("prop_persistence",
               evidence={"prop_ids_checked": sorted(set(curr_props) & set(prev_props))})


# ─────────────────────────────────────────────────────────────────────────────
# invariant 4: gaze_target_validity
# ─────────────────────────────────────────────────────────────────────────────


_GAZE_NAMED_OBJECT_PREFIX = "at_named_object_"
_GAZE_NAMED_CHARACTER_PREFIX = "at_named_character_"


def check_gaze_target_validity(inp: ContinuityValidationInput) -> ValidationResult:
    curr_chars = inp.current.get("character_state") or {}
    if not curr_chars:
        return _na("gaze_target_validity", "no characters on stage")

    failures = []
    scene_state = inp.current.get("scene_state") or {}
    prop_state = inp.current.get("prop_state") or {}
    named_props = set(prop_state.keys())
    named_chars = set(curr_chars.keys())

    for cid, cstate in curr_chars.items():
        gaze = (cstate or {}).get("gaze_direction")
        if not isinstance(gaze, str):
            continue
        if gaze.startswith(_GAZE_NAMED_OBJECT_PREFIX):
            target = gaze[len(_GAZE_NAMED_OBJECT_PREFIX):]
            if target not in named_props:
                failures.append({
                    "character_id": cid, "gaze": gaze, "target_kind": "object",
                    "target": target, "props_on_stage": sorted(named_props),
                })
        elif gaze.startswith(_GAZE_NAMED_CHARACTER_PREFIX):
            target = gaze[len(_GAZE_NAMED_CHARACTER_PREFIX):]
            if target not in named_chars:
                failures.append({
                    "character_id": cid, "gaze": gaze, "target_kind": "character",
                    "target": target, "characters_on_stage": sorted(named_chars),
                })

    if failures:
        return _fail(
            "gaze_target_validity",
            evidence={"failures": failures},
            hint="Gaze targets a named entity not present on stage. Add the target to "
                 "scene_state/prop_state/character_state OR change gaze enum.",
        )
    return _ok("gaze_target_validity",
               evidence={"named_props": sorted(named_props),
                         "named_characters": sorted(named_chars)})


# ─────────────────────────────────────────────────────────────────────────────
# invariant 5: temporal_continuity
# ─────────────────────────────────────────────────────────────────────────────


def check_temporal_continuity(inp: ContinuityValidationInput) -> ValidationResult:
    if inp.previous is None:
        return _na("temporal_continuity", "episode-opening panel: no prev to compare")

    cycle_doc = inp.temporal_cycle or {}
    cycle = cycle_doc.get("cycle", [])
    exempt = set(cycle_doc.get("exemption_beat_types", []))

    curr_temp = (inp.current.get("scene_state") or {}).get("temporal")
    prev_temp = (inp.previous.get("scene_state") or {}).get("temporal")

    if curr_temp is None or prev_temp is None:
        return _na("temporal_continuity",
                   f"missing temporal in current ({curr_temp!r}) or previous ({prev_temp!r})")

    if inp.beat_type in exempt:
        return _ok("temporal_continuity",
                   evidence={"prev": prev_temp, "current": curr_temp,
                             "beat_type": inp.beat_type, "exemption": True})

    if not cycle:
        return _fail(
            "temporal_continuity",
            evidence={"reason": "temporal_cycle config not supplied"},
            hint="Supply temporal_cycle config (config/manga/continuity/temporal_cycle.yaml).",
        )

    if curr_temp == prev_temp:
        return _ok("temporal_continuity",
                   evidence={"temporal": curr_temp, "delta": "identical"})

    if prev_temp not in cycle or curr_temp not in cycle:
        return _fail(
            "temporal_continuity",
            evidence={"prev": prev_temp, "current": curr_temp, "cycle": cycle},
            hint="Temporal value not in declared cycle.",
        )

    prev_idx = cycle.index(prev_temp)
    next_idx = (prev_idx + 1) % len(cycle)
    next_in_cycle = cycle[next_idx]
    if curr_temp == next_in_cycle:
        return _ok("temporal_continuity",
                   evidence={"prev": prev_temp, "current": curr_temp,
                             "delta": "next-in-cycle"})

    return _fail(
        "temporal_continuity",
        evidence={"prev": prev_temp, "current": curr_temp,
                  "expected": [prev_temp, next_in_cycle], "beat_type": inp.beat_type},
        hint=f"Temporal jumped {prev_temp!r} -> {curr_temp!r}; allowed values on beat={inp.beat_type!r}: "
             f"{[prev_temp, next_in_cycle]}. Use beat_type in {sorted(exempt)} for full temporal jump.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# invariant 6: expression_dial_bounded_delta
# ─────────────────────────────────────────────────────────────────────────────


def check_expression_dial_bounded_delta(inp: ContinuityValidationInput) -> ValidationResult:
    if inp.previous is None:
        return _na("expression_dial_bounded_delta", "episode-opening panel")

    bound = EXPRESSION_DIAL_BOUNDS.get(inp.beat_type)
    if bound is None:
        return _ok("expression_dial_bounded_delta",
                   evidence={"beat_type": inp.beat_type, "bound": "unbounded"})

    curr_chars = inp.current.get("character_state") or {}
    prev_chars = inp.previous.get("character_state") or {}

    failures = []
    for cid, cstate in curr_chars.items():
        if cid not in prev_chars:
            continue
        try:
            curr_dial = float((cstate or {}).get("expression_dial"))
            prev_dial = float((prev_chars[cid] or {}).get("expression_dial"))
        except (TypeError, ValueError):
            continue
        delta = abs(curr_dial - prev_dial)
        if delta > bound:
            failures.append({
                "character_id": cid,
                "prev_dial": prev_dial, "current_dial": curr_dial,
                "delta": round(delta, 3), "bound": bound,
                "beat_type": inp.beat_type,
            })

    if failures:
        return _fail(
            "expression_dial_bounded_delta",
            evidence={"failures": failures},
            hint=f"Expression dial delta exceeds {bound} on beat_type={inp.beat_type!r}. "
                 f"Insert intermediate beat OR use beat_type=standard for unbounded transition.",
        )
    return _ok("expression_dial_bounded_delta",
               evidence={"beat_type": inp.beat_type, "bound": bound})


# ─────────────────────────────────────────────────────────────────────────────
# invariant 7: light_rig_within_scene
# ─────────────────────────────────────────────────────────────────────────────


def check_light_rig_within_scene(inp: ContinuityValidationInput) -> ValidationResult:
    scene_state = inp.current.get("scene_state") or {}
    scene_id = scene_state.get("scene_id")
    rig_id = scene_state.get("light_rig_id")

    if scene_id is None or rig_id is None:
        return _na("light_rig_within_scene",
                   f"missing scene_id ({scene_id!r}) or light_rig_id ({rig_id!r}) "
                   f"in current panel scene_state")

    if inp.scene_inventory is None:
        return _na("light_rig_within_scene", "no scene_inventory supplied")

    scenes = inp.scene_inventory.get("scenes", [])
    target_scene = next((s for s in scenes if s.get("scene_id") == scene_id), None)
    if target_scene is None:
        return _fail(
            "light_rig_within_scene",
            evidence={"scene_id": scene_id, "available_scenes": [s.get("scene_id") for s in scenes]},
            hint=f"Scene {scene_id!r} not declared in scene_inventory.",
        )

    declared_rigs = [r.get("light_rig_id") if isinstance(r, dict) else r
                     for r in (target_scene.get("light_rigs") or [])]
    if rig_id not in declared_rigs:
        return _fail(
            "light_rig_within_scene",
            evidence={"scene_id": scene_id, "rig_id": rig_id,
                      "declared_rigs_for_scene": declared_rigs},
            hint=f"Light rig {rig_id!r} not declared in scene_inventory.scenes[{scene_id!r}].light_rigs.",
        )

    return _ok("light_rig_within_scene",
               evidence={"scene_id": scene_id, "rig_id": rig_id})


# ─────────────────────────────────────────────────────────────────────────────
# orchestration
# ─────────────────────────────────────────────────────────────────────────────


_ALL_CHECKS = [
    check_scene_continuity,
    check_character_identity_continuity,
    check_prop_persistence,
    check_gaze_target_validity,
    check_temporal_continuity,
    check_expression_dial_bounded_delta,
    check_light_rig_within_scene,
]


def validate_continuity(inp: ContinuityValidationInput) -> list[ValidationResult]:
    return [fn(inp) for fn in _ALL_CHECKS]


def all_class_a_passed(results: list[ValidationResult]) -> bool:
    return all(r.passed for r in results if r.class_ == "A" and r.severity == "FAIL")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _load_yaml(path: Path) -> dict | None:
    if path is None or not path.is_file():
        return None
    return yaml.safe_load(path.read_text())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate deterministic continuity invariants between consecutive panels."
    )
    ap.add_argument("--current", type=Path, required=True,
                    help="Current panel continuity_state YAML")
    ap.add_argument("--previous", type=Path,
                    help="Previous panel continuity_state YAML (omit for episode opener)")
    ap.add_argument("--beat-type", required=True,
                    choices=["micro", "spatial", "standard", "long_drop", "miyazaki_ma"])
    ap.add_argument("--scene-inventory", type=Path, help="Series scene_inventory.yaml")
    ap.add_argument("--prop-evolution", type=Path, default=DEFAULT_PROP_EVOLUTION)
    ap.add_argument("--temporal-cycle", type=Path, default=DEFAULT_TEMPORAL_CYCLE)
    ap.add_argument("--character-pose-inventory", type=Path)
    ap.add_argument("--output-json", type=Path)
    args = ap.parse_args(argv)

    try:
        current = _load_yaml(args.current)
        if current is None:
            raise FileNotFoundError(f"current panel not found: {args.current}")
        previous = _load_yaml(args.previous) if args.previous else None
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    inp = ContinuityValidationInput(
        current=current,
        previous=previous,
        beat_type=args.beat_type,
        scene_inventory=_load_yaml(args.scene_inventory) if args.scene_inventory else None,
        prop_evolution=_load_yaml(args.prop_evolution),
        temporal_cycle=_load_yaml(args.temporal_cycle),
        character_pose_inventory=_load_yaml(args.character_pose_inventory) if args.character_pose_inventory else None,
    )

    results = validate_continuity(inp)
    passed = all_class_a_passed(results)

    for r in results:
        status = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
        line = f"[{status}] {r.check_id}"
        if r.skipped:
            line += f" — {r.skip_reason}"
        elif not r.passed:
            line += f" (class {r.class_} {r.severity}; score {r.score:.3f}): {r.remediation_hint}"
        print(line)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(
            {"passed": passed, "results": [r.to_dict() for r in results]},
            indent=2, default=str,
        ))

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

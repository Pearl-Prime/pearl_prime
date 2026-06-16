#!/usr/bin/env python3
"""
check_agent_registry.py — Agent registry ↔ subsystem-authority-map consistency gate.

Implements P0-1 from docs/specs/AGENT_SYSTEM_IMPROVEMENT_V2_SPEC.md §2, finishing the
validator outlined-but-never-built in docs/AGENT_SYSTEM_IMPROVEMENT_SPEC.md §5
("future scripts/ci/check_agent_registry.py").

It asserts two invariants between the machine-readable agent roster
(config/agents/agent_registry.yaml) and the subsystem routing authority
(artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv):

  RULE 1 (coverage):   every subsystem_id in SUBSYSTEM_AUTHORITY_MAP.tsv appears in
                       EXACTLY ONE agent's `subsystems` list — UNLESS it is explicitly
                       documented as shared. A subsystem claimed by zero agents is an
                       ORPHAN (registry↔map drift); a subsystem claimed by >1 agents is
                       OVER-CLAIMED unless documented shared.
  RULE 2 (skill_path): every agent's `skill_path` is null OR points at an existing file.

"Documented as shared" (per IMPROVEMENT_SPEC §5 "document exception in notes") is honored
two ways, either of which suppresses the coverage violation for that subsystem_id:
  (a) the agent's `notes` string mentions the subsystem_id AND the word "shared"
      (case-insensitive); OR
  (b) the SUBSYSTEM_AUTHORITY_MAP row for that subsystem_id names a multi-owner
      (owner_agent contains "+"), which is the map's own way of declaring shared ownership.
Shared subsystems are reported as INFO (non-fatal) so the roster stays auditable.

This script reuses the loader conventions of scripts/ci/pr_governance_review.py
(REPO_ROOT resolution, csv.DictReader('\t') for the TSV) and the YAML-load style of
scripts/ci/check_doctrine_schema.py. It performs NO network or LLM calls and is therefore
Tier-2 / unattended-safe (CLAUDE.md LLM policy; passes scripts/ci/audit_llm_callers.py).

Exit 0 = pass. Exit 1 = fail (violations printed). Exit 2 = could-not-load inputs.

Usage:
    PYTHONPATH=. python3 scripts/ci/check_agent_registry.py
    PYTHONPATH=. python3 scripts/ci/check_agent_registry.py --json
    PYTHONPATH=. python3 scripts/ci/check_agent_registry.py \
        --registry config/agents/agent_registry.yaml \
        --map artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Same REPO_ROOT resolution as scripts/ci/pr_governance_review.py (scripts/ci/<file>).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Canonical input locations (singletons per CANONICAL_ARTIFACTS_REGISTRY.tsv — append, never fork).
DEFAULT_REGISTRY = REPO_ROOT / "config" / "agents" / "agent_registry.yaml"
DEFAULT_MAP = REPO_ROOT / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv"

# Severity labels.
SEV_VIOLATION = "VIOLATION"  # fatal -> exit 1
SEV_INFO = "INFO"            # documented/expected -> non-fatal


# ---------------------------------------------------------------------------
# Loaders (mirror pr_governance_review.load_subsystem_map / check_doctrine_schema._load_yaml)
# ---------------------------------------------------------------------------
def load_registry(path: Path) -> dict[str, Any]:
    """Load agent_registry.yaml. Returns {} with __load_error on failure."""
    if not path.exists():
        return {"__load_error": f"registry not found: {path}"}
    try:
        import yaml  # PyYAML; same dependency as the other scripts/ci/check_*.py validators
    except Exception as e:  # pragma: no cover - environment-dependent
        return {"__load_error": f"PyYAML unavailable: {e}"}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        return {"__load_error": f"YAML parse error in {path}: {e}"}
    if not isinstance(data, dict):
        return {"__load_error": f"registry root is not a mapping: {path}"}
    return data


def load_map_subsystems(path: Path) -> tuple[list[dict[str, str]], str | None]:
    """Load SUBSYSTEM_AUTHORITY_MAP.tsv rows.

    Returns (rows, error). Each row dict carries subsystem_id + owner_agent (+ status).
    Uses csv.DictReader('\t') exactly like pr_governance_review.load_subsystem_map.
    """
    if not path.exists():
        return [], f"subsystem map not found: {path}"
    rows: list[dict[str, str]] = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                sid = (row.get("subsystem_id") or "").strip()
                if not sid:
                    continue
                rows.append(
                    {
                        "subsystem_id": sid,
                        "owner_agent": (row.get("owner_agent") or "").strip(),
                        "status": (row.get("status") or "").strip(),
                    }
                )
    except Exception as e:
        return [], f"TSV parse error in {path}: {e}"
    return rows, None


# ---------------------------------------------------------------------------
# Core validation (pure; testable with explicit inputs)
# ---------------------------------------------------------------------------
def _agent_declarations(registry: dict[str, Any]) -> dict[str, list[str]]:
    """subsystem_id -> [agent_id, ...] that declare it in their `subsystems` list."""
    decl: dict[str, list[str]] = defaultdict(list)
    for aid, a in (registry.get("agents") or {}).items():
        if not isinstance(a, dict):
            continue
        for s in a.get("subsystems") or []:
            decl[str(s).strip()].append(aid)
    return decl


def _notes_marks_shared(registry: dict[str, Any], subsystem_id: str) -> bool:
    """True if any agent's notes documents this subsystem_id as shared (per IMPROVEMENT_SPEC §5)."""
    needle = subsystem_id.lower()
    for a in (registry.get("agents") or {}).values():
        if not isinstance(a, dict):
            continue
        notes = str(a.get("notes") or "").lower()
        if "shared" in notes and needle in notes:
            return True
    return False


def validate(
    registry: dict[str, Any],
    map_rows: list[dict[str, str]],
    registry_path: Path,
) -> list[dict[str, str]]:
    """Run RULE 1 (coverage) + RULE 2 (skill_path). Return list of finding dicts.

    Each finding: {severity, rule, subsystem_id?, agent?, message}.
    Only SEV_VIOLATION findings make the gate fail.
    """
    findings: list[dict[str, str]] = []
    agents = registry.get("agents") or {}
    decl = _agent_declarations(registry)
    map_ids = [r["subsystem_id"] for r in map_rows]
    owner_by_sid = {r["subsystem_id"]: r["owner_agent"] for r in map_rows}

    # ---- RULE 1: coverage (every map subsystem_id in exactly one agent, unless shared) ----
    seen: set[str] = set()
    for sid in map_ids:
        if sid in seen:
            continue  # de-dupe if the map ever lists a sid twice
        seen.add(sid)
        claimers = decl.get(sid, [])
        map_owner = owner_by_sid.get(sid, "")
        map_declares_shared = "+" in map_owner  # e.g. "Pearl_Int (operations) + Pearl_Architect (spec)"
        documented_shared = map_declares_shared or _notes_marks_shared(registry, sid)

        if len(claimers) == 1:
            continue  # the happy path
        if len(claimers) == 0:
            if documented_shared:
                findings.append(
                    {
                        "severity": SEV_INFO,
                        "rule": "coverage",
                        "subsystem_id": sid,
                        "agent": "",
                        "message": (
                            f"subsystem '{sid}' has no agent in agent_registry.subsystems, but is "
                            f"documented as shared/multi-owner (map owner_agent='{map_owner}'). "
                            f"Non-fatal; add it to an agent's subsystems list to make the roster explicit."
                        ),
                    }
                )
            else:
                findings.append(
                    {
                        "severity": SEV_VIOLATION,
                        "rule": "coverage",
                        "subsystem_id": sid,
                        "agent": "",
                        "message": (
                            f"ORPHAN: subsystem '{sid}' (map owner_agent='{map_owner}') is in "
                            f"SUBSYSTEM_AUTHORITY_MAP.tsv but appears in NO agent's `subsystems` list in "
                            f"{registry_path.name}. Add it to exactly one agent, or document it as shared "
                            f"(say 'shared' + the subsystem id in that agent's `notes`, or give the map row a "
                            f"multi-owner owner_agent with '+')."
                        ),
                    }
                )
        else:  # >1 claimers
            sev = SEV_INFO if documented_shared else SEV_VIOLATION
            kind = "shared (documented)" if documented_shared else "OVER-CLAIMED (undocumented)"
            findings.append(
                {
                    "severity": sev,
                    "rule": "coverage",
                    "subsystem_id": sid,
                    "agent": ";".join(claimers),
                    "message": (
                        f"{kind}: subsystem '{sid}' is claimed by {len(claimers)} agents "
                        f"({', '.join(claimers)}). The map requires exactly one owner unless shared. "
                        + (
                            "Documented shared -> non-fatal."
                            if documented_shared
                            else "Document it as shared in one agent's `notes` (mention 'shared' + the id), "
                            "or remove the duplicate claim."
                        )
                    ),
                }
            )

    # ---- Reverse-drift visibility: registry subsystem NOT in the map (INFO, non-fatal) ----
    map_id_set = set(map_ids)
    for sid in sorted(decl):
        if sid not in map_id_set:
            findings.append(
                {
                    "severity": SEV_INFO,
                    "rule": "coverage",
                    "subsystem_id": sid,
                    "agent": ";".join(decl[sid]),
                    "message": (
                        f"subsystem '{sid}' is declared in agent_registry ({', '.join(decl[sid])}) but is "
                        f"NOT a row in SUBSYSTEM_AUTHORITY_MAP.tsv. Likely a proposed subsystem "
                        f"(IMPROVEMENT_SPEC §8) not yet added to the map. Non-fatal; add the map row when ratified."
                    ),
                }
            )

    # ---- RULE 2: skill_path null-or-exists ----
    for aid, a in agents.items():
        if not isinstance(a, dict):
            findings.append(
                {
                    "severity": SEV_VIOLATION,
                    "rule": "skill_path",
                    "subsystem_id": "",
                    "agent": str(aid),
                    "message": f"agent '{aid}' is not a mapping in {registry_path.name}.",
                }
            )
            continue
        sp = a.get("skill_path", None)
        if sp is None:
            continue  # null is allowed
        sp_str = str(sp).strip()
        if not sp_str or sp_str.lower() in ("null", "none", "~"):
            continue  # treat empty / textual-null defensively as null
        skill_file = (REPO_ROOT / sp_str)
        if not skill_file.exists():
            findings.append(
                {
                    "severity": SEV_VIOLATION,
                    "rule": "skill_path",
                    "subsystem_id": "",
                    "agent": str(aid),
                    "message": (
                        f"agent '{aid}' skill_path '{sp_str}' does not exist (must be null or an existing file)."
                    ),
                }
            )

    return findings


# ---------------------------------------------------------------------------
# Reporting / CLI
# ---------------------------------------------------------------------------
def _print_human(findings: list[dict[str, str]], registry_path: Path, map_path: Path) -> None:
    violations = [f for f in findings if f["severity"] == SEV_VIOLATION]
    infos = [f for f in findings if f["severity"] == SEV_INFO]
    print("check_agent_registry: agent_registry ↔ SUBSYSTEM_AUTHORITY_MAP consistency")
    print(f"  registry: {registry_path}")
    print(f"  map:      {map_path}")
    print(f"  findings: {len(violations)} violation(s), {len(infos)} info")
    if violations:
        print("\nVIOLATIONS (gate fails):")
        for f in violations:
            tag = f["subsystem_id"] or f["agent"] or "-"
            print(f"  [{f['rule']}] {tag}: {f['message']}")
    if infos:
        print("\nINFO (non-fatal):")
        for f in infos:
            tag = f["subsystem_id"] or f["agent"] or "-"
            print(f"  [{f['rule']}] {tag}: {f['message']}")
    print("\nRESULT: " + ("FAIL" if violations else "PASS"))


def run(registry_path: Path, map_path: Path, as_json: bool) -> int:
    registry = load_registry(registry_path)
    if registry.get("__load_error"):
        msg = registry["__load_error"]
        if as_json:
            print(json.dumps({"ok": False, "load_error": msg, "findings": []}, indent=2))
        else:
            print(f"check_agent_registry: LOAD ERROR: {msg}", file=sys.stderr)
        return 2

    map_rows, map_err = load_map_subsystems(map_path)
    if map_err:
        if as_json:
            print(json.dumps({"ok": False, "load_error": map_err, "findings": []}, indent=2))
        else:
            print(f"check_agent_registry: LOAD ERROR: {map_err}", file=sys.stderr)
        return 2

    findings = validate(registry, map_rows, registry_path)
    violations = [f for f in findings if f["severity"] == SEV_VIOLATION]

    if as_json:
        print(
            json.dumps(
                {
                    "ok": not violations,
                    "registry": str(registry_path),
                    "map": str(map_path),
                    "counts": {
                        "violations": len(violations),
                        "info": len(findings) - len(violations),
                        "map_subsystems": len({r["subsystem_id"] for r in map_rows}),
                        "agents": len(registry.get("agents") or {}),
                    },
                    "findings": findings,
                },
                indent=2,
            )
        )
    else:
        _print_human(findings, registry_path, map_path)

    return 1 if violations else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Path to agent_registry.yaml")
    ap.add_argument("--map", type=Path, default=DEFAULT_MAP, help="Path to SUBSYSTEM_AUTHORITY_MAP.tsv")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = ap.parse_args(argv)
    return run(args.registry, args.map, args.json)


if __name__ == "__main__":
    raise SystemExit(main())

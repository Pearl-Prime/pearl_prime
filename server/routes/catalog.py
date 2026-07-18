"""
Catalog and pipeline endpoints.

GET  /api/v1/catalog/brands      — list brands from brand_registry.yaml
GET  /api/v1/catalog/topics      — list topics from topic_engine_bindings.yaml
GET  /api/v1/catalog/plans       — list compiled plan artifacts
GET  /api/v1/catalog/arcs        — list arc files
POST /api/v1/catalog/validate    — validate a plan JSON against arc alignment
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@router.get("/brands")
async def list_brands():
    """List brands from brand_registry.yaml."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    data = _load_yaml(repo_root / "config" / "brand_registry.yaml")
    brands = data.get("brands", data)
    return {"brands": brands}


@router.get("/topics")
async def list_topics():
    """List topics from topic_engine_bindings.yaml."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    data = _load_yaml(repo_root / "config" / "topic_engine_bindings.yaml")
    return {"topics": data}


@router.get("/plans")
async def list_plans():
    """List compiled plan artifacts from artifacts/plans/."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    plans_dir = repo_root / "artifacts" / "plans"
    if not plans_dir.is_dir():
        return {"plans": [], "count": 0}
    plan_files = sorted(str(p.name) for p in plans_dir.glob("*.json"))
    return {"plans": plan_files, "count": len(plan_files)}


@router.get("/arcs")
async def list_arcs():
    """List arc blueprint files."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()

    # Check both possible arc locations per Arc-First spec
    arc_dirs = [
        repo_root / "arcs",
        repo_root / "config" / "source_of_truth" / "master_arcs",
    ]
    arcs = []
    for arc_dir in arc_dirs:
        if arc_dir.is_dir():
            for p in sorted(arc_dir.rglob("*.yaml")):
                arcs.append(str(p.relative_to(repo_root)))
            for p in sorted(arc_dir.rglob("*.yml")):
                arcs.append(str(p.relative_to(repo_root)))
    return {"arcs": arcs, "count": len(arcs)}


@router.post("/validate")
async def validate_plan(plan: dict):
    """
    Validate a compiled plan dict against basic structural rules.

    Checks: arc_id present, chapter_count > 0, required fields exist.
    Full arc-alignment validation requires the pipeline validators.
    """
    errors = []
    if not plan.get("arc_id"):
        errors.append("arc_id is required (Arc-First rule: no arc = no compile)")
    if not plan.get("persona"):
        errors.append("persona is required")
    if not plan.get("topic"):
        errors.append("topic is required")
    if not plan.get("engine"):
        errors.append("engine is required")

    chapters = plan.get("chapters", plan.get("chapter_slot_sequence", []))
    if not chapters:
        errors.append("No chapters/chapter_slot_sequence found")

    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})

    return {
        "valid": True,
        "arc_id": plan.get("arc_id"),
        "chapter_count": len(chapters),
    }

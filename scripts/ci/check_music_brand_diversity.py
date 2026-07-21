#!/usr/bin/env python3
"""Music-brand diversity gate — G1-G8 (the anti-copy-paste gate).

Ratified spec: MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES
(docs/PEARL_ARCHITECT_STATE.md); restated in artifacts/coordination/
ACTIVE_WORKSTREAMS.tsv row ws_pearl_dev_music_brand_diversity_ci_guard_20260611.
Metric math lives in ``scripts/qa/music_brand_diversity_lib.py`` (this script owns
I/O + policy only; it never re-implements a threshold).

Public entry point: ``evaluate_kit(payload)`` — this is the exact name
``phoenix_v4/musician/song_kit_generator.py``'s ``run_diversity_gate`` adapter
probes for, so kit generation reports real G1-G8 verdicts with zero further
changes to that adapter. It takes an in-memory payload and does NO file I/O
itself, so both the adapter and this file's own ``main()`` share one code path.

Phase-A degraded mode (N<50 catalog book-plan rows): only G1 (per-slot-pool
variant reuse, evaluated against the SOURCE atom bank pools) is meaningful and
runs; G2-G8 need catalog-scale N and are reported ``skipped`` with an explicit
"insufficient N" note rather than false-passing on tiny synthetic-scale data.
This is today's reality for every music-mode brand (catalog rows are downstream
of later lanes) — see docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/.

Usage:
  PYTHONPATH=. python3 scripts/ci/check_music_brand_diversity.py \\
      --brand-id ahjan_music --quality-profile production
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.qa import music_brand_diversity_lib as lib  # noqa: E402

REGISTRY_PATH = REPO_ROOT / "config/music/music_brand_registry.yaml"
MUSICIAN_BANKS_DIR = REPO_ROOT / "SOURCE_OF_TRUTH/musician_banks"
DEFAULT_OUT_DIR = REPO_ROOT / "artifacts/qa"

HARD_FAIL_GATES: tuple[str, ...] = ("G1", "G2", "G3", "G4", "G5")
WARN_GATES: tuple[str, ...] = ("G6", "G7", "G8")
ALL_GATES: tuple[str, ...] = HARD_FAIL_GATES + WARN_GATES


class BrandNotFoundError(RuntimeError):
    pass


def _display_path(path: Path) -> Path:
    """Relative-to-repo-root display path, falling back to the absolute path when
    the target lives outside the repo (e.g. a --out-dir override for local/CI dry-runs)."""
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


# ---------------------------------------------------------------------------------
# Disk loaders (the ONLY I/O in this module — evaluate_kit() itself is pure)
# ---------------------------------------------------------------------------------
def load_registry(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}


def resolve_musician_handle(brand_id: str, registry_path: Path = REGISTRY_PATH) -> str:
    registry = load_registry(registry_path)
    for row in registry.get("music_brands") or []:
        if row.get("brand_id") == brand_id:
            handle = row.get("musician_handle")
            if handle:
                return str(handle)
    raise BrandNotFoundError(f"brand_id={brand_id!r} not found in {_display_path(registry_path)}")


def load_pool_atoms(bank_dir: Path, pool: str) -> list[dict[str, Any]]:
    """Load atom yaml objects for one slot pool from approved_atoms/ + draft_atoms/
    (draft_atoms/ is included if a sibling lane has introduced that split; the
    directory simply does not exist yet otherwise)."""
    import yaml

    atoms: list[dict[str, Any]] = []
    for sub in ("approved_atoms", "draft_atoms"):
        pool_dir = bank_dir / sub / pool
        if not pool_dir.is_dir():
            continue
        for atom_file in sorted(pool_dir.glob("*.yaml")):
            obj = yaml.safe_load(atom_file.read_text(encoding="utf-8")) or {}
            if obj.get("atom_id"):
                atoms.append(obj)
    return atoms


def discover_pools(bank_dir: Path) -> list[str]:
    pools: set[str] = set()
    for sub in ("approved_atoms", "draft_atoms"):
        sub_dir = bank_dir / sub
        if sub_dir.is_dir():
            pools.update(p.name for p in sub_dir.iterdir() if p.is_dir())
    return sorted(pools)


def load_book_plans_for_brand(brand_id: str) -> list[dict[str, Any]]:
    """Catalog-scale book-plan metadata (topic/persona/format/locale/title/author_bio)
    for this brand, if any exists yet. Returns [] today for every music-mode brand —
    catalog generation is downstream of this lane (see lane 04 DISCOVERY REPORT)."""
    return []


def build_payload(brand_id: str, quality_profile: str, platform: str = "kdp_us") -> dict[str, Any]:
    handle = resolve_musician_handle(brand_id)
    bank_dir = MUSICIAN_BANKS_DIR / handle
    if not bank_dir.is_dir():
        raise BrandNotFoundError(
            f"musician bank dir not found for brand_id={brand_id!r} (handle={handle!r}): {bank_dir}"
        )
    pools = {pool: load_pool_atoms(bank_dir, pool) for pool in discover_pools(bank_dir)}
    return {
        "brand_id": brand_id,
        "musician_id": handle,
        "quality_profile": quality_profile,
        "platform": platform,
        "pools": pools,
        "books": load_book_plans_for_brand(brand_id),
    }


# ---------------------------------------------------------------------------------
# Public entry point — pure, no I/O. This is what song_kit_generator.run_diversity_
# gate() dynamically imports and calls.
# ---------------------------------------------------------------------------------
def evaluate_kit(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Compute G1-G8 for a payload of the shape ``run_diversity_gate`` builds:
    ``{"brand_id", "musician_id", "quality_profile", "pools": {pool: [atom_obj,...]}}``.
    ``payload["books"]`` (catalog-scale book-plan metadata) and
    ``payload["platform"]`` are optional; both default to the current small-N
    reality (no catalog rows yet, KDP US thresholds).
    """
    quality_profile = str(payload.get("quality_profile") or "draft")
    pools: Mapping[str, Any] = payload.get("pools") or {}
    books: list[Mapping[str, Any]] = list(payload.get("books") or [])
    platform = str(payload.get("platform") or "kdp_us")

    gates: dict[str, dict[str, Any]] = {}

    # G1 runs unconditionally: it evaluates the SOURCE atom pools themselves, which
    # exist regardless of catalog scale.
    per_pool_g1: dict[str, Any] = {}
    g1_violation = False
    for pool, atoms in pools.items():
        usages = [
            variant.get("body", "")
            for atom in atoms
            for variant in (atom.get("variants") or [])
        ]
        metric = lib.compute_variant_reuse(usages)
        per_pool_g1[pool] = metric
        g1_violation = g1_violation or metric["violation"]
    gates["G1"] = {
        "status": "fail" if g1_violation else "pass",
        "pools": per_pool_g1,
        "note": "per-slot-pool variant reuse against the source atom bank (Phase-A anti-copy-paste check)",
    }

    n_books = len(books)
    phase_a = n_books < lib.PHASE_A_N_THRESHOLD
    if phase_a:
        skip_note = (
            f"insufficient N ({n_books} catalog book-plan rows < {lib.PHASE_A_N_THRESHOLD}); "
            "Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only "
            "gate meaningful at this scale; catalog-scale gates skipped rather than "
            "false-passed on tiny data"
        )
        for gate_id in ("G2", "G3", "G4", "G5", "G6", "G7", "G8"):
            gates[gate_id] = {"status": "skipped", "note": skip_note}
    else:
        gates["G2"] = _status(lib.g2_topic_concentration(books))
        gates["G3"] = _status(lib.g3_persona_concentration(books))
        gates["G4"] = _status(lib.g4_format_concentration(books))
        gates["G5"] = _status(lib.g5_locale_concentration(books, platform=platform))
        gates["G6"] = _status(lib.g6_title_clusters([b.get("title", "") for b in books]))
        gates["G7"] = _status(lib.g7_author_bio_reuse([b.get("author_bio", "") for b in books]))
        gates["G8"] = {
            "status": "skipped",
            "note": "G8 rotation Gini requires per-book atom-usage logs not yet produced by any catalog generator",
        }

    hard_failures = [g for g in HARD_FAIL_GATES if gates.get(g, {}).get("status") == "fail"]
    warnings = [g for g in WARN_GATES if gates.get(g, {}).get("status") == "fail"]

    if hard_failures and quality_profile == "production":
        overall = "HARD_FAIL"
    elif hard_failures or warnings:
        overall = "WARN"
    else:
        overall = "PASS"

    return {
        "brand_id": payload.get("brand_id"),
        "musician_id": payload.get("musician_id"),
        "quality_profile": quality_profile,
        "platform": platform,
        "phase": "phase_a_degraded" if phase_a else "full",
        "n_books": n_books,
        "gates": gates,
        "hard_failures": hard_failures,
        "warnings": warnings,
        "overall": overall,
    }


def _status(metric: dict[str, Any]) -> dict[str, Any]:
    if metric.get("n", 0) == 0:
        return {"status": "skipped", "note": "no data", **metric}
    return {"status": "fail" if metric.get("violation") else "pass", **metric}


# ---------------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------------
def render_report(verdict: dict[str, Any], *, brand_id: str, batch_id: str) -> str:
    lines = [
        "# Music Brand Diversity Gate Report (G1-G8)",
        "",
        f"brand_id={brand_id}",
        f"batch_id={batch_id}",
        f"musician_id={verdict.get('musician_id')}",
        f"quality_profile={verdict.get('quality_profile')}",
        f"phase={verdict.get('phase')}",
        f"n_books={verdict.get('n_books')}",
        f"overall={verdict.get('overall')}",
        "",
        "## Gates",
        "",
    ]
    for gate_id in ALL_GATES:
        gate = verdict.get("gates", {}).get(gate_id, {"status": "missing"})
        tier = "HARD_FAIL" if gate_id in HARD_FAIL_GATES else "WARN"
        lines.append(f"- **{gate_id}** ({tier}) — status={gate.get('status')}")
        if gate.get("note"):
            lines.append(f"  - note: {gate['note']}")
        if gate_id == "G1" and gate.get("pools"):
            for pool, metric in gate["pools"].items():
                lines.append(
                    f"  - {pool}: n={metric['n']} limit={metric['limit']} "
                    f"max_reuse={metric['max_reuse']} violation={metric['violation']}"
                )
    lines += [
        "",
        "## Limitations",
        "",
        (
            "Phase-A degraded mode: this brand has no catalog-scale book-plan data yet "
            "(0 rows found), so G2-G8 are reported skipped rather than fabricated as "
            "passing — see DO NOT list in "
            "docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/"
            "04_Pearl_Dev_diversity_ci_guard.md."
            if verdict.get("phase") == "phase_a_degraded"
            else "Full catalog-scale evaluation."
        ),
        "",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand-id", required=True, help="e.g. ahjan_music")
    parser.add_argument(
        "--quality-profile",
        default="draft",
        choices=["draft", "production"],
        help="mirrors run_pipeline.py's --quality-profile convention",
    )
    parser.add_argument("--platform", default="kdp_us", help="G5 per-platform locale threshold key")
    parser.add_argument("--batch-id", default=None, help="defaults to a date stamp")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="where to write the .md + .json report (default artifacts/qa/)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="skip writing report files (for local/CI dry-runs and tests)",
    )
    args = parser.parse_args(argv)

    batch_id = args.batch_id or datetime.date.today().isoformat().replace("-", "")

    try:
        payload = build_payload(args.brand_id, args.quality_profile, platform=args.platform)
    except BrandNotFoundError as exc:
        print(f"❌ MUSIC BRAND DIVERSITY GATE — {exc}", file=sys.stderr)
        return 1

    verdict = evaluate_kit(payload)
    report_text = render_report(verdict, brand_id=args.brand_id, batch_id=batch_id)
    print(report_text)

    if not args.no_write:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        md_path = args.out_dir / f"music_brand_diversity_report_{args.brand_id}_{batch_id}.md"
        json_path = md_path.with_suffix(".json")
        md_path.write_text(report_text, encoding="utf-8")
        json_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
        print(f"wrote {_display_path(md_path)}")
        print(f"wrote {_display_path(json_path)}")

    return 1 if verdict["overall"] == "HARD_FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())

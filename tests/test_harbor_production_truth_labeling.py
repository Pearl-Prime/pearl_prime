"""Harbor Line / Kamiko Parker truth labeling: catalog metadata is not shippable production.

Locks the invariant that a packet-bridge "buildable" verdict can never outrank
``production_files_ready: false``. See scripts/ci/check_harbor_production_truth_labeling.py.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/ci/check_harbor_production_truth_labeling.py"
STABILIZER_DELIVERY = ROOT / "brand-wizard-app/public/brand_deliveries/stabilizer.json"


def _run_gate(repo_root: Path) -> subprocess.CompletedProcess[str]:
    """Run the gate that lives inside ``repo_root``.

    The gate resolves its own ROOT from ``__file__``, so the copy under the target repo must
    be invoked — passing ``cwd`` alone would silently re-check the real repo.
    """
    gate = repo_root / "scripts/ci" / CHECK.name
    return subprocess.run(
        [sys.executable, str(gate)], cwd=repo_root, capture_output=True, text=True
    )


def test_truth_labeling_gate_passes_on_repo() -> None:
    proc = _run_gate(ROOT)
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_harbor_delivery_is_production_pending_not_shippable() -> None:
    """Harbor Line is catalog-ready only; nothing here may claim shippable production files."""
    data = json.loads(STABILIZER_DELIVERY.read_text(encoding="utf-8"))
    assert data["display_brand"] == "Harbor Line Books"
    assert data["brand_director_name"] == "Kamiko Parker"
    assert data["production_files_ready"] is False
    assert data["delivery_status"] == "catalog_ready_production_files_pending"
    books = data["weeks"]["2026-W29"]["catalog_metadata"]
    assert books, "expected Harbor catalog metadata to stay visible (label, do not hide)"
    assert all(b["production_files_ready"] is False for b in books)


def test_gate_catches_bridge_ready_outranking_production_pending(tmp_path: Path) -> None:
    """The regression this gate exists for: bridge says buildable, production files do not exist."""
    import shutil

    work = tmp_path / "repo"
    (work / "scripts/ci").mkdir(parents=True)
    (work / "brand-wizard-app/public/brand_deliveries").mkdir(parents=True)
    shutil.copy(CHECK, work / "scripts/ci" / CHECK.name)
    shutil.copy(STABILIZER_DELIVERY, work / "brand-wizard-app/public/brand_deliveries/stabilizer.json")

    handoff = ROOT / "brand-wizard-app/public/brand_handoff_dashboard.html"
    weekly = ROOT / "brand_admin_weekly_os.html"
    shutil.copy(weekly, work / "brand_admin_weekly_os.html")

    # Reintroduce the pre-fix precedence: the bridge verdict wins outright.
    broken = handoff.read_text(encoding="utf-8").replace(
        '  if(pendingProduction) return {state:"blocked", reason:"Catalog ready, production files pending."};\n  return bridgeVerdict;',
        "  return bridgeVerdict;",
    )
    (work / "brand-wizard-app/public/brand_handoff_dashboard.html").write_text(broken, encoding="utf-8")

    proc = _run_gate(work)
    assert proc.returncode == 1, "gate must fail when a bridge 'ready' verdict outranks production-pending"
    assert "authoritative" in proc.stderr

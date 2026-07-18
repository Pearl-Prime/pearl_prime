"""Registry-mode pipeline must carry runtime_format_id for word-count gating."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_registry_plan_json_includes_runtime_format_id() -> None:
    arc = (
        REPO_ROOT
        / "config"
        / "source_of_truth"
        / "master_arcs"
        / "gen_z_professionals__anxiety__overwhelm__F006.yaml"
    )
    if not arc.exists():
        return
    run_pipeline = REPO_ROOT / "scripts" / "run_pipeline.py"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "plan.json"
        cmd = [
            sys.executable,
            str(run_pipeline),
            "--topic",
            "anxiety",
            "--persona",
            "gen_z_professionals",
            "--arc",
            str(arc),
            "--pipeline-mode",
            "registry",
            "--out",
            str(out),
            "--no-generate-freebies",
            "--no-update-freebie-index",
            "--no-job-check",
        ]
        result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
        assert result.returncode == 0, result.stderr + result.stdout
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data.get("source") == "section_registry"
        assert data.get("runtime_format_id"), "registry plan must expose runtime_format_id for render gates"
        assert data.get("format_id"), "registry plan should carry structural format id"


def test_resolved_runtime_format_id_reads_format_runtime_id() -> None:
    from scripts.run_pipeline import _resolved_runtime_format_id

    class _A:
        runtime_format = ""

    assert _resolved_runtime_format_id(_A(), {"format_runtime_id": "short_book_30"}) == "short_book_30"


def test_resolved_runtime_format_cli_overrides_plan() -> None:
    from scripts.run_pipeline import _resolved_runtime_format_id

    class _A:
        runtime_format = "standard_book"

    assert _resolved_runtime_format_id(_A(), {"format_runtime_id": "short_book_30"}) == "standard_book"

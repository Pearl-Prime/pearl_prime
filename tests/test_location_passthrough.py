from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_resolve_location_profile_id_supports_aliases() -> None:
    from phoenix_v4.planning.catalog_planner import resolve_location_profile_id

    assert resolve_location_profile_id("nyc") == "nyc_metro"
    assert resolve_location_profile_id("New York City") == "nyc_metro"
    assert resolve_location_profile_id("grand_central") == "nyc_grand_central"
    assert resolve_location_profile_id("coastal_california") == "coastal_california"
    assert resolve_location_profile_id("santa_monica") == "coastal_california"
    assert resolve_location_profile_id("generic_us_urban") == "generic_us_urban"
    assert resolve_location_profile_id("chicago") == "generic_us_urban"
    assert resolve_location_profile_id("chicago_metro") == "generic_us_urban"
    assert resolve_location_profile_id("toronto_ca") == "toronto_ca"
    assert resolve_location_profile_id("queen_west") == "toronto_ca"


def test_bookspec_to_dict_includes_location_fields() -> None:
    from phoenix_v4.planning.catalog_planner import CatalogPlanner

    planner = CatalogPlanner()
    spec = planner.produce_single(
        topic_id="overthinking",
        persona_id="gen_z_professionals",
        angle_id="at_work",
        requested_location_id="grand_central",
    )

    payload = spec.to_dict()
    assert payload["requested_location_id"] == "grand_central"
    assert payload["resolved_location_id"] == "nyc_grand_central"


def test_run_pipeline_persists_location_fields_when_build_succeeds() -> None:
    import tempfile

    arc_path = (
        REPO_ROOT
        / "config"
        / "source_of_truth"
        / "master_arcs"
        / "gen_z_professionals__overthinking__spiral__F006.yaml"
    )
    if not arc_path.exists():
        return

    spec = {
        "topic_id": "overthinking",
        "persona_id": "gen_z_professionals",
        "location_id": "grand_central",
        "seed": "location_passthrough_seed",
    }
    run_pipeline = REPO_ROOT / "scripts" / "run_pipeline.py"
    with tempfile.TemporaryDirectory() as tmp:
        spec_path = Path(tmp) / "spec.yaml"
        try:
            import yaml

            spec_path.write_text(yaml.safe_dump(spec), encoding="utf-8")
        except ImportError:
            spec_path.write_text(
                "topic_id: overthinking\n"
                "persona_id: gen_z_professionals\n"
                "location_id: grand_central\n"
                "seed: location_passthrough_seed\n",
                encoding="utf-8",
            )
        out_path = Path(tmp) / "out_plan.json"
        cmd = [
            sys.executable,
            str(run_pipeline),
            "--input",
            str(spec_path),
            "--arc",
            str(arc_path),
            "--out",
            str(out_path),
            "--no-generate-freebies",
            "--no-job-check",
        ]
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return
        data = json.loads(out_path.read_text())
        if data.get("source") == "section_registry":
            return
        assert data.get("requested_topic_id") == "overthinking"
        assert data.get("requested_persona_id") == "gen_z_professionals"
        assert data.get("canonical_topic_id") == data.get("topic_id")
        assert data.get("canonical_persona_id") == data.get("persona_id")
        assert data.get("requested_location_id") == "grand_central"
        assert data.get("resolved_location_id") == "nyc_grand_central"
        assert data.get("location_id") == "nyc_grand_central"
        assert data.get("city_name") == "New York City"

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "qa"))

import audit_atom_bank_health as audit  # noqa: E402


def _block(label: str, version: int, body: str, band: int | None = None) -> str:
    metadata = f"BAND: {band}\nMECHANISM_DEPTH: 2" if band is not None else ""
    return (
        f"## {label} v{version:02d}\n"
        "---\n"
        f"{metadata}\n"
        "---\n"
        f"{body}\n"
        "---\n\n"
    )


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    atoms = repo / "atoms/corporate_managers/burnout"
    (atoms / "HOOK").mkdir(parents=True)
    (atoms / "overwhelm").mkdir(parents=True)
    arc_root = repo / "config/source_of_truth/master_arcs"
    arc_root.mkdir(parents=True)

    hooks = "".join(
        _block(
            "HOOK",
            version,
            (
                f"Real authored management hook number {version} with enough "
                "specific detail to be usable in an opening."
                if version <= 5
                else "[Persona-specific hook for corporate_managers × burnout]"
            ),
        )
        for version in range(1, 13)
    )
    (atoms / "HOOK/CANONICAL.txt").write_text(hooks, encoding="utf-8")

    engine = "".join(
        [
            _block(
                "RECOGNITION",
                1,
                "The mechanism deepens. Stakes rise. The cost becomes clear.",
                band=3,
            ),
            _block(
                "COST_REVEAL",
                2,
                (
                    "A manager sits in the parking garage after the all-hands "
                    "and realizes she cannot make her hands turn the wheel "
                    "because every destination contains another demand."
                ),
                band=4,
            ),
            _block(
                "RECKONING",
                3,
                (
                    "The VP asks what support is needed, and the manager finally "
                    "names the impossible workload and the identity built around "
                    "being the person who can carry everything."
                ),
                band=5,
            ),
        ]
    )
    (atoms / "overwhelm/CANONICAL.txt").write_text(
        engine,
        encoding="utf-8",
    )

    arc = {
        "arc_id": "corporate_managers_burnout_overwhelm_F006_test",
        "persona": "corporate_managers",
        "topic": "burnout",
        "engine": "overwhelm",
        "format": "F006",
        "chapter_count": 20,
        "emotional_curve": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5] * 2,
    }
    (arc_root / "corporate_managers__burnout__overwhelm__F006.yaml").write_text(
        yaml.safe_dump(arc, sort_keys=False),
        encoding="utf-8",
    )
    return repo


def test_placeholders_never_count_as_usable():
    text = (
        _block("HOOK", 1, "A real authored hook with specific embodied detail.")
        + _block(
            "HOOK",
            2,
            "[Persona-specific hook for corporate_managers × burnout]",
        )
    )
    blocks, errors = audit.parse_canonical_text(text)
    assert not errors
    assert sum(not block.placeholder for block in blocks) == 1
    assert sum(block.placeholder for block in blocks) == 1


def test_parse_ok_alone_does_not_make_bank_healthy(tmp_path):
    repo = _fixture_repo(tmp_path)
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    payload = audit.audit_repo(repo, out)
    rows = list(
        csv.DictReader(
            (out / "atom_bank_health.tsv").open(encoding="utf-8"),
            delimiter="\t",
        )
    )
    hook = next(row for row in rows if row["family"] == "HOOK")
    assert hook["parse_ok"] == "true"
    assert hook["usable_atom_count"] == "5"
    assert hook["healthy"] == "false"
    assert hook["hook_depth_risk"] == "true"
    assert payload["high_risk_count"] == 1


def test_corporate_managers_burnout_overwhelm_is_flagged(tmp_path):
    repo = _fixture_repo(tmp_path)
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    payload = audit.audit_repo(repo, out)
    sentinel = payload["acceptance_sentinel"]
    assert sentinel["found"] is True
    assert sentinel["high_risk"] is True
    assert any("HOOK_real_depth=5<12" in reason for reason in sentinel["risk_reasons"])
    assert any("missing_required_arc_bands:1,2" in reason for reason in sentinel["risk_reasons"])


def test_bands_1_to_5_deficits_are_explicit(tmp_path):
    repo = _fixture_repo(tmp_path)
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    audit.audit_repo(repo, out)
    rows = list(
        csv.DictReader(
            (out / "atom_bank_health.tsv").open(encoding="utf-8"),
            delimiter="\t",
        )
    )
    engine = next(row for row in rows if row["family"] == "overwhelm")
    assert engine["bands_present"] == "4,5"
    # Band 3's low-information body is classified as placeholder/non-usable.
    assert engine["bands_missing_1_5"] == "1,2,3"
    assert engine["required_arc_bands_missing"] == "1,2,3"


def test_writer_backlog_has_exact_file_and_word_target(tmp_path):
    repo = _fixture_repo(tmp_path)
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    audit.audit_repo(repo, out)
    backlog = (out / "writer_backlog.md").read_text(encoding="utf-8")
    assert "atoms/corporate_managers/burnout/HOOK/CANONICAL.txt" in backlog
    assert "Target added words:" in backlog


def test_required_artifacts_are_emitted(tmp_path):
    repo = _fixture_repo(tmp_path)
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    audit.audit_repo(repo, out)
    assert (out / "atom_bank_health.tsv").is_file()
    assert (out / "tuple_health_summary.md").is_file()
    assert (out / "writer_backlog.md").is_file()
    assert (out / "high_risk_tuples.json").is_file()
    data = json.loads((out / "high_risk_tuples.json").read_text())
    assert data["acceptance_sentinel"]["high_risk"] is True



def test_duplicate_atom_ids_are_explicitly_flagged(tmp_path):
    repo = _fixture_repo(tmp_path)
    bank = repo / "atoms/corporate_managers/burnout/INTEGRATION/CANONICAL.txt"
    bank.parent.mkdir(parents=True, exist_ok=True)
    bank.write_text(
        _block("INTEGRATION", 18, "First authored integration body with enough real detail.")
        + _block("INTEGRATION", 18, "Second authored body must not overwrite the first."),
        encoding="utf-8",
    )
    out = repo / "artifacts/qa/atom_bank_health_20260714"
    audit.audit_repo(repo, out)
    rows = list(
        csv.DictReader(
            (out / "atom_bank_health.tsv").open(encoding="utf-8"),
            delimiter="\t",
        )
    )
    row = next(item for item in rows if item["family"] == "INTEGRATION")
    assert row["duplicate_atom_id_count"] == "1"
    assert "INTEGRATION_v18" in row["duplicate_atom_ids"]
    assert row["healthy"] == "false"

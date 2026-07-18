from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "ci" / "check_voice_audition_contract.py"
SPEC = importlib.util.spec_from_file_location("check_voice_audition_contract", MODULE_PATH)
voice_contract = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(voice_contract)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_voice_audition_contract_accepts_allowlisted_pending_assignments(tmp_path, monkeypatch) -> None:
    repo = tmp_path
    locale_path = repo / "config" / "localization" / "brand_registry_locale_extension.yaml"
    pending_path = repo / "config" / "voice_auditions" / "pending_voice_assignments.yaml"

    _write_yaml(
        locale_path,
        {
            "brands": {
                "sleep_repair_tw": {
                    "locale": "zh-TW",
                    "voice_identity": {
                        "elevenlabs_voice_id": "TBD",
                        "google_voice": "cmn-TW-Wavenet-A",
                    },
                },
                "stabilizer_hu": {
                    "locale": "hu-HU",
                    "voice_identity": {
                        "google_voice": "hu-HU-Standard-A",
                        "elevenlabs_preferred": True,
                    },
                },
            }
        },
    )
    _write_yaml(
        pending_path,
        {
            "pending_assignments": [
                {
                    "brand_id": "sleep_repair_tw",
                    "locale": "zh-TW",
                    "placeholder": "TBD",
                    "status": "pending_audition",
                    "fallback_voice_id": "cmn-TW-Wavenet-A",
                },
                {
                    "brand_id": "stabilizer_hu",
                    "locale": "hu-HU",
                    "placeholder": None,
                    "status": "pending_audition",
                    "fallback_voice_id": "hu-HU-Standard-A",
                },
            ]
        },
    )

    monkeypatch.setattr(voice_contract, "REPO_ROOT", repo)
    monkeypatch.setattr(voice_contract, "LOCALE_EXTENSION_PATH", locale_path)
    monkeypatch.setattr(voice_contract, "PENDING_ASSIGNMENTS_PATH", pending_path)

    assert voice_contract.main() == 0


def test_voice_audition_contract_rejects_untracked_placeholder(tmp_path, monkeypatch) -> None:
    repo = tmp_path
    locale_path = repo / "config" / "localization" / "brand_registry_locale_extension.yaml"
    pending_path = repo / "config" / "voice_auditions" / "pending_voice_assignments.yaml"

    _write_yaml(
        locale_path,
        {
            "brands": {
                "sleep_repair_tw": {
                    "locale": "zh-TW",
                    "voice_identity": {
                        "elevenlabs_voice_id": "TBD",
                        "google_voice": "cmn-TW-Wavenet-A",
                    },
                }
            }
        },
    )
    _write_yaml(pending_path, {"pending_assignments": []})

    monkeypatch.setattr(voice_contract, "REPO_ROOT", repo)
    monkeypatch.setattr(voice_contract, "LOCALE_EXTENSION_PATH", locale_path)
    monkeypatch.setattr(voice_contract, "PENDING_ASSIGNMENTS_PATH", pending_path)

    assert voice_contract.main() == 1

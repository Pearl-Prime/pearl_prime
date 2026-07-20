"""Phase C proofs: hybrid generation + 409 offer routing + cap."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from phoenix_v4.brand_generation import (
    generate_hybrid_brand,
    generate_teacher_owned_brand,
    list_available_hybrid_archetypes,
    token_overlap_ratio,
)
from server.routes.brand_onboarding import (
    HybridAcceptRequest,
    OnboardingSubmission,
    _brands_index,
    _teacher_identity,
    _valid_brand_ids,
    accept_hybrid_brand,
    submit_onboarding,
)


def test_valid_brand_ids_includes_teacher_originated_without_touching_40():
    ids = _valid_brand_ids()
    assert "stillness_press_en_us" in ids
    sample = generate_teacher_owned_brand("master_wu", seed="valid_ids_c", register=True)
    assert sample["brand_id"] in _valid_brand_ids()
    assert "stillness_press_en_us" in _valid_brand_ids()


def test_teacher_originated_skips_exclusivity_ledger():
    sample = generate_teacher_owned_brand("miki", seed="skip_ledger_c", register=True)
    assert _teacher_identity(sample["brand_id"], _brands_index()) is None


def test_hybrid_differs_from_named_and_is_generalized(tmp_path, monkeypatch):
    import phoenix_v4.brand_generation.teacher_brand_generator as mod

    reg = tmp_path / "teacher_originated_brands.yaml"
    pub = tmp_path / "teacher_originated_brands.json"
    reg.write_text("schema_version: '1.0'\nsource: teacher_originated\nbrands: {}\n", encoding="utf-8")
    monkeypatch.setattr(mod, "TEACHER_ORIGINATED", reg)
    monkeypatch.setattr(mod, "PUBLIC_INDEX", pub)

    named = generate_teacher_owned_brand("master_feung", seed="hy_diff", register=True)
    available = list_available_hybrid_archetypes("master_feung", "en_US")
    arch = "stillness_press" if "stillness_press" in available else available[0]
    hybrid = generate_hybrid_brand("master_feung", arch, seed="hy_diff", lane_id="en_US", register=True)
    assert hybrid["attribution_mode"] == "generalized"
    assert hybrid["hybrid_of_archetype"] == arch
    og = token_overlap_ratio(json.dumps(named["gtm_identity"]), json.dumps(hybrid["gtm_identity"]))
    assert og < 0.85  # must not be a copy of the named brand
    # Reader-facing imprint must not carry the teacher's personal name (generalized mode).
    imprint = " ".join(
        [
            hybrid.get("display_name") or "",
            hybrid.get("mission") or "",
            hybrid.get("brand_focus") or "",
            (hybrid.get("gtm_identity") or {}).get("emotional_job") or "",
            (hybrid.get("gtm_identity") or {}).get("doctrine_lead") or "",
        ]
    ).lower()
    assert "feung" not in imprint
    assert "master feung" not in imprint


def test_accept_hybrid_endpoint_and_cap(tmp_path, monkeypatch):
    import phoenix_v4.brand_generation.teacher_brand_generator as mod

    reg = tmp_path / "teacher_originated_brands.yaml"
    pub = tmp_path / "teacher_originated_brands.json"
    reg.write_text("schema_version: '1.0'\nsource: teacher_originated\nbrands: {}\n", encoding="utf-8")
    monkeypatch.setattr(mod, "TEACHER_ORIGINATED", reg)
    monkeypatch.setattr(mod, "PUBLIC_INDEX", pub)

    available = list_available_hybrid_archetypes("adi_da", "en_US")
    arch = available[0]
    out = accept_hybrid_brand(
        HybridAcceptRequest(teacher_id="adi_da", archetype_id=arch, lane="en_US", seed="cap")
    )
    assert out["status"] == "hybrid_created"
    assert out["brand_id"].startswith("hy_adi_da_")
    assert arch not in out["remaining_archetypes"]

    with pytest.raises(HTTPException) as got:
        accept_hybrid_brand(
            HybridAcceptRequest(teacher_id="adi_da", archetype_id=arch, lane="en_US", seed="cap")
        )
    assert got.value.status_code == 409
    assert got.value.detail["error"] == "hybrid_already_exists"


def test_teacher_claimed_offer_shape(monkeypatch, tmp_path):
    """Simulate second claim → 409 includes offer object (409 trigger preserved)."""
    import server.routes.brand_onboarding as bo

    # Point claims ledger at temp file with a prior claim
    claims = tmp_path / "teacher_claims.yaml"
    claims.write_text(
        "claims:\n  en_US__master_feung:\n    brand_id: some_teacher_brand_en_us\n    email: first@example.invalid\n    ts: '2026-07-20T00:00:00Z'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bo, "TEACHER_CLAIMS_YAML", claims)

    # Force teacher identity for the posted brand
    monkeypatch.setattr(
        bo,
        "_teacher_identity",
        lambda brand_id, index: ("en_US", "master_feung"),
    )
    monkeypatch.setattr(bo, "_valid_brand_ids", lambda: {"stillness_press_en_us"})
    monkeypatch.setattr(
        bo,
        "_brands_index",
        lambda: {"stillness_press_en_us": {"buildable": True, "arch": "stillness_press", "lane": "en_US", "is_teacher": True, "tid": "master_feung"}},
    )
    monkeypatch.setattr(bo, "_assignment_conflict", lambda brand_id, index: None)
    monkeypatch.setattr(bo, "_is_catalog_bearing", lambda brand_id, index: True)

    req = OnboardingSubmission(
        brand_id="stillness_press_en_us",
        lane="en_US",
        publication_corp="Stillness Press",
        brand_email="second@example.invalid",
        contact={"first_name": "Second", "last_name": "Claimant"},
        brand_director_name="Second Claimant",
        wizard_yaml="brand_id: stillness_press_en_us\n",
    )
    with pytest.raises(HTTPException) as got:
        submit_onboarding(req)
    assert got.value.status_code == 409
    detail = got.value.detail
    assert detail["error"] == "teacher_claimed"
    assert detail["offer"]["mode"] == "generalized_hybrid"
    assert isinstance(detail["offer"]["available_archetypes"], list)

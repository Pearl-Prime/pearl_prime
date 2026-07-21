"""Phase B proofs for teacher-owned brand generation (deterministic, no LLM)."""
from __future__ import annotations

import json

from phoenix_v4.brand_generation import generate_teacher_owned_brand, token_overlap_ratio


def test_named_brands_differentiated_for_pilot_teachers():
    a = generate_teacher_owned_brand("master_feung", seed="unit_diff", register=False)
    b = generate_teacher_owned_brand("adi_da", seed="unit_diff", register=False)
    c = generate_teacher_owned_brand("ahjan", seed="unit_diff", register=False)
    for x, y in ((a, b), (a, c), (b, c)):
        og = token_overlap_ratio(json.dumps(x["gtm_identity"]), json.dumps(y["gtm_identity"]))
        oe = token_overlap_ratio(
            json.dumps(x["emotional_vocabulary"]), json.dumps(y["emotional_vocabulary"])
        )
        assert og < 0.55, (x["brand_id"], y["brand_id"], og)
        assert oe < 0.55, (x["brand_id"], y["brand_id"], oe)


def test_named_brand_schema_fields():
    b = generate_teacher_owned_brand("master_wu", seed="schema", register=False)
    assert b["source"] == "teacher_originated"
    assert b["attribution_mode"] == "named"
    assert b["origin_teacher_id"] == "master_wu"
    assert b["gtm_identity"]["emotional_job"]
    assert b["emotional_vocabulary"]["core"]
    assert b["duration_strategy"]
    assert b["cover_art_identity"]["treatment"]
    assert b["pricing_posture"]
    assert b["generation"]["llm"] is False
    assert b["brand_id"].startswith("to_master_wu_")

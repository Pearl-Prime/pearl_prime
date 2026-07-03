"""Restore workstream #4: purpose-seeded pool index kills cross-section dups."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from phoenix_v4.planning.registry_resolver import _deterministic_index

REPO = Path(__file__).resolve().parents[3]
MOD_PATH = REPO / "scripts" / "registry" / "generate_topic_registry.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("generate_topic_registry", MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_purpose_seeded_index_diverges_across_sections():
    gen = _load_mod()
    pool_size = 90
    # Same type, same variant_i, different purpose → different index (usually).
    a = gen.purpose_seeded_index(
        "financial_stress", "chapter_01", "section_02",
        "Phone-bank balance check at 11pm", 0, pool_size,
    )
    b = gen.purpose_seeded_index(
        "financial_stress", "chapter_01", "section_03",
        "Partner conversation about the bill", 0, pool_size,
    )
    c = gen.purpose_seeded_index(
        "financial_stress", "chapter_01", "section_04",
        "Coworker lunch when the card declines", 0, pool_size,
    )
    assert len({a, b, c}) == 3


def test_purpose_seeded_index_stable():
    gen = _load_mod()
    kwargs = dict(
        topic="anxiety",
        ch_key="chapter_01",
        sec_key="section_02",
        purpose="digital doomscroll",
        variant_i=1,
        pool_size=40,
    )
    assert gen.purpose_seeded_index(**kwargs) == gen.purpose_seeded_index(**kwargs)


def test_purpose_seeded_index_varies_by_variant_i():
    gen = _load_mod()
    idxs = {
        gen.purpose_seeded_index("anxiety", "chapter_01", "section_02", "p", i, 50)
        for i in range(10)
    }
    assert len(idxs) > 1


def test_resolver_seed_includes_purpose():
    # Same seed/ch/sec, different purpose → different index.
    pool = 40
    a = _deterministic_index("book:chapter_01:section_02:digital purpose:persona", pool)
    b = _deterministic_index("book:chapter_01:section_02:relational purpose:persona", pool)
    assert a != b


def test_all_topics_includes_reconciled_set():
    gen = _load_mod()
    for topic in ("adhd_focus", "grief", "mindfulness", "somatic_healing"):
        assert topic in gen.ALL_TOPICS
    assert len(gen.ALL_TOPICS) == 17


def test_generate_variants_persists_provenance(monkeypatch):
    gen = _load_mod()
    monkeypatch.setattr(gen, "_load_cached", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_save_cache", lambda *a, **k: None)
    monkeypatch.setattr(gen, "_track", lambda *a, **k: None)
    monkeypatch.setattr(
        gen,
        "qwen_generate",
        lambda **k: (_ for _ in ()).throw(AssertionError("should use pool")),
    )
    pool = [f"atom body number {n} " + ("x" * 60) for n in range(20)]
    variants, _prov = gen.generate_variants(
        topic="anxiety",
        ch_key="chapter_01",
        sec_key="section_01",
        sec_spec={
            "seq": 1,
            "type": "HOOK",
            "scene_type": None,
            "location_aware": False,
            "min_variants": 3,
        },
        sec_id="ch01_sec01",
        section_purpose="Opening recognition",
        chapter_title="Chapter 1",
        arc_role="recognition",
        skin={},
        persona_atoms={"HOOK": pool},
        teacher_atoms={},
        min_variants=3,
        dry_run=False,
        resume=False,
    )
    assert all(v.get("_provenance") == "atom_pool" for v in variants)

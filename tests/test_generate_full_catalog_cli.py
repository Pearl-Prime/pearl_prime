from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.generate_full_catalog as gen
from phoenix_v4.planning.catalog_planner import AtomsModel, BookSpec


def _fake_specs(brand_id: str, count: int) -> list[BookSpec]:
    return [
        BookSpec(
            topic_id="grief",
            persona_id=f"persona_{i}",
            series_id=f"series_{i}",
            installment_number=i + 1,
            teacher_id="default_teacher",
            brand_id=brand_id,
            angle_id="grief_general",
            domain_id="grief_cluster",
            seed=f"seed:{brand_id}:{i}",
            teacher_mode=False,
            atoms_model=AtomsModel.CLUSTER,
        )
        for i in range(count)
    ]


def test_load_brand_ids_from_yaml_validates_total_brands(tmp_path: Path) -> None:
    path = tmp_path / "brands.yaml"
    path.write_text("total_brands: 2\nbrands:\n  only_one: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="brand-count drift"):
        gen._load_brand_ids_from_yaml(path)


def test_main_books_per_brand_plan_only_writes_expected_count(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    brand_list = tmp_path / "brands.yaml"
    brand_list.write_text(
        "total_brands: 2\nbrands:\n  alpha: {}\n  beta: {}\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "candidates"

    def fake_generate_for_brand(self, brand_id: str, n: int, **_: object) -> list[BookSpec]:
        return _fake_specs(brand_id, n)

    monkeypatch.setattr(
        "phoenix_v4.planning.catalog_planner.CatalogPlanner.generate_for_brand",
        fake_generate_for_brand,
    )
    monkeypatch.setattr(gen, "_available_arc_persona_topic_pairs", lambda: {(f"persona_{i}", "grief") for i in range(8)})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_full_catalog.py",
            "--all-brands-from",
            str(brand_list),
            "--books-per-brand",
            "2",
            "--plan-only",
            "--candidates-dir",
            str(out_dir),
        ],
    )

    rc = gen.main()

    assert rc == 0
    files = sorted(out_dir.glob("*.spec.json"))
    assert len(files) == 4
    brand_ids = [json.loads(path.read_text(encoding="utf-8"))["brand_id"] for path in files]
    assert brand_ids.count("alpha") == 2
    assert brand_ids.count("beta") == 2


def test_collect_compileable_brand_specs_retries_until_target(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakePlanner:
        def __init__(self) -> None:
            self.calls = 0

        def generate_for_brand(self, brand_id: str, n: int, **_: object) -> list[BookSpec]:
            self.calls += 1
            if self.calls == 1:
                return _fake_specs(brand_id, 1)
            return [
                BookSpec(
                    topic_id="grief",
                    persona_id="good_persona",
                    series_id="series_good",
                    installment_number=1,
                    teacher_id="default_teacher",
                    brand_id=brand_id,
                    angle_id="grief_general",
                    domain_id="grief_cluster",
                    seed="seed:good",
                    teacher_mode=False,
                    atoms_model=AtomsModel.CLUSTER,
                )
            ]

    monkeypatch.setattr(gen, "_available_arc_persona_topic_pairs", lambda: {("good_persona", "grief")})

    specs = gen._collect_compileable_brand_specs(
        FakePlanner(),
        brand_id="alpha",
        count=1,
        seed="seed",
        teacher_id="default_teacher",
    )

    assert len(specs) == 1
    assert specs[0].persona_id == "good_persona"


def test_catalog_generate_full_catalog_bootstraps_repo_root_on_sys_path() -> None:
    module_path = REPO_ROOT / "scripts" / "catalog" / "generate_full_catalog.py"
    spec = importlib.util.spec_from_file_location("catalog_generate_full_catalog_bootstrap", module_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["catalog_generate_full_catalog_bootstrap"] = mod

    spec.loader.exec_module(mod)

    assert str(REPO_ROOT) in sys.path
    assert hasattr(mod, "main")

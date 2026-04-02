from pathlib import Path

from phoenix_v4.planning.pool_index import AtomEntry, _load_teacher_pool
from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class _DummyPoolIndex:
    def __init__(self, pool):
        self._pool = pool

    def get_pool(self, slot_type, persona_id, topic_id, format_plan, required_count=None, teacher_exercise_fallback=False):
        return list(self._pool)


def test_load_teacher_story_universal_sets_band_and_wildcard(tmp_path: Path) -> None:
    root = tmp_path / "approved_atoms"
    _write_yaml(
        root / "STORY" / "story_u.yaml",
        "atom_id: s1\nband: universal\nemotional_intensity_band: 2\nsource: native\n",
    )
    pool = _load_teacher_pool(root, "STORY")
    assert len(pool) == 1
    assert (pool[0].metadata or {}).get("band") == 2
    assert (pool[0].metadata or {}).get("band_universal") is True


def test_resolver_allows_universal_story_for_any_required_band() -> None:
    pool = [AtomEntry(atom_id="s1", metadata={"band": 2, "band_universal": True})]
    context = ResolverContext(
        persona_id="p",
        topic_id="t",
        slot_definitions=[["STORY"]],
        used_atom_ids=set(),
        pool_index=_DummyPoolIndex(pool),
        selector_key_prefix="u-band",
        required_band_by_chapter={0: 5},
        used_semantic_families=set(),
    )
    result = resolve_slot("STORY", 0, 0, context)
    assert result is not None
    assert result[0] == "s1"

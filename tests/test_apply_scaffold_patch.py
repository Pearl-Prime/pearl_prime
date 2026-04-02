from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.marketing import apply_scaffold_patch as patcher


def test_load_alias_map_raises_clear_error_for_malformed_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    alias_path = tmp_path / "brand_id_alias_map.yaml"
    alias_path.write_text("alias_to_canonical: [bad", encoding="utf-8")
    monkeypatch.setattr(patcher, "ALIAS_MAP_PATH", alias_path)

    with pytest.raises(RuntimeError, match="failed to load alias map"):
        patcher._load_alias_map()


def test_apply_consumer_language_patch_initializes_missing_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path / "repo"
    (repo_root / "config" / "marketing").mkdir(parents=True)
    monkeypatch.setattr(patcher, "REPO_ROOT", repo_root)

    data = {"topics": [{"topic_id": "anxiety", "search_cluster": {"primary_keyword": "calm"}}]}

    dest, messages = patcher.apply_consumer_language_patch(data, dry_run=False)

    written = Path(dest)
    payload = yaml.safe_load(written.read_text(encoding="utf-8"))

    assert written == repo_root / "config" / "marketing" / "consumer_language_by_topic.yaml"
    assert payload["topics"][0]["topic_id"] == "anxiety"
    assert messages == ["wrote config/marketing/consumer_language_by_topic.yaml"]

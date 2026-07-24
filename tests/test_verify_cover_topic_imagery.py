from pathlib import Path
import yaml
from scripts.ci.verify_cover_topic_imagery import audit

def test_audit_reports_uncovered_topics(tmp_path: Path):
    catalog = tmp_path / "catalog.yaml"; catalog.write_text(yaml.safe_dump({"topics": ["anxiety", "grief"]}))
    result = audit(index_path=tmp_path / "none.jsonl", catalog_path=catalog)
    assert not result["ok"] and result["uncovered_topics"] == ["anxiety", "grief"] and result["missing_topic_rules"] == []

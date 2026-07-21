from pathlib import Path
import json

from scripts.qa.audit_zhtw_genz_anxiety import build_backlog


def test_failing_chapter_and_mixed_english_are_reported(tmp_path: Path):
    repo = tmp_path
    render = repo / "render"
    render.mkdir()
    (render / "chapter_flow_report.json").write_text(
        json.dumps({
            "chapters": [
                {"chapter": 1, "status": "FAIL", "errors": ["MISSING_CLEAR_POINT"]},
                {"chapter": 2, "status": "PASS", "errors": []},
            ]
        }),
        encoding="utf-8",
    )
    (render / "selected_content_variants.json").write_text(
        json.dumps([
            {
                "chapter": 1,
                "slot_type": "INTEGRATION",
                "atom_id": "a1",
                "source_path": "atoms/p/t/INTEGRATION/locales/zh-TW/CANONICAL.txt",
                "content": "你一直撐著。 This is a long English fallback sentence that should be repaired.",
            }
        ]),
        encoding="utf-8",
    )
    (render / "book.txt").write_text(
        "Chapter 1\n\n你一直撐著。 This is another English fallback sentence in prose.",
        encoding="utf-8",
    )
    result = build_backlog(repo, render)
    assert result["status"] == "NEEDS_WRITER_REPAIR"
    assert result["failing_chapter_count"] == 1
    assert result["chapters"][0]["exact_files_needing_work"]
    assert result["manuscript_mixed_english_hits"]

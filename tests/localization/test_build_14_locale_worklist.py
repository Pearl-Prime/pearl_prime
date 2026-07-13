from pathlib import Path

from scripts.localization.build_14_locale_worklist import build


def test_missing_and_partial_locale_files_are_reported(tmp_path: Path):
    base = tmp_path / "atoms/p/t/HOOK/CANONICAL.txt"
    base.parent.mkdir(parents=True)
    base.write_text(
        "## HOOK v01\n---\n---\nReal base prose.\n---\n"
        "## HOOK v02\n---\n---\nSecond base prose.\n---\n",
        encoding="utf-8",
    )
    zh = base.parent / "locales/zh-TW/CANONICAL.txt"
    zh.parent.mkdir(parents=True)
    zh.write_text(
        "## HOOK v01\n---\n---\n真正的繁體中文內容。\n---\n",
        encoding="utf-8",
    )
    payload = build(tmp_path)
    row = next(
        item for item in payload["incomplete_rows"]
        if item["locale"] == "zh-TW"
    )
    assert row["status"] == "PARTIAL"
    assert row["missing_atom_ids"] == ["HOOK_v02"]
    assert payload["language_count_including_en_US_baseline"] == 14

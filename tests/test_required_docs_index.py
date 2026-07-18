from pathlib import Path

from scripts.ci.check_required_docs_index import parse_required_docs


def test_parse_required_docs_from_agent_brief(tmp_path: Path) -> None:
    brief = tmp_path / "agent_brief.txt"
    brief.write_text(
        "Before generating any prompt, read:\n"
        "- docs/PROGRAM_STATE.md          <- current verified state\n"
        "- artifacts/coordination/ACTIVE_PROJECTS.tsv\n"
        "Follow the router.\n",
        encoding="utf-8",
    )

    assert parse_required_docs(brief) == [
        "docs/agent_brief.txt",
        "docs/PROGRAM_STATE.md",
        "artifacts/coordination/ACTIVE_PROJECTS.tsv",
    ]

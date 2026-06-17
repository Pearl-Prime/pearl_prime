"""
Unit tests for ei.reader_council (P0.3).

The persona-card structure is tested without a GPU. The live read needs
Ollama on Pearl Star and skips gracefully.
"""
import pytest

from ei import reader_council as rc
from ei import corpus as corp
from ei import ollama_client as oc


def test_persona_frames_grounded_in_frameworks():
    for pid, frame in rc.PERSONA_FRAMES.items():
        assert frame["cbt"], f"{pid} missing CBT grounding"
        assert frame["ifs"], f"{pid} missing IFS grounding"
        assert frame["sdt"], f"{pid} missing SDT grounding"
        assert frame["reads_for"]


def test_default_council_personas_exist():
    for pid in rc.DEFAULT_COUNCIL:
        assert pid in rc.PERSONA_FRAMES


def _ollama_up() -> bool:
    try:
        return oc.ollama_available()
    except Exception:
        return False


@pytest.mark.skipif(not _ollama_up(), reason="Pearl Star Ollama unreachable")
def test_live_reader_response_is_structured():
    book = corp.find_gold_ref_books()[0]
    text = corp.load_gold_ref(book)
    resp = rc.read_book("tech_finance_burnout", text, max_chars=4000)
    assert resp is not None
    assert resp.persona == "tech_finance_burnout"
    assert "CBT" in resp.framework_lens
    assert isinstance(resp.landed, list)
    assert 0 <= resp.resonance_0_10 <= 10
    assert isinstance(resp.would_finish, bool)

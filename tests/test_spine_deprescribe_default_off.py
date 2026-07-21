"""D2 — deprescribe one-line beat injectors stay off on the default spine path."""
from __future__ import annotations

import os

from phoenix_v4.rendering.register_output_strengthen import spine_deprescribe_inject_enabled


def test_spine_deprescribe_inject_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PHOENIX_SPINE_DEPRESCRIBE", raising=False)
    assert spine_deprescribe_inject_enabled() is False


def test_spine_deprescribe_inject_opt_in(monkeypatch):
    monkeypatch.setenv("PHOENIX_SPINE_DEPRESCRIBE", "1")
    assert spine_deprescribe_inject_enabled() is True

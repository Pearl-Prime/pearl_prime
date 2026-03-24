"""LLM client protocol + replay implementation for JSON contract outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def generate_json(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        debug_path: Path | None = None,
        prompt_version: str | None = None,
    ) -> dict[str, Any]:
        ...


class ReplayLLMClient:
    """Deterministic client: returns a deep-copied payload (for CI / tests)."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response

    def generate_json(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        debug_path: Path | None = None,
        prompt_version: str | None = None,
    ) -> dict[str, Any]:
        if debug_path is not None:
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            debug_path.write_text(
                json.dumps(
                    {
                        "prompt_excerpt": prompt[:2000],
                        "prompt_version": prompt_version,
                        "response": self._response,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        return json.loads(json.dumps(self._response))

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional


class VariantSelectionLogger:
    """Append-only JSONL log of content-bank selections (per run)."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self._opened = False

    def enabled(self) -> bool:
        return self.path is not None

    def append(self, record: dict[str, Any]) -> None:
        if not self.path:
            return
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        self._opened = True

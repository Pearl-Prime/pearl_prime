"""License-on-download store (Pearl Prime equivalent of CampaignAssetDownload).

HD bytes live under per-work-unit prefixes only — no shared HD pool (§B).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LICENSE_ROOT = REPO_ROOT / "artifacts" / "storyblocks_licensed"
DEFAULT_INDEX_PATH = REPO_ROOT / "artifacts" / "storyblocks" / "license_index.jsonl"

# AI wall-off: rows here must never be exported into training corpora.
AI_TRAINING_EXCLUDED = True


@dataclass
class LicenseRecord:
    source_provider: str
    storyblocks_stock_id: str
    work_unit_type: str
    work_unit_id: str
    brand_id: str
    locale: str
    surface: str
    media_type: str
    mau_user_id: str
    download_query_at: str
    local_uri: str
    model_released: bool | None = None
    property_released: bool | None = None
    attribution_label: str = "Stock media via Storyblocks"
    metadata: dict[str, Any] = field(default_factory=dict)

    def key(self) -> str:
        return f"{self.work_unit_id}::{self.storyblocks_stock_id}"


class LicenseStore:
    """JSONL index + per-work-unit license sidecar next to HD bytes."""

    def __init__(
        self,
        bank_root: Path | None = None,
        index_path: Path | None = None,
    ) -> None:
        self.bank_root = bank_root or Path(
            os.environ.get("STORYBLOCKS_LICENSED_BANK_ROOT", str(DEFAULT_LICENSE_ROOT))
        )
        self.index_path = index_path or Path(
            os.environ.get("STORYBLOCKS_LICENSE_INDEX_PATH", str(DEFAULT_INDEX_PATH))
        )

    def work_unit_dir(self, work_unit_id: str) -> Path:
        safe = work_unit_id.replace("/", "_").replace("..", "_")
        return self.bank_root / safe

    def hd_path(self, work_unit_id: str, stock_id: str, ext: str) -> Path:
        safe_stock = stock_id.replace("/", "_")
        return self.work_unit_dir(work_unit_id) / f"{safe_stock}.{ext.lstrip('.')}"

    def sidecar_path(self, work_unit_id: str, stock_id: str) -> Path:
        safe_stock = stock_id.replace("/", "_")
        return self.work_unit_dir(work_unit_id) / f"{safe_stock}.license.json"

    def get(self, work_unit_id: str, stock_id: str) -> LicenseRecord | None:
        side = self.sidecar_path(work_unit_id, stock_id)
        if side.exists():
            data = json.loads(side.read_text(encoding="utf-8"))
            return LicenseRecord(**{k: data[k] for k in LicenseRecord.__dataclass_fields__ if k in data})
        if not self.index_path.exists():
            return None
        target = f"{work_unit_id}::{stock_id}"
        with self.index_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if f"{row.get('work_unit_id')}::{row.get('storyblocks_stock_id')}" == target:
                    return LicenseRecord(**{k: row[k] for k in LicenseRecord.__dataclass_fields__ if k in row})
        return None

    def has_license(self, work_unit_id: str, stock_id: str) -> bool:
        rec = self.get(work_unit_id, stock_id)
        return bool(rec and rec.local_uri and Path(rec.local_uri).exists())

    def put(self, record: LicenseRecord) -> Path:
        """Persist license proof + sidecar. Does not write HD bytes."""
        if record.source_provider != "storyblocks":
            raise ValueError("LicenseStore only accepts source_provider=storyblocks")
        wu = self.work_unit_dir(record.work_unit_id)
        wu.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(record)
        payload["ai_training_excluded"] = AI_TRAINING_EXCLUDED
        side = self.sidecar_path(record.work_unit_id, record.storyblocks_stock_id)
        side.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.index_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return side


def new_download_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


default_license_store = LicenseStore()

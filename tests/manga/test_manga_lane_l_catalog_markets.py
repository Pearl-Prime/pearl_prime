from __future__ import annotations
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image
REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from audit_catalog_global_markets import audit

def test_catalog_auditor_counts_complete_market_row(tmp_path: Path):
    p=tmp_path/"config/manga"; p.mkdir(parents=True)
    (p/"m.yaml").write_text("""plans:
- market: japan
  locale: ja_JP
  brand_id: b
  target_audience: a
  genre_shell: mecha
  topic_embed_strategy: subtle
  reading_format: page
  proof_status: planned
  production_owner: pm
""")
    report=audit(tmp_path)
    assert report["manga-global-market-count"]==1
    assert report["incomplete_row_count"]==0

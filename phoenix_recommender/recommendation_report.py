from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_outputs(
    out_dir: Path,
    repo_root: Path,
    ranked: list[dict[str, Any]],
    inputs: dict[str, Any],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ranked.json"
    md_path = out_dir / "summary.md"

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "counts": {
            "topics": len(inputs["topics"]),
            "personas": len(inputs["personas"]),
            "teachers": len(inputs["teachers"]),
            "selected": len(ranked),
        },
        "recommendations": ranked,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Phoenix Recommender",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Selected recommendations: `{len(ranked)}`",
        f"Teachers considered: `{len(inputs['teachers'])}`",
        f"Topics considered: `{len(inputs['topics'])}`",
        f"Personas considered: `{len(inputs['personas'])}`",
        "",
        "## Top Recommendations",
    ]
    for item in ranked[:10]:
        lines.append(
            f"- `{item['score']:.4f}` {item['teacher_id']} | {item['topic']} | {item['persona']} | series: {item['series_summary']}"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path

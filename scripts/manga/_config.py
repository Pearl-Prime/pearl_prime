"""Config and JSON helpers for manga scripts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_MANGA_DIR = "config/manga"


def load_yaml(rel_path: str) -> dict:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML required for manga config; pip install pyyaml")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_or_yaml(path: Path) -> dict | list:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML required for YAML inputs; pip install pyyaml")
        return yaml.safe_load(text) or {}
    return json.loads(text)


def config_snapshot_hash(config_dir: str = CONFIG_MANGA_DIR) -> str:
    root = REPO_ROOT / config_dir
    if not root.exists():
        return hashlib.sha256(b"").hexdigest()[:16]
    parts: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        parts.append(str(path.relative_to(root)))
        parts.append(path.read_text(encoding="utf-8"))
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()[:16]


def write_atomically(out_path: Path, data: dict | list, encoding: str = "utf-8") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding=encoding)
    tmp.rename(out_path)


def should_skip_output(
    out_path: Path,
    required_keys: list[str],
    force: bool,
    expected_config_hash: str | None = None,
) -> bool:
    if force or not out_path.exists():
        return False
    try:
        obj = json.loads(out_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    if not isinstance(obj, dict) or not all(key in obj for key in required_keys):
        return False
    if expected_config_hash is not None and obj.get("config_hash") != expected_config_hash:
        return False
    return True

"""Load config/duration/*.yaml. REPO_ROOT-relative; atomic JSON writes; optional PyYAML."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DURATION_DIR = REPO_ROOT / "config" / "duration"

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / path
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("PyYAML required for config/duration; pip install pyyaml")
    return yaml.safe_load(text) or {}


def load_duration_configs() -> dict:
    """Return merged dict of all standard CDIS config blobs."""
    out = {}
    for name in (
        "duration_registry.yaml",
        "platform_duration_profiles.yaml",
        "persona_duration_profiles.yaml",
        "therapeutic_dose_rules.yaml",
        "serialization_cadence.yaml",
    ):
        key = name.replace(".yaml", "")
        out[key] = load_yaml(CONFIG_DURATION_DIR / name)
    return out


def config_snapshot_hash() -> str:
    root = CONFIG_DURATION_DIR
    if not root.exists():
        return hashlib.sha256(b"").hexdigest()[:16]
    parts: list[str] = []
    for p in sorted(root.glob("*.yaml")):
        parts.append(p.name)
        parts.append(p.read_text(encoding="utf-8"))
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()[:16]


def write_atomically(out_path: Path, data: dict | list) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.rename(out_path)


def should_skip_output(out_path: Path, required_keys: list[str], force: bool, expected_hash: str | None) -> bool:
    if force or not out_path.exists():
        return False
    try:
        obj = json.loads(out_path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or not all(k in obj for k in required_keys):
            return False
        if expected_hash and obj.get("config_hash") != expected_hash:
            return False
        return True
    except Exception:
        return False

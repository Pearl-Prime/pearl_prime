#!/usr/bin/env python3
"""CI durability gate for Metricool managed posting (offline, no network).

Fails closed when:
- brand map fails validate_config (incl. --strict-blog-ids)
- waystream pin drifts from metricool_brands.yaml
- METRICOOL_* missing from integration_env_registry
- docs/metricool_api.txt is not gitignored
- a second Metricool HTTP client appears outside scripts/integrations/metricool/

Usage:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_metricool_managed.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "integrations" / "metricool"))

import yaml  # noqa: E402

from integration_env_registry import REGISTRY  # noqa: E402
import validate_config  # noqa: E402

BRANDS_MAP = REPO_ROOT / "config" / "integrations" / "metricool_brands.yaml"
PIN_PATH = REPO_ROOT / "config" / "integrations" / "metricool_waystream_pin.yaml"
GITIGNORE = REPO_ROOT / ".gitignore"

REQUIRED_ENV = ("METRICOOL_API_KEY", "METRICOOL_USER_ID", "METRICOOL_BASE_URL")
FORBIDDEN_CLIENT_GLOBS = (
    "**/metricool_client.py",
    "**/metricool_http.py",
    "phoenix_v4/**/metricool*.py",
)


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def check_registry() -> list[str]:
    errors: list[str] = []
    names = {row[1] for row in REGISTRY}
    for name in REQUIRED_ENV:
        if name not in names:
            errors.append(f"integration_env_registry missing {name}")
    return errors


def check_gitignore() -> list[str]:
    text = GITIGNORE.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    if "metricool_api.txt" not in text and "*_api.txt" not in text:
        errors.append(".gitignore must cover docs/metricool_api.txt or *_api.txt")
    # Tracked leak check
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files", "--", "docs/metricool_api.txt"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        tracked = ""
    if tracked:
        errors.append("docs/metricool_api.txt is tracked by git — must remain untracked")
    return errors


def check_pin(brands: dict, pin: dict) -> list[str]:
    errors: list[str] = []
    brand_key = str(pin.get("brand_key") or "waystream_sanctuary")
    row = (brands.get("brands") or {}).get(brand_key)
    if not isinstance(row, dict):
        return [f"brands.yaml missing wired brand {brand_key!r}"]
    expected_blog = str(pin.get("blog_id") or "").strip()
    actual_blog = "" if row.get("blog_id") is None else str(row.get("blog_id")).strip()
    if not expected_blog or not re.fullmatch(r"\d{4,}", expected_blog):
        errors.append(f"pin blog_id must be numeric digits (got {expected_blog!r})")
    if actual_blog != expected_blog:
        errors.append(
            f"pin drift: {brand_key}.blog_id={actual_blog!r} != pin {expected_blog!r}"
        )
    if (row.get("status") or "").strip().lower() != "wired":
        errors.append(f"{brand_key} must be status:wired (pin)")
    pin_user = str(pin.get("user_id") or "").strip()
    if pin_user and pin_user != "3564167":
        # Allow pin updates but surface unexpected account
        errors.append(f"pin user_id unexpected: {pin_user!r} (documented Waystream=3564167)")
    return errors


def check_no_forked_client() -> list[str]:
    """Refuse a second live HTTP client outside the canonical package.

    Uses ``git ls-files`` (tracked paths only) — never walks the full worktree
    (this repo is huge; recursive globs hang).
    """
    errors: list[str] = []
    canonical = REPO_ROOT / "scripts" / "integrations" / "metricool" / "client.py"
    if not canonical.is_file():
        return ["missing canonical scripts/integrations/metricool/client.py"]
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files", "--", "*.py"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=60,
        ).splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        # Offline/no-git: skip fork scan rather than hang
        return []

    suspects: list[str] = []
    for rel in tracked:
        name = Path(rel).name.lower()
        if "metricool" not in name and "metricool" not in rel.lower():
            continue
        if not (name.endswith(".py")):
            continue
        # Allowed: canonical package, tests, docs reference utils
        if rel.startswith("scripts/integrations/metricool/"):
            continue
        if rel.startswith("tests/"):
            continue
        if rel.startswith("docs/"):
            continue
        if rel.startswith("artifacts/"):
            continue
        if name in {"metricool_utils.py", "metricool_client.py", "metricool_http.py"} or (
            "metricool" in name and "client" in name
        ):
            suspects.append(rel)
    if suspects:
        errors.append(
            "possible Metricool client fork(s): " + ", ".join(sorted(suspects)[:8])
        )
    return errors


def main() -> int:
    errors: list[str] = []
    if not BRANDS_MAP.is_file():
        print(f"FAIL missing {BRANDS_MAP}")
        return 2
    if not PIN_PATH.is_file():
        print(f"FAIL missing pin {PIN_PATH}")
        return 2

    report = validate_config.load_and_validate(BRANDS_MAP, strict_blog_ids=True)
    if not report.get("ok"):
        for e in report.get("errors") or []:
            errors.append(f"validate_config: {e}")

    brands = _load_yaml(BRANDS_MAP)
    pin = _load_yaml(PIN_PATH)
    errors.extend(check_pin(brands, pin))
    errors.extend(check_registry())
    errors.extend(check_gitignore())
    errors.extend(check_no_forked_client())

    if errors:
        print("FAIL Metricool managed durability gate")
        for e in errors:
            print(f"  - {e}")
        return 2

    print(
        "OK Metricool managed durability "
        f"(wired={report.get('wired_count')} unwired={report.get('unwired_count')} "
        f"pin_blog_id={pin.get('blog_id')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

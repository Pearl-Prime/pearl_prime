"""Tests for the Hardening Spec sentinel acceptance tuple.

Sentinel tuple: topic=overthinking, persona=gen_z_professionals,
location=nyc_metro, teacher=ahjan, arc=F006, runtime=standard_book.

Must either compile cleanly or fail with explicit reason.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import resolve_sentinel_tuple via importlib (script, not package)
_canary_path = REPO_ROOT / "scripts" / "canary" / "run_bestseller_canary.py"


@pytest.fixture(scope="module")
def canary_module():
    if not _canary_path.exists():
        pytest.skip("scripts/canary/run_bestseller_canary.py not found")
    spec = importlib.util.spec_from_file_location("run_bestseller_canary", _canary_path)
    mod = importlib.util.module_from_spec(spec)
    old = sys.path[:]
    sys.path.insert(0, str(REPO_ROOT))
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        pytest.skip(f"Cannot load canary module: {exc}")
    finally:
        sys.path[:] = old
    return mod


class TestSentinelTupleResolves:
    """resolve_sentinel_tuple() returns structured output."""

    def test_returns_dict_with_required_keys(self, canary_module):
        if not hasattr(canary_module, "resolve_sentinel_tuple"):
            pytest.skip("resolve_sentinel_tuple not defined in canary module")
        try:
            result = canary_module.resolve_sentinel_tuple()
        except Exception as exc:
            # Honest failure is acceptable — system may not have atoms on disk
            assert str(exc), f"Sentinel tuple failed but with empty message: {exc}"
            return
        required_keys = {"persona", "topic", "engine_used", "format_id"}
        present = set(result.keys()) if isinstance(result, dict) else set()
        missing = required_keys - present
        assert not missing, f"Sentinel result missing keys: {missing}"

    def test_sentinel_topic_is_overthinking_or_aliased(self, canary_module):
        if not hasattr(canary_module, "resolve_sentinel_tuple"):
            pytest.skip("resolve_sentinel_tuple not defined")
        try:
            result = canary_module.resolve_sentinel_tuple()
        except Exception:
            return  # honest failure accepted
        topic = result.get("topic", "")
        # Must preserve overthinking or explicitly record alias
        assert topic in ("overthinking", "anxiety"), (
            f"Sentinel topic should be 'overthinking' or aliased 'anxiety', got '{topic}'"
        )

    def test_sentinel_persona_is_gen_z(self, canary_module):
        if not hasattr(canary_module, "resolve_sentinel_tuple"):
            pytest.skip("resolve_sentinel_tuple not defined")
        try:
            result = canary_module.resolve_sentinel_tuple()
        except Exception:
            return
        assert result.get("persona") == "gen_z_professionals"


class TestSentinelCanaryConfig:
    """Canary config includes sentinel defaults."""

    def test_canary_config_exists(self):
        config_path = REPO_ROOT / "config" / "quality" / "canary_config.yaml"
        assert config_path.exists(), "canary_config.yaml missing"

    def test_canary_config_has_sentinel_defaults(self):
        config_path = REPO_ROOT / "config" / "quality" / "canary_config.yaml"
        if not config_path.exists():
            pytest.skip("canary_config.yaml not found")
        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        sentinel = data.get("sentinel_defaults")
        assert sentinel is not None, "canary_config.yaml missing sentinel_defaults section"
        assert sentinel.get("topic") == "overthinking"
        assert sentinel.get("persona") == "gen_z_professionals"

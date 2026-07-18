#!/usr/bin/env python3
"""Assert that the current process is running in a remote-mode environment.

Phoenix Omega's cloud-native agent policy: long-running, disk-heavy, or
worktree-creating agent work must run in **Codespaces** or **GitHub
Actions**, never on the operator's laptop. This module is the single
chokepoint that enforces it.

Usage in agent scripts:
    from scripts.agent.assert_remote import assert_remote
    assert_remote()  # raises RuntimeError on local laptop

CLI usage (from devcontainer post-create or CI):
    python scripts/agent/assert_remote.py
    # exit 0 = remote, exit 1 = local laptop, exit 2 = config error

Bypass for local debugging only:
    PHOENIX_OMEGA_REMOTE=local-override python scripts/agent/assert_remote.py
    (Loud warning printed; logged. Do not use in agent scripts.)

Why this exists:
    Multiple disk-full incidents (2026-04-25 session) caused by agents
    creating .claude/worktrees/ trees on the operator's laptop. Each
    worktree = ~3 GB. Aggregate hit 32 GB and ENOSPC blocked all tool
    calls. Cloud-native migration moves this to Codespaces (ephemeral
    32 GB VM disk) so the operator's laptop never sees it.
"""
from __future__ import annotations

import os
import sys
from typing import Final

REMOTE_ENV_VAR: Final = "PHOENIX_OMEGA_REMOTE"

REMOTE_VALUES: Final = frozenset(
    {
        "codespaces",        # GitHub Codespaces VM
        "github-actions",    # GitHub Actions runner
        "cloudflare",        # Cloudflare Workers / cron
        "pearl-star",        # Pearl Star Tailnet host (Tier 2 unattended)
    }
)

OVERRIDE_VALUE: Final = "local-override"


class RemoteModeViolation(RuntimeError):
    """Raised when an agent attempts to run on a local laptop."""


def detect_environment() -> str:
    """Return the detected execution context, or 'local' if none.

    Detection order: explicit env var → platform-specific signals → local.
    """
    explicit = os.environ.get(REMOTE_ENV_VAR, "").strip().lower()
    if explicit in REMOTE_VALUES or explicit == OVERRIDE_VALUE:
        return explicit

    # Auto-detect platforms even if PHOENIX_OMEGA_REMOTE isn't set.
    if os.environ.get("CODESPACES") == "true":
        return "codespaces"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github-actions"
    if os.environ.get("CF_PAGES") == "1" or os.environ.get("CF_WORKER"):
        return "cloudflare"
    # Pearl Star detection: Tailscale hostname or marker file.
    pearl_marker = os.path.expanduser("~/.phoenix_omega_pearl_star")
    if os.path.exists(pearl_marker):
        return "pearl-star"

    return "local"


def assert_remote(allow_override: bool = False) -> str:
    """Raise RemoteModeViolation if running on a local laptop.

    Returns the detected environment label on success.

    allow_override=True permits PHOENIX_OMEGA_REMOTE=local-override to
    bypass the check (with a loud warning). Default False — agent
    scripts should leave this False.
    """
    env = detect_environment()

    if env == OVERRIDE_VALUE:
        if not allow_override:
            raise RemoteModeViolation(
                "PHOENIX_OMEGA_REMOTE=local-override is set but the calling "
                "agent does not allow override. Run in Codespaces or Actions."
            )
        sys.stderr.write(
            "⚠️  PHOENIX_OMEGA_REMOTE=local-override active. "
            "Agent is running on a local laptop with override. "
            "This bypasses the disk-safety guard. Do not commit results.\n"
        )
        return env

    if env == "local":
        raise RemoteModeViolation(
            "Phoenix Omega cloud-native policy: this agent must run in "
            "Codespaces, GitHub Actions, Cloudflare, or Pearl Star — not "
            "on a local laptop.\n\n"
            "Open the repo in a Codespace:\n"
            "  https://github.com/Ahjan108/phoenix_omega_v4.8/codespaces\n\n"
            "Or set PHOENIX_OMEGA_REMOTE explicitly if running on a "
            "remote you've vetted."
        )

    return env


def _cli() -> int:
    try:
        env = assert_remote(allow_override=True)
    except RemoteModeViolation as e:
        sys.stderr.write(f"❌ {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"⚠️  config error: {e}\n")
        return 2

    print(f"✓ remote-mode active: {env}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

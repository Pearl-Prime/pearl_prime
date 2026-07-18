#!/usr/bin/env python3
"""
SerpApi Budget Guard — tracks monthly search usage, enforces hard-stop at 245.
Auto-resets on the 1st of each month.

Usage:
  from scripts.feeds.budget_guard import BudgetGuard
  guard = BudgetGuard()
  if guard.can_search(cost=1):
      # do the search
      guard.record(cost=1, description="tier1 batch: EMDR,somatic therapy,...")
  print(guard.remaining())

CLI:
  python scripts/feeds/budget_guard.py status
  python scripts/feeds/budget_guard.py reset
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_budget_config() -> dict:
    path = REPO_ROOT / "config" / "trend_keywords" / "budget_config.yaml"
    if not path.exists() or yaml is None:
        return {"serpapi": {"monthly_limit": 250, "hard_stop": 245, "safety_margin": 5}}
    with open(path) as f:
        return yaml.safe_load(f) or {}


class BudgetGuard:
    """Tracks SerpApi usage per calendar month. Persists state to JSON."""

    def __init__(self, state_path: Optional[Path] = None):
        cfg = _load_budget_config().get("serpapi", {})
        self.monthly_limit: int = cfg.get("monthly_limit", 250)
        self.hard_stop: int = cfg.get("hard_stop", 245)
        self.warn_pct: int = cfg.get("budget_guard", {}).get("warn_at_pct", 80)

        default_state = REPO_ROOT / "artifacts" / "feeds" / ".serpapi_budget_state.json"
        self.state_path = state_path or default_state
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError):
                state = {}
        else:
            state = {}

        now = datetime.now(timezone.utc)
        current_month = now.strftime("%Y-%m")

        # Auto-reset if month changed
        if state.get("month") != current_month:
            state = {
                "month": current_month,
                "used": 0,
                "log": [],
                "reset_at": now.isoformat(),
            }
            self._save_state(state)

        return state

    def _save_state(self, state: Optional[dict] = None) -> None:
        state = state or self._state
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    @property
    def used(self) -> int:
        return self._state.get("used", 0)

    def remaining(self) -> int:
        """Searches remaining before hard-stop."""
        return max(0, self.hard_stop - self.used)

    def can_search(self, cost: int = 1) -> bool:
        """True if we have budget for `cost` more searches."""
        return (self.used + cost) <= self.hard_stop

    def record(self, cost: int = 1, description: str = "") -> None:
        """Record `cost` searches used. Call AFTER successful API call."""
        self._state["used"] = self.used + cost
        self._state.setdefault("log", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "cost": cost,
            "description": description,
            "cumulative": self._state["used"],
        })

        # Keep log manageable — last 200 entries
        if len(self._state["log"]) > 200:
            self._state["log"] = self._state["log"][-200:]

        self._save_state()

        # Warnings
        pct = (self._state["used"] / self.hard_stop) * 100
        if pct >= 100:
            print(f"⛔ BUDGET GUARD: Hard-stop reached ({self._state['used']}/{self.hard_stop}). No more searches this month.")
        elif pct >= self.warn_pct:
            print(f"⚠️  BUDGET GUARD: {pct:.0f}% used ({self._state['used']}/{self.hard_stop}). {self.remaining()} remaining.")

    def force_reset(self) -> None:
        """Manual reset — use only for testing or start of new billing cycle."""
        now = datetime.now(timezone.utc)
        self._state = {
            "month": now.strftime("%Y-%m"),
            "used": 0,
            "log": [],
            "reset_at": now.isoformat(),
            "manual_reset": True,
        }
        self._save_state()
        print(f"Budget guard reset for {self._state['month']}.")

    def status(self) -> dict:
        """Return current budget status."""
        return {
            "month": self._state.get("month"),
            "used": self.used,
            "hard_stop": self.hard_stop,
            "remaining": self.remaining(),
            "pct_used": round((self.used / self.hard_stop) * 100, 1) if self.hard_stop else 0,
            "total_log_entries": len(self._state.get("log", [])),
        }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/feeds/budget_guard.py [status|reset]")
        return 1

    guard = BudgetGuard()
    cmd = sys.argv[1].lower()

    if cmd == "status":
        s = guard.status()
        print(f"Month: {s['month']}")
        print(f"Used:  {s['used']} / {s['hard_stop']} ({s['pct_used']}%)")
        print(f"Remaining: {s['remaining']}")
        return 0

    elif cmd == "reset":
        guard.force_reset()
        return 0

    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

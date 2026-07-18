"""
phoenix_v4/video/quota_manager.py
Daily publish quota tracker for the brand × platform matrix.

Loads config/video/brand_platform_matrix.yaml and enforces per-brand,
per-platform daily upload limits.  Counts are kept in memory and
optionally persisted to a JSON file for cross-process visibility.

Usage — library:
    from phoenix_v4.video.quota_manager import QuotaManager
    qm = QuotaManager()
    if qm.can_publish("stillness_press", "youtube"):
        qm.record_publish("stillness_press", "youtube")
    remaining = qm.get_remaining_quota("stillness_press", "youtube")

Usage — CLI:
    python -m phoenix_v4.video.quota_manager --status
    python -m phoenix_v4.video.quota_manager --status --brand stillness_press
    python -m phoenix_v4.video.quota_manager --reset
    python -m phoenix_v4.video.quota_manager --record --brand stillness_press --platform youtube
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MATRIX_PATH = _REPO_ROOT / "config" / "video" / "brand_platform_matrix.yaml"
_DEFAULT_PERSIST_PATH = _REPO_ROOT / "phoenix_v4" / "video" / ".quota_state.json"

# Canonical platform names recognised by the matrix.
KNOWN_PLATFORMS = (
    "youtube",
    "youtube_shorts",
    "tiktok",
    "instagram_reels",
    "bilibili",
    "douyin",
)


# ---------------------------------------------------------------------------
# QuotaManager
# ---------------------------------------------------------------------------

class QuotaManager:
    """
    In-memory daily quota tracker backed by an optional JSON state file.

    The manager is date-aware: if the persisted state is from a previous
    calendar day (UTC), counts are reset automatically on first access.

    Parameters
    ----------
    matrix_path:
        Path to brand_platform_matrix.yaml.  Defaults to the repo-relative
        canonical location.
    persist_path:
        Path for the JSON state file.  Pass ``None`` to disable persistence
        (state lives only in memory for the lifetime of this object).
    """

    def __init__(
        self,
        matrix_path: Path = _MATRIX_PATH,
        persist_path: Optional[Path] = _DEFAULT_PERSIST_PATH,
    ) -> None:
        self._matrix_path = Path(matrix_path)
        self._persist_path = Path(persist_path) if persist_path else None
        self._matrix: dict = {}
        self._counts: dict[str, dict[str, int]] = {}  # brand → platform → count
        self._state_date: date = self._today()

        self._load_matrix()
        self._load_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def can_publish(self, brand: str, platform: str) -> bool:
        """
        Return True if the brand still has remaining quota on the platform
        for today.

        Raises
        ------
        ValueError
            If the brand or platform is not present in the matrix.
        """
        self._check_day_rollover()
        quota = self._get_quota(brand, platform)
        if quota == 0:
            return False
        used = self._counts.get(brand, {}).get(platform, 0)
        return used < quota

    def record_publish(self, brand: str, platform: str) -> int:
        """
        Increment the publish count for brand/platform.

        Returns the updated count after recording.

        Raises
        ------
        ValueError
            If the brand or platform is not in the matrix, or if the
            platform is disabled for this brand.
        RuntimeError
            If the daily quota has already been exhausted.
        """
        self._check_day_rollover()
        if not self._is_enabled(brand, platform):
            raise ValueError(
                f"Platform '{platform}' is disabled for brand '{brand}'."
            )
        quota = self._get_quota(brand, platform)
        used = self._counts.setdefault(brand, {}).get(platform, 0)
        if used >= quota:
            raise RuntimeError(
                f"Daily quota exhausted for {brand}/{platform} "
                f"({used}/{quota} used)."
            )
        new_count = used + 1
        self._counts[brand][platform] = new_count
        self._save_state()
        return new_count

    def get_remaining_quota(self, brand: str, platform: str) -> int:
        """
        Return the number of remaining publishes allowed today.

        Returns 0 when the platform is disabled or the brand is unknown.
        """
        self._check_day_rollover()
        try:
            quota = self._get_quota(brand, platform)
        except ValueError:
            return 0
        if quota == 0:
            return 0
        used = self._counts.get(brand, {}).get(platform, 0)
        return max(0, quota - used)

    def reset_daily_counts(self) -> None:
        """
        Reset all in-memory counts to zero and persist the cleared state.

        This is called automatically on day rollover.  It can also be
        called manually (e.g., from a cron job that runs at midnight UTC).
        """
        self._counts = {}
        self._state_date = self._today()
        self._save_state()

    def status(self, brand_filter: Optional[str] = None) -> dict:
        """
        Return a structured status dict suitable for display or serialisation.

        Returns a mapping of brand → platform → {quota, used, remaining, enabled}.
        """
        self._check_day_rollover()
        result: dict = {}
        brands = self._matrix.get("brands", {})
        for brand, brand_cfg in brands.items():
            if brand_filter and brand != brand_filter:
                continue
            result[brand] = {}
            platforms_cfg = brand_cfg.get("platforms", {})
            for platform in KNOWN_PLATFORMS:
                pcfg = platforms_cfg.get(platform, {})
                enabled = bool(pcfg.get("enabled", False))
                quota = int(pcfg.get("daily_quota", 0)) if enabled else 0
                used = self._counts.get(brand, {}).get(platform, 0)
                remaining = max(0, quota - used) if enabled else 0
                result[brand][platform] = {
                    "enabled": enabled,
                    "quota": quota,
                    "used": used,
                    "remaining": remaining,
                }
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _today() -> date:
        return datetime.now(tz=timezone.utc).date()

    def _check_day_rollover(self) -> None:
        today = self._today()
        if today != self._state_date:
            self.reset_daily_counts()

    def _load_matrix(self) -> None:
        if not self._matrix_path.exists():
            raise FileNotFoundError(
                f"Brand platform matrix not found: {self._matrix_path}"
            )
        with self._matrix_path.open("r", encoding="utf-8") as fh:
            self._matrix = yaml.safe_load(fh) or {}

    def _load_state(self) -> None:
        """Load persisted counts from disk, resetting if stale."""
        if not self._persist_path or not self._persist_path.exists():
            self._counts = {}
            return
        try:
            with self._persist_path.open("r", encoding="utf-8") as fh:
                state = json.load(fh)
            saved_date = date.fromisoformat(state.get("date", "1970-01-01"))
            if saved_date != self._today():
                # Stale state — start fresh
                self._counts = {}
                self._state_date = self._today()
            else:
                self._counts = state.get("counts", {})
                self._state_date = saved_date
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupt state file — start fresh
            self._counts = {}

    def _save_state(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "date": self._state_date.isoformat(),
            "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            "counts": self._counts,
        }
        tmp = self._persist_path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        tmp.replace(self._persist_path)

    def _brand_cfg(self, brand: str) -> dict:
        brands = self._matrix.get("brands", {})
        if brand not in brands:
            raise ValueError(f"Unknown brand '{brand}'. Check brand_platform_matrix.yaml.")
        return brands[brand]

    def _platform_cfg(self, brand: str, platform: str) -> dict:
        if platform not in KNOWN_PLATFORMS:
            raise ValueError(
                f"Unknown platform '{platform}'. "
                f"Valid platforms: {', '.join(KNOWN_PLATFORMS)}"
            )
        bcfg = self._brand_cfg(brand)
        pcfg = bcfg.get("platforms", {}).get(platform, {})
        return pcfg

    def _is_enabled(self, brand: str, platform: str) -> bool:
        return bool(self._platform_cfg(brand, platform).get("enabled", False))

    def _get_quota(self, brand: str, platform: str) -> int:
        """Return the daily quota for brand/platform. 0 if disabled."""
        pcfg = self._platform_cfg(brand, platform)
        if not pcfg.get("enabled", False):
            return 0
        return int(pcfg.get("daily_quota", 0))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m phoenix_v4.video.quota_manager",
        description="Brand × platform daily publish quota manager.",
    )
    sub = p.add_subparsers(dest="command")

    # --status
    status_p = sub.add_parser("status", help="Show current quota status.")
    status_p.add_argument(
        "--brand", metavar="BRAND", default=None,
        help="Filter output to a single brand.",
    )
    status_p.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output as JSON instead of a table.",
    )

    # --reset
    sub.add_parser("reset", help="Reset all daily counts to zero.")

    # --record
    record_p = sub.add_parser("record", help="Record a publish event.")
    record_p.add_argument("--brand", required=True, metavar="BRAND")
    record_p.add_argument("--platform", required=True, metavar="PLATFORM")

    # --can-publish
    can_p = sub.add_parser(
        "can-publish", help="Exit 0 if quota available, 1 if exhausted."
    )
    can_p.add_argument("--brand", required=True, metavar="BRAND")
    can_p.add_argument("--platform", required=True, metavar="PLATFORM")

    # Backwards-compat: bare --status flag on root parser
    p.add_argument(
        "--status", dest="_legacy_status", action="store_true",
        help="(deprecated) Use the 'status' subcommand instead.",
    )
    p.add_argument("--brand", metavar="BRAND", default=None)
    p.add_argument("--json", dest="as_json", action="store_true")
    p.add_argument("--reset", dest="_legacy_reset", action="store_true")

    return p


def _print_status_table(status_data: dict) -> None:
    """Render a human-readable quota table to stdout."""
    header = f"{'BRAND':<28}  {'PLATFORM':<20}  {'QUOTA':>5}  {'USED':>4}  {'LEFT':>4}  ENABLED"
    print(header)
    print("-" * len(header))
    for brand, platforms in sorted(status_data.items()):
        for platform, info in sorted(platforms.items()):
            if not info["enabled"]:
                status_str = "disabled"
                quota_str = "-"
                used_str = "-"
                left_str = "-"
            else:
                status_str = "enabled"
                quota_str = str(info["quota"])
                used_str = str(info["used"])
                left_str = str(info["remaining"])
            print(
                f"{brand:<28}  {platform:<20}  {quota_str:>5}  "
                f"{used_str:>4}  {left_str:>4}  {status_str}"
            )


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        qm = QuotaManager()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # Subcommand routing
    command = args.command

    # Legacy flag compat
    if command is None:
        if getattr(args, "_legacy_reset", False):
            command = "reset"
        elif getattr(args, "_legacy_status", False):
            command = "status"
        else:
            command = "status"  # Default

    if command == "status":
        brand_filter = getattr(args, "brand", None)
        as_json = getattr(args, "as_json", False)
        data = qm.status(brand_filter=brand_filter)
        if as_json:
            print(json.dumps(data, indent=2))
        else:
            today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
            print(f"\nQuota status — {today} UTC\n")
            _print_status_table(data)
            print()
        return 0

    if command == "reset":
        qm.reset_daily_counts()
        print("Daily counts reset.")
        return 0

    if command == "record":
        try:
            count = qm.record_publish(args.brand, args.platform)
            remaining = qm.get_remaining_quota(args.brand, args.platform)
            print(
                f"Recorded publish for {args.brand}/{args.platform}. "
                f"Count today: {count}. Remaining: {remaining}."
            )
        except (ValueError, RuntimeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return 0

    if command == "can-publish":
        try:
            ok = qm.can_publish(args.brand, args.platform)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        remaining = qm.get_remaining_quota(args.brand, args.platform)
        if ok:
            print(
                f"OK: {args.brand}/{args.platform} can publish. "
                f"Remaining quota: {remaining}."
            )
            return 0
        else:
            print(
                f"BLOCKED: {args.brand}/{args.platform} quota exhausted "
                f"(remaining: {remaining})."
            )
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

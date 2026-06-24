#!/usr/bin/env python3
"""Publish REAL weekly-package deliverables to the static deploy + emit a delivery feed.

The director dashboard's downloads have been EXACT metadata only. This surfaces the
brand's ACTUAL rendered files where they exist: it scans
artifacts/weekly_packages/<canon>/<week>/<platform>/ for real content
(epub/pdf/mp3/m4b/png — not stub READMEs or .zip wrappers), maps the package brand to
its archetype base, copies the files into
brand-wizard-app/public/deliveries/<base>/<week>/<platform>/, and writes
public/brand_deliveries/<base>.json so the dashboard can offer the real downloadable
files. Today only `stillness_press` has rendered output; every other brand stays
metadata-only until its books are rendered (the production-gate frontier).

Run:  python3 scripts/onboarding/gen_brand_deliveries.py
"""
from __future__ import annotations
import json
import os
import shutil
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WP = REPO / "artifacts" / "weekly_packages"
PUB = REPO / "brand-wizard-app" / "public"
DELIV = PUB / "deliveries"
FEED = PUB / "brand_deliveries"
REG = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
SAFE_VELOCITY = REPO / "config" / "release_velocity" / "safe_velocity.yaml"

CONTENT_EXT = {".epub", ".pdf", ".mp3", ".m4b", ".png", ".cue", ".md"}  # real content; skip .zip + README.txt
MAX_BYTES = 25 * 1024 * 1024  # keep the static deploy lean
# Repo CI (no-binary-blobs.yml) rejects new binary blobs > 1 MB. Oversize EPUBs are
# uploaded to R2 by scripts/release/upload_waystream_deliveries_r2.py instead.
GIT_PUBLISH_MAX = 1_048_576

# ── Release-cadence guard (SSOT: config/release_velocity/safe_velocity.yaml) ──
# A brand's books must NOT all dump into one week. This builder mirrors whatever
# weekly_packages/<brand>/<week>/<platform>/ holds, so if an upstream step over-
# stuffs a single week it would show e.g. 80 books for one week on the Brand
# Director dashboard — violating the per-platform-per-week caps + new-brand ramp.
# We validate each week's per-platform count here and FAIL on overflow. To re-slice
# an over-stuffed folder into a cadenced ramp, run:
#   scripts/release/cadence_reslice_deliveries.py
# Delivery-platform folder name -> safe_velocity platform key (new-tier cap).
# Anything not mapped (e.g. amazon_kdp, which safe_velocity does not list) is capped
# against the EN lane's Google Play new_imprint ceiling, the conservative English rule.
PLATFORM_CAP_KEY = {
    "google_play_books": ("google_play_books", "new_imprint"),
    "google_play": ("google_play_books", "new_imprint"),
    "findaway_voices": ("findaway_voices", "new_account"),
    "findaway": ("findaway_voices", "new_account"),
    "ximalaya": ("ximalaya", "verified_account"),
}
# Fallback for unmapped platforms (amazon_kdp, webtoon, kdp, ...): English channel rule.
_DEFAULT_CAP_PLATFORM = ("google_play_books", "new_imprint")
# Escape hatch for legitimate operator-approved bulk weeks (off by default).
ALLOW_OVERFLOW = os.environ.get("GEN_BRAND_DELIVERIES_ALLOW_OVERFLOW") == "1"


def _cap_max_for_platform(plat: str, safe: dict) -> int | None:
    """Per-week cap_max for a delivery-platform folder name, from safe_velocity.yaml."""
    plat_key, tier_key = PLATFORM_CAP_KEY.get(plat, _DEFAULT_CAP_PLATFORM)
    per_week = ((safe.get(plat_key) or {}).get(tier_key) or {}).get("per_week")
    if not per_week:
        return None
    return int(per_week[1])


def _current_iso_week() -> str:
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"

def archetype_bases() -> list:
    try:
        reg = yaml.safe_load(REG.read_text(encoding="utf-8")) or {}
        bs = {v.get("brand_archetype_id") for v in (reg.get("brands") or {}).values()
              if isinstance(v, dict) and v.get("brand_archetype_id")}
        return sorted((b for b in bs if b), key=len, reverse=True)  # longest-prefix first
    except Exception:
        return []

def to_base(brand_dir: str, bases: list) -> str:
    for b in bases:
        if brand_dir == b or brand_dir.startswith(b + "_"):
            return b
    return brand_dir

def _scan_feeds(bases: list) -> dict:
    """Build the feed structure {base: {brand, weeks:{week:{plat:[files]}}}} from
    weekly_packages, WITHOUT copying yet. Lets us cadence-validate before publishing."""
    feeds: dict = {}
    for bdir in sorted(p.name for p in WP.iterdir() if p.is_dir()):
        base = to_base(bdir, bases)
        for week in sorted(p.name for p in (WP / bdir).iterdir() if p.is_dir()):
            plats: dict = {}
            for plat in sorted(p.name for p in (WP / bdir / week).iterdir() if p.is_dir()):
                files = []
                for f in sorted((WP / bdir / week / plat).iterdir()):
                    if (f.is_file() and f.suffix.lower() in CONTENT_EXT
                            and f.name != "README.txt" and 0 < f.stat().st_size <= MAX_BYTES):
                        files.append({"file": f.name,
                                      "src": str(f),
                                      "url": f"deliveries/{base}/{week}/{plat}/{f.name}",
                                      "kb": round(f.stat().st_size / 1024)})
                if files:
                    plats[plat] = files
            if plats:
                feeds.setdefault(base, {"brand": base, "weeks": {}})["weeks"][week] = plats
    return feeds


def _cadence_violations(feeds: dict, safe: dict) -> list[str]:
    """Return human-readable violations where a week's per-platform count > cap_max."""
    violations: list[str] = []
    for base, feed in feeds.items():
        for week, plats in feed["weeks"].items():
            for plat, files in plats.items():
                cap_max = _cap_max_for_platform(plat, safe)
                if cap_max is not None and len(files) > cap_max:
                    violations.append(
                        f"{base} {week} {plat}: {len(files)} > cap_max {cap_max} "
                        f"(excess {len(files) - cap_max})")
    return violations


def main() -> None:
    if not WP.exists():
        raise SystemExit(f"no weekly_packages dir: {WP}")
    bases = archetype_bases()
    feeds = _scan_feeds(bases)

    # ── Cadence guard: refuse to publish an un-cadenced dump ──────────────
    safe = yaml.safe_load(SAFE_VELOCITY.read_text(encoding="utf-8")) or {} if SAFE_VELOCITY.exists() else {}
    violations = _cadence_violations(feeds, safe)
    if violations:
        msg = ["RELEASE-CADENCE VIOLATION — a week exceeds its per-platform cap "
               "(config/release_velocity/safe_velocity.yaml):"]
        msg += [f"  {v}" for v in violations]
        msg.append("Re-slice the over-stuffed folder into a cadenced ramp first:")
        msg.append("  python3 scripts/release/cadence_reslice_deliveries.py "
                   "--brand-dir artifacts/weekly_packages/<brand> --from-week <WK> --platform <plat> --lane en")
        msg.append("(Operator override: GEN_BRAND_DELIVERIES_ALLOW_OVERFLOW=1)")
        if ALLOW_OVERFLOW:
            print("WARN (override active):\n" + "\n".join(msg))
        else:
            raise SystemExit("\n".join(msg))

    # ── Publish: copy real files into public/deliveries + strip the src key ──
    published = 0
    cur_week = _current_iso_week()
    FEED.mkdir(parents=True, exist_ok=True)
    for base, feed in feeds.items():
        for week, plats in feed["weeks"].items():
            for plat, files in plats.items():
                for entry in files:
                    src = Path(entry.pop("src"))
                    if src.stat().st_size > GIT_PUBLISH_MAX:
                        # Feed entry stays; R2 upload patches url for large EPUBs.
                        continue
                    dest = DELIV / base / week / plat / entry["file"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    published += 1
        weeks_sorted = sorted(feed["weeks"])
        # Dashboard shows latest_week's count — point it at the CURRENT week when the
        # brand has a packet this week, so a ramped backlog shows the cadenced count
        # (e.g. ~1-2) rather than the largest/last future week.
        feed["latest_week"] = cur_week if cur_week in feed["weeks"] else weeks_sorted[-1]
        (FEED / f"{base}.json").write_text(
            json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        plats = sorted({p for w in feed["weeks"].values() for p in w})
        print(f"  {base}: latest_week={feed['latest_week']} weeks={weeks_sorted} platforms={plats}")
    print(f"published {published} real files across {len(feeds)} brand delivery feeds -> {FEED.relative_to(REPO)}")

main()

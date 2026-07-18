#!/usr/bin/env python3
"""Publish weekly-package deliverables to the static deploy + emit a delivery feed.

The director dashboard's downloads have been EXACT metadata only. This surfaces the
brand's ACTUAL rendered files where they exist: it scans
artifacts/weekly_packages/<canon>/<week>/<platform>/ for real content
(epub/pdf/mp3/m4b/png — not stub READMEs or .zip wrappers), maps the package brand to
its archetype base, copies the files into
brand-wizard-app/public/deliveries/<base>/<week>/<platform>/, and writes
public/brand_deliveries/<base>.json so the dashboard can offer the real downloadable
files.

For assigned Brand Director brands that have a real catalog but no rendered files yet,
this also emits a catalog-backed ops feed. That feed makes the ops dashboard live with
metadata/title queues while truthfully marking production files as pending.

Run:  python3 scripts/onboarding/gen_brand_deliveries.py
"""
from __future__ import annotations
import argparse
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
CATALOGS = PUB / "brand_catalogs"
REG = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
SAFE_VELOCITY = REPO / "config" / "release_velocity" / "safe_velocity.yaml"
DIRECTOR_ASSIGNMENTS = REPO / "config" / "brand_management" / "brand_director_assignments.yaml"

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
# Shrink-guard: this builder is a FULL REGEN keyed on the EPUBs physically present in
# weekly_packages — it is NOT additive. Running it with only a partial local subset
# (e.g. an 18-EPUB pilot when main carries a 48-week / 153-SKU feed) silently rewrites
# the tracked feed down to that subset (a destructive regression that already happened).
# Refuse to overwrite a tracked feed with FEWER file entries than it currently holds,
# unless explicitly overridden. Only run the unguarded regen in the full-tree CI context.
ALLOW_SHRINK = os.environ.get("GEN_BRAND_DELIVERIES_ALLOW_SHRINK") == "1"


def _feed_file_count(feed: dict) -> int:
    """Total delivery file entries across all weeks/platforms in a feed dict."""
    total = 0
    for plats in (feed.get("weeks") or {}).values():
        if not isinstance(plats, dict):
            continue
        for files in plats.values():
            if not isinstance(files, list):
                continue
            total += sum(1 for item in files if isinstance(item, dict) and item.get("file"))
    return total


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

def _scan_feeds(bases: list, *, base_filter: str | None = None) -> dict:
    """Build the feed structure {base: {brand, weeks:{week:{plat:[files]}}}} from
    weekly_packages, WITHOUT copying yet. Lets us cadence-validate before publishing."""
    feeds: dict = {}
    for bdir in sorted(p.name for p in WP.iterdir() if p.is_dir()):
        base = to_base(bdir, bases)
        if base_filter and base != base_filter:
            continue
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


def _director_assignments_by_base() -> dict[str, dict]:
    if not DIRECTOR_ASSIGNMENTS.exists():
        return {}
    data = yaml.safe_load(DIRECTOR_ASSIGNMENTS.read_text(encoding="utf-8")) or {}
    out: dict[str, dict] = {}
    for key, rec in (data.get("assignments") or {}).items():
        if not isinstance(rec, dict):
            continue
        name = str(rec.get("brand_director_name") or "").strip()
        director_id = str(rec.get("brand_director_id") or "").strip()
        base = str(rec.get("base_brand") or "").strip()
        brand_id = str(rec.get("brand_id") or key or "").strip()
        if not (name and director_id and base and brand_id):
            continue
        out[base] = {
            "brand_id": brand_id,
            "base_brand": base,
            "display_brand": str(rec.get("display_brand") or base).strip(),
            "brand_director_name": name,
            "brand_director_id": director_id,
            "brand_director_status": str(rec.get("status") or "assigned").strip(),
            "assigned_at": str(rec.get("assigned_at") or "").strip(),
            "assignment_source": str(rec.get("assignment_source") or "").strip(),
        }
    return out


def _load_catalog(base: str) -> dict | None:
    path = CATALOGS / f"{base}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid catalog JSON {path.relative_to(REPO)}: {exc}") from exc
    books = data.get("books") if isinstance(data, dict) else None
    return data if isinstance(books, list) and books else None


def _book_id(base: str, book: dict, idx: int) -> str:
    existing = str(book.get("book_id") or book.get("id") or "").strip()
    if existing:
        return existing
    title = str(book.get("title") or f"title-{idx + 1}").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in title)
    slug = "_".join(part for part in slug.split("_") if part)
    return f"{base}_{idx + 1:02d}_{slug[:54] or 'title'}"


def _catalog_metadata(base: str, catalog: dict) -> list[dict]:
    books = catalog.get("books") or []
    rows: list[dict] = []
    for idx, book in enumerate(books):
        if not isinstance(book, dict):
            continue
        rows.append({
            "book_id": _book_id(base, book, idx),
            "title": book.get("title") or "",
            "subtitle": book.get("subtitle") or "",
            "author": book.get("author") or "",
            "persona": book.get("persona") or "",
            "topic": book.get("topic") or "",
            "engine": book.get("engine") or "",
            "cover": book.get("cover") or "",
            "isbn": book.get("isbn") or "",
            "production_files_ready": False,
            "required_files": ["epub", "frontcover.jpg", "audio", "manga/webtoon assets"],
        })
    return rows


def _catalog_backed_feed(base: str, assignment: dict, cur_week: str) -> dict | None:
    catalog = _load_catalog(base)
    if not catalog:
        return None
    catalog_rows = _catalog_metadata(base, catalog)
    if not catalog_rows:
        return None
    display_brand = (
        assignment.get("display_brand")
        or catalog.get("display_brand")
        or catalog.get("brand")
        or base
    )
    return {
        "brand": base,
        "brand_id": assignment.get("brand_id"),
        "base_brand": base,
        "display_brand": display_brand,
        "brand_director_name": assignment.get("brand_director_name"),
        "brand_director_id": assignment.get("brand_director_id"),
        "brand_director_status": assignment.get("brand_director_status") or "assigned",
        "latest_week": cur_week,
        "delivery_status": "catalog_ready_production_files_pending",
        "production_files_ready": False,
        "source": "brand_catalog",
        "catalog": {
            "url": f"brand_catalogs/{base}.json",
            "count": len(catalog_rows),
        },
        "weeks": {
            cur_week: {
                "catalog_metadata": catalog_rows,
            },
        },
    }


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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--brand",
        help="Optional archetype/base brand filter, e.g. stabilizer. Limits feed writes to that base.",
    )
    args = ap.parse_args()
    base_filter = args.brand.strip() if args.brand else None

    if not WP.exists():
        raise SystemExit(f"no weekly_packages dir: {WP}")
    bases = archetype_bases()
    feeds = _scan_feeds(bases, base_filter=base_filter)

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
        assignment = _director_assignments_by_base().get(base)
        if assignment:
            feed.update({k: v for k, v in assignment.items() if v})
            feed["production_files_ready"] = True
            feed["delivery_status"] = "production_files_live"
            feed["source"] = "weekly_packages"
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
        out_path = FEED / f"{base}.json"
        new_count = _feed_file_count(feed)
        if out_path.is_file() and not ALLOW_SHRINK:
            try:
                prev = json.loads(out_path.read_text(encoding="utf-8"))
                prev_count = _feed_file_count(prev)
            except (json.JSONDecodeError, OSError):
                prev_count = 0
            if new_count < prev_count:
                raise SystemExit(
                    f"SHRINK-GUARD: {base}.json would drop from {prev_count} -> {new_count} file "
                    f"entries. This is a FULL REGEN keyed on EPUBs present under "
                    f"artifacts/weekly_packages/{base}/ — you are almost certainly running it "
                    f"locally with only a partial subset (build the full tree first, or run in "
                    f"the full-tree CI context). To intentionally shrink, set "
                    f"GEN_BRAND_DELIVERIES_ALLOW_SHRINK=1.")
        out_path.write_text(
            json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        plats = sorted({p for w in feed["weeks"].values() for p in w})
        print(f"  {base}: latest_week={feed['latest_week']} weeks={weeks_sorted} platforms={plats}")
    # Assigned Brand Director brands still need a live ops feed as soon as their catalog
    # exists. If no rendered production files were found, publish catalog metadata and keep
    # production_files_ready=false so the dashboard cannot imply a shippable package.
    assignment_feeds = 0
    assignments_by_base = _director_assignments_by_base()
    for base, assignment in sorted(assignments_by_base.items()):
        if base_filter and base != base_filter:
            continue
        if base in feeds:
            continue
        feed = _catalog_backed_feed(base, assignment, cur_week)
        if not feed:
            continue
        out_path = FEED / f"{base}.json"
        out_path.write_text(
            json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        assignment_feeds += 1
        print(
            f"  {base}: latest_week={cur_week} catalog={feed['catalog']['count']} "
            "status=catalog_ready_production_files_pending"
        )
    total_feeds = len(feeds) + assignment_feeds
    print(f"published {published} real files across {total_feeds} brand delivery feeds -> {FEED.relative_to(REPO)}")

if __name__ == "__main__":
    main()

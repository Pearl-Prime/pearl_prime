#!/usr/bin/env python3
"""
Bridge #2: weekly packet inventory  ->  brand_admin_weekly_os.html WEEKLY phase (static JSON).

Sibling of gen_brand_admin_brands.py (#1611). That generator emits the BRAND bridge
(brand_admin_brands.json — who the wizard assigned you to). THIS generator emits the
PACKET bridge (brand_admin_weekly_packets.json — what real weekly package is ready to
download for your brand), so the Phase 0-3 console works on static Cloudflare Pages with
NO FastAPI backend.

Why a second static bridge
--------------------------
On main the console's WEEKLY surface (Phase 2 "Your Content Package") fetches the live
FastAPI endpoints:
  - GET /api/brand_admin/coordination-status   (the "Last built:" badge)
  - GET /api/brand_admin/download/{brand}/{week}   (the "Download Week 1 Package" button)
Cloudflare Pages is static and cannot reach those. This bridge gives the console the same
DATA as a committed JSON it reads via ?brand=<id>. The FastAPI path is KEPT as a fallback
when an ?api_base= is supplied (operator running scripts/run_server.py locally).

Source of truth for packets
----------------------------
The real weekly packages produced by scripts/build_weekly_brand_package.py +
scripts/release/build_admin_packets.py land under
    artifacts/weekly_packages/<packet_dir>/<week>/
each with a manifest.json (axis status + provenance) and a monolithic
<packet_dir>_<week>.zip (the FastAPI download). This generator reads those manifests
(NEVER fabricates them) and surfaces a per-brand summary.

Key spaces (read before editing)
---------------------------------
The console B[] map (brand_admin_brands.json) is keyed by the LOCALE-SUFFIXED unified
brand_id (e.g. stillness_press_en_us). The packet dirs on disk are keyed by the manga
"packet dir" name, which is the ARCHETYPE BASE optionally + a demographic suffix
(e.g. stillness_press, qi_foundation_cultivation, somatic_wisdom_shojo). We join via the
unified registry's brand_archetype_id (same join key as config/brand_management/
brand_buildability.yaml): packet_dir == archetype  OR  packet_dir.startswith(archetype+'_').

Buildability + exclusions
-------------------------
- devotion_path is EXCLUDED unconditionally (its catalog is NOT release-ready; blocked on
  the engine re-point ws). It is never emitted with a packet even if a stale dir exists.
- brand_buildability.yaml non_buildable archetypes are emitted as buildable:false with a
  reason and NO download (so the console can render "pending catalog reconciliation"
  rather than offer a dead button). They are NEVER stubbed.
- Brands with no real packet on disk are emitted buildable:<gate> packet:null. Never a stub.

Output
------
brand-wizard-app/public/brand_admin_weekly_packets.json, shape:
{
  "generated_at": "...Z",
  "week": "2026-W22",
  "schema": 1,
  "brands": {
    "<console_brand_id>": {
      "packet_dir": "stillness_press",
      "week": "2026-W22",
      "week_monday": "2026-05-25",
      "buildable": true,
      "package_type": "book_axis_mvp+podcast_axis_mvp+...",
      "axes": {"books":"ready","podcast":"ready","audiobook":"ready","manga_panels":"ready",...},
      "axis_count_ready": 4,
      "cost_usd": 0,
      "download": {
        "api_path": "/api/brand_admin/download/stillness_press/2026-W22",
        "filename": "stillness_press_2026-W22.zip",
        "size_bytes": 5084496,
        "release_record": "artifacts/release/2026-W22/stillness_press/"
      },
      "coordination": {"status":"CURRENT","relative":"...","monday":"2026-05-25","mtime_iso":"..."}
    },
    ...
  },
  "blocked": {
    "<console_brand_id>": {"reason": "...", "packet_dir": null}
  }
}

Usage
-----
    python3 scripts/onboarding/gen_brand_admin_weekly_packets.py            # default week = newest on disk
    python3 scripts/onboarding/gen_brand_admin_weekly_packets.py --week 2026-W22
Run after a weekly build (or after committing real packets) to refresh the bridge.

PII / secrets: this JSON is PUBLIC (served on Pages). It carries ONLY brand_id, week,
axis status, file counts/sizes, and tier/provider strings from the manifest. It must NEVER
carry admin emails, credentials, or secret keys. The emitter asserts this before writing.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
UNIFIED = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"
BUILDABILITY = REPO / "config" / "brand_management" / "brand_buildability.yaml"
PACKAGES_DIR = REPO / "artifacts" / "weekly_packages"
COORD_DIR = REPO / "artifacts" / "coordination"
OUT = REPO / "brand-wizard-app" / "public" / "brand_admin_weekly_packets.json"

# Archetypes we never emit a packet for, regardless of disk state.
HARD_EXCLUDE = {"devotion_path"}

# Manifest axis keys -> short axis label surfaced to the console.
AXIS_KEYS = ("books", "podcast", "audiobook", "manga_panels", "atoms", "pearl_news")
# Axes that count toward the "real N-axis MVP" headline (the #1344-#1349 four).
HEADLINE_AXES = ("books", "podcast", "audiobook", "manga_panels")

# A REAL packet must have at least this many READY headline axes. Seed/dry-run scaffolds
# emit a manifest + a ~575-byte placeholder zip with ALL axes "stub"; those are NOT
# shippable and are logged blocked-pending-reconciliation, never surfaced as buildable.
MIN_READY_HEADLINE_AXES = 1
# Below this the monolithic zip is a placeholder scaffold, not a real multi-axis bundle.
MIN_REAL_ZIP_BYTES = 4096

# Anything matching these in the public JSON would be a PII/secret leak. Fail-closed.
_LEAK_RE = re.compile(r"@[\w.-]+\.\w+|api[_-]?key|secret|password|authorization|bearer\s", re.I)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _newest_week_on_disk() -> str | None:
    """Find the newest ISO week that has at least one <dir>/<week>/manifest.json."""
    weeks: set[str] = set()
    if not PACKAGES_DIR.is_dir():
        return None
    for brand_dir in PACKAGES_DIR.iterdir():
        if not brand_dir.is_dir():
            continue
        for wk in brand_dir.iterdir():
            if wk.is_dir() and re.fullmatch(r"\d{4}-W\d{2}", wk.name) and (wk / "manifest.json").is_file():
                weeks.add(wk.name)
    if not weeks:
        return None
    # ISO week strings sort chronologically as plain strings (YYYY-Www).
    return sorted(weeks)[-1]


def _week_monday_iso(week: str) -> str | None:
    m = re.fullmatch(r"(\d{4})-W(\d{2})", week)
    if not m:
        return None
    year, wk = int(m.group(1)), int(m.group(2))
    try:
        return datetime.fromisocalendar(year, wk, 1).date().isoformat()
    except ValueError:
        return None


def _coordination_block(week: str) -> dict:
    """Mirror server/routes/brand_admin_download.py coordination_build_status() from the
    committed coordination TSV, so the static badge shows the same 'Last built:' phrase."""
    monday = _week_monday_iso(week)
    path = COORD_DIR / f"weekly_packages_{monday}.tsv" if monday else None
    if path is None or not path.is_file():
        cands = sorted(COORD_DIR.glob("weekly_packages_*.tsv"), key=lambda p: p.stat().st_mtime, reverse=True)
        path = cands[0] if cands else None
    if path is None or not path.is_file():
        return {"status": "MISSING", "monday": monday, "mtime_iso": None, "relative": "never", "age_days": None}
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_days = (datetime.now(tz=timezone.utc) - mtime).total_seconds() / 86400.0
    # Static bridge: the packet is committed, so the badge reflects "package present",
    # not freshness of a cron run. Report PRESENT (console treats non-MISSING as built).
    return {
        "status": "PRESENT",
        "monday": path.stem.replace("weekly_packages_", ""),
        "mtime_iso": mtime.isoformat(),
        "relative": "committed package",
        "age_days": round(age_days, 2),
    }


def _build_archetype_index(unified: dict) -> dict[str, str]:
    """console_brand_id (locale-suffixed) -> archetype base."""
    idx: dict[str, str] = {}
    for bid, b in (unified.get("brands") or {}).items():
        if isinstance(b, dict) and b.get("brand_archetype_id"):
            idx[bid] = b["brand_archetype_id"]
    return idx


def _packet_dir_for_archetype(archetype: str, packet_dirs: list[str]) -> str | None:
    """Join archetype base -> on-disk packet dir name.

    Exact match wins (e.g. stillness_press); else a '<archetype>_<demographic>' prefix
    match (e.g. qi_foundation -> qi_foundation_cultivation). Prefer the shortest such
    match to avoid a longer archetype swallowing a shorter one's dir."""
    if archetype in packet_dirs:
        return archetype
    prefixed = sorted((d for d in packet_dirs if d.startswith(archetype + "_")), key=len)
    return prefixed[0] if prefixed else None


def _read_manifest(packet_dir: str, week: str) -> dict | None:
    mpath = PACKAGES_DIR / packet_dir / week / "manifest.json"
    if not mpath.is_file():
        return None
    try:
        return json.loads(mpath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _monolithic_zip(packet_dir: str, week: str) -> Path | None:
    z = PACKAGES_DIR / packet_dir / week / f"{packet_dir}_{week}.zip"
    return z if (z.is_file() and z.stat().st_size > 0) else None


def _axes_from_manifest(manifest: dict) -> dict[str, str]:
    deliv = manifest.get("deliverables") or {}
    out: dict[str, str] = {}
    for k in AXIS_KEYS:
        v = deliv.get(k)
        if isinstance(v, dict) and v.get("status"):
            out[k] = str(v["status"])
    return out


def _cost_usd(manifest: dict) -> float:
    """Pull the audiobook axis cost_usd (the only paid-risk axis); default 0 ($0 packet)."""
    deliv = manifest.get("deliverables") or {}
    ab = deliv.get("audiobook") or {}
    src = ab.get("source") or {}
    try:
        return float(src.get("cost_usd", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def build_bridge(week: str) -> dict:
    unified = _load_yaml(UNIFIED)
    buildability = _load_yaml(BUILDABILITY)
    non_buildable = (buildability.get("non_buildable") or {})

    arch_idx = _build_archetype_index(unified)
    packet_dirs = (
        sorted(d.name for d in PACKAGES_DIR.iterdir() if d.is_dir())
        if PACKAGES_DIR.is_dir()
        else []
    )
    coord = _coordination_block(week)

    brands: dict[str, dict] = {}
    blocked: dict[str, dict] = {}

    for cbid, archetype in sorted(arch_idx.items()):
        # 1) hard exclusions (devotion_path) — never a packet
        if archetype in HARD_EXCLUDE:
            blocked[cbid] = {
                "reason": "excluded — catalog not release-ready (engine re-point ws); see brand_buildability.yaml",
                "packet_dir": None,
                "archetype": archetype,
            }
            continue

        # 2) buildability gate (non_buildable archetypes -> no download, with reason)
        if archetype in non_buildable:
            entry = non_buildable[archetype] or {}
            blocked[cbid] = {
                "reason": (str(entry.get("reason") or "blocked, pending catalog reconciliation")).strip(),
                "packet_dir": None,
                "archetype": archetype,
                "shippable_count": entry.get("shippable_count"),
            }
            continue

        # 3) locate a REAL packet on disk for this archetype
        pdir = _packet_dir_for_archetype(archetype, packet_dirs)
        manifest = _read_manifest(pdir, week) if pdir else None
        mono = _monolithic_zip(pdir, week) if pdir else None
        if not (pdir and manifest and mono):
            blocked[cbid] = {
                "reason": "blocked, pending catalog reconciliation — no real weekly packet on disk for this brand/week",
                "packet_dir": pdir,
                "archetype": archetype,
            }
            continue

        axes = _axes_from_manifest(manifest)
        ready = {k: v for k, v in axes.items() if v == "ready"}
        headline_ready = sum(1 for k in HEADLINE_AXES if axes.get(k) == "ready")

        # 4) STUB GUARD — a manifest + tiny placeholder zip with 0 ready axes is a
        # seed scaffold, not a shippable packet. Log blocked; never surface as buildable.
        if headline_ready < MIN_READY_HEADLINE_AXES or mono.stat().st_size < MIN_REAL_ZIP_BYTES:
            blocked[cbid] = {
                "reason": (
                    "blocked, pending catalog reconciliation — packet dir is a seed scaffold "
                    f"({headline_ready} ready headline axes, {mono.stat().st_size}B zip); no shippable content yet"
                ),
                "packet_dir": pdir,
                "archetype": archetype,
            }
            continue

        brands[cbid] = {
            "packet_dir": pdir,
            "week": week,
            "week_monday": manifest.get("week_monday") or _week_monday_iso(week),
            "buildable": True,
            "package_type": manifest.get("package_type") or "",
            "axes": axes,
            "axis_count_ready": len(ready),
            "headline_axes_ready": headline_ready,
            "cost_usd": _cost_usd(manifest),
            "download": {
                # Real monolithic zip — served by FastAPI when ?api_base= is set (operator
                # running scripts/run_server.py). On static Pages the zip is LFS (130-byte
                # pointer) and artifacts/ is not in the deploy, so the console renders the
                # packet summary from THIS bridge inline and offers a client-built manifest
                # blob instead of a dead link. See console downloadAdminPacket().
                "api_path": f"/api/brand_admin/download/{pdir}/{week}",
                "filename": f"{pdir}_{week}.zip",
                "size_bytes": mono.stat().st_size,
                # Committed provenance copy (Pages-safe text deliverables only) for the record;
                # not fetched by the static console (artifacts/ is outside the Pages root).
                "release_record": f"artifacts/release/{week}/{pdir}/",
            },
            "coordination": coord,
        }

    out = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "week": week,
        "schema": 1,
        "brands": brands,
        "blocked": blocked,
    }
    return out


def _assert_no_leak(payload: dict) -> None:
    blob = json.dumps(payload, ensure_ascii=False)
    m = _LEAK_RE.search(blob)
    if m:
        raise SystemExit(
            f"REFUSING to write {OUT.name}: potential PII/secret leak matched {m.group(0)!r}. "
            "The public packet bridge must carry no emails/keys."
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the static weekly-packet bridge JSON.")
    ap.add_argument("--week", default=None, help="ISO week (e.g. 2026-W22). Default: newest on disk.")
    args = ap.parse_args()

    week = args.week or _newest_week_on_disk()
    if not week:
        raise SystemExit("No weekly packets found on disk (artifacts/weekly_packages/*/<week>/manifest.json).")

    payload = build_bridge(week)
    _assert_no_leak(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    nb = len(payload["brands"])
    nblk = len(payload["blocked"])
    print(f"wrote {nb} buildable + {nblk} blocked brands (week {week}) -> {OUT.relative_to(REPO)}")
    # sanity: the proven MVP brand must resolve with a real packet
    sp = payload["brands"].get("stillness_press_en_us")
    if sp:
        print(
            f"  stillness_press_en_us: packet_dir={sp['packet_dir']} "
            f"axes_ready={sp['axis_count_ready']} headline={sp['headline_axes_ready']}/4 "
            f"cost_usd={sp['cost_usd']} zip={sp['download']['filename']} ({sp['download']['size_bytes']}B)"
        )
    else:
        print("  WARNING: stillness_press_en_us has no real packet — check the join/week.")


if __name__ == "__main__":
    main()

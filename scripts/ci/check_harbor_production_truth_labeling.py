#!/usr/bin/env python3
"""Guard: catalog metadata must never be presented as shippable production files.

TRUTH-LABELING INVARIANT (signal: harbor-line-production-truth-labeling)

When a brand's delivery feed says ``production_files_ready: false`` (today: Harbor Line
Books / stabilizer, brand director Kamiko Parker), every ops surface that renders that
brand MUST label it "catalog ready, production files pending" and MUST NOT offer a
production packet download.

The failure mode this blocks is *catalog-as-production*: the weekly packet bridge is
regenerated independently of the delivery feed, so a brand can be marked ``buildable``
by the bridge while its rendered production files still do not exist. Before this gate,
a bridge "ready" verdict silently outranked ``production_files_ready: false`` and the
dashboard offered a download for books that had never been rendered.

This gate is deliberately BEHAVIOURAL, not a marker grep: it extracts the real guard
functions from the shipped HTML and executes them under node against a synthetic
"bridge says buildable" bridge. Deleting or inverting the guard fails the gate; renaming
things around it does not. Fix real failures by restoring the guard, never by editing
the expectation.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "brand-wizard-app" / "public"
DELIVERIES = PUBLIC / "brand_deliveries"
HANDOFF_HTML = PUBLIC / "brand_handoff_dashboard.html"
WEEKLY_OS_HTML = ROOT / "brand_admin_weekly_os.html"

# A brand with production_files_ready=false must carry a pending-flavoured delivery_status.
PENDING_STATUS_RE = re.compile(r"pending", re.IGNORECASE)


def _fail(errors: list[str]) -> int:
    for err in errors:
        print(f"check_harbor_production_truth_labeling.py: {err}", file=sys.stderr)
    return 1


def check_delivery_data(errors: list[str]) -> None:
    """A feed that is not production-ready must say so, and must not over-claim per book."""
    if not DELIVERIES.is_dir():
        errors.append(f"missing delivery feed dir: {DELIVERIES.relative_to(ROOT)}")
        return
    feeds = sorted(DELIVERIES.glob("*.json"))
    if not feeds:
        errors.append(f"no delivery feeds under {DELIVERIES.relative_to(ROOT)}")
        return
    for feed in feeds:
        rel = feed.relative_to(ROOT)
        try:
            data = json.loads(feed.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {rel}: {exc}")
            continue
        if data.get("production_files_ready") is not False:
            continue
        status = str(data.get("delivery_status") or "")
        if not PENDING_STATUS_RE.search(status):
            errors.append(
                f"{rel}: production_files_ready=false but delivery_status={status!r} "
                "does not say production files are pending"
            )
        for week, wdata in (data.get("weeks") or {}).items():
            for book in (wdata or {}).get("catalog_metadata") or []:
                if book.get("production_files_ready") is not False:
                    errors.append(
                        f"{rel}: week {week} book {book.get('book_id')!r} claims "
                        "production_files_ready but the brand feed is production-pending"
                    )


def _extract(src: str, pattern: str, label: str, errors: list[str]) -> str:
    match = re.search(pattern, src)
    if not match:
        errors.append(
            f"{label}: truth-labeling guard not found — the production_files_ready=false "
            "guard must not be removed or renamed"
        )
        return ""
    return match.group(0)


def check_guard_behaviour(errors: list[str]) -> None:
    """Execute the shipped guard logic: bridge 'buildable' must NOT clear production-pending."""
    handoff = HANDOFF_HTML.read_text(encoding="utf-8")
    weekly = WEEKLY_OS_HTML.read_text(encoding="utf-8")

    fns = [
        _extract(handoff, r"function packetBridgeStatus\(brandId\)\{[\s\S]*?\n\}", HANDOFF_HTML.name, errors),
        _extract(handoff, r"function resolvePacketBlock\(bridgeVerdict, delivery\)\{[\s\S]*?\n\}", HANDOFF_HTML.name, errors),
        _extract(weekly, r"function packetStatus\(bid\)\{[\s\S]*?\n\}", WEEKLY_OS_HTML.name, errors),
    ]
    if errors:
        return

    node = shutil.which("node")
    if not node:
        errors.append("node not found — cannot execute the behavioural truth-labeling check")
        return

    harness = """
%s
let PACKET_BRIDGE=null;
const PRODUCTION_PENDING_REASON='Catalog ready, production files pending.';
let DELIVERY=null;
const pendingDelivery={production_files_ready:false, weeks:{}};
// The regression scenario: the packet bridge says buildable while production files do not exist.
const buildableBridge={brands:{stabilizer_en_us:{buildable:true,week:'2026-W29'}},blocked:{}};
const out={};

// Surface 1 — brand_handoff_dashboard.html
PACKET_BRIDGE=buildableBridge;
out.handoff=resolvePacketBlock(packetBridgeStatus('stabilizer_en_us'), pendingDelivery);
// A brand that IS production-ready must still be able to show ready (guard must not over-block).
out.handoff_ready=resolvePacketBlock(packetBridgeStatus('stabilizer_en_us'), {production_files_ready:true, weeks:{}});

// Surface 2 — brand_admin_weekly_os.html
DELIVERY=pendingDelivery;
out.weekly=packetStatus('stabilizer_en_us');
DELIVERY={production_files_ready:true, weeks:{}};
out.weekly_ready=packetStatus('stabilizer_en_us');
console.log(JSON.stringify(out));
""" % "\n".join(fns)

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(harness)
        harness_path = fh.name
    try:
        proc = subprocess.run([node, harness_path], capture_output=True, text=True, timeout=60)
    finally:
        Path(harness_path).unlink(missing_ok=True)

    if proc.returncode != 0:
        errors.append(f"guard harness failed to execute: {proc.stderr.strip()}")
        return

    try:
        out = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as exc:
        errors.append(f"guard harness emitted non-JSON: {exc}: {proc.stdout[:200]!r}")
        return

    for surface, key in (("brand_handoff_dashboard.html", "handoff"), ("brand_admin_weekly_os.html", "weekly")):
        verdict = out.get(key) or {}
        if verdict.get("state") != "blocked":
            errors.append(
                f"{surface}: production_files_ready=false yielded state="
                f"{verdict.get('state')!r} — catalog metadata would be presented as a "
                "shippable production packet. production_files_ready=false is authoritative."
            )
    # The guard must label, not blanket-hide: a production-ready brand still reads ready.
    for surface, key in (("brand_handoff_dashboard.html", "handoff_ready"), ("brand_admin_weekly_os.html", "weekly_ready")):
        verdict = out.get(key) or {}
        if verdict.get("state") != "ready":
            errors.append(
                f"{surface}: production_files_ready=true yielded state={verdict.get('state')!r} "
                "— the guard must only block production-pending brands"
            )


def main() -> int:
    errors: list[str] = []
    for path in (HANDOFF_HTML, WEEKLY_OS_HTML):
        if not path.is_file():
            errors.append(f"missing surface: {path.relative_to(ROOT)}")
    if errors:
        return _fail(errors)

    check_delivery_data(errors)
    check_guard_behaviour(errors)
    if errors:
        return _fail(errors)

    print(
        "check_harbor_production_truth_labeling.py: OK — production_files_ready=false is "
        "authoritative on brand_handoff_dashboard.html + brand_admin_weekly_os.html"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

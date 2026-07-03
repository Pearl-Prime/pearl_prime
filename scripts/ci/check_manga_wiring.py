#!/usr/bin/env python3
"""Drift detector: config/manga/*.yaml must be wired or declared unwired.

The unwired-config-as-working kill. Prior manga sessions shipped config that
existed but was consumed by no code path, then reported the feature as working
(the vision-conformance audit found manga_mode_vessels.yaml loaded by nothing on
a callable path). This gate makes an unwired config a hard, visible fact: every
top-level config/manga/*.yaml must EITHER have >= 1 non-test Python consumer that
references it, OR declare `status: unwired` in its own body, OR be listed in the
KNOWN_UNWIRED allowlist below (with a reason + the roadmap milestone that wires
it). A NEW unwired config that does none of these cannot merge.

"Consumer" = a non-test .py under scripts/ (excluding scripts/ci/ — gates and
validators name configs without consuming them) or phoenix_v4/ whose text
references the config's stem. This catches configs with ZERO string-reachability
(future orphans). It does NOT prove call-reachability: a config whose only
reference is a loader module that nothing invokes will read as "wired" here even
though it is functionally dead. That deeper class is what KNOWN_UNWIRED records
(e.g. manga_mode_vessels: loader present, uncalled — the audit's finding) and
what roadmap M4 fixes; KNOWN_UNWIRED therefore takes precedence over a string
match so such configs are reported honestly as declared-unwired.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_wiring.py

Exit: 0 all configs wired-or-declared; 1 an undeclared unwired config exists.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so scripts.ci.X import resolves this
from drift_detector_git import repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))
CONFIG_DIR = "config/manga"
CONSUMER_ROOTS = ("scripts", "phoenix_v4")

# Configs known to be unwired on origin/main 2026-07-03 (vision-conformance
# audit). Each entry: reason + the roadmap milestone that removes it from here.
# To wire a config: add a real consumer, then delete its line. To add a NEW
# unwired config: prefer `status: unwired` in the file; use this list only for
# reference/historical YAMLs that are not runtime configs.
KNOWN_UNWIRED = {
    "manga_mode_vessels.yaml":
        "teacher/music narrative vessels; loader is test-only — roadmap M4 wires "
        "it into story_architect + chapter-writer prompt assembly",
    "anatomical_correction_loras.yaml": "research metadata, not a runtime config",
    "community_assets_audit_2026-04-29.yaml": "historical audit record",
    "genre_ite_profiles.yaml": "designed for ITE; integration pending",
    "japan_dual_track_config.yaml": "designed for JP dual-track; pipeline pending",
    "page_and_layout_enums.yaml": "reference/enum documentation",
    "sabido_roles.yaml": "designed for story architecture; integration pending",
}


def _has_status_unwired(path: Path) -> bool:
    try:
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped.replace(" ", "").lower() in ("status:unwired", "status:'unwired'",
                                                     'status:"unwired"'):
                return True
    except OSError:
        return False
    return False


def _consumer_index(repo_root: Path) -> str:
    """One big blob of all non-test consumer .py text (lowercased for matching)."""
    blobs: list[str] = []
    ci_dir = repo_root / "scripts" / "ci"
    for root in CONSUMER_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            parts = {p.lower() for p in py.parts}
            if "tests" in parts or py.name.startswith("test_"):
                continue
            if ci_dir in py.parents:  # gates/validators name configs, don't consume them
                continue
            try:
                blobs.append(py.read_text(errors="ignore"))
            except OSError:
                continue
    return "\n".join(blobs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="config/manga wiring gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = ap.parse_args(argv)
    repo_root: Path = args.repo_root

    cfg_dir = repo_root / CONFIG_DIR
    configs = sorted(p for p in cfg_dir.glob("*.yaml"))
    if not configs:
        print(f"MANGA WIRING: no configs under {CONFIG_DIR}", file=sys.stderr)
        return 0

    index = _consumer_index(repo_root)
    violations: list[str] = []
    wired = declared = 0
    for cfg in configs:
        stem = cfg.stem  # basename without .yaml
        # declaration takes precedence over an incidental string reference, so a
        # loader-present-but-uncalled config (manga_mode_vessels) is reported
        # honestly rather than passing silently as "wired".
        if cfg.name in KNOWN_UNWIRED or _has_status_unwired(cfg):
            declared += 1
            continue
        if stem in index:
            wired += 1
            continue
        violations.append(
            f"{CONFIG_DIR}/{cfg.name}: no non-test consumer references '{stem}' and "
            f"no `status: unwired` marker — wire it, add the marker, or add it to "
            f"KNOWN_UNWIRED with a reason")

    if not violations:
        print(f"MANGA WIRING: PASS ({wired} wired, {declared} declared-unwired, "
              f"{len(configs)} total)", file=sys.stderr)
        return 0
    for v in violations:
        print(f"FAIL: {v}", file=sys.stderr)
    print(f"MANGA WIRING: {len(violations)} undeclared unwired config(s) — blocking",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

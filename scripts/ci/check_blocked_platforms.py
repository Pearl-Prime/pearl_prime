#!/usr/bin/env python3
"""CI guard — refuse uploader/submitter scripts that target AI-blocked platforms.

Reads `config/publishing/ai_policy_blockers.yaml` (single source of truth from
PR #626 manga research) and scans uploader-pattern files for references to
BLOCKED / PARTNER_ONLY platforms without an explicit AI_POLICY_BLOCKER_OK waiver.

Usage:
    python3 scripts/ci/check_blocked_platforms.py
    python3 scripts/ci/check_blocked_platforms.py --paths scripts/manga/foo_upload.py

Exit codes:
    0 — clean / no violations
    1 — at least one blocked-platform target found without waiver
    2 — config not found / malformed

Run in CI (.github/workflows/blocked-platforms.yml or similar) on every PR.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / "config" / "publishing" / "ai_policy_blockers.yaml"


def _load_policy() -> dict:
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("ERROR: PyYAML required to run this check.", file=sys.stderr)
        sys.exit(2)
    if not POLICY_PATH.exists():
        print(f"ERROR: policy file missing: {POLICY_PATH}", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def _find_uploader_files(repo: Path, patterns: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    for pat in patterns:
        out.extend(repo.glob(pat))
    return sorted(set(out))


def _platform_keywords(name: str) -> list[str]:
    """Generate likely keyword spellings for a platform identifier."""
    base = name.lower()
    keywords = {base, base.replace("_", " "), base.replace("_", "")}
    # Special-cases for compound names
    if "shueisha" in base:
        keywords.update(["shueisha", "shōnen jump", "shonen jump", "weekly shonen jump"])
    if "mangaplus" in base:
        keywords.update(["mangaplus", "manga plus", "manga-plus"])
    if "jump_toon" in base:
        keywords.update(["jump toon", "jumptoon", "jump_toon"])
    if "jump_rookie" in base:
        keywords.update(["jump rookie", "jumprookie"])
    if "yen_press" in base:
        keywords.update(["yen press", "yenpress"])
    if "viz_media" in base:
        keywords.update(["viz media", "vizmedia"])
    if "kakao_page" in base:
        keywords.update(["kakao page", "kakaopage"])
    if "piccoma" in base:
        keywords.update(["piccoma", "smartoon"])
    if "tapas" in base:
        keywords.update(["tapas"])
    if "bilibili" in base:
        keywords.update(["bilibili"])
    if "kuaikan" in base:
        keywords.update(["kuaikan"])
    return [k for k in keywords if k]


def _has_waiver(text: str, platform: str) -> bool:
    pattern = re.compile(
        r"#\s*AI_POLICY_BLOCKER_OK:\s*([a-z_, ]+)", re.IGNORECASE
    )
    for m in pattern.finditer(text):
        granted = [p.strip().lower() for p in m.group(1).split(",")]
        if platform.lower() in granted:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Specific files to check (default: all uploader_filename_patterns from policy)",
    )
    args = parser.parse_args()

    policy = _load_policy()
    platforms = policy.get("platforms") or {}
    blocked = {
        name: spec
        for name, spec in platforms.items()
        if spec.get("status") in ("BLOCKED", "PARTNER_ONLY")
    }
    patterns = policy.get("uploader_filename_patterns") or []

    if args.paths:
        candidates = [Path(p) for p in args.paths]
    else:
        candidates = _find_uploader_files(REPO, patterns)

    violations: list[tuple[Path, str, str]] = []
    for f in candidates:
        if not f.exists() or not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        text_lower = text.lower()
        for plat_name, spec in blocked.items():
            keywords = _platform_keywords(plat_name)
            for kw in keywords:
                if kw in text_lower:
                    if _has_waiver(text, plat_name):
                        continue
                    rationale = (spec.get("rationale") or "").strip()
                    violations.append((f, plat_name, rationale[:200]))
                    break  # one violation per (file, platform) is enough

    if not violations:
        print(f"✅ No blocked-platform targets found in {len(candidates)} uploader file(s).")
        return 0

    print("❌ AI-policy blocker violations:\n")
    for f, plat, rationale in violations:
        print(f"  {f.relative_to(REPO)}")
        print(f"    targets: {plat}")
        print(f"    why blocked: {rationale}")
        print(f"    waiver hint: add `# AI_POLICY_BLOCKER_OK: {plat}` if intentional")
        print()
    print(
        f"Total violations: {len(violations)}\n"
        f"Source of truth: {POLICY_PATH.relative_to(REPO)}"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
G-CLAIM / Q-ENFORCE-02 — acceptance-layer claim language gate.

Blocks merge when changed CLOSEOUT*.md files (or PR body) use ship/bestseller
claim words without naming an acceptance layer from
docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md.

Also blocks "improve catalog register" language without a Layer-3 / ONTGP /
system-working packet reference (composer-as-flagship-lever drift).

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md

Usage:
  PYTHONPATH=scripts/ci:. python3 scripts/ci/check_acceptance_claim_language.py
  PYTHONPATH=scripts/ci:. python3 scripts/ci/check_acceptance_claim_language.py \\
      --base origin/main --head HEAD
  PR_BODY='...' PYTHONPATH=scripts/ci:. python3 scripts/ci/check_acceptance_claim_language.py

Exit: 0 pass; 1 fail.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ci for drift_detector_git
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))

# Claim triggers that require an acceptance-layer term nearby / in the same doc.
CLAIM_RE = re.compile(
    r"\b("
    r"bestseller(?:s)?"
    r"|shippable"
    r"|production[-_]ready"
    r"|register[-_\s]?PASS"
    r")\b",
    re.IGNORECASE,
)

ACCEPTANCE_LAYER_RE = re.compile(
    r"("
    r"structurally\s+clear"
    r"|authored\s+candidate"
    r"|system\s+working"
    r"|bestseller\s+register"
    r"|path\s+works"
    r"|Layer\s*[1-4]"
    r"|acceptance_layer\s*[:=]"
    r")",
    re.IGNORECASE,
)

# Spec §2: PRs that pitch "improve catalog register" without Layer-3 packet.
CATALOG_REGISTER_LEVER_RE = re.compile(
    r"improve\s+catalog\s+register",
    re.IGNORECASE,
)
LAYER3_PACKET_RE = re.compile(
    r"("
    r"Layer\s*3"
    r"|ONTGP"
    r"|system\s+working"
    r"|flagship_line_edit"
    r"|line[-_\s]?edit\s+lane"
    r")",
    re.IGNORECASE,
)

CLOSEOUT_NAME_RE = re.compile(r"(^|/)CLOSEOUT[^/]*\.md$", re.IGNORECASE)
# Also catch handoff closeouts that use the receipt naming.
CLOSEOUT_ALT_RE = re.compile(r"(^|/)[^/]*CLOSEOUT[^/]*\.(md|txt)$", re.IGNORECASE)

ALLOWLIST_MARKER = "CI-ALLOWLIST: claim-language-ok"


def _is_closeout_path(path: str) -> bool:
    p = path.replace("\\", "/")
    return bool(CLOSEOUT_NAME_RE.search(p) or CLOSEOUT_ALT_RE.search(p))


def _collect_pr_body() -> str:
    chunks: list[str] = []
    for key in ("PR_BODY", "GITHUB_PR_BODY"):
        val = os.environ.get(key)
        if val:
            chunks.append(val)
    return "\n".join(chunks)


def _scan_text(label: str, text: str) -> list[str]:
    violations: list[str] = []
    if not text or not text.strip():
        return violations
    if ALLOWLIST_MARKER in text:
        return violations

    has_claim = bool(CLAIM_RE.search(text))
    has_layer = bool(ACCEPTANCE_LAYER_RE.search(text))
    if has_claim and not has_layer:
        samples = sorted({m.group(0) for m in CLAIM_RE.finditer(text)})[:6]
        violations.append(
            f"{label}: claim language {samples} without acceptance-layer term "
            f"(structurally clear | authored candidate | system working | "
            f"bestseller register | Layer 1-4). Q-ENFORCE-02 / G-CLAIM."
        )

    if CATALOG_REGISTER_LEVER_RE.search(text) and not LAYER3_PACKET_RE.search(text):
        violations.append(
            f"{label}: 'improve catalog register' without Layer-3 / ONTGP / "
            f"system working / flagship_line_edit packet "
            f"(composer is not the flagship lever)."
        )
    return violations


def check(
    *,
    base: str | None,
    head: str,
    pr_body: str | None = None,
    repo_root: Path | None = None,
) -> list[str]:
    root = repo_root or REPO_ROOT
    violations: list[str] = []

    paths = changed_paths(base, head, root)
    # When no base (local dirty), also scan unstaged/untracked closeouts via git status.
    if not base and not paths:
        import subprocess

        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        for line in (proc.stdout or "").splitlines():
            path = line[3:].strip().replace("\\", "/")
            if " -> " in path:
                path = path.split(" -> ", 1)[-1]
            if path:
                paths.append(path)

    for rel in paths:
        if not _is_closeout_path(rel):
            continue
        fp = root / rel
        if not fp.is_file():
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            violations.append(f"{rel}: unreadable ({exc})")
            continue
        violations.extend(_scan_text(rel, text))

    body = pr_body if pr_body is not None else _collect_pr_body()
    if body.strip():
        violations.extend(_scan_text("PR_BODY", body))

    return violations


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-CLAIM / Q-ENFORCE-02 acceptance claim language")
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument(
        "--pr-body-file",
        default=None,
        help="Optional file containing PR body text (else PR_BODY env)",
    )
    args = ap.parse_args(argv)

    pr_body = None
    if args.pr_body_file:
        pr_body = Path(args.pr_body_file).read_text(encoding="utf-8", errors="replace")

    violations = check(base=args.base, head=args.head, pr_body=pr_body)
    if not violations:
        print(
            "G-CLAIM / Q-ENFORCE-02: PASS — no unscoped bestseller/shippable claims "
            "in changed CLOSEOUT*.md or PR body."
        )
        return 0

    print("G-CLAIM / Q-ENFORCE-02: FAIL", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
        print(f"::error::{v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

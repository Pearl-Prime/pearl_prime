#!/usr/bin/env python3
"""Drift detector: a PR may not introduce NEW Simplified text into zh-TW atoms.

THE DRIFT CLASS: simplified-as-traditional
------------------------------------------
zh-TW (Taiwan) prose must be Traditional Chinese. Simplified characters have
repeatedly leaked into landed zh-TW atoms — most often when a Simplified-emitting
translator is routed at zh-TW (Qwen does this: see the standing "never route Qwen
at zh-TW" rule). The corpus audit at
`artifacts/qa/zh_tw_simplified_contamination_20260715/` found **869 of 5,172**
landed zh-TW files already carrying Simplified characters.

Per the "memory is recall, not enforcement" doctrine, that audit is only recall:
without a gate, contamination keeps re-entering `main`. This is the enforcement.

WHY THIS IS A DELTA (RATCHET) GATE, NOT AN ABSOLUTE ONE
-------------------------------------------------------
869 contaminated files are ALREADY on main. A gate that simply failed on
contamination would turn main permanently red and block every unrelated PR —
which gets the gate disabled within a day, leaving the drift unenforced. So:

  * `scripts/ci/zh_tw_simplified_baseline.tsv` records the pre-existing debt,
    dated and pinned to a sha, as an explicit known-debt allowlist.
  * The gate only inspects zh-TW files **changed by this PR**. An unrelated PR
    touches no zh-TW atoms and the gate is a no-op.
  * A changed file FAILS iff it carries MORE distinct Simplified chars than its
    baseline entry (or has an entry of 0 / no entry at all and is contaminated).

The baseline may only SHRINK. Repairing a file and dropping its row is always
allowed; the gate nudges you to. Adding a row to silence a red PR is the exact
bypass this gate exists to prevent — do not do it, and do not accept a PR that
does.

DETECTOR
--------
Reused, not greenfielded, from the zh-TW lanes' calibrated rule (frozen into
`scripts/ci/zh_tw_simplified_charset.py`): a char is Simplified-only iff OpenCC
`s2t` changes it AND Big5 cannot encode it. Naive s2t alone false-flags
台/吃/游/群/床 across 1,651 legitimate Taiwan-usage files; the Big5 leg is
load-bearing. Severity tiers key on DISTINCT Simplified chars (matching the
lane-02 audit): >=10 WHOLE_FILE, 3-9 PARTIAL, 1-2 SPOT_LEAK.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_zh_tw_simplified_contamination.py \
        --base origin/main --head HEAD

Exit: 0 pass; 1 fail (new or worsened contamination in a changed zh-TW file).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector_git import repo_root_from_script  # noqa: E402
from zh_tw_simplified_charset import (  # noqa: E402
    SIMPLIFIED_ONLY_CHARS,
    severity_for,
)

REPO_ROOT = repo_root_from_script(Path(__file__))
BASELINE_PATH = Path(__file__).resolve().parent / "zh_tw_simplified_baseline.tsv"
AUDIT_DIR = "artifacts/qa/zh_tw_simplified_contamination_20260715"

ZH_TW_SUFFIX = "/locales/zh-TW/CANONICAL.txt"


def is_zh_tw_atom(path: str) -> bool:
    return path.startswith("atoms/") and path.endswith(ZH_TW_SUFFIX)


@dataclass
class Violation:
    path: str
    found: int
    allowed: int
    chars: str

    @property
    def kind(self) -> str:
        return "NEW_CONTAMINATION" if self.allowed == 0 else "WORSENED"


def _display(path: Path, repo_root: Path) -> str:
    """Repo-relative path for messages, tolerating a baseline outside the root.

    Must never raise: this runs inside the gate's own failure message, and a
    traceback there would bury the guidance a blocked author needs to read.
    """
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def load_baseline(path: Path) -> dict[str, int]:
    """Parse the known-debt baseline: {zh_tw_file: distinct_simplified_chars}."""
    baseline: dict[str, int] = {}
    if not path.exists():
        return baseline
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2 or parts[0] == "distinct_simplified_chars":
            continue
        try:
            baseline[parts[1]] = int(parts[0])
        except ValueError:
            continue
    return baseline


def distinct_simplified(text: str) -> tuple[int, str]:
    """Return (distinct Simplified-only char count, those chars) for *text*."""
    seen: list[str] = []
    for ch in text:
        if ch in SIMPLIFIED_ONLY_CHARS and ch not in seen:
            seen.append(ch)
    return len(seen), "".join(seen)


def changed_zh_tw_paths(base: str | None, head: str,
                        repo_root: Path) -> list[tuple[str, str | None]]:
    """Changed zh-TW atoms as (new_path, old_path_or_None).

    Renames are resolved so a moved-but-unmodified contaminated file inherits its
    baseline entry from the old path instead of false-failing as brand-new debt.
    """
    cmd = ["git", "diff", "--name-status", "-M",
           f"{base}...{head}" if base else "HEAD"]
    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True,
                          text=True, check=False)
    if proc.returncode != 0:
        return []
    out: list[tuple[str, str | None]] = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        if status.startswith("D"):
            continue  # deleting a contaminated file removes debt; never a violation
        if status.startswith("R") and len(parts) >= 3:
            new, old = parts[2].replace("\\", "/"), parts[1].replace("\\", "/")
        else:
            new, old = parts[-1].replace("\\", "/"), None
        if is_zh_tw_atom(new):
            out.append((new, old))
    return out


def all_zh_tw_paths(ref: str, repo_root: Path) -> list[str]:
    """Every landed zh-TW atom at *ref* (corpus-ratchet mode)."""
    proc = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref],
                          cwd=repo_root, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    return [p for p in proc.stdout.splitlines() if is_zh_tw_atom(p)]


def read_at(ref: str | None, path: str, repo_root: Path) -> str | None:
    """File contents at *ref* (or working tree when ref is None)."""
    if ref is None:
        p = repo_root / path
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    proc = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=repo_root,
                          capture_output=True, text=True, check=False)
    return None if proc.returncode != 0 else proc.stdout


def read_many(ref: str, paths: list[str], repo_root: Path) -> dict[str, str]:
    """Batch-read *paths* at *ref* via one `git cat-file --batch`.

    Corpus mode reads ~5k blobs; one subprocess per file would take ~a minute.
    stdin is fed from a thread because filling the request pipe while git blocks
    writing its (much larger) output deadlocks both ends.
    """
    import threading

    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=repo_root,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert proc.stdin and proc.stdout

    def feed() -> None:
        try:
            for p in paths:
                proc.stdin.write(f"{ref}:{p}\n".encode())
            proc.stdin.flush()
            proc.stdin.close()
        except (BrokenPipeError, ValueError):
            pass

    threading.Thread(target=feed, daemon=True).start()

    out: dict[str, str] = {}
    for p in paths:
        header = proc.stdout.readline().decode(errors="replace").strip()
        if not header or header.endswith("missing"):
            continue
        try:
            size = int(header.split()[-1])
        except ValueError:
            continue
        out[p] = proc.stdout.read(size).decode("utf-8", errors="replace")
        proc.stdout.read(1)  # trailing newline
    proc.wait()
    return out


def evaluate(pairs: list[tuple[str, str | None]], baseline: dict[str, int],
             head: str | None, repo_root: Path,
             texts: dict[str, str] | None = None) -> tuple[list[Violation], list[str]]:
    """Return (violations, repaired_paths) for the changed zh-TW files."""
    violations: list[Violation] = []
    repaired: list[str] = []
    for new_path, old_path in pairs:
        if texts is not None:
            text = texts.get(new_path)
        else:
            text = read_at(head, new_path, repo_root)
        if text is None:
            continue
        found, chars = distinct_simplified(text)
        allowed = baseline.get(new_path)
        if allowed is None and old_path is not None:
            allowed = baseline.get(old_path)  # rename inherits its debt
        allowed = allowed or 0
        if found > allowed:
            violations.append(Violation(new_path, found, allowed, chars))
        elif allowed > 0 and found < allowed:
            repaired.append(f"{new_path} ({allowed} -> {found})")
    return violations, repaired


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--base", default=None, help="git base ref for PR diff")
    ap.add_argument("--head", default="HEAD", help="git head ref")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="scan exactly these paths (tests / explicit)")
    ap.add_argument("--baseline", type=Path, default=BASELINE_PATH)
    ap.add_argument("--worktree", action="store_true",
                    help="read contents from the working tree instead of --head")
    ap.add_argument("--audit-corpus", action="store_true",
                    help="ratchet the WHOLE landed zh-TW corpus against the baseline "
                         "(readiness runner mode) instead of only PR-changed files")
    args = ap.parse_args(argv)

    baseline = load_baseline(args.baseline)
    head_ref = None if args.worktree else args.head

    if args.paths is not None:
        pairs = [(p.replace("\\", "/"), None) for p in args.paths
                 if is_zh_tw_atom(p.replace("\\", "/"))]
    elif args.audit_corpus:
        pairs = [(p, None) for p in all_zh_tw_paths(args.head, args.repo_root)]
    else:
        pairs = changed_zh_tw_paths(args.base, args.head, args.repo_root)

    if not pairs:
        print("zh-TW Simplified gate: no zh-TW atoms changed — nothing to check.")
        return 0

    texts = None
    if head_ref is not None and len(pairs) > 50:
        texts = read_many(head_ref, [p for p, _ in pairs], args.repo_root)

    violations, repaired = evaluate(pairs, baseline, head_ref, args.repo_root, texts)

    scope = "landed" if args.audit_corpus else "changed"
    print(f"zh-TW Simplified gate: checked {len(pairs)} {scope} zh-TW atom(s) "
          f"against {len(baseline)} baseline entries.")

    if repaired:
        print(f"\n  {len(repaired)} file(s) IMPROVED vs baseline — thank you. "
              f"Shrink the baseline by updating/removing these rows in "
              f"{_display(args.baseline, args.repo_root)}:")
        for r in repaired[:20]:
            print(f"    - {r}")

    if not violations:
        print("\nPASS: no new or worsened Simplified contamination.")
        return 0

    print(f"\nFAIL: {len(violations)} zh-TW file(s) gained Simplified characters.\n")
    for v in violations:
        print(f"  [{v.kind}] {v.path}")
        print(f"      severity={severity_for(v.found)} "
              f"distinct_simplified={v.found} baseline_allowed={v.allowed}")
        print(f"      chars: {v.chars[:40]}{'…' if len(v.chars) > 40 else ''}")
    print(
        "\nzh-TW prose must be Traditional Chinese.\n"
        "  * If a translator emitted this: do NOT route Qwen at zh-TW — it emits\n"
        "    Simplified. zh-TW is Tier-1 Claude only.\n"
        "  * Fix the PROSE, not this gate. Do NOT add rows to\n"
        f"    {_display(args.baseline, args.repo_root)} to silence this — that\n"
        "    allowlist is pre-existing debt and may only shrink.\n"
        f"  * Corpus context / severity tiers: {AUDIT_DIR}/\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

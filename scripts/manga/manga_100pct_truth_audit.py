#!/usr/bin/env python3
"""Evidence-first truth audit for the Phoenix Omega manga 100% claim."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
GREEN_CLAIM_RE = re.compile(r"(?im)^\s*[-*]?\s*manga-100pct-final\s*=\s*GREEN\s*$")


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def _default_runner(command: list[str]) -> CommandResult:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _resolve(root: Path, path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _dotted_get(data: Any, dotted: str) -> Any:
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _is_present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _assert_json(data: dict[str, Any], assertions: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for dotted, expected in assertions.items():
        actual = _dotted_get(data, dotted)
        if expected == "present":
            if not _is_present(actual):
                failures.append(f"{dotted} is missing")
        elif actual != expected:
            failures.append(f"{dotted}: expected {expected!r}, found {actual!r}")
    return failures


def _walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_values(item)
    else:
        yield value


def _scan_forbidden_json(data: Any, forbidden: list[str]) -> list[str]:
    hits: set[str] = set()
    for value in _walk_values(data):
        if isinstance(value, str):
            for token in forbidden:
                if token in value:
                    hits.add(token)
    return sorted(hits)


def _load_json(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label} unreadable: {exc}"]
    if not isinstance(loaded, dict):
        return None, [f"{label} JSON root must be an object"]
    return loaded, []


def _registry_pr_rows(agent_row: dict[str, Any]) -> list[dict[str, Any]]:
    rows = agent_row.get("prs")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    if "pr_number" in agent_row or "merge_sha" in agent_row:
        return [agent_row]
    return []


def gh_verify_pr(
    repository: str,
    pr_number: int,
    expected_merge_sha: str,
    runner: Callable[[list[str]], CommandResult] = _default_runner,
) -> list[str]:
    """Verify one PR directly against GitHub using the authenticated ``gh`` CLI."""
    result = runner(["gh", "api", f"repos/{repository}/pulls/{pr_number}"])
    if result.returncode:
        return [f"PR #{pr_number} GitHub verification failed: {result.stderr.strip() or 'gh api failed'}"]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [f"PR #{pr_number} GitHub response was invalid JSON: {exc}"]
    failures: list[str] = []
    if not payload.get("merged_at"):
        failures.append(f"PR #{pr_number} is not merged on GitHub")
    actual_sha = str(payload.get("merge_commit_sha") or "")
    if actual_sha != expected_merge_sha:
        failures.append(
            f"PR #{pr_number} merge SHA mismatch: registry {expected_merge_sha}, GitHub {actual_sha or 'missing'}"
        )
    return failures


def _audit_merge_registry(
    path: Path,
    *,
    display_path: str,
    required_agents: list[str],
    foundation_pr_number: int,
    repository: str,
    github_verifier: Callable[[str, int, str], list[str]] | None,
    require_github_verification: bool,
) -> tuple[list[str], list[tuple[int, str]]]:
    if not path.is_file():
        return [f"merge registry missing: {display_path}"], []
    data, failures = _load_json(path, "merge registry")
    if data is None:
        return failures, []

    verified_targets: list[tuple[int, str]] = []
    foundation = data.get("foundation") or {}
    if foundation.get("pr_number") != foundation_pr_number:
        failures.append(f"merge registry foundation PR is not #{foundation_pr_number}")
    foundation_sha = str(foundation.get("merge_sha") or "")
    if foundation.get("merged") is not True or not SHA_RE.fullmatch(foundation_sha):
        failures.append("merge registry lacks a valid merged foundation SHA")
    else:
        verified_targets.append((foundation_pr_number, foundation_sha))

    agents = data.get("agents") or {}
    for name in required_agents:
        row = agents.get(name)
        if not isinstance(row, dict):
            failures.append(f"merge registry missing agent {name}")
            continue
        prs = _registry_pr_rows(row)
        if not prs:
            failures.append(f"agent {name} has no PR records")
            continue
        for index, pr_row in enumerate(prs, start=1):
            label = f"agent {name} PR record {index}"
            pr_number = pr_row.get("pr_number")
            merge_sha = str(pr_row.get("merge_sha") or "")
            if pr_row.get("merged") is not True:
                failures.append(f"{label} is not recorded merged")
            if not isinstance(pr_number, int) or pr_number <= 0:
                failures.append(f"{label} has no valid PR number")
            if not SHA_RE.fullmatch(merge_sha):
                failures.append(f"{label} has no valid merge SHA")
            if isinstance(pr_number, int) and pr_number > 0 and SHA_RE.fullmatch(merge_sha):
                verified_targets.append((pr_number, merge_sha))

    if require_github_verification and github_verifier is None:
        failures.append("live GitHub merge-SHA verification was required but not performed")
    elif github_verifier is not None:
        seen: set[tuple[int, str]] = set()
        for pr_number, merge_sha in verified_targets:
            target = (pr_number, merge_sha)
            if target in seen:
                continue
            seen.add(target)
            failures.extend(github_verifier(repository, pr_number, merge_sha))
    return failures, verified_targets


def _audit_foundation(path: Path, display_path: str, foundation_pr_number: int) -> list[str]:
    if not path.is_file():
        return [f"foundation receipt missing: {display_path}"]
    data, failures = _load_json(path, "foundation receipt")
    if data is None:
        return failures
    if data.get("pr_number") != foundation_pr_number:
        failures.append(f"foundation receipt PR is not #{foundation_pr_number}")
    if data.get("merged") is not True:
        failures.append(f"foundation receipt says PR #{foundation_pr_number} is not merged")
    if data.get("required_checks_pass") is not True:
        failures.append("foundation receipt says required checks did not pass")
    if data.get("dispatch_allowed") is not True:
        failures.append("foundation receipt does not authorize dispatch")
    if not SHA_RE.fullmatch(str(data.get("merge_sha") or "")):
        failures.append("foundation receipt has no valid merge SHA")
    return failures


def _audit_requirement(root: Path, name: str, rule: dict[str, Any], forbidden_json: list[str]) -> dict[str, Any]:
    path = _resolve(root, str(rule.get("path") or ""))
    shown = _display_path(root, path)
    failures: list[str] = []
    if not path.is_file():
        failures.append(f"required artifact missing: {shown}")
        return {"name": name, "path": shown, "green": False, "failures": failures}

    data: dict[str, Any] | None = None
    if path.suffix.lower() == ".json":
        data, load_failures = _load_json(path, name)
        failures.extend(load_failures)
        if data is not None:
            failures.extend(_assert_json(data, rule.get("json_assertions") or {}))
            for dotted, minimum in (rule.get("min_list_items") or {}).items():
                actual = _dotted_get(data, dotted)
                if not isinstance(actual, list) or len(actual) < int(minimum):
                    failures.append(f"{dotted}: expected at least {minimum} list items")
            forbidden_hits = _scan_forbidden_json(data, forbidden_json)
            if forbidden_hits:
                failures.append("forbidden JSON value(s): " + ", ".join(forbidden_hits))
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in rule.get("forbidden_tokens") or []:
            if token.lower() in text.lower():
                failures.append(f"forbidden token present: {token}")
        minimum_rows = rule.get("min_data_rows")
        if minimum_rows is not None:
            rows = [line for line in text.splitlines() if line.strip()]
            data_rows = max(0, len(rows) - 1)
            if data_rows < int(minimum_rows):
                failures.append(f"expected at least {minimum_rows} data rows, found {data_rows}")

    for token in rule.get("forbidden_filename_tokens") or []:
        if token.lower() in path.name.lower():
            failures.append(f"forbidden filename token present: {token}")

    required_globs = rule.get("required_globs") or []
    if required_globs:
        matches: set[Path] = set()
        for pattern in required_globs:
            matches.update(path.parent.glob(str(pattern)))
        minimum = int(rule.get("min_glob_matches") or 1)
        if len([item for item in matches if item.is_file()]) < minimum:
            failures.append(f"expected at least {minimum} proof files matching {required_globs}")

    return {"name": name, "path": shown, "green": not failures, "failures": failures}


def _audit_all_json_paths(root: Path, scan_roots: list[str], forbidden: list[str]) -> list[str]:
    failures: list[str] = []
    for configured_root in scan_roots:
        scan_root = _resolve(root, configured_root)
        if not scan_root.exists():
            continue
        for path in sorted(scan_root.rglob("*.json")):
            data, load_failures = _load_json(path, _display_path(root, path))
            failures.extend(load_failures)
            if data is None:
                continue
            hits = _scan_forbidden_json(data, forbidden)
            if hits:
                failures.append(
                    f"{_display_path(root, path)} contains forbidden JSON value(s): {', '.join(hits)}"
                )
    return failures


def audit(
    repo_root: Path,
    config_path: Path,
    *,
    github_verifier: Callable[[str, int, str], list[str]] | None = None,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    failures: list[str] = []
    requirement_results: dict[str, Any] = {}
    repository = str(config.get("repository") or "")
    foundation_pr_number = int(config.get("foundation_pr_number") or 5597)

    foundation_path = _resolve(repo_root, str(config.get("foundation_receipt") or ""))
    failures.extend(
        _audit_foundation(
            foundation_path,
            _display_path(repo_root, foundation_path),
            foundation_pr_number,
        )
    )

    registry_path = _resolve(repo_root, str(config.get("merge_registry") or ""))
    registry_failures, verified_targets = _audit_merge_registry(
        registry_path,
        display_path=_display_path(repo_root, registry_path),
        required_agents=list(config.get("required_agents") or []),
        foundation_pr_number=foundation_pr_number,
        repository=repository,
        github_verifier=github_verifier,
        require_github_verification=bool(config.get("require_github_verification", False)),
    )
    failures.extend(registry_failures)

    forbidden_json = list(config.get("forbidden_json_values") or [])
    for name, rule in (config.get("requirements") or {}).items():
        result = _audit_requirement(repo_root, name, rule or {}, forbidden_json)
        requirement_results[name] = result
        failures.extend(f"{name}: {item}" for item in result["failures"])

    failures.extend(
        _audit_all_json_paths(
            repo_root,
            list(config.get("json_scan_roots") or []),
            forbidden_json,
        )
    )

    false_claims: list[str] = []
    if failures:
        for claim_file in config.get("claim_files") or []:
            path = _resolve(repo_root, str(claim_file))
            if path.is_file() and GREEN_CLAIM_RE.search(path.read_text(encoding="utf-8", errors="replace")):
                false_claims.append(f"corrected unsupported GREEN claim in {_display_path(repo_root, path)}")

    final = "GREEN" if not failures else "NOT_GREEN"
    return {
        "manga-100pct-final": final,
        "repository": repository,
        "foundation_receipt": _display_path(repo_root, foundation_path),
        "merge_registry": _display_path(repo_root, registry_path),
        "github_verified_pr_count": len(set(verified_targets)) if github_verifier is not None else 0,
        "requirements": requirement_results,
        "failures": failures,
        "false_claims_corrected": false_claims,
        "next_actions": [
            "satisfy and regenerate each failed evidence artifact",
            "record real PR merge SHAs in the merge registry",
            "rerun with --verify-github under an authenticated identity",
            "retain the resulting JSON and Markdown receipts",
        ] if failures else [],
        "final_sentence": (
            "FINAL VERDICT: Phoenix Omega manga is GREEN for the explicitly audited production scope."
            if final == "GREEN"
            else "FINAL VERDICT: Phoenix Omega manga is NOT GREEN for the explicitly audited production scope."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Manga 100% Truth Audit — 2026-07-14",
        "",
        f"- manga-100pct-final={report['manga-100pct-final']}",
        f"- github-verified-pr-count={report['github_verified_pr_count']}",
        "",
        "## Evidence requirements",
        "",
    ]
    for name, row in report["requirements"].items():
        lines.append(f"- {name}: {'GREEN' if row['green'] else 'NOT_GREEN'} — `{row['path']}`")
        lines.extend(f"  - {failure}" for failure in row["failures"])
    lines.extend(["", "## Blockers", ""])
    lines.extend([f"- {item}" for item in report["failures"]] or ["- None"])
    lines.extend(["", "## False claims corrected", ""])
    lines.extend([f"- {item}" for item in report["false_claims_corrected"]] or ["- None"])
    lines.extend(["", "## Next actions", ""])
    lines.extend([f"- {item}" for item in report["next_actions"]] or ["- None"])
    lines.extend(["", report["final_sentence"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--verify-github", action="store_true")
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else args.repo_root / args.config
    json_out = args.json_out if args.json_out.is_absolute() else args.repo_root / args.json_out
    markdown_out = args.markdown_out if args.markdown_out.is_absolute() else args.repo_root / args.markdown_out
    verifier = gh_verify_pr if args.verify_github else None
    report = audit(args.repo_root, config_path, github_verifier=verifier)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(markdown_out, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["manga-100pct-final"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())

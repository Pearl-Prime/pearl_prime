#!/usr/bin/env python3
"""
PR Governance Review — Automated Pearl_PM + Pearl_Architect gate.

Runs on every PR to main. Validates:
1. SCOPE: files changed stay within a single subsystem (or explicitly cross-subsystem)
2. AUTHORITY: the subsystem's authority docs exist and are referenced
3. MASS DELETION: blocks PRs deleting >50 files
4. DRIFT: detects common drift patterns (duplicate specs, parallel UIs, etc.)
5. OWNERSHIP: files are in the right subsystem per SUBSYSTEM_AUTHORITY_MAP
6. CONFLICT: checks for overlap with active workstreams
7. REINVENTION: WARNs when an added file looks like a fork of a canonical artifact
   (Layer 3 of the anti-reinvention system; docs/specs/CANONICAL_ARTIFACTS_REGISTRY_SPEC.md)
8. DURATION: BLOCKs a format_registry.yaml edit that does not co-change the duration
   derivation spec (docs/DURATION_DERIVATION_SPEC.md §6)
9. SKELETON FREEZE: BLOCKs `feat(catalog): {locale} skeletons {brand} batch {N}` PRs
   (any locale except CJK ja_/zh_/ko_) while skeleton_freeze.yaml → active: true
10. FLAGSHIP GOLDEN: BLOCKs CANONICAL_FLAGSHIP_CH1 snapshot edits without
    `GOLDEN-UPDATE-RATIFIED: <OPD ref>` in PR body / commit messages
11. FLAGSHIP PIPELINE: WARNs when phoenix_v4/{planning,rendering,exercises}/ or
    scripts/run_pipeline.py changes without a test change in the same PR

Exit 0 = approved. Exit 1 = blocked (with reasons).

Usage:
    python3 scripts/ci/pr_governance_review.py
    # Reads PR diff from git (origin/main...HEAD)

    python3 scripts/ci/pr_governance_review.py --json
    # Output machine-readable JSON

    python3 scripts/ci/pr_governance_review.py --pr 253
    # Review a specific PR by number (requires gh CLI)
"""

import subprocess
import sys
import os
import json
import csv
import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Subsystem mapping
# ---------------------------------------------------------------------------

def load_subsystem_map():
    """Load SUBSYSTEM_AUTHORITY_MAP.tsv → dict of path prefixes → subsystem info."""
    tsv_path = REPO_ROOT / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv"
    if not tsv_path.exists():
        return {}

    subsystems = {}
    with open(tsv_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            sid = row.get("subsystem_id", "")
            config_paths = row.get("config_path", "").split(";")
            authority = row.get("authority_doc", "").split(";")
            owner = row.get("owner_agent", "")
            for cp in config_paths:
                cp = cp.strip()
                if cp:
                    subsystems[cp] = {
                        "subsystem_id": sid,
                        "authority_docs": [a.strip() for a in authority if a.strip()],
                        "owner_agent": owner,
                    }
    return subsystems


def load_active_workstreams():
    """Load ACTIVE_WORKSTREAMS.tsv → list of active workstream write scopes."""
    tsv_path = REPO_ROOT / "artifacts" / "coordination" / "ACTIVE_WORKSTREAMS.tsv"
    if not tsv_path.exists():
        return []

    workstreams = []
    with open(tsv_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            status = row.get("status", "")
            if status in ("active", "in_progress"):
                workstreams.append({
                    "id": row.get("workstream_id", ""),
                    "task": row.get("task", ""),
                    "write_scope": row.get("write_scope", ""),
                    "owner": row.get("owner_agent", ""),
                })
    return workstreams


def load_canonical_registry():
    """Load CANONICAL_ARTIFACTS_REGISTRY.tsv → list of canonical-artifact rows.

    Mirrors load_subsystem_map() / load_active_workstreams(): a TSV DictReader,
    tab-delimited, that FAILS OPEN — returns [] if the file is absent so a PR is
    never crashed because the registry has not landed on that ref (the registry is
    a convenience that may or may not be present on a given branch/checkout, per
    CANONICAL_ARTIFACTS_REGISTRY_SPEC.md §1.1).

    Schema (9 cols, see spec §2): concept_key, canonical_path, sha_or_pr,
    owner_agent, subsystem, edit_not_recreate, last_verified, supersedes, notes.
    Rows with an empty canonical_path are skipped (cannot anchor a match).

    A `canonical_path` cell MAY carry multiple ';'-joined mirror paths (the seed
    `teacher_real_photos` row lists `teacher_pics/;brand-wizard-app/public/teacher_pics/`;
    this mirrors how SUBSYSTEM_AUTHORITY_MAP.tsv ';'-joins config_path). Each mirror is
    expanded into its OWN row (sharing the other 8 columns) so every mirror is
    independently matchable by the guard; the original combined string is preserved in
    `canonical_path_raw` for messages.
    """
    tsv_path = REPO_ROOT / "artifacts" / "coordination" / "CANONICAL_ARTIFACTS_REGISTRY.tsv"
    if not tsv_path.exists():
        return []

    rows = []
    with open(tsv_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            raw = (row.get("canonical_path") or "").strip()
            if not raw:
                continue
            mirrors = [p.strip() for p in raw.split(";") if p.strip()]
            for cp in mirrors:
                rows.append({
                    "concept_key": (row.get("concept_key") or "").strip(),
                    "canonical_path": cp,
                    "canonical_path_raw": raw,
                    "sha_or_pr": (row.get("sha_or_pr") or "").strip(),
                    "owner_agent": (row.get("owner_agent") or "").strip(),
                    "subsystem": (row.get("subsystem") or "").strip(),
                    "edit_not_recreate": (row.get("edit_not_recreate") or "").strip(),
                    "last_verified": (row.get("last_verified") or "").strip(),
                    "supersedes": (row.get("supersedes") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                })
    return rows


def load_skeleton_freeze_config():
    """Load config/governance/skeleton_freeze.yaml → freeze dict or None.

    FAIL-OPEN: returns None if the file is absent, malformed, or PyYAML is missing —
    a missing marker must never crash PR review.
    """
    yaml_path = REPO_ROOT / "config" / "governance" / "skeleton_freeze.yaml"
    if not yaml_path.exists():
        return None

    try:
        import yaml
    except Exception:
        return None

    try:
        with open(yaml_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    return data


# Catalog skeleton batch PR title: feat(catalog): es_ES skeletons legacy_builder batch 2
_SKELETON_BATCH_TITLE_RE = re.compile(
    r"(?i)^feat\(catalog\):\s+"
    r"(\S+)\s+"
    r"skeletons\s+"
    r"(\S+)\s+"
    r"batch\s+"
    r"(\d+)\s*$"
)

_DEFAULT_CJK_SKELETON_PREFIXES = ("ja_", "zh_", "ko_")


def _cjk_skeleton_prefixes(freeze_cfg) -> tuple[str, ...]:
    if not freeze_cfg:
        return _DEFAULT_CJK_SKELETON_PREFIXES
    raw = freeze_cfg.get("excluded_cjk_locale_prefixes") or _DEFAULT_CJK_SKELETON_PREFIXES
    if not isinstance(raw, (list, tuple)):
        return _DEFAULT_CJK_SKELETON_PREFIXES
    out = tuple(str(p).lower() for p in raw if p)
    return out or _DEFAULT_CJK_SKELETON_PREFIXES


def _is_frozen_catalog_skeleton_batch_title(title: str, freeze_cfg) -> bool:
    """True if title matches the observed skeleton-batch storm pattern, excluding CJK locales."""
    m = _SKELETON_BATCH_TITLE_RE.match((title or "").strip())
    if not m:
        return False
    locale = m.group(1).lower().replace("-", "_")
    for prefix in _cjk_skeleton_prefixes(freeze_cfg):
        if locale.startswith(prefix):
            return False
    return True


def get_pr_title(pr_number=None) -> str:
    """Best-effort PR title for governance checks (fail-open → '')."""
    if pr_number:
        try:
            res = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "title"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            if res.returncode == 0 and res.stdout.strip():
                return (json.loads(res.stdout) or {}).get("title") or ""
        except Exception:
            pass
        return ""

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and os.path.isfile(event_path):
        try:
            with open(event_path) as f:
                ev = json.load(f)
            pr = ev.get("pull_request") or {}
            title = pr.get("title") or ""
            if title:
                return title
        except Exception:
            pass

    head_ref = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if head_ref:
        try:
            res = subprocess.run(
                ["gh", "pr", "view", head_ref, "--json", "title"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            if res.returncode == 0 and res.stdout.strip():
                return (json.loads(res.stdout) or {}).get("title") or ""
        except Exception:
            pass

    return ""


def _is_exempt_skeleton_pr(pr_number, freeze_cfg) -> bool:
    if not pr_number or not freeze_cfg:
        return False
    try:
        num = int(pr_number)
    except (TypeError, ValueError):
        return False
    exempt = freeze_cfg.get("exempt_pr_numbers") or []
    try:
        return num in {int(x) for x in exempt}
    except (TypeError, ValueError):
        return num in exempt


def check_skeleton_freeze(files, freeze_cfg, pr_title="", pr_number=None):
    """BLOCK catalog skeleton batch PRs while skeleton_freeze.yaml active (OPD-20260630-001)."""
    if not freeze_cfg or not freeze_cfg.get("active"):
        return {
            "check": "skeleton_freeze",
            "status": "PASS",
            "message": "Skeleton freeze inactive — batch merges allowed.",
            "details": {"active": False},
        }

    if freeze_cfg.get("operator_override"):
        return {
            "check": "skeleton_freeze",
            "status": "PASS",
            "message": "Skeleton freeze bypassed via operator_override in skeleton_freeze.yaml.",
            "details": {"active": True, "operator_override": True},
        }

    if _is_exempt_skeleton_pr(pr_number, freeze_cfg):
        return {
            "check": "skeleton_freeze",
            "status": "PASS",
            "message": f"PR #{pr_number} is exempt from skeleton freeze (pre-staged spine).",
            "details": {"exempt_pr": pr_number},
        }

    title = (pr_title or "").strip()
    title_match = _is_frozen_catalog_skeleton_batch_title(title, freeze_cfg)

    if title_match:
        opd = freeze_cfg.get("opd") or "OPD-20260630-001"
        lift = freeze_cfg.get("lift_condition") or "first R2 EPUB batch shipped"
        return {
            "check": "skeleton_freeze",
            "status": "BLOCKED",
            "message": (
                f"Catalog skeleton batch merge blocked by {opd} (hard freeze). "
                f"Lift condition: {lift}. Set active: false in "
                f"config/governance/skeleton_freeze.yaml after the first R2 EPUB batch ships. "
                f"Pre-staged spine PRs (#3110/#3123/#3127/#3147/#3166) remain exempt. "
                f"CJK locales (ja_/zh_/ko_) are excluded from this freeze."
            ),
            "details": {
                "opd": opd,
                "lift_condition": lift,
                "pr_title": title,
                "marker": "config/governance/skeleton_freeze.yaml",
            },
        }

    return {
        "check": "skeleton_freeze",
        "status": "PASS",
        "message": "Not a catalog skeleton batch PR — freeze inert for this change.",
        "details": {"active": True, "title_match": False},
    }


def load_reinvention_allowlist():
    """Load config/governance/reinvention_allowlist.yaml → set of allowed paths.

    Standing, reviewed exceptions to the reinvention guard (spec §5). FAILS OPEN:
    returns an empty set if the file is absent, empty, malformed, or if PyYAML is
    not importable — a missing/broken allowlist must never crash a PR. Each entry's
    `allowed_path` is normalized (see _normalize_path) for comparison.

    Ships EMPTY (schema-only) in Phase 1; entries are added under review.
    """
    yaml_path = REPO_ROOT / "config" / "governance" / "reinvention_allowlist.yaml"
    if not yaml_path.exists():
        return set()

    try:
        import yaml  # local import: keep the module importable even without PyYAML
    except Exception:
        return set()

    try:
        with open(yaml_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return set()

    entries = []
    if isinstance(data, dict):
        entries = data.get("allowlist") or []
    if not isinstance(entries, list):
        return set()

    allowed = set()
    for ent in entries:
        if isinstance(ent, dict):
            ap = ent.get("allowed_path")
            if isinstance(ap, str) and ap.strip():
                allowed.add(_normalize_path(ap))
    return allowed

# ---------------------------------------------------------------------------
# Git diff analysis
# ---------------------------------------------------------------------------

def _telemetry_pr_changed_files(source: str, **kwargs: object) -> None:
    parts = [f"[pr_governance_review] changed_files_source={source}"]
    for k, v in kwargs.items():
        if v is None:
            continue
        s = str(v).replace("\n", " ").strip()
        if not s:
            continue
        parts.append(f"{k}={s}")
    print(" ".join(parts), file=sys.stderr)


def _parse_gh_name_status(stdout: str) -> list[dict]:
    files: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            files.append({"status": status.strip(), "path": path.strip()})
    return files


def _change_type_to_status(change_type: str) -> str:
    ct = (change_type or "").upper()
    if ct == "ADDED":
        return "A"
    if ct in ("DELETED", "REMOVED"):
        return "D"
    if ct in ("MODIFIED", "CHANGED"):
        return "M"
    if ct == "RENAMED":
        return "M"
    return "M"


def _files_from_pr_view_json(pr_number) -> list[dict]:
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "files"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    for ent in data.get("files") or []:
        path = ent.get("path") or ""
        if not path:
            continue
        out.append(
            {
                "status": _change_type_to_status(ent.get("changeType") or ""),
                "path": path,
            }
        )
    return out


def get_changed_files(pr_number=None):
    """Get list of changed files with status (A/M/D)."""
    if not pr_number:
        result = subprocess.run(
            ["git", "diff", "--name-status", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return _parse_gh_name_status(result.stdout)

    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--name-status"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    parsed = _parse_gh_name_status(result.stdout)
    if result.returncode == 0 and parsed:
        _telemetry_pr_changed_files("gh_pr_diff_name_status", gh_pr_diff_rc=result.returncode)
        return parsed

    extra: dict[str, object] = {}
    if result.returncode != 0:
        extra["gh_pr_diff_rc"] = result.returncode
        err = (result.stderr or "").strip()
        if err:
            extra["gh_pr_diff_stderr"] = err[:200]
    elif not (result.stdout or "").strip():
        extra["detail"] = "empty_or_failed_diff"
    else:
        extra["detail"] = "gh_pr_diff_unparseable"

    _telemetry_pr_changed_files("gh_pr_view_json_files", **extra)
    return _files_from_pr_view_json(pr_number)

# ---------------------------------------------------------------------------
# Override-token plumbing (shared by reinvention + duration guards)
# ---------------------------------------------------------------------------

def _normalize_path(path: str) -> str:
    """Normalize a repo-relative path for comparison ONLY (originals kept for msgs).

    - strip leading './'
    - collapse repeated '/'
    - strip a trailing '/' (dir rows compare as their bare path)
    - lowercase-fold (case-insensitive match)

    Per CANONICAL_ARTIFACTS_REGISTRY_SPEC.md §4.1 step 1. The folded form is used
    only for equality/sibling tests; the original string is surfaced in messages.
    """
    p = (path or "").strip()
    if p.startswith("./"):
        p = p[2:]
    while "//" in p:
        p = p.replace("//", "/")
    p = p.rstrip("/")
    return p.lower()


def collect_override_text(pr_number=None) -> str:
    """Gather text in which an override token may appear: PR body + commit messages.

    Override tokens (NEW-ARTIFACT-JUSTIFIED:, DURATION-DERIVATION-OK:,
    GOLDEN-UPDATE-RATIFIED:) live in the PR description OR a commit body (per both
    PR description OR a commit body (per both specs). This reader is fail-open and
    additive — it never raises; if no source is available it returns "".

    Sources, all unioned (any one carrying the token is sufficient):
      1. Env PR_BODY / GITHUB_PR_BODY — a CI workflow MAY export the PR description
         (no-op today; forward-compatible so a later workflow tweak Just Works).
      2. `gh pr view <n> --json body` when --pr <n> was passed (the script already
         shells gh for that path).
      3. Commit messages on origin/main..HEAD (default, no --pr path) — the
         spec-blessed "commit body" channel, available in the current CI.
    """
    chunks: list[str] = []

    for env_key in ("PR_BODY", "GITHUB_PR_BODY"):
        val = os.environ.get(env_key)
        if val:
            chunks.append(val)

    if pr_number:
        try:
            res = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "body"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            if res.returncode == 0 and res.stdout.strip():
                body = (json.loads(res.stdout) or {}).get("body") or ""
                if body:
                    chunks.append(body)
        except Exception:
            pass
    else:
        try:
            res = subprocess.run(
                ["git", "log", "--format=%B", "origin/main..HEAD"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            if res.returncode == 0 and res.stdout.strip():
                chunks.append(res.stdout)
        except Exception:
            pass

    return "\n".join(chunks)


def _has_override_token(text: str, token: str) -> bool:
    """True if `token` appears with a non-empty reason, e.g. 'TOKEN: some reason'.

    Both override tokens require a human-written reason (spec §5 / §6.2). A bare
    'TOKEN:' with nothing after it does NOT count. Matching is case-sensitive on
    the token (the tokens are upper-kebab by convention) and tolerant of leading
    whitespace / list-bullets.
    """
    if not text:
        return False
    esc = re.escape(token)
    # token, optional whitespace, ':', then at least one non-space char on the line
    pattern = re.compile(rf"{esc}\s*:\s*\S.*", re.MULTILINE)
    return bool(pattern.search(text))

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_mass_deletion(files):
    """BLOCK if >50 files deleted."""
    deleted = [f for f in files if f["status"] == "D"]
    if len(deleted) > 50:
        dirs = defaultdict(int)
        for f in deleted:
            top = f["path"].split("/")[0]
            dirs[top] += 1
        top_dirs = sorted(dirs.items(), key=lambda x: -x[1])[:10]
        return {
            "check": "mass_deletion",
            "status": "BLOCKED",
            "message": f"PR deletes {len(deleted)} files (threshold: 50)",
            "details": {
                "deleted_count": len(deleted),
                "top_directories": dict(top_dirs),
            }
        }
    return {
        "check": "mass_deletion",
        "status": "PASS",
        "message": f"{len(deleted)} deletions (within threshold)",
    }


def check_subsystem_scope(files, subsystem_map):
    """WARN if PR touches multiple subsystems without explicit cross-subsystem flag."""
    touched_subsystems = set()
    unowned_files = []

    for f in files:
        path = f["path"]
        matched = False
        for prefix, info in subsystem_map.items():
            if path.startswith(prefix.rstrip("*").rstrip("/")):
                touched_subsystems.add(info["subsystem_id"])
                matched = True
                break
        if not matched:
            # Check top-level directory mapping
            top = path.split("/")[0]
            common_unowned = {".github", ".claude", "CLAUDE.md", ".gitignore",
                            "README.md", "ps.txt", "requirements.txt"}
            if top not in common_unowned and not path.startswith("artifacts/"):
                unowned_files.append(path)

    if len(touched_subsystems) > 3:
        return {
            "check": "subsystem_scope",
            "status": "WARN",
            "message": f"PR touches {len(touched_subsystems)} subsystems: {', '.join(sorted(touched_subsystems))}. Consider splitting.",
            "details": {"subsystems": sorted(touched_subsystems)},
        }

    return {
        "check": "subsystem_scope",
        "status": "PASS",
        "message": f"Touches {len(touched_subsystems)} subsystem(s)",
        "details": {"subsystems": sorted(touched_subsystems)},
    }


def check_authority_docs(files, subsystem_map):
    """WARN if authority docs for touched subsystems don't exist."""
    missing_docs = []
    for f in files:
        path = f["path"]
        for prefix, info in subsystem_map.items():
            if path.startswith(prefix.rstrip("*").rstrip("/")):
                for doc in info["authority_docs"]:
                    doc_path = REPO_ROOT / doc
                    if not doc_path.exists():
                        missing_docs.append(doc)
                break

    missing_docs = list(set(missing_docs))
    if missing_docs:
        return {
            "check": "authority_docs",
            "status": "WARN",
            "message": f"{len(missing_docs)} authority doc(s) missing: {', '.join(missing_docs[:5])}",
            "details": {"missing": missing_docs},
        }

    return {
        "check": "authority_docs",
        "status": "PASS",
        "message": "All authority docs present",
    }


def check_drift_patterns(files):
    """WARN on common drift patterns."""
    warnings = []

    added_files = [f["path"] for f in files if f["status"] == "A"]

    # Pattern 1: New spec when canonical exists
    new_specs = [f for f in added_files if f.startswith("specs/") and f.endswith(".md")]
    if len(new_specs) > 2:
        warnings.append(f"Adding {len(new_specs)} new specs — verify no duplicates of existing canonical specs")

    # Pattern 2: New docs that might duplicate existing
    new_docs = [f for f in added_files if f.startswith("docs/") and f.endswith(".md")]
    if len(new_docs) > 5:
        warnings.append(f"Adding {len(new_docs)} new docs — verify against DOCS_INDEX for duplicates")

    # Pattern 3: New config dirs that might shadow existing
    new_configs = [f for f in added_files if f.startswith("config/") and f.endswith(".yaml")]

    # Pattern 4: Files outside standard directories
    nonstandard = [f for f in added_files if "/" not in f and not f.startswith(".")]
    if nonstandard:
        warnings.append(f"Root-level files added: {', '.join(nonstandard[:5])}. Should these be in a subdirectory?")

    if warnings:
        return {
            "check": "drift_patterns",
            "status": "WARN",
            "message": "; ".join(warnings),
            "details": {"warnings": warnings},
        }

    return {
        "check": "drift_patterns",
        "status": "PASS",
        "message": "No drift patterns detected",
    }


def check_workstream_conflict(files, workstreams):
    """WARN if PR modifies files claimed by an active workstream."""
    conflicts = []
    for ws in workstreams:
        scope_paths = [s.strip() for s in ws["write_scope"].split(";") if s.strip()]
        for f in files:
            for sp in scope_paths:
                sp_clean = sp.rstrip("*").rstrip("/")
                if sp_clean and f["path"].startswith(sp_clean):
                    conflicts.append({
                        "file": f["path"],
                        "workstream": ws["id"],
                        "owner": ws["owner"],
                    })
                    break

    if conflicts:
        ws_ids = list(set(c["workstream"] for c in conflicts))
        return {
            "check": "workstream_conflict",
            "status": "WARN",
            "message": f"Overlaps with {len(ws_ids)} active workstream(s): {', '.join(ws_ids)}",
            "details": {"conflicts": conflicts[:10]},
        }

    return {
        "check": "workstream_conflict",
        "status": "PASS",
        "message": "No active workstream conflicts",
    }


def check_reinvention(files, registry, allowlist=None, override_text=""):
    """Layer-3 anti-reinvention guard (CANONICAL-ARTIFACTS-REGISTRY-V1-01).

    WARNs when an ADDED file looks like a fork of a canonical artifact recorded in
    artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv. Spec:
    docs/specs/CANONICAL_ARTIFACTS_REGISTRY_SPEC.md §4.

    SEVERITY (Q-CAR-SEVERITY): **WARN-only** in Phase 1 — never BLOCKED. A
    false-positive block on a legitimately-new artifact is worse than a missed
    reinvention. Promotion to BLOCKED for NO-without-ratification rows is a deferred
    follow-up gated on false-positive-rate data.

    MATCH-ALGO (Q-CAR-MATCH-ALGO): **full normalized canonical_path**, NOT bare
    basename. Bare-basename matching produces false positives on ubiquitous names
    (CANONICAL.txt, README.md, config.yaml). Two deterministic match shapes fire
    (Phase-2a, path-match arm; spec §4.1 step 3):
      (a) exact-path: a newly ADDED file whose normalized path equals a registry
          row's normalized canonical_path (the canonical was deleted+re-added, or a
          duplicate landed at the same path on a parallel branch).
      (b) sibling-fork: an ADDED file with the SAME basename as a canonical_path but
          under a DIFFERENT parent dir (e.g. pearl_news/v2/assemble_v52.py vs
          canonical pearl_news/pipeline/assemble_v52.py) — a likely fork. Directory
          canonical rows (path ending '/') have no basename and skip arm (b).

    The content-overlap (semantic) arm is **Phase-2b** and is NOT implemented here:
    it would require a local / Tier-2 embedding model (Gemma/Qwen via Ollama) per
    the LLM Tier policy + .github/workflows/llm-policy-enforcement.yml. A guard that
    phoned a paid LLM API would itself be blocked. See spec §4.2.

    SUPPRESSION (spec §5):
      - override tag `NEW-ARTIFACT-JUSTIFIED: <reason>` in the PR body / commit body
        → the candidate is acknowledged (skipped) for this PR.
      - config/governance/reinvention_allowlist.yaml standing allowlist → an added
        path that is a reviewed, recurring mirror never WARNs.

    FAIL-OPEN: an empty/absent registry yields a no-op PASS (registry may not be on
    this ref). Returns the standard dict shape {check, status, message, details}.
    """
    if allowlist is None:
        allowlist = set()

    if not registry:
        return {
            "check": "reinvention",
            "status": "PASS",
            "message": "Canonical registry absent/empty — reinvention guard is a no-op on this ref.",
            "details": {"registry_rows": 0},
        }

    has_global_override = _has_override_token(override_text, "NEW-ARTIFACT-JUSTIFIED")

    added = [f for f in files if f.get("status") == "A"]

    # Pre-index registry rows by normalized canonical path and by basename.
    by_norm_path = {}
    by_basename = defaultdict(list)
    for row in registry:
        norm = _normalize_path(row["canonical_path"])
        by_norm_path[norm] = row
        # Directory canonicals (original ended with '/') have no usable basename.
        if not row["canonical_path"].rstrip().endswith("/"):
            base = norm.rsplit("/", 1)[-1]
            if base:
                by_basename[base].append(row)

    findings = []
    for f in added:
        orig_path = f["path"]
        norm = _normalize_path(orig_path)

        # Allowlisted standing mirror → never WARN.
        if norm in allowlist:
            continue

        # Arm (a): exact normalized canonical_path match.
        row = by_norm_path.get(norm)
        match_kind = None
        if row is not None:
            match_kind = "exact_path"
        else:
            # Arm (b): same basename under a different parent dir.
            base = norm.rsplit("/", 1)[-1]
            for cand in by_basename.get(base, []):
                cand_norm = _normalize_path(cand["canonical_path"])
                if cand_norm != norm:  # different full path → a likely fork
                    row = cand
                    match_kind = "sibling_basename"
                    break

        if row is None:
            continue

        finding = {
            "added_path": orig_path,
            "canonical_path": row["canonical_path"],
            "concept_key": row["concept_key"],
            "owner_agent": row["owner_agent"],
            "edit_not_recreate": row["edit_not_recreate"],
            "match_kind": match_kind,
            "requires_ratification": row["edit_not_recreate"].startswith("NO"),
        }
        findings.append(finding)

    if not findings:
        return {
            "check": "reinvention",
            "status": "PASS",
            "message": f"No likely reinventions among added files ({len(registry)} canonical rows checked).",
            "details": {"registry_rows": len(registry), "added_checked": len(added)},
        }

    if has_global_override:
        return {
            "check": "reinvention",
            "status": "PASS",
            "message": (
                f"{len(findings)} candidate reinvention(s) acknowledged via "
                f"NEW-ARTIFACT-JUSTIFIED override. Ensure a registry row was added in this PR."
            ),
            "details": {"justified": findings, "override": "NEW-ARTIFACT-JUSTIFIED"},
        }

    parts = []
    for fnd in findings:
        msg = (
            f"'{fnd['added_path']}' looks like a fork of canonical "
            f"'{fnd['canonical_path']}' (concept '{fnd['concept_key']}', owner "
            f"{fnd['owner_agent'] or '?'})"
        )
        if fnd["requires_ratification"]:
            msg += " — NO-without-ratification: a cap-entry/operator ratification is required for a new variant"
        parts.append(msg)

    message = (
        "Possible reinvention(s): " + "; ".join(parts)
        + ". Remediation: edit the canonical artifact, or add the "
        "'NEW-ARTIFACT-JUSTIFIED: <reason>' override + a registry row in this same PR."
    )
    return {
        "check": "reinvention",
        "status": "WARN",
        "message": message,
        "details": {"findings": findings, "registry_rows": len(registry)},
    }


def check_duration_derivation(files, override_text=""):
    """Duration co-change guard (DURATION-DERIVATION-01).

    Spec: docs/DURATION_DERIVATION_SPEC.md §6 (CI guard contract).

    v1 = **path-level co-change BLOCK** (§6.1–§6.2). `get_changed_files()` returns
    [{status, path}] — changed file PATHS only, no diff content / no field values —
    so the guard cannot read whether word_range numerically changed. Rule:

      TRIGGER: config/format_selection/format_registry.yaml is in the changed-paths
               set (status A or M).
      REQUIRE: docs/DURATION_DERIVATION_SPEC.md is ALSO in the changed-paths set
               (forces the author to re-read the derivation contract whenever
               word_range / fill_regime / duration fields could move), ELSE BLOCK.
      OVERRIDE: a PR-body / commit-trailer token `DURATION-DERIVATION-OK: <reason>`
               downgrades BLOCK → WARN (for registry edits that provably don't touch
               word_range/fill_regime/duration — e.g. adding a
               compatible_structural_formats entry). The token requires a
               human-written reason.

    A PR that does NOT touch format_registry.yaml → PASS (guard inert).

    ±15% BAND (§6.3, recorded here as the contract; NOT computed in v1): when the
    guard graduates to value-level it accepts a derived label within **±15%** of the
    real target — deliberately WIDER than config/duration_scorecard.yaml's
    `duration_tolerance_pct: 10` (the scorecard's 10% is for *measurement* of
    renders; the derivation guard's 15% is for *label acceptance*). The 15% band
    keeps the two already-accepted deep formats green (deep_book_4h real −11%,
    deep_book_6h real +2%); the scorecard's 10% would wrongly flag deep_book_4h.

    v2 (§6.4, noted — NOT built here): value-level. Read format_registry.yaml at
    origin/main and at HEAD, diff word_range / fill_regime / cap_word_target per
    format, recompute audiobook_minutes/ebook_minutes
    (audiobook = round(word_target / tts_wpm=150); ebook = round(word_target /
    ebook_wpm=230); word_target derived from fill_regime cap|floor|midpoint, §4.1),
    and BLOCK if the stored label is outside ±15% of the recomputed value. en-US
    only (§7); skip formats without a word_range (§8). Requires reading file
    *contents* at two refs (the script already shells git; additive).

    Returns the standard dict shape {check, status, message, details}.
    """
    REGISTRY_PATH = "config/format_selection/format_registry.yaml"
    SPEC_PATH = "docs/DURATION_DERIVATION_SPEC.md"

    changed_paths = {f.get("path") for f in files}

    registry_touched = REGISTRY_PATH in changed_paths
    if not registry_touched:
        return {
            "check": "duration_derivation",
            "status": "PASS",
            "message": f"{REGISTRY_PATH} not in this PR — duration co-change guard inert.",
            "details": {"registry_touched": False},
        }

    spec_touched = SPEC_PATH in changed_paths
    if spec_touched:
        return {
            "check": "duration_derivation",
            "status": "PASS",
            "message": (
                f"{REGISTRY_PATH} edited and {SPEC_PATH} co-changed — "
                "duration derivation contract re-read together."
            ),
            "details": {"registry_touched": True, "spec_touched": True},
        }

    has_override = _has_override_token(override_text, "DURATION-DERIVATION-OK")
    if has_override:
        return {
            "check": "duration_derivation",
            "status": "WARN",
            "message": (
                f"{REGISTRY_PATH} edited WITHOUT {SPEC_PATH}, but "
                "'DURATION-DERIVATION-OK: <reason>' override present — downgraded BLOCK→WARN. "
                "Confirm this edit does not touch word_range / fill_regime / duration fields."
            ),
            "details": {
                "registry_touched": True,
                "spec_touched": False,
                "override": "DURATION-DERIVATION-OK",
            },
        }

    return {
        "check": "duration_derivation",
        "status": "BLOCKED",
        "message": (
            f"{REGISTRY_PATH} is edited but {SPEC_PATH} is NOT co-changed. A change to the "
            "runtime-format registry must travel with the duration derivation contract "
            "(word_range/fill_regime/duration fields drive advertised minutes). Either edit "
            f"{SPEC_PATH} in this PR, or add 'DURATION-DERIVATION-OK: <reason>' to the PR body "
            "if this edit provably does not touch word_range/fill_regime/duration."
        ),
        "details": {"registry_touched": True, "spec_touched": False, "override": None},
    }


def check_pr_size(files):
    """INFO on PR size for awareness."""
    total = len(files)
    added = len([f for f in files if f["status"] == "A"])
    modified = len([f for f in files if f["status"] == "M"])
    deleted = len([f for f in files if f["status"] == "D"])

    status = "PASS"
    msg = f"{total} files ({added} added, {modified} modified, {deleted} deleted)"

    if total > 200:
        status = "WARN"
        msg = f"Large PR: {msg}. Consider splitting into smaller PRs."
    elif total > 500:
        status = "BLOCKED"
        msg = f"Very large PR: {msg}. Must split or get explicit approval."

    return {
        "check": "pr_size",
        "status": status,
        "message": msg,
        "details": {"total": total, "added": added, "modified": modified, "deleted": deleted},
    }


FLAGSHIP_SNAPSHOT_PATHS = {
    "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt",
    "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json",
}

FLAGSHIP_PIPELINE_TOUCH_PREFIXES = (
    "phoenix_v4/planning/",
    "phoenix_v4/rendering/",
    "phoenix_v4/exercises/",
    "scripts/run_pipeline.py",
)

FLAGSHIP_TEST_TOUCH_PREFIXES = (
    "tests/",
    "scripts/ci/check_flagship",
)


def _path_touched(files, predicate) -> list[str]:
    hits = []
    for f in files:
        path = f.get("path", "")
        if predicate(path):
            hits.append(path)
    return hits


def check_flagship_golden_ratification(files, override_text=""):
    """BLOCK snapshot edits without operator ratification (GOLDEN-UPDATE-RATIFIED)."""
    changed_paths = {f.get("path") for f in files}
    snapshot_touched = sorted(changed_paths & FLAGSHIP_SNAPSHOT_PATHS)
    if not snapshot_touched:
        return {
            "check": "flagship_golden_ratification",
            "status": "PASS",
            "message": "Flagship CH1 golden snapshot not in this PR — ratification guard inert.",
            "details": {"snapshot_touched": []},
        }
    if _has_override_token(override_text, "GOLDEN-UPDATE-RATIFIED"):
        return {
            "check": "flagship_golden_ratification",
            "status": "PASS",
            "message": (
                "Flagship CH1 golden snapshot edited with GOLDEN-UPDATE-RATIFIED override present."
            ),
            "details": {"snapshot_touched": snapshot_touched, "override": True},
        }
    return {
        "check": "flagship_golden_ratification",
        "status": "BLOCKED",
        "message": (
            "Flagship CH1 golden snapshot changed without operator ratification. "
            "Add 'GOLDEN-UPDATE-RATIFIED: <OPD ref>' to the PR body / commit message, "
            "or restore via `git checkout <sha> -- artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`; "
            "do NOT fresh-fix. Golden recipe: "
            "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json"
        ),
        "details": {"snapshot_touched": snapshot_touched, "override": False},
    }


def check_flagship_pipeline_test_coupling(files):
    """WARN when flagship pipeline paths change without a test change in the same PR."""
    pipeline_hits = _path_touched(
        files,
        lambda p: any(p == pref or p.startswith(pref) for pref in FLAGSHIP_PIPELINE_TOUCH_PREFIXES),
    )
    if not pipeline_hits:
        return {
            "check": "flagship_pipeline_test_coupling",
            "status": "PASS",
            "message": "No flagship pipeline paths in this PR — test-coupling guard inert.",
            "details": {"pipeline_touched": []},
        }
    test_hits = _path_touched(
        files,
        lambda p: any(p.startswith(pref) for pref in FLAGSHIP_TEST_TOUCH_PREFIXES),
    )
    if test_hits:
        return {
            "check": "flagship_pipeline_test_coupling",
            "status": "PASS",
            "message": (
                f"Flagship pipeline paths changed with co-test updates "
                f"({len(test_hits)} test file(s))."
            ),
            "details": {"pipeline_touched": pipeline_hits, "test_touched": test_hits},
        }
    return {
        "check": "flagship_pipeline_test_coupling",
        "status": "WARN",
        "message": (
            "Flagship pipeline paths changed without a test change in this PR. "
            "Add/update tests/product/test_flagship_contract.py and/or "
            "scripts/ci/check_flagship_book_parity.py coverage."
        ),
        "details": {"pipeline_touched": pipeline_hits, "test_touched": []},
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    use_json = "--json" in sys.argv
    pr_number = None
    for i, arg in enumerate(sys.argv):
        if arg == "--pr" and i + 1 < len(sys.argv):
            pr_number = sys.argv[i + 1]

    subsystem_map = load_subsystem_map()
    workstreams = load_active_workstreams()
    registry = load_canonical_registry()
    allowlist = load_reinvention_allowlist()
    skeleton_freeze = load_skeleton_freeze_config()
    files = get_changed_files(pr_number)
    pr_title = get_pr_title(pr_number)

    if not files:
        if use_json:
            print(json.dumps({"status": "PASS", "message": "No files changed", "checks": []}))
        else:
            print("✅ No files changed — nothing to review.")
        sys.exit(0)

    override_text = collect_override_text(pr_number)

    # Run all checks
    results = [
        check_mass_deletion(files),
        check_pr_size(files),
        check_subsystem_scope(files, subsystem_map),
        check_authority_docs(files, subsystem_map),
        check_drift_patterns(files),
        check_workstream_conflict(files, workstreams),
        check_reinvention(files, registry, allowlist, override_text),
        check_duration_derivation(files, override_text),
        check_skeleton_freeze(files, skeleton_freeze, pr_title, pr_number),
        check_flagship_golden_ratification(files, override_text),
        check_flagship_pipeline_test_coupling(files),
    ]

    blocked = [r for r in results if r["status"] == "BLOCKED"]
    warned = [r for r in results if r["status"] == "WARN"]
    passed = [r for r in results if r["status"] == "PASS"]

    overall = "BLOCKED" if blocked else ("WARN" if warned else "PASS")

    if use_json:
        print(json.dumps({
            "status": overall,
            "checks": results,
            "summary": {
                "blocked": len(blocked),
                "warnings": len(warned),
                "passed": len(passed),
            }
        }, indent=2))
    else:
        print("=" * 60)
        print("PR GOVERNANCE REVIEW (Pearl_PM + Pearl_Architect)")
        print("=" * 60)

        for r in results:
            icon = {"PASS": "✅", "WARN": "⚠️ ", "BLOCKED": "⛔"}[r["status"]]
            print(f"{icon} [{r['check']}] {r['message']}")

        print()
        if blocked:
            print(f"⛔ BLOCKED — {len(blocked)} blocking issue(s). Do NOT merge.")
            for b in blocked:
                print(f"   → {b['check']}: {b['message']}")
        elif warned:
            print(f"⚠️  APPROVED WITH WARNINGS — {len(warned)} warning(s). Review before merge.")
        else:
            print("✅ APPROVED — all checks passed.")

    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()

"""Unit tests for the two Phase-2 governance guards added to pr_governance_review.py:

  - check_reinvention()         — CANONICAL-ARTIFACTS-REGISTRY-V1-01 (Layer 3 guard)
  - check_duration_derivation() — DURATION-DERIVATION-01 (§6 co-change BLOCK)

Plus the shared override-token plumbing (_has_override_token, _normalize_path) and
the fail-open loaders. These tests drive the check functions in isolation on
synthetic file lists — no git, no gh, no network.
"""

from __future__ import annotations

from scripts.ci import pr_governance_review as gov


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _registry():
    """A minimal synthetic canonical registry (subset of the real schema)."""
    return [
        {
            "concept_key": "pearl_news_sidebar",
            "canonical_path": "pearl_news/pipeline/assemble_v52.py",
            "sha_or_pr": "PR#853 8070e81fd",
            "owner_agent": "Pearl_News",
            "subsystem": "pearl_news",
            "edit_not_recreate": "YES",
            "last_verified": "2026-06-12",
            "supersedes": "-",
            "notes": "",
        },
        {
            "concept_key": "manga_brand_canon",
            "canonical_path": "config/manga/canonical_brand_list.yaml",
            "sha_or_pr": "PR#722 9205b2307",
            "owner_agent": "Pearl_Dev",
            "subsystem": "manga_pipeline",
            "edit_not_recreate": "NO-without-ratification",
            "last_verified": "2026-06-12",
            "supersedes": "-",
            "notes": "",
        },
        {
            "concept_key": "teacher_real_photos",
            "canonical_path": "teacher_pics/",  # directory canonical (trailing slash)
            "sha_or_pr": "c513ac18d",
            "owner_agent": "Pearl_Brand",
            "subsystem": "dashboard",
            "edit_not_recreate": "YES",
            "last_verified": "2026-06-12",
            "supersedes": "-",
            "notes": "",
        },
    ]


def _files(*pairs):
    """[(status, path), ...] → [{status, path}, ...]."""
    return [{"status": s, "path": p} for s, p in pairs]


# ---------------------------------------------------------------------------
# _normalize_path
# ---------------------------------------------------------------------------

def test_normalize_path_strips_dotslash_collapses_and_folds():
    assert gov._normalize_path("./Pearl_News//pipeline/Assemble_v52.py") == (
        "pearl_news/pipeline/assemble_v52.py"
    )


def test_normalize_path_strips_trailing_slash():
    assert gov._normalize_path("teacher_pics/") == "teacher_pics"


# ---------------------------------------------------------------------------
# _has_override_token
# ---------------------------------------------------------------------------

def test_has_override_token_requires_reason():
    assert gov._has_override_token("NEW-ARTIFACT-JUSTIFIED: real new capability", "NEW-ARTIFACT-JUSTIFIED")
    # bare token with no reason → not honored
    assert not gov._has_override_token("NEW-ARTIFACT-JUSTIFIED:", "NEW-ARTIFACT-JUSTIFIED")
    assert not gov._has_override_token("NEW-ARTIFACT-JUSTIFIED:   ", "NEW-ARTIFACT-JUSTIFIED")


def test_has_override_token_absent():
    assert not gov._has_override_token("nothing relevant here", "DURATION-DERIVATION-OK")
    assert not gov._has_override_token("", "DURATION-DERIVATION-OK")


def test_has_override_token_tolerates_bullet_and_whitespace():
    body = "Some PR body.\n  - DURATION-DERIVATION-OK: only added a compatible_structural_formats entry\n"
    assert gov._has_override_token(body, "DURATION-DERIVATION-OK")


# ---------------------------------------------------------------------------
# check_reinvention — fail-open
# ---------------------------------------------------------------------------

def test_reinvention_empty_registry_is_noop_pass():
    res = gov.check_reinvention(_files(("A", "anything/at/all.py")), registry=[], allowlist=set())
    assert res["check"] == "reinvention"
    assert res["status"] == "PASS"
    assert res["details"]["registry_rows"] == 0


def test_reinvention_no_added_files_passes():
    # Modifying the canonical in place is the CORRECT behavior → no WARN.
    res = gov.check_reinvention(
        _files(("M", "pearl_news/pipeline/assemble_v52.py")), _registry(), set()
    )
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# check_reinvention — path-match arms
# ---------------------------------------------------------------------------

def test_reinvention_exact_path_readd_warns():
    # Canonical path ADDED (e.g. deleted+re-added or duplicate landed) → WARN.
    res = gov.check_reinvention(
        _files(("A", "pearl_news/pipeline/assemble_v52.py")), _registry(), set()
    )
    assert res["status"] == "WARN"
    f = res["details"]["findings"][0]
    assert f["match_kind"] == "exact_path"
    assert f["canonical_path"] == "pearl_news/pipeline/assemble_v52.py"
    assert f["concept_key"] == "pearl_news_sidebar"


def test_reinvention_sibling_basename_fork_warns():
    # Same basename, different parent dir → likely fork → WARN.
    res = gov.check_reinvention(
        _files(("A", "pearl_news/v2/assemble_v52.py")), _registry(), set()
    )
    assert res["status"] == "WARN"
    f = res["details"]["findings"][0]
    assert f["match_kind"] == "sibling_basename"
    assert f["canonical_path"] == "pearl_news/pipeline/assemble_v52.py"


def test_reinvention_no_without_ratification_flagged_in_message():
    res = gov.check_reinvention(
        _files(("A", "config/manga/v2/canonical_brand_list.yaml")), _registry(), set()
    )
    assert res["status"] == "WARN"
    f = res["details"]["findings"][0]
    assert f["requires_ratification"] is True
    assert "ratification" in res["message"].lower()


def test_reinvention_no_false_positive_on_common_basename():
    # MATCH-ALGO: full normalized path, NOT bare basename. A brand-new README.md /
    # CANONICAL.txt anywhere must NOT collide with any canonical row.
    res = gov.check_reinvention(
        _files(("A", "some/new/module/README.md"), ("A", "another/CANONICAL.txt")),
        _registry(),
        set(),
    )
    assert res["status"] == "PASS"


def test_reinvention_unrelated_new_file_passes():
    res = gov.check_reinvention(
        _files(("A", "scripts/ci/brand_new_unrelated_tool.py")), _registry(), set()
    )
    assert res["status"] == "PASS"


def test_reinvention_directory_canonical_no_basename_arm():
    # teacher_pics/ is a directory canonical (no basename). A file with basename
    # 'teacher_pics' anywhere must NOT sibling-match it; only an exact-path add does.
    res = gov.check_reinvention(
        _files(("A", "unrelated/teacher_pics")), _registry(), set()
    )
    # 'unrelated/teacher_pics' normalizes differently from 'teacher_pics' → no match.
    assert res["status"] == "PASS"


def test_reinvention_directory_canonical_exact_add_warns():
    res = gov.check_reinvention(
        _files(("A", "teacher_pics/new_teacher.jpg")), _registry(), set()
    )
    # 'teacher_pics/new_teacher.jpg' != 'teacher_pics' → not an exact match either;
    # adding a FILE under the canonical dir is normal, not a fork → PASS.
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# check_reinvention — suppression (override + allowlist)
# ---------------------------------------------------------------------------

def test_reinvention_override_tag_downgrades_to_pass():
    res = gov.check_reinvention(
        _files(("A", "pearl_news/pipeline/assemble_v52.py")),
        _registry(),
        set(),
        override_text="NEW-ARTIFACT-JUSTIFIED: genuinely new sidebar variant, registry row added",
    )
    assert res["status"] == "PASS"
    assert res["details"]["override"] == "NEW-ARTIFACT-JUSTIFIED"
    # the candidate is still recorded for reviewer visibility
    assert res["details"]["justified"]


def test_reinvention_allowlist_skips_standing_mirror():
    # A standing allowlist entry for the colliding path suppresses the WARN.
    allow = {gov._normalize_path("pearl_news/pipeline/assemble_v52.py")}
    res = gov.check_reinvention(
        _files(("A", "pearl_news/pipeline/assemble_v52.py")), _registry(), allow
    )
    assert res["status"] == "PASS"


def test_reinvention_bare_override_without_reason_does_not_suppress():
    # A bare 'NEW-ARTIFACT-JUSTIFIED:' with no reason must NOT suppress the WARN.
    res = gov.check_reinvention(
        _files(("A", "pearl_news/pipeline/assemble_v52.py")),
        _registry(),
        set(),
        override_text="NEW-ARTIFACT-JUSTIFIED:",
    )
    assert res["status"] == "WARN"


def test_reinvention_multipath_row_each_mirror_matchable():
    # A registry row may carry ';'-joined mirrors; the guard must match either.
    # (load_canonical_registry expands them into separate rows; here we pass two
    # pre-expanded rows to assert check_reinvention treats each as a canonical.)
    reg = [
        {
            "concept_key": "teacher_real_photos",
            "canonical_path": "teacher_pics/",
            "owner_agent": "Pearl_Brand",
            "edit_not_recreate": "YES",
            "subsystem": "dashboard",
            "sha_or_pr": "c513ac18d",
            "last_verified": "2026-06-12",
            "supersedes": "-",
            "notes": "",
        },
        {
            "concept_key": "teacher_real_photos",
            "canonical_path": "brand-wizard-app/public/teacher_pics/",
            "owner_agent": "Pearl_Brand",
            "edit_not_recreate": "YES",
            "subsystem": "dashboard",
            "sha_or_pr": "c513ac18d",
            "last_verified": "2026-06-12",
            "supersedes": "-",
            "notes": "",
        },
    ]
    res = gov.check_reinvention(
        _files(("A", "brand-wizard-app/public/teacher_pics")), reg, set()
    )
    assert res["status"] == "WARN"
    assert res["details"]["findings"][0]["concept_key"] == "teacher_real_photos"


# ---------------------------------------------------------------------------
# check_duration_derivation
# ---------------------------------------------------------------------------

REG = "config/format_selection/format_registry.yaml"
SPEC = "docs/DURATION_DERIVATION_SPEC.md"


def test_duration_non_registry_pr_passes():
    res = gov.check_duration_derivation(_files(("M", "scripts/ci/something_else.py")))
    assert res["check"] == "duration_derivation"
    assert res["status"] == "PASS"
    assert res["details"]["registry_touched"] is False


def test_duration_cochange_passes():
    res = gov.check_duration_derivation(_files(("M", REG), ("M", SPEC)))
    assert res["status"] == "PASS"
    assert res["details"]["spec_touched"] is True


def test_duration_registry_without_spec_blocks():
    res = gov.check_duration_derivation(_files(("M", REG)))
    assert res["status"] == "BLOCKED"
    assert res["details"]["registry_touched"] is True
    assert res["details"]["spec_touched"] is False


def test_duration_added_registry_without_spec_blocks():
    # status 'A' (added) also triggers the guard, not just 'M'.
    res = gov.check_duration_derivation(_files(("A", REG)))
    assert res["status"] == "BLOCKED"


def test_duration_override_downgrades_block_to_warn():
    res = gov.check_duration_derivation(
        _files(("M", REG)),
        override_text="DURATION-DERIVATION-OK: only added a compatible_structural_formats entry, no word_range change",
    )
    assert res["status"] == "WARN"
    assert res["details"]["override"] == "DURATION-DERIVATION-OK"


def test_duration_bare_override_without_reason_still_blocks():
    res = gov.check_duration_derivation(
        _files(("M", REG)),
        override_text="DURATION-DERIVATION-OK:",
    )
    assert res["status"] == "BLOCKED"


def test_duration_cochange_wins_over_override():
    # If the spec is co-changed, that PASS takes precedence (override irrelevant).
    res = gov.check_duration_derivation(
        _files(("M", REG), ("M", SPEC)),
        override_text="DURATION-DERIVATION-OK: whatever",
    )
    assert res["status"] == "PASS"


# ---------------------------------------------------------------------------
# Integration: both checks registered and wired in main()
# ---------------------------------------------------------------------------

def test_both_checks_present_in_source():
    # Guard against accidental removal from the main() results list.
    import inspect

    src = inspect.getsource(gov.main)
    assert "check_reinvention(" in src
    assert "check_duration_derivation(" in src


def test_check_dicts_have_standard_shape():
    for res in (
        gov.check_reinvention(_files(("A", "x/y.py")), _registry(), set()),
        gov.check_duration_derivation(_files(("M", REG))),
    ):
        assert set(("check", "status", "message")).issubset(res.keys())
        assert res["status"] in ("PASS", "WARN", "BLOCKED")

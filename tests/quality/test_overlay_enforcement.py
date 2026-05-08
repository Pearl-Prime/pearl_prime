"""Phase 1 overlay enforcement for refrain allowlist (PER-CHAPTER_OVERLAY_ENFORCEMENT_V1)."""
from __future__ import annotations

from phoenix_v4.quality.book_quality_gate import _extract_chapters, _repeated_phrase_violations


def _book_12(mid_body: str | None = None, **chapter_bodies: str) -> tuple[str, list[str]]:
    chunks: list[str] = []
    for i in range(1, 13):
        body = chapter_bodies.get(f"c{i}") or chapter_bodies.get(str(i))
        if body is None and i >= 4 and i <= 8 and mid_body is not None:
            body = mid_body
        elif body is None:
            body = "neutral filler words that carry no motifs"
        chunks.append(f"Chapter {i}\n{body}\n")
    text = "".join(chunks)
    return text, _extract_chapters(text)


def test_rule_fired_book_wide_cap_when_default_cap_exceeded() -> None:
    noise = "aaa bbb ccc ddd"
    body = " ".join([noise] * 14)
    text = f"Chapter 1\n{body}\n"
    chs = _extract_chapters(text)
    violations = _repeated_phrase_violations(text, allowlist={}, chapter_texts=chs)
    assert violations
    top = violations[0]
    assert top["phrase"] == noise
    assert top["rule_fired"] == "book_wide_cap"
    assert top["rule"] == "book_wide_cap"
    assert all(v.get("rule_fired") != "overlay" for v in violations)


def test_density_ceiling_overlay_fire() -> None:
    motif = "alfa bravo charlie delta"
    chap1 = " ".join([motif, motif, motif])
    chap2 = "other unrelated words here"
    text = f"Chapter 1\n{chap1}\nChapter 2\n{chap2}\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 2,
            "classification": "test",
            "overlay_rule": "density_ceiling",
            "overlay_param": {"N": 2},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    ov = [v for v in violations if v.get("rule_fired") == "overlay"]
    assert len(ov) == 1
    assert ov[0]["overlay_rule_kind"] == "density_ceiling"
    assert ov[0]["chapter"] == 1
    assert ov[0]["count"] == 3
    assert ov[0]["rule"] == "overlay:density_ceiling"


def test_drift_detection_overlay_fire() -> None:
    motif = "one drift phrase cell"
    chap1 = " ".join([motif, motif, motif])
    text = f"Chapter 1\n{chap1}\nChapter 2\nquiet calm chapter without drift\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 2,
            "classification": "test",
            "overlay_rule": "drift_detection",
            "overlay_param": {"drift_threshold": 3},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    ov = [v for v in violations if v.get("rule_fired") == "overlay"]
    assert ov and ov[0]["overlay_rule_kind"] == "drift_detection"


def test_presence_floor_reports_absent_mid() -> None:
    motif = "spine refrain motif core"
    # Motif appears in chapter 1 and 9 only; mid band (ch 4–8) should miss it.
    text, chs = _book_12(
        mid_body="no motif in the middle chapters at all please",
        c1=f"opening carries {motif} once",
        c9=f"later tension returns with {motif}",
        c10="closing thoughts without motif",
    )
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 8,
            "classification": "test",
            "overlay_rule": "presence_floor",
            "overlay_param": {"structural_chapters": ["opening", "mid", "climax"]},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    mid_miss = [
        v
        for v in violations
        if v.get("rule_fired") == "overlay"
        and v.get("overlay_rule_kind") == "presence_floor"
        and v.get("structural_class") == "mid"
    ]
    assert mid_miss


def test_absence_guard_blocks_excluded_class() -> None:
    motif = "forbidden refrain token line"
    text = (
        f"Chapter 1\n{motif} appears in opening forbidden zone\n"
        "Chapter 2\nneutral words only here\n"
    )
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 5,
            "classification": "test",
            "overlay_rule": "absence_guard",
            "overlay_param": {"excluded_chapter_classes": ["opening"]},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    ag = [v for v in violations if v.get("overlay_rule_kind") == "absence_guard"]
    assert ag and ag[0]["chapter"] == 1
    assert ag[0]["excluded_class"] == "opening"


def test_compression_chapter_membership_via_hook() -> None:
    motif = "zip zap zop zoink"
    text = "Chapter 1\nplain filler\nChapter 2\n" + motif + " inside compression-like chapter\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 5,
            "classification": "test",
            "overlay_rule": "absence_guard",
            "overlay_param": {"excluded_chapter_classes": ["compression_chapters"]},
        }
    }
    violations = _repeated_phrase_violations(
        text,
        allowlist=alist,
        chapter_texts=chs,
        compression_chapters_1based={2},
    )
    ag = [v for v in violations if v.get("overlay_rule_kind") == "absence_guard"]
    assert ag and ag[0]["chapter"] == 2


def test_overlay_none_skips_structural_even_if_dense_per_chapter() -> None:
    motif = "dense none overlay rule motif"
    chap1 = " ".join([motif, motif, motif])
    text = f"Chapter 1\n{chap1}\nChapter 2\nneutral\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 2,
            "classification": "test",
            "overlay_rule": "none",
            "overlay_param": {},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    assert not any(v.get("rule_fired") == "overlay" for v in violations)


def test_composition_book_wide_cap_plus_overlay_in_one_manuscript() -> None:
    noise = "qqq www eee rrr"
    motif = "ttt yyy uuu iii"
    noisy_block = " ".join([noise] * 14)
    drift_block = " ".join([motif, motif, motif])
    text = f"Chapter 1\n{noisy_block} {drift_block}\nChapter 2\nquiet\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 120,
            "cap_per_chapter": 10,
            "classification": "test",
            "overlay_rule": "drift_detection",
            "overlay_param": {},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    bw = [v for v in violations if v["rule_fired"] == "book_wide_cap"]
    ov = [v for v in violations if v["rule_fired"] == "overlay"]
    assert bw and ov


def test_invalid_overlay_rule_string_falls_back_to_none() -> None:
    motif = "bad rule enum phrase here"
    chap1 = " ".join([motif, motif, motif])
    text = f"Chapter 1\n{chap1}\n"
    chs = _extract_chapters(text)
    alist = {
        motif: {
            "phrase": motif,
            "cap_book_wide": 80,
            "cap_per_chapter": 2,
            "classification": "test",
            "overlay_rule": "not_a_real_overlay_enum",
            "overlay_param": {"N": 2},
        }
    }
    violations = _repeated_phrase_violations(text, allowlist=alist, chapter_texts=chs)
    assert not any(v.get("rule_fired") == "overlay" for v in violations)

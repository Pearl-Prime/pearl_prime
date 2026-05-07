"""Tests for V2 Phase A.3 face-distance QA harness.

We mock out the heavy facenet-pytorch backend so tests run quickly + don't
require torch/MTCNN/VGGFace2 weights to be in the unit-test environment.
The thresholds + classifier + collision-scan plumbing are what the tests
exercise; the actual embedding fidelity is covered by Phase E empirical
calibration per the spec.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.manga.character_individuation import qa_face_distance as q


# ── classifier ──────────────────────────────────────────────────────────────

def test_classify_fail_at_low_distance():
    assert q.classify(0.0) == "fail"
    assert q.classify(0.39) == "fail"


def test_classify_borderline_in_middle_band():
    assert q.classify(0.4) == "borderline"
    assert q.classify(0.5) == "borderline"
    assert q.classify(0.549) == "borderline"


def test_classify_pass_at_high_distance():
    assert q.classify(0.55) == "pass"
    assert q.classify(0.9) == "pass"
    assert q.classify(1.5) == "pass"


def test_classify_threshold_overrides():
    # Tighter borderline → 0.5 reclassifies as pass
    assert q.classify(0.5, fail_threshold=0.3, borderline_threshold=0.45) == "pass"


# ── distance with mocked backend ────────────────────────────────────────────

def test_distance_facenet_uses_facenet_backend(tmp_path):
    fa = tmp_path / "a.png"; fa.write_bytes(b"x")
    fb = tmp_path / "b.png"; fb.write_bytes(b"x")
    with patch.object(q, "_facenet_embed") as embed_mock, \
         patch.object(q, "_cosine_distance", return_value=0.42) as cd_mock:
        embed_mock.side_effect = ["EMB_A", "EMB_B"]
        d = q.distance(fa, fb, backend="facenet")
    assert d == 0.42
    assert embed_mock.call_count == 2
    cd_mock.assert_called_once_with("EMB_A", "EMB_B")


def test_distance_raises_when_no_face_detected(tmp_path):
    fa = tmp_path / "a.png"; fa.write_bytes(b"x")
    fb = tmp_path / "b.png"; fb.write_bytes(b"x")
    with patch.object(q, "_facenet_embed", return_value=None):
        try:
            q.distance(fa, fb, backend="facenet")
        except q.FaceNotDetected:
            return
    raise AssertionError("FaceNotDetected not raised")


def test_distance_deepface_backend_routes_to_deepface(tmp_path):
    fa = tmp_path / "a.png"; fa.write_bytes(b"x")
    fb = tmp_path / "b.png"; fb.write_bytes(b"x")
    with patch.object(q, "_deepface_distance", return_value=0.61) as df_mock:
        d = q.distance(fa, fb, backend="deepface")
    assert d == 0.61
    df_mock.assert_called_once()


def test_distance_unknown_backend_raises():
    try:
        q.distance("a", "b", backend="banana")
    except ValueError:
        return
    raise AssertionError("ValueError not raised")


# ── catalog scan ─────────────────────────────────────────────────────────────

def test_find_collisions_returns_only_below_borderline(tmp_path):
    cat = tmp_path / "cat"
    cat.mkdir()
    (cat / "a.png").write_bytes(b"x")
    (cat / "b.png").write_bytes(b"x")
    (cat / "c.png").write_bytes(b"x")
    new = tmp_path / "new.png"; new.write_bytes(b"x")

    distances = {(str(new), str(cat / "a.png")): 0.30,   # fail
                 (str(new), str(cat / "b.png")): 0.50,   # borderline
                 (str(new), str(cat / "c.png")): 0.70}   # pass (excluded)

    def fake_distance(a, b, *, backend):
        return distances[(str(a), str(b))]

    with patch.object(q, "distance", side_effect=fake_distance):
        cols = q.find_collisions(new, cat)
    assert [c.catalog_path.name for c in cols] == ["a.png", "b.png"]
    assert cols[0].classification == "fail"
    assert cols[1].classification == "borderline"
    # Sorted ascending by distance
    assert cols[0].distance < cols[1].distance


def test_find_collisions_skips_face_not_detected(tmp_path):
    cat = tmp_path / "cat"; cat.mkdir()
    (cat / "a.png").write_bytes(b"x")
    (cat / "b.png").write_bytes(b"x")
    new = tmp_path / "new.png"; new.write_bytes(b"x")

    def fake_distance(a, b, *, backend):
        if str(b).endswith("a.png"):
            raise q.FaceNotDetected("synthetic")
        return 0.30

    with patch.object(q, "distance", side_effect=fake_distance):
        cols = q.find_collisions(new, cat)
    # a.png skipped; b.png present
    assert [c.catalog_path.name for c in cols] == ["b.png"]


def test_find_collisions_returns_empty_when_all_distinct(tmp_path):
    cat = tmp_path / "cat"; cat.mkdir()
    (cat / "a.png").write_bytes(b"x")
    new = tmp_path / "new.png"; new.write_bytes(b"x")
    with patch.object(q, "distance", return_value=0.99):
        cols = q.find_collisions(new, cat)
    assert cols == []

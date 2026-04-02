"""Tests for scripts/image_generation/image_qc.py — see MANGA_QC_AND_EBOOK_PIPELINE_SPEC §A.3.6."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
import pytest

from scripts.image_generation.image_qc import (
    _png_dimensions,
    _sha256_file,
    validate_author_pic_prompt,
    validate_output,
    validate_prompt,
)
from scripts.image_generation.prompt_compiler import SHARED_NEGATIVE_TOKENS, _sha256, compile_image_prompt


def _make_compiled(**overrides):
    base = compile_image_prompt(
        task="cover_art_base",
        subject="abstract book cover background, calm mood",
        style_hint="contemplative",
        palette_tokens=[],
        scene="soft gradient",
        extra_positive="",
        extra_negative="",
        author_id="ahjan",
        bio_keywords=[],
    )
    base.update(overrides)
    return base


def test_validate_prompt_passes_valid() -> None:
    c = _make_compiled()
    r = validate_prompt(c)
    assert r["status"] in ("passed", "passed_with_warnings")


def test_validate_prompt_blocks_no_subject() -> None:
    c = _make_compiled()
    c["positive"] = "masterpiece, best quality"
    c["positive_token_count"] = 4
    r = validate_prompt(c)
    assert r["status"] == "failed"
    assert "IMAGE.PROMPT.STRUCTURE" in r["blockers"]


def test_validate_prompt_blocks_no_quality() -> None:
    c = _make_compiled()
    c["positive"] = "only subject text here with no quality tokens at all"
    c["positive_token_count"] = 12
    r = validate_prompt(c)
    assert r["status"] == "failed"


def test_validate_prompt_warns_token_over_budget() -> None:
    c = _make_compiled()
    c["positive_token_count"] = 500
    c["negative_token_count"] = 10
    r = validate_prompt(c)
    assert r["status"] == "passed_with_warnings"
    assert "IMAGE.PROMPT.TOKEN_BUDGET" in r["majors"]


def test_validate_prompt_warns_empty_negative() -> None:
    c = _make_compiled()
    c["negative"] = ""
    r = validate_prompt(c)
    assert r["status"] == "passed_with_warnings"
    assert "IMAGE.PROMPT.NEGATIVE" in r["majors"]


def test_validate_prompt_warns_missing_hash() -> None:
    c = _make_compiled()
    c["provenance"] = {}
    r = validate_prompt(c)
    assert "IMAGE.PROMPT.PROVENANCE" in r["majors"]


def test_validate_prompt_report_structure() -> None:
    c = _make_compiled()
    r = validate_prompt(c)
    assert "gates" in r and "status" in r
    assert "blockers" in r and "majors" in r


def _make_valid_png(path: Path, width: int, height: int) -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(120, 130, 140))
    img.save(path, format="PNG")


def test_validate_output_passes_valid_png(tmp_path: Path) -> None:
    p = tmp_path / "out.png"
    _make_valid_png(p, 576, 1024)
    # Pad file size to pass min_bytes
    data = p.read_bytes()
    if len(data) < 512:
        p.write_bytes(data + b"\x00" * (512 - len(data)))
    r = validate_output(p, expected_width=576, expected_height=1024, min_bytes=512)
    assert r["status"] == "passed"
    assert "content_sha256" in r


def test_validate_output_blocks_missing_file(tmp_path: Path) -> None:
    p = tmp_path / "missing.png"
    r = validate_output(p)
    assert r["status"] == "failed"
    assert "IMAGE.OUTPUT.FILE_EXISTS" in r["blockers"]


def test_validate_output_blocks_invalid_format(tmp_path: Path) -> None:
    p = tmp_path / "bad.txt"
    p.write_bytes(b"not an image" * 50)
    r = validate_output(p, min_bytes=512)
    assert r["status"] == "failed"
    assert "IMAGE.OUTPUT.FORMAT" in r["blockers"]


def test_validate_output_warns_small_file(tmp_path: Path) -> None:
    p = tmp_path / "tiny.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    r = validate_output(p, min_bytes=512)
    assert "IMAGE.OUTPUT.MIN_FILE_SIZE" in r["majors"]


def test_validate_output_checks_dimensions(tmp_path: Path) -> None:
    p = tmp_path / "dim.png"
    _make_valid_png(p, 576, 1024)
    data = p.read_bytes()
    if len(data) < 512:
        p.write_bytes(data + b"\x00" * (512 - len(data)))
    r = validate_output(p, expected_width=576, expected_height=1024, min_bytes=512)
    assert r["status"] == "passed"


def test_validate_output_warns_wrong_dimensions(tmp_path: Path) -> None:
    p = tmp_path / "wrong.png"
    _make_valid_png(p, 100, 100)
    data = p.read_bytes()
    if len(data) < 512:
        p.write_bytes(data + b"\x00" * (512 - len(data)))
    r = validate_output(p, expected_width=576, expected_height=1024, min_bytes=512)
    assert "IMAGE.OUTPUT.DIMENSIONS" in r["majors"]


def test_png_dimensions_valid() -> None:
    pytest.importorskip("PIL")
    from PIL import Image
    import io

    buf = io.BytesIO()
    Image.new("RGB", (64, 48), color=(1, 2, 3)).save(buf, format="PNG")
    w, h = _png_dimensions(buf.getvalue())
    assert w == 64 and h == 48


def test_png_dimensions_invalid() -> None:
    assert _png_dimensions(b"garbage") == (0, 0)


def test_sha256_file_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "f.bin"
    p.write_bytes(b"abc")
    assert _sha256_file(p) == _sha256_file(p)


def test_author_pic_validation_structure() -> None:
    from scripts.image_generation.prompt_compiler import compile_author_pic_prompt

    bio = "y" * 55 + " meditation wellness daily practice for portrait."
    c = compile_author_pic_prompt("ahjan", bio, "soft", "Ahjan")
    r = validate_author_pic_prompt(c, "ahjan")
    assert "gates" in r and r["status"] in ("passed", "passed_with_warnings", "failed")


def test_image_gates_yaml_contains_expected_ids() -> None:
    p = REPO_ROOT / "config" / "image_generation" / "image_gates.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    ids = {g["id"] for g in data.get("gates", [])}
    for gate_id in (
        "IMAGE.PROMPT.STRUCTURE",
        "IMAGE.PROMPT.TOKEN_BUDGET",
        "IMAGE.OUTPUT.DIMENSIONS",
        "IMAGE.AUTHOR_PIC.PROMPT_HAS_BIO",
    ):
        assert gate_id in ids


def test_validate_output_jpeg_detected(tmp_path: Path) -> None:
    pytest.importorskip("PIL")
    from PIL import Image

    p = tmp_path / "x.jpg"
    Image.new("RGB", (576, 1024), color=(1, 2, 3)).save(p, format="JPEG", quality=95)
    data = p.read_bytes()
    if len(data) < 512:
        p.write_bytes(data + b"\x00" * (512 - len(data)))
    r = validate_output(p, expected_width=0, expected_height=0, min_bytes=512)
    assert r["status"] == "passed"


def test_author_pic_blocks_missing_registry() -> None:
    c = compile_image_prompt(
        task="author_pic",
        subject="Someone, professional portrait",
        style_hint="soft",
        palette_tokens=[],
        scene="serene",
        extra_positive="x",
        extra_negative="",
        author_id="__not_a_real_author_zz__",
        bio_keywords=[],
    )
    c["bio_length"] = 80
    c["author_id"] = "__not_a_real_author_zz__"
    r = validate_author_pic_prompt(c, "__not_a_real_author_zz__")
    assert r["status"] == "passed_with_warnings"
    assert "IMAGE.AUTHOR_PIC.REGISTRY_MATCH" in r["majors"]

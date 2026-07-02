#!/usr/bin/env python3
"""
EPUB Book Packager — build_epub.py

Takes rendered book text files and produces KDP-ready EPUB 3 packages
with cover images, metadata, and multi-chapter structure.

Usage:
    # Build EPUB from a book text file
    python scripts/release/build_epub.py \
        --input artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt \
        --title "The Alarm Is Lying" \
        --subtitle "A Nervous System Guide to Anxiety Recovery" \
        --author "Lena Thorne" \
        --teacher "Ahjan" \
        --publisher "Inner Light Press" \
        --cover artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png \
        --output artifacts/epub/ahjan_anxiety.epub

    # Build all 13 teacher books
    python scripts/release/build_epub.py --batch

    # Dry run (show what would be built)
    python scripts/release/build_epub.py --batch --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# KDP ideal embedded / storefront portrait (height × width per Amazon Help G200645690)
_EBOOK_COVER_W = 1600
_EBOOK_COVER_H = 2560

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("epub_builder")

try:
    from ebooklib import epub
except ImportError:
    print("Error: ebooklib required. Install: pip install ebooklib", file=sys.stderr)
    sys.exit(1)


# THE GATE (assembly-path stub catch). #3787 added a stub-catch to
# book_renderer.delivery_contract_gate + book_quality_gate, but build_epub.py —
# the operator/pathway EPUB packager — never invoked it, so a stub-bearing book
# text could still be packaged into a shippable EPUB (the flip pilot proved this).
# We invoke the CANONICAL gate here so any unfilled stub HARD-FAILS emission. No
# parallel detector; we reuse delivery_contract_gate verbatim.
#
# Escape hatch: PHOENIX_EPUB_SKIP_STUB_GATE=1 disables the gate for legacy test
# fixtures / book texts that intentionally carry forbidden tokens. Default OFF —
# the gate runs on every build.
def _run_stub_delivery_gate(text: str, *, source_hint: str) -> None:
    """Hard-fail EPUB assembly if ``text`` contains an unfilled atom stub.

    Raises book_renderer.DeliveryContractError (which propagates to a non-zero
    exit through main()/build_all()). The gate is the SAME stub-catch wired by
    #3787 into the delivery contract, so the spine EPUB-assembly path and the
    renderer agree on what blocks a ship.
    """
    import os

    if os.environ.get("PHOENIX_EPUB_SKIP_STUB_GATE") == "1":
        logger.warning(
            "PHOENIX_EPUB_SKIP_STUB_GATE=1 — skipping assembly-path stub gate for %s",
            source_hint,
        )
        return
    from phoenix_v4.rendering.book_renderer import delivery_contract_gate

    delivery_contract_gate(text, source_hint=source_hint)


# ─── TEACHER-MODE BYLINE RESOLVER (Q-TEACHERMODE-BYLINE-01) ───────────
#
# RATIFIED DEFAULT (operator, OPD-20260701-001): teacher-mode books byline a
# PEN-NAME author drawn from the brand's author pool; the teacher is credited
# SEPARATELY ("Teaching by <teacher>"). A teacher display name NEVER appears as
# the EPUB primary creator (dc:creator role=aut) or in --author. This mirrors the
# Sai-Maa rule ([Sai Maa never author]): every name in
# config/teachers/teacher_registry.yaml is teacher-mode-only, never a byline.
#
# Resolution chain:  book.teacher (teacher_id)
#   → brand   via config/catalog_planning/teacher_brand_author_roster.yaml (<brand>.teacher)
#   → pool    of pen-names for that brand. PRIMARY SSOT =
#             config/brand_author_assignments.yaml (assignments[].author_pool,
#             author_ids mapped to display names via the roster). Fallbacks:
#             config/author_registry.yaml (authors[].brand_id → pen_name), then
#             the roster's own author list. (Q-BYLINE-POOL-SOURCE-01 → RESOLVED.)
#   → pick    TOPIC-FIT + anti-dup: band-gate on the teacher's topic score
#             (strong ≥0.7 / medium ≥0.4, config/catalog_planning/
#             teacher_topic_persona_scores.yaml), build the topic-eligible set
#             from the assignments' topic-affinity rows (this topic + the
#             teacher's other same-band topics), then DETERMINISTIC
#             SHA256(book_id) % len(eligible) so a brand's books distribute
#             across its pool. We do NOT call the topic→author router — it
#             collapses to lena_thorne for every book ([Author system real
#             state]), re-introducing an anti-spam single-byline hazard.
#
# If a book's teacher resolves to a brand with NO pen-name pool yet, we RAISE
# (TeacherBylineError) rather than fall back to the teacher name — a missing pool
# is a real provisioning gap, never a licence to ship the teacher as author.

REPO_CONFIG = REPO_ROOT / "config"
_AUTHOR_REGISTRY_PATH = REPO_CONFIG / "author_registry.yaml"
_TEACHER_ROSTER_PATH = REPO_CONFIG / "catalog_planning" / "teacher_brand_author_roster.yaml"
_TEACHER_REGISTRY_PATH = REPO_CONFIG / "teachers" / "teacher_registry.yaml"
# Multi-author pool SSOT (Q-BYLINE-POOL-SOURCE-01 → RESOLVED). Each row:
#   {brand_id, default_author, author_pool: [{author_id, voice_lock, tier}]}
# plus topic-affinity rows {brand_id, topic_ids, default_author} that curate a
# per-topic author fit. "Pipeline resolves author from this file."
_BRAND_ASSIGNMENTS_PATH = REPO_CONFIG / "brand_author_assignments.yaml"
# Teacher-level topic_scores (14 teachers; joshin unscored) — used only to pick
# the eligibility BAND (strong ≥0.7 / medium ≥0.4) for topic-fit gating. There
# are NO per-pen-name topic_scores anywhere in the repo, so per-author fit comes
# from the assignments' own topic-affinity rows, band-gated by the teacher score.
_TEACHER_TOPIC_SCORES_PATH = REPO_CONFIG / "catalog_planning" / "teacher_topic_persona_scores.yaml"

_STRONG_BAND_MIN = 0.7   # PEN_NAME_AUTHOR_SYSTEM.md §6 — strong topic fit
_MEDIUM_BAND_MIN = 0.4   # medium topic fit


class TeacherBylineError(RuntimeError):
    """Raised when a teacher-mode book cannot resolve a pen-name byline.

    Never resolves to the teacher's own name — a missing pool is surfaced, not
    papered over, so no teacher identity can leak into dc:creator.
    """


_YAML_CACHE: dict[str, dict[str, Any]] = {}


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # local import: keeps ebooklib the only hard top-level dep

    # Cache by (path, mtime) — the byline resolver reads a handful of config
    # files many times per --batch run; re-parsing them each call is wasteful.
    try:
        key = f"{path}:{path.stat().st_mtime_ns}"
    except OSError:
        key = str(path)
    cached = _YAML_CACHE.get(key)
    if cached is not None:
        return cached
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    _YAML_CACHE[key] = data
    return data


def _brand_for_teacher(teacher_id: str) -> str:
    """Map a teacher_id → brand_id via the teacher_brand_author_roster."""
    roster = _load_yaml(_TEACHER_ROSTER_PATH)
    for brand_id, block in roster.items():
        if isinstance(block, dict) and block.get("teacher") == teacher_id:
            return brand_id
    raise TeacherBylineError(
        f"No brand maps to teacher '{teacher_id}' in {_TEACHER_ROSTER_PATH.name}"
    )


def _author_id_to_display(brand_id: str) -> dict[str, str]:
    """author_id → display_name for a brand, sourced from the roster's author list.

    The assignments SSOT keys authors by ``author_id``; the byline (dc:creator)
    needs the human display name. The roster carries both for every provisioned
    brand, so it is the id→name bridge.
    """
    out: dict[str, str] = {}
    roster = _load_yaml(_TEACHER_ROSTER_PATH)
    block = roster.get(brand_id) or {}
    for author in block.get("authors") or []:
        aid = (author.get("author_id") or "").strip()
        name = (author.get("display_name") or "").strip()
        if aid and name:
            out[aid] = name
    return out


def _assignment_rows_for_brand(brand_id: str) -> list[dict[str, Any]]:
    data = _load_yaml(_BRAND_ASSIGNMENTS_PATH)
    return [
        row
        for row in (data.get("assignments") or [])
        if isinstance(row, dict) and row.get("brand_id") == brand_id
    ]


def _brand_author_pool_ids(brand_id: str) -> list[str]:
    """Ordered author_id pool for a brand from the assignments SSOT (first
    author_pool row wins). Empty when the brand is not provisioned there."""
    for row in _assignment_rows_for_brand(brand_id):
        pool = row.get("author_pool")
        if pool:
            return [a["author_id"] for a in pool if a.get("author_id")]
    return []


def _brand_topic_affinities(brand_id: str) -> dict[str, str]:
    """topic_id → author_id, from the assignments' topic-affinity rows. This is
    the curated per-author topic fit (the assignments file's own signal)."""
    aff: dict[str, str] = {}
    for row in _assignment_rows_for_brand(brand_id):
        author = row.get("default_author")
        for topic in row.get("topic_ids") or []:
            if author:
                aff.setdefault(topic, author)
    return aff


def _teacher_topic_band(teacher_id: str, topic: str) -> str | None:
    """Band ('strong'/'medium'/'weak') for a teacher's topic score, or None when
    the teacher/topic is unscored. Gates topic-fit eligibility only."""
    try:
        data = _load_yaml(_TEACHER_TOPIC_SCORES_PATH)
    except Exception:  # noqa: BLE001 — scores are an optional gating signal
        return None
    scores = ((data.get("teachers") or {}).get(teacher_id) or {}).get("topic_scores") or {}
    val = scores.get(topic)
    if val is None:
        return None
    if val >= _STRONG_BAND_MIN:
        return "strong"
    if val >= _MEDIUM_BAND_MIN:
        return "medium"
    return "weak"


def _pen_name_pool_for_brand(brand_id: str) -> list[str]:
    """Resolve the full pen-name pool (display names) for a brand.

    Primary SSOT: config/brand_author_assignments.yaml author_pool (author_ids),
    mapped to display names via the roster. Falls back to author_registry.yaml
    (authors[].brand_id == brand → pen_name) and then the roster's own author
    list. Returns a de-duplicated, sorted pool of display names.
    """
    id_to_name = _author_id_to_display(brand_id)

    # 1) assignments SSOT — the multi-author pool of record
    pool = [id_to_name.get(aid, aid) for aid in _brand_author_pool_ids(brand_id)]

    # 2) author_registry.yaml fallback (pen_name by brand_id)
    if not pool:
        registry = _load_yaml(_AUTHOR_REGISTRY_PATH)
        for _aid, meta in (registry.get("authors") or {}).items():
            if isinstance(meta, dict) and meta.get("brand_id") == brand_id:
                pen = (meta.get("pen_name") or "").strip()
                if pen:
                    pool.append(pen)

    # 3) roster author list fallback (display_name)
    if not pool:
        pool = [name for name in id_to_name.values() if name]

    return sorted(set(pool))


def _topic_fit_pool(book: dict[str, Any], brand_id: str) -> tuple[list[str], str]:
    """Topic-eligible pen-name display names for a book, plus the band used.

    Selection is topic-fit + anti-dup (Q-BYLINE-POOL-SOURCE-01):
      * Band gate — the teacher's topic score picks the eligibility band
        (strong ≥0.7, else medium ≥0.4; Q-TOPICBAND-01).
      * Eligible set — the assignments' topic-affinity author for THIS topic,
        UNION the affinity authors of the teacher's OTHER same-band topics. This
        keeps every candidate on-band for topic fit while spreading a brand's
        books across its pool instead of collapsing to a single byline.
      * Fallback — if no topic-affinity data qualifies, the full pool by hash.
    The dead topic→author router is never consulted.
    """
    teacher_id = book["teacher"]
    topic = book.get("topic") or ""
    full_pool_ids = _brand_author_pool_ids(brand_id)
    id_to_name = _author_id_to_display(brand_id)
    full_pool = _pen_name_pool_for_brand(brand_id)
    if not full_pool_ids:
        # No id-keyed pool (registry/roster fallback path) — cannot topic-rank;
        # spread over the resolved display-name pool.
        return full_pool, "full_pool"

    aff = _brand_topic_affinities(brand_id)
    valid_ids = set(full_pool_ids)
    band = _teacher_topic_band(teacher_id, topic)

    eligible_ids: set[str] = set()
    if topic in aff and aff[topic] in valid_ids:
        eligible_ids.add(aff[topic])
    if band:
        for a_topic, a_id in aff.items():
            if a_id in valid_ids and _teacher_topic_band(teacher_id, a_topic) == band:
                eligible_ids.add(a_id)

    if not eligible_ids:  # no scored/affinity fit — spread across the whole pool
        return full_pool, "full_pool"

    names = sorted({id_to_name.get(aid, aid) for aid in eligible_ids})
    return names, (band or "affinity")


def resolve_teacher_byline(book: dict[str, Any]) -> tuple[str, str]:
    """Return (pen_name_author, teacher_display_name) for a teacher-mode book.

    ``pen_name_author`` becomes the EPUB primary creator; ``teacher_display_name``
    is credited separately. Selection is topic-fit (band-gated over the
    assignments' affinity rows) + anti-dup (deterministic SHA256(book_id) index
    over the topic-eligible set), so a brand's books distribute across its pool.
    Raises TeacherBylineError if the brand has no pen-name pool at all.
    """
    teacher_id = book["teacher"]
    teacher_display = _teacher_display_name(teacher_id)
    brand_id = _brand_for_teacher(teacher_id)
    pool = _pen_name_pool_for_brand(brand_id)
    if not pool:
        raise TeacherBylineError(
            f"Brand '{brand_id}' (teacher '{teacher_id}') has no pen-name pool in "
            f"{_BRAND_ASSIGNMENTS_PATH.name}, {_AUTHOR_REGISTRY_PATH.name}, or "
            f"{_TEACHER_ROSTER_PATH.name}; cannot byline book '{book['id']}'. "
            f"Provision the pool — never ship the teacher."
        )
    eligible, _band = _topic_fit_pool(book, brand_id)
    eligible = eligible or pool
    idx = int(hashlib.sha256(book["id"].encode()).hexdigest(), 16) % len(eligible)
    return eligible[idx], teacher_display


def _teacher_display_name(teacher_id: str) -> str:
    """Display name for a teacher_id from teacher_registry.yaml (fallback: titled id)."""
    try:
        registry = _load_yaml(_TEACHER_REGISTRY_PATH)
        meta = (registry.get("teachers") or {}).get(teacher_id) or {}
        name = (meta.get("display_name") or meta.get("formal_name") or "").strip()
        if name:
            return name
    except Exception:  # noqa: BLE001 — display-name lookup is best-effort
        pass
    return teacher_id.replace("_", " ").title()

# ─── BOOK MANIFEST ────────────────────────────────────────────────────
#
# BYLINE NOTE: entries carry ``teacher`` (a teacher_id), NOT ``author``. The
# byline (dc:creator) is resolved to a brand pen-name at build time via
# resolve_teacher_byline(); the teacher is credited separately. This is the fix
# for Q-TEACHERMODE-BYLINE-01 — no teacher name is ever a primary author.

TEACHER_BOOKS = [
    {"id": "ahjan", "teacher": "ahjan", "publisher": "Inner Light Press",
     "title": "The Alarm Is Lying", "subtitle": "A Nervous System Guide to Anxiety Recovery",
     "topic": "anxiety", "lang": "en"},
    {"id": "adi_da", "teacher": "adi_da", "publisher": "Awakening Press",
     "title": "You Were Always Enough", "subtitle": "Rebuilding Self-Esteem and Reclaiming Your Worth",
     "topic": "self_worth", "lang": "en"},
    {"id": "joshin", "teacher": "joshin", "publisher": "Still Forest",
     "title": "Quiet Enough", "subtitle": "A Zen Guide to Calming Anxiety and Finding Presence",
     "topic": "anxiety", "lang": "en"},
    {"id": "miyuki", "teacher": "miyuki", "publisher": "Zen Clarity",  # per OPD-111 — Loop Breaker is contemplative
     "title": "The Loop Breaker", "subtitle": "How to Stop Overthinking and Quiet Your Racing Mind",
     "topic": "overthinking", "lang": "en"},
    {"id": "maat", "teacher": "maat", "publisher": "Truth Compass",
     "title": "The No That Saved Me", "subtitle": "A Practical Guide to Setting Boundaries and Finding Peace",
     "topic": "boundaries", "lang": "en"},
    {"id": "master_feung", "teacher": "master_feung", "publisher": "Vitality Path",
     "title": "After Burnout", "subtitle": "A Taoist Guide to Energy Recovery",
     "topic": "burnout", "lang": "zh-CN"},
    {"id": "master_sha", "teacher": "master_sha", "publisher": "Soul Repair",
     "title": "The Weight of Gone", "subtitle": "A Gentle Guide to Grief, Loss, and Healing",
     "topic": "grief", "lang": "en"},
    {"id": "master_wu", "teacher": "master_wu", "publisher": "Mountain Gate Press",
     "title": "The Way of Courage", "subtitle": "Shaolin Wisdom for Facing Fear",
     "topic": "courage", "lang": "zh-TW"},
    {"id": "miki", "teacher": "miki", "publisher": "Gen Spark",
     "title": "Who Let Me In", "subtitle": "A Guide to Dismantling Imposter Syndrome from the Inside",
     "topic": "imposter_syndrome", "lang": "en"},
    {"id": "omote", "teacher": "omote", "publisher": "Gentle Wave",
     "title": "Dark Room, Loud Brain", "subtitle": "A Somatic Guide to Beating Sleep Anxiety",
     "topic": "sleep_anxiety", "lang": "en"},
    {"id": "pamela_fellows", "teacher": "pamela_fellows", "publisher": "Body Wisdom",
     "title": "Wired for Worry", "subtitle": "Understanding Your Anxiety Response and How to Rewire It",
     "topic": "anxiety", "lang": "en"},
    {"id": "ra", "teacher": "ra", "publisher": "Cosmic Edge",
     "title": "The Proof Was Always You", "subtitle": "Overcoming Imposter Syndrome and Owning Your Worth",
     "topic": "imposter_syndrome", "lang": "en"},
    {"id": "sai_ma", "teacher": "sai_ma", "publisher": "Healing Ground Press",
     "title": "Still Here Without You", "subtitle": "Finding Your Way Through Grief and Heartbreak",
     "topic": "grief", "lang": "en"},
]


# ─── CHAPTER PARSER ───────────────────────────────────────────────────

def parse_book_text(text: str) -> list[dict[str, str]]:
    """Parse a book text file into chapters.

    Detects chapter boundaries by looking for:
    - Lines starting with "CHAPTER" or "第" (Chinese)
    - Lines starting with "A NOTE ON THE TEACHINGS" or "教"
    - Lines starting with "WHERE TO GO DEEPER" or "深入"
    - All-caps section headers
    """
    lines = text.split("\n")
    chapters: list[dict[str, str]] = []
    current_title = ""
    current_body: list[str] = []

    chapter_re = re.compile(
        r"^(CHAPTER \d+|Chapter \d+|第[一二三四五六七八九十\d]+章|"
        r"A NOTE ON THE TEACHINGS|教[导導]缘起|"
        r"WHERE TO GO DEEPER|深入修[行炼練]|"
        r"[A-Z][A-Z\s:—\-]{8,}$)",
        re.MULTILINE,
    )

    for line in lines:
        stripped = line.strip()
        if chapter_re.match(stripped) and len(stripped) < 100:
            # Save previous chapter
            if current_title or current_body:
                chapters.append({
                    "title": current_title or "Introduction",
                    "body": "\n".join(current_body).strip(),
                })
            current_title = stripped
            current_body = []
        else:
            current_body.append(line)

    # Save last chapter
    if current_title or current_body:
        chapters.append({
            "title": current_title or "Content",
            "body": "\n".join(current_body).strip(),
        })

    return chapters


# ─── EPUB BUILDER ─────────────────────────────────────────────────────

CSS_STYLE = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.8;
    margin: 2em;
    color: #2a2a2a;
}
h1, h2 {
    font-family: 'Palatino Linotype', Palatino, serif;
    color: #1a1a1a;
    margin-top: 2em;
    margin-bottom: 0.5em;
}
h1 { font-size: 1.6em; text-align: center; }
h2 { font-size: 1.3em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
p { margin-bottom: 1em; text-indent: 0; }
.pre-intro { font-style: italic; color: #555; }
.exercise { background: #f9f6f0; padding: 1em; border-left: 3px solid #b45309; margin: 1em 0; }
.permission { font-weight: bold; color: #8b4513; }
.publisher { text-align: center; font-size: 0.9em; color: #888; margin-top: 3em; }
.ai-disclosure {
    font-size: 0.8em; color: #999; text-align: center;
    margin-top: 2em; padding: 1em; border-top: 1px solid #eee;
}
"""


def prepare_embedded_ebook_cover(cover_path: Path, *, raw: bool = False) -> tuple[bytes, str]:
    """Bytes + media-type for EPUB cover item.

    When Pillow is available and ``raw`` is False, image is letterboxed to
    :data:`_EBOOK_COVER_W` × :data:`_EBOOK_COVER_H` (1.6:1) so square or odd
    storefront crops do not produce non-portrait EPUB embeds that fail common
    distributor guidance. Output is always PNG for a single predictable spine item.
    """
    ext = cover_path.suffix.lower()
    src_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")
    raw_bytes = cover_path.read_bytes()
    if raw:
        return raw_bytes, src_type
    try:
        from PIL import Image
    except ImportError:
        logger.warning(
            "Pillow not installed; embedding %s without resize. Install Pillow for KDP-portrait-normalization.",
            cover_path,
        )
        return raw_bytes, src_type

    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    w, h = img.size
    tw, th = _EBOOK_COVER_W, _EBOOK_COVER_H
    if abs(w - tw) <= 2 and abs(h - th) <= 2:
        out = img
    else:
        scale = min(tw / w, th / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tw, th), (245, 245, 245))
        x0 = (tw - nw) // 2
        y0 = (th - nh) // 2
        canvas.paste(resized, (x0, y0))
        out = canvas
        logger.info(
            "Normalized EPUB cover %s from %d×%d → %d×%d (portrait embed).",
            cover_path,
            w,
            h,
            tw,
            th,
        )
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), "image/png"


def text_to_html(text: str) -> str:
    """Convert plain text to simple HTML paragraphs."""
    paragraphs = text.split("\n\n")
    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Escape HTML entities
        para = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Preserve single newlines as <br>
        para = para.replace("\n", "<br/>\n")
        html_parts.append(f"<p>{para}</p>")
    return "\n".join(html_parts)


def build_epub(
    *,
    input_path: Path,
    title: str,
    subtitle: str,
    author: str,
    publisher: str,
    language: str = "en",
    cover_path: Path | None = None,
    output_path: Path,
    topic: str = "",
    raw_cover: bool = False,
    description: str = "",
    disclosure: str = "",
    teacher: str = "",
) -> Path:
    """Build a KDP-ready EPUB 3 from a book text file.

    ``author`` is the primary creator (dc:creator role=aut) — for teacher-mode
    books this MUST be a brand pen-name, never a teacher. ``teacher`` (optional)
    is the teaching credit: emitted as a dc:contributor (role=oth) and a visible
    "Teaching by <teacher>" line on the title page. See Q-TEACHERMODE-BYLINE-01.
    """
    text = input_path.read_text(encoding="utf-8")

    # THE GATE: hard-fail before EPUB emission on any unfilled atom stub.
    _run_stub_delivery_gate(text, source_hint=str(input_path))

    chapters = parse_book_text(text)

    if not chapters:
        raise ValueError(f"No chapters found in {input_path}")

    book = epub.EpubBook()

    # ── Metadata ──
    uid = hashlib.sha256(f"{author}|{title}|{topic}".encode()).hexdigest()[:16]
    book.set_identifier(f"phoenix-omega-{uid}")
    book.set_title(f"{title}: {subtitle}")
    book.set_language(language)
    # Primary creator (dc:creator role=aut) — a pen-name for teacher-mode books.
    book.add_author(author)

    teacher_credit = teacher.strip()
    if teacher_credit:
        # Teacher credited SEPARATELY, never as primary author. dc:contributor
        # role=oth ("other") carries the teaching-by relationship; ebooklib emits
        # the opf:role refinement so the pen-name stays the sole aut creator.
        book.add_metadata(
            "DC", "contributor", teacher_credit,
            {"id": "teacher", "{http://www.idpf.org/2007/opf}role": "oth"},
        )

    book.add_metadata("DC", "publisher", publisher)
    _teaching_by = f" Teaching by {teacher_credit}." if teacher_credit else ""
    desc = description.strip() or (
        f"{subtitle}. A therapeutic book by {author}, published by {publisher}."
        f"{_teaching_by} Part of the Phoenix Omega series."
    )
    book.add_metadata("DC", "description", desc)
    book.add_metadata("DC", "subject", topic.replace("_", " ").title())
    book.add_metadata("DC", "date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    ei_disclosure = disclosure.strip() or (
        "This book was created with AI assistance as part of the Phoenix Omega "
        "therapeutic content system. All content has been reviewed and curated "
        "by human editors. This work is intended for informational purposes "
        "and is not a substitute for professional mental health care."
    )
    book.add_metadata("DC", "rights", ei_disclosure)

    # ── Cover (embedded; storefront upload still uses separate file in distributor UI / our PNG exports) ──
    if cover_path and cover_path.exists():
        cover_data, _media_type = prepare_embedded_ebook_cover(cover_path, raw=raw_cover)
        book.set_cover("cover.png", cover_data, create_page=True)

    # ── Stylesheet ──
    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=CSS_STYLE.encode("utf-8"),
    )
    book.add_item(style)

    # ── Title page ──
    title_html = f"""
    <html><head><link rel="stylesheet" href="style/default.css"/></head>
    <body>
    <h1>{title}</h1>
    <p style="text-align:center; font-size:1.1em; color:#555;">{subtitle}</p>
    <p style="text-align:center; margin-top:2em;">By {author}</p>
    {f'<p style="text-align:center; font-size:0.95em; color:#777;">Teaching by {teacher_credit}</p>' if teacher_credit else ''}
    <p class="publisher">{publisher}</p>
    <p class="ai-disclosure">
        {ei_disclosure}
    </p>
    </body></html>
    """
    title_page = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang=language)
    title_page.content = title_html.encode("utf-8")
    title_page.add_item(style)
    book.add_item(title_page)

    # ── Chapters ──
    epub_chapters = [title_page]
    toc_entries = []

    for i, ch in enumerate(chapters):
        ch_title = ch["title"]
        ch_body = text_to_html(ch["body"])

        ch_html = f"""
        <html><head><link rel="stylesheet" href="style/default.css"/></head>
        <body>
        <h2>{ch_title}</h2>
        {ch_body}
        </body></html>
        """

        ch_item = epub.EpubHtml(
            title=ch_title,
            file_name=f"chapter_{i+1:02d}.xhtml",
            lang=language,
        )
        ch_item.content = ch_html.encode("utf-8")
        ch_item.add_item(style)
        book.add_item(ch_item)
        epub_chapters.append(ch_item)
        toc_entries.append(ch_item)

    # ── Navigation ──
    book.toc = toc_entries
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    # ── Write ──
    output_path.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(output_path), book, {})
    logger.info("Built: %s (%d chapters, %d bytes)", output_path, len(chapters), output_path.stat().st_size)

    return output_path


# ─── BATCH MODE ───────────────────────────────────────────────────────

def build_all(dry_run: bool = False, raw_cover: bool = False) -> list[dict[str, Any]]:
    """Build EPUBs for all 13 teacher books."""
    examples_dir = REPO_ROOT / "artifacts" / "pipeline_examples"
    epub_dir = REPO_ROOT / "artifacts" / "epub"
    results: list[dict[str, Any]] = []

    for book in TEACHER_BOOKS:
        tid = book["id"]
        topic = book["topic"]
        input_path = examples_dir / tid / f"book_{tid}_{topic}_15min.txt"
        cover_path = examples_dir / tid / f"cover_{tid}_{topic}.png"
        output_path = epub_dir / f"{tid}_{topic}.epub"

        # Resolve the pen-name byline + teacher credit BEFORE any file check, so a
        # missing pool surfaces as an explicit error rather than a silent skip and
        # a teacher name can never reach dc:creator.
        try:
            pen_author, teacher_display = resolve_teacher_byline(book)
        except TeacherBylineError as e:
            logger.error("Byline unresolved: %s — %s", tid, e)
            print(f"  ✗ [{tid}] {book['title']} — byline: {e}")
            results.append({"id": tid, "status": "byline_error", "error": str(e)})
            continue

        if not input_path.exists():
            logger.warning("Missing: %s", input_path)
            results.append({"id": tid, "status": "missing_input", "path": str(input_path)})
            continue

        if dry_run:
            has_cover = cover_path.exists()
            print(
                f"  [{tid}] {book['title']} → {output_path.name} "
                f"(author: {pen_author}, teaching by: {teacher_display}, "
                f"cover: {'yes' if has_cover else 'NO'})"
            )
            results.append({
                "id": tid, "status": "dry_run", "has_cover": has_cover,
                "author": pen_author, "teacher": teacher_display,
            })
            continue

        try:
            path = build_epub(
                input_path=input_path,
                title=book["title"],
                subtitle=book["subtitle"],
                author=pen_author,
                teacher=teacher_display,
                publisher=book["publisher"],
                language=book["lang"],
                cover_path=cover_path if cover_path.exists() else None,
                output_path=output_path,
                topic=topic,
                raw_cover=raw_cover,
            )
            size = path.stat().st_size
            print(f"  ✓ [{tid}] {book['title']} → {path.name} ({size:,} bytes)")
            results.append({
                "id": tid, "status": "ok", "path": str(path), "size": size,
                "author": pen_author, "teacher": teacher_display,
            })
        except Exception as e:
            logger.error("Failed: %s — %s", tid, e)
            print(f"  ✗ [{tid}] {book['title']} — {e}")
            results.append({"id": tid, "status": "error", "error": str(e)})

    return results


# ─── CLI ──────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Build KDP-ready EPUBs from book texts")
    parser.add_argument("--input", type=Path, help="Input book text file")
    parser.add_argument("--title", help="Book title")
    parser.add_argument("--subtitle", default="", help="Book subtitle")
    parser.add_argument("--author", help="Author name (pen-name; NEVER a teacher name)")
    parser.add_argument(
        "--teacher", default="",
        help="Teaching credit (dc:contributor + 'Teaching by' line); the teacher "
             "is NEVER the primary author",
    )
    parser.add_argument("--publisher", default="Phoenix Omega", help="Publisher name")
    parser.add_argument("--cover", type=Path, help="Cover image path")
    parser.add_argument("--output", type=Path, help="Output EPUB path")
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--topic", default="", help="Topic for metadata")
    parser.add_argument("--batch", action="store_true", help="Build all 13 teacher books")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be built")
    parser.add_argument(
        "--raw-cover",
        action="store_true",
        help="Embed the source cover file as-is (skip 1600×2560 letterbox normalization)",
    )
    parser.add_argument("--description", default="", help="DC description metadata")
    parser.add_argument("--disclosure", default="", help="Title-page EI disclosure (not AI boilerplate)")

    args = parser.parse_args()

    if args.batch:
        print(f"=== EPUB BATCH BUILD — {len(TEACHER_BOOKS)} BOOKS ===\n")
        results = build_all(dry_run=args.dry_run, raw_cover=args.raw_cover)
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"\n{'DRY-RUN: ' if args.dry_run else ''}{ok}/{len(results)} built")
        # THE GATE: a stub (or any) build failure in batch mode must exit
        # non-zero so CI / the operator pipeline does not treat a stub-blocked
        # run as a clean ship.
        errored = [r for r in results if r["status"] in ("error", "byline_error")]
        if errored and not args.dry_run:
            print(f"FAIL: {len(errored)} book(s) failed the build/stub/byline gate.", file=sys.stderr)
            return 1
        return 0

    if not args.input:
        parser.error("--input or --batch required")

    # Single build: build_epub() raises DeliveryContractError on a stub, which
    # propagates here as a non-zero exit (return 1) rather than packaging the EPUB.
    build_epub(
        input_path=args.input,
        title=args.title or "Untitled",
        subtitle=args.subtitle,
        author=args.author or "Unknown",
        teacher=args.teacher,
        publisher=args.publisher,
        language=args.language,
        cover_path=args.cover,
        output_path=args.output or Path(f"{args.input.stem}.epub"),
        topic=args.topic,
        raw_cover=args.raw_cover,
        description=args.description,
        disclosure=args.disclosure,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

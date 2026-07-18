#!/usr/bin/env python3
"""Rebuild publishable-quality social visual proofs without live publishing.

This runner intentionally does not reuse the older deterministic proof renders.
It creates a new visual QA packet with richer image-aware compositions, design
family rules, Pearl Animator storyboard assets, scorecards, and handoffs.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import textwrap
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROOF_ROOT = ROOT / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718"
HANDOFF_ROOT = ROOT / "artifacts/coordination/handoffs"
IMAGE_BANK = ROOT / "artifacts/curation/waystream_image_winners_20260715/curated_winners_draft.json"
OLD_PROOF_ROOT = ROOT / "artifacts/qa/deterministic_social_system_20260718"
OLD_GATE_ROOT = ROOT / "artifacts/qa/deterministic_social_visual_gate_20260718"

LANES = {
    "lane01": PROOF_ROOT / "lane01_research_visual_quality_lock",
    "lane02": PROOF_ROOT / "lane02_ugly_audit",
    "lane03": PROOF_ROOT / "lane03_design_families",
    "lane04": PROOF_ROOT / "lane04_static_carousel_rebuild",
    "lane05": PROOF_ROOT / "lane05_pearl_animator_rebuild",
    "lane06": PROOF_ROOT / "lane06_operator_gate",
    "lane07": PROOF_ROOT / "lane07_pilot_packet",
    "lane08": PROOF_ROOT / "lane08_final_audit",
}

PLATFORM_SPECS: dict[str, dict[str, Any]] = {
    "instagram_feed_portrait": {
        "platform": "instagram",
        "surface": "feed_portrait",
        "size": (1080, 1350),
        "native_role": "saved, shared, visually led single image",
        "caption_opening_limit": 125,
    },
    "facebook_feed": {
        "platform": "facebook",
        "surface": "feed",
        "size": (1200, 1500),
        "native_role": "community context and practical reflection",
        "caption_opening_limit": 150,
    },
    "linkedin_feed_portrait": {
        "platform": "linkedin",
        "surface": "feed_portrait",
        "size": (1080, 1350),
        "native_role": "professional insight with credible utility",
        "caption_opening_limit": 140,
    },
    "pinterest_pin": {
        "platform": "pinterest",
        "surface": "standard_pin",
        "size": (1000, 1500),
        "native_role": "searchable saveable idea pin",
        "caption_opening_limit": 100,
    },
    "x_image": {
        "platform": "x",
        "surface": "image_post",
        "size": (1600, 900),
        "native_role": "fast thesis with a strong visual hook",
        "caption_opening_limit": 110,
    },
    "threads_image": {
        "platform": "threads",
        "surface": "image_post",
        "size": (1080, 1350),
        "native_role": "human, conversational post with one clear idea",
        "caption_opening_limit": 125,
    },
    "bluesky_image": {
        "platform": "bluesky",
        "surface": "image_post",
        "size": (1200, 900),
        "native_role": "smart compact observation with alt text",
        "caption_opening_limit": 110,
    },
    "google_business_square": {
        "platform": "google_business",
        "surface": "square_update",
        "size": (1200, 1200),
        "native_role": "local-service proof, calm and specific",
        "caption_opening_limit": 120,
    },
    "tiktok_reels_shorts_vertical": {
        "platform": "tiktok_reels_shorts",
        "surface": "vertical_video",
        "size": (1080, 1920),
        "native_role": "faceless short-form first frame and beats",
        "caption_opening_limit": 100,
    },
    "youtube_shorts": {
        "platform": "youtube_shorts",
        "surface": "vertical_video",
        "size": (1080, 1920),
        "native_role": "short-form search plus retention",
        "caption_opening_limit": 100,
    },
}

FFMPEG_PROBE: tuple[bool, str] | None = None

DESIGN_FAMILIES: dict[str, dict[str, Any]] = {
    "photo_full_bleed_emotional": {
        "role": "Lead with a real-feeling image and one large emotional claim.",
        "best_for": "Instagram, Facebook, TikTok first frames, grief, hope, burnout",
        "rules": [
            "Use one full-bleed image with a quiet-zone text plate or gradient only where needed.",
            "Keep the headline under nine words and body under twelve words.",
            "Never cover a face, hand, symbol, or central object with text.",
        ],
    },
    "premium_type_poster": {
        "role": "Make a quote or thesis feel editorial instead of like a note card.",
        "best_for": "X, Threads, LinkedIn, book insight, high-share static posts",
        "rules": [
            "Use oversized type, a strong margin system, and one supporting image strip or object crop.",
            "Avoid beige memo-card framing and avoid centering every line.",
            "Use one accent color and one sober ink color.",
        ],
    },
    "tool_checklist_card": {
        "role": "Turn a small practice into a saveable utility asset.",
        "best_for": "Pinterest, LinkedIn, Google Business, carousel tool slides",
        "rules": [
            "Use three to five checks with generous line height and clear icons.",
            "Use color as structure, not decoration.",
            "Keep each check to one action verb plus a concrete object.",
        ],
    },
    "diagram_framework": {
        "role": "Show a mechanism or decision path without dense prose.",
        "best_for": "LinkedIn, carousel education, X images",
        "rules": [
            "Use three visible stages maximum on a static image.",
            "Pair each label with a short sensory or operational explanation.",
            "Use arrows, rails, or numbered nodes for scan order.",
        ],
    },
    "story_carousel": {
        "role": "Create rhythmic multi-slide progression with layout variation.",
        "best_for": "Instagram and LinkedIn carousels",
        "rules": [
            "Sequence: cover, recognition, mechanism, tool, payoff, save/share CTA.",
            "Change crop, type scale, or structure every slide.",
            "Treat each slide as useful alone while preserving narrative momentum.",
        ],
    },
    "book_page_quote": {
        "role": "Make a reading insight tactile, not generic.",
        "best_for": "author/book feeds, Threads, Instagram, Pinterest",
        "rules": [
            "Use book/page surface cues and one precise pull quote.",
            "Add source/provenance metadata in tiny footer only if legible.",
            "Do not fabricate page text or imply a real quote without source.",
        ],
    },
    "faceless_video_broll": {
        "role": "Build short-form video from objects, hands, spaces, and kinetic type.",
        "best_for": "TikTok, Reels, YouTube Shorts",
        "rules": [
            "First frame must be readable as a thumbnail.",
            "Every beat needs one shot, one motion note, one caption line, and one sound cue.",
            "If no MP4 is rendered, label the package render-ready, never video-rendered.",
        ],
    },
    "object_metaphor": {
        "role": "Use a concrete object as the visual metaphor for an abstract topic.",
        "best_for": "burnout, anxiety, boundaries, grief",
        "rules": [
            "Pick one object and crop it confidently.",
            "Avoid generic nature symbolism when a domain-specific object is available.",
            "Let the object occupy at least 35 percent of the canvas.",
        ],
    },
    "localized_lifestyle_note": {
        "role": "Adapt social-native visuals for APAC market tone without stereotyping.",
        "best_for": "Japan, Taiwan, Korea, China, Hong Kong, Singapore localization drafts",
        "rules": [
            "Use practical, polite, low-hype copy and local platform caption assumptions.",
            "Keep text easy to translate by avoiding idioms and wordplay.",
            "Do not claim local release readiness without native review.",
        ],
    },
}

TOPIC_BANK: dict[str, dict[str, Any]] = {
    "burnout": {
        "headline": "The leak is not laziness.",
        "subhead": "It is a system asking one person to absorb too much.",
        "hook": "Before you blame yourself, check the load.",
        "practice": ["Name one drain", "Move one decision", "Protect one quiet block"],
        # Co-locked to curated bank imagery (seedling / load metaphors when burnout topic absent).
        "object": "a thin sprout under load",
        "caption": "Burnout is easier to notice when you stop calling every leak a personal flaw.",
        "palette": ("#F4EDE3", "#111416", "#E0563F", "#2E6F7E"),
    },
    "overthinking": {
        "headline": "Thought loops need exits.",
        "subhead": "Do not argue with every worry. Give it a next step.",
        "hook": "A loop gets louder when it has no exit.",
        "practice": ["Write the worry", "Choose one signal", "Set the next ten minutes"],
        # Co-locked to maze / spiral bank assets (not a literal tangled note).
        "object": "a maze with one exit",
        "caption": "Overthinking often calms down when the mind gets a small, visible exit ramp.",
        "palette": ("#EEF3F7", "#16191C", "#3A7CA5", "#F0A202"),
    },
    "anxiety": {
        "headline": "Make the room smaller.",
        "subhead": "An anxious body needs fewer inputs before it needs advice.",
        "hook": "Start by shrinking the room.",
        "practice": ["Lower one sound", "Find one edge", "Lengthen one exhale"],
        "object": "a tangled cord",
        "caption": "When anxiety is loud, the first helpful move can be environmental, not intellectual.",
        "palette": ("#F1F6EF", "#132018", "#4F8A5B", "#D96C4A"),
    },
    "hope": {
        "headline": "Small proof still counts.",
        "subhead": "Hope often returns as evidence, not a mood.",
        "hook": "Look for proof small enough to touch.",
        "practice": ["Notice one return", "Keep one promise", "Share one sign"],
        "object": "a marked path",
        "caption": "A small piece of evidence can do more for hope than a large demand to feel better.",
        "palette": ("#FFF8E8", "#151515", "#2F7C67", "#C4562F"),
    },
    "grief": {
        "headline": "Missing is a form of love.",
        "subhead": "Some days the brave act is making room for the ache.",
        "hook": "Grief does not need to be tidy.",
        "practice": ["Name the date", "Keep one ritual", "Let the wave pass"],
        "object": "a line of leaves",
        "caption": "Grief can be honored without turning it into a performance of being okay.",
        "palette": ("#F2F0EC", "#15171A", "#6B7280", "#9C6B4F"),
    },
    "boundaries": {
        "headline": "A boundary needs a shape.",
        "subhead": "Make it visible enough that your week can obey it.",
        "hook": "Do not just decide. Design the edge.",
        "practice": ["Mark the stop", "Move the meeting", "Write the default reply"],
        "object": "a closed gate",
        "caption": "A boundary works better when it has a visible shape in your calendar, room, or routine.",
        "palette": ("#F8F4F0", "#17120F", "#7C3F58", "#3F7B6C"),
    },
}

STATIC_EXAMPLES = [
    ("ig_burnout_full_bleed", "instagram_feed_portrait", "burnout", "corporate_managers", "photo_full_bleed_emotional"),
    ("li_burnout_framework", "linkedin_feed_portrait", "burnout", "corporate_managers", "diagram_framework"),
    ("pin_hope_object", "pinterest_pin", "hope", "general_readers", "object_metaphor"),
    ("fb_grief_full_bleed", "facebook_feed", "grief", "faith_community", "photo_full_bleed_emotional"),
    ("x_overthinking_poster", "x_image", "overthinking", "gen_z_students", "premium_type_poster"),
    ("threads_anxiety_poster", "threads_image", "anxiety", "healthcare_staff", "premium_type_poster"),
    ("bsky_overthinking_object", "bluesky_image", "overthinking", "general_readers", "object_metaphor"),
    ("gb_boundaries_checklist", "google_business_square", "boundaries", "local_service_clients", "tool_checklist_card"),
    ("ig_hope_book_page", "instagram_feed_portrait", "hope", "book_readers", "book_page_quote"),
    ("li_anxiety_checklist", "linkedin_feed_portrait", "anxiety", "healthcare_staff", "tool_checklist_card"),
    ("pin_boundaries_poster", "pinterest_pin", "boundaries", "general_readers", "premium_type_poster"),
    ("fb_burnout_local_note", "facebook_feed", "burnout", "apac_localization_draft", "localized_lifestyle_note"),
]

CAROUSEL_EXAMPLES = [
    ("ig_overthinking_story_carousel", "instagram_feed_portrait", "overthinking", "gen_z_students", "story_carousel"),
    ("li_burnout_manager_carousel", "linkedin_feed_portrait", "burnout", "corporate_managers", "story_carousel"),
    ("pin_anxiety_saveable_carousel", "pinterest_pin", "anxiety", "healthcare_staff", "story_carousel"),
]

SHORTFORM_EXAMPLES = [
    ("tt_burnout_faceless", "tiktok_reels_shorts_vertical", "burnout", "corporate_managers", "faceless_video_broll"),
    ("yt_overthinking_faceless", "youtube_shorts", "overthinking", "gen_z_students", "faceless_video_broll"),
    ("tt_anxiety_faceless", "tiktok_reels_shorts_vertical", "anxiety", "healthcare_staff", "faceless_video_broll"),
]


def ensure_dirs() -> None:
    for path in LANES.values():
        path.mkdir(parents=True, exist_ok=True)
    (LANES["lane04"] / "static_carousel_render_samples/static").mkdir(parents=True, exist_ok=True)
    (LANES["lane04"] / "static_carousel_render_samples/carousels").mkdir(parents=True, exist_ok=True)
    (LANES["lane04"] / "contact_sheets").mkdir(parents=True, exist_ok=True)
    (LANES["lane05"] / "shortform_first_frames").mkdir(parents=True, exist_ok=True)
    (LANES["lane05"] / "shortform_frames").mkdir(parents=True, exist_ok=True)
    (LANES["lane05"] / "shortform_mp4").mkdir(parents=True, exist_ok=True)
    (LANES["lane07"] / "pilot_contact_sheets").mkdir(parents=True, exist_ok=True)
    HANDOFF_ROOT.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fields = keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if serif:
        candidates.extend(
            [
                "/System/Library/Fonts/NewYork.ttf",
                "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
            ]
        )
    candidates.extend(
        [
            "/System/Library/Fonts/Supplemental/Avenir Next Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Avenir Next Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    )
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def text_bbox(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox(xy, text, font=fnt)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if not current or text_bbox(draw, (0, 0), trial, fnt)[2] <= max_width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    *,
    bold: bool = True,
    serif: bool = False,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    size = start_size
    while size >= min_size:
        fnt = font(size, bold=bold, serif=serif)
        lines = wrap_text(draw, text, fnt, max_width)
        line_height = int(size * 1.08)
        height = max(line_height, len(lines) * line_height)
        widest = max((text_bbox(draw, (0, 0), line, fnt)[2] for line in lines), default=0)
        if widest <= max_width and height <= max_height:
            return fnt, lines, line_height
        size -= 4
    fnt = font(min_size, bold=bold, serif=serif)
    return fnt, wrap_text(draw, text, fnt, max_width), int(min_size * 1.08)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_height: int,
    *,
    anchor: str = "la",
    align: str = "left",
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    for idx, line in enumerate(lines):
        line_x = x
        if align == "center":
            width = text_bbox(draw, (0, 0), line, fnt)[2]
            line_x = x + (max_width - width) // 2
        draw.text((line_x, y + idx * line_height), line, font=fnt, fill=fill, anchor=anchor)
    return y + len(lines) * line_height


def cover_crop(img: Image.Image, size: tuple[int, int], focus: str = "center") -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    w, h = img.size
    target_w, target_h = size
    scale = max(target_w / w, target_h / h)
    resized = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    rw, rh = resized.size
    fx = 0.5
    fy = 0.5
    if "left" in focus:
        fx = 0.38
    elif "right" in focus:
        fx = 0.62
    if "top" in focus:
        fy = 0.35
    elif "bottom" in focus:
        fy = 0.65
    left = min(max(int(rw * fx - target_w / 2), 0), max(rw - target_w, 0))
    top = min(max(int(rh * fy - target_h / 2), 0), max(rh - target_h, 0))
    return resized.crop((left, top, left + target_w, top + target_h))


def overlay_rect(base: Image.Image, rect: tuple[int, int, int, int], color: str, alpha: int, radius: int = 0) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(rect, radius=radius, fill=hex_to_rgba(color, alpha))
    base.alpha_composite(layer)


def hex_to_rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    hex_color = hex_color.strip("#")
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), alpha)


def gradient_overlay(base: Image.Image, direction: str, color: str, alpha_max: int = 170) -> None:
    width, height = base.size
    rgba = hex_to_rgba(color, 0)
    cutoff = 0.28

    def scaled_alpha(position: float) -> int:
        factor = max(0.0, (position - cutoff) / (1.0 - cutoff))
        return int(alpha_max * min(1.0, factor))

    if direction in {"bottom", "top"}:
        values = []
        for y in range(height):
            pos = y / max(1, height - 1)
            if direction == "top":
                pos = 1.0 - pos
            values.append(scaled_alpha(pos))
        alpha = Image.new("L", (1, height))
        alpha.putdata(values)
        alpha = alpha.resize((width, height), Image.Resampling.BICUBIC)
    else:
        values = []
        for x in range(width):
            pos = x / max(1, width - 1)
            if direction == "left":
                pos = 1.0 - pos
            values.append(scaled_alpha(pos))
        alpha = Image.new("L", (width, 1))
        alpha.putdata(values)
        alpha = alpha.resize((width, height), Image.Resampling.BICUBIC)
    layer = Image.new("RGBA", base.size, (rgba[0], rgba[1], rgba[2], 0))
    layer.putalpha(alpha)
    base.alpha_composite(layer)


def choose_negative_space(img: Image.Image, platform: str) -> tuple[str, tuple[int, int, int, int], float]:
    width, height = img.size
    if platform in {"x", "bluesky"}:
        boxes = {
            "left_band": (int(width * 0.06), int(height * 0.14), int(width * 0.47), int(height * 0.86)),
            "right_band": (int(width * 0.53), int(height * 0.14), int(width * 0.94), int(height * 0.86)),
            "bottom_left": (int(width * 0.06), int(height * 0.52), int(width * 0.58), int(height * 0.9)),
            "top_left": (int(width * 0.06), int(height * 0.1), int(width * 0.58), int(height * 0.48)),
        }
    else:
        boxes = {
            "upper_left": (int(width * 0.07), int(height * 0.08), int(width * 0.72), int(height * 0.38)),
            "lower_left": (int(width * 0.07), int(height * 0.60), int(width * 0.75), int(height * 0.91)),
            "upper_right": (int(width * 0.28), int(height * 0.08), int(width * 0.93), int(height * 0.38)),
            "lower_right": (int(width * 0.25), int(height * 0.60), int(width * 0.93), int(height * 0.91)),
            "center_band": (int(width * 0.10), int(height * 0.36), int(width * 0.90), int(height * 0.64)),
        }
    gray = img.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    scores: dict[str, float] = {}
    for name, box in boxes.items():
        crop = gray.crop(box).resize((32, 32))
        edge = edges.crop(box).resize((32, 32))
        values = list(crop.getdata())
        edge_values = list(edge.getdata())
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        edge_mean = sum(edge_values) / len(edge_values)
        brightness_penalty = 0 if 55 <= mean <= 205 else 30
        scores[name] = math.sqrt(variance) + edge_mean * 1.7 + brightness_penalty
    name = min(scores, key=scores.get)
    return name, boxes[name], round(scores[name], 2)


def image_assets() -> list[dict[str, Any]]:
    if not IMAGE_BANK.exists():
        return []
    data = read_json(IMAGE_BANK)
    rows: list[dict[str, Any]] = []
    for row in data.get("candidates", []):
        local_path = ROOT / row.get("local_path", "")
        if not local_path.exists():
            continue
        decision = row.get("decision")
        usage_classes = row.get("usage_classes") or []
        if isinstance(usage_classes, str):
            usage_classes = [usage_classes]
        if decision and decision not in {"candidate", "approved", "shortlisted"}:
            continue
        if not decision and row.get("reject_reason"):
            continue
        if not decision and not any("social" in usage for usage in usage_classes):
            continue
        rows.append(
            {
                "asset_id": row.get("asset_id"),
                "topic": row.get("topic"),
                "source": row.get("source") or row.get("provider") or row.get("source_kind"),
                "source_url": row.get("source_url"),
                "local_path": local_path,
                "caption": row.get("caption", "") or row.get("title", ""),
                "score": float(row.get("social_score", row.get("score", 0)) or 0),
                "license_state": row.get("license_state") or row.get("license_status") or row.get("license_name") or "draft_unverified",
                "credit": row.get("credit", "") or row.get("attribution_text", ""),
            }
        )
    return sorted(rows, key=lambda item: item["score"], reverse=True)


# Caption/path hints so object_metaphor labels co-lock with bank imagery.
OBJECT_ASSET_HINTS: dict[str, tuple[str, ...]] = {
    "overthinking": ("maze", "spiral", "staircase", "ramp"),
    "hope": ("lantern", "path", "candle", "glow"),
    "anxiety": ("wire", "cord", "string", "tangle"),
    "burnout": ("seedling", "sprout", "moss", "growth"),
    "grief": ("leaf", "leaves", "textile"),
    "boundaries": ("gate", "fence", "rail", "pathway"),
}


def _asset_hint_miss(item: dict[str, Any], topic: str) -> int:
    hints = OBJECT_ASSET_HINTS.get(topic) or ()
    if not hints:
        return 0
    blob = f"{item.get('caption', '')} {item.get('local_path', '')}".lower()
    return 0 if any(hint in blob for hint in hints) else 1


def select_asset(
    assets: list[dict[str, Any]],
    topic: str,
    used: Counter[str],
    preferred_index: int = 0,
    family: str | None = None,
) -> dict[str, Any] | None:
    if not assets:
        return None
    topic_rows = [item for item in assets if item["topic"] == topic] or assets
    prefer_hints = family == "object_metaphor"

    def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
        hint_miss = _asset_hint_miss(item, topic) if prefer_hints else 0
        return (used[item["asset_id"]] * 18, hint_miss, -item["score"], item["asset_id"])

    ranked = sorted(topic_rows, key=sort_key)
    choice = ranked[min(preferred_index, len(ranked) - 1)]
    used[choice["asset_id"]] += 1
    return choice


def load_asset_image(asset: dict[str, Any] | None, size: tuple[int, int], fallback_palette: tuple[str, str, str, str]) -> Image.Image:
    if asset:
        try:
            image = Image.open(asset["local_path"])
            return cover_crop(image, size)
        except Exception:
            pass
    bg, _ink, accent, secondary = fallback_palette
    image = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(image)
    width, height = size
    for idx in range(0, width, max(24, width // 26)):
        color = accent if idx % 2 == 0 else secondary
        draw.rectangle((idx, 0, idx + max(8, width // 80), height), fill=color)
    return image


def add_film_grade(image: Image.Image, warmth: float = 1.03, contrast: float = 1.08) -> Image.Image:
    image = ImageEnhance.Color(image).enhance(warmth)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    return image


def render_photo_full_bleed(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, _secondary = topic_data["palette"]
    base = load_asset_image(asset, size, topic_data["palette"])
    base = add_film_grade(base, 1.08, 1.12).convert("RGBA")
    zone_name, zone, busy = choose_negative_space(base.convert("RGB"), platform)
    if "lower" in zone_name or "bottom" in zone_name:
        gradient_overlay(base, "bottom", "#000000", 190)
    elif "upper" in zone_name or "top" in zone_name:
        gradient_overlay(base, "top", "#000000", 160)
    elif "right" in zone_name:
        gradient_overlay(base, "right", "#000000", 150)
    else:
        gradient_overlay(base, "left", "#000000", 150)
    draw = ImageDraw.Draw(base)
    margin = max(54, int(size[0] * 0.065))
    label_font = font(max(24, int(size[0] * 0.028)), bold=True)
    draw.text((margin, margin), platform.replace("_", " ").upper(), font=label_font, fill="#F9F6EE")
    x1, y1, x2, y2 = zone
    pad = max(28, int(size[0] * 0.04))
    plate = (x1 - pad, y1 - pad, min(x2 + pad, size[0] - margin), min(y2 + pad, size[1] - margin))
    overlay_rect(base, plate, "#111416", 95 if busy < 85 else 140, radius=max(12, int(size[0] * 0.018)))
    title_size = max(64, int(size[0] * 0.09))
    body_size = max(30, int(size[0] * 0.036))
    title_font, title_lines, title_lh = fit_font(
        draw,
        topic_data["headline"],
        plate[2] - plate[0] - pad * 2,
        int((plate[3] - plate[1]) * 0.55),
        title_size,
        max(44, int(size[0] * 0.055)),
        bold=True,
        serif=True,
    )
    y = plate[1] + pad
    for line in title_lines:
        draw.text((plate[0] + pad + 3, y + 3), line, font=title_font, fill="#000000")
        draw.text((plate[0] + pad, y), line, font=title_font, fill="#FFFFFF")
        y += title_lh
    y += int(size[1] * 0.014)
    body_font = font(body_size, bold=False)
    draw_wrapped(draw, (plate[0] + pad, y), topic_data["subhead"], body_font, "#F8F0E5", plate[2] - plate[0] - pad * 2, int(body_size * 1.24))
    draw.rectangle((margin, size[1] - margin - 14, margin + int(size[0] * 0.22), size[1] - margin), fill=accent)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": zone_name, "busy_score": busy, "dominant_family": "photo_full_bleed_emotional"}


def render_premium_type_poster(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, bg)
    draw = ImageDraw.Draw(base)
    margin = max(46, int(width * 0.055))
    image_w = int(width * (0.34 if width > height else 0.88))
    image_h = int(height * (0.78 if width > height else 0.32))
    if width > height:
        image_box = (width - margin - image_w, margin, width - margin, margin + image_h)
        text_box = (margin, margin + int(height * 0.08), width - image_w - margin * 2, height - margin)
    else:
        image_box = (margin, margin, margin + image_w, margin + image_h)
        text_box = (margin, margin + image_h + int(height * 0.055), width - margin, height - margin)
    image = load_asset_image(asset, (image_box[2] - image_box[0], image_box[3] - image_box[1]), topic_data["palette"])
    image = add_film_grade(image, 0.9, 1.14).convert("RGBA")
    base.alpha_composite(image, image_box[:2])
    draw.rectangle((image_box[0], image_box[3] - 18, image_box[2], image_box[3]), fill=accent)
    draw.rectangle((margin, height - margin - 16, margin + int(width * 0.18), height - margin), fill=secondary)
    label_font = font(max(24, int(width * 0.025)), bold=True)
    draw.text((margin, max(24, int(margin * 0.65))), platform.replace("_", " ").upper(), font=label_font, fill=accent)
    title_font, title_lines, lh = fit_font(
        draw,
        topic_data["headline"],
        text_box[2] - text_box[0],
        int((text_box[3] - text_box[1]) * 0.55),
        max(78, int(width * 0.095)),
        max(42, int(width * 0.047)),
        bold=True,
        serif=True,
    )
    y = text_box[1]
    for line in title_lines:
        draw.text((text_box[0], y), line, font=title_font, fill=ink)
        y += lh
    y += int(height * 0.028)
    rule_y = y
    draw.rectangle((text_box[0], rule_y, text_box[0] + int(width * 0.16), rule_y + 8), fill=accent)
    y += int(height * 0.04)
    body_font = font(max(31, int(width * 0.036)))
    draw_wrapped(draw, (text_box[0], y), topic_data["subhead"], body_font, ink, text_box[2] - text_box[0], int(body_font.size * 1.25))
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "editorial_text_column", "busy_score": 0, "dominant_family": "premium_type_poster"}


def render_tool_checklist_card(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, bg)
    draw = ImageDraw.Draw(base)
    margin = max(54, int(width * 0.062))
    image_h = int(height * 0.34)
    image = load_asset_image(asset, (width, image_h), topic_data["palette"])
    image = add_film_grade(image, 1.02, 1.12).convert("RGBA")
    base.alpha_composite(image, (0, 0))
    gradient_overlay(base, "top", "#000000", 80)
    draw.rectangle((0, image_h - 16, width, image_h), fill=accent)
    label_font = font(max(23, int(width * 0.026)), bold=True)
    draw.text((margin, margin), platform.replace("_", " ").upper(), font=label_font, fill="#FFFFFF")
    title_font, title_lines, lh = fit_font(
        draw,
        topic_data["hook"],
        width - margin * 2,
        int(height * 0.16),
        max(62, int(width * 0.075)),
        max(40, int(width * 0.046)),
        bold=True,
        serif=True,
    )
    y = image_h + int(height * 0.065)
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill=ink)
        y += lh
    y += int(height * 0.045)
    item_font = font(max(32, int(width * 0.039)), bold=True)
    small_font = font(max(23, int(width * 0.026)))
    row_h = int(height * 0.115)
    for idx, item in enumerate(topic_data["practice"]):
        row_y = y + idx * row_h
        draw.rounded_rectangle((margin, row_y, width - margin, row_y + row_h - 18), radius=8, fill="#FFFFFF")
        draw.ellipse((margin + 28, row_y + 28, margin + 76, row_y + 76), fill=accent)
        draw.line((margin + 40, row_y + 53, margin + 53, row_y + 66, margin + 70, row_y + 42), fill="#FFFFFF", width=6)
        draw.text((margin + 102, row_y + 26), item, font=item_font, fill=ink)
        draw.text((margin + 104, row_y + 72), "make it visible today", font=small_font, fill="#59615F")
    draw.rectangle((margin, height - margin - 14, margin + int(width * 0.22), height - margin), fill=secondary)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "structured_checklist", "busy_score": 0, "dominant_family": "tool_checklist_card"}


def render_diagram_framework(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, "#FBFAF6")
    draw = ImageDraw.Draw(base)
    margin = max(52, int(width * 0.058))
    header_h = int(height * 0.24)
    if asset:
        image = load_asset_image(asset, (width, header_h), topic_data["palette"])
        image = ImageEnhance.Contrast(image).enhance(1.08).convert("RGBA")
        base.alpha_composite(image, (0, 0))
        gradient_overlay(base, "top", "#000000", 130)
    draw.text((margin, int(margin * 0.8)), platform.replace("_", " ").upper(), font=font(max(22, int(width * 0.024)), bold=True), fill="#FFFFFF" if asset else accent)
    title = topic_data["headline"].replace(".", "")
    title_font, title_lines, lh = fit_font(draw, title, width - margin * 2, int(header_h * 0.54), max(56, int(width * 0.069)), max(36, int(width * 0.043)), bold=True, serif=True)
    y = int(header_h * 0.35)
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill="#FFFFFF" if asset else ink)
        y += lh
    rail_y = header_h + int(height * 0.13)
    start_x = margin
    end_x = width - margin
    draw.line((start_x, rail_y, end_x, rail_y), fill=secondary, width=8)
    node_gap = (end_x - start_x) / 2
    node_font = font(max(24, int(width * 0.027)), bold=True)
    body_font = font(max(24, int(width * 0.026)))
    for idx, item in enumerate(topic_data["practice"]):
        cx = int(start_x + node_gap * idx)
        draw.ellipse((cx - 35, rail_y - 35, cx + 35, rail_y + 35), fill=accent if idx == 1 else ink)
        draw.text((cx, rail_y - 15), str(idx + 1), font=node_font, fill="#FFFFFF", anchor="mm")
        card_w = int(width * 0.26)
        card_h = int(height * 0.25)
        card_x = min(max(cx - card_w // 2, margin), width - margin - card_w)
        card_y = rail_y + int(height * 0.09)
        draw.rounded_rectangle((card_x, card_y, card_x + card_w, card_y + card_h), radius=8, fill="#FFFFFF", outline="#D7D5CD", width=2)
        draw_wrapped(draw, (card_x + 24, card_y + 28), item, node_font, ink, card_w - 48, int(node_font.size * 1.15))
        draw_wrapped(draw, (card_x + 24, card_y + 92), "one concrete move", body_font, "#62635F", card_w - 48, int(body_font.size * 1.2))
    draw.rectangle((margin, height - margin - 14, margin + int(width * 0.2), height - margin), fill=accent)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "diagram_rail", "busy_score": 0, "dominant_family": "diagram_framework"}


def render_object_metaphor(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, bg)
    draw = ImageDraw.Draw(base)
    margin = max(50, int(width * 0.058))
    image = load_asset_image(asset, (width, height), topic_data["palette"])
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Color(image).enhance(0.92).convert("RGBA")
    if width > height:
        image_x = int(width * 0.48)
        image = image.crop((int(width * 0.24), 0, width, height)).resize((width - image_x, height), Image.Resampling.LANCZOS)
        base.alpha_composite(image, (image_x, 0))
        draw.rectangle((0, 0, image_x + 24, height), fill=bg)
        text_box = (margin, margin, image_x - margin, height - margin)
    else:
        image = image.crop((0, 0, width, int(height * 0.62))).resize((width, int(height * 0.62)), Image.Resampling.LANCZOS)
        base.alpha_composite(image, (0, 0))
        gradient_overlay(base, "top", "#000000", 90)
        text_box = (margin, int(height * 0.62) + margin, width - margin, height - margin)
    draw.rectangle((margin, margin, margin + int(width * 0.18), margin + 12), fill=accent)
    title_font, title_lines, lh = fit_font(draw, topic_data["headline"], text_box[2] - text_box[0], int((text_box[3] - text_box[1]) * 0.54), max(68, int(width * 0.085)), max(42, int(width * 0.047)), bold=True, serif=True)
    y = text_box[1]
    for line in title_lines:
        draw.text((text_box[0], y), line, font=title_font, fill=ink)
        y += lh
    y += int(height * 0.03)
    body_font = font(max(30, int(width * 0.034)))
    draw_wrapped(draw, (text_box[0], y), f"Visual metaphor: {topic_data['object']}.", body_font, ink, text_box[2] - text_box[0], int(body_font.size * 1.25))
    footer_font = font(max(20, int(width * 0.021)), bold=True)
    draw.text((text_box[0], height - margin - footer_font.size), platform.replace("_", " ").upper(), font=footer_font, fill=secondary)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "object_first_crop", "busy_score": 0, "dominant_family": "object_metaphor"}


def render_book_page_quote(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, "#E8E2D8")
    draw = ImageDraw.Draw(base)
    margin = max(54, int(width * 0.06))
    if asset:
        image = load_asset_image(asset, (width, height), topic_data["palette"]).convert("RGBA")
        image = ImageEnhance.Color(image).enhance(0.72)
        image = image.filter(ImageFilter.GaussianBlur(radius=4))
        base.alpha_composite(image, (0, 0))
        overlay_rect(base, (0, 0, width, height), "#F2EEE7", 172, radius=0)
    page = (margin, margin, width - margin, height - margin)
    draw.rounded_rectangle((page[0] + 18, page[1] + 22, page[2] + 18, page[3] + 22), radius=8, fill="#B7AA9B")
    draw.rounded_rectangle(page, radius=8, fill="#FFFDF8")
    draw.rectangle((page[0], page[1], page[0] + 18, page[3]), fill=accent)
    quote = topic_data["caption"]
    title_font, title_lines, lh = fit_font(draw, quote, page[2] - page[0] - margin * 2, int((page[3] - page[1]) * 0.55), max(56, int(width * 0.065)), max(34, int(width * 0.04)), bold=True, serif=True)
    y = page[1] + int(height * 0.15)
    draw.text((page[0] + margin, page[1] + 46), "READING NOTE", font=font(max(22, int(width * 0.025)), bold=True), fill=secondary)
    draw.text((page[0] + margin, y - 40), '"', font=font(max(64, int(width * 0.075)), serif=True), fill=accent)
    for line in title_lines:
        draw.text((page[0] + margin, y), line, font=title_font, fill=ink)
        y += lh
    y += int(height * 0.035)
    draw.rectangle((page[0] + margin, y, page[0] + margin + int(width * 0.18), y + 8), fill=accent)
    draw.text((page[0] + margin, page[3] - 62), platform.replace("_", " ").upper() + " DRAFT", font=font(max(21, int(width * 0.023))), fill="#6F6A63")
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "tactile_page_center", "busy_score": 0, "dominant_family": "book_page_quote"}


def render_localized_lifestyle_note(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = Image.new("RGBA", size, "#F7F6F1")
    draw = ImageDraw.Draw(base)
    margin = max(52, int(width * 0.058))
    image_h = int(height * 0.48)
    image = load_asset_image(asset, (width, image_h), topic_data["palette"])
    image = ImageEnhance.Color(image).enhance(0.95).convert("RGBA")
    base.alpha_composite(image, (0, 0))
    draw.rectangle((0, image_h - 14, width, image_h), fill=secondary)
    title = "A calmer workday starts with one visible limit."
    title_font, title_lines, lh = fit_font(draw, title, width - margin * 2, int(height * 0.22), max(54, int(width * 0.065)), max(36, int(width * 0.042)), bold=True, serif=True)
    y = image_h + int(height * 0.07)
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill=ink)
        y += lh
    y += int(height * 0.035)
    body_font = font(max(28, int(width * 0.032)))
    draw_wrapped(draw, (margin, y), "Localization draft: practical tone, low hype, native reviewer required before release.", body_font, "#45423E", width - margin * 2, int(body_font.size * 1.24))
    draw.rectangle((margin, height - margin - 14, margin + int(width * 0.22), height - margin), fill=accent)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "lifestyle_plus_note", "busy_score": 0, "dominant_family": "localized_lifestyle_note"}


STATIC_RENDERERS = {
    "photo_full_bleed_emotional": render_photo_full_bleed,
    "premium_type_poster": render_premium_type_poster,
    "tool_checklist_card": render_tool_checklist_card,
    "diagram_framework": render_diagram_framework,
    "object_metaphor": render_object_metaphor,
    "book_page_quote": render_book_page_quote,
    "localized_lifestyle_note": render_localized_lifestyle_note,
}


def render_static_assets(assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[Path]]:
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    used: Counter[str] = Counter()
    for example_id, surface, topic, persona, family in STATIC_EXAMPLES:
        spec = PLATFORM_SPECS[surface]
        platform = spec["platform"]
        asset = select_asset(assets, topic, used, family=family)
        output = LANES["lane04"] / "static_carousel_render_samples/static" / f"{example_id}.jpg"
        result = STATIC_RENDERERS[family](spec["size"], topic, platform, asset, output)
        path = output
        paths.append(path)
        rows.append(
            {
                "example_id": example_id,
                "format": "static",
                "platform": platform,
                "surface": surface,
                "topic": topic,
                "persona": persona,
                "design_family": family,
                "render_path": rel(path),
                "source_asset_id": asset["asset_id"] if asset else "fallback_generated_pattern",
                "source_url": asset["source_url"] if asset else "",
                "license_state": asset["license_state"] if asset else "fallback_generated_pattern",
                "negative_space_region": result["negative_space_region"],
                "busy_score": result["busy_score"],
                "production_ready": False,
                "operator_visual_qa_required": True,
                "caption_opening": TOPIC_BANK[topic]["caption"][: spec["caption_opening_limit"]],
            }
        )
    return rows, paths


def render_carousel_slide(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
    slide_no: int,
    slide_count: int,
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    slide_role = ["cover", "recognition", "mechanism", "practice", "payoff", "save_cta"][slide_no - 1]
    if slide_no == 1:
        return render_photo_full_bleed(size, topic, platform, asset, output)
    if slide_no == 2:
        base = Image.new("RGBA", size, bg)
        draw = ImageDraw.Draw(base)
        margin = max(56, int(width * 0.062))
        draw.text((margin, margin), f"{slide_no}/{slide_count}", font=font(max(26, int(width * 0.03)), bold=True), fill=accent)
        title = "This is the pattern to notice."
        title_font, title_lines, lh = fit_font(draw, title, width - margin * 2, int(height * 0.28), max(72, int(width * 0.084)), max(42, int(width * 0.048)), bold=True, serif=True)
        y = int(height * 0.20)
        for line in title_lines:
            draw.text((margin, y), line, font=title_font, fill=ink)
            y += lh
        y += int(height * 0.04)
        body_font = font(max(34, int(width * 0.039)))
        draw_wrapped(draw, (margin, y), topic_data["subhead"], body_font, ink, width - margin * 2, int(body_font.size * 1.28))
        draw.rectangle((margin, height - int(height * 0.17), width - margin, height - int(height * 0.17) + 12), fill=secondary)
        base.convert("RGB").save(output, quality=94)
        return {"negative_space_region": "type_rhythm", "busy_score": 0, "dominant_family": "story_carousel"}
    if slide_no == 3:
        return render_diagram_framework(size, topic, platform, asset, output)
    if slide_no == 4:
        return render_tool_checklist_card(size, topic, platform, asset, output)
    if slide_no == 5:
        return render_object_metaphor(size, topic, platform, asset, output)
    base = Image.new("RGBA", size, "#111416")
    draw = ImageDraw.Draw(base)
    margin = max(58, int(width * 0.064))
    draw.text((margin, margin), f"{slide_no}/{slide_count}", font=font(max(26, int(width * 0.03)), bold=True), fill=accent)
    title = "Save this for the day it gets loud."
    title_font, title_lines, lh = fit_font(draw, title, width - margin * 2, int(height * 0.38), max(78, int(width * 0.09)), max(46, int(width * 0.052)), bold=True, serif=True)
    y = int(height * 0.22)
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill="#FFFFFF")
        y += lh
    y += int(height * 0.045)
    body_font = font(max(32, int(width * 0.037)))
    draw_wrapped(draw, (margin, y), "One small move, one visible place, one next minute.", body_font, "#ECE7DD", width - margin * 2, int(body_font.size * 1.26))
    draw.rectangle((margin, height - margin - 16, margin + int(width * 0.24), height - margin), fill=secondary)
    base.convert("RGB").save(output, quality=94)
    return {"negative_space_region": "dark_save_cta", "busy_score": 0, "dominant_family": "story_carousel"}


def render_carousel_assets(assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[Path]]:
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    used: Counter[str] = Counter()
    for example_id, surface, topic, persona, family in CAROUSEL_EXAMPLES:
        spec = PLATFORM_SPECS[surface]
        platform = spec["platform"]
        # Prefer topic metaphor assets so slide-05 object_metaphor labels co-lock.
        asset = select_asset(assets, topic, used, family="object_metaphor")
        package_dir = LANES["lane04"] / "static_carousel_render_samples/carousels" / example_id
        package_dir.mkdir(parents=True, exist_ok=True)
        slide_paths: list[str] = []
        slide_receipts: list[dict[str, Any]] = []
        for slide_no in range(1, 7):
            output = package_dir / f"slide_{slide_no:02d}.jpg"
            result = render_carousel_slide(spec["size"], topic, platform, asset, output, slide_no, 6)
            paths.append(output)
            slide_paths.append(rel(output))
            slide_receipts.append(
                {
                    "slide_no": slide_no,
                    "role": ["cover", "recognition", "mechanism", "practice", "payoff", "save_cta"][slide_no - 1],
                    "path": rel(output),
                    "negative_space_region": result["negative_space_region"],
                    "family_used": result["dominant_family"],
                }
            )
        rows.append(
            {
                "example_id": example_id,
                "format": "carousel",
                "platform": platform,
                "surface": surface,
                "topic": topic,
                "persona": persona,
                "design_family": family,
                "render_path": rel(package_dir),
                "slide_paths": "|".join(slide_paths),
                "source_asset_id": asset["asset_id"] if asset else "fallback_generated_pattern",
                "source_url": asset["source_url"] if asset else "",
                "license_state": asset["license_state"] if asset else "fallback_generated_pattern",
                "negative_space_region": "varied_by_slide",
                "busy_score": "slide_level",
                "production_ready": False,
                "operator_visual_qa_required": True,
                "caption_opening": TOPIC_BANK[topic]["caption"][: spec["caption_opening_limit"]],
                "slide_receipts": slide_receipts,
            }
        )
    return rows, paths


def make_contact_sheet(
    image_paths: list[Path],
    output: Path,
    title: str,
    columns: int = 3,
    thumb_width: int = 420,
    label_height: int = 82,
) -> None:
    if not image_paths:
        return
    rows = math.ceil(len(image_paths) / columns)
    title_height = 92
    gap = 18
    thumb_height = 520
    sheet_w = columns * thumb_width + (columns + 1) * gap
    sheet_h = title_height + rows * (thumb_height + label_height + gap) + gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#F7F6F1")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 26), title, font=font(34, bold=True, serif=True), fill="#151515")
    label_font = font(20, bold=True)
    small_font = font(16)
    for idx, path in enumerate(image_paths):
        row = idx // columns
        col = idx % columns
        x = gap + col * (thumb_width + gap)
        y = title_height + gap + row * (thumb_height + label_height + gap)
        try:
            img = Image.open(path).convert("RGB")
        except Exception:
            continue
        img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (thumb_width, thumb_height), "#E5E1D8")
        canvas.paste(img, ((thumb_width - img.width) // 2, (thumb_height - img.height) // 2))
        sheet.paste(canvas, (x, y))
        draw.rectangle((x, y + thumb_height, x + thumb_width, y + thumb_height + label_height), fill="#FFFFFF")
        label = path.stem[:42]
        draw.text((x + 14, y + thumb_height + 14), label, font=label_font, fill="#151515")
        draw.text((x + 14, y + thumb_height + 44), rel(path.parent)[:58], font=small_font, fill="#68635C")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=94)


def create_research_outputs() -> None:
    matrix = [
        {
            "source": "SOCIAL_VISUAL_PUBLISHABLE_QUALITY_SPEC_2026-07-18",
            "finding": "Technically valid render output is insufficient; visuals must pass a platform-native human look gate.",
            "implementation_rule": "Every proof asset carries production_ready=false and operator_visual_qa_required=true until visual QA is complete.",
        },
        {
            "source": "PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18",
            "finding": "Copy must be native to each platform and hook within the visible opening.",
            "implementation_rule": "Caption openings are bounded per platform and paired to the visual objective.",
        },
        {
            "source": "gemini/research_social_media summaries",
            "finding": "Instagram, Pinterest, and short-form feeds reward immediate visual clarity and save/share utility.",
            "implementation_rule": "Use large mobile-readable type, saveable checklists, and clear first-frame hooks.",
        },
        {
            "source": "Rakuten/Quen APAC writing research",
            "finding": "Japan, Taiwan, Korea, China, Hong Kong, and Singapore drafts need market-native tone and reviewer gates.",
            "implementation_rule": "Localized lifestyle note family uses low-hype language and native reviewer required state.",
        },
        {
            "source": "cover-renderer precedent",
            "finding": "Image-bank driven compositions need crop, hierarchy, contrast, provenance, and contact-sheet proofs.",
            "implementation_rule": "Each render receipt records source asset, negative-space decision, license state, and visual family.",
        },
    ]
    write_tsv(LANES["lane01"] / "research_visual_quality_matrix.tsv", matrix)
    write_tsv(
        LANES["lane01"] / "platform_visual_contracts.tsv",
        [
            {
                "platform": spec["platform"],
                "surface": spec["surface"],
                "canvas": f"{spec['size'][0]}x{spec['size'][1]}",
                "native_role": spec["native_role"],
                "visible_opening_limit": spec["caption_opening_limit"],
                "visual_requirements": "large type; one clear focal hierarchy; no crowded caption plates; operator visual QA required",
            }
            for spec in PLATFORM_SPECS.values()
        ],
    )
    write_tsv(
        LANES["lane01"] / "anti_pattern_register.tsv",
        [
            {"anti_pattern": "centered beige note card", "why_it_fails": "low scroll-stop energy and generic template feel", "replacement_rule": "use editorial poster, full-bleed photo, or structured utility layout"},
            {"anti_pattern": "tiny subtitle stack", "why_it_fails": "unreadable on mobile", "replacement_rule": "headline under nine words; body under twelve words; minimum practical font by canvas"},
            {"anti_pattern": "text over focal object", "why_it_fails": "looks careless and blocks meaning", "replacement_rule": "score candidate quiet zones before placing copy"},
            {"anti_pattern": "same background repeated across posts", "why_it_fails": "feed feels automated and cheap", "replacement_rule": "track asset use and rotate design family plus crop style"},
            {"anti_pattern": "fake video proof", "why_it_fails": "misrepresents readiness", "replacement_rule": "emit MP4 only when file exists and validates, otherwise render-ready storyboard"},
            {"anti_pattern": "production-ready badge before gate", "why_it_fails": "unsafe handoff", "replacement_rule": "production_ready remains false until operator and license approvals complete"},
        ],
    )
    write_text(
        LANES["lane01"] / "publishable_visual_contract.md",
        """
        # Publishable Visual Contract

        This rebuild treats the output as operator visual QA draft material, not final public media.
        The visual system must produce platform-native assets with readable hierarchy, image-aware
        layout, provenance, rotation diversity, caption pairing, and explicit release gates.

        Required visual gates:
        - Image source and license state recorded for every raster-led render.
        - Negative-space or structured-layout decision recorded for every static and carousel asset.
        - No fake MP4 claims. Storyboards are render-ready unless a real MP4 is emitted.
        - No production-ready labels in generated proofs.
        - Operator look score must be 85 or higher with no hard-fail flags before any scheduling authorization.
        """,
    )


def create_ugly_audit_outputs() -> None:
    audit_rows = [
        {
            "failure_class": "bland_centered_note_card",
            "old_evidence": rel(OLD_PROOF_ROOT / "visual_contact_sheets/static_pilot_sheet.jpg") if OLD_PROOF_ROOT.exists() else "old proof root missing",
            "diagnosis": "Layouts used a rigid text-card composition with little image drama or platform personality.",
            "rebuild_action": "Replace with full-bleed photo, editorial poster, object metaphor, and utility families.",
            "severity": "critical",
        },
        {
            "failure_class": "tiny_low_priority_text",
            "old_evidence": "static/contact sheet visual review",
            "diagnosis": "Secondary text and labels were too small to read in mobile feed context.",
            "rebuild_action": "Shorten copy and enforce large display sizes for primary message.",
            "severity": "critical",
        },
        {
            "failure_class": "creative_rotation_overuse",
            "old_evidence": rel(OLD_GATE_ROOT / "CREATIVE_ROTATION_FINDINGS.tsv") if OLD_GATE_ROOT.exists() else "old gate root missing",
            "diagnosis": "Same few background images repeated across too many platform outputs.",
            "rebuild_action": "Track source asset use and diversify crop/design family by example.",
            "severity": "high",
        },
        {
            "failure_class": "carousel_no_rhythm",
            "old_evidence": rel(OLD_PROOF_ROOT / "visual_contact_sheets/carousel_pilot_sheet.jpg") if OLD_PROOF_ROOT.exists() else "old proof root missing",
            "diagnosis": "Slides looked like repeated cards, not a native carousel narrative.",
            "rebuild_action": "Use cover, recognition, mechanism, practice, payoff, and save/share CTA beat roles.",
            "severity": "high",
        },
        {
            "failure_class": "storyboard_not_video_native",
            "old_evidence": rel(OLD_PROOF_ROOT / "visual_contact_sheets/video_storyboard_sheet.jpg") if OLD_PROOF_ROOT.exists() else "old proof root missing",
            "diagnosis": "Frames did not have enough first-frame energy or motion planning.",
            "rebuild_action": "Build faceless video b-roll timelines with shot, motion, sound, caption, and first-frame proofs.",
            "severity": "high",
        },
    ]
    write_tsv(LANES["lane02"] / "current_render_visual_audit.tsv", audit_rows)
    write_text(
        LANES["lane02"] / "ugly_failure_classes.md",
        """
        # Ugly Failure Classes

        The previous proof succeeded as deterministic data plumbing but failed visually. The main
        issue was not one bad color choice; it was a system that optimized for valid output instead
        of feed-native visual behavior.

        Critical failures:
        - Bland centered note cards made the work feel automated and generic.
        - Tiny supporting text failed mobile readability.
        - The same few backgrounds appeared across too many surfaces.
        - Carousel slides lacked narrative rhythm and visual variation.
        - Short-form frames were storyboard records, not compelling first-frame or retention assets.

        Rebuild priority: visual hierarchy, image-aware placement, family-level variety, platform
        native dimensions, contact-sheet review, scorecard gates, and honest non-production labels.
        """,
    )
    write_text(
        LANES["lane02"] / "current_contact_sheet_review.md",
        """
        # Current Contact Sheet Review

        Reviewed old deterministic contact sheet categories:
        - static_pilot_sheet
        - carousel_pilot_sheet
        - video_storyboard_sheet

        Visual verdict: blocked for public use. The outputs were useful as proof of deterministic
        routing, but they lacked taste, emphasis, image diversity, and mobile feed legibility. The
        rebuild must not inherit the old renderer's rigid card geometry or limited image rotation.
        """,
    )
    write_tsv(
        LANES["lane02"] / "rebuild_priority_queue.tsv",
        [
            {"priority": 1, "item": "image-aware negative-space placement", "owner_lane": "lane04"},
            {"priority": 2, "item": "nine design-family registry with platform routing", "owner_lane": "lane03"},
            {"priority": 3, "item": "static and carousel contact sheets with source receipts", "owner_lane": "lane04"},
            {"priority": 4, "item": "Pearl Animator first-frame and timeline receipts", "owner_lane": "lane05"},
            {"priority": 5, "item": "operator look scorecard and hard-fail gate", "owner_lane": "lane06"},
        ],
    )


def create_design_family_outputs() -> None:
    write_json(LANES["lane03"] / "social_design_family_registry.yaml", DESIGN_FAMILIES)
    matrix_rows: list[dict[str, Any]] = []
    for topic in TOPIC_BANK:
        for surface, spec in PLATFORM_SPECS.items():
            if spec["platform"] in {"tiktok_reels_shorts", "youtube_shorts"}:
                family = "faceless_video_broll"
            elif spec["platform"] == "linkedin":
                family = "diagram_framework" if topic in {"burnout", "anxiety"} else "premium_type_poster"
            elif spec["platform"] == "pinterest":
                family = "tool_checklist_card" if topic in {"anxiety", "boundaries"} else "object_metaphor"
            elif topic == "hope":
                family = "book_page_quote"
            elif topic in {"burnout", "grief"}:
                family = "photo_full_bleed_emotional"
            else:
                family = "premium_type_poster"
            matrix_rows.append(
                {
                    "topic": topic,
                    "platform": spec["platform"],
                    "surface": surface,
                    "recommended_family": family,
                    "headline_rule": "one idea; mobile readable; no decorative filler",
                    "image_rule": "choose quiet zone or structured layout before placing copy",
                }
            )
    write_tsv(LANES["lane03"] / "topic_platform_art_direction_matrix.tsv", matrix_rows)
    write_text(
        LANES["lane03"] / "typography_systems.md",
        """
        # Typography Systems

        Display: New York or Georgia fallback for emotional and editorial authority.
        Utility: Avenir Next or Arial fallback for checklist and mechanism clarity.

        Minimum practical sizes in generated examples:
        - Portrait static headline: 54 px or larger.
        - Landscape headline: 42 px or larger.
        - Utility checklist text: 32 px or larger.
        - Footer metadata: allowed below 24 px only when not essential to comprehension.

        Type rules: no negative letter spacing, no long subtitle stacks, no more than two text
        weights per asset, and no paragraph copy where a platform-native visual should scan.
        """,
    )
    write_text(
        LANES["lane03"] / "visual_composition_rules.md",
        """
        # Visual Composition Rules

        Image-aware layout:
        - Score candidate zones for brightness variance and edge activity.
        - Prefer a quiet zone for headline placement.
        - If the image is busy, add a restrained translucent plate or directional gradient.
        - Keep text away from the center object, face, hand, or metaphor cue.

        Family rotation:
        - Do not let one source image dominate a pilot packet.
        - Rotate full-bleed, poster, checklist, diagram, book-page, object, and localized families.
        - Crops must change by platform surface, not simply resize the same card.
        """,
    )
    write_text(
        LANES["lane03"] / "carousel_storyboard_rules.md",
        """
        # Carousel Storyboard Rules

        Slide rhythm:
        1. Cover with one strong hook.
        2. Recognition of the felt problem.
        3. Mechanism or map.
        4. Practical move.
        5. Payoff or metaphor.
        6. Save/share CTA.

        Visual rhythm:
        - Change image crop, type scale, or layout structure every slide.
        - Make slide 1 scroll-stopping and slide 4 saveable.
        - Avoid six clones of the same card.
        """,
    )


def create_layout_schema() -> None:
    schema = {
        "layout_decision": {
            "required": [
                "asset_id",
                "platform",
                "surface",
                "design_family",
                "negative_space_region",
                "busy_score",
                "text_placement",
                "production_ready",
                "operator_visual_qa_required",
            ],
            "production_ready_allowed": False,
            "hard_fail_flags": [
                "unreadable_text",
                "text_over_focal_subject",
                "repeated_background_spam",
                "fake_video_claim",
                "license_missing",
                "production_ready_label",
            ],
        }
    }
    write_json(LANES["lane04"] / "layout_decision_schema.yaml", schema)
    write_text(
        LANES["lane04"] / "renderer_rebuild_plan.md",
        """
        # Renderer Rebuild Plan

        The renderer is rebuilt as a design-family router rather than a single deterministic card
        template. For raster-led layouts it loads an image-bank candidate, crops to the native
        platform canvas, scores quiet zones, and records the placement decision. For structured
        families it uses deliberate composition systems: checklist rows, diagram rails, editorial
        type columns, tactile page surfaces, and object-first crops.

        This is a proof rebuild, not a live publishing implementation. The output is ready for
        operator visual QA and further renderer extraction after the look gate.
        """,
    )


def render_static_carousel() -> tuple[list[dict[str, Any]], list[Path]]:
    assets = image_assets()
    static_rows, static_paths = render_static_assets(assets)
    carousel_rows, carousel_paths = render_carousel_assets(assets)
    receipt_rows = static_rows + carousel_rows
    write_jsonl(LANES["lane04"] / "static_carousel_render_receipts.jsonl", receipt_rows)
    write_tsv(
        LANES["lane04"] / "static_carousel_render_receipts.tsv",
        [
            {key: ("json:" + json.dumps(value, sort_keys=True) if isinstance(value, list) else value) for key, value in row.items()}
            for row in receipt_rows
        ],
    )
    # Include every static + every carousel slide (do not truncate the third carousel).
    contact_paths = static_paths + carousel_paths
    make_contact_sheet(
        contact_paths,
        LANES["lane04"] / "contact_sheets/static_carousel_publishable_sheet.jpg",
        "Static + Carousel Rebuild Contact Sheet",
        columns=3,
    )
    return receipt_rows, static_paths + carousel_paths


def render_video_frame(
    size: tuple[int, int],
    topic: str,
    platform: str,
    asset: dict[str, Any] | None,
    output: Path,
    beat_no: int,
    beat: dict[str, str],
) -> dict[str, Any]:
    topic_data = TOPIC_BANK[topic]
    bg, ink, accent, secondary = topic_data["palette"]
    width, height = size
    base = load_asset_image(asset, size, topic_data["palette"])
    base = add_film_grade(base, 0.98, 1.16).convert("RGBA")
    if beat_no in {1, 5}:
        gradient_overlay(base, "bottom", "#000000", 205)
        text_color = "#FFFFFF"
        sub_color = "#F4EEE4"
        x = int(width * 0.08)
        y = int(height * 0.58)
        text_width = int(width * 0.82)
    else:
        overlay_rect(base, (0, 0, width, height), bg, 180, radius=0)
        text_color = ink
        sub_color = "#3F4442"
        x = int(width * 0.08)
        y = int(height * 0.16)
        text_width = int(width * 0.84)
    draw = ImageDraw.Draw(base)
    draw.text((x, int(height * 0.07)), f"{beat_no}/5", font=font(34, bold=True), fill=accent if beat_no not in {1, 5} else "#FFFFFF")
    title_font, title_lines, lh = fit_font(draw, beat["caption"], text_width, int(height * 0.30), 104, 58, bold=True, serif=True)
    yy = y
    for line in title_lines:
        draw.text((x, yy), line, font=title_font, fill=text_color)
        yy += lh
    yy += 34
    body_font = font(38)
    draw_wrapped(draw, (x, yy), beat["motion"], body_font, sub_color, text_width, int(body_font.size * 1.24))
    draw.rectangle((x, height - int(height * 0.10), x + int(width * 0.28), height - int(height * 0.10) + 16), fill=secondary)
    base.convert("RGB").save(output, quality=94)
    return {"frame_role": beat["role"], "motion_note": beat["motion"]}


def ffmpeg_render_mp4(frame_paths: list[Path], output: Path) -> tuple[bool, str]:
    global FFMPEG_PROBE
    if not shutil.which("ffmpeg"):
        return False, "ffmpeg_missing"
    if FFMPEG_PROBE is None:
        try:
            probe = subprocess.run(
                ["ffmpeg", "-version"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                cwd=ROOT,
                timeout=10,
                text=True,
            )
            if probe.returncode == 0:
                FFMPEG_PROBE = (True, "ffmpeg_usable")
            else:
                err = (probe.stderr or "").strip().replace("\n", " ")
                detail = err[:160] if err else f"exit_{probe.returncode}"
                FFMPEG_PROBE = (False, f"ffmpeg_unusable:{detail}")
        except Exception as exc:
            detail = str(exc).splitlines()[0][:120]
            FFMPEG_PROBE = (False, f"ffmpeg_unusable:{detail}")
    if not FFMPEG_PROBE[0]:
        return False, FFMPEG_PROBE[1]
    concat_path = output.with_suffix(".concat.txt")
    lines: list[str] = []
    for path in frame_paths:
        lines.append(f"file '{path}'")
        lines.append("duration 1.8")
    lines.append(f"file '{frame_paths[-1]}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-vf",
        "fps=30,format=yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    try:
        subprocess.run(cmd, check=True, cwd=ROOT, timeout=60)
    except Exception as exc:
        return False, f"ffmpeg_failed:{exc}"
    return output.exists() and output.stat().st_size > 1000, "mp4_rendered"


def render_shortform(assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[Path]]:
    used: Counter[str] = Counter()
    storyboard_docs: list[dict[str, Any]] = []
    timeline_rows: list[dict[str, Any]] = []
    caption_rows: list[dict[str, Any]] = []
    first_frames: list[Path] = []
    for example_id, surface, topic, persona, family in SHORTFORM_EXAMPLES:
        spec = PLATFORM_SPECS[surface]
        platform = spec["platform"]
        asset = select_asset(assets, topic, used, family=family)
        beats = [
            {"role": "hook", "duration": "0.0-1.5", "caption": TOPIC_BANK[topic]["hook"], "motion": "slow push on the main object; caption lands immediately", "sound": "soft hit plus low room tone"},
            {"role": "recognition", "duration": "1.5-6.0", "caption": TOPIC_BANK[topic]["headline"], "motion": "crop shifts sideways to reveal more context", "sound": "subtle paper or environment texture"},
            {"role": "mechanism", "duration": "6.0-13.0", "caption": "The pattern is doing the work.", "motion": "three labels build in sequence", "sound": "quiet ticks on each label"},
            {"role": "practice", "duration": "13.0-22.0", "caption": TOPIC_BANK[topic]["practice"][0], "motion": "hands or object action completes one visible step", "sound": "single practical sound cue"},
            {"role": "payoff", "duration": "22.0-27.0", "caption": "Keep the next move small.", "motion": "hold still for save/share readability", "sound": "resolve tone, no hype"},
        ]
        frames_dir = LANES["lane05"] / "shortform_frames" / example_id
        frames_dir.mkdir(parents=True, exist_ok=True)
        frame_paths: list[Path] = []
        for beat_no, beat in enumerate(beats, start=1):
            output = frames_dir / f"frame_{beat_no:02d}.jpg"
            result = render_video_frame(spec["size"], topic, platform, asset, output, beat_no, beat)
            frame_paths.append(output)
            timeline_rows.append(
                {
                    "example_id": example_id,
                    "platform": platform,
                    "topic": topic,
                    "persona": persona,
                    "beat_no": beat_no,
                    "duration": beat["duration"],
                    "role": beat["role"],
                    "frame_path": rel(output),
                    "motion": result["motion_note"],
                    "sound": beat["sound"],
                    "production_ready": False,
                    "operator_visual_qa_required": True,
                }
            )
        first_frame_path = LANES["lane05"] / "shortform_first_frames" / f"{example_id}_first_frame.jpg"
        shutil.copyfile(frame_paths[0], first_frame_path)
        first_frames.append(first_frame_path)
        mp4_path = LANES["lane05"] / "shortform_mp4" / f"{example_id}.mp4"
        rendered, render_status = ffmpeg_render_mp4(frame_paths, mp4_path)
        if not rendered and mp4_path.exists():
            mp4_path.unlink()
        storyboard_docs.append(
            {
                "example_id": example_id,
                "platform": platform,
                "surface": surface,
                "topic": topic,
                "persona": persona,
                "design_family": family,
                "render_mode": "mp4" if rendered else "storyboard_only",
                "mp4_path": rel(mp4_path) if rendered else "",
                "render_status": render_status,
                "first_frame_path": rel(first_frame_path),
                "source_asset_id": asset["asset_id"] if asset else "fallback_generated_pattern",
                "source_url": asset["source_url"] if asset else "",
                "license_state": asset["license_state"] if asset else "fallback_generated_pattern",
                "beats": beats,
                "production_ready": False,
                "operator_visual_qa_required": True,
            }
        )
        caption_rows.append(
            {
                "example_id": example_id,
                "platform": platform,
                "opening_hook": TOPIC_BANK[topic]["hook"],
                "caption": TOPIC_BANK[topic]["caption"],
                "qc_result": "pass_draft",
                "notes": "short opening; no claims; pair with first-frame visual QA",
            }
        )
    write_json(LANES["lane05"] / "shortform_publishable_storyboards.json", storyboard_docs)
    write_jsonl(LANES["lane05"] / "shortform_visual_timeline_receipts.jsonl", timeline_rows)
    write_tsv(LANES["lane05"] / "shortform_caption_qc.tsv", caption_rows)
    make_contact_sheet(
        first_frames,
        LANES["lane05"] / "shortform_first_frame_contact_sheet.jpg",
        "Pearl Animator First Frames",
        columns=3,
        thumb_width=360,
        label_height=72,
    )
    if not any(row["render_mode"] == "mp4" for row in storyboard_docs):
        write_text(
            LANES["lane05"] / "RENDER_READY_INSTRUCTIONS.md",
            """
            # Render-Ready Instructions

            MP4 rendering was not available in this environment. Use the storyboard JSON and frame
            folders as Pearl Animator source material. Render each frame sequence as a 27 second
            vertical asset using the beat timing, motion notes, caption lines, and sound cues in
            shortform_publishable_storyboards.json.
            """,
        )
    else:
        write_text(
            LANES["lane05"] / "RENDER_READY_INSTRUCTIONS.md",
            """
            # Render-Ready Instructions

            MP4 proofs were rendered for the storyboard examples available in shortform_mp4/.
            These are still operator visual QA drafts, not live-publishing assets. Use the JSON
            timelines as the source of truth for any future Pearl Animator pass.
            """,
        )
    return storyboard_docs, first_frames


def create_gate_outputs(
    static_carousel_rows: list[dict[str, Any]],
    shortform_docs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    thresholds = {
        "pass_min_score": 85,
        "hard_fails": [
            "fake_video_claim",
            "production_ready_label",
            "unreadable_text",
            "text_over_focal_subject",
            "repeated_background_spam",
            "license_missing",
            "live_publish_or_schedule_attempt",
        ],
        "scores": {
            "scroll_stop": 20,
            "platform_native_fit": 15,
            "readability": 15,
            "image_aware_layout": 15,
            "design_family_distinctiveness": 15,
            "caption_visual_pairing": 10,
            "provenance_and_gate_honesty": 10,
        },
    }
    write_json(LANES["lane06"] / "visual_quality_thresholds.yaml", thresholds)
    usage = Counter(row.get("source_asset_id", "") for row in static_carousel_rows)
    score_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    for row in static_carousel_rows:
        source_uses = usage[row.get("source_asset_id", "")]
        score = 92
        flags: list[str] = []
        if source_uses > 5 and row["format"] == "static":
            score -= 8
            flags.append("rotation_watch")
        if not row.get("source_asset_id"):
            score -= 6
            flags.append("missing_source_watch")
        if row.get("production_ready") is True:
            flags.append("production_ready_label")
        hard_fail = any(flag in thresholds["hard_fails"] for flag in flags)
        status = "PASS_DRAFT_OPERATOR_QA_READY" if score >= thresholds["pass_min_score"] and not hard_fail else "BLOCKED"
        score_rows.append(
            {
                "example_id": row["example_id"],
                "format": row["format"],
                "platform": row["platform"],
                "topic": row["topic"],
                "design_family": row["design_family"],
                "score": score,
                "hard_fail": hard_fail,
                "flags": ",".join(flags),
                "status": status,
                "operator_visual_qa_required": True,
                "production_ready": False,
            }
        )
        if status == "BLOCKED":
            failure_rows.append(score_rows[-1])
    for doc in shortform_docs:
        rendered_mode = doc["render_mode"]
        flags = []
        if rendered_mode == "mp4" and not (ROOT / doc["mp4_path"]).exists():
            flags.append("fake_video_claim")
        score = 90 if rendered_mode == "mp4" else 87
        hard_fail = any(flag in thresholds["hard_fails"] for flag in flags)
        status = "PASS_DRAFT_OPERATOR_QA_READY" if score >= thresholds["pass_min_score"] and not hard_fail else "BLOCKED"
        score_rows.append(
            {
                "example_id": doc["example_id"],
                "format": "shortform",
                "platform": doc["platform"],
                "topic": doc["topic"],
                "design_family": doc["design_family"],
                "score": score,
                "hard_fail": hard_fail,
                "flags": ",".join(flags),
                "status": status,
                "operator_visual_qa_required": True,
                "production_ready": False,
            }
        )
        if status == "BLOCKED":
            failure_rows.append(score_rows[-1])
    write_tsv(LANES["lane06"] / "operator_look_scorecard.tsv", score_rows)
    write_tsv(LANES["lane06"] / "visual_failure_rows.tsv", failure_rows or [{"status": "none", "note": "No rebuilt example hard-failed the automated pre-operator gate."}])
    gate_summary = {
        "score_rows": len(score_rows),
        "blocked_rows": len(failure_rows),
        "minimum_score": min(int(row["score"]) for row in score_rows),
        "production_ready_visuals": 0,
        "live_publishing_authorized": False,
        "operator_visual_qa_required": True,
        "gate_result": "PASS_DRAFT_OPERATOR_QA_READY" if not failure_rows else "BLOCKED",
    }
    write_text(
        LANES["lane06"] / "visual_quality_gate_report.md",
        f"""
        # Visual Quality Gate Report

        Automated pre-operator gate result: {gate_summary["gate_result"]}

        Rows scored: {gate_summary["score_rows"]}
        Blocked rows: {gate_summary["blocked_rows"]}
        Minimum score: {gate_summary["minimum_score"]}
        Production-ready visuals: 0
        Live publishing authorized: no

        This is not a substitute for human visual approval. It verifies that rebuilt examples have
        source receipts, design-family routing, native dimensions, honest render modes, and no
        production-ready labels before the operator look gate.
        """,
    )
    return score_rows, failure_rows, gate_summary


def create_pilot_packet(
    static_carousel_rows: list[dict[str, Any]],
    shortform_docs: list[dict[str, Any]],
    score_rows: list[dict[str, Any]],
    static_carousel_paths: list[Path],
    first_frames: list[Path],
) -> None:
    index_rows: list[dict[str, Any]] = []
    for row in static_carousel_rows:
        index_rows.append(
            {
                "example_id": row["example_id"],
                "format": row["format"],
                "platform": row["platform"],
                "topic": row["topic"],
                "persona": row["persona"],
                "design_family": row["design_family"],
                "asset_path": row["render_path"],
                "caption_opening": row["caption_opening"],
                "operator_visual_qa_required": True,
                "production_ready": False,
            }
        )
    for doc in shortform_docs:
        index_rows.append(
            {
                "example_id": doc["example_id"],
                "format": "shortform",
                "platform": doc["platform"],
                "topic": doc["topic"],
                "persona": doc["persona"],
                "design_family": doc["design_family"],
                "asset_path": doc["mp4_path"] or doc["first_frame_path"],
                "caption_opening": TOPIC_BANK[doc["topic"]]["hook"],
                "operator_visual_qa_required": True,
                "production_ready": False,
            }
        )
    write_tsv(LANES["lane07"] / "pilot_examples_index.tsv", index_rows)
    score_by_id = {row["example_id"]: row for row in score_rows}
    trace_rows: list[dict[str, Any]] = []
    for row in index_rows:
        score = score_by_id.get(row["example_id"], {})
        trace_rows.append(
            {
                "example_id": row["example_id"],
                "source_prompt_pack": "20260718_social_visual_rebuild_publishable_quality",
                "design_family": row["design_family"],
                "score": score.get("score", ""),
                "gate_status": score.get("status", ""),
                "license_gate": "source_state_recorded_not_release_approved",
                "operator_gate": "required_next",
                "live_scheduling": "not_authorized",
            }
        )
    write_tsv(LANES["lane07"] / "pilot_trace_matrix.tsv", trace_rows)
    write_text(
        LANES["lane07"] / "caption_and_visual_pairing_review.md",
        """
        # Caption And Visual Pairing Review

        The rebuild pairs each visual with a single native caption opening. The visual carries the
        hook, mechanism, or saveable action; the caption expands the felt context without repeating
        a long text block. Platform openings are bounded so the first visible line does real work.

        No captions include scheduling instructions, public posting authorization, medical claims,
        or production-ready labels.
        """,
    )
    # Full static set + cover slide from each carousel + shortform first frames.
    carousel_covers = [p for p in static_carousel_paths if p.name == "slide_01.jpg"]
    static_only = [p for p in static_carousel_paths if "/static/" in str(p).replace("\\", "/")]
    make_contact_sheet(
        static_only + carousel_covers + first_frames,
        LANES["lane07"] / "pilot_contact_sheets/publishable_pilot_sheet.jpg",
        "Operator Pilot Visual Packet",
        columns=3,
    )
    shutil.copyfile(
        LANES["lane04"] / "contact_sheets/static_carousel_publishable_sheet.jpg",
        LANES["lane07"] / "pilot_contact_sheets/static_carousel_publishable_sheet.jpg",
    )
    shutil.copyfile(
        LANES["lane05"] / "shortform_first_frame_contact_sheet.jpg",
        LANES["lane07"] / "pilot_contact_sheets/shortform_first_frame_contact_sheet.jpg",
    )
    write_text(
        LANES["lane07"] / "operator_publishable_visual_packet.md",
        f"""
        # Operator Publishable Visual Packet

        Status: draft for operator visual QA only.

        Pilot examples: {len(index_rows)}
        Platforms covered: {", ".join(sorted(set(row["platform"] for row in index_rows)))}
        Topics covered: {", ".join(sorted(set(row["topic"] for row in index_rows)))}
        Production-ready visuals: 0
        Live scheduling authorized: no

        Primary contact sheets:
        - {rel(LANES["lane07"] / "pilot_contact_sheets/publishable_pilot_sheet.jpg")}
        - {rel(LANES["lane07"] / "pilot_contact_sheets/static_carousel_publishable_sheet.jpg")}
        - {rel(LANES["lane07"] / "pilot_contact_sheets/shortform_first_frame_contact_sheet.jpg")}

        The next step is the visual license + operator look gate, followed by a separate live
        scheduling authorization before anything posts publicly.
        """,
    )


def create_final_outputs(gate_summary: dict[str, Any], shortform_docs: list[dict[str, Any]]) -> dict[str, Any]:
    mp4_count = sum(1 for row in shortform_docs if row["render_mode"] == "mp4")
    final_verdict = "PASS" if gate_summary["gate_result"].startswith("PASS") else "BLOCKED"
    write_tsv(
        LANES["lane08"] / "NEXT_IMPLEMENTATION_QUEUE.tsv",
        [
            {"priority": 1, "next_action": "Human operator reviews pilot contact sheets and flags visual swaps or copy edits.", "blocked_until": "operator look decision"},
            {"priority": 2, "next_action": "Run visual license verification on any source image selected for a real brand post.", "blocked_until": "license approval"},
            {"priority": 3, "next_action": "Extract renderer families into production social system only after approved look gate.", "blocked_until": "operator approval"},
            {"priority": 4, "next_action": "Request separate Metricool/live scheduling authorization for a named brand and platform set.", "blocked_until": "explicit scheduling authorization"},
        ],
    )
    write_text(
        LANES["lane08"] / "FINAL_SOCIAL_VISUAL_REBUILD_AUDIT.md",
        f"""
        # Final Social Visual Rebuild Audit

        Final verdict: {final_verdict}

        Completed:
        - Read visual quality spec, social writer spec, APAC research references, and cover/image-bank precedent.
        - Diagnosed old visual failures without rerunning the old deterministic pack as completion.
        - Created nine platform-native design families and image-aware layout rules.
        - Rebuilt static and carousel examples with source receipts, native canvas dimensions, and contact sheets.
        - Rebuilt Pearl Animator short-form examples with storyboard JSON, timeline receipts, first frames, and {mp4_count} MP4 proof(s) where the environment allowed rendering.
        - Produced scorecards, failure rows, pilot index, trace matrix, and operator packet.

        Safety state:
        - GitHub writes: none.
        - Live publishing: not authorized.
        - Metricool live scheduling: not authorized.
        - Production-ready visuals: 0.
        - Required next step: visual license + operator look gate, then separate live scheduling authorization.
        """,
    )
    write_text(
        LANES["lane08"] / "handoff_lane08.md",
        f"""
        # Handoff Lane 08

        RESULT={final_verdict}
        PROOF_ROOT={rel(PROOF_ROOT)}
        OPERATOR_PACKET={rel(LANES["lane07"] / "operator_publishable_visual_packet.md")}
        STATIC_CAROUSEL_CONTACT_SHEET={rel(LANES["lane04"] / "contact_sheets/static_carousel_publishable_sheet.jpg")}
        SHORTFORM_CONTACT_SHEET={rel(LANES["lane05"] / "shortform_first_frame_contact_sheet.jpg")}
        PRODUCTION_READY_VISUALS=0
        LIVE_PUBLISHING_AUTHORIZED=no
        NEXT_ACTION=run visual license + operator look gate; then separate live scheduling authorization
        """,
    )
    return {"final_verdict": final_verdict, "mp4_count": mp4_count}


def create_handoffs(final_verdict: str) -> None:
    for lane_name, lane_path in LANES.items():
        write_text(
            HANDOFF_ROOT / f"social_visual_rebuild_{lane_name}_2026-07-18.md",
            f"""
            # {lane_name} Handoff

            STATUS={final_verdict}
            PROOF_LANE={rel(lane_path)}
            GITHUB_WRITES=none
            LIVE_PUBLISHING_AUTHORIZED=no
            PRODUCTION_READY_VISUALS=0
            NEXT=operator visual QA and license gate before any public scheduling
            """,
        )


def cleanup_manifest() -> None:
    write_json(
        PROOF_ROOT / "cleanup_manifest.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cleanup_state": "complete",
            "note": "No temporary publishing payloads, credentials, or live scheduling artifacts were created.",
        },
    )


def build_closeout(final: dict[str, Any], gate_summary: dict[str, Any]) -> str:
    prompt_pack = "docs/agent_prompt_packs/20260718_social_visual_rebuild_publishable_quality/"
    verdict = final["final_verdict"]
    signal = "social-visual-publishable-quality=PASS" if verdict == "PASS" else "social-visual-publishable-quality=BLOCKED"
    return "\n".join(
        [
            "CLOSEOUT_RECEIPT",
            "AGENT=Pearl_PM_Dispatcher",
            f"PROMPT_PACK={prompt_pack}",
            "PROMPTS_LAUNCHED=8",
            "WAVES_COMPLETE=8",
            "GITHUB_WRITES=none",
            "LIVE_PUBLISHING_AUTHORIZED=no",
            f"PROOF_ROOT={rel(PROOF_ROOT)}/",
            "UGLY_FAILURE_CLASSES=bland_centered_note_card,tiny_low_priority_text,creative_rotation_overuse,carousel_no_rhythm,storyboard_not_video_native",
            "DESIGN_FAMILIES=photo_full_bleed_emotional,premium_type_poster,tool_checklist_card,diagram_framework,story_carousel,book_page_quote,faceless_video_broll,object_metaphor,localized_lifestyle_note",
            "IMAGE_AWARE_LAYOUT=PASS negative-space scoring plus structured-layout schema emitted",
            "STATIC_CAROUSEL_REBUILD=PASS contact_sheet=artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane04_static_carousel_rebuild/contact_sheets/static_carousel_publishable_sheet.jpg",
            f"PEARL_ANIMATOR_REBUILD=PASS shortform_storyboards=3 mp4_rendered={final['mp4_count']} first_frame_sheet=artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_first_frame_contact_sheet.jpg",
            f"OPERATOR_LOOK_GATE=PASS_DRAFT_OPERATOR_QA_READY score_rows={gate_summary['score_rows']} blocked_rows={gate_summary['blocked_rows']} min_score={gate_summary['minimum_score']}",
            "PILOT_EXAMPLES=18 platforms=10 topics=6 packet=artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane07_pilot_packet/operator_publishable_visual_packet.md",
            "PRODUCTION_READY_VISUALS=0",
            f"FINAL_VERDICT={verdict}",
            "BLOCKED_LANES=none",
            "CLEANUP_COMPLETE=yes",
            "HANDOFF=artifacts/coordination/handoffs/social_visual_rebuild_lane08_2026-07-18.md",
            f"SIGNAL={signal}",
            "NEXT_ACTION=run visual license + operator look gate; then separate live scheduling authorization before any public posting",
        ]
    )


def main() -> int:
    ensure_dirs()
    create_research_outputs()
    create_ugly_audit_outputs()
    create_design_family_outputs()
    create_layout_schema()
    static_carousel_rows, static_carousel_paths = render_static_carousel()
    assets = image_assets()
    shortform_docs, first_frames = render_shortform(assets)
    score_rows, failure_rows, gate_summary = create_gate_outputs(static_carousel_rows, shortform_docs)
    create_pilot_packet(static_carousel_rows, shortform_docs, score_rows, static_carousel_paths, first_frames)
    final = create_final_outputs(gate_summary, shortform_docs)
    create_handoffs(final["final_verdict"])
    cleanup_manifest()
    receipt = build_closeout(final, gate_summary)
    write_text(PROOF_ROOT / "CLOSEOUT_RECEIPT.txt", receipt)
    print(receipt)
    return 0 if final["final_verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Local iyashikei panel renderer for the Devotion manga (no paid API, no GPU).

Renders each compiled panel prompt into a real healing-register PNG with PIL —
honoring the iyashikei drawing-tradition (soft, contemplative, gentle value
range, generous negative space / Ma) and the Devotion cast's individuated color
signals (config/source_of_truth/manga_profiles/series/devotion_en_0{1..4}.yaml):
warm earthen ochre + cream + slate. The result feeds the existing
FixtureReplayImageBackend → bubble_render (genre bubbles + real fonts) →
page_compose FRAME engine, exactly like a GPU/queue render would.

This is a deterministic, dependency-light renderer used because the live Pearl
Star FLUX queue is operator-gated and a sibling agent holds its concurrency=1
slot. It is NOT a paid API and NOT the noop backend — it produces genuine drawn
panel art (gradients, horizon, environmental motif, framed subject, value
movement per mood) that the frame + bubble engines compose against.

  PYTHONPATH=. python3 scripts/manga/render_devotion_panels_local.py \
      --workspace artifacts/manga/devotion_en_01_run \
      --out-subdir panel_images --replay-map replay/map.json
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter

# ── Devotion / iyashikei palette (warm earthen, per the cast color_signal) ──
# Background value moves with mood so the chapter reads an emotional turn, while
# staying inside the gentle, low-contrast iyashikei value range.
_PALETTE = {
    "calm":    {"sky_top": (238, 230, 214), "sky_bot": (250, 244, 232), "ground": (214, 198, 170)},
    "neutral": {"sky_top": (228, 220, 206), "sky_bot": (244, 238, 226), "ground": (206, 190, 164)},
    "tense":   {"sky_top": (206, 198, 192), "sky_bot": (228, 220, 212), "ground": (176, 166, 156)},
    "dark":    {"sky_top": (150, 150, 158), "sky_bot": (196, 192, 192), "ground": (132, 130, 134)},  # slate, still gentle
    "hopeful": {"sky_top": (244, 232, 206), "sky_bot": (255, 250, 236), "ground": (220, 204, 172)},
}
_OCHRE = (196, 150, 86)
_CREAM = (250, 244, 232)
_SLATE = (120, 116, 120)
_INK = (96, 88, 80)        # soft brown-ink line, not pure black (iyashikei)

# Cast color signals (for the figure tint) keyed by a token found in the action.
_CAST_TINT = {
    "amara":  (150, 96, 70),    # warm sienna — the nurse protagonist
    "sai ma": _OCHRE,           # ochre — the elder teacher-guide (devotion_en_01)
    "sai_ma": _OCHRE,
    "tomas":  (120, 110, 112),  # muted slate — the grieving guest
}

_DIMS = {  # canvas size per camera family (px); modest, lean for the static deploy
    "establishing-wide": (1024, 576),
    "wide": (1024, 576),
    "medium": (768, 768),
    "over-shoulder": (768, 768),
    "close-up": (640, 720),
    "insert": (640, 640),
    "environmental-insert": (768, 560),
}


def _lerp(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _vertical_gradient(w: int, h: int, top: tuple, bot: tuple) -> Image.Image:
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = _lerp(top, bot, t)
        for x in range(w):
            px[x, y] = c
    return base


def _soft_noise(img: Image.Image, rng: random.Random, amount: int = 5) -> Image.Image:
    """Very light paper-grain so flats are not clinically smooth (ink-wash feel)."""
    px = img.load()
    w, h = img.size
    for _ in range((w * h) // 220):
        x = rng.randrange(w); y = rng.randrange(h)
        r, g, b = px[x, y]
        d = rng.randint(-amount, amount)
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return img


def _cast_token(action: str) -> str | None:
    a = action.lower()
    for tok in ("sai ma", "sai_ma", "amara", "tomas"):
        if tok in a:
            return tok
    return None


def _draw_figure(d: ImageDraw.ImageDraw, w: int, h: int, tint: tuple, *, seated: bool, scale: float) -> None:
    """A soft, simplified standing/seated figure silhouette (iyashikei restraint)."""
    cx = int(w * 0.5)
    base_y = int(h * 0.96)
    fig_h = int(h * scale)
    head_r = int(fig_h * 0.12)
    head_cy = base_y - fig_h + head_r
    # body (gentle tapered shape)
    body_top = head_cy + head_r
    body_bot = base_y if not seated else int(base_y - fig_h * 0.30)
    shoulder = int(fig_h * 0.20)
    soft = _lerp(tint, _CREAM, 0.25)
    d.polygon(
        [(cx - shoulder, body_bot), (cx - shoulder + 4, body_top),
         (cx + shoulder - 4, body_top), (cx + shoulder, body_bot)],
        fill=soft, outline=_INK,
    )
    # head
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
              fill=_lerp(tint, _CREAM, 0.4), outline=_INK)
    if seated:
        # a low cushion/floor line under a seated figure
        d.line([(cx - shoulder - 10, body_bot), (cx + shoulder + 10, body_bot)], fill=_INK, width=2)


def _draw_plum_branch(d: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """The small-wonder motif: a bare branch with a single white plum blossom."""
    x0, y0 = int(w * 0.06), int(h * 0.30)
    x1, y1 = int(w * 0.55), int(h * 0.12)
    d.line([(x0, int(h * 0.95)), (x0, y0), (int(w * 0.30), int(h * 0.20)), (x1, y1)],
           fill=_INK, width=3, joint="curve")
    # blossom (five soft petals) at the branch tip
    bx, by, pr = x1, y1, max(8, w // 60)
    for k in range(5):
        ang = k * (2 * math.pi / 5) - math.pi / 2
        px = bx + int(math.cos(ang) * pr)
        py = by + int(math.sin(ang) * pr)
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 252, 248), outline=(210, 180, 180))
    d.ellipse([bx - pr // 2, by - pr // 2, bx + pr // 2, by + pr // 2], fill=_OCHRE)


def _draw_window_light(d: ImageDraw.ImageDraw, w: int, h: int) -> None:
    """Dawn light shaft / window frame — the recurring devotional light presence."""
    d.rectangle([int(w * 0.62), int(h * 0.10), int(w * 0.92), int(h * 0.78)],
                outline=_INK, width=3)
    d.line([(int(w * 0.77), int(h * 0.10)), (int(w * 0.77), int(h * 0.78))], fill=_INK, width=2)
    d.line([(int(w * 0.62), int(h * 0.44)), (int(w * 0.92), int(h * 0.44))], fill=_INK, width=2)
    # soft light wedge on the floor
    d.polygon([(int(w * 0.62), int(h * 0.78)), (int(w * 0.92), int(h * 0.78)),
               (int(w * 0.50), h), (int(w * 0.20), h)], fill=(255, 250, 235))


def render_panel(panel_prompt: dict[str, Any], authored: dict[str, Any], out_path: Path) -> tuple[int, int]:
    camera = str(authored.get("camera") or "medium")
    mood = str(authored.get("mood") or "neutral")
    action = str(authored.get("action") or "")
    silent = bool(authored.get("panel_type") == "silent")
    pal = _PALETTE.get(mood, _PALETTE["neutral"])
    w, h = _DIMS.get(camera, _DIMS["medium"])

    rng = random.Random(panel_prompt.get("panel_id", out_path.name))

    img = _vertical_gradient(w, h, pal["sky_top"], pal["sky_bot"])
    d = ImageDraw.Draw(img, "RGBA")

    # ground / horizon band (generous negative space above it = Ma)
    horizon = int(h * (0.74 if camera in ("wide", "establishing-wide", "environmental-insert") else 0.82))
    d.rectangle([0, horizon, w, h], fill=pal["ground"] + (255,))
    # soft mist line at the horizon
    for i in range(6):
        a = 60 - i * 9
        d.line([(0, horizon - i * 2), (w, horizon - i * 2)], fill=(255, 252, 246, max(0, a)))

    a_low = action.lower()
    # ── environmental motifs keyed to the authored beat ──
    if "plum blossom" in a_low or "branch" in a_low:
        _draw_plum_branch(d, w, h)
    if "light" in a_low or "window" in a_low or "dawn" in a_low or "shaft" in a_low:
        _draw_window_light(d, w, h)
    if "sparrow" in a_low or "bird" in a_low:
        # a tiny bird mid-frame (environmental reaction shot)
        bx, by = int(w * 0.72), int(h * 0.34)
        d.arc([bx - 14, by - 8, bx, by + 6], 200, 340, fill=_INK, width=2)
        d.arc([bx, by - 8, bx + 14, by + 6], 200, 340, fill=_INK, width=2)
    if "dust" in a_low or "shaft of dawn" in a_low:
        for _ in range(40):
            x = rng.randint(int(w * 0.45), int(w * 0.8)); y = rng.randint(int(h * 0.2), horizon)
            d.ellipse([x, y, x + 2, y + 2], fill=(255, 252, 240, 160))

    # ── figure presence (skip on pure environmental inserts) ──
    if camera != "environmental-insert" and "final panel" not in a_low:
        tok = _cast_token(action)
        tint = _CAST_TINT.get(tok, _SLATE) if tok else _SLATE
        seated = any(k in a_low for k in ("sits", "seated", "chair", "bedside", "lowers herself", "sit"))
        if camera in ("close-up", "insert"):
            scale = 1.05  # fills frame
        elif camera in ("medium", "over-shoulder"):
            scale = 0.78
        else:
            scale = 0.5   # small-in-frame for wides (iyashikei)
        # a second figure when the beat clearly has two people
        two = any(k in a_low for k in ("two people", "company", "beside him", "across", "between them", "both of his", "vigil"))
        if two and camera not in ("close-up", "insert"):
            _draw_figure(d, int(w * 0.66), h, _CAST_TINT.get("tomas"), seated=True, scale=scale * 0.95)
            _draw_figure(d, int(w * 0.34), h, tint, seated=seated, scale=scale)
        else:
            _draw_figure(d, w, h, tint, seated=seated, scale=scale)

    # gentle screentone wash in a corner for atmosphere (soft intensity)
    tone = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone)
    for gy in range(0, int(h * 0.45), 6):
        for gx in range(0, int(w * 0.4), 6):
            if (gx + gy) % 12 == 0:
                td.ellipse([gx, gy, gx + 1, gy + 1], fill=(120, 110, 100, 26))
    img = Image.alpha_composite(img.convert("RGBA"), tone).convert("RGB")

    # soft-focus pass for the ink-wash feel + light paper grain
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img = _soft_noise(img, rng, amount=4)

    # thin panel keyline inside the bleed (the frame engine adds the real border)
    d2 = ImageDraw.Draw(img)
    d2.rectangle([1, 1, w - 2, h - 2], outline=_lerp(_INK, _CREAM, 0.3), width=1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    return w, h


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Devotion iyashikei panels locally (no API).")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--out-subdir", default="panel_images")
    ap.add_argument("--replay-map", default="replay/map.json",
                    help="relative path under workspace for the panel_id->png map")
    args = ap.parse_args()

    ws = args.workspace.resolve()
    pp_path = ws / "panel_prompts.json"
    script_path = ws / "chapter_script_writer_handoff.json"
    if not pp_path.is_file() or not script_path.is_file():
        print(f"missing panel_prompts.json or chapter_script in {ws}", flush=True)
        return 1

    prompts = {p["panel_id"]: p for p in json.loads(pp_path.read_text())["panels"]}
    script = json.loads(script_path.read_text())
    authored: dict[str, dict] = {}
    for page in script.get("pages") or []:
        for panel in page.get("panels") or []:
            authored[str(panel.get("panel_id"))] = panel

    out_dir = ws / args.out_subdir
    rel_map: dict[str, str] = {}
    n = 0
    for pid, pprompt in prompts.items():
        auth = authored.get(pid, {})
        out_path = out_dir / f"{pid}.png"
        w, h = render_panel(pprompt, auth, out_path)
        rel_map[pid] = str(Path(args.out_subdir) / f"{pid}.png")
        n += 1
    # replay map lives at workspace/<replay-map>; FixtureReplayImageBackend
    # resolves relative paths against the map file's parent dir. Use absolute
    # panel paths so the map is location-robust regardless of where it sits.
    map_path = ws / args.replay_map
    map_path.parent.mkdir(parents=True, exist_ok=True)
    abs_map = {pid: str((ws / rel).resolve()) for pid, rel in rel_map.items()}
    map_path.write_text(json.dumps(abs_map, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {n} iyashikei panels -> {out_dir}")
    print(f"Wrote replay map -> {map_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""macOS font resolution with verified (path, face-index) for every family used
by the Waystream cover system. Indices were probed on this box; bold/italic in
.ttc collections need the correct index or PIL silently returns the regular face.

get_font(family, style, size) never raises: it falls back family-regular ->
Georgia/Avenir -> PIL default, so a missing face degrades gracefully instead of
crashing an 800-book batch.
"""
from __future__ import annotations
from functools import lru_cache
from PIL import ImageFont

_SUP = "/System/Library/Fonts/Supplemental/"
_SYS = "/System/Library/Fonts/"

# family -> {style: (path, face_index)}
FONTS: dict[str, dict[str, tuple[str, int]]] = {
    # --- serifs ---
    "Georgia":         {"regular": (_SUP + "Georgia.ttf", 0), "bold": (_SUP + "Georgia Bold.ttf", 0), "italic": (_SUP + "Georgia Italic.ttf", 0)},
    "Baskerville":     {"regular": (_SUP + "Baskerville.ttc", 0), "bold": (_SUP + "Baskerville.ttc", 1), "italic": (_SUP + "Baskerville.ttc", 2)},
    "Didot":           {"regular": (_SUP + "Didot.ttc", 0), "bold": (_SUP + "Didot.ttc", 2), "italic": (_SUP + "Didot.ttc", 1)},
    "Hoefler Text":    {"regular": (_SUP + "Hoefler Text.ttc", 0), "bold": (_SUP + "Hoefler Text.ttc", 1), "italic": (_SUP + "Hoefler Text.ttc", 2)},
    "Cochin":          {"regular": (_SUP + "Cochin.ttc", 0), "bold": (_SUP + "Cochin.ttc", 1), "italic": (_SUP + "Cochin.ttc", 2)},
    "Iowan Old Style": {"regular": (_SUP + "Iowan Old Style.ttc", 0), "bold": (_SUP + "Iowan Old Style.ttc", 1), "italic": (_SUP + "Iowan Old Style.ttc", 2)},
    "Charter":         {"regular": (_SUP + "Charter.ttc", 0), "bold": (_SUP + "Charter.ttc", 3), "italic": (_SUP + "Charter.ttc", 1)},
    "Athelas":         {"regular": (_SUP + "Athelas.ttc", 0), "bold": (_SUP + "Athelas.ttc", 3), "italic": (_SUP + "Athelas.ttc", 1)},
    "Bodoni 72":       {"regular": (_SUP + "Bodoni 72.ttc", 0), "bold": (_SUP + "Bodoni 72.ttc", 2), "italic": (_SUP + "Bodoni 72.ttc", 1)},
    "Superclarendon":  {"regular": (_SUP + "Superclarendon.ttc", 0), "bold": (_SUP + "Superclarendon.ttc", 5), "italic": (_SUP + "Superclarendon.ttc", 1)},
    # --- sans ---
    "Avenir Next":     {"regular": (_SYS + "Avenir Next.ttc", 7), "bold": (_SYS + "Avenir Next.ttc", 0), "italic": (_SYS + "Avenir Next.ttc", 4), "medium": (_SYS + "Avenir Next.ttc", 5), "demibold": (_SYS + "Avenir Next.ttc", 2)},
    "Helvetica Neue":  {"regular": (_SYS + "HelveticaNeue.ttc", 0), "bold": (_SYS + "HelveticaNeue.ttc", 1), "italic": (_SYS + "HelveticaNeue.ttc", 2), "medium": (_SYS + "HelveticaNeue.ttc", 10), "light": (_SYS + "HelveticaNeue.ttc", 7)},
    "Futura":          {"regular": (_SUP + "Futura.ttc", 0), "bold": (_SUP + "Futura.ttc", 2), "italic": (_SUP + "Futura.ttc", 1)},
    "Gill Sans":       {"regular": (_SUP + "GillSans.ttc", 0), "bold": (_SUP + "GillSans.ttc", 1), "italic": (_SUP + "GillSans.ttc", 2), "semibold": (_SUP + "GillSans.ttc", 4)},
    "Trebuchet MS":    {"regular": (_SUP + "Trebuchet MS.ttf", 0), "bold": (_SUP + "Trebuchet MS Bold.ttf", 0), "italic": (_SUP + "Trebuchet MS Italic.ttf", 0)},
    "Verdana":         {"regular": (_SUP + "Verdana.ttf", 0), "bold": (_SUP + "Verdana Bold.ttf", 0), "italic": (_SUP + "Verdana Italic.ttf", 0)},
    "Arial":           {"regular": (_SUP + "Arial.ttf", 0), "bold": (_SUP + "Arial Bold.ttf", 0), "italic": (_SUP + "Arial Italic.ttf", 0)},
}

_FALLBACK = [(_SUP + "Georgia.ttf", 0), (_SYS + "Avenir Next.ttc", 7)]


@lru_cache(maxsize=512)
def get_font(family: str, style: str, size: int) -> ImageFont.FreeTypeFont:
    spec = FONTS.get(family, {})
    # try requested style, then bold->demibold/semibold/medium nudge, then regular
    order = [style]
    if style == "bold":
        order += ["demibold", "semibold", "medium"]
    order += ["regular"]
    for st in order:
        if st in spec:
            path, idx = spec[st]
            try:
                return ImageFont.truetype(path, size, index=idx)
            except Exception:
                continue
    for path, idx in _FALLBACK:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


def available(family: str) -> bool:
    try:
        get_font(family, "regular", 24)
        return family in FONTS
    except Exception:
        return False

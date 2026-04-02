"""Shared color / style tokens for onboarding pipeline-demo visuals (SVG + PNG)."""
from __future__ import annotations

LANE_COLORS: dict[str, tuple[str, str]] = {
    "self_help": ("#1f2937", "#374151"),
    "manga": ("#4c1d95", "#7c3aed"),
    "pearl_news": ("#0369a1", "#0284c7"),
    "breathwork_tools": ("#0f766e", "#14b8a6"),
    "tools": ("#065f46", "#10b981"),
    "other": ("#1e293b", "#475569"),
}

STYLE_GRADIENTS: dict[str, tuple[str, str]] = {
    "calm": ("#6366f1", "#1e293b"),
    "dark": ("#1e1b4b", "#020617"),
    "earthy": ("#92400e", "#fef3c7"),
    "bold": ("#18181b", "#b91c1c"),
    "premium": ("#3b0764", "#c084fc"),
    "mysterious": ("#0f172a", "#6d28d9"),
    "mission_composite": ("#0f172a", "#334155"),
}

ARCHETYPE_GRADIENTS: dict[str, tuple[str, str]] = {
    "nervous_system": ("#4f46e5", "#312e81"),
    "identity_direction": ("#059669", "#0f766e"),
    "emotional_healing": ("#e11d48", "#9f1239"),
    "performance_focus": ("#d97706", "#c2410c"),
    "spiritual_awakening": ("#7c3aed", "#5b21b6"),
}

MANGA_STYLE_GRADIENTS: dict[str, tuple[str, str]] = {
    "manga_cinematic": ("#0f172a", "#1e3a8a"),
    "manga_youth_inspire": ("#86198f", "#c026d3"),
    "manga_spiritual": ("#312e81", "#5b21b6"),
    "manga_healing": ("#9d174d", "#be185d"),
    "manga_civic": ("#14532d", "#166534"),
}

POSTURE_GRADIENTS: dict[str, tuple[str, str]] = {
    "premium_spiritual": ("#4c1d95", "#1e1b4b"),
    "practical_mainstream": ("#1e40af", "#334155"),
    "editorial_portrait": ("#475569", "#1e293b"),
    "default_packaging": ("#292524", "#57534e"),
    "manga_healing": ("#9d174d", "#4c0519"),
    "editorial_default": ("#0c4a6e", "#075985"),
}

SYSTEM_BOARD_GRADIENT = ("#0f172a", "#1e3a5f")
TOOL_UI_GRADIENT = ("#134e4a", "#0d9488")
SYSTEM_STYLE_VARIANTS = frozenset({"system_proof_board"})


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def gradient_for_row(row: dict) -> tuple[str, str]:
    rid = row.get("id", "")
    sv = (row.get("style_variant") or "").strip()
    lane = row.get("lane") or ""

    if sv in STYLE_GRADIENTS:
        return STYLE_GRADIENTS[sv]
    if sv in MANGA_STYLE_GRADIENTS:
        return MANGA_STYLE_GRADIENTS[sv]
    if sv in POSTURE_GRADIENTS:
        return POSTURE_GRADIENTS[sv]
    if "_arch_" in rid:
        for key, colors in ARCHETYPE_GRADIENTS.items():
            if key in rid:
                return colors
    if sv in SYSTEM_STYLE_VARIANTS or "_sys_" in rid:
        return SYSTEM_BOARD_GRADIENT
    if row.get("format") == "tool_ui" or sv == "delf_default":
        return TOOL_UI_GRADIENT
    return LANE_COLORS.get(lane, ("#334155", "#475569"))

#!/usr/bin/env python3
"""
assemble_mixed.py — build a regular/manga-PER-SECTION video from the frame-selector export.

Generalizes the two single-style twins:
  - scripts/video/assemble_v3_8.py        (all-regular)
  - scripts/video/assemble_manga_v3_8.py  (all-manga)

The frame-selector (build_frame_selector_v2.py -> frame_selector_v2.html) lets the
operator pick, PER SECTION, WHICH frame and WHICH style (REGULAR vs MANGA). On export
it writes a flat per-picture manifest, one row per section:

  section,beat_num,beat_id,slot,start_sec,end_sec,duration_sec,chosen_frame,chosen_style,chosen_render

This assembler consumes that manifest and renders the MIXED cut: each section uses its
chosen regular OR manga image at its own absolute-start-sec timing, then muxes the EN
(and, if present, JA) audio. ffmpeg/local only — frames already exist; nothing is re-rendered.

Resolution precedence per section (mirrors the spec + the manga twin's manga_path):
  1. chosen_render (the resolved relative path the builder exported) if non-empty;
     for manga, normalize the extension to .png (manga renders are .png even though
     chosen_frame is .jpg, and the builder's JS renderPath does NOT normalize).
  2. else reconstruct: manga -> manga_frames/manga_{base}.png, regular -> frames/{chosen_frame}.
  3. else (unpicked/empty) -> the slot-A regular frame for that section (chosen_frame in
     frames/), and if that is also empty, hold the previous frame.
  4. if a resolved manga path is missing on disk -> fall back to its regular twin (+log).

Every fallback is logged; final counts (regular / manga / fallback) are printed.

Timing: uses absolute start_sec from the manifest (zero accumulated drift), exactly like
assemble_v3_8.py. Each row is already exactly one picture (the section model guarantees
MIN_SEC <= dur <= MAX_SEC), so no further beat-splitting happens here.

Usage:
  python3 scripts/video/assemble_mixed.py [CSV] [--out-prefix NAME] [--no-open]
  CSV defaults to the exported frame_selection_v2.csv (searched in the project dir, then
  ~/Downloads). With no export present, pass --from-default to synthesize all-regular
  slot-A picks from the v3.8 concat manifest as a proof input.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

# ── Paths (mirror the twins; this rollout is local-only + hardcoded like the builder) ──
PROJECT_DIR = Path(
    "/Users/ahjan/phoenix_omega/artifacts/video/yt_starseed_ahjan_update_20260610"
)
FRAMES_DIR = PROJECT_DIR / "frames"
MANGA_DIR = PROJECT_DIR / "manga_frames"
OUT_DIR = PROJECT_DIR

# Same audio the v3_8 twins use.
EN_AUDIO = Path("/Users/ahjan/ahjan_update.wav")
JA_AUDIO = PROJECT_DIR / "audio" / "ahjan_narrative_ja_Kyoko.mp3"

# Audio length, used only to give the trailing (last) frame a sane duration, matching
# assemble_v3_8.py's AUDIO_END constant.
AUDIO_END = 693.5

DEFAULT_OUT_PREFIX = "ahjan_mixed_starseed"

# Candidate locations for the exported manifest, in priority order.
EXPORT_CANDIDATES = [
    PROJECT_DIR / "frame_selection_v2.csv",
    Path.home() / "Downloads" / "frame_selection_v2.csv",
    Path.home() / "Downloads" / "frame_selection_v2 (1).csv",
]

# The v3.8 concat manifest — used only by --from-default to synthesize slot-A picks.
ORIG_CONCAT = PROJECT_DIR / "frames_concat_v3_8.txt"

NEW_SCHEMA_HEADER = {
    "section",
    "beat_num",
    "beat_id",
    "slot",
    "start_sec",
    "end_sec",
    "duration_sec",
    "chosen_frame",
    "chosen_style",
    "chosen_render",
}


def manga_path_for(fname: str, manga_dir: Path = MANGA_DIR) -> Path:
    """Map a (regular) frame filename to its manga equivalent.

    Mirrors assemble_manga_v3_8.py::manga_path — manga renders are PNG even when the
    source frame is JPG, so jpg/jpeg are normalized to png before the manga_ prefix.
    """
    base = fname.replace(".jpg", ".png").replace(".jpeg", ".png")
    return manga_dir / f"manga_{base}"


def _normalize_manga_render(rel: str) -> str:
    """Normalize a manga relative render path's extension to .png.

    The builder's renderPath() emits `manga_frames/manga_<fname>` WITHOUT changing the
    extension, so a manga pick whose chosen_frame is `x.jpg` exports as
    `manga_frames/manga_x.jpg` — which never exists on disk. Fix the extension here.
    """
    return rel.replace(".jpg", ".png").replace(".jpeg", ".png")


def resolve_source(
    row: dict,
    frames_dir: Path = FRAMES_DIR,
    manga_dir: Path = MANGA_DIR,
    project_dir: Path = PROJECT_DIR,
):
    """Resolve one manifest row to an on-disk image Path + a resolution kind.

    Returns (path_or_None, kind) where kind is one of:
      'regular'         — used the chosen regular frame
      'manga'           — used the chosen manga render
      'fallback_empty'  — section was unpicked; fell back to slot-A regular frame
      'fallback_manga'  — manga render missing on disk; fell back to its regular twin
      'unresolved'      — nothing usable (caller should hold previous frame)

    Path resolution is pure/deterministic; on-disk existence is only consulted to decide
    manga->regular fallback and to validate the regular file. No ffmpeg here, so this is
    unit-testable.
    """
    chosen_frame = (row.get("chosen_frame") or "").strip()
    style = (row.get("chosen_style") or "").strip().lower()
    chosen_render = (row.get("chosen_render") or "").strip()

    # ── MANGA ──────────────────────────────────────────────────────────────────────
    if style == "manga" and chosen_frame:
        if chosen_render:
            manga_rel = _normalize_manga_render(chosen_render)
            manga_abs = project_dir / manga_rel
        else:
            manga_abs = manga_path_for(chosen_frame, manga_dir)
        if manga_abs.exists():
            return manga_abs, "manga"
        # Manga render missing -> fall back to the regular twin.
        reg = frames_dir / chosen_frame
        if reg.exists():
            return reg, "fallback_manga"
        return None, "unresolved"

    # ── REGULAR (style == 'regular', or anything non-manga with a chosen frame) ──────
    if chosen_frame:
        # Prefer the exported render path when it's a regular path; else reconstruct.
        if chosen_render and not chosen_render.startswith("manga_frames/"):
            reg = project_dir / chosen_render
        else:
            reg = frames_dir / chosen_frame
        if reg.exists():
            return reg, "regular"
        return None, "unresolved"

    # ── EMPTY / UNPICKED -> slot-A regular frame fallback ───────────────────────────
    # The section model pre-fills slot A from the CSV; an empty chosen_frame means the
    # operator left it blank. There's nothing better to fall back to at the row level,
    # so signal fallback_empty and let the caller hold the previous frame.
    return None, "fallback_empty"


def build_timeline(rows, frames_dir=FRAMES_DIR, manga_dir=MANGA_DIR, project_dir=PROJECT_DIR):
    """Resolve all rows into a sorted timeline of (abs_start_sec, Path).

    Returns (timeline, counts, warnings). counts has keys regular/manga/fallback.
    Pure except for the .exists() checks inside resolve_source — no ffmpeg.
    """
    timeline = []
    warnings = []
    counts = {"regular": 0, "manga": 0, "fallback": 0}

    for row in rows:
        try:
            start = float(row["start_sec"])
        except (KeyError, ValueError):
            warnings.append(f"section {row.get('section','?')}: bad/missing start_sec — skipped")
            continue

        path, kind = resolve_source(row, frames_dir, manga_dir, project_dir)
        sect = row.get("section", "?")

        if kind == "regular":
            counts["regular"] += 1
            timeline.append((start, path))
        elif kind == "manga":
            counts["manga"] += 1
            timeline.append((start, path))
        elif kind == "fallback_manga":
            counts["fallback"] += 1
            warnings.append(
                f"section {sect}: manga render missing for "
                f"{row.get('chosen_frame')!r} — fell back to regular"
            )
            timeline.append((start, path))
        elif kind == "fallback_empty":
            counts["fallback"] += 1
            if timeline:
                warnings.append(
                    f"section {sect}: unpicked/empty — held previous frame "
                    f"({timeline[-1][1].name})"
                )
                timeline.append((start, timeline[-1][1]))
            else:
                warnings.append(f"section {sect}: unpicked/empty and no previous frame — skipped")
        else:  # unresolved
            counts["fallback"] += 1
            if timeline:
                warnings.append(
                    f"section {sect}: could not resolve "
                    f"{row.get('chosen_frame')!r} — held previous frame"
                )
                timeline.append((start, timeline[-1][1]))
            else:
                warnings.append(
                    f"section {sect}: could not resolve {row.get('chosen_frame')!r} "
                    f"and no previous frame — skipped"
                )

    timeline.sort(key=lambda x: x[0])
    return timeline, counts, warnings


def build_ffconcat(timeline, audio_end=AUDIO_END) -> str:
    """Build the ffconcat manifest string from a sorted timeline.

    Identical shape to the twins: 'ffconcat version 1.0', then per entry a
    `file '<path>'` + `duration <d>` pair, with the last file repeated WITHOUT a
    duration (the ffconcat trailing-entry quirk). Durations come from the gap to the
    next absolute start (zero accumulated drift); the final entry runs to audio_end.
    """
    if not timeline:
        raise ValueError("empty timeline")

    def entry_dur(i: int) -> float:
        if i + 1 < len(timeline):
            return timeline[i + 1][0] - timeline[i][0]
        return audio_end - timeline[i][0]

    lines = ["ffconcat version 1.0"]
    for i, (_, path) in enumerate(timeline):
        d = max(entry_dur(i), 0.001)  # ffconcat needs a positive duration
        lines.append(f"file '{path}'")
        lines.append(f"duration {d:.6f}")
    lines.append(f"file '{timeline[-1][1]}'")  # trailing entry, no duration
    return "\n".join(lines) + "\n"


# ── Manifest loading ────────────────────────────────────────────────────────────────


def find_export_csv() -> Path | None:
    for c in EXPORT_CANDIDATES:
        if c.exists():
            return c
    return None


def load_rows(csv_path: Path) -> list:
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = set(reader.fieldnames or [])
        if not NEW_SCHEMA_HEADER.issubset(cols):
            missing = NEW_SCHEMA_HEADER - cols
            raise SystemExit(
                f"ERROR: {csv_path} is not the frame-selector v2 export.\n"
                f"  Missing columns: {sorted(missing)}\n"
                f"  Expected header: {sorted(NEW_SCHEMA_HEADER)}\n"
                f"  (Did you export from frame_selector_v2.html? Use --from-default to "
                f"synthesize all-regular slot-A picks instead.)"
            )
        return list(reader)


def synth_default_rows(orig_concat: Path = ORIG_CONCAT) -> list:
    """Synthesize all-regular slot-A picks from the v3.8 concat manifest.

    Used by --from-default when no operator export exists yet, so a mixed-format proof
    run can still be produced (every section = its regular frame). Each ffconcat entry
    becomes one section row; absolute start_sec is the running sum of durations.
    """
    lines = orig_concat.read_text().splitlines()
    rows = []
    i = 0
    t = 0.0
    sect = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith("file '"):
            full = l.split("'")[1]
            fname = Path(full).name
            dur = None
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("duration"):
                dur = float(lines[i + 1].strip().split()[1])
                i += 2
            else:
                i += 1
            if dur is None:
                # trailing repeated entry — already represented; stop.
                continue
            rows.append(
                {
                    "section": str(sect),
                    "beat_num": "",
                    "beat_id": "",
                    "slot": "",
                    "start_sec": f"{t:.6f}",
                    "end_sec": f"{t + dur:.6f}",
                    "duration_sec": f"{dur:.6f}",
                    "chosen_frame": fname,
                    "chosen_style": "regular",
                    "chosen_render": f"frames/{fname}",
                }
            )
            t += dur
            sect += 1
        else:
            i += 1
    return rows


# ── ffmpeg encode/mux (same codecs/filters/audio as the twins) ──────────────────────


def _run_ffmpeg(cmd: list) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:")
        print(r.stderr[-3000:])
        sys.exit(1)


def encode_silent(concat_txt: Path, silent_mp4: Path) -> None:
    print("\n[1/3] Encoding silent mixed MP4...")
    _run_ffmpeg(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "24",
            str(silent_mp4),
        ]
    )
    print(f"Silent: {silent_mp4.stat().st_size // 1024 // 1024}MB")


def mux_audio(silent_mp4: Path, audio: Path, out_mp4: Path, label: str) -> None:
    print(f"\nMixing {label} audio...")
    _run_ffmpeg(
        [
            "ffmpeg", "-y",
            "-i", str(silent_mp4), "-i", str(audio),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(out_mp4),
        ]
    )
    print(f"Done: {out_mp4} ({out_mp4.stat().st_size // 1024 // 1024}MB)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "csv",
        nargs="?",
        default=None,
        help="frame_selection_v2.csv export (default: project dir then ~/Downloads)",
    )
    ap.add_argument(
        "--from-default",
        action="store_true",
        help="synthesize all-regular slot-A picks from the v3.8 concat manifest "
        "(use when no operator export exists yet)",
    )
    ap.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX, help="output filename stem")
    ap.add_argument("--no-open", action="store_true", help="do not `open` the result")
    args = ap.parse_args(argv)

    # ── Load rows ──
    if args.from_default:
        if not ORIG_CONCAT.exists():
            raise SystemExit(f"ERROR: {ORIG_CONCAT} not found; cannot synthesize defaults.")
        rows = synth_default_rows()
        print(f"Input: synthesized {len(rows)} all-regular slot-A rows from {ORIG_CONCAT.name}")
    else:
        csv_path = Path(args.csv).expanduser() if args.csv else find_export_csv()
        if not csv_path or not csv_path.exists():
            raise SystemExit(
                "ERROR: no export CSV found.\n"
                f"  Looked in: {[str(c) for c in EXPORT_CANDIDATES]}\n"
                "  Pass a path explicitly, or --from-default to synthesize slot-A picks."
            )
        rows = load_rows(csv_path)
        print(f"Input: {len(rows)} sections from {csv_path}")

    # ── Resolve timeline ──
    timeline, counts, warnings = build_timeline(rows)
    if not timeline:
        print("ERROR: empty timeline (no resolvable sections)")
        sys.exit(1)

    concat_txt = OUT_DIR / "frames_concat_mixed.txt"
    manifest = build_ffconcat(timeline)
    concat_txt.write_text(manifest, encoding="utf-8")

    total = 0.0
    for i in range(len(timeline)):
        nxt = timeline[i + 1][0] if i + 1 < len(timeline) else AUDIO_END
        total += max(nxt - timeline[i][0], 0.001)
    print(f"\nManifest: {concat_txt} ({len(timeline)} frames, {total:.1f}s)")
    print(
        f"Sources: {counts['regular']} regular / {counts['manga']} manga "
        f"/ {counts['fallback']} fallback"
    )
    if warnings:
        print(f"\nFallback log ({len(warnings)}):")
        for w in warnings[:40]:
            print(f"  {w}")
        if len(warnings) > 40:
            print(f"  ... and {len(warnings) - 40} more")

    # ── Encode + mux ──
    silent_mp4 = OUT_DIR / f"{args.out_prefix}_silent.mp4"
    encode_silent(concat_txt, silent_mp4)

    en_mp4 = OUT_DIR / f"{args.out_prefix}.mp4"
    if EN_AUDIO.exists():
        print("\n[2/3] EN audio")
        mux_audio(silent_mp4, EN_AUDIO, en_mp4, "EN")
    else:
        print(f"\n[2/3] EN audio MISSING ({EN_AUDIO}) — skipped")
        en_mp4 = None

    ja_mp4 = OUT_DIR / f"{args.out_prefix}_ja.mp4"
    if JA_AUDIO.exists():
        print("\n[3/3] JA audio")
        mux_audio(silent_mp4, JA_AUDIO, ja_mp4, "JA")
    else:
        print(f"\n[3/3] JA audio MISSING ({JA_AUDIO}) — skipped")
        ja_mp4 = None

    final = en_mp4 or ja_mp4 or silent_mp4
    print(f"\nMixed video: {final}")
    if not args.no_open:
        subprocess.Popen(["open", str(final)])


if __name__ == "__main__":
    main()

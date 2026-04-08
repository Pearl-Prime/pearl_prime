#!/usr/bin/env python3
"""Generate teacher showcase narration audio via CosyVoice2.

Extracts book text from teacher_showcase.html and generates:
  - Full narration (~15 min, ~2000 words) for audiobook showcase
  - Hook segment (~90s, ~250 words) for TikTok showcase

Uses CosyVoice2 on Pearl Star (COSYVOICE_URL) with English built-in voices.

Usage:
  python3 scripts/audio/generate_teacher_showcase_audio.py
  python3 scripts/audio/generate_teacher_showcase_audio.py --teacher ahjan
  python3 scripts/audio/generate_teacher_showcase_audio.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Teacher → gender for voice selection
TEACHER_GENDER = {
    "ahjan": "male", "adi_da": "male", "joshin": "female",
    "junko": "female", "maat": "female", "master_feung": "male",
    "master_sha": "male", "master_wu": "male", "miki": "female",
    "omote": "male", "pamela_fellows": "female", "ra": "male",
    "sai_ma": "female",
}

# Topic assignments for audiobook (column C from plan)
TEACHER_AUDIOBOOK_TOPIC = {
    "ahjan": "depression", "adi_da": "depression", "joshin": "sleep_anxiety",
    "junko": "imposter_syndrome", "maat": "courage", "master_feung": "self_worth",
    "master_sha": "anxiety", "master_wu": "self_worth", "miki": "compassion_fatigue",
    "omote": "imposter_syndrome", "pamela_fellows": "burnout", "ra": "self_worth",
    "sai_ma": "boundaries",
}

OUTPUT_DIR = REPO_ROOT / "artifacts" / "showcase" / "audio"


def extract_book_text_from_html(html_path: Path) -> dict[str, str]:
    """Extract full book text per teacher from teacher_showcase.html."""
    content = html_path.read_text(encoding="utf-8")
    teachers: dict[str, str] = {}

    # Each teacher section has id="{teacher_id}" and contains a reader div
    # Pattern: <div class="reader-content" id="reader-{id}"> ... </div>
    pattern = r'<div[^>]*class="reader-content"[^>]*id="reader-(\w+)"[^>]*>(.*?)</div>\s*</div>\s*</section>'
    for match in re.finditer(pattern, content, re.DOTALL):
        teacher_id = match.group(1)
        html_text = match.group(2)
        # Strip HTML tags to get plain text
        plain = re.sub(r'<[^>]+>', ' ', html_text)
        plain = re.sub(r'\s+', ' ', plain).strip()
        if len(plain) > 100:
            teachers[teacher_id] = plain

    # Fallback: try simpler section-based extraction
    if not teachers:
        sections = re.findall(r'<section[^>]*id="(\w+)"[^>]*>(.*?)</section>', content, re.DOTALL)
        for tid, section_html in sections:
            if tid in TEACHER_GENDER:
                # Find the book content area
                book_match = re.search(r'class="book-content[^"]*"[^>]*>(.*?)</div>', section_html, re.DOTALL)
                if book_match:
                    plain = re.sub(r'<[^>]+>', ' ', book_match.group(1))
                    plain = re.sub(r'\s+', ' ', plain).strip()
                    if len(plain) > 100:
                        teachers[tid] = plain

    return teachers


def generate_cosyvoice_audio(
    text: str,
    output_path: Path,
    voice: str = "english_female",
    cosyvoice_url: str = "",
    dry_run: bool = False,
) -> bool:
    """Generate audio via CosyVoice2 REST API."""
    if dry_run:
        print(f"    [DRY-RUN] CosyVoice2 ({voice}) → {output_path.name}")
        return True

    if not cosyvoice_url:
        print("    ERROR: COSYVOICE_URL not set")
        return False

    # CosyVoice2 API: POST with text + speaker
    payload = json.dumps({
        "text": text,
        "speaker": voice,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{cosyvoice_url.rstrip('/')}/api/v1/tts",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            audio_bytes = resp.read()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio_bytes)
        size = output_path.stat().st_size
        if size < 1000:
            print(f"    WARN: Small file ({size} bytes) — may be an error response")
            # Check if it's JSON error
            try:
                err = json.loads(audio_bytes)
                print(f"    ERROR response: {err}")
                output_path.unlink(missing_ok=True)
                return False
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        print(f"    OK ({size:,} bytes) → {output_path.name}")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def generate_edge_tts_audio(
    text: str,
    output_path: Path,
    voice: str = "en-US-GuyNeural",
    dry_run: bool = False,
) -> bool:
    """Fallback: generate via edge-tts CLI."""
    import subprocess

    if dry_run:
        print(f"    [DRY-RUN] Edge-TTS ({voice}) → {output_path.name}")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "edge_tts", "--text", text[:5000], "--voice", voice, "--write-media", str(output_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
            print(f"    OK (Edge-TTS) ({output_path.stat().st_size:,} bytes) → {output_path.name}")
            return True
        print(f"    ERROR: edge-tts failed: {result.stderr[:200]}")
        return False
    except FileNotFoundError:
        print("    ERROR: edge-tts not installed")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate teacher showcase narration audio.")
    parser.add_argument("--teacher", default=None, help="Generate for single teacher")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    cosyvoice_url = os.environ.get("COSYVOICE_URL", "").strip()
    print(f"CosyVoice2: {'at ' + cosyvoice_url if cosyvoice_url else 'NOT SET (will use Edge-TTS)'}")

    # Extract book text
    showcase_path = REPO_ROOT / "brand-wizard-app" / "public" / "teacher_showcase.html"
    if not showcase_path.exists():
        print(f"ERROR: {showcase_path} not found")
        return 1

    print(f"Extracting book text from {showcase_path.name}...")
    books = extract_book_text_from_html(showcase_path)
    print(f"Found {len(books)} teachers with book text")

    if not books:
        print("ERROR: No book text extracted. Check HTML structure.")
        return 1

    teachers = list(TEACHER_GENDER.keys())
    if args.teacher:
        teachers = [t for t in teachers if t == args.teacher]

    args.output.mkdir(parents=True, exist_ok=True)
    ok_count = 0
    total = 0

    for tid in teachers:
        text = books.get(tid, "")
        if not text:
            print(f"\n  {tid}: NO BOOK TEXT — skipping")
            continue

        topic = TEACHER_AUDIOBOOK_TOPIC.get(tid, "anxiety")
        gender = TEACHER_GENDER[tid]
        voice = f"english_{gender}"
        edge_voice = "en-US-GuyNeural" if gender == "male" else "en-US-JennyNeural"

        words = text.split()
        word_count = len(words)
        print(f"\n  {tid} ({topic}): {word_count} words, voice={voice}")

        # Full narration (~2000 words = ~15 min)
        full_text = " ".join(words[:2000])
        full_path = args.output / f"{tid}_{topic}.mp3"
        total += 1

        if cosyvoice_url:
            ok = generate_cosyvoice_audio(full_text, full_path, voice, cosyvoice_url, args.dry_run)
        else:
            ok = generate_edge_tts_audio(full_text, full_path, edge_voice, args.dry_run)
        if ok:
            ok_count += 1

        # Hook segment (~250 words = ~90s)
        hook_text = " ".join(words[:250])
        hook_path = args.output / f"{tid}_{topic}_hook.mp3"
        total += 1

        if cosyvoice_url:
            ok = generate_cosyvoice_audio(hook_text, hook_path, voice, cosyvoice_url, args.dry_run)
        else:
            ok = generate_edge_tts_audio(hook_text, hook_path, edge_voice, args.dry_run)
        if ok:
            ok_count += 1

        if not args.dry_run:
            time.sleep(1)  # Rate limit

    print(f"\n{'='*50}")
    print(f"Generated: {ok_count}/{total} audio files")
    print(f"Output: {args.output}/")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

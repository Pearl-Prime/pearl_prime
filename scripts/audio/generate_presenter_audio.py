#!/usr/bin/env python3
"""Generate TTS audio for all presenter narration scripts.

CJK decks (briefing_jp, briefing_kr, briefing_cn, briefing_tw) use CosyVoice2
on Pearl Star as primary, Edge-TTS as fallback, ElevenLabs as final fallback.
All other decks use ElevenLabs (unchanged).

Usage:
    python3 scripts/audio/generate_presenter_audio.py [--dry-run] [--deck intro] [--voice Daniel]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# ── Voice assignments ──
VOICES = {
    "Daniel": "onwK4e9ZLuTAKqWW03F9",   # Steady Broadcaster (British) — main presenter
    "Matilda": "XrExE9yKIg1WjnnlVkGX",   # Knowledgeable, Professional — data slides
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",     # Clear, Engaging Educator — educational
    "Roger": "CwhRBWXzGAHq8TQ4Fs17",     # Laid-Back, Casual — conversational
    "Bella": "hpp4J3VqNfWAUOO0d1Us",      # Professional, Bright — warm
}

# Deck → voice assignment
DECK_VOICE = {
    "intro": "Daniel",
    "marketing": "Matilda",
    "briefing_us": "Daniel",
    "briefing_jp": "Daniel",
    "briefing_kr": "Daniel",
    "briefing_fr": "Alice",
    "briefing_de": "Alice",
    "briefing_id": "Daniel",
    "briefing_br": "Daniel",
}

# ElevenLabs model
MODEL_ID = "eleven_multilingual_v2"

OUTPUT_DIR = Path("artifacts/audio/presenter")

# CJK decks → CosyVoice2 primary, Edge-TTS fallback, ElevenLabs final fallback
CJK_DECKS = {"briefing_jp", "briefing_kr", "briefing_cn", "briefing_tw"}

EDGE_TTS_CJK_VOICES = {
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "zh-cn": "zh-CN-XiaoxiaoNeural",
    "zh-tw": "zh-TW-HsiaoChenNeural",
    "zh-hk": "zh-HK-HiuGaaiNeural",
}


def generate_audio_cosyvoice(cosyvoice_url, text, language, output_path, dry_run=False):
    """Generate TTS via CosyVoice2 server (POST /tts)."""
    if dry_run:
        print(f"    [DRY-RUN] CosyVoice2 → {output_path.name}")
        return True
    import urllib.request
    payload = json.dumps({"text": text, "lang": language}).encode("utf-8")
    req = urllib.request.Request(
        f"{cosyvoice_url.rstrip('/')}/tts",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio_bytes = resp.read()
        output_path.write_bytes(audio_bytes)
        size = output_path.stat().st_size
        if size < 500:
            print(f"    ERROR: CosyVoice2 returned small file ({size} bytes)")
            output_path.unlink(missing_ok=True)
            return False
        print(f"    OK (CosyVoice2) {output_path.name} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"    ERROR: CosyVoice2 failed: {e}")
        return False


def generate_audio_edge_tts(text, voice, output_path, dry_run=False):
    """Generate TTS via edge-tts CLI (free Microsoft service)."""
    if dry_run:
        print(f"    [DRY-RUN] Edge-TTS ({voice}) → {output_path.name}")
        return True
    try:
        result = subprocess.run(
            ["edge-tts", "--text", text, "--voice", voice, "--write-media", str(output_path)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"    ERROR: edge-tts failed: {result.stderr[:200]}")
            return False
        if output_path.exists() and output_path.stat().st_size > 500:
            print(f"    OK (Edge-TTS) {output_path.name} ({output_path.stat().st_size:,} bytes)")
            return True
        return False
    except FileNotFoundError:
        print("    ERROR: edge-tts not installed (pip install edge-tts)")
        return False
    except Exception as e:
        print(f"    ERROR: edge-tts failed: {e}")
        return False


def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        # Try loading from keychain
        try:
            result = subprocess.run(
                ["python3", "scripts/ci/load_integration_env_from_keychain.py"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                if line.startswith("export ELEVENLABS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("'\"")
                    break
        except Exception:
            pass
    if not key:
        print("ERROR: ELEVENLABS_API_KEY not found. Run:")
        print('  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"')
        sys.exit(1)
    return key


def extract_scripts_from_html(html_path):
    """Extract all SCRIPTS_* data from presenter.html using regex."""
    with open(html_path) as f:
        content = f.read()

    # Find all script arrays: var SCRIPTS_XXX = [...]
    pattern = r'var\s+(SCRIPTS_\w+)\s*=\s*\['
    decks = {}

    for match in re.finditer(pattern, content):
        var_name = match.group(1)
        start = match.end() - 1  # include the [

        # Find matching closing bracket
        depth = 0
        pos = start
        while pos < len(content):
            if content[pos] == '[':
                depth += 1
            elif content[pos] == ']':
                depth -= 1
                if depth == 0:
                    break
            pos += 1

        array_str = content[start:pos + 1]

        # Map var name to deck name
        deck_name = var_name.replace("SCRIPTS_", "").lower()
        if deck_name == "intro":
            deck_name = "intro"
        elif deck_name == "marketing":
            deck_name = "marketing"
        else:
            deck_name = deck_name.replace("briefing_", "briefing_")

        # Extract text fields using regex (JS object notation)
        texts = []
        text_pattern = r'\{[^}]*?label:"([^"]*)"[^}]*?\}'
        entry_pattern = r'\{path:"([^"]*)",slide:([^,]*),label:"([^"]*)",flag:"([^"]*)",lines:\['

        # Simpler approach: extract all text:"..." values grouped by label
        current_label = None
        for line in array_str.split('\n'):
            label_match = re.search(r'label:"([^"]*)"', line)
            if label_match:
                current_label = label_match.group(1)

            text_match = re.search(r'text:"((?:[^"\\]|\\.)*)"', line)
            lang_match = re.search(r'lang:"([^"]*)"', line)

            if text_match and current_label:
                text = text_match.group(1)
                lang = lang_match.group(1) if lang_match else "en"
                # Unescape JS strings
                text = text.replace('\\n', '\n').replace("\\'", "'").replace('\\"', '"')
                # Decode unicode escapes
                text = text.encode().decode('unicode_escape', errors='replace')
                texts.append({
                    "label": current_label,
                    "lang": lang,
                    "text": text
                })

        decks[deck_name] = texts

    return decks


def generate_audio(api_key, voice_id, text, output_path, model_id=MODEL_ID, dry_run=False):
    """Generate TTS audio using ElevenLabs API via curl."""
    if dry_run:
        print(f"    [DRY-RUN] → {output_path}")
        print(f"    Voice: {voice_id}, Text: {text[:80]}...")
        return True

    # Use curl to call ElevenLabs API
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True
        }
    })

    cmd = [
        "curl", "-s", "-o", str(output_path),
        "-X", "POST", url,
        "-H", f"xi-api-key: {api_key}",
        "-H", "Content-Type: application/json",
        "-H", "Accept: audio/mpeg",
        "-d", payload
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        print(f"    ERROR: curl failed: {result.stderr}")
        return False

    # Check if output is valid MP3 (not a JSON error)
    if output_path.exists():
        size = output_path.stat().st_size
        if size < 1000:
            # Likely an error response
            with open(output_path, 'r', errors='replace') as f:
                content = f.read(500)
            if '{' in content and '"error"' in content.lower():
                print(f"    ERROR: API returned error: {content[:200]}")
                output_path.unlink()
                return False
        print(f"    ✓ {output_path.name} ({size:,} bytes)")
        return True

    print(f"    ERROR: No output file created")
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate ElevenLabs presenter audio")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be generated")
    parser.add_argument("--deck", type=str, help="Generate only for this deck (e.g., 'intro', 'briefing_us')")
    parser.add_argument("--voice", type=str, help="Override voice for all decks")
    parser.add_argument("--lang", type=str, default="en", help="Only generate for this language (default: en)")
    parser.add_argument("--html", type=str, default="brand-wizard-app/public/presenter.html",
                        help="Path to presenter.html")
    args = parser.parse_args()

    api_key = get_api_key()

    cosyvoice_url = os.environ.get("COSYVOICE_URL", "").strip()
    print("=" * 60)
    print("Presenter Audio Generator")
    print(f"  CJK provider: {'CosyVoice2 at ' + cosyvoice_url if cosyvoice_url else 'Edge-TTS fallback'}")
    print(f"  EN provider:  ElevenLabs")
    print("=" * 60)

    # Extract scripts
    print(f"\nReading: {args.html}")
    decks = extract_scripts_from_html(args.html)

    if not decks:
        print("ERROR: No script data found in presenter.html")
        sys.exit(1)

    print(f"Found {len(decks)} decks:")
    for name, texts in decks.items():
        en_count = sum(1 for t in texts if t['lang'] == 'en' or t['lang'].startswith('en'))
        print(f"  {name}: {len(texts)} segments ({en_count} English)")

    # Filter decks
    if args.deck:
        if args.deck not in decks:
            print(f"ERROR: Deck '{args.deck}' not found. Available: {list(decks.keys())}")
            sys.exit(1)
        decks = {args.deck: decks[args.deck]}

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0

    for deck_name, segments in decks.items():
        voice_name = args.voice or DECK_VOICE.get(deck_name, "Daniel")
        voice_id = VOICES.get(voice_name)
        if not voice_id:
            print(f"  WARNING: Voice '{voice_name}' not found, using Daniel")
            voice_name = "Daniel"
            voice_id = VOICES["Daniel"]

        deck_dir = OUTPUT_DIR / deck_name
        deck_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'─' * 60}")
        print(f"  Deck: {deck_name}  |  Voice: {voice_name}")
        print(f"{'─' * 60}")

        # Group segments by label
        seg_idx = 0
        prev_label = None
        label_idx = 0

        for seg in segments:
            # Filter by language
            if args.lang and not seg['lang'].startswith(args.lang):
                continue

            if seg['label'] != prev_label:
                label_idx += 1
                seg_idx = 0
                prev_label = seg['label']

            seg_idx += 1
            total += 1

            # Clean filename
            safe_label = re.sub(r'[^\w\s-]', '', seg['label']).strip().replace(' ', '_').lower()
            filename = f"{label_idx:02d}_{safe_label}_{seg_idx:02d}_{seg['lang']}.mp3"
            output_path = deck_dir / filename

            if output_path.exists() and not args.dry_run:
                print(f"    SKIP (exists): {filename}")
                success += 1
                continue

            is_cjk = deck_name in CJK_DECKS
            ok = False

            if is_cjk:
                # CJK: CosyVoice2 → Edge-TTS → ElevenLabs
                lang = seg['lang'].lower()
                if cosyvoice_url:
                    ok = generate_audio_cosyvoice(cosyvoice_url, seg['text'], lang,
                                                  output_path, dry_run=args.dry_run)
                if not ok:
                    edge_voice = EDGE_TTS_CJK_VOICES.get(lang, EDGE_TTS_CJK_VOICES.get(lang.split('-')[0], "zh-CN-XiaoxiaoNeural"))
                    ok = generate_audio_edge_tts(seg['text'], edge_voice,
                                                output_path, dry_run=args.dry_run)
                if not ok:
                    ok = generate_audio(api_key, voice_id, seg['text'], output_path,
                                       dry_run=args.dry_run)
            else:
                ok = generate_audio(api_key, voice_id, seg['text'], output_path,
                                   dry_run=args.dry_run)

            if ok:
                success += 1

            if not args.dry_run:
                time.sleep(0.5)

    print(f"\n{'=' * 60}")
    print(f"  COMPLETE: {success}/{total} segments generated")
    print(f"  Output:   {OUTPUT_DIR}/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

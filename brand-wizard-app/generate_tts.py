#!/usr/bin/env python3
"""Generate ElevenLabs TTS MP3 files for all presenter decks."""

import os, re, json, time, sys, requests

API_KEY = os.environ['ELEVENLABS_API_KEY']
BASE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE, 'public', 'presenter.html')
AUDIO_DIR = os.path.join(BASE, 'public', 'assets', 'audio')

# Voice IDs
VOICES = {
    'en_m': 'v3p1kjzUvro6S76qmYmH',   # Mark
    'en_f': '56AoDkrOh6qfVPDXZ7Pt',   # Cassidy
    'jp_m': 'TzUI53GPXnGDRdeLAWZ4',   # Toshi
    'jp_f': 'Z5Rahxh8jMhJKEgBfCSS',   # Yukiko
    'zh-tw_m': 'BrbEfHMQu0fyclQR7lfh', # Kevin Tu
    'zh-tw_f': '1AKkSX7KMPHIWuz76m0n', # Tiffy
    'zh-cn_m': 'pTOe8BQRdydOEIgv0wFL', # Liu Ping
    'zh-cn_f': '1a0nAYA3FcNQcMMfbddY', # Ziyu
}

# Language normalization: map script lang values to our voice key prefixes
LANG_MAP = {
    'en': 'en',
    'jp': 'jp',
    'ja': 'jp',
    'zh-tw': 'zh-tw',
    'zh-cn': 'zh-cn',
    'ko': 'ko',
    'fr': 'fr',
    'de': 'de',
}

# Map lang to file suffix
LANG_FILE_SUFFIX = {
    'en': 'en',
    'jp': 'ja',
    'ja': 'ja',
    'zh-tw': 'zh-tw',
    'zh-cn': 'zh-cn',
    'ko': 'ko',
    'fr': 'fr',
    'de': 'de',
}

def get_voice_id(lang, section_idx):
    """Get voice ID based on language and section index (alternating M/F)."""
    norm = LANG_MAP.get(lang, lang)
    gender = 'm' if section_idx % 2 == 0 else 'f'
    key = f'{norm}_{gender}'
    return VOICES.get(key)

def should_generate_tts(deck_id, lang):
    """Determine if TTS should be generated for this deck+lang combo."""
    # intro: ALL 4 languages get TTS (en, jp, zh-tw, zh-cn)
    if deck_id == 'intro':
        return lang in ('en', 'jp', 'ja', 'zh-tw', 'zh-cn')
    # marketing: EN lines get TTS. Non-EN lines (jp, zh-cn, ko) also get TTS in native voice
    if deck_id == 'marketing':
        return lang in ('en', 'jp', 'ja', 'zh-cn', 'ko')
    # briefing_us: EN only
    if deck_id == 'briefing_us':
        return lang == 'en'
    # briefing_jp: ALL lines (jp + en + zh-cn)
    if deck_id == 'briefing_jp':
        return lang in ('en', 'jp', 'ja', 'zh-cn')
    # briefing_kr: EN only, Korean SKIPPED
    if deck_id == 'briefing_kr':
        return lang == 'en'
    # briefing_tw: ALL (zh-tw + en)
    if deck_id == 'briefing_tw':
        return lang in ('en', 'zh-tw')
    # briefing_cn: ALL (zh-cn + en)
    if deck_id == 'briefing_cn':
        return lang in ('en', 'zh-cn')
    # briefing_fr: EN only, French SKIPPED
    if deck_id == 'briefing_fr':
        return lang == 'en'
    # briefing_de: EN only, German SKIPPED
    if deck_id == 'briefing_de':
        return lang == 'en'
    return False

def generate_tts(text, voice_id):
    """Call ElevenLabs TTS API and return MP3 bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    if resp.status_code == 429:
        print("  RATE LIMITED, waiting 5s...", file=sys.stderr)
        time.sleep(5)
        resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.content

def parse_scripts(html):
    """Parse all SCRIPTS_XXX arrays from presenter.html using JS eval via regex."""
    decks = {}
    # Match var SCRIPTS_XXX = [...];
    pattern = r'var\s+(SCRIPTS_\w+)\s*=\s*\['
    for m in re.finditer(pattern, html):
        var_name = m.group(1)
        start = m.end() - 1  # start of [
        # Find matching ];\n
        depth = 0
        i = start
        while i < len(html):
            if html[i] == '[':
                depth += 1
            elif html[i] == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        array_str = html[start:i+1]

        # Convert JS object notation to JSON
        # Add quotes around unquoted keys
        js = array_str
        js = re.sub(r'(?<=[{,])\s*(path|slide|label|flag|lines|lang|nav|text)\s*:', lambda m: f'"{m.group(1)}":', js)
        # Handle null
        js = js.replace(':null', ':null')  # already valid JSON
        # Fix JS hex escapes like \xA5 -> actual char (valid JS, not valid JSON)
        js = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), js)
        # Remove trailing commas before ] or }
        js = re.sub(r',\s*([}\]])', r'\1', js)

        try:
            sections = json.loads(js)
        except json.JSONDecodeError as e:
            print(f"  JSON parse error for {var_name}: {e}", file=sys.stderr)
            # Try a more aggressive approach
            sections = parse_sections_regex(array_str)

        # Map var name to deck_id
        deck_id = var_name.replace('SCRIPTS_', '').lower()
        decks[deck_id] = sections

    return decks

def parse_sections_regex(array_str):
    """Fallback: parse sections using regex."""
    sections = []
    # Find each {path:...,lines:[...]} block
    sec_pattern = r'\{path:"([^"]*)"[^}]*lines:\[(.*?)\]\}'
    for sm in re.finditer(sec_pattern, array_str, re.DOTALL):
        lines_str = sm.group(2)
        lines = []
        line_pattern = r'\{lang:"([^"]*)"[^}]*text:"((?:[^"\\]|\\.)*)"\}'
        for lm in re.finditer(line_pattern, lines_str):
            lang = lm.group(1)
            text = lm.group(2)
            # Unescape
            text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
            lines.append({'lang': lang, 'text': text})
        sections.append({'lines': lines})
    return sections

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    decks = parse_scripts(html)

    total_calls = 0
    total_skipped = 0
    total_bytes = 0

    # Optional filter: --deck briefing_jp
    filter_deck = None
    if len(sys.argv) > 2 and sys.argv[1] == '--deck':
        filter_deck = sys.argv[2]

    for deck_id, sections in decks.items():
        if filter_deck and deck_id != filter_deck:
            continue
        print(f"\n{'='*60}")
        print(f"DECK: {deck_id} ({len(sections)} sections)")
        print(f"{'='*60}")

        deck_dir = os.path.join(AUDIO_DIR, deck_id)
        os.makedirs(deck_dir, exist_ok=True)

        for sec_idx, section in enumerate(sections):
            lines = section.get('lines', [])
            for seg_idx, line in enumerate(lines):
                lang = line.get('lang', 'en')
                text = line.get('text', '')
                suffix = LANG_FILE_SUFFIX.get(lang, lang)
                filename = f"{sec_idx:02d}_{seg_idx:02d}_{suffix}.mp3"
                filepath = os.path.join(deck_dir, filename)

                if not should_generate_tts(deck_id, lang):
                    total_skipped += 1
                    print(f"SKIP: {deck_id}/{filename} (lang={lang}, no TTS for this deck)")
                    continue

                voice_id = get_voice_id(lang, sec_idx)
                if not voice_id:
                    total_skipped += 1
                    print(f"SKIP: {deck_id}/{filename} (no voice for lang={lang})")
                    continue

                # Generate TTS
                try:
                    mp3_data = generate_tts(text, voice_id)
                    with open(filepath, 'wb') as f:
                        f.write(mp3_data)
                    total_calls += 1
                    total_bytes += len(mp3_data)
                    print(f"OK: {deck_id}/{filename} -> {len(mp3_data):,} bytes")
                    time.sleep(0.3)
                except Exception as e:
                    print(f"ERR: {deck_id}/{filename} -> {e}", file=sys.stderr)

    print(f"\n{'='*60}")
    print(f"DONE: {total_calls} files generated, {total_skipped} skipped, {total_bytes:,} total bytes")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

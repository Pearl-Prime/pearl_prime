"""
Fixed validator: strip_meta / body-isolation now mirrors emit.py's own
replace_body() body-extraction EXACTLY (same "last two dashes" / "field-line
after header" logic), instead of assuming every block has a metadata section
sandwiched between exactly two `---` fences. This fixes two bugs in the
original validate.py:
  1. False-PASS: if a translated body was accidentally empty/lost, the old
     cjk_ratio() returned 1.0 for empty string (short-circuit), silently
     passing a corrupted-empty block.
  2. False-FAIL: metadata-heavy blocks (mode:/carry_line:/family:/etc, or the
     BAND/MECHANISM_DEPTH/COST_TYPE story-atom header stack) got swept into
     the "body" text used for the cjk_ratio/meta-phrase checks, dragging a
     genuinely-fine short translated body under threshold.
"""
import re
try:
    import opencc
    CONVERTER_S2T = opencc.OpenCC('s2t')
except Exception:
    CONVERTER_S2T = None

FALSE_POSITIVE_SAFE = set("台吃游群床")

def is_big5_encodable(ch):
    try:
        ch.encode("big5")
        return True
    except Exception:
        return False

def simplified_contamination_chars(text):
    if CONVERTER_S2T is None:
        return []
    converted = CONVERTER_S2T.convert(text)
    bad = []
    for a, b in zip(text, converted):
        if a != b and a not in FALSE_POSITIVE_SAFE and not is_big5_encodable(a):
            bad.append(a)
    return bad

META_PHRASES = ["here is", "here's", "i hear you", "this framework", "given your profile",
                "as an ai", "i understand", "let me", "sure,", "i can help", "i apologize",
                "certainly", "note:", "translation:", "i'll translate", "below is", "###", "**"]

def cjk_ratio(s):
    s2 = re.sub(r"\s|[-—…、，。！？：；「」『』（）\(\)\.,!?:;'\"]", "", s)
    if not s2:
        return 0.0   # FIX: empty body must read as 0.0 (fail), never 1.0 (pass)
    cjk = sum(1 for ch in s2 if '一' <= ch <= '鿿')
    return cjk / len(s2)

def parse_blocks_raw(text):
    idx = [m.start() for m in re.finditer(r"(?m)^## ", text)]
    if not idx:
        return []
    blocks = []
    for i, start in enumerate(idx):
        end = idx[i+1] if i+1 < len(idx) else len(text)
        blocks.append(text[start:end])
    return blocks

def header_of(block_text):
    return block_text.split("\n", 1)[0][3:].strip()

def extract_body(block_text):
    """Mirrors emit.py replace_body()'s body-region identification exactly."""
    lines = block_text.split("\n")
    if len(lines) > 1 and lines[1].strip() == "---":
        dash_idx = [i for i, l in enumerate(lines) if l.strip() == "---"]
        if len(dash_idx) < 2:
            return "\n".join(lines[1:]).strip()
        body_start = dash_idx[-2] + 1
        body_end = dash_idx[-1]
        return "\n".join(lines[body_start:body_end]).strip()
    else:
        dash_idx = [i for i, l in enumerate(lines) if l.strip() == "---"]
        if not dash_idx:
            return "\n".join(lines[1:]).strip()
        fd = dash_idx[0]
        body_start_line = 1
        if len(lines) > 1 and re.match(r"^[a-zA-Z_]+:\s", lines[1]):
            body_start_line = 2
        return "\n".join(lines[body_start_line:fd]).strip()

def validate_text_fixed(en_text, zh_text):
    problems = []
    en_blocks = parse_blocks_raw(en_text)
    zh_blocks = parse_blocks_raw(zh_text)
    en_headers = [header_of(b) for b in en_blocks]
    zh_headers = [header_of(b) for b in zh_blocks]
    if en_headers != zh_headers:
        problems.append(f"HEADER_MISMATCH en={en_headers} zh={zh_headers}")

    for i, b in enumerate(zh_blocks):
        h = header_of(b)
        body = extract_body(b)
        bl = body.lower()
        if any(p in bl for p in META_PHRASES):
            problems.append(f"{h}[{i}]: META_PHRASE_FOUND")
        cr = cjk_ratio(body)
        if cr < 0.5:
            # allow known-legit non-prose bodies (pure CALLBACK_ID/CALLBACK_PHASE
            # placeholder blocks that are genuinely empty/ID-only in the EN source)
            if i < len(en_blocks):
                en_body = extract_body(en_blocks[i])
                if body.strip() == en_body.strip() and re.match(r"^CALLBACK_ID:", body.strip()):
                    continue
            problems.append(f"{h}[{i}]: LOW_CJK_RATIO={cr:.2f} body_len={len(body)}")
        bad_chars = simplified_contamination_chars(body)
        if bad_chars:
            problems.append(f"{h}[{i}]: SIMPLIFIED_CHARS={set(bad_chars)}")
    return problems

if __name__ == "__main__":
    import sys as _sys
    en_path, zh_path = _sys.argv[1], _sys.argv[2]
    en_text = open(en_path, encoding="utf-8").read()
    zh_text = open(zh_path, encoding="utf-8").read()
    problems = validate_text_fixed(en_text, zh_text)
    if problems:
        print(f"FAIL {zh_path}")
        for p in problems:
            print("  -", p)
    else:
        print(f"PASS {zh_path}")

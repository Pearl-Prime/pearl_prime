import re, sys
import opencc

CONVERTER_S2T = opencc.OpenCC('s2t')
FALSE_POSITIVE_SAFE = set("台吃游群床")

def is_big5_encodable(ch):
    try:
        ch.encode("big5")
        return True
    except Exception:
        return False

def simplified_contamination_chars(text):
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
        return 1.0
    cjk = sum(1 for ch in s2 if '一' <= ch <= '鿿')
    return cjk / len(s2)

def parse_blocks(text):
    lines = text.split("\n")
    blocks = []
    cur_header = None
    cur_body = []
    for ln in lines:
        if ln.startswith("## "):
            if cur_header is not None:
                blocks.append((cur_header, "\n".join(cur_body)))
            cur_header = ln[3:].strip()
            cur_body = []
        else:
            cur_body.append(ln)
    if cur_header is not None:
        blocks.append((cur_header, "\n".join(cur_body)))
    return blocks

def validate_file(en_path, zh_path):
    problems = []
    en_text = open(en_path, encoding="utf-8").read()
    zh_text = open(zh_path, encoding="utf-8").read()
    en_blocks = parse_blocks(en_text)
    zh_blocks = parse_blocks(zh_text)
    en_headers = [h for h,_ in en_blocks]
    zh_headers = [h for h,_ in zh_blocks]
    if en_headers != zh_headers:
        problems.append(f"HEADER_MISMATCH en={en_headers} zh={zh_headers}")
    for h, body in zh_blocks:
        bl = body.lower()
        if any(p in bl for p in META_PHRASES):
            problems.append(f"{h}: META_PHRASE_FOUND")
        cr = cjk_ratio(body)
        if cr < 0.5:
            problems.append(f"{h}: LOW_CJK_RATIO={cr:.2f}")
        bad_chars = simplified_contamination_chars(body)
        if bad_chars:
            problems.append(f"{h}: SIMPLIFIED_CHARS={set(bad_chars)}")
    return problems

if __name__ == "__main__":
    en_path, zh_path = sys.argv[1], sys.argv[2]
    problems = validate_file(en_path, zh_path)
    if problems:
        print(f"FAIL {zh_path}")
        for p in problems:
            print("  -", p)
    else:
        print(f"PASS {zh_path}")

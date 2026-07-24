import re, sys, csv

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

def strip_meta(body):
    m = re.match(r"\s*---\n(.*?)\n---\n?(.*)", body, re.S)
    if m:
        return m.group(2)
    return body

def cjk_ratio(s):
    s2 = re.sub(r"\s|[-—…、，。！？：；「」『』（）\(\)\.,!?:;'\"]", "", s)
    if not s2:
        return 0.0
    cjk = sum(1 for ch in s2 if '一' <= ch <= '鿿')
    return cjk / len(s2)

META_PHRASES = ["here is", "here's", "i hear you", "this framework", "given your profile",
                "as an ai", "i understand", "let me", "sure,", "i can help", "i apologize",
                "certainly", "note:", "translation:", "i'll translate", "below is"]

def classify_file(path_en, path_zh):
    with open(path_en, encoding="utf-8") as f:
        en_text = f.read()
    with open(path_zh, encoding="utf-8") as f:
        zh_text = f.read()
    en_blocks = parse_blocks(en_text)
    zh_blocks = parse_blocks(zh_text)
    en_headers = [h for h,_ in en_blocks]
    zh_headers = [h for h,_ in zh_blocks]
    issues = []
    if en_headers != zh_headers:
        issues.append("HEADER_MISMATCH")
    dupe = len(zh_headers) != len(set(zh_headers))
    if dupe:
        issues.append("DUPLICATE_HEADERS")
    bad_blocks = 0
    for h, body in zh_blocks:
        b = strip_meta(body)
        bl = b.lower()
        if len(b.strip()) < 8:
            bad_blocks += 1
            continue
        if any(p in bl for p in META_PHRASES):
            bad_blocks += 1
            continue
        if cjk_ratio(b) < 0.3:
            bad_blocks += 1
            continue
    if bad_blocks:
        issues.append(f"BAD_BLOCKS:{bad_blocks}/{len(zh_blocks)}")
    return issues, len(en_blocks), len(zh_blocks)

if __name__ == "__main__":
    tsv = sys.argv[1]
    out = sys.argv[2]
    rows = []
    with open(tsv, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["en_source_status"] != "EN_CLEAN_ZH_CORRUPTED":
                continue
            zh_path = row["path"]
            en_path = zh_path.replace("/locales/zh-TW/CANONICAL.txt", "/CANONICAL.txt")
            try:
                issues, nen, nzh = classify_file(en_path, zh_path)
            except Exception as e:
                issues, nen, nzh = [f"ERROR:{e}"], -1, -1
            rows.append((zh_path, en_path, ";".join(issues) if issues else "CLEAN_FALSE_POSITIVE", nen, nzh))
    with open(out, "w", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["zh_path","en_path","triage","n_en_blocks","n_zh_blocks"])
        for r in rows:
            w.writerow(r)
    print("done", len(rows))

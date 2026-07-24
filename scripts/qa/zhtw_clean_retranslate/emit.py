import re, sys, json

def parse_blocks_raw(text):
    idx = [m.start() for m in re.finditer(r"(?m)^## ", text)]
    if not idx:
        return text, []
    prefix = text[:idx[0]]
    blocks = []
    for i, start in enumerate(idx):
        end = idx[i+1] if i+1 < len(idx) else len(text)
        blocks.append(text[start:end])
    return prefix, blocks

def replace_body(block_text, new_body):
    lines = block_text.split("\n")
    header = lines[0]
    dash_idx = [i for i,l in enumerate(lines) if l.strip() == "---"]

    if len(lines) > 1 and lines[1].strip() == "---":
        # Pattern A/B: header / --- / [metadata or blank] / --- / BODY / --- / (trailing)
        if len(dash_idx) < 2:
            return header + "\n" + new_body + "\n"
        body_start = dash_idx[-2] + 1
        body_end = dash_idx[-1]
        prefix_lines = lines[:body_start]
        suffix_lines = lines[body_end:]
        return "\n".join(prefix_lines) + "\n" + new_body + "\n" + "\n".join(suffix_lines)
    else:
        # Pattern C: header / [optional single-line field:] / BODY (one or more lines) / --- / ... (trailing dashes)
        if not dash_idx:
            return header + "\n" + new_body + "\n"
        fd = dash_idx[0]
        field_lines = []
        body_start_line = 1
        if len(lines) > 1 and re.match(r"^[a-zA-Z_]+:\s", lines[1]):
            field_lines = [lines[1]]
            body_start_line = 2
        prefix_lines = [header] + field_lines
        suffix_lines = lines[fd:]
        return "\n".join(prefix_lines) + "\n" + new_body + "\n" + "\n".join(suffix_lines)

def build_zh(en_path, translations, out_path):
    with open(en_path, encoding="utf-8") as f:
        text = f.read()
    prefix, blocks = parse_blocks_raw(text)
    assert len(blocks) == len(translations), f"{en_path}: {len(blocks)} blocks vs {len(translations)} translations"
    new_blocks = []
    for i, b in enumerate(blocks):
        nb = replace_body(b, translations[i])
        new_blocks.append(nb)
    out = prefix + "".join(new_blocks)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    build_zh(spec["en_path"], spec["translations"], spec["out_path"])
    print("wrote", spec["out_path"])

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

def strip_meta(header, body):
    # Isolate translatable prose from surrounding "---" fences / metadata
    # lines (path:/BAND:/etc) that emit.py deliberately leaves untouched
    # from the EN source. Mirrors emit.py's replace_body body-isolation
    # logic exactly (block_text = "## " + header + body), rather than a
    # regex, so validate.py checks precisely what emit.py wrote as "body".
    #
    # Fixed 2026-07-23 (chunk1): an earlier regex-based version silently
    # discarded real content for blocks with no metadata section (single
    # dash-pair), returning "" — which then false-passed cjk_ratio's
    # empty-string short-circuit (cr==1.0).
    #
    # Fixed 2026-07-23 (chunk1, follow-up): added a 3-fence branch for
    # blocks with layout header / --- / metaA / --- / metaB / --- / BODY,
    # no closing fence (seen in financial_stress/{overwhelm,spiral}).
    #
    # Fixed 2026-07-23 (chunk8): the previous 3-fence fix used
    # `len(dash_idx) == 3` as the *unconditional* signal for "3-fence, no
    # closing fence". This is wrong: the extremely common STANDARD
    # 2-fence-pair shape (header / --- / metadata / --- / BODY / ---) also
    # has exactly 3 dashes (open, meta/body split, close). Any file using
    # the standard shape was being silently mis-parsed as having an empty
    # body -> false PASS via the cjk_ratio empty-string short-circuit.
    # Reproduced directly against every RECOGNITION/MECHANISM_PROOF/
    # TURNING_POINT/EMBODIMENT engine-root file translated on the
    # chunk8 branch (the standard shape used by the vast majority of
    # blocks in that whole engine family) -- confirmed by extracting each
    # file from its committed git object (not the live shared-worktree
    # disk state, which is also not safe to trust for this kind of check)
    # and running strip_meta() on every block: every standard-shape block
    # returned length-0 body and the file still reported PASS.
    #
    # The correct signal is not dash count -- it's whether there is real
    # (non-blank) content *after* the last dash. If yes, the block is the
    # true 3-fence-no-closing shape and the body runs from the last dash
    # to the end. If no (the block ends at/near the last dash), it's the
    # standard shape and the body is between the last two dashes. This
    # also correctly handles files that MIX both shapes across different
    # blocks (confirmed on atoms/gen_x_sandwich/courage/shame, which uses
    # the 3-fence shape for its first 20 blocks and the standard shape for
    # its last 7) -- a pure dash-count check cannot distinguish these
    # per-block within the same file.
    lines = ["## " + header] + body.split("\n")
    dash_idx = [i for i, l in enumerate(lines) if l.strip() == "---"]
    if len(lines) > 1 and lines[1].strip() == "---":
        if len(dash_idx) < 2:
            return body
        after_last = lines[dash_idx[-1] + 1:]
        real_after = [l for l in after_last if l.strip() != ""]
        if real_after:
            # 3-fence-no-closing shape: body runs from the last dash to the end.
            body_start = dash_idx[-1] + 1
            return "\n".join(lines[body_start:])
        # standard 2-fence-pair shape: body is between the last two dashes.
        body_start = dash_idx[-2] + 1
        body_end = dash_idx[-1]
        return "\n".join(lines[body_start:body_end])
    else:
        if not dash_idx:
            return "\n".join(lines[1:])
        fd = dash_idx[0]
        body_start_line = 1
        if len(lines) > 1 and re.match(r"^[a-zA-Z_]+:\s", lines[1]):
            body_start_line = 2
        return "\n".join(lines[body_start_line:fd])

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
        body = strip_meta(h, body)
        bl = body.lower()
        if any(p in bl for p in META_PHRASES):
            problems.append(f"{h}: META_PHRASE_FOUND")
        cr = cjk_ratio(body)
        if cr < 0.5:
            problems.append(f"{h}: LOW_CJK_RATIO={cr:.2f}")
        # Defense in depth against the whole class of "body silently
        # resolved to empty/near-empty" bug (two prior real instances of
        # this in this file's own history): flag it explicitly instead of
        # relying solely on cjk_ratio's empty-string short-circuit, which
        # is exactly the mechanism that let both prior bugs false-PASS.
        if len(body.strip()) < 8:
            problems.append(f"{h}: EMPTY_OR_NEAR_EMPTY_BODY len={len(body.strip())}")
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

#!/usr/bin/env python3
"""Triage the zh-TW audit's WRONG_REGISTER_CLEAN_SCRIPT bucket.

Context (see artifacts/qa/zh_tw_register_rewrite_scope_correction_20260723.md):
the 1,242-row WRONG_REGISTER_CLEAN_SCRIPT verdict in
artifacts/qa/zh_tw_rewrite_list_20260722.tsv is a translation-completeness
metric (CJK-character density over the *whole file*), not a register-quality
metric -- and it is confused by English structural/metadata fields that every
schema in this repo carries by design (atom header blocks `path:`/`BAND:`/etc,
YAML quote-bank `text_en:`/`quote_id:`/etc, JSON `"text"`/`"body"` keys). This
script strips each known schema's structural fields and re-measures
completeness on the actual translatable body content only, separating:

  - genuinely stub/incomplete files (need authoring, not register editing)
  - files that are fully authored but tripped the density heuristic purely
    because of structural metadata (false positives -- do not touch)
  - a residual "authored candidate" pool that is the closest thing to a real
    register-review worklist in this bucket (still needs individual register
    verification -- this script only checks completeness, not tone/word
    choice)

Usage:
    python3 scripts/qa/triage_zh_tw_wrong_register_bucket.py \
        --input artifacts/qa/zh_tw_rewrite_list_20260722.tsv \
        --output artifacts/qa/zh_tw_wrong_register_bucket_triage_20260723.tsv \
        --ref HEAD
"""
import argparse
import re
import subprocess

CJK_RE = re.compile(r'[一-鿿]')
META_KEYS = ("path:", "BAND:", "MECHANISM_DEPTH:", "COST_TYPE:", "COST_INTENSITY:",
             "IDENTITY_STAGE:", "SEMANTIC_FAMILY:", "compression_family:")
BARE_STUB_HEADER_RE = re.compile(r'^[A-Z_]+ v\d+$')


def git_show(path, ref):
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                        capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        return None
    return r.stdout


def classify_atom_canonical(text):
    """atoms/**/locales/zh-TW/CANONICAL.txt -- sectioned by '## NAME vNN' headers,
    each followed by a '---' metadata block then prose body."""
    lines = text.split("\n")
    sections = []
    cur = []
    in_meta = False
    started = False
    for ln in lines:
        if ln.startswith("## "):
            if started:
                sections.append(cur)
            cur = []
            started = True
            in_meta = False
            continue
        if not started:
            continue
        if ln.strip() == "---":
            in_meta = not in_meta
            continue
        if in_meta:
            continue
        if any(ln.startswith(k) for k in META_KEYS):
            continue
        if BARE_STUB_HEADER_RE.match(ln.strip()):
            # bare stub header line (e.g. "RECOGNITION v02" with no "## " prefix
            # and no metadata/body of its own) -- structural noise, not prose
            continue
        cur.append(ln)
    if started:
        sections.append(cur)
    if not sections:
        return "NO_SECTIONS", 0, 0
    empty = 0
    body_cjk = 0
    body_chars = 0
    for sec in sections:
        joined = "\n".join(sec).strip()
        if not joined:
            empty += 1
        else:
            body_cjk += len(CJK_RE.findall(joined))
            body_chars += len(joined)
    frac_empty = empty / len(sections)
    body_density = (body_cjk / body_chars) if body_chars else 0.0
    if frac_empty > 0.5:
        verdict = "STUB_MAJORITY_EMPTY"
    elif frac_empty > 0.05:
        verdict = "PARTIAL_SOME_EMPTY"
    elif body_density < 0.5:
        verdict = "AUTHORED_LOW_BODY_CJK"
    else:
        verdict = "AUTHORED_CANDIDATE"
    return verdict, len(sections), empty


def classify_structural(text):
    """SOURCE_OF_TRUTH yaml/json (quote banks, practice library, teacher banks):
    check the actual content key(s) rather than whole-file density."""
    texts = re.findall(r'^\s*text:\s*(.+)$', text, re.M)          # yaml `text:`
    if not texts:
        texts = re.findall(r'^\s*body:\s*"?(.+)$', text, re.M)     # yaml `body:`
    if not texts:
        texts = re.findall(r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"', text)  # json "text"
    if not texts:
        texts = re.findall(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"', text)  # json "body"
    if not texts:
        return "NO_TEXT_FIELDS", 0, 0
    empty = sum(1 for t in texts if not CJK_RE.search(t))
    frac_empty = empty / len(texts)
    verdict = "YAML_TEXT_MISSING_CJK" if frac_empty > 0.3 else "YAML_TEXT_OK_STRUCTURAL_FALSE_POSITIVE"
    return verdict, len(texts), empty


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="zh_tw_rewrite_list TSV (path/verdict/evidence/confidence)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--ref", default="HEAD", help="git ref to read file content from")
    ap.add_argument("--verdict-filter", default="WRONG_REGISTER_CLEAN_SCRIPT",
                     help="only triage rows whose verdict column equals this")
    args = ap.parse_args()

    rows = []
    with open(args.input, newline='', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            if args.verdict_filter and parts[1] != args.verdict_filter:
                continue
            rows.append(parts)

    out_rows = []
    counts = {}
    for path, verdict_col, evidence, confidence in rows:
        text = git_show(path, args.ref)
        if text is None:
            v, n, e = "FILE_MISSING_AT_REF", 0, 0
        elif path.startswith("SOURCE_OF_TRUTH"):
            v, n, e = classify_structural(text)
        else:
            v, n, e = classify_atom_canonical(text)
        counts[v] = counts.get(v, 0) + 1
        out_rows.append((path, v, n, e, evidence))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("path\ttriage_verdict\tsections_or_fields\tempty_count\toriginal_evidence\n")
        for r in out_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    print("=== TRIAGE COUNTS ===")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{v:6d}  {k}")
    print(f"\nTotal: {len(out_rows)}")


if __name__ == "__main__":
    main()

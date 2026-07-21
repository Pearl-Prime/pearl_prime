#!/usr/bin/env python3
"""Catalog + triage Cursor agent transcripts older than a cutoff date.

Emits SESSION_CATALOG.tsv under artifacts/qa/archived_session_audit_gt30d_YYYYMMDD/.
Also writes triage candidates JSON for deep-read waves.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

HIGH_SIGNAL = re.compile(
    r"\b("
    r"TODO|next steps?|not yet|missing|spec|gate|pipeline|should we|idea|proposal|"
    r"blocked|never landed|undone|unfinished|backlog|wishlist|feature|"
    r"pearl news|manga|register_gate|accent bank|metricool|comfy|ontgp|"
    r"bestseller|drift|workstream|prompt pack|session mining|atom bank|"
    r"audiobook|social|storyblocks|cover|translation|cjk|qwen|gemma|"
    r"freebie|harbor|teacher|voice bank|catalog|skeleton|bisac|"
    r"retention|dispatcher|plantime|judge|ladder|naming engine"
    r")\b",
    re.I,
)
LOW_SIGNAL = re.compile(
    r"\b("
    r"fix ci|merge (this )?pr|babysit|green the|re-run|retry|"
    r"read CLAUDE\.md|startup_receipt|closeout_receipt|"
    r"push.?guard|preflight|health_check"
    r")\b",
    re.I,
)
ROLE_RE = re.compile(
    r"\b(Pearl_(?:Dev|PM|GitHub|Brand|Manga|News|Video|Research|DevOps|Prime|"
    r"Editor|Int|Prez|Architect|Marketing|Writer)|Booker[A-G])\b",
    re.I,
)
THEME_PATTERNS = [
    ("manga", re.compile(r"\bmanga|panel|comfy|v5 layer|story.?authored\b", re.I)),
    ("pearl_news", re.compile(r"\bpearl.?news|sidebar|opd-\d+\b", re.I)),
    ("pipeline_gates", re.compile(r"\bgate|register_gate|pipeline|drift|ontgp|chord\b", re.I)),
    ("catalog_atoms", re.compile(r"\bcatalog|atom|skeleton|accent.?bank|thesis\b", re.I)),
    ("social_video", re.compile(r"\bsocial|tiktok|metricool|storyblocks|voice.?bank|reel|video\b", re.I)),
    ("translation", re.compile(r"\btranslati|cjk|zh-?tw|qwen|locale|i18n\b", re.I)),
    ("governance_ci", re.compile(r"\bci|github|pr #|worktree|branch|governance|push.?guard\b", re.I)),
    ("covers_brand", re.compile(r"\bcover|brand|runcomfy|visual.?identit\b", re.I)),
    ("audiobook", re.compile(r"\baudiobook|elevenlabs|tts|voice\b", re.I)),
    ("research_tooling", re.compile(r"\bresearch|prompt.?pack|analyzer|scanner|audit\b", re.I)),
]


def extract_text_from_message(obj: dict) -> str:
    msg = obj.get("message") or obj
    content = msg.get("content") if isinstance(msg, dict) else None
    parts: list[str] = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    parts.append(part.get("text") or "")
                elif "text" in part:
                    parts.append(str(part.get("text") or ""))
            elif isinstance(part, str):
                parts.append(part)
    elif isinstance(content, str):
        parts.append(content)
    return " ".join(parts)


def first_user_preview(jsonl_path: Path, max_lines: int = 40) -> str:
    try:
        with jsonl_path.open(encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = obj.get("role") or obj.get("type")
                if role != "user":
                    continue
                text = extract_text_from_message(obj)
                text = re.sub(r"</?user_query>", " ", text)
                text = re.sub(r"</?timestamp>[^<]*", " ", text)
                text = " ".join(text.split())
                if text:
                    return text[:240]
    except OSError:
        return ""
    return ""


def sample_tail_text(jsonl_path: Path, head_n: int = 40, tail_n: int = 20) -> str:
    """Cheap sample: first head_n lines + last tail_n lines of text content."""
    chunks: list[str] = []
    try:
        with jsonl_path.open(encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return ""
    for line in lines[:head_n] + lines[-tail_n:]:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = obj.get("role") or obj.get("type")
        if role not in ("user", "assistant"):
            continue
        text = extract_text_from_message(obj)
        if text:
            chunks.append(text[:500])
    return "\n".join(chunks)


def guess_role(title: str, sample: str) -> str:
    blob = f"{title}\n{sample[:2000]}"
    m = ROLE_RE.search(blob)
    return m.group(1) if m else ""


def theme_tags(title: str, sample: str) -> str:
    blob = f"{title}\n{sample}"
    tags = [name for name, pat in THEME_PATTERNS if pat.search(blob)]
    return ",".join(tags[:6])


def triage_score(title: str, sample: str, nbytes: int) -> tuple[int, str]:
    if nbytes < 2000:
        return 0, "SKIP"
    blob = f"{title}\n{sample}"
    high = len(HIGH_SIGNAL.findall(blob))
    low = len(LOW_SIGNAL.findall(blob))
    score = min(10, high)
    # Penalize pure ops rituals
    if low >= 3 and high <= 2:
        score = max(0, score - 3)
    # Boost design/proposal language
    if re.search(r"\b(proposal|should we|idea|spec|design|architect)\b", blob, re.I):
        score = min(10, score + 2)
    if re.search(r"\b(not yet|never|missing|undone|unfinished|still need)\b", blob, re.I):
        score = min(10, score + 2)
    if nbytes < 8000 and score <= 3:
        return score, "SKIP"
    if score >= 6:
        return score, "DEEP"
    if score >= 3:
        return score, "SKIM"
    return score, "SKIP"


def already_mined_hint(title: str) -> bool:
    # Heuristic: old-chat finish / session mining / last-30d audit language
    return bool(
        re.search(
            r"old.?chat|session.?mining|untitled\s+3\d{2}|archived session follow|"
            r"past 30 days|last 30 days|github.?return.?replay",
            title,
            re.I,
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--transcripts",
        default=str(
            Path.home()
            / ".cursor/projects/Users-ahjan-phoenix-omega/agent-transcripts"
        ),
    )
    ap.add_argument("--cutoff", default="2026-06-22")
    ap.add_argument(
        "--out-dir",
        default="artifacts/qa/archived_session_audit_gt30d_20260722",
    )
    args = ap.parse_args()
    base = Path(args.transcripts)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cutoff = time.mktime(time.strptime(args.cutoff, "%Y-%m-%d"))

    rows: list[dict] = []
    deep_by_month: dict[str, list[dict]] = defaultdict(list)
    months = Counter()

    for d in sorted(base.iterdir(), key=lambda p: p.stat().st_mtime):
        if not d.is_dir():
            continue
        mtime = d.stat().st_mtime
        if mtime >= cutoff:
            continue
        jl_files = list(d.glob("*.jsonl"))
        if not jl_files:
            continue
        jl = max(jl_files, key=lambda p: p.stat().st_size)
        nbytes = jl.stat().st_size
        month = time.strftime("%Y-%m", time.localtime(mtime))
        mtime_s = time.strftime("%Y-%m-%d", time.localtime(mtime))
        title = first_user_preview(jl)
        sample = sample_tail_text(jl)
        role = guess_role(title, sample)
        themes = theme_tags(title, sample)
        score, disposition = triage_score(title, sample, nbytes)
        if already_mined_hint(title):
            disposition = "ALREADY_MINED"
        months[month] += 1
        row = {
            "session_id": d.name,
            "mtime": mtime_s,
            "month": month,
            "bytes": nbytes,
            "title_preview": title.replace("\t", " ").replace("\n", " "),
            "agent_role_guess": role,
            "theme_tags": themes,
            "triage_score": score,
            "disposition": disposition,
        }
        rows.append(row)
        if disposition == "DEEP":
            deep_by_month[month].append(row)

    # Cap DEEP per large months — keep top by score then bytes
    deep_caps = {"2026-02": 31, "2026-03": 40, "2026-04": 35, "2026-05": 35, "2026-06": 3}
    demoted = 0
    deep_ids: set[str] = set()
    for month, cap in deep_caps.items():
        candidates = deep_by_month.get(month, [])
        candidates.sort(key=lambda r: (-r["triage_score"], -r["bytes"]))
        keep = {c["session_id"] for c in candidates[:cap]}
        deep_ids |= keep
        for c in candidates[cap:]:
            # demote overflow DEEP → SKIM
            for r in rows:
                if r["session_id"] == c["session_id"] and r["disposition"] == "DEEP":
                    r["disposition"] = "SKIM"
                    demoted += 1

    catalog_path = out / "SESSION_CATALOG.tsv"
    cols = [
        "session_id",
        "mtime",
        "month",
        "bytes",
        "title_preview",
        "agent_role_guess",
        "theme_tags",
        "triage_score",
        "disposition",
    ]
    with catalog_path.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda x: (x["month"], -x["triage_score"], x["session_id"])):
            f.write("\t".join(str(r[c]) for c in cols) + "\n")

    # Deep candidate list for waves
    deep_rows = [r for r in rows if r["disposition"] == "DEEP"]
    deep_path = out / "DEEP_CANDIDATES.json"
    deep_path.write_text(json.dumps(deep_rows, indent=2), encoding="utf-8")

    disp = Counter(r["disposition"] for r in rows)
    summary = {
        "cutoff": args.cutoff,
        "total_sessions": len(rows),
        "months": dict(sorted(months.items())),
        "disposition_counts": dict(disp),
        "deep_demoted_to_skim": demoted,
        "catalog": str(catalog_path),
        "deep_candidates": str(deep_path),
    }
    (out / "CATALOG_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

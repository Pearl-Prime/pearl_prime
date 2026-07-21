#!/usr/bin/env python3
"""Deep-extract idea candidates from DEEP_CANDIDATES.json (+ optional SKIM top).

Writes IDEA_BACKLOG_RAW.jsonl with extracted signals for later reconcile.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SIGNAL_LINE = re.compile(
    r"(?i)("
    r"next steps?|TODO|not yet|still need|missing|never (landed|merged|done)|"
    r"should (we|add|build|create)|proposal|recommend|backlog|"
    r"undone|unfinished|left to do|do not reopen|operator (must|gate)|"
    r"TRULY_MISSING|LANDED-OFFLINE|blocked on|wish ?list|"
    r"implement|add (a |the )?(gate|script|spec|validator|dashboard|widget)|"
    r"create (a |the )?(analyzer|gate|spec|pipeline|pack)"
    r").{0,200}"
)
USER_QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.S | re.I)


def extract_text(obj: dict) -> str:
    msg = obj.get("message") or obj
    content = msg.get("content") if isinstance(msg, dict) else None
    parts: list[str] = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text") or "")
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part["text"]))
            elif isinstance(part, str):
                parts.append(part)
    elif isinstance(content, str):
        parts.append(content)
    return "\n".join(parts)


def load_session_texts(jsonl_path: Path, max_chars: int = 120_000) -> tuple[str, str, str]:
    """Return (first_user, all_user_joined, assistant_tail)."""
    users: list[str] = []
    assistants: list[str] = []
    try:
        with jsonl_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = obj.get("role") or obj.get("type")
                text = extract_text(obj)
                if not text:
                    continue
                if role == "user":
                    users.append(text)
                elif role == "assistant":
                    assistants.append(text)
    except OSError:
        return "", "", ""
    first = ""
    if users:
        m = USER_QUERY_RE.search(users[0])
        first = (m.group(1) if m else users[0]).strip()
        first = " ".join(first.split())[:400]
    user_blob = "\n".join(users)[: max_chars // 2]
    asst_blob = "\n".join(assistants[-8:])[: max_chars // 2]
    return first, user_blob, asst_blob


def theme_from_tags(tags: str) -> str:
    if not tags:
        return "general"
    return tags.split(",")[0]


def extract_signals(session: dict, transcripts_root: Path) -> list[dict]:
    sid = session["session_id"]
    jl = transcripts_root / sid / f"{sid}.jsonl"
    if not jl.exists():
        jl_files = list((transcripts_root / sid).glob("*.jsonl"))
        if not jl_files:
            return []
        jl = jl_files[0]
    first, user_blob, asst_blob = load_session_texts(jl)
    blob = user_blob + "\n" + asst_blob
    hits = SIGNAL_LINE.findall(blob)  # only the keyword groups — re-find with context
    ideas: list[dict] = []
    seen: set[str] = set()

    # Prefer full-context matches
    for m in SIGNAL_LINE.finditer(blob):
        quote = " ".join(m.group(0).split())
        if len(quote) < 24:
            continue
        key = quote[:120].lower()
        if key in seen:
            continue
        seen.add(key)
        ideas.append(
            {
                "source_session": sid,
                "mtime": session.get("mtime"),
                "month": session.get("month"),
                "title": session.get("title_preview", "")[:200],
                "theme": theme_from_tags(session.get("theme_tags", "")),
                "triage_score": session.get("triage_score"),
                "quote_or_signal": quote[:280],
                "first_user": first[:280],
            }
        )
        if len(ideas) >= 8:
            break

    # Always keep at least one idea from the first user ask for DEEP sessions
    if not ideas and first:
        ideas.append(
            {
                "source_session": sid,
                "mtime": session.get("mtime"),
                "month": session.get("month"),
                "title": session.get("title_preview", "")[:200],
                "theme": theme_from_tags(session.get("theme_tags", "")),
                "triage_score": session.get("triage_score"),
                "quote_or_signal": first[:280],
                "first_user": first[:280],
            }
        )
    return ideas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-dir",
        default="artifacts/qa/archived_session_audit_gt30d_20260722",
    )
    ap.add_argument(
        "--transcripts",
        default=str(
            Path.home()
            / ".cursor/projects/Users-ahjan-phoenix-omega/agent-transcripts"
        ),
    )
    ap.add_argument("--months", default="", help="Comma months filter e.g. 2026-02,2026-03")
    ap.add_argument("--also-skim-top", type=int, default=0, help="Also extract top N SKIM by score")
    args = ap.parse_args()
    out = Path(args.out_dir)
    root = Path(args.transcripts)
    deep = json.loads((out / "DEEP_CANDIDATES.json").read_text(encoding="utf-8"))
    months = {m.strip() for m in args.months.split(",") if m.strip()}
    if months:
        deep = [d for d in deep if d.get("month") in months]

    # optional SKIM
    if args.also_skim_top:
        catalog_lines = (out / "SESSION_CATALOG.tsv").read_text(encoding="utf-8").splitlines()
        header = catalog_lines[0].split("\t")
        skim = []
        for line in catalog_lines[1:]:
            cols = line.split("\t")
            row = dict(zip(header, cols))
            if row.get("disposition") != "SKIM":
                continue
            if months and row.get("month") not in months:
                continue
            skim.append(row)
        skim.sort(key=lambda r: (-int(r.get("triage_score") or 0), -int(r.get("bytes") or 0)))
        for r in skim[: args.also_skim_top]:
            r["triage_score"] = int(r["triage_score"])
            deep.append(r)

    raw_path = out / "IDEA_BACKLOG_RAW.jsonl"
    # append mode if filtering months; truncate if full
    mode = "a" if months and raw_path.exists() else "w"
    if not months:
        mode = "w"

    n_sessions = 0
    n_ideas = 0
    with raw_path.open(mode, encoding="utf-8") as f:
        for session in deep:
            ideas = extract_signals(session, root)
            n_sessions += 1
            for idea in ideas:
                f.write(json.dumps(idea, ensure_ascii=False) + "\n")
                n_ideas += 1
            if n_sessions % 25 == 0:
                print(f"processed {n_sessions} sessions, {n_ideas} ideas", flush=True)

    print(json.dumps({"sessions": n_sessions, "ideas": n_ideas, "raw": str(raw_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

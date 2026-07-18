#!/usr/bin/env python3
"""
Native ja_JP manga title / topic / EI-author synthesis for the live SSOT.
=========================================================================

Fills the `title` / `localized_titles.ja_JP` / `topic` / `manga_author` fields
(currently `TBD`) on the 270 live ja_JP series plans at
``config/source_of_truth/manga_series_plans/ja_JP/*.yaml``.

Per-field provenance (LLM tier policy compliant):
  - title          → Qwen on Pearl Star via Ollama (CJK generator, Tier-2 free
                     local). Native Japanese, genre-faithful, wellness topic kept
                     as INTERIOR architecture (Genre Shell thesis) — never an
                     explicit self-help label. NO paid API (DashScope is BANNED).
  - topic          → deterministic rotation of the brand's primary + secondary
                     topics across its series (covers all topics). No LLM.
  - manga_author   → generate_manga_author.generate_display_name (deterministic
                     ja_JP kanji name pools). No LLM.

In-place, idempotent: only `: TBD` lines are rewritten, so partial runs resume and
re-runs never clobber filled values. File comments / field order are preserved
(targeted line replacement, not a YAML round-trip).

This does NOT render, call any paid API, or touch any other locale.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 scripts/manga/synthesize_manga_titles_jajp.py            # all 270
  python3 scripts/manga/synthesize_manga_titles_jajp.py --brand stillness_press
  python3 scripts/manga/synthesize_manga_titles_jajp.py --limit 3 --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from generate_manga_author import generate_display_name  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
ROOT = _MAIN_REPO if (not (REPO_ROOT / "config").exists()
                      and (_MAIN_REPO / "config").exists()) else REPO_ROOT

SERIES_DIR = ROOT / "config" / "source_of_truth" / "manga_series_plans" / "ja_JP"
CANONICAL_BRANDS = ROOT / "config" / "manga" / "canonical_brand_list.yaml"
REVIEW_OUT = ROOT / "artifacts" / "catalog" / "manga" / "ssot_rollup" / "ja_JP_title_synthesis_review.csv"

# Pearl Star Ollama endpoint — load via scripts/ci/load_integration_env_from_keychain.py
# (QWEN_BASE_URL/QWEN_MODEL). Never the paid DashScope cloud (BANNED by tier policy).
QWEN_BASE = os.environ.get("QWEN_BASE_URL", "http://localhost:11434").rstrip("/")
if QWEN_BASE.endswith("/v1"):
    QWEN_BASE = QWEN_BASE[:-3]
QWEN_MODEL = os.environ.get("QWEN_MODEL", "qwen2.5:14b")

# ── Genre flavour (Japanese register anchor) ────────────────────────────────
GENRE_JP: dict[str, str] = {
    "iyashikei": "癒し・日常・静けさ", "dark_fantasy": "ダークファンタジー・呪い・運命",
    "supernatural_mystery": "怪異・謎・現代の闇", "romance_josei_drama": "大人の恋愛・心の機微",
    "psychological_thriller": "心理サスペンス・緊張", "workplace_drama": "職場・人間模様",
    "sci_fi_cyberpunk": "近未来・電脳・SF", "psychological_horror": "静かな恐怖・心理ホラー",
    "action_battle": "戦い・熱血", "historical_period": "時代もの・歴史",
    "isekai": "異世界・転生", "sports_competition": "スポーツ・競技",
    "school_coming_of_age": "学園・青春", "cultivation_martial": "仙道・武術・修行",
}
TOPIC_JP: dict[str, str] = {
    "anxiety": "不安", "sleep": "眠り", "burnout": "燃え尽き", "overthinking": "考えすぎ",
    "grief": "喪失と悲しみ", "somatic_healing": "身体の感覚", "social_anxiety": "対人の緊張",
    "self_worth": "自己の価値", "imposter_syndrome": "自分への疑い", "trauma_recovery": "傷からの回復",
    "shame": "羞恥", "boundaries": "境界線", "courage": "勇気", "compassion": "慈しみ",
    "financial_anxiety": "お金の不安", "adhd_focus": "集中", "self_compassion": "自分への優しさ",
}

SYSTEM_PROMPT = (
    "あなたは日本の大手漫画編集者であり、売れるタイトルを生み出すプロのコピーライターです。"
    "指定されたジャンルに忠実な、日本語ネイティブの漫画タイトルを1つだけ作ります。"
    "心理・ウェルネスのテーマは作品の『内的構造』として扱い、タイトルには絶対に直接出しません。"
    "【禁止】自己啓発・セラピー・カウンセリングの語、および『不安』『注意力』『集中力』"
    "『自己肯定』『燃え尽き』『トラウマ』など、テーマを説明する語をタイトルに使うこと。"
    "【良い例】ジャンル=psychological_thriller／内的テーマ=自己価値 → 「幻影探偵社」"
    "（テーマを表に出さず、ジャンルの魅力で惹きつける）。"
    "【悪い例】「注意力大作戦」（テーマ語を直出し→禁止）／「不安からの解放」（説明的→禁止）。"
    "商業漫画として書店で目を引く、短く強いタイトルにします。"
    '出力はJSONのみ: {"title_ja":"日本語タイトル","english_gloss":"short English gloss"}'
)

# Clinical / self-help stems that must never appear in a title (topic-leak guard).
# Deliberately excludes soft words (心, 癒, 夢) that can be legitimate manga vocabulary.
CLINICAL_STEMS = (
    "不安", "セラピー", "カウンセリング", "自己啓発", "注意力", "集中力",
    "自己肯定", "燃え尽き", "トラウマ", "うつ病", "メンタルヘルス", "症候群",
)


def _leaks_topic(title: str, topic: str) -> bool:
    if any(s in title for s in CLINICAL_STEMS):
        return True
    t_jp = TOPIC_JP.get(topic, "")
    return bool(t_jp) and t_jp in title


def _load_yaml(p: Path) -> Any:
    with open(p, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _ollama_generate(prompt: str, *, temperature: float, retries: int = 4) -> str | None:
    """Single Qwen /api/generate call with retry on transient runner crashes."""
    payload = json.dumps({
        "model": QWEN_MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": temperature, "num_predict": 200},
    }).encode("utf-8")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                f"{QWEN_BASE}/api/generate", data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read())
            reply = re.sub(r"<think>.*?</think>", "", result.get("response", ""),
                           flags=re.DOTALL).strip()
            return reply or None
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:120]
            except Exception:
                pass
            # 500 "llama runner process has terminated" = transient cold-start crash
            if attempt < retries:
                time.sleep(3 * attempt)
                continue
            print(f"    HTTP{e.code} after {retries} tries: {body}")
            return None
        except Exception as e:  # noqa: BLE001
            if attempt < retries:
                time.sleep(3 * attempt)
                continue
            print(f"    ERROR after {retries} tries: {e}")
            return None
    return None


def _parse_title(reply: str) -> tuple[str, str] | None:
    m = re.search(r"\{.*\}", reply, re.DOTALL)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    title = str(d.get("title_ja", "")).strip().strip("「」『』\"' ")
    gloss = str(d.get("english_gloss", "")).strip()
    return (title, gloss) if title else None


def _has_jp(s: str) -> bool:
    return any(("぀" <= c <= "ヿ") or ("一" <= c <= "鿿") for c in s)


def gen_title(brand: str, genre: str, topic: str, demo: str,
              avoid: set[str], dry_run: bool) -> tuple[str, str]:
    if dry_run:
        return (f"[DRY {genre}/{topic}]", "dry-run")
    g_jp = GENRE_JP.get(genre, genre)
    t_jp = TOPIC_JP.get(topic, topic.replace("_", " "))
    base_user = (
        f"ブランド: {brand}\nジャンル: {genre}（{g_jp}）\n"
        f"内的テーマ（隠す）: {t_jp}\n読者層: {demo}\n"
    )
    for attempt in range(5):
        temp = 0.85 + 0.07 * attempt
        user = base_user
        if avoid:
            shown = list(avoid)[-12:]
            user += "次のタイトルとは重複しないこと: " + " / ".join(shown) + "\n"
        reply = _ollama_generate(SYSTEM_PROMPT + "\n\n" + user, temperature=temp)
        if not reply:
            continue
        parsed = _parse_title(reply)
        if not parsed:
            continue
        title, gloss = parsed
        if not _has_jp(title):           # reject romaji-only / English output
            continue
        if _leaks_topic(title, topic):   # topic/clinical word leaked → regen
            continue
        if title in avoid:               # within-run collision → regen
            continue
        return title, gloss
    return "", ""


def assign_topics(brand_info: dict, series_list: list[dict]) -> None:
    """Round-robin the brand's [primary]+secondary topics across its series."""
    topics = [brand_info.get("primary_topic", "")] + list(brand_info.get("secondary_topics", []) or [])
    topics = [t for t in topics if t] or ["self_worth"]
    for i, sp in enumerate(sorted(series_list, key=lambda r: (r["genre"], r["series_index"]))):
        sp["_topic"] = topics[i % len(topics)]


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def apply_edits(path: Path, *, title: str, topic: str, author: str) -> bool:
    """Replace `: TBD` lines in place. Idempotent. Returns True if changed."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    in_localized = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if re.match(r"^title:\s*TBD\s*$", stripped):
            lines[i] = f"title: {_yaml_quote(title)}\n"; changed = True
        elif re.match(r"^localized_titles:\s*$", stripped):
            in_localized = True
        elif in_localized and re.match(r"^\s+ja_JP:\s*TBD\s*$", stripped):
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = f"{indent}ja_JP: {_yaml_quote(title)}\n"; changed = True; in_localized = False
        elif re.match(r"^topic:\s*TBD\s*$", stripped):
            lines[i] = f"topic: {topic}\n"; changed = True
        elif re.match(r"^manga_author:\s*TBD\s*$", stripped):
            lines[i] = f"manga_author: {_yaml_quote(author)}\n"; changed = True
        elif stripped and not line.startswith((" ", "\t")) and in_localized:
            in_localized = False
    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", help="Restrict to one brand_id")
    ap.add_argument("--limit", type=int, help="Process at most N series")
    ap.add_argument("--dry-run", action="store_true", help="No Qwen calls / no writes; placeholder titles")
    ap.add_argument("--no-write", action="store_true", help="Generate but do not edit YAML (review only)")
    args = ap.parse_args()

    brands = (_load_yaml(CANONICAL_BRANDS) or {}).get("brands", {})
    plans: list[dict] = []
    for p in sorted(SERIES_DIR.glob("*.yaml")):
        sp = _load_yaml(p) or {}
        plans.append({
            "path": p, "brand_id": sp.get("brand_id", ""), "genre": sp.get("genre", ""),
            "demographic": sp.get("demographic", "general"), "series_id": sp.get("series_id", p.stem),
            "series_index": sp.get("series_id", p.stem).split("__")[-1],
            "title_is_tbd": str(sp.get("title", "")).strip().upper() == "TBD",
        })

    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in plans:
        by_brand[r["brand_id"]].append(r)
    for b, lst in by_brand.items():
        assign_topics(brands.get(b, {}), lst)

    todo = [r for r in plans if (not args.brand or r["brand_id"] == args.brand)]
    todo.sort(key=lambda r: (r["brand_id"], r["genre"], r["series_index"]))
    if args.limit:
        todo = todo[: args.limit]

    used_by_brand: dict[str, set[str]] = defaultdict(set)
    review_rows: list[dict] = []
    filled = skipped = failed = 0
    t0 = time.time()
    for n, r in enumerate(todo, 1):
        if not r["title_is_tbd"] and not args.dry_run:
            skipped += 1
            continue
        demo_jp = {"josei": "josei（成人女性）", "seinen": "seinen（成人男性）",
                   "shonen": "shonen（少年）", "shojo": "shojo（少女）",
                   "manhwa": "webtoon", "general": "一般"}.get(
            brands.get(r["brand_id"], {}).get("demographic", "general"), "一般")
        title, gloss = gen_title(r["brand_id"], r["genre"], r["_topic"], demo_jp,
                                 used_by_brand[r["brand_id"]], args.dry_run)
        if not title:
            failed += 1
            print(f"[{n}/{len(todo)}] FAIL {r['series_id']}")
            continue
        used_by_brand[r["brand_id"]].add(title)
        author = generate_display_name(genre=r["genre"], locale="ja_JP",
                                       brand_id=r["brand_id"], topic=r["_topic"],
                                       demographic=r["demographic"])
        wrote = False
        if not args.dry_run and not args.no_write:
            wrote = apply_edits(r["path"], title=title, topic=r["_topic"], author=author)
        filled += 1
        review_rows.append({"brand_id": r["brand_id"], "genre": r["genre"],
                            "series_id": r["series_id"], "topic": r["_topic"],
                            "title_ja": title, "english_gloss": gloss,
                            "manga_author": author, "written": wrote})
        if n % 10 == 0 or n == len(todo):
            print(f"[{n}/{len(todo)}] filled={filled} skip={skipped} fail={failed} "
                  f"({time.time()-t0:.0f}s)  last: {title}  ({gloss})")

    if review_rows:
        REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(REVIEW_OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(review_rows[0].keys()))
            w.writeheader(); w.writerows(review_rows)
        print(f"review sidecar → {REVIEW_OUT.relative_to(ROOT)}")
    print(f"DONE filled={filled} skipped={skipped} failed={failed} "
          f"in {time.time()-t0:.0f}s  model={QWEN_MODEL}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

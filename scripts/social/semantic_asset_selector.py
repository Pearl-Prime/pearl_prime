#!/usr/bin/env python3
"""CTQC semantic asset selector — caption/atom keywords → best stock plate.

Replaces blind ``pool[seed % len(pool)]`` with deterministic weighted overlap
against ``asset_keywords.tsv``. No paid vision APIs. Optional local CLIP is
documented but not required for v1.

Authority:
  - config/social/semantic_keyword_taxonomy.yaml
  - artifacts/research/storyblocks_semantic_sourcing_20260720/RECOMMENDED_TAXONOMY.md
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_TAXONOMY = REPO / "config/social/semantic_keyword_taxonomy.yaml"
DEFAULT_TAG_STORE = (
    REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "asset_keywords.tsv"
)

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


@dataclass(frozen=True)
class CompiledQuery:
    topic: str
    keywords: tuple[str, ...]
    required_keywords: tuple[str, ...]
    filtered_keywords: tuple[str, ...]
    primary: tuple[str, ...]
    objects_and_hooks: tuple[str, ...]
    beat_role: str
    match_sources: tuple[str, ...]  # human-readable provenance


@dataclass(frozen=True)
class SelectionResult:
    path: Path
    keyword_score: float
    match_quality: str  # aligned | weak_topic_fallback
    match_rationale: str
    matched_keywords: tuple[str, ...]
    compiled: CompiledQuery


@dataclass
class AssetRecord:
    path: Path
    topic_folder: str
    keywords: set[str] = field(default_factory=set)
    metaphor: str = ""
    title: str = ""


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_").replace("-", "_")


def _uniq(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        t = _norm(raw)
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def load_taxonomy(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_TAXONOMY
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"taxonomy must be a mapping: {p}")
    return data


def load_tag_store(path: Path | None = None) -> list[AssetRecord]:
    p = path or DEFAULT_TAG_STORE
    if not p.is_file():
        raise FileNotFoundError(f"asset keyword tag store missing: {p}")
    records: list[AssetRecord] = []
    with p.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rel = (row.get("asset_path") or "").strip()
            if not rel:
                continue
            ap = Path(rel)
            if not ap.is_absolute():
                ap = REPO / ap
            kws = {_norm(x) for x in (row.get("keywords") or "").split(",") if x.strip()}
            records.append(
                AssetRecord(
                    path=ap,
                    topic_folder=(row.get("topic_folder") or "").strip(),
                    keywords=kws,
                    metaphor=(row.get("metaphor") or "").strip(),
                    title=(row.get("title") or "").strip(),
                )
            )
    return records


def extract_caption_nouns(text: str, allowlist: Sequence[str], max_n: int = 2) -> list[str]:
    allow = {_norm(a) for a in allowlist}
    blob = (text or "").lower()
    found: list[str] = []
    for noun in allowlist:
        n = _norm(noun)
        # match underscore or space form in caption
        surface = noun.replace("_", " ").lower()
        if n in allow and (surface in blob or n in blob.replace(" ", "_")):
            if n not in found:
                found.append(n)
        if len(found) >= max_n:
            break
    return found


def apply_phrase_boosts(text: str, taxonomy: dict[str, Any]) -> list[str]:
    blob = (text or "").lower()
    out: list[str] = []
    for rule in taxonomy.get("caption_phrase_boosts") or []:
        phrases = rule.get("phrases") or []
        if any(str(p).lower() in blob for p in phrases):
            out.extend(rule.get("keywords") or [])
    return _uniq(out)


def compile_query(
    *,
    topic: str,
    caption: str = "",
    persona: str = "",
    hook_family: str = "",
    tone: str = "",
    beat_role: str = "beat",
    taxonomy: dict[str, Any] | None = None,
) -> CompiledQuery:
    tax = taxonomy or load_taxonomy()
    topic_key = topic
    tv_map = tax.get("topic_visual_keywords") or {}
    if topic_key not in tv_map:
        # alias folders (e.g. social_anxiety may be requested while stock is loneliness)
        topic_key = topic
    tv = tv_map.get(topic_key) or tv_map.get("anxiety") or {
        "primary": [topic],
        "secondary": [],
        "objects": [],
        "filtered": [],
    }
    hw_map = tax.get("hook_family_weights") or {}
    hw = hw_map.get(hook_family) or hw_map.get("_default") or {"keyword_boost": []}
    tf_map = tax.get("tone_filters") or {}
    tf = tf_map.get(tone) or tf_map.get("_default") or {}
    flavor_map = tax.get("persona_scene_flavor") or {}
    flavor = flavor_map.get(persona) or flavor_map.get("_default") or []

    primary = list(tv.get("primary") or [])
    objects = list(tv.get("objects") or [])
    secondary = list(tv.get("secondary") or [])
    filtered = list(tv.get("filtered") or []) + list(tf.get("filtered_extra") or [])
    hook_boost = list(hw.get("keyword_boost") or [])
    tone_boost = list(tf.get("keyword_boost") or [])
    allow = list(tax.get("concrete_noun_allowlist") or [])
    caption_nouns = extract_caption_nouns(caption, allow, max_n=2)
    phrase_boost = apply_phrase_boosts(caption, tax)

    keywords = _uniq(
        primary[:3]
        + hook_boost[:2]
        + list(flavor)[:2]
        + objects[:2]
        + caption_nouns
        + phrase_boost
        + secondary[:1]
        + tone_boost[:1]
    )
    required = _uniq([primary[0]] + ([flavor[0]] if flavor and any(x in flavor[0] for x in ("office", "workplace")) else []))
    if not required and primary:
        required = [primary[0]]

    sources = [
        f"topic:{topic}",
        f"hook_family:{hook_family or '_default'}",
        f"persona:{persona or '_default'}",
        f"beat_role:{beat_role}",
    ]
    if caption_nouns:
        sources.append("caption_nouns:" + ",".join(caption_nouns))
    if phrase_boost:
        sources.append("phrase_boost:" + ",".join(phrase_boost[:4]))

    objects_and_hooks = _uniq(objects + hook_boost + phrase_boost)

    return CompiledQuery(
        topic=topic,
        keywords=tuple(keywords),
        required_keywords=tuple(required[:2]),
        filtered_keywords=tuple(_uniq(filtered)),
        primary=tuple(_uniq(primary)),
        objects_and_hooks=tuple(objects_and_hooks),
        beat_role=beat_role,
        match_sources=tuple(sources),
    )


def score_asset(
    record: AssetRecord,
    compiled: CompiledQuery,
    taxonomy: dict[str, Any],
) -> tuple[float, list[str], bool]:
    """Return (score, matched_keywords, hit_filtered)."""
    cfg = taxonomy.get("scoring") or {}
    w_primary = float(cfg.get("primary_weight", 3.0))
    w_obj = float(cfg.get("object_hook_weight", 1.5))
    penalty = float(cfg.get("filtered_penalty", 5.0))
    folder_bonus = float(cfg.get("topic_folder_bonus", 0.5))

    asset_kw = set(record.keywords)
    # also tokenize metaphor/title lightly
    for blob in (record.metaphor, record.title, record.topic_folder):
        asset_kw.update(_TOKEN_RE.findall(_norm(blob).replace("_", " ")))
        asset_kw.update(_norm(x) for x in blob.lower().replace("-", " ").split())

    matched: list[str] = []
    score = 0.0
    for k in compiled.primary:
        if k in asset_kw or k.replace("_", "") in {a.replace("_", "") for a in asset_kw}:
            score += w_primary
            matched.append(k)
    for k in compiled.objects_and_hooks:
        if k in asset_kw:
            score += w_obj
            if k not in matched:
                matched.append(k)
    # residual keyword overlap
    for k in compiled.keywords:
        if k in asset_kw and k not in matched:
            score += 1.0
            matched.append(k)

    hit_filtered = False
    for bad in compiled.filtered_keywords:
        if bad and (bad in asset_kw or bad.replace("_", " ") in (record.title or "").lower()):
            score -= penalty
            hit_filtered = True
            break

    if record.topic_folder in {compiled.topic, compiled.topic.split("_")[0]} or compiled.topic in {
        "social_anxiety"
    } and record.topic_folder in {"loneliness", "social_anxiety", "anxiety"}:
        score += folder_bonus
    elif record.topic_folder == compiled.topic:
        score += folder_bonus

    return score, matched, hit_filtered


def select_asset(
    *,
    pool: Sequence[Path],
    topic: str,
    caption: str = "",
    persona: str = "",
    hook_family: str = "",
    tone: str = "",
    beat_role: str = "beat",
    seed: int = 0,
    taxonomy_path: Path | None = None,
    tag_store_path: Path | None = None,
    allow_weak_fallback: bool = True,
) -> SelectionResult:
    """Pick best pool image for caption/atom fields.

    Deterministic: same inputs → same path. Never silently uses seed%pool.
    If no keyword overlap reaches min score, either:
      - raise RuntimeError (allow_weak_fallback=False), or
      - return weak_topic_fallback with explicit match_quality (visible, not silent).
    """
    if not pool:
        raise ValueError("empty asset pool")

    tax = load_taxonomy(taxonomy_path)
    compiled = compile_query(
        topic=topic,
        caption=caption,
        persona=persona,
        hook_family=hook_family,
        tone=tone,
        beat_role=beat_role,
        taxonomy=tax,
    )
    records = load_tag_store(tag_store_path)
    by_path = {r.path.resolve(): r for r in records}
    # also index by name for relative path mismatches
    by_name = {r.path.name: r for r in records}

    min_aligned = float((tax.get("scoring") or {}).get("min_score_for_aligned", 1.5))

    scored: list[tuple[float, Path, list[str], AssetRecord | None]] = []
    for p in pool:
        rec = by_path.get(p.resolve()) or by_name.get(p.name)
        if rec is None:
            # untagged: folder-only signal
            rec = AssetRecord(path=p, topic_folder=topic, keywords={_norm(topic), _norm(p.parent.name)})
        score, matched, _hit = score_asset(rec, compiled, tax)
        scored.append((score, p, matched, rec))

    # sort by score desc, then path name for stability; seed breaks residual ties
    scored.sort(key=lambda t: (-t[0], t[1].name, (hash(str(t[1])) ^ seed) & 0xFFFFFFFF))
    best_score, best_path, matched, _rec = scored[0]

    if best_score >= min_aligned and matched:
        quality = "aligned"
        rationale = (
            f"CTQC match topic={topic} beat={beat_role}; "
            f"score={best_score:.2f}; matched={','.join(matched[:8])}; "
            f"sources={';'.join(compiled.match_sources)}"
        )
    else:
        if not allow_weak_fallback:
            raise RuntimeError(
                f"no keyword-aligned asset for topic={topic!r} caption={caption[:80]!r}; "
                f"best_score={best_score:.2f}. Refusing silent seed%pool fallback."
            )
        quality = "weak_topic_fallback"
        # Still pick argmax among pool (topic folder), never seed% — but mark loud.
        rationale = (
            f"WEAK_TOPIC_FALLBACK topic={topic} beat={beat_role}; "
            f"best_score={best_score:.2f} below min_aligned={min_aligned}; "
            f"matched={','.join(matched) or 'none'}; "
            f"sources={';'.join(compiled.match_sources)}; "
            f"NOT silent seed%pool — explicit weak quality"
        )

    return SelectionResult(
        path=best_path,
        keyword_score=float(best_score),
        match_quality=quality,
        match_rationale=rationale,
        matched_keywords=tuple(matched),
        compiled=compiled,
    )


def select_from_topic_pool(
    topic: str,
    pool: Sequence[Path],
    *,
    caption: str = "",
    beat_role: str = "beat",
    seed: int = 0,
    atom: Optional[dict[str, Any]] = None,
) -> SelectionResult:
    """Convenience wrapper used by build_video_snippet_bank retrofit."""
    atom = atom or {}
    return select_asset(
        pool=pool,
        topic=topic,
        caption=caption or str(atom.get("text") or ""),
        persona=str(atom.get("persona") or ""),
        hook_family=str(atom.get("hook_family") or ""),
        tone=str(atom.get("tone") or ""),
        beat_role=beat_role,
        seed=seed,
        allow_weak_fallback=True,
    )


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--caption", default="")
    ap.add_argument("--beat-role", default="beat")
    ap.add_argument("--persona", default="")
    ap.add_argument("--hook-family", default="")
    ap.add_argument("--pool-dir", type=Path, default=None)
    args = ap.parse_args()
    if args.pool_dir:
        pool = sorted(args.pool_dir.glob("*.jpeg")) + sorted(args.pool_dir.glob("*.jpg"))
    else:
        raise SystemExit("--pool-dir required for CLI smoke")
    result = select_asset(
        pool=pool,
        topic=args.topic,
        caption=args.caption,
        persona=args.persona,
        hook_family=args.hook_family,
        beat_role=args.beat_role,
    )
    print(result.path)
    print(result.match_quality, result.keyword_score)
    print(result.match_rationale)

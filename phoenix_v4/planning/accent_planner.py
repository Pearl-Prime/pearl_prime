"""
Planner-owned accent / story intelligence (v1).

Assigns sparse accent_beats, accent_budget, accent_signature, and story_mix_profile.
Renderer materializes planner-assigned accents only.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ACCENT_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "accent_banks"

ACCENT_CLASSES_V1 = frozenset(
    {
        "ENCOURAGEMENT",
        "CITED_EVIDENCE",
        "WISDOM_ESSENCE",
        "AUTHOR_COMMENTARY",
        "EXTERNAL_STORY",
    }
)

CLASS_DEFAULT_POSITIONS: Dict[str, Tuple[str, ...]] = {
    "ENCOURAGEMENT": ("after_EXERCISE", "after_turning_point"),
    "CITED_EVIDENCE": ("after_HOOK", "before_STORY"),
    "WISDOM_ESSENCE": ("after_REFLECTION", "before_THREAD"),
    "AUTHOR_COMMENTARY": ("after_REFLECTION", "after_EXERCISE", "before_THREAD"),
    "EXTERNAL_STORY": ("after_REFLECTION", "before_STORY", "after_HOOK"),
}

_TEACHER_NAME_TOKENS = frozenset(
    {
        "ahjan",
        "master wu",
        "master feung",
        "junko",
        "sai ma",
        "master sha",
        "dalai lama",
        "jagadguru",
    }
)


@dataclass(frozen=True)
class AccentBeat:
    class_: str
    accent_id: str
    position: str
    body: str
    keys: Dict[str, Any] = field(default_factory=dict)

    def to_plan_dict(self) -> Dict[str, Any]:
        return {
            "class": self.class_,
            "accent_id": self.accent_id,
            "position": self.position,
            "keys": dict(self.keys),
        }


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def locale_to_cluster(locale: Optional[str]) -> str:
    loc = (locale or "en-US").strip().replace("-", "_")
    if loc.lower() in ("en_us", "en"):
        return "en_US"
    return loc


def resolve_story_mix_profile(
    brand_id: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    repo_root: Path = REPO_ROOT,
) -> str:
    accent_profiles = _load_yaml(repo_root / "config" / "accent" / "brand_accent_profiles.yaml")
    pilot = (accent_profiles.get("pilot_cells") or {}).get(f"{persona_id}:{topic_id}")
    if isinstance(pilot, dict) and pilot.get("story_mix_profile"):
        return str(pilot["story_mix_profile"])
    data = _load_yaml(repo_root / "config" / "authoring" / "story_mix_profiles.yaml")
    return str((data.get("default_by_brand") or {}).get(brand_id) or "practical_credible")


def resolve_accent_budget(
    brand_id: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    repo_root: Path = REPO_ROOT,
) -> Tuple[Dict[str, int], str, float]:
    data = _load_yaml(repo_root / "config" / "accent" / "brand_accent_profiles.yaml")
    pilot = (data.get("pilot_cells") or {}).get(f"{persona_id}:{topic_id}")
    if isinstance(pilot, dict) and pilot.get("profile"):
        profile_name = str(pilot["profile"])
    else:
        profile_name = str(
            (data.get("default_by_brand") or {}).get(brand_id)
            or data.get("default_profile")
            or "minimal_accent"
        )
    profile = (data.get("profiles") or {}).get(profile_name) or {}
    budget = {k: int(v) for k, v in (profile.get("accent_budget") or {}).items() if k in ACCENT_CLASSES_V1}
    for cls in ACCENT_CLASSES_V1:
        budget.setdefault(cls, 0)
    return budget, profile_name, float(profile.get("max_accent_chapter_share", 0.25))


def compute_accent_signature(
    assignments: Sequence[Mapping[str, Any]],
    *,
    accent_budget: Mapping[str, int],
) -> str:
    counts = {k: 0 for k in ACCENT_CLASSES_V1}
    placements: List[Tuple[int, str, str]] = []
    for row in assignments:
        cls = str(row.get("class") or "")
        if cls in counts:
            counts[cls] += 1
        placements.append((int(row.get("chapter") or 0), cls, str(row.get("position") or "")))
    payload = {
        "budget": {k: int(accent_budget.get(k, 0)) for k in sorted(ACCENT_CLASSES_V1)},
        "counts": counts,
        "placements": sorted(placements),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _deterministic_rank(seed: str, key: str) -> int:
    return int(hashlib.sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()[:12], 16)


def _spread_chapters(candidates: List[int], count: int, seed: str, salt: str) -> List[int]:
    if count <= 0 or not candidates:
        return []
    ranked = sorted(candidates, key=lambda ch: _deterministic_rank(seed, f"{salt}:ch{ch}"))
    if count >= len(ranked):
        return ranked[:count]
    step = max(1, len(ranked) // count)
    picked = [ranked[i] for i in range(0, len(ranked), step)][:count]
    for ch in ranked:
        if len(picked) >= count:
            break
        if ch not in picked:
            picked.append(ch)
    return sorted(picked)[:count]


def _chapter_slot_types(ch: EnrichedChapter) -> List[str]:
    return [str(s.slot_type or "").strip().upper() for s in ch.slots if str(s.slot_type or "").strip()]


def _position_fits(position: str, slot_types: Sequence[str]) -> bool:
    st = list(slot_types)
    if position == "before_HOOK":
        return "HOOK" in st
    if position == "after_HOOK":
        return "HOOK" in st
    if position == "before_STORY":
        return any(x == "STORY" for x in st)
    if position == "after_EXERCISE":
        return "EXERCISE" in st
    if position == "after_REFLECTION":
        return "REFLECTION" in st
    if position == "before_THREAD":
        return "THREAD" in st
    if position == "after_PIVOT":
        return "PIVOT" in st
    if position == "after_INTEGRATION":
        return "INTEGRATION" in st
    if position == "after_turning_point":
        return st.count("STORY") >= 2
    return False


def _pick_position(accent_class: str, slot_types: Sequence[str], *, seed: str, chapter_number: int) -> Optional[str]:
    options = [p for p in CLASS_DEFAULT_POSITIONS.get(accent_class, ()) if _position_fits(p, slot_types)]
    if not options:
        return None
    return options[_deterministic_rank(seed, f"pos:{accent_class}:ch{chapter_number}") % len(options)]


def _locale_fit_ok(entry: Mapping[str, Any], locale_cluster: str) -> bool:
    fit = entry.get("locale_fit")
    if fit is None:
        return True
    if isinstance(fit, list):
        normalized = {str(x).strip() for x in fit}
        return "universal" in normalized or locale_cluster in normalized
    return str(fit).strip() in ("universal", locale_cluster)


def _composite_body_safe(body: str, *, composite_mode: bool) -> bool:
    if not composite_mode:
        return True
    lower = body.lower()
    return not any(tok in lower for tok in _TEACHER_NAME_TOKENS)


def _secular_entry_ok(entry: Mapping[str, Any], *, composite_mode: bool) -> bool:
    if not composite_mode:
        return True
    if entry.get("secular_safe") is False or entry.get("composite_safe") is False:
        return False
    return _composite_body_safe(_entry_body(entry), composite_mode=True)


def _entry_body(entry: Mapping[str, Any]) -> str:
    variants = entry.get("position_variants")
    if isinstance(variants, dict):
        for v in variants.values():
            if isinstance(v, dict) and v.get("body"):
                return str(v["body"]).strip()
    for key in ("body", "story", "claim", "text", "text_en"):
        val = entry.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    reg = entry.get("register_variants")
    if isinstance(reg, dict):
        sec = reg.get("secular")
        if isinstance(sec, dict) and sec.get("body"):
            return str(sec["body"]).strip()
    return ""


def _wrap_cited_evidence(claim: str, citation: str, *, position: str) -> str:
    handoff = (
        "Carry that evidence into the scene that follows."
        if position in ("after_HOOK", "before_STORY")
        else "Let that finding sit beside what you already know before the next beat."
    )
    return f"A documented finding worth naming before we go further. {claim.strip()} ({citation.strip()}). {handoff}"


def _wrap_external_story(story: str, source: str, *, position: str) -> str:
    handoff = (
        "Let that story echo through what happens next in this room."
        if position != "before_THREAD"
        else "Carry that image into the thread that follows."
    )
    return (
        f"This is not fiction from this book's cast — it is a cited story from elsewhere. "
        f"{story.strip()} Source: {source.strip()}. {handoff}"
    )


def _wrap_encouragement(prose: str, *, position: str) -> str:
    handoff = (
        "Take that recognition into the integration that follows."
        if position == "after_EXERCISE"
        else "Let that land before the next story beat."
    )
    return f"{prose.strip()}\n\n{handoff}".strip()


def _load_external_stories(topic: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    data = _load_yaml(ACCENT_BANKS / "external_stories" / f"{topic}_entries.yaml")
    clusters = data.get("clusters") or {}
    rows = list(clusters.get("universal") or []) + list(clusters.get(locale_cluster) or [])
    return [r for r in rows if isinstance(r, dict)]


def _load_cited_evidence(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    return [e for e in (_load_yaml(ACCENT_BANKS / "evidence" / topic / "entries.yaml").get("entries") or []) if isinstance(e, dict)]


def _load_wisdom_essence(topic: str, repo_root: Path) -> List[dict[str, Any]]:
    return [e for e in (_load_yaml(ACCENT_BANKS / "wisdom_essence" / topic / "entries.yaml").get("entries") or []) if isinstance(e, dict)]


def _load_author_commentary(topic: str, author_id: str, locale_cluster: str, repo_root: Path) -> List[dict[str, Any]]:
    data = _load_yaml(ACCENT_BANKS / "author_commentary" / topic / author_id / f"{locale_cluster}.yaml")
    return [r for r in (data.get("commentaries") or data.get("entries") or []) if isinstance(r, dict)]


def _load_encouragement_pool(persona_id: str, topic_id: str, repo_root: Path) -> List[dict[str, Any]]:
    out: List[dict[str, Any]] = []
    for sub in ("PERMISSION_GRANT", "PERMISSION"):
        path = repo_root / "atoms" / persona_id / topic_id / sub / "CANONICAL.txt"
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        for i, block in enumerate(re.split(r"(?m)^##\s+\S+\s+v\d+", raw)):
            prose = re.sub(r"(?ms)^---\s*$.*?^---\s*$", "", block).strip()
            if len(prose.split()) < 12:
                continue
            out.append({"accent_id": f"enc_{persona_id}_{topic_id}_{sub.lower()}_v{i:02d}", "body": prose, "secular_safe": True, "topic_keys": [topic_id]})
    return out


def _topic_match(entry: Mapping[str, Any], topic_id: str) -> bool:
    keys = entry.get("topic_keys") or []
    return not keys or topic_id in keys


def _entry_id(entry: Mapping[str, Any]) -> str:
    return str(entry.get("accent_id") or entry.get("story_id") or entry.get("evidence_id") or entry.get("essence_id") or entry.get("commentary_id") or "")


def _select_entry(pool: Sequence[Mapping[str, Any]], *, accent_class: str, topic_id: str, locale_cluster: str, composite_mode: bool, seed: str, chapter_number: int, used_ids: set[str]) -> Optional[dict[str, Any]]:
    candidates = []
    for row in pool:
        if not _topic_match(row, topic_id) or not _locale_fit_ok(row, locale_cluster) or not _secular_entry_ok(row, composite_mode=composite_mode):
            continue
        aid = _entry_id(row)
        if aid and aid in used_ids:
            continue
        if len(_entry_body(row).split()) < 8:
            continue
        candidates.append(dict(row))
    if not candidates:
        return None
    return candidates[_deterministic_rank(seed, f"pick:{accent_class}:ch{chapter_number}") % len(candidates)]


def _resolve_body(accent_class: str, entry: Mapping[str, Any], *, position: str, composite_mode: bool) -> Tuple[str, str]:
    if accent_class == "CITED_EVIDENCE":
        aid = str(entry.get("evidence_id") or "cited_unknown")
        return aid, _wrap_cited_evidence(str(entry.get("claim") or _entry_body(entry)), str(entry.get("citation") or ""), position=position)
    if accent_class == "EXTERNAL_STORY":
        aid = str(entry.get("story_id") or "ext_unknown")
        return aid, _wrap_external_story(str(entry.get("story") or ""), str(entry.get("source") or ""), position=position)
    if accent_class == "WISDOM_ESSENCE":
        reg = entry.get("register_variants") or {}
        sec = reg.get("secular") if isinstance(reg, dict) else {}
        return str(entry.get("essence_id") or "we_unknown"), str((sec or {}).get("body") or _entry_body(entry))
    if accent_class == "AUTHOR_COMMENTARY":
        variants = entry.get("position_variants") or {}
        pv = variants.get(position) if isinstance(variants, dict) else {}
        return str(entry.get("commentary_id") or "ac_unknown"), str((pv or {}).get("body") or _entry_body(entry))
    if accent_class == "ENCOURAGEMENT":
        return str(entry.get("accent_id") or "enc_unknown"), _wrap_encouragement(_entry_body(entry), position=position)
    return str(entry.get("accent_id") or "accent_unknown"), _entry_body(entry)


def plan_accent_beats_for_book(
    enriched: EnrichedBook,
    *,
    brand_id: str = "phoenix",
    author_id: Optional[str] = None,
    seed: str = "",
    locale: Optional[str] = None,
    teacher_mode: bool = False,
    repo_root: Path = REPO_ROOT,
) -> Tuple[Dict[str, int], str, List[Dict[str, Any]], str, Dict[int, List[AccentBeat]]]:
    persona_id, topic_id = enriched.persona_id, enriched.topic
    accent_budget, _, share_cap = resolve_accent_budget(brand_id, persona_id=persona_id, topic_id=topic_id, repo_root=repo_root)
    story_mix_profile = resolve_story_mix_profile(brand_id, persona_id=persona_id, topic_id=topic_id, repo_root=repo_root)
    if sum(accent_budget.values()) <= 0:
        return accent_budget, story_mix_profile, [], compute_accent_signature([], accent_budget=accent_budget), {}

    locale_cluster = locale_to_cluster(locale or getattr(enriched, "locale", None))
    composite_mode = not teacher_mode and not enriched.teacher_id
    pools = {
        "EXTERNAL_STORY": _load_external_stories(topic_id, locale_cluster, repo_root),
        "CITED_EVIDENCE": _load_cited_evidence(topic_id, repo_root),
        "WISDOM_ESSENCE": _load_wisdom_essence(topic_id, repo_root),
        "AUTHOR_COMMENTARY": _load_author_commentary(topic_id, author_id or "ravi_chandra", locale_cluster, repo_root),
        "ENCOURAGEMENT": _load_encouragement_pool(persona_id, topic_id, repo_root),
    }

    used_ids: set[str] = set()
    chapter_assignments: Dict[int, List[AccentBeat]] = {}
    flat_rows: List[Dict[str, Any]] = []
    anchor_chapters: List[int] = []

    for accent_class, budget in accent_budget.items():
        if budget <= 0 or not pools.get(accent_class):
            continue
        candidates = [
            ch.number
            for ch in enriched.chapters
            if _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch.number)
        ]
        prefer = [c for c in candidates if c in anchor_chapters]
        pick_from = prefer if prefer else candidates
        picked = _spread_chapters(pick_from, budget, seed, accent_class)
        if not picked and candidates:
            picked = _spread_chapters(candidates, budget, seed, accent_class)
        for ch_num in picked:
            ch = next((c for c in enriched.chapters if c.number == ch_num), None)
            if ch is None:
                continue
            if any(b.class_ == accent_class for beats in chapter_assignments.values() for b in beats):
                continue
            position = _pick_position(accent_class, _chapter_slot_types(ch), seed=seed, chapter_number=ch_num)
            if not position:
                continue
            entry = _select_entry(
                pools[accent_class],
                accent_class=accent_class,
                topic_id=topic_id,
                locale_cluster=locale_cluster,
                composite_mode=composite_mode,
                seed=seed,
                chapter_number=ch_num,
                used_ids=used_ids,
            )
            if not entry:
                continue
            accent_id, body = _resolve_body(accent_class, entry, position=position, composite_mode=composite_mode)
            if not body or not _composite_body_safe(body, composite_mode=composite_mode):
                continue
            used_ids.add(accent_id)
            beat = AccentBeat(accent_class, accent_id, position, body, {"topic_id": topic_id, "persona_id": persona_id})
            chapter_assignments.setdefault(ch_num, []).append(beat)
            flat_rows.append({"chapter": ch_num, "class": accent_class, "accent_id": accent_id, "position": position, "keys": dict(beat.keys)})
            if ch_num not in anchor_chapters:
                anchor_chapters.append(ch_num)

    total_chapters = max(1, len(enriched.chapters))
    if share_cap > 0 and flat_rows:
        max_chapters = max(1, int(total_chapters * share_cap))
        trim_order = ["WISDOM_ESSENCE", "AUTHOR_COMMENTARY", "ENCOURAGEMENT", "CITED_EVIDENCE", "EXTERNAL_STORY"]
        beats_by_id = {b.accent_id: b for beats in chapter_assignments.values() for b in beats}

        def _chapter_count(rows: List[Dict[str, Any]]) -> int:
            return len({int(r["chapter"]) for r in rows})

        while flat_rows and _chapter_count(flat_rows) > max_chapters:
            removed = False
            for cls in trim_order:
                for i in range(len(flat_rows) - 1, -1, -1):
                    if flat_rows[i]["class"] == cls:
                        flat_rows.pop(i)
                        removed = True
                        break
                if removed:
                    break
            if not removed:
                flat_rows.pop()
        chapter_assignments = {}
        for row in flat_rows:
            beat = beats_by_id.get(str(row["accent_id"]))
            if beat:
                chapter_assignments.setdefault(int(row["chapter"]), []).append(beat)

    signature = compute_accent_signature(flat_rows, accent_budget=accent_budget)
    return accent_budget, story_mix_profile, flat_rows, signature, chapter_assignments


def attach_accent_plan(
    enriched: EnrichedBook,
    *,
    brand_id: str = "phoenix",
    author_id: Optional[str] = None,
    seed: str = "",
    locale: Optional[str] = None,
    teacher_mode: bool = False,
    repo_root: Path = REPO_ROOT,
) -> EnrichedBook:
    accent_budget, story_mix_profile, flat_rows, signature, chapter_assignments = plan_accent_beats_for_book(
        enriched,
        brand_id=brand_id,
        author_id=author_id,
        seed=seed,
        locale=locale,
        teacher_mode=teacher_mode,
        repo_root=repo_root,
    )
    new_chapters = []
    for ch in enriched.chapters:
        beats = chapter_assignments.get(ch.number, [])
        new_chapters.append(
            replace(
                ch,
                accent_beats=[b.to_plan_dict() for b in beats],
                accent_bodies={b.accent_id: b.body for b in beats},
            )
        )
    spine_context = dict(enriched.spine_context or {})
    spine_context.update(
        {
            "accent_budget": dict(accent_budget),
            "accent_signature": signature,
            "story_mix_profile": story_mix_profile,
            "accent_assignments": list(flat_rows),
            "brand_id": brand_id,
        }
    )
    audit = dict(enriched.enrichment_audit or {})
    audit["accent_planner"] = {
        "accent_budget": dict(accent_budget),
        "accent_signature": signature,
        "story_mix_profile": story_mix_profile,
        "assignment_count": len(flat_rows),
    }
    return replace(enriched, chapters=new_chapters, spine_context=spine_context, enrichment_audit=audit)


def validate_accent_plan(enriched: EnrichedBook) -> List[str]:
    errors: List[str] = []
    ctx = enriched.spine_context or {}
    budget = ctx.get("accent_budget") or {}
    assignments = ctx.get("accent_assignments") or []
    counts: Dict[str, int] = {}
    chapters_with: set[int] = set()
    for row in assignments:
        cls = str(row.get("class") or "")
        counts[cls] = counts.get(cls, 0) + 1
        chapters_with.add(int(row.get("chapter") or 0))
    for cls, cap in budget.items():
        if counts.get(cls, 0) > int(cap):
            errors.append(f"accent_budget exceeded for {cls}: {counts.get(cls, 0)} > {cap}")
    total = max(1, len(enriched.chapters))
    _, _, share_cap = resolve_accent_budget(
        str(ctx.get("brand_id") or "phoenix"),
        persona_id=enriched.persona_id,
        topic_id=enriched.topic,
    )
    if share_cap > 0 and len(chapters_with) / total > share_cap + 1e-9:
        errors.append(f"accent chapter share {len(chapters_with)/total:.2f} exceeds cap {share_cap}")
    return errors

"""
Deterministic teacher-owned / hybrid brand identity generator.

No live LLM. Seeds from (teacher_id, seed[, archetype_id]) the same way
phoenix_v4/naming/generator.py seeds title candidates — reproducible shuffle
over doctrine themes + positioning profiles + consumer-language / invisible-script
banks. Writes to config/brand_management/teacher_originated_brands.yaml only
(never mutates the fixed 40×14 unified registry rows).

Authority: Pearl_Prez (brand_admin) + Pearl_Editor (teacher_mode).
Q-BRAND-GEN-01/02/03 defaults: separate registry; seeded composition; lazy hybrids.
"""
from __future__ import annotations

import hashlib
import random
import re
from pathlib import Path
from typing import Any, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TEACHER_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
UNIFIED_REGISTRY = REPO_ROOT / "config" / "brand_management" / "global_brand_registry_unified.yaml"
TEACHER_ORIGINATED = REPO_ROOT / "config" / "brand_management" / "teacher_originated_brands.yaml"
POSITIONING = REPO_ROOT / "config" / "authoring" / "author_positioning_profiles.yaml"
CONSUMER_LANG = REPO_ROOT / "config" / "marketing" / "consumer_language_by_topic.yaml"
INVISIBLE_SCRIPTS = REPO_ROOT / "config" / "marketing" / "invisible_scripts_by_persona_topic.yaml"
PUBLIC_INDEX = REPO_ROOT / "brand-wizard-app" / "public" / "teacher_originated_brands.json"

_DOCTRINE_DIRS = ("TEACHER_DOCTRINE", "COMPRESSION", "REFLECTION", "TEACHING")
_WORD_RE = re.compile(r"[a-z0-9']+", re.I)

# Display-name stems composed with doctrine tokens (seeded pick).
_BRAND_STEMS = (
    "Press",
    "Path",
    "Studio",
    "House",
    "Line",
    "Works",
    "Field",
    "Atelier",
    "Institute",
    "Library",
)

_DURATION_STRATEGIES = (
    "short_form_daily_practice",
    "seasonal_arc_series",
    "deep_companion_volumes",
    "micro_dose_then_deepen",
)

_COVER_TREATMENTS = (
    "typographic_mark_on_field",
    "abstract_ink_wash",
    "minimal_geometry",
    "warm_paper_grain",
    "high_contrast_glyph",
)

_PRICING = ("accessible", "mid_tier", "premium_companion")


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if data is not None else {}


def _seed_int(*parts: str) -> int:
    seed_str = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(seed_str.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:48] or "brand"


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _WORD_RE.findall(text or "") if len(t) > 2}


def token_overlap_ratio(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def _read_doctrine_snippets(teacher_id: str, limit: int = 24) -> list[str]:
    root = TEACHER_BANKS / teacher_id / "approved_atoms"
    if not root.is_dir():
        raise FileNotFoundError(f"No approved_atoms for teacher_id={teacher_id!r} under {TEACHER_BANKS}")
    snippets: list[str] = []
    for dirname in _DOCTRINE_DIRS:
        d = root / dirname
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.yaml")) + sorted(d.glob("*.yml")):
            try:
                data = _load_yaml(path)
            except Exception:
                continue
            body = ""
            if isinstance(data, dict):
                body = str(data.get("body") or data.get("text") or data.get("content") or "")
                if not body and isinstance(data.get("layers"), dict):
                    body = " ".join(str(v) for v in data["layers"].values() if v)
            if body.strip():
                snippets.append(body.strip())
            if len(snippets) >= limit:
                return snippets
        # also accept CANONICAL.txt banks
        for path in sorted(d.rglob("CANONICAL.txt")):
            body = path.read_text(encoding="utf-8", errors="ignore").strip()
            if body:
                snippets.append(body[:800])
            if len(snippets) >= limit:
                return snippets
    if not snippets:
        raise ValueError(f"No doctrine/compression atoms readable for teacher_id={teacher_id!r}")
    return snippets


def _theme_words(snippets: list[str], rng: random.Random, n: int = 8) -> list[str]:
    counts: dict[str, int] = {}
    stop = {
        "the", "and", "that", "this", "with", "from", "your", "you", "for", "are",
        "not", "but", "can", "into", "when", "what", "have", "has", "was", "were",
        "they", "their", "them", "then", "than", "also", "just", "about", "will",
        "there", "here", "been", "being", "over", "under", "more", "some", "only",
        "very", "much", "such", "like", "make", "made", "does", "done", "down",
        "life", "place", "where", "which", "while", "would", "could", "should",
    }
    for s in snippets:
        for tok in _tokens(s):
            if tok in stop or len(tok) < 5:
                continue
            counts[tok] = counts.get(tok, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    pool = [w for w, _ in ranked[:40]] or ["presence", "practice", "clarity"]
    # Prefer highest-signal words first (deterministic order), then light shuffle of tail.
    head = pool[: max(3, n // 2)]
    tail = pool[len(head) :]
    rng.shuffle(tail)
    out = (head + tail)[:n]
    return out if out else ["presence", "practice", "clarity"]


def _pick_positioning(rng: random.Random, themes: list[str]) -> tuple[str, dict]:
    data = _load_yaml(POSITIONING)
    profiles = data.get("profiles") if isinstance(data, dict) else {}
    if not isinstance(profiles, dict) or not profiles:
        return "elder_stabilizer", {
            "authority_type": "seasoned_practitioner",
            "trust_anchor_style": "elder",
            "vulnerability_band": "low",
        }
    keys = list(profiles.keys())
    # Bias: spiritual/doctrine words → devotional; body words → somatic; else elder/research
    joined = " ".join(themes).lower()
    if any(w in joined for w in ("body", "breath", "somatic", "nervous", "felt")):
        prefer = "somatic_companion"
    elif any(w in joined for w in ("grace", "sacred", "spirit", "devotion", "surrender")):
        prefer = "devotional_companion"
    elif any(w in joined for w in ("study", "research", "evidence", "pattern")):
        prefer = "research_guide"
    else:
        prefer = "elder_stabilizer"
    if prefer in profiles and rng.random() < 0.7:
        key = prefer
    else:
        key = rng.choice(keys)
    return key, dict(profiles[key] or {})


def _consumer_phrases(rng: random.Random, n: int = 3) -> list[str]:
    data = _load_yaml(CONSUMER_LANG)
    topics = data.get("topics") if isinstance(data, dict) else None
    phrases: list[str] = []
    if isinstance(topics, list):
        for topic in topics:
            if not isinstance(topic, dict):
                continue
            for p in topic.get("consumer_phrases") or []:
                if isinstance(p, str) and p.strip():
                    phrases.append(p.strip())
    if not phrases:
        phrases = ["why does this keep happening", "i need a steadier way through"]
    return rng.sample(phrases, min(n, len(phrases)))


def _invisible_script_hooks(rng: random.Random, n: int = 2) -> list[str]:
    data = _load_yaml(INVISIBLE_SCRIPTS)
    scripts = data.get("scripts") if isinstance(data, dict) else None
    hooks: list[str] = []
    if isinstance(scripts, list):
        for row in scripts:
            if not isinstance(row, dict):
                continue
            for key in ("invisible_script", "reframe", "hook", "script"):
                val = row.get(key)
                if isinstance(val, str) and val.strip():
                    hooks.append(val.strip())
                    break
    elif isinstance(scripts, dict):
        for row in scripts.values():
            if isinstance(row, dict):
                for val in row.values():
                    if isinstance(val, str) and len(val) > 20:
                        hooks.append(val.strip())
            elif isinstance(row, str) and len(row) > 20:
                hooks.append(row.strip())
    if not hooks:
        hooks = ["The alarm is lying — your body can learn a quieter signal."]
    return rng.sample(hooks, min(n, len(hooks)))


def _title_case_token(tok: str) -> str:
    return tok[:1].upper() + tok[1:] if tok else tok


def _compose_display_name(teacher_id: str, themes: list[str], rng: random.Random) -> str:
    # Sibling to naming.generator seeded pick — not a fork of title templates.
    human = teacher_id.replace("_", " ").title()
    theme = _title_case_token(rng.choice(themes)) if themes else "Presence"
    stem = rng.choice(_BRAND_STEMS)
    pattern = rng.choice(
        [
            f"{human} {stem}",
            f"{theme} {stem}",
            f"{human}'s {theme} {stem}",
            f"The {theme} {stem}",
        ]
    )
    return pattern


def _archetype_ids() -> list[str]:
    # Prefer the compact public list (avoids parsing the 560-row unified YAML).
    public_list = REPO_ROOT / "brand-wizard-app" / "public" / "brand_archetype_ids.json"
    if public_list.exists():
        try:
            import json

            data = json.loads(public_list.read_text(encoding="utf-8")) or {}
            arches = data.get("archetypes") if isinstance(data, dict) else None
            if isinstance(arches, list) and arches:
                return sorted({str(a) for a in arches if a})
        except Exception:
            pass
    data = _load_yaml(UNIFIED_REGISTRY)
    brands = data.get("brands") if isinstance(data, dict) else {}
    ids: set[str] = set()
    if isinstance(brands, dict):
        for row in brands.values():
            if isinstance(row, dict) and row.get("brand_archetype_id"):
                ids.add(str(row["brand_archetype_id"]))
    return sorted(ids)


def _archetype_identity(archetype_id: str) -> dict[str, Any]:
    # Stream only the matching en_US row — do not yaml-load the full 560-brand file.
    target_key = f"{archetype_id}_en_us:"
    sample: Optional[dict] = None
    if UNIFIED_REGISTRY.exists():
        try:
            text = UNIFIED_REGISTRY.read_text(encoding="utf-8")
            # Find brand block start for this archetype's en_US row
            needle = f"\n  {archetype_id}_en_us:\n"
            idx = text.find(needle)
            if idx < 0:
                needle = f"\n  {archetype_id}_en_US:\n"
                idx = text.find(needle)
            if idx >= 0:
                chunk = text[idx + 1 : idx + 2500]
                # Terminate at next brand_id key at indent 2
                end = chunk.find("\n  ", 3)
                block = chunk if end < 0 else chunk[:end]
                parsed = yaml.safe_load(block)
                if isinstance(parsed, dict) and len(parsed) == 1:
                    sample = next(iter(parsed.values()))
        except Exception:
            sample = None
    if not isinstance(sample, dict):
        # Minimal fallback so hybrid generation still works offline
        return {
            "brand_archetype_id": archetype_id,
            "display_name": archetype_id.replace("_", " ").title(),
            "publication_corp": archetype_id.replace("_", " ").title(),
            "brand_focus": f"{archetype_id.replace('_', ' ')} catalog angle",
            "mission": "",
            "tradition": "",
            "primary_topics": ["anxiety"],
            "primary_personas": [],
        }
    return {
        "brand_archetype_id": archetype_id,
        "display_name": sample.get("display_name") or archetype_id,
        "publication_corp": sample.get("publication_corp") or sample.get("display_name"),
        "brand_focus": sample.get("brand_focus") or "",
        "mission": sample.get("mission") or "",
        "tradition": sample.get("tradition") or "",
        "primary_topics": list(sample.get("primary_topics") or []),
        "primary_personas": list(sample.get("primary_personas") or []),
    }


def load_teacher_originated_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or TEACHER_ORIGINATED
    data = _load_yaml(p)
    if not isinstance(data, dict):
        data = {}
    data.setdefault("schema_version", "1.0")
    data.setdefault("source", "teacher_originated")
    data.setdefault("brands", {})
    if not isinstance(data["brands"], dict):
        data["brands"] = {}
    return data


def _write_registry(data: dict[str, Any], path: Path | None = None) -> Path:
    p = path or TEACHER_ORIGINATED
    p.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    p.write_text(text, encoding="utf-8")
    # Mirror a compact public index for brandMatch.js (Q-BRAND-GEN-01 wiring).
    import json

    public = {}
    for bid, row in (data.get("brands") or {}).items():
        if not isinstance(row, dict):
            continue
        attribution = row.get("attribution_mode") or "named"
        # Named teacher-owned brands are assignable as teacher brands; hybrids are
        # generalized escape hatches and must NOT re-enter the teacher exclusivity ledger.
        public[bid] = {
            "d": row.get("display_name") or bid,
            "t": row.get("origin_teacher_id") or "",
            "tid": row.get("origin_teacher_id") or "",
            "is_teacher": attribution == "named",
            "arch": row.get("hybrid_of_archetype") or "teacher_originated",
            "lane": (row.get("lane_id") or "en_US").replace("-", "_"),
            "buildable": row.get("buildable", True),
            "source": row.get("source") or "teacher_originated",
            "attribution_mode": attribution,
            "tr": row.get("tradition") or "",
            "tp": list(row.get("primary_topics") or []),
            "f": (row.get("brand_focus") or "")[:80],
        }
    PUBLIC_INDEX.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_INDEX.write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def register_brand(brand: dict[str, Any], *, path: Path | None = None) -> dict[str, Any]:
    data = load_teacher_originated_registry(path)
    bid = brand["brand_id"]
    data["brands"][bid] = brand
    data["total_brands"] = len(data["brands"])
    _write_registry(data, path)
    return brand


def list_available_hybrid_archetypes(teacher_id: str, lane: str = "en_US") -> list[str]:
    """Archetypes not yet hybridized for this teacher in this lane (max 40)."""
    data = load_teacher_originated_registry()
    used: set[str] = set()
    for row in (data.get("brands") or {}).values():
        if not isinstance(row, dict):
            continue
        if row.get("origin_teacher_id") != teacher_id:
            continue
        if row.get("attribution_mode") != "generalized":
            continue
        if str(row.get("lane_id") or "en_US") != lane:
            continue
        arch = row.get("hybrid_of_archetype")
        if arch:
            used.add(str(arch))
    return [a for a in _archetype_ids() if a not in used]


def generate_teacher_owned_brand(
    teacher_id: str,
    *,
    seed: str = "v1",
    lane_id: str = "en_US",
    register: bool = False,
) -> dict[str, Any]:
    """Named teacher-owned brand (Phase B). Deterministic from (teacher_id, seed, lane)."""
    rng = random.Random(_seed_int("teacher_owned", teacher_id, seed, lane_id))
    snippets = _read_doctrine_snippets(teacher_id)
    themes = _theme_words(snippets, rng)
    pos_key, pos = _pick_positioning(rng, themes)
    phrases = _consumer_phrases(rng)
    hooks = _invisible_script_hooks(rng)
    display = _compose_display_name(teacher_id, themes, rng)
    lane_norm = lane_id.replace("-", "_")
    lane_suffix = lane_norm.lower()
    brand_id = f"to_{_slug(teacher_id)}_{lane_suffix}"
    doctrine_lead = snippets[0][:180].rstrip(".")
    # Second snippet anchors differentiation (teachers share little overlapping doctrine text).
    doctrine_b = (snippets[1] if len(snippets) > 1 else snippets[0])[:160].rstrip(".")
    emotional = {
        "core": themes[:4],
        "bridge_phrases": phrases,
        "doctrine_markers": themes[:6],
        "doctrine_fingerprint": [s[:120] for s in snippets[:3]],
        "allowed_language": list(pos.get("allowed_language") or []),
        "forbidden_language": list(pos.get("forbidden_language") or []),
    }
    emo_templates = [
        f"When {themes[0]} tightens, remember: {doctrine_lead}",
        f"Move from alarm into {themes[0]} — {doctrine_b}",
        f"Let {themes[0]} replace the false urgency: {doctrine_lead}",
    ]
    fun_templates = [
        f"Daily {themes[1] if len(themes) > 1 else themes[0]} drills drawn from {teacher_id.replace('_', ' ')}'s teaching voice",
        f"A {pos_key.replace('_', ' ')} path: {doctrine_b}",
        f"Practice sequences built on {', '.join(themes[:3])}",
    ]
    gtm = {
        "emotional_job": emo_templates[rng.randrange(len(emo_templates))],
        "functional_job": fun_templates[rng.randrange(len(fun_templates))],
        "discovery_hook": hooks[0] if hooks else f"{doctrine_lead}.",
        "positioning_profile": pos_key,
        "authority_type": pos.get("authority_type"),
        "trust_anchor_style": pos.get("trust_anchor_style"),
        "teacher_doctrine_lead": doctrine_lead,
        "teacher_doctrine_secondary": doctrine_b,
    }
    brand = {
        "brand_id": brand_id,
        "lane_id": lane_norm,
        "locale": lane_norm.replace("_", "-"),
        "display_name": display,
        "publication_corp": display,
        "source": "teacher_originated",
        "origin_teacher_id": teacher_id,
        "attribution_mode": "named",
        "hybrid_of_archetype": None,
        "buildable": True,
        "teacher_mode": True,
        "tradition": f"Teacher-originated · {teacher_id}",
        "brand_focus": f"Doctrine-led catalog for {teacher_id.replace('_', ' ')}",
        "primary_topics": ["anxiety", "burnout", "self_worth"][:],
        "gtm_identity": gtm,
        "emotional_vocabulary": emotional,
        "duration_strategy": rng.choice(_DURATION_STRATEGIES),
        "cover_art_identity": {
            "treatment": rng.choice(_COVER_TREATMENTS),
            "mark_motif": themes[0] if themes else "circle",
            "note": "Reuses brand-driven cover system (render_kdp_cover / abstract_cover_art); no new cover pipeline.",
        },
        "pricing_posture": rng.choice(_PRICING),
        "mission": f"Carry {teacher_id.replace('_', ' ')}'s doctrine into a named brand readers can trust.",
        "generation": {
            "engine": "phoenix_v4.brand_generation.teacher_brand_generator",
            "seed": seed,
            "deterministic": True,
            "llm": False,
            "doctrine_snippet_count": len(snippets),
            "themes": themes,
        },
    }
    if register:
        register_brand(brand)
    return brand


def generate_hybrid_brand(
    teacher_id: str,
    archetype_id: str,
    *,
    seed: str = "v1",
    lane_id: str = "en_US",
    register: bool = False,
) -> dict[str, Any]:
    """
    Generalized hybrid: teacher doctrine (no-name attribution) × one of the 40 archetypes.
    Lazy — only call on explicit accept of a second-claim offer (Q-BRAND-GEN-03).
    """
    available = list_available_hybrid_archetypes(teacher_id, lane_id)
    if archetype_id not in available:
        # Cap or already hybridized
        if not available:
            raise ValueError(
                f"hybrid_cap_reached: teacher={teacher_id} lane={lane_id} already has "
                f"{len(_archetype_ids())} hybrids (ceiling 40)"
            )
        raise ValueError(
            f"hybrid_already_exists_or_unknown: archetype={archetype_id} teacher={teacher_id} "
            f"lane={lane_id}; available={available[:5]}..."
        )

    rng = random.Random(_seed_int("hybrid", teacher_id, archetype_id, seed, lane_id))
    snippets = _read_doctrine_snippets(teacher_id)
    themes = _theme_words(snippets, rng)
    arch = _archetype_identity(archetype_id)
    pos_key, pos = _pick_positioning(rng, themes)
    phrases = _consumer_phrases(rng)
    hooks = _invisible_script_hooks(rng)

    # Compose identity from BOTH sources — must differ from pure teacher-owned AND stock archetype.
    arch_name = str(arch.get("display_name") or archetype_id)
    theme = _title_case_token(themes[0]) if themes else "Doctrine"
    display = f"{arch_name} × {theme} Path"
    lane_norm = lane_id.replace("-", "_")
    lane_suffix = lane_norm.lower()
    brand_id = f"hy_{_slug(teacher_id)}_{_slug(archetype_id)}_{lane_suffix}"

    gtm = {
        "emotional_job": f"{arch.get('brand_focus') or arch_name}: meet it through {themes[0]} without naming the teacher",
        "functional_job": f"Generalized doctrine practice aligned to {archetype_id.replace('_', ' ')}",
        "discovery_hook": hooks[0] if hooks else phrases[0],
        "positioning_profile": pos_key,
        "authority_type": pos.get("authority_type"),
        "trust_anchor_style": pos.get("trust_anchor_style"),
        "archetype_mission_echo": (arch.get("mission") or "")[:200],
        "doctrine_lead": snippets[0][:160],
    }
    emotional = {
        "core": themes[:3] + [archetype_id.replace("_", " ")],
        "bridge_phrases": phrases,
        "doctrine_markers": themes[:6],
        "archetype_focus_tokens": list(_tokens(str(arch.get("brand_focus") or "")))[:6],
        "allowed_language": list(pos.get("allowed_language") or []),
        "forbidden_language": list(pos.get("forbidden_language") or []) + ["named_teacher_attribution"],
    }
    brand = {
        "brand_id": brand_id,
        "lane_id": lane_norm,
        "locale": lane_norm.replace("_", "-"),
        "display_name": display,
        "publication_corp": display,
        "source": "teacher_originated",
        "origin_teacher_id": teacher_id,
        "attribution_mode": "generalized",
        "hybrid_of_archetype": archetype_id,
        "buildable": True,
        "teacher_mode": True,
        # Reader-facing copy must stay nameless (generalized attribution).
        "tradition": arch.get("tradition") or f"Hybrid · generalized doctrine × {archetype_id}",
        "brand_focus": f"{arch.get('brand_focus') or arch_name} via generalized doctrine",
        "primary_topics": list(arch.get("primary_topics") or ["anxiety"])[:6],
        "primary_personas": list(arch.get("primary_personas") or [])[:4],
        "gtm_identity": gtm,
        "emotional_vocabulary": emotional,
        "duration_strategy": rng.choice(_DURATION_STRATEGIES),
        "cover_art_identity": {
            "treatment": rng.choice(_COVER_TREATMENTS),
            "mark_motif": themes[0] if themes else archetype_id,
            "note": "Brand-driven cover system keys off brand_id the same as the 40 archetypes.",
        },
        "pricing_posture": rng.choice(_PRICING),
        "mission": (
            f"Offer grounded doctrine in generalized attribution, "
            f"angled through the {archetype_id.replace('_', ' ')} archetype."
        ),
        "generation": {
            "engine": "phoenix_v4.brand_generation.teacher_brand_generator",
            "seed": seed,
            "mode": "generalized_hybrid",
            "deterministic": True,
            "llm": False,
            "doctrine_snippet_count": len(snippets),
            "themes": themes,
            "archetype_id": archetype_id,
        },
    }
    if register:
        register_brand(brand)
    return brand


def brand_ids() -> set[str]:
    data = load_teacher_originated_registry()
    return set((data.get("brands") or {}).keys())

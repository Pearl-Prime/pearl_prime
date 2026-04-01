#!/usr/bin/env python3
"""Generate a manga EI character-author profile.

Takes (brand_id, genre, locale, topic, persona_demographic) and produces a
manga author YAML profile.  Validates no collision with existing pen-name
authors or other manga authors within the same brand.

Usage:
    python scripts/manga/generate_manga_author.py \
        --brand-id stillness_press \
        --genre iyashikei \
        --locale en_US \
        --topic anxiety \
        --demographic anxious_millennials_urban

    # Preview without writing:
    python scripts/manga/generate_manga_author.py \
        --brand-id stillness_press \
        --genre iyashikei \
        --locale en_US \
        --topic anxiety \
        --demographic anxious_millennials_urban \
        --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_REGISTRY = REPO_ROOT / "config" / "brand_registry.yaml"
PEN_NAME_PROFILES_JSON = REPO_ROOT / "config" / "authoring" / "pen_name_teacher_profiles_full.json"
PEN_NAME_PROFILES_YAML = REPO_ROOT / "config" / "authoring" / "pen_name_teacher_profiles.yaml"
MANGA_AUTHORS_DIR = REPO_ROOT / "config" / "authoring" / "manga_authors"

# ---------------------------------------------------------------------------
# Genre ↔ name generation tables
# ---------------------------------------------------------------------------

# Locale-aware name component pools.  Each genre has themed name parts; the
# deterministic hash selects from them.

_EN_GIVEN_NAMES: dict[str, list[str]] = {
    "iyashikei":  ["Hana", "Mira", "Lumi", "Sage", "Wren", "Fern", "Dove", "Cove", "Petal", "Brook"],
    "seinen":     ["Ash", "Grey", "Vex", "Slate", "Nox", "Dusk", "Rune", "Shade", "Falk", "Thorn"],
    "shonen":     ["Blaze", "Forge", "Rex", "Bolt", "Flint", "Axel", "Storm", "Titan", "Jet", "Ryker"],
    "shojo":      ["Rose", "Lila", "Ivy", "Clara", "Elara", "Sylvia", "Dahlia", "Celeste", "Aria", "Luna"],
    "josei":      ["Nara", "Yuki", "Ren", "Mina", "Sora", "Emi", "Kira", "Yuna", "Mei", "Haru"],
    "sports":     ["Ace", "Dash", "Kit", "Rally", "Spike", "Lane", "Pace", "Stride", "Fleet", "Crest"],
    "horror":     ["Crow", "Wraith", "Hollow", "Shade", "Bane", "Haunt", "Dirge", "Vesper", "Gloom", "Mortis"],
    "cultivation": ["Astral", "Zenith", "Void", "Aether", "Nimbus", "Sable", "Orion", "Phoenix", "Nebula", "Cosmos"],
    "isekai":     ["Nova", "Rift", "Drift", "Echo", "Prism", "Glitch", "Warp", "Link", "Flux", "Gate"],
}

_EN_SURNAMES: dict[str, list[str]] = {
    "iyashikei":  ["Tidecalm", "Moongarden", "Stillwater", "Hearthlight", "Dawnmoss", "Softwind", "Dewpath", "Restshore"],
    "seinen":     ["Darkwell", "Fracture", "Voidmask", "Nightscar", "Ironsilence", "Boneash", "Greyfield", "Depthmark"],
    "shonen":     ["Ironarc", "Firesteel", "Thunderforge", "Bladecrest", "Stormhammer", "Ashborn", "Warpath", "Skycleaver"],
    "shojo":      ["Roseveil", "Moonwhisper", "Starbloom", "Heartvine", "Lovelock", "Dreampath", "Crystalwing", "Silkpetal"],
    "josei":      ["Greenvale", "Softridge", "Willowbank", "Clearbrook", "Mossheart", "Tenderglen", "Oakquiet", "Rainfield"],
    "sports":     ["Fastbreak", "Highmark", "Ironrun", "Steelstride", "Surefoot", "Windsprint", "Peakform", "Goldfinish"],
    "horror":     ["Gravesong", "Bloodthorn", "Nightweave", "Darkhollow", "Soulrend", "Doomquiet", "Ashcrypt", "Fearseed"],
    "cultivation": ["Starriver", "Cloudpeak", "Voidgate", "Heavenfall", "Daoroot", "Moonforge", "Spiritwell", "Cosmicvein"],
    "isekai":     ["Worldrift", "Portalweave", "Gatekeeper", "Realmshift", "Codex", "Dimensia", "Pixelforge", "Glitchfield"],
}

_ZH_SURNAMES = ["沈", "林", "陈", "张", "李", "王", "赵", "周", "吴", "黄", "许", "何"]

_ZH_GIVEN_PARTS: dict[str, list[str]] = {
    "iyashikei":  ["静", "安", "和", "柔", "暖", "宁", "雪", "露", "风", "月"],
    "seinen":     ["夜", "暗", "深", "冷", "铁", "灰", "影", "寂", "幽", "墨"],
    "shonen":     ["焰", "雷", "刚", "猛", "锋", "烈", "威", "战", "龙", "虎"],
    "shojo":      ["樱", "瑶", "梦", "蝶", "星", "芷", "兰", "珊", "翠", "云"],
    "josei":      ["雨", "秋", "芳", "慧", "琳", "韵", "清", "婉", "萱", "漫"],
    "sports":     ["胜", "翔", "驰", "飞", "锐", "健", "力", "速", "冲", "毅"],
    "horror":     ["鬼", "幽", "冥", "魅", "骸", "夜", "血", "暗", "诡", "凄"],
    "cultivation": ["星", "河", "道", "仙", "玄", "天", "灵", "虚", "云", "元"],
    "isekai":     ["异", "界", "穿", "维", "幻", "域", "码", "数", "光", "梦"],
}

_ZH_GIVEN_SUFFIXES: dict[str, list[str]] = {
    "iyashikei":  ["兮", "然", "心", "溪", "泉", "棉", "雾", "荷"],
    "seinen":     ["境", "渊", "骨", "镜", "尘", "烬", "雾", "裂"],
    "shonen":     ["拳", "刃", "甲", "弓", "斧", "锤", "盾", "枪"],
    "shojo":      ["瞳", "语", "歌", "舞", "心", "泪", "颜", "音"],
    "josei":      ["兮", "霜", "笛", "琴", "墨", "叶", "瓷", "纱"],
    "sports":     ["峰", "鹰", "豹", "风", "旗", "志", "途", "程"],
    "horror":     ["灵", "魂", "影", "窟", "棺", "烛", "坟", "蛛"],
    "cultivation": ["悠", "渺", "玄", "空", "寂", "冲", "默", "尘"],
    "isekai":     ["元", "脉", "核", "符", "环", "钥", "盘", "阵"],
}

_JA_SURNAMES = ["月影", "星空", "風花", "雪村", "海原", "森川", "水瀬", "白石", "藍沢", "桜庭"]

_JA_GIVEN_NAMES: dict[str, list[str]] = {
    "iyashikei":  ["静", "穏", "和", "優", "凪", "柔", "癒", "泉", "蛍", "楓"],
    "seinen":     ["闇", "灰", "鉄", "影", "黙", "深", "冷", "裂", "塵", "朽"],
    "shonen":     ["炎", "雷", "剛", "猛", "鋼", "烈", "威", "竜", "虎", "獅"],
    "shojo":      ["桜", "瑠璃", "蝶", "星", "薫", "蘭", "雫", "翠", "彩", "詩"],
    "josei":      ["雨", "秋", "芳", "慧", "琳", "韻", "清", "婉", "萱", "漫"],
    "cultivation": ["仙", "道", "天", "霊", "玄", "虚", "雲", "元", "星", "月"],
}

# ---------------------------------------------------------------------------
# EI disclosure templates per locale
# ---------------------------------------------------------------------------

_EI_DISCLOSURE_TEMPLATES: dict[str, str] = {
    "en_US": (
        "{display_name} is an Enlightened Intelligence (EI) author — a character brought "
        "to life by AI to guide you through stories of {topic_phrase}. Full transparency: "
        "every word is crafted by an AI system designed to hold space for your journey. "
        "That's not a limitation — it's a superpower."
    ),
    "zh_TW": (
        "{display_name}是一位由人工智慧（EI, Enlightened Intelligence）創造的角色作者。"
        "每一頁漫畫都由 AI 系統精心編織，旨在陪伴你走過{topic_phrase}的旅程。"
        "這不是缺陷——這是一種全新的創作方式，透明、真誠、為你而生。"
    ),
    "zh_CN": (
        "{display_name}是一位由人工智能（EI，觉悟智能）创造的角色作者。"
        "每一页漫画都由 AI 系统精心打造，旨在用{topic_phrase}的故事帮助你找到内在的平衡。"
        "完全透明——这是一种全新的创作方式。"
    ),
    "zh_HK": (
        "{display_name}係一位由人工智能（EI, Enlightened Intelligence）創造嘅角色作者。"
        "每一頁漫畫都由 AI 系統精心編織，旨在陪你行過{topic_phrase}嘅旅程。"
        "呢個唔係缺陷——係全新嘅創作方式。"
    ),
    "ja_JP": (
        "{display_name}は、AIが生み出した覚醒知性（EI）キャラクター作者です。"
        "すべてのページはAIシステムによって丁寧に紡がれ、{topic_phrase}の物語を通じて"
        "あなたの旅に寄り添います。完全な透明性——これは制限ではなく、新しい可能性です。"
    ),
}

# Topic → human-readable phrase per locale
_TOPIC_PHRASES: dict[str, dict[str, str]] = {
    "en_US": {
        "anxiety": "gentle restoration",
        "burnout": "recovery from exhaustion",
        "grief": "navigating loss",
        "performance_pressure": "growth under pressure",
        "relational_instability": "healing relationships",
        "identity_fracture": "finding yourself",
        "sleep_anxiety": "finding rest",
    },
    "zh_TW": {
        "anxiety": "焦慮療癒",
        "burnout": "倦怠恢復",
        "grief": "失落陪伴",
        "performance_pressure": "壓力下的成長",
        "relational_instability": "關係修復",
        "identity_fracture": "自我尋找",
        "sleep_anxiety": "安眠之旅",
    },
    "zh_CN": {
        "anxiety": "焦虑疗愈",
        "burnout": "倦怠恢复",
        "grief": "失落陪伴",
        "performance_pressure": "压力下的成长",
        "relational_instability": "关系修复",
        "identity_fracture": "自我寻找",
        "sleep_anxiety": "安眠之旅",
    },
    "zh_HK": {
        "anxiety": "焦慮療癒",
        "burnout": "倦怠恢復",
        "grief": "失落陪伴",
        "performance_pressure": "壓力下嘅成長",
        "relational_instability": "關係修復",
        "identity_fracture": "搵返自己",
        "sleep_anxiety": "安眠之旅",
    },
    "ja_JP": {
        "anxiety": "穏やかな回復",
        "burnout": "疲弊からの回復",
        "grief": "喪失の旅路",
        "performance_pressure": "プレッシャー下の成長",
        "relational_instability": "関係の修復",
        "identity_fracture": "自分探し",
        "sleep_anxiety": "安眠への道",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _yaml_safe_load(path: Path) -> Any:
    if yaml is None:
        raise ImportError("PyYAML is required: pip install pyyaml")
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deterministic_index(seed: str, pool_size: int) -> int:
    """Deterministic index from a seed string."""
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % max(pool_size, 1)


def load_brand_registry() -> dict[str, Any]:
    """Load brand_registry.yaml; return the brands dict."""
    data = _yaml_safe_load(BRAND_REGISTRY)
    return data.get("brands", {})


def load_pen_name_display_names() -> set[str]:
    """Return set of all display_name values from pen-name teacher profiles."""
    names: set[str] = set()
    # JSON source (primary)
    if PEN_NAME_PROFILES_JSON.exists():
        with open(PEN_NAME_PROFILES_JSON, encoding="utf-8") as f:
            profiles = json.load(f)
        if isinstance(profiles, list):
            for p in profiles:
                dn = p.get("display_name", "")
                if dn:
                    names.add(dn)
    return names


def load_existing_manga_authors() -> list[dict[str, Any]]:
    """Load all existing manga author YAML profiles."""
    authors: list[dict[str, Any]] = []
    if not MANGA_AUTHORS_DIR.exists():
        return authors
    for p in sorted(MANGA_AUTHORS_DIR.glob("*.yaml")):
        if p.name == "schema.yaml":
            continue
        data = _yaml_safe_load(p)
        if isinstance(data, dict) and "author_id" in data:
            authors.append(data)
    return authors


def validate_no_collision(
    display_name: str,
    brand_id: str,
    pen_name_names: set[str] | None = None,
    existing_authors: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Return list of collision error strings (empty = OK)."""
    errors: list[str] = []
    if pen_name_names is None:
        pen_name_names = load_pen_name_display_names()
    if existing_authors is None:
        existing_authors = load_existing_manga_authors()

    if display_name in pen_name_names:
        errors.append(
            f"COLLISION: display_name '{display_name}' already exists in pen_name_teacher_profiles"
        )

    for a in existing_authors:
        if a.get("display_name") == display_name and a.get("brand_id") == brand_id:
            errors.append(
                f"COLLISION: display_name '{display_name}' already exists for brand '{brand_id}'"
            )
    return errors


# ---------------------------------------------------------------------------
# Name generation
# ---------------------------------------------------------------------------


def generate_display_name(
    *,
    genre: str,
    locale: str,
    brand_id: str,
    topic: str,
    demographic: str,
) -> str:
    """Generate a locale-appropriate character-author name from genre + seed data."""
    seed = f"{brand_id}|{genre}|{locale}|{topic}|{demographic}"
    lang = locale[:2]  # en, zh, ja

    # Normalize genre key
    genre_key = genre.lower().replace("-", "_").replace("ō", "o")

    if lang == "ja":
        surnames = _JA_SURNAMES
        given_pool = _JA_GIVEN_NAMES.get(genre_key, _JA_GIVEN_NAMES.get("iyashikei", []))
        si = _deterministic_index(seed + "|surname", len(surnames))
        gi = _deterministic_index(seed + "|given", len(given_pool))
        return f"{surnames[si]} {given_pool[gi]}" if given_pool else surnames[si]

    if lang == "zh":
        si = _deterministic_index(seed + "|surname", len(_ZH_SURNAMES))
        parts = _ZH_GIVEN_PARTS.get(genre_key, _ZH_GIVEN_PARTS.get("iyashikei", []))
        suffixes = _ZH_GIVEN_SUFFIXES.get(genre_key, _ZH_GIVEN_SUFFIXES.get("iyashikei", []))
        pi = _deterministic_index(seed + "|part", len(parts))
        xi = _deterministic_index(seed + "|suffix", len(suffixes))
        return f"{_ZH_SURNAMES[si]}{parts[pi]}{suffixes[xi]}"

    # Default: English
    given_pool = _EN_GIVEN_NAMES.get(genre_key, _EN_GIVEN_NAMES.get("iyashikei", []))
    surname_pool = _EN_SURNAMES.get(genre_key, _EN_SURNAMES.get("iyashikei", []))
    gi = _deterministic_index(seed + "|given", len(given_pool))
    si = _deterministic_index(seed + "|surname", len(surname_pool))
    return f"{given_pool[gi]} {surname_pool[si]}"


# ---------------------------------------------------------------------------
# Profile generation
# ---------------------------------------------------------------------------


def generate_manga_author_profile(
    *,
    brand_id: str,
    genre: str,
    locale: str,
    topic: str,
    demographic: str,
) -> dict[str, Any]:
    """Generate a complete manga author profile dict."""
    brands = load_brand_registry()
    if brand_id not in brands:
        raise ValueError(f"brand_id '{brand_id}' not found in brand_registry.yaml")

    display_name = generate_display_name(
        genre=genre, locale=locale, brand_id=brand_id, topic=topic, demographic=demographic,
    )

    # Build author_id
    name_slug = display_name.lower().replace(" ", "_")
    # For CJK names, use pinyin-ish slug from brand+genre
    if any("\u4e00" <= ch <= "\u9fff" for ch in display_name):
        digest = hashlib.sha256(display_name.encode("utf-8")).hexdigest()[:6]
        name_slug = f"{genre}_{digest}"
    locale_tag = locale.lower().replace("-", "_")
    idx_seed = f"{brand_id}|{genre}|{locale}|{topic}|{demographic}|idx"
    idx = _deterministic_index(idx_seed, 999) + 1
    author_id = f"{name_slug}_{locale_tag}_{idx:03d}"

    # EI disclosure
    lang_key = locale.replace("-", "_")
    if lang_key not in _EI_DISCLOSURE_TEMPLATES:
        # Fallback: try base language
        lang_key = f"{locale[:2]}_{locale[:2].upper()}" if "_" not in locale else locale
    if lang_key not in _EI_DISCLOSURE_TEMPLATES:
        lang_key = "en_US"
    topic_phrase_map = _TOPIC_PHRASES.get(lang_key, _TOPIC_PHRASES["en_US"])
    topic_phrase = topic_phrase_map.get(topic, topic.replace("_", " "))
    ei_text = _EI_DISCLOSURE_TEMPLATES[lang_key].format(
        display_name=display_name, topic_phrase=topic_phrase,
    )

    # Visual style notes (generic, brand-aware)
    visual_notes = (
        f"Visual style aligned with {brand_id} brand DNA. "
        f"Genre: {genre}. Locale: {locale}. "
        f"See config/brand_dna/ for linework, shading, color, and lettering parameters."
    )

    # Bio blurb (template-based)
    bio = (
        f"{display_name} is an EI manga author creating {genre} stories "
        f"for the {brand_id} brand, exploring {topic.replace('_', ' ')} "
        f"through the lens of {genre} genre conventions."
    )

    profile: dict[str, Any] = {
        "author_id": author_id,
        "display_name": display_name,
        "locale": locale,
        "genre_tie_in": genre,
        "brand_id": brand_id,
        "target_demographic": demographic,
        "therapeutic_topic": topic,
        "ei_disclosure_text": ei_text,
        "visual_style_notes": visual_notes,
        "bio_blurb": bio,
        "status": "active",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return profile


def write_manga_author_profile(profile: dict[str, Any]) -> Path:
    """Write a manga author profile to YAML. Returns the output path."""
    if yaml is None:
        raise ImportError("PyYAML is required: pip install pyyaml")
    MANGA_AUTHORS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{profile['author_id']}.yaml"
    out = MANGA_AUTHORS_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a manga EI character-author profile.",
    )
    parser.add_argument("--brand-id", required=True, help="Brand ID from brand_registry.yaml")
    parser.add_argument("--genre", required=True, help="Genre (iyashikei, seinen, shonen, etc.)")
    parser.add_argument("--locale", required=True, help="Locale (en_US, zh_TW, zh_CN, ja_JP, etc.)")
    parser.add_argument("--topic", required=True, help="Therapeutic topic (anxiety, burnout, etc.)")
    parser.add_argument("--demographic", required=True, help="Target demographic tag")
    parser.add_argument("--dry-run", action="store_true", help="Print profile without writing to disk")
    args = parser.parse_args()

    profile = generate_manga_author_profile(
        brand_id=args.brand_id,
        genre=args.genre,
        locale=args.locale,
        topic=args.topic,
        demographic=args.demographic,
    )

    # Collision check
    pen_names = load_pen_name_display_names()
    existing = load_existing_manga_authors()
    collisions = validate_no_collision(
        profile["display_name"], profile["brand_id"], pen_names, existing,
    )
    if collisions:
        for c in collisions:
            print(f"ERROR: {c}", file=sys.stderr)
        return 1

    if args.dry_run:
        if yaml is not None:
            print(yaml.dump(profile, allow_unicode=True, default_flow_style=False, sort_keys=False))
        else:
            print(json.dumps(profile, indent=2, ensure_ascii=False))
        return 0

    out = write_manga_author_profile(profile)
    print(f"OK wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

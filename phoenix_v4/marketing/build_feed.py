"""
Build marketing_feed.json for GHL consumption.
Authority: config/funnel/freebie_to_book_map.yaml, config/marketing/marketing_feed_schema.yaml
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from phoenix_v4.marketing.book_url_index import (
    load_index,
    resolve_book_url,
    resolve_series_shop_url,
    _pick_brand_entry,
)
from phoenix_v4.marketing.feed_metadata import (
    archetype_for_topic,
    content_type_for_freebie,
    resolve_email_slot,
    resolve_funnel_variant,
    validate_slot_rules,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FUNNEL = REPO_ROOT / "config" / "funnel"
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"

DEFAULT_SHOP_BASE = "https://pearlprime.shop"
DEFAULT_LANDING_BASE = "https://phoenix-brand-admin.pages.dev"
DEFAULT_PERSONA = "corporate_managers"
DEFAULT_TIER = "better"


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _iso_week(d: dt.date | None = None) -> str:
    d = d or dt.date.today()
    return f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"


def _landing_url(base: str, landing_path: str) -> str:
    return urljoin(base.rstrip("/") + "/", landing_path.lstrip("/"))


def _e2_url(base: str, e2_app: str) -> str:
    return f"{base.rstrip('/')}/somatic_exercise_freebee_apps/{e2_app}?unlock=1"


def _normalize_shop_url(store_url: str, shop_base: str) -> str:
    if "pearlprime.shop" in store_url:
        return store_url
    if "/book/" in store_url:
        idx = store_url.find("/book/")
        return shop_base.rstrip("/") + store_url[idx:]
    return store_url


def _resolve_e4_url(
    topic_id: str,
    persona_id: str,
    entry_book: dict[str, Any],
    shop_base: str,
    locale: str,
    brand_id: str,
    url_index: dict[str, Any] | None,
) -> str:
    indexed = resolve_book_url(
        topic_id,
        persona_id,
        locale=locale,
        product_type="book",
        brand_id=brand_id,
        index=url_index,
    )
    if indexed:
        return indexed
    store_url = str(entry_book.get("store_url") or "")
    if store_url:
        return _normalize_shop_url(store_url, shop_base)
    return shop_base.rstrip("/")


def _tier_bonus_types(tier: str = DEFAULT_TIER, *, slot: str | None = None) -> list[str]:
    bundles = _load_yaml(CONFIG_FREEBIES / "tier_bundles.yaml")
    if slot == "bonus_pre_story":
        for source in ("best", tier):
            row = bundles.get(source) or {}
            types = list(row.get("freebie_types") or [])
            if "guided_audio" in types:
                return ["guided_audio"]
            if "assessment_html" in types:
                return ["assessment_html"]
        return ["guided_audio"]

    row = bundles.get(tier) or {}
    types = list(row.get("freebie_types") or [])
    excludes = set(row.get("pre_purchase_excludes") or [])
    out: list[str] = []
    for t in types:
        if t in excludes:
            continue
        if t in ("somatic_html_tool", "assessment_html", "guided_audio"):
            continue
        if t.endswith("_pdf"):
            out.append("checklist_pdf")
    return out


def build_topic_items(
    topic_id: str,
    topic_cfg: dict[str, Any],
    *,
    brand_id: str,
    persona_id: str = DEFAULT_PERSONA,
    landing_base: str = DEFAULT_LANDING_BASE,
    shop_base: str = DEFAULT_SHOP_BASE,
    include_paid: bool = True,
    locale: str = "en_US",
    url_index: dict[str, Any] | None = None,
    funnel_path_prefix: str | None = None,
) -> list[dict[str, Any]]:
    freebie = topic_cfg.get("freebie") or {}
    entry_book = topic_cfg.get("entry_book") or {}
    series = topic_cfg.get("series_upsell") or {}
    arch = archetype_for_topic(topic_id)
    funnel_variant = resolve_funnel_variant(topic_id, persona_id, arch)
    slug = arch.get("funnel_slug") or str(freebie.get("slug") or "")
    freebie_type = str(freebie.get("type") or "interactive_html_tool")
    e1_content = content_type_for_freebie(freebie_type)
    landing_path = str(freebie.get("landing_path") or f"/free/{slug}/")
    if funnel_path_prefix:
        landing_path = f"/free/{funnel_path_prefix}/{slug}/"
    tof_url = _landing_url(landing_base, landing_path)
    e2_app = arch.get("e2_somatic_app") or "ex02_box_breathing.html"
    e2_url = _e2_url(landing_base, e2_app)
    primary_arch = arch.get("primary_archetype_id") or slug.replace("-", "_")

    items: list[dict[str, Any]] = []

    def _item(
        slot: str,
        content_type: str,
        pricing: str,
        cta_url: str,
        title: str,
        archetype_id: str | None = None,
        id_suffix: str | None = None,
    ) -> dict[str, Any]:
        suffix = id_suffix or archetype_id or content_type
        row = {
            "id": f"{brand_id}__{topic_id}__{slot}__{suffix}",
            "topic": topic_id,
            "email_slot": slot,
            "content_type": content_type,
            "pricing": pricing,
            "cta_url": cta_url,
            "title": title,
            "archetype_id": archetype_id or primary_arch,
            "funnel_variant": funnel_variant,
        }
        return row

    items.append(
        _item(
            "e1",
            e1_content,
            "free",
            tof_url,
            str(freebie.get("name") or f"{topic_id} tool"),
        )
    )
    items.append(
        _item(
            "e2",
            "somatic_exercise",
            "free",
            e2_url,
            "Second exercise",
            archetype_id=arch.get("e2_archetype_id") or primary_arch,
        )
    )

    if funnel_variant == "welcome_depth":
        items.append(
            _item(
                "bonus_pre_story",
                "guided_audio",
                "free",
                tof_url,
                f"{topic_id} guided audio",
                archetype_id="guided_audio_nurture",
                id_suffix="guided_audio_nurture",
            )
        )

    items.append(
        _item(
            "e3",
            "story",
            "free",
            tof_url,
            f"{topic_id} story",
            archetype_id="proof_loop_story",
        )
    )

    store_url = str(entry_book.get("store_url") or "")
    if include_paid and (store_url or url_index):
        e4_url = _resolve_e4_url(
            topic_id, persona_id, entry_book, shop_base, locale, brand_id, url_index
        )
        e4_title = str(entry_book.get("title") or f"{topic_id} book")
        if url_index:
            loc = (url_index.get("locales") or {}).get(locale.replace("-", "_"), {})
            persona_row = _pick_brand_entry((loc.get(topic_id) or {}).get(persona_id), brand_id) or {}
            if persona_row.get("title"):
                e4_title = persona_row["title"]
        items.append(
            _item(
                "e4",
                "book_offer",
                "paid",
                e4_url,
                e4_title,
                archetype_id="book_offer",
            )
        )

    series_id = series.get("series_id") or entry_book.get("series_id")
    if series_id:
        series_url = resolve_series_shop_url(
            topic_id,
            persona_id,
            locale=locale,
            shop_base=shop_base,
            brand_id=brand_id,
            index=url_index,
        )
        items.append(
            _item(
                "e5",
                "series_offer",
                "paid",
                series_url or shop_base.rstrip("/"),
                f"{topic_id} series",
                archetype_id="series_upsell",
            )
        )

    drip_idx = 0
    for bonus_type in _tier_bonus_types():
        if bonus_type == "guided_audio":
            continue
        slot = resolve_email_slot(bonus_type, "free")
        if slot not in ("post_e5", "bonus_pre_story"):
            continue
        drip_idx += 1
        items.append(
            _item(
                slot,
                bonus_type if bonus_type != "guided_audio" else "guided_audio",
                "free",
                tof_url,
                f"{topic_id} bonus {drip_idx}",
                archetype_id=bonus_type,
                id_suffix=f"{bonus_type}_{drip_idx}",
            )
        )

    for row in items:
        row["email_slot"] = resolve_email_slot(
            str(row["content_type"]),
            str(row["pricing"]),
            str(row.get("email_slot") or ""),
        )
    return items


def build_marketing_feed(
    *,
    brand_id: str,
    locale: str = "en_US",
    week: str | None = None,
    topics: list[str] | None = None,
    landing_base: str = DEFAULT_LANDING_BASE,
    shop_base: str = DEFAULT_SHOP_BASE,
    persona_id: str = DEFAULT_PERSONA,
    funnel_path_prefix: str | None = None,
) -> dict[str, Any]:
    funnel_map = _load_yaml(CONFIG_FUNNEL / "freebie_to_book_map.yaml")
    map_base = str(funnel_map.get("base_url") or landing_base)
    landing_base = map_base or landing_base
    all_topics = funnel_map.get("topics") or {}
    topic_ids = topics or sorted(all_topics.keys())
    url_index = load_index()

    items: list[dict[str, Any]] = []
    for topic_id in topic_ids:
        cfg = all_topics.get(topic_id)
        if not isinstance(cfg, dict):
            continue
        items.extend(
            build_topic_items(
                topic_id,
                cfg,
                brand_id=brand_id,
                persona_id=persona_id,
                landing_base=landing_base,
                shop_base=shop_base,
                locale=locale,
                url_index=url_index,
                funnel_path_prefix=funnel_path_prefix,
            )
        )

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    return {
        "schema_version": 3,
        "brand_id": brand_id,
        "locale": locale,
        "week": week or _iso_week(),
        "persona_id": persona_id,
        "published_at": now.isoformat().replace("+00:00", "Z"),
        "shop_base_url": shop_base,
        "landing_base_url": landing_base,
        "items": items,
    }


def validate_feed(feed: dict[str, Any]) -> list[str]:
    schema = _load_yaml(REPO_ROOT / "config" / "marketing" / "marketing_feed_schema.yaml")
    errors: list[str] = []

    for key in schema.get("required_top_level") or []:
        if key not in feed:
            errors.append(f"missing top-level field: {key}")

    pricing_enum = set(schema.get("pricing_enum") or [])
    content_enum = set(schema.get("content_type_enum") or [])
    slot_enum = set(schema.get("email_slot_enum") or [])
    required_item = set(schema.get("item_required_for_ghl") or [])

    items = feed.get("items")
    if not isinstance(items, list):
        return errors + ["items must be a list"]

    seen_ids: set[str] = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{i}] must be an object")
            continue
        item_id = str(item.get("id") or "")
        if not item_id:
            errors.append(f"items[{i}] missing id")
        elif item_id in seen_ids:
            errors.append(f"duplicate item id: {item_id}")
        else:
            seen_ids.add(item_id)

        for key in required_item:
            if not item.get(key):
                errors.append(f"items[{i}] ({item_id}) missing required field: {key}")

        pricing = str(item.get("pricing") or "")
        if pricing and pricing not in pricing_enum:
            errors.append(f"items[{i}] invalid pricing: {pricing}")

        content_type = str(item.get("content_type") or "")
        if content_type and content_type not in content_enum:
            errors.append(f"items[{i}] invalid content_type: {content_type}")

        email_slot = str(item.get("email_slot") or "")
        if email_slot and email_slot not in slot_enum:
            errors.append(f"items[{i}] invalid email_slot: {email_slot}")

        errors.extend(validate_slot_rules(item))

    return errors

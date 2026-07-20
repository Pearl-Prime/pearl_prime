#!/usr/bin/env python3
"""Fill a Pearl Prime social media content bank from Storyblocks (EULA-safe).

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 scripts/storyblocks/fill_social_bank.py \\
    --brand-id way_stream_sanctuary --locale en-US \\
    --topics anxiety,burnout,boundaries --media video,image \\
    --max-per-topic 2

  python3 scripts/storyblocks/fill_social_bank.py --dry-run --topics anxiety --media video
  python3 scripts/storyblocks/fill_social_bank.py \\
    --bootstrap-receipt artifacts/storyblocks/social_bank_fill_20260720.json

HD lands only under artifacts/storyblocks_licensed/{work_unit_id}/ (no shared pool).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.storyblocks.api_client import MediaType, StoryblocksAPIClient  # noqa: E402
from scripts.storyblocks.confirm_download import confirm_selection  # noqa: E402
from scripts.storyblocks.consumer_guard import assert_storyblocks_licensed_for_consumer  # noqa: E402
from scripts.storyblocks.exceptions import StoryblocksConfigError, StoryblocksMauCapError  # noqa: E402
from scripts.storyblocks.license_store import LicenseStore, default_license_store  # noqa: E402
from scripts.storyblocks.mau_ledger import MauLedger, default_mau_ledger  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_BRAND = "way_stream_sanctuary"
DEFAULT_LOCALE = "en-US"
DEFAULT_TOPICS = (
    "anxiety,burnout,boundaries,depression,grief,hope,loneliness,"
    "overthinking,self_worth,trauma,healing,anger"
)
BANK_INDEX_NAME = "BANK_INDEX.json"
MANIFEST_TSV_NAME = "MANIFEST.tsv"

TOPIC_QUERIES: dict[str, dict[str, list[str]]] = {
    "anxiety": {
        "video": ["calm ocean waves soft light", "empty chair soft window light"],
        "image": ["soft morning light window interior empty room"],
    },
    "burnout": {
        "video": ["empty desk coffee steam morning light", "slow clouds over quiet horizon"],
        "image": ["abstract soft fabric calm texture", "empty laptop desk natural light"],
    },
    "boundaries": {
        "video": ["gentle forest path morning mist", "closed door soft hallway light"],
        "image": ["quiet desk plant natural light", "doorway threshold soft light"],
    },
    "depression": {
        "video": ["rain on window grey morning quiet room", "empty bed soft grey light"],
        "image": ["rain window empty room soft grey"],
    },
    "grief": {
        "video": ["candle soft light empty chair remembrance", "fallen leaves quiet path"],
        "image": ["candle empty chair soft light"],
    },
    "hope": {
        "video": ["sunrise over calm water soft gold", "window light plants growing"],
        "image": ["sunrise soft gold empty horizon"],
    },
    "loneliness": {
        "video": ["single chair by window soft light", "empty park bench mist morning"],
        "image": ["single chair window soft light"],
    },
    "overthinking": {
        "video": ["notebook pen desk soft lamp night", "clock soft focus quiet room"],
        "image": ["notebook sticky notes soft desk light"],
    },
    "self_worth": {
        "video": ["mirror soft morning light empty room", "hands holding warm mug window"],
        "image": ["soft mirror light empty calm room"],
    },
    "trauma": {
        "video": ["gentle waves shoreline soft fog", "quiet forest light through trees"],
        "image": ["soft fog forest path calm"],
    },
    "healing": {
        "video": ["hands in warm water soft light", "plants growing window sunlight"],
        "image": ["green plant sunlight soft interior"],
    },
    "anger": {
        "video": ["storm clouds clearing soft light", "ocean waves crashing then calm"],
        "image": ["storm clearing sky soft light"],
    },
    "social_anxiety": {
        "video": ["empty hallway soft light quiet", "elevator doors closed soft light"],
        "image": ["empty hallway soft light"],
    },
}


@dataclass
class BankAsset:
    topic: str
    media_type: str
    stock_id: str
    title: str
    query: str
    local_uri: str
    work_unit_id: str
    model_released: bool | None
    property_released: bool | None
    layer: str


@dataclass
class BankFillResult:
    work_unit_id: str
    brand_id: str
    locale: str
    mode: Literal["live", "dry_run"]
    layer: str
    assets: list[BankAsset] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    mau_distinct_count: int = 0
    generated_at: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def keys_present() -> bool:
    return bool(os.environ.get("STORYBLOCKS_PUBLIC_KEY") and os.environ.get("STORYBLOCKS_PRIVATE_KEY"))


def _results_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("results", "items", "videos", "images", "data", "stockItems"):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
    return []


def _stock_id_of(item: dict[str, Any]) -> str:
    for key in ("id", "stock_id", "stockItemId", "stock_item_id", "assetId"):
        if item.get(key) is not None:
            return str(item[key])
    return ""


def _title_of(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("Title") or item.get("description") or "")[:120]


def _release_flags(item: dict[str, Any]) -> tuple[bool | None, bool | None]:
    mr = item.get("model_released")
    if mr is None:
        mr = item.get("is_model_released")
    if mr is None:
        mr = item.get("hasTalentReleased")
    pr = item.get("property_released")
    if pr is None:
        pr = item.get("is_property_released")
    if pr is None:
        pr = item.get("hasPropertyReleased")
    return (bool(mr) if mr is not None else None, bool(pr) if pr is not None else None)


def queries_for(topic: str, media_type: MediaType) -> list[str]:
    block = TOPIC_QUERIES.get(topic) or {}
    qs = list(block.get(media_type) or [])
    if not qs:
        qs = [topic.replace("_", " ") + (" soft light calm" if media_type == "image" else " soft light")]
    return qs


def rank_items(items: list[dict[str, Any]], *, media_type: MediaType) -> list[dict[str, Any]]:
    def score(it: dict[str, Any]) -> tuple[int, int]:
        mr, pr = _release_flags(it)
        release = (2 if mr is True else 0) + (1 if pr is True else 0)
        dur = it.get("duration") or it.get("Duration") or it.get("durationMs")
        try:
            dur_s = float(dur) / (1000.0 if float(dur) > 100 else 1.0)
        except (TypeError, ValueError):
            dur_s = 99.0
        dur_pref = -abs(dur_s - 5.0) if media_type == "video" else 0
        return (release, int(dur_pref * 10))

    return sorted(items, key=score, reverse=True)


def mock_payload(media_type: MediaType, topic: str, n: int) -> dict[str, Any]:
    prefix = "SBV" if media_type == "video" else "SBI"
    results = []
    for i in range(n):
        results.append(
            {
                "id": f"{prefix}-FILL-{topic}-{i+1}",
                "title": f"Mock {topic} {media_type} {i+1}",
                "keywords": [topic, "soft", "light", "calm"],
                "duration": 5 if media_type == "video" else None,
                "model_released": True,
                "property_released": False,
            }
        )
    return {"results": results}


class _MockBody:
    def __init__(self, content: bytes) -> None:
        self.status_code = 200
        self.content = content


def _mock_download_response(media_type: MediaType) -> Any:
    class R:
        status_code = 200
        text = ""

        @staticmethod
        def json() -> dict[str, Any]:
            if media_type == "video":
                return {"MP4": {"_1080p": "https://cdn.example/hd.mp4"}}
            return {"JPG": {"_max": "https://cdn.example/hd.jpg"}}

        def raise_for_status(self) -> None:
            return None

    return R()


def search_once(
    api: StoryblocksAPIClient,
    *,
    query: str,
    media_type: MediaType,
    brand_id: str,
    locale: str,
    work_unit_id: str,
) -> list[dict[str, Any]]:
    if media_type == "video":
        payload = api.search_videos(
            query,
            brand_id=brand_id,
            locale=locale,
            work_unit_id=work_unit_id,
            max_duration=15,
            results_per_page=50,
        )
    else:
        payload = api.search_images(
            query,
            brand_id=brand_id,
            locale=locale,
            work_unit_id=work_unit_id,
            results_per_page=50,
        )
    return _results_list(payload)


def fill_social_bank(
    *,
    topics: list[str],
    media_types: list[MediaType],
    brand_id: str = DEFAULT_BRAND,
    locale: str = DEFAULT_LOCALE,
    work_unit_id: str | None = None,
    max_per_topic: int = 2,
    dry_run: bool | None = None,
    client: StoryblocksAPIClient | None = None,
    mau_ledger: MauLedger | None = None,
    license_store: LicenseStore | None = None,
) -> BankFillResult:
    wu = work_unit_id or f"social_media_bank_storyblocks_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    ledger = mau_ledger or default_mau_ledger
    store = license_store or default_license_store
    force_dry = dry_run if dry_run is not None else (not keys_present())
    mode: Literal["live", "dry_run"] = "dry_run" if force_dry else "live"
    layer = "CODE-WIRED" if force_dry else "EXECUTED-REAL"
    assets: list[BankAsset] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    if force_dry:
        api = client or StoryblocksAPIClient(
            public_key="dry-pub",
            private_key="dry-priv",
            require_keys=True,
            request_fn=lambda *a, **k: _mock_download_response("video"),
        )
        http_get = lambda url, timeout=120: _MockBody(b"\x00MOCK-HD-FILL")  # noqa: E731
    else:
        try:
            api = client or StoryblocksAPIClient(require_keys=True)
        except StoryblocksConfigError as exc:
            raise SystemExit(f"Storyblocks keys missing: {exc}") from exc
        http_get = None

    for topic in topics:
        topic = topic.strip()
        if not topic:
            continue
        for media_type in media_types:
            needed = max_per_topic
            for query in queries_for(topic, media_type):
                if needed <= 0:
                    break
                try:
                    if force_dry:
                        items = _results_list(mock_payload(media_type, topic, max_per_topic + 2))
                    else:
                        items = search_once(
                            api,
                            query=query,
                            media_type=media_type,
                            brand_id=brand_id,
                            locale=locale,
                            work_unit_id=wu,
                        )
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"search {topic}/{media_type}/{query!r}: {exc}")
                    continue

                for item in rank_items(items, media_type=media_type):
                    if needed <= 0:
                        break
                    sid = _stock_id_of(item)
                    if not sid or sid in seen_ids:
                        continue
                    mr, pr = _release_flags(item)
                    try:
                        if force_dry:
                            api._request_fn = lambda *a, mt=media_type, **k: _mock_download_response(mt)  # type: ignore[method-assign]
                        rec = confirm_selection(
                            stock_id=sid,
                            media_type=media_type,
                            brand_id=brand_id,
                            locale=locale,
                            work_unit_id=wu,
                            work_unit_type="social_campaign",
                            surface="social_broll",
                            model_released=mr,
                            property_released=pr,
                            metadata={
                                "topic": topic,
                                "query": query,
                                "title": _title_of(item),
                                "fill_social_bank": True,
                            },
                            client=api,
                            mau_ledger=ledger,
                            license_store=store,
                            http_get=http_get,
                        )
                        assert_storyblocks_licensed_for_consumer(
                            {
                                "source_provider": "storyblocks",
                                "storyblocks_stock_id": sid,
                                "work_unit_id": wu,
                                "local_uri": rec.local_uri,
                            },
                            work_unit_id=wu,
                            license_store=store,
                        )
                    except StoryblocksMauCapError as exc:
                        errors.append(f"MAU cap blocked: {exc}")
                        return BankFillResult(
                            work_unit_id=wu,
                            brand_id=brand_id,
                            locale=locale,
                            mode=mode,
                            layer=layer,
                            assets=assets,
                            errors=errors,
                            mau_distinct_count=ledger.distinct_count(),
                            generated_at=_now_iso(),
                        )
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"confirm {topic}/{media_type}/{sid}: {exc}")
                        continue

                    seen_ids.add(sid)
                    assets.append(
                        BankAsset(
                            topic=topic,
                            media_type=media_type,
                            stock_id=sid,
                            title=_title_of(item),
                            query=query,
                            local_uri=rec.local_uri,
                            work_unit_id=wu,
                            model_released=mr,
                            property_released=pr,
                            layer=layer,
                        )
                    )
                    needed -= 1

            if needed > 0:
                errors.append(f"shortfall topic={topic} media={media_type}: still need {needed}")

    return BankFillResult(
        work_unit_id=wu,
        brand_id=brand_id,
        locale=locale,
        mode=mode,
        layer=layer,
        assets=assets,
        errors=errors,
        mau_distinct_count=ledger.distinct_count(),
        generated_at=_now_iso(),
    )


def write_bank_artifacts(result: BankFillResult, *, out_dir: Path | None = None) -> Path:
    root = out_dir or (REPO / "artifacts" / "storyblocks" / result.work_unit_id)
    root.mkdir(parents=True, exist_ok=True)

    by_topic: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for a in result.assets:
        by_topic.setdefault(a.topic, {}).setdefault(a.media_type, []).append(asdict(a))

    index = {
        "generated_at": result.generated_at,
        "work_unit_id": result.work_unit_id,
        "brand_id": result.brand_id,
        "locale": result.locale,
        "mode": result.mode,
        "layer": result.layer,
        "mau_distinct_count": result.mau_distinct_count,
        "asset_count": len(result.assets),
        "by_topic": by_topic,
        "assets": [asdict(a) for a in result.assets],
        "errors": result.errors,
        "eula": {
            "confirm_selection_sole_hd": True,
            "work_unit_scoped_bank": True,
            "no_shared_hd_pool": True,
            "search_does_not_burn_mau": True,
        },
        "consumer_hint": (
            "Point build_video_snippet_bank at local_uri paths, or use "
            "social_bank_latest.json / BANK_INDEX.json topic lookup."
        ),
    }
    (root / BANK_INDEX_NAME).write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    rows = [
        "topic\tmedia_type\tstock_id\tlocal_uri\twork_unit_id\tmodel_released\tproperty_released\tlayer\tquery\ttitle\n"
    ]
    for a in result.assets:
        rows.append(
            f"{a.topic}\t{a.media_type}\t{a.stock_id}\t{a.local_uri}\t"
            f"{a.work_unit_id}\t{a.model_released}\t{a.property_released}\t"
            f"{a.layer}\t{a.query}\t{a.title.replace(chr(9), ' ')}\n"
        )
    (root / MANIFEST_TSV_NAME).write_text("".join(rows), encoding="utf-8")

    latest = REPO / "artifacts" / "storyblocks" / "social_bank_latest.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(
        json.dumps(
            {
                "work_unit_id": result.work_unit_id,
                "bank_index": str((root / BANK_INDEX_NAME).resolve()),
                "layer": result.layer,
                "mode": result.mode,
                "asset_count": len(result.assets),
                "generated_at": result.generated_at,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def load_bank_index(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid bank index: {path}")
    return data


def plates_for_topic(
    topic: str,
    *,
    media_type: MediaType = "image",
    bank_index: dict[str, Any] | Path | None = None,
) -> list[Path]:
    if bank_index is None:
        latest = REPO / "artifacts" / "storyblocks" / "social_bank_latest.json"
        if not latest.is_file():
            return []
        ptr = json.loads(latest.read_text(encoding="utf-8"))
        bank_index = Path(ptr["bank_index"])
    if isinstance(bank_index, Path):
        bank_index = load_bank_index(bank_index)
    block = (bank_index.get("by_topic") or {}).get(topic) or {}
    entries = block.get(media_type) or []
    if not entries and topic == "social_anxiety":
        entries = ((bank_index.get("by_topic") or {}).get("anxiety") or {}).get(media_type) or []
    out: list[Path] = []
    for e in entries:
        p = Path(str(e.get("local_uri") or ""))
        if p.is_file():
            out.append(p)
    return out


def bootstrap_index_from_receipt(
    receipt_path: Path,
    *,
    brand_id: str = DEFAULT_BRAND,
    locale: str = DEFAULT_LOCALE,
) -> Path | None:
    if not receipt_path.is_file():
        return None
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    wu = str(data.get("work_unit") or data.get("work_unit_id") or "")
    if not wu:
        return None
    assets: list[BankAsset] = []
    for c in data.get("confirmed") or []:
        uri = str(c.get("local_uri") or "")
        if not uri or not Path(uri).is_file():
            continue
        assets.append(
            BankAsset(
                topic=str(c.get("topic") or ""),
                media_type=str(c.get("media") or c.get("media_type") or ""),
                stock_id=str(c.get("stock_id") or ""),
                title=str(c.get("title") or "")[:120],
                query="",
                local_uri=uri,
                work_unit_id=wu,
                model_released=c.get("model_released"),
                property_released=c.get("property_released"),
                layer="EXECUTED-REAL",
            )
        )
    result = BankFillResult(
        work_unit_id=wu,
        brand_id=brand_id,
        locale=locale,
        mode="live",
        layer="EXECUTED-REAL",
        assets=assets,
        errors=list(data.get("errors") or []),
        mau_distinct_count=1,
        generated_at=_now_iso(),
    )
    return write_bank_artifacts(result)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand-id", default=DEFAULT_BRAND)
    ap.add_argument("--locale", default=DEFAULT_LOCALE)
    ap.add_argument("--work-unit-id", default="")
    ap.add_argument("--topics", default=DEFAULT_TOPICS)
    ap.add_argument("--media", default="video,image")
    ap.add_argument("--max-per-topic", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--bootstrap-receipt", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    return ap


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    if args.bootstrap_receipt:
        root = bootstrap_index_from_receipt(
            args.bootstrap_receipt, brand_id=args.brand_id, locale=args.locale
        )
        if not root:
            raise SystemExit(f"bootstrap failed for {args.bootstrap_receipt}")
        print(json.dumps({"layer": "EXECUTED-REAL", "bank_dir": str(root), "mode": "bootstrap"}, indent=2))
        return 0

    topics = [t.strip() for t in args.topics.split(",") if t.strip()]
    media_types: list[MediaType] = [
        m.strip() for m in args.media.split(",") if m.strip() in ("video", "image")
    ]  # type: ignore[assignment]
    if not media_types:
        raise SystemExit("--media must include video and/or image")

    result = fill_social_bank(
        topics=topics,
        media_types=media_types,  # type: ignore[arg-type]
        brand_id=args.brand_id,
        locale=args.locale,
        work_unit_id=args.work_unit_id or None,
        max_per_topic=args.max_per_topic,
        dry_run=True if args.dry_run else None,
    )
    root = write_bank_artifacts(result, out_dir=args.out_dir)
    print(
        json.dumps(
            {
                "layer": result.layer,
                "mode": result.mode,
                "work_unit_id": result.work_unit_id,
                "asset_count": len(result.assets),
                "mau_distinct_count": result.mau_distinct_count,
                "errors": result.errors,
                "bank_dir": str(root),
                "bank_index": str(root / BANK_INDEX_NAME),
            },
            indent=2,
        )
    )
    return 0 if result.assets else 2


if __name__ == "__main__":
    raise SystemExit(main())

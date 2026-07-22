#!/usr/bin/env python3
"""
Social post variation / anti-spam CI gate (SOCIAL-ATOM-BANK-VIBE-01).

Generates a deterministic batch of posts across ≥2 platforms × ≥2 brands for one
well-covered cell and fails when:
  1) two posts for the SAME brand/platform/cell are near-duplicates, or
  2) two DIFFERENT brands produce near-identical captions for the same cell
     (watermark-only swaps are not enough — voice CTA/sign-off must differ), or
  3) the same CTA string repeats in more than half of the posts in a single
     brand×platform×topic slice, or
  4) the same hashtag SET (verbatim, order-independent) repeats in more than
     half of the posts in a single brand×platform×topic slice.

Checks 3/4 close a gap found during the 2026-07-23 pilot: the full-caption
near-duplicate check (1/2) can pass green while the CTA and hashtag block are
byte-identical across nearly every post in a slice — a real anti-spam failure
mode the caption-similarity metric alone does not see, because CTA/hashtags
are a small fraction of total caption tokens and rarely move the 3-gram
Jaccard score past the near-duplicate threshold on their own.

Similarity metric (checks 1/2): 3-gram Jaccard over whitespace-tokenized
captions — same family as scripts/ci/check_prose_duplication.py (ngram
Jaccard), justified there as the repo's catalog/prose dedup rail. Thresholds:
  - SAME brand/platform/cell fail if jaccard >= 0.72
  - CROSS brand fail if jaccard >= 0.90 (allows shared topic vocabulary but
    requires measurable voice/CTA divergence)

Repetition-rate metric (checks 3/4): exact-match count over a brand×platform×
topic slice. Threshold is a strict majority (>50%): two posts out of five (or
any minority) coincidentally sharing one CTA or hashtag set is plausible and
not spam; more than half of a slice sharing one verbatim CTA/hashtag-set is a
structural repetition, not chance, and is the exact shape of the gap the
2026-07-23 pilot surfaced (10/10 posts per brand shared one CTA string). The
slice must have >= MIN_SLICE_SIZE_FOR_REPEAT_CHECK posts before either check
applies, so a 2-post slice sharing a CTA does not false-positive.

Usage:
  python3 scripts/ci/check_social_post_variation.py
  python3 scripts/ci/check_social_post_variation.py --write-pilot DIR
  python3 scripts/ci/check_social_post_variation.py --inject-duplicates 3       # mutation RED (checks 1/2)
  python3 scripts/ci/check_social_post_variation.py --inject-cta-repeat 3       # mutation RED (check 3)
  python3 scripts/ci/check_social_post_variation.py --inject-hashtag-repeat 3   # mutation RED (check 4)

Exit codes:
  0  PASS
  1  FAIL (near-duplicate / cross-brand collision / CTA or hashtag-set over-repeat)
  2  setup / generation error
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.social.deterministic_social import (  # noqa: E402
    generate_copy_package,
    select_atoms_with_cooldown,
)

# Pilot cell — evergreen bank has dense coverage for this persona×topic.
PERSONA = "corporate_managers"
TOPIC = "burnout"
SURFACES = ("linkedin_feed_portrait", "instagram_feed_portrait")
BRANDS = ("stillness_press", "cognitive_clarity")
POSTS_PER_BRAND_SURFACE = 5  # 2×2×5 = 20

SAME_BRAND_FAIL_JACCARD = 0.72
CROSS_BRAND_FAIL_JACCARD = 0.90

# See module docstring "Repetition-rate metric" for the threshold rationale.
CTA_REPEAT_FAIL_RATIO = 0.5
HASHTAG_SET_REPEAT_FAIL_RATIO = 0.5
MIN_SLICE_SIZE_FOR_REPEAT_CHECK = 4


def _body_for_similarity(text: str) -> str:
    """Drop hashtag blocks / inline tags — shared taxonomy is not the spam signal.

    Mirrors prose-dedup practice of comparing body text, not catalog metadata.
    """
    lines = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        # Drop pure hashtag lines and strip trailing inline #tags.
        tokens = stripped.split()
        kept = [t for t in tokens if not t.startswith("#")]
        if kept:
            lines.append(" ".join(kept))
    return "\n".join(lines).strip()


def _tokens(text: str) -> list[str]:
    return [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t]


def ngrams(ws: Sequence[str], n: int = 3) -> set[str]:
    if len(ws) < n:
        return {" ".join(ws)} if ws else set()
    return {" ".join(ws[i : i + n]) for i in range(len(ws) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def caption_similarity(a: str, b: str) -> float:
    return jaccard(ngrams(_tokens(_body_for_similarity(a)), 3), ngrams(_tokens(_body_for_similarity(b)), 3))


def generate_batch(
    *,
    inject_duplicates: int = 0,
    inject_cta_repeat: int = 0,
    inject_hashtag_repeat: int = 0,
    as_of: date | None = None,
) -> list[dict[str, Any]]:
    as_of = as_of or date(2026, 7, 21)
    posts: list[dict[str, Any]] = []
    # Per-brand selection ledger so cooldown is respected across post_index.
    history: dict[str, dict[str, date]] = defaultdict(dict)

    for brand in BRANDS:
        for surface in SURFACES:
            for idx in range(POSTS_PER_BRAND_SURFACE):
                used = history[brand]
                copy = generate_copy_package(
                    PERSONA,
                    TOPIC,
                    surface,
                    brand_id=brand,
                    post_index=idx + 1,  # nonzero → atom/hook rotation path
                    used_history=used,
                    as_of=as_of + timedelta(days=idx),  # advance inside cooldown window
                )
                for atom_id in copy.get("selected_atom_ids") or []:
                    used[atom_id] = as_of + timedelta(days=idx)
                # Also record cooldown picks even when caption falls back to templates.
                for atom in select_atoms_with_cooldown(
                    persona=PERSONA,
                    topic=TOPIC,
                    platform=copy["platform"],
                    brand_id=brand,
                    post_index=idx + 1,
                    used_history=used,
                    as_of=as_of + timedelta(days=idx),
                ):
                    aid = atom.get("atom_id")
                    if aid:
                        used[aid] = as_of + timedelta(days=idx)
                posts.append(
                    {
                        "brand_id": brand,
                        "surface_id": surface,
                        "platform": copy["platform"],
                        "persona": PERSONA,
                        "topic": TOPIC,
                        "post_index": idx + 1,
                        "caption": copy["caption"],
                        "cta": copy.get("cta", {}).get("text"),
                        "hashtags": copy.get("hashtags") or [],
                        "selected_atom_ids": copy.get("selected_atom_ids") or [],
                        "copy_id": copy["copy_id"],
                    }
                )

    if inject_duplicates > 0 and posts:
        donor = posts[0]
        for i in range(inject_duplicates):
            clone = dict(donor)
            clone["copy_id"] = f"injected_dup_{i}"
            clone["post_index"] = 1000 + i
            # Keep same brand/surface/cell so SAME-brand detector must fire.
            posts.append(clone)

    if inject_cta_repeat > 0 and posts:
        # Isolated mutation lever for check 3: force the SAME CTA string across
        # posts in one slice while leaving captions/hashtags distinct, so a PASS
        # here can only be explained by the CTA-repeat check itself (not by the
        # caption near-duplicate check, which this deliberately does not trip).
        donor_slice = [p for p in posts if p["brand_id"] == BRANDS[0] and p["platform"] == posts[0]["platform"]]
        fixed_cta = "Injected fixed CTA for mutation test."
        for i, post in enumerate(donor_slice[:inject_cta_repeat]):
            post["cta"] = fixed_cta

    if inject_hashtag_repeat > 0 and posts:
        # Isolated mutation lever for check 4: force the SAME hashtag SET across
        # posts in one slice while leaving captions/CTA distinct.
        donor_slice = [p for p in posts if p["brand_id"] == BRANDS[0] and p["platform"] == posts[0]["platform"]]
        fixed_tags = ["injectedmutationtag1", "injectedmutationtag2", "injectedmutationtag3"]
        for i, post in enumerate(donor_slice[:inject_hashtag_repeat]):
            post["hashtags"] = list(fixed_tags)

    return posts


def evaluate(posts: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if len(posts) < 20:
        failures.append(f"batch_too_small:{len(posts)}<20")

    # Same brand/platform/cell near-duplicates
    by_cell: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for p in posts:
        by_cell[(p["brand_id"], p["surface_id"])].append(p)

    for (brand, surface), group in by_cell.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sim = caption_similarity(group[i]["caption"], group[j]["caption"])
                if sim >= SAME_BRAND_FAIL_JACCARD:
                    failures.append(
                        f"same_brand_near_dup brand={brand} surface={surface} "
                        f"i={group[i]['post_index']} j={group[j]['post_index']} jaccard={sim:.3f}"
                    )

    # Cross-brand: pair posts with the same surface + post_index
    by_surface_idx: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for p in posts:
        by_surface_idx[(p["surface_id"], int(p["post_index"]))].append(p)
    for (surface, idx), group in by_surface_idx.items():
        brands = {p["brand_id"] for p in group}
        if len(brands) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if group[i]["brand_id"] == group[j]["brand_id"]:
                    continue
                sim = caption_similarity(group[i]["caption"], group[j]["caption"])
                if sim >= CROSS_BRAND_FAIL_JACCARD:
                    failures.append(
                        f"cross_brand_near_identical surface={surface} post_index={idx} "
                        f"{group[i]['brand_id']} vs {group[j]['brand_id']} jaccard={sim:.3f}"
                    )
                # Also require visible CTA/sign-off divergence (not just watermark).
                if group[i].get("cta") and group[j].get("cta") and group[i]["cta"] == group[j]["cta"]:
                    # Shared null/default CTA across brands is a soft signal only when captions also collide.
                    if sim >= 0.5:
                        failures.append(
                            f"cross_brand_same_cta surface={surface} post_index={idx} "
                            f"{group[i]['brand_id']} vs {group[j]['brand_id']}"
                        )

    # CTA-string and hashtag-SET repetition within a brand×platform×topic slice.
    # This is deliberately independent of the caption-similarity checks above:
    # a CTA/hashtag block is a small fraction of total caption tokens, so it can
    # repeat verbatim across every post in a slice without ever pushing the
    # 3-gram Jaccard score up to the near-duplicate threshold. Gap confirmed
    # 2026-07-23 pilot: 10/10 posts per brand shared one CTA string and one
    # hashtag set, and checks 1/2 above passed clean throughout.
    by_slice: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for p in posts:
        by_slice[(p["brand_id"], p["platform"], p["topic"])].append(p)

    for (brand, platform, topic), group in by_slice.items():
        if len(group) < MIN_SLICE_SIZE_FOR_REPEAT_CHECK:
            continue
        cta_counts = Counter(p.get("cta") for p in group if p.get("cta"))
        if cta_counts:
            cta_value, cta_n = cta_counts.most_common(1)[0]
            ratio = cta_n / len(group)
            if ratio > CTA_REPEAT_FAIL_RATIO:
                failures.append(
                    f"cta_repeat_over_threshold brand={brand} platform={platform} topic={topic} "
                    f"cta={cta_value!r} count={cta_n}/{len(group)} ratio={ratio:.2f} "
                    f"(threshold>{CTA_REPEAT_FAIL_RATIO})"
                )
        tag_counts = Counter(tuple(sorted(p.get("hashtags") or [])) for p in group)
        tag_counts.pop((), None)  # empty hashtag sets (e.g. youtube) are not a spam signal
        if tag_counts:
            tagset, tag_n = tag_counts.most_common(1)[0]
            ratio = tag_n / len(group)
            if ratio > HASHTAG_SET_REPEAT_FAIL_RATIO:
                failures.append(
                    f"hashtag_set_repeat_over_threshold brand={brand} platform={platform} topic={topic} "
                    f"hashtags={list(tagset)} count={tag_n}/{len(group)} ratio={ratio:.2f} "
                    f"(threshold>{HASHTAG_SET_REPEAT_FAIL_RATIO})"
                )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Social post variation / anti-spam gate")
    parser.add_argument("--write-pilot", type=Path, default=None, help="Write sample packet JSONL+README here")
    parser.add_argument(
        "--inject-duplicates",
        type=int,
        default=0,
        help="Mutation-test helper: append N cloned posts (must go RED)",
    )
    parser.add_argument(
        "--inject-cta-repeat",
        type=int,
        default=0,
        help="Mutation-test helper: force N posts in one slice to share one CTA string, "
        "captions/hashtags left distinct (isolates check 3, must go RED)",
    )
    parser.add_argument(
        "--inject-hashtag-repeat",
        type=int,
        default=0,
        help="Mutation-test helper: force N posts in one slice to share one hashtag set, "
        "captions/CTA left distinct (isolates check 4, must go RED)",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    try:
        posts = generate_batch(
            inject_duplicates=args.inject_duplicates,
            inject_cta_repeat=args.inject_cta_repeat,
            inject_hashtag_repeat=args.inject_hashtag_repeat,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: generation error: {exc}", file=sys.stderr)
        return 2

    if args.write_pilot:
        out = args.write_pilot
        out.mkdir(parents=True, exist_ok=True)
        packet = out / "posts.jsonl"
        with packet.open("w", encoding="utf-8") as fh:
            for row in posts:
                fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        (out / "README.md").write_text(
            "\n".join(
                [
                    "# Social atom composition pilot (2026-07-21)",
                    "",
                    f"- Cell: persona=`{PERSONA}` topic=`{TOPIC}`",
                    f"- Platforms/surfaces: {', '.join(SURFACES)}",
                    f"- Brands: {', '.join(BRANDS)}",
                    f"- Posts: {len(posts)} (target ≥20)",
                    "",
                    "Regenerate:",
                    "```bash",
                    "python3 scripts/ci/check_social_post_variation.py \\",
                    f"  --write-pilot {out}",
                    "```",
                    "",
                    "Similarity: 3-gram Jaccard (see check_prose_duplication.py).",
                    f"Same-brand fail ≥ {SAME_BRAND_FAIL_JACCARD}; cross-brand fail ≥ {CROSS_BRAND_FAIL_JACCARD}.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    failures = evaluate(posts)
    brands = sorted({p["brand_id"] for p in posts})
    surfaces = sorted({p["surface_id"] for p in posts})
    if args.verbose or failures:
        print(
            f"batch posts={len(posts)} brands={brands} surfaces={surfaces} "
            f"inject_duplicates={args.inject_duplicates}"
        )
    if failures:
        print(f"FAIL: {len(failures)} variation violation(s)", file=sys.stderr)
        for line in failures[:40]:
            print(f"  - {line}", file=sys.stderr)
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more", file=sys.stderr)
        return 1

    print(
        f"PASS: social post variation ok — {len(posts)} posts, "
        f"{len(brands)} brands, {len(surfaces)} surfaces; "
        f"same-brand jaccard<{SAME_BRAND_FAIL_JACCARD}, "
        f"cross-brand jaccard<{CROSS_BRAND_FAIL_JACCARD}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

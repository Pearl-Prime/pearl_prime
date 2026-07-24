#!/usr/bin/env python3
"""Blind calibration harness.

Samples 150-300 items from `analysis/<locale_dir>/calibration_set.jsonl`
(Lane 02 produces this; schema: one row per item with at minimum
`item_id`, `source_path`, `risk_tier`, `persona`, `topic`, `atom_shape` --
see pipeline_config.yaml). Generates candidates from every configured
engine for each sampled item, randomizes/blinds labels (A/B/C/D, not model
names) before handing off for evaluation, and records the label->model
mapping separately so results can be unblinded after judging, not before.

This module does NOT judge anything -- it only generates and blinds
candidates. The actual evaluation (semantic_fidelity, natural_taiwan_mandarin,
etc.) is Claude Code's job (Lane 02 Phase 3), consuming this harness's
blinded output.

Usage:
    python3 scripts/localization/translation_quality/calibration_harness.py \\
        --calibration-set analysis/zh_cn/calibration_set.jsonl \\
        --engines ollama google \\
        --sample-size 150 \\
        --out artifacts/qa/calibration_run_<date>/
"""
from __future__ import annotations

import argparse
import json
import random
import string
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.translation_quality.candidates import CandidateResult  # noqa: E402
from scripts.localization.translation_quality.candidates.ollama_qwen_client import (  # noqa: E402
    translate as ollama_translate,
)
from scripts.localization.translation_quality.candidates.google_translate_client import (  # noqa: E402
    translate as google_translate,
    GoogleTranslateAuthError,
)
from scripts.localization.translation_quality.candidates.dashscope_qwen_client import (  # noqa: E402
    translate as dashscope_translate,
    DashScopeNotYetExemptError,
    DashScopeEndpointError,
)

ENGINE_REGISTRY: dict[str, Callable[..., CandidateResult]] = {
    "ollama": ollama_translate,
    "google": google_translate,
    # "dashscope" now real (Lane 00 exemption landed 2026-07-22, client
    # wired 2026-07-23 -- see candidates/dashscope_qwen_client.py). Still
    # gated at call time by PHOENIX_TRANSLATION_ALLOW_CLOUD, DASHSCOPE_API_KEY,
    # and a hard per-run call cap inside the client itself -- registering it
    # here does not bypass any of those; a caller that hasn't opted in gets
    # a caught, logged error per item (see generate_blinded_candidates)
    # rather than a silent skip or a runaway spend.
    "dashscope": dashscope_translate,
}

RISK_TIERS = ("low", "medium", "high", "critical_recurring")


@dataclass
class CalibrationItem:
    item_id: str
    source_path: str
    risk_tier: str
    persona: str | None = None
    topic: str | None = None
    atom_shape: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def load_calibration_set(path: Path) -> list[CalibrationItem]:
    items: list[CalibrationItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        known = {"item_id", "source_path", "risk_tier", "persona", "topic", "atom_shape"}
        items.append(
            CalibrationItem(
                item_id=row["item_id"],
                source_path=row["source_path"],
                risk_tier=row.get("risk_tier", "medium"),
                persona=row.get("persona"),
                topic=row.get("topic"),
                atom_shape=row.get("atom_shape"),
                extra={k: v for k, v in row.items() if k not in known},
            )
        )
    return items


def stratified_sample(
    items: list[CalibrationItem], sample_size: int, *, seed: int | None = None
) -> list[CalibrationItem]:
    """Stratify by risk_tier so every tier is represented, not uniform-random.

    Allocates sample_size proportionally across tiers present in `items`,
    with a floor of 1 per tier that has any items, then random-samples
    within each tier (seeded for reproducibility when `seed` is given).
    """
    rng = random.Random(seed)
    by_tier: dict[str, list[CalibrationItem]] = {}
    for it in items:
        by_tier.setdefault(it.risk_tier, []).append(it)

    if not by_tier:
        return []

    total = len(items)
    sample_size = min(sample_size, total)
    allocation: dict[str, int] = {}
    remaining = sample_size
    tiers = sorted(by_tier)
    for i, tier in enumerate(tiers):
        tier_items = by_tier[tier]
        if i == len(tiers) - 1:
            allocation[tier] = remaining
        else:
            share = max(1, round(sample_size * (len(tier_items) / total)))
            share = min(share, len(tier_items), remaining)
            allocation[tier] = share
            remaining -= share

    sampled: list[CalibrationItem] = []
    for tier, n in allocation.items():
        pool = by_tier[tier][:]
        rng.shuffle(pool)
        sampled.extend(pool[:n])
    rng.shuffle(sampled)
    return sampled


def _blind_labels(n: int) -> list[str]:
    """A, B, C, ..., Z, AA, AB, ... for however many engines are configured."""
    labels = []
    letters = string.ascii_uppercase
    i = 0
    while len(labels) < n:
        label = ""
        x = i
        while True:
            label = letters[x % 26] + label
            x = x // 26 - 1
            if x < 0:
                break
        labels.append(label)
        i += 1
    return labels


@dataclass
class BlindedCandidateSet:
    item_id: str
    source_path: str
    risk_tier: str
    blinded: dict[str, str]  # label -> candidate text
    unblind_map: dict[str, str]  # label -> engine name (private, written separately)
    errors: dict[str, str] = field(default_factory=dict)  # engine -> error string


def generate_blinded_candidates(
    item: CalibrationItem,
    source_text: str,
    *,
    target_locale: str,
    source_locale: str = "en-US",
    engines: dict[str, Callable[..., CandidateResult]] | None = None,
    seed: int | None = None,
) -> BlindedCandidateSet:
    engines = engines or ENGINE_REGISTRY
    engine_names = sorted(engines)
    rng = random.Random(seed if seed is None else hash((seed, item.item_id)))
    order = engine_names[:]
    rng.shuffle(order)
    labels = _blind_labels(len(order))

    blinded: dict[str, str] = {}
    unblind_map: dict[str, str] = {}
    errors: dict[str, str] = {}

    for label, engine_name in zip(labels, order):
        fn = engines[engine_name]
        try:
            result = fn(source_text, source_locale=source_locale, target_locale=target_locale)
            blinded[label] = result.text
            unblind_map[label] = result.candidate_id
        except GoogleTranslateAuthError as exc:
            errors[engine_name] = str(exc)
        except Exception as exc:  # noqa: BLE001 -- record and continue, don't abort the whole batch
            errors[engine_name] = f"{type(exc).__name__}: {exc}"

    return BlindedCandidateSet(
        item_id=item.item_id,
        source_path=item.source_path,
        risk_tier=item.risk_tier,
        blinded=blinded,
        unblind_map=unblind_map,
        errors=errors,
    )


def run_harness(
    calibration_set_path: Path,
    out_dir: Path,
    *,
    sample_size: int = 150,
    target_locale: str = "zh-CN",
    source_locale: str = "en-US",
    engine_names: list[str] | None = None,
    seed: int | None = None,
) -> Path:
    items = load_calibration_set(calibration_set_path)
    sampled = stratified_sample(items, sample_size, seed=seed)

    engines = {name: ENGINE_REGISTRY[name] for name in (engine_names or ENGINE_REGISTRY)}

    out_dir.mkdir(parents=True, exist_ok=True)
    blinded_path = out_dir / "blinded_candidates.jsonl"
    unblind_path = out_dir / "unblind_map.jsonl"  # keep separate; do not ship to the evaluator

    with blinded_path.open("w", encoding="utf-8") as bf, unblind_path.open("w", encoding="utf-8") as uf:
        for item in sampled:
            src_path = REPO_ROOT / item.source_path
            if not src_path.is_file():
                bf.write(json.dumps({"item_id": item.item_id, "error": "source_path_not_found"}) + "\n")
                continue
            source_text = src_path.read_text(encoding="utf-8")
            cset = generate_blinded_candidates(
                item,
                source_text,
                target_locale=target_locale,
                source_locale=source_locale,
                engines=engines,
                seed=seed,
            )
            bf.write(
                json.dumps(
                    {
                        "item_id": cset.item_id,
                        "source_path": cset.source_path,
                        "risk_tier": cset.risk_tier,
                        "candidates": cset.blinded,
                        "errors": cset.errors,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            uf.write(json.dumps({"item_id": cset.item_id, "unblind_map": cset.unblind_map}) + "\n")

    print(f"Sampled {len(sampled)}/{len(items)} items; wrote {blinded_path} + {unblind_path}")
    return blinded_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calibration-set", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sample-size", type=int, default=150)
    ap.add_argument("--target-locale", default="zh-CN")
    ap.add_argument("--source-locale", default="en-US")
    ap.add_argument("--engines", nargs="+", default=None, choices=sorted(ENGINE_REGISTRY))
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args(argv)

    run_harness(
        args.calibration_set,
        args.out,
        sample_size=args.sample_size,
        target_locale=args.target_locale,
        source_locale=args.source_locale,
        engine_names=args.engines,
        seed=args.seed,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

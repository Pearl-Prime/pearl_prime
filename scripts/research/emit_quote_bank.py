#!/usr/bin/env python3
"""Emit quote bank YAML files from curated verified corpus (Wave 1 or Wave 2)."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BANK = REPO / "SOURCE_OF_TRUTH" / "accent_banks" / "quotes"
CLAIMS = REPO / "pearl_research" / "claims"
LEDGER = REPO / "artifacts" / "research" / "quote_verification_ledger.jsonl"
REJECTED = REPO / "artifacts" / "research" / "quote_rejected_log.jsonl"
SENSITIVITY = REPO / "artifacts" / "research" / "quote_sensitivity_exclusion_log.jsonl"

CLUSTERS = [
    "universal", "en_US", "zh_CN", "zh_TW", "ja_JP",
    "de_DE", "fr_FR", "it_IT", "es_ES", "hu_HU", "pt_BR",
]

WAVE_CONFIG = {
    1: {
        "topics": [
            "anxiety", "burnout", "overthinking", "imposter_syndrome",
            "financial_anxiety", "adhd_focus",
        ],
        "targets": {
            "anxiety": {"cluster": 12, "universal": 20},
            "burnout": {"cluster": 10, "universal": 20},
            "overthinking": {"cluster": 10, "universal": 20},
            "imposter_syndrome": {"cluster": 10, "universal": 20},
            "financial_anxiety": {"cluster": 10, "universal": 20},
            "adhd_focus": {"cluster": 10, "universal": 20},
        },
        "corpus_module": "scripts.research.quote_bank_wave1.corpus",
        "closeout": REPO / "artifacts/research/quote_bank_wave1_closeout.md",
    },
    2: {
        "topics": [
            "boundaries", "compassion_fatigue", "courage", "depression",
            "financial_stress", "grief", "mindfulness", "self_worth",
            "sleep_anxiety", "social_anxiety", "somatic_healing",
        ],
        "targets": {t: {"cluster": 12, "universal": 20} for t in [
            "boundaries", "compassion_fatigue", "courage", "depression",
            "financial_stress", "grief", "mindfulness", "self_worth",
            "sleep_anxiety", "social_anxiety", "somatic_healing",
        ]},
        "corpus_module": "scripts.research.quote_bank_wave2.corpus",
        "closeout": REPO / "artifacts/research/quote_bank_wave2_closeout.md",
    },
}


def load_corpus(module_path: str) -> tuple[list[dict], list[dict], list[dict]]:
    import importlib
    mod = importlib.import_module(module_path)
    return mod.QUOTES, mod.REJECTED, mod.SENSITIVITY_EXCLUSIONS


def quote_matches_cluster(q: dict, cluster: str) -> bool:
    fit = q.get("locale_fit", [])
    if cluster == "universal":
        return "universal" in fit
    if cluster == "en_US":
        return cluster in fit
    if cluster in ("de_DE", "fr_FR", "it_IT", "es_ES", "hu_HU", "pt_BR"):
        return cluster in fit or "universal" in fit
    return cluster in fit


def emit_cluster_file(topic: str, cluster: str, quotes: list[dict], wave: int, targets: dict) -> int:
    filtered = [q for q in quotes if topic in q["topic_keys"] and quote_matches_cluster(q, cluster)]
    target = targets[topic]["universal"] if cluster == "universal" else targets[topic]["cluster"]
    if len(filtered) < target:
        print(f"WARN {topic}/{cluster}: need {target}, got {len(filtered)}")
    filtered = filtered[:target]
    out = {
        "status": "unwired",
        "topic": topic,
        "locale_cluster": cluster,
        "wave": wave,
        "quote_count": len(filtered),
        "quotes": [{k: v for k, v in q.items() if k != "locale_fit" or cluster == "universal"} for q in filtered],
    }
    for q in out["quotes"]:
        if cluster != "universal":
            q.pop("locale_fit", None)
    path = BANK / topic / f"{cluster}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Quote bank — {topic} / {cluster} — Wave {wave}\n"
        f"# status: unwired | KNOWN_UNWIRED: accent_banks/quotes/\n"
    )
    path.write_text(header + yaml.dump(out, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return len(filtered)


def write_claim(q: dict) -> None:
    CLAIMS.mkdir(parents=True, exist_ok=True)
    path = CLAIMS / f"{q['quote_id']}.json"
    if path.exists():
        return
    claim = {
        "claim_id": q["quote_id"],
        "claim_type": "quote_attribution",
        "statement": q["text_en"],
        "author": q["author"],
        "primary_source": q["primary_source"],
        "verified_via": q["verified_via"],
        "public_domain": q["public_domain"],
        "verified_date": str(date.today()),
        "status": "verified",
    }
    path.write_text(json.dumps(claim, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, new_lines: list[dict], key: str) -> None:
    existing_ids: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_ids.add(json.loads(line)[key])
    with path.open("a", encoding="utf-8") as f:
        for obj in new_lines:
            if obj[key] not in existing_ids:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
                existing_ids.add(obj[key])


def run_wave(wave: int, topics_filter: list[str] | None = None) -> None:
    cfg = WAVE_CONFIG[wave]
    topics = topics_filter or cfg["topics"]
    targets = cfg["targets"]
    quotes, rejected, sensitivity = load_corpus(cfg["corpus_module"])
    wave_quotes = [q for q in quotes if any(t in q["topic_keys"] for t in topics)]

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger_lines = [
        {
            "quote_id": q["quote_id"], "author": q["author"],
            "primary_source": q["primary_source"], "verified_via": q["verified_via"],
            "topic_keys": q["topic_keys"], "locale_fit": q["locale_fit"],
            "status": "accepted", "wave": wave,
        }
        for q in wave_quotes
    ]
    for q in wave_quotes:
        write_claim(q)
    if wave == 1:
        LEDGER.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ledger_lines) + "\n")
        REJECTED.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rejected) + "\n")
        SENSITIVITY.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in sensitivity) + "\n")
    else:
        append_jsonl(LEDGER, ledger_lines, "quote_id")
        append_jsonl(REJECTED, [{**r, "wave": wave} for r in rejected], "rejected_id")
        append_jsonl(SENSITIVITY, [{**s, "wave": wave} for s in sensitivity], "exclusion_id")

    counts: dict[str, dict[str, int]] = {t: {} for t in topics}
    total = 0
    for topic in topics:
        for cluster in CLUSTERS:
            n = emit_cluster_file(topic, cluster, quotes, wave, targets)
            counts[topic][cluster] = n
            total += n

    closeout = cfg["closeout"]
    lines = [
        f"# Quote Bank Wave {wave} — Closeout",
        f"**Date:** {date.today()}",
        f"**Total quotes emitted:** {total}",
        f"**Accepted (corpus):** {len(wave_quotes)}",
        f"**Rejected (wave corpus):** {len(rejected)}",
        f"**Sensitivity exclusions:** {len(sensitivity)}",
        "",
        "## Counts per topic × cluster",
        "",
        "| topic | " + " | ".join(CLUSTERS) + " |",
        "|-------|" + "|".join(["---"] * len(CLUSTERS)) + "|",
    ]
    for topic in topics:
        row = [topic] + [str(counts[topic].get(c, 0)) for c in CLUSTERS]
        lines.append("| " + " | ".join(row) + " |")
    rate = len(wave_quotes) / (len(wave_quotes) + len(rejected)) * 100 if wave_quotes else 0
    lines += [
        "", "## Verification rate",
        f"- Collected: {len(wave_quotes)}", f"- Rejected: {len(rejected)}",
        f"- Rate: {rate:.1f}% accepted",
        "", "## Artifacts",
        f"- Bank: `SOURCE_OF_TRUTH/accent_banks/quotes/`",
        f"- Ledger: `artifacts/research/quote_verification_ledger.jsonl`",
    ]
    closeout.write_text("\n".join(lines) + "\n")
    print(f"Wave {wave}: emitted {total} quotes for {len(topics)} topics")
    print(f"Closeout: {closeout}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--wave", type=int, required=True, choices=[1, 2])
    p.add_argument("--topics", nargs="*", help="Subset of topics (wave 2 batching)")
    args = p.parse_args()
    run_wave(args.wave, args.topics or None)


if __name__ == "__main__":
    main()

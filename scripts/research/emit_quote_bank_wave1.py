#!/usr/bin/env python3
"""Emit Wave 1 quote bank YAML files from curated verified corpus."""
from __future__ import annotations

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
CLOSEOUT = REPO / "artifacts" / "research" / "quote_bank_wave1_closeout.md"

TOPICS = [
    "anxiety",
    "burnout",
    "overthinking",
    "imposter_syndrome",
    "financial_anxiety",
    "adhd_focus",
]
CLUSTERS = [
    "universal",
    "en_US",
    "zh_CN",
    "zh_TW",
    "ja_JP",
    "de_DE",
    "fr_FR",
    "it_IT",
    "es_ES",
    "hu_HU",
    "pt_BR",
]
TARGETS = {
    "anxiety": {"cluster": 12, "universal": 20},
    "burnout": {"cluster": 10, "universal": 20},
    "overthinking": {"cluster": 10, "universal": 20},
    "imposter_syndrome": {"cluster": 10, "universal": 20},
    "financial_anxiety": {"cluster": 10, "universal": 20},
    "adhd_focus": {"cluster": 10, "universal": 20},
}


def load_corpus() -> tuple[list[dict], list[dict], list[dict]]:
    from scripts.research.quote_bank_wave1 import corpus as c

    return c.QUOTES, c.REJECTED, c.SENSITIVITY_EXCLUSIONS


def quote_matches_cluster(q: dict, cluster: str) -> bool:
    fit = q.get("locale_fit", [])
    if cluster == "universal":
        return "universal" in fit
    if cluster == "en_US":
        # Abe Lincoln rule: Western canon tagged en_* only — no universal bleed
        return cluster in fit
    if cluster in ("de_DE", "fr_FR", "it_IT", "es_ES", "hu_HU", "pt_BR"):
        # European clusters: native canon + universal workhorses
        return cluster in fit or "universal" in fit
    # zh_CN, zh_TW, ja_JP — strict locale canon
    return cluster in fit


def emit_cluster_file(topic: str, cluster: str, quotes: list[dict]) -> int:
    filtered = [q for q in quotes if topic in q["topic_keys"] and quote_matches_cluster(q, cluster)]
    target = TARGETS[topic]["universal"] if cluster == "universal" else TARGETS[topic]["cluster"]
    if len(filtered) < target:
        print(f"WARN {topic}/{cluster}: need {target}, got {len(filtered)}")
    filtered = filtered[:target]
    out = {
        "status": "unwired",
        "topic": topic,
        "locale_cluster": cluster,
        "wave": 1,
        "quote_count": len(filtered),
        "quotes": [{k: v for k, v in q.items() if k != "locale_fit" or cluster == "universal"} for q in filtered],
    }
    for q in out["quotes"]:
        if cluster != "universal":
            q.pop("locale_fit", None)
    path = BANK / topic / f"{cluster}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Quote bank — {topic} / {cluster} — Wave 1\n"
        f"# status: unwired | KNOWN_UNWIRED: accent_banks/quotes/\n"
    )
    path.write_text(header + yaml.dump(out, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return len(filtered)


def write_claim(q: dict) -> None:
    CLAIMS.mkdir(parents=True, exist_ok=True)
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
    (CLAIMS / f"{q['quote_id']}.json").write_text(json.dumps(claim, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    quotes, rejected, sensitivity = load_corpus()
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, dict[str, int]] = {t: {} for t in TOPICS}
    ledger_lines = []
    for q in quotes:
        write_claim(q)
        ledger_lines.append(
            {
                "quote_id": q["quote_id"],
                "author": q["author"],
                "primary_source": q["primary_source"],
                "verified_via": q["verified_via"],
                "topic_keys": q["topic_keys"],
                "locale_fit": q["locale_fit"],
                "status": "accepted",
            }
        )
    LEDGER.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ledger_lines) + "\n")
    REJECTED.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rejected) + "\n")
    SENSITIVITY.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in sensitivity) + "\n")
    total = 0
    for topic in TOPICS:
        for cluster in CLUSTERS:
            n = emit_cluster_file(topic, cluster, quotes)
            counts[topic][cluster] = n
            total += n
    lines = [
        "# Quote Bank Wave 1 — Closeout",
        f"**Date:** {date.today()}",
        f"**Total quotes emitted:** {total}",
        f"**Accepted (ledger):** {len(quotes)}",
        f"**Rejected:** {len(rejected)}",
        f"**Sensitivity exclusions:** {len(sensitivity)}",
        "",
        "## Counts per topic × cluster",
        "",
        "| topic | " + " | ".join(CLUSTERS) + " |",
        "|-------|" + "|".join(["---"] * len(CLUSTERS)) + "|",
    ]
    for topic in TOPICS:
        row = [topic] + [str(counts[topic].get(c, 0)) for c in CLUSTERS]
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## Verification rate",
        f"- Collected: {len(quotes)}",
        f"- Rejected: {len(rejected)}",
        f"- Rate: {len(quotes) / (len(quotes) + len(rejected)) * 100:.1f}% accepted",
        "",
        "## Artifacts",
        f"- Bank: `SOURCE_OF_TRUTH/accent_banks/quotes/`",
        f"- Ledger: `artifacts/research/quote_verification_ledger.jsonl`",
        f"- Claims: `pearl_research/claims/` ({len(quotes)} files)",
    ]
    CLOSEOUT.write_text("\n".join(lines) + "\n")
    print(f"Emitted {total} quotes across {len(TOPICS)} topics × {len(CLUSTERS)} clusters")
    print(f"Closeout: {CLOSEOUT}")


if __name__ == "__main__":
    main()

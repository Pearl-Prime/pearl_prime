# RCG-020 — Payout tier sourcing (LOW)

**Audit ref:** `RESEARCH_AUDIT_2026_03_30.md` section A item 20
**Source file:** `config/payouts/`
**Claim:** Pricing/payout tiers — unable to verify if sourced (may be contractual/internal)
**Research query:** KDP royalty tiers 2025 OR internal contract label

---

## Claim analysis

The payout configuration files define pricing and royalty tiers for audiobook distribution. The audit flags that it is unclear whether these tiers are derived from market research (competitor benchmarks), platform policies (e.g., KDP/ACX royalty rates), or internal contractual decisions. No source attribution exists.

## Research findings

### Amazon KDP / ACX royalty structures (public)

1. **Amazon KDP (Kindle Direct Publishing) — eBook royalties.** Two tiers:
   - 35% royalty: Available for books priced $0.99-$200.00
   - 70% royalty: Available for books priced $2.99-$9.99 (with delivery cost deduction)
   - Source: https://kdp.amazon.com/en_US/help/topic/G200634500 (KDP Pricing Page)

2. **ACX (Audiobook Creation Exchange) — audiobook royalties.** As of 2024-2025:
   - Exclusive distribution (Audible only): 40% royalty
   - Non-exclusive distribution: 25% royalty
   - Royalty share with narrator: 20% each (exclusive)
   - Source: https://www.acx.com/help/royalties/200484920 (ACX Royalties)

3. **Findaway Voices / Authors Republic (wide distribution).** Royalty rates vary by retailer:
   - Typically 50-80% of net receipts depending on the retailer and distribution agreement
   - Apple Books: typically ~52% net to author through wide distributors
   - Google Play: varies

4. **International KDP royalties** differ:
   - 70% royalty available in select markets (US, UK, DE, FR, ES, IT, NL, JP, BR, MX, CA, IN, AU)
   - 35% royalty applies in all other markets
   - Source: KDP pricing support pages

### Assessment

Payout tiers in a content business typically reflect a combination of:
- **Platform-imposed rates** (KDP/ACX royalty schedules — publicly documented)
- **Internal business decisions** (profit margin targets, author compensation models)
- **Contractual terms** (specific to the business entity)

The configuration files likely contain a mix of externally verifiable platform rates and internal business decisions.

## Verdict

**PARTIALLY_CONFIRMED** — Platform royalty rates (KDP, ACX) are publicly documented and verifiable. Internal pricing decisions and margin structures are proprietary and cannot be externally verified. The appropriate action is to label each tier's provenance.

## Recommendation

For each tier in `config/payouts/`:
```yaml
# If based on platform policy:
_source:
  url: "https://kdp.amazon.com/en_US/help/topic/G200634500"
  note: "KDP 70% royalty tier, verified 2026-04-01"

# If internal business decision:
_source:
  note: "Internal pricing decision — not externally sourced. Owner: [business role]. Last reviewed: [date]."
  label: "internal_contract"
```

## Citations

```yaml
_source:
  url: "https://kdp.amazon.com/en_US/help/topic/G200634500; https://www.acx.com/help/royalties/200484920"
  note: "Platform rates (KDP/ACX) are public. Internal tiers should be labeled 'internal_contract' per audit recommendation."
  date: "2026-04-01"
```

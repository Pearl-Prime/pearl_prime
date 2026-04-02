# RCG-022 — Payout / pricing tiers (`config/payouts/`)

**Audit:** `artifacts/research/RESEARCH_AUDIT_2026_03_30.md` §A item 20 (LOW).  
**Dev spec mapping:** `docs/RESEARCH_CITATION_GAP_DEV_SPEC.md` Batch 3 **RCG-020** (same claim).  
**Tooling:** Claude-in-Chrome MCP was **not** available; **web fetch** of Audible newsroom + repo file review.

## Claim in repo

Pricing/payout assumptions in `config/payouts/` may be **market-based**, **contractual**, or **internal** — audit could not tell from structure alone.

## What is in tree (verified)

1. **`kdp_store_royalty_reference.yaml`** — Explicitly a **research extract**, not Phoenix contractual terms; rows carry `_source` pointers to `artifacts/research/kdp_global_ebook_strategy_2026_03_23.md` and warn to verify live KDP rules [internal YAML].  
2. **`churches.yaml` / `payees.yaml`** — Church payout registry **stubs**; authority points to `specs/PHOENIX_CHURCHES_PAYOUT_SPEC.md` [internal YAML].  
3. **`cn_digital_tax_withholding_reference.yaml`** — (not fully re-read in this pass; treat as reference extract unless marked contractual in file header.)

## External benchmark — Audible / ACX royalty model (official)

Audible’s newsroom describes a **new royalty model** (rolling out from 2025): member plan value (Plus / Premium Plus plus credits used) is **allocated across titles listened to in the month**, then multiplied by the **contractual royalty rate** to determine payment [1]. This is a **platform** benchmark for **how** royalties are computed under that program, not Phoenix’s private deals.

Independent summaries of **historical** ACX exclusive vs non-exclusive **percentage** splits (e.g. 40% / 25% era) appear on third-party blogs [2] — use only as secondary; **contractual** rates for any given project remain **agreement-specific**.

## Conclusion

- **KDP table in repo:** Already **sourced** to an internal research markdown extract; **not** a substitute for live Amazon legal terms — operators should use https://kdp.amazon.com/ help [3] for current rules.  
- **Church / payee payout amounts:** **Internal / contractual** surface in spec + YAML; **no** public “tier” table was required to close this LOW item.  
- **Recommendation:** Keep `_source:` on market-reference YAML; label any future **Phoenix-specific** tier numbers as `internal_contract` or `operator_config` per `RESEARCH_CITATION_GAP_DEV_SPEC.md` §6.

## Sources

[1] https://www.audible.com/about/newsroom/audibles-new-royalty-model-more-opportunities-for-authors-and-publishers — Audible newsroom, new royalty model and calculation description (fetched 2026-03-31).  
[2] https://www.acx.com/mp/blog/money-talks-paying-and-getting-paid-for-your-audiobook — ACX blog, paying/getting paid (official ACX domain; verify current numbers against latest posts).  
[3] https://kdp.amazon.com/ — Amazon KDP (canonical live policy for Kindle/ebook royalties; not a single static article).

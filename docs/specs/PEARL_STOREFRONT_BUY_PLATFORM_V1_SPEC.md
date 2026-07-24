# Pearl Storefront Buy Platform — V1 Spec

**Status:** SPECCED (gt30d C03 · 2026-07-22)  
**Keepers:** I034  
**Owner:** Pearl_Architect (Claude)  
**Acceptance layer:** SPECCED — no live checkout required for this landing

## 0. Purpose

Specify a book + audiobook buying surface for Pearl brands without requiring live
payment credentials in agent sessions.

## 1. Scope

| In | Out |
|---|---|
| Product model (book EPUB, audiobook SKU) | Live Stripe/Snipcart key entry by agents |
| Cart → checkout handoff contract | Full marketplace multi-seller |
| Locale/currency placeholders | Tax engine v1 |
| Operator-gated secrets checklist | Public launch authorization |

## 2. Operator-gated dependencies

- Snipcart and/or Stripe keys (operator only).
- Domain + HTTPS storefront host.
- Legal/refund copy approval.

Agents must stop at `OPERATOR_GATE` when keys are missing — do not invent fake keys.

## 3. Product record (minimum)

```yaml
sku_id: string
format: epub|audiobook
brand_id: string
locale: string
title: string
price_cents: int
currency: ISO4217
fulfillment: download_link|stream_entitlement
```

## 4. Cursor-may-implement (Wave-B unless PM advances)

1. [ ] Schema + fixture under `config/` or `docs/specs` examples.
2. [ ] Dry-run checkout page stub with `PAYMENT_KEYS=missing` banner.
3. [ ] No production publish without `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`.

## 5. Signal

`gt30d-c03-spec-terminal` when this file lands.

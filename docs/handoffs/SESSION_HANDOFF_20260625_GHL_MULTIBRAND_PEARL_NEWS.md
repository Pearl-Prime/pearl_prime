# Session Handoff — GHL Multi-Brand + Pearl News Ops (2026-06-25)

**Audience:** Operator / next agent  
**Repo:** `Ahjan108/phoenix_omega_v4.8`  
**Branch at handoff:** `main` @ `aecc7b0719`  
**Session span:** 2026-06-22 → 2026-06-25

---

## Executive summary

| Workstream | Status | Blocker |
|------------|--------|---------|
| **A — Stillness Press GHL feed CDN** | **Done** — feed live on R2 | GHL admin webhook |
| **B — Multi-brand GHL (3 pilots)** | **Scaffolded** | R2 publish + admin packages for Devotion/Waystream |
| **C — Waystream EPUB production** | **Partial** — 786 delivery JSON, 800 catalog | Local EPUB artifacts missing |
| **D — Pearl News daily publish** | **Restored on pearl-star** (#1909, #1911) | Re-enable workflow + verify dry-run |

**Brands:** Stillness Press ≠ Waystream Sanctuary ≠ Devotion Path (Sai Maa).

---

## 1. GHL — Stillness Press feed ✅

**Live feed URL** (HTTP 200, schema v3, 109 items):

```text
https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/stillness_press/en_US/2026-W26/marketing_feed.json
```

**PRs:** #1893 (wrangler --remote), #1894 (boto3 R2), #1895 (Python fix)

**Handoff:** `docs/handoffs/GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md`  
**Email:** `docs/handoffs/GHL_ADMIN_FORWARD_EMAIL_20260623.txt`

**Webhook blocked:** `PHOENIX_GHL_FUNNEL_WEBHOOK` unset → run `setup_ghl_webhook.sh` when admin replies.

---

## 2. Multi-brand GHL (3 pilots)

| Brand | Display | Teacher | Catalog | Funnel prefix |
|-------|---------|---------|---------|---------------|
| `stillness_press` | Stillness Press | ahjan | 61 | `/free/{slug}/` |
| `devotion_path` | Open Vessel Press | sai_ma | 22 | `/free/devotion_path/{slug}/` |
| `way_stream_sanctuary` | Waystream Sanctuary | none | 800 | `/free/way_stream_sanctuary/{slug}/` |

**Registry:** `config/marketing/brand_marketing_registry.yaml`  
**Scripts:** `build_all_marketing_feeds.py`, `sync_brand_funnel_pages.py`  
**Handoffs:** `GHL_TOTAL_INTEGRATION_HANDOFF_DEVOTION_PATH_20260624.md`, `..._WAYSTREAM_20260624.md`

**15 freebies:** anxiety reset, burnout audit, self-worth inventory, imposter log, boundaries scripts, depression kit, courage map, thought sorter, compassion audit, social toolkit, financial check-in, financial stress audit, sleep wind-down, body scan, grief letter.

---

## 3. Waystream EPUBs

- **800** catalog plans; **786** in delivery feed (48 weeks)
- Covers: PR #1891 merged
- **Missing:** `artifacts/weekly_packages/way_stream_sanctuary/`
- **Rebuild:** `build_waystream_epub_only.py` → R2 upload → `gen_brand_deliveries.py`

---

## 4. Pearl News

**Merged this session:**

| PR | Change |
|----|--------|
| #1909 | Restore daily publish on pearl-star self-hosted runner |
| #1911 | Loopback Ollama URL (`127.0.0.1:11434`) + Python preflight |

**Workflow:** `.github/workflows/pearl-news-daily.yml` — was `disabled_manually` after May 28 failures (bad LLM secrets).

**Do not break:** sidebar parity gate, `CANONICAL_SIDEBAR.html`, `assemble_v52.py`

**Next:** re-enable scheduled workflow after successful `workflow_dispatch` dry-run on pearl-star runner.

---

## 5. Operator next steps

1. **P0** — Email GHL admin (Stillness); wire webhook on reply  
2. **P1** — Publish Devotion + Waystream feeds; deploy 30 funnel pages  
3. **P2** — Rebuild Waystream EPUB artifacts + R2  
4. **P3** — Pearl News: enable schedule after green dry-run  

---

## 6. Key URLs

| Resource | URL |
|----------|-----|
| Stillness feed | see §1 |
| Feed pattern | `{CDN}/pearl-prime-content/{brand_id}/en_US/{week}/marketing_feed.json` |
| Funnel (Stillness) | `https://brand-admin-onboarding.pages.dev/free/{slug}/` |
| Funnel (Devotion) | `.../free/devotion_path/{slug}/` |
| Funnel (Waystream) | `.../free/way_stream_sanctuary/{slug}/` |

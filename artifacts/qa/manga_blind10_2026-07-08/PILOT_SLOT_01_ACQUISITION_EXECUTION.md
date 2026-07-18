# M6 Pilot — Slot 01 Acquisition Execution Sheet

**Run ID:** `manga_blind10_2026-07-08`  
**Date:** 2026-07-08  
**Layer:** SPECCED → operator execution (not PROVEN-AT-BAR)  
**Pilot slot:** 01 · iyashikei · `stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying` ep_001

---

## Comparator A — Yotsuba&! (comp_01_a)

| Field | Value |
|---|---|
| Creator | Kiyohiko Azuma |
| EN publisher | Yen Press |
| Volume | Vol 1 |
| Chapter | 1 (morning establishing sequence) |
| **Excerpt pages** | **pp 5–8** (4 pages) |
| Output filename | `comparators/yotsuba_v1_ch1_pages_5-8.pdf` |
| ISBN-13 | 978-0-7595-0410-5 |
| Registry ID | `comp_01_a` |

### Purchase (pick one — licensed retail only)

| Source | URL |
|---|---|
| Yen Press (publisher) | https://yenpress.com/products/yotsuba-vol-1 |
| Barnes & Noble | https://www.barnesandnoble.com/w/yotsuba-vol-1-kiyohiko-azuma/1100351234 |
| Amazon (ISBN lookup) | https://www.amazon.com/dp/0759504105 |
| Local indie / Kinokuniya | Operator discretion — retain receipt |

### Scan / export spec

1. Flatbed or document scanner at **300 DPI minimum** (600 DPI preferred for halftone).
2. Crop to **page bleed only** — no scanner bed, no fingers, no spine shadow on text.
3. Export **PDF**, sRGB, **4 pages** (pp 5–8 of printed volume).
4. Target file size: **≥ 500 KB**, **≤ 15 MB**.
5. Verify EN Yen Press edition page numbers match (count from first story page if TOC differs).
6. Run: `sha256sum comparators/yotsuba_v1_ch1_pages_5-8.pdf`
7. Update `COMPARATOR_REGISTRY.yaml` → `comp_01_a`: `asset_status: ACQUIRED`, `sha256`, `acquired_date`, `source_isbn`.

---

## Comparator B — Barakamon (comp_01_b)

| Field | Value |
|---|---|
| Creator | Satsuki Yoshino |
| EN publisher | Yen Press |
| Volume | Vol 1 |
| Chapter | 1 (arrival on island) |
| **Excerpt pages** | **pp 6–10** (5 pages) |
| Output filename | `comparators/barakamon_v1_ch1_pages_6-10.pdf` |
| ISBN-13 | 978-0-316-36217-6 |
| Registry ID | `comp_01_b` |

### Purchase (pick one — licensed retail only)

| Source | URL |
|---|---|
| Yen Press (publisher) | https://yenpress.com/products/barakamon-vol-1 |
| Barnes & Noble | https://www.barnesandnoble.com/w/barakamon-vol-1-satsuki-yoshino/1118334567 |
| Amazon (ISBN lookup) | https://www.amazon.com/dp/0316362177 |
| Local indie / Kinokuniya | Operator discretion — retain receipt |

### Scan / export spec

Same as Comparator A — **5 pages** (pp 6–10), output to `comparators/barakamon_v1_ch1_pages_6-10.pdf`.

---

## Post-acquisition validation (operator)

```bash
cd /Users/ahjan/phoenix_omega
python3 scripts/qa/validate_manga_blind10_comparators.py \
  --run-id manga_blind10_2026-07-08 \
  --require-p0
```

Expected when both PDFs land: exit 0, `pilot_ready: true`, `acquired: 2`.

Then update:

1. `COMPARATOR_REGISTRY.yaml` slot `01` — both entries `ACQUIRED` + sha256
2. `SOURCING_TRACKER.yaml` — `comparators.acquired: 2`, slot `01` statuses `ACQUIRED`
3. `BLOCKERS.md` — note M6-BLK-004 pilot subset unblocked (full 20 still pending)

---

## Judge outreach — Variant A (slot_01 pilot)

**Status:** drafted (not sent) — see `JUDGE_OUTREACH_DRAFTS_SLOT_01.md`  
**Target:** 8–10 en_US prospects · **floor:** 3 confirmed before packet distribution

### Prospect criteria (must meet ≥ 1)

| Rank | Profile | Where to find |
|---|---|---|
| 1 | Serialized manga editor / associate editor | LinkedIn: Viz, Yen Press, Kodansha USA, Seven Seas, local imprints |
| 2 | Lettering / localization lead (EN manga or webtoon) | Letterer guild contacts, Lion Forge / Kodansha loc alumni |
| 3 | Credited manga artist or assistant | Published volume credits (Amazon "Look Inside" contributor, ANN encyclopedia) |
| 4 | EN vertical-scroll / webtoon editor | Line Webtoon, Tapas, Webtoon Unscrolled editorial |

### Disqualifiers (do not contact)

- No professional serialized or collected manga / webtoon credits
- Active Phoenix Omega contractor on manga renders
- Hobbyist / fan translator without publisher credits

### Prospect list template (operator fills — not git)

| # | Name | Profile | Source | Outreach status |
|---|---|---|---|---|
| 1 | | | LinkedIn | drafted |
| 2 | | | referral | drafted |
| 3 | | | | drafted |
| 4 | | | | drafted |
| 5 | | | | drafted |
| 6 | | | | drafted |
| 7 | | | | drafted |
| 8 | | | | drafted |

**After send:** change status to `sent` in local copy only; log `prospects_contacted` in `SOURCING_TRACKER.yaml`.  
**Do not distribute judge packets** until both comparator PDFs pass validation.

### Pilot compensation / timeline (operator-set defaults in draft)

| Item | Suggested value |
|---|---|
| Rate | **$75–125 USD** for single slot_01 session (~30–45 min) |
| Timeline window | **2026-07-15 – 2026-07-29** (adjust before send) |
| NDA | Required before packet — store signed copies locally, not in git |

---

## Execution order (human)

```
1. [ ] Buy Yotsuba&! Vol 1 + Barakamon Vol 1 (URLs above)
2. [ ] Scan/export 2 PDFs → comparators/
3. [ ] Run validate_manga_blind10_comparators.py --require-p0
4. [ ] Update registry + tracker with sha256
5. [ ] Personalize JUDGE_OUTREACH_DRAFTS_SLOT_01.md (8–10 names)
6. [ ] Send Variant A emails — mark sent in local tracker
7. [ ] On ≥ 3 yes + NDA signed → assign judge_XX IDs in SOURCING_TRACKER.yaml
8. [ ] Run slot_01 pre-screen on Pearl Star (parallel OK before step 7)
9. [ ] Assemble judge_packets/slot_01_stillness_ep001/ only after steps 3 + 7
```

---

## Blockers this sheet does not clear

| ID | Still blocked until |
|---|---|
| M6-BLK-001 | M5 delivers ≥ 8 render-ready slots (full blind-10) |
| M6-BLK-002 | ≥ 3 judges confirmed in tracker |
| M6-BLK-003 | Pearl Star GPU online for pre-screen |
| M6-BLK-004 (full) | All 20 comparators acquired |

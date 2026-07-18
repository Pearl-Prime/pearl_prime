# M6 — Judge Prospect List (slot_01 pilot)

**Run ID:** `manga_blind10_2026-07-08`  
**Status:** `ready_to_send` — **0 contacted, 0 confirmed**  
**Variant:** A (iyashikei episode, en_US lane)  
**Date:** 2026-07-08

---

## Headcount targets

| Metric | Floor | Ideal |
|---|---|---|
| Prospects on list | 8 | 10 |
| Confirmed judges | **3** | 5 |

---

## Prospect list (operator personalizes + sends)

Public professional credits only. Verify current employment before send; do not contact Phoenix contractors.

| # | Name | Profile | Credential summary | Source | Outreach status |
|---|---|---|---|---|---|
| 1 | **Carl Li** | Manga Editor | Yen Press manga editor; serialized EN manga editorial | [LinkedIn](https://www.linkedin.com/in/carl-li-4496336) | ready_to_send |
| 2 | **Won Young Seo** | Manga Editor | Yen Press editor; JP manga + KR manhwa/novel localization | [LinkedIn](https://www.linkedin.com/in/won-young-seo-434902150) | ready_to_send |
| 3 | **Jacquelyn Li** | Associate Editor | Yen Press; JP manga + CN comics localization review | [LinkedIn](https://www.linkedin.com/in/jacquelyn-li-869631213) | ready_to_send |
| 4 | **Rachel Mimms** | Associate Editor / Letterer | Yen Press localization; letters manga (2025 reel) | [LinkedIn](https://www.linkedin.com/in/rachel-mimms) | ready_to_send |
| 5 | **Tania Biswas** | Localization Manager | Yen Press localization lead (verify via yenpress.com team page) | Yen Press careers / LinkedIn | ready_to_send |
| 6 | **Eve Grandt** | Letterer | Credited letterer on multiple Viz/Yen Press volumes | ANN encyclopedia / portfolio | ready_to_send |
| 7 | **Joel Enos** | Editor | Viz Media senior editor (verify current role) | LinkedIn / Viz credits | ready_to_send |
| 8 | **Lillian Olsen** | Editor | Seven Seas manga editor (verify current role) | LinkedIn / Seven Seas credits | ready_to_send |
| 9 | **Kodansha USA editorial** | Editor pool | Kodansha Comics serialized manga editorial | kodansha.us team page | ready_to_send |
| 10 | **Webtoon Unscrolled editorial** | Webtoon editor | EN vertical-scroll editorial lane | webtoons.com careers | ready_to_send |

---

## Personalization notes (per prospect)

Use `JUDGE_OUTREACH_DRAFTS_SLOT_01.md` Variant A. Replace `[Name]` and add one line showing you read their credits:

| # | Suggested hook |
|---|---|
| 1–4 | Reference specific Yen Press iyashikei/slice-of-life titles they edited |
| 5 | Localization workflow + genre calibration angle |
| 6 | Lettering craft axis on rubric (lettering_weight) |
| 7–8 | Competitor-publisher editorial perspective |
| 9–10 | Vertical-scroll / webtoon register fluency |

---

## Send gate (all must be true before packet)

- [x] `validate_manga_blind10_comparators.py --require-p0` → exit 0 (`pilot_ready: true`)
- [ ] ≥3 judges `status: confirmed` in `SOURCING_TRACKER.yaml`
- [ ] Pre-screen JSON archived (Pearl Star online)
- [ ] NDA template ready (local, not git)

---

## Post-send tracker updates

After operator sends emails:

```yaml
judges:
  status: recruiting
  outreach:
    status: sent
  locale_lanes:
    en_US:
      prospects_contacted: <N>
```

Append confirmed judges to `judges.recruited[]` only after NDA returned.

---

## Disqualifiers (do not contact)

- No professional serialized or collected manga / webtoon credits
- Active Phoenix Omega contractor on manga renders
- Hobbyist / fan translator without publisher credits

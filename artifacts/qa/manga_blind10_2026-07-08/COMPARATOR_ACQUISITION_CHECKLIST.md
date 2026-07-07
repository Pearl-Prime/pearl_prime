# M6 Blind-10 — Comparator Acquisition Checklist

**Run ID:** `manga_blind10_2026-07-08`  
**Rule:** 2 comparators per slot × 10 slots = **20 excerpts** total  
**Asset root:** `artifacts/qa/manga_blind10_2026-07-08/comparators/` (gitignored — operator local)

---

## Sourcing rules (all slots)

1. **Licensed only** — purchased volume, publisher marketing asset, or operator-owned scan with provenance
2. **5–12 pages per excerpt** — genre-matched establishing or craft-dense sequence
3. **Record before distribution:** `sha256`, source (ISBN / purchase receipt / publisher URL), date acquired
4. **Forbidden:** Phoenix renders, AI-generated refs, aggregate pirate sites

Update `COMPARATOR_REGISTRY.yaml` `asset_status` → `ACQUIRED` and `SOURCING_TRACKER.yaml` when each PDF lands.

---

## Per-slot acquisition list

| Slot | Genre | Comparator A | Excerpt target | Comparator B | Excerpt target | Priority |
|---|---|---|---|---|---|---|
| **01** | iyashikei | **Yotsuba&!** — Kiyohiko Azuma | Vol 1, Ch 1, pp 5–8 | **Barakamon** — Satsuki Yoshino | Vol 1, Ch 1, pp 6–10 | **P0** (pilot) |
| **02** | iyashikei | **March Comes in Like a Lion** — Chica Umino | Vol 1, Ch 1, pp 8–14 | **Mushishi** — Yuki Urushibara | Vol 1, Ch 1, pp 6–11 | P1 (M5 re-render) |
| **03** | mecha | **Mobile Suit Gundam: The Origin** — Yoshikazu Yasuhiko | Vol 1, cockpit intro | **Planetes** — Makoto Yukimura | Vol 1, workplace-mechanical routine | P1 |
| **04** | psychological_thriller | **Monster** — Naoki Urasawa | Vol 1, tension dialogue | **20th Century Boys** — Naoki Urasawa | Vol 1, paranoia-establishing | P1 |
| **05** | action_battle | **Vinland Saga** — Makoto Yukimura | Vol 1, Ch 1, pp 10–18 | **Demon Slayer** — Koyoharu Gotouge | Vol 1, Ch 1, pp 8–15 | P2 |
| **06** | dark_fantasy | **Berserk** — Kentaro Miura | Vol 1, Ch 1, pp 12–20 | **Frieren: Beyond Journey's End** — Kanehito Yamada / Tsukasa Abe | Vol 1, Ch 1, pp 6–12 | P2 |
| **07** | isekai | **Re:Zero** — Tappei Nagatsuki / Shinichirou Otsuka | Vol 1, Ch 1, arrival sequence | **Mushoku Tensei** — Rifujin na Magonote / Yuka Fujikawa | Vol 1, Ch 1, pp 8–14 | P2 |
| **08** | workplace_drama | **Aggretsuko** — Yeti (Sanrio) | Vol 1, office-pressure sequence | **Wotakoi: Love Is Hard for Otaku** — Fujita | Vol 1, Ch 1, workplace beat | P2 |
| **09** | school_coming_of_age | **March Comes in Like a Lion** — Chica Umino | Vol 2, school-belonging sequence | **Keep Your Hands Off Eizouken!** — Sumito Owara | Vol 1, Ch 1, club-room intro | P2 |
| **10** | sci_fi_cyberpunk | **Akira** — Katsuhiiro Otomo | Vol 1, Ch 1, pp 10–18 | **Ghost in the Shell** — Masamune Shirow | Vol 1, Ch 1, body-machine intro | P2 |

**P0** = blocks slot_01 pilot judge packet. **P1** = first M5-assembled slots (02–04). **P2** = remaining blind-10 slots when renders land.

---

## Operator steps (per comparator)

```
[ ] Purchase / scan licensed volume
[ ] Export 5–12 page PDF to comparators/<filename>.pdf
[ ] sha256sum comparators/<filename>.pdf
[ ] Update COMPARATOR_REGISTRY.yaml: asset_status=ACQUIRED, sha256, acquired_date
[ ] Update SOURCING_TRACKER.yaml comparators.acquired count
[ ] Verify PDF has no Phoenix watermarks and no AI-gen artifacts
```

---

## Volume purchase shortcuts (en_US market)

| Title | Typical EN edition | Notes |
|---|---|---|
| Yotsuba&! | Yen Press Vol 1 | Pilot comp A |
| Barakamon | Yen Press Vol 1 | Pilot comp B |
| March Comes in Like a Lion | Yen Press Vol 1–2 | Slots 02 + 09 |
| Mushishi | Del Rey / Kodansha Vol 1 | Slot 02 |
| Gundam: The Origin | Vertical Vol 1 | Slot 03 |
| Planetes | Dark Horse Omnibus 1 | Slot 03 |
| Monster | Viz Perfect Edition Vol 1 | Slot 04 |
| 20th Century Boys | Viz Perfect Edition Vol 1 | Slot 04 |
| Vinland Saga | Kodansha Vol 1 | Slot 05 |
| Demon Slayer | Viz Vol 1 | Slot 05 |
| Berserk | Dark Horse Vol 1 (Deluxe) | Slot 06 — mature content flag for judges |
| Frieren | Viz Vol 1 | Slot 06 |
| Re:Zero | Yen Press Vol 1 | Slot 07 |
| Mushoku Tensei | Seven Seas Vol 1 | Slot 07 |
| Aggretsuko | Oni Press Vol 1 | Slot 08 |
| Wotakoi | Kodansha Vol 1 | Slot 08 |
| Keep Your Hands Off Eizouken! | Viz Vol 1 | Slot 09 |
| Akira | Kodansha Epic Collection Vol 1 | Slot 10 |
| Ghost in the Shell | Kodansha Vol 1 | Slot 10 |

---

## Exit criteria (comparator lane)

- **Pilot ready:** slot 01 both comparators `ACQUIRED`
- **Full blind-10 ready:** all 20 comparators `ACQUIRED` with sha256 logged
- **M6-BLK-004 cleared** when pilot + scheduled slots have assets on disk

# Pearl Prime Intro Deck — Image Integration Handoff

**Session dates:** 2026-04-18 / 2026-04-19 / 2026-04-20
**Live deployment:** https://10cf53cc.phoenix-command.pages.dev/presenter?deck=intro&lane=us&briefing=briefing_us
**Alias URL:** https://agent-scenario-a-template-wi.phoenix-command.pages.dev/presenter?deck=intro&lane=us&briefing=briefing_us
**File modified:** `brand-wizard-app/public/presenter.html`

---

## What Was Done

Generated 48 cinematic AI images (12 slides × 4 variants each) via Bing Image Creator, then wired them into the Pearl Prime intro presenter as per-slide slideshows. Each slide's visual panel now shows its existing data/chart content first, followed by an auto-cycling 4-image slideshow of the Bing-generated gold editorial images.

---

## Image Generation

**Tool:** Bing Image Creator (DALL-E 3)
**Style prompt prefix:** `cinematic dark editorial, [subject], amber and gold light, dark background, ultra-detailed 4K`
**Format:** 1024×1024 JPEG via Bing CDN
**CDN base:** `https://th.bing.com/th/id/<ID>?w=1024&h=1024&c=6&r=0&o=5&pid=ImgGn`
**Account:** Images saved to Bing "My Creations" history under the logged-in account

---

## Slideshow Implementation

Added to `presenter.html` before the `SLIDE_VISUALS` block:

```javascript
function bingSlideshow(ids){
  var q='?w=1024&h=1024&c=6&r=0&o=5&pid=ImgGn';
  var cid='bss'+Math.floor(Math.random()*1e9);
  // renders 4 stacked images, shows 1 at a time
  // auto-cycles every 3.5s
  // amber dot indicator tracks position
  // self-cleans interval when container leaves DOM
}
```

Called at the END of each `SLIDE_VISUALS[...]` function, after the existing chart/card/cover content.

---

## Full Image Inventory

All 48 IDs. First listed is the one shown on page load.

### Slide 1 — Welcome (The Opportunity)
`SLIDE_VISUALS["intro:Welcome"]`
```
OIG4.pLvPzpQL7nt.ndFjiWSR
OIG2.tYb60IJfo6cSFAeV5si_
OIG2.1Lp4mW0alwZHXcYKiTOG
OIG4.et48p4f22Gxk5bSeLkIb
```

### Slide 2 — Overview & Revenue (Revenue Projection)
`SLIDE_VISUALS["intro:Overview & Revenue"]`
```
OIG4.RmeQcgHZhTT1pzDI0CtQ
OIG4.XMxfqu24hhb3aaALE5Mz
OIG4.ERdFPub7v.uKDNFJ75Ik
OIG4.RCtZhvSvsOTAxCLCDCCd
```

### Slide 3 — Origin & Mission (What Is Ei)
`SLIDE_VISUALS["intro:Origin & Mission"]`
```
OIG1.TTMcX6tYI8z.KrbmBxTdj6ITzTr9bC2R
OIG1.spGONbCYqaxptzMAFiHmlw61QFc5tef6
OIG1.Rde4y7STKVFm38EBH28B
OIG1.bZ3lfDMb7vkQNW4d2wUd
```

### Slide 4 — Architecture (Pipeline Proof)
`SLIDE_VISUALS["intro:Architecture"]`
```
OIG2.S6mbPjUaqqaJNH4o3MWY
OIG2.pDbnTZ6mYFxDT.6GiCV0
OIG2.crQcJMCqWJg5X2W.KnoI
OIG2.KPbw7oNCL0jFkWXEBa6W
```

### Slide 5 — Brand Angles
`SLIDE_VISUALS["intro:Brand Angles"]`
```
OIG3.uwNLiPNyv7p_7GLNiTzU
OIG3.QRa26CaaY0PjYQ4TZ8pI
OIG3.3XMW4J9J8LFYXKImOje_
OIG3.qbI2PsLlnEmXD9_ZSgQF
```

### Slide 6 — 48Social (48Social + Growth)
`SLIDE_VISUALS["intro:48Social"]`
```
OIG3.FjO4ds_M7DyCyM.qGMm1
OIG3.ONcv8hFv63O4v0lgQeS5
OIG3.Ws22yo54t.vl3Bqu3s4p
OIG3.OrWUyvA3.xwqiVlt0Esl
```

### Slide 7 — Weekly OS
`SLIDE_VISUALS["intro:Weekly OS"]`
```
OIG1.aUCveB_rpqv5Qd49vCCQ
OIG1.GI94_xs9zRw2XNxf48Rn
OIG1.FGXtdOd5TsNNTAZJQc_n
OIG1.f6OwyVntjWG4LaHfV3LR
```

### Slide 8 — Platform Revenue (Platform Strategy)
`SLIDE_VISUALS["intro:Platform Revenue"]`
```
OIG2.srHiHdTDQDDCeUfkib4X
OIG2.b05ZTV.Fdc59ozs.DaQG
OIG2.eJkSFnqVw9XnMcXLzEpd
OIG2.tBKl7Me1DdHl1Pw4NWUq
```

### Slide 9 — Close (The Close)
`SLIDE_VISUALS["intro:Close"]`
```
OIG1.gUbd7vWCPV89QCmO7cvS
OIG1.imQ1nzHO7K8yvPB0nyG5
OIG1.Kpk_hvJwmuc8GFrlgazu
OIG1.gC6xABtla7xAz_oo0CPC
```

### JP Path — JP Overview (Revenue Split)
`SLIDE_VISUALS["intro:JP"]`
```
OIG1.jIL5tQF7MtyJuy6zZ5h7prK9rPXhWKOA
OIG1.PsP.V1OzcQPJyY1fbBK.dlSBd6Yb87Bb
OIG1.8WLt_eYSorTTieI7pqVs88eZXhGdeOde
OIG1.cLNMjXSwHXfMi12pfreNd0UZGL6zT985
```

### JP Path — Ei Adaptation (Zero COGS)
`SLIDE_VISUALS["intro:Ei Adaptation"]`
```
OIG1.qSoZcQVZcaQDqow.JUtBGAQGpJw871WK
OIG1.V6pO_D4MUwwt.p7ldArPyPJmfggBVrS1
OIG1.iBOrpQ3NxmdV9a84ZN4b.O6EHS9.aEvW
OIG1.HecY9s0_5qX1MUXhQNawH14uvGO7QCvx
```

### JP Path — Incorporation (Catalog Architecture)
`SLIDE_VISUALS["intro:Incorporation"]`
```
OIG1.O.q1U.g2yvWSTO55k_ayO4koT5rNWDAm
OIG1.hM78v0wM7_hlh8wj6U2X.wSwd6yj6BLe
OIG1.NZWrAy5l9nALxdHkB_5uShD1ZVH.39pa
OIG1.TvWtBUlSh5fq0X8PdTNbruZHSCU0oIw3
```

---

## Deployment History (this session)

| Hash | Change |
|------|--------|
| `a58fda3f` | Initial single-hero-image per slide (local files) |
| `d75e11d7` | Added slides 1–5, Welcome visual, JP slides |
| `e909c0a4` | Switched to 2×2 Bing grid layout |
| `10cf53cc` | **Current** — 1 image at a time, auto-cycling slideshow, existing content first |

---

## Known Limitations

- **Bing CDN expiry:** Bing-hosted thumbnail/image URLs (`th.bing.com/th/id/OIG...`) are tied to the generating account's session. If they expire or are removed from Bing history, the slideshow images will disappear silently (`onerror="this.style.display='none'"` handles graceful fallback).
- **Fix if URLs expire:** Re-generate images (same prompts), update IDs in `bingSlideshow([...])` calls in `presenter.html`, redeploy.
- **Local backup:** 7 images were downloaded to the main repo at `brand-wizard-app/public/assets/deck_imgs/` (first variant per slide, slides 6–12 only). These are not referenced in the live code but serve as local backups.
- **No marketing/briefing decks:** Images were only added to the `intro` deck SLIDE_VISUALS. The `marketing:*` and `briefing_*` SLIDE_VISUALS are unchanged.

---

## To Swap an Image

Find the relevant `SLIDE_VISUALS["intro:..."]` function in `presenter.html`, locate the `bingSlideshow([...])` call, replace any of the 4 IDs with a new Bing image ID, redeploy:

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
npx wrangler pages deploy brand-wizard-app/public --project-name phoenix-command
```

---

## To Add Images to Marketing / Briefing Decks

Same pattern — append `+bingSlideshow([id1,id2,id3,id4])` to any `SLIDE_VISUALS["marketing:..."]` or `SLIDE_VISUALS["briefing_us:..."]` function's `vp.innerHTML` string.

# Global Markets Distribution Guide — ko / es-US / es-ES / fr / de / it / hu / pt-BR

Authority doc for the eight non-CJK Weekly-OS market profiles added in the
14-market localization pass. Companion to the existing
`en_US_distribution_guide.md`, `zh_TW_distribution_guide.md`,
`zh_CN_distribution_guide.md`, `zh_HK_distribution_guide.md`,
`zh_SG_distribution_guide.md`.

**Scope.** This guide records the *self-serve* (`ready`) vs *agency/publisher-gated*
(`planned`) split encoded in
`config/brand_management/brand_admin_weekly_os_platforms.yaml` for each market.
`ready` = a brand director can open the signup URL and publish today. `planned` =
the platform is real and relevant but is contract/agency/CP-gated or not yet wired
into the repo's weekly packet output — surfaced in the OS as a *planned* row with
no download button, never presented as automated.

**Global self-publishing spine (ready in every market below unless noted):** Amazon
KDP (localized marketplace), Google Play Books, Apple Books, Kobo Writing Life,
Draft2Digital, WEBTOON Canvas, YouTube, TikTok, Instagram, Spotify for Creators.
Markets differ mainly in the *local* retailers layered on top.

---

## Korea — `ko_kr` (한국어)

- **Ready (self-serve):** Amazon KDP, Google Play Books, Apple Books, Kobo Writing
  Life, YouTube, TikTok, Instagram, Naver 도전만화 / WEBTOON Canvas (`comic.naver.com/challenge`).
- **Planned (publisher/CP-gated — no self-serve signup):** 리디북스 (Ridibooks),
  네이버 시리즈 (Naver Series), 카카오페이지 (KakaoPage), 밀리의 서재 (Millie's Library),
  YES24 eBook, 교보문고 (Kyobo). Korea's dominant ebook/webnovel platforms all require
  a publisher/content-provider contract; there is no foreign self-serve path.
- **Note:** achievement/burnout culture (학벌, 빨리빨리) favors micro-format, secular framing.

## US Hispanic — `es_us` (Español, neutral LatAm)

- **Territory:** US storefronts, Spanish-language metadata/covers (same territory as
  en-US, different locale — do not mix uploads).
- **Ready:** Amazon KDP (US, español), Google Play Books, Apple Books US, Kobo Writing
  Life, Barnes & Noble Press, Draft2Digital, WEBTOON Canvas (español), YouTube, TikTok,
  Instagram, Spotify for Creators.
- **Planned:** Storytel LatAm and similar subscription-audio require aggregator deals.

## Spain — `es_es` (Español, Castellano)

- **Ready:** Amazon KDP (Amazon.es), Google Play Books, Apple Books ES, Kobo Writing
  Life (strong in Spain via Fnac/Rakuten), StreetLib, Draft2Digital, WEBTOON Canvas,
  YouTube, TikTok, Instagram.
- **Planned:** Casa del Libro / Tagus, Lantia, Bookwire/Odilo library channels
  (aggregator/retailer-gated).
- **Note:** Castilian register (vosotros, c/z). Separate storefront from es-US.

## France — `fr_fr` (Français)

- **Ready:** Amazon KDP (Amazon.fr), Google Play Livres, Apple Books FR, Kobo Writing
  Life (very strong in France via Fnac), Vivlio (ex-TEA/ePagine), 7switch, Librinova,
  StreetLib, Draft2Digital, WEBTOON Canvas, YouTube, TikTok, Instagram.
- **Planned:** Bookelis→librairies distribution, Numilog/Immatériel aggregation.

## Germany — `de_de` (Deutsch)

- **Ready:** Amazon KDP (Amazon.de), Google Play Bücher, Apple Books DE, **Tolino Media**
  (`partner.tolino-media.de` — self-publish into Thalia/Weltbild/Hugendubel/Tolino,
  the dominant German ebook network), Kobo Writing Life, BoD, neobooks, Draft2Digital,
  WEBTOON Canvas, YouTube, TikTok, Instagram, Spotify for Creators.
- **Planned:** Audible ACX (not self-serve for DE), Skoobe/library subscription.

## Italy — `it_it` (Italiano)

- **Ready:** Amazon KDP (Amazon.it), Google Play Libri, Apple Books IT, Kobo Writing
  Life (strong via Mondadori/laFeltrinelli), StreetLib (Italian-origin), Youcanprint,
  Draft2Digital, WEBTOON Canvas, YouTube, TikTok, Instagram.
- **Planned:** IBS.it / laFeltrinelli direct, Bookrepublic, Storytel IT.

## Hungary — `hu_hu` (Magyar)

- **Small market — most local channels are application/retailer-gated; be honest.**
- **Ready:** Amazon KDP (limited HU metadata but functional), Google Play Könyvek,
  Apple Books, Draft2Digital, WEBTOON Canvas, YouTube, TikTok, Instagram.
- **Planned:** Publio (`publio.hu`, application-based Hungarian ebook self-publish),
  Libri-Bookline / eKönyv (`bookline.hu`, retailer-gated), Kobo (weak HU presence),
  DiBook.

## Brazil — `pt_br` (Português)

- **Ready:** Amazon KDP (Amazon.com.br), Google Play Livros, Apple Books, Kobo Writing
  Life, Draft2Digital, StreetLib, WEBTOON Canvas (português), YouTube, TikTok, Instagram,
  Spotify for Creators.
- **Planned:** Ubook (audiolivro, agency), Skeelo, Simplíssimo/AGBook distribution,
  Storytel BR, Tocalivros.

---

## Maintenance

When a `planned` platform gains a real self-serve signup path **and** the repo weekly
packet emits matching upload files, flip its `status` to `ready` in the YAML and
regenerate `brand-wizard-app/public/brand_admin_weekly_os_data.json` via
`scripts/onboarding/gen_brand_admin_weekly_os_data.py`. Do not flip a row to `ready`
that a director cannot actually action today.

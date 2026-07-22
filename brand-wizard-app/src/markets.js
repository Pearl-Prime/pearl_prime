/**
 * Shared 14-market roster for onboarding hub + wizards.
 * Market tokens map to lane suffixes via brandMatch.LANE_FROM_MARKET.
 */

export const ONBOARDING_MARKETS = [
  { id: "us", flag: "🇺🇸", label: "United States", sub: "Amazon KDP · Apple Books · Spotify", lane: "en_us", lang: "en" },
  { id: "jp", flag: "🇯🇵", label: "Japan", sub: "楽天Kobo · Audiobook.jp · Piccoma", lane: "ja_jp", lang: "ja" },
  { id: "tw", flag: "🇹🇼", label: "Taiwan", sub: "Readmoo · Kobo TW · BOOKWALKER", lane: "zh_tw", lang: "tw" },
  { id: "cn", flag: "🇨🇳", label: "Mainland China", sub: "Ximalaya · Dangdang · WeChat Reading", lane: "zh_cn", lang: "zh" },
  { id: "kr", flag: "🇰🇷", label: "Korea", sub: "Naver Series · Kakao Page · Millie's", lane: "ko_kr", lang: "ko" },
  { id: "hk", flag: "🇭🇰", label: "Hong Kong", sub: "Kobo HK · Google Play · Apple Books", lane: "zh_hk", lang: "tw" },
  { id: "sg", flag: "🇸🇬", label: "Singapore", sub: "Google Play · Apple Books · Kobo", lane: "zh_sg", lang: "zh" },
  { id: "mexico", flag: "🇲🇽", label: "Spanish (US / LatAm)", sub: "Amazon · Google Play · Apple Books", lane: "es_us", lang: "es" },
  { id: "spain", flag: "🇪🇸", label: "Spain", sub: "Amazon.es · Casa del Libro · Audible", lane: "es_es", lang: "es_es" },
  { id: "france", flag: "🇫🇷", label: "France", sub: "Amazon.fr · Fnac · Audible", lane: "fr_fr", lang: "fr" },
  { id: "germany", flag: "🇩🇪", label: "Germany", sub: "Amazon.de · Tolino · Audible", lane: "de_de", lang: "de" },
  { id: "italy", flag: "🇮🇹", label: "Italy", sub: "Amazon.it · IBS · Audible", lane: "it_it", lang: "it" },
  { id: "hungary", flag: "🇭🇺", label: "Hungary", sub: "Libri · Bookline · Google Play", lane: "hu_hu", lang: "hu" },
  { id: "brazil", flag: "🇧🇷", label: "Brazil", sub: "Amazon.br · Google Play · Apple Books", lane: "pt_br", lang: "pt" },
];

/** UI/i18n lang key → default market when ?market= is absent */
export const LANG_TO_DEFAULT_MARKET = {
  en: "us",
  ja: "jp",
  zh: "cn",
  tw: "tw",
  ko: "kr",
  es: "mexico",
  es_es: "spain",
  fr: "france",
  de: "germany",
  it: "italy",
  hu: "hungary",
  pt: "brazil",
};

/** Lane suffix → market token for ops / roster deep links */
export const LANE_TO_MARKET = Object.fromEntries(
  ONBOARDING_MARKETS.map((m) => [m.lane, m.id])
);

export function normMarketToken(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
}

/**
 * Resolve market for wizard boot. Prefer explicit ?market=, then localStorage,
 * then ?lang=→default market. Never silently invent "us" when lang implies another lane.
 */
export function resolveSeededMarket({ searchParams, localStorageGet } = {}) {
  const params = searchParams || new URLSearchParams(typeof window !== "undefined" ? window.location.search : "");
  const getLs =
    localStorageGet ||
    ((key) => {
      try {
        return localStorage.getItem(key);
      } catch (_) {
        return null;
      }
    });

  const explicit = normMarketToken(params.get("market") || params.get("lane") || "");
  if (explicit) {
    return { market: explicit, source: "url" };
  }

  const stored = normMarketToken(getLs("phoenix_onboarding_market") || getLs("phoenix_lane") || "");
  if (stored) {
    return { market: stored, source: "localStorage" };
  }

  const lang = normMarketToken(params.get("lang") || params.get("locale") || "");
  if (lang && LANG_TO_DEFAULT_MARKET[lang]) {
    return { market: LANG_TO_DEFAULT_MARKET[lang], source: "lang" };
  }

  return { market: "us", source: "default" };
}

export function wizardHrefForMarket(market) {
  const key = normMarketToken(market);
  const row = ONBOARDING_MARKETS.find((m) => m.id === key || m.lane === key);
  const marketToken = row?.id || key || "us";
  const lang = row?.lang || "en";
  if (marketToken === "jp" || key === "japan" || key === "ja_jp") {
    return `/wizard-ja.html?mode=composite&market=${encodeURIComponent(marketToken)}`;
  }
  if (marketToken === "tw" || marketToken === "hk" || key === "taiwan" || key === "zh_tw" || key === "zh_hk") {
    return `/wizard-tw.html?mode=composite&market=${encodeURIComponent(marketToken)}`;
  }
  if (marketToken === "cn" || marketToken === "sg" || key === "china" || key === "zh_cn" || key === "zh_sg") {
    return `/wizard-zh.html?mode=composite&market=${encodeURIComponent(marketToken)}`;
  }
  return `/wizard.html?lang=${encodeURIComponent(lang)}&mode=composite&market=${encodeURIComponent(marketToken)}`;
}

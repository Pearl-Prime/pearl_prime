// Map any market/lane token → the correct localized Brand Wizard URL.
// jp/tw/cn keep their dedicated forked builds (extra locale guards); every other
// market rides the generic wizard.html with an explicit ?lang= so nothing lands
// on US-English copy by accident.
const norm = (s) => String(s || "").toLowerCase().replace(/[\s-]+/g, "_");

const DEDICATED = {
  jp: "/wizard-ja.html", japan: "/wizard-ja.html", ja_jp: "/wizard-ja.html",
  tw: "/wizard-tw.html", taiwan: "/wizard-tw.html", zh_tw: "/wizard-tw.html",
  cn: "/wizard-zh.html", china: "/wizard-zh.html", zh_cn: "/wizard-zh.html",
};

// market token → generic-wizard ?lang= key
const LANG_BY_MARKET = {
  us: "en", usa: "en", en_us: "en",
  kr: "ko", korea: "ko", ko_kr: "ko",
  hk: "tw", hong_kong: "tw", zh_hk: "tw",
  sg: "zh", singapore: "zh", zh_sg: "zh",
  mexico: "es", es_us: "es", latam: "es",
  spain: "es_es", es_es: "es_es",
  france: "fr", fr_fr: "fr",
  germany: "de", de_de: "de",
  italy: "it", it_it: "it",
  hungary: "hu", hu_hu: "hu",
  brazil: "pt", br: "pt", pt_br: "pt",
};

function wizardHref(market) {
  const key = norm(market);
  const dedicated = DEDICATED[key];
  if (dedicated) return `${dedicated}?mode=composite&market=${encodeURIComponent(market)}`;
  const lang = LANG_BY_MARKET[key] || "en";
  return `/wizard.html?lang=${lang}&mode=composite&market=${encodeURIComponent(market)}`;
}

export default function WizardHandoff({ market = "us" }) {
  const href = wizardHref(market);

  const persistMarket = () => {
    try {
      localStorage.setItem("phoenix_onboarding_market", market);
    } catch (_) {}
  };

  return (
    <div className="py-32 px-6 text-center">
      <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-6">Step 10</p>
      <h2 className="font-serif text-5xl text-amber-100 mb-6 font-light">Ready to begin?</h2>
      <p className="text-amber-100/50 text-sm mb-12 max-w-md mx-auto leading-relaxed">
        The Brand Wizard will configure your voice, angle, market, and content spine.
        It takes about 11 steps and 8 minutes.
      </p>
      <a
        href={href}
        onClick={persistMarket}
        className="inline-block bg-amber-700 hover:bg-amber-600 text-amber-50 text-xs font-mono tracking-widest uppercase px-10 py-4 transition-colors"
      >
        Launch Brand Wizard →
      </a>
      <div className="mt-8">
        <a href="/presenter" className="text-xs font-mono text-amber-100/30 hover:text-amber-100/60 transition-colors tracking-widest uppercase">
          View market briefings instead
        </a>
      </div>
    </div>
  );
}

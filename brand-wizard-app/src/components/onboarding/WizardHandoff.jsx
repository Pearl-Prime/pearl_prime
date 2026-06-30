const WIZARD_BY_MARKET = {
  us: "/wizard.html",
  jp: "/wizard-ja.html",
  tw: "/wizard-tw.html",
  cn: "/wizard-zh.html",
  kr: "/wizard.html",
};

export default function WizardHandoff({ market = "us" }) {
  const wizardPath = WIZARD_BY_MARKET[market] || "/wizard.html";
  const href = `${wizardPath}?mode=composite&market=${encodeURIComponent(market)}`;

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

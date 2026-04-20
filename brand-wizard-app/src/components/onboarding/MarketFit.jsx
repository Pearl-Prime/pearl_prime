const DATA = {
  us:  { heading: "United States", cpc: "$1.20", pop: "330M", demand: "Highest self-help search volume globally. Nervous System angle dominates. Burnout + anxiety + somatic work.",  dist: "Amazon KDP · Apple Books · Spotify · Audible · Findaway" },
  jp:  { heading: "Japan", cpc: "¥45 (~$0.30)", pop: "125M", demand: "Manga-native audience. Academic entrance exam anxiety. Karoshi workplace burnout. Mental health stigma = underserved market.", dist: "楽天Kobo · Audiobook.jp · Piccoma · LINE Manga · Kindle JP" },
  tw:  { heading: "Taiwan", cpc: "NT$12 (~$0.38)", pop: "23M", demand: "Traditional Chinese self-help gap. High literacy. Strong ebook penetration. Therapeutic content underserved.", dist: "Readmoo · Kobo TW · BOOKWALKER · myBook · Apple Books TW" },
  cn:  { heading: "Mainland China", cpc: "¥3 (~$0.42)", pop: "1.4B", demand: "345M Ximalaya users. Audiobook boom. Gen Z mental wellness demand. Largest single-language audience.", dist: "Ximalaya · Dangdang · WeChat Reading · NetEase Cloud Music" },
  kr:  { heading: "Korea", cpc: "₩70 (~$0.054)", pop: "52M", demand: "빨리빨리 culture meets therapeutic need. Naver at 5 cents per click. K-beauty wellness crossover audience.", dist: "Naver Series · Kakao Page · Millie's Library · Yes24 · Ridi" },
};

export default function MarketFit({ market = "us" }) {
  const d = DATA[market] || DATA.us;
  return (
    <div className="py-24 px-6 bg-amber-950/10">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 7</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-2">{d.heading} market fit</h2>
        <p className="text-amber-100/50 text-sm text-center mb-12">Validated demand signals for your chosen market.</p>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-5 border border-amber-900/30">
            <div className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-1">Avg. CPC</div>
            <div className="text-2xl text-amber-200">{d.cpc}</div>
          </div>
          <div className="p-5 border border-amber-900/30">
            <div className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-1">Market size</div>
            <div className="text-2xl text-amber-200">{d.pop}</div>
          </div>
        </div>
        <div className="p-6 border border-amber-900/30 mb-4">
          <div className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-2">Demand insight</div>
          <p className="text-amber-100/70 text-sm leading-relaxed">{d.demand}</p>
        </div>
        <div className="p-5 border border-amber-900/30">
          <div className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-2">Distribution</div>
          <p className="text-amber-100/50 text-sm">{d.dist}</p>
        </div>
      </div>
    </div>
  );
}

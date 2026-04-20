const MARKETS = [
  { id: "us", flag: "🇺🇸", label: "United States", sub: "Amazon KDP · Apple Books · Spotify" },
  { id: "jp", flag: "🇯🇵", label: "Japan", sub: "楽天Kobo · Audiobook.jp · Piccoma" },
  { id: "tw", flag: "🇹🇼", label: "Taiwan", sub: "Readmoo · Kobo TW · BOOKWALKER" },
  { id: "cn", flag: "🇨🇳", label: "Mainland China", sub: "Ximalaya · Dangdang · WeChat Reading" },
  { id: "kr", flag: "🇰🇷", label: "Korea", sub: "Naver Series · Kakao Page · Millie's" },
];

export default function CountrySelection({ selected, onSelect }) {
  return (
    <div className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 2</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-2">Choose your market</h2>
        <p className="text-amber-100/50 text-center mb-12 text-sm">Your selection filters everything below.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {MARKETS.map((m) => (
            <button
              key={m.id}
              onClick={() => onSelect(m.id)}
              className={[
                "text-left p-5 border transition-all duration-200",
                selected === m.id
                  ? "border-amber-600 bg-amber-900/20"
                  : "border-amber-900/30 hover:border-amber-700/50 hover:bg-amber-900/10",
              ].join(" ")}
            >
              <span className="text-3xl mb-3 block">{m.flag}</span>
              <div className="font-medium text-amber-100 text-sm mb-1">{m.label}</div>
              <div className="text-xs text-amber-100/40">{m.sub}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

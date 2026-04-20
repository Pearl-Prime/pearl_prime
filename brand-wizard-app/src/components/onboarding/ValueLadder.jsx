const TIERS = [
  { label: "Month 1–2", rev: "$0 – $200", note: "Platform approvals. Algorithmic cold start. First uploads land." },
  { label: "Month 3–6", rev: "$200 – $1,500", note: "Reviews accumulate. Discovery activates. 48Social content compounds." },
  { label: "Month 6–12", rev: "$500 – $3,000 / mo", note: "Catalogue depth. Cross-platform reach. Passive royalty layers." },
  { label: "Year 2+", rev: "$3,000 – $12,000+ / mo", note: "Brand equity. Foreign rights. Licensing. Speaking." },
];

export default function ValueLadder() {
  return (
    <div className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 4</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-4">Revenue trajectory</h2>
        <p className="text-amber-100/50 text-sm text-center mb-12">Cold-start benchmarks. No existing audience. No ad spend.</p>
        <div className="space-y-px">
          {TIERS.map((t, i) => (
            <div key={i} className="flex gap-6 p-5 border border-amber-900/30 hover:bg-amber-900/10 transition-colors">
              <div className="w-24 shrink-0">
                <div className="text-xs font-mono text-amber-600 uppercase tracking-wider">{t.label}</div>
              </div>
              <div className="flex-1">
                <div className="text-amber-200 font-medium mb-1">{t.rev}</div>
                <div className="text-xs text-amber-100/40">{t.note}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

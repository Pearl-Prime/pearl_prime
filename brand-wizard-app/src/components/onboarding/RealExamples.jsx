const EXAMPLES = [
  { name: "Atomic Habits", author: "James Clear", angle: "Performance & Focus", result: "15M+ copies · #1 NYT · Every platform" },
  { name: "The Body Keeps the Score", author: "Bessel van der Kolk", angle: "Nervous System", result: "200+ weeks NYT · Somatic crossover" },
  { name: "Big Magic", author: "Elizabeth Gilbert", angle: "Identity & Direction", result: "Global spiritual self-help anchor" },
  { name: "Ikigai", author: "García & Miralles", angle: "Spiritual Awakening", result: "JP origin → 3M+ EN copies · 60 languages" },
];

export default function RealExamples() {
  return (
    <div className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <p className="text-xs font-mono tracking-widest uppercase text-amber-600 mb-2 text-center">Step 8</p>
        <h2 className="font-serif text-4xl text-amber-100 text-center mb-4">Proven demand</h2>
        <p className="text-amber-100/50 text-sm text-center mb-12 max-w-xl mx-auto">
          These titles prove the demand. Pearl Prime delivers the same reader transformation — weekly, at scale, across five markets.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {EXAMPLES.map((e) => (
            <div key={e.name} className="p-6 border border-amber-900/30 hover:bg-amber-900/10 transition-colors">
              <div className="text-xs font-mono text-amber-600 uppercase tracking-wider mb-2">{e.angle}</div>
              <div className="text-amber-200 font-medium mb-1">{e.name}</div>
              <div className="text-xs text-amber-100/40 mb-3">{e.author}</div>
              <div className="text-xs text-amber-100/60">{e.result}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
